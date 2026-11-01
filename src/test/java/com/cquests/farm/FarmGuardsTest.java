package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.junit.jupiter.api.Test;
import static org.mockito.Mockito.*;

class FarmGuardsTest {
    @Test void armorStandCannotTakeBoundToolDuringExitCleanup() {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);FarmService farm=mock(FarmService.class);
        when(plugin.farm()).thenReturn(farm);Player player=mock(Player.class);
        PlayerInventory inventory=mock(PlayerInventory.class);when(player.getInventory()).thenReturn(inventory);
        ItemStack hoe=mock(ItemStack.class);when(inventory.getItemInMainHand()).thenReturn(hoe);when(farm.marked(hoe)).thenReturn(true);
        var event=mock(org.bukkit.event.player.PlayerInteractAtEntityEvent.class);when(event.getPlayer()).thenReturn(player);
        try(var tag=mockStatic(com.cquests.npc.NpcTag.class)){
            new FarmListener(plugin).entityAt(event);verify(event).setCancelled(true);
        }
    }
    @Test void unreachableCropCannotAwardOrQueueHarvest() {
        FarmService farm=mock(FarmService.class,CALLS_REAL_METHODS);
        Player player=mock(Player.class);org.bukkit.World world=mock(org.bukkit.World.class);
        org.bukkit.block.Block block=mock(org.bukkit.block.Block.class);
        when(player.isOnline()).thenReturn(true);when(player.getGameMode()).thenReturn(org.bukkit.GameMode.SURVIVAL);
        when(player.getWorld()).thenReturn(world);when(block.getWorld()).thenReturn(world);
        when(player.getEyeLocation()).thenReturn(new org.bukkit.Location(world,0,65,0));
        when(block.getLocation()).thenReturn(new org.bukkit.Location(world,100,64,0));
        farm.harvest(player,block);verify(player,never()).getInventory();verify(block,never()).getType();
    }
    @Test void creativeModeCannotGenerateFarmRewards() {
        FarmService farm=mock(FarmService.class,CALLS_REAL_METHODS);Player player=mock(Player.class);
        when(player.isOnline()).thenReturn(true);when(player.getGameMode()).thenReturn(org.bukkit.GameMode.CREATIVE);
        farm.harvest(player,mock(org.bukkit.block.Block.class));verify(player,never()).getInventory();
    }
    @Test void offhandSwapCannotPutBoundHoeIntoContainer() {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);FarmService farm=mock(FarmService.class);
        when(plugin.farm()).thenReturn(farm);Player player=mock(Player.class);
        PlayerInventory inventory=mock(PlayerInventory.class);when(player.getInventory()).thenReturn(inventory);
        ItemStack hoe=mock(ItemStack.class);when(inventory.getItemInOffHand()).thenReturn(hoe);
        when(farm.marked(hoe)).thenReturn(true);when(farm.inFarm(player)).thenReturn(true);
        InventoryClickEvent event=mock(InventoryClickEvent.class);
        when(event.getWhoClicked()).thenReturn(player);when(event.getHotbarButton()).thenReturn(-1);
        when(event.getClick()).thenReturn(ClickType.SWAP_OFFHAND);
        new FarmListener(plugin).inventory(event);
        verify(event).setCancelled(true);
    }
    @Test void hopperTransferCannotMoveBoundHoe() {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);FarmService farm=mock(FarmService.class);
        when(plugin.farm()).thenReturn(farm);ItemStack hoe=mock(ItemStack.class);
        when(farm.marked(hoe)).thenReturn(true);InventoryMoveItemEvent event=mock(InventoryMoveItemEvent.class);
        when(event.getItem()).thenReturn(hoe);new FarmListener(plugin).transfer(event);
        verify(event).setCancelled(true);
    }
}
