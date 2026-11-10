package com.cbosses.fight;

import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.block.data.BlockData;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.inventory.ItemStack;
import org.bukkit.plugin.Plugin;
import org.bukkit.util.Transformation;
import org.joml.AxisAngle4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * The effects every boss draws with: particles scaled by the quality setting, telegraph rings that fill
 * up before a hit lands, flying chunks of ground (block displays thrown in arcs that land, roll and
 * shrink away), ground eruptions, spikes, meteors and the loot fountain. Everything here is visual only:
 * no block in the world is ever placed, broken or changed. All of it runs on the region that owns the
 * location, so it is safe on Folia.
 */
public final class Fx {
    private static Plugin plugin;
    /** effects.particles: 1 = full, 0.5 = half, 0 = none. */
    public static volatile double particles = 1;
    /** effects.debris: flying block chunks on or off, and how many may exist at once on the whole server. */
    public static volatile boolean debrisOn = true;
    public static volatile int maxDebris = 160;
    /** effects.view-distance: effects are only sent to players this close. */
    public static volatile int viewDistance = 48;
    private static final AtomicInteger debris = new AtomicInteger();

    private Fx() {}

    public static void init(Plugin owner) { plugin = owner; }

    public static int activeDebris() { return debris.get(); }

    static int n(int count) {
        if (count <= 0) return 0;
        return Math.max(1, (int) Math.round(count * particles));
    }

    /** A particle of any kind; the extra data some particles need (a block, a colour) comes from the theme. */
    public static void particle(World world, Particle particle, Location at, int count, double dx, double dy, double dz, double speed, Theme theme) {
        int c = n(count);
        if (c <= 0 || world == null || particles <= 0) return;
        Class<?> type = particle.getDataType();
        try {
            if (type == Void.class) Privacy.particle(world, particle, at, c, dx, dy, dz, speed);
            else if (type == BlockData.class) Privacy.particle(world, particle, at, c, dx, dy, dz, speed, (theme == null ? Material.STONE : theme.debris()).createBlockData());
            else if (type == Particle.DustOptions.class) Privacy.particle(world, particle, at, c, dx, dy, dz, 0, new Particle.DustOptions(theme == null ? Color.WHITE : theme.main(), 1.5f));
            else if (type == Color.class) Privacy.particle(world, particle, at, c, dx, dy, dz, 0, theme == null ? Color.WHITE : theme.main());
            else if (type == Float.class) Privacy.particle(world, particle, at, c, dx, dy, dz, speed, 0f);
            else if (type == Integer.class) Privacy.particle(world, particle, at, c, dx, dy, dz, speed, 0);
        } catch (RuntimeException ignored) { }
    }

    public static void dust(Location at, Color color, float size, int count, double spread) {
        int c = n(count);
        if (c <= 0) return;
        Privacy.particle(at.getWorld(), Particle.DUST, at, c, spread, spread, spread, 0, new Particle.DustOptions(color, size));
    }

    public static void blockDust(Location at, Material block, int count, double spread) {
        int c = n(count);
        if (c <= 0) return;
        try { Privacy.particle(at.getWorld(), Particle.BLOCK, at, c, spread, 0.2, spread, 0.1, block.createBlockData()); } catch (RuntimeException ignored) { }
    }

    /** A flat ring of coloured dust on the ground. */
    public static void ring(Location center, double radius, Color color, float size, int points) {
        int p = Math.max(8, (int) Math.round(points * Math.max(0.4, particles)));
        Particle.DustOptions dust = new Particle.DustOptions(color, size);
        World w = center.getWorld();
        for (int i = 0; i < p; i++) {
            double a = Math.PI * 2 * i / p;
            Privacy.particle(w, Particle.DUST, center.getX() + Math.cos(a) * radius, center.getY() + 0.15, center.getZ() + Math.sin(a) * radius, 1, 0, 0, 0, 0, dust);
        }
    }

    public static void sound(Location at, String name, float volume, float pitch) {
        com.cbosses.model.BossModel.sound(at.getWorld(), at, name, pitch, volume);
    }

    /** The block under a spot, for the chunks that fly when the ground is hit; the theme's block when it is air or liquid. */
    public static Material ground(Location at, Theme theme) {
        Block b = at.getBlock();
        for (int i = 0; i < 3 && (b.isPassable() || b.isLiquid()); i++) b = b.getRelative(BlockFace.DOWN);
        Material m = b.getType();
        if (b.isPassable() || b.isLiquid() || !m.isSolid() || !m.isBlock()) return theme.debris();
        return m;
    }

    private static void later(Location at, long ticks, Runnable run) {
        Bukkit.getRegionScheduler().runDelayed(plugin, at, t -> run.run(), Math.max(1, ticks));
    }

    // ------------------------------------------------------------------ telegraphs

    /**
     * A warning on the ground: an outer ring in the boss's colour and an inner one that grows to meet it.
     * When they meet the hit lands, so players can read exactly when to get out.
     */
    public static void telegraph(Location center, double radius, Theme theme, int ticks) {
        Location c = center.clone();
        int frames = Math.max(1, ticks / 3);
        Color warn = Color.fromRGB(0xff2a2a);
        for (int f = 0; f <= frames; f++) {
            double p = (double) f / frames;
            later(c, 1 + f * 3L, () -> {
                ring(c, radius, warn, 1.3f, (int) (radius * 7));
                ring(c, Math.max(0.3, radius * p), theme.main(), 1.6f, (int) (radius * 5 * Math.max(0.3, p)));
                if (p > 0.6) particle(c.getWorld(), theme.spark(), c.clone().add(0, 0.2, 0), (int) (radius * 2), radius / 2, 0.05, radius / 2, 0.01, theme);
            });
        }
    }

    /** A warning line from a to b, for charges and beams. */
    public static void lineTelegraph(Location a, Location b, double width, Theme theme, int ticks) {
        Location from = a.clone(), to = b.clone();
        int frames = Math.max(1, ticks / 4);
        for (int f = 0; f <= frames; f++) {
            later(from, 1 + f * 4L, () -> line(from, to, Color.fromRGB(0xff2a2a), 1.2f, width));
        }
    }

    public static void line(Location from, Location to, Color color, float size, double width) {
        double len = from.distance(to);
        int steps = Math.max(2, (int) (len * 2.5 * Math.max(0.4, particles)));
        Particle.DustOptions dust = new Particle.DustOptions(color, size);
        org.bukkit.util.Vector d = to.toVector().subtract(from.toVector());
        org.bukkit.util.Vector side = new org.bukkit.util.Vector(-d.getZ(), 0, d.getX());
        if (side.lengthSquared() > 1e-4) side.normalize().multiply(width / 2);
        World w = from.getWorld();
        for (int i = 0; i <= steps; i++) {
            double t = (double) i / steps;
            Location p = from.clone().add(d.clone().multiply(t)).add(0, 0.15, 0);
            Privacy.particle(w, Particle.DUST, p.clone().add(side), 1, 0, 0, 0, 0, dust);
            Privacy.particle(w, Particle.DUST, p.clone().subtract(side), 1, 0, 0, 0, 0, dust);
        }
    }

    /** A straight beam of particles (sonic boom, breath, lasers). */
    public static void beam(Location from, Location to, Particle particle, Theme theme, double step) {
        double len = from.distance(to);
        org.bukkit.util.Vector d = to.toVector().subtract(from.toVector()).normalize().multiply(step);
        Location p = from.clone();
        for (double t = 0; t <= len; t += step) {
            particle(from.getWorld(), particle, p, 1, 0, 0, 0, 0, theme);
            p.add(d);
        }
    }

    // ------------------------------------------------------------------ flying chunks

    private static boolean take() {
        if (!debrisOn) return false;
        if (debris.incrementAndGet() > Math.max(0, maxDebris)) { debris.decrementAndGet(); return false; }
        return true;
    }

    private static Transformation tf(Vector3f at, float scale, Quaternionf rot) {
        return new Transformation(at, rot, new Vector3f(scale), new Quaternionf());
    }

    /**
     * Chunks of a block thrown up from a spot: each one flies in an arc, lands, rolls a little and shrinks
     * away. {@code power} is how far they fly, {@code up} how high, {@code size} their size in blocks.
     */
    public static void debris(Location at, Material block, int count, double power, double up, float size) {
        if (!block.isBlock()) block = Material.STONE;
        BlockData data;
        try { data = block.createBlockData(); } catch (RuntimeException e) { return; }
        int c = Math.max(1, (int) Math.round(count * Math.max(0.3, particles)));
        ThreadLocalRandom r = ThreadLocalRandom.current();
        for (int i = 0; i < c; i++) {
            if (!take()) return;
            double a = r.nextDouble() * Math.PI * 2, dist = power * (0.4 + r.nextDouble() * 0.8), h = up * (0.5 + r.nextDouble() * 0.8);
            float s = size * (0.6f + r.nextFloat() * 0.7f);
            float dx = (float) (Math.cos(a) * dist), dz = (float) (Math.sin(a) * dist);
            Vector3f axis = new Vector3f(r.nextFloat() - 0.5f, r.nextFloat() - 0.5f, r.nextFloat() - 0.5f).normalize();
            float spin = (float) Math.toRadians(r.nextDouble(200, 600));
            int flight = 8 + r.nextInt(8);
            BlockDisplay d;
            try {
                d = at.getWorld().spawn(at, BlockDisplay.class, e -> { Privacy.claim(e);
                    e.setPersistent(false);
                    e.setBlock(data);
                    e.setShadowRadius(0);
                    e.setViewRange(0.6f);
                    e.setTransformation(tf(new Vector3f(-s / 2, 0, -s / 2), s, new Quaternionf()));
                });
            } catch (RuntimeException e) { debris.decrementAndGet(); return; }
            float half = s / 2;
            // up and out, then down to the floor, a little roll, then shrink
            key(d, 1, flight / 2, tf(new Vector3f(dx * 0.5f - half, (float) h, dz * 0.5f - half), s, new Quaternionf(new AxisAngle4f(spin * 0.5f, axis))));
            key(d, 1 + flight / 2, flight - flight / 2, tf(new Vector3f(dx - half, 0, dz - half), s, new Quaternionf(new AxisAngle4f(spin, axis))));
            key(d, 1 + flight, 6, tf(new Vector3f(dx * 1.12f - half, (float) (h * 0.08), dz * 1.12f - half), s, new Quaternionf(new AxisAngle4f(spin * 1.1f, axis))));
            key(d, 7 + flight, 5, tf(new Vector3f(dx * 1.18f - half, 0, dz * 1.18f - half), s, new Quaternionf(new AxisAngle4f(spin * 1.12f, axis))));
            int linger = 14 + r.nextInt(14);
            key(d, 12 + flight + linger, 8, tf(new Vector3f(dx * 1.18f, s * 0.5f, dz * 1.18f), 0.01f, new Quaternionf(new AxisAngle4f(spin * 1.12f, axis))));
            later(at, 21 + flight + linger, () -> { if (d.isValid()) d.remove(); debris.decrementAndGet(); });
        }
    }

    private static void key(Display d, long delay, int duration, Transformation t) {
        later(d.getLocation(), delay, () -> {
            if (!d.isValid()) return;
            d.setInterpolationDelay(0);
            d.setInterpolationDuration(Math.max(1, duration));
            d.setTransformation(t);
        });
    }

    /**
     * The ground cracks outward in a wave: rings of blocks pop up out of the floor one after another,
     * each ring further out, with dust. Players see a wave racing across the arena.
     */
    public static void eruption(Location center, double radius, Material block, Theme theme, int steps) {
        Location c = center.clone();
        BlockData data;
        try { data = (block.isBlock() ? block : Material.STONE).createBlockData(); } catch (RuntimeException e) { return; }
        int rings = Math.max(2, steps);
        for (int k = 1; k <= rings; k++) {
            double rr = radius * k / rings;
            int count = Math.max(6, (int) (rr * 2.2 * Math.max(0.35, particles)));
            later(c, k * 2L, () -> {
                ThreadLocalRandom r = ThreadLocalRandom.current();
                for (int i = 0; i < count; i++) {
                    double a = Math.PI * 2 * i / count + r.nextDouble() * 0.2;
                    Location spot = c.clone().add(Math.cos(a) * rr, 0, Math.sin(a) * rr);
                    if (Bukkit.isOwnedByCurrentRegion(spot) && take()) {
                        float s = 0.55f + r.nextFloat() * 0.35f;
                        float tilt = (float) Math.toRadians(r.nextDouble(-35, 35));
                        BlockDisplay d;
                        try {
                            d = spot.getWorld().spawn(spot, BlockDisplay.class, e -> { Privacy.claim(e);
                                e.setPersistent(false); e.setBlock(data); e.setShadowRadius(0); e.setViewRange(0.6f);
                                e.setTransformation(tf(new Vector3f(-s / 2, -s, -s / 2), s, new Quaternionf()));
                            });
                        } catch (RuntimeException e) { debris.decrementAndGet(); continue; }
                        key(d, 1, 3, tf(new Vector3f(-s / 2, 0.15f, -s / 2), s, new Quaternionf().rotateY((float) a).rotateX(tilt)));
                        key(d, 10, 8, tf(new Vector3f(-s / 2, -s - 0.1f, -s / 2), s, new Quaternionf().rotateY((float) a)));
                        later(spot, 20, () -> { if (d.isValid()) d.remove(); debris.decrementAndGet(); });
                    }
                    if (i % 3 == 0) {
                        try { Privacy.particle(spot.getWorld(), Particle.BLOCK, spot.clone().add(0, 0.3, 0), n(3), 0.2, 0.1, 0.2, 0.1, data); } catch (RuntimeException ignored) { }
                    }
                }
                if (theme != null) particle(c.getWorld(), theme.spark(), c.clone().add(0, 0.3, 0), (int) (rr * 3), rr * 0.7, 0.1, rr * 0.7, 0.02, theme);
            });
        }
    }

    /** A spike of a block shoots up out of the ground, stays for a moment and sinks back. */
    public static void spike(Location at, Material block, float height, int stay) {
        if (!take()) return;
        BlockData data;
        try { data = (block.isBlock() ? block : Material.POINTED_DRIPSTONE).createBlockData(); } catch (RuntimeException e) { debris.decrementAndGet(); return; }
        float w = 0.55f;
        BlockDisplay d;
        try {
            d = at.getWorld().spawn(at, BlockDisplay.class, e -> { Privacy.claim(e);
                e.setPersistent(false); e.setBlock(data); e.setShadowRadius(0); e.setViewRange(0.6f);
                e.setTransformation(new Transformation(new Vector3f(-w / 2, -height, -w / 2), new Quaternionf(), new Vector3f(w, height, w), new Quaternionf()));
            });
        } catch (RuntimeException e) { debris.decrementAndGet(); return; }
        Quaternionf lean = new Quaternionf().rotateY((float) (Math.random() * Math.PI * 2)).rotateX((float) Math.toRadians(Math.random() * 14 - 7));
        key(d, 1, 3, new Transformation(new Vector3f(-w / 2, 0, -w / 2), lean, new Vector3f(w, height, w), new Quaternionf()));
        key(d, 4 + stay, 8, new Transformation(new Vector3f(-w / 2, -height, -w / 2), lean, new Vector3f(w, height, w), new Quaternionf()));
        later(at, 14 + stay, () -> { if (d.isValid()) d.remove(); debris.decrementAndGet(); });
    }

    /**
     * A block falls out of the sky onto a spot with a trail, then {@code impact} runs where it lands.
     * The block itself stays visual; impact does the damage.
     */
    public static void meteor(Location target, Material block, Theme theme, int fall, float size, Runnable impact) {
        Location t = target.clone();
        double height = 22;
        boolean shown = take();
        BlockData data;
        try { data = (block.isBlock() ? block : Material.MAGMA_BLOCK).createBlockData(); } catch (RuntimeException e) { data = Material.MAGMA_BLOCK.createBlockData(); }
        BlockData d0 = data;
        BlockDisplay[] d = {null};
        if (shown) {
            try {
                d[0] = t.getWorld().spawn(t, BlockDisplay.class, e -> { Privacy.claim(e);
                    e.setPersistent(false); e.setBlock(d0); e.setShadowRadius(0); e.setViewRange(1f);
                    e.setBrightness(new Display.Brightness(15, 15));
                    e.setTransformation(tf(new Vector3f(-size / 2 - 6, (float) height, -size / 2 - 3), size, new Quaternionf()));
                });
            } catch (RuntimeException e) { debris.decrementAndGet(); }
        }
        if (d[0] != null) key(d[0], 1, fall, tf(new Vector3f(-size / 2, 0, -size / 2), size, new Quaternionf().rotateXYZ(2.4f, 1.1f, 0.7f)));
        for (int i = 0; i < fall; i += 2) {
            double p = (double) i / fall;
            later(t, 1 + i, () -> {
                Location trail = t.clone().add(-6 * (1 - p), height * (1 - p) + size / 2, -3 * (1 - p));
                particle(t.getWorld(), theme.spark(), trail, 4, 0.2, 0.2, 0.2, 0.01, theme);
                particle(t.getWorld(), Particle.LARGE_SMOKE, trail, 2, 0.15, 0.15, 0.15, 0.01, theme);
            });
        }
        later(t, fall + 1L, () -> {
            if (d[0] != null && d[0].isValid()) { d[0].remove(); debris.decrementAndGet(); }
            impact.run();
        });
    }

    /** Items spray up from a spot and rain down around it: the loot fountain after a kill. */
    public static void fountain(Location at, java.util.List<Material> items, int count) {
        if (items.isEmpty()) return;
        ThreadLocalRandom r = ThreadLocalRandom.current();
        int c = Math.max(1, (int) Math.round(count * Math.max(0.4, particles)));
        for (int i = 0; i < c; i++) {
            if (!take()) return;
            Material m = items.get(r.nextInt(items.size()));
            if (!m.isItem()) m = Material.GOLD_NUGGET;
            ItemStack stack = new ItemStack(m);
            double a = r.nextDouble() * Math.PI * 2, dist = 1.5 + r.nextDouble() * 4, h = 3 + r.nextDouble() * 4;
            float dx = (float) (Math.cos(a) * dist), dz = (float) (Math.sin(a) * dist);
            float spin = (float) r.nextDouble(3, 9);
            int flight = 14 + r.nextInt(10);
            long delay = i / 3;
            later(at, 1 + delay, () -> {
                ItemDisplay d;
                try {
                    d = at.getWorld().spawn(at.clone().add(0, 1, 0), ItemDisplay.class, e -> { Privacy.claim(e);
                        e.setPersistent(false); e.setItemStack(stack); e.setShadowRadius(0); e.setViewRange(0.6f);
                        e.setBrightness(new Display.Brightness(15, 15));
                        e.setTransformation(tf(new Vector3f(), 0.6f, new Quaternionf()));
                    });
                } catch (RuntimeException e) { debris.decrementAndGet(); return; }
                key(d, 1, flight / 2, tf(new Vector3f(dx * 0.5f, (float) h, dz * 0.5f), 0.7f, new Quaternionf().rotateY(spin * 0.5f)));
                key(d, 1 + flight / 2, flight - flight / 2, tf(new Vector3f(dx, -0.7f, dz), 0.6f, new Quaternionf().rotateY(spin)));
                key(d, 1 + flight + 30, 8, tf(new Vector3f(dx, -0.7f, dz), 0.01f, new Quaternionf().rotateY(spin * 1.5f)));
                later(at, 40 + flight, () -> { if (d.isValid()) d.remove(); debris.decrementAndGet(); });
            });
        }
    }

    /** A column of particles from the ground up. */
    public static void pillar(Location at, Particle particle, Theme theme, double height, double radius) {
        for (double y = 0; y < height; y += 0.6) {
            double a = y * 1.7;
            particle(at.getWorld(), particle, at.clone().add(Math.cos(a) * radius, y, Math.sin(a) * radius), 1, 0.03, 0.03, 0.03, 0, theme);
        }
    }
}
