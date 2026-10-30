package com.cquests.data;

public final class ActiveQuest {

    private final String questId;
    private final int[] progress;
    private final long acceptedAt;

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

    public boolean untouched() {
        for (int p : progress) {
            if (p > 0) {
                return false;
            }
        }
        return true;
    }
}
