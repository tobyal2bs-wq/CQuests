"""v3 seasonal bosses."""
import math
from models import model, biped, horn, limb, quad
from build import Model
from kit import paint, band, stack, bevel, crack
from v3_kit import grow, vines, flower
from v2_seasonal import blob

SPAWN, DEATH = {"sunscorch": [{"op": "pose", "at": 0}], "brain_freeze": [{"op": "pose", "at": 0}]}, {}


@model
def sunscorch():
    """A small sun that came to the beach and is melting: a glowing orange jelly with a white-hot core,
    a crown of flame rays, big pink sunglasses, a melting grin with its tongue out, drips running down
    its sides and a rubber duck swim ring round its middle."""
    m = Model("sunscorch", "slime", 1.9)
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 14, 0))
    m.bone("mouth", "body", (0, 10, 14))
    # a melting little sun, far too hot, on holiday: a glowing orange jelly with a yellow core
    sh, sh2 = "orange_stained_glass", "yellow_stained_glass"
    blob(m, "body", sh, (0, 13, 0), (28, 24, 28), 5)
    m.c("body", sh, (0, 1.2, 0), (32, 2.4, 32))
    blob(m, "inner", "yellow_concrete", (0, 14, 0), (14, 13, 14), 3, light=True)
    m.c("inner", "orange_concrete", (0, 14, 0), (8, 8, 14.4), light=True)
    # sun rays poking up round the top like a crown of flames
    for k in range(10):
        a = math.radians(k * 36 + 18)
        h = 6 if k % 2 else 4.4
        x, z = 11.4 * math.cos(a), 11.4 * math.sin(a)
        m.c("body", sh2, (x, 25 + h / 2, z), (2.6, h, 2.6), (math.degrees(math.sin(a)) * 0.4, -k * 36 - 18, -math.degrees(math.cos(a)) * 0.4), light=True)
    # melting: drips sliding down, a puddle spreading round its base
    for x, z, h in ((-9, 14.6, 6), (5, 14.6, 4), (14.6, 7, 5), (-14.6, -4, 7), (9, -14.6, 4)):
        m.c("body", sh2, (x, 3.4 + h / 2, z), (1.8, h, 1.8), light=True)
        m.c("body", sh2, (x, 3, z), (2.6, 1.6, 2.6), light=True)
    m.c("body", "orange_stained_glass", (0, 0.2, 0), (34, 0.4, 32))
    # face: huge sunglasses with a pink rim, sunscreen smeared on the nose, a melting grin, tongue out
    for s in (1, -1):
        m.c("body", "black_stained_glass", (5 * s, 17.6, 14.4), (7.4, 4.6, 0.6))
        m.c("body", "magenta_concrete", (5 * s, 20.2, 14.6), (8, 0.8, 0.8))
        m.c("body", "white_concrete", (6.6 * s, 18.6, 14.8), (1.4, 0.8, 0.2), (0, 0, 30))
        m.c("body", "magenta_concrete", (12.4 * s, 18.6, 9), (0.6, 0.6, 12))
        m.c("body", "pink_concrete", (9.6 * s, 13, 14.2), (3, 1.4, 0.4))
    m.c("body", "magenta_concrete", (0, 18.4, 14.6), (2.6, 0.8, 0.8))
    m.c("body", "white_concrete", (0, 15, 14.6), (3.4, 2.4, 1.2))
    m.c("body", "white_concrete", (0, 15.6, 15.4), (1.2, 1, 0.6))
    m.c("mouth", "black_concrete", (0, 9.6, 14.3), (12, 3, 0.4))
    for x in (-4.6, -1.6, 1.6, 4.6):
        m.c("mouth", "white_concrete", (x, 10.8, 14.5), (1.6, 0.9, 0.3))
    m.c("mouth", "red_concrete", (2.4, 7.4, 15.2), (3.6, 4, 1.4), (20, 0, -8))
    m.c("mouth", "pink_concrete", (2.4, 6, 16), (2.6, 1.6, 0.8), (20, 0, -8))
    # a rubber duck float ring round its middle, the duck head grinning back at you
    for k in range(16):
        a = k * 22.5
        x, z = 16.6 * math.cos(math.radians(a)), 16.6 * math.sin(math.radians(a))
        c = "yellow_concrete" if (k // 2) % 2 else "white_concrete"
        m.c("body", c, (x, 7.4, z), (4.6, 4.2, 7), (0, -a, 0))
    m.c("body", "yellow_concrete", (-11, 12.6, 14), (5, 5, 5), (0, -30, 0))
    m.c("body", "orange_concrete", (-12.2, 12, 16.8), (3, 1.2, 2.4), (0, -30, 0))
    m.m("body", "black_concrete", (-9.6 + 0, 13.8, 16.2), (0.8, 0.8, 0.2), (0, -30, 0))
    m.c("body", "black_concrete", (-12.6, 13.8, 14.2), (0.8, 0.8, 0.2), (0, -30, 0))
    # a second ring of short flames between the rays, all lit
    for k in range(10):
        an = math.radians(k * 36)
        x, z = 10.6 * math.cos(an), 10.6 * math.sin(an)
        m.c("body", "orange_concrete", (x, 25.6, z), (2, 2.6, 2), (0, -k * 36, 0), light=True)
    # the hot heart: shroomlight flares inside the core
    for (x, y, z) in ((4, 18, 3), (-4, 11, -3), (3, 9, -4), (-3, 19, 4)):
        m.c("inner", "shroomlight", (x, y, z), (3, 3, 3), (45, 0, 45), light=True)
    # angry brows over the shades, peeling sunburn, a sunscreen bottle stuck in its side, a beach spade
    for s_ in (1, -1):
        m.c("body", "orange_concrete", (5 * s_, 21.8, 14.6), (6, 1, 0.6), (0, 0, 14 * s_), light=True)
        m.c("body", "white_terracotta", (10 * s_, 22, 13.4), (1.6, 1, 0.3))
        m.c("body", "white_terracotta", (11.4 * s_, 16, 14.2), (1, 1.4, 0.3))
    m.c("body", "white_concrete", (0, 23.6, 14.4), (2, 0.6, 0.3))
    # more drips, heavier on the sunny side
    for x, z, h in ((-3, 14.7, 7), (11, 11.4, 5), (-12, 10, 3), (14.7, -9, 6), (0, -14.7, 5)):
        m.c("body", "yellow_stained_glass", (x, 3.4 + h / 2, z), (1.4, h, 1.4), light=True)
    m.attacks = {"leap": "slam", "quake": "hop", "fire_ring": "burst", "volley": "spit"}
    m.melee = "hop"
    return m


@model
def brain_freeze():
    """An ice cream with a brain freeze and a bad temper: a waffle cone for legs and hips, three scoops
    stacked up (mint, vanilla, strawberry) dripping over each other, an angry face on the vanilla scoop
    with frosted brows, sprinkles, a cherry on top, two wafer-stick arms and a giant silver spoon."""
    m = Model("brain_freeze", "biped", 2.2)
    biped(m, hip=9, legx=2.4, neck=21, shoulder=17.5, armx=8.6)
    m.bone("spoon", "armR", (-8.6, 9, 2))
    m.hold = {"spoon": 15}
    m.bend = -35
    WF, WF2, MI, VA, ST, CH = "yellow_terracotta", "orange_terracotta", "lime_wool", "white_wool", "pink_wool", "brown_concrete"
    cone = {"A": WF2, "B": WF2}
    # legs: two short waffle stubs
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 2.4 * s
        m.c(b, WF, (x, 4.5, 0), (3.6, 9, 3.6))
        paint(m, b, "front", (x, 4.5, 1.85), ["X..", ".X.", "..X", "X..", ".X.", "..X"], {"X": WF2}, px=1.2, depth=0.2)
    # the cone: a wide waffle cup with a crosshatch, a rolled rim
    stack(m, "hips", WF, 0, 8, 0, [(8, 2, 8), (10, 2, 10), (12, 2, 12)])
    paint(m, "hips", "front", (0, 11, 6.05), ["X.X.X.", ".X.X.X", "X.X.X."], {"X": WF2}, px=2, depth=0.25)
    paint(m, "hips", "back", (0, 11, -6.05), ["X.X.X.", ".X.X.X", "X.X.X."], {"X": WF2}, px=2, depth=0.25)
    m.c("hips", WF2, (0, 14.4, 0), (13, 1, 13))
    # the scoops: mint at the bottom, vanilla (the face) in the middle, strawberry on top
    bevel(m, "body", MI, (0, 17.4, 0), (13, 5, 13), 1.6)
    for (x, z, L) in ((-5, 6, 2.4), (3, 6.2, 3.6), (6.2, -2, 2), (-6.2, -4, 3)):
        m.c("body", MI, (x, 14.8 - L / 2, z), (1.6, L, 1.6))
    for (x, z) in ((-3, 6.6), (2, 6.6), (5, 6.6)):
        m.c("body", CH, (x, 17.6 + (x % 2) * 0.6, z), (0.8, 0.8, 0.3))
    bevel(m, "head", VA, (0, 24, 0.2), (12, 8, 12), 1.6)
    for (x, z, L) in ((-4.4, 6.2, 2.4), (5, 4.4, 1.8), (-6, -3, 3)):
        m.c("head", VA, (x, 20.2 - L / 2, z), (1.6, L, 1.6))
    paint(m, "head", "front", (0, 24.4, 6.25), [
        "BB......BB",
        ".BBB..BBB.",
        "..WK..KW..",
        "..........",
        "...MMMM...",
        "..M....M..",
    ], {"B": "light_blue_concrete", "W": "white_concrete", "K": "black_concrete", "M": "red_terracotta"}, px=1, depth=0.3)
    for s in (1, -1):
        m.c("head", "pink_terracotta", (4.2 * s, 22.6, 6.3), (1.6, 1, 0.2))
    bevel(m, "head", ST, (0, 30.2, 0), (10, 5, 10), 1.4)
    for (x, z, L) in ((-3.4, 5.1, 2.2), (4, 3.6, 1.6)):
        m.c("head", ST, (x, 27.7 - L / 2, z), (1.4, L, 1.4))
    for k, (x, z) in enumerate(((-2, 2), (2.4, -1), (0, 4), (-3, -3), (3, 3), (1, -4))):
        c = ("yellow_concrete", "light_blue_concrete", "lime_concrete", "white_concrete")[k % 4]
        m.c("head", c, (x, 32.8, z), (1.4, 0.4, 0.5), (0, k * 40, 0))
    m.c("head", "red_concrete", (0.6, 34.2, 0.4), (2.6, 2.6, 2.6))
    m.c("head", "white_concrete", (0.0, 34.9, 1.6), (0.6, 0.6, 0.2))
    m.c("head", "green_concrete", (1.2, 36.4, 0.2), (0.4, 2, 0.4), (0, 0, -20))
    # little ice crystals round the head: the brain freeze
    for (x, y, z) in ((-7.4, 28, 2), (7.6, 26, -1), (6.4, 31, 3)):
        m.c("head", "light_blue_stained_glass", (x, y, z), (1.6, 1.6, 1.6), (45, 0, 45), light=True)
    # wafer-stick arms and the spoon
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8.6 * s
        m.c(a, WF, (x, 13.6, 0), (2.2, 8, 2.2))
        m.c(a, WF2, (x, 13.6, 1.15), (2.2, 8, 0.2))
        m.c(a, MI if s > 0 else ST, (x, 9, 0), (2.8, 2.6, 2.8))
    m.c("spoon", "iron_block", (-8.6, 15, 2), (1, 16, 1))
    bevel(m, "spoon", "iron_block", (-8.6, 25, 2), (1, 6, 4), 0.4)
    m.c("spoon", "light_gray_concrete", (-8.05, 25, 2), (0.2, 4.6, 2.8))
    m.c("spoon", VA, (-7.8, 25, 2), (0.8, 3, 2))
    m.attacks = {"freeze": "cast", "slam": "slam", "sprinkles": "sweep", "blizzard": "roar"}
    m.melee = "swipe"
    return m
