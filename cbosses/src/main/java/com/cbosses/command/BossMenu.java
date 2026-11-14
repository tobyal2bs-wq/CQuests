package com.cbosses.command;

import com.cbosses.T;

import com.cbosses.CBossesPlugin;
import com.cbosses.fight.BossDef;
import com.cbosses.util.Text;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemStack;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

/** /cbosses menu: every boss as an icon. Left-click tests it in front of you, right-click spawns it at the main arena. */
public final class BossMenu implements Listener {
    private final CBossesPlugin plugin;

    public BossMenu(CBossesPlugin plugin) { this.plugin = plugin; }

    private static final class Holder implements InventoryHolder {
        final List<String> ids = new ArrayList<>();
        final int page;
        Inventory inv;
        Holder(int page) { this.page = page; }
        @Override public @NotNull Inventory getInventory() { return inv; }
    }

    public void open(Player player, int page) {
        List<BossDef> all = new ArrayList<>(plugin.service().defs().values());
        all.removeIf(BossDef::sidekick);
        int pages = Math.max(1, (all.size() + 44) / 45);
        page = Math.max(0, Math.min(pages - 1, page));
        Holder h = new Holder(page);
        Inventory inv = Bukkit.createInventory(h, 54, Text.mm(T.t("menu.bosses", "<dark_gray>Bosses <gray>(<page>/<pages>)", "page", (page + 1), "pages", pages)));
        h.inv = inv;
        for (int i = 0; i < 45 && page * 45 + i < all.size(); i++) {
            BossDef d = all.get(page * 45 + i);
            h.ids.add(d.id());
            inv.setItem(i, icon(d));
        }
        if (page > 0) inv.setItem(45, button(Material.ARROW, T.t("menu.previous-page", "<yellow>Previous page")));
        if (page < pages - 1) inv.setItem(53, button(Material.ARROW, T.t("menu.next-page", "<yellow>Next page")));
        inv.setItem(49, button(Material.CLOCK, T.t("menu.next-weekly-boss", "<gold>Next weekly boss: <white>") + Text.escape(plugin.service().upcomingName().isEmpty() ? "none" : plugin.service().upcomingName())
                + " <gray>" + plugin.service().nextText()));
        player.openInventory(inv);
    }

    private static ItemStack button(Material m, String name) {
        ItemStack item = new ItemStack(m);
        item.editMeta(meta -> meta.displayName(Text.mm(name).decoration(TextDecoration.ITALIC, false)));
        return item;
    }

    private ItemStack icon(BossDef d) {
        Material egg = Material.matchMaterial(d.entity().name() + "_SPAWN_EGG");
        ItemStack item = new ItemStack(egg != null ? egg : d.mini() ? Material.TURTLE_EGG : d.chapterBoss() ? Material.WRITTEN_BOOK : d.seasonal() ? Material.CAKE : Material.WITHER_SKELETON_SKULL);
        item.editMeta(meta -> {
            meta.displayName(Text.mm(d.name()).decoration(TextDecoration.ITALIC, false));
            List<Component> lore = new ArrayList<>();
            if (!d.title().isBlank()) lore.add(Text.mm("<gray><italic>" + Text.escape(d.title())));
            lore.add(Text.mm(d.mini() ? T.t("menu.mini", "<yellow>Mini boss") : d.chapterBoss() ? T.t("menu.chapter", "<aqua>Chapter ") + d.chapter() + " boss" : d.seasonal() ? T.t("menu.seasonal", "<light_purple>Seasonal: ") + d.season() : T.t("menu.world-boss", "<gold>World boss"))
                    .decoration(TextDecoration.ITALIC, false));
            lore.add(Text.mm(T.t("menu.health-attacks", "<gray>Health <white><health></white>  Attacks <white><size></white>  <movement>", "health", (int) d.health(), "size", d.abilities().size(), "movement", d.movement())).decoration(TextDecoration.ITALIC, false));
            if (!d.description().isBlank()) for (String line : wrap(d.description(), 38)) lore.add(Text.mm("<dark_gray>" + Text.escape(line)).decoration(TextDecoration.ITALIC, false));
            lore.add(Component.empty());
            lore.add(Text.mm(T.t("menu.left-click-spawn-here", "<yellow>Left-click</yellow> <gray>spawn it where you stand (real fight)")).decoration(TextDecoration.ITALIC, false));
            lore.add(Text.mm(T.t("menu.shift-click-test", "<yellow>Shift-left</yellow> <gray>test it in front of you (no rewards)")).decoration(TextDecoration.ITALIC, false));
            lore.add(Text.mm(T.t("menu.right-click-spawn-at-the", "<yellow>Right-click</yellow> <gray>spawn at the main arena")).decoration(TextDecoration.ITALIC, false));
            meta.lore(lore);
        });
        return item;
    }

    static List<String> wrap(String text, int width) {
        List<String> out = new ArrayList<>();
        StringBuilder line = new StringBuilder();
        for (String word : text.split("\\s+")) {
            if (line.length() + word.length() + 1 > width && !line.isEmpty()) { out.add(line.toString()); line.setLength(0); }
            if (!line.isEmpty()) line.append(' ');
            line.append(word);
        }
        if (!line.isEmpty()) out.add(line.toString());
        return out;
    }

    @EventHandler
    public void click(InventoryClickEvent event) {
        if (!(event.getInventory().getHolder(false) instanceof Holder h)) return;
        event.setCancelled(true);
        if (!(event.getWhoClicked() instanceof Player p) || event.getClickedInventory() != event.getInventory()) return;
        if (!BossCommand.canControl(p)) { p.closeInventory(); return; }
        int slot = event.getRawSlot();
        if (slot == 45 && h.page > 0) { open(p, h.page - 1); return; }
        if (slot == 53) { open(p, h.page + 1); return; }
        if (slot < 0 || slot >= h.ids.size()) return;
        String id = h.ids.get(slot);
        p.closeInventory();
        if (event.getClick() == ClickType.RIGHT || event.getClick() == ClickType.SHIFT_RIGHT)
            plugin.service().spawnAt(p, id, plugin.getConfig().getString("schedule.arena", "main"));
        else if (event.getClick() == ClickType.SHIFT_LEFT) plugin.service().test(p, id);
        else plugin.service().spawnHere(p, id);
    }

    @EventHandler
    public void drag(InventoryDragEvent event) {
        if (event.getInventory().getHolder(false) instanceof Holder) event.setCancelled(true);
    }
}
