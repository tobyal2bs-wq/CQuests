package com.cbosses.mini;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.arena.Arena;
import com.cbosses.fight.BossDef;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerQuitEvent;

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Mini bosses: every minis.every-minutes a round of small bosses (kind: mini) wakes. Where they wake is up
 * to the ops: at fixed spots (/cbosses minis add), at random places near players, or mixed. Spots are kept
 * in minis.yml and shown to ops as barrier markers. Everything runs off one global timer; nothing is held
 * per player except the set of ops who switched the markers on, which is cleared when they leave.
 */
public final class MiniBosses implements Listener {
    public static final List<String> MODES = List.of("fixed", "random", "mixed");

    /** A place a mini boss may wake. bosses empty means any mini boss. */
    public static final class Spot {
        public final String id;
        public volatile String world;
        public volatile double x, y, z;
        public volatile int radius;
        public volatile boolean enabled = true;
        public final List<String> bosses = new ArrayList<>();
        Spot(String id) { this.id = id; }
        public Location location() {
            World w = Bukkit.getWorld(world);
            return w == null ? null : new Location(w, x, y, z);
        }
    }

    private final CBossesPlugin plugin;
    private final Map<String, Spot> spots = new LinkedHashMap<>();
    private final Set<UUID> showing = ConcurrentHashMap.newKeySet();
    private final AtomicInteger counter = new AtomicInteger();
    private ScheduledTask timer, markers;
    private volatile long nextAt;
    private File file;

    public MiniBosses(CBossesPlugin plugin) { this.plugin = plugin; }

    FileConfiguration cfg() { return plugin.getConfig(); }
    public boolean enabled() { return cfg().getBoolean("minis.enabled", true); }
    public String mode() { String m = cfg().getString("minis.mode", "mixed").toLowerCase(Locale.ROOT); return MODES.contains(m) ? m : "mixed"; }
    public int everyMinutes() { return Math.max(1, cfg().getInt("minis.every-minutes", 60)); }
    public int maxAlive() { return Math.max(1, cfg().getInt("minis.max-alive", 3)); }
    public int perRound() { return Math.max(1, cfg().getInt("minis.per-round", 1)); }
    public long nextAt() { return nextAt; }
    public synchronized List<Spot> spots() { return new ArrayList<>(spots.values()); }
    public boolean showing(Player p) { return showing.contains(p.getUniqueId()); }

    // ------------------------------------------------------------------ lifecycle

    public void start() {
        stop();
        load();
        if (nextAt <= System.currentTimeMillis()) nextAt = System.currentTimeMillis() + everyMinutes() * 60_000L;
        timer = Sched.globalTimer(t -> tick(), 200, 200);
        markers = Sched.globalTimer(t -> drawMarkers(), 20, 10);
    }

    public void stop() {
        if (timer != null) { timer.cancel(); timer = null; }
        if (markers != null) { markers.cancel(); markers = null; }
    }

    private void tick() {
        if (!enabled() || Bukkit.getOnlinePlayers().isEmpty()) return;
        long now = System.currentTimeMillis();
        int warn = Math.max(0, cfg().getInt("minis.warn-seconds", 60));
        if (warn > 0 && now < nextAt && nextAt - now <= warn * 1000L && nextAt - now > warn * 1000L - 10_000L && cfg().getBoolean("minis.announce", true))
            plugin.service().broadcast(T.t("mini.warning", "<yellow><bold>✦ MINI BOSS</bold></yellow> <gray>Something small and angry wakes in <white><seconds>s</white>.", "seconds", warn));
        if (now < nextAt) return;
        nextAt = now + everyMinutes() * 60_000L;
        save();
        spawnRound(null);
    }

    /** Wakes perRound() minis now (or one of a given boss). Returns how many were started. */
    public int spawnRound(String onlyBoss) {
        int started = 0;
        for (int i = 0; i < perRound(); i++) {
            if (alive() >= maxAlive()) break;
            if (spawnOne(onlyBoss)) started++;
        }
        return started;
    }

    public int alive() {
        int n = 0;
        for (String key : plugin.service().fights().keySet()) if (key.startsWith("mini-")) n++;
        return n;
    }

    public List<BossDef> minis() {
        List<String> allowed = cfg().getStringList("minis.bosses");
        List<BossDef> out = new ArrayList<>();
        for (BossDef d : plugin.service().defs().values())
            if (d.mini() && (allowed.isEmpty() || allowed.contains(d.id()))) out.add(d);
        return out;
    }

    private boolean spawnOne(String onlyBoss) {
        List<Spot> fixed = new ArrayList<>();
        for (Spot s : spots()) if (s.enabled && s.location() != null && !busy(s)) fixed.add(s);
        String mode = mode();
        boolean useFixed = switch (mode) {
            case "fixed" -> true;
            case "random" -> false;
            default -> !fixed.isEmpty() && ThreadLocalRandom.current().nextBoolean();
        };
        if (useFixed && fixed.isEmpty()) { if (mode.equals("fixed")) return false; useFixed = false; }
        if (useFixed) {
            Spot s = fixed.get(ThreadLocalRandom.current().nextInt(fixed.size()));
            BossDef def = pick(onlyBoss, s.bosses);
            if (def == null) return false;
            Arena a = new Arena("mini-" + s.id + "-" + counter.incrementAndGet(), Math.max(8, s.radius));
            a.spawn(s.location());
            return start(def, a);
        }
        BossDef def = pick(onlyBoss, List.of());
        if (def == null) return false;
        List<Player> players = new ArrayList<>();
        List<String> worlds = cfg().getStringList("minis.random-worlds");
        for (Player p : Bukkit.getOnlinePlayers())
            if (worlds.isEmpty() || worlds.contains(p.getWorld().getName())) players.add(p);
        if (players.isEmpty()) return false;
        Player near = players.get(ThreadLocalRandom.current().nextInt(players.size()));
        int min = Math.max(8, cfg().getInt("minis.random-min-distance", 30)), max = Math.max(min + 1, cfg().getInt("minis.random-max-distance", 80));
        double ang = ThreadLocalRandom.current().nextDouble(Math.PI * 2), dist = ThreadLocalRandom.current().nextDouble(min, max);
        Location rough = near.getLocation().clone().add(Math.cos(ang) * dist, 0, Math.sin(ang) * dist);
        int radius = Math.max(8, cfg().getInt("minis.radius", 24));
        Sched.at(rough, () -> {
            World w = rough.getWorld();
            int y = w.getHighestBlockYAt(rough.getBlockX(), rough.getBlockZ());
            Material ground = w.getBlockAt(rough.getBlockX(), y, rough.getBlockZ()).getType();
            if (ground == Material.WATER || ground == Material.LAVA || y <= w.getMinHeight()) return;
            Location at = new Location(w, rough.getBlockX() + 0.5, y + 1, rough.getBlockZ() + 0.5);
            Arena a = new Arena("mini-random-" + counter.incrementAndGet(), radius);
            a.spawn(at);
            Sched.global(() -> start(def, a));
        });
        return true;
    }

    private boolean busy(Spot s) {
        for (String key : plugin.service().fights().keySet()) if (key.startsWith("mini-" + s.id + "-")) return true;
        return false;
    }

    private BossDef pick(String onlyBoss, List<String> spotBosses) {
        if (onlyBoss != null) { BossDef d = plugin.service().def(onlyBoss); return d; }
        List<BossDef> pool = new ArrayList<>();
        for (BossDef d : minis()) if (spotBosses.isEmpty() || spotBosses.contains(d.id())) pool.add(d);
        return pool.isEmpty() ? null : pool.get(ThreadLocalRandom.current().nextInt(pool.size()));
    }

    private boolean start(BossDef def, Arena a) {
        boolean ok = plugin.service().spawn(def, a, null, false, null);
        if (ok && cfg().getBoolean("minis.announce", true)) {
            Location l = a.spawn();
            plugin.service().broadcast(T.t("mini.awake", "<yellow><bold>✦ MINI BOSS</bold></yellow> <boss> <gray>woke at <white><x>, <z></white> (<world>).",
                    "boss", def.name(), "x", l.getBlockX(), "z", l.getBlockZ(), "world", l.getWorld().getName()));
        }
        return ok;
    }

    // ------------------------------------------------------------------ spots

    public synchronized Spot add(Location at, int radius) {
        int n = spots.size() + 1;
        while (spots.containsKey("spot" + n)) n++;
        Spot s = new Spot("spot" + n);
        s.world = at.getWorld().getName();
        s.x = at.getBlockX() + 0.5; s.y = at.getBlockY(); s.z = at.getBlockZ() + 0.5;
        s.radius = radius;
        spots.put(s.id, s);
        save();
        return s;
    }

    public synchronized boolean remove(String id) {
        boolean ok = spots.remove(id) != null;
        if (ok) save();
        return ok;
    }

    public synchronized Spot nearest(Location at, double within) {
        Spot best = null;
        double bd = within * within;
        for (Spot s : spots.values()) {
            if (!s.world.equals(at.getWorld().getName())) continue;
            double d = (s.x - at.getX()) * (s.x - at.getX()) + (s.y - at.getY()) * (s.y - at.getY()) + (s.z - at.getZ()) * (s.z - at.getZ());
            if (d < bd) { bd = d; best = s; }
        }
        return best;
    }

    public synchronized Spot spot(String id) { return spots.get(id); }

    public void toggleMarkers(Player p) {
        if (!showing.remove(p.getUniqueId())) showing.add(p.getUniqueId());
    }

    @EventHandler
    public void quit(PlayerQuitEvent event) { showing.remove(event.getPlayer().getUniqueId()); }

    /** Barrier markers and a light beam over each spot, only for ops who turned them on (packets only). */
    private void drawMarkers() {
        if (showing.isEmpty()) return;
        List<Spot> all = spots();
        var barrier = Material.BARRIER.createBlockData();
        for (UUID id : showing) {
            Player p = Bukkit.getPlayer(id);
            if (p == null) { showing.remove(id); continue; }
            Sched.entity(p, () -> {
                Location me = p.getLocation();
                for (Spot s : all) {
                    if (!s.world.equals(me.getWorld().getName())) continue;
                    double dx = s.x - me.getX(), dz = s.z - me.getZ();
                    if (dx * dx + dz * dz > 160 * 160) continue;
                    Location l = new Location(me.getWorld(), s.x, s.y + 0.5, s.z);
                    p.spawnParticle(Particle.BLOCK_MARKER, l, 1, 0, 0, 0, 0, barrier);
                    p.spawnParticle(Particle.END_ROD, l.clone().add(0, 1.5, 0), 4, 0.05, 1.2, 0.05, 0);
                    // the border ring, a few points each pass so it stays cheap
                    double phase = (System.currentTimeMillis() / 500L % 12) * Math.PI / 6;
                    for (int k = 0; k < 12; k++) {
                        double a = phase + k * Math.PI / 6;
                        p.spawnParticle(s.enabled ? Particle.END_ROD : Particle.SMOKE,
                                l.getX() + Math.cos(a) * s.radius, l.getY(), l.getZ() + Math.sin(a) * s.radius, 1, 0, 0, 0, 0);
                    }
                }
            });
        }
    }

    // ------------------------------------------------------------------ storage

    private synchronized void load() {
        file = new File(plugin.getDataFolder(), "minis.yml");
        spots.clear();
        YamlConfiguration y = YamlConfiguration.loadConfiguration(file);
        nextAt = y.getLong("next-at", 0);
        ConfigurationSection root = y.getConfigurationSection("spots");
        if (root == null) return;
        for (String id : root.getKeys(false)) {
            ConfigurationSection c = root.getConfigurationSection(id);
            if (c == null) continue;
            Spot s = new Spot(id);
            s.world = c.getString("world", "world");
            s.x = c.getDouble("x"); s.y = c.getDouble("y"); s.z = c.getDouble("z");
            s.radius = c.getInt("radius", 24);
            s.enabled = c.getBoolean("enabled", true);
            s.bosses.addAll(c.getStringList("bosses"));
            spots.put(id, s);
        }
    }

    public synchronized void save() {
        if (file == null) return;
        YamlConfiguration y = new YamlConfiguration();
        y.set("next-at", nextAt);
        for (Spot s : spots.values()) {
            String k = "spots." + s.id + ".";
            y.set(k + "world", s.world); y.set(k + "x", s.x); y.set(k + "y", s.y); y.set(k + "z", s.z);
            y.set(k + "radius", s.radius); y.set(k + "enabled", s.enabled); y.set(k + "bosses", new ArrayList<>(s.bosses));
        }
        String text = y.saveToString();
        File f = file;
        Sched.async(() -> {
            try { com.cbosses.util.SafeFiles.write(f, text); }
            catch (Exception e) { plugin.getLogger().warning("Could not save minis.yml: " + e.getMessage()); }
        });
    }

    public void setNext(long at) { nextAt = at; save(); }

    public String nextText() {
        long s = Math.max(0, (nextAt - System.currentTimeMillis()) / 1000);
        return s >= 3600 ? (s / 3600) + "h " + (s % 3600 / 60) + "m" : (s / 60) + "m " + (s % 60) + "s";
    }

    public void set(String path, Object value) {
        cfg().set("minis." + path, value);
        plugin.saveConfig();
    }

    public void info(CommandSender to) {
        plugin.send(to, T.t("mini.info", "<yellow>Mini bosses <white><state></white> <gray>· mode <white><mode></white> · every <white><every>m</white> · next in <white><next></white> · alive <white><alive>/<max></white> · spots <white><spots></white> · minis <white><count></white>",
                "state", enabled() ? "on" : "off", "mode", mode(), "every", everyMinutes(), "next", nextText(), "alive", alive(), "max", maxAlive(),
                "spots", spots().size(), "count", minis().size()));
        for (Spot s : spots())
            to.sendMessage(Text.mm(T.t("mini.spot-line", " <gray>• <white><id></white> <world> <x> <y> <z> r<radius><off><bosses>", "id", s.id, "world", s.world,
                    "x", (int) s.x, "y", (int) s.y, "z", (int) s.z, "radius", s.radius, "off", s.enabled ? "" : " <red>(off)",
                    "bosses", s.bosses.isEmpty() ? "" : " <dark_gray>only " + String.join(", ", s.bosses))));
    }
}
