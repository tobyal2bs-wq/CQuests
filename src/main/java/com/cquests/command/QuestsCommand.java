package com.cquests.command;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.Quest;
import com.cquests.quest.QuestManager;
import com.cquests.util.Text;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** /quests: the journal book, plus a chat list that also works anywhere a book cannot open. */
public final class QuestsCommand implements TabExecutor {

    private final CQuestsPlugin plugin;

    public QuestsCommand(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("Only players have a quest journal.");
            return true;
        }
        String sub = args.length == 0 ? "book" : args[0].toLowerCase(Locale.ROOT);
        switch (sub) {
            case "accept" -> {
                if (!plugin.dialogue().acceptPending(player)) {
                    plugin.send(player, "<red>There is no quest offer waiting. Click a villager first.");
                }
            }
            case "list" -> list(player);
            case "abandon" -> abandon(player, args);
            default -> plugin.book().open(player);
        }
        return true;
    }

    private void list(Player player) {
        QuestManager qm = plugin.questManager();
        PlayerData data = qm.data(player);
        List<Quest> active = qm.activeQuests(data);
        plugin.send(player, "<gold><bold>Your quests</bold></gold> <gray>(" + data.completedCount() + " done)");
        if (active.isEmpty()) {
            plugin.send(player, "<gray>No active quests. Talk to a villager at spawn.");
        }
        for (Quest quest : active) {
            ActiveQuest progress = data.active(quest.id());
            StringBuilder line = new StringBuilder("<yellow>• <white>" + Text.escape(quest.name()) + "</white> <dark_gray>Lv " + quest.level());
            if (progress != null) {
                for (int i = 0; i < quest.objectives().size(); i++) {
                    line.append("\n   <gray>").append(qm.objectiveLabel(quest.objectives().get(i))).append(' ')
                            .append(qm.objectiveDone(quest, progress, i) ? "<green>" : "<yellow>")
                            .append(progress.get(i)).append('/').append(quest.objectives().get(i).amount());
                }
            }
            plugin.send(player, line.toString());
        }
    }

    private void abandon(Player player, String[] args) {
        if (args.length < 2) {
            plugin.send(player, "<red>Usage: /quests abandon <quest id>");
            return;
        }
        Quest quest = plugin.quests().get(args[1]);
        if (quest == null || !plugin.questManager().data(player).isActive(quest.id())) {
            plugin.send(player, "<red>You don't have that quest.");
            return;
        }
        if (!plugin.questManager().abandon(player, quest)) {
            plugin.send(player, "<red>Story quests can't be abandoned.");
            return;
        }
        plugin.send(player, "<gray>Abandoned <white>" + Text.escape(quest.name()) + "</white>.");
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 1) {
            return filter(List.of("list", "accept", "abandon"), args[0]);
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("abandon") && sender instanceof Player player) {
            return filter(new ArrayList<>(plugin.questManager().data(player).active().keySet()), args[1]);
        }
        return List.of();
    }

    static List<String> filter(List<String> options, String prefix) {
        String lower = prefix.toLowerCase(Locale.ROOT);
        return options.stream().filter(o -> o.toLowerCase(Locale.ROOT).startsWith(lower)).limit(50).toList();
    }
}
