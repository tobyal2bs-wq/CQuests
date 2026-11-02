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
    private NpcCustomization customization;
    public void customization(NpcCustomization customization){this.customization=customization;}
    private NpcDef decorated(NpcDef npc){return customization==null?npc:customization.apply(npc);}
    private final Map<String, Integer> chapters = new LinkedHashMap<>();

    public void load(File file, Settings settings, Logger log) {
        this.settings = settings;
        npcs.clear();
        chapters.clear();
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
            if (s.contains("chapter")) chapters.put(key, Math.max(1, s.getInt("chapter")));
            npcs.put(key, new NpcDef(
                    key,
                    s.getString("name", id),
                    s.getString("title", ""),
                    s.getString("profession", "NONE"),
                    s.getString("skin", "PLAINS"),
                    s.getBoolean("daily",false)?settings.dailyMinLevel:s.getInt("level",0),
                    s.getInt("act", 1),
                    s.getBoolean("personal", false),
                    s.getBoolean("daily", false),
                    s.getBoolean("baby", false),
                    s.getString("player-skin", ""),
                    s.getStringList("intro"),
                    s.getStringList("idle")));
        }
        log.info("Loaded " + npcs.size() + " NPCs");
    }

    public NpcDef get(String id) {
        if (id == null) return null;
        NpcDef exact = npcs.get(id.toLowerCase(Locale.ROOT));
        if (exact != null) return decorated(exact);
        String lookup = id.replaceAll("[^a-zA-Z0-9]", "").toLowerCase(Locale.ROOT);
        NpcDef match = null;
        for (NpcDef raw : npcs.values()) {
            NpcDef npc=decorated(raw);
            if (Text.plain(Text.mm(npc.name())).replaceAll("[^a-zA-Z0-9]", "").toLowerCase(Locale.ROOT).equals(lookup)) {
                if (match != null) return null;
                match = npc;
            }
        }
        return match;
    }

    public int chapter(String id) { return chapters.getOrDefault(id, 0); }

    public Collection<NpcDef> all() {
        return npcs.values().stream().map(this::decorated).toList();
    }

    /** "<blue>Villager Stephan</blue>" style mention used inside quest text. */
    public String mention(String id) {
        NpcDef npc = get(id);
        String name = npc == null ? id : npc.name();
        return settings.npcMentionFormat.replace("<name>", name);
    }

    public String name(String id) {
        NpcDef npc = get(id);
        return npc == null ? id : Text.plain(Text.mm(npc.name()));
    }
}
