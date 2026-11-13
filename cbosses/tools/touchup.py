"""Hand fixes to single models, applied to models.json after the build. python3 touchup.py models.json
Each fix is done once (touchup-revision)."""
import json, sys

size = lambda c: [round(b - a, 1) for a, b in zip(c["f"], c["t"])]


def mallard(m):
    """Sir Quacks: the big black slab behind his tail and the black wing tips read as boxes stuck on him.
    The slab goes (the white tail and its black curl stay) and the wing tips take the wing's own grey."""
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "tail" and c["k"] == "black_concrete" and "r" not in c and size(c)[0] > 4)]
    for c in m["cubes"]:
        if c["b"] in ("armL", "armR") and c["k"] == "black_concrete": c["k"] = "gray_concrete_powder"


FIXES = {"mallard": mallard}


def smooth(m):
    """Concrete powder is grainy: on a model it reads as random specks. Every powder block becomes the smooth
    concrete of the same colour, in the pieces and in the spawn and death steps that name blocks. Wool on a
    piece too small to show its weave (two sides under 2.5 px) becomes concrete as well."""
    n = 0
    for c in m["cubes"]:
        k = c["k"]
        if k.endswith("_concrete_powder"): c["k"] = k[:-7]; n += 1
        elif k.endswith("_wool") and sorted(b - a for a, b in zip(c["f"], c["t"]))[1] < 2.5: c["k"] = k[:-5] + "_concrete"; n += 1
    for key in ("spawn", "death"):
        if key in m: m[key] = json.loads(json.dumps(m[key]).replace("_concrete_powder", "_concrete"))
    return n

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    for id, fn in FIXES.items():
        m = d["models"].get(id)
        if m and not m.get("touchup-revision"):
            fn(m); m["touchup-revision"] = 1; print("touched", id)
    total = 0
    for id, m in d["models"].items():
        if not m.get("smooth-revision"):
            total += smooth(m); m["smooth-revision"] = 1
    print("pieces smoothed:", total)
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
