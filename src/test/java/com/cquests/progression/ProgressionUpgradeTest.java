package com.cquests.progression;

import com.cquests.CQuestsPlugin;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.io.File;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class ProgressionUpgradeTest {
    @Test void formerCapGetsBackupWithoutChangingPlayerFilesOrCustomPrices(@TempDir File folder) throws Exception {
        var plugin=mock(CQuestsPlugin.class);when(plugin.getDataFolder()).thenReturn(folder);
        Path config=folder.toPath().resolve("farming.yml");String original="levels:\n  maximum: 100\n  target-active-hours: 401\ntiers:\n  2:\n    cost: 12345\n";
        Files.writeString(config,original);Path player=folder.toPath().resolve("players/player.yml");Files.createDirectories(player.getParent());Files.writeString(player,"skill:\n  xp: 123456\ncompleted: [welcome]\n");byte[] state=Files.readAllBytes(player);
        ProgressionUpgrade.apply(plugin);var result=YamlConfiguration.loadConfiguration(config.toFile());
        assertEquals(500,result.getInt("levels.maximum"));assertEquals(401,result.getInt("levels.target-active-hours"));assertEquals(12345,result.getInt("tiers.2.cost"));
        assertEquals(original,Files.readString(folder.toPath().resolve("farming.yml.before-1.4.0")));assertArrayEquals(state,Files.readAllBytes(player));
        Files.writeString(config,"levels:\n  maximum: 750\n");ProgressionUpgrade.apply(plugin);assertTrue(Files.readString(config).contains("750"));
    }
    @Test void aCustomCapIsKeptByteForByte(@TempDir File folder) throws Exception {
        var plugin=mock(CQuestsPlugin.class);when(plugin.getDataFolder()).thenReturn(folder);
        var path=folder.toPath().resolve("farming.yml");String original="# My custom curve\nlevels:\n  maximum: 800\n";Files.writeString(path,original);
        ProgressionUpgrade.apply(plugin);assertEquals(original,Files.readString(path));assertFalse(Files.exists(folder.toPath().resolve("farming.yml.before-1.4.0")));
    }
}
