package com.cquests.gui;

import com.cquests.CQuestsPlugin;
import com.cquests.data.ActiveQuest;
import com.cquests.data.PlayerData;
import com.cquests.model.Objective;
import com.cquests.model.ObjectiveType;
import com.cquests.model.Quest;
import com.cquests.model.QuestCategory;
import com.cquests.quest.QuestManager;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import net.kyori.adventure.text.Component;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemFlag;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * The quest menu behind /quests: chapter progress at the top, active quests in the middle, chapters
 * along the bottom. A chest menu reads well on Java and on Bedrock through Geyser. Every click is
 * cancelled by {@link MenuListener}, so nothing can be taken out of it.
 */
public final class QuestMenu implements InventoryHolder {

    private static final int[] QUEST_SLOTS = {10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34};
    private static final int CHAPTER_ROW = 36;
    private static final int SLOT_BOOK = 48;
    private static final int SLOT_CLOSE = 49;
    private static final int SLOT_TRACKER = 50;

    private final CQuestsPlugin plugin;
    private final Player player;
    private final Inventory inventory;
    private final Map<Integer, String> questAt = new HashMap<>();

    private QuestMenu(CQuestsPlugin plugin, Player player) {
        this.plugin = plugin;
        this.player = player;
        this.inventory = Bukkit.createInventory(this, 54, Text.mm("<dark_gray>Quest Journal"));
    }

    public static void open(CQuestsPlugin plugin, Player player) {
        Sched.entity(player, () -> {
            QuestMenu menu = new QuestMenu(plugin, player);
            menu.fill();
            player.openInventory(menu.inventory);
            player.playSound(player.getLocation(), Sound.ITEM_BOOK_PAGE_TURN, 0.8f, 1f);
        });
    }

    @Override
    public Inventory getInventory() {
        return inventory;
    }

    private void fill() {
        inventory.clear();
        questAt.clear();
        QuestManager qm = plugin.questManager();
        PlayerData data = qm.data(player);
        ItemStack glass = item(Material.GRAY_STAINED_GLASS_PANE, " ", List.of());
        for (int slot = 0; slot < 54; slot++) {
            if (slot < 9 || slot >= 45 || slot % 9 == 0 || slot % 9 == 8) {
                inventory.setItem(slot, glass);
            }
        }
        inventory.setItem(4, chapterItem(data));
        inventory.setItem(0, statsItem(data));
        inventory.setItem(8, dailyItem(data));

        List<Quest> active = qm.activeQuests(data);
        String tracked = plugin.tracker().tracked(player);
        for (int i = 0; i < active.size() && i < QUEST_SLOTS.length; i++) {
            Quest quest = active.get(i);
            inventory.setItem(QUEST_SLOTS[i], questItem(quest, data.active(quest.id()), quest.id().equals(tracked)));
            questAt.put(QUEST_SLOTS[i], quest.id());
        }
        if (active.isEmpty()) {
            inventory.setItem(22, item(Material.MAP, "<yellow>No active quests", List.of(
                    "<gray>Click a villager to get one.",
                    "<gray>Look for the white names around spawn.")));
        }
        chapters(data);
        inventory.setItem(SLOT_BOOK, item(Material.WRITABLE_BOOK, "<gold>Open the journal book", List.of("<gray>Every quest, page by page.")));
        inventory.setItem(SLOT_CLOSE, item(Material.BARRIER, "<red>Close", List.of()));
        boolean on = plugin.tracker().enabled(player);
        inventory.setItem(SLOT_TRACKER, item(Material.COMPASS, "<aqua>Quest tracker: " + (on ? "<green>on" : "<red>off"),
                List.of("<gray>The bar at the top of your screen.", "<yellow>Click to turn it " + (on ? "off" : "on") + ".")));
    }

    private ItemStack chapterItem(PlayerData data) {
        Quest next = plugin.questManager().nextStoryQuest(data);
        List<Quest> story = plugin.quests().story();
        int chapter = next != null ? next.chapter() : story.isEmpty() ? 1 : story.get(story.size() - 1).chapter();
        int inChapter = 0;
        int doneInChapter = 0;
        for (Quest quest : story) {
            if (quest.chapter() == chapter) {
                inChapter++;
                if (data.isCompleted(quest.id())) {
                    doneInChapter++;
                }
            }
        }
        List<String> lore = new ArrayList<>();
        lore.add("<white>" + Text.escape(plugin.quests().chapterName(chapter)));
        lore.add(bar(doneInChapter, inChapter) + " <gray>" + doneInChapter + "/" + inChapter);
        if (next != null) {
            String gate = plugin.questManager().chapterGate(data, next);
            lore.add("");
            if (gate != null) {
                int need = plugin.questManager().sideRequired(next);
                lore.add("<gray>Next story step needs side quests");
                lore.add("<gray>from " + plugin.npcs().mention(gate) + "<gray>: <yellow>" + Math.min(need, data.sideDone(gate)) + "/" + need);
            } else if (!data.isActive(next.id())) {
                lore.add("<gray>Next: talk to " + plugin.npcs().mention(next.giver()));
            }
        } else {
            lore.add("<green>Journey finished!");
        }
        ItemStack stack = item(Material.ENCHANTED_BOOK, "<gold><bold>Chapter " + chapter, lore);
        return stack;
    }

    private ItemStack statsItem(PlayerData data) {
        int storyDone = 0;
        List<Quest> story = plugin.quests().story();
        for (Quest quest : story) {
            if (data.isCompleted(quest.id())) {
                storyDone++;
            }
        }
        return item(Material.KNOWLEDGE_BOOK, "<aqua>Your journey", List.of(
                "<gray>Story: <white>" + storyDone + "/" + story.size(),
                "<gray>Side quests: <white>" + data.totalSideDone(),
                "<gray>Daily quests: <white>" + data.dailiesDone(),
                bar(storyDone, story.size())));
    }

    private ItemStack dailyItem(PlayerData data) {
        long left = plugin.questManager().dailyCooldownLeft(data);
        String daily = plugin.settings().dailyNpc;
        if (left > 0) {
            return item(Material.CLOCK, "<yellow>Daily quest", List.of(
                    "<gray>Come back in <white>" + Text.duration(left),
                    "<gray>to " + plugin.npcs().mention(daily) + "<gray>."));
        }
        return item(Material.CLOCK, "<green>Daily quest ready", List.of(
                "<gray>Visit " + plugin.npcs().mention(daily) + " <gray>for today's job."));
    }

    private void chapters(PlayerData data) {
        List<Quest> story = plugin.quests().story();
        int last = story.isEmpty() ? 1 : story.get(story.size() - 1).chapter();
        Quest next = plugin.questManager().nextStoryQuest(data);
        int current = next == null ? last + 1 : next.chapter();
        int first = Math.max(1, Math.min(current - 3, last - 6));
        for (int c = first, slot = CHAPTER_ROW + 1; c <= last && slot < CHAPTER_ROW + 8; c++, slot++) {
            String name = Text.escape(plugin.quests().chapterName(c));
            if (c < current) {
                inventory.setItem(slot, glow(item(Material.LIME_STAINED_GLASS_PANE, "<green>✔ Chapter " + c, List.of("<white>" + name, "<gray>Finished"))));
            } else if (c == current) {
                inventory.setItem(slot, glow(item(Material.YELLOW_STAINED_GLASS_PANE, "<yellow>Chapter " + c, List.of("<white>" + name, "<gray>In progress"))));
            } else {
                inventory.setItem(slot, item(Material.RED_STAINED_GLASS_PANE, "<red>Chapter " + c, List.of("<dark_gray>Locked")));
            }
        }
    }

    private ItemStack questItem(Quest quest, ActiveQuest active, boolean tracked) {
        QuestManager qm = plugin.questManager();
        List<String> lore = new ArrayList<>();
        String kind = switch (quest.category()) {
            case STORY -> "<gold>Story";
            case SIDE -> "<aqua>Side quest";
            case DAILY -> "<light_purple>Daily";
        };
        lore.add(kind + " <dark_gray>• <gray>Level " + quest.level());
        lore.add("");
        boolean ready = active != null && qm.ready(quest, active);
        for (int i = 0; i < quest.objectives().size(); i++) {
            Objective objective = quest.objectives().get(i);
            int value = active == null ? 0 : Math.min(objective.amount(), active.get(i));
            boolean done = active != null && qm.objectiveDone(quest, active, i);
            lore.add((done ? "<green>✔ " : "<yellow>○ ") + "<white>" + qm.objectiveLabel(objective));
            lore.add("   " + bar(value, objective.amount()) + " <gray>" + value + "/" + objective.amount());
        }
        lore.add("");
        if (ready) {
            lore.add("<green>Done! Return to " + plugin.npcs().mention(quest.turnIn()));
        }
        lore.add("<gray>Rewards:");
        for (String line : qm.rewardLines(quest.reward())) {
            lore.add("<gray>  " + line);
        }
        lore.add("");
        lore.add(tracked ? "<aqua>Tracking on your screen" : "<yellow>Click to track");
        if (quest.category() != QuestCategory.STORY) {
            lore.add("<red>Shift + right click to abandon");
        }
        ItemStack stack = item(icon(quest), (tracked ? "<aqua>▶ " : "") + "<white><bold>" + Text.escape(quest.name()), lore);
        return quest.category() == QuestCategory.STORY || tracked ? glow(stack) : stack;
    }

    private static Material icon(Quest quest) {
        ObjectiveType type = quest.objectives().isEmpty() ? ObjectiveType.TALK : quest.objectives().get(0).type();
        return switch (type) {
            case KILL -> Material.IRON_SWORD;
            case MINE -> Material.IRON_PICKAXE;
            case HARVEST -> Material.WHEAT;
            case PLACE -> Material.BRICKS;
            case CRAFT -> Material.CRAFTING_TABLE;
            case SMELT -> Material.FURNACE;
            case FISH -> Material.FISHING_ROD;
            case BREED -> Material.WHEAT_SEEDS;
            case TAME -> Material.BONE;
            case SHEAR -> Material.SHEARS;
            case ENCHANT -> Material.ENCHANTING_TABLE;
            case CONSUME -> Material.COOKED_BEEF;
            case DELIVER -> Material.CHEST;
            case TALK -> Material.EMERALD;
        };
    }

    /** Called by the listener for a click in the top inventory; the click itself is already cancelled. */
    void click(int slot, ClickType type) {
        String questId = questAt.get(slot);
        if (questId != null) {
            Quest quest = plugin.quests().get(questId);
            if (quest == null) {
                return;
            }
            if (type == ClickType.SHIFT_RIGHT && quest.category() != QuestCategory.STORY) {
                if (plugin.questManager().abandon(player, quest)) {
                    plugin.send(player, "<gray>Abandoned <white>" + Text.escape(quest.name()) + "</white>.");
                    player.playSound(player.getLocation(), Sound.ENTITY_VILLAGER_NO, 0.7f, 1f);
                }
            } else {
                plugin.tracker().track(player, questId);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1.2f);
            }
            fill();
            return;
        }
        switch (slot) {
            case SLOT_BOOK -> {
                player.closeInventory();
                plugin.book().open(player);
            }
            case SLOT_CLOSE -> player.closeInventory();
            case SLOT_TRACKER -> {
                plugin.tracker().toggle(player);
                player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1f);
                fill();
            }
            default -> {
            }
        }
    }

    private String bar(int done, int total) {
        int length = 12;
        int filled = total <= 0 ? 0 : (int) Math.round((double) done / total * length);
        return "<green>" + "▮".repeat(filled) + "<dark_gray>" + "▯".repeat(length - filled);
    }

    private static ItemStack glow(ItemStack stack) {
        stack.editMeta(meta -> meta.setEnchantmentGlintOverride(true));
        return stack;
    }

    private static ItemStack item(Material material, String name, List<String> lore) {
        ItemStack stack = new ItemStack(material);
        ItemMeta meta = stack.getItemMeta();
        meta.displayName(Text.mm("<!italic>" + name));
        List<Component> lines = new ArrayList<>(lore.size());
        for (String line : lore) {
            lines.add(Text.mm("<!italic>" + line));
        }
        meta.lore(lines);
        meta.addItemFlags(ItemFlag.values());
        stack.setItemMeta(meta);
        return stack;
    }
}
