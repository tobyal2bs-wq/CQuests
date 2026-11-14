package com.cquests;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/** Typed view of config.yml. */
public final class Settings {

    public final String serverName;
    public final String prefix;
    public final boolean countSpawnerMobs;
    public final Set<String> blockedItems;
    public final int netheriteMinLevel;
    public final String moneyCommand;
    public final String npcNameFormat;
    public final String npcChatFormat;
    public final String npcMentionFormat;

    public final long lineDelayTicks;
    public final long acceptTimeoutMillis;

    public final int maxActiveSide;
    public final String welcomeQuest;
    public final boolean ignorePlacedBlocks;
    public final int sideQuestsPerChapter;

    public final String dailyNpc;
    public final int dailyMinLevel;
    public final Map<Integer,Integer> chapterLevels;
    /** Chapter 1 (the villagers at spawn) needs no level. */
    public final boolean starterFree;
    /** Chapters switched off with /cq chapter: their villagers and story quests are not loaded at all. */
    public final Set<Integer> lockedChapters;
    public final Set<String> spawnNpcIds;
    public final long dailyCooldownMillis;
    public final long dailyMoney;

    public final boolean autoPlace;
    public final String autoPlaceWorld;
    public final double act1Min;
    public final double act1Max;
    public final double act2Min;
    public final double act2Max;
    public final long checkSeconds;
    public final boolean lookAtPlayer;

    public final double spawnRange;
    public final long roamMinutes;
    public final boolean trackerEnabled;
    public final boolean trackerDefault;
    public final boolean directionsDefault;
    public final boolean sideGatesEnabled;
    public final String defaultMenu;
    public final boolean backupsEnabled;
    public final long backupEveryHours;
    public final int backupKeep;
    public final boolean hideFinishedVillagers;
    public final double shieldRadius;
    public final boolean shieldBuild;
    public final boolean shieldPvp;

    public final String bookTitle;
    public final String bookAuthor;
    public final int indexPerPage;
    public final int barLength;

    public final boolean celebrateBigQuests;
    public final boolean finaleEnabled;
    public final int finaleSceneTicks;
    public final int finaleMaxScenes;
    public final String advancementTitle;
    public final String advancementDescription;

    public final Map<String, List<String>> groups;
    private final Map<String, String> messages;

    /** Reads settings and messages from one file (old layout, and the tests). */
    public Settings(FileConfiguration c) {
        this(c, c);
    }

    /**
     * @param c config.yml
     * @param m messages.yml. Its groups only organise the file: every message is looked up by its own key.
     */
    public Settings(FileConfiguration c, ConfigurationSection m) {
        serverName = c.getString("server-name", "our server");
        dailyMinLevel=Math.max(1,c.getInt("progression.daily-min-level",10));
        starterFree=c.getBoolean("progression.starter-chapter-free",true);
        var levels=new HashMap<Integer,Integer>();
        for(int chapter=1;chapter<=5;chapter++)levels.put(chapter,Math.max(0,c.getInt("progression.chapter-levels."+chapter,chapter==1?0:(chapter-1)*100)));
        // Chapters 6 to 10 sit between level 420 and the 500 cap unless config.yml says otherwise.
        for(int chapter=6;chapter<=10;chapter++)levels.put(chapter,Math.max(0,c.getInt("progression.chapter-levels."+chapter,Math.min(500,400+(chapter-5)*20))));
        var extra=c.getConfigurationSection("progression.chapter-levels");
        if(extra!=null)for(String key:extra.getKeys(false))try{levels.put(Integer.parseInt(key),Math.max(0,extra.getInt(key)));}catch(NumberFormatException ignored){}
        chapterLevels=Map.copyOf(levels);
        var locked=new HashSet<Integer>();
        for(Object value:c.getList("chapters.locked",List.of(6,7,8,9,10)))try{locked.add(Integer.parseInt(String.valueOf(value).trim()));}catch(NumberFormatException ignored){}
        locked.remove(1);
        lockedChapters=Set.copyOf(locked);
        var spawn=new HashSet<>(c.getStringList("spawning.camp-npcs"));
        if(spawn.isEmpty())spawn.addAll(List.of("stephan","jerry","rosie","copper_jack","luma"));
        spawn.add("bob");spawnNpcIds=Set.copyOf(spawn);
        prefix = m.getString("prefix", c.getString("prefix", "<#8fd3ff><bold>QUESTS</bold></#8fd3ff> <dark_gray>»</dark_gray> "));
        countSpawnerMobs = c.getBoolean("quests.count-spawner-mobs", false);
        blockedItems = new HashSet<>();
        for (String item : c.getStringList("rewards.blocked-items")) {
            blockedItems.add(item.toUpperCase(Locale.ROOT));
        }
        if (!c.contains("rewards.blocked-items")) {
            blockedItems.addAll(List.of("ELYTRA", "DRAGON_EGG", "ENCHANTED_GOLDEN_APPLE", "TOTEM_OF_UNDYING", "BEACON", "NETHER_STAR"));
        }
        netheriteMinLevel = c.getInt("rewards.netherite-min-level", 85);
        moneyCommand = c.getString("money-command", "economy give %player% %amount%");
        String nameFormat=m.getString("formats.npc-name",c.getString("npc.name-format",com.cquests.npc.NpcNameplates.FORMAT));
        npcNameFormat=com.cquests.npc.NpcNameplates.LEGACY.equals(nameFormat)?com.cquests.npc.NpcNameplates.FORMAT:nameFormat;
        npcChatFormat = m.getString("formats.npc-chat", c.getString("npc.chat-format", "<white><bold><name></bold></white> <dark_gray>»</dark_gray> <#e6e6e6><text>"));
        npcMentionFormat = m.getString("formats.npc-mention", c.getString("npc.mention-format", "<blue>Villager <name></blue>"));

        lineDelayTicks = Math.max(1, c.getLong("dialogue.line-delay-ticks", 35));
        acceptTimeoutMillis = c.getLong("dialogue.accept-timeout-seconds", 60) * 1000L;

        maxActiveSide = Math.max(1, c.getInt("quests.max-active-side", 3));
        welcomeQuest = c.getString("quests.welcome-quest", "welcome");
        ignorePlacedBlocks = c.getBoolean("quests.ignore-player-placed-blocks", true);
        sideQuestsPerChapter = Math.max(0, c.getInt("quests.side-quests-per-chapter", 0));
        sideGatesEnabled = c.getBoolean("quests.require-side-quests", false);
        defaultMenu = c.getString("dialogue.default-mode", "book");

        dailyNpc = c.getString("daily.npc", "marigold");
        dailyCooldownMillis = (long) (c.getDouble("daily.cooldown-hours", 24) * 3_600_000L);
        dailyMoney = c.getLong("daily.money", 10_000);

        autoPlace = c.getBoolean("spawning.auto-place-unplaced", true);
        autoPlaceWorld = c.getString("spawning.auto-place-world", "");
        List<Double> ring1 = c.getDoubleList("spawning.act1-ring");
        List<Double> ring2 = c.getDoubleList("spawning.act2-ring");
        act1Min = ring1.size() == 2 ? ring1.get(0) : 5;
        act1Max = ring1.size() == 2 ? ring1.get(1) : 60;
        act2Min = ring2.size() == 2 ? ring2.get(0) : 26;
        act2Max = ring2.size() == 2 ? ring2.get(1) : 300;
        checkSeconds = Math.max(1, c.getLong("spawning.check-seconds", 3));
        lookAtPlayer = c.getBoolean("spawning.look-at-player", true);

        spawnRange = Math.max(16, c.getDouble("spawning.player-range", 100));
        roamMinutes = Math.max(0, c.getLong("spawning.roam-minutes", 0));
        trackerEnabled = c.getBoolean("tracker.enabled", true);
        trackerDefault = c.getBoolean("tracker.default-on", false);
        directionsDefault = c.getBoolean("directions.default-on", true);
        backupsEnabled = c.getBoolean("backups.enabled", true);
        backupEveryHours = Math.max(1, c.getLong("backups.every-hours", 6));
        backupKeep = Math.max(1, c.getInt("backups.keep", 28));
        hideFinishedVillagers = c.getBoolean("spawning.hide-finished-villagers", false);
        shieldRadius = Math.max(0, c.getDouble("shield.radius", 6));
        shieldBuild = c.getBoolean("shield.block-building", true);
        shieldPvp = c.getBoolean("shield.block-pvp", true);

        bookTitle = c.getString("book.title", "Quest Journal");
        bookAuthor = c.getString("book.author", "The Wanderers");
        indexPerPage = Math.max(3, c.getInt("book.quests-per-index-page", 8));
        barLength = Math.max(5, c.getInt("book.progress-bar-length", 18));

        celebrateBigQuests = c.getBoolean("celebrations.big-quests", true);
        finaleEnabled = c.getBoolean("finale.enabled", true);
        finaleSceneTicks = (int) Math.max(40, c.getDouble("finale.scene-seconds", 4) * 20);
        finaleMaxScenes = Math.max(1, c.getInt("finale.max-scenes", 12));
        advancementTitle = m.getString("achievements.journey-title", c.getString("finale.advancement.title", "Finished the Journey"));
        advancementDescription = m.getString("achievements.journey-description",
                c.getString("finale.advancement.description", "Free the Hollow King and bring the Wanderers home"));

        groups = new HashMap<>();
        ConfigurationSection g = c.getConfigurationSection("groups");
        if (g != null) {
            for (String key : g.getKeys(false)) {
                groups.put(key.toUpperCase(Locale.ROOT), g.getStringList(key));
            }
        }
        messages = new HashMap<>();
        ConfigurationSection old = c.getConfigurationSection("messages");
        if (old != null) {
            for (String key : old.getKeys(false)) {
                messages.put(key, old.getString(key, ""));
            }
        }
        for (String path : m.getKeys(true)) {
            if (m.isString(path) && path.contains(".") && !path.startsWith("formats.") && !path.startsWith("messages.")) {
                messages.put(path.substring(path.lastIndexOf('.') + 1), m.getString(path, ""));
            }
        }
    }

    /** Every message key and its text, for /cq test messages. */
    public Map<String, String> messages() {
        return java.util.Collections.unmodifiableMap(messages);
    }

    public String msg(String key, String fallback) {
        return messages.getOrDefault(key, fallback);
    }
}
