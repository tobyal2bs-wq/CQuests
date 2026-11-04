package com.cquests.command;

import com.cquests.T;

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
            "finish", "unfinish", "roam", "book", "boss", "bossphase", "bossstop", "bossevent", "discord", "where", "pip", "companion", "bossnext", "coop", "daily", "cost", "targets", "worldboss", "worldbossnext", "worldbossphase", "worldbossstop", "tutorial", "season", "invite", "all");

    /** What /cq test finish changed, so /cq test unfinish can put it back exactly. */
    private record Undo(List<String> completed, int sideDone) {
    }

    private final CQuestsPlugin plugin;
    private final Map<String, Undo> undo = new ConcurrentHashMap<>();
    private final Map<java.util.UUID, Integer> nextBoss = new ConcurrentHashMap<>();
    private final Map<java.util.UUID, Integer> nextWorldBoss = new ConcurrentHashMap<>();

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
                <yellow>/cq test bossnext</yellow> <gray>stop the current fight and start the next boss, one by one through all of them
                <yellow>/cq test companion</yellow> <gray>Pip follows you for a minute like on an escort quest
                <yellow>/cq test worldboss <boss></yellow> <gray>a world boss in front of you inside a 25 block circle, nothing paid
                <yellow>/cq test worldbossnext</yellow> <gray>go through all world bosses one by one
                <yellow>/cq test worldbossphase</yellow> <gray>drop your test world boss to half health; <yellow>worldbossstop</yellow> <gray>ends it
                <yellow>/cq test tutorial</yellow> <gray>start the tutorial quest again
                <yellow>/cq test season <id></yellow> <gray>see a season and try its daily and boss
                <yellow>/cq test invite</yellow> <gray>see what invite rewards both players get
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
            plugin.send(sender, T.t("test-command.run-this-one-in-game", "<red>Run this one in game; it plays on you."));
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
                    plugin.send(player, T.t("test-command.playing-the-ending-as-a", "<gray>Playing the ending as a preview: no rewards, no achievement."));
                }
                case "achievement" -> achievement(player, arg);
                case "finish" -> finish(player, arg);
                case "unfinish" -> unfinish(player, arg);
                case "roam" -> roam(player, arg);
                case "book" -> StoryBook.open(plugin, player);
                case "boss" -> {
                    if (arg.isBlank()) plugin.send(player, T.t("test-command.cq-test-boss-bosses", "<yellow>/cq test boss <quest></yellow> <gray>Bosses: <white><bossids>", "bossids", String.join(", ", plugin.adventures().bossIds())));
                    else if (!plugin.adventures().testBoss(player, arg)) plugin.send(player, T.t("test-command.the-boss-could-not-start", "<yellow>The boss could not start. Stand on open, solid ground with space around you, not in Peaceful."));
                }
                case "bossphase" -> { if (!plugin.adventures().testPhase(player)) plugin.send(player, T.t("test-command.start-one-first-with-cq", "<yellow>Start one first with /cq test boss <quest>.")); }
                case "bossstop" -> plugin.send(player, plugin.adventures().testStop(player) ? "<gray>Boss fight ended." : "<gray>No boss fight is running for you.");
                case "bossevent" -> { if (!plugin.adventures().testEvent(player, arg)) plugin.send(player, T.t("test-command.events", "<yellow>Events: <events>", "events", String.join(", ", com.cquests.adventure.QuestAdventures.EVENTS))); }
                case "discord" -> discord(player, arg);
                case "pip" -> { if (!plugin.adventures().testPip(player, arg)) plugin.send(player, T.t("test-command.the-test-fight-could-not", "<yellow>The test fight could not start. Stand on open, solid ground, not in Peaceful.")); }
                case "companion" -> plugin.send(player, plugin.adventures().testCompanion(player)
                        ? "<gray>Pip follows you for a minute, like on an escort quest. <yellow>/cq test bossstop</yellow> sends Pip home."
                        : "<yellow>Pip could not come. Stand on open, solid ground.");
                case "bossnext" -> bossNext(player);
                case "worldboss" -> plugin.worldBosses().test(player, arg);
                case "worldbossnext" -> worldBossNext(player);
                case "worldbossphase" -> plugin.send(player, plugin.worldBosses().testPhase(player) ? "<gray>Your test world boss drops to half health: rage, minions and faster abilities." : "<yellow>Start one first with /cq test worldboss <boss>.");
                case "worldbossstop" -> plugin.send(player, plugin.worldBosses().testStop(player) ? "<gray>Test world boss ended." : "<gray>No test world boss is running for you.");
                case "tutorial" -> tutorial(player);
                case "season" -> season(player, arg);
                case "invite" -> plugin.invites().test(player);
                case "coop" -> coop(player);
                case "daily" -> daily(player);
                case "cost" -> cost(player, arg);
                case "where" -> plugin.directions().explain(player, true);
                case "all" -> {
                    plugin.send(player, T.t("test-command.every-boss-click-to-start", "<gold>Every boss</gold> <gray>(click to start a test fight)"));
                    for (String id : plugin.adventures().bossIds()) {
                        Quest q = plugin.quests().get(id);
                        player.sendMessage(Text.mm(T.t("test-command.line", "<yellow><click:run_command:'/cq test boss <id>'><hover:show_text:'Start this test fight'> ▶ <id></hover></click> <gray><name>", "id", id, "name", (q == null ? "(chapter switched off)" : "Chapter " + q.chapter() + ": " + Text.escape(q.name())))));
                    }
                    plugin.send(player, T.t("test-command.also-cq-test-worldbossnext-worldboss", "<gray>Also: /cq test worldbossnext, worldboss <id>, tutorial, season <id>, invite, bossnext, companion, pip <bow|sword>, celebrate, chapter <n>, ending, bossevent <event>, discord <event>, where, welcome."));
                }
                default -> help(player);
            }
        });
    }

    /** Each call stops the current test fight and starts the next boss, so every boss and mini boss can be seen in turn. */
    private void bossNext(Player player) {
        List<String> ids = new java.util.ArrayList<>(plugin.adventures().bossIds());
        if (ids.isEmpty()) { plugin.send(player, T.t("test-command.no-bosses-in-bosses-yml", "<yellow>No bosses in bosses.yml.")); return; }
        int index = Math.floorMod(nextBoss.merge(player.getUniqueId(), 1, Integer::sum) - 1, ids.size());
        plugin.adventures().testStop(player);
        String id = ids.get(index);
        plugin.send(player, T.t("test-command.boss-run-cq-test-bossnext", "<gold>Boss <index>/<size>:</gold> <white><id> <gray>(run /cq test bossnext again for the next one)", "index", (index + 1), "size", ids.size(), "id", id));
        if (!plugin.adventures().testBoss(player, id)) plugin.send(player, T.t("test-command.the-boss-could-not-start", "<yellow>The boss could not start. Stand on open, solid ground with space around you, not in Peaceful."));
    }

    /** Each call ends your test world boss and starts the next one, so all of them can be seen in turn. */
    private void worldBossNext(Player player) {
        List<String> ids = plugin.worldBosses().ids();
        if (ids.isEmpty()) { plugin.send(player, T.t("test-command.no-bosses-in-worldbosses-yml", "<yellow>No bosses in worldbosses.yml.")); return; }
        int index = Math.floorMod(nextWorldBoss.merge(player.getUniqueId(), 1, Integer::sum) - 1, ids.size());
        plugin.worldBosses().testStop(player);
        plugin.send(player, T.t("test-command.world-boss-run-cq-test", "<gold>World boss <index>/<size>:</gold> <white><index2> <gray>(run /cq test worldbossnext again for the next one)", "index", (index + 1), "size", ids.size(), "index2", ids.get(index)));
        plugin.worldBosses().test(player, ids.get(index));
    }

    /** Starts the tutorial quest again for you, so you can play it through. */
    private void tutorial(Player player) {
        String id = plugin.getConfig().getString("quests.tutorial-quest", "tutorial");
        Quest quest = id == null || id.isBlank() ? null : plugin.quests().get(id);
        if (quest == null) { plugin.send(player, T.t("test-command.no-tutorial-quest-quests-tutorial", "<yellow>No tutorial quest (quests.tutorial-quest in config.yml).")); return; }
        var data = plugin.questManager().data(player);
        synchronized (data) { data.remove(quest.id()); data.uncomplete(quest.id()); }
        plugin.questManager().forceAccept(player, quest);
        plugin.send(player, T.t("test-command.tutorial-started-it-pays-out", "<gray>Tutorial started: <white><name></white>. It pays out when every step is done.", "name", Text.escape(quest.name())));
    }

    /** Shows whether a season is on and gives you one of its daily quests to try. */
    private void season(Player player, String id) {
        if (id.isBlank()) { plugin.send(player, T.t("test-command.cq-test-season-seasons", "<yellow>/cq test season <id></yellow> <gray>Seasons: <list>", "list", String.join(", ", plugin.seasons().ids()))); return; }
        String season = id.toLowerCase(java.util.Locale.ROOT);
        plugin.send(player, T.t("test-command.is", "<season> <gray>is <white><season2></white><running>", "season", plugin.seasons().name(season), "season2", plugin.seasons().mode(season), "running", (plugin.seasons().active(season) ? " <green>(running)" : " <dark_gray>(not running)")));
        Quest pick = null;
        for (Quest q : plugin.quests().dailyPool()) if (season.equals(plugin.quests().season(q.id()))) { pick = q; break; }
        if (pick == null) plugin.send(player, T.t("test-command.no-seasonal-dailies-for-in", "<gray>No seasonal dailies for <season> in quests.yml.", "season", Text.escape(season)));
        else {
            var data = plugin.questManager().data(player);
            if (!data.isActive(pick.id())) plugin.questManager().forceAccept(player, pick);
            plugin.send(player, T.t("test-command.gave-you-the-seasonal-daily", "<gray>Gave you the seasonal daily <white><name></white>. <gray>Abandon it with /quests abandon <id>", "name", Text.escape(pick.name()), "id", pick.id()));
        }
        for (var def : plugin.worldBosses().defs().values()) if (season.equals(def.season()))
            player.sendMessage(Text.mm(T.t("test-command.seasonal-boss", "<yellow><click:run_command:'/cq test worldboss <id>'><hover:show_text:'Try this boss'> ▶ Seasonal boss: </hover></click><boss>", "id", def.id(), "boss", def.name())));
    }

    private void coop(Player player) {
        Quest quest = null;
        for (Quest q : plugin.quests().dailyPool()) if (plugin.quests().together(q.id()) > 1) { quest = q; break; }
        if (quest == null) { plugin.send(player, T.t("test-command.no-co-op-quests-in", "<yellow>No co-op quests in quests.yml (together: 2 or more).")); return; }
        var data = plugin.questManager().data(player);
        if (!data.isActive(quest.id())) plugin.questManager().forceAccept(player, quest);
        plugin.send(player, T.t("test-command.needs-players-friends-near-you", "<gold><name></gold> <gray>needs <white><id></white> players. Friends near you now: <white><player></white>. Progress only counts while they do the same thing within 5 seconds. Drop it with /quests abandon.", "name", Text.escape(quest.name()), "id", plugin.quests().together(quest.id()), "player", plugin.questManager().nearbyPlayers(player)));
    }

    private void daily(Player player) {
        var pool = plugin.quests().dailyPool();
        if (pool.isEmpty()) { plugin.send(player, T.t("test-command.no-daily-quests", "<yellow>No daily quests.")); return; }
        long day = System.currentTimeMillis() / 86_400_000L;
        var rnd = new java.util.Random(player.getUniqueId().getLeastSignificantBits() ^ day * 1_000_003L);
        Quest quest = pool.get(rnd.nextInt(pool.size()));
        var reward = plugin.questManager().dailyReward(player, quest);
        plugin.send(player, T.t("test-command.a-daily-you-could-get", "<gold>A daily you could get today:</gold> <white><name></white> <gray>• pays <green>$<money></green> <gray>(base $<money2>). Each player gets their own daily and money roll.", "name", Text.escape(quest.name()), "money", Text.formatMoney(reward.money()), "money2", Text.formatMoney(quest.reward().money())));
    }

    private void cost(Player player, String arg) {
        int chapter;
        try { chapter = Integer.parseInt(arg.isBlank() ? "2" : arg); } catch (NumberFormatException e) { plugin.send(player, T.t("test-command.cq-test-cost", "<red>/cq test cost <chapter>")); return; }
        Quest first = null;
        for (Quest q : plugin.quests().story()) if (q.chapter() == chapter) { first = q; break; }
        long cost = first == null ? com.cquests.quest.QuestManager.chapterCostFor(plugin, chapter) : plugin.questManager().chapterCost(first);
        double balance = new com.cquests.farm.EconomyBridge().balance(player);
        plugin.send(player, T.t("test-command.chapter-costs-your-balance-reads", "<gold>Chapter <chapter></gold> <gray>costs <white><cost></white>. Your balance reads <white><place></white>.", "chapter", chapter, "cost", Text.compact(cost), "place", (Double.isFinite(balance) ? Text.compact((long) balance) : "nothing (set economy.balance-placeholder or install Vault)")));
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
        plugin.send(sender, T.t("test-command.checked-objectives-against-this-server", "<yellow>Checked <checked> objectives against this server's own items, blocks, mobs and recipes: <problems>", "yellow", (bad == 0 ? "<green>" : "<yellow>"), "checked", checked, "problems", (bad == 0 ? "all real." : bad + " problems.")));
    }

    private void discord(Player player, String what) {
        var hook = plugin.discord();
        if (hook == null || !hook.enabled()) { plugin.send(player, T.t("test-command.set-discord-webhook-url-in", "<yellow>Set discord.webhook-url in config.yml and /cq reload first.")); return; }
        switch (what.toLowerCase(Locale.ROOT)) {
            case "boss" -> hook.bossDefeated(player, "Gorehorn, the Iron Tusk");
            case "streak" -> hook.dailyStreak(player, 7);
            case "journey" -> hook.journeyFinished(player);
            default -> hook.chapterComplete(player, 1, plugin.quests().chapterName(1));
        }
        plugin.send(player, T.t("test-command.sample-post-sent-to-discord", "<green>Sample post sent to Discord. <gray>(Event switches under discord.events still apply.)"));
    }

    // ------------------------------------------------------------------ messages

    private void messages(CommandSender sender) {
        Player player = sender instanceof Player p ? p : null;
        String name = player == null ? "Steve" : player.getName();
        QuestManager qm = plugin.questManager();
        plugin.send(sender, T.t("test-command.every-message-sample-values-filled", "<gold><bold>Every message</bold></gold> <gray>(sample values filled in)"));
        plugin.send(sender, T.t("test-command.name-tag", "<gray>Name tag: <place>", "place", plugin.settings().npcNameFormat
                .replace("<name>", "Stephan").replace("<level>", "0").replace("<title>", " <gray>Keeper of the Road</gray>")));
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
                sender.sendMessage(Text.mm(T.t("test-command.achievement-text", "<gray>Achievement text: <white><text>", "text", Text.escape(text))));
            } else {
                plugin.send(sender, text);
            }
        }
        plugin.send(sender, T.t("test-command.see-the-new-player-guide", "<gray>See the new player guide with <yellow>/cq test welcome</yellow>."));
    }

    // ------------------------------------------------------------------ animations

    private void celebrate(Player player) {
        Quest quest = plugin.quests().story().stream().filter(Quest::big).findFirst()
                .orElse(plugin.quests().story().isEmpty() ? null : plugin.quests().story().get(0));
        if (quest == null) {
            plugin.send(player, T.t("test-command.there-are-no-story-quests", "<red>There are no story quests."));
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
            plugin.send(player, T.t("test-command.there-is-no-chapter", "<red>There is no chapter <chapter>.", "chapter", chapter));
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
            plugin.send(player, T.t("test-command.usage-cq-test-achievement", "<red>Usage: /cq test achievement <chapter number|end|reset>"));
            return;
        }
        if (!plugin.finale().achievements().grantForTest(player, chapter)) {
            plugin.send(player, T.t("test-command.that-achievement-isn-t-loaded", "<red>That achievement isn't loaded. Is there a chapter <chapter>?", "chapter", chapter));
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
            plugin.send(player, T.t("test-command.has-no-story-quests-so", "<red><name> has no story quests, so it never disappears.", "name", Text.escape(npc.name())));
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
            plugin.send(player, T.t("test-command.is-finished-for-you-undo", "<green><name> is finished for you.<it> <gray>Undo with <yellow>/cq test unfinish <id></yellow>.", "name", Text.escape(npc.name()), "it", (plugin.settings().hideFinishedVillagers ? " It is hidden if no active quest needs it." : " Enable spawning.hide-finished-villagers to hide it."), "id", npc.id()));
        } else {
            plugin.send(player, T.t("test-command.still-shows-because-one-of", "<yellow><name> still shows because one of your active quests needs it.", "name", Text.escape(npc.name())));
        }
    }

    private void unfinish(Player player, String id) {
        NpcDef npc = npc(player, id);
        if (npc == null) {
            return;
        }
        Undo previous = undo.remove(key(player, npc));
        if (previous == null) {
            plugin.send(player, T.t("test-command.nothing-to-undo-for-use", "<red>Nothing to undo for <name>. Use /cq test finish first.", "name", Text.escape(npc.name())));
            return;
        }
        PlayerData data = plugin.questManager().data(player);
        synchronized (data) {
            previous.completed().forEach(data::uncomplete);
            data.setSideDone(npc.id(), previous.sideDone());
        }
        plugin.store().saveNow(data);
        plugin.visibility().refresh(player);
        plugin.send(player, T.t("test-command.is-back-and-your-progress", "<green><name> is back, and your progress is as it was.", "name", Text.escape(npc.name())));
    }

    private void roam(Player player, String id) {
        NpcDef npc = npc(player, id);
        if (npc == null) {
            return;
        }
        if (plugin.spawns().roamNow(npc)) {
            plugin.send(player, T.t("test-command.is-moving-to-a-new", "<green><name> is moving to a new spot in its area.", "name", Text.escape(npc.name())));
        } else {
            plugin.send(player, T.t("test-command.has-no-area-to-roam", "<red><name> has no area to roam in. Place it with /cq scatter first.", "name", Text.escape(npc.name())));
        }
    }

    // ------------------------------------------------------------------ helpers

    private NpcDef npc(Player player, String id) {
        NpcDef npc = plugin.npcs().get(id.toLowerCase(Locale.ROOT));
        if (npc == null) {
            plugin.send(player, T.t("test-command.unknown-villager-see-cq-npc", "<red>Unknown villager '<id>'. See /cq npc list.", "id", Text.escape(id)));
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
