"""Chapter bosses: one small, well made boss at the end of each story chapter. Smaller than the world
bosses, each built around one clear idea that matches its chapter."""
import math
from models import model, biped, horn, mhorn, limb, mlimb, taper, quad, dirof
from build import Model
from kit import paint, crack, band, hem, tufts, spikes, plate, stack, mirror_rows, bevel
from v2_general import quad_leg

SPAWN, DEATH = {}, {}


@model
def brakka():
    """Chapter 1, The Wanderers' Camp: Brakka the bandit chief. A burly raider with a red bandana over his
    face, an eye patch, leather armour with a wolf-fur collar, a satchel of stolen loot, a crossbow slung
    on his back and a hatchet in each hand."""
    m = Model("brakka", "biped", 1.7)
    biped(m, hip=13, legx=3.6, neck=31, shoulder=29, armx=9)
    m.bone("cape", "body", (0, 28.6, -3.4))
    m.bone("axeR", "armR", (-9, 12, 2))
    m.bone("axeL", "armL", (9, 12, 2))
    m.hold = {"axeR": 30, "axeL": 30}
    m.bend = -40
    SK, LE, LE2, FU, RD, BK = "light_gray_terracotta", "brown_terracotta", "spruce_planks", "gray_wool", "red_concrete", "black_concrete"
    # legs: dark trousers, leather boots with buckles and fur tops, a knee guard
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.6 * s
        bevel(m, b, "gray_concrete", (x, 9.6, 0), (4.4, 7, 4.4), 0.5)
        bevel(m, b, LE, (x, 3, 0.5), (4.8, 6, 5.6), 0.5)
        m.c(b, LE, (x, 0.6, 3.2), (4.4, 1.2, 1.6))
        m.c(b, FU, (x, 6.4, 0.3), (5.4, 1.4, 5.8))
        m.c(b, "iron_block", (x, 4, 3.35), (1.4, 1, 0.3))
        m.c(b, LE2, (x, 10.4, 2.35), (3, 3, 0.4))
    # body: leather jerkin over a grey shirt, a wide belt with a skull buckle, straps for the crossbow
    bevel(m, "hips", LE, (0, 13.2, 0), (9.6, 3, 5.6), 0.5)
    bevel(m, "body", LE, (0, 21.6, 0), (10.4, 12, 6.2), 0.8)
    m.c("body", "light_gray_wool", (0, 23, 3.15), (3, 9, 0.2))
    for y in (19.6, 22, 24.4, 26.8):
        m.c("body", BK, (0, y, 3.3), (2.4, 0.4, 0.2), (0, 0, 25))
    band(m, "body", BK, (0, 16.4, 0), (10.6, 1.6, 6.4))
    paint(m, "body", "front", (0, 16.4, 3.3), ["WWW", "K.K", "WWW"], {"W": "bone_block", "K": BK}, px=0.6, depth=0.3)
    m.c("body", LE2, (0, 22, 0), (1.2, 15, 6.6), (0, 0, 38))
    # a wolf-fur collar and a pauldron of studded leather on one shoulder
    bevel(m, "body", FU, (0, 28.6, 0), (12, 2.6, 7.4), 0.8)
    tufts(m, "body", FU, [(-5, 29.6, 3), (-1.6, 29.8, 3.6), (1.8, 29.8, 3.6), (5, 29.6, 3), (0, 29.6, -3.4)], 1.8, alt="light_gray_wool")
    bevel(m, "armL", LE, (9.6, 28.4, 0), (5, 2.6, 5.6), 0.5, (0, 0, -18), (9, 29, 0))
    for z in (-1.6, 0, 1.6):
        m.c("armL", "iron_block", (11.6, 27.8, z), (0.4, 0.6, 0.6), (0, 0, -18))
    # the satchel of loot on his hip, gold spilling out
    m.c("hips", LE2, (-5.6, 12.4, 1.4), (2, 4, 4))
    m.c("hips", "gold_block", (-5.8, 14.8, 1.8), (1.4, 0.8, 1.4), (0, 30, 0))
    m.c("hips", "emerald_block", (-5.6, 15, 0.4), (0.8, 0.8, 0.8), (45, 0, 45))
    # arms: bare forearms, leather bracers, fingerless gloves
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 9 * s
        bevel(m, a, "light_gray_wool", (x, 24.6, 0), (4, 6, 4.2), 0.5)
        m.c(a, SK, (x, 19.4, 0.4), (3.6, 4.6, 3.8))
        bevel(m, a, LE, (x, 15.6, 0.6), (4.2, 3.4, 4.4), 0.5)
        m.c(a, BK, (x, 13, 1), (3.6, 2, 3.8))
        m.c(a, LE2, (x, 16.6, 0.6), (4.4, 0.4, 4.6))
    # the head: a weathered face, a red bandana over the nose and mouth, an eye patch, a scar, a topknot
    bevel(m, "head", SK, (0, 35.2, 0.4), (7.8, 7.6, 7.6), 1)
    m.c("head", RD, (0, 33.2, 0.4), (8.2, 3.6, 8))
    m.c("head", RD, (0, 31.4, 4), (4, 2, 1), (20, 0, 0))
    for s in (1, -1):
        m.c("head", RD, (1.2 * s, 32.6, -4.4), (1.2, 3, 0.6), (0, 0, 20 * s))
    paint(m, "head", "front", (0, 36.8, 4.25), ["KKK.KKK", "KKK.W.K", "...K..."], {"K": BK, "W": "white_concrete"}, px=0.9, depth=0.3)
    m.c("head", BK, (0, 37.4, 4.3), (8, 0.4, 0.2), (0, 0, -18))
    m.c("head", "red_terracotta", (2.6, 36, 4.25), (0.4, 2.4, 0.2), (0, 0, 15))
    m.c("head", "brown_concrete", (0, 39.2, 0), (8, 1.2, 7.8))
    m.c("head", "brown_concrete", (0, 40.6, -2), (2.4, 2.4, 2.4))
    m.c("head", LE2, (0, 39.8, -2), (2.6, 0.6, 2.6))
    # the crossbow slung across his back
    m.c("body", LE2, (0, 22, -3.6), (1.2, 12, 1.2), (0, 0, -30))
    m.c("body", "iron_block", (3, 26.6, -3.8), (8, 0.8, 0.8), (0, 0, -30))
    m.c("body", "white_wool", (3, 26.6, -4.4), (0.3, 0.3, 0.4))
    # two hatchets: dark wood hafts wrapped in leather, iron heads with a bright edge
    for s, b in ((1, "axeL"), (-1, "axeR")):
        x = 9 * s
        m.c(b, LE2, (x, 16.6, 2), (1.1, 10, 1.1))
        m.c(b, LE, (x, 13, 2), (1.4, 2.6, 1.4))
        m.c(b, "iron_block", (x, 20.4, 3.8), (0.8, 3.6, 3.4))
        m.c(b, "white_concrete", (x, 20.4, 5.55), (0.85, 3.6, 0.3))
        m.c(b, "iron_block", (x, 20.4, 0.8), (0.8, 1.4, 1.4))
    # a string of trophies on his belt: a wolf fang, a gold coin and a feather, and a canteen
    for k, (x, c, h) in enumerate(((2.4, "bone_block", 1.6), (3.6, "gold_block", 0.8), (4.8, "white_wool", 2))):
        m.c("body", c, (x, 15 - h / 2, 3.4), (0.6, h, 0.4), (0, 0, 10))
    m.c("hips", "green_terracotta", (5.4, 12, -1), (2, 3, 2))
    m.c("hips", LE, (5.4, 13.8, -1), (0.8, 0.8, 0.8))
    # a wide-brimmed bandit hat over the topknot, a red band with a feather, and a ragged travelling cloak
    m.c("head", "brown_concrete", (0, 39.6, 0.4), (13, 0.8, 12))
    bevel(m, "head", "brown_terracotta", (0, 41.6, 0.4), (8.4, 3.6, 8), 0.6)
    m.c("head", RD, (0, 40.4, 0.4), (8.8, 0.9, 8.4))
    m.c("head", "white_wool", (4.6, 42.4, -1), (0.4, 4, 1), (0, 0, -25))
    m.c("cape", LE2, (0, 19.6, -3.8), (10, 17, 0.5))
    hem(m, "cape", LE2, -5, 5, 11.1, -3.8, 0.5, 5, long=3, short=1.2, seed=3)
    m.c("cape", FU, (0, 28.2, -3.9), (11, 1.6, 0.9))
    m.attacks = {"hatchets": "double", "volley": "cast", "charge": "lunge", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def gate_shade():
    """Chapter 2, Shadows at the Gate: a wraith made of shadow. A tall tattered hood with two white eyes
    burning in the dark, a ragged cloak that trails into wisps, long clawed hands, broken gate chains still
    locked round its wrists, and a cold lantern it carries to lure travellers off the road."""
    m = Model("gate_shade", "float", 1.5)
    m.bone("core", "root", (0, 12, 0))
    m.bone("head", "core", (0, 30, 0))
    m.mbone("armL", "core", (7, 27, 0))
    m.bone("ring1", "core", (0, 6, 0))
    m.bone("ring2", "core", (0, 20, 0))
    m.no_elbows = True
    CL, CL2, DK, EY, CH, LA = "black_wool", "gray_wool", "black_concrete", "white_concrete", "chain", "light_blue_concrete"
    # the cloak: narrow at the shoulders, flaring out and tearing into long ragged strips
    stack(m, "core", CL, 0, 9, 0, [(10, 3, 8), (9, 4, 7.4), (8.4, 5, 7), (8.6, 4, 7), (9.4, 4, 7.4)])
    for k in range(10):
        a = math.radians(k * 36)
        L = 6 + (k * 7 % 4)
        x, z = math.sin(a) * 4.6, math.cos(a) * 3.8
        m.c("core", CL if k % 2 else CL2, (x, 9 - L / 2, z), (2.2, L, 1), (0, k * 36, (k % 3 - 1) * 8), (x, 9, z))
    m.c("core", CL2, (0, 18, 3.6), (1.2, 16, 0.4))
    # the hood: a tall drooping point, the dark hollow inside, two burning eyes
    bevel(m, "head", CL, (0, 32.4, 0), (8, 7.6, 8), 1)
    m.c("head", DK, (0, 31.6, 3.4), (5.6, 5.6, 1.4))
    m.c("head", CL, (0, 37.4, -1.6), (5, 4, 5), (-20, 0, 0))
    m.c("head", CL, (0, 39.6, -4), (3, 3.4, 3), (-50, 0, 0))
    m.c("head", CL, (0, 39.6, -6.6), (1.6, 3, 1.6), (-90, 0, 0))
    for s in (1, -1):
        m.c("head", EY, (1.2 * s, 32.4, 4.45), (0.8, 0.6, 0.1), light=True)
    hem(m, "head", CL, -4, 4, 28.8, 4, 0.6, 5, long=1.6, short=0.6)
    # arms: thin ragged sleeves, long grey hands with claws, broken chains hanging from iron cuffs
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 7 * s
        tip = limb(m, a, CL, (x, 27, 0), [(7, 2.6, (10, 0, -16 * s)), (6, 2.2, (-30, 0, -8 * s))])
        tx, ty, tz = tip
        hem(m, a, CL2, tx - 1.6, tx + 1.6, ty + 4, tz, 0.6, 3, long=2, short=0.8)
        m.c(a, "iron_block", (tx, ty + 1.2, tz), (2.8, 1.2, 2.8))
        m.c(a, CH, (tx + 0.8 * s, ty - 2, tz - 1), (0.6, 5, 0.6), (10, 0, 10 * s))
        m.c(a, "iron_block", (tx + 1.2 * s, ty - 4.8, tz - 1.4), (1.2, 1.2, 0.6))
        m.c(a, "light_gray_concrete", (tx, ty - 1, tz + 0.6), (1.6, 2, 1.6))
        for t in (-0.6, 0, 0.6):
            m.c(a, "light_gray_concrete", (tx + t, ty - 3, tz + 1.4), (0.4, 2.6, 0.4), (25, 0, 0))
    # the cold lantern: on a chain from the left hand
    m.c("armL", CH, (9, 13, 2.4), (0.6, 3, 0.6))
    m.c("armL", "iron_block", (9, 10.6, 2.4), (2.6, 0.6, 2.6))
    m.c("armL", "soul_lantern", (9, 9, 2.4), (2.2, 2.6, 2.2), light=True)
    m.c("armL", "iron_block", (9, 7.4, 2.4), (2.6, 0.6, 2.6))
    # wisps of shadow circling it, and a faint cold glow drifting up from the hem
    for k in range(6):
        a = math.radians(k * 60)
        m.c("ring1", CL2 if k % 2 else "gray_concrete", (math.sin(a) * 8, 4 + (k % 3), math.cos(a) * 8), (1.2, 1.2, 2.6), (0, k * 60, 0))
    for k in range(4):
        a = math.radians(k * 90 + 45)
        m.c("ring2", LA, (math.sin(a) * 9, 18 + (k % 2) * 4, math.cos(a) * 9), (0.6, 0.6, 0.6), (45, 45, 0), light=True)
    # a pale skull face deep in the hood, a soul-blue trim along the hood and the cloak's front edges
    bevel(m, "head", "light_gray_concrete", (0, 31.8, 3.7), (4.4, 4.4, 1.2), 0.5)
    m.c("head", "black_concrete", (0, 30.4, 4.35), (2.6, 0.6, 0.1))
    for s_ in (1, -1):
        m.c("head", "black_concrete", (1.2 * s_, 32.4, 4.35), (1.4, 1.2, 0.1))
    for s_ in (1, -1):
        m.c("head", LA, (3.9 * s_, 32, 3.2), (0.3, 6.4, 0.4), light=True)
        m.c("core", LA, (1.6 * s_, 17, 3.75), (0.3, 14, 0.3), light=True)
    m.c("head", LA, (0, 35.9, 3.4), (7.4, 0.3, 0.4), light=True)
    # a heavy chain wrapped round its chest and a broken gate lock hanging from it
    for k in range(5):
        a = math.radians(k * 72 + 20)
        m.c("core", CH, (math.sin(a) * 4.8, 22 + k * 0.5, math.cos(a) * 4), (3.4, 0.6, 0.6), (0, k * 72 + 110, 12))
    m.c("core", "iron_block", (2, 19.6, 4.4), (2.6, 2.8, 1))
    m.c("core", "black_concrete", (2, 19.4, 4.95), (0.6, 1.2, 0.1))
    m.c("core", "iron_block", (2, 21.4, 4.4), (1.8, 1.2, 0.4))
    # grey layers in the cloak so the shape reads in the dark, mantle over the shoulders
    bevel(m, "core", CL2, (0, 25.6, 0), (11, 2.6, 8.4), 0.6)
    hem(m, "core", CL2, -5.5, 5.5, 24.4, 4.2, 0.4, 6, long=2.4, short=0.8)
    hem(m, "core", CL2, -5.5, 5.5, 24.4, -4.2, 0.4, 6, long=3, short=1, seed=2)
    for s_ in (1, -1):
        hem(m, "core", CL2, -3.6, 3.6, 24.4, 5.5 * s_, 0.4, 4, long=2.6, short=1, face_z=False, seed=1)
    m.attacks = {"darkness": "pulse", "blink": "dive", "chains": "swipe", "minions": "raise"}
    m.melee = "swipe"
    return m


@model
def oakheart():
    """Chapter 3, The Elder's Charge: an old oak that woke up to protect the elder's grove. A trunk of
    bark with a hollow full of amber light for a face, mossy shoulders, branch arms that end in leafy
    fists, roots for feet, mushrooms on its side and a bird's nest in its crown of leaves."""
    m = Model("oakheart", "biped", 1.8)
    biped(m, hip=12, legx=4.4, neck=31, shoulder=28, armx=10.6)
    m.bend = -24
    BK, BK2, MO, LV, LV2, AM = "oak_log", "dark_oak_log", "moss_block", "oak_leaves", "azalea_leaves", "orange_concrete"
    # legs: thick root stumps with roots spreading out over the ground
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.4 * s
        bevel(m, b, BK, (x, 7, 0), (5.6, 10, 5.6), 0.8)
        for k, r in enumerate((-40, 10, 60, 140)):
            rr = math.radians(r)
            m.c(b, BK2, (x + math.sin(rr) * 3.4 * s, 0.8, math.cos(rr) * 3.4), (1.6, 1.4, 4), (0, r * s, 0))
        m.c(b, MO, (x, 12.2, 0), (5.8, 0.8, 5.8))
    # the trunk: bark plates, a deep hollow lit with amber, knots, a ring of moss round the shoulders
    bevel(m, "hips", BK, (0, 13.4, 0), (10, 3, 7), 0.8)
    bevel(m, "body", BK, (0, 21.6, 0), (12, 14, 8.6), 1.2)
    for x in (-4.4, -1.4, 1.6, 4.4):
        m.c("body", BK2, (x, 21, 4.4), (1, 12 - abs(x) * 0.6, 0.4))
    m.c("body", BK2, (4.6, 19, -4.4), (2, 2, 0.4))
    m.c("body", BK2, (-3, 24, -4.4), (1.6, 1.6, 0.4))
    m.c("body", MO, (0, 28.4, 0), (13, 1.6, 9.4))
    tufts(m, "body", MO, [(-5.4, 29.4, 3.4), (-1.6, 29.6, 4), (2, 29.6, 4), (5.4, 29.4, 3.4), (-4, 29.2, -3.6), (4, 29.2, -3.6)], 1.8, alt="moss_block")
    # mushrooms growing out of its side and a vine hanging down
    for (x, y, c) in ((6.4, 20, "red_concrete"), (6.4, 17, "brown_concrete")):
        m.c("body", "white_terracotta", (x + 0.6, y - 0.6, 1), (0.8, 1.6, 0.8))
        m.c("body", c, (x + 1, y + 0.4, 1), (2.6, 0.8, 2.6))
    m.c("body", "white_concrete", (7.4, 20.9, 1.6), (0.5, 0.2, 0.5))
    for k in range(3):
        m.c("body", "green_concrete", (-5.6, 26 - k * 2.4, 4.3), (0.6, 2.4, 0.4), (0, 0, (k % 2 * 2 - 1) * 10))
    # the face: a hollow in the bark, amber glow inside, heavy brow knots, a mouth crack
    m.c("head", BK, (0, 34.6, 0), (10, 7, 8.4))
    m.c("head", BK2, (0, 36.6, 4.3), (8, 1.4, 0.6), (0, 0, 0))
    m.c("head", "black_concrete", (0, 34.4, 4.25), (6, 3, 0.2))
    for s in (1, -1):
        m.c("head", AM, (1.8 * s, 34.6, 4.3), (1.6, 1.2, 0.3), light=True)
        m.c("head", BK2, (3.6 * s, 37.2, 4.4), (2.6, 1.4, 0.8), (0, 0, -18 * s))
    crack(m, "head", "front", (0, 32, 4.25), [(-2, 0), (-0.6, 0), (-0.6, -0.8), (0.8, -0.8), (0.8, 0), (2, 0)], block=AM, width=0.5)
    # the crown: branches spreading into clumps of leaves, a bird's nest with eggs
    for k, (x, z, r) in enumerate(((-4, 1, 30), (4, 0, -30), (0, -3, 0), (-2, 3, 15))):
        m.c("head", BK2, (x, 40, z), (1.6, 6, 1.6), (0, 0, r))
    for (x, y, z, w) in ((-6.4, 43, 1, 7), (6.4, 43, 0, 7), (0, 45, -2, 8), (-2.4, 44, 4, 6), (3, 46.6, 2, 5), (0, 41.6, 0, 9)):
        bevel(m, "head", LV if w > 6 else LV2, (x, y, z), (w, w * 0.6, w), 1.2)
    m.c("head", "spruce_planks", (3, 49.2, 2), (3.4, 1, 3.4))
    for t in (-0.6, 0.6):
        m.c("head", "light_blue_concrete", (3 + t, 49.9, 2), (0.8, 1, 0.8))
    for (x, y, z) in ((-8, 44, 3), (5, 47, -3), (-3, 47.6, -3)):
        m.c("head", "pink_concrete", (x, y, z), (1, 1, 1), (45, 45, 0))
    # arms: crooked branches, leafy knuckles, twig fingers
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10.6 * s
        bevel(m, a, BK, (x, 25, 0), (4.6, 7, 4.6), 0.6)
        m.c(a, BK2, (x + 1.6 * s, 27.4, -1.6), (1, 4, 1), (20, 0, -50 * s))
        bevel(m, a, BK, (x, 18.4, 0.8), (4, 7, 4), 0.6)
        bevel(m, a, LV, (x, 14, 1.2), (5.4, 3.4, 5.4), 1)
        for t in (-1.2, 0, 1.2):
            m.c(a, BK2, (x + t, 11.6, 2.2), (0.7, 3, 0.7), (20, 0, t * 10))
        m.c(a, MO, (x, 28.4, 0), (5, 1, 5))
    # more of the grove grown on him: moss creeping up the trunk front and back, amber light in the bark
    # seams, vines hanging off the arms, flowers in the moss
    from v3_kit import grow, vines
    grow(m, "body", "front", (0, 19, 4.3), 6, 4, 33, {"A": MO, "B": "green_concrete"}, cover=0.45, top=0.2, edge={"b"}, px=2, depth=0.4)
    grow(m, "body", "back", (0, 22, -4.3), 6, 6, 34, {"A": MO, "B": "green_concrete"}, cover=0.5, top=0.8, edge={"t"}, px=2, depth=0.4)
    crack(m, "body", "left", (6, 22, 0), [(2, 4), (2, 1), (-1, 1), (-1, -3)], block=AM, width=0.5)
    crack(m, "body", "right", (-6, 21, 0), [(-2, 3), (-2, 0), (1, 0), (1, -4)], block=AM, width=0.5)
    for s, a in ((1, "armL"), (-1, "armR")):
        vines(m, a, [12.8 * s], 22, 0, [6])
    for (x, z, c) in ((-3.4, 4.7, "yellow_concrete"), (2.6, 4.7, "light_blue_concrete"), (4, -4.7, "pink_concrete")):
        m.c("body", c, (x, 15.6 if z > 0 else 26, z), (1, 1, 0.4))
    m.attacks = {"roots": "slam", "thorns": "cast", "quake": "stomp", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def vault_mimic():
    """Chapter 4, The Five Keys: the fifth key's chest was never a chest. A wooden trunk with iron
    banding and a gold lock that opens into a mouth of teeth and a long tongue, one big eye in the lid,
    gold and gems spilling out, and crab legs that carry it sideways across the vault."""
    m = Model("vault_mimic", "spider", 1.6)
    m.bone("body", "root", (0, 8, 0))
    m.bone("head", "body", (0, 15.6, -5))
    m.bone("abdomen", "body", (0, 10, -6))
    m.bone("fangL", "body", (3, 11, 5))
    m.bone("fangR", "body", (-3, 11, 5))
    WD, WD2, IR, GD = "spruce_planks", "dark_oak_planks", "gray_concrete", "gold_block"
    # the chest: the lower box, planks and iron bands, the inside dark with treasure piled at the back
    bevel(m, "body", WD, (0, 11.6, 0), (14, 8, 10), 0.6)
    for x in (-6.6, 6.6):
        m.c("body", IR, (x, 11.6, 0), (0.8, 8.2, 10.2))
    for x in (-2.4, 2.4):
        m.c("body", WD2, (x, 11.6, 5.05), (0.3, 7.8, 0.2))
    m.c("body", IR, (0, 8, 0), (14.2, 0.8, 10.2))
    m.c("body", "black_concrete", (0, 15.4, 0), (12.4, 0.6, 8.4))
    for (x, z, c) in ((-3, -2.6, GD), (2, -3, GD), (4.4, -1, "emerald_block"), (-4.6, -0.6, "diamond_block"), (0, -1.6, GD)):
        m.c("body", c, (x, 16, z), (2, 1.2, 2), (0, x * 10, 0), light=c != GD)
    # teeth along the rim of the box and under the lid
    for k in range(6):
        m.c("body", "white_concrete", (-5.6 + k * 2.24, 16.4, 4.6), (1, 1.6, 0.8))
    for x in (-6.6, 6.6):
        for z in (-2, 2):
            m.c("body", "white_concrete", (x * 0.94, 16.4, z), (0.8, 1.6, 1))
    # the tongue: long, thick and wet, rolling out over the front of the chest and curling back up at the
    # end, darker down the middle, split into two tips; it lashes with the fang bone
    tip = limb(m, "fangL", "pink_concrete", (0, 15.4, 3.6), [(3.4, 2.6, (95, 0, 0)), (3.2, 2.4, (130, 0, 0)), (3, 2.2, (175, 0, 0)),
                                                             (2.6, 2.0, (215, 0, 0)), (2.2, 1.8, (250, 0, 0))])
    limb(m, "fangL", "magenta_concrete", (0, 15.95, 3.6), [(3.4, 0.6, (95, 0, 0)), (3.2, 0.6, (130, 0, 0)), (3, 0.6, (175, 0, 0))])
    for s in (1, -1):
        m.c("fangL", "pink_concrete", (tip[0] + 0.6 * s, tip[1] + 0.6, tip[2] - 0.4), (0.9, 1.6, 0.9), (-20, 0, -20 * s))
    m.c("fangR", "lime_stained_glass", (1.6, 12.4, 6.2), (0.5, 2.4, 0.5), light=True)
    # the lid: hinged at the back, curved top, the big eye in the front, a gold lock hanging below it
    m.rest("head", (-32, 0, 0))
    bevel(m, "head", WD, (0, 18, 0), (14, 4, 10), 0.6)
    m.c("head", WD, (0, 20.4, 0), (13, 1.2, 9))
    for x in (-6.6, 6.6):
        m.c("head", IR, (x, 18.4, 0), (0.8, 4.4, 10.2))
    m.c("head", IR, (0, 20.6, 0), (14.2, 0.8, 1))
    for k in range(6):
        m.c("head", "white_concrete", (-5.6 + k * 2.24, 15.6, 4.6), (1, 1.6, 0.8))
    m.c("head", "white_concrete", (0, 19.2, 5.1), (4.4, 2.8, 0.4))
    m.c("head", "red_concrete", (0, 19.2, 5.3), (2, 2, 0.2), light=True)
    m.c("head", "black_concrete", (0, 19.2, 5.4), (0.8, 1.4, 0.1))
    m.c("head", WD2, (0, 21, 5.1), (5, 0.8, 0.5), (0, 0, 0))
    m.c("head", GD, (0, 15.8, 5.6), (2.4, 2.6, 0.8))
    m.c("head", "black_concrete", (0, 15.6, 6.05), (0.6, 1, 0.1))
    # coins tumbling out the back as it runs
    for k in range(4):
        m.c("abdomen", GD, (-2 + k * 1.4, 9 + k * 0.4, -6 - k * 0.6), (1.2, 0.3, 1.2), (k * 20, 0, k * 30))
    # crab legs: two jointed legs on each side plus two short front claws, iron-shod tips
    zs = (3, 0.6, -1.8, -4.2)
    for i, z in enumerate(zs):
        for s, side in ((1, "L"), (-1, "R")):
            name = f"leg{side}{i + 1}"
            m.bone(name, "body", (7 * s, 10, z))
            ang = (30 - i * 20)
            tip = limb(m, name, WD2, (7 * s, 10, z), [(5, 1.6, (ang, 0, -70 * s)), (7, 1.3, (ang * 0.8, 0, -160 * s))], joint=WD)
            m.c(name, IR, tip, (1.4, 1.4, 1.4))
    # corner brackets and studs, a second eye half-open on the lid, a drool of slime
    for x in (-6.6, 6.6):
        for z in (-4.6, 4.6):
            m.c("body", GD, (x, 15, z), (1, 1, 1))
            m.c("body", GD, (x, 8.4, z), (1, 1, 1))
    m.c("head", "white_concrete", (4.4, 19.6, 5.05), (2, 1.4, 0.3))
    m.c("head", "black_concrete", (4.4, 19.3, 5.25), (0.8, 0.8, 0.1))
    m.c("head", WD2, (4.4, 20.4, 5.25), (2.2, 0.6, 0.2))
    m.c("body", "lime_stained_glass", (-3.4, 13.8, 5.4), (0.6, 2.6, 0.6), light=True)
    m.attacks = {"leap": "leap", "coins": "spit", "bite": "fang", "minions": "drum"}
    m.melee = "fang"
    return m


@model
def crypt_knight():
    """Chapter 5, The King Wakes: the first knight to answer the king. Rusted iron plate gone green at the
    joints, a torn purple tabard with the king's sign, a horned helm with a slit that glows, a battered
    tower shield and a spiked flail on a chain."""
    m = Model("crypt_knight", "biped", 1.7)
    biped(m, hip=13, legx=3.8, neck=31, shoulder=29, armx=9.4)
    m.bone("cape", "body", (0, 28.4, -3.6))
    m.bone("flail", "armR", (-9.4, 12, 2))
    m.bone("shield", "armL", (9.4, 18, 0))
    m.hold = {"flail": 20, "shield": 0}
    m.bend = -36
    IR, IR2, RU, TB, GD, GL = "polished_andesite", "iron_block", "weathered_copper", "purple_concrete", "gold_block", "light_blue_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.8 * s
        bevel(m, b, IR, (x, 9.6, 0), (4.4, 7, 4.6), 0.5)
        m.c(b, RU, (x, 6.4, 2.4), (2.6, 2, 0.6))
        bevel(m, b, IR, (x, 3, 0.4), (4.8, 6, 5.4), 0.5)
        m.c(b, "polished_deepslate", (x, 0.6, 1), (5, 1.2, 6.2))
    bevel(m, "hips", "chain", (0, 12.6, 0), (9.6, 3.4, 5.6), 0.4)
    bevel(m, "body", IR, (0, 21.6, 0), (10.6, 12, 6.6), 1)
    m.c("body", IR2, (0, 23.6, 3.35), (6, 6, 0.3))
    for (x, y) in ((-3.6, 26.4), (3, 18), (-2, 17.4)):
        m.c("body", RU, (x, y, 3.4), (2, 1.4, 0.2))
    # the tabard: purple, torn, the king's crown sign in gold
    m.c("body", TB, (0, 20, 3.5), (5, 16, 0.4))
    hem(m, "body", TB, -2.5, 2.5, 12, 3.5, 0.4, 3, long=2.6, short=1)
    paint(m, "body", "front", (0, 23, 3.75), ["G.G.G", "GGGGG", ".GGG."], {"G": GD}, px=0.8, depth=0.2)
    # the king's cloak: purple, heavy, torn at the hem, pinned at both shoulders with gold
    m.c("cape", TB, (0, 18.6, -4.0), (11, 19.6, 0.5))
    m.c("cape", "purple_terracotta", (0, 27.6, -4.3), (11.4, 1.6, 0.5))
    hem(m, "cape", TB, -5.5, 5.5, 8.8, -4.0, 0.5, 6, long=3.4, short=1.4, seed=2)
    paint(m, "cape", "back", (0, 20, -4.25), ["G.G.G", "GGGGG", ".GGG."], {"G": GD}, px=1.4, depth=0.2)
    for s in (1, -1):
        m.c("body", GD, (4.6 * s, 28, -3.4), (1.4, 1.4, 0.6))
    # pauldrons stacked in two plates, rusty rivets
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 9.4 * s
        bevel(m, a, IR, (x + 0.6 * s, 29.4, 0), (6, 2.6, 6.6), 0.6, (0, 0, -16 * s), (x, 29, 0))
        bevel(m, a, IR2, (x + 1.6 * s, 27.4, 0), (5, 1.8, 6), 0.4, (0, 0, -26 * s), (x, 29, 0))
        m.c(a, RU, (x + 2.6 * s, 30, 0), (0.6, 0.6, 0.6), (0, 0, -16 * s))
        bevel(m, a, "chain", (x, 23.6, 0), (3.6, 6, 3.8), 0.4)
        bevel(m, a, IR, (x, 17.4, 0.6), (4.2, 6, 4.4), 0.5)
        bevel(m, a, "polished_deepslate", (x, 13.4, 1), (3.8, 2.6, 4), 0.4)
    # the helm: rounded, a visor slit that glows, curling horns, a broken crest
    bevel(m, "head", IR, (0, 35.4, 0.4), (8.4, 8.4, 8.4), 1.2)
    m.c("head", "black_concrete", (0, 35.6, 4.65), (6, 1.2, 0.2))
    m.c("head", GL, (0, 35.6, 4.75), (4.4, 0.6, 0.1), light=True)
    m.c("head", "black_concrete", (0, 33.2, 4.65), (0.8, 2.4, 0.2))
    for y in (32.6, 33.8):
        for x in (-2, -1, 1, 2):
            m.c("head", "black_concrete", (x, y, 4.65), (0.4, 0.4, 0.2))
    mhorn(m, "head", "bone_block", (4.2, 37, 0), 3, (0, 0, -70), (0, 0, 32), 1.6, 0.8)
    for k in range(3):
        m.c("head", TB, (0, 40.4 + k * 0.6, -1.6 + k * 1.4), (0.8, 1.4, 1.4))
    m.c("head", RU, (2.6, 38.6, 3.4), (1.6, 1.2, 0.3))
    # the tower shield: dented iron with a gold rim and the king's sign
    m.c("shield", IR, (12.4, 18, 1), (1, 13, 8))
    m.c("shield", GD, (12.95, 18, 1), (0.3, 13.4, 8.4))
    m.c("shield", IR2, (13.15, 18, 1), (0.3, 12, 7))
    paint(m, "shield", "left", (13.3, 19, 1), ["G.G.G", "GGGGG", ".GGG.", "..G..", "..G.."], {"G": GD}, px=1, depth=0.2)
    m.c("shield", RU, (13.3, 13.6, -1.4), (0.2, 1.6, 2))
    # the flail: a short haft, a chain and a spiked iron ball
    m.c("flail", "dark_oak_log", (-9.4, 14.6, 2), (1.2, 6, 1.2))
    m.c("flail", "chain", (-9.4, 19.4, 2), (0.6, 4, 0.6))
    bevel(m, "flail", IR, (-9.4, 22.8, 2), (3.4, 3.4, 3.4), 0.6)
    for r in ((0, 0, 0), (90, 0, 0), (0, 0, 90)):
        m.c("flail", IR2, (-9.4, 22.8, 2), (0.8, 5.6, 0.8), r)
    m.attacks = {"flail": "sweep", "shield": "lunge", "souls": "cast", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def iron_tusk():
    """Chapter 6, The Iron Tusk: a war boar the smiths armoured for the raiders. Bristly brown hide, iron
    plates riveted down its back, a spiked iron face guard, two tusks capped in iron, a chain dragging
    from its collar and a little war banner on its saddle."""
    m = Model("iron_tusk", "quad", 1.5)
    quad(m, body_y=13, legx=5, legz_front=7, legz_back=-8, neck_y=15, neck_z=11)
    HI, HI2, BR, IR, IR2 = "brown_terracotta", "brown_concrete", "spruce_planks", "iron_block", "polished_andesite"
    for s, (b, z) in ((1, ("legFL", 7)), (-1, ("legFR", 7)), (1, ("legBL", -8)), (-1, ("legBR", -8))):
        quad_leg(m, b, 5 * s, 12, z, 4.4, HI, HI2, "polished_deepslate")
        m.c(b, IR2, (5 * s, 9.4, z + 2.3), (3, 3, 0.4))
    # body: a barrel of bristly hide, a ridge of dark bristles down the spine
    bevel(m, "body", HI, (0, 15, -0.4), (12, 10, 19), 2)
    bevel(m, "body", HI, (0, 14.6, 6.6), (11, 9.6, 6), 2)
    for k in range(6):
        m.c("body", HI2, (0, 20.6, 7 - k * 3), (1.6, 1.8 + (k % 2) * 0.6, 2), (-20, 0, 0))
    # iron plates riveted down the back, overlapping, and a skirt of chain under the belly
    for k, z in enumerate((4, -0.6, -5.2)):
        bevel(m, "body", IR2 if k % 2 else IR, (0, 19.8, z), (13, 1.6, 5), 0.4)
        for s in (1, -1):
            m.c("body", IR2 if k % 2 else IR, (6.6 * s, 16.6, z), (0.8, 5.6, 5))
            m.c("body", "gold_block", (7.05 * s, 18.6, z), (0.3, 0.6, 0.6))
    for z in (-6, -2, 2, 6):
        m.c("body", "chain", (0, 9.8, z), (10, 0.4, 0.4))
    # a small saddle with a war banner
    m.c("body", BR, (0, 21, -1.2), (6, 1.2, 6))
    m.c("body", "dark_oak_log", (-2.4, 25, -4), (0.6, 9, 0.6))
    m.c("body", "red_wool", (-2.4, 27.4, -5.6), (0.3, 4, 3))
    paint(m, "body", "left", (-2.2, 27.4, -5.6), [".W.", "WWW", ".W."], {"W": "white_concrete"}, px=0.8, depth=0.1)
    # tail: a short curl with a tuft
    limb(m, "tail", HI, (0, 18, -10), [(3, 1.2, (-140, 0, 0)), (2, 1, (-200, 0, 0))])
    m.c("tail", HI2, (0, 15.4, -11.4), (1.6, 1.6, 1.6))
    # head: long snout, an iron face guard with a spike, small red eyes, ears, iron-capped tusks
    bevel(m, "head", HI, (0, 15, 13), (8.6, 8, 7), 1.2)
    bevel(m, "head", HI, (0, 13, 17.4), (6.4, 5, 5), 0.8)
    m.c("head", "pink_terracotta", (0, 13, 20), (5, 3.6, 0.4))
    for s in (1, -1):
        m.c("head", "black_concrete", (1.2 * s, 13.4, 20.25), (1, 1.2, 0.1))
        m.c("head", "redstone_block", (3.2 * s, 16.2, 16.55), (1, 0.8, 0.1), light=True)
        m.c("head", HI, (4 * s, 19.2, 11.6), (1.6, 3, 2.4), (-20, 0, -30 * s))
        tip = limb(m, "head", "white_concrete", (3 * s, 12, 18.6), [(3, 1.2, (-50, 0, -30 * s)), (2.4, 1, (-20, 0, -10 * s))])
        m.c("head", IR, tip, (1.2, 1.4, 1.2), (-20, 0, -10 * s))
    bevel(m, "head", IR, (0, 17.6, 14.4), (7.6, 2.6, 6), 0.5)
    m.c("head", IR2, (0, 17.6, 17.5), (6.6, 2, 0.4))
    m.c("head", IR, (0, 20.4, 15.6), (1.4, 3, 1.4), (30, 0, 0))
    bevel(m, "jaw", HI2, (0, 10.8, 16), (5.4, 1.6, 5), 0.4)
    # a heavy collar with a broken chain dragging behind
    m.c("head", IR2, (0, 15, 9.6), (10, 2, 2))
    m.c("head", "chain", (4.6, 11, 9), (0.6, 6, 0.6), (20, 0, 10))
    m.attacks = {"charge": "charge", "toss": "toss", "quake": "rear", "roar": "howl"}
    m.melee = "bite"
    return m


@model
def reef_hulk():
    """Chapter 7, Tides of the Drowned: a drowned brute that has lain on the reef so long the reef grew on
    it. Pale blue-green skin, coral growing out of its shoulders and back in four colours, barnacles,
    kelp hanging off its arms, glowing sea-lantern eyes, and a ship's anchor for a club."""
    m = Model("reef_hulk", "biped", 1.5)
    biped(m, hip=12, legx=4, neck=29, shoulder=27, armx=10.6)
    m.bone("anchor", "armR", (-10.6, 12, 2))
    m.hold = {"anchor": 10}
    m.bend = -30
    m.rest("body", (-12, 0, 0))
    m.rest("head", (14, 0, 0))
    SK, SK2, CL, KE = "prismarine", "dark_prismarine", "light_blue_terracotta", "green_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        bevel(m, b, "cyan_terracotta", (x, 8.6, 0), (5, 7, 5), 0.6)
        hem(m, b, "cyan_terracotta", x - 2.5, x + 2.5, 5.4, 2.4, 0.4, 3, long=2, short=0.8)
        bevel(m, b, SK, (x, 2.4, 0.6), (4.6, 4.8, 5.6), 0.6)
    bevel(m, "hips", "cyan_terracotta", (0, 12.6, 0), (10.6, 3, 6.4), 0.5)
    m.c("hips", "brown_terracotta", (0, 13.6, 0), (10.8, 1, 6.6))
    # a hulking torso, rope still tied round it from the ship it sank with, barnacles
    bevel(m, "body", SK, (0, 20.6, 0), (13, 12, 8), 1.4)
    bevel(m, "body", SK, (0, 22, 3.2), (11, 7, 3), 1)
    m.c("body", SK2, (0, 21.6, 4.75), (6, 3, 0.2))
    m.c("body", "brown_terracotta", (0, 20, 0), (1.2, 13, 8.6), (0, 0, 40))
    for (x, y, z) in ((-4, 17, 4.2), (4.6, 24, 3.6), (-5.6, 24.6, -4.1), (2, 17.6, -4.1), (5, 15.6, 3.8)):
        m.c("body", "white_terracotta", (x, y, z), (1.4, 1.4, 0.6))
        m.c("body", "light_gray_concrete", (x, y, z + (0.35 if z > 0 else -0.35)), (0.6, 0.6, 0.2))
    # coral growing out of shoulders and back
    for (x, y, z, c, h, r) in ((-5, 28, -2, "fire_coral_block", 4, -20), (-3, 29, -3.6, "horn_coral_block", 3, 10), (4.6, 28.4, -2.4, "tube_coral_block", 4.6, 25),
                               (2.4, 27, -4.4, "brain_coral_block", 2.6, 0), (0, 25, -4.4, "fire_coral_block", 3, -10), (-2, 21, -4.4, "tube_coral_block", 2.4, 30)):
        m.c("body", c, (x, y, z), (1.4, h, 1.4), (-20, 0, r))
        m.c("body", c, (x + r * 0.05, y + h * 0.3, z - 0.6), (1, h * 0.6, 1), (-40, 0, r * 2))
    bevel(m, "body", "brain_coral_block", (-5.6, 27, 1), (3, 2, 3), 0.5)
    # arms: huge forearms, kelp hanging, barnacled knuckles
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10.6 * s
        bevel(m, a, SK, (x, 24, 0), (5, 7, 5.4), 0.7)
        bevel(m, a, SK, (x, 16.6, 0.6), (6, 8, 6.2), 0.8)
        bevel(m, a, SK2, (x, 12, 1), (5, 2.6, 5), 0.6)
        for t in (-1.4, 1.4):
            m.c(a, KE, (x + t, 18, -3.2), (0.8, 7, 0.4), (10, 0, t * 4))
        m.c(a, "white_terracotta", (x, 12.6, 3.6), (1.2, 1.2, 0.4))
    # head: low and heavy, a crooked jaw, glowing eyes, kelp for hair
    bevel(m, "head", SK, (0, 32, 1.4), (8.4, 7, 8), 1)
    paint(m, "head", "front", (0, 33, 5.45), ["KK...KK", ".LK.KL.", "......."], {"K": "black_concrete", "L": ("sea_lantern", 0.4, True)}, px=0.9, depth=0.3)
    m.c("head", SK2, (0, 29.4, 4.6), (6.4, 2.4, 2))
    for x in (-2.2, 0, 2.2):
        m.c("head", "white_terracotta", (x, 30.6, 5.7), (0.8, 1.2, 0.4))
    for k, x in enumerate((-3.4, -1.2, 1, 3.2)):
        m.c("head", KE, (x, 32, -2.8), (1.2, 6 + k % 2 * 2, 0.6), (8, 0, 0))
    # the anchor: an iron shaft, a ring at the top, two flukes curving up, rope wound round it
    m.c("anchor", "iron_block", (-10.6, 18, 2), (1.6, 18, 1.6))
    m.c("anchor", "gray_concrete", (-10.6, 26, 2), (6, 1.2, 1.2))
    for s in (1, -1):
        limb(m, "anchor", "iron_block", (-10.6, 10, 2), [(4, 1.6, (-80 * s, 0, 0)), (3, 1.4, (-30 * s, 0, 0))])
    m.c("anchor", "iron_block", (-10.6, 28.6, 2), (0.8, 2.6, 2.6))
    m.c("anchor", "brown_terracotta", (-10.6, 21, 2), (2, 2, 2))
    m.c("anchor", "oxidized_copper", (-10.6, 15, 2), (1.8, 1, 1.8))
    m.attacks = {"anchor": "slam", "wave": "sweep", "minions": "roar", "pull": "cast"}
    m.melee = "swipe"
    return m


@model
def ember_knight():
    """Chapter 8, The Ember Court: the court's champion. Plate armour forged from nether brick and gold,
    the visor a grille of fire, a mantle of flame on the shoulders, three blaze rods turning round him
    and a sword whose blade is a bar of fire."""
    m = Model("ember_knight", "biped", 1.45)
    biped(m, hip=13, legx=3.8, neck=31, shoulder=29, armx=9.4)
    m.bone("sword", "armR", (-9.4, 12, 2))
    m.bone("ring1", "body", (0, 22, 0))
    m.hold = {"sword": 20}
    m.bend = -36
    NB, NB2, GD, FL, FL2, BL = "nether_bricks", "red_nether_bricks", "gold_block", "orange_concrete", "yellow_concrete", "magma_block"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.8 * s
        bevel(m, b, NB, (x, 9.6, 0), (4.4, 7, 4.6), 0.5)
        m.c(b, GD, (x, 7, 2.4), (3, 1.4, 0.5))
        bevel(m, b, NB2, (x, 3.2, 0.4), (4.8, 6, 5.4), 0.5)
        m.c(b, GD, (x, 0.6, 1), (5, 1.2, 6.2))
        m.c(b, FL, (x, 4, 3.15), (1.6, 2, 0.2), light=True)
    bevel(m, "hips", NB2, (0, 12.6, 0), (9.6, 3.4, 5.6), 0.4)
    for x in (-3, 0, 3):
        m.c("hips", NB, (x, 10.6, 3), (2.6, 4, 0.6))
        m.c("hips", GD, (x, 8.8, 3.2), (2.6, 0.6, 0.4))
    # breastplate: nether brick with gold edges and a magma heart that shows through a gold sunburst
    bevel(m, "body", NB, (0, 21.6, 0), (10.6, 12, 6.6), 1)
    bevel(m, "body", NB2, (0, 23, 2.8), (8, 7, 1.6), 0.5)
    m.c("body", BL, (0, 23, 3.7), (3, 3, 0.4), light=True)
    paint(m, "body", "front", (0, 23, 3.95), ["G.G.G", ".....", "G...G", ".....", "G.G.G"], {"G": GD}, px=1, depth=0.3)
    band(m, "body", GD, (0, 16.6, 0), (10.8, 1.2, 6.8))
    # shoulders: gold-rimmed pauldrons with flames licking up off them
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 9.4 * s
        bevel(m, a, NB, (x + 0.6 * s, 29.4, 0), (6, 2.8, 6.6), 0.6, (0, 0, -16 * s), (x, 29, 0))
        m.c(a, GD, (x + 1.8 * s, 28, 0), (4.4, 0.6, 6.8), (0, 0, -16 * s), (x, 29, 0))
        for k, (dz, h) in enumerate(((-2, 3), (0, 4.4), (2, 2.6))):
            m.c(a, FL if k != 1 else FL2, (x + 1 * s, 31.4 + h / 2, dz), (1.2, h, 1.2), (0, 0, -12 * s), light=True)
        bevel(m, a, NB2, (x, 23.4, 0), (3.6, 6, 3.8), 0.4)
        bevel(m, a, NB, (x, 17.4, 0.6), (4.2, 6, 4.4), 0.5)
        m.c(a, GD, (x, 15, 0.6), (4.4, 0.8, 4.6))
        bevel(m, a, NB2, (x, 13.2, 1), (3.8, 2.6, 4), 0.4)
    # the helm: a tall great-helm with a grille visor of fire and a gold crest
    bevel(m, "head", NB, (0, 35.6, 0.4), (8, 9, 8), 1)
    for x in (-2.4, -0.8, 0.8, 2.4):
        m.c("head", FL, (x, 35.4, 4.45), (0.8, 4, 0.2), light=True)
    m.c("head", GD, (0, 37.8, 4.5), (7, 0.8, 0.3))
    m.c("head", GD, (0, 33, 4.5), (7, 0.8, 0.3))
    m.c("head", GD, (0, 41, 0.4), (1.2, 3, 8))
    for k in range(3):
        m.c("head", FL if k % 2 else FL2, (0, 43 + k * 0.4, 2.6 - k * 2.6), (0.8, 2.4, 1.6), (-10, 0, 0), light=True)
    # three blaze rods slowly turning round him
    for k in range(3):
        a = math.radians(k * 120)
        x, z = math.sin(a) * 11, math.cos(a) * 11
        m.c("ring1", FL2, (x, 22 + k * 2, z), (1, 6, 1), (0, 0, 20), light=True)
        m.c("ring1", FL, (x, 25.4 + k * 2, z), (1.6, 1.4, 1.6), (45, 0, 45), light=True)
    # the sword: a gold hilt, a nether-brick guard and a blade that is a bar of fire
    m.c("sword", GD, (-9.4, 12.6, 2), (1.2, 4, 1.2))
    m.c("sword", NB, (-9.4, 15, 2), (1.6, 1.2, 6))
    m.c("sword", GD, (-9.4, 10.4, 2), (1.8, 1.2, 1.8))
    m.c("sword", BL, (-9.4, 24, 2), (1, 16, 2.6), light=True)
    m.c("sword", FL2, (-9.4, 24, 2), (1.2, 14, 1), light=True)
    m.c("sword", FL, (-9.4, 32.6, 2), (0.8, 2, 1.6), (45, 0, 0), light=True)
    m.attacks = {"sword": "sweep", "fire": "cast", "slam": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def choirmaster():
    """Chapter 9, The Bone Choir: the skeleton who leads the choir of the dead. A tall thin skeleton in a
    black choir robe with a white surplice and a red stole, a bell hanging round its neck, a hymn book
    floating open in front of it and a long conductor's baton tipped with a soul flame; its jaw hangs
    open mid-note."""
    m = Model("choirmaster", "biped", 1.5)
    biped(m, hip=13, legx=3, neck=32, shoulder=30, armx=8)
    m.bone("jaw", "head", (0, 33.6, 2))
    m.bone("baton", "armR", (-8, 13, 2))
    m.bone("book", "body", (0, 22, 8))
    m.hold = {"baton": 40}
    m.bend = -60
    BN, BN2, RB, SU, ST, GD, SO = "bone_block", "calcite", "black_wool", "white_wool", "red_concrete", "gold_block", "light_blue_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, BN2, (3 * s, 1.4, 1.6), (2.6, 2.8, 4))
    # robe: long and black, a white surplice over it with a lace hem, a red stole with gold crosses
    stack(m, "hips", RB, 0, 1, 0, [(11, 4, 8.4), (10, 4, 7.6), (9, 5, 7)])
    bevel(m, "body", RB, (0, 22, 0), (9, 14, 6), 0.8)
    stack(m, "body", SU, 0, 13.6, 0, [(10.4, 6, 7.4), (9.6, 6, 6.6)])
    hem(m, "body", SU, -5.2, 5.2, 13.8, 3.7, 0.4, 7, long=1.4, short=0.6)
    hem(m, "body", SU, -5.2, 5.2, 13.8, -3.7, 0.4, 7, long=1.4, short=0.6, seed=3)
    for s in (1, -1):
        m.c("body", ST, (1.6 * s, 21, 3.5), (1.4, 18, 0.4))
        m.c("body", GD, (1.6 * s, 14, 3.75), (1, 1.6, 0.2))
        m.c("body", GD, (1.6 * s, 14.4, 3.75), (1.6, 0.5, 0.2))
    m.c("body", BN2, (0, 31.4, 0.4), (1.8, 3.6, 1.8))
    # a bone collar and the bell hanging at the throat
    m.c("body", BN, (0, 29, 0), (8, 1.4, 6))
    m.c("body", "chain", (0, 27.6, 3.4), (0.4, 2, 0.4))
    stack(m, "body", GD, 0, 23.6, 3.6, [(3.4, 1, 3), (2.6, 1.4, 2.4), (1.6, 1.2, 1.6)])
    m.c("body", "brown_terracotta", (0, 23.4, 3.6), (0.8, 0.6, 0.8))
    # arms: wide sleeves, thin bone forearms, long finger bones
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8 * s
        bevel(m, a, RB, (x, 25.6, 0), (3.6, 7, 4), 0.5)
        stack(m, a, SU, x, 19, 0, [(4.6, 2, 4.8)])
        m.c(a, BN2, (x, 16.4, 0.8), (1.6, 6, 1.6))
        m.c(a, BN, (x, 13.2, 1.2), (2.4, 1.6, 2.4))
        for t in (-0.7, 0, 0.7):
            m.c(a, BN2, (x + t, 11.6, 1.6), (0.4, 2, 0.4))
    # the skull: hollow eyes lit by soul fire, the jaw hanging open singing, a skullcap
    bevel(m, "head", BN2, (0, 37, 0.6), (7, 6.4, 7), 1)
    paint(m, "head", "front", (0, 37.6, 4.15), ["KK.KK", "KS.SK", "..K.."], {"K": "black_concrete", "S": (SO, 0.3, True)}, px=1, depth=0.3)
    bevel(m, "jaw", BN2, (0, 32.6, 1.8), (5, 1.6, 4.6), 0.4, (24, 0, 0), (0, 33.6, 0))
    m.c("jaw", "black_concrete", (0, 33.4, 2.6), (4, 1.2, 3), (24, 0, 0), (0, 33.6, 0))
    paint(m, "head", "front", (0, 34.8, 4.15), ["W.W.W"], {"W": BN}, px=0.8, depth=0.4)
    m.c("head", ST, (0, 40.4, 0.6), (5.6, 1, 5.6))
    m.c("head", ST, (0, 41.1, 0.6), (3.6, 0.6, 3.6))
    m.c("head", GD, (0, 41.6, 0.6), (0.8, 0.6, 0.8))
    # the hymn book floating open in front, its pages glowing, a ribbon trailing
    m.c("book", "brown_terracotta", (-1.8, 22, 8), (3.4, 0.6, 4.4), (-30, -12, 8))
    m.c("book", "brown_terracotta", (1.8, 22, 8), (3.4, 0.6, 4.4), (-30, 12, -8))
    m.c("book", "white_concrete", (-1.8, 22.4, 8), (3, 0.3, 4), (-30, -12, 8), light=True)
    m.c("book", "white_concrete", (1.8, 22.4, 8), (3, 0.3, 4), (-30, 12, -8), light=True)
    for k in range(3):
        m.c("book", "black_concrete", (1.8, 22.6, 7 + k * 1.2), (2, 0.1, 0.3), (-30, 12, -8))
    m.c("book", ST, (0, 20, 10.2), (0.4, 3, 0.2))
    # musical notes of soul fire drifting up from it
    for k, (x, y, z) in enumerate(((-3, 27, 8), (2.4, 29, 9), (-1, 31, 10))):
        m.c("book", SO, (x, y, z), (1, 1, 0.3), light=True)
        m.c("book", SO, (x + 0.4, y + 1.2, z), (0.3, 2, 0.3), light=True)
    # the baton: long white bone, a gold band, a soul flame on the tip
    m.c("baton", BN2, (-8, 20, 2), (0.6, 14, 0.6))
    m.c("baton", GD, (-8, 14, 2), (1, 1.4, 1))
    m.c("baton", SO, (-8, 27.6, 2), (1.2, 1.6, 1.2), light=True)
    m.c("baton", "soul_lantern", (-8, 27.6, 2), (0.8, 0.8, 0.8), light=True)
    m.attacks = {"hymn": "cast", "souls": "double", "minions": "roar", "bell": "slam"}
    m.melee = "swipe"
    return m


@model
def sculk_herald():
    """Chapter 10, The Listener Below: the thing that wakes the Listener. A floating mass of sculk shaped
    like a ribcage with a shrieker for a mouth, sensor tendrils sweeping the air, soul-blue light pulsing
    from its veins and two long clawed arms; it has no eyes, it hears you."""
    m = Model("sculk_herald", "float", 1.6)
    m.bone("core", "root", (0, 12, 0))
    m.bone("head", "core", (0, 28, 1))
    m.mbone("armL", "core", (8, 25, 0))
    m.bone("ring1", "core", (0, 18, 0))
    m.bone("ring2", "head", (0, 36, 0))
    m.no_elbows = True
    SC, SC2, DK, BN, GL, GL2 = "sculk", "sculk_catalyst", "black_concrete", "bone_block", "cyan_concrete", "light_blue_concrete"
    # the body: a spine and ribcage of bone overgrown with sculk, a glowing heart in the middle
    m.c("core", BN, (0, 18, -3), (2, 18, 2))
    for k, y in enumerate((14, 17, 20, 23, 26)):
        w = 10 - abs(k - 2) * 1.4
        for s in (1, -1):
            m.c("core", BN, (w / 2 * s, y, 0), (1.2, 1.2, 6))
        m.c("core", BN, (0, y, 3), (w, 1.2, 1.2))
    bevel(m, "core", SC, (0, 20, -0.6), (8, 13, 5), 1)
    m.c("core", SC2, (0, 20.6, 1.6), (3.4, 3.4, 3.4), light=True)
    m.c("core", GL, (0, 20.6, 1.6), (1.6, 1.6, 3.8), light=True)
    # the lower half trails away into sculk tendrils
    for k in range(8):
        a = math.radians(k * 45)
        L = 8 - k % 3 * 2
        x, z = math.sin(a) * 3, math.cos(a) * 2.4
        m.c("core", SC, (x, 11 - L / 2, z), (1.6, L, 1.6), (math.cos(a) * 20, 0, -math.sin(a) * 20), (x, 11, z))
        if k % 2 == 0:
            m.c("core", GL, (x * 1.4, 11 - L, z * 1.4), (0.6, 0.6, 0.6), light=True)
    # veins of light running over it
    for (x, y, h) in ((-3, 18, 6), (3, 22, 5), (-1.6, 25, 3)):
        m.c("core", GL2, (x, y, 1.95), (0.4, h, 0.3), light=True)
    # the head: a shrieker mouth with bone teeth, no eyes, sensor tendrils sweeping up and back
    bevel(m, "head", SC, (0, 31, 1), (8, 6, 7.4), 1)
    m.c("head", "calcite", (0, 28.6, 2.4), (7, 1.2, 5))
    for k in range(4):
        a = math.radians(k * 90 + 45)
        m.c("head", BN, (math.sin(a) * 2.6, 29.4, 2.4 + math.cos(a) * 1.6), (1, 1.8, 1), (0, k * 90, 0))
    m.c("head", GL, (0, 28.2, 2.4), (3, 0.4, 3), light=True)
    for k, (x, z, r) in enumerate(((-3, -1, (-30, 0, 30)), (3, -1, (-30, 0, -30)), (-1.4, -2.6, (-50, 0, 12)), (1.4, -2.6, (-50, 0, -12)))):
        tip = limb(m, "head", SC, (x, 34, z), [(5, 1, r), (4, 0.8, (r[0] - 20, 0, r[2] * 1.4))])
        m.c("head", GL, tip, (1, 1, 1), light=True)
    # arms: thin sculk arms with long bone claws, glowing at the joints
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8 * s
        tip = limb(m, a, SC, (x, 25, 0), [(7, 2, (20, 0, -20 * s)), (7, 1.6, (-40, 0, -6 * s))], joint=SC2)
        tx, ty, tz = tip
        for t in (-0.8, 0, 0.8):
            m.c(a, BN, (tx + t, ty - 1.6, tz + 1), (0.5, 3, 0.5), (30, 0, t * 10))
        m.c(a, GL, (x + 1.2 * s, 22, 1.6), (0.6, 0.6, 0.6), light=True)
    # sound rings drifting off it, the blue it hears you with
    for k in range(8):
        a = math.radians(k * 45)
        m.c("ring1", GL2, (math.sin(a) * 10, 18, math.cos(a) * 10), (3.6, 0.3, 0.6), (0, k * 45 + 90, 0), light=True)
    for k in range(6):
        a = math.radians(k * 60)
        m.c("ring2", GL, (math.sin(a) * 6.4, 38, math.cos(a) * 6.4), (2.4, 0.3, 0.5), (0, k * 60 + 90, 0), light=True)
    m.attacks = {"sonic": "pulse", "darkness": "raise", "claws": "swipe", "minions": "spin"}
    m.melee = "swipe"
    return m
