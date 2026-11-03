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
    public void customization(NpcCustomization customization){this.customization=customization;refresh();}
    /**
     * NPCs with renames from characters.yml applied, plus a lookup by visible name. Rebuilt only when
     * npcs.yml or a rename changes, instead of on every lookup (lookups run many times a second).
     */
    private volatile Map<String, NpcDef> view = Map.of();
    private volatile Map<String, NpcDef> byName = Map.of();
    private volatile Map<String, String> originalNames = Map.of();
    private static String simple(String text){return Text.plain(Text.mm(text)).replaceAll("[^a-zA-Z0-9]", "").toLowerCase(Locale.ROOT);}

    /** Call after npcs.yml is loaded or any NPC is renamed. */
    public synchronized void refresh() {
        Map<String, NpcDef> next = new LinkedHashMap<>();
        Map<String, NpcDef> names = new java.util.HashMap<>();
        Map<String, String> originals = new java.util.HashMap<>();
        java.util.Set<String> clashes = new java.util.HashSet<>();
        for (NpcDef raw : npcs.values()) {
            NpcDef npc = customization == null ? raw : customization.apply(raw);
            next.put(raw.id(), npc);
            String key = simple(npc.name());
            if (names.putIfAbsent(key, npc) != null) clashes.add(key);
            originals.putIfAbsent(simple(raw.name()), raw.id());
        }
        clashes.forEach(names::remove); // two NPCs with the same visible name: only the id finds them
        view = java.util.Collections.unmodifiableMap(next);
        byName = Map.copyOf(names);
        originalNames = Map.copyOf(originals);
    }

    /** The NPC id for a name as written in npcs.yml or letters.yml, even after it was renamed; else null. */
    public String idForOriginalName(String name) {
        if (name == null) return null;
        String id = name.toLowerCase(Locale.ROOT);
        if (npcs.containsKey(id)) return id;
        return originalNames.get(simple(name));
    }
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
        int locked = 0;
        for (String id : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(id);
            if (s == null) {
                continue;
            }
            String key = id.toLowerCase(Locale.ROOT);
            if (s.contains("chapter") && settings.lockedChapters.contains(s.getInt("chapter"))) {
                locked++;
                continue; // chapter switched off with /cq chapter: not spawned, not shown, not counted
            }
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
        refresh();
        log.info("Loaded " + npcs.size() + " NPCs" + (locked > 0 ? " (" + locked + " more wait in chapters that are switched off)" : ""));
    }

    public NpcDef get(String id) {
        if (id == null) return null;
        Map<String, NpcDef> current = view;
        NpcDef exact = current.get(id.toLowerCase(Locale.ROOT));
        if (exact != null) return exact;
        return byName.get(id.replaceAll("[^a-zA-Z0-9]", "").toLowerCase(Locale.ROOT));
    }

    public int chapter(String id) { return chapters.getOrDefault(id, 0); }

    public Collection<NpcDef> all() {
        return view.values();
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
