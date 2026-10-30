package com.cquests.quest;

import com.cquests.CQuestsPlugin;
import com.cquests.Settings;
import com.cquests.data.ActiveQuest;
import com.cquests.data.JourneyEntry;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.model.Reward;
import com.cquests.model.RewardEffect;
import com.cquests.model.RewardItem;
import com.cquests.npc.NpcRegistry;
import com.cquests.npc.SpawnManager;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Registry;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.PlayerInventory;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.Set;

/** Quest rules: who can take what, progress counting, turn-ins and rewards. */
public final class QuestManager {

    public enum State { LOCKED, AVAILABLE, ACTIVE, READY, COMPLETED }

    /** Result of asking an NPC for work. Exactly one of the fields is meaningful. */
    public record Offer(Quest quest, String reason) {
        static Offer of(Quest quest) {
            return new Offer(quest, null);
        }

        static Offer none(String reason) {
            return new Offer(null, reason);
        }
    }

    private final CQuestsPlugin plugin;

    public QuestManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    private Settings settings() {
        return plugin.settings();
    }

    private QuestRegistry quests() {
        return plugin.quests();
    }

    private NpcRegistry npcs() {
        return plugin.npcs();
    }

    public PlayerData data(Player player) {
        return plugin.store().get(player.getUniqueId());
    }

    // ------------------------------------------------------------------ state

    /** The quest behind an active entry, cached on the entry (side quests are generated, so this saves work). */
    public Quest resolve(ActiveQuest active) {
        int generation = quests().generation();
        Quest quest = active.cached(generation);
        if (quest == null) {
            quest = quests().get(active.questId());
            active.cache(quest, generation);
        }
        return quest;
    }

    public boolean requirementsMet(PlayerData data, Quest quest) {
        for (String required : quest.requires()) {
            if (!data.isCompleted(required)) {
                return false;
            }
        }
        return chapterGate(data, quest) == null;
    }

    /**
     * Story chapters are long on purpose: before a villager's story quest opens up, the player has to
     * finish {@code side-quests-per-chapter} side quests for the previous story villager.
     * Returns that villager's id while the gate is still closed, otherwise null.
     */
    public String chapterGate(PlayerData data, Quest quest) {
        int needed = Math.min(sideRequired(quest), quests().sidePerNpc());
        if (quest.category() != QuestCategory.STORY || needed <= 0) {
            return null;
        }
        for (String required : quest.requires()) {
            Quest previous = quests().get(required);
            if (previous != null && previous.category() == QuestCategory.STORY && !previous.giver().isEmpty()
                    && !previous.giver().equals(quest.giver()) && data.sideDone(previous.giver()) < needed) {
                return previous.giver();
            }
        }
        return null;
    }

    /** Side quests needed for the previous story villager before this story quest opens. */
    public int sideRequired(Quest quest) {
        return quest.sideRequired() >= 0 ? quest.sideRequired() : settings().sideQuestsPerChapter;
    }

    /** Side quests are numbered per NPC and done in order, so "done" means its number is within the NPC's count. */
    public boolean isDone(PlayerData data, Quest quest) {
        if (quest.category() == QuestCategory.SIDE) {
            return quest.order() <= data.sideDone(quest.giver());
        }
        return data.isCompleted(quest.id());
    }

    public State state(PlayerData data, Quest quest) {
        ActiveQuest active = data.active(quest.id());
        if (active != null) {
            return ready(quest, active) ? State.READY : State.ACTIVE;
        }
        if (isDone(data, quest)) {
            return State.COMPLETED;
        }
        return requirementsMet(data, quest) ? State.AVAILABLE : State.LOCKED;
    }

    public boolean objectiveDone(Quest quest, ActiveQuest active, int index) {
        return active.get(index) >= quest.objectives().get(index).amount();
    }

    public boolean ready(Quest quest, ActiveQuest active) {
        for (int i = 0; i < quest.objectives().size(); i++) {
            if (!objectiveDone(quest, active, i)) {
                return false;
            }
        }
        return true;
    }

    /** Active quests in journal order: story first, then daily, then side quests. */
    public List<Quest> activeQuests(PlayerData data) {
        List<Quest> story = new ArrayList<>();
        List<Quest> daily = new ArrayList<>();
        List<Quest> side = new ArrayList<>();
        synchronized (data) {
            for (ActiveQuest active : data.active().values()) {
                Quest quest = resolve(active);
                if (quest == null) {
                    continue;
                }
                switch (quest.category()) {
                    case STORY -> story.add(quest);
                    case DAILY -> daily.add(quest);
                    case SIDE -> side.add(quest);
                }
            }
        }
        List<Quest> out = new ArrayList<>(story);
        out.addAll(daily);
        out.addAll(side);
        return out;
    }

    public int activeCount(PlayerData data, QuestCategory category) {
        int count = 0;
        for (Quest quest : activeQuests(data)) {
            if (quest.category() == category) {
                count++;
            }
        }
        return count;
    }

    /** The next story quest the player should go for, or null when the story is finished. */
    public Quest nextStoryQuest(PlayerData data) {
        for (Quest quest : quests().story()) {
            if (!data.isCompleted(quest.id())) {
                return quest;
            }
        }
        return null;
    }

    public long dailyCooldownLeft(PlayerData data) {
        return data.lastDailyAt() + settings().dailyCooldownMillis - System.currentTimeMillis();
    }

    // ------------------------------------------------------------------ offers

    public Offer nextOffer(Player player, NpcDef npc) {
        PlayerData data = data(player);
        if (npc.daily()) {
            return dailyOffer(player, data);
        }
        List<Quest> storyQuests = quests().storyFrom(npc.id());
        boolean storyDone = true;
        for (Quest quest : storyQuests) {
            if (data.isCompleted(quest.id())) {
                continue;
            }
            storyDone = false;
            if (!data.isActive(quest.id()) && requirementsMet(data, quest)) {
                return Offer.of(quest);
            }
        }
        if (!storyDone) {
            return Offer.none("locked");
        }
        Quest side = quests().side(npc.id(), data.sideDone(npc.id()) + 1);
        if (side == null || data.isActive(side.id())) {
            return Offer.none("nothing");
        }
        if (!requirementsMet(data, side)) {
            return Offer.none("locked");
        }
        if (activeCount(data, QuestCategory.SIDE) >= settings().maxActiveSide) {
            return Offer.none("too-many");
        }
        return Offer.of(side);
    }

    private Offer dailyOffer(Player player, PlayerData data) {
        List<Quest> pool = quests().dailyPool();
        if (pool.isEmpty()) {
            return Offer.none("nothing");
        }
        if (activeCount(data, QuestCategory.DAILY) > 0) {
            return Offer.none("daily-active");
        }
        if (dailyCooldownLeft(data) > 0) {
            return Offer.none("daily-cooldown");
        }
        long day = System.currentTimeMillis() / 86_400_000L;
        Random rnd = new Random(player.getUniqueId().getLeastSignificantBits() ^ day * 1_000_003L);
        return Offer.of(pool.get(rnd.nextInt(pool.size())));
    }

    // ------------------------------------------------------------------ actions

    public boolean accept(Player player, Quest quest) {
        PlayerData data = data(player);
        synchronized (data) {
            if (data.isActive(quest.id()) || (quest.category() != QuestCategory.DAILY && isDone(data, quest))) {
                return false;
            }
            data.start(new ActiveQuest(quest.id(), quest.objectives().size(), System.currentTimeMillis()));
            data.markStarted(System.currentTimeMillis());
            if (quest.category() == QuestCategory.DAILY) {
                data.setLastDailyAt(System.currentTimeMillis());
            }
        }
        plugin.send(player, settings().msg("quest-accepted", "<green>New quest: <white><bold><quest></bold></white>. Type <yellow>/quests</yellow> to read your journal.")
                .replace("<quest>", Text.escape(quest.name())));
        player.playSound(player.getLocation(), Sound.UI_TOAST_IN, 1f, 1f);
        plugin.visibility().refresh(player);
        plugin.tracker().track(player, quest.id());
        return true;
    }

    public void giveWelcome(Player player) {
        Quest welcome = quests().get(settings().welcomeQuest);
        PlayerData data = data(player);
        if (welcome == null || data.isCompleted(welcome.id()) || data.isActive(welcome.id())) {
            return;
        }
        accept(player, welcome);
    }

    public boolean abandon(Player player, Quest quest) {
        if (quest.category() == QuestCategory.STORY) {
            return false;
        }
        PlayerData data = data(player);
        if (data.remove(quest.id()) == null) {
            return false;
        }
        plugin.visibility().refresh(player);
        plugin.tracker().update(player);
        return true;
    }

    /** Counts a game event (kill, mine, craft...) towards every matching active objective. */
    public void progress(Player player, ObjectiveType type, String key, int amount) {
        if (amount <= 0) {
            return;
        }
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data == null) {
            return;
        }
        List<Quest> newlyReady = new ArrayList<>();
        boolean tracked = false;
        synchronized (data) {
            if (data.active().isEmpty()) {
                return;
            }
            for (ActiveQuest active : data.active().values()) {
                Quest quest = resolve(active);
                if (quest == null) {
                    continue;
                }
                boolean wasReady = ready(quest, active);
                boolean changed = false;
                for (int i = 0; i < quest.objectives().size(); i++) {
                    Objective objective = quest.objectives().get(i);
                    if (objective.type() != type || objectiveDone(quest, active, i) || !objective.target().matches(key)) {
                        continue;
                    }
                    int value = Math.min(objective.amount(), active.get(i) + amount);
                    active.set(i, value);
                    changed = true;
                    actionBar(player, quest, objective, value);
                }
                if (changed) {
                    data.markDirty();
                    tracked = true;
                    if (!wasReady && ready(quest, active)) {
                        newlyReady.add(quest);
                    }
                }
            }
        }
        if (tracked) {
            plugin.tracker().update(player);
        }
        for (Quest quest : newlyReady) {
            onReady(player, quest);
        }
    }

    private void actionBar(Player player, Quest quest, Objective objective, int value) {
        boolean done = value >= objective.amount();
        player.sendActionBar(Text.mm("<gold>" + Text.escape(quest.name()) + "</gold> <dark_gray>»</dark_gray> <white>"
                + objectiveLabel(objective) + " " + (done ? "<green>" : "<yellow>") + value + "/" + objective.amount()));
        if (done) {
            player.playSound(player.getLocation(), Sound.ENTITY_EXPERIENCE_ORB_PICKUP, 0.6f, 1.4f);
        }
    }

    private void onReady(Player player, Quest quest) {
        if (quest.autoComplete()) {
            Sched.entity(player, () -> complete(player, quest));
            return;
        }
        plugin.send(player, settings().msg("quest-ready", "<green>✔ <white><bold><quest></bold></white> is done! Return to <npc>.")
                .replace("<quest>", Text.escape(quest.name()))
                .replace("<npc>", npcs().mention(quest.turnIn())));
        player.playSound(player.getLocation(), Sound.ENTITY_PLAYER_LEVELUP, 0.7f, 1.2f);
    }

    /**
     * Completes TALK objectives for this NPC. A TALK objective only counts once every other
     * objective of its quest is done, so "kill a wolf, then tell Jerry" works as expected.
     */
    public boolean talk(Player player, String npcId) {
        PlayerData data = data(player);
        boolean any = false;
        List<Quest> newlyReady = new ArrayList<>();
        synchronized (data) {
            for (ActiveQuest active : data.active().values()) {
                Quest quest = resolve(active);
                if (quest == null) {
                    continue;
                }
                for (int i = 0; i < quest.objectives().size(); i++) {
                    Objective objective = quest.objectives().get(i);
                    if (objective.type() != ObjectiveType.TALK || !npcId.equals(objective.npc()) || objectiveDone(quest, active, i)) {
                        continue;
                    }
                    if (!othersDone(quest, active, i)) {
                        continue;
                    }
                    active.set(i, objective.amount());
                    data.markDirty();
                    any = true;
                    if (ready(quest, active) && !quest.turnIn().equals(npcId)) {
                        newlyReady.add(quest);
                    }
                }
            }
        }
        for (Quest quest : newlyReady) {
            onReady(player, quest);
        }
        return any;
    }

    private boolean othersDone(Quest quest, ActiveQuest active, int skip) {
        for (int i = 0; i < quest.objectives().size(); i++) {
            if (i != skip && quest.objectives().get(i).type() != ObjectiveType.TALK && !objectiveDone(quest, active, i)) {
                return false;
            }
        }
        return true;
    }

    /** Takes items for DELIVER objectives aimed at this NPC. Returns a line per hand-over. */
    public List<String> deliver(Player player, String npcId) {
        PlayerData data = data(player);
        List<String> lines = new ArrayList<>();
        List<Quest> newlyReady = new ArrayList<>();
        PlayerInventory inventory = player.getInventory();
        synchronized (data) {
            for (ActiveQuest active : data.active().values()) {
                Quest quest = resolve(active);
                if (quest == null) {
                    continue;
                }
                boolean wasReady = ready(quest, active);
                for (int i = 0; i < quest.objectives().size(); i++) {
                    Objective objective = quest.objectives().get(i);
                    if (objective.type() != ObjectiveType.DELIVER || !npcId.equals(objective.npc()) || objectiveDone(quest, active, i)) {
                        continue;
                    }
                    int needed = objective.amount() - active.get(i);
                    int taken = take(inventory, objective.target().materials(), needed);
                    if (taken > 0) {
                        active.set(i, active.get(i) + taken);
                        data.markDirty();
                        lines.add(settings().msg("delivered", "<gray>You hand over <white><amount> <item></white>. <yellow>(<have>/<need>)")
                                .replace("<amount>", Integer.toString(taken))
                                .replace("<item>", Text.escape(objective.label()))
                                .replace("<have>", Integer.toString(active.get(i)))
                                .replace("<need>", Integer.toString(objective.amount())));
                    }
                }
                if (!wasReady && ready(quest, active) && !quest.turnIn().equals(npcId)) {
                    newlyReady.add(quest);
                }
            }
        }
        if (!lines.isEmpty()) {
            plugin.store().saveNow(data);
        }
        for (Quest quest : newlyReady) {
            onReady(player, quest);
        }
        return lines;
    }

    private static int take(PlayerInventory inventory, Set<Material> materials, int needed) {
        int taken = 0;
        ItemStack[] contents = inventory.getStorageContents();
        for (int slot = 0; slot < contents.length && taken < needed; slot++) {
            ItemStack stack = contents[slot];
            if (stack == null || !materials.contains(stack.getType())) {
                continue;
            }
            int use = Math.min(stack.getAmount(), needed - taken);
            taken += use;
            if (use >= stack.getAmount()) {
                inventory.setItem(slot, null);
            } else {
                stack.setAmount(stack.getAmount() - use);
                inventory.setItem(slot, stack);
            }
        }
        return taken;
    }

    /** Ready quests this NPC accepts as turn-in. */
    public List<Quest> readyAt(PlayerData data, String npcId) {
        List<Quest> out = new ArrayList<>();
        for (Quest quest : activeQuests(data)) {
            ActiveQuest active = data.active(quest.id());
            if (active != null && quest.turnIn().equals(npcId) && ready(quest, active)) {
                out.add(quest);
            }
        }
        return out;
    }

    /** An unfinished quest this NPC is waiting on (gave it out or takes it in). */
    public Quest pendingAt(PlayerData data, String npcId) {
        for (Quest quest : activeQuests(data)) {
            ActiveQuest active = data.active(quest.id());
            if (active != null && !ready(quest, active) && (quest.giver().equals(npcId) || quest.turnIn().equals(npcId))) {
                return quest;
            }
        }
        return null;
    }

    /** Hands out rewards and marks the quest done. Must run on the player's thread. */
    public void complete(Player player, Quest quest) {
        PlayerData data = data(player);
        synchronized (data) {
            if (!data.isActive(quest.id())) {
                return;
            }
            switch (quest.category()) {
                case DAILY -> {
                    data.complete(quest.id(), false);
                    data.addDailyDone();
                }
                case SIDE -> {
                    data.complete(quest.id(), false);
                    data.addSideDone(quest.giver());
                }
                case STORY -> {
                    data.complete(quest.id(), true);
                    Location at = journeySpot(player, quest);
                    data.addJourney(new JourneyEntry(quest.id(), System.currentTimeMillis(), at.getWorld().getName(),
                            at.getX(), at.getY(), at.getZ()));
                }
            }
        }
        // Persist before paying out, so a crash can't leave the quest claimable with the reward already given.
        plugin.store().saveNow(data);
        plugin.send(player, settings().msg("quest-complete", "<gold>★ Quest complete: <white><bold><quest></bold></white>")
                .replace("<quest>", Text.escape(quest.name())));
        giveRewards(player, quest.reward());
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1f);
        plugin.visibility().refresh(player);
        plugin.tracker().update(player);
        if (isFinalQuest(quest)) {
            plugin.finale().play(player);
        } else if (quests().endsChapter(quest)) {
            plugin.finale().chapterComplete(player, quest, quests().nextStory(quest));
        } else if (quest.big()) {
            plugin.finale().celebrate(player, quest);
        }
    }

    /** The last quest of the story chain; finishing it plays the ending. */
    public boolean isFinalQuest(Quest quest) {
        List<Quest> story = quests().story();
        return !story.isEmpty() && story.get(story.size() - 1).id().equals(quest.id());
    }

    /** Where a story quest "happened" for the replay: the villager you turned it in to, or the player. */
    private Location journeySpot(Player player, Quest quest) {
        SpawnManager.Point point = plugin.spawns().points().get(quest.turnIn().isEmpty() ? quest.giver() : quest.turnIn());
        Location loc = point == null ? null : point.location();
        return loc != null ? loc : player.getLocation();
    }

    public void giveRewards(Player player, Reward reward) {
        if (reward.money() > 0 && !settings().moneyCommand.isBlank()) {
            String command = settings().moneyCommand
                    .replace("%player%", player.getName())
                    .replace("%amount%", Long.toString(reward.money()));
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), stripSlash(command)));
        }
        for (RewardItem item : reward.items()) {
            ItemStack stack = new ItemStack(item.material(), item.amount());
            player.getInventory().addItem(stack).values()
                    .forEach(left -> player.getWorld().dropItemNaturally(player.getLocation(), left));
        }
        for (RewardEffect effect : reward.effects()) {
            PotionEffectType type = Registry.EFFECT.get(NamespacedKey.minecraft(effect.effect()));
            if (type != null) {
                player.addPotionEffect(new PotionEffect(type, effect.seconds() * 20, effect.amplifier()));
            }
        }
        if (reward.xp() > 0) {
            player.giveExp(reward.xp());
        }
        for (String raw : reward.commands()) {
            String command = raw.replace("%player%", player.getName());
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), stripSlash(command)));
        }
        for (String line : rewardLines(reward)) {
            plugin.send(player, "  <dark_gray>+</dark_gray> " + line);
        }
    }

    private static String stripSlash(String command) {
        return command.startsWith("/") ? command.substring(1) : command;
    }

    public List<String> rewardLines(Reward reward) {
        List<String> lines = new ArrayList<>();
        if (reward.money() > 0) {
            lines.add("<green>$" + Text.formatMoney(reward.money()) + "</green>");
        }
        for (RewardItem item : reward.items()) {
            String name = Text.pretty(item.material().name());
            lines.add("<white>" + item.amount() + " " + (item.amount() > 1 ? Text.plural(name) : name) + "</white>");
        }
        for (RewardEffect effect : reward.effects()) {
            String name = effect.effect().equals("speed") ? "Swiftness" : Text.capitalize(Text.pretty(effect.effect()));
            String level = effect.amplifier() > 0 ? " " + (effect.amplifier() + 1) : "";
            lines.add("<light_purple>" + name + level + " for " + Text.duration(effect.seconds() * 1000L) + "</light_purple>");
        }
        if (reward.xp() > 0) {
            lines.add("<aqua>" + reward.xp() + " xp</aqua>");
        }
        return lines;
    }

    // ------------------------------------------------------------------ visibility & text

    /** Personal NPCs only show for players who met them, need them for a quest, or are due to meet them next. */
    public boolean shouldSee(PlayerData data, NpcDef npc) {
        if (settings().hideFinishedVillagers && finishedWith(data, npc)) {
            return false;
        }
        if (!npc.personal() || data.hasMet(npc.id())) {
            return true;
        }
        for (Quest quest : activeQuests(data)) {
            if (quest.involves(npc.id())) {
                return true;
            }
        }
        for (Quest quest : quests().storyFrom(npc.id())) {
            if (!data.isCompleted(quest.id()) && requirementsMet(data, quest)) {
                return true;
            }
        }
        return false;
    }

    /**
     * True once a player owes a villager nothing: every story quest it gives is done, the side quests
     * the next chapter step asks for are done, and no active quest needs it. That player stops seeing it.
     */
    public boolean finishedWith(PlayerData data, NpcDef npc) {
        List<Quest> own = quests().storyFrom(npc.id());
        if (npc.daily() || own.isEmpty()) {
            return false;
        }
        for (Quest quest : own) {
            if (!data.isCompleted(quest.id())) {
                return false;
            }
        }
        for (Quest quest : activeQuests(data)) {
            if (quest.involves(npc.id())) {
                return false;
            }
        }
        Quest next = quests().nextStory(own.get(own.size() - 1));
        return next == null || data.isCompleted(next.id()) || !npc.id().equals(chapterGate(data, next));
    }

    /** "Kill wolves", "Bring Villager Martha wheat", "Talk to Villager Stephan". */
    public String objectiveLabel(Objective objective) {
        return switch (objective.type()) {
            case TALK -> "Talk to " + npcs().mention(objective.npc());
            case DELIVER -> "Bring " + npcs().mention(objective.npc()) + " " + Text.escape(objective.label());
            default -> objective.type().verb() + " " + Text.escape(objective.label());
        };
    }

    public String objectiveSentence(Objective objective) {
        return switch (objective.type()) {
            case TALK -> "Talk to " + npcs().mention(objective.npc()) + ".";
            case DELIVER -> "Bring " + npcs().mention(objective.npc()) + " " + objective.amount() + " " + Text.escape(objective.label()) + ".";
            default -> objective.type().verb() + " " + objective.amount() + " " + Text.escape(objective.label()) + ".";
        };
    }

    /** Fills {player}, {server} and {npc:id} placeholders in dialogue and description text. */
    public String fill(String text, Player player) {
        String out = text.replace("{player}", player.getName()).replace("{server}", settings().serverName);
        int start = out.indexOf("{npc:");
        while (start >= 0) {
            int end = out.indexOf('}', start);
            if (end < 0) {
                break;
            }
            String id = out.substring(start + 5, end);
            out = out.substring(0, start) + npcs().mention(id) + out.substring(end + 1);
            start = out.indexOf("{npc:", start);
        }
        return out;
    }
}
