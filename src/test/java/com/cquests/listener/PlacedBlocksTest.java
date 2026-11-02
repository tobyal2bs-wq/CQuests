package com.cquests.listener;

import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.persistence.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class PlacedBlocksTest {
    @Test void maturePlayerPlantedCropCountsForHarvestButNotMining() {
        var f=progressFixture(Material.WHEAT,7);new PlacedBlocks().add(f.block());f.listener().onBreak(f.event());
        verify(f.manager()).progress(f.player(),com.cquests.model.ObjectiveType.HARVEST,"WHEAT",1);
        verify(f.manager(),never()).progress(any(),eq(com.cquests.model.ObjectiveType.MINE),anyString(),anyInt());
    }
    @Test void immaturePlayerPlantedCropDoesNotCountForHarvest() {
        var f=progressFixture(Material.WHEAT,0);new PlacedBlocks().add(f.block());f.listener().onBreak(f.event());
        verifyNoInteractions(f.manager());
    }
    @Test void placedOreRemainsBlockedWhileNaturalOreCounts() {
        var placed=progressFixture(Material.DIAMOND_ORE,-1);new PlacedBlocks().add(placed.block());placed.listener().onBreak(placed.event());
        verifyNoInteractions(placed.manager());
        var natural=progressFixture(Material.DIAMOND_ORE,-1);natural.listener().onBreak(natural.event());
        verify(natural.manager()).progress(natural.player(),com.cquests.model.ObjectiveType.MINE,"DIAMOND_ORE",1);
    }
    private record ProgressFixture(ProgressListener listener,com.cquests.quest.QuestManager manager,
                                   org.bukkit.entity.Player player,Block block,org.bukkit.event.block.BlockBreakEvent event) {}
    private static ProgressFixture progressFixture(Material material,int age) {
        var plugin=mock(com.cquests.CQuestsPlugin.class);var manager=mock(com.cquests.quest.QuestManager.class);
        when(plugin.questManager()).thenReturn(manager);
        when(plugin.settings()).thenReturn(new com.cquests.Settings(new org.bukkit.configuration.file.YamlConfiguration()));
        Chunk chunk=mock(Chunk.class);PersistentDataContainer data=container();when(chunk.getPersistentDataContainer()).thenReturn(data);
        World world=mock(World.class);when(world.getMinHeight()).thenReturn(-64);Block block=block(chunk,world,1,64,1);
        when(block.getType()).thenReturn(material);
        if(age>=0){var crop=mock(org.bukkit.block.data.Ageable.class);when(crop.getAge()).thenReturn(age);when(crop.getMaximumAge()).thenReturn(7);when(block.getBlockData()).thenReturn(crop);}
        var player=mock(org.bukkit.entity.Player.class);var event=mock(org.bukkit.event.block.BlockBreakEvent.class);
        when(event.getBlock()).thenReturn(block);when(event.getPlayer()).thenReturn(player);
        return new ProgressFixture(new ProgressListener(plugin),manager,player,block,event);
    }
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
