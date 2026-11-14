package com.cbosses.decor;

import com.cbosses.CBossesPlugin;
import com.cbosses.T;
import com.cbosses.model.BossModel;
import com.cbosses.model.ModelRig;
import com.cbosses.util.Sched;
import io.papermc.paper.threadedregions.scheduler.ScheduledTask;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.World;
import org.bukkit.block.data.BlockData;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Player;
import org.bukkit.util.Transformation;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;

/**
 * Decorations ops place (/cbosses decor place <model>): a block model that just sits there, pulls faces
 * (mostly happy, now and then sad) and now and then hops in place, like the carved pumpkins, gingerbread
 * people and Easter eggs. One goes on top of the block you look at, or on top of the decoration already
 * standing there, so they stack. They are drawn only while a player is within 48 blocks and taken away
 * again when nobody is near, so a decoration costs nothing in empty chunks and is never saved into the
 * world; their places are kept in decor.yml.
 */
public final class Decor {
    private static final double SHOW = 48, HIDE = 64;

    static final class Piece {
        final String id, model, world;
        final double x, z;
        volatile double y;
        final float yaw;
        volatile List<BlockDisplay> parts;
        volatile String face = "idle";
        volatile long nextFace;
        Piece(String id, String model, String world, double x, double y, double z, float yaw) {
            this.id = id; this.model = model; this.world = world; this.x = x; this.y = y; this.z = z; this.yaw = yaw;
        }
        Location at() { World w = Bukkit.getWorld(world); return w == null ? null : new Location(w, x, y, z); }
    }

    private final CBossesPlugin plugin;
    private final Map<String, Piece> pieces = new ConcurrentHashMap<>();
    private ScheduledTask timer;
    private File file;

    public Decor(CBossesPlugin plugin) { this.plugin = plugin; }

    public List<String> models() {
        List<String> out = new ArrayList<>();
        for (String id : plugin.service().modelIds()) if (id.startsWith("decor_")) out.add(id);
        out.sort(null);
        return out;
    }

    public void start() {
        stop();
        load();
        timer = Sched.globalTimer(t -> tick(), 40, 10);
    }

    public void stop() {
        if (timer != null) { timer.cancel(); timer = null; }
        for (Piece p : pieces.values()) hide(p);
    }

    private void tick() {
        long now = System.currentTimeMillis();
        for (Piece p : pieces.values()) {
            Location at = p.at();
            if (at == null) continue;
            Sched.at(at, () -> {
                boolean near = false, far = true;
                for (Player pl : at.getNearbyPlayers(HIDE)) {
                    far = false;
                    if (pl.getLocation().distanceSquared(at) < SHOW * SHOW) { near = true; break; }
                }
                List<BlockDisplay> parts = p.parts;
                if (parts != null && (far || !parts.get(0).isValid())) { hide(p); return; }
                if (parts == null && near) show(p, at);
                else if (parts != null && now >= p.nextFace) changeFace(p, at);
            });
        }
    }

    private Matrix4f[] pose(Piece p, ModelRig.Model m) {
        Matrix4f[] cubes = ModelRig.cubes(m, ModelRig.pose(m, List.of(new ModelRig.Layer(m.anim("idle"), 0, 1))));
        m.showFace(cubes, p.face);
        Matrix4f turn = new Matrix4f().rotationY((float) Math.toRadians(-p.yaw));
        for (int i = 0; i < cubes.length; i++) cubes[i] = new Matrix4f(turn).mul(cubes[i]);
        return cubes;
    }

    private void show(Piece p, Location at) {
        ModelRig.Model m = plugin.service().model(p.model);
        if (m == null) return;
        Matrix4f[] pose = pose(p, m);
        List<BlockDisplay> parts = new ArrayList<>(m.cubes.size());
        Location base = at.clone(); base.setYaw(0); base.setPitch(0);
        for (int i = 0; i < m.cubes.size(); i++) {
            ModelRig.Cube c = m.cubes.get(i);
            BlockData data;
            try { data = Bukkit.createBlockData(c.block().contains(":") ? c.block() : "minecraft:" + c.block()); }
            catch (IllegalArgumentException e) { Material mat = Material.matchMaterial(c.base()); data = (mat != null && mat.isBlock() ? mat : Material.STONE).createBlockData(); }
            BlockData d0 = data;
            Transformation tf = BossModel.transformation(pose[i]);
            parts.add(at.getWorld().spawn(base, BlockDisplay.class, e -> {
                e.setPersistent(false);
                e.setBlock(d0);
                e.setTransformation(tf);
                e.setViewRange(0.75f);
                e.setShadowRadius(0);
                e.setInterpolationDuration(3);
                if (c.light()) e.setBrightness(new Display.Brightness(15, 15));
            }));
        }
        p.parts = parts;
        p.nextFace = System.currentTimeMillis() + 1500;
    }

    private void changeFace(Piece p, Location at) {
        ModelRig.Model m = plugin.service().model(p.model);
        if (m == null || m.faces.size() < 2) return;
        ThreadLocalRandom r = ThreadLocalRandom.current();
        List<String> faces = new ArrayList<>(m.faces);
        faces.removeAll(List.of(p.face, "dead", "sad"));
        if (m.faces.contains("sad") && r.nextInt(7) == 0) p.face = "sad";
        else if (m.faces.contains("happy") && !p.face.equals("happy") && r.nextInt(5) < 2) p.face = "happy";
        else if (!faces.isEmpty()) p.face = faces.get(r.nextInt(faces.size()));
        p.nextFace = System.currentTimeMillis() + r.nextLong(1800, 4200);
        boolean hop = r.nextInt(3) == 0 && above(p) == null;
        Matrix4f[] pose = pose(p, m);
        if (hop) { hop(p, m, at, pose); return; }
        send(p, m, pose, 0, 3, true);
        // a little puff and sound when it changes its face, only close by
        at.getWorld().spawnParticle(org.bukkit.Particle.SMOKE, at.clone().add(0, 1.2, 0), 3, 0.3, 0.2, 0.3, 0.01);
        if (ThreadLocalRandom.current().nextInt(4) == 0)
            at.getWorld().playSound(at, org.bukkit.Sound.BLOCK_WOOD_HIT, 0.4f, 0.6f + ThreadLocalRandom.current().nextFloat() * 0.6f);
    }

    /** Sends a pose to the parts (only the face plates when faceOnly), offset up by lift and squashed by squash. */
    private void send(Piece p, ModelRig.Model m, Matrix4f[] pose, float lift, int ticks, boolean faceOnly) {
        send(p, m, pose, lift, 1, ticks, faceOnly);
    }

    private void send(Piece p, ModelRig.Model m, Matrix4f[] pose, float lift, float squash, int ticks, boolean faceOnly) {
        List<BlockDisplay> parts = p.parts;
        if (parts == null) return;
        Matrix4f move = new Matrix4f().translation(0, lift, 0).scale(1 + (1 - squash) * 0.8f, squash, 1 + (1 - squash) * 0.8f);
        for (int i = 0; i < parts.size() && i < pose.length; i++) {
            if (faceOnly && m.faceOf[i] == null) continue;
            BlockDisplay d = parts.get(i);
            if (!d.isValid()) continue;
            d.setInterpolationDelay(0);
            d.setInterpolationDuration(ticks);
            d.setTransformation(BossModel.transformation(new Matrix4f(move).mul(pose[i])));
        }
    }

    /** A little hop in place: crouch, up, land with a squash, back to shape. Only when nothing stands on it. */
    private void hop(Piece p, ModelRig.Model m, Location at, Matrix4f[] pose) {
        List<BlockDisplay> parts = p.parts;
        send(p, m, pose, 0, 0.88f, 2, false);
        int[][] keys = {{2, 4, 30}, {6, 3, 0}, {9, 3, -1}};          // tick, length, lift in hundredths (-1: squash)
        for (int[] k : keys) Bukkit.getRegionScheduler().runDelayed(plugin, at, t -> {
            if (p.parts != parts) return;                               // hidden or shown again meanwhile
            if (k[2] < 0) send(p, m, pose, 0, 0.9f, k[1], false);
            else send(p, m, pose, k[2] / 100f, 1, k[1], false);
        }, k[0]);
        Bukkit.getRegionScheduler().runDelayed(plugin, at, t -> { if (p.parts == parts) send(p, m, pose, 0, 1, 3, false); }, 12);
        at.getWorld().playSound(at, org.bukkit.Sound.ENTITY_SLIME_JUMP_SMALL, 0.35f, 1.3f + ThreadLocalRandom.current().nextFloat() * 0.4f);
    }

    /** The decoration standing right on top of this one, if any. */
    private Piece above(Piece p) {
        double top = p.y + height(p);
        for (Piece o : pieces.values())
            if (o != p && o.world.equals(p.world) && Math.abs(o.x - p.x) < 0.01 && Math.abs(o.z - p.z) < 0.01 && Math.abs(o.y - top) < 0.02) return o;
        return null;
    }

    private double height(Piece p) {
        ModelRig.Model m = plugin.service().model(p.model);
        return m == null ? 1 : m.blocks();
    }

    /** The y a new decoration sits at in this column: on the block, or on top of the stack already there. */
    private double top(String world, double x, double y, double z) {
        for (boolean moved = true; moved; ) {
            moved = false;
            for (Piece o : pieces.values())
                if (o.world.equals(world) && Math.abs(o.x - x) < 0.01 && Math.abs(o.z - z) < 0.01 && Math.abs(o.y - y) < 0.02) { y = o.y + height(o); moved = true; break; }
        }
        return y;
    }

    private void hide(Piece p) {
        List<BlockDisplay> parts = p.parts;
        p.parts = null;
        if (parts == null) return;
        for (BlockDisplay d : parts) {
            if (!d.isValid()) continue;
            try { if (Bukkit.isOwnedByCurrentRegion(d)) d.remove(); else d.getScheduler().run(plugin, t -> d.remove(), null); }
            catch (RuntimeException ignored) { }
        }
    }

    // ------------------------------------------------------------------ commands

    public void command(CommandSender to, Player player, String label, String[] args) {
        String what = args.length > 1 ? args[1].toLowerCase(java.util.Locale.ROOT) : "list";
        switch (what) {
            case "place" -> {
                if (player == null) { plugin.send(to, T.t("command.players-only", "<red>Players only.")); return; }
                String model = args.length > 2 ? args[2].toLowerCase(java.util.Locale.ROOT) : null;
                if (model == null || plugin.service().model(model) == null) {
                    plugin.send(to, T.t("decor.models", "<yellow>/<label> decor place <model> <gray>Models: <white><list>", "label", label, "list", String.join(", ", models())));
                    return;
                }
                Location l = player.getLocation();
                int n = pieces.size() + 1;
                while (pieces.containsKey("decor" + n)) n++;
                // on top of the block looked at (or of the decorations already stacked there), facing the player
                org.bukkit.block.Block hit = player.getTargetBlockExact(6);
                org.bukkit.block.Block on = hit != null && hit.getType().isSolid() ? hit.getRelative(org.bukkit.block.BlockFace.UP) : l.getBlock();
                String w = l.getWorld().getName();
                double x = on.getX() + 0.5, z = on.getZ() + 0.5;
                Piece p = new Piece("decor" + n, model, w, x, top(w, x, on.getY(), z), z, Math.round((l.getYaw() + 180) / 90f) * 90f);
                pieces.put(p.id, p);
                save();
                plugin.send(to, T.t("decor.placed", "<green>Placed <white><model></white> (<id>). <gray>Remove it with /<label> decor remove", "model", model, "id", p.id, "label", label));
            }
            case "remove" -> {
                Piece best = null;
                if (args.length > 2) best = pieces.get(args[2]);
                else if (player != null) {
                    double bd = 6 * 6;
                    for (Piece p : pieces.values()) {
                        Location a = p.at();
                        if (a == null || a.getWorld() != player.getWorld()) continue;
                        double d = a.distanceSquared(player.getLocation());
                        if (d < bd) { bd = d; best = p; }
                    }
                }
                if (best == null) { plugin.send(to, T.t("decor.none", "<red>No decoration within 6 blocks. <gray>/<label> decor remove <id>", "label", label)); return; }
                Piece gone = best;
                // whatever was stacked on it comes down by its height
                List<Piece> stack = new ArrayList<>();
                for (Piece up = above(gone); up != null && !stack.contains(up); up = above(up)) stack.add(up);
                double drop = height(gone);
                pieces.remove(gone.id);
                Location a = gone.at();
                for (Piece up : stack) { if (a != null) Sched.at(a, () -> hide(up)); up.y -= drop; }
                if (a != null) Sched.at(a, () -> hide(gone)); else hide(gone);
                save();
                plugin.send(to, T.t("decor.removed", "<gray>Removed <white><id></white>.", "id", gone.id));
            }
            default -> {
                plugin.send(to, T.t("decor.list", "<yellow>Decorations: <white><count></white> <gray>· models: <white><list>", "count", pieces.size(), "list", String.join(", ", models())));
                for (Piece p : pieces.values())
                    to.sendMessage(com.cbosses.util.Text.mm(" <gray>• <white>" + p.id + "</white> " + p.model + " " + p.world + " " + (int) p.x + " " + (int) p.y + " " + (int) p.z));
            }
        }
    }

    public List<String> ids() { return new ArrayList<>(pieces.keySet()); }

    // ------------------------------------------------------------------ storage

    private void load() {
        file = new File(plugin.getDataFolder(), "decor.yml");
        pieces.clear();
        YamlConfiguration y = YamlConfiguration.loadConfiguration(file);
        ConfigurationSection root = y.getConfigurationSection("decor");
        if (root == null) return;
        for (String id : root.getKeys(false)) {
            ConfigurationSection c = root.getConfigurationSection(id);
            if (c == null) continue;
            pieces.put(id, new Piece(id, c.getString("model", ""), c.getString("world", "world"), c.getDouble("x"), c.getDouble("y"), c.getDouble("z"), (float) c.getDouble("yaw")));
        }
    }

    private void save() {
        if (file == null) return;
        YamlConfiguration y = new YamlConfiguration();
        for (Piece p : pieces.values()) {
            String k = "decor." + p.id + ".";
            y.set(k + "model", p.model); y.set(k + "world", p.world); y.set(k + "x", p.x); y.set(k + "y", p.y); y.set(k + "z", p.z); y.set(k + "yaw", p.yaw);
        }
        String text = y.saveToString();
        File f = file;
        Sched.async(() -> {
            try { java.nio.file.Files.writeString(f.toPath(), text); }
            catch (Exception e) { plugin.getLogger().warning("Could not save decor.yml: " + e.getMessage()); }
        });
    }
}
