package com.cquests.npc;

import com.cquests.Settings;
import com.cquests.model.NpcDef;
import com.cquests.util.Text;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.logging.Logger;

public final class NpcRegistry {

    private final Map<String, NpcDef> npcs = new LinkedHashMap<>();
    private Settings settings;

    public void load(File file, Settings settings, Logger log) {
        this.settings = settings;
        npcs.clear();
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection root = yaml.getConfigurationSection("npcs");
        if (root == null) {
            log.warning("npcs.yml has no 'npcs' section");
            return;
        }
        for (String id : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(id);
            if (s == null) {
                continue;
            }
            String key = id.toLowerCase(Locale.ROOT);
            npcs.put(key, new NpcDef(
                    key,
                    s.getString("name", id),
                    s.getString("title", ""),
                    s.getString("profession", "NONE"),
                    s.getString("skin", "PLAINS"),
                    s.getInt("level", 0),
                    s.getInt("act", 1),
                    s.getBoolean("personal", false),
                    s.getBoolean("daily", false),
                    s.getStringList("intro"),
                    s.getStringList("idle")));
        }
        log.info("Loaded " + npcs.size() + " NPCs");
    }

    public NpcDef get(String id) {
        return id == null ? null : npcs.get(id.toLowerCase(Locale.ROOT));
    }

    public Collection<NpcDef> all() {
        return npcs.values();
    }

    /** "<blue>Villager Stephan</blue>" style mention used inside quest text. */
    public String mention(String id) {
        NpcDef npc = get(id);
        String name = npc == null ? id : npc.name();
        return settings.npcMentionFormat.replace("<name>", Text.escape(name));
    }

    public String name(String id) {
        NpcDef npc = get(id);
        return npc == null ? id : npc.name();
    }
}
