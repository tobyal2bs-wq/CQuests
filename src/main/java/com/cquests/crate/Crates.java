package com.cquests.crate;

import com.cquests.CQuestsPlugin;
import com.cquests.T;
import com.cquests.model.ObjectiveType;
import com.cquests.util.Sched;
import com.cquests.util.Text;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.*;
import org.bukkit.block.Block;
import org.bukkit.block.BlockFace;
import org.bukkit.block.data.BlockData;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.*;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.ItemSpawnEvent;
import org.bukkit.event.inventory.PrepareItemCraftEvent;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.ItemStack;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.util.Vector;
import org.joml.Matrix4f;

import java.io.File;
import java.time.LocalDate;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Loot crates: a wooden crate of block displays that breaks open when a player uses it and drops loot from
 * crates.loot, and very rarely a Chest Token (odds change every day between crates.token min and max).
 * Ops place crate spots (/cq crate place: it falls to the ground below, region protection does not stop it
 * or its opening); a spot comes back crates.respawn-minutes after it is opened. A few wild crates also hide
 * around the world and move somewhere else after a while. Opening one counts for FIND quests.
 * Crates are drawn only while a player is near and never saved into the world.
 */
public final class Crates implements Listener {
    private static final double SHOW = 40, HIDE = 56;

    private static final class Crate {
        final String id; final boolean wild;
        volatile String world; volatile int x, y, z;
        volatile long back, expires;           // back: when an opened crate returns (0 = here); expires: when a wild one moves
        volatile float fall;                   // blocks it still drops on its first showing
        volatile List<Display> parts; volatile Interaction hitbox; volatile boolean opening, moving;
        Crate(String id, boolean wild, String world, int x, int y, int z) { this.id = id; this.wild = wild; this.world = world; this.x = x; this.y = y; this.z = z; }
        Location at() { World w = Bukkit.getWorld(world); return w == null ? null : new Location(w, x, y, z); }
        boolean here() { return back == 0 && !moving; }
    }

    private final CQuestsPlugin plugin;
    private final NamespacedKey tokenKey, crateKey;
    private final Map<String, Crate> crates = new ConcurrentHashMap<>();
    private final File file;
    private ScheduledTask timer;

    public Crates(CQuestsPlugin plugin) {
        this.plugin = plugin;
        tokenKey = new NamespacedKey(plugin, "chest_token");
        crateKey = new NamespacedKey(plugin, "crate");
        file = new File(plugin.getDataFolder(), "crates.yml");
    }

    private ConfigurationSection cfg() {
        ConfigurationSection c = plugin.getConfig().getConfigurationSection("crates");
        return c != null ? c : new YamlConfiguration();
    }

    public void start() {
        stop();
        load();
        if (!cfg().getBoolean("enabled", true)) return;
        timer = Sched.globalTimer(t -> tick(), 40, 20);
    }

    public void stop() {
        if (timer != null) { timer.cancel(); timer = null; }
        if (!plugin.isEnabled()) return;                       // shutting down: the displays are never saved, nothing to clean
        for (Crate c : crates.values()) { Location a = c.at(); if (a != null) Sched.at(a, () -> hide(c)); }
    }

    // ------------------------------------------------------------------ the token

    /** The Chest Token: a glowing sunflower only this plugin can make (a tag players cannot add or copy in survival). */
    public ItemStack token(int amount) {
        ItemStack item = new ItemStack(Material.SUNFLOWER, Math.max(1, Math.min(64, amount)));
        item.editMeta(m -> {
            m.displayName(Text.mm("<!italic><gold><bold>Chest Token"));
            m.lore(List.of(Text.mm("<!italic><gray>A rare token found in a loot crate."), Text.mm("<!italic><yellow>Trade it with the Token Keeper.")));
            m.setEnchantmentGlintOverride(true);
            m.getPersistentDataContainer().set(tokenKey, PersistentDataType.BYTE, (byte) 1);
        });
        return item;
    }

    public boolean isToken(ItemStack item) {
        return item != null && item.getType() == Material.SUNFLOWER && item.hasItemMeta() && item.getItemMeta().getPersistentDataContainer().has(tokenKey);
    }

    /** Today's token odds, 1 in this many crates: the same all day, a new number every day. */
    public int odds() {
        int lo = Math.max(1, cfg().getInt("token.min-odds", 10000)), hi = Math.max(lo, cfg().getInt("token.max-odds", 200000));
        return lo + new Random(LocalDate.now().toEpochDay() * 0x9E3779B97F4A7C15L).nextInt(hi - lo + 1);
    }

    @EventHandler(ignoreCancelled = true)
    public void place(BlockPlaceEvent e) { if (isToken(e.getItemInHand())) e.setCancelled(true); }

    @EventHandler
    public void craft(PrepareItemCraftEvent e) { for (ItemStack i : e.getInventory().getMatrix()) if (isToken(i)) { e.getInventory().setResult(null); return; } }

    @EventHandler(ignoreCancelled = true)
    public void compost(PlayerInteractEvent e) {
        if (isToken(e.getItem()) && e.getClickedBlock() != null && e.getClickedBlock().getType() == Material.COMPOSTER) e.setCancelled(true);
    }

    /** A dropped token sparkles and glows until someone picks it up. */
    @EventHandler(ignoreCancelled = true)
    public void dropped(ItemSpawnEvent e) {
        if (!isToken(e.getEntity().getItemStack())) return;
        Item item = e.getEntity();
        item.setGlowing(true);
        item.getScheduler().runAtFixedRate(plugin, t -> {
            Location l = item.getLocation().add(0, 0.35, 0);
            item.getWorld().spawnParticle(Particle.END_ROD, l, 2, 0.15, 0.15, 0.15, 0.01);
            item.getWorld().spawnParticle(Particle.WAX_ON, l, 3, 0.25, 0.2, 0.25, 0);
        }, null, 1, 5);
    }

    // ------------------------------------------------------------------ showing crates

    private void tick() {
        long now = System.currentTimeMillis();
        long wildCount = crates.values().stream().filter(c -> c.wild).count();
        for (int i = (int) wildCount; i < Math.max(0, cfg().getInt("wild.count", 3)); i++) crates.putIfAbsent("wild" + i, relocate(new Crate("wild" + i, true, "", 0, -999, 0)));
        for (Crate c : crates.values()) {
            if (c.moving) continue;
            if (c.back > 0 && now >= c.back) { c.back = 0; if (c.wild) { relocate(c); continue; } save(); }
            if (c.wild && c.here() && now >= c.expires) { Location a = c.at(); if (a != null) Sched.at(a, () -> hide(c)); relocate(c); continue; }
            Location at = c.at();
            if (at == null) continue;
            Sched.at(at, () -> {
                boolean near = false, far = true;
                for (Player p : at.getNearbyPlayers(HIDE)) { far = false; if (p.getLocation().distanceSquared(at) < SHOW * SHOW) { near = true; break; } }
                List<Display> parts = c.parts;
                if (parts != null && (far || !c.here() && !c.opening || !parts.get(0).isValid())) hide(c);
                else if (parts == null && near && c.here()) show(c, at);
            });
        }
    }

    /** A wild crate moves to a random dry spot on the surface of already generated land. */
    private Crate relocate(Crate c) {
        c.moving = true;
        String name = cfg().getString("wild.world", "");
        World w = name.isBlank() ? Bukkit.getWorlds().get(0) : Bukkit.getWorld(name);
        if (w == null) { c.moving = false; c.expires = Long.MAX_VALUE; return c; }
        int r = Math.max(32, cfg().getInt("wild.radius", 1500));
        Location spawn = w.getSpawnLocation();
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        int bx = spawn.getBlockX() + rnd.nextInt(-r, r + 1), bz = spawn.getBlockZ() + rnd.nextInt(-r, r + 1);
        w.getChunkAtAsync(bx >> 4, bz >> 4, false).thenAccept(chunk -> {
            if (chunk == null) { c.moving = false; c.expires = 0; return; }              // not generated: try again next tick
            Sched.at(new Location(w, bx, 0, bz), () -> {
                Block top = w.getHighestBlockAt(bx, bz, HeightMap.MOTION_BLOCKING_NO_LEAVES);
                if (!top.isLiquid() && top.getType().isSolid()) {
                    c.world = w.getName(); c.x = bx; c.y = top.getY() + 1; c.z = bz; c.fall = 0;
                    c.expires = System.currentTimeMillis() + Math.max(1, cfg().getLong("wild.lifetime-minutes", 360)) * 60_000L;
                } else c.expires = 0;
                c.moving = false;
            });
        });
        return c;
    }

    private void show(Crate c, Location at) {
        World w = at.getWorld();
        List<Display> parts = new ArrayList<>(33);
        BlockData panel = Material.OAK_PLANKS.createBlockData(), frame = Material.DARK_OAK_PLANKS.createBlockData(), stud = Material.IRON_BLOCK.createBlockData();
        float t = 0.14f;
        List<Object[]> boxes = new ArrayList<>();
        boxes.add(new Object[]{panel, box(0.06f, 0.06f, 0.06f, 0.88f, 0.88f, 0.88f)});
        for (int axis = 0; axis < 3; axis++) for (int k = 0; k < 4; k++) {     // the 12 edges of the frame
            float a = (k & 1) == 0 ? 0 : 1 - t, b = (k & 2) == 0 ? 0 : 1 - t;
            boxes.add(new Object[]{frame, axis == 0 ? box(0, a, b, 1, t, t) : axis == 1 ? box(a, 0, b, t, 1, t) : box(a, b, 0, t, t, 1)});
        }
        Matrix4f[] faces = {new Matrix4f(), new Matrix4f().rotationY((float) Math.PI / 2), new Matrix4f().rotationY((float) Math.PI),
                new Matrix4f().rotationY((float) -Math.PI / 2), new Matrix4f().rotationX((float) Math.PI / 2), new Matrix4f().rotationX((float) -Math.PI / 2)};
        for (Matrix4f f : faces) for (int s = -1; s <= 1; s += 2)              // an X brace on every side, all six the same
            boxes.add(new Object[]{frame, new Matrix4f().translate(0.5f, 0.5f, 0.5f).mul(f).translate(0, 0, -0.5f + 0.035f)
                    .rotateZ((float) Math.toRadians(45 * s)).scale(1.0f, 0.12f, 0.05f).translate(-0.5f, -0.5f, -0.5f)});
        for (int k = 0; k < 8; k++)                                             // iron studs on the corners
            boxes.add(new Object[]{stud, box((k & 1) == 0 ? -0.02f : 0.82f, (k & 2) == 0 ? -0.02f : 0.82f, (k & 4) == 0 ? -0.02f : 0.82f, 0.2f, 0.2f, 0.2f)});
        float drop = c.fall;
        c.fall = 0;
        for (Object[] b : boxes) {
            Matrix4f m = (Matrix4f) b[1];
            parts.add(w.spawn(at, BlockDisplay.class, d -> {
                d.setPersistent(false); d.setBlock((BlockData) b[0]); d.setViewRange(0.6f); d.setShadowRadius(0);
                d.setTransformationMatrix(new Matrix4f().translation(0, drop, 0).mul(m));
                d.getPersistentDataContainer().set(crateKey, PersistentDataType.STRING, c.id);
            }));
        }
        c.hitbox = w.spawn(at.clone().add(0.5, 0, 0.5), Interaction.class, i -> {
            i.setPersistent(false); i.setInteractionWidth(1.05f); i.setInteractionHeight(1.05f); i.setResponsive(true);
            i.getPersistentDataContainer().set(crateKey, PersistentDataType.STRING, c.id);
        });
        c.parts = parts;
        if (drop > 0.05f) {                                                     // placed in the air: it falls and lands
            int ticks = Math.max(4, Math.min(30, Math.round(drop * 3)));
            Bukkit.getRegionScheduler().runDelayed(plugin, at, x -> {
                for (int i = 0; i < parts.size(); i++) move(parts.get(i), (Matrix4f) boxes.get(i)[1], ticks);
            }, 2);
            Bukkit.getRegionScheduler().runDelayed(plugin, at, x -> {
                w.playSound(at, Sound.BLOCK_WOOD_FALL, 1f, 0.7f);
                w.spawnParticle(Particle.BLOCK, at.clone().add(0.5, 0.05, 0.5), 20, 0.4, 0.05, 0.4, 0.1, at.clone().add(0, -1, 0).getBlock().getBlockData());
            }, 2 + ticks);
        }
    }

    private static Matrix4f box(float x, float y, float z, float w, float h, float d) { return new Matrix4f().translation(x, y, z).scale(w, h, d); }

    private static void move(Display d, Matrix4f m, int ticks) {
        if (!d.isValid()) return;
        d.setInterpolationDelay(0); d.setInterpolationDuration(ticks); d.setTransformationMatrix(m);
    }

    private void hide(Crate c) {
        List<Display> parts = c.parts;
        Interaction box = c.hitbox;
        c.parts = null; c.hitbox = null;
        if (parts != null) for (Display d : parts) if (d.isValid()) d.remove();
        if (box != null && box.isValid()) box.remove();
    }

    // ------------------------------------------------------------------ opening

    // HIGHEST and ignoreCancelled=false: region protection never stops a crate from opening
    @EventHandler(priority = EventPriority.HIGHEST)
    public void use(PlayerInteractEntityEvent e) { if (open(e.getPlayer(), e.getRightClicked())) e.setCancelled(true); }

    @EventHandler(priority = EventPriority.HIGHEST)
    public void hit(EntityDamageByEntityEvent e) { if (e.getDamager() instanceof Player p && open(p, e.getEntity())) e.setCancelled(true); }

    private boolean open(Player player, Entity entity) {
        if (!(entity instanceof Interaction)) return false;
        String id = entity.getPersistentDataContainer().get(crateKey, PersistentDataType.STRING);
        Crate c = id == null ? null : crates.get(id);
        if (c == null) return id != null;
        List<Display> parts = c.parts;
        if (parts == null || c.opening || !c.here()) return true;
        c.opening = true;
        Location at = c.at(), mid = at.clone().add(0.5, 0.5, 0.5);
        World w = at.getWorld();
        w.playSound(mid, Sound.BLOCK_BARREL_OPEN, 1f, 0.8f);
        w.playSound(mid, Sound.ENTITY_ZOMBIE_BREAK_WOODEN_DOOR, 0.6f, 1.4f);
        w.spawnParticle(Particle.BLOCK, mid, 40, 0.35, 0.35, 0.35, 0.15, Material.OAK_PLANKS.createBlockData());
        ThreadLocalRandom r = ThreadLocalRandom.current();
        for (Display d : parts) {                                              // the planks burst apart, spin and shrink away
            Matrix4f now = d.getTransformation() == null ? new Matrix4f() : new Matrix4f().translation(d.getTransformation().getTranslation());
            move(d, new Matrix4f().translation(r.nextFloat() * 1.6f - 0.8f, 0.3f + r.nextFloat() * 0.9f, r.nextFloat() * 1.6f - 0.8f).mul(now)
                    .rotateXYZ(r.nextFloat() * 3, r.nextFloat() * 3, r.nextFloat() * 3).scale(0.05f), 7);
        }
        Bukkit.getRegionScheduler().runDelayed(plugin, at, t -> { hide(c); c.opening = false; }, 8);
        c.back = System.currentTimeMillis() + Math.max(1, cfg().getLong(c.wild ? "wild.respawn-minutes" : "respawn-minutes", c.wild ? 20 : 30)) * 60_000L;
        if (!c.wild) save();
        Vector toward = player.getLocation().toVector().subtract(mid.toVector()).setY(0);
        Vector push = (toward.lengthSquared() > 0.01 ? toward.normalize().multiply(0.18) : new Vector()).setY(0.32);
        for (ItemStack item : loot()) w.dropItem(mid, item, i -> i.setVelocity(push.clone().add(new Vector(r.nextGaussian() * 0.04, 0, r.nextGaussian() * 0.04))));
        if (r.nextInt(odds()) == 0) {
            w.dropItem(mid, token(1), i -> i.setVelocity(push));
            w.spawnParticle(Particle.TOTEM_OF_UNDYING, mid, 60, 0.4, 0.6, 0.4, 0.4);
            w.playSound(mid, Sound.UI_TOAST_CHALLENGE_COMPLETE, 1f, 1.2f);
            Bukkit.getServer().sendMessage(Text.mm(T.t("crates.token-found", "<gold><bold>✦</bold> <yellow><player></yellow> found a <gold><bold>Chest Token</bold></gold> in a loot crate!", "player", Text.escape(player.getName()))));
        }
        plugin.questManager().progress(player, ObjectiveType.FIND, "CRATE", 1);
        return true;
    }

    /** One pick from crates.loot ("weight ITEM amount" lines). */
    private List<ItemStack> loot() {
        List<String> lines = cfg().getStringList("loot");
        int total = 0;
        List<Object[]> table = new ArrayList<>();
        for (String line : lines) {
            String[] p = line.trim().split("\\s+");
            Material m = p.length > 1 ? Material.matchMaterial(p[1]) : null;
            if (m == null || !m.isItem()) continue;
            try { int wgt = Integer.parseInt(p[0]); total += Math.max(0, wgt); table.add(new Object[]{total, m, p.length > 2 ? Integer.parseInt(p[2]) : 1}); }
            catch (NumberFormatException ignored) { }
        }
        if (total == 0) return List.of(new ItemStack(Material.DIAMOND, 5));
        int roll = ThreadLocalRandom.current().nextInt(total);
        for (Object[] row : table) if (roll < (int) row[0]) return List.of(new ItemStack((Material) row[1], Math.max(1, Math.min(64, (int) row[2]))));
        return List.of();
    }

    // ------------------------------------------------------------------ hints for FIND quests

    /** Rough spots of the nearest crates that are out right now, as a villager would tell them. */
    public void hint(Player player, int count) {
        Location me = player.getLocation();
        List<Crate> out = new ArrayList<>();
        for (Crate c : crates.values()) if (c.here() && c.y > -999 && c.world.equals(me.getWorld().getName())) out.add(c);
        out.sort(Comparator.comparingDouble(c -> sq(c.x - me.getX()) + sq(c.z - me.getZ())));
        if (out.isEmpty()) { plugin.send(player, T.t("crates.no-hint", "<gray>\"I haven't heard of any crates lying about just now. Look again later.\"")); return; }
        for (Crate c : out.subList(0, Math.min(count, out.size()))) {
            Random jitter = new Random(c.id.hashCode() * 31L + c.x * 7L + c.z);     // the same rough spot every time you ask
            int hx = Math.round((c.x + jitter.nextInt(-12, 13)) / 10f) * 10, hz = Math.round((c.z + jitter.nextInt(-12, 13)) / 10f) * 10;
            int dist = (int) Math.sqrt(sq(c.x - me.getX()) + sq(c.z - me.getZ()));
            plugin.send(player, T.t("crates.hint", "<gold>✦ <gray>\"Someone saw a crate around <white>X <x>, Z <z></white>. That's about <white><dist></white> blocks <white><dir></white> of here.\"",
                    "x", hx, "z", hz, "dist", Math.max(10, Math.round(dist / 10f) * 10), "dir", direction(c.x - me.getX(), c.z - me.getZ())));
        }
    }

    private static double sq(double v) { return v * v; }

    private static String direction(double dx, double dz) {
        String[] names = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};
        return names[(int) Math.floorMod(Math.round(Math.toDegrees(Math.atan2(-dx, dz)) / 45), 8)];
    }

    // ------------------------------------------------------------------ commands (/cq crate ...)

    public void command(CommandSender to, String[] args) {
        Player player = to instanceof Player p ? p : null;
        switch (args.length > 1 ? args[1].toLowerCase(Locale.ROOT) : "list") {
            case "place" -> {
                if (player == null) { plugin.send(to, T.t("crates.players-only", "<red>Players only.")); return; }
                Block b = player.getLocation().getBlock();
                int air = 0;
                while (air < 128 && b.getY() > b.getWorld().getMinHeight() && b.getRelative(BlockFace.DOWN).isPassable()) { b = b.getRelative(BlockFace.DOWN); air++; }
                int n = 1;
                while (crates.containsKey("crate" + n)) n++;
                Crate c = new Crate("crate" + n, false, b.getWorld().getName(), b.getX(), b.getY(), b.getZ());
                c.fall = (float) (player.getLocation().getY() - b.getY());
                crates.put(c.id, c);
                save();
                plugin.send(to, T.t("crates.placed", "<green>Placed loot crate <white><id></white>. <gray>It comes back <mins> minutes after it is opened.", "id", c.id, "mins", cfg().getLong("respawn-minutes", 30)));
            }
            case "remove" -> {
                Crate best = args.length > 2 ? crates.get(args[2]) : null;
                if (best == null && player != null) {
                    double bd = 36;
                    for (Crate c : crates.values()) {
                        Location a = c.at();
                        if (c.wild || a == null || a.getWorld() != player.getWorld()) continue;
                        double d = a.add(0.5, 0, 0.5).distanceSquared(player.getLocation());
                        if (d < bd) { bd = d; best = c; }
                    }
                }
                if (best == null || best.wild) { plugin.send(to, T.t("crates.none", "<red>No crate spot within 6 blocks. <gray>/cq crate remove <id>")); return; }
                Crate gone = crates.remove(best.id);
                Location a = gone.at();
                if (a != null) Sched.at(a, () -> hide(gone));
                save();
                plugin.send(to, T.t("crates.removed", "<gray>Removed crate <white><id></white>.", "id", gone.id));
            }
            case "token" -> {
                Player target = args.length > 2 ? Bukkit.getPlayerExact(args[2]) : player;
                if (target == null) { plugin.send(to, T.t("crates.no-player", "<red>No such player online.")); return; }
                int amount = 1;
                try { if (args.length > 3) amount = Integer.parseInt(args[3]); } catch (NumberFormatException ignored) { }
                ItemStack t = token(amount);
                Sched.entity(target, () -> target.getInventory().addItem(t).values().forEach(left -> target.getWorld().dropItem(target.getLocation(), left)));
                plugin.send(to, T.t("crates.token-given", "<green>Gave <white><amount></white> Chest Token(s) to <white><player></white>.", "amount", t.getAmount(), "player", target.getName()));
            }
            case "wild" -> {
                for (Crate c : crates.values()) if (c.wild && c.here()) { Location a = c.at(); if (a != null) Sched.at(a, () -> hide(c)); relocate(c); }
                plugin.send(to, T.t("crates.wild-moved", "<gray>The wild crates are moving to new hiding spots."));
            }
            case "hint" -> { if (player != null) hint(player, 3); }
            default -> {
                plugin.send(to, T.t("crates.list", "<yellow>Loot crates: <white><count></white> <gray>· token odds today: <white>1 in <odds></white> · /cq crate place|remove|token|wild|hint",
                        "count", crates.size(), "odds", String.format(Locale.ROOT, "%,d", odds())));
                long now = System.currentTimeMillis();
                for (Crate c : crates.values())
                    to.sendMessage(Text.mm(" <gray>• <white>" + c.id + "</white> " + c.world + " " + c.x + " " + c.y + " " + c.z
                            + (c.here() ? " <green>here" : c.back > 0 ? " <yellow>back in " + Math.max(1, (c.back - now) / 60_000) + "m" : " <gray>moving")));
            }
        }
    }

    public List<String> ids() { return crates.values().stream().filter(c -> !c.wild).map(c -> c.id).sorted().toList(); }

    // ------------------------------------------------------------------ storage (only the spots ops placed)

    private void load() {
        crates.clear();
        ConfigurationSection root = YamlConfiguration.loadConfiguration(file).getConfigurationSection("crates");
        if (root == null) return;
        for (String id : root.getKeys(false)) {
            ConfigurationSection s = root.getConfigurationSection(id);
            if (s == null) continue;
            Crate c = new Crate(id, false, s.getString("world", "world"), s.getInt("x"), s.getInt("y"), s.getInt("z"));
            c.back = s.getLong("back", 0);
            crates.put(id, c);
        }
    }

    private void save() {
        YamlConfiguration y = new YamlConfiguration();
        for (Crate c : crates.values()) {
            if (c.wild) continue;
            String k = "crates." + c.id + ".";
            y.set(k + "world", c.world); y.set(k + "x", c.x); y.set(k + "y", c.y); y.set(k + "z", c.z); y.set(k + "back", c.back);
        }
        String text = y.saveToString();
        Sched.async(() -> {
            try { java.nio.file.Files.writeString(file.toPath(), text); }
            catch (Exception e) { plugin.getLogger().warning("Could not save crates.yml: " + e.getMessage()); }
        });
    }
}
