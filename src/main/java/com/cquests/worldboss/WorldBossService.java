package com.cquests.worldboss;

import com.cquests.CQuestsPlugin;
import com.cquests.util.Sched;
import com.cquests.util.Text;
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
import org.bukkit.entity.AbstractArrow;
import org.bukkit.entity.Ageable;
import org.bukkit.entity.Arrow;
import org.bukkit.entity.Creeper;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EvokerFangs;
import org.bukkit.entity.Hoglin;
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
import org.bukkit.event.entity.CreatureSpawnEvent;
import org.bukkit.event.block.EntityBlockFormEvent;
import org.bukkit.event.entity.EntityChangeBlockEvent;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.EntityExplodeEvent;
import org.bukkit.event.entity.EntityPortalEvent;
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
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Weekly world bosses: big public fights at a spawn point an op sets, inside a border drawn with a
 * stick. A world boss only ever attacks players, never breaks, burns or changes blocks, drops
 * nothing, is never saved into the world and is pulled back whenever it reaches its border.
 * Every fight runs on the boss's own region thread (Folia safe).
 */
public final class WorldBossService implements Listener {

    static final class Fight {
        final String key; final WorldBossDef def; final Arena arena; final boolean test; final UUID tester;
        final Mob boss; final double max; final BossBar bar;
        /** Minecraft caps max health at 1024; bigger bosses take proportionally less damage instead. */
        final double ratio;
        final List<Entity> parts = new CopyOnWriteArrayList<>();
        final List<Mob> minions = new CopyOnWriteArrayList<>();
        final Map<UUID, Double> damage = new ConcurrentHashMap<>();
        final Map<UUID, String> names = new ConcurrentHashMap<>();
        final Set<UUID> viewers = ConcurrentHashMap.newKeySet();
        final long born = System.currentTimeMillis();
        volatile long lastPlayer = System.currentTimeMillis();
        long nextAbility; long nextTitle; boolean raged; int heals; int ticks;
        volatile boolean over;
        int chunkX, chunkZ; String chunkWorld;

        Fight(String key, WorldBossDef def, Arena arena, boolean test, UUID tester, Mob boss, double max, BossBar bar) {
            this.key = key; this.def = def; this.arena = arena; this.test = test; this.tester = tester;
            this.boss = boss; this.max = max; this.bar = bar;
            this.ratio = Math.max(1, def.health() / Math.max(1, max));
        }
    }

    private final CQuestsPlugin plugin;
    private final NamespacedKey kindKey, fightKey, wandKey;
    private final File arenasFile;
    private volatile Map<String, WorldBossDef> defs = Map.of();
    private final Map<String, Arena> arenas = new ConcurrentHashMap<>();
    private final Map<String, Fight> fights = new ConcurrentHashMap<>();
    private final Map<UUID, Fight> byEntity = new ConcurrentHashMap<>();
    private volatile String lastRun = "", lastWarn = "";
    private volatile boolean scheduleOn = true;
    private ScheduledTask timer;

    public WorldBossService(CQuestsPlugin plugin) {
        this.plugin = plugin;
        kindKey = new NamespacedKey(plugin, "worldboss");
        fightKey = new NamespacedKey(plugin, "worldboss_fight");
        wandKey = new NamespacedKey(plugin, "worldboss_wand");
        arenasFile = new File(plugin.getDataFolder(), "worldboss-arenas.yml");
        reload();
    }

    // ------------------------------------------------------------------ setup

    public void reload() {
        defs = WorldBossDef.load(YamlConfiguration.loadConfiguration(new File(plugin.getDataFolder(), "worldbosses.yml")), plugin.getLogger());
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
            for (String point : yaml.getStringList("arenas." + id + ".border")) {
                String[] xz = point.split(",");
                if (xz.length == 2) try { a.points.add(new int[]{Integer.parseInt(xz[0].trim()), Integer.parseInt(xz[1].trim())}); } catch (NumberFormatException ignored) { }
            }
            a.rebuild();
            arenas.put(a.id, a);
        }
        lastRun = yaml.getString("schedule.last-run", "");
        lastWarn = yaml.getString("schedule.last-warn", "");
        scheduleOn = plugin.getConfig().getBoolean("world-bosses.schedule.enabled", true);
    }

    public void start() {
        if (timer != null) timer.cancel();
        timer = Sched.globalTimer(t -> scheduleTick(), 20 * 30, 20 * 30);
    }

    public void shutdown() {
        if (timer != null) timer.cancel();
        for (Fight f : new ArrayList<>(fights.values())) end(f, "shutdown");
    }

    private int radius() { return Math.max(8, plugin.getConfig().getInt("world-bosses.default-radius", 40)); }
    public boolean enabled() { return plugin.getConfig().getBoolean("world-bosses.enabled", true); }
    public Map<String, WorldBossDef> defs() { return defs; }
    public List<String> ids() { return new ArrayList<>(defs.keySet()); }
    public List<String> arenaIds() { return new ArrayList<>(arenas.keySet()); }
    public boolean alive() { return fights.values().stream().anyMatch(f -> !f.test); }

    private synchronized void save() {
        YamlConfiguration yaml = new YamlConfiguration();
        for (Arena a : arenas.values()) {
            String base = "arenas." + a.id + ".";
            if (a.hasSpawn) yaml.set(base + "spawn", a.world + ";" + a.x + ";" + a.y + ";" + a.z);
            yaml.set(base + "radius", a.radius);
            List<String> border = new ArrayList<>();
            for (int[] p : a.points()) border.add(p[0] + "," + p[1]);
            yaml.set(base + "border", border);
        }
        yaml.set("schedule.last-run", lastRun);
        yaml.set("schedule.last-warn", lastWarn);
        String text = yaml.saveToString();
        Sched.async(() -> {
            synchronized (arenasFile) {
                try { java.nio.file.Files.writeString(arenasFile.toPath(), text); }
                catch (IOException e) { plugin.getLogger().warning("Could not save worldboss-arenas.yml: " + e.getMessage()); }
            }
        });
    }

    private Arena arena(String id, boolean create) {
        String key = id.toLowerCase(Locale.ROOT);
        return create ? arenas.computeIfAbsent(key, k -> new Arena(k, radius())) : arenas.get(key);
    }

    // ------------------------------------------------------------------ admin

    public void setSpawn(Player player, String arenaId) {
        Arena a = arena(arenaId, true);
        a.spawn(player.getLocation());
        save();
        plugin.send(player, "<green>World boss spawn for arena <white>" + a.id + "</white> set here. <gray>Border: " + a.describe()
                + ". Use <yellow>/cq worldboss wand " + a.id + "</yellow> to draw the border.");
    }

    public void giveWand(Player player, String arenaId) {
        Arena a = arena(arenaId, true);
        ItemStack stick = new ItemStack(Material.STICK);
        stick.editMeta(meta -> {
            meta.displayName(Text.mm("<gold><bold>Boss Border Stick</bold></gold> <gray>(" + a.id + ")").decoration(net.kyori.adventure.text.format.TextDecoration.ITALIC, false));
            meta.lore(List.of(Text.mm("<yellow>Left-click a block</yellow><gray>: add a corner"), Text.mm("<yellow>Right-click</yellow><gray>: remove the last corner"),
                    Text.mm("<yellow>Sneak + right-click</yellow><gray>: show the border")));
            meta.setEnchantmentGlintOverride(true);
            meta.getPersistentDataContainer().set(wandKey, PersistentDataType.STRING, a.id);
        });
        player.getInventory().addItem(stick).values().forEach(left -> player.getWorld().dropItemNaturally(player.getLocation(), left));
        plugin.send(player, "<gold>Border stick for arena <white>" + a.id + "</white>. <gray>Left-click blocks around the arena to add corners in order. The boss can never walk past this outline.");
    }

    public void clearBorder(Player player, String arenaId) {
        Arena a = arena(arenaId, false);
        if (a == null) { plugin.send(player, "<red>No arena " + Text.escape(arenaId)); return; }
        a.clear(); save();
        plugin.send(player, "<gray>Border cleared. Arena <white>" + a.id + "</white> now uses a circle of " + a.radius + " blocks around its spawn.");
    }

    public void setRadius(Player player, String arenaId, int radius) {
        Arena a = arena(arenaId, true);
        a.radius = Math.max(8, Math.min(500, radius)); save();
        plugin.send(player, "<gray>Arena <white>" + a.id + "</white> circle radius: " + a.radius + " (used when there is no outline).");
    }

    public void listArenas(org.bukkit.command.CommandSender to) {
        if (arenas.isEmpty()) { plugin.send(to, "<yellow>No arenas yet. Stand where the boss should appear and run /cq worldboss setspawn main."); return; }
        for (Arena a : arenas.values()) {
            Location s = a.spawn();
            plugin.send(to, "<white>" + a.id + " <gray>" + (s == null ? "no spawn set" : s.getWorld().getName() + " " + s.getBlockX() + " " + s.getBlockY() + " " + s.getBlockZ())
                    + ", border: " + a.describe() + (fights.containsKey(a.id) ? " <red>(boss alive)" : ""));
        }
    }

    public void listBosses(org.bukkit.command.CommandSender to) {
        plugin.send(to, "<gold>World bosses</gold> <gray>(" + defs.size() + ")");
        for (WorldBossDef d : defs.values())
            to.sendMessage(Text.mm(" <dark_gray>-</dark_gray> <white>" + d.id() + "</white> " + d.name() + " <gray>" + Text.escape(d.title())
                    + (d.seasonal() ? " <light_purple>(" + d.season() + ")" : "")));
    }

    public boolean stop(String arenaId) {
        Fight f = fights.get(arenaId.toLowerCase(Locale.ROOT));
        if (f == null) return false;
        end(f, "stopped"); return true;
    }

    public void stopAll() { for (Fight f : new ArrayList<>(fights.values())) end(f, "stopped"); }

    public void scheduleToggle(org.bukkit.command.CommandSender to, boolean on) {
        scheduleOn = on;
        plugin.getConfig().set("world-bosses.schedule.enabled", on);
        plugin.saveConfig();
        plugin.send(to, "<gray>Weekly world boss: <white>" + (on ? "on" : "off"));
    }

    // ------------------------------------------------------------------ schedule

    private ZoneId zone() {
        String z = plugin.getConfig().getString("world-bosses.schedule.zone", "");
        try { return z == null || z.isBlank() ? ZoneId.systemDefault() : ZoneId.of(z); } catch (RuntimeException e) { return ZoneId.systemDefault(); }
    }

    /** The next scheduled spawn after now, or null when the schedule is off or has no days. */
    public ZonedDateTime next() {
        if (!scheduleOn || !enabled()) return null;
        List<DayOfWeek> days = new ArrayList<>();
        for (String d : plugin.getConfig().getStringList("world-bosses.schedule.days"))
            try { days.add(DayOfWeek.valueOf(d.trim().toUpperCase(Locale.ROOT))); } catch (IllegalArgumentException ignored) { }
        if (days.isEmpty()) return null;
        LocalTime time;
        try { time = LocalTime.parse(plugin.getConfig().getString("world-bosses.schedule.time", "20:00")); } catch (RuntimeException e) { time = LocalTime.of(20, 0); }
        return nextAfter(ZonedDateTime.now(zone()), days, time, lastRun);
    }

    /** First day/time slot at or after {@code now} that has not run yet. Static for tests. */
    static ZonedDateTime nextAfter(ZonedDateTime now, List<DayOfWeek> days, LocalTime time, String lastRun) {
        for (int i = 0; i <= 14; i++) {
            LocalDate date = now.toLocalDate().plusDays(i);
            if (!days.contains(date.getDayOfWeek()) || date.toString().equals(lastRun)) continue;
            ZonedDateTime slot = date.atTime(time).atZone(now.getZone());
            if (i == 0 && slot.isBefore(now.minusHours(1))) continue; // missed by more than an hour: wait for the next one
            return slot;
        }
        return null;
    }

    /** The boss that the next scheduled spawn brings: a seasonal one while its season is on, otherwise the weekly rotation. */
    public WorldBossDef upcoming() {
        List<WorldBossDef> seasonal = new ArrayList<>();
        List<WorldBossDef> normal = new ArrayList<>();
        for (WorldBossDef d : defs.values()) {
            if (!d.seasonal()) normal.add(d);
            else if (plugin.seasons() != null && plugin.seasons().active(d.season())) seasonal.add(d);
        }
        long week = LocalDate.now(zone()).toEpochDay() / 7;
        if (!seasonal.isEmpty()) return seasonal.get((int) (week % seasonal.size()));
        if (normal.isEmpty()) return null;
        if ("random".equalsIgnoreCase(plugin.getConfig().getString("world-bosses.schedule.order", "rotate")))
            return normal.get(new java.util.Random(week * 7919L).nextInt(normal.size()));
        return normal.get((int) (week % normal.size()));
    }

    private void scheduleTick() {
        ZonedDateTime slot = next();
        if (slot == null) return;
        ZonedDateTime now = ZonedDateTime.now(zone());
        String date = slot.toLocalDate().toString();
        int warn = Math.max(0, plugin.getConfig().getInt("world-bosses.schedule.warn-minutes", 10));
        WorldBossDef def = upcoming();
        if (def == null) return;
        if (warn > 0 && !date.equals(lastWarn) && now.isAfter(slot.minusMinutes(warn)) && now.isBefore(slot)) {
            lastWarn = date; save();
            broadcast("<gold><bold>⚔ WORLD BOSS</bold></gold> " + def.name() + " <gray>wakes in <white>" + warn + " minutes</white>" + where(arenaFor()));
        }
        if (!now.isBefore(slot)) {
            lastRun = date; save();
            Arena a = arenaFor();
            if (a == null || a.spawn() == null) {
                plugin.getLogger().info("Weekly world boss skipped: set a spawn with /cq worldboss setspawn " + plugin.getConfig().getString("world-bosses.schedule.arena", "main"));
                return;
            }
            spawn(def, a, null, false);
        }
    }

    public Arena arenaFor(String id) { return arena(id, false); }

    private Arena arenaFor() { return arena(plugin.getConfig().getString("world-bosses.schedule.arena", "main"), false); }

    private String where(Arena a) {
        Location s = a == null ? null : a.spawn();
        return s == null ? "." : " <gray>at <white>" + s.getBlockX() + ", " + s.getBlockZ() + "</white> (" + s.getWorld().getName() + ").";
    }

    // ------------------------------------------------------------------ spawning

    /** Starts a fight. {@code tester} non-null makes it a test: at the tester, nothing is paid, and the tester is told why if it fails. */
    public boolean spawn(WorldBossDef def, Arena arena, Player tester, boolean test) {
        if (!enabled()) { if (tester != null) plugin.send(tester, "<yellow>World bosses are off (world-bosses.enabled)."); return false; }
        String key = test ? "test:" + tester.getUniqueId() : arena.id;
        Fight old = fights.get(key);
        if (old != null) { if (!test) { if (tester != null) plugin.send(tester, "<yellow>A boss is already alive in " + arena.id + ". /cq worldboss stop " + arena.id); return false; } end(old, "stopped"); }
        if (fights.size() >= Math.max(1, plugin.getConfig().getInt("world-bosses.max-active", 4))) {
            if (tester != null) plugin.send(tester, "<yellow>Too many world bosses are alive at once."); return false;
        }
        Location at = arena.spawn();
        if (at == null) { if (tester != null) plugin.send(tester, "<yellow>Arena " + arena.id + " has no spawn. /cq worldboss setspawn " + arena.id); return false; }
        if (at.getWorld().getDifficulty() == org.bukkit.Difficulty.PEACEFUL) { if (tester != null) plugin.send(tester, "<yellow>Bosses cannot appear in a Peaceful world."); return false; }
        Sched.at(at, () -> doSpawn(def, arena, key, at, tester, test));
        return true;
    }

    public boolean spawnAt(Player player, String bossId, String arenaId) {
        WorldBossDef def = defs.get(bossId.toLowerCase(Locale.ROOT));
        if (def == null) { plugin.send(player, "<red>No world boss " + Text.escape(bossId) + ". <gray>/cq worldboss list"); return false; }
        Arena a = arena(arenaId, false);
        if (a == null) { plugin.send(player, "<red>No arena " + Text.escape(arenaId) + ". <gray>/cq worldboss setspawn " + Text.escape(arenaId)); return false; }
        return spawn(def, a, player, false);
    }

    /** /cq test worldboss: the boss appears a few blocks in front of you inside a 25 block circle; nothing is paid. */
    public boolean test(Player player, String bossId) {
        WorldBossDef def = bossId == null || bossId.isBlank() ? null : defs.get(bossId.toLowerCase(Locale.ROOT));
        if (def == null) { plugin.send(player, "<yellow>/cq test worldboss <boss></yellow> <gray>Bosses: <white>" + String.join(", ", defs.keySet())); return false; }
        Arena a = new Arena("test-" + player.getName().toLowerCase(Locale.ROOT), 25);
        Vector look = player.getLocation().getDirection().setY(0);
        if (look.lengthSquared() < 0.01) look = new Vector(1, 0, 0);
        Location front = player.getLocation().clone().add(look.normalize().multiply(6));
        front.setY(player.getLocation().getY());
        a.spawn(front);
        return spawn(def, a, player, true);
    }

    public boolean testStop(Player player) {
        Fight f = fights.get("test:" + player.getUniqueId());
        if (f == null) return false;
        end(f, "stopped"); return true;
    }

    public boolean testPhase(Player player) {
        Fight f = fights.get("test:" + player.getUniqueId());
        if (f == null) return false;
        Sched.entity(f.boss, () -> { if (f.boss.isValid()) f.boss.setHealth(Math.max(1, f.max * 0.49)); });
        return true;
    }

    private void doSpawn(WorldBossDef def, Arena arena, String key, Location at, Player tester, boolean test) {
        Mob mob;
        try {
            mob = (Mob) at.getWorld().spawn(at, def.entity().getEntityClass(), e -> dress((Mob) e, def, key));
        } catch (RuntimeException e) {
            if (tester != null) plugin.send(tester, "<yellow>" + def.name() + " <yellow>could not appear here: " + Text.escape(String.valueOf(e.getMessage())));
            return;
        }
        if (!mob.isValid()) { if (tester != null) plugin.send(tester, "<yellow>Something stopped the boss from appearing (another plugin or a protected area)."); return; }
        double max = maxHealth(mob);
        BossBar bar = BossBar.bossBar(Text.mm(def.name()), 1f, barColor(def.bar()), BossBar.Overlay.NOTCHED_20);
        Fight fight = new Fight(key, def, arena, test, tester == null ? null : tester.getUniqueId(), mob, max, bar);
        fight.nextAbility = System.currentTimeMillis() + 6000;
        fights.put(key, fight);
        byEntity.put(mob.getUniqueId(), fight);
        fight.chunkWorld = at.getWorld().getName(); fight.chunkX = at.getBlockX() >> 4; fight.chunkZ = at.getBlockZ() >> 4;
        at.getWorld().addPluginChunkTicket(fight.chunkX, fight.chunkZ, plugin);
        if (def.mount() != null) try {
            Entity mount = at.getWorld().spawn(at, def.mount().getEntityClass(), e -> part(e, key));
            mount.addPassenger(mob); fight.parts.add(mount); byEntity.put(mount.getUniqueId(), fight);
        } catch (RuntimeException ignored) { }
        if (def.rider() != null) try {
            Entity rider = at.getWorld().spawn(at, def.rider().getEntityClass(), e -> part(e, key));
            mob.addPassenger(rider); fight.parts.add(rider); byEntity.put(rider.getUniqueId(), fight);
        } catch (RuntimeException ignored) { }
        at.getWorld().strikeLightningEffect(at);
        at.getWorld().spawnParticle(Particle.EXPLOSION_EMITTER, at.clone().add(0, 1, 0), 2);
        mob.getScheduler().runAtFixedRate(plugin, t -> { if (!tick(fight)) t.cancel(); }, () -> end(fight, "gone"), 2, 10);
        if (test) {
            plugin.send(tester, "<gray>Test world boss: " + def.name() + " <gray>(" + def.id() + "). Nothing is paid. <yellow>/cq test worldbossphase</yellow> jumps to rage, <yellow>/cq test worldbossstop</yellow> ends it.");
        } else {
            broadcast("<gold><bold>⚔ WORLD BOSS</bold></gold> " + def.name() + (def.title().isBlank() ? "" : " <gray>" + Text.escape(def.title())) + " <gold>has risen" + where(arena)
                    + " <gray>Everyone who helps gets a reward.");
            Sched.global(() -> { for (Player p : Bukkit.getOnlinePlayers()) Sched.entity(p, () -> p.playSound(p.getLocation(), Sound.ENTITY_WITHER_SPAWN, 0.5f, 0.8f)); });
        }
    }

    private void dress(Mob m, WorldBossDef def, String key) {
        m.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "boss");
        m.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, key);
        m.setPersistent(false); m.setRemoveWhenFarAway(false); m.setCanPickupItems(false);
        m.customName(Text.mm(def.name())); m.setCustomNameVisible(true); m.setGlowing(def.glow());
        if (m instanceof Ageable a) a.setAdult();
        if (m instanceof PiglinAbstract p) p.setImmuneToZombification(true);
        if (m instanceof Hoglin h) h.setImmuneToZombification(true);
        if (m instanceof Creeper c) { c.setPowered(true); c.setMaxFuseTicks(Integer.MAX_VALUE / 4); }
        if (m instanceof Slime s) s.setSize(def.size());
        if (m instanceof Wolf w) w.setAngry(true);
        if (m instanceof Rabbit r) r.setRabbitType(Rabbit.Type.THE_KILLER_BUNNY);
        attr(m, "max_health", Math.min(1024, def.health()));
        m.setHealth(Math.max(1, Math.min(1024, def.health())));
        if (!(m instanceof Slime)) attr(m, "scale", def.scale());
        if (def.damage() > 0) attr(m, "attack_damage", def.damage());
        if (def.speed() > 0) attr(m, "movement_speed", def.speed());
        if (def.armor() > 0) attr(m, "armor", def.armor());
        attr(m, "knockback_resistance", 0.8);
        attr(m, "follow_range", 48);
        EntityEquipment eq = m.getEquipment();
        if (eq != null) for (var entry : def.equipment().entrySet()) {
            Material material = Material.matchMaterial(entry.getValue());
            if (material == null) continue;
            ItemStack item = new ItemStack(material);
            item.editMeta(meta -> {
                meta.setEnchantmentGlintOverride(true);
                if (meta instanceof LeatherArmorMeta leather) leather.setColor(color(def.color()));
            });
            EquipmentSlot slot = switch (entry.getKey()) {
                case "head" -> EquipmentSlot.HEAD; case "chest" -> EquipmentSlot.CHEST; case "legs" -> EquipmentSlot.LEGS;
                case "feet" -> EquipmentSlot.FEET; case "offhand" -> EquipmentSlot.OFF_HAND; default -> EquipmentSlot.HAND;
            };
            eq.setItem(slot, item);
            eq.setDropChance(slot, 0f);
        }
    }

    private void part(Entity e, String key) {
        e.getPersistentDataContainer().set(kindKey, PersistentDataType.STRING, "part");
        e.getPersistentDataContainer().set(fightKey, PersistentDataType.STRING, key);
        e.setPersistent(false); e.setInvulnerable(true);
        if (e instanceof Mob m) { m.setRemoveWhenFarAway(false); m.setCanPickupItems(false); if (m instanceof Ageable a) a.setAdult(); }
        if (e instanceof PiglinAbstract p) p.setImmuneToZombification(true);
    }

    private static Attribute attribute(String name) {
        Attribute a = Registry.ATTRIBUTE.get(NamespacedKey.minecraft(name));
        return a != null ? a : Registry.ATTRIBUTE.get(NamespacedKey.minecraft("generic." + name));
    }

    private static void attr(LivingEntity e, String name, double value) {
        Attribute a = attribute(name);
        var instance = a == null ? null : e.getAttribute(a);
        if (instance != null) instance.setBaseValue(value);
    }

    private static double maxHealth(LivingEntity e) {
        Attribute a = attribute("max_health");
        var instance = a == null ? null : e.getAttribute(a);
        return instance == null ? Math.max(1, e.getHealth()) : instance.getValue();
    }

    private static Color color(String hex) {
        try { return Color.fromRGB(Integer.parseInt(hex.replace("#", ""), 16) & 0xFFFFFF); } catch (RuntimeException e) { return Color.RED; }
    }

    private static BossBar.Color barColor(String name) {
        try { return BossBar.Color.valueOf(name); } catch (IllegalArgumentException e) { return BossBar.Color.RED; }
    }

    // ------------------------------------------------------------------ fight loop

    private static boolean fighter(Player p) {
        return p.isOnline() && !p.isDead() && (p.getGameMode() == GameMode.SURVIVAL || p.getGameMode() == GameMode.ADVENTURE);
    }

    private List<Player> near(Fight f, double radius, boolean inside) {
        List<Player> out = new ArrayList<>();
        for (Player p : f.boss.getLocation().getNearbyPlayers(radius))
            if (fighter(p) && Bukkit.isOwnedByCurrentRegion(p) && (!inside || f.arena.contains(p.getLocation()))) out.add(p);
        return out;
    }

    /** Runs every half second on the boss's region thread. False ends the timer. */
    private boolean tick(Fight f) {
        Mob boss = f.boss;
        if (f.over) return false;
        if (!boss.isValid()) { end(f, "gone"); return false; }
        long now = System.currentTimeMillis();
        f.ticks++;
        // The border: anything past it is pulled straight back to the spawn.
        Entity root = boss.getVehicle() != null ? boss.getVehicle() : boss;
        if (!f.arena.contains(boss.getLocation())) {
            Location home = f.arena.spawn();
            if (home != null) {
                boss.setTarget(null);
                root.teleportAsync(home, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                boss.getWorld().spawnParticle(Particle.REVERSE_PORTAL, boss.getLocation().add(0, 1, 0), 40, 0.5, 1, 0.5, 0.1);
            }
            return true;
        }
        // Boss bar for everyone close by.
        List<Player> close = near(f, 56, false);
        Set<UUID> seen = new java.util.HashSet<>();
        for (Player p : close) {
            seen.add(p.getUniqueId());
            if (f.viewers.add(p.getUniqueId())) p.showBossBar(f.bar);
        }
        for (UUID id : new ArrayList<>(f.viewers)) if (!seen.contains(id)) {
            f.viewers.remove(id);
            Player p = Bukkit.getPlayer(id);
            if (p != null) p.hideBossBar(f.bar);
        }
        double health = boss.getHealth();
        f.bar.progress((float) Math.max(0, Math.min(1, health / Math.max(1, f.max))));
        f.bar.name(Text.mm(f.def.name() + " <gray>❤ <white>" + String.format(Locale.ROOT, "%,d", Math.round(health * f.ratio)) + "<gray>/" + String.format(Locale.ROOT, "%,d", Math.round(f.max * f.ratio))));
        // Aura.
        aura(f);
        // Target the closest player inside the border; walk home when there is nobody.
        List<Player> inside = near(f, 40, true);
        if (!inside.isEmpty()) {
            f.lastPlayer = now;
            Player target = inside.stream().min(Comparator.comparingDouble(p -> p.getLocation().distanceSquared(boss.getLocation()))).orElseThrow();
            if (boss.getTarget() == null || !(boss.getTarget() instanceof Player current) || !inside.contains(current)) boss.setTarget(target);
            for (Mob minion : f.minions) {
                if (!minion.isValid()) { f.minions.remove(minion); byEntity.remove(minion.getUniqueId()); continue; }
                if (Bukkit.isOwnedByCurrentRegion(minion) && minion.getTarget() == null) minion.setTarget(target);
            }
            for (Entity part : f.parts) if (part instanceof Mob m && Bukkit.isOwnedByCurrentRegion(m)) m.setTarget(target);
        } else {
            boss.setTarget(null);
            Location home = f.arena.spawn();
            if (home != null && f.ticks % 10 == 0 && home.distanceSquared(boss.getLocation()) > 16) boss.getPathfinder().moveTo(home);
        }
        // Rage at half health.
        if (!f.raged && health <= f.max / 2) {
            f.raged = true;
            f.bar.color(BossBar.Color.PURPLE);
            attr(boss, "movement_speed", Math.max(0.25, (f.def.speed() > 0 ? f.def.speed() : 0.25) * 1.25));
            for (Player p : close) {
                p.showTitle(Title.title(Text.mm(f.def.name()), Text.mm("<red><bold>is enraged!")));
                p.playSound(p.getLocation(), Sound.ENTITY_ENDER_DRAGON_GROWL, 0.8f, 0.7f);
            }
            if (f.def.minion() != null) summonMinions(f, f.def.minions());
        }
        if (!inside.isEmpty() && now >= f.nextAbility && !f.def.abilities().isEmpty()) {
            String ability = f.def.abilities().get(ThreadLocalRandom.current().nextInt(f.def.abilities().size()));
            ability(f, ability, inside);
            f.nextAbility = now + (long) (f.def.abilitySeconds() * (f.raged ? 650 : 1000));
        }
        // Leaves when nobody is around, and after the time limit.
        int idle = Math.max(1, plugin.getConfig().getInt("world-bosses.idle-minutes", 5));
        int maxMinutes = Math.max(2, plugin.getConfig().getInt("world-bosses.max-minutes", 30));
        if (now - f.lastPlayer > idle * 60_000L) { end(f, "idle"); return false; }
        if (now - f.born > maxMinutes * 60_000L) { end(f, "time"); return false; }
        return true;
    }

    private void aura(Fight f) {
        Location at = f.boss.getLocation().add(0, f.boss.getHeight() / 2, 0);
        double w = Math.max(0.4, f.boss.getWidth() / 1.5), h = Math.max(0.5, f.boss.getHeight() / 2);
        Particle particle;
        try { particle = Particle.valueOf(f.def.particle()); } catch (IllegalArgumentException e) { particle = Particle.FLAME; }
        if (particle.getDataType() == Particle.DustOptions.class) at.getWorld().spawnParticle(particle, at, 14, w, h, w, 0, new Particle.DustOptions(color(f.def.color()), 1.6f));
        else if (particle.getDataType() == Void.class) at.getWorld().spawnParticle(particle, at, 10, w, h, w, 0.02);
        else at.getWorld().spawnParticle(Particle.FLAME, at, 10, w, h, w, 0.02);
        if (f.ticks % 4 == 0) {
            // A slow ring on the ground around the boss.
            Particle.DustOptions dust = new Particle.DustOptions(color(f.def.color()), 1.2f);
            Location base = f.boss.getLocation().add(0, 0.15, 0);
            double r = Math.max(1.5, f.boss.getWidth() * 1.3);
            for (int i = 0; i < 24; i++) {
                double a = Math.PI * 2 * i / 24 + f.ticks * 0.1;
                base.getWorld().spawnParticle(Particle.DUST, base.clone().add(Math.cos(a) * r, 0, Math.sin(a) * r), 1, dust);
            }
        }
    }

    private PotionEffectType effect(String name) {
        return Registry.EFFECT.get(NamespacedKey.minecraft(name));
    }

    private void effect(Player p, String name, int ticks, int level) {
        PotionEffectType type = effect(name);
        if (type != null) p.addPotionEffect(new PotionEffect(type, ticks, level));
    }

    private void ability(Fight f, String ability, List<Player> targets) {
        Mob boss = f.boss;
        Location at = boss.getLocation();
        var world = at.getWorld();
        Player main = boss.getTarget() instanceof Player p && targets.contains(p) ? p : targets.get(0);
        switch (ability) {
            case "lightning" -> {
                for (Player p : targets.subList(0, Math.min(4, targets.size()))) {
                    world.strikeLightningEffect(p.getLocation());
                    p.damage(4 + (f.raged ? 2 : 0), boss);
                }
            }
            case "shockwave" -> {
                world.playSound(at, Sound.ENTITY_GENERIC_EXPLODE, 1f, 0.6f);
                for (int i = 0; i < 48; i++) {
                    double a = Math.PI * 2 * i / 48;
                    for (double r = 2; r <= 8; r += 2) world.spawnParticle(Particle.SWEEP_ATTACK, at.clone().add(Math.cos(a) * r, 0.3, Math.sin(a) * r), 1);
                }
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 64) {
                    p.damage(3, boss);
                    p.setVelocity(p.getLocation().toVector().subtract(at.toVector()).setY(0).normalize().multiply(1.4).setY(0.6));
                }
            }
            case "minions" -> summonMinions(f, Math.max(1, f.def.minions() / 2));
            case "fire_ring" -> {
                world.playSound(at, Sound.ITEM_FIRECHARGE_USE, 1f, 0.7f);
                for (int i = 0; i < 60; i++) {
                    double a = Math.PI * 2 * i / 60;
                    world.spawnParticle(Particle.FLAME, at.clone().add(Math.cos(a) * 6, 0.2, Math.sin(a) * 6), 2, 0.1, 0.3, 0.1, 0.01);
                }
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 49) { p.setFireTicks(80); p.damage(2, boss); }
            }
            case "pull" -> {
                world.playSound(at, Sound.ENTITY_EVOKER_PREPARE_SUMMON, 1f, 0.6f);
                for (Player p : targets) {
                    Vector v = at.toVector().subtract(p.getLocation().toVector());
                    if (v.lengthSquared() < 9) continue;
                    p.setVelocity(v.normalize().multiply(1.3).setY(0.35));
                    world.spawnParticle(Particle.PORTAL, p.getLocation().add(0, 1, 0), 30, 0.3, 0.6, 0.3, 0.5);
                }
            }
            case "leap" -> {
                Vector v = main.getLocation().toVector().subtract(at.toVector());
                if (v.lengthSquared() > 1) {
                    (boss.getVehicle() != null ? boss.getVehicle() : boss).setVelocity(v.normalize().multiply(1.2).setY(0.7));
                    world.playSound(at, Sound.ENTITY_RAVAGER_ROAR, 1f, 1.2f);
                    world.spawnParticle(Particle.CLOUD, at, 30, 0.6, 0.2, 0.6, 0.05);
                }
            }
            case "poison" -> {
                world.playSound(at, Sound.ENTITY_SPIDER_AMBIENT, 1f, 0.5f);
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 100) {
                    effect(p, "poison", 80, f.raged ? 1 : 0);
                    world.spawnParticle(Particle.DUST, p.getLocation().add(0, 1, 0), 30, 0.6, 0.6, 0.6, 0, new Particle.DustOptions(Color.fromRGB(0x55aa22), 1.4f));
                }
            }
            case "blink" -> {
                Vector facing = main.getLocation().getDirection().setY(0);
                if (facing.lengthSquared() < 0.01) facing = new Vector(1, 0, 0);
                Location behind = main.getLocation().clone().subtract(facing.normalize().multiply(2));
                behind.setY(main.getLocation().getY());
                if (f.arena.contains(behind) && Bukkit.isOwnedByCurrentRegion(behind) && behind.getBlock().isPassable() && behind.clone().add(0, 1, 0).getBlock().isPassable()) {
                    world.spawnParticle(Particle.REVERSE_PORTAL, at.clone().add(0, 1, 0), 60, 0.5, 1, 0.5, 0.2);
                    (boss.getVehicle() != null ? boss.getVehicle() : boss).teleportAsync(behind, PlayerTeleportEvent.TeleportCause.PLUGIN, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                    world.playSound(behind, Sound.ENTITY_ENDERMAN_TELEPORT, 1f, 0.6f);
                }
            }
            case "frost" -> {
                world.playSound(at, Sound.BLOCK_GLASS_BREAK, 1f, 0.5f);
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 144) {
                    effect(p, "slowness", 80, 2);
                    p.setFreezeTicks(Math.min(p.getMaxFreezeTicks() + 60, 200));
                    world.spawnParticle(Particle.SNOWFLAKE, p.getLocation().add(0, 1, 0), 40, 0.5, 0.8, 0.5, 0.02);
                }
            }
            case "volley" -> {
                world.playSound(at, Sound.ENTITY_SKELETON_SHOOT, 1f, 0.6f);
                for (Player p : targets.subList(0, Math.min(5, targets.size()))) {
                    Location eye = boss.getEyeLocation();
                    Vector dir = p.getEyeLocation().toVector().subtract(eye.toVector()).normalize();
                    for (int i = 0; i < 3; i++) {
                        Arrow arrow = boss.launchProjectile(Arrow.class, dir.clone().multiply(1.8).add(new Vector(ThreadLocalRandom.current().nextGaussian() * 0.05, 0.05, ThreadLocalRandom.current().nextGaussian() * 0.05)));
                        arrow.setPickupStatus(AbstractArrow.PickupStatus.DISALLOWED);
                        arrow.setPersistent(false);
                    }
                }
            }
            case "darkness" -> {
                world.playSound(at, Sound.ENTITY_WARDEN_SONIC_CHARGE, 1f, 0.8f);
                for (Player p : targets) effect(p, "darkness", 120, 0);
            }
            case "levitate" -> {
                world.playSound(at, Sound.ENTITY_SHULKER_SHOOT, 1f, 0.6f);
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 100) effect(p, "levitation", 40, 0);
            }
            case "heal" -> {
                if (f.heals < 2 && boss.getHealth() < f.max * 0.35) {
                    f.heals++;
                    boss.setHealth(Math.min(f.max, boss.getHealth() + f.max * 0.12));
                    world.spawnParticle(Particle.HAPPY_VILLAGER, at.clone().add(0, boss.getHeight() / 2, 0), 60, 1, 1, 1, 0.1);
                    world.playSound(at, Sound.BLOCK_BEACON_POWER_SELECT, 1f, 0.8f);
                    for (Player p : targets) p.sendActionBar(Text.mm(f.def.name() + " <green>heals itself!"));
                } else ability(f, "shockwave", targets);
            }
            case "quake" -> {
                world.playSound(at, Sound.ENTITY_IRON_GOLEM_HURT, 1f, 0.4f);
                world.spawnParticle(Particle.EXPLOSION, at, 6, 3, 0.2, 3, 0);
                for (Player p : targets) if (p.getLocation().distanceSquared(at) <= 100 && p.isOnGround()) {
                    p.damage(4, boss); effect(p, "slowness", 40, 1);
                    p.setVelocity(new Vector(0, 0.6, 0));
                }
            }
            case "detonate" -> {
                world.playSound(at, Sound.ENTITY_CREEPER_PRIMED, 1.5f, 0.5f);
                Sched.entityLater(boss, 30, () -> {
                    if (!boss.isValid() || f.over) return;
                    Location here = boss.getLocation();
                    here.getWorld().spawnParticle(Particle.EXPLOSION_EMITTER, here, 1);
                    here.getWorld().playSound(here, Sound.ENTITY_GENERIC_EXPLODE, 1.5f, 0.8f);
                    for (Player p : here.getNearbyPlayers(7)) if (fighter(p) && Bukkit.isOwnedByCurrentRegion(p)) {
                        p.damage(7, boss);
                        p.setVelocity(p.getLocation().toVector().subtract(here.toVector()).setY(0).normalize().multiply(1.6).setY(0.8));
                    }
                });
            }
            default -> { // roar
                world.playSound(at, Sound.ENTITY_WARDEN_ROAR, 1.2f, 0.8f);
                for (Player p : targets) effect(p, "weakness", 100, 0);
            }
        }
    }

    private void summonMinions(Fight f, int count) {
        if (f.def.minion() == null) return;
        int alive = 0;
        for (Mob m : f.minions) if (m.isValid()) alive++;
        Location at = f.boss.getLocation();
        for (int i = 0; i < count && alive < 8; i++) {
            Location spot = at.clone().add(ThreadLocalRandom.current().nextInt(-4, 5), 0, ThreadLocalRandom.current().nextInt(-4, 5));
            if (!Bukkit.isOwnedByCurrentRegion(spot) || !f.arena.contains(spot) || !spot.getBlock().isPassable() || !spot.clone().add(0, 1, 0).getBlock().isPassable()) continue;
            try {
                Entity e = spot.getWorld().spawn(spot, f.def.minion().getEntityClass(), m -> {
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
                spot.getWorld().spawnParticle(Particle.LARGE_SMOKE, spot.clone().add(0, 0.5, 0), 15, 0.3, 0.5, 0.3, 0.02);
            } catch (RuntimeException ignored) { }
        }
    }

    // ------------------------------------------------------------------ ending

    private void end(Fight f, String reason) {
        if (f.over) return;
        f.over = true;
        fights.remove(f.key, f);
        byEntity.remove(f.boss.getUniqueId());
        for (UUID id : f.viewers) { Player p = Bukkit.getPlayer(id); if (p != null) p.hideBossBar(f.bar); }
        f.viewers.clear();
        List<Entity> leftovers = new ArrayList<>(f.parts);
        leftovers.addAll(f.minions);
        if (!reason.equals("defeated")) leftovers.add(f.boss);
        for (Entity e : leftovers) {
            byEntity.remove(e.getUniqueId());
            if (!e.isValid()) continue;
            if (Bukkit.isOwnedByCurrentRegion(e)) e.remove(); else Sched.entity(e, e::remove);
        }
        var world = Bukkit.getWorld(f.chunkWorld == null ? "" : f.chunkWorld);
        if (world != null) {
            Location chunk = new Location(world, f.chunkX * 16 + 8, 64, f.chunkZ * 16 + 8);
            Runnable unticket = () -> world.removePluginChunkTicket(f.chunkX, f.chunkZ, plugin);
            if (Bukkit.isOwnedByCurrentRegion(chunk)) unticket.run(); else Sched.at(chunk, unticket);
        }
        if (f.test) {
            Player tester = f.tester == null ? null : Bukkit.getPlayer(f.tester);
            if (tester != null && !reason.equals("shutdown")) plugin.send(tester, "<gray>Test world boss ended (" + reason + ").");
            return;
        }
        switch (reason) {
            case "idle" -> broadcast("<gray>" + f.def.name() + " <gray>found no challengers and left.");
            case "time" -> broadcast("<gray>" + f.def.name() + " <gray>was not beaten in time and vanished.");
            case "stopped" -> broadcast("<gray>" + f.def.name() + " <gray>was sent away.");
            default -> { }
        }
    }

    private void victory(Fight f) {
        List<Map.Entry<UUID, Double>> ranked = new ArrayList<>(f.damage.entrySet());
        ranked.sort(Map.Entry.<UUID, Double>comparingByValue().reversed());
        end(f, "defeated");
        Location at = f.boss.getLocation();
        at.getWorld().spawnParticle(Particle.TOTEM_OF_UNDYING, at.clone().add(0, 1, 0), 150, 1.5, 1.5, 1.5, 0.4);
        at.getWorld().playSound(at, Sound.UI_TOAST_CHALLENGE_COMPLETE, 2f, 1f);
        if (f.test) {
            Player tester = f.tester == null ? null : Bukkit.getPlayer(f.tester);
            if (tester != null) plugin.send(tester, "<green>Test boss beaten. <gray>Top damage: " + top(f, ranked));
            return;
        }
        double minimum = f.max * f.ratio * Math.max(0, plugin.getConfig().getDouble("world-bosses.min-damage-percent", 2)) / 100.0;
        WorldBossDef.Rewards r = f.def.rewards();
        int place = 0;
        for (var entry : ranked) {
            place++;
            if (entry.getValue() < minimum) continue;
            boolean topThree = place <= 3;
            String name = f.names.getOrDefault(entry.getKey(), "?");
            long money = r.money() + (topThree ? r.topMoney() / place : 0);
            String moneyCommand = plugin.settings().moneyCommand;
            if (money > 0 && moneyCommand != null && !moneyCommand.isBlank()) {
                String command = moneyCommand.replace("%player%", name).replace("%amount%", Long.toString(money));
                Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
            }
            List<String> commands = new ArrayList<>(r.commands());
            if (place == 1) commands.addAll(r.topCommands());
            for (String raw : commands) {
                String command = raw.replace("%player%", name).replace("<player>", name);
                Sched.global(() -> Bukkit.dispatchCommand(Bukkit.getConsoleSender(), command.startsWith("/") ? command.substring(1) : command));
            }
            Player p = Bukkit.getPlayer(entry.getKey());
            if (p == null) continue;
            List<String> items = new ArrayList<>(r.items());
            if (topThree) items.addAll(r.topItems());
            final int rank = place; final long paid = money;
            Sched.entity(p, () -> {
                for (String line : items) {
                    String[] parts = line.trim().split("\\s+");
                    Material m = Material.matchMaterial(parts[0]);
                    int amount = 1;
                    try { if (parts.length > 1) amount = Math.max(1, Math.min(64, Integer.parseInt(parts[1]))); } catch (NumberFormatException ignored) { }
                    if (m != null && m.isItem()) p.getInventory().addItem(new ItemStack(m, amount)).values().forEach(left -> p.getWorld().dropItemNaturally(p.getLocation(), left));
                }
                p.showTitle(Title.title(Text.mm("<gold><bold>VICTORY"), Text.mm(f.def.name() + " <gray>is defeated. You placed <white>#" + rank)));
                plugin.send(p, "<gold>World boss reward: <white>#" + rank + "</white> in damage" + (paid > 0 ? ", <green>+" + String.format(Locale.ROOT, "%,d", paid) + "</green> money" : "") + (items.isEmpty() ? "" : ", plus items") + ".");
            });
        }
        broadcast("<gold><bold>⚔ WORLD BOSS DEFEATED</bold></gold> " + f.def.name() + " <gray>has fallen! Top damage: " + top(f, ranked));
        if (!ranked.isEmpty() && plugin.discord() != null) {
            Player best = Bukkit.getPlayer(ranked.get(0).getKey());
            if (best != null) plugin.discord().bossDefeated(best, Text.plain(Text.mm(f.def.name())) + " (world boss)");
        }
    }

    private String top(Fight f, List<Map.Entry<UUID, Double>> ranked) {
        List<String> names = new ArrayList<>();
        for (int i = 0; i < Math.min(3, ranked.size()); i++)
            names.add("<white>" + Text.escape(f.names.getOrDefault(ranked.get(i).getKey(), "?")) + "</white> <gray>(" + Math.round(ranked.get(i).getValue()) + ")");
        return names.isEmpty() ? "<gray>nobody" : String.join("<gray>, ", names);
    }

    private void broadcast(String message) {
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
        Fight live = fights.values().stream().filter(f -> !f.test).findFirst().orElse(null);
        if (live != null) {
            plugin.send(to, "<gold>⚔ " + live.def.name() + " <gold>is alive now" + where(live.arena));
            return;
        }
        WorldBossDef def = upcoming();
        ZonedDateTime next = next();
        if (def == null || next == null) { plugin.send(to, "<gray>No world boss is scheduled."); return; }
        plugin.send(to, "<gold>Next world boss: </gold>" + def.name() + " <gray>" + Text.escape(def.title()) + " <gray>in <white>" + nextText() + "</white>"
                + " <dark_gray>(" + next.getDayOfWeek().toString().charAt(0) + next.getDayOfWeek().toString().substring(1).toLowerCase(Locale.ROOT) + " " + next.toLocalTime() + ")" + where(arenaFor()));
    }

    public String upcomingName() {
        WorldBossDef def = upcoming();
        return def == null ? "" : Text.plain(Text.mm(def.name()));
    }

    // ------------------------------------------------------------------ border stick

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void wand(PlayerInteractEvent event) {
        ItemStack item = event.getItem();
        if (item == null || item.getType() != Material.STICK || !item.hasItemMeta()) return;
        String id = item.getItemMeta().getPersistentDataContainer().get(wandKey, PersistentDataType.STRING);
        if (id == null) return;
        event.setCancelled(true);
        if (event.getHand() != EquipmentSlot.HAND) return;
        Player player = event.getPlayer();
        if (!player.hasPermission("cquests.admin")) return;
        Arena a = arena(id, true);
        if (event.getAction() == Action.LEFT_CLICK_BLOCK && event.getClickedBlock() != null) {
            var b = event.getClickedBlock();
            if (a.world != null && !a.world.equals(b.getWorld().getName()) && !a.points().isEmpty()) { plugin.send(player, "<red>The border must be in the same world as the arena spawn."); return; }
            if (a.world == null) a.world = b.getWorld().getName();
            String problem = a.add(b.getX(), b.getZ());
            save();
            int n = a.points().size();
            plugin.send(player, "<green>Corner " + n + "</green> <gray>at " + b.getX() + ", " + b.getZ() + (n < 3 ? ". Add " + (3 - n) + " more." : problem == null ? ". Border saved." : ". <red>" + Text.escape(problem)));
            show(player, a);
        } else if (event.getAction() == Action.RIGHT_CLICK_BLOCK || event.getAction() == Action.RIGHT_CLICK_AIR) {
            if (player.isSneaking()) { show(player, a); plugin.send(player, "<gray>Arena <white>" + a.id + "</white>: " + a.describe() + "."); return; }
            plugin.send(player, a.undo() ? "<yellow>Removed the last corner. <gray>" + a.points().size() + " left." : "<gray>No corners to remove.");
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

    @EventHandler(priority = EventPriority.HIGHEST, ignoreCancelled = false)
    public void damage(EntityDamageByEntityEvent event) {
        Entity victim = event.getEntity();
        Entity attacker = source(event.getDamager());
        String victimKind = kind(victim), attackerKind = kind(attacker);
        if (attackerKind == null && kind(event.getDamager()) != null) attackerKind = kind(event.getDamager());
        // Boss side only ever hurts players.
        if (attackerKind != null && !(victim instanceof Player)) { event.setCancelled(true); return; }
        if (victimKind == null) return;
        if ("part".equals(victimKind) || !(attacker instanceof Player player)) { event.setCancelled(true); return; }
        Fight f = byEntity.get(victim.getUniqueId());
        if (f == null) return;
        if ("boss".equals(victimKind) && plugin.getConfig().getBoolean("world-bosses.only-hurt-from-inside", true) && !f.arena.contains(player.getLocation())) {
            event.setCancelled(true);
            player.sendActionBar(Text.mm("<red>Step inside the arena to hurt " + f.def.name()));
            return;
        }
        if ("boss".equals(victimKind)) event.setDamage(event.getDamage() / f.ratio);
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void record(EntityDamageByEntityEvent event) {
        if (!"boss".equals(kind(event.getEntity())) || !(source(event.getDamager()) instanceof Player player)) return;
        Fight f = byEntity.get(event.getEntity().getUniqueId());
        if (f == null) return;
        f.damage.merge(player.getUniqueId(), event.getFinalDamage() * f.ratio, Double::sum);
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
        if (f != null && "boss".equals(k) && !f.over) victory(f);
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

    /** For the order of keys in listings. */
    static Map<String, WorldBossDef> sorted(Map<String, WorldBossDef> in) { return new LinkedHashMap<>(in); }
}
