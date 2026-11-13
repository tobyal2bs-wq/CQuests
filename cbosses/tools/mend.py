"""Joins what the gap check flags. python3 mend.py models.json gaps.txt
gaps.txt is the output of the viewer gap check: lines 'model bone detached at rest' or 'model bone <- parent: ...'.
A limb or torso gets a ball of its own block on its parent round the hinge and a post from the hinge into itself,
so it stays joined at rest and through every move. A held thing is moved into the hand that holds it: its grip
is put at the centre of the hand and it turns about that point, with a fist of the hand's block round a thin shaft.
A model is mended once (mend-revision).
Every model also gets its flickering shared planes separated once (flicker-revision)."""
import json, sys

LIFT = {"hollow_mage": 0.7, "cinder_hollow": 3.3, "rime_hollow": 1.5, "bramble_hollow": 1.5}      # these lean as they stand: the staff rides higher in the fist
SKIP = ("halo", "ring", "lure", "pupil", "eye", "whistle", "orbit", "cloud")
mid = lambda c: [(a + b) / 2 for a, b in zip(c["f"], c["t"])]
size = lambda c: [b - a for a, b in zip(c["f"], c["t"])]
solid = lambda c: "r" not in c and min(size(c)) >= 0.5
gap = lambda c, P: sum(max(0, c["f"][i] - P[i], P[i] - c["t"][i]) ** 2 for i in range(3)) ** 0.5


def reach(f, t, c):
    for i in range(3):
        if c["f"][i] > t[i] - 0.5: t[i] = min(c["f"][i] + 0.5, c["t"][i])
        if c["t"][i] < f[i] + 0.5: f[i] = max(c["t"][i] - 0.5, c["f"][i])
    return [round(v, 3) for v in f], [round(v, 3) for v in t]


def mend(m, bones):
    pv = {b["name"]: b for b in m["bones"]}
    by = {}
    for c in m["cubes"]:
        if solid(c): by.setdefault(c["b"], []).append(c)
    for c in m["cubes"]:                                   # a part made only of turned or thin pieces still counts
        if c["b"] not in by and min(size(c)) >= 0.2: by.setdefault("~" + c["b"], []).append(c)
    for k in [k for k in by if k[0] == "~"]: by.setdefault(k[1:], by[k])
    done = 0
    for n in bones:
        if n not in pv or n not in by or any(w in n.lower() for w in SKIP): continue
        a = pv[n]["parent"]
        while a and a not in by: a = pv[a]["parent"]
        if not a: continue
        b = pv[n]
        if a[:4] in ("fore", "armL", "armR") and n[:4] not in ("fore", "fing", "hand"):          # a held thing: into the hand
            hand = min((c for c in by[a] if min(size(c)) >= 0.8), key=lambda c: mid(c)[1], default=None)
            if not hand: continue
            H = mid(hand)
            main = max(by[n], key=lambda c: max(size(c)) * (2 if size(c)[1] == max(size(c)) else 1))
            s, G = size(main), []
            for i in range(3):
                thin = s[i] <= 2.6
                G.append(mid(main)[i] if thin else min(max(H[i], main["f"][i] + min(1, s[i] / 4)), main["t"][i] - min(1, s[i] / 4)))
            d = [h - g for h, g in zip(H, G)]
            low = min(c["f"][1] for c in by[n]) + d[1]
            if low < 0 and s[1] > 6: d[1] -= low
            d[1] += LIFT.get(m.get("_id"), 0)                                                   # a long shaft slides up in the fist, never through the floor
            tree, grew = {n}, True
            while grew:
                grew = False
                for x in m["bones"]:
                    if x["parent"] in tree and x["name"] not in tree: tree.add(x["name"]); grew = True
            for x in m["bones"]:
                if x["name"] in tree and x["name"] != n: x["pivot"] = [round(v + e, 3) for v, e in zip(x["pivot"], d)]
            for c in m["cubes"]:
                if c["b"] in tree:
                    for k in ("f", "t", "o"):
                        if k in c: c[k] = [round(v + e, 3) for v, e in zip(c[k], d)]
            b["pivot"] = [round(v, 3) for v in H]
            if s[0] <= 2.6 and s[2] <= 2.6:                                                        # a fist round a thin shaft
                w, dd = s[0] + 1.6, s[2] + 1.6
                m["cubes"].append({"b": n, "k": hand["k"], "f": [round(H[0] - w / 2, 3), round(H[1] - 1.2, 3), round(H[2] - dd / 2, 3)],
                                   "t": [round(H[0] + w / 2, 3), round(H[1] + 1.2, 3), round(H[2] + dd / 2, 3)]})
            done += 1
            continue
        P = b["pivot"]
        c = min(by[n], key=lambda c: gap(c, P))
        q = min(by[a], key=lambda c: gap(c, P))
        h = max(0.6, min(2.4, 0.42 * min(min(size(c)[0], size(c)[2]), min(size(q)[0], size(q)[2]))))
        f, t = reach([v - h for v in P], [v + h for v in P], q)
        m["cubes"].append({"b": a, "k": c["k"], "f": f, "t": t})
        if gap(c, P) > 0.6 * h:
            g = 0.9 * h
            f, t = reach([v - g for v in P], [v + g for v in P], c)
            m["cubes"].append({"b": n, "k": c["k"], "f": f, "t": t})
        done += 1
    return done


def unfight(m):
    """Two faces in one plane, facing the same way, flicker. The smaller box steps 0.03 out of that plane."""
    cs = [c for c in m["cubes"] if "r" not in c]
    vol = lambda c: (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2])
    n = 0
    for _ in range(3):
        moved = False
        for i, a in enumerate(cs):
            for b in cs[i + 1:]:
                for ax in range(3):
                    if not all(min(a["t"][k], b["t"][k]) - max(a["f"][k], b["f"][k]) > 0.01 for k in range(3) if k != ax): continue
                    s = a if vol(a) < vol(b) else b
                    if abs(a["f"][ax] - b["f"][ax]) < 0.005: s["f"][ax] = round(s["f"][ax] + (0.03 if ax == 1 and s["f"][ax] < 0.03 else -0.03), 3); moved = True; n += 1
                    if abs(a["t"][ax] - b["t"][ax]) < 0.005: s["t"][ax] = round(s["t"][ax] + 0.03, 3); moved = True; n += 1
        if not moved: break
    return n


if __name__ == "__main__":
    path, gaps = sys.argv[1], sys.argv[2]
    d = json.load(open(path))
    want = {}
    for line in open(gaps):
        p = line.split()
        if len(p) >= 3 and p[0] in d["models"] and (p[2] in ("detached", "<-")): want.setdefault(p[0], []).append(p[1])
    for id, bones in want.items():
        m = d["models"][id]
        if m.get("mend-revision"): continue
        m["_id"] = id
        n = mend(m, list(dict.fromkeys(bones)))
        del m["_id"]
        if n: m["mend-revision"] = 1
        print(id, n, "of", len(set(bones)))
    total = 0
    for id, m in d["models"].items():
        if m.get("flicker-revision"): continue
        k = unfight(m)
        m["flicker-revision"] = 1
        total += k
    print("faces moved out of shared planes:", total)
    json.dump(d, open(path, "w"), separators=(",", ":"))
