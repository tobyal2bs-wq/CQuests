"""v4 normal bosses: real Minecraft mobs, grown huge and given a story, in the clean chunky style of the
Grand Augur. Each keeps the shape and colours you know the mob by and adds only what tells its story."""
import copy
import math
import anims
from models import model, biped, horn, limb, quad, dirof
from build import Model
from kit import paint, band, stack, bevel, crack
from v3_kit import grow, vines

SPAWN, DEATH = {}, {}

OMINOUS = [
    ".......",
    ".GGGGG.",
    ".G.K.G.",
    ".GGGGG.",
    "..KKK..",
    "...C...",
    "..CCC..",
    ".K.K.K.",
    "K.K.K.K",
    ".......",
]


@model
def pillager_captain():
    """Captain Crossfire, the raid captain: a big grey pillager head with the dark unibrow and long nose,
    the ominous banner worn on his head like every raid captain, a dark shirt under a leather vest with a
    bandolier of fireworks, and a heavy crossbow loaded with a rocket, held at the hip."""
    m = Model("pillager_captain", "biped", 2.0)
    biped(m, hip=8, legx=2.4, neck=19.5, shoulder=18, armx=6.6)
    m.bone("banner", "head", (0, 33, 0.5))
    m.bone("bow", "armR", (-6.6, 9, 0.4))
    m.hold = {"bow": 0}
    m.bend = -40
    SK, SK2, BR, SH, VS, LT, WD = ("light_gray_concrete", "polished_andesite", "gray_concrete", "gray_terracotta",
                                   "brown_terracotta", "brown_concrete", "dark_oak_planks")
    # legs: dark trousers, leather boots
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.4 * s
        m.c(b, VS, (x, 5.4, 0), (3, 5.2, 3))
        m.c(b, LT, (x, 1.4, 0.4), (3.4, 2.8, 4))
        m.c(b, BR, (x, 3.0, 0.4), (3.6, 0.6, 4.2))
    # body: the dark shirt, an open brown vest, a belt, a bandolier of red fireworks across the chest
    stack(m, "hips", VS, 0, 7.4, 0, [(8.6, 1.6, 6)])
    bevel(m, "body", SH, (0, 13.8, 0), (8.6, 9, 6), 0.6)
    for s in (1, -1):
        m.c("body", VS, (3.1 * s, 13.8, 3.05), (2.4, 9, 0.3))
        m.c("body", VS, (4.35 * s, 13.8, 0), (0.2, 8.4, 5.4))
    band(m, "body", LT, (0, 10.2, 0), (8.8, 1.2, 6.2), studs=1, stud_block="iron_block")
    for k in range(5):
        x, y = -3.2 + k * 1.6, 17 - k * 1.5
        m.c("body", LT, (x, y, 3.3), (1.8, 1.0, 0.3), (0, 0, 40))
        m.c("body", "red_concrete", (x, y + 0.4, 3.55), (0.7, 1.6, 0.4))
    m.c("body", LT, (0, 13, -3.3), (2.4, 9, 0.6), (0, 0, -30))
    # a quiver of bolts on the back
    m.c("body", LT, (2.4, 14.6, -3.9), (2.6, 7, 2.2), (0, 0, -18))
    for dx in (-0.5, 0.5):
        m.c("body", "white_concrete", (3.6 + dx, 19, -3.9), (0.4, 2.4, 0.4), (0, 0, -18))
    # arms: dark sleeves, leather bracers, grey hands
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6.6 * s
        bevel(m, a, SH, (x, 15.4, 0), (3.4, 5.4, 3.6), 0.5)
        m.c(a, SH, (x, 11.2, 0.3), (3.2, 4.4, 3.4))
        m.c(a, LT, (x, 10, 0.3), (3.6, 1.6, 3.8))
        m.c(a, SK, (x, 8, 0.4), (2.6, 2.4, 2.6))
    # the crossbow: stock along the arm, a curved bow across the front, the string, a loaded rocket
    m.c("bow", WD, (-6.6, 9, 3.6), (1.4, 1.4, 10))
    m.c("bow", "iron_block", (-6.6, 9, 7.4), (1.8, 1.8, 1.2))
    for s in (1, -1):
        m.c("bow", WD, (-6.6 + 3 * s, 9, 8.2), (4.4, 1.0, 1.0), (0, 22 * s, 0))
        m.c("bow", WD, (-6.6 + 5.6 * s, 9, 6.8), (1.4, 1.0, 1.0), (0, 50 * s, 0))
    m.c("bow", "white_wool", (-6.6, 9, 6.0), (11, 0.25, 0.25))
    m.c("bow", "red_concrete", (-6.6, 9.9, 7.4), (0.9, 0.9, 4))
    m.c("bow", "white_concrete", (-6.6, 9.9, 9.6), (0.9, 0.9, 0.6))
    # head: the pillager face, big and grey: dark unibrow, small eyes, a long nose, a sour mouth
    bevel(m, "head", SK, (0, 26.4, 0.5), (13, 12.6, 12.4), 1.2)
    m.c("head", SK2, (0, 20.6, 0.5), (11, 1.4, 10.4))
    m.c("head", BR, (0, 28.8, 6.85), (11.4, 1.8, 0.4))
    for s in (1, -1):
        m.c("head", "white_concrete", (3.2 * s, 26.8, 6.8), (2.4, 1.6, 0.2))
        m.c("head", "black_concrete", (2.6 * s, 26.8, 6.95), (1.0, 1.6, 0.2))
        m.c("head", SK2, (5 * s, 24, 6.8), (2.2, 1.2, 0.2))
    m.c("head", "light_gray_terracotta", (0, 24, 8.2), (3, 7, 3))
    m.c("head", "light_gray_terracotta", (0, 20.8, 8.5), (2.4, 1, 2.4))
    m.c("head", BR, (0, 22.2, 6.8), (5, 0.6, 0.2))
    # the ominous banner worn on the head: a crossbar, a white cloth with the illager pattern both sides
    m.c("banner", "dark_oak_log", (0, 33.4, 0.5), (1, 1.2, 1))
    m.c("banner", "dark_oak_log", (0, 46.4, 0.5), (11, 1, 1))
    m.c("banner", "white_wool", (0, 39.6, 0.5), (10, 12.6, 0.6))
    for face, z in (("front", 0.8), ("back", 0.2)):
        paint(m, "banner", face, (0, 39.8, z), OMINOUS, {"G": "light_gray_concrete", "K": "black_concrete", "C": "cyan_concrete"}, px=1.3, depth=0.15)
    m.attacks = {"volley": "cast", "meteor": "roar", "shockwave": "stomp", "charge": "lunge"}
    m.melee = "swipe"
    return m


@model
def pale_watcher():
    """The Pale Watcher, a creaking that grew for a thousand years in the pale garden: a tall, thin body of
    grey pale oak bark, long arms ending in twig fingers, a narrow head with two burning orange eyes, its
    creaking heart beating orange in an open chest, resin oozing at the joints, pale moss hanging off it
    and branches growing out of its shoulders and head."""
    m = Model("pale_watcher", "biped", 2.2)
    biped(m, hip=20, legx=2.6, neck=38, shoulder=37, armx=6.4)
    m.bone("heart", "body", (0, 30, 1))
    m.bend = -14
    BK, BK2, MS, RS, EY, HT = "pale_oak_log", "gray_terracotta", "pale_moss_block", "resin_block", "orange_concrete", "creaking_heart"
    # legs: long thin bark pillars, knotted knees, root feet splayed on the ground
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.6 * s
        m.c(b, BK, (x, 14.6, 0), (3.4, 11, 3.4))
        m.c(b, BK2, (x, 9.2, 0.2), (4, 2, 4))
        m.c(b, BK, (x, 4.6, 0.2), (3, 8, 3))
        for dz, ry in ((2.2, 0), (-1.6, 180), (0.4, 90 * s)):
            m.c(b, BK2, (x + (1.8 * s if ry == 90 * s else 0), 0.6, dz), (1.4, 1.2, 3), (0, ry, 0))
        m.c(b, RS, (x + 1.4 * s, 9.6, 1.6), (1, 1.4, 1), light=True)
    # body: a narrow torso, the bark split open on the chest round the heart
    m.c("hips", BK2, (0, 21, 0), (7, 2.4, 4))
    m.c("body", BK, (0, 25.6, 0), (6, 7, 4))
    bevel(m, "body", BK, (0, 33, 0), (9, 8, 5), 0.6)
    m.c("body", "black_concrete", (0, 30.4, 2.3), (4, 5, 0.6))
    for s in (1, -1):
        m.c("body", BK2, (2.6 * s, 30.4, 2.6), (1, 6.4, 0.8), (0, 0, 6 * s))
    m.c("heart", HT, (0, 30.4, 1.6), (3, 3.6, 2.4), light=True)
    m.c("heart", EY, (0, 30.4, 2.85), (1, 1.6, 0.2), light=True)
    m.c("body", RS, (-3.6, 27, 2.1), (1.4, 2.2, 1), light=True)
    m.c("body", RS, (3.2, 35.4, 2.4), (1.6, 1.2, 0.8), light=True)
    # pale moss hanging from the shoulders, front and back
    for (x, z, L) in ((-3.4, 2.6, 5), (3.8, 2.6, 3.2), (-1.6, -2.6, 6), (2.4, -2.6, 4.4)):
        m.c("body", MS, (x, 36.6 - L / 2, z), (1.6, L, 0.4))
    # arms: long and thin, a knotted elbow, twig fingers spread
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6.4 * s
        m.c(a, BK, (x, 32, 0), (2.8, 10, 2.8))
        m.c(a, BK2, (x, 26.6, 0), (3.4, 1.8, 3.4))
        m.c(a, BK, (x, 20.6, 0.2), (2.4, 10, 2.4))
        for k, (dx, dz) in enumerate(((-0.8, 0.8), (0.4, 1.0), (1.0, -0.4))):
            m.c(a, BK2, (x + dx * s, 13.8, dz), (0.7, 4.4, 0.7), (dz * 10, 0, -dx * 12 * s))
        m.c(a, MS, (x + 1.5 * s, 21, 0), (0.4, 6, 1.6))
    # branches out of the shoulders: crooked, tipped with pale moss
    for s in (1, -1):
        tip = limb(m, "body", BK, (4 * s, 37, -0.6), [(4, 1.4, (-10, 0, -40 * s)), (3.6, 1.0, (-20, 0, -10 * s)), (2.6, 0.8, (-30, 0, -50 * s))])
        m.c("body", MS, tip, (2.4, 1.6, 2.4))
    # head: tall and narrow, twigs crowning it, two burning orange eye slits and a dark mouth crack
    bevel(m, "head", BK, (0, 44, 0), (7, 12, 6), 0.6)
    for s in (1, -1):
        m.c("head", EY, (1.7 * s, 45.6, 3.05), (1.2, 2.6, 0.2), light=True)
        m.c("head", "yellow_concrete", (1.7 * s, 46.2, 3.15), (0.5, 0.8, 0.1), light=True)
    m.c("head", "black_concrete", (0, 40.6, 3.05), (3.4, 0.8, 0.2))
    m.c("head", "black_concrete", (0.6, 41.3, 3.05), (0.8, 0.8, 0.2))
    for (x, rz, L) in ((-2.6, 30, 6), (-0.6, 8, 8), (1.6, -18, 5), (2.8, -40, 6.4)):
        tip = limb(m, "head", BK2, (x, 50, 0), [(L * 0.6, 1.0, (0, 0, rz)), (L * 0.4, 0.7, (-20, 0, rz * 1.6))])
    m.c("head", MS, (0, 50.4, -1.6), (6, 1.0, 3))
    m.c("head", MS, (-2.4, 47, -3.1), (1.6, 6, 0.4))
    m.attacks = {"spikes": "slam", "frost": "roar", "pull": "lunge", "minions": "cast"}
    m.melee = "swipe"
    return m


@model
def weeping_ghast():
    """The Weeping Matron, the oldest ghast of the Nether: the vanilla ghast as a giant white cube, its eyes
    shut with grey tears running down, nine tentacles hanging under it that sway on their own, old
    scorch marks and cracks on its skin, and tears of soul fire that glow and fall when it cries."""
    m = Model("weeping_ghast", "float", 3.0)
    m.bone("core", "root", (0, 22, 0))
    m.bone("head", "core", (0, 22, 0))
    WH, WH2, GR, DK, SL = "white_concrete", "smooth_stone", "light_gray_concrete", "gray_concrete", "light_blue_concrete"
    # the body: the white cube, softened at the edges, a few grey scorch marks and a crack
    bevel(m, "head", WH, (0, 22, 0), (16, 16, 16), 0.8)
    paint(m, "head", "front", (0, 22, 8), [
        "................",
        "................",
        "................",
        "..GGGG....GGGG..",
        "..DDDD....DDDD..",
        "...T........T...",
        "...T........T...",
        "...S........S...",
        "...T........T...",
        "...S...DDDD.S...",
        ".......DDDD.....",
        "...S........S...",
        "................",
        "................",
        "................",
        "................",
    ], {"G": GR, "D": DK, "T": GR, "S": (SL, 0.3, True)}, px=1, depth=0.3)
    for side in ("left", "right"):
        paint(m, "head", side, ((8 if side == "left" else -8), 22, 0), [
            "................", ".....G..........", "....GG......G...", "...........GG...", "................",
            "..G.............", "..GG............", "........G.......", ".......GG.......", "................",
        ], {"G": GR}, px=1.6, depth=0.25)
    paint(m, "head", "top", (0, 30, 0), ["......", ".G..G.", "..GG..", "......"], {"G": GR}, px=2.6, depth=0.25)
    # tentacles: nine, in a three by three grid, each its own bone so each one sways on its own
    lens = [9, 13, 10, 12, 8, 14, 11, 9, 12]
    for i in range(9):
        x, z = (i % 3 - 1) * 5, (i // 3 - 1) * 5
        b = "tent%d" % i
        m.bone(b, "head", (x, 14, z))
        L = lens[i]
        m.c(b, WH, (x, 14 - L * 0.32, z), (2.2, L * 0.64, 2.2))
        m.c(b, WH2, (x, 14 - L * 0.82, z), (1.8, L * 0.36, 1.8))
    idle = copy.deepcopy(anims.RIGS["float"]["idle"])
    for i in range(9):
        a, b = 10 + (i % 3) * 4, -8 - (i % 2) * 5
        sg = 1 if i % 2 == 0 else -1
        idle["bones"]["tent%d" % i] = {"rot": anims.K((0, (a * sg, 0, b * sg)), (1.5, (-a * sg, 0, -b * sg)), (3.0, (a * sg, 0, b * sg)))}
    m.anims = {"idle": idle}
    m.no_elbows = True
    m.attacks = {"meteor": "pulse", "roar": "raise", "orbs": "spin", "dive": "dive"}
    m.melee = "pulse"
    return m


@model
def elder_sniffer():
    """The Elder Sniffer, the last of the ancient sniffers: the vanilla sniffer's rust-red fur and green
    moss back, its big flat nose and six short legs, so old that a whole garden grows on its back:
    torchflowers, a pitcher plant, mossy stones and a sapling."""
    m = Model("elder_sniffer", "quad", 2.2)
    quad(m, body_y=13, legx=8, legz_front=10, legz_back=-10, neck_y=16, neck_z=16)
    FR, FR2, MS, MS2, NS, DK = "red_terracotta", "terracotta", "moss_block", "green_concrete", "lime_terracotta", "black_concrete"
    # six short legs: the four of the rig and a middle pair on the body
    for s, (b, z) in ((1, ("legFL", 10)), (-1, ("legFR", 10)), (1, ("legBL", -10)), (-1, ("legBR", -10))):
        x = 8 * s
        bevel(m, b, FR, (x, 6, z), (5, 8, 5), 0.6)
        m.c(b, FR2, (x, 1.2, z + 0.4), (5.4, 2.4, 6))
    for s in (1, -1):
        bevel(m, "body", FR, (8 * s, 6, 0), (5, 8, 5), 0.6)
        m.c("body", FR2, (8 * s, 1.2, 0.4), (5.4, 2.4, 6))
    # body: long and low, rust-red fur, a deep green moss blanket over the back
    bevel(m, "body", FR, (0, 15, 0), (20, 12, 30), 1.6)
    m.c("body", MS, (0, 21.4, 0), (20.4, 1.6, 30.4))
    for s in (1, -1):
        m.c("body", MS, (10.3 * s, 18.4, 0), (0.6, 5, 30.2))
        for k in range(6):
            z = -12.6 + k * 5
            L = 2.2 + (k * 7 % 3) * 0.9
            m.c("body", MS2, (10.5 * s, 15.9 - L / 2 + 1, z), (0.4, L, 2.6))
    m.c("body", FR2, (0, 9.2, 0), (17, 0.6, 26))
    # the garden on its back: mossy stones, two torchflowers, a pitcher plant, a sapling
    m.c("body", "mossy_cobblestone", (-5, 23.4, -8), (5, 2.6, 4), (0, 20, 0))
    m.c("body", "mossy_cobblestone", (6, 23, 6), (3.4, 2, 3.4), (0, -15, 0))
    for (x, z) in ((4, -6), (-6, 7)):
        m.c("body", MS2, (x, 24.4, z), (0.5, 4, 0.5))
        for dx, dz in ((0.9, 0), (-0.9, 0), (0, 0.9), (0, -0.9)):
            m.c("body", "orange_concrete", (x + dx, 26.4, z + dz), (1, 1.4, 1))
        m.c("body", "yellow_concrete", (x, 26.6, z), (0.8, 1, 0.8), light=True)
    m.c("body", "lime_concrete", (0, 24.6, -2), (1.4, 5, 1.4))
    for dx in (-1.2, 1.2):
        m.c("body", "light_blue_concrete", (dx, 27.4, -2), (1, 2.6, 1.6), (0, 0, dx * 20))
    m.c("body", "oak_log", (-6, 25.6, 1), (1.4, 7, 1.4))
    m.c("body", "oak_leaves", (-6, 30, 1), (6, 4, 6))
    m.c("body", "oak_leaves", (-6, 32.6, 1), (3.6, 2, 3.6))
    # tail: a short mossy tuft
    m.c("tail", MS, (0, 17, -15.6), (4, 3, 2))
    # head: a big boxy head with a long flat nose, small dark eyes under a fringe of moss
    bevel(m, "head", FR, (0, 16.4, 19), (14, 11, 8), 1.0)
    m.c("head", MS, (0, 22.3, 18.6), (14.4, 1.4, 8.4))
    for s in (1, -1):
        m.c("head", MS2, (5 * s, 21, 23.1), (3, 1.4, 0.3))
        m.c("head", DK, (4 * s, 19.2, 23.1), (1.6, 1.6, 0.2))
        m.c("head", "white_concrete", (4.4 * s, 19.6, 23.2), (0.6, 0.6, 0.1))
    bevel(m, "jaw", NS, (0, 12.4, 25.4), (11, 4, 7), 0.6)
    m.c("jaw", "lime_terracotta", (0, 14.45, 26), (9, 0.2, 5))
    for s in (1, -1):
        m.c("jaw", DK, (2.4 * s, 14.6, 27.2), (1.6, 0.2, 1.0))
    m.attacks = {"roar": "howl", "quake": "rear", "charge": "charge", "poison": "toss"}
    m.melee = "bite"
    return m


@model
def cinderheart():
    """Cinderheart, the magma cube that never cooled: the vanilla magma cube made of eight stacked slices
    of dark crust, each its own piece so they spread apart and show the glowing core when it jumps; a
    blazing orange core, the yellow eyes with red pupils, a ring of black basalt grown round its rim.
    It splits off small magma cubes as it is hurt."""
    m = Model("cinderheart", "slime", 2.4)
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 12, 0))
    m.bone("mouth", "body", (0, 8, 12))
    CR, CR2, MG, GL, EY, BS = "red_nether_bricks", "nether_bricks", "magma_block", "shroomlight", "yellow_concrete", "polished_basalt"
    # the core, glowing between the slices
    m.c("inner", GL, (0, 12, 0), (18, 18, 18), light=True)
    m.c("inner", "orange_concrete", (0, 12, 0), (20.4, 16, 20.4), light=True)
    # eight slices of crust, each its own bone; the hop animation spreads them apart
    hop = {"length": 1.0, "loop": False, "bones": {}}
    for k in range(8):
        b = "slice%d" % k
        y = 1.5 + k * 3
        m.bone(b, "body", (0, y, 0))
        blk = CR if k % 2 == 0 else CR2
        m.c(b, blk, (0, y, 0), (24, 2.4, 24))
        # glowing spots on the crust, a few per slice, always in a different place
        for j in range(3):
            a = (k * 97 + j * 131) % 360
            r = math.radians(a)
            side = (k + j) % 4
            px = [(11.95, (k * 5 + j * 7) % 18 - 9), (-11.95, (k * 3 + j * 11) % 18 - 9)][side % 2]
            if side < 2:
                m.c(b, MG, (px[0], y, px[1]), (0.3, 1.4, 2.4), light=True)
            else:
                m.c(b, MG, (px[1], y, px[0]), (2.4, 1.4, 0.3), light=True)
        spread = (k - 3.5) * 1.6
        hop["bones"][b] = {"pos": anims.K((0, (0, 0, 0)), (0.3, (0, spread, 0)), (0.7, (0, spread, 0)), (1.0, (0, 0, 0)))}
    # a ring of black basalt grown round the top rim, like a crown that grew there
    for k in range(8):
        a = k * math.pi / 4
        m.c("slice7", BS, (math.cos(a) * 11.4, 25.6, math.sin(a) * 11.4), (2.4, 3 + (k % 2) * 2, 2.4), (0, -math.degrees(a), 0))
    # eyes: yellow with red pupils, on the fifth and sixth slices; a dark mouth on the third
    for s in (1, -1):
        m.c("slice5", EY, (5 * s, 16.5, 12.1), (4.6, 2.4, 0.4), light=True)
        m.c("slice5", "red_concrete", (4 * s, 16.5, 12.3), (1.6, 2.0, 0.3), light=True)
        m.c("slice4", EY, (5 * s, 13.5, 12.1), (4.6, 2.4, 0.4), light=True)
        m.c("slice4", "red_concrete", (4 * s, 13.5, 12.3), (1.6, 2.0, 0.3), light=True)
    m.c("slice2", "black_concrete", (0, 7.5, 12.1), (10, 2.4, 0.4))
    m.anims = {"hop": hop}
    m.attacks = {"minions": "burst", "slam": "slam", "volley": "spit", "leap": "hop"}
    m.melee = "slam"
    return m


@model
def shulker_matriarch():
    """The Shulker Matriarch from the oldest End city: a huge purpur shell that opens to show the pale
    yellow head inside, four smaller shulker boxes circling her, and an end rod lamp set on the lid."""
    m = Model("shulker_matriarch", "float", 2.6)
    m.bone("core", "root", (0, 8, 0))
    m.bone("head", "core", (0, 13, 0))
    m.bone("lid", "core", (0, 16, -8))
    m.bone("ring1", "core", (0, 14, 0))
    SH, SH2, HD, DK = "purpur_block", "purple_terracotta", "end_stone", "black_concrete"
    # the lower shell
    m.c("core", SH, (0, 4, 0), (16, 8, 16))
    m.c("core", SH2, (0, 8.2, 0), (16.4, 0.6, 16.4))
    m.c("core", SH2, (0, 0.3, 0), (16.6, 0.6, 16.6))
    # the head inside: pale, two dark eyes, a little mouth
    m.c("head", HD, (0, 12.6, 0), (7, 7, 7))
    for s in (1, -1):
        m.c("head", DK, (1.6 * s, 13.6, 3.55), (1.2, 1.4, 0.2))
    m.c("head", DK, (0, 11.2, 3.55), (2.2, 0.6, 0.2))
    # the lid, hinged at the back so it can open
    m.c("lid", SH, (0, 12.6, 0), (16, 8, 16))
    m.c("lid", SH2, (0, 8.6, 0), (16.4, 0.6, 16.4))
    m.c("lid", SH2, (0, 16.7, 0), (14, 0.4, 14))
    m.c("lid", "end_rod", (0, 19.4, 0), (1, 5, 1), light=True)
    m.c("lid", SH2, (0, 17.2, 0), (2.4, 0.8, 2.4))
    # four small shulker boxes in orbit, each with its own head peeking out
    for k in range(4):
        a = k * math.pi / 2
        x, z = math.cos(a) * 16, math.sin(a) * 16
        y = 14 + (k % 2) * 4
        m.c("ring1", SH, (x, y - 1.2, z), (4, 2.4, 4))
        m.c("ring1", SH, (x, y + 1.4, z), (4, 2.0, 4))
        m.c("ring1", HD, (x, y + 0.1, z), (2.4, 0.8, 2.4))
    m.rest("lid", (-24, 0, 0))
    m.no_elbows = True
    m.attacks = {"orbs": "spin", "levitate": "raise", "shockwave": "pulse", "dive": "dive"}
    m.melee = "pulse"
    return m


@model
def frostmaw():
    """Frostmaw, the great polar bear of the ice spikes: the vanilla polar bear's white fur and black nose,
    huge and scarred, its back crusted with packed ice and icicles, frost on its paws and a salmon still
    caught in its jaw."""
    m = Model("frostmaw", "quad", 2.2)
    quad(m, body_y=14, legx=6, legz_front=9, legz_back=-9, neck_y=17, neck_z=14)
    FU, FU2, IC, IC2, DK = "white_wool", "snow_block", "packed_ice", "blue_ice", "black_concrete"
    for s, (b, z) in ((1, ("legFL", 9)), (-1, ("legFR", 9)), (1, ("legBL", -9)), (-1, ("legBR", -9))):
        x = 6 * s
        bevel(m, b, FU, (x, 8, z), (6, 13, 6.4), 0.8)
        m.c(b, FU2, (x, 1.2, z + 0.8), (6.4, 2.4, 7.6))
        for t in (-1.8, 0, 1.8):
            m.c(b, "gray_concrete", (x + t, 0.6, z + 4.7), (0.8, 1, 1))
    # body: big and round-shouldered, the back crusted with ice and icicles hanging off the flanks
    bevel(m, "body", FU, (0, 17, -1), (14, 12, 26), 1.8)
    bevel(m, "body", FU, (0, 19, 7), (15, 12, 10), 2.0)
    for (x, z, w, d, h) in ((-2, 2, 7, 8, 2), (3, -6, 6, 7, 1.6), (0, 9, 8, 5, 2.2), (-3, -10, 5, 5, 1.4)):
        m.c("body", IC, (x, 23.6 + h / 2, z), (w, h, d))
    for (x, z, h) in ((-1, 3, 4), (2.4, -5, 3), (0.6, 9.4, 5), (-2.4, -10, 2.6)):
        m.c("body", IC2, (x, 24.6 + h / 2, z), (1.4, h, 1.4), (10, 0, x * 5))
    for s in (1, -1):
        for z, L in ((6, 3), (0, 2), (-7, 3.6)):
            m.c("body", IC, (7.1 * s, 11.6 - L / 2 + 2, z), (0.6, L, 1))
        # old claw scars across the flank
        for k in range(3):
            m.c("body", "light_gray_wool", (7.05 * s, 19 - k * 1.6, -2 + k * 1.4), (0.2, 0.6, 5), (0, 0, 0))
    m.c("tail", FU, (0, 18, -14.6), (3, 3, 2))
    # head: the polar bear's head, small ears, a long muzzle with a black nose, dark eyes, a salmon in the jaw
    bevel(m, "head", FU, (0, 18.6, 17.4), (10, 9, 8), 1.0)
    bevel(m, "head", FU2, (0, 16.4, 22.6), (6, 4.6, 4), 0.6)
    m.c("head", DK, (0, 17.8, 24.65), (2.6, 1.6, 0.3))
    for s in (1, -1):
        m.c("head", DK, (3 * s, 20, 21.45), (1.2, 1.2, 0.2))
        m.c("head", FU, (4 * s, 23.8, 16), (2.6, 2, 1.6))
        m.c("head", "light_gray_wool", (4 * s, 23.8, 16.85), (1.4, 1, 0.2))
    m.c("jaw", FU2, (0, 13.6, 22), (5.4, 1.8, 4.6))
    m.c("jaw", "red_concrete", (1, 14.2, 24.4), (8, 1.6, 1.6), (0, 20, 0))
    m.c("jaw", "light_gray_terracotta", (5.2, 14.2, 26.2), (1, 2.6, 1.6), (0, 20, 0))
    m.attacks = {"slam": "rear", "frost": "howl", "charge": "charge", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def bogmaw():
    """Bogmaw, the swamp's giant frog: the vanilla orange frog with its cream belly, big eyes on top of a
    flat head, a wide mouth and the long sticky tongue it shoots out to grab you, a lily pad still stuck on
    its back and mud on its feet."""
    m = Model("bogmaw", "quad", 2.4)
    quad(m, body_y=8, legx=6, legz_front=5, legz_back=-5, neck_y=10, neck_z=6)
    for b in m.bones:
        if b["name"] == "jaw": b["pivot"] = [0, 8, 2]
    m.bone("tongue", "jaw", (0, 8.2, 8))
    SK, SK2, BL, EY, DK, TG = "orange_terracotta", "terracotta", "white_terracotta", "yellow_concrete", "black_concrete", "pink_concrete"
    # legs: folded back legs, short front legs, webbed feet
    for s, (b, z) in ((1, ("legFL", 5)), (-1, ("legFR", 5)), (1, ("legBL", -5)), (-1, ("legBR", -5))):
        x = 6 * s
        if z > 0:
            m.c(b, SK, (x, 3.4, z + 1), (2.6, 5, 2.6))
        else:
            bevel(m, b, SK, (x + 1.2 * s, 4.4, z - 1), (4.6, 6, 8), 0.8)
        m.c(b, SK2, (x + (0 if z > 0 else 1.2 * s), 0.4, z + (2.6 if z > 0 else 1)), (5, 0.8, 4.6))
        m.c(b, "brown_concrete", (x + (0 if z > 0 else 1.2 * s), 0.9, z + (2.6 if z > 0 else 1)), (5.2, 0.3, 4.8))
    # body: a squat flat oval, cream belly, darker speckles on the back, a lily pad stuck on top
    bevel(m, "body", SK, (0, 8.4, -1), (13, 8, 14), 1.6)
    m.c("body", BL, (0, 4.6, 0), (10, 0.6, 11))
    for (x, z) in ((-3, -4), (2.6, -1), (0, -6), (-2, 2)):
        m.c("body", SK2, (x, 12.55, z), (2, 0.3, 2))
    m.c("body", "green_concrete", (2, 12.9, -3), (6, 0.4, 6), (0, 20, 0))
    m.c("body", "lime_concrete", (2, 13.15, -3), (2, 0.2, 2), (0, 20, 0))
    # head: wide and flat, two big eyes up on top, a wide grin
    bevel(m, "head", SK, (0, 9.6, 8.6), (15, 5, 9), 1.0)
    for s in (1, -1):
        bevel(m, "head", SK, (4.6 * s, 13, 8), (4, 3.4, 4), 0.5)
        m.c("head", EY, (4.6 * s, 13.4, 10.05), (2.8, 2.2, 0.3))
        m.c("head", DK, (4.6 * s, 13.2, 10.25), (2.8, 0.8, 0.2))
    m.c("head", DK, (0, 7.6, 13.15), (13, 0.5, 0.3))
    m.c("jaw", BL, (0, 6.4, 8.6), (14, 1.8, 9))
    # the tongue, rolled up in the mouth, reaching out on its own bone when it strikes
    m.c("tongue", TG, (0, 7.6, 10), (2.4, 0.6, 5))
    m.c("tongue", "red_concrete", (0, 7.8, 12.6), (3, 1, 1.4))
    m.attacks = {"pull": "bite", "leap": "pounce", "roar": "howl", "poison": "toss"}
    m.melee = "bite"
    return m


@model
def ramthunder():
    """Ramthunder, the king of the mountain goats: the vanilla goat's white coat and long beard, black
    hooves and a pair of great curled horns, so old that snow and stone have caught in its fleece, with
    an old bell on a rope round its neck that rings when it charges."""
    m = Model("ramthunder", "quad", 2.3)
    quad(m, body_y=15, legx=4.6, legz_front=8, legz_back=-8, neck_y=21, neck_z=12)
    FU, FU2, HN, HN2, HF, DK = "white_wool", "snow_block", "light_gray_concrete", "polished_andesite", "black_concrete", "gray_concrete"
    for s, (b, z) in ((1, ("legFL", 8)), (-1, ("legFR", 8)), (1, ("legBL", -8)), (-1, ("legBR", -8))):
        x = 4.6 * s
        bevel(m, b, FU, (x, 11.6, z), (4.2, 7, 4.2), 0.6)
        m.c(b, FU2, (x, 5.6, z), (3, 6, 3))
        m.c(b, HF, (x, 1.3, z + 0.3), (3.2, 2.6, 3.6))
    # body: a deep shaggy coat that hangs low on the flanks, stones and snow caught in the fleece
    bevel(m, "body", FU, (0, 17.6, 0), (12, 10, 20), 1.6)
    for s in (1, -1):
        for k in range(5):
            z = -8 + k * 4
            L = 3 + (k % 2) * 1.4
            m.c("body", FU, (5.6 * s, 12.6 - L / 2 + 1, z), (1.2, L, 3.4))
    m.c("body", FU2, (0, 22.9, 0), (9, 0.6, 14))
    for (x, z) in ((-2.6, 5), (2, -4)):
        m.c("body", "cobblestone", (x, 23.2, z), (2, 1.2, 2), (0, 30, 0))
    m.c("tail", FU, (0, 21, -10.6), (2, 3, 1.6), (30, 0, 0))
    # head: a long goat head held high, a long beard, small ears, amber eyes with bar pupils
    bevel(m, "head", FU, (0, 24.6, 15), (6.6, 6.6, 9), 0.8)
    m.c("head", FU2, (0, 23, 19.8), (4.4, 3.4, 2))
    m.c("head", DK, (0, 23.8, 20.85), (2.4, 0.8, 0.2))
    for s in (1, -1):
        m.c("head", "orange_concrete", (3.35 * s, 25.4, 16.4), (0.2, 1.2, 1.8))
        m.c("head", HF, (3.45 * s, 25.4, 16.4), (0.1, 0.4, 1.4))
        m.c("head", FU, (4.4 * s, 26.2, 12.4), (2.4, 1, 1.4), (0, 0, -20 * s))
        # the horns: thick, ridged and curling back and out
        horn(m, "head", HN, (2 * s, 28, 14), 5, (-30, 0, -20 * s), (-38, 0, -8 * s), 2.2, 0.86)
    m.c("jaw", FU, (0, 18.6, 18.4), (2.4, 6, 2.4))
    m.c("jaw", FU2, (0, 15.2, 18.6), (1.6, 2, 1.6))
    # an old bell on a rope round the neck
    m.c("head", "brown_wool", (0, 20.4, 12.6), (6.8, 0.8, 6))
    m.c("head", "gold_block", (0, 18.2, 15.2), (2.4, 2.6, 2.4))
    m.c("head", "yellow_concrete", (0, 16.8, 15.2), (2.8, 0.6, 2.8))
    m.attacks = {"charge": "charge", "leap": "rear", "quake": "howl", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def bogged_hunter():
    """The Bogged Hunter, the oldest skeleton of the swamp: the vanilla bogged's mossy grey-green bones and
    skull with glowing sockets, red and brown mushrooms growing out of its head and shoulders, vines and
    moss hanging off it, and a long bow strung with a vine that fires poisoned arrows."""
    m = Model("bogged_hunter", "biped", 2.1)
    biped(m, hip=14, legx=2.4, neck=28, shoulder=26.4, armx=5.4)
    m.bone("bow", "armL", (5.4, 13, 0.4))
    m.hold = {"bow": 0}
    m.bend = -24
    BN, BN2, MS, MS2, RM, BM = "mossy_cobblestone", "tuff", "moss_block", "green_concrete", "red_concrete", "brown_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.4 * s
        m.c(b, BN, (x, 7.4, 0), (1.8, 13, 1.8))
        m.c(b, BN2, (x, 0.8, 0.4), (2.4, 1.6, 3))
        m.c(b, MS, (x, 9, 0), (2.2, 1.2, 2.2))
    m.c("hips", BN, (0, 15, 0), (5, 2, 2.4))
    m.c("body", BN, (0, 21, -0.6), (1.6, 8, 1.6))
    for k in range(4):
        m.c("body", BN, (0, 18.6 + k * 1.8, 0.4), (6.4 - (k == 0) * 1.4, 0.9, 3))
    m.c("body", BN, (0, 26.2, 0), (8, 1.2, 3))
    for (x, z, L) in ((-2.6, 1.8, 5), (2.4, 1.8, 3.4), (0.6, -1.8, 6)):
        m.c("body", MS2, (x, 26 - L / 2, z), (0.6, L, 0.6))
        m.c("body", MS, (x, 25.6 - L, z), (1.2, 0.8, 1.2))
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 5.4 * s
        m.c(a, BN, (x, 20, 0), (1.6, 12, 1.6))
        m.c(a, BN2, (x, 13.4, 0.2), (2.2, 2, 2.2))
        # mushrooms on the shoulders: a red one on the left, a brown one on the right
        m.c(a, "white_terracotta", (x, 27.2, 0), (0.8, 1.4, 0.8))
        m.c(a, RM if s > 0 else BM, (x, 28.2, 0), (3, 0.8, 3))
    m.c("armL", "white_concrete", (5.4, 28.7, 0.8), (0.5, 0.2, 0.5))
    bevel(m, "head", BN, (0, 32, 0.3), (8, 8, 8), 0.4)
    paint(m, "head", "front", (0, 31.6, 4.3), ["........", ".KK..KK.", ".KG..GK.", "...KK...", ".K.KK.K.", "..KKKK.."],
          {"K": "black_concrete", "G": ("lime_concrete", 0.3, True)}, px=1, depth=0.3)
    m.c("head", MS, (0, 36.3, 0.3), (8.4, 0.8, 8.4))
    for (x, z, c, h) in ((-2.4, 1, RM, 2.4), (2, -1.6, BM, 1.8), (0.6, 2.4, RM, 1.4)):
        m.c("head", "white_terracotta", (x, 36.6 + h / 2, z), (0.8, h, 0.8))
        m.c("head", c, (x, 37 + h, z), (3.2 - h * 0.4, 0.9, 3.2 - h * 0.4))
    for x in (-3.4, 3.4):
        m.c("head", MS2, (x, 33, -4.4), (1, 6, 0.4))
    # the bow: a long dark bow held upright in the left hand, strung with a vine
    for k in range(5):
        y = 13 + (k - 2) * 4
        m.c("bow", "dark_oak_log", (5.4, y, 0.4 + abs(k - 2) * -1.0 + 1.6), (1, 4.2, 1), (-(k - 2) * 18, 0, 0))
    m.c("bow", MS2, (5.4, 13, -0.6), (0.3, 16, 0.3))
    m.attacks = {"volley": "cast", "poison": "swipe", "vines": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m
