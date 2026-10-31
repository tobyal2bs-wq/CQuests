package com.cquests.listener;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.npc.NpcTag;
import com.cquests.util.Sched;
import io.papermc.paper.event.entity.EntityMoveEvent;
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
        NpcDef npc = plugin.npcs().get(npcId);
        if (npc != null) {
            plugin.dialogue().onClick(event.getPlayer(), npc, clicked);
        }
    }

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

    @EventHandler(priority = EventPriority.LOWEST)
    public void onMove(EntityMoveEvent event) {
        // AI is off, but pistons, water or explosions could still shove them.
        if (event.hasChangedBlock() && NpcTag.isNpc(event.getEntity())) {
            event.setCancelled(true);
        }
    }

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
        Sched.entityLater(player, 40, () -> {
            plugin.finale().restoreIfNeeded(player);
            plugin.questManager().giveWelcome(player);
            plugin.visibility().refresh(player);
            plugin.tracker().update(player);
            plugin.finale().achievements().sync(player);
        });
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent event) {
        plugin.dialogue().forget(event.getPlayer());
        plugin.tracker().forget(event.getPlayer());
        plugin.shield().forget(event.getPlayer());
        plugin.store().unload(event.getPlayer().getUniqueId());
    }
}
