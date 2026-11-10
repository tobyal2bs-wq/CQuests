package com.cbosses.season;

import com.cbosses.T;

import com.cbosses.CBossesPlugin;
import com.cbosses.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;

import java.time.LocalDate;
import java.time.MonthDay;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Seasons for seasonal bosses. Each is on, off, or auto (between its from and to dates every year).
 * With seasons.follow-cquests and CQuests installed, a season is also on whenever CQuests has it on.
 */
public final class Seasons {
    public static final List<String> MODES = List.of("on", "off", "auto");
    private final CBossesPlugin plugin;

    public Seasons(CBossesPlugin plugin) { this.plugin = plugin; }

    public List<String> ids() {
        Set<String> out = new LinkedHashSet<>();
        var defaults = plugin.getConfig().getDefaults();
        ConfigurationSection d = defaults == null ? null : defaults.getConfigurationSection("seasons.list");
        if (d != null) out.addAll(d.getKeys(false));
        var own = plugin.getConfig().getConfigurationSection("seasons.list");
        if (own != null) out.addAll(own.getKeys(false));
        return new ArrayList<>(out);
    }

    private static String or(String value, String fallback) { return value == null || value.isBlank() ? fallback : value; }

    public String mode(String id) {
        String mode = String.valueOf(or(plugin.getConfig().getString("seasons.list." + id + ".mode"), "auto")).toLowerCase(Locale.ROOT);
        return mode.equals("true") ? "on" : mode.equals("false") ? "off" : mode;
    }

    public String name(String id) { return or(plugin.getConfig().getString("seasons.list." + id + ".name"), id); }

    public boolean active(String id) {
        if (id == null || id.isEmpty()) return true;
        if (plugin.getConfig().getBoolean("seasons.follow-cquests", true) && cquests(id)) return true;
        String mode = mode(id);
        if (mode.equals("on")) return true;
        if (!mode.equals("auto")) return false;
        try {
            MonthDay from = MonthDay.parse("--" + or(plugin.getConfig().getString("seasons.list." + id + ".from"), "01-01"));
            MonthDay to = MonthDay.parse("--" + or(plugin.getConfig().getString("seasons.list." + id + ".to"), "01-01"));
            return inWindow(from, to, LocalDate.now());
        } catch (RuntimeException e) {
            return false;
        }
    }

    /** CQuests' own season switch, read without a compile-time dependency. */
    private static boolean cquests(String id) {
        var cq = Bukkit.getPluginManager().getPlugin("CQuests");
        if (cq == null || !cq.isEnabled()) return false;
        try {
            Object seasons = cq.getClass().getMethod("seasons").invoke(cq);
            return seasons != null && (boolean) seasons.getClass().getMethod("active", String.class).invoke(seasons, id);
        } catch (ReflectiveOperationException | RuntimeException e) {
            return false;
        }
    }

    public static boolean inWindow(MonthDay from, MonthDay to, LocalDate day) {
        MonthDay d = MonthDay.from(day);
        if (!from.isAfter(to)) return !d.isBefore(from) && !d.isAfter(to);
        return !d.isBefore(from) || !d.isAfter(to);
    }

    public void command(CommandSender sender, String[] args) {
        if (args.length < 2) {
            plugin.send(sender, T.t("season.seasons-cbosses-season-on-off", "<gold>Seasons</gold> <gray>(/cbosses season <id> on|off|auto)"));
            for (String id : ids())
                sender.sendMessage(Text.mm(T.t("season.mode", " <dark_gray>-</dark_gray> <white><id></white> <id2> <gray>mode <white><id3></white><off>", "id", id, "id2", name(id), "id3", mode(id), "off", (active(id) ? " <green>● on now" : " <dark_gray>○ off"))));
            return;
        }
        String id = args[1].toLowerCase(Locale.ROOT);
        if (!ids().contains(id)) { plugin.send(sender, T.t("season.no-season-seasons", "<red>No season <id>. <gray>Seasons: <list>", "id", Text.escape(id), "list", String.join(", ", ids()))); return; }
        if (args.length < 3 || !MODES.contains(args[2].toLowerCase(Locale.ROOT))) { plugin.send(sender, T.t("season.cbosses-season-on-off-auto", "<yellow>/cbosses season <id> on|off|auto", "id", id)); return; }
        plugin.getConfig().set("seasons.list." + id + ".mode", args[2].toLowerCase(Locale.ROOT));
        plugin.saveConfig();
        plugin.send(sender, T.t("season.is-now", "<gray><id> <gray>is now <white><id2></white><running>", "id", name(id), "id2", mode(id), "running", (active(id) ? " <green>(running)" : " <dark_gray>(not running)")));
    }
}
