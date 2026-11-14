package com.cquests.model;

import java.util.List;

/**
 * @param giver      NPC that offers the quest; empty when it is handed out automatically (welcome quest)
 * @param turnIn     NPC you return to; empty means it completes as soon as every objective is done
 * @param order      position in the story chain or in the giver's side quest list
 * @param description MiniMessage text shown in the journal under the title
 * @param big        plays the big celebration (title, fireworks) on completion
 * @param chapter    story chapter number (1-5 by default); 0 for side and daily quests
 * @param sideRequired side quests the player must finish for the previous story villager before this
 *                   story quest opens; -1 uses quests.side-quests-per-chapter from config.yml
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
        Reward reward,
        boolean big,
        int chapter,
        int sideRequired,
        /** Seconds to finish it after taking it; 0 means no clock. Running out drops the quest (it can be taken again). */
        int timeLimit
) {

    public Quest(String id, String name, int level, QuestCategory category, int order, String giver, String turnIn, List<String> requires,
                 List<Objective> objectives, String description, List<String> offer, List<String> complete, Reward reward, boolean big,
                 int chapter, int sideRequired) {
        this(id, name, level, category, order, giver, turnIn, requires, objectives, description, offer, complete, reward, big, chapter, sideRequired, 0);
    }

    public boolean timed() { return timeLimit > 0; }

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
