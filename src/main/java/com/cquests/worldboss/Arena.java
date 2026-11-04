package com.cquests.worldboss;

import com.cquests.farm.Polygon;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Where a world boss appears and the outline it can never leave. Points are block x/z set with the
 * border stick; with fewer than 3 points the border is a circle of {@code radius} around the spawn.
 */
public final class Arena {
    final String id;
    volatile String world;
    volatile double x, y, z;
    volatile boolean hasSpawn;
    final List<int[]> points = new ArrayList<>();
    volatile Polygon polygon;
    volatile int radius;

    Arena(String id, int radius) {
        this.id = id.toLowerCase(Locale.ROOT);
        this.radius = radius;
    }

    public String id() { return id; }

    public Location spawn() {
        World w = world == null ? null : Bukkit.getWorld(world);
        return w == null || !hasSpawn ? null : new Location(w, x, y, z);
    }

    void spawn(Location at) {
        world = at.getWorld().getName(); x = at.getBlockX() + 0.5; y = at.getBlockY(); z = at.getBlockZ() + 0.5; hasSpawn = true;
    }

    synchronized List<int[]> points() { return new ArrayList<>(points); }

    /** Adds a corner; returns null when fine, or why the outline is not usable yet. */
    synchronized String add(int bx, int bz) {
        if (points.size() >= 128) return "An outline can have at most 128 points.";
        if (!points.isEmpty()) {
            int[] last = points.get(points.size() - 1);
            if (last[0] == bx && last[1] == bz) return "That is the same point as the last one.";
        }
        points.add(new int[]{bx, bz});
        return rebuild();
    }

    synchronized boolean undo() {
        if (points.isEmpty()) return false;
        points.remove(points.size() - 1); rebuild(); return true;
    }

    synchronized void clear() { points.clear(); polygon = null; }

    synchronized String rebuild() {
        if (points.size() < 3) { polygon = null; return null; }
        List<Polygon.Vertex> v = new ArrayList<>();
        for (int[] p : points) v.add(new Polygon.Vertex(p[0], p[1]));
        try { polygon = new Polygon(v); return null; }
        catch (IllegalArgumentException e) { polygon = null; return e.getMessage(); }
    }

    /** Inside the border: the outline when there is one, otherwise the circle around the spawn. */
    public boolean contains(Location at) {
        if (at == null || at.getWorld() == null || !at.getWorld().getName().equals(world)) return false;
        Polygon p = polygon;
        if (p != null) return p.contains(at.getBlockX(), at.getBlockZ());
        double dx = at.getX() - x, dz = at.getZ() - z;
        return dx * dx + dz * dz <= (double) radius * radius;
    }

    public String describe() {
        Polygon p = polygon;
        return p != null ? p.vertices().size() + "-point outline" : "circle of " + radius + " blocks";
    }
}
