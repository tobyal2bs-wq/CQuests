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

    /** Last compass target per player, so the compass packet is only sent when the target changes. */
    private final java.util.Map<java.util.UUID, String> compass = new java.util.concurrent.ConcurrentHashMap<>();

    public Directions(CQuestsPlugin plugin) { this.plugin = plugin; }

    public void forget(Player player) { compass.remove(player.getUniqueId()); }

    private static final String[] COMPASS = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};

    /** "north-east": the direction from one point to another, as a compass word. */
    public static String heading(double dx, double dz) {
        double yaw = Math.toDegrees(Math.atan2(-dx, dz));
        return COMPASS[Math.floorMod((int) Math.round(yaw / 45.0), 8)];
    }

    /**
     * /quests where: tells the player who to visit next and where they stand, in chat. Also used on
     * the first join, so a new player knows where villager number one is.
     */
    public void explain(Player player, boolean withHint) {
        String id = target(player);
        var npc = id == null ? null : plugin.npcs().get(id);
        if (npc == null) { plugin.send(player, "<gray>Nobody is waiting for you right now. Open <yellow>/quests</yellow> to see your journal."); return; }
        String name = plugin.npcs().mention(npc.id());
        SpawnManager.Point point = plugin.spawns().points().get(npc.id());
        if (point == null) { plugin.send(player, "<white>Next: " + name + " <gray>(not placed in the world yet; ask an admin)"); return; }
        if (!point.world().equals(player.getWorld().getName())) {
            plugin.send(player, "<white>Next: " + name + " <gray>in <white>" + Text.escape(point.world()) + "</white> at <white>" + (int) point.x() + ", " + (int) point.y() + ", " + (int) point.z());
            return;
        }
        Location from = player.getLocation();
        double dx = point.x() - from.getX(), dz = point.z() - from.getZ(), dy = point.y() - from.getY();
        long meters = Math.round(Math.sqrt(dx * dx + dy * dy + dz * dz));
        plugin.send(player, "<white>Next: " + name + " <gray>• <aqua>" + meters + " m " + heading(dx, dz) + "</aqua> <gray>at <white>"
                + (int) point.x() + ", " + (int) point.y() + ", " + (int) point.z() + "</white>");
        if (withHint) plugin.send(player, "<gray>Your compass points to them" + (enabled(player) ? " and the arrow above your hotbar shows the way." : ". <yellow><click:run_command:'/quests directions'>Click here</click></yellow> for an arrow above your hotbar."));
    }

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
        pointCompass(player, npc.id(), point);
        double dx = point.x() - from.getX(), dz = point.z() - from.getZ(), dy = point.y() - from.getY();
        long meters = Math.round(Math.sqrt(dx * dx + dy * dy + dz * dz));
        String vertical = Math.abs(dy) > 4 ? (dy > 0 ? " • above you" : " • below you") : "";
        player.sendActionBar(Text.mm("<white><bold>" + arrow(dx, dz, from.getYaw()) + "</bold> "
                + Text.escape(npc.name()) + " <aqua>" + meters + " m</aqua>" + vertical + "</white>"));
    }

    /** Points the player's own compass at the villager (per player, no item needed); only on change. */
    private void pointCompass(Player player, String id, SpawnManager.Point point) {
        String key = id + "@" + point.world() + ";" + (int) point.x() + ";" + (int) point.z();
        if (key.equals(compass.put(player.getUniqueId(), key))) return;
        player.setCompassTarget(new Location(player.getWorld(), point.x(), point.y(), point.z()));
    }

    /** Keeps the compass on the next villager even for players who turned the arrow off. Cheap: no packet unless it changed. */
    public void updateCompass(Player player) {
        String id = target(player);
        var npc = id == null ? null : plugin.npcs().get(id);
        if (npc == null) return;
        SpawnManager.Point point = plugin.spawns().points().get(npc.id());
        if (point != null && point.world().equals(player.getWorld().getName())) pointCompass(player, npc.id(), point);
    }

    public static String arrow(double dx, double dz, float yaw) {
        double targetYaw = Math.toDegrees(Math.atan2(-dx, dz));
        return ARROWS[Math.floorMod((int) Math.round((yaw - targetYaw) / 45.0), 8)];
    }
}
