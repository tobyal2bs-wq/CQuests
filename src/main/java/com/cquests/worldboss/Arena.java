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
    /** A spot: a boss wakes here every this many minutes (0 = not a timed spot, only the weekly schedule). */
    volatile long intervalMinutes;
    /** When the next boss wakes at this spot (epoch millis), and the slot already warned about. */
    volatile long nextAt, warned;
    /** The boss and movement pattern of the last fight here, so the next one is always different. */
    volatile String lastBoss = "";
    volatile int lastPattern = -1;
    /** Areas inside the border the boss may not enter: {0, x, z, r} circles and {1, x1, z1, x2, z2} boxes. */
    final List<double[]> nopass = new java.util.concurrent.CopyOnWriteArrayList<>();
    /** First corner of a box being marked. */
    volatile double[] corner;

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

    /** Inside a no-pass area. */
    public boolean blocked(double bx, double bz) {
        for (double[] z : nopass) {
            if (z[0] == 0) { double dx = bx - z[1], dz = bz - z[2]; if (dx * dx + dz * dz <= z[3] * z[3]) return true; }
            else if (bx >= Math.min(z[1], z[3]) && bx <= Math.max(z[1], z[3]) + 1 && bz >= Math.min(z[2], z[4]) && bz <= Math.max(z[2], z[4]) + 1) return true;
        }
        return false;
    }

    static String nopassText(double[] z) {
        return z[0] == 0 ? "circle:" + z[1] + "," + z[2] + "," + z[3] : "box:" + z[1] + "," + z[2] + "," + z[3] + "," + z[4];
    }

    static double[] nopassParse(String s) {
        try {
            String[] kv = s.split(":", 2);
            String[] n = kv[1].split(",");
            if (kv[0].equals("circle") && n.length == 3) return new double[]{0, Double.parseDouble(n[0]), Double.parseDouble(n[1]), Double.parseDouble(n[2])};
            if (kv[0].equals("box") && n.length == 4) return new double[]{1, Double.parseDouble(n[0]), Double.parseDouble(n[1]), Double.parseDouble(n[2]), Double.parseDouble(n[3])};
        } catch (RuntimeException ignored) { }
        return null;
    }

    /** "2h", "400h", "90m", "1d12h", "off" to minutes (0 = off, -1 = not understood). */
    public static long parseInterval(String text) {
        String t = text.trim().toLowerCase(Locale.ROOT);
        if (t.equals("off") || t.equals("0") || t.equals("none")) return 0;
        var m = java.util.regex.Pattern.compile("(\\d+)([dhm])").matcher(t);
        long total = 0; int end = 0;
        while (m.find()) {
            if (m.start() != end) return -1;
            long n = Long.parseLong(m.group(1));
            total += switch (m.group(2)) { case "d" -> n * 1440; case "h" -> n * 60; default -> n; };
            end = m.end();
        }
        if (end != t.length()) {
            try { return Long.parseLong(t) * 60; } catch (NumberFormatException e) { return -1; }
        }
        return total >= 5 ? total : -1;
    }

    public static String intervalText(long minutes) {
        if (minutes <= 0) return "off";
        long d = minutes / 1440, h = minutes % 1440 / 60, m = minutes % 60;
        return (d > 0 ? d + "d" : "") + (h > 0 ? h + "h" : "") + (m > 0 ? m + "m" : "");
    }

    public String describe() {
        Polygon p = polygon;
        return p != null ? p.vertices().size() + "-point outline" : "circle of " + radius + " blocks";
    }
}
