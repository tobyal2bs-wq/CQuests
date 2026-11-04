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
    m.attacks = {"leap": "pounce", "frost": "howl", "minions": "rear", "roar": "charge"}
    m.melee = "bite"
    m.spawn = {"style": "assemble", "particle": "SNOWFLAKE", "sound": "ENTITY_WOLF_HOWL"}
    m.death = {"style": "ascend", "swap": "ice", "particle": "END_ROD", "sound": "ENTITY_WOLF_DEATH"}
    return m

@model
def killer_bunny():
    m = Model("killer_bunny", "quad", 1.55)
    quad(m, body_y=10, legx=5, legz_front=8, legz_back=-6, neck_y=22, neck_z=8)
    fur, fur2, pink = "white_wool", "snow_block", "pink_wool"
    # round body from stacked boxes, fluffy chest, cotton tail
    m.c("body", fur, (0, 16, -2), (16, 16, 18))
    m.c("body", fur, (0, 16, -2), (14, 18, 16))
    m.c("body", fur, (0, 16, -2), (18, 12, 14))
    m.c("body", fur2, (0, 17, 7.4), (11, 12, 3))
    m.c("body", fur2, (0, 15, -11.6), (6, 6, 4))
    m.c("body", fur, (0, 15, -12.6), (4, 4, 4))
    for x, y, z in ((3, 21, 8.4), (-2, 18, 8.8), (1, 14, 8.6)):
        m.c("body", "red_terracotta", (x, y, z), (1.4 + (x > 0), 1.2, 0.4))
    # small front paws, huge hind feet
    for s in (1, -1):
        b = "legFL" if s > 0 else "legFR"
        m.c(b, fur, (3 * s, 6, 8), (3.6, 7, 3.6))
        m.c(b, fur2, (3 * s, 2, 9.6), (3.6, 2.4, 4.6))
        m.c(b, "red_terracotta", (3 * s, 1.6, 12), (2.6, 0.4, 0.4))
        b = "legBL" if s > 0 else "legBR"
        m.c(b, fur, (6.4 * s, 9, -6), (5, 9, 9))
        m.c(b, fur2, (6.6 * s, 1.4, -2), (4.6, 2.8, 13))
        m.c(b, pink, (6.6 * s, 0.4, 4.2), (3.4, 0.6, 0.6))
    # head: round, red eyes, pink nose, blood on the muzzle, buck teeth; long ears, one flopped
    m.c("head", fur, (0, 28, 9), (13, 11, 11))
    m.c("head", fur2, (0, 25, 14.6), (8, 5, 2))
    m.m("head", fur, (5.6, 24.4, 11.4), (3, 4, 5))
    m.c("head", pink, (0, 27, 15.8), (2.2, 1.6, 0.8))
    m.m("head", "black_concrete", (3.4, 29.6, 14.55), (2.4, 2.4, 0.2))
    m.m("head", "red_concrete", (3.4, 29.6, 14.65), (1.6, 1.6, 0.1), light=True)
    m.m("head", "red_concrete", (3.6, 30, 14.7), (0.6, 0.6, 0.1))
    m.m("head", fur, (3.4, 32.3, 14.5), (3.6, 0.8, 0.6), (0, 0, 15))
    m.c("head", "white_concrete", (0, 23.4, 15.4), (2.6, 2.6, 0.6))
    m.c("head", "black_concrete", (0, 23.4, 15.75), (0.2, 2.6, 0.1))
    m.c("jaw", "red_terracotta", (0, 22, 14), (6, 1.4, 2.4))
    m.c("jaw", "red_concrete", (1.2, 21, 15), (1.4, 2, 0.6))
    m.c("jaw", fur2, (0, 21.4, 12), (7, 2, 4))
    limb(m, "head", fur, (2.6, 33, 8), [(9, 3.4, (-8, 0, -8)), (7, 3, (-12, 0, -4))])
    m.c("head", pink, (2.9, 38.4, 9.3), (1.6, 11, 0.4), (-10, 0, -7), (2.6, 33, 8))
    limb(m, "head", fur, (-2.6, 33, 8), [(6, 3.4, (-10, 0, 20)), (8, 3, (-60, 0, 80))])
    m.attacks = {"leap": "pounce", "minions": "howl", "shockwave": "rear"}
    m.melee = "bite"
    m.spawn = {"style": "grow", "particle": "HEART", "sound": "ENTITY_RABBIT_ATTACK"}
    m.death = {"style": "explode", "swap": "", "particle": "CLOUD", "sound": "ENTITY_RABBIT_DEATH"}
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
    m.attacks = {"detonate": "rear", "leap": "pounce", "pull": "howl"}
    m.melee = "toss"
    m.spawn = {"style": "unfold", "particle": "SMOKE", "sound": "ENTITY_CREEPER_PRIMED"}
    m.death = {"style": "explode", "swap": "tnt", "particle": "EXPLOSION", "sound": "ENTITY_GENERIC_EXPLODE"}
    return m

@model
def headless_horseman():
    m = Model("headless_horseman", "quad", 1.5)
    quad(m, body_y=26, legx=4.6, legz_front=10, legz_back=-10, neck_y=36, neck_z=12)
    m.bone("rider", "body", (0, 38, -1))
    m.bone("riderArmR", "rider", (-5.6, 52, -1))
    m.bone("riderArmL", "rider", (5.6, 52, -1))
    horse, bone, flame, armor = "black_terracotta", "bone_block", "orange_stained_glass", "polished_blackstone"
    # dark horse: barrel body, bony ribs, saddle and blanket
    m.c("body", horse, (0, 31, 0), (10, 10, 24))
    for z in (-4, -1, 2, 5):
        m.m("body", bone, (5.1, 31, z), (0.4, 8, 1.2))
    m.c("body", "red_wool", (0, 36.4, -1), (11, 1, 10))
    m.m("body", "red_wool", (5.6, 33, -1), (0.4, 6, 10))
    m.m("body", "gold_block", (5.7, 30.2, -1), (0.4, 0.6, 10.2))
    m.c("body", "dark_oak_planks", (0, 37.4, -1), (7, 1.6, 7))
    for leg, z in (("legFL", 10), ("legBL", -10)):
        for s, b in ((1, leg), (-1, leg[:-1] + "R")):
            m.c(b, horse, (4.6 * s, 21, z), (3.6, 10, 4))
            m.c(b, bone, (4.6 * s, 11, z), (2.4, 10, 2.4))
            m.c(b, horse, (4.6 * s, 5, z), (2.8, 3, 2.8))
            m.c(b, "shroomlight", (4.6 * s, 1.4, z), (3.4, 2.8, 3.4), light=True)
            m.c(b, flame, (4.6 * s, 3.4, z), (4, 2, 4), light=True)
    # neck, skull face, burning mane
    m.c("head", horse, (0, 39, 14), (5, 13, 6), (-30, 0, 0), (0, 36, 12))
    m.c("head", bone, (0, 45, 21), (5, 5, 11), (20, 0, 0), (0, 45, 18))
    m.c("head", "calcite", (0, 46.8, 18), (5.4, 2, 5))
    m.m("head", "black_concrete", (2.2, 46, 19), (1.4, 1.6, 2), )
    m.m("head", "orange_concrete", (2.75, 46, 19), (0.3, 0.8, 0.8), light=True)
    m.m("head", bone, (1.8, 49.4, 16.6), (1, 2.6, 1))
    m.c("jaw", bone, (0, 41.8, 22.6), (4.4, 1.4, 7), (20, 0, 0), (0, 43, 19))
    for i, y in enumerate((48, 45, 42, 39)):
        m.c("head", flame, (0, y + 1.2, 14 - i * 0.7), (1.4, 4 + i % 2, 3), (-30, 0, 0), light=True)
        m.c("head", "shroomlight", (0, y, 13.6 - i * 0.7), (0.8, 2, 2), (-30, 0, 0), light=True)
    limb(m, "tail", flame, (0, 33, -12), [(5, 2.4, (-150, 0, 0)), (5, 2, (-175, 0, 0)), (4, 1.4, (170, 0, 0))], light=True)
    # the rider: no head, flames rise from the collar; armor, a cape, a scythe and a jack o'lantern
    for s in (1, -1):
        m.c("rider", "black_wool", (3.6 * s, 37.6, 1), (3, 3, 7))
        m.c("rider", "black_wool", (5.4 * s, 32.6, 3.4), (2.4, 8, 2.6))
        m.c("rider", "black_terracotta", (5.4 * s, 28.6, 4.4), (2.8, 2, 4))
    m.c("rider", armor, (0, 45, -1), (9, 11, 5))
    m.c("rider", "black_wool", (0, 40, -1), (9.4, 2, 5.4))
    m.c("rider", "gold_block", (0, 40, 1.8), (2, 2, 0.4))
    m.c("rider", "polished_blackstone_bricks", (0, 47, 1.7), (6, 6, 0.6))
    m.c("rider", "red_wool", (0, 51.4, -1), (10.4, 2, 6))
    m.c("rider", "black_wool", (0, 52.6, -1), (6, 1.4, 4))
    for i, (x, h) in enumerate(((0, 5), (-1.4, 3.4), (1.4, 3.8))):
        m.c("rider", flame, (x, 53.5 + h / 2, -1), (1.6, h, 1.6), (0, 45, 0), light=True)
    m.c("rider", "shroomlight", (0, 54, -1), (2.6, 1.4, 2.6), light=True)
    m.c("rider", "black_wool", (0, 42, -5.6), (10, 18, 0.8), (14, 0, 0), (0, 51, -4))
    for i, x in enumerate((-3.4, 0, 3.4)):
        m.c("rider", "red_wool", (x, 31.6 - i % 2, -8.2), (3, 3 + i % 2, 0.8), (14, 0, 0), (0, 51, -4))
    for s, a in ((1, "riderArmL"), (-1, "riderArmR")):
        m.c(a, armor, (6.4 * s, 52, -1), (3.6, 2.6, 4.6))
        m.c(a, "black_wool", (6.4 * s, 47.4, -0.4), (2.6, 7, 2.6))
        m.c(a, armor, (6.4 * s, 43, 1), (2.8, 3.6, 3), (-40, 0, 0))
    m.c("riderArmL", "jack_o_lantern[facing=south]", (6.6, 40.4, 4), (4.4, 4.4, 4.4), light=True)
    m.c("riderArmR", "dark_oak_log", (-6.6, 46, 3), (1.2, 30, 1.2), (-10, 0, 0))
    m.c("riderArmR", "iron_block", (-6.6, 60.6, 4.6), (1, 1.4, 1.4))
    limb(m, "riderArmR", "iron_block", (-6.6, 60.6, 5), [(5, 1, (90, 0, 0)), (4, 0.8, (120, 0, 0)), (3, 0.6, (150, 0, 0))])
    m.attacks = {"volley": "rear", "fire_ring": "howl", "darkness": "toss", "minions": "charge"}
    m.melee = "bite"
    m.spawn = {"style": "drop", "particle": "FLAME", "sound": "ENTITY_SKELETON_HORSE_DEATH"}
    m.death = {"style": "burn", "swap": "", "particle": "FLAME", "sound": "ENTITY_SKELETON_HORSE_DEATH"}
    return m
