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
