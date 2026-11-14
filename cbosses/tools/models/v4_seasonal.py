"""v4 seasonal bosses: Frostbottom rebuilt to walk, with stick arms that swing and snowball legs, and no
ice platform. The other seasonal bosses are improved in place in v2_seasonal and v3_seasonal."""
import math
from models import model, biped, horn, limb, quad, dirof
from build import Model
from kit import paint, band, stack, bevel, crack

SPAWN, DEATH = {}, {}


@model
def frostbottom():
    """Frostbottom, the snowman who wanted to walk: three great snowballs packed hard, the bottom one split
    into two stomping snowball legs, long stick arms with red mittens that wave and throw, a carrot nose,
    coal eyes and a coal grin, a striped scarf and a battered top hat. Snow golems follow him into battle."""
    m = Model("frostbottom", "biped", 1.9)
    biped(m, hip=9, legx=4, neck=28, shoulder=24, armx=8)
    m.bone("hat", "head", (0, 37, 0))
    m.bend = -30
    SN, SN2, CO, WD, MT, SC, SC2, HT = "snow_block", "white_concrete_powder", "coal_block", "spruce_log", "red_wool", "red_concrete", "green_concrete", "black_concrete"
    # legs: two packed snowballs, flattened at the foot, with a little ice where they meet the ground
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        bevel(m, b, SN, (x, 4.6, 0), (6.6, 8, 7), 1.6)
        m.c(b, SN2, (x, 0.6, 0.6), (6.4, 1.2, 7.6))
        m.c(b, "packed_ice", (x, 0.15, 0.6), (6.8, 0.3, 8))
    # body: a big snowball for the belly with coal buttons, a smaller one for the chest
    bevel(m, "hips", SN, (0, 12.4, 0), (14, 8, 12), 2.4)
    bevel(m, "body", SN, (0, 19.6, 0), (15, 8, 13), 2.6)
    bevel(m, "body", SN, (0, 24.6, 0), (11, 6, 10), 2.0)
    for y in (13, 17, 21):
        m.c("body" if y > 14 else "hips", CO, (0, y, 6.3 if y > 14 else 6.1), (1.6, 1.6, 0.6))
    for (x, y, z) in ((-5, 22, 5.8), (5.6, 16, 5.9), (-4, 12, -6)):
        m.c("body" if y > 14 else "hips", SN2, (x, y, z), (2, 1.6, 0.6))
    # the scarf: red and green stripes round the neck, one end hanging down the front
    m.c("body", SC, (0, 27.8, 0), (10.4, 1.8, 9.4))
    for k in range(4):
        m.c("body", SC if k % 2 == 0 else SC2, (3, 26 - k * 1.6, 5.2), (2.4, 1.6, 0.6), (0, 0, 6))
    # arms: long crooked sticks with twigs, ending in big red mittens
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8 * s
        tip = limb(m, a, WD, (x - 1.4 * s, 24, 0), [(6, 1.2, (0, 0, -100 * s)), (6, 1.0, (0, 0, -150 * s))])
        m.c(a, WD, (x + 4 * s, 24.6, 0), (0.6, 2.4, 0.6), (0, 0, -30 * s))
        bevel(m, a, MT, (tip[0], tip[1] - 1.2, tip[2]), (3, 3.4, 3), 0.6)
        m.c(a, MT, (tip[0] - 1.6 * s, tip[1] - 0.6, tip[2] + 0.8), (1.2, 1.6, 1.2))
        m.c(a, "white_wool", (tip[0], tip[1] + 0.8, tip[2]), (3.2, 0.8, 3.2))
    # the head: a round snowball, coal eyes and grin, a long carrot nose
    bevel(m, "head", SN, (0, 32.6, 0.4), (9, 9, 9), 1.8)
    for s in (1, -1):
        m.c("head", CO, (2 * s, 34, 4.95), (1.6, 1.6, 0.4))
        m.c("head", "white_concrete", (1.6 * s, 34.4, 5.2), (0.5, 0.5, 0.1))
    for k, x in enumerate((-2.4, -1.2, 0, 1.2, 2.4)):
        m.c("head", CO, (x, 30.4 + (0.5 if k in (0, 4) else 0), 4.95), (0.8, 0.8, 0.4))
    m.c("head", "orange_concrete", (0, 32.6, 6.6), (1.4, 1.4, 3.4))
    m.c("head", "orange_terracotta", (0, 32.6, 8.6), (0.8, 0.8, 1.2))
    # the top hat: tall, black and a little crushed, a red band with a sprig of holly
    m.c("hat", HT, (0, 37.2, 0.4), (11, 0.8, 11))
    m.c("hat", HT, (0, 40.4, 0.4), (7, 6, 7), (0, 0, 6), (0, 37.2, 0.4))
    m.c("hat", SC, (0, 38.4, 0.4), (7.2, 1.2, 7.2), (0, 0, 6), (0, 37.2, 0.4))
    m.c("hat", SC2, (2.4, 38.6, 4), (1.6, 1.0, 0.4))
    m.c("hat", SC, (2.8, 39.2, 4.2), (0.6, 0.6, 0.3))
    m.attacks = {"volley": "cast", "quake": "stomp", "minions": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m
