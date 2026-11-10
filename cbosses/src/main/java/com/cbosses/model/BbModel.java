package com.cbosses.model;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import org.bukkit.Material;

import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * Blockbench round trip. A boss model goes out as a Blockbench project (groups are bones, each cube is one block
 * display named after its block, animations are Blockbench animations) and an edited project comes back as a
 * model in the models.json shape, keeping the built-in model's attacks, entrance, death and hit zones.
 *
 * Blockbench shows bone rotations with x and y mirrored and positions with x mirrored compared with the game,
 * so those keys flip sign on the way out and back in. Cube rotations are stored the same way in both.
 */
public final class BbModel {
    private BbModel() { }

    private static final String[] FACES = {"north", "east", "south", "west", "up", "down"};
    private static final int TILE = 16;

    // ------------------------------------------------------------------ Blockbench -> game

    /** Converts a .bbmodel into one models.json model; base is the built-in model with the same id, or null. */
    public static JsonObject toModel(String id, JsonObject bb, JsonObject base, Consumer<String> warn) {
        Map<String, JsonObject> elements = new HashMap<>();
        if (bb.has("elements")) for (JsonElement e : bb.getAsJsonArray("elements")) {
            JsonObject o = e.getAsJsonObject();
            String type = o.has("type") ? o.get("type").getAsString() : "cube";
            if (type.equals("cube") && o.has("uuid")) elements.put(o.get("uuid").getAsString(), o);
        }
        JsonArray bones = new JsonArray(), cubes = new JsonArray();
        Map<String, String> boneOf = new LinkedHashMap<>();
        java.util.Set<String> names = new java.util.HashSet<>();
        if (bb.has("outliner")) for (JsonElement node : bb.getAsJsonArray("outliner")) walk(node, null, elements, bones, boneOf, names);
        // cubes left outside every group hang on a root bone
        List<String> loose = new ArrayList<>();
        if (bb.has("outliner")) for (JsonElement node : bb.getAsJsonArray("outliner")) if (node.isJsonPrimitive()) loose.add(node.getAsString());
        if (!loose.isEmpty() || bones.isEmpty()) {
            String root = names.contains("root") ? "root" : unique("root", names);
            if (!names.contains(root)) {
                JsonObject b = new JsonObject();
                b.addProperty("name", root); b.add("parent", null); b.add("pivot", vec(0, 0, 0));
                JsonArray withRoot = new JsonArray(); withRoot.add(b); withRoot.addAll(bones); bones = withRoot; names.add(root);
            }
            for (String u : loose) boneOf.put(u, root);
        }
        int bad = 0;
        float top = 0;
        for (var e : boneOf.entrySet()) {
            JsonObject o = elements.get(e.getKey());
            if (o == null) continue;
            String[] parts = o.has("name") ? o.get("name").getAsString().trim().split("\\|") : new String[]{"stone"};
            String block = parts[0].trim().toLowerCase(Locale.ROOT).replace("minecraft:", "").replace(' ', '_');
            int cut = block.lastIndexOf('.');                     // Blockbench names copies "stone.001"
            if (cut > 0 && block.substring(cut + 1).chars().allMatch(Character::isDigit)) block = block.substring(0, cut);
            Material mat = Material.matchMaterial(ModelRig.base(block));
            if (mat == null || !mat.isBlock() || mat.isAir()) { bad++; block = "white_concrete"; }
            float[] f = arr(o, "from"), t = arr(o, "to");
            JsonObject c = new JsonObject();
            c.addProperty("b", e.getValue());
            c.addProperty("k", block);
            c.add("f", vec(Math.min(f[0], t[0]), Math.min(f[1], t[1]), Math.min(f[2], t[2])));
            c.add("t", vec(Math.max(f[0], t[0]), Math.max(f[1], t[1]), Math.max(f[2], t[2])));
            top = Math.max(top, Math.max(f[1], t[1]));
            float[] r = o.has("rotation") ? arr(o, "rotation") : new float[3];
            if (r[0] != 0 || r[1] != 0 || r[2] != 0) {
                c.add("r", vec(r[0], r[1], r[2]));
                float[] org = o.has("origin") ? arr(o, "origin") : new float[]{(f[0] + t[0]) / 2, (f[1] + t[1]) / 2, (f[2] + t[2]) / 2};
                c.add("o", vec(org[0], org[1], org[2]));
            }
            boolean lit = o.has("light_emission") && o.get("light_emission").getAsInt() > 0;
            for (int i = 1; i < parts.length; i++) {
                String p = parts[i].trim().toLowerCase(Locale.ROOT);
                if (p.equals("lit")) lit = true;
                else if (!p.isEmpty()) c.addProperty("g", p);
            }
            if (lit) c.addProperty("l", 1);
            cubes.add(c);
        }
        if (bad > 0) warn.accept(id + ": " + bad + " cube(s) are not named after a block and became white concrete");
        JsonObject m = new JsonObject();
        m.addProperty("rig", base != null && base.has("rig") ? base.get("rig").getAsString() : "biped");
        m.addProperty("scale", base != null && base.has("scale") ? base.get("scale").getAsFloat() : 1f);
        m.addProperty("height", top);
        m.add("bones", bones);
        m.add("cubes", cubes);
        for (String k : new String[]{"attacks", "melee", "spawn", "death", "hitbox"})
            if (base != null && base.has(k)) m.add(k, base.get(k).deepCopy());
        if (!m.has("spawn")) m.add("spawn", new JsonArray());
        if (!m.has("death")) m.add("death", new JsonArray());
        JsonArray zones = new JsonArray();
        if (base != null && base.has("zones")) for (JsonElement z : base.getAsJsonArray("zones"))
            if (names.contains(z.getAsJsonObject().get("b").getAsString())) zones.add(z.deepCopy());
        m.add("zones", zones);
        JsonObject anims = new JsonObject();
        Map<String, String> boneByUuid = new HashMap<>();
        collectGroups(bb, boneByUuid);
        if (bb.has("animations")) for (JsonElement a : bb.getAsJsonArray("animations")) {
            JsonObject in = a.getAsJsonObject();
            JsonObject out = new JsonObject();
            out.addProperty("length", in.has("length") ? in.get("length").getAsFloat() : 1f);
            if (in.has("loop") && in.get("loop").getAsString().equals("loop")) out.addProperty("loop", true);
            if (in.has("markers") && !in.getAsJsonArray("markers").isEmpty())
                out.addProperty("hit", in.getAsJsonArray("markers").get(0).getAsJsonObject().get("time").getAsFloat());
            JsonObject ab = new JsonObject();
            if (in.has("animators")) for (var an : in.getAsJsonObject("animators").entrySet()) {
                JsonObject animator = an.getValue().getAsJsonObject();
                String bone = boneByUuid.getOrDefault(an.getKey(), animator.has("name") ? animator.get("name").getAsString() : "");
                if (!names.contains(bone) || !animator.has("keyframes")) continue;
                Map<String, List<float[]>> ch = new LinkedHashMap<>();
                for (JsonElement kf : animator.getAsJsonArray("keyframes")) {
                    JsonObject k = kf.getAsJsonObject();
                    String channel = k.get("channel").getAsString();
                    String key = switch (channel) { case "rotation" -> "rot"; case "position" -> "pos"; case "scale" -> "scl"; default -> null; };
                    if (key == null || !k.has("data_points") || k.getAsJsonArray("data_points").isEmpty()) continue;
                    JsonObject p = k.getAsJsonArray("data_points").get(0).getAsJsonObject();
                    float x = num(p, "x"), y = num(p, "y"), z = num(p, "z");
                    if (key.equals("rot")) { x = -x; y = -y; }
                    if (key.equals("pos")) x = -x;
                    ch.computeIfAbsent(key, q -> new ArrayList<>()).add(new float[]{k.get("time").getAsFloat(), x, y, z});
                }
                JsonObject bo = new JsonObject();
                for (var c : ch.entrySet()) {
                    c.getValue().sort((p, q) -> Float.compare(p[0], q[0]));
                    JsonArray keys = new JsonArray();
                    for (float[] v : c.getValue()) { JsonArray k = new JsonArray(); k.add(v[0]); k.add(vec(v[1], v[2], v[3])); keys.add(k); }
                    bo.add(c.getKey(), keys);
                }
                if (!bo.isEmpty()) ab.add(bone, bo);
            }
            out.add("bones", ab);
            if (in.has("name")) anims.add(in.get("name").getAsString(), out);
        }
        m.add("anims", anims);
        return m;
    }

    private static void walk(JsonElement node, String parent, Map<String, JsonObject> elements, JsonArray bones, Map<String, String> boneOf, java.util.Set<String> names) {
        if (!node.isJsonObject()) return;                         // loose cubes are handled by the caller
        JsonObject g = node.getAsJsonObject();
        String name = unique(g.has("name") ? g.get("name").getAsString() : "bone", names);
        names.add(name);
        JsonObject b = new JsonObject();
        b.addProperty("name", name);
        if (parent == null) b.add("parent", null); else b.addProperty("parent", parent);
        float[] o = g.has("origin") ? arr(g, "origin") : new float[3];
        b.add("pivot", vec(o[0], o[1], o[2]));
        if (g.has("rotation")) {
            float[] r = arr(g, "rotation");
            if (r[0] != 0 || r[1] != 0 || r[2] != 0) b.add("rest", vec(r[0], r[1], r[2]));
        }
        bones.add(b);
        if (g.has("children")) for (JsonElement ch : g.getAsJsonArray("children")) {
            if (ch.isJsonPrimitive()) { if (elements.containsKey(ch.getAsString())) boneOf.put(ch.getAsString(), name); }
            else walk(ch, name, elements, bones, boneOf, names);
        }
    }

    private static void collectGroups(JsonObject bb, Map<String, String> out) {
        if (!bb.has("outliner")) return;
        java.util.ArrayDeque<JsonElement> todo = new java.util.ArrayDeque<>();
        bb.getAsJsonArray("outliner").forEach(todo::add);
        while (!todo.isEmpty()) {
            JsonElement n = todo.pop();
            if (!n.isJsonObject()) continue;
            JsonObject g = n.getAsJsonObject();
            if (g.has("uuid") && g.has("name")) out.put(g.get("uuid").getAsString(), g.get("name").getAsString());
            if (g.has("children")) g.getAsJsonArray("children").forEach(todo::add);
        }
    }

    private static String unique(String name, java.util.Set<String> taken) {
        if (!taken.contains(name)) return name;
        int i = 2;
        while (taken.contains(name + i)) i++;
        return name + i;
    }

    // ------------------------------------------------------------------ game -> Blockbench

    /** A Blockbench project for one models.json model; rigAnims are the shared animations of its rig. */
    public static JsonObject toBlockbench(String id, JsonObject m, JsonObject rigAnims) {
        List<String> blocks = new ArrayList<>();
        for (JsonElement c : m.getAsJsonArray("cubes")) {
            String k = c.getAsJsonObject().get("k").getAsString();
            if (!blocks.contains(k)) blocks.add(k);
        }
        int cols = 1;
        while (cols * cols < Math.max(1, blocks.size())) cols++;
        int rows = Math.max(1, (blocks.size() + cols - 1) / cols);
        BufferedImage img = new BufferedImage(cols * TILE, rows * TILE, BufferedImage.TYPE_INT_ARGB);
        for (int i = 0; i < blocks.size(); i++) {
            int rgb = colour(blocks.get(i)), tx = i % cols * TILE, ty = i / cols * TILE;
            int dark = shade(rgb, 0.8f);
            for (int y = 0; y < TILE; y++) for (int x = 0; x < TILE; x++)
                img.setRGB(tx + x, ty + y, 0xff000000 | (((x * 7 + y * 13 + (x / 4) * 5 + i) % 11) < 3 ? dark : rgb));
        }
        JsonArray elements = new JsonArray();
        Map<String, JsonArray> children = new LinkedHashMap<>();
        int i = 0;
        for (JsonElement ce : m.getAsJsonArray("cubes")) {
            JsonObject c = ce.getAsJsonObject();
            String k = c.get("k").getAsString();
            int at = blocks.indexOf(k), tx = at % cols * TILE, ty = at / cols * TILE;
            JsonObject e = new JsonObject();
            String name = k + (c.has("g") ? "|" + c.get("g").getAsString() : "") + (c.has("l") ? "|lit" : "");
            e.addProperty("name", name);
            e.addProperty("box_uv", false);
            e.addProperty("rescale", false);
            e.addProperty("locked", false);
            e.addProperty("light_emission", c.has("l") ? 15 : 0);
            e.add("from", c.get("f").deepCopy());
            e.add("to", c.get("t").deepCopy());
            e.addProperty("autouv", 0);
            e.addProperty("color", i % 8);
            float[] f = arr(c, "f"), t = arr(c, "t");
            e.add("origin", c.has("o") ? c.get("o").deepCopy() : vec((f[0] + t[0]) / 2, (f[1] + t[1]) / 2, (f[2] + t[2]) / 2));
            e.add("rotation", c.has("r") ? c.get("r").deepCopy() : vec(0, 0, 0));
            JsonObject faces = new JsonObject();
            for (String face : FACES) {
                JsonObject fo = new JsonObject();
                JsonArray uv = new JsonArray(); uv.add(tx); uv.add(ty); uv.add(tx + TILE); uv.add(ty + TILE);
                fo.add("uv", uv); fo.addProperty("texture", 0);
                faces.add(face, fo);
            }
            e.add("faces", faces);
            e.addProperty("type", "cube");
            String u = uuid(id, "cube", i++);
            e.addProperty("uuid", u);
            elements.add(e);
            children.computeIfAbsent(c.get("b").getAsString(), q -> new JsonArray()).add(u);
        }
        Map<String, JsonObject> groups = new LinkedHashMap<>();
        JsonArray outliner = new JsonArray();
        for (JsonElement be : m.getAsJsonArray("bones")) {
            JsonObject b = be.getAsJsonObject();
            String name = b.get("name").getAsString();
            JsonObject g = new JsonObject();
            g.addProperty("name", name);
            g.add("origin", b.get("pivot").deepCopy());
            g.add("rotation", b.has("rest") ? b.get("rest").deepCopy() : vec(0, 0, 0));
            g.addProperty("uuid", uuid(id, "bone", name));
            g.addProperty("export", true);
            g.addProperty("isOpen", false);
            g.addProperty("visibility", true);
            g.add("children", children.getOrDefault(name, new JsonArray()));
            groups.put(name, g);
            String parent = b.has("parent") && !b.get("parent").isJsonNull() ? b.get("parent").getAsString() : null;
            if (parent != null && groups.containsKey(parent)) groups.get(parent).getAsJsonArray("children").add(g);
            else outliner.add(g);
        }
        Map<String, JsonObject> all = new LinkedHashMap<>();
        if (rigAnims != null) for (var a : rigAnims.entrySet()) all.put(a.getKey(), a.getValue().getAsJsonObject());
        if (m.has("anims")) for (var a : m.getAsJsonObject("anims").entrySet()) all.put(a.getKey(), a.getValue().getAsJsonObject());
        JsonArray animations = new JsonArray();
        for (var a : all.entrySet()) {
            JsonObject in = a.getValue(), out = new JsonObject();
            out.addProperty("uuid", uuid(id, "anim", a.getKey()));
            out.addProperty("name", a.getKey());
            out.addProperty("loop", in.has("loop") && in.get("loop").getAsBoolean() ? "loop" : "once");
            out.addProperty("override", false);
            out.addProperty("length", in.has("length") ? in.get("length").getAsFloat() : 1f);
            out.addProperty("snapping", 20);
            JsonObject animators = new JsonObject();
            if (in.has("bones")) for (var b : in.getAsJsonObject("bones").entrySet()) {
                if (!groups.containsKey(b.getKey())) continue;
                JsonArray keys = new JsonArray();
                JsonObject ch = b.getValue().getAsJsonObject();
                String[][] map = {{"rot", "rotation"}, {"pos", "position"}, {"scl", "scale"}};
                for (String[] cm : map) if (ch.has(cm[0])) {
                    int n = 0;
                    for (JsonElement ke : ch.getAsJsonArray(cm[0])) {
                        JsonArray k = ke.getAsJsonArray(), v = k.get(1).getAsJsonArray();
                        float x = v.get(0).getAsFloat(), y = v.get(1).getAsFloat(), z = v.get(2).getAsFloat();
                        if (cm[0].equals("rot")) { x = -x; y = -y; }
                        if (cm[0].equals("pos")) x = -x;
                        JsonObject kf = new JsonObject(), p = new JsonObject();
                        kf.addProperty("channel", cm[1]);
                        p.addProperty("x", x); p.addProperty("y", y); p.addProperty("z", z);
                        JsonArray dp = new JsonArray(); dp.add(p);
                        kf.add("data_points", dp);
                        kf.addProperty("uuid", uuid(id, a.getKey() + "/" + b.getKey() + "/" + cm[0], n++));
                        kf.addProperty("time", k.get(0).getAsFloat());
                        kf.addProperty("color", -1);
                        kf.addProperty("interpolation", "linear");
                        keys.add(kf);
                    }
                }
                if (keys.isEmpty()) continue;
                JsonObject an = new JsonObject();
                an.addProperty("name", b.getKey()); an.addProperty("type", "bone"); an.add("keyframes", keys);
                animators.add(groups.get(b.getKey()).get("uuid").getAsString(), an);
            }
            out.add("animators", animators);
            JsonArray markers = new JsonArray();
            if (in.has("hit") && in.get("hit").getAsFloat() >= 0) {
                JsonObject mk = new JsonObject(); mk.addProperty("color", 0); mk.addProperty("time", in.get("hit").getAsFloat()); markers.add(mk);
            }
            out.add("markers", markers);
            animations.add(out);
        }
        JsonObject meta = new JsonObject();
        meta.addProperty("format_version", "4.10"); meta.addProperty("model_format", "free"); meta.addProperty("box_uv", false);
        JsonObject res = new JsonObject();
        res.addProperty("width", cols * TILE); res.addProperty("height", rows * TILE);
        JsonObject tex = new JsonObject();
        tex.addProperty("path", ""); tex.addProperty("name", "blocks.png"); tex.addProperty("folder", ""); tex.addProperty("namespace", "");
        tex.addProperty("id", "0"); tex.addProperty("width", cols * TILE); tex.addProperty("height", rows * TILE);
        tex.addProperty("uv_width", cols * TILE); tex.addProperty("uv_height", rows * TILE); tex.addProperty("particle", false);
        tex.addProperty("render_mode", "default"); tex.addProperty("visible", true); tex.addProperty("internal", true);
        tex.addProperty("saved", false); tex.addProperty("uuid", uuid(id, "texture", 0)); tex.addProperty("source", png(img));
        JsonArray textures = new JsonArray(); textures.add(tex);
        JsonObject out = new JsonObject();
        out.add("meta", meta);
        out.addProperty("name", id);
        out.addProperty("model_identifier", id);
        out.add("resolution", res);
        out.add("elements", elements);
        out.add("outliner", outliner);
        out.add("textures", textures);
        out.add("animations", animations);
        return out;
    }

    private static int colour(String block) {
        try {
            Material mat = Material.matchMaterial(ModelRig.base(block));
            if (mat != null && mat.isBlock()) return mat.createBlockData().getMapColor().asRGB();
        } catch (Throwable ignored) { }   // a server without map colours just gets grey cubes
        return 0xb0b0b0;
    }

    private static int shade(int rgb, float f) {
        int r = (int) (((rgb >> 16) & 255) * f), g = (int) (((rgb >> 8) & 255) * f), b = (int) ((rgb & 255) * f);
        return (r << 16) | (g << 8) | b;
    }

    private static String png(BufferedImage img) {
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            javax.imageio.ImageIO.write(img, "png", out);
            return "data:image/png;base64," + Base64.getEncoder().encodeToString(out.toByteArray());
        } catch (IOException e) { return ""; }
    }

    private static String uuid(String id, String kind, int n) {
        return UUID.nameUUIDFromBytes(("cbosses/" + id + "/" + kind + "/" + n).getBytes(StandardCharsets.UTF_8)).toString();
    }

    private static String uuid(String id, String kind, String name) {
        return UUID.nameUUIDFromBytes(("cbosses/" + id + "/" + kind + "/" + name).getBytes(StandardCharsets.UTF_8)).toString();
    }

    private static float[] arr(JsonObject o, String key) {
        JsonArray a = o.getAsJsonArray(key);
        return new float[]{a.get(0).getAsFloat(), a.get(1).getAsFloat(), a.get(2).getAsFloat()};
    }

    private static float num(JsonObject o, String key) {
        if (!o.has(key)) return 0;
        JsonElement e = o.get(key);
        if (e.isJsonPrimitive() && e.getAsJsonPrimitive().isNumber()) return e.getAsFloat();
        try { return Float.parseFloat(e.getAsString().trim()); } catch (RuntimeException ex) { return 0; }   // Molang text: ignored
    }

    private static JsonArray vec(float x, float y, float z) {
        JsonArray a = new JsonArray(); a.add(x); a.add(y); a.add(z); return a;
    }
}
