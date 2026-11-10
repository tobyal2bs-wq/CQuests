package com.cbosses.command;

import com.cbosses.T;

import com.cbosses.CBossesPlugin;
import com.cbosses.fight.BossDef;
import com.cbosses.fight.BossService;
import com.cbosses.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** /cbosses (aliases /cb, /bosses). Players see /cbosses next; controlling bosses needs op or the bosses.use permission. */
public final class BossCommand implements CommandExecutor, TabCompleter {
    private static final List<String> ADMIN = List.of("menu", "list", "spawn", "test", "stop", "selftest", "arena", "schedule", "chapter", "season", "finale", "settings", "reload", "info", "next", "help", "minis", "decor", "edit", "enable", "disable", "mythic");
    private final CBossesPlugin plugin;
    private final BossMenu menu;
    private final SettingsMenu settings;
    private final com.cbosses.mini.MiniMenu miniMenu;

    public BossCommand(CBossesPlugin plugin, BossMenu menu, SettingsMenu settings, com.cbosses.mini.MiniMenu miniMenu) {
        this.plugin = plugin; this.menu = menu; this.settings = settings; this.miniMenu = miniMenu;
    }

    /** Controlling bosses is for operators, and for anyone given bosses.use (cbosses.admin still works). */
    public static boolean canControl(CommandSender sender) {
        return sender.isOp() || sender.hasPermission("bosses.use") || sender.hasPermission("cbosses.admin");
    }

    private BossService s() { return plugin.service(); }
    private com.cbosses.fight.BossEditor editor() { return editor == null ? (editor = new com.cbosses.fight.BossEditor(plugin)) : editor; }
    private com.cbosses.fight.BossEditor editor;

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, String @NotNull [] args) {
        String sub = args.length == 0 ? (canControl(sender) && sender instanceof Player ? "menu" : "next") : args[0].toLowerCase(Locale.ROOT);
        if (sub.equals("next") || sub.equals("info")) { s().info(sender); return true; }
        if (sub.equals("chapter") && args.length >= 2 && args[1].equalsIgnoreCase("retry") && sender instanceof Player p) {
            if (!plugin.chapters().retry(p)) plugin.send(p, T.t("command.no-chapter-boss-is-waiting", "<gray>No chapter boss is waiting for you."));
            return true;
        }
        if (!canControl(sender)) { plugin.send(sender, T.t("command.you-can-t-use-that", "<red>You can't use that. <gray>Try /<label> next", "label", label)); return true; }
        Player player = sender instanceof Player p ? p : null;
        switch (sub) {
            case "menu", "gui" -> { if (player == null) plugin.send(sender, T.t("command.players-only", "<red>Players only.")); else menu.open(player, 0); }
            case "list" -> s().listBosses(sender);
            case "spawn" -> {
                if (args.length < 2) { plugin.send(sender, T.t("command.spawn-arena", "<yellow>/<label> spawn <boss> [arena]", "label", label)); return true; }
                if (args.length > 2 && args[2].equalsIgnoreCase("here")) {
                    if (player == null) plugin.send(sender, T.t("command.players-only", "<red>Players only."));
                    else s().spawnHere(player, args[1]);
                    return true;
                }
                String arena = args.length > 2 ? args[2] : plugin.getConfig().getString("schedule.arena", "main");
                BossDef def = s().def(args[1]);
                var a = s().arena(arena, false);
                if (def == null) plugin.send(sender, T.t("command.no-boss", "<red>No boss <input>", "input", Text.escape(args[1])));
                else if (a == null) plugin.send(sender, T.t("command.no-arena", "<red>No arena <arena>", "arena", Text.escape(arena)));
                else if (s().spawn(def, a, player, false, null)) plugin.send(sender, T.t("command.is-rising-at", "<green><boss> <green>is rising at <arena>.", "boss", def.name(), "arena", a.id));
            }
            case "test" -> {
                if (player == null) { plugin.send(sender, T.t("command.players-only-console-can-run", "<red>Players only. Console can run /<label> selftest.", "label", label)); return true; }
                if (args.length < 2) { plugin.send(player, T.t("command.test-phase-stop", "<yellow>/<label> test <boss>|phase|stop", "label", label)); return true; }
                switch (args[1].toLowerCase(Locale.ROOT)) {
                    case "stop" -> { if (!s().testStop(player)) plugin.send(player, T.t("command.you-have-no-test-boss", "<gray>You have no test boss.")); }
                    case "phase" -> { if (!s().testPhase(player)) plugin.send(player, T.t("command.you-have-no-test-boss", "<gray>You have no test boss.")); }
                    default -> s().test(player, args[1]);
                }
            }
            case "stop" -> {
                if (args.length < 2) { s().stopAll(); plugin.send(sender, T.t("command.every-boss-was-sent-away", "<gray>Every boss was sent away.")); return true; }
                if (!s().stop(args[1]) && !s().stopBoss(args[1].toLowerCase(Locale.ROOT))) plugin.send(sender, T.t("command.nothing-to-stop-called", "<gray>Nothing to stop called <input>.", "input", Text.escape(args[1])));
            }
            case "selftest" -> { plugin.send(sender, T.t("command.running-the-boss-self-test", "<gray>Running the boss self-test near the world spawn (takes about a minute)...")); s().selfTest(sender); }
            case "arena" -> arena(sender, player, label, args);
            case "schedule" -> {
                if (args.length >= 2 && (args[1].equalsIgnoreCase("on") || args[1].equalsIgnoreCase("off"))) s().scheduleToggle(sender, args[1].equalsIgnoreCase("on"));
                else s().info(sender);
            }
            case "chapter" -> {
                String act = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "";
                if (act.equals("bosses") || act.equals("list")) { plugin.chapters().list(sender); return true; }
                if (act.equals("set") && args.length >= 4) {
                    try {
                        int n = Integer.parseInt(args[2]);
                        if (plugin.chapters().set(n, args[3])) { plugin.send(sender, T.t("command.chapter-set", "<green>Chapter <n> boss set. Player progress is kept.", "n", n)); plugin.chapters().list(sender); }
                        else plugin.send(sender, T.t("command.no-boss", "<red>No boss <input>", "input", Text.escape(args[3])));
                    } catch (NumberFormatException e) { plugin.send(sender, T.t("command.chapter-must-be-a-number", "<red>Chapter must be a number.")); }
                    return true;
                }
                if (act.equals("swap") && args.length >= 4) {
                    try {
                        int a = Integer.parseInt(args[2]), b = Integer.parseInt(args[3]);
                        if (plugin.chapters().swap(a, b)) { plugin.send(sender, T.t("command.chapter-swapped", "<green>Swapped the bosses of chapters <a> and <b>. Player progress is kept.", "a", a, "b", b)); plugin.chapters().list(sender); }
                        else plugin.send(sender, T.t("command.chapter-swap-missing", "<red>Both chapters need a boss."));
                    } catch (NumberFormatException e) { plugin.send(sender, T.t("command.chapter-must-be-a-number", "<red>Chapter must be a number.")); }
                    return true;
                }
                if (args.length >= 3 && args[1].equalsIgnoreCase("reset")) {
                    var target = Bukkit.getOfflinePlayer(args[2]);
                    plugin.chapters().reset(target.getUniqueId());
                    plugin.send(sender, T.t("command.chapter-bosses-reset-for", "<gray>Chapter bosses reset for <input2>.", "input2", Text.escape(args[2])));
                    return true;
                }
                if (args.length < 3) { plugin.send(sender, T.t("command.chapter-reset-retry", "<yellow>/<label> chapter <player> <chapter> <gray>| bosses | set <chapter> <boss|default> | swap <a> <b> | reset <player> | retry", "label", label)); return true; }
                Player target = Bukkit.getPlayerExact(args[1]);
                int n;
                try { n = Integer.parseInt(args[2]); } catch (NumberFormatException e) { plugin.send(sender, T.t("command.chapter-must-be-a-number", "<red>Chapter must be a number.")); return true; }
                if (target == null) { plugin.send(sender, T.t("command.is-not-online", "<red><input> is not online.", "input", Text.escape(args[1]))); return true; }
                if (plugin.chapters().bossFor(n) == null) { plugin.send(sender, T.t("command.no-boss-for-chapter", "<red>No boss for chapter <n>.", "n", n)); return true; }
                plugin.send(sender, plugin.chapters().trigger(target, n, true) ? T.t("command.chapter-boss-coming", "<green>Chapter <n> boss is coming for <player>.", "n", n, "player", target.getName()) : T.t("command.they-already-have-a-boss", "<yellow>They already have a boss coming."));
            }
            case "season", "seasons" -> plugin.seasons().command(sender, args);
            case "minis", "mini" -> minis(sender, player, label, args);
            case "edit" -> {
                if (args.length < 2) { plugin.send(sender, T.t("command.edit-usage", "<yellow>/<label> edit <boss> [<field> <value>] <gray>fields: <list>", "label", label, "list", String.join(", ", com.cbosses.fight.BossEditor.FIELDS))); return true; }
                if (args.length < 4) { editor().show(sender, args[1].toLowerCase(Locale.ROOT)); return true; }
                editor().set(sender, args[1], args[2], String.join(" ", java.util.Arrays.copyOfRange(args, 3, args.length)));
            }
            case "enable", "disable" -> {
                if (args.length < 2) {
                    List<String> off = editor().disabled();
                    plugin.send(sender, T.t("command.disabled-list", "<gray>Turned off: <white><list>", "list", off.isEmpty() ? "none" : String.join(", ", off)));
                    return true;
                }
                editor().set(sender, args[1], "enabled", sub.equals("enable") ? "true" : "false");
            }
            case "mythic" -> {
                String what = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "list";
                if ((what.equals("add") || what.equals("remove")) && args.length > 2) editor().set(sender, args[2], "tier", what.equals("add") ? "mythic" : "big");
                else plugin.send(sender, T.t("command.mythic-list", "<light_purple>Mythic bosses: <white><list> <gray>(/<label> mythic add|remove <boss>; their extra damage, health and evolving are under mythic: in config.yml)",
                        "list", String.join(", ", editor().mythics()), "label", label));
            }
            case "decor", "decoration" -> plugin.decor().command(sender, player, label, args);
            case "finale" -> {
                String what = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "info";
                switch (what) {
                    case "wake" -> plugin.send(sender, plugin.finale().wake(true) ? T.t("command.finale-waking", "<light_purple>The finale is waking.") : T.t("command.finale-already", "<gray>The finale is already on its way, or its boss is missing."));
                    case "reset" -> { plugin.finale().reset(); plugin.send(sender, T.t("command.finale-reset", "<gray>Finale progress reset: every legend must be beaten again.")); }
                    default -> plugin.finale().info(sender);
                }
            }
            case "settings", "config" -> settings.command(sender, args);
            case "reload" -> { plugin.reloadAll(); plugin.send(sender, T.t("command.reloaded-bosses", "<green>Reloaded: <count> bosses.", "count", s().defs().size())); }
            default -> help(sender, label);
        }
        return true;
    }

    private void minis(CommandSender sender, Player player, String label, String[] args) {
        var m = plugin.minis();
        String what = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : (player != null ? "menu" : "info");
        switch (what) {
            case "menu" -> { if (player == null) plugin.send(sender, T.t("command.players-only", "<red>Players only.")); else miniMenu.open(player); }
            case "info", "list" -> m.info(sender);
            case "add" -> {
                if (player == null) { plugin.send(sender, T.t("command.players-only", "<red>Players only.")); return; }
                int r = plugin.getConfig().getInt("minis.radius", 24);
                try { if (args.length > 2) r = Integer.parseInt(args[2]); } catch (NumberFormatException ignored) { }
                var s = m.add(player.getLocation(), Math.max(8, r));
                plugin.send(sender, T.t("mini.added", "<green>Spot <white><id></white> added where you stand.", "id", s.id));
            }
            case "remove" -> {
                String id = args.length > 2 ? args[2] : null;
                if (id == null && player != null) { var near = m.nearest(player.getLocation(), 16); id = near == null ? null : near.id; }
                plugin.send(sender, id != null && m.remove(id) ? T.t("mini.removed", "<gray>Spot <white><id></white> removed.", "id", id) : T.t("mini.no-spot", "<red>No spot there. <gray>/<label> minis remove <id>", "label", label));
            }
            case "show" -> { if (player != null) { m.toggleMarkers(player); plugin.send(player, m.showing(player) ? T.t("mini.markers-on", "<green>Spot markers on.") : T.t("mini.markers-off", "<gray>Spot markers off.")); } }
            case "mode" -> {
                if (args.length < 3 || !com.cbosses.mini.MiniBosses.MODES.contains(args[2].toLowerCase(Locale.ROOT))) { plugin.send(sender, "<yellow>/" + label + " minis mode fixed|random|mixed"); return; }
                m.set("mode", args[2].toLowerCase(Locale.ROOT)); m.info(sender);
            }
            case "every" -> {
                try { m.set("every-minutes", Math.max(1, Integer.parseInt(args[2]))); m.setNext(System.currentTimeMillis() + m.everyMinutes() * 60_000L); m.info(sender); }
                catch (Exception e) { plugin.send(sender, "<yellow>/" + label + " minis every <minutes>"); }
            }
            case "next" -> {
                try { m.setNext(System.currentTimeMillis() + Math.max(0, Integer.parseInt(args[2])) * 60_000L); m.info(sender); }
                catch (Exception e) { plugin.send(sender, "<yellow>/" + label + " minis next <minutes from now>"); }
            }
            case "now" -> {
                int n = m.spawnRound(args.length > 2 ? args[2] : null);
                plugin.send(sender, n > 0 ? T.t("mini.woke", "<green>A mini boss is waking.") : T.t("mini.none", "<yellow>No mini could wake (max alive reached, no spots or no minis)."));
            }
            case "on", "off" -> { m.set("enabled", what.equals("on")); m.info(sender); }
            default -> plugin.send(sender, "<yellow>/" + label + " minis menu|info|add [radius]|remove [id]|show|mode <m>|every <min>|next <min>|now [boss]|on|off");
        }
    }

    private void arena(CommandSender sender, Player player, String label, String[] args) {
        if (args.length < 2 || args[1].equalsIgnoreCase("list")) { s().listArenas(sender); return; }
        String action = args[1].toLowerCase(Locale.ROOT);
        String id = args.length > 2 ? args[2] : "main";
        switch (action) {
            case "setspawn" -> { if (player == null) plugin.send(sender, T.t("command.players-only", "<red>Players only.")); else s().setSpawn(player, id); }
            case "wand" -> { if (player == null) plugin.send(sender, T.t("command.players-only", "<red>Players only.")); else s().giveWand(player, id); }
            case "show" -> {
                var a = s().arena(id, false);
                if (player == null || a == null) plugin.send(sender, T.t("command.no-arena-2", "<red>No arena <id>", "id", Text.escape(id))); else s().show(player, a);
            }
            case "region" -> s().setRegion(sender, id, args.length > 3 ? args[3] : null);
            case "radius" -> {
                try { s().setRadius(sender, id, Integer.parseInt(args.length > 3 ? args[3] : "40")); }
                catch (NumberFormatException e) { plugin.send(sender, T.t("command.radius-must-be-a-number", "<red>Radius must be a number.")); }
            }
            case "clear" -> s().clearBorder(sender, id);
            case "delete" -> s().deleteArena(sender, id);
            default -> plugin.send(sender, T.t("command.arena-setspawn-wand-show-region", "<yellow>/<label> arena setspawn|wand|show|region|radius|clear|delete|list <arena>", "label", label));
        }
    }

    private void help(CommandSender to, String label) {
        String l = "/" + label;
        plugin.send(to, T.t("command.cbosses-commands", "<gold>CBosses commands"));
        String[][] lines = {
                {"menu", "<cmd> menu <gray>every boss in a menu"},
                {"list", "<cmd> list <gray>boss ids"},
                {"test", "<cmd> test <boss>|phase|stop <gray>try a boss in front of you, nothing is paid"},
                {"spawn", "<cmd> spawn <boss> [arena|here] <gray>start a real fight (here: where you stand)"},
                {"minis", "<cmd> minis <gray>mini boss spots, timer, mode and markers"},
                {"decor", "<cmd> decor place <model>|remove|list <gray>pumpkins and other models that sit and pull faces"},
                {"stop", "<cmd> stop [arena|boss] <gray>send bosses away"},
                {"arena", "<cmd> arena setspawn|wand|region|radius|show|clear|delete <arena>"},
                {"schedule", "<cmd> schedule on|off <gray>the weekly boss"},
                {"chapter", "<cmd> chapter <player> <n> | reset <player> | retry"},
                {"season", "<cmd> season <id> on|off|auto"},
                {"finale", "<cmd> finale [wake|reset] <gray>the boss after the three legends"},
                {"selftest", "<cmd> selftest <gray>spawn every boss, run every attack and death"},
                {"settings", "<cmd> settings [page] <gray>every option in a settings screen | settings set <path> <value>"},
                {"edit", "<cmd> edit <boss> [field value] <gray>change name, color #hex [#hex], health, damage, bar, tier, evolve..."},
                {"disable", "<cmd> enable|disable <boss> <gray>turn a boss on or off (no name: list the ones that are off)"},
                {"mythic", "<cmd> mythic [add|remove <boss>] <gray>choose which bosses are mythic"},
                {"reload", "<cmd> reload"}};
        for (String[] line : lines)
            to.sendMessage(Text.mm(T.t("command.help." + line[0], " <yellow>" + line[1], "cmd", l)));
    }

    @Override
    public List<String> onTabComplete(@NotNull CommandSender sender, @NotNull Command command, @NotNull String alias, String @NotNull [] args) {
        if (!canControl(sender)) return args.length == 1 ? filter(List.of("next", "chapter"), args[0]) : List.of();
        if (args.length == 1) return filter(ADMIN, args[0]);
        String sub = args[0].toLowerCase(Locale.ROOT);
        if (args.length == 2) return switch (sub) {
            case "spawn" -> filter(s().ids(), args[1]);
            case "test" -> { List<String> out = new ArrayList<>(s().ids()); out.add("phase"); out.add("stop"); yield filter(out, args[1]); }
            case "stop" -> { List<String> out = new ArrayList<>(s().arenaIds()); out.addAll(s().ids()); yield filter(out, args[1]); }
            case "arena" -> filter(List.of("setspawn", "wand", "show", "region", "radius", "clear", "delete", "list"), args[1]);
            case "schedule" -> filter(List.of("on", "off"), args[1]);
            case "finale" -> filter(List.of("info", "wake", "reset"), args[1]);
            case "decor", "decoration" -> filter(List.of("place", "remove", "list"), args[1]);
            case "minis", "mini" -> filter(List.of("menu", "info", "add", "remove", "show", "mode", "every", "next", "now", "on", "off"), args[1]);
            case "settings", "config" -> filter(List.of("effects", "schedule", "fight", "chapters", "seasons", "set"), args[1]);
            case "season", "seasons" -> filter(plugin.seasons().ids(), args[1]);
            case "edit" -> filter(editor().ids(), args[1]);
            case "enable" -> filter(editor().disabled(), args[1]);
            case "disable" -> filter(s().ids(), args[1]);
            case "mythic" -> filter(List.of("list", "add", "remove"), args[1]);
            case "chapter" -> { List<String> out = new ArrayList<>(List.of("reset", "retry", "bosses", "set", "swap")); for (Player p : Bukkit.getOnlinePlayers()) out.add(p.getName()); yield filter(out, args[1]); }
            default -> List.of();
        };
        if (args.length == 3 && (sub.equals("settings") || sub.equals("config")) && args[1].equalsIgnoreCase("set")) {
            List<String> paths = new ArrayList<>();
            for (var pg : settings.pages()) for (var st : pg.settings()) paths.add(st.path());
            return filter(paths, args[2]);
        }
        if (args.length == 3) return switch (sub) {
            case "spawn" -> { List<String> out = new ArrayList<>(s().arenaIds()); out.add("here"); yield filter(out, args[2]); }
            case "arena" -> filter(s().arenaIds(), args[2]);
            case "decor", "decoration" -> args[1].equalsIgnoreCase("place") ? filter(plugin.decor().models(), args[2])
                    : args[1].equalsIgnoreCase("remove") ? filter(plugin.decor().ids(), args[2]) : List.of();
            case "minis", "mini" -> args[1].equalsIgnoreCase("mode") ? filter(com.cbosses.mini.MiniBosses.MODES, args[2])
                    : args[1].equalsIgnoreCase("now") ? filter(plugin.minis().minis().stream().map(com.cbosses.fight.BossDef::id).toList(), args[2])
                    : args[1].equalsIgnoreCase("remove") ? filter(plugin.minis().spots().stream().map(x -> x.id).toList(), args[2]) : List.of();
            case "season", "seasons" -> filter(List.of("on", "off", "auto"), args[2]);
            case "edit" -> filter(com.cbosses.fight.BossEditor.FIELDS, args[2]);
            case "mythic" -> args[1].equalsIgnoreCase("remove") ? filter(editor().mythics(), args[2]) : filter(s().ids(), args[2]);
            case "chapter" -> filter(List.of("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), args[2]);
            default -> List.of();
        };
        if (args.length == 4 && sub.equals("edit")) return switch (args[2].toLowerCase(Locale.ROOT)) {
            case "bar" -> filter(com.cbosses.fight.BossEditor.BARS, args[3]);
            case "tier" -> filter(List.of("mini", "big", "mythic"), args[3]);
            case "enabled" -> filter(List.of("true", "false"), args[3]);
            case "evolve" -> filter(List.of("true", "false", "0.5", "default"), args[3]);
            case "theme" -> filter(new ArrayList<>(com.cbosses.fight.Theme.ALL.keySet()), args[3]);
            case "partner" -> { List<String> out = new ArrayList<>(editor().ids()); out.add("none"); yield filter(out, args[3]); }
            case "color" -> filter(List.of("#ff5555", "#ffaa00"), args[3]);
            default -> List.of();
        };
        return List.of();
    }

    static List<String> filter(List<String> options, String typed) {
        String t = typed.toLowerCase(Locale.ROOT);
        List<String> out = new ArrayList<>();
        for (String o : options) if (o.toLowerCase(Locale.ROOT).startsWith(t)) out.add(o);
        return out;
    }
}
