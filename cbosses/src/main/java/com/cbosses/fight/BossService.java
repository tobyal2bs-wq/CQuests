package com.cbosses.fight;

import com.cbosses.T;

import com.cbosses.CBossesPlugin;
import com.cbosses.api.BossDefeatEvent;
import com.cbosses.api.BossSpawnEvent;
import com.cbosses.arena.Arena;
import com.cbosses.hook.WorldGuardHook;
import com.cbosses.model.BossModel;
import com.cbosses.model.ModelRig;
import com.cbosses.util.Sched;
import com.cbosses.util.Text;
import io.papermc.paper.entity.TeleportFlag;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import net.kyori.adventure.bossbar.BossBar;
import net.kyori.adventure.title.Title;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.Particle;
import org.bukkit.Registry;
import org.bukkit.Sound;
import org.bukkit.attribute.Attribute;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Ageable;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EvokerFangs;
import org.bukkit.entity.Hoglin;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Mob;
import org.bukkit.entity.PiglinAbstract;
import org.bukkit.entity.Player;
import org.bukkit.entity.Projectile;
import org.bukkit.entity.Rabbit;
import org.bukkit.entity.Slime;
import org.bukkit.entity.Vex;
import org.bukkit.entity.Wolf;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.block.BlockIgniteEvent;
import org.bukkit.event.block.EntityBlockFormEvent;
import org.bukkit.event.entity.CreatureSpawnEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntityPortalEvent;
import org.bukkit.event.entity.EntitySpawnEvent;
import org.bukkit.event.entity.EntityTargetLivingEntityEvent;
import org.bukkit.event.entity.EntityTransformEvent;
import org.bukkit.event.entity.ExplosionPrimeEvent;
import org.bukkit.event.entity.ProjectileLaunchEvent;
import org.bukkit.event.entity.SlimeSplitEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerTeleportEvent;
import org.bukkit.inventory.EntityEquipment;
import org.bukkit.inventory.EquipmentSlot;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.LeatherArmorMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.potion.PotionEffect;
import org.bukkit.potion.PotionEffectType;
import org.bukkit.util.Vector;

import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;

/**
 * Every boss fight: the weekly world boss at an arena an op sets up, seasonal bosses, the chapter bosses
 * players fight after a CQuests chapter, and tests. A boss only ever attacks players, never breaks, burns
 * or changes blocks, drops nothing, is never saved into the world and is pulled back whenever it reaches
 * its border. Every fight runs on the boss's own region thread (Folia safe).
 */
public final class BossService implements Listener {

    private final CBossesPlugin plugin;
    private final NamespacedKey kindKey, fightKey, wandKey;
    private final File arenasFile;
    private volatile Map<String, BossDef> defs = Map.of();
    private volatile Map<String, ModelRig.Model> models = Map.of();
    private final Map<String, Arena> arenas = new ConcurrentHashMap<>();
    private final Map<String, Fight> fights = new ConcurrentHashMap<>();
    private final Map<UUID, Fight> byEntity = new ConcurrentHashMap<>();
    private volatile String lastRun = "", lastWarn = "";
    private volatile boolean scheduleOn = true;
    private ScheduledTask timer;
    final Abilities abilities;
    final Cinematics cinema;

    /** Private circles made in spawn(), handed to the fight once it exists. */
    private final Map<String, String> pendingZone = new ConcurrentHashMap<>();

    public BossService(CBossesPlugin plugin) {
        this.plugin = plugin;
        kindKey = new NamespacedKey(plugin, "boss");
        Privacy.init(plugin);
        fightKey = new NamespacedKey(plugin, "fight");
        wandKey = new NamespacedKey(plugin, "wand");
        arenasFile = new File(plugin.getDataFolder(), "arenas.yml");
        abilities = new Abilities(this);
        cinema = new Cinematics(plugin, this);
        reload();
    }

    // ------------------------------------------------------------------ setup

    /** Copies the bundled name (or title) over the server's when the server still has one the boss used to ship with. */
    static boolean follow(YamlConfiguration yaml, String at, org.bukkit.configuration.ConfigurationSection sec, String key, String previous) {
        String now = yaml.getString(at + "." + key), next = sec.getString(key);
        if (now == null || next == null || now.equals(next) || !sec.getStringList(previous).contains(now)) return false;
        yaml.set(at + "." + key, next);
        yaml.set(at + "." + previous, sec.getStringList(previous));
        return true;
    }

    /** Bosses added in a new version are copied into an older bosses.yml; existing ones are left alone. */
    private void addNewBosses(File file, YamlConfiguration yaml) {
        try (var in = plugin.getResource("bosses.yml")) {
            if (in == null || !file.exists()) return;
            YamlConfiguration bundled = YamlConfiguration.loadConfiguration(new InputStreamReader(in, StandardCharsets.UTF_8));
            var from = bundled.getConfigurationSection("bosses");
            if (from == null) return;
            List<String> added = new ArrayList<>(), updated = new ArrayList<>(), renamed = new ArrayList<>();
            for (String id : from.getKeys(false)) {
                var sec = from.getConfigurationSection(id);
                if (sec == null) continue;
                String at = "bosses." + id;
                if (yaml.contains(at)) {
                    // a renamed boss: a name or title nobody edited follows the new one; an admin's own name stays
                    if (follow(yaml, at, sec, "name", "previous-names") | follow(yaml, at, sec, "title", "previous-titles")) renamed.add(id);
                    // a redesigned boss: take the new entry, keep the server's rewards and on/off switch
                    if (sec.getInt("revision", 0) <= yaml.getInt(at + ".revision", 0)) continue;
                    Object rewards = yaml.get(at + ".rewards");
                    boolean enabled = yaml.getBoolean(at + ".enabled", true);
                    yaml.set(at, null);
                    for (String k : sec.getKeys(true)) if (!sec.isConfigurationSection(k)) yaml.set(at + "." + k, sec.get(k));
                    if (rewards instanceof org.bukkit.configuration.ConfigurationSection r)
                        for (String k : r.getKeys(true)) if (!r.isConfigurationSection(k)) yaml.set(at + ".rewards." + k, r.get(k));
                    if (!enabled) yaml.set(at + ".enabled", false);
                    updated.add(id);
                    continue;
                }
                for (String k : sec.getKeys(true)) if (!sec.isConfigurationSection(k)) yaml.set(at + "." + k, sec.get(k));
                added.add(id);
            }
            List<String> removed = new ArrayList<>();
            for (String id : bundled.getStringList("removed"))
                if (yaml.contains("bosses." + id)) { yaml.set("bosses." + id, null); removed.add(id); }
            yaml.set("removed", bundled.getStringList("removed"));
            if (!removed.isEmpty()) plugin.getLogger().info("Removed retired bosses from bosses.yml: " + String.join(", ", removed));
            if (added.isEmpty() && updated.isEmpty() && removed.isEmpty() && renamed.isEmpty()) return;
            if (!renamed.isEmpty()) plugin.getLogger().info("Gave bosses their new names in bosses.yml: " + String.join(", ", renamed));
            if (!updated.isEmpty()) plugin.getLogger().info("Updated redesigned bosses in bosses.yml (rewards kept, old file saved as bosses.yml.bak): " + String.join(", ", updated));
            com.cbosses.util.SafeFiles.write(file, yaml.saveToString());
            if (!added.isEmpty()) plugin.getLogger().info("Added new bosses to bosses.yml: " + String.join(", ", added));
        } catch (Exception e) {
            plugin.getLogger().warning("Could not add new bosses to bosses.yml: " + e.getMessage());
        }
    }

    /** Apply the requested health and damage tiers once (v2: minis 1000, the rest 3000, softer hits);
     *  every reward and other custom field is kept. */
    private void migratePolishHealth(java.io.File file, YamlConfiguration yaml) {
        if (yaml.getInt("polish-health-version", 0) >= 2) return;
        try (var in = plugin.getResource("bosses.yml")) {
            if (in == null) return;
            var bundled = YamlConfiguration.loadConfiguration(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
            var bosses = bundled.getConfigurationSection("bosses");
            if (bosses == null) return;
            for (String id : bosses.getKeys(false)) {
                String path = "bosses." + id + ".health";
                if (yaml.contains("bosses." + id)) {
                    yaml.set(path, bundled.getDouble(path));
                    yaml.set("bosses." + id + ".damage", bundled.getDouble("bosses." + id + ".damage"));
                }
            }
            yaml.set("polish-health-version", 2);
            com.cbosses.util.SafeFiles.write(file, yaml.saveToString());
        } catch (Exception e) { plugin.getLogger().warning("Could not migrate boss health: " + e.getMessage()); }
    }

    public void reload() {
        File bossFile = new File(plugin.getDataFolder(), "bosses.yml");
        YamlConfiguration bossYaml = YamlConfiguration.loadConfiguration(bossFile);
        addNewBosses(bossFile, bossYaml);
        migratePolishHealth(bossFile, bossYaml);
        defs = BossDef.load(bossYaml, plugin.getLogger());
        commands.load(bossYaml.getConfigurationSection("bosses"), plugin.getConfig());
        ModelRig.detail = switch (plugin.getConfig().getString("effects.model-detail", "high").toLowerCase(Locale.ROOT)) {
            case "low" -> 0;
            case "medium" -> 1;
            default -> 2;
        };
        Map<String, ModelRig.Model> loaded = new java.util.HashMap<>();
        try (var in = plugin.getResource("models.json")) {
            if (in != null) loaded.putAll(ModelRig.load(new InputStreamReader(in, StandardCharsets.UTF_8)));
        } catch (IOException | RuntimeException e) {
            plugin.getLogger().warning("Could not read the boss models, bosses use plain mobs: " + e);
        }
        loadModelFolder(loaded);
        models = loaded;
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(arenasFile);
        arenas.clear();
        var section = yaml.getConfigurationSection("arenas");
        if (section != null) for (String id : section.getKeys(false)) {
            Arena a = new Arena(id, Math.max(8, yaml.getInt("arenas." + id + ".radius", radius())));
            String spawn = yaml.getString("arenas." + id + ".spawn", "");
            String[] p = spawn.split(";");
            if (p.length == 4) try {
                a.world = p[0]; a.x = Double.parseDouble(p[1]); a.y = Double.parseDouble(p[2]); a.z = Double.parseDouble(p[3]); a.hasSpawn = true;
            } catch (NumberFormatException ignored) { }
            String region = yaml.getString("arenas." + id + ".region", "");
            a.region = region == null || region.isBlank() ? null : region;
            for (String point : yaml.getStringList("arenas." + id + ".border")) {
                String[] xz = point.split(",");
                if (xz.length == 2) try { a.points.add(new int[]{Integer.parseInt(xz[0].trim()), Integer.parseInt(xz[1].trim())}); } catch (NumberFormatException ignored) { }
            }
            a.rebuild();
            arenas.put(a.id, a);
        }
        lastRun = yaml.getString("schedule.last-run", "");
        lastWarn = yaml.getString("schedule.last-warn", "");
        scheduleOn = plugin.getConfig().getBoolean("schedule.enabled", true);
        var c = plugin.getConfig();
        Fx.rings = c.getBoolean("effects.rings", false);
        Fx.aura = c.getBoolean("effects.aura", false);
        Fx.particles = Math.max(0, Math.min(2, quality(c.getString("effects.quality", "high")) * c.getDouble("effects.particle-multiplier", 1)));
        Fx.debrisOn = c.getBoolean("effects.flying-blocks", true);
        Fx.maxDebris = Math.max(0, c.getInt("effects.max-flying-blocks", 160));
        BossModel.period = Math.max(1, Math.min(10, c.getInt("effects.model-update-ticks", 3)));
        BossModel.maxShards = Math.max(0, c.getInt("effects.max-shards-per-death", 48));
        BossModel.viewDistance = Math.max(32, c.getInt("effects.model-view-distance", 96));
    }

    private static double quality(String q) {
        return switch (q == null ? "high" : q.toLowerCase(Locale.ROOT)) {
            case "low" -> 0.35;
            case "medium" -> 0.65;
            case "ultra" -> 1.3;
            default -> 1;
        };
    }

    public void start() {
        if (timer != null) timer.cancel();
        timer = Sched.globalTimer(t -> scheduleTick(), 20 * 30, 20 * 30);
    }

    public void shutdown() {
        if (timer != null) timer.cancel();
        for (Fight f : new ArrayList<>(fights.values())) end(f, "shutdown");
    }

    private int radius() { return Math.max(8, plugin.getConfig().getInt("arenas.default-radius", 40)); }
    public boolean enabled() { return plugin.getConfig().getBoolean("enabled", true); }
    public Map<String, BossDef> defs() { return defs; }
    public BossDef def(String id) { return id == null ? null : defs.get(id.toLowerCase(Locale.ROOT)); }
    double damageMultiplier() { return Math.max(0, plugin.getConfig().getDouble("fight.damage-multiplier", 1)); }
    boolean introDarkness() { return plugin.getConfig().getBoolean("effects.intro-darkness", true); }

    /**
     * Models in plugins/CBosses/models/*.json (same format as the jar's models.json) replace or add to the
     * built-in ones by id. The folder is never touched by an update, so edited models survive a new jar,
     * and player progress lives in its own files (chapters.yml, minis.yml), so nothing is lost either way.
     */
    private void loadModelFolder(Map<String, ModelRig.Model> models) {
        File dir = new File(plugin.getDataFolder(), "models");
        if (!dir.isDirectory() && dir.mkdirs()) {
            try {
                java.nio.file.Files.writeString(new File(dir, "README.txt").toPath(), String.join("\n",
                        "Put model files here to change boss models without touching the jar.",
                        "Each .json file uses the same format as models.json inside the jar (copy it out of the jar to start).",
                        "A model here replaces the built-in model with the same id; new ids add new models.",
                        "Updating the plugin never changes this folder, and no player progress is stored in it.",
                        "Blockbench: /cbosses blockbench <boss|all> writes plugins/CBosses/blockbench/<boss>.bbmodel. Open it in",
                        "Blockbench, edit it, save it here as <boss>.bbmodel and run /cbosses reload. Cubes are named after their block.",
                        "Run /cbosses reload after changing a file.", ""));
            } catch (IOException ignored) { }
        }
        File[] bb = dir.listFiles((d, n) -> n.toLowerCase(Locale.ROOT).endsWith(".bbmodel"));
        if (bb != null && bb.length > 0) {
            java.util.Arrays.sort(bb);
            com.google.gson.JsonObject bundled = bundledModels();
            for (File f : bb) {
                String id = f.getName().substring(0, f.getName().length() - ".bbmodel".length()).toLowerCase(Locale.ROOT);
                try (var r = java.nio.file.Files.newBufferedReader(f.toPath(), StandardCharsets.UTF_8)) {
                    var project = com.google.gson.JsonParser.parseReader(r).getAsJsonObject();
                    var base = bundled != null && bundled.getAsJsonObject("models").has(id) ? bundled.getAsJsonObject("models").getAsJsonObject(id) : null;
                    var model = com.cbosses.model.BbModel.toModel(id, project, base, plugin.getLogger()::warning);
                    var root = new com.google.gson.JsonObject();
                    root.add("rigs", bundled != null ? bundled.getAsJsonObject("rigs") : new com.google.gson.JsonObject());
                    var one = new com.google.gson.JsonObject();
                    one.add(id, model);
                    root.add("models", one);
                    models.putAll(ModelRig.load(new java.io.StringReader(root.toString())));
                    plugin.getLogger().info("Loaded the Blockbench model models/" + f.getName());
                } catch (IOException | RuntimeException e) {
                    plugin.getLogger().warning("Could not read models/" + f.getName() + ": " + e.getMessage());
                }
            }
        }
        File[] files = dir.listFiles((d, n) -> n.toLowerCase(Locale.ROOT).endsWith(".json"));
        if (files == null) return;
        java.util.Arrays.sort(files);
        for (File f : files) {
            try (var r = java.nio.file.Files.newBufferedReader(f.toPath(), StandardCharsets.UTF_8)) {
                var extra = ModelRig.load(r);
                models.putAll(extra);
                plugin.getLogger().info("Loaded " + extra.size() + " boss model(s) from models/" + f.getName());
            } catch (IOException | RuntimeException e) {
                plugin.getLogger().warning("Could not read models/" + f.getName() + ": " + e.getMessage());
            }
        }
    }

    /** The jar's models.json as JSON (read fresh, only when a Blockbench file needs it), or null. */
    private com.google.gson.JsonObject bundledModels() {
        try (var in = plugin.getResource("models.json")) {
            if (in == null) return null;
            return com.google.gson.JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (IOException | RuntimeException e) {
            plugin.getLogger().warning("Could not read the built-in models: " + e.getMessage());
            return null;
        }
    }

    /** Writes Blockbench projects of one model (or "all") to plugins/CBosses/blockbench/, off the main thread. */
    public void exportBlockbench(org.bukkit.command.CommandSender to, String which) {
        Sched.async(() -> {
            String msg;
            try {
                com.google.gson.JsonObject bundled = bundledModels();
                if (bundled == null) throw new IOException("models.json is missing from the jar");
                var all = bundled.getAsJsonObject("models");
                List<String> ids = which.equalsIgnoreCase("all") ? new ArrayList<>(all.keySet()) : List.of(which.toLowerCase(Locale.ROOT));
                File dir = new File(plugin.getDataFolder(), "blockbench");
                if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("cannot create " + dir);
                int n = 0;
                for (String id : ids) {
                    if (!all.has(id)) continue;
                    var m = all.getAsJsonObject(id);
                    var rig = bundled.getAsJsonObject("rigs").getAsJsonObject(m.get("rig").getAsString());
                    java.nio.file.Files.writeString(new File(dir, id + ".bbmodel").toPath(), com.cbosses.model.BbModel.toBlockbench(id, m, rig).toString(), StandardCharsets.UTF_8);
                    n++;
                }
                msg = n == 0 ? T.t("command.blockbench-none", "<red>No built-in model called <id>.", "id", which)
                        : T.t("command.blockbench-done", "<green>Wrote <count> Blockbench model(s) to plugins/CBosses/blockbench/. <gray>Edit one, save it into plugins/CBosses/models/ and run /cbosses reload.", "count", n);
            } catch (IOException | RuntimeException e) {
                msg = "<red>Blockbench export failed: " + e.getMessage();
            }
            String done = msg;
            if (to instanceof org.bukkit.entity.Player p) Sched.entity(p, () -> plugin.send(p, done)); else Sched.global(() -> plugin.send(to, done));
        });
    }

    /** A model from models.json by id, or null. */
    public ModelRig.Model model(String id) { return id == null ? null : models.get(id.toLowerCase(Locale.ROOT)); }
    public java.util.Set<String> modelIds() { return models.keySet(); }

    /** The block model a boss is drawn with, or null (models off, "model: none", or no model by that name). */
    public ModelRig.Model modelFor(BossDef def) {
        if (!plugin.getConfig().getBoolean("models", true) || def.model().equals("none")) return null;
        return models.get(def.model());
    }
    public List<String> ids() { return new ArrayList<>(defs.keySet()); }
    public boolean scheduleOn() { return scheduleOn; }
    public Map<String, Fight> fights() { return fights; }

    /** True while a real (not test) fight with this boss is on. */
    public boolean alive(String bossId) {
        for (Fight f : fights.values()) if (!f.test && !f.over && f.def.id().equals(bossId)) return true;
        return false;
    }

    public boolean stopBoss(String bossId) {
        boolean any = false;
        for (Fight f : new ArrayList<>(fights.values())) if (f.def.id().equals(bossId)) { end(f, "stopped"); any = true; }
        return any;
    }

    public List<String> arenaIds() { return new ArrayList<>(arenas.keySet()); }
    public boolean alive() { return fights.values().stream().anyMatch(f -> !f.test && f.owner == null); }
    public Fight fightOf(UUID player) {
        for (Fight f : fights.values()) if (player.equals(f.owner) || player.equals(f.tester)) return f;
        return null;
    }

    private synchronized void save() {
        YamlConfiguration yaml = new YamlConfiguration();
        for (Arena a : arenas.values()) {
            String base = "arenas." + a.id + ".";
            if (a.hasSpawn) yaml.set(base + "spawn", a.world + ";" + a.x + ";" + a.y + ";" + a.z);
            yaml.set(base + "radius", a.radius);
            if (a.region != null) yaml.set(base + "region", a.region);
            List<String> border = new ArrayList<>();
            for (int[] p : a.points()) border.add(p[0] + "," + p[1]);
            yaml.set(base + "border", border);
        }
        yaml.set("schedule.last-run", lastRun);
        yaml.set("schedule.last-warn", lastWarn);
        String text = yaml.saveToString();
        Sched.async(() -> {
            synchronized (arenasFile) {
                try { com.cbosses.util.SafeFiles.write(arenasFile, text); }
                catch (IOException e) { plugin.getLogger().warning("Could not save arenas.yml: " + e.getMessage()); }
            }
        });
    }

    public Arena arena(String id, boolean create) {
        String key = id.toLowerCase(Locale.ROOT);
        return create ? arenas.computeIfAbsent(key, k -> new Arena(k, radius())) : arenas.get(key);
    }

    // ------------------------------------------------------------------ admin

    public void setSpawn(Player player, String arenaId) {
        Arena a = arena(arenaId, true);
        a.spawn(player.getLocation());
        save();
        plugin.send(player, T.t("fight.boss-spawn-for-arena-set", "<green>Boss spawn for arena <white><arena></white> set here. <gray>Border: <border>. Draw one with <yellow>/cbosses arena wand <arena></yellow> or link a WorldGuard region with <yellow>/cbosses arena region <arena> <region></yellow>.", "arena", a.id, "border", a.describe()));
    }

    public void setRegion(org.bukkit.command.CommandSender to, String arenaId, String region) {
        Arena a = arena(arenaId, true);
        if (region == null || region.equalsIgnoreCase("none") || region.equalsIgnoreCase("off")) {
            a.region = null; save();
            plugin.send(to, T.t("fight.arena-no-longer-uses-a", "<gray>Arena <white><arena></white> no longer uses a WorldGuard region. Border: <border>.", "arena", a.id, "border", a.describe()));
            return;
        }
        if (!WorldGuardHook.available()) { plugin.send(to, T.t("fight.worldguard-is-not-running-on", "<red>WorldGuard is not running on this server.")); return; }
        org.bukkit.World world = a.world == null ? (to instanceof Player p ? p.getWorld() : Bukkit.getWorlds().get(0)) : Bukkit.getWorld(a.world);
        int[] b = world == null ? null : WorldGuardHook.bounds(world, region);
        if (b == null) { plugin.send(to, T.t("fight.no-worldguard-region-called-in", "<red>No WorldGuard region called <region> in <world>.", "region", Text.escape(region), "world", (world == null ? "that world" : world.getName()))); return; }
        a.region = region;
        if (!a.hasSpawn) {
            int cx = (b[0] + b[3]) / 2, cz = (b[2] + b[5]) / 2;
            a.spawn(new Location(world, cx, world.getHighestBlockYAt(cx, cz) + 1, cz));
        }
        save();
        plugin.send(to, T.t("fight.arena-now-uses-the-worldguard", "<green>Arena <white><arena></white> now uses the WorldGuard region <white><region></white> as its border.", "arena", a.id, "region", Text.escape(region)));
    }

    public void giveWand(Player player, String arenaId) {
        Arena a = arena(arenaId, true);
        ItemStack stick = new ItemStack(Material.BLAZE_ROD);
        stick.editMeta(meta -> {
            meta.displayName(Text.mm(T.t("fight.boss-border-rod", "<gold><bold>Boss Border Rod</bold></gold> <gray>(<arena>)", "arena", a.id)).decoration(net.kyori.adventure.text.format.TextDecoration.ITALIC, false));
            meta.lore(List.of(Text.mm(T.t("fight.left-click-a-block-add", "<yellow>Left-click a block</yellow><gray>: add a corner")), Text.mm(T.t("fight.right-click-remove-the-last", "<yellow>Right-click</yellow><gray>: remove the last corner")),
                    Text.mm(T.t("fight.sneak-right-click-show-the", "<yellow>Sneak + right-click</yellow><gray>: show the border"))));
            meta.setEnchantmentGlintOverride(true);
            meta.getPersistentDataContainer().set(wandKey, PersistentDataType.STRING, a.id);
        });
        player.getInventory().addItem(stick).values().forEach(left -> player.getWorld().dropItemNaturally(player.getLocation(), left));
        plugin.send(player, T.t("fight.border-rod-for-arena-left", "<gold>Border rod for arena <white><arena></white>. <gray>Left-click blocks around the arena to add corners in order. The boss can never walk past this outline.", "arena", a.id));
    }

    public void clearBorder(org.bukkit.command.CommandSender to, String arenaId) {
        Arena a = arena(arenaId, false);
        if (a == null) { plugin.send(to, T.t("fight.no-arena", "<red>No arena <arenaid>", "arenaid", Text.escape(arenaId))); return; }
        a.clear(); save();
        plugin.send(to, T.t("fight.border-cleared-arena-now-uses", "<gray>Border cleared. Arena <white><arena></white> now uses <border>.", "arena", a.id, "border", a.describe()));
    }

    public void setRadius(org.bukkit.command.CommandSender to, String arenaId, int radius) {
        Arena a = arena(arenaId, true);
        a.radius = Math.max(8, Math.min(500, radius)); save();
        plugin.send(to, T.t("fight.arena-circle-radius-used-when", "<gray>Arena <white><arena></white> circle radius: <radius> (used when there is no outline or region).", "arena", a.id, "radius", a.radius));
    }

    public void deleteArena(org.bukkit.command.CommandSender to, String arenaId) {
        Arena a = arenas.remove(arenaId.toLowerCase(Locale.ROOT));
        if (a == null) { plugin.send(to, T.t("fight.no-arena", "<red>No arena <arenaid>", "arenaid", Text.escape(arenaId))); return; }
        save();
        plugin.send(to, T.t("fight.arena-deleted", "<gray>Arena <white><arena></white> deleted.", "arena", a.id));
    }

    public void listArenas(org.bukkit.command.CommandSender to) {
        if (arenas.isEmpty()) { plugin.send(to, T.t("fight.no-arenas-yet-stand-where", "<yellow>No arenas yet. Stand where the boss should appear and run /cbosses arena setspawn main.")); return; }
        for (Arena a : arenas.values()) {
            Location s = a.spawn();
            plugin.send(to, T.t("fight.border", "<white><arena> <gray><player>, border: <border><alive>", "arena", a.id, "player", (s == null ? "no spawn set" : s.getWorld().getName() + " " + s.getBlockX() + " " + s.getBlockY() + " " + s.getBlockZ()), "border", a.describe(), "alive", (fights.containsKey(a.id) ? " <red>(boss alive)" : "")));
        }
    }

    public void listBosses(org.bukkit.command.CommandSender to) {
        plugin.send(to, T.t("fight.bosses", "<gold>Bosses</gold> <gray>(<count>)", "count", defs.size()));
        for (BossDef d : defs.values()) if (!d.sidekick())
            to.sendMessage(Text.mm(" <dark_gray>-</dark_gray> <white>" + d.id() + "</white> " + d.name() + " <gray>" + Text.escape(d.title())
                    + (d.seasonal() ? " <light_purple>(" + d.season() + ")" : d.chapterBoss() ? " <aqua>(chapter " + d.chapter() + ")" : "")));
    }

    public boolean stop(String arenaId) {
        Fight f = fights.get(arenaId.toLowerCase(Locale.ROOT));
        if (f == null) return false;
        end(f, "stopped"); return true;
    }

    public void stopAll() { for (Fight f : new ArrayList<>(fights.values())) end(f, "stopped"); }

    public void scheduleToggle(org.bukkit.command.CommandSender to, boolean on) {
        scheduleOn = on;
        plugin.getConfig().set("schedule.enabled", on);
        plugin.saveConfig();
        plugin.send(to, T.t("fight.weekly-boss", "<gray>Weekly boss: <white><off>", "off", (on ? "on" : "off")));
    }

    // ------------------------------------------------------------------ schedule

    private ZoneId zone() {
        String z = plugin.getConfig().getString("schedule.zone", "");
        try { return z == null || z.isBlank() ? ZoneId.systemDefault() : ZoneId.of(z); } catch (RuntimeException e) { return ZoneId.systemDefault(); }
    }

    /** The next scheduled spawn after now, or null when the schedule is off or has no days. */
    public ZonedDateTime next() {
        if (!scheduleOn || !enabled()) return null;
        List<DayOfWeek> days = new ArrayList<>();
        for (String d : plugin.getConfig().getStringList("schedule.days"))
            try { days.add(DayOfWeek.valueOf(d.trim().toUpperCase(Locale.ROOT))); } catch (IllegalArgumentException ignored) { }
        if (days.isEmpty()) return null;
        List<LocalTime> times = new ArrayList<>();
        Object raw = plugin.getConfig().get("schedule.time", "20:00");
        List<?> list = raw instanceof List<?> l ? l : List.of(String.valueOf(raw));
        for (Object o : list) try { times.add(LocalTime.parse(String.valueOf(o).trim())); } catch (RuntimeException ignored) { }
        if (times.isEmpty()) times.add(LocalTime.of(20, 0));
        ZonedDateTime best = null;
        for (LocalTime time : times) {
            ZonedDateTime slot = nextAfter(ZonedDateTime.now(zone()), days, time, lastRun);
            if (slot != null && (best == null || slot.isBefore(best))) best = slot;
        }
        return best;
    }

    /** First day/time slot at or after {@code now} that has not run yet. lastRun is "date" or "date time". Static for tests. */
    public static ZonedDateTime nextAfter(ZonedDateTime now, List<DayOfWeek> days, LocalTime time, String lastRun) {
        for (int i = 0; i <= 14; i++) {
            LocalDate date = now.toLocalDate().plusDays(i);
            if (!days.contains(date.getDayOfWeek())) continue;
            String key = date + " " + time;
            if (key.equals(lastRun) || date.toString().equals(lastRun)) continue;
            ZonedDateTime slot = date.atTime(time).atZone(now.getZone());
            if (i == 0 && slot.isBefore(now.minusHours(1))) continue; // missed by more than an hour: wait for the next one
            return slot;
        }
        return null;
    }

    /** The boss the next scheduled spawn brings: a seasonal one while its season is on, otherwise the weekly rotation. */
    public BossDef upcoming() {
        List<BossDef> seasonal = new ArrayList<>(), normal = new ArrayList<>();
        Set<String> skip = new HashSet<>(plugin.getConfig().getStringList("schedule.exclude"));
        boolean chapterInRotation = plugin.getConfig().getBoolean("schedule.include-chapter-bosses", false);
        for (BossDef d : defs.values()) {
            if (skip.contains(d.id()) || d.mini() || d.sidekick()) continue;
            if (d.seasonal()) { if (plugin.seasons().active(d.season())) seasonal.add(d); }
            else if (!d.chapterBoss() || chapterInRotation) normal.add(d);
        }
        long week = LocalDate.now(zone()).toEpochDay() / 7;
        if (!seasonal.isEmpty() && plugin.getConfig().getBoolean("seasons.replace-weekly-boss", true)) return seasonal.get((int) (week % seasonal.size()));
        if (normal.isEmpty()) return null;
        if ("random".equalsIgnoreCase(plugin.getConfig().getString("schedule.order", "rotate")))
            return normal.get(new java.util.Random(week * 7919L).nextInt(normal.size()));
        return normal.get((int) (week % normal.size()));
    }

    private void scheduleTick() {
        ZonedDateTime slot = next();
        if (slot == null) return;
        ZonedDateTime now = ZonedDateTime.now(zone());
        String key = slot.toLocalDate() + " " + slot.toLocalTime();
        int warn = Math.max(0, plugin.getConfig().getInt("schedule.warn-minutes", 10));
        BossDef def = upcoming();
        if (def == null) return;
        if (warn > 0 && !key.equals(lastWarn) && now.isAfter(slot.minusMinutes(warn)) && now.isBefore(slot)) {
            lastWarn = key; save();
            broadcast(plugin.msg("schedule-warning", T.t("fight.boss-wakes-in-minutes", "<gold><bold>⚔ BOSS</bold></gold> <boss> <gray>wakes in <white><minutes> minutes</white><where>"))
                    .replace("<boss>", def.name()).replace("<minutes>", Integer.toString(warn)).replace("<where>", where(arenaFor())));
        }
        if (!now.isBefore(slot)) {
            lastRun = key; save();
            Arena a = arenaFor();
            if (a == null || a.spawn() == null) {
                plugin.getLogger().info("Weekly boss skipped: set a spawn with /cbosses arena setspawn " + plugin.getConfig().getString("schedule.arena", "main"));
                return;
            }
            spawn(def, a, null, false, null);
        }
    }

    private Arena arenaFor() { return arena(plugin.getConfig().getString("schedule.arena", "main"), false); }

    private String where(Arena a) {
        Location s = a == null ? null : a.spawn();
        return s == null ? "." : " <gray>at <white>" + s.getBlockX() + ", " + s.getBlockZ() + "</white> (" + s.getWorld().getName() + ").";
    }

    // ------------------------------------------------------------------ spawning

    /**
     * Starts a fight. {@code tester} non-null gets told why if it fails; {@code test} pays nothing.
     * {@code owner} makes it a chapter fight that belongs to that player.
     */
    public boolean spawn(BossDef def, Arena arena, Player tester, boolean test, Player owner) {
        if (!enabled()) { if (tester != null) plugin.send(tester, T.t("fight.cbosses-is-turned-off-enabled", "<yellow>CBosses is turned off (enabled: false).")); return false; }
        String key = owner != null ? "chapter:" + owner.getUniqueId() : test ? "test:" + tester.getUniqueId() : arena.id;
        Fight old = fights.get(key);
        if (old != null) {
            if (!test && owner == null) { if (tester != null) plugin.send(tester, T.t("fight.a-boss-is-already-alive", "<yellow>A boss is already alive in <arena>. /cbosses stop <arena>", "arena", arena.id)); return false; }
            end(old, "stopped");
        }
        if (fights.size() >= Math.max(1, plugin.getConfig().getInt("fight.max-active", 6))) {
            if (tester != null) plugin.send(tester, T.t("fight.too-many-bosses-are-alive", "<yellow>Too many bosses are alive at once (fight.max-active)."));
            return false;
        }
        Location at = arena.spawn();
        if (at == null) { if (tester != null) plugin.send(tester, T.t("fight.arena-has-no-spawn-cbosses", "<yellow>Arena <arena> has no spawn. /cbosses arena setspawn <arena>", "arena", arena.id)); return false; }
        if (at.getWorld().getDifficulty() == org.bukkit.Difficulty.PEACEFUL) { if (tester != null) plugin.send(tester, T.t("fight.bosses-cannot-appear-in-a", "<yellow>Bosses cannot appear in a Peaceful world.")); return false; }
        if (!WorldGuardHook.maySpawn(at)) { if (tester != null) plugin.send(tester, T.t("fight.the-worldguard-flag-cbosses-spawn", "<yellow>The WorldGuard flag cbosses-spawn is set to deny here.")); return false; }
        List<String> worlds = plugin.getConfig().getStringList("fight.disabled-worlds");
        if (worlds.contains(at.getWorld().getName())) { if (tester != null) plugin.send(tester, T.t("fight.bosses-are-off-in-this", "<yellow>Bosses are off in this world (fight.disabled-worlds).")); return false; }
        BossSpawnEvent event = new BossSpawnEvent(def.id(), at, owner, test);
        Bukkit.getPluginManager().callEvent(event);
        if (event.isCancelled()) { if (tester != null) plugin.send(tester, T.t("fight.another-plugin-stopped-the-boss", "<yellow>Another plugin stopped the boss from spawning.")); return false; }
        UUID ownerId = owner == null ? null : owner.getUniqueId();
        // a chapter boss is the quest player's own: nobody else sees, hears or meets any part of it
        String zone = ownerId != null && privateChapters() ? key + "#" + System.nanoTime() : null;
        if (zone != null) {
            Privacy.add(zone, at, arena.radius + 8, ownerId);
            pendingZone.put(key, zone);
        }
        Runnable go = () -> {
            if (spawnFight(def, arena, key, at, tester, test, ownerId) == null && zone != null) { Privacy.remove(zone); pendingZone.remove(key, zone); }
        };
        Sched.at(at, () -> {
            if (plugin.getConfig().getBoolean("effects.intro", true)) cinema.omen(at, def, go);
            else go.run();
        });
        return true;
    }

    public boolean spawnAt(Player player, String bossId, String arenaId) {
        BossDef def = def(bossId);
        if (def == null) { plugin.send(player, T.t("fight.no-boss-cbosses-list", "<red>No boss <bossid>. <gray>/cbosses list", "bossid", Text.escape(bossId))); return false; }
        Arena a = arena(arenaId, false);
        if (a == null) { plugin.send(player, T.t("fight.no-arena-cbosses-arena-setspawn", "<red>No arena <arenaid>. <gray>/cbosses arena setspawn <arenaid>", "arenaid", Text.escape(arenaId))); return false; }
        return spawn(def, a, player, false, null);
    }

    private final java.util.concurrent.atomic.AtomicInteger hereCount = new java.util.concurrent.atomic.AtomicInteger();

    /**
     * Ops only: a real fight right where the player stands. Its border is a circle (arenas.here-radius) around
     * that spot; like every boss it only attacks players and never touches blocks.
     */
    public boolean spawnHere(Player player, String bossId) {
        BossDef def = def(bossId);
        if (def == null) { plugin.send(player, T.t("fight.no-boss-cbosses-list", "<red>No boss <bossid>. <gray>/cbosses list", "bossid", Text.escape(bossId))); return false; }
        Arena a = new Arena("here-" + hereCount.incrementAndGet(), Math.max(10, plugin.getConfig().getInt("arenas.here-radius", 40)));
        a.spawn(player.getLocation().clone());
        return spawn(def, a, player, false, null);
    }

    /** /cbosses test: the boss appears a few blocks in front of you inside a 25 block circle; nothing is paid. */
    public boolean test(Player player, String bossId) {
        BossDef def = def(bossId);
        if (def == null) { plugin.send(player, T.t("fight.cbosses-test-bosses", "<yellow>/cbosses test <boss></yellow> <gray>Bosses: <white><list>", "list", String.join(", ", defs.keySet()))); return false; }
        Arena a = new Arena("test-" + player.getName().toLowerCase(Locale.ROOT), 25);
        Vector look = player.getLocation().getDirection().setY(0);
        if (look.lengthSquared() < 0.01) look = new Vector(1, 0, 0);
        Location front = player.getLocation().clone().add(look.normalize().multiply(7));
        front.setY(player.getLocation().getY());
        a.spawn(front);
        return spawn(def, a, player, true, null);
    }

    /** A chapter boss for one player, in a circle around where they stand. */
    public boolean chapterFight(Player player, BossDef def, int radius) {
        Arena a = new Arena("chapter-" + player.getName().toLowerCase(Locale.ROOT), Math.max(12, radius));
        Vector look = player.getLocation().getDirection().setY(0);
        if (look.lengthSquared() < 0.01) look = new Vector(1, 0, 0);
        Location front = player.getLocation().clone().add(look.normalize().multiply(9));
        front.setY(front.getWorld().getHighestBlockYAt(front) + 1);
        if (Math.abs(front.getY() - player.getLocation().getY()) > 6) front.setY(player.getLocation().getY());
        a.spawn(front);
        return spawn(def, a, player, false, player);
    }

    /**
     * /cbosses selftest (console too): every boss appears near the world spawn, runs every attack once with
     * nobody around, plays its death animation and is removed. Reports how many worked.
     */
    public void selfTest(org.bukkit.command.CommandSender to) {
        var world = Bukkit.getWorlds().get(0);
        Location base = world.getSpawnLocation();
        List<BossDef> list = new ArrayList<>(defs.values());
        list.removeIf(BossDef::sidekick);
        AtomicInteger appeared = new AtomicInteger(), attacks = new AtomicInteger(), done = new AtomicInteger(), drawn = new AtomicInteger(),
                blocks = new AtomicInteger(), hitZones = new AtomicInteger(), animations = new AtomicInteger(), deaths = new AtomicInteger();
        List<String> broken = new CopyOnWriteArrayList<>();
        Map<String, String> stage = new ConcurrentHashMap<>();
        Map<String, Fight> running = new ConcurrentHashMap<>();
        AtomicBoolean reported = new AtomicBoolean();
        Runnable report = () -> {
            if (!reported.compareAndSet(false, true)) return;
            stage.forEach((id, w) -> {
                if (w.equals("done")) return;
                Fight f = running.get(id);
                broken.add(id + ": stuck at " + w + (f == null ? "" : " (fight " + (f.over ? "ended: " + f.endReason : "running")
                        + ", boss " + (f.boss.isValid() ? "valid" : f.boss.isDead() ? "dead" : "removed") + ")"));
            });
            String text = "Boss self-test: " + appeared.get() + "/" + list.size() + " appeared, " + attacks.get() + " attacks ran, "
                    + drawn.get() + " drawn with " + blocks.get() + " blocks and " + hitZones.get() + " hit zones, " + animations.get() + " animations, " + deaths.get() + " deaths played"
                    + (broken.isEmpty() ? "" : ". Problems: " + String.join("; ", broken));
            if (broken.isEmpty()) plugin.getLogger().info(text); else plugin.getLogger().warning(text);
            if (to instanceof Player) plugin.send(to, "<gray>" + Text.escape(text));
        };
        Consumer<String> finish = id -> { if (!"done".equals(stage.put(id, "done")) && done.incrementAndGet() >= list.size()) report.run(); };
        Bukkit.getGlobalRegionScheduler().runDelayed(plugin, t -> report.run(), 1500);
        for (int i = 0; i < list.size(); i++) {
            BossDef def = list.get(i);
            stage.put(def.id(), "omen");
            Location at = base.clone().add(30 + (i % 7) * 12, 0, 30 + (i / 7) * 12);
            Sched.at(at, () -> cinema.omen(at, def, () -> {
                at.setY(at.getWorld().getHighestBlockYAt(at) + 1);
                Arena arena = new Arena("selftest-" + def.id(), 20);
                arena.spawn(at);
                Fight f;
                try { f = spawnFight(def, arena, "selftest:" + def.id(), at, null, true, null); }
                catch (RuntimeException | LinkageError e) { broken.add(def.id() + ": " + e); finish.accept(def.id()); return; }
                if (f == null) { broken.add(def.id() + ": did not appear"); finish.accept(def.id()); return; }
                appeared.incrementAndGet();
                stage.put(def.id(), "entrance");
                running.put(def.id(), f);
                BossModel model = f.model;
                if (model != null) { model.force = true; drawn.incrementAndGet(); blocks.addAndGet(model.blocks()); hitZones.addAndGet(model.zoneCount()); }
                else if (modelFor(def) != null) broken.add(def.id() + ": model missing");
                int entrance = 0;
                if (model != null) for (ModelRig.Step s : model.model.spawn) entrance = Math.max(entrance, s.end());
                Sched.entityLater(f.boss, 20 + entrance, () -> {
                    stage.put(def.id(), "attacks");
                    for (String ability : Abilities.ALL) {
                        try { abilities.run(f, ability, List.of()); attacks.incrementAndGet(); }
                        catch (RuntimeException | LinkageError e) { broken.add(def.id() + " " + ability + ": " + e); }
                    }
                    try { aura(f, f.boss.getLocation()); cinema.phase(f, 1); }
                    catch (RuntimeException | LinkageError e) { broken.add(def.id() + " effects: " + e); }
                    if (model == null) {
                        Sched.entityLater(f.boss, 60, () -> {
                            try { cinema.deathStart(f, f.boss.getLocation()); cinema.deathEnd(f, f.boss.getLocation()); deaths.incrementAndGet(); }
                            catch (RuntimeException | LinkageError e) { broken.add(def.id() + " death: " + e); }
                            end(f, "stopped"); finish.accept(def.id());
                        });
                        return;
                    }
                    List<String> anims = new ArrayList<>(model.model.attackAnimations());
                    for (int k = 0; k < anims.size(); k++) {
                        String name = anims.get(k);
                        Sched.entityLater(f.boss, 40 + k * 24L, () -> model.attack(name));
                    }
                    Sched.entityLater(f.boss, 42 + anims.size() * 24L, () -> {
                        stage.put(def.id(), "death");
                        animations.addAndGet(model.animationsPlayed);
                        Location fell = f.boss.getLocation();
                        try {
                            cinema.deathStart(f, fell);
                            model.die(() -> { deaths.incrementAndGet(); try { cinema.deathEnd(f, fell); } catch (RuntimeException ignored) { } finish.accept(def.id()); });
                        } catch (RuntimeException | LinkageError e) { broken.add(def.id() + " death: " + e); finish.accept(def.id()); }
                        end(f, "stopped");
                    });
                });
            }));
        }
    }

    public boolean testStop(Player player) {
        Fight f = fights.get("test:" + player.getUniqueId());
        if (f == null) f = fights.get("chapter:" + player.getUniqueId());
        if (f == null) return false;
        end(f, "stopped"); return true;
    }

    public boolean testPhase(Player player) {
        Fight f = fights.get("test:" + player.getUniqueId());
        if (f == null) return false;
        Sched.entity(f.boss, () -> {
            if (!f.boss.isValid()) return;
            double next = f.phase < f.def.phases().size() ? f.def.phases().get(f.phase) : 0.1;
            f.boss.setHealth(Math.max(1, f.max * next - 1));
        });
        return true;
    }

    /** Console commands set per boss (bosses.yml) and per group (config.yml rewards.commands). */
    final BossCommands commands = new BossCommands();

    private void runCommands(BossDef def, String when, Location at, String player) {
        Map<String, String> v = new java.util.HashMap<>();
        v.put("player", player == null ? "" : player);
        v.put("boss", def.id());
        v.put("bossname", def.name().replaceAll("<[^>]*>", ""));
        v.put("place", "1");
        if (at != null && at.getWorld() != null) {
            v.put("world", at.getWorld().getName());
            v.put("x", Integer.toString(at.getBlockX())); v.put("y", Integer.toString(at.getBlockY())); v.put("z", Integer.toString(at.getBlockZ()));
        }
        for (String raw : commands.forBoss(def, when, null)) {
            if (raw.contains("%player%") && v.get("player").isEmpty()) continue;
            String command = BossCommands.fill(raw, v);
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command));
        }
    }

    private String nearestName(Location at) {
        Player best = null;
        double d = Double.MAX_VALUE;
        for (Player p : at.getNearbyPlayers(64)) { double q = p.getLocation().distanceSquared(at); if (q < d) { d = q; best = p; } }
        return best == null ? null : best.getName();
    }

    private Fight spawnFight(BossDef def, Arena arena, String key, Location at, Player tester, boolean test, UUID owner) {
        return spawnFight(def, arena, key, at, tester, test, owner, false);
    }

    private boolean mythic(BossDef def) { return def.tier().equals("mythic"); }

    /** quiet: the second body of a two-body boss, which appears without its own announcement. */
    private Fight spawnFight(BossDef def, Arena arena, String key, Location at, Player tester, boolean test, UUID owner, boolean quiet) {
        Mob mob;
        ModelRig.Model look = modelFor(def);
        // more health for every extra player near when it wakes (fight.health-per-player)
        int crowd = 0;
        for (Player p : at.getNearbyPlayers(Math.max(24, arena.radius + 8))) if (fighter(p)) crowd++;
        double health = def.health() * (1 + def.healthPerPlayer() * Math.max(0, crowd - 1)) * Math.max(0.05, plugin.getConfig().getDouble("fight.health-multiplier", 1));
        if (owner != null) health *= Math.max(0.05, plugin.getConfig().getDouble("chapter-bosses.health-multiplier", 1));
        if (mythic(def)) health *= Math.max(0.05, plugin.getConfig().getDouble("mythic.health-multiplier", 1));
        final double hp = health;
        try {
            mob = (Mob) at.getWorld().spawn(at, def.entity().getEntityClass(), e -> { Privacy.claim(e); dress((Mob) e, def, key, look, hp); });
        } catch (RuntimeException e) {
            if (tester != null) plugin.send(tester, T.t("fight.could-not-appear-here", "<yellow><boss> <yellow>could not appear here: <getmessage>", "boss", def.name(), "getmessage", Text.escape(String.valueOf(e.getMessage()))));
            else plugin.getLogger().warning("Boss " + def.id() + " could not appear: " + e);
            return null;
        }
        if (!mob.isValid()) {
            if (tester != null) plugin.send(tester, T.t("fight.something-stopped-the-boss-from", "<yellow>Something stopped the boss from appearing (another plugin or a protected area)."));
            else plugin.getLogger().warning("Boss " + def.id() + " was removed right after spawning (protected area, Peaceful or another plugin). With WorldGuard, check worldguard.bypass-spawn-blocking in config.yml.");
            return null;
        }
        double max = maxHealth(mob);
        BossBar bar = BossBar.bossBar(Text.mm(def.name()), 0f, barColor(def.bar()), BossBar.Overlay.NOTCHED_20);
        Fight fight = new Fight(key, def, arena, test, tester == null ? null : tester.getUniqueId(), owner, mob, max, bar, hp);
        fight.privateZone = owner == null ? null : pendingZone.remove(key);
        if (fight.privateZone != null) mob.setCollidable(false);
        fight.nextAbility = System.currentTimeMillis() + 6000;
        fight.nextDash = System.currentTimeMillis() + 9000;
        var cfg = plugin.getConfig();
        if (mythic(def)) fight.power = Math.max(0.1, cfg.getDouble("mythic.damage-multiplier", 1.25));
        try { fight.aura = Particle.valueOf(plugin.getConfig().getString("bosses-aura." + def.id(), fight.theme.spark().name())); } catch (IllegalArgumentException e) { fight.aura = fight.theme.spark(); }
        if (owner != null) { Player o = Bukkit.getPlayer(owner); if (o != null) fight.names.put(owner, o.getName()); }
        fights.put(key, fight);
        byEntity.put(mob.getUniqueId(), fight);
        if (!test) runCommands(def, "on-spawn", at, owner != null && Bukkit.getPlayer(owner) != null ? Bukkit.getPlayer(owner).getName() : nearestName(at));
        fight.chunkWorld = at.getWorld().getName(); fight.chunkX = at.getBlockX() >> 4; fight.chunkZ = at.getBlockZ() >> 4;
        fight.chunkR = Math.max(1, Math.min(2, (arena.radius + 15) >> 4));
        tickets(at.getWorld(), fight, 1);
        if (def.flies()) {
            mob.setGravity(false);
            mob.setAI(false);
        }
        if (look != null) {
            BossModel model = new BossModel(plugin, look, mob);
            try {
                model.build(kindKey, fightKey, key);
                model.meleeDamage = (def.damage() > 0 ? def.damage() : 6) * fight.power;
                model.flying = def.flies();
                fight.model = model;
                boolean ai = mob.hasAI();
                mob.setAI(false);
                mob.setInvulnerable(true);
                int entrance = 0;
                for (ModelRig.Step s : look.spawn) entrance = Math.max(entrance, s.end());
                fight.nextAbility = System.currentTimeMillis() + 5000 + entrance * 50L;
                fight.nextDash = fight.nextAbility + 3000;
                model.appear(() -> {
                    if (!mob.isValid() || fight.over) return;
                    mob.setInvulnerable(false);
                    if (ai) mob.setAI(true);
                    if ((!test || tester != null) && !quiet) cinema.titleCard(fight);
                });
            } catch (RuntimeException | LinkageError e) {
                model.remove();
                fight.model = null;
                mob.setInvisible(false);
                plugin.getLogger().warning("Boss " + def.id() + " could not build its model, using the plain mob: " + e);
            }
        }
        if (fight.model == null) {
            at.getWorld().strikeLightningEffect(at);
            Fx.particle(at.getWorld(), Particle.EXPLOSION_EMITTER, at.clone().add(0, 1, 0), 2, 0, 0, 0, 0, fight.theme);
            Fx.sound(at, "ENTITY_WITHER_SPAWN", 1.2f, 0.9f);
            cinema.titleCard(fight);
        }
        mob.getScheduler().runAtFixedRate(plugin, t -> { if (!tick(fight)) t.cancel(); }, () -> end(fight, "gone"), 2, 10);
        if (def.flies()) mob.getScheduler().runAtFixedRate(plugin, t -> { if (!fly(fight)) t.cancel(); }, null, 4, 2);
        if (!def.partner().isEmpty() && !def.sidekick() && !quiet) {
            BossDef pd = def(def.partner());
            if (pd != null && !pd.id().equals(def.id())) {
                Location side = null;
                for (double dx : new double[]{2.4, -2.4, 0}) {
                    Location l = at.clone().add(dx, 0, dx == 0 ? 2.4 : 0);
                    if (!l.getBlock().isSolid() && !l.clone().add(0, 1, 0).getBlock().isSolid()) { side = l; break; }
                }
                Fight other = spawnFight(pd, arena, key + "+" + pd.id(), side == null ? at : side, tester, test, owner, true);
                if (other != null) {
                    other.partner = fight; fight.partner = other; other.payDef = def;
                    other.privateZone = fight.privateZone;
                    if (other.privateZone != null) other.boss.setCollidable(false);
                }
            }
        }
        if (quiet) return fight;
        if (test) {
            if (tester != null) plugin.send(tester, T.t("fight.test-boss-nothing-is-paid", "<gray>Test boss: <boss> <gray>(<id>). Nothing is paid. <yellow>/cbosses test phase</yellow> jumps to the next phase, <yellow>/cbosses test stop</yellow> ends it.", "boss", def.name(), "id", def.id()));
        } else if (owner != null) {
            Player o = Bukkit.getPlayer(owner);
            if (o != null) plugin.send(o, plugin.msg("chapter-boss-started", T.t("fight.has-come-for-you-beat", "<gold>⚔ <boss> <gold>has come for you! <gray>Beat it to claim the chapter reward. Leave the circle or die and it leaves.")).replace("<boss>", def.name()));
        } else {
            broadcast(plugin.msg("spawn-broadcast", T.t("fight.world-boss-has-risen-everyone", "<dark_gray><st>                                        </st>\n<gold><bold>⚔ WORLD BOSS ⚔</bold></gold>  <boss>\n<title>\n<gold>has risen<where>\n<gray>Everyone who helps gets a reward; the top 3 by damage get more.\n<dark_gray><st>                                        </st>"))
                    .replace("<boss>", def.name()).replace("<title>", def.title().isBlank() ? "" : "<gray><italic>" + Text.escape(def.title()) + "</italic>").replace("<where>", where(arena)));
            if (plugin.getConfig().getBoolean("announcements.spawn-sound", true))
                Sched.global(() -> { for (Player p : Bukkit.getOnlinePlayers()) Sched.entity(p, () -> p.playSound(p.getLocation(), Sound.ENTITY_WITHER_SPAWN, 0.5f, 0.8f)); });
        }
        return fight;
    }

    private void dress(Mob m, BossDef def, String key, ModelRig.Model look, double health) {
        m.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "boss");
        m.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, key);
        m.setPersistent(false); m.setRemoveWhenFarAway(false); m.setCanPickupItems(false); m.setSilent(look != null);
        m.customName(Text.mm(def.name())); m.setCustomNameVisible(look == null); m.setGlowing(look == null && plugin.getConfig().getBoolean("fight.glow-plain-mobs", true));
        if (m instanceof Ageable a) a.setAdult();
        if (m instanceof PiglinAbstract p) p.setImmuneToZombification(true);
        if (m instanceof Hoglin h) h.setImmuneToZombification(true);
        if (m instanceof Creeper c) { c.setPowered(look == null); c.setMaxFuseTicks(Integer.MAX_VALUE / 4); }
        double baseHeight = Math.max(0.2, m.getHeight());
        if (m instanceof Slime s) s.setSize(look == null ? def.size() : Math.max(1, Math.min(16, (int) Math.round(look.blocks() * look.hitbox / 0.52))));
        if (m instanceof Wolf w) w.setAngry(true);
        if (m instanceof Rabbit r) r.setRabbitType(Rabbit.Type.THE_KILLER_BUNNY);
        attr(m, "max_health", Math.min(1024, health));
        m.setHealth(Math.max(1, Math.min(1024, health)));
        if (!(m instanceof Slime)) attr(m, "scale", look == null ? def.scale() : Math.max(0.3, Math.min(14, look.blocks() * look.hitbox / baseHeight)));
        if (look != null) m.setInvisible(true);
        if (def.damage() > 0) attr(m, "attack_damage", def.damage() * Math.max(0, plugin.getConfig().getDouble("fight.damage-multiplier", 1))
                * (mythic(def) ? Math.max(0.1, plugin.getConfig().getDouble("mythic.damage-multiplier", 1.25)) : 1));
        if (def.speed() > 0) attr(m, "movement_speed", def.speed());
        if (def.armor() > 0) attr(m, "armor", def.armor());
        attr(m, "knockback_resistance", 1.0);   // hits never launch a boss; only its own leap, charge or slam moves it
        attr(m, "follow_range", 48);
        attr(m, "step_height", 1.5);
        EntityEquipment eq = m.getEquipment();
        if (look != null) { eq.clear(); return; }
        for (var entry : def.equipment().entrySet()) {
            Material material = Material.matchMaterial(entry.getValue());
            if (material == null) continue;
            ItemStack item = new ItemStack(material);
            item.editMeta(meta -> {
                meta.setEnchantmentGlintOverride(true);
                if (meta instanceof LeatherArmorMeta leather) leather.setColor(Theme.of(def.theme()).main());
            });
            EquipmentSlot slot = switch (entry.getKey()) {
                case "head" -> EquipmentSlot.HEAD; case "chest" -> EquipmentSlot.CHEST; case "legs" -> EquipmentSlot.LEGS;
                case "feet" -> EquipmentSlot.FEET; case "offhand" -> EquipmentSlot.OFF_HAND; default -> EquipmentSlot.HAND;
            };
            eq.setItem(slot, item);
            eq.setDropChance(slot, 0f);
        }
    }

    private static Attribute attribute(String name) {
        Attribute a = Registry.ATTRIBUTE.get(NamespacedKey.minecraft(name));
        return a != null ? a : Registry.ATTRIBUTE.get(NamespacedKey.minecraft("generic." + name));
    }

    static void attr(LivingEntity e, String name, double value) {
        Attribute a = attribute(name);
        var instance = a == null ? null : e.getAttribute(a);
        if (instance != null) instance.setBaseValue(value);
    }

    private static double maxHealth(LivingEntity e) {
        Attribute a = attribute("max_health");
        var instance = a == null ? null : e.getAttribute(a);
        return instance == null ? Math.max(1, e.getHealth()) : instance.getValue();
    }

    private static BossBar.Color barColor(String name) {
        try { return BossBar.Color.valueOf(name); } catch (IllegalArgumentException e) { return BossBar.Color.RED; }
    }

    // ------------------------------------------------------------------ fight loop

    static boolean fighter(Player p) {
        return p.isOnline() && !p.isDead() && (p.getGameMode() == GameMode.SURVIVAL || p.getGameMode() == GameMode.ADVENTURE);
    }

    /** Chapter bosses only exist for their own player (chapter-bosses.private). */
    boolean privateChapters() { return plugin.getConfig().getBoolean("chapter-bosses.private", true); }

    /** May the boss hurt this player: a chapter fight only hurts its owner (and helpers when allowed); the cbosses-fight flag is respected. */
    boolean mayHurt(Fight f, Player p) {
        if (!fighter(p)) return false;
        if (f.privateZone != null && !p.getUniqueId().equals(f.owner)) return false;
        if (f.owner != null && !f.owner.equals(p.getUniqueId()) && !plugin.getConfig().getBoolean("chapter-bosses.allow-helpers", true)) return false;
        return WorldGuardHook.mayFight(p);
    }

    /** Players in the fight: inside the border, near the boss, and allowed to be hurt. */
    List<Player> fighters(Fight f) {
        List<Player> out = new ArrayList<>();
        Location loc = f.boss.getLocation();
        for (Player p : loc.getNearbyPlayers(40)) if (Bukkit.isOwnedByCurrentRegion(p) && f.arena.contains(p.getLocation()) && mayHurt(f, p)) out.add(p);
        return out;
    }

    void later(Fight f, long ticks, Runnable hit) {
        Sched.entityLater(f.boss, ticks, () -> { if (f.boss.isValid() && !f.over) hit.run(); });
    }

    Entity root(Mob boss) { return boss.getVehicle() != null ? boss.getVehicle() : boss; }

    void effect(Player p, String name, int ticks, int level) {
        PotionEffectType type = Registry.EFFECT.get(NamespacedKey.minecraft(name));
        if (type != null) p.addPotionEffect(new PotionEffect(type, ticks, level));
    }

    /** Runs every half second on the boss's region thread. False ends the timer. */
    private boolean tick(Fight f) {
        Mob boss = f.boss;
        if (f.over) return false;
        if (!boss.isValid()) { end(f, "gone"); return false; }
        long now = System.currentTimeMillis();
        f.ticks++;
        Location loc = boss.getLocation();
        if (!f.arena.contains(loc)) {
            Location home = f.arena.spawn();
            if (home != null) {
                boss.setTarget(null);
                if (f.def.flies()) home = home.clone().add(0, f.def.flyHeight(), 0);
                root(boss).teleportAsync(home, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                Fx.particle(loc.getWorld(), Particle.REVERSE_PORTAL, loc.add(0, 1, 0), 40, 0.5, 1, 0.5, 0.1, f.theme);
            }
            return true;
        }
        List<Player> close = new ArrayList<>(), inside = new ArrayList<>();
        int barRange = Math.max(16, plugin.getConfig().getInt("fight.boss-bar-range", 56));
        for (Player p : loc.getNearbyPlayers(barRange)) {
            if (!p.isOnline() || !Bukkit.isOwnedByCurrentRegion(p)) continue;
            if (f.privateZone != null && !p.getUniqueId().equals(f.owner)) continue;
            close.add(p);
            if (p.getLocation().distanceSquared(loc) <= 1600 && f.arena.contains(p.getLocation()) && mayHurt(f, p)) inside.add(p);
        }
        if (f.viewers.size() != close.size() || f.ticks % 4 == 0) {
            Set<UUID> seen = new HashSet<>();
            for (Player p : close) { seen.add(p.getUniqueId()); if (f.viewers.add(p.getUniqueId())) p.showBossBar(f.bar); }
            for (UUID id : new ArrayList<>(f.viewers)) if (!seen.contains(id)) {
                f.viewers.remove(id);
                Player p = Bukkit.getPlayer(id);
                if (p != null) p.hideBossBar(f.bar);
            }
        }
        double health = boss.getHealth();
        long shown = Math.round(health * f.ratio);
        if (shown != f.shownHealth) {
            f.shownHealth = shown;
            if (f.introDone || f.model == null) f.bar.progress((float) Math.max(0, Math.min(1, health / Math.max(1, f.max))));
            // the bar shows only the name and the health
            f.bar.name(Text.mm(f.def.name() + " <gray>❤ <white>" + String.format(Locale.ROOT, "%,d", shown) + "<gray>/" + String.format(Locale.ROOT, "%,d", Math.round(f.max * f.ratio))));
        }
        if (!close.isEmpty()) aura(f, loc);
        Player target = null;
        if (!inside.isEmpty()) {
            f.lastPlayer = now;
            double best = Double.MAX_VALUE;
            // the two bodies of a pair hunt different players when there is more than one
            Fight mate = f.partner;
            Player avoid = mate != null && !mate.over && inside.size() > 1 && mate.boss.getTarget() instanceof Player pt ? pt : null;
            for (Player p : inside) {
                double d = p.getLocation().distanceSquared(loc) * (f.owner != null && f.owner.equals(p.getUniqueId()) ? 0.5 : 1) * (p.equals(avoid) ? 16 : 1);
                if (d < best) { best = d; target = p; }
            }
            if (!(boss.getTarget() instanceof Player current) || !inside.contains(current) || current.equals(avoid)) boss.setTarget(target);
            target = boss.getTarget() instanceof Player cur ? cur : target;
            if (f.ticks % 2 == 0) {
                for (Mob minion : f.minions) {
                    if (!minion.isValid()) { f.minions.remove(minion); byEntity.remove(minion.getUniqueId()); continue; }
                    if (Bukkit.isOwnedByCurrentRegion(minion) && minion.getTarget() == null) minion.setTarget(target);
                }
            }
        } else {
            if (boss.getTarget() != null) boss.setTarget(null);
            Location home = f.arena.spawn();
            if (home != null && !f.def.flies() && f.ticks % 10 == 0 && home.distanceSquared(loc) > 16) boss.getPathfinder().moveTo(home);
        }
        // phases at the health thresholds in bosses.yml
        while (f.phase < f.def.phases().size() && health <= f.max * f.def.phases().get(f.phase)) {
            f.phase++;
            cinema.phase(f, f.phase);
            attr(boss, "movement_speed", Math.max(0.25, (f.def.speed() > 0 ? f.def.speed() : 0.25) * (1 + 0.15 * f.phase)));
            if (f.def.minion() != null) summonMinions(f, f.def.minions());
            List<String> ab = f.def.abilities();
            if (!ab.isEmpty() && !inside.isEmpty()) { String sig = ab.get(ab.size() - 1); later(f, 30, () -> abilities.run(f, sig, fighters(f))); }
            f.nextAbility = now + 4000;
        }
        // gap closer: a walking boss far from its target dashes or leaps at it
        if (target != null && !f.def.flies() && !f.busy() && now >= f.nextDash && f.introDone && boss.hasAI()
                && target.getLocation().distanceSquared(loc) > 12 * 12 && plugin.getConfig().getBoolean("fight.gap-closer", true)) {
            f.nextDash = now + 9000;
            abilities.run(f, ThreadLocalRandom.current().nextBoolean() ? "leap" : "charge", inside);
            f.nextAbility = Math.max(f.nextAbility, now + 3500);
        }
        if (!inside.isEmpty() && now >= f.nextAbility && !f.busy() && !f.def.abilities().isEmpty() && (f.introDone || f.model == null)) {
            String ability = f.def.abilities().get(ThreadLocalRandom.current().nextInt(f.def.abilities().size()));
            abilities.run(f, ability, inside);
            f.nextAbility = now + (long) (f.def.abilitySeconds() * 1000 * f.speedFactor());
        }
        if (!f.test || f.tester != null) {
            int idle = Math.max(1, plugin.getConfig().getInt(f.owner != null ? "chapter-bosses.leave-after-seconds" : "fight.idle-minutes", f.owner != null ? 30 : 5));
            long idleMs = f.owner != null ? idle * 1000L : idle * 60_000L;
            int maxMinutes = Math.max(2, plugin.getConfig().getInt("fight.max-minutes", 30));
            if (now - f.lastPlayer > idleMs) { end(f, "idle"); return false; }
            if (now - f.born > maxMinutes * 60_000L) { end(f, "time"); return false; }
            if (f.owner != null) {
                Player o = Bukkit.getPlayer(f.owner);
                if (o == null || !o.isOnline() || o.isDead()) { end(f, o != null && o.isDead() ? "owner-died" : "owner-left"); return false; }
            }
        }
        return true;
    }

    /**
     * Flying and hovering bosses steer themselves: they circle their target at their height, turn to face
     * it and keep inside the border. A dive (from the dive attack) takes over for a moment.
     */
    private boolean fly(Fight f) {
        Mob boss = f.boss;
        if (f.over || !boss.isValid()) return false;
        if (f.model != null && !f.model.live()) return true;
        Location loc = boss.getLocation();
        Location home = f.arena.spawn();
        if (home == null) return true;
        Player target = boss.getTarget() instanceof Player p && p.isValid() && p.getWorld().equals(loc.getWorld()) ? p : null;
        if (f.swoop > 0) { f.swoop--; return true; }
        Location centre = target != null ? target.getLocation() : home;
        boolean hover = f.def.movement().equals("hover");
        f.orbit += hover ? 0.035 : 0.06;
        double radius = hover ? 5 : 9;
        double ground = centre.getWorld().getHighestBlockYAt(centre.getBlockX(), centre.getBlockZ()) + 1;
        Location want = new Location(loc.getWorld(), centre.getX() + Math.cos(f.orbit) * radius,
                Math.max(ground, centre.getY()) + f.def.flyHeight() + Math.sin(f.orbit * 2.3) * 0.8, centre.getZ() + Math.sin(f.orbit) * radius);
        if (!f.arena.contains(want)) want = home.clone().add(Math.cos(f.orbit) * 4, f.def.flyHeight(), Math.sin(f.orbit) * 4);
        Vector move = want.toVector().subtract(loc.toVector());
        double max = (hover ? 0.22 : 0.42) * (1 + 0.12 * f.phase);
        if (move.lengthSquared() > max * max) move.normalize().multiply(max);
        Location to = loc.clone().add(move);
        Location look = target != null ? target.getLocation() : want;
        Vector face = look.toVector().subtract(to.toVector()).setY(0);
        if (face.lengthSquared() > 0.01) to.setDirection(face);
        to.setPitch(0);
        if (!Bukkit.isOwnedByCurrentRegion(to)) return true;
        root(boss).teleportAsync(to, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
        if (f.ticks % 3 == 0) Fx.particle(loc.getWorld(), f.theme.mist(), loc.clone().add(0, 0.5, 0), 3, 0.6, 0.3, 0.6, 0.01, f.theme);
        return true;
    }

    /** The dive: a flying boss marks a line, then swoops down through it and climbs back up. */
    void dive(Fight f, Player target) {
        if (target == null) return;
        Mob boss = f.boss;
        Location from = boss.getLocation();
        Location aim = target.getLocation();
        Fx.lineTelegraph(new Location(aim.getWorld(), from.getX(), aim.getY(), from.getZ()), aim, 3, f.theme, 14);
        Fx.sound(from, f.theme.charge(), 1.6f, 0.7f);
        Fx.sound(from, "ENTITY_PHANTOM_SWOOP", 2f, 0.6f);
        f.swoop = 40;
        f.busyUntil = System.currentTimeMillis() + 2600;
        int steps = 10;
        Vector beyond = aim.toVector().subtract(from.toVector()).setY(0);
        if (beyond.lengthSquared() < 0.01) beyond = new Vector(1, 0, 0);
        Location end = aim.clone().add(beyond.normalize().multiply(6)).add(0, f.def.flyHeight(), 0);
        for (int i = 1; i <= steps * 2; i++) {
            int k = i;
            later(f, 14 + i * 2L, () -> {
                double t = (double) k / (steps * 2);
                Location a = from, b = aim.clone().add(0, 0.8, 0), c = end;
                // a quadratic curve: down to the target, then up and past it
                double x = (1 - t) * (1 - t) * a.getX() + 2 * (1 - t) * t * b.getX() + t * t * c.getX();
                double y = (1 - t) * (1 - t) * a.getY() + 2 * (1 - t) * t * (b.getY() - 2) + t * t * c.getY();
                double z = (1 - t) * (1 - t) * a.getZ() + 2 * (1 - t) * t * b.getZ() + t * t * c.getZ();
                Location to = new Location(a.getWorld(), x, y, z);
                Vector face = c.toVector().subtract(a.toVector()).setY(0);
                if (face.lengthSquared() > 0.01) to.setDirection(face);
                to.setPitch(0);
                if (!f.arena.contains(to) || !Bukkit.isOwnedByCurrentRegion(to)) return;
                root(boss).teleportAsync(to, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                Fx.particle(to.getWorld(), f.theme.spark(), to.clone().add(0, 1, 0), 10, 0.8, 0.4, 0.8, 0.02, f.theme);
                if (Math.abs(t - 0.5) < 0.12) {
                    Fx.debris(new Location(to.getWorld(), x, aim.getY(), z), Fx.ground(aim, f.theme), 4, 2.5, 1.5, 0.4f);
                    for (Player p : fighters(f)) if (p.getLocation().distanceSquared(to) <= 12) {
                        if (!mayHurt(f, p)) continue;
                        p.damage(abilities.dmg(f, 7), boss);
                        Vector v = p.getLocation().toVector().subtract(to.toVector()).setY(0);
                        if (v.lengthSquared() > 0.01) p.setVelocity(v.normalize().multiply(1.3).setY(0.7));
                    }
                }
            });
        }
    }

    void aura(Fight f, Location feet) {
        if (!Fx.aura) return;
        double h = f.model != null ? f.model.model.blocks() : f.boss.getHeight();
        double w = Math.max(0.6, (f.model != null ? h * 0.35 : f.boss.getWidth() / 1.5));
        Location at = feet.clone().add(0, h / 2, 0);
        Fx.particle(at.getWorld(), f.aura, at, 6, w, h / 2.5, w, 0.02, f.theme);

    }

    void summonMinions(Fight f, int count) { summonMinionsAt(f, f.boss.getLocation(), count); }

    void summonMinionsAt(Fight f, Location at, int count) {
        if (f.def.minion() == null) return;
        int max = Math.max(0, plugin.getConfig().getInt("fight.max-minions", 8));
        int alive = 0;
        for (Mob m : f.minions) if (m.isValid()) alive++;
        for (int i = 0; i < count && alive < max; i++) {
            Location spot = at.clone().add(ThreadLocalRandom.current().nextInt(-4, 5), 0, ThreadLocalRandom.current().nextInt(-4, 5));
            if (f.def.flies()) spot.setY(spot.getWorld().getHighestBlockYAt(spot) + 1);
            if (!Bukkit.isOwnedByCurrentRegion(spot) || !f.arena.contains(spot) || !spot.getBlock().isPassable() || !spot.clone().add(0, 1, 0).getBlock().isPassable()) continue;
            try {
                Entity e = spot.getWorld().spawn(spot, f.def.minion().getEntityClass(), m -> { Privacy.claim(m);
                    m.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "minion");
                    m.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, f.key);
                    m.setPersistent(false);
                    if (m instanceof Mob mob) { mob.setRemoveWhenFarAway(false); mob.setCanPickupItems(false); }
                    if (m instanceof PiglinAbstract p) p.setImmuneToZombification(true);
                    if (m instanceof Hoglin h) h.setImmuneToZombification(true);
                    if (m instanceof Wolf w) w.setAngry(true);
                    if (m instanceof Slime s) s.setSize(2);
                    if (m instanceof Creeper c) c.setMaxFuseTicks(Integer.MAX_VALUE / 4);
                });
                if (e instanceof Mob mob) { f.minions.add(mob); byEntity.put(mob.getUniqueId(), f); alive++; }
                Fx.particle(spot.getWorld(), Particle.LARGE_SMOKE, spot.clone().add(0, 0.5, 0), 15, 0.3, 0.5, 0.3, 0.02, f.theme);
                Fx.debris(spot, Fx.ground(spot, f.theme), 3, 1, 0.8, 0.3f);
            } catch (RuntimeException ignored) { }
        }
    }

    // ------------------------------------------------------------------ ending

    private final Map<String, Integer> ticketUsers = new ConcurrentHashMap<>();

    private void tickets(org.bukkit.World world, Fight f, int delta) {
        for (int dx = -f.chunkR; dx <= f.chunkR; dx++) for (int dz = -f.chunkR; dz <= f.chunkR; dz++) {
            int x = f.chunkX + dx, z = f.chunkZ + dz;
            String key = world.getName() + ":" + x + ":" + z;
            int users = ticketUsers.merge(key, delta, Integer::sum);
            if (users <= 0) ticketUsers.remove(key);
            boolean add = delta > 0 && users == 1, remove = delta < 0 && users <= 0;
            if (!add && !remove) continue;
            Location chunk = new Location(world, x * 16 + 8, 64, z * 16 + 8);
            Runnable change = () -> { if (add) world.addPluginChunkTicket(x, z, plugin); else world.removePluginChunkTicket(x, z, plugin); };
            if (Bukkit.isOwnedByCurrentRegion(chunk)) change.run(); else Sched.at(chunk, change);
        }
    }

    void end(Fight f, String reason) {
        if (f.over) return;
        f.over = true;
        Fight mate = f.partner;
        if (mate != null && !mate.over && !reason.equals("defeated")) {
            if (Bukkit.isOwnedByCurrentRegion(mate.boss)) end(mate, reason);
            else mate.boss.getScheduler().run(plugin, t -> end(mate, reason), () -> end(mate, reason));
        }
        // the death animation and its shards keep the circle private until they are gone
        if (f.privateZone != null) { String z = f.privateZone; Bukkit.getGlobalRegionScheduler().runDelayed(plugin, t -> Privacy.remove(z), 20L * 20); }
        f.endReason = reason;
        fights.remove(f.key, f);
        byEntity.remove(f.boss.getUniqueId());
        for (UUID id : f.viewers) { Player p = Bukkit.getPlayer(id); if (p != null) p.hideBossBar(f.bar); }
        f.viewers.clear();
        BossModel model = f.model;
        if (model != null) {
            if (reason.equals("shutdown")) model.remove();
            else if (!model.dying()) model.vanish();
        }
        List<Entity> leftovers = new ArrayList<>(f.parts);
        leftovers.addAll(f.minions);
        if (!reason.equals("defeated")) leftovers.add(f.boss);
        for (Entity e : leftovers) {
            byEntity.remove(e.getUniqueId());
            if (!e.isValid()) continue;
            if (Bukkit.isOwnedByCurrentRegion(e)) e.remove(); else Sched.entity(e, e::remove);
        }
        var world = Bukkit.getWorld(f.chunkWorld == null ? "" : f.chunkWorld);
        if (world != null) tickets(world, f, -1);
        if (f.test) {
            Player tester = f.tester == null ? null : Bukkit.getPlayer(f.tester);
            if (tester != null && !reason.equals("shutdown") && !reason.equals("stopped") && !reason.equals("defeated")) plugin.send(tester, T.t("fight.test-boss-ended", "<gray>Test boss ended (<reason>).", "reason", reason));
            return;
        }
        if (f.owner != null) {
            Player o = Bukkit.getPlayer(f.owner);
            if (f.def.sidekick()) return;
            if (!reason.equals("defeated")) plugin.chapters().failed(f.owner, f.payDef, reason);
            if (o != null && !reason.equals("defeated") && !reason.equals("shutdown"))
                plugin.send(o, plugin.msg("chapter-boss-left", T.t("fight.left-fight-it-again-with", "<gray><boss> <gray>left. Fight it again with <yellow>/cbosses chapter retry</yellow>.")).replace("<boss>", f.payDef.name()));
            return;
        }
        if (f.def.sidekick()) return;
        switch (reason) {
            case "idle" -> broadcast(plugin.msg("boss-idle", T.t("fight.found-no-challengers-and-left", "<gray><boss> <gray>found no challengers and left.")).replace("<boss>", f.def.name()));
            case "time" -> broadcast(plugin.msg("boss-timeout", T.t("fight.was-not-beaten-in-time", "<gray><boss> <gray>was not beaten in time and vanished.")).replace("<boss>", f.def.name()));
            case "stopped" -> broadcast(plugin.msg("boss-stopped", T.t("fight.was-sent-away", "<gray><boss> <gray>was sent away.")).replace("<boss>", f.def.name()));
            default -> { }
        }
    }

    private void victory(Fight f) {
        Fight mate = f.partner;
        if (mate != null && !mate.over) {
            // one body of a pair fell: the other carries everyone's damage, keeps the pair's rewards and gets angry
            for (var e : f.damage.entrySet()) mate.damage.merge(e.getKey(), e.getValue(), Double::sum);
            mate.names.putAll(f.names);
            if (!f.def.sidekick()) mate.payDef = f.payDef;
            Location fell = f.boss.getLocation();
            cinema.deathStart(f, fell);
            if (f.model != null) f.model.die(() -> cinema.deathEnd(f, fell));
            end(f, "defeated");
            if (f.model == null) cinema.deathEnd(f, fell);
            return;
        }
        List<Map.Entry<UUID, Double>> ranked = new ArrayList<>(f.damage.entrySet());
        ranked.sort(Map.Entry.<UUID, Double>comparingByValue().reversed());
        Location fell = f.boss.getLocation();
        cinema.deathStart(f, fell);
        if (f.model != null) f.model.die(() -> cinema.deathEnd(f, fell));
        end(f, "defeated");
        if (f.model == null) cinema.deathEnd(f, fell);
        List<UUID> order = new ArrayList<>();
        for (var e : ranked) order.add(e.getKey());
        Bukkit.getPluginManager().callEvent(new BossDefeatEvent(f.payDef.id(), fell, order, f.owner, f.test));
        if (!f.test) runCommands(f.payDef, "on-defeat", fell, f.killer != null ? f.killer : ranked.isEmpty() ? null : f.names.get(ranked.get(0).getKey()));
        if (f.test) {
            Player tester = f.tester == null ? null : Bukkit.getPlayer(f.tester);
            if (tester != null) plugin.send(tester, T.t("fight.test-boss-beaten-top-damage", "<green>Test boss beaten. <gray>Top damage: <ranked>", "ranked", top(f, ranked)));
            return;
        }
        if (f.owner != null) {
            plugin.chapters().won(f.owner, f.payDef, ranked);
            return;
        }
        double minimum = f.max * f.ratio * Math.max(0, plugin.getConfig().getDouble("rewards.min-damage-percent", 2)) / 100.0;
        if (mate != null) minimum *= 2;
        BossDef.Rewards r = f.payDef.rewards();
        int place = 0;
        for (var entry : ranked) {
            place++;
            if (entry.getValue() < minimum) continue;
            pay(entry.getKey(), f.names.getOrDefault(entry.getKey(), "?"), place, r, f.payDef);
        }
        broadcast(defeatMessage(f, ranked));
    }

    /** Pays one player: money, commands, items (top 3 get the top rewards, the best gets top-commands). */
    public void pay(UUID id, String name, int place, BossDef.Rewards r, BossDef def) {
        boolean topThree = place <= 3;
        long money = r.money() + (topThree ? r.topMoney() / place : 0);
        String moneyCommand = plugin.getConfig().getString("rewards.money-command", "eco give %player% %amount%");
        if (money > 0 && moneyCommand != null && !moneyCommand.isBlank()) {
            String command = moneyCommand.replace("%player%", name).replace("%amount%", Long.toString(money));
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
        }
        List<String> run = new ArrayList<>(commands.forBoss(def, "every-player", r.commands()));
        if (place == 1) run.addAll(commands.forBoss(def, "top-player", r.topCommands()));
        Map<String, String> values = Map.of("player", name, "place", Integer.toString(place), "boss", def.id(), "bossname", def.name().replaceAll("<[^>]*>", ""));
        for (String raw : run) {
            String command = BossCommands.fill(raw, values);
            Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command));
        }
        Player p = Bukkit.getPlayer(id);
        if (p == null) return;
        List<String> items = new ArrayList<>(r.items());
        if (topThree) items.addAll(r.topItems());
        long paid = money;
        Sched.entity(p, () -> {
            for (String line : items) {
                String[] parts = line.trim().split("\\s+");
                Material m = Material.matchMaterial(parts[0]);
                int amount = 1;
                try { if (parts.length > 1) amount = Math.max(1, Math.min(64, Integer.parseInt(parts[1]))); } catch (NumberFormatException ignored) { }
                if (m != null && m.isItem()) p.getInventory().addItem(new ItemStack(m, amount)).values().forEach(left -> p.getWorld().dropItemNaturally(p.getLocation(), left));
            }
            p.showTitle(Title.title(Text.mm(T.t("fight.victory", "<gold><bold>VICTORY")), Text.mm(T.t("fight.is-defeated-you-placed", "<boss> <gray>is defeated. You placed <white>#<place>", "boss", def.name(), "place", place))));
            plugin.send(p, T.t("fight.boss-reward-in-damage", "<gold>Boss reward: <white>#<place></white> in damage<amount><items>.", "place", place, "amount", (paid > 0 ? ", <green>+" + String.format(Locale.ROOT, "%,d", paid) + "</green> money" : ""), "items", (items.isEmpty() ? "" : ", plus items")));
        });
    }

    String defeatMessage(Fight f, List<Map.Entry<UUID, Double>> ranked) {
        double total = 0;
        for (var e : ranked) total += e.getValue();
        String line = "<dark_gray><st>                                        </st>";
        StringBuilder rows = new StringBuilder();
        String[] medal = {"defeat-first", "defeat-second", "defeat-third"};
        String[] medalDef = {"<#ffd700><bold>#1</bold>", "<#c0c0c0><bold>#2</bold>", "<#cd7f32><bold>#3</bold>"};
        for (int i = 0; i < Math.min(3, ranked.size()); i++) {
            double dmg = ranked.get(i).getValue();
            rows.append(T.t("fight.defeat-row", "<medal> <white><player> <gray><damage> damage <dark_gray>(<percent>%)",
                    "medal", T.t("fight." + medal[i], medalDef[i]), "player", Text.escape(f.names.getOrDefault(ranked.get(i).getKey(), "?")),
                    "damage", String.format(Locale.ROOT, "%,d", Math.round(dmg)), "percent", total > 0 ? Math.round(dmg * 100 / total) : 0)).append("\n");
        }
        if (ranked.isEmpty()) rows.append(T.t("fight.nobody-hurt-it", "<gray>Nobody hurt it.")).append("\n");
        String killer = f.killer == null ? "" : T.t("fight.defeat-killer", " by <white><player></white>", "player", Text.escape(f.killer));
        return T.t("fight.defeat-broadcast", "<line>\n<gold><bold>⚔ BOSS DEFEATED ⚔</bold></gold>\n<boss> <gray>was slain<killer><gray>!\n<rows><line>",
                "line", line, "boss", f.payDef.name(), "killer", killer, "rows", rows.toString());
    }

    private String top(Fight f, List<Map.Entry<UUID, Double>> ranked) {
        List<String> names = new ArrayList<>();
        for (int i = 0; i < Math.min(3, ranked.size()); i++)
            names.add("<white>" + Text.escape(f.names.getOrDefault(ranked.get(i).getKey(), "?")) + "</white> <gray>(" + Math.round(ranked.get(i).getValue()) + ")");
        return names.isEmpty() ? T.t("fight.nobody", "<gray>nobody") : String.join("<gray>, ", names);
    }

    public void broadcast(String message) {
        if (message == null || message.isBlank()) return;
        Sched.global(() -> Bukkit.broadcast(Text.mm(message)));
    }

    // ------------------------------------------------------------------ placeholders and info

    public String nextText() {
        ZonedDateTime next = next();
        if (next == null) return "";
        long minutes = Math.max(0, java.time.Duration.between(ZonedDateTime.now(zone()), next).toMinutes());
        return minutes >= 1440 ? (minutes / 1440) + "d " + (minutes % 1440 / 60) + "h" : minutes >= 60 ? (minutes / 60) + "h " + (minutes % 60) + "m" : minutes + "m";
    }

    public void info(org.bukkit.command.CommandSender to) {
        Fight live = fights.values().stream().filter(f -> !f.test && f.owner == null).findFirst().orElse(null);
        if (live != null) { plugin.send(to, T.t("fight.is-alive-now", "<gold>⚔ <boss> <gold>is alive now<where>", "boss", live.def.name(), "where", where(live.arena))); return; }
        BossDef def = upcoming();
        ZonedDateTime next = next();
        if (def == null || next == null) { plugin.send(to, T.t("fight.no-boss-is-scheduled", "<gray>No boss is scheduled.")); return; }
        plugin.send(to, T.t("fight.next-boss-in", "<gold>Next boss: </gold><boss> <gray><title> <gray>in <white><time></white> <dark_gray>(<charat><root> <tolocaltime>)<where>", "boss", def.name(), "title", Text.escape(def.title()), "time", nextText(), "charat", next.getDayOfWeek().toString().charAt(0), "root", next.getDayOfWeek().toString().substring(1).toLowerCase(Locale.ROOT), "tolocaltime", next.toLocalTime(), "where", where(arenaFor())));
    }

    public String upcomingName() {
        BossDef def = upcoming();
        return def == null ? "" : Text.plain(Text.mm(def.name()));
    }

    public String aliveName() {
        Fight live = fights.values().stream().filter(f -> !f.test && f.owner == null).findFirst().orElse(null);
        return live == null ? "" : Text.plain(Text.mm(live.def.name()));
    }

    // ------------------------------------------------------------------ border rod

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void wand(PlayerInteractEvent event) {
        ItemStack item = event.getItem();
        if (item == null || item.getType() != Material.BLAZE_ROD || !item.hasItemMeta()) return;
        String id = item.getItemMeta().getPersistentDataContainer().get(wandKey, PersistentDataType.STRING);
        if (id == null) return;
        event.setCancelled(true);
        if (event.getHand() != EquipmentSlot.HAND) return;
        Player player = event.getPlayer();
        if (!com.cbosses.command.BossCommand.canControl(player)) return;
        Arena a = arena(id, true);
        if (event.getAction() == Action.LEFT_CLICK_BLOCK && event.getClickedBlock() != null) {
            var b = event.getClickedBlock();
            if (a.world != null && !a.world.equals(b.getWorld().getName()) && !a.points().isEmpty()) { plugin.send(player, T.t("fight.the-border-must-be-in", "<red>The border must be in the same world as the arena spawn.")); return; }
            if (a.world == null) a.world = b.getWorld().getName();
            String problem = a.add(b.getX(), b.getZ());
            save();
            int n = a.points().size();
            plugin.send(player, T.t("fight.corner-at", "<green>Corner <n></green> <gray>at <getx>, <getz><problem>", "n", n, "getx", b.getX(), "getz", b.getZ(), "problem", (n < 3 ? ". Add " + (3 - n) + " more." : problem == null ? ". Border saved." : ". <red>" + Text.escape(problem))));
            show(player, a);
        } else if (event.getAction() == Action.RIGHT_CLICK_BLOCK || event.getAction() == Action.RIGHT_CLICK_AIR) {
            if (player.isSneaking()) { show(player, a); plugin.send(player, T.t("fight.arena", "<gray>Arena <white><arena></white>: <border>.", "arena", a.id, "border", a.describe())); return; }
            plugin.send(player, a.undo() ? T.t("fight.removed-the-last-corner", "<yellow>Removed the last corner. <gray><left> left.", "left", a.points().size()) : T.t("fight.no-corners-to-remove", "<gray>No corners to remove."));
            save();
            show(player, a);
        }
    }

    /** Draws the border and spawn to one player for ten seconds. */
    public void show(Player player, Arena a) {
        List<int[]> pts = a.points();
        double y = player.getLocation().getY() + 0.5;
        Particle.DustOptions edge = new Particle.DustOptions(Color.fromRGB(0xff3355), 1.5f);
        Particle.DustOptions spawnDust = new Particle.DustOptions(Color.fromRGB(0xffcc00), 2f);
        int[] runs = {0};
        player.getScheduler().runAtFixedRate(plugin, t -> {
            if (++runs[0] > 10 || !player.isOnline()) { t.cancel(); return; }
            var world = player.getWorld();
            if (pts.size() >= 2) for (int i = 0; i < pts.size(); i++) {
                int[] p1 = pts.get(i), p2 = pts.get((i + 1) % pts.size());
                if (pts.size() == 2 && i == 1) break;
                double dx = p2[0] - p1[0], dz = p2[1] - p1[1];
                int steps = (int) Math.min(200, Math.max(1, Math.sqrt(dx * dx + dz * dz)));
                for (int s = 0; s <= steps; s++)
                    player.spawnParticle(Particle.DUST, new Location(world, p1[0] + 0.5 + dx * s / steps, y, p1[1] + 0.5 + dz * s / steps), 1, edge);
            } else if (pts.isEmpty() && a.spawn() != null) {
                Location c = a.spawn();
                for (int i = 0; i < 90; i++) {
                    double ang = Math.PI * 2 * i / 90;
                    player.spawnParticle(Particle.DUST, new Location(world, c.getX() + Math.cos(ang) * a.radius, y, c.getZ() + Math.sin(ang) * a.radius), 1, edge);
                }
            }
            for (int[] p : pts) player.spawnParticle(Particle.END_ROD, new Location(world, p[0] + 0.5, y + 0.5, p[1] + 0.5), 3, 0, 0.5, 0, 0);
            Location s = a.spawn();
            if (s != null && s.getWorld().equals(world)) player.spawnParticle(Particle.DUST, s.clone().add(0, 1, 0), 20, 0.2, 1, 0.2, 0, spawnDust);
        }, null, 1, 20);
    }

    // ------------------------------------------------------------------ protection

    private String kind(Entity e) {
        return e == null ? null : e.getPersistentDataContainer().get(kindKey, PersistentDataType.STRING);
    }

    private static Entity source(Entity e) {
        if (e instanceof Projectile p && p.getShooter() instanceof Entity shooter) return shooter;
        if (e instanceof EvokerFangs fangs && fangs.getOwner() != null) return fangs.getOwner();
        return e;
    }

    /** WorldGuard (mob-spawning deny, block-plugin-spawning) would cancel the boss and its blocks; they are put back. */
    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void spawnAllowed(EntitySpawnEvent event) {
        if (!event.isCancelled() || kind(event.getEntity()) == null) return;
        if (plugin.getConfig().getBoolean("worldguard.bypass-spawn-blocking", true)) event.setCancelled(false);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void damage(EntityDamageByEntityEvent event) {
        Entity victim = event.getEntity();
        Entity attacker = source(event.getDamager());
        String victimKind = kind(victim), attackerKind = kind(attacker);
        if (attackerKind == null && kind(event.getDamager()) != null) attackerKind = kind(event.getDamager());
        if (attackerKind != null && !(victim instanceof Player)) { event.setCancelled(true); return; }
        if (attackerKind != null && victim instanceof Player p) {
            Fight f = byEntity.get(attacker.getUniqueId());
            if (f != null && !mayHurt(f, p)) { event.setCancelled(true); return; }
        }
        if (victimKind == null) return;
        if ("zone".equals(victimKind)) { event.setCancelled(true); if (attacker instanceof Player p) hitZone(p, victim); return; }
        if ("part".equals(victimKind) || !(attacker instanceof Player player)) { event.setCancelled(true); return; }
        Fight f = byEntity.get(victim.getUniqueId());
        if (f == null) return;
        if (!WorldGuardHook.mayFight(player)) { event.setCancelled(true); player.sendActionBar(Text.mm(T.t("fight.fighting-bosses-is-off-here", "<red>Fighting bosses is off here."))); return; }
        if (f.owner != null && !f.owner.equals(player.getUniqueId()) && !plugin.getConfig().getBoolean("chapter-bosses.allow-helpers", true)) {
            event.setCancelled(true);
            player.sendActionBar(Text.mm(T.t("fight.this-is-someone-else-s", "<red>This is someone else's chapter boss.")));
            return;
        }
        if ("boss".equals(victimKind) && plugin.getConfig().getBoolean("fight.only-hurt-from-inside", true) && !f.arena.contains(player.getLocation())) {
            event.setCancelled(true);
            player.sendActionBar(Text.mm(T.t("fight.step-inside-the-arena-to", "<red>Step inside the arena to hurt <boss>", "boss", f.def.name())));
            return;
        }
        if ("boss".equals(victimKind)) {
            ModelRig.Zone zone = aimed.remove(player.getUniqueId());
            event.setDamage(event.getDamage() / f.ratio * (zone == null ? 1 : zone.mult()));
        }
    }

    private final Map<UUID, ModelRig.Zone> aimed = new ConcurrentHashMap<>();

    /** Nothing about a player who left is kept: their aimed hit zone and their place in boss bars. */
    @EventHandler
    public void quit(org.bukkit.event.player.PlayerQuitEvent event) {
        UUID id = event.getPlayer().getUniqueId();
        aimed.remove(id);
        for (Fight f : fights.values()) f.viewers.remove(id);
    }

    /** A player struck one of the model's hit boxes: it becomes a normal attack on the boss with that part's multiplier. */
    private void hitZone(Player player, Entity box) {
        String key = box.getPersistentDataContainer().get(fightKey, PersistentDataType.STRING);
        Fight f = key == null ? null : fights.get(key);
        if (f == null || f.over || f.model == null || !f.boss.isValid() || !Bukkit.isOwnedByCurrentRegion(f.boss)) return;
        ModelRig.Zone zone = f.model.zone(box);
        if (zone == null) return;
        aimed.put(player.getUniqueId(), zone);
        try { player.attack(f.boss); } finally { aimed.remove(player.getUniqueId()); }
        Location at = box.getLocation().add(0, ((Interaction) box).getInteractionHeight() / 2, 0);
        var world = at.getWorld();
        String label;
        switch (zone.kind()) {
            case "head", "helmet" -> {
                Privacy.particle(world, Particle.CRIT, at, 14, 0.3, 0.3, 0.3, 0.2);
                Privacy.sound(world, at, Sound.ENTITY_PLAYER_ATTACK_CRIT, 1f, 1.1f);
                label = zone.kind().equals("head") ? T.t("fight.head-hit", "<gold>Head hit") : T.t("fight.helmet", "<yellow>Helmet");
            }
            case "weak" -> {
                Privacy.particle(world, Particle.ENCHANTED_HIT, at, 22, 0.3, 0.3, 0.3, 0.3);
                Privacy.sound(world, at, Sound.BLOCK_AMETHYST_BLOCK_BREAK, 1.2f, 1.4f);
                Fx.debris(at, f.theme.shard(), 2, 1, 0.8, 0.2f);
                label = T.t("fight.weak-spot", "<light_purple><bold>Weak spot!");
            }
            case "armor" -> {
                Privacy.particle(world, Particle.ELECTRIC_SPARK, at, 8, 0.2, 0.2, 0.2, 0.1);
                Privacy.sound(world, at, Sound.ITEM_SHIELD_BLOCK, 0.9f, 0.8f);
                label = T.t("fight.armour", "<gray>Armour");
            }
            case "weapon" -> {
                Privacy.particle(world, Particle.ELECTRIC_SPARK, at, 10, 0.2, 0.2, 0.2, 0.15);
                Privacy.sound(world, at, Sound.BLOCK_ANVIL_LAND, 0.35f, 1.8f);
                label = T.t("fight.blocked-by-its-weapon", "<gray>Blocked by its weapon");
            }
            default -> label = "<white>" + zone.kind().substring(0, 1).toUpperCase(Locale.ROOT) + zone.kind().substring(1);
        }
        player.sendActionBar(Text.mm(label + " <dark_gray>x" + (Math.round(zone.mult() * 10) / 10.0)));
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void hitEffect(EntityDamageByEntityEvent event) {
        if (!(event.getEntity() instanceof Player p) || !"boss".equals(kind(event.getDamager()))) return;
        Location at = p.getLocation().add(0, 1, 0);
        Privacy.particle(p.getWorld(), Particle.SWEEP_ATTACK, at, 1);
        Privacy.particle(p.getWorld(), Particle.CRIT, at, 15, 0.3, 0.4, 0.3, 0.3);
        Privacy.sound(p.getWorld(), at, Sound.ENTITY_PLAYER_ATTACK_STRONG, 1f, 0.6f);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void record(EntityDamageByEntityEvent event) {
        if (!"boss".equals(kind(event.getEntity())) || !(source(event.getDamager()) instanceof Player player)) return;
        Fight f = byEntity.get(event.getEntity().getUniqueId());
        if (f == null) return;
        f.damage.merge(player.getUniqueId(), event.getFinalDamage() * f.ratio, Double::sum);
        if (f.model != null) f.model.hurt();
        f.names.put(player.getUniqueId(), player.getName());
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void environment(EntityDamageEvent event) {
        if (event instanceof EntityDamageByEntityEvent) return;
        String k = kind(event.getEntity());
        if (k == null) return;
        if (event.getCause() == EntityDamageEvent.DamageCause.VOID) return;
        String cause = event.getCause().name();
        if (k.equals("part") || !(cause.equals("CUSTOM") || cause.equals("KILL") || cause.equals("MAGIC") || cause.equals("POISON") || cause.equals("WITHER"))) event.setCancelled(true);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void target(EntityTargetLivingEntityEvent event) {
        if (kind(event.getEntity()) != null && event.getTarget() != null && !(event.getTarget() instanceof Player)) event.setCancelled(true);
    }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void death(EntityDeathEvent event) {
        String k = kind(event.getEntity());
        if (k == null) return;
        event.getDrops().clear();
        event.setDroppedExp(0);
        Fight f = byEntity.remove(event.getEntity().getUniqueId());
        if (f != null && "boss".equals(k) && !f.over) {
            Player killer = event.getEntity().getKiller();
            if (killer != null) f.killer = killer.getName();
            victory(f);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void launch(ProjectileLaunchEvent event) {
        if (event.getEntity().getShooter() instanceof Entity shooter && kind(shooter) != null)
            event.getEntity().getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "shot");
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void vex(CreatureSpawnEvent event) {
        if (event.getEntity() instanceof Vex vex && vex.getSummoner() != null && kind(vex.getSummoner()) != null) {
            Fight f = byEntity.get(vex.getSummoner().getUniqueId());
            if (f == null) { event.setCancelled(true); return; }
            vex.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "minion");
            vex.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, f.key);
            vex.setPersistent(false);
            f.minions.add(vex); byEntity.put(vex.getUniqueId(), f);
        }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void blocks(EntityChangeBlockEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void form(EntityBlockFormEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void explode(EntityExplodeEvent event) {
        if (kind(event.getEntity()) != null || kind(source(event.getEntity())) != null) { event.blockList().clear(); event.setYield(0); }
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void prime(ExplosionPrimeEvent event) {
        if (kind(event.getEntity()) == null && kind(source(event.getEntity())) == null) return;
        event.setFire(false);
        if (event.getEntity() instanceof Creeper) event.setCancelled(true);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void ignite(BlockIgniteEvent event) {
        Entity e = event.getIgnitingEntity();
        if (e != null && (kind(e) != null || kind(source(e)) != null)) event.setCancelled(true);
    }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void split(SlimeSplitEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void transform(EntityTransformEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void burn(EntityCombustEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void portal(EntityPortalEvent event) { if (kind(event.getEntity()) != null) event.setCancelled(true); }

    static Map<String, BossDef> sorted(Map<String, BossDef> in) { return new LinkedHashMap<>(in); }

    /** A private boss and its minions never go after anyone but their own player. */
    @org.bukkit.event.EventHandler(ignoreCancelled = true)
    public void privateTarget(org.bukkit.event.entity.EntityTargetLivingEntityEvent event) {
        if (!(event.getTarget() instanceof Player p) || !Privacy.any()) return;
        String key = event.getEntity().getPersistentDataContainer().get(fightKey, PersistentDataType.STRING);
        if (key == null) return;
        Fight f = fights.get(key);
        if (f != null && f.privateZone != null && !p.getUniqueId().equals(f.owner)) event.setCancelled(true);
    }
}
