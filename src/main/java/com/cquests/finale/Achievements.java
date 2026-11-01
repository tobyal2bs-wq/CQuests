package com.cquests.finale;

import com.cquests.CQuestsPlugin;
import com.cquests.data.PlayerData;
import com.cquests.model.Quest;
import com.cquests.util.Text;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.bukkit.Bukkit;
import org.bukkit.NamespacedKey;
import org.bukkit.advancement.Advancement;
import org.bukkit.advancement.AdvancementProgress;
import org.bukkit.entity.Player;

import java.lang.reflect.Method;
import java.util.List;
import java.util.TreeSet;

/**
 * Real Minecraft advancements: one for every chapter and "Finished the Journey" at the end.
 * They are built in memory when the plugin starts, so no datapack or resource pack is needed.
 * They show up in the Adventure tab as a chain, with a toast and a chat line like any vanilla one.
 * Chapters added later (6, 7, ...) get their own advancement on the next start or /cq reload.
 */
public final class Achievements {

    private static final String[] ICONS = {
            "minecraft:campfire", "minecraft:iron_sword", "minecraft:ender_eye", "minecraft:tripwire_hook",
            "minecraft:wither_skeleton_skull", "minecraft:spyglass", "minecraft:trident", "minecraft:heart_of_the_sea"};

    private final CQuestsPlugin plugin;
    private static final int[] LEVELS={5,10,25,50,75,100};
    private boolean warned;

    public Achievements(CQuestsPlugin plugin) {
        this.plugin = plugin;
    }

    private NamespacedKey chapterKey(int chapter) {
        return new NamespacedKey(plugin, "chapter_" + chapter);
    }

    private NamespacedKey journeyKey() {
        return new NamespacedKey(plugin, "finished_the_journey");
    }

    /** Registers any advancement that isn't loaded yet. Call at startup and after a reload. */
    public void register() {
        NamespacedKey rootKey = new NamespacedKey(plugin, "wanderers");
        load(rootKey, json(null, "minecraft:written_book", "The Wanderers", "Write your own story in Dawn SMP", "task", "aqua"));
        String parent = rootKey.toString();
        int loaded = 0;
        for (int chapter : chapters()) {
            NamespacedKey key = chapterKey(chapter);
            String name = plugin.quests().chapterName(chapter);
            String title = plugin.settings().msg("chapter-title", "Chapter <chapter>: <name>")
                    .replace("<chapter>", Integer.toString(chapter)).replace("<name>", name.isEmpty() ? "Complete" : name);
            String description = plugin.settings().msg("chapter-description", "Finish chapter <chapter> of the story")
                    .replace("<chapter>", Integer.toString(chapter));
            if (load(key, json(parent, ICONS[(chapter - 1) % ICONS.length], title, description, "goal", "yellow"))) {
                loaded++;
            }
            parent = key.toString();
        }
        if (load(journeyKey(), json(parent, "minecraft:nether_star", plugin.settings().advancementTitle,
                plugin.settings().advancementDescription, "challenge", "gold"))) {
            loaded++;
        }
        for (Milestones.Goal goal : Milestones.ALL) {
            if (load(new NamespacedKey(plugin, goal.id()), json(rootKey.toString(), goal.icon(), goal.title(),
                    goal.description(), goal.target() >= 100 ? "challenge" : "task", "aqua"))) loaded++;
        }
        for(int level:LEVELS)if(load(new NamespacedKey(plugin,"wayfarer_"+level),json(rootKey.toString(),"minecraft:experience_bottle",
                "Wayfarer "+level,"Reach custom Wayfarer level "+level,"goal","aqua")))loaded++;
        plugin.getLogger().info("Registered " + (loaded + 1) + " achievements (chapters, ending and milestones)");
    }

    private TreeSet<Integer> chapters() {
        TreeSet<Integer> chapters = new TreeSet<>();
        for (Quest quest : plugin.quests().story()) {
            chapters.add(quest.chapter());
        }
        return chapters;
    }

    /** @return true if the advancement is loaded (now or already) */
    private boolean load(NamespacedKey key, String json) {
        if (Bukkit.getAdvancement(key) != null) {
            return true;
        }
        try {
            Object unsafe = Bukkit.getUnsafe();
            Method load = unsafe.getClass().getMethod("loadAdvancement", NamespacedKey.class, String.class);
            load.invoke(unsafe, key, json);
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            if (!warned) {
                warned = true;
                plugin.getLogger().warning("This server can't load advancements at runtime; achievements are shown in chat instead.");
            }
        }
        return Bukkit.getAdvancement(key) != null;
    }

    /** Called when a story quest is completed. Must run on the player's thread. */
    public void onStoryQuest(Player player, Quest quest) {
        Quest next = plugin.quests().nextStory(quest);
        if (next == null || next.chapter() != quest.chapter()) {
            grant(player, chapterKey(quest.chapter()), true);
        }
    }

    public void grantJourney(Player player) {
        grant(player, journeyKey(), true);
    }

    /**
     * Gives a player every achievement they have earned but don't have yet, for example after a
     * restore from backup or after a chapter was added. Silent fallback: no chat spam on join.
     */
    public void sync(Player player) {
        PlayerData data = plugin.store().cached(player.getUniqueId());
        if (data == null) {
            return;
        }
        List<Quest> story = plugin.quests().story();
        if (data.startedAt() > 0) grant(player, new NamespacedKey(plugin, "wanderers"), false);
        if(plugin.progression()!=null)for(int level:LEVELS)if(plugin.progression().level(data)>=level)grant(player,new NamespacedKey(plugin,"wayfarer_"+level),false);
        for (Milestones.Goal goal : Milestones.ALL) {
            if (goal.value(data) >= goal.target()) grant(player, new NamespacedKey(plugin, goal.id()), false);
        }
        for (int i = 0; i < story.size(); i++) {
            Quest quest = story.get(i);
            boolean lastOfChapter = i + 1 == story.size() || story.get(i + 1).chapter() != quest.chapter();
            if (lastOfChapter && data.isCompleted(quest.id())) {
                grant(player, chapterKey(quest.chapter()), false);
            }
        }
        if (!story.isEmpty() && data.isCompleted(story.get(story.size() - 1).id())) {
            grant(player, journeyKey(), false);
        }
    }

    /** For /cq test: give a chapter's achievement (0 = Finished the Journey). */
    public boolean grantForTest(Player player, int chapter) {
        NamespacedKey key = chapter <= 0 ? journeyKey() : chapterKey(chapter);
        grant(player, key, true);
        return Bukkit.getAdvancement(key) != null;
    }

    /** For /cq test: takes every CQuests achievement away again so they can be earned once more. */
    public int revokeAll(Player player) {
        int revoked = 0;
        List<NamespacedKey> keys = new java.util.ArrayList<>();
        chapters().forEach(c -> keys.add(chapterKey(c)));
        keys.add(journeyKey());
        keys.add(new NamespacedKey(plugin, "wanderers"));
        for(int level:LEVELS)keys.add(new NamespacedKey(plugin,"level_"+level));
        for (Milestones.Goal goal : Milestones.ALL) keys.add(new NamespacedKey(plugin, goal.id()));
        for (NamespacedKey key : keys) {
            Advancement advancement = Bukkit.getAdvancement(key);
            if (advancement == null) {
                continue;
            }
            AdvancementProgress progress = player.getAdvancementProgress(advancement);
            for (String criterion : progress.getAwardedCriteria()) {
                progress.revokeCriteria(criterion);
                revoked++;
            }
        }
        return revoked;
    }

    private void grant(Player player, NamespacedKey key, boolean announceFallback) {
        Advancement advancement = Bukkit.getAdvancement(key);
        if (advancement == null) {
            if (announceFallback) {
                plugin.send(player, "<gold>★ Achievement unlocked: <yellow>[" + Text.escape(key.getKey().replace('_', ' ')) + "]");
            }
            return;
        }
        AdvancementProgress progress = player.getAdvancementProgress(advancement);
        for (String criterion : progress.getRemainingCriteria()) {
            progress.awardCriteria(criterion);
        }
    }

    private static String json(String parent, String iconId, String titleText, String descriptionText, String frame, String color) {
        JsonObject icon = new JsonObject();
        icon.addProperty("id", iconId);
        JsonObject title = new JsonObject();
        title.addProperty("text", titleText);
        title.addProperty("color", color);
        JsonObject description = new JsonObject();
        description.addProperty("text", descriptionText);

        JsonObject display = new JsonObject();
        display.add("icon", icon);
        display.add("title", title);
        display.add("description", description);
        display.addProperty("frame", frame);
        display.addProperty("show_toast", true);
        display.addProperty("announce_to_chat", true);
        display.addProperty("hidden", false);
        if (parent == null) display.addProperty("background", "minecraft:textures/gui/advancements/backgrounds/adventure.png");

        JsonObject trigger = new JsonObject();
        trigger.addProperty("trigger", "minecraft:impossible");
        JsonObject criteria = new JsonObject();
        criteria.add("done", trigger);
        JsonArray requirement = new JsonArray();
        requirement.add("done");
        JsonArray requirements = new JsonArray();
        requirements.add(requirement);

        JsonObject root = new JsonObject();
        if (parent != null) root.addProperty("parent", parent);
        root.add("display", display);
        root.add("criteria", criteria);
        root.add("requirements", requirements);
        return root.toString();
    }

    public void show(Player player) {
        PlayerData data = plugin.questManager().data(player);
        plugin.send(player, "<gold><bold>Your milestones</bold> <white>• Optional goals, earned at your pace");
        int level=plugin.progression().level(data);
        plugin.send(player,"<aqua>Wayfarer level "+level+" <gray>• "+Text.formatMoney(plugin.progression().curve().remaining(data.skillXp()))+" XP to the next level");
        for (Milestones.Goal goal : Milestones.ALL) {
            long value = Math.min(goal.target(), goal.value(data));
            plugin.send(player, (value == goal.target() ? "<green>✔ " : "<white>○ ") + Text.escape(goal.title())
                    + " <aqua>" + value + "/" + goal.target() + " <gray>" + Text.escape(goal.kind()));
        }
    }
}
