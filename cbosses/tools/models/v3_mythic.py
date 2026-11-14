"""v3 mythic bosses: the Warden, the Wither and the Ender Dragon, rebuilt as the biggest and most
detailed bosses on the server. Each one keeps the silhouette every player knows and pushes it further."""
import math
from models import model, biped, horn, limb, quad, dirof
from v2_general import quad_leg
from build import Model
from kit import paint, band, stack, bevel, crack
from v3_kit import grow, vines

SPAWN, DEATH = {}, {}


@model
def the_listener():
    """The Warden as a myth: the vanilla Warden's exact shape (short legs, long heavy arms, a broad chest
    and a big eyeless head with two flat tendrils) at three times the size, in its own dark navy and teal.
    The ribcage on its chest is open over the trapped souls, which glow and pulse; the deep dark has grown
    over its shoulders, with sculk shriekers and sensors rooted in its back."""
    m = Model("the_listener", "biped", 2.6)
    biped(m, hip=13, legx=5.9, neck=34, shoulder=32, armx=13)
    m.bone("jaw", "head", (0, 38, 4))
    m.bone("heart", "body", (0, 26, 3))
    m.mbone("tendrilL", "head", (7, 47.5, 0))
    m.bend = -16
    NV, NV2, DK, TL, TL2, GL, GL2, BN = ("sculk", "black_concrete", "black_concrete", "cyan_terracotta",
                                        "calcite", "cyan_concrete", "light_blue_concrete", "bone_block")
    # legs: short pillars, the vanilla 6 x 13, with a darker foot and a teal vein on the shin
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5.9 * s
        bevel(m, b, NV, (x, 7.4, 0), (6.6, 11.4, 6.6), 0.8)
        bevel(m, b, NV2, (x, 1.1, 0.6), (7.6, 2.2, 8.2), 0.5)
        crack(m, b, "front", (x, 7, 3.3), [(-1.2, 4), (-1.2, 0.6), (0.8, 0.6), (0.8, -3.6)], GL, 0.6, 0.25)
    # torso: a narrower belly, a broad chest that rolls into heavy shoulders
    bevel(m, "hips", NV, (0, 15, 0), (15, 4, 9.4), 0.8)
    bevel(m, "body", NV, (0, 20.4, 0), (16, 7, 10), 1.0)
    bevel(m, "body", NV, (0, 28.4, -0.2), (18, 10, 11), 1.4)
    for s in (1, -1):
        bevel(m, "body", NV, (7.8 * s, 32.4, -0.6), (6.4, 3.6, 10.4), 1.0)
    # the open ribcage: a dark hollow, the soul heart inside, pale ribs and a breastbone over it
    m.c("body", DK, (0, 26.6, 5.1), (11.6, 11, 0.6))
    for k in range(4):
        y = 22.4 + k * 2.8
        for s in (1, -1):
            m.c("body", TL2, (3.3 * s, y, 5.75), (4.6 - (k == 3) * 0.8, 1.0, 1.0), (0, 0, -8 * s))
            m.c("body", TL, (6.1 * s, y - 0.3, 5.3), (1.2, 1.0, 1.0))
    m.c("body", TL2, (0, 26.8, 5.85), (1.6, 11.2, 1.0))
    bevel(m, "heart", GL, (0, 26.6, 4.9), (7.4, 7.4, 1.2), 0.6, light=True)
    m.c("heart", "sea_lantern", (0, 26.6, 5.2), (4, 4, 1.0), light=True)
    # souls: small lit faces caught between the ribs
    for (x, y) in ((-3.8, 23.8), (3.4, 29.4), (-3.2, 29.2), (3.8, 23.6)):
        m.c("heart", GL2, (x, y, 5.45), (1.6, 1.4, 0.3), light=True)
        m.c("heart", DK, (x, y + 0.1, 5.62), (0.9, 0.3, 0.1))
    # the deep dark grown over it: sculk crust on the shoulders, shriekers and sensors in the back
    for s, side in ((1, "left"), (-1, "right")):
        grow(m, "body", side, (9 * s, 29, -0.2), 5, 5, 320 + s, {"A": TL, "B": NV2}, cover=0.6, top=0.9, edge={"t"}, px=2, depth=0.3)
    grow(m, "body", "back", (0, 27, -5.55), 9, 7, 311, {"A": TL, "B": NV2}, cover=0.45, top=0.8, px=2, depth=0.4)
    for s, (x, z) in ((1, (7.2, -3.4)), (-1, (-5.4, -4.6))):
        y = 34.2
        bevel(m, "body", NV2, (x, y + 0.6, z), (5, 1.6, 5), 0.4)
        for dx, dz in ((-1.6, -1.6), (1.6, -1.6), (-1.6, 1.6), (1.6, 1.6)):
            m.c("body", BN, (x + dx, y + 2.6, z + dz), (1.0, 2.6, 1.0), (dz * 6, 0, -dx * 6))
        m.c("body", GL, (x, y + 1.5, z), (2.4, 0.4, 2.4), light=True)
    for (x, y) in ((-5, 29), (5.6, 23.6)):
        m.c("body", NV2, (x, y, -6.0), (3, 2, 1.2))
        for d in (-0.8, 0.8):
            m.c("body", GL, (x + d, y + 0.6, -7.1), (0.5, 0.5, 2.6), (-35, 0, 0), light=True)
    for k in range(4):
        m.c("body", NV2, (0, 33 - k * 3.4, -5.9), (2.6 - k * 0.3, 2.2, 1.4), (-12, 0, 0))
    # arms: the vanilla 8 x 28, heavy fists, teal veins, the shoulder joint crusted with sculk
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 13 * s
        bevel(m, a, NV, (x, 27.4, 0), (8, 11, 8), 1.0)
        bevel(m, a, NV2, (x, 32.6, -0.2), (8.8, 2.6, 8.8), 0.6)
        bevel(m, a, NV, (x, 15.6, 0.2), (7.6, 11, 7.6), 0.9)
        crack(m, a, "front", (x, 16, 3.9), [(-1.6, 4.6), (-1.6, 0.6), (1, 0.6), (1, -4)], GL, 0.6, 0.25)
        crack(m, a, "left" if s > 0 else "right", (x + 3.8 * s, 26, 0), [(1.4, 4), (1.4, -1), (-1.2, -1), (-1.2, -4)], GL, 0.6, 0.25)
        bevel(m, a, NV2, (x, 7.4, 0.4), (8.6, 5.6, 8.6), 1.0)
        for t in (-2.6, 0, 2.6):
            m.c(a, TL, (x + t, 8.6, 4.85), (1.6, 1.4, 0.6))
    # head: the big square eyeless head, cheeks glowing, a wide dark mouth with a jaw that drops
    bevel(m, "head", NV, (0, 43, 0.4), (16, 10, 10), 1.2)
    # no eyes: a smooth dark brow, and the soul light seen through the cheeks
    m.c("head", NV2, (0, 45.6, 5.5), (12, 1.4, 0.4))
    for s in (1, -1):
        m.c("head", GL, (5.2 * s, 41.6, 5.5), (2.4, 1.0, 0.3), light=True)
        m.c("head", GL2, (6.4 * s, 43.0, 5.5), (1.0, 1.0, 0.3), light=True)
    m.c("jaw", GL, (0, 37.6, 4.5), (8, 0.8, 0.6), light=True)
    bevel(m, "jaw", NV, (0, 36.4, 0.8), (15, 4, 9), 0.8)
    m.c("jaw", DK, (0, 37.6, 5.0), (11, 1.8, 0.8))
    m.c("jaw", TL2, (0, 36.0, 5.3), (11.6, 1.0, 0.6))
    m.c("head", DK, (0, 39.4, 5.1), (11, 1.6, 0.8))
    m.rest("body", (8, 0, 0))
    m.rest("head", (-8, 0, 0))
    # tendrils: two broad flat lobes off the top corners of the head, lit teal on the inside face
    for s, b in ((1, "tendrilL"), (-1, "tendrilR")):
        o = (7 * s, 47.5, 0)
        for (cx, cy, w, h) in ((5.4, 3.2, 8, 6.4), (9.6, 7.4, 5, 5)):
            c = (7 * s + cx * s, 47.5 + cy, 0)
            m.c(b, NV, c, (w, h, 1.6), (0, 0, -24 * s), o)
            m.c(b, GL, (c[0], c[1], 0.95), (w - 2, h - 2, 0.3), (0, 0, -24 * s), o, light=True)
            m.c(b, GL, (c[0], c[1], -0.95), (w - 2, h - 2, 0.3), (0, 0, -24 * s), o, light=True)
    m.attacks = {"sonic_boom": "roar", "slam": "slam", "quake": "stomp", "darkness": "cast"}
    m.melee = "swipe"
    return m


def wither_skull(m, bone, c, w, base, shade, dark, glow, crown=None, star=False):
    """A wither skull the vanilla way, every face painted: a charcoal head, a grey brow ridge over two
    deep sockets with a soul light inside, a dark nose and a crooked row of grey teeth; the sides and back
    cracked. crown adds the black spikes of the great middle skull."""
    x, y, z = c
    bevel(m, bone, base, c, (w, w, w), w * 0.06)
    p = w / 8
    paint(m, bone, "front", (x, y, z + w / 2), [
        "........",
        ".HH..HH.",
        ".DD..DD.",
        ".DG..GD.",
        "...NN...",
        ".TTTTTT.",
        ".DTDTDT.",
        "........",
    ], {"D": dark, "G": (glow, 0.3, True), "T": shade, "H": shade, "N": dark}, px=p, depth=0.3)
    for side in ("left", "right"):
        sx = x + (w / 2 if side == "left" else -w / 2)
        paint(m, bone, side, (sx, y, z), ["........", "......S.", ".....SS.", "..S.....", ".SS.....", "........", "....S...", "........"],
              {"S": shade}, px=p, depth=0.25)
    m.c(bone, dark, (x, y - w / 2 + p / 2, z + w * 0.1), (w * 0.8, p, w * 0.7))
    if crown:
        for k in range(5):
            t = k / 4 - 0.5
            h = w * (0.7 if k == 2 else 0.5 if k % 2 == 0 else 0.34)
            m.c(bone, crown, (x + t * w * 0.82, y + w / 2 + h / 2, z + w * 0.18), (p * 1.2, h, p * 1.2), (-10, 0, -t * 36))
    if star:
        # the nether star it carries, set in the forehead and burning white
        m.c(bone, "white_concrete", (x, y + w * 0.36, z + w / 2 + 0.25), (p * 1.4, p * 1.4, 0.3), (0, 0, 45), light=True)
        m.c(bone, "yellow_concrete", (x, y + w * 0.36, z + w / 2 + 0.45), (p * 0.6, p * 0.6, 0.2), (0, 0, 45), light=True)


@model
def withered_tyrant():
    """The Wither, true to the vanilla shape and made huge: a charcoal shoulder beam carrying three
    skulls (the great crowned one in the middle with the nether star in its brow), a spine that hangs
    from the beam with three ribs curling round a cold blue heart, and a tail that sweeps back. Soul fire
    burns in every socket and three small skulls circle it, waiting to be fired."""
    m = Model("withered_tyrant", "float", 3.0)
    m.bone("core", "root", (0, 22, 0))
    m.bone("head", "core", (0, 28, 0))
    m.bone("ring1", "core", (0, 20, 0))
    m.bone("ring2", "core", (0, 14, 0))
    m.bone("ring3", "core", (0, 13, -1))
    m.mbone("armL", "core", (10, 26, 0))
    BS, SH, DK, BN, GL, GL2 = "gray_concrete", "light_gray_concrete", "black_concrete", "polished_deepslate", "light_blue_concrete", "cyan_concrete"
    # the shoulder beam, with bone spurs over the side skulls
    bevel(m, "core", BS, (0, 24.5, 0), (22, 3, 3.4), 0.5)
    m.c("core", SH, (0, 25.7, 1.5), (20, 0.5, 0.4))
    for s in (1, -1):
        m.c("core", BN, (6.4 * s, 26.6, -0.4), (1, 2.4, 1), (0, 0, -20 * s))
    # the spine, hanging from the beam and leaning forward a little
    bevel(m, "core", BS, (0, 18.6, -0.4), (3.2, 10, 3.2), 0.4, (8, 0, 0), (0, 23, 0))
    for k in range(4):
        m.c("core", SH, (0, 21.6 - k * 2.4, -2.1), (1.4, 1.0, 0.6), (8, 0, 0), (0, 23, 0))
    # three ribs curling round from the spine to the front, the lowest the shortest
    for k, (y, w) in enumerate(((21.4, 11), (18.8, 10), (16.2, 8))):
        z0 = 0.4 - k * 0.3
        m.c("core", BS, (0, y, z0 - 1.0), (w, 1.6, 1.6))
        for s in (1, -1):
            m.c("core", BS, ((w / 2 - 0.8) * s, y, z0 + 0.8), (1.6, 1.6, 3.6))
            m.c("core", BS, ((w / 2 - 2.2) * s, y, z0 + 2.6), (2.2, 1.4, 1.4))
    # its heart, cold blue between the ribs
    m.c("ring1", GL2, (0, 19, 0.8), (3.2, 4, 2.4), light=True)
    m.c("ring1", GL, (0, 19, 1.0), (1.8, 2.4, 2.4), light=True)
    # the tail: the spine running on and sweeping back to a point
    limb(m, "ring3", BS, (0, 13.6, -1.2), [(4.6, 2.6, (-160, 0, 0)), (4, 2.0, (-140, 0, 0)), (3.4, 1.4, (-120, 0, 0))], joint=BN)
    # the three skulls: the crowned great skull in the middle, two on the beam's ends
    wither_skull(m, "head", (0, 30.6, 0.2), 8.4, BS, SH, DK, GL, crown=DK, star=True)
    for s, a in ((1, "armL"), (-1, "armR")):
        wither_skull(m, a, (10 * s, 29, -0.2), 6.2, BS, SH, DK, GL)
    # three wither skulls circling, each trailing soul fire
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        x, z = math.cos(a) * 15, math.sin(a) * 15
        y = 20 + (k % 2) * 4
        wither_skull(m, "ring2", (x, y, z), 3.2, BS, SH, DK, GL)
        m.c("ring2", GL2, (x - math.sin(a) * 2.4, y, z + math.cos(a) * 2.4), (1.0, 1.0, 1.0), light=True)
        m.c("ring2", GL, (x - math.sin(a) * 3.6, y, z + math.cos(a) * 3.6), (0.6, 0.6, 0.6), light=True)
    m.no_elbows = True
    m.attacks = {"skulls": "spin", "blast": "pulse", "minions": "raise", "charge": "dive"}
    m.melee = "swipe"
    return m


@model
def ender_wyrm():
    """The Ender Dragon, built to its vanilla proportions and made mythic: a long black body with grey
    dorsal plates, a five-joint neck, a long head with a lower jaw lined with teeth and two purple eyes, a
    tail of ten tapering joints, and huge wings on grey finger bones with black membrane between them. An
    end crystal is grown into its chest and burns purple, its eyes trail light and the membrane edges are
    lit with the End's purple."""
    m = Model("ender_wyrm", "dragon", 1.0)
    quad(m, body_y=26, legx=10, legz_front=20, legz_back=-18, neck_y=28, neck_z=28)
    for b in m.bones:
        if b["name"] == "jaw": b["pivot"] = [0, 47, 84]
        if b["name"] == "tail": b["pivot"] = [0, 28, -28]
    m.mbone("wingL", "body", (11, 34, 12))
    BK, BK2, PL, PL2, EY, MB, VN = ("black_concrete", "polished_blackstone", "gray_concrete", "light_gray_concrete",
                                    "magenta_concrete", "black_wool", "purple_concrete")
    # body: long and deep, a dark belly, three dorsal plates, grey scales painted along both flanks
    bevel(m, "body", BK, (0, 26, 0), (22, 20, 56), 2.5)
    for z in (16, 0, -16):
        m.c("body", PL, (0, 38, z), (2.4, 6, 10), (-25, 0, 0))
        m.c("body", PL2, (0, 39.6, z - 1.6), (1.0, 3.6, 6), (-25, 0, 0))
    for side in ("left", "right"):
        x = 11 if side == "left" else -11
        paint(m, "body", side, (x, 27, 0), [
            "..S...S...S...",
            ".S.S.S.S.S.S..",
            "S...S...S...S.",
        ], {"S": BK2}, px=3.6, depth=0.3)
    # the end crystal grown into its chest
    m.c("body", "magenta_stained_glass", (0, 22, 28.4), (7, 7, 1.4), (0, 0, 45), light=True)
    m.c("body", "white_concrete", (0, 22, 28.6), (2.6, 2.6, 1.4), (0, 0, 45), light=True)
    # neck: five joints rising in an S to the head, each with a dorsal plate
    pts = [(28, 30), (35, 35), (43, 39.5), (51, 43), (59, 45), (67, 46)]
    for k, (z, y) in enumerate(pts[1:]):
        bevel(m, "head", BK if k % 2 == 0 else BK2, (0, y, z), (10 - k * 0.3, 10 - k * 0.3, 9), 1.0)
        m.c("head", PL, (0, y + 6.4 - k * 0.2, z - 1), (1.6, 4, 5), (-25, 0, 0))
    # head: a long box skull, a longer snout with nostrils, purple eyes under a grey brow, scale ears
    hz, hy = 79, 49
    bevel(m, "head", BK, (0, hy, hz), (16, 14, 16), 1.6)
    bevel(m, "head", BK, (0, hy - 2.4, hz + 15), (12, 6, 16), 1.0)
    m.c("head", BK2, (0, hy + 0.65, hz + 15), (10, 0.4, 14))
    for s in (1, -1):
        m.c("head", PL, (3 * s, hy + 1.2, hz + 21), (2, 1.4, 3))
        m.c("head", BK, (3 * s, hy + 1.95, hz + 21.4), (1, 0.2, 1.4))
        # eyes: a purple slit with a bright core under a grey brow ridge
        m.c("head", PL, (8.15 * s, hy + 3.4, hz + 3.4), (0.4, 1.4, 6))
        m.c("head", EY, (8.2 * s, hy + 1.4, hz + 3.6), (0.4, 1.6, 4.4), light=True)
        m.c("head", "white_concrete", (8.35 * s, hy + 1.4, hz + 3.8), (0.2, 1.0, 1.4), light=True)
        # the two scale ears at the back of the skull, and mythic horns sweeping back from them
        m.c("head", PL, (4.4 * s, hy + 9, hz - 4), (2, 4, 6), (-30, 0, 0))
        horn(m, "head", PL2, (5.6 * s, hy + 6.8, hz - 6), 4, (-115, 0, -10 * s), (12, 0, 0), 2.2, 0.8)
    for k in range(3):
        m.c("head", PL, (0, hy + 7.6 - k * 0.3, hz + 4 - k * 5), (1.4, 2.6, 3), (-25, 0, 0))
    # the jaw, lit purple inside, teeth on both jaws
    bevel(m, "jaw", BK2, (0, hy - 7.6, hz + 13), (11, 3.2, 18), 0.6)
    m.c("jaw", VN, (0, hy - 5.9, hz + 13), (8, 0.3, 15), light=True)
    for s in (1, -1):
        for k in range(3):
            m.c("jaw", "white_concrete", (4.4 * s, hy - 5.4, hz + 8 + k * 5.4), (0.8, 1.4, 0.8))
            m.c("head", "white_concrete", (4.8 * s, hy - 6, hz + 10.6 + k * 5.4), (0.8, 1.4, 0.8))
    # tail: ten joints, tapering and dipping, each with a plate, ending in a lit purple barb
    y, z = 27, -30
    for k in range(10):
        w = 9 - k * 0.55
        z -= w * 0.95
        y -= 0.6 + k * 0.15
        bevel(m, "tail", BK if k % 2 == 0 else BK2, (0, y, z), (w, w, w), 0.8)
        m.c("tail", PL, (0, y + w / 2 + 1.6, z), (1.2, 3.2 - k * 0.2, w * 0.6), (-25, 0, 0))
    m.c("tail", VN, (0, y, z - 5), (1.6, 1.6, 4), light=True)
    m.c("tail", PL, (0, y, z - 4), (3, 1, 3), (0, 45, 0))
    # legs: short front legs with grey claws, big rear legs
    for s, b, z, big in ((1, "legFL", 20, False), (-1, "legFR", 20, False), (1, "legBL", -18, True), (-1, "legBR", -18, True)):
        x = 10 * s
        w = 9 if big else 6.4
        bevel(m, b, BK, (x, 18, z), (w, 14 if big else 12, w + (2 if big else 0)), 1.0)
        bevel(m, b, BK2, (x, 7.6, z + 1), (w * 0.75, 10, w * 0.75), 0.8)
        bevel(m, b, BK, (x, 1.4, z + 3), (w + 1, 2.8, w * 1.8), 0.6)
        for t in (-0.3, 0, 0.3):
            m.c(b, PL2, (x + t * w, 1, z + 3 + w * 0.95), (1.2, 1.6, 2))
    # wings: an arm bone and forearm to the wrist, four finger bones swept back, black membrane between
    # them in strips that follow the scalloped trailing edge, lit purple along the edge
    def spar(w, a, b, t, blk, light=False):
        cx, cy, cz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        m.c(w, blk, (cx, cy, cz), (t, t, L), (-math.degrees(math.asin(dy / L)), math.degrees(math.atan2(dx, dz)), 0), (cx, cy, cz), light)
    lead = [(11, 12), (40, 10), (70, 4), (84, -6)]
    trail = [(11, -12), (24, -30), (34, -24), (44, -40), (54, -30), (64, -36), (74, -24), (84, -6)]
    def zt(x, pts):
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            if x0 <= x <= x1: return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
        return pts[-1][1]
    for s, w in ((1, "wingL"), (-1, "wingR")):
        sh, el, wr = (11 * s, 34, 12), (40 * s, 36, 10), (70 * s, 34, 4)
        spar(w, sh, el, 4, PL)
        spar(w, el, wr, 3, PL)
        m.c(w, PL2, el, (4.6, 4.6, 4.6))
        m.c(w, PL2, (wr[0], wr[1] + 2.4, wr[2] + 1), (1.6, 5, 1.6), (-20, 0, -12 * s))
        for (tx, tz) in ((84, -6), (64, -36), (44, -40), (24, -30)):
            spar(w, wr if tx > 30 else el, (tx * s, 33.6, tz), 1.6, PL)
        for k in range(9):
            x0, x1 = 11 + k * 8.1, 11 + (k + 1) * 8.1
            xm = (x0 + x1) / 2
            f, b = zt(xm, lead), zt(xm, trail)
            m.c(w, MB, (xm * s, 33.4, (f + b) / 2), (x1 - x0 + 0.05, 0.5, f - b))
            m.c(w, VN, (xm * s, 33.2, b + 0.6), (x1 - x0 + 0.05, 0.5, 1.2), light=True)
    m.rest("wingL", (0, -8, 18))
    m.rest("wingR", (0, 8, -18))
    m.attacks = {"breath": "howl", "charge": "charge", "bite": "bite", "minions": "rear"}
    m.melee = "bite"
    return m
