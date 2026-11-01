package com.cquests.progression;

/** Cumulative, monotonic custom XP. Never reads or changes vanilla experience. */
public record LevelCurve(int maxLevel, long totalXp, double exponent) {
    public LevelCurve {
        if (maxLevel < 2 || maxLevel > 1000 || totalXp < maxLevel || !Double.isFinite(exponent) || exponent < 1)
            throw new IllegalArgumentException("Invalid skill curve");
    }
    public long threshold(int level) {
        if (level <= 1) return 0;
        int step=Math.min(level,maxLevel)-1;
        return step+Math.round((totalXp-(maxLevel-1L))*Math.pow(step/(maxLevel-1.0),exponent));
    }
    public int level(long xp) {
        int low = 1, high = maxLevel;
        while (low < high) {
            int mid = (low + high + 1) >>> 1;
            if (threshold(mid) <= xp) low = mid; else high = mid - 1;
        }
        return low;
    }
    public long remaining(long xp) {
        int level = level(xp);
        return level >= maxLevel ? 0 : Math.max(0, threshold(level + 1) - xp);
    }
    public double progress(long xp) {
        int level = level(xp);
        if (level >= maxLevel) return 1;
        return Math.max(0, Math.min(1, (xp - threshold(level)) / (double) Math.max(1, threshold(level + 1) - threshold(level))));
    }
}
