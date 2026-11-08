package com.cquests.merchant;

import com.cquests.T;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import org.bukkit.entity.*;
import org.bukkit.event.*;
import org.bukkit.event.entity.*;
import org.bukkit.event.inventory.*;
import org.bukkit.event.player.*;
import org.bukkit.event.world.EntitiesLoadEvent;
import org.bukkit.inventory.EquipmentSlot;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public final class MerchantListener implements Listener {
    private final CQuestsPlugin plugin;private final Map<UUID,Long> clicks=new ConcurrentHashMap<>();private final Set<UUID> samples=ConcurrentHashMap.newKeySet();
    public MerchantListener(CQuestsPlugin plugin){this.plugin=plugin;}
    @EventHandler(priority=EventPriority.LOWEST,ignoreCancelled=false)
    public void interact(PlayerInteractEntityEvent e){
        String id=plugin.merchants().id(e.getRightClicked());if(id==null)return;e.setCancelled(true);
        if(e.getHand()!=EquipmentSlot.HAND||!plugin.merchants().current(e.getRightClicked()))return;
        Player p=e.getPlayer();long now=System.nanoTime();if(now<clicks.getOrDefault(p.getUniqueId(),0L))return;clicks.put(p.getUniqueId(),now+150_000_000L);
        boolean editing=MerchantService.editGesture(p);
        Sched.entity(p,()->plugin.merchants().interact(p,id,editing));
    }
    @EventHandler(priority=EventPriority.LOWEST,ignoreCancelled=false)
    public void interactAt(PlayerInteractAtEntityEvent e){interact(e);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void inventory(InventoryClickEvent e){
        var holder=e.getView().getTopInventory().getHolder(false);
        if(!(holder instanceof MerchantMenu)&&!(holder instanceof MerchantEditor))return;e.setCancelled(true);
        if(!(e.getWhoClicked() instanceof Player p)||!(holder instanceof MerchantEditor editor)||!p.getUniqueId().equals(editor.viewer())
                ||!MerchantService.canEdit(p)||e.getClickedInventory()!=p.getInventory()
                ||(e.getClick()!=ClickType.LEFT&&e.getClick()!=ClickType.RIGHT))return;
        var item=e.getCurrentItem();if(item==null||!samples.add(p.getUniqueId()))return;var copy=item.clone();
        var task=p.getScheduler().run(plugin,ignored->{try{if(p.getOpenInventory().getTopInventory().getHolder(false)==editor&&MerchantService.canEdit(p))editor.capture(copy);}finally{samples.remove(p.getUniqueId());}},()->samples.remove(p.getUniqueId()));
        if(task==null)samples.remove(p.getUniqueId());
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void drag(InventoryDragEvent e){var holder=e.getView().getTopInventory().getHolder(false);if(holder instanceof MerchantMenu||holder instanceof MerchantEditor)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void open(InventoryOpenEvent e){if(e.getInventory() instanceof org.bukkit.inventory.MerchantInventory inventory&&inventory.getMerchant() instanceof Entity entity&&plugin.merchants().id(entity)!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void wand(PlayerInteractEvent e){
        if(e.getHand()!=EquipmentSlot.HAND)return;String id=plugin.merchants().wandId(e.getItem());if(id==null||e.getClickedBlock()==null)return;
        e.setCancelled(true);Player p=e.getPlayer();if(!MerchantService.canEdit(p)){plugin.send(p,T.t("merchant-listener.only-operators-can-edit-merchant", "<red>Only operators can edit merchant routes."));return;}
        if(!p.getWorld().equals(e.getClickedBlock().getWorld())||p.getEyeLocation().distanceSquared(e.getClickedBlock().getLocation().add(.5,.5,.5))>36)return;
        if(e.getAction()==org.bukkit.event.block.Action.LEFT_CLICK_BLOCK)plugin.merchants().undo(p,id,false);
        else if(e.getAction()==org.bukkit.event.block.Action.RIGHT_CLICK_BLOCK)plugin.merchants().setPoint(p,id,"point",e.getClickedBlock().getLocation().add(.5,1,.5));
    }
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void spawn(CreatureSpawnEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(false);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void spawnEntity(EntitySpawnEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(false);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void vehicle(org.bukkit.event.vehicle.VehicleEnterEvent e){if(plugin.merchants().id(e.getEntered())!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void damage(EntityDamageEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void combust(EntityCombustEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void transform(EntityTransformEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void career(VillagerCareerChangeEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(true);}
    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void recipes(VillagerAcquireTradeEvent e){if(plugin.merchants().id(e.getEntity())!=null)e.setCancelled(true);}
    @EventHandler public void load(EntitiesLoadEvent e){for(Entity entity:e.getEntities())if(plugin.merchants().id(entity)!=null&&!plugin.merchants().current(entity))entity.remove();}
    @EventHandler public void quit(PlayerQuitEvent e){clicks.remove(e.getPlayer().getUniqueId());samples.remove(e.getPlayer().getUniqueId());plugin.merchants().forget(e.getPlayer());}
}
