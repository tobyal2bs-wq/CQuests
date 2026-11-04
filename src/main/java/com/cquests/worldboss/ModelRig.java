package com.cquests.worldboss;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * The block models of the bosses (worldboss-models.json, written by tools/worldboss). A model is
 * bones (pivots in model pixels, 16 = one block at scale 1) and cubes (a block stretched between two
 * corners). Animations are keyframes per bone, shared by every boss on the same rig. Pure data and
 * maths, so it is checked without a server.
 *
 * Spawn and death are lists of steps played on the cubes. Each step has an op, a start tick (at), a
 * blend time (dur) and can be spread over the cubes (stagger, order up/down/out/in/random) or limited
 * to some of them (only: lit, unlit, a block id, a bone name prefix, or a detail tag: vein, trim, detail, or plain for the untagged blocks). Ops: pose (back to the model's
 * shape), move, drop (fall to the floor), burst (fly outward), toward (pull to a point), shrink, scale,
 * spin, tilt, swap (change block, "" = the original), light, anim (play a rig animation), fx
 * (particles, sound, lightning), fling (thrown in an arc that lands and bounces), shatter (the block
 * breaks into flying shards), flash (every block turns white or red for a moment) and shake (the whole
 * model trembles). "only" can start with ! to mean everything except.
 */
public final class ModelRig {

    public static final Set<String> OPS = Set.of("pose", "move", "drop", "burst", "toward", "shrink", "scale", "spin", "tilt",
            "swap", "light", "anim", "fx", "fling", "shatter", "flash", "shake");
    public static final Set<String> ORDERS = Set.of("none", "up", "down", "out", "in", "random");

    /** Keyframes: times and xyz values, eased between keys like the preview does. */
    public record Keys(float[] times, float[][] values) {
        void sample(float t, float[] out) {
            int n = times.length;
            if (t <= times[0]) { copy(values[0], out); return; }
            for (int i = 1; i < n; i++) {
                if (t <= times[i]) {
                    float p = (t - times[i - 1]) / Math.max(1e-6f, times[i] - times[i - 1]);
                    p = p * p * (3 - 2 * p);
                    float[] a = values[i - 1], b = values[i];
                    for (int k = 0; k < 3; k++) out[k] = a[k] + (b[k] - a[k]) * p;
                    return;
                }
            }
            copy(values[n - 1], out);
        }

        private static void copy(float[] v, float[] out) { out[0] = v[0]; out[1] = v[1]; out[2] = v[2]; }
    }

    public record Channel(Keys rot, Keys pos, Keys scl) {}

    public record Anim(String name, float length, boolean loop, float hit, Map<String, Channel> bones) {
        float local(float t) {
            if (loop) { float m = t % length; return m < 0 ? m + length : m; }
            return Math.min(t, length);
        }
    }

    public record Bone(String name, int parent, Vector3f pivot, Vector3f rest) {}

    /** One block of the model; {@code local} places a unit block in its bone, in model pixels. */
    public record Cube(int bone, String block, String base, Matrix4f local, boolean light, float centerY, String tag) {}

    /** How much fine detail the models keep (effects.model-detail): 2 = everything, 1 = no surface
     * patches, 0 = no patches, trims or fringes either. Glowing veins always stay. Set before load. */
    public static volatile int detail = 2;

    static boolean keep(String tag) {
        if (tag.equals("detail")) return detail >= 2;
        if (tag.equals("trim")) return detail >= 1;
        return true;
    }

    public record Step(String op, int at, int dur, int stagger, String order, String only, JsonObject params) {
        public float num(String key, float def) {
            JsonElement e = params.get(key);
            return e == null || !e.isJsonPrimitive() ? def : e.getAsFloat();
        }
        public String str(String key, String def) {
            JsonElement e = params.get(key);
            return e == null || !e.isJsonPrimitive() ? def : e.getAsString();
        }
        public boolean flag(String key) {
            JsonElement e = params.get(key);
            return e != null && e.isJsonPrimitive() && e.getAsBoolean();
        }
        public float[] vec(String key) {
            JsonElement e = params.get(key);
            if (e == null || !e.isJsonArray() || e.getAsJsonArray().size() < 2) return null;
            JsonArray a = e.getAsJsonArray();
            float[] v = new float[a.size()];
            for (int i = 0; i < v.length; i++) v[i] = a.get(i).getAsFloat();
            return v;
        }
        /** Last tick this step touches any cube. */
        public int end() { return at + stagger + dur; }
    }

    public static final class Model {
        public final String id, rig;
        public final float scale, height;
        public final List<Bone> bones;
        public final List<Cube> cubes;
        public final Map<String, String> attacks;
        public final String melee;
        public final List<Step> spawn, death;
        public final Map<String, Anim> anims;
        final Map<String, Integer> boneIndex = new HashMap<>();
        /** Hit zones, and how tall the real mob's hitbox is next to the model (0..1). */
        public List<Zone> zones = List.of();
        public float hitbox = 1f;
        /** Cubes on a bone named shell...: only shown during the entrance (an egg, a crate, a cocoon). */
        public boolean[] entranceOnly = new boolean[0];

        Model(String id, String rig, float scale, float height, List<Bone> bones, List<Cube> cubes, Map<String, String> attacks,
              String melee, List<Step> spawn, List<Step> death, Map<String, Anim> anims) {
            this.id = id; this.rig = rig; this.scale = scale; this.height = height; this.bones = bones; this.cubes = cubes;
            this.attacks = attacks; this.melee = melee; this.spawn = spawn; this.death = death; this.anims = anims;
            for (int i = 0; i < bones.size(); i++) boneIndex.put(bones.get(i).name(), i);
        }

        /** Height in blocks. */
        public float blocks() { return height * scale / 16f; }

        public Anim anim(String name) { return name == null ? null : anims.get(name); }

        /** The animation an ability plays, or the melee swing when the model has none for it. */
        public String attackFor(String ability) { return attacks.getOrDefault(ability, melee); }

        /** Distinct attack animations this boss can play (attacks plus the melee swing). */
        public Set<String> attackAnimations() {
            Set<String> out = new java.util.LinkedHashSet<>(attacks.values());
            if (melee != null) out.add(melee);
            return out;
        }

        /** Does a step's "only" filter include this cube. */
        public boolean matches(String only, int cube) {
            if (only == null || only.isEmpty() || only.equals("all")) return true;
            if (only.startsWith("!")) return !matches(only.substring(1), cube);
            Cube c = cubes.get(cube);
            if (only.equals("lit")) return c.light();
            if (only.equals("unlit")) return !c.light();
            if (c.base().equals(only)) return true;
            if (!c.tag().isEmpty() && c.tag().equals(only)) return true;
            if (only.equals("plain")) return c.tag().isEmpty();
            return bones.get(c.bone()).name().startsWith(only);
        }
    }

    public record Layer(Anim anim, float time, float weight) {}

    /**
     * A part of the body players can hit: head, weak spot, body, arm, tail, weapon or armour. The centre
     * is in model pixels before posing (it follows its bone), w and h in model pixels; mult scales the
     * damage of a hit there.
     */
    public record Zone(String kind, int bone, Vector3f center, float w, float h, float mult) {}

    private ModelRig() {}

    // ------------------------------------------------------------------ loading

    public static Map<String, Model> load(Reader reader) {
        JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
        Map<String, Map<String, Anim>> rigs = new HashMap<>();
        for (var rig : root.getAsJsonObject("rigs").entrySet()) {
            Map<String, Anim> anims = new HashMap<>();
            for (var a : rig.getValue().getAsJsonObject().entrySet()) anims.put(a.getKey(), anim(a.getKey(), a.getValue().getAsJsonObject()));
            rigs.put(rig.getKey(), Collections.unmodifiableMap(anims));
        }
        Map<String, Model> out = new LinkedHashMap<>();
        for (var e : root.getAsJsonObject("models").entrySet()) {
            JsonObject m = e.getValue().getAsJsonObject();
            String rig = m.get("rig").getAsString();
            Map<String, Anim> anims = rigs.get(rig);
            if (anims == null) throw new IllegalArgumentException(e.getKey() + ": unknown rig " + rig);
            List<Bone> bones = new ArrayList<>();
            Map<String, Integer> index = new HashMap<>();
            for (JsonElement b : m.getAsJsonArray("bones")) {
                JsonObject o = b.getAsJsonObject();
                String name = o.get("name").getAsString();
                int parent = o.get("parent") == null || o.get("parent").isJsonNull() ? -1 : index.getOrDefault(o.get("parent").getAsString(), -2);
                if (parent == -2) throw new IllegalArgumentException(e.getKey() + ": bone " + name + " has an unknown parent");
                index.put(name, bones.size());
                bones.add(new Bone(name, parent, vec3(o.getAsJsonArray("pivot")), o.has("rest") ? vec3(o.getAsJsonArray("rest")) : new Vector3f()));
            }
            List<Cube> cubes = new ArrayList<>();
            for (JsonElement c : m.getAsJsonArray("cubes")) {
                JsonObject o = c.getAsJsonObject();
                Integer bone = index.get(o.get("b").getAsString());
                if (bone == null) throw new IllegalArgumentException(e.getKey() + ": cube on unknown bone " + o.get("b").getAsString());
                Vector3f f = vec3(o.getAsJsonArray("f")), t = vec3(o.getAsJsonArray("t"));
                Matrix4f local = new Matrix4f();
                if (o.has("r")) {
                    Vector3f r = vec3(o.getAsJsonArray("r")), origin = vec3(o.getAsJsonArray("o"));
                    local.translate(origin).rotateZ(rad(r.z)).rotateY(rad(r.y)).rotateX(rad(r.x)).translate(-origin.x, -origin.y, -origin.z);
                }
                local.translate(f).scale(t.x - f.x, t.y - f.y, t.z - f.z);
                String block = o.get("k").getAsString();
                String tag = o.has("g") ? o.get("g").getAsString() : "";
                if (!keep(tag)) continue;
                cubes.add(new Cube(bone, block, base(block), local, o.has("l"), (f.y + t.y) / 2, tag));
            }
            Map<String, String> attacks = new LinkedHashMap<>();
            if (m.has("attacks")) for (var a : m.getAsJsonObject("attacks").entrySet()) attacks.put(a.getKey(), a.getValue().getAsString());
            String melee = m.has("melee") && !m.get("melee").isJsonNull() ? m.get("melee").getAsString() : null;
            Model model = new Model(e.getKey(), rig, m.get("scale").getAsFloat(), m.get("height").getAsFloat(), List.copyOf(bones),
                    List.copyOf(cubes), Collections.unmodifiableMap(attacks), melee, steps(m.getAsJsonArray("spawn")), steps(m.getAsJsonArray("death")), anims);
            if (m.has("hitbox")) model.hitbox = Math.max(0.2f, Math.min(1f, m.get("hitbox").getAsFloat()));
            List<Zone> zones = new ArrayList<>();
            if (m.has("zones")) for (JsonElement z : m.getAsJsonArray("zones")) {
                JsonObject o = z.getAsJsonObject();
                Integer bone = index.get(o.get("b").getAsString());
                if (bone == null) throw new IllegalArgumentException(e.getKey() + ": zone on unknown bone " + o.get("b").getAsString());
                zones.add(new Zone(o.get("kind").getAsString(), bone, vec3(o.getAsJsonArray("c")), o.get("w").getAsFloat(), o.get("h").getAsFloat(), o.get("mult").getAsFloat()));
            }
            model.zones = List.copyOf(zones);
            boolean[] only = new boolean[cubes.size()];
            for (int i = 0; i < cubes.size(); i++) {
                int b = cubes.get(i).bone();
                while (b >= 0 && !only[i]) { if (bones.get(b).name().startsWith("shell")) only[i] = true; b = bones.get(b).parent(); }
            }
            model.entranceOnly = only;
            out.put(e.getKey(), model);
        }
        return out;
    }

    /** "minecraft:jack_o_lantern[facing=south]" -> "jack_o_lantern". */
    public static String base(String block) {
        String b = block.toLowerCase(Locale.ROOT);
        int i = b.indexOf('[');
        if (i >= 0) b = b.substring(0, i);
        return b.startsWith("minecraft:") ? b.substring(10) : b;
    }

    private static List<Step> steps(JsonArray arr) {
        List<Step> out = new ArrayList<>();
        if (arr == null) return out;
        for (JsonElement e : arr) {
            JsonObject o = e.getAsJsonObject();
            out.add(new Step(o.get("op").getAsString(), o.has("at") ? o.get("at").getAsInt() : 0, o.has("dur") ? o.get("dur").getAsInt() : 0,
                    o.has("stagger") ? o.get("stagger").getAsInt() : 0, o.has("order") ? o.get("order").getAsString() : "none",
                    o.has("only") ? o.get("only").getAsString() : "", o));
        }
        out.sort(java.util.Comparator.comparingInt(Step::at));
        return List.copyOf(out);
    }

    private static Anim anim(String name, JsonObject o) {
        Map<String, Channel> bones = new HashMap<>();
        for (var b : o.getAsJsonObject("bones").entrySet()) {
            JsonObject ch = b.getValue().getAsJsonObject();
            bones.put(b.getKey(), new Channel(keys(ch.getAsJsonArray("rot")), keys(ch.getAsJsonArray("pos")), keys(ch.getAsJsonArray("scl"))));
        }
        return new Anim(name, o.get("length").getAsFloat(), o.has("loop") && o.get("loop").getAsBoolean(),
                o.has("hit") ? o.get("hit").getAsFloat() : -1, Map.copyOf(bones));
    }

    private static Keys keys(JsonArray arr) {
        if (arr == null || arr.isEmpty()) return null;
        float[] t = new float[arr.size()];
        float[][] v = new float[arr.size()][];
        for (int i = 0; i < t.length; i++) {
            JsonArray k = arr.get(i).getAsJsonArray();
            t[i] = k.get(0).getAsFloat();
            JsonArray x = k.get(1).getAsJsonArray();
            v[i] = new float[]{x.get(0).getAsFloat(), x.get(1).getAsFloat(), x.get(2).getAsFloat()};
        }
        return new Keys(t, v);
    }

    private static Vector3f vec3(JsonArray a) {
        return new Vector3f(a.get(0).getAsFloat(), a.get(1).getAsFloat(), a.get(2).getAsFloat());
    }

    static float rad(float deg) { return (float) Math.toRadians(deg); }

    // ------------------------------------------------------------------ posing

    /**
     * Bone matrices in model pixels for a stack of animation layers. Later layers win bone by bone,
     * blended by their weight, exactly like the preview.
     */
    public static Matrix4f[] pose(Model model, List<Layer> layers) {
        int n = model.bones.size();
        Matrix4f[] out = new Matrix4f[n];
        float[] rot = new float[3], pos = new float[3], scl = new float[3], tmp = new float[3];
        for (int i = 0; i < n; i++) {
            Bone b = model.bones.get(i);
            rot[0] = rot[1] = rot[2] = 0; pos[0] = pos[1] = pos[2] = 0; scl[0] = scl[1] = scl[2] = 1;
            for (Layer layer : layers) {
                if (layer.anim() == null || layer.weight() <= 0) continue;
                Channel ch = layer.anim().bones().get(b.name());
                if (ch == null) continue;
                float t = layer.anim().local(layer.time()), w = Math.min(1, layer.weight());
                if (ch.rot() != null) { ch.rot().sample(t, tmp); blend(rot, tmp, w); }
                if (ch.pos() != null) { ch.pos().sample(t, tmp); blend(pos, tmp, w); }
                if (ch.scl() != null) { ch.scl().sample(t, tmp); blend(scl, tmp, w); }
            }
            // resting bends (elbows, a raised weapon) add to whatever the animations do
            rot[0] += b.rest().x; rot[1] += b.rest().y; rot[2] += b.rest().z;
            Vector3f p = b.pivot();
            Matrix4f m = new Matrix4f().translation(p.x + pos[0], p.y + pos[1], p.z + pos[2])
                    .rotateZ(rad(rot[2])).rotateY(rad(rot[1])).rotateX(rad(rot[0]))
                    .scale(scl[0], scl[1], scl[2]).translate(-p.x, -p.y, -p.z);
            out[i] = b.parent() < 0 ? m : new Matrix4f(out[b.parent()]).mul(m);
        }
        return out;
    }

    private static void blend(float[] into, float[] v, float w) {
        for (int k = 0; k < 3; k++) into[k] += (v[k] - into[k]) * w;
    }

    /** Every cube in model space, in blocks: scale/16 x bone x cube. */
    public static Matrix4f[] cubes(Model model, Matrix4f[] bones) {
        Matrix4f[] out = new Matrix4f[model.cubes.size()];
        float s = model.scale / 16f;
        for (int i = 0; i < out.length; i++) {
            Cube c = model.cubes.get(i);
            out[i] = new Matrix4f().scaling(s).mul(bones[c.bone()]).mul(c.local());
        }
        return out;
    }

    /** The order cubes take in a staggered step: 0 first, 1 last. */
    public static float[] ranks(Model model, Matrix4f[] cubes, String order, long seed) {
        int n = cubes.length;
        float[] key = new float[n];
        java.util.Random random = new java.util.Random(seed);
        Vector3f c = new Vector3f();
        for (int i = 0; i < n; i++) {
            cubes[i].transformPosition(0.5f, 0.5f, 0.5f, c);
            key[i] = switch (order) {
                case "up" -> c.y;
                case "down" -> -c.y;
                case "out" -> c.x * c.x + c.z * c.z + (c.y - model.blocks() / 2) * (c.y - model.blocks() / 2) * 0.3f;
                case "in" -> -(c.x * c.x + c.z * c.z);
                case "random" -> random.nextFloat();
                default -> 0;
            };
        }
        float[] out = new float[n];
        if (order.equals("none")) return out;
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        java.util.Arrays.sort(idx, (a, b) -> Float.compare(key[a], key[b]));
        for (int r = 0; r < n; r++) out[idx[r]] = n <= 1 ? 0 : (float) r / (n - 1);
        return out;
    }
}
