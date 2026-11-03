package com.cquests.listener;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.npc.NpcTag;
import com.cquests.util.Sched;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.entity.EntityTransformEvent;
import org.bukkit.event.entity.VillagerAcquireTradeEvent;
import org.bukkit.event.entity.VillagerCareerChangeEvent;
import org.bukkit.event.player.AsyncPlayerPreLoginEvent;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.world.EntitiesLoadEvent;
import org.bukkit.inventory.EquipmentSlot;

/** Clicks on NPCs, NPC protection, the WorldGuard spawn bypass, and player data loading. */
public final class NpcListener implements Listener {

    private final CQuestsPlugin plugin;
    private final java.util.Map<java.util.UUID,Long> clicks=new java.util.concurrent.ConcurrentHashMap<>();

    public NpcListener(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    /**
     * WorldGuard (mob-spawning / deny-spawn flags) and similar plugins cancel spawns at HIGH or lower.
     * Our villagers are tagged before the event fires, so we simply undo that cancel.
     */
    @EventHandler(priority = EventPriority.HIGHEST)
    public void onSpawn(EntitySpawnEvent event) {
        if (event.isCancelled() && NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(false);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void onCreatureSpawn(org.bukkit.event.entity.CreatureSpawnEvent event) {
        if (NpcTag.isNpc(event.getEntity())) event.setCancelled(false);
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onInteract(PlayerInteractEntityEvent event) {
        Entity clicked = event.getRightClicked();
        String npcId = NpcTag.npcId(clicked);
        if (npcId == null) {
            return;
        }
        event.setCancelled(true); // no trading screen
        if (event.getHand() != EquipmentSlot.HAND) {
            return;
        }
        var player=event.getPlayer();var point=plugin.spawns().points().get(npcId);var anchor=point==null?null:point.location();
        if(!plugin.spawns().isCurrent(npcId,clicked)||anchor==null||!anchor.getWorld().equals(player.getWorld())||anchor.distanceSquared(player.getLocation())>64)return;
        long now=System.nanoTime();if(now<clicks.getOrDefault(player.getUniqueId(),0L))return;clicks.put(player.getUniqueId(),now+150_000_000L);
        NpcDef npc = plugin.npcs().get(npcId);
        if (npc != null && plugin.questManager().shouldSee(plugin.questManager().data(player),npc)) {
            String role=plugin.farm().role(npc.id());
            boolean merchant=plugin.quests().storyFrom(npc.id()).isEmpty();
            boolean sneak=com.cquests.merchant.MerchantService.editGesture(player);
            if(role!=null&&(merchant?!sneak:sneak)){
                plugin.send(player,"<yellow>Right-click the Fieldsmith Anvil to upgrade your hoe. Enter the fields to collect your stored tool.");
                return;
            }
            plugin.dialogue().onClick(event.getPlayer(), npc, clicked);
        }
    }

    @EventHandler(priority=EventPriority.LOWEST)
    public void onInteractAt(org.bukkit.event.player.PlayerInteractAtEntityEvent event){onInteract(event);}

    @EventHandler(priority=EventPriority.HIGHEST,ignoreCancelled=false)
    public void onVehicle(org.bukkit.event.vehicle.VehicleEnterEvent event){if(NpcTag.isNpc(event.getEntered()))event.setCancelled(true);}

    @EventHandler(priority = EventPriority.LOWEST)
    public void onDamage(EntityDamageEvent event) {
        if (NpcTag.isNpc(event.getEntity())
                || (event instanceof EntityDamageByEntityEvent byEntity && plugin.finale().isShowFirework(byEntity.getDamager()))) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onCombust(EntityCombustEvent event) {
        if (NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onTransform(EntityTransformEvent event) {
        if (NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onCareer(VillagerCareerChangeEvent event) {
        if (NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(true);
        }
    }

    @EventHandler(priority = EventPriority.LOWEST)
    public void onTrade(VillagerAcquireTradeEvent event) {
        if (NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(true);
        }
    }

    // No EntityMoveEvent listener on purpose: having one makes Paper fire that event for every moving
    // mob on the server. The spawn check puts a shoved NPC back on its spot instead.

    /** Removes leftover NPC entities, e.g. from a crash, that are not the tracked live copy. */
    @EventHandler
    public void onEntitiesLoad(EntitiesLoadEvent event) {
        for (Entity entity : event.getEntities()) {
            String npcId = NpcTag.npcId(entity);
            if (npcId != null && !plugin.spawns().isCurrent(npcId, entity)) {
                entity.remove();
            }
        }
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void onPreLogin(AsyncPlayerPreLoginEvent event) {
        if (event.getLoginResult() == AsyncPlayerPreLoginEvent.Result.ALLOWED) {
            plugin.store().get(event.getUniqueId()); // load from disk off the main thread
        }
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent event) {
        Player player = event.getPlayer();
        plugin.store().get(player.getUniqueId());
        plugin.progression().initialize(player);
        plugin.farm().update(player);
        Sched.entityLater(player, 40, () -> {
            plugin.mail().notifyNew(player);
            plugin.finale().restoreIfNeeded(player);
            plugin.questManager().giveWelcome(player);
            plugin.visibility().refresh(player);
            plugin.tracker().update(player);
            plugin.finale().achievements().sync(player);
        });
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent event) {
        plugin.mail().forget(event.getPlayer());
        clicks.remove(event.getPlayer().getUniqueId());
        plugin.dialogue().forget(event.getPlayer());
        plugin.speech().stop(event.getPlayer());
        plugin.tracker().forget(event.getPlayer());
        plugin.shield().forget(event.getPlayer());
        plugin.store().unload(event.getPlayer().getUniqueId());
    }
}
