"""Seasonal world bosses: two per season, built to be fun to look at and to fight. Chunky silhouettes,
exaggerated faces and a joke each, in the spirit of the hand-made models clarx shared."""
from models import *
import math

def blob(m, bone, block, center, size, r=1.5, rot=None, origin=None, light=False):
    """A rounded box from three crossed boxes: reads as soft instead of a hard cube."""
    x, y, z = center
    sx, sy, sz = size
    r = min(r, sx / 3, sy / 3, sz / 3)
    m.c(bone, block, center, (sx, sy - 2 * r, sz - 2 * r), rot, origin, light)
    m.c(bone, block, center, (sx - 2 * r, sy, sz - 2 * r), rot, origin, light)
    m.c(bone, block, center, (sx - 2 * r, sy - 2 * r, sz), rot, origin, light)

def ring(m, bone, block, y, rad, n, size, z0=0, x0=0, light=False, tilt=0):
    for k in range(n):
        a = k * 360 / n
        m.c(bone, block, (x0 + rad * math.cos(math.radians(a)), y, z0 + rad * math.sin(math.radians(a))), size, (tilt, -a, 0), light=light)

# ================================================================================================= HALLOWEEN

@model
def headless_horseman():
    m = Model("headless_horseman", "quad", 1.5)
    quad(m, body_y=26, legx=4.8, legz_front=10, legz_back=-10, neck_y=36, neck_z=12)
    m.bone("rider", "body", (0, 38, -1))
    m.bone("riderArmR", "rider", (-6, 52, -1))
    m.bone("riderArmL", "rider", (6, 52, -1))
    horse, horse2, bone, fl, fl2 = "black_terracotta", "gray_terracotta", "bone_block", "orange_stained_glass", "yellow_stained_glass"
    # nightmare horse: a deep chest, ribs showing through, a ragged purple blanket with orange trim
    blob(m, "body", horse, (0, 31, 3), (12, 13, 15), 2)
    blob(m, "body", horse, (0, 31, -8), (11, 11, 11), 2)
    for z in (-3, 0, 3, 6):
        m.m("body", bone, (6.15, 30.4, z), (0.5, 7, 1.2))
    m.c("body", "purple_wool", (0, 37.6, -2), (12.4, 1, 14))
    for z in (-7, -3, 1, 5):
        m.m("body", "purple_wool", (6.3, 34 - (z % 2), z), (0.5, 7 - abs(z) * 0.2, 3.6))
    m.m("body", "orange_wool", (6.45, 30.6, -1), (0.4, 0.8, 14))
    m.c("body", "dark_oak_planks", (0, 38.6, -2), (7, 1.6, 8))
    m.c("body", "dark_oak_planks", (0, 39.8, 1.6), (6, 1.6, 1.4))
    # a trick-or-treat sack tied to the saddle, sweets spilling out
    m.c("body", "orange_wool", (-7.6, 31, -9), (3.4, 5, 4))
    m.c("body", "black_wool", (-7.6, 33.8, -9), (2, 1, 2))
    for k, c in enumerate(("red_concrete", "lime_concrete", "yellow_concrete")):
        m.c("body", c, (-7.8 + k * 0.6, 34.8 + k * 0.3, -9.4 + k), (1, 1, 1), (0, 30 * k, 45))
    # legs: thick thighs, bony shins, burning hooves
    for leg, z in (("legFL", 10), ("legBL", -10)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            blob(m, b, horse, (4.8 * s, 21.6, z), (4.4, 9, 5), 1)
            m.c(b, bone, (4.8 * s, 12.6, z + (0.6 if z > 0 else -0.6)), (2.4, 9, 2.4))
            m.c(b, horse2, (4.8 * s, 16.6, z + (0.6 if z > 0 else -0.6)), (3, 2, 3))
            m.c(b, horse, (4.8 * s, 5.6, z), (3, 4, 3))
            m.c(b, "shroomlight", (4.8 * s, 1.8, z + 0.4), (3.8, 3, 4.2), light=True)
            m.c(b, fl, (4.8 * s, 3.2, z + 0.4), (4.4, 1.6, 4.6), (0, 45, 0), light=True)
    # arched neck with a burning mane, a long skull with a silly overbite grin
    m.c("head", horse, (0, 40, 15), (5.4, 13, 6.4), (-32, 0, 0), (0, 36, 12))
    m.c("head", bone, (0, 46, 22), (5.6, 5.4, 11), (18, 0, 0), (0, 45, 18))
    m.c("head", "calcite", (0, 48, 19), (6, 2, 5.4))
    m.m("head", "black_concrete", (2.5, 47, 20.6), (1.6, 2, 2.4))
    m.m("head", "lime_concrete", (3.05, 47, 21), (0.3, 1, 1), light=True)
    m.m("head", "black_concrete", (1.2, 44.6, 27.4), (1, 1, 0.6), (18, 0, 0), (0, 45, 18))
    for x in (-2, -0.7, 0.7, 2):
        m.c("head", "white_concrete", (x, 42.2, 26.6), (1.1, 1.6, 0.8), (18, 0, 0), (0, 45, 18))
    m.m("head", bone, (2, 50.8, 17.4), (1.2, 3, 1.2), (-10, 0, -12))
    m.c("jaw", bone, (0, 41.4, 23), (4.6, 1.6, 7.4), (18, 0, 0), (0, 43, 19))
    m.c("jaw", "pink_concrete", (0, 40.2, 27.2), (1.6, 1.4, 2.4), (40, 0, 0))
    for i, y in enumerate((49, 46, 43, 40)):
        m.c("head", fl, (0, y + 1.4, 14.4 - i * 0.8), (1.6, 4.4 + i % 2, 3.4), (-32, 0, 0), light=True)
        m.c("head", fl2, (0, y + 2.6, 13.4 - i * 0.8), (1, 2.4, 1.6), (-32, 0, 0), light=True)
    limb(m, "tail", fl, (0, 33, -13), [(5, 2.6, (-150, 0, 0)), (5, 2.2, (-172, 0, 0)), (4, 1.6, (170, 0, 0))], light=True)
    limb(m, "tail", fl2, (0, 32.6, -13.4), [(4, 1.4, (-140, 0, 0)), (4, 1, (-165, 0, 0))], light=True)
    # the rider: a long black coat with orange lining, legs round the horse, no head at all
    for s in (1, -1):
        m.c("rider", "black_wool", (4.2 * s, 39, 1.4), (3.2, 3.2, 7))
        m.c("rider", "black_wool", (6.4 * s, 34, 3.4), (2.6, 8, 2.8))
        m.c("rider", "brown_terracotta", (6.4 * s, 29.4, 4.4), (3, 2.4, 4.4))
        m.c("rider", "gold_block", (6.4 * s, 29.4, 6.7), (1, 1, 0.3))
    blob(m, "rider", "black_wool", (0, 45.6, -1), (9.6, 12, 5.6), 1)
    m.c("rider", "orange_wool", (0, 45, 1.95), (4, 10, 0.4))
    for y in (48, 45, 42):
        m.c("rider", "gold_block", (0, y, 2.25), (0.8, 0.8, 0.3))
    m.c("rider", "brown_terracotta", (0, 40.4, -1), (10, 1.6, 6))
    m.c("rider", "gold_block", (0, 40.4, 2.05), (2, 1.8, 0.4))
    # tall collar standing up round the empty neck, green ghost-fire rising out of it
    m.c("rider", "black_wool", (0, 53, -1), (11, 2, 6.6))
    m.m("rider", "black_wool", (4.6, 55, -1), (1, 3.4, 6), (0, 0, -12))
    m.c("rider", "black_wool", (0, 55, -3.8), (8, 3.4, 1), (12, 0, 0))
    m.c("rider", "orange_wool", (0, 54.6, -3.2), (7, 2.6, 0.3), (12, 0, 0))
    m.c("rider", "red_terracotta", (0, 54.2, -1), (3, 0.6, 3))
    for i, (x, z, h) in enumerate(((0, -1, 6), (-1.4, 0, 4), (1.4, -1.8, 4.6), (0.4, 0.6, 3))):
        m.c("rider", "lime_stained_glass", (x, 54.6 + h / 2, z), (1.6 - i * 0.2, h, 1.6 - i * 0.2), (0, 45 * i, 8 * (i - 1.5)), light=True)
    m.c("rider", "lime_stained_glass", (0.4, 62, -1), (1, 1, 1), (45, 45, 0), light=True)
    # coat tails flapping behind
    m.c("rider", "black_wool", (0, 37, -5.4), (9.6, 16, 0.8), (22, 0, 0), (0, 45, -4))
    for k, x in enumerate((-3.4, 0, 3.4)):
        m.c("rider", "orange_wool" if k == 1 else "black_wool", (x, 28.4 - (k % 2), -9), (3, 3, 0.8), (22, 0, 0), (0, 45, -4))
    # arms in coat sleeves with frilly cuffs
    for s, a in ((1, "riderArmL"), (-1, "riderArmR")):
        blob(m, a, "black_wool", (6.8 * s, 51.4, -1), (4.2, 4, 5), 0.8)
        m.c(a, "black_wool", (6.8 * s, 46.6, -0.4), (3, 7, 3))
        m.c(a, "white_wool", (6.8 * s, 43, 0.6), (3.6, 1.4, 3.6), (-40, 0, 0))
        m.c(a, "light_gray_terracotta", (6.8 * s, 41.4, 2), (2.6, 2.4, 2.6), (-40, 0, 0))
    # his head, tucked under his arm, grinning back at you with a tongue out and a tiny top hat
    blob(m, "riderArmL", "carved_pumpkin[facing=south]", (7.6, 39.6, 5.6), (7.6, 6.6, 7.6), 1)
    m.c("riderArmL", "jack_o_lantern[facing=south]", (7.6, 39.6, 9.45), (5.6, 4.4, 0.2), light=True)
    m.c("riderArmL", "red_concrete", (7.6, 37, 9.6), (2, 2, 0.6), (30, 0, 0))
    m.c("riderArmL", "green_terracotta", (7.6, 43.2, 5), (1, 1.8, 1), (0, 0, 15))
    m.c("riderArmL", "black_wool", (6.2, 43.2, 4.6), (4.4, 0.6, 4.4), (0, 0, -18))
    m.c("riderArmL", "black_wool", (6, 45, 4.6), (2.8, 3, 2.8), (0, 0, -18))
    m.c("riderArmL", "orange_wool", (6.2, 44, 4.6), (2.9, 0.6, 2.9), (0, 0, -18))
    # a scythe: dark shaft, bound grip, a hooked blade with a wicked edge
    m.c("riderArmR", "dark_oak_log", (-7, 47, 3.4), (1.3, 32, 1.3), (-10, 0, 0))
    m.c("riderArmR", "brown_wool", (-7, 42, 2.6), (1.7, 4, 1.7), (-10, 0, 0))
    m.c("riderArmR", "iron_block", (-7, 62.4, 6.2), (1.6, 1.6, 1.6))
    limb(m, "riderArmR", "iron_block", (-7, 62.2, 6.6), [(5, 1.2, (90, 0, 0)), (4.4, 1, (115, 0, 0)), (3.4, 0.8, (140, 0, 0)), (2, 0.6, (165, 0, 0))])
    limb(m, "riderArmR", "light_gray_concrete", (-7, 61.5, 6.6), [(5, 0.4, (90, 0, 0)), (4.4, 0.4, (115, 0, 0))])
    m.attacks = {"volley": "rear", "fire_ring": "howl", "darkness": "toss", "minions": "charge"}
    m.melee = "bite"
    return m


@model
def great_gourd():
    m = Model("great_gourd", "biped", 1.8)
    biped(m, hip=12, legx=5, neck=33, shoulder=27, armx=11.5)
    # the lid is hinged at the back, so it flips open when the head tips back
    next(b for b in m.bones if b["name"] == "head")["pivot"] = [0, 32.5, -8.5]
    m.bone("lolly", "armR", (-12.5, 9, 2))
    pk, pk2, rib, vine, leaf = "orange_terracotta", "orange_concrete", "red_terracotta", "green_terracotta", "moss_block"
    # stubby root legs with curling toes
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, vine, (5 * s, 7, 0), (4, 8, 4))
        m.c(b, "brown_terracotta", (5 * s, 2.4, 0.6), (5.4, 3.4, 6))
        for k in (-1, 1):
            m.c(b, vine, (5 * s + k * 1.6, 0.8, 4.4), (1.4, 1.6, 2.4), (0, k * 15, 0))
        m.c(b, vine, (5 * s + 2.6 * s, 4.6, 0), (1, 3, 1), (0, 0, 30 * s))
    # the pumpkin body: a fat rounded gourd with darker ribs and a glowing carved face
    blob(m, "body", pk, (0, 22, 0), (24, 20, 22), 3)
    for x in (-8.5, -3, 3, 8.5):
        m.c("body", rib, (x, 22, 11.05), (1.4, 15, 0.3))
        m.c("body", rib, (x, 22, -11.05), (1.4, 15, 0.3))
    for z in (-6, 0, 6):
        m.m("body", rib, (12.05, 22, z), (0.3, 15, 1.4))
    m.c("body", "brown_terracotta", (0, 12.4, 0), (16, 1, 16))
    # triangle eyes and a jagged grin, lit from inside
    for s in (1, -1):
        m.c("body", "black_concrete", (4.6 * s, 26.6, 11.1), (5, 4, 0.3))
        m.c("body", "shroomlight", (4.6 * s, 26, 11.2), (3.6, 2.6, 0.3), light=True)
        m.c("body", "black_concrete", (4.6 * s - 1.8 * s, 28.6, 11.25), (1.4, 1.4, 0.3), (0, 0, 45))
        m.c("body", "yellow_concrete", (4.6 * s + 0.6 * s, 26.6, 11.3), (1, 1, 0.3), light=True)
        m.c("body", pk2, (4.6 * s, 30, 11.2), (5.6, 1, 0.5), (0, 0, -18 * s))
    m.c("body", "black_concrete", (0, 23.4, 11.1), (1.6, 1.6, 0.3), (0, 0, 45))
    # the grin is its jaw: it drops open when it laughs
    m.c("body", "black_concrete", (0, 18.6, 11.1), (14, 4.6, 0.3))
    m.c("body", "shroomlight", (0, 18.4, 11.2), (12, 3, 0.3), light=True)
    for k, x in enumerate((-5.4, -2.7, 0, 2.7, 5.4)):
        c = ("yellow_concrete", "orange_concrete", "white_concrete")[k % 3]
        m.c("body", c, (x, 20.4, 11.35), (1.6, 1.4, 0.4))
        m.c("body", "white_concrete", (x + 1.35, 16.8, 11.35), (1.2, 1.2, 0.4), (0, 0, 45))
    m.c("body", pk, (0, 15.6, 9.6), (15, 1.6, 3))
    # the lid: the top of the pumpkin is its head, with a crooked stem, curly vines and a tiny witch hat
    blob(m, "head", pk, (0, 33.6, 0), (19, 3.4, 17), 2)
    m.c("head", "brown_terracotta", (0, 32.2, 0), (17, 0.6, 15))
    m.c("head", "dark_oak_log", (1, 37, 0), (2.4, 4, 2.4), (0, 0, -15))
    m.c("head", "dark_oak_log", (2.4, 39.4, 0), (1.8, 2, 1.8), (0, 0, -40))
    limb(m, "head", vine, (-1.5, 35.4, 1), [(4, 0.8, (0, 0, 70)), (3, 0.8, (0, 0, 20)), (2, 0.7, (0, 0, -40))])
    m.c("head", leaf, (-6, 36.6, 2), (4, 0.6, 3), (0, 30, 15))
    m.c("head", leaf, (5, 36, -4), (3, 0.6, 4), (0, -20, -10))
    m.c("head", "black_wool", (-3.5, 36, -2), (7, 0.8, 7), (0, 0, 10))
    m.c("head", "black_wool", (-3.8, 38, -2), (4.4, 3, 4.4), (0, 0, 14))
    m.c("head", "black_wool", (-4.6, 40.4, -2), (2.6, 2.6, 2.6), (0, 0, 30))
    m.c("head", "black_wool", (-6, 41.8, -2), (1.4, 2, 1.4), (0, 0, 60))
    m.c("head", "purple_wool", (-3.8, 36.8, -2), (4.6, 0.8, 4.6), (0, 0, 14))
    m.c("head", "gold_block", (-1.6, 36.8, 0.3), (0.8, 0.8, 0.3), (0, 0, 14))
    # long vine arms with leafy shoulders and big leafy mitts
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, leaf, (11.6 * s, 27.6, 0), (6, 2, 6), (0, 0, -15 * s))
        m.c(a, leaf, (12.6 * s, 26.2, 2.6), (3, 0.6, 3.4), (20, 0, -25 * s))
        m.c(a, vine, (12.5 * s, 21, 0), (2.6, 11, 2.6))
        m.c(a, vine, (12.5 * s, 14.6, 0.6), (2.4, 8, 2.4))
        m.c(a, leaf, (12.5 * s, 9.6, 1.4), (4.4, 4, 4.4))
        m.c(a, vine, (12.5 * s + 1.6 * s, 18, 0.6), (0.8, 3, 0.8), (0, 0, 35 * s))
    # a trick-or-treat bucket in the left hand, sweets heaped inside
    m.c("armL", pk2, (12.5, 4.6, 3), (5, 5, 5))
    m.c("armL", "black_concrete", (12.5, 5, 5.55), (3, 1.2, 0.2))
    m.c("armL", "iron_block", (12.5, 8.6, 3), (5.4, 0.4, 0.4))
    for k, c in enumerate(("red_concrete", "lime_concrete", "purple_concrete", "yellow_concrete")):
        m.c("armL", c, (11.4 + k * 0.8, 7.4, 2 + (k % 2) * 1.6), (1.2, 1.2, 1.2), (0, 20 * k, 45))
    # and a giant swirly lollipop as a club
    m.c("lolly", "white_concrete", (-12.5, 17, 2), (1.2, 18, 1.2))
    m.c("lolly", "pink_concrete", (-12.5, 30, 2), (1.6, 9, 9))
    m.c("lolly", "white_concrete", (-12.5, 30, 2), (1.8, 6.4, 6.4), (45, 0, 0))
    m.c("lolly", "pink_concrete", (-12.5, 30, 2), (2, 3.6, 3.6))
    m.c("lolly", "red_concrete", (-12.5, 30, 2), (2.1, 1.4, 1.4), (45, 0, 0))
    m.c("lolly", "lime_concrete", (-12.5, 25.6, 2), (1.6, 0.8, 1.6))
    m.attacks = {"fire_ring": "roar", "minions": "cast", "poison": "double", "leap": "slam"}
    m.melee = "swipe"
    m.hold = {"lolly": 30}
    return m

# ================================================================================================= WINTER

@model
def old_man_winter():
    m = Model("old_man_winter", "biped", 1.9)
    biped(m, hip=17, legx=4.2, neck=33, shoulder=31, armx=11)
    m.bone("jaw", "head", (0, 37, 6))
    m.bone("cape", "body", (0, 33, -5))
    m.bone("staff", "armR", (-12, 12, 3))
    skin, beard, red, green = "white_terracotta", "white_wool", "red_wool", "green_wool"
    # fluffy pink slippers and striped long johns
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "pink_wool", (4.2 * s, 1.8, 1.4), (6, 3.6, 8.4))
        m.c(b, "white_wool", (4.2 * s, 3.8, 1.2), (6.4, 1.2, 8.8))
        m.c(b, "pink_wool", (4.2 * s, 2.6, 5.8), (3, 2.4, 1))
        for y in (6, 9, 12, 15):
            m.c(b, red if y % 6 == 0 else "white_wool", (4.2 * s, y, 0), (5, 3, 5))
    # a big round belly in an ugly holiday sweater: zigzags, a reindeer, a pom-pom
    blob(m, "body", red, (0, 24.6, 0.6), (18, 15, 13), 2.4)
    for x in range(-7, 8, 2):
        m.c("body", "white_wool", (x, 28.4 + (x % 4 == 1), 7.15), (1.4, 1.4, 0.3), (0, 0, 45))
        m.c("body", green, (x + 1, 20.4 + (x % 4 == 1), 7.15), (1.4, 1.4, 0.3), (0, 0, 45))
    m.c("body", "brown_terracotta", (0, 24.4, 7.2), (5, 3, 0.4))
    m.c("body", "brown_terracotta", (2.4, 26.6, 7.2), (1.6, 2.4, 0.4))
    m.c("body", "red_concrete", (3.4, 27.6, 7.4), (1, 1, 0.4), light=True)
    for x in (-1.6, 1.6):
        m.c("body", "brown_terracotta", (x, 21.8, 7.2), (0.8, 2.2, 0.4))
    m.c("body", green, (0, 17.4, 0.6), (17.4, 1.6, 12.4))
    m.c("body", red, (0, 31.6, 0), (14, 1.6, 10))
    # stick-thin arms in fat knitted sleeves and huge mittens
    for s, a in ((1, "armL"), (-1, "armR")):
        blob(m, a, red, (11.6 * s, 28, 0), (5.4, 7, 5.4), 1)
        m.c(a, "white_wool", (11.6 * s, 24.4, 0), (5, 1.2, 5))
        m.c(a, red, (12 * s, 19.6, 0.4), (4.4, 8, 4.4))
        m.c(a, "white_wool", (12 * s, 15.6, 0.6), (5, 1.4, 5))
        blob(m, a, green, (12 * s, 12, 1.2), (5.4, 5, 5.4), 1)
        m.c(a, green, (12 * s - 2.8 * s, 13, 2.4), (1.6, 2.6, 2), (0, 0, -20 * s))
    # head: a round red nose, bushy brows hiding the eyes, earmuffs and a bobble hat
    blob(m, "head", skin, (0, 38.6, 1), (9, 9, 9), 1.4)
    m.c("head", "red_concrete", (0, 37.6, 6.4), (3, 3, 2.6))
    m.c("head", "pink_concrete", (0.6, 38.4, 7.6), (1, 1, 0.4))
    m.m("head", "light_blue_concrete", (2.4, 40, 5.55), (1.4, 0.8, 0.2), light=True)
    m.m("head", beard, (2.8, 41.4, 6), (4.4, 2, 2), (0, 0, -14))
    m.m("head", beard, (5, 40.4, 6.4), (2.4, 1.4, 1.6), (0, 0, -40))
    m.m("head", "white_wool", (5, 38.4, 1), (1.6, 4.6, 4.6))
    m.m("head", "pink_wool", (5.5, 38.4, 1), (1.2, 3.6, 3.6))
    m.c("head", "white_wool", (0, 43.8, 1), (6, 0.6, 9.4), (0, 0, 90))
    blob(m, "head", red, (0, 44.4, 0.6), (10, 3.6, 10), 1.4)
    m.c("head", "white_wool", (0, 42.8, 0.6), (10.6, 1.6, 10.6))
    m.c("head", red, (0, 47.4, -0.6), (6, 3, 6), (-15, 0, 0))
    m.c("head", red, (0, 49, -2.6), (3.4, 2.6, 3.4), (-35, 0, 0))
    blob(m, "head", "white_wool", (0, 49.6, -5.4), (3.6, 3.6, 3.6), 0.8)
    # an enormous beard that reaches his knees, with icicles and a forgotten cookie in it
    for y, w, d, z in ((35, 11, 3.4, 5.8), (31, 12, 3.4, 7.6), (27, 11, 3, 8.6), (23, 9, 2.8, 9.2), (19.4, 6.4, 2.4, 9.4), (16.6, 3.4, 2, 9.4)):
        blob(m, "jaw", beard, (0, y, z), (w, 4.4, d), 0.8)
    m.m("jaw", beard, (3, 37.8, 6.6), (4, 1.6, 2), (0, 0, 20))
    m.c("jaw", "pink_concrete", (0, 36.6, 7), (2.6, 0.8, 0.8))
    m.c("jaw", "packed_ice", (-1.2, 14.4, 9.4), (0.8, 2.4, 0.8), light=True)
    m.c("jaw", "packed_ice", (1.4, 15.4, 9.6), (0.7, 1.8, 0.7), light=True)
    m.c("jaw", "brown_terracotta", (2.8, 26, 10.3), (2.4, 2.4, 0.6), (0, 0, 20))
    m.c("jaw", "black_concrete", (2.6, 26.4, 10.65), (0.5, 0.5, 0.2))
    # a scarf flapping behind him
    m.c("body", green, (0, 32.4, 0.4), (11, 2.6, 10.6))
    m.c("cape", green, (-2, 26, -6.4), (3, 14, 0.8), (16, 0, 6), (0, 33, -5))
    m.c("cape", red, (-2, 21, -7.8), (3.2, 1.2, 0.9), (16, 0, 6), (0, 33, -5))
    m.c("cape", green, (2, 28, -6.2), (2.6, 10, 0.8), (12, 0, -10), (0, 33, -5))
    # a candy-cane walking stick
    for k in range(9):
        m.c("staff", "red_concrete" if k % 2 else "white_concrete", (-12, 6.4 + k * 3.2, 3), (1.8, 3.2, 1.8))
    limb(m, "staff", "white_concrete", (-12, 35, 3), [(3, 1.8, (0, 0, 40)), (3, 1.8, (0, 0, 110), "red_concrete"), (3, 1.8, (0, 0, 170))])
    m.attacks = {"frost": "cast", "volley": "sweep", "shockwave": "stomp", "minions": "roar"}
    m.melee = "swipe"
    m.hold = {"staff": 0}
    return m

@model
def frostbottom():
    m = Model("frostbottom", "biped", 1.9)
    biped(m, hip=14, legx=4.6, neck=36, shoulder=31, armx=12)
    m.bone("cape", "body", (0, 33, 0))
    m.bone("club", "armR", (-16, 16, 3))
    snow, snow2, coal = "snow_block", "white_concrete_powder", "coal_block"
    # three snowballs: a huge bottom one (the legs hide under it), a middle and a head
    blob(m, "hips", snow, (0, 9, 0), (20, 16, 18), 3.4)
    m.c("hips", snow2, (0, 1, 0), (18, 2, 16))
    for x, y, z in ((-7, 6, 8), (6, 12, 8.4), (9, 4, -6), (-9, 13, -4)):
        m.c("hips", "powder_snow", (x, y, z), (3, 2, 2), (0, 30, 0))
    # it waddles on two little snowy stumps peeking out
    for s, b in ((1, "legL"), (-1, "legR")):
        blob(m, b, snow, (4.6 * s, 1.6, 5), (6, 3.2, 6), 1)
    blob(m, "body", snow, (0, 25, 0), (16, 13, 14), 3)
    for y in (28, 24.4, 20.8):
        m.c("body", coal, (0, y, 7.05), (2.2, 2.2, 1), (0, 0, 45))
    # a striped scarf with a tail blowing out behind
    m.c("body", "red_wool", (0, 31.4, 0), (13, 2.6, 12))
    for x in (-4, 0, 4):
        m.c("body", "white_wool", (x, 31.4, 6.05), (1.6, 2.6, 0.2))
    m.c("cape", "red_wool", (4, 26, -6.6), (3, 9, 1), (20, 0, -18), (3, 31, -5))
    m.c("cape", "white_wool", (5.4, 21.8, -8), (3.1, 1.4, 1.1), (20, 0, -18), (3, 31, -5))
    # head: coal eyes with angry brows, a crooked coal grin and a VERY long carrot nose
    blob(m, "head", snow, (0, 41, 0), (12, 11, 11), 2.4)
    m.m("head", coal, (2.6, 43, 5.6), (2, 2, 0.6))
    m.m("head", "white_concrete", (3, 43.4, 5.95), (0.6, 0.6, 0.2))
    m.m("head", coal, (2.6, 45.2, 5.6), (3.2, 0.9, 0.6), (0, 0, 16))
    for k in range(6):
        x = -3.6 + k * 1.45
        m.c("head", coal, (x, 37.6 + abs(x) * 0.25 - (k == 4) * 0.4, 5.6), (1.1, 1.1, 0.6))
    limb(m, "head", "orange_concrete", (0, 41, 5.4), [(5, 2, (80, 0, 0)), (4, 1.4, (84, 0, 0)), (3, 0.9, (90, 0, 0))])
    m.c("head", "orange_terracotta", (0, 41, 8.4), (2.2, 0.4, 0.4), (80, 0, 0))
    # a top hat with a holly sprig, worn at a jaunty angle
    m.c("head", "black_wool", (0.8, 46.8, 0), (12, 1, 12), (0, 0, 8))
    m.c("head", "black_wool", (1.2, 51, 0), (8, 8, 8), (0, 0, 8))
    m.c("head", "red_wool", (0.9, 48.2, 0), (8.2, 1.4, 8.2), (0, 0, 8))
    m.c("head", "green_wool", (2.6, 48.6, 4.1), (2.4, 1.2, 0.4), (0, 0, 30))
    m.c("head", "red_concrete", (1.6, 49, 4.2), (1, 1, 0.6), light=True)
    # twig arms with frosty mittens
    for s, a in ((1, "armL"), (-1, "armR")):
        limb(m, a, "spruce_log", (8 * s, 29, 0), [(8, 1.6, (0, 0, -125 * s)), (7, 1.4, (0, 0, -160 * s))])
        m.c(a, "spruce_log", (12.4 * s, 27.6, 0), (0.9, 3, 0.9), (0, 0, -20 * s))
        blob(m, a, "light_blue_wool", (16 * s, 16.4, 1), (4.6, 4.6, 4.6), 1)
        m.c(a, "light_blue_wool", (16 * s - 2.4 * s, 17.4, 2), (1.6, 2.4, 1.6), (0, 0, -20 * s))
    # a snowball club: a branch with a packed iceball on the end
    m.c("club", "spruce_log", (-16, 23, 3), (1.6, 16, 1.6))
    blob(m, "club", "packed_ice", (-16, 32.6, 3), (6, 6, 6), 1.2, light=True)
    for k in range(4):
        m.c("club", "ice", (-16 + (k - 1.5) * 2, 35.6, 3 + (k % 2) * 2 - 1), (0.9, 2.4, 0.9), (0, 0, (k - 1.5) * 20))
    m.attacks = {"frost": "cast", "volley": "double", "quake": "stomp", "minions": "roar"}
    m.melee = "swipe"
    m.hold = {"club": 25}
    return m

# ================================================================================================= SPRING

@model
def killer_bunny():
    m = Model("killer_bunny", "quad", 1.6)
    quad(m, body_y=10, legx=5, legz_front=8, legz_back=-6, neck_y=22, neck_z=8)
    fur, fur2, shade, pink = "white_wool", "snow_block", "light_gray_wool", "pink_wool"
    # a chubby round bunny
    blob(m, "body", fur, (0, 16, -2), (18, 16, 18), 3)
    m.c("body", shade, (0, 8.6, -2), (12, 1.4, 14))
    blob(m, "body", fur2, (0, 15.6, 7.2), (11, 11, 3), 1)
    blob(m, "body", fur2, (0, 15, -11.6), (7, 7, 4), 1.4)
    m.c("body", shade, (0, 12.6, -13.4), (3, 1, 1))
    # ...dressed for war: a carrot bandolier, grenade-carrots on the belt, dog tags
    m.c("body", "brown_terracotta", (0, 16.4, 0), (2, 20, 19.4), (0, 0, 40))
    for k in range(5):
        t = -6 + k * 3
        m.c("body", "orange_concrete", (t * 0.64, 16.4 + t * 0.77, 9.9), (1.2, 2.8, 1.2), (0, 0, 40))
        m.c("body", "green_concrete", (t * 0.64 + 0.9 * 0.64, 16.4 + t * 0.77 + 1.8 * 0.77, 9.9), (1.4, 0.8, 1.4), (0, 0, 40))
    m.c("body", "brown_terracotta", (0, 10.6, -2), (18.4, 1.6, 18.4))
    for x in (-6, 6):
        m.c("body", "orange_concrete", (x, 9.4, 9.4), (1.8, 2.4, 1.8))
        m.c("body", "green_concrete", (x, 11, 9.4), (1.2, 0.8, 1.2))
    m.c("body", "chain", (0, 21.6, 9.2), (3, 0.4, 0.4))
    m.c("body", "iron_block", (0.6, 20.4, 9.5), (1.2, 1.6, 0.3), (0, 0, 10))
    # front paws with bloody claws, enormous hind feet
    for s in (1, -1):
        b = "legFL" if s > 0 else "legFR"
        blob(m, b, fur, (3 * s, 6, 8), (4, 8, 4), 0.8)
        blob(m, b, fur2, (3 * s, 2, 9.8), (4, 2.6, 5), 0.6)
        for k in (-1, 0, 1):
            m.c(b, "white_concrete", (3 * s + k * 1.1, 1.4, 12.6), (0.6, 0.8, 1.6), (25, 0, 0))
            m.c(b, "red_concrete", (3 * s + k * 1.1, 1, 13.3), (0.6, 0.5, 0.6))
        b = "legBL" if s > 0 else "legBR"
        blob(m, b, fur, (6.6 * s, 9, -6), (5.4, 9, 9), 2)
        blob(m, b, fur2, (6.8 * s, 1.4, -1.6), (5, 2.8, 14), 1)
        m.c(b, pink, (6.8 * s, 0.1, -1.6), (3.6, 0.2, 10))
        for k in (-1, 0, 1):
            m.c(b, fur2, (6.8 * s + k * 1.5, 1.2, 5.6), (1.2, 2, 1.6))
    # the head: huge red eyes, an eyepatch, a red headband with tails blowing, buck teeth, whiskers
    blob(m, "head", fur, (0, 28, 9), (14, 12, 12), 2.4)
    blob(m, "head", fur2, (0, 24.6, 14.6), (9, 5, 2.4), 1)
    m.m("head", fur2, (6.8, 25.4, 12), (2.6, 3.6, 3.6), (0, 0, 20))
    m.c("head", pink, (0, 27, 15.9), (2.4, 1.8, 0.8))
    m.c("head", "black_concrete", (3.6, 29.6, 15.05), (3, 3, 0.2))
    m.c("head", "red_concrete", (3.6, 29.6, 15.15), (2, 2, 0.1), light=True)
    m.c("head", "white_concrete", (4.2, 30.2, 15.2), (0.7, 0.7, 0.1))
    m.c("head", "black_wool", (-3.6, 29.8, 15.2), (3.6, 3.2, 0.4))
    m.c("head", "black_wool", (0, 31.6, 15.1), (14.6, 0.6, 0.3), (0, 0, -18))
    m.c("head", "red_terracotta", (-3.6, 33, 15.2), (0.5, 3, 0.2), (0, 0, 25))
    m.c("head", "red_wool", (0, 32.8, 9), (14.4, 1.8, 12.4))
    m.c("head", "red_wool", (-6.4, 32, 2.2), (1.2, 1.2, 5), (-30, 30, 0))
    m.c("head", "red_wool", (-5.4, 31, 0.6), (1.2, 1.2, 5), (-50, 10, 0))
    m.c("head", "white_concrete", (0, 22.8, 15.6), (3, 3, 0.6))
    m.c("head", "black_concrete", (0, 22.8, 15.95), (0.2, 3, 0.1))
    for y in (26.2, 25.2):
        m.m("head", "light_gray_concrete", (6.6, y, 15.6), (6, 0.3, 0.3), (0, -12, 0))
    # a carrot clamped in the teeth like a cigar
    m.c("jaw", "orange_concrete", (3.6, 22.4, 17.2), (1, 1, 5), (0, -25, -8))
    m.c("jaw", "green_concrete", (5.4, 22.8, 19.2), (1.2, 1.2, 1.2), (0, -25, -8))
    m.c("jaw", fur2, (0, 21.4, 12.6), (7, 2, 4))
    m.c("jaw", "red_terracotta", (-1.6, 21.2, 14.7), (1, 0.6, 0.2))
    # ears: one tall and proud with a notch bitten out, one flopped over with a bandage
    limb(m, "head", fur, (2.8, 33.4, 8), [(9, 3.4, (-8, 0, -8)), (7, 3, (-12, 0, -4))])
    m.c("head", pink, (3.1, 38.8, 9.3), (1.6, 11, 0.4), (-10, 0, -7), (2.8, 33.4, 8))
    m.c("head", "black_concrete", (4.4, 41.2, 8.8), (1.4, 1.6, 3.8), (-14, 0, -8))
    limb(m, "head", fur, (-2.8, 33.4, 8), [(6, 3.4, (-10, 0, 20)), (8, 3, (-60, 0, 80))])
    m.c("head", "white_concrete", (-5, 37.4, 8.6), (3.8, 1.2, 3.8), (-10, 0, 20))
    m.c("head", "red_terracotta", (-5, 37.4, 10.55), (1, 0.6, 0.2), (-10, 0, 20))
    m.attacks = {"leap": "pounce", "minions": "howl", "shockwave": "rear"}
    m.melee = "bite"
    return m

@model
def clucksworth():
    m = Model("clucksworth", "biped", 1.9)
    biped(m, hip=13, legx=4, neck=33, shoulder=28, armx=11)
    m.bone("jaw", "head", (0, 38, 7))
    feather, feather2, beak, comb = "white_wool", "snow_block", "orange_terracotta", "red_concrete"
    # skinny scaly legs with big three-toed feet
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "orange_concrete", (4 * s, 7, 0), (1.8, 12, 1.8))
        m.c(b, feather, (4 * s, 12.4, 0), (4.4, 2.6, 4.4))
        for k, r in ((-1, -25), (0, 0), (1, 25)):
            m.c(b, "orange_concrete", (4 * s + k * 1.6, 0.6, 2.6), (1.2, 1.2, 5), (0, r, 0))
            m.c(b, "black_concrete", (4 * s + k * 2.6, 0.6, 5), (0.8, 0.8, 0.8), (0, r, 0))
        m.c(b, "orange_concrete", (4 * s, 0.6, -1.6), (1, 1, 2.6))
    # a fat round feathery body with a fluffy behind and tail plumes
    blob(m, "body", feather, (0, 22, 0), (18, 17, 18), 4)
    blob(m, "body", feather2, (0, 21, 8.4), (11, 11, 2.4), 1.4)
    for k, (x, r) in enumerate(((-3, -20), (0, 0), (3, 20))):
        m.c("body", feather if k != 1 else feather2, (x, 30, -10), (2.6, 9, 2.6), (-35, 0, r), (x, 26, -8))
    m.c("body", "black_wool", (0, 31.6, -12.6), (1.8, 2.4, 1.4), (-35, 0, 0))
    # spring flowers stuck in its feathers
    for x, y, z, c in ((6.4, 27, 6.8, "pink_concrete"), (-7.4, 18, 6, "yellow_concrete"), (-5.6, 29, -6, "light_blue_concrete")):
        m.c("body", c, (x, y, z), (1.6, 1.6, 1.6), (45, 45, 0))
        m.c("body", "yellow_concrete" if c != "yellow_concrete" else "orange_concrete", (x, y, z), (0.8, 0.8, 1.9))
    # its weak spot: the golden egg it is sitting on, peeking out of the chest feathers and glowing
    m.c("body", "gold_block", (0, 18, 9.2), (5, 6.4, 2.6), light=True)
    m.c("body", "gold_block", (0, 18, 9.8), (3.6, 4.6, 2.6), light=True)
    m.c("body", "yellow_concrete", (-1, 19.6, 11.15), (1, 1.4, 0.2), light=True)
    # wings as arms, with feather fingers
    for s, a in ((1, "armL"), (-1, "armR")):
        blob(m, a, feather, (11 * s, 22, -0.4), (3.4, 12, 10), 1.4)
        for k in range(3):
            m.c(a, feather2, (11 * s, 15.4 - k * 0.4, -3.4 + k * 3), (2.6, 4, 2.4), (0, 0, 10 * s))
    # the head: angry eyebrows, a big beak that clacks, a floppy red comb and wattle
    blob(m, "head", feather, (0, 38, 1), (11, 10, 10), 2)
    m.m("head", "black_concrete", (3, 39.6, 5.95), (2, 2.4, 0.2))
    m.m("head", "white_concrete", (3.4, 40.2, 6.05), (0.7, 0.7, 0.1))
    m.m("head", "black_concrete", (3, 42.2, 6), (3.6, 0.8, 0.4), (0, 0, -22))
    m.c("head", beak, (0, 37.8, 7.6), (4.4, 2.2, 4))
    m.c("head", "orange_concrete", (0, 37.4, 10), (3, 1.4, 1.6))
    m.c("jaw", beak, (0, 36, 8.6), (3.6, 1.2, 3.6))
    m.c("jaw", comb, (0, 34, 7.6), (2, 3, 1.4))
    m.c("jaw", comb, (0, 32.6, 7.6), (1.4, 1.6, 1.2))
    for k, (z, h) in enumerate(((-2, 3.4), (0.6, 4.6), (3, 3.4))):
        m.c("head", comb, (0, 43 + h / 2, z), (1.6, h, 2.6), (0, 0, (k - 1) * 12))
    # ...and the funniest part: half an eggshell worn as a helmet, cracked, with a flower in it
    m.c("head", "white_concrete", (0, 43.6, 1), (12, 1.2, 11))
    m.m("head", "white_concrete", (5.6, 41.6, 1), (1, 3, 10))
    m.c("head", "white_concrete", (0, 41.6, -4.1), (11, 3, 1))
    for x in (-4.6, -1.4, 1.8, 4.8):
        m.c("head", "white_concrete", (x, 42, 6.1), (1.6, 1.6 + abs(x) * 0.2, 0.8), (0, 0, 45))
    m.c("head", "light_gray_concrete", (-2.6, 44.3, 1), (0.4, 0.2, 6), (0, 20, 0))
    m.c("head", "pink_concrete", (3.6, 45.2, -1), (1.6, 1.6, 1.6), (45, 45, 0))
    m.c("head", "lime_concrete", (3.6, 44.4, -1), (0.4, 1.4, 0.4))
    m.attacks = {"leap": "slam", "minions": "roar", "shockwave": "stomp", "volley": "double"}
    m.melee = "swipe"
    return m

# ================================================================================================= SUMMER

@model
def sunscorch():
    m = Model("sunscorch", "slime", 1.9)
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 14, 0))
    m.bone("mouth", "body", (0, 10, 14))
    # a melting little sun, far too hot, on holiday: a glowing orange jelly with a yellow core
    sh, sh2 = "orange_stained_glass", "yellow_stained_glass"
    blob(m, "body", sh, (0, 13, 0), (28, 24, 28), 5)
    m.c("body", sh, (0, 1.2, 0), (32, 2.4, 32))
    blob(m, "inner", "yellow_concrete", (0, 14, 0), (14, 13, 14), 3, light=True)
    m.c("inner", "orange_concrete", (0, 14, 0), (8, 8, 14.4), light=True)
    # sun rays poking up round the top like a crown of flames
    for k in range(10):
        a = math.radians(k * 36 + 18)
        h = 6 if k % 2 else 4.4
        x, z = 11.4 * math.cos(a), 11.4 * math.sin(a)
        m.c("body", sh2, (x, 25 + h / 2, z), (2.6, h, 2.6), (math.degrees(math.sin(a)) * 0.4, -k * 36 - 18, -math.degrees(math.cos(a)) * 0.4), light=True)
    # melting: drips sliding down, a puddle spreading round its base
    for x, z, h in ((-9, 14.6, 6), (5, 14.6, 4), (14.6, 7, 5), (-14.6, -4, 7), (9, -14.6, 4)):
        m.c("body", sh2, (x, 3.4 + h / 2, z), (1.8, h, 1.8), light=True)
        m.c("body", sh2, (x, 3, z), (2.6, 1.6, 2.6), light=True)
    m.c("body", "orange_stained_glass", (0, 0.2, 0), (34, 0.4, 32))
    # sweat drops flying off its forehead
    for x, y in ((-12.6, 24), (13.4, 22), (-14.6, 20)):
        m.c("body", "light_blue_stained_glass", (x, y, 9), (1.4, 2.2, 1.4), (0, 0, 20 if x > 0 else -20))
    # face: huge sunglasses with a pink rim, sunscreen smeared on the nose, a melting grin, tongue out
    for s in (1, -1):
        m.c("body", "black_stained_glass", (5 * s, 17.6, 14.4), (7.4, 4.6, 0.6))
        m.c("body", "magenta_concrete", (5 * s, 20.2, 14.6), (8, 0.8, 0.8))
        m.c("body", "white_concrete", (6.6 * s, 18.6, 14.8), (1.4, 0.8, 0.2), (0, 0, 30))
        m.c("body", "magenta_concrete", (12.4 * s, 18.6, 9), (0.6, 0.6, 12))
        m.c("body", "pink_concrete", (9.6 * s, 13, 14.2), (3, 1.4, 0.4))
    m.c("body", "magenta_concrete", (0, 18.4, 14.6), (2.6, 0.8, 0.8))
    m.c("body", "white_concrete", (0, 15, 14.6), (3.4, 2.4, 1.2))
    m.c("body", "white_concrete", (0, 15.6, 15.4), (1.2, 1, 0.6))
    m.c("mouth", "black_concrete", (0, 9.6, 14.3), (12, 3, 0.4))
    for x in (-4.6, -1.6, 1.6, 4.6):
        m.c("mouth", "white_concrete", (x, 10.8, 14.5), (1.6, 0.9, 0.3))
    m.c("mouth", "red_concrete", (2.4, 7.4, 15.2), (3.6, 4, 1.4), (20, 0, -8))
    m.c("mouth", "pink_concrete", (2.4, 6, 16), (2.6, 1.6, 0.8), (20, 0, -8))
    # a rubber duck float ring round its middle, the duck head grinning back at you
    for k in range(16):
        a = k * 22.5
        x, z = 16.6 * math.cos(math.radians(a)), 16.6 * math.sin(math.radians(a))
        c = "yellow_concrete" if (k // 2) % 2 else "white_concrete"
        m.c("body", c, (x, 7.4, z), (4.6, 4.2, 7), (0, -a, 0))
    m.c("body", "yellow_concrete", (-11, 12.6, 14), (5, 5, 5), (0, -30, 0))
    m.c("body", "orange_concrete", (-12.2, 12, 16.8), (3, 1.2, 2.4), (0, -30, 0))
    m.m("body", "black_concrete", (-9.6 + 0, 13.8, 16.2), (0.8, 0.8, 0.2), (0, -30, 0))
    m.c("body", "black_concrete", (-12.6, 13.8, 14.2), (0.8, 0.8, 0.2), (0, -30, 0))
    # a cocktail umbrella stuck in its head, and a straw
    m.c("body", "white_concrete", (5, 31, -3), (0.6, 12, 0.6), (0, 0, -12))
    m.c("body", "lime_concrete", (6.4, 37, -3), (12, 0.8, 12), (0, 45, -12))
    m.c("body", "pink_concrete", (6.6, 37.8, -3), (8, 0.8, 8), (0, 45, -12))
    m.c("body", "yellow_concrete", (6.8, 38.6, -3), (3, 0.8, 3), (0, 45, -12))
    m.c("body", "red_concrete", (-5, 30, 2), (0.8, 10, 0.8), (14, 0, 20))
    m.c("body", "red_concrete", (-7, 34.8, 3.2), (0.8, 3, 0.8), (40, 0, 70))
    m.attacks = {"leap": "slam", "quake": "hop", "fire_ring": "burst", "volley": "spit"}
    m.melee = "hop"
    return m

@model
def admiral_pinchworth():
    m = Model("admiral_pinchworth", "spider", 1.7)
    m.bone("body", "root", (0, 12, 0))
    m.bone("abdomen", "body", (0, 16, -4))
    m.bone("head", "body", (0, 14, 9))
    m.bone("fangL", "head", (10, 14, 10))
    m.bone("fangR", "head", (-10, 14, 10))
    sh, sh2, leg, belly = "red_concrete", "red_terracotta", "orange_terracotta", "white_terracotta"
    # a wide flat crab shell, bumpy rim, pale belly
    blob(m, "body", sh, (0, 14, 0), (26, 8, 20), 2.4)
    m.c("body", sh2, (0, 18.4, 0), (18, 1.4, 12))
    for x in (-10, -5, 0, 5, 10):
        m.c("body", sh2, (x, 15, 10.4), (2.4, 2, 1), (0, 0, 45))
    for x, z in ((-7, 3), (7, 3), (-4, -4), (4, -4), (0, 1)):
        m.c("body", sh, (x, 19.2, z), (2.2, 1.2, 2.2))
    m.c("body", belly, (0, 10, 0), (20, 1, 15))
    # a whole sandcastle built on its back, with a little flag and a starfish
    m.c("abdomen", "sandstone", (0, 22, -4), (12, 6, 10))
    for x, z in ((-5, -8), (5, -8), (-5, 0), (5, 0)):
        m.c("abdomen", "sandstone", (x, 27, z), (3.4, 5, 3.4))
        m.c("abdomen", "smooth_sandstone", (x, 30, z), (4, 1, 4))
    m.c("abdomen", "smooth_sandstone", (0, 25.6, -4), (13, 1, 11))
    m.c("abdomen", "sandstone", (0, 28, -4), (5, 6, 5))
    m.c("abdomen", "black_concrete", (0, 23, 1.05), (2, 3, 0.2))
    m.c("abdomen", "spruce_log", (0, 34, -4), (0.5, 6, 0.5))
    m.c("abdomen", "blue_concrete", (1.6, 36, -4), (3, 2, 0.2))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (3.6, 0.8, 0.8), (0, 0, 36))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (3.6, 0.8, 0.8), (0, 0, -36))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (0.8, 3.6, 0.8))
    # googly eyes on stalks, a twirled moustache, a tiny admiral's bicorne
    m.c("head", sh, (0, 14, 10.6), (14, 5, 3))
    for s in (1, -1):
        m.c("head", sh2, (3 * s, 19, 10.6), (1.2, 7, 1.2), (0, 0, -10 * s))
        m.c("head", "white_concrete", (3.6 * s, 22.8, 10.6), (3.4, 3.4, 3.4))
        m.c("head", "black_concrete", (3.6 * s + 0.4 * s, 22.2, 12.35), (1.4, 1.4, 0.2))
        m.c("head", "black_concrete", (4.4 * s, 14.8, 12.2), (4, 0.9, 0.6), (0, 0, -20 * s))
        m.c("head", "black_concrete", (6.4 * s, 15.8, 12.2), (1, 1, 0.6))
    m.c("head", "black_concrete", (0, 12.2, 12.15), (4, 0.8, 0.2))
    m.c("head", "blue_terracotta", (0, 26, 9.6), (11, 2.6, 2), (0, 0, 0))
    m.c("head", "blue_terracotta", (0, 27.4, 9.6), (7, 2, 1.8))
    m.c("head", "gold_block", (0, 25, 10.7), (11.2, 0.6, 0.2))
    m.c("head", "white_concrete", (0, 27.4, 10.6), (1.6, 1.6, 0.2))
    # big lopsided claws: the left one is massive and keeps snapping
    for s, b, k in ((1, "fangL", 1.4), (-1, "fangR", 1.0)):
        limb(m, b, leg, (10 * s, 14, 10), [(6, 2.2, (-60, 0, -30 * s)), (5, 2, (-90, 0, 10 * s))])
        cx, cy, cz = 13 * s, 14.6, 20
        m.c(b, sh, (cx, cy, cz), (5 * k, 4.4 * k, 6 * k))
        m.c(b, sh, (cx + 1 * s, cy + 0.4, cz + 5.4 * k), (3 * k, 2.4 * k, 6 * k), (-8, 0, 0))
        m.c(b, sh2, (cx - 1.4 * s, cy - 1.8 * k, cz + 4.8 * k), (2.2 * k, 1.6 * k, 5 * k), (14, 0, 0))
        m.c(b, "white_terracotta", (cx + 1 * s, cy + 0.4, cz + 8.6 * k), (2.4 * k, 1.6 * k, 0.6))
    # eight legs splayed sideways, with pointed tips
    zs = {1: 5, 2: 2, 3: -1.5, 4: -5}
    fan = {1: 30, 2: 10, 3: -10, 4: -30}
    for i in (1, 2, 3, 4):
        m.bone(f"legL{i}", "body", (11, 13, zs[i]))
        m.bone(f"legR{i}", "body", (-11, 13, zs[i]))
        a = fan[i]
        mlimb(m, f"legL{i}", leg, (11, 13, zs[i]), [(8, 1.8, (a, 0, -60)), (13, 1.5, (a * 0.5, 0, -160), sh2), (5, 0.9, (a * 0.3, 0, -178), "white_terracotta")])
    m.attacks = {"leap": "leap", "minions": "drum", "pull": "rearup", "volley": "spit"}
    m.melee = "fang"
    return m
