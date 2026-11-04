package com.cquests.worldboss;

import com.google.gson.Gson;
import org.bukkit.Material;
import org.bukkit.configuration.file.YamlConfiguration;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Logger;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ModelRigTest {
    static Map<String, ModelRig.Model> models;
    static Map<String, WorldBossDef> defs;

    @BeforeAll
    static void load() throws IOException {
        try (FileReader r = new FileReader("src/main/resources/worldboss-models.json")) { models = ModelRig.load(r); }
        defs = WorldBossDef.load(YamlConfiguration.loadConfiguration(new File("src/main/resources/worldbosses.yml")), Logger.getLogger("ModelRigTest"));
    }

    @Test
    void everyBossHasADetailedModel() {
        for (WorldBossDef d : defs.values()) {
            ModelRig.Model m = models.get(d.model());
            assertNotNull(m, d.id() + " has a model");
            assertTrue(m.cubes.size() >= 38, d.id() + " has " + m.cubes.size() + " blocks");
            assertTrue(m.cubes.size() <= 140, d.id() + " is not too heavy: " + m.cubes.size());
            assertTrue(m.blocks() >= 3 && m.blocks() <= 8, d.id() + " is " + m.blocks() + " blocks tall");
            for (ModelRig.Cube c : m.cubes) {
                Material mat = Material.matchMaterial(c.base());
                assertNotNull(mat, d.id() + ": unknown block " + c.block());
            }
        }
    }

    @Test
    void threeOrMoreAttackAnimationsEachAndTheyExist() {
        for (WorldBossDef d : defs.values()) {
            ModelRig.Model m = models.get(d.model());
            assertTrue(m.attackAnimations().size() >= 3, d.id() + " has " + m.attackAnimations());
            for (String a : m.attackAnimations()) {
                ModelRig.Anim anim = m.anim(a);
                assertNotNull(anim, d.id() + ": no animation " + a + " on rig " + m.rig);
                assertTrue(anim.hit() > 0 && anim.hit() < anim.length(), d.id() + " " + a + " lands inside the animation");
            }
            for (String ability : d.abilities()) assertNotNull(m.anim(m.attackFor(ability)), d.id() + " " + ability);
            for (String base : List.of("idle", "walk", "hurt")) assertNotNull(m.anim(base), d.id() + " " + base);
        }
    }

    @Test
    void everySpawnAndEveryDeathIsDifferent() {
        Gson gson = new Gson();
        Set<String> spawns = new HashSet<>(), deaths = new HashSet<>();
        for (ModelRig.Model m : models.values()) {
            assertTrue(m.spawn.size() >= 3 && m.death.size() >= 3, m.id + " has a spawn and a death");
            assertTrue(spawns.add(gson.toJson(m.spawn.stream().map(ModelRig.Step::params).toList())), m.id + " spawn is unique");
            assertTrue(deaths.add(gson.toJson(m.death.stream().map(ModelRig.Step::params).toList())), m.id + " death is unique");
            for (ModelRig.Step s : concat(m.spawn, m.death)) {
                assertTrue(ModelRig.OPS.contains(s.op()), m.id + ": unknown step " + s.op());
                assertTrue(ModelRig.ORDERS.contains(s.order()), m.id + ": unknown order " + s.order());
                if (s.op().equals("anim")) assertNotNull(m.anim(s.str("name", "")), m.id + ": no animation " + s.str("name", ""));
                if (!s.only().isEmpty()) {
                    boolean any = false;
                    for (int i = 0; i < m.cubes.size(); i++) any |= m.matches(s.only(), i);
                    assertTrue(any, m.id + ": '" + s.only() + "' matches no block");
                }
                if (s.op().equals("swap") && !s.str("block", "").isEmpty()) assertNotNull(Material.matchMaterial(s.str("block", "")), m.id + " swap " + s.str("block", ""));
                if (s.op().equals("fx") && !s.str("sound", "").isEmpty()) {
                    try { org.bukkit.Sound.class.getField(s.str("sound", "")); }
                    catch (NoSuchFieldException e) { throw new AssertionError(m.id + ": no sound " + s.str("sound", "")); }
                }
                if (s.op().equals("fx") && !s.str("particle", "").isEmpty()) org.bukkit.Particle.valueOf(s.str("particle", ""));
            }
        }
        assertEquals(models.size(), spawns.size());
    }

    private static List<ModelRig.Step> concat(List<ModelRig.Step> a, List<ModelRig.Step> b) {
        List<ModelRig.Step> out = new java.util.ArrayList<>(a); out.addAll(b); return out;
    }

    @Test
    void restPoseStandsOnTheGround() {
        for (ModelRig.Model m : models.values()) {
            Matrix4f[] cubes = ModelRig.cubes(m, ModelRig.pose(m, List.of(new ModelRig.Layer(m.anim("idle"), 0, 1))));
            float min = Float.MAX_VALUE, max = -Float.MAX_VALUE;
            Vector3f p = new Vector3f();
            for (Matrix4f c : cubes) for (int k = 0; k < 8; k++) {
                c.transformPosition(k & 1, k >> 1 & 1, k >> 2 & 1, p);
                min = Math.min(min, p.y); max = Math.max(max, p.y);
            }
            // Floaters hover; everything else touches the floor.
            if (!m.rig.equals("float")) assertTrue(Math.abs(min) < 0.35f, m.id + " lowest point " + min);
            assertTrue(max > 2.5f, m.id + " top " + max);
        }
    }

    @Test
    void animationsMoveTheBonesTheyName() {
        ModelRig.Model m = models.get("gravelord");
        Matrix4f[] rest = ModelRig.pose(m, List.of(new ModelRig.Layer(m.anim("idle"), 0, 1)));
        ModelRig.Anim slam = m.anim("slam");
        Matrix4f[] hit = ModelRig.pose(m, List.of(new ModelRig.Layer(m.anim("idle"), 0, 1), new ModelRig.Layer(slam, 0.6f, 1)));
        int arm = m.boneIndex.get("armR");
        Vector3f a = rest[arm].transformPosition(new Vector3f(-9, 16, 2)), b = hit[arm].transformPosition(new Vector3f(-9, 16, 2));
        assertTrue(b.y > a.y + 10, "the slam raises the arm: " + a + " -> " + b);
        // A bone the animation does not name follows its parent only.
        int legL = m.boneIndex.get("legL");
        assertTrue(rest[legL].equals(hit[legL], 1e-3f) || slam.bones().containsKey("legL") || slam.bones().containsKey("hips"));
    }

    @Test
    void transformationKeepsShapeAndHandlesZeroScale() {
        Matrix4f m = new Matrix4f().translation(1, 2, 3).rotateY(0.7f).scale(2, 0.5f, 3);
        var t = BossModel.transformation(m);
        assertEquals(2, t.getScale().x, 1e-4); assertEquals(0.5, t.getScale().y, 1e-4); assertEquals(3, t.getScale().z, 1e-4);
        assertEquals(1, t.getTranslation().x, 1e-4);
        var zero = BossModel.transformation(new Matrix4f().translation(1, 1, 1).scale(0));
        assertTrue(Float.isFinite(zero.getLeftRotation().w));
    }

    @Test
    void staggerRanksCoverZeroToOne() {
        ModelRig.Model m = models.get("pharaoh");
        Matrix4f[] cubes = ModelRig.cubes(m, ModelRig.pose(m, List.of(new ModelRig.Layer(m.anim("idle"), 0, 1))));
        float[] up = ModelRig.ranks(m, cubes, "up", 1);
        float lo = 2, hi = -1;
        for (float r : up) { lo = Math.min(lo, r); hi = Math.max(hi, r); }
        assertEquals(0, lo, 1e-6); assertEquals(1, hi, 1e-6);
        for (float r : ModelRig.ranks(m, cubes, "none", 1)) assertEquals(0, r);
    }
}
