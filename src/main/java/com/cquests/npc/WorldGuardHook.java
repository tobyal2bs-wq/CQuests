package com.cquests.npc;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.Location;

import java.lang.reflect.Method;

/**
 * Reads WorldGuard region bounds through reflection so the plugin has no hard dependency on it.
 * Only used to scatter NPCs inside a named region; spawning itself bypasses WorldGuard flags
 * in {@link com.cquests.listener.NpcListener}.
 */
public final class WorldGuardHook {
    private static final java.util.Map<String,Method> METHODS=new java.util.concurrent.ConcurrentHashMap<>();
    private static Method method(String owner,String name,Class<?>... types)throws ReflectiveOperationException{
        String key=owner+"#"+name+java.util.Arrays.toString(types);
        Method value=METHODS.get(key);if(value!=null)return value;
        value=Class.forName(owner).getMethod(name,types);METHODS.put(key,value);return value;
    }

    private WorldGuardHook() {
    }

    public static boolean available() {
        var plugin=Bukkit.getPluginManager().getPlugin("WorldGuard");
        return plugin != null && plugin.isEnabled();
    }

    /** Exact protected-region shape, including WorldGuard polygon regions. Missing WG fails closed. */
    public static boolean contains(Location loc,String regionName) {
        if(!available()||regionName==null||regionName.isBlank()||regionName.equalsIgnoreCase("__global__"))return false;
        try {
            Object instance=method("com.sk89q.worldguard.WorldGuard","getInstance").invoke(null);
            Object platform=method("com.sk89q.worldguard.WorldGuard","getPlatform").invoke(instance);
            Object container=method("com.sk89q.worldguard.internal.platform.WorldGuardPlatform","getRegionContainer").invoke(platform);
            Object world=method("com.sk89q.worldedit.bukkit.BukkitAdapter","adapt",World.class).invoke(null,loc.getWorld());
            Object manager=method("com.sk89q.worldguard.protection.regions.RegionContainer",
                    "get",Class.forName("com.sk89q.worldedit.world.World")).invoke(container,world);
            if(manager==null)return false;
            Object region=method("com.sk89q.worldguard.protection.managers.RegionManager","getRegion",String.class).invoke(manager,regionName);
            return region!=null&&(boolean)method("com.sk89q.worldguard.protection.regions.ProtectedRegion",
                    "contains",int.class,int.class,int.class).invoke(region,loc.getBlockX(),loc.getBlockY(),loc.getBlockZ());
        }catch(ReflectiveOperationException|RuntimeException|LinkageError e){return false;}
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
