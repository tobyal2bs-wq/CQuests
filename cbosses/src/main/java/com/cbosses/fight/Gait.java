package com.cbosses.fight;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.util.Vector;

import java.util.Locale;
import java.util.concurrent.ThreadLocalRandom;

/**
 * A walking boss's own way of moving. The mob under the model loses every vanilla goal (no zombie
 * shuffle, no golem wander, no witch potions) and this steers it instead, so each boss moves like
 * itself: stalking, charging, circling, hopping, slithering, lumbering or skittering. The rhythm and
 * distances also differ per boss, taken from its id, so two bosses with the same style still move
 * differently. Holds no references beyond its own mob; it is dropped with the fight.
 */
public final class Gait {
    public enum Style { STALK, CHARGE, CIRCLE, HOP, SLITHER, LUMBER, SKITTER }

    private final Mob mob;
    public final Style style;
    private final double reach, radius;
    private final int rhythm;
    private int beat, side = 1;
    private double angle;
    private long pauseUntil;
    private Location wander;

    public Gait(Mob mob, Style style, String id, double reach) {
        this.mob = mob; this.style = style; this.reach = Math.max(2, reach);
        int h = id.hashCode() & 0x7fffffff;
        this.rhythm = 6 + h % 5;                 // beats between bursts or pauses: 6..10
        this.radius = 3.5 + (h >> 4) % 4;        // circling distance: 3.5..6.5 blocks
        this.angle = (h >> 8) % 360;
    }

    /** Which style a boss gets: the config wins, then its name and mob, then its id. */
    public static Style pick(String id, String configured, EntityType entity) {
        if (configured != null) try { return Style.valueOf(configured.toUpperCase(Locale.ROOT)); } catch (IllegalArgumentException ignored) { }
        String n = id.toLowerCase(Locale.ROOT);
        if (has(n, "serpent", "snake", "eel", "worm", "coil", "basilisk", "wyrm")) return Style.SLITHER;
        if (has(n, "frog", "toad", "hop", "bunny", "rabbit", "slime", "jelly", "blob", "puff") || entity == EntityType.SLIME || entity == EntityType.MAGMA_CUBE) return Style.HOP;
        if (has(n, "spider", "crab", "beetle", "ant", "scorp", "tick", "mite") || entity == EntityType.SPIDER || entity == EntityType.CAVE_SPIDER) return Style.SKITTER;
        if (has(n, "golem", "giant", "titan", "ogre", "troll", "turtle", "mossback", "stump", "boulder", "monk", "colossus")) return Style.LUMBER;
        if (has(n, "boar", "bull", "horn", "rhino", "ram", "tusk", "thunder", "charger")) return Style.CHARGE;
        if (has(n, "wolf", "cat", "fox", "hound", "lynx", "stalker", "shade", "wraith")) return Style.CIRCLE;
        Style[] all = { Style.STALK, Style.CHARGE, Style.CIRCLE, Style.STALK, Style.LUMBER };
        return all[(id.hashCode() & 0x7fffffff) % all.length];
    }

    private static boolean has(String n, String... words) { for (String w : words) if (n.contains(w)) return true; return false; }

    /** Takes the vanilla goals off the mob. Its body still walks, falls and is pushed; only its mind is ours. */
    public static void free(Mob mob) {
        try { Bukkit.getMobGoals().removeAllGoals(mob); } catch (Throwable ignored) { }
    }

    /** One step, every half second, on the mob's region. No target: it ambles about its home. */
    public void step(LivingEntity target, Location home, boolean busy) {
        if (busy) { mob.getPathfinder().stopPathfinding(); return; }
        Location at = mob.getLocation();
        long now = System.currentTimeMillis();
        beat++;
        if (target == null || !target.getWorld().equals(at.getWorld())) { amble(at, home, now); return; }
        wander = null;
        Location there = target.getLocation();
        Vector to = there.toVector().subtract(at.toVector()).setY(0);
        double d = to.length();
        if (d < 0.05) return;
        Vector dir = to.multiply(1 / d), across = new Vector(-dir.getZ(), 0, dir.getX());
        if (now < pauseUntil) { mob.getPathfinder().stopPathfinding(); mob.lookAt(target); return; }
        ThreadLocalRandom r = ThreadLocalRandom.current();
        switch (style) {
            case STALK -> {
                if (d < reach * 0.8) { stop(target); if (r.nextInt(4) == 0) pauseUntil = now + 700; }
                else go(there, d > 10 ? 1.25 : 0.9);
            }
            case LUMBER -> {
                if (beat % rhythm == 0) { pauseUntil = now + 900; stop(target); }      // a heavy stop, then on again
                else if (d < reach * 0.8) stop(target);
                else go(there, 0.75);
            }
            case CHARGE -> {
                int b = beat % rhythm;
                if (b >= rhythm - 3) go(there.clone().add(dir.clone().multiply(2)), 2.0);   // run through the target
                else if (d < 6) go(at.clone().subtract(dir.clone().multiply(3)).add(across.clone().multiply(side * 2)), 1.0);
                else if (d > 12) go(there, 1.1);
                else { stop(target); if (b == 0) side = -side; }
            }
            case CIRCLE -> {
                angle += side * (40.0 / radius);
                if (r.nextInt(12) == 0) side = -side;
                if (beat % rhythm == 0 || d > radius * 2.5) go(there, 1.6);          // dart in
                else {
                    double a = Math.toRadians(angle);
                    go(there.clone().add(Math.cos(a) * radius, 0, Math.sin(a) * radius), 1.2);
                }
            }
            case SLITHER -> {
                if (d < reach) go(there, 1.4);
                else go(at.clone().add(dir.clone().multiply(3.5)).add(across.multiply(Math.sin(beat * 1.1) * 2.5)), 1.35);
            }
            case HOP -> {
                if (!mob.isOnGround()) return;
                if (beat % 3 != 0) { stop(target); return; }
                double push = Math.min(0.9, 0.3 + d * 0.06);
                mob.lookAt(target);
                mob.setVelocity(dir.multiply(push).setY(d < reach ? 0.35 : 0.55));
            }
            case SKITTER -> {
                if (beat % 2 == 0) { stop(target); return; }
                double off = (r.nextBoolean() ? 1 : -1) * (1.5 + r.nextDouble() * 2);
                Location dash = d < reach ? there : at.clone().add(dir.clone().multiply(Math.min(4, d - 1))).add(across.multiply(off));
                go(dash, 1.9);
            }
        }
    }

    private void amble(Location at, Location home, long now) {
        if (now < pauseUntil) return;
        if (home != null && home.getWorld() == at.getWorld() && home.distanceSquared(at) > 18 * 18) { wander = home; go(home, 1); return; }
        if (wander == null || wander.distanceSquared(at) < 2.5 || beat % 16 == 0) {
            ThreadLocalRandom r = ThreadLocalRandom.current();
            if (r.nextInt(3) == 0) { wander = null; pauseUntil = now + 1500 + r.nextInt(2500); mob.getPathfinder().stopPathfinding(); return; }
            Location base = home != null && home.getWorld() == at.getWorld() ? home : at;
            wander = base.clone().add(r.nextDouble(-7, 7), 0, r.nextDouble(-7, 7));
        }
        go(wander, 0.55);
    }

    private void go(Location to, double speed) { mob.getPathfinder().moveTo(to, speed); }

    private void stop(LivingEntity target) { mob.getPathfinder().stopPathfinding(); mob.lookAt(target); }
}
