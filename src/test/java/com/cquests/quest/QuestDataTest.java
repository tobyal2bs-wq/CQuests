package com.cquests.quest;

import com.cquests.Settings;
import com.cquests.model.NpcDef;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.model.TargetMatcher;
import com.cquests.npc.NpcRegistry;
import org.bukkit.Material;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.EntityType;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/** Loads the bundled config files the way the plugin does and checks the quest data end to end. */
class QuestDataTest {

    private static final File RESOURCES = new File("src/main/resources");
    private static final List<String> WARNINGS = new ArrayList<>();
    private static Settings settings;
    private static NpcRegistry npcs;
    private static QuestRegistry quests;

    @BeforeAll
    static void load() {
        // Material.isItem() needs a running server's registry; every reward in the files is a plain item anyway.
        QuestRegistry.itemCheck = material -> !material.isLegacy();
        Logger log = Logger.getLogger("CQuestsTest");
        log.setUseParentHandlers(false);
        log.addHandler(new Handler() {
            @Override
            public void publish(LogRecord record) {
                if (record.getLevel().intValue() >= Level.WARNING.intValue()) {
                    WARNINGS.add(record.getMessage());
                }
            }

            @Override
            public void flush() {
            }

            @Override
            public void close() {
            }
        });
        settings = new Settings(YamlConfiguration.loadConfiguration(new File(RESOURCES, "config.yml")),
                YamlConfiguration.loadConfiguration(new File(RESOURCES, "messages.yml")));
        npcs = new NpcRegistry();
        npcs.load(new File(RESOURCES, "npcs.yml"), settings, log);
        quests = new QuestRegistry();
        quests.load(new File(RESOURCES, "quests.yml"), new File(RESOURCES, "generator.yml"), settings, npcs, log);
    }

    @Test
    void npcsAreFoundByIdNameAndOriginalName() {
        assertEquals("bob", npcs.get("B.O.B").id());
        assertEquals("bob", npcs.get("bob").id());
        assertEquals("bob", npcs.idForOriginalName("B.O.B"));
        assertEquals("stephan", npcs.idForOriginalName("Stephan"));
        assertEquals(null, npcs.idForOriginalName("Nobody At All"));
        assertTrue(npcs.all() == npcs.all(), "the NPC list is cached, not rebuilt on every call");
    }

    @Test
    void loadsWithoutWarnings() {
        assertTrue(WARNINGS.isEmpty(), "warnings while loading: " + WARNINGS);
    }

    @Test
    void storyIsOneLinkedChainInFiveChapters() {
        List<Quest> story = quests.story();
        assertEquals(101, story.size());
        assertEquals("welcome", story.get(0).id());
        Set<Integer> chapters = new HashSet<>();
        for (int i = 1; i < story.size(); i++) {
            Quest quest = story.get(i);
            assertEquals(List.of(story.get(i - 1).id()), quest.requires(), quest.id() + " should follow the previous quest");
            assertTrue(quest.chapter() >= story.get(i - 1).chapter(), "chapters only go forward");
            assertNotNull(npcs.get(quest.giver()), quest.id() + " giver");
            assertFalse(quests.chapterName(quest.chapter()).isEmpty(), "chapter " + quest.chapter() + " has a name");
            chapters.add(quest.chapter());
        }
        assertEquals(Set.of(1, 2, 3, 4, 5), chapters);
    }

    @Test
    void fifteenVillagersAtSpawn() {
        long atSpawn = npcs.all().stream().filter(npc -> npc.act() <= 1).count();
        assertEquals(17, atSpawn);
        assertTrue(npcs.all().stream().filter(NpcDef::daily).count() == 1, "one daily villager");
    }

    @Test
    void oneMillionSideQuests() {
        assertEquals(1_080_000L, quests.totalSide());
    }

    @Test
    void sideQuestsAreValidStableAndFast() {
        Random rnd = new Random(7);
        List<NpcDef> givers = npcs.all().stream().filter(npc -> !npc.daily()).toList();
        long start = System.nanoTime();
        int checked = 0;
        Set<String> names = new HashSet<>();
        for (NpcDef npc : givers) {
            for (int n = 0; n < 60; n++) {
                int index = n < 30 ? n + 1 : 1 + rnd.nextInt(quests.sidePerNpc());
                Quest quest = quests.side(npc.id(), index);
                assertNotNull(quest, npc.id() + " #" + index);
                assertEquals(QuestCategory.SIDE, quest.category());
                assertEquals(index, quest.order());
                assertTrue(quest.objectives().size() >= 1 && quest.objectives().size() <= 3, quest.id());
                assertTrue(quest.level() >= npc.level() && quest.level() <= 99, quest.id() + " level " + quest.level());
                assertTrue(quest.reward().money() >= 50, quest.id() + " money");
                for (Objective objective : quest.objectives()) {
                    assertTrue(objective.amount() >= 1, quest.id());
                    if (objective.type() == ObjectiveType.DELIVER) {
                        assertEquals(npc.id(), objective.npc(), "deliveries go to the giver");
                    }
                }
                Quest again = quests.get(quest.id());
                assertNotNull(again, "lookup by id " + quest.id());
                assertEquals(quest.name(), again.name());
                assertEquals(quest.objectives().size(), again.objectives().size());
                names.add(quest.name());
                checked++;
            }
        }
        double millis = (System.nanoTime() - start) / 1e6;
        assertTrue(millis < 5000, "generating " + checked + " quests took " + millis + " ms");
        assertTrue(names.size() > checked / 4, "names should vary: " + names.size() + " unique of " + checked);
        assertEquals(null, quests.side(givers.get(0).id(), quests.sidePerNpc() + 1), "past the end");
    }

    @Test
    void laterSideQuestsAreHarderAndPayMore() {
        NpcDef npc = npcs.get("jerry");
        long early = 0;
        long late = 0;
        for (int i = 1; i <= 200; i++) {
            early += quests.side(npc.id(), i).reward().money();
            late += quests.side(npc.id(), 5000 + i).reward().money();
        }
        assertTrue(late > early, "late quests should pay more on average (" + early + " vs " + late + ")");
    }

    @Test
    void messagesFileIsRead() {
        assertTrue(settings.prefix.contains("QUESTS"));
        assertTrue(settings.npcNameFormat.startsWith("<gold>"), "NPC nameplates use readable gold names");
        assertTrue(settings.npcNameFormat.contains("\n"), "level is on a separate line");
        assertFalse(settings.msg("quest-accepted", "").isEmpty());
        assertFalse(settings.msg("npc-chapter-gate", "").isEmpty());
    }

    @Test
    void rewardsStayFair() {
        Set<String> banned = Set.of("ELYTRA", "DRAGON_EGG", "ENCHANTED_GOLDEN_APPLE", "TOTEM_OF_UNDYING", "BEACON", "NETHER_STAR");
        for (Quest quest : quests.story()) {
            assertTrue(quest.reward().money() <= 10_000, quest.id() + " pays too much");
            quest.reward().items().forEach(item -> {
                assertFalse(banned.contains(item.material().name()), quest.id() + " gives " + item.material());
                if (item.material().name().startsWith("NETHERITE")) {
                    assertTrue(quest.level() >= settings.netheriteMinLevel, quest.id() + " gives netherite too early");
                }
            });
        }
        for (int index = 1; index <= quests.sidePerNpc(); index += 97) {
            Quest side = quests.side("stephan", index);
            assertTrue(side.reward().money() <= 2_000, side.id() + " pays too much");
            side.reward().effects().forEach(effect -> assertTrue(effect.seconds() <= 3600, side.id() + " effect too long"));
        }
    }

    @Test
    void chaptersAreLongAndBobIsABot() {
        int chapterOne = 0;
        for (Quest quest : quests.story()) {
            if (quest.chapter() == 1) {
                chapterOne += quests.story().indexOf(quest) == 0 ? 0 : Math.max(0, quest.sideRequired());
            }
        }
        assertTrue(chapterOne >= 60, "chapter 1 should ask for plenty of side quests, got " + chapterOne);
        Quest bob = quests.get("story_bob");
        assertEquals("Touch Grass", bob.name());
        assertEquals(1000, bob.objectives().get(0).amount());
        assertTrue(npcs.get("bob").title().contains("Discord"));
        assertEquals(3, npcs.all().stream().filter(NpcDef::baby).count(), "three baby villagers");
    }

    @Test
    void everyTargetNamesRealThings() {
        checkTargets(npcs, quests);
    }

    private static List<Quest> sample(NpcRegistry npcs, QuestRegistry quests) {
        List<Quest> sample = new ArrayList<>(quests.story());
        sample.addAll(quests.dailyPool());
        for (NpcDef npc : npcs.all()) {
            for (int i = 1; i <= 40; i++) {
                Quest quest = quests.side(npc.id(), i);
                if (quest != null) {
                    sample.add(quest);
                }
            }
        }
        return sample;
    }

    private static void checkTargets(NpcRegistry npcs, QuestRegistry quests) {
        for (Quest quest : sample(npcs, quests)) {
            for (Objective objective : quest.objectives()) {
                TargetMatcher target = objective.target();
                if (target.any() || objective.type() == ObjectiveType.TALK) {
                    continue;
                }
                boolean entity = switch (objective.type()) {
                    case KILL, BREED, TAME, SHEAR -> true;
                    default -> false;
                };
                boolean found = false;
                if (entity) {
                    for (EntityType type : EntityType.values()) {
                        found |= target.matches(type.name());
                    }
                } else {
                    for (Material material : Material.values()) {
                        found |= !material.isLegacy() && target.matches(material.name());
                    }
                }
                assertTrue(found, quest.id() + ": '" + target.spec() + "' matches no " + (entity ? "entity" : "material"));
            }
        }
    }

    /** Loads the bundled files with every chapter switched on, the way /cq chapter N on does. */
    private static QuestRegistry unlocked(NpcRegistry into, List<String> warnings) {
        Logger log = Logger.getLogger("CQuestsUnlocked");
        log.setUseParentHandlers(false);
        for (Handler h : log.getHandlers()) log.removeHandler(h);
        log.addHandler(new Handler() {
            @Override public void publish(LogRecord record) { if (record.getLevel().intValue() >= Level.WARNING.intValue()) warnings.add(record.getMessage()); }
            @Override public void flush() { }
            @Override public void close() { }
        });
        YamlConfiguration config = YamlConfiguration.loadConfiguration(new File(RESOURCES, "config.yml"));
        config.set("chapters.locked", List.of());
        Settings open = new Settings(config, YamlConfiguration.loadConfiguration(new File(RESOURCES, "messages.yml")));
        assertTrue(open.lockedChapters.isEmpty());
        into.load(new File(RESOURCES, "npcs.yml"), open, log);
        QuestRegistry registry = new QuestRegistry();
        registry.load(new File(RESOURCES, "quests.yml"), new File(RESOURCES, "generator.yml"), open, into, log);
        return registry;
    }

    @Test
    void chaptersSixToTenStartLocked() {
        assertEquals(Set.of(6, 7, 8, 9, 10), settings.lockedChapters);
        assertTrue(quests.story().stream().noneMatch(q -> q.chapter() > 5));
        assertEquals(null, npcs.get("garrick"), "chapter 6 villagers do not exist while locked");
        assertEquals("The Iron Tusk", quests.chapterName(6), "names stay known for /cq chapter");
    }

    @Test
    void chaptersSixToTenLoadCleanlyWhenSwitchedOn() {
        List<String> warnings = new ArrayList<>();
        NpcRegistry all = new NpcRegistry();
        QuestRegistry open = unlocked(all, warnings);
        assertEquals(List.of(), warnings);
        List<Quest> story = open.story();
        assertEquals(151, story.size());
        Set<Integer> chapters = new HashSet<>();
        for (int i = 1; i < story.size(); i++) {
            Quest quest = story.get(i);
            chapters.add(quest.chapter());
            assertEquals(List.of(story.get(i - 1).id()), quest.requires(), quest.id() + " should follow the previous quest");
            assertTrue(quest.chapter() >= story.get(i - 1).chapter());
        }
        assertEquals(Set.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), chapters);
        for (String boss : List.of("story_garrick", "story_brine", "story_emberly", "story_mortimer", "story_aldis_elder")) {
            Quest quest = open.get(boss);
            assertNotNull(quest, boss);
            assertTrue(open.endsChapter(quest) || open.nextStory(quest) == null, boss + " ends its chapter");
            assertEquals(ObjectiveType.KILL, quest.objectives().get(0).type());
            assertNotNull(all.get(quest.giver()), boss + " giver exists");
        }
        checkTargets(all, open);
    }

    @Test
    void noQuestAsksForWheat() {
        List<String> warnings = new ArrayList<>();
        NpcRegistry all = new NpcRegistry();
        QuestRegistry open = unlocked(all, warnings);
        for (Quest quest : sample(all, open)) {
            for (Objective objective : quest.objectives()) {
                if (objective.target().any()) continue;
                assertFalse(objective.target().matches("WHEAT") || objective.target().matches("HAY_BLOCK"),
                        quest.id() + " asks for wheat: " + objective.target().spec());
            }
        }
    }

    @Test
    void everyBossBelongsToARealQuest() {
        List<String> warnings = new ArrayList<>();
        NpcRegistry all = new NpcRegistry();
        QuestRegistry open = unlocked(all, warnings);
        YamlConfiguration bosses = YamlConfiguration.loadConfiguration(new File(RESOURCES, "bosses.yml"));
        var section = bosses.getConfigurationSection("bosses");
        assertNotNull(section);
        for (String id : section.getKeys(false)) {
            Quest quest = open.get(id);
            assertNotNull(quest, "bosses.yml: " + id + " is not a quest");
            assertEquals(quest.giver(), section.getString(id + ".giver"), id + " giver");
            EntityType type = EntityType.valueOf(section.getString(id + ".entity"));
            assertTrue(type.isAlive(), id);
        }
    }
}
