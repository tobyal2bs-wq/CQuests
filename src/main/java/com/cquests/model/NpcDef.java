package com.cquests.model;

import java.util.List;

/**
 * @param act        1 = spawn village, 2 = out in the world; only used for auto placement
 * @param personal   when true the villager is only visible to players that are involved with it
 * @param baby       a baby villager
 * @param playerSkin player name whose skin a player-shaped NPC wears (Minecraft 1.21.9+); empty for a villager
 */
public record NpcDef(
        String id,
        String name,
        String title,
        String profession,
        String skin,
        int level,
        int act,
        boolean personal,
        boolean daily,
        boolean baby,
        String playerSkin,
        List<String> intro,
        List<String> idle
) {
}
