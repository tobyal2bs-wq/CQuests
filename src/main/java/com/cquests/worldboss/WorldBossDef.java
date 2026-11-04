package com.cquests.worldboss;

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

/** One world boss from worldbosses.yml. Pure data, so it can be checked without a server. */
public record WorldBossDef(String id, String name, String title, EntityType entity, double health, double scale,
                           double damage, double speed, double armor, String bar, boolean glow, String particle,
                           String color, Map<String, String> equipment, EntityType mount, EntityType rider,
                           EntityType minion, int minions, List<String> abilities, int abilitySeconds,
                           String season, Rewards rewards, int size, String halo) {

    public record Rewards(long money, long topMoney, List<String> items, List<String> topItems, List<String> commands, List<String> topCommands) {
        static final Rewards NONE = new Rewards(0, 0, List.of(), List.of(), List.of(), List.of());
    }

    public static final Set<String> ABILITIES = Set.of("lightning", "shockwave", "minions", "fire_ring", "pull", "leap",
            "poison", "blink", "frost", "volley", "darkness", "levitate", "heal", "quake", "detonate", "roar");
    public static final Set<String> SLOTS = Set.of("head", "chest", "legs", "feet", "hand", "offhand");

    public boolean seasonal() {
        return !season.isEmpty();
    }

    /** Reads every boss; a broken entry is skipped with a warning that names it. */
    public static Map<String, WorldBossDef> load(YamlConfiguration yaml, Logger log) {
        Map<String, WorldBossDef> out = new LinkedHashMap<>();
        ConfigurationSection root = yaml.getConfigurationSection("bosses");
        if (root == null) return out;
        for (String key : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(key);
            if (s == null) continue;
            String id = key.toLowerCase(Locale.ROOT);
            try {
                out.put(id, parse(id, s));
            } catch (IllegalArgumentException e) {
                log.warning("worldbosses.yml: skipping '" + id + "': " + e.getMessage());
            }
        }
        return out;
    }

    static EntityType type(String raw, boolean mob) {
        if (raw == null || raw.isBlank()) return null;
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

    private static WorldBossDef parse(String id, ConfigurationSection s) {
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
            if (!ABILITIES.contains(lower)) throw new IllegalArgumentException("unknown ability " + a);
            abilities.add(lower);
        }
        EntityType minion = type(s.getString("minion"), true);
        if (abilities.contains("minions") && minion == null) throw new IllegalArgumentException("minions ability needs a minion entity");
        ConfigurationSection r = s.getConfigurationSection("rewards");
        Rewards rewards = r == null ? Rewards.NONE : new Rewards(Math.max(0, r.getLong("money")), Math.max(0, r.getLong("top-money")),
                r.getStringList("items"), r.getStringList("top-items"), r.getStringList("commands"), r.getStringList("top-commands"));
        return new WorldBossDef(id, s.getString("name", id), s.getString("title", ""), entity,
                Math.max(20, s.getDouble("health", 800)), Math.max(0.5, Math.min(4, s.getDouble("scale", 1.5))),
                Math.max(0, s.getDouble("damage", 8)), Math.max(0, s.getDouble("speed", 0)), Math.max(0, s.getDouble("armor", 0)),
                s.getString("bar", "RED").toUpperCase(Locale.ROOT), s.getBoolean("glow", true), s.getString("particle", "FLAME").toUpperCase(Locale.ROOT),
                s.getString("color", "#ff5500"), Map.copyOf(equipment), type(s.getString("mount"), false), type(s.getString("rider"), false),
                minion, Math.max(0, Math.min(8, s.getInt("minions", 3))), List.copyOf(abilities),
                Math.max(3, s.getInt("ability-seconds", 8)), s.getString("season", "").toLowerCase(Locale.ROOT), rewards,
                Math.max(1, Math.min(16, s.getInt("size", 1))), s.getString("halo", null));
    }
}
