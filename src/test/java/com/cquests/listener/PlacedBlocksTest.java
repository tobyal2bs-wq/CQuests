package com.cquests.listener;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.persistence.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class PlacedBlocksTest {
    @Test void pistonChainCarriesMarksAcrossChunkBoundaryAndBack() {
        World world=mock(World.class);when(world.getMinHeight()).thenReturn(-64);
        Chunk left=mock(Chunk.class),right=mock(Chunk.class);
        PersistentDataContainer leftData=container(),rightData=container();
        when(left.getPersistentDataContainer()).thenReturn(leftData);when(right.getPersistentDataContainer()).thenReturn(rightData);
        Block a=block(left,world,14,64,0),b=block(left,world,15,64,0),c=block(right,world,16,64,0);
        when(a.getRelative(org.bukkit.block.BlockFace.EAST)).thenReturn(b);when(b.getRelative(org.bukkit.block.BlockFace.EAST)).thenReturn(c);
        when(b.getRelative(org.bukkit.block.BlockFace.WEST)).thenReturn(a);when(c.getRelative(org.bukkit.block.BlockFace.WEST)).thenReturn(b);
        PlacedBlocks marks=new PlacedBlocks();marks.add(a);marks.add(b);
        marks.move(List.of(a,b),org.bukkit.block.BlockFace.EAST);
        assertFalse(marks.remove(a));
        marks.move(List.of(c,b),org.bukkit.block.BlockFace.WEST);
        assertTrue(marks.remove(a));assertTrue(marks.remove(b));assertFalse(marks.remove(c));
    }
    @Test void naturalBlocksDoNotInheritMarksAndDestroyedBlocksDoNotMoveThem() {
        World world=mock(World.class);when(world.getMinHeight()).thenReturn(-64);Chunk chunk=mock(Chunk.class);
        PersistentDataContainer data=container();when(chunk.getPersistentDataContainer()).thenReturn(data);
        Block a=block(chunk,world,0,64,0),b=block(chunk,world,1,64,0),c=block(chunk,world,2,64,0);
        when(a.getRelative(org.bukkit.block.BlockFace.EAST)).thenReturn(b);when(b.getRelative(org.bukkit.block.BlockFace.EAST)).thenReturn(c);
        PlacedBlocks marks=new PlacedBlocks();marks.add(a);marks.move(List.of(a,b),org.bukkit.block.BlockFace.EAST);
        assertTrue(marks.remove(b));assertFalse(marks.remove(c));
        marks.add(a);when(a.getPistonMoveReaction()).thenReturn(org.bukkit.block.PistonMoveReaction.BREAK);
        marks.move(List.of(a),org.bukkit.block.BlockFace.EAST);assertFalse(marks.remove(a));assertFalse(marks.remove(b));
    }
    private static PersistentDataContainer container(){
        Map<NamespacedKey,byte[]> saved=new HashMap<>();PersistentDataContainer data=mock(PersistentDataContainer.class);
        when(data.get(any(NamespacedKey.class),eq(PersistentDataType.BYTE_ARRAY))).thenAnswer(i->saved.get(i.getArgument(0)));
        doAnswer(i->{saved.put(i.getArgument(0),i.getArgument(2));return null;}).when(data).set(any(NamespacedKey.class),eq(PersistentDataType.BYTE_ARRAY),any(byte[].class));
        doAnswer(i->{saved.remove(i.getArgument(0));return null;}).when(data).remove(any(NamespacedKey.class));return data;
    }
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
