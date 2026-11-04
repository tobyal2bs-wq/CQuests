package com.cquests.worldboss;

import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.block.data.BlockData;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.plugin.Plugin;
import org.bukkit.util.Transformation;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * A world boss drawn with block displays. The real mob is invisible and keeps its AI and hitbox; every
 * block of the model rides it, so the client moves them smoothly with the mob. Each block's pose is
 * baked into its transformation (bone, then the mob's facing, then the riding offset) and the client
 * blends between updates. Updates go out every few ticks, only while someone is close, and only for
 * blocks that changed. Spawn and death play the model's own steps (ModelRig) on the blocks.
 */
final class BossModel {
    private static final int PERIOD = 3;
    private static final float DT = PERIOD / 20f;

    final ModelRig.Model model;
    private final Plugin plugin;
    private final Mob mob;
    private final List<BlockDisplay> parts = new ArrayList<>();
    /** One invisible hit box per zone of the body (head, weak spot, arms...), moved with its bone. */
    private final List<Interaction> zones = new ArrayList<>();
    private final Map<UUID, Integer> zoneIndex = new java.util.concurrent.ConcurrentHashMap<>();
    private Matrix4f[] bones;
    /** Far from every player the model updates half as often; the client blends over the longer gap. */
    private int frame, stride = 1;
    private final BlockData[] original;
    private final Matrix4f[] pose, op;
    private final Transformation[] sent;
    private final Random random = new Random();

    private final Vector3f attach = new Vector3f();
    private float yaw;
    private float idleT, walkT, walkW, attackT, hurtT = 99, lastMelee = -99;
    private ModelRig.Anim attack;
    private Location last;
    private boolean live, dying, gone, visible = true;
    private int viewerCheck;
    /** The self-test has nobody watching but still wants every update sent. */
    volatile boolean force;
    /** Damage of a melee swing that lands beyond the mob's own short reach (its hitbox is smaller than the model). */
    volatile double meleeDamage;
    private ScheduledTask loop;
    int animationsPlayed;

    BossModel(Plugin plugin, ModelRig.Model model, Mob mob) {
        this.plugin = plugin; this.model = model; this.mob = mob;
        int n = model.cubes.size();
        original = new BlockData[n];
        pose = new Matrix4f[n]; op = new Matrix4f[n]; sent = new Transformation[n];
        for (int i = 0; i < n; i++) op[i] = new Matrix4f();
    }

    int blocks() { return parts.size(); }
    int zoneCount() { int n = 0; for (Interaction z : zones) if (z.isValid()) n++; return n; }
    boolean dying() { return dying; }

    /** Spawns the hidden blocks on the mob. Runs on the mob's region. */
    void build(NamespacedKey kindKey, NamespacedKey fightKey, String fight) {
        Location at = mob.getLocation();
        at.setYaw(0); at.setPitch(0);
        // view range 1 is about 64 blocks; a boss is seen a little further than a normal mob, no more
        float range = Math.max(0.75f, Math.min(1.5f, model.blocks() / 5f));
        Transformation hidden = new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(), new Quaternionf());
        for (int i = 0; i < model.cubes.size(); i++) {
            ModelRig.Cube c = model.cubes.get(i);
            BlockData data;
            try { data = Bukkit.createBlockData(c.block().contains(":") ? c.block() : "minecraft:" + c.block()); }
            catch (IllegalArgumentException e) {
                Material m = Material.matchMaterial(c.base());
                data = (m != null && m.isBlock() ? m : Material.STONE).createBlockData();
            }
            original[i] = data;
            BlockData d0 = data;
            BlockDisplay d = at.getWorld().spawn(at, BlockDisplay.class, e -> {
                e.setPersistent(false);
                e.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "part");
                e.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, fight);
                e.setBlock(d0);
                e.setTransformation(hidden);
                e.setViewRange(range);
                e.setShadowRadius(0);
                if (c.light()) e.setBrightness(new Display.Brightness(15, 15));
            });
            mob.addPassenger(d);
            parts.add(d);
        }
        float s = model.scale / 16f;
        for (int i = 0; i < model.zones.size(); i++) {
            ModelRig.Zone z = model.zones.get(i);
            Interaction box = at.getWorld().spawn(at, Interaction.class, e -> {
                e.setPersistent(false);
                e.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "zone");
                e.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, fight);
                e.setInteractionWidth(z.w() * s);
                e.setInteractionHeight(z.h() * s);
                e.setResponsive(true);
            });
            zoneIndex.put(box.getUniqueId(), i);
            zones.add(box);
        }
    }

    /** The zone a hit box stands for, or null when it is not one of this model's. */
    ModelRig.Zone zone(Entity box) {
        Integer i = zoneIndex.get(box.getUniqueId());
        return i == null ? null : model.zones.get(i);
    }

    /** Moves each hit box to where its bone is now. */
    private void placeZones() {
        if (bones == null || zones.isEmpty()) return;
        Location base = mob.getLocation();
        float s = model.scale / 16f, r = ModelRig.rad(yaw);
        Matrix4f turn = new Matrix4f().rotationY(-r);
        for (int i = 0; i < zones.size(); i++) {
            Interaction box = zones.get(i);
            if (!box.isValid()) continue;
            ModelRig.Zone z = model.zones.get(i);
            Vector3f p = bones[z.bone()].transformPosition(new Vector3f(z.center())).mul(s);
            turn.transformPosition(p);
            Location to = new Location(base.getWorld(), base.getX() + p.x, base.getY() + p.y - z.h() * s / 2, base.getZ() + p.z);
            Location at = box.getLocation();
            if (at.getWorld() == to.getWorld() && at.distanceSquared(to) < 0.01) continue;
            if (Bukkit.isOwnedByCurrentRegion(box)) box.teleportAsync(to);
            else box.getScheduler().run(plugin, t -> box.teleportAsync(to), null);
        }
    }

    private void removeZones() {
        for (Interaction box : zones) {
            if (!box.isValid()) continue;
            try {
                if (Bukkit.isOwnedByCurrentRegion(box)) box.remove(); else box.getScheduler().run(plugin, t -> box.remove(), null);
            } catch (RuntimeException ignored) { }
        }
    }

    /** Measures where the blocks ride, plays the spawn steps, then starts the live loop and calls ready. */
    void appear(Runnable ready) {
        mob.getScheduler().runDelayed(plugin, t -> {
            if (!mob.isValid() || parts.isEmpty()) { ready.run(); return; }
            measure();
            restPose();
            play(model.spawn, mob, () -> { startLoop(); ready.run(); });
        }, null, 3);
    }

    private void measure() {
        Location m = mob.getLocation();
        yaw = m.getYaw();
        Location d = parts.get(0).getLocation();
        Vector3f world = new Vector3f((float) (d.getX() - m.getX()), (float) (d.getY() - m.getY()), (float) (d.getZ() - m.getZ()));
        // Store the offset in the mob's own frame; it turns with the mob.
        new Matrix4f().rotationY(ModelRig.rad(yaw)).transformDirection(world, attach);
        last = m;
    }

    private void restPose() {
        ModelRig.Anim idle = model.anim("idle");
        bones = ModelRig.pose(model, List.of(new ModelRig.Layer(idle, 0, 1)));
        Matrix4f[] cubes = ModelRig.cubes(model, bones);
        System.arraycopy(cubes, 0, pose, 0, cubes.length);
        placeZones();
    }

    private Matrix4f world() {
        float r = ModelRig.rad(yaw);
        Vector3f off = new Matrix4f().rotationY(-r).transformDirection(new Vector3f(attach));
        return new Matrix4f().translation(-off.x, -off.y, -off.z).rotateY(-r);
    }

    // ------------------------------------------------------------------ live

    private void startLoop() {
        if (dying || gone) return;
        live = true;
        loop = mob.getScheduler().runAtFixedRate(plugin, t -> { if (!update()) t.cancel(); }, null, 1, PERIOD);
    }

    void attack(String name) {
        ModelRig.Anim a = model.anim(name);
        if (a == null || !live) return;
        attack = a; attackT = 0; animationsPlayed++;
    }

    void hurt() { if (hurtT > 0.25f) hurtT = 0; }

    /** One live frame. False stops the loop. */
    private boolean update() {
        if (!live || dying || gone) return false;
        if (!mob.isValid()) return false;
        Location now = mob.getLocation();
        double dx = now.getX() - last.getX(), dz = now.getZ() - last.getZ();
        double speed = Math.sqrt(dx * dx + dz * dz) / PERIOD;
        last = now;
        float target = speed > 0.025 ? 1 : 0;
        walkW += Math.max(-0.35f, Math.min(0.35f, target - walkW));
        idleT += DT;
        walkT += DT * (float) Math.max(0.6, Math.min(2.2, speed / 0.12));
        hurtT += DT;
        if (attack != null && (attackT += DT) > attack.length()) attack = null;
        // Melee: swing when the target is in reach; the vanilla attack lands about then.
        if (attack == null && model.melee != null && idleT - lastMelee > 1.4f && mob.getTarget() instanceof LivingEntity target2
                && target2.getWorld().equals(now.getWorld()) && target2.getLocation().distanceSquared(now) < Math.pow(Math.max(2.6, model.blocks() * 0.55), 2)) {
            lastMelee = idleT;
            attack(model.melee);
            ModelRig.Anim swing = model.anim(model.melee);
            double reach = Math.max(2.6, model.blocks() * 0.55);
            if (swing != null && meleeDamage > 0) mob.getScheduler().runDelayed(plugin, t -> {
                if (!live || !mob.isValid() || !target2.isValid() || !target2.getWorld().equals(mob.getWorld())) return;
                double d = target2.getLocation().distanceSquared(mob.getLocation());
                // close in, the mob's own attack already lands
                if (d > 1.8 * 1.8 && d < reach * reach && Bukkit.isOwnedByCurrentRegion(target2)) target2.damage(meleeDamage, mob);
            }, null, Math.max(1, Math.round(swing.hit() * 20)));
        }
        float turn = now.getYaw() - yaw;
        yaw = now.getYaw();
        if (++viewerCheck % 7 == 1) {
            double near = Double.MAX_VALUE;
            for (var p : now.getNearbyPlayers(96)) near = Math.min(near, p.getLocation().distanceSquared(now));
            visible = force || near < Double.MAX_VALUE;
            stride = force || near < 28 * 28 ? 1 : 2;
        }
        if (!visible) return true;
        if (++frame % stride != 0 && Math.abs(turn) <= 90 && attackT > DT * 2) return true;
        List<ModelRig.Layer> layers = new ArrayList<>(4);
        layers.add(new ModelRig.Layer(model.anim("idle"), idleT, 1));
        if (walkW > 0.01f) layers.add(new ModelRig.Layer(model.anim("walk"), walkT, walkW));
        if (attack != null) {
            float w = Math.min(1, Math.min(attackT / 0.12f, (attack.length() - attackT) / 0.18f));
            layers.add(new ModelRig.Layer(attack, attackT, Math.max(0, w)));
        }
        if (hurtT < 0.35f) layers.add(new ModelRig.Layer(model.anim("hurt"), hurtT, 1));
        bones = ModelRig.pose(model, layers);
        Matrix4f[] cubes = ModelRig.cubes(model, bones);
        System.arraycopy(cubes, 0, pose, 0, cubes.length);
        send(Math.abs(turn) > 90 ? 1 : PERIOD * stride);
        if (frame % 2 == 0 || stride == 1) placeZones();
        return true;
    }

    private void send(int duration) {
        Matrix4f w = world();
        for (int i = 0; i < parts.size(); i++) send(i, w, duration);
    }

    private void send(int i, Matrix4f w, int duration) {
        BlockDisplay d = parts.get(i);
        if (!d.isValid()) return;
        Transformation t = transformation(new Matrix4f(w).mul(op[i]).mul(pose[i]));
        if (same(t, sent[i])) return;
        sent[i] = t;
        d.setInterpolationDelay(0);
        d.setInterpolationDuration(duration);
        d.setTransformation(t);
    }

    /** translation x rotation x scale, without the shear a general matrix could have. */
    static Transformation transformation(Matrix4f m) {
        Vector3f t = m.getTranslation(new Vector3f());
        Vector3f s = m.getScale(new Vector3f());
        Quaternionf q = s.x < 1e-4f || s.y < 1e-4f || s.z < 1e-4f ? new Quaternionf() : m.getNormalizedRotation(new Quaternionf());
        if (!Float.isFinite(q.x) || !Float.isFinite(q.w)) q = new Quaternionf();
        return new Transformation(t, q, s, new Quaternionf());
    }

    private static boolean same(Transformation a, Transformation b) {
        if (b == null) return false;
        // Plain arithmetic: the JOML bundled with each server version differs, so avoid newer helpers.
        Vector3f ta = a.getTranslation(), tb = b.getTranslation(), sa = a.getScale(), sb = b.getScale();
        Quaternionf qa = a.getLeftRotation(), qb = b.getLeftRotation();
        float dt = sq(ta.x - tb.x) + sq(ta.y - tb.y) + sq(ta.z - tb.z);
        float ds = sq(sa.x - sb.x) + sq(sa.y - sb.y) + sq(sa.z - sb.z);
        float dot = qa.x * qb.x + qa.y * qb.y + qa.z * qb.z + qa.w * qb.w;
        return dt < 1e-6f && ds < 1e-6f && Math.abs(dot) > 0.99999f;
    }

    private static float sq(float v) {
        return v * v;
    }

    // ------------------------------------------------------------------ spawn and death steps

    private record Event(int tick, ModelRig.Step step, int index, int cube) {}

    /**
     * Plays a list of steps. On the mob's scheduler while it lives (spawn), on the region at the spot
     * otherwise (death). Calls done after the last step.
     */
    private void play(List<ModelRig.Step> steps, Entity owner, Runnable done) {
        Matrix4f[] now = new Matrix4f[pose.length];
        for (int i = 0; i < pose.length; i++) now[i] = new Matrix4f(op[i]).mul(pose[i]);
        List<Event> events = new ArrayList<>();
        int end = 0;
        for (int s = 0; s < steps.size(); s++) {
            ModelRig.Step step = steps.get(s);
            end = Math.max(end, step.end());
            if (step.op().equals("fx") || step.op().equals("anim")) { events.add(new Event(step.at(), step, s, -1)); continue; }
            float[] rank = ModelRig.ranks(model, now, step.order(), s * 31L + model.id.hashCode());
            float[] part = step.vec("part");
            for (int i = 0; i < pose.length; i++) {
                if (!model.matches(step.only(), i)) continue;
                if (part != null && (rank[i] < part[0] || rank[i] > part[1] || (rank[i] == part[1] && part[1] < 1))) continue;
                events.add(new Event(step.at() + Math.round(rank[i] * step.stagger()), step, s, i));
            }
        }
        events.sort(java.util.Comparator.comparingInt(Event::tick));
        int finish = end + 2;
        int[] tick = {0};
        int[] next = {0};
        Map<Integer, Integer> dirty = new HashMap<>();
        ModelRig.Anim[] anim = {null};
        int[] animStart = {0}, animEnd = {0};
        Matrix4f[] animBase = {null};
        Consumer<ScheduledTask> body = task -> {
            if (gone) { task.cancel(); return; }
            int k = tick[0]++;
            while (next[0] < events.size() && events.get(next[0]).tick() <= k) {
                Event e = events.get(next[0]++);
                try { apply(e, dirty, anim, animStart, k, animEnd); } catch (RuntimeException ex) { plugin.getLogger().fine("boss model step: " + ex); }
            }
            if (anim[0] != null && (k - animStart[0]) % 2 == 0) {
                float t = (k - animStart[0]) / 20f;
                List<ModelRig.Layer> layers = List.of(new ModelRig.Layer(model.anim("idle"), idleT, 1), new ModelRig.Layer(anim[0], t, 1));
                Matrix4f[] cubes = ModelRig.cubes(model, ModelRig.pose(model, layers));
                System.arraycopy(cubes, 0, pose, 0, cubes.length);
                for (int i = 0; i < pose.length; i++) dirty.merge(i, 2, Math::max);
                if (k >= animEnd[0]) anim[0] = null;
            }
            if (!dirty.isEmpty()) {
                Matrix4f w = world();
                for (var d : dirty.entrySet()) send(d.getKey(), w, d.getValue());
                dirty.clear();
            }
            if (k >= finish) { task.cancel(); done.run(); }
        };
        if (owner != null && owner.isValid()) owner.getScheduler().runAtFixedRate(plugin, body, done, 1, 1);
        else Bukkit.getRegionScheduler().runAtFixedRate(plugin, deathSpot, body, 1, 1);
    }

    private Location deathSpot;

    private void apply(Event e, Map<Integer, Integer> dirty, ModelRig.Anim[] anim, int[] animStart, int k, int[] animEnd) {
        ModelRig.Step s = e.step();
        switch (s.op()) {
            case "fx" -> fx(s);
            case "anim" -> {
                anim[0] = model.anim(s.str("name", ""));
                animStart[0] = k; animEnd[0] = k + Math.max(2, s.dur());
                if (anim[0] != null) animationsPlayed++;
            }
            case "swap" -> {
                String b = s.str("block", "");
                BlockData data = original[e.cube()];
                if (!b.isEmpty()) try { data = Bukkit.createBlockData("minecraft:" + b); } catch (IllegalArgumentException ignored) { }
                BlockDisplay d = parts.get(e.cube());
                if (d.isValid()) d.setBlock(data);
            }
            case "light" -> {
                BlockDisplay d = parts.get(e.cube());
                if (d.isValid()) d.setBrightness(s.flag("on") || model.cubes.get(e.cube()).light() ? new Display.Brightness(15, 15) : null);
            }
            default -> {
                int i = e.cube();
                Matrix4f x = step(s, i, new Random(e.index() * 977L + i * 131L));
                if (x == null) op[i].identity(); else op[i].mulLocal(x);
                dirty.merge(i, Math.max(1, s.dur()), Math::max);
            }
        }
    }

    /** The change a step makes to one cube, in model space (blocks, origin at the feet). Null means back to shape. */
    private Matrix4f step(ModelRig.Step s, int i, Random r) {
        Matrix4f cur = new Matrix4f(op[i]).mul(pose[i]);
        Vector3f c = cur.transformPosition(new Vector3f(0.5f, 0.5f, 0.5f));
        float h = model.blocks();
        return switch (s.op()) {
            case "pose" -> null;
            case "move" -> {
                float[] v = s.vec("v"), vh = s.vec("vh");
                float rand = s.num("rand", 0);
                float x = 0, y = 0, z = 0;
                if (v != null) { x += v[0]; y += v[1]; z += v[2]; }
                if (vh != null) { x += vh[0] * h; y += vh[1] * h; z += vh[2] * h; }
                yield new Matrix4f().translation(x + (r.nextFloat() - 0.5f) * 2 * rand, y + (r.nextFloat() - 0.5f) * rand, z + (r.nextFloat() - 0.5f) * 2 * rand);
            }
            case "drop" -> {
                float minY = Float.MAX_VALUE;
                Vector3f p = new Vector3f();
                for (int k = 0; k < 8; k++) { cur.transformPosition((k & 1), (k >> 1 & 1), (k >> 2 & 1), p); minY = Math.min(minY, p.y); }
                float rand = s.num("rand", 0);
                yield tumble(new Matrix4f().translation((r.nextFloat() - 0.5f) * 2 * rand, -minY + r.nextFloat() * 0.05f, (r.nextFloat() - 0.5f) * 2 * rand), c, s.num("tilt", 0), r);
            }
            case "burst" -> {
                float dx = c.x, dz = c.z, len = (float) Math.sqrt(dx * dx + dz * dz);
                if (len < 0.05f) { double a = r.nextDouble() * Math.PI * 2; dx = (float) Math.cos(a); dz = (float) Math.sin(a); len = 1; }
                float power = s.num("power", 4) * (0.6f + r.nextFloat() * 0.8f), up = s.num("up", 0) * (0.5f + r.nextFloat()), rand = s.num("rand", 0);
                yield tumble(new Matrix4f().translation(dx / len * power + (r.nextFloat() - 0.5f) * rand, up + (r.nextFloat() - 0.5f) * rand,
                        dz / len * power + (r.nextFloat() - 0.5f) * rand), c, s.num("tilt", 0), r);
            }
            case "toward" -> {
                float k = s.num("k", 1), y = s.num("y", 0.5f) * h;
                yield new Matrix4f().translation(-c.x * k, (y - c.y) * k, -c.z * k);
            }
            case "shrink" -> {
                float f = Math.max(0, s.num("s", 0));
                yield new Matrix4f().translation(c).scale(f).translate(-c.x, -c.y, -c.z);
            }
            case "scale" -> {
                float[] v = s.vec("s");
                yield v == null ? new Matrix4f() : new Matrix4f().scaling(v[0], v[1], v[2]);
            }
            case "spin" -> new Matrix4f().rotationY(ModelRig.rad(s.num("deg", 90)));
            case "tilt" -> {
                float[] p = s.vec("pivot");
                Vector3f pv = p == null ? new Vector3f() : new Vector3f(p[0], p[1], p[2]);
                float a = ModelRig.rad(s.num("deg", 90));
                Matrix4f rot = s.str("axis", "x").equals("z") ? new Matrix4f().rotationZ(a) : new Matrix4f().rotationX(a);
                yield new Matrix4f().translation(pv).mul(rot).translate(-pv.x, -pv.y, -pv.z);
            }
            default -> new Matrix4f();
        };
    }

    private static Matrix4f tumble(Matrix4f move, Vector3f c, float tilt, Random r) {
        if (tilt <= 0) return move;
        float a = ModelRig.rad((r.nextFloat() - 0.5f) * 2 * Math.min(170, tilt));
        Vector3f axis = new Vector3f(r.nextFloat() - 0.5f, (r.nextFloat() - 0.5f) * 0.4f, r.nextFloat() - 0.5f);
        if (axis.lengthSquared() < 1e-4f) axis.set(1, 0, 0);
        axis.normalize();
        return move.translate(c).rotate(a, axis).translate(-c.x, -c.y, -c.z);
    }

    // ------------------------------------------------------------------ effects

    private Location origin() {
        Location base = deathSpot != null ? deathSpot.clone() : mob.getLocation();
        return base;
    }

    private void fx(ModelRig.Step s) {
        Location at = origin();
        World world = at.getWorld();
        if (world == null) return;
        Location p = at.clone().add(0, s.num("y", 0.5f) * model.blocks(), 0);
        float spread = s.num("spread", 1);
        String name = s.str("particle", "");
        int count = (int) s.num("count", 30);
        if (!name.isEmpty()) {
            float ring = s.num("ring", 0);
            if (ring > 0) for (int i = 0; i < 40; i++) {
                double a = Math.PI * 2 * i / 40;
                particle(world, at.clone().add(Math.cos(a) * ring, 0.2, Math.sin(a) * ring), name, 1, 0.05, s);
            }
            particle(world, p, name, count, spread, s);
        }
        String sound = s.str("sound", "");
        if (!sound.isEmpty()) sound(world, p, sound, s.num("pitch", 1));
        if (s.flag("lightning")) world.strikeLightningEffect(at);
    }

    private static void particle(World world, Location at, String name, int count, double spread, ModelRig.Step s) {
        Particle particle;
        try { particle = Particle.valueOf(name); } catch (IllegalArgumentException e) { return; }
        Class<?> type = particle.getDataType();
        try {
            if (type == Void.class) world.spawnParticle(particle, at, count, spread, spread, spread, 0.05);
            else if (type == BlockData.class) {
                Material m = Material.matchMaterial(s.str("block", "STONE"));
                world.spawnParticle(particle, at, count, spread, spread, spread, 0.05, (m != null && m.isBlock() ? m : Material.STONE).createBlockData());
            } else if (type == Color.class) world.spawnParticle(particle, at, count, spread, spread, spread, 0, color(s.str("color", "#ffffff")));
            else if (type == Particle.DustOptions.class) world.spawnParticle(particle, at, count, spread, spread, spread, 0, new Particle.DustOptions(color(s.str("color", "#ffffff")), 1.5f));
            else if (type == Float.class) world.spawnParticle(particle, at, count, spread, spread, spread, 0, 0f);
            else if (type == Integer.class) world.spawnParticle(particle, at, count, spread, spread, spread, 0, 0);
        } catch (RuntimeException ignored) { }
    }

    private static Color color(String hex) {
        try { return Color.fromRGB(Integer.parseInt(hex.replace("#", ""), 16) & 0xFFFFFF); } catch (RuntimeException e) { return Color.WHITE; }
    }

    private static final Map<String, Sound> SOUNDS = new java.util.concurrent.ConcurrentHashMap<>();

    /** Sound by its constant name (ENTITY_WITHER_SPAWN); one missing on this server version is skipped. */
    static void sound(World world, Location at, String name, float pitch) {
        Sound sound = SOUNDS.computeIfAbsent(name, n -> {
            try { return (Sound) Sound.class.getField(n).get(null); } catch (ReflectiveOperationException | RuntimeException e) { return null; }
        });
        if (sound != null) world.playSound(at, sound, 2f, pitch);
    }

    // ------------------------------------------------------------------ ending

    /** The death steps: the blocks leave the mob and play out where it fell, then disappear. On the mob's region. */
    void die(Runnable done) {
        if (dying || gone) { done.run(); return; }
        dying = true; live = false;
        if (loop != null) loop.cancel();
        deathSpot = mob.getLocation();
        yaw = deathSpot.getYaw();
        for (BlockDisplay d : parts) if (d.isValid()) mob.removePassenger(d);
        removeZones();
        play(model.death, null, () -> { remove(); done.run(); });
    }

    /** Leaving without a fight: the blocks shrink away. */
    void vanish() {
        if (dying || gone) return;
        dying = true; live = false;
        if (loop != null) loop.cancel();
        removeZones();
        Runnable shrink = () -> {
            Matrix4f w = world();
            for (int i = 0; i < parts.size(); i++) {
                Matrix4f cur = new Matrix4f(op[i]).mul(pose[i]);
                Vector3f c = cur.transformPosition(new Vector3f(0.5f, 0.5f, 0.5f));
                op[i].mulLocal(new Matrix4f().translation(c).scale(0).translate(-c.x, -c.y, -c.z));
                send(i, w, 10);
            }
        };
        if (mob.isValid()) {
            mob.getScheduler().run(plugin, t -> { shrink.run(); mob.getScheduler().runDelayed(plugin, t2 -> remove(), this::remove, 12); }, this::remove);
        } else remove();
    }

    /** Removes every block now (shutdown, or the end of an animation). */
    void remove() {
        gone = true; live = false;
        if (loop != null) loop.cancel();
        removeZones();
        for (BlockDisplay d : parts) {
            if (!d.isValid()) continue;
            try {
                if (Bukkit.isOwnedByCurrentRegion(d)) d.remove(); else d.getScheduler().run(plugin, t -> d.remove(), null);
            } catch (RuntimeException ignored) { }
        }
    }
}
