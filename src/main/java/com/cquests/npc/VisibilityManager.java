package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.entity.Villager;

import java.util.Map;

/** Shows personal NPCs only to the players who need them for a quest. */
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
        for (Map.Entry<String, Villager> entry : plugin.spawns().live().entrySet()) {
            NpcDef npc = plugin.npcs().get(entry.getKey());
            if (npc != null && npc.personal()) {
                show(player, entry.getValue(), plugin.questManager().shouldSee(data, npc));
            }
        }
    }

    /** A personal NPC was (re)spawned hidden; reveal it to everyone who should see it. */
    public void onSpawn(NpcDef npc, Villager villager) {
        if (!npc.personal()) {
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

    private void show(Player player, Villager villager, boolean visible) {
        if (!villager.isValid()) {
            return;
        }
        if (visible) {
            player.showEntity(plugin, villager);
        } else {
            player.hideEntity(plugin, villager);
        }
    }
}
