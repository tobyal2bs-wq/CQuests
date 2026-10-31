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
        if (!(event.getView().getTopInventory().getHolder(false) instanceof LockedMenu menu)) {
            return;
        }
        event.setCancelled(true);
        if (event.getWhoClicked().getUniqueId().equals(menu.viewer())
                && event.getClickedInventory() == event.getView().getTopInventory()
                && (event.isLeftClick() || event.isRightClick())) {
            int slot = event.getRawSlot();
            var click = event.getClick();
            if (event.getWhoClicked() instanceof org.bukkit.entity.Player player) {
                com.cquests.util.Sched.entity(player, () -> {
                    if (player.getOpenInventory().getTopInventory().getHolder(false) == menu) menu.click(slot, click);
                });
            }
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onDrag(InventoryDragEvent event) {
        if (event.getView().getTopInventory().getHolder(false) instanceof LockedMenu) {
            event.setCancelled(true);
        }
    }
}
