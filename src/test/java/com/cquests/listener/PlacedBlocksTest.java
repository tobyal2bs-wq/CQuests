package com.cquests.listener;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.persistence.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class PlacedBlocksTest {
    @Test void freshTrackerRetainsPlacedAndCountedMarksFromChunkData() {
        Map<NamespacedKey,byte[]> saved=new HashMap<>();PersistentDataContainer data=mock(PersistentDataContainer.class);
        when(data.get(any(NamespacedKey.class),eq(PersistentDataType.BYTE_ARRAY))).thenAnswer(i->saved.get(i.getArgument(0)));
        doAnswer(i->{saved.put(i.getArgument(0),i.getArgument(2));return null;}).when(data).set(any(NamespacedKey.class),eq(PersistentDataType.BYTE_ARRAY),any(byte[].class));
        doAnswer(i->{saved.remove(i.getArgument(0));return null;}).when(data).remove(any(NamespacedKey.class));
        Chunk chunk=mock(Chunk.class);when(chunk.getPersistentDataContainer()).thenReturn(data);
        World world=mock(World.class);when(world.getMinHeight()).thenReturn(-64);
        Block first=block(chunk,world,-1,-63,-1),neighbor=block(chunk,world,-2,-63,-1);
        PlacedBlocks original=new PlacedBlocks();original.add(first);assertTrue(original.firstPlacementAt(first));
        PlacedBlocks restarted=new PlacedBlocks();assertFalse(restarted.firstPlacementAt(first));
        assertTrue(restarted.firstPlacementAt(neighbor));assertFalse(restarted.remove(neighbor));
        assertTrue(restarted.remove(first));assertFalse(restarted.remove(first));
        restarted.add(first);assertFalse(new PlacedBlocks().firstPlacementAt(first));
        assertTrue(new PlacedBlocks().remove(first));
    }
    private static Block block(Chunk chunk,World world,int x,int y,int z){
        Block b=mock(Block.class);when(b.getChunk()).thenReturn(chunk);when(b.getWorld()).thenReturn(world);
        when(b.getX()).thenReturn(x);when(b.getY()).thenReturn(y);when(b.getZ()).thenReturn(z);return b;
    }
}
