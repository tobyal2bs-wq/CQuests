package com.cquests.gui;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.npc.SpawnManager;
import com.cquests.util.Text;
import org.bukkit.Location;
import org.bukkit.entity.Player;

/** Navigation reads saved coordinates, never another region's live NPC entity. */
public final class Directions {
    private static final String[] ARROWS = {"↑", "↗", "→", "↘", "↓", "↙", "←", "↖"};
    private final CQuestsPlugin plugin;

    public Directions(CQuestsPlugin plugin) { this.plugin = plugin; }

    public boolean enabled(Player player) {
        PlayerData data = plugin.store().cached(player.getUniqueId());
        return data != null && data.directionsOn(plugin.settings().directionsDefault);
    }

    public boolean toggle(Player player) {
        PlayerData data = plugin.questManager().data(player);
        data.setDirectionsOn(!enabled(player));
        plugin.store().saveNow(data);
        if (!enabled(player)) player.sendActionBar(net.kyori.adventure.text.Component.empty());
        update(player);
        return enabled(player);
    }

    public String target(Player player) {
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data == null) return null;
        Quest quest = plugin.tracker().pick(player, data);
        if (quest == null) {
            Quest next = plugin.questManager().nextStoryQuest(data);
            return next == null ? null : next.giver();
        }
        ActiveQuest active = data.active(quest.id());
        if (active == null) return null;
        if (plugin.questManager().ready(quest, active)) return quest.turnIn();
        for (int i = 0; i < quest.objectives().size(); i++) {
            var objective = quest.objectives().get(i);
            if (!plugin.questManager().objectiveDone(quest, active, i)
                    && (objective.type() == ObjectiveType.TALK || objective.type() == ObjectiveType.DELIVER)) return objective.npc();
        }
        return quest.giver();
    }

    public void update(Player player) {
        if (!enabled(player)) return;
        String id = target(player);
        var npc = plugin.npcs().get(id);
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (npc == null || data == null || !plugin.questManager().shouldSee(data, npc)) return;
        SpawnManager.Point point = plugin.spawns().points().get(npc.id());
        if (point == null) {
            player.sendActionBar(Text.mm("<white>" + Text.escape(npc.name()) + " • awaiting placement</white>"));
            return;
        }
        if (!point.world().equals(player.getWorld().getName())) {
            player.sendActionBar(Text.mm("<white>" + Text.escape(npc.name()) + " • in " + Text.escape(point.world()) + "</white>"));
            return;
        }
        Location from = player.getLocation();
        double dx = point.x() - from.getX(), dz = point.z() - from.getZ(), dy = point.y() - from.getY();
        long meters = Math.round(Math.sqrt(dx * dx + dy * dy + dz * dz));
        String vertical = Math.abs(dy) > 4 ? (dy > 0 ? " • above you" : " • below you") : "";
        player.sendActionBar(Text.mm("<white><bold>" + arrow(dx, dz, from.getYaw()) + "</bold> "
                + Text.escape(npc.name()) + " <aqua>" + meters + " m</aqua>" + vertical + "</white>"));
    }

    public static String arrow(double dx, double dz, float yaw) {
        double targetYaw = Math.toDegrees(Math.atan2(-dx, dz));
        return ARROWS[Math.floorMod((int) Math.round((yaw - targetYaw) / 45.0), 8)];
    }
}
