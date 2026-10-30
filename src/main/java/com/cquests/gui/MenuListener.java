package com.cquests.gui;

import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;

/** Locks the quest menu: no item can be moved in or out of it, whatever the click. */
public final class MenuListener implements Listener {

    @EventHandler(priority = EventPriority.LOWEST)
    public void onClick(InventoryClickEvent event) {
        if (!(event.getView().getTopInventory().getHolder(false) instanceof QuestMenu menu)) {
            return;
        }
        event.setCancelled(true);
        if (event.getClickedInventory() == event.getView().getTopInventory()) {
            menu.click(event.getRawSlot(), event.getClick());
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onDrag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder(false) instanceof QuestMenu) {
            event.setCancelled(true);
        }
    }
}
