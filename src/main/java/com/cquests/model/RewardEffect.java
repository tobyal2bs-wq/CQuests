package com.cquests.model;

/** A potion effect reward, e.g. 1 hour of Swiftness. The effect is looked up by name when it is given. */
public record RewardEffect(String effect, int seconds, int amplifier) {
}
