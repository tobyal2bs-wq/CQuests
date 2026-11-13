"""Hand fixes to single models, applied to models.json after the build. python3 touchup.py models.json
Each fix is done once (its own revision key)."""
import collections, json, sys

size = lambda c: [round(b - a, 1) for a, b in zip(c["f"], c["t"])]


def mallard(m):
    """Sir Quacks: the big black slab behind his tail and the black wing tips read as boxes stuck on him.
    The slab goes (the white tail and its black curl stay) and the wing tips take the wing's own grey."""
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "tail" and c["k"] == "black_concrete" and "r" not in c and size(c)[0] > 4)]
    for c in m["cubes"]:
        if c["b"] in ("armL", "armR") and c["k"] == "black_concrete": c["k"] = "gray_concrete_powder"


def abyssal_eye(m):
    """The lure stalk was three tilted sticks that did not touch: now one bent rod from the head to the light."""
    rod = {"lure1": ([-0.6, 21.0, 0.3], [0.6, 30.7, 1.5]), "lure2": ([-0.6, 29.5, 1.5], [0.6, 30.7, 12.9]), "lure3": ([-0.5, 25.5, 11.9], [0.5, 29.5, 12.9])}
    for c in m["cubes"]:
        if c["b"] in rod and c["k"] == "black_concrete": c["f"], c["t"] = rod[c["b"]]; c.pop("r", None)


FIXES = {"mallard": mallard}
FIXES2 = {"abyssal_eye": abyssal_eye}


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

FLAT = {"andesite": "light_gray_concrete", "polished_andesite": "light_gray_concrete", "stone": "light_gray_concrete",
        "cobblestone": "gray_concrete", "tuff": "gray_concrete", "moss_block": "lime_terracotta", "sculk": "black_concrete",
        "nether_wart_block": "red_terracotta", "warped_wart_block": "cyan_terracotta", "red_nether_bricks": "red_terracotta",
        "nether_bricks": "gray_terracotta", "blackstone": "black_terracotta", "packed_mud": "terracotta", "mud": "gray_terracotta",
        "rooted_dirt": "brown_terracotta", "end_stone": "yellow_terracotta", "cobbled_deepslate": "gray_concrete"}
ODD = ("abyssal_eye", "tide_tyrant", "mossback", "old_wizard", "horned_brute", "rotting_giant", "grave_marshal", "old_ironroot",
       "frost_yeti", "bog_orc", "withered_tyrant", "brain_freeze", "moss_spirit")


def flat(m):
    """Noisy stone, moss, sculk and brick skins read as random specks at boss size: each takes the flat block of
    its own colour. Wool of any colour but white and black becomes concrete. Buildings on a model keep their stone."""
    n = 0
    for c in m["cubes"]:
        k = c["k"]
        if k in FLAT: c["k"] = FLAT[k]; n += 1
        elif k.endswith("_wool") and k not in ("white_wool", "black_wool"): c["k"] = k[:-5] + "_concrete"; n += 1
    return n


def lonely(m):
    """Leftover skin patches: a thin trim plate off the centre line with no twin on the other side of the body is
    not a design mark (those come in pairs or sit on the middle), so it goes."""
    cx = m["bones"][0]["pivot"][0]
    thin = lambda c: c.get("g") == "trim" and "r" not in c and min(b - a for a, b in zip(c["f"], c["t"])) <= 0.26
    key = lambda c, s: (c["k"],) + tuple(round(v) for v in ((c["f"][0] - cx, c["t"][0] - cx) if s > 0 else (cx - c["t"][0], cx - c["f"][0]))) + tuple(round(c[a][i]) for i in (1, 2) for a in "ft")
    have = collections.Counter(key(c, 1) for c in m["cubes"] if thin(c))
    gone = [c for c in m["cubes"] if thin(c) and abs(c["f"][0] + c["t"][0] - 2 * cx) >= 0.5 and not have[key(c, -1)]]
    m["cubes"] = [c for c in m["cubes"] if not any(c is g for g in gone)]
    return len(gone)


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
    total = 0
    for id, m in d["models"].items():
        if not m.get("flat-revision"):
            total += flat(m) + (lonely(m) if id in ODD else 0); m["flat-revision"] = 1
            if id in FIXES2: FIXES2[id](m)
    print("pieces flattened or dropped:", total)
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
