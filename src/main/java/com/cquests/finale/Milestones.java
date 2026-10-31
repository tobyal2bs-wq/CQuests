package com.cquests.finale;

import com.cquests.data.PlayerData;
import java.util.List;

public final class Milestones {
    public record Goal(String id, String title, String icon, String kind, int target) {
        public long value(PlayerData data) {
            return switch (kind) {
                case "side" -> data.totalSideDone();
                case "daily" -> data.dailiesDone();
                default -> data.metCount();
            };
        }
        public String description() { return "Complete " + target + " " + (kind.equals("met") ? "villager introductions" : kind + " quests"); }
    }
    public static final List<Goal> ALL = List.of(
        new Goal("helping_hand", "A Helping Hand", "minecraft:bread", "side", 1),
        new Goal("local_hero", "Local Hero", "minecraft:emerald", "side", 10),
        new Goal("village_favorite", "Village Favorite", "minecraft:gold_ingot", "side", 50),
        new Goal("hundred_favors", "A Hundred Favors", "minecraft:diamond", "side", 100),
        new Goal("wanderer_legend", "Wanderer Legend", "minecraft:enchanted_book", "side", 500),
        new Goal("thousand_stories", "A Thousand Stories", "minecraft:amethyst_shard", "side", 1000),
        new Goal("never_done", "There Is Always Another Story", "minecraft:dragon_breath", "side", 5000),
        new Goal("daily_first", "See You Tomorrow", "minecraft:clock", "daily", 1),
        new Goal("daily_seven", "A Familiar Face", "minecraft:sunflower", "daily", 7),
        new Goal("daily_thirty", "Marigold's Favorite", "minecraft:honey_bottle", "daily", 30),
        new Goal("met_five", "Making Friends", "minecraft:poppy", "met", 5),
        new Goal("met_fifteen", "Around the Campfire", "minecraft:campfire", "met", 15),
        new Goal("met_fifty", "Everyone Has a Story", "minecraft:map", "met", 50),
        new Goal("met_hundred", "The Wanderers Know Your Name", "minecraft:bell", "met", 100)
    );
    private Milestones() {}
}
