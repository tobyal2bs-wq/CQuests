#!/usr/bin/env python3
"""Makes every attack and hurt clip a boss's own, and makes smashes bend the body.

python3 tools/owned.py models.json

Bosses built from the same rig started with the same clips. Each boss gets its own timing of the wind-up,
its own reach, a twist of the body and head into the blow and a follow-through after it, all drawn from its
name, so no two bosses share a clip. A slam, quake, stomp or shockwave that left the back straight now winds
up, folds the body over the blow and bends the knees. Run once per model (own-revision).
"""
import json, sys, zlib, random

SMASH = ("slam", "quake", "shockwave", "stomp", "smash", "pound")
SPINE = ("body", "torso", "chest")


def keys(clip, bone, kind="rot"):
    return clip["bones"].setdefault(bone, {}).setdefault(kind, [])


def at(track, t):
    """Value of a track at time t (linear), [0,0,0] when empty."""
    if not track: return [0, 0, 0]
    if t <= track[0][0]: return list(track[0][1])
    for (t0, a), (t1, b) in zip(track, track[1:]):
        if t <= t1:
            p = (t - t0) / max(1e-6, t1 - t0)
            return [x + (y - x) * p for x, y in zip(a, b)]
    return list(track[-1][1])


def put(track, t, add):
    """Adds `add` to the track at time t, making a key there if none is close."""
    for k in track:
        if abs(k[0] - t) < 0.03:
            k[1] = [round(v + a, 2) for v, a in zip(k[1], add)]; return
    track.append([round(t, 3), [round(v + a, 2) for v, a in zip(at(sorted(track), t), add)]])
    track.sort(key=lambda k: k[0])


def own(m, name, clip, r, bones):
    L, hit = clip["length"], clip.get("hit") or clip["length"] * 0.45
    warp = r.uniform(0.78, 1.22)          # how early the wind-up peaks
    reach = r.uniform(0.86, 1.3)
    for bone, ch in clip["bones"].items():
        gain = reach * r.uniform(0.92, 1.1)
        for kind in ("rot", "pos"):
            for k in ch.get(kind, []):
                if 0 < k[0] < hit - 0.02: k[0] = round(min(hit - 0.03, k[0] * warp), 3)
                k[1] = [round(v * gain, 2) for v in k[1]]
            if ch.get(kind): ch[kind].sort(key=lambda k: k[0])
    spine = next((b for b in SPINE if b in bones), None)
    side = r.choice((-1, 1))
    twist, lean = side * r.uniform(5, 11), side * r.uniform(2, 6)
    if spine:
        t = keys(clip, spine)
        if not t: t += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
        put(t, hit * 0.55, [0, -twist * 0.7, -lean * 0.5]); put(t, hit, [0, twist, lean]); put(t, min(L - 0.05, hit + 0.12), [0, twist * 1.15, lean * 0.6])
    if "head" in bones:
        t = keys(clip, "head")
        if not t: t += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
        put(t, hit * 0.55, [r.uniform(-8, 4), twist * 0.5, 0]); put(t, hit, [r.uniform(-4, 10), -twist * 0.6, -lean])
    if "jaw" in bones and not clip["bones"].get("jaw", {}).get("rot"):
        keys(clip, "jaw").extend([[0, [0, 0, 0]], [round(hit, 3), [round(r.uniform(14, 26), 1), 0, 0]], [round(min(L, hit + 0.3), 3), [0, 0, 0]]])


def bend(m, clip, bones, r):
    """A smash folds the body over the blow: lean back, fold forward at the hit, knees bent, then stand."""
    L, hit = clip["length"], clip.get("hit") or clip["length"] * 0.45
    spine = next((b for b in SPINE if b in bones), None)
    if not spine: return False
    t = keys(clip, spine)
    if t and max(abs(k[1][0]) for k in t) >= 22: return False
    if not t: t += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
    fold = r.uniform(26, 38)
    put(t, hit * 0.5, [-fold * 0.45, 0, 0]); put(t, hit, [fold, 0, 0]); put(t, min(L - 0.05, hit + 0.25), [fold * 0.8, 0, 0])
    if "head" in bones:
        h = keys(clip, "head")
        if not h: h += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
        put(h, hit, [-fold * 0.5, 0, 0])
    if all(b in bones for b in ("legL", "legR", "shinL", "shinR")):
        for s in "LR":
            a, b = keys(clip, "leg" + s), keys(clip, "shin" + s)
            for tr in (a, b):
                if not tr: tr += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
            put(a, hit, [-fold * 0.6, 0, 0]); put(b, hit, [fold * 1.1, 0, 0])
        root = keys(clip, "root", "pos")
        if not root: root += [[0, [0, 0, 0]], [L, [0, 0, 0]]]
        put(root, hit, [0, -1.4, 0])
    return True


def run(models):
    seen, bent, n = {}, 0, 0
    for id, m in models.items():
        if id.startswith("decor_") or m.get("own-revision"): continue
        bones = {b["name"] for b in m["bones"]}
        clips = {c: a for a, c in m.get("attacks", {}).items()}
        if "hurt" in m.get("anims", {}): clips["hurt"] = "hurt"
        for name, ability in clips.items():
            clip = m.get("anims", {}).get(name)
            if not clip or not clip.get("bones"): continue
            r = random.Random(zlib.crc32((id + ":" + name).encode()))
            if name != "hurt" and (ability in SMASH or any(s in name for s in SMASH)): bent += bend(m, clip, bones, r)
            own(m, name, clip, r, bones); n += 1
        m["own-revision"] = 1
    for id, m in models.items():
        for name in list(m.get("attacks", {}).values()) + ["hurt"]:
            clip = m.get("anims", {}).get(name)
            if clip and not id.startswith("decor_"): seen.setdefault(json.dumps(clip["bones"], sort_keys=True), []).append(id + ":" + name)
    dup = [v for v in seen.values() if len({x.split(":")[0] for x in v}) > 1]
    return n, bent, dup


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    n, bent, dup = run(d["models"])
    print("clips made their own:", n, "smashes that now bend:", bent, "still shared between bosses:", len(dup), dup[:3])
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
