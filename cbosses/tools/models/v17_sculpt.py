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


# ------------------------------------------------------------------------------------------------ the ogre

@sculpt("brewgut")
def brewgut():
    """The tavern ogre, sculpted: a heavy round head sunk forward between hunched shoulders, a jutting
    underbite with two curved tusks, a thick brow over small deep eyes, a broad flat nose and pointed ears;
    a barrel belly in a grubby white shirt under an open leather vest, a thick belt with a brass buckle, a
    ragged apron, short thick legs in patched trousers and heavy boots, puffed sleeves, huge green forearms
    and fists, and a wooden tankard."""
    m = Model("brewgut", "biped", 1.6)
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
