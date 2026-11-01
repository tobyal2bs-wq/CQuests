package com.cquests.npc;

import org.bukkit.Material;
import org.bukkit.World;

/** Pure terrain rules shared by automatic, scattered and manual placements. */
public final class TerrainSafety {
    // Server registry lookup is replaceable in isolated terrain-fixture tests.
    static java.util.function.Predicate<Material> occluding = Material::isOccluding;
    @FunctionalInterface public interface Blocks { Material at(int x, int y, int z); }
    private TerrainSafety() {}

    public static boolean floor(Material material) {
        return occluding.test(material) && !switch (material) {
            case MAGMA_BLOCK, CACTUS, CAMPFIRE, SOUL_CAMPFIRE, POWDER_SNOW -> true;
            default -> false;
        };
    }

    public static boolean clear(Material material) {
        return switch (material) {
            case AIR, CAVE_AIR, VOID_AIR, SHORT_GRASS, TALL_GRASS, FERN, LARGE_FERN, DEAD_BUSH, SNOW -> true;
            default -> false;
        };
    }

    public static boolean safe(Blocks blocks, World.Environment environment, int x, int feetY, int z, int minHeight) {
        if (feetY <= minHeight || !floor(blocks.at(x, feetY - 1, z))
                || !clear(blocks.at(x, feetY, z)) || !clear(blocks.at(x, feetY + 1, z))) return false;
        // Every column in the End's ten-block circle needs nearby supporting terrain.
        // Reject island edges, holes and large drops even if the central block is solid.
        if (environment == World.Environment.THE_END) {
            for (int dx = -10; dx <= 10; dx++) for (int dz = -10; dz <= 10; dz++) {
                if (dx * dx + dz * dz > 100) continue;
                boolean supported = false;
                for (int y = feetY - 5; y <= feetY + 3; y++) {
                    if (y >= minHeight && floor(blocks.at(x + dx, y, z + dz))) { supported = true; break; }
                }
                if (!supported) return false;
            }
        }
        if (environment == World.Environment.NETHER) {
            if (feetY >= 123) return false; // never strand a villager on the bedrock roof
            for (int dx = -10; dx <= 10; dx++) for (int dz = -10; dz <= 10; dz++) {
                if (dx * dx + dz * dz > 100) continue;
                for (int y = Math.max(minHeight, feetY - 4); y <= feetY + 2; y++) {
                    if (blocks.at(x + dx, y, z + dz) == Material.LAVA) return false;
                }
            }
        }
        return true;
    }

    public static int find(Blocks blocks, World.Environment environment, int x, int z, int minFeet, int maxFeet, int minHeight) {
        int top = environment == World.Environment.NETHER ? Math.min(122, maxFeet) : maxFeet;
        for (int feet = top; feet >= Math.max(minFeet, minHeight + 1); feet--) {
            if (safe(blocks, environment, x, feet, z, minHeight)) return feet;
        }
        return Integer.MIN_VALUE;
    }

    public static boolean exposed(Blocks blocks,World.Environment environment,int x,int feet,int z,int maxHeight){
        int ceiling=environment==World.Environment.NETHER?Math.min(maxHeight,feet+6):maxHeight;
        for(int y=feet;y<ceiling;y++)if(!clear(blocks.at(x,y,z)))return false;
        return true;
    }
}
