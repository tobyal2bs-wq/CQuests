"""v4 chapter bosses: one boss after each CQuests chapter. These five are new; Brakka, Sir Oakheart, the
Vault Mimic, the Crypt Knight and the Ember Knight are improved in place in v2_chapters. Each one is a real
Minecraft mob, built big and given the chapter's story."""
import copy
import math
import anims
from models import model, biped, horn, limb, quad, dirof
from v2_general import quad_leg
from build import Model
from kit import paint, band, stack, bevel, crack

SPAWN, DEATH = {}, {}


@model
def nightwing():
    """Chapter 2, Shadows at the Gate: the shadow over the gate was a phantom, the oldest one, that has hunted
    the sleepless for a hundred years. The vanilla phantom's long blue-grey body, ragged wings with pale
    bones, a tail of two fins and the glowing green eyes, grown huge, its wings torn at the edges."""
    m = Model("nightwing", "dragon", 1.8)
    quad(m, body_y=20, legx=3, legz_front=4, legz_back=-4, neck_y=21, neck_z=8)
    for b in m.bones:
        if b["name"] == "tail": b["pivot"] = [0, 20, -9]
        if b["name"] == "jaw": b["pivot"] = [0, 18.6, 10]
    m.mbone("wingL", "body", (4.4, 21.6, 2))
    BD, BD2, MB, MB2, EY = "light_blue_terracotta", "blue_terracotta", "gray_concrete", "light_gray_concrete", "lime_concrete"
    # body: long, flat and narrow, ribbed along the back
    bevel(m, "body", BD, (0, 20.4, -1), (9, 4.6, 18), 1.0)
    for k in range(4):
        m.c("body", BD2, (0, 22.85, 5 - k * 4), (6, 0.3, 1.4))
    m.c("body", MB2, (0, 18.0, -1), (6, 0.3, 14))
    # head: wide and flat, the two glowing green eyes, a jaw full of small teeth
    bevel(m, "head", BD, (0, 20.6, 11.6), (8, 4.6, 7), 0.8)
    for s in (1, -1):
        m.c("head", EY, (2.4 * s, 21.4, 15.15), (2.4, 1.2, 0.3), light=True)
        m.c("head", "white_concrete", (2.0 * s, 21.6, 15.3), (0.8, 0.6, 0.1), light=True)
    m.c("jaw", BD2, (0, 18.1, 12.4), (7, 1.0, 5.4))
    for x in (-2.4, -0.8, 0.8, 2.4):
        m.c("jaw", "white_concrete", (x, 18.85, 14.6), (0.6, 0.6, 0.6))
    # tail: two segments ending in a pair of fins
    m.c("tail", BD, (0, 20.4, -12.4), (5, 3.2, 7))
    m.c("tail", BD, (0, 20.4, -18.6), (3, 2.2, 6))
    for s in (1, -1):
        m.c("tail", MB2, (2.2 * s, 20.4, -23), (3.4, 0.4, 4), (0, 25 * s, 0))
    # wings: an arm bone and three finger bones, grey membrane between them, the trailing edge torn
    def spar(w, a, b, t, blk):
        cx, cy, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        m.c(w, blk, (cx, cy, cz), (t, t, L), (-math.degrees(math.asin(dy / L)), math.degrees(math.atan2(dx, dz)), 0), (cx, cy, cz))
    lead = [(4.4, 6), (16, 5), (28, 2), (34, -2)]
    trail = [(4.4, -7), (10, -12), (14, -9), (20, -13), (25, -8), (30, -9), (34, -2)]
    def zt(x, pts):
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            if x0 <= x <= x1: return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return pts[-1][1]
    for s, w in ((1, "wingL"), (-1, "wingR")):
        spar(w, (4.4 * s, 21.8, 4), (16 * s, 22.2, 5), 1.6, MB2)
        spar(w, (16 * s, 22.2, 5), (34 * s, 21.6, -2), 1.2, MB2)
        for tx, tz in ((30, -9), (20, -13), (10, -12)):
            spar(w, (16 * s, 22.2, 5), (tx * s, 21.6, tz), 0.8, MB2)
        for k in range(6):
            x0, x1 = 4.4 + k * 4.95, 4.4 + (k + 1) * 4.95
            xm = (x0 + x1) / 2
            f, b = zt(xm, lead), zt(xm, trail)
            m.c(w, MB, (xm * s, 21.5, (f + b) / 2), (x1 - x0 + 0.05, 0.3, f - b))
    m.rest("wingL", (0, 0, 10))
    m.rest("wingR", (0, 0, -10))
    m.attacks = {"dive": "charge", "bite": "bite", "roar": "howl", "minions": "rear"}
    m.melee = "bite"
    return m


@model
def iron_tusk():
    """Chapter 6, The Iron Tusk: a zoglin the raiders caught, chained and armoured, and that turned on them.
    The vanilla zoglin's pale pink hide with rotten patches and bare ribs, its pale green-grey mane, and
    great tusks the smiths capped in iron; an iron face plate bolted on, iron plates down its back and a
    broken chain still hanging from its collar."""
    m = Model("iron_tusk", "quad", 1.9)
    quad(m, body_y=14, legx=5.6, legz_front=8, legz_back=-8, neck_y=16, neck_z=12)
    HD, HD2, RT, MN, IR, IR2, BN = "white_terracotta", "pink_terracotta", "lime_terracotta", "light_gray_wool", "iron_block", "polished_andesite", "bone_block"
    for s, (b, z) in ((1, ("legFL", 8)), (-1, ("legFR", 8)), (1, ("legBL", -8)), (-1, ("legBR", -8))):
        x = 5.6 * s
        bevel(m, b, HD, (x, 9.4, z), (5, 9, 5), 0.6)
        m.c(b, HD2, (x, 3.4, z + 0.2), (4.4, 4, 4.4))
        m.c(b, "gray_concrete", (x, 0.8, z + 0.6), (5, 1.6, 5.6))
        m.c(b, IR2, (x, 3.6, z + 2.4), (3.4, 2.4, 0.4))
    # body: the barrel of pale hide, a rotten patch on the flank with bare ribs showing
    bevel(m, "body", HD, (0, 15.6, 0), (12, 10, 20), 1.8)
    for s in (1, -1):
        m.c("body", RT, (6.05 * s, 14.6, -2), (0.3, 5, 7))
        for k in range(3):
            m.c("body", BN, (6.25 * s, 14.6, -4.4 + k * 2.4), (0.3, 4.6, 0.8))
    # the mane: pale green-grey bristles running from the head down the spine
    for k in range(7):
        m.c("body", MN, (0, 21.3 + (k % 2) * 0.6, 9 - k * 2.9), (2, 2.6 + (k % 2), 2.4), (-15, 0, 0))
    # iron plates down the back, riveted, and a chain collar with the broken chain hanging
    for k, z in enumerate((3, -2, -7)):
        bevel(m, "body", IR if k % 2 == 0 else IR2, (0, 20.8, z), (11, 1.2, 4.4), 0.3)
        for s in (1, -1):
            m.c("body", "gray_concrete", (4.6 * s, 21.5, z), (0.6, 0.4, 0.6))
    m.c("body", "chain", (0, 16, 9.8), (12.6, 1.4, 1.4))
    for k in range(4):
        m.c("body", "chain", (3 + k * 0.2, 14.6 - k * 1.4, 10.4 + k * 0.4), (0.8, 1.4, 0.8), (k * 15, 0, 0))
    m.c("tail", HD, (0, 17, -10.6), (1.4, 4, 1.4), (30, 0, 0))
    # head: long and low, pale, the iron face plate bolted on, small white eyes, iron-capped tusks
    bevel(m, "head", HD, (0, 15.6, 16.6), (10, 8, 10), 1.0)
    bevel(m, "head", HD2, (0, 13.6, 22.4), (7, 4, 3), 0.6)
    for s in (1, -1):
        m.c("head", "black_concrete", (1.6 * s, 13.6, 23.95), (1, 1.2, 0.2))
        m.c("head", "white_concrete", (4 * s, 17.4, 21.65), (1.4, 1, 0.2))
        m.c("head", "red_concrete", (4.3 * s, 17.4, 21.8), (0.6, 0.6, 0.1))
        m.c("head", MN, (4.4 * s, 20.4, 13), (2, 2, 3), (0, 0, -25 * s))
        # tusks: pale bone with iron caps, curving up
        m.c("head", BN, (4.6 * s, 13.6, 22), (1.4, 3.4, 1.4), (-20, 0, -12 * s))
        m.c("head", IR, (5.2 * s, 16.2, 23), (1.8, 2.2, 1.8), (-20, 0, -12 * s))
    m.c("head", IR, (0, 19.9, 18.6), (8, 0.6, 7))
    m.c("head", IR2, (0, 18.6, 21.75), (6, 3.2, 0.4))
    for s in (1, -1):
        m.c("head", "gray_concrete", (2 * s, 19.6, 21.95), (0.6, 0.6, 0.1))
    m.c("jaw", HD2, (0, 11.6, 18.4), (7, 1.8, 7))
    m.attacks = {"charge": "charge", "toss": "toss", "quake": "rear", "minions": "howl"}
    m.melee = "bite"
    return m


@model
def deep_mother():
    """Chapter 7, Tides of the Drowned: the drowned were only her children. The Deep Mother is a glow squid
    grown as big as a ship: the vanilla glow squid's teal body lit with glowing spots, big pale eyes, and
    eight tentacles that sway on their own and reach for you."""
    m = Model("deep_mother", "float", 2.6)
    m.bone("core", "root", (0, 18, 0))
    m.bone("head", "core", (0, 18, 0))
    BD, BD2, GL, GL2, EY = "cyan_concrete", "warped_wart_block", "light_blue_concrete", "sea_lantern", "white_concrete"
    # the mantle: tall and rounded, glowing spots scattered over it
    bevel(m, "head", BD, (0, 24, 0), (12, 16, 12), 1.4)
    m.c("head", BD, (0, 32.6, 0), (9, 1.4, 9))
    for face, c in (("front", (0, 26, 6)), ("back", (0, 26, -6)), ("left", (6, 26, 0)), ("right", (-6, 26, 0))):
        paint(m, "head", face, c, ["..G...", "....G.", ".G....", "...G..", "G....G"], {"G": (GL, 0.3, True)}, px=1.8, depth=0.3)
    # the eyes: big, pale and glowing a little, low on the mantle
    for s in (1, -1):
        m.c("head", EY, (3 * s, 19.4, 6.1), (3, 3, 0.3), light=True)
        m.c("head", "black_concrete", (3.4 * s, 19.4, 6.3), (1.2, 1.8, 0.2))
    m.c("head", BD2, (0, 16.6, 0), (12.6, 1.4, 12.6))
    # eight tentacles round the bottom, each its own bone, in two lengths
    idle = copy.deepcopy(anims.RIGS["float"]["idle"])
    for i in range(8):
        a = i * math.pi / 4
        x, z = math.cos(a) * 4.6, math.sin(a) * 4.6
        b = "tent%d" % i
        m.bone(b, "head", (x, 16, z))
        L = 14 if i % 2 == 0 else 10
        m.c(b, BD, (x, 16 - L * 0.3, z), (2.2, L * 0.6, 2.2))
        m.c(b, BD2, (x, 16 - L * 0.8, z), (1.6, L * 0.4, 1.6))
        m.c(b, GL, (x * 1.2, 16 - L * 0.5, z * 1.2), (0.6, 0.6, 0.6), light=True)
        ax, az = math.sin(a) * 18, -math.cos(a) * 18
        sg = 1 if i % 2 == 0 else -1
        idle["bones"][b] = {"rot": anims.K((0, (ax * sg, 0, az * sg)), (1.5, (-ax * sg, 0, -az * sg)), (3.0, (ax * sg, 0, az * sg)))}
    m.anims = {"idle": idle}
    m.no_elbows = True
    m.attacks = {"darkness": "pulse", "pull": "raise", "levitate": "spin", "dive": "dive"}
    m.melee = "pulse"
    return m


@model
def bellwarden():
    """Chapter 9, The Bone Choir: the skeleton who rang the bell that woke the dead. A tall skeleton with the
    vanilla skeleton's square skull and dark sockets, in a ragged black choir robe with a red stole, carrying
    the old village bell on its back in a frame of bones, and the bell rope wound round its fist."""
    m = Model("bellwarden", "biped", 2.0)
    biped(m, hip=14, legx=2.4, neck=28, shoulder=26.4, armx=5.6)
    m.bone("bell", "body", (0, 27, -4))
    m.bend = -30
    BN, BN2, RB, RB2, ST, GD = "bone_block", "calcite", "black_wool", "gray_wool", "red_wool", "gold_block"
    # legs: thin bones under the robe's torn hem
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.4 * s
        m.c(b, BN, (x, 6, 0), (1.6, 12, 1.6))
        m.c(b, BN2, (x, 0.8, 0.6), (2.2, 1.6, 3))
    # the robe: long, black and torn at the hem, a red stole hanging from the shoulders
    m.c("hips", RB, (0, 14, 0), (8, 4, 5))
    for k, L in enumerate((5, 3.4, 6, 4, 5.4)):
        m.c("hips", RB if k % 2 else RB2, (-3.2 + k * 1.6, 12 - L / 2, 2.3), (1.5, L, 0.5))
        m.c("hips", RB if k % 2 == 0 else RB2, (-3.2 + k * 1.6, 12 - L / 2, -2.3), (1.5, L, 0.5))
    bevel(m, "body", RB, (0, 21, 0), (8, 11, 4.8), 0.5)
    m.c("body", "black_concrete", (0, 23.4, 2.45), (3.4, 5, 0.2))
    for k in range(3):
        m.c("body", BN, (0, 21.6 + k * 1.4, 2.6), (3, 0.6, 0.3))
    for s in (1, -1):
        m.c("body", ST, (2.2 * s, 21, 2.55), (1.4, 12, 0.3))
        m.c("body", GD, (2.2 * s, 15.6, 2.7), (1.4, 0.8, 0.3))
    # arms: bone arms in torn sleeves, the bell rope wound round the right fist
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 5.6 * s
        m.c(a, RB, (x, 24, 0), (3, 5, 3))
        m.c(a, RB2, (x, 21, 0.2), (3.2, 1.4, 3.2))
        m.c(a, BN, (x, 17, 0.2), (1.4, 7, 1.4))
        m.c(a, BN2, (x, 13, 0.2), (2, 2, 2))
    m.c("armR", "brown_wool", (-5.6, 13, 0.2), (2.4, 1, 2.4))
    for k in range(3):
        m.c("armR", "brown_wool", (-5.2 + k * 0.4, 12 + k * 2, -1.4 - k * 0.8), (0.6, 2.4, 0.6), (30, 0, -10))
    # the skull: square and white, deep black sockets and nose, a grim set of teeth
    bevel(m, "head", BN2, (0, 32, 0.4), (8, 8, 8), 0.4)
    paint(m, "head", "front", (0, 31.6, 4.4), ["........", ".KK..KK.", ".KK..KK.", "...KK...", ".K.KK.K.", "..KKKK.."],
          {"K": "black_concrete"}, px=1, depth=0.3)
    m.c("head", RB, (0, 36.4, 0), (8.6, 1.4, 8.6))
    m.c("head", RB, (0, 33, -4), (8.6, 7.4, 1))
    # the bell on its back in a frame of bones: gold body, a dark mouth, a lip
    for s in (1, -1):
        m.c("bell", BN, (4.4 * s, 31, -5.4), (1.2, 13, 1.2))
    m.c("bell", BN, (0, 37.4, -5.4), (10, 1.2, 1.2))
    m.c("bell", GD, (0, 34.4, -5.4), (4, 4, 4))
    m.c("bell", GD, (0, 31, -5.4), (6, 3, 6))
    m.c("bell", "yellow_concrete", (0, 29.2, -5.4), (7, 0.8, 7))
    m.c("bell", "black_concrete", (0, 28.8, -5.4), (5.4, 0.2, 5.4))
    m.c("bell", "chain", (0, 36.6, -5.4), (0.6, 1.2, 0.6))
    m.attacks = {"bell": "slam", "hymn": "cast", "minions": "roar", "charge": "sweep"}
    m.melee = "swipe"
    return m


@model
def the_shrieker():
    """Chapter 10, The Listener Below: the deep dark's alarm, grown legs. A great crawling mass of sculk with
    a sculk shrieker for a head, its bone jaws open round a soul light that screams, sculk sensors sprouting
    from its back with glowing tendrils that twitch at every sound, and a sculk catalyst for a heart."""
    m = Model("the_shrieker", "quad", 2.1)
    quad(m, body_y=10, legx=8, legz_front=6, legz_back=-7, neck_y=13, neck_z=9)
    SK, DK, BN, BN2, GL, GL2 = "sculk", "black_concrete", "calcite", "bone_block", "cyan_concrete", "light_blue_concrete"
    # legs: low and wide-set, crooked, like something that crawls
    for s, (b, z) in ((1, ("legFL", 6)), (-1, ("legFR", 6)), (1, ("legBL", -7)), (-1, ("legBR", -7))):
        x = 8 * s
        m.c(b, SK, (x + 1.6 * s, 9, z), (6, 3.4, 4), (0, 0, -25 * s))
        m.c(b, SK, (x + 3.6 * s, 4, z), (3.6, 8, 3.6))
        m.c(b, DK, (x + 3.6 * s, 0.4, z + 0.6), (4.4, 0.8, 5))
    # body: a low, broad mound of sculk, a glowing catalyst set in the middle of the back
    bevel(m, "body", SK, (0, 10.6, -0.6), (16, 8, 18), 1.6)
    m.c("body", "sculk_catalyst", (0, 15.6, -1), (6, 3, 6), light=True)
    m.c("body", GL, (0, 17.2, -1), (3, 0.3, 3), light=True)
    # sensors: small blocks with two glowing tendrils each, sprouting from the back
    for (x, z) in ((-5, 4), (5, 3), (-4.6, -6), (5.4, -5.6)):
        m.c("body", SK, (x, 15.4, z), (3, 1.6, 3))
        for d in (-0.6, 0.6):
            m.c("body", GL, (x + d, 17.4, z), (0.5, 2.6, 0.5), (0, 0, d * 20), light=True)
    # the head is a sculk shrieker: a sculk base, four bone jaws round a soul light
    m.c("head", SK, (0, 12, 12.4), (9, 4, 7))
    m.c("head", GL2, (0, 14.4, 12.4), (4.6, 1.2, 4.6), light=True)
    m.c("head", "sea_lantern", (0, 15, 12.4), (2.4, 1.2, 2.4), light=True)
    for (dx, dz) in ((-2.8, -2.4), (2.8, -2.4), (-2.8, 2.6), (2.8, 2.6)):
        m.c("head", BN, (dx, 16.4, 12.4 + dz), (1.4, 5, 1.4), (dz * 6, 0, -dx * 6))
        m.c("head", BN2, (dx * 1.2, 19, 12.4 + dz * 1.2), (1.0, 1.4, 1.0), (dz * 10, 0, -dx * 10))
    m.c("jaw", BN, (0, 10, 15.4), (7, 1.4, 2.4))
    m.attacks = {"sonic": "howl", "pounce": "pounce", "darkness": "rear", "minions": "toss"}
    m.melee = "bite"
    return m


@model
def ember_knight():
    """Chapter 8, The Ember Court: the court's champion is a wither skeleton, the tallest in the fortress. The
    vanilla wither skeleton's charcoal bones and black skull with its dark sockets, in pieces of gilded
    blackstone armour taken from the bastion (a crowned helm, one heavy pauldron, a breastplate and a belt
    with a gold buckle), embers glowing in the cracks of the stone, and the stone sword every wither
    skeleton carries, grown into a greatsword."""
    m = Model("ember_knight", "biped", 1.7)
    biped(m, hip=15, legx=2.6, neck=31, shoulder=29.4, armx=6.4)
    m.bone("sword", "armR", (-6.4, 13.4, 0.4))
    m.hold = {"sword": 30}
    m.bend = -34
    BN, BN2, DK, BS, BS2, GD, EM = "gray_concrete", "polished_deepslate", "black_concrete", "polished_blackstone", "gilded_blackstone", "gold_block", "orange_concrete"
    # legs: charcoal bones, blackstone greaves with ember cracks
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.6 * s
        m.c(b, BN, (x, 11.4, 0), (1.8, 7, 1.8))
        bevel(m, b, BS, (x, 4.4, 0.3), (3.4, 7, 3.8), 0.4)
        m.c(b, BN2, (x, 0.8, 0.8), (3.6, 1.6, 4.8))
        m.c(b, EM, (x + 0.4 * s, 5, 2.25), (0.4, 2.6, 0.2), light=True)
    # hips and belt: a dark pelvis, a blackstone belt with a gold buckle, a torn black tabard
    m.c("hips", BN, (0, 15.6, 0), (5, 2, 2.4))
    band(m, "hips", BS, (0, 17.4, 0), (8, 1.6, 4.6))
    m.c("hips", GD, (0, 17.4, 2.45), (2, 1.8, 0.3))
    for z in (2.4, -2.4):
        m.c("hips", DK, (0, 13.4, z), (3.6, 6, 0.4))
        m.c("hips", DK, (-0.8, 9.8, z), (1.4, 1.4, 0.4))
    # torso: spine and ribs, a blackstone breastplate over them, gold trim, ember cracks
    m.c("body", BN, (0, 21, -0.6), (1.6, 7, 1.6))
    for k in range(3):
        m.c("body", BN, (0, 19.4 + k * 1.6, 0.4), (6 - k * 0.3, 0.8, 3))
    bevel(m, "body", BS, (0, 25.6, 0.2), (8.4, 5.6, 4.8), 0.6)
    m.c("body", GD, (0, 23, 2.65), (8.6, 0.5, 0.2))
    crack(m, "body", "front", (0, 26, 2.6), [(-2.4, 1.6), (-0.6, 1.6), (-0.6, -0.4), (1.4, -0.4), (1.4, -1.6)], EM, 0.4, 0.2)
    # the heavy pauldron on the left shoulder: gilded blackstone, three plates, a gold rim
    bevel(m, "armL", BS2, (7.2, 29.6, 0), (5.6, 3.4, 5.6), 0.6)
    m.c("armL", BS, (7.8, 27.6, 0), (5.6, 1.6, 5.8))
    m.c("armL", GD, (7.8, 26.7, 0), (5.8, 0.4, 6))
    m.c("armL", EM, (9.9, 29.6, 1), (0.2, 0.4, 2.4), light=True)
    # arms: long charcoal bones, dark hands; the right is bare to the shoulder
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6.4 * s
        m.c(a, BN, (x, 24, 0), (1.8, 8, 1.8))
        m.c(a, BN2, (x, 19.4, 0.2), (2.2, 1.6, 2.2))
        m.c(a, BN, (x, 16, 0.3), (1.6, 6, 1.6))
        m.c(a, DK, (x, 13, 0.4), (2.2, 2.2, 2.2))
    m.c("armR", BS, (-6.6, 29, 0), (3.4, 2.4, 3.4))
    # the skull: the black wither skull, square, deep sockets with a faint ember light, grim teeth
    bevel(m, "head", "black_concrete", (0, 35, 0.3), (8, 8, 8), 0.4)
    paint(m, "head", "front", (0, 34.6, 4.3), ["........", ".GG..GG.", ".GE..EG.", "...GG...", ".G.GG.G.", "..GGGG.."],
          {"G": BN, "E": (EM, 0.3, True)}, px=1, depth=0.3)
    # the crowned helm of the court: a blackstone band with gold points over the skull
    m.c("head", BS, (0, 38.4, 0.3), (8.6, 1.6, 8.6))
    m.c("head", GD, (0, 37.7, 4.6), (8.6, 0.4, 0.2))
    for k, x in enumerate((-3.4, -1.2, 1.2, 3.4)):
        h = 2.6 if k in (1, 2) else 1.8
        m.c("head", BS2, (x, 39.2 + h / 2, 4.2), (1.2, h, 0.6))
        m.c("head", BS2, (x, 39.2 + h / 2, -3.6), (1.2, h, 0.6))
    # the greatsword: the stone sword grown huge, a dark wooden grip, a chipped grey blade
    m.c("sword", "dark_oak_log", (-6.4, 13.4, 0.4), (1.1, 4.4, 1.1))
    m.c("sword", "stone", (-6.4, 16.2, 0.4), (1.4, 1.2, 5))
    bevel(m, "sword", "stone", (-6.4, 25.4, 0.4), (0.9, 17, 3), 0.3)
    m.c("sword", "cobblestone", (-6.4, 33.6, 0.4), (0.9, 1.6, 1.8), (45, 0, 0))
    m.c("sword", "polished_andesite", (-6.4, 22, 1.95), (0.95, 3, 0.1))
    m.c("sword", EM, (-6.4, 28, -1.15), (0.95, 2.4, 0.1), light=True)
    m.attacks = {"sword": "sweep", "fire": "cast", "slam": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m
