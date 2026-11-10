package com.cbosses.hook;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Player;

import java.util.logging.Logger;

/**
 * WorldGuard support without a hard dependency: every call goes through {@link WorldGuardBridge}, which is
 * only loaded once WorldGuard is known to be there.
 *
 * Two region flags are added (WorldGuard must load before them, so they are registered while CBosses loads):
 *   cbosses-spawn  deny: no boss can be summoned or spawned inside the region
 *   cbosses-fight  deny: bosses cannot hurt players there and players cannot hurt bosses there
 * Arenas can also use a region as their border (/cbosses arena region <arena> <region>).
 */
public final class WorldGuardHook {
    private static volatile boolean registered;
    private static volatile boolean broken;
    private static volatile boolean enabled = true;

    private WorldGuardHook() {}

    public static boolean present() {
        return Bukkit.getPluginManager().getPlugin("WorldGuard") != null;
    }

    /** worldguard.enabled in config.yml; false ignores WorldGuard entirely. */
    public static void init(boolean on, Logger log) {
        enabled = on;
        if (present() && !on) log.info("WorldGuard support is turned off in config.yml (worldguard.enabled).");
    }

    public static boolean available() {
        if (broken || !enabled) return false;
        var plugin = Bukkit.getPluginManager().getPlugin("WorldGuard");
        return plugin != null && plugin.isEnabled();
    }

    /** Called from onLoad, before WorldGuard locks its flag registry. */
    public static void registerFlags(Logger log) {
        if (!present()) return;
        try {
            WorldGuardBridge.registerFlags();
            registered = true;
            log.info("WorldGuard found: added the cbosses-spawn and cbosses-fight region flags.");
        } catch (Throwable e) {
            log.warning("Could not add the WorldGuard flags (" + e + "). Regions still work as arena borders.");
        }
    }

    public static boolean contains(Location at, String region) {
        if (!available() || at == null || region == null || region.isBlank()) return false;
        try { return WorldGuardBridge.contains(at, region); }
        catch (Throwable e) { fail(e); return false; }
    }

    /** {minX, minY, minZ, maxX, maxY, maxZ}, or null when there is no such region. */
    public static int[] bounds(World world, String region) {
        if (!available()) return null;
        try { return WorldGuardBridge.bounds(world, region); }
        catch (Throwable e) { fail(e); return null; }
    }

    public static boolean exists(World world, String region) { return bounds(world, region) != null; }

    /** False when the cbosses-spawn flag is set to deny here. */
    public static boolean maySpawn(Location at) {
        if (!registered || !available()) return true;
        try { return WorldGuardBridge.test(at, null, "spawn"); }
        catch (Throwable e) { fail(e); return true; }
    }

    /** False when the cbosses-fight flag is set to deny where this player stands. */
    public static boolean mayFight(Player player) {
        if (!registered || !available()) return true;
        try { return WorldGuardBridge.test(player.getLocation(), player, "fight"); }
        catch (Throwable e) { fail(e); return true; }
    }

    private static void fail(Throwable e) {
        if (broken) return;
        broken = true;
        Bukkit.getLogger().warning("[CBosses] WorldGuard support turned off after an error: " + e);
    }
}
