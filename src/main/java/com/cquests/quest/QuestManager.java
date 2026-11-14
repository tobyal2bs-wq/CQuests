package com.cquests.quest;

import com.cquests.T;

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
        if(plugin.progression()!=null&&!plugin.progression().canTake(data,quest.level()))return false;
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
        if (!settings().sideGatesEnabled) return 0;
        return quest.sideRequired() >= 0 ? quest.sideRequired() : settings().sideQuestsPerChapter;
    }

    /** Side quests are numbered per NPC and done in order, so "done" means its number is within the NPC's count. */
    public boolean isDone(PlayerData data, Quest quest) {
        if (quest.category() == QuestCategory.SIDE && !quest.giver().isEmpty()) {
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
        if (!shouldSee(data, npc)) return Offer.none("locked");
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
        if(!plugin.progression().canTake(data,settings().dailyMinLevel))return Offer.none("daily-level");
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
        // Every player gets their own daily. Co-op dailies are only offered when enough friends stand nearby.
        int friends = nearbyPlayers(player);
        // Seasonal dailies only exist while their season is on (/cq season).
        List<Quest> inSeason = new ArrayList<>();
        for (Quest quest : pool) {
            String season = quests().season(quest.id());
            if (season.isEmpty() || (plugin.seasons() != null && plugin.seasons().active(season))) inSeason.add(quest);
        }
        if (inSeason.isEmpty()) return Offer.none("nothing");
        List<Quest> fitting = new ArrayList<>();
        for (Quest quest : inSeason) if (quests().together(quest.id()) - 1 <= friends) fitting.add(quest);
        if (fitting.isEmpty()) fitting = inSeason;
        List<Quest> seasonal = fitting.stream().filter(q -> !quests().season(q.id()).isEmpty()).toList();
        if (!seasonal.isEmpty() && rnd.nextInt(2) == 0) return Offer.of(seasonal.get(rnd.nextInt(seasonal.size())));
        List<Quest> coop = fitting.stream().filter(q -> quests().together(q.id()) > 1).toList();
        if (!coop.isEmpty() && rnd.nextInt(3) == 0) return Offer.of(coop.get(rnd.nextInt(coop.size())));
        return Offer.of(fitting.get(rnd.nextInt(fitting.size())));
    }

    // ------------------------------------------------------------------ actions

    public boolean accept(Player player, Quest quest) {
        return accept(player,quest,false);
    }
    public boolean forceAccept(Player player,Quest quest){return accept(player,quest,true);}
    private boolean accept(Player player,Quest quest,boolean force) {return accept(player,quest,force,false);}
    private boolean accept(Player player,Quest quest,boolean force,boolean quiet) {
        PlayerData data = data(player);
        if(!force&&!requirementsMet(data,quest)){
            plugin.send(player,T.t("quest-manager.finish-the-previous-tasks-and", "<yellow>Finish the previous tasks and reach Wayfarer level <level> before taking this quest.", "level", Math.max(1,quest.level())));
            return false;
        }
        if (data.isActive(quest.id()) || (quest.category() != QuestCategory.DAILY && isDone(data, quest))) return false;
        com.cquests.farm.EconomyBridge.Payment paid = force ? null : payChapter(player, quest);
        if (!force && paid == null) return false;
        synchronized (data) {
            if (data.isActive(quest.id()) || (quest.category() != QuestCategory.DAILY && isDone(data, quest))) {
                if (paid != null) paid.refund();
                return false;
            }
            data.start(new ActiveQuest(quest.id(), quest.objectives().size(), System.currentTimeMillis()));
            data.markStarted(System.currentTimeMillis());
            if (quest.category() == QuestCategory.DAILY) {
                data.setLastDailyAt(System.currentTimeMillis());
            }
        }
        if (!quiet) plugin.send(player, settings().msg("quest-accepted", "<green>New quest: <white><bold><quest></bold></white>. Type <yellow>/quests</yellow> to read your journal.")
                .replace("<quest>", Text.escape(quest.name())));
        if (!quiet && (plugin.getConfig() == null || plugin.getConfig().getBoolean("dialogue.how-to-tips", true))) {
            int needed = quests().together(quest.id());
            if (needed > 1) plugin.send(player, T.t("quest-manager.co-op-needs-players-within", "<aqua>Co-op: <white>needs <needed> players within 16 blocks doing it at the same time.", "needed", needed));
            for (Objective objective : quest.objectives()) {
                String tip = HowTo.describe(objective);
                if (tip != null) plugin.send(player, T.t("quest-manager.tip", "<dark_gray>  Tip: <gray><tip>", "tip", Text.escape(tip)));
            }
        }
        if (!quiet && quest.objectives().stream().anyMatch(o -> o.type() == ObjectiveType.FIND)) plugin.crates().hint(player, 2);
        player.playSound(player.getLocation(), Sound.UI_TOAST_IN, 1f, 1f);
        plugin.visibility().refresh(player);
        plugin.tracker().track(player, quest.id());
        guide(player, "start", quest.id());
        return true;
    }

    private final com.cquests.farm.EconomyBridge economy = new com.cquests.farm.EconomyBridge();
    private volatile boolean warnedNoEconomy;

    /** Money a player pays to start this chapter (its first story quest), 0 for every other quest. */
    public long chapterCost(Quest quest) {
        if (quest.category() != QuestCategory.STORY || quest.chapter() <= 1) return 0;
        var config = plugin.getConfig();
        if (config == null || !config.getBoolean("chapters.costs-enabled", true)) return 0;
        List<Quest> story = quests().story();
        int index = story.indexOf(quest);
        if (index <= 0 || story.get(index - 1).chapter() == quest.chapter()) return 0;
        return Math.max(0, config.getLong("chapters.cost." + quest.chapter(), defaultChapterCost(quest.chapter())));
    }

    /** The configured cost of a chapter number, for /cq test cost when the chapter is switched off. */
    public static long chapterCostFor(CQuestsPlugin plugin, int chapter) {
        var config = plugin.getConfig();
        if (chapter <= 1 || config == null || !config.getBoolean("chapters.costs-enabled", true)) return 0;
        return Math.max(0, config.getLong("chapters.cost." + chapter, defaultChapterCost(chapter)));
    }

    static long defaultChapterCost(int chapter) {
        long[] costs = {0, 0, 5_000_000, 10_000_000, 20_000_000, 35_000_000, 50_000_000, 75_000_000, 100_000_000, 150_000_000, 250_000_000};
        return chapter < costs.length ? costs[chapter] : 250_000_000L + (chapter - 10) * 100_000_000L;
    }

    /** Charges the chapter cost; a payment that does nothing when there is no cost. Null when the player can't pay. */
    private com.cquests.farm.EconomyBridge.Payment payChapter(Player player, Quest quest) {
        long cost = chapterCost(quest);
        com.cquests.farm.EconomyBridge.Payment none = economy.charge(player, 0);
        if (cost <= 0) return none;
        if (!economy.available()) {
            if (!warnedNoEconomy) { warnedNoEconomy = true; plugin.getLogger().info("Chapter costs need Vault or economy.take-command in config.yml; chapters are free until then."); }
            return none;
        }
        var payment = economy.charge(player, cost);
        if (payment == null) {
            double balance = economy.balance(player);
            plugin.send(player, settings().msg("chapter-cost-missing", "<red>Chapter <chapter> costs <gold><cost></gold> to start. You have <white><balance></white>.")
                    .replace("<chapter>", Integer.toString(quest.chapter())).replace("<cost>", Text.compact(cost))
                    .replace("<balance>", Double.isFinite(balance) ? Text.compact((long) balance) : "?"));
            return null;
        }
        plugin.send(player, settings().msg("chapter-cost-paid", "<gold>You paid <cost> to begin Chapter <chapter>: <name>.")
                .replace("<chapter>", Integer.toString(quest.chapter())).replace("<cost>", Text.compact(cost))
                .replace("<name>", Text.escape(quests().chapterName(quest.chapter()))));
        return payment;
    }

    public void giveWelcome(Player player) {
        Quest welcome = quests().get(settings().welcomeQuest);
        PlayerData data = data(player);
        if (welcome == null || data.isCompleted(welcome.id()) || data.isActive(welcome.id())) {
            return;
        }
        String tip = settings().msg("first-join", "");
        // No chat on join unless welcome.chat-message is turned on; the arrow and compass already point the way.
        boolean chat = plugin.getConfig() != null && plugin.getConfig().getBoolean("welcome.chat-message", false);
        if (accept(player, welcome, false, !chat) && !tip.isBlank() && chat) {
            player.sendMessage(Text.mm(fill(tip, player)));
        }
    }

    /** A timed quest ran out: it is dropped (its progress too) and can be taken again from its villager. */
    public void timeUp(Player player, Quest quest) {
        PlayerData data = data(player);
        if (data.remove(quest.id()) == null) return;
        plugin.store().saveNow(data);
        plugin.send(player, settings().msg("quest-time-up", "<red>⌛ Out of time: <white><quest></white>. <gray>Ask the villager again to retry.").replace("<quest>", Text.escape(quest.name())));
        player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASS, 1f, 0.6f);
        plugin.visibility().refresh(player);
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
    /** True if one of the player's active quests still needs this kind of progress. Cheap; no changes. */
    public boolean wants(Player player, ObjectiveType type, String key) {
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data == null) {
            return false;
        }
        synchronized (data) {
            for (ActiveQuest active : data.active().values()) {
                Quest quest = resolve(active);
                if (quest == null) {
                    continue;
                }
                for (int i = 0; i < quest.objectives().size(); i++) {
                    Objective objective = quest.objectives().get(i);
                    if (objective.type() == type && !objectiveDone(quest, active, i) && objective.target().matches(key)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public void progress(Player player, ObjectiveType type, String key, int amount) {
        progress(player, type, key, amount, false);
    }

    /**
     * @param fromBoss true only when a private boss fight ended; boss quests ignore ordinary kills of
     *                 the same mob type, so a stray Ravager or Warden can't stand in for the boss
     */
    public void progress(Player player, ObjectiveType type, String key, int amount, boolean fromBoss) {
        progress(player, type, key, amount, fromBoss, false);
    }

    /**
     * Wheat from the farm fields only counts for side and daily quests of the spawn villagers
     * (act 1). It never moves the story forward; it still gives levels.
     */
    public void progressFromFarm(Player player, String key) {
        progress(player, ObjectiveType.HARVEST, key, 1, false, true);
    }

    /** When each player last made progress of each kind, for co-op quests. Cleared on logout. */
    private final java.util.Map<java.util.UUID, long[]> lastAction = new java.util.concurrent.ConcurrentHashMap<>();
    private final java.util.Map<java.util.UUID, Long> coopHint = new java.util.concurrent.ConcurrentHashMap<>();

    public void forget(Player player) {
        lastAction.remove(player.getUniqueId());
        coopHint.remove(player.getUniqueId());
    }

    /** Co-op partners: other players within 16 blocks who did the same kind of thing in the last 5 seconds. */
    public int partners(Player player, ObjectiveType type) {
        long now = System.currentTimeMillis();
        int count = 0;
        for (Player other : player.getLocation().getNearbyPlayers(16)) {
            if (other.equals(player)) continue;
            long[] times = lastAction.get(other.getUniqueId());
            if (times != null && now - times[type.ordinal()] <= 5000) count++;
        }
        return count;
    }

    /** Players standing within 16 blocks, for offering co-op dailies only to groups. */
    public int nearbyPlayers(Player player) {
        int count = 0;
        for (Player other : player.getLocation().getNearbyPlayers(16)) if (!other.equals(player)) count++;
        return count;
    }

    private void progress(Player player, ObjectiveType type, String key, int amount, boolean fromBoss, boolean farm) {
        if (amount <= 0) {
            return;
        }
        lastAction.computeIfAbsent(player.getUniqueId(), id -> new long[ObjectiveType.values().length])[type.ordinal()] = System.currentTimeMillis();
        int partners = -1;
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
                if (!fromBoss && type == ObjectiveType.KILL && plugin.adventures() != null && plugin.adventures().isBossQuest(quest.id())) {
                    continue;
                }
                if (farm) {
                    if (quest.category() == QuestCategory.STORY) continue;
                    NpcDef giver = npcs().get(quest.giver());
                    if (quest.category() == QuestCategory.SIDE && (giver == null || giver.act() > 1)) continue;
                }
                int needed = quests().together(quest.id());
                if (needed > 1) {
                    if (partners < 0) partners = partners(player, type);
                    if (partners < needed - 1) {
                        long now = System.currentTimeMillis();
                        if (now - coopHint.getOrDefault(player.getUniqueId(), 0L) > 3000) {
                            coopHint.put(player.getUniqueId(), now);
                            player.sendActionBar(Text.mm(T.t("quest-manager.needs-players-doing-it-together", "<yellow><name> <gray>needs <white><needed> players</white> doing it together. <white><partners></white> nearby right now.", "name", Text.escape(quest.name()), "needed", needed, "partners", partners)));
                        }
                        continue;
                    }
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

    private int take(PlayerInventory inventory, Set<Material> materials, int needed) {
        int taken = 0;
        ItemStack[] contents = inventory.getStorageContents();
        for (int slot = 0; slot < contents.length && taken < needed; slot++) {
            ItemStack stack = contents[slot];
            if (stack == null || !materials.contains(stack.getType()) || (plugin.farm()!=null && plugin.farm().marked(stack))) {
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
        int streak = 0;
        synchronized (data) {
            ActiveQuest active = data.active(quest.id());
            if (active == null || !ready(quest, active)) {
                return;
            }
            switch (quest.category()) {
                case DAILY -> {
                    data.complete(quest.id(), false);
                    data.addDailyDone();
                    streak = data.recordDailyStreak(java.time.LocalDate.now().toEpochDay());
                }
                case SIDE -> {
                    // A hand-written quest without a giver (the tutorial) is remembered by id.
                    data.complete(quest.id(), quest.giver().isEmpty());
                    if (!quest.giver().isEmpty()) data.addSideDone(quest.giver());
                }
                case STORY -> {
                    data.complete(quest.id(), true);
                    Location at = journeySpot(player, quest);
                    data.addJourney(new JourneyEntry(quest.id(), System.currentTimeMillis(), at.getWorld().getName(),
                            at.getX(), at.getY(), at.getZ()));
                }
            }
        }
        if (quest.category() == QuestCategory.STORY) {
            plugin.finale().achievements().onStoryQuest(player, quest);
        }
        plugin.finale().achievements().sync(player);
        if(plugin.progression()!=null)plugin.progression().award(player,200L+quest.level()*40L,false);
        // Queue quest state and custom XP together before handing out rewards.
        plugin.store().saveNow(data);
        plugin.send(player, settings().msg("quest-complete", "<gold>★ Quest complete: <white><bold><quest></bold></white>")
                .replace("<quest>", Text.escape(quest.name())));
        if(plugin.mail()!=null)plugin.mail().notifyNew(player);
        giveRewards(player, quest.category() == QuestCategory.DAILY ? dailyReward(player, quest) : quest.reward());
        if (streak > 0) dailyStreakBonus(player, quest, streak);
        if (quest.category() == QuestCategory.STORY && (quests().endsChapter(quest) || isFinalQuest(quest))) chapterReward(player, quest.chapter());
        if(quest.category()==QuestCategory.STORY&&(quests().endsChapter(quest)||isFinalQuest(quest)))
            Sched.global(()->Bukkit.broadcast(Text.mm(T.t("quest-manager.chapter-complete-completed-chapter", "<gold><bold>CHAPTER COMPLETE</bold></gold> <white><player></white> <gray>completed Chapter <chapter>: <aqua><chapter2>", "player", Text.escape(player.getName()), "chapter", quest.chapter(), "chapter2", Text.escape(quests().chapterName(quest.chapter()))))));
        if(quest.category()==QuestCategory.STORY&&(quests().endsChapter(quest)||isFinalQuest(quest))&&plugin.discord()!=null)
            plugin.discord().chapterComplete(player,quest.chapter(),quests().chapterName(quest.chapter()));
        player.playSound(player.getLocation(), Sound.UI_TOAST_CHALLENGE_COMPLETE, 0.8f, 1f);
        plugin.visibility().refresh(player);
        plugin.tracker().update(player);
        startTutorialAfter(player, quest);
        guide(player, "after", quest.id());
        if (isFinalQuest(quest)) {
            plugin.finale().play(player);
        } else if (quests().endsChapter(quest)) {
            plugin.finale().chapterComplete(player, quest, quests().nextStory(quest));
        } else if (quest.big()) {
            plugin.finale().celebrate(player, quest);
        }
    }

    /**
     * The beginner guide: a short tip at the first few steps (messages.yml, guide section, keys
     * guide-start-<quest> and guide-after-<quest>). Blank or missing keys show nothing; guide.enabled
     * in config.yml turns it off. Tips arrive a moment later so they do not drown in the reward lines.
     */
    void guide(Player player, String when, String questId) {
        if (plugin.getConfig() != null && !plugin.getConfig().getBoolean("guide.enabled", true)) return;
        String tip = settings().msg("guide-" + when + "-" + questId, "");
        if (tip.isBlank()) return;
        Sched.entityLater(player, 50L, () -> {
            if (!player.isOnline()) return;
            player.sendMessage(Text.mm(fill(tip, player)));
            player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_CHIME, 0.6f, 1.4f);
        });
    }

    /** The tutorial quest (quests.tutorial-quest) starts as soon as the welcome quest is done; finishing it pays the player's inviter. */
    private void startTutorialAfter(Player player, Quest done) {
        var config = plugin.getConfig();
        String id = config == null ? "" : config.getString("quests.tutorial-quest", "tutorial");
        Quest tutorial = id == null || id.isBlank() ? null : quests().get(id);
        if (done.id().equals(settings().welcomeQuest)) {
            if (tutorial != null && !data(player).isCompleted(tutorial.id()) && !data(player).isActive(tutorial.id())) {
                accept(player, tutorial, true, true);
                plugin.send(player, T.t("quest-manager.tutorial-quick-steps-that-pay", "<gold>Tutorial:</gold> <white><name> <gray>Quick steps that pay out in a few minutes. Type <yellow>/quests</yellow> to see them.", "name", Text.escape(tutorial.name())));
            } else if (tutorial == null && plugin.invites() != null) plugin.invites().onTutorialDone(player);
        }
        if (tutorial != null && done.id().equals(tutorial.id()) && plugin.invites() != null) plugin.invites().onTutorialDone(player);
    }

    /**
     * Daily money is a roll for each player and day: anywhere from daily.money-min-percent to
     * daily.money-max-percent of the quest's money, so some days pay little and some pay a lot.
     */
    public Reward dailyReward(Player player, Quest quest) {
        var config = plugin.getConfig();
        Reward base = quest.reward();
        if (config == null || base.money() <= 0) return base;
        int min = Math.max(0, config.getInt("daily.money-min-percent", 25));
        int max = Math.max(min, config.getInt("daily.money-max-percent", 300));
        long day = System.currentTimeMillis() / 86_400_000L;
        Random rnd = new Random(player.getUniqueId().getMostSignificantBits() ^ day * 31_337L ^ quest.id().hashCode());
        int percent = min + rnd.nextInt(max - min + 1);
        long money = Math.round(base.money() * percent / 100.0);
        if (percent >= 200) plugin.send(player, T.t("quest-manager.lucky-day-this-daily-paid", "<gold>★ Lucky day! <white>This daily paid <percent>%.", "percent", percent));
        else if (percent <= 50) plugin.send(player, T.t("quest-manager.a-quiet-day-this-daily", "<gray>A quiet day. This daily paid <percent>%.", "percent", percent));
        return new Reward(money, base.items(), base.effects(), base.commands(), base.xp());
    }

    /** Extra rewards for finishing a chapter: chapters.rewards.<n>.items and .commands in config.yml. */
    private void chapterReward(Player player, int chapter) {
        var config = plugin.getConfig();
        if (config == null) return;
        var section = config.getConfigurationSection("chapters.rewards." + chapter);
        if (section == null) return;
        List<RewardItem> items = new ArrayList<>();
        for (String line : section.getStringList("items")) {
            String[] parts = line.trim().split("\\s+");
            Material material = Material.matchMaterial(parts[0]);
            int amount = parts.length > 1 ? Math.max(1, Math.min(64, Integer.parseInt(parts[1].replaceAll("\\D", "").isEmpty() ? "1" : parts[1].replaceAll("\\D", "")))) : 1;
            if (material != null && material.isItem()) items.add(new RewardItem(material, amount));
        }
        Reward reward = new Reward(0, items, List.of(), section.getStringList("commands"), 0);
        if (reward.isEmpty()) return;
        plugin.send(player, T.t("quest-manager.chapter-reward", "<gold><bold>Chapter <chapter> reward!</bold>", "chapter", chapter));
        giveRewards(player, reward);
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

    /**
     * Daily streaks: every day in a row adds daily.streak-bonus-percent of the daily's money, up to
     * daily.streak-max-days. Missing a day starts the streak again at 1.
     */
    private void dailyStreakBonus(Player player, Quest quest, int streak) {
        var config = plugin.getConfig();
        if (!config.getBoolean("daily.streaks", true)) return;
        int days = Math.min(streak, Math.max(1, config.getInt("daily.streak-max-days", 7))) - 1;
        long bonus = Math.round(quest.reward().money() * days * Math.max(0, config.getDouble("daily.streak-bonus-percent", 10)) / 100.0);
        if (bonus > 0 && !settings().moneyCommand.isBlank()) {
            String command = settings().moneyCommand.replace("%player%", player.getName()).replace("%amount%", Long.toString(bonus));
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), stripSlash(command)));
        }
        plugin.send(player, settings().msg("daily-streak", "<gold>🔥 Daily streak: <white><streak> day(s)</white>. <gray>Streak bonus: <green>+<bonus></green>. Come back tomorrow to keep it going!")
                .replace("<streak>", Integer.toString(streak)).replace("<bonus>", String.format(java.util.Locale.ROOT, "%,d", bonus)));
        if (plugin.discord() != null && (streak == 7 || streak == 30 || streak == 100 || streak % 365 == 0)) plugin.discord().dailyStreak(player, streak);
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
        if(npc.daily()||settings().spawnNpcIds.contains(npc.id()))return true;
        // Active quests always keep their participants visible, including shared chapter NPCs.
        for (Quest quest : activeQuests(data)) if (quest.involves(npc.id())) return true;
        Quest next = nextStoryQuest(data);
        int chapter = next == null ? Integer.MAX_VALUE : next.chapter();
        if (quests().firstChapter(npc.id()) > chapter) return false;
        if (settings().hideFinishedVillagers && finishedWith(data, npc)) {
            return false;
        }
        if (!npc.personal() || data.hasMet(npc.id()) || quests().firstChapter(npc.id()) <= chapter) {
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
        // Optional side work remains available after the story has moved on.
        if (quests().sidePerNpc() > 0 && data.sideDone(npc.id()) < quests().sidePerNpc()) return false;
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
