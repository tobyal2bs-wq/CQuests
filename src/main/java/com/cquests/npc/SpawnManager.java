package com.cquests.npc;

import com.cquests.CQuestsPlugin;
import com.cquests.model.NpcDef;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.NamespacedKey;
import org.bukkit.Registry;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Villager;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.logging.Level;

/**
 * Keeps one NPC at every saved spawn point while a player is near. NPCs are never saved with the
 * chunk; they are created when someone comes within range and removed when everyone leaves.
 * Points that were scattered inside an area wander to a new spot in it every so often, so nobody
 * can camp a villager.
 */
public final class SpawnManager {

    /** @param area the box the NPC roams in ({minX, minY, minZ, maxX, maxY, maxZ}), or null to stay put */
    public record Point(String world, double x, double y, double z, float yaw, int[] area) {
        static Point of(Location loc, int[] area) {
            return new Point(loc.getWorld().getName(), loc.getX(), loc.getY(), loc.getZ(), loc.getYaw(), area);
        }

        public Location location() {
            World w = Bukkit.getWorld(world);
            return w == null ? null : new Location(w, x, y, z, yaw, 0f);
        }
    }

    private static final double GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

    private final CQuestsPlugin plugin;
    private final File file;
    private final Map<String, Point> points = new ConcurrentHashMap<>();
    private final Map<String, LivingEntity> live = new ConcurrentHashMap<>();
    private final Map<String, Long> nextRoam = new ConcurrentHashMap<>();
    private ScheduledTask ticker;
    private EntityType mannequinType;

    public SpawnManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.file = new File(plugin.getDataFolder(), "spawns.yml");
        try {
            // Player-shaped NPCs with skins exist from Minecraft 1.21.9; older servers fall back to villagers.
            mannequinType = EntityType.valueOf("MANNEQUIN");
        } catch (IllegalArgumentException e) {
            mannequinType = null;
        }
    }

    public Map<String, LivingEntity> live() {
        return live;
    }

    public Map<String, Point> points() {
        return points;
    }

    // ------------------------------------------------------------------ lifecycle

    public void load() {
        points.clear();
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection root = yaml.getConfigurationSection("points");
        if (root != null) {
            for (String id : root.getKeys(false)) {
                ConfigurationSection s = root.getConfigurationSection(id);
                if (s == null) {
                    continue;
                }
                List<Integer> area = s.getIntegerList("area");
                points.put(id.toLowerCase(Locale.ROOT), new Point(s.getString("world", "world"),
                        s.getDouble("x"), s.getDouble("y"), s.getDouble("z"), (float) s.getDouble("yaw"),
                        area.size() == 6 ? area.stream().mapToInt(Integer::intValue).toArray() : null));
            }
        }
        plugin.shield().rebuild();
    }

    public synchronized void save() {
        plugin.shield().rebuild();
        YamlConfiguration yaml = new YamlConfiguration();
        yaml.options().setHeader(List.of(
                "Where each NPC stands. Edit with /cq npc place, /cq scatter or by hand, then /cq reload.",
                "An 'area' makes the NPC wander inside that box every spawning.roam-minutes."));
        for (Map.Entry<String, Point> e : points.entrySet()) {
            String path = "points." + e.getKey();
            Point p = e.getValue();
            yaml.set(path + ".world", p.world());
            yaml.set(path + ".x", round(p.x()));
            yaml.set(path + ".y", round(p.y()));
            yaml.set(path + ".z", round(p.z()));
            yaml.set(path + ".yaw", Math.round(p.yaw()));
            if (p.area() != null) {
                List<Integer> area = new ArrayList<>();
                for (int v : p.area()) {
                    area.add(v);
                }
                yaml.set(path + ".area", area);
            }
        }
        try {
            yaml.save(file);
        } catch (IOException e) {
            plugin.getLogger().log(Level.WARNING, "Could not save spawns.yml", e);
        }
    }

    private static double round(double v) {
        return Math.round(v * 100) / 100.0;
    }

    public void start() {
        if (plugin.settings().autoPlace) {
            autoPlace();
        }
        long period = plugin.settings().checkSeconds * 20L;
        ticker = Sched.globalTimer(t -> tick(), 40, period);
    }

    public void stop() {
        if (ticker != null) {
            ticker.cancel();
            ticker = null;
        }
        for (LivingEntity entity : live.values()) {
            Sched.entity(entity, entity::remove);
        }
        live.clear();
    }

    private void tick() {
        long now = System.currentTimeMillis();
        long roamMillis = plugin.settings().roamMinutes * 60_000L;
        boolean changed = false;
        for (Map.Entry<String, Point> e : points.entrySet()) {
            NpcDef npc = plugin.npcs().get(e.getKey());
            Point point = e.getValue();
            Location loc = point.location();
            if (npc == null || loc == null) {
                continue;
            }
            if (point.area() != null && roamMillis > 0) {
                long due = nextRoam.computeIfAbsent(npc.id(), k -> now + jitter(roamMillis));
                if (now >= due) {
                    nextRoam.put(npc.id(), now + jitter(roamMillis));
                    roam(npc, point);
                    changed = true;
                    continue;
                }
            }
            Sched.at(loc, () -> ensure(npc, point, loc));
        }
        if (changed) {
            Sched.async(this::save);
        }
    }

    private static long jitter(long base) {
        return base + ThreadLocalRandom.current().nextLong(Math.max(1, base / 2));
    }

    /**
     * Runs on the region thread that owns {@code loc}. An NPC only exists while a player is within
     * spawning.player-range of it; with nobody around it is removed, so idle NPCs cost nothing.
     */
    private void ensure(NpcDef npc, Point point, Location loc) {
        if (points.get(npc.id()) != point) {
            return; // moved since this check was queued
        }
        World world = loc.getWorld();
        LivingEntity current = live.get(npc.id());
        boolean alive = current != null && current.isValid();
        if (current != null && !alive) {
            live.remove(npc.id(), current);
        }
        if (!world.isChunkLoaded(loc.getBlockX() >> 4, loc.getBlockZ() >> 4)) {
            return;
        }
        double range = plugin.settings().spawnRange;
        // A little extra range before despawning stops NPCs flickering at the edge.
        boolean playerNear = !loc.getNearbyPlayers(alive ? range + 16 : range).isEmpty();
        if (alive && !playerNear) {
            live.remove(npc.id(), current);
            current.remove();
            return;
        }
        if (alive || !playerNear) {
            return;
        }
        LivingEntity entity = spawn(npc, loc);
        live.put(npc.id(), entity);
        plugin.visibility().onSpawn(npc, entity);
    }

    private LivingEntity spawn(NpcDef npc, Location loc) {
        World world = loc.getWorld();
        if (!npc.playerSkin().isEmpty() && mannequinType != null && mannequinType.getEntityClass() != null) {
            try {
                Consumer<Entity> setup = e -> configureMannequin((LivingEntity) e, npc, loc);
                Entity entity = world.spawn(loc, mannequinType.getEntityClass(), setup);
                if (entity instanceof LivingEntity living) {
                    return living;
                }
                entity.remove();
            } catch (RuntimeException | LinkageError e) {
                plugin.getLogger().log(Level.FINE, "Mannequin spawn failed, using a villager", e);
            }
        }
        Consumer<Villager> setup = v -> configureVillager(v, npc, loc);
        return world.spawn(loc, Villager.class, setup);
    }

    private void configureCommon(LivingEntity e, NpcDef npc, Location loc) {
        // Tag first: the spawn listener uses the tag to override WorldGuard and other spawn blockers.
        NpcTag.tag(e, npc.id());
        e.setPersistent(false);
        e.setRemoveWhenFarAway(false);
        e.setAI(false);
        e.setInvulnerable(true);
        e.setSilent(true);
        e.setCollidable(false);
        e.setCanPickupItems(false);
        e.setRotation(loc.getYaw(), 0f);
        String title = npc.title().isEmpty() ? "" : " <gray>" + Text.escape(npc.title()) + "</gray>";
        e.customName(Text.mm(plugin.settings().npcNameFormat
                .replace("<name>", Text.escape(npc.name()))
                .replace("<level>", Integer.toString(npc.level()))
                .replace("<title>", title)));
        e.setCustomNameVisible(true);
        if (npc.personal()) {
            e.setVisibleByDefault(false);
        }
    }

    private void configureVillager(Villager v, NpcDef npc, Location loc) {
        configureCommon(v, npc, loc);
        Villager.Profession profession = Registry.VILLAGER_PROFESSION.get(NamespacedKey.minecraft(npc.profession().toLowerCase(Locale.ROOT)));
        if (profession != null) {
            v.setProfession(profession);
        }
        Villager.Type type = Registry.VILLAGER_TYPE.get(NamespacedKey.minecraft(npc.skin().toLowerCase(Locale.ROOT)));
        if (type != null) {
            v.setVillagerType(type);
        }
        // The badge on the robe climbs with the NPC's level: stone, iron, gold, emerald, diamond.
        v.setVillagerLevel(Math.max(1, Math.min(5, 1 + npc.level() / 20)));
        if (npc.baby()) {
            v.setBaby();
            v.setAgeLock(true);
        }
    }

    /** Sets the skin through reflection, since the Mannequin API only exists on newer servers. */
    private void configureMannequin(LivingEntity e, NpcDef npc, Location loc) {
        configureCommon(e, npc, loc);
        immovable(e);
        if (npc.playerSkin().equalsIgnoreCase("default")) {
            return;
        }
        try {
            Class<?> profileClass = Class.forName("io.papermc.paper.datacomponent.item.ResolvableProfile");
            Class<?> builderClass = Class.forName("io.papermc.paper.datacomponent.item.ResolvableProfile$Builder");
            Object builder = profileClass.getMethod("resolvableProfile").invoke(null);
            builderClass.getMethod("name", String.class).invoke(builder, npc.playerSkin());
            Object profile = builderClass.getMethod("build").invoke(builder);
            for (Method method : e.getClass().getMethods()) {
                if (method.getName().equals("setProfile") && method.getParameterCount() == 1
                        && method.getParameterTypes()[0].isAssignableFrom(profileClass)) {
                    method.invoke(e, profile);
                    break;
                }
            }
        } catch (ReflectiveOperationException | LinkageError ignored) {
            // keeps the default skin
        }
    }

    private static void immovable(LivingEntity e) {
        try {
            e.getClass().getMethod("setImmovable", boolean.class).invoke(e, true);
        } catch (ReflectiveOperationException | LinkageError ignored) {
            // older API: the NPC has no AI and cancelled movement anyway
        }
    }

    public boolean isCurrent(String npcId, Entity entity) {
        return live.get(npcId) == entity;
    }

    // ------------------------------------------------------------------ editing

    public void place(NpcDef npc, Location loc) {
        place(npc, loc, null, true);
    }

    private void place(NpcDef npc, Location loc, int[] area, boolean save) {
        Point point = Point.of(loc, area);
        points.put(npc.id(), point);
        despawn(npc.id());
        if (save) {
            save();
        }
        Sched.at(loc, () -> ensure(npc, point, loc));
    }

    public boolean remove(String npcId) {
        boolean existed = points.remove(npcId) != null;
        despawn(npcId);
        nextRoam.remove(npcId);
        if (existed) {
            save();
        }
        return existed;
    }

    private void despawn(String npcId) {
        LivingEntity old = live.remove(npcId);
        if (old != null) {
            Sched.entity(old, old::remove);
        }
    }

    /** Moves an NPC to a fresh random spot inside its area. */
    private void roam(NpcDef npc, Point point) {
        World world = Bukkit.getWorld(point.world());
        if (world == null) {
            return;
        }
        int[] a = point.area();
        Random rnd = ThreadLocalRandom.current();
        double x = Math.min(a[0], a[3]) + rnd.nextInt(Math.abs(a[3] - a[0]) + 1) + 0.5;
        double z = Math.min(a[2], a[5]) + rnd.nextInt(Math.abs(a[5] - a[2]) + 1) + 0.5;
        float yaw = rnd.nextFloat() * 360f - 180f;
        ground(world, x, z, Math.min(a[1], a[4]), Math.max(a[1], a[4]), yaw, loc -> place(npc, loc, a, false));
    }

    /**
     * Spreads the NPCs at random spots inside the box, on solid ground, at least 2 blocks apart, and
     * remembers the box so they keep wandering inside it. Bounds come from a WorldGuard region or the
     * admin's pos1/pos2 selection.
     */
    public void scatter(List<NpcDef> npcs, World world, int[] box, CommandSender feedback) {
        Random rnd = new Random();
        List<double[]> chosen = new ArrayList<>();
        AtomicInteger remaining = new AtomicInteger(npcs.size());
        int minX = Math.min(box[0], box[3]);
        int maxX = Math.max(box[0], box[3]);
        int minY = Math.min(box[1], box[4]);
        int maxY = Math.max(box[1], box[4]);
        int minZ = Math.min(box[2], box[5]);
        int maxZ = Math.max(box[2], box[5]);
        int[] area = {minX, minY, minZ, maxX, maxY, maxZ};
        double centerX = (minX + maxX) / 2.0 + 0.5;
        double centerZ = (minZ + maxZ) / 2.0 + 0.5;
        for (NpcDef npc : npcs) {
            double[] spot = null;
            for (int attempt = 0; attempt < 30; attempt++) {
                double x = minX + rnd.nextInt(maxX - minX + 1) + 0.5;
                double z = minZ + rnd.nextInt(maxZ - minZ + 1) + 0.5;
                spot = new double[]{x, z};
                if (chosen.stream().allMatch(c -> Math.hypot(c[0] - x, c[1] - z) >= 2)) {
                    break;
                }
            }
            chosen.add(spot);
            float yaw = yawTowards(spot[0], spot[1], centerX, centerZ);
            ground(world, spot[0], spot[1], minY, maxY, yaw, loc -> {
                place(npc, loc, area, false);
                if (remaining.decrementAndGet() == 0) {
                    save();
                    if (feedback != null) {
                        plugin.send(feedback, "<green>Scattered " + npcs.size() + " NPCs. They will wander inside that area.");
                    }
                }
            });
        }
    }

    /** Places every NPC that has no spawn point yet around the world spawn, act 1 close in, act 2 further out. */
    private void autoPlace() {
        List<NpcDef> act1 = new ArrayList<>();
        List<NpcDef> act2 = new ArrayList<>();
        for (NpcDef npc : plugin.npcs().all()) {
            if (!points.containsKey(npc.id())) {
                (npc.act() <= 1 ? act1 : act2).add(npc);
            }
        }
        if (act1.isEmpty() && act2.isEmpty()) {
            return;
        }
        String worldName = plugin.settings().autoPlaceWorld;
        World world = worldName.isEmpty() ? Bukkit.getWorlds().get(0) : Bukkit.getWorld(worldName);
        if (world == null) {
            plugin.getLogger().warning("spawning.auto-place-world '" + worldName + "' not found; NPCs without a spawn point stay hidden");
            return;
        }
        Location spawn = world.getSpawnLocation();
        int total = act1.size() + act2.size();
        AtomicInteger remaining = new AtomicInteger(total);
        Runnable finished = () -> {
            if (remaining.decrementAndGet() == 0) {
                save();
                plugin.getLogger().info("Auto-placed " + total + " NPCs around spawn in " + world.getName()
                        + ". Move them with /cq npc place or /cq scatter.");
            }
        };
        ring(world, spawn, act1, plugin.settings().act1Min, plugin.settings().act1Max, finished);
        ring(world, spawn, act2, plugin.settings().act2Min, plugin.settings().act2Max, finished);
    }

    private void ring(World world, Location center, List<NpcDef> npcs, double min, double max, Runnable finished) {
        int n = npcs.size();
        for (int i = 0; i < n; i++) {
            NpcDef npc = npcs.get(i);
            // Sunflower spiral: even spacing without visible rows.
            double radius = min + (max - min) * Math.sqrt((i + 0.5) / n);
            double angle = i * GOLDEN_ANGLE;
            double x = Math.floor(center.getX() + Math.cos(angle) * radius) + 0.5;
            double z = Math.floor(center.getZ() + Math.sin(angle) * radius) + 0.5;
            float yaw = yawTowards(x, z, center.getX(), center.getZ());
            ground(world, x, z, null, null, yaw, loc -> {
                Point point = Point.of(loc, null);
                points.put(npc.id(), point);
                ensure(npc, point, loc);
                finished.run();
            });
        }
    }

    /** Finds a standable block at x/z on that region's thread and hands back the location there. */
    private void ground(World world, double x, double z, Integer minY, Integer maxY, float yaw, Consumer<Location> done) {
        Location probe = new Location(world, x, world.getMinHeight(), z);
        world.getChunkAtAsync(probe).thenAccept(chunk -> Sched.at(probe, () -> {
            int y = findY(world, (int) Math.floor(x), (int) Math.floor(z), minY, maxY);
            done.accept(new Location(world, x, y, z, yaw, 0f));
        }));
    }

    private static int findY(World world, int x, int z, Integer minY, Integer maxY) {
        if (minY != null && maxY != null) {
            int top = Math.min(maxY, world.getMaxHeight() - 3);
            for (int y = top; y >= Math.max(minY - 1, world.getMinHeight()); y--) {
                Block floor = world.getBlockAt(x, y, z);
                if (floor.getType().isSolid()
                        && floor.getRelative(0, 1, 0).isPassable()
                        && floor.getRelative(0, 2, 0).isPassable()) {
                    return y + 1;
                }
            }
        }
        return world.getHighestBlockYAt(x, z) + 1;
    }

    private static float yawTowards(double fromX, double fromZ, double toX, double toZ) {
        return (float) Math.toDegrees(Math.atan2(-(toX - fromX), toZ - fromZ));
    }
}
