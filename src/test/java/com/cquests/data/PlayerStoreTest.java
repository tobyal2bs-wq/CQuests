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
