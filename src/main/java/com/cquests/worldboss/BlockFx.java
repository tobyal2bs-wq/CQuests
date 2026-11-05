package com.cquests.worldboss;

import com.cquests.util.Sched;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Block effects for the big attacks: a shockwave of ground blocks that ripples outward and falls back, and
 * meteors that really fall from the sky, crash and leave broken pieces on the ground for a while.
 *
 * Everything is a block display: no real block is ever placed, broken or changed. Displays are never saved
 * into the world, move by client-side interpolation (the server sends a few keyframes, not one update per
 * tick) and are removed on a timer. A hard cap ({@link #max}, 30 to 50 by default) on the displays alive at
 * once keeps a busy fight from flooding anyone's client; past it an effect falls back to particles.
 */
public final class BlockFx {

    /** Most block displays the effects keep alive at once on the whole server. */
    public static volatile int max = 48;
    private static final AtomicInteger alive = new AtomicInteger();

    private BlockFx() {}

    private static boolean take(int n) {
        while (true) {
            int a = alive.get();
            if (a + n > max) return false;
            if (alive.compareAndSet(a, a + n)) return true;
        }
    }

    private static Material ground(Location at, Material fallback) {
        Block b = at.clone().add(0, -0.5, 0).getBlock();
        for (int i = 0; i < 3 && !b.getType().isSolid(); i++) b = b.getRelative(0, -1, 0);
        Material m = b.getType();
        return m.isSolid() && m.isBlock() && !m.isInteractable() && m != Material.BEDROCK ? m : fallback;
    }

    private static float floorY(Location at) {
        Block b = at.getBlock();
        for (int i = 0; i < 6 && !b.getType().isSolid(); i++) b = b.getRelative(0, -1, 0);
        return b.getType().isSolid() ? b.getY() + 1 : (float) at.getY();
    }

    private static BlockDisplay piece(World w, Location at, Material m, float size, boolean glow) {
        return w.spawn(at, BlockDisplay.class, d -> {
            d.setPersistent(false);
            d.setBlock(m.createBlockData());
            d.setTransformation(new Transformation(new Vector3f(-size / 2, 0, -size / 2), new Quaternionf(), new Vector3f(size), new Quaternionf()));
            d.setViewRange(0.6f);
            d.setShadowRadius(0);
            if (glow) d.setBrightness(new Display.Brightness(15, 15));
        });
    }

    private static void move(BlockDisplay d, int ticks, Vector3f translate, float size, Quaternionf rot) {
        d.setInterpolationDelay(0);
        d.setInterpolationDuration(ticks);
        d.setTransformation(new Transformation(new Vector3f(translate).add(-size / 2, 0, -size / 2), rot, new Vector3f(size), new Quaternionf()));
    }

    private static void later(BlockDisplay d, long ticks, Runnable run) {
        d.getScheduler().runDelayed(com.cquests.util.Sched.owner(), t -> { if (d.isValid()) run.run(); }, null, Math.max(1, ticks));
    }

    private static void gone(BlockDisplay d, long ticks) {
        d.getScheduler().runDelayed(com.cquests.util.Sched.owner(), t -> { if (d.isValid()) d.remove(); alive.decrementAndGet(); }, () -> alive.decrementAndGet(), Math.max(1, ticks));
    }

    /**
     * A ring of the ground's own blocks bursts up around {@code center} and rolls outward to {@code radius},
     * rising and falling like a wave, then sinks away. Up to {@code pieces} displays.
     */
    public static void shockwave(Location center, double radius, int pieces, Material fallback) {
        World w = center.getWorld();
        int n = Math.max(8, Math.min(pieces, 36));
        if (!take(n)) {
            for (int i = 0; i < 36; i++) {
                double a = Math.PI * 2 * i / 36;
                w.spawnParticle(Particle.BLOCK, center.clone().add(Math.cos(a) * radius * 0.6, 0.2, Math.sin(a) * radius * 0.6), 4, 0.2, 0.1, 0.2, ground(center, fallback).createBlockData());
            }
            return;
        }
        Material m = ground(center, fallback);
        float y = floorY(center);
        Location base = center.clone(); base.setY(y - 0.2);
        ThreadLocalRandom r = ThreadLocalRandom.current();
        double turn = r.nextDouble() * Math.PI * 2;
        for (int i = 0; i < n; i++) {
            double a = turn + Math.PI * 2 * i / n;
            float size = 0.7f + r.nextFloat() * 0.35f;
            Location at = base.clone().add(Math.cos(a) * 1.4, 0, Math.sin(a) * 1.4);
            BlockDisplay d = piece(w, at, m, size, false);
            float dx = (float) (Math.cos(a) * (radius - 1.4)), dz = (float) (Math.sin(a) * (radius - 1.4));
            Quaternionf tilt = new Quaternionf(new AxisAngle4f((float) Math.toRadians(25 + r.nextInt(30)), (float) -Math.sin(a), 0, (float) Math.cos(a)));
            later(d, 2, () -> move(d, 5, new Vector3f(dx * 0.45f, 0.9f + r.nextFloat() * 0.5f, dz * 0.45f), size, tilt));
            later(d, 7, () -> move(d, 6, new Vector3f(dx, 0.1f, dz), size * 0.9f, new Quaternionf()));
            later(d, 14, () -> move(d, 6, new Vector3f(dx, -0.8f, dz), 0.05f, new Quaternionf()));
            gone(d, 21);
        }
        w.playSound(center, Sound.BLOCK_ROOTED_DIRT_BREAK, 1.4f, 0.6f);
    }

    /**
     * One meteor: a burning rock falls from high above at an angle, smoke behind it, and crashes at
     * {@code target}; {@code impact} runs when it lands (damage). Broken pieces stay on the ground,
     * still glowing, for {@code linger} ticks and then sink away. About 10 displays.
     */
    public static void meteor(Location target, Material rock, Material core, int linger, Runnable impact) {
        World w = target.getWorld();
        ThreadLocalRandom r = ThreadLocalRandom.current();
        float floor = floorY(target);
        Location land = target.clone(); land.setY(floor);
        double a = r.nextDouble() * Math.PI * 2;
        float sx = (float) (Math.cos(a) * 9), sz = (float) (Math.sin(a) * 9), sy = 26;
        int fall = 22;
        int crust = 4, chunks = 5;
        if (!take(1 + crust)) {
            // Particles only: a falling trail and the crash.
            for (int k = 0; k <= 10; k++) {
                float t = k / 10f;
                Location p = land.clone().add(sx * (1 - t), sy * (1 - t), sz * (1 - t));
                Sched.at(land, () -> w.spawnParticle(Particle.FLAME, p, 6, 0.3, 0.3, 0.3, 0.02));
            }
            Sched.at(land, () -> crash(w, land, rock, impact));
            return;
        }
        Location start = land.clone().add(sx, sy, sz);
        BlockDisplay rockD = piece(w, start, core, 1.7f, true);
        BlockDisplay[] shell = new BlockDisplay[crust];
        for (int k = 0; k < crust; k++) {
            double b = Math.PI * 2 * k / crust;
            shell[k] = piece(w, start.clone().add(Math.cos(b) * 0.55, 0.35 + (k % 2) * 0.7, Math.sin(b) * 0.55), rock, 1.0f, false);
        }
        // the fall: teleport keyframes the client smooths, spinning as it comes
        for (BlockDisplay d : concat(rockD, shell)) {
            d.setTeleportDuration(4);
            Location from = d.getLocation();
            for (int step = 1; step <= fall / 4; step++) {
                float t = Math.min(1, step * 4f / fall);
                float ease = t * t * 0.4f + t * 0.6f;
                Location to = from.clone().add(-sx * ease, -sy * ease, -sz * ease);
                int s = step;
                later(d, step * 4L, () -> {
                    d.teleport(to);
                    move(d, 4, new Vector3f(), d == rockD ? 1.7f : 1.0f, new Quaternionf().rotateXYZ(s * 0.7f, s * 0.4f, s * 0.2f));
                    if (d == rockD) {
                        w.spawnParticle(Particle.FLAME, to.clone().add(0, 0.8, 0), 8, 0.3, 0.3, 0.3, 0.02);
                        w.spawnParticle(Particle.LARGE_SMOKE, to.clone().add(0, 1.2, 0), 4, 0.3, 0.3, 0.3, 0.01);
                    }
                });
            }
            gone(d, fall + 2);
        }
        w.playSound(land, Sound.ENTITY_BLAZE_SHOOT, 1.5f, 0.4f);
        Sched.entityLater(rockD, fall, () -> {
            crash(w, land, rock, impact);
            if (!take(chunks)) return;
            for (int k = 0; k < chunks; k++) {
                double b = r.nextDouble() * Math.PI * 2, dist = 0.6 + r.nextDouble() * 1.8;
                boolean hot = k % 2 == 0;
                float size = 0.35f + r.nextFloat() * 0.35f;
                BlockDisplay c = piece(w, land.clone().add(Math.cos(b) * 0.3, 0.1, Math.sin(b) * 0.3), hot ? core : rock, size, hot);
                Quaternionf rot = new Quaternionf().rotateXYZ(r.nextFloat() * 3, r.nextFloat() * 3, r.nextFloat() * 3);
                float dx = (float) (Math.cos(b) * dist), dz = (float) (Math.sin(b) * dist);
                later(c, 1, () -> move(c, 4, new Vector3f(dx * 0.6f, 0.9f, dz * 0.6f), size, rot));
                later(c, 5, () -> move(c, 4, new Vector3f(dx, -0.05f, dz), size, rot));
                later(c, Math.max(20, linger - 12), () -> move(c, 12, new Vector3f(dx, -0.4f, dz), 0.02f, rot));
                gone(c, Math.max(32, linger));
            }
        });
    }

    private static void crash(World w, Location land, Material rock, Runnable impact) {
        w.spawnParticle(Particle.EXPLOSION, land.clone().add(0, 0.5, 0), 2, 0.4, 0.2, 0.4, 0);
        w.spawnParticle(Particle.LAVA, land.clone().add(0, 0.4, 0), 12, 0.8, 0.2, 0.8, 0);
        w.spawnParticle(Particle.BLOCK, land.clone().add(0, 0.3, 0), 40, 1.2, 0.2, 1.2, rock.createBlockData());
        w.spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, land.clone().add(0, 0.4, 0), 6, 0.6, 0.2, 0.6, 0.02);
        w.playSound(land, Sound.ENTITY_GENERIC_EXPLODE, 1.6f, 0.7f);
        if (impact != null) impact.run();
    }

    private static BlockDisplay[] concat(BlockDisplay a, BlockDisplay[] rest) {
        BlockDisplay[] out = new BlockDisplay[rest.length + 1];
        out[0] = a;
        System.arraycopy(rest, 0, out, 1, rest.length);
        return out;
    }
}
