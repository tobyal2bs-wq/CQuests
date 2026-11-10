package com.cbosses.chapter;

import com.cbosses.T;

import com.cbosses.CBossesPlugin;
import com.cbosses.fight.BossDef;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.Sound;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerAdvancementDoneEvent;
import org.bukkit.event.player.PlayerJoinEvent;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Chapter bosses: when a player finishes a CQuests chapter (CQuests gives the advancement
 * cquests:chapter_N), the boss for that chapter comes for them after a short countdown. Each player
 * meets each chapter boss once; if they lose they can try again with /cbosses chapter retry.
 * Works without CQuests too: /cbosses chapter <player> <n> sends one by hand.
 */
public final class ChapterBosses implements Listener {
    private final CBossesPlugin plugin;
    private final File file;
    /** player -> chapters whose boss they have beaten. */
    private final Map<UUID, Set<Integer>> beaten = new ConcurrentHashMap<>();
    /** player -> the chapter boss they last met but did not beat (for retry). */
    private final Map<UUID, Integer> pending = new ConcurrentHashMap<>();
    private final Set<UUID> counting = ConcurrentHashMap.newKeySet();

    public ChapterBosses(CBossesPlugin plugin) {
        this.plugin = plugin;
        file = new File(plugin.getDataFolder(), "chapters.yml");
        load();
    }

    private boolean on() { return plugin.getConfig().getBoolean("chapter-bosses.enabled", true); }

    private void load() {
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        beaten.clear(); pending.clear();
        var b = yaml.getConfigurationSection("beaten");
        if (b != null) for (String id : b.getKeys(false)) try { beaten.put(UUID.fromString(id), new HashSet<>(yaml.getIntegerList("beaten." + id))); } catch (IllegalArgumentException ignored) { }
        var p = yaml.getConfigurationSection("pending");
        if (p != null) for (String id : p.getKeys(false)) try { pending.put(UUID.fromString(id), yaml.getInt("pending." + id)); } catch (IllegalArgumentException ignored) { }
    }

    private synchronized void save() {
        YamlConfiguration yaml = new YamlConfiguration();
        beaten.forEach((id, set) -> yaml.set("beaten." + id, List.copyOf(set)));
        pending.forEach((id, n) -> yaml.set("pending." + id, n));
        String text = yaml.saveToString();
        Sched.async(() -> {
            synchronized (file) {
                try { com.cbosses.util.SafeFiles.write(file, text); }
                catch (IOException e) { plugin.getLogger().warning("Could not save chapters.yml: " + e.getMessage()); }
            }
        });
    }

    /** The boss for a chapter: the one with "chapter: N" in bosses.yml, or the config override. */
    public BossDef bossFor(int chapter) {
        String override = plugin.getConfig().getString("chapter-bosses.bosses." + chapter, "");
        if (override != null && !override.isBlank()) {
            if (override.equalsIgnoreCase("none")) return null;
            BossDef d = plugin.service().def(override);
            if (d != null) return d;
        }
        for (BossDef d : plugin.service().defs().values()) if (d.chapterBoss() && d.chapter() == chapter) return d;
        return null;
    }

    public boolean beat(UUID player, int chapter) { return beaten.getOrDefault(player, Set.of()).contains(chapter); }

    @EventHandler(priority = EventPriority.MONITOR)
    public void advancement(PlayerAdvancementDoneEvent event) {
        var key = event.getAdvancement().getKey();
        if (!key.getNamespace().equals("cquests") || !key.getKey().startsWith("chapter_")) return;
        int chapter;
        try { chapter = Integer.parseInt(key.getKey().substring("chapter_".length())); } catch (NumberFormatException e) { return; }
        if (!on() || !plugin.getConfig().getBoolean("chapter-bosses.from-cquests", true)) return;
        trigger(event.getPlayer(), chapter, false);
    }

    @EventHandler
    public void join(PlayerJoinEvent event) {
        Integer chapter = pending.get(event.getPlayer().getUniqueId());
        if (chapter == null || !on()) return;
        BossDef def = bossFor(chapter);
        if (def == null) return;
        Player p = event.getPlayer();
        Sched.entityLater(p, 100, () -> plugin.send(p, plugin.msg("chapter-boss-waiting", T.t("chapter.is-still-waiting-for-you", "<gold><boss> <gray>is still waiting for you. <yellow>/cbosses chapter retry</yellow> when you are ready.")).replace("<boss>", def.name())));
    }

    /** Starts the countdown for a player's chapter boss. force skips the "already beaten" check. */
    public boolean trigger(Player player, int chapter, boolean force) {
        BossDef def = bossFor(chapter);
        if (def == null) return false;
        UUID id = player.getUniqueId();
        if (!force && beat(id, chapter)) return false;
        if (!counting.add(id)) return false;
        if (plugin.getConfig().getStringList("fight.disabled-worlds").contains(player.getWorld().getName())) {
            counting.remove(id);
            pending.put(id, chapter); save();
            plugin.send(player, T.t("chapter.a-chapter-boss-wants-to", "<gray>A chapter boss wants to fight you, but bosses are off in this world. <yellow>/cbosses chapter retry</yellow> somewhere else."));
            return false;
        }
        pending.put(id, chapter); save();
        int seconds = Math.max(3, plugin.getConfig().getInt("chapter-bosses.countdown-seconds", 10));
        boolean big = plugin.getConfig().getIntegerList("chapter-bosses.big-chapters").contains(chapter);
        String label = big ? T.t("chapter.a-great-evil-stirs", "<dark_red><bold>A GREAT EVIL STIRS") : T.t("chapter.chapter-boss", "<gold><bold>CHAPTER BOSS");
        plugin.send(player, plugin.msg("chapter-boss-warning", T.t("chapter.is-coming-for-you-in", "<gold>⚔ <boss> <gray>is coming for you in <white><seconds></white> seconds. Get ready!"))
                .replace("<boss>", def.name()).replace("<seconds>", Integer.toString(seconds)));
        int[] left = {seconds};
        player.getScheduler().runAtFixedRate(plugin, t -> {
            if (!player.isOnline()) { counting.remove(id); t.cancel(); return; }
            if (left[0] <= 0) {
                t.cancel();
                counting.remove(id);
                if (!plugin.service().chapterFight(player, def, plugin.getConfig().getInt("chapter-bosses.arena-radius", 28)))
                    plugin.send(player, T.t("chapter.the-chapter-boss-could-not", "<gray>The chapter boss could not appear here. <yellow>/cbosses chapter retry</yellow> somewhere open."));
                return;
            }
            if (left[0] <= 5 || left[0] == seconds) {
                player.showTitle(Title.title(Text.mm(label), Text.mm(T.t("chapter.in", "<boss> <gray>in <white><left>", "boss", def.name(), "left", left[0])),
                        Title.Times.times(Duration.ZERO, Duration.ofMillis(1100), Duration.ofMillis(200))));
                player.playSound(player.getLocation(), Sound.BLOCK_NOTE_BLOCK_BASEDRUM, 1f, left[0] <= 3 ? 0.6f : 0.9f);
                if (big) player.playSound(player.getLocation(), Sound.ENTITY_WARDEN_HEARTBEAT, 1f, 1f);
            }
            left[0]--;
        }, null, 20, 20);
        return true;
    }

    public void won(UUID player, BossDef def, List<Map.Entry<UUID, Double>> ranked) {
        // progress is kept by chapter number, so swapping which boss guards a chapter never loses it
        int chapter = pending.getOrDefault(player, def.chapter());
        beaten.computeIfAbsent(player, k -> ConcurrentHashMap.newKeySet()).add(chapter);
        pending.remove(player);
        save();
        Player p = Bukkit.getPlayer(player);
        String name = p != null ? p.getName() : Bukkit.getOfflinePlayer(player).getName();
        if (name == null) return;
        plugin.service().pay(player, name, 1, def.rewards(), def);
        // helpers (if allowed) get the base reward
        int place = 1;
        for (var e : ranked) {
            if (e.getKey().equals(player)) continue;
            place++;
            Player helper = Bukkit.getPlayer(e.getKey());
            if (helper != null) plugin.service().pay(e.getKey(), helper.getName(), Math.max(4, place), def.rewards(), def);
        }
        if (plugin.getConfig().getBoolean("chapter-bosses.announce", true))
            Sched.global(() -> Bukkit.broadcast(Text.mm(plugin.msg("chapter-boss-beaten", T.t("chapter.defeated-the-chapter-boss", "<gold>⚔ <white><player></white> <gray>defeated the chapter boss <boss><gray>!"))
                    .replace("<player>", Text.escape(name)).replace("<boss>", def.name()))));
    }

    public void failed(UUID player, BossDef def, String reason) {
        if (!reason.equals("shutdown") && !reason.equals("stopped") && !pending.containsKey(player) && def.chapter() > 0) { pending.put(player, def.chapter()); save(); }
    }

    public boolean retry(Player player) {
        Integer chapter = pending.get(player.getUniqueId());
        if (chapter == null) return false;
        return trigger(player, chapter, true);
    }

    public void reset(UUID player) { beaten.remove(player); pending.remove(player); save(); }

    /** Which boss guards each chapter (1 to 10 and any chapter set in the config). */
    public void list(org.bukkit.command.CommandSender to) {
        java.util.TreeSet<Integer> chapters = new java.util.TreeSet<>();
        for (BossDef d : plugin.service().defs().values()) if (d.chapterBoss()) chapters.add(d.chapter());
        var sec = plugin.getConfig().getConfigurationSection("chapter-bosses.bosses");
        if (sec != null) for (String k : sec.getKeys(false)) try { chapters.add(Integer.parseInt(k)); } catch (NumberFormatException ignored) { }
        plugin.send(to, T.t("chapter.list-head", "<gold>Chapter bosses <gray>(swap with /cbosses chapter swap <a> <b>):"));
        for (int c : chapters) {
            BossDef d = bossFor(c);
            String set = plugin.getConfig().getString("chapter-bosses.bosses." + c, "");
            plugin.send(to, T.t("chapter.list-line", "<gray>  <white><n></white>: <boss> <dark_gray><how>", "n", c,
                    "boss", d == null ? "<red>none" : d.name() + " <dark_gray>(" + d.id() + ")", "how", set == null || set.isBlank() ? "" : "set in config"));
        }
    }

    /** Puts a boss on a chapter ("default" goes back to bosses.yml). Player progress is by chapter, so nothing is lost. */
    public boolean set(int chapter, String boss) {
        if (!boss.equalsIgnoreCase("default") && !boss.equalsIgnoreCase("none") && plugin.service().def(boss) == null) return false;
        plugin.getConfig().set("chapter-bosses.bosses." + chapter, boss.equalsIgnoreCase("default") ? null : boss);
        plugin.saveConfig();
        return true;
    }

    /** Swaps the bosses of two chapters. */
    public boolean swap(int a, int b) {
        BossDef da = bossFor(a), db = bossFor(b);
        if (da == null || db == null) return false;
        plugin.getConfig().set("chapter-bosses.bosses." + a, db.id());
        plugin.getConfig().set("chapter-bosses.bosses." + b, da.id());
        plugin.saveConfig();
        return true;
    }
}
