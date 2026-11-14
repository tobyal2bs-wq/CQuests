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


def redeye_mouth(m):
    """The mouth was red on red. Now a black open mouth with four top teeth, two bottom fangs and a tongue."""
    m["cubes"] = [c for c in m["cubes"] if c["b"] != "jaw"]
    z = 4.53
    box(m, "jaw", "black_concrete", -4.6, 5.6, z - 1.0, 4.6, 8.6, z + 0.2)
    box(m, "jaw", "red_terracotta", -5.0, 5.0, z, 5.0, 5.6, z + 0.5)
    for x in (-3.6, -1.7, 0.4, 2.3): box(m, "jaw", "white_concrete", x, 7.6, z + 0.2, x + 1.3, 8.6, z + 0.45)
    pair(m, "jaw", "white_concrete", 2.6, 5.6, z + 0.2, 3.5, 6.7, z + 0.45)
    box(m, "jaw", "pink_concrete", -1.6, 5.6, z + 0.2, 1.6, 6.4, z + 0.4)


def withered_faces(m):
    """Three skulls with no faces: each gets white eyes under a grey brow and a toothed grey mouth."""
    X = 0.1
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] in ("head", "armL", "armR") and "r" not in c and min(b - a for a, b in zip(c["f"], c["t"])) < 0.3)]
    z = 4.07
    box(m, "head", "gray_concrete", -3.9, 23.6, z, 4.1, 24.5, z + 0.5)
    pair(m, "head", "white_concrete", 1.2, 22.2, z, 3.3, 23.6, z + 0.14, X)
    box(m, "head", "gray_concrete", -2.9, 19.7, z, 3.1, 21.0, z + 0.14)
    for x in (-1.6, 0.0, 1.6): box(m, "head", "black_concrete", x - 0.1, 19.7, z + 0.14, x + 0.3, 21.0, z + 0.26)
    pair(m, "armL", "gray_concrete", 6.1, 20.9, z, 12.1, 21.6, z + 0.4, X)
    pair(m, "armL", "white_concrete", 6.9, 19.8, z, 8.4, 20.9, z + 0.14, X)
    pair(m, "armL", "white_concrete", 9.8, 19.8, z, 11.3, 20.9, z + 0.14, X)
    pair(m, "armL", "gray_concrete", 7.1, 17.5, z, 11.1, 18.4, z + 0.14, X)
    pair(m, "armL", "black_concrete", 8.3, 17.5, z + 0.14, 8.6, 18.4, z + 0.26, X)
    pair(m, "armL", "black_concrete", 9.6, 17.5, z + 0.14, 9.9, 18.4, z + 0.26, X)


FIXES = {"mallard": mallard}
MORE2 = {"redeye": redeye_mouth, "withered_tyrant": withered_faces}
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


GRAIN = ("andesite", "polished_andesite", "stone", "cobblestone", "tuff", "moss_block", "sculk", "blackstone", "cobbled_deepslate")
big = lambda c: sorted(b - a for a, b in zip(c["f"], c["t"]))[0] >= 1.0 and sorted(b - a for a, b in zip(c["f"], c["t"]))[1] >= 2.5


def flat(m):
    """Noisy skins read as random specks on small pieces, so those take the flat block of their colour. Stone,
    moss and sculk keep their texture on the big pieces, where it shows as rock or moss and not as noise. Wool of
    any colour but white and black becomes concrete."""
    n = 0
    for c in m["cubes"]:
        k = c["k"]
        if k in GRAIN and big(c): continue
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


SIZES = {"abyssal_eye": 3.0, "broodmother": 3.0, "dusk_scorpion": 3.0, "admiral_pinchworth": 3.0, "the_listener": 4.0,
         "withered_tyrant": 4.0, "the_unmaker": 4.0}


def resize(id, m):
    """Big bosses stand 3 to 4 blocks high, minis 1 to 2. The few outside that are scaled into it."""
    if id in SIZES: m["scale"] = round(SIZES[id] * 16 / m["height"], 4)


def fall(m):
    """A death that tips the boss over stopped half way, leaning in the air. It now goes all the way down: the
    body hits the floor, bounces once and lies flat."""
    for st in m.get("death", []):
        a = m.get("anims", {}).get(st.get("name", "")) if st.get("op") == "anim" else None
        root = a and a["bones"].get("root")
        if not root or "rot" not in root or m["rig"] == "float": continue  # a floater turns about a point under the floor
        x, _, z = root["rot"][-1][1]
        ax = 0 if abs(x) >= abs(z) else 2
        v = (x, 0, z)[ax]
        if not 10 <= abs(v) < 80: continue
        s, L = (1 if v > 0 else -1), a["length"]
        aim = lambda d: [s * d if i == ax else 0 for i in range(3)]
        root["rot"] += [[round(L + 0.35, 3), aim(90)], [round(L + 0.48, 3), aim(81)], [round(L + 0.6, 3), aim(88)]]
        a["length"] = round(L + 0.6, 3)
        for o in m["death"]:
            if o is st: o["dur"] = o.get("dur", 0) + 12
            elif o.get("at", 0) > 8: o["at"] += 12


SWAY = {"killer_bunny": {"earL": (6, 0, 7, 1.4), "earR": (6, 0, -7, 1.4), "basket": (0, 0, 5, 1.6)},
        "the_listener": {"tendrilL": (5, 0, 10, 2.0), "tendrilR": (5, 0, -10, 2.0)}, "withered_tyrant": {"tail": (12, 0, 5, 1.8)},
        "gnome_little": {"beard": (5, 0, 2, 1.5)}, "killer_claus": {"sack": (3, 0, 4, 1.7)}, "millstone_monk": {"jaw": (5, 0, 0, 2.2)},
        "grand_augur": {"gem": (0, 360, 0, 3.0)}, "prism_sentinel": {"ring1": (0, 360, 0, 4.0)}, "clucksworth": {"shell": (0, 0, 3, 1.6)},
        "thorncoil_basilisk": {f"coil{i}": (0, 5 if i % 2 else -5, 2, 2.4) for i in (0, 1, 2, 3, 4, 7)}}


def sway(m, bones):
    """Parts that never moved (ears, tendrils, a tail, a beard, a sack, a floating gem) get their own motion in
    every clip but the spawn and the death: a swing of (x, y, z) degrees each period, or a full turn for 360."""
    for name, a in m.get("anims", {}).items():
        if name.startswith(("death", "die", "opening")): continue
        L = a["length"]
        for b, (x, y, z, per) in bones.items():
            if b in a["bones"] or not any(c["b"] == b for c in m["cubes"]): continue
            n = max(1, round(L / per)); q = L / n
            if 360 in (x, y, z): keys = [[round(i * q / 2, 3), [x * i / 2, y * i / 2, z * i / 2]] for i in range(2 * n + 1)]
            else: keys = [[round(i * q / 4, 3), [v * (0, 1, 0, -1)[i % 4] for v in (x, y, z)]] for i in range(4 * n + 1)]
            a["bones"][b] = {"rot": keys}


def hollow_staff(m):
    """The crook stood half a block behind the hand that was meant to hold it. The whole crook moves forward so the
    shaft runs through the fist, and the light hangs from the tip of the crook in front."""
    hand = next(b for b in m["bones"] if b["name"] == "staff")["pivot"][2]
    rods = [c for c in m["cubes"] if c["b"] == "staff" and "r" in c]
    shaft = max(rods, key=lambda c: c["t"][1] - c["f"][1])
    dz = round(hand - (shaft["f"][2] + shaft["t"][2]) / 2, 2)
    for c in m["cubes"]:
        if c["b"] != "staff": continue
        fist = "r" not in c and c["k"] == "black_concrete"
        if not fist:
            c["f"][2] = round(c["f"][2] + dz, 3); c["t"][2] = round(c["t"][2] + dz, 3)
            if "o" in c: c["o"][2] = round(c["o"][2] + dz, 3)


def scute(m, b, x0, y0, z0, x1, y1, z1, ax, out, dark, light):
    """One shell plate: a raised dark plate with a lighter boss in its middle, standing out along ax by out."""
    lo, hi = [x0, y0, z0], [x1, y1, z1]
    a, c = list(lo), list(hi)
    (c if out > 0 else a)[ax] += out
    box(m, b, dark, *a, *c)
    a, c = list(lo), list(hi)
    for k in range(3):
        if k != ax: w = (hi[k] - lo[k]) * 0.28; a[k] += w; c[k] -= w
    (c if out > 0 else a)[ax] += out * 1.9
    box(m, b, light, *a, *c)


def mossy_turtle(m):
    """The shell was flat plank panels. It is a domed shell of raised plates now: three a side, three front and
    back, four on top, each with a paler boss, and the face has eyes with a shine and a mouth line."""
    m["cubes"] = [c for c in m["cubes"] if c["k"] != "dark_oak_planks"]
    D, L = "green_terracotta", "lime_terracotta"
    for z in (-6.16, -1.76, 2.64): scute(m, "body", 6.0, 5.4, z, 6.0, 8.8, z + 3.6, 0, 0.35, D, L); scute(m, "body", -6.0, 5.4, z, -6.0, 8.8, z + 3.6, 0, -0.35, D, L)
    for x in (-4.6, -1.2, 2.2): scute(m, "body", x, 5.4, 6.44, x + 2.4, 8.8, 6.44, 2, 0.35, D, L); scute(m, "body", x, 5.4, -7.76, x + 2.4, 8.8, -7.76, 2, -0.35, D, L)
    for x in (-3.2, 0.4):
        for z in (-4.6, -0.3): scute(m, "body", x, 12.8, z, x + 2.8, 12.8, z + 3.6, 1, 0.3, D, L)
    for x in (-4.6, 0.6):
        for z in (-6.2, -0.4): scute(m, "body", x, 11.8, z, x + 1.0, 11.8, z + 1.0, 1, 0.01, D, D)
    m["cubes"] = [c for c in m["cubes"] if not (c["b"] == "body" and c["k"] == "lime_terracotta" and abs(c["t"][1] - 13.3) < 0.01 and c["t"][0] - c["f"][0] == 6.0)]
    pair(m, "head", "white_concrete", 2.6, 5.6, 7.6, 2.75, 7.0, 9.2)
    pair(m, "head", "black_concrete", 2.75, 5.8, 8.2, 2.87, 6.8, 9.2)
    pair(m, "head", "white_concrete", 2.87, 6.4, 8.8, 2.97, 6.8, 9.2)
    pair(m, "head", "black_concrete", 0.6, 5.2, 10.44, 1.0, 5.6, 10.56)


def mossback(m):
    """The island turtle's shell was three bare slabs. Each tier has raised plates with paler bosses all round, the
    rim is scalloped, and the head has brows, nostrils and a beak line."""
    D, L = "brown_concrete", "terracotta"
    X = -0.1
    for i in range(4):
        z = -15.2 + i * 7.2
        scute(m, "body", 12.9, 7.6, z, 12.9, 10.4, z + 6.0, 0, 0.4, D, L); scute(m, "body", -13.1, 7.6, z, -13.1, 10.4, z + 6.0, 0, -0.4, D, L)
    for i in range(3):
        z = -13.3 + i * 8.4
        scute(m, "body", 10.9, 11.8, z, 10.9, 15.2, z + 7.4, 0, 0.4, D, L); scute(m, "body", -11.1, 11.8, z, -11.1, 15.2, z + 7.4, 0, -0.4, D, L)
    for i in range(4):
        x = -12.3 + i * 6.3
        scute(m, "body", x, 7.6, -16.1, x + 5.5, 10.4, -16.1, 2, -0.4, D, L)
    for i in range(3):
        x = -10.3 + i * 7.0
        scute(m, "body", x, 11.8, -14.1, x + 6.2, 15.2, -14.1, 2, -0.4, D, L)
        if i != 1: scute(m, "body", x, 11.8, 11.9, x + 6.2, 15.2, 11.9, 2, 0.4, D, L)
    pair(m, "head", "brown_concrete", 1.2 + X, 13.4, 23.9, 3.6 + X, 14.2, 24.5, X)
    pair(m, "head", "black_concrete", 0.5 + X, 11.4, 23.9, 1.1 + X, 12.0, 24.05, X)
    box(m, "head", "brown_concrete", -3.3 + X, 9.4, 23.9, 3.3 + X, 9.8, 24.05)


def wizard(m):
    """The old wizard was plain purple boxes. His robe has a gold hem, cuffs and a starred front, his hat a moon and
    stars, and his face heavy brows and a moustache over the beard."""
    G, W = "gold_block", "white_concrete"
    box(m, "body", G, -5.6, 7.0, -4.6, 5.6, 7.9, 3.6)
    box(m, "body", "brown_terracotta", -5.1, 12.6, -4.1, 5.1, 13.8, 3.1); box(m, "body", G, -1.0, 12.4, 3.1, 1.0, 14.0, 3.5)
    for x, y in ((-3.6, 16.4), (2.6, 18.2), (-2.8, 9.2), (3.0, 10.4)): box(m, "body", "yellow_concrete", x, y, 3.0, x + 0.9, y + 0.9, 3.14)
    pair(m, "foreL", G, 5.4, 10.5, -3.1, 9.6, 11.3, 2.1)
    pair(m, "armL", G, 5.4, 19.7, -3.1, 9.6, 20.5, 2.1)
    box(m, "hat", "yellow_concrete", -1.2, 32.4, 5.0, 1.2, 34.8, 5.14); box(m, "hat", "purple_concrete", -0.2, 32.9, 5.14, 1.4, 34.3, 5.2)
    for x, y in ((-4.2, 31.6), (3.2, 34.6), (-3.4, 35.0)): box(m, "hat", "yellow_concrete", x, y, 5.0, x + 0.8, y + 0.8, 5.14)
    pair(m, "head", W, 1.3, 27.8, 4.0, 4.4, 28.8, 4.9)
    pair(m, "head", "light_gray_concrete", 0.3, 23.6, 6.2, 3.8, 24.6, 6.7)
    for i, x in enumerate((-4.3, -1.5, 1.3)): box(m, "head", "light_gray_concrete", x, 14.2 + (i % 2) * 2.4, 6.2, x + 0.5, 20.8, 6.34)


def egg_cracks(m):
    """The egg shook and blew apart with no warning. Three black cracks now run up the shell one after another
    before it breaks: each is in its own bone, hidden until its moment in the hatching."""
    for i in (1, 2, 3): m["bones"].append({"name": f"shellcrk{i}", "parent": "shell", "pivot": [0.0, 20.0, 0.0]})
    K = "black_concrete"
    def zig(b, pts, face):  # pts: (across, y0, y1); face: ("z", depth) or ("x", depth)
        for u, y0, y1, d in pts:
            if face == "z": box(m, b, K, u, y0, d, u + 1.1, y1, d + 0.14)
            else: box(m, b, K, d, y0, u, d + 0.14 if d > 0 else d - 0.14, y1, u + 1.1)
    zig("shellcrk1", [(-1.6, 11.6, 14.6, 15.4), (-0.5, 14.2, 16.8, 15.4), (-1.4, 16.8, 19.6, 15.2), (-0.3, 19.2, 22.2, 15.2), (-2.7, 14.2, 15.0, 15.4)], "z")
    zig("shellcrk2", [(2.0, 16.9, 19.4, 15.5), (3.1, 19.0, 22.2, 15.5), (1.4, 22.3, 25.0, 14.7), (2.5, 24.6, 27.7, 14.7), (0.9, 12.0, 14.4, 15.7), (2.0, 14.0, 16.7, 15.7)], "x")
    zig("shellcrk3", [(4.0, 22.4, 25.2, 14.4), (5.1, 24.8, 27.7, 14.4), (4.2, 27.8, 30.6, 12.8), (5.3, 30.2, 33.2, 12.8), (3.2, 33.3, 36.0, 10.4), (-6.0, 6.0, 9.0, 14.9), (-4.9, 8.6, 11.2, 14.9)], "z")
    sp = [dict(o) for o in m["spawn"]]
    sp.insert(1, {"op": "shrink", "at": 0, "s": 0, "only": "shellcrk"})
    sp += [{"op": "pose", "at": 16, "dur": 2, "only": "shellcrk1"}, {"op": "pose", "at": 26, "dur": 2, "only": "shellcrk2"},
           {"op": "pose", "at": 34, "dur": 2, "only": "shellcrk3"},
           {"op": "fx", "at": 26, "y": 0.5, "spread": 1.0, "particle": "EGG_CRACK", "count": 14, "sound": "ENTITY_TURTLE_EGG_CRACK", "pitch": 1.1}]
    m["spawn"] = sorted(sp, key=lambda o: o["at"])


LAUNCH = {"hollow_mage": hollow_staff, "cinder_hollow": hollow_staff, "rime_hollow": hollow_staff, "bramble_hollow": hollow_staff,
          "mossy_turtle": mossy_turtle, "mossback": mossback, "old_wizard": wizard, "clucksworth": egg_cracks}


PLANKS = {"dark_oak_planks": "brown_terracotta", "spruce_planks": "brown_concrete", "oak_planks": "yellow_terracotta",
          "birch_planks": "smooth_sandstone", "bamboo_planks": "yellow_terracotta", "crimson_planks": "purple_terracotta"}


def no_planks(m):
    """A plank reads as a building block, never as a hat, a handle or a shell: each one takes the flat block of its colour."""
    n = 0
    for c in m["cubes"]:
        if c["k"] in PLANKS: c["k"] = PLANKS[c["k"]]; n += 1
    return n


def easter_egg(m):
    """Painted, not striped: white diamonds on the lower band too, dots of the band colour round the back and
    sides, a shine on the upper front."""
    band = next(c["k"] for c in m["cubes"] if c["k"] not in ("black_concrete", "white_concrete") and c["k"] != m["cubes"][0]["k"])
    for sx in (-1, 1):
        for z0, z1 in ((4.9, 5.02), (-5.02, -4.9)):
            m["cubes"].append({"b": "body", "k": "white_concrete", "f": [sx * 1.6 - 0.4, 3.8, z0], "t": [sx * 1.6 + 0.4, 4.6, z1], "r": [0, 0, 45], "o": [sx * 1.6, 4.2, (z0 + z1) / 2], "g": "detail"})
            m["cubes"].append({"b": "body", "k": "white_concrete", "f": [z0, 3.8, sx * 1.4 - 0.4], "t": [z1, 4.6, sx * 1.4 + 0.4], "r": [45, 0, 0], "o": [(z0 + z1) / 2, 4.2, sx * 1.4], "g": "detail"})
        for x, y in ((1.6, 6.3), (-1.3, 7.6), (0.1, 5.3)):
            box(m, "body", band, sx * x - 0.4, y, -5.02 if y < 7.2 else -4.92, sx * x + 0.4, y + 0.8, -4.9 if y < 7.2 else -4.8)
        for z, y in ((-1.4, 6.3), (1.5, 7.5)):
            box(m, "body", band, sx * 4.92 if sx > 0 else -5.02, y, z - 0.4, sx * 4.92 + 0.1 if sx > 0 else -4.92, y + 0.8, z + 0.4)
    box(m, "body", "white_concrete", -2.4, 10.95, 2.176, -1.3, 11.85, 2.28)
    box(m, "body", "white_concrete", -2.9, 9.75, 2.56, -2.5, 10.25, 2.66)


def gingerbread(m):
    """Iced like a real biscuit: a scalloped collar, three gumdrops, rosy cheeks, icing curls on the head and an
    icing heart on the back."""
    z = 1.59
    for x in (-2.4, -1.2, 0, 1.2, 2.4):
        box(m, "body", "white_concrete", x - 0.45, 9.55, z, x + 0.45, 10.05, z + 0.1, "trim")
    box(m, "body", "pink_concrete", -0.6, 3.0 + 1.5, z, 0.6, 3.0 + 1.5 + 0.4, z + 0.45)
    for sx in (-1, 1):
        box(m, "body", "pink_concrete", sx * 2.6 - 0.4, 12.5, z - 0.1, sx * 2.6 + 0.4, 13.2, z + 0.02, "trim")
        box(m, "body", "white_concrete", sx * 1.5 - 0.5, 16.2, 0.2, sx * 1.5 + 0.5, 16.5, 1.2, "trim")
        box(m, "body", "white_concrete", sx * 0.7 - 0.45, 6.4, -z - 0.1, sx * 0.7 + 0.45, 7.4, -z, "trim")
    box(m, "body", "white_concrete", -0.5, 16.2, -0.4, 0.5, 16.6, 0.7, "trim")
    box(m, "body", "white_concrete", -0.6, 5.6, -z - 0.1, 0.6, 6.7, -z, "trim")


LAUNCH2 = {"decor_egg_pink": easter_egg, "decor_egg_blue": easter_egg, "decor_egg_mint": easter_egg,
           "decor_gingerbread": gingerbread, "decor_gingerbread_girl": gingerbread}


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
    for id, m in d["models"].items():
        if not m.get("fall-revision"): resize(id, m); fall(m); m["fall-revision"] = 1
    for id, m in d["models"].items():
        if m.get("glitch-revision"): continue
        m["glitch-revision"] = 1
        if id == "tide_tyrant":  # the eye stalks stopped in the air above the head
            for c in m["cubes"]:
                if c["b"] in ("eyeL", "eyeR") and c["k"] == "orange_terracotta": c["f"][1] = 16.0
        mend.unfight(m)
    for id, fn in LAUNCH.items():
        m = d["models"].get(id)
        if m and not m.get("launch-revision"): fn(m); mend.unfight(m); m["launch-revision"] = 1; print("launch", id, len(m["cubes"]))
    planks = 0
    for id, m in d["models"].items():
        if not m.get("plank-revision"):
            planks += no_planks(m); m["plank-revision"] = 1
            if id in LAUNCH2: LAUNCH2[id](m)
            mend.unfight(m)
    print("planks replaced:", planks)
    for id, bones in SWAY.items():
        m = d["models"].get(id)
        if m and not m.get("sway-revision"): sway(m, bones); m["sway-revision"] = 1; print("sway", id)
    for id, fn in MORE2.items():
        m = d["models"].get(id)
        if m and not m.get("mouth-revision"): fn(m); mend.unfight(m); m["mouth-revision"] = 1; print("detail", id, len(m["cubes"]))
    print("pieces flattened or dropped:", total)
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
