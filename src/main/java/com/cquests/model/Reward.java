package com.cquests.model;

import java.util.List;

public record Reward(long money, List<RewardItem> items, List<RewardEffect> effects, List<String> commands, int xp) {

    public static final Reward NONE = new Reward(0, List.of(), List.of(), List.of(), 0);

    public boolean isEmpty() {
        return money <= 0 && items.isEmpty() && effects.isEmpty() && commands.isEmpty() && xp <= 0;
    }
}
