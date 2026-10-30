package com.cquests.gui;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.Objective;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.quest.QuestManager;
import com.cquests.util.Text;
import net.kyori.adventure.bossbar.BossBar;
import org.bukkit.entity.Player;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A boss bar at the top of the screen that follows one quest: its name, the next thing to do and how
 * far along it is. Boss bars work the same on Java and Bedrock and need no scoreboard, so they are safe on Folia.
 */
public final class Tracker {

    private final CQuestsPlugin plugin;
    private final Map<UUID, String> tracked = new ConcurrentHashMap<>();
    private final Map<UUID, BossBar> bars = new ConcurrentHashMap<>();
    private final Set<UUID> off = ConcurrentHashMap.newKeySet();

    public Tracker(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    public void track(Player player, String questId) {
        tracked.put(player.getUniqueId(), questId);
        update(player);
    }

    public String tracked(Player player) {
        return tracked.get(player.getUniqueId());
    }

    public boolean enabled(Player player) {
        return plugin.settings().trackerEnabled && !off.contains(player.getUniqueId());
    }

    /** Turns the bar on or off for this player and returns the new state. */
    public boolean toggle(Player player) {
        UUID id = player.getUniqueId();
        if (!off.remove(id)) {
            off.add(id);
        }
        update(player);
        return !off.contains(id);
    }

    public void update(Player player) {
        BossBar bar = bars.get(player.getUniqueId());
        PlayerData data = plugin.store().cached(player.getUniqueId());
        Quest quest = enabled(player) && data != null ? pick(player, data) : null;
        if (quest == null) {
            if (bar != null) {
                player.hideBossBar(bar);
            }
            return;
        }
        QuestManager qm = plugin.questManager();
        ActiveQuest active = data.active(quest.id());
        if (active == null) {
            return;
        }
        int done = 0;
        int total = 0;
        String next = null;
        List<Objective> objectives = quest.objectives();
        for (int i = 0; i < objectives.size(); i++) {
            Objective objective = objectives.get(i);
            int value = Math.min(objective.amount(), active.get(i));
            done += value;
            total += objective.amount();
            if (next == null && !qm.objectiveDone(quest, active, i)) {
                next = qm.objectiveLabel(objective) + " <yellow>" + value + "/" + objective.amount() + "</yellow>";
            }
        }
        boolean ready = qm.ready(quest, active);
        String step = ready ? "<green>Return to " + plugin.npcs().mention(quest.turnIn()) + "</green>" : next == null ? "" : "<gray>" + next;
        String name = "<white><bold>" + Text.escape(quest.name()) + "</bold></white> <dark_gray>»</dark_gray> " + step;
        float progress = ready ? 1f : total == 0 ? 0f : Math.min(1f, (float) done / total);
        BossBar.Color color = ready ? BossBar.Color.GREEN : quest.category() == QuestCategory.STORY ? BossBar.Color.YELLOW : BossBar.Color.BLUE;
        if (bar == null) {
            bar = BossBar.bossBar(Text.mm(name), progress, color, BossBar.Overlay.NOTCHED_10);
            bars.put(player.getUniqueId(), bar);
        } else {
            bar.name(Text.mm(name));
            bar.progress(progress);
            bar.color(color);
        }
        player.showBossBar(bar);
    }

    /** The chosen quest if it is still active, otherwise the story quest, otherwise any active quest. */
    private Quest pick(Player player, PlayerData data) {
        List<Quest> active = plugin.questManager().activeQuests(data);
        if (active.isEmpty()) {
            return null;
        }
        String chosen = tracked.get(player.getUniqueId());
        for (Quest quest : active) {
            if (quest.id().equals(chosen)) {
                return quest;
            }
        }
        for (Quest quest : active) {
            if (quest.category() == QuestCategory.STORY) {
                return quest;
            }
        }
        return active.get(0);
    }

    public void forget(Player player) {
        BossBar bar = bars.remove(player.getUniqueId());
        if (bar != null) {
            player.hideBossBar(bar);
        }
        tracked.remove(player.getUniqueId());
    }
}
