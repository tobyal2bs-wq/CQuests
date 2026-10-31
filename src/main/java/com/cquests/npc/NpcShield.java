package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Text;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A protected bubble around every villager's spawn point: no building, breaking, buckets, explosions
 * or PvP, so nobody can wall a villager in or camp players at it. Lookups go through a chunk index,
 * so the check costs the same with 10 villagers or 10,000.
 */
public final class NpcShield {

    private final CQuestsPlugin plugin;
    /** world -> chunk key -> spawn points whose bubble touches that chunk */
    private volatile Map<UUID, Map<Long, List<Location>>> index = Map.of();
    private final Map<UUID, Long> lastWarning = new ConcurrentHashMap<>();

    public NpcShield(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    /** Rebuilds the chunk index; call whenever spawn points change. */
    public void rebuild() {
        double radius = plugin.settings().shieldRadius;
        Map<UUID, Map<Long, List<Location>>> fresh = new HashMap<>();
        if (radius > 0) {
            for (SpawnManager.Point point : plugin.spawns().points().values()) {
                Location loc = point.location();
                if (loc == null) {
                    continue;
                }
                Map<Long, List<Location>> chunks = fresh.computeIfAbsent(loc.getWorld().getUID(), k -> new HashMap<>());
                int minCx = (int) Math.floor((loc.getX() - radius) / 16);
                int maxCx = (int) Math.floor((loc.getX() + radius) / 16);
                int minCz = (int) Math.floor((loc.getZ() - radius) / 16);
                int maxCz = (int) Math.floor((loc.getZ() + radius) / 16);
                for (int cx = minCx; cx <= maxCx; cx++) {
                    for (int cz = minCz; cz <= maxCz; cz++) {
                        chunks.computeIfAbsent(key(cx, cz), k -> new ArrayList<>()).add(loc);
                    }
                }
            }
        }
        index = fresh;
    }

    /** The spawn point whose bubble contains this position, or null. */
    public Location protecting(World world, double x, double y, double z) {
        Map<Long, List<Location>> chunks = index.get(world.getUID());
        if (chunks == null) {
            return null;
        }
        List<Location> nearby = chunks.get(key((int) Math.floor(x) >> 4, (int) Math.floor(z) >> 4));
        if (nearby == null) {
            return null;
        }
        double radius = plugin.settings().shieldRadius;
        double r2 = radius * radius;
        for (Location loc : nearby) {
            double dx = loc.getX() - x;
            double dy = loc.getY() - y;
            double dz = loc.getZ() - z;
            if (dx * dx + dz * dz <= r2 && Math.abs(dy) <= radius + 2) {
                return loc;
            }
        }
        return null;
    }

    public Location protecting(Block block) {
        return protecting(block.getWorld(), block.getX() + 0.5, block.getY(), block.getZ() + 0.5);
    }

    public Location protecting(Location loc) {
        return protecting(loc.getWorld(), loc.getX(), loc.getY(), loc.getZ());
    }

    public boolean bypass(Player player) {
        return player.hasPermission("cquests.bypass");
    }

    /** Quiet, rate-limited protection message. No boundary particles. */
    public void warn(Player player, Location center) {
        long now = System.currentTimeMillis();
        Long last = lastWarning.get(player.getUniqueId());
        if (last != null && now - last < 1500) {
            return;
        }
        lastWarning.put(player.getUniqueId(), now);
        player.sendActionBar(Text.mm(plugin.settings().msg("shield", "<aqua>✦ This villager's area is protected.")));
    }

    public void forget(Player player) {
        lastWarning.remove(player.getUniqueId());
    }

    private static long key(int cx, int cz) {
        return ((long) cx << 32) ^ (cz & 0xffffffffL);
    }
}
