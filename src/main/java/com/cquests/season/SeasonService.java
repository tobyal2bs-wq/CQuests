package com.cquests.season;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;

import java.time.LocalDate;
import java.time.MonthDay;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Seasonal events (Halloween, Winter, Spring, Summer). Each one is on, off, or auto (on between its
 * from and to dates). While a season is on, its daily quests (quests.yml "season: halloween") can be
 * offered and its world boss takes the weekly slot.
 */
public final class SeasonService {
    public static final List<String> MODES = List.of("on", "off", "auto");
    private final CQuestsPlugin plugin;

    public SeasonService(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    public List<String> ids() {
        // Keys from the bundled defaults too, so servers whose config.yml predates seasons still have them.
        java.util.Set<String> out = new java.util.LinkedHashSet<>();
        var defaults = plugin.getConfig().getDefaults();
        ConfigurationSection d = defaults == null ? null : defaults.getConfigurationSection("seasons");
        if (d != null) out.addAll(d.getKeys(false));
        if (plugin.getConfig().isConfigurationSection("seasons")) out.addAll(plugin.getConfig().getConfigurationSection("seasons").getKeys(false));
        return new ArrayList<>(out);
    }

    /** getString(path) falls back to the bundled config.yml; getString(path, def) would skip it. */
    private static String or(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    public String mode(String id) {
        // YAML reads a bare on/off as true/false.
        String mode = String.valueOf(or(plugin.getConfig().getString("seasons." + id + ".mode"), "off")).toLowerCase(Locale.ROOT);
        return mode.equals("true") ? "on" : mode.equals("false") ? "off" : mode;
    }

    public String name(String id) {
        return or(plugin.getConfig().getString("seasons." + id + ".name"), id);
    }

    public boolean active(String id) {
        if (id == null || id.isEmpty()) return true;
        String mode = mode(id);
        if (mode.equals("on")) return true;
        if (!mode.equals("auto")) return false;
        try {
            MonthDay from = MonthDay.parse("--" + or(plugin.getConfig().getString("seasons." + id + ".from"), "01-01"));
            MonthDay to = MonthDay.parse("--" + or(plugin.getConfig().getString("seasons." + id + ".to"), "01-01"));
            return inWindow(from, to, LocalDate.now());
        } catch (RuntimeException e) {
            return false;
        }
    }

    /** True when {@code day} falls between from and to, both included, also across New Year (12-10 to 01-05). */
    public static boolean inWindow(MonthDay from, MonthDay to, LocalDate day) {
        MonthDay d = MonthDay.from(day);
        if (!from.isAfter(to)) return !d.isBefore(from) && !d.isAfter(to);
        return !d.isBefore(from) || !d.isAfter(to);
    }

    public List<String> activeIds() {
        List<String> out = new ArrayList<>();
        for (String id : ids()) if (active(id)) out.add(id);
        return out;
    }

    /** Names of the seasons that are on now, for placeholders: "Halloween, Winterfest" or "". */
    public String activeNames() {
        List<String> out = new ArrayList<>();
        for (String id : activeIds()) out.add(Text.plain(Text.mm(name(id))));
        return String.join(", ", out);
    }

    public void command(CommandSender sender, String[] args) {
        if (args.length < 2) {
            plugin.send(sender, "<gold>Seasons</gold> <gray>(/cq season <id> on|off|auto)");
            for (String id : ids())
                sender.sendMessage(Text.mm(" <dark_gray>-</dark_gray> <white>" + id + "</white> " + name(id) + " <gray>mode <white>" + mode(id)
                        + "</white>" + (mode(id).equals("auto") ? " (" + or(plugin.getConfig().getString("seasons." + id + ".from"), "?") + " to "
                        + or(plugin.getConfig().getString("seasons." + id + ".to"), "?") + ")" : "") + (active(id) ? " <green>● on now" : " <dark_gray>○ off")));
            return;
        }
        String id = args[1].toLowerCase(Locale.ROOT);
        if (!ids().contains(id)) { plugin.send(sender, "<red>No season " + Text.escape(id) + ". <gray>Seasons: " + String.join(", ", ids())); return; }
        if (args.length < 3 || !MODES.contains(args[2].toLowerCase(Locale.ROOT))) { plugin.send(sender, "<yellow>/cq season " + id + " on|off|auto"); return; }
        boolean was = active(id);
        plugin.getConfig().set("seasons." + id + ".mode", args[2].toLowerCase(Locale.ROOT));
        plugin.saveConfig();
        boolean now = active(id);
        plugin.send(sender, "<gray>" + name(id) + " <gray>is now <white>" + mode(id) + "</white>" + (now ? " <green>(running)" : " <dark_gray>(not running)"));
        if (now && !was) {
            String text = plugin.getConfig().getString("seasons." + id + ".announce", "<gold><bold>✦ " + name(id) + " <gold>has begun!</bold> <gray>Seasonal dailies and a seasonal world boss are here for a limited time.");
            Sched.global(() -> Bukkit.broadcast(Text.mm(text)));
        } else if (was && !now) {
            Sched.global(() -> Bukkit.broadcast(Text.mm("<gray>" + name(id) + " <gray>has ended. See you next time!")));
        }
    }
}
