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

    public Settings(FileConfiguration c) {
        serverName = c.getString("server-name", "our server");
        prefix = c.getString("prefix", "<#8fd3ff><bold>QUESTS</bold></#8fd3ff> <dark_gray>»</dark_gray> ");
        countSpawnerMobs = c.getBoolean("quests.count-spawner-mobs", false);
        blockedItems = new HashSet<>();
        for (String item : c.getStringList("rewards.blocked-items")) {
            blockedItems.add(item.toUpperCase(Locale.ROOT));
        }
        if (!c.contains("rewards.blocked-items")) {
            blockedItems.addAll(List.of("ELYTRA", "DRAGON_EGG", "ENCHANTED_GOLDEN_APPLE", "TOTEM_OF_UNDYING", "BEACON", "NETHER_STAR"));
        }
        netheriteMinLevel = c.getInt("rewards.netherite-min-level", 85);
        moneyCommand = c.getString("money-command", "eco give %player% %amount%");
        npcNameFormat = c.getString("npc.name-format", "<white><name></white> <dark_gray>[<gray>Lv <level></gray>]</dark_gray>");
        npcChatFormat = c.getString("npc.chat-format", "<white><bold><name></bold></white> <dark_gray>»</dark_gray> <#e6e6e6><text>");
        npcMentionFormat = c.getString("npc.mention-format", "<blue>Villager <name></blue>");

        lineDelayTicks = Math.max(1, c.getLong("dialogue.line-delay-ticks", 35));
        acceptTimeoutMillis = c.getLong("dialogue.accept-timeout-seconds", 60) * 1000L;

        maxActiveSide = Math.max(1, c.getInt("quests.max-active-side", 3));
        welcomeQuest = c.getString("quests.welcome-quest", "welcome");
        ignorePlacedBlocks = c.getBoolean("quests.ignore-player-placed-blocks", true);
        sideQuestsPerChapter = Math.max(0, c.getInt("quests.side-quests-per-chapter", 10));

        dailyNpc = c.getString("daily.npc", "marigold");
        dailyCooldownMillis = (long) (c.getDouble("daily.cooldown-hours", 24) * 3_600_000L);
        dailyMoney = c.getLong("daily.money", 10_000);

        autoPlace = c.getBoolean("spawning.auto-place-unplaced", true);
        autoPlaceWorld = c.getString("spawning.auto-place-world", "");
        List<Double> ring1 = c.getDoubleList("spawning.act1-ring");
        List<Double> ring2 = c.getDoubleList("spawning.act2-ring");
        act1Min = ring1.size() == 2 ? ring1.get(0) : 5;
        act1Max = ring1.size() == 2 ? ring1.get(1) : 22;
        act2Min = ring2.size() == 2 ? ring2.get(0) : 26;
        act2Max = ring2.size() == 2 ? ring2.get(1) : 40;
        checkSeconds = Math.max(1, c.getLong("spawning.check-seconds", 3));
        lookAtPlayer = c.getBoolean("spawning.look-at-player", true);

        spawnRange = Math.max(16, c.getDouble("spawning.player-range", 100));
        roamMinutes = Math.max(0, c.getLong("spawning.roam-minutes", 20));
        hideFinishedVillagers = c.getBoolean("spawning.hide-finished-villagers", true);
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
        advancementTitle = c.getString("finale.advancement.title", "Finished the Journey");
        advancementDescription = c.getString("finale.advancement.description", "Free the Hollow King and bring the Wanderers home");

        groups = new HashMap<>();
        ConfigurationSection g = c.getConfigurationSection("groups");
        if (g != null) {
            for (String key : g.getKeys(false)) {
                groups.put(key.toUpperCase(Locale.ROOT), g.getStringList(key));
            }
        }
        messages = new HashMap<>();
        ConfigurationSection m = c.getConfigurationSection("messages");
        if (m != null) {
            for (String key : m.getKeys(false)) {
                messages.put(key, m.getString(key, ""));
            }
        }
    }

    public String msg(String key, String fallback) {
        return messages.getOrDefault(key, fallback);
    }
}
