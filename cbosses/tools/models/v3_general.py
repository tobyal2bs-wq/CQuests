"""v3 normal bosses: each one is a real creature built on vanilla mob proportions, three or four
materials that belong together, and detail painted into its surfaces instead of loose bits."""
from models import model, biped, horn, mhorn, limb, quad
from build import Model
from kit import paint, band, stack, bevel, mirror_rows
from v3_kit import grow, vines, flower, patch_rows, sprinkle

SPAWN, DEATH = {}, {}


@model
def old_ironroot():
    """An iron guardian that stood in the same forest so long the forest grew over it: weathered iron with
    tan rust, moss creeping down from the shoulders, flowering vines, and a young oak growing out of its
    left shoulder. Long golem arms, small head, a heavy brow over two red eyes."""
    m = Model("old_ironroot", "biped", 2.3)
    biped(m, hip=13, legx=4.6, neck=30, shoulder=28.5, armx=11.4)
    m.bone("tree", "body", (8, 31, -1))
    m.no_elbows = True
    IR, RU, JT, MO, MO2, LF = "iron_block", "raw_iron_block", "polished_andesite", "moss_block", "green_terracotta", "flowering_azalea_leaves"
    moss = {"A": MO, "B": MO2}
    rust = {"A": RU, "B": "light_gray_concrete"}
    # legs: plain iron columns on wide feet, a dark knee joint, rust at the shins, moss on one foot
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4.6 * s
        m.c(b, IR, (x, 9.5, 0), (6, 7, 5))
        m.c(b, JT, (x, 5.6, 0), (5, 1.2, 4.4))
        m.c(b, IR, (x, 2.6, 0.2), (6.4, 5.2, 5.6))
        m.c(b, RU, (x, 0.5, 0.4), (7, 1, 6.4))
        grow(m, b, "front", (x, 10, 2.5), 3, 4, 11 + s, rust, cover=0.2, top=0.3, px=2, depth=0.3)
        grow(m, b, "front", (x, 2.6, 3.0), 3, 2, 21 + s, moss if s > 0 else rust, cover=0.25, top=0.2, edge={"b"}, px=2, depth=0.4)
    # waist: a narrow dark joint, then a band of iron
    m.c("hips", JT, (0, 14.2, 0), (8, 2.4, 5.4))
    m.c("hips", IR, (0, 16.8, 0), (10, 3, 6.4))
    # chest: the big iron barrel, rounded front edges, moss pouring over the shoulders
    bevel(m, "body", IR, (0, 24.2, -0.5), (18, 12, 11), 1.2)
    grow(m, "body", "front", (0, 24.2, 5.0), 9, 6, 4, moss, cover=0.42, top=0.85, edge={"t", "r"}, px=2, depth=0.6, flowers="yellow_concrete")
    grow(m, "body", "top", (0, 30.2, -0.5), 9, 6, 5, moss, cover=0.75, top=0.5, px=2, depth=0.6)
    grow(m, "body", "back", (0, 24.2, -6.0), 9, 6, 6, moss, cover=0.5, top=0.9, edge={"t"}, px=2, depth=0.6)
    for s, side in ((1, "left"), (-1, "right")):
        grow(m, "body", side, (9.0 * s, 24.2, -0.5), 6, 6, 7 + s, moss if s > 0 else rust, cover=0.4, top=0.85, edge={"t"}, px=2, depth=0.5)
    grow(m, "body", "front", (-3, 22, 5.0), 3, 2, 9, rust, cover=0.3, top=0.3, px=2, depth=0.3)
    vines(m, "body", (-6.5, -2, 3.5, 7.4), 18.6, 5.4, (5, 8, 3.6, 6.4), MO2, LF)
    flower(m, "body", (5.5, 30.4, 2.5), "yellow_concrete", "orange_concrete", 2.2)
    flower(m, "body", (-6.5, 30.4, -3), "white_concrete", "yellow_concrete", 1.8)
    # arms: long golem arms hanging to the knees, a dark joint at the elbow, big flat fists with knuckles
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11.6 * s
        bevel(m, a, IR, (x, 26.6, 0), (5, 5, 6.4), 0.6)
        m.c(a, IR, (x, 20.8, 0), (4.4, 7, 5.4))
        m.c(a, JT, (x, 16.6, 0), (3.8, 1.4, 4.8))
        m.c(a, IR, (x, 11.4, 0), (4.6, 9, 5.6))
        bevel(m, a, IR, (x, 4.6, 0.3), (5.4, 5, 6.4), 0.7)
        for k in range(3):
            m.c(a, JT, (x, 2.2, 2.2 - k * 1.9), (5.6, 0.6, 1.2))
        grow(m, a, "left" if s > 0 else "right", (x + 2.3 * s, 22, 0), 3, 5, 30 + s, moss if s > 0 else rust, cover=0.45, top=0.9, edge={"t"}, px=2, depth=0.4)
        grow(m, a, "front", (x, 12, 2.85), 2, 5, 33 + s, rust if s > 0 else moss, cover=0.3, top=0.4, px=2, depth=0.3)
        grow(m, a, "top", (x, 29.1, 0), 2, 3, 35 + s, moss, cover=0.9, px=2, depth=0.5)
    vines(m, "armR", (1.6, -0.4, -2.2), 21, -14.4, (6, 9, 4), MO2, LF, face_z=False)
    vines(m, "armL", (-1.2, 1.4), 21, 14.4, (4, 7), MO2, LF, face_z=False)
    # head: small and set forward, a long nose, a heavy brow over red eyes, moss growing on the crown
    bevel(m, "head", IR, (0, 35.2, 2.2), (8, 10, 8), 0.6)
    paint(m, "head", "front", (0, 35.6, 6.25), [
        "BBBBBBBB",
        ".BB..BB.",
        ".KR..RK.",
        "........",
        "........",
    ], {"B": "gray_concrete", "K": "black_concrete", "R": ("red_concrete", 0.3, True)}, px=1, depth=0.3)
    m.c("head", IR, (0, 32.4, 7.2), (2, 4, 2))
    m.c("head", RU, (0, 30.8, 7.2), (2, 0.8, 2))
    grow(m, "head", "top", (0, 40.2, 2.2), 4, 4, 41, moss, cover=0.9, px=2, depth=0.6)
    grow(m, "head", "back", (0, 36.5, -1.8), 4, 4, 42, moss, cover=0.5, top=0.9, edge={"t"}, px=2, depth=0.4)
    for s in (1, -1):
        grow(m, "head", "left" if s > 0 else "right", (4 * s, 37, 2.2), 4, 3, 43 + s, moss, cover=0.5, top=0.9, edge={"t"}, px=2, depth=0.4)
    flower(m, "head", (-2, 40.6, 3.5), "yellow_concrete", "orange_concrete", 1.8)
    # the young oak growing out of the left shoulder: a bent trunk, two branches and a round crown
    tip = limb(m, "tree", "oak_log", (7.6, 30.4, -2), [(5, 1.6, (0, 0, -8)), (5, 1.3, (0, 0, 14))])
    limb(m, "tree", "oak_log", (8.4, 34.6, -2), [(3.2, 0.9, (0, 0, -55))])
    limb(m, "tree", "oak_log", (7.6, 36.2, -2), [(2.8, 0.8, (30, 0, 40))])
    x, y, z = tip
    for (dx, dy, dz, w, h, d, b) in ((0, 2.6, 0, 8, 4.6, 7, "oak_leaves"), (0, 4.9, 0, 5, 2, 4.6, "oak_leaves"), (2.4, 0.4, 0.6, 4, 2.6, 4, "azalea_leaves"),
                                     (-2.6, 1.0, -0.6, 3.6, 2.4, 3.6, "oak_leaves"), (0.6, 2.8, 2.2, 3, 2.4, 3, LF)):
        m.c("tree", b, (x + dx, y + dy, z + dz), (w, h, d))
    for (dx, dy, dz) in ((2.2, 4.2, 2.6), (-2.6, 3, 2), (3.4, 2, -2.4)):
        m.c("tree", "red_concrete", (x + dx, y + dy, z + dz), (0.9, 0.9, 0.9))
    m.attacks = {"slam": "slam", "toss": "swipe", "roots": "stomp", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def grave_marshal():
    """A skeleton general in dented violet plate: huge fringed pauldrons, a breastplate over an open
    ribcage, a tabard on a belt with a soul gem, a stone warhammer bound in chain and a tall wooden tower
    shield that still carries the arrows of its last siege."""
    m = Model("grave_marshal", "biped", 2.0)
    biped(m, hip=14, legx=2.8, neck=28, shoulder=26.5, armx=7.6)
    m.bone("hammer", "armR", (-7.6, 10.8, 0.2))
    m.bone("shield", "armL", (7.6, 10.8, 0.2))
    m.hold = {"hammer": 12, "shield": 0}
    m.bend = -35
    BN, BN2, PU, PU2, DK, TR, GD = "bone_block", "calcite", "purple_concrete", "purple_wool", "polished_blackstone", "gray_terracotta", "gold_block"
    # legs: bone shins inside violet greaves and heavy dark boots
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.8 * s
        m.c(b, BN, (x, 10.5, 0), (1.6, 6, 1.6))
        m.c(b, BN2, (x, 7.2, 0.2), (2.4, 1.4, 2.4))
        bevel(m, b, PU, (x, 4.6, 0.2), (3.8, 5, 4), 0.4)
        m.c(b, DK, (x, 6.9, 0.2), (4.2, 0.8, 4.4))
        m.c(b, DK, (x, 1.1, 0.7), (4.2, 2.2, 5.4))
        m.c(b, PU2, (x, 4.6, 2.25), (1, 3, 0.2))
    # hips: a dark belt with a gold buckle and a soul gem, a torn violet tabard front and back
    m.c("hips", BN, (0, 15.5, 0), (5, 2.4, 2.4))
    band(m, "hips", DK, (0, 17.4, 0), (8.6, 1.8, 5.2))
    m.c("hips", GD, (0, 17.4, 2.7), (2.4, 2.2, 0.4))
    m.c("hips", "magenta_concrete", (0, 17.4, 2.95), (1.2, 1.2, 0.3), light=True)
    for z, sgn in ((2.4, 1), (-2.4, -1)):
        m.c("hips", PU, (0, 13.2, z), (4.4, 6.4, 0.5))
        for k, L in enumerate((1.6, 0.8, 1.2)):
            m.c("hips", PU, (-1.5 + k * 1.5, 9.4 - L / 2, z), (1.3, L, 0.5))
        m.c("hips", PU2, (0, 15.4, z + 0.2 * sgn), (4.4, 0.6, 0.3))
    # torso: a spine and an open ribcage under a violet breastplate
    m.c("body", BN, (0, 21, -0.6), (1.8, 8, 1.8))
    for k in range(3):
        y = 19 + k * 1.8
        m.c("body", BN, (0, y, 0.6), (7 - k * 0.4 if k else 6, 0.9, 3.4))
        for s in (1, -1):
            m.c("body", BN, ((3.3 - k * 0.2) * s, y, -0.4), (0.9, 0.9, 2.6))
    bevel(m, "body", PU, (0, 25, 0.2), (9, 5.4, 5), 0.7)
    m.c("body", DK, (0, 22.5, 0.4), (9.4, 0.6, 5.2))
    paint(m, "body", "front", (0, 25.2, 2.75), [
        ".DD.",
        "DMMD",
        "DMMD",
        ".DD.",
    ], {"D": DK, "M": ("magenta_concrete", 0.3, True)}, px=1, depth=0.3)
    m.c("body", PU, (0, 25, -2.6), (8, 5, 0.6))
    # the pauldrons: three stacked violet plates each side, a dark rim and a fringe of tassels
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 7.8 * s
        bevel(m, a, PU, (x + 0.4 * s, 27.6, 0), (8.6, 4.4, 7.6), 0.8)
        m.c(a, PU2, (x + 0.4 * s, 30.0, 0), (6.4, 0.8, 6.0))
        m.c(a, PU, (x + 0.8 * s, 25.0, 0), (8.2, 1.8, 8.2))
        m.c(a, DK, (x + 0.8 * s, 24.0, 0), (8.6, 0.6, 8.6))
        for k in range(6):
            zz = -3.2 + k * 1.28
            L = 1.6 if k % 2 else 2.4
            m.c(a, DK, (x + 4.95 * s, 23.7 - L / 2, zz * 1.2), (0.4, L, 0.8))
            m.c(a, DK, (x + 0.8 * s - 3.6 + k * 1.44, 23.7 - L / 2, 4.15), (0.8, L, 0.4))
        # the arm itself: bone upper arm, a dark bracer, a bony hand
        m.c(a, BN, (x, 19.6, 0), (1.7, 7, 1.7))
        bevel(m, a, DK, (x, 14.4, 0.2), (3.2, 4.6, 3.2), 0.4)
        m.c(a, PU, (x, 16.4, 0.2), (3.4, 0.6, 3.4))
        m.c(a, BN, (x, 10.8, 0.2), (2.4, 2.4, 2.6))
    # the skull: square and white, deep black sockets with a faint violet glow, a grinning jaw
    bevel(m, "head", BN2, (0, 32, 0.4), (8, 8, 8), 0.5)
    paint(m, "head", "front", (0, 31.6, 4.45), [
        "........",
        ".KK..KK.",
        ".KP..PK.",
        "...KK...",
        ".WKWKWK.",
        "..WWWW..",
    ], {"K": "black_concrete", "P": ("purple_concrete", 0.3, True), "W": BN}, px=1, depth=0.3)
    m.c("head", TR, (0, 36.15, 0.4), (6, 0.3, 6))
    for (x, z) in ((-2.6, 2.6), (2.2, -1.4)):
        m.c("head", TR, (x, 34.4, 4.45), (0.4, 2.4, 0.2))
    # the warhammer: a grey stone head with iron caps, a long dark haft wrapped in chain, gripped in the fist
    m.c("hammer", "dark_oak_log", (-7.6, 13, 0.2), (1.2, 24, 1.2))
    m.c("hammer", BN, (-7.6, 10.8, 0.2), (2.6, 2.6, 2.6))
    m.c("hammer", "chain", (-7.6, 6.2, 0.2), (1.5, 5, 1.5))
    bevel(m, "hammer", "polished_andesite", (-7.6, 25.6, 0.2), (5.6, 5.6, 9), 0.6)
    for zz in (-4.2, 4.6):
        m.c("hammer", "iron_block", (-7.6, 25.6, zz), (6, 6, 0.6))
    m.c("hammer", "gray_concrete", (-7.6, 25.6, 0.2), (5.8, 0.6, 9.2))
    m.c("hammer", DK, (-7.6, 1.6, 0.2), (1.8, 1.6, 1.8))
    # the tower shield: strapped to the forearm and held by a grip, dark planks in a gold-brown frame,
    # a violet boss and three arrows still in it; it stands clear of the pauldron
    X = 11.2
    m.c("shield", DK, (9.4, 10.8, 0.2), (2.6, 1.0, 1.0))
    m.c("shield", "dark_oak_planks", (X, 12, 0.6), (1, 16, 11))
    for (dy, dz, h, d) in ((7.8, 0, 0.8, 11.8), (-7.8, 0, 0.8, 11.8), (0, 5.7, 16.4, 0.8), (0, -5.7, 16.4, 0.8)):
        m.c("shield", "stripped_oak_log", (X + 0.7, 12 + dy, 0.6 + dz), (0.6, h, d))
    for dy in (-3, 3):
        m.c("shield", "stripped_dark_oak_log", (X + 0.6, 12 + dy, 0.6), (0.3, 0.5, 10.6))
    m.c("shield", PU, (X + 0.8, 12, 0.6), (0.6, 3.2, 3.2))
    m.c("shield", DK, (X + 1.2, 12, 0.6), (0.4, 1.4, 1.4))
    for (y, z, ry, rz) in ((16, 3.4, 25, 10), (9.4, -3.2, 35, -15), (7.6, 3.6, 15, 20)):
        m.c("shield", "dark_oak_log", (X + 2.4, y, z), (4, 0.35, 0.35), (0, ry, rz))
        m.c("shield", "white_concrete", (X + 4.1, y + rz * 0.03, z - ry * 0.03), (1, 0.9, 0.15), (0, ry, rz))
    m.attacks = {"slam": "slam", "charge": "lunge", "volley": "cast", "shockwave": "swipe"}
    m.melee = "swipe"
    return m


@model
def mayor_grumble():
    """The mayor of a village that was never on any map: a villager who is almost all head, on two stubby
    legs, arms folded over his belly in the villager way. A towering black top hat with an emerald band,
    a gold monocle, one long grey unibrow and the biggest nose in the overworld."""
    m = Model("mayor_grumble", "biped", 2.2)
    biped(m, hip=5, legx=3.6, neck=7, shoulder=11, armx=0.1)
    m.bone("hat", "head", (0, 25, 0))
    m.bone("fold", "head", (0, 8, 9))
    m.no_elbows = True
    SK, SK2, SK3, RB, RB2, HT, GD, EM = "terracotta", "packed_mud", "white_terracotta", "green_terracotta", "lime_terracotta", "black_concrete", "gold_block", "emerald_block"
    # stubby legs in green robe hems, brown shoes poking forward
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.6 * s
        m.c(b, RB, (x, 4, 0), (4.4, 4, 4.4))
        m.c(b, "brown_terracotta", (x, 1, 1), (4.4, 2, 6.4))
        m.c(b, "brown_concrete", (x, 0.3, 1.2), (4.8, 0.6, 6.8))
    # the head is the whole body: skin, a robe collar round the bottom, the face on the front
    bevel(m, "head", SK, (0, 16, 0), (16, 16, 15), 1.2)
    m.c("head", RB, (0, 9.2, 0), (16.6, 2.6, 15.6))
    m.c("head", RB2, (0, 10.7, 0), (16.8, 0.6, 15.8))
    for x in (-5, 0, 5):
        m.c("head", GD, (x, 9.2, 7.9), (1.2, 1.2, 0.4))
    # face: a grey unibrow across the whole face, green eyes, ruddy cheeks, the great nose
    paint(m, "head", "front", (0, 18.5, 7.55), [
        "GGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGG",
        ".WWEE....EEWW...",
        ".WWEE....EEWW...",
        "................",
        "CCC..........CCC",
    ], {"G": "light_gray_concrete", "W": "white_concrete", "E": "green_concrete", "C": "pink_terracotta"}, px=1, depth=0.3)
    bevel(m, "head", SK, (0, 14.4, 9.0), (4, 8, 3), 0.5)
    m.c("head", SK2, (0, 10.8, 9.4), (3.4, 1.2, 2.2))
    for s in (1, -1):
        m.c("head", SK2, (1.2 * s, 11.2, 10.55), (0.8, 0.8, 0.2))
    # the monocle on his right eye: a gold ring, glass, a gold chain to the collar
    for (dx, dy, w, h) in ((0, 1.7, 3.6, 0.5), (0, -1.7, 3.6, 0.5), (1.6, 0, 0.5, 3), (-1.6, 0, 0.5, 3)):
        m.c("head", GD, (-4.5 + dx, 17.0 + dy, 7.95), (w, h, 0.4))
    m.c("head", "white_stained_glass", (-4.5, 17.0, 7.85), (2.8, 2.8, 0.2))
    for k in range(4):
        m.c("head", GD, (-6.4 + k * 0.1, 14.9 - k * 1.1, 7.95), (0.35, 1.0, 0.35))
    # arms folded in front of the belly, villager style: two sleeves meeting a crossbar, hands peeking
    # (on their own bone that never swings, so the folded arms stay folded whatever he does)
    for s in (1, -1):
        m.c("fold", RB, (5.2 * s, 8.8, 8.4), (3.4, 4, 3.2), (-30, 0, 0))
        m.c("fold", RB2, (5.2 * s, 7.2, 9.3), (3.6, 0.6, 2.8), (-30, 0, 0))
    m.c("fold", RB, (0, 7.0, 9.8), (8, 3, 3.2))
    for s in (1, -1):
        m.c("fold", SK, (3.0 * s, 7.2, 11.3), (2.0, 2.2, 0.6))
    # the top hat: tall and black, a wide brim, an emerald band with a gold buckle, a little dent
    m.c("hat", HT, (0, 24.6, 0), (17, 0.8, 16))
    m.c("hat", HT, (0, 28.6, 0), (11, 7.2, 10))
    m.c("hat", EM, (0, 26.6, 0), (11.4, 1.8, 10.4))
    m.c("hat", GD, (0, 26.6, 5.3), (2.6, 2.2, 0.3))
    m.c("hat", EM, (0, 26.6, 5.5), (1.2, 1.0, 0.2), light=True)
    m.c("hat", "gray_concrete", (0, 32.3, 0), (11.2, 0.4, 10.2))
    m.c("hat", HT, (2, 32.5, 1), (4, 0.4, 3))
    # grey hair tufts poking out under the hat at the sides and back
    for s in (1, -1):
        for k, (y, z) in enumerate(((22.5, 4), (21, 1), (22, -3))):
            m.c("head", "light_gray_concrete", (8.3 * s, y, z), (0.8, 2.2, 2.6), (0, 0, 15 * s))
    m.c("head", "light_gray_concrete", (0, 21.5, -7.8), (12, 2.6, 0.8))
    m.attacks = {"minions": "roar", "volley": "cast", "quake": "stomp", "roar": "roar"}
    m.melee = "stomp"
    return m


@model
def old_sizzle():
    """A creeper so old it outgrew every cave: the classic mottled green skin, gone grey and mossy at the
    feet, split by cracks that glow like a fuse that has been burning for a hundred years. The face is
    the one every player knows, just far too big."""
    m = Model("old_sizzle", "quad", 3.2)
    quad(m, body_y=6, legx=2.1, legz_front=2.2, legz_back=-2.2, neck_y=18, neck_z=0)
    G0, G1, G2, G3, FU = "lime_concrete", "green_concrete", "lime_wool", "light_gray_concrete", "orange_concrete"
    skin = {"A": G1, "B": G2}
    speck = {"A": G3, "B": "lime_terracotta"}
    # four stubby feet, darker and grey at the toes
    for s, (b, z) in ((1, ("legFL", 2.2)), (-1, ("legFR", 2.2)), (1, ("legBL", -2.2)), (-1, ("legBR", -2.2))):
        x = 2.1 * s
        m.c(b, G0, (x, 3.4, z), (4, 5.2, 4))
        m.c(b, "green_terracotta", (x, 0.5, z + (0.2 if z > 0 else -0.2)), (4.2, 1, 4.4))
        grow(m, b, "front" if z > 0 else "back", (x, 3.4, z + (2 if z > 0 else -2)), 2, 3, 50 + int(s + z), skin, cover=0.5, px=2, depth=0.2)
    # the body: tall and narrow, mottled, cracks glowing orange down the front and back
    m.c("body", G0, (0, 12, 0), (8, 12, 4))
    for face, c in (("front", (0, 12, 2)), ("back", (0, 12, -2))):
        grow(m, "body", face, c, 4, 6, 60 if face == "front" else 61, skin, cover=0.55, top=0.5, px=2, depth=0.2)
        pass
    for s, face in ((1, "left"), (-1, "right")):
        grow(m, "body", face, (4 * s, 12, 0), 2, 6, 64 + s, skin, cover=0.6, px=2, depth=0.2)
    from kit import crack
    crack(m, "body", "front", (0, 12, 2.2), [(-2.5, 5), (-2.5, 2), (0.5, 2), (0.5, -1.5), (2.5, -1.5), (2.5, -4.5)], FU, 0.7, 0.3)
    crack(m, "body", "back", (0, 12, -2.2), [(2, 5.5), (2, 1), (-1, 1), (-1, -3), (-3, -3)], FU, 0.7, 0.3)
    crack(m, "body", "left", (4.2, 12, 0), [(-1, 3), (-1, 0), (1, 0), (1, -3)], FU, 0.6, 0.3)
    # the fuse: a smouldering stub on the back of the head
    # head: the creeper face, mottled skin, moss on the crown
    m.c("head", G0, (0, 22, 0), (8, 8, 8))
    paint(m, "head", "front", (0, 22, 4.15), [
        "........",
        ".KK..KK.",
        ".KK..KK.",
        "...KK...",
        "..KKKK..",
        "..KKKK..",
        "..K..K..",
        "........",
    ], {"K": "black_concrete"}, px=1, depth=0.3)
    m.c("head", "gray_concrete", (-1.5, 21.2, 4.34), (1, 1, 0.1))
    m.c("head", "gray_concrete", (1.5, 21.2, 4.34), (1, 1, 0.1))
    for face, c, seed in (("left", (4, 22, 0), 70), ("right", (-4, 22, 0), 71), ("back", (0, 22, -4), 72), ("top", (0, 26, 0), 73)):
        grow(m, "head", face, c, 4, 4, seed, skin, cover=0.55, px=2, depth=0.2)
    grow(m, "head", "top", (0, 26, 0), 8, 8, 74, {"A": "moss_block", "B": "green_terracotta"}, cover=0.35, px=1, depth=0.4)
    m.c("head", "gray_terracotta", (1.5, 26.9, -2.5), (1, 1.8, 1))
    m.c("head", FU, (1.5, 28.0, -2.5), (0.7, 0.6, 0.7), light=True)
    m.attacks = {"fuse": "rear", "spawn": "howl", "charge": "charge", "quake": "rear"}
    m.melee = "bite"
    return m


@model
def goldtooth():
    """The piglin brute who won the most fights in the nether and kept the gold: a wide pink head with
    a broad snout, two gold-capped tusks and floppy ears, a tall gold crown, black leather and gold
    plate, a gold-banded belt and a huge double-headed gold axe."""
    m = Model("goldtooth", "biped", 2.3)
    biped(m, hip=12, legx=2.2, neck=24, shoulder=23, armx=6)
    m.bone("crown", "head", (0, 32, 0))
    m.bone("axe", "armR", (-6, 8, 2))
    m.hold = {"axe": 20}
    m.bend = -32
    SK, SK2, SN, LT, LT2, GD, GD2 = "white_terracotta", "pink_terracotta", "pink_concrete", "black_concrete", "polished_blackstone", "gold_block", "raw_gold_block"
    # legs: black leather trousers, gold knee caps, heavy boots
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.2 * s
        m.c(b, LT2, (x, 7, 0), (4, 10, 4))
        m.c(b, GD, (x, 7.2, 2.1), (3, 2.4, 0.4))
        m.c(b, LT, (x, 1.2, 0.4), (4.4, 2.4, 5))
        m.c(b, GD2, (x, 2.6, 0.4), (4.6, 0.6, 5.2))
    # body: bare pink belly under a black leather harness, a gold chest plate on one side, a gold belt
    m.c("body", SK, (0, 18, 0), (8, 12, 4))
    m.c("body", LT2, (0, 21, 0), (8.4, 6, 4.4))
    m.c("body", GD, (2, 21.4, 2.3), (3.6, 4.4, 0.4))
    m.c("body", GD2, (2, 21.4, 2.55), (2, 2, 0.2))
    m.c("body", LT, (-1.6, 18.4, 2.25), (1, 6, 0.3), (0, 0, -28))
    band(m, "hips", LT, (0, 12.8, 0), (8.6, 1.8, 4.6), studs=3, stud_block=GD)
    m.c("hips", GD, (0, 12.8, 2.45), (2.2, 2.2, 0.4))
    m.c("body", SK2, (0, 15.6, 2.1), (6, 3, 0.2))
    # arms: bare and pink, big gold bracers, a pauldron on the axe arm
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6 * s
        m.c(a, SK, (x, 17, 0), (4, 12, 4))
        m.c(a, GD, (x, 13.2, 0), (4.6, 3, 4.6))
        m.c(a, GD2, (x, 13.2, 2.4), (1.4, 1.4, 0.3))
        m.c(a, SK2, (x, 11.2, 0), (3.6, 1, 3.6))
    bevel(m, "armR", GD, (-6.6, 23, 0), (5.6, 3, 5.4), 0.5)
    m.c("armR", LT, (-6.6, 21.3, 0), (5.8, 0.6, 5.6))
    # head: wide and pink, a big snout with dark nostrils, gold-capped tusks, floppy ears, angry brows
    m.c("head", SK, (0, 28, 0), (10, 8, 8))
    bevel(m, "head", SK2, (0, 26.4, 4.6), (5, 3.6, 1.4), 0.3)
    for s in (1, -1):
        m.c("head", "brown_terracotta", (1.2 * s, 26.4, 5.35), (1, 1.4, 0.2))
        m.c("head", "white_concrete", (2.8 * s, 24.6, 4.6), (1, 2.6, 1))
        m.c("head", GD, (2.8 * s, 25.4, 4.6), (1.2, 0.8, 1.2))
        m.c("head", SK2, (5.6 * s, 27.6, 0.4), (1, 5, 3.4), (0, 0, 30 * s))
        m.c("head", SK, (5.4 * s, 29.6, -0.4), (1.2, 2, 3.4), (0, 0, 30 * s))
    paint(m, "head", "front", (0, 29.2, 4.15), [
        "BBB....BBB",
        ".WK....KW.",
        "..........",
    ], {"B": "brown_terracotta", "W": "white_concrete", "K": "black_concrete"}, px=1, depth=0.3)
    m.c("head", SK2, (0, 24.4, 3.6), (6, 0.8, 1))
    m.c("head", "brown_terracotta", (-3.4, 30.6, 4.1), (1.2, 0.6, 0.2))
    # the crown: tall gold with five points and a black band
    m.c("crown", GD, (0, 32.8, 0), (8.4, 1.6, 6.8))
    m.c("crown", LT, (0, 33.8, 0), (8.6, 0.4, 7))
    for k, x in enumerate((-3.4, -1.7, 0, 1.7, 3.4)):
        h = (2.4, 3.2, 4.2, 3.2, 2.4)[k]
        m.c("crown", GD, (x, 34 + h / 2, 3.1), (1.4, h, 0.6))
        m.c("crown", GD, (x, 34 + h / 2, -3.1), (1.4, h, 0.6))
    for z in (-1.6, 0, 1.6):
        m.c("crown", GD, (4.0, 35.4, z), (0.6, 2.8, 1.2))
        m.c("crown", GD, (-4.0, 35.4, z), (0.6, 2.8, 1.2))
    m.c("crown", "redstone_block", (0, 32.8, 3.5), (1.4, 1.2, 0.3), light=True)
    # the axe: a long dark haft and two broad gold blades with black edges
    m.c("axe", "dark_oak_log", (-6, 16, 2), (1.2, 24, 1.2))
    m.c("axe", GD, (-6, 27.4, 2), (1.6, 2.4, 1.6))
    for zz, sgn in ((5.4, 1), (-1.4, -1)):
        m.c("axe", GD, (-6, 26.2, zz), (0.8, 8, 5.4))
        m.c("axe", GD2, (-6, 26.2, zz + 2.4 * sgn), (0.9, 9.4, 1))
        m.c("axe", LT, (-6, 26.2, zz - 0.4 * sgn), (1, 1, 3))
    m.c("axe", GD, (-6, 3.6, 2), (1.6, 1.4, 1.6))
    m.attacks = {"cleave": "slam", "charge": "lunge", "horde": "roar", "spin": "sweep"}
    m.melee = "swipe"
    return m


@model
def siegebreaker():
    """The illagers' war ravager: a massive grey-brown beast, low head swinging under curled pale horns,
    a dark plank war-saddle bolted down with iron, a tall pole with the grey and white raid banner, and
    iron-shod hooves that leave cracks in the ground."""
    m = Model("siegebreaker", "quad", 2.0)
    quad(m, body_y=17, legx=7.2, legz_front=8, legz_back=-9, neck_y=19, neck_z=12)
    m.bone("banner", "body", (0, 30, -8))
    HD, HD2, HN, WD, IR, BN = "tuff", "cyan_terracotta", "white_terracotta", "dark_oak_planks", "iron_block", "white_wool"
    for s, (b, z) in ((1, ("legFL", 8)), (-1, ("legFR", 8)), (1, ("legBL", -9)), (-1, ("legBR", -9))):
        x = 7.2 * s
        bevel(m, b, HD, (x, 12, z), (7.6, 10, 7.6), 1.2)
        bevel(m, b, HD2, (x, 5.4, z + 0.3), (6.6, 5.4, 6.6), 0.8)
        m.c(b, IR, (x, 1.5, z + 0.6), (7.6, 3.0, 8.2))
        m.c(b, "gray_concrete", (x, 0.3, z + 0.6), (8.2, 0.6, 8.8))
    # body: a deep chest, a high humped back, shaggy darker hide along the spine
    bevel(m, "body", HD, (0, 19, -1), (14, 13, 22), 2.0)
    bevel(m, "body", HD, (0, 22, 6), (15, 13, 10), 2.0)
    grow(m, "body", "top", (0, 28.5, 0), 6, 10, 80, {"A": HD2, "B": "gray_terracotta"}, cover=0.6, px=2, depth=0.6)
    for s, side in ((1, "left"), (-1, "right")):
        grow(m, "body", side, (7.5 * s if abs(s) else 0, 20, 4), 6, 3, 81 + s, {"A": HD2, "B": HD2}, cover=0.5, top=0.9, edge={"t"}, px=2, depth=0.3)
    # war saddle: dark planks bolted with iron, a skirt of planks down each flank
    bevel(m, "body", WD, (0, 26.4, -3), (12, 2.4, 11), 0.5)
    for s in (1, -1):
        m.c("body", WD, (7.4 * s, 22, -3), (0.8, 8, 10))
        for z in (-7, -3, 1):
            m.c("body", IR, (7.9 * s, 25, z), (0.4, 1.2, 1.2))
            m.c("body", IR, (7.9 * s, 19, z), (0.4, 1.2, 1.2))
        m.c("body", "stripped_dark_oak_log", (7.85 * s, 22, -3), (0.3, 0.6, 9.4))
    m.c("body", IR, (0, 27.8, -3), (12.4, 0.6, 1.2))
    # the raid banner on a pole rising from the back of the saddle
    m.c("banner", WD, (0, 35, -8), (1.6, 18, 1.6))
    m.c("banner", IR, (0, 28.6, -8), (2.4, 1.6, 2.4))
    m.c("banner", WD, (0, 45.6, -8), (8.4, 1.0, 1.0))
    m.c("banner", BN, (0, 40, -8.6), (7.4, 10.4, 0.4))
    paint(m, "banner", "back", (0, 40, -8.8), [
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
    ], {"G": "light_gray_concrete", "K": "black_concrete", "C": "cyan_concrete"}, px=1.04, depth=0.2)
    paint(m, "banner", "front", (0, 40, -8.4), [
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
    ], {"G": "light_gray_concrete", "K": "black_concrete", "C": "cyan_concrete"}, px=1.04, depth=0.2)
    # tail: a short tuft
    limb(m, "tail", HD, (0, 20, -12), [(4, 2.4, (-150, 0, 0)), (2.6, 1.8, (-175, 0, 0), HD2)])
    # head: huge and low, a flat face, tiny dark eyes under a heavy brow, pale horns curling back
    bevel(m, "head", HD, (0, 17.6, 19), (13, 13, 13), 1.8)
    bevel(m, "head", HD2, (0, 13.6, 27.4), (9, 6.4, 3), 0.8)
    paint(m, "head", "front", (0, 14.2, 29.0), ["K.....K", ".......", ".TTTTT."], {"K": "black_concrete", "T": "gray_terracotta"}, px=1, depth=0.3)
    paint(m, "head", "front", (0, 20.2, 26.6), ["BBBB...BBBB", ".WK.....KW."], {"B": HD2, "W": "white_concrete", "K": "black_concrete"}, px=1, depth=0.3)
    for s in (1, -1):
        limb(m, "head", HN, (5.6 * s, 22.4, 18), [(4, 2.8, (-10, 0, -40 * s)), (4, 2.4, (50, 0, -60 * s)), (3.4, 2.0, (110, 0, -40 * s)), (2.4, 1.5, (160, 0, -20 * s))])
    m.c("jaw", HD2, (0, 10.6, 23), (10, 2.4, 9))
    for x in (-3, -1, 1, 3):
        m.c("jaw", "white_concrete", (x, 12.1, 27.0), (0.8, 1, 0.6))
    m.c("head", "gray_concrete", (0, 23.7, 19.5), (7, 0.8, 6))
    m.attacks = {"charge": "charge", "roar": "howl", "quake": "rear", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def tidecaller():
    """A drowned giant that walked out of a sunken ship: teal water-logged skin, torn cyan shirt and
    dark trousers, coral grown over both shoulders, kelp hanging off the arms, eyes that glow like a
    guardian's, and a big glowing trident."""
    m = Model("tidecaller", "biped", 2.3)
    biped(m, hip=12, legx=2.1, neck=24, shoulder=23, armx=6)
    m.bone("trident", "armR", (-6, 9, 2))
    m.hold = {"trident": 10}
    m.bend = -30
    SK, SK2, SH, PT, CO1, CO2, CO3, KE = "prismarine", "oxidized_copper", "cyan_concrete", "blue_terracotta", "brain_coral_block", "horn_coral_block", "tube_coral_block", "green_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.1 * s
        m.c(b, PT, (x, 8, 0), (4, 8, 4))
        for k in range(2):
            m.c(b, PT, (x - 1 + k * 2, 3.6 - k * 0.6, 1.6), (1.6, 1.2 + k, 0.8))
        m.c(b, SK, (x, 1.8, 0), (4, 3.6, 4))
    m.c("hips", PT, (0, 12.6, 0), (8.2, 1.6, 4.2))
    m.c("body", SK, (0, 18, 0), (8, 12, 4))
    m.c("body", SH, (0, 19.4, 0), (8.4, 9, 4.4))
    for k, (x, L) in enumerate(((-3, 2.4), (-1, 1.2), (1, 3), (3, 1.6))):
        m.c("body", SH, (x, 14.9 - L / 2, 2.0), (1.8, L, 0.6))
    for (x, y) in ((-2, 21), (1.6, 17)):
        m.c("body", SK, (x, y, 2.25), (1.4, 1.6, 0.2))
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6 * s
        m.c(a, SK, (x, 17, 0), (4, 12, 4))
        m.c(a, SH, (x, 21, 0), (4.4, 4, 4.4))
        m.c(a, SK2, (x, 11.6, 0), (4.2, 1.6, 4.2))
        vines(m, a, (x + 1.2 * s, x - 0.6 * s), 18.8, -2.3, (5, 7), KE, "kelp_block")
    # coral growing over the shoulders: a pink brain coral lump, yellow horn coral, a blue tube
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 6 * s
        bevel(m, a, CO1 if s > 0 else CO3, (x, 23.8, -0.4), (3.8, 2.4, 3.6), 0.4)
        m.c(a, CO2, (x + 1 * s, 25.8, 0.8), (1.2, 2.4, 1.2), (0, 0, 15 * s))
        m.c(a, CO2, (x - 0.6 * s, 26.4, -1.2), (1, 3, 1), (10, 0, -10 * s))
        m.c(a, "fire_coral_block" if s > 0 else CO1, (x + 0.6 * s, 25.4, -1.6), (1.4, 1.4, 1.4))
    # head: teal, a glowing pair of eyes, a slack mouth, dark wet hair hanging over the back and sides
    m.c("head", SK, (0, 28, 0), (8, 8, 8))
    paint(m, "head", "front", (0, 27.6, 4.15), [
        "........",
        ".EE..EE.",
        "........",
        "........",
        "..KKKK..",
        "........",
    ], {"E": ("light_blue_concrete", 0.3, True), "K": "black_terracotta"}, px=1, depth=0.3)
    m.c("head", "cyan_terracotta", (0, 32.2, 0), (8.4, 0.6, 8.4))
    m.c("head", "cyan_terracotta", (0, 29.4, -4.2), (8.4, 5.6, 0.6))
    for s in (1, -1):
        m.c("head", "cyan_terracotta", (4.2 * s, 30.4, -1), (0.6, 3.6, 6.4))
    m.c("head", CO1, (-2.6, 32.8, 1.6), (2, 1.2, 2))
    # an old fishing net hanging off the shoulders as a cape, barnacles on the skin
    m.c("body", "cobweb", (0, 17, -2.6), (9, 12, 0.3))
    for k, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
        m.c("body", "cobweb", (x, 10.6 - (k % 2), -2.6), (2.2, 1.4 + (k % 2) * 1.6, 0.3))
    m.c("body", "spruce_planks", (0, 23.2, -2.7), (9.4, 0.6, 0.6))
    for (b, face, c, seed) in (("legL", "front", (2.1, 1.8, 2.0), 90), ("armR", "front", (-6, 14, 2.0), 91), ("head", "left", (4.0, 26, 0), 92), ("armL", "back", (6, 15, -2.0), 93)):
        grow(m, b, face, c, 4, 4, seed, {"A": "white_terracotta", "B": "light_gray_concrete"}, cover=0.25, px=1, depth=0.4, blobs=2)
    # the trident: a long teal haft, a glowing three-pronged head
    m.c("trident", SK2, (-6, 18, 2), (1, 30, 1))
    m.c("trident", "sea_lantern", (-6, 33.4, 2), (4.6, 1, 1), light=True)
    for dx in (-2, 0, 2):
        h = 4.6 if dx == 0 else 3.4
        m.c("trident", "sea_lantern", (-6 + dx, 34 + h / 2, 2), (0.9, h, 0.9), light=True)
    m.c("trident", "prismarine_bricks", (-6, 31.8, 2), (1.6, 2, 1.6))
    m.attacks = {"wave": "slam", "throw": "lunge", "whirlpool": "cast", "drowned": "roar"}
    m.melee = "swipe"
    return m


@model
def forgemaster():
    """A blaze that took over a nether forge: the yellow blaze head under a blackstone smith's hood, a
    glowing crucible of molten gold for a body, three rings of blaze rods spinning round it, and two
    floating blackstone gauntlets, one gripping a smith's hammer."""
    m = Model("forgemaster", "float", 2.4)
    m.bone("core", "root", (0, 16, 0))
    m.bone("head", "core", (0, 22, 0))
    m.bone("ring1", "core", (0, 20, 0))
    m.bone("ring2", "core", (0, 13, 0))
    m.bone("ring3", "core", (0, 6, 0))
    m.mbone("armL", "core", (11, 17, 1))
    m.bone("hammer", "armR", (-11, 14, 3))
    BZ, BZ2, BL, BL2, GD, MG = "yellow_concrete", "orange_concrete", "polished_blackstone", "blackstone", "gold_block", "magma_block"
    # the crucible body: a blackstone bowl with gold bands, molten gold glowing over the rim
    stack(m, "core", BL, 0, 7, 0, [(5, 2, 5), (7, 2, 7), (9, 3, 9), (10, 3, 10)])
    m.c("core", GD, (0, 12.5, 0), (9.6, 0.6, 9.6))
    m.c("core", GD, (0, 15.6, 0), (10.4, 0.6, 10.4))
    m.c("core", "shroomlight", (0, 16.4, 0), (8.8, 0.8, 8.8), light=True)
    m.c("core", BZ2, (0, 16.9, 0), (6, 0.4, 6), light=True)
    m.c("core", "gilded_blackstone", (0, 10, 4.6), (3, 3, 0.4))
    # the head: the blaze face in yellow and orange, dark eyes, a blackstone hood with gold trim over it
    m.c("head", BZ, (0, 22, 0), (8, 8, 8), light=True)
    paint(m, "head", "front", (0, 22, 4.15), [
        "OOOOOOOO",
        "O......O",
        ".KK..KK.",
        ".KK..KK.",
        "........",
        "O..OO..O",
        "OOOOOOOO",
        "OO....OO",
    ], {"O": (BZ2, 0.3, True), "K": "black_concrete"}, px=1, depth=0.3)
    m.c("head", BL, (0, 26.5, -0.6), (9.2, 1.4, 9.4))
    m.c("head", BL, (0, 23, -4.5), (9.2, 8, 1))
    for s in (1, -1):
        m.c("head", BL, (4.55 * s, 23.6, -0.6), (0.6, 6.4, 8.6))
        m.c("head", GD, (4.6 * s, 20.2, 2.4), (0.8, 0.8, 0.8))
    m.c("head", GD, (0, 27.3, 3.6), (9.4, 0.5, 0.6))
    m.c("head", BL2, (0, 28.4, -1), (5, 1, 5))
    # three rings of blaze rods, each rod ringed with blackstone, the rings at different heights
    import math
    for ring, y, n, r, L in (("ring1", 20, 6, 9, 6), ("ring2", 13, 5, 7.6, 5.4), ("ring3", 6, 4, 5.6, 4.6)):
        for k in range(n):
            a = 2 * math.pi * k / n + (0.3 if ring == "ring2" else 0)
            x, z = math.cos(a) * r, math.sin(a) * r
            m.c(ring, BZ2, (x, y, z), (1.6, L, 1.6), light=True)
            m.c(ring, BL, (x, y - L / 2 + 0.5, z), (1.9, 0.8, 1.9))
    # floating gauntlets: blackstone with gold knuckles, the right one holding the forge hammer
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 11 * s
        bevel(m, a, BL, (x, 17, 1), (4.4, 5, 4.4), 0.5)
        m.c(a, GD, (x, 18.6, 3.3), (4.4, 1, 0.4))
        m.c(a, BL2, (x, 20.2, 1), (5, 1.4, 5))
        m.c(a, MG, (x, 20.95, 1), (3.6, 0.2, 3.6), light=True)
    m.c("hammer", "dark_oak_log", (-11, 14, 3), (1.2, 14, 1.2))
    bevel(m, "hammer", BL, (-11, 8, 3), (6, 4, 4), 0.5)
    m.c("hammer", GD, (-11, 8, 3), (6.4, 1, 4.4))
    m.c("hammer", MG, (-14.05, 8, 3), (0.2, 3, 3), light=True)
    m.c("hammer", MG, (-7.95, 8, 3), (0.2, 3, 3), light=True)
    m.attacks = {"fireballs": "pulse", "meteor": "raise", "hammer": "swipe", "spin": "spin"}
    m.melee = "swipe"
    return m


@model
def plague_butcher():
    """A huge zombie that used to be the village butcher: a sagging green belly under a stained apron,
    one torn sleeve rolled up, a bloodied cleaver, a rope belt of hooks, a butcher's cap, sunken black
    eyes and a jaw hanging loose."""
    m = Model("plague_butcher", "biped", 2.4)
    biped(m, hip=10, legx=2.6, neck=24, shoulder=22.5, armx=7.2)
    m.bone("cleaver", "armR", (-7.2, 8, 2))
    m.hold = {"cleaver": 40}
    m.bend = -40
    SK, SK2, AP, AP2, SH, TR, BL = "green_terracotta", "lime_terracotta", "white_terracotta", "light_gray_terracotta", "cyan_concrete", "blue_terracotta", "red_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.6 * s
        m.c(b, TR, (x, 6, 0), (4.6, 8, 4.6))
        m.c(b, "gray_terracotta", (x, 1.4, 0.5), (5, 2.8, 5.6))
    # body: a big belly, the blue shirt split open, a long apron with stains, a rope of hooks
    bevel(m, "body", SH, (0, 18.5, 0), (12, 11, 7), 1.2)
    bevel(m, "body", SK, (0, 14.5, 1.2), (11, 7, 7), 2.0)
    m.c("body", SK2, (0, 14.2, 4.75), (5, 4, 0.2))
    m.c("hips", AP, (0, 12.4, 4.8), (9, 10, 0.5))
    m.c("hips", AP, (0, 16.2, 4.5), (6, 4, 0.5))
    paint(m, "hips", "front", (0, 11.6, 5.1), [
        "....B....",
        ".......BB",
        "..B......",
        "BB....A..",
        "......AA.",
        ".A.......",
    ], {"B": BL, "A": AP2}, px=1, depth=0.2)
    band(m, "hips", "stripped_oak_log", (0, 12.6, 0), (11.6, 1, 7.6))
    for x in (-4.6, 4.6):
        m.c("hips", "iron_block", (x, 11.2, 3.8), (0.4, 2.2, 0.4))
        m.c("hips", "iron_block", (x, 10.2, 4.2), (0.4, 0.4, 1))
    m.c("body", AP, (0, 22.6, 3.6), (0.6, 3, 0.4), (0, 0, 40))
    m.c("body", AP, (0, 22.6, 3.6), (0.6, 3, 0.4), (0, 0, -40))
    # arms: one sleeve torn off to show the green arm, the other rolled up, both hanging forward
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 7.2 * s
        bevel(m, a, SH if s > 0 else SK, (x, 19.6, 0), (4.6, 6, 4.6), 0.5)
        m.c(a, SK, (x, 13.2, 0.4), (4.2, 7.4, 4.2))
        m.c(a, SK2, (x, 9.0, 0.6), (4.4, 2.2, 4.6))
    m.c("armL", AP2, (7.2, 16.4, 0), (4.8, 1.2, 4.8))
    grow(m, "armR", "front", (-7.2, 14, 2.5), 4, 6, 95, {"A": SK2, "B": "green_concrete"}, cover=0.4, px=1, depth=0.3)
    # head: zombie green, sunken black eyes, a slack open jaw, a white cap pushed back
    m.c("head", SK, (0, 29, 0.6), (9, 9, 9))
    paint(m, "head", "front", (0, 29, 5.15), [
        ".........",
        ".KK...KK.",
        ".KK...KK.",
        "....S....",
        "..DDDDD..",
        "..D.D.D..",
        ".........",
    ], {"K": "black_concrete", "S": SK2, "D": "black_terracotta"}, px=1, depth=0.3)
    m.c("head", SK, (0, 24.4, 2.2), (6, 1.4, 5))
    m.c("head", AP, (0, 34.2, -0.4), (9.6, 2, 9.6))
    m.c("head", AP, (0, 35.4, -1), (8, 1.2, 8))
    m.c("head", AP2, (0, 33.4, 4.9), (9.6, 0.6, 1))
    # the cleaver: a wide rectangular blade with a dark edge and a stain, short wooden grip
    m.c("cleaver", "dark_oak_log", (-7.2, 12, 2), (1.2, 7, 1.2))
    m.c("cleaver", "iron_block", (-7.2, 18.6, 3.6), (0.6, 7, 6))
    m.c("cleaver", "gray_concrete", (-7.2, 18.6, 6.9), (0.7, 7, 0.6))
    m.c("cleaver", BL, (-7.2, 17, 4.6), (0.7, 2, 2))
    m.c("cleaver", "gray_concrete", (-7.2, 21, 1.6), (0.8, 1, 1))
    m.attacks = {"cleave": "slam", "hook": "lunge", "horde": "roar", "spit": "cast"}
    m.melee = "swipe"
    return m


@model
def the_collector():
    """An enderman who keeps every block it ever stole: too tall and too thin, black with purple eyes,
    a long dark coat stitched from end stone and obsidian, and a crooked stack of stolen blocks carried
    in its arms and floating round it."""
    m = Model("the_collector", "biped", 2.0)
    biped(m, hip=22, legx=2, neck=36, shoulder=35, armx=5.4)
    m.bone("stack", "body", (0, 22, 6))
    m.no_elbows = True
    m.rest("armL", (-50, 0, 0))
    m.rest("armR", (-50, 0, 0))
    EN, EN2, CO, CO2, EY = "black_concrete", "obsidian", "polished_blackstone", "purpur_block", "magenta_concrete"
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2 * s
        m.c(b, EN, (x, 11, 0), (2, 22, 2))
        m.c(b, EN2, (x, 0.6, 0.4), (2.4, 1.2, 3))
    # coat: a long end-stone coat open at the front, purpur cuffs and hem, obsidian buttons
    m.c("body", EN, (0, 29, 0), (8, 14, 4))
    m.c("body", CO, (0, 30, 0), (8.6, 12, 4.6))
    m.c("body", EN, (0, 30, 2.2), (3, 12, 0.4))
    m.c("hips", CO, (0, 18, 0), (8.6, 10, 4.6))
    m.c("hips", EN, (0, 18, 2.3), (2.6, 10, 0.2))
    m.c("hips", CO2, (0, 13.4, 0), (8.8, 1, 4.8))
    for y in (33, 30, 27):
        m.c("body", EN2, (2.2, y, 2.4), (0.8, 0.8, 0.3))
    m.c("body", CO2, (0, 35.6, 0), (9, 1.2, 5))
    # long thin arms in coat sleeves, bent to carry the stack in front
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 5.4 * s
        m.c(a, CO, (x, 30, 0), (2.6, 10, 2.6))
        m.c(a, CO2, (x, 25.4, 0), (2.8, 1, 2.8))
        m.c(a, EN, (x, 18, 0), (2, 14, 2))
    # head: black, wide purple eyes, a jaw that hangs a little open
    m.c("head", EN, (0, 40, 0), (8, 8, 8))
    paint(m, "head", "front", (0, 40, 4.15), [
        "........",
        "........",
        "........",
        ".PEE.EEP",
        "........",
        "........",
    ], {"E": (EY, 0.3, True), "P": ("purple_concrete", 0.3, True)}, px=1, depth=0.3)
    m.c("head", EN, (0, 35.2, 0.6), (7.6, 1.6, 7.6))
    # the stolen stack: a grass block, a crooked tower of others, one end stone block floating free
    blocks = [("moss_block", 0, 0, 0), ("dirt", 0.5, 1, 6), ("sand", -0.4, 2, -7), ("pumpkin", 0.3, 3, 10)]
    for k, (b, dx, y, rot) in enumerate(blocks):
        m.c("stack", b, (dx, 16.5 + y * 4.6, 15), (4.6, 4.6, 4.6), (0, rot, 0))
    for (x, y, z, b) in ((7, 44, 4, "melon"), (-7, 41, 3, "end_stone"), (0, 48, -3, "moss_block")):
        m.c("stack", b, (x, y, z), (3.2, 3.2, 3.2), (20, 30, 10))
        m.c("stack", "purple_stained_glass", (x, y, z), (3.8, 3.8, 3.8), (20, 30, 10), light=True)
    m.attacks = {"blink": "cast", "throw": "lunge", "stare": "roar", "grab": "swipe"}
    m.melee = "swipe"
    return m


@model
def silk_queen():
    """A spider queen as big as a house: a dark body with red markings like a hourglass, a swollen
    abdomen wrapped in old silk, eight bristled legs, a cluster of red eyes, a crown of pale fangs and
    cobwebs hanging from her legs."""
    from v2_general import spider_legs
    m = Model("silk_queen", "spider", 2.4)
    m.bone("body", "root", (0, 10, 0))
    m.bone("abdomen", "body", (0, 12, -5))
    m.bone("head", "body", (0, 10, 6))
    m.bone("fangL", "head", (1.6, 7, 11))
    m.bone("fangR", "head", (-1.6, 7, 11))
    BD, BD2, MK, SL, FG = "black_terracotta", "gray_terracotta", "red_concrete", "white_wool", "bone_block"
    bevel(m, "body", BD, (0, 10, 1), (9, 6, 9), 1.2)
    spider_legs(m, "body", BD, BD2, "red_terracotta", 4.6, 10, (5, 2, -1, -4), 0.9, 1.3)
    # the abdomen: big and round, red hourglass marks on top, old silk wound round the back of it
    bevel(m, "abdomen", BD, (0, 14, -13), (17, 13, 19), 3.0)
    paint(m, "abdomen", "top", (0, 20.5, -12), [
        "..MMMM..",
        "...MM...",
        "....M...",
        "...MM...",
        "..MMMM..",
        ".......M",
    ], {"M": (MK, 0.3, True)}, px=1.4, depth=0.3)
    for k, z in enumerate((-17, -14.4, -11.8)):
        m.c("abdomen", SL, (0, 14 - k * 0.2, z - 2), (17.6 - k * 0.6, 1, 0.8), (0, 0, 12 - k * 12))

    # head: a cluster of eight red eyes, pale fangs, a crown of bristles
    bevel(m, "head", BD, (0, 10, 8.4), (8, 6, 6), 1.0)
    paint(m, "head", "front", (0, 10.6, 11.45), [
        "R.R..R.R",
        "........",
        ".RR..RR.",
    ], {"R": (MK, 0.3, True)}, px=1, depth=0.3)
    for s, f in ((1, "fangL"), (-1, "fangR")):
        limb(m, f, FG, (1.6 * s, 7.6, 11), [(2.4, 1.2, (150, 0, -10 * s)), (1.8, 0.9, (175, 0, 10 * s))])
    for x in (-2.4, 0, 2.4):
        m.c("head", BD2, (x, 13.6, 7.6), (0.6, 2, 0.6), (-25, 0, x * 8))

    m.attacks = {"web": "spit", "leap": "leap", "brood": "drum", "poison": "fang"}
    m.melee = "fang"
    return m


@model
def elder_eye():
    """An elder guardian grown ancient on the sea floor: the pale grey-green box body with one huge eye,
    rows of orange spikes along every edge, a long segmented tail with a fin, sea grass and prismarine
    crust growing on its back."""
    Z0 = (0, 0, 0)
    m = Model("elder_eye", "float", 2.4)
    m.bone("core", "root", (0, 14, 0))
    m.bone("head", "core", (0, 14, 6))
    m.bone("ring1", "core", (0, 14, 0))
    m.bone("ring2", "core", (0, 14, -9))
    m.mbone("armL", "core", (7, 14, 0))
    m.bone("ring3", "core", (0, 14, -14))
    SH, SH2, SP, CR, EY = "light_gray_terracotta", "white_terracotta", "orange_terracotta", "prismarine", "white_concrete"
    bevel(m, "core", SH, (0, 14, 0), (12, 12, 12), 1.0)
    for s, side in ((1, "left"), (-1, "right")):
        grow(m, "core", side, (6 * s, 14, 0), 6, 6, 100 + s, {"A": SH2, "B": CR}, cover=0.45, px=2, depth=0.3)
    grow(m, "core", "top", (0, 20, 0), 6, 6, 103, {"A": CR, "B": "dark_prismarine"}, cover=0.7, px=2, depth=0.5)
    grow(m, "core", "bottom", (0, 8, 0), 6, 6, 104, {"A": SH2, "B": SH2}, cover=0.4, px=2, depth=0.3)
    vines(m, "core", (-4, -1, 3), 21.2, -2, (-3, -4, -2.6), "green_concrete", "green_concrete", 0.5)
    # the eye: a big white eye on the front with a dark slit pupil and an orange-red iris
    m.c("head", SH, (0, 14, 6.4), (10.4, 10.4, 0.8))
    paint(m, "head", "front", (0, 14, 6.85), [
        "..WWWW..",
        ".WWWWWW.",
        "WWROORWW",
        "WWOKKOWW",
        "WWOKKOWW",
        "WWROORWW",
        ".WWWWWW.",
        "..WWWW..",
    ], {"W": EY, "O": ("orange_concrete", 0.3, True), "R": "red_terracotta", "K": "black_concrete"}, px=1, depth=0.3)
    # spikes: orange spikes standing out of the middle of every face edge, like the vanilla guardian
    for (x, y, z, r) in ((6.4, 14, 3, (0, 0, -90)), (6.4, 14, -3, (0, 0, -90)), (-6.4, 14, 3, (0, 0, 90)), (-6.4, 14, -3, (0, 0, 90)),
                         (3, 20.4, 0, Z0), (-3, 20.4, 0, Z0), (0, 20.4, -3.5, Z0), (3, 7.6, 3, (180, 0, 0)), (-3, 7.6, -3, (180, 0, 0)),
                         (4, 14, -6.4, (-90, 0, 0)), (-4, 14, -6.4, (-90, 0, 0)), (0, 18, -6.4, (-90, 0, 0))):
        from models import dirof
        d = dirof(r)
        m.c("ring1", SP, (x + d[0] * 1.6, y + d[1] * 1.6, z + d[2] * 1.6), (1.2, 3.2, 1.2), r)
    # side fins
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, SP, (7.6 * s, 14, -2), (1, 6, 6), (0, 0, 20 * s))
        m.c(a, "orange_concrete", (8.4 * s, 14, -2), (0.4, 4, 4), (0, 0, 20 * s))
    # tail: three shrinking segments and a fin
    m.c("ring2", SH, (0, 14, -9), (6, 6, 6))
    m.c("ring2", SH2, (0, 14, -13.5), (4, 4, 4))
    m.c("ring3", SH, (0, 14, -17), (2.6, 2.6, 4))
    m.c("ring3", SP, (0, 14, -20), (0.6, 6, 4))
    m.attacks = {"sonic_boom": "pulse", "spikes": "spin", "darkness": "raise", "dive": "dive"}
    m.melee = "swipe"
    return m


@model
def rollshell():
    """A giant armadillo: banded brown and pink shell plates over a soft belly, a pointed snout with
    small dark eyes, big ears and a short armoured tail. It rolls into a ball and bowls into players."""
    m = Model("rollshell", "quad", 2.4)
    quad(m, body_y=9, legx=4.4, legz_front=5, legz_back=-6, neck_y=10, neck_z=9)
    SH, SH2, SK, SK2 = "brown_terracotta", "pink_terracotta", "white_terracotta", "terracotta"
    for s, (b, z) in ((1, ("legFL", 5)), (-1, ("legFR", 5)), (1, ("legBL", -6)), (-1, ("legBR", -6))):
        x = 4.4 * s
        m.c(b, SK2, (x, 4, z), (3, 6, 3))
        m.c(b, SK2, (x, 0.6, z + 0.8), (3.4, 1.2, 4.2))
        for t in (-1, 0, 1):
            m.c(b, "gray_terracotta", (x + t, 0.4, z + 3.2), (0.6, 0.8, 1))
    # the shell: arched bands front to back, alternating colours, pink rims
    m.c("body", SK, (0, 9.4, -0.5), (10, 5, 14))
    for k, (z, h, w) in enumerate(((-6, 8, 11), (-3, 10, 12.4), (0, 11, 13), (3, 10, 12.4), (6, 8, 11))):
        bevel(m, "body", SH if k % 2 == 0 else SH2, (0, 10 + h / 2 - 1, z), (w, h, 3.1), 1.2)
        m.c("body", SK2, (0, 10 + h - 1.3, z), (w - 2, 0.6, 3.2))
    for s in (1, -1):
        paint(m, "body", "left" if s > 0 else "right", (6.6 * s, 13, 0), ["S.S.S.S.S", ".S.S.S.S."], {"S": SK2}, px=1.4, depth=0.3)
    # head: a long snout, small black eyes, two big pink ears
    bevel(m, "head", SK2, (0, 10, 10.6), (4.6, 4.6, 5), 0.6)
    m.c("head", SK2, (0, 9, 14.2), (2.6, 2.6, 3))
    m.c("head", "black_concrete", (0, 9.2, 15.75), (1.4, 1, 0.2))
    for s in (1, -1):
        m.c("head", "black_concrete", (2.35 * s, 11, 12), (0.2, 1, 1))
        m.c("head", SH2, (1.8 * s, 14, 9.6), (1.4, 3.4, 2.2), (0, 0, -15 * s))
    m.c("head", SH, (0, 12.6, 10), (4.8, 0.8, 4))
    # tail: a short tapered armoured tail
    limb(m, "tail", SH, (0, 10, -8), [(3, 2.4, (-120, 0, 0)), (2.6, 1.6, (-150, 0, 0), SH2), (2, 1, (-170, 0, 0))])
    m.attacks = {"roll": "charge", "curl": "rear", "dig": "rear", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def queen_bee():
    """The queen of every hive: a round fuzzy bee as big as a cart, yellow and black bands, honey
    dripping from her, a gold crown on a fluffy head, clear wings, a dark stinger and a honeycomb sceptre."""
    m = Model("queen_bee", "float", 2.6)
    m.bone("core", "root", (0, 12, 0))
    m.bone("head", "core", (0, 13, 5))
    m.bone("ring1", "core", (0, 18, 0))
    m.bone("ring2", "core", (0, 12, -6))
    m.bone("ring3", "core", (0, 8, 0))
    m.mbone("armL", "core", (4, 9, 3))
    Y, K, H, H2, WG, GD = "yellow_wool", "black_wool", "honey_block", "honeycomb_block", "white_stained_glass", "gold_block"
    # the body: a round box in bands, fuzzy edges, a stinger, honey dripping from the belly
    bevel(m, "core", Y, (0, 12, -1), (10, 10, 14), 1.4)
    for z in (-5.2, 0.4):
        m.c("core", K, (0, 12, z), (10.4, 10.4, 2.4))
    m.c("core", Y, (0, 12, -8.2), (7, 7, 0.6))
    m.c("ring2", "gray_concrete", (0, 12, -9.6), (1, 1, 2.4))
    for (x, z, L) in ((-2, -3, 3), (2.4, 1.5, 2), (0.4, -6.5, 4)):
        m.c("core", H, (x, 7 - L / 2, z), (1.2, L, 1.2))
        m.c("core", H, (x, 7 - L - 0.4, z), (1.8, 1, 1.8))
    # wings: two pairs of clear glass panes with dark veins
    for s in (1, -1):
        m.c("ring1", WG, (5 * s, 18.4, -1), (6, 0.3, 8), (0, 0, 20 * s))
        m.c("ring1", WG, (4 * s, 18.6, -5), (4, 0.3, 5), (0, -20 * s, 25 * s))
        m.c("ring1", "light_gray_concrete", (5 * s, 18.55, -1), (5.6, 0.3, 0.3), (0, 0, 20 * s))
    # head: round and black-faced, big dark eyes with shine, antennae, a gold crown
    bevel(m, "head", Y, (0, 13, 7.6), (7.6, 7, 4), 1.0)
    paint(m, "head", "front", (0, 13, 9.65), [
        ".......",
        ".KW.WK.",
        ".KK.KK.",
        ".......",
        "...O...",
    ], {"K": "black_concrete", "W": "white_concrete", "O": "orange_concrete"}, px=1, depth=0.3)
    for s in (1, -1):
        limb(m, "head", K, (1.6 * s, 16.4, 8.6), [(2.4, 0.5, (20, 0, -20 * s)), (1.6, 0.5, (70, 0, -20 * s))])
    for k in range(5):
        a = k / 4 - 0.5
        h = 2.6 if k % 2 == 0 else 1.6
        m.c("head", GD, (a * 5, 16.6 + h / 2, 7.4), (1, h, 1))
    m.c("head", GD, (0, 16.8, 7.4), (5.6, 0.8, 3))
    m.c("head", "redstone_block", (0, 16.8, 8.95), (1, 0.6, 0.2), light=True)
    # legs as arms: little dark legs, the right one holding a honeycomb sceptre
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, K, (4 * s, 7.4, 3), (0.8, 3.4, 0.8), (0, 0, 20 * s))
    m.bone("sceptre", "armR", (-4.6, 6, 3))
    m.c("sceptre", "stripped_oak_log", (-5, 9, 4), (0.7, 8, 0.7))
    bevel(m, "sceptre", H2, (-5, 14, 4), (2.6, 2.6, 2.6), 0.4)
    m.c("sceptre", H, (-5, 14, 4), (2.9, 1, 2.9), light=True)
    m.attacks = {"minions": "pulse", "dive": "dive", "poison": "raise", "levitate": "spin"}
    m.melee = "swipe"
    return m


@model
def old_tusker():
    """The oldest hoglin in the nether, so old the crimson forest grows on it: a tan-pink hoglin body
    under a wiry orange-brown mane, a patch of crimson nylium and fungus on its back with glowing
    shroomlights, weeping vines hanging off its flanks, one tusk snapped off, a scarred snout."""
    m = Model("old_tusker", "quad", 2.2)
    quad(m, body_y=15, legx=6, legz_front=7, legz_back=-8, neck_y=17, neck_z=12)
    HI, HI2, MN, MN2, NY, FU, SL = "terracotta", "pink_terracotta", "orange_terracotta", "brown_terracotta", "crimson_nylium", "crimson_fungus", "shroomlight"
    for s, (b, z) in ((1, ("legFL", 7)), (-1, ("legFR", 7)), (1, ("legBL", -8)), (-1, ("legBR", -8))):
        x = 6 * s
        bevel(m, b, HI, (x, 10.5, z), (5.4, 8, 5.4), 0.8)
        m.c(b, HI2, (x, 4.6, z + 0.2), (4.6, 5, 4.6))
        m.c(b, "gray_terracotta", (x, 1, z + 0.5), (5, 2, 5.4))
        m.c(b, "black_terracotta", (x, 1, z + 3.1), (0.6, 2, 0.4))
    # body: the long hoglin barrel, a darker belly, the mane running from head to hips
    bevel(m, "body", HI, (0, 18, -1), (13, 11, 22), 1.6)
    m.c("body", HI2, (0, 13, -1), (11, 1.2, 19))
    for k, z in enumerate(range(9, -11, -3)):
        h = 4.6 - abs(k - 2) * 0.5
        m.c("body", MN if k % 2 == 0 else MN2, (0, 23.4 + h / 2, z), (3, h, 2.6), (-12, 0, 0))
    for s, side in ((1, "left"), (-1, "right")):
        grow(m, "body", side, (6.5 * s, 18, -1), 11, 5, 120 + s, {"A": HI2, "B": "brown_terracotta"}, cover=0.3, px=2, depth=0.3)
    # the crimson forest on its back: nylium, fungus, two shroomlights, roots
    grow(m, "body", "top", (0, 23.5, -4), 6, 6, 125, {"A": NY, "B": "nether_wart_block"}, cover=0.8, px=2, depth=0.7)
    for (x, z, h) in ((-3.4, -2, 3.4), (3.6, -6, 4.2), (-2, -10, 2.6)):
        m.c("body", "crimson_stem", (x, 24 + h / 2, z), (0.8, h, 0.8))
        m.c("body", FU, (x, 24.4 + h, z), (3.4, 1.4, 3.4))
        m.c("body", "red_terracotta", (x, 25.2 + h, z), (2, 0.8, 2))
    for (x, z) in ((2.8, 0.6), (-4.2, -6.4)):
        m.c("body", SL, (x, 25, z), (2.2, 2.2, 2.2), light=True)
    vines(m, "body", (-6.6, -6.6, 6.6, 6.6), 22, 0, (5, 8, 6, 3.4), "red_terracotta", "crimson_roots", 0.6, face_z=False)
    # tail
    limb(m, "tail", HI, (0, 19, -12), [(3, 1.4, (-150, 0, 0)), (2, 1, (-170, 0, 0))])
    m.c("tail", MN2, (0, 15.2, -13.6), (1.8, 1.8, 1.8))
    # head: the broad flat hoglin head held low, ears out, a long snout, one tusk whole and one broken
    bevel(m, "head", HI, (0, 15, 18), (12, 10, 10), 1.4)
    bevel(m, "head", HI2, (0, 12.4, 24), (8, 5, 3), 0.6)
    paint(m, "head", "front", (0, 12.6, 25.55), ["K....K", "......", "..SS.."], {"K": "black_concrete", "S": "pink_terracotta"}, px=1, depth=0.3)
    paint(m, "head", "front", (0, 17.6, 23.05), ["BBB....BBB", ".WK....KW."], {"B": MN2, "W": "white_concrete", "K": "black_concrete"}, px=1, depth=0.3)
    m.c("head", "pink_terracotta", (-3.2, 18.6, 23.15), (0.4, 3.2, 0.2), (0, 0, 20))
    for s in (1, -1):
        m.c("head", HI, (7 * s, 18, 16), (3, 1.4, 3.6), (0, 0, -30 * s))
    limb(m, "head", "bone_block", (4.2, 10.6, 24), [(3.2, 1.4, (-10, 0, -20)), (2.6, 1.1, (20, 0, -10)), (1.8, 0.8, (50, 0, 0))])
    limb(m, "head", "bone_block", (-4.2, 10.6, 24), [(1.6, 1.4, (-10, 0, 20))])
    m.c("head", "calcite", (-4.5, 12.2, 24.2), (1.5, 0.4, 1.5))
    for k in range(4):
        m.c("head", MN if k % 2 == 0 else MN2, (-1.8 + k * 1.2, 21.2, 15 - k * 0.6), (1.2, 3, 1.2), (-25, 0, 0))
    m.c("jaw", HI2, (0, 9.4, 20.5), (9, 1.8, 7))
    m.attacks = {"charge": "charge", "toss": "toss", "quake": "rear", "poison": "howl"}
    m.melee = "bite"
    return m
