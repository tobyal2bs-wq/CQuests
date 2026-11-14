package com.cbosses.fight;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.Sound;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.plugin.Plugin;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Private fights (chapter bosses with chapter-bosses.private): inside their circle every block of the boss,
 * its minions, flying debris, particles and sounds exist only for the player whose quest it is. Everyone else
 * sees and hears nothing and cannot be touched by it. Fights register their circle here; the effect code asks
 * which player, if any, owns a spot.
 */
public final class Privacy {
    private record Zone(String world, double x, double z, double r2, UUID owner) {}

    private static final Map<String, Zone> zones = new ConcurrentHashMap<>();
    private static volatile Plugin plugin;

    private Privacy() {}

    static void init(Plugin owner) { plugin = owner; }

    static void add(String key, Location center, double radius, UUID owner) {
        zones.put(key, new Zone(center.getWorld().getName(), center.getX(), center.getZ(), radius * radius, owner));
    }

    static void remove(String key) { zones.remove(key); }

    public static boolean any() { return !zones.isEmpty(); }

    /** The player a spot belongs to, or null when it is public. */
    public static UUID owner(Location at) {
        if (zones.isEmpty() || at == null || at.getWorld() == null) return null;
        String w = at.getWorld().getName();
        for (Zone z : zones.values()) {
            if (!z.world.equals(w)) continue;
            double dx = at.getX() - z.x, dz = at.getZ() - z.z;
            if (dx * dx + dz * dz <= z.r2) return z.owner;
        }
        return null;
    }

    /** May this player see what happens at that spot. */
    public static boolean sees(Player p, Location at) {
        UUID o = owner(at);
        return o == null || o.equals(p.getUniqueId());
    }

    /** Hides a freshly spawned entity from everyone but the owner when it is inside a private circle. */
    public static void claim(Entity e) {
        UUID o = owner(e.getLocation());
        if (o == null || plugin == null) return;
        try {
            e.setVisibleByDefault(false);
            Player p = Bukkit.getPlayer(o);
            if (p != null) {
                if (Bukkit.isOwnedByCurrentRegion(p)) p.showEntity(plugin, e);
                else p.getScheduler().run(plugin, t -> { if (e.isValid()) p.showEntity(plugin, e); }, null);
            }
        } catch (RuntimeException ignored) { }
    }

    // ------------------------------------------------------------------ particles and sounds

    private static Player only(Location at) {
        UUID o = owner(at);
        if (o == null) return null;
        Player p = Bukkit.getPlayer(o);
        return p == null ? NOBODY : p;
    }

    /** Marker for a private spot whose owner is gone: nothing is shown. */
    private static final Player NOBODY = null;

    private static boolean hidden(Location at) { return owner(at) != null && only(at) == null; }

    public static void particle(World w, Particle p, Location at, int c) { particle(w, p, at, c, 0, 0, 0, 0); }

    public static void particle(World w, Particle p, Location at, int c, double dx, double dy, double dz, double speed) {
        if (hidden(at)) return;
        Player o = only(at);
        if (o != null) o.spawnParticle(p, at, c, dx, dy, dz, speed); else w.spawnParticle(p, at, c, dx, dy, dz, speed);
    }

    public static <T> void particle(World w, Particle p, Location at, int c, double dx, double dy, double dz, double speed, T data) {
        if (hidden(at)) return;
        Player o = only(at);
        if (o != null) o.spawnParticle(p, at, c, dx, dy, dz, speed, data); else w.spawnParticle(p, at, c, dx, dy, dz, speed, data);
    }

    public static void particle(World w, Particle p, double x, double y, double z, int c, double dx, double dy, double dz, double speed) {
        particle(w, p, new Location(w, x, y, z), c, dx, dy, dz, speed);
    }

    public static <T> void particle(World w, Particle p, double x, double y, double z, int c, double dx, double dy, double dz, double speed, T data) {
        particle(w, p, new Location(w, x, y, z), c, dx, dy, dz, speed, data);
    }

    public static void sound(World w, Location at, Sound s, float volume, float pitch) {
        if (hidden(at)) return;
        Player o = only(at);
        if (o != null) o.playSound(at, s, volume, pitch); else w.playSound(at, s, volume, pitch);
    }
}
