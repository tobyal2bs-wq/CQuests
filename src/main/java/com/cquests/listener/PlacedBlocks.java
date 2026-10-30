package com.cquests.listener;

import org.bukkit.block.Block;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Remembers blocks players placed so that breaking them again does not count for MINE objectives.
 * Kept in memory and capped; it only needs to stop the place-and-break loop, not survive restarts.
 */
final class PlacedBlocks {

    private static final int MAX = 250_000;

    private record Pos(UUID world, int x, int y, int z) {
    }

    private final Set<Pos> placed = ConcurrentHashMap.newKeySet();

    void add(Block block) {
        if (placed.size() >= MAX) {
            placed.clear();
        }
        placed.add(key(block));
    }

    /** Returns true and forgets the block if a player placed it. */
    boolean remove(Block block) {
        return placed.remove(key(block));
    }

    private static Pos key(Block block) {
        return new Pos(block.getWorld().getUID(), block.getX(), block.getY(), block.getZ());
    }
}
