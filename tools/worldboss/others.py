from models import *

@model
def broodmother():
    m = Model("broodmother", "spider", 1.55)
    m.bone("body", "root", (0, 14, 0))
    m.bone("abdomen", "body", (0, 16, -6))
    m.bone("head", "body", (0, 15, 8))
    m.bone("fangL", "head", (2.2, 11.4, 15))
    m.bone("fangR", "head", (-2.2, 11.4, 15))
    hair, hair2, mark = "black_wool", "gray_wool", "lime_terracotta"
    # cephalothorax
    m.c("body", hair, (0, 15, 2), (14, 8, 14))
    m.c("body", hair2, (0, 19.4, 2), (10, 1.2, 10))
    m.c("body", "coal_block", (0, 11.4, 2), (10, 1.2, 12))
    # abdomen: huge, banded, egg sacs and webbing stuck to it, spinnerets at the back
    m.c("abdomen", hair, (0, 22, -18), (22, 18, 26), (-12, 0, 0), (0, 16, -6))
    m.c("abdomen", hair, (0, 22, -18), (18, 22, 22), (-12, 0, 0), (0, 16, -6))
    m.c("abdomen", hair2, (0, 33.2, -16), (12, 1.2, 18), (-12, 0, 0), (0, 16, -6))
    for z in (-10, -16, -22):
        m.c("abdomen", mark, (0, 33.6, z), (8 - abs(z + 16) * 0.4, 0.4, 2.6), (-12, 0, 0), (0, 16, -6))
        m.m("abdomen", mark, (9.2, 25, z), (0.4, 6, 2), (-12, 0, 0), (0, 16, -6))
    m.c("abdomen", "red_concrete", (0, 28, -30.4), (3, 5, 0.4), (-12, 0, 0), (0, 16, -6), light=True)
    m.c("abdomen", "red_concrete", (0, 28, -30.4), (5, 1.4, 0.4), (-12, 0, 0), (0, 16, -6), light=True)
    for x, y, z in ((-8, 31, -8), (6, 33, -20), (9, 26, -14), (-10, 22, -24)):
        m.c("abdomen", "white_wool", (x, y, z), (5, 5, 5), (-12, 20, 0), (0, 16, -6))
        m.c("abdomen", "lime_concrete", (x, y, z), (5.2, 1, 1), (-12, 20, 0), (0, 16, -6), light=True)
    for x, y, z in ((0, 34, -26), (-6, 18, -30)):
        m.c("abdomen", "cobweb", (x, y, z), (7, 7, 7), (-12, 0, 0), (0, 16, -6))
    for x in (-2, 2):
        m.c("abdomen", hair2, (x, 17, -31.6), (2, 3, 2), (-30, 0, 0), (0, 16, -6))
    # head: eight glowing eyes in two rows, fangs
    m.c("head", hair, (0, 14, 12.6), (10, 8, 6))
    m.c("head", hair2, (0, 18.4, 12.4), (8, 1, 5))
    for x, y, sz in ((-1.4, 16.4, 1.6), (1.4, 16.4, 1.6), (-3.6, 16, 1.2), (3.6, 16, 1.2), (-2.4, 13.8, 1.1), (2.4, 13.8, 1.1), (-4.4, 13.6, 0.8), (4.4, 13.6, 0.8)):
        m.c("head", "red_concrete", (x, y, 15.65), (sz, sz, 0.3), light=True)
    for s, b in ((1, "fangL"), (-1, "fangR")):
        limb(m, b, "bone_block", (2.2 * s, 11.4, 15), [(3, 1.6, (150, 0, 0)), (2.4, 1.1, (120, 0, 15 * s)), (1.6, 0.7, (80, 0, 20 * s))])
        m.c(b, "black_concrete", (2.2 * s, 11.8, 15.4), (2.2, 2, 1.6))
    # eight legs: knee high above the body, long hairy lower legs
    fan = {1: 42, 2: 14, 3: -14, 4: -42}
    zs = {1: 7, 2: 4, 3: 0, 4: -3}
    for i in (1, 2, 3, 4):
        m.bone(f"legL{i}", "body", (6.4, 14, zs[i]))
        m.bone(f"legR{i}", "body", (-6.4, 14, zs[i]))
        a = fan[i]
        segs = [(14, 2.4, (a, 0, -55)), (18, 1.9, (a, 0, -150), hair2), (6, 1.1, (a * 0.6, 0, -172), "coal_block")]
        mlimb(m, f"legL{i}", hair, (6.4, 14, zs[i]), segs, joint="red_terracotta")
        m.c(f"legL{i}", hair2, (14 + 0 * i, 21.4, zs[i] + 8 * (a / 42)), (0.6, 2, 0.6), (0, 0, -20))
    m.attacks = {"poison": "spit", "minions": "drum", "leap": "leap", "pull": "rearup"}
    m.melee = "fang"
    m.spawn = {"style": "drop", "particle": "SPORE_BLOSSOM_AIR", "sound": "ENTITY_SPIDER_AMBIENT"}
    m.death = {"style": "curl", "swap": "", "particle": "SPORE_BLOSSOM_AIR", "sound": "ENTITY_SPIDER_DEATH"}
    return m

def floater(m, core_y, neck, shoulder, armx):
    m.bone("core", "root", (0, core_y, 0))
    m.bone("head", "core", (0, neck, 0))
    m.mbone("armL", "core", (armx, shoulder, 0))
    for i in (1, 2, 3):
        m.bone(f"ring{i}", "root", (0, 0, 0))

def ringof(m, bone, block, y, r, n, size, tilt=0, phase=0, light=False, inner=None):
    import math
    for k in range(n):
        a = phase + 360 * k / n
        x, z = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        m.c(bone, block, (x, y, z), size, (0, -a, tilt), light=light)
        if inner:
            m.c(bone, inner, (x, y, z), (size[0] * 0.5, size[1] * 1.04, size[2] * 0.5), (0, -a, tilt), light=True)

@model
def cinder_sovereign():
    m = Model("cinder_sovereign", "float", 1.6)
    floater(m, core_y=26, neck=38, shoulder=35, armx=7)
    # a body of fire: torso of gilded stone over a tail of flame
    m.c("core", "gilded_blackstone", (0, 31, 0), (10, 10, 7))
    m.c("core", "gold_block", (0, 35.6, 0), (12, 2, 8))
    m.c("core", "magma_block", (0, 31, 3.6), (4, 6, 0.4), light=True)
    m.c("core", "shroomlight", (0, 31.4, 3.9), (2, 3, 0.3), light=True)
    taper(m, "core", "orange_stained_glass", 0, 12, 0, [(1.6, 1.6), (3, 3), (4.6, 4), (6, 5), (7.6, 6), (9, 6.6)], 2.4, light=True)
    taper(m, "core", "shroomlight", 0, 15, 0, [(1.6, 1.4), (2.6, 2), (3.6, 3), (4.6, 3.6)], 2.6, light=True)
    for x, y, z in ((3, 18, 2), (-3, 21, -2), (2, 24, -3), (-4, 15, 1)):
        m.c("core", "yellow_stained_glass", (x, y, z), (1.4, 3, 1.4), (0, 45, 20), light=True)
    # arms of magma ending in fireballs
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "gold_block", (8 * s, 35, 0), (4.4, 3, 5))
        m.c(a, "magma_block", (8.6 * s, 29.4, 0), (3, 9, 3), light=True)
        m.c(a, "shroomlight", (9 * s, 23.6, 0.6), (3.6, 3.6, 3.6), (45, 45, 0), light=True)
        m.c(a, "orange_stained_glass", (9 * s, 23.6, 0.6), (5, 5, 5), (20, 20, 20), light=True)
    # blaze head with a crown of flame
    m.c("head", "yellow_terracotta", (0, 42.4, 0), (8, 8, 8))
    m.c("head", "orange_terracotta", (0, 39, 0.4), (7, 1.4, 7))
    m.m("head", "black_concrete", (1.8, 42.4, 4.05), (2.4, 1.4, 0.2))
    m.m("head", "orange_concrete", (1.8, 42.4, 4.15), (1.2, 0.6, 0.1), light=True)
    m.c("head", "black_concrete", (0, 40.2, 4.05), (3, 0.8, 0.2))
    m.c("head", "gold_block", (0, 46.8, 0), (9, 1.4, 9))
    for x, z in ((-3.4, 3.4), (0, 3.6), (3.4, 3.4), (-3.6, 0), (3.6, 0), (-3.4, -3.4), (0, -3.6), (3.4, -3.4)):
        h = 2.4 if abs(x) > 1 and abs(z) > 1 else 3.6
        m.c("head", "gold_block", (x, 47.5 + h / 2, z), (1.2, h, 1.2))
        m.c("head", "orange_stained_glass", (x, 48.3 + h, z), (1, 2.2, 1), (0, 45, 0), light=True)
    m.c("head", "redstone_block", (0, 49.4, 4.2), (1.6, 1.6, 0.6), (0, 0, 45), light=True)
    # three rings of blaze rods turning around it
    ringof(m, "ring1", "yellow_terracotta", 16, 9, 6, (1.8, 8, 1.8), 10, 0, True, "shroomlight")
    ringof(m, "ring2", "orange_terracotta", 27, 12, 8, (1.8, 9, 1.8), -12, 20, True, "shroomlight")
    ringof(m, "ring3", "yellow_terracotta", 38, 9.6, 5, (1.6, 7, 1.6), 15, 10, True, "shroomlight")
    m.attacks = {"fire_ring": "spin", "minions": "raise", "blink": "dive", "levitate": "pulse"}
    m.melee = "swipe"
    m.spawn = {"style": "spiral", "particle": "FLAME", "sound": "ENTITY_BLAZE_AMBIENT"}
    m.death = {"style": "burn", "swap": "", "particle": "LAVA", "sound": "ENTITY_BLAZE_DEATH"}
    return m

@model
def tempest():
    m = Model("tempest", "float", 1.6)
    floater(m, core_y=24, neck=36, shoulder=33, armx=6.6)
    wind, wind2, cloud = "light_blue_stained_glass", "white_stained_glass", "white_wool"
    # whirlwind body: a funnel of glass bands that spin
    m.c("core", "light_blue_terracotta", (0, 30, 0), (8, 8, 7))
    m.c("core", "light_blue_concrete", (0, 30, 3.6), (3, 3, 0.4), (0, 0, 45), light=True)
    m.c("core", "white_concrete", (0, 34.4, 0), (10, 1.4, 8))
    taper(m, "core", wind2, 0, 6, 0, [(1.4, 1.4), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)], 3.2, light=True)
    ringof(m, "ring1", wind, 9, 4.6, 7, (3.4, 1.6, 0.6), 0, 0, True)
    ringof(m, "ring1", wind2, 15, 7, 9, (3.6, 1.6, 0.6), 0, 15, True)
    ringof(m, "ring2", wind, 21, 9.6, 11, (4, 1.8, 0.6), 0, 5, True)
    ringof(m, "ring2", wind2, 26, 11, 12, (4, 1.6, 0.6), 0, 25, True)
    ringof(m, "ring3", "light_blue_terracotta", 30, 13, 4, (1.6, 9, 1.6), 0, 45, False, "light_blue_concrete")
    ringof(m, "ring3", wind, 40, 9, 8, (3.4, 1.4, 0.6), 0, 10, True)
    # wispy arms that end in wind charges
    for s, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "light_blue_terracotta", (7.4 * s, 32, 0), (3.4, 3, 4))
        limb(m, a, wind, (7.6 * s, 31, 0), [(5, 2.6, (0, 0, 160 * s if s < 0 else -160)), (4, 2, (0, 0, 150 * s if s < 0 else -150))], light=True)
        m.c(a, "light_blue_concrete", (10.6 * s, 23.6, 0), (3.4, 3.4, 3.4), (45, 0, 45), light=True)
        m.c(a, wind2, (10.6 * s, 23.6, 0), (4.6, 4.6, 4.6), (0, 45, 0), light=True)
    # head: smooth cap, wide visor eyes, cloud plume
    m.c("head", "light_blue_terracotta", (0, 40, 0), (8, 7, 8))
    m.c("head", "white_concrete", (0, 44, 0), (7, 1.6, 7))
    m.c("head", "black_concrete", (0, 40.4, 4.05), (6.4, 2, 0.2))
    m.m("head", "light_blue_concrete", (1.8, 40.4, 4.15), (1.8, 1, 0.1), light=True)
    for x, y, z, w in ((0, 46, -1, 5), (-2, 47, -3, 4), (2, 47.4, -3.6, 4), (0, 48.6, -5, 3)):
        m.c("head", cloud, (x, y, z), (w, w * 0.7, w))
    m.attacks = {"levitate": "raise", "pull": "spin", "shockwave": "pulse", "lightning": "dive"}
    m.melee = "swipe"
    m.spawn = {"style": "spiral", "particle": "GUST", "sound": "ENTITY_BREEZE_WIND_BURST"}
    m.death = {"style": "scatter", "swap": "", "particle": "GUST", "sound": "ENTITY_BREEZE_DEATH"}
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
    # see-through shell with rounded edges, the old core and swallowed loot inside
    m.c("body", shell, (0, 13, 0), (28, 26, 28))
    m.c("body", shell, (0, 13, 0), (30, 22, 24))
    m.c("body", shell, (0, 13, 0), (24, 22, 30))
    m.c("inner", "lime_concrete", (0, 14, 0), (12, 12, 12))
    m.c("inner", "green_concrete", (0, 14, 0), (8, 8, 13), (0, 0, 0))
    m.c("inner", "bone_block", (-7, 6, -6), (2, 7, 2), (0, 20, 60))
    m.c("inner", "gold_block", (8, 5, 5), (3, 1, 3), (0, 30, 0))
    m.c("inner", "iron_block", (6, 20, -7), (1, 9, 1.2), (30, 0, 20))
    m.c("inner", "diamond_block", (-6, 21, 6), (2, 2, 2), (45, 45, 0))
    # face on the shell
    m.m("body", "black_concrete", (5.4, 17.4, 15.1), (4, 5, 0.4))
    m.m("body", "white_concrete", (6.2, 18.6, 15.35), (1.4, 1.4, 0.2))
    m.c("mouth", "black_concrete", (0, 9, 15.1), (8, 2.4, 0.4))
    m.c("mouth", "green_concrete", (0, 8, 15.2), (5, 1, 0.3))
    # crown: gold band, points, gems, a red velvet top
    m.c("body", "gold_block", (0, 27, 0), (16, 3, 16))
    m.c("body", "red_wool", (0, 28.6, 0), (13, 2, 13))
    for k, (x, z) in enumerate(((-7, 7), (0, 7.6), (7, 7), (7.6, 0), (7, -7), (0, -7.6), (-7, -7), (-7.6, 0))):
        h = 4.6 if k % 2 else 3.4
        m.c("body", "gold_block", (x, 28.5 + h / 2, z), (2.2, h, 2.2), (0, 45, 0))
    for x, z, k in ((0, 8.1, "redstone_block"), (8.1, 0, "emerald_block"), (-8.1, 0, "lapis_block"), (0, -8.1, "diamond_block")):
        m.c("body", k, (x, 27, z), (1.8, 1.8, 0.4) if abs(z) > 1 else (0.4, 1.8, 1.8), light=True)
    m.c("body", "gold_block", (0, 31.6, 0), (2, 2, 2), (45, 0, 45))
    # royal cape with ermine trim
    m.c("body", "red_wool", (0, 13, -15.4), (24, 22, 0.8))
    m.c("body", "white_wool", (0, 24.6, -15.4), (25, 2.4, 1.2))
    for x in (-8, 0, 8):
        m.c("body", "black_wool", (x, 24.6, -16.05), (0.8, 1.2, 0.2))
    m.c("body", "white_wool", (0, 2, -15.4), (25, 2, 1.2))
    # a sceptre stuck in its side
    m.c("body", "gold_block", (16, 18, 4), (1.4, 16, 1.4), (0, 0, -25))
    m.c("body", "emerald_block", (19.6, 25.8, 4), (3, 3, 3), (45, 0, 20), light=True)
    m.attacks = {"leap": "slam", "quake": "hop", "minions": "burst", "poison": "spit"}
    m.melee = "hop"
    m.spawn = {"style": "drop", "particle": "ITEM_SLIME", "sound": "ENTITY_SLIME_SQUISH"}
    m.death = {"style": "splat", "swap": "", "particle": "ITEM_SLIME", "sound": "ENTITY_SLIME_DEATH"}
    return m

@model
def sunscorch():
    m = Model("sunscorch", "slime", 1.9)
    slime(m)
    # stacked molten layers with gaps that glow, a burning heart, solar flares turning around it
    m.c("inner", "ochre_froglight", (0, 14, 0), (20, 20, 20), light=True)
    m.c("inner", "shroomlight", (0, 14, 0), (16, 22, 16), (0, 45, 0), light=True)
    for i, (y, h) in enumerate(((0, 5), (6, 4.6), (11.6, 4.6), (17.2, 4.6), (22.8, 5))):
        m.c("body", "magma_block", (0, y + h / 2, 0), (26, h, 26), light=i in (1, 3))
        m.c("body", "nether_bricks" if i % 2 else "blackstone", (0, y + h / 2, 0), (26.4, h * 0.3, 26.4))
    m.c("body", "magma_block", (0, 29, 0), (20, 2.4, 20))
    m.m("body", "yellow_concrete", (6, 19.6, 13.25), (5, 2, 0.4), light=True)
    m.m("body", "white_concrete", (6, 19.6, 13.35), (2, 1, 0.4), light=True)
    m.c("mouth", "orange_concrete", (0, 8.6, 13.25), (10, 2, 0.4), light=True)
    for x in (-3.6, -1.2, 1.2, 3.6):
        m.c("mouth", "blackstone", (x, 9.8, 13.35), (1, 0.8, 0.3))
    import math
    for k in range(12):
        a = k * 30
        x, z = 17 * math.cos(math.radians(a)), 17 * math.sin(math.radians(a))
        h = 7 if k % 2 else 4.6
        m.c("inner", "orange_stained_glass" if k % 2 else "yellow_stained_glass", (x, 14, z), (h, 2, 2), (0, -a, 0), light=True)
    for k in range(6):
        a = k * 60 + 15
        x, z = 11 * math.cos(math.radians(a)), 11 * math.sin(math.radians(a))
        m.c("inner", "yellow_stained_glass", (x, 31.6, z), (2, 4, 2), (0, -a, 25), light=True)
    m.attacks = {"fire_ring": "burst", "leap": "slam", "quake": "hop", "minions": "spit"}
    m.melee = "hop"
    m.spawn = {"style": "unfold", "particle": "LAVA", "sound": "ENTITY_MAGMA_CUBE_SQUISH"}
    m.death = {"style": "implode", "swap": "", "particle": "FLAME", "sound": "ENTITY_MAGMA_CUBE_DEATH"}
    return m
