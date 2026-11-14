package com.cquests.command;

import com.cquests.T;

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

    /** Controlling bosses is for operators, and for anyone given bosses.use (the same rule as CBosses). */
    public static boolean canControlBosses(CommandSender sender) {
        return sender.isOp() || sender.hasPermission("bosses.use") || sender.hasPermission("cquests.admin");
    }

    private static boolean bossCommand(String[] args) {
        if (args.length == 0) return false;
        String a = args[0].toLowerCase(Locale.ROOT);
        return a.equals("worldboss") || a.equals("wb") || a.equals("boss") || (a.equals("test") && args.length > 1 && args[1].toLowerCase(Locale.ROOT).startsWith("worldboss"));
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (bossCommand(args) ? !canControlBosses(sender) : !sender.hasPermission("cquests.admin")) {
            plugin.send(sender, T.t("admin-command.no-permission", "<red>You can't use that."));
            return true;
        }
        if (args.length == 0) {
            help(sender);
            return true;
        }
        switch (args[0].toLowerCase(Locale.ROOT)) {
            case "reload" -> {
                plugin.reload();
                plugin.send(sender, T.t("admin-command.cquests-reloaded-npcs-story-quests", "<green>CQuests reloaded: <size> NPCs, <size2> story quests, <amount> side quests.", "size", plugin.npcs().all().size(), "size2", plugin.quests().story().size(), "amount", String.format(Locale.ROOT, "%,d", plugin.quests().totalSide())));
            }
            case "character" -> plugin.characters().command(sender,args);
            case "npc" -> npc(sender, args);
            case "pos1", "pos2" -> pos(sender, args[0].equalsIgnoreCase("pos1") ? 0 : 1);
            case "scatter" -> scatter(sender, args);
            case "scatterworld", "worldscatter" -> scatterWorld(sender, args);
            case "chapter", "chapters" -> chapter(sender, args);
            case "farm" -> plugin.farmCommand().run(sender,args);
            case "merchant" -> new com.cquests.merchant.MerchantCommand(plugin).run(sender,args);
            case "crate", "crates" -> plugin.crates().command(sender, args);
            case "camp", "spawnvillagers" -> plugin.spawns().arrangeCamp(sender);
            case "player" -> player(sender, args);
            case "quest" -> quest(sender, args);
            case "finale" -> finale(sender, args);
            case "test" -> test.run(sender, args);
            case "backup" -> backup(sender);
            case "backups" -> backups(sender);
            case "restore" -> restore(sender, args);
            case "worldboss", "wb", "boss" -> worldBoss(sender, args);
            case "season", "seasons" -> plugin.seasons().command(sender, args);
            default -> help(sender);
        }
        return true;
    }

    private void worldBoss(CommandSender sender, String[] args) {
        var wb = plugin.worldBosses();
        String action = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "help";
        String arena = args.length > 2 ? args[2] : "main";
        Player player = sender instanceof Player p ? p : null;
        switch (action) {
            case "list" -> wb.listBosses(sender);
            case "menu", "panel", "gui" -> {
                if (player == null) plugin.send(sender, T.t("admin-command.run-this-in-game", "<red>Run this in game.")); else com.cquests.worldboss.BossPanel.open(plugin, player);
            }
            case "arenas" -> wb.listArenas(sender);
            case "spots" -> wb.spots(sender);
            case "interval", "every" -> {
                if (args.length < 4) { plugin.send(sender, T.t("admin-command.cq-worldboss-interval", "<yellow>/cq worldboss interval <arena> <2h|400h|90m|off>")); return; }
                wb.setInterval(sender, arena, args[3]);
            }
            case "nopass", "block" -> wb.nopass(sender, player, arena, java.util.Arrays.copyOfRange(args, Math.min(args.length, 3), args.length));
            case "next", "info" -> wb.info(sender);
            case "selftest" -> { plugin.send(sender, T.t("admin-command.spawning-every-world-boss-near", "<gray>Spawning every world boss near the world spawn to check it works...")); wb.selfTest(sender); }
            case "stop" -> plugin.send(sender, (args.length > 2 ? wb.stop(arena) : stopAll(wb)) ? "<gray>World boss sent away." : "<gray>No world boss is alive there.");
            case "schedule" -> {
                if (args.length > 2 && List.of("on", "off").contains(args[2].toLowerCase(Locale.ROOT))) wb.scheduleToggle(sender, args[2].equalsIgnoreCase("on"));
                else wb.info(sender);
            }
            case "setspawn", "wand", "border", "radius", "spawn" -> {
                if (player == null) { plugin.send(sender, T.t("admin-command.run-this-in-game", "<red>Run this in game.")); return; }
                switch (action) {
                    case "setspawn" -> wb.setSpawn(player, arena);
                    case "wand" -> wb.giveWand(player, arena);
                    case "border" -> {
                        String what = args.length > 3 ? args[3].toLowerCase(Locale.ROOT) : "show";
                        if (what.equals("clear")) wb.clearBorder(player, arena);
                        else {
                            var a = wb.arenaFor(arena);
                            if (a == null) plugin.send(player, T.t("admin-command.no-arena", "<red>No arena <arena>", "arena", Text.escape(arena))); else wb.show(player, a);
                        }
                    }
                    case "radius" -> {
                        int r;
                        try { r = Integer.parseInt(args.length > 3 ? args[3] : ""); } catch (NumberFormatException e) { plugin.send(player, T.t("admin-command.cq-worldboss-radius", "<yellow>/cq worldboss radius <arena> <blocks>")); return; }
                        wb.setRadius(player, arena, r);
                    }
                    default -> { // spawn <boss> [arena]: no arena means right where you stand
                        if (args.length < 3) { plugin.send(player, T.t("admin-command.cq-worldboss-spawn-arena", "<yellow>/cq boss spawn <boss> [arena]")); return; }
                        if (args.length > 3 && !args[3].equalsIgnoreCase("here")) wb.spawnAt(player, args[2], args[3]);
                        else if (wb.spawnHere(player, args[2])) plugin.send(player, T.t("boss-panel.summoning-it-here", "<green>Summoning it where you stand..."));
                    }
                }
            }
            default -> plugin.send(sender, """
                    <gold><bold>World bosses</bold></gold> <gray>(one wakes every week, see config.yml world-bosses)
                    <yellow>/cq worldboss setspawn <arena></yellow> <gray>the boss appears where you stand (arena "main" is used by the weekly schedule)
                    <yellow>/cq worldboss wand <arena></yellow> <gray>border stick: left-click blocks for corners, right-click undo, sneak+right-click show
                    <yellow>/cq worldboss border <arena> [show|clear]</yellow> <gray>see or remove the outline
                    <yellow>/cq worldboss radius <arena> <blocks></yellow> <gray>circle border when there is no outline
                    <yellow>/cq worldboss interval <arena> <2h|400h|off></yellow> <gray>make it a spot: a boss wakes there that often, a different one each time
                    <yellow>/cq worldboss spots</yellow> <gray>every timed spot and when its next boss wakes
                    <yellow>/cq worldboss nopass <arena> here [radius]|corner|list|remove <n>|clear</yellow> <gray>areas the boss can never enter
                    <yellow>/cq worldboss menu</yellow> <gray>the operators' panel: spawn, try or send away any boss
                    <yellow>/cq worldboss list</yellow> <gray>every boss; <yellow>arenas</yellow> <gray>every arena; <yellow>next</yellow> <gray>next weekly boss
                    <yellow>/cq worldboss spawn <boss> [arena]</yellow> <gray>start one now (real fight, real rewards)
                    <yellow>/cq worldboss stop [arena]</yellow> <gray>send it away
                    <yellow>/cq worldboss schedule on|off</yellow> <gray>turn the weekly boss on or off
                    <yellow>/cq worldboss selftest</yellow> <gray>spawn every boss near the world spawn, run every attack, report problems
                    <yellow>/cq test worldboss <boss></yellow> <gray>try one in front of you, nothing is paid""");
        }
    }

    private static boolean stopAll(com.cquests.worldboss.WorldBossService wb) {
        boolean any = wb.alive(); wb.stopAll(); return any;
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
                <yellow>/cq scatterworld chapter6 10000 [depth] [world] [centerX centerZ]</yellow> <gray>spread over the world (or <yellow>border</yellow>); keeps progress
                <yellow>/cq chapter [number] [on|off]</yellow> <gray>list chapters or switch one on or off
                <yellow>/cq camp</yellow> <gray>place only the spawn villagers around you (wild ones stay)
                <yellow>/cq farm wand|outside <id></yellow> <gray>select a farm outline
                <yellow>/cq farm save <id> <wg-region></yellow> <gray>bind the outline to WorldGuard
                <yellow>/cq farm anvil</yellow> <gray>OP: get the special hoe-upgrade anvil
                <yellow>/cq farm bind</yellow> <gray>OP: bind an existing anvil
                <yellow>/cq merchant list</yellow> <gray>five travelling merchants; OP-only route/trade editor
                <yellow>/cq player <name> reset|complete <quest>|give <quest>|resetdaily</yellow>
                <yellow>/cq quest <id></yellow> <gray>show a quest's details
                <yellow>/cq finale [player]</yellow> <gray>preview the ending cinematic
                <yellow>/cq worldboss</yellow> <gray>weekly world bosses: spawn point, border stick, list, spawn, stop
                <yellow>/cq season [id] [on|off|auto]</yellow> <gray>seasonal events (Halloween, Winter, Spring, Summer)
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
                String shown = plugin.npcs().name(npc.id());
                boolean differs = !shown.replaceAll("[^A-Za-z0-9]", "").equalsIgnoreCase(npc.id().replaceAll("[^A-Za-z0-9]", ""));
                rows.add((has ? "<green>" : "<red>") + npc.id() + "</" + (has ? "green" : "red") + ">"
                        + (differs ? " <white>(" + Text.escape(shown) + ")</white>" : ""));
            }
            out.append(placed).append('/').append(rows.size()).append(" placed; ").append(plugin.spawns().live().size())
                    .append(" currently spawned near players)</gray>\n").append(String.join("<gray>, ", rows));
            plugin.send(sender, out.toString());
            return;
        }
        if (args.length < 3) {
            plugin.send(sender, T.t("admin-command.usage-cq-npc", "<red>Usage: /cq npc <action> <id>", "action", action));
            return;
        }
        NpcDef npc = plugin.npcs().get(args[2]);
        if (npc == null) {
            plugin.send(sender, T.t("admin-command.no-npc-with-id-see", "<red>No NPC with id '<input2>'. See /cq npc list.", "input2", Text.escape(args[2])));
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
            case "skin" -> {
                if (!sender.isOp()) { plugin.send(sender,T.t("admin-command.only-operators-can-change-npc", "<red>Only operators can change NPC skins.")); return; }
                if(args.length!=4||!args[3].matches("[A-Za-z0-9_]{1,16}")){plugin.send(sender,T.t("admin-command.cq-npc-skin", "<red>/cq npc skin <id> <username|default|villager>"));return;}
                String skin=args[3].equalsIgnoreCase("villager")?"":args[3];
                var file=new File(plugin.getDataFolder(),"npcs.yml");
                var yaml=org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(file);
                yaml.set("npcs."+npc.id()+".player-skin",skin);
                try{yaml.save(file);plugin.reload();plugin.send(sender,T.t("admin-command.npc-appearance-saved-quests-and", "<green>NPC appearance saved; quests and progress preserved. Player skins require Minecraft 1.21.9+."));}
                catch(IOException e){plugin.send(sender,T.t("admin-command.could-not-save-skin", "<red>Could not save skin: <getmessage>", "getmessage", Text.escape(e.getMessage())));}
            }
            case "rename" -> {
                var forwarded=new ArrayList<String>(List.of("character",npc.id(),"name"));
                forwarded.addAll(java.util.Arrays.asList(args).subList(3,args.length));
                plugin.characters().command(sender,forwarded.toArray(String[]::new));
            }
            case "remove" -> plugin.send(sender, plugin.spawns().remove(npc.id())
                    ? "<green>Removed " + Text.escape(npc.name()) + " from the map."
                    : "<gray>" + Text.escape(npc.name()) + " had no spawn point.");
            case "tp" -> {
                SpawnManager.Point point = plugin.spawns().points().get(npc.id());
                Location loc = point == null ? null : point.location();
                if (!(sender instanceof Player player) || loc == null) {
                    plugin.send(sender, T.t("admin-command.that-npc-has-no-spawn", "<red>That NPC has no spawn point (or run this in game)."));
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
        plugin.send(sender, T.t("admin-command.pos-set-to", "<green>pos<index> set to <getblockx>, <getblocky>, <getblockz>", "index", (index + 1), "getblockx", l.getBlockX(), "getblocky", l.getBlockY(), "getblockz", l.getBlockZ()));
    }

    private void scatter(CommandSender sender, String[] args) {
        if (args.length < 2) {
            plugin.send(sender, T.t("admin-command.usage-cq-scatter-worldguard-region", "<red>Usage: /cq scatter <id,id,...|act1|act2|all> [worldguard-region]"));
            return;
        }
        List<NpcDef> npcs = selectNpcs(args[1]);
        if (npcs.isEmpty()) {
            plugin.send(sender, T.t("admin-command.no-npcs-matched", "<red>No NPCs matched '<input>'.", "input", Text.escape(args[1])));
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
                plugin.send(sender, T.t("admin-command.unknown-world", "<red>Unknown world."));
                return;
            }
            if (!WorldGuardHook.available()) {
                plugin.send(sender, T.t("admin-command.worldguard-is-not-installed-use", "<red>WorldGuard is not installed; use /cq pos1 and /cq pos2 instead."));
                return;
            }
            box = WorldGuardHook.bounds(world, args[2]);
            if (box == null) {
                plugin.send(sender, T.t("admin-command.no-worldguard-region-in", "<red>No WorldGuard region '<input2>' in <world>.", "input2", Text.escape(args[2]), "world", world.getName()));
                return;
            }
        } else {
            Location[] sel = sender instanceof Player p ? selections.get(p.getUniqueId()) : null;
            if (sel == null || sel[0] == null || sel[1] == null || !sel[0].getWorld().equals(sel[1].getWorld())) {
                plugin.send(sender, T.t("admin-command.set-cq-pos1-and-cq", "<red>Set /cq pos1 and /cq pos2 first, or name a WorldGuard region."));
                return;
            }
            world = sel[0].getWorld();
            if(sender instanceof Player player&&!player.getWorld().equals(world)){
                plugin.send(sender,T.t("admin-command.your-selection-belongs-to-another", "<yellow>Your selection belongs to another world. Set both corners here, or use /cq scatterworld in your current world."));return;
            }
            box = new int[]{sel[0].getBlockX(), sel[0].getBlockY(), sel[0].getBlockZ(), sel[1].getBlockX(), sel[1].getBlockY(), sel[1].getBlockZ()};
        }
        plugin.send(sender, T.t("admin-command.scattering-npcs", "<gray>Scattering <size> NPCs...", "size", npcs.size()));
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

    /**
     * /cq scatterworld <selector> <size|border> [depth] [world] [centerX centerZ]
     * Spreads villagers over the world itself: a square centred on the world's centre (the world
     * border's centre, normally 0 0), not around the admin or spawn. "border" uses the whole world
     * border, capped at 100,000. Positions change; quest progress never does.
     */
    private void scatterWorld(CommandSender sender, String[] args) {
        if (args.length < 3) {
            plugin.send(sender, T.t("admin-command.cq-scatterworld-depth-world-centerx", "<red>/cq scatterworld <chapter6|all|id,id> <size|border> [depth] [world] [centerX centerZ]"));
            plugin.send(sender, T.t("admin-command.example-cq-scatterworld-chapter6-10000", "<gray>Example: <yellow>/cq scatterworld chapter6 10000</yellow> spreads chapter 6 over 10,000 × 10,000 blocks of the world."));
            return;
        }
        try {
            List<String> rest = new ArrayList<>(java.util.Arrays.asList(args).subList(2, args.length));
            String first = rest.remove(0);
            Integer depthArg = null;
            if (!rest.isEmpty() && rest.get(0).replace(",", "").matches("\\d+")) depthArg = Integer.parseInt(rest.remove(0).replace(",", ""));
            World world = sender instanceof Player p ? p.getWorld() : Bukkit.getWorlds().get(0);
            if (!rest.isEmpty() && !rest.get(0).matches("-?\\d+")) {
                world = Bukkit.getWorld(rest.remove(0));
                if (world == null) { plugin.send(sender, T.t("admin-command.unknown-world", "<red>Unknown world.")); return; }
            }
            var border = world.getWorldBorder();
            int centerX = border.getCenter().getBlockX(), centerZ = border.getCenter().getBlockZ();
            if (rest.size() == 2) { centerX = Integer.parseInt(rest.get(0)); centerZ = Integer.parseInt(rest.get(1)); }
            else if (!rest.isEmpty()) throw new IllegalArgumentException();
            int width = first.equalsIgnoreCase("border") ? (int) Math.min(100_000, Math.max(16, border.getSize() - 32))
                    : Integer.parseInt(first.replace(",", ""));
            int depth = depthArg != null ? depthArg : width;
            if (width < 16 || depth < 16 || width > 100000 || depth > 100000) throw new IllegalArgumentException();
            if (Math.abs((long) centerX) + width / 2L > 29_999_000 || Math.abs((long) centerZ) + depth / 2L > 29_999_000) throw new IllegalArgumentException();
            List<NpcDef> npcs = selectNpcs(args[1]);
            if (npcs.isEmpty()) { plugin.send(sender, T.t("admin-command.no-npcs-matched-that-selector", "<red>No NPCs matched that selector.")); return; }
            int minX = centerX - width / 2, minZ = centerZ - depth / 2;
            int[] box = {minX, world.getMinHeight() + 1, minZ, minX + width - 1, world.getMaxHeight() - 2, minZ + depth - 1};
            plugin.send(sender, T.t("admin-command.spreading-villagers-over-blocks-of", "<white>Spreading <size> villagers over <amount> blocks of <world> (centre <centerx>, <centerz>). Only safe ground is used; progress is preserved.", "size", npcs.size(), "amount", String.format(Locale.ROOT, "%,d × %,d", width, depth), "world", Text.escape(world.getName()), "centerx", centerX, "centerz", centerZ));
            plugin.spawns().scatter(npcs, world, box, sender);
        } catch (IllegalArgumentException e) {
            plugin.send(sender, T.t("admin-command.size-must-be-a-whole", "<red>Size must be a whole number from 16 to 100000 (or border); centers must be valid world coordinates."));
        }
    }

    /** /cq chapter [number] [on|off]: lists chapters, or switches one on or off for everyone. */
    private void chapter(CommandSender sender, String[] args) {
        var names = plugin.quests().chapterNames();
        var locked = plugin.settings().lockedChapters;
        if (args.length < 3) {
            StringBuilder out = new StringBuilder("<gold>Chapters</gold> <gray>(switch with /cq chapter <number> on|off)");
            names.forEach((number, name) -> {
                boolean off = locked.contains(number);
                long quests = plugin.quests().story().stream().filter(q -> q.chapter() == number).count();
                out.append("\n").append(off ? "<red>✖ off " : "<green>✔ on  ").append("<white>").append(number).append(". ")
                        .append(Text.escape(name)).append(off ? "" : " <dark_gray>(" + quests + " story quests)");
            });
            plugin.send(sender, out.toString());
            return;
        }
        int number;
        try { number = Integer.parseInt(args[1]); } catch (NumberFormatException e) { plugin.send(sender, T.t("admin-command.usage-cq-chapter-on-off", "<red>Usage: /cq chapter <number> on|off")); return; }
        String mode = args[2].toLowerCase(Locale.ROOT);
        if (!List.of("on", "enable", "true", "off", "disable", "false").contains(mode)) { plugin.send(sender, T.t("admin-command.usage-cq-chapter-on-off", "<red>Usage: /cq chapter <number> on|off")); return; }
        boolean on = List.of("on", "enable", "true").contains(mode);
        if (!names.containsKey(number)) { plugin.send(sender, T.t("admin-command.quests-yml-has-no-chapter", "<red>quests.yml has no chapter <number>.", "number", number)); return; }
        if (number == 1 && !on) { plugin.send(sender, T.t("admin-command.chapter-1-is-where-everyone", "<red>Chapter 1 is where everyone starts and can't be switched off.")); return; }
        if (on != locked.contains(number)) { plugin.send(sender, T.t("admin-command.chapter-is-already", "<gray>Chapter <number> is already <off>.", "number", number, "off", (on ? "on" : "off"))); return; }
        var next = new java.util.TreeSet<>(locked);
        if (on) next.remove(number); else next.add(number);
        plugin.getConfig().set("chapters.locked", new ArrayList<>(next));
        plugin.saveConfig();
        plugin.reload();
        plugin.send(sender, on
                ? "<green>Chapter " + number + " (" + Text.escape(names.get(number)) + ") is on. Its villagers appear for players who reach it; place them with <yellow>/cq scatterworld chapter" + number + " 10000</yellow> or let auto placement do it."
                : "<yellow>Chapter " + number + " is off. Its villagers are gone for now; nobody's progress was changed.");
    }

    private void backup(CommandSender sender) {
        plugin.send(sender, T.t("admin-command.backing-up-quest-data", "<gray>Backing up quest data..."));
        Sched.async(() -> {
            String name = plugin.backups().backup("manual");
            plugin.send(sender, name == null ? "<red>Backup failed, see the console." : "<green>Saved backups/" + name);
        });
    }

    private void backups(CommandSender sender) {
        List<File> files = plugin.backups().files();
        if (files.isEmpty()) {
            plugin.send(sender, T.t("admin-command.no-backups-yet-make-one", "<gray>No backups yet. Make one with <yellow>/cq backup</yellow>."));
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
            plugin.send(sender, T.t("admin-command.usage-cq-restore", "<red>Usage: /cq restore <backup|latest> <player|all>"));
            return;
        }
        File backup = plugin.backups().find(args[1]);
        if (backup == null) {
            plugin.send(sender, T.t("admin-command.no-backup-called-see-cq", "<red>No backup called '<input>'. See /cq backups.", "input", Text.escape(args[1])));
            return;
        }
        UUID target = null;
        if (!args[2].equalsIgnoreCase("all")) {
            target = resolve(args[2]);
            if (target == null) {
                plugin.send(sender, T.t("admin-command.unknown-player-use-their-exact", "<red>Unknown player '<input2>'. Use their exact name or UUID.", "input2", Text.escape(args[2])));
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
                plugin.send(sender, T.t("admin-command.restore-failed", "<red>Restore failed: <getmessage>", "getmessage", Text.escape(String.valueOf(e.getMessage()))));
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
            plugin.send(sender, T.t("admin-command.usage-cq-player-reset-complete", "<red>Usage: /cq player <name> reset|complete <quest>|give <quest>|resetdaily"));
            return;
        }
        Player target = Bukkit.getPlayerExact(args[1]);
        if (target == null) {
            plugin.send(sender, T.t("admin-command.that-player-is-not-online", "<red>That player is not online."));
            return;
        }
        PlayerData data = plugin.questManager().data(target);
        String action = args[2].toLowerCase(Locale.ROOT);
        Quest quest = args.length > 3 ? plugin.quests().get(args[3]) : null;
        switch (action) {
            case "reset" -> {
                data.reset();
                plugin.send(sender, T.t("admin-command.reset-all-quest-progress-for", "<green>Reset all quest progress for <player>.", "player", target.getName()));
            }
            case "resetdaily" -> {
                data.setLastDailyAt(0);
                plugin.send(sender, T.t("admin-command.can-take-a-new-daily", "<green><player> can take a new daily quest now.", "player", target.getName()));
            }
            case "complete" -> {
                if (quest == null) {
                    plugin.send(sender, T.t("admin-command.unknown-quest", "<red>Unknown quest."));
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
                plugin.send(sender, T.t("admin-command.done-if-the-quest-was", "<green>Done. If the quest was active it now waits for turn-in."));
            }
            case "give" -> {
                if (quest == null) {
                    plugin.send(sender, T.t("admin-command.unknown-quest", "<red>Unknown quest."));
                    return;
                }
                data.uncomplete(quest.id());
                if (quest.category() == QuestCategory.SIDE) {
                    data.setSideDone(quest.giver(), Math.min(data.sideDone(quest.giver()), quest.order() - 1));
                }
                plugin.questManager().forceAccept(target, quest);
                plugin.send(sender, T.t("admin-command.gave-to", "<green>Gave <name> to <player>.", "name", Text.escape(quest.name()), "player", target.getName()));
            }
            default -> plugin.send(sender, T.t("admin-command.unknown-action", "<red>Unknown action."));
        }
        plugin.visibility().refresh(target);
    }

    private void finale(CommandSender sender, String[] args) {
        Player target = args.length > 1 ? Bukkit.getPlayerExact(args[1]) : sender instanceof Player p ? p : null;
        if (target == null) {
            plugin.send(sender, T.t("admin-command.usage-cq-finale-player", "<red>Usage: /cq finale [player]"));
            return;
        }
        plugin.finale().play(target, true);
        plugin.send(sender, T.t("admin-command.playing-the-ending-for-preview", "<green>Playing the ending for <player> (preview, no advancement).", "player", target.getName()));
    }

    private void quest(CommandSender sender, String[] args) {
        Quest quest = args.length > 1 ? plugin.quests().get(args[1]) : null;
        if (quest == null) {
            plugin.send(sender, T.t("admin-command.usage-cq-quest-example-ids", "<red>Usage: /cq quest <id>. Example ids: welcome, side_jerry_1, daily_1"));
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
        if (!sender.hasPermission("cquests.admin")) {
            if (!canControlBosses(sender)) return List.of();
            if (args.length == 1) return QuestsCommand.filter(List.of("worldboss", "test"), args[0]);
            if (!bossCommand(args) && !(args.length == 2 && args[0].equalsIgnoreCase("test"))) return List.of();
            if (args.length == 2 && args[0].equalsIgnoreCase("test")) return QuestsCommand.filter(List.of("worldboss"), args[1]);
        }
        if (args.length == 1) {
            return QuestsCommand.filter(List.of("reload", "character", "npc", "pos1", "pos2", "scatter", "scatterworld", "worldscatter", "chapter", "camp", "farm", "merchant", "crate", "player", "quest", "finale", "test", "backup", "backups", "restore", "boss", "worldboss", "season"), args[0]);
        }
        String first = args[0].toLowerCase(Locale.ROOT);
        if (first.equals("crate") || first.equals("crates")) {
            if (args.length == 2) return QuestsCommand.filter(List.of("list", "place", "remove", "token", "wild", "hint"), args[1]);
            if (args.length == 3 && args[1].equalsIgnoreCase("remove")) return QuestsCommand.filter(plugin.crates().ids(), args[2]);
            if (args.length == 3 && args[1].equalsIgnoreCase("token")) return null;
            return List.of();
        }
        if(first.equals("merchant")){
            if(!(sender instanceof Player p)||!p.isOp())return List.of();
            if(args.length==2)return QuestsCommand.filter(List.of("test","list","spawn","point","shop","end","wand","undo","routeclear","walk","despawn","edit"),args[1]);
            if(args.length==3)return QuestsCommand.filter(plugin.merchants().all().stream().map(com.cquests.merchant.MerchantDefinition::id).toList(),args[2]);
        }
        if (first.equals("worldboss") || first.equals("wb") || first.equals("boss")) {
            if (args.length == 2) return QuestsCommand.filter(List.of("menu", "setspawn", "wand", "border", "radius", "interval", "spots", "nopass", "list", "arenas", "next", "spawn", "stop", "schedule", "selftest"), args[1]);
            String action = args[1].toLowerCase(Locale.ROOT);
            if (args.length == 3) {
                if (action.equals("spawn")) return QuestsCommand.filter(plugin.worldBosses().ids(), args[2]);
                if (action.equals("schedule")) return QuestsCommand.filter(List.of("on", "off"), args[2]);
                List<String> arenas = new ArrayList<>(plugin.worldBosses().arenaIds());
                if (!arenas.contains("main")) arenas.add("main");
                return QuestsCommand.filter(arenas, args[2]);
            }
            if (args.length == 4 && action.equals("interval")) return QuestsCommand.filter(List.of("2h", "6h", "24h", "400h", "off"), args[3]);
            if (args.length == 4 && action.equals("nopass")) return QuestsCommand.filter(List.of("here", "corner", "list", "remove", "clear", "show"), args[3]);
            if (args.length == 4 && action.equals("border")) return QuestsCommand.filter(List.of("show", "clear"), args[3]);
            if (args.length == 4 && action.equals("spawn")) { List<String> where = new ArrayList<>(plugin.worldBosses().arenaIds()); where.add(0, "here"); return QuestsCommand.filter(where, args[3]); }
            return List.of();
        }
        if (first.equals("season") || first.equals("seasons")) {
            if (args.length == 2) return QuestsCommand.filter(plugin.seasons().ids(), args[1]);
            if (args.length == 3) return QuestsCommand.filter(com.cquests.season.SeasonService.MODES, args[2]);
            return List.of();
        }
        if(first.equals("farm")&&args.length==2)return QuestsCommand.filter(List.of("wand","outside","save","anvil","bind"),args[1]);
        if(first.equals("character")){
            if(args.length==2){var ids=new ArrayList<String>();plugin.npcs().all().forEach(n->ids.add(n.id()));plugin.merchants().all().forEach(n->ids.add(n.id()));ids.add("pip");return QuestsCommand.filter(ids,args[1]);}
            if(args.length==3)return QuestsCommand.filter(List.of("name","title","prefix","format","speech-prefix","intro","idle","arrival","reset"),args[2]);
        }
        List<String> npcIds = plugin.npcs().all().stream().map(NpcDef::id).toList();
        if (first.equals("npc")) {
            if (args.length == 2) {
                return QuestsCommand.filter(List.of("list", "place", "remove", "tp", "repair", "rename", "skin"), args[1]);
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
                if (action.equals("boss")) return QuestsCommand.filter(new ArrayList<>(plugin.adventures().bossIds()), args[2]);
                if (action.equals("bossevent")) return QuestsCommand.filter(com.cquests.adventure.QuestAdventures.EVENTS, args[2]);
                if (action.equals("pip")) return QuestsCommand.filter(List.of("bow", "sword"), args[2]);
                if (action.equals("worldboss")) return QuestsCommand.filter(plugin.worldBosses().ids(), args[2]);
                if (action.equals("season")) return QuestsCommand.filter(plugin.seasons().ids(), args[2]);
                if (action.equals("discord")) return QuestsCommand.filter(List.of("chapter", "boss", "streak", "journey"), args[2]);
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
        if (first.equals("chapter") || first.equals("chapters")) {
            if (args.length == 2) return QuestsCommand.filter(plugin.quests().chapterNames().keySet().stream().map(String::valueOf).toList(), args[1]);
            if (args.length == 3) return QuestsCommand.filter(List.of("on", "off"), args[2]);
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
        if ((first.equals("scatter") || first.equals("scatterworld") || first.equals("worldscatter")) && args.length == 2) {
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
