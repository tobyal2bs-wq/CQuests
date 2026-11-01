package com.cquests.quest;

import com.cquests.CQuestsPlugin;
import com.cquests.Settings;
import com.cquests.data.PlayerData;
import com.cquests.npc.NpcRegistry;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import java.io.File;
import java.util.UUID;
import java.util.logging.Logger;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class ProgressionTest {
    private final File resources = new File("src/main/resources");
    private final Settings settings = new Settings(YamlConfiguration.loadConfiguration(new File(resources, "config.yml")));
    private final NpcRegistry npcs = new NpcRegistry();
    private final QuestRegistry quests = new QuestRegistry();
    private final QuestManager manager;
    private final CQuestsPlugin plugin;

    ProgressionTest() {
        QuestRegistry.itemCheck = m -> !m.isLegacy();
        Logger log = Logger.getLogger("progression-test");
        npcs.load(new File(resources, "npcs.yml"), settings, log);
        quests.load(new File(resources, "quests.yml"), new File(resources, "generator.yml"), settings, npcs, log);
        plugin = mock(CQuestsPlugin.class);
        when(plugin.settings()).thenReturn(settings);
        when(plugin.npcs()).thenReturn(npcs);
        when(plugin.quests()).thenReturn(quests);
        manager = new QuestManager(plugin);
    }

    @Test void requiredCustomLevelAndPreviousTaskBothGateStory(@org.junit.jupiter.api.io.TempDir File folder) {
        when(plugin.getDataFolder()).thenReturn(folder);
        var progression=new com.cquests.progression.Progression(plugin);
        when(plugin.progression()).thenReturn(progression);
        var quest=quests.get("story_steve");PlayerData data=new PlayerData(UUID.randomUUID());
        assertFalse(manager.requirementsMet(data,quest));
        data.complete("story_jerry",true);assertFalse(manager.requirementsMet(data,quest));
        data.addSkillXp(progression.curve().threshold(quest.level()));assertTrue(manager.requirementsMet(data,quest));
        data.uncomplete("story_jerry");assertFalse(manager.requirementsMet(data,quest));
    }

    @Test void futureChapterVillagersStayHiddenEvenIfMetButSharedNpcsAreVisible() {
        PlayerData data = new PlayerData(UUID.randomUUID());
        var future = npcs.get("astra");
        data.meet(future.id());
        assertFalse(manager.shouldSee(data, future));
        assertTrue(manager.shouldSee(data, npcs.get("stephan")));
        assertTrue(manager.shouldSee(data, npcs.get("marigold")));
        for (var quest : quests.story()) {
            if (quest.chapter() < 5) data.complete(quest.id(), true);
        }
        assertTrue(manager.shouldSee(data, future));
        assertTrue(manager.shouldSee(data, npcs.get("bob")));
    }

    @Test void storyQuotasAreOptionalAndOldQuestIdsStillResolve() {
        assertFalse(settings.sideGatesEnabled);
        assertFalse(settings.trackerDefault);
        assertFalse(settings.directionsDefault);
        PlayerData data = new PlayerData(UUID.randomUUID());
        for (var quest : quests.story()) {
            assertEquals(0, manager.sideRequired(quest));
            assertNull(manager.chapterGate(data, quest));
        }
        assertNotNull(quests.get("side_bob_17"));
        assertEquals("bob", npcs.get("B.O.B").id());
        assertEquals("B.O.B", npcs.get("BOB").name());
        assertNotNull(quests.side("luma", 1));
        assertEquals(5, quests.firstChapter("astra"));
    }
}
