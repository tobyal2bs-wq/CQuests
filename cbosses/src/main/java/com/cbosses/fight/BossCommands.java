package com.cbosses.fight;

import org.bukkit.configuration.ConfigurationSection;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Console commands a boss runs, set per boss in bosses.yml and for a whole group in config.yml.
 *
 * <pre>
 * config.yml                              bosses.yml (one boss)
 * rewards:                                  my_boss:
 *   commands:                                 commands:          # (existing) every rewarded player
 *     bosses:      # big and mythic             top-commands:      # (existing) the best player
 *       every-player: []                        spawn-commands: [] # once when it wakes
 *       top-player: []                          defeat-commands: []# once when it falls
 *       on-spawn: []                            group-commands: true  # false: skip config.yml's group lists
 *       on-defeat: []
 *     minis:    { same four lists }
 *     chapter:  { same four lists }
 *     seasonal: { same four lists, run on top of bosses: }
 * </pre>
 *
 * Placeholders: %player% (rewarded player, or the killer / nearest player for spawn and defeat), %place%,
 * %boss% (the id), %bossname% (plain name), %world%, %x%, %y%, %z%. Pure data, so it is unit tested without a server.
 */
public final class BossCommands {

    public static final List<String> WHEN = List.of("every-player", "top-player", "on-spawn", "on-defeat");

    /** per boss id: its own spawn and defeat commands and whether it takes the group lists */
    private final Map<String, List<String>> spawn = new HashMap<>(), defeat = new HashMap<>();
    private final Map<String, Boolean> group = new HashMap<>();
    /** group -> when -> commands */
    private final Map<String, Map<String, List<String>>> groups = new HashMap<>();

    public void load(ConfigurationSection bosses, ConfigurationSection config) {
        spawn.clear(); defeat.clear(); group.clear(); groups.clear();
        if (bosses != null) for (String id : bosses.getKeys(false)) {
            ConfigurationSection s = bosses.getConfigurationSection(id);
            if (s == null) continue;
            String key = id.toLowerCase(Locale.ROOT);
            spawn.put(key, clean(s.getStringList("spawn-commands")));
            defeat.put(key, clean(s.getStringList("defeat-commands")));
            group.put(key, s.getBoolean("group-commands", true));
        }
        ConfigurationSection c = config == null ? null : config.getConfigurationSection("rewards.commands");
        if (c != null) for (String g : c.getKeys(false)) {
            ConfigurationSection s = c.getConfigurationSection(g);
            if (s == null) continue;
            Map<String, List<String>> lists = new HashMap<>();
            for (String w : WHEN) lists.put(w, clean(s.getStringList(w)));
            groups.put(g.toLowerCase(Locale.ROOT), lists);
        }
    }

    /** The config.yml groups a boss belongs to: minis, chapter, or bosses (plus seasonal for seasonal ones). */
    public static List<String> groupsOf(BossDef def) {
        if (def.mini() || def.sidekick() && "mini".equals(def.tier())) return List.of("minis");
        if (def.chapterBoss()) return List.of("chapter");
        if (def.seasonal()) return List.of("bosses", "seasonal");
        return List.of("bosses");
    }

    /** Commands for one moment ("every-player", "top-player", "on-spawn" or "on-defeat"), the boss's own last. */
    public List<String> forBoss(BossDef def, String when, List<String> own) {
        List<String> out = new ArrayList<>();
        if (group.getOrDefault(def.id(), true))
            for (String g : groupsOf(def)) out.addAll(groups.getOrDefault(g, Map.of()).getOrDefault(when, List.of()));
        switch (when) {
            case "on-spawn" -> out.addAll(spawn.getOrDefault(def.id(), List.of()));
            case "on-defeat" -> out.addAll(defeat.getOrDefault(def.id(), List.of()));
            default -> { if (own != null) out.addAll(own); }
        }
        return out;
    }

    public static String fill(String raw, Map<String, String> values) {
        String s = raw;
        for (var e : values.entrySet()) s = s.replace("%" + e.getKey() + "%", e.getValue());
        s = s.replace("<player>", values.getOrDefault("player", ""));
        return s.startsWith("/") ? s.substring(1) : s;
    }

    private static List<String> clean(List<String> in) {
        List<String> out = new ArrayList<>();
        for (String s : in) if (s != null && !s.isBlank()) out.add(s.trim());
        return out;
    }
}
