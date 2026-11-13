"""Hand fixes to single models, applied to models.json after the build. python3 touchup.py models.json
Each fix is done once (its own revision key)."""
import collections, json, sys
import mend

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
        if c["b"] in rod and c["k"] == "black_concrete": c["f"], c["t"] = rod[c["b"]]; c.pop("r", None); c.pop("o", None)


def box(m, b, k, x0, y0, z0, x1, y1, z1, g="detail"):
    m["cubes"].append({"b": b, "k": k, "f": [x0, y0, z0], "t": [x1, y1, z1], "g": g})


def frost_yeti(m):
    """A real face: big eyes under a heavy brow, a nose that stands out, an open mouth with two fangs."""
    z, x = 8.21, 0.71
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "head" and c["f"][2] > 8.1 and c["t"][2] - c["f"][2] < 0.3)]
    for s in (-1, 1):
        a, b = sorted((x + s * 1.3, x + s * 4.1))
        box(m, "head", "white_concrete", a, 32.8, z, b, 35.2, z + 0.15)
        a, b = sorted((x + s * 1.5, x + s * 2.9))
        box(m, "head", "black_concrete", a, 33.0, z + 0.15, b, 34.6, z + 0.3)
        a, b = sorted((x + s * 0.9, x + s * 4.5))
        box(m, "head", "white_wool", a, 35.2, z, b, 36.4, z + 0.9)
        a, b = sorted((x + s * 1.9, x + s * 3.0))
        box(m, "head", "white_concrete", a, 29.6, z + 0.15, b, 31.0, z + 0.7)
    box(m, "head", "gray_concrete", x - 1.1, 31.4, z, x + 1.1, 33.0, z + 1.0)
    box(m, "head", "black_concrete", x - 3.6, 28.6, z, x + 3.6, 30.6, z + 0.15)


def rotting_giant(m):
    """Slit eyes became a dead face: sunken sockets, one live yellow eye and one blind white one, a brow ridge and
    a crooked mouth with three teeth."""
    z = 4.99
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "head" and c.get("g") == "trim" and c["k"] == "black_concrete")]
    for s in (-1, 1):
        a, b = sorted((s * 1.0, s * 4.0))
        box(m, "head", "black_concrete", a, 41.4, z, b, 43.6, z + 0.15)
    box(m, "head", "yellow_concrete", 1.8, 41.9, z + 0.15, 3.0, 43.1, z + 0.3)
    box(m, "head", "white_concrete", -3.4, 41.7, z + 0.15, -1.6, 43.3, z + 0.3)
    box(m, "head", "green_concrete", -4.6, 43.6, z, 4.6, 44.8, z + 0.7)
    box(m, "head", "black_concrete", -3.2, 38.4, z, 3.4, 40.0, z + 0.15)
    for x, y in ((-2.4, 39.2), (0.4, 39.2), (2.0, 38.4)): box(m, "head", "white_terracotta", x, y, z + 0.15, x + 0.9, y + 0.8, z + 0.5)


def pair(m, b, k, x0, y0, z0, x1, y1, z1, cx=0.0, g="detail"):
    """The same piece on both sides of the body: bone names ending in L swap to R on the far side."""
    box(m, b, k, x0, y0, z0, x1, y1, z1, g)
    box(m, b[:-1] + "R" if b.endswith("L") else b, k, 2 * cx - x1, y0, z0, 2 * cx - x0, y1, z1, g)


def abyssal_details(m):
    """Designed detail in place of the random patches: two slanted glowing eyes under black brows, three gill slits
    and two glow spots a side, side teeth, tail flukes."""
    for c in m["cubes"]: c.pop("o", None) if "r" not in c else None
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "head" and c["f"][2] > 8.8 and c["t"][2] - c["f"][2] < 0.3 and c["k"] in ("yellow_concrete", "black_concrete"))]
    z = 8.91
    pair(m, "head", "yellow_concrete", 2.4, 15.4, z, 6.0, 17.6, z + 0.14)
    pair(m, "head", "black_concrete", 3.8, 15.4, z + 0.14, 4.6, 17.6, z + 0.27)
    pair(m, "head", "black_concrete", 1.8, 17.6, z, 4.4, 18.6, z + 0.6)
    pair(m, "head", "black_concrete", 4.4, 18.2, z, 6.6, 19.2, z + 0.6)
    for i, zz in enumerate((-5.0, -2.6, -0.2)): pair(m, "head", "black_concrete", 9.0, 9.4 + i * 0.6, zz, 9.14, 14.4 + i * 0.6, zz + 1.0)
    pair(m, "head", "cyan_concrete", 9.0, 16.4, 3.2, 9.16, 18.4, 5.2)
    pair(m, "head", "cyan_concrete", 9.0, 10.2, 4.6, 9.16, 11.8, 6.2)
    for zz in (7.4, 9.6): pair(m, "jaw", "white_concrete", 7.5, 5.1, zz, 8.5, 7.3, zz + 1.0)
    box(m, "tail2", "cyan_concrete", -0.5, 18.1, -27.6, 0.5, 21.6, -23.6)
    box(m, "tail2", "cyan_concrete", -0.5, 0.6, -27.6, 0.5, 4.1, -23.6)


def moss_spirit(m):
    """A stone golem under moss: moss hangs from every slab in tufts, the stone has seams and blue runes, the
    hands have fingers and the feet toes, and a flower and a mushroom grow on it."""
    X, moss, rune, seam = 0.2, "lime_terracotta", "light_blue_concrete", "gray_concrete"
    for i, (x, h) in enumerate(((0.6, 2.6), (3.0, 1.4), (5.2, 2.2))):
        pair(m, "body", moss, x, 25.0 - h, 4.42, x + 1.4, 25.0, 5.0, X)
        pair(m, "body", moss, x, 25.0 - h * 0.8, -5.16, x + 1.4, 25.0, -4.58, X)
        pair(m, "armL", moss, 7.4 + i * 1.7, 26.0 - h * 0.7, 2.42, 8.6 + i * 1.7, 26.0, 3.0, X)
        pair(m, "armL", moss, 12.2, 26.0 - h * 0.7, -2.4 + i * 1.6, 12.78, 26.0, -1.2 + i * 1.6, X)
        pair(m, "grass", moss, 0.5 + i * 1.5, 36.0 - h * 0.6, 3.92, 1.6 + i * 1.5, 36.0, 4.5, X)
        pair(m, "foreL", seam, 7.6 + i * 1.6, 11.8, -0.6, 8.8 + i * 1.6, 13.412, 0.8, X)
        pair(m, "footL", seam, 0.8 + i * 1.9, 6.012, 4.02, 2.2 + i * 1.9, 6.8, 4.9, X)
    pair(m, "foreL", rune, 12.2, 17.6, -0.5, 12.34, 19.6, 0.5, X)
    pair(m, "foreL", rune, 12.7, 14.2, -1.4, 12.84, 16.6, 1.4, X)
    pair(m, "armL", rune, 12.2, 21.4, -0.5, 12.34, 24.2, 0.5, X)
    pair(m, "legL", rune, 2.9, 10.6, 2.42, 3.9, 13.0, 2.56, X)
    for y in (16.0, 19.0, 22.0): box(m, "body", rune, X - 0.6, y, -4.72, X + 0.6, y + 1.6, -4.58)
    pair(m, "body", seam, 0.2, 18.4, 4.42, 7.2, 18.8, 4.55, X)
    pair(m, "body", seam, 4.4, 14.012, 4.42, 4.8, 18.4, 4.55, X)
    pair(m, "body", seam, 7.2, 20.6, -4.58, 7.33, 21.0, 4.42, X)
    pair(m, "body", seam, 0.2, 20.6, -4.71, 7.2, 21.0, -4.58, X)
    pair(m, "head", seam, 4.7, 31.0, -4.08, 4.83, 31.4, 3.92, X)
    box(m, "grass", "lime_concrete", 2.6, 38.0, 0.6, 3.0, 40.2, 1.0); box(m, "grass", "white_concrete", 1.9, 40.2, 0.3, 3.7, 40.7, 2.1)
    box(m, "grass", "yellow_concrete", 2.4, 40.7, 0.8, 3.2, 41.0, 1.6)
    box(m, "armR", "white_terracotta", -10.4, 29.0, -0.6, -9.4, 30.6, 0.4); box(m, "armR", "red_concrete", -11.4, 30.6, -1.6, -8.4, 31.8, 1.4)
    box(m, "armR", "white_concrete", -10.6, 31.8, -0.4, -9.8, 31.95, 0.4)


FIXES = {"mallard": mallard}
MORE = {"abyssal_eye": abyssal_details, "moss_spirit": moss_spirit}
FACES = {"frost_yeti": frost_yeti, "rotting_giant": rotting_giant}
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
    for id, fn in FACES.items():
        m = d["models"].get(id)
        if m and not m.get("face-revision"): fn(m); mend.unfight(m); m["face-revision"] = 1; print("new face", id)
    for id, fn in MORE.items():
        m = d["models"].get(id)
        if m and not m.get("detail-revision"): fn(m); mend.unfight(m); m["detail-revision"] = 1; print("detail", id, len(m["cubes"]))
    print("pieces flattened or dropped:", total)
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
