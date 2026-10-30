package com.cquests.listener;

import org.bukkit.block.Block;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Remembers blocks players placed so that breaking them again does not count for MINE objectives,
 * and spots that already counted for PLACE objectives. Kept in memory and capped; it only needs to
 * stop place-and-break loops, not survive restarts.
 */
final class PlacedBlocks {

    private static final int MAX = 250_000;

    private record Pos(UUID world, int x, int y, int z) {
    }

    private final Set<Pos> placed = ConcurrentHashMap.newKeySet();
    /** Spots that already counted for a PLACE objective, so placing and breaking one block over and over counts once. */
    private final Set<Pos> counted = ConcurrentHashMap.newKeySet();

    void add(Block block) {
        if (placed.size() >= MAX) {
            placed.clear();
        }
        placed.add(key(block));
    }

    /** True the first time a spot is used for a PLACE objective. */
    boolean firstPlacementAt(Block block) {
        if (counted.size() >= MAX) {
            counted.clear();
        }
        return counted.add(key(block));
    }

    /** Returns true and forgets the block if a player placed it. */
    boolean remove(Block block) {
        return placed.remove(key(block));
    }

    private static Pos key(Block block) {
        return new Pos(block.getWorld().getUID(), block.getX(), block.getY(), block.getZ());
    }
}
