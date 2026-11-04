from models import *

@model
def bloodtusk():
    m = Model("bloodtusk", "quad", 1.6)
    quad(m, body_y=17, legx=7, legz_front=9, legz_back=-11, neck_y=25, neck_z=15)
    hide, belly, mane = "terracotta", "pink_terracotta", "nether_wart_block"
    m.c("body", hide, (0, 26, 6), (17, 17, 16))
    m.c("body", hide, (0, 24, -8), (15, 14, 14))
    m.c("body", belly, (0, 17.4, 0), (13, 2, 24))
    m.c("body", "brown_terracotta", (0, 29, -1), (14.4, 9, 28))
    for x, y, z in ((8.6, 28, 9), (-8.6, 24, 3), (7.6, 22, -10), (-7.6, 28, -12)):
        m.c("body", "brown_terracotta", (x, y, z), (0.4, 4, 3))
    for y, z in ((19, 13), (21, 9), (19, 5)):
        m.m("body", "pink_terracotta", (8.6, y, z), (0.4, 1.4, 2))
    # a ridge of red bristles from the head to the rump, fungus growing out of it
    for i, (z, h) in enumerate(((13, 6), (9, 8), (5, 9), (1, 8), (-3, 7), (-7, 5), (-11, 4))):
        m.c("body", mane, (0, 33 + h / 2 - (0 if z > 0 else 2), z), (5, h, 3.6), (-15, 0, 0))
        m.m("body", mane, (3, 33 + h / 3 - (0 if z > 0 else 2), z + 0.6), (2, h * 0.6, 3), (-15, 0, -20))
    for x, z, k in ((5, 2, "crimson_fungus"), (-5, -4, "crimson_roots"), (4, -9, "crimson_roots"), (-4, 7, "crimson_fungus")):
        m.c("body", k, (x, 33.6, z), (5, 5, 5))
    for x, z in ((8.6, 4), (-8.6, -6), (8.6, -9)):
        m.c("body", "crimson_nylium", (x, 25, z), (0.6, 4, 5))
    m.m("body", "red_terracotta", (8.6, 21, 8), (0.4, 5, 0.8), (0, 0, 20))
    m.m("body", "red_terracotta", (8.6, 23, 6), (0.4, 4, 0.8), (0, 0, 30))
    for leg, z in (("legFL", 9), ("legBL", -11)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, hide, (7 * s, 12.6, z), (6, 9, 6))
            m.c(b, hide, (7 * s, 5, z), (4.6, 7, 4.6))
            m.c(b, "black_terracotta", (7 * s, 1, z + 0.4), (5.4, 2, 6))
            m.c(b, "black_terracotta", (7 * s, 1, z + 3.6), (1, 1.6, 1.4))
    # head: wide, flat snout, little furious eyes, enormous tusks from the lower jaw
    m.c("head", hide, (0, 24, 22), (14, 11, 12))
    m.c("head", "white_terracotta", (0, 21, 29.6), (9, 6, 3.4))
    m.m("head", "black_terracotta", (2.2, 21.4, 31.35), (1.8, 2.2, 0.2))
    m.m("head", "black_concrete", (4.8, 26, 28.05), (2, 1.4, 0.2))
    m.m("head", "red_concrete", (4.8, 26, 28.15), (1, 0.8, 0.1), light=True)
    m.c("head", mane, (0, 29.8, 22), (6, 2.6, 10))
    m.m("head", hide, (8, 28.5, 20), (2, 4, 4), (0, 0, -60), (7, 27, 20))
    m.c("jaw", hide, (0, 17.6, 25), (12, 3, 9))
    mhorn(m, "jaw", "bone_block", (5.4, 18.4, 28), 4, (-30, 0, -25), (-28, 0, 10), 2.4, 0.78)
    m.c("tail", hide, (0, 19, -16.6), (1.4, 6, 1.4), (20, 0, 0), (0, 22, -15))
    m.c("tail", mane, (0, 15.8, -17.8), (2.4, 2.4, 2.4))
    m.attacks = {"leap": "pounce", "shockwave": "rear", "minions": "howl", "roar": "charge"}
    m.melee = "toss"
    m.spawn = {"style": "spiral", "particle": "CRIMSON_SPORE", "sound": "ENTITY_HOGLIN_ANGRY"}
    m.death = {"style": "topple", "swap": "", "particle": "CRIMSON_SPORE", "sound": "ENTITY_HOGLIN_DEATH"}
    return m

@model
def ruinmaw():
    m = Model("ruinmaw", "quad", 1.6)
    quad(m, body_y=18, legx=7.6, legz_front=9, legz_back=-12, neck_y=26, neck_z=15)
    rot, rot2, bone, dark = "green_terracotta", "lime_terracotta", "bone_block", "black_terracotta"
    m.c("body", rot, (0, 28, 6), (18, 18, 16))
    m.c("body", rot2, (0, 37, 6), (14, 3, 12))
    m.c("body", dark, (0, 25, -7), (13, 12, 13))
    # exposed ribs over the hollow rear half, a spine of bones
    for z in (-2, -5.4, -8.8, -12):
        m.m("body", bone, (6.8, 25, z), (1.2, 12, 1.4), (0, 0, -8))
        m.c("body", bone, (0, 31.4, z), (12.6, 1.4, 1.4))
    m.c("body", bone, (0, 31.6, -7), (2.2, 2.2, 15))
    for z in (14, 10, 6, 2, -3, -8, -13):
        m.c("body", bone, (0, (38.6 if z > 0 else 33), z), (1.4, 3.4, 1.4), (-20, 0, 0))
    for x, y, z, w, h in ((-6, 30, 12, 6, 5), (5, 24, 8, 5, 6), (-3, 36, 2, 6, 3)):
        m.c("body", "moss_block", (x, y, z), (w, h, 1) if abs(z) > 10 else (w, h, w), )
    m.m("body", "brown_mushroom", (5, 39, 4), (4, 4, 4))
    for leg, z in (("legFL", 9), ("legBL", -12)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, rot if leg == "legFL" else dark, (7.6 * s, 12.6, z), (6.6, 10, 6.6))
            m.c(b, bone, (7.6 * s, 5, z), (3, 8, 3))
            m.c(b, rot2, (7.6 * s, 7, z + 0.4), (5, 3, 5))
            m.c(b, dark, (7.6 * s, 1, z + 0.6), (5.4, 2, 6.6))
    m.c("legFL", "chain", (7.6, 6, 13), (0.6, 0.6, 10), (0, 30, 0))
    m.c("legFL", "iron_block", (7.6, 8.6, 9), (7, 1.6, 7))
    # head: half flesh, half bare skull; one tusk broken off
    m.c("head", rot, (2, 25, 22), (9, 11, 12))
    m.c("head", "calcite", (-3.6, 25, 22), (6, 10.6, 11.6))
    m.c("head", "calcite", (0, 22, 30), (10, 6, 4))
    m.c("head", "black_concrete", (-3.6, 26.4, 27.95), (3, 2.4, 0.2))
    m.c("head", "lime_concrete", (-3.6, 26.4, 28.05), (1.2, 1.2, 0.1), light=True)
    m.c("head", "black_concrete", (4.4, 26.4, 28.05), (2, 1.2, 0.2))
    m.c("head", "red_concrete", (4.4, 26.4, 28.15), (1, 0.8, 0.1), light=True)
    m.m("head", "black_concrete", (2, 22.4, 32.05), (1.4, 2, 0.2))
    m.c("head", rot2, (3, 30.6, 21), (6, 1.6, 8))
    m.c("jaw", rot, (0, 18.4, 26), (11, 3, 10))
    for x in (-4, -2, 0, 2, 4):
        m.c("jaw", "white_concrete", (x, 20.2, 30.4), (0.8, 1.2 + (x % 4 == 0) * 0.8, 0.8))
    horn(m, "jaw", bone, (5, 19.4, 29), 4, (-30, 0, -25), (-25, 0, 10), 2.4, 0.78)
    horn(m, "jaw", bone, (-5, 19.4, 29), 1, (-30, 0, 25), (0, 0, 0), 2.4)
    m.c("jaw", "white_concrete", (-6.2, 22.4, 29.6), (1.6, 0.6, 1.6), (0, 0, 30))
    m.c("tail", bone, (0, 19.6, -21), (1.4, 1.4, 8), (-40, 0, 0), (0, 23, -18))
    # raw flesh where the hide has rotted away, strips hanging off the ribs, flies of moss
    for x, y, z, w, h, d in ((6.2, 30, 9, 0.8, 6, 5), (-9.05, 27, 3, 0.6, 7, 6), (2, 37.1, 9, 6, 0.4, 4), (-9.05, 23, 10, 0.6, 3, 4)):
        m.c("body", "red_terracotta", (x, y, z), (w, h, d))
    for x, z, h in ((6.6, -3.6, 5), (-6.6, -7, 7), (6.6, -10.4, 4), (-6.6, -2, 3)):
        m.c("body", rot2, (x, 19.6 - h / 2 + 2, z), (0.8, h, 1.6))
    # spine plates, broken chains still locked round the neck and a back leg
    for z in (12, 6, 0):
        m.c("body", dark, (0, 37.8 if z > 4 else 37.2, z), (6, 1, 4))
    m.c("body", "iron_block", (0, 30, 14.4), (19, 2, 2))
    for x, r in ((-8, 20), (8.5, -35), (3, 5)):
        m.c("body", "chain", (x, 25.4, 15.6), (0.6, 8, 0.6), (r, 0, 0))
    m.c("legBR", "iron_block", (-7.6, 8.6, -12), (7, 1.6, 7))
    m.c("legBR", "chain", (-7.6, 4, -16), (0.6, 0.6, 8), (0, -20, 0))
    # split hooves
    for leg, z in (("legFL", 9), ("legBL", -12)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, "black_concrete", (7.6 * s, 1, z + 3.95), (0.4, 2, 0.4))
    # head: a torn ear, nostrils, bare teeth along the skull side, a crack glowing in the skull
    m.c("head", rot, (6.6, 29, 18), (3, 2, 5), (0, 0, -30))
    m.c("head", rot2, (7.6, 28.6, 16), (1.6, 1.4, 1.6), (0, 0, -30))
    m.c("head", "calcite", (-7, 29.4, 18), (2, 4, 3), (0, 0, 40))
    m.c("head", "black_concrete", (-1.2, 23, 32.05), (0.8, 0.8, 0.2))
    m.c("head", "black_concrete", (1.6, 23, 32.05), (0.8, 0.8, 0.2))
    for z in (24, 26, 28):
        m.c("head", "white_concrete", (-6.65, 21.4, z), (0.4, 1.4, 0.8))
    m.c("head", "lime_stained_glass", (-4, 29.8, 22), (0.6, 3.6, 0.6), (0, 0, 25), light=True)
    # bony tail with a tuft
    m.c("tail", bone, (0, 15.4, -25.2), (1.2, 1.2, 4), (-60, 0, 0), (0, 17, -24))
    m.c("tail", rot2, (0, 13, -27), (2.4, 2.4, 2.4))
    m.attacks = {"leap": "pounce", "quake": "rear", "shockwave": "charge", "roar": "howl"}
    m.melee = "bite"
    m.spawn = {"style": "rise", "particle": "MYCELIUM", "sound": "ENTITY_ZOGLIN_ANGRY"}
    m.death = {"style": "dissolve", "swap": "", "particle": "MYCELIUM", "sound": "ENTITY_ZOGLIN_DEATH"}
    return m

@model
def fenrir():
    m = Model("fenrir", "quad", 1.6)
    quad(m, body_y=22, legx=5.4, legz_front=10, legz_back=-12, neck_y=31, neck_z=14)
    fur, fur2, dark, rune = "light_gray_wool", "white_wool", "gray_wool", "light_blue_concrete"
    # deep chest, narrow waist, layered ruff
    m.c("body", fur, (0, 30, 8), (13, 15, 12))
    m.c("body", fur, (0, 29, -3), (10, 10, 12))
    m.c("body", fur, (0, 28.6, -12), (11, 11, 8))
    m.c("body", fur2, (0, 26, 13), (11, 10, 4))
    for i, (y, w) in enumerate(((39, 12), (35, 15), (31, 15.6))):
        m.c("body", fur2 if i % 2 else fur, (0, y, 12 + i * 0.4), (w, 4, 8), (-15, 0, 0))
    for z in (4, 0, -4, -8):
        m.c("body", dark, (0, 34.8 - (z < 0) * 1, z), (6, 1.4, 3), (-10, 0, 0))
    for x, z, h in ((6.6, 0, 4), (6.6, -5, 3), (-6.6, 0, 4)):
        m.c("body", rune, (x, 29, z), (0.2, h, 0.8), (0, 0, 0), light=True)
        m.c("body", rune, (x, 29 + h / 2 - 0.4, z + 0.8), (0.2, 0.8, 1.6), light=True)
    # collar with a broken chain
    m.c("body", "iron_block", (0, 34, 15.6), (11, 2, 2), (-30, 0, 0))
    m.c("body", "chain", (2, 30, 17.6), (0.7, 6, 0.7), (20, 0, 20))
    m.c("body", "chain", (2.6, 25.6, 19), (0.7, 4, 0.7), (60, 0, 0))
    m.c("body", "iron_block", (2.6, 24.8, 21), (1.8, 1.8, 1.4))
    for leg, z in (("legFL", 10), ("legBL", -12)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            if leg == "legFL":
                m.c(b, fur, (5.4 * s, 17, z), (4.4, 11, 4.4))
                m.c(b, fur, (5.4 * s, 7, z + 0.6), (3.4, 10, 3.4))
            else:
                m.c(b, fur, (5.4 * s, 17.4, z), (5, 10, 6), (-15, 0, 0))
                m.c(b, fur, (5.4 * s, 8, z - 2), (3.2, 8, 3.2), (20, 0, 0))
                m.c(b, fur, (5.4 * s, 3, z - 0.6), (3, 5, 3))
            m.c(b, dark, (5.4 * s, 0.8, z + 1.2), (4, 1.6, 5))
            for dx in (-1.2, 0, 1.2):
                m.c(b, "white_concrete", (5.4 * s + dx, 0.6, z + 4), (0.6, 1, 1))
    # head: long snout, snarl, pointed ears, glowing eyes
    m.c("head", fur, (0, 34, 21), (10, 9, 9))
    m.c("head", fur, (0, 32, 29.6), (6, 5, 9))
    m.c("head", fur2, (0, 34.6, 28), (5, 1, 7), (-8, 0, 0))
    m.c("head", "black_wool", (0, 33.4, 34.3), (2.4, 1.8, 0.6))
    m.c("head", fur2, (0, 37.8, 21.6), (8, 1.4, 6))
    m.m("head", "black_concrete", (2.8, 35.4, 25.55), (2, 1, 0.2))
    m.m("head", "light_blue_concrete", (2.8, 35.4, 25.65), (1.2, 0.6, 0.1), light=True)
    m.m("head", fur, (3, 40.6, 19.4), (2.6, 5, 2), (-10, 0, -12))
    m.m("head", dark, (3, 40.4, 20.5), (1.4, 3.4, 0.2), (-10, 0, -12))
    for x in (-2.2, -0.8, 0.8, 2.2):
        m.c("head", "white_concrete", (x, 29, 33.4), (0.6, 1.4, 0.6))
    m.m("head", "white_concrete", (2.6, 29.2, 31), (0.8, 2.2, 0.8))
    m.c("jaw", fur, (0, 28.2, 29), (5.4, 2, 9))
    m.c("jaw", "red_terracotta", (0, 29.3, 29.4), (4, 0.4, 7))
    # big tail sweeping up
    limb(m, "tail", fur, (0, 31, -15), [(5, 4, (-60, 0, 0)), (5, 4.6, (-35, 0, 0)), (4, 3.6, (-10, 0, 0), fur2), (3, 2.4, (15, 0, 0), fur2)])
    # shaggy hackles down the neck and back, darker saddle, a pale belly
    for k, z in enumerate((14, 10, 6, 2, -2, -6, -10, -14)):
        h = 3.4 - k * 0.25
        m.c("body", dark if k % 2 else fur, (0, (38 if z > 8 else 35.4 - (z < -4) * 0.8) + h / 2, z), (4 - k * 0.2, h, 2.6), (-30, 0, 0))
    m.c("body", dark, (0, 34.3, -6), (9, 1, 14))
    m.c("body", fur2, (0, 22.4, 2), (8, 1.4, 18))
    for s in (1, -1):
        for z in (6, 2):
            m.c("body", fur2, (6.6 * s, 24 + (z == 2) * 1.4, z), (1, 4, 3), (0, 0, 10 * s))
    # runes of the binding: more of them, and the broken fetter still clamped on a hind leg
    for x, z, h in ((-6.6, -6, 3), (5.2, -12.5, 2.4), (-5.2, -12.5, 2.4)):
        m.c("body", rune, (x, 29.4, z), (0.2 if abs(x) > 6 else 0.8, h, 0.8 if abs(x) > 6 else 0.2), light=True)
    m.c("legBL", "iron_block", (5.4, 5, -12.6), (4.4, 1.8, 4.4))
    m.c("legBL", "chain", (5.4, 3.4, -16), (0.6, 0.6, 6), (-20, 0, 0))
    m.c("legBL", rune, (7.65, 5, -12.6), (0.2, 1, 1.6), light=True)
    # head: a brow ridge, cheek ruff, scarred muzzle, frost breath curling from the jaws
    m.c("head", dark, (0, 37, 25.4), (9, 1.2, 1.4))
    m.m("head", fur2, (5.4, 32.4, 22), (2, 5, 5), (0, 0, 12))
    m.c("head", "red_terracotta", (1.8, 33.2, 32), (0.6, 3, 0.2), (0, 0, 30))
    m.m("head", "gray_wool", (3.1, 32.8, 30), (0.2, 1, 6))
    m.c("jaw", "light_blue_stained_glass", (0, 27.6, 35), (3, 1.6, 2), light=True)
    m.c("jaw", "white_stained_glass", (0, 28.4, 37.4), (2, 1.2, 2), light=True)
    m.attacks = {"leap": "pounce", "frost": "howl", "minions": "rear", "roar": "charge"}
    m.melee = "bite"
    m.spawn = {"style": "assemble", "particle": "SNOWFLAKE", "sound": "ENTITY_WOLF_HOWL"}
    m.death = {"style": "ascend", "swap": "ice", "particle": "END_ROD", "sound": "ENTITY_WOLF_DEATH"}
    return m

@model
def volatile_colossus():
    m = Model("volatile_colossus", "quad", 1.75)
    quad(m, body_y=8, legx=3.6, legz_front=3.8, legz_back=-3.8, neck_y=30, neck_z=0)
    g1, g2, g3, g4 = "lime_concrete", "green_concrete", "lime_terracotta", "moss_block"
    for leg, z in (("legFL", 3.8), ("legBL", -3.8)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, g2, (3.6 * s, 4, z), (4.4, 8, 4.4))
            m.c(b, g1, (3.6 * s + 1 * s, 5, z + (1.6 if z > 0 else -1.6)), (2, 3, 1.4))
            m.c(b, "black_concrete", (3.6 * s, 0.4, z + (2 if z > 0 else -2)), (3.6, 0.8, 0.8))
    # body column with camo pixels, cracks showing TNT inside, strapped TNT and a belt
    m.c("body", g2, (0, 19, 0), (10, 22, 7.4))
    for x, y, z, k in ((-3, 12, 3.8, g1), (2.6, 16, 3.8, g3), (-1, 23, 3.8, g1), (3, 27, 3.8, g4), (-3.4, 19, -3.8, g3),
                       (2.4, 13, -3.8, g1), (5.1, 14, 1, g1), (-5.1, 22, -1, g3), (5.1, 25, -2, g4)):
        m.c("body", k, (x, y, z), (2.6 if abs(x) < 5 else 0.4, 2.6, 0.4 if abs(x) < 5 else 2.6))
    m.c("body", "tnt", (1, 20, 2.4), (4, 4, 3), light=True)
    m.c("body", "black_concrete", (1, 20, 3.75), (1.4, 6, 0.3), (0, 0, 25))
    m.c("body", "red_concrete", (1, 20, 3.8), (0.6, 4, 0.3), (0, 0, 25), light=True)
    m.c("body", "brown_terracotta", (0, 15, 0), (10.6, 1.6, 8))
    m.c("body", "iron_block", (0, 15, 4.05), (1.6, 1.6, 0.4))
    for x in (-3, 0, 3):
        m.c("body", "tnt", (x, 21, -5.2), (2.6, 9, 2.6))
        m.c("body", "chain", (x, 26.2, -5.2), (0.4, 1.4, 0.4))
    m.c("body", "brown_terracotta", (0, 24, -5.2), (10.4, 1.2, 3.2))
    # head: the famous face, a lit fuse on top
    m.c("head", g1, (0, 35.5, 0), (12, 11, 11))
    for x, y, z, k in ((-4, 39, 5.55, g2), (3, 40, 5.55, g3), (4.5, 32, 5.55, g2), (-5, 33, 5.55, g4), (0, 40.6, 2, g2),
                       (6.05, 36, 2, g2), (-6.05, 34, -2, g3), (6.05, 38, -3, g4), (0, 34, -5.55, g2)):
        m.c("head", k, (x, y, z), (2.6 if abs(x) < 6 else 0.2, 2.6 if y < 40.5 else 0.2, 0.2 if abs(z) > 5 else 2.6))
    for x in (-2.6, 2.6):
        m.c("head", "black_concrete", (x, 37.2, 5.6), (3, 3, 0.3))
    m.c("head", "black_concrete", (0, 33.6, 5.6), (2.6, 3.4, 0.3))
    m.m("head", "black_concrete", (2.2, 31.8, 5.6), (1.6, 3, 0.3))
    m.m("head", "red_concrete", (2.6, 37.2, 5.75), (0.8, 0.8, 0.1), light=True)
    m.c("head", "chain", (0, 42.2, 0), (0.8, 2.4, 0.8), (0, 0, 15))
    m.c("head", "end_rod", (-0.6, 44.2, 0), (1.6, 1.6, 1.6), light=True)
    # cracks in the skin glowing with the charge building inside
    for x, y, z, w, h, d, r in ((-2.6, 26, 3.75, 0.5, 5, 0.3, 30), (-3.6, 28.4, 3.75, 0.5, 2.6, 0.3, -40), (3.4, 11, 3.75, 0.5, 4, 0.3, -20),
                                (5.05, 19, 0, 0.3, 5, 0.5, 15), (-5.05, 13, 1, 0.3, 4, 0.5, -25), (-2, 16, -3.75, 0.5, 5, 0.3, 35)):
        m.c("body", "red_stained_glass", (x, y, z), (w, h, d), (0, 0, r), light=True)
    m.c("head", "red_stained_glass", (4.6, 39.6, 5.65), (0.5, 3.4, 0.2), (0, 0, -30), light=True)
    m.c("head", "red_stained_glass", (-6.1, 38, 1), (0.2, 3, 0.5), (25, 0, 0), light=True)
    # a bandolier of dynamite across the chest and a detonator on the back
    m.c("body", "brown_terracotta", (0, 21, 3.9), (1.4, 15, 0.5), (0, 0, -38))
    for k in range(4):
        t = -4.5 + k * 3
        m.c("body", "red_concrete", (t * 0.62, 21 + t * 0.79, 4.4), (1, 2.6, 0.8), (0, 0, -38))
        m.c("body", "white_concrete", (t * 0.62, 21 + t * 0.79, 4.85), (1.05, 0.5, 0.2), (0, 0, -38))
    m.c("body", "iron_block", (0, 28.4, -5.4), (5, 3, 2))
    m.c("body", "redstone_lamp", (-1.2, 28.4, -6.5), (1.6, 1.6, 0.4), light=True)
    m.c("body", "lever", (1.4, 30.4, -5.6), (1, 2, 1))
    m.c("body", "red_wool", (0, 31.6, -4.6), (0.5, 4, 0.5), (-25, 0, 0))
    # a neck ring of darker skin and toes on every foot
    m.c("head", g2, (0, 30.4, 0), (10.6, 1.4, 8.4))
    for leg, z in (("legFL", 3.8), ("legBL", -3.8)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            for k in (-1, 1):
                m.c(b, g2, (3.6 * s + k * 1.2, 0.7, z + (2.6 if z > 0 else -2.6)), (1.4, 1.4, 1.6))
            m.c(b, g3, (3.6 * s, 7.4, z), (4.8, 1, 4.8))
    m.attacks = {"detonate": "rear", "leap": "pounce", "pull": "howl"}
    m.melee = "toss"
    m.spawn = {"style": "unfold", "particle": "SMOKE", "sound": "ENTITY_CREEPER_PRIMED"}
    m.death = {"style": "explode", "swap": "tnt", "particle": "EXPLOSION", "sound": "ENTITY_GENERIC_EXPLODE"}
    return m

