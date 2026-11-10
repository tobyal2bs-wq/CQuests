package com.cbosses.fight;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.util.SafeFiles;
import com.cbosses.util.Text;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Op editing of bosses.yml from the game: names, colours, health, damage, bar colour, tier (mythic), whether
 * it evolves, and turning bosses on and off. Every change is written safely (a .bak copy is kept) and only the
 * one value changes, so nothing else in the file, and no player data, is touched. Running fights keep going.
 */
public final class BossEditor {
    public static final List<String> FIELDS = List.of("name", "color", "title", "health", "damage", "speed", "armor", "bar", "theme", "tier",
            "evolve", "ability-seconds", "health-per-player", "partner", "enabled", "description");
    public static final List<String> BARS = List.of("PINK", "BLUE", "RED", "GREEN", "YELLOW", "PURPLE", "WHITE");
    private static final Set<String> NUMBERS = Set.of("health", "damage", "speed", "armor", "ability-seconds", "health-per-player");
    private final CBossesPlugin plugin;

    public BossEditor(CBossesPlugin plugin) { this.plugin = plugin; }

    private File file() { return new File(plugin.getDataFolder(), "bosses.yml"); }

    private YamlConfiguration yaml() { return YamlConfiguration.loadConfiguration(file()); }

    /** Every boss in bosses.yml, turned on or not (the second body of a pair included). */
    public List<String> ids() {
        ConfigurationSection s = yaml().getConfigurationSection("bosses");
        return s == null ? List.of() : new ArrayList<>(s.getKeys(false));
    }

    public List<String> disabled() {
        YamlConfiguration y = yaml();
        List<String> out = new ArrayList<>();
        for (String id : ids()) if (!y.getBoolean("bosses." + id + ".enabled", true)) out.add(id);
        return out;
    }

    public List<String> mythics() {
        YamlConfiguration y = yaml();
        List<String> out = new ArrayList<>();
        for (String id : ids()) if ("mythic".equalsIgnoreCase(y.getString("bosses." + id + ".tier", ""))) out.add(id);
        return out;
    }

    public void show(CommandSender to, String id) {
        YamlConfiguration y = yaml();
        ConfigurationSection s = y.getConfigurationSection("bosses." + id);
        if (s == null) { plugin.send(to, T.t("edit.no-boss", "<red>No boss <id> in bosses.yml.", "id", Text.escape(id))); return; }
        plugin.send(to, T.t("edit.header", "<gold>Boss <white><id></white> <gray>(change with /cbosses edit <id> <field> <value>)", "id", id));
        for (String f : FIELDS) {
            if (f.equals("color")) continue;
            Object v = s.get(f);
            to.sendMessage(Text.mm(" <dark_gray>-</dark_gray> <yellow>" + f + "</yellow> <gray>" + (v == null ? "<dark_gray>(default)" : Text.escape(String.valueOf(v)))));
        }
    }

    /** Sets one value; returns false (and says why) when the value is not allowed. */
    public boolean set(CommandSender to, String id, String field, String value) {
        id = id.toLowerCase(Locale.ROOT);
        field = field.toLowerCase(Locale.ROOT);
        YamlConfiguration y = yaml();
        String base = "bosses." + id;
        if (!y.isConfigurationSection(base)) { plugin.send(to, T.t("edit.no-boss", "<red>No boss <id> in bosses.yml.", "id", Text.escape(id))); return false; }
        if (!FIELDS.contains(field)) { plugin.send(to, T.t("edit.fields", "<red>Fields: <list>", "list", String.join(", ", FIELDS))); return false; }
        Object out;
        String v = value.trim();
        try {
            if (NUMBERS.contains(field)) {
                double d = Double.parseDouble(v);
                if (d < 0 || (field.equals("health") && d < 20)) throw new NumberFormatException();
                out = d == Math.rint(d) && !field.equals("speed") && !field.equals("health-per-player") ? (Object) (long) d : (Object) d;
            } else switch (field) {
                case "bar" -> { if (!BARS.contains(v.toUpperCase(Locale.ROOT))) throw new IllegalArgumentException(String.join(", ", BARS)); out = v.toUpperCase(Locale.ROOT); }
                case "tier" -> { if (!BossDef.TIERS.contains(v.toLowerCase(Locale.ROOT))) throw new IllegalArgumentException("mini, big, mythic"); out = v.toLowerCase(Locale.ROOT); }
                case "theme" -> { if (!Theme.ALL.containsKey(v.toLowerCase(Locale.ROOT))) throw new IllegalArgumentException(String.join(", ", new java.util.TreeSet<>(Theme.ALL.keySet()))); out = v.toLowerCase(Locale.ROOT); }
                case "enabled" -> out = parseBool(v);
                case "evolve" -> {
                    if (v.equalsIgnoreCase("default")) out = null;
                    else if (v.equalsIgnoreCase("true") || v.equalsIgnoreCase("false")) out = Boolean.parseBoolean(v.toLowerCase(Locale.ROOT));
                    else { double d = Double.parseDouble(v); if (d < 0 || d > 1) throw new NumberFormatException(); out = d; }
                }
                case "partner" -> { if (!v.equalsIgnoreCase("none") && !y.isConfigurationSection("bosses." + v.toLowerCase(Locale.ROOT))) throw new IllegalArgumentException("a boss id or none"); out = v.equalsIgnoreCase("none") ? null : v.toLowerCase(Locale.ROOT); }
                case "color" -> {
                    String[] c = v.split("\\s+");
                    for (String hex : c) if (!hex.matches("#[0-9a-fA-F]{6}")) throw new IllegalArgumentException("#rrggbb [#rrggbb]");
                    String plain = Text.plain(Text.mm(y.getString(base + ".name", id)));
                    out = c.length >= 2 ? "<gradient:" + c[0] + ":" + c[1] + "><bold>" + Text.escape(plain) + "</bold></gradient>" : "<" + c[0] + "><bold>" + Text.escape(plain) + "</bold>";
                    field = "name";
                }
                default -> out = v;
            }
        } catch (NumberFormatException e) {
            plugin.send(to, T.t("edit.number", "<red><field> needs a number of 0 or more (health at least 20; evolve 0 to 1, true or false).", "field", field));
            return false;
        } catch (IllegalArgumentException e) {
            plugin.send(to, T.t("edit.allowed", "<red><field> must be one of: <list>", "field", field, "list", Text.escape(String.valueOf(e.getMessage()))));
            return false;
        }
        y.set(base + "." + field, out);
        try { SafeFiles.write(file(), y.saveToString()); }
        catch (IOException e) { plugin.send(to, T.t("edit.save-failed", "<red>Could not save bosses.yml: <error>", "error", Text.escape(String.valueOf(e.getMessage())))); return false; }
        plugin.service().reload();
        plugin.send(to, T.t("edit.saved", "<green>Saved <white><id></white> <field> = <white><value></white>. <gray>New fights use it; running fights keep their old values.",
                "id", id, "field", field, "value", out == null ? "default" : Text.escape(String.valueOf(out))));
        return true;
    }

    private static boolean parseBool(String v) {
        return switch (v.toLowerCase(Locale.ROOT)) {
            case "true", "on", "yes" -> true;
            case "false", "off", "no" -> false;
            default -> throw new IllegalArgumentException("true, false");
        };
    }
}
