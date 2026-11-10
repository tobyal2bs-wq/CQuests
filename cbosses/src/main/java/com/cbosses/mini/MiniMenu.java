package com.cbosses.mini;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.fight.BossDef;
import com.cbosses.util.Text;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.Location;
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

/**
 * /cbosses minis: the op screen for mini bosses. Top: every spot (click to manage). Bottom row: add a spot
 * where you stand, markers on/off, mode, timer, max alive, per round, wake one now, on/off.
 * A spot's own screen picks which minis may wake there.
 */
public final class MiniMenu implements Listener {
    private final CBossesPlugin plugin;
    private final MiniBosses minis;

    public MiniMenu(CBossesPlugin plugin, MiniBosses minis) { this.plugin = plugin; this.minis = minis; }

    private static final class Holder implements InventoryHolder {
        final List<String> ids = new ArrayList<>();
        final String spot;
        Inventory inv;
        Holder(String spot) { this.spot = spot; }
        @Override public @NotNull Inventory getInventory() { return inv; }
    }

    public void open(Player p) {
        Holder h = new Holder(null);
        Inventory inv = Bukkit.createInventory(h, 54, Text.mm(T.t("mini.menu", "<dark_gray>Mini bosses")));
        h.inv = inv;
        List<MiniBosses.Spot> all = minis.spots();
        for (int i = 0; i < 45 && i < all.size(); i++) {
            MiniBosses.Spot s = all.get(i);
            h.ids.add(s.id);
            inv.setItem(i, item(s.enabled ? Material.BEACON : Material.GRAY_STAINED_GLASS, "<gold>" + s.id + (s.enabled ? "" : " <red>(off)"),
                    "<gray>" + s.world + " " + (int) s.x + " " + (int) s.y + " " + (int) s.z,
                    "<gray>Border radius <white>" + s.radius,
                    "<gray>Minis: <white>" + (s.bosses.isEmpty() ? "any" : String.join(", ", s.bosses)),
                    "",
                    "<yellow>Left</yellow> <gray>teleport there",
                    "<yellow>Right</yellow> <gray>turn on/off",
                    "<yellow>Shift-left</yellow> <gray>radius +4, <yellow>Shift-right</yellow> <gray>radius -4",
                    "<yellow>Q</yellow> <gray>choose which minis wake here",
                    "<yellow>Ctrl-Q</yellow> <red>delete this spot"));
        }
        inv.setItem(45, item(Material.EMERALD, "<green>Add a spot where you stand", "<gray>Radius " + plugin.getConfig().getInt("minis.radius", 24)));
        inv.setItem(46, item(minis.showing(p) ? Material.BARRIER : Material.GLASS, "<aqua>Markers: " + (minis.showing(p) ? "<green>on" : "<red>off"),
                "<gray>Barrier markers and a ring show every spot,", "<gray>only to you."));
        inv.setItem(47, item(Material.COMPASS, "<aqua>Mode: <white>" + minis.mode(), "<gray>fixed: only your spots", "<gray>random: near a random player",
                "<gray>mixed: either", "<yellow>Click</yellow> <gray>to change"));
        inv.setItem(48, item(Material.CLOCK, "<aqua>Every <white>" + minis.everyMinutes() + " minutes", "<gray>Next in <white>" + minis.nextText(),
                "<yellow>Left</yellow> <gray>+5  <yellow>Right</yellow> <gray>-5", "<yellow>Shift</yellow> <gray>+/-30"));
        inv.setItem(49, item(Material.NETHER_STAR, "<gold>Wake a mini now", "<gray>Alive " + minis.alive() + "/" + minis.maxAlive(), "<yellow>Right</yellow> <gray>also restart the timer"));
        inv.setItem(50, item(Material.TOTEM_OF_UNDYING, "<aqua>Max alive: <white>" + minis.maxAlive(), "<yellow>Left</yellow> <gray>+1  <yellow>Right</yellow> <gray>-1"));
        inv.setItem(51, item(Material.SPAWNER, "<aqua>Per round: <white>" + minis.perRound(), "<yellow>Left</yellow> <gray>+1  <yellow>Right</yellow> <gray>-1"));
        inv.setItem(52, item(Material.MAP, "<aqua>Mini bosses: <white>" + minis.minis().size(), "<gray>Allowed list: " + (plugin.getConfig().getStringList("minis.bosses").isEmpty() ? "all" : "custom"),
                "<gray>Set minis.bosses in config.yml to limit them."));
        inv.setItem(53, item(minis.enabled() ? Material.LIME_DYE : Material.GRAY_DYE, "<aqua>Mini bosses " + (minis.enabled() ? "<green>on" : "<red>off"), "<yellow>Click</yellow> <gray>to switch"));
        p.openInventory(inv);
    }

    private void openSpot(Player p, MiniBosses.Spot s) {
        Holder h = new Holder(s.id);
        Inventory inv = Bukkit.createInventory(h, 54, Text.mm("<dark_gray>Minis at " + s.id));
        h.inv = inv;
        List<BossDef> all = minis.minis();
        for (int i = 0; i < 45 && i < all.size(); i++) {
            BossDef d = all.get(i);
            h.ids.add(d.id());
            boolean on = s.bosses.isEmpty() || s.bosses.contains(d.id());
            inv.setItem(i, item(on ? Material.LIME_STAINED_GLASS_PANE : Material.RED_STAINED_GLASS_PANE, d.name(), on ? "<green>Can wake here" : "<red>Never wakes here", "<yellow>Click</yellow> <gray>to switch"));
        }
        inv.setItem(45, item(Material.ARROW, "<yellow>Back"));
        inv.setItem(49, item(Material.BARRIER, "<yellow>Allow every mini"));
        p.openInventory(inv);
    }

    private static ItemStack item(Material m, String name, String... lore) {
        ItemStack it = new ItemStack(m);
        it.editMeta(meta -> {
            meta.displayName(Text.mm(name).decoration(TextDecoration.ITALIC, false));
            List<Component> l = new ArrayList<>();
            for (String s : lore) l.add(Text.mm(s).decoration(TextDecoration.ITALIC, false));
            meta.lore(l);
        });
        return it;
    }

    @EventHandler
    public void click(InventoryClickEvent e) {
        if (!(e.getInventory().getHolder(false) instanceof Holder h)) return;
        e.setCancelled(true);
        if (!(e.getWhoClicked() instanceof Player p) || e.getClickedInventory() != e.getInventory()) return;
        if (!com.cbosses.command.BossCommand.canControl(p)) { p.closeInventory(); return; }
        int slot = e.getRawSlot();
        ClickType c = e.getClick();
        if (h.spot != null) { spotClick(p, h, slot); return; }
        if (slot < 45) {
            if (slot >= h.ids.size()) return;
            MiniBosses.Spot s = minis.spot(h.ids.get(slot));
            if (s == null) return;
            switch (c) {
                case LEFT -> { Location l = s.location(); if (l != null) { p.closeInventory(); p.teleportAsync(l.add(0, 1, 0)); } return; }
                case RIGHT -> s.enabled = !s.enabled;
                case SHIFT_LEFT -> s.radius = Math.min(96, s.radius + 4);
                case SHIFT_RIGHT -> s.radius = Math.max(8, s.radius - 4);
                case DROP -> { openSpot(p, s); return; }
                case CONTROL_DROP -> { minis.remove(s.id); plugin.send(p, T.t("mini.removed", "<gray>Spot <white><id></white> removed.", "id", s.id)); }
                default -> { return; }
            }
            minis.save();
            open(p);
            return;
        }
        boolean right = c.isRightClick(), shift = c.isShiftClick();
        switch (slot) {
            case 45 -> { var s = minis.add(p.getLocation(), Math.max(8, plugin.getConfig().getInt("minis.radius", 24)));
                plugin.send(p, T.t("mini.added", "<green>Spot <white><id></white> added where you stand.", "id", s.id)); }
            case 46 -> minis.toggleMarkers(p);
            case 47 -> minis.set("mode", MiniBosses.MODES.get((MiniBosses.MODES.indexOf(minis.mode()) + 1) % 3));
            case 48 -> { int step = shift ? 30 : 5; minis.set("every-minutes", Math.max(5, minis.everyMinutes() + (right ? -step : step))); }
            case 49 -> { if (right) minis.setNext(System.currentTimeMillis() + minis.everyMinutes() * 60_000L);
                int n = minis.spawnRound(null);
                plugin.send(p, n > 0 ? T.t("mini.woke", "<green>A mini boss is waking.") : T.t("mini.none", "<yellow>No mini could wake (max alive reached, no spots or no minis).")); }
            case 50 -> minis.set("max-alive", Math.max(1, minis.maxAlive() + (right ? -1 : 1)));
            case 51 -> minis.set("per-round", Math.max(1, minis.perRound() + (right ? -1 : 1)));
            case 53 -> minis.set("enabled", !minis.enabled());
            default -> { return; }
        }
        open(p);
    }

    private void spotClick(Player p, Holder h, int slot) {
        MiniBosses.Spot s = minis.spot(h.spot);
        if (s == null) { p.closeInventory(); return; }
        if (slot == 45) { open(p); return; }
        if (slot == 49) { s.bosses.clear(); minis.save(); openSpot(p, s); return; }
        if (slot < 0 || slot >= h.ids.size()) return;
        String id = h.ids.get(slot);
        synchronized (minis) {
            if (s.bosses.isEmpty()) { for (BossDef d : minis.minis()) if (!d.id().equals(id)) s.bosses.add(d.id()); }
            else if (!s.bosses.remove(id)) s.bosses.add(id);
            else if (s.bosses.isEmpty()) s.bosses.add(id);
            if (s.bosses.size() >= minis.minis().size()) s.bosses.clear();
        }
        minis.save();
        openSpot(p, s);
    }

    @EventHandler
    public void drag(InventoryDragEvent e) { if (e.getInventory().getHolder(false) instanceof Holder) e.setCancelled(true); }
}
