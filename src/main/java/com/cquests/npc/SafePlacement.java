package com.cquests.npc;

import com.cquests.util.Sched;
import org.bukkit.ChunkSnapshot;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

/** Captures each chunk on its owning region, then searches detached snapshots asynchronously. */
public final class SafePlacement {
    private SafePlacement() {}

    public static CompletableFuture<Location> find(World world, double x, double z, Integer minFeet, Integer maxFeet, float yaw) {
        return inspect(world, x, z, minFeet, maxFeet, yaw, null);
    }

    public static CompletableFuture<Boolean> validate(Location location) {
        return inspect(location.getWorld(), location.getX(), location.getZ(), null, null,
                location.getYaw(), location.getBlockY()).thenApply(result -> result != null);
    }

    private static CompletableFuture<Location> inspect(World world, double x, double z, Integer minFeet, Integer maxFeet, float yaw, Integer exactY) {
        World.Environment environment = world.getEnvironment();
        int radius = environment == World.Environment.NORMAL ? 0 : 10;
        int bx = (int) Math.floor(x), bz = (int) Math.floor(z);
        Location center = new Location(world, x, world.getMinHeight(), z);
        if (!world.getWorldBorder().isInside(center)) return CompletableFuture.completedFuture(null);
        int bottom = world.getMinHeight(), top = world.getMaxHeight();
        Map<Long, ChunkSnapshot> snapshots = new ConcurrentHashMap<>();
        var tasks = new ArrayList<CompletableFuture<Void>>();
        for (int cx = (bx - radius) >> 4; cx <= (bx + radius) >> 4; cx++) {
            for (int cz = (bz - radius) >> 4; cz <= (bz + radius) >> 4; cz++) {
                int chunkX = cx, chunkZ = cz;
                CompletableFuture<Void> captured = new CompletableFuture<>();
                tasks.add(captured);
                world.getChunkAtAsync(cx, cz, true).whenComplete((chunk, error) -> {
                    if (error != null) { captured.completeExceptionally(error); return; }
                    try { Sched.at(new Location(world, chunkX * 16, bottom, chunkZ * 16), () -> {
                        try {
                            snapshots.put(key(chunkX, chunkZ), chunk.getChunkSnapshot(false, false, false));
                            captured.complete(null);
                        } catch (Throwable failure) { captured.completeExceptionally(failure); }
                    }); } catch (Throwable failure) { captured.completeExceptionally(failure); }
                });
            }
        }
        return CompletableFuture.allOf(tasks.toArray(CompletableFuture[]::new)).thenApplyAsync(ignored -> {
            TerrainSafety.Blocks blocks = (xx, yy, zz) -> {
                if (yy < bottom || yy >= top) return Material.AIR;
                ChunkSnapshot snapshot = snapshots.get(key(xx >> 4, zz >> 4));
                return snapshot == null ? Material.AIR : snapshot.getBlockType(xx & 15, yy, zz & 15);
            };
            int y = exactY == null ? TerrainSafety.find(blocks, environment, bx, bz,
                    minFeet == null ? bottom + 1 : minFeet, Math.min(top - 2, maxFeet == null ? top - 2 : maxFeet), bottom)
                    : (TerrainSafety.safe(blocks, environment, bx, exactY, bz, bottom) ? exactY : Integer.MIN_VALUE);
            return y == Integer.MIN_VALUE || !TerrainSafety.exposed(blocks,environment,bx,y,bz,top)
                    ? null : new Location(world, x, y, z, yaw, 0f);
        });
    }

    private static long key(int x, int z) { return ((long) x << 32) ^ (z & 0xffffffffL); }
}
