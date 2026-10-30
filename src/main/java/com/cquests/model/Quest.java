package com.cquests.model;

import java.util.List;

/**
 * @param giver      NPC that offers the quest; empty when it is handed out automatically (welcome quest)
 * @param turnIn     NPC you return to; empty means it completes as soon as every objective is done
 * @param order      position in the story chain or in the giver's side quest list
 * @param description MiniMessage text shown in the journal under the title
 */
public record Quest(
        String id,
        String name,
        int level,
        QuestCategory category,
        int order,
        String giver,
        String turnIn,
        List<String> requires,
        List<Objective> objectives,
        String description,
        List<String> offer,
        List<String> complete,
        Reward reward
) {

    public boolean autoComplete() {
        return turnIn.isEmpty();
    }

    /** True when an NPC is involved in the quest, which makes per-player NPCs visible to its holder. */
    public boolean involves(String npcId) {
        if (giver.equals(npcId) || turnIn.equals(npcId)) {
            return true;
        }
        for (Objective objective : objectives) {
            if (npcId.equals(objective.npc())) {
                return true;
            }
        }
        return false;
    }
}
