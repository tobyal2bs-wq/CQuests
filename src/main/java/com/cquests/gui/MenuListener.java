package com.cquests.gui;

import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;

/** Locks the quest menu: no item can be moved in or out of it, whatever the click. */
public final class MenuListener implements Listener {
    private final org.bukkit.plugin.Plugin plugin;
    public MenuListener(org.bukkit.plugin.Plugin plugin){this.plugin=plugin;}
    private final java.util.Map<java.util.UUID,Object> queued=new java.util.concurrent.ConcurrentHashMap<>();
    @EventHandler public void quit(org.bukkit.event.player.PlayerQuitEvent event){queued.remove(event.getPlayer().getUniqueId());}

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
                Object token=new Object();var id=player.getUniqueId();if(queued.putIfAbsent(id,token)!=null)return;
                var scheduled=player.getScheduler().run(plugin, ignored->{
                    try{if(player.getOpenInventory().getTopInventory().getHolder(false)==menu)menu.click(slot,click);}
                    finally{queued.remove(id,token);}
                },()->queued.remove(id,token));
                if(scheduled==null)queued.remove(id,token);
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
