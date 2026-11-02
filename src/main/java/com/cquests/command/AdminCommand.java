package com.cquests.command;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.npc.SpawnManager;
import com.cquests.npc.WorldGuardHook;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.OfflinePlayer;
import org.bukkit.World;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabExecutor;
import org.bukkit.entity.Player;

import java.io.File;
import java.io.IOException;
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
    private final TestCommand test;

    public AdminCommand(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.test = new TestCommand(plugin);
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
                plugin.send(sender, "<green>CQuests reloaded: " + plugin.npcs().all().size() + " NPCs, "
                        + plugin.quests().story().size() + " story quests, "
                        + String.format(Locale.ROOT, "%,d", plugin.quests().totalSide()) + " side quests.");
            }
            case "npc" -> npc(sender, args);
            case "pos1", "pos2" -> pos(sender, args[0].equalsIgnoreCase("pos1") ? 0 : 1);
            case "scatter" -> scatter(sender, args);
            case "scatterworld" -> scatterWorld(sender, args);
            case "farm" -> plugin.farmCommand().run(sender,args);
            case "merchant" -> new com.cquests.merchant.MerchantCommand(plugin).run(sender,args);
            case "camp" -> plugin.spawns().arrangeCamp(sender);
            case "player" -> player(sender, args);
            case "quest" -> quest(sender, args);
            case "finale" -> finale(sender, args);
            case "test" -> test.run(sender, args);
            case "backup" -> backup(sender);
            case "backups" -> backups(sender);
            case "restore" -> restore(sender, args);
            default -> help(sender);
        }
        return true;
    }

    private void help(CommandSender s) {
        plugin.send(s, """
                <gold><bold>CQuests admin</bold></gold>
                <yellow>/cq reload</yellow> <gray>reload configs, NPCs and quests
                <yellow>/cq npc list</yellow> <gray>NPCs and where they stand
                <yellow>/cq npc place <id></yellow> <gray>put an NPC where you stand
                <yellow>/cq npc remove <id></yellow> <gray>take an NPC off the map
                <yellow>/cq npc tp <id></yellow> <gray>teleport to an NPC
                <yellow>/cq pos1</yellow>, <yellow>/cq pos2</yellow> <gray>select a box for scattering
                <yellow>/cq scatter <ids|act1|act2|all> [wg-region]</yellow> <gray>spread NPCs in a region or your box
                <yellow>/cq scatterworld chapter1 10000 10000 [world] [centerX centerZ]</yellow> <gray>safe world scatter; keeps progress
                <yellow>/cq camp</yellow> <gray>arrange five residents plus the daily NPC
                <yellow>/cq farm wand|outside <id></yellow> <gray>select a farm outline
                <yellow>/cq farm save <id> <wg-region></yellow> <gray>bind the outline to WorldGuard
                <yellow>/cq farm anvil</yellow> <gray>bind the anvil you look at
                <yellow>/cq merchant list</yellow> <gray>five travelling merchants; OP-only route/trade editor
                <yellow>/cq player <name> reset|complete <quest>|give <quest>|resetdaily</yellow>
                <yellow>/cq quest <id></yellow> <gray>show a quest's details
                <yellow>/cq finale [player]</yellow> <gray>preview the ending cinematic
                <yellow>/cq test</yellow> <gray>try messages, animations, achievements and disappearing villagers
                <yellow>/cq backup</yellow> <gray>back up all quest data now
                <yellow>/cq backups</yellow> <gray>list backups
                <yellow>/cq restore <backup|latest> <player|all></yellow> <gray>put quest data back from a backup""");
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
            out.append(placed).append('/').append(rows.size()).append(" placed; ").append(plugin.spawns().live().size())
                    .append(" currently spawned near players)</gray>\n").append(String.join("<gray>, ", rows));
            plugin.send(sender, out.toString());
            return;
        }
        if (args.length < 3) {
            plugin.send(sender, "<red>Usage: /cq npc " + action + " <id>");
            return;
        }
        NpcDef npc = plugin.npcs().get(args[2]);
        if (npc == null) {
            plugin.send(sender, "<red>No NPC with id '" + Text.escape(args[2]) + "'. See /cq npc list.");
            return;
        }
        switch (action) {
            case "place" -> {
                if (!(sender instanceof Player player)) {
                    sender.sendMessage("Run this in game.");
                    return;
                }
                plugin.spawns().placeChecked(npc, player.getLocation(), sender);
            }
            case "repair" -> plugin.spawns().repair(npc, sender);
            case "rename" -> {
                if (args.length < 4) { plugin.send(sender, "<red>/cq npc rename <id> <Display Name>"); return; }
                String name = String.join(" ", java.util.Arrays.copyOfRange(args, 3, args.length));
                if (name.length() > 48) { plugin.send(sender, "<red>Use a name of 48 characters or fewer."); return; }
                var file = new File(plugin.getDataFolder(), "npcs.yml");
                var yaml = org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(file);
                yaml.set("npcs." + npc.id() + ".name", name);
                try {
                    yaml.save(file); plugin.reload();
                    plugin.send(sender, "<green>Display name changed to " + Text.escape(name) + ". Quest IDs and progress preserved.");
                } catch (IOException e) { plugin.send(sender, "<red>Could not save name: " + Text.escape(e.getMessage())); }
            }
            case "remove" -> plugin.send(sender, plugin.spawns().remove(npc.id())
                    ? "<green>Removed " + Text.escape(npc.name()) + " from the map."
                    : "<gray>" + Text.escape(npc.name()) + " had no spawn point.");
            case "tp" -> {
                SpawnManager.Point point = plugin.spawns().points().get(npc.id());
                Location loc = point == null ? null : point.location();
                if (!(sender instanceof Player player) || loc == null) {
                    plugin.send(sender, "<red>That NPC has no spawn point (or run this in game).");
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
        plugin.send(sender, "<green>pos" + (index + 1) + " set to " + l.getBlockX() + ", " + l.getBlockY() + ", " + l.getBlockZ());
    }

    private void scatter(CommandSender sender, String[] args) {
        if (args.length < 2) {
            plugin.send(sender, "<red>Usage: /cq scatter <id,id,...|act1|act2|all> [worldguard-region]");
            return;
        }
        List<NpcDef> npcs = selectNpcs(args[1]);
        if (npcs.isEmpty()) {
            plugin.send(sender, "<red>No NPCs matched '" + Text.escape(args[1]) + "'.");
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
                plugin.send(sender, "<red>Unknown world.");
                return;
            }
            if (!WorldGuardHook.available()) {
                plugin.send(sender, "<red>WorldGuard is not installed; use /cq pos1 and /cq pos2 instead.");
                return;
            }
            box = WorldGuardHook.bounds(world, args[2]);
            if (box == null) {
                plugin.send(sender, "<red>No WorldGuard region '" + Text.escape(args[2]) + "' in " + world.getName() + ".");
                return;
            }
        } else {
            Location[] sel = sender instanceof Player p ? selections.get(p.getUniqueId()) : null;
            if (sel == null || sel[0] == null || sel[1] == null || !sel[0].getWorld().equals(sel[1].getWorld())) {
                plugin.send(sender, "<red>Set /cq pos1 and /cq pos2 first, or name a WorldGuard region.");
                return;
            }
            world = sel[0].getWorld();
            box = new int[]{sel[0].getBlockX(), sel[0].getBlockY(), sel[0].getBlockZ(), sel[1].getBlockX(), sel[1].getBlockY(), sel[1].getBlockZ()};
        }
        plugin.send(sender, "<gray>Scattering " + npcs.size() + " NPCs...");
        plugin.spawns().scatter(npcs, world, box, sender);
    }

    private List<NpcDef> selectNpcs(String spec) {
        List<NpcDef> out = new ArrayList<>();
        String lower = spec.toLowerCase(Locale.ROOT);
        if (lower.matches("chapter[1-9][0-9]*")) {
            try {
                int chapter = Integer.parseInt(lower.substring(7));
                return plugin.npcs().all().stream().filter(n -> plugin.quests().firstChapter(n.id()) == chapter).toList();
            } catch (NumberFormatException e) { return List.of(); }
        }
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

    private void scatterWorld(CommandSender sender, String[] args) {
        if (args.length < 4 || args.length == 6 || args.length > 7) {
            plugin.send(sender, "<red>/cq scatterworld <chapter1|chapter2|all|id,id> <width> <depth> [world] [centerX centerZ]"); return;
        }
        try {
            int width = Integer.parseInt(args[2]), depth = Integer.parseInt(args[3]);
            if (width < 16 || depth < 16 || width > 100000 || depth > 100000) throw new IllegalArgumentException();
            World world = args.length >= 5 ? Bukkit.getWorld(args[4]) : sender instanceof Player p ? p.getWorld() : Bukkit.getWorlds().get(0);
            if (world == null) { plugin.send(sender, "<red>Unknown world."); return; }
            int centerX = args.length == 7 ? Integer.parseInt(args[5]) : world.getSpawnLocation().getBlockX();
            int centerZ = args.length == 7 ? Integer.parseInt(args[6]) : world.getSpawnLocation().getBlockZ();
            if (Math.abs((long) centerX) + width / 2L > 29_999_000 || Math.abs((long) centerZ) + depth / 2L > 29_999_000) throw new IllegalArgumentException();
            List<NpcDef> npcs = selectNpcs(args[1]);
            if (npcs.isEmpty()) { plugin.send(sender, "<red>No NPCs matched that selector."); return; }
            int minX = centerX - width / 2, minZ = centerZ - depth / 2;
            int[] box = {minX, world.getMinHeight() + 1, minZ, minX + width - 1, world.getMaxHeight() - 2, minZ + depth - 1};
            plugin.send(sender, "<white>Searching safe terrain for " + npcs.size() + " villagers in " + width + " × " + depth + ". This may generate chunks; progress is preserved.");
            plugin.spawns().scatter(npcs, world, box, sender);
        } catch (IllegalArgumentException e) {
            plugin.send(sender, "<red>Width/depth must be whole numbers from 16 to 100000; centers must be valid world coordinates.");
        }
    }

    private void backup(CommandSender sender) {
        plugin.send(sender, "<gray>Backing up quest data...");
        Sched.async(() -> {
            String name = plugin.backups().backup("manual");
            plugin.send(sender, name == null ? "<red>Backup failed, see the console." : "<green>Saved backups/" + name);
        });
    }

    private void backups(CommandSender sender) {
        List<File> files = plugin.backups().files();
        if (files.isEmpty()) {
            plugin.send(sender, "<gray>No backups yet. Make one with <yellow>/cq backup</yellow>.");
            return;
        }
        StringBuilder out = new StringBuilder("<gold>Backups</gold> <gray>(newest first)");
        for (int i = 0; i < files.size() && i < 10; i++) {
            File file = files.get(i);
            out.append("\n<yellow>").append(file.getName()).append(" <dark_gray>").append(file.length() / 1024).append(" KB");
        }
        plugin.send(sender, out.toString());
    }

    private void restore(CommandSender sender, String[] args) {
        if (args.length < 3) {
            plugin.send(sender, "<red>Usage: /cq restore <backup|latest> <player|all>");
            return;
        }
        File backup = plugin.backups().find(args[1]);
        if (backup == null) {
            plugin.send(sender, "<red>No backup called '" + Text.escape(args[1]) + "'. See /cq backups.");
            return;
        }
        UUID target = null;
        if (!args[2].equalsIgnoreCase("all")) {
            target = resolve(args[2]);
            if (target == null) {
                plugin.send(sender, "<red>Unknown player '" + Text.escape(args[2]) + "'. Use their exact name or UUID.");
                return;
            }
        }
        UUID only = target;
        Sched.async(() -> {
            try {
                List<UUID> restored = plugin.backups().restore(backup, only);
                for (UUID id : restored) {
                    Player online = Bukkit.getPlayer(id);
                    if (online != null) {
                        plugin.visibility().refresh(online);
                        Sched.entity(online, () -> {
                            plugin.tracker().update(online);
                            plugin.finale().achievements().sync(online);
                        });
                    }
                }
                plugin.send(sender, restored.isEmpty()
                        ? "<red>That backup has no data for that player."
                        : "<green>Restored " + restored.size() + (restored.size() == 1 ? " player" : " players") + " from " + backup.getName()
                        + ". <gray>The replaced files were kept as .yml.before-restore.");
            } catch (IOException e) {
                plugin.send(sender, "<red>Restore failed: " + Text.escape(String.valueOf(e.getMessage())));
            }
        });
    }

    private static UUID resolve(String nameOrUuid) {
        Player online = Bukkit.getPlayerExact(nameOrUuid);
        if (online != null) {
            return online.getUniqueId();
        }
        try {
            return UUID.fromString(nameOrUuid);
        } catch (IllegalArgumentException ignored) {
            OfflinePlayer cached = Bukkit.getOfflinePlayerIfCached(nameOrUuid);
            return cached == null ? null : cached.getUniqueId();
        }
    }

    private void player(CommandSender sender, String[] args) {
        if (args.length < 3) {
            plugin.send(sender, "<red>Usage: /cq player <name> reset|complete <quest>|give <quest>|resetdaily");
            return;
        }
        Player target = Bukkit.getPlayerExact(args[1]);
        if (target == null) {
            plugin.send(sender, "<red>That player is not online.");
            return;
        }
        PlayerData data = plugin.questManager().data(target);
        String action = args[2].toLowerCase(Locale.ROOT);
        Quest quest = args.length > 3 ? plugin.quests().get(args[3]) : null;
        switch (action) {
            case "reset" -> {
                data.reset();
                plugin.send(sender, "<green>Reset all quest progress for " + target.getName() + ".");
            }
            case "resetdaily" -> {
                data.setLastDailyAt(0);
                plugin.send(sender, "<green>" + target.getName() + " can take a new daily quest now.");
            }
            case "complete" -> {
                if (quest == null) {
                    plugin.send(sender, "<red>Unknown quest.");
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
                Sched.entity(target, () -> plugin.finale().achievements().sync(target));
                plugin.send(sender, "<green>Done. If the quest was active it now waits for turn-in.");
            }
            case "give" -> {
                if (quest == null) {
                    plugin.send(sender, "<red>Unknown quest.");
                    return;
                }
                data.uncomplete(quest.id());
                if (quest.category() == QuestCategory.SIDE) {
                    data.setSideDone(quest.giver(), Math.min(data.sideDone(quest.giver()), quest.order() - 1));
                }
                plugin.questManager().forceAccept(target, quest);
                plugin.send(sender, "<green>Gave " + Text.escape(quest.name()) + " to " + target.getName() + ".");
            }
            default -> plugin.send(sender, "<red>Unknown action.");
        }
        plugin.visibility().refresh(target);
    }

    private void finale(CommandSender sender, String[] args) {
        Player target = args.length > 1 ? Bukkit.getPlayerExact(args[1]) : sender instanceof Player p ? p : null;
        if (target == null) {
            plugin.send(sender, "<red>Usage: /cq finale [player]");
            return;
        }
        plugin.finale().play(target, true);
        plugin.send(sender, "<green>Playing the ending for " + target.getName() + " (preview, no advancement).");
    }

    private void quest(CommandSender sender, String[] args) {
        Quest quest = args.length > 1 ? plugin.quests().get(args[1]) : null;
        if (quest == null) {
            plugin.send(sender, "<red>Usage: /cq quest <id>. Example ids: welcome, side_jerry_1, daily_1");
            return;
        }
        StringBuilder out = new StringBuilder("<gold><bold>" + Text.escape(quest.name()) + "</bold></gold> <gray>" + quest.id()
                + " · " + quest.category() + " · Lv " + quest.level() + "\n<gray>Giver: <white>" + plugin.npcs().name(quest.giver())
                + "</white> Turn in: <white>" + plugin.npcs().name(quest.turnIn()) + "</white>");
        quest.objectives().forEach(o -> out.append("\n<gray>• <white>").append(plugin.questManager().objectiveSentence(o)));
        out.append("\n<gray>Reward: ").append(String.join("<gray>, ", plugin.questManager().rewardLines(quest.reward())));
        plugin.send(sender, out.toString());
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 1) {
            return QuestsCommand.filter(List.of("reload", "npc", "pos1", "pos2", "scatter", "scatterworld", "camp", "farm", "merchant", "player", "quest", "finale", "test", "backup", "backups", "restore"), args[0]);
        }
        String first = args[0].toLowerCase(Locale.ROOT);
        if(first.equals("merchant")){
            if(!(sender instanceof Player p)||!p.isOp())return List.of();
            if(args.length==2)return QuestsCommand.filter(List.of("list","spawn","point","shop","wand","undo","routeclear","walk","despawn","edit"),args[1]);
            if(args.length==3)return QuestsCommand.filter(plugin.merchants().all().stream().map(com.cquests.merchant.MerchantDefinition::id).toList(),args[2]);
        }
        if(first.equals("farm")&&args.length==2)return QuestsCommand.filter(List.of("wand","outside","save","anvil","menu"),args[1]);
        List<String> npcIds = plugin.npcs().all().stream().map(NpcDef::id).toList();
        if (first.equals("npc")) {
            if (args.length == 2) {
                return QuestsCommand.filter(List.of("list", "place", "remove", "tp", "repair", "rename"), args[1]);
            }
            if (args.length == 3) {
                return QuestsCommand.filter(npcIds, args[2]);
            }
        }
        if (first.equals("test")) {
            if (args.length == 2) {
                return QuestsCommand.filter(TestCommand.ACTIONS, args[1]);
            }
            if (args.length == 3) {
                String action = args[1].toLowerCase(Locale.ROOT);
                if (List.of("finish", "unfinish", "roam").contains(action)) {
                    return QuestsCommand.filter(npcIds, args[2]);
                }
                if (action.equals("achievement")) {
                    List<String> options = new ArrayList<>(List.of("end", "reset"));
                    plugin.quests().story().stream().map(q -> Integer.toString(q.chapter())).distinct().forEach(options::add);
                    return QuestsCommand.filter(options, args[2]);
                }
                if (action.equals("chapter")) {
                    return QuestsCommand.filter(plugin.quests().story().stream().map(q -> Integer.toString(q.chapter())).distinct().toList(), args[2]);
                }
            }
        }
        if (first.equals("restore")) {
            if (args.length == 2) {
                List<String> names = new ArrayList<>(List.of("latest"));
                plugin.backups().files().stream().limit(20).forEach(f -> names.add(f.getName()));
                return QuestsCommand.filter(names, args[1]);
            }
            if (args.length == 3) {
                List<String> names = new ArrayList<>(List.of("all"));
                Bukkit.getOnlinePlayers().forEach(p -> names.add(p.getName()));
                return QuestsCommand.filter(names, args[2]);
            }
        }
        if ((first.equals("scatter") || first.equals("scatterworld")) && args.length == 2) {
            List<String> options = new ArrayList<>(List.of("act1", "act2", "all", "chapter1", "chapter2", "chapter3", "chapter4", "chapter5"));
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
