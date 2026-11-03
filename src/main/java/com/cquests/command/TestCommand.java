package com.cquests.command;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.finale.StoryBook;
import com.cquests.model.NpcDef;
import com.cquests.model.Quest;
import com.cquests.quest.QuestManager;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * /cq test: lets admins see messages, animations, achievements and villagers disappearing without
 * playing the whole story. Only cquests.admin (op) can use it. Anything that changes a player's
 * progress can be undone with the matching command.
 */
final class TestCommand {

    static final List<String> ACTIONS = List.of("messages", "welcome", "celebrate", "chapter", "ending", "achievement",
            "finish", "unfinish", "roam", "book", "boss", "bossphase", "bossstop", "bossevent", "discord", "where", "pip", "coop", "daily", "cost", "targets", "all");

    /** What /cq test finish changed, so /cq test unfinish can put it back exactly. */
    private record Undo(List<String> completed, int sideDone) {
    }

    private final CQuestsPlugin plugin;
    private final Map<String, Undo> undo = new ConcurrentHashMap<>();

    TestCommand(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    void help(CommandSender s) {
        plugin.send(s, """
                <gold><bold>CQuests test commands</bold></gold> <gray>(op only, they act on you)
                <yellow>/cq test messages</yellow> <gray>show every message from messages.yml
                <yellow>/cq test welcome</yellow> <gray>show the new player guide
                <yellow>/cq test celebrate</yellow> <gray>play the big quest animation
                <yellow>/cq test chapter <number></yellow> <gray>play a chapter complete animation
                <yellow>/cq test ending</yellow> <gray>play the ending cinematic (no rewards)
                <yellow>/cq test achievement <chapter|end|reset></yellow> <gray>give an achievement, or take them all back
                <yellow>/cq test finish <npc></yellow> <gray>pretend you finished a villager, so it disappears for you
                <yellow>/cq test unfinish <npc></yellow> <gray>undo that, the villager comes back
                <yellow>/cq test roam <npc></yellow> <gray>move a scattered villager to a new spot now
                <yellow>/cq test book</yellow> <gray>read your Your Story book as it is so far
                <yellow>/cq test boss <quest></yellow> <gray>start that boss fight next to you (any game mode, nothing counts; creative to just watch)
                <yellow>/cq test bossphase</yellow> <gray>jump your test boss to half health: rage, minions and events
                <yellow>/cq test bossstop</yellow> <gray>end your boss fight
                <yellow>/cq test bossevent <lightning|darkness|slowness|levitate|roar></yellow> <gray>feel one boss event
                <yellow>/cq test discord <chapter|boss|streak|journey></yellow> <gray>send a sample post to your Discord webhook
                <yellow>/cq test where</yellow> <gray>show how players are pointed to their next villager
                <yellow>/cq test pip <bow|sword></yellow> <gray>a test boss with Pip fighting next to you
                <yellow>/cq test coop</yellow> <gray>start a co-op daily (bring friends) and see how it counts
                <yellow>/cq test daily</yellow> <gray>see today's daily and money roll for you
                <yellow>/cq test cost <chapter></yellow> <gray>what a chapter costs and what your balance reads
                <yellow>/cq test targets</yellow> <gray>check every quest asks for real things this server version has
                <yellow>/cq test all</yellow> <gray>list every boss you can test""");
    }

    void run(CommandSender sender, String[] args) {
        if (args.length < 2) {
            help(sender);
            return;
        }
        String action = args[1].toLowerCase(Locale.ROOT);
        if (action.equals("messages")) {
            messages(sender);
            return;
        }
        if (action.equals("targets")) {
            targets(sender);
            return;
        }
        if (!(sender instanceof Player player)) {
            plugin.send(sender, "<red>Run this one in game; it plays on you.");
            return;
        }
        String arg = args.length > 2 ? args[2] : "";
        Sched.entity(player, () -> {
            switch (action) {
                case "welcome" -> player.sendMessage(Text.mm(plugin.questManager().fill(plugin.settings().msg("first-join", ""), player)));
                case "celebrate" -> celebrate(player);
                case "chapter" -> chapter(player, arg);
                case "ending" -> {
                    plugin.finale().play(player, true);
                    plugin.send(player, "<gray>Playing the ending as a preview: no rewards, no achievement.");
                }
                case "achievement" -> achievement(player, arg);
                case "finish" -> finish(player, arg);
                case "unfinish" -> unfinish(player, arg);
                case "roam" -> roam(player, arg);
                case "book" -> StoryBook.open(plugin, player);
                case "boss" -> {
                    if (arg.isBlank()) plugin.send(player, "<yellow>/cq test boss <quest></yellow> <gray>Bosses: <white>" + String.join(", ", plugin.adventures().bossIds()));
                    else if (!plugin.adventures().testBoss(player, arg)) plugin.send(player, "<yellow>The boss could not start. Stand on open, solid ground with space around you, not in Peaceful.");
                }
                case "bossphase" -> { if (!plugin.adventures().testPhase(player)) plugin.send(player, "<yellow>Start one first with /cq test boss <quest>."); }
                case "bossstop" -> plugin.send(player, plugin.adventures().testStop(player) ? "<gray>Boss fight ended." : "<gray>No boss fight is running for you.");
                case "bossevent" -> { if (!plugin.adventures().testEvent(player, arg)) plugin.send(player, "<yellow>Events: " + String.join(", ", com.cquests.adventure.QuestAdventures.EVENTS)); }
                case "discord" -> discord(player, arg);
                case "pip" -> { if (!plugin.adventures().testPip(player, arg)) plugin.send(player, "<yellow>The test fight could not start. Stand on open, solid ground, not in Peaceful."); }
                case "coop" -> coop(player);
                case "daily" -> daily(player);
                case "cost" -> cost(player, arg);
                case "where" -> plugin.directions().explain(player, true);
                case "all" -> {
                    plugin.send(player, "<gold>Every boss</gold> <gray>(click to start a test fight)");
                    for (String id : plugin.adventures().bossIds()) {
                        Quest q = plugin.quests().get(id);
                        player.sendMessage(Text.mm("<yellow><click:run_command:'/cq test boss " + id + "'><hover:show_text:'Start this test fight'> ▶ " + id
                                + "</hover></click> <gray>" + (q == null ? "(chapter switched off)" : "Chapter " + q.chapter() + ": " + Text.escape(q.name()))));
                    }
                    plugin.send(player, "<gray>Also: /cq test celebrate, chapter <n>, ending, bossevent <event>, discord <event>, where, welcome.");
                }
                default -> help(player);
            }
        });
    }

    private void coop(Player player) {
        Quest quest = null;
        for (Quest q : plugin.quests().dailyPool()) if (plugin.quests().together(q.id()) > 1) { quest = q; break; }
        if (quest == null) { plugin.send(player, "<yellow>No co-op quests in quests.yml (together: 2 or more)."); return; }
        var data = plugin.questManager().data(player);
        if (!data.isActive(quest.id())) plugin.questManager().forceAccept(player, quest);
        plugin.send(player, "<gold>" + Text.escape(quest.name()) + "</gold> <gray>needs <white>" + plugin.quests().together(quest.id())
                + "</white> players. Friends near you now: <white>" + plugin.questManager().nearbyPlayers(player)
                + "</white>. Progress only counts while they do the same thing within 5 seconds. Drop it with /quests abandon.");
    }

    private void daily(Player player) {
        var pool = plugin.quests().dailyPool();
        if (pool.isEmpty()) { plugin.send(player, "<yellow>No daily quests."); return; }
        long day = System.currentTimeMillis() / 86_400_000L;
        var rnd = new java.util.Random(player.getUniqueId().getLeastSignificantBits() ^ day * 1_000_003L);
        Quest quest = pool.get(rnd.nextInt(pool.size()));
        var reward = plugin.questManager().dailyReward(player, quest);
        plugin.send(player, "<gold>A daily you could get today:</gold> <white>" + Text.escape(quest.name()) + "</white> <gray>• pays <green>$"
                + Text.formatMoney(reward.money()) + "</green> <gray>(base $" + Text.formatMoney(quest.reward().money()) + "). Each player gets their own daily and money roll.");
    }

    private void cost(Player player, String arg) {
        int chapter;
        try { chapter = Integer.parseInt(arg.isBlank() ? "2" : arg); } catch (NumberFormatException e) { plugin.send(player, "<red>/cq test cost <chapter>"); return; }
        Quest first = null;
        for (Quest q : plugin.quests().story()) if (q.chapter() == chapter) { first = q; break; }
        long cost = first == null ? com.cquests.quest.QuestManager.chapterCostFor(plugin, chapter) : plugin.questManager().chapterCost(first);
        double balance = new com.cquests.farm.EconomyBridge().balance(player);
        plugin.send(player, "<gold>Chapter " + chapter + "</gold> <gray>costs <white>" + Text.compact(cost) + "</white>. Your balance reads <white>"
                + (Double.isFinite(balance) ? Text.compact((long) balance) : "nothing (set economy.balance-placeholder or install Vault)") + "</white>.");
    }

    private void targets(CommandSender sender) {
        List<Quest> sample = new ArrayList<>(plugin.quests().story());
        sample.addAll(plugin.quests().dailyPool());
        for (NpcDef npc : plugin.npcs().all()) for (int i = 1; i <= 5; i++) { Quest q = plugin.quests().side(npc.id(), i); if (q != null) sample.add(q); }
        int checked = 0, bad = 0;
        for (Quest quest : sample) for (var objective : quest.objectives()) {
            checked++;
            String problem = com.cquests.quest.HowTo.problem(objective);
            if (problem != null && bad++ < 20) plugin.send(sender, "<red>" + quest.id() + "</red> <gray>" + Text.escape(objective.target().spec()) + ": " + Text.escape(problem));
        }
        plugin.send(sender, (bad == 0 ? "<green>" : "<yellow>") + "Checked " + checked + " objectives against this server's own items, blocks, mobs and recipes: "
                + (bad == 0 ? "all real." : bad + " problems."));
    }

    private void discord(Player player, String what) {
        var hook = plugin.discord();
        if (hook == null || !hook.enabled()) { plugin.send(player, "<yellow>Set discord.webhook-url in config.yml and /cq reload first."); return; }
        switch (what.toLowerCase(Locale.ROOT)) {
            case "boss" -> hook.bossDefeated(player, "Gorehorn, the Iron Tusk");
            case "streak" -> hook.dailyStreak(player, 7);
            case "journey" -> hook.journeyFinished(player);
            default -> hook.chapterComplete(player, 1, plugin.quests().chapterName(1));
        }
        plugin.send(player, "<green>Sample post sent to Discord. <gray>(Event switches under discord.events still apply.)");
    }

    // ------------------------------------------------------------------ messages

    private void messages(CommandSender sender) {
        Player player = sender instanceof Player p ? p : null;
        String name = player == null ? "Steve" : player.getName();
        QuestManager qm = plugin.questManager();
        plugin.send(sender, "<gold><bold>Every message</bold></gold> <gray>(sample values filled in)");
        plugin.send(sender, "<gray>Name tag: " + plugin.settings().npcNameFormat
                .replace("<name>", "Stephan").replace("<level>", "0").replace("<title>", " <gray>Keeper of the Road</gray>"));
        for (Map.Entry<String, String> entry : new TreeMap<>(plugin.settings().messages()).entrySet()) {
            String key = entry.getKey();
            if (key.equals("first-join") || entry.getValue().isBlank()) {
                continue;
            }
            String text = entry.getValue()
                    .replace("<quest>", "Touch Grass")
                    .replace("<npc>", plugin.npcs().mention("stephan"))
                    .replace("<player>", Text.escape(name))
                    .replace("<time>", "3h 20m")
                    .replace("<gate>", "jerry")
                    .replace("<left>", "5")
                    .replace("<amount>", "8")
                    .replace("<item>", "bread")
                    .replace("<have>", "8")
                    .replace("<need>", "16")
                    .replace("{player}", Text.escape(name))
                    .replace("{server}", Text.escape(plugin.settings().serverName));
            text = player == null ? text : qm.fill(text, player);
            sender.sendMessage(Text.mm("<dark_gray>[" + key + "]</dark_gray>"));
            if (key.startsWith("npc-")) {
                sender.sendMessage(Text.mm(plugin.settings().npcChatFormat.replace("<name>", "Stephan").replace("<text>", text)));
            } else if (key.endsWith("-title") || key.endsWith("-description")) {
                sender.sendMessage(Text.mm("<gray>Achievement text: <white>" + Text.escape(text)));
            } else {
                plugin.send(sender, text);
            }
        }
        plugin.send(sender, "<gray>See the new player guide with <yellow>/cq test welcome</yellow>.");
    }

    // ------------------------------------------------------------------ animations

    private void celebrate(Player player) {
        Quest quest = plugin.quests().story().stream().filter(Quest::big).findFirst()
                .orElse(plugin.quests().story().isEmpty() ? null : plugin.quests().story().get(0));
        if (quest == null) {
            plugin.send(player, "<red>There are no story quests.");
            return;
        }
        plugin.finale().celebrate(player, quest);
    }

    private void chapter(Player player, String arg) {
        int chapter = parse(arg, 1);
        Quest last = null;
        for (Quest quest : plugin.quests().story()) {
            if (quest.chapter() == chapter) {
                last = quest;
            }
        }
        if (last == null) {
            plugin.send(player, "<red>There is no chapter " + chapter + ".");
            return;
        }
        plugin.finale().chapterComplete(player, last, plugin.quests().nextStory(last));
    }

    // ------------------------------------------------------------------ achievements

    private void achievement(Player player, String arg) {
        if (arg.equalsIgnoreCase("reset")) {
            int revoked = plugin.finale().achievements().revokeAll(player);
            plugin.send(player, revoked == 0 ? "<gray>You had no CQuests achievements." : "<green>Took your CQuests achievements back. You can earn them again.");
            return;
        }
        int chapter = arg.equalsIgnoreCase("end") ? 0 : parse(arg, -1);
        if (chapter < 0) {
            plugin.send(player, "<red>Usage: /cq test achievement <chapter number|end|reset>");
            return;
        }
        if (!plugin.finale().achievements().grantForTest(player, chapter)) {
            plugin.send(player, "<red>That achievement isn't loaded. Is there a chapter " + chapter + "?");
        }
    }

    // ------------------------------------------------------------------ disappearing villagers

    private void finish(Player player, String id) {
        NpcDef npc = npc(player, id);
        if (npc == null) {
            return;
        }
        List<Quest> own = plugin.quests().storyFrom(npc.id());
        if (own.isEmpty()) {
            plugin.send(player, "<red>" + Text.escape(npc.name()) + " has no story quests, so it never disappears.");
            return;
        }
        PlayerData data = plugin.questManager().data(player);
        List<String> changed = new ArrayList<>();
        synchronized (data) {
            for (Quest quest : own) {
                if (!data.isCompleted(quest.id())) {
                    data.complete(quest.id(), true);
                    changed.add(quest.id());
                }
            }
            undo.putIfAbsent(key(player, npc), new Undo(changed, data.sideDone(npc.id())));
            Quest next = plugin.quests().nextStory(own.get(own.size() - 1));
            data.setSideDone(npc.id(), plugin.quests().sidePerNpc());
            if (next != null) {
                data.setSideDone(npc.id(), Math.max(data.sideDone(npc.id()), plugin.questManager().sideRequired(next)));
            }
        }
        plugin.store().saveNow(data);
        plugin.visibility().refresh(player);
        if (plugin.questManager().finishedWith(data, npc)) {
            plugin.send(player, "<green>" + Text.escape(npc.name()) + " is finished for you."
                    + (plugin.settings().hideFinishedVillagers ? " It is hidden if no active quest needs it." : " Enable spawning.hide-finished-villagers to hide it.")
                    + " <gray>Undo with <yellow>/cq test unfinish " + npc.id() + "</yellow>.");
        } else {
            plugin.send(player, "<yellow>" + Text.escape(npc.name()) + " still shows because one of your active quests needs it.");
        }
    }

    private void unfinish(Player player, String id) {
        NpcDef npc = npc(player, id);
        if (npc == null) {
            return;
        }
        Undo previous = undo.remove(key(player, npc));
        if (previous == null) {
            plugin.send(player, "<red>Nothing to undo for " + Text.escape(npc.name()) + ". Use /cq test finish first.");
            return;
        }
        PlayerData data = plugin.questManager().data(player);
        synchronized (data) {
            previous.completed().forEach(data::uncomplete);
            data.setSideDone(npc.id(), previous.sideDone());
        }
        plugin.store().saveNow(data);
        plugin.visibility().refresh(player);
        plugin.send(player, "<green>" + Text.escape(npc.name()) + " is back, and your progress is as it was.");
    }

    private void roam(Player player, String id) {
        NpcDef npc = npc(player, id);
        if (npc == null) {
            return;
        }
        if (plugin.spawns().roamNow(npc)) {
            plugin.send(player, "<green>" + Text.escape(npc.name()) + " is moving to a new spot in its area.");
        } else {
            plugin.send(player, "<red>" + Text.escape(npc.name()) + " has no area to roam in. Place it with /cq scatter first.");
        }
    }

    // ------------------------------------------------------------------ helpers

    private NpcDef npc(Player player, String id) {
        NpcDef npc = plugin.npcs().get(id.toLowerCase(Locale.ROOT));
        if (npc == null) {
            plugin.send(player, "<red>Unknown villager '" + Text.escape(id) + "'. See /cq npc list.");
        }
        return npc;
    }

    private static String key(Player player, NpcDef npc) {
        UUID uuid = player.getUniqueId();
        return uuid + ":" + npc.id();
    }

    private static int parse(String text, int fallback) {
        try {
            return Integer.parseInt(text);
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
}
