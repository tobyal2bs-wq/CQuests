package com.cbosses.model;

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
 * The block models of the bosses (models.json, written by tools/models). A model is
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

    /** level: a foot that stays flat on the ground whatever its leg does (only the body's turn is kept). */
    public record Bone(String name, int parent, Vector3f pivot, Vector3f rest, boolean level) {
        public Bone(String name, int parent, Vector3f pivot, Vector3f rest) { this(name, parent, pivot, rest, false); }
    }

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
        /** Level foot bones (each has a shin and a leg above it), and the root bone or -1. */
        public int[] feet = new int[0];
        public int root = -1;
        /** Face pieces: faceOf[cube] is the face it belongs to (idle, angry, hurt, rage, dead...), or null. */
        public String[] faceOf;
        public Set<String> faces = Set.of();

        /** Hides every face piece that is not part of face (falls back to idle). */
        public void showFace(Matrix4f[] pose, String face) {
            if (faceOf == null) return;
            String f = faces.contains(face) ? face : "idle";
            for (int i = 0; i < faceOf.length && i < pose.length; i++)
                if (faceOf[i] != null && !faceOf[i].equals(f)) pose[i].scale(0);
        }

        Model(String id, String rig, float scale, float height, List<Bone> bones, List<Cube> cubes, Map<String, String> attacks,
              String melee, List<Step> spawn, List<Step> death, Map<String, Anim> anims) {
            this.id = id; this.rig = rig; this.scale = scale; this.height = height; this.bones = bones; this.cubes = cubes;
            this.attacks = attacks; this.melee = melee; this.spawn = spawn; this.death = death; this.anims = anims;
            for (int i = 0; i < bones.size(); i++) boneIndex.put(bones.get(i).name(), i);
        }

        /** Height in blocks. */
        public float blocks() { return height * scale / 16f; }
        /** Constant rest-pose floor correction in model pixels; shared by skin and hit zones. */
        float groundLift;

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
                bones.add(new Bone(name, parent, vec3(o.getAsJsonArray("pivot")), o.has("rest") ? vec3(o.getAsJsonArray("rest")) : new Vector3f(),
                        o.has("level") && o.get("level").getAsInt() == 1));
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
            // A model can bring its own animations: its attacks and moves are its own, the rig's fill the rest.
            if (m.has("anims")) {
                Map<String, Anim> own = new HashMap<>(anims);
                for (var a : m.getAsJsonObject("anims").entrySet()) own.put(a.getKey(), anim(a.getKey(), a.getValue().getAsJsonObject()));
                anims = Collections.unmodifiableMap(own);
            }
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
            String[] faceOf = new String[cubes.size()];
            Set<String> faces = new java.util.HashSet<>();
            for (int i = 0; i < cubes.size(); i++) {
                String tg = cubes.get(i).tag();
                if (tg.startsWith("face:")) { faceOf[i] = tg.substring(5); faces.add(faceOf[i]); }
            }
            if (!faces.isEmpty()) { model.faceOf = faceOf; model.faces = Set.copyOf(faces); }
            List<Integer> feet = new ArrayList<>();
            for (int i = 0; i < bones.size(); i++) {
                Bone b = bones.get(i);
                int shin = b.parent(), leg = shin < 0 ? -1 : bones.get(shin).parent();
                if (b.level() && shin >= 0 && leg >= 0) feet.add(i);
            }
            model.feet = feet.stream().mapToInt(Integer::intValue).toArray();
            model.root = index.getOrDefault("root", -1);
            // A rotated foot, hoof or spider leg can extend below its unrotated
            // JSON box. Anchor the real posed geometry, not the raw f/t values.
            Matrix4f[] baseline = rawPose(model, List.of(new Layer(model.anim("idle"), 0, 1)), null);
            float bottom = Float.POSITIVE_INFINITY;
            Vector3f corner = new Vector3f();
            for (int ci = 0; ci < cubes.size(); ci++) {
                Cube c = cubes.get(ci);
                if (only[ci] || c.tag().startsWith("face:") && !c.tag().equals("face:idle")) continue;
                Matrix4f matrix = new Matrix4f(baseline[c.bone()]).mul(c.local());
                for (int k = 0; k < 8; k++) {
                    matrix.transformPosition(k & 1, k >> 1 & 1, k >> 2 & 1, corner);
                    bottom = Math.min(bottom, corner.y);
                }
            }
            if (Float.isFinite(bottom)) model.groundLift = -bottom;
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
    public static Matrix4f[] pose(Model model, List<Layer> layers) { return pose(model, layers, null); }

    /** As above; ground (model pixels per foot, in model.feet order, may be null) lifts feet onto uneven ground. */
    public static Matrix4f[] pose(Model model, List<Layer> layers, float[] ground) {
        Matrix4f[] out = rawPose(model, layers, ground);
        if (Math.abs(model.groundLift) > 1e-5f) {
            Matrix4f lift = new Matrix4f().translation(0, model.groundLift, 0);
            for (int i = 0; i < out.length; i++) out[i] = new Matrix4f(lift).mul(out[i]);
        }
        return out;
    }

    private static Matrix4f[] rawPose(Model model, List<Layer> layers, float[] ground) {
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
        if (model.feet.length > 0) plantFeet(model, out, ground);
        return out;
    }

    /**
     * Keeps every level foot flat (only the root's turn is kept) and, when a foot ends up below where it
     * should stand, bends hip and knee (two-bone IK) to put it back on the ground. A crouching or leaning
     * body therefore keeps its feet planted instead of tilting them into the floor. Same as the preview.
     */
    static void plantFeet(Model model, Matrix4f[] out, float[] ground) {
        Matrix4f rootM = model.root >= 0 ? out[model.root] : new Matrix4f();
        Matrix4f rr = new Matrix4f(rootM).setTranslation(0, 0, 0);
        float rootY = rootM.m31();
        for (int fi = 0; fi < model.feet.length; fi++) {
            int f = model.feet[fi];
            Bone foot = model.bones.get(f);
            int shinI = foot.parent(), legI = model.bones.get(shinI).parent();
            Bone shin = model.bones.get(shinI), leg = model.bones.get(legI);
            Vector3f F = out[shinI].transformPosition(new Vector3f(foot.pivot()));
            float floor = foot.pivot().y + (ground != null && fi < ground.length ? ground[fi] : 0) + rootY;
            if (F.y < floor - 0.01f) {
                Vector3f H = out[legI].transformPosition(new Vector3f(leg.pivot()));
                Vector3f Kn = out[shinI].transformPosition(new Vector3f(shin.pivot()));
                float L1 = H.distance(Kn), L2 = Kn.distance(F);
                if (L1 < 1e-4f || L2 < 1e-4f) continue;
                Vector3f T = new Vector3f(F.x, floor, F.z);
                float D = T.distance(H);
                D = Math.max(Math.abs(L1 - L2) + 0.01f, Math.min(L1 + L2 - 0.01f, D));
                Vector3f u = new Vector3f(T).sub(H);
                if (u.lengthSquared() < 1e-8f) u.set(0, -1, 0);
                u.normalize();
                T.set(H).add(new Vector3f(u).mul(D));
                Vector3f kh = new Vector3f(Kn).sub(H);
                Vector3f n = new Vector3f(kh).sub(new Vector3f(u).mul(kh.dot(u)));
                if (n.lengthSquared() < 1e-4f) {
                    n = rr.transformDirection(new Vector3f(0, 0, 1));
                    n.sub(new Vector3f(u).mul(n.dot(u)));
                    if (n.lengthSquared() < 1e-4f) {
                        n.set(1, 0, 0);
                        n.sub(new Vector3f(u).mul(n.dot(u)));
                    }
                }
                n.normalize();
                float a = (L1 * L1 - L2 * L2 + D * D) / (2 * D), h = (float) Math.sqrt(Math.max(0, L1 * L1 - a * a));
                Vector3f K2 = new Vector3f(H).add(new Vector3f(u).mul(a)).add(n.mul(h));
                Matrix4f d1 = turn(new Vector3f(Kn).sub(H), new Vector3f(K2).sub(H), H);
                // Apply each correction to the entire subtree (armour, toes, and
                // attachments included), otherwise the rig separates at the knee.
                transformBranch(model, out, legI, d1);
                Vector3f F1 = d1.transformPosition(new Vector3f(F));
                Matrix4f d2 = turn(F1.sub(K2), new Vector3f(T).sub(K2), K2);
                transformBranch(model, out, shinI, d2);
                // The target may be outside the chain's reach. Keep the foot on
                // the actual ankle, not the unreachable target.
                F = out[shinI].transformPosition(new Vector3f(foot.pivot()));
            }
            Vector3f p = foot.pivot();
            Matrix4f level = new Matrix4f().translation(F).mul(rr).translate(-p.x, -p.y, -p.z);
            Matrix4f correction = new Matrix4f(level).mul(new Matrix4f(out[f]).invert());
            transformBranch(model, out, f, correction);
        }
    }

    private static void transformBranch(Model model, Matrix4f[] pose, int root, Matrix4f correction) {
        for (int i = root; i < pose.length; i++) {
            int ancestor = i;
            while (ancestor >= 0 && ancestor != root) ancestor = model.bones.get(ancestor).parent();
            if (ancestor == root) pose[i] = new Matrix4f(correction).mul(pose[i]);
        }
    }

    private static Matrix4f turn(Vector3f from, Vector3f to, Vector3f c) {
        org.joml.Quaternionf q = new org.joml.Quaternionf().rotationTo(new Vector3f(from).normalize(), new Vector3f(to).normalize());
        return new Matrix4f().translation(c).rotate(q).translate(-c.x, -c.y, -c.z);
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
