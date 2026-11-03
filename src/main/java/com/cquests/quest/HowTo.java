package com.cquests.quest;

import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.Tag;
import org.bukkit.entity.EntityType;
import org.bukkit.inventory.CookingRecipe;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.Recipe;
import org.bukkit.inventory.RecipeChoice;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.inventory.ShapelessRecipe;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * What villagers know about things: how an item is crafted, smelted or mined, read live from the
 * running server's own recipes and registries. A server on a newer Minecraft version (new blocks,
 * items, mobs, recipes) is understood without a plugin update.
 */
public final class HowTo {
    private HowTo() {}

    /** The first real material a target matches, or null. */
    static Material material(Objective objective) {
        for (Material material : Material.values()) if (!material.isLegacy() && objective.target().matches(material.name())) return material;
        return null;
    }

    static EntityType entity(Objective objective) {
        for (EntityType type : EntityType.values()) if (type != EntityType.UNKNOWN && objective.target().matches(type.name())) return type;
        return null;
    }

    /** A short tip for an objective, e.g. "Craft at a crafting table: 1 iron nugget ×8, 1 torch". Null when nothing useful. */
    public static String describe(Objective objective) {
        if (objective.target().any()) return null;
        try {
            return switch (objective.type()) {
                case CRAFT -> craft(objective);
                case SMELT -> smelt(objective);
                case MINE -> mine(objective);
                case PLACE -> { Material m = material(objective); yield m == null ? null : "Place " + name(m) + " anywhere in the world."; }
                default -> null;
            };
        } catch (RuntimeException | LinkageError e) {
            return null;
        }
    }

    private static String craft(Objective objective) {
        Material m = material(objective);
        if (m == null) return null;
        for (Recipe recipe : Bukkit.getRecipesFor(new ItemStack(m))) {
            Map<String, Integer> parts = new LinkedHashMap<>();
            boolean grid;
            if (recipe instanceof ShapedRecipe shaped) {
                grid = shaped.getShape().length > 2 || shaped.getShape()[0].length() > 2;
                Map<Character, RecipeChoice> choices = shaped.getChoiceMap();
                for (String row : shaped.getShape()) for (char c : row.toCharArray()) {
                    RecipeChoice choice = choices.get(c);
                    if (choice != null) parts.merge(choice(choice), 1, Integer::sum);
                }
            } else if (recipe instanceof ShapelessRecipe shapeless) {
                grid = shapeless.getChoiceList().size() > 4;
                for (RecipeChoice choice : shapeless.getChoiceList()) parts.merge(choice(choice), 1, Integer::sum);
            } else continue;
            if (parts.isEmpty()) continue;
            List<String> list = new ArrayList<>();
            parts.forEach((part, count) -> list.add(count + " " + part));
            int makes = recipe.getResult().getAmount();
            return "Craft " + name(m) + (makes > 1 ? " (makes " + makes + ")" : "") + (grid ? " at a crafting table" : " in your inventory") + ": " + String.join(", ", list) + ".";
        }
        return null;
    }

    private static String smelt(Objective objective) {
        Material m = material(objective);
        if (m == null) return null;
        Iterator<Recipe> it = Bukkit.recipeIterator();
        while (it.hasNext()) {
            Recipe recipe = it.next();
            if (recipe instanceof CookingRecipe<?> cooking && cooking.getResult().getType() == m)
                return "Smelt " + choice(cooking.getInputChoice()) + " in a furnace to get " + name(m) + ".";
        }
        return null;
    }

    private static String mine(Objective objective) {
        Material m = material(objective);
        if (m == null || !m.isBlock()) return null;
        String tool = Tag.MINEABLE_PICKAXE.isTagged(m) ? "a pickaxe" : Tag.MINEABLE_AXE.isTagged(m) ? "an axe"
                : Tag.MINEABLE_SHOVEL.isTagged(m) ? "a shovel" : Tag.MINEABLE_HOE.isTagged(m) ? "a hoe" : null;
        return tool == null ? null : "Mine " + name(m) + " with " + tool + ".";
    }

    private static String choice(RecipeChoice choice) {
        if (choice instanceof RecipeChoice.MaterialChoice mc && !mc.getChoices().isEmpty()) {
            return mc.getChoices().size() > 1 ? "any " + name(mc.getChoices().get(0)).replaceAll("^(oak|white|acacia) ", "") : name(mc.getChoices().get(0));
        }
        if (choice instanceof RecipeChoice.ExactChoice ec && !ec.getChoices().isEmpty()) return name(ec.getChoices().get(0).getType());
        return "something";
    }

    private static String name(Material m) {
        return Text.pretty(m.name()).toLowerCase(Locale.ROOT);
    }

    /** /cq test targets: null when the objective asks for something that really exists and can be done this way. */
    public static String problem(Objective objective) {
        if (objective.target().any() || objective.type() == ObjectiveType.TALK) return null;
        switch (objective.type()) {
            case KILL, BREED, TAME, SHEAR -> {
                EntityType type = entity(objective);
                return type == null ? "no such mob" : type.isAlive() ? null : type.name() + " is not a mob";
            }
            default -> { }
        }
        Material m = material(objective);
        if (m == null) return "no such item or block on this server";
        return switch (objective.type()) {
            case MINE, PLACE -> m.isBlock() ? null : name(m) + " is not a block";
            case CRAFT -> Bukkit.getRecipesFor(new ItemStack(m)).isEmpty() ? name(m) + " has no recipe" : null;
            case CONSUME -> m.isEdible() || m == Material.POTION || m == Material.MILK_BUCKET || m == Material.HONEY_BOTTLE ? null : name(m) + " can't be eaten";
            default -> m.isItem() ? null : name(m) + " is not an item";
        };
    }
}
