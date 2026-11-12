"""v20: the mob style from the user's reference pictures (modded-Minecraft creatures: the gnome and mini gnome,
the old blindman, the moss spirit, the goblins and ogres). Each part is one big clean box in a block picked
for its colour and grain, with shading painted on as a few large deliberate patches (a darker band low down,
a lighter patch where light hits), never single scattered pixels. Faces are drawn on a pixel grid like a mob
skin: eyes with a white and a pupil, brows, a nose that sticks out, a mouth with teeth or tusks. Clothes go on
as layers a little bigger than the body: belts with buckles, straps, cuffs, ragged hems. Concrete stays flat
(the model is flat, so nothing is swapped for speckled powder) and every painted plate sits clear of the
surface under it, so nothing flickers."""
from build import Model
from v14_studio import studio
from v14_kit import standard_anims, idle_biped, walk_biped, attack, wave, K, Z
from v17_sculpt import slab

E = 0.06   # how far a painted plate sits off the face under it


def mob(id):
    """Registers a mob-style model: flat blocks, no mottle pass."""
    def deco(fn):
        def run():
            m = fn()
            m.flat = m.sculpted = True
            m.post = lambda m: (joints(m), unfight(m))
            return m
        run.__name__ = fn.__name__
        run.__doc__ = fn.__doc__
        return studio(id, revise=False)(run)
    return deco


LOOSE = ("tail", "wing", "ring", "ray", "cloud", "key", "lantern", "shovel", "staff", "rod", "cat", "little", "rider", "hat", "beard", "jaw", "inner")


def joints(m):
    """Keeps every limb joined to what it hangs from. The parent gets a ball of the limb's own block round each
    hinge, reaching into the parent's nearest part, and the limb gets a short post from the hinge into its own
    nearest part when that sits away from the hinge. A limb turns about its hinge, so it always passes
    through the ball: bending an elbow, knee, neck or waist never opens a hole, and nothing floats at rest.
    Loose things (tails, wings, rings, held tools) are left alone."""
    pv = {b["name"]: b for b in m.bones}
    solid = lambda c: min(t - f for f, t in zip(c["f"], c["t"])) >= 0.5
    for f in [b["name"] for b in m.bones if b["name"].startswith("foot")]:
        mine = [c for c in m.cubes if c["b"] == f]
        if mine and not any(map(solid, mine)):        # only paint fell below the knee cut: it stays on the shin
            for c in mine: c["b"] = pv[f]["parent"]
    by = {}
    for c in m.cubes:
        if solid(c) and "r" not in c and not c.get("l"): by.setdefault(c["b"], []).append(c)
    def gap(c, P): return sum(max(0, c["f"][i] - P[i], P[i] - c["t"][i]) ** 2 for i in range(3)) ** 0.5
    def near(cs, P): return min(cs, key=lambda c: (round(gap(c, P), 2), -min(c["t"][i] - c["f"][i] for i in (0, 2))))
    def reach(f, t, c):          # stretch a box along each axis until it runs 0.5 into c
        for i in range(3):
            if c["f"][i] > t[i] - 0.5: t[i] = min(c["f"][i] + 0.5, c["t"][i])
            if c["t"][i] < f[i] + 0.5: f[i] = max(c["t"][i] - 0.5, c["f"][i])
        return f, t
    for b in list(m.bones):
        n = b["name"]
        if n not in by or not b["parent"] or any(w in n.lower() for w in LOOSE): continue
        a = b["parent"]
        while a and a not in by: a = pv[a]["parent"]
        if not a: continue
        P = b["pivot"]
        c, q = near(by[n], P), near(by[a], P)
        w = min(c["t"][i] - c["f"][i] for i in (0, 2))
        h = max(0.5, (0.3 if n == "head" else 0.42) * min(w, min(q["t"][i] - q["f"][i] for i in (0, 2))))
        a_bone = a if a == b["parent"] else b["parent"]
        m.box(a_bone, c["k"], *reach([v - h for v in P], [v + h for v in P], q))
        if gap(c, P) > 0.6 * h:
            g = 0.9 * h
            m.box(n, c["k"], *reach([v - g for v in P], [v + g for v in P], c))


def unfight(m):
    """Two faces in one plane, facing the same way, flicker against each other (a band's bottom on its box's
    bottom, a strap flush with a side). The smaller box steps 0.03 out of that plane, so the detail always wins."""
    cs = [c for c in m.cubes if "r" not in c]
    vol = lambda c: (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2])
    for _ in range(3):
        moved = False
        for i, a in enumerate(cs):
            for b in cs[i + 1:]:
                for ax in range(3):
                    if not all(min(a["t"][k], b["t"][k]) - max(a["f"][k], b["f"][k]) > 0.01 for k in range(3) if k != ax): continue
                    s = a if vol(a) < vol(b) else b
                    if abs(a["f"][ax] - b["f"][ax]) < 0.005: s["f"][ax] = round(s["f"][ax] - 0.03, 3); moved = True
                    if abs(a["t"][ax] - b["t"][ax]) < 0.005: s["t"][ax] = round(s["t"][ax] + 0.03, 3); moved = True
        if not moved: break


def bx(m, bone, c, s, block, rot=None, origin=None):
    slab(m, bone, c[0], c[1], c[2], s[0], s[1], s[2], block, rot, origin)


def part(m, bone, c, s, block, dark=None, band=0.28, light=None, rot=None, origin=None):
    """A body part: one box, a darker band round its lower part (a skin just outside it) and a lighter cap on top."""
    bx(m, bone, c, s, block, rot, origin)
    if dark:
        h = s[1] * band
        bx(m, bone, (c[0], c[1] - s[1] / 2 + h / 2, c[2]), (s[0] + 2 * E, h, s[2] + 2 * E), dark, rot, origin or (rot and c))
    if light:
        bx(m, bone, (c[0], c[1] + s[1] / 2 + E / 2, c[2]), (s[0] - 0.02, E, s[2] - 0.02), light, rot, origin or (rot and c))


def paint(m, bone, face, c, rows, ink, p, d=0.1):
    """Pixel rows drawn on one face of a box. face is f (front, +z), b, l (+x side), r (-x side) or t (top);
    c is the centre of that face. Runs of one colour merge into one strip. '.' is left bare."""
    H = len(rows)
    W = max(len(r) for r in rows)
    for j, r in enumerate(rows):
        i = 0
        while i < len(r):
            ch = r[i]
            if ch == ".":
                i += 1; continue
            k = i
            while k < len(r) and r[k] == ch: k += 1
            u = (i + k) / 2 * p - W * p / 2          # across the face, left to right as you look at it
            v = H * p / 2 - (j + 0.5) * p             # up the face
            w = (k - i) * p
            off = E + d / 2
            if face == "f": pos, size = (c[0] + u, c[1] + v, c[2] + off), (w, p, d)
            elif face == "b": pos, size = (c[0] - u, c[1] + v, c[2] - off), (w, p, d)
            elif face == "l": pos, size = (c[0] + off, c[1] + v, c[2] - u), (d, p, w)
            elif face == "r": pos, size = (c[0] - off, c[1] + v, c[2] + u), (d, p, w)
            else: pos, size = (c[0] + u, c[1] + off, c[2] - v), (w, d, p)
            bx(m, bone, pos, size, ink[ch])
            i = k


def moves(m, walk=None, body=0, **clips):
    """A boss's own walk (walk_biped settings, leaning the body forward by body degrees) and signature clips,
    on top of the shared biped set. Clips are written as the engine plays them: +x on a bone tips it forward,
    +z swings the left arm out and the right arm in."""
    if walk:
        w = walk_biped(**walk)
        if body: w["bones"]["body"]["rot"] = [[t, [x + body, y, z]] for t, (x, y, z) in w["bones"]["body"]["rot"]]
        m.anims["walk"] = w
    m.anims.update(clips)


def checker(w, h, odd=0):
    return ["".join("g" if (x + y + odd) % 2 else "." for x in range(w)) for y in range(h)]


# ------------------------------------------------------------------------------------------------ gnomes

def gnome(m, B, X, Z0, s, HAT, COAT, BOOT, LEG, tall=1.0, bent=1.0):
    """One gnome in the style of the gnome-and-mini-gnome picture: a huge stepped hat pulled down to the eyes and
    leaning back, a big peach nose, a long checked beard that hides the body, a coat with a belt, little arms
    and stubby boots. B maps the parts to bones; X, Z0 place him; s scales him."""
    P = lambda x, y, z: (X + x * s, y * s, Z0 + z * s)
    S = lambda w, h, d: (w * s, h * s, d * s)
    SKIN, SKIN_D = "white_terracotta", "pink_terracotta"
    W1, W2 = "white_wool", "white_concrete"
    for sd in (1, -1):
        leg = B["legL"] if sd == 1 else B["legR"]
        bx(m, leg, P(sd * 2.2, 3.6, 0), S(2.4, 3.4, 2.4), LEG)
        part(m, leg, P(sd * 2.2, 1.1, 0.8), S(3.0, 2.2, 4.0), BOOT[0], dark=BOOT[1], band=0.3)
    # the coat with a darker hem, a belt and a gold buckle
    part(m, B["hips"], P(0, 6.6, 0), S(9.0, 2.4, 7.0), COAT[1])
    part(m, B["body"], P(0, 11.2, 0), S(8.4, 7.2, 6.4), COAT[0], dark=COAT[1], band=0.2)
    bx(m, B["body"], P(0, 8.8, 0), S(8.6, 1.0, 6.6), "black_terracotta")
    for sd in (1, -1):
        arm = B["armL"] if sd == 1 else B["armR"]
        part(m, arm, P(sd * 5.4, 12.4, 0), S(2.6, 5.0, 2.6), COAT[0], dark=COAT[1], band=0.25)
        bx(m, arm, P(sd * 5.4, 9.6, 0), S(2.9, 0.9, 2.9), W1)
        part(m, arm, P(sd * 5.4, 8.3, 0.2), S(2.2, 2.0, 2.2), SKIN, dark=SKIN_D, band=0.2)
    # the head, mostly hidden: little dark eyes under bushy brows, rosy cheeks, ears and a big nose
    H = B["head"]
    bx(m, H, P(0, 17.8, 0), S(8.0, 6.6, 7.0), SKIN)
    for sd in (1, -1):
        bx(m, H, P(sd * 4.3, 17.6, 0), S(0.8, 2.0, 1.4), SKIN)
    paint(m, H, "f", P(0, 18.9, 3.5), [".bbb..bbb.", ".bbb..bbb.", "..kw..wk..", "..kk..kk..", "pp......pp"], {"b": W1, "k": "black_concrete", "w": "white_concrete", "p": SKIN_D}, 0.8 * s)
    part(m, H, P(0, 17.0, 4.7), S(3.2, 3.2, 2.4), SKIN, dark=SKIN_D, band=0.18)
    bx(m, H, P(-0.6, 18.0, 5.96), S(1.0, 1.0, 0.1), "white_concrete_powder")            # a shine on the nose
    # the beard: a wide checked curtain from the cheeks to the boots, narrowing at the bottom
    for (y, w, h, z) in ((14.2, 9.2, 6.0, 3.9), (9.2, 8.4, 4.0, 4.0), (6.2, 6.4, 2.0, 4.0), (4.6, 4.0, 1.2, 3.9)):
        bx(m, H, P(0, y, z), S(w, h, 2.2), W1)
        cols, nrows = max(1, round(w / 1.6)), max(1, round(h / 1.6))
        paint(m, H, "f", P(0, y, z + 1.1), checker(cols, nrows, round(y)), {"g": W2}, w / cols * s)
    for sd in (1, -1):
        bx(m, H, P(sd * 3.2, 16.8, 4.0), S(2.8, 1.8, 2.0), W1)                             # moustache either side of the nose
        paint(m, H, "l" if sd == 1 else "r", P(sd * 4.6, 14.2, 3.9), checker(1, 4, sd > 0), {"g": W2}, 1.5 * s)
    # the hat: a brim, then stepped layers that narrow and lean back, the tip flopping over
    layers = [(B["hat1"], 0, 21.2, 0, 9.8, 1.6, 8.8), (B["hat1"], 0, 23.4, -0.2, 9.0, 2.8, 8.0), (B["hat2"], 0.3, 26.6, -0.7, 7.8, 3.6, 7.0),
              (B["hat2"], 0.6, 29.9, -1.3, 6.4, 3.0, 5.6), (B["hat3"], 1.0, 32.6, -2.1, 4.8, 2.6, 4.2), (B["hat3"], 1.6, 34.8, -3.1, 3.4, 2.0, 3.0)]
    base = 21.2
    for k, (b, x, y, z, w, h, d) in enumerate(layers):
        y = base + (y - base) * tall
        part(m, b, P(x * bent, y, z), S(w, h * tall, d), HAT[0] if k else HAT[1])
        if k in (1, 3):
            paint(m, b, "f", P(x * bent - w * 0.22, y + h * tall * 0.15, z + d / 2), ["ll", "l."], {"l": HAT[2]}, 1.2 * s)
            paint(m, b, "l", P(x * bent + w / 2, y + h * tall * 0.2, z), [".l", "ll"], {"l": HAT[2]}, 1.2 * s)
    tip = layers[-1][0]
    yt = base + (36.4 - base) * tall
    part(m, tip, P(2.8 * bent, yt, -4.6), S(2.2, 1.8 * tall, 2.2), HAT[0], dark=HAT[1], rot=(-30, 0, -30 * bent), origin=P(2.8 * bent, yt, -4.6))


@mob("gnome_brothers")
def gnome_brothers():
    """The Gnome Brothers, from the gnome-and-mini-gnome picture: Bramble in a huge leaning green hat and a red
    coat, and his little brother Thimble at his side in a tall dark red hat and a green coat. Both have big
    peach noses and long checked white beards. The hats sway and Thimble hops about."""
    from v14_kit import humanoid
    m = Model("gnome_brothers", "biped", 2.2)
    humanoid(m, hip=6, legx=2.2, neck=16, shoulder=15, armx=5.4)
    m.bone("hat1", "head", (0, 21, 0)); m.bone("hat2", "hat1", (0.3, 24.8, -0.6)); m.bone("hat3", "hat2", (1.0, 31.2, -2.0))
    X, Z0, s = 9.6, -2.4, 0.62
    m.bone("little", "root", (X, 0, Z0)); m.bone("lhead", "little", (X, 16 * s, Z0))
    m.bone("lhat1", "lhead", (X, 21 * s, Z0)); m.bone("lhat2", "lhat1", (X, 30 * s, Z0 - 1.4 * s))
    GREEN = ("green_concrete", "green_terracotta", "green_concrete_powder")
    RED = ("red_terracotta", "brown_terracotta", "terracotta")
    gnome(m, {k: k for k in ("legL", "legR", "hips", "body", "armL", "armR", "head", "hat1", "hat2", "hat3")}, 0, 0, 1.0,
          GREEN, ("red_wool", "red_terracotta"), ("brown_terracotta", "black_terracotta"), "gray_concrete")
    L = {"legL": "little", "legR": "little", "hips": "little", "body": "little", "armL": "little", "armR": "little",
         "head": "lhead", "hat1": "lhat1", "hat2": "lhat1", "hat3": "lhat2"}
    gnome(m, L, X, Z0, s, RED, ("green_concrete", "green_terracotta"), ("green_terracotta", "black_terracotta"), "brown_terracotta", tall=1.45, bent=-1.0)
    hop = K((0, Z), (0.4, (0, 1.4, 0)), (0.8, Z), (2.0, Z), (2.4, (0, 1.4, 0)), (2.8, Z), (4.0, Z))
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(4.0, 12, breath=0.03, extra={
        "hat1": {"rot": wave(2, 3, 4.0)}, "hat2": {"rot": wave(2, 5, 4.0, 0.1)}, "hat3": {"rot": wave(2, 9, 4.0, 0.2)},
        "little": {"pos": hop}, "lhead": {"rot": wave(1, 16, 4.0)},
        "lhat1": {"rot": wave(2, 5, 4.0, 0.3)}, "lhat2": {"rot": wave(2, 10, 4.0, 0.45)}})})
    up = lambda sd: K((0, Z), (0.3, (-40, 0, 10 * sd)), (0.55, (-160, 0, -40 * sd)), (0.7, (-150, 0, -55 * sd)), (0.85, (-160, 0, -40 * sd)), (1.0, (-150, 0, -55 * sd)), (1.4, Z))   # raised, -z throws the left arm wide
    moves(m, dict(length=0.8, swing=24, arm=22, bob=0.9, sway=8),
          rally=attack(1.4, 0.55, {"armL": {"rot": up(1)}, "armR": {"rot": up(-1)}, "body": {"rot": K((0, Z), (0.3, (10, 0, 0)), (0.55, (-14, 0, 0)), (1.4, Z))},
                                   "head": {"rot": K((0, Z), (0.55, (-22, 0, 0)), (0.85, (-18, 12, 0)), (1.0, (-18, -12, 0)), (1.4, Z))},
                                   "hips": {"pos": K((0, Z), (0.3, (0, -1.2, 0)), (0.55, (0, 2.6, 0)), (0.75, Z), (0.9, (0, 1.2, 0)), (1.05, Z), (1.4, Z))},
                                   "little": {"rot": K((0, Z), (0.45, (0, 0, 0)), (0.7, (-12, 20, 0)), (0.95, (-12, -20, 0)), (1.4, Z))},
                                   "hat3": {"rot": K((0, Z), (0.55, (24, 0, 0)), (0.8, (-18, 0, 0)), (1.4, Z))}}))
    m.attacks = {"minions": "rally", "leap": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


def lit(m):
    m.cubes[-1]["l"] = True


# ------------------------------------------------------------------------------------------------ Ugor

@mob("ugor")
def ugor():
    """Ugor, the last brute: a huge hunched boar-man in coarse brown fur with a dark mane from his crown down his
    back, a big pink snout, small mean eyes under a heavy black brow, two curved ivory tusks, floppy ears, a
    studded belt with a skull buckle over a ragged leather loincloth, a necklace of teeth, long arms with
    leather-wrapped forearms and huge fists, and black hooves."""
    from v14_kit import humanoid
    m = Model("ugor", "biped", 2.0)
    humanoid(m, hip=12, legx=4.4, neck=27, shoulder=26, armx=11.4, jaw=(0, 26.4, 6))
    FUR, DARK, LIGHT, MANE = "brown_wool", "brown_terracotta", "terracotta", "black_terracotta"
    PINK, PINK_D, IVORY = "pink_terracotta", "brown_terracotta", "end_stone"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 4.4
        part(m, leg, (x, 9.4, 0), (5.2, 6.0, 5.2), FUR)
        part(m, leg, (x, 4.6, 0.4), (4.4, 4.0, 4.4), FUR, dark=DARK, band=0.35)
        part(m, leg, (x, 1.2, 1.0), (4.8, 2.4, 5.6), MANE)
        paint(m, leg, "f", (x, 1.2, 3.8), [".k.", ".k."], {"k": "gray_terracotta"}, 1.2)          # the split in the hoof
    # a studded black belt with a skull buckle, a ragged loincloth front and back
    bx(m, "hips", (0, 13.4, 0.4), (12.6, 2.4, 9.6), MANE)
    for x in (-5.2, -3.4, 3.4, 5.2):
        bx(m, "hips", (x, 13.4, 5.3), (0.8, 0.8, 0.2), "light_gray_concrete")
    bx(m, "hips", (0, 13.4, 5.5), (3.2, 2.8, 0.6), "white_concrete")
    paint(m, "hips", "f", (0, 13.6, 5.8), ["k.k", "...", ".k."], {"k": "black_concrete"}, 0.8)
    for z, sd in ((5.2, 1), (-4.4, -1)):
        bx(m, "hips", (0, 10.0, z), (7.0, 4.6, 0.6), DARK)
        for i, x in enumerate((-2.6, -0.9, 0.9, 2.6)):
            bx(m, "hips", (x, 7.2 - (i % 2) * 0.6, z), (1.6, 1.2 + (i % 2) * 1.2, 0.6), DARK)
    # the body: a deep barrel chest, a paler belly and a hump of muscle under the mane
    part(m, "body", (0, 20.2, 0.4), (17.0, 10.0, 11.0), FUR, dark=DARK, band=0.2)
    bx(m, "body", (0, 18.6, 5.96 + E), (9.0, 6.4, 0.1), LIGHT)
    part(m, "body", (0, 26.6, -1.0), (15.0, 3.6, 9.0), FUR)
    # a necklace of teeth
    bx(m, "body", (0, 24.2, 6.0), (11.0, 0.5, 0.3), MANE)
    for x in (-4.4, -2.2, 0, 2.2, 4.4):
        bx(m, "body", (x, 23.0, 6.1), (0.8, 2.0, 0.4), IVORY, rot=(0, 0, -x * 3), origin=(x, 24.0, 6.1))
    # the mane, from the crown down his back
    for y, z, h, w in ((28.8, -2.0, 3.0, 4.2), (25.6, -5.6, 4.0, 3.6), (21.4, -6.2, 4.6, 3.2), (17.0, -6.2, 3.6, 2.6)):
        bx(m, "body", (0, y, z), (w, h, 1.6), MANE)
    # long arms: fur shoulders, leather-wrapped forearms and big fists with knuckles drawn on
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 11.4
        part(m, arm, (x, 25.0, 0), (6.2, 5.4, 6.2), FUR, light=LIGHT)
        paint(m, arm, "l" if sd == 1 else "r", (x + sd * 3.1, 24.6, 0), ["kk.k..", ".k..kk", "...k.."], {"k": DARK}, 1.0)
        part(m, arm, (x + sd * 0.4, 19.4, 0.4), (5.0, 6.6, 5.0), FUR)
        part(m, arm, (x + sd * 0.7, 13.2, 0.8), (5.4, 6.4, 5.4), FUR)
        for y, b in ((14.6, DARK), (12.4, MANE)):
            bx(m, arm, (x + sd * 0.7, y, 0.8), (5.7, 1.4, 5.7), b)
        part(m, arm, (x + sd * 0.9, 8.0, 1.2), (6.0, 4.4, 6.0), FUR, dark=DARK, band=0.25)
        paint(m, arm, "f", (x + sd * 0.9, 8.6, 4.2), ["k.k.k", "k.k.k"], {"k": DARK}, 1.0)
    for x in (-1.4, 0, 1.4):
        bx(m, "head", (x, 35.6, 4.6), (0.9, 2.2, 0.9), MANE, rot=(-25, 0, x * 10), origin=(x, 34.8, 4.6))
    # the head: low and forward, heavy black brow, little eyes, floppy ears, a big snout
    part(m, "head", (0, 30.6, 6.6), (11.4, 8.6, 9.0), FUR, light=LIGHT)
    bx(m, "head", (0, 33.6, 11.2), (11.8, 1.6, 1.4), MANE)
    paint(m, "head", "f", (0, 31.8, 11.1), ["wk....kw", "kk....kk"], {"k": "black_concrete", "w": "red_concrete"}, 0.9)
    for sd in (1, -1):
        part(m, "head", (sd * 7.2, 33.2, 5.4), (4.0, 1.2, 3.2), FUR, rot=(0, 0, -34 * sd), origin=(sd * 5.7, 33.6, 5.4))
        bx(m, "head", (sd * 7.2, 33.2 + 0.66, 5.4), (3.0, 0.1, 2.2), PINK, rot=(0, 0, -34 * sd), origin=(sd * 5.7, 33.6, 5.4))
    part(m, "head", (0, 29.0, 12.6), (6.2, 4.2, 3.6), PINK, dark=PINK_D, band=0.18)
    paint(m, "head", "f", (0, 29.0, 14.4), ["......", ".kk.kk", ".kk.kk", "......"], {"k": PINK_D}, 0.8)
    # the jaw with an underbite of teeth, and the tusks curving up past the snout
    part(m, "jaw", (0, 25.8, 9.6), (9.0, 2.4, 7.0), FUR, dark=DARK, band=0.4)
    paint(m, "jaw", "f", (0, 26.6, 13.1), ["w.w.w.w"], {"w": IVORY}, 0.7)
    for sd in (1, -1):
        bx(m, "jaw", (sd * 3.7, 27.4, 12.4), (1.4, 3.0, 1.4), IVORY, rot=(0, 0, -14 * sd), origin=(sd * 3.7, 26.0, 12.4))
        bx(m, "jaw", (sd * 4.2, 29.6, 12.6), (1.0, 1.8, 1.0), IVORY, rot=(-20, 0, -30 * sd), origin=(sd * 3.9, 28.8, 12.4))
    # coarse detail: bristles along the mane, fur patches on the thighs and back, scars, studded wraps
    for y, z in ((31.0, -0.6), (27.6, -4.6), (23.4, -6.6), (19.0, -6.6)):
        for sd in (1, -1):
            bx(m, "body", (sd * 1.4, y, z - 1.0), (0.8, 2.4, 0.8), MANE, rot=(-30, 0, 14 * sd), origin=(sd * 1.4, y - 1.0, z - 1.0))
    for sd, leg in ((1, "legL"), (-1, "legR")):
        bx(m, leg, (sd * 4.4, 2.7, 1.0), (5.0, 0.6, 5.8), DARK)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        for y in (14.6, 12.4):
            paint(m, arm, "f", (sd * 12.1, y, 3.5 + E), ["w.w.w"], {"w": "light_gray_concrete"}, 0.8)
    # a bone shoulder plate with spikes, strapped across the chest
    part(m, "armL", (11.6, 28.2, 0), (7.4, 1.8, 7.4), "calcite", dark="light_gray_concrete", band=0.4)
    for z in (-2.2, 0, 2.2):
        bx(m, "armL", (12.4, 30.0, z), (1.0, 2.4, 1.0), IVORY, rot=(0, 0, -20), origin=(12.4, 29.0, z))
    bx(m, "body", (1.2, 20.4, 6.1), (2.0, 15.6, 0.4), DARK, rot=(0, 0, 38), origin=(1.2, 20.4, 6.1))
    bx(m, "body", (1.2, 20.4, -5.3), (2.0, 15.6, 0.4), DARK, rot=(0, 0, -38), origin=(1.2, 20.4, -5.3))
    bx(m, "body", (-2.2, 16.8, 6.4), (1.8, 1.8, 0.3), "iron_block")
    # a gold ring through the snout, thumbs on the fists, tufts at the ends of the brow
    bx(m, "head", (0, 26.9, 14.4), (2.0, 0.4, 0.4), "gold_block")
    for sd in (1, -1):
        bx(m, "head", (sd * 0.8, 27.3, 14.4), (0.4, 1.0, 0.4), "gold_block")
        bx(m, "head", (sd * 6.2, 33.9, 10.4), (1.4, 1.2, 1.4), MANE, rot=(0, 0, -25 * sd), origin=(sd * 5.6, 33.6, 10.4))
        arm = "armL" if sd == 1 else "armR"
        bx(m, arm, (sd * 9.4, 8.8, 4.2), (1.4, 2.6, 1.6), FUR)
    for z in (5.55, -4.75):
        bx(m, "hips", (0, 12.1, z), (7.2, 0.6, 0.6), MANE)
    # bristles on the crown
    m.bend = -16
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(3.6, 14, breath=0.05, extra={"jaw": {"rot": wave(0, 4, 3.6)}})})
    def beat(sd, d):
        hit, lift = (-28, 0, -24 * sd), (-48, 0, -30 * sd)
        return K((0, Z), *[(t + d, v) for k in range(3) for t, v in ((0.25 + 0.4 * k, lift), (0.4 + 0.4 * k, hit))], (1.9, Z))
    moves(m, dict(length=1.3, swing=22, arm=24, bob=1.4, sway=6), body=6,
          beat=attack(1.9, 0.6, {"armL": {"rot": beat(1, 0)}, "armR": {"rot": beat(-1, 0.2)},
                                 "foreL": {"rot": K((0, Z), (0.25, (-95, 0, 0)), (1.4, (-95, 0, 0)), (1.9, Z))},
                                 "foreR": {"rot": K((0, Z), (0.45, (-95, 0, 0)), (1.6, (-95, 0, 0)), (1.9, Z))},
                                 "body": {"rot": K((0, Z), (0.3, (-14, 0, 0)), (1.5, (-12, 0, 0)), (1.9, Z)),
                                          "scl": K((0, (1, 1, 1)), (0.4, (1.06, 1.03, 1.08)), (0.8, (1.03, 1, 1.04)), (1.2, (1.07, 1.03, 1.09)), (1.9, (1, 1, 1)))},
                                 "head": {"rot": K((0, Z), (0.3, (-26, 0, 0)), (1.0, (-22, 10, 0)), (1.4, (-22, -10, 0)), (1.9, Z))},
                                 "jaw": {"rot": K((0, Z), (0.3, (34, 0, 0)), (1.5, (30, 0, 0)), (1.9, Z))}}))
    m.attacks = {"minions": "beat", "charge": "lunge", "quake": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ Mister Bones

@mob("gravelord")
def gravelord():
    """Mister Bones, the gravedigger: a big chunky skeleton in a tall battered top hat with a purple band and a
    long black coat hanging open over his ribs. Soul-blue lights burn in his eye sockets above a toothy grin.
    He has bony hands and knees, worn boots, a soul lantern on his belt, and digs with a huge iron shovel."""
    from v14_kit import humanoid
    m = Model("gravelord", "biped", 1.9)
    humanoid(m, hip=13, legx=3.4, neck=30, shoulder=29, armx=7.4, jaw=(0, 31.2, 2))
    m.bone("hat", "head", (0, 38, 0))
    m.bone("shovel", "armR", (-8.2, 7.6, 1.6))
    m.bone("lantern", "hips", (5.4, 12.6, 3.4))
    m.hold = {"shovel": 0}
    BONE, BONE_D, COAT, COAT_D = "calcite", "light_gray_concrete", "black_wool", "gray_wool"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.4
        bx(m, leg, (x, 10.0, 0), (1.6, 5.6, 1.6), BONE)
        bx(m, leg, (x, 7.0, 0.2), (2.4, 1.8, 2.4), BONE)                                       # knee
        bx(m, leg, (x, 4.4, 0.3), (1.4, 3.6, 1.4), BONE)
        part(m, leg, (x, 1.3, 1.0), (3.2, 2.6, 4.6), "black_terracotta", dark="brown_terracotta", band=0.25)
    # the pelvis and a belt with the soul lantern hanging from it
    bx(m, "hips", (0, 13.2, 0), (7.4, 2.4, 4.0), BONE)
    bx(m, "hips", (0, 14.6, 0), (8.4, 1.0, 5.0), "brown_terracotta")
    bx(m, "hips", (0, 14.6, 2.6), (1.4, 1.2, 0.3), "gold_block")
    bx(m, "lantern", (5.4, 11.8, 3.4), (0.4, 1.6, 0.4), "chain")
    bx(m, "lantern", (5.4, 9.6, 3.4), (2.2, 2.8, 2.2), "soul_lantern"); lit(m)
    # the ribcage and spine, the coat hanging open over them
    bx(m, "body", (0, 21.0, -0.6), (1.6, 13.0, 1.6), BONE)
    for k, y in enumerate((26.0, 23.8, 21.6, 19.4)):
        w = 8.4 - k * 0.8
        bx(m, "body", (0, y, 0.4), (w, 1.1, 4.4), BONE)
    bx(m, "body", (0, 22.8, 2.4), (1.0, 6.0, 0.6), BONE)                                      # breastbone
    for sd in (1, -1):
        part(m, "body", (sd * 4.2, 22.0, 0), (2.6, 14.0, 6.4), COAT, dark=COAT_D, band=0.12)
        bx(m, "body", (sd * 3.0, 27.6, 3.3), (1.6, 3.2, 0.4), COAT_D, rot=(0, 0, 16 * sd), origin=(sd * 3.0, 27.6, 3.3))    # lapels
    part(m, "body", (0, 22.0, -2.9), (8.6, 14.0, 1.2), COAT)
    part(m, "body", (0, 28.4, 0), (11.0, 2.4, 6.6), COAT)
    # the coat tails, split at the back and torn at the hem
    for sd in (1, -1):
        bx(m, "hips", (sd * 2.6, 10.6, -2.6), (4.6, 6.0, 1.0), COAT)
        bx(m, "hips", (sd * 4.6, 10.2, 1.2), (1.2, 6.8, 5.2), COAT)
        paint(m, "hips", "b", (sd * 2.6, 9.2, -3.1), ["k.k", "kkk"], {"k": COAT_D}, 1.2)
    # thin bony arms with knobbly elbows and long fingers
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 7.4
        part(m, arm, (x, 25.4, 0), (3.4, 7.6, 3.8), COAT, dark=COAT_D, band=0.14)
        bx(m, arm, (x + sd * 0.3, 20.6, 0.4), (2.0, 1.6, 2.0), BONE)
        bx(m, arm, (x + sd * 0.5, 15.6, 0.8), (1.3, 7.0, 1.3), BONE)
        bx(m, arm, (x + sd * 0.6, 11.4, 1.2), (2.6, 1.6, 2.4), BONE)
        for t in (-0.8, 0, 0.8):
            bx(m, arm, (x + sd * 0.6 + t, 9.6, 1.8), (0.5, 2.4, 0.5), BONE_D)
    # the skull: a big square one, deep sockets with soul lights, a nose hole and a toothy grin
    part(m, "head", (0, 34.4, 0.4), (8.6, 6.4, 8.0), BONE, dark=BONE_D, band=0.12)
    paint(m, "head", "f", (0, 34.6, 4.4), [".kkk..kkk.", ".kbk..kbk.", ".kkk..kkk.", "....kk....", "....kk...."],
          {"k": "black_concrete", "b": "black_concrete"}, 0.85)
    bx(m, "head", (-2.12, 35.45, 4.58), (0.6, 0.6, 0.1), "light_blue_concrete"); lit(m)
    bx(m, "head", (2.12, 35.45, 4.58), (0.6, 0.6, 0.1), "light_blue_concrete"); lit(m)
    part(m, "jaw", (0, 30.4, 1.4), (7.4, 2.0, 6.8), BONE, dark=BONE_D, band=0.3)
    paint(m, "jaw", "f", (0, 31.0, 4.8), ["kwkwkwkwk"], {"k": "black_concrete", "w": "white_concrete"}, 0.75)
    # the top hat: a wide brim, a tall battered crown leaning back, a purple band with a buckle
    part(m, "hat", (0, 38.0, 0.4), (11.4, 0.9, 10.6), COAT)
    part(m, "hat", (0, 41.6, 0.2), (7.4, 6.4, 7.0), COAT, light=COAT_D, rot=(-6, 0, 4), origin=(0, 38.4, 0.2))
    bx(m, "hat", (0, 39.4, 0.2), (7.6, 1.4, 7.2), "purple_terracotta", rot=(-6, 0, 4), origin=(0, 38.4, 0.2))
    bx(m, "hat", (0, 39.4, 3.85), (1.6, 1.4, 0.2), "gold_block", rot=(-6, 0, 4), origin=(0, 38.4, 0.2))
    # the shovel: a long wooden handle, a D grip at the top and an iron blade at the bottom
    bx(m, "shovel", (-8.2, 13.0, 1.6), (1.2, 22.0, 1.2), "stripped_spruce_log")
    bx(m, "shovel", (-8.2, 25.0, 1.6), (3.0, 0.8, 1.0), "stripped_spruce_log")
    for sd in (1, -1):
        bx(m, "shovel", (-8.2 + sd * 1.2, 24.0, 1.6), (0.6, 2.0, 0.8), "stripped_spruce_log")
    part(m, "shovel", (-8.2, 0.8, 1.6), (4.4, 4.6, 0.6), "iron_block", dark="light_gray_concrete", band=0.3)
    bx(m, "shovel", (-8.2, 3.6, 1.6), (1.8, 1.4, 1.2), "iron_block")
    m.bend = -20
    standard_anims(m, heavy=1.0, extra={"idle": idle_biped(4.0, 18, breath=0.03, extra={
        "jaw": {"rot": wave(0, 5, 2.0)}, "hat": {"rot": wave(2, 4, 4.0, 0.2)}, "lantern": {"rot": wave(0, 14, 2.0)}})})
    moves(m, dict(length=1.2, swing=28, arm=12, bob=0.8, sway=4), body=4,
          dig=attack(1.4, 0.75, {"armR": {"rot": K((0, Z), (0.4, (-24, 0, 6)), (0.6, (-36, 0, 0)), (0.75, (-150, 0, -6)), (1.0, (-140, 0, -6)), (1.4, Z))},
                                 "armL": {"rot": K((0, Z), (0.4, (-50, 0, 8)), (0.75, (-120, 0, -8)), (1.0, (-110, 0, -8)), (1.4, Z))},
                                 "foreR": {"rot": K((0, Z), (0.4, (-10, 0, 0)), (0.75, (-30, 0, 0)), (1.4, Z))},
                                 "body": {"rot": K((0, Z), (0.4, (28, 0, 0)), (0.6, (30, 0, 0)), (0.75, (-12, 0, 0)), (1.0, (-10, 0, 0)), (1.4, Z))},
                                 "head": {"rot": K((0, Z), (0.4, (12, 0, 0)), (0.75, (-20, 0, 0)), (1.4, Z))},
                                 "hat": {"rot": K((0, Z), (0.75, (-14, 0, 0)), (1.0, (6, 0, 0)), (1.4, Z))},
                                 "hips": {"pos": K((0, Z), (0.4, (0, -1.5, 0)), (0.75, (0, 0.6, 0)), (1.4, Z))}}))
    m.attacks = {"skulls": "cast", "pull": "dig", "minions": "roar"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ Grimsby

@mob("gate_shade")
def gate_shade():
    """Grimsby, the gate gargoyle: a crouching stone gargoyle that hovers on slow beats of its bat wings, mossy on
    the shoulders, with curled horns, a heavy brow over glowing soul-blue eyes, a wide fanged grin and pointed
    ears. It hugs a huge iron key to its chest with clawed hands, its legs are tucked up under it, and a long
    tail with a spade tip hangs below."""
    m = Model("gate_shade", "float", 2.0)
    STONE, STONE_D, STONE_L, MOSS = "stone", "andesite", "polished_andesite", "moss_block"
    WING, WING_D = "gray_concrete", "cobbled_deepslate"
    m.bone("core", "root", (0, 16, 0))
    m.bone("head", "core", (0, 30, 2))
    m.bone("armL", "core", (7.4, 27, 1)); m.bone("armR", "core", (-7.4, 27, 1))
    m.bone("ring1", "core", (0, 16, 0)); m.bone("ring2", "ring1", (0, 12, 0)); m.bone("ring3", "ring2", (0, 8, 0))
    m.bone("wingL", "core", (4, 28, -4)); m.bone("wingR", "core", (-4, 28, -4))
    m.bone("tail", "core", (0, 16, -3))
    # the body: a hunched stone torso, moss over the shoulders, a carved belly
    part(m, "core", (0, 22.6, 0), (12.0, 11.0, 8.6), STONE, dark=STONE_D, band=0.25)
    part(m, "core", (0, 28.6, -0.6), (13.4, 3.2, 9.4), STONE, light=MOSS)
    paint(m, "core", "f", (0, 28.4, 4.1), ["mm.mmm.mm", "m...m...m", "....m...."], {"m": MOSS}, 1.0)
    paint(m, "core", "f", (0, 21.0, 4.3), [".kkkkk.", ".......", ".kkkkk.", ".......", "..kkk.."], {"k": STONE_D}, 1.0)
    # legs tucked up, big clawed feet under the belly
    for sd in (1, -1):
        part(m, "core", (sd * 4.4, 17.2, 1.4), (4.4, 4.0, 6.4), STONE, dark=STONE_D, band=0.3)
        part(m, "core", (sd * 4.4, 15.0, 4.4), (4.0, 1.8, 3.4), STONE_D)
        paint(m, "core", "f", (sd * 4.4, 15.0, 6.1), ["w.w.w"], {"w": STONE_L}, 0.7)
    # the tail with a spade tip
    for i, (y, z) in enumerate(((14.4, -4.6), (11.2, -6.0), (8.2, -6.6))):
        bx(m, "tail", (0, y, z), (1.8 - i * 0.3, 3.6, 1.8 - i * 0.3), STONE, rot=(30 - i * 15, 0, 0), origin=(0, y + 1.8, z))
    bx(m, "tail", (0, 5.8, -6.8), (2.6, 2.6, 0.8), STONE_D, rot=(0, 0, 45), origin=(0, 5.8, -6.8))
    # the wings: an arm bone along the top with three finger spars and dark membrane between them
    for sd, w in ((1, "wingL"), (-1, "wingR")):
        o, r = (sd * 4.0, 28.0, -5.0), (0, 30 * sd, 0)
        bx(m, w, (sd * 9.4, 32.2, -5.0), (11.0, 1.4, 1.4), STONE, rot=r, origin=o)                   # the arm bone
        bx(m, w, (sd * 15.2, 33.4, -5.0), (1.2, 3.6, 1.2), STONE, rot=r, origin=o)                   # the thumb claw
        for cx, w_, top, h in ((6.6, 5.2, 31.6, 10.0), (10.6, 3.0, 31.6, 8.0), (13.4, 2.8, 31.6, 5.6)):
            bx(m, w, (sd * cx, top - h / 2, -5.2), (w_, h, 0.4), WING, rot=r, origin=o)
        for cx, h in ((9.0, 9.6), (12.0, 7.4), (14.6, 5.2)):
            bx(m, w, (sd * cx, 31.6 - h / 2, -4.9), (0.6, h, 0.4), WING_D, rot=r, origin=o)            # finger bones
    # arms hugging the key, with claws
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 7.4
        part(m, arm, (x, 26.6, 1.0), (4.0, 4.0, 4.4), STONE, light=MOSS)
        part(m, arm, (x - sd * 0.4, 22.2, 2.6), (3.2, 5.0, 3.4), STONE)
        part(m, arm, (x - sd * 2.4, 19.6, 4.6), (3.6, 2.4, 3.6), STONE_D)
        paint(m, arm, "f", (x - sd * 2.4, 19.4, 6.4), ["w.w.w"], {"w": STONE_L}, 0.7)
    # the key, held upright against the chest
    bx(m, "core", (0, 10.6, 6.6), (1.4, 14.0, 1.4), "iron_block")
    for dx, dy, w, h in ((0, 3.2, 5.0, 1.2), (0, -1.0, 5.0, 1.2), (-1.9, 1.1, 1.2, 5.4), (1.9, 1.1, 1.2, 5.4)):
        bx(m, "core", (dx, 19.4 + dy, 6.8), (w, h, 1.0), "iron_block")
    for y, w in ((4.4, 3.0), (6.4, 2.2)):
        bx(m, "core", (1.6 + w / 2 - 1.0, y, 6.6), (w, 1.2, 1.2), "iron_block")
    # the head: a broad stone face, curled horns, pointed ears, a heavy brow, soul eyes and a fanged grin
    part(m, "head", (0, 33.4, 2.8), (9.0, 7.0, 8.0), STONE, dark=STONE_D, band=0.2, light=STONE_L)
    bx(m, "head", (0, 35.2, 6.9), (9.4, 1.4, 0.6), STONE_D)
    paint(m, "head", "f", (0, 34.0, 6.8), ["kkk...kkk", "kbk...kbk"], {"k": "black_concrete", "b": "black_concrete"}, 0.8)
    for sd in (1, -1):
        bx(m, "head", (sd * 2.4, 33.6, 6.94), (0.7, 0.7, 0.1), "light_blue_concrete"); lit(m)
        bx(m, "head", (sd * 5.6, 34.6, 2.6), (2.6, 2.6, 0.6), STONE, rot=(0, 30 * sd, -30 * sd), origin=(sd * 4.5, 34, 2.6))     # ears
        bx(m, "head", (sd * 3.8, 38.2, 1.8), (1.8, 3.0, 1.8), STONE_D, rot=(-20, 0, -24 * sd), origin=(sd * 3.4, 36.8, 1.8))     # horns
        bx(m, "head", (sd * 4.8, 40.2, 0.2), (1.2, 2.4, 1.2), STONE_D, rot=(-55, 0, -40 * sd), origin=(sd * 4.4, 39.4, 1.0))
    bx(m, "head", (0, 32.0, 7.2), (2.0, 1.8, 1.4), STONE)                                         # snub nose
    bx(m, "head", (0, 30.6, 6.86), (7.0, 1.6, 0.1), "black_concrete")
    paint(m, "head", "f", (0, 30.6, 6.86), ["w.w...w.w"], {"w": "white_concrete"}, 0.75)
    flap = lambda sd: {"rot": K((0, (0, -10 * sd, 0)), (1.0, (0, 26 * sd, 0)), (2.0, (0, -10 * sd, 0)), (3.0, (0, 26 * sd, 0)), (4.0, (0, -10 * sd, 0)))}
    m.anims = {"idle": {"length": 4.0, "loop": True, "bones": {
        "core": {"pos": K((0, Z), (1.0, (0, 1.6, 0)), (2.0, Z), (3.0, (0, 1.6, 0)), (4.0, Z))},
        "head": {"rot": K((0, (0, -10, 0)), (2.0, (4, 10, 0)), (4.0, (0, -10, 0)))},
        "wingL": flap(1), "wingR": flap(-1), "tail": {"rot": wave(2, 10, 4.0)}}}}
    m.attacks = {"blink": "spin", "darkness": "raise", "minions": "pulse"}
    m.melee = "swipe"
    return m


def litbox(m, bone, c, s, block):
    bx(m, bone, c, s, block); lit(m)


# ------------------------------------------------------------------------------------------------ Bjorn

@mob("storm_herald")
def storm_herald():
    """Bjorn, the Storm Ram: a towering ram-man in thick white wool with grey patches, a long dark grey face with
    a pale muzzle and a wool goatee, glowing yellow eyes with slit pupils, two huge cream horns that curl back
    and round past his ears, a storm cloud riding his shoulders with lit bolts hanging from it, copper bracers
    on dark forearms, a forked copper rod in his fist and black hooves."""
    from v14_kit import humanoid
    m = Model("storm_herald", "biped", 2.0)
    humanoid(m, hip=11, legx=3.8, neck=28, shoulder=27, armx=9.8, jaw=(0, 29, 5))
    m.bone("cloud", "body", (0, 31, -4))
    m.bone("rod", "armR", (-10.8, 9.6, 1.2))
    m.hold = {"rod": 4}
    W, W2, SKIN, SKIN_L = "white_wool", "light_gray_wool", "gray_concrete", "light_gray_concrete"
    HORN, HORN_D, COP = "sandstone", "cut_sandstone", "copper_block"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.8
        part(m, leg, (x, 8.6, 0), (5.0, 5.2, 5.0), W, dark=W2, band=0.25)
        bx(m, leg, (x, 4.2, 0.3), (3.2, 3.8, 3.2), SKIN)
        part(m, leg, (x, 1.1, 0.8), (4.0, 2.2, 4.8), "black_terracotta")
        paint(m, leg, "f", (x, 1.1, 3.2), [".k.", ".k."], {"k": "gray_terracotta"}, 1.0)
    # a wool skirt under a belt with a copper buckle and a lightning sign on it
    part(m, "hips", (0, 10.0, 0.2), (12.4, 3.6, 8.4), W)
    paint(m, "hips", "f", (0, 8.6, 4.4), ["g.g..g.g..g.", "g.g.gg.g.g.g"], {"g": W2}, 1.03)
    bx(m, "hips", (0, 12.6, 0.2), (13.0, 1.6, 8.8), "brown_terracotta")
    bx(m, "hips", (0, 12.6, 4.7), (3.0, 2.2, 0.4), COP)
    paint(m, "hips", "f", (0, 12.6, 4.9), [".y", "y.", ".y"], {"y": "yellow_concrete"}, 0.6)
    # a deep woolly chest with a fluffy bib and grey patches
    part(m, "body", (0, 20.0, 0.3), (15.0, 11.0, 9.6), W, dark=W2, band=0.18)
    part(m, "body", (0, 22.6, 5.4), (10.0, 6.0, 1.0), W)
    for y, w in ((20.2, 8.6), (18.6, 6.4)):
        bx(m, "body", (0, y, 6.0), (w, 1.6, 0.6), W)                                      # the bib hangs in tufts
    # big woolly shoulders, dark forearms in copper bracers, heavy fists
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 9.8
        part(m, arm, (x, 25.2, 0), (6.4, 5.4, 6.4), W, dark=W2, band=0.25)
        bx(m, arm, (x + sd * 0.4, 18.6, 0.4), (3.8, 8.4, 3.8), SKIN)
        part(m, arm, (x + sd * 0.4, 15.6, 0.4), (4.6, 3.4, 4.6), COP, dark="cut_copper", band=0.3)
        paint(m, arm, "f", (x + sd * 0.4, 15.9, 2.7), ["k.k"], {"k": "oxidized_copper"}, 0.9)
        part(m, arm, (x + sd * 0.6, 11.4, 0.8), (4.6, 4.0, 4.6), SKIN, dark="gray_terracotta", band=0.2)
    # the head: a long grey face, glowing eyes, a pale muzzle, wool cap and forelock, curled horns
    part(m, "head", (0, 31.6, 2.6), (7.4, 7.0, 7.4), SKIN)
    for sd in (1, -1):
        litbox(m, "head", (sd * 2.3, 32.6, 6.36), (1.8, 1.0, 0.1), "yellow_concrete")
        bx(m, "head", (sd * 2.3, 32.6, 6.44), (1.2, 0.3, 0.1), "black_concrete")
        bx(m, "head", (sd * 4.5, 31.6, 3.0), (2.8, 1.0, 1.6), SKIN, rot=(0, 0, -20 * sd), origin=(sd * 3.7, 31.6, 3.0))
    part(m, "head", (0, 29.8, 7.4), (4.8, 3.8, 3.6), SKIN_L, light="white_concrete")
    bx(m, "head", (0, 30.8, 9.26), (2.4, 1.0, 0.1), "black_terracotta")
    part(m, "head", (0, 35.6, 2.2), (8.2, 2.0, 8.2), W, dark=W2, band=0.4)
    bx(m, "head", (0, 34.6, 6.5), (4.6, 1.6, 1.0), W)
    import math
    for sd in (1, -1):
        for k, th in enumerate((60, 95, 130, 165, 200, 235, 270, 305, 335)):
            a, r = math.radians(th), 3.4 - k * 0.18
            y, z = 32.2 + 3.8 * math.sin(a), -0.8 + 3.8 * math.cos(a)
            bx(m, "head", (sd * (4.9 + k * 0.28), y, z), (2 * r * 0.9, 2 * r * 0.8, 2 * r * 0.8), HORN if k % 2 else HORN_D,
               rot=(90 - th, 0, 0), origin=(sd * (4.9 + k * 0.28), y, z))
    # the jaw with a wool goatee
    bx(m, "jaw", (0, 27.6, 7.0), (4.4, 1.2, 3.4), SKIN_L)
    part(m, "jaw", (0, 25.8, 8.0), (2.4, 2.8, 1.6), W)
    # the storm cloud on his shoulders, bolts hanging down his back
    for (x, y, z), (w, h, d), b in (((-6.6, 31.0, -2.8), (6.0, 3.6, 5.6), W2), ((6.6, 31.0, -2.8), (6.0, 3.6, 5.6), W2),
                                    ((0, 33.4, -5.8), (11.0, 4.6, 5.4), "gray_wool"), ((-3.6, 36.4, -5.6), (5.0, 2.8, 4.2), W2),
                                    ((3.8, 36.8, -4.8), (4.6, 3.4, 4.0), W2), ((0, 38.4, -6.4), (3.6, 2.2, 3.0), "gray_wool")):
        part(m, "cloud", (x, y, z), (w, h, d), b, dark="gray_concrete", band=0.25)
    for x, z in ((-4.6, -8.7), (4.8, -8.7), (0, -8.7)):
        for dx, y, h, a in ((0, 29.0, 3.4, 25), (0.9, 26.2, 3.0, -25), (0.3, 23.8, 2.2, 25)):
            bx(m, "cloud", (x + dx, y, z), (0.8, h, 0.8), "yellow_concrete", rot=(0, 0, a), origin=(x + dx, y, z)); lit(m)
    # the copper rod: a long shaft, green bands, a forked head and a crackling tip
    bx(m, "rod", (-10.8, 13.6, 1.2), (1.1, 23.0, 1.1), "cut_copper")
    for y in (8.6, 18.2, 22.4):
        bx(m, "rod", (-10.8, y, 1.2), (1.7, 0.8, 1.7), "oxidized_copper")
    for sd in (1, -1):
        bx(m, "rod", (-10.8 + sd * 1.0, 26.0, 1.2), (0.7, 2.8, 0.7), "cut_copper", rot=(0, 0, -16 * sd), origin=(-10.8, 24.8, 1.2))
    litbox(m, "rod", (-10.8, 26.8, 1.2), (0.8, 1.6, 0.8), "yellow_concrete")
    standard_anims(m, heavy=1.2, extra={"idle": idle_biped(4.0, 14, breath=0.04, extra={
        "cloud": {"rot": wave(1, 6, 4.0), "pos": wave(1, 0.6, 4.0, 0.25)}, "jaw": {"rot": wave(0, 4, 2.0)}})})
    moves(m, dict(length=1.2, swing=22, arm=18, bob=1.0, sway=5), body=4,
          call=attack(1.6, 1.0, {"armR": {"rot": K((0, Z), (0.5, (-60, 0, -10)), (0.85, (-172, 0, 6)), (1.25, (-168, 0, 6)), (1.6, Z))},
                                 "armL": {"rot": K((0, Z), (0.5, (-20, 0, 30)), (0.85, (-30, 0, 55)), (1.25, (-28, 0, 50)), (1.6, Z))},
                                 "body": {"rot": K((0, Z), (0.5, (8, 0, 0)), (0.85, (-16, 0, 0)), (1.25, (-14, 0, 0)), (1.6, Z))},
                                 "head": {"rot": K((0, Z), (0.5, (10, 0, 0)), (0.85, (-30, 0, 0)), (1.25, (-26, 0, 0)), (1.6, Z))},
                                 "jaw": {"rot": K((0, Z), (0.85, (30, 0, 0)), (1.25, (26, 0, 0)), (1.6, Z))},
                                 "cloud": {"scl": K((0, (1, 1, 1)), (0.85, (1.25, 1.15, 1.25)), (1.0, (1.45, 1.3, 1.45)), (1.25, (1.35, 1.2, 1.35)), (1.6, (1, 1, 1)))}}))
    m.attacks = {"lightning": "call", "charge": "lunge", "shockwave": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ Old Jangles

@mob("keywarden")
def keywarden():
    """Old Jangles, Keeper of the Five Keys: a stout clockwork vault guardian. A brass boiler body in copper bands
    with rivets, a lock plate with a glowing keyhole and a pressure gauge, two smokestacks on its back, a brass
    head with two glowing amber lenses, a grille mouth and a glass dome with a lit gear inside, piston arms with
    brass gauntlets, a round lock shield, a ring of five keys jangling at its belt and a big wind-up key turning
    in its back."""
    from v14_kit import humanoid
    m = Model("keywarden", "biped", 1.7)
    BR, BR_D, BR_L, COP, IR, DK = "gold_block", "yellow_terracotta", "yellow_concrete", "copper_block", "iron_block", "gray_concrete"
    humanoid(m, hip=13, legx=5, neck=33, shoulder=31, armx=11.6)
    m.bone("key", "body", (0, 26, -6))
    m.bone("keys", "hips", (3.6, 13.2, 4.8))
    m.bend = -24
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 5
        part(m, leg, (x, 11.2, 0), (4.6, 3.2, 4.6), COP)
        bx(m, leg, (x, 7.8, 0.2), (2.0, 4.6, 2.0), IR)
        part(m, leg, (x, 5.0, 0.5), (4.4, 3.2, 4.4), BR, dark=BR_D, band=0.3)
        part(m, leg, (x, 1.4, 1.2), (5.4, 2.8, 7.0), BR, dark=BR_D, band=0.35)
        bx(m, leg, (x, 1.3, 4.8), (4.6, 1.8, 0.6), IR)
    bx(m, "hips", (0, 14.2, 0), (11.4, 2.6, 7.6), DK)
    # the boiler: a brass barrel with copper bands and rivets
    part(m, "body", (0, 23.4, 0), (14.6, 15.4, 10.6), BR, dark=BR_D, band=0.15)
    part(m, "body", (0, 31.4, 0), (12.4, 1.6, 8.8), BR_D)
    for y in (18.2, 28.6):
        bx(m, "body", (0, y, 0), (15.0, 1.4, 11.0), COP)
        paint(m, "body", "f", (0, y, 5.5), ["k.k.k.k.k"], {"k": IR}, 0.8)
    paint(m, "body", "f", (-4.6, 23.6, 5.3), ["l", "l", "l", "."], {"l": BR_L}, 0.9)      # a shine down the side
    # the lock plate with a glowing keyhole, and a pressure gauge
    bx(m, "body", (0, 23.4, 5.6), (6.0, 6.4, 0.6), IR)
    paint(m, "body", "f", (0, 23.6, 5.9), ["..kk..", ".kook.", ".kook.", "..kk..", "..kk..", ".kkkk."], {"k": "black_concrete", "o": "orange_concrete"}, 0.8)
    for c in m.cubes[-6:]:
        if c["k"] == "orange_concrete": c["l"] = True
    bx(m, "body", (5.0, 26.6, 5.5), (2.6, 2.6, 0.4), "white_concrete")
    bx(m, "body", (5.1, 26.8, 5.76), (0.3, 1.2, 0.1), "red_concrete", rot=(0, 0, -40), origin=(5.1, 26.6, 5.76))
    # two smokestacks on the back
    for sd in (1, -1):
        bx(m, "body", (sd * 4.0, 33.4, -3.4), (2.4, 5.4, 2.4), DK)
        bx(m, "body", (sd * 4.0, 36.4, -3.4), (3.2, 0.8, 3.2), "black_concrete")
    # five keys on an iron hoop at the belt
    bx(m, "keys", (3.6, 13.2, 4.8), (2.4, 0.4, 2.4), IR)
    for i, b in enumerate(("gold_block", IR, COP, "emerald_block", "diamond_block")):
        x0, a = 3.6 + (i - 2) * 0.6, (i - 2) * 12
        o = (x0, 13.0, 5.4)
        bx(m, "keys", (x0, 12.0, 5.4), (1.3, 1.3, 0.4), b, rot=(0, 0, a), origin=o)
        bx(m, "keys", (x0, 9.9, 5.4), (0.5, 3.2, 0.4), b, rot=(0, 0, a), origin=o)
        bx(m, "keys", (x0 + 0.5, 8.8, 5.4), (0.8, 0.6, 0.4), b, rot=(0, 0, a), origin=o)
    # arms: copper shoulder joints, iron pistons, brass gauntlets, iron fingers
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 11.6
        part(m, arm, (x, 31.0, 0), (5.2, 5.0, 5.2), COP, light="cut_copper")
        bx(m, arm, (x, 25.8, 0.2), (2.0, 6.6, 2.0), DK)
        bx(m, arm, (x, 26.8, 0.2), (2.8, 2.4, 2.8), IR)
        part(m, arm, (x, 19.0, 0.8), (6.0, 7.0, 6.0), BR, dark=BR_D, band=0.2)
        bx(m, arm, (x, 16.2, 0.8), (6.4, 1.0, 6.4), COP)
        for t in (-1.4, 0, 1.4):
            bx(m, arm, (x + t, 14.0, 2.0), (1.1, 2.6, 1.1), IR)
    # the round lock shield on the left arm
    bx(m, "armL", (15.4, 19.0, 0.8), (0.9, 8.6, 8.6), IR)
    bx(m, "armL", (15.4, 19.0, 0.8), (0.9, 8.6, 8.6), IR, rot=(45, 0, 0), origin=(15.4, 19.0, 0.8))
    bx(m, "armL", (16.0, 19.0, 0.8), (0.6, 3.6, 3.6), "gold_block", rot=(45, 0, 0), origin=(16.0, 19.0, 0.8))
    bx(m, "armL", (16.4, 19.4, 0.8), (0.2, 1.2, 1.2), "black_concrete")
    bx(m, "armL", (16.4, 18.3, 0.8), (0.2, 1.4, 0.5), "black_concrete")
    # the head: copper collar, brass face with amber lenses and a grille, a glass dome with a lit gear
    bx(m, "head", (0, 33.8, 0.2), (8.4, 1.6, 8.0), COP)
    part(m, "head", (0, 36.6, 0.4), (8.4, 4.6, 7.4), BR, dark=BR_D, band=0.2)
    for sd in (1, -1):
        bx(m, "head", (sd * 1.9, 37.2, 4.3), (2.4, 2.4, 0.4), IR)
        litbox(m, "head", (sd * 1.9, 37.2, 4.56), (1.4, 1.4, 0.1), "orange_concrete")
        bx(m, "head", (sd * 4.4, 36.6, 0.4), (0.6, 2.0, 2.0), COP)
    bx(m, "head", (0, 35.0, 4.2), (3.4, 1.0, 0.2), "black_concrete")
    for x in (-0.9, 0, 0.9):
        bx(m, "head", (x, 35.0, 4.35), (0.3, 1.0, 0.1), IR)
    bx(m, "head", (0, 40.6, 0.4), (6.0, 3.4, 6.0), "white_stained_glass")
    for a in (0, 45):
        bx(m, "head", (0, 40.6, 0.4), (2.6, 2.6, 0.6), "orange_concrete", rot=(0, 0, a), origin=(0, 40.6, 0.4)); lit(m)
    litbox(m, "head", (0, 40.6, 0.4), (1.0, 1.0, 0.9), "yellow_concrete")
    bx(m, "head", (0, 42.6, 0.4), (3.0, 0.6, 3.0), "gold_block")
    litbox(m, "head", (0, 43.4, 0.4), (1.2, 1.2, 1.2), "redstone_lamp")
    # the wind-up key in the back
    bx(m, "key", (0, 26, -7.0), (1.2, 1.2, 4.4), DK)
    for sd in (1, -1):
        part(m, "key", (sd * 2.6, 26, -9.6), (4.0, 4.6, 0.8), "gold_block", dark=BR_D, band=0.3)
        bx(m, "key", (sd * 2.8, 26, -9.6), (2.0, 2.6, 1.0), COP)
    bx(m, "key", (0, 26, -9.6), (1.6, 1.6, 1.0), COP)
    turn = K(*[(t, (0, 0, 90 * t)) for t in range(5)])
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(4.0, 12, breath=0.02, extra={"key": {"rot": turn}, "keys": {"rot": wave(0, 12, 2.0)}})})
    piston = lambda d: K((0, Z), *[(0.2 + 0.3 * k + d, (-70 if k % 2 else -10, 0, 0)) for k in range(4)], (1.6, Z))
    moves(m, dict(length=1.0, swing=20, arm=26, bob=0.4, sway=0),
          wind=attack(1.6, 1.0, {"key": {"rot": K((0, Z), (1.3, (0, 0, 1080)), (1.6, (0, 0, 1080)))},
                                 "armL": {"rot": piston(0)}, "armR": {"rot": piston(0.15)},
                                 "head": {"rot": K((0, Z), (0.9, Z), (1.2, (0, 180, 0)), (1.4, (0, 360, 0)), (1.6, (0, 360, 0)))},
                                 "body": {"rot": K(*[(0.1 * k, (0, 0, (2 if k % 2 else -2) if 0 < k < 16 else 0)) for k in range(17)])}}))
    m.attacks = {"slam": "slam", "charge": "sweep", "minions": "wind", "darkness": "roar"}
    m.melee = "swipe"
    return m


def glow_last(m, n, blocks):
    """Lights the last n cubes whose block is in blocks (painted fire, glowing eyes)."""
    for c in m.cubes[-n:]:
        if c["k"] in blocks: c["l"] = True


# ------------------------------------------------------------------------------------------------ Sunny

@mob("sunscorch")
def sunscorch():
    """Sunny, a little sun on its summer holiday: a cube of orange sun with a glowing yellow top that melts down
    its sides in drips, a crown of flame rays, big pink heart sunglasses, a wide grin with its tongue out and a
    yellow duck swim ring round its middle."""
    import v14_studio
    m = Model("sunscorch", "slime", 1.6)
    for b, p, at in (("body", "root", (0, 0, 0)), ("inner", "body", (0, 10, 0)), ("mouth", "body", (0, 9, 9)), ("ring", "body", (0, 6, 0)), ("rays", "body", (0, 21, 0))):
        m.bone(b, p, at)
    OR, OR_D, YE = "orange_concrete", "orange_terracotta", "yellow_concrete"
    litbox(m, "inner", (0, 10.5, 0), (9.0, 9.0, 9.0), "shroomlight")                        # the white-hot core, seen when it bursts
    part(m, "body", (0, 9.6, 0), (18.0, 19.2, 18.0), OR, dark=OR_D, band=0.1)
    litbox(m, "body", (0, 17.6, 0), (18.3, 3.6, 18.3), YE)
    for x, z, h in ((-6.0, 9.15, 3.6), (-1.6, 9.15, 2.0), (6.6, 9.15, 4.4), (9.15, -5.0, 5.2), (9.15, 2.4, 2.6), (-9.15, 4.6, 4.8), (-9.15, -3.4, 2.2), (2.0, -9.15, 4.0), (-5.0, -9.15, 2.8)):
        w = (1.4, h, 0.2) if abs(z) > 9 else (0.2, h, 1.4)
        litbox(m, "body", (x, 15.8 - h / 2, z), w, YE)
    litbox(m, "body", (-6.4, 18.4, 9.26), (2.4, 0.8, 0.1), "white_concrete")                     # a shine
    # heart sunglasses
    paint(m, "body", "f", (0, 12.8, 9.0), [".pp.pp...pp.pp.", "pmmpmmp.pmmpmmp", "pmwmmmpppmwmmmp", "pmmmmmp.pmmmmmp", ".pmmmp...pmmmp.", "..pmp.....pmp..", "...p.......p..."],
          {"p": "pink_concrete", "m": "magenta_concrete", "w": "white_concrete"}, 0.9, d=0.3)
    for sd in (1, -1):
        bx(m, "body", (sd * 9.12, 14.6, 4.4), (0.2, 0.8, 9.0), "pink_concrete")
    # the grin with teeth and the tongue sticking out
    paint(m, "mouth", "f", (0, 6.0, 9.0), [".kkkkkkkkkkk.", "kwwkwwkwwkwwk", "kkkkkkkkkkkkk", ".kkkrrrrrkkk.", "...krrrrrk..."], {"k": "black_concrete", "w": "white_concrete", "r": "red_concrete"}, 0.9)
    part(m, "mouth", (0, 3.8, 9.8), (3.2, 2.6, 1.4), "red_concrete", light="pink_concrete")
    bx(m, "mouth", (0, 3.6, 10.56), (0.4, 1.8, 0.1), "pink_concrete")
    # the crown of flame rays
    import math
    for k in range(8):
        a = k * math.pi / 4
        x, z = math.cos(a) * 6.2, math.sin(a) * 6.2
        tall = 5.5 if k % 2 == 0 else 3.8
        litbox(m, "rays", (x, 21 + tall / 2, z), (2.6, tall, 2.6), YE)
        litbox(m, "rays", (x, 21 + tall + 0.8, z), (1.4, 1.8, 1.4), OR)
    # the duck swim ring, white stripes and a duck head at the front
    for c, s in (((0, 2.6, -10.6), (24.0, 3.4, 3.2)), ((0, 2.6, 10.6), (24.0, 3.4, 3.2)), ((-10.6, 2.6, 0), (3.2, 3.4, 18.0)), ((10.6, 2.6, 0), (3.2, 3.4, 18.0))):
        part(m, "ring", c, s, YE, dark="yellow_terracotta", band=0.25)
    for x, z in ((-12.26, -4.6), (-12.26, 4.6), (12.26, -4.6), (12.26, 4.6)):
        bx(m, "ring", (x, 2.6, z), (0.1, 3.4, 2.0), "white_concrete")
    part(m, "ring", (8.4, 6.0, 12.0), (4.4, 4.4, 4.0), YE)
    part(m, "ring", (8.4, 5.4, 14.8), (2.6, 1.2, 1.8), OR)
    paint(m, "ring", "f", (8.4, 6.8, 14.0), ["k..k"], {"k": "black_concrete"}, 0.8)
    m.anims = v14_studio.sunscorch().anims
    m.attacks = {"leap": "slam", "quake": "hop", "fire_ring": "burst", "volley": "spit"}
    m.melee = "hop"
    return m


# ------------------------------------------------------------------------------------------------ Granny Morwen

@mob("hexmother")
def hexmother():
    """Granny Morwen, the swamp witch: a hunched crone with green skin, a long hooked nose with a wart, mean
    yellow eyes under heavy brows, a crooked grin with one tooth and wild grey hair, a huge black hat with a
    purple band, a gold buckle and a spider web, a ragged purple dress with a black shawl, striped stockings
    and pointed boots, glowing potion bottles on her belt, a black cat on her shoulder, and a gnarled staff
    topped with a skull and green fire."""
    from v14_kit import humanoid
    m = Model("hexmother", "biped", 1.8)
    humanoid(m, hip=13, legx=3, neck=31, shoulder=28.6, armx=7.4, jaw=(0, 32, 4))
    m.bone("hat", "head", (0, 39.6, 0.4))
    m.bone("staff", "armR", (-8.6, 11, 2))
    m.bone("cat", "body", (7.6, 29.4, -1))
    m.hold = {"staff": 0}
    SKIN, SKIN_D, HAIR, HAIR_D = "lime_terracotta", "green_terracotta", "light_gray_wool", "gray_wool"
    DRESS, DRESS_D, HAT = "purple_wool", "purple_terracotta", "black_wool"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3
        bx(m, leg, (x, 6.6, 0), (2.2, 6.4, 2.2), "black_wool")
        for y in (4.6, 6.6, 8.6):
            bx(m, leg, (x, y, 0), (2.4, 0.8, 2.4), DRESS)
        part(m, leg, (x, 1.2, 0.8), (3.0, 2.4, 4.4), "black_terracotta")
        bx(m, leg, (x, 2.4, 3.4), (1.4, 1.2, 1.4), "black_terracotta", rot=(-30, 0, 0), origin=(x, 1.8, 3.0))
    # the ragged dress, a patch, the belt with potions
    part(m, "hips", (0, 12.0, 0), (11.6, 5.0, 8.6), DRESS, dark=DRESS_D, band=0.3)
    for i, x in enumerate((-4.6, -2.3, 0, 2.3, 4.6)):
        for z in (4.0, -4.0):
            bx(m, "hips", (x, 8.6 - (i + (z > 0)) % 2 * 0.8, z), (2.3, 1.8 + (i + (z > 0)) % 2 * 1.6, 0.6), DRESS_D)
    bx(m, "hips", (3.2, 11.0, 4.36), (2.0, 2.0, 0.1), "magenta_terracotta")
    part(m, "body", (0, 20.6, 0), (10.0, 10.0, 7.0), DRESS, dark=DRESS_D, band=0.15)
    bx(m, "body", (0, 15.4, 0), (10.4, 1.2, 7.4), "black_terracotta")
    for x, glass, core in ((-3.6, "lime_stained_glass", "lime_concrete"), (-1.4, "magenta_stained_glass", "magenta_concrete"), (3.4, "light_blue_stained_glass", "light_blue_concrete")):
        bx(m, "body", (x, 14.0, 4.0), (1.6, 2.0, 1.2), glass)
        litbox(m, "body", (x, 13.8, 4.0), (1.0, 1.2, 0.8), core)
        bx(m, "body", (x, 15.3, 4.0), (0.8, 0.8, 0.8), "brown_terracotta")
    part(m, "body", (0, 25.6, 0), (11.0, 2.6, 7.6), "black_wool")
    paint(m, "body", "f", (0, 24.0, 3.8), ["k.k.k.k.k.k", "k...k...k.."], {"k": "black_wool"}, 1.0)
    # thin arms in long sleeves, ragged cuffs, green hands with long fingers
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 7.4
        part(m, arm, (x, 23.0, 0), (3.4, 10.0, 3.6), DRESS, dark=DRESS_D, band=0.15)
        bx(m, arm, (x, 17.6, 0.4), (2.0, 2.6, 2.0), SKIN)
        for t in (-0.6, 0.6):
            bx(m, arm, (x + t, 15.6, 0.8), (0.5, 2.0, 0.5), SKIN_D)
    # the head: green skin, wild grey hair, mean yellow eyes, a hooked nose with a wart
    part(m, "head", (0, 35.0, 1.0), (7.6, 6.4, 7.0), SKIN)
    paint(m, "head", "f", (0, 36.0, 4.5), ["kk...kk", "yk...ky", ".......", "d.....d"], {"k": "black_concrete", "y": "yellow_concrete", "d": SKIN_D}, 0.9)
    glow_last(m, 8, {"yellow_concrete"})
    bx(m, "head", (0, 35.4, 5.7), (1.6, 1.6, 2.4), SKIN)
    bx(m, "head", (0, 34.2, 7.0), (1.4, 2.0, 1.4), SKIN, rot=(20, 0, 0), origin=(0, 35.0, 6.6))
    bx(m, "head", (0.8, 35.6, 6.4), (0.6, 0.6, 0.6), SKIN_D)
    for sd in (1, -1):
        part(m, "head", (sd * 4.3, 35.2, 0.2), (1.6, 6.4, 6.6), HAIR, dark=HAIR_D, band=0.3)
        bx(m, "head", (sd * 5.0, 33.2, -0.6), (1.8, 4.0, 2.0), HAIR, rot=(0, 0, 24 * sd), origin=(sd * 4.6, 35.0, -0.6))
        bx(m, "head", (sd * 5.6, 37.6, 1.0), (2.0, 1.0, 1.6), HAIR_D, rot=(0, 0, -30 * sd), origin=(sd * 4.6, 37.6, 1.0))
    part(m, "head", (0, 34.4, -2.9), (8.0, 8.0, 1.6), HAIR, dark=HAIR_D, band=0.3)
    bx(m, "head", (0, 30.0, -2.6), (6.0, 2.4, 1.2), HAIR)
    # the jaw: a pointed chin and a crooked grin with one tooth
    part(m, "jaw", (0, 31.4, 1.6), (6.4, 1.6, 6.2), SKIN)
    bx(m, "jaw", (0, 30.4, 4.2), (2.0, 1.2, 1.4), SKIN)
    paint(m, "jaw", "f", (0, 32.0, 4.7), ["k.....k", ".kkwkk."], {"k": "black_concrete", "w": "white_concrete"}, 0.7)
    # the hat: a wide brim, a tall bent cone, a purple band with a gold buckle, a spider web on the side
    part(m, "hat", (0, 39.6, 0.4), (13.0, 0.8, 12.0), HAT)
    bx(m, "hat", (0, 38.8, 0.8), (7.2, 1.4, 6.6), HAT)          # the crown sits down on her head
    cone = ((0, 41.4, 0.2, 7.6, 2.8, 7.2), (0.4, 44.0, -0.4, 6.0, 2.6, 5.8), (1.2, 46.4, -1.4, 4.4, 2.4, 4.2), (2.4, 48.4, -2.8, 3.0, 1.8, 3.0), (3.8, 49.6, -4.4, 1.8, 1.4, 1.8))
    for x, y, z, w, h, d in cone:
        part(m, "hat", (x, y, z), (w, h, d), HAT)
    bx(m, "hat", (0, 40.8, 0.2), (7.8, 1.2, 7.4), DRESS)
    bx(m, "hat", (0, 40.8, 3.95), (1.8, 1.4, 0.2), "gold_block")
    paint(m, "hat", "l", (3.8, 42.0, 0.2), ["w...w", ".w.w.", "wwwww", ".w.w.", "w...w"], {"w": "white_concrete"}, 0.45, d=0.06)
    # the black cat on her shoulder
    part(m, "cat", (7.6, 29.6, -1.2), (3.0, 2.4, 4.4), "black_wool")
    part(m, "cat", (7.6, 31.4, 1.6), (3.0, 2.6, 2.6), "black_wool")
    for sd in (1, -1):
        bx(m, "cat", (7.6 + sd * 0.9, 33.1, 1.6), (0.8, 1.0, 0.8), "black_wool")
        litbox(m, "cat", (7.6 + sd * 0.7, 31.7, 2.96), (0.6, 0.5, 0.1), "yellow_concrete")
    for y, z in ((30.4, -3.8), (32.2, -4.4), (33.8, -3.8)):
        bx(m, "cat", (7.6, y, z), (0.7, 2.0, 0.7), "black_wool", rot=(-20, 0, 0), origin=(7.6, y, z))
    # the gnarled staff, a skull on top and green fire
    for y, dx, h in ((6.0, 0, 9), (14.0, 0.4, 7), (20.6, -0.2, 6), (25.4, 0.2, 4)):
        bx(m, "staff", (-8.6 + dx, y, 2), (1.3, h, 1.3), "dark_oak_log")
    bx(m, "staff", (-8.6, 13.2, 2), (1.8, 1.0, 1.8), "dark_oak_log")
    part(m, "staff", (-8.6, 28.6, 2), (2.8, 2.6, 2.6), "calcite")
    paint(m, "staff", "f", (-8.6, 28.8, 3.3), ["k.k", "...", ".k."], {"k": "black_concrete"}, 0.7)
    litbox(m, "staff", (-8.6, 31.0, 2), (2.0, 1.6, 2.0), "lime_concrete")
    litbox(m, "staff", (-8.4, 32.4, 2), (1.2, 1.6, 1.2), "lime_stained_glass")
    m.bend = -50
    standard_anims(m, heavy=0.9, extra={"idle": idle_biped(4.0, 18, breath=0.03, extra={
        "hat": {"rot": wave(2, 4, 4.0)}, "jaw": {"rot": wave(0, 5, 2.0)}, "cat": {"rot": wave(1, 12, 4.0, 0.3)}})})
    moves(m, dict(length=1.0, swing=16, arm=8, bob=0.5, sway=6), body=10,
          hex=attack(1.6, 0.95, {"armR": {"rot": K((0, Z), (0.6, (-150, 0, -10)), (0.8, (-165, 0, -12)), (0.95, (-100, 0, -4)), (1.3, (-95, 0, -4)), (1.6, Z))},
                                 "armL": {"rot": K((0, Z), (0.6, (-40, 0, 20)), (0.95, (-95, 0, -4)), (1.3, (-90, 0, -4)), (1.6, Z))},
                                 "foreL": {"rot": K((0, Z), (0.6, (-60, 0, 0)), (0.95, (-5, 0, 0)), (1.6, Z))},
                                 "body": {"rot": K((0, Z), (0.6, (-12, 10, 0)), (0.95, (14, -6, 0)), (1.3, (12, -6, 0)), (1.6, Z))},
                                 "head": {"rot": K((0, Z), (0.6, (-15, 0, 0)), (0.95, (8, 0, 0)), (1.6, Z))},
                                 "jaw": {"rot": K((0, Z), (0.6, (6, 0, 0)), (0.95, (26, 0, 0)), (1.3, (22, 0, 0)), (1.6, Z))},
                                 "hat": {"rot": K((0, Z), (0.6, (-15, 0, 6)), (0.95, (12, 0, -4)), (1.25, (-4, 0, 2)), (1.6, Z))},
                                 "cat": {"rot": K((0, Z), (0.8, (-12, 0, 0)), (0.95, (8, 0, 0)), (1.6, Z))}}))
    m.attacks = {"hex": "hex", "potions": "double", "minions": "roar", "blink": "cast"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ The Headless Horseman

@mob("headless_horseman")
def headless_horseman():
    """The Headless Horseman on his nightmare horse. The horse is black with a bone mask, ribs showing on its
    chest, glowing eyes and nostrils, a mane and tail of fire and burning hooves, under a purple caparison with
    orange trim and a black saddle. The rider wears a dark coat with gold buttons, a ruffled white collar and a
    tattered cape; flames rise from his neck, he holds his carved, glowing jack-o'-lantern head up high in one
    hand and points a long sabre with the other."""
    m = Model("headless_horseman", "quad", 1.8)
    m.bone("body", "root", (0, 21, 0))
    for n, x, z in (("legFL", 3.6, 8.6), ("legFR", -3.6, 8.6), ("legBL", 3.6, -9.4), ("legBR", -3.6, -9.4)):
        m.bone(n, "body", (x, 21, z))
    m.bone("head", "body", (0, 30, 11)); m.bone("jaw", "head", (0, 30, 16))
    m.bone("tail", "body", (0, 26, -12)); m.bone("rider", "body", (0, 30, -1))
    m.bone("riderArmR", "rider", (-4.6, 40.4, -1)); m.bone("riderArmL", "rider", (4.6, 40.4, -1))
    HB, HB_L, BONE, FIRE, FIRE2 = "black_concrete", "gray_concrete", "calcite", "orange_concrete", "yellow_concrete"
    CAP, TRIM, COAT, COAT_D = "purple_wool", "orange_concrete", "blue_terracotta", "black_wool"
    # the horse: body, ribs on the chest, the caparison and saddle
    part(m, "body", (0, 24.8, -0.4), (9.6, 8.4, 22.0), HB)
    for sd in (1, -1):
        paint(m, "body", "l" if sd == 1 else "r", (sd * 4.8, 25.2, 6.6), ["w.w.w", "w.w.w", "....."], {"w": BONE}, 1.0)
    part(m, "body", (0, 26.0, -3.0), (10.4, 6.2, 13.0), CAP)
    bx(m, "body", (0, 23.2, -3.0), (10.6, 1.0, 13.2), TRIM)
    for sd in (1, -1):
        for z in (-7.6, -3.0, 1.6):
            bx(m, "body", (sd * 5.3, 22.2, z), (0.2, 1.4, 1.8), TRIM)
    part(m, "body", (0, 29.4, -1.0), (8.4, 1.2, 6.4), "black_terracotta")
    # the neck with a fiery mane
    bx(m, "body", (0, 30.0, 9.2), (4.8, 9.0, 5.4), HB, rot=(-28, 0, 0), origin=(0, 26, 8))
    for y, z, h in ((33.6, 7.6, 3.0), (31.2, 6.0, 2.6), (28.8, 4.6, 2.2)):
        litbox(m, "body", (0, y, z), (1.6, h, 2.2), FIRE)
        litbox(m, "body", (0, y + h / 2 + 0.6, z - 0.4), (1.0, 1.4, 1.2), FIRE2)
    # legs: black, with burning hooves
    for n, x, z in (("legFL", 3.6, 8.6), ("legFR", -3.6, 8.6), ("legBL", 3.6, -9.4), ("legBR", -3.6, -9.4)):
        part(m, n, (x, 17.0, z), (3.6, 7.4, 4.2), HB)
        bx(m, n, (x, 8.6, z), (2.8, 10.0, 3.0), HB)
        litbox(m, n, (x, 1.6, z + 0.3), (3.0, 3.2, 3.4), FIRE)
        litbox(m, n, (x, 3.8, z + 0.3), (2.6, 1.2, 2.8), FIRE2)
    # the head: long and black, a bone mask with glowing eye holes, fire nostrils, ears
    part(m, "head", (0, 34.0, 13.4), (5.2, 5.6, 6.4), HB)
    part(m, "head", (0, 31.4, 18.2), (4.4, 3.8, 5.0), HB)
    bx(m, "head", (0, 34.4, 16.75), (5.4, 3.6, 0.3), BONE)
    bx(m, "head", (0, 33.4, 18.6), (4.6, 0.3, 4.2), BONE)
    for sd in (1, -1):
        bx(m, "head", (sd * 1.4, 35.0, 16.94), (1.4, 1.0, 0.1), "black_concrete")
        litbox(m, "head", (sd * 1.4, 34.9, 16.98), (0.6, 0.6, 0.1), FIRE)
        litbox(m, "head", (sd * 1.0, 31.8, 20.74), (0.8, 0.8, 0.1), FIRE)
        bx(m, "head", (sd * 1.6, 37.6, 12.6), (1.0, 2.0, 1.0), HB)
    litbox(m, "head", (0, 37.6, 11.0), (1.4, 2.6, 2.6), FIRE)
    part(m, "jaw", (0, 29.2, 18.0), (3.8, 1.0, 4.4), HB)
    # the fire tail
    bx(m, "tail", (0, 26.0, -12.0), (1.6, 1.6, 2.4), HB)
    litbox(m, "tail", (0, 24.0, -13.6), (2.2, 4.0, 2.2), FIRE)
    litbox(m, "tail", (0, 20.8, -14.4), (1.6, 3.2, 1.6), FIRE2)
    # the rider: legs astride, dark coat, ruffled collar, a cape and flames where his head should be
    for sd in (1, -1):
        bx(m, "rider", (sd * 3.6, 31.0, 0.4), (2.4, 2.4, 5.0), COAT_D)
        part(m, "rider", (sd * 5.4, 27.6, 2.2), (2.0, 6.0, 2.4), "black_terracotta")
        bx(m, "rider", (sd * 5.4, 24.4, 2.6), (2.2, 1.0, 3.0), "iron_block")
    part(m, "rider", (0, 36.6, -1.0), (7.0, 9.0, 4.4), COAT, dark=COAT_D, band=0.2)
    paint(m, "rider", "f", (0, 36.6, 1.2), ["g", ".", "g", ".", "g"], {"g": "gold_block"}, 0.8)
    part(m, "rider", (0, 41.8, -1.0), (5.8, 1.6, 4.4), "white_wool")
    paint(m, "rider", "f", (0, 41.4, 1.2), ["w.w.w.w"], {"w": "white_concrete"}, 0.8)
    litbox(m, "rider", (0, 43.6, -1.0), (3.0, 2.2, 2.6), FIRE)
    litbox(m, "rider", (0.2, 45.6, -1.0), (1.8, 2.0, 1.6), FIRE2)
    litbox(m, "rider", (-0.3, 47.2, -1.2), (1.0, 1.4, 1.0), FIRE)
    part(m, "rider", (0, 35.6, -3.8), (7.8, 11.0, 0.6), COAT_D, rot=(14, 0, 0), origin=(0, 41, -3.6))
    for i, x in enumerate((-3.0, -1.0, 1.0, 3.0)):
        bx(m, "rider", (x, 29.2 - (i % 2) * 0.8, -5.4), (1.8, 2.0 + (i % 2) * 1.6, 0.6), COAT_D, rot=(14, 0, 0), origin=(0, 41, -3.6))
    # his right hand points the sabre forward, his left holds his glowing pumpkin head high
    part(m, "riderArmR", (-4.6, 38.4, -0.6), (2.2, 4.6, 2.2), COAT)
    bx(m, "riderArmR", (-4.6, 36.4, 1.6), (2.0, 2.0, 4.0), COAT)
    bx(m, "riderArmR", (-4.6, 36.4, 4.2), (1.8, 1.8, 1.8), COAT_D)
    bx(m, "riderArmR", (-4.6, 36.6, 5.6), (2.6, 0.6, 0.6), "gold_block")
    bx(m, "riderArmR", (-4.6, 39.8, 11.2), (0.4, 1.4, 13.0), "iron_block", rot=(-22, 0, 0), origin=(-4.6, 36.6, 5.4))
    part(m, "riderArmL", (4.6, 43.2, -1.0), (2.2, 6.0, 2.2), COAT)
    bx(m, "riderArmL", (4.6, 46.8, -1.0), (1.8, 1.6, 1.8), COAT_D)
    part(m, "riderArmL", (4.6, 49.8, -1.0), (4.8, 4.4, 4.8), "orange_concrete", dark="orange_terracotta", band=0.2)
    bx(m, "riderArmL", (4.6, 52.4, -1.0), (1.0, 1.0, 1.0), "green_concrete")
    paint(m, "riderArmL", "f", (4.6, 50.0, 1.4), ["y...y", "yy.yy", ".....", "yyyyy", ".y.y."], {"y": FIRE2}, 0.8)
    glow_last(m, 8, {FIRE2})
    m.attacks = {"charge": "charge", "fire": "rear", "minions": "howl", "heads": "toss"}
    m.melee = "bite"
    return m


# ------------------------------------------------------------------------------------------------ Grandpa Pip

@mob("old_pip")
def old_pip():
    """Grandpa Pip, the gnome elder: a round little gnome under a tall red cap with a turned-up brim, its tip
    flopping down his back with a white bobble, bushy white brows over bright green eyes, rosy cheeks, a long
    drooping nose over a big white moustache and a pointed beard, a round teal tunic with a dark belt and a
    glowing emerald buckle, small hands and stubby boots with turned-up toes."""
    from v14_kit import humanoid
    m = Model("old_pip", "biped", 1.0)
    humanoid(m, hip=4, legx=2, neck=13, shoulder=12.5, armx=5.4)
    m.bone("hat", "head", (0, 19.5, 0.6)); m.bone("beard", "head", (0, 13.6, 4))
    SKIN, SKIN_D, W, TUN, TUN_D, RED, RED_D = "white_terracotta", "pink_terracotta", "white_wool", "cyan_concrete", "cyan_terracotta", "red_wool", "red_terracotta"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2
        bx(m, leg, (x, 3.0, 0), (2.0, 2.0, 2.0), "brown_wool")
        part(m, leg, (x, 0.9, 0.6), (2.6, 1.8, 3.6), "brown_terracotta")
        bx(m, leg, (x, 1.9, 2.7), (1.4, 1.2, 1.2), "brown_terracotta", rot=(-35, 0, 0), origin=(x, 1.4, 2.4))
    part(m, "body", (0, 8.6, 0.2), (9.4, 7.4, 7.6), TUN, dark=TUN_D, band=0.15)
    bx(m, "body", (0, 6.4, 0.2), (9.8, 1.0, 8.0), "black_terracotta")
    litbox(m, "body", (0, 6.4, 4.26), (1.4, 1.2, 0.2), "emerald_block")
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 5.4
        part(m, arm, (x, 10.6, 0), (2.4, 3.8, 2.4), TUN, dark=TUN_D, band=0.25)
        part(m, arm, (x, 8.0, 0.2), (2.0, 1.8, 2.0), SKIN, dark=SKIN_D, band=0.2)
    part(m, "head", (0, 15.8, 0.6), (7.4, 5.4, 6.6), SKIN)
    paint(m, "head", "f", (0, 16.8, 3.9), ["wwww.wwww", ".kgk.kgk.", "pp.....pp"], {"w": W, "k": "black_concrete", "g": "lime_concrete", "p": SKIN_D}, 0.75)
    bx(m, "head", (0, 15.4, 4.8), (1.8, 2.6, 2.2), SKIN)
    bx(m, "head", (0, 14.0, 5.6), (1.6, 1.4, 1.6), SKIN_D)
    for sd in (1, -1):
        bx(m, "head", (sd * 3.9, 15.8, 0.6), (0.6, 1.8, 1.4), SKIN)
        part(m, "head", (sd * 3.4, 15.4, -0.4), (1.2, 2.6, 4.4), W)
    part(m, "beard", (0, 13.6, 4.4), (6.4, 1.6, 1.8), W)
    for sd in (1, -1):
        bx(m, "beard", (sd * 3.2, 12.6, 4.4), (1.4, 2.0, 1.6), W)
    part(m, "beard", (0, 11.2, 4.4), (5.0, 3.4, 1.8), W)
    bx(m, "beard", (0, 8.8, 4.5), (3.2, 1.8, 1.6), W)
    bx(m, "beard", (0, 7.4, 4.5), (1.6, 1.2, 1.4), W)
    paint(m, "beard", "f", (0, 11.4, 5.3), ["g.g.g", ".g.g."], {"g": "white_concrete"}, 0.9)
    # the red cap: a turned-up brim, a tall crown, the tip flopping down the back with a bobble
    part(m, "hat", (0, 19.4, 0.6), (8.2, 1.6, 7.6), RED_D)
    for x, y, z, w, h, d in ((0, 21.4, 0.3, 7.0, 2.6, 6.6), (0, 23.6, -0.4, 5.6, 2.2, 5.2), (0, 25.4, -1.6, 4.2, 1.8, 4.0), (0, 26.4, -3.2, 3.0, 1.4, 3.0)):
        part(m, "hat", (x, y, z), (w, h, d), RED)
    bx(m, "hat", (0, 25.4, -4.8), (2.0, 2.4, 2.0), RED, rot=(30, 0, 0), origin=(0, 26.4, -4.4))
    bx(m, "hat", (0, 23.8, -5.4), (1.6, 1.6, 1.6), W)
    standard_anims(m, heavy=0.7, extra={"idle": idle_biped(3.2, 14, breath=0.04, extra={"hat": {"rot": wave(2, 4, 3.2)}, "beard": {"rot": wave(0, 4, 3.2, 0.2)}})})
    moves(m, dict(length=0.9, swing=28, arm=20, bob=0.7, sway=9), body=5)
    m.anims["walk"]["bones"]["beard"] = {"rot": wave(2, 8, 0.9)}
    m.attacks = {"volley": "cast", "blink": "stomp"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ Hedgey

@mob("sproutbeak")
def sproutbeak():
    """Hedgey, a hedge with legs: a round bush of moss and leaves with tufts sticking out and a few flowers in it,
    beady eyes on each side under leafy brows, a small orange beak, stubby leaf wings, a leather backpack strapped
    on with a gold buckle at the front, and two long thin orange legs with big flat three-toed feet."""
    from v14_kit import humanoid
    m = Model("sproutbeak", "biped", 1.0)
    humanoid(m, hip=10, legx=3, neck=14, shoulder=18, armx=8.2)
    LEAF, LEAF_D, LEAF_L, LEG = "moss_block", "green_concrete", "green_concrete_powder", "orange_terracotta"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3
        bx(m, leg, (x, 6.0, 0), (1.0, 8.6, 1.0), LEG)
        bx(m, leg, (x, 2.0, 0), (1.4, 1.2, 1.4), LEG)
        part(m, leg, (x, 0.4, 1.4), (3.6, 0.8, 4.4), LEG)
        paint(m, leg, "t", (x, 0.8, 1.4), ["k.k", "k.k", "..."], {"k": "brown_terracotta"}, 1.2, d=0.05)
    # the hedge: a big leafy cube with tufts sticking out and a few flowers
    part(m, "body", (0, 17.6, 0), (15.0, 13.0, 13.0), LEAF, dark=LEAF_D, band=0.15)
    for c, s in (((5.4, 24.6, 3.4), (3.2, 2.2, 3.2)), ((-4.6, 24.6, -2.4), (3.6, 2.4, 3.6)), ((0.4, 24.8, 0.6), (3.0, 2.6, 3.0)),
                 ((7.8, 19.4, -3.6), (1.6, 3.2, 3.2)), ((-7.8, 15.4, 2.6), (1.6, 3.0, 3.0)), ((-2.4, 21.4, -6.8), (3.6, 3.0, 1.6)),
                 ((3.6, 13.6, -6.8), (3.0, 2.6, 1.6)), ((-5.4, 12.0, 4.6), (2.6, 2.2, 3.0))):
        part(m, "body", c, s, LEAF_L if c[1] > 20 else LEAF)
    for x, y, z in ((-4.2, 15.6, 6.56), (4.4, 16.2, 6.56), (-7.56, 21.2, -3.0)):
        f = "f" if z > 6 else "r"
        paint(m, "body", f, (x, y, z), [".p.", "pyp", ".p."], {"p": "pink_concrete", "y": "yellow_concrete"}, 0.6)
    # the backpack, its straps and the buckle at the front
    part(m, "body", (0, 17.2, -8.0), (9.0, 9.0, 3.0), "brown_terracotta")
    bx(m, "body", (0, 20.6, -9.6), (9.2, 3.0, 0.4), "brown_concrete")
    bx(m, "body", (0, 19.6, -9.9), (1.4, 1.2, 0.2), "gold_block")
    for sd in (1, -1):
        bx(m, "body", (sd * 6.0, 17.6, 6.56), (1.2, 13.0, 0.1), "brown_concrete")
        bx(m, "body", (sd * 6.0, 24.16, 0), (1.2, 0.1, 13.0), "brown_concrete")
    bx(m, "body", (0, 13.2, 6.7), (13.0, 1.0, 0.2), "brown_concrete")
    bx(m, "body", (0, 13.2, 6.8), (1.8, 1.6, 0.2), "gold_block")
    # the face: beady eyes on each side under leafy brows, a small orange beak
    for sd in (1, -1):
        bx(m, "head", (sd * 3.0, 19.6, 6.56), (2.6, 2.6, 0.1), "white_concrete")
        bx(m, "head", (sd * 2.6, 19.4, 6.62), (1.4, 1.6, 0.1), "black_concrete")
        bx(m, "head", (sd * 3.0, 21.6, 6.8), (3.2, 0.8, 0.6), LEAF_D, rot=(0, 0, -12 * sd), origin=(sd * 3.0, 21.6, 6.8))
    part(m, "head", (0, 17.6, 7.4), (2.4, 1.6, 2.0), "orange_concrete", dark="orange_terracotta", band=0.4)
    # stubby leaf wings
    for sd, arm in ((1, "armL"), (-1, "armR")):
        part(m, arm, (sd * 8.2, 16.8, 0.4), (1.4, 5.0, 4.8), LEAF_D, light=LEAF_L)
        paint(m, arm, "l" if sd == 1 else "r", (sd * 8.9, 16.8, 0.4), ["..l..", ".l.l.", "l...l"], {"l": LEAF_L}, 0.9)
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(2.4, 18, breath=0.05)})
    moves(m, dict(length=0.6, swing=34, arm=0, bob=1.6, sway=4))
    flap = lambda sd: K(*[(0.075 * k, (0, 0, sd * (48 if k % 2 else 8))) for k in range(9)])
    m.anims["walk"]["bones"]["armL"], m.anims["walk"]["bones"]["armR"] = {"rot": flap(1)}, {"rot": flap(-1)}
    m.attacks = {"charge": "lunge"}
    m.melee = "swipe"
    return m


# Hoo, the little ghost, is retired: servers drop it from bosses.yml on the next start
import v12_final
v12_final.drop("boo_twin_b")
v12_final.REMOVED.append("boo_twin_b")
