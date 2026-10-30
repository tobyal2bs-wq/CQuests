package com.cquests.listener;

import com.cquests.CQuestsPlugin;
import com.cquests.npc.NpcShield;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.event.Cancellable;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockExplodeEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.player.PlayerBucketEmptyEvent;
import org.bukkit.event.player.PlayerBucketFillEvent;

/** Enforces the {@link NpcShield} bubble around villagers. */
public final class ShieldListener implements Listener {

    private final CQuestsPlugin plugin;

    public ShieldListener(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    private NpcShield shield() {
        return plugin.shield();
    }

    private void guardBlock(Player player, Block block, Cancellable event) {
        if (!plugin.settings().shieldBuild || shield().bypass(player)) {
            return;
        }
        Location center = shield().protecting(block);
        if (center != null) {
            event.setCancelled(true);
            shield().warn(player, center);
        }
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onPlace(BlockPlaceEvent event) {
        guardBlock(event.getPlayer(), event.getBlockPlaced(), event);
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onBreak(BlockBreakEvent event) {
        guardBlock(event.getPlayer(), event.getBlock(), event);
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onBucketEmpty(PlayerBucketEmptyEvent event) {
        guardBlock(event.getPlayer(), event.getBlock(), event);
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onBucketFill(PlayerBucketFillEvent event) {
        guardBlock(event.getPlayer(), event.getBlock(), event);
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onEntityExplode(EntityExplodeEvent event) {
        if (plugin.settings().shieldBuild) {
            event.blockList().removeIf(block -> shield().protecting(block) != null);
        }
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onBlockExplode(BlockExplodeEvent event) {
        if (plugin.settings().shieldBuild) {
            event.blockList().removeIf(block -> shield().protecting(block) != null);
        }
    }

    /** No PvP inside the bubble, whether the attacker or the victim stands in it. */
    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onPvp(EntityDamageByEntityEvent event) {
        if (!plugin.settings().shieldPvp || !(event.getEntity() instanceof Player victim)) {
            return;
        }
        Player attacker = attacker(event.getDamager());
        if (attacker == null || attacker.equals(victim)) {
            return;
        }
        Location center = shield().protecting(victim.getLocation());
        if (center == null) {
            center = shield().protecting(attacker.getLocation());
        }
        if (center != null) {
            event.setCancelled(true);
            shield().warn(attacker, center);
        }
    }

    private static Player attacker(Entity damager) {
        if (damager instanceof Player player) {
            return player;
        }
        if (damager instanceof Projectile projectile && projectile.getShooter() instanceof Player shooter) {
            return shooter;
        }
        return null;
    }
}
