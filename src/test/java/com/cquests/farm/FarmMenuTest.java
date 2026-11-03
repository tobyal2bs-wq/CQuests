package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.gui.QuestMenu;
import com.cquests.progression.Progression;
import com.cquests.quest.QuestManager;
import net.kyori.adventure.text.Component;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.*;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class FarmMenuTest {
    @Test void reviewingCostsNothingAndOldBuyClicksCannotBuyTheFollowingTier() {
        var plugin=mock(CQuestsPlugin.class);var farm=mock(FarmService.class);
        var quests=mock(QuestManager.class);var levels=mock(Progression.class);
        var player=mock(Player.class);var data=mock(PlayerData.class);var inventory=mock(Inventory.class);
        when(plugin.farm()).thenReturn(farm);when(plugin.questManager()).thenReturn(quests);
        when(plugin.progression()).thenReturn(levels);when(quests.data(player)).thenReturn(data);
        var station=new FarmService.Spot("world",0,64,0);when(farm.nearbyUpgrader(player)).thenReturn(station);when(farm.validUpgrader(player,station)).thenReturn(true);
        when(levels.level(data)).thenReturn(100);when(data.hoeTier()).thenReturn(1);
        for(int i=1;i<=3;i++)when(farm.tier(i)).thenReturn(new FarmService.Tier(i,"Hoe "+i,Material.WOODEN_HOE,5000,1,1.2,0,5));
        try(var bukkit=mockStatic(Bukkit.class);var items=mockStatic(QuestMenu.class)) {
            bukkit.when(()->Bukkit.createInventory(any(InventoryHolder.class),eq(45),any(Component.class))).thenReturn(inventory);
            items.when(()->QuestMenu.item(any(),anyString(),anyList())).thenReturn(mock(ItemStack.class));
            FarmMenu.open(plugin,player);
            var holder=ArgumentCaptor.forClass(InventoryHolder.class);
            bukkit.verify(()->Bukkit.createInventory(holder.capture(),eq(45),any(Component.class)));
            var menu=(FarmMenu)holder.getValue();
            verify(farm,never()).purchase(any(),anyInt());
            menu.click(24,ClickType.LEFT);
            verify(farm,never()).purchase(any(),anyInt());
            when(farm.purchase(player,2)).thenAnswer(invocation->{when(data.hoeTier()).thenReturn(2);return true;});
            menu.click(34,ClickType.LEFT);
            for(int i=0;i<20;i++)menu.click(34,ClickType.LEFT);
            verify(farm,times(1)).purchase(player,2);verify(farm,never()).purchase(player,3);
            menu.click(24,ClickType.LEFT);menu.click(34,ClickType.LEFT);
            verify(farm).purchase(player,3);
        }
    }
    @Test void noStationCannotOpenTheUpgradeInventory(){
        var plugin=mock(CQuestsPlugin.class);var farm=mock(FarmService.class);var player=mock(Player.class);when(plugin.farm()).thenReturn(farm);
        FarmMenu.open(plugin,player);verify(player,never()).openInventory(any(Inventory.class));verify(farm,never()).purchase(any(),anyInt());
    }
}
