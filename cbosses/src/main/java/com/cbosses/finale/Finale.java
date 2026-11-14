package com.cbosses.finale;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.api.BossDefeatEvent;
import com.cbosses.fight.BossDef;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import org.bukkit.Bukkit;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * The finale: once every legend in finale.after has been beaten (in any order, any fight but a test),
 * the finale boss wakes at its arena after a warning. Progress is kept in finale.yml and starts over
 * after the finale is beaten.
 */
public final class Finale implements Listener {
    private final CBossesPlugin plugin;
    private final File file;
    private final Set<String> beaten = new LinkedHashSet<>();
    private volatile boolean pending;

    public Finale(CBossesPlugin plugin) {
        this.plugin = plugin;
        this.file = new File(plugin.getDataFolder(), "finale.yml");
        YamlConfiguration y = YamlConfiguration.loadConfiguration(file);
        beaten.addAll(y.getStringList("beaten"));
    }

    private boolean on() { return plugin.getConfig().getBoolean("finale.enabled", true); }
    public String boss() { return plugin.getConfig().getString("finale.boss", "the_unmaker"); }
    public List<String> after() {
        List<String> l = new ArrayList<>(plugin.getConfig().getStringList("finale.after"));
        // bosses retired in 1.3.2 no longer stand in the way on servers with an older config
        l.removeAll(List.of("ender_wyrm", "gale_sovereign", "hollow_king"));
        return l.isEmpty() ? List.of("withered_tyrant", "the_listener") : l;
    }

    /** The legends still standing between the server and the finale. */
    public List<String> left() {
        List<String> out = new ArrayList<>();
        for (String id : after()) if (!beaten.contains(id)) out.add(id);
        return out;
    }

    @EventHandler
    public void onDefeat(BossDefeatEvent e) {
        if (!on() || e.isTest()) return;
        String id = e.getBoss();
        if (id.equals(boss())) {
            synchronized (beaten) { beaten.clear(); save(); }
            return;
        }
        if (!after().contains(id)) return;
        boolean ready;
        synchronized (beaten) {
            if (!beaten.add(id)) return;
            save();
            ready = left().isEmpty();
        }
        BossDef def = plugin.service().def(id);
        String name = def == null ? id : def.name();
        if (!ready) {
            broadcast(T.t("finale.progress", "<dark_purple>✦ <boss> <gray>has fallen. <white><left></white> <gray>legend(s) still stand before <light_purple>something wakes</light_purple>.",
                    "boss", name, "left", left().size()));
            return;
        }
        wake(false);
    }

    /** Warns everyone and wakes the finale boss after finale.delay-seconds. */
    public boolean wake(boolean forced) {
        if (pending) return false;
        BossDef def = plugin.service().def(boss());
        if (def == null) { plugin.getLogger().warning("finale.boss " + boss() + " is not in bosses.yml"); return false; }
        pending = true;
        int delay = Math.max(5, plugin.getConfig().getInt("finale.delay-seconds", 60));
        broadcast(T.t("finale.warning", "<dark_gray><st>                                        </st>\n<light_purple><bold>✦ THE LEGENDS HAVE FALLEN ✦</bold></light_purple>\n<gray>Something older than all of them is waking...\n<boss> <gray>arrives in <white><seconds></white> seconds<where>.\n<dark_gray><st>                                        </st>",
                "boss", def.name(), "seconds", delay, "where", where()));
        Sched.global(() -> { for (Player p : Bukkit.getOnlinePlayers()) Sched.entity(p, () -> p.playSound(p.getLocation(), org.bukkit.Sound.ENTITY_WARDEN_EMERGE, 0.6f, 0.5f)); });
        Bukkit.getGlobalRegionScheduler().runDelayed(plugin, t -> {
            pending = false;
            var arena = plugin.service().arena(plugin.getConfig().getString("finale.arena", plugin.getConfig().getString("schedule.arena", "main")), false);
            if (arena == null) { plugin.getLogger().warning("The finale has no arena: set one with /cbosses arena setspawn " + plugin.getConfig().getString("finale.arena", "main")); return; }
            if (!plugin.service().spawn(def, arena, null, false, null)) plugin.getLogger().warning("The finale boss could not wake (another boss alive there, or spawning is blocked).");
        }, delay * 20L);
        return true;
    }

    private String where() {
        var arena = plugin.service().arena(plugin.getConfig().getString("finale.arena", plugin.getConfig().getString("schedule.arena", "main")), false);
        var s = arena == null ? null : arena.spawn();
        return s == null ? "" : T.t("finale.where", " <gray>at <white><x> <y> <z></white> in <white><world></white>", "x", s.getBlockX(), "y", s.getBlockY(), "z", s.getBlockZ(), "world", s.getWorld().getName());
    }

    public void reset() { synchronized (beaten) { beaten.clear(); save(); } }

    public void info(org.bukkit.command.CommandSender to) {
        BossDef def = plugin.service().def(boss());
        List<String> names = new ArrayList<>();
        for (String id : after()) {
            BossDef d = plugin.service().def(id);
            names.add((beaten.contains(id) ? "<green>✔ " : "<red>✘ ") + (d == null ? id : d.name()));
        }
        plugin.send(to, T.t("finale.info", "<light_purple>Finale</light_purple> <gray>(<state>): <boss> <gray>wakes after <legends>",
                "state", on() ? "on" : "off", "boss", def == null ? boss() : def.name(), "legends", String.join("<gray>, ", names)));
    }

    private void save() {
        YamlConfiguration y = new YamlConfiguration();
        y.set("beaten", new ArrayList<>(beaten));
        try { com.cbosses.util.SafeFiles.write(file, y.saveToString()); } catch (IOException e) { plugin.getLogger().warning("Could not save finale.yml: " + e.getMessage()); }
    }

    private void broadcast(String mm) { Sched.global(() -> Bukkit.broadcast(Text.mm(mm))); }

    static String lower(String s) { return s.toLowerCase(Locale.ROOT); }
}
