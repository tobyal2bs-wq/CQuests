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
import org.bukkit.entity.Villager;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.logging.Level;

/**
 * Keeps one villager alive at every saved spawn point. Villagers are not saved with the chunk;
 * they are re-created whenever their chunk is loaded, so moving a point or deleting one is clean.
 */
public final class SpawnManager {

    public record Point(String world, double x, double y, double z, float yaw) {
        static Point of(Location loc) {
            return new Point(loc.getWorld().getName(), loc.getX(), loc.getY(), loc.getZ(), loc.getYaw());
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
    private final Map<String, Villager> live = new ConcurrentHashMap<>();
    private ScheduledTask ticker;

    public SpawnManager(CQuestsPlugin plugin) {
        this.plugin = plugin;
        this.file = new File(plugin.getDataFolder(), "spawns.yml");
    }

    public Map<String, Villager> live() {
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
        if (root == null) {
            return;
        }
        for (String id : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(id);
            if (s != null) {
                points.put(id.toLowerCase(Locale.ROOT), new Point(s.getString("world", "world"),
                        s.getDouble("x"), s.getDouble("y"), s.getDouble("z"), (float) s.getDouble("yaw")));
            }
        }
    }

    public synchronized void save() {
        YamlConfiguration yaml = new YamlConfiguration();
        yaml.options().setHeader(List.of(
                "Where each NPC stands. Edit with /cq npc place, /cq scatter or by hand, then /cq reload."));
        for (Map.Entry<String, Point> e : points.entrySet()) {
            String path = "points." + e.getKey();
            Point p = e.getValue();
            yaml.set(path + ".world", p.world());
            yaml.set(path + ".x", round(p.x()));
            yaml.set(path + ".y", round(p.y()));
            yaml.set(path + ".z", round(p.z()));
            yaml.set(path + ".yaw", Math.round(p.yaw()));
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
        long period = plugin.settings().respawnSeconds * 20L;
        ticker = Sched.globalTimer(t -> tick(), 40, period);
    }

    public void stop() {
        if (ticker != null) {
            ticker.cancel();
            ticker = null;
        }
        for (Villager villager : live.values()) {
            Sched.entity(villager, villager::remove);
        }
        live.clear();
    }

    private void tick() {
        for (Map.Entry<String, Point> e : points.entrySet()) {
            NpcDef npc = plugin.npcs().get(e.getKey());
            Location loc = e.getValue().location();
            if (npc != null && loc != null) {
                Sched.at(loc, () -> ensure(npc, loc));
            }
        }
    }

    /** Runs on the region thread that owns {@code loc}. */
    private void ensure(NpcDef npc, Location loc) {
        World world = loc.getWorld();
        if (!world.isChunkLoaded(loc.getBlockX() >> 4, loc.getBlockZ() >> 4)) {
            return;
        }
        Villager current = live.get(npc.id());
        if (current != null && current.isValid()) {
            return;
        }
        Consumer<Villager> setup = v -> configure(v, npc, loc);
        Villager villager = world.spawn(loc, Villager.class, setup);
        live.put(npc.id(), villager);
        plugin.visibility().onSpawn(npc, villager);
    }

    private void configure(Villager v, NpcDef npc, Location loc) {
        // Tag first: the spawn listener uses the tag to override WorldGuard and other spawn blockers.
        NpcTag.tag(v, npc.id());
        v.setPersistent(false);
        v.setRemoveWhenFarAway(false);
        v.setAI(false);
        v.setInvulnerable(true);
        v.setSilent(true);
        v.setCollidable(false);
        v.setCanPickupItems(false);
        v.setRotation(loc.getYaw(), 0f);
        Villager.Profession profession = Registry.VILLAGER_PROFESSION.get(NamespacedKey.minecraft(npc.profession().toLowerCase(Locale.ROOT)));
        if (profession != null) {
            v.setProfession(profession);
        }
        Villager.Type type = Registry.VILLAGER_TYPE.get(NamespacedKey.minecraft(npc.skin().toLowerCase(Locale.ROOT)));
        if (type != null) {
            v.setVillagerType(type);
        }
        // The badge on the villager's robe climbs with the NPC's level: stone, iron, gold, emerald, diamond.
        v.setVillagerLevel(Math.max(1, Math.min(5, 1 + npc.level() / 20)));
        String title = npc.title().isEmpty() ? "" : " <gray>" + Text.escape(npc.title()) + "</gray>";
        v.customName(Text.mm(plugin.settings().npcNameFormat
                .replace("<name>", Text.escape(npc.name()))
                .replace("<level>", Integer.toString(npc.level()))
                .replace("<title>", title)));
        v.setCustomNameVisible(true);
        if (npc.personal()) {
            v.setVisibleByDefault(false);
        }
    }

    public boolean isCurrent(String npcId, Villager villager) {
        return live.get(npcId) == villager;
    }

    // ------------------------------------------------------------------ editing

    public void place(NpcDef npc, Location loc) {
        points.put(npc.id(), Point.of(loc));
        despawn(npc.id());
        save();
        Sched.at(loc, () -> ensure(npc, loc));
    }

    public boolean remove(String npcId) {
        boolean existed = points.remove(npcId) != null;
        despawn(npcId);
        if (existed) {
            save();
        }
        return existed;
    }

    private void despawn(String npcId) {
        Villager old = live.remove(npcId);
        if (old != null) {
            Sched.entity(old, old::remove);
        }
    }

    /**
     * Spreads the NPCs at random spots inside the box, on solid ground, at least 2 blocks apart.
     * Bounds come from a WorldGuard region or the admin's pos1/pos2 selection.
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
                place(npc, loc);
                if (remaining.decrementAndGet() == 0 && feedback != null) {
                    feedback.sendMessage(Text.mm("<green>Scattered " + npcs.size() + " NPCs."));
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
        Consumer<Void> finished = v -> {
            if (remaining.decrementAndGet() == 0) {
                save();
                plugin.getLogger().info("Auto-placed " + total + " NPCs around spawn in " + world.getName()
                        + ". Move them with /cq npc place or /cq scatter.");
            }
        };
        ring(world, spawn, act1, plugin.settings().act1Min, plugin.settings().act1Max, finished);
        ring(world, spawn, act2, plugin.settings().act2Min, plugin.settings().act2Max, finished);
    }

    private void ring(World world, Location center, List<NpcDef> npcs, double min, double max, Consumer<Void> finished) {
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
                points.put(npc.id(), Point.of(loc));
                ensure(npc, loc);
                finished.accept(null);
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
