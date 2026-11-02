package com.cquests.gui;

import io.papermc.paper.threadedregions.scheduler.*;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.*;
import org.bukkit.inventory.*;
import org.bukkit.plugin.Plugin;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import java.util.UUID;
import java.util.function.Consumer;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MenuQueueTest {
    @Test void packetBurstQueuesOneCallbackAndChecksHolderAgain(){
        Plugin plugin=mock(Plugin.class);MenuListener listener=new MenuListener(plugin);
        Player player=mock(Player.class);UUID id=UUID.randomUUID();when(player.getUniqueId()).thenReturn(id);
        LockedMenu menu=mock(LockedMenu.class);when(menu.viewer()).thenReturn(id);
        Inventory top=mock(Inventory.class);when(top.getHolder(false)).thenReturn(menu);
        InventoryView view=mock(InventoryView.class);when(view.getTopInventory()).thenReturn(top);when(player.getOpenInventory()).thenReturn(view);
        EntityScheduler scheduler=mock(EntityScheduler.class);when(player.getScheduler()).thenReturn(scheduler);
        when(scheduler.run(eq(plugin),any(),any())).thenReturn(mock(ScheduledTask.class));
        InventoryClickEvent event=mock(InventoryClickEvent.class);when(event.getView()).thenReturn(view);when(event.getWhoClicked()).thenReturn(player);
        when(event.getClickedInventory()).thenReturn(top);when(event.isLeftClick()).thenReturn(true);when(event.getRawSlot()).thenReturn(31);when(event.getClick()).thenReturn(ClickType.LEFT);
        for(int i=0;i<1000;i++)listener.onClick(event);
        @SuppressWarnings("unchecked") ArgumentCaptor<Consumer<ScheduledTask>> callback=ArgumentCaptor.forClass(Consumer.class);
        verify(scheduler).run(eq(plugin),callback.capture(),any());verify(event,times(1000)).setCancelled(true);
        callback.getValue().accept(mock(ScheduledTask.class));verify(menu).click(31,ClickType.LEFT);
        listener.onClick(event);verify(scheduler,times(2)).run(eq(plugin),callback.capture(),any());
        when(top.getHolder(false)).thenReturn(null);callback.getValue().accept(mock(ScheduledTask.class));verify(menu,times(1)).click(anyInt(),any());
    }
}
