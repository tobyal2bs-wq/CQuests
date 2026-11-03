package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import org.bukkit.entity.FallingBlock;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.EquipmentSlot;

/** OP-placed persistent stations; ordinary anvils never open the farming inventory. */
public final class FarmAnvils implements Listener {
    private final CQuestsPlugin plugin;
    public FarmAnvils(CQuestsPlugin plugin){this.plugin=plugin;}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void place(BlockPlaceEvent event){
        if(!plugin.farm().anvilItem(event.getItemInHand()))return;
        if(!event.getPlayer().isOp()){event.setCancelled(true);plugin.send(event.getPlayer(),"<red>Only OPs can place a Fieldsmith Anvil.");return;}
        if(!event.getBlock().getRelative(0,-1,0).getType().isSolid()){event.setCancelled(true);plugin.send(event.getPlayer(),"<yellow>Place the Fieldsmith Anvil on a solid floor.");return;}
        try{plugin.farm().addUpgrader(event.getBlock().getLocation());plugin.send(event.getPlayer(),"<green>Fieldsmith Anvil placed. Right-click to open hoe upgrades.");}
        catch(RuntimeException failure){event.setCancelled(true);plugin.getLogger().warning("Could not save Fieldsmith Anvil placement.");plugin.send(event.getPlayer(),"<red>The anvil could not be saved. Placement cancelled.");}
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void interact(PlayerInteractEvent event){
        if(event.getHand()!=EquipmentSlot.HAND||event.getAction()!=Action.RIGHT_CLICK_BLOCK||!plugin.farm().upgrader(event.getClickedBlock()))return;
        event.setCancelled(true);var player=event.getPlayer();
        var point=new FarmService.Spot(event.getClickedBlock().getWorld().getName(),event.getClickedBlock().getX(),event.getClickedBlock().getY(),event.getClickedBlock().getZ());
        if(plugin.farm().validUpgrader(player,point))Sched.entity(player,()->FarmMenu.open(plugin,player));
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void protect(BlockBreakEvent event){if(plugin.farm().upgrader(event.getBlock())&&!event.getPlayer().isOp()){event.setCancelled(true);plugin.send(event.getPlayer(),"<yellow>Only an OP can remove this Fieldsmith Anvil.");}}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true)
    public void removed(BlockBreakEvent event){if(plugin.farm().upgrader(event.getBlock()))try{plugin.farm().removeUpgrader(event.getBlock().getLocation());}catch(RuntimeException failure){plugin.getLogger().warning("Fieldsmith Anvil removed from memory, but its configuration could not be saved.");}}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void explode(EntityExplodeEvent event){event.blockList().removeIf(plugin.farm()::upgrader);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void explode(BlockExplodeEvent event){event.blockList().removeIf(plugin.farm()::upgrader);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=true)
    public void falling(EntityChangeBlockEvent event){if(plugin.farm().upgrader(event.getBlock())){event.setCancelled(true);if(event.getEntity() instanceof FallingBlock block)Sched.entity(block,block::remove);}}
}
