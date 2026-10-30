package com.cquests.finale;

import com.cquests.CQuestsPlugin;
import com.cquests.data.JourneyEntry;
import com.cquests.data.PlayerData;
import com.cquests.model.Quest;
import com.cquests.util.Text;
import net.kyori.adventure.inventory.Book;
import net.kyori.adventure.text.Component;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.BookMeta;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * "Your Story": a written book made from the player's own journey, about 15 to 20 pages. It is built
 * once when the journey ends, from data already in memory, and given as a tattered copy so it can't be
 * duplicated in a crafting table.
 */
public final class StoryBook {

    private static final int LINES_PER_PAGE = 13;
    private static final int CHARS_PER_LINE = 19;

    private StoryBook() {
    }

    /** Gives the book once per player; later calls do nothing. */
    public static void give(CQuestsPlugin plugin, Player player) {
        PlayerData data = plugin.questManager().data(player);
        if (!data.claimStoryBook()) {
            return;
        }
        plugin.store().saveNow(data);
        ItemStack book = new ItemStack(Material.WRITTEN_BOOK);
        BookMeta meta = (BookMeta) book.getItemMeta();
        meta.title(Text.mm("Your Story"));
        meta.author(Text.mm(Text.escape(player.getName())));
        meta.setGeneration(BookMeta.Generation.TATTERED);
        meta.pages(pages(plugin, player, data));
        book.setItemMeta(meta);
        player.getInventory().addItem(book).values()
                .forEach(left -> player.getWorld().dropItem(player.getLocation(), left));
        plugin.send(player, "<gold>You received <white><bold>Your Story</bold></white>, the book of your journey.");
    }

    /** Opens the same book without giving an item, for /quests story. */
    public static void open(CQuestsPlugin plugin, Player player) {
        PlayerData data = plugin.questManager().data(player);
        player.openBook(Book.book(Text.mm("Your Story"), Text.mm(Text.escape(player.getName())), pages(plugin, player, data)));
    }

    static List<Component> pages(CQuestsPlugin plugin, Player player, PlayerData data) {
        List<JourneyEntry> journey = data.journey();
        long start = data.startedAt() > 0 ? data.startedAt() : journey.isEmpty() ? System.currentTimeMillis() : journey.get(0).time();
        long end = journey.isEmpty() ? System.currentTimeMillis() : journey.get(journey.size() - 1).time();
        long days = Math.max(1, (end - start) / 86_400_000L + 1);
        String date = new SimpleDateFormat("d MMM yyyy", Locale.ROOT).format(new Date(start));

        List<Component> pages = new ArrayList<>();
        pages.add(Text.mm("\n<dark_gray>    ✦ ✦ ✦\n\n<gold><bold>   Your Story</bold></gold>\n\n<black>The journey of\n<dark_blue><bold>" + Text.escape(player.getName())
                + "</bold></dark_blue>\n<black>on " + Text.escape(plugin.settings().serverName)
                + "\n\n<dark_gray>Began " + date + "\n" + days + (days == 1 ? " day" : " days") + " on the road\n\n<dark_gray>    ✦ ✦ ✦"));

        Pager pager = new Pager(pages);
        int chapter = -1;
        for (JourneyEntry entry : journey) {
            Quest quest = plugin.quests().get(entry.questId());
            if (quest == null) {
                continue;
            }
            if (quest.chapter() != chapter) {
                chapter = quest.chapter();
                pager.breakPage();
                pager.add("<dark_red><bold>Chapter " + chapter + "</bold></dark_red>", 1);
                String name = plugin.quests().chapterName(chapter);
                if (!name.isEmpty()) {
                    pager.add("<dark_gray><italic>" + Text.escape(name) + "</italic></dark_gray>", lines(name));
                }
                pager.add("", 1);
            }
            long day = (entry.time() - start) / 86_400_000L + 1;
            String line = "<dark_gray>" + day + "</dark_gray> <black>" + Text.escape(quest.name());
            pager.add(line, lines(day + " " + quest.name()));
            if (quest.big() && !quest.complete().isEmpty()) {
                String quote = quest.complete().get(0);
                pager.add("<dark_blue><italic>\"" + plugin.questManager().fill(Text.escape(quote), player) + "\"</italic></dark_blue>", lines(quote) + 1);
            }
        }
        pager.breakPage();
        pages.add(Text.mm("\n<gold><bold>   The End</bold></gold>\n\n<black>Story quests: <dark_blue>" + data.completedCount()
                + "\n<black>Side quests: <dark_blue>" + String.format(Locale.ROOT, "%,d", data.totalSideDone())
                + "\n<black>Daily quests: <dark_blue>" + data.dailiesDone()
                + "\n\n<dark_gray><italic>Every villager remembers your name.\n\n<dark_gray>    ✦ ✦ ✦"));
        return pages;
    }

    private static int lines(String text) {
        return Math.max(1, (text.length() + CHARS_PER_LINE - 1) / CHARS_PER_LINE);
    }

    /** Packs lines into pages without overflowing them. */
    private static final class Pager {
        private final List<Component> pages;
        private final StringBuilder page = new StringBuilder();
        private int used;

        Pager(List<Component> pages) {
            this.pages = pages;
        }

        void add(String miniMessage, int lineCount) {
            if (used + lineCount > LINES_PER_PAGE) {
                breakPage();
            }
            page.append(miniMessage).append("<reset>\n");
            used += lineCount;
        }

        void breakPage() {
            if (used > 0) {
                pages.add(Text.mm(page.toString()));
                page.setLength(0);
                used = 0;
            }
        }
    }
}
