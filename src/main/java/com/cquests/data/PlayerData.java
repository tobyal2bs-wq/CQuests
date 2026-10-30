package com.cquests.data;

import java.util.HashSet;
import java.util.LinkedHashMap;
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
    long lastDailyAt;
    int dailiesDone;
    private volatile boolean dirty;

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

    public synchronized void reset() {
        active.clear();
        completed.clear();
        met.clear();
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
