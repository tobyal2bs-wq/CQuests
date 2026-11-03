package com.cquests.quest;

import com.cquests.Settings;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.model.Reward;
import com.cquests.model.RewardEffect;
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
import java.util.function.Predicate;
import java.util.logging.Logger;

/**
 * Holds every quest: story quests from quests.yml, the daily pool, and side quests that
 * {@link QuestGenerator} builds on demand (kept in a small cache).
 */
public final class QuestRegistry {

    /** Whether a material can be given as an item. Swapped out in tests, where there is no server registry. */
    static Predicate<Material> itemCheck = Material::isItem;

    private final Map<String, Quest> byId = new LinkedHashMap<>();
    private final List<Quest> story = new ArrayList<>();
    private final Map<String, Quest> sideCache = new LinkedHashMap<>(1024, 0.75f, true) {
        @Override
        protected boolean removeEldestEntry(Map.Entry<String, Quest> eldest) {
            return size() > 20_000;
        }
    };
    private QuestGenerator generator;
    private volatile int generation;
    private NpcRegistry npcs;
    private final Map<String, List<Quest>> storyByGiver = new HashMap<>();
    private final List<Quest> dailyPool = new ArrayList<>();
    private final Map<Integer, String> chapterNames = new HashMap<>();
    private YamlConfiguration twists;

    public void load(File questsFile, File generatorFile, Settings settings, NpcRegistry npcs, Logger log) {
        byId.clear();
        story.clear();
        synchronized (sideCache) {
            sideCache.clear();
        }
        generator = null;
        this.npcs = npcs;
        storyByGiver.clear();
        dailyPool.clear();
        together.clear();

        generation++;
        chapterNames.clear();
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(questsFile);
        twists=YamlConfiguration.loadConfiguration(new File(questsFile.getParentFile(),"twists.yml"));
        ConfigurationSection chapters = yaml.getConfigurationSection("chapters");
        if (chapters != null) {
            for (String key : chapters.getKeys(false)) {
                try {
                    chapterNames.put(Integer.parseInt(key), chapters.getString(key, ""));
                } catch (NumberFormatException e) {
                    log.warning("quests.yml: chapter keys must be numbers, got '" + key + "'");
                }
            }
        }
        ConfigurationSection root = yaml.getConfigurationSection("quests");
        int order = 0;
        String previousStory = null;
        if (root != null) {
            for (String id : root.getKeys(false)) {
                ConfigurationSection s = root.getConfigurationSection(id);
                if (s == null) {
                    continue;
                }
                if (s.getString("category", "STORY").equalsIgnoreCase("STORY")
                        && settings.lockedChapters.contains(Math.max(1, s.getInt("chapter", 1)))) {
                    order++;
                    continue; // chapter switched off with /cq chapter
                }
                try {
                    Quest quest = parse(id.toLowerCase(Locale.ROOT), s, order++, previousStory, settings, npcs, log);
                    add(quest);
                    int party = Math.max(1, Math.min(4, s.getInt("together", 1)));
                    if (party > 1) together.put(quest.id(), party);
                    if (quest.category() == QuestCategory.STORY) {
                        previousStory = quest.id();
                    }
                } catch (IllegalArgumentException e) {
                    log.warning("Skipping quest '" + id + "': " + e.getMessage());
                }
            }
        }

        YamlConfiguration gen = YamlConfiguration.loadConfiguration(generatorFile);
        if (gen.getBoolean("enabled", true)) {
            generator = new QuestGenerator(gen, settings, npcs, log);
            for (Quest quest : generator.dailyPool()) {
                if (!byId.containsKey(quest.id())) {
                    add(quest);
                }
            }
        }

        story.sort(Comparator.comparingInt(Quest::order));
        storyByGiver.values().forEach(list -> list.sort(Comparator.comparingInt(Quest::order)));
        log.info("Loaded " + story.size() + " story quests, " + dailyPool.size() + " daily quests and "
                + totalSide() + " side quests (" + sidePerNpc() + " per story NPC, generated on demand)");
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
            case SIDE -> {
                // Hand-written side quests are not supported; side quests come from generator.yml.
            }
            case DAILY -> dailyPool.add(quest);
        }
    }

    /**
     * @param previousStory the story quest above this one in the file; a story quest without
     *                      "requires" follows it, so new chapters can simply be appended
     */
    private Quest parse(String id, ConfigurationSection s, int order, String previousStory, Settings settings,
                        NpcRegistry npcs, Logger log) {
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
        List<String> requires;
        if (s.contains("requires")) {
            requires = s.getStringList("requires").stream().map(r -> r.toLowerCase(Locale.ROOT)).toList();
        } else {
            requires = category == QuestCategory.STORY && previousStory != null ? List.of(previousStory) : List.of();
        }
        int level = s.getInt("level", 0);
        int chapter=category==QuestCategory.STORY?Math.max(1,s.getInt("chapter",1)):0;
        int requiredLevel=category==QuestCategory.STORY?Math.max(level,settings.chapterLevels.getOrDefault(chapter,0))
                :category==QuestCategory.DAILY?settings.dailyMinLevel:level;
        return new Quest(
                id,
                s.getString("name", id).replace("{server}", settings.serverName),
                requiredLevel,
                category,
                s.getInt("order", order),
                giver,
                turnIn,
                requires,
                List.copyOf(objectives),
                s.getString("description", null),
                twistLines(id,"offer-append",s.getStringList("offer"),false),
                twistLines(id,"complete-prepend",s.getStringList("complete"),true),
                parseReward(id, s.getConfigurationSection("rewards"), level, settings, log),
                s.getBoolean("big", false),
                chapter,
                s.getInt("side-required", -1));
    }
    private List<String> twistLines(String id,String key,List<String> original,boolean prepend){
        if(twists==null||!twists.getBoolean("enabled",true))return original;
        List<String> extra=twists.getStringList("quests."+id+"."+key);List<String> result=new ArrayList<>();
        if(prepend)result.addAll(extra);result.addAll(original);if(!prepend)result.addAll(extra);return List.copyOf(result);
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

    static Reward parseReward(String questId, ConfigurationSection s, int level, Settings settings, Logger log) {
        if (s == null) {
            return Reward.NONE;
        }
        List<RewardItem> items = new ArrayList<>();
        for (String line : s.getStringList("items")) {
            RewardItem item = parseItem(line);
            if (item == null) {
                log.warning("Quest '" + questId + "': unknown reward item '" + line + "'");
            } else if (!allowedItem(item, level, settings)) {
                log.warning("Quest '" + questId + "': reward " + item.material() + " is not allowed at level " + level
                        + " (see rewards.blocked-items and rewards.netherite-min-level)");
            } else {
                items.add(item);
            }
        }
        List<RewardEffect> effects = new ArrayList<>();
        for (String line : s.getStringList("effects")) {
            RewardEffect effect = parseEffect(line);
            if (effect == null) {
                log.warning("Quest '" + questId + "': bad effect '" + line + "' (use NAME SECONDS [LEVEL], e.g. SPEED 3600 1)");
            } else {
                effects.add(effect);
            }
        }
        return new Reward(s.getLong("money", 0), List.copyOf(items), List.copyOf(effects), s.getStringList("commands"), s.getInt("xp", 0));
    }

    /** Keeps rewards fair: blocked items never, netherite only for hard quests. */
    static boolean allowedItem(RewardItem item, int level, Settings settings) {
        String name = item.material().name();
        if (settings.blockedItems.contains(name)) {
            return false;
        }
        return !name.startsWith("NETHERITE") || level >= settings.netheriteMinLevel;
    }

    /** "SPEED 3600 1" -> Speed I for an hour. The level is 1-based like in game; 0 or missing means I. */
    static RewardEffect parseEffect(String line) {
        String[] parts = line.trim().split("\\s+");
        if (parts.length < 2) {
            return null;
        }
        try {
            int seconds = Integer.parseInt(parts[1]);
            int level = parts.length > 2 ? Integer.parseInt(parts[2]) : 1;
            return seconds <= 0 ? null : new RewardEffect(parts[0].toLowerCase(Locale.ROOT), seconds, Math.max(0, level - 1));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    /** "DIAMOND 3" -> 3 diamonds. */
    static RewardItem parseItem(String line) {
        String[] parts = line.trim().split("\\s+");
        Material material = Material.matchMaterial(parts[0]);
        if (material == null || !itemCheck.test(material)) {
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
        if (id == null) {
            return null;
        }
        String key = id.toLowerCase(Locale.ROOT);
        Quest quest = byId.get(key);
        if (quest != null || !key.startsWith("side_")) {
            return quest;
        }
        int split = key.lastIndexOf('_');
        if (split <= 5) {
            return null;
        }
        try {
            return side(key.substring(5, split), Integer.parseInt(key.substring(split + 1)));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    /** Side quest {@code index} (1-based) of an NPC, or null if out of range or the NPC has no story quest. */
    public Quest side(String npcId, int index) {
        if (generator == null || index < 1 || index > generator.perNpc()) {
            return null;
        }
        List<Quest> storyQuests = storyFrom(npcId);
        NpcDef npc = npcs.get(npcId);
        if (npc == null || npc.daily() || (storyQuests.isEmpty() && npcs.chapter(npc.id()) == 0)) {
            return null;
        }
        String id = "side_" + npc.id() + "_" + index;
        synchronized (sideCache) {
            Quest cached = sideCache.get(id);
            if (cached != null) {
                return cached;
            }
        }
        Quest quest = generator.side(npc, index, storyQuests.stream().map(Quest::id).toList());
        if (quest != null) {
            synchronized (sideCache) {
                sideCache.put(id, quest);
            }
        }
        return quest;
    }

    public int sidePerNpc() {
        return generator == null ? 0 : generator.perNpc();
    }

    public long totalSide() {
        return (long) sidePerNpc() * npcs.all().stream()
                .filter(npc -> !npc.daily() && (!storyFrom(npc.id()).isEmpty() || npcs.chapter(npc.id()) > 0)).count();
    }

    /** Earliest story involvement; shared NPCs become visible from their first chapter onward. */
    public int firstChapter(String npcId) {
        int storyChapter = story.stream().filter(q -> q.involves(npcId)).mapToInt(Quest::chapter).min().orElse(Integer.MAX_VALUE);
        int configured = npcs.chapter(npcId);
        int result = configured > 0 ? Math.min(configured, storyChapter) : storyChapter;
        return result == Integer.MAX_VALUE ? 1 : result;
    }

    /** Bumped on every load, so cached quest objects from an older load are ignored. */
    public int generation() {
        return generation;
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

    private final Map<String, Integer> together = new java.util.concurrent.ConcurrentHashMap<>();

    /** Players needed at the same time for a co-op quest (quests.yml "together: 2" to 4); 1 for normal quests. */
    public int together(String questId) {
        return together.getOrDefault(questId, 1);
    }

    public List<Quest> dailyPool() {
        return dailyPool;
    }

    /** Every chapter named in quests.yml, including chapters that are switched off. */
    public java.util.SortedMap<Integer, String> chapterNames() {
        return new java.util.TreeMap<>(chapterNames);
    }

    public String chapterName(int chapter) {
        return chapterNames.getOrDefault(chapter, "");
    }

    /** The story quest after this one, or null for the last. */
    public Quest nextStory(Quest quest) {
        int index = story.indexOf(quest);
        return index < 0 || index + 1 >= story.size() ? null : story.get(index + 1);
    }

    /** True for the last quest of a chapter (the next story quest starts a new chapter). */
    public boolean endsChapter(Quest quest) {
        if (quest.category() != QuestCategory.STORY) {
            return false;
        }
        Quest next = nextStory(quest);
        return next != null && next.chapter() != quest.chapter();
    }
}
