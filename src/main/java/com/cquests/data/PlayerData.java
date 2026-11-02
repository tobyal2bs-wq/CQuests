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
    final Map<String, String> decisions = new LinkedHashMap<>();
    /** Side quests are done in order per NPC, so a count per NPC is all we store, even for a million quests. */
    final Map<String, Integer> sideDone = new HashMap<>();
    final List<JourneyEntry> journey = new ArrayList<>();
    long startedAt;
    long lastDailyAt;
    int dailiesDone;
    /** Where to put the player back if they log out during the ending cinematic: "world;x;y;z;yaw;pitch;GAMEMODE". */
    String finaleReturn;
    boolean storyBookGiven;
    Boolean trackerOn;
    Boolean directionsOn;
    String menuMode;
    long skillXp;
    boolean skillInitialized;
    long wheatHarvested;
    int hoeTier;
    private volatile boolean dirty;
    /** Save ordering, see PlayerStore. */
    long saveSeq;
    long writtenSeq;
    /** Set when a backup replaced this player's data; a retired copy is never written to disk again. */
    volatile boolean retired;

    public PlayerData(UUID uuid) {
        this.uuid = uuid;
    }

    public UUID uuid() {
        return uuid;
    }

    public synchronized String decision(String quest) { return decisions.get(quest); }
    public synchronized Map<String, String> decisions() { return Map.copyOf(decisions); }
    /** A story decision is permanent for this journey and cannot be replayed. */
    public synchronized boolean decide(String quest, String choice) {
        if (!completed.contains(quest) || decisions.containsKey(quest)
                || !List.of("kind", "selfish").contains(choice) || decisions.size() >= 256) return false;
        decisions.put(quest, choice); dirty = true; return true;
    }

    public synchronized long skillXp() { return skillXp; }
    public synchronized boolean skillInitialized() { return skillInitialized; }
    public synchronized void initializeSkill(long minimum) {
        if (!skillInitialized) { skillXp=Math.max(skillXp,minimum);skillInitialized=true;dirty=true; }
    }
    public synchronized long wheatHarvested() { return wheatHarvested; }
    public synchronized int hoeTier() { return hoeTier; }
    public synchronized void setHoeTier(int tier) { hoeTier = Math.max(0, tier); dirty = true; }
    public synchronized void addSkillXp(long amount) {
        if (amount > 0) { skillXp = amount > Long.MAX_VALUE - skillXp ? Long.MAX_VALUE : skillXp + amount; dirty = true; }
    }
    public synchronized void addWheat(long amount) { if (amount > 0) { wheatHarvested += amount; dirty = true; } }

    public synchronized boolean trackerOn(boolean defaultValue) {
        return trackerOn == null ? defaultValue : trackerOn;
    }

    public synchronized void setTrackerOn(boolean value) { trackerOn = value; dirty = true; }

    public synchronized boolean directionsOn(boolean defaultValue) {
        return directionsOn == null ? defaultValue : directionsOn;
    }

    public synchronized void setDirectionsOn(boolean value) { directionsOn = value; dirty = true; }

    public synchronized String menuMode(String defaultValue) {
        return menuMode == null ? defaultValue : menuMode;
    }

    public synchronized void setMenuMode(String value) { menuMode = value; dirty = true; }

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

    public synchronized int metCount() { return met.size(); }

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

    /** Marks the story book as handed out; true only the first time, so it can never be given twice. */
    public synchronized boolean claimStoryBook() {
        if (storyBookGiven) {
            return false;
        }
        storyBookGiven = true;
        dirty = true;
        return true;
    }

    public synchronized void reset() {
        active.clear();
        completed.clear();
        met.clear();
        sideDone.clear();
        journey.clear();
        decisions.clear();
        startedAt = 0;
        finaleReturn = null;
        storyBookGiven = false;
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
