"""The 24 world boss models. Run gen_models.py to write src/main/resources/worldboss-models.json."""
from build import Model

MODELS = []
def model(fn):
    MODELS.append(fn)
    return fn

def biped(m, hip, legx, neck, shoulder, armx):
    """Standard humanoid bones; pivots only, cubes are added by each boss."""
    m.bone("hips", "root", (0, hip, 0))
    m.mbone("legL", "hips", (legx, hip, 0))
    m.bone("body", "hips", (0, hip + 1, 0))
    m.bone("head", "body", (0, neck, 0))
    m.mbone("armL", "body", (armx, shoulder, 0))

def horn(m, bone, block, base, segs, rot0, bend, size0, shrink=0.8, light=False):
    """A curved horn or spike: each segment continues from the tip of the last and turns by bend."""
    import math
    x, y, z = base
    rx, ry, rz = rot0
    s = size0
    for i in range(segs):
        L = s * 2.2
        # direction of a cube's local +y after its rotation (Z*Y*X)
        a, b, c = math.radians(rx), math.radians(ry), math.radians(rz)
        dx, dy, dz = 0.0, 1.0, 0.0
        dy, dz = dy * math.cos(a) - dz * math.sin(a), dy * math.sin(a) + dz * math.cos(a)
        dx, dz = dx * math.cos(b) + dz * math.sin(b), -dx * math.sin(b) + dz * math.cos(b)
        dx, dy = dx * math.cos(c) - dy * math.sin(c), dx * math.sin(c) + dy * math.cos(c)
        cx, cy, cz = x + dx * L / 2, y + dy * L / 2, z + dz * L / 2
        m.c(bone, block, (cx, cy, cz), (s, L, s), (rx, ry, rz), (cx, cy, cz), light)
        x, y, z = x + dx * L * 0.9, y + dy * L * 0.9, z + dz * L * 0.9
        rx, ry, rz = rx + bend[0], ry + bend[1], rz + bend[2]
        s *= shrink

def mhorn(m, bone, block, base, segs, rot0, bend, size0, shrink=0.8, light=False):
    horn(m, bone, block, base, segs, rot0, bend, size0, shrink, light)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone
    horn(m, rb, block, (-base[0], base[1], base[2]), segs, (rot0[0], -rot0[1], -rot0[2]), (bend[0], -bend[1], -bend[2]), size0, shrink, light)


def dirof(rot):
    import math
    a, b, c = (math.radians(v) for v in rot)
    dx, dy, dz = 0.0, 1.0, 0.0
    dy, dz = dy * math.cos(a) - dz * math.sin(a), dy * math.sin(a) + dz * math.cos(a)
    dx, dz = dx * math.cos(b) + dz * math.sin(b), -dx * math.sin(b) + dz * math.cos(b)
    dx, dy = dx * math.cos(c) - dy * math.sin(c), dx * math.sin(c) + dy * math.cos(c)
    return dx, dy, dz

def limb(m, bone, block, base, segs, light=False, joint=None):
    """A chain of rotated pieces: segs = [(length, thickness, (rx, ry, rz)), ...] with absolute rotations.
    Each piece starts where the last ended. joint adds a small knob block at each joint. Returns the tip."""
    x, y, z = base
    for i, seg in enumerate(segs):
        L, s, rot = seg[0], seg[1], seg[2]
        blk = seg[3] if len(seg) > 3 else block
        dx, dy, dz = dirof(rot)
        cx, cy, cz = x + dx * L / 2, y + dy * L / 2, z + dz * L / 2
        m.c(bone, blk, (cx, cy, cz), (s, L, s), rot, (cx, cy, cz), light)
        x, y, z = x + dx * L, y + dy * L, z + dz * L
        if joint and i < len(segs) - 1:
            m.c(bone, joint, (x, y, z), (s * 1.25, s * 1.25, s * 1.25), rot, (x, y, z))
    return x, y, z

def mlimb(m, bone, block, base, segs, light=False, joint=None):
    limb(m, bone, block, base, segs, light, joint)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone[:-2] + "R" + bone[-1] if bone[-2:-1] == "L" else bone
    limb(m, rb, block, (-base[0], base[1], base[2]), [(s[0], s[1], (s[2][0], -s[2][1], -s[2][2])) + tuple(s[3:]) for s in segs], light, joint)

def taper(m, bone, block, x, y0, z, sizes, step, light=False):
    """Stacked boxes, one per (width, depth), each step high: robes, cones, tails."""
    y = y0
    for w, d in sizes:
        m.c(bone, block, (x, y + step / 2, z), (w, step, d), light=light)
        y += step

# ---------------------------------------------------------------------------------------------- bipeds

@model
def gravelord():
    m = Model("gravelord", "biped", 1.75)
    biped(m, hip=21, legx=3.5, neck=37, shoulder=35, armx=8)
    m.bone("jaw", "head", (0, 39, 3))
    m.bone("cape", "body", (0, 36, -4))
    m.bone("staff", "armR", (-9.5, 17, 2))
    # robe skirt, split in two so it sways with the walk
    for s, bone in ((1, "legL"), (-1, "legR")):
        m.box(bone, "purple_wool", (0, 3, -4.5), (7 * s, 21, 4.5))
        m.box(bone, "purple_wool", (0.5 * s, 0.8, -5), (7.6 * s, 4, 5))
        for i, (zz, hh) in enumerate(((-4.2, 2.2), (-1.4, 1.2), (1.6, 2.6), (4.2, 1.6))):
            m.c(bone, "black_wool", (6.4 * s, 0.8 - hh / 2 + 0.6, zz), (1.4, hh, 1.6))
        m.c(bone, "gold_block", (3.5 * s, 4.4, 4.9), (7, 0.8, 0.4))
        for zz in (2.5, 4.4):
            m.c(bone, "bone_block", (2.6 * s, 0.6, 5 + zz - 2), (1, 1.2, 2.8))
        m.c(bone, "bone_block", (4.4 * s, 0.6, 5.6), (1, 1.2, 2.2))
    m.c("hips", "purple_terracotta", (0, 12, 4.9), (4, 17, 0.8))
    m.c("hips", "gold_block", (0, 4.2, 5.2), (4.4, 1.4, 0.6))
    m.c("hips", "crying_obsidian", (0, 15, 5.4), (2, 2, 0.6), light=True)
    m.c("hips", "polished_blackstone", (0, 21.5, 0), (13, 2.4, 9.4))
    m.c("hips", "gold_block", (0, 21.5, 4.8), (3, 3, 0.8))
    # spine, ribs and the soul lantern heart
    m.c("body", "bone_block", (0, 29, -2.2), (2.4, 15, 2.4))
    for y in (25.5, 28.5, 31.5, 34.2):
        w = 5.6 if y < 33 else 6.4
        m.m("body", "bone_block", (w - 0.6, y, 0.2), (1.2, 1.2, 5))
        m.m("body", "bone_block", (w / 2 + 0.2, y, 2.9), (w - 1.6, 1.2, 1.2))
    m.c("body", "soul_lantern", (0, 29.5, 0.6), (6.5, 6.5, 6.5), light=True)
    m.c("body", "bone_block", (0, 31, 3.1), (1.2, 7, 1.2))
    # mantle and pauldrons
    m.c("body", "purple_wool", (0, 35.5, -0.5), (15, 3, 9))
    m.c("body", "gold_block", (0, 34.4, 4.1), (15.4, 0.8, 0.6))
    m.c("body", "black_wool", (0, 37.4, -1.6), (11, 1.6, 7))
    m.c("armL", "polished_blackstone_bricks", (9.6, 36.2, 0), (6.4, 3.6, 7.4), (0, 0, -14))
    m.c("armL", "gold_block", (9.8, 34.3, 0), (6.6, 0.8, 7.8), (0, 0, -14))
    horn(m, "armL", "bone_block", (10.4, 37.4, -1.5), 3, (0, 0, -20), (0, 0, -12), 1.4)
    horn(m, "armL", "bone_block", (10.0, 37.4, 1.8), 2, (8, 0, -16), (0, 0, -10), 1.1)
    m.c("armR", "polished_blackstone_bricks", (-9.6, 36.2, 0), (6.4, 3.6, 7.4), (0, 0, 14))
    m.c("armR", "gold_block", (-9.8, 34.3, 0), (6.6, 0.8, 7.8), (0, 0, 14))
    horn(m, "armR", "bone_block", (-10.4, 37.4, -1.5), 3, (0, 0, 20), (0, 0, 12), 1.4)
    horn(m, "armR", "bone_block", (-10.0, 37.4, 1.8), 2, (8, 0, 16), (0, 0, 10), 1.1)
    # bony arms with ragged sleeves
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "purple_wool", (9 * s, 31.5, 0), (4.4, 5, 4.4))
        m.c(a, "black_wool", (9 * s, 28.6, 0.4), (3.4, 1.4, 3.6))
        m.c(a, "bone_block", (9 * s, 26.5, 0), (1.8, 9, 1.8))
        m.c(a, "bone_block", (9 * s, 19.5, 1.2), (1.6, 7, 1.6), (-12, 0, 0), (9 * s, 22.5, 0.6))
        m.c(a, "calcite", (9 * s, 16.4, 2), (2.8, 2.4, 2.8))
        for k in (-0.9, 0, 0.9):
            m.c(a, "bone_block", (9 * s + k, 14.6, 2.8), (0.6, 2, 0.6), (18, 0, 0))
    # staff: dark wood shaft, gold bands, crystal head with a burning orb
    m.c("staff", "dark_oak_log", (-9.5, 22, 2.2), (1.8, 38, 1.8))
    for y in (8, 17, 31, 38):
        m.c("staff", "gold_block", (-9.5, y, 2.2), (2.4, 0.9, 2.4))
    for ang in (0, 90, 180, 270):
        m.c("staff", "polished_blackstone", (-9.5, 42.5, 2.2), (0.9, 6, 0.9), (0, ang, 22), (-9.5, 41, 2.2))
    m.c("staff", "crying_obsidian", (-9.5, 44, 2.2), (3.4, 3.4, 3.4), (45, 45, 0), light=True)
    m.c("staff", "amethyst_block", (-9.5, 47.8, 2.2), (1.6, 4, 1.6), (0, 45, 0), light=True)
    m.c("staff", "amethyst_block", (-8.2, 46.2, 2.2), (1.1, 2.6, 1.1), (0, 0, -30), light=True)
    m.c("staff", "amethyst_block", (-10.8, 46.4, 2.6), (1.1, 2.4, 1.1), (0, 0, 30), light=True)
    # hood, skull, jaw, crown and horns
    m.c("head", "black_wool", (0, 42, -1.4), (9.6, 9.6, 6.6))
    m.m("head", "black_wool", (4.4, 41, 2), (0.9, 7.6, 3.4))
    m.c("head", "calcite", (0, 42.6, 0.9), (7, 6.4, 7))
    m.c("head", "calcite", (0, 46, 0.5), (6.2, 1.2, 6))
    m.m("head", "black_concrete", (1.75, 42.8, 4.45), (2, 2.2, 0.3))
    m.m("head", "light_blue_concrete", (1.75, 42.6, 4.62), (0.8, 0.8, 0.2), light=True)
    m.c("head", "black_concrete", (0, 41, 4.45), (1, 1.4, 0.3))
    m.c("head", "white_concrete", (0, 39.7, 4.2), (5, 0.9, 0.6))
    m.c("jaw", "calcite", (0, 38.4, 1.8), (5.8, 1.6, 5.2))
    m.c("jaw", "white_concrete", (0, 39.4, 4.1), (4.8, 0.8, 0.5))
    for x in (-3.3, -1.1, 1.1, 3.3):
        m.c("head", "gold_block", (x, 47, 3.8), (1, 2.6 if abs(x) < 2 else 1.8, 0.8))
    m.c("head", "gold_block", (0, 46.3, 0.6), (8, 0.9, 7.6))
    m.c("head", "crying_obsidian", (0, 47.4, 4.3), (1.4, 1.4, 0.5), (0, 0, 45), light=True)
    mhorn(m, "head", "polished_blackstone", (3.6, 45, -0.5), 4, (-20, 0, -55), (-6, 0, 28), 2.0, 0.78)
    # tattered cape
    m.c("cape", "black_wool", (0, 21, -5), (13, 30, 0.8), (6, 0, 0), (0, 36, -4.6))
    for i, x in enumerate((-5, -2.4, 0.2, 2.8, 5.2)):
        m.c("cape", "black_wool", (x, 5.2 - (i % 2) * 1.6, -6.6), (2.2, 3 + (i % 2) * 2, 0.8), (6, 0, 0), (0, 36, -4.6))
    m.c("cape", "purple_wool", (0, 34, -4.9), (14, 3, 1), (6, 0, 0), (0, 36, -4.6))
    m.attacks = {"minions": "cast", "darkness": "roar", "shockwave": "slam", "blink": "lunge"}
    m.melee = "swipe"
    m.spawn = {"style": "rise", "particle": "SOUL_FIRE_FLAME", "sound": "ENTITY_WITHER_SPAWN"}
    m.death = {"style": "crumble", "swap": "", "particle": "SOUL", "sound": "ENTITY_WITHER_DEATH"}
    return m

# ---------------------------------------------------------------------------------------------- quadrupeds

def quad(m, body_y, legx, legz_front, legz_back, neck_y, neck_z):
    m.bone("body", "root", (0, body_y, 0))
    m.mbone("legFL", "body", (legx, body_y, legz_front))
    m.mbone("legBL", "body", (legx, body_y, legz_back))
    m.bone("head", "body", (0, neck_y, neck_z))
    m.bone("jaw", "head", (0, neck_y - 3, neck_z + 4))
    m.bone("tail", "body", (0, body_y + 4, legz_back - 6))

@model
def ironhide_behemoth():
    m = Model("ironhide_behemoth", "quad", 1.5)
    quad(m, body_y=20, legx=9, legz_front=11, legz_back=-13, neck_y=24, neck_z=20)
    hide, hide2, belly, plate = "brown_terracotta", "mud_bricks", "packed_mud", "polished_deepslate"
    # a huge shoulder hump in front, a smaller rump behind: a charging war beast
    m.c("body", hide, (0, 29, 10), (22, 20, 16))
    m.c("body", hide, (0, 26, -4), (19, 16, 14))
    m.c("body", hide, (0, 25, -15), (17, 14, 10))
    m.c("body", belly, (0, 18.6, 2), (16, 3, 26))
    m.c("body", hide2, (0, 38, 11), (16, 3, 12))
    # riveted deepslate plates on the back and flanks, spikes along the spine
    for z, w in ((13, 20), (5, 19), (-4, 18), (-12, 16)):
        m.c("body", plate, (0, 39.4 if z > 8 else 34.4, z), (w, 1.6, 7.4))
        m.m("body", plate, (w / 2 + 0.6, 30 if z > 8 else 27, z), (1.4, 9, 7.4), (0, 0, -6))
        m.m("body", "iron_block", (w / 2 + 1.35, 33 if z > 8 else 30, z + 2.6), (0.4, 1, 1))
        m.c("body", "iron_block", (0, (41.6 if z > 8 else 36.6), z), (2.4, 3, 2.4), (25, 45, 0))
    m.m("body", "chain", (10.6, 23, 2), (0.6, 0.6, 22))
    # war saddle with drums and a banner
    m.c("body", "red_wool", (0, 41, 4), (14, 1, 12))
    m.m("body", "gold_block", (7.2, 40.4, 4), (0.6, 2.4, 12.4))
    m.c("body", "dark_oak_planks", (0, 43, 4), (9, 3, 8))
    m.m("body", "note_block", (6.6, 43.6, 6), (3.4, 4, 3.4))
    m.m("body", "white_wool", (6.6, 45.7, 6), (3, 0.3, 3))
    m.c("body", "dark_oak_log", (0, 51, 0), (1.2, 18, 1.2))
    m.c("body", "red_wool", (2.8, 56, 0), (5, 7, 0.4))
    m.c("body", "black_wool", (2.8, 56, 0), (2, 2, 0.5))
    m.c("body", "gold_block", (0, 60.6, 0), (1.8, 1.4, 1.8))
    # pillar legs with armored knees and big toes
    for leg, z, top in (("legFL", 11, 20), ("legBL", -13, 19)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, hide, (9 * s, 14, z), (8, 12, 8))
            m.c(b, hide2, (9 * s, 5, z), (7, 8, 7))
            m.c(b, plate, (9 * s, 11, z + 4.2), (6.4, 6, 1))
            m.c(b, "iron_block", (9 * s, 11, z + 4.8), (1.6, 1.6, 0.6), (0, 0, 45))
            m.c(b, belly, (9 * s, 1, z + 0.6), (8.4, 2, 8.6))
            for dx in (-2.6, 0, 2.6):
                m.c(b, "bone_block", (9 * s + dx, 0.9, z + 5.2), (1.6, 1.8, 1.6))
    # head hangs low in front of the hump: brow plate, nose horn, sweeping horns, tusks
    m.c("head", hide, (0, 22, 25), (14, 13, 12))
    m.c("head", belly, (0, 18.4, 32.4), (10, 7, 4))
    m.c("head", plate, (0, 29.2, 25.4), (15, 2, 11))
    m.c("head", plate, (0, 26, 31.4), (11, 5, 1.2))
    m.c("head", "iron_block", (0, 26, 32.2), (1.4, 1.4, 0.6), (0, 0, 45))
    m.m("head", "black_concrete", (4.8, 23.6, 31.1), (2.4, 1.4, 0.3))
    m.m("head", "red_concrete", (4.8, 23.6, 31.25), (1.2, 0.8, 0.3), light=True)
    m.m("head", "black_concrete", (2.2, 18.6, 34.5), (1.6, 1.6, 0.2))
    limb(m, "head", "bone_block", (0, 21.4, 34), [(4, 2.6, (60, 0, 0)), (3, 1.8, (35, 0, 0)), (2, 1, (10, 0, 0))])
    mhorn(m, "head", "bone_block", (7, 27, 26), 5, (-35, 0, -65), (16, 0, 18), 3.0, 0.8)
    m.c("jaw", belly, (0, 15, 29), (11, 3, 9))
    mhorn(m, "jaw", "bone_block", (4.2, 15.6, 32.6), 2, (30, 0, -20), (-30, 0, 5), 1.5)
    m.c("head", "red_wool", (0, 31, 20), (10, 2, 6))
    m.c("head", "gold_block", (0, 31, 23.2), (2, 2, 0.4))
    # short tail with a spiked club
    m.c("tail", hide, (0, 22.5, -22), (4, 4, 8), (-30, 0, 0), (0, 24, -19))
    m.c("tail", plate, (0, 18, -26.5), (5, 5, 5), (-30, 45, 0), (0, 18, -26.5))
    for r in ((0, 0, 90), (90, 0, 0), (0, 0, 0)):
        m.c("tail", "iron_block", (0, 18, -26.5), (1, 7.4, 1), r, (0, 18, -26.5))
    m.attacks = {"leap": "pounce", "shockwave": "rear", "roar": "howl", "quake": "charge"}
    m.melee = "toss"
    m.spawn = {"style": "drop", "particle": "EXPLOSION", "sound": "ENTITY_RAVAGER_ROAR"}
    m.death = {"style": "collapse", "swap": "", "particle": "BLOCK", "sound": "ENTITY_RAVAGER_DEATH"}
    return m
