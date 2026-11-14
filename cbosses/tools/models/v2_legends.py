"""The legends and the finale: The Listener (the warden of the deep dark), the Withered Tyrant (three
skulls on a burning spine), the Ender Wyrm (a dragon), the Gale Sovereign (a breeze grown huge in a trial
chamber) and The Unmaker, the four-armed titan that wakes when the others are beaten. Each has its own rig
so its attacks are its own."""
import copy, math
import anims
from anims import K, Z
from models import model, biped, horn, mhorn, limb, mlimb, taper, quad, dirof
from build import Model
from kit import paint, crack, band, hem, tufts, spikes, plate, stack, mirror_rows, bevel
from v2_general import quad_leg

SPAWN, DEATH = {}, {}

# ================================================================================================ TITAN RIG

TITAN = copy.deepcopy(anims.FLOAT)
TITAN["idle"] = {"length": 4.0, "loop": True, "bones": {
    "core": {"pos": K((0, Z), (2.0, (0, 2.4, 0)), (4.0, Z)), "rot": K((0, (-2, 0, 0)), (2.0, (2, 0, 0)), (4.0, (-2, 0, 0)))},
    "chest": {"scl": K((0, (1, 1, 1)), (1.0, (1.03, 1.02, 1.04)), (2.0, (1, 1, 1)), (3.0, (1.03, 1.02, 1.04)), (4.0, (1, 1, 1)))},
    "heart": {"rot": K((0, Z), (2.0, (180, 90, 0)), (4.0, (360, 180, 0))), "scl": K((0, (1, 1, 1)), (0.25, (1.18, 1.18, 1.18)), (0.6, (1, 1, 1)), (2.0, (1, 1, 1)), (2.25, (1.18, 1.18, 1.18)), (2.6, (1, 1, 1)), (4.0, (1, 1, 1)))},
    "head": {"rot": K((0, (4, -10, 0)), (2.0, (-2, 10, 0)), (4.0, (4, -10, 0)))},
    "halo": {"rot": K((0, Z), (2.0, (0, 180, 0)), (4.0, (0, 360, 0))), "pos": K((0, Z), (1.0, (0, 0.8, 0)), (3.0, (0, -0.8, 0)), (4.0, Z))},
    "armL": {"rot": K((0, (8, 0, -14)), (2.0, (-4, 0, -20)), (4.0, (8, 0, -14)))},
    "armR": {"rot": K((0, (-4, 0, 20)), (2.0, (8, 0, 14)), (4.0, (-4, 0, 20)))},
    "arm2L": {"rot": K((0, (-20, 10, -24)), (2.0, (-12, 0, -30)), (4.0, (-20, 10, -24)))},
    "arm2R": {"rot": K((0, (-12, 0, 30)), (2.0, (-20, -10, 24)), (4.0, (-12, 0, 30)))},
    "finL": {"rot": K((0, (0, 12, 0)), (2.0, (0, 22, 6)), (4.0, (0, 12, 0)))},
    "finR": {"rot": K((0, (0, -12, 0)), (2.0, (0, -22, -6)), (4.0, (0, -12, 0)))},
    "tail": {"rot": K((0, (6, 0, 4)), (2.0, (12, 0, -4)), (4.0, (6, 0, 4)))},
    "ring1": {"rot": K((0, Z), (2.0, (0, 180, 0)), (4.0, (0, 360, 0)))},
    "ring2": {"rot": K((0, Z), (2.0, (0, -180, 0)), (4.0, (0, -360, 0)))},
    "ring3": {"rot": K((0, Z), (2.0, (0, 120, 0)), (4.0, (0, 240, 0)))},
}}
TITAN["walk"] = {"length": 3.0, "loop": True, "bones": {
    "core": {"rot": K((0, (10, 0, 0)), (1.5, (12, 0, 0)), (3.0, (10, 0, 0)))},
    "tail": {"rot": K((0, (24, 0, 6)), (1.5, (30, 0, -6)), (3.0, (24, 0, 6)))},
    "halo": {"rot": K((0, Z), (3.0, (0, 360, 0)))},
    "ring1": {"rot": K((0, Z), (1.5, (0, 180, 0)), (3.0, (0, 360, 0)))},
    "ring2": {"rot": K((0, Z), (1.5, (0, -180, 0)), (3.0, (0, -360, 0)))},
    "ring3": {"rot": K((0, Z), (1.5, (0, 180, 0)), (3.0, (0, 360, 0)))},
}}
# both great fists rise over the head and come down together
TITAN["smash"] = {"length": 1.8, "hit": 1.05, "bones": {
    "armL": {"rot": K((0, Z), (0.7, (-170, 0, -10)), (0.95, (-175, 0, -6)), (1.1, (-30, 0, -4)), (1.4, (-26, 0, -4)), (1.8, Z))},
    "armR": {"rot": K((0, Z), (0.7, (-170, 0, 10)), (0.95, (-175, 0, 6)), (1.1, (-30, 0, 4)), (1.4, (-26, 0, 4)), (1.8, Z))},
    "foreL": {"rot": K((0, Z), (0.7, (-40, 0, 0)), (1.1, (0, 0, 0)), (1.8, Z))},
    "foreR": {"rot": K((0, Z), (0.7, (-40, 0, 0)), (1.1, (0, 0, 0)), (1.8, Z))},
    "core": {"rot": K((0, Z), (0.7, (-16, 0, 0)), (1.1, (24, 0, 0)), (1.4, (22, 0, 0)), (1.8, Z)), "pos": K((0, Z), (0.7, (0, 6, 0)), (1.1, (0, -5, 4)), (1.8, Z))},
    "head": {"rot": K((0, Z), (0.7, (-20, 0, 0)), (1.1, (10, 0, 0)), (1.8, Z))},
    "arm2L": {"rot": K((0, Z), (0.7, (10, 0, -50)), (1.1, (-10, 0, -20)), (1.8, Z))},
    "arm2R": {"rot": K((0, Z), (0.7, (10, 0, 50)), (1.1, (-10, 0, 20)), (1.8, Z))},
}}
# the lower left arm sweeps the void blade in a wide arc, the body twists into it
TITAN["sweep"] = {"length": 1.3, "hit": 0.7, "bones": {
    "arm2L": {"rot": K((0, Z), (0.45, (-80, -70, -40)), (0.7, (-70, 80, -10)), (0.9, (-60, 90, -10)), (1.3, Z))},
    "core": {"rot": K((0, Z), (0.45, (0, 35, 0)), (0.7, (0, -40, 0)), (1.3, Z))},
    "halo": {"rot": K((0, Z), (0.7, (0, -180, 0)), (1.3, (0, -360, 0)))},
    "armL": {"rot": K((0, Z), (0.45, (-30, 0, -40)), (0.7, (10, 0, -20)), (1.3, Z))},
}}
# raises the orb in the lower right hand, the heart flares, the eye glares
TITAN["cast"] = {"length": 1.6, "hit": 0.95, "bones": {
    "arm2R": {"rot": K((0, Z), (0.6, (-150, 0, 20)), (1.2, (-150, 0, 20)), (1.6, Z))},
    "heart": {"scl": K((0, (1, 1, 1)), (0.6, (0.7, 0.7, 0.7)), (0.95, (1.6, 1.6, 1.6)), (1.3, (1, 1, 1)), (1.6, (1, 1, 1)))},
    "chest": {"rot": K((0, Z), (0.6, (-12, 0, 0)), (0.95, (6, 0, 0)), (1.6, Z))},
    "head": {"rot": K((0, Z), (0.6, (-24, 0, 0)), (0.95, (8, 0, 0)), (1.6, Z))},
    "halo": {"scl": K((0, (1, 1, 1)), (0.6, (0.7, 1, 0.7)), (0.95, (1.5, 1, 1.5)), (1.6, (1, 1, 1)))},
    "armL": {"rot": K((0, Z), (0.6, (-20, 0, -50)), (1.6, Z))}, "armR": {"rot": K((0, Z), (0.6, (-20, 0, 50)), (1.6, Z))},
}}
# throws all four arms wide and the shards of the crown fly out, then snap back
TITAN["roar"] = {"length": 2.0, "hit": 0.9, "bones": {
    "armL": {"rot": K((0, Z), (0.6, (-40, 0, -80)), (1.6, (-40, 0, -78)), (2.0, Z))},
    "armR": {"rot": K((0, Z), (0.6, (-40, 0, 80)), (1.6, (-40, 0, 78)), (2.0, Z))},
    "arm2L": {"rot": K((0, Z), (0.6, (20, 0, -70)), (1.6, (20, 0, -68)), (2.0, Z))},
    "arm2R": {"rot": K((0, Z), (0.6, (20, 0, 70)), (1.6, (20, 0, 68)), (2.0, Z))},
    "head": {"rot": K((0, Z), (0.6, (-30, 0, 0)), (1.0, (-30, 8, 0)), (1.4, (-30, -8, 0)), (2.0, Z))},
    "jaw": {"rot": K((0, Z), (0.6, (40, 0, 0)), (1.6, (38, 0, 0)), (2.0, Z))},
    "halo": {"scl": K((0, (1, 1, 1)), (0.6, (1.8, 1.2, 1.8)), (1.6, (1.8, 1.2, 1.8)), (2.0, (1, 1, 1)))},
    "finL": {"rot": K((0, Z), (0.6, (0, 40, 20)), (1.6, (0, 40, 20)), (2.0, Z))},
    "finR": {"rot": K((0, Z), (0.6, (0, -40, -20)), (1.6, (0, -40, -20)), (2.0, Z))},
    "core": {"rot": K((0, Z), (0.6, (-14, 0, 0)), (1.6, (-12, 0, 0)), (2.0, Z))},
}}
TITAN["swipe"] = {"length": 0.8, "hit": 0.4, "bones": {
    "armR": {"rot": K((0, Z), (0.25, (-120, 0, 40)), (0.4, (20, 0, -10)), (0.8, Z))},
    "foreR": {"rot": K((0, Z), (0.25, (-50, 0, 0)), (0.4, (0, 0, 0)), (0.8, Z))},
    "core": {"rot": K((0, Z), (0.25, (0, -22, 0)), (0.4, (0, 28, 0)), (0.8, Z))},
}}
TITAN["hurt"] = {"length": 0.35, "bones": {"core": {"rot": K((0, Z), (0.1, (-8, 0, 0)), (0.35, Z))}, "head": {"rot": K((0, Z), (0.1, (-14, 0, 0)), (0.35, Z))}}}
TITAN["die_drop"] = {"length": 2.2, "bones": {
    "root": {"pos": K((0, Z), (0.5, (0, 6, 0)), (1.8, (0, -14, 0)), (2.2, (0, -13, 0)))},
    "core": {"rot": K((0, Z), (0.5, (-20, 0, 0)), (1.8, (35, 0, 12)))},
    "head": {"rot": K((0, Z), (0.5, (-40, 0, 0)), (1.8, (40, 0, 10)))},
    "armL": {"rot": K((0, Z), (1.6, (50, 0, 40)))}, "armR": {"rot": K((0, Z), (1.6, (50, 0, -40)))},
    "arm2L": {"rot": K((0, Z), (1.6, (60, 0, 20)))}, "arm2R": {"rot": K((0, Z), (1.6, (60, 0, -20)))},
    "halo": {"pos": K((0, Z), (1.8, (0, -8, 0)))}, "ring1": {"pos": K((0, Z), (1.6, (0, -8, 0)))},
    "ring2": {"pos": K((0, Z), (1.6, (0, -14, 0)))}, "ring3": {"pos": K((0, Z), (1.6, (0, -20, 0)))}}}
anims.RIGS["titan"] = TITAN
anims.MELEE["titan"] = "swipe"

# ================================================================================================ THE LISTENER

@model
def the_listener():
    """The warden of the deep dark grown into a legend: a towering dark-teal brute with no eyes, a wide
    jaw full of bone teeth, two great sensor horns that glow at the tips, an open ribcage where souls burn
    in a pulsing heart, sculk spreading over its shoulders and back, and long arms ending in clawed fists
    laced with glowing veins. It finds you by sound."""
    m = Model("the_listener", "biped", 2.2)
    biped(m, hip=16, legx=5.6, neck=40, shoulder=36, armx=13)
    m.bone("jaw", "head", (0, 41, 4))
    m.bone("heart", "body", (0, 30, 3))
    m.bend = -26
    m.rest("body", (-10, 0, 0))
    m.rest("head", (10, 0, 0))
    HI, HI2, DK, SC, BN, GL, GL2 = "warped_wart_block", "sculk", "black_concrete", "sculk", "calcite", "cyan_concrete", "light_blue_concrete"
    # legs: thick thighs, lean shins, wide feet with bone claws, a glowing vein down each
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5.6 * s
        bevel(m, b, HI, (x, 12, 0), (7, 9, 7), 1)
        bevel(m, b, HI2, (x, 5.4, -0.6), (5.8, 7, 5.8), 0.8)
        bevel(m, b, DK, (x, 1.3, 1.4), (8, 2.6, 9), 0.6)
        for t in (-2.4, 0, 2.4):
            m.c(b, BN, (x + t, 1, 6.6), (1.2, 1.2, 2.2), (-10, 0, 0))
        m.c(b, GL, (x + 3.55 * s, 11, 0), (0.3, 7, 0.8), light=True)
        m.c(b, SC, (x, 15.6, 0), (7.4, 1.4, 7.4))
    # waist and hips
    bevel(m, "hips", DK, (0, 16.6, 0), (12, 4, 8), 0.8)
    bevel(m, "body", HI, (0, 21.6, 0), (11, 6, 7.6), 1)
    # the chest: broad, open at the front into a ribcage with a soul heart inside
    bevel(m, "body", HI, (0, 30.6, 0), (18, 12, 11), 1.6)
    m.c("body", DK, (0, 30.4, 5.2), (11, 9, 1))
    m.c("body", GL, (0, 30.4, 5), (8, 6.4, 0.4), light=True)
    for k, y in enumerate((26.6, 28.8, 31, 33.2)):
        w = 12.6 - abs(k - 1.5) * 0.8
        m.c("body", BN, (0, y, 5.9), (w, 1, 1))
    m.c("body", BN, (0, 30.2, 6.1), (1.6, 9, 0.8))
    bevel(m, "heart", GL2, (0, 30.4, 3.4), (3.4, 3.4, 3.4), 0.6, light=True)
    m.c("heart", "soul_lantern", (0, 30.4, 3.4), (2, 2, 2), light=True)
    for s in (1, -1):
        m.c("body", GL, (8.95 * s, 30, 2), (0.3, 7, 0.8), light=True)
        m.c("body", GL, (8.95 * s, 27, -1.4), (0.3, 0.8, 3), light=True)
    # shoulders: lumps of sculk over the collar, the back spined with sculk growths tipped in light
    for s in (1, -1):
        bevel(m, "body", SC, (8.4 * s, 36.4, 0), (7, 4.6, 9), 1)
    bevel(m, "body", SC, (0, 33, -5), (14, 10, 2), 0.8)
    for k, (x, y, h) in enumerate(((0, 37, 5), (-4, 34, 4), (4, 34.6, 4.4), (-2, 29, 3.4), (2.4, 28, 3), (0, 24.4, 2.6))):
        m.c("body", DK, (x, y, -6.6), (1.6, h, 1.6), (-45, 0, x * 3))
        m.c("body", GL, (x, y + h * 0.4, -6.6 - h * 0.45), (0.8, 0.8, 0.8), light=True)
    # arms: long and heavy, veins of light down the forearms, fists with bone claws
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 13 * s
        bevel(m, a, HI, (x, 30.4, 0), (6.4, 10, 6.6), 1)
        bevel(m, a, HI, (x, 19.4, 0.6), (7.6, 11, 7.6), 1.2)
        m.c(a, HI2, (x, 23, 4.4), (5, 4, 0.4))
        for t in (-1.6, 1.6):
            m.c(a, GL, (x + t, 19.4, 4.45), (0.4, 9, 0.3), light=True)
        m.c(a, GL, (x + 3.85 * s, 18, 0.6), (0.3, 6, 0.6), light=True)
        bevel(m, a, DK, (x, 11.4, 1.2), (8, 5.4, 8), 1)
        for t in (-2.4, 0, 2.4):
            m.c(a, BN, (x + t, 7.4, 3), (1.3, 4, 1.3), (20, 0, 0))
        m.c(a, SC, (x, 35.4, 0), (6.8, 1.6, 7))
    # the head: wide and flat, eyeless, a huge jaw, sensor horns that glow at the tips
    bevel(m, "head", HI, (0, 45, 1), (13, 8, 11), 1.6)
    m.c("head", HI2, (0, 47.6, 6.6), (9, 2, 0.4))
    m.c("head", DK, (0, 43.4, 6.6), (11, 2, 0.4))
    paint(m, "head", "front", (0, 42.2, 6.7), ["W.W.W.W.W"], {"W": BN}, px=1.2, depth=0.6)
    bevel(m, "jaw", HI, (0, 39.4, 2.6), (12, 3, 8.6), 0.8)
    m.c("jaw", "red_terracotta", (0, 40.9, 3), (9, 0.4, 6))
    paint(m, "jaw", "front", (0, 41.2, 7.0), ["W.W.W.W"], {"W": BN}, px=1.4, depth=0.6)
    m.c("jaw", GL, (0, 38.2, 6.95), (6, 0.4, 0.2), light=True)
    for side in (1, -1):
        tip = limb(m, "head", HI2, (5 * side, 48, -1), [(6, 2.4, (-18, 0, -28 * side)), (6, 2, (-38, 0, -12 * side)), (5, 1.6, (-62, 0, 8 * side))], joint=SC)
        bevel(m, "head", GL2, tip, (2.6, 2.6, 2.6), 0.5, light=True)
        tip2 = limb(m, "head", HI2, (3 * side, 48.6, 3), [(4, 1.6, (-6, 0, -16 * side)), (3.4, 1.2, (-26, 0, -6 * side))])
        m.c("head", GL, tip2, (1.6, 1.6, 1.6), light=True)
    for (x, z) in ((-3, 4), (3.4, 2), (0, -2)):
        m.c("head", SC, (x, 49.2, z), (3.4, 0.8, 3.4))
    m.attacks = {"sonic": "cast", "slam": "slam", "darkness": "roar", "quake": "stomp"}
    m.melee = "swipe"
    return m


# ================================================================================================ THE WITHERED TYRANT

def skull(m, bone, c, w, base, dark, glow, teeth):
    """A skull: a rounded head, two deep sockets with a light in each, a nose hole and a row of teeth."""
    x, y, z = c
    bevel(m, bone, base, c, (w, w * 0.9, w * 0.92), w * 0.12)
    f = z + w * 0.46
    for s in (1, -1):
        m.c(bone, dark, (x + w * 0.22 * s, y + w * 0.08, f + 0.05), (w * 0.28, w * 0.24, 0.3))
        m.c(bone, glow, (x + w * 0.22 * s, y + w * 0.08, f + 0.15), (w * 0.12, w * 0.1, 0.2), light=True)
    m.c(bone, dark, (x, y - w * 0.14, f + 0.05), (w * 0.12, w * 0.12, 0.3))
    m.c(bone, dark, (x, y - w * 0.3, f + 0.05), (w * 0.6, w * 0.14, 0.3))
    for k in range(4):
        m.c(bone, teeth, (x - w * 0.22 + k * w * 0.147, y - w * 0.3, f + 0.2), (w * 0.08, w * 0.12, 0.2))


@model
def withered_tyrant():
    """The Wither grown into a tyrant: three skulls on a bar of blackstone set with bone spikes, the middle
    one crowned in netherite and soul gems, a ribcage of dark bone with soul fire burning inside, a long
    spine that curls into a tail of flame, tattered black banners hanging from the bar and wither skulls
    circling it like moons."""
    m = Model("withered_tyrant", "float", 2.0)
    m.bone("core", "root", (0, 16, 0))
    m.bone("head", "core", (0, 38, 0))
    m.mbone("armL", "core", (12, 37, 0))
    m.bone("ring1", "core", (0, 28, 0))
    m.bone("ring2", "head", (0, 50, 0))
    m.bone("ring3", "core", (0, 8, 0))
    m.no_elbows = True
    SK, SK2, DK, BS, NE, SO, SO2 = "gray_concrete", "light_gray_concrete", "black_concrete", "polished_blackstone", "netherite_block", "light_blue_concrete", "soul_lantern"
    # the bar across the shoulders, spiked with bone, banners hanging from it
    bevel(m, "core", BS, (0, 36, 0), (30, 4, 6), 1)
    m.c("core", "chiseled_polished_blackstone", (0, 36, 3.05), (6, 3, 0.2))
    for x in (-12, -6, 6, 12):
        m.c("core", SK, (x, 38.6, -2), (1.2, 3.6, 1.2), (-20, 0, x * 1.2))
    for x, h in ((-10, 12), (-4, 15), (4, 14), (10, 11)):
        m.c("core", DK if x % 4 else "black_wool", (x, 34 - h / 2, -3.4), (5, h, 0.4))
        hem(m, "core", "black_wool", x - 2.5, x + 2.5, 34 - h, -3.4, 0.4, 3, long=2.6, short=1, seed=int(x))
    m.c("core", "purple_concrete", (-4, 30, -3.65), (1.4, 6, 0.2))
    m.c("core", "purple_concrete", (4, 30.6, -3.65), (1.4, 5, 0.2))
    # the ribcage: a spine, dark ribs curving round a fire of souls
    m.c("core", SK, (0, 26, -1.6), (3, 18, 3))
    for k, y in enumerate((31, 28, 25, 22)):
        w = 13 - k * 1.6
        for s in (1, -1):
            m.c("core", SK, (w / 2 * s, y, 0.6), (1.4, 1.4, 6))
            m.c("core", SK, (w / 2 * s - 1.2 * s, y, 3.8), (2.4, 1.4, 1.4), (0, 30 * s, 0))
        m.c("core", SK2, (0, y, 4.4), (2, 1.4, 1.4))
    for k, (dx, dz, h, r) in enumerate(((0, 0.8, 7, 0), (-1.8, 1.4, 4.4, 20), (1.8, 0.4, 5, -15), (0, 2.2, 3.4, 45))):
        m.c("core", SO if k else "white_concrete", (dx, 23 + h / 2, dz), (2.2 - k * 0.2, h, 2.2 - k * 0.2), (0, r, dx * 4), light=True)
    m.c("core", SO2, (0, 25, 0.8), (2.4, 2.4, 2.4), light=True)
    # the tail: vertebrae tapering down and curling back, ending in soul flame
    tip = limb(m, "core", SK, (0, 17, -1.6), [(4, 2.6, (180, 0, 0)), (4, 2.2, (200, 0, 0)), (4, 1.8, (225, 0, 0)), (3.4, 1.4, (255, 0, 0)), (3, 1.1, (280, 0, 0))], joint=DK)
    for k, r in enumerate((0, 45, 90)):
        m.c("core", SO if k != 1 else "white_concrete", (tip[0], tip[1] + 1, tip[2] - 1), (1.6, 3 - k * 0.6, 1.6), (0, r, 20), light=True)
    # the three skulls: side ones smaller, the middle one crowned
    skull(m, "head", (0, 43.4, 0.6), 12, SK, DK, SO, SK2)
    bevel(m, "head", SK2, (0, 47, 1), (11, 2, 11), 0.6)
    band(m, "head", NE, (0, 49.4, 0.6), (12.4, 1.6, 11.6))
    for k in range(7):
        a = math.radians(-90 + k * 30)
        x, z = math.sin(a) * 6, math.cos(a) * 5.6 + 0.6
        h = 4.4 if k == 3 else 3.2 if k in (2, 4) else 2.4
        m.c("head", NE, (x, 50.2 + h / 2, z), (1.4, h, 1.4), (0, 0, -x * 2), (x, 50.2, z))
        if k in (1, 3, 5):
            m.c("head", SO, (x, 50.2, z + 0.8), (1, 1, 0.3), light=True)
    for s, a in ((1, "armL"), (-1, "armR")):
        skull(m, a, (13 * s, 41, 0.4), 8.4, SK, DK, SO, SK2)
        m.c(a, BS, (13 * s, 37.6, 0), (4, 2.6, 4))
        for t in (-2, 0, 2):
            m.c(a, NE, (13 * s + t, 45.6, 0), (1, 1.8 if t else 2.6, 1))
    # wither skulls circling like moons, a halo of netherite shards over the crown, ash falling below
    for k in range(4):
        a = math.radians(k * 90 + 45)
        x, z = math.sin(a) * 17, math.cos(a) * 17
        bevel(m, "ring1", DK, (x, 28 + (k % 2) * 4, z), (3.6, 3.4, 3.6), 0.5)
        m.c("ring1", SO, (x, 28.4 + (k % 2) * 4, z), (3.8, 0.6, 0.6), (0, math.degrees(a) + 90, 0), light=True)
    for k in range(6):
        a = math.radians(k * 60)
        m.c("ring2", NE, (math.sin(a) * 9, 52, math.cos(a) * 9), (1, 3, 1), (0, k * 60, 20))
    for k in range(5):
        a = math.radians(k * 72)
        m.c("ring3", "gray_concrete" if k % 2 else "black_concrete_powder", (math.sin(a) * 7, 6 + k % 3, math.cos(a) * 7), (1, 1, 1), (45, k * 30, 0))
    m.attacks = {"skulls": "spin", "blast": "pulse", "minions": "raise", "charge": "dive"}
    m.melee = "swipe"
    return m


# ================================================================================================ THE ENDER WYRM

DRAGON = copy.deepcopy(anims.QUAD)
def _wings(name, keys):
    """keys: [(time, lift)] lift in degrees, positive raises the wing tips. Mirrored for the right wing."""
    DRAGON[name]["bones"]["wingL"] = {"rot": K(*[(t, (0, 0, a)) for t, a in keys])}
    DRAGON[name]["bones"]["wingR"] = {"rot": K(*[(t, (0, 0, -a)) for t, a in keys])}
_wings("idle", [(0, -8), (1.3, 22), (2.6, -8)])
_wings("walk", [(0, -14), (0.45, 30), (0.9, -14)])
_wings("bite", [(0, 0), (0.35, 34), (0.7, 0)])
_wings("charge", [(0, 0), (0.4, 50), (0.8, -30), (1.3, 0)])
_wings("rear", [(0, 0), (0.7, 60), (0.9, -20), (1.5, 0)])
_wings("toss", [(0, 0), (0.55, 30), (1.1, 0)])
_wings("pounce", [(0, 0), (0.4, 55), (0.85, -35), (1.3, 0)])
_wings("howl", [(0, 0), (0.6, 62), (1.2, 60), (1.5, 0)])
_wings("hurt", [(0, 0), (0.1, 20), (0.35, 0)])
_wings("die_side", [(0, 0), (0.6, 40), (1.4, -50)])
_wings("die_collapse", [(0, 0), (0.6, 40), (1.5, -45)])
DRAGON["fly"] = copy.deepcopy(DRAGON["walk"])
anims.RIGS["dragon"] = DRAGON
anims.MELEE["dragon"] = "bite"


@model
def ender_wyrm():
    """A dragon of the End: a black body armoured in dark grey scales, a ridge of plates from its horns to
    the spade of its tail, purple eyes that glow, a long jaw lined with teeth, great membrane wings on
    finger bones that beat as it moves, and end crystals set into its chest like a heart."""
    m = Model("ender_wyrm", "dragon", 1.55)
    quad(m, body_y=18, legx=6, legz_front=8, legz_back=-10, neck_y=24, neck_z=11)
    m.mbone("wingL", "body", (5, 27, 3))
    BK, BK2, PL, EY, MB, MB2, EN = "black_concrete", "polished_blackstone", "gray_concrete", "magenta_concrete", "black_wool", "purple_concrete", "end_stone"
    for s, (b, z) in ((1, ("legFL", 8)), (-1, ("legFR", 8)), (1, ("legBL", -10)), (-1, ("legBR", -10))):
        quad_leg(m, b, 6 * s, 17, z, 5, BK, BK2, BK, "end_stone")
        m.c(b, PL, (6 * s + 2.6 * s, 13, z), (0.4, 5, 3))
    # body: a deep chest, a long back, scaled belly plates, end crystals set in the breast
    bevel(m, "body", BK, (0, 21, 3), (12, 11, 14), 2)
    bevel(m, "body", BK, (0, 21.4, -8.6), (11, 10, 12), 2)
    for k, z in enumerate((8, 4, 0, -4, -8, -12)):
        m.c("body", BK2, (0, 15.6, z), (9 - abs(k - 2) * 0.6, 0.6, 3.4))
    m.c("body", "pink_stained_glass", (0, 22, 10.1), (3, 3, 1), (0, 0, 45), light=True)
    m.c("body", "white_concrete", (0, 22, 10.5), (1.2, 1.2, 0.4), (0, 0, 45), light=True)
    for s in (1, -1):
        m.c("body", "pink_stained_glass", (3.4 * s, 19.6, 9.7), (1.6, 1.6, 0.8), (0, 0, 45), light=True)
    # the ridge: grey plates down the spine from shoulders to tail
    for k, z in enumerate((10, 6, 2, -2, -6, -10, -14)):
        h = 4 - abs(k - 2) * 0.4
        m.c("body", PL, (0, 26.6 + h / 2 - 0.6, z), (0.8, h, 2.6), (-20, 0, 0))
    # side scales: grey edges along the flanks
    for s in (1, -1):
        for z in (6, 0, -6, -11):
            m.c("body", PL, (6 * s, 22, z), (0.4, 3, 3.6), (0, 0, 10 * s))
    # neck and head: a long curved neck, a narrow skull with horns, glowing eyes, a jaw full of teeth
    neck = limb(m, "head", BK, (0, 24, 11), [(6, 5.6, (48, 0, 0)), (6, 5, (40, 0, 0)), (5, 4.6, (30, 0, 0))], joint=BK2)
    for k, t in enumerate((0.3, 0.55, 0.8)):
        m.c("head", PL, (0, 26.6 + k * 4.6, 14 + k * 3.4), (0.8, 2.6, 2.4), (-30, 0, 0))
    hx, hy, hz = neck
    bevel(m, "head", BK, (0, hy + 1.6, hz + 3.6), (7, 5, 7), 1)
    bevel(m, "head", BK, (0, hy + 0.8, hz + 9.4), (5, 3.4, 7), 0.8)
    m.c("head", BK2, (0, hy + 2.6, hz + 12.6), (4, 0.8, 1))
    for s in (1, -1):
        m.c("head", "black_concrete", (1.2 * s, hy + 2.4, hz + 12.95), (0.8, 0.6, 0.2))
        m.c("head", EY, (3.55 * s, hy + 2.6, hz + 4.6), (0.3, 1, 2), light=True)
        m.c("head", PL, (3.6 * s, hy + 3.8, hz + 4.4), (0.4, 0.6, 3), (0, 0, 0))
        horn(m, "head", PL, (2.4 * s, hy + 4, hz + 1.4), 3, (-60, 0, -14 * s), (-14, 0, 0), 1.6, 0.78)
    for k in range(3):
        m.c("head", PL, (0, hy + 4.4, hz + 5.6 - k * 2.4), (0.6, 1.6 - k * 0.3, 1.6), (-20, 0, 0))
    bevel(m, "jaw", BK2, (0, hy - 1.6, hz + 8.6), (4.4, 1.6, 8), 0.5)
    for s in (1, -1):
        for k in range(3):
            m.c("jaw", "white_concrete", (1.8 * s, hy - 0.5, hz + 6.6 + k * 2.2), (0.5, 1, 0.5))
            m.c("head", "white_concrete", (1.8 * s, hy - 0.8, hz + 7.6 + k * 2.2), (0.5, 1, 0.5))
    # tail: a long whip of segments with plates, ending in a spade
    tip = limb(m, "tail", BK, (0, 22, -14), [(6, 4, (-112, 0, 0)), (6, 3.4, (-100, 0, 6)), (6, 2.8, (-96, 0, 12)), (5, 2.2, (-94, 0, 16)), (5, 1.6, (-92, 0, 18))], joint=BK2)
    m.c("tail", PL, (tip[0], tip[1], tip[2]), (4, 0.6, 4), (0, 45, 0))
    m.c("tail", EY, (tip[0], tip[1] + 0.3, tip[2]), (1, 0.4, 1), (0, 45, 0), light=True)
    for k in range(4):
        d = dirof((-100, 0, 6 + k * 4))
        x, y, z = 0 + d[0] * 6 * (k + 1), 22 + d[1] * 6 * (k + 1), -14 + d[2] * 6 * (k + 1)
        m.c("tail", PL, (x, y + 2.2 - k * 0.3, z), (0.6, 2 - k * 0.3, 2), (-20, 0, 0))
    # wings: an arm bone out to the wrist, three finger bones swept back, black membrane between them with
    # a scalloped trailing edge lit purple
    def spar(w, a, b, t, blk):
        cx, cy, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        yaw = math.degrees(math.atan2(dx, dz))
        pitch = -math.degrees(math.asin(dy / L))
        m.c(w, blk, (cx, cy, cz), (t, t, L), (pitch, yaw, 0), (cx, cy, cz))
    trail = [(5, -9), (10, -12), (16, -15), (22, -17), (27, -16), (31, -11)]
    def zt(x):
        for (x0, z0), (x1, z1) in zip(trail, trail[1:]):
            if x0 <= x <= x1:
                return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return trail[-1][1]
    for s, w in ((1, "wingL"), (-1, "wingR")):
        sh, el, wr = (5 * s, 27, 3), (17 * s, 30, 3.6), (30 * s, 28, 2)
        spar(w, sh, el, 2.2, BK2)
        spar(w, el, wr, 1.8, BK2)
        m.c(w, BK, el, (2.4, 2.4, 2.4))
        m.c(w, PL, (wr[0], wr[1] + 1.6, wr[2] + 0.6), (1, 3, 1), (-20, 0, -10 * s))
        for tx in (31, 22, 13):
            spar(w, wr, (tx * s, 27.4 - (31 - tx) * 0.02, zt(tx) - 0.4), 1, BK2)
        for k in range(6):
            x0, x1 = 5 + k * 4.4, 5 + (k + 1) * 4.4
            xm = (x0 + x1) / 2
            front = 3 + (0.3 if xm < 17 else -0.05 * (xm - 17))
            back = zt(xm)
            y = 28 + (xm - 5) * 0.08 - (xm - 17) ** 2 * 0.006
            m.c(w, MB, (xm * s, y, (front + back) / 2), (x1 - x0, 0.3, front - back))
            m.c(w, MB2, (xm * s, y - 0.1, back + 0.3), (x1 - x0 - 0.8, 0.3, 0.8), light=True)
    m.attacks = {"breath": "howl", "charge": "charge", "bite": "bite", "minions": "rear"}
    m.melee = "bite"
    return m


# ================================================================================================ THE GALE SOVEREIGN

@model
def gale_sovereign():
    """A breeze that grew up in a trial chamber and took its armour: a pale head in an oxidized copper helm
    with a visor slit that glows, a heavy iron core where its heart should be, a body that is nothing but
    a spinning column of wind in three bands, breeze rods circling its head and two copper gauntlets that
    float where its hands would be."""
    m = Model("gale_sovereign", "float", 1.9)
    m.bone("core", "root", (0, 10, 0))
    m.bone("head", "core", (0, 26, 0))
    m.mbone("armL", "core", (9, 22, 0))
    m.bone("ring1", "core", (0, 4, 0))
    m.bone("ring2", "head", (0, 32, 0))
    m.bone("ring3", "core", (0, 16, 0))
    m.no_elbows = True
    WN, WN2, CU, CU2, TU, HD, GL = "white_stained_glass", "light_blue_stained_glass", "oxidized_copper", "copper_block", "tuff_bricks", "calcite", "light_blue_concrete"
    # the wind: three bands of curling gusts, the widest at the bottom, each spinning its own way
    for k in range(10):
        a = math.radians(k * 36)
        m.c("ring1", WN if k % 2 else WN2, (math.sin(a) * 8, 3 + (k % 2) * 1.6, math.cos(a) * 8), (5, 1.4, 1.6), (0, k * 36 + 90, 18))
    for k in range(8):
        a = math.radians(k * 45 + 20)
        m.c("ring1", WN2 if k % 2 else WN, (math.sin(a) * 5.6, 8 + (k % 2), math.cos(a) * 5.6), (3.6, 1.2, 1.4), (0, k * 45 + 110, -16))
    for k in range(8):
        a = math.radians(k * 45)
        m.c("ring3", WN if k % 2 else WN2, (math.sin(a) * 4.6, 14 + (k % 2) * 1.4, math.cos(a) * 4.6), (3, 1.2, 1.2), (0, k * 45 + 90, 14))
    for k in range(4):
        a = math.radians(k * 90 + 45)
        m.c("ring3", GL, (math.sin(a) * 6.6, 17, math.cos(a) * 6.6), (0.8, 0.8, 0.8), (45, 45, 0), light=True)
    # the spine of the column: stacked tuff and copper discs narrowing to a point
    stack(m, "core", TU, 0, 1, 0, [(1.6, 3, 1.6), (2.4, 3, 2.4), (3.2, 4, 3.2), (4, 4, 4)])
    for y in (4, 8, 12):
        m.c("core", CU, (0, y, 0), (y * 0.3 + 1.6, 0.6, y * 0.3 + 1.6))
    # the chest: a tuff-brick ribcage round the heavy core, copper bands, the core glowing at the seams
    bevel(m, "core", TU, (0, 21, 0), (9, 7, 7), 1)
    bevel(m, "core", "polished_deepslate", (0, 21, 2.6), (4.4, 4.4, 3), 0.6)
    m.c("core", "iron_block", (0, 21, 3.9), (2.6, 2.6, 0.6))
    m.c("core", GL, (0, 21, 4.25), (3.4, 0.4, 0.2), light=True)
    m.c("core", GL, (0, 21, 4.25), (0.4, 3.4, 0.2), light=True)
    band(m, "core", CU, (0, 24.4, 0), (9.4, 1, 7.4), studs=3, stud_block=CU2)
    band(m, "core", CU, (0, 17.6, 0), (8, 1, 6.4))
    for s in (1, -1):
        bevel(m, "core", CU, (6 * s, 24.6, 0), (4, 2.6, 6), 0.6, (0, 0, -18 * s), (5 * s, 24, 0))
        m.c("core", "lightning_rod", (7.4 * s, 26.6, 0), (0.8, 3.4, 0.8), (0, 0, -24 * s))
    # the head: pale, in a copper helm with a crest, the visor slit glowing, gusts streaming off the back
    bevel(m, "head", HD, (0, 30, 0.4), (9, 8, 9), 1.2)
    bevel(m, "head", CU, (0, 33.4, 0.2), (9.6, 2.6, 9.6), 0.6)
    for s in (1, -1):
        m.c("head", CU, (4.6 * s, 30.4, 0), (0.8, 6, 8.4))
    m.c("head", CU, (0, 36, -0.4), (1.4, 3, 8), (0, 0, 0))
    m.c("head", CU2, (0, 37.6, -0.4), (0.8, 0.8, 7))
    m.c("head", "black_concrete", (0, 30.6, 4.75), (7, 1.8, 0.2))
    for s in (1, -1):
        m.c("head", GL, (2 * s, 30.6, 4.9), (2, 0.8, 0.2), light=True)
    m.c("head", "black_concrete", (0, 27.8, 4.75), (3, 0.8, 0.2))
    for k, (x, y, L) in enumerate(((-2, 31, 6), (2, 29.6, 7), (0, 33, 5))):
        m.c("head", WN, (x, y, -4.6 - L / 2), (1.4, 1, L), (0, 0, 0))
    # breeze rods circling the head
    for k in range(5):
        a = math.radians(k * 72)
        x, z = math.sin(a) * 9, math.cos(a) * 9
        m.c("ring2", GL, (x, 31 + (k % 2) * 2, z), (1, 6, 1), (0, 0, 12), light=True)
        m.c("ring2", "white_concrete", (x, 34.6 + (k % 2) * 2, z), (1.3, 1.2, 1.3), light=True)
    # the gauntlets: oxidized copper fists floating free, a cuff of wind where the wrist would be
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11 * s
        bevel(m, a, CU, (x, 18, 1.4), (5, 6, 5), 0.8)
        m.c(a, CU2, (x, 15.2, 1.4), (5.4, 1, 5.4))
        for t in (-1.4, 0, 1.4):
            m.c(a, CU, (x + t, 14, 3.4), (1.2, 2, 1.2))
        m.c(a, "lightning_rod", (x, 21.6, 1.4), (1, 2.6, 1))
        for k in range(4):
            aa = math.radians(k * 90)
            m.c(a, WN, (x + math.sin(aa) * 3.4, 22.6, 1.4 + math.cos(aa) * 3.4), (2.6, 0.6, 0.8), (0, k * 90 + 90, 0))
    # more wind: a wide skirt of gusts at the ground, a collar of gusts under the chest, wind charges
    # orbiting further out, rivets on the helm
    for k in range(8):
        a = math.radians(k * 45 + 22)
        m.c("ring1", WN2 if k % 2 else WN, (math.sin(a) * 11, 0.8, math.cos(a) * 11), (4.4, 0.8, 1.2), (0, k * 45 + 90, 8))
    for k in range(8):
        a = math.radians(k * 45 + 10)
        m.c("ring3", WN if k % 2 else WN2, (math.sin(a) * 6.6, 19.6, math.cos(a) * 6.6), (3.4, 0.8, 1.2), (0, k * 45 + 90, -10))
    for k in range(3):
        a = math.radians(k * 120 + 30)
        x, z = math.sin(a) * 14, math.cos(a) * 14
        bevel(m, "ring2", WN2, (x, 27, z), (2.6, 2.6, 2.6), 0.6, light=True)
        m.c("ring2", "white_concrete", (x, 27, z), (1.2, 1.2, 1.2), light=True)
        m.c("ring2", WN, (x, 27, z), (3.6, 0.6, 0.6), (0, k * 40, 30))
    for s_ in (1, -1):
        for z in (-2.6, 0, 2.6):
            m.c("head", CU2, (5.05 * s_, 32, z), (0.3, 0.6, 0.6))
    # the tip of the tornado: a tight spiral of wind streaks where it touches the ground
    for k in range(4):
        a = math.radians(k * 90 + 20)
        m.c("ring1", WN if k % 2 else WN2, (math.sin(a) * 2.6, 0.4 + k * 0.45, math.cos(a) * 2.6), (2.8, 0.6, 0.8), (0, k * 90 + 110, 12))
    m.attacks = {"gust": "pulse", "charges": "spin", "pull": "raise", "dash": "dive"}
    m.melee = "swipe"
    return m


# ================================================================================================ THE UNMAKER

@model
def the_unmaker():
    """THE UNMAKER, the finale. A floating titan of obsidian armoured in end-stone plates trimmed in gold.
    One great eye with a purple iris; a crown of eight shards turning over its head; a void heart in a
    diamond-shaped opening in its chest; four arms: two huge gauntleted fists above, a void blade and an
    end-crystal orb below; two blade fins on its back; no legs, its body ends in a trailing tail of stone
    plates over a rune circle on the ground."""
    m = Model("the_unmaker", "titan", 3.0)
    m.bone("core", "root", (0, 18, 0))
    m.bone("tail", "core", (0, 14, 0))
    m.bone("chest", "core", (0, 24, 0))
    m.bone("heart", "chest", (0, 29, 5.6))
    m.bone("head", "chest", (0, 38, 0.5))
    m.bone("jaw", "head", (0, 39.5, 4))
    m.bone("halo", "head", (0, 47, 0.5))
    m.mbone("armL", "chest", (12, 36, 0))
    m.mbone("foreL", "armL", (17, 26, 0.5))
    m.mbone("arm2L", "chest", (9.5, 27, 1))
    m.mbone("finL", "chest", (5, 34, -6))
    for i in (1, 2, 3):
        m.bone(f"ring{i}", "root", (0, 0, 0))
    m.no_elbows = True
    OB, CRY, EN, ENB, GD, PU, PU2, MG = "obsidian", "crying_obsidian", "end_stone", "end_stone_bricks", "gold_block", "purpur_block", "purple_stained_glass", "magenta_concrete"
    # the tail: stone plates hanging in tiers, narrowing to a point, void light leaking between them
    for k, (y, w, d) in enumerate(((17, 12, 9), (13.4, 10, 8), (10, 8, 6.6), (6.8, 6, 5), (4, 4, 3.6))):
        bevel(m, "tail", OB, (0, y, 0), (w, 3.2, d), 0.6)
        m.c("tail", ENB if k % 2 == 0 else EN, (0, y - 1.5, d / 2 - 0.2), (w * 0.8, 0.6, 0.4))
        if k < 4:
            m.c("tail", PU2, (0, y - 1.8, 0), (w * 0.7, 0.4, d * 0.7), light=True)
    m.c("tail", MG, (0, 1.6, 0), (1.6, 2, 1.6), light=True)
    # the chest: a broad obsidian torso, end-stone plates with gold trim, a diamond opening for the heart
    bevel(m, "chest", OB, (0, 30, 0), (20, 14, 12), 2)
    bevel(m, "chest", OB, (0, 22.6, 0), (14, 4, 9), 1)
    for s in (1, -1):
        bevel(m, "chest", ENB, (5.8 * s, 31.6, 5.6), (7, 9, 1.6), 0.6)
        m.c("chest", GD, (5.8 * s, 36.3, 5.8), (7.2, 0.6, 1.6))
        m.c("chest", GD, (9.3 * s, 31.6, 5.8), (0.6, 9, 1.6))
    m.c("chest", "black_concrete", (0, 30, 6.1), (6, 6, 0.4), (0, 0, 45))
    for s in (1, -1):
        m.c("chest", GD, (2.4 * s, 32.4, 6.3), (0.6, 4.8, 0.6), (0, 0, 45 * s))
        m.c("chest", GD, (2.4 * s, 27.6, 6.3), (0.6, 4.8, 0.6), (0, 0, -45 * s))
    band(m, "chest", GD, (0, 24.6, 0), (14.4, 1, 9.4), studs=4, stud_block=MG)
    # the heart: a void core, a crying-obsidian shell, magenta light
    bevel(m, "heart", CRY, (0, 30, 5.2), (4.4, 4.4, 3), 0.6, light=True)
    m.c("heart", MG, (0, 30, 6.4), (2.4, 2.4, 0.8), (0, 0, 45), light=True)
    m.c("heart", "white_concrete", (0, 30, 6.85), (0.8, 0.8, 0.2), (0, 0, 45), light=True)
    # shoulders: great end-stone pauldrons with gold rims and a purpur spike
    for s in (1, -1):
        bevel(m, "chest", ENB, (11.6 * s, 37.6, 0), (8, 4, 10), 1, (0, 0, -14 * s), (10 * s, 36, 0))
        m.c("chest", GD, (12.4 * s, 35.6, 0), (7.4, 0.8, 10.4), (0, 0, -14 * s), (10 * s, 36, 0))
        horn(m, "chest", PU, (12.6 * s, 39.6, 0), 3, (0, 0, -20 * s), (0, 0, -14 * s), 2.2, 0.75)
    # the head: a smooth helm of obsidian, one great eye, a jaw of end-stone teeth
    bevel(m, "head", OB, (0, 43, 0.6), (10, 9, 9.4), 1.4)
    m.c("head", GD, (0, 47.2, 0.6), (10.4, 0.8, 9.8))
    m.c("head", OB, (0, 46.6, 5.4), (8, 1.6, 0.8), (0, 0, 0))
    bevel(m, "head", "white_concrete", (0, 43.6, 5.25), (5.6, 4, 0.6), 0.6)
    m.c("head", MG, (0, 43.6, 5.6), (3, 3, 0.2), light=True)
    m.c("head", "black_concrete", (0, 43.6, 5.75), (1.2, 2.2, 0.1))
    m.c("head", "white_concrete", (-0.8, 44.6, 5.8), (0.6, 0.6, 0.1), light=True)
    bevel(m, "jaw", OB, (0, 38.4, 2.8), (8, 2.4, 6.6), 0.6)
    paint(m, "jaw", "front", (0, 39.8, 6.1), ["W.W.W.W"], {"W": EN}, px=1.1, depth=0.4)
    for s in (1, -1):
        m.c("head", ENB, (5.2 * s, 43, 0.6), (0.6, 6, 6))
        m.c("head", GD, (5.55 * s, 43, 0.6), (0.2, 1, 6.2))
    # the crown: eight shards turning over the head, gold-tipped, evenly spaced
    for k in range(8):
        a = math.radians(k * 45)
        x, z = math.sin(a) * 8, math.cos(a) * 8 + 0.5
        h = 6 if k % 2 == 0 else 4.4
        m.c("halo", PU if k % 2 else EN, (x, 49 + h / 2, z), (1.6, h, 1.6), (math.cos(a) * 10, 0, -math.sin(a) * 10), (x, 49, z))
        m.c("halo", GD, (x, 49.4 + h, z), (1, 1, 1), (45, k * 45, 0))
    # upper arms: obsidian with end-stone gauntlets, gold rings, huge fists
    for s, a, f in ((1, "armL", "foreL"), (-1, "armR", "foreR")):
        x = 15 * s
        bevel(m, a, OB, (x, 31.4, 0), (6.6, 10, 6.6), 1, (0, 0, -12 * s), (12 * s, 36, 0))
        m.c(a, GD, (x + 1 * s, 27.6, 0.3), (7, 1, 7), (0, 0, -12 * s), (12 * s, 36, 0))
        bevel(m, f, ENB, (17 * s, 20.6, 0.5), (7.4, 10, 7.4), 1)
        m.c(f, GD, (17 * s, 25, 0.5), (7.8, 1, 7.8))
        m.c(f, MG, (17 * s + 3.75 * s, 21, 0.5), (0.3, 4, 1.4), light=True)
        bevel(m, f, OB, (17 * s, 13, 1.4), (8.6, 6.4, 8.6), 1.2)
        for t in (-2.6, 0, 2.6):
            m.c(f, EN, (17 * s + t, 13.6, 5.8), (1.6, 1.6, 0.6))
    # lower arms: thinner; the left holds a void blade, the right an end crystal
    for s, a in ((1, "arm2L"), (-1, "arm2R")):
        x = 11 * s
        bevel(m, a, OB, (x, 22, 2), (4, 9, 4), 0.6)
        m.c(a, GD, (x, 18.4, 2), (4.4, 0.8, 4.4))
        bevel(m, a, ENB, (x, 15.6, 2.4), (4.4, 4.6, 4.4), 0.6)
    m.c("arm2L", GD, (11, 12.6, 4), (1.4, 3, 1.4))
    m.c("arm2L", OB, (11, 14.6, 4), (1.4, 1, 7))
    m.c("arm2L", PU, (11, 27, 4), (1.2, 22, 3.6))
    m.c("arm2L", MG, (11, 27, 4), (1.4, 20, 0.6), light=True)
    m.c("arm2L", PU, (11, 38.4, 4), (1.2, 2.6, 2.6), (45, 0, 0))
    m.c("arm2R", OB, (-11, 11.6, 4), (3, 1, 3))
    m.c("arm2R", PU2, (-11, 8.4, 4), (4.4, 4.4, 4.4), (45, 0, 45), light=True)
    m.c("arm2R", MG, (-11, 8.4, 4), (2.4, 2.4, 2.4), (0, 45, 45), light=True)
    m.c("arm2R", "white_concrete", (-11, 8.4, 4), (1, 1, 1), light=True)
    # fins: two blades on the back, obsidian with a purple edge
    for s, f in ((1, "finL"), (-1, "finR")):
        for k, (L, r) in enumerate(((14, 30), (10, 55))):
            m.c(f, OB, (5 * s + math.sin(math.radians(r)) * L / 2 * s, 34 + math.cos(math.radians(r)) * L / 2, -6.6 - k * 0.6), (2.4, L, 0.8), (0, 0, -r * s), (5 * s, 34, -6.6))
            m.c(f, PU2, (5 * s + math.sin(math.radians(r)) * (L / 2 + 0.6) * s + 1.2 * s * math.cos(math.radians(r)), 34 + math.cos(math.radians(r)) * L / 2 - 1.2 * math.sin(math.radians(r)), -6.6 - k * 0.6), (0.6, L * 0.9, 0.9), (0, 0, -r * s), light=True)
    # rings: end-stone chunks orbiting the waist, motes higher up, a rune circle on the ground
    for k in range(6):
        a = math.radians(k * 60)
        bevel(m, "ring1", EN if k % 2 else ENB, (math.sin(a) * 18, 20, math.cos(a) * 18), (3.4, 3, 3.4), 0.6)
    for k in range(6):
        a = math.radians(k * 60 + 30)
        m.c("ring2", MG, (math.sin(a) * 22, 34, math.cos(a) * 22), (1, 1, 1), (45, 45, 0), light=True)
    for k in range(12):
        a = math.radians(k * 30)
        m.c("ring3", PU if k % 2 else MG, (math.sin(a) * 16, 0.2, math.cos(a) * 16), (5, 0.3, 1), (0, k * 30 + 90, 0), light=k % 2 == 0)
    m.attacks = {"smash": "smash", "blade": "sweep", "orb": "cast", "crown": "roar"}
    m.melee = "swipe"
    return m
