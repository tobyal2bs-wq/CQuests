package com.cquests.listener;

import com.cquests.CQuestsPlugin;
import com.cquests.model.ObjectiveType;
import com.cquests.npc.NpcTag;
import org.bukkit.block.data.Ageable;
import org.bukkit.entity.Item;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.block.BlockPistonExtendEvent;
import org.bukkit.event.block.BlockPistonRetractEvent;
import org.bukkit.event.enchantment.EnchantItemEvent;
import org.bukkit.event.entity.CreatureSpawnEvent;
import org.bukkit.event.entity.EntityBreedEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityTameEvent;
import org.bukkit.event.inventory.CraftItemEvent;
import org.bukkit.event.inventory.FurnaceExtractEvent;
import org.bukkit.event.player.PlayerFishEvent;
import org.bukkit.event.player.PlayerItemConsumeEvent;
import org.bukkit.event.player.PlayerShearEntityEvent;
import org.bukkit.inventory.ItemStack;

/** Turns game events into quest progress. */
public final class ProgressListener implements Listener {

    private final CQuestsPlugin plugin;
    private final PlacedBlocks placed = new PlacedBlocks();

    public ProgressListener(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    private void count(Player player, ObjectiveType type, String key, int amount) {
        plugin.questManager().progress(player, type, key, amount);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onDeath(EntityDeathEvent event) {
        Player killer = event.getEntity().getKiller();
        if (killer == null || NpcTag.isNpc(event.getEntity())) {
            return;
        }
        // Mob farms on spawners would make kill quests trivial.
        CreatureSpawnEvent.SpawnReason reason = event.getEntity().getEntitySpawnReason();
        if (!plugin.settings().countSpawnerMobs
                && (reason == CreatureSpawnEvent.SpawnReason.SPAWNER || reason == CreatureSpawnEvent.SpawnReason.SPAWNER_EGG)) {
            return;
        }
        count(killer, ObjectiveType.KILL, event.getEntityType().name(), 1);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBreak(BlockBreakEvent event) {
        boolean playerPlaced = placed.remove(event.getBlock());
        if (playerPlaced && plugin.settings().ignorePlacedBlocks) {
            return;
        }
        String key = event.getBlock().getType().name();
        if (event.getBlock().getBlockData() instanceof Ageable crop && crop.getAge() >= crop.getMaximumAge()) {
            count(event.getPlayer(), ObjectiveType.HARVEST, key, 1);
        }
        count(event.getPlayer(), ObjectiveType.MINE, key, 1);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onPlace(BlockPlaceEvent event) {
        placed.add(event.getBlockPlaced());
        if (placed.firstPlacementAt(event.getBlockPlaced())) {
            count(event.getPlayer(), ObjectiveType.PLACE, event.getBlockPlaced().getType().name(), 1);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onExtend(BlockPistonExtendEvent event) { placed.move(event.getBlocks(),event.getDirection()); }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onRetract(BlockPistonRetractEvent event) { placed.move(event.getBlocks(),event.getDirection()); }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onCraft(CraftItemEvent event) {
        if (event.getAction() == org.bukkit.event.inventory.InventoryAction.NOTHING
                || event.getAction() == org.bukkit.event.inventory.InventoryAction.UNKNOWN) return;
        if (!(event.getWhoClicked() instanceof Player player)) {
            return;
        }
        ItemStack result = event.getRecipe().getResult();
        int times = 1;
        if (event.isShiftClick()) {
            int min = Integer.MAX_VALUE;
            for (ItemStack ingredient : event.getInventory().getMatrix()) {
                if (ingredient != null && !ingredient.getType().isAir()) {
                    min = Math.min(min, ingredient.getAmount());
                }
            }
            times = min == Integer.MAX_VALUE ? 1 : min;
            // Shift-click stops when the inventory is full; only count what actually fits.
            int fits = room(player, result) / Math.max(1, result.getAmount());
            times = Math.max(0, Math.min(times, fits));
        }
        count(player, ObjectiveType.CRAFT, result.getType().name(), result.getAmount() * times);
    }

    private static int room(Player player, ItemStack item) {
        int room = 0;
        int max = item.getMaxStackSize();
        for (ItemStack slot : player.getInventory().getStorageContents()) {
            if (slot == null || slot.getType().isAir()) {
                room += max;
            } else if (slot.isSimilar(item)) {
                room += Math.max(0, max - slot.getAmount());
            }
        }
        return room;
    }

    @EventHandler(priority = EventPriority.MONITOR)
    public void onSmelt(FurnaceExtractEvent event) {
        count(event.getPlayer(), ObjectiveType.SMELT, event.getItemType().name(), event.getItemAmount());
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onFish(PlayerFishEvent event) {
        if (event.getState() == PlayerFishEvent.State.CAUGHT_FISH && event.getCaught() instanceof Item item) {
            count(event.getPlayer(), ObjectiveType.FISH, item.getItemStack().getType().name(), item.getItemStack().getAmount());
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBreed(EntityBreedEvent event) {
        if (event.getBreeder() instanceof Player player) {
            count(player, ObjectiveType.BREED, event.getEntityType().name(), 1);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onTame(EntityTameEvent event) {
        if (event.getOwner() instanceof Player player) {
            count(player, ObjectiveType.TAME, event.getEntityType().name(), 1);
        }
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onShear(PlayerShearEntityEvent event) {
        count(event.getPlayer(), ObjectiveType.SHEAR, event.getEntity().getType().name(), 1);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onEnchant(EnchantItemEvent event) {
        count(event.getEnchanter(), ObjectiveType.ENCHANT, event.getItem().getType().name(), 1);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onConsume(PlayerItemConsumeEvent event) {
        count(event.getPlayer(), ObjectiveType.CONSUME, event.getItem().getType().name(), 1);
    }
}
