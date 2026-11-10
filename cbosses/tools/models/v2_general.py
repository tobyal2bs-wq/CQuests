"""General (spot) bosses, hand built."""
import math
from models import model, biped, horn, mhorn, limb, mlimb, taper, quad
from build import Model
from kit import paint, crack, band, hem, tufts, spikes, plate, stack, mirror_rows, bevel

SPAWN, DEATH = {}, {}


@model
def slagheart():
    """A hunched stone colossus with one oversized fist. Its body is a molten core held in by grey stone
    plates; the gaps between the plates glow, so the cracks follow the armour instead of being random."""
    m = Model("slagheart", "biped", 1.5)
    biped(m, hip=14, legx=6.5, neck=34, shoulder=35, armx=15)
    m.bone("jaw", "head", (0, 31, 10))
    m.bend = -12
    m.rest("body", (-14, 0, 0))
    m.rest("head", (14, 0, 0))
    for a in ("armL", "armR"):
        m.rest(a, (14, 0, 0))
    PL, PL2, DK, HI = "polished_andesite", "andesite", "polished_deepslate", "smooth_stone"
    CORE, HOT = "redstone_block", "orange_concrete"
    # legs: a plated thigh, dark shin, broad foot with toes
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 6.5 * s
        m.c(b, CORE, (x, 13.6, 0), (6, 1, 6), light=True)
        bevel(m, b, PL, (x, 11.6, 0.3), (8, 4.6, 8), 0.8)
        m.c(b, PL2, (x + 0.6 * s, 11.6, 4.5), (5, 3.4, 0.6))
        bevel(m, b, DK, (x, 5.6, 0.2), (6.6, 7, 6.6), 0.8)
        m.c(b, HI, (x, 5.8, 3.7), (4.4, 4.4, 0.6))
        bevel(m, b, PL, (x, 1.4, 1.6), (9, 2.8, 11), 0.7)
        for t in (-2.8, 0, 2.8):
            m.c(b, PL2, (x + t, 1.1, 7.5), (2.2, 2.2, 1.8))
    # hips: dark belt of blocks with a glowing seam
    m.c("hips", CORE, (0, 16, 0), (16, 2.4, 10), light=True)
    bevel(m, "hips", DK, (0, 17.2, 0), (18, 3, 11), 0.8)
    # torso: a glowing core wrapped in plates with narrow gaps between them
    m.c("body", CORE, (0, 27, 0.5), (18, 14, 11), light=True)
    m.c("body", HOT, (0, 27, 6.1), (3, 9, 0.4), light=True)
    m.c("body", "shroomlight", (0, 27.6, 6.3), (1.4, 4, 0.4), light=True)
    for sx in (1, -1):
        bevel(m, "body", PL, (5.9 * sx, 29.4, 2.2), (8.4, 9, 10), 1.0)          # chest plate
        bevel(m, "body", PL2, (6.6 * sx, 22.2, 2.4), (7.2, 4.6, 9.4), 0.9)      # belly plate
        bevel(m, "body", PL, (10.6 * sx, 36.2, -0.4), (8, 5.2, 13), 1.1)        # shoulder boulder
        m.c("body", HI, (10.6 * sx, 39, -0.4), (5.4, 0.8, 9))
        bevel(m, "body", PL2, (4.9 * sx, 28, -4.6), (9.4, 15, 3.4), 0.9)            # back plate
        bevel(m, "body", PL2, (9.4 * sx, 27, 0.5), (2.4, 12, 9), 0.6)             # flank
        m.c("body", DK, (5.6 * sx, 32.6, 7.6), (6, 1.2, 0.8))                  # chest rim
    bevel(m, "body", PL, (0, 37.4, -1), (10, 3.6, 12), 1.0)                     # yoke over the neck
    # back: two chimney vents
    for sx in (1, -1):
        stack(m, "body", DK, 4.6 * sx, 33, -6.8, [(4.4, 2.4, 4.4), (3.4, 3.6, 3.4), (4, 1.2, 4)])
        m.c("body", HOT, (4.6 * sx, 40.3, -6.8), (2.2, 0.4, 2.2), light=True)
    # head: sunk in front of the chest. Angry brow, slit eyes, a lit maw with stone teeth.
    m.c("head", CORE, (0, 33.4, 9.2), (8, 6, 6), light=True)
    bevel(m, "head", PL, (0, 35.6, 9.4), (10, 3.6, 7.6), 0.8)
    paint(m, "head", "front", (0, 34.6, 13.2), [
        "bb......bb",
        ".bbb..bbb.",
        "..eE..Ee..",
    ], {"b": DK, "e": (HOT, 0.4, True), "E": ("shroomlight", 0.4, True)}, px=1.0, depth=0.6)
    m.m("head", PL2, (4.2, 32.6, 10.2), (2.2, 3.6, 5.4))
    bevel(m, "jaw", PL2, (0, 29.6, 10.4), (8.6, 2.8, 6.8), 0.7)
    paint(m, "jaw", "front", (0, 31.2, 13.8), ["c.c..c.c"], {"c": "calcite"}, px=0.9, depth=0.5)
    # right arm: shoulder, a short upper arm, then the giant fist that almost drags on the ground
    m.c("armR", CORE, (-15.6, 26.4, 0), (4, 4, 4), light=True)
    bevel(m, "armR", PL2, (-15.6, 28.2, 0.2), (6.4, 9, 6.4), 0.8)
    m.c("armR", DK, (-15.6, 24, 0.4), (6.4, 1.6, 6.4))
    bevel(m, "armR", PL, (-16, 15.6, 0.8), (11, 13, 11), 1.6)
    crack(m, "armR", "right", (-21.6, 15.6, 0.8), [(-4.6, 4), (-1, 4), (-1, 0.4), (2.2, 0.4), (2.2, -4.4)], HOT, 0.8)
    crack(m, "armR", "front", (-16, 15.6, 6.4), [(-3.6, -3), (-0.6, -3), (-0.6, 1.6), (2.6, 1.6), (2.6, 4.6)], HOT, 0.8)
    for i, z in enumerate((-3.2, 0, 3.2, 6.2)):
        bevel(m, "armR", PL2 if i % 2 else PL, (-16, 7.4, -0.8 + z), (10, 3.4, 2.8), 0.6)
    m.c("armR", HI, (-21.6, 17, 0.8), (0.6, 4, 5))
    # left arm: lean, stone claws
    m.c("armL", CORE, (15.2, 26.4, 0), (3.6, 4, 3.6), light=True)
    bevel(m, "armL", PL2, (15.2, 28.6, 0.2), (5.4, 9, 5.4), 0.7)
    bevel(m, "armL", PL, (15.2, 20.4, 0.6), (6.4, 8, 6.4), 0.9)
    crack(m, "armL", "left", (18.5, 20.4, 0.6), [(1.6, 3), (1.6, 0), (-1.2, 0), (-1.2, -3)], HOT, 0.7)
    m.c("armL", DK, (15.2, 15.8, 0.6), (6.8, 1.8, 6.8))
    for x in (-2, 0, 2):
        limb(m, "armL", HI, (15.2 + x, 15, 2.2), [(3, 1.4, (160, 0, 0)), (2.4, 1.1, (120, 0, 0))])
    for s_ in (1, -1):
        m.c("body", HI, (5.9 * s_, 24.6, 7.25), (6, 0.6, 0.4))
        m.c("body", HOT, (8.6 * s_, 31.4, 7.0), (0.6, 2.4, 0.3), light=True)
    m.attacks = {"slam": "slam", "quake": "stomp", "meteor": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


@model
def warlord_gruk():
    """A pot-bellied piglin warlord: gold half helm with iron horns, a buckled war belt over a ragged
    green kilt, gold pauldrons, studded bracers and a stone maul bound with iron."""
    m = Model("warlord_gruk", "biped", 1.6)
    biped(m, hip=13, legx=4.8, neck=35, shoulder=33, armx=12.5)
    m.bone("jaw", "head", (0, 37, 5))
    m.bone("maul", "armR", (-12.5, 14, 1.5))
    m.hold = {"maul": 30}
    m.bend = -30
    SK, SK2, GD, GD2, IR, DK = "white_terracotta", "pink_terracotta", "gold_block", "raw_gold_block", "iron_block", "polished_blackstone"
    KILT, KILT2, BELT = "green_terracotta", "lime_terracotta", "gray_concrete"
    # legs: pink thighs, dark boots with gold toe caps
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.8 * s
        bevel(m, b, SK, (x, 9, 0), (6, 8, 6), 0.8)
        bevel(m, b, DK, (x, 3.4, 0.6), (7, 5.4, 7.6), 0.8)
        m.c(b, GD, (x, 1.4, 4.2), (6, 2.8, 1.2))
        m.c(b, DK, (x, 5.8, 0.6), (7.4, 1, 8))
    # kilt with a torn hem, belt with a gold buckle
    bevel(m, "hips", KILT, (0, 12.4, 0.2), (17, 6, 12.4), 0.8)
    hem(m, "hips", KILT, -8, 8, 9.6, 6.1, 0.8, 8, long=3.2, short=1.2)
    hem(m, "hips", KILT2, -8, 8, 9.6, -6.1, 0.8, 8, long=2.6, short=1.0, seed=2)
    hem(m, "hips", KILT, -5.5, 5.5, 9.6, 8.4, 0.8, 5, long=2.4, seed=1, face_z=False)
    hem(m, "hips", KILT, -5.5, 5.5, 9.6, -8.4, 0.8, 5, long=2.6, seed=3, face_z=False)
    m.c("hips", BELT, (0, 16.6, 0.4), (18, 3.6, 13.2))
    paint(m, "hips", "front", (0, 16.6, 7), [
        "GGGG.GGGG",
        "G..G.G..G",
        "G.GGGGG.G",
        "GGGG.GGGG",
    ], {"G": GD}, px=0.8, depth=0.6)
    # belly and chest
    bevel(m, "body", SK, (0, 23.4, 1.2), (18, 11, 13), 1.6)
    bevel(m, "body", SK, (0, 31, 0.4), (19, 6, 12), 1.2)
    paint(m, "body", "front", (0, 25, 7.7), ["b...b", ".....", "..b.."], {"b": SK2}, px=1.2, depth=0.3)
    # gold strap across the chest with rivets, a tusk-tooth necklace
    m.c("body", BELT, (0, 28, 1.2), (2.2, 22, 14.4), (0, 0, 42))
    for t in (-6, -2, 2, 6):
        m.c("body", GD, (t * 0.74, 28 + t * 0.67, 7.6), (1, 1, 0.5))
    for i, x in enumerate((-4, -2, 0, 2, 4)):
        m.c("body", "calcite" if i % 2 == 0 else "bone_block", (x, 32.6 - abs(x) * 0.3, 6.8), (1.2, 2.2 - abs(x) * 0.15, 1))
    # arms: big gold pauldrons in two layers, pink arms, studded dark bracers
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12.5 * s
        bevel(m, a, GD, (x + 0.8 * s, 34.4, 0), (8.4, 4, 9.4), 0.8, (0, 0, -16 * s), (x, 34, 0))
        bevel(m, a, GD2, (x + 2.4 * s, 31.6, 0), (6, 2.6, 8.4), 0.6, (0, 0, -24 * s), (x, 34, 0))
        m.c(a, DK, (x + 1 * s, 36.4, 0), (5, 0.8, 7.4), (0, 0, -16 * s), (x, 34, 0))
        bevel(m, a, SK, (x, 26, 0), (6, 9, 6), 0.8)
        bevel(m, a, SK, (x, 18.4, 0.6), (6.4, 6.6, 6.4), 0.8)
        band(m, a, DK, (x, 18.6, 0.6), (7, 3.6, 7), studs=3, stud_block=IR)
        bevel(m, a, SK, (x, 14, 1.2), (6, 3.4, 6), 0.7)
    # head: wide brute head, big snout with nostrils, tusks, floppy ears, small mean eyes
    bevel(m, "head", SK, (0, 40.4, 1.6), (11, 9, 10), 1.2)
    bevel(m, "head", SK2, (0, 39, 7.6), (6, 4, 3), 0.6)
    paint(m, "head", "front", (0, 39, 9.1), ["n..n"], {"n": "brown_terracotta"}, px=1.0, depth=0.3)
    paint(m, "head", "front", (0, 42.4, 6.6), [
        "bb.....bb",
        ".bbe.ebb.",
    ], {"b": "brown_terracotta", "e": ("red_concrete", 0.3, True)}, px=1.0, depth=0.4)
    bevel(m, "jaw", SK, (0, 36.4, 4), (10, 2.6, 7.6), 0.6)
    mhorn(m, "jaw", "calcite", (3.6, 37, 7.2), 2, (-8, 0, -14), (-14, 0, -6), 1.5)
    for s in (1, -1):
        m.c("head", SK, (7.2 * s, 41.6, 1.4), (2, 5, 4.4), (0, 0, -38 * s), (5.6, 43.4, 1.4) if s > 0 else (-5.6, 43.4, 1.4))
        m.c("head", SK2, (7.9 * s, 40.4, 1.4), (0.6, 2.6, 2.6), (0, 0, -38 * s), (5.6, 43.4, 1.4) if s > 0 else (-5.6, 43.4, 1.4))
    # gold half helm with a nose guard and two curling iron horns
    bevel(m, "head", GD, (0, 45.6, 1.2), (11.6, 2.8, 10.6), 0.7)
    m.c("head", GD2, (0, 47.4, 1.2), (8, 1.2, 8))
    m.c("head", GD, (0, 43.6, 6.9), (1.6, 3, 0.8))
    for x in (-4, 0, 4):
        m.c("head", IR, (x, 45.6, 6.6), (0.9, 0.9, 0.4))
    mhorn(m, "head", DK, (5.4, 46.4, 1.2), 4, (0, 0, -64), (0, 0, 26), 2.2, 0.8)
    # stone maul bound with iron
    m.c("maul", "stripped_dark_oak_log", (-12.5, 22, 1.5), (1.6, 26, 1.6))
    m.c("maul", "brown_wool", (-12.5, 13, 1.5), (2, 4, 2))
    bevel(m, "maul", "polished_andesite", (-12.5, 35, 1.5), (7, 6, 10), 1.2)
    band(m, "maul", IR, (-12.5, 35, 1.5), (7.4, 1.6, 10.4))
    for z in (-3.4, 6.4):
        m.c("maul", IR, (-12.5, 35, 1.5 + z), (7.4, 6.4, 0.8))
    spikes(m, "maul", IR, [(-12.5, 35, 6.6), (-12.5, 35, -3.6)], (90, 0, 0), 2.4, 1.0)
    m.attacks = {"slam": "slam", "charge": "sweep", "minions": "roar", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def grand_augur():
    """The illager king-sorcerer: a huge grey head with a heavy
    dark unibrow and a long nose, a towering gold crown set with a red and a blue gem, a short blue
    robe with gold edging, a stand-up gold collar and a ruby amulet, big square gold cuffs, and a grey
    staff banded in red with a gold crystal floating over it."""
    m = Model("grand_augur", "biped", 1.9)
    biped(m, hip=8, legx=2.4, neck=19.5, shoulder=18, armx=6.6)
    m.bone("crown", "head", (0, 32.5, 0.5))
    m.bone("staff", "armR", (-6.6, 9.4, 2))
    m.bone("gem", "staff", (-6.6, 33, 2))
    m.hold = {"staff": (0, 0, 42)}
    m.bend = -30
    m.rest("armR", (0, 0, -42))
    SK, SK2, BR, RB, RB2, GD, GD2, IN = "light_gray_concrete", "polished_andesite", "gray_concrete", "blue_concrete", "blue_terracotta", "gold_block", "orange_concrete", "dark_prismarine"
    # short legs in grey hose, gold anklets, dark shoes
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.4 * s
        m.c(b, SK2, (x, 5, 0), (2.6, 6, 2.6))
        m.c(b, GD, (x, 2.6, 0), (3, 1, 3))
        m.c(b, BR, (x, 1, 0.6), (3, 2, 4))
    # robe: an open blue coat over a dark tunic, gold edging down both fronts and along the hem
    stack(m, "hips", RB, 0, 3.4, 0, [(9.6, 2, 7), (9, 3, 6.6)])
    m.c("hips", IN, (0, 6, 3.35), (3, 5, 0.3))
    for s in (1, -1):
        m.c("hips", GD, (1.9 * s, 5.8, 3.5), (0.7, 5.2, 0.3))
    m.c("hips", GD, (0, 3.7, 0), (10, 0.7, 7.4))
    bevel(m, "body", RB, (0, 13.6, 0), (8.6, 8.6, 6), 0.6)
    m.c("body", IN, (0, 13.4, 3.05), (3, 8, 0.3))
    for s in (1, -1):
        m.c("body", GD, (1.9 * s, 13.2, 3.15), (0.7, 8.6, 0.3))
        m.c("body", RB2, (4.35 * s, 13.6, 0), (0.2, 7, 4.6))
    band(m, "body", "brown_terracotta", (0, 10.2, 0), (8.8, 1, 6.2))
    # a gold collar standing up behind the head in a V, and the ruby amulet hanging in front
    for s in (1, -1):
        m.c("body", GD, (2.4 * s, 19.2, 2.4), (3.4, 3, 0.6), (0, 20 * s, -24 * s))
        m.c("body", GD, (3.9 * s, 19.6, 0), (0.6, 3.4, 5))
    m.c("body", GD, (0, 19.4, -2.8), (8, 3.4, 0.6))
    m.c("body", GD, (0, 15.6, 3.4), (2.6, 2.6, 0.6))
    m.c("body", "redstone_block", (0, 15.4, 3.75), (1.6, 1.6, 0.3), light=True)
    m.c("body", "white_concrete", (-0.4, 15.9, 3.95), (0.5, 0.5, 0.1))
    m.c("body", GD, (0, 17.4, 3.3), (0.4, 1.4, 0.3))
    # the back: a gold-edged blue panel hanging from the collar
    m.c("body", RB2, (0, 12.4, -3.25), (6.4, 9, 0.5))
    m.c("body", GD, (0, 8.1, -3.35), (6.8, 0.6, 0.5))
    paint(m, "body", "back", (0, 13.6, -3.5), [".G.", "GRG", ".G."], {"G": GD, "R": ("redstone_block", 0.2, True)}, px=0.9, depth=0.2)
    # arms: blue sleeves, big square gold cuffs, grey hands
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6.6 * s
        bevel(m, a, RB, (x, 15.6, 0), (3.6, 5, 3.8), 0.5)
        m.c(a, RB, (x, 11.4, 0.4), (3.2, 4.6, 3.4))
        for (dx, dz, w, d) in ((0, 2.2, 4.8, 0.6), (0, -1.4, 4.8, 0.6), (2.1, 0.4, 0.6, 3.6), (-2.1, 0.4, 0.6, 3.6)):
            m.c(a, GD, (x + dx, 9.6, dz), (w, 2.4, d))
        m.c(a, SK, (x, 7.8, 0.4), (2.6, 2.4, 2.6))
    # the head: big and grey, a dark unibrow that dips in the middle, small eyes, a long nose
    bevel(m, "head", SK, (0, 26.4, 0.5), (14, 13, 13), 1.2)
    m.c("head", SK2, (0, 20.6, 0.5), (12, 1.4, 11))
    for s in (1, -1):
        m.c("head", BR, (3.4 * s, 28.6, 7.1), (5.2, 1.8, 0.4), (0, 0, -16 * s))
        m.c("head", BR, (5.8 * s, 29.6, 7.1), (2, 1.2, 0.4))
        m.c("head", "white_concrete", (3.4 * s, 26.6, 7.05), (2.4, 1.6, 0.2))
        m.c("head", "black_concrete", (2.8 * s, 26.6, 7.2), (1, 1.6, 0.2))
        m.c("head", SK2, (5.4 * s, 23.8, 7.05), (2.4, 1.2, 0.2))
    m.c("head", BR, (0, 27.6, 7.1), (2, 1.4, 0.4))
    m.c("head", "light_gray_terracotta", (0, 24, 8.6), (3, 7, 3))
    m.c("head", "light_gray_terracotta", (0, 20.8, 8.9), (2.4, 1, 2.4))
    m.c("head", BR, (0, 22, 7.05), (4.4, 0.6, 0.2))
    for (x, y) in ((-5, 31), (4.6, 30.4)):
        m.c("head", SK2, (x, y, 7.05), (1.6, 0.8, 0.2))
    # the crown: a tall gold tube leaning slightly back, a jagged open top, a red and a blue gem
    m.rest("crown", (-6, 0, 4))
    m.c("crown", GD, (0, 39, 0.5), (6, 13, 6))
    m.c("crown", GD2, (-2.85, 39, 0.5), (0.4, 13, 6))
    m.c("crown", GD2, (-1.6, 39, -2.6), (0.8, 13, 0.4))
    m.c("crown", GD2, (1.4, 39, -2.6), (0.6, 13, 0.4))
    m.c("crown", GD, (0, 33, 0.5), (7, 1, 7))
    for k, (x, z, h) in enumerate(((-2.4, 3.3, 2.4), (2.4, 3.3, 1.6), (2.8, -2.2, 2.6), (-2.6, -2.4, 1.8), (0, 3.3, 1.2))):
        m.c("crown", GD, (x, 45.5 + h / 2, z), (1.4, h, 0.6) if abs(z) > 3 else (0.6, h, 1.4))
    m.c("crown", "orange_terracotta", (0, 45.4, 0.5), (5, 0.4, 5))
    paint(m, "crown", "front", (0, 39, 3.5), ["RR", "RO", "..", "..", "BB", "BL"], {"R": ("red_concrete", 0.4, True), "O": ("orange_concrete", 0.4, True), "B": ("blue_concrete", 0.4, True), "L": ("light_blue_concrete", 0.4, True)}, px=1.3, depth=0.4)
    for k in range(4):
        m.c("crown", GD2, (1.8, 35 + k * 2.6, 3.6), (0.6, 1.2, 0.2))
    # the staff: a grey shaft with red bands, a T cap, and the gold crystal floating over it
    m.c("staff", SK2, (-6.6, 18, 2), (1.2, 30, 1.2))
    for y in (8, 10.2, 19, 26):
        m.c("staff", "red_concrete", (-6.6, y, 2), (1.5, 1.4 if y != 19 else 2.6, 1.5))
    m.c("staff", SK2, (-6.6, 33.4, 2), (4, 1.2, 1.6))
    m.c("staff", BR, (-6.6, 3.2, 2), (1.6, 1.4, 1.6))
    m.c("gem", GD, (-6.6, 38.6, 2), (5, 5, 5), (45, 0, 45), light=True)
    m.c("gem", "yellow_stained_glass", (-6.6, 38.6, 2), (6.4, 6.4, 6.4), (45, 0, 45), light=True)
    m.c("gem", "yellow_concrete", (-6.6, 38.6, 2), (2.6, 2.6, 6.8), (0, 0, 45), light=True)
    m.attacks = {"vex": "cast", "beam": "double", "blink": "cast", "fangs": "slam"}
    m.melee = "swipe"
    return m


@model
def crimson_ronin():
    """A red oni warlord: a snarling face framed by a white mane and two ivory horns, a gold rope of
    beads, a white loincloth with a black tooth pattern, gold-trimmed armour skirt and a huge studded
    iron club."""
    m = Model("crimson_ronin", "biped", 1.65)
    biped(m, hip=13, legx=4.6, neck=33, shoulder=31, armx=11.5)
    m.bone("jaw", "head", (0, 34.6, 4))
    m.bone("club", "armR", (-11.5, 13, 2))
    m.hold = {"club": 12}
    m.bend = -24
    SK, SK2, AR, AR2, GD, WH, DK, IR = "red_terracotta", "red_concrete", "red_nether_bricks", "nether_bricks", "gold_block", "white_concrete", "black_concrete", "polished_andesite"
    # legs: red shins, dark shin guards with gold edges, clawed feet
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.6 * s
        bevel(m, b, SK, (x, 8.4, 0), (5.4, 9, 5.4), 0.7)
        plate(m, b, AR, (x, 6.4, 2.9), (5, 6, 1))
        m.c(b, GD, (x, 9.6, 3.5), (5.2, 0.7, 0.4))
        bevel(m, b, SK2, (x, 1.6, 1), (6, 3.2, 7.4), 0.6)
        for t in (-1.8, 0, 1.8):
            m.c(b, "calcite", (x + t, 0.6, 5.2), (1, 1.2, 1.4))
    # armoured skirt: overlapping red plates edged in gold, the white tooth loincloth in front
    for i, (x, w) in enumerate(((-5.6, 6), (0, 6), (5.6, 6))):
        m.c("hips", AR if i % 2 == 0 else AR2, (x, 10.4, -0.2), (w, 6, 11.6))
        m.c("hips", GD, (x, 7.6, -0.2), (w + 0.2, 0.6, 11.8))
    m.c("hips", WH, (0, 10, 6.2), (6, 8, 0.6))
    paint(m, "hips", "front", (0, 9.6, 6.5), [
        "KKKKKK",
        "K.KK.K",
        "......",
        ".K..K.",
        "K.KK.K",
    ], {"K": DK}, px=1.0, depth=0.2)
    hem(m, "hips", WH, -3, 3, 6, 6.2, 0.6, 3, long=2.4, short=1.2)
    band(m, "hips", "brown_terracotta", (0, 14, 0), (16.4, 2, 12), studs=4, stud_block=GD)
    # torso: muscled red chest, a sash, gold bead rope
    bevel(m, "body", SK, (0, 21, 0.4), (14, 9, 10), 1.2)
    bevel(m, "body", SK, (0, 28.4, 0.6), (17, 7, 11), 1.4)
    paint(m, "body", "front", (0, 26, 6.1), ["SS..SS", ".S..S.", "......", "..SS..", "..SS.."], {"S": SK2}, px=1.4, depth=0.3)
    for i in range(9):
        t = (i - 4) / 4
        m.c("body", GD if i % 2 == 0 else "orange_terracotta", (t * 6.2, 31 - abs(t) * 0 - (1 - t * t) * 4.4, 6.4 - abs(t) * 1.2), (1.6, 1.6, 1.6), (45, 45, 0))
    m.c("body", "orange_terracotta", (0, 22, 0.4), (14.6, 1.6, 10.6))
    # shoulders: red lacquered plates with gold rims, white fur under them
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11.5 * s
        tufts(m, a, "white_wool", [(x, 33, -2), (x + 1 * s, 33.4, 1), (x, 33, 3)], 2.6)
        bevel(m, a, AR, (x + 1 * s, 30.8, 0.2), (7.4, 3.4, 8.4), 0.6, (0, 0, -18 * s), (x, 31, 0))
        m.c(a, GD, (x + 1.5 * s, 29.2, 0.2), (7.6, 0.6, 8.6), (0, 0, -18 * s), (x, 31, 0))
        bevel(m, a, SK, (x, 24.4, 0), (5.4, 9, 5.4), 0.8)
        bevel(m, a, SK, (x, 16.6, 0.8), (5.8, 6.4, 5.8), 0.8)
        band(m, a, "brown_terracotta", (x, 17.4, 0.8), (6.2, 2.2, 6.2))
        m.c(a, GD, (x, 17.4, 3.95), (1.6, 1.6, 0.3))
        m.c(a, SK2, (x, 12.8, 1.6), (5, 2.6, 5))
    # head: snarling face, gold eyes under a heavy brow, a fanged jaw, white mane and two horns
    bevel(m, "head", SK, (0, 38, 1), (9, 8, 8), 0.9)
    paint(m, "head", "front", (0, 39.2, 5.1), [
        "KK.....KK",
        ".KKK.KKK.",
        "..YW.WY..",
        "....S....",
    ], {"K": DK, "Y": ("yellow_concrete", 0.4, True), "W": WH, "S": SK2}, px=1.0, depth=0.5)
    bevel(m, "jaw", SK, (0, 34.6, 2.6), (8, 2.6, 6.4), 0.6)
    m.c("jaw", DK, (0, 35.4, 5.6), (5, 1, 0.4))
    paint(m, "jaw", "front", (0, 35.6, 5.95), ["W.W.W.W", "WW...WW"], {"W": WH}, px=0.8, depth=0.5)
    for i, (x, y, z, sz) in enumerate(((0, 43, -1, 5), (-4, 42, -2, 4), (4, 42, -2, 4), (-5, 38.5, -2.5, 4), (5, 38.5, -2.5, 4),
                                       (-3, 35, -3.6, 4), (3, 35, -3.6, 4), (0, 37, -4.2, 5), (-5.4, 34, -1, 3), (5.4, 34, -1, 3))):
        m.c("head", "white_wool", (x, y, z), (sz, sz * 1.1, sz), (14 if i % 2 else -10, 0, 12 if x > 0 else -12))
    mhorn(m, "head", "calcite", (3, 42, 1.6), 4, (-10, 0, -22), (-6, 0, 10), 2.0, 0.78)
    m.c("head", GD, (0, 42.6, 5), (3, 1.2, 0.6))
    # the club: an iron kanabo with rows of studs and a wrapped grip
    m.c("club", "brown_wool", (-11.5, 13, 2), (2, 6, 2))
    m.c("club", DK, (-11.5, 9.6, 2), (2.6, 1, 2.6))
    m.c("club", "polished_deepslate", (-11.5, 22, 2), (2.4, 12, 2.4))
    bevel(m, "club", IR, (-11.5, 34, 2), (5, 14, 5), 1.0)
    m.c("club", "polished_deepslate", (-11.5, 41.6, 2), (4.4, 1.2, 4.4))
    for y in (29, 32.5, 36, 39.5):
        for dx, dz in ((2.6, 0), (-2.6, 0), (0, 2.6), (0, -2.6)):
            m.c("club", "iron_block", (-11.5 + dx, y + (0.9 if dx else 0), 2 + dz), (1.1, 1.1, 1.1), (45, 0, 45))
    m.attacks = {"slam": "slam", "charge": "sweep", "quake": "stomp", "roar": "roar"}
    m.melee = "swipe"
    return m


@model
def thunderback():
    """A giant storm ape that walks on its knuckles: shaggy red-brown fur, a bare tan chest and face,
    gold arm rings stamped with a lightning glyph and a chieftain's feather crown."""
    m = Model("thunderback", "biped", 1.7)
    biped(m, hip=12, legx=6, neck=31, shoulder=31, armx=14)
    m.bone("jaw", "head", (0, 30, 9))
    m.bend = -8
    m.rest("body", (-24, 0, 0))
    m.rest("head", (22, 0, 0))
    for a in ("armL", "armR"):
        m.rest(a, (16, 0, 0))
    FU, FU2, FU3, SK, SK2, GD, DK = "brown_wool", "brown_terracotta", "red_terracotta", "white_terracotta", "terracotta", "gold_block", "black_terracotta"
    # short legs, big feet
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 6 * s
        bevel(m, b, FU, (x, 8, -0.6), (7, 9, 7), 1.0)
        tufts(m, b, FU2, [(x + 3 * s, 9, -1), (x + 3 * s, 6, 1), (x, 4.6, -3.6)], 2.2)
        bevel(m, b, SK2, (x, 1.6, 1.4), (7.4, 3.2, 8.6), 0.7)
        for t in (-2.2, 0, 2.2):
            m.c(b, SK, (x + t, 1, 5.8), (1.8, 1.8, 1.4))
    bevel(m, "hips", FU, (0, 13.4, -1), (16, 5, 11), 1.0)
    # torso: a huge furred back and shoulders, a bare chest
    bevel(m, "body", FU, (0, 23, -1), (20, 14, 13), 1.8)
    bevel(m, "body", FU, (0, 31.4, -1.4), (24, 7, 14), 2.0)
    bevel(m, "body", SK, (0, 24.4, 4.8), (13, 11, 2.4), 0.8)
    paint(m, "body", "front", (0, 25, 6.1), ["SSS.SSS", "SSS.SSS", ".......", ".SS.SS.", ".SS.SS."], {"S": SK2}, px=1.4, depth=0.2)
    for pts, blk in (([(-9, 34, -6), (-5, 35.4, -7.2), (0, 35.8, -7.6), (5, 35.4, -7.2), (9, 34, -6)], FU2),
                     ([(-7, 28, -7.4), (-2, 29, -7.8), (3, 28.6, -7.8), (7.6, 27.6, -7.4)], FU3),
                     ([(-11.4, 31, 2), (11.4, 31, 2), (-11, 27, -2), (11, 27, -2)], FU2)):
        tufts(m, "body", blk, pts, 3.0)
    # arms: thick, long, knuckles on the ground, gold rings with the lightning glyph
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 14.5 * s
        bevel(m, a, FU, (x, 26, 0), (8, 11, 8), 1.2)
        tufts(m, a, FU2, [(x + 3.6 * s, 29, 0), (x + 3.6 * s, 25, -2), (x, 31, -3.8)], 2.6)
        bevel(m, a, FU, (x, 15.6, 0.6), (7.4, 10, 7.4), 1.1)
        band(m, a, GD, (x, 18.6, 0.6), (8, 2.6, 8))
        paint(m, a, "left" if s > 0 else "right", (x + 4 * s, 18.6, 0.6), ["Y.YY", ".YY.", "YY.Y"], {"Y": ("yellow_concrete", 0.3, True)}, px=0.8, depth=0.2)
        bevel(m, a, SK2, (x, 8.6, 1.6), (8, 4.4, 8.4), 0.9)
        for t in (-2.6, 0, 2.6):
            m.c(a, SK, (x + t * 0.9, 7, 5.6), (2.2, 2.4, 1.6))
    # head: heavy brow, deep-set red eyes, flat nose, a jaw that roars, feather crown
    bevel(m, "head", FU, (0, 33.6, 6.6), (12, 9, 9), 1.2)
    bevel(m, "head", SK, (0, 32.8, 11.2), (9, 6, 1.6), 0.6)
    paint(m, "head", "front", (0, 34, 12.1), [
        "KKKKKKK",
        ".R...R.",
        "...N...",
        "..NNN..",
    ], {"K": DK, "R": ("red_concrete", 0.4, True), "N": SK2}, px=1.0, depth=0.5)
    bevel(m, "jaw", SK2, (0, 29.4, 10), (9, 3, 4.6), 0.6)
    paint(m, "jaw", "front", (0, 30.4, 12.4), ["W.....W", ".KKKKK."], {"W": "calcite", "K": DK}, px=1.0, depth=0.3)
    tufts(m, "head", FU2, [(-5.6, 38, 6), (5.6, 38, 6), (0, 38.8, 5), (-3, 39, 3), (3, 39, 3)], 2.8)
    for i, (x, rz, col) in enumerate(((-4, 26, "red_concrete"), (-1.4, 8, "yellow_concrete"), (1.4, -8, "lime_concrete"), (4, -26, "light_blue_concrete"))):
        m.c("head", col, (x, 42.6, 4), (1.4, 6, 0.8), (-10, 0, rz), (x, 39.6, 4))
        m.c("head", "white_concrete", (x, 45, 4), (0.8, 1.6, 0.9), (-10, 0, rz), (x, 39.6, 4))
    band(m, "head", GD, (0, 38.8, 6.6), (12.4, 1.4, 9.4))
    for x in (-4.4, -1.5, 1.5, 4.4):
        m.c("head", "lapis_block" if abs(x) < 2 else "red_concrete", (x, 38.8, 11.4), (1.2, 1.2, 0.4))
    # a silver saddle of fur down the back, storm-blue war paint stripes on the shoulders
    for i, (y, w) in enumerate(((34.6, 10), (31.4, 12), (28, 11), (24.6, 9), (21.2, 7))):
        m.c("body", "light_gray_wool", (0, y, -8.2 + i * 0.25), (w, 2.8, 1.4))
    for s in (1, -1):
        for k in range(3):
            m.c("body", "light_blue_concrete", (9.4 * s, 33.6 - k * 1.6, 3.6 - k * 0.6), (3.4, 0.7, 0.6), (0, 0, 20 * s))
    # more shag: long hair hanging off the forearms and back of the legs
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 14.5 * s
        for k, (dy, dz) in enumerate(((22, -4.4), (19, -4.4), (14, -4.2), (11.6, -3.8))):
            m.c(a, FU2 if k % 2 else FU3, (x + (1 if k % 2 else -1) * 1.6, dy, dz), (3, 3.4, 2), (20, 0, 0))
    for s, b in ((1, "legL"), (-1, "legR")):
        for k, dy in enumerate((11, 7.6)):
            m.c(b, FU2, (6 * s + (k - 0.5) * 2, dy, -4.6), (3, 3.2, 2), (18, 0, 0))
    m.attacks = {"slam": "slam", "quake": "stomp", "lightning": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


@model
def gorehorn():
    """A minotaur pit champion: dark brown bull head with frosted-white horns and a gold nose ring,
    snow-white fur over the shoulders, a leather harness, a blue loincloth and a double-headed axe."""
    m = Model("gorehorn", "biped", 1.75)
    biped(m, hip=14, legx=5, neck=34, shoulder=32, armx=12.5)
    m.bone("jaw", "head", (0, 36, 6))
    m.bone("axe", "armR", (-12.5, 13.4, 2))
    m.hold = {"axe": 18}
    m.bend = -34
    HD, HD2, FU, FU2, SK, LE, BL, IR = "brown_terracotta", "black_terracotta", "white_wool", "light_gray_wool", "terracotta", "brown_concrete", "blue_terracotta", "iron_block"
    # legs: furred thighs, hooves
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5 * s
        bevel(m, b, HD, (x, 9.6, 0), (6.4, 9, 6.4), 0.9)
        tufts(m, b, FU2, [(x + 2.6 * s, 11, 1), (x, 6.6, -3.2), (x + 2.4 * s, 6.6, 2.6)], 2.0)
        bevel(m, b, HD2, (x, 2.4, 0.8), (6, 4.8, 7), 0.7)
        m.c(b, "black_concrete", (x, 1, 4.1), (1, 2, 0.6))
    # loincloth and a studded belt
    bevel(m, "hips", LE, (0, 15.4, 0), (15, 4, 10), 0.8)
    band(m, "hips", "brown_terracotta", (0, 17.2, 0), (15.4, 1.6, 10.4), studs=5, stud_block=IR)
    m.c("hips", BL, (0, 10.6, 5.4), (6, 8, 0.6))
    paint(m, "hips", "front", (0, 11, 5.75), ["W.W.W", ".....", "..W..", "....."], {"W": "light_blue_terracotta"}, px=1.0, depth=0.2)
    hem(m, "hips", BL, -3, 3, 6.6, 5.4, 0.6, 3, long=2.2)
    m.c("hips", BL, (0, 11.4, -5.3), (7, 7, 0.6))
    # torso: broad and muscled, a cross harness with a round iron boss
    bevel(m, "body", SK, (0, 22.6, 0.4), (15, 9, 10), 1.4)
    bevel(m, "body", HD, (0, 29.6, 0), (19, 7, 11.6), 1.4)
    paint(m, "body", "front", (0, 24, 5.95), ["HH.HH", "HH.HH", ".....", "H.H.H"], {"H": HD}, px=1.6, depth=0.25)
    for r in (40, -40):
        m.c("body", LE, (0, 26, 0.4), (2, 20, 12.2), (0, 0, r))
    m.c("body", IR, (0, 26.6, 6.5), (3.6, 3.6, 0.8), (0, 0, 45))
    m.c("body", "polished_andesite", (0, 26.6, 6.9), (1.6, 1.6, 0.4))
    # shoulders: a thick white mane over the back and shoulders
    pts = [(x, 34 + (i % 2) * 0.6, z) for i, (x, z) in enumerate(((-9, 2), (-6, -3), (-3, -4), (0, -4.5), (3, -4), (6, -3), (9, 2), (-7, 4), (7, 4), (-4, 4.6), (4, 4.6)))]
    tufts(m, "body", FU, pts, 3.4, alt=FU2)
    tufts(m, "body", FU, [(-5, 31, -5.8), (0, 30.4, -6.2), (5, 31, -5.8), (-2.6, 28, -6.2), (2.6, 28, -6.2)], 2.6, alt=FU2)
    # arms: thick, a fur cuff at the shoulder, a leather bracer
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12.5 * s
        tufts(m, a, FU, [(x + 1.4 * s, 34, -1.6), (x + 1.8 * s, 34, 1.8), (x + 3 * s, 32, 0)], 3.2)
        bevel(m, a, SK, (x, 26, 0), (6.4, 10, 6.4), 0.9)
        bevel(m, a, SK, (x, 17.6, 0.8), (6.2, 7, 6.2), 0.9)
        band(m, a, LE, (x, 17.4, 0.8), (6.8, 3.4, 6.8), studs=2, stud_block=IR)
        bevel(m, a, HD, (x, 13.2, 1.6), (5.4, 2.8, 5.4), 0.6)
    # head: a long bull muzzle, flared nostrils, a gold ring, red eyes and huge frost-tipped horns
    bevel(m, "head", HD, (0, 40, 2.4), (10, 9, 9), 1.2)
    bevel(m, "head", HD2, (0, 37.6, 8.2), (7, 5, 4.6), 0.8)
    paint(m, "head", "front", (0, 38.4, 10.55), ["N...N", "....."], {"N": "black_concrete"}, px=1.0, depth=0.3)
    m.c("head", "gold_block", (0, 36.2, 10.6), (3, 0.6, 0.6))
    m.m("head", "gold_block", (1.3, 37, 10.6), (0.6, 1.6, 0.6))
    paint(m, "head", "front", (0, 42.4, 7.0), [
        "KKK...KKK",
        ".KRK.KRK.",
    ], {"K": "black_concrete", "R": ("red_concrete", 0.4, True)}, px=1.0, depth=0.4)
    bevel(m, "jaw", HD, (0, 35.4, 6.6), (6.4, 1.8, 5.6), 0.5)
    for s in (1, -1):
        m.c("head", HD, (6.2 * s, 41, 1.6), (2.6, 1.6, 3), (0, 0, -24 * s))
        horn(m, "head", "white_terracotta", (5 * s, 43.6, 2), 3, (0, 0, -84 * s), (0, 0, 24 * s), 2.6, 0.82)
        horn(m, "head", "calcite", (11.2 * s, 46.4, 2), 2, (0, 0, 10 * s), (-10, 0, 16 * s), 1.7, 0.75)
    tufts(m, "head", FU, [(0, 45, 1), (-2.4, 44.6, -1.4), (2.4, 44.6, -1.4)], 2.4)
    # double axe: two curved iron blades on a long haft
    m.c("axe", "stripped_spruce_log", (-12.5, 24, 2), (1.6, 30, 1.6))
    m.c("axe", LE, (-12.5, 13.4, 2), (2, 5, 2))
    for y in (19, 30):
        m.c("axe", IR, (-12.5, y, 2), (2, 0.8, 2))
    for dz in (1, -1):
        bevel(m, "axe", IR, (-12.5, 34.6, 2 + dz * 4.4), (1.2, 8, 6), 0.8)
        m.c("axe", IR, (-12.5, 34.6, 2 + dz * 7.6), (1, 11, 1.6))
        m.c("axe", "light_gray_concrete", (-12.5, 34.6, 2 + dz * 8.5), (0.8, 10, 0.4))
    m.c("axe", IR, (-12.5, 40, 2), (1.8, 3, 1.8), (45, 0, 0))
    m.attacks = {"charge": "lunge", "slam": "slam", "quake": "stomp", "roar": "roar"}
    m.melee = "swipe"
    return m


@model
def abyssal_eye():
    """An ancient deep-sea sentinel: a stone-armoured fish body with one great eye, prismarine spines
    that turn slowly around it, fins and a forked tail."""
    m = Model("abyssal_eye", "float", 2.0)
    m.bone("core", "root", (0, 20, 0))
    m.bone("head", "core", (0, 20, 4))
    m.bone("ring1", "core", (0, 20, 0))
    m.bone("ring2", "core", (0, 20, 0))
    m.mbone("armL", "core", (8, 18, -2))
    m.bone("ring3", "core", (0, 20, -10))
    SH, SH2, SP, SP2, EY, DK = "end_stone_bricks", "smooth_sandstone", "prismarine", "dark_prismarine", "white_concrete", "polished_blackstone"
    # the body: a rounded stone shell built in layers
    bevel(m, "core", SH, (0, 20, 0), (14, 13, 15), 2.4)
    bevel(m, "core", SH2, (0, 20, -6), (12, 11, 6), 2.0)
    bevel(m, "core", SH, (0, 20, -10), (8, 8, 4), 1.4)
    for y, w in ((26.8, 10), (13.2, 10)):
        m.c("core", "end_stone", (0, y, 0), (w, 0.8, 12))
    paint(m, "core", "left", (7.05, 20, 0), [
        "S.SS.S",
        ".SSSS.",
        "SS..SS",
        ".SSSS.",
        "S.SS.S",
    ], {"S": SH2}, px=1.6, depth=0.3)
    paint(m, "core", "right", (-7.05, 20, 0), [
        "S.SS.S",
        ".SSSS.",
        "SS..SS",
        ".SSSS.",
        "S.SS.S",
    ], {"S": SH2}, px=1.6, depth=0.3)
    # the eye: a sunken socket, white, a cyan iris that glows and a slit pupil, eyelid plates
    m.c("head", DK, (0, 20, 7.4), (9, 8, 1))
    m.c("head", EY, (0, 20, 7.9), (7.4, 6.4, 0.6))
    m.c("head", "cyan_concrete", (0, 20, 8.3), (4, 4, 0.4), light=True)
    m.c("head", "light_blue_concrete", (0, 20.6, 8.45), (1.6, 1.4, 0.3), light=True)
    m.c("head", "black_concrete", (0, 20, 8.55), (1, 3.2, 0.3))
    m.c("head", SH2, (0, 24.4, 8), (10, 1.8, 1.4))
    m.c("head", SH2, (0, 15.6, 8), (10, 1.8, 1.4))
    for s in (1, -1):
        m.c("head", SH, (5.2 * s, 20, 8), (1.4, 8, 1.4))
    # spines in three rings that slowly turn around the body
    for ring, y, n, off in (("ring1", 27, 8, 0), ("ring2", 13, 8, 22), ):
        import math
        for i in range(n):
            a = 2 * math.pi * i / n + math.radians(off)
            x, z = math.sin(a) * 6.4, math.cos(a) * 6.4
            dy = 1 if y > 20 else -1
            rot = (math.degrees(math.cos(a)) * 0 - 40 * math.cos(a) * dy, 0, 40 * math.sin(a) * dy)
            m.c(ring, SP, (x * 1.15, y + dy * 2.6, z * 1.15), (1.8, 6, 1.8), (-38 * math.cos(a) * -dy, 0, 38 * math.sin(a) * -dy) if False else (40 * math.cos(a) * dy, 0, -40 * math.sin(a) * dy))
            m.c(ring, SP2, (x * 1.45, y + dy * 5.6, z * 1.45), (1.1, 3, 1.1), (40 * math.cos(a) * dy, 0, -40 * math.sin(a) * dy))
    for i, (x, y) in enumerate(((7.6, 20), (-7.6, 20))):
        m.c("ring2", SP, (x * 1.15, y, -2), (6, 1.8, 1.8), (0, 0, 0))
        m.c("ring2", SP2, (x * 1.62, y, -2), (3, 1.1, 1.1))
    # fins: side fins on the arm bones, a top fin, a forked tail
    for s, a in ((1, "armL"), (-1, "armR")):
        for k in range(3):
            m.c(a, SP if k % 2 == 0 else SP2, (9.4 * s + k * 1.2 * s, 17 - k * 1.6, -2 - k * 1.2), (1, 4.4 - k * 0.6, 3), (20, 0, -30 * s))
    for k, (y, h) in enumerate(((28.8, 4), (28.4, 3), (27.6, 2.4))):
        m.c("core", SP2 if k % 2 else SP, (0, y, -2 - k * 3.2), (1, h, 3), (-10, 0, 0))
    for s in (1, -1):
        m.c("ring3", SP, (0, 20 + 3.4 * s, -14.6), (1.4, 6, 3.6), (36 * s, 0, 0))
        m.c("ring3", SP2, (0, 20 + 6.4 * s, -16.6), (1, 3, 2.4), (52 * s, 0, 0))
    m.c("ring3", SH, (0, 20, -12.6), (4, 5, 2.4))
    # armour: overlapping shell plates on top and bottom, barnacles and coral, a fanged mouth under the eye
    for k, z in enumerate((4, 0, -4, -8)):
        bevel(m, "core", SH2 if k % 2 else SH, (0, 27.2 - k * 0.3, z), (11 - k, 1.4, 4.2), 0.5)
        bevel(m, "core", SH2 if k % 2 == 0 else SH, (0, 12.8 + k * 0.3, z), (11 - k, 1.4, 4.2), 0.5)
    for (x, y, z, b) in ((5.6, 25, -5, "tube_coral_block"), (-5.8, 15, -3, "brain_coral_block"), (6.2, 15.4, 2, "horn_coral_block"),
                         (-6.4, 24.4, 1, "tube_coral_block"), (2, 27.6, -7, "bubble_coral_block"), (-3, 12.6, -6, "fire_coral_block")):
        m.c("core", b, (x, y, z), (2, 2, 2), (0, 30, 0))
        m.c("core", "calcite", (x * 1.08, y + (0.9 if y > 20 else -0.9), z), (1, 1, 1))
    m.c("head", DK, (0, 13.6, 7.2), (6, 2.2, 1))
    paint(m, "head", "front", (0, 13.6, 7.7), ["W.W.W.W", ".W...W."], {"W": "calcite"}, px=0.8, depth=0.6)
    for s in (1, -1):
        paint(m, "core", "left" if s > 0 else "right", (7.3 * s, 20, 5.2), ["D", "D", "D", ".", "D"], {"D": SP2}, px=1.2, depth=0.3)
    # glowing cyan gill slits on the flanks
    for s in (1, -1):
        for k in range(3):
            m.c("core", "cyan_concrete", (7.1 * s, 20 - 2.4 + k * 2.4, -4.6), (0.4, 0.7, 3), light=True)
    for s_ in (1, -1):
        for k in range(4):
            m.c("core", SH2, (5.8 * s_, 26.6 - k * 0.2, 4 - k * 4), (2.4, 0.6, 2.4), (0, 45, 0))
    m.attacks = {"beam": "pulse", "orbs": "spin", "pull": "raise", "charge": "dive"}
    m.melee = "swipe"
    m.no_elbows = True
    return m


@model
def overgrowth():
    """A ruined terracotta guardian that the jungle took back: banded clay limbs made of stacked rings,
    moss on the shoulders, vines hanging down its chest and arms, one amber eye in a cracked head."""
    m = Model("overgrowth", "biped", 1.7)
    biped(m, hip=14, legx=5.2, neck=34, shoulder=33, armx=12)
    m.bend = -10
    CL, CL2, DK, MO, VI, VI2 = "terracotta", "red_terracotta", "brown_terracotta", "moss_block", "green_concrete", "lime_terracotta"
    def rings(bone, x, y0, y1, z, w, d, n):
        step = (y1 - y0) / n
        for i in range(n):
            y = y0 + step * (i + 0.5)
            m.c(bone, CL if i % 2 == 0 else CL2, (x, y, z), (w, step * 0.72, d))
        m.c(bone, DK, (x, (y0 + y1) / 2, z), (w * 0.62, y1 - y0, d * 0.62))
    for s, b in ((1, "legL"), (-1, "legR")):
        rings(b, 5.2 * s, 2.6, 13.6, 0, 6.4, 6.4, 5)
        bevel(m, b, CL, (5.2 * s, 1.2, 1), (7.4, 2.4, 8.4), 0.6)
        m.c(b, VI, (5.2 * s + 2.4 * s, 8, 3.3), (1, 7, 0.6))
    bevel(m, "hips", DK, (0, 15.6, 0), (14, 3.4, 9), 0.8)
    # torso: stacked clay slabs with a ribbed belly, a moss mantle and hanging vines
    for i, (y, w) in enumerate(((19, 12), (21.6, 13), (24.2, 15), (26.8, 17), (29.4, 18))):
        bevel(m, "body", CL if i % 2 == 0 else CL2, (0, y, 0), (w, 2, 10), 0.5)
    m.c("body", DK, (0, 24, 0), (11, 11, 8.4))
    bevel(m, "body", CL, (0, 33, 0), (19, 4, 11), 1.0)
    for s in (1, -1):
        bevel(m, "body", MO, (6 * s, 35.4, -0.4), (8, 1.6, 11.4), 0.6)
    tufts(m, "body", VI2, [(-8, 35.6, 4), (-3, 36, 5), (3, 36, 5), (8, 35.6, 4), (0, 35.8, -5.6), (-6, 35.6, -5), (6, 35.6, -5)], 2.4, alt=MO)
    for x, L in ((-6, 12), (-2.6, 7), (1.6, 15), (5.4, 9)):
        m.c("body", VI, (x, 33 - L / 2, 5.9), (0.9, L, 0.6))
        m.c("body", VI2, (x + 0.6, 33 - L + 0.6, 6), (1.6, 1.4, 0.8))
    for x, L in ((-4, 10), (3, 13)):
        m.c("body", VI, (x, 33 - L / 2, -5.9), (0.9, L, 0.6))
    # a carved sun disc on the chest, half-buried under the vines
    paint(m, "body", "front", (0, 27.6, 5.3), [
        ".YYY.",
        "Y.Y.Y",
        "YYAYY",
        "Y.Y.Y",
        ".YYY.",
    ], {"Y": "yellow_terracotta", "A": ("orange_concrete", 0.4, True)}, px=1.1, depth=0.3)
    # arms: ring-stacked, heavy clay hands, vines wrapped around
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12.4 * s
        bevel(m, a, MO, (x, 34, 0), (7, 3, 7.4), 0.7)
        rings(a, x, 22, 32, 0, 5.4, 5.4, 4)
        rings(a, x, 14, 22, 0.6, 5.8, 5.8, 3)
        bevel(m, a, CL2, (x, 11.4, 1), (6.6, 4.2, 6.6), 0.8)
        for k in range(4):
            m.c(a, VI, (x, 30 - k * 4.4, 0), (6.2 if k % 2 else 0.9, 0.9, 0.9 if k % 2 else 6.2))
        m.c(a, VI, (x + 3 * s, 18, 1.6), (0.7, 12, 0.7))
        for t in (-2, 0, 2):
            m.c(a, CL, (x + t * 0.9, 8.6, 3), (1.6, 2, 1.6))
    # head: a cracked clay mask with one amber eye and a sprouting crown of leaves
    bevel(m, "head", CL, (0, 39.4, 0.6), (9, 9, 8), 1.0)
    paint(m, "head", "front", (0, 39.6, 4.65), [
        "DDDDDDD",
        ".......",
        "..D.A..",
        "..D....",
        ".DD.DD.",
        "..D.D..",
    ], {"D": DK, "A": ("orange_concrete", 0.5, True)}, px=1.0, depth=0.4)
    m.c("head", "shroomlight", (1, 39.6, 5.1), (0.8, 0.8, 0.3), light=True)
    tufts(m, "head", VI2, [(-3, 44.4, 0), (0, 45, 1), (3, 44.4, 0), (-1.6, 44.6, -2.4), (1.6, 44.6, -2.4)], 2.2, alt=MO)
    m.c("head", "flowering_azalea_leaves", (-3, 45.6, 2), (2, 2, 2))
    # little blooms and mushrooms living on it
    for bone, (x, y, z), col in (("body", (-8, 36.6, 2), "red_concrete"), ("body", (7.4, 36.6, -2), "yellow_concrete"), ("body", (2, 36.8, -4.4), "pink_concrete"),
                                 ("armL", (13, 35.8, 2), "yellow_concrete"), ("armR", (-12, 35.8, -2), "red_concrete"), ("head", (2.6, 44.8, 2.4), "light_blue_concrete")):
        m.c(bone, "lime_concrete", (x, y - 0.4, z), (0.4, 1.4, 0.4))
        m.c(bone, col, (x, y + 0.6, z), (1.2, 0.8, 1.2))
    for bone, (x, y, z) in (("legL", (7.8, 4, -2)), ("legR", (-7.6, 6, 1.6)), ("body", (-9.2, 24, 1))):
        m.c(bone, "mushroom_stem", (x, y, z), (0.6, 1.4, 0.6))
        m.c(bone, "red_concrete", (x, y + 0.9, z), (1.8, 0.6, 1.8))
    m.c("head", VI, (-4.6, 37, 4.4), (0.8, 5, 0.6))
    m.attacks = {"vines": "cast", "slam": "slam", "quake": "stomp", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def prism_sentinel():
    """A crystal golem cut from diamond and amethyst: faceted plates over a glowing cyan core, a gem set in
    its chest, crystal clusters growing from the shoulders and a visor slit for eyes."""
    m = Model("prism_sentinel", "biped", 1.7)
    biped(m, hip=15, legx=5.4, neck=35, shoulder=33, armx=12.4)
    m.bend = -16
    DI, DI2, AM, AM2, CO, DK = "diamond_block", "light_blue_concrete", "amethyst_block", "purple_stained_glass", "cyan_concrete", "polished_deepslate"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5.4 * s
        m.c(b, CO, (x, 8, 0), (4, 10, 4), light=True)
        bevel(m, b, DI, (x, 11.4, 0), (6.6, 6, 6.6), 0.9)
        bevel(m, b, DI2, (x, 4.6, 0.3), (6.2, 5, 6.2), 0.8)
        m.c(b, DK, (x, 1.2, 1), (7, 2.4, 8))
        m.c(b, DI, (x, 1.6, 5.2), (5.4, 2, 1))
    bevel(m, "hips", DK, (0, 16, 0), (14, 3, 9), 0.7)
    # torso: faceted diamond plates around a cyan core, a gem in the middle
    m.c("body", CO, (0, 25, 0), (12, 14, 8), light=True)
    for s in (1, -1):
        bevel(m, "body", DI, (4.2 * s, 27.6, 1.4), (7, 9, 9), 1.2)
        bevel(m, "body", DI2, (4 * s, 20.8, 1.2), (6.6, 4.4, 8.4), 0.9)
        bevel(m, "body", DI, (4.2 * s, 25.6, -3.6), (7.4, 13, 3.4), 1.0)
    bevel(m, "body", DI, (0, 33.4, 0), (17, 3.6, 10), 1.0)
    m.c("body", AM, (0, 27, 6.1), (3.6, 3.6, 1), (0, 0, 45), light=True)
    m.c("body", "magenta_stained_glass", (0, 27, 6.7), (2, 2, 0.6), (0, 0, 45), light=True)
    for y in (23, 31):
        m.c("body", DK, (0, y, 6.2), (6, 0.6, 0.4))
    # crystal clusters on the shoulders and back
    for s in (1, -1):
        for k, (dx, dy, dz, h, rz) in enumerate(((0, 0, 0, 7, 0), (1.6, -0.6, 1.6, 5, -22), (-1.4, -0.8, -1.4, 4.4, 20), (1.2, -1, -1.8, 3.6, -30))):
            m.c("body", AM if k % 2 == 0 else "pink_stained_glass", (7 * s + dx * s, 37 + dy + h / 2 - 1, -1 + dz), (1.8, h, 1.8), (10 * (k - 1.5), 0, rz * s), light=k == 0)
    for k, (x, y, h) in enumerate(((-2.6, 31, 5), (0, 29, 7), (2.6, 31, 5))):
        m.c("body", AM if k != 1 else "pink_stained_glass", (x, y, -6.8), (1.6, h, 1.6), (-28, 0, (k - 1) * 18))
    # arms: plated, with prism fists that glow at the knuckles
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12.4 * s
        bevel(m, a, DI, (x + 0.8 * s, 34, 0), (7.4, 4.6, 8), 1.0)
        m.c(a, CO, (x, 26, 0), (3.6, 10, 3.6), light=True)
        bevel(m, a, DI2, (x, 27, 0), (5.4, 6, 5.4), 0.8)
        bevel(m, a, DI, (x, 17.4, 0.8), (7, 8, 7), 1.0)
        for k in range(3):
            m.c(a, CO, (x + (k - 1) * 2, 13, 4.5), (1.4, 1.4, 0.4), light=True)
        m.c(a, AM, (x + 3.8 * s, 18, 0.8), (1, 5, 3), (0, 0, -10 * s))
    # head: a narrow diamond helm, a cyan visor slit, a single crystal horn
    bevel(m, "head", DI, (0, 39.6, 0.4), (8, 8, 8), 1.0)
    m.c("head", DK, (0, 40, 4.5), (6.6, 1.6, 0.4))
    m.c("head", CO, (0, 40, 4.75), (5.4, 0.8, 0.3), light=True)
    m.c("head", DI2, (0, 37, 4.5), (4, 2, 0.4))
    m.c("head", AM, (0, 46, 0.4), (1.8, 6, 1.8), (-12, 0, 0), light=True)
    m.c("head", "pink_stained_glass", (0, 49, -0.2), (1, 2.6, 1), (-12, 0, 0))
    # facet lines cut into the plates, gold-rimmed knee and elbow gems
    for s in (1, -1):
        paint(m, "body", "front", (4.2 * s, 27.6, 5.95), ["W...", ".W..", "..W.", "...W"] if s > 0 else ["...W", "..W.", ".W..", "W..."], {"W": "white_stained_glass"}, px=1.4, depth=0.2)
        paint(m, "body", "back", (4.2 * s, 26, -5.35), ["W..W", ".WW.", ".WW.", "W..W"], {"W": "white_stained_glass"}, px=1.4, depth=0.2)
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "gold_block", (5.4 * s, 9.2, 3.5), (2.6, 2.6, 0.6), (0, 0, 45))
        m.c(b, AM, (5.4 * s, 9.2, 3.9), (1.4, 1.4, 0.4), (0, 0, 45), light=True)
        for k in range(3):
            m.c(b, "white_stained_glass", (5.4 * s + 3.4 * s, 11 - k * 2.4, 0), (0.3, 1.6, 4))
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12.4 * s
        m.c(a, "gold_block", (x, 21.6, 4.1), (2.4, 2.4, 0.6), (0, 0, 45))
        m.c(a, AM, (x, 21.6, 4.5), (1.2, 1.2, 0.4), (0, 0, 45), light=True)
        for k, (dz, h) in enumerate(((-2, 4), (0, 5.4), (2, 3.4))):
            m.c(a, AM if k == 1 else "pink_stained_glass", (x + 2.6 * s, 37.4 + h / 2 - 1, dz), (1.4, h, 1.4), (dz * 8, 0, -20 * s))
    # floating shards that orbit the head
    m.bone("ring1", "head", (0, 40, 0))
    for k in range(5):
        import math
        a = 2 * math.pi * k / 5
        m.c("ring1", "light_blue_stained_glass" if k % 2 else AM, (math.sin(a) * 9, 43 + (k % 2) * 1.6, math.cos(a) * 9), (1.4, 2.6, 1.4), (30, k * 40, 20), light=k % 2 == 0)
    # diamond collar and a cyan belt of light
    bevel(m, "body", DI2, (0, 35.6, 0), (11, 1.6, 8), 0.4)
    m.c("hips", CO, (0, 16, 4.6), (10, 0.8, 0.4), light=True)
    m.c("hips", CO, (0, 16, -4.6), (10, 0.8, 0.4), light=True)
    for s_ in (1, -1):
        for k in range(4):
            m.c("body", "white_stained_glass", (7.6 * s_, 22 + k * 2.6, 2), (0.3, 1.4, 2))
    m.attacks = {"beam": "cast", "shards": "double", "slam": "slam", "shield": "roar"}
    m.melee = "swipe"
    return m


@model
def tiki_warden():
    """A volcanic tiki idol come to life: a huge carved mask for a head with a lit mouth, orange stone
    body cut with glyph bands, a feathered headdress and a jagged obsidian-edged war blade."""
    m = Model("tiki_warden", "biped", 1.7)
    biped(m, hip=12, legx=4.8, neck=28, shoulder=27, armx=11)
    m.bone("jaw", "head", (0, 30, 6))
    m.bone("blade", "armR", (-11, 12, 2))
    m.hold = {"blade": 40}
    m.bend = -36
    ST, ST2, DK, GL, OB, WD = "orange_terracotta", "red_sandstone", "brown_terracotta", "orange_concrete", "obsidian", "cut_red_sandstone"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.8 * s
        bevel(m, b, ST2, (x, 7.4, 0), (5.4, 9, 5.4), 0.7)
        band(m, b, DK, (x, 9, 0), (5.8, 1.2, 5.8))
        bevel(m, b, ST, (x, 1.6, 0.8), (6.4, 3.2, 7.6), 0.7)
        m.c(b, GL, (x, 5, 2.85), (1.4, 1.4, 0.3), light=True)
    # a grass skirt made of tufts over a stone belt
    bevel(m, "hips", DK, (0, 13.6, 0), (14, 2.6, 9), 0.6)
    for i in range(10):
        x = -6.3 + i * 1.4
        for z, d in ((4.6, 0.8), (-4.6, 0.8)):
            m.c("hips", "green_terracotta" if i % 3 else "lime_terracotta", (x, 9.8 - (i % 2) * 0.6, z), (1.3, 6.2 + (i % 3) * 0.8, d))
    # torso: carved blocks with a glyph band and a glowing heart mark
    bevel(m, "body", ST, (0, 20.4, 0), (14, 11, 9), 1.2)
    bevel(m, "body", ST2, (0, 26, 0), (16, 3, 10), 0.8)
    paint(m, "body", "front", (0, 20.4, 4.65), [
        "DD.DD.DD.DD",
        "D...D.D...D",
        "...........",
        "....GGG....",
        "...G.G.G...",
        "....GGG....",
    ], {"D": DK, "G": (GL, 0.4, True)}, px=1.0, depth=0.3)
    paint(m, "body", "back", (0, 21, -4.65), ["D.D.D.D", ".D.D.D.", "D.D.D.D"], {"D": DK}, px=1.4, depth=0.3)
    # arms: stone with glyph bracers
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11 * s
        bevel(m, a, ST2, (x, 26.6, 0), (6, 3.4, 6.4), 0.7)
        bevel(m, a, ST, (x, 20.6, 0), (4.6, 8, 4.6), 0.6)
        band(m, a, DK, (x, 15.6, 0.6), (5.4, 3, 5.4))
        paint(m, a, "front", (x, 15.6, 3.35), ["G.G", ".G."], {"G": (GL, 0.3, True)}, px=0.9, depth=0.2)
        bevel(m, a, ST, (x, 12.2, 1.2), (4.6, 3.4, 4.6), 0.6)
    # the mask: a tall carved face with angry brows, round eyes, a big lit mouth with teeth
    bevel(m, "head", ST, (0, 34.6, 1.4), (12, 13, 9), 1.2)
    paint(m, "head", "front", (0, 36.2, 6.0), [
        "DDDD....DDDD",
        ".DDDDD.DDDD.",
        "..WWW..WWW..",
        "..WKW..WKW..",
        "..WWW..WWW..",
        ".....DD.....",
        ".....DD.....",
    ], {"D": DK, "W": "white_terracotta", "K": ("black_concrete", 0.4)}, px=1.0, depth=0.5)
    m.c("head", DK, (0, 30.6, 6.2), (9, 3.6, 0.6))
    m.c("jaw", GL, (0, 30.4, 6.3), (7.4, 2.4, 0.6), light=True)
    paint(m, "jaw", "front", (0, 30.6, 6.7), ["W.W.W.W.W", "........."], {"W": "white_terracotta"}, px=0.85, depth=0.5)
    for s in (1, -1):
        m.c("head", ST2, (6.6 * s, 34, 1.4), (1.4, 8, 6))
        m.c("head", DK, (7.3 * s, 34, 3), (0.4, 4, 1.4))
    # headdress: a fan of feathers in red, orange, yellow and green behind the mask
    import math
    cols = ["red_concrete", "orange_concrete", "yellow_concrete", "lime_concrete", "yellow_concrete", "orange_concrete", "red_concrete"]
    for i, c in enumerate(cols):
        a = -60 + i * 20
        x, y = math.sin(math.radians(a)) * 6.4, 41 + math.cos(math.radians(a)) * 2.4
        m.c("head", c, (x, y + 3, -2.6), (1.6, 8, 0.8), (0, 0, -a), (x, y, -2.6))
        m.c("head", "white_concrete", (x + math.sin(math.radians(a)) * 3.8, y + 3 + math.cos(math.radians(a)) * 3.8, -2.6), (1, 1.6, 0.9), (0, 0, -a))
    band(m, "head", DK, (0, 41.4, 1.4), (12.4, 1.6, 9.4), studs=3, stud_block=GL)
    # the blade: a wooden paddle sword with obsidian teeth on both edges
    m.c("blade", "brown_wool", (-11, 12, 2), (1.8, 4, 1.8))
    m.c("blade", WD, (-11, 15, 2), (1.6, 2, 3.6))
    m.c("blade", "stripped_jungle_log", (-11, 25, 2), (1.2, 18, 4.4))
    for k in range(5):
        for dz in (1, -1):
            m.c("blade", OB, (-11, 18.4 + k * 3.2, 2 + dz * 2.6), (0.8, 2, 1.4), (45 * dz, 0, 0))
    m.c("blade", OB, (-11, 34.6, 2), (0.8, 2.2, 2.2), (45, 0, 0))
    m.attacks = {"meteor": "cast", "slam": "slam", "charge": "sweep", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def hollow_king():
    """A skeleton king: bone-white ribs and skull, a tall iron crown set with soul gems, a torn royal
    cloak of deep purple with gold trim, gilded pauldrons and a long soul-fire greatsword."""
    m = Model("hollow_king", "biped", 1.8)
    biped(m, hip=15, legx=4, neck=35, shoulder=33, armx=10.5)
    m.bone("jaw", "head", (0, 36.4, 3))
    m.bone("cape", "body", (0, 34, -4))
    m.bone("sword", "armR", (-10.5, 14, 2))
    m.hold = {"sword": 10}
    m.bend = -40
    BN, BN2, IR, GD, CL, CL2, SO = "bone_block", "calcite", "iron_block", "gold_block", "purple_terracotta", "magenta_terracotta", "light_blue_concrete"
    # legs: bone shins and thighs, armoured greaves, iron sabatons
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        m.c(b, BN2, (x, 11, 0), (2, 8, 2))
        m.c(b, BN, (x, 7, 0), (3, 2, 3))
        bevel(m, b, IR, (x, 4.6, 0.6), (4.6, 5, 4.6), 0.6)
        m.c(b, GD, (x, 7.2, 2.95), (3.6, 0.6, 0.4))
        bevel(m, b, "polished_deepslate", (x, 1.2, 1.2), (5, 2.4, 6.6), 0.5)
    # pelvis and a hanging tasset of iron plates over a purple skirt
    m.c("hips", BN, (0, 15.4, 0), (8, 2.4, 4))
    m.c("hips", CL, (0, 11.6, 0), (11, 6, 7))
    hem(m, "hips", CL, -5.5, 5.5, 8.6, 3.6, 0.6, 5, long=2.4, short=1.0)
    for x in (-3.6, 0, 3.6):
        plate(m, "hips", IR, (x, 12.4, 3.9), (3.2, 5, 0.6))
        m.c("hips", GD, (x, 10.2, 4.25), (3.2, 0.5, 0.2))
    # ribcage: spine, ribs that curve around, a glowing soul in the chest
    m.c("body", BN2, (0, 24, -2), (2, 18, 2))
    m.c("body", SO, (0, 25.4, 0.6), (3, 3, 3), light=True)
    m.c("body", "soul_lantern", (0, 25.4, 0.6), (1.6, 1.6, 1.6), light=True)
    for k, y in enumerate((19.4, 22, 24.6, 27.2, 29.8)):
        w = 9 + k * 0.8
        m.c("body", BN2, (0, y, 2.8), (w, 1.1, 1.1))
        for s in (1, -1):
            m.c("body", BN2, (w / 2 * s, y, 0.4), (1.1, 1.1, 5.2))
    m.c("body", BN2, (0, 25, 3.4), (1.6, 12, 0.8))
    # gilded collar and pauldrons
    bevel(m, "body", IR, (0, 32.6, 0), (14, 3, 7), 0.7)
    m.c("body", GD, (0, 31, 0), (14.4, 0.6, 7.4))
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10.5 * s
        bevel(m, a, IR, (x + 0.8 * s, 34, 0), (7, 3.4, 7.4), 0.7, (0, 0, -18 * s), (x, 33, 0))
        bevel(m, a, GD, (x + 2 * s, 31.6, 0), (5.4, 2, 6.4), 0.5, (0, 0, -26 * s), (x, 33, 0))
        m.c(a, SO, (x + 1 * s, 35.8, 0), (1.4, 1.4, 1.4), (0, 0, -18 * s), (x, 33, 0), light=True)
        m.c(a, BN2, (x, 26.4, 0), (2, 9, 2))
        m.c(a, BN, (x, 21.6, 0), (2.8, 2, 2.8))
        bevel(m, a, IR, (x, 17.4, 0.8), (4.4, 6, 4.4), 0.6)
        m.c(a, GD, (x, 20, 0.8), (4.6, 0.6, 4.6))
        m.c(a, BN2, (x, 13.4, 1.4), (2.6, 2.2, 3))
    # skull: hollow eyes with soul flames, a jaw that hangs, cracks, the crown
    bevel(m, "head", BN2, (0, 39.4, 0.4), (8.4, 7.6, 8.4), 1.0)
    paint(m, "head", "front", (0, 39.4, 4.6), [
        ".KKK.KKK.",
        ".KSK.KSK.",
        ".KKK.KKK.",
        "....K....",
        "...KKK...",
    ], {"K": "black_concrete", "S": (SO, 0.5, True)}, px=1.0, depth=0.4)
    bevel(m, "jaw", BN2, (0, 35.4, 1.6), (6.4, 2, 6), 0.5)
    paint(m, "jaw", "front", (0, 36.2, 4.65), ["W.W.W.W"], {"W": BN}, px=0.8, depth=0.5)
    m.c("head", BN, (2.6, 42.2, 4.5), (0.5, 2.4, 0.3), (0, 0, 20))
    band(m, "head", IR, (0, 43.8, 0.4), (9, 1.6, 9))
    for k, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
        h = 4 if k in (1, 2) else 3
        m.c("head", IR, (x, 44.6 + h / 2, 4.2), (1.6, h, 0.8))
        m.c("head", IR, (x, 44.6 + h / 2, -3.4), (1.6, h, 0.8))
        m.c("head", SO, (x, 44.6 + h + 0.3, 4.2), (0.8, 0.8, 0.8), light=True)
    for s in (1, -1):
        m.c("head", IR, (4.2 * s, 46, 0.4), (0.8, 3, 7))
    m.c("head", "magenta_concrete", (0, 44.4, 4.75), (1.6, 1.6, 0.4), (0, 0, 45), light=True)
    # cloak: deep purple with gold trim, torn at the bottom, a sigil on the back
    m.c("cape", CL, (0, 22, -5.2), (14, 22, 0.8))
    m.c("cape", GD, (0, 32.6, -5.4), (14.4, 1, 1))
    for s in (1, -1):
        m.c("cape", GD, (7.1 * s, 22, -5.3), (0.4, 22, 0.9))
    hem(m, "cape", CL, -7, 7, 11, -5.2, 0.8, 7, long=4, short=1.4)
    hem(m, "cape", CL2, -6, 6, 11, -5.5, 0.4, 4, long=2.2, short=1, seed=2)
    paint(m, "cape", "back", (0, 24, -5.6), [
        "..G.G.G..",
        "..GGGGG..",
        "...GSG...",
        "....G....",
        "...GGG...",
    ], {"G": GD, "S": (SO, 0.3, True)}, px=1.1, depth=0.2)
    # soul greatsword: a broad dark blade with a glowing cyan fuller and a gold cross-guard
    m.c("sword", "polished_deepslate", (-10.5, 13, 2), (1.4, 5, 1.4))
    m.c("sword", GD, (-10.5, 10, 2), (2.2, 1.6, 2.2), (0, 45, 0))
    m.c("sword", GD, (-10.5, 16, 2), (1.8, 1.4, 8))
    for s in (1, -1):
        m.c("sword", GD, (-10.5, 16.8, 2 + 4.6 * s), (1.4, 2.4, 1.4))
    m.c("sword", "netherite_block", (-10.5, 29, 2), (0.9, 24, 4.2))
    m.c("sword", SO, (-10.5, 28, 2), (1.1, 18, 0.9), light=True)
    m.c("sword", "netherite_block", (-10.5, 42, 2), (0.9, 2.6, 2.6), (45, 0, 0))
    m.attacks = {"souls": "cast", "slam": "slam", "minions": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


def spider_legs(m, body, blk, blk2, joint, xs, y, zs, spread=1.0, thick=2.2):
    """Eight spider legs: each a knee-up, foot-down chain from the side of the body."""
    for i, z in enumerate(zs):
        for s, side in ((1, "L"), (-1, "R")):
            name = f"leg{side}{i + 1}"
            m.bone(name, body, (xs * s, y, z))
            ang = (38 - i * 25) * spread
            tip = limb(m, name, blk, (xs * s, y, z), [(10, thick, (ang, 0, -58 * s)), (13, thick * 0.8, (ang * 0.8, 0, -148 * s), blk2), (4, thick * 0.5, (ang * 0.5, 0, -176 * s), blk2)], joint=joint)
            # bristles along the upper segment
            from models import dirof
            dx, dy, dz = dirof((ang, 0, -58 * s))
            for t in (0.35, 0.7):
                px, py, pz = xs * s + dx * 10 * t, y + dy * 10 * t, z + dz * 10 * t
                m.c(name, blk2, (px, py + thick * 0.6, pz), (0.5, 1.6, 0.5), (0, 0, -30 * s))


@model
def broodmother():
    """The spider queen: a black, hairy body banded in venom green, a swollen abdomen marked with a red
    hourglass, eight glowing eyes in two rows, long jointed legs and dripping fangs."""
    m = Model("broodmother", "spider", 1.6)
    m.bone("body", "root", (0, 12, 0))
    m.bone("abdomen", "body", (0, 14, -6))
    m.bone("head", "body", (0, 13, 7))
    m.bone("fangL", "head", (2, 9.6, 13))
    m.bone("fangR", "head", (-2, 9.6, 13))
    HA, HA2, MK, GR, DK = "black_wool", "gray_wool", "lime_concrete", "green_terracotta", "coal_block"
    bevel(m, "body", HA, (0, 13, 1), (13, 7, 13), 1.6)
    paint(m, "body", "top", (0, 16.5, 1), [".G.G.", "GGGGG", ".G.G."], {"G": GR}, px=1.6, depth=0.3)
    m.c("body", DK, (0, 9.4, 1), (9, 1, 10))
    # abdomen: big rounded mass, banded, an hourglass on top, spinnerets
    for k, (z, w, h) in enumerate(((-9, 16, 13), (-15, 20, 17), (-21, 18, 15), (-26, 12, 10))):
        bevel(m, "abdomen", HA, (0, 19 + h * 0.12, z), (w, h, 6.4), 2.4, (-10, 0, 0), (0, 14, -6))
    for k, z in enumerate((-12, -18, -24)):
        m.c("abdomen", MK if k != 1 else GR, (0, 19 + 9.6 - k * 0.6, z), (10 - k * 2, 0.5, 2), (-10, 0, 0), (0, 14, -6), light=k != 1)
        for s in (1, -1):
            m.c("abdomen", GR, ((9.6 - k * 0.6) * s, 19.4, z), (0.5, 7, 2), (-10, 0, 0), (0, 14, -6))
    paint(m, "abdomen", "top", (0, 28.6, -17.5), [
        "RRRRR",
        ".RRR.",
        "..R..",
        ".RRR.",
        "RRRRR",
    ], {"R": ("red_concrete", 0.4, True)}, px=1.2, depth=0.3)
    for x in (-1.6, 1.6):
        m.c("abdomen", HA2, (x, 15, -29.6), (1.6, 2.4, 2), (-40, 0, 0), (0, 14, -6))
    for (x, y, z) in ((-7.4, 25, -12), (7, 24, -23), (8.6, 18, -15)):
        m.c("abdomen", "white_wool", (x, y, z), (3.6, 3.6, 3.6), (0, 30, 0), (0, 14, -6))
        m.c("abdomen", MK, (x, y, z), (3.8, 0.6, 0.6), (0, 30, 0), (0, 14, -6), light=True)
    tufts(m, "abdomen", HA2, [(-6, 28, -16), (6, 28, -16), (-4, 27, -24), (4, 27, -24), (0, 28, -10)], 2)
    # head: eight eyes, two big and six small, mandibles and fangs
    bevel(m, "head", HA, (0, 13, 10.6), (9, 7, 6), 1.2)
    paint(m, "head", "front", (0, 13.6, 13.65), [
        ".r.r..r.r.",
        "..RR..RR..",
        "..RR..RR..",
        "r........r",
    ], {"R": ("red_concrete", 0.5, True), "r": ("red_concrete", 0.4, True)}, px=0.8, depth=0.4)
    for s, f in ((1, "fangL"), (-1, "fangR")):
        m.c(f, HA, (2 * s, 9.6, 13.6), (2.4, 2.4, 2.4))
        limb(m, f, "black_terracotta", (2 * s, 8.6, 14.4), [(3, 1.4, (150, 0, -10 * s)), (2.4, 1, (120, 0, -10 * s), "calcite")])
        m.c(f, MK, (2 * s * 1.2, 4.4, 16.4), (0.5, 1.4, 0.5), light=True)
    spider_legs(m, "body", HA, "black_terracotta", GR, 5.6, 12.6, (6, 2.6, -0.8, -4.2))
    # a ridge of bristle spikes along the abdomen and green venom sacs on its flanks
    for k, z in enumerate((-8, -11, -14, -17, -20, -23, -26)):
        for s in (1, -1):
            m.c("abdomen", HA2 if k % 2 else "black_terracotta", (2.4 * s, 28.4 - abs(z + 17) * 0.25, z), (0.8, 2.6, 0.8), (-10, 0, -20 * s), (0, 14, -6))
    for s in (1, -1):
        for k, z in enumerate((-14, -20)):
            m.c("abdomen", "lime_stained_glass", (10.4 * s, 20.4, z), (1.6, 3, 2.6), (-10, 0, 0), (0, 14, -6), light=True)
    # mandibles, palps and hair around the eyes
    for s in (1, -1):
        limb(m, "head", HA, (3.6 * s, 11, 13), [(3, 1.2, (110, 0, -30 * s)), (2.6, 1, (150, 0, -10 * s), "black_terracotta")])
        m.c("head", HA2, (4.8 * s, 16.2, 12), (1.6, 2, 1.6), (0, 0, -25 * s))
    tufts(m, "head", HA2, [(0, 16.8, 11), (-2.4, 16.6, 9), (2.4, 16.6, 9)], 1.6)
    tufts(m, "body", HA2, [(-6, 15.6, 6), (6, 15.6, 6), (-6.4, 15.4, -4), (6.4, 15.4, -4)], 2)
    # silk trailing from the spinnerets
    for k in range(3):
        m.c("abdomen", "white_stained_glass", (0, 13.6 - k * 2.4, -30.6 - k * 0.6), (0.4, 2.4, 0.4), (-40 + k * 10, 0, 0), (0, 14, -6))
    m.attacks = {"web": "spit", "venom": "fang", "minions": "drum", "leap": "leap"}
    m.melee = "fang"
    return m


def quad_leg(m, bone, x, y0, z, w, blk, blk2, foot, claws=None, s=1):
    """A beast leg: a thick upper, a lower with a joint plate and a broad foot with claws."""
    bevel(m, bone, blk, (x, y0 - 4, z), (w, 8, w), w * 0.16)
    bevel(m, bone, blk2, (x, y0 - 11, z + 0.4), (w * 0.82, 7, w * 0.82), w * 0.14)
    bevel(m, bone, foot, (x, 1.4, z + 1), (w * 1.05, 2.8, w * 1.25), 0.5)
    if claws:
        for t in (-0.3, 0, 0.3):
            m.c(bone, claws, (x + t * w, 0.8, z + 1 + w * 0.68), (w * 0.2, 1.4, 1.4))


@model
def ironhide_behemoth():
    """A war rhino in riveted iron barding: a great nose horn and a second smaller one, plated neck,
    overlapping back plates, chain fringe, a war banner on its back and glowing furnace eyes."""
    m = Model("ironhide_behemoth", "quad", 1.5)
    quad(m, body_y=19, legx=8.6, legz_front=10, legz_back=-12, neck_y=22, neck_z=17)
    HI, HI2, IR, IR2, DK, GD = "tuff", "polished_andesite", "iron_block", "light_gray_concrete", "polished_deepslate", "gold_block"
    for s, (b, z) in ((1, ("legFL", 10)), (-1, ("legFR", 10)), (1, ("legBL", -12)), (-1, ("legBR", -12))):
        quad_leg(m, b, 8.6 * s, 18, z, 7, HI, HI, DK, "calcite")
        plate(m, b, IR, (8.6 * s + 3.2 * s, 13.6, z), (1, 7, 6.4))
        for y in (11, 16):
            m.c(b, IR2, (8.6 * s + 3.8 * s, y, z), (0.4, 0.8, 0.8))
    # body: heavy hide, iron barding in overlapping plates with gold rivets, chain fringe below
    bevel(m, "body", HI, (0, 21, -1), (17, 13, 30), 2.4)
    for k, z in enumerate((9, 3, -3, -9)):
        bevel(m, "body", IR if k % 2 == 0 else IR2, (0, 27.6 - abs(k - 1.5) * 0.4, z), (19, 2.6, 6.6), 0.8)
        for s in (1, -1):
            bevel(m, "body", IR if k % 2 == 0 else IR2, (9.6 * s, 22.4, z), (1.6, 9, 6.4), 0.4)
            m.c("body", GD, (10.5 * s, 25.6, z), (0.5, 0.8, 0.8))
            for t in (-2, 0, 2):
                m.c("body", "chain", (10.4 * s, 16.4, z + t), (0.4, 3, 0.4))
    bevel(m, "body", HI2, (0, 15, -1), (13, 1.6, 24), 0.5)
    # a war banner on a pole above the back
    m.c("body", "dark_oak_log", (0, 36, -8), (1, 16, 1))
    m.c("body", "red_wool", (0, 38.4, -11.6), (0.6, 8, 6.4))
    paint(m, "body", "left", (0.3, 38.4, -11.6), ["..G..", ".GGG.", "GG.GG", ".GGG.", "..G.."], {"G": GD}, px=1.0, depth=0.2)
    hem(m, "body", "red_wool", -14.6, -8.6, 34.4, 0, 0.6, 3, long=2, face_z=False)
    m.c("body", GD, (0, 44.4, -8), (1.6, 1.6, 1.6), (45, 0, 45))
    # tail: a short club with iron bands
    limb(m, "tail", HI, (0, 23, -15.6), [(5, 3, (-120, 0, 0)), (4, 2.4, (-150, 0, 0))])
    m.c("tail", IR, (0, 20, -20.4), (3.4, 3.4, 3.4), (30, 0, 0))
    # head: wide armoured skull, nose horn and a second horn, furnace eyes, chain bridle
    bevel(m, "head", HI, (0, 21, 22.4), (11, 9, 11), 1.6)
    bevel(m, "head", HI2, (0, 18.6, 28), (8, 5, 3), 0.8)
    bevel(m, "head", IR, (0, 25.8, 21.6), (9, 2.2, 10), 0.6)
    m.c("head", GD, (0, 25.8, 26.7), (3, 1.4, 0.4))
    horn(m, "head", "bone_block", (0, 22, 29), 4, (40, 0, 0), (-14, 0, 0), 3, 0.78)
    horn(m, "head", "bone_block", (0, 25.6, 25.4), 2, (20, 0, 0), (-12, 0, 0), 2, 0.78)
    for s in (1, -1):
        m.c("head", "orange_concrete", (5.6 * s, 22.4, 24.8), (0.4, 1.2, 1.8), light=True)
        m.c("head", DK, (5.7 * s, 23.6, 24.8), (0.4, 0.6, 2.4))
        m.c("head", HI, (5.6 * s, 25.6, 19.6), (1.6, 3, 2), (0, 0, -30 * s))
        m.c("head", "chain", (5.8 * s, 18.4, 25), (0.4, 0.4, 6))
    bevel(m, "jaw", HI, (0, 16.4, 24.6), (8, 2.4, 6), 0.6)
    m.attacks = {"charge": "charge", "quake": "rear", "toss": "toss", "roar": "howl"}
    m.melee = "bite"
    return m


@model
def fenrir():
    """A giant frost wolf: a thick grey-white coat in layered tufts, a snarling muzzle with ice fangs,
    blue glowing eyes, a broken iron chain collar and ice crystals growing out of its back."""
    m = Model("fenrir", "quad", 1.55)
    quad(m, body_y=17, legx=6, legz_front=10, legz_back=-10, neck_y=22, neck_z=14)
    FU, FU2, FU3, ICE, ICE2, IR = "light_gray_wool", "white_wool", "gray_wool", "packed_ice", "blue_ice", "iron_block"
    for s, (b, z) in ((1, ("legFL", 10)), (-1, ("legFR", 10)), (1, ("legBL", -10)), (-1, ("legBR", -10))):
        quad_leg(m, b, 6 * s, 16, z, 5.4, FU, FU2, FU3, "calcite")
        tufts(m, b, FU2, [(6 * s + 2.4 * s, 13, z - 1), (6 * s, 10, z - 2.8)], 2)
    # body: deep chest, lean belly, a mane that thickens toward the neck
    bevel(m, "body", FU, (0, 19, -1), (12, 11, 24), 2.0)
    bevel(m, "body", FU2, (0, 20, 8), (14, 14, 9), 2.4)
    for k, z in enumerate((12, 9, 6, 3, 0, -3, -6, -9)):
        tufts(m, "body", FU2 if k < 3 else FU, [(-5, 25 - k * 0.3, z), (0, 26 - k * 0.3, z), (5, 25 - k * 0.3, z)], 2.6 - k * 0.1, alt=FU3)
    # ice crystals along the spine
    for k, (z, h) in enumerate(((2, 6), (-2.6, 8), (-7, 5))):
        m.c("body", ICE2 if k == 1 else ICE, (0, 25 + h / 2, z), (2, h, 2), (-10, 45, 0), light=k == 1)
        m.c("body", ICE, (1.6, 25 + h / 3, z - 1), (1.2, h * 0.6, 1.2), (-10, 45, 20))
    # broken chain collar
    band(m, "body", IR, (0, 22, 12.4), (14.6, 1.6, 4))
    for k in range(4):
        m.c("body", "chain", (-6.6, 18.4 - k * 1.6, 13 + k * 0.4), (0.6, 1.6, 0.6), (0, 0, 20 * (k % 2)))
    # tail: a long fluffy curve
    limb(m, "tail", FU, (0, 21, -12.6), [(5, 4, (-130, 0, 0), FU), (5, 3.6, (-160, 0, 0), FU2), (4, 3, (-175, 0, 0), FU2)])
    # head: long muzzle, wrinkled snarl, ice fangs, glowing eyes, ears
    bevel(m, "head", FU, (0, 23, 17.6), (9, 8, 8), 1.4)
    bevel(m, "head", FU2, (0, 21, 23.4), (5.4, 4, 6), 0.8)
    m.c("head", "black_concrete", (0, 22.4, 26.5), (2, 1.4, 0.6))
    paint(m, "head", "front", (0, 25, 21.65), ["KK...KK", ".KB.BK."], {"K": FU3, "B": ("light_blue_concrete", 0.4, True)}, px=1.0, depth=0.4)
    bevel(m, "jaw", FU2, (0, 18.6, 22.4), (4.6, 1.8, 6.4), 0.5)
    for s in (1, -1):
        m.c("head", ICE, (1.6 * s, 19.6, 26), (0.7, 1.8, 0.7), light=True)
        m.c("jaw", ICE, (1.2 * s, 19.8, 25), (0.6, 1.4, 0.6), light=True)
        m.c("head", FU, (3 * s, 28, 16), (2.4, 4, 1.6), (-10, 0, -14 * s))
        m.c("head", "pink_terracotta", (3 * s, 27.6, 16.8), (1.2, 2.4, 0.3), (-10, 0, -14 * s))
        tufts(m, "head", FU2, [(4.8 * s, 21, 16), (4.4 * s, 18, 15)], 2.2)
    # frost on the paws and shoulders, a scar over one eye, a white chest ruff
    for s in (1, -1):
        for b, z in (("legF" + ("L" if s > 0 else "R"), 10), ("legB" + ("L" if s > 0 else "R"), -10)):
            m.c(b, ICE, (6 * s, 3.4, z + 2.6), (4, 0.8, 1), light=False)
            m.c(b, "snow_block", (6 * s, 3.4, z), (5.6, 0.6, 5.6))
        tufts(m, "body", FU2, [(6.6 * s, 22, 10), (7 * s, 19, 6), (6.6 * s, 16, 10)], 2.4)
    m.c("head", "red_terracotta", (-2.6, 25, 21.8), (0.4, 3, 0.3), (0, 0, 20))
    tufts(m, "body", FU2, [(-2, 14.6, 12), (2, 14.6, 12), (0, 12.6, 11), (-3, 17, 13), (3, 17, 13)], 2.2)
    for s_ in (1, -1):
        m.c("head", FU3, (3.6 * s_, 26.4, 18), (2, 1, 3))
        m.c("body", FU3, (6.2 * s_, 23.4, 4), (0.4, 2, 6))
    m.attacks = {"pounce": "pounce", "frost": "howl", "minions": "howl", "charge": "charge"}
    m.melee = "bite"
    return m


@model
def tide_tyrant():
    """A drowned sea king: teal scaled skin, a coral and pearl crown, a barnacled breastplate of oxidised
    copper, a kelp cape, a fin crest and a glowing trident."""
    m = Model("tide_tyrant", "biped", 1.75)
    biped(m, hip=14, legx=4.6, neck=34, shoulder=32, armx=11.4)
    m.bone("jaw", "head", (0, 36, 4))
    m.bone("cape", "body", (0, 33, -4))
    m.bone("trident", "armR", (-11.4, 13, 2))
    m.hold = {"trident": 0}
    m.bend = -44
    SK, SK2, CU, CU2, KE, PE, GD = "prismarine", "dark_prismarine", "oxidized_copper", "oxidized_cut_copper", "dried_kelp_block", "white_concrete", "gold_block"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.6 * s
        bevel(m, b, SK, (x, 8.6, 0), (5.4, 10, 5.4), 0.7)
        paint(m, b, "front", (x, 9, 2.7), ["S.S", ".S.", "S.S"], {"S": SK2}, px=1.2, depth=0.2)
        bevel(m, b, CU, (x, 2, 0.8), (6, 4, 7.4), 0.6)
        m.c(b, SK, (x + 2.6 * s, 3, 3.6), (1, 2, 2.4), (0, 0, -20 * s))
    bevel(m, "hips", CU2, (0, 14.4, 0), (13, 4, 8.6), 0.6)
    for x in (-4, 0, 4):
        m.c("hips", KE, (x, 9.4, 4.2), (2.6, 7, 0.6))
        m.c("hips", KE, (x, 9.4, -4.2), (2.6, 7, 0.6))
    m.c("hips", PE, (0, 14.4, 4.5), (1.4, 1.4, 0.4), light=True)
    # torso: copper breastplate with a shell emblem, barnacles, teal scaled shoulders
    bevel(m, "body", SK, (0, 22, 0), (13, 10, 8.4), 1.0)
    bevel(m, "body", CU, (0, 28.4, 0.4), (16, 8, 9.6), 1.2)
    paint(m, "body", "front", (0, 28.4, 5.25), [
        "..G.G.G..",
        ".GGGGGGG.",
        "..GGGGG..",
        "...GGG...",
        "....G....",
    ], {"G": GD}, px=1.0, depth=0.3)
    for (x, y, z) in ((-5.6, 25, 4.8), (6, 31, 4.6), (-6.6, 31.6, -4.6), (5, 24.6, -4.4)):
        m.c("body", "calcite", (x, y, z), (1.4, 1.4, 1.4), (0, 45, 0))
        m.c("body", "white_terracotta", (x, y + 0.8, z), (0.8, 0.6, 0.8))
    paint(m, "body", "front", (0, 21.6, 4.25), ["S.S.S", ".S.S.", "S.S.S"], {"S": SK2}, px=1.4, depth=0.2)
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11.4 * s
        bevel(m, a, CU, (x + 0.6 * s, 33.4, 0), (6.6, 3.6, 7.4), 0.7, (0, 0, -16 * s), (x, 32, 0))
        for k in range(3):
            m.c(a, SK2, (x + (2.4 + k * 1.4) * s, 35.4 - k * 0.8, 0), (1, 3 - k * 0.6, 4), (0, 0, -40 * s))
        bevel(m, a, SK, (x, 25.6, 0), (5, 9, 5), 0.7)
        bevel(m, a, SK, (x, 18, 0.8), (5.4, 6.4, 5.4), 0.7)
        band(m, a, CU, (x, 18.6, 0.8), (5.8, 2.6, 5.8))
        m.c(a, PE, (x, 18.6, 3.85), (1, 1, 0.3), light=True)
        m.c(a, SK2, (x + 2.8 * s, 19, 0.8), (0.6, 4, 3), (0, 0, -20 * s))
    # head: fish-like, wide mouth, glowing yellow eyes, gill fins, crown of coral and pearls
    bevel(m, "head", SK, (0, 39, 1), (9, 8, 8.4), 1.0)
    paint(m, "head", "front", (0, 40, 5.25), [
        "D.......D",
        ".DYD.DYD.",
        ".........",
    ], {"D": SK2, "Y": ("yellow_concrete", 0.4, True)}, px=1.0, depth=0.4)
    bevel(m, "jaw", SK2, (0, 35.4, 2.6), (8, 2, 6.4), 0.5)
    paint(m, "jaw", "front", (0, 36.4, 5.85), ["W.W.W.W"], {"W": PE}, px=0.8, depth=0.4)
    for s in (1, -1):
        for k in range(3):
            m.c("head", SK2, (5 * s + k * 0.6 * s, 39.6 - k * 1.2, 0.6 - k * 0.8), (0.8, 3.4 - k * 0.6, 2.2), (0, 0, -30 * s))
    for k in range(5):
        m.c("head", SK2, (0, 43.6 + (2 - abs(k - 2)) * 0.6, -2.4 + k * 1.4), (0.8, 2.6, 1.2), (-10, 0, 0))
    band(m, "head", GD, (0, 43.4, 1), (9.4, 1.2, 8.8))
    for k, (x, c) in enumerate(((-3.6, "fire_coral_block"), (-1.2, "tube_coral_block"), (1.2, "brain_coral_block"), (3.6, "horn_coral_block"))):
        m.c("head", c, (x, 45.6 + (k % 2) * 0.8, 4.6), (1.6, 3.4 + (k % 2), 1.2))
        m.c("head", PE, (x, 44.2, 5.3), (0.8, 0.8, 0.4), light=True)
    # kelp cape
    m.c("cape", KE, (0, 20, -4.6), (13, 24, 0.8))
    hem(m, "cape", KE, -6.5, 6.5, 8, -4.6, 0.8, 7, long=4, short=1.4)
    for x in (-4, 0, 4):
        m.c("cape", "green_terracotta", (x, 20, -5.5), (1, 22, 0.4))
    # trident: a long gold shaft and three glowing tines
    m.c("trident", "gold_block", (-11.4, 24, 2), (1.1, 34, 1.1))
    m.c("trident", "prismarine_bricks", (-11.4, 40.8, 2), (5, 1.4, 1.4))
    for dx in (-2, 0, 2):
        h = 6 if dx == 0 else 4.6
        m.c("trident", "light_blue_concrete", (-11.4 + dx, 41.6 + h / 2, 2), (0.9, h, 0.9), light=True)
        m.c("trident", "light_blue_stained_glass", (-11.4 + dx, 41.6 + h + 0.6, 2), (0.6, 1.4, 0.6), (0, 0, 45), light=True)
    m.c("trident", PE, (-11.4, 39.6, 2), (1.6, 1.6, 1.6), (45, 0, 45), light=True)
    m.attacks = {"wave": "slam", "orbs": "cast", "pull": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


@model
def void_walker():
    """A towering ender lord: thin black limbs, a plated obsidian torso cracked with purple light, a
    flowing tattered cowl, purple eyes and a halo of floating end-stone shards."""
    m = Model("void_walker", "biped", 1.6)
    biped(m, hip=22, legx=3, neck=44, shoulder=42, armx=7.4)
    m.bone("jaw", "head", (0, 44.6, 3))
    m.bone("cape", "body", (0, 43, -3))
    m.bone("ring1", "head", (0, 50, 0))
    m.bend = -20
    BK, BK2, OB, PU, PU2, EN = "black_concrete", "polished_blackstone", "obsidian", "purple_concrete", "magenta_concrete", "end_stone_bricks"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3 * s
        m.c(b, BK, (x, 12, 0), (2.2, 20, 2.2))
        bevel(m, b, OB, (x, 15, 0.4), (3, 5, 3), 0.4)
        crack(m, b, "front", (x, 15, 1.9), [(0, 2), (0, -2)], PU, 0.5)
        m.c(b, BK2, (x, 1, 1), (3, 2, 4))
    bevel(m, "hips", OB, (0, 23, 0), (9, 3, 5), 0.5)
    # torso: obsidian plates with purple light leaking between them
    m.c("body", PU, (0, 33, 0), (8, 16, 4.6), light=True)
    for k, (y, w) in enumerate(((26.6, 8.4), (30.4, 9.6), (34.2, 10.4), (38, 11))):
        bevel(m, "body", OB, (0, y, 0), (w, 3, 5.4), 0.5)
    bevel(m, "body", BK2, (0, 41.6, 0), (13, 2.6, 6), 0.6)
    for s in (1, -1):
        m.c("body", PU2, (2 * s, 32.3, 2.8), (0.6, 0.5, 0.3), light=True)
    # arms: very long and thin, clawed hands, obsidian bracers
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 7.6 * s
        bevel(m, a, BK2, (x + 0.4 * s, 42, 0), (4, 2.4, 5), 0.5)
        m.c(a, BK, (x, 34, 0), (2, 14, 2))
        bevel(m, a, OB, (x, 26, 0.4), (3, 6, 3), 0.4)
        crack(m, a, "left" if s > 0 else "right", (x + 1.5 * s, 26, 0.4), [(0, 2), (0, -2)], PU, 0.5)
        m.c(a, BK, (x, 19, 0.6), (2, 9, 2))
        for t in (-1, 0, 1):
            limb(m, a, BK2, (x + t * 0.7, 14.4, 1), [(2.4, 0.6, (160, 0, 0)), (1.8, 0.5, (130, 0, 0))])
    # head: flat dark head, a wide glowing slit mouth, purple eyes, a hood
    bevel(m, "head", BK, (0, 48, 0), (8, 7, 8), 0.8)
    paint(m, "head", "front", (0, 48.4, 4.05), [
        "PPP..PPP",
        "PEP..PEP",
    ], {"P": (PU, 0.3, True), "E": (PU2, 0.4, True)}, px=1.0, depth=0.3)
    bevel(m, "jaw", BK, (0, 44.2, 0.4), (7, 1.6, 7), 0.4)
    m.c("jaw", PU, (0, 45, 3.85), (5, 0.6, 0.3), light=True)
    m.c("head", BK2, (0, 52, -0.6), (9, 1.4, 9))
    for s in (1, -1):
        m.c("head", BK2, (4.6 * s, 49, -0.6), (0.8, 7, 8.6))
    m.c("head", BK2, (0, 49.6, -4.6), (9, 6, 0.8))
    # halo of end-stone shards that turn around the head
    import math
    for k in range(6):
        a = 2 * math.pi * k / 6
        m.c("ring1", EN if k % 2 else "end_stone", (math.sin(a) * 7, 54 + (k % 2) * 1.4, math.cos(a) * 7), (1.6, 1.6, 1.6), (45, k * 30, 45))
        if k % 2 == 0:
            m.c("ring1", PU2, (math.sin(a) * 7, 54, math.cos(a) * 7), (0.6, 2.2, 0.6), light=True)
    # tattered cowl down the back
    m.c("cape", BK2, (0, 33, -3.6), (10, 20, 0.6))
    hem(m, "cape", BK2, -5, 5, 23, -3.6, 0.6, 6, long=4.6, short=1.6)
    for x in (-3, 1.6):
        m.c("cape", PU, (x, 30, -4), (0.5, 8, 0.3), light=True)
    # obsidian spikes jutting from the shoulders and spine, purple veins of light up the neck
    for s in (1, -1):
        for k, (dx, dy, dz, rz) in enumerate(((1.6, 2.4, 0, -30), (0.4, 2.8, -1.6, -10), (2.6, 1.4, 1.4, -55))):
            m.c("body", OB, (6.6 * s + dx * s, 42 + dy, dz), (1.2, 3.6 - k * 0.6, 1.2), (dz * 10, 0, rz * s))
            m.c("body", PU, (6.6 * s + dx * s * 1.2, 42 + dy * 1.5, dz), (0.6, 0.8, 0.6), light=True)
    for k, y in enumerate((28, 31.5, 35, 38.5)):
        m.c("body", OB, (0, y, -3.2), (1.4, 2.2, 1.6), (-30, 0, 0))
    paint(m, "body", "front", (0, 36, 2.75), ["..P..", ".PEP.", "..P.."], {"P": (PU, 0.3, True), "E": ("pearlescent_froglight", 0.4, True)}, px=0.9, depth=0.3)
    # long fingers of light down the legs, a purple drip from the jaw
    for s, b in ((1, "legL"), (-1, "legR")):
        for y in (8, 4):
            m.c(b, BK2, (3 * s, y, 0), (2.6, 0.8, 2.6))
        m.c(b, PU, (3 * s, 6, 1.35), (0.5, 3, 0.3), light=True)
    for s, a in ((1, "armL"), (-1, "armR")):
        for y in (37, 31, 22):
            m.c(a, BK2, (7.6 * s, y, 0), (2.6, 0.8, 2.6))
    for k in range(3):
        m.c("jaw", PU2, (-1.2 + k * 1.2, 43.4 - k * 0.5, 3.6), (0.4, 1.2 + k * 0.4, 0.4), light=True)
    # floating motes of void in a ring at the waist
    m.bone("ring2", "body", (0, 30, 0))
    import math
    for k in range(8):
        a = 2 * math.pi * k / 8
        m.c("ring2", "black_stained_glass" if k % 2 else PU2, (math.sin(a) * 9, 28 + (k % 3), math.cos(a) * 9), (1, 1, 1), (45, 0, 45), light=k % 2 == 0)
    for s_ in (1, -1):
        for y in (26.6, 30.4, 34.2):
            m.c("body", PU2, (4.6 * s_, y, 2.75), (0.6, 0.6, 0.3), light=True)
    m.attacks = {"blink": "cast", "orbs": "cast", "darkness": "roar", "pull": "sweep"}
    m.melee = "swipe"
    return m


@model
def storm_herald():
    """A floating storm caller: a hooded figure in grey storm cloth with copper armour that crackles,
    lightning rods for a crown, a long lightning-rod staff and a ring of spinning cloud stones; it has no
    legs, its robe ends in a swirl of cloud."""
    m = Model("storm_herald", "float", 1.7)
    m.bone("core", "root", (0, 18, 0))
    m.bone("head", "core", (0, 33, 0))
    m.mbone("armL", "core", (8, 30, 0))
    m.bone("ring1", "core", (0, 12, 0))
    m.bone("ring2", "core", (0, 36, 0))
    RB, RB2, CU, CU2, CL, YE, DK = "light_gray_wool", "gray_wool", "copper_block", "exposed_copper", "white_wool", "yellow_concrete", "gray_concrete"
    # robe: tapers into a swirl of cloud
    stack(m, "core", RB2, 0, 8, 0, [(5, 2, 5), (7, 3, 6), (9, 4, 7), (11, 4, 8), (12, 4, 8.4)])
    for k, (x, y, z, sz) in enumerate(((0, 6.6, 0, 4), (-2.6, 8.4, 1.6, 3.4), (2.4, 8, -1.8, 3), (0, 4.6, 0.6, 2.6), (1.6, 10, 2.4, 2.6), (-2, 10.6, -2.4, 2.6))):
        m.c("core", CL, (x, y, z), (sz, sz * 0.8, sz), (0, k * 30, 0))
    bevel(m, "core", RB, (0, 26.6, 0), (12, 9, 7.6), 1.0)
    # copper breastplate, belt and pauldrons with bolts drawn on them
    bevel(m, "core", CU, (0, 27.4, 0.6), (12.6, 6, 7.6), 1.0)
    paint(m, "core", "front", (0, 27.6, 4.45), [
        "...YY..",
        "..YY...",
        ".YYYY..",
        "...YY..",
        "..YY...",
    ], {"Y": (YE, 0.3, True)}, px=1.0, depth=0.3)
    band(m, "core", CU2, (0, 23, 0), (12.4, 1.6, 8.2), studs=4, stud_block=CU)
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8 * s
        bevel(m, a, CU, (x + 0.6 * s, 31, 0), (5.6, 3, 6.4), 0.6, (0, 0, -14 * s), (x, 30, 0))
        m.c(a, "lightning_rod", (x + 1.4 * s, 34, 0), (1, 4, 1), (0, 0, -12 * s))
        bevel(m, a, RB, (x, 25, 0.4), (4.4, 9, 4.6), 0.6)
        bevel(m, a, RB2, (x, 18.6, 1.4), (5, 5, 5), 0.6)
        m.c(a, CU2, (x, 16.6, 1.4), (5.4, 1, 5.4))
        m.c(a, "light_gray_terracotta", (x, 15, 2), (2.6, 2, 2.6))
    # the hood: deep, a pale face in shadow with lit eyes, lightning-rod crown
    bevel(m, "head", RB2, (0, 36, 0), (9, 8, 9), 1.0)
    m.c("head", "black_concrete", (0, 35.4, 4.2), (6, 5, 0.6))
    paint(m, "head", "front", (0, 35.6, 4.5), ["Y..Y", "....", ".WW."], {"Y": (YE, 0.4, True), "W": "light_gray_concrete"}, px=1.0, depth=0.3)
    m.c("head", RB, (0, 40.4, -0.6), (7, 1.6, 7))
    for k, x in enumerate((-3, 0, 3)):
        m.c("head", "lightning_rod", (x, 43 + (1 if k == 1 else 0), -0.6), (1, 4 + (2 if k == 1 else 0), 1))
    band(m, "head", CU, (0, 40, 0), (9.4, 1.2, 9.4))
    # staff: a tall copper rod forked at the top with a glowing core
    m.bone("staff", "armR", (-8, 15, 2))
    m.c("staff", CU2, (-8, 22, 2), (1.1, 34, 1.1))
    for s in (1, -1):
        m.c("staff", CU, (-8 + 1.4 * s, 40, 2), (0.8, 5, 0.8), (0, 0, -20 * s))
    m.c("staff", YE, (-8, 40.4, 2), (1.6, 1.6, 1.6), (45, 45, 0), light=True)
    m.c("staff", "light_blue_stained_glass", (-8, 40.4, 2), (2.6, 2.6, 2.6), (45, 45, 0), light=True)
    for y in (12, 20, 30):
        m.c("staff", CU, (-8, y, 2), (1.6, 1, 1.6))
    # spinning storm stones around the robe and a crackling ring at the shoulders
    import math
    for k in range(6):
        a = 2 * math.pi * k / 6
        m.c("ring1", "gray_concrete" if k % 2 else "light_gray_concrete", (math.sin(a) * 10, 12 + (k % 2) * 2, math.cos(a) * 10), (2.4, 1.8, 2.4), (0, k * 25, 15))
        if k % 2 == 0:
            m.c("ring1", YE, (math.sin(a) * 10, 13.4, math.cos(a) * 10), (0.5, 2.2, 0.5), (0, 0, 25), light=True)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.5
        m.c("ring2", "light_blue_stained_glass", (math.sin(a) * 11, 36, math.cos(a) * 11), (0.6, 3, 0.6), (0, 0, 35 if k % 2 else -35), light=True)
    # cloth panels down the robe with copper trim, a short shoulder cape, stormcloud billows at the hem
    for x in (-3.6, 0, 3.6):
        m.c("core", RB, (x, 16, 3.9 if x == 0 else 3.6), (3, 14, 0.5))
        m.c("core", CU2, (x, 9.4, 3.9 if x == 0 else 3.6), (3.2, 0.8, 0.6))
        paint(m, "core", "front", (x, 15, 4.25 if x == 0 else 3.95), ["Y", ".", "Y", "."], {"Y": (YE, 0.2, True)}, px=1.0, depth=0.2) if x == 0 else None
    bevel(m, "core", RB2, (0, 31.4, -1.6), (14, 2.4, 7), 0.6)
    m.c("core", RB2, (0, 24, -4.6), (12, 14, 0.6))
    hem(m, "core", RB2, -6, 6, 17, -4.6, 0.6, 6, long=3.6, short=1.4)
    for k, (x, y, z, sz) in enumerate(((3.6, 5.6, 2.4, 2.4), (-3.6, 5.2, -1.4, 2.6), (0, 3, -2, 2.2), (4.4, 9, -3, 2.2), (-4.6, 9.4, 3, 2.2), (0, 2.4, 2.4, 1.8))):
        m.c("core", CL if k % 2 else "white_concrete_powder", (x, y, z), (sz, sz * 0.8, sz), (0, k * 40, 0))
    # sparks that live in the folds
    for (x, y, z) in ((5.4, 20, 4), (-5, 14, 3.4), (2, 11, 4.2), (-6, 26, -3)):
        m.c("core", YE, (x, y, z), (0.4, 1.6, 0.4), (0, 0, 30), light=True)
    # a copper gorget with rivets, bolts of yellow on the sleeves, a second ring of rods at the head
    band(m, "core", CU2, (0, 31.6, 0.4), (10, 1.2, 7.4), studs=4, stud_block=CU)
    for s_, a in ((1, "armL"), (-1, "armR")):
        paint(m, a, "left" if s_ > 0 else "right", (8 * s_ + 2.3 * s_, 25, 0.4), ["Y.", ".Y", "Y.", ".Y"], {"Y": (YE, 0.2, True)}, px=1.0, depth=0.2)
        m.c(a, CU2, (8 * s_, 21.4, 0.4), (4.8, 0.8, 5))
        m.c(a, CU, (8 * s_, 23, 0.4), (4.6, 0.4, 4.8))
    import math as _m
    m.bone("ring3", "head", (0, 40, 0))
    for k in range(8):
        a = 2 * _m.pi * k / 8
        m.c("ring3", "lightning_rod" if k % 2 else CU, (_m.sin(a) * 6.4, 42, _m.cos(a) * 6.4), (0.8, 2.6 if k % 2 else 1.2, 0.8), (0, 0, 0), light=False)
    for (x, y, z) in ((0, 30.4, 4.3), (-4, 28, 4.2), (4, 28, 4.2)):
        m.c("core", CU, (x, y, z), (0.8, 0.8, 0.3))
    for k in range(4):
        m.c("core", "white_concrete_powder", (-4.6 + k * 3, 14 - (k % 2), -4.2), (2.4, 2, 1.6), (0, k * 30, 0))
    m.c("head", "white_concrete", (0, 36.6, 4.5), (0.6, 0.6, 0.2))
    # a lightning-bolt sigil on the chest
    paint(m, "core", "front", (0, 25, 4.4), ["..Y", ".Y.", "YYY", ".Y.", "Y.."], {"Y": (YE, 0.2, True)}, px=0.9, depth=0.2)
    m.attacks = {"lightning": "raise", "orbs": "spin", "pull": "pulse", "blink": "dive"}
    m.melee = "swipe"
    m.no_elbows = True
    return m


@model
def pharaoh():
    """A mummy pharaoh: linen-wrapped limbs with loose strips, a striped gold and lapis headdress with a
    cobra crest, a broad jewelled collar, a gold mask over one half of the face and a crook staff."""
    m = Model("pharaoh", "biped", 1.7)
    biped(m, hip=14, legx=4, neck=33, shoulder=31, armx=10.4)
    m.bone("jaw", "head", (0, 35, 3))
    m.bone("crook", "armR", (-10.4, 13, 2))
    m.hold = {"crook": 0}
    m.bend = -42
    LI, LI2, GD, LA, SA, DK = "white_wool", "smooth_sandstone", "gold_block", "lapis_block", "cut_sandstone", "black_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        bevel(m, b, LI, (x, 7.6, 0), (4.6, 12, 4.6), 0.5)
        for y in (4, 8, 12):
            m.c(b, LI2, (x, y, 0), (4.8, 0.7, 4.8), (0, 0, 8 * s))
        m.c(b, GD, (x, 1, 0.8), (5, 2, 6))
    # kilt: white pleated linen with a gold belt and a lapis-and-gold apron
    bevel(m, "hips", LI, (0, 12.4, 0), (12, 5, 7.6), 0.5)
    for x in (-4.4, -2.2, 0, 2.2, 4.4):
        m.c("hips", LI2, (x, 11.4, 3.9), (0.4, 5, 0.4))
    band(m, "hips", GD, (0, 15.2, 0), (12.4, 1.6, 8))
    paint(m, "hips", "front", (0, 11.6, 4.1), ["GG", "LL", "GG", "LL", "GG"], {"G": GD, "L": LA}, px=1.2, depth=0.3)
    # torso: wrapped, with loose strips and the broad collar
    bevel(m, "body", LI, (0, 23, 0), (12, 13, 7.6), 1.0)
    for k, y in enumerate((18.6, 21.6, 24.6, 27.6)):
        m.c("body", LI2, (0, y, 0), (12.2, 0.7, 7.8), (0, 0, 6 if k % 2 else -6))
    for x, L in ((-4.6, 5), (3, 7)):
        m.c("body", LI, (x, 17 - L / 2, 3.9), (1.2, L, 0.3), (0, 0, 8))
    for k, (w, c) in enumerate(((15, GD), (13.4, LA), (11.8, GD), (10.2, "red_concrete"))):
        m.c("body", c, (0, 30.4 - k * 1.1, 0.5), (w, 1.1, 8.4 - k * 0.3))
    m.c("body", "light_blue_concrete", (0, 26.6, 4.25), (1.8, 1.8, 0.4), (0, 0, 45), light=True)
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10.4 * s
        bevel(m, a, LI, (x, 25, 0), (4.6, 10, 4.6), 0.5)
        bevel(m, a, LI, (x, 17.4, 0.8), (4.8, 6, 4.8), 0.5)
        for y in (27, 23, 19.6):
            m.c(a, LI2, (x, y, 0.4), (4.8, 0.7, 4.8), (6, 0, 0))
        band(m, a, GD, (x, 21.4, 0.6), (5.2, 1.2, 5.2))
        band(m, a, LA, (x, 15.8, 0.8), (5.2, 1, 5.2))
        m.c(a, LI, (x + 2.6 * s, 13, 0.8), (0.4, 6, 1), (0, 0, 10 * s))
    # head: wrapped face with one glowing eye, half gold mask, the striped headdress and cobra
    bevel(m, "head", LI, (0, 37.6, 0.4), (8, 8, 8), 0.8)
    paint(m, "head", "front", (0, 38, 4.45), [
        "WWWGGGG.",
        "W.WGGGG.",
        "WKWGBGG.",
        "WWWGGGG.",
        "W.WGGGG.",
    ], {"W": LI2, "K": ("lime_concrete", 0.4, True), "G": GD, "B": "black_concrete"}, px=1.0, depth=0.3)
    for s in (1, -1):
        for k in range(6):
            m.c("head", GD if k % 2 == 0 else LA, (4.6 * s, 39.4 - k * 1.5, -0.6), (1.4, 1.5, 6.6))
    for k in range(4):
        m.c("head", GD if k % 2 == 0 else LA, (0, 42.6 - k * 0.2, 0.4 - k * 0.2), (9.4, 0.8, 8.8))
    m.c("head", GD, (0, 43.6, 4.2), (1.2, 2.4, 1.2))
    m.c("head", GD, (0, 45, 4.6), (2.2, 1.2, 1.2))
    m.c("head", "red_concrete", (0, 45, 5.3), (0.6, 0.4, 0.3), light=True)
    m.c("jaw", GD, (0, 32, 3.4), (1.6, 4, 1.2))
    for y in (33, 31):
        m.c("jaw", LA, (0, y, 3.4), (1.7, 0.4, 1.3))
    # crook: gold and lapis bands with a curl at the top
    m.c("crook", LA, (-10.4, 22, 2), (1.1, 30, 1.1))
    for y in (10, 15, 20, 25, 30):
        m.c("crook", GD, (-10.4, y, 2), (1.4, 1.6, 1.4))
    limb(m, "crook", GD, (-10.4, 37, 2), [(3, 1.2, (0, 0, 0)), (3, 1.2, (60, 0, 0)), (2.6, 1.2, (130, 0, 0)), (2, 1.2, (180, 0, 0))])
    # a scarab on the belt, an ankh on a chain, loose wraps trailing from the arms and legs, gold sandals
    paint(m, "hips", "front", (0, 15.2, 4.2), [".GBG.", "GBBBG", ".GBG."], {"G": GD, "B": ("light_blue_concrete", 0.3, True)}, px=0.8, depth=0.3)
    m.c("body", GD, (0, 25.6, 4.0), (0.8, 3.6, 0.4))
    m.c("body", GD, (0, 26.6, 4.0), (2.6, 0.8, 0.4))
    m.c("body", GD, (0, 28.3, 4.0), (1.8, 1.6, 0.4))
    m.c("body", DK, (0, 28.3, 4.15), (0.7, 0.7, 0.3))
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, LI, (4 * s + 2.4 * s, 6, -1), (0.4, 5, 1), (0, 0, 14 * s))
        m.c(b, GD, (4 * s, 2.6, 2.6), (1, 1.2, 1.4))
        m.c(b, LA, (4 * s, 9.6, 2.45), (2, 2, 0.3), (0, 0, 45))
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, LI2, (10.4 * s, 28.6, 0), (5, 1.8, 5))
        m.c(a, GD, (10.4 * s, 29.8, 0), (5.2, 0.6, 5.2))
    # headdress lappets that fall over the shoulders, a ceremonial beard, a gold band on the brow
    for s in (1, -1):
        for k in range(5):
            m.c("head", GD if k % 2 == 0 else LA, (4.4 * s, 33.4 - k * 1.4, 2.2), (2.2, 1.4, 1.6))
    for k in range(3):
        m.c("head", GD if k % 2 == 0 else LA, (0, 32.8 - k * 1.2, 4.0), (1.8 - k * 0.2, 1.2, 1.2))
    for s_ in (1, -1):
        m.c("body", GD, (6.2 * s_, 23, 0), (0.4, 12, 0.4))
        m.c("hips", LA, (6.2 * s_, 12.4, 0), (0.4, 4.6, 6))
    m.attacks = {"curse": "cast", "minions": "roar", "sand": "sweep", "blink": "cast"}
    m.melee = "swipe"
    return m


@model
def executioner():
    """A giant headsman: a black hood with a single eye slit, a bare grey chest crossed with chains, a
    blood-red apron over leather, iron manacles on its wrists and a huge crescent axe."""
    m = Model("executioner", "biped", 1.85)
    biped(m, hip=14, legx=5, neck=34, shoulder=32, armx=12)
    m.bone("axe", "armR", (-12, 13, 2))
    m.hold = {"axe": 14}
    m.bend = -30
    HD, SK, SK2, LE, LE2, AP, IR, DK = "black_wool", "light_gray_terracotta", "gray_terracotta", "brown_terracotta", "brown_concrete", "red_terracotta", "iron_block", "polished_deepslate"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5 * s
        bevel(m, b, LE, (x, 9, 0), (6.4, 10, 6.4), 0.8)
        for y in (6, 10):
            band(m, b, LE2, (x, y, 0), (6.8, 1, 6.8), studs=2, stud_block=IR)
        bevel(m, b, DK, (x, 2, 0.8), (7, 4, 8), 0.7)
    bevel(m, "hips", LE2, (0, 15.4, 0), (15, 3.4, 9.6), 0.6)
    band(m, "hips", LE, (0, 17, 0), (15.4, 1.2, 10), studs=4, stud_block=IR)
    # the apron: blood red, stained darker at the bottom, torn
    m.c("hips", AP, (0, 10.6, 5.2), (10, 11, 0.6))
    paint(m, "hips", "front", (0, 7.6, 5.55), [".DD..D.DD.", "DDD.DDDDDD", "DDDDDDDDDD"], {"D": "red_nether_bricks"}, px=1.0, depth=0.2)
    hem(m, "hips", AP, -5, 5, 5.1, 5.2, 0.6, 5, long=2.4, short=1)
    # torso: broad grey chest, scars, chains crossing it, a gut
    bevel(m, "body", SK, (0, 22.4, 0.6), (17, 10, 11), 1.6)
    bevel(m, "body", SK, (0, 29.4, 0), (20, 6, 11), 1.6)
    paint(m, "body", "front", (0, 25, 6.15), ["S.....S", ".S...S.", "..S.S..", ".......", "..SSS.."], {"S": SK2}, px=1.2, depth=0.2)
    for r in (34, -34):
        m.c("body", "chain", (0, 26, 0), (1.4, 24, 12.4), (0, 0, r))
    m.c("body", IR, (0, 26.4, 6.4), (2.6, 2.6, 1), (0, 0, 45))
    # shoulder: a leather pauldron on the left, a spiked iron one on the right
    bevel(m, "armL", LE, (12.8, 33.6, 0), (7, 3.4, 8), 0.6, (0, 0, -16), (12, 32, 0))
    m.c("armL", LE2, (14, 32, 0), (5.4, 0.8, 8.2), (0, 0, -24), (12, 32, 0))
    bevel(m, "armR", IR, (-12.8, 33.6, 0), (7.4, 3.6, 8.4), 0.6, (0, 0, 16), (-12, 32, 0))
    spikes(m, "armR", IR, [(-13.6, 35.4, -2.4), (-13.6, 35.4, 0), (-13.6, 35.4, 2.4)], (0, 0, 30), 3, 1.0)
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 12 * s
        bevel(m, a, SK, (x, 25.6, 0), (6.6, 10, 6.6), 0.9)
        bevel(m, a, SK, (x, 17.4, 0.8), (6.6, 7, 6.6), 0.9)
        bevel(m, a, IR, (x, 16, 0.8), (7.2, 3, 7.2), 0.5)
        for k in range(3):
            m.c(a, "chain", (x + 1.6 * s, 13.6 - k * 1.6, 0.8 + 3.8), (0.6, 1.6, 0.6), (0, 0, 20 * (k % 2)))
        bevel(m, a, SK2, (x, 12.4, 1.6), (5.6, 3, 5.6), 0.6)
    # the hood: tall and pointed, one slit with two red eyes, a stained edge
    bevel(m, "head", HD, (0, 38.6, 0.6), (9.4, 9, 9.4), 1.2)
    stack(m, "head", HD, 0, 43, -0.4, [(7.6, 2, 7.6), (5.6, 2, 5.6), (3.6, 1.6, 3.6)])
    m.c("head", "black_concrete", (0, 39.4, 5.35), (7, 2.4, 0.3))
    paint(m, "head", "front", (0, 39.4, 5.55), [".R...R."], {"R": ("red_concrete", 0.3, True)}, px=1.0, depth=0.3)
    m.c("head", HD, (0, 34.4, 3.4), (11, 1.6, 6))
    hem(m, "head", HD, -5.5, 5.5, 34, 5.6, 0.8, 5, long=2, short=0.8)
    # the axe: a long iron-shod haft and a great crescent blade
    m.c("axe", "dark_oak_log", (-12, 24, 2), (1.6, 32, 1.6))
    for y in (13, 16, 33):
        m.c("axe", IR, (-12, y, 2), (2, 0.8, 2))
    bevel(m, "axe", "polished_andesite", (-12, 36, 6.4), (1.2, 10, 8), 1.2)
    for k in range(5):
        m.c("axe", "iron_block", (-12, 32 + k * 2, 10.2 + (2 - abs(k - 2)) * 0.8), (1, 2.2, 1.4))
    m.c("axe", "red_concrete", (-12, 34.6, 10.6), (1.1, 1.4, 1))
    m.c("axe", DK, (-12, 36, 2.6), (2, 4, 2.6))
    m.c("axe", IR, (-12, 41.4, 2), (1, 3, 1))
    # a ring of keys and a sack on the belt, stitched scars on the arms, nails in the boot soles, a shackle
    m.c("hips", "iron_block", (-5.6, 14.6, 5.2), (2.4, 2.4, 0.4))
    for k in range(3):
        m.c("hips", "gold_block", (-6.4 + k * 0.8, 12.6, 5.3), (0.4, 1.8, 0.3))
    m.c("hips", "brown_wool", (6, 13, 4.6), (3.4, 3.4, 2))
    m.c("hips", "brown_terracotta", (6, 14.8, 4.6), (1.6, 0.8, 1.6))
    for s_, a in ((1, "armL"), (-1, "armR")):
        x = 12 * s_
        for k in range(3):
            m.c(a, SK2, (x + 3.35 * s_, 26 - k * 1.2, 0.4 - k * 0.6), (0.3, 0.4, 1.6))
    for s_, b in ((1, "legL"), (-1, "legR")):
        for t in (-2.2, 0, 2.2):
            m.c(b, "iron_block", (5 * s_ + t, 0.3, 4.85), (0.6, 0.6, 0.3))
    m.c("legL", "iron_block", (5, 4.6, 0), (7.6, 1.6, 7.6))
    m.c("legL", "chain", (5 + 3.8, 3, 0), (0.6, 3, 0.6))
    m.attacks = {"slam": "slam", "charge": "sweep", "chains": "roar", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def ember_queen():
    """A fire witch queen: a gown of magma and nether brick flaring into flame at the hem, a black corset
    with gold lacing, a crown of blaze rods, burning hair and a sceptre topped with a fire orb."""
    m = Model("ember_queen", "biped", 1.7)
    biped(m, hip=14, legx=3, neck=31, shoulder=29.6, armx=8.4)
    m.bone("cape", "body", (0, 30, -3))
    m.bone("sceptre", "armR", (-8.4, 14, 2))
    m.hold = {"sceptre": 0}
    m.bend = -50
    GW, GW2, MA, CO, GD, SK, FL = "red_nether_bricks", "nether_bricks", "magma_block", "black_concrete", "gold_block", "orange_terracotta", "orange_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, CO, (3 * s, 1.6, 1.6), (2.6, 3.2, 3.4))
    # the gown: a stepped bell of nether brick with a magma band and flames licking up from the hem
    stack(m, "hips", GW, 0, 1, 0, [(15, 3, 12), (14, 3, 11), (12.4, 3, 10), (11, 3, 9), (9.6, 3, 8)])
    m.c("hips", MA, (0, 2.6, 0), (15.4, 1.6, 12.4), light=True)
    for k in range(10):
        import math
        a = 2 * math.pi * k / 10
        h = 3 + (k % 3) * 1.2
        m.c("hips", FL if k % 2 else "yellow_concrete", (math.sin(a) * 7.2, 4 + h / 2, math.cos(a) * 5.8), (1.4, h, 1.4), (0, math.degrees(a), 0), light=True)
    for x in (-3.4, 0, 3.4):
        m.c("hips", GW2, (x, 8, 5.6 - abs(x) * 0.15), (1, 12, 0.6))
    # corset: black with gold lacing, a ruby at the heart, puffed sleeves
    bevel(m, "body", CO, (0, 21, 0), (9.6, 9, 6.4), 0.8)
    for k in range(4):
        m.c("body", GD, (0, 18 + k * 2, 3.3), (2.4, 0.4, 0.3), (0, 0, 30 if k % 2 else -30))
    bevel(m, "body", GW, (0, 27, 0), (11, 4, 6.8), 0.8)
    m.c("body", "red_concrete", (0, 27, 3.55), (1.6, 1.6, 0.4), (0, 0, 45), light=True)
    for s in (1, -1):
        m.c("body", GD, (5.4 * s, 21, 0), (0.4, 9, 6.6))
    bevel(m, "body", GD, (0, 29.4, 0), (11.6, 1, 7.4), 0.3)
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8.4 * s
        bevel(m, a, GW, (x, 27.6, 0), (5.4, 4.6, 5.4), 1.0)
        m.c(a, GD, (x, 25.2, 0), (4.4, 0.6, 4.4))
        m.c(a, SK, (x, 20.6, 0.4), (2.6, 8, 2.6))
        bevel(m, a, CO, (x, 16.6, 1), (3.4, 4, 3.4), 0.4)
        m.c(a, FL, (x, 14.4, 1.4), (1.6, 0.6, 1.6), light=True)
    # head: dark-skinned queen, gold eyes, burning hair, a crown of blaze rods
    bevel(m, "head", SK, (0, 35, 0.4), (7, 7, 7), 0.8)
    paint(m, "head", "front", (0, 35.4, 3.95), ["KK.KK", "Y...Y", ".....", "..R.."], {"K": CO, "Y": ("yellow_concrete", 0.3, True), "R": "red_terracotta"}, px=1.0, depth=0.3)
    for k, (x, y, z, h) in enumerate(((-3, 37, -3, 6), (0, 38, -3.6, 8), (3, 37, -3, 6), (-3.6, 33, -2, 6), (3.6, 33, -2, 6), (0, 32, -4, 8))):
        m.c("head", FL if k % 2 else "red_concrete", (x, y, z), (2.6, h, 2.6), (-14, 0, x * 3), light=True)
        m.c("head", "yellow_concrete", (x * 1.1, y + h / 2, z - 0.6), (1.4, 2, 1.4), (-14, 0, x * 3), light=True)
    band(m, "head", GD, (0, 38.4, 0.4), (7.6, 1.2, 7.6))
    for k, x in enumerate((-3, -1, 1, 3)):
        m.c("head", "blaze_rod" if False else "orange_concrete", (x, 40.6 + (k in (1, 2)), 3.4), (0.7, 3.2 + (k in (1, 2)) * 1.2, 0.7), light=True)
    # a flowing cape of fire cloth
    m.c("cape", GW, (0, 18, -3.6), (11, 22, 0.6))
    hem(m, "cape", FL, -5.5, 5.5, 7, -3.6, 0.6, 6, long=3.6, short=1.4, alt="yellow_concrete")
    # sceptre: gold with a ring holding a fire orb
    m.c("sceptre", GD, (-8.4, 22, 2), (1, 22, 1))
    m.c("sceptre", GD, (-8.4, 33.6, 2), (3.4, 3.4, 0.6))
    m.c("sceptre", "shroomlight", (-8.4, 33.6, 2), (2, 2, 2), (45, 45, 0), light=True)
    m.c("sceptre", "orange_stained_glass", (-8.4, 33.6, 2), (3, 3, 3), (45, 45, 0), light=True)
    # gold flame embroidery climbing the gown, layered panels, a ruby necklace and shoulder flames
    for x in (-5, 5):
        paint(m, "hips", "front", (x, 7.2, 5.3), ["..G.", ".GG.", "GG.G", ".GG.", "..G."], {"G": GD}, px=0.8, depth=0.2)
    paint(m, "hips", "back", (0, 7.2, -5.3), ["G..G..G", ".GG.GG.", "..GGG..", "...G..."], {"G": GD}, px=0.9, depth=0.2)
    for s_ in (1, -1):
        paint(m, "hips", "left" if s_ > 0 else "right", (6.6 * s_, 6.4, 0), [".G..G.", "GGGGGG", "......", "G.GG.G"], {"G": GD}, px=0.9, depth=0.2)
    for k, (y, w, d) in enumerate(((13.8, 10.4, 8.4), (11, 12, 9.4))):
        m.c("hips", GW2, (0, y, 0), (w, 0.6, d))
    for k in range(5):
        m.c("body", "red_concrete" if k % 2 else GD, (-2.4 + k * 1.2, 25.2 - (2 - abs(k - 2)) * 0.5, 3.5), (0.8, 0.8, 0.3), light=k % 2 == 1)
    for s_, a in ((1, "armL"), (-1, "armR")):
        x = 8.4 * s_
        for k, (dx, h) in enumerate(((0, 4), (1.4, 3), (-1.4, 2.6))):
            m.c(a, FL if k else "yellow_concrete", (x + dx * s_, 31 + h / 2, -0.4 + k * 0.6), (1.2, h, 1.2), (0, 0, -10 * s_), light=True)
        m.c(a, GD, (x, 18.4, 0.4), (2.8, 0.6, 2.8))
        m.c(a, "red_concrete", (x, 18.4, 1.75), (0.6, 0.6, 0.2), light=True)
    # hair: long flaming locks down her back
    for k, (x, y, h) in enumerate(((-2.4, 28.6, 7), (0, 27.6, 9), (2.4, 28.6, 7))):
        m.c("head", "red_concrete" if k != 1 else FL, (x, y, -3.6), (2, h, 1.2), (8, 0, 0), light=True)
    # crown jewels and a floating ring of embers around her
    for x in (-2, 2):
        m.c("head", "red_concrete", (x, 38.4, 4.0), (0.8, 0.8, 0.3), light=True)
    m.c("head", "yellow_concrete", (0, 38.4, 4.0), (1, 1, 0.3), light=True)
    m.bone("ring1", "body", (0, 22, 0))
    import math
    for k in range(10):
        a = 2 * math.pi * k / 10
        m.c("ring1", FL if k % 2 else "yellow_concrete", (math.sin(a) * 11, 14 + (k % 3) * 3, math.cos(a) * 11), (0.8, 0.8, 0.8), (45, 0, 45), light=True)
    for k in range(6):
        m.c("cape", GD, (-4.4 + k * 1.76, 28.6, -4), (0.6, 0.6, 0.3))
    m.attacks = {"meteor": "cast", "fire": "double", "minions": "roar", "blink": "cast"}
    m.melee = "swipe"
    return m


@model
def gravelord():
    """A necromancer lord: a skull face under a deep hood, a mantle of bone and black feathers, robes
    stitched with green soul thread, a lantern of trapped souls on a chain and a scythe-staff."""
    m = Model("gravelord", "biped", 1.75)
    biped(m, hip=13, legx=3.4, neck=32, shoulder=30, armx=9)
    m.bone("jaw", "head", (0, 33, 2.6))
    m.bone("scythe", "armR", (-9, 13, 2))
    m.hold = {"scythe": 0}
    m.bend = -44
    RB, RB2, BN, FE, GR, GR2, DK = "gray_concrete", "light_gray_concrete", "calcite", "black_wool", "lime_concrete", "green_terracotta", "polished_blackstone"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, DK, (3.4 * s, 1.4, 1.4), (3, 2.8, 4))
    # robe: long, stepped, torn hem, green soul stitching
    stack(m, "hips", RB, 0, 0.6, 0, [(13, 3, 10), (12, 3, 9), (11, 4, 8.4), (10.4, 4, 8)])
    hem(m, "hips", RB, -6.5, 6.5, 1.2, 5, 0.6, 7, long=2.2, short=0.8)
    for x in (-2.6, 2.6):
        for k in range(5):
            m.c("hips", GR, (x, 2.6 + k * 2.4, 4.6 - k * 0.15), (0.4, 1.2, 0.3), (0, 0, 30 if k % 2 else -30), light=True)
    band(m, "hips", "brown_terracotta", (0, 13.6, 0), (10.8, 1.4, 8.4))
    for k, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
        m.c("hips", BN if k % 2 else "bone_block", (x, 12, 4.4), (1.2, 1.6, 0.8))
    # torso: robe top, a bone mantle and a ridge of black feathers
    bevel(m, "body", RB, (0, 21, 0), (10.4, 12, 7.4), 0.8)
    m.c("body", RB2, (0, 21, 3.75), (2, 12, 0.3))
    paint(m, "body", "front", (0, 22, 3.95), ["G.G", ".G.", "G.G", ".G.", "G.G"], {"G": (GR, 0.2, True)}, px=0.8, depth=0.2)
    for k, x in enumerate((-5, -3, -1, 1, 3, 5)):
        m.c("body", BN, (x, 27.6 - abs(x) * 0.2, 3.9), (1.4, 3, 0.8), (0, 0, x * 3))
    for s in (1, -1):
        for k in range(4):
            m.c("body", FE, (6.4 * s + k * 0.6 * s, 29.6 + k * 0.6, -1 + k * 0.4), (2, 5 - k * 0.6, 1), (-20, 0, -40 * s + k * 10 * s))
    tufts(m, "body", FE, [(-4, 29.6, -3.4), (0, 30.2, -3.8), (4, 29.6, -3.4)], 2.6)
    # arms: bell sleeves, bony hands
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 9 * s
        bevel(m, a, RB, (x, 24, 0), (4.4, 10, 4.6), 0.6)
        bevel(m, a, RB, (x, 16.6, 1), (5.4, 6, 5.6), 0.8)
        m.c(a, GR2, (x, 13.8, 1), (5.6, 0.6, 5.8))
        m.c(a, BN, (x, 12.4, 1.6), (2.4, 2.4, 2.4))
        for t in (-0.8, 0, 0.8):
            m.c(a, BN, (x + t, 10.8, 2.4), (0.5, 2, 0.5))
    # head: a skull deep in the hood with green fire in the eyes
    bevel(m, "head", RB, (0, 36.4, -0.2), (9, 9.4, 9), 1.0)
    m.c("head", "black_concrete", (0, 36, 4.2), (6.6, 7, 0.4))
    bevel(m, "head", BN, (0, 36.4, 3.6), (5.6, 5.4, 1.6), 0.4)
    paint(m, "head", "front", (0, 36.8, 4.45), ["KK.KK", "GK.KG", ".....", "..K.."], {"K": "black_concrete", "G": (GR, 0.3, True)}, px=1.0, depth=0.3)
    bevel(m, "jaw", BN, (0, 33, 3.6), (4.4, 1.6, 1.6), 0.3)
    paint(m, "jaw", "front", (0, 33.4, 4.45), ["W.W.W"], {"W": "bone_block"}, px=0.8, depth=0.3)
    m.c("head", RB, (0, 41.6, -1.6), (7, 2, 7))
    m.c("head", RB, (0, 43, -3), (4, 2, 4))
    # soul lantern on a chain hanging from the left hand
    for k in range(3):
        m.c("armL", "chain", (9, 10 - k * 1.6, 1.6), (0.5, 1.6, 0.5))
    m.c("armL", "soul_lantern", (9, 4.6, 1.6), (2.4, 2.8, 2.4), light=True)
    m.c("armL", "lime_stained_glass", (9, 4.6, 1.6), (1.6, 2, 1.6), light=True)
    # scythe-staff: a crooked shaft and a long bone blade
    m.c("scythe", "dark_oak_log", (-9, 22, 2), (1.2, 32, 1.2))
    for y in (12, 22, 30):
        m.c("scythe", "chain", (-9, y, 2), (1.5, 0.8, 1.5))
    m.c("scythe", BN, (-9, 37.6, 2), (2, 2, 2))
    for k in range(5):
        m.c("scythe", BN if k < 4 else "bone_block", (-9, 38.4 - k * 0.9, 4.4 + k * 2.2), (0.8, 2 - k * 0.2, 2.4), (-20 - k * 8, 0, 0))
    m.c("scythe", GR, (-9, 38.4, 3.2), (0.9, 0.9, 0.9), light=True)
    # grey stitched panels and a green rune band on the back, bone spikes on the shoulders, hood rim
    for x in (-3.8, 3.8):
        m.c("hips", RB2, (x, 7, 4.5), (1.6, 12, 0.3))
        m.c("hips", RB2, (x, 7, -4.5), (1.6, 12, 0.3))
    paint(m, "body", "back", (0, 22, -3.75), ["G.G.G", ".GGG.", "G.G.G", ".....", "GGGGG"], {"G": (GR, 0.2, True)}, px=1.0, depth=0.2)
    paint(m, "hips", "back", (0, 8, -4.7), ["G...G", ".G.G.", "..G..", ".G.G.", "G...G"], {"G": (GR, 0.2, True)}, px=1.0, depth=0.2)
    for s_ in (1, -1):
        spikes(m, "body", BN, [(5.6 * s_, 29, 1.6), (5.6 * s_, 29, -1.6)], (0, 0, -40 * s_), 3.4, 1.0)
        m.c("body", RB2, (5.6 * s_, 21, 0), (0.4, 11, 6.8))
    band(m, "head", RB2, (0, 31.9, 0), (9.6, 0.8, 9.4))
    m.c("head", RB2, (0, 40.8, 3.9), (7, 0.6, 0.6))
    for s_ in (1, -1):
        m.c("head", RB2, (4.6 * s_, 36, 3.9), (0.6, 9, 0.6))
    # skulls hanging from the belt
    for x in (-4.4, 4.4):
        m.c("hips", BN, (x, 10.4, 4.5), (2, 2, 1.6))
        m.c("hips", "black_concrete", (x - 0.4, 10.6, 5.35), (0.5, 0.5, 0.1))
        m.c("hips", "black_concrete", (x + 0.4, 10.6, 5.35), (0.5, 0.5, 0.1))
    m.attacks = {"minions": "roar", "souls": "cast", "darkness": "cast", "pull": "sweep"}
    m.melee = "swipe"
    return m


@model
def captain_brine():
    """A ghost pirate captain: a big tricorn hat with a skull badge, a red coat with gold buttons and
    cuffs, a peg leg, a hook hand, a cutlass and a green ghostly glow coming off him."""
    m = Model("captain_brine", "biped", 1.7)
    biped(m, hip=14, legx=3.8, neck=33, shoulder=31, armx=10)
    m.bone("jaw", "head", (0, 34.6, 3))
    m.bone("cutlass", "armR", (-10, 13, 2))
    m.hold = {"cutlass": 40}
    m.bend = -34
    CO, CO2, GD, SK, HT, DK, GH = "red_terracotta", "red_concrete", "gold_block", "light_blue_terracotta", "black_concrete", "brown_terracotta", "lime_stained_glass"
    # legs: a boot and a peg leg
    bevel(m, "legL", "black_terracotta", (3.8, 8, 0), (4.6, 10, 4.6), 0.6)
    bevel(m, "legL", HT, (3.8, 2.6, 0.8), (5.2, 5.2, 6.6), 0.6)
    m.c("legL", "brown_wool", (3.8, 5.8, 0), (5.4, 1, 5.4))
    bevel(m, "legR", "black_terracotta", (-3.8, 11, 0), (4.6, 5, 4.6), 0.6)
    m.c("legR", "stripped_oak_log", (-3.8, 5, 0), (2.2, 8, 2.2))
    m.c("legR", "iron_block", (-3.8, 1, 0), (2.6, 2, 2.6))
    # the coat: long tails, gold buttons, a wide belt with a big buckle
    bevel(m, "hips", CO, (0, 12, -0.4), (12.4, 6, 8), 0.6)
    for s in (1, -1):
        m.c("hips", CO, (3.6 * s, 7, -3.6), (4.4, 6, 0.8))
        m.c("hips", GD, (3.6 * s, 4.2, -3.6), (4.6, 0.6, 1))
    bevel(m, "body", CO, (0, 22.4, 0), (12, 13, 7.6), 0.8)
    m.c("body", "white_wool", (0, 26, 3.9), (4, 7, 0.4))
    for k in range(3):
        m.c("body", "white_wool", (0, 28.4 - k * 1.4, 4.2), (3 - k * 0.6, 1, 0.4))
    for y in (25, 22, 19):
        for s in (1, -1):
            m.c("body", GD, (3.6 * s, y, 3.95), (1, 1, 0.3))
    band(m, "body", "brown_terracotta", (0, 16.6, 0), (12.4, 2, 8))
    m.c("body", GD, (0, 16.6, 4.2), (2.6, 2.4, 0.4))
    m.c("body", DK, (0, 16.6, 4.45), (1.2, 1.2, 0.2))
    bevel(m, "body", CO2, (0, 29.2, 0), (13, 2, 8.4), 0.5)
    # arms: gold cuffs, a hook for the left hand
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10 * s
        bevel(m, a, CO, (x + 0.4 * s, 30.4, 0), (5.4, 3.6, 6), 0.6)
        for k in range(3):
            m.c(a, GD, (x + (1 + k) * s, 32.4, -1.6 + k * 1.6), (0.6, 1.6, 0.6))
        bevel(m, a, CO, (x, 24, 0), (4.4, 9, 4.6), 0.6)
        bevel(m, a, CO, (x, 17.4, 0.8), (5, 6, 5), 0.6)
        bevel(m, a, GD, (x, 15.2, 0.8), (5.6, 2, 5.6), 0.4)
    m.c("armR", SK, (-10, 12.6, 1.6), (2.6, 2.6, 2.6))
    limb(m, "armL", "iron_block", (10, 13.6, 1.6), [(3, 0.8, (180, 0, 0)), (2, 0.8, (120, 0, 0)), (1.6, 0.7, (30, 0, 0))])
    # head: a ghostly blue face, a patch, a scraggly beard, the big tricorn hat
    bevel(m, "head", SK, (0, 37.4, 0.4), (8, 8, 8), 0.8)
    paint(m, "head", "front", (0, 38, 4.45), ["KKK.....", "KKK..GG.", ".K...GK.", "........"], {"K": HT, "G": (GH, 0.3, True)}, px=1.0, depth=0.3)
    m.c("head", HT, (0, 39.6, 0.4), (8.6, 0.5, 8.6), (0, 0, -22))
    bevel(m, "jaw", "gray_wool", (0, 34.4, 3.2), (6.6, 3, 3), 0.6)
    for x in (-2, 0, 2):
        m.c("jaw", "gray_wool", (x, 32.2, 4), (1.4, 2.4, 1.2))
    bevel(m, "head", HT, (0, 42.4, 0.4), (14, 1.4, 12), 0.6)
    for s in (1, -1):
        m.c("head", HT, (6.4 * s, 44, 0.4), (1.4, 3.4, 11), (0, 0, 20 * s))
        m.c("head", GD, (7 * s, 45.4, 0.4), (1.6, 0.5, 11.4), (0, 0, 20 * s))
    m.c("head", HT, (0, 44, -5.4), (13, 3.4, 1.4), (-20, 0, 0))
    m.c("head", GD, (0, 45.6, -5.9), (13.4, 0.5, 1.6), (-20, 0, 0))
    bevel(m, "head", HT, (0, 45, 0.4), (9, 4, 9), 0.6)
    paint(m, "head", "front", (0, 45, 4.95), [".WWW.", "WKWKW", ".WWW.", "W.W.W"], {"W": "white_concrete", "K": HT}, px=0.7, depth=0.3)
    m.c("head", "red_wool", (3.6, 47.4, -2), (1, 4, 1), (20, 0, -30))
    # cutlass
    m.c("cutlass", GD, (-10, 14.6, 2), (1.6, 1, 4.6))
    m.c("cutlass", GD, (-10, 13, 4.4), (1.2, 4, 0.8))
    m.c("cutlass", "iron_block", (-10, 22, 2.6), (0.6, 14, 2.4), (6, 0, 0))
    m.c("cutlass", "iron_block", (-10, 29.6, 3.6), (0.6, 3, 2), (24, 0, 0))
    # the ghost glow: green wisps clinging to him
    for (b, x, y, z) in (("body", 6.6, 20, -2), ("body", -6.4, 25, 3), ("hips", 5, 8, 3.6), ("head", -4.8, 36, -2), ("legR", -2, 6, 1.4)):
        m.c(b, GH, (x, y, z), (1.4, 2.6, 1.4), (0, 30, 15), light=True)
    # a bandolier with flintlocks, a gold earring, epaulettes with fringe, a compass on the belt
    m.c("body", "brown_terracotta", (0, 23, 0), (1.6, 18, 8.6), (0, 0, -38))
    for k in range(4):
        m.c("body", DK, (-3 + k * 2, 19.6 + k * 1.6, 4.4), (0.8, 1.2, 0.4))
    m.c("body", "dark_oak_planks", (4.4, 18.6, 4.6), (1, 3.4, 1), (0, 0, 30))
    m.c("body", "iron_block", (5.4, 20.4, 4.6), (0.6, 2.4, 0.6), (0, 0, 30))
    m.c("head", GD, (4.2, 35.6, 0.6), (0.4, 1.4, 0.4))
    for s_, a in ((1, "armL"), (-1, "armR")):
        m.c(a, GD, (10.4 * s_, 32.4, 0), (5.8, 0.6, 6.4))
        for k in range(4):
            m.c(a, GD, (10.4 * s_ + 2.8 * s_, 31.4, -2.2 + k * 1.5), (0.3, 1.6, 0.3))
    m.c("hips", GD, (3.6, 13.4, 4.15), (1.6, 1.6, 0.4), (0, 0, 45))
    m.c("hips", "white_concrete", (3.6, 13.4, 4.4), (0.8, 0.8, 0.2))
    paint(m, "body", "back", (0, 22, -3.85), ["..W..", ".WKW.", "..W..", "W...W", ".W.W."], {"W": "white_concrete", "K": HT}, px=0.9, depth=0.2)
    for (b, x, y, z) in (("cutlass", -10, 17, 2.6), ("head", 4.6, 44, -2), ("body", 0, 30.6, -4.4)):
        m.c(b, GH, (x, y, z), (1, 1.8, 1), (0, 20, 25), light=True)
    m.attacks = {"cannon": "cast", "minions": "roar", "charge": "sweep", "pull": "cast"}
    m.melee = "swipe"
    return m


@model
def keywarden():
    """A clockwork vault guardian: a brass and copper body riveted together, a round glass dome head with a
    glowing gear inside, a giant wind-up key turning in its back, piston arms and a lock-plate shield."""
    m = Model("keywarden", "biped", 1.7)
    biped(m, hip=13, legx=5, neck=33, shoulder=31, armx=11.6)
    m.bone("key", "body", (0, 26, -6))
    m.bend = -24
    BR, BR2, CU, CU2, IR, DK, GL = "gold_block", "raw_gold_block", "copper_block", "cut_copper", "iron_block", "polished_deepslate", "orange_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5 * s
        m.c(b, DK, (x, 9, 0), (2.4, 8, 2.4))
        bevel(m, b, CU, (x, 11, 0), (5.6, 4, 5.6), 0.6)
        bevel(m, b, CU2, (x, 5.6, 0.4), (5, 4, 5), 0.6)
        m.c(b, BR, (x, 8, 2.8), (2, 2, 0.4), (0, 0, 45))
        bevel(m, b, BR2, (x, 1.6, 1.2), (6.4, 3.2, 8), 0.6)
        m.c(b, IR, (x, 1.6, 5.3), (5, 1.2, 0.4))
    bevel(m, "hips", DK, (0, 14.6, 0), (13, 3, 8), 0.6)
    # body: a brass boiler with rivet rows, a pressure gauge and a lock plate in the chest
    bevel(m, "body", BR, (0, 23.4, 0), (15, 13, 10), 1.8)
    for y in (18, 28.6):
        band(m, "body", CU, (0, y, 0), (15.4, 1.4, 10.4), studs=6, stud_block=IR)
    bevel(m, "body", IR, (0, 23.4, 5.2), (6, 6, 1), 0.6)
    paint(m, "body", "front", (0, 23.4, 5.75), [".KKK.", "K...K", "K...K", "..K..", ".KKK."], {"K": DK}, px=0.9, depth=0.3)
    m.c("body", GL, (0, 22.4, 5.9), (0.8, 1.4, 0.3), light=True)
    m.c("body", "white_concrete", (5, 26.6, 5.2), (2.6, 2.6, 0.6))
    m.c("body", "red_concrete", (5.4, 27, 5.55), (0.4, 1.4, 0.2), (0, 0, -40))
    for s in (1, -1):
        m.c("body", CU2, (7.8 * s, 24, 0), (0.6, 8, 8))
        for k in range(3):
            m.c("body", DK, (8.2 * s, 21 + k * 3, 0), (0.4, 0.8, 6))
    # smokestacks on the shoulders
    for s in (1, -1):
        stack(m, "body", DK, 4.6 * s, 30, -3.4, [(2.4, 4, 2.4), (3, 1, 3)])
    # arms: piston upper arms, round shoulder joints, gauntlets
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11.6 * s
        m.c(a, CU, (x, 31, 0), (5, 5, 5), (45, 0, 45))
        m.c(a, DK, (x, 25, 0), (2, 8, 2))
        m.c(a, IR, (x, 26, 0), (3, 4, 3))
        bevel(m, a, BR, (x, 18, 0.8), (6, 7, 6), 0.8)
        band(m, a, CU, (x, 15.4, 0.8), (6.4, 1.2, 6.4), studs=2, stud_block=IR)
        for t in (-1.6, 0, 1.6):
            m.c(a, BR2, (x + t, 13, 2.2), (1.2, 2.6, 1.2))
    # the shield: a round lock plate on the left arm
    m.c("armL", IR, (15.2, 19, 0.8), (1, 9, 9))
    m.c("armL", IR, (15.2, 19, 0.8), (1, 9, 9), (45, 0, 0))
    m.c("armL", BR, (15.8, 19, 0.8), (0.6, 4, 4), (45, 0, 0))
    m.c("armL", DK, (16.15, 19.4, 0.8), (0.3, 1.6, 1))
    m.c("armL", DK, (16.15, 18.2, 0.8), (0.3, 1.6, 0.5))
    # head: a glass dome over a glowing gear, a brass collar and a lamp
    bevel(m, "head", BR, (0, 34.4, 0), (9, 2.4, 9), 0.6)
    m.c("head", "white_stained_glass", (0, 39, 0), (8, 7, 8))
    m.c("head", GL, (0, 39, 0), (3.6, 3.6, 0.8), light=True)
    m.c("head", GL, (0, 39, 0), (3.6, 3.6, 0.8), (0, 0, 45), light=True)
    m.c("head", "yellow_concrete", (0, 39, 0), (1.4, 1.4, 1.2), light=True)
    m.c("head", BR, (0, 42.8, 0), (5, 0.8, 5))
    m.c("head", "redstone_lamp", (0, 44, 0), (1.6, 1.6, 1.6), light=True)
    # the wind-up key in the back
    m.c("key", DK, (0, 26, -7.4), (1.4, 1.4, 4.4))
    for s in (1, -1):
        m.c("key", IR, (3.2 * s, 26, -9.4), (4.4, 5.4, 0.8))
        m.c("key", CU, (3.2 * s, 26, -9.4), (2.4, 3, 1))
        m.c("key", DK, (5.6 * s, 26, -9.4), (0.6, 3.6, 1.1))
    # exposed gears on the hips and back, pipes, rivets, a vault number plate
    for (b, x, y, z, face) in (("hips", 6.6, 14.6, 0, "x"), ("hips", -6.6, 14.6, 0, "x"), ("body", -3.6, 21, -5.2, "z"), ("body", 3.6, 25, -5.2, "z")):
        for r in (0, 45):
            if face == "x":
                m.c(b, CU, (x, y, z), (0.6, 3.2, 3.2), (r, 0, 0))
            else:
                m.c(b, CU, (x, y, z), (3.2, 3.2, 0.6), (0, 0, r))
        m.c(b, DK, (x, y, z), (0.8 if face == "x" else 1.2, 1.2, 1.2 if face == "x" else 0.8))
    for s_ in (1, -1):
        m.c("body", DK, (6.4 * s_, 24, -5.4), (1, 10, 1))
        m.c("body", DK, (6.4 * s_, 29.4, -3.6), (1, 1, 4))
        m.c("body", CU, (6.4 * s_, 19.4, -5.4), (1.4, 1, 1.4))
    paint(m, "body", "front", (0, 29.8, 5.1), ["IIIIIII", "I.K.K.I", "IIIIIII"], {"I": IR, "K": DK}, px=0.8, depth=0.3)
    for s_, b in ((1, "legL"), (-1, "legR")):
        for y in (11, 5.6):
            m.c(b, IR, (5 * s_ + 2.9 * s_, y, 0), (0.3, 0.8, 0.8))
            m.c(b, IR, (5 * s_, y, 2.95), (0.8, 0.8, 0.3))
    for s_, a in ((1, "armL"), (-1, "armR")):
        for k in range(3):
            m.c(a, IR, (11.6 * s_, 21.6 - k * 1.8, 3.9), (0.6, 0.6, 0.3))
        m.c(a, DK, (11.6 * s_ + 3.1 * s_, 18, 0.8), (0.3, 5, 1))
    m.c("head", BR2, (0, 35.8, 4.5), (3, 0.8, 0.4))
    for s_ in (1, -1):
        m.c("head", IR, (4.2 * s_, 39, 0), (0.6, 7, 0.6))
    m.attacks = {"slam": "slam", "steam": "roar", "charge": "sweep", "minions": "cast"}
    m.melee = "swipe"
    return m


@model
def bloodtusk():
    """A hoglin war beast: a massive head with four tusks, a mane of red bristle, a spiked iron saddle with
    a war drum, chain barding and bone trophies, and hooves that split the ground."""
    m = Model("bloodtusk", "quad", 1.6)
    quad(m, body_y=16, legx=7, legz_front=8, legz_back=-9, neck_y=19, neck_z=13)
    HI, HI2, MA, IR, DK, BN = "pink_terracotta", "brown_terracotta", "red_wool", "iron_block", "polished_blackstone", "bone_block"
    for s, (b, z) in ((1, ("legFL", 8)), (-1, ("legFR", 8)), (1, ("legBL", -9)), (-1, ("legBR", -9))):
        quad_leg(m, b, 7 * s, 15, z, 6, HI, HI2, DK)
    # body: heavy hindquarters, a hump under a bristle mane, chain barding
    bevel(m, "body", HI, (0, 18, -1), (15, 11, 22), 2.0)
    bevel(m, "body", HI, (0, 21, 6), (16, 13, 10), 2.4)
    for k, z in enumerate((10, 7, 4, 1, -2, -5)):
        for x in (-2, 0, 2):
            m.c("body", MA if k % 2 == 0 else "red_terracotta", (x, 27.6 - k * 0.6 + (1 if x == 0 else 0), z), (1.4, 3.4, 1.6), (-20, 0, x * 6))
    for s in (1, -1):
        for z in (6, 2, -2, -6, -10):
            m.c("body", "chain", (8 * s, 15.6, z), (0.4, 4, 0.4))
        m.c("body", "chain", (8 * s, 17.6, -2), (0.4, 0.4, 18))
    # saddle with spikes and a war drum
    bevel(m, "body", "brown_terracotta", (0, 24.4, -4), (11, 2, 9), 0.6)
    for s in (1, -1):
        m.c("body", IR, (5.6 * s, 23.4, -4), (1, 4, 9))
        spikes(m, "body", IR, [(6 * s, 24.6, -7), (6 * s, 24.6, -1)], (0, 0, -60 * s), 2.6, 0.9)
    m.c("body", "red_terracotta", (0, 27, -8.6), (5, 5, 5))
    m.c("body", "white_wool", (0, 29.6, -8.6), (5.2, 0.4, 5.2))
    m.c("body", "white_wool", (0, 24.4, -8.6), (5.2, 0.4, 5.2))
    for k in range(4):
        m.c("body", "gold_block", (-2.6 + (k % 2) * 5.2, 27, -8.6 + (k // 2 - 0.5) * 5.2), (0.4, 5, 0.4))
    for (x, y, z) in ((-7.8, 20, 10), (7.8, 20, 10), (-7.6, 20, -12)):
        m.c("body", BN, (x, y, z), (1.4, 3, 1.4), (0, 0, 20))
        m.c("body", "calcite", (x, y - 2, z), (2, 1.6, 2))
    # tail
    limb(m, "tail", HI, (0, 20, -12), [(3, 1.6, (-140, 0, 0)), (2.4, 1.2, (-170, 0, 0))])
    m.c("tail", MA, (0, 15.4, -14.6), (2, 2, 2))
    # head: huge, flat snout, four tusks, a scarred brow, small furious eyes
    bevel(m, "head", HI, (0, 18, 18.6), (12, 10, 10), 1.8)
    bevel(m, "head", HI2, (0, 16, 24.6), (8, 5, 3), 0.8)
    paint(m, "head", "front", (0, 16, 26.15), ["KK.KK"], {"K": "black_concrete"}, px=0.9, depth=0.3)
    paint(m, "head", "front", (0, 21.6, 23.65), ["BBB...BBB", ".BRB.BRB."], {"B": HI2, "R": ("red_concrete", 0.3, True)}, px=1.0, depth=0.4)
    for s in (1, -1):
        horn(m, "head", BN, (4.6 * s, 14.4, 23), 3, (60, 0, -30 * s), (-28, 0, 0), 1.8, 0.8)
        horn(m, "head", "calcite", (2.6 * s, 14, 24), 2, (40, 0, -10 * s), (-30, 0, 0), 1.2, 0.8)
        m.c("head", HI, (6.4 * s, 22, 15.6), (2, 4, 1.6), (0, 0, -40 * s))
    bevel(m, "head", IR, (0, 23.6, 18), (10, 1.6, 8), 0.4)
    m.c("jaw", HI2, (0, 13, 20.6), (9, 2, 7))
    # war paint on the flanks, iron rings through the ears, a bone-studded brow plate
    for s_ in (1, -1):
        paint(m, "body", "left" if s_ > 0 else "right", (8.05 * s_, 19, 0), ["W..W..W", ".W..W..", "W..W..W"], {"W": "white_concrete"}, px=1.4, depth=0.2)
        m.c("head", "iron_block", (7.4 * s_, 20.6, 15.4), (0.4, 1.4, 1.4))
    for x in (-3, 0, 3):
        m.c("head", BN, (x, 24.8, 21.6), (1, 1.6, 1), (20, 0, 0))
    for k in range(3):
        m.c("head", MA, (-2 + k * 2, 23.4, 14), (1.2, 3, 1.2), (-30, 0, 0))
    m.attacks = {"charge": "charge", "toss": "toss", "quake": "rear", "roar": "howl"}
    m.melee = "bite"
    return m


def slime(m):
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 14, 0))
    m.bone("mouth", "body", (0, 10, 14))


@model
def king_gloop():
    m = Model("king_gloop", "slime", 2.0)
    slime(m)
    shell = "slime_block"
    # A rounded jelly: a core box, slabs pushed out on every side and bevelled corners, so it reads as
    # a soft blob instead of a cube. It sags at the bottom like something heavy.
    m.c("body", shell, (0, 13.5, 0), (26, 25, 26))
    m.c("body", shell, (0, 12, 0), (30, 19, 24))
    m.c("body", shell, (0, 12, 0), (24, 19, 30))
    m.c("body", shell, (0, 27, 0), (18, 2, 18))
    m.c("body", shell, (0, 1, 0), (30, 2, 30))
    for x, z in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        m.c("body", shell, (12 * x, 13, 12 * z), (6, 21, 6), (0, 45, 0))
        m.c("body", "lime_stained_glass", (13.6 * x, 0.6, 13.6 * z), (5, 1.2, 5), (0, 45, 0))
    # drips running down the sides
    for x, z, h in ((-9, 15.2, 5), (4, 15.2, 3.4), (15.2, 6, 4), (-15.2, -3, 6), (8, -15.2, 4.4)):
        m.c("body", "lime_stained_glass", (x, 4 + h / 2, z), (1.6, h, 1.6))
        m.c("body", "lime_stained_glass", (x, 3.6, z), (2.2, 1.6, 2.2))
    # the core: a darker heart of jelly
    m.c("inner", "lime_concrete", (0, 14, 0), (11, 11, 11))
    m.c("inner", "green_concrete", (0, 14, 0), (7, 7, 11.4))
    m.c("inner", "green_concrete", (0, 14, 0), (11.4, 7, 7))
    # only one thing it swallowed is still in there: the old king's sword, standing in the core
    m.c("inner", "iron_block", (7, 21, -6), (1, 10, 1.4), (35, 0, 25))
    m.c("inner", "gold_block", (4.6, 16.6, -5.2), (3.4, 0.8, 1), (35, 0, 25))
    m.c("inner", "brown_wool", (3.6, 15.4, -4.8), (0.9, 2.6, 0.9), (35, 0, 25))
    # face: big glossy eyes with highlights, angry brows, cheeks, a wide mouth with a tongue
    m.m("body", "black_concrete", (6, 17.6, 15.1), (5, 6, 0.4))
    m.m("body", "white_concrete", (7, 19.4, 15.35), (1.8, 1.8, 0.2))
    m.m("body", "white_concrete", (5, 16.2, 15.35), (0.8, 0.8, 0.2))
    m.m("body", "green_concrete", (6, 21.8, 15.4), (6, 1.4, 0.6), (0, 0, 14))
    m.m("body", "pink_concrete", (10.4, 13.4, 15.2), (2.4, 1.2, 0.3))
    m.c("mouth", "black_concrete", (0, 9.4, 15.1), (11, 3.4, 0.4))
    m.c("mouth", "red_concrete", (0, 8.4, 15.25), (5, 1.2, 0.3))
    for x in (-4.2, -2.4, 2.4, 4.2):
        m.c("mouth", "white_concrete", (x, 10.6, 15.3), (1, 1, 0.3))
    # crown: ermine band, gold band, eight points with pearls, a velvet top and an orb
    m.c("body", "white_wool", (0, 26.6, 0), (17.6, 1.8, 17.6))
    for x, z in ((-6, 8.85), (0, 8.85), (6, 8.85), (8.85, -4), (8.85, 4), (-8.85, 0)):
        m.c("body", "black_wool", (x, 26.6, z), (0.6, 0.8, 0.2) if abs(z) > 8 else (0.2, 0.8, 0.6))
    m.c("body", "gold_block", (0, 28.6, 0), (16, 2.4, 16))
    m.c("body", "red_wool", (0, 30.6, 0), (13, 2, 13))
    m.c("body", "red_wool", (0, 32.2, 0), (9, 1.4, 9))
    for k, (x, z) in enumerate(((-7, 7), (0, 7.6), (7, 7), (7.6, 0), (7, -7), (0, -7.6), (-7, -7), (-7.6, 0))):
        h = 5 if k % 2 else 3.6
        m.c("body", "gold_block", (x, 29.8 + h / 2, z), (2, h, 2), (0, 45, 0))
        m.c("body", "white_concrete", (x, 30.2 + h, z), (1, 1, 1), (45, 45, 0))
    for x, z, k in ((0, 8.1, "redstone_block"), (8.1, 0, "emerald_block"), (-8.1, 0, "lapis_block"), (0, -8.1, "diamond_block")):
        m.c("body", k, (x, 28.6, z), (2, 2, 0.4) if abs(z) > 1 else (0.4, 2, 2), light=True)
    m.c("body", "gold_block", (0, 34, 0), (2.4, 2.4, 2.4), (45, 0, 45))
    m.c("body", "gold_block", (0, 36, 0), (0.7, 2.4, 0.7))
    m.c("body", "gold_block", (0, 36.4, 0), (2, 0.7, 0.7))
    # royal cape pinned with a gold clasp, ermine trim, a hem that rests on the ground
    m.c("body", "red_wool", (0, 13, -15.4), (24, 22, 0.8))
    m.c("body", "red_wool", (0, 2, -16.4), (24, 2, 2.4))
    m.c("body", "white_wool", (0, 24.6, -15.6), (25, 2.6, 1.4))
    for x in (-8, -4, 0, 4, 8):
        m.c("body", "black_wool", (x, 24.6, -16.35), (0.8, 1.2, 0.2))
    m.c("body", "white_wool", (0, 3.4, -15.6), (25, 1.6, 1.2))
    m.m("body", "gold_block", (12, 23.8, -14), (2.6, 2.6, 1.6), (0, 0, 45))
    # a sceptre stuck in its side
    m.c("body", "gold_block", (16, 18, 4), (1.4, 16, 1.4), (0, 0, -25))
    for y in (14, 18.4):
        m.c("body", "gold_block", (16 + (y - 18) * -0.47, y, 4), (2.2, 0.7, 2.2), (0, 0, -25))
    m.c("body", "emerald_block", (19.6, 25.8, 4), (3, 3, 3), (45, 0, 20), light=True)
    m.c("body", "gold_block", (19.6, 25.8, 4), (3.6, 0.6, 3.6), (0, 0, -25))
    # baby slimes clinging to its sides, each with its own little face
    for (x, y, z, r) in ((15.6, 6, 6, 20), (-15.6, 9, -6, -30), (9, 4, -15.6, 60)):
        m.c("body", "slime_block", (x, y, z), (5, 4.4, 5), (0, r, 0))
        m.c("body", "lime_concrete", (x, y, z), (2.6, 2.4, 2.6), (0, r, 0))
        fx, fz = math.sin(math.radians(r)) * 2.55, math.cos(math.radians(r)) * 2.55
        for d in (-1, 1):
            m.c("body", "black_concrete", (x + fx + d * 0.9 * math.cos(math.radians(r)), y + 0.6, z + fz - d * 0.9 * math.sin(math.radians(r))), (0.7, 1, 0.2), (0, r, 0))
    # arrows that bounced into the jelly and stuck
    for (x, y, z, rx, rz) in ((-6, 22, 15.4, 70, 10), (10, 17, 15.4, 75, -20), (-15.4, 16, 6, 10, 80)):
        m.c("body", "oak_planks", (x, y, z), (0.5, 6, 0.5), (rx, 0, rz), (x, y, z))
        m.c("body", "white_wool", (x - (rz / 90) * 2.6 if abs(rz) > 45 else x, y + (0 if abs(rz) > 45 else 1.2), z + (2.6 if abs(rz) < 45 else 0)), (1.4, 0.4, 1.4), (rx, 0, rz))
    # more things it swallowed: a fish, a boot, a key, air bubbles
    m.c("inner", "orange_terracotta", (6, 10, 5), (4.4, 2.2, 1.2), (0, 0, 20))
    m.c("inner", "orange_terracotta", (3.2, 9, 5), (1.6, 2.6, 1), (0, 0, 20))
    m.c("inner", "black_concrete", (7.4, 10.8, 5.65), (0.5, 0.5, 0.2))
    m.c("inner", "brown_terracotta", (-8, 13, 3), (2.6, 4, 2.6), (0, 0, -15))
    m.c("inner", "brown_terracotta", (-9.2, 11.4, 4.6), (2.6, 1.6, 3), (0, 0, -15))
    m.c("inner", "gold_block", (2, 4, 7), (0.6, 4, 0.6), (0, 0, 70))
    m.c("inner", "gold_block", (4, 4.6, 7), (1.6, 1.6, 0.6), (0, 0, 70))
    for (x, y, z, w) in ((-2, 20, 9, 1.2), (9, 22, 2, 1), (-10, 8, -8, 1.4), (4, 12, -10, 1), (-6, 16, 10, 0.8), (0, 6, 11, 1)):
        m.c("inner", "white_stained_glass", (x, y, z), (w, w, w))
    # the crown's velvet gets ermine spots, the clasps get rubies
    for (x, z) in ((-4, 6.6), (4, 6.6), (0, -6.6), (6.6, 0), (-6.6, 0)):
        m.c("body", "white_wool", (x, 31.2, z), (1, 0.8, 0.3) if abs(z) > 1 else (0.3, 0.8, 1))
    m.c("body", "redstone_block", (12.2, 23.8, -13.2), (1, 1, 0.4), light=True)
    # glints on the jelly so it reads wet and shiny
    for (x, y, z, w, h) in ((-9, 23, 15.2, 3.4, 0.8), (-10.6, 21, 15.2, 0.8, 2.4), (15.2, 20, -6, 0.8, 2), (11, 25, -12, 2.6, 0.6)):
        m.c("body", "white_stained_glass", (x, y, z), (w, h, 0.3) if abs(z) > 14 else (0.3, h, w))
    m.attacks = {"leap": "slam", "quake": "hop", "minions": "burst", "poison": "spit"}
    m.melee = "hop"
    m.spawn = {"style": "drop", "particle": "ITEM_SLIME", "sound": "ENTITY_SLIME_SQUISH"}
    m.death = {"style": "splat", "swap": "", "particle": "ITEM_SLIME", "sound": "ENTITY_SLIME_DEATH"}
    return m
