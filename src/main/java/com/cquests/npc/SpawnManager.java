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
import java.util.concurrent.atomic.AtomicLong;
import java.util.Set;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.nio.file.AtomicMoveNotSupportedException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
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
    private static final List<String> DEFAULT_CAMP=List.of("stephan","jerry","rosie","copper_jack","luma");
    private boolean atCamp(NpcDef npc){
        List<String> ids=plugin.getConfig().getStringList("spawning.camp-npcs");
        return npc.daily()||(ids.isEmpty()?DEFAULT_CAMP:ids).contains(npc.id());
    }
    /** Explicit relocation; existing saves are only moved when an admin requests it. */
    public void arrangeCamp(CommandSender feedback){
        World world=plugin.settings().autoPlaceWorld.isEmpty()?Bukkit.getWorlds().get(0):Bukkit.getWorld(plugin.settings().autoPlaceWorld);
        if(world==null){tell(feedback,"<red>Spawn world is unavailable.");return;}
        Location center=world.getSpawnLocation();
        List<NpcDef> selected=plugin.npcs().all().stream().filter(n->{
            Point p=points.get(n.id());return atCamp(n)||(p!=null&&p.world().equals(world.getName())&&Math.hypot(p.x()-center.getX(),p.z()-center.getZ())<96);
        }).toList();
        Map<String,Long> tokens=new java.util.HashMap<>();for(NpcDef n:selected)tokens.put(n.id(),edit(n.id()));
        autoNext(world,center,selected,0,tokens,epoch,new int[2]);
        tell(feedback,"<gold>Arranging five camp residents plus the daily villager; other nearby residents move to the surrounding world. Progress is preserved.");
    }

    private final CQuestsPlugin plugin;
    private final File file;
    private final Map<String, Point> points = new ConcurrentHashMap<>();
    private final Map<String, LivingEntity> live = new ConcurrentHashMap<>();
    private final Map<String, Long> nextRoam = new ConcurrentHashMap<>();
    private ScheduledTask ticker;
    private EntityType mannequinType;
    private final Set<Point> validated = ConcurrentHashMap.newKeySet();
    private final Set<Point> checking = ConcurrentHashMap.newKeySet();
    private final Set<Point> rejected = ConcurrentHashMap.newKeySet();
    private final Set<String> disabled = ConcurrentHashMap.newKeySet();
    private final Map<String, Long> revisions = new ConcurrentHashMap<>();
    private final AtomicLong revision = new AtomicLong();
    private volatile long epoch;
    private volatile boolean running;
    private final ExecutorService writer = Executors.newSingleThreadExecutor(r -> {
        Thread t = new Thread(r, "CQuests-spawn-writer"); t.setDaemon(true); return t;
    });

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
        disabled.clear();
        validated.clear(); checking.clear(); rejected.clear(); nextRoam.clear();
        YamlConfiguration yaml = YamlConfiguration.loadConfiguration(file);
        disabled.addAll(yaml.getStringList("disabled"));
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
        if (writer.isShutdown()) return;
        plugin.shield().rebuild();
        YamlConfiguration yaml = new YamlConfiguration();
        yaml.set("disabled", new ArrayList<>(disabled));
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
        String content = yaml.saveToString();
        writer.execute(() -> {
            try {
                var tmp = file.toPath().resolveSibling("spawns.yml.tmp");
                Files.writeString(tmp, content, java.nio.charset.StandardCharsets.UTF_8);
                if (file.exists()) Files.copy(file.toPath(), file.toPath().resolveSibling("spawns.yml.bak"), StandardCopyOption.REPLACE_EXISTING);
                try { Files.move(tmp, file.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
                catch (AtomicMoveNotSupportedException e) { Files.move(tmp, file.toPath(), StandardCopyOption.REPLACE_EXISTING); }
            } catch (IOException e) { plugin.getLogger().log(Level.WARNING, "Could not save spawns.yml", e); }
        });
    }

    private static double round(double v) {
        return Math.round(v * 100) / 100.0;
    }

    public void start() {
        running = true;
        if (plugin.settings().autoPlace) {
            autoPlace();
        }
        long period = plugin.settings().checkSeconds * 20L;
        ticker = Sched.globalTimer(t -> tick(), 40, period);
    }

    public synchronized void stop() {
        running = false; epoch++;
        if (ticker != null) {
            ticker.cancel();
            ticker = null;
        }
        for (LivingEntity entity : live.values()) {
            if (plugin.isEnabled()) Sched.entity(entity, entity::remove);
        }
        live.clear();
        flushWrites();
    }

    public synchronized void shutdown() {
        stop(); writer.shutdown();
        try { if (!writer.awaitTermination(10, TimeUnit.SECONDS)) plugin.getLogger().warning("Spawn writer did not drain within 10 seconds"); }
        catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }

    private void flushWrites() {
        try { writer.submit(() -> {}).get(10, TimeUnit.SECONDS); }
        catch (Exception e) { plugin.getLogger().log(Level.WARNING, "Could not drain spawn writes", e); }
    }

    private void tick() {
        long now = System.currentTimeMillis();
        long roamMillis = plugin.settings().roamMinutes * 60_000L;
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
                    continue;
                }
            }
            Sched.at(loc, () -> ensure(npc, point, loc));
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
        if (!running || points.get(npc.id()) != point) {
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
        if (rejected.contains(point)) return;
        if (!validated.remove(point)) {
            if (checking.add(point)) {
                long expectedEpoch = epoch;
                SafePlacement.validate(loc).whenComplete((safe, error) -> {
                    checking.remove(point);
                    if (!running || epoch != expectedEpoch || points.get(npc.id()) != point) return;
                    if (error == null && Boolean.TRUE.equals(safe)) {
                        validated.add(point);
                        Sched.at(loc, () -> ensure(npc, point, loc));
                    } else {
                        rejected.add(point);
                        plugin.getLogger().warning("Unsafe spawn for " + npc.id() + " at " + point.world() + " " + point.x() + "," + point.y() + "," + point.z()
                                + "; use /cq npc repair " + npc.id() + " or /cq npc place " + npc.id());
                    }
                });
            }
            return;
        }
        // Recheck the central floor on its owning region after the snapshot search.
        Block feet = loc.getBlock();
        if (!TerrainSafety.floor(feet.getRelative(0, -1, 0).getType())
                || !TerrainSafety.clear(feet.getType()) || !TerrainSafety.clear(feet.getRelative(0, 1, 0).getType())) return;
        LivingEntity entity = spawn(npc, loc);
        if (!entity.isValid()) {
            plugin.getLogger().warning("Spawn of " + npc.id() + " was cancelled by another plugin; check spawn protection plugins.");
            return;
        }
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
        return world.spawn(loc, Villager.class, org.bukkit.event.entity.CreatureSpawnEvent.SpawnReason.CUSTOM, false, setup);
    }

    private void configureCommon(LivingEntity e, NpcDef npc, Location loc) {
        // Tag first: the spawn listener uses the tag to override WorldGuard and other spawn blockers.
        NpcTag.tag(e, npc.id());
        e.setPersistent(false);
        e.setRemoveWhenFarAway(false);
        e.setAI(false);
        e.setGravity(false);
        e.setInvulnerable(true);
        e.setSilent(true);
        e.setCollidable(false);
        e.setCanPickupItems(false);
        e.setRotation(loc.getYaw(), 0f);
        String title = npc.title().isEmpty() ? "" : " <gray>" + Text.escape(npc.title()) + "</gray>";
        e.customName(Text.mm(plugin.settings().npcNameFormat
                .replace("<name>", "<bold>"+npc.name()+"</bold>")
                .replace("<level>", Integer.toString(npc.level()))
                .replace("<title>", title)));
        e.setCustomNameVisible(true);
        e.setVisibleByDefault(false); // chapter visibility is applied before a player sees the NPC
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
        placeChecked(npc, loc, null);
    }

    public void placeChecked(NpcDef npc, Location loc, CommandSender feedback) {
        long token = edit(npc.id()), expectedEpoch = epoch;
        SafePlacement.validate(loc).whenComplete((safe, error) -> {
            if (!current(npc.id(), token, expectedEpoch)) return;
            if (error != null || !Boolean.TRUE.equals(safe)) {
                tell(feedback, "<red>Unsafe spot. Use solid ground with two clear blocks above it. End: no void within 10 blocks. Nether: no nearby lava or roof placement. Previous position kept.");
                return;
            }
            if (commit(npc, loc, null, token, expectedEpoch)) {
                save();
                tell(feedback, "<green>" + Text.escape(npc.name()) + " now stands here.");
            }
        });
    }

    private void place(NpcDef npc, Location loc, int[] area, boolean save) {
        Point point = Point.of(loc, area);
        Point previous = points.put(npc.id(), point);
        disabled.remove(npc.id());
        if (previous != null) { validated.remove(previous); rejected.remove(previous); checking.remove(previous); }
        validated.add(point);
        despawn(npc.id());
        if (save) {
            save();
        }
        Sched.at(loc, () -> ensure(npc, point, loc));
    }

    public synchronized boolean remove(String npcId) {
        edit(npcId);
        disabled.add(npcId);
        boolean existed = points.remove(npcId) != null;
        despawn(npcId);
        nextRoam.remove(npcId);
        save();
        return existed;
    }

    private void despawn(String npcId) {
        LivingEntity old = live.remove(npcId);
        if (old != null) {
            Sched.entity(old, old::remove);
        }
    }

    /** Moves an NPC to a new spot in its area right now. False if it has no area (not placed with /cq scatter). */
    public boolean roamNow(NpcDef npc) {
        Point point = points.get(npc.id());
        if (point == null || point.area() == null) {
            return false;
        }
        roam(npc, point);
        return true;
    }

    /** Moves an NPC to a fresh random spot inside its area. */
    private void roam(NpcDef npc, Point point) {
        World world = Bukkit.getWorld(point.world());
        if (world == null) {
            return;
        }
        long token = edit(npc.id()), expectedEpoch = epoch;
        search(npc, world, point.area(), 0, token, expectedEpoch, loc -> {
            if (loc != null && commit(npc, loc, point.area(), token, expectedEpoch)) save();
        });
    }

    /**
     * Spreads the NPCs at random spots inside the box, on solid ground, at least 2 blocks apart, and
     * remembers the box so they keep wandering inside it. Bounds come from a WorldGuard region or the
     * admin's pos1/pos2 selection.
     */
    public void scatter(List<NpcDef> npcs, World world, int[] box, CommandSender feedback) {
        if (npcs.isEmpty()) { tell(feedback, "<gray>No NPCs selected."); return; }
        long expectedEpoch = epoch;
        Map<String, Long> tokens = new java.util.HashMap<>();
        for (NpcDef npc : npcs) tokens.put(npc.id(), edit(npc.id()));
        // One search at a time bounds chunk generation even for a 10,000 x 10,000 world area.
        scatterNext(npcs, 0, world, box.clone(), feedback, tokens, expectedEpoch, new int[2]);
    }

    private void scatterNext(List<NpcDef> npcs, int index, World world, int[] area, CommandSender feedback,
                             Map<String, Long> tokens, long expectedEpoch, int[] counts) {
        if (!running || epoch != expectedEpoch) return;
        if (index >= npcs.size()) {
            save();
            tell(feedback, "<green>Scattered " + counts[0] + " NPCs; " + counts[1]
                    + " skipped (no safe spot or a newer edit). Previous positions kept for skipped NPCs. Quest progress preserved.");
            return;
        }
        NpcDef npc = npcs.get(index);
        long token = tokens.get(npc.id());
        search(npc, world, area, 0, token, expectedEpoch, loc -> {
            if (loc != null && commit(npc, loc, area, token, expectedEpoch)) counts[0]++;
            else counts[1]++;
            scatterNext(npcs, index + 1, world, area, feedback, tokens, expectedEpoch, counts);
        });
    }

    private void search(NpcDef npc, World world, int[] area, int attempt, long token, long expectedEpoch, Consumer<Location> done) {
        if (!current(npc.id(), token, expectedEpoch) || attempt >= 32) { done.accept(null); return; }
        Random rnd = ThreadLocalRandom.current();
        int minX = Math.min(area[0], area[3]), maxX = Math.max(area[0], area[3]);
        int minZ = Math.min(area[2], area[5]), maxZ = Math.max(area[2], area[5]);
        double x = rnd.nextLong(minX, (long) maxX + 1) + 0.5;
        double z = rnd.nextLong(minZ, (long) maxZ + 1) + 0.5;
        float yaw = rnd.nextFloat() * 360f - 180f;
        SafePlacement.find(world, x, z, Math.min(area[1], area[4]), Math.max(area[1], area[4]), yaw)
                .whenComplete((loc, error) -> {
                    if (!current(npc.id(), token, expectedEpoch)) { done.accept(null); return; }
                    double spacing = Math.max(4, plugin.settings().shieldRadius * 2 + 2);
                    boolean free = loc != null && points.entrySet().stream().noneMatch(e -> !e.getKey().equals(npc.id())
                            && e.getValue().world().equals(world.getName()) && Math.hypot(e.getValue().x() - x, e.getValue().z() - z) < spacing);
                    if (error == null && free) done.accept(loc);
                    else search(npc, world, area, attempt + 1, token, expectedEpoch, done);
                });
    }

    private synchronized long edit(String id) {
        long token = revision.incrementAndGet(); revisions.put(id, token); return token;
    }

    private boolean current(String id, long token, long expectedEpoch) {
        return running && epoch == expectedEpoch && revisions.getOrDefault(id, 0L) == token;
    }

    private synchronized boolean commit(NpcDef npc, Location loc, int[] area, long token, long expectedEpoch) {
        if (!current(npc.id(), token, expectedEpoch)) return false;
        place(npc, loc, area, false);
        // Queue each accepted edit before a reload/shutdown can drain the writer.
        save();
        return true;
    }

    private void tell(CommandSender sender, String message) {
        if (sender == null) return;
        if (sender instanceof org.bukkit.entity.Player player) Sched.entity(player, () -> plugin.send(player, message));
        else Sched.global(() -> plugin.send(sender, message));
    }

    public void repair(NpcDef npc, CommandSender feedback) {
        Point point = points.get(npc.id());
        World world = point == null ? null : Bukkit.getWorld(point.world());
        if (world == null) { tell(feedback, "<red>No saved point or world is unavailable."); return; }
        int x = (int) Math.floor(point.x()), z = (int) Math.floor(point.z());
        int[] area = point.area() == null ? new int[]{x - 32, world.getMinHeight() + 1, z - 32,
                x + 32, world.getMaxHeight() - 2, z + 32} : point.area();
        long token = edit(npc.id()), expectedEpoch = epoch;
        search(npc, world, area, 0, token, expectedEpoch, loc -> {
            if (loc != null && commit(npc, loc, point.area(), token, expectedEpoch)) {
                save(); tell(feedback, "<green>Repaired " + Text.escape(npc.name()) + " on safe terrain.");
            } else tell(feedback, "<red>No safe spot found. Previous position kept; try /cq npc place " + npc.id());
        });
    }

    /** Places every NPC that has no spawn point yet around the world spawn, act 1 close in, act 2 further out. */
    private void autoPlace() {
        List<NpcDef> act1 = new ArrayList<>();
        List<NpcDef> act2 = new ArrayList<>();
        for (NpcDef npc : plugin.npcs().all()) {
            if (!points.containsKey(npc.id()) && !disabled.contains(npc.id())) {
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
        List<NpcDef> all = new ArrayList<>(act1); all.addAll(act2);
        Map<String, Long> tokens = new java.util.HashMap<>();
        for (NpcDef npc : all) tokens.put(npc.id(), edit(npc.id()));
        autoNext(world, spawn, all, 0, tokens, epoch, new int[2]);
    }

    private void autoNext(World world, Location center, List<NpcDef> npcs, int index, Map<String, Long> tokens, long expectedEpoch, int[] counts) {
        if (!running || epoch != expectedEpoch) return;
        if (index >= npcs.size()) {
            save();
            plugin.getLogger().info("Auto-placed " + counts[0] + " NPCs around spawn in " + world.getName() + "; " + counts[1] + " skipped. Use /cq npc list or /cq scatterworld.");
            return;
        }
        NpcDef npc = npcs.get(index);
        int radius = (int) Math.ceil(atCamp(npc) ? Math.max(40,plugin.settings().act1Max) : Math.max(300,plugin.settings().act2Max));
        int x = center.getBlockX(), z = center.getBlockZ();
        int[] area = {x - radius, world.getMinHeight() + 1, z - radius, x + radius, world.getMaxHeight() - 2, z + radius};
        if(!atCamp(npc))area=new int[]{x+128,world.getMinHeight()+1,z-radius,x+radius,world.getMaxHeight()-2,z+radius};
        long token = tokens.get(npc.id());
        search(npc, world, area, 0, token, expectedEpoch, loc -> {
            if (loc != null && commit(npc, loc, null, token, expectedEpoch)) counts[0]++; else counts[1]++;
            autoNext(world, center, npcs, index + 1, tokens, expectedEpoch, counts);
        });
    }

    private static float yawTowards(double fromX, double fromZ, double toX, double toZ) {
        return (float) Math.toDegrees(Math.atan2(-(toX - fromX), toZ - fromZ));
    }
}
