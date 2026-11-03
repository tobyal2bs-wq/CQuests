package com.cquests;

import org.bukkit.configuration.file.YamlConfiguration;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

/** Adds new side villagers once; never replaces an existing NPC or any player data. */
final class ContentUpgrade {
    private ContentUpgrade() {}
    static void apply(CQuestsPlugin plugin) {
        applySideVillagers(plugin);
        applyChapters(plugin);
        applyChapters18(plugin);
        applyCoop19(plugin);
    }

    /** 1.9.0: co-op daily quests (coop_*) for groups of 2 to 4 players. */
    private static void applyCoop19(CQuestsPlugin plugin) {
        File marker = new File(plugin.getDataFolder(), ".content-1.9.0");
        if (marker.exists()) return;
        try {
            merge(plugin, "quests.yml", "quests", (id, value) -> id.startsWith("coop_"), ".before-1.9.0", List.of());
            Files.writeString(marker.toPath(), "Co-op daily quests added. Existing IDs and progress preserved.\n");
        } catch (Exception e) {
            plugin.getLogger().warning("Could not add the 1.9.0 co-op quests; existing files kept: " + e.getMessage());
        }
    }

    /**
     * 1.8.0: chapters 6 to 10 grow from 10 to 20 villagers each, with five mini bosses. New villagers,
     * quests and bosses are added; the story chain (order and requires) of chapter 6+ quests is
     * updated so the new quests slot in. Text an admin changed is kept.
     */
    private static void applyChapters18(CQuestsPlugin plugin) {
        File marker = new File(plugin.getDataFolder(), ".content-1.8.0");
        if (marker.exists()) return;
        try {
            java.util.function.BiPredicate<String, Object> later = (id, value) -> value instanceof org.bukkit.configuration.ConfigurationSection c && c.getInt("chapter") >= 6;
            merge(plugin, "npcs.yml", "npcs", later, ".before-1.8.0", List.of());
            merge(plugin, "quests.yml", "quests", later, ".before-1.8.0", List.of("order", "requires", "level"));
            merge(plugin, "bosses.yml", "bosses", (id, value) -> true, ".before-1.8.0", List.of());
            Files.writeString(marker.toPath(), "Chapters 6-10 now have 20 villagers each and five mini bosses. Existing IDs and progress preserved.\n");
        } catch (Exception e) {
            plugin.getLogger().warning("Could not add the 1.8.0 villagers; existing files kept: " + e.getMessage());
        }
    }

    /**
     * 1.7.0: adds chapters 6 to 10 (villagers, story quests and chapter names) to existing servers,
     * and swaps the two wheat quests for other crops when they are still word for word the old ones.
     * Anything the admin already has with the same id is left alone. Chapters 6 to 10 start switched off.
     */
    private static void applyChapters(CQuestsPlugin plugin) {
        File marker = new File(plugin.getDataFolder(), ".content-1.7.0");
        if (marker.exists()) return;
        try {
            // Word-for-word swaps first, while the files still have their original quoting.
            replaceExact(plugin, "quests.yml", java.util.Map.of(
                    "\"HARVEST WHEAT 16 wheat\"", "\"HARVEST CARROTS|POTATOES|BEETROOTS 16 crops\"",
                    "\"Harvest ripe wheat for {npc:steve}.\"", "\"Harvest ripe carrots, potatoes or beetroots for {npc:steve}.\"",
                    "\"My wheat is ready but my back isn't.\"", "\"My carrots and potatoes are ready but my back isn't.\"",
                    "\"BREED SHEEP 4 sheep\"", "\"SHEAR SHEEP 6 sheep\"",
                    "\"Breed four sheep for me. Wheat does the trick.\"", "\"Shear six of them before the heat gets to them.\""));
            replaceExact(plugin, "generator.yml", java.util.Map.of(
                    "\"WHEAT | 0 | 8 | 64 | wheat | wheat\"", "\"CARROTS | 0 | 8 | 64 | carrot | carrots\"",
                    "\"WHEAT | 0 | 16 | 64 | wheat | wheat\"", "\"CARROT | 0 | 16 | 64 | carrot | carrots\""));
            // Only the new chapters; villagers or quests an admin deleted on purpose stay deleted.
            merge(plugin, "npcs.yml", "npcs", (id, value) -> value instanceof org.bukkit.configuration.ConfigurationSection c && c.getInt("chapter") >= 6);
            merge(plugin, "quests.yml", "quests", (id, value) -> value instanceof org.bukkit.configuration.ConfigurationSection c && c.getInt("chapter") >= 6);
            merge(plugin, "quests.yml", "chapters", (id, value) -> id.matches("\\d+") && Integer.parseInt(id) >= 6);
            Files.writeString(marker.toPath(), "Chapters 6-10 added (switched off until /cq chapter <n> on). Existing IDs and progress preserved.\n");
        } catch (Exception e) {
            plugin.getLogger().warning("Could not add chapters 6 to 10; existing files kept: " + e.getMessage());
        }
    }

    /** Copies sections from the bundled file that the server's copy doesn't have yet, keeping a backup once. */
    private static void merge(CQuestsPlugin plugin, String name, String root, java.util.function.BiPredicate<String, Object> wanted) throws Exception {
        merge(plugin, name, root, wanted, ".before-1.7.0", List.of());
    }

    /** @param sync keys copied from the bundled file onto entries the server already has (story chain fields) */
    private static void merge(CQuestsPlugin plugin, String name, String root, java.util.function.BiPredicate<String, Object> wanted,
                              String backupSuffix, List<String> sync) throws Exception {
        File file = new File(plugin.getDataFolder(), name);
        if (!file.exists()) return;
        try (var stream = plugin.getResource(name)) {
            if (stream == null) return;
            var bundled = YamlConfiguration.loadConfiguration(new InputStreamReader(stream, StandardCharsets.UTF_8));
            var current = new YamlConfiguration();
            current.load(file);
            var section = bundled.getConfigurationSection(root);
            if (section == null) return;
            boolean changed = false;
            for (String id : section.getKeys(false)) {
                String path = root + "." + id;
                if (!wanted.test(id, section.get(id))) continue;
                if (current.contains(path)) {
                    for (String key : sync) {
                        Object value = section.get(id + "." + key);
                        if (value != null && !value.equals(current.get(path + "." + key))) { current.set(path + "." + key, value); changed = true; }
                    }
                    continue;
                }
                if (section.isConfigurationSection(id)) current.createSection(path, section.getConfigurationSection(id).getValues(true));
                else current.set(path, section.get(id));
                changed = true;
            }
            if (changed) {
                File backup = new File(plugin.getDataFolder(), name + backupSuffix);
                if (!backup.exists()) Files.copy(file.toPath(), backup.toPath());
                current.save(file);
            }
        }
    }

    private static void replaceExact(CQuestsPlugin plugin, String name, java.util.Map<String, String> swaps) throws Exception {
        File file = new File(plugin.getDataFolder(), name);
        if (!file.exists()) return;
        String text = Files.readString(file.toPath()), next = text;
        for (var swap : swaps.entrySet()) next = next.replace(swap.getKey(), swap.getValue());
        if (!next.equals(text)) {
            File backup = new File(plugin.getDataFolder(), name + ".before-1.7.0");
            if (!backup.exists()) Files.copy(file.toPath(), backup.toPath());
            Files.writeString(file.toPath(), next);
        }
    }

    private static void applySideVillagers(CQuestsPlugin plugin) {
        File marker = new File(plugin.getDataFolder(), ".content-1.1.0");
        if (marker.exists()) return;
        File file = new File(plugin.getDataFolder(), "npcs.yml");
        try (var stream = plugin.getResource("npcs.yml")) {
            if (stream == null) return;
            var bundled = YamlConfiguration.loadConfiguration(new InputStreamReader(stream, StandardCharsets.UTF_8));
            var current = new YamlConfiguration();
            current.load(file);
            boolean changed = false;
            for (String id : List.of("luma", "copper_jack", "map", "fern_gardener", "nox", "ember", "astra", "tilly_weaver")) {
                String path = "npcs." + id;
                if (!current.contains(path)) {
                    if (!changed && !new File(plugin.getDataFolder(), "npcs.yml.before-1.1.0").exists())
                        Files.copy(file.toPath(), file.toPath().resolveSibling("npcs.yml.before-1.1.0"));
                    var section = bundled.getConfigurationSection(path);
                    if (section != null) current.createSection(path, section.getValues(true));
                    changed = true;
                }
            }
            if (changed) current.save(file);
            Files.writeString(marker.toPath(), "Side villager upgrade applied. Existing IDs and progress preserved.\n");
        } catch (Exception e) {
            plugin.getLogger().warning("Could not add new side villagers; existing files kept: " + e.getMessage());
        }
    }
}
