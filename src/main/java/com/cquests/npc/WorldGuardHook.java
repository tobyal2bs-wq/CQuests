package com.cquests.npc;

import org.bukkit.Bukkit;
import org.bukkit.World;

import java.lang.reflect.Method;

/**
 * Reads WorldGuard region bounds through reflection so the plugin has no hard dependency on it.
 * Only used to scatter NPCs inside a named region; spawning itself bypasses WorldGuard flags
 * in {@link com.cquests.listener.NpcListener}.
 */
public final class WorldGuardHook {

    private WorldGuardHook() {
    }

    public static boolean available() {
        return Bukkit.getPluginManager().getPlugin("WorldGuard") != null;
    }

    /** @return {minX, minY, minZ, maxX, maxY, maxZ} or null when the region does not exist */
    public static int[] bounds(World world, String regionName) {
        if (!available()) {
            return null;
        }
        try {
            Class<?> wgClass = Class.forName("com.sk89q.worldguard.WorldGuard");
            Object wg = wgClass.getMethod("getInstance").invoke(null);
            Object platform = wgClass.getMethod("getPlatform").invoke(wg);
            Class<?> platformClass = Class.forName("com.sk89q.worldguard.internal.platform.WorldGuardPlatform");
            Object container = platformClass.getMethod("getRegionContainer").invoke(platform);

            Class<?> adapter = Class.forName("com.sk89q.worldedit.bukkit.BukkitAdapter");
            Object weWorld = adapter.getMethod("adapt", World.class).invoke(null, world);
            Class<?> weWorldClass = Class.forName("com.sk89q.worldedit.world.World");
            Class<?> containerClass = Class.forName("com.sk89q.worldguard.protection.regions.RegionContainer");
            Object manager = containerClass.getMethod("get", weWorldClass).invoke(container, weWorld);
            if (manager == null) {
                return null;
            }
            Class<?> managerClass = Class.forName("com.sk89q.worldguard.protection.managers.RegionManager");
            Object region = managerClass.getMethod("getRegion", String.class).invoke(manager, regionName);
            if (region == null) {
                return null;
            }
            Class<?> regionClass = Class.forName("com.sk89q.worldguard.protection.regions.ProtectedRegion");
            Object min = regionClass.getMethod("getMinimumPoint").invoke(region);
            Object max = regionClass.getMethod("getMaximumPoint").invoke(region);
            return new int[]{coord(min, "x"), coord(min, "y"), coord(min, "z"), coord(max, "x"), coord(max, "y"), coord(max, "z")};
        } catch (ReflectiveOperationException | LinkageError e) {
            return null;
        }
    }

    private static int coord(Object vector, String axis) throws ReflectiveOperationException {
        Class<?> type = Class.forName("com.sk89q.worldedit.math.BlockVector3");
        Method method;
        try {
            method = type.getMethod(axis); // WorldEdit 7.3+
        } catch (NoSuchMethodException e) {
            method = type.getMethod("getBlock" + axis.toUpperCase()); // older WorldEdit
        }
        return ((Number) method.invoke(vector)).intValue();
    }
}
