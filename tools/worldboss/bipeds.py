from models import *

@model
def frost_jarl():
    m = Model("frost_jarl", "biped", 1.7)
    biped(m, hip=19, legx=4, neck=37, shoulder=35, armx=10.5)
    m.bone("jaw", "head", (0, 38, 3))
    m.bone("cape", "body", (0, 37, -5))
    m.bone("axe", "armR", (-11, 16.8, 1))
    skin = "light_blue_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "white_wool", (4 * s, 3, 0.6), (6.4, 6, 7.6))
        m.c(b, "light_gray_wool", (4 * s, 6.4, 0.4), (7, 1.8, 7.2))
        m.c(b, "spruce_planks", (4 * s, 0.6, 1), (6.6, 1.2, 8.4))
        m.c(b, "brown_wool", (4 * s, 13, 0), (5.4, 12, 5.6))
        m.c(b, "iron_block", (4 * s, 11.5, 2.9), (4.2, 3.6, 0.8))
        for y in (9, 15):
            m.c(b, "brown_terracotta", (4 * s, y, 0), (5.8, 0.8, 6))
    # belt, chainmail torso, straps, fur mantle
    m.c("hips", "brown_terracotta", (0, 21.5, 0), (16.5, 3.4, 10.4))
    m.c("hips", "gold_block", (0, 21.5, 5.3), (4, 3.8, 0.8))
    m.c("hips", "diamond_block", (0, 21.5, 5.75), (1.6, 1.6, 0.4), light=True)
    m.c("hips", "brown_wool", (0, 16, 4.6), (6, 8, 0.8))
    m.c("hips", "white_wool", (0, 12.2, 4.6), (6.4, 1, 0.9))
    m.c("body", "light_gray_concrete", (0, 29, 0), (15, 13, 9))
    m.c("body", "polished_andesite", (0, 30, 4.3), (12, 9, 0.8))
    m.c("body", skin, (0, 35, 2.5), (7, 3, 4))
    m.c("body", "brown_terracotta", (0, 29.5, 4.9), (2.2, 16, 0.6), (0, 0, 38))
    m.c("body", "iron_block", (2.2, 32.2, 5.3), (1.6, 1.6, 0.4), (0, 0, 38))
    m.c("body", "brown_terracotta", (0, 29.5, -4.9), (2.2, 16, 0.6), (0, 0, 38))
    m.c("body", "white_wool", (0, 36, -0.5), (19, 4, 11))
    m.c("body", "light_gray_wool", (0, 38.2, -1.4), (15, 1.6, 9))
    for x in (-8, -4, 0, 4, 8):
        m.c("body", "white_wool", (x, 33.4, 5), (3.4, 1.8 + (abs(x) % 8) * 0.15, 1.4))
    # arms: blue skin, fur pauldrons, iron bracers
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "white_wool", (11 * s, 36.4, 0), (7, 4, 8))
        m.c(a, "iron_block", (11.6 * s, 35, 0), (6, 2.6, 7.2), (0, 0, -16 * s))
        m.c(a, skin, (11 * s, 29, 0), (5, 9, 5))
        m.c(a, "iron_block", (11 * s, 21.5, 0.4), (5.6, 6, 5.6))
        m.c(a, "brown_terracotta", (11 * s, 24.8, 0.4), (5.8, 0.9, 5.8))
        m.c(a, skin, (11 * s, 16.8, 1), (4.6, 4, 5))
        m.c(a, skin, (11 * s - 2.3 * s, 17.4, 2.4), (1.4, 2.4, 1.4))
    # round shield on the left forearm: an octagon from two crossed plates
    m.c("armL", "spruce_planks", (14.3, 21, 0.4), (0.9, 11, 11))
    m.c("armL", "spruce_planks", (14.3, 21, 0.4), (0.9, 11, 11), (45, 0, 0))
    m.c("armL", "iron_block", (14.7, 21, 0.4), (0.6, 12, 1.6))
    m.c("armL", "iron_block", (14.7, 21, 0.4), (0.6, 1.6, 12))
    m.c("armL", "gold_block", (15.1, 21, 0.4), (1, 3, 3), (45, 0, 0))
    # head: blue skin, glowing eyes, braided ice beard, horned iron helm
    m.c("head", skin, (0, 41.5, 0.5), (8, 8, 8))
    m.c("head", "white_wool", (0, 43.6, 4.6), (7.6, 1.2, 0.6))
    m.m("head", "light_blue_concrete", (1.9, 42.6, 4.6), (1.6, 1, 0.3), light=True)
    m.c("head", skin, (0, 41, 5), (1.6, 2.6, 1.4))
    m.c("jaw", "white_wool", (0, 37.2, 4.6), (8.4, 4, 2.6))
    m.c("jaw", "white_wool", (0, 34, 5.4), (6.6, 3.4, 2.4))
    m.c("jaw", "packed_ice", (0, 30.8, 6), (4, 3.4, 2), light=False)
    m.m("jaw", "white_wool", (2.2, 27.6, 6.2), (1.2, 3.8, 1.2))
    m.m("jaw", "gold_block", (2.2, 29, 6.2), (1.6, 0.9, 1.6))
    m.m("jaw", "packed_ice", (2.2, 25, 6.2), (1, 1.8, 1))
    m.m("head", "white_wool", (3.2, 39.4, 4.9), (2.4, 1.2, 1.4), (0, 0, -15))
    m.c("head", "iron_block", (0, 46.2, 0.4), (9, 2.6, 9))
    m.c("head", "iron_block", (0, 48, 0.4), (6.6, 1.4, 6.6))
    m.c("head", "gold_block", (0, 45.1, 0.4), (9.4, 0.8, 9.4))
    m.c("head", "iron_block", (0, 43.2, 5), (1.2, 4, 0.8))
    m.m("head", "iron_block", (4.3, 42.6, 1), (0.9, 4, 6))
    mhorn(m, "head", "packed_ice", (4.6, 46.5, 0.4), 5, (0, 0, -70), (0, 0, 22), 2.4, 0.8)
    # long fur cloak
    m.c("cape", "light_gray_wool", (0, 22, -6), (17, 30, 1.2), (5, 0, 0), (0, 37, -5.6))
    m.c("cape", "white_wool", (0, 36, -5.8), (19, 3.4, 2), (5, 0, 0), (0, 37, -5.6))
    for i, x in enumerate((-6.4, -2.2, 2.2, 6.4)):
        m.c("cape", "white_wool", (x, 6.2 - (i % 2), -7.4), (4, 2.2, 1.4), (5, 0, 0), (0, 37, -5.6))
    # ice greataxe
    m.c("axe", "spruce_log", (-11, 27, 1), (1.8, 30, 1.8))
    m.c("axe", "brown_wool", (-11, 17, 1), (2.2, 7, 2.2))
    m.c("axe", "iron_block", (-11, 12.6, 1), (2.6, 1.6, 2.6))
    m.c("axe", "iron_block", (-11, 41.8, 1), (2.6, 2, 2.6))
    for dz, h, w in ((4.5, 10, 4), (8, 8, 3.4), (10.5, 5, 2)):
        m.c("axe", "blue_ice", (-11, 37, 1 + dz), (1, h, w), light=True)
    m.c("axe", "packed_ice", (-11, 37, -3.2), (1.2, 5, 4.4))
    m.c("axe", "light_blue_stained_glass", (-11, 37, 11.4), (0.8, 2.4, 1.4), light=True)
    m.attacks = {"frost": "cast", "volley": "double", "minions": "roar", "shockwave": "slam"}
    m.melee = "swipe"
    m.spawn = {"style": "assemble", "particle": "SNOWFLAKE", "sound": "BLOCK_GLASS_PLACE"}
    m.death = {"style": "shatter", "swap": "ice", "particle": "SNOWFLAKE", "sound": "BLOCK_GLASS_BREAK"}
    return m

@model
def warlord_gruk():
    m = Model("warlord_gruk", "biped", 1.65)
    biped(m, hip=14, legx=5.2, neck=36, shoulder=33, armx=12.5)
    m.bone("jaw", "head", (0, 38, 4))
    m.bone("axe", "armR", (-13, 13.4, 1.2))
    skin = "pink_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, skin, (5.2 * s, 9, 0), (6.4, 10, 6.4))
        m.c(b, "gold_block", (5.2 * s, 6.4, 3.4), (5.6, 6, 0.8))
        m.c(b, "gold_block", (5.6 * s, 11.4, 0), (6.8, 1, 6.8))
        m.c(b, "black_terracotta", (5.2 * s, 1.3, 0.8), (7, 2.6, 8))
        m.c(b, "black_terracotta", (5.2 * s, 3.6, 0), (6.6, 2, 6.6))
    # pot belly, belt with a skull, gold chest plate with rivets, red loincloth
    m.c("body", skin, (0, 22, 0.6), (19, 13, 13))
    m.c("body", skin, (0, 21, 7.6), (15, 9, 2))
    m.c("body", "brown_terracotta", (0, 16.4, 0.6), (19.6, 3, 13.6))
    m.c("body", "calcite", (0, 16.4, 7.6), (4, 4, 1.4))
    m.m("body", "black_concrete", (0.9, 16.9, 8.35), (1, 1, 0.2))
    m.c("hips", "red_wool", (0, 9.6, 7), (8, 7, 0.9))
    m.c("hips", "gold_block", (0, 6.4, 7.2), (8.4, 0.8, 1))
    m.c("body", "gold_block", (0, 31, 0.4), (20, 9, 12.4))
    m.c("body", "raw_gold_block", (0, 31, 6.8), (12, 6, 0.8))
    for x in (-8.5, 8.5):
        for y in (28, 34):
            m.c("body", "iron_block", (x, y, 6.75), (1, 1, 0.4))
    m.c("body", "chain", (0, 30, 7.4), (0.8, 17, 0.8), (0, 0, 50))
    # bone necklace
    for i, x in enumerate((-5, -3, -1, 1, 3, 5)):
        m.c("body", "bone_block" if i % 2 else "calcite", (x, 34.5 - abs(x) * 0.25, 7), (1.4, 2.2 if i % 2 else 1.6, 1))
    # huge arms with spiked gold pauldrons
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "gold_block", (13 * s, 34.5, 0), (9, 5, 10), (0, 0, -12 * s))
        m.c(a, "raw_gold_block", (13 * s, 37.2, 0), (6, 1.4, 7), (0, 0, -12 * s))
        horn(m, a, "iron_block", (14.6 * s, 37, -2), 2, (0, 0, -30 * s), (0, 0, -10 * s), 1.8)
        horn(m, a, "iron_block", (14.6 * s, 37, 2), 2, (0, 0, -30 * s), (0, 0, -10 * s), 1.8)
        m.c(a, skin, (13 * s, 26, 0), (7, 10, 7))
        m.c(a, "gold_block", (13 * s, 18.4, 0.6), (7.4, 5.6, 7.4))
        m.c(a, skin, (13 * s, 13.4, 1.2), (6.4, 4.6, 6.6))
    # head: wide brute face, snout, tusks, floppy ears, gold half helmet with a red crest
    m.c("head", skin, (0, 41.4, 1.6), (12, 10, 10))
    m.c("head", "white_terracotta", (0, 40.4, 7.8), (6.4, 5, 2.6))
    m.m("head", "black_terracotta", (1.6, 40.6, 9.15), (1.4, 1.8, 0.2))
    m.m("head", "black_concrete", (3.6, 43.4, 6.65), (1.6, 1.3, 0.3))
    m.m("head", "red_concrete", (3.4, 43.2, 6.8), (0.7, 0.7, 0.2), light=True)
    m.c("head", "brown_terracotta", (0, 44.6, 6.7), (10, 1.2, 0.6))
    m.c("jaw", skin, (0, 36.6, 3.4), (11, 3, 7.6))
    mhorn(m, "jaw", "bone_block", (3.8, 37.6, 6.6), 2, (-10, 0, -10), (-12, 0, -4), 1.6)
    m.m("head", skin, (7.5, 43, 1), (2, 5, 5), (0, 0, -40), (6.2, 44.5, 1))
    m.m("head", "brown_terracotta", (8.3, 41.2, 1.2), (1.8, 2, 4), (0, 0, -40), (6.2, 44.5, 1))
    m.c("head", "gold_block", (0, 47, 1.2), (12.6, 2.4, 10.6))
    m.c("head", "gold_block", (0, 48.6, 0.6), (9, 1.4, 8))
    for i, z in enumerate((-3, -0.6, 1.8, 4.2)):
        m.c("head", "red_wool", (0, 50.6 + (1 if i in (1, 2) else 0), z), (1.6, 3.6 + (2 if i in (1, 2) else 0), 2.6))
    # double bladed golden axe
    m.c("axe", "dark_oak_log", (-13, 25, 1.2), (2.2, 30, 2.2))
    m.c("axe", "gold_block", (-13, 9.6, 1.2), (3, 1.6, 3))
    m.c("axe", "gold_block", (-13, 40.4, 1.2), (3, 1.6, 3))
    for dz in (1, -1):
        m.c("axe", "gold_block", (-13, 35, 1.2 + 5 * dz), (1.4, 9, 7))
        m.c("axe", "raw_gold_block", (-13, 35, 1.2 + 8.6 * dz), (1, 12, 1.6))
        m.c("axe", "gold_block", (-13, 35, 1.2 + 2 * dz), (2, 4, 3))
    m.c("axe", "red_wool", (-13, 13.4, 1.2), (2.6, 5, 2.6))
    m.attacks = {"leap": "lunge", "shockwave": "slam", "minions": "roar", "roar": "stomp"}
    m.melee = "double"
    m.spawn = {"style": "drop", "particle": "WAX_ON", "sound": "ENTITY_PIGLIN_BRUTE_ANGRY"}
    m.death = {"style": "explode", "swap": "gold", "particle": "WAX_ON", "sound": "ENTITY_PIGLIN_BRUTE_DEATH"}
    return m

@model
def tide_tyrant():
    m = Model("tide_tyrant", "biped", 1.75)
    biped(m, hip=20, legx=3.4, neck=37, shoulder=34.5, armx=8.8)
    m.bone("jaw", "head", (0, 38.6, 3))
    m.bone("cape", "body", (0, 36, -4))
    m.bone("trident", "armR", (-9, 16, 2))
    skin = "cyan_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "blue_wool", (3.4 * s, 12, 0), (4.6, 14, 4.6))
        m.c(b, skin, (3.4 * s, 3.2, 0.4), (4.2, 6.4, 4.4))
        m.c(b, "black_terracotta", (3.4 * s, 0.7, 1), (4.8, 1.4, 6))
        m.c(b, "tuff", (3.4 * s + 1.4 * s, 8, 2.4), (1, 1, 0.6))
        m.c(b, "warped_wart_block", (3.4 * s, 13, 2.4), (3, 2, 0.4))
    # admiral coat: long tails, gold buttons, epaulettes, torn sash
    m.c("body", "blue_wool", (0, 28.6, 0), (13, 14, 7.6))
    m.c("body", skin, (0, 31, 3.6), (5, 8, 0.6))
    for y in (24.5, 27.5, 30.5):
        m.m("body", "gold_block", (3.2, y, 3.95), (1, 1, 0.4))
    m.c("body", "red_wool", (0, 27, 4.0), (2.4, 15, 0.6), (0, 0, -40))
    m.c("hips", "blue_wool", (0, 21, 0), (13.4, 3, 8))
    m.c("hips", "gold_block", (0, 21, 4.05), (3, 2.4, 0.4))
    for s in (1, -1):
        m.c("hips", "blue_wool", (4.6 * s, 12.4, -1), (4.4, 15, 6), (6, 0, 4 * s), (4.6 * s, 20, -1))
        m.c("hips", "gold_block", (4.6 * s, 5.4, -1.2), (4.6, 0.8, 6.2), (6, 0, 4 * s), (4.6 * s, 20, -1))
    for x, y in ((-4, 26), (5, 33), (-2, 34)):
        m.c("body", "tuff", (x, y, 3.95), (1.2, 1.2, 0.5))
    m.c("body", "warped_wart_block", (4, 24, -3.9), (4, 5, 0.4))
    # arms
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "gold_block", (9.6 * s, 35.5, 0), (5.6, 1.8, 6.4))
        for k in (-2, 0, 2):
            m.c(a, "gold_block", (11.6 * s, 33.6, k), (0.6, 2.4, 0.6))
        m.c(a, "blue_wool", (9.2 * s, 29, 0), (4.4, 9, 4.4))
        m.c(a, "gold_block", (9.2 * s, 24, 0.2), (4.8, 1, 4.8))
        m.c(a, skin, (9.2 * s, 20, 0.6), (3.6, 7.5, 3.6))
        m.c(a, skin, (9.2 * s, 15.4, 1.2), (3.8, 2.6, 3.8))
        m.c(a, "tuff", (9.2 * s + 1.8 * s, 21, 1), (0.6, 1, 1))
    # anchor on a chain in the left hand
    m.c("armL", "chain", (9.6, 10.5, 1.6), (0.9, 8, 0.9))
    m.c("armL", "iron_block", (9.6, 5.5, 1.6), (1.6, 3, 1.6))
    m.c("armL", "iron_block", (9.6, 6, 1.6), (7, 1.4, 1.4))
    m.c("armL", "iron_block", (9.6, 1.8, 1.6), (1.8, 7, 1.8))
    m.c("armL", "iron_block", (9.6, -1.6, 1.6), (8, 1.6, 1.8))
    m.m("armL", "iron_block", (4, 0.2, 1.6), (1.6, 3.4, 1.8), (0, 0, 25))
    m.c("armL", "iron_block", (13.4, 0.2, 1.6), (1.6, 3.4, 1.8), (0, 0, 25))
    m.c("armL", "iron_block", (5.8, 0.2, 1.6), (1.6, 3.4, 1.8), (0, 0, -25))
    # head: drowned face, glowing eyes, coral crown, kelp hair
    m.c("head", skin, (0, 41.8, 0.6), (7.6, 7.6, 7.6))
    m.c("head", "warped_wart_block", (-2.4, 44, 4.5), (2.4, 2, 0.3))
    m.m("head", "black_concrete", (1.8, 42.4, 4.45), (2, 1.6, 0.2))
    m.m("head", "sea_lantern", (1.8, 42.4, 4.55), (1, 1, 0.2), light=True)
    m.c("jaw", skin, (0, 38.4, 1.8), (6.6, 1.8, 5.6))
    m.c("jaw", "white_concrete", (0, 39.4, 4.4), (5, 0.6, 0.4))
    for i, x in enumerate((-3, -1, 1, 3)):
        m.c("head", "dried_kelp_block", (x, 38 - i % 2 * 2, -3.4), (1.6, 10 + i % 2 * 4, 1.2), (8, 0, 0), (x, 45, -3))
    m.m("head", "dried_kelp_block", (4.2, 39, -1), (1.2, 9, 1.6), (6, 0, -6), (4, 45, -1))
    m.c("head", "dark_prismarine", (0, 46, 0.6), (8.4, 1.4, 8.4))
    for x, z, h, blk in ((0, 4, 5, "fire_coral_block"), (-3, 3, 3.6, "horn_coral_block"), (3, 3, 3.6, "horn_coral_block"),
                         (-4, -1, 3, "tube_coral_block"), (4, -1, 3, "tube_coral_block"), (0, -3.5, 3.4, "brain_coral_block"),
                         (-2, -3, 2.4, "bubble_coral_block"), (2, -3, 2.4, "bubble_coral_block")):
        m.c("head", blk, (x, 46.6 + h / 2, z), (1.6, h, 1.6), (0, 0, x * 3))
    m.c("head", "sea_lantern", (0, 47.6, 4.6), (1.6, 1.6, 0.6), light=True)
    # tattered sea cape with barnacles
    m.c("cape", "cyan_wool", (0, 20, -4.7), (12, 32, 0.8), (6, 0, 0), (0, 36, -4.4))
    for i, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
        m.c("cape", "cyan_wool", (x, 3.4 - (i % 2) * 2.2, -6.4), (2.6, 2.4 + (i % 2) * 3, 0.8), (6, 0, 0), (0, 36, -4.4))
    for x, y in ((-3, 28), (2, 20), (4, 12)):
        m.c("cape", "tuff", (x, y, -5.3), (1.4, 1.4, 0.6), (6, 0, 0), (0, 36, -4.4))
    # trident: prismarine shaft, three diamond prongs
    m.c("trident", "prismarine", (-9, 22, 2.4), (1.6, 40, 1.6))
    m.c("trident", "gold_block", (-9, 41.8, 2.4), (6.6, 1.2, 1.6))
    for dx, h in ((-3, 5), (0, 7), (3, 5)):
        m.c("trident", "prismarine_bricks", (-9 + dx, 42.4 + h / 2, 2.4), (1.2, h, 1.2))
        m.c("trident", "diamond_block", (-9 + dx, 42.4 + h + 0.8, 2.4), (1.6, 1.6, 1.6), (0, 45, 45), light=True)
    m.c("trident", "kelp_block" if False else "dried_kelp_block", (-9, 32, 2.4), (2.2, 3, 2.2))
    m.attacks = {"pull": "cast", "volley": "lunge", "frost": "sweep", "minions": "roar"}
    m.melee = "swipe"
    m.spawn = {"style": "rise", "particle": "BUBBLE_POP", "sound": "ENTITY_ELDER_GUARDIAN_CURSE"}
    m.death = {"style": "sink", "swap": "", "particle": "BUBBLE_COLUMN_UP", "sound": "ENTITY_DROWNED_DEATH"}
    return m

@model
def storm_herald():
    m = Model("storm_herald", "biped", 1.8)
    biped(m, hip=22, legx=3.4, neck=38, shoulder=35.5, armx=8)
    m.bone("cloud", "body", (0, 56, 0))
    m.bone("staff", "armL", (9, 18, 2))
    skin = "light_gray_terracotta"
    # long robe: straight panels, blue hem and trims, gold sash
    for s, b in ((1, "legL"), (-1, "legR")):
        m.box(b, "white_wool", (0, 1.2, -4.4), (6.4 * s, 22, 4.4))
        m.box(b, "blue_concrete", (0.4 * s, 0, -4.8), (6.8 * s, 2.6, 4.8))
        m.c(b, "yellow_concrete", (3.4 * s, 2.8, 4.75), (6, 0.6, 0.3), light=True)
        m.c(b, "gray_concrete", (3.2 * s, 0.4, 3.4), (3.6, 0.8, 3.2))
    m.c("hips", "blue_concrete", (0, 12, 4.7), (3.6, 21, 0.6))
    for s, b in ((1, "legL"), (-1, "legR")):
        m.box(b, "white_wool", (6 * s, 0.4, -5.4), (7.6 * s, 8, 5.4))
        m.box(b, "blue_concrete", (6.4 * s, 0, -5.8), (8 * s, 2.2, 5.8))
        for y in (10, 14, 18):
            m.c(b, "light_blue_concrete", (6.45 * s, y, 0), (0.2, 0.8, 4), light=True)
            m.c(b, "light_blue_concrete", (6.45 * s, y + 1.4, 0), (0.2, 2, 0.8), light=True)
    m.c("hips", "yellow_concrete", (0, 15, 5.05), (1.2, 7, 0.2), light=True)
    m.c("hips", "yellow_concrete", (0, 17.5, 5.05), (3, 1, 0.2), light=True)
    m.c("body", "white_wool", (0, 29.5, 0), (12, 13, 8))
    m.c("body", "blue_concrete", (0, 29.5, 4.1), (4, 13, 0.4))
    m.c("body", "gold_block", (0, 23.5, 0), (12.6, 1.6, 8.6))
    m.c("body", "gold_block", (0, 23.5, 4.4), (2.4, 2.4, 0.6))
    # standing collar with copper rods
    m.c("body", "blue_concrete", (0, 37, -2.4), (14, 6, 1.4), (-14, 0, 0))
    m.m("body", "blue_concrete", (6.6, 37, 0.6), (1.4, 6, 6), (0, 0, -14))
    m.c("body", "white_wool", (0, 35.6, 0), (16, 2.4, 9))
    for x in (-7, -3.5, 3.5, 7):
        m.c("body", "lightning_rod", (x, 41.5 + (1 if abs(x) < 5 else 0), -3), (2, 4, 2), (-14, 0, -x * 2))
    # sleeves that flare at the wrist, thin grey hands
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "white_wool", (8.6 * s, 30, 0), (4.2, 10, 4.2))
        m.c(a, "white_wool", (8.8 * s, 23, 0.6), (5.6, 5, 5.6))
        m.c(a, "blue_concrete", (8.8 * s, 20.8, 0.6), (6, 1, 6))
        m.c(a, skin, (8.8 * s, 18.6, 1.2), (2.6, 3, 2.6))
        m.c(a, "copper_block", (8.6 * s, 33.4, 0), (4.6, 1.2, 4.6))
    # illager face: long head, huge nose, unibrow, glowing yellow eyes; hood
    m.c("head", skin, (0, 43, 0.4), (7, 9.6, 7))
    m.c("head", skin, (0, 41, 4.6), (2, 4.4, 2))
    m.c("head", "black_wool", (0, 45, 3.95), (6.4, 1, 0.4))
    m.m("head", "black_concrete", (2, 43.6, 3.95), (1.6, 1, 0.3))
    m.m("head", "yellow_concrete", (2, 43.6, 4.05), (0.8, 0.8, 0.2), light=True)
    m.c("head", "white_wool", (0, 48.4, -0.4), (8.4, 2, 8.4))
    m.c("head", "white_wool", (0, 43, -3.2), (8.4, 10, 1.6))
    m.m("head", "white_wool", (3.9, 43, 0), (0.8, 10, 6))
    m.c("head", "blue_concrete", (0, 49.6, -0.4), (2, 1, 8.6))
    # floating storm cloud above with a lightning bolt hanging out of it
    for x, y, z, w, h, d in ((0, 58, 0, 12, 4, 8), (-5, 59, 1, 6, 4, 6), (5, 59.4, -1, 7, 5, 6), (0, 61, -1, 7, 3, 6), (-2, 56.4, 2, 5, 2, 5)):
        m.c("cloud", "gray_wool", (x, y, z), (w, h, d))
    m.c("cloud", "light_gray_wool", (3, 62.4, 0), (4, 2, 4))
    for i, (x, y, rz) in enumerate(((2, 54, 20), (1.2, 51.6, -30), (2.2, 49.6, 20))):
        m.c("cloud", "yellow_concrete", (x, y, 1), (0.9, 3, 0.9), (0, 0, rz), light=True)
    # staff: copper with a glowing rod tip and spinning rune stones
    m.c("staff", "cut_copper", (9, 22, 2.4), (1.6, 36, 1.6))
    m.c("staff", "oxidized_copper", (9, 39, 2.4), (2.6, 2, 2.6))
    m.c("staff", "end_rod", (9, 43, 2.4), (2.6, 6, 2.6), light=True)
    m.c("staff", "copper_bulb", (9, 41.5, 2.4), (2, 2, 2), (45, 0, 45), light=True)
    m.attacks = {"lightning": "cast", "levitate": "roar", "blink": "lunge", "pull": "sweep"}
    m.melee = "swipe"
    m.spawn = {"style": "lightning", "particle": "ELECTRIC_SPARK", "sound": "ENTITY_LIGHTNING_BOLT_THUNDER"}
    m.death = {"style": "ascend", "swap": "", "particle": "ELECTRIC_SPARK", "sound": "ENTITY_EVOKER_DEATH"}
    return m

@model
def executioner():
    m = Model("executioner", "biped", 1.75)
    biped(m, hip=19, legx=3.8, neck=36, shoulder=34, armx=10)
    m.bone("cleaver", "armR", (-10.5, 16.4, 1))
    skin = "light_gray_terracotta"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "black_terracotta", (3.8 * s, 12, 0), (5.4, 13, 5.6))
        m.c(b, "brown_terracotta", (3.8 * s, 3.4, 0.4), (5.8, 6.8, 6.2))
        m.c(b, "black_concrete", (3.8 * s, 0.6, 1), (6, 1.2, 7.4))
        m.c(b, "iron_block", (3.8 * s, 8.4, 3.2), (4.4, 3, 0.8))
        for y in (4, 6.4):
            m.c(b, "black_terracotta", (3.8 * s, y, 3.55), (4.6, 0.6, 0.3))
    # leather apron, heavy belt with chains and hooks, bare grey muscle
    m.c("hips", "brown_terracotta", (0, 20.6, 0), (15, 3.4, 9.6))
    m.c("hips", "iron_block", (0, 20.6, 4.9), (3.6, 3.6, 0.6))
    m.c("hips", "brown_terracotta", (0, 12.4, 4.6), (9, 15, 0.8), (-4, 0, 0), (0, 20, 4.6))
    m.c("hips", "red_terracotta", (1.6, 10, 5.1), (2.4, 3, 0.2), (-4, 0, 0), (0, 20, 4.6))
    m.c("hips", "red_terracotta", (-2, 14.6, 5.1), (1.6, 1.8, 0.2), (-4, 0, 0), (0, 20, 4.6))
    m.c("hips", "chain", (-7.8, 16, 0), (0.8, 8, 0.8))
    m.c("hips", "iron_block", (-7.8, 11.6, 0), (1.6, 1.6, 0.6))
    m.c("hips", "chain", (6, 17, 3.4), (0.7, 5, 0.7), (0, 0, 30))
    m.c("body", skin, (0, 28.8, 0), (16, 13, 9))
    m.m("body", skin, (3.4, 30.6, 4.4), (5.6, 4.6, 1.2))
    for y in (24, 26.6):
        m.m("body", skin, (1.6, y, 4.6), (2.6, 2, 0.6))
    m.c("body", "brown_terracotta", (0, 28.6, 4.75), (2.6, 18, 0.6), (0, 0, -40))
    m.c("body", "brown_terracotta", (0, 28.6, -4.75), (2.6, 18, 0.6), (0, 0, -40))
    m.c("body", "iron_block", (-4.1, 33.4, 5.15), (2, 2, 0.4), (0, 0, -40))
    m.c("body", "red_terracotta", (4, 25, 4.65), (2, 1.2, 0.2))
    # black hood with a short mantle
    m.c("body", "black_wool", (0, 35.2, -0.2), (14, 3, 10))
    m.m("body", "black_wool", (5.6, 33, 0), (3, 2.4, 10.4))
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, skin, (10.6 * s, 30, 0), (6, 9, 6))
        m.c(a, skin, (10.6 * s, 22.4, 0.4), (5.4, 7, 5.6))
        m.c(a, "brown_terracotta", (10.6 * s, 20.8, 0.4), (6, 3.4, 6.2))
        m.c(a, "iron_block", (10.6 * s, 20.8, 0.4), (6.2, 0.8, 6.4))
        m.c(a, skin, (10.6 * s, 16.4, 1), (5, 4, 5.4))
        m.c(a, "brown_terracotta", (10.6 * s, 34, 0), (6.6, 2, 6.6))
    m.c("armL", "chain", (11.6, 10.6, 1.4), (0.8, 8, 0.8))
    m.c("armL", "iron_block", (11.6, 6, 1.4), (3, 0.8, 0.8))
    m.c("armL", "iron_block", (11.6, 4.4, 1.4), (0.8, 3, 0.8))
    # head: tall hood with eye slits, the illager nose pokes through
    m.c("head", "black_wool", (0, 42, 0.4), (8.6, 11, 8.6))
    m.c("head", "black_wool", (0, 48.4, -0.6), (6, 2.4, 6))
    m.c("head", "black_wool", (0, 50.4, -1.6), (3.4, 2.2, 3.4), (-20, 0, 0))
    m.m("head", "black_concrete", (2, 43.6, 4.75), (2.2, 1.2, 0.2))
    m.m("head", "red_concrete", (2, 43.6, 4.85), (1, 0.7, 0.1), light=True)
    m.c("head", skin, (0, 41.4, 5.4), (1.8, 3.6, 1.6))
    m.c("head", "red_terracotta", (-2.6, 39, 4.75), (1.4, 2, 0.2))
    # cleaver: broad iron blade, notched, bloody edge, wrapped grip
    m.c("cleaver", "dark_oak_log", (-10.5, 18.6, 1.0), (2, 12, 2))
    m.c("cleaver", "black_wool", (-10.5, 19.0, 1.0), (2.4, 6, 2.4))
    m.c("cleaver", "iron_block", (-10.5, 24.9, 1.0), (2.8, 1.4, 4))
    m.c("cleaver", "iron_block", (-10.5, 35.0, 2.8), (1.2, 19, 9))
    m.c("cleaver", "iron_block", (-10.5, 44.8, 1.8), (1.2, 1.4, 7))
    m.c("cleaver", "red_terracotta", (-10.5, 36.0, 7.6), (1.3, 14, 1))
    m.c("cleaver", "red_concrete", (-10.5, 39.0, 6.8), (1.35, 3, 1))
    m.c("cleaver", "gray_concrete", (-10.5, 40.0, 0.0), (1.35, 1.6, 1.6))
    m.c("cleaver", "dark_oak_log", (-10.5, 29.0, 7.9), (1.3, 1.4, 0.6))
    # muscle shading: darker skin under the chest and between the ribs, a stitched scar, a brand
    m.c("body", "gray_terracotta", (0, 27.6, 4.6), (0.6, 7, 0.3))
    m.m("body", "gray_terracotta", (3.4, 28, 4.6), (5, 0.5, 0.3))
    m.m("body", "gray_terracotta", (7.6, 29, 2), (0.4, 8, 4))
    m.c("body", "red_terracotta", (-3.6, 30.4, 4.75), (0.4, 5, 0.2), (0, 0, 35))
    for k in range(3):
        m.c("body", "black_concrete", (-4.6 + k * 1.1, 29 + k * 1.5, 4.85), (1.4, 0.3, 0.15), (0, 0, -55))
    m.c("body", "orange_terracotta", (4.8, 25.4, 4.75), (1.6, 1.6, 0.2), (0, 0, 45))
    # shoulders: a spiked iron pauldron on the cleaver arm, a coil of rope on the other
    m.c("armR", "iron_block", (-11.4, 35.2, 0), (7.4, 2.6, 7.4), (0, 0, 12))
    m.c("armR", "iron_block", (-11.8, 33.6, 0), (7.8, 1, 7.8), (0, 0, 12))
    for z in (-2.4, 0, 2.4):
        m.c("armR", "gray_concrete", (-13.4, 37.2, z), (0.9, 2.4, 0.9), (0, 0, 25))
    m.c("armL", "spruce_planks", (10.6, 33, 0), (7, 1, 7))
    for y in (31.4, 30.2):
        m.c("armL", "birch_planks", (10.6, y, 0), (6.8, 0.9, 6.8), (0, 22, 0))
    # forearms: leather bracers with iron studs
    for s, a in ((1, "armL"), (-1, "armR")):
        for z in (-1.6, 1.6):
            m.c(a, "iron_block", (10.6 * s + 3.1 * s, 20.8, 0.4 + z), (0.4, 1, 1))
    # belt: hanging keys, a whetstone and a hood rope
    m.c("hips", "iron_block", (5.8, 13.4, 4.4), (2.4, 2.4, 0.4), (0, 0, 45))
    for k, h in enumerate((2.4, 1.6, 2)):
        m.c("hips", "gold_block", (4.8 + k * 1.1, 11 - h / 2, 4.6), (0.4, h, 0.4))
    m.c("hips", "smooth_stone", (-5.4, 15.8, 4.2), (2, 3.4, 1), (0, 0, 10))
    m.c("hips", "brown_terracotta", (6.4, 18.6, 4.8), (1.4, 3, 0.6))
    # boots: buckles and toe caps
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, "iron_block", (3.8 * s, 2.6, 3.6), (1.4, 1, 0.3))
        m.c(b, "black_terracotta", (3.8 * s, 1.2, 4.3), (5.4, 1.6, 0.8))
    # hood: stitched seam up the back and a frayed hem
    m.c("head", "gray_wool", (0, 44, -3.9), (0.5, 9, 0.3))
    for x in (-3.6, -1.2, 1.2, 3.6):
        m.c("head", "black_wool", (x, 36.4 - abs(x) * 0.2, 4.3), (2, 1.6, 0.8))
    m.attacks = {"leap": "lunge", "shockwave": "slam", "minions": "roar", "roar": "sweep"}
    m.melee = "swipe"
    m.spawn = {"style": "build", "particle": "SMOKE", "sound": "ENTITY_VINDICATOR_CELEBRATE"}
    m.death = {"style": "topple", "swap": "", "particle": "LARGE_SMOKE", "sound": "ENTITY_VINDICATOR_DEATH"}
    return m

@model
def pharaoh():
    m = Model("pharaoh", "biped", 1.75)
    biped(m, hip=19, legx=3.4, neck=36, shoulder=34, armx=8.6)
    m.bone("jaw", "head", (0, 38, 3))
    m.bone("crook", "armR", (-9, 16, 2))
    m.bone("flail", "armL", (9, 16, 2))
    wrap, wrap2 = "white_wool", "smooth_sandstone"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, wrap, (3.4 * s, 10, 0), (4.6, 19, 4.6))
        for y in (3, 7, 11.5, 15.5):
            m.c(b, wrap2, (3.4 * s, y, 0), (4.9, 1.2, 4.9), (0, 0, 6 * s))
        m.c(b, "gold_block", (3.4 * s, 1, 0.6), (5, 2, 6))
        m.c(b, "lapis_block", (3.4 * s, 2.1, 3.4), (5, 0.4, 0.4))
        m.c(b, wrap, (3.4 * s + 2.5 * s, 5, -1), (0.6, 5, 1.2), (0, 0, 10 * s))
    # gold kilt (shendyt) with a lapis apron, bandaged torso, broad collar, scarab
    m.c("hips", "gold_block", (0, 18, 0), (11.4, 4, 7))
    m.c("hips", "cut_sandstone", (0, 14.4, 0.6), (10.6, 4, 6.6))
    m.c("hips", "lapis_block", (0, 12, 3.9), (4, 10, 0.6))
    for y in (8.4, 11, 13.6):
        m.c("hips", "gold_block", (0, y, 4.25), (4.2, 0.6, 0.3))
    m.c("body", wrap, (0, 27.5, 0), (11, 13, 6.6))
    for y, rz in ((22, 8), (25.5, -6), (29, 10), (32, -5)):
        m.c("body", wrap2, (0, y, 0), (11.4, 1.4, 7), (0, 0, rz))
    m.c("body", "gold_block", (0, 33.8, 0), (14, 2.6, 8))
    m.c("body", "lapis_block", (0, 32.2, 3.6), (12, 1.2, 1))
    m.c("body", "gold_block", (0, 31, 3.7), (9, 1.2, 1))
    m.c("body", "lapis_block", (0, 30, 3.6), (6, 1, 0.9))
    m.c("body", "emerald_block", (0, 27, 3.6), (3, 2.4, 0.8), light=True)
    m.m("body", "gold_block", (2.4, 27.4, 3.5), (1.8, 1.2, 0.6), (0, 0, -20))
    m.c("body", wrap, (3, 21, 3.4), (1.2, 6, 0.4), (0, 0, 15))
    # arms: wrapped, gold armlets and cuffs
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, wrap, (9 * s, 26.5, 0), (3.8, 15, 3.8))
        m.c(a, "gold_block", (9 * s, 30, 0), (4.2, 1.6, 4.2))
        m.c(a, "gold_block", (9 * s, 20.6, 0.2), (4.2, 2.4, 4.2))
        m.c(a, "lapis_block", (9 * s, 20.6, 2.3), (4.3, 0.8, 0.2))
        m.c(a, wrap2, (9 * s, 17.6, 0.8), (3.4, 3, 3.6))
        m.c(a, wrap, (9 * s + 2 * s, 23, -1), (0.6, 7, 1), (0, 0, 12 * s))
    # nemes headdress: striped gold and lapis, flaps on the shoulders, cobra on the brow, false beard
    m.c("head", "brown_terracotta", (0, 41.4, 0.8), (7, 8, 7))
    m.c("head", wrap, (0, 40.6, 4.4), (7, 1.2, 0.2))
    m.m("head", "black_concrete", (1.8, 42.4, 4.35), (2, 1.4, 0.2))
    m.m("head", "lime_concrete", (1.8, 42.4, 4.45), (1, 0.9, 0.1), light=True)
    m.c("head", "gold_block", (0, 46, 0.2), (8.6, 2, 8.6))
    m.c("head", "lapis_block", (0, 47.4, 0.2), (7.4, 1, 7.4))
    m.c("head", "gold_block", (0, 48.4, 0), (6, 1.2, 6))
    m.c("head", "gold_block", (0, 42, -3.6), (9, 9, 1.2))
    for y in (38, 40, 42, 44):
        m.c("head", "lapis_block", (0, y, -4.3), (9.2, 0.8, 0.2))
    for s in (1, -1):
        m.c("head", "gold_block", (4.5 * s, 40, 1), (1.2, 12, 6), (0, 0, -8 * s), (4.5 * s, 46, 1))
        for y in (36, 38.5, 41, 43.5):
            m.c("head", "lapis_block", (5.2 * s, y + 0.2, 1), (0.3, 0.8, 6.2), (0, 0, -8 * s), (4.5 * s, 46, 1))
    m.c("head", "gold_block", (0, 46.4, 4.6), (1.2, 2.4, 0.9))
    m.c("head", "lapis_block", (0, 48, 4.9), (1.6, 1.2, 1))
    m.c("head", "emerald_block", (0, 48.1, 5.45), (0.6, 0.5, 0.1), light=True)
    m.c("jaw", "brown_terracotta", (0, 38, 1.8), (6, 1.6, 5.6))
    m.c("jaw", "gold_block", (0, 35.4, 4.2), (1.6, 4, 1.4))
    for y in (34.4, 36.2):
        m.c("jaw", "lapis_block", (0, y, 4.95), (1.7, 0.4, 0.2))
    # crook and flail
    m.c("crook", "gold_block", (-9, 26, 3), (1.2, 22, 1.2))
    for y in (19, 23, 27, 31):
        m.c("crook", "lapis_block", (-9, y, 3), (1.4, 1, 1.4))
    m.c("crook", "gold_block", (-9, 37.6, 4.8), (1.2, 1.2, 4.8))
    m.c("crook", "gold_block", (-9, 36.2, 6.8), (1.2, 3, 1.2))
    m.c("flail", "gold_block", (9, 20, 4.2), (1.2, 1.2, 8), (-30, 0, 0))
    for i, dx in enumerate((-1, 0, 1)):
        m.c("flail", "lapis_block", (9 + dx, 18, 8.6), (0.7, 5, 0.7), (-10, 0, dx * 15), (9, 20.5, 8))
        m.c("flail", "gold_block", (9 + dx * 1.4, 15.4, 9), (1.1, 1.2, 1.1))
    m.attacks = {"darkness": "cast", "poison": "roar", "minions": "slam", "blink": "lunge"}
    m.melee = "swipe"
    m.spawn = {"style": "rise", "particle": "FALLING_DUST", "sound": "ENTITY_HUSK_AMBIENT"}
    m.death = {"style": "dissolve", "swap": "sand", "particle": "FALLING_DUST", "sound": "BLOCK_SAND_BREAK"}
    return m

@model
def hexmother():
    m = Model("hexmother", "biped", 1.7)
    biped(m, hip=17, legx=3, neck=33, shoulder=31, armx=7.6)
    m.bone("jaw", "head", (0, 35, 5))
    m.bone("staff", "armR", (-8.6, 13, 6))
    skin = "lime_terracotta"
    H = (0, 18, 0)  # the whole upper body leans forward from the waist
    lean = (22, 0, 0)
    for s, b in ((1, "legL"), (-1, "legR")):
        m.box(b, "purple_terracotta", (0, 1.4, -5), (6.6 * s, 18, 5))
        m.box(b, "black_wool", (0, 0, -5.4), (7 * s, 2, 5.4))
        for i, z in enumerate((-4, -1, 2, 4.4)):
            m.c(b, "green_terracotta", (6.7 * s, 3 + i % 2, z), (0.4, 3 + i % 3, 2.2))
        m.c(b, "black_concrete", (2.6 * s, 0.5, 5.6), (2.4, 1, 3))
        m.c(b, "black_concrete", (2.6 * s, 1.2, 7.4), (1.4, 1.4, 1), (-30, 0, 0))
    m.c("hips", "black_wool", (0, 12, 5.2), (7, 12, 0.6))
    m.c("hips", "green_wool", (0, 10, 5.6), (5, 6, 0.4))
    m.c("hips", "brown_terracotta", (0, 18, 0), (14, 2, 10.6))
    for x, blk in ((-5.5, "magenta_stained_glass"), (-3.2, "lime_stained_glass"), (3.4, "orange_stained_glass"), (5.6, "light_blue_stained_glass")):
        m.c("hips", blk, (x, 15.8, 5.4), (1.6, 2.4, 1.6), light=True)
        m.c("hips", "brown_terracotta", (x, 17.3, 5.4), (0.9, 0.7, 0.9))
    m.c("hips", "bone_block", (6.8, 14, 2), (1.4, 3.6, 1.4), (0, 0, 20))
    # hunched body, shawl, hump
    m.c("body", "purple_terracotta", (0, 25, 0.6), (12, 13, 8), lean, H)
    m.c("body", "purple_terracotta", (0, 28, -4), (10, 7, 3), lean, H)
    m.c("body", "black_wool", (0, 30, 1.4), (14, 3, 9.4), lean, H)
    m.c("body", "black_wool", (0, 27.6, 5.4), (8, 3, 1.2), lean, H)
    m.c("body", "magenta_wool", (0, 27, 5.6), (2, 2, 0.8), lean, H)
    m.c("body", "green_terracotta", (-3, 22, 4.8), (3, 3, 0.4), lean, H)
    for x in (-5, 0, 5):
        m.c("body", "gray_wool", (x, 31.4, -3.2), (3, 6, 1.6), (40, 0, 0), (x, 33, -2))
    # long thin arms, claw fingers
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "purple_terracotta", (8 * s, 26, 1.6), (3.6, 10, 3.6), (20, 0, 0), (8 * s, 31, 0))
        m.c(a, "black_wool", (8.2 * s, 21.4, 3.4), (4.6, 3, 4.6), (20, 0, 0), (8 * s, 31, 0))
        m.c(a, skin, (8.2 * s, 17.4, 5), (2.4, 6, 2.4), (30, 0, 0), (8 * s, 31, 0))
        for k in (-0.8, 0, 0.8):
            m.c(a, skin, (8.2 * s + k, 13.6, 7.6), (0.5, 3, 0.5), (50, 0, 0), (8 * s, 31, 0))
    # face: green skin, long hooked nose with a wart, glowing purple eyes, grey hair, chin
    m.c("head", skin, (0, 37.4, 3), (7, 7, 7))
    m.c("head", skin, (0, 36.6, 7.6), (1.8, 2, 3), (-20, 0, 0))
    m.c("head", skin, (0, 35.2, 9), (1.4, 1.6, 1.4), (-30, 0, 0))
    m.c("head", "green_concrete", (0.9, 37, 8.2), (0.8, 0.8, 0.8))
    m.m("head", "black_concrete", (1.8, 38.6, 6.55), (1.8, 1.2, 0.2))
    m.m("head", "magenta_concrete", (1.8, 38.6, 6.65), (0.8, 0.8, 0.1), light=True)
    m.c("head", "black_wool", (0, 39.8, 6.6), (6, 0.6, 0.2))
    m.c("jaw", skin, (0, 33.4, 4), (5, 1.8, 5))
    m.c("jaw", skin, (0, 32.6, 6.8), (2, 1.4, 1.4))
    for x in (-3.5, -2, 2, 3.5):
        m.c("head", "gray_wool", (x, 34.4, 1), (1.4, 8, 3), (0, 0, x * 2), (x, 39, 1))
    m.c("head", "gray_wool", (0, 35, -0.6), (7.4, 9, 1.6))
    # the hat: a wide floppy brim, a bent cone that tips back, purple band with a gold buckle
    m.c("head", "black_wool", (0, 41.2, 2.6), (17, 0.9, 17), (-8, 0, 4))
    m.c("head", "black_wool", (0, 43.2, 2.2), (9, 3.4, 9), (-8, 0, 4))
    m.c("head", "purple_wool", (0, 42.4, 2.4), (9.4, 1.4, 9.4), (-8, 0, 4))
    m.c("head", "gold_block", (0, 42.4, 7.2), (2.4, 1.8, 0.4), (-8, 0, 4))
    limb(m, "head", "black_wool", (0, 44.6, 1.6), [(5, 7, (-15, 0, 4)), (5, 5, (-30, 0, 8)), (4, 3.4, (-60, 0, 10)), (4, 2.2, (-100, 0, 10)), (3, 1.4, (-140, 0, 0))])
    m.c("head", "lime_stained_glass", (0.4, 41.8, 10), (0.6, 1.4, 0.6), light=True)
    # staff with a dangling cauldron
    m.c("staff", "dark_oak_log", (-8.6, 18, 6.4), (1.6, 34, 1.6), (12, 0, 0), (-8.6, 13, 6))
    m.c("staff", "dark_oak_log", (-8.6, 35, 10.8), (1.2, 5, 1.2), (60, 0, 0))
    m.c("staff", "chain", (-8.6, 31.8, 13), (0.6, 4, 0.6))
    m.c("staff", "cauldron", (-8.6, 27.6, 13), (5, 5, 5))
    m.c("staff", "lime_stained_glass", (-8.6, 29.2, 13), (3.6, 1, 3.6), light=True)
    m.c("staff", "bone_block", (-8.6, 39, 9.6), (2.2, 2.2, 2.2), (30, 45, 0))
    m.attacks = {"levitate": "cast", "poison": "lunge", "blink": "sweep", "heal": "roar", "darkness": "double"}
    m.melee = "swipe"
    m.spawn = {"style": "portal", "particle": "WITCH", "sound": "ENTITY_WITCH_CELEBRATE"}
    m.death = {"style": "melt", "swap": "slime", "particle": "WITCH", "sound": "ENTITY_WITCH_DEATH"}
    return m

@model
def void_walker():
    m = Model("void_walker", "biped", 1.55)
    biped(m, hip=34, legx=2.6, neck=50, shoulder=49, armx=6.2)
    m.bone("jaw", "head", (0, 51.5, 3))
    skin, crack = "black_concrete", "crying_obsidian"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, skin, (2.6 * s, 25, 0), (2.6, 18, 2.6))
        m.c(b, skin, (2.6 * s, 8, 0.6), (2.2, 16, 2.2), (-4, 0, 0), (2.6 * s, 16, 0))
        m.c(b, "obsidian", (2.6 * s, 16.4, 0.4), (3, 2, 3))
        m.c(b, crack, (2.6 * s + 0.7 * s, 26, 1.35), (0.6, 5, 0.2), light=True)
        m.c(b, skin, (2.6 * s, 0.6, 1.6), (2.6, 1.2, 4.6))
    m.c("hips", "obsidian", (0, 34.6, 0), (8.4, 3, 4.4))
    m.c("body", skin, (0, 42, 0), (8, 12, 4))
    m.c("body", "obsidian", (0, 46.4, 0.2), (9, 4, 4.6))
    for x, y, h, rz in ((-2, 41, 5, 20), (1.6, 43.6, 4, -25), (0.4, 39, 3, 10)):
        m.c("body", crack, (x, y, 2.05), (0.6, h, 0.2), (0, 0, rz), light=True)
    m.c("body", "purple_stained_glass", (0, 43, 2.1), (2.4, 2.4, 0.4), (0, 0, 45), light=True)
    for i, x in enumerate((-3, -1, 1, 3)):
        m.c("hips", "black_stained_glass", (x, 29 - i % 2 * 2, 2.4), (1.8, 8 + i % 2 * 4, 0.4), (-6, 0, x * 2), (x, 34, 2.2))
        m.c("hips", "black_stained_glass", (x, 30 - i % 2, -2.4), (1.8, 7 + i % 2 * 3, 0.4), (6, 0, -x * 2), (x, 34, -2.2))
    m.c("hips", "purple_wool", (0, 34.6, 2.4), (8.8, 1.2, 0.4))
    for y in (38, 40.4, 42.8):
        m.m("body", "obsidian", (2.4, y, 2.1), (3, 0.8, 0.3))
    m.m("body", "obsidian", (4.8, 48.6, 0), (2, 2.4, 5), (0, 0, -20))
    horn(m, "body", "obsidian", (4.8, 49.6, -1), 3, (-20, 0, -30), (-10, 0, 15), 1.2)
    horn(m, "body", "obsidian", (-4.8, 49.6, -1), 3, (-20, 0, 30), (-10, 0, -15), 1.2)
    horn(m, "body", "obsidian", (0, 45, -2), 3, (-60, 0, 0), (-10, 0, 0), 1.1)
    # shards that hang in the air around the shoulders
    for x, y, z, sz, r in ((-8.6, 55, -2, 2.2, (30, 20, 40)), (9.4, 57, 0, 2.6, (10, 45, 30)), (-6, 59, 1.6, 1.6, (45, 0, 45)),
                           (7, 52, -3, 1.6, (20, 60, 10)), (0, 57.4, -4.4, 2, (45, 45, 0)), (-10.6, 49, 1, 1.4, (0, 30, 60))):
        m.c("body", "obsidian", (x, y, z), (sz, sz * 1.6, sz), r)
        m.c("body", crack, (x, y, z), (sz * 0.5, sz * 0.9, sz * 1.02), r, light=True)
    # long arms and claws
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, skin, (6.4 * s, 38, 0), (2.4, 20, 2.4))
        m.c(a, skin, (6.4 * s, 20, 0.4), (2.2, 17, 2.2))
        m.c(a, "obsidian", (6.4 * s, 29, 0.2), (2.8, 2, 2.8))
        m.c(a, crack, (6.4 * s + 0.7 * s, 40, 1.25), (0.5, 6, 0.2), light=True)
        for k in (-0.8, 0.8):
            m.c(a, "obsidian", (6.4 * s + k, 9.6, 1.2), (0.6, 4, 0.6), (12, 0, -k * 10))
        m.c(a, "obsidian", (6.4 * s, 10, -0.6), (0.6, 3, 0.6), (-12, 0, 0))
    # head: long jaw that unhinges, glowing violet eyes, cracked crown of the skull
    m.c("head", skin, (0, 55, 0.4), (8, 7, 8))
    m.c("head", "obsidian", (0, 58.8, 0.4), (8.4, 1, 8.4))
    m.m("head", "magenta_concrete", (2.2, 55, 4.45), (2.6, 1, 0.2), light=True)
    m.m("head", "purple_concrete", (2.2, 55, 4.5), (1.4, 0.6, 0.2), light=True)
    m.c("head", crack, (-2, 57.6, 4.45), (0.6, 2, 0.2), (0, 0, 30), light=True)
    m.c("jaw", skin, (0, 50.4, 1.6), (7.6, 2.4, 7))
    m.c("jaw", "purple_concrete", (0, 51.7, 3.6), (6, 0.4, 4), light=True)
    for x in (-3, -1, 1, 3):
        m.c("jaw", "white_concrete", (x, 52, 4.8), (0.6, 0.8, 0.6))
    m.attacks = {"blink": "lunge", "darkness": "roar", "levitate": "cast", "pull": "sweep"}
    m.melee = "double"
    m.spawn = {"style": "blink", "particle": "REVERSE_PORTAL", "sound": "ENTITY_ENDERMAN_SCREAM"}
    m.death = {"style": "implode", "swap": "", "particle": "REVERSE_PORTAL", "sound": "ENTITY_ENDERMAN_DEATH"}
    return m

@model
def pale_watcher():
    m = Model("pale_watcher", "biped", 1.75)
    biped(m, hip=22, legx=3, neck=40, shoulder=38, armx=7.4)
    bark, wood, moss = "pale_oak_log", "pale_oak_planks", "pale_moss_block"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, bark, (3 * s, 13, 0), (3, 18, 3), (0, 0, -4 * s))
        m.c(b, bark, (3.4 * s, 3, 0.4), (3.6, 4, 3.6))
        for rx in (35, -35, 0):
            limb(m, b, bark, (3.4 * s, 1.6, 0.4), [(4, 1.4, (rx, 0, -105 * s)), (2.4, 0.9, (rx, 0, -125 * s))])
        m.c(b, moss, (3 * s, 18, -1.6), (2, 4, 0.6))
    # twisted trunk with a glowing heart and bare ribs of wood
    m.c("hips", bark, (0, 22.6, 0), (7, 3, 4.6))
    limb(m, "body", bark, (0, 23, 0), [(7, 5, (4, 10, -6)), (6, 5.6, (-6, 25, 6)), (5, 6, (4, 40, -4))])
    m.c("body", "creaking_heart", (0, 31, 1.2), (4, 4, 4), light=True)
    for y in (28, 33):
        m.m("body", wood, (2.8, y, 2.8), (2.6, 0.9, 0.9), (0, -20, 0))
    m.c("body", bark, (0, 38, 0), (11, 3.4, 4.6), (0, 0, -6))
    for x, h in ((-4, 7), (-1.4, 10), (2, 6), (4.6, 9)):
        m.c("body", moss, (x, 37 - h / 2, -2.6), (2.2, h, 0.6))
    # twigs growing from the back and shoulders
    limb(m, "body", bark, (-4, 38, -1), [(6, 1.6, (-20, 0, 30)), (5, 1, (-30, 0, 60)), (3, 0.7, (-30, 0, 20))])
    limb(m, "body", bark, (4, 39, -1), [(7, 1.6, (-25, 0, -25)), (5, 1, (-10, 0, -55)), (4, 0.7, (-40, 0, -10))])
    limb(m, "body", bark, (0, 37, -2), [(6, 1.4, (-45, 0, 5)), (5, 1, (-60, 0, -20))])
    limb(m, "body", bark, (-6, 39, 0), [(4, 1.2, (0, 0, 55)), (3, 0.8, (-10, 0, 85))])
    # long branch arms with twig fingers
    for s, a in ((1, "armL"), (-1, "armR")):
        limb(m, a, bark, (7.6 * s, 38, 0), [(11, 2.6, (8, 0, 172 * s if s < 0 else -172)), (11, 2.2, (-10, 0, 176 * s if s < 0 else -176))])
        m.c(a, moss, (7.8 * s, 31, -1.2), (1.6, 6, 0.6))
        for k, (rx, rz) in enumerate(((150, 10), (165, -12), (175, 20), (160, -30))):
            limb(m, a, bark, (7.6 * s + (k - 1.5) * 0.4, 16.4, 0.6), [(4, 0.7, (rx, 0, rz * s)), (2.4, 0.5, (rx + 10, 0, rz * s * 1.4))])
    # head: a block of bark with glowing orange eyes and a split mouth
    m.c("head", bark, (0, 44.5, 0.4), (7, 9, 6.4), (0, 0, 4))
    m.c("head", wood, (0, 49.4, 0.4), (5, 1.4, 4.4), (0, 0, 4))
    m.m("head", "orange_concrete", (1.7, 46, 3.65), (1.6, 1.6, 0.2), light=True)
    m.m("head", "yellow_concrete", (1.7, 46, 3.75), (0.6, 0.6, 0.1), light=True)
    m.c("head", "black_concrete", (0, 42.4, 3.65), (4, 0.8, 0.2), (0, 0, 8))
    limb(m, "head", bark, (2.4, 49, 0), [(4, 1.2, (0, 0, -35)), (3, 0.8, (-20, 0, -70))])
    limb(m, "head", bark, (-2, 49.4, -0.6), [(3, 1, (-20, 0, 25)), (2.4, 0.7, (-30, 0, 55))])
    m.attacks = {"darkness": "roar", "blink": "lunge", "quake": "stomp", "roar": "cast"}
    m.melee = "double"
    m.spawn = {"style": "grow", "particle": "SPORE_BLOSSOM_AIR", "sound": "BLOCK_CREAKING_HEART_SPAWN"}
    m.death = {"style": "crumble", "swap": "", "particle": "CRIMSON_SPORE", "sound": "ENTITY_CREAKING_DEATH"}
    return m

@model
def molten_colossus():
    m = Model("molten_colossus", "biped", 1.65)
    biped(m, hip=16, legx=6, neck=38, shoulder=38, armx=14)
    m.bone("jaw", "head", (0, 34, 13))
    rock, plate, lava = "blackstone", "polished_basalt", "magma_block"
    for s, b in ((1, "legL"), (-1, "legR")):
        m.c(b, rock, (6 * s, 9, 0), (8, 12, 8))
        m.c(b, plate, (6 * s, 9.6, 4.3), (6.6, 6, 0.8))
        m.c(b, lava, (6 * s + 2.2 * s, 7, 4.25), (1.4, 4, 0.4), light=True)
        m.c(b, rock, (6 * s, 1.6, 1), (9, 3.2, 10))
        for dx in (-3, 0, 3):
            m.c(b, "obsidian", (6 * s + dx, 1, 6.6), (2, 2, 2))
    # huge hunched torso: shoulders far wider than the hips, glowing chest core
    m.c("hips", rock, (0, 17, 0), (14, 6, 9))
    m.c("body", rock, (0, 26, 1), (18, 12, 12), (14, 0, 0), (0, 18, 0))
    m.c("body", rock, (0, 36.5, 2), (28, 10, 14), (14, 0, 0), (0, 18, 0))
    m.c("body", plate, (0, 42, -1), (22, 3, 10), (14, 0, 0), (0, 18, 0))
    m.c("body", "shroomlight", (0, 32, 8.4), (7, 7, 2), (14, 0, 0), (0, 18, 0), light=True)
    m.c("body", "ochre_froglight", (0, 32, 9.2), (4, 4, 1), (14, 45, 0), (0, 18, 0), light=True)
    for x, y, h, rz in ((-7, 34, 7, 20), (7, 35, 6, -25), (-3, 25, 5, -10), (4, 23, 4, 30), (10, 40, 4, 10)):
        m.c("body", lava, (x, y, 8.1), (1.2, h, 0.6), (14, 0, rz), (0, 18, 0), light=True)
    for x in (-10, -5, 5, 10):
        m.c("body", "basalt", (x, 44, -2), (2.6, 5, 2.6), (-10, 0, -x * 2), (0, 18, 0))
    for x, z in ((-6, -6), (6, -6), (0, -6.6)):
        m.c("body", lava, (x, 34, z), (3, 5, 0.6), (14, 0, 0), (0, 18, 0), light=True)
    # gorilla arms: fists nearly reach the floor
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, rock, (15.6 * s, 38.6, 2), (9, 7, 10))
        m.c(a, plate, (16 * s, 42.6, 2), (8, 2, 9), (0, 0, -14 * s))
        m.c(a, rock, (15.6 * s, 28, 3), (7, 12, 7))
        m.c(a, lava, (15.6 * s + 3.6 * s, 29, 3), (0.4, 7, 2), light=True)
        m.c(a, rock, (15.6 * s, 16, 4), (8, 12, 8))
        m.c(a, plate, (15.6 * s, 17, 8.2), (6, 8, 0.6))
        m.c(a, rock, (15.6 * s, 6.4, 5), (10, 8, 10))
        m.c(a, lava, (15.6 * s, 6.4, 10.1), (6, 1.4, 0.4), light=True)
        for dx in (-3, 0, 3):
            m.c(a, "obsidian", (15.6 * s + dx, 3.6, 10.4), (2.2, 2.2, 1.4))
    # small head sunk between the shoulders, glowing eyes and mouth, basalt horns
    m.c("head", rock, (0, 36.4, 12.4), (9, 7, 7))
    m.c("head", plate, (0, 40.2, 12), (10, 1.6, 7.6))
    m.c("head", plate, (0, 38, 16), (9.4, 1.4, 1))
    m.m("head", "yellow_concrete", (2.2, 37, 16), (2, 1.2, 0.3), light=True)
    m.m("head", "orange_concrete", (2.2, 37, 16.05), (1, 0.6, 0.3), light=True)
    m.c("jaw", lava, (0, 33.8, 15.7), (5, 1, 0.4), light=True)
    m.c("jaw", rock, (0, 32.6, 13.2), (8, 2.2, 6))
    for x in (-2.4, 0, 2.4):
        m.c("jaw", "obsidian", (x, 34, 16), (1, 1.2, 0.6))
    mhorn(m, "head", "basalt", (4, 39, 12), 4, (20, 0, -50), (-20, 0, 15), 2.2, 0.75)
    m.attacks = {"fire_ring": "slam", "quake": "stomp", "leap": "lunge", "shockwave": "double"}
    m.melee = "swipe"
    m.spawn = {"style": "build", "particle": "LAVA", "sound": "ITEM_BUCKET_EMPTY_LAVA"}
    m.death = {"style": "melt", "swap": "magma", "particle": "LAVA", "sound": "ENTITY_IRON_GOLEM_DEATH"}
    return m

