package com.cbosses.model;

import com.cbosses.fight.Privacy;

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
public final class BossModel {
    /** Ticks between live updates (effects.model-update-ticks); far from players it doubles. */
    public static volatile int period = 3;
    /** Most shards one death may throw (effects.max-shards). */
    public static volatile int maxShards = 48;
    /** Players further than this see no updates at all (effects.model-view-distance). */
    public static volatile int viewDistance = 96;

    public final ModelRig.Model model;
    private final Plugin plugin;
    private final Mob mob;
    private final List<BlockDisplay> parts = new ArrayList<>();
    /** Pieces thrown by shatter steps; they are not part of the body. */
    private final List<BlockDisplay> shards = new ArrayList<>();
    /** One invisible hit box per zone of the body (head, weak spot, arms...), moved with its bone. */
    private final List<Interaction> zones = new ArrayList<>();
    private final Map<UUID, Integer> zoneIndex = new java.util.concurrent.ConcurrentHashMap<>();
    private Matrix4f[] bones;
    /** Far from every player the model updates half as often; the client blends over the longer gap. */
    private int frame, stride = 1;
    private final BlockData[] original, current;
    private final Matrix4f[] pose, op;
    private final Transformation[] sent;
    private final boolean[] outsideCull;
    private final Random random = new Random();

    private final Vector3f attach = new Vector3f();
    private float yaw;
    private float idleT, walkT, walkW, attackT, hurtT = 99, lastMelee = -99;
    private ModelRig.Anim attack;
    private Location last;
    private boolean live, dying, gone, visible = true;
    private int viewerCheck;
    /** The self-test has nobody watching but still wants every update sent. */
    public volatile boolean force;
    /** Set by the fight for flying bosses: the walk cycle becomes the rig's fly cycle when it has one. */
    public volatile boolean flying;
    /** Damage of a melee swing that lands beyond the mob's own short reach (its hitbox is smaller than the model). */
    public volatile double meleeDamage;
    private ScheduledTask loop;
    public int animationsPlayed;

    public BossModel(Plugin plugin, ModelRig.Model model, Mob mob) {
        this.plugin = plugin; this.model = model; this.mob = mob;
        int n = model.cubes.size();
        original = new BlockData[n]; current = new BlockData[n];
        pose = new Matrix4f[n]; op = new Matrix4f[n]; sent = new Transformation[n]; outsideCull = new boolean[n];
        for (int i = 0; i < n; i++) op[i] = new Matrix4f();
    }

    public int blocks() { return parts.size(); }
    public int zoneCount() { int n = 0; for (Interaction z : zones) if (z.isValid()) n++; return n; }
    public boolean dying() { return dying; }
    public boolean live() { return live; }

    /** Spawns the hidden blocks on the mob. Runs on the mob's region. */
    public void build(NamespacedKey kindKey, NamespacedKey fightKey, String fight) {
        Location at = mob.getLocation();
        at.setYaw(0); at.setPitch(0);
        // view range 1 is about 64 blocks; a boss is seen a little further than a normal mob, no more
        float range = Math.max(0.75f, Math.min(1.5f, model.blocks() / 5f));
        float cull = model.blocks() + 2f;
        Transformation hidden = new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(), new Quaternionf());
        for (int i = 0; i < model.cubes.size(); i++) {
            ModelRig.Cube c = model.cubes.get(i);
            BlockData data;
            try { data = Bukkit.createBlockData(c.block().contains(":") ? c.block() : "minecraft:" + c.block()); }
            catch (IllegalArgumentException e) {
                Material m = Material.matchMaterial(c.base());
                data = (m != null && m.isBlock() ? m : Material.STONE).createBlockData();
            }
            original[i] = data; current[i] = data;
            BlockData d0 = data;
            BlockDisplay d = at.getWorld().spawn(at, BlockDisplay.class, e -> { Privacy.claim(e);
                e.setPersistent(false);
                e.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "part");
                e.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, fight);
                e.setBlock(d0);
                e.setTransformation(hidden);
                e.setViewRange(range);
                // the client hides a display whose box is off screen; a box as big as the boss keeps the head
                // and every far piece drawn when you look up at it, not only while its feet are in view
                e.setDisplayWidth(cull * 2f);
                e.setDisplayHeight(cull + 1f);
                e.setShadowRadius(0);
                if (c.light()) e.setBrightness(new Display.Brightness(15, 15));
            });
            mob.addPassenger(d);
            parts.add(d);
        }
        float s = model.scale / 16f;
        for (int i = 0; i < model.zones.size(); i++) {
            ModelRig.Zone z = model.zones.get(i);
            Interaction box = at.getWorld().spawn(at, Interaction.class, e -> { Privacy.claim(e);
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
    public ModelRig.Zone zone(Entity box) {
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
    public void appear(Runnable ready) {
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
        if (model.faceOf != null) model.showFace(pose, "idle");
        placeZones();
    }

    private Matrix4f world() {
        float r = ModelRig.rad(yaw);
        Vector3f off = new Matrix4f().rotationY(-r).transformDirection(new Vector3f(attach));
        return new Matrix4f().translation(-off.x, -off.y + drop, -off.z).rotateY(-r);
    }

    /** Per foot ground height (model pixels) and how far the whole body sinks (blocks) on uneven ground. */
    private float[] footGround;
    private float drop;

    /**
     * Looks at the ground under each foot a few times a second: steps up to one block are climbed by the
     * leg bending (IK in ModelRig), and when every foot is lower the body sinks with them, up to 0.6 blocks.
     * At most three block reads a foot, only blocks this region owns.
     */
    private void sampleGround(Location at) {
        int n = model.feet.length;
        if (n == 0) return;
        if (footGround == null) footGround = new float[n];
        if (flying || !mob.isOnGround()) { java.util.Arrays.fill(footGround, 0); drop = 0; return; }
        float s = model.scale / 16f, r = ModelRig.rad(yaw);
        Matrix4f turn = new Matrix4f().rotationY(-r);
        org.bukkit.World w = at.getWorld();
        float low = 0;
        for (int i = 0; i < n; i++) {
            Vector3f p = model.bones.get(model.feet[i]).pivot();
            Vector3f o = turn.transformDirection(new Vector3f(p.x * s - attach.x, 0, p.z * s - attach.z));
            Location spot = new Location(w, at.getX() + o.x, at.getY(), at.getZ() + o.z);
            if (!Bukkit.isOwnedByCurrentRegion(spot)) { footGround[i] = 0; continue; }
            int bx = spot.getBlockX(), by = spot.getBlockY(), bz = spot.getBlockZ();
            double top;
            org.bukkit.block.Block b0 = w.getBlockAt(bx, by, bz);
            if (!b0.isPassable()) top = b0.getBoundingBox().getMaxY();
            else {
                org.bukkit.block.Block b1 = w.getBlockAt(bx, by - 1, bz);
                top = !b1.isPassable() ? b1.getBoundingBox().getMaxY() : by - 1;
            }
            float g = (float) Math.max(-0.6, Math.min(1.0, top - at.getY()));
            low = Math.min(low, g);
            footGround[i] = g;
        }
        drop = low;
        for (int i = 0; i < n; i++) footGround[i] = (footGround[i] - low) / s;
    }

    // ------------------------------------------------------------------ live

    private void startLoop() {
        if (dying || gone) return;
        live = true;
        loop = mob.getScheduler().runAtFixedRate(plugin, t -> { if (!update()) t.cancel(); }, null, 1, Math.max(1, period));
    }

    public void attack(String name) {
        ModelRig.Anim a = model.anim(name);
        if (a == null || !live) return;
        attack = a; attackT = 0; animationsPlayed++;
    }

    public void hurt() { if (hurtT > 0.25f) hurtT = 0; }

    private static final class HealthAttribute {
        static final org.bukkit.attribute.Attribute MAX_HEALTH = maxHealth();
    }
    private static org.bukkit.attribute.Attribute maxHealth() {
        var a = org.bukkit.Registry.ATTRIBUTE.get(org.bukkit.NamespacedKey.minecraft("max_health"));
        return a != null ? a : org.bukkit.Registry.ATTRIBUTE.get(org.bukkit.NamespacedKey.minecraft("generic.max_health"));
    }

    /** Which face a face-changing model shows right now: hurt when hit, angry while attacking, rage below half health. */
    private String face() {
        if (hurtT < 0.5f) return "hurt";
        if (attack != null) return "angry";
        var max = HealthAttribute.MAX_HEALTH == null ? null : mob.getAttribute(HealthAttribute.MAX_HEALTH);
        if (max != null && mob.getHealth() < max.getValue() * 0.5) return "rage";
        return "idle";
    }

    /** One live frame. False stops the loop. */
    private boolean update() {
        if (!live || dying || gone) return false;
        if (!mob.isValid()) return false;
        final int PERIOD = Math.max(1, period);
        final float DT = PERIOD / 20f;
        Location now = mob.getLocation();
        double dx = now.getX() - last.getX(), dz = now.getZ() - last.getZ();
        double speed = Math.sqrt(dx * dx + dz * dz) / PERIOD;
        last = now;
        float target = speed > 0.025 ? 1 : 0;
        walkW = MotionBlend.approach(walkW, target, DT, 0.18f);
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
        // Follow the shortest arc through +/-180 rather than spinning a whole turn.
        float heading = !flying && speed > 0.025
                ? (float) Math.toDegrees(Math.atan2(-dx, dz)) : now.getYaw();
        float turn = MotionBlend.turn(yaw, heading, DT);
        yaw += turn;
        if (++viewerCheck % 7 == 1) {
            double near = Double.MAX_VALUE;
            for (var p : now.getNearbyPlayers(Math.max(32, viewDistance))) near = Math.min(near, p.getLocation().distanceSquared(now));
            visible = force || near < Double.MAX_VALUE;
            stride = force || near < 28 * 28 ? 1 : 2;
        }
        if (!visible) return true;
        if (++frame % stride != 0 && Math.abs(turn) < 6 && (attack == null || attackT > DT * 2) && hurtT > DT * 2) return true;
        List<ModelRig.Layer> layers = new ArrayList<>(4);
        layers.add(new ModelRig.Layer(model.anim("idle"), idleT, 1));
        ModelRig.Anim fly = flying ? model.anim("fly") : null;
        if (fly != null) layers.add(new ModelRig.Layer(fly, idleT, 1));
        else if (walkW > 0.01f) layers.add(new ModelRig.Layer(model.anim("walk"), walkT, walkW));
        if (attack != null) {
            float w = MotionBlend.envelope(attackT, attack.length(), 0.12f, 0.18f);
            layers.add(new ModelRig.Layer(attack, attackT, Math.max(0, w)));
        }
        ModelRig.Anim hurt = model.anim("hurt");
        if (hurt != null && hurtT < hurt.length())
            layers.add(new ModelRig.Layer(hurt, hurtT, MotionBlend.envelope(hurtT, hurt.length(), 0.04f, 0.14f)));
        if (model.feet.length > 0 && frame % 4 == 0) sampleGround(now);
        bones = ModelRig.pose(model, layers, footGround);
        Matrix4f[] cubes = ModelRig.cubes(model, bones);
        System.arraycopy(cubes, 0, pose, 0, cubes.length);
        for (int i = 0; i < model.entranceOnly.length && i < pose.length; i++) if (model.entranceOnly[i]) pose[i] = new Matrix4f().scale(0);
        if (model.faceOf != null) model.showFace(pose, face());
        send(PERIOD * stride);
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
        Matrix4f posed = new Matrix4f(w).mul(op[i]).mul(pose[i]);
        Transformation t = transformation(posed);
        boolean outside = Displays.outsideDisplayBox(posed, model.blocks()+2, model.blocks()+3);
        // Keep the old pose visible throughout interpolation too. Normal parts
        // retain frustum culling; only displaced parts need its zero-height opt-out.
        float cullHeight = outside || outsideCull[i] ? 0 : model.blocks()+3;
        outsideCull[i] = outside;
        if (d.getDisplayHeight() != cullHeight) d.setDisplayHeight(cullHeight);
        // The carrier may update passenger yaw even when the pose did not change.
        if (d.getYaw() != 0 || d.getPitch() != 0) d.setRotation(0, 0);
        if (same(t, sent[i])) return;
        sent[i] = t;
        d.setInterpolationDelay(0);
        boolean visibilityCut = sentVisibilityChanged(t, d.getTransformation());
        d.setInterpolationDuration(visibilityCut ? 0 : duration);
        // Some carriers rotate their passengers. All yaw belongs to world(), exactly once.
        d.setTransformation(t);
    }

    private static boolean sentVisibilityChanged(Transformation a, Transformation b) {
        boolean hiddenA = a.getScale().lengthSquared() < 1e-10f;
        boolean hiddenB = b.getScale().lengthSquared() < 1e-10f;
        return hiddenA != hiddenB;
    }

    /** translation x rotation x scale, without the shear a general matrix could have. */
    public static Transformation transformation(Matrix4f m) { return Displays.transformation(m); }

    private static boolean same(Transformation a, Transformation b) {
        if (b == null) return false;
        // Plain arithmetic: the JOML bundled with each server version differs, so avoid newer helpers.
        Vector3f ta = a.getTranslation(), tb = b.getTranslation(), sa = a.getScale(), sb = b.getScale();
        Quaternionf ra = a.getRightRotation(), rb = b.getRightRotation();
        if (Math.abs(ra.x * rb.x + ra.y * rb.y + ra.z * rb.z + ra.w * rb.w) < 0.99999f) return false;
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
        later.clear(); horizon = 0;
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
            List<java.util.function.Consumer<Map<Integer, Integer>>> due = later.remove(k);
            if (due != null) for (var run : due) {
                try { run.accept(dirty); } catch (RuntimeException ex) { plugin.getLogger().fine("boss model keyframe: " + ex); }
            }
            if (anim[0] != null && (k - animStart[0]) % 2 == 0) {
                float t = (k - animStart[0]) / 20f;
                List<ModelRig.Layer> layers = List.of(new ModelRig.Layer(model.anim("idle"), idleT, 1), new ModelRig.Layer(anim[0], t, 1));
                Matrix4f[] cubes = ModelRig.cubes(model, ModelRig.pose(model, layers));
                System.arraycopy(cubes, 0, pose, 0, cubes.length);
                if (model.faceOf != null) model.showFace(pose, dying ? "dead" : "idle");
                for (int i = 0; i < pose.length; i++) dirty.merge(i, 2, Math::max);
                if (k >= animEnd[0]) anim[0] = null;
            }
            if (!dirty.isEmpty()) {
                Matrix4f w = world();
                for (var d : dirty.entrySet()) send(d.getKey(), w, d.getValue());
                dirty.clear();
            }
            if (k >= finish && k >= horizon) { task.cancel(); done.run(); }
        };
        if (owner != null && owner.isValid()) owner.getScheduler().runAtFixedRate(plugin, body, done, 1, 1);
        else Bukkit.getRegionScheduler().runAtFixedRate(plugin, deathSpot, body, 1, 1);
    }

    private Location deathSpot;
    /** Keyframes of the steps that move in several parts (fling, shatter, flash, shake), by tick. */
    private final Map<Integer, List<java.util.function.Consumer<Map<Integer, Integer>>>> later = new HashMap<>();
    private int horizon;

    private void at(int tick, java.util.function.Consumer<Map<Integer, Integer>> run) {
        later.computeIfAbsent(tick, t -> new ArrayList<>()).add(run);
        horizon = Math.max(horizon, tick + 1);
    }

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
                current[e.cube()] = data;
                BlockDisplay d = parts.get(e.cube());
                if (d.isValid()) d.setBlock(data);
            }
            case "flash" -> flash(e, k);
            case "shake" -> shake(e, k);
            case "shatter" -> shatter(e, k, dirty);
            case "fling" -> thrown(e, k, false, s.num("power", 4), s.num("up", 2), s.num("tilt", 120));
            case "burst" -> {
                if (s.dur() > 2) thrown(e, k, false, s.num("power", 4), s.num("up", 0) + 0.4f, s.num("tilt", 0));
                else { int i = e.cube(); op[i].mulLocal(step(s, i, new Random(e.index() * 977L + i * 131L))); dirty.merge(i, Math.max(1, s.dur()), Math::max); }
            }
            case "drop" -> {
                if (s.dur() > 2) thrown(e, k, true, s.num("rand", 0) * 1.4f, 0, s.num("tilt", 0));
                else { int i = e.cube(); op[i].mulLocal(step(s, i, new Random(e.index() * 977L + i * 131L))); dirty.merge(i, Math.max(1, s.dur()), Math::max); }
            }
            case "light" -> {
                BlockDisplay d = parts.get(e.cube());
                if (d.isValid()) d.setBrightness((s.params().has("on") ? s.flag("on") : model.cubes.get(e.cube()).light()) ? new Display.Brightness(15, 15) : null);
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

    /** Lowest point of a cube, in model blocks above the feet. */
    private static float lowest(Matrix4f m) {
        float minY = Float.MAX_VALUE;
        Vector3f p = new Vector3f();
        for (int k = 0; k < 8; k++) { m.transformPosition((k & 1), (k >> 1 & 1), (k >> 2 & 1), p); minY = Math.min(minY, p.y); }
        return minY;
    }

    /**
     * A block thrown in an arc: it flies outward, rises and falls with gravity, lands on the floor,
     * bounces once and settles, tumbling the whole way. Sent as a few keyframes the client blends.
     */
    private void thrown(Event e, int k, boolean drop, float power, float up, float tilt) {
        ModelRig.Step s = e.step();
        int i = e.cube();
        Random r = new Random(e.index() * 977L + i * 131L);
        Matrix4f cur = new Matrix4f(op[i]).mul(pose[i]);
        Vector3f c = cur.transformPosition(new Vector3f(0.5f, 0.5f, 0.5f));
        float dx = c.x, dz = c.z, len = (float) Math.sqrt(dx * dx + dz * dz);
        if (len < 0.05f || drop) { double a = r.nextDouble() * Math.PI * 2; dx = (float) Math.cos(a); dz = (float) Math.sin(a); len = 1; }
        float rand = s.num("rand", 0);
        float dist = drop ? power * r.nextFloat() : power * (0.6f + r.nextFloat() * 0.8f) + (r.nextFloat() - 0.5f) * rand;
        float height = drop ? 0 : Math.max(0, up) * (0.5f + r.nextFloat());
        float land = -lowest(cur) + 0.01f;
        float bounce = s.num("bounce", drop ? 0.18f : 0.3f);
        float angle = ModelRig.rad((r.nextFloat() - 0.5f) * 2 * Math.min(175, tilt));
        Vector3f axis = new Vector3f(r.nextFloat() - 0.5f, (r.nextFloat() - 0.5f) * 0.4f, r.nextFloat() - 0.5f);
        if (axis.lengthSquared() < 1e-4f) axis.set(1, 0, 0);
        axis.normalize();
        float ux = dx / len, uz = dz / len;
        int dur = Math.max(3, s.dur());
        int segs = Math.max(2, Math.min(5, dur / 3));
        // positions along the arc: t in 0..1 the flight, then a small hop
        List<float[]> keys = new ArrayList<>();
        for (int j = 1; j <= segs; j++) {
            float t = (float) j / segs;
            keys.add(new float[]{Math.round(dur * t), ux * dist * t, land * t * t + 4 * height * t * (1 - t), uz * dist * t, angle * t});
        }
        float hop = bounce * Math.min(1.4f, 0.22f * (height + dist + Math.abs(land)));
        if (hop > 0.05f) {
            int b = Math.max(2, Math.round(dur * 0.22f));
            keys.add(new float[]{dur + b, ux * dist * 1.1f, land + hop, uz * dist * 1.1f, angle * 1.08f});
            keys.add(new float[]{dur + b * 2, ux * dist * 1.18f, land, uz * dist * 1.18f, angle * 1.12f});
        }
        Matrix4f[] prev = {new Matrix4f()};
        int[] last = {0};
        for (float[] key : keys) {
            int when = (int) key[0];
            int gap = Math.max(1, when - last[0]);
            last[0] = when;
            Matrix4f m = new Matrix4f().translation(key[1], key[2], key[3]).translate(c).rotate(key[4], axis).translate(-c.x, -c.y, -c.z);
            at(k + when, dirty -> {
                Matrix4f delta = new Matrix4f(m).mul(new Matrix4f(prev[0]).invert());
                op[i].mulLocal(delta);
                prev[0] = m;
                dirty.merge(i, gap, Math::max);
            });
        }
    }

    /** Every block turns white (or the step's block) and full bright for a moment, like a hit flash. */
    private void flash(Event e, int k) {
        int i = e.cube();
        BlockDisplay d = parts.get(i);
        if (!d.isValid()) return;
        BlockData to;
        try { to = Bukkit.createBlockData("minecraft:" + e.step().str("block", "white_concrete")); } catch (IllegalArgumentException ex) { return; }
        d.setBlock(to);
        d.setBrightness(new Display.Brightness(15, 15));
        at(k + Math.max(1, e.step().dur()), dirty -> {
            if (!d.isValid()) return;
            d.setBlock(current[i]);
            d.setBrightness(model.cubes.get(i).light() ? new Display.Brightness(15, 15) : null);
        });
    }

    /** The whole model trembles: every block gets the same small jolt every two ticks, then settles. */
    private void shake(Event e, int k) {
        int i = e.cube();
        ModelRig.Step s = e.step();
        float amp = s.num("amp", 0.06f + 0.025f * model.blocks());
        int dur = Math.max(2, s.dur());
        Vector3f[] prev = {new Vector3f()};
        for (int j = 0; j <= dur; j += 2) {
            Random r = new Random(e.index() * 7919L + j);
            Vector3f jolt = j + 2 > dur ? new Vector3f() : new Vector3f((r.nextFloat() - 0.5f) * 2 * amp, (r.nextFloat() - 0.5f) * amp * 0.6f, (r.nextFloat() - 0.5f) * 2 * amp);
            at(k + j, dirty -> {
                op[i].mulLocal(new Matrix4f().translation(jolt.x - prev[0].x, jolt.y - prev[0].y, jolt.z - prev[0].z));
                prev[0] = jolt;
                dirty.merge(i, 2, Math::max);
            });
        }
    }

    /**
     * The block breaks: it vanishes and a few smaller pieces of it fly out in arcs, bounce, lie on the
     * floor for a moment and shrink away. Limited by effects.max-shards for each death.
     */
    private void shatter(Event e, int k, Map<Integer, Integer> dirty) {
        int i = e.cube();
        ModelRig.Step s = e.step();
        BlockDisplay body = parts.get(i);
        if (!body.isValid()) return;
        Matrix4f cur = new Matrix4f(op[i]).mul(pose[i]);
        Vector3f c = cur.transformPosition(new Vector3f(0.5f, 0.5f, 0.5f));
        // hide the block itself
        op[i].mulLocal(new Matrix4f().translation(c).scale(0).translate(-c.x, -c.y, -c.z));
        dirty.merge(i, 1, Math::max);
        int pieces = Math.max(1, Math.min(8, (int) s.num("pieces", 3)));
        if (shards.size() + pieces > Math.max(0, maxShards)) return;
        Random r = new Random(e.index() * 31L + i * 17L);
        Location base = body.getLocation();
        float power = s.num("power", 3), up = s.num("up", 2.5f);
        int dur = Math.max(4, s.dur()), linger = (int) s.num("linger", 24);
        Matrix4f w = world();
        java.util.Set<Integer> used = new java.util.HashSet<>();
        for (int p = 0; p < pieces; p++) {
            int corner;
            do corner = r.nextInt(8); while (!used.add(corner) && used.size() < 8);
            Matrix4f piece = new Matrix4f(cur).translate((corner & 1) * 0.5f, (corner >> 1 & 1) * 0.5f, (corner >> 2 & 1) * 0.5f).scale(0.5f);
            Vector3f pc = piece.transformPosition(new Vector3f(0.5f, 0.5f, 0.5f));
            float dx = pc.x + (r.nextFloat() - 0.5f) * 0.6f, dz = pc.z + (r.nextFloat() - 0.5f) * 0.6f, len = (float) Math.sqrt(dx * dx + dz * dz);
            if (len < 0.05f) { dx = 1; dz = 0; len = 1; }
            float ux = dx / len, uz = dz / len;
            float dist = power * (0.5f + r.nextFloat()), height = up * (0.4f + r.nextFloat() * 0.9f), land = -lowest(piece) + 0.01f;
            float spin = ModelRig.rad((r.nextFloat() - 0.5f) * 520);
            Vector3f axis = new Vector3f(r.nextFloat() - 0.5f, r.nextFloat() - 0.5f, r.nextFloat() - 0.5f);
            if (axis.lengthSquared() < 1e-4f) axis.set(0, 1, 0);
            axis.normalize();
            BlockData data = current[i];
            BlockDisplay shard;
            try {
                shard = base.getWorld().spawn(base, BlockDisplay.class, d -> { Privacy.claim(d);
                    d.setPersistent(false);
                    d.setBlock(data);
                    d.setShadowRadius(0);
                    d.setViewRange(body.getViewRange());
                    d.setTransformation(transformation(new Matrix4f(w).mul(piece)));
                    if (model.cubes.get(i).light()) d.setBrightness(new Display.Brightness(15, 15));
                });
            } catch (RuntimeException ex) { return; }
            shards.add(shard);
            int segs = 3;
            int lastT = 0;
            for (int j = 1; j <= segs + 2; j++) {
                float t = Math.min(1, (float) j / segs);
                int when = j <= segs ? Math.round(dur * t) : dur + (j - segs) * 3;
                float bx = ux * dist * (j <= segs ? t : 1 + 0.08f * (j - segs));
                float by = j <= segs ? land * t * t + 4 * height * t * (1 - t) : land + (j == segs + 1 ? 0.25f * height * 0.3f : 0);
                float bz = uz * dist * (j <= segs ? t : 1 + 0.08f * (j - segs));
                float ang = spin * (j <= segs ? t : 1.1f);
                Matrix4f m = new Matrix4f(w).translate(bx, by, bz).translate(pc).rotate(ang, axis).translate(-pc.x, -pc.y, -pc.z).mul(piece);
                int gap = Math.max(1, when - lastT);
                lastT = when;
                at(k + when, dd -> send(shard, m, gap));
            }
            int gone = dur + 6 + linger + r.nextInt(10);
            Matrix4f small = new Matrix4f(w).translate(ux * dist * 1.16f, land, uz * dist * 1.16f).translate(pc).scale(0.01f).translate(-pc.x, -pc.y, -pc.z).mul(piece);
            at(k + gone, dd -> send(shard, small, 8));
            at(k + gone + 9, dd -> { if (shard.isValid()) shard.remove(); });
        }
    }

    private static void send(BlockDisplay d, Matrix4f m, int duration) {
        if (!d.isValid()) return;
        d.setInterpolationDelay(0);
        d.setInterpolationDuration(duration);
        d.setTransformation(transformation(m));
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
        int count = (int) Math.round(s.num("count", 30) * com.cbosses.fight.Fx.particles);
        if (!name.isEmpty() && count > 0) {
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
            if (type == Void.class) Privacy.particle(world, particle, at, count, spread, spread, spread, 0.05);
            else if (type == BlockData.class) {
                Material m = Material.matchMaterial(s.str("block", "STONE"));
                Privacy.particle(world, particle, at, count, spread, spread, spread, 0.05, (m != null && m.isBlock() ? m : Material.STONE).createBlockData());
            } else if (type == Color.class) Privacy.particle(world, particle, at, count, spread, spread, spread, 0, color(s.str("color", "#ffffff")));
            else if (type == Particle.DustOptions.class) Privacy.particle(world, particle, at, count, spread, spread, spread, 0, new Particle.DustOptions(color(s.str("color", "#ffffff")), 1.5f));
            else if (type == Float.class) Privacy.particle(world, particle, at, count, spread, spread, spread, 0, 0f);
            else if (type == Integer.class) Privacy.particle(world, particle, at, count, spread, spread, spread, 0, 0);
        } catch (RuntimeException ignored) { }
    }

    private static Color color(String hex) {
        try { return Color.fromRGB(Integer.parseInt(hex.replace("#", ""), 16) & 0xFFFFFF); } catch (RuntimeException e) { return Color.WHITE; }
    }

    /** Empty when this server version does not have the sound. Kept lazy so the class loads without a server. */
    private static final Map<String, java.util.Optional<Sound>> SOUNDS = new java.util.concurrent.ConcurrentHashMap<>();

    /** Sound by its constant name (ENTITY_WITHER_SPAWN); one missing on this server version is skipped. */
    public static void sound(World world, Location at, String name, float pitch) { sound(world, at, name, pitch, 2f); }

    public static void sound(World world, Location at, String name, float pitch, float volume) {
        if (name == null || name.isEmpty() || world == null) return;
        java.util.Optional<Sound> sound = SOUNDS.computeIfAbsent(name, n -> {
            try { return java.util.Optional.ofNullable((Sound) Sound.class.getField(n).get(null)); }
            catch (ReflectiveOperationException | RuntimeException e) { return java.util.Optional.empty(); }
        });
        sound.ifPresent(s -> Privacy.sound(world, at, s, volume, pitch));
    }

    // ------------------------------------------------------------------ ending

    /** The death steps: the blocks leave the mob and play out where it fell, then disappear. On the mob's region. */
    public void die(Runnable done) {
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
    public void vanish() {
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
    public void remove() {
        gone = true; live = false;
        if (loop != null) loop.cancel();
        removeZones();
        List<BlockDisplay> all = new ArrayList<>(parts);
        all.addAll(shards);
        for (BlockDisplay d : all) {
            if (!d.isValid()) continue;
            try {
                if (Bukkit.isOwnedByCurrentRegion(d)) d.remove(); else d.getScheduler().run(plugin, t -> d.remove(), null);
            } catch (RuntimeException ignored) { }
        }
    }
}
