package com.cquests.quest;

import com.cquests.CQuestsPlugin;
import com.cquests.data.*;
import com.cquests.farm.FarmService;
import com.cquests.model.*;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.*;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class RewardGuardsTest {
    @Test void incompleteAndReplayedQuestCannotPayRewards() {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);PlayerStore store=mock(PlayerStore.class);
        when(plugin.store()).thenReturn(store);Player player=mock(Player.class);UUID id=UUID.randomUUID();
        when(player.getUniqueId()).thenReturn(id);PlayerData data=new PlayerData(id);when(store.get(id)).thenReturn(data);
        Quest quest=mock(Quest.class);when(quest.id()).thenReturn("test");
        Objective objective=mock(Objective.class);when(objective.amount()).thenReturn(10);
        when(quest.objectives()).thenReturn(List.of(objective));
        QuestManager manager=new QuestManager(plugin);
        manager.complete(player,quest); // stale response after removal
        data.start(new ActiveQuest("test",1,0));manager.complete(player,quest); // active but unfinished
        assertTrue(data.isActive("test"));verify(plugin,never()).finale();verify(store,never()).saveNow(any());
    }
    @Test void deliveryCannotConsumeReusableBoundTool() throws Exception {
        CQuestsPlugin plugin=mock(CQuestsPlugin.class);FarmService farm=mock(FarmService.class);
        when(plugin.farm()).thenReturn(farm);PlayerInventory inventory=mock(PlayerInventory.class);
        ItemStack bound=mock(ItemStack.class),normal=mock(ItemStack.class);
        when(bound.getType()).thenReturn(Material.WOODEN_HOE);when(normal.getType()).thenReturn(Material.WOODEN_HOE);
        when(normal.getAmount()).thenReturn(1);when(farm.marked(bound)).thenReturn(true);
        when(inventory.getStorageContents()).thenReturn(new ItemStack[]{bound,normal});
        var take=QuestManager.class.getDeclaredMethod("take",PlayerInventory.class,Set.class,int.class);take.setAccessible(true);
        assertEquals(1,take.invoke(new QuestManager(plugin),inventory,Set.of(Material.WOODEN_HOE),2));
        verify(inventory,never()).setItem(eq(0),any());verify(inventory).setItem(1,null);
    }
}
