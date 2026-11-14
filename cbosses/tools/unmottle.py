"""Takes the random tone patches off every model. python3 unmottle.py models.json
The skin pass laid thin square plates of a darker or lighter block over big faces. They read as blocks of a
colour that has nothing to do with the model, so they go: a plate up to 0.2 px thick, tagged trim or detail, lying
flat on a bigger piece of the same bone whose block is a nearby tone of the plate's block. Eyes, mouths,
stripes, buckles and every other plate that is not a tone of what it sits on stay. Done once (skin-revision)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))
import mottle_pass

base = lambda k: k.replace("_powder", "")
size = lambda c: [b - a for a, b in zip(c["f"], c["t"])]


def near(a, b):
    a, b = base(a), base(b)
    return a != b and (b in mottle_pass.tones(a) or a in mottle_pass.tones(b))


def strip(m):
    big = {}
    for c in m["cubes"]:
        if "r" not in c and min(size(c)) >= 1.0: big.setdefault(c["b"], []).append(c)
    keep, gone = [], 0
    for c in m["cubes"]:
        s = size(c)
        if c.get("g") in ("trim", "detail") and "r" not in c and min(s) <= 0.21 and not c.get("l"):
            ax = s.index(min(s))
            o = [k for k in range(3) if k != ax]
            under = [q for q in big.get(c["b"], []) if all(q["f"][k] - 0.05 <= c["f"][k] and c["t"][k] <= q["t"][k] + 0.05 for k in o)
                     and (abs(c["f"][ax] - q["t"][ax]) < 0.2 or abs(c["t"][ax] - q["f"][ax]) < 0.2 or (q["f"][ax] < c["f"][ax] < q["t"][ax]) or (q["f"][ax] < c["t"][ax] < q["t"][ax]))]
            if any(near(c["k"], q["k"]) for q in under):
                gone += 1
                continue
        keep.append(c)
    m["cubes"] = keep
    return gone


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    total = 0
    for id, m in d["models"].items():
        if m.get("skin-revision"): continue
        n = strip(m)
        m["skin-revision"] = 1
        total += n
        if n: print(id, n)
    print("patches removed:", total)
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
