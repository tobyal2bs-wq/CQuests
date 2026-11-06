package com.cquests.worldboss;

import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.time.DayOfWeek;
import java.time.LocalTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class WorldBossDefTest {

    @Test
    void twentyBossesPlusSeasonalOnesLoadCleanly() {
        List<String> warnings = new ArrayList<>();
        Logger log = Logger.getLogger("WorldBossDefTest");
        log.setUseParentHandlers(false);
        log.addHandler(new Handler() {
            @Override public void publish(LogRecord r) { if (r.getLevel().intValue() >= Level.WARNING.intValue()) warnings.add(r.getMessage()); }
            @Override public void flush() { }
            @Override public void close() { }
        });
        Map<String, WorldBossDef> defs = WorldBossDef.load(YamlConfiguration.loadConfiguration(new File("src/main/resources/worldbosses.yml")), log);
        assertTrue(warnings.isEmpty(), warnings.toString());
        assertEquals(26, defs.values().stream().filter(d -> !d.seasonal()).count(), "24 general bosses and 2 legends");
        assertEquals(12, defs.values().stream().filter(d -> d.seasonal()).count(), "three for each season");
        YamlConfiguration config = YamlConfiguration.loadConfiguration(new File("src/main/resources/config.yml"));
        for (WorldBossDef d : defs.values()) {
            assertTrue(d.health() >= 800, d.id() + " health");
            assertTrue(!d.abilities().isEmpty(), d.id() + " has abilities");
            assertTrue(d.rewards().money() > 0, d.id() + " pays");
            if (d.seasonal()) assertNotNull(config.getConfigurationSection("seasons." + d.season()), d.id() + " season exists");
        }
        for (String season : List.of("halloween", "winter", "spring", "summer"))
            assertTrue(defs.values().stream().anyMatch(d -> d.season().equals(season)), season + " has a boss");
    }

    @Test
    void weeklyScheduleFindsTheNextSlot() {
        ZonedDateTime friday = ZonedDateTime.of(2026, 11, 6, 12, 0, 0, 0, ZoneOffset.UTC);
        ZonedDateTime next = WorldBossService.nextAfter(friday, List.of(DayOfWeek.SATURDAY), LocalTime.of(20, 0), "");
        assertEquals(ZonedDateTime.of(2026, 11, 7, 20, 0, 0, 0, ZoneOffset.UTC), next);
        // Already ran on that Saturday: the one after.
        ZonedDateTime later = WorldBossService.nextAfter(friday, List.of(DayOfWeek.SATURDAY), LocalTime.of(20, 0), "2026-11-07");
        assertEquals(ZonedDateTime.of(2026, 11, 14, 20, 0, 0, 0, ZoneOffset.UTC), later);
        assertNull(WorldBossService.nextAfter(friday, List.of(), LocalTime.of(20, 0), ""));
    }

    @Test
    void arenaBorderIsTheOutlineOrACircle() {
        Arena a = new Arena("main", 10);
        a.world = "world"; a.x = 0.5; a.z = 0.5; a.hasSpawn = true;
        assertNull(a.add(0, 0));
        assertNull(a.add(20, 0));
        assertNull(a.add(20, 20));
        assertNotNull(a.polygon);
        assertTrue(a.undo());
        assertNull(a.polygon);
        assertEquals("circle of 10 blocks", a.describe());
        assertEquals(120, Arena.parseInterval("2h"));
        assertEquals(24000, Arena.parseInterval("400h"));
        assertEquals(2160, Arena.parseInterval("1d12h"));
        assertEquals(0, Arena.parseInterval("off"));
        assertEquals(-1, Arena.parseInterval("soon"));
        assertEquals("1d12h", Arena.intervalText(2160));
        a.nopass.add(new double[]{0, 5, 5, 3});
        a.nopass.add(Arena.nopassParse("box:10.0,10.0,12.0,14.0"));
        assertTrue(a.blocked(6, 6));
        assertTrue(a.blocked(11, 12));
        assertTrue(!a.blocked(15, 0));
    }
}
