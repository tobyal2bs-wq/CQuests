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
            "finish", "unfinish", "roam", "book");

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
                <yellow>/cq test book</yellow> <gray>read your Your Story book as it is so far""");
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
                default -> help(player);
            }
        });
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
            if (next != null) {
                data.setSideDone(npc.id(), Math.max(data.sideDone(npc.id()), plugin.questManager().sideRequired(next)));
            }
        }
        plugin.store().saveNow(data);
        plugin.visibility().refresh(player);
        if (plugin.questManager().finishedWith(data, npc)) {
            plugin.send(player, "<green>" + Text.escape(npc.name()) + " is finished for you and should vanish in a puff of smoke."
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
