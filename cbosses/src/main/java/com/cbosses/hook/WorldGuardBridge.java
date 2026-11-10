package com.cbosses.hook;

import com.sk89q.worldedit.bukkit.BukkitAdapter;
import com.sk89q.worldedit.math.BlockVector3;
import com.sk89q.worldguard.LocalPlayer;
import com.sk89q.worldguard.WorldGuard;
import com.sk89q.worldguard.bukkit.WorldGuardPlugin;
import com.sk89q.worldguard.protection.flags.Flag;
import com.sk89q.worldguard.protection.flags.StateFlag;
import com.sk89q.worldguard.protection.flags.registry.FlagRegistry;
import com.sk89q.worldguard.protection.managers.RegionManager;
import com.sk89q.worldguard.protection.regions.ProtectedRegion;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Player;

/** The only class that touches WorldGuard's API. Loaded only when WorldGuard is installed. */
final class WorldGuardBridge {
    private static StateFlag spawn, fight;

    private WorldGuardBridge() {}

    static void registerFlags() {
        FlagRegistry registry = WorldGuard.getInstance().getFlagRegistry();
        spawn = flag(registry, "cbosses-spawn");
        fight = flag(registry, "cbosses-fight");
    }

    private static StateFlag flag(FlagRegistry registry, String name) {
        try {
            StateFlag f = new StateFlag(name, true);
            registry.register(f);
            return f;
        } catch (RuntimeException e) {
            // Already there (a reload): reuse it.
            Flag<?> existing = registry.get(name);
            if (existing instanceof StateFlag s) return s;
            throw e;
        }
    }

    private static ProtectedRegion region(World world, String name) {
        RegionManager manager = WorldGuard.getInstance().getPlatform().getRegionContainer().get(BukkitAdapter.adapt(world));
        return manager == null ? null : manager.getRegion(name);
    }

    static boolean contains(Location at, String name) {
        ProtectedRegion r = region(at.getWorld(), name);
        return r != null && r.contains(at.getBlockX(), at.getBlockY(), at.getBlockZ());
    }

    static int[] bounds(World world, String name) {
        ProtectedRegion r = region(world, name);
        if (r == null) return null;
        BlockVector3 min = r.getMinimumPoint(), max = r.getMaximumPoint();
        return new int[]{min.getBlockX(), min.getBlockY(), min.getBlockZ(), max.getBlockX(), max.getBlockY(), max.getBlockZ()};
    }

    static boolean test(Location at, Player player, String which) {
        StateFlag f = which.equals("spawn") ? spawn : fight;
        if (f == null) return true;
        LocalPlayer local = player == null ? null : WorldGuardPlugin.inst().wrapPlayer(player);
        return WorldGuard.getInstance().getPlatform().getRegionContainer().createQuery().testState(BukkitAdapter.adapt(at), local, f);
    }
}
