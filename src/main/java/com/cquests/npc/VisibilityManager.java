package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import org.bukkit.Bukkit;
import org.bukkit.Particle;
import org.bukkit.entity.Player;
import org.bukkit.entity.LivingEntity;

import java.util.Map;

/**
 * Decides who sees which NPC. Personal NPCs only show to players who need them for a quest, and any
 * villager a player has fully finished disappears for that player.
 */
public final class VisibilityManager {

    private final CQuestsPlugin plugin;

    public VisibilityManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    public void refresh(Player player) {
        Sched.entity(player, () -> apply(player));
    }

    public void refreshAll() {
        for (Player player : Bukkit.getOnlinePlayers()) {
            refresh(player);
        }
    }

    private void apply(Player player) {
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data == null) {
            return;
        }
        for (Map.Entry<String, LivingEntity> entry : plugin.spawns().live().entrySet()) {
            NpcDef npc = plugin.npcs().get(entry.getKey());
            if (npc != null && !npc.daily()) {
                show(player, entry.getValue(), plugin.questManager().shouldSee(data, npc));
            }
        }
    }

    /** An NPC was (re)spawned; show or hide it for everyone online. */
    public void onSpawn(NpcDef npc, LivingEntity villager) {
        if (npc.daily()) {
            return;
        }
        for (Player player : Bukkit.getOnlinePlayers()) {
            Sched.entity(player, () -> {
                PlayerData data = plugin.store().cached(player.getUniqueId());
                if (data != null) {
                    show(player, villager, plugin.questManager().shouldSee(data, npc));
                }
            });
        }
    }

    private void show(Player player, LivingEntity villager, boolean visible) {
        if (!villager.isValid()) {
            return;
        }
        if (visible) {
            player.showEntity(plugin, villager);
        } else {
            if (player.canSee(villager) && player.getWorld().equals(villager.getWorld())) {
                // A little puff of smoke, only for this player, so the villager doesn't just blink out.
                player.spawnParticle(Particle.POOF, villager.getLocation().add(0, 1, 0), 25, 0.3, 0.5, 0.3, 0.02);
            }
            player.hideEntity(plugin, villager);
        }
    }
}
