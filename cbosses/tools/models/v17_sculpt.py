"""v17: sculpted models. The user wants bosses that look designed and natural, not stacks of cubes or pixel
skins: round bellies, tapered limbs, heavy brows, soft colour that blends from dark underneath to light on
top. Block displays are boxes, so every round form here is built from stacked slices whose cross-section is
a plus of two overlapping boxes (it reads as round from every side), and each slice takes the next tone of a
dark-to-light ramp of the same colour, so shading blends instead of jumping.

Helpers:
- blob(): an ellipsoid (or half of one) in slices; a belly, a head, a fist, a boot.
- taper(): a rounded limb or horn between two points, thick to thin, shaded along its length.
- ramp picks the tone for a height inside a form, so shapes share one light direction (from above)."""
import math
from build import Model
from v14_studio import studio
from v14_kit import humanoid, standard_anims, idle_biped, wave, wave2, K, Z, attack, loop


def sculpt(id):
    return studio(id, revise=False)


def tone(ramp, t):
    """t in 0..1 from bottom (dark) to top (light)."""
    t = min(0.999, max(0.0, t))
    return ramp[int(t * len(ramp))]


def slab(m, bone, cx, cy, cz, w, h, d, block, rot=None, origin=None, g=None):
    if w <= 0.05 or h <= 0.05 or d <= 0.05: return
    m.box(bone, block, (cx - w / 2, cy - h / 2, cz - d / 2), (cx + w / 2, cy + h / 2, cz + d / 2), rot, origin)
    if g: m.cubes[-1]["g"] = g


def ring(m, bone, cx, cy, cz, a, b, h, block, rot=None, origin=None, round_=0.62):
    """One rounded slice: a plus of two boxes, so the corners are cut and it reads round."""
    slab(m, bone, cx, cy, cz, 2 * a * 0.94, h, 2 * b * round_, block, rot, origin)
    slab(m, bone, cx, cy, cz, 2 * a * round_, h, 2 * b * 0.94, block, rot, origin)


def blob(m, bone, c, r, ramp, n=6, top=1.0, bottom=-1.0, light=None, rot=None, origin=None, round_=0.62):
    """An ellipsoid with radii r = (rx, ry, rz) centred at c, from bottom to top (-1..1 of ry) in n slices.
    Each slice's tone comes from its height, dark below and light above."""
    cx, cy, cz = c
    rx, ry, rz = r
    edges = [bottom + (top - bottom) * i / n for i in range(n + 1)]
    for i in range(n):
        u0, u1 = edges[i], edges[i + 1]
        um = (u0 + u1) / 2
        f = math.sqrt(max(0.0, 1 - um * um))
        if f < 0.2: f = 0.2
        h = (u1 - u0) * ry
        y = cy + um * ry
        blk = tone(ramp, (um + 1) / 2) if light is None else tone(ramp, light(um))
        ring(m, bone, cx, y, cz, rx * f, rz * f, h + 0.02, blk, rot, origin or (rot and c), round_)


def taper(m, bone, p0, p1, r0, r1, ramp, n=3, flat=1.0, bright=None):
    """A rounded limb from p0 (radius r0) to p1 (radius r1) in n pieces; each piece is rotated to follow the
    line, so arms, horns and tusks can point anywhere. flat squashes the depth (1 = round)."""
    dx, dy, dz = (p1[i] - p0[i] for i in range(3))
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    # rotation that turns +y onto the direction: tilt about x (towards z) then about z (towards x)
    rx = math.degrees(math.atan2(dz, math.sqrt(dx * dx + dy * dy)))
    rz = -math.degrees(math.atan2(dx, dy))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        tm = (t0 + t1) / 2
        c = [p0[k] + (p1[k] - p0[k]) * tm for k in range(3)]
        r = r0 + (r1 - r0) * tm
        seg = L / n * 1.08
        blk = tone(ramp, bright(tm) if bright else 1 - tm * 0.5)
        rot = (rx, 0, rz) if abs(rx) > 0.5 or abs(rz) > 0.5 else None
        slab(m, bone, c[0], c[1], c[2], 2 * r * 0.94, seg, 2 * r * 0.62 * flat, blk, rot, c if rot else None)
        slab(m, bone, c[0], c[1], c[2], 2 * r * 0.62, seg, 2 * r * 0.94 * flat, blk, rot, c if rot else None)


def lathe(m, bone, prof, ramp, round_=0.62, lo=0.0, hi=1.0):
    """A turned form (robe, hat, bell sleeve) from a profile of points (y, a, b, x, z): one rounded slice
    between each pair of points, so the outline can flare, narrow and lean. Tone runs lo..hi by height."""
    y0, y1 = prof[0][0], prof[-1][0]
    for p, q in zip(prof, prof[1:]):
        a, b = (p[1] + q[1]) / 2, (p[2] + q[2]) / 2
        x, z = (p[3] + q[3]) / 2, (p[4] + q[4]) / 2
        t = ((p[0] + q[0]) / 2 - y0) / max(0.01, y1 - y0)
        ring(m, bone, x, (p[0] + q[0]) / 2, z, a, b, abs(q[0] - p[0]) + 0.04, tone(ramp, lo + (hi - lo) * t), round_=round_)


def chain(m, bone, pts, r0, r1, ramp, flat=1.0, bright=None):
    """A bent taper through several points (a gnarled staff, a drooping hat tip, a curling beard)."""
    n = len(pts) - 1
    for i in range(n):
        a, b = r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n
        taper(m, bone, pts[i], pts[i + 1], a, b, ramp, n=1, flat=flat, bright=(lambda t, i=i: bright((i + t) / n)) if bright else None)


# ------------------------------------------------------------------------------------------------ the ogre

@sculpt("brewgut")
def brewgut():
    """The tavern ogre, sculpted: a heavy round head sunk forward between hunched shoulders, a jutting
    underbite with two curved tusks, a thick brow over small deep eyes, a broad flat nose and pointed ears;
    a barrel belly in a grubby white shirt under an open leather vest, a thick belt with a brass buckle, a
    ragged apron, short thick legs in patched trousers and heavy boots, puffed sleeves, huge green forearms
    and fists, and a wooden tankard."""
    m = Model("brewgut", "biped", 1.6)
    m.sculpted = True          # shading comes from the ramps; no mottle patches
    GREEN = ["green_terracotta", "green_terracotta", "lime_terracotta", "lime_terracotta", "green_concrete_powder"]
    SHIRT = ["light_gray_concrete_powder", "white_concrete", "white_concrete_powder", "white_wool"]
    VEST = ["brown_terracotta", "brown_concrete", "brown_wool", "brown_concrete_powder"]
    TROU = ["brown_terracotta", "light_gray_terracotta", "light_gray_terracotta"]
    BOOT = ["black_terracotta", "gray_terracotta", "brown_terracotta"]
    humanoid(m, hip=13, legx=3.6, neck=27, shoulder=28, armx=10)
    m.bone("jaw", "head", (0, 28, 4))
    m.bone("mug", "armR", (-12, 11, 3))
    # legs: thick, slightly bowed, heavy boots with a rounded toe
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.8
        taper(m, leg, (x, 13, 0), (x + sd * 0.6, 3.5, 0.4), 3.2, 2.7, TROU, n=3)
        slab(m, leg, x + sd * 0.4, 8.5, 2.7, 1.2, 1.4, 0.3, "brown_terracotta")                 # patch
        blob(m, leg, (x + sd * 0.6, 2.2, 1.6), (3.2, 2.2, 4.6), BOOT, n=3, bottom=-1.0, top=0.9)
        slab(m, leg, x + sd * 0.6, 0.35, 1.6, 6.0, 0.7, 9.0, "black_terracotta")                 # sole
    # the barrel belly in the shirt, the vest over the sides and back
    blob(m, "body", (0, 21, 0.8), (8.6, 8.5, 7.4), SHIRT, n=7, bottom=-0.85, top=0.9)
    for sd in (1, -1):
        blob(m, "body", (sd * 5.0, 22, -0.4), (4.4, 7.6, 7.0), VEST, n=5, bottom=-0.75, top=0.95)
        taper(m, "body", (sd * 3.2, 28.5, 5.8), (sd * 4.6, 16.0, 7.2), 1.0, 0.8, VEST, n=3, flat=0.5)   # vest edge
    blob(m, "body", (0, 23, -3.5), (7.8, 7.0, 4.2), VEST, n=4, bottom=-0.8, top=0.95)
    for y in (24.5, 21.5):
        slab(m, "body", 0, y, 8.05, 0.9, 0.9, 0.4, "light_gray_concrete_powder")                # laces
    # belt and buckle, then the apron that flares and hangs ragged
    ring(m, "hips", 0, 14.6, 0.6, 8.8, 7.6, 2.0, "dark_oak_planks", round_=0.7)
    slab(m, "hips", 0, 14.6, 8.6, 2.6, 2.2, 0.5, "gold_block")
    slab(m, "hips", 0, 14.6, 8.85, 1.2, 1.0, 0.2, "dark_oak_planks")
    for i, (y, a) in enumerate(((12.6, 8.4), (10.9, 8.9))):
        ring(m, "hips", 0, y, 0.6, a, 7.4 + i * 0.4, 1.8, SHIRT[2 - i], round_=0.72)
    for x, h, z in ((-6.5, 2.4, 6.0), (-3.6, 3.2, 7.8), (-0.6, 2.2, 8.2), (2.4, 3.4, 7.9), (5.4, 2.0, 6.4), (7.6, 2.8, 2.0), (-7.8, 2.6, 1.0)):
        slab(m, "hips", x, 10.0 - h / 2, z, 2.2, h, 0.8, SHIRT[1], rot=(0, 0, 8 if x > 0 else -8), origin=(x, 10.0, z))
    # shoulders hunch up into puffed sleeves
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 10
        blob(m, arm, (x, 26.2, 0), (4.0, 4.0, 4.0), SHIRT, n=4)
        taper(m, arm, (x + sd * 0.3, 22.5, 0.2), (x + sd * 0.8, 12.5, 1.2), 3.4, 3.8, GREEN, n=3, bright=lambda t: 0.85 - t * 0.6)
        blob(m, arm, (x + sd * 0.9, 10.6, 1.6), (3.6, 3.0, 3.6), GREEN, n=3)                   # fist
        for k in (-1.4, 0, 1.4):
            slab(m, arm, x + sd * 0.9 + k, 9.8, 5.0, 1.1, 1.2, 0.6, "green_terracotta")         # knuckles
        slab(m, arm, x + sd * 0.4, 20.5, 2.0, 3.0, 1.0, 3.4, "light_gray_concrete_powder")      # rolled cuff
    # the head: round skull sunk low and forward, heavy jaw with an underbite
    blob(m, "head", (0, 31.2, 3.6), (6.4, 5.8, 6.0), GREEN, n=6, bottom=-0.6, top=0.97)
    blob(m, "jaw", (0, 27.4, 4.6), (5.2, 2.4, 4.6), GREEN, n=3, bottom=-1.0, top=0.6, light=lambda u: 0.15 + (u + 1) * 0.25)
    slab(m, "jaw", 0, 28.5, 8.9, 6.4, 1.0, 0.9, "lime_terracotta")                                # lower lip
    slab(m, "jaw", 0, 29.15, 8.7, 5.4, 0.5, 0.8, "black_terracotta")                               # mouth line
    slab(m, "jaw", 1.4, 29.1, 8.95, 1.4, 0.5, 0.6, "pink_terracotta")                            # tongue tip
    for sd in (1, -1):
        taper(m, "jaw", (sd * 2.8, 28.6, 8.8), (sd * 3.4, 31.0, 9.8), 0.7, 0.3, ["end_stone", "bone_block", "bone_block"], n=2)
    slab(m, "head", 0, 34.0, 8.8, 8.2, 1.3, 2.4, "green_terracotta", rot=(10, 0, 0))                   # heavy brow
    for sd in (1, -1):
        slab(m, "head", sd * 2.5, 32.4, 9.4, 2.2, 1.5, 0.4, "white_concrete")                    # eyes
        slab(m, "head", sd * 2.2, 32.3, 9.65, 1.0, 1.1, 0.2, "black_concrete")
        slab(m, "head", sd * 2.6, 33.3, 9.6, 2.8, 0.6, 0.6, "green_terracotta", rot=(0, 0, -16 * sd))   # angry lid
        taper(m, "head", (sd * 6.0, 31.4, 3.2), (sd * 9.0, 32.6, 1.4), 1.3, 0.35, GREEN[1:], n=2, flat=0.45)  # ear
    blob(m, "head", (0, 30.6, 9.8), (1.8, 1.2, 1.4), ["green_terracotta", "lime_terracotta"], n=2)                                  # nose
    for sd in (1, -1):
        slab(m, "head", sd * 0.8, 30.1, 10.9, 0.6, 0.5, 0.3, "green_terracotta")                 # nostrils
    # the tankard: a little barrel with hoops and foam
    blob(m, "mug", (-12.2, 8.0, 4.4), (2.6, 3.2, 2.6), ["spruce_planks", "spruce_planks", "oak_planks"], n=3, round_=0.75)
    for y in (6.0, 9.6):
        ring(m, "mug", -12.2, y, 4.4, 2.75, 2.75, 0.5, "iron_block", round_=0.75)
    blob(m, "mug", (-12.2, 11.2, 4.4), (2.4, 0.9, 2.4), ["white_wool"], n=1)
    m.bend = -14
    swig = attack(1.6, 1.0, {
        "armR": {"rot": K((0, Z), (0.5, (-150, 0, 0)), (0.9, (-160, 0, 10)), (1.1, (-60, 0, 0)), (1.6, Z))},
        "head": {"rot": K((0, Z), (0.5, (-30, 0, 0)), (0.9, (-34, 0, 0)), (1.1, (14, 0, 0)), (1.6, Z))},
        "jaw": {"rot": K((0, Z), (0.9, Z), (1.05, (24, 0, 0)), (1.3, (24, 0, 0)), (1.6, Z))},
        "body": {"rot": K((0, Z), (0.5, (-10, 0, 0)), (1.0, (14, 0, 0)), (1.6, Z))}})
    standard_anims(m, heavy=1.2, extra={"swig": swig, "idle": idle_biped(4.0, 18, breath=0.04, extra={"jaw": {"rot": wave(0, 3, 4.0)}})})
    m.attacks = {"slam": "slam", "charge": "lunge", "roar": "swig"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the hermit

@sculpt("old_blindman")
def old_blindman():
    """Hermit Ezra, sculpted: a stooped old man in a heavy brown hooded robe that flares to a ragged hem, the
    hood thrown forward so his face sits in shadow, eyes long gone under drooping white brows, a long hooked
    nose, a white beard that flows down to a rope belt, wide bell sleeves, a hump on his back, and a gnarled
    staff with a brass band whose crook carries a small lantern."""
    m = Model("old_blindman", "biped", 1.0)
    m.sculpted = True          # shading comes from the ramps; no mottle patches
    ROBE = ["black_terracotta", "brown_terracotta", "brown_terracotta", "brown_concrete", "brown_concrete"]
    SKIN = ["brown_terracotta", "terracotta", "terracotta", "white_terracotta"]
    BEARD = ["light_gray_wool", "light_gray_concrete_powder", "white_concrete", "white_concrete_powder", "white_wool"]
    WOOD = ["black_terracotta", "dark_oak_planks", "stripped_dark_oak_log"]
    humanoid(m, hip=7, legx=2, neck=18, shoulder=18.5, armx=6)
    m.bone("lamp", "armR", (-10.4, 26.6, 4.2))
    # feet peeking out under the hem
    for sd, leg in ((1, "legL"), (-1, "legR")):
        blob(m, leg, (sd * 2.3, 1.0, 2.6), (1.7, 1.0, 2.5), ["black_terracotta", "brown_terracotta"], n=2, bottom=-1.0, top=0.8)
    # the skirt flares to the floor; a ragged hem of tilted strips
    lathe(m, "hips", [(0.8, 7.0, 6.0, 0, 0.3), (3.0, 6.6, 5.6, 0, 0.3), (5.4, 6.0, 5.0, 0, 0.2), (8.0, 5.5, 4.6, 0, 0.2)], ROBE, round_=0.7, lo=0.15, hi=0.6)
    for x, z, h in ((-5.6, 3.0, 1.4), (-3.0, 5.4, 1.8), (0.0, 5.9, 1.2), (3.0, 5.4, 1.7), (5.6, 3.0, 1.3), (6.4, -1.0, 1.6), (-6.4, -1.0, 1.5), (0, -5.7, 1.6)):
        slab(m, "hips", x, 0.8 - h / 2 + 0.5, z, 2.4, h, 0.7, "black_terracotta", rot=(0, math.degrees(math.atan2(x, z)), 7 if x >= 0 else -7), origin=(x, 1.0, z))
    # the upper robe, leaning forward into a stoop, with a hump on the back
    lathe(m, "body", [(8.0, 5.5, 4.6, 0, 0.2), (11.0, 5.7, 4.6, 0, 0.3), (14.0, 5.9, 4.6, 0, 0.6), (16.6, 5.6, 4.4, 0, 1.0), (18.6, 4.4, 3.6, 0, 1.4)], ROBE, round_=0.7, lo=0.35, hi=0.95)
    blob(m, "body", (0, 15.2, -2.4), (4.6, 3.6, 3.0), ROBE[1:], n=3, top=0.9)
    for sd in (1, -1):
        taper(m, "body", (sd * 1.6, 18.0, 5.5), (sd * 3.6, 8.6, 5.2), 0.9, 1.1, ["brown_terracotta", "brown_concrete"], n=2, flat=0.5)   # robe edges
    # rope belt with a knot and two hanging ends
    ring(m, "hips", 0, 8.6, 0.3, 5.9, 5.0, 0.9, "stripped_oak_log", round_=0.7)
    blob(m, "hips", (1.6, 8.5, 5.4), (0.8, 0.7, 0.6), ["stripped_oak_log"], n=1)
    for dx in (1.2, 2.2):
        taper(m, "hips", (dx + 0.2, 8.2, 5.5), (dx + 0.6, 4.2, 6.0), 0.35, 0.3, ["stripped_spruce_log", "stripped_oak_log"], n=2)
    # head: a face in the shadow of the hood
    blob(m, "head", (0, 21.4, 2.4), (3.4, 3.6, 3.0), SKIN, n=4, bottom=-0.8, top=0.95)
    slab(m, "head", 0, 21.8, 0.6, 8.4, 7.6, 1.0, "black_terracotta")                                # dark inside of the hood
    blob(m, "head", (0, 22.0, -0.8), (5.0, 5.4, 4.6), ROBE[1:], n=5, bottom=-0.75, top=0.98)
    chain(m, "head", [(-4.4, 17.8, 3.4), (-4.6, 22.6, 4.0), (-3.0, 25.8, 4.4), (0, 26.6, 4.6), (3.0, 25.8, 4.4), (4.6, 22.6, 4.0), (4.4, 17.8, 3.4)],
          1.3, 1.3, ROBE[2:], bright=lambda t: 1 - abs(t - 0.5))                                                       # hood rim
    # blind eyes under heavy drooping brows, a long hooked nose, sunken cheeks
    slab(m, "head", 0, 22.0, 5.3, 5.4, 0.5, 0.3, "black_terracotta")
    for sd in (1, -1):
        taper(m, "head", (sd * 0.5, 23.0, 5.4), (sd * 3.4, 21.6, 5.0), 0.75, 0.4, BEARD[2:], n=2, flat=0.7)       # brow
    chain(m, "head", [(0, 22.2, 5.2), (0, 20.2, 6.4), (0, 18.6, 6.9)], 0.95, 0.85, ["terracotta", "terracotta", "white_terracotta"])
    blob(m, "head", (0, 18.4, 6.6), (1.0, 0.9, 1.0), ["terracotta", "terracotta"], n=2)
    # the beard flows down over the chest to the belt, a moustache over it
    chain(m, "head", [(0, 19.0, 4.6), (0, 15.5, 5.6), (0, 12.0, 5.9), (0.3, 8.6, 6.1), (0.6, 6.6, 6.2)], 3.0, 0.7, BEARD, flat=0.55, bright=lambda t: 1 - t * 0.85)
    for sd in (1, -1):
        chain(m, "head", [(sd * 0.6, 18.4, 6.0), (sd * 2.4, 17.6, 5.7), (sd * 3.0, 15.4, 5.4)], 0.7, 0.4, BEARD[2:], flat=0.8)
        taper(m, "head", (sd * 2.6, 18.4, 4.6), (sd * 2.4, 13.0, 5.4), 1.3, 0.6, BEARD[1:], n=2, flat=0.6)       # side locks
    # bell sleeves and knobbly hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        blob(m, arm, (sd * 6.0, 17.4, 0.6), (2.4, 2.4, 2.6), ROBE[2:], n=3)
        lathe(m, arm, [(16.4, 2.0, 2.0, sd * 6.4, 0.8), (14.0, 2.3, 2.3, sd * 6.8, 1.6), (11.8, 2.8, 2.8, sd * 7.0, 2.4)], ROBE, lo=0.3, hi=0.9)
        ring(m, arm, sd * 7.0, 11.6, 2.4, 2.95, 2.95, 0.5, "brown_terracotta")
        blob(m, arm, (sd * 7.0, 10.2, 2.8), (1.4, 1.5, 1.4), SKIN[1:], n=2)
        slab(m, arm, sd * 7.0, 10.6, 4.1, 2.0, 0.8, 0.6, "terracotta")                                        # knuckles
    # the gnarled staff with a brass band and a crook that carries the lantern
    chain(m, "armR", [(-7.2, 0.0, 3.6), (-7.5, 5.0, 3.3), (-7.0, 10.0, 3.7), (-7.4, 15.0, 3.4), (-7.0, 20.0, 3.8), (-7.3, 24.6, 3.6)], 0.75, 0.6, WOOD,
          bright=lambda t: 0.2 + t * 0.6)
    for y, r in ((12.6, 0.8), (6.0, 0.95), (17.8, 0.9)):
        blob(m, "armR", (-7.2, y, 3.6), (r, 0.5, r), ["dark_oak_planks"], n=1)                                      # knots
    ring(m, "armR", -7.1, 13.6, 3.6, 0.85, 0.85, 0.7, "gold_block", round_=0.75)
    chain(m, "armR", [(-7.3, 24.4, 3.6), (-7.6, 26.8, 3.9), (-9.2, 27.8, 4.1), (-10.4, 26.8, 4.2)], 0.6, 0.45, WOOD[1:])
    # a small iron lantern built from blocks (the real lantern block would show tiny inside its box)
    slab(m, "lamp", -10.4, 26.0, 4.3, 0.3, 1.0, 0.3, "polished_blackstone")
    slab(m, "lamp", -10.4, 25.35, 4.3, 1.9, 0.4, 1.9, "polished_blackstone")
    slab(m, "lamp", -10.4, 24.2, 4.3, 1.5, 1.9, 1.5, "shroomlight")
    m.cubes[-1]["l"] = True
    for dx, dz in ((-0.75, -0.75), (0.75, -0.75), (-0.75, 0.75), (0.75, 0.75)):
        slab(m, "lamp", -10.4 + dx, 24.2, 4.3 + dz, 0.3, 1.9, 0.3, "polished_blackstone")
    slab(m, "lamp", -10.4, 23.05, 4.3, 1.9, 0.4, 1.9, "polished_blackstone")
    m.no_elbows = m.no_knees = True
    m.bend = -10
    sway = {"lamp": {"rot": wave2((6, 0, 3), 2.2)}}
    standard_anims(m, heavy=0.6, idle=idle_biped(4.4, 10, breath=0.02, extra=sway))
    m.attacks = {"pull": "cast", "darkness": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the gnome

@sculpt("old_pip")
def old_pip():
    """Grandpa Pip, sculpted: a round little gnome elder under a tall red cap that folds at the brim and droops
    back at the tip, bushy white brows over bright green eyes, rosy cheeks, a long drooping nose over a big
    white moustache and a pointed beard, a round teal tunic with a dark belt and a glowing emerald buckle,
    small skin hands and stubby boots with turned-up toes."""
    m = Model("old_pip", "biped", 1.0)
    m.sculpted = True          # shading comes from the ramps; no mottle patches
    RED = ["red_terracotta", "red_wool", "red_wool", "red_concrete", "red_concrete"]
    SKIN = ["terracotta", "white_terracotta", "white_terracotta"]
    WHITE = ["light_gray_concrete_powder", "white_concrete", "white_concrete_powder", "white_wool"]
    TEAL = ["cyan_terracotta", "cyan_wool", "cyan_wool", "cyan_concrete", "cyan_concrete"]
    NOSE = ["brown_terracotta", "terracotta", "terracotta"]
    humanoid(m, hip=4, legx=2, neck=13, shoulder=12.5, armx=5.6)
    m.bone("hat", "head", (0, 19.5, 0.6))
    m.bone("beard", "head", (0, 13.6, 4))
    # stubby legs and boots with a turned-up toe
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2.1
        taper(m, leg, (x, 4.6, 0), (x, 2.0, 0.2), 1.6, 1.5, ["brown_terracotta", "brown_concrete"], n=2)
        blob(m, leg, (x, 1.2, 0.9), (1.8, 1.2, 2.7), ["black_terracotta", "brown_terracotta", "brown_concrete"], n=2, bottom=-1.0, top=0.9)
        taper(m, leg, (x, 1.0, 3.2), (x, 2.2, 4.4), 0.8, 0.35, ["brown_terracotta", "brown_concrete"], n=1)
        slab(m, leg, x, 0.25, 1.1, 3.4, 0.5, 5.2, "black_terracotta")
    # a round tunic that flares over the hips, the belt and the emerald buckle
    blob(m, "body", (0, 8.8, 0.3), (5.0, 4.8, 4.4), TEAL, n=6, bottom=-0.85, top=0.95)
    lathe(m, "hips", [(3.6, 5.4, 4.8, 0, 0.3), (5.0, 5.3, 4.7, 0, 0.3), (6.4, 5.1, 4.6, 0, 0.3)], TEAL, round_=0.7, lo=0.25, hi=0.5)
    ring(m, "hips", 0, 6.6, 0.3, 5.3, 4.7, 1.2, "dark_oak_planks", round_=0.7)
    slab(m, "hips", 0, 6.6, 4.9, 2.6, 2.2, 0.5, "emerald_block")
    m.cubes[-1]["l"] = True
    slab(m, "hips", 0, 6.6, 5.15, 1.2, 1.0, 0.2, "black_terracotta")
    # arms: teal sleeves, skin hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 5.4
        blob(m, arm, (x - sd * 0.3, 11.4, 0.2), (1.8, 1.7, 1.8), TEAL[2:], n=2)
        taper(m, arm, (x + sd * 0.3, 11.0, 0.3), (x + sd * 0.8, 7.6, 1.0), 1.7, 1.8, TEAL, n=2, bright=lambda t: 0.8 - t * 0.5)
        ring(m, arm, x + sd * 0.8, 7.3, 1.0, 1.9, 1.9, 0.6, "cyan_terracotta")
        blob(m, arm, (x + sd * 0.9, 6.1, 1.3), (1.3, 1.3, 1.3), SKIN, n=2)
    # head: round face, rosy cheeks, green eyes under bushy brows, white hair at the back
    blob(m, "head", (0, 16.2, 1.0), (3.8, 3.8, 3.6), SKIN, n=5, bottom=-0.8, top=0.95)
    blob(m, "head", (0, 16.6, -0.8), (4.1, 3.0, 3.0), WHITE, n=3, bottom=-0.9, top=0.9)
    for sd in (1, -1):
        slab(m, "head", sd * 1.5, 16.9, 4.55, 1.5, 1.3, 0.3, "white_concrete")
        slab(m, "head", sd * 1.35, 16.8, 4.75, 0.9, 1.0, 0.2, "lime_concrete")
        slab(m, "head", sd * 1.2, 16.9, 4.9, 0.4, 0.5, 0.1, "black_concrete")
        taper(m, "head", (sd * 0.5, 18.0, 4.6), (sd * 3.0, 18.6, 4.0), 0.6, 0.45, WHITE[1:], n=2, flat=0.8)   # brows
        slab(m, "head", sd * 2.3, 15.4, 4.3, 1.4, 0.9, 0.3, "pink_terracotta")                                 # cheeks
        slab(m, "head", sd * 3.9, 16.0, 1.2, 0.7, 1.8, 1.4, "white_terracotta")                                 # ears
    chain(m, "head", [(0, 17.0, 4.4), (0, 15.2, 5.8), (0, 13.2, 6.6)], 1.0, 1.0, NOSE)
    blob(m, "head", (0, 13.0, 6.4), (1.1, 1.0, 1.0), NOSE[1:], n=2)
    # moustache and beard on their own bone so they bob
    for sd in (1, -1):
        chain(m, "beard", [(sd * 0.5, 13.8, 5.4), (sd * 2.4, 13.2, 5.0), (sd * 3.6, 12.0, 4.4)], 1.0, 0.5, WHITE[1:], flat=0.8)
    blob(m, "beard", (0, 11.4, 3.6), (3.6, 2.4, 2.0), WHITE, n=3, bottom=-0.9, top=0.9)
    chain(m, "beard", [(0, 10.4, 4.2), (0, 7.8, 5.0), (0.3, 5.8, 5.2)], 2.4, 0.5, WHITE, flat=0.6, bright=lambda t: 0.9 - t * 0.7)
    # the cap: a folded brim, then a tall cone that bends back and droops at the tip
    ring(m, "hat", 0, 19.6, 0.6, 4.6, 4.4, 1.4, "red_wool", round_=0.72)
    ring(m, "hat", 0, 18.95, 0.6, 4.5, 4.3, 0.2, "red_terracotta", round_=0.72)
    lathe(m, "hat", [(20.2, 4.2, 4.0, 0, 0.5), (21.2, 3.95, 3.75, 0, 0.35), (22.2, 3.6, 3.4, 0, 0.15), (23.2, 3.15, 3.0, 0, -0.15),
                     (24.1, 2.7, 2.6, 0.1, -0.5), (25.0, 2.2, 2.1, 0.25, -0.9), (25.8, 1.75, 1.7, 0.5, -1.3), (26.5, 1.35, 1.3, 0.8, -1.7),
                     (27.1, 1.0, 1.0, 1.1, -2.0)], RED, lo=0.2, hi=0.99)
    chain(m, "hat", [(1.1, 27.0, -2.0), (1.7, 27.6, -2.9), (2.0, 27.2, -3.8)], 0.8, 0.4, RED[1:])
    m.no_elbows = m.no_knees = True
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(3.0, 18, extra={"hat": {"rot": wave(2, 4, 3.0)}, "beard": {"rot": wave(0, 3, 1.5)}})})
    m.attacks = {"volley": "cast", "blink": "stomp"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the trolls

def knuckles(m, bone, x, y, z, w=1.2, n=3, gap=1.4, block="green_terracotta"):
    for k in range(n):
        slab(m, bone, x + (k - (n - 1) / 2) * gap, y, z, w, w * 1.05, 0.7, block)


@sculpt("grubnose")
def grubnose():
    """Grub the troll, sculpted: a hunched ochre troll that is all shoulders and long arms, the head hung low
    and forward under a hump of muscle, a heavy brow over small black eyes, a huge bulbous red nose over a
    lipless grin with stubby tusks, long drooping ears, rag wraps round thick forearms and big fists, short
    bowed legs with splayed toes, and a leather loincloth on a belt strung with bones and a little skull."""
    m = Model("grubnose", "biped", 1.6)
    m.sculpted = True
    SK = ["orange_terracotta", "yellow_terracotta", "yellow_terracotta", "yellow_terracotta", "yellow_terracotta", "yellow_terracotta"]
    NOSE = ["red_terracotta", "terracotta", "terracotta", "orange_terracotta"]
    LEA = ["black_terracotta", "brown_terracotta", "brown_concrete", "brown_concrete"]
    RAG = ["light_gray_concrete", "light_gray_concrete", "white_concrete"]
    BONE = ["bone_block", "white_concrete"]
    humanoid(m, hip=13, legx=5.5, neck=29, shoulder=30, armx=12, jaw=(0, 29.6, 7))
    m.bone("cloth", "hips", (0, 13, 6))
    # short bowed legs, wide feet with toes
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 5.6
        taper(m, leg, (x, 13.5, 0), (x + sd * 1.2, 4.5, 0.6), 4.2, 3.3, SK, n=3, bright=lambda t: 0.75 - t * 0.5)
        blob(m, leg, (x + sd * 1.3, 2.2, 1.8), (3.9, 2.2, 4.8), SK, n=3, bottom=-1.0, top=0.9, light=lambda u: 0.1 + (u + 1) * 0.3)
        for k in (-1.4, 0.0, 1.4):
            blob(m, leg, (x + sd * 1.3 + k * 1.5, 1.1, 6.2), (1.0, 1.0, 1.1), SK[1:3], n=1)
            slab(m, leg, x + sd * 1.3 + k * 1.5, 1.4, 7.0, 0.9, 0.6, 0.5, "bone_block")                 # toenails
    # the hunched trunk: a big chest under a hump, a round gut over the belt
    blob(m, "body", (0, 18.5, 2.2), (8.0, 5.6, 6.6), SK, n=5, bottom=-0.9, top=0.8, light=lambda u: 0.15 + (u + 1) * 0.3)
    blob(m, "body", (0, 24.0, 1.2), (9.4, 6.2, 7.0), SK, n=6, bottom=-0.75, top=0.95)
    blob(m, "body", (0, 28.0, -2.4), (6.6, 3.2, 4.6), SK[1:], n=3, bottom=-0.6, top=0.98)                # hump
    for sd in (1, -1):
        blob(m, "body", (sd * 4.0, 25.0, 6.8), (3.4, 2.4, 1.5), SK[1:], n=2)                                # pecs
    # a leather strap across the chest, strung with teeth
    chain(m, "body", [(7.2, 29.4, 4.2), (4.2, 26.6, 8.0), (0.4, 23.0, 8.6), (-3.6, 19.6, 8.0), (-6.8, 16.6, 5.4)], 0.95, 0.95, LEA[1:], flat=0.5)
    chain(m, "body", [(7.2, 29.4, 3.6), (3.0, 27.0, -5.4), (-3.0, 21.0, -6.2), (-6.8, 16.6, 4.8)], 0.95, 0.95, LEA[1:2], flat=0.5)
    for x, y, z in ((3.0, 25.0, 8.6), (0.4, 22.2, 9.1), (-2.2, 19.6, 8.8)):
        taper(m, "body", (x, y, z), (x - 0.1, y - 1.8, z + 0.4), 0.4, 0.2, BONE, n=1)
    slab(m, "body", 0, 29.0, 7.6, 8.0, 1.0, 1.4, "orange_terracotta")                                        # shadow under the chin
    for k in range(3):                                                                                        # warts on the hump
        slab(m, "body", (k - 1) * 3.0, 31.0 - abs(k - 1) * 0.8, -2.6 + abs(k - 1) * 0.6, 1.0, 0.7, 1.0, "orange_terracotta")
    # belt with bones and a skull, the loincloth on its own bone so it swings
    ring(m, "hips", 0, 13.8, 1.6, 8.6, 7.2, 2.0, "brown_terracotta", round_=0.72)
    for x, z in ((-5.6, 6.6), (5.6, 6.6), (-7.8, 2.6), (7.8, 2.6)):
        taper(m, "hips", (x, 13.0, z), (x * 1.04, 9.6, z + 0.4), 0.55, 0.45, BONE, n=1)
        slab(m, "hips", x * 1.04, 9.3, z + 0.4, 1.4, 0.7, 0.9, "bone_block")
    blob(m, "hips", (2.8, 13.2, 8.6), (1.4, 1.4, 1.2), BONE, n=2)                                           # skull
    for dx in (-0.5, 0.5):
        slab(m, "hips", 2.8 + dx, 13.4, 9.85, 0.5, 0.5, 0.1, "black_concrete")
    taper(m, "cloth", (0, 13.0, 7.4), (0, 4.4, 8.4), 4.4, 3.4, LEA, n=3, flat=0.25, bright=lambda t: 0.9 - t * 0.6)
    for x, h in ((-2.4, 1.4), (0.4, 2.0), (2.6, 1.1)):
        slab(m, "cloth", x, 4.0 - h / 2, 8.5, 1.8, h, 0.5, "brown_terracotta", rot=(0, 0, 7 if x > 0 else -7), origin=(x, 4.0, 8.5))
    taper(m, "hips", (0, 13.0, -5.0), (0, 6.0, -5.8), 4.6, 3.8, LEA, n=2, flat=0.25)
    # long heavy arms: shoulder balls, a rag-wrapped forearm, big fists near the knees
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 12
        blob(m, arm, (x - sd * 0.8, 28.2, 0.4), (4.0, 3.8, 4.2), SK, n=4)
        taper(m, arm, (x, 26.6, 0.4), (x + sd * 1.4, 18.6, 1.6), 3.1, 2.7, SK, n=4, bright=lambda t: 0.85 - t * 0.4)
        blob(m, arm, (x + sd * 0.3, 23.6, 1.6), (2.6, 3.0, 2.4), SK[2:], n=3)                                  # biceps
        taper(m, arm, (x + sd * 1.4, 18.6, 1.6), (x + sd * 1.8, 10.6, 3.0), 3.0, 3.5, SK, n=4, bright=lambda t: 0.6 - t * 0.4)
        if sd < 0:                                                                                          # rag wraps
            for y, r in ((15.6, 3.45), (13.6, 3.6)):
                ring(m, arm, x + sd * 1.65, y, 2.4, r, r, 1.3, RAG[1 if y > 14.5 else 2], round_=0.66)
            slab(m, arm, x + sd * 3.2, 12.4, 4.0, 0.9, 2.6, 0.8, "light_gray_concrete", rot=(0, 0, 14 * sd), origin=(x + sd * 3.2, 13.6, 4.0))
        else:                                                                                               # leather bracer with a stone
            ring(m, arm, x + sd * 1.65, 14.4, 2.4, 3.6, 3.6, 3.4, "brown_terracotta", round_=0.66)
            for y in (16.0, 12.8):
                ring(m, arm, x + sd * 1.65, y, 2.4, 3.75, 3.75, 0.5, "dark_oak_planks", round_=0.66)
            slab(m, arm, x + sd * 1.65, 14.4, 5.9, 1.8, 1.8, 0.5, "dark_oak_planks")
            slab(m, arm, x + sd * 1.65, 14.4, 6.15, 1.1, 1.1, 0.3, "prismarine_bricks")  # loose rag end
        blob(m, arm, (x + sd * 1.9, 8.6, 3.4), (3.7, 3.0, 3.7), SK, n=3, light=lambda u: 0.1 + (u + 1) * 0.35)    # fist
        knuckles(m, arm, x + sd * 1.9, 7.9, 7.0, w=1.3, gap=1.6, block="yellow_terracotta")
    # the head hangs low and forward: skull, brow, little eyes, a huge nose, long ears
    blob(m, "head", (0, 31.6, 6.6), (6.4, 5.6, 6.0), SK, n=5, bottom=-0.6, top=0.97)
    chain(m, "head", [(-4.6, 33.4, 11.0), (-1.8, 34.2, 12.0), (1.8, 34.2, 12.0), (4.6, 33.4, 11.0)], 1.2, 1.2, SK[2:])        # brow ridge
    for sd in (1, -1):
        slab(m, "head", sd * 2.5, 32.40, 12.45, 1.7, 1.3, 0.4, "black_concrete")                            # small deep eyes
        slab(m, "head", sd * 2.2, 32.70, 12.70, 0.5, 0.5, 0.1, "white_concrete")
        slab(m, "head", sd * 2.8, 33.30, 12.60, 2.6, 0.6, 0.6, "orange_terracotta", rot=(0, 0, -14 * sd))
        chain(m, "head", [(sd * 5.2, 32.0, 6.4), (sd * 8.2, 32.4, 5.4), (sd * 10.6, 31.2, 4.0)], 1.6, 0.35, SK[1:], flat=0.4)   # drooping ears
    for x, z, h, tilt in ((-2.4, 6.8, 2.2, -18), (-0.8, 6.2, 2.8, -6), (0.9, 6.4, 2.6, 8), (2.4, 7.0, 2.0, 20), (0.0, 3.8, 2.4, 0)):
        slab(m, "head", x, 37.0 + h / 2 - 0.4, z, 0.9, h, 0.9, "brown_terracotta", rot=(-14, 0, tilt), origin=(x, 37.0, z))   # scraggly tufts
    blob(m, "head", (0, 32.0, 12.8), (1.3, 1.6, 1.2), NOSE[1:], n=2)                                         # nose bridge
    blob(m, "head", (0, 29.6, 13.8), (2.6, 2.6, 2.4), NOSE, n=4)                                             # the big nose
    for sd in (1, -1):
        blob(m, "head", (sd * 2.0, 28.8, 13.4), (1.1, 1.0, 1.0), NOSE[:2], n=1)                              # nostril wings
    # jaw: a wide lipless grin with stubby tusks
    blob(m, "jaw", (0, 27.2, 8.6), (5.4, 2.4, 5.0), SK, n=3, bottom=-1.0, top=0.7, light=lambda u: 0.1 + (u + 1) * 0.3)
    slab(m, "jaw", 0, 28.20, 12.95, 7.6, 0.6, 0.4, "black_terracotta")
    for k in range(-2, 3):
        slab(m, "jaw", k * 1.4, 27.90, 13.05, 0.9, 0.7, 0.3, "bone_block")
    for sd in (1, -1):
        taper(m, "jaw", (sd * 3.4, 27.8, 12.2), (sd * 3.8, 30.2, 12.8), 0.75, 0.4, BONE, n=2)
    m.bend = -16
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(4.0, 16, breath=0.04, extra={"cloth": {"rot": wave(0, 6, 2.0, base=(4, 0, 0))},
                                                                                        "jaw": {"rot": wave(0, 4, 4.0)}})})
    m.attacks = {"slam": "slam", "shockwave": "stomp", "charge": "lunge"}
    m.melee = "swipe"
    return m


@sculpt("mudclub")
def mudclub():
    """Mudd the bog ogre, sculpted: a broad dark green brute with two curved pale horns sweeping out of its
    brow, a scowl over red eyes, a wide grin full of square teeth over a black goatee, a chest that tapers
    to a hard gut, a ragged brown loincloth, iron bands on its wrists and a heavy knotted log club studded
    with iron."""
    m = Model("mudclub", "biped", 1.6)
    m.sculpted = True
    SK = ["black_terracotta", "green_terracotta", "green_terracotta", "green_concrete", "lime_terracotta"]
    HORN = ["light_gray_terracotta", "white_terracotta", "bone_block", "bone_block"]
    LEA = ["black_terracotta", "brown_terracotta", "brown_terracotta", "brown_concrete"]
    WOOD = ["black_terracotta", "dark_oak_planks", "stripped_dark_oak_log", "spruce_planks"]
    humanoid(m, hip=13, legx=5.5, neck=32, shoulder=33, armx=13.5, jaw=(0, 32, 5))
    m.bone("cloth", "hips", (0, 13, 6))
    m.bone("club", "armR", (-15, 8, 3))
    m.hold = {"club": 30}
    # thick legs, dark heavy feet
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 5.4
        taper(m, leg, (x, 14.0, 0), (x + sd * 0.8, 4.6, 0.4), 4.0, 3.4, SK[1:], n=3, bright=lambda t: 0.7 - t * 0.5)
        blob(m, leg, (x + sd * 0.9, 2.2, 1.6), (3.8, 2.2, 4.6), ["black_terracotta", "green_terracotta"], n=3, bottom=-1.0, top=0.9)
        ring(m, leg, x + sd * 0.8, 5.4, 0.4, 3.6, 3.6, 1.0, "brown_terracotta", round_=0.66)                  # leg wrap
    # V-shaped torso: broad chest, tapering to a hard gut
    blob(m, "body", (0, 18.6, 1.4), (7.4, 5.4, 6.0), SK, n=4, bottom=-0.9, top=0.8, light=lambda u: 0.2 + (u + 1) * 0.3)
    blob(m, "body", (0, 26.0, 0.6), (10.6, 7.0, 7.0), SK, n=6, bottom=-0.75, top=0.95)
    for sd in (1, -1):
        blob(m, "body", (sd * 4.4, 27.0, 6.2), (4.0, 2.8, 1.8), SK[2:], n=2)                                   # pecs
        slab(m, "body", sd * 2.0, 21.6, 7.05, 2.6, 1.4, 0.5, "green_terracotta")                                # abs
        slab(m, "body", sd * 2.0, 19.2, 7.0, 2.4, 1.4, 0.5, "green_terracotta")
    # a fur collar of black goat hair under the chin
    chain(m, "body", [(0, 31.0, 6.6), (0, 27.6, 8.4), (0, 24.6, 8.0)], 3.0, 0.5, ["black_wool", "black_terracotta", "gray_terracotta"], flat=0.5,
          bright=lambda t: t * 0.6)
    # belt, the ragged loincloth front and back
    ring(m, "hips", 0, 14.2, 1.2, 8.4, 6.8, 2.2, "brown_terracotta", round_=0.72)
    slab(m, "hips", 0, 14.2, 8.2, 2.4, 2.4, 0.5, "iron_block")
    taper(m, "cloth", (0, 13.2, 7.0), (0, 4.6, 7.8), 4.6, 3.6, LEA, n=3, flat=0.25, bright=lambda t: 0.9 - t * 0.7)
    for x, h in ((-3.0, 1.6), (-0.8, 2.4), (1.4, 1.2), (3.2, 2.0)):
        slab(m, "cloth", x, 4.2 - h / 2, 7.9, 1.6, h, 0.5, "brown_terracotta", rot=(0, 0, 8 if x > 0 else -8), origin=(x, 4.2, 7.9))
    taper(m, "hips", (0, 13.2, -5.0), (0, 5.4, -5.8), 4.8, 3.8, LEA, n=2, flat=0.25)
    # arms: big shoulders, iron-banded wrists, fists
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 13.5
        blob(m, arm, (x - sd * 0.4, 30.4, 0.2), (4.6, 4.4, 4.6), SK[1:], n=4)
        taper(m, arm, (x + sd * 0.2, 28.0, 0.3), (x + sd * 1.2, 18.6, 1.2), 3.8, 3.2, SK, n=3, bright=lambda t: 0.9 - t * 0.4)
        taper(m, arm, (x + sd * 1.2, 18.6, 1.2), (x + sd * 1.5, 10.0, 2.6), 3.3, 3.6, SK, n=3, bright=lambda t: 0.6 - t * 0.35)
        ring(m, arm, x + sd * 1.45, 11.0, 2.4, 3.8, 3.8, 1.6, "iron_block", round_=0.66)
        for k in (-1.4, 1.4):
            slab(m, arm, x + sd * 1.45 + k, 11.0, 6.2, 0.6, 0.6, 0.4, "polished_blackstone")                     # rivets
        blob(m, arm, (x + sd * 1.6, 8.0, 3.0), (3.6, 3.0, 3.6), SK[1:], n=3)
        knuckles(m, arm, x + sd * 1.6, 7.4, 6.5, w=1.3, gap=1.6, block="green_terracotta")
    # the club: a knotted log, fat at the head, with iron studs
    chain(m, "club", [(-15.1, 4.0, 4.2), (-15.2, 10.0, 3.8), (-15.0, 16.0, 4.6), (-15.3, 22.0, 5.4)], 1.2, 2.6, WOOD, bright=lambda t: 0.25 + t * 0.7)
    blob(m, "club", (-15.3, 22.6, 5.5), (2.9, 2.6, 2.9), WOOD[1:], n=3)
    for dx, y, dz in ((2.6, 20.4, 0.4), (-2.6, 21.6, 0.2), (0.3, 19.8, 2.7), (0.2, 23.2, -2.6), (2.2, 23.6, 1.6), (-1.8, 24.0, 2.0)):
        slab(m, "club", -15.3 + dx, y, 5.5 + dz, 0.9, 0.9, 0.9, "iron_block")
    blob(m, "club", (-15.1, 12.8, 4.3), (1.6, 0.9, 1.6), ["dark_oak_planks"], n=1)                              # knot
    # head: square heavy jaw, scowl, red eyes, curved horns out of the brow
    blob(m, "head", (0, 35.6, 4.2), (5.6, 5.0, 5.2), SK, n=5, bottom=-0.7, top=0.97)
    chain(m, "head", [(-4.4, 37.0, 8.4), (-1.6, 37.6, 9.2), (1.6, 37.6, 9.2), (4.4, 37.0, 8.4)], 1.1, 1.1, SK[2:])        # brow ridge
    for sd in (1, -1):
        slab(m, "head", sd * 2.4, 36.0, 9.35, 2.2, 1.2, 0.4, "black_terracotta")
        slab(m, "head", sd * 2.3, 36.0, 9.6, 1.2, 0.9, 0.2, "red_concrete")
        m.cubes[-1]["l"] = True
        slab(m, "head", sd * 2.6, 36.9, 9.7, 3.0, 0.7, 0.7, "green_terracotta", rot=(0, 0, -20 * sd))          # scowl
        chain(m, "head", [(sd * 4.2, 38.6, 5.4), (sd * 7.6, 40.2, 4.6), (sd * 9.2, 43.2, 3.4), (sd * 8.4, 46.0, 2.0)], 1.5, 0.35, HORN,
              bright=lambda t: 0.1 + t * 0.85)
        ring(m, "head", sd * 4.6, 38.7, 5.3, 1.6, 1.6, 0.7, "light_gray_terracotta")
        taper(m, "head", (sd * 5.2, 35.6, 3.6), (sd * 7.6, 36.6, 2.2), 1.2, 0.35, SK[2:], n=2, flat=0.45)       # ears
    blob(m, "head", (0, 34.6, 9.6), (1.7, 1.3, 1.3), ["green_terracotta", "green_concrete"], n=2)
    for sd in (1, -1):
        slab(m, "head", sd * 0.8, 34.0, 10.6, 0.6, 0.5, 0.3, "black_terracotta")
    # the jaw: a wide grin of square teeth, two lower tusks and the goatee
    blob(m, "jaw", (0, 31.6, 5.0), (5.0, 2.2, 4.6), SK, n=3, bottom=-1.0, top=0.6, light=lambda u: 0.15 + (u + 1) * 0.3)
    slab(m, "jaw", 0, 32.8, 9.25, 7.4, 1.4, 0.5, "black_terracotta")
    for k in range(-2, 3):
        slab(m, "jaw", k * 1.4, 33.15, 9.45, 1.1, 0.7, 0.3, "white_concrete")
        slab(m, "jaw", k * 1.4 + 0.7, 32.45, 9.45, 1.1, 0.6, 0.3, "white_concrete")
    for sd in (1, -1):
        taper(m, "jaw", (sd * 3.4, 32.8, 9.0), (sd * 3.8, 35.0, 9.8), 0.7, 0.35, HORN[1:], n=2)
    chain(m, "jaw", [(0, 30.0, 9.0), (0, 28.2, 9.6), (0, 26.6, 9.4)], 1.5, 0.5, ["black_wool", "black_terracotta"], flat=0.7)
    m.bend = -20
    standard_anims(m, heavy=1.2, extra={"idle": idle_biped(4.0, 18, breath=0.04, extra={"cloth": {"rot": wave(0, 5, 2.0, base=(3, 0, 0))}})})
    m.attacks = {"slam": "slam", "leap": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the gorilla

@sculpt("thunderback")
def thunderback():
    """Big Bongo, the storm gorilla, sculpted: a huge silverback that leans on its knuckles, a peaked skull
    hung low between a wall of shoulders, a heavy brow over glowing storm-blue eyes, a wide flat nose and a
    fanged scowl, a bare dark chest, gold rings with a lightning mark
    on its arms, and a chieftain's band of four coloured feathers."""
    m = Model("thunderback", "biped", 1.7)
    m.sculpted = True
    FUR = ["black_terracotta", "brown_terracotta", "brown_terracotta", "brown_concrete", "brown_concrete"]
    SKIN = ["black_terracotta", "gray_terracotta", "gray_terracotta", "brown_terracotta"]
    FACE = ["gray_terracotta", "brown_terracotta", "light_gray_terracotta"]
    humanoid(m, hip=12, legx=6, neck=30, shoulder=31, armx=14, jaw=(0, 29.5, 8))
    m.bone("crown", "head", (0, 36, 5))
    # short bowed legs, dark leathery feet
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 6.0
        taper(m, leg, (x, 12.6, 0), (x + sd * 1.0, 4.4, 0.4), 4.2, 3.4, FUR, n=3, bright=lambda t: 0.8 - t * 0.5)
        blob(m, leg, (x + sd * 1.1, 1.8, 1.8), (3.6, 1.8, 4.6), SKIN, n=2, bottom=-1.0, top=0.9)
        for k in (-1.3, 0, 1.3):
            slab(m, leg, x + sd * 1.1 + k * 1.3, 1.0, 6.2, 1.1, 1.4, 0.9, "gray_terracotta")
    # the trunk: belly, a wall of chest and shoulders, a hump of muscle, the bare chest in front
    blob(m, "body", (0, 16.0, 0.8), (8.4, 4.6, 6.6), FUR, n=3, bottom=-0.9, top=0.9, light=lambda u: 0.15 + (u + 1) * 0.3)
    blob(m, "body", (0, 24.0, 0.6), (11.6, 7.6, 8.0), FUR, n=6, bottom=-0.8, top=0.95)
    blob(m, "body", (0, 30.2, -1.6), (9.4, 3.4, 6.0), FUR[2:], n=2, top=0.98)
    for sd in (1, -1):
        blob(m, "body", (sd * 4.4, 25.4, 6.9), (4.4, 3.6, 1.8), SKIN, n=3)                                     # pecs
    blob(m, "body", (0, 18.8, 6.4), (5.2, 3.4, 1.8), SKIN, n=2)                                                 # belly
    # arms: long and huge, fur tufts at the elbows, gold rings, knuckles on the ground
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 14
        blob(m, arm, (x - sd * 0.6, 28.8, 0.4), (5.0, 4.8, 5.2), FUR[1:], n=4)
        taper(m, arm, (x + sd * 0.2, 27.0, 0.6), (x + sd * 2.0, 16.6, 2.4), 4.2, 3.6, FUR, n=3, bright=lambda t: 0.95 - t * 0.4)
        ring(m, arm, x + sd * 1.1, 22.0, 1.5, 4.25, 4.25, 1.6, "gold_block", round_=0.66)
        for i, (dy, dx) in enumerate(((0.8, -0.3), (0, 0.3), (-0.8, -0.3))):
            slab(m, arm, x + sd * (1.1 + dx * 0.0) + dx, 22.0 + dy, 1.5 + 4.1, 1.0, 0.6, 0.3, "light_blue_concrete", rot=(0, 0, 30 if i % 2 else -30), origin=(x + sd * 1.1 + dx, 22.0 + dy, 5.6))
            m.cubes[-1]["l"] = True
        taper(m, arm, (x + sd * 2.0, 16.6, 2.4), (x + sd * 2.4, 5.0, 4.2), 3.8, 4.4, FUR, n=3, bright=lambda t: 0.7 - t * 0.45)
        taper(m, arm, (x + sd * 2.6, 17.2, -0.6), (x + sd * 3.4, 14.2, -3.0), 1.6, 0.4, FUR[2:], n=1, flat=0.6)   # elbow tuft
        blob(m, arm, (x + sd * 2.4, 2.6, 4.8), (3.6, 2.6, 4.0), SKIN, n=3, light=lambda u: 0.1 + (u + 1) * 0.3)
        knuckles(m, arm, x + sd * 2.4, 1.2, 8.2, w=1.5, gap=1.8, block="gray_terracotta")
    # head: peaked skull, heavy brow, glowing eyes, wide flat nose
    blob(m, "head", (0, 31.6, 6.4), (5.6, 5.0, 5.2), FUR, n=5, bottom=-0.6, top=0.95)
    blob(m, "head", (0, 36.0, 4.8), (3.4, 2.0, 3.8), FUR[2:], n=2, bottom=-0.5)                                   # crest
    blob(m, "head", (0, 30.8, 9.6), (4.2, 3.6, 2.6), FACE, n=4, bottom=-0.9, top=0.8)                              # bare face
    chain(m, "head", [(-4.6, 33.4, 10.0), (-1.8, 34.0, 11.4), (1.8, 34.0, 11.4), (4.6, 33.4, 10.0)], 1.3, 1.3, ["black_terracotta", "gray_terracotta"])
    for sd in (1, -1):
        slab(m, "head", sd * 2.0, 32.4, 11.75, 1.8, 1.0, 0.4, "black_concrete")
        slab(m, "head", sd * 2.0, 32.4, 11.95, 1.0, 0.7, 0.2, "light_blue_concrete")
        m.cubes[-1]["l"] = True
        slab(m, "head", sd * 5.6, 31.4, 5.8, 0.8, 1.8, 1.6, "gray_terracotta")                                       # ears
    blob(m, "head", (0, 30.6, 12.0), (2.2, 1.2, 1.0), ["black_terracotta", "gray_terracotta"], n=2)              # flat nose
    for sd in (1, -1):
        slab(m, "head", sd * 0.9, 30.2, 12.95, 0.8, 0.6, 0.2, "black_concrete")
    # jaw: a jutting muzzle with fangs
    blob(m, "jaw", (0, 28.2, 9.6), (4.4, 2.0, 3.2), FACE, n=3, bottom=-1.0, top=0.7)
    slab(m, "jaw", 0, 29.0, 12.45, 5.6, 0.5, 0.4, "black_terracotta")
    for sd in (1, -1):
        taper(m, "jaw", (sd * 2.0, 28.8, 12.2), (sd * 2.1, 30.2, 12.5), 0.5, 0.25, ["white_concrete", "bone_block"], n=1)
    # the chieftain's band: gold with four feathers
    ring(m, "crown", 0, 35.0, 5.6, 5.5, 5.2, 1.3, "gold_block", round_=0.7)
    for i, (x, c) in enumerate(((-3.0, "red_wool"), (-1.0, "yellow_wool"), (1.0, "lime_wool"), (3.0, "light_blue_wool"))):
        taper(m, "crown", (x, 35.6, 1.4), (x * 1.6, 42.4 - abs(x) * 0.5, -0.6), 0.9, 0.35, ["black_terracotta", c, c, "white_wool"], n=2, flat=0.35,
              bright=lambda t: 0.3 + t * 0.7)
    slab(m, "crown", 0, 35.0, 10.95, 1.6, 1.6, 0.4, "light_blue_concrete")
    m.cubes[-1]["l"] = True
    m.bend = -12
    standard_anims(m, heavy=1.4, extra={"idle": idle_biped(4.0, 14, breath=0.03, extra={"crown": {"rot": wave(2, 3, 2.0)}})})
    m.attacks = {"slam": "slam", "quake": "stomp", "lightning": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the minotaur

@sculpt("gorehorn")
def gorehorn():
    """Gorehorn, champion of the fighting pit, sculpted: a huge minotaur with a dark bull head on a thick
    neck, a long pale muzzle with a gold nose ring, red eyes under a heavy brow and two long pale horns that
    sweep out and forward; a white mane over his shoulders like a cape, crossed leather straps meeting at an
    iron boss, a studded belt with a blue loincloth, shaggy bull legs on black hooves, and a double axe."""
    m = Model("gorehorn", "biped", 1.6)
    m.sculpted = True
    HEAD = ["black_terracotta", "brown_terracotta", "brown_terracotta", "brown_concrete"]
    SKIN = ["brown_terracotta", "brown_concrete", "brown_concrete", "packed_mud"]
    MANE = ["light_gray_wool", "white_concrete", "white_wool", "white_wool"]
    HORN = ["gray_terracotta", "light_gray_terracotta", "white_terracotta", "bone_block", "bone_block"]
    LEA = ["black_terracotta", "brown_terracotta", "brown_concrete"]
    BLUE = ["blue_terracotta", "blue_terracotta", "blue_concrete"]
    humanoid(m, hip=14, legx=5, neck=33, shoulder=32, armx=12.5, jaw=(0, 34.6, 7))
    m.bone("axe", "armR", (-13.6, 10, 3))
    m.bone("cloth", "hips", (0, 14, 5.5))
    m.hold = {"axe": 18}
    # shaggy bull legs on black split hooves
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 5.2
        taper(m, leg, (x, 14.6, 0), (x + sd * 0.4, 7.0, -0.6), 3.9, 2.8, HEAD, n=3, bright=lambda t: 0.9 - t * 0.5)
        taper(m, leg, (x + sd * 0.4, 7.0, -0.6), (x + sd * 0.6, 2.6, 0.6), 2.5, 2.0, HEAD, n=2, bright=lambda t: 0.45 - t * 0.3)
        ring(m, leg, x + sd * 0.6, 3.2, 0.5, 2.6, 2.6, 1.2, "brown_concrete", round_=0.66)                          # fetlock tuft
        blob(m, leg, (x + sd * 0.6, 1.2, 1.2), (2.4, 1.2, 2.9), ["black_terracotta", "gray_terracotta"], n=2, bottom=-1.0, top=0.9)
        slab(m, leg, x + sd * 0.6, 1.0, 3.95, 0.3, 1.8, 1.0, "black_concrete")                                       # split hoof
    # torso: broad chest tapering to the waist
    blob(m, "body", (0, 19.6, 0.8), (7.0, 4.4, 5.4), SKIN, n=3, bottom=-0.9, top=0.8, light=lambda u: 0.2 + (u + 1) * 0.3)
    blob(m, "body", (0, 26.6, 0.6), (10.0, 6.4, 6.6), SKIN, n=5, bottom=-0.75, top=0.95)
    for sd in (1, -1):
        blob(m, "body", (sd * 4.0, 27.6, 5.8), (3.8, 2.6, 1.6), SKIN[1:], n=2)
        # crossed straps that meet at the iron boss
        chain(m, "body", [(sd * 7.6, 31.0, 4.2), (sd * 3.4, 27.0, 7.6), (0, 24.6, 7.8), (-sd * 3.6, 21.0, 6.8), (-sd * 6.2, 17.6, 4.8)], 0.9, 0.9, LEA[1:], flat=0.5)
    blob(m, "body", (0, 24.6, 8.2), (1.7, 1.7, 0.8), ["polished_blackstone", "iron_block", "iron_block"], n=2)
    slab(m, "body", 0, 24.6, 9.05, 0.6, 0.6, 0.2, "polished_blackstone")
    # the white mane over the shoulders, hanging down the back like a cape
    blob(m, "body", (0, 31.4, -0.8), (10.6, 3.6, 7.6), MANE, n=3, bottom=-0.6, top=0.98)
    for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5):
        taper(m, "body", (x, 30.0, -6.4 + abs(x) * 0.12), (x * 1.06, 21.0 + abs(x) * 0.4, -7.2 + abs(x) * 0.1), 1.9, 0.6, MANE, n=2, flat=0.55, bright=lambda t: 0.9 - t * 0.6)
    # studded belt and the blue loincloth
    ring(m, "hips", 0, 15.6, 0.8, 7.6, 6.0, 2.2, "brown_terracotta", round_=0.72)
    for x, z in ((-5.0, 5.4), (-2.5, 6.4), (2.5, 6.4), (5.0, 5.4)):
        slab(m, "hips", x, 15.6, z + 0.2, 0.7, 0.7, 0.5, "iron_block")
    slab(m, "hips", 0, 15.6, 6.95, 2.4, 2.4, 0.5, "iron_block")
    taper(m, "cloth", (0, 14.6, 6.2), (0, 6.0, 7.0), 3.8, 3.0, BLUE, n=3, flat=0.25, bright=lambda t: 0.9 - t * 0.7)
    slab(m, "cloth", 0, 5.9, 7.0, 5.6, 0.5, 0.8, "gold_block")
    taper(m, "hips", (0, 14.6, -4.6), (0, 7.4, -5.6), 4.0, 3.2, BLUE, n=2, flat=0.25)
    # arms: round shoulders, leather bracers, fists
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 12.5
        blob(m, arm, (x - sd * 0.4, 30.0, 0.2), (4.2, 3.8, 4.2), SKIN[1:], n=3)
        taper(m, arm, (x + sd * 0.2, 28.4, 0.3), (x + sd * 1.0, 19.6, 1.2), 3.3, 2.8, SKIN, n=3, bright=lambda t: 0.9 - t * 0.4)
        blob(m, arm, (x + sd * 0.4, 25.4, 2.2), (2.4, 2.8, 2.0), SKIN[2:], n=2)                                         # biceps
        taper(m, arm, (x + sd * 1.0, 19.6, 1.2), (x + sd * 1.2, 11.6, 2.6), 2.9, 3.1, SKIN, n=3, bright=lambda t: 0.6 - t * 0.35)
        ring(m, arm, x + sd * 1.15, 13.6, 2.3, 3.3, 3.3, 3.0, "brown_terracotta", round_=0.66)
        ring(m, arm, x + sd * 1.15, 15.0, 2.3, 3.45, 3.45, 0.5, "iron_block", round_=0.66)
        blob(m, arm, (x + sd * 1.3, 9.8, 3.0), (3.0, 2.6, 3.0), SKIN[1:], n=3)
    # the bull head on a thick neck
    blob(m, "head", (0, 34.4, 2.4), (5.0, 3.2, 4.6), HEAD, n=3)                                                          # neck
    blob(m, "head", (0, 38.4, 4.4), (5.4, 4.8, 5.0), HEAD, n=5, bottom=-0.7, top=0.97)
    blob(m, "head", (0, 36.2, 9.4), (3.8, 2.9, 3.8), ["brown_terracotta", "brown_concrete", "packed_mud"], n=3)        # muzzle
    blob(m, "head", (0, 35.6, 12.6), (2.9, 2.2, 1.4), ["black_terracotta", "gray_terracotta"], n=2)                    # nose
    for sd in (1, -1):
        slab(m, "head", sd * 1.1, 35.8, 13.85, 0.8, 0.7, 0.3, "black_concrete")
    for p, q in (((-1.0, 35.0, 13.6), (-0.8, 33.8, 13.8)), ((0.8, 33.8, 13.8), (1.0, 35.0, 13.6))):
        taper(m, "head", p, q, 0.3, 0.3, ["gold_block"], n=1)
    slab(m, "head", 0, 33.7, 13.8, 1.8, 0.45, 0.45, "gold_block")                                                     # nose ring
    chain(m, "head", [(-4.6, 40.2, 7.8), (-1.8, 40.8, 9.0), (1.8, 40.8, 9.0), (4.6, 40.2, 7.8)], 1.1, 1.1, HEAD[1:])  # brow
    for sd in (1, -1):
        slab(m, "head", sd * 2.8, 39.2, 9.1, 1.6, 0.9, 0.4, "black_concrete")
        slab(m, "head", sd * 2.7, 39.2, 9.35, 0.9, 0.6, 0.2, "red_concrete")
        m.cubes[-1]["l"] = True
        slab(m, "head", sd * 2.9, 39.9, 9.3, 2.4, 0.6, 0.6, "brown_terracotta", rot=(0, 0, -18 * sd))               # scowl
        taper(m, "head", (sd * 4.4, 38.6, 3.0), (sd * 7.6, 37.6, 2.4), 1.2, 0.4, HEAD[1:], n=2, flat=0.4)         # ears
        ring(m, "head", sd * 4.4, 41.0, 4.2, 1.7, 1.7, 1.0, "gray_terracotta")
        chain(m, "head", [(sd * 4.4, 41.2, 4.2), (sd * 8.2, 42.0, 4.0), (sd * 10.6, 44.6, 5.0), (sd * 10.8, 47.6, 7.2)], 1.6, 0.35, HORN,
              bright=lambda t: 0.1 + t * 0.85)
    blob(m, "jaw", (0, 33.6, 8.8), (3.2, 1.2, 3.6), ["black_terracotta", "brown_terracotta", "brown_concrete"], n=2)
    # the double axe: a wrapped haft and two crescent iron heads
    chain(m, "axe", [(-14.0, 0.5, 4.0), (-14.0, 12.0, 4.0), (-14.0, 27.0, 4.0)], 0.65, 0.6, ["dark_oak_planks", "stripped_dark_oak_log"])
    for y in (8.6, 10.6):
        ring(m, "axe", -14.0, y, 4.0, 0.75, 0.75, 1.2, "brown_terracotta")
    ring(m, "axe", -14.0, 23.4, 4.0, 1.0, 1.0, 4.2, "polished_blackstone")
    for sz in (1, -1):
        for dy, h, ln in ((0, 3.0, 5.0), (2.4, 1.8, 6.0), (-2.4, 1.8, 6.0), (3.9, 1.2, 6.8), (-3.9, 1.2, 6.8)):
            z0, z1 = 4.0 + sz * 0.9, 4.0 + sz * ln
            slab(m, "axe", -14.0, 23.4 + dy, (z0 + z1) / 2, 0.7, h, abs(z1 - z0), "iron_block")
        slab(m, "axe", -14.0, 23.4, 4.0 + sz * 6.5, 0.5, 8.6, 0.7, "white_concrete")                               # bright edge
    taper(m, "axe", (-14.0, 27.0, 4.0), (-14.0, 30.0, 4.0), 0.7, 0.2, ["iron_block"], n=1)
    m.bend = -28
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(4.0, 16, breath=0.03, extra={"cloth": {"rot": wave(0, 5, 2.0, base=(3, 0, 0))}})})
    m.attacks = {"charge": "lunge", "slam": "slam", "quake": "stomp", "roar": "roar"}
    m.melee = "swipe"
    return m
