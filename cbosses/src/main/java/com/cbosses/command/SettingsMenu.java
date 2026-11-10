package com.cbosses.command;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.command.CommandSender;
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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * /cbosses settings: every option of config.yml on five pages. On 1.21.6 and newer servers it opens as a
 * native dialog screen (toggle buttons that cycle, sliders, text boxes and a Save button), the same kind of
 * screen as the game's own settings; older servers get a chest menu where a click changes a value. Both
 * write config.yml and reload the plugin, so a change applies at once.
 */
public final class SettingsMenu implements Listener {

    enum Kind { BOOL, CHOICE, INT, DOUBLE, TEXT }

    record Setting(String path, String label, Kind kind, List<String> options, double min, double max, double step, Material icon) {}

    record Page(String id, String title, Material icon, List<Setting> settings) {}

    private static final Gson GSON = new GsonBuilder().disableHtmlEscaping().create();
    private final CBossesPlugin plugin;

    public SettingsMenu(CBossesPlugin plugin) { this.plugin = plugin; }

    // ------------------------------------------------------------------------------------------ the pages

    private static Setting b(String path, String label, Material icon) { return new Setting(path, label, Kind.BOOL, List.of(), 0, 1, 1, icon); }
    private static Setting c(String path, String label, Material icon, String... options) { return new Setting(path, label, Kind.CHOICE, List.of(options), 0, 0, 0, icon); }
    private static Setting i(String path, String label, Material icon, int min, int max, int step) { return new Setting(path, label, Kind.INT, List.of(), min, max, step, icon); }
    private static Setting d(String path, String label, Material icon, double min, double max, double step) { return new Setting(path, label, Kind.DOUBLE, List.of(), min, max, step, icon); }
    private static Setting t(String path, String label, Material icon) { return new Setting(path, label, Kind.TEXT, List.of(), 0, 0, 0, icon); }

    List<Page> pages() {
        List<Page> out = new ArrayList<>();
        out.add(new Page("effects", "Effects and lag", Material.BLAZE_POWDER, List.of(
                b("enabled", "Plugin on", Material.LEVER),
                b("models", "Block models", Material.ARMOR_STAND),
                c("effects.quality", "Effect quality", Material.FIREWORK_ROCKET, "low", "medium", "high", "ultra"),
                c("effects.model-detail", "Model detail", Material.SPYGLASS, "low", "medium", "high"),
                d("effects.particle-multiplier", "Particles", Material.GLOWSTONE_DUST, 0, 2, 0.1),
                b("effects.flying-blocks", "Flying blocks", Material.GRAVEL),
                i("effects.max-flying-blocks", "Max flying blocks", Material.SAND, 0, 400, 10),
                i("effects.max-shards-per-death", "Shards per death", Material.AMETHYST_SHARD, 0, 128, 4),
                i("effects.model-update-ticks", "Model update ticks", Material.CLOCK, 1, 10, 1),
                i("effects.model-view-distance", "Model view distance", Material.ENDER_EYE, 32, 160, 8),
                b("effects.intro", "Entrance omens", Material.BELL),
                b("effects.intro-darkness", "Darkness at entrances", Material.BLACK_DYE))));
        out.add(new Page("schedule", "Weekly boss", Material.CLOCK, List.of(
                b("schedule.enabled", "Weekly boss on", Material.LEVER),
                t("schedule.days", "Days (comma list)", Material.PAPER),
                t("schedule.time", "Time (HH:MM)", Material.CLOCK),
                t("schedule.zone", "Time zone (blank = server)", Material.COMPASS),
                i("schedule.warn-minutes", "Warn minutes before", Material.GOAT_HORN, 0, 60, 1),
                t("schedule.arena", "Arena", Material.LODESTONE),
                c("schedule.order", "Order", Material.HOPPER, "rotate", "random"),
                b("schedule.include-chapter-bosses", "Include chapter bosses", Material.WRITABLE_BOOK))));
        out.add(new Page("fight", "Fights", Material.NETHERITE_SWORD, List.of(
                d("fight.health-multiplier", "Boss health x", Material.GOLDEN_APPLE, 0.25, 5, 0.25),
                d("fight.damage-multiplier", "Boss damage x", Material.IRON_SWORD, 0.25, 5, 0.25),
                i("fight.idle-minutes", "Leave when idle (min)", Material.COBWEB, 1, 30, 1),
                i("fight.max-minutes", "Longest fight (min)", Material.CLOCK, 5, 120, 5),
                b("fight.only-hurt-from-inside", "Only hurt from inside", Material.BARRIER),
                b("fight.gap-closer", "Boss closes the gap", Material.RABBIT_FOOT),
                i("fight.max-minions", "Max minions", Material.ZOMBIE_HEAD, 0, 30, 1),
                i("fight.max-active", "Max bosses at once", Material.WITHER_SKELETON_SKULL, 1, 20, 1),
                i("fight.boss-bar-range", "Boss bar range", Material.NAME_TAG, 16, 160, 8),
                b("fight.glow-plain-mobs", "Glow on plain mobs", Material.GLOW_INK_SAC),
                i("rewards.min-damage-percent", "Min damage for reward %", Material.EMERALD, 0, 50, 1),
                b("announcements.spawn-sound", "Spawn sound", Material.NOTE_BLOCK))));
        out.add(new Page("evolve", "Evolving and mythic bosses", Material.NETHER_STAR, List.of(
                b("evolve.enabled", "Bosses evolve", Material.EXPERIENCE_BOTTLE),
                d("evolve.chance", "Chance to evolve", Material.RABBIT_FOOT, 0, 1, 0.05),
                i("evolve.after-seconds", "First evolve after (s)", Material.CLOCK, 30, 600, 10),
                i("evolve.max-stages", "Most evolve stages", Material.LADDER, 1, 5, 1),
                d("evolve.damage-per-stage", "Extra damage per stage", Material.IRON_SWORD, 0, 1, 0.05),
                d("evolve.speed-per-stage", "Extra speed per stage", Material.SUGAR, 0, 0.5, 0.02),
                d("evolve.heal-percent", "Heal when evolving", Material.GOLDEN_APPLE, 0, 0.5, 0.05),
                d("mythic.health-multiplier", "Mythic health x", Material.ENCHANTED_GOLDEN_APPLE, 0.5, 5, 0.25),
                d("mythic.damage-multiplier", "Mythic damage x", Material.NETHERITE_SWORD, 0.5, 5, 0.05),
                b("mythic.always-evolve", "Mythic always evolve", Material.DRAGON_BREATH))));
        out.add(new Page("chapters", "Chapter bosses", Material.WRITABLE_BOOK, List.of(
                b("chapter-bosses.enabled", "Chapter bosses on", Material.LEVER),
                b("chapter-bosses.from-cquests", "Start from CQuests", Material.BOOK),
                i("chapter-bosses.countdown-seconds", "Countdown (s)", Material.CLOCK, 0, 60, 1),
                i("chapter-bosses.arena-radius", "Arena radius", Material.LODESTONE, 10, 64, 1),
                d("chapter-bosses.health-multiplier", "Health x", Material.GOLDEN_APPLE, 0.25, 5, 0.25),
                b("chapter-bosses.private", "Private fight", Material.ENDER_PEARL),
                b("chapter-bosses.allow-helpers", "Allow helpers", Material.PLAYER_HEAD),
                i("chapter-bosses.leave-after-seconds", "Leave after (s)", Material.OAK_DOOR, 5, 300, 5),
                b("chapter-bosses.announce", "Announce wins", Material.GOAT_HORN))));
        List<Setting> seasons = new ArrayList<>(List.of(
                b("seasons.follow-cquests", "Follow CQuests seasons", Material.BOOK),
                b("seasons.replace-weekly-boss", "Seasonal replaces weekly", Material.PUMPKIN)));
        var list = plugin.getConfig().getConfigurationSection("seasons.list");
        if (list != null) for (String id : list.getKeys(false))
            seasons.add(c("seasons.list." + id + ".mode", nice(id) + " season", Material.SUNFLOWER, "auto", "on", "off"));
        seasons.addAll(List.of(
                b("finale.enabled", "Finale on", Material.DRAGON_EGG),
                i("finale.delay-seconds", "Finale delay (s)", Material.CLOCK, 0, 600, 10),
                t("finale.arena", "Finale arena", Material.LODESTONE),
                b("worldguard.enabled", "WorldGuard support", Material.SHIELD),
                b("worldguard.bypass-spawn-blocking", "Bypass mob-spawning deny", Material.SPAWNER)));
        out.add(new Page("seasons", "Seasons, finale and WorldGuard", Material.SUNFLOWER, seasons));
        return out;
    }

    Page page(String id) {
        for (Page p : pages()) if (p.id.equalsIgnoreCase(id)) return p;
        return pages().get(0);
    }

    private static String nice(String s) {
        String t = s.replace('_', ' ').replace('-', ' ');
        return t.isEmpty() ? t : Character.toUpperCase(t.charAt(0)) + t.substring(1);
    }

    // ------------------------------------------------------------------------------------------ values

    String value(Setting s) {
        var cfg = plugin.getConfig();
        return switch (s.kind) {
            case BOOL -> String.valueOf(cfg.getBoolean(s.path, false));
            case INT -> String.valueOf(cfg.getInt(s.path, (int) s.min));
            case DOUBLE -> fmt(cfg.getDouble(s.path, 1));
            case CHOICE -> cfg.getString(s.path, s.options.get(0)).toLowerCase(Locale.ROOT);
            case TEXT -> cfg.isList(s.path) ? String.join(",", cfg.getStringList(s.path)) : cfg.getString(s.path, "");
        };
    }

    private static String fmt(double v) {
        return v == Math.rint(v) ? String.valueOf((long) v) : String.valueOf(Math.round(v * 100) / 100.0);
    }

    /** Sets one option from text, inside its limits. False when the text is not a valid value. */
    boolean set(Setting s, String raw) {
        var cfg = plugin.getConfig();
        String v = raw == null ? "" : raw.trim();
        try {
            switch (s.kind) {
                case BOOL -> {
                    if (!v.equalsIgnoreCase("true") && !v.equalsIgnoreCase("false")) return false;
                    cfg.set(s.path, Boolean.parseBoolean(v.toLowerCase(Locale.ROOT)));
                }
                case INT -> cfg.set(s.path, (int) Math.max(s.min, Math.min(s.max, Math.round(Double.parseDouble(v)))));
                case DOUBLE -> cfg.set(s.path, Math.max(s.min, Math.min(s.max, Math.round(Double.parseDouble(v) * 100) / 100.0)));
                case CHOICE -> {
                    if (!s.options.contains(v.toLowerCase(Locale.ROOT))) return false;
                    cfg.set(s.path, v.toLowerCase(Locale.ROOT));
                }
                case TEXT -> {
                    if (s.path.equals("schedule.days")) {
                        List<String> days = new ArrayList<>();
                        for (String d : v.split("[,; ]+")) {
                            if (d.isBlank()) continue;
                            java.time.DayOfWeek.valueOf(d.trim().toUpperCase(Locale.ROOT));
                            days.add(d.trim().toUpperCase(Locale.ROOT));
                        }
                        if (days.isEmpty()) return false;
                        cfg.set(s.path, days);
                    } else if (s.path.equals("schedule.time")) {
                        java.time.LocalTime.parse(v.length() == 4 ? "0" + v : v);
                        cfg.set(s.path, v);
                    } else if (s.path.equals("schedule.zone")) {
                        if (!v.isEmpty()) java.time.ZoneId.of(v);
                        cfg.set(s.path, v);
                    } else {
                        if (v.isEmpty() || !v.matches("[A-Za-z0-9_\\-]+")) return false;
                        cfg.set(s.path, v);
                    }
                }
            }
            return true;
        } catch (RuntimeException e) {
            return false;
        }
    }

    Setting find(String path) {
        for (Page p : pages()) for (Setting s : p.settings) if (s.path.equalsIgnoreCase(path)) return s;
        return null;
    }

    private void apply(CommandSender to) {
        plugin.saveConfig();
        plugin.reloadAll();
        plugin.send(to, T.t("settings.saved", "<green>Settings saved and applied."));
    }

    // ------------------------------------------------------------------------------------------ the command

    /** /cbosses settings [page] | set <path> <value> | save <page> key=value... (sent by the dialog's Save button) */
    public void command(CommandSender sender, String[] args) {
        String what = args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "";
        if (what.equals("set")) {
            if (args.length < 3) { plugin.send(sender, T.t("settings.set-usage", "<yellow>/cbosses settings set <path> <value>")); return; }
            Setting s = find(args[2]);
            String v = args.length > 3 ? String.join(" ", java.util.Arrays.copyOfRange(args, 3, args.length)) : "";
            if (s == null) { plugin.send(sender, T.t("settings.unknown", "<red>No setting <path>.", "path", Text.escape(args[2]))); return; }
            if (!set(s, v)) { plugin.send(sender, T.t("settings.bad-value", "<red><value> is not a valid value for <path>.", "value", Text.escape(v), "path", s.path)); return; }
            apply(sender);
            return;
        }
        if (what.equals("save") && args.length >= 3) {
            Page page = page(args[2]);
            Map<String, String> got = new LinkedHashMap<>();
            String last = null;
            for (int k = 3; k < args.length; k++) {
                int eq = args[k].indexOf('=');
                if (eq > 0 && args[k].substring(0, eq).matches("s\\d+")) { last = args[k].substring(0, eq); got.put(last, args[k].substring(eq + 1)); }
                else if (last != null) got.put(last, got.get(last) + " " + args[k]);
            }
            List<String> bad = new ArrayList<>();
            for (int k = 0; k < page.settings.size(); k++) {
                String v = got.get("s" + k);
                if (v == null) continue;
                Setting s = page.settings.get(k);
                if (!v.equals(value(s)) && !set(s, v)) bad.add(s.label);
            }
            if (!bad.isEmpty()) plugin.send(sender, T.t("settings.not-saved", "<red>Not changed, the value was not valid: <list>", "list", Text.escape(String.join(", ", bad))));
            apply(sender);
            if (sender instanceof Player p) open(p, page.id);
            return;
        }
        if (!(sender instanceof Player p)) { plugin.send(sender, T.t("command.players-only", "<red>Players only.")); return; }
        open(p, what.isEmpty() ? "effects" : what);
    }

    public void open(Player player, String pageId) {
        String mode = plugin.getConfig().getString("settings-menu", "auto").toLowerCase(Locale.ROOT);
        boolean dialog = mode.equals("dialog") || (!mode.equals("chest") && dialogs());
        if (dialog) openDialog(player, page(pageId));
        else openChest(player, page(pageId));
    }

    /** Native dialogs came in Minecraft 1.21.6. */
    static boolean dialogs() {
        try {
            String[] v = Bukkit.getMinecraftVersion().split("[.\\-]");
            int major = Integer.parseInt(v[0]), minor = v.length > 1 ? Integer.parseInt(v[1]) : 0, patch = v.length > 2 ? Integer.parseInt(v[2]) : 0;
            return major > 1 || minor > 21 || (minor == 21 && patch >= 6);
        } catch (RuntimeException e) {
            return false;
        }
    }

    // ------------------------------------------------------------------------------------------ the dialog (1.21.6+)

    private static JsonObject text(String s, String color) {
        JsonObject o = new JsonObject();
        o.addProperty("text", s);
        if (color != null) o.addProperty("color", color);
        return o;
    }

    private static JsonObject message(JsonObject contents) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "minecraft:plain_message");
        o.add("contents", contents);
        o.addProperty("width", 300);
        return o;
    }

    private static JsonObject button(String label, String color, JsonObject action, int width) {
        JsonObject o = new JsonObject();
        o.add("label", text(label, color));
        o.addProperty("width", width);
        if (action != null) o.add("action", action);
        return o;
    }

    private static JsonObject run(String command) {
        JsonObject o = new JsonObject();
        o.addProperty("type", "run_command");
        o.addProperty("command", command);
        return o;
    }

    JsonObject dialog(Page page) {
        JsonObject d = new JsonObject();
        d.addProperty("type", "minecraft:multi_action");
        d.add("title", text("CBosses Settings: " + page.title, "gold"));
        d.add("external_title", text("CBosses Settings", null));
        JsonArray body = new JsonArray();
        var s = plugin.service();
        JsonArray stats = new JsonArray();
        stats.add(text("Current boss statistics:\n", "gold"));
        stats.add(text(" • Bosses loaded: ", "gray")); stats.add(text(s.defs().size() + "\n", "yellow"));
        String alive = s.aliveName();
        stats.add(text(" • Fighting now: ", "gray")); stats.add(text((alive == null || alive.isEmpty() ? "none" : alive) + "\n", "yellow"));
        stats.add(text(" • Next weekly boss: ", "gray")); String up = s.upcomingName(), when = s.nextText();
        stats.add(text((up.isEmpty() ? "none scheduled" : up + (when.isEmpty() ? "" : " in " + when)) + "\n", "yellow"));
        stats.add(text(" • Players online: ", "gray")); stats.add(text(Bukkit.getOnlinePlayers().size() + "/" + Bukkit.getMaxPlayers(), "green"));
        JsonObject statLine = new JsonObject();
        statLine.addProperty("text", "");
        statLine.add("extra", stats);
        body.add(message(text("Change the options below, then press Save.", "white")));
        body.add(message(statLine));
        d.add("body", body);

        JsonArray inputs = new JsonArray();
        StringBuilder template = new StringBuilder("cbosses settings save ").append(page.id);
        for (int k = 0; k < page.settings.size(); k++) {
            Setting st = page.settings.get(k);
            String key = "s" + k, cur = value(st);
            JsonObject in = new JsonObject();
            in.addProperty("key", key);
            switch (st.kind) {
                case BOOL, CHOICE -> {
                    in.addProperty("type", "minecraft:single_option");
                    in.add("label", text(st.label, null));
                    in.addProperty("width", 300);
                    JsonArray opts = new JsonArray();
                    List<String> values = st.kind == Kind.BOOL ? List.of("true", "false") : st.options;
                    for (String o : values) {
                        JsonObject op = new JsonObject();
                        op.addProperty("id", o);
                        op.add("display", st.kind == Kind.BOOL ? text(o.equals("true") ? "On" : "Off", o.equals("true") ? "green" : "red") : text(nice(o), "yellow"));
                        if (o.equals(cur)) op.addProperty("initial", true);
                        opts.add(op);
                    }
                    in.add("options", opts);
                }
                case INT, DOUBLE -> {
                    in.addProperty("type", "minecraft:number_range");
                    in.add("label", text(st.label, null));
                    in.addProperty("width", 300);
                    in.addProperty("start", st.min);
                    in.addProperty("end", st.max);
                    in.addProperty("step", st.step);
                    double v;
                    try { v = Double.parseDouble(cur); } catch (NumberFormatException e) { v = st.min; }
                    in.addProperty("initial", Math.max(st.min, Math.min(st.max, v)));
                }
                case TEXT -> {
                    in.addProperty("type", "minecraft:text");
                    in.add("label", text(st.label, null));
                    in.addProperty("width", 300);
                    in.addProperty("initial", cur);
                    in.addProperty("max_length", 64);
                }
            }
            inputs.add(in);
            template.append(' ').append(key).append("=$(").append(key).append(')');
        }
        d.add("inputs", inputs);

        JsonArray actions = new JsonArray();
        JsonObject save = new JsonObject();
        save.addProperty("type", "dynamic/run_command");
        save.addProperty("template", template.toString());
        actions.add(button("Save", "green", save, 150));
        for (Page other : pages()) if (!other.id.equals(page.id)) actions.add(button(other.title, "aqua", run("cbosses settings " + other.id), 150));
        actions.add(button("Boss menu", "yellow", run("cbosses menu"), 150));
        d.add("actions", actions);
        d.addProperty("columns", 2);
        d.add("exit_action", button("Close", "gray", null, 150));
        d.addProperty("can_close_with_escape", true);
        d.addProperty("pause", false);
        return d;
    }

    private void openDialog(Player player, Page page) {
        String json = GSON.toJson(dialog(page));
        Sched.global(() -> {
            try {
                if (!Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "minecraft:dialog show " + player.getName() + " " + json))
                    Sched.entity(player, () -> openChest(player, page));
            } catch (RuntimeException e) {
                plugin.getLogger().warning("Settings dialog failed (" + e.getMessage() + "), using the chest menu instead.");
                Sched.entity(player, () -> openChest(player, page));
            }
        });
    }

    // ------------------------------------------------------------------------------------------ the chest menu (older servers)

    private static final class Holder implements InventoryHolder {
        final Page page;
        Inventory inv;
        Holder(Page page) { this.page = page; }
        @Override public @NotNull Inventory getInventory() { return inv; }
    }

    private void openChest(Player player, Page page) {
        Holder h = new Holder(page);
        Inventory inv = Bukkit.createInventory(h, 54, Text.mm("<dark_gray>CBosses Settings: " + page.title));
        h.inv = inv;
        for (int k = 0; k < page.settings.size() && k < 36; k++) {
            Setting s = page.settings.get(k);
            String v = value(s);
            ItemStack it = new ItemStack(s.kind == Kind.BOOL ? (v.equals("true") ? Material.LIME_DYE : Material.GRAY_DYE) : s.icon);
            var meta = it.getItemMeta();
            meta.displayName(Component.text(s.label, NamedTextColor.GOLD).decoration(TextDecoration.ITALIC, false));
            List<Component> lore = new ArrayList<>();
            lore.add(Component.text("Now: ", NamedTextColor.GRAY).append(Component.text(s.kind == Kind.BOOL ? (v.equals("true") ? "On" : "Off") : v, NamedTextColor.YELLOW)).decoration(TextDecoration.ITALIC, false));
            String hint = switch (s.kind) {
                case BOOL -> "Click to switch";
                case CHOICE -> "Click for the next choice";
                case INT, DOUBLE -> "Left +" + fmt(s.step) + "  Right -" + fmt(s.step) + "  Shift x10";
                case TEXT -> "Click to get the command to change it";
            };
            lore.add(Component.text(hint, NamedTextColor.DARK_GRAY).decoration(TextDecoration.ITALIC, false));
            lore.add(Component.text(s.path, NamedTextColor.DARK_GRAY).decoration(TextDecoration.ITALIC, false));
            meta.lore(lore);
            it.setItemMeta(meta);
            inv.setItem(k, it);
        }
        int slot = 45;
        for (Page p : pages()) {
            ItemStack it = new ItemStack(p.icon);
            var meta = it.getItemMeta();
            meta.displayName(Component.text(p.title, p.id.equals(page.id) ? NamedTextColor.GREEN : NamedTextColor.AQUA).decoration(TextDecoration.ITALIC, false));
            it.setItemMeta(meta);
            inv.setItem(slot++, it);
        }
        player.openInventory(inv);
    }

    @EventHandler
    public void onClick(InventoryClickEvent e) {
        if (!(e.getInventory().getHolder() instanceof Holder h)) return;
        e.setCancelled(true);
        if (!(e.getWhoClicked() instanceof Player p) || e.getClickedInventory() != e.getInventory()) return;
        if (!BossCommand.canControl(p)) { p.closeInventory(); return; }
        int slot = e.getRawSlot();
        if (slot >= 45) {
            int k = slot - 45;
            List<Page> all = pages();
            if (k < all.size()) openChest(p, all.get(k));
            return;
        }
        if (slot >= h.page.settings.size()) return;
        Setting s = h.page.settings.get(slot);
        String v = value(s);
        ClickType click = e.getClick();
        switch (s.kind) {
            case BOOL -> set(s, String.valueOf(!v.equals("true")));
            case CHOICE -> set(s, s.options.get((s.options.indexOf(v) + 1) % s.options.size()));
            case INT, DOUBLE -> {
                double step = s.step * (click.isShiftClick() ? 10 : 1) * (click.isRightClick() ? -1 : 1);
                set(s, String.valueOf(Double.parseDouble(v) + step));
            }
            case TEXT -> {
                p.closeInventory();
                p.sendMessage(Text.mm("<gray>Type <yellow><click:suggest_command:'/cbosses settings set " + s.path + " " + v + "'>/cbosses settings set " + s.path + " <value></click> <gray>(click to fill it in)"));
                return;
            }
        }
        plugin.saveConfig();
        plugin.reloadAll();
        openChest(p, h.page);
    }

    @EventHandler
    public void onDrag(InventoryDragEvent e) {
        if (e.getInventory().getHolder() instanceof Holder) e.setCancelled(true);
    }
}
