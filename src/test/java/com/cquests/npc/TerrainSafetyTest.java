package com.cquests.npc;

import org.bukkit.Material;
import org.bukkit.World;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TerrainSafetyTest {
    @Test void overheadRockDisqualifiesAnOverworldCaveButOpenSurfacePasses(){
        TerrainSafety.Blocks cave=(x,y,z)->y==63||y==90?Material.STONE:Material.AIR;
        assertTrue(TerrainSafety.safe(cave,World.Environment.NORMAL,0,64,0,-64));
        assertFalse(TerrainSafety.exposed(cave,World.Environment.NORMAL,0,64,0,320));
        assertTrue(TerrainSafety.exposed(cave,World.Environment.NORMAL,0,91,0,320));
    }
    @Test void smallDecorationsAtFeetDoNotBlockASpot(){
        assertTrue(TerrainSafety.clear(Material.TORCH));
        assertTrue(TerrainSafety.clear(Material.RED_CARPET));
        assertTrue(TerrainSafety.clear(Material.POPPY));
        assertFalse(TerrainSafety.clear(Material.LAVA));
        assertFalse(TerrainSafety.clear(Material.WATER));
        assertFalse(TerrainSafety.clear(Material.COBWEB));
    }
    @org.junit.jupiter.api.BeforeAll static void registryFixture() {
        TerrainSafety.occluding = m -> java.util.Set.of(Material.STONE, Material.END_STONE, Material.NETHERRACK, Material.BEDROCK, Material.MAGMA_BLOCK).contains(m);
    }
    @org.junit.jupiter.api.AfterAll static void resetRegistry() { TerrainSafety.occluding = Material::isOccluding; }
    @Test void endRejectsOneBlockOfVoidAtTenBlocksIncludingNegativeCoordinates() {
        TerrainSafety.Blocks land = (x,y,z) -> y == 63 ? Material.END_STONE : Material.AIR;
        assertTrue(TerrainSafety.safe(land, World.Environment.THE_END, -16, 64, -16, 0));
        TerrainSafety.Blocks edge = (x,y,z) -> x == -6 && z == -16 ? Material.AIR : land.at(x,y,z);
        assertFalse(TerrainSafety.safe(edge, World.Environment.THE_END, -16, 64, -16, 0));
        TerrainSafety.Blocks outside = (x,y,z) -> x == -5 && z == -16 ? Material.AIR : land.at(x,y,z);
        assertTrue(TerrainSafety.safe(outside, World.Environment.THE_END, -16, 64, -16, 0));
    }
    @Test void netherRejectsLavaNearbyAndTheRoof() {
        TerrainSafety.Blocks land = (x,y,z) -> y == 63 ? Material.NETHERRACK : Material.AIR;
        assertTrue(TerrainSafety.safe(land, World.Environment.NETHER, 0, 64, 0, 0));
        TerrainSafety.Blocks lava = (x,y,z) -> x == 10 && z == 0 && y == 63 ? Material.LAVA : land.at(x,y,z);
        assertFalse(TerrainSafety.safe(lava, World.Environment.NETHER, 0, 64, 0, 0));
        TerrainSafety.Blocks roof = (x,y,z) -> y == 127 ? Material.BEDROCK : Material.AIR;
        assertEquals(Integer.MIN_VALUE, TerrainSafety.find(roof, World.Environment.NETHER, 0, 0, 1, 250, 0));
    }
    @Test void unsafeFloorAndLiquidHeadroomHaveNoFallback() {
        for (Material material : new Material[]{Material.LAVA, Material.WATER, Material.MAGMA_BLOCK, Material.CACTUS, Material.POWDER_SNOW}) {
            TerrainSafety.Blocks bad = (x,y,z) -> y == 63 ? material : Material.AIR;
            assertEquals(Integer.MIN_VALUE, TerrainSafety.find(bad, World.Environment.NORMAL, 0, 0, 64, 70, 0));
        }
        TerrainSafety.Blocks submerged = (x,y,z) -> y == 63 ? Material.STONE : y == 64 ? Material.WATER : Material.AIR;
        assertFalse(TerrainSafety.safe(submerged, World.Environment.NORMAL, 0, 64, 0, 0));
    }
    @Test void requestedHeightIsAnActualBound() {
        TerrainSafety.Blocks ground = (x,y,z) -> y == 63 ? Material.STONE : Material.AIR;
        assertEquals(Integer.MIN_VALUE, TerrainSafety.find(ground, World.Environment.NORMAL, 0, 0, 70, 90, 0));
        assertEquals(64, TerrainSafety.find(ground, World.Environment.NORMAL, 0, 0, 60, 64, 0));
    }
}
