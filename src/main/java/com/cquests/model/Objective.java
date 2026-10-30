package com.cquests.model;

/**
 * One goal inside a quest.
 *
 * @param npc for TALK the NPC to talk to; for DELIVER the NPC that receives the items
 * @param label display name of the target, e.g. "wolves"; empty for TALK
 */
public record Objective(ObjectiveType type, TargetMatcher target, int amount, String npc, String label) {
}
