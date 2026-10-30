package com.cquests.data;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * One player's quest state. Mutations happen on the player's own region thread; the async saver
 * takes a snapshot under the same lock, so callers wrap multi-step changes in {@code synchronized (data)}.
 */
public final class PlayerData {

    private final UUID uuid;
    final Map<String, ActiveQuest> active = new LinkedHashMap<>();
    final Set<String> completed = new HashSet<>();
    final Set<String> met = new HashSet<>();
    /** Side quests are done in order per NPC, so a count per NPC is all we store, even for a million quests. */
    final Map<String, Integer> sideDone = new HashMap<>();
    final List<JourneyEntry> journey = new ArrayList<>();
    long startedAt;
    long lastDailyAt;
    int dailiesDone;
    /** Where to put the player back if they log out during the ending cinematic: "world;x;y;z;yaw;pitch;GAMEMODE". */
    String finaleReturn;
    private volatile boolean dirty;
    /** Save ordering, see PlayerStore. */
    long saveSeq;
    long writtenSeq;

    public PlayerData(UUID uuid) {
        this.uuid = uuid;
    }

    public UUID uuid() {
        return uuid;
    }

    public synchronized Map<String, ActiveQuest> active() {
        return active;
    }

    public synchronized ActiveQuest active(String questId) {
        return active.get(questId);
    }

    public synchronized boolean isActive(String questId) {
        return active.containsKey(questId);
    }

    public synchronized boolean isCompleted(String questId) {
        return completed.contains(questId);
    }

    public synchronized int completedCount() {
        return completed.size();
    }

    public synchronized void start(ActiveQuest quest) {
        active.put(quest.questId(), quest);
        dirty = true;
    }

    public synchronized ActiveQuest remove(String questId) {
        dirty = true;
        return active.remove(questId);
    }

    public synchronized void complete(String questId, boolean remember) {
        active.remove(questId);
        if (remember) {
            completed.add(questId);
        }
        dirty = true;
    }

    public synchronized void uncomplete(String questId) {
        completed.remove(questId);
        dirty = true;
    }

    public synchronized boolean hasMet(String npcId) {
        return met.contains(npcId);
    }

    public synchronized boolean meet(String npcId) {
        boolean added = met.add(npcId);
        dirty |= added;
        return added;
    }

    public synchronized long lastDailyAt() {
        return lastDailyAt;
    }

    public synchronized void setLastDailyAt(long time) {
        lastDailyAt = time;
        dirty = true;
    }

    public synchronized int dailiesDone() {
        return dailiesDone;
    }

    public synchronized void addDailyDone() {
        dailiesDone++;
        dirty = true;
    }

    public synchronized int sideDone(String npcId) {
        return sideDone.getOrDefault(npcId, 0);
    }

    public synchronized long totalSideDone() {
        long total = 0;
        for (int done : sideDone.values()) {
            total += done;
        }
        return total;
    }

    public synchronized void addSideDone(String npcId) {
        sideDone.merge(npcId, 1, Integer::sum);
        dirty = true;
    }

    public synchronized void setSideDone(String npcId, int count) {
        sideDone.put(npcId, Math.max(0, count));
        dirty = true;
    }

    public synchronized List<JourneyEntry> journey() {
        return List.copyOf(journey);
    }

    public synchronized void addJourney(JourneyEntry entry) {
        journey.add(entry);
        dirty = true;
    }

    public synchronized long startedAt() {
        return startedAt;
    }

    public synchronized void markStarted(long time) {
        if (startedAt == 0) {
            startedAt = time;
            dirty = true;
        }
    }

    public synchronized String finaleReturn() {
        return finaleReturn;
    }

    public synchronized void setFinaleReturn(String value) {
        finaleReturn = value;
        dirty = true;
    }

    public synchronized void reset() {
        active.clear();
        completed.clear();
        met.clear();
        sideDone.clear();
        journey.clear();
        startedAt = 0;
        finaleReturn = null;
        lastDailyAt = 0;
        dailiesDone = 0;
        dirty = true;
    }

    public void markDirty() {
        dirty = true;
    }

    public boolean dirty() {
        return dirty;
    }

    void clean() {
        dirty = false;
    }
}
