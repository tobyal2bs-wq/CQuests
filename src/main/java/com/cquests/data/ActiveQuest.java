package com.cquests.data;

import com.cquests.model.Quest;

public final class ActiveQuest {

    private final String questId;
    private final int[] progress;
    private final long acceptedAt;
    /** The resolved quest, cached so hot event paths skip the registry lookup; tied to a registry load. */
    private Quest cachedQuest;
    private int cachedGeneration = -1;

    public ActiveQuest(String questId, int objectives, long acceptedAt) {
        this(questId, new int[objectives], acceptedAt);
    }

    public ActiveQuest(String questId, int[] progress, long acceptedAt) {
        this.questId = questId;
        this.progress = progress;
        this.acceptedAt = acceptedAt;
    }

    public String questId() {
        return questId;
    }

    public int[] progress() {
        return progress;
    }

    public int get(int index) {
        return index < progress.length ? progress[index] : 0;
    }

    public void set(int index, int value) {
        if (index < progress.length) {
            progress[index] = value;
        }
    }

    public long acceptedAt() {
        return acceptedAt;
    }

    public Quest cached(int generation) {
        return generation == cachedGeneration ? cachedQuest : null;
    }

    public void cache(Quest quest, int generation) {
        cachedQuest = quest;
        cachedGeneration = generation;
    }

    public boolean untouched() {
        for (int p : progress) {
            if (p > 0) {
                return false;
            }
        }
        return true;
    }
}
