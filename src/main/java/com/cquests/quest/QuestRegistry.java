package com.cquests.quest;

import com.cquests.Settings;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.model.Reward;
import com.cquests.model.RewardItem;
import com.cquests.model.TargetMatcher;
import com.cquests.npc.NpcRegistry;
import com.cquests.util.Text;
import org.bukkit.Material;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.logging.Logger;

/** Holds every quest: hand-written ones from quests.yml plus the ones built by {@link QuestGenerator}. */
public final class QuestRegistry {

    private final Map<String, Quest> byId = new LinkedHashMap<>();
    private final List<Quest> story = new ArrayList<>();
    private final Map<String, List<Quest>> sideByGiver = new HashMap<>();
    private final Map<String, List<Quest>> storyByGiver = new HashMap<>();
    private final List<Quest> dailyPool = new ArrayList<>();

    public void load(File questsFile, File generatorFile, Settings settings, NpcRegistry npcs, Logger log) {
        byId.clear();
        story.clear();
        sideByGiver.clear();
        storyByGiver.clear();
        dailyPool.clear();

        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(questsFile);
        ConfigurationSection root = yaml.getConfigurationSection("quests");
        int order = 0;
        if (root != null) {
            for (String id : root.getKeys(false)) {
                ConfigurationSection s = root.getConfigurationSection(id);
                if (s == null) {
                    continue;
                }
                try {
                    add(parse(id.toLowerCase(Locale.ROOT), s, order++, settings, npcs));
                } catch (IllegalArgumentException e) {
                    log.warning("Skipping quest '" + id + "': " + e.getMessage());
                }
            }
        }
        int handWritten = byId.size();

        YamlConfiguration gen = YamlConfiguration.loadConfiguration(generatorFile);
        if (gen.getBoolean("enabled", true)) {
            QuestGenerator generator = new QuestGenerator(gen, settings, npcs, log);
            for (Quest quest : generator.generate(this)) {
                if (!byId.containsKey(quest.id())) {
                    add(quest);
                }
            }
        }

        story.sort(Comparator.comparingInt(Quest::order));
        sideByGiver.values().forEach(list -> list.sort(Comparator.comparingInt(Quest::order)));
        storyByGiver.values().forEach(list -> list.sort(Comparator.comparingInt(Quest::order)));
        log.info("Loaded " + byId.size() + " quests (" + handWritten + " from quests.yml, "
                + (byId.size() - handWritten) + " generated; " + story.size() + " story, "
                + dailyPool.size() + " daily)");
    }

    private void add(Quest quest) {
        byId.put(quest.id(), quest);
        switch (quest.category()) {
            case STORY -> {
                story.add(quest);
                if (!quest.giver().isEmpty()) {
                    storyByGiver.computeIfAbsent(quest.giver(), k -> new ArrayList<>()).add(quest);
                }
            }
            case SIDE -> sideByGiver.computeIfAbsent(quest.giver(), k -> new ArrayList<>()).add(quest);
            case DAILY -> dailyPool.add(quest);
        }
    }

    private Quest parse(String id, ConfigurationSection s, int order, Settings settings, NpcRegistry npcs) {
        String giver = s.getString("giver", "").toLowerCase(Locale.ROOT);
        List<Objective> objectives = new ArrayList<>();
        for (String line : s.getStringList("objectives")) {
            objectives.add(parseObjective(line, giver, settings.groups));
        }
        if (objectives.isEmpty()) {
            throw new IllegalArgumentException("no objectives");
        }
        for (Objective objective : objectives) {
            if (!objective.npc().isEmpty() && npcs.get(objective.npc()) == null) {
                throw new IllegalArgumentException("unknown NPC '" + objective.npc() + "'");
            }
        }
        String turnIn;
        if (s.contains("turn-in")) {
            turnIn = s.getString("turn-in", "").toLowerCase(Locale.ROOT);
        } else {
            Objective last = objectives.get(objectives.size() - 1);
            turnIn = last.type() == ObjectiveType.TALK ? last.npc() : giver;
        }
        QuestCategory category = QuestCategory.valueOf(s.getString("category", "STORY").toUpperCase(Locale.ROOT));
        return new Quest(
                id,
                s.getString("name", id).replace("{server}", settings.serverName),
                s.getInt("level", 0),
                category,
                s.getInt("order", order),
                giver,
                turnIn,
                s.getStringList("requires").stream().map(r -> r.toLowerCase(Locale.ROOT)).toList(),
                List.copyOf(objectives),
                s.getString("description", null),
                s.getStringList("offer"),
                s.getStringList("complete"),
                parseReward(s.getConfigurationSection("rewards")));
    }

    /**
     * Parses objective lines:
     * <pre>
     * KILL WOLF 3 wolves
     * MINE COAL_ORE|DEEPSLATE_COAL_ORE 16 coal ore
     * DELIVER WHEAT 16 to:martha wheat     (to: defaults to the quest giver)
     * TALK jerry
     * </pre>
     */
    public static Objective parseObjective(String line, String giver, Map<String, List<String>> groups) {
        String[] parts = line.trim().split("\\s+");
        if (parts.length < 2) {
            throw new IllegalArgumentException("bad objective '" + line + "'");
        }
        ObjectiveType type;
        try {
            type = ObjectiveType.valueOf(parts[0].toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("unknown objective type '" + parts[0] + "'");
        }
        if (type == ObjectiveType.TALK) {
            return new Objective(type, TargetMatcher.ANY, 1, parts[1].toLowerCase(Locale.ROOT), "");
        }
        if (parts.length < 3) {
            throw new IllegalArgumentException("objective '" + line + "' needs an amount");
        }
        TargetMatcher target = TargetMatcher.parse(parts[1], groups);
        int amount;
        try {
            amount = Math.max(1, Integer.parseInt(parts[2]));
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("bad amount in '" + line + "'");
        }
        String npc = type == ObjectiveType.DELIVER ? giver : "";
        StringBuilder label = new StringBuilder();
        for (int i = 3; i < parts.length; i++) {
            if (parts[i].toLowerCase(Locale.ROOT).startsWith("to:")) {
                npc = parts[i].substring(3).toLowerCase(Locale.ROOT);
                continue;
            }
            if (!label.isEmpty()) {
                label.append(' ');
            }
            label.append(parts[i]);
        }
        if (label.isEmpty()) {
            label.append(defaultLabel(target, amount));
        }
        if (type == ObjectiveType.DELIVER && npc.isEmpty()) {
            throw new IllegalArgumentException("DELIVER objective '" + line + "' has no NPC to deliver to");
        }
        return new Objective(type, target, amount, npc, label.toString());
    }

    private static String defaultLabel(TargetMatcher target, int amount) {
        if (target.any()) {
            return amount == 1 ? "thing" : "things";
        }
        String first = target.spec().split("\\|")[0].replace("*", "").replace("@", "");
        String singular = Text.pretty(first).trim();
        return amount == 1 ? singular : Text.plural(singular);
    }

    static Reward parseReward(ConfigurationSection s) {
        if (s == null) {
            return Reward.NONE;
        }
        List<RewardItem> items = new ArrayList<>();
        for (String line : s.getStringList("items")) {
            RewardItem item = parseItem(line);
            if (item != null) {
                items.add(item);
            }
        }
        return new Reward(s.getLong("money", 0), List.copyOf(items), s.getStringList("commands"), s.getInt("xp", 0));
    }

    /** "DIAMOND 3" -> 3 diamonds. */
    static RewardItem parseItem(String line) {
        String[] parts = line.trim().split("\\s+");
        Material material = Material.matchMaterial(parts[0]);
        if (material == null || !material.isItem()) {
            return null;
        }
        int amount = 1;
        if (parts.length > 1) {
            try {
                amount = Math.max(1, Integer.parseInt(parts[1]));
            } catch (NumberFormatException ignored) {
                // keep 1
            }
        }
        return new RewardItem(material, amount);
    }

    public Quest get(String id) {
        return id == null ? null : byId.get(id.toLowerCase(Locale.ROOT));
    }

    public Collection<Quest> all() {
        return byId.values();
    }

    public List<Quest> story() {
        return story;
    }

    public List<Quest> storyFrom(String npcId) {
        return storyByGiver.getOrDefault(npcId, List.of());
    }

    public List<Quest> sideFrom(String npcId) {
        return sideByGiver.getOrDefault(npcId, List.of());
    }

    public List<Quest> dailyPool() {
        return dailyPool;
    }

    public int sideCount() {
        int total = 0;
        for (List<Quest> list : sideByGiver.values()) {
            total += list.size();
        }
        return total;
    }
}
