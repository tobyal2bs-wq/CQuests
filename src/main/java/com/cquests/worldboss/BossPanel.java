package com.cquests.worldboss;

import com.cquests.CQuestsPlugin;
import com.cquests.gui.LockedMenu;
import com.cquests.gui.QuestMenu;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.Sound;
import org.bukkit.entity.Player;
import org.bukkit.event.inventory.ClickType;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

/**
 * The operators' world boss panel (/cq worldboss menu, or the command block in /quests): every boss
 * with its state. Left-click spawns it for real at the main arena with an announcement, right-click
 * tries it in front of you with nothing paid, shift-click sends it away. The bottom row holds the
 * weekly schedule, stop all, set the spawn here and the self-test.
 */
public final class BossPanel implements LockedMenu {
    private static final int SLOT_SCHEDULE = 45, SLOT_SPAWN = 46, SLOT_STOP = 47, SLOT_CLOSE = 49, SLOT_SELFTEST = 52, SLOT_BACK = 53;

    private final CQuestsPlugin plugin;
    private final Player player;
    private final Inventory inventory;
    private final Map<Integer, String> bossAt = new HashMap<>();

    private BossPanel(CQuestsPlugin plugin, Player player) {
        this.plugin = plugin; this.player = player;
        this.inventory = Bukkit.createInventory(this, 54, Text.mm("<dark_gray>World boss controls"));
    }

    public static void open(CQuestsPlugin plugin, Player player) {
        if (!player.hasPermission("cquests.admin")) { plugin.send(player, "<red>Only operators can open the boss controls."); return; }
        Sched.entity(player, () -> {
            BossPanel panel = new BossPanel(plugin, player);
            panel.fill();
            player.openInventory(panel.inventory);
            player.playSound(player.getLocation(), Sound.BLOCK_ENDER_CHEST_OPEN, 0.6f, 1.2f);
        });
    }

    @Override public Inventory getInventory() { return inventory; }
    @Override public UUID viewer() { return player.getUniqueId(); }

    private void fill() {
        inventory.clear(); bossAt.clear();
        WorldBossService wb = plugin.worldBosses();
        List<WorldBossDef> defs = new ArrayList<>(wb.defs().values());
        defs.sort((a, b) -> a.seasonal() == b.seasonal() ? 0 : a.seasonal() ? 1 : -1);
        WorldBossDef next = wb.upcoming();
        for (int i = 0; i < defs.size() && i < 45; i++) {
            WorldBossDef d = defs.get(i);
            boolean alive = wb.alive(d.id());
            List<String> lore = new ArrayList<>();
            if (!d.title().isBlank()) lore.add("<gray>" + Text.escape(d.title()));
            lore.add("<dark_gray>" + d.id() + " · " + Math.round(d.health()) + " health" + (d.seasonal() ? " · <light_purple>" + d.season() : ""));
            lore.add("<dark_gray>Attacks: <gray>" + String.join(", ", d.abilities()));
            lore.add("");
            if (alive) lore.add("<green>● Alive now");
            if (next != null && next.id().equals(d.id())) lore.add("<aqua>Next weekly boss");
            lore.add("<yellow>Left-click <gray>spawn it now at its arena (announced, real rewards)");
            lore.add("<yellow>Right-click <gray>try it in front of you (nothing paid)");
            lore.add("<yellow>Shift-click <gray>send it away");
            ItemStack icon = QuestMenu.item(icon(d), d.name(), lore);
            if (alive) icon.editMeta(m -> m.setEnchantmentGlintOverride(true));
            inventory.setItem(i, icon);
            bossAt.put(i, d.id());
        }
        boolean on = wb.scheduleOn();
        inventory.setItem(SLOT_SCHEDULE, QuestMenu.item(Material.CLOCK, "<white>Weekly schedule: " + (on ? "<green>on" : "<red>off"),
                List.of("<gray>One boss wakes every week at the main arena.", "<yellow>Click to turn it " + (on ? "off" : "on") + ".")));
        inventory.setItem(SLOT_SPAWN, QuestMenu.item(Material.BEACON, "<white>Set the boss spawn here",
                List.of("<gray>Bosses from this panel appear where you stand now.", "<gray>Draw the border with <yellow>/cq worldboss wand main")));
        inventory.setItem(SLOT_STOP, QuestMenu.item(Material.BARRIER, "<red>Send every boss away", List.of("<gray>Ends every fight, nothing is paid.")));
        inventory.setItem(SLOT_CLOSE, QuestMenu.item(Material.OAK_DOOR, "<gray>Close", List.of()));
        inventory.setItem(SLOT_SELFTEST, QuestMenu.item(Material.COMMAND_BLOCK, "<white>Self-test every boss",
                List.of("<gray>Spawns each boss near the world spawn,", "<gray>runs every attack and death, then reports.")));
        inventory.setItem(SLOT_BACK, QuestMenu.item(Material.ARROW, "<white>Back to quests", List.of()));
    }

    private static Material icon(WorldBossDef d) {
        Material egg = Material.matchMaterial(d.entity().name() + "_SPAWN_EGG");
        return egg != null ? egg : Material.DRAGON_HEAD;
    }

    @Override
    public void click(int slot, ClickType type) {
        WorldBossService wb = plugin.worldBosses();
        String id = bossAt.get(slot);
        if (id != null) {
            if (type.isShiftClick()) {
                boolean sent = wb.stopBoss(id);
                plugin.send(player, sent ? "<gray>Sent it away." : "<gray>That boss is not alive.");
            } else if (type.isRightClick()) {
                player.closeInventory();
                wb.test(player, id);
                return;
            } else {
                player.closeInventory();
                if (wb.spawnAt(player, id, "main")) plugin.send(player, "<green>Summoning it at the main arena...");
                return;
            }
            Sched.entityLater(player, 2, this::fill);
            return;
        }
        switch (slot) {
            case SLOT_SCHEDULE -> { wb.scheduleToggle(player, !wb.scheduleOn()); fill(); }
            case SLOT_SPAWN -> { wb.setSpawn(player, "main"); fill(); }
            case SLOT_STOP -> { wb.stopAll(); plugin.send(player, "<gray>Every world boss was sent away."); Sched.entityLater(player, 2, this::fill); }
            case SLOT_SELFTEST -> { player.closeInventory(); plugin.send(player, "<gray>Spawning every world boss near the world spawn..."); wb.selfTest(player); }
            case SLOT_BACK -> { player.closeInventory(); QuestMenu.open(plugin, player); }
            case SLOT_CLOSE -> player.closeInventory();
            default -> { }
        }
        player.playSound(player.getLocation(), Sound.UI_BUTTON_CLICK, 0.6f, 1f);
    }

    static String lower(String s) { return s.toLowerCase(Locale.ROOT); }
}
