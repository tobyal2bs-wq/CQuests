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
 * Decorations ops place (/cbosses decor place <model>): a block model that just sits there and pulls faces,
 * like the three carved pumpkins. They are drawn only while a player is within 48 blocks and taken away
 * again when nobody is near, so a decoration costs nothing in empty chunks and is never saved into the
 * world; their places are kept in decor.yml.
 */
public final class Decor {
    private static final double SHOW = 48, HIDE = 64;

    static final class Piece {
        final String id, model, world;
        final double x, y, z;
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
        List<String> faces = new ArrayList<>(m.faces);
        faces.remove(p.face);
        faces.remove("dead");
        p.face = faces.get(ThreadLocalRandom.current().nextInt(faces.size()));
        p.nextFace = System.currentTimeMillis() + ThreadLocalRandom.current().nextLong(1800, 4200);
        Matrix4f[] pose = pose(p, m);
        List<BlockDisplay> parts = p.parts;
        for (int i = 0; i < parts.size() && i < pose.length; i++) {
            if (m.faceOf[i] == null) continue;
            BlockDisplay d = parts.get(i);
            if (!d.isValid()) continue;
            d.setInterpolationDelay(0);
            d.setTransformation(BossModel.transformation(pose[i]));
        }
        // a little puff and sound when it changes its face, only close by
        at.getWorld().spawnParticle(org.bukkit.Particle.SMOKE, at.clone().add(0, 1.2, 0), 3, 0.3, 0.2, 0.3, 0.01);
        if (ThreadLocalRandom.current().nextInt(4) == 0)
            at.getWorld().playSound(at, org.bukkit.Sound.BLOCK_WOOD_HIT, 0.4f, 0.6f + ThreadLocalRandom.current().nextFloat() * 0.6f);
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
                // it faces the player who placed it
                Piece p = new Piece("decor" + n, model, l.getWorld().getName(), l.getBlockX() + 0.5, l.getBlockY(), l.getBlockZ() + 0.5, Math.round((l.getYaw() + 180) / 90f) * 90f);
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
                pieces.remove(gone.id);
                Location a = gone.at();
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
