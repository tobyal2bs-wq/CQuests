package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import org.bukkit.block.Block;
import org.bukkit.entity.Player;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.inventory.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class FarmAnvilsTest {
    @Test void adminPermissionAloneCannotObtainTheOpAnvil(){
        var plugin=mock(CQuestsPlugin.class);when(plugin.getName()).thenReturn("CQuests");var farm=mock(FarmService.class);when(plugin.farm()).thenReturn(farm);
        var player=mock(Player.class);when(player.hasPermission("cquests.admin")).thenReturn(true);
        new FarmCommand(plugin).run(player,new String[]{"farm","anvil"});
        verify(farm,never()).anvilItem();verify(player,never()).getInventory();
    }
    @Test void opCommandGivesTheMarkedItemInsteadOfOpeningAnInventory(){
        var plugin=mock(CQuestsPlugin.class);when(plugin.getName()).thenReturn("CQuests");var farm=mock(FarmService.class);when(plugin.farm()).thenReturn(farm);
        var player=mock(Player.class);var inventory=mock(PlayerInventory.class);var item=mock(ItemStack.class);
        when(player.isOp()).thenReturn(true);when(player.getInventory()).thenReturn(inventory);when(inventory.firstEmpty()).thenReturn(0);when(farm.anvilItem()).thenReturn(item);
        new FarmCommand(plugin).run(player,new String[]{"farm","anvil"});verify(inventory).addItem(item);verify(player,never()).openInventory(any(Inventory.class));
    }
    @Test void nonOpCannotPlaceAMarkedAnvilEvenWhenTheyHaveItsItem(){
        var plugin=mock(CQuestsPlugin.class);var farm=mock(FarmService.class);when(plugin.farm()).thenReturn(farm);
        var event=mock(BlockPlaceEvent.class);var player=mock(Player.class);var item=mock(ItemStack.class);
        when(event.getItemInHand()).thenReturn(item);when(event.getPlayer()).thenReturn(player);when(farm.anvilItem(item)).thenReturn(true);
        new FarmAnvils(plugin).place(event);verify(event).setCancelled(true);verify(farm,never()).addUpgrader(any());
    }
    @Test void onlyRegisteredStationsAreProtectedFromBreaksAndExplosions(){
        var plugin=mock(CQuestsPlugin.class);var farm=mock(FarmService.class);when(plugin.farm()).thenReturn(farm);
        var station=mock(Block.class);var ordinary=mock(Block.class);when(farm.upgrader(station)).thenReturn(true);
        var broken=mock(BlockBreakEvent.class);when(broken.getBlock()).thenReturn(station);when(broken.getPlayer()).thenReturn(mock(Player.class));
        var listener=new FarmAnvils(plugin);listener.protect(broken);verify(broken).setCancelled(true);
        var explosion=mock(EntityExplodeEvent.class);var blocks=new ArrayList<>(List.of(station,ordinary));when(explosion.blockList()).thenReturn(blocks);
        listener.explode(explosion);assertEquals(List.of(ordinary),blocks);
    }
}
