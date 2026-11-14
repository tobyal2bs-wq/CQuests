package com.cbosses.fight;

import org.bukkit.Material;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.Mob;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.logging.Logger;

/**
 * One boss from bosses.yml. Pure data, so it can be checked without a server.
 * kind: world (the weekly rotation), seasonal (takes the weekly slot while its season is on) or chapter
 * (fought by one player after finishing a CQuests chapter; it can still be spawned from the panel).
 */
public record BossDef(String id, String name, String title, String kind, int chapter, EntityType entity, double health, double scale,
                      double damage, double speed, double armor, String bar, String theme, String movement, double flyHeight,
                      List<Double> phases, Map<String, String> equipment, EntityType minion, int minions, List<String> abilities,
                      int abilitySeconds, String season, Rewards rewards, int size, String model, double healthPerPlayer,
                      String spawnText, String deathText, String description, String tier,
                      String partner, double evolve) {

    public record Rewards(long money, long topMoney, List<String> items, List<String> topItems, List<String> commands, List<String> topCommands) {
        static final Rewards NONE = new Rewards(0, 0, List.of(), List.of(), List.of(), List.of());
    }

    public static final Set<String> KINDS = Set.of("world", "seasonal", "chapter", "mini", "partner");
    /** Health tiers: mini (hourly), big (weekly and chapter) and mythic (legends and the finale). */
    public static final Set<String> TIERS = Set.of("mini", "big", "mythic");
    public static final Set<String> MOVEMENTS = Set.of("walk", "fly", "hover", "still");
    public static final Set<String> SLOTS = Set.of("head", "chest", "legs", "feet", "hand", "offhand");

    public boolean seasonal() { return kind.equals("seasonal"); }
    public boolean chapterBoss() { return kind.equals("chapter"); }
    public boolean mini() { return kind.equals("mini"); }
    /** The second body of a two-body boss: it only appears beside the boss that names it as partner. */
    public boolean sidekick() { return kind.equals("partner"); }
    public boolean flies() { return movement.equals("fly") || movement.equals("hover"); }

    /** Reads every boss; a broken entry is skipped with a warning that names it. */
    public static Map<String, BossDef> load(YamlConfiguration yaml, Logger log) {
        Map<String, BossDef> out = new LinkedHashMap<>();
        ConfigurationSection root = yaml.getConfigurationSection("bosses");
        if (root == null) return out;
        for (String key : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(key);
            if (s == null) continue;
            String id = key.toLowerCase(Locale.ROOT);
            if (!s.getBoolean("enabled", true)) continue;
            try {
                out.put(id, parse(id, s));
            } catch (IllegalArgumentException e) {
                log.warning("bosses.yml: skipping '" + id + "': " + e.getMessage());
            }
        }
        return out;
    }

    static EntityType type(String raw, boolean mob) {
        if (raw == null || raw.isBlank() || raw.equalsIgnoreCase("none")) return null;
        EntityType type;
        try {
            type = EntityType.valueOf(raw.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("unknown entity " + raw);
        }
        Class<?> cls = type.getEntityClass();
        if (mob && (cls == null || !Mob.class.isAssignableFrom(cls))) throw new IllegalArgumentException(raw + " is not a mob");
        return type;
    }

    static BossDef parse(String id, ConfigurationSection s) {
        EntityType entity = type(s.getString("entity"), true);
        if (entity == null) throw new IllegalArgumentException("no entity");
        Map<String, String> equipment = new LinkedHashMap<>();
        ConfigurationSection eq = s.getConfigurationSection("equipment");
        if (eq != null) for (String slot : eq.getKeys(false)) {
            String lower = slot.toLowerCase(Locale.ROOT);
            if (!SLOTS.contains(lower)) throw new IllegalArgumentException("unknown equipment slot " + slot);
            String item = eq.getString(slot, "");
            if (Material.matchMaterial(item) == null) throw new IllegalArgumentException("unknown item " + item);
            equipment.put(lower, item.toUpperCase(Locale.ROOT));
        }
        List<String> abilities = new ArrayList<>();
        for (String a : s.getStringList("abilities")) {
            String lower = a.toLowerCase(Locale.ROOT);
            if (!Abilities.ALL.contains(lower)) throw new IllegalArgumentException("unknown ability " + a);
            abilities.add(lower);
        }
        EntityType minion = type(s.getString("minion"), true);
        if (abilities.contains("minions") && minion == null) throw new IllegalArgumentException("minions ability needs a minion entity");
        String season = s.getString("season", "").toLowerCase(Locale.ROOT);
        int chapter = Math.max(0, s.getInt("chapter", 0));
        String kind = s.getString("kind", chapter > 0 ? "chapter" : season.isEmpty() ? "world" : "seasonal").toLowerCase(Locale.ROOT);
        if (!KINDS.contains(kind)) throw new IllegalArgumentException("kind must be world, seasonal, chapter, mini or partner");
        String tier = s.getString("tier", kind.equals("mini") ? "mini" : "big").toLowerCase(Locale.ROOT);
        if (!TIERS.contains(tier)) throw new IllegalArgumentException("tier must be mini, big or mythic");
        if (kind.equals("seasonal") && season.isEmpty()) throw new IllegalArgumentException("a seasonal boss needs a season");
        if (kind.equals("chapter") && chapter <= 0) throw new IllegalArgumentException("a chapter boss needs chapter: <number>");
        String movement = s.getString("movement", "walk").toLowerCase(Locale.ROOT);
        if (!MOVEMENTS.contains(movement)) throw new IllegalArgumentException("movement must be walk, fly, hover or still");
        List<Double> phases = new ArrayList<>();
        for (Object o : s.getList("phases", List.of(0.5))) {
            try { double p = Double.parseDouble(String.valueOf(o)); if (p > 0 && p < 1) phases.add(p); } catch (NumberFormatException ignored) { }
        }
        phases.sort((a, b) -> Double.compare(b, a));
        ConfigurationSection r = s.getConfigurationSection("rewards");
        Rewards rewards = r == null ? Rewards.NONE : new Rewards(Math.max(0, r.getLong("money")), Math.max(0, r.getLong("top-money")),
                r.getStringList("items"), r.getStringList("top-items"), r.getStringList("commands"), r.getStringList("top-commands"));
        String theme = s.getString("theme", "soul").toLowerCase(Locale.ROOT);
        if (!Theme.ALL.containsKey(theme)) throw new IllegalArgumentException("unknown theme " + theme + " (themes: " + String.join(", ", new java.util.TreeSet<>(Theme.ALL.keySet())) + ")");
        return new BossDef(id, s.getString("name", id), s.getString("title", ""), kind, chapter, entity,
                Math.max(20, s.getDouble("health", tier.equals("mythic") ? 8000 : tier.equals("mini") ? 3000 : 5000)), Math.max(0.5, Math.min(4, s.getDouble("scale", 1.5))),
                Math.max(0, s.getDouble("damage", 8)), Math.max(0, s.getDouble("speed", 0)), Math.max(0, s.getDouble("armor", 0)),
                s.getString("bar", "RED").toUpperCase(Locale.ROOT), theme, movement, Math.max(2, Math.min(20, s.getDouble("fly-height", 6))),
                List.copyOf(phases), Map.copyOf(equipment), minion, Math.max(0, Math.min(8, s.getInt("minions", 3))), List.copyOf(abilities),
                Math.max(3, s.getInt("ability-seconds", 7)), season, rewards,
                Math.max(1, Math.min(16, s.getInt("size", 1))), s.getString("model", id).toLowerCase(Locale.ROOT),
                Math.max(0, Math.min(2, s.getDouble("health-per-player", 0.25))),
                s.getString("spawn-text", ""), s.getString("death-text", ""), s.getString("description", ""), tier,
                s.getString("partner", "").toLowerCase(Locale.ROOT).trim(), s.contains("evolve") ? Math.max(0, Math.min(1, evolveChance(s.get("evolve")))) : -1);
    }

    /** evolve: true, false or a chance from 0 to 1 that this boss evolves during a fight. */
    static double evolveChance(Object o) {
        if (o instanceof Boolean b) return b ? 1 : 0;
        try { return Double.parseDouble(String.valueOf(o)); } catch (NumberFormatException e) { return -1; }
    }
}
