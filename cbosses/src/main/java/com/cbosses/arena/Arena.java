package com.cbosses.arena;

import com.cbosses.hook.WorldGuardHook;
import com.cbosses.util.Polygon;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Where a boss appears and the outline it can never leave. The border is, in order: a WorldGuard region
 * (when one is linked and WorldGuard is on), the outline drawn with the border stick (3 or more points),
 * or a circle of {@code radius} around the spawn.
 */
public final class Arena {
    public final String id;
    public volatile String world;
    /** WorldGuard region used as the border, or null. */
    public volatile String region;
    public volatile double x, y, z;
    public volatile boolean hasSpawn;
    public final List<int[]> points = new ArrayList<>();
    volatile Polygon polygon;
    public volatile int radius;

    public Arena(String id, int radius) {
        this.id = id.toLowerCase(Locale.ROOT);
        this.radius = radius;
    }

    public String id() { return id; }

    public Location spawn() {
        World w = world == null ? null : Bukkit.getWorld(world);
        return w == null || !hasSpawn ? null : new Location(w, x, y, z);
    }

    public void spawn(Location at) {
        world = at.getWorld().getName(); x = at.getBlockX() + 0.5; y = at.getBlockY(); z = at.getBlockZ() + 0.5; hasSpawn = true;
    }

    public synchronized List<int[]> points() { return new ArrayList<>(points); }

    /** Adds a corner; returns null when fine, or why the outline is not usable yet. */
    public synchronized String add(int bx, int bz) {
        if (points.size() >= 128) return "An outline can have at most 128 points.";
        if (!points.isEmpty()) {
            int[] last = points.get(points.size() - 1);
            if (last[0] == bx && last[1] == bz) return "That is the same point as the last one.";
        }
        points.add(new int[]{bx, bz});
        return rebuild();
    }

    public synchronized boolean undo() {
        if (points.isEmpty()) return false;
        points.remove(points.size() - 1); rebuild(); return true;
    }

    public synchronized void clear() { points.clear(); polygon = null; }

    public synchronized String rebuild() {
        if (points.size() < 3) { polygon = null; return null; }
        List<Polygon.Vertex> v = new ArrayList<>();
        for (int[] p : points) v.add(new Polygon.Vertex(p[0], p[1]));
        try { polygon = new Polygon(v); return null; }
        catch (IllegalArgumentException e) { polygon = null; return e.getMessage(); }
    }

    /** Inside the border: the outline when there is one, otherwise the circle around the spawn. */
    public boolean contains(Location at) {
        if (at == null || at.getWorld() == null || !at.getWorld().getName().equals(world)) return false;
        String r = region;
        if (r != null && !r.isBlank() && WorldGuardHook.available()) return WorldGuardHook.contains(at, r);
        Polygon p = polygon;
        if (p != null) return p.contains(at.getBlockX(), at.getBlockZ());
        double dx = at.getX() - x, dz = at.getZ() - z;
        return dx * dx + dz * dz <= (double) radius * radius;
    }

    public String describe() {
        String r = region;
        if (r != null && !r.isBlank()) return "WorldGuard region " + r + (WorldGuardHook.available() ? "" : " (WorldGuard is not running)");
        Polygon p = polygon;
        return p != null ? p.vertices().size() + "-point outline" : "circle of " + radius + " blocks";
    }
}
