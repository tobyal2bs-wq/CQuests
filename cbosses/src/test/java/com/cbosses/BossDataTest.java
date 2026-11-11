package com.cbosses;

import com.cbosses.fight.BossDef;
import com.cbosses.fight.BossService;
import com.cbosses.model.ModelRig;
import com.cbosses.season.Seasons;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.MonthDay;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.*;

class BossDataTest {

    private static Map<String, ModelRig.Model> models() throws Exception {
        try (var in = BossDataTest.class.getResourceAsStream("/models.json")) {
            assertNotNull(in, "models.json is missing");
            return ModelRig.load(new InputStreamReader(in, StandardCharsets.UTF_8));
        }
    }

    private static Map<String, BossDef> bosses() throws Exception {
        try (var in = BossDataTest.class.getResourceAsStream("/bosses.yml")) {
            assertNotNull(in, "bosses.yml is missing");
            YamlConfiguration yaml = YamlConfiguration.loadConfiguration(new InputStreamReader(in, StandardCharsets.UTF_8));
            int listed = yaml.getConfigurationSection("bosses").getKeys(false).size();
            Map<String, BossDef> defs = BossDef.load(yaml, Logger.getLogger("test"));
            assertEquals(listed, defs.size(), "every boss in bosses.yml loads");
            return defs;
        }
    }

    @Test
    void everyBossHasAModelWithAnEntranceAndADeath() throws Exception {
        var models = models();
        var defs = bosses();
        assertEquals(94, defs.size(), "41 weekly, 3 mythic, 12 seasonal, 8 chapter and 30 mini bosses");
        for (BossDef d : defs.values()) {
            ModelRig.Model m = models.get(d.model());
            assertNotNull(m, d.id() + " has no model");
            assertFalse(m.spawn.isEmpty(), d.id() + " has no entrance");
            assertFalse(m.death.isEmpty(), d.id() + " has no death");
            for (var s : m.spawn) assertTrue(ModelRig.OPS.contains(s.op()) || s.op().equals("fx"), d.id() + " entrance step " + s.op());
            for (var s : m.death) assertTrue(ModelRig.OPS.contains(s.op()) || s.op().equals("fx"), d.id() + " death step " + s.op());
            assertTrue(m.death.stream().anyMatch(s -> s.op().equals("flash")), d.id() + " death has no flash");
            for (String anim : m.attackAnimations()) assertNotNull(m.anim(anim), d.id() + " attack animation " + anim + " is not in rig " + m.rig);
            assertNotNull(m.anim("idle"), d.id() + " idle");
            assertNotNull(m.anim("hurt"), d.id() + " hurt");
            if (d.flies()) assertNotNull(m.anim("idle"), d.id() + " flies");
        }
    }

    @Test
    void bigBossesHave150BlocksChapterBossesAreSmallAndAllCanDropDetail() throws Exception {
        var full = models();
        var defs = bosses();
        for (BossDef d : defs.values()) {
            ModelRig.Model fm = full.get(d.model());
            int n = fm.cubes.size();
            // only one face is shown at a time, so the spare faces don't count
            if (fm.faceOf != null) for (String f : fm.faceOf) if (f != null && !f.equals("idle")) n--;
            if (d.mini()) assertTrue(n >= 25 && n <= 300, d.id() + " is a mini boss with " + n + " blocks");
            else if (d.chapterBoss() && d.chapter() >= 4) assertTrue(n >= 150 && n <= 300, d.id() + " is a rebuilt chapter boss with " + n + " blocks");
            else if (d.chapterBoss()) assertTrue(n >= 70 && n <= 300, d.id() + " is a chapter boss with " + n + " blocks");
            else if (d.sidekick()) assertTrue(n >= 150 && n <= 300, d.id() + " is a second body with " + n + " blocks");
            else if (d.seasonal()) assertTrue(n >= 60 && n <= 300, d.id() + " is a painted seasonal boss with " + n + " blocks");
            else assertTrue(n >= 40 && n <= 300, d.id() + " has " + n + " blocks");
        }
        int was = ModelRig.detail;
        try {
            ModelRig.detail = 0;
            var low = models();
            for (var e : low.entrySet()) {
                assertTrue(low.get(e.getKey()).cubes.size() < full.get(e.getKey()).cubes.size(), e.getKey() + " keeps every block on low detail");
                assertFalse(low.get(e.getKey()).cubes.isEmpty(), e.getKey() + " is empty on low detail");
            }
        } finally { ModelRig.detail = was; }
    }

    @Test
    void threeBossesForEverySeason() throws Exception {
        var defs = bosses();
        for (String season : new String[]{"winter", "summer", "spring", "halloween"})
            assertEquals(3, defs.values().stream().filter(d -> d.seasonal() && season.equals(d.season())).count(), season);
        assertEquals(44, defs.values().stream().filter(d -> !d.seasonal() && !d.chapterBoss() && !d.mini() && !d.sidekick()).count(), "41 weekly bosses and 3 mythic");
    }

    @Test
    void healthTiersAndMiniBosses() throws Exception {
        var defs = bosses();
        assertEquals(30, defs.values().stream().filter(BossDef::mini).count(), "30 mini bosses");
        for (BossDef d : defs.values()) {
            if (d.mini()) assertEquals(1000, d.health(), 0.01, d.id());
            else if (d.tier().equals("mythic")) assertEquals(3000, d.health(), 0.01, d.id());
            else if (!d.chapterBoss() && !d.sidekick()) assertEquals(3000, d.health(), 0.01, d.id());
        }
        for (String id : new String[]{"the_unmaker", "withered_tyrant", "the_listener"}) assertEquals("mythic", defs.get(id).tier(), id);
    }

    @Test
    void everyModelIsItsClassSize() throws Exception {
        var models = models();
        var defs = bosses();
        for (BossDef d : defs.values()) {
            ModelRig.Model m = models.get(d.model());
            float blocks = m.blocks();
            // long, low models (wolves, crabs, turtles) are sized by their length, so they stand lower
            if (d.mini() || d.sidekick()) assertTrue(blocks >= 0.6 && blocks <= 2.05, d.id() + " is a mini " + blocks + " blocks tall");
            else if (d.tier().equals("mythic")) assertTrue(blocks >= 1.8 && blocks <= 5.1, d.id() + " is mythic and " + blocks + " blocks tall");
            else assertTrue(blocks >= 1.8 && blocks <= 3.6, d.id() + " is a big boss " + blocks + " blocks tall");
            assertTrue(m.hitbox >= 0.45f, d.id() + " hitbox " + m.hitbox);
        }
    }

    @Test
    void retiredBossesAreGoneAndTwinsAreOneModelAgain() throws Exception {
        var defs = bosses();
        for (String id : new String[]{"cluck_rider", "hollow_king", "ender_wyrm", "gale_sovereign", "ghost_jelly", "orc_bruiser", "cyclops_ogre", "cinder_imp", "boo_twins", "shulker_matriarch", "pink_burrower", "ironhide_behemoth", "void_walker", "fenrir"}) assertNull(defs.get(id), id);
        assertEquals(0, defs.values().stream().filter(BossDef::sidekick).count());
        var yaml = org.bukkit.configuration.file.YamlConfiguration.loadConfiguration(new java.io.File("src/main/resources/bosses.yml"));
        assertTrue(yaml.getStringList("removed").contains("cluck_rider"));
    }

    @Test
    void newBigBossesAreCleanAndAlive() throws Exception {
        var models = models();
        for (String id : new String[]{"abyssal_eye", "tide_tyrant", "storm_herald", "ember_queen", "gravelord", "bloodtusk",
                "old_ironroot", "gate_shade", "frost_yeti", "bog_orc"}) {
            ModelRig.Model m = models.get(id);
            assertNotNull(m, id);
            int n = m.cubes.size();
            assertTrue(n >= 50 && n <= 300, id + " has " + n + " blocks");
            assertNotNull(m.anim("idle"), id + " idle");
        }
    }

    @Test
    void rebuiltBossesAreTexturedAndAlive() throws Exception {
        var models = models();
        for (String id : new String[]{"gnome_brothers", "moss_spirit", "grubnose", "mudclub", "ugor"}) {
            ModelRig.Model m = models.get(id);
            assertNotNull(m, id);
            int n = m.cubes.size();
            assertTrue(n >= 150 && n <= 300, id + " has " + n + " blocks");
            long kinds = m.cubes.stream().map(ModelRig.Cube::base).distinct().count();
            assertTrue(kinds >= 6, id + " uses only " + kinds + " kinds of block");
            assertNotNull(m.anim("idle"), id + " idle");
        }
    }

    @Test
    void faceChangingModels() throws Exception {
        var models = models();
        ModelRig.Model king = models.get("gourd_king");
        assertNotNull(king.faceOf, "the Gourd King changes faces");
        for (String f : new String[]{"idle", "angry", "hurt", "rage", "dead"}) assertTrue(king.faces.contains(f), "gourd king face " + f);
        for (String id : new String[]{"decor_pumpkin_tall", "decor_pumpkin_flat", "decor_pumpkin_cube"}) {
            ModelRig.Model m = models.get(id);
            assertNotNull(m, id);
            assertTrue(m.faces.size() >= 5, id + " has faces");
        }
        for (String id : new String[]{"decor_gingerbread", "decor_gingerbread_girl", "decor_egg_pink", "decor_egg_blue", "decor_egg_mint"}) {
            ModelRig.Model m = models.get(id);
            assertNotNull(m, id);
            assertTrue(m.faces.contains("happy") && m.faces.contains("sad"), id + " is happy and sometimes sad");
            assertTrue(m.blocks() > 0.8f && m.blocks() < 1.2f, id + " stands about one block tall, so they stack");
        }
        // only one face shows at a time
        var pose = ModelRig.cubes(king, ModelRig.pose(king, java.util.List.of(new ModelRig.Layer(king.anim("idle"), 0, 1))));
        king.showFace(pose, "angry");
        for (int i = 0; i < pose.length; i++) if (king.faceOf[i] != null && !king.faceOf[i].equals("angry"))
            assertTrue(pose[i].getScale(new org.joml.Vector3f()).length() < 1e-4, "hidden face piece " + i);
    }

    @Test
    void theFinaleBossExistsAndIsKeptOutOfTheWeeklyRotation() throws Exception {
        var defs = bosses();
        assertNotNull(defs.get("the_unmaker"), "the finale boss");
        for (String legend : new String[]{"withered_tyrant", "the_listener"}) assertNotNull(defs.get(legend), legend);
        ModelRig.Model m = models().get("the_unmaker");
        assertTrue(m.cubes.size() >= 200, "the finale is the most detailed boss");
        assertTrue(m.death.stream().anyMatch(s -> s.op().equals("shatter")), "the finale shatters");
    }

    @Test
    void chapterBossesCoverTenChapters() throws Exception {
        var defs = bosses();
        // chapters 6 and 8 lost their bosses (Gulp and Borka were removed); ops can put any boss there
        for (int ch : new int[]{1, 2, 3, 4, 5, 7, 9, 10}) {
            int n = ch;
            assertTrue(defs.values().stream().anyMatch(d -> d.chapterBoss() && d.chapter() == n), "no boss for chapter " + ch);
        }
    }

    @Test
    void cluckworthHatchesFromAnEggThatOnlyShowsDuringItsEntrance() throws Exception {
        ModelRig.Model m = models().get("clucksworth");
        int shell = 0;
        for (boolean b : m.entranceOnly) if (b) shell++;
        assertTrue(shell >= 10, "the egg has pieces");
        assertTrue(m.spawn.stream().anyMatch(s -> s.op().equals("shatter")), "the egg shatters");
    }

    @Test
    void scheduleFindsTheNextSlot() {
        ZonedDateTime now = ZonedDateTime.of(2026, 11, 4, 12, 0, 0, 0, ZoneOffset.UTC); // a Wednesday
        ZonedDateTime next = BossService.nextAfter(now, List.of(DayOfWeek.SATURDAY), LocalTime.of(20, 0), "");
        assertEquals(LocalDate.of(2026, 11, 7), next.toLocalDate());
        ZonedDateTime skip = BossService.nextAfter(now, List.of(DayOfWeek.SATURDAY), LocalTime.of(20, 0), "2026-11-07 20:00");
        assertEquals(LocalDate.of(2026, 11, 14), skip.toLocalDate());
    }

    @Test
    void seasonsWrapAroundNewYear() {
        assertTrue(Seasons.inWindow(MonthDay.of(12, 10), MonthDay.of(1, 5), LocalDate.of(2027, 1, 2)));
        assertFalse(Seasons.inWindow(MonthDay.of(12, 10), MonthDay.of(1, 5), LocalDate.of(2027, 2, 2)));
        assertTrue(Seasons.inWindow(MonthDay.of(7, 1), MonthDay.of(7, 31), LocalDate.of(2027, 7, 15)));
    }

    @Test
    void blocksShownInGameMatchTheModel() throws Exception {
        // what the client draws (translation x rotation x scale) must be the posed cube, or the boss breaks apart
        for (ModelRig.Model m : models().values()) {
            for (String an : new String[]{"idle", "walk"}) {
                var anim = m.anim(an);
                if (anim == null) continue;
                org.joml.Matrix4f[] cubes = ModelRig.cubes(m, ModelRig.pose(m, java.util.List.of(new ModelRig.Layer(anim, 0.5f, 1))));
                for (org.joml.Matrix4f c : cubes) {
                    var t = com.cbosses.model.Displays.transformation(c);
                    org.joml.Matrix4f shown = new org.joml.Matrix4f().translation(t.getTranslation()).rotate(t.getLeftRotation()).scale(t.getScale()).rotate(t.getRightRotation());
                    for (int k = 0; k < 8; k++) {
                        float d = c.transformPosition(k & 1, k >> 1 & 1, k >> 2 & 1, new org.joml.Vector3f())
                                .distance(shown.transformPosition(k & 1, k >> 1 & 1, k >> 2 & 1, new org.joml.Vector3f()));
                        assertTrue(d < 0.01f, m.id + " " + an + ": a block is drawn " + d + " blocks off");
                    }
                }
            }
        }
    }

    @Test
    void approvedMonkShipsAsAWorldBossAndOtherDraftsStayExcluded() throws Exception {
        var d = bosses().get("millstone_monk");
        assertNotNull(d); assertEquals("world", d.kind()); assertEquals("big", d.tier());
        assertEquals(3000, d.health(), .01); assertFalse(d.seasonal()); assertFalse(d.chapterBoss());
        assertEquals(List.of("shockwave", "quake", "heal"), d.abilities());
        var all = models(); var m = all.get("millstone_monk"); assertNotNull(m);
        assertEquals(2, m.cubes.stream().filter(c -> c.tag().equals("eye_socket")).count());
        var wheel = m.bones.stream().filter(b -> b.name().equals("wheel")).findFirst().orElseThrow();
        assertEquals("body", m.bones.get(wheel.parent()).name());
        assertTrue(m.zones.stream().anyMatch(z -> z.kind().equals("weak") && m.bones.get(z.bone()).name().equals("wheel")));
        for (String draft : List.of("bellwether", "driftjaw")) assertFalse(all.containsKey(draft), draft);
    }
}
