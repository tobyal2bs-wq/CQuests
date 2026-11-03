package com.cquests.data;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.nio.file.Files;
import java.util.UUID;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PlayerStoreTest {
    @Test void mailAndSpentTokensSurviveRestartWithoutReissuingCurrency(@TempDir File folder){
        var store=new PlayerStore(folder,Logger.getLogger("mail-test"));UUID id=UUID.randomUUID();var data=store.get(id);
        data.addWheat(2250);assertTrue(data.spendSunflowers(2));assertTrue(data.readLetter("flora_first"));data.setHoeTier(3);data.addSkillXp(1234);
        store.saveAllNow();var read=new PlayerStore(folder,Logger.getLogger("mail-test")).get(id);
        assertEquals(1,read.sunflowers());assertTrue(read.letterRead("flora_first"));assertEquals(3,read.hoeTier());assertEquals(1234,read.skillXp());
        assertTrue(read.spendSunflowers(1));org.junit.jupiter.api.Assertions.assertFalse(read.spendSunflowers(1));
    }
    @Test void decisionsSurviveRestartWithoutChangingQuestOrSkillState(@TempDir File folder){
        var store=new PlayerStore(folder,Logger.getLogger("memory-test"));UUID id=UUID.randomUUID();var data=store.get(id);
        data.complete("story_martha",true);assertTrue(data.decide("story_martha","kind"));data.addSkillXp(1234);data.setHoeTier(3);
        store.saveAllNow();var read=new PlayerStore(folder,Logger.getLogger("memory-test")).get(id);
        assertEquals("kind",read.decision("story_martha"));assertEquals(1234,read.skillXp());assertEquals(3,read.hoeTier());assertTrue(read.isCompleted("story_martha"));
        org.junit.jupiter.api.Assertions.assertFalse(read.decide("story_martha","selfish"));
    }
    @Test void offlinePlayersAreSavedAndLeaveMemory(@TempDir File folder) {
        java.util.List<Runnable> tasks=new java.util.ArrayList<>();
        PlayerStore store=new PlayerStore(folder,Logger.getLogger("test"),tasks::add);
        UUID online=UUID.randomUUID(),offline=UUID.randomUUID();
        store.get(online);store.get(offline).setHoeTier(2);
        store.evictOffline(online::equals);
        while(!tasks.isEmpty())tasks.removeFirst().run();
        org.junit.jupiter.api.Assertions.assertNotNull(store.cached(online));
        org.junit.jupiter.api.Assertions.assertNull(store.cached(offline));
        assertEquals(2,new PlayerStore(folder,Logger.getLogger("test")).get(offline).hoeTier());
    }
    @Test void reconnectBeforeQuitSaveKeepsLatestLedger(@TempDir File folder) {
        java.util.List<Runnable> tasks=new java.util.ArrayList<>();
        PlayerStore store=new PlayerStore(folder,Logger.getLogger("test"),tasks::add);
        UUID id=UUID.randomUUID();PlayerData first=store.get(id);
        first.complete("welcome",true);first.setHoeTier(2);store.unload(id);
        PlayerData rejoined=store.get(id);
        org.junit.jupiter.api.Assertions.assertSame(first,rejoined);
        tasks.removeFirst().run();
        org.junit.jupiter.api.Assertions.assertSame(rejoined,store.cached(id));
        assertTrue(rejoined.isCompleted("welcome"));assertEquals(2,rejoined.hoeTier());
        rejoined.addSkillXp(100);store.unload(id);tasks.removeFirst().run();
        org.junit.jupiter.api.Assertions.assertNull(store.cached(id));
        assertEquals(100,store.get(id).skillXp());
    }
    @Test void oldQueuedSaveCannotOverwriteNewSessionOrRestore(@TempDir File folder) throws Exception {
        java.util.List<Runnable> tasks=new java.util.ArrayList<>();
        PlayerStore store=new PlayerStore(folder,Logger.getLogger("test"),tasks::add);
        UUID id=UUID.randomUUID();PlayerData first=store.get(id);first.setHoeTier(1);
        store.saveNow(first);Runnable late=tasks.removeFirst();
        first.setHoeTier(2);store.unload(id);tasks.removeFirst().run();
        PlayerData next=store.get(id);next.setHoeTier(3);store.saveAllNow();late.run();
        assertEquals(3,new PlayerStore(folder,Logger.getLogger("test")).get(id).hoeTier());
        store.unload(id);PlayerData restored=store.restore(id,GOOD);tasks.removeFirst().run();
        org.junit.jupiter.api.Assertions.assertSame(restored,store.cached(id));
        assertTrue(new PlayerStore(folder,Logger.getLogger("test")).get(id).isCompleted("welcome"));
    }
    @Test void customSkillAndPaidUnlockSurviveRestartAndInitializeOnlyOnce(@TempDir File folder) {
        PlayerStore store=new PlayerStore(folder,Logger.getLogger("test"));UUID id=UUID.randomUUID();
        PlayerData data=store.get(id);assertTrue(!data.skillInitialized());
        data.initializeSkill(5000);data.addSkillXp(10);data.addWheat(1);data.setHoeTier(3);data.initializeSkill(9000);
        store.saveAllNow();
        PlayerData read=new PlayerStore(folder,Logger.getLogger("test")).get(id);
        assertTrue(read.skillInitialized());assertEquals(5010,read.skillXp());assertEquals(1,read.wheatHarvested());assertEquals(3,read.hoeTier());
        read.reset();assertEquals(3,read.hoeTier());assertEquals(5010,read.skillXp());
    }
    @Test void displayPreferencesSurviveSaveReloadWithoutChangingProgress(@TempDir File folder) throws Exception {
        PlayerStore store = new PlayerStore(folder, Logger.getLogger("test"));
        UUID uuid = UUID.randomUUID();
        Files.writeString(new File(store.dir(), uuid + ".yml").toPath(), GOOD);
        PlayerData data = store.get(uuid);
        assertTrue(!data.trackerOn(false));
        assertTrue(!data.directionsOn(false));
        assertEquals("book", data.menuMode("book"));
        data.setTrackerOn(true); data.setDirectionsOn(true); data.setMenuMode("menu");
        data.meet("bob");
        store.saveAllNow();
        PlayerData read = new PlayerStore(folder, Logger.getLogger("test")).get(uuid);
        assertTrue(read.trackerOn(false));
        assertTrue(read.directionsOn(false));
        assertEquals("menu", read.menuMode("book"));
        assertEquals(4, read.sideDone("stephan"));
        assertTrue(read.isCompleted("story_stephan"));
        assertTrue(read.hasMet("bob"));
    }

    private static final String GOOD = "completed:\n- welcome\n- story_stephan\nside-done:\n  stephan: 4\n";

    @Test
    void brokenFileIsRecoveredFromThePreviousSave(@TempDir File folder) throws Exception {
        PlayerStore store = new PlayerStore(folder, Logger.getLogger("test"));
        UUID uuid = UUID.randomUUID();
        Files.writeString(new File(store.dir(), uuid + ".yml").toPath(), "completed: [oops\n  : : broken");
        Files.writeString(new File(store.dir(), uuid + ".yml.bak").toPath(), GOOD);

        PlayerData data = store.get(uuid);

        assertTrue(data.isCompleted("story_stephan"));
        assertEquals(4, data.sideDone("stephan"));
        File[] kept = store.dir().listFiles((dir, name) -> name.contains(".broken-"));
        assertTrue(kept != null && kept.length == 1, "the broken file is kept for inspection");
    }

    @Test
    void restoreReplacesOnlineDataAndRetiresTheOldCopy(@TempDir File folder) throws Exception {
        PlayerStore store = new PlayerStore(folder, Logger.getLogger("test"));
        UUID uuid = UUID.randomUUID();
        PlayerData old = store.get(uuid);

        PlayerData restored = store.restore(uuid, GOOD);

        assertTrue(old.retired, "a late save of the old copy must not overwrite the restore");
        assertTrue(store.cached(uuid) == restored);
        assertTrue(restored.isCompleted("welcome"));
        assertEquals(GOOD, Files.readString(new File(store.dir(), uuid + ".yml").toPath()));
    }
}
