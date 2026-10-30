package com.cquests.command;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.npc.SpawnManager;
import com.cquests.npc.WorldGuardHook;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** /cq: NPC placement, region scattering, reloads and player data fixes. */
public final class AdminCommand implements TabExecutor {

    private final CQuestsPlugin plugin;
    private final Map<UUID, Location[]> selections = new ConcurrentHashMap<>();

    public AdminCommand(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 0) {
            help(sender);
            return true;
        }
        switch (args[0].toLowerCase(Locale.ROOT)) {
            case "reload" -> {
                plugin.reload();
                sender.sendMessage(Text.mm("<green>CQuests reloaded: " + plugin.npcs().all().size() + " NPCs, "
                        + plugin.quests().story().size() + " story quests, "
                        + String.format(Locale.ROOT, "%,d", plugin.quests().totalSide()) + " side quests."));
            }
            case "npc" -> npc(sender, args);
            case "pos1", "pos2" -> pos(sender, args[0].equalsIgnoreCase("pos1") ? 0 : 1);
            case "scatter" -> scatter(sender, args);
            case "player" -> player(sender, args);
            case "quest" -> quest(sender, args);
            case "finale" -> finale(sender, args);
            default -> help(sender);
        }
        return true;
    }

    private void help(CommandSender s) {
        s.sendMessage(Text.mm("""
                <gold><bold>CQuests admin</bold></gold>
                <yellow>/cq reload</yellow> <gray>reload configs, NPCs and quests
                <yellow>/cq npc list</yellow> <gray>NPCs and where they stand
                <yellow>/cq npc place <id></yellow> <gray>put an NPC where you stand
                <yellow>/cq npc remove <id></yellow> <gray>take an NPC off the map
                <yellow>/cq npc tp <id></yellow> <gray>teleport to an NPC
                <yellow>/cq pos1</yellow>, <yellow>/cq pos2</yellow> <gray>select a box for scattering
                <yellow>/cq scatter <ids|act1|act2|all> [wg-region]</yellow> <gray>spread NPCs in a region or your box
                <yellow>/cq player <name> reset|complete <quest>|give <quest>|resetdaily</yellow>
                <yellow>/cq quest <id></yellow> <gray>show a quest's details
                <yellow>/cq finale [player]</yellow> <gray>preview the ending cinematic"""));
    }

    private void npc(CommandSender sender, String[] args) {
        String action = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "list";
        if (action.equals("list")) {
            int placed = 0;
            StringBuilder out = new StringBuilder("<gold>NPCs</gold> <gray>(");
            List<String> rows = new ArrayList<>();
            for (NpcDef npc : plugin.npcs().all()) {
                boolean has = plugin.spawns().points().containsKey(npc.id());
                placed += has ? 1 : 0;
                rows.add((has ? "<green>" : "<red>") + npc.id() + "</" + (has ? "green" : "red") + ">");
            }
            out.append(placed).append('/').append(rows.size()).append(" placed)</gray>\n").append(String.join("<gray>, ", rows));
            sender.sendMessage(Text.mm(out.toString()));
            return;
        }
        if (args.length < 3) {
            sender.sendMessage(Text.mm("<red>Usage: /cq npc " + action + " <id>"));
            return;
        }
        NpcDef npc = plugin.npcs().get(args[2]);
        if (npc == null) {
            sender.sendMessage(Text.mm("<red>No NPC with id '" + Text.escape(args[2]) + "'. See /cq npc list."));
            return;
        }
        switch (action) {
            case "place" -> {
                if (!(sender instanceof Player player)) {
                    sender.sendMessage("Run this in game.");
                    return;
                }
                plugin.spawns().place(npc, player.getLocation());
                sender.sendMessage(Text.mm("<green>" + Text.escape(npc.name()) + " now stands here."));
            }
            case "remove" -> sender.sendMessage(Text.mm(plugin.spawns().remove(npc.id())
                    ? "<green>Removed " + Text.escape(npc.name()) + " from the map."
                    : "<gray>" + Text.escape(npc.name()) + " had no spawn point."));
            case "tp" -> {
                SpawnManager.Point point = plugin.spawns().points().get(npc.id());
                Location loc = point == null ? null : point.location();
                if (!(sender instanceof Player player) || loc == null) {
                    sender.sendMessage(Text.mm("<red>That NPC has no spawn point (or run this in game)."));
                    return;
                }
                player.teleportAsync(loc);
            }
            default -> help(sender);
        }
    }

    private void pos(CommandSender sender, int index) {
        if (!(sender instanceof Player player)) {
            sender.sendMessage("Run this in game.");
            return;
        }
        selections.computeIfAbsent(player.getUniqueId(), k -> new Location[2])[index] = player.getLocation().toBlockLocation();
        Location l = player.getLocation();
        sender.sendMessage(Text.mm("<green>pos" + (index + 1) + " set to " + l.getBlockX() + ", " + l.getBlockY() + ", " + l.getBlockZ()));
    }

    private void scatter(CommandSender sender, String[] args) {
        if (args.length < 2) {
            sender.sendMessage(Text.mm("<red>Usage: /cq scatter <id,id,...|act1|act2|all> [worldguard-region]"));
            return;
        }
        List<NpcDef> npcs = selectNpcs(args[1]);
        if (npcs.isEmpty()) {
            sender.sendMessage(Text.mm("<red>No NPCs matched '" + Text.escape(args[1]) + "'."));
            return;
        }
        World world;
        int[] box;
        if (args.length >= 3) {
            world = sender instanceof Player p ? p.getWorld() : Bukkit.getWorlds().get(0);
            if (args.length >= 4) {
                world = Bukkit.getWorld(args[3]);
            }
            if (world == null) {
                sender.sendMessage(Text.mm("<red>Unknown world."));
                return;
            }
            if (!WorldGuardHook.available()) {
                sender.sendMessage(Text.mm("<red>WorldGuard is not installed; use /cq pos1 and /cq pos2 instead."));
                return;
            }
            box = WorldGuardHook.bounds(world, args[2]);
            if (box == null) {
                sender.sendMessage(Text.mm("<red>No WorldGuard region '" + Text.escape(args[2]) + "' in " + world.getName() + "."));
                return;
            }
        } else {
            Location[] sel = sender instanceof Player p ? selections.get(p.getUniqueId()) : null;
            if (sel == null || sel[0] == null || sel[1] == null || !sel[0].getWorld().equals(sel[1].getWorld())) {
                sender.sendMessage(Text.mm("<red>Set /cq pos1 and /cq pos2 first, or name a WorldGuard region."));
                return;
            }
            world = sel[0].getWorld();
            box = new int[]{sel[0].getBlockX(), sel[0].getBlockY(), sel[0].getBlockZ(), sel[1].getBlockX(), sel[1].getBlockY(), sel[1].getBlockZ()};
        }
        sender.sendMessage(Text.mm("<gray>Scattering " + npcs.size() + " NPCs..."));
        plugin.spawns().scatter(npcs, world, box, sender);
    }

    private List<NpcDef> selectNpcs(String spec) {
        List<NpcDef> out = new ArrayList<>();
        String lower = spec.toLowerCase(Locale.ROOT);
        for (NpcDef npc : plugin.npcs().all()) {
            boolean match = switch (lower) {
                case "all" -> true;
                case "act1" -> npc.act() <= 1;
                case "act2" -> npc.act() >= 2;
                default -> false;
            };
            if (match) {
                out.add(npc);
            }
        }
        if (out.isEmpty()) {
            for (String id : lower.split(",")) {
                NpcDef npc = plugin.npcs().get(id.trim());
                if (npc != null) {
                    out.add(npc);
                }
            }
        }
        return out;
    }

    private void player(CommandSender sender, String[] args) {
        if (args.length < 3) {
            sender.sendMessage(Text.mm("<red>Usage: /cq player <name> reset|complete <quest>|give <quest>|resetdaily"));
            return;
        }
        Player target = Bukkit.getPlayerExact(args[1]);
        if (target == null) {
            sender.sendMessage(Text.mm("<red>That player is not online."));
            return;
        }
        PlayerData data = plugin.questManager().data(target);
        String action = args[2].toLowerCase(Locale.ROOT);
        Quest quest = args.length > 3 ? plugin.quests().get(args[3]) : null;
        switch (action) {
            case "reset" -> {
                data.reset();
                sender.sendMessage(Text.mm("<green>Reset all quest progress for " + target.getName() + "."));
            }
            case "resetdaily" -> {
                data.setLastDailyAt(0);
                sender.sendMessage(Text.mm("<green>" + target.getName() + " can take a new daily quest now."));
            }
            case "complete" -> {
                if (quest == null) {
                    sender.sendMessage(Text.mm("<red>Unknown quest."));
                    return;
                }
                synchronized (data) {
                    ActiveQuest active = data.active(quest.id());
                    if (active == null && quest.category() == QuestCategory.SIDE) {
                        data.setSideDone(quest.giver(), Math.max(data.sideDone(quest.giver()), quest.order()));
                    } else if (active == null) {
                        data.complete(quest.id(), true);
                    } else {
                        for (int i = 0; i < quest.objectives().size(); i++) {
                            active.set(i, quest.objectives().get(i).amount());
                        }
                        data.markDirty();
                    }
                }
                sender.sendMessage(Text.mm("<green>Done. If the quest was active it now waits for turn-in."));
            }
            case "give" -> {
                if (quest == null) {
                    sender.sendMessage(Text.mm("<red>Unknown quest."));
                    return;
                }
                data.uncomplete(quest.id());
                if (quest.category() == QuestCategory.SIDE) {
                    data.setSideDone(quest.giver(), Math.min(data.sideDone(quest.giver()), quest.order() - 1));
                }
                plugin.questManager().accept(target, quest);
                sender.sendMessage(Text.mm("<green>Gave " + Text.escape(quest.name()) + " to " + target.getName() + "."));
            }
            default -> sender.sendMessage(Text.mm("<red>Unknown action."));
        }
        plugin.visibility().refresh(target);
    }

    private void finale(CommandSender sender, String[] args) {
        Player target = args.length > 1 ? Bukkit.getPlayerExact(args[1]) : sender instanceof Player p ? p : null;
        if (target == null) {
            sender.sendMessage(Text.mm("<red>Usage: /cq finale [player]"));
            return;
        }
        plugin.finale().play(target, true);
        sender.sendMessage(Text.mm("<green>Playing the ending for " + target.getName() + " (preview, no advancement)."));
    }

    private void quest(CommandSender sender, String[] args) {
        Quest quest = args.length > 1 ? plugin.quests().get(args[1]) : null;
        if (quest == null) {
            sender.sendMessage(Text.mm("<red>Usage: /cq quest <id>. Example ids: welcome, side_jerry_1, daily_1"));
            return;
        }
        StringBuilder out = new StringBuilder("<gold><bold>" + Text.escape(quest.name()) + "</bold></gold> <gray>" + quest.id()
                + " · " + quest.category() + " · Lv " + quest.level() + "\n<gray>Giver: <white>" + plugin.npcs().name(quest.giver())
                + "</white> Turn in: <white>" + plugin.npcs().name(quest.turnIn()) + "</white>");
        quest.objectives().forEach(o -> out.append("\n<gray>• <white>").append(plugin.questManager().objectiveSentence(o)));
        out.append("\n<gray>Reward: ").append(String.join("<gray>, ", plugin.questManager().rewardLines(quest.reward())));
        sender.sendMessage(Text.mm(out.toString()));
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 1) {
            return QuestsCommand.filter(List.of("reload", "npc", "pos1", "pos2", "scatter", "player", "quest", "finale"), args[0]);
        }
        String first = args[0].toLowerCase(Locale.ROOT);
        List<String> npcIds = plugin.npcs().all().stream().map(NpcDef::id).toList();
        if (first.equals("npc")) {
            if (args.length == 2) {
                return QuestsCommand.filter(List.of("list", "place", "remove", "tp"), args[1]);
            }
            if (args.length == 3) {
                return QuestsCommand.filter(npcIds, args[2]);
            }
        }
        if (first.equals("scatter") && args.length == 2) {
            List<String> options = new ArrayList<>(List.of("act1", "act2", "all"));
            options.addAll(npcIds);
            return QuestsCommand.filter(options, args[1]);
        }
        if (first.equals("player")) {
            if (args.length == 2) {
                return QuestsCommand.filter(Bukkit.getOnlinePlayers().stream().map(Player::getName).toList(), args[1]);
            }
            if (args.length == 3) {
                return QuestsCommand.filter(List.of("reset", "complete", "give", "resetdaily"), args[2]);
            }
        }
        if (first.equals("quest") && args.length == 2) {
            return QuestsCommand.filter(plugin.quests().story().stream().map(Quest::id).toList(), args[1]);
        }
        return List.of();
    }
}
