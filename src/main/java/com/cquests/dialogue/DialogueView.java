package com.cquests.dialogue;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import net.kyori.adventure.inventory.Book;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.serializer.plain.PlainTextComponentSerializer;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** A paginated conversation with one server-validated action. */
public final class DialogueView implements LockedMenu {
    private final Player player;
    private final CQuestsPlugin plugin;
    private final NpcDef npc;
    private final List<List<String>> pages;
    private final String label;
    private final String token;
    private final Inventory inventory;
    private int page;

    public DialogueView(CQuestsPlugin plugin, Player player, NpcDef npc, List<String> lines, String label, String token) {
        this.plugin = plugin; this.player = player; this.npc = npc; this.label = label; this.token = token;
        pages = paginate(lines, 48, 10);
        inventory = Bukkit.createInventory(this, 54, Text.mm(npc.name()));
    }

    public void open() { fill(); player.openInventory(inventory); }
    public UUID viewer() { return player.getUniqueId(); }
    public Inventory getInventory() { return inventory; }

    private void fill() {
        for (int i = 0; i < 54; i++) inventory.setItem(i, QuestMenu.item(Material.BLACK_STAINED_GLASS_PANE, " ", List.of()));
        inventory.setItem(4, QuestMenu.item(Material.PLAYER_HEAD, "<white><bold>" + npc.name(),
                List.of("<gray>" + Text.escape(npc.title()), "<aqua>Page " + (page + 1) + "/" + pages.size())));
        inventory.setItem(22, QuestMenu.item(Material.WRITABLE_BOOK, "<gold>" + npc.name() + "</gold><gray> says…",
                pages.get(page).stream().map(s -> "<white>" + Text.escape(s)).toList()));
        if (token != null) inventory.setItem(40, QuestMenu.item(page + 1 < pages.size() ? Material.GRAY_CONCRETE : Material.LIME_CONCRETE, "<green><bold>" + Text.escape(label),
                List.of("<gray>" + (page + 1 < pages.size() ? "There is more to hear. Turn the page." : "Click to reply."))));
        inventory.setItem(49, QuestMenu.item(Material.BARRIER, "<gray>See you around", List.of("<gray>You can speak again any time.")));
        if (page > 0) inventory.setItem(45, QuestMenu.item(Material.ARROW, "<white>Previous page", List.of()));
        if (page + 1 < pages.size()) inventory.setItem(53, QuestMenu.item(Material.ARROW, "<white>Next page", List.of()));
        inventory.setItem(47, QuestMenu.item(Material.BOOK, "<white>Use book dialogue", List.of("<gray>Click to read this conversation in a book.")));
    }

    public void click(int slot, ClickType type) {
        if (slot == 45 && page > 0) { page--; fill(); }
        else if (slot == 53 && page + 1 < pages.size()) { page++; fill(); }
        else if (slot == 49) Sched.entity(player, player::closeInventory);
        else if (slot == 47) Sched.entity(player, () -> {
            plugin.questManager().data(player).setMenuMode("book");
            plugin.store().saveNow(plugin.questManager().data(player));
            openBook(plugin, player, npc, pages.stream().flatMap(List::stream).toList(), label, token);
        });
        else if (slot == 40 && token != null && page + 1 == pages.size()) Sched.entity(player, () -> {
            player.closeInventory(); plugin.dialogue().respond(player, token);
        });
    }

    public static void openBook(CQuestsPlugin plugin, Player player, NpcDef npc, List<String> lines, String label, String token) {
        List<Component> pages = new ArrayList<>();
        for (List<String> text : paginate(lines, 18, 8)) {
            pages.add(Text.mm("<black><bold>" + Text.escape(Text.plain(Text.mm(npc.name()))) + "</bold>\n\n" + Text.escape(String.join("\n", text))));
        }
        String action = token == null ? "" : "<click:run_command:'/quests respond " + token + "'><dark_green><bold>["
                + Text.escape(label) + "]</bold></dark_green></click>\n\n";
        pages.add(Text.mm("<black><bold>Your response</bold>\n\n" + action
                + "<click:run_command:'/quests mode menu'><dark_blue>[Use menu dialogue]</dark_blue></click>\n\n<dark_gray>Close the book to take a moment. You can speak again any time.</dark_gray>"));
        player.openBook(Book.book(Text.mm(npc.name()), Component.text("The Wanderers"), pages));
    }

    public static List<List<String>> paginate(List<String> lines, int width, int height) {
        List<List<String>> pages = new ArrayList<>(); List<String> current = new ArrayList<>();
        for (String rich : lines) {
            String plain = PlainTextComponentSerializer.plainText().serialize(Text.mm(rich));
            for (String paragraph : plain.split("\n", -1)) {
                String rest = paragraph.strip();
                do {
                    int end = Math.min(width, rest.length());
                    if (end < rest.length()) {
                        int space = rest.lastIndexOf(' ', end);
                        if (space > 0) end = space;
                    }
                    current.add(rest.substring(0, end));
                    rest = rest.substring(end).stripLeading();
                    if (current.size() == height) { pages.add(List.copyOf(current)); current.clear(); }
                } while (!rest.isEmpty());
            }
        }
        if (!current.isEmpty() || pages.isEmpty()) pages.add(List.copyOf(current));
        return pages;
    }
}
