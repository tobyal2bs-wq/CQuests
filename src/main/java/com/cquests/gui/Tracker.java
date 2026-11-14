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
    /** What the bar shows now, so the twice-a-second refresh skips rebuilding text that didn't change. */
    private final Map<UUID, String> shown = new ConcurrentHashMap<>();

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
        PlayerData data = plugin.store().cached(player.getUniqueId());
        return plugin.settings().trackerEnabled && data != null && data.trackerOn(plugin.settings().trackerDefault);
    }

    /** Turns the bar on or off for this player and returns the new state. */
    public boolean toggle(Player player) {
        PlayerData data = plugin.questManager().data(player);
        data.setTrackerOn(!data.trackerOn(plugin.settings().trackerDefault));
        plugin.store().saveNow(data);
        update(player);
        return enabled(player);
    }

    public void update(Player player) {
        BossBar bar = bars.get(player.getUniqueId());
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data != null) expire(player, data);
        Quest quest = enabled(player) && data != null ? pick(player, data) : null;
        if (quest == null) {
            if (bar != null && shown.remove(player.getUniqueId()) != null) {
                player.hideBossBar(bar);
            }
            return;
        }
        QuestManager qm = plugin.questManager();
        ActiveQuest active = data.active(quest.id());
        if (active == null) {
            return;
        }
        int left = quest.timed() ? (int) Math.max(0, quest.timeLimit() - (System.currentTimeMillis() - active.acceptedAt()) / 1000) : -1;
        StringBuilder state = new StringBuilder(quest.id()).append('@').append(left);
        for (int i = 0; i < quest.objectives().size(); i++) {
            state.append(':').append(active.get(i));
        }
        String key = state.toString();
        if (bar != null && key.equals(shown.get(player.getUniqueId()))) {
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
                next = plain(qm.objectiveLabel(objective)) + (objective.amount() > 1 ? "  " + value + "/" + objective.amount() : "");
            }
        }
        boolean ready = qm.ready(quest, active);
        String step = ready ? "Return to " + plugin.npcs().name(quest.turnIn()) : next == null ? "" : next;
        String name = "<white><bold>" + Text.escape(shorten(quest.name(), 30)) + "</bold></white> <white>• " + Text.escape(shorten(step, 64)) + "</white>";
        if (left >= 0) { String c = left < 60 ? "red" : "yellow"; name += " <" + c + ">⌛ " + left / 60 + ":" + String.format("%02d", left % 60) + "</" + c + ">"; }
        float progress = ready ? 1f : total == 0 ? 0f : Math.min(1f, (float) done / total);
        BossBar.Color color = ready ? BossBar.Color.GREEN : BossBar.Color.WHITE;
        if (bar == null) {
            bar = BossBar.bossBar(Text.mm(name), progress, color, BossBar.Overlay.PROGRESS);
            bars.put(player.getUniqueId(), bar);
        } else {
            bar.name(Text.mm(name));
            bar.progress(progress);
            bar.color(color);
        }
        player.showBossBar(bar);
        shown.put(player.getUniqueId(), key);
    }

    /** Drops every timed quest whose clock ran out. Runs with the twice-a-second refresh. */
    private void expire(Player player, PlayerData data) {
        long now = System.currentTimeMillis();
        for (Quest quest : plugin.questManager().activeQuests(data)) {
            if (!quest.timed()) continue;
            ActiveQuest active = data.active(quest.id());
            if (active != null && now - active.acceptedAt() > quest.timeLimit() * 1000L && !plugin.questManager().ready(quest, active))
                plugin.questManager().timeUp(player, quest);
        }
    }

    /** The chosen quest if it is still active, otherwise the story quest, otherwise any active quest. */
    public Quest pick(Player player, PlayerData data) {
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

    /** After /cq reload: quest names or settings may have changed, so rebuild every bar once. */
    public void invalidate() {
        shown.clear();
    }

    public void forget(Player player) {
        BossBar bar = bars.remove(player.getUniqueId());
        if (bar != null) {
            player.hideBossBar(bar);
        }
        tracked.remove(player.getUniqueId());
        shown.remove(player.getUniqueId());
    }

    private static String plain(String value) {
        return net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer.plainText().serialize(Text.mm(value));
    }

    private static String shorten(String value, int max) {
        return value.length() <= max ? value : value.substring(0, max - 1) + "…";
    }
}
