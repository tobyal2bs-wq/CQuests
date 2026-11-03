package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import com.cquests.npc.NpcTag;
import com.cquests.util.Sched;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.world.ChunkLoadEvent;
import org.bukkit.inventory.ItemStack;

public final class FarmListener implements Listener {
    private final CQuestsPlugin plugin;
    public FarmListener(CQuestsPlugin plugin){this.plugin=plugin;}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void interact(PlayerInteractEvent e){
        boolean mainHand=e.getHand()==org.bukkit.inventory.EquipmentSlot.HAND;
        Player p=e.getPlayer();var block=e.getClickedBlock();
        if(mainHand&&block!=null&&plugin.farmCommand().wand(e.getItem())&&p.hasPermission("cquests.admin")){
            e.setCancelled(true);plugin.farmCommand().point(p,block,e.getAction()==Action.RIGHT_CLICK_BLOCK);return;
        }
        if(plugin.farm().marked(e.getItem())){
            e.setCancelled(true);
            if(mainHand&&block!=null&&e.getAction()==Action.LEFT_CLICK_BLOCK)plugin.farm().harvest(p,block);
            if(!plugin.farm().inFarm(p))plugin.farm().strip(p);
        }else if(plugin.farm().inFarm(p)&&e.getAction()==Action.RIGHT_CLICK_BLOCK){
            // No containers, shops or workstations can take the bound tool inside a field.
            if(block!=null&&block.getState() instanceof org.bukkit.inventory.InventoryHolder)e.setCancelled(true);
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void breakBlock(BlockBreakEvent e){
        if(plugin.farm().marked(e.getPlayer().getInventory().getItemInMainHand())){
            e.setCancelled(true);plugin.farm().harvest(e.getPlayer(),e.getBlock());
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void damage(BlockDamageEvent e){if(plugin.farm().marked(e.getItemInHand())){e.setCancelled(true);plugin.farm().harvest(e.getPlayer(),e.getBlock());}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void fade(BlockFadeEvent e){
        if(e.getBlock().getType()==Material.FARMLAND&&plugin.farm().pendingRegrowth(e.getBlock().getRelative(0,1,0).getLocation()))
            e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void drop(PlayerDropItemEvent e){if(plugin.farm().marked(e.getItemDrop().getItemStack()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void spawn(ItemSpawnEvent e){if(plugin.farm().marked(e.getEntity().getItemStack()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void durability(PlayerItemDamageEvent e){if(plugin.farm().marked(e.getItem()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void pickup(EntityPickupItemEvent e){if(plugin.farm().marked(e.getItem().getItemStack())){e.setCancelled(true);e.getItem().remove();}}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void inventory(InventoryClickEvent e){
        if(!(e.getWhoClicked() instanceof Player p))return;
        ItemStack hotbar=e.getHotbarButton()>=0?p.getInventory().getItem(e.getHotbarButton()):null;
        ItemStack offhand=e.getClick()==ClickType.SWAP_OFFHAND?p.getInventory().getItemInOffHand():null;
        if(plugin.farm().marked(e.getCurrentItem())||plugin.farm().marked(e.getCursor())||plugin.farm().marked(hotbar)||plugin.farm().marked(offhand)){
            e.setCancelled(true);if(!plugin.farm().inFarm(p))Sched.entity(p,()->plugin.farm().strip(p));
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void transfer(InventoryMoveItemEvent e){if(plugin.farm().marked(e.getItem()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void drag(InventoryDragEvent e){if(plugin.farm().marked(e.getOldCursor())||e.getNewItems().values().stream().anyMatch(plugin.farm()::marked))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void swap(PlayerSwapHandItemsEvent e){if(plugin.farm().marked(e.getMainHandItem())||plugin.farm().marked(e.getOffHandItem()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void command(PlayerCommandPreprocessEvent e){
        if(plugin.farm().blockCommands()&&plugin.farm().inFarm(e.getPlayer())&&!e.getPlayer().hasPermission("cquests.admin")){
            String[] command=e.getMessage().split(" ");
            if(command.length==3&&command[0].equalsIgnoreCase("/quests")&&command[1].equalsIgnoreCase("respond")
                    &&plugin.dialogue().hasResponse(e.getPlayer(),command[2]))return;
            e.setCancelled(true);plugin.send(e.getPlayer(),"<yellow>Leave the harvest grounds before using commands.");
        }
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void entity(PlayerInteractEntityEvent e){
        Player p=e.getPlayer();
        if(NpcTag.npcId(e.getRightClicked())==null&&(plugin.farm().inFarm(p)
                ||plugin.farm().marked(p.getInventory().getItemInMainHand())
                ||plugin.farm().marked(p.getInventory().getItemInOffHand())))e.setCancelled(true);
    }
    @EventHandler(priority=EventPriority.HIGHEST)
    public void entityAt(PlayerInteractAtEntityEvent e){entity(e);}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void weapon(EntityDamageByEntityEvent e){if(e.getDamager() instanceof Player p&&plugin.farm().marked(p.getInventory().getItemInMainHand()))e.setCancelled(true);}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void move(PlayerMoveEvent e){if(e.hasChangedBlock())plugin.farm().update(e.getPlayer(),false);}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void teleport(PlayerTeleportEvent e){Sched.entity(e.getPlayer(),()->plugin.farm().update(e.getPlayer()));}
    @EventHandler(priority=EventPriority.HIGHEST)
    public void death(PlayerDeathEvent e){e.getDrops().removeIf(plugin.farm()::marked);plugin.farm().strip(e.getEntity());}
    @EventHandler public void quit(PlayerQuitEvent e){plugin.farm().forget(e.getPlayer());plugin.farmCommand().forget(e.getPlayer());}
    @EventHandler public void chunk(ChunkLoadEvent e){plugin.farm().restoreChunk(e.getWorld(),e.getChunk().getX(),e.getChunk().getZ());}
    @EventHandler public void respawn(PlayerRespawnEvent e){Sched.entityLater(e.getPlayer(),2,()->{plugin.farm().update(e.getPlayer());plugin.farm().equip(e.getPlayer());});}
}
