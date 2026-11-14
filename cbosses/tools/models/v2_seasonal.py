"""Seasonal bosses, three per season: winter, summer, Easter and Halloween. Hand built with the kit,
each with its own joke and its own silhouette."""
import math
from models import model, biped, horn, mhorn, limb, mlimb, taper, quad
from build import Model
from kit import paint, crack, band, hem, tufts, spikes, plate, stack, mirror_rows, bevel
from v2_general import quad_leg

SPAWN, DEATH = {}, {}


def ring(m, bone, block, y, rad, n, size, x0=0, z0=0, light=False, tilt=0, phase=0):
    for k in range(n):
        a = math.radians(phase + k * 360 / n)
        m.c(bone, block, (x0 + rad * math.sin(a), y, z0 + rad * math.cos(a)), size, (tilt, math.degrees(a), 0), light=light)


def present(m, bone, box, ribbon, center, size, rot=(0, 0, 0)):
    """A wrapped present: box, two ribbons crossing over it and a bow on top."""
    x, y, z = center
    w, h, d = size
    m.c(bone, box, center, size, rot, center)
    m.c(bone, ribbon, center, (w + 0.2, h + 0.2, d * 0.22), rot, center)
    m.c(bone, ribbon, center, (w * 0.22, h + 0.2, d + 0.2), rot, center)
    m.c(bone, ribbon, (x, y + h / 2 + 0.5, z), (w * 0.5, 0.9, 0.9), (rot[0], rot[1] + 45, rot[2]), center)


# ================================================================================================== WINTER

@model
def killer_claus():
    """Santa gone bad: a red coat with matted white fur, a beard stained grey at the tips, a crooked hat,
    glowing red eyes and a grin full of teeth. He drags a sack of stolen presents on his back, swings a
    giant candy-cane hook and keeps a burning lump of coal for the naughty."""
    m = Model("killer_claus", "biped", 1.8)
    biped(m, hip=14, legx=4, neck=34, shoulder=31.5, armx=10)
    m.bone("jaw", "head", (0, 34.6, 3))
    m.bone("sack", "body", (0, 30, -5))
    m.bone("cane", "armR", (-10, 12, 2))
    m.bone("coal", "armL", (10, 12, 2))
    m.hold = {"cane": 14}
    m.bend = -40
    RD, RD2, FU, FU2, BK, GD, SK = "red_concrete", "red_terracotta", "white_wool", "light_gray_wool", "black_concrete", "gold_block", "white_terracotta"
    # legs: red trousers tucked into black boots with fur cuffs and buckles
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        bevel(m, b, RD, (x, 10.4, 0), (5, 7.6, 5), 0.6)
        bevel(m, b, BK, (x, 3.4, 0.6), (5.6, 6.8, 6.2), 0.6)
        m.c(b, BK, (x, 0.8, 3.6), (5, 1.6, 2))
        m.c(b, FU, (x, 7, 0.4), (6.2, 1.8, 6.6))
        m.c(b, GD, (x, 3.6, 3.75), (1.6, 1.4, 0.3))
        m.c(b, BK, (x, 3.6, 3.95), (0.8, 0.6, 0.2))
    # the coat skirt: it flares over the hips, fur hem stained grey in places
    stack(m, "hips", RD, 0, 9, 0, [(14, 3, 10), (13, 3, 9.4)])
    m.c("hips", FU, (0, 8.6, 0), (14.6, 1.8, 10.6))
    for k, x in enumerate((-5.4, -1.8, 1.8, 5.4)):
        m.c("hips", FU2, (x, 8.4, 5.4), (1.6, 1.4, 0.3))
    m.c("hips", FU, (0, 12, 5.05), (2.6, 6, 0.4))
    # body: a round belly in the red coat, a black belt with a gold buckle, a fur placket
    bevel(m, "body", RD, (0, 22.4, 0.4), (13, 13, 9), 1.2)
    bevel(m, "body", RD, (0, 20.4, 3.6), (10, 8, 4), 1.2)
    m.c("body", RD2, (0, 26, 4.75), (9, 0.6, 0.3))
    band(m, "body", BK, (0, 17.6, 1), (13.4, 2.2, 10.4))
    paint(m, "body", "front", (0, 17.6, 6.2), ["GGGGG", "G.K.G", "GGGGG"], {"G": GD, "K": BK}, px=0.8, depth=0.3)
    m.c("body", FU, (0, 24.8, 4.9), (2.6, 12, 0.6))
    for y in (21.2, 24.2, 27.2):
        m.c("body", BK, (0, y, 5.3), (0.8, 0.8, 0.3))
    # fur collar and a mantle over the shoulders
    bevel(m, "body", FU, (0, 30.4, 0), (14.4, 2.6, 9.6), 0.8)
    tufts(m, "body", FU, [(-6, 31.6, 3.6), (-2, 31.8, 4.6), (2, 31.8, 4.6), (6, 31.6, 3.6), (-6, 31.6, -3.6), (6, 31.6, -3.6)], 1.8, alt=FU2)
    # arms: red sleeves, fur cuffs, black gloves
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10 * s
        bevel(m, a, RD, (x, 27.6, 0), (5.4, 7, 5.6), 0.7)
        bevel(m, a, RD, (x, 20.4, 0.6), (5, 7.4, 5.2), 0.6)
        m.c(a, RD2, (x + 2.6 * s, 24, 0.3), (0.3, 1, 5))
        m.c(a, FU, (x, 16.2, 0.8), (6, 2.2, 6.2))
        bevel(m, a, BK, (x, 13, 1.4), (4.2, 4.4, 4.2), 0.6)
        m.c(a, BK, (x - 1.6 * s, 13.4, 3.4), (1.4, 2.6, 1.4))
    # head: pale skin, red glowing eyes under thick angry brows, a red nose, rosy cheeks
    bevel(m, "head", SK, (0, 38.4, 0.4), (8.2, 7.6, 8), 1.0)
    paint(m, "head", "front", (0, 39.8, 4.45), [
        "WWW...WWW",
        ".WWW.WWW.",
        "..R...R..",
        "...PPP...",
        ".C.PPP.C.",
    ], {"W": "white_concrete", "R": ("redstone_block", 0.4, True), "P": "pink_concrete", "C": "pink_terracotta"}, px=0.9, depth=0.3)
    # moustache that curls up at the ends, then a big beard that hides the jaw
    paint(m, "head", "front", (0, 35.8, 4.9), ["WW.....WW", ".WWW.WWW.", "..WWWWW.."], {"W": "white_concrete"}, px=1.0, depth=0.6)
    bevel(m, "jaw", FU, (0, 32.6, 3.2), (9.4, 6.6, 3.2), 0.9)
    bevel(m, "jaw", FU, (0, 28.8, 3.8), (7, 4.4, 2.6), 0.8)
    m.c("jaw", FU2, (0, 26, 4), (4, 2.4, 2))
    m.c("jaw", FU2, (0, 24.6, 4.2), (2, 1.6, 1.4))
    tufts(m, "jaw", FU, [(-4.6, 30.6, 3.6), (4.6, 30.6, 3.6), (-3, 27.4, 4), (3, 27.4, 4)], 1.8, alt=FU2)
    # a gap in the beard showing a grin of sharp teeth
    m.c("jaw", BK, (0, 33.4, 4.85), (5.4, 1.6, 0.2))
    paint(m, "jaw", "front", (0, 33.6, 5.0), ["W.W.W.W", ".W.W.W."], {"W": "white_concrete"}, px=0.75, depth=0.2)
    # the hat: a fur band, then a red cone that bends back and droops, with a grey bobble
    bevel(m, "head", FU, (0, 42.6, 0.2), (9.6, 2.4, 9.4), 0.7)
    m.c("head", RD, (0, 45, -0.2), (8, 2.6, 8))
    m.c("head", RD, (0.4, 47.2, -1.2), (6.2, 2.6, 6.2), (-14, 0, 6), (0.4, 46, -1.2))
    m.c("head", RD, (1, 48.6, -3.4), (4.6, 2.4, 4.6), (-42, 0, 10), (1, 48, -3.4))
    m.c("head", RD2, (1.4, 48.4, -5.8), (3.4, 2.6, 3.4), (-80, 0, 14), (1.4, 48.4, -5.8))
    m.c("head", FU2, (1.6, 46.8, -7.6), (2.8, 2.8, 2.8), (20, 20, 0))
    m.c("head", RD2, (-2.6, 44.6, 3.9), (1.4, 1.2, 0.4))
    # the sack: lumpy, patched, tied with rope, stolen presents spilling out of the top
    bevel(m, "sack", "brown_wool", (0, 24.6, -10.4), (13, 14, 9), 1.6)
    bevel(m, "sack", "brown_wool", (0, 31.6, -10), (9, 3, 7), 0.8)
    m.c("sack", "brown_terracotta", (0, 33.4, -9.6), (6, 1.4, 5))
    paint(m, "sack", "back", (3, 22, -14.95), ["PPP", "P.P", "PPP"], {"P": "green_terracotta"}, px=1.2, depth=0.2)
    m.c("sack", "brown_terracotta", (-4.6, 26, -14.95), (0.3, 4, 0.3), (0, 0, 30))
    m.c("sack", "brown_terracotta", (0, 31, -5.6), (1, 1, 10), (-30, 0, 0))
    m.c("sack", "brown_terracotta", (0, 28, -1.4), (13.6, 1, 1))
    present(m, "sack", "green_concrete", "red_concrete", (-2.6, 36.4, -9.4), (4, 4, 4), (0, 20, 10))
    present(m, "sack", "blue_concrete", GD, (2.6, 35.8, -10.8), (3.6, 3, 3.6), (10, -15, -12))
    m.c("sack", RD, (0.6, 38.6, -11.8), (0.8, 6, 0.8), (20, 0, -20))
    m.c("sack", FU, (1.4, 37, -11.6), (0.9, 0.9, 0.9), (20, 0, -20))
    m.c("sack", "yellow_concrete", (-3.6, 34.6, -12.6), (1.4, 3.4, 1.4), (-20, 0, 30))
    m.c("sack", BK, (-4.2, 36.4, -13.2), (1.6, 1, 1.6), (-20, 0, 30))
    # the candy-cane hook: red and white stripes, a curled hook, a cruel point on the end
    for k in range(10):
        m.c("cane", RD if k % 2 else "white_concrete", (-10, 8 + k * 2.4, 2), (1.8, 2.4, 1.8), (0, 0, 0))
    hk = [(-10, 33.2, 2.6, -20), (-10, 35, 4.4, -60), (-10, 35, 6.8, -110), (-10, 33.2, 8.4, -150), (-10, 30.8, 8.8, -180)]
    for k, (x, y, z, r) in enumerate(hk):
        m.c("cane", "white_concrete" if k % 2 else RD, (x, y, z), (1.8, 2.8, 1.8), (r, 0, 0), (x, y, z))
    m.c("cane", "iron_block", (-10, 28.6, 8.8), (0.9, 2.4, 0.9))
    m.c("cane", BK, (-10, 9, 2), (2.2, 3.4, 2.2))
    # a lump of coal burning in his other fist
    m.c("coal", "coal_block", (10, 9.4, 3.2), (3.4, 3, 3.4), (20, 30, 10), (10, 9.4, 3.2))
    for (u, v) in ((0, 0), (0.8, 1)):
        m.c("coal", "orange_concrete", (10 + u, 9.4 + v * 0.6, 4.95), (1.6, 0.4, 0.3), (0, 0, 30 - v * 60), light=True)
    m.c("coal", "magma_block", (10, 11.2, 3.2), (1.6, 1, 1.6), light=True)
    m.attacks = {"coal": "cast", "hook": "sweep", "minions": "roar", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def frostbottom():
    """A snow golem grown huge and grumpy: three packed snowballs, a cracked ice face with coal eyes that
    glow cold blue, a carrot nose, stick arms with twig fingers, a striped scarf, a dented bucket for a hat
    and icicles hanging off every ledge. It slides around on a patch of ice instead of walking."""
    m = Model("frostbottom", "float", 1.9)
    m.bone("core", "root", (0, 12, 0))
    m.bone("head", "core", (0, 30, 0))
    m.mbone("armL", "core", (9, 25, 0))
    m.bone("ring1", "core", (0, 2, 0))
    m.bone("ring2", "head", (0, 40, 0))
    m.no_elbows = True
    SN, SN2, IC, IC2, CO, ST = "snow_block", "white_concrete", "packed_ice", "blue_ice", "coal_block", "spruce_log"
    # the bottom ball (rounded with three crossed boxes and a sagging rim), the ice patch it slides on
    bevel(m, "core", SN, (0, 7, 0), (16, 14, 16), 3)
    m.c("core", SN, (0, 1.2, 0), (13, 2.4, 13))
    for (x, z) in ((5, 6), (-6, 4), (6, -5), (-4, -6)):
        m.c("core", SN2, (x, 10.4, z), (3, 1.4, 3), (0, 30, 0))
    m.c("ring1", IC, (0, 0.3, 0), (24, 0.6, 24))
    m.c("ring1", IC2, (0, 0.4, 0), (16, 0.6, 16), (0, 45, 0))
    for k in range(6):
        a = math.radians(k * 60 + 15)
        m.c("ring1", IC, (math.sin(a) * 12.4, 1.2, math.cos(a) * 12.4), (2.2, 2.4, 2.2), (0, k * 60, 20))
    # middle ball with coal buttons, bottom ball sits slightly forward
    bevel(m, "core", SN, (0, 19, 0.4), (13, 11, 12), 2.4)
    for y in (16.6, 19.6, 22.6):
        m.c("core", CO, (0, y, 6.6), (1.8, 1.8, 0.6))
    # ice crust on the shoulders, icicles hanging all the way round
    m.c("core", IC, (0, 24.4, 0.4), (13.6, 0.8, 12.4))
    for k, (x, z, h) in enumerate(((-6, 6.2, 3), (-3, 6.4, 2), (3.4, 6.4, 3.4), (6.4, 5.8, 2.2), (-6.6, -4, 3), (6.6, -3, 2.4), (0, -6.2, 3.6), (-4, -6.2, 2))):
        m.c("core", IC2 if k % 3 == 0 else IC, (x, 13.6 - h / 2 + 10, z), (1.2, h, 1.2))
    for k, (x, z, h) in enumerate(((-7, 7, 2.6), (2, 8.1, 3.4), (7.6, 5, 2), (-8, -5, 3), (5, -8, 2.4))):
        m.c("core", IC, (x, 13.4 - h / 2, z), (1.4, h, 1.4))
    # the scarf: red and green stripes wound round the neck, one end blowing out behind
    for k in range(6):
        a = math.radians(k * 60)
        m.c("core", "red_wool" if k % 2 else "green_wool", (math.sin(a) * 5.4, 26.2, math.cos(a) * 5.4 + 0.4), (5.8, 2.6, 1.6), (0, k * 60, 0))
    for k in range(4):
        m.c("core", "green_wool" if k % 2 else "red_wool", (3 + k * 0.6, 24.4 - k * 2.2, -6.4 - k * 0.9), (2.6, 2.4, 0.6), (-20, 0, -10))
    hem(m, "core", "white_wool", 3.4, 6.6, 15.8, -10, 0.6, 3, long=1.6, short=0.8)
    # the head: smaller ball, a cracked ice face, coal eyes lit blue, a carrot nose, a frown of coal
    bevel(m, "head", SN, (0, 34, 0.4), (10.6, 9.4, 10), 2)
    paint(m, "head", "front", (0, 35, 5.45), [
        "KK...KK",
        "KBK.KBK",
        ".KK.KK.",
        ".......",
        ".K...K.",
        "..KKK..",
    ], {"K": CO, "B": ("light_blue_concrete", 0.4, True)}, px=1.0, depth=0.35)
    crack(m, "head", "front", (0, 34, 5.45), [(-4.6, 4), (-3.4, 4), (-3.4, 2.4)], block=IC2, width=0.5)
    crack(m, "head", "left", (5.35, 34, 0.4), [(-3, 3), (-1, 3), (-1, -1), (1.6, -1)], block=IC2, width=0.5)
    m.c("head", "orange_concrete", (0, 34.6, 7.6), (1.6, 1.6, 4.4))
    m.c("head", "orange_concrete", (0, 34.4, 10.4), (1, 1, 2.2))
    m.c("head", "orange_terracotta", (0, 35.2, 6.2), (1.8, 0.4, 1.4))
    # a dented bucket hat, tipped back, with icicles on its rim and a sprig of holly
    m.c("head", "iron_block", (0, 40, -0.4), (8.6, 1, 8.6), (-10, 0, 6))
    m.c("head", "iron_block", (0, 42.6, -0.8), (7.4, 4.6, 7.4), (-10, 0, 6))
    m.c("head", "gray_concrete", (0, 41.4, 2.95), (7.6, 0.6, 0.3), (-10, 0, 6))
    m.c("head", "gray_concrete", (2.4, 43.6, 2.7), (1.6, 1.6, 0.3), (-10, 0, 6))
    m.c("head", "green_concrete", (-3, 44.4, 2.4), (2.2, 1, 0.4), (0, 0, 30))
    m.c("head", "green_concrete", (-1.8, 44.8, 2.4), (2.2, 1, 0.4), (0, 0, -30))
    m.c("head", "red_concrete", (-2.4, 44.2, 2.75), (0.8, 0.8, 0.4))
    for x in (-3.6, 0, 3.4):
        m.c("head", IC, (x, 38.8, 4.2), (0.8, 1.8, 0.8))
    # floating snowflakes circling the head
    for k in range(6):
        a = math.radians(k * 60)
        x, z = math.sin(a) * 10, math.cos(a) * 10
        m.c("ring2", "white_concrete", (x, 40 + (k % 2) * 3, z), (1.6, 0.4, 0.4), (0, k * 60, 45))
        m.c("ring2", "white_concrete", (x, 40 + (k % 2) * 3, z), (0.4, 1.6, 0.4), (0, k * 60, 45))
    # stick arms: a branch with a fork, three twig fingers, a snowball in each hand
    for s, a in ((1, "armL"), (-1, "armR")):
        tip = limb(m, a, ST, (6 * s, 25, 0), [(7, 1.4, (10, 0, -70 * s)), (6, 1.2, (-20, 0, -110 * s)), (3, 1, (-30, 0, -150 * s))])
        limb(m, a, ST, (11.4 * s, 27, 0), [(3.4, 0.8, (0, 0, -30 * s))])
        x, y, z = tip
        for k, r in enumerate((-30, 0, 30)):
            m.c(a, ST, (x + 0.6 * s, y - 1.4, z + k * 0.8 - 0.8), (0.6, 2.6, 0.6), (r, 0, 0))
        bevel(m, a, SN, (x, y - 3.6, z + 1), (3.4, 3.4, 3.4), 0.8)
    # frost patches on the snow, snow piled up round the base, a corncob pipe in its frown
    for (y, z, w) in ((5, 8.05, 4), (18, 6.45, 3)):
        m.c("core", "light_blue_concrete", (-3.6, y, z), (w, 1, 0.2))
        m.c("core", "light_blue_concrete", (-4.6, y - 1, z), (w * 0.6, 1, 0.2))
    for (x, z, w) in ((7.6, 4, 5), (-7.4, -3, 6), (3, -7.6, 5), (-4, 7.6, 4), (7, -6, 3), (-7.6, 6, 3)):
        m.c("core", SN, (x, 1.4, z), (w, 2.8, w * 0.8), (0, x * 5, 0))
        m.c("core", SN2, (x, 3.2, z), (w * 0.6, 1, w * 0.5), (0, x * 5, 0))
    m.c("head", "yellow_terracotta", (2.4, 31.8, 6.4), (1.6, 2.2, 1.6))
    m.c("head", "brown_terracotta", (1.4, 31.4, 5.8), (2.4, 0.6, 0.6))
    m.c("head", "white_stained_glass", (2.4, 34, 6.4), (1, 1, 1), (45, 45, 0))
    m.c("head", "white_stained_glass", (2.9, 35.6, 6.4), (0.7, 0.7, 0.7), (45, 45, 0))
    # pebbles and rough lumps on the balls
    for (x, y, z) in ((7.8, 8, 2), (-7.8, 6, -1), (6.4, 20, 2), (-6.4, 18, -2), (0, 9, -8), (0, 20, -6.2), (5, 36, 3.6), (-5, 33, -2)):
        b = "head" if y > 30 else "core"
        m.c(b, SN2, (x, y, z), (1.8, 1.8, 1.8), (20, 30, 10))
    # a ridge of ice spikes growing up its back
    for k, (y, h) in enumerate(((10, 3), (15, 4), (20, 4.4), (24, 3.4))):
        m.c("core", IC2 if k % 2 else IC, (0, y, -7.6 + (k == 3) * 1.4), (1.6, h, 1.6), (-35, 0, 0))
    m.c("core", "light_blue_concrete", (0, 26.2, 7.4), (2, 2, 0.8), (0, 0, 45), light=True)
    for s_ in (1, -1):
        m.c("head", "pink_concrete", (3.8 * s_, 33.4, 5.5), (1.6, 0.8, 0.2))
    m.attacks = {"snowballs": "spin", "frost": "pulse", "slide": "dive", "minions": "raise"}
    m.melee = "swipe"
    return m


@model
def old_man_winter():
    """The spirit of winter as an old giant: an ice-blue robe embroidered with snowflakes, a mantle of
    white fur, a beard of icicles that reaches his belt, a crown of ice spikes and frozen breath. He leans
    on a frozen staff topped by a huge blue crystal and a lantern of cold light."""
    m = Model("old_man_winter", "biped", 1.95)
    biped(m, hip=14, legx=3.8, neck=35, shoulder=32.5, armx=9.6)
    m.bone("jaw", "head", (0, 35.6, 3))
    m.bone("cape", "body", (0, 33, -4))
    m.bone("staff", "armR", (-9.6, 12, 2))
    m.hold = {"staff": 0}
    m.bend = -46
    RB, RB2, TR, FU, IC, IC2, SK, SN = "light_blue_concrete", "blue_concrete", "white_concrete", "white_wool", "packed_ice", "blue_ice", "white_terracotta", "snow_block"
    # a long robe that hides the legs, widening to the ground with a fur hem and snowflake embroidery
    for s, b in ((1, "legL"), (-1, "legR")):
        bevel(m, b, RB2, (3.8 * s, 1.2, 1.6), (4.6, 2.4, 6), 0.5)
    stack(m, "hips", RB, 0, 1.4, 0, [(14, 3, 11), (13, 3, 10), (12, 3, 9.4), (11, 3, 8.8), (10.6, 2, 8.4)])
    m.c("hips", FU, (0, 1.6, 0), (14.6, 2, 11.6))
    m.c("hips", RB2, (0, 7.6, 5.05), (3, 12, 0.4))
    for y in (10, 6):
        paint(m, "hips", "front", (-4.4, y, 5.0 - (10 - y) * 0.05), [".T.", "TTT", ".T."], {"T": TR}, px=0.8, depth=0.2)
        paint(m, "hips", "front", (4.4, y, 5.0 - (10 - y) * 0.05), [".T.", "TTT", ".T."], {"T": TR}, px=0.8, depth=0.2)
    paint(m, "hips", "back", (0, 8, -5.05), ["T.T.T", ".TTT.", "TTTTT", ".TTT.", "T.T.T"], {"T": TR}, px=1.0, depth=0.2)
    # upper robe, a silver belt with an ice gem, and a heavy fur mantle
    bevel(m, "body", RB, (0, 23.6, 0), (11.4, 14, 7.6), 1.0)
    band(m, "body", "iron_block", (0, 17.6, 0), (11.8, 1.6, 8))
    m.c("body", IC2, (0, 17.6, 4.15), (2, 2, 0.6), (0, 0, 45), light=True)
    bevel(m, "body", FU, (0, 30.8, 0), (15, 3.6, 9.4), 1.0)
    tufts(m, "body", FU, [(-6.6, 29, 4), (-3.6, 28.6, 4.6), (3.6, 28.6, 4.6), (6.6, 29, 4), (-6.6, 29, -4), (0, 29, -4.6), (6.6, 29, -4)], 2, alt="light_gray_wool")
    # arms: wide sleeves with fur cuffs, old bony hands
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 9.6 * s
        bevel(m, a, RB, (x, 27.4, 0), (4.6, 7, 5), 0.6)
        bevel(m, a, RB, (x, 19.8, 0.8), (5.6, 8, 5.8), 0.7)
        m.c(a, RB2, (x, 16.4, 0.8), (5.8, 1, 6))
        m.c(a, FU, (x, 15.4, 0.8), (6, 1.4, 6.2))
        m.c(a, SK, (x, 13, 1.4), (3, 3.4, 3))
        paint(m, a, "left" if s > 0 else "right", (x + 2.95 * s, 22, 0.8), [".T.", "TTT", ".T."], {"T": TR}, px=0.8, depth=0.2)
    m.c("armL", SK, (10.6, 11.2, 3.2), (0.8, 2, 0.8))
    # the face: deep-set pale eyes that glow, frosted brows, a long nose, wrinkles
    bevel(m, "head", SK, (0, 39.2, 0.6), (7.8, 8.4, 7.8), 1.0)
    paint(m, "head", "front", (0, 40.4, 4.55), [
        "WWW.WWW",
        "WWW.WWW",
        ".B...B.",
        "...N...",
        ".K.N.K.",
    ], {"W": TR, "B": ("light_blue_concrete", 0.4, True), "N": SK, "K": "brown_terracotta"}, px=0.9, depth=0.3)
    m.c("head", SK, (0, 38.4, 5.2), (1.4, 2.6, 1.6))
    # the beard: a moustache that sweeps out, then layered icicles down to the belt
    paint(m, "head", "front", (0, 37, 5.0), ["WWW...WWW", ".WWWWWWW."], {"W": TR}, px=1.0, depth=0.6)
    bevel(m, "jaw", FU, (0, 33.4, 3.6), (8.4, 5, 2.6), 0.8)
    for k, (x, y, h, w) in enumerate(((-3.2, 29.4, 6, 1.8), (-1.2, 27.4, 10, 2.2), (1.2, 28, 9, 2.0), (3.2, 30, 5, 1.6), (0, 25, 12, 1.6), (-2.2, 28, 5, 1.2), (2.2, 27, 6, 1.2))):
        m.c("jaw", IC if k % 2 else FU, (x, y, 3.8 + (k % 3) * 0.3), (w, h, w), (0, 0, x * 2))
    m.c("jaw", IC2, (0, 18.8, 4), (0.8, 2, 0.8))
    # long white hair falling down the back and sides of the head
    m.c("head", TR, (0, 38.6, -3.6), (8.6, 8, 1.6))
    m.c("head", FU, (0, 34.4, -3.8), (7.6, 3.4, 1.4))
    for s_ in (1, -1):
        m.c("head", TR, (4.15 * s_, 38.6, -0.6), (0.8, 7, 5))
        m.c("head", FU, (4.3 * s_, 34.6, -1.2), (1, 4, 3.6))
    m.c("head", TR, (0, 42.8, 0.6), (8, 0.8, 8))
    # a crown of ice spikes, tallest at the front, set in a silver band
    band(m, "head", "iron_block", (0, 43.6, 0.6), (8.6, 1.4, 8.6))
    for k in range(8):
        a = math.radians(k * 45)
        h = (6.4 if k == 0 else 4.6 if k in (1, 7) else 3.4)
        x, z = math.sin(a) * 4, math.cos(a) * 4 + 0.6
        m.c("head", IC if k % 2 else IC2, (x, 44.2 + h / 2, z), (1.4, h, 1.4), (math.cos(a) * 12, 0, -math.sin(a) * 12), (x, 44.2, z), light=k == 0)
    # cape: a long fur-trimmed blue cloak with a frost pattern, torn into icicles at the bottom
    m.c("cape", RB2, (0, 18.6, -4.8), (13, 28, 0.8))
    m.c("cape", FU, (0, 32.4, -5), (14, 1.6, 1.2))
    hem(m, "cape", RB2, -6.5, 6.5, 4.6, -4.8, 0.8, 7, long=3, short=1.2)
    hem(m, "cape", IC, -6, 6, 5.6, -5.4, 0.4, 4, long=3.4, short=1.6, seed=2)
    paint(m, "cape", "back", (0, 20, -5.3), [
        "...T...",
        "T..T..T",
        ".T.T.T.",
        "..TTT..",
        "TTTTTTT",
        "..TTT..",
        ".T.T.T.",
        "T..T..T",
        "...T...",
    ], {"T": TR}, px=1.1, depth=0.2)
    # the staff: frozen wood wrapped in ice, a great crystal and a cold lantern hanging under it
    for k in range(4):
        m.c("staff", "stripped_spruce_log", (-9.6, 5 + k * 7, 2), (1.4, 7, 1.4))
        m.c("staff", IC, (-9.6, 8 + k * 7, 2), (1.8, 1.2, 1.8), (0, 45, 0))
    bevel(m, "staff", IC2, (-9.6, 37.6, 2), (3.4, 6.4, 3.4), 0.7, light=True)
    m.c("staff", IC, (-9.6, 37.6, 2), (4.6, 2.2, 4.6), (0, 45, 0))
    for s in (1, -1):
        m.c("staff", IC, (-9.6 + 2.4 * s, 36, 2), (1.4, 4, 1.4), (0, 0, 24 * s))
    m.c("staff", "white_stained_glass", (-9.6, 42, 2), (1.2, 2.4, 1.2), light=True)
    m.c("staff", "chain", (-11.8, 31.4, 2), (0.6, 3, 0.6))
    m.c("staff", "soul_lantern", (-11.8, 28.6, 2), (2.2, 2.6, 2.2), light=True)
    m.attacks = {"blizzard": "cast", "frost": "roar", "spikes": "slam", "minions": "double"}
    m.melee = "swipe"
    return m


def blob(m, bone, block, center, size, r=1.5, rot=None, origin=None, light=False):
    bevel(m, bone, block, center, size, r, rot, origin, light)


# ================================================================================================== SUMMER

@model
def sunscorch():
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
    # sweat drops flying off its forehead
    for x, y in ((-12.6, 24), (13.4, 22), (-14.6, 20)):
        m.c("body", "light_blue_stained_glass", (x, y, 9), (1.4, 2.2, 1.4), (0, 0, 20 if x > 0 else -20))
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
    # a cocktail umbrella stuck in its head, and a straw
    m.c("body", "white_concrete", (5, 31, -3), (0.6, 12, 0.6), (0, 0, -12))
    m.c("body", "lime_concrete", (6.4, 37, -3), (12, 0.8, 12), (0, 45, -12))
    m.c("body", "pink_concrete", (6.6, 37.8, -3), (8, 0.8, 8), (0, 45, -12))
    m.c("body", "yellow_concrete", (6.8, 38.6, -3), (3, 0.8, 3), (0, 45, -12))
    m.c("body", "red_concrete", (-5, 30, 2), (0.8, 10, 0.8), (14, 0, 20))
    m.c("body", "red_concrete", (-7, 34.8, 3.2), (0.8, 3, 0.8), (40, 0, 70))
    # a lei of flowers round its middle, above the duck ring
    for k in range(14):
        an = math.radians(k * 360 / 14)
        c = ("pink_concrete", "white_concrete", "magenta_concrete", "yellow_concrete")[k % 4]
        m.c("body", c, (math.sin(an) * 14.6, 11.6 + (k % 2) * 0.6, math.cos(an) * 14.6), (2.4, 2.4, 1), (0, math.degrees(an), 45))
    for k in range(7):
        an = math.radians(k * 360 / 7 + 13)
        m.c("body", "lime_concrete", (math.sin(an) * 14.3, 11, math.cos(an) * 14.3), (1.6, 0.6, 0.6), (0, math.degrees(an), 0))
    # a second ring of short flames between the rays, all lit
    for k in range(10):
        an = math.radians(k * 36)
        x, z = 10.6 * math.cos(an), 10.6 * math.sin(an)
        m.c("body", "orange_concrete", (x, 25.6, z), (2, 2.6, 2), (0, -k * 36, 0), light=True)
    # its beach spot: a striped towel under it, a beach ball, flip-flops left in front, a coconut drink
    m.c("body", "light_blue_wool", (-4, 0.1, 2), (40, 0.2, 22), (0, 15, 0))
    for k in range(4):
        m.c("body", "white_wool", (-4 + (k - 1.5) * 8 * math.cos(math.radians(15)), 0.22, 2 + (k - 1.5) * 8 * math.sin(math.radians(-15)) * -1), (2.4, 0.2, 21.6), (0, 15, 0))
    for k, c in enumerate(("red_concrete", "white_concrete", "blue_concrete", "yellow_concrete")):
        m.c("body", c, (-19, 3.2, 8), (6, 6, 6), (0, k * 22.5, 0), (-19, 3.2, 8)) if k == 0 else m.c("body", c, (-19, 3.2, 8 + (k - 2) * 0.01), (6.2, 4.4 - k * 0.6, 4.4 - k * 0.6) if k % 2 else (4.4, 6.2, 4.4), (0, k * 30, 0))
    for x in (-3, 3):
        m.c("body", "lime_concrete", (x, 0.5, 20), (2.4, 0.6, 5), (0, x * 3, 0))
        m.c("body", "pink_concrete", (x, 1.1, 19), (0.4, 0.8, 2.6), (0, x * 3, 0))
    m.c("body", "brown_terracotta", (10, 2, 18.6), (3.6, 3.6, 3.6))
    m.c("body", "white_concrete", (10, 3.9, 18.6), (2.6, 0.3, 2.6))
    m.c("body", "pink_concrete", (10.6, 5.6, 18.6), (0.4, 3.6, 0.4), (0, 0, -15))
    # the hot heart: shroomlight flares inside the core
    for (x, y, z) in ((4, 18, 3), (-4, 11, -3), (3, 9, -4), (-3, 19, 4)):
        m.c("inner", "shroomlight", (x, y, z), (3, 3, 3), (45, 0, 45), light=True)
    # angry brows over the shades, peeling sunburn, a sunscreen bottle stuck in its side, a beach spade
    for s_ in (1, -1):
        m.c("body", "orange_concrete", (5 * s_, 21.8, 14.6), (6, 1, 0.6), (0, 0, 14 * s_), light=True)
        m.c("body", "white_terracotta", (10 * s_, 22, 13.4), (1.6, 1, 0.3))
        m.c("body", "white_terracotta", (11.4 * s_, 16, 14.2), (1, 1.4, 0.3))
    m.c("body", "white_concrete", (15.4, 17, -3), (2.6, 5, 2.6), (0, 0, -30))
    m.c("body", "blue_concrete", (16.8, 19.8, -3), (1.6, 1.4, 1.6), (0, 0, -30))
    m.c("body", "light_blue_concrete", (15.3, 16.6, -1.65), (2, 2, 0.2), (0, 0, -30))
    m.c("body", "red_concrete", (-12, 6, -14.6), (0.6, 8, 0.6), (30, 0, 10))
    m.c("body", "red_concrete", (-12.6, 11.4, -16.6), (2.4, 3, 0.4), (30, 0, 10))
    m.c("body", "yellow_concrete", (12, 4.4, -14), (4, 4, 4))
    m.c("body", "orange_concrete", (12, 6.6, -14), (4.4, 0.6, 4.4))
    m.c("body", "sand", (12, 7.2, -14), (3.4, 0.6, 3.4))
    m.c("body", "white_concrete", (0, 23.6, 14.4), (2, 0.6, 0.3))
    # more drips, heavier on the sunny side
    for x, z, h in ((-3, 14.7, 7), (11, 11.4, 5), (-12, 10, 3), (14.7, -9, 6), (0, -14.7, 5)):
        m.c("body", "yellow_stained_glass", (x, 3.4 + h / 2, z), (1.4, h, 1.4), light=True)
    m.attacks = {"leap": "slam", "quake": "hop", "fire_ring": "burst", "volley": "spit"}
    m.melee = "hop"
    return m


@model
def admiral_pinchworth():
    m = Model("admiral_pinchworth", "spider", 1.7)
    m.bone("body", "root", (0, 12, 0))
    m.bone("abdomen", "body", (0, 16, -4))
    m.bone("head", "body", (0, 14, 9))
    m.bone("fangL", "head", (10, 14, 10))
    m.bone("fangR", "head", (-10, 14, 10))
    sh, sh2, leg, belly = "red_concrete", "red_terracotta", "orange_terracotta", "white_terracotta"
    # a wide flat crab shell, bumpy rim, pale belly
    blob(m, "body", sh, (0, 14, 0), (26, 8, 20), 2.4)
    m.c("body", sh2, (0, 18.4, 0), (18, 1.4, 12))
    for x in (-10, -5, 0, 5, 10):
        m.c("body", sh2, (x, 15, 10.4), (2.4, 2, 1), (0, 0, 45))
    for x, z in ((-7, 3), (7, 3), (-4, -4), (4, -4), (0, 1)):
        m.c("body", sh, (x, 19.2, z), (2.2, 1.2, 2.2))
    m.c("body", belly, (0, 10, 0), (20, 1, 15))
    # a whole sandcastle built on its back, with a little flag and a starfish
    m.c("abdomen", "sandstone", (0, 22, -4), (12, 6, 10))
    for x, z in ((-5, -8), (5, -8), (-5, 0), (5, 0)):
        m.c("abdomen", "sandstone", (x, 27, z), (3.4, 5, 3.4))
        m.c("abdomen", "smooth_sandstone", (x, 30, z), (4, 1, 4))
    m.c("abdomen", "smooth_sandstone", (0, 25.6, -4), (13, 1, 11))
    m.c("abdomen", "sandstone", (0, 28, -4), (5, 6, 5))
    m.c("abdomen", "black_concrete", (0, 23, 1.05), (2, 3, 0.2))
    # its weak spot: the treasure it hides in the castle, a glowing pearl in the gate
    m.c("abdomen", "sea_lantern", (0, 22.6, 1.4), (3.4, 3.4, 3.4), light=True)
    m.c("abdomen", "spruce_log", (0, 34, -4), (0.5, 6, 0.5))
    m.c("abdomen", "blue_concrete", (1.6, 36, -4), (3, 2, 0.2))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (3.6, 0.8, 0.8), (0, 0, 36))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (3.6, 0.8, 0.8), (0, 0, -36))
    m.c("abdomen", "orange_concrete", (-6.6, 20.6, 1.4), (0.8, 3.6, 0.8))
    # googly eyes on stalks, a twirled moustache, a tiny admiral's bicorne
    m.c("head", sh, (0, 14, 10.6), (14, 5, 3))
    for s in (1, -1):
        m.c("head", sh2, (3 * s, 19, 10.6), (1.2, 7, 1.2), (0, 0, -10 * s))
        m.c("head", "white_concrete", (3.6 * s, 22.8, 10.6), (3.4, 3.4, 3.4))
        m.c("head", "black_concrete", (3.6 * s + 0.4 * s, 22.2, 12.35), (1.4, 1.4, 0.2))
        m.c("head", "black_concrete", (4.4 * s, 14.8, 12.2), (4, 0.9, 0.6), (0, 0, -20 * s))
        m.c("head", "black_concrete", (6.4 * s, 15.8, 12.2), (1, 1, 0.6))
    m.c("head", "black_concrete", (0, 12.2, 12.15), (4, 0.8, 0.2))
    m.c("head", "blue_terracotta", (0, 26, 9.6), (11, 2.6, 2), (0, 0, 0))
    m.c("head", "blue_terracotta", (0, 27.4, 9.6), (7, 2, 1.8))
    m.c("head", "gold_block", (0, 25, 10.7), (11.2, 0.6, 0.2))
    m.c("head", "white_concrete", (0, 27.4, 10.6), (1.6, 1.6, 0.2))
    # big lopsided claws: the left one is massive and keeps snapping
    for s, b, k in ((1, "fangL", 1.4), (-1, "fangR", 1.0)):
        limb(m, b, leg, (10 * s, 14, 10), [(6, 2.2, (-60, 0, -30 * s)), (5, 2, (-90, 0, 10 * s))])
        cx, cy, cz = 13 * s, 14.6, 20
        m.c(b, sh, (cx, cy, cz), (5 * k, 4.4 * k, 6 * k))
        m.c(b, sh, (cx + 1 * s, cy + 0.4, cz + 5.4 * k), (3 * k, 2.4 * k, 6 * k), (-8, 0, 0))
        m.c(b, sh2, (cx - 1.4 * s, cy - 1.8 * k, cz + 4.8 * k), (2.2 * k, 1.6 * k, 5 * k), (14, 0, 0))
        m.c(b, "white_terracotta", (cx + 1 * s, cy + 0.4, cz + 8.6 * k), (2.4 * k, 1.6 * k, 0.6))
    # eight legs splayed sideways, with pointed tips
    zs = {1: 5, 2: 2, 3: -1.5, 4: -5}
    fan = {1: 30, 2: 10, 3: -10, 4: -30}
    for i in (1, 2, 3, 4):
        m.bone(f"legL{i}", "body", (11, 13, zs[i]))
        m.bone(f"legR{i}", "body", (-11, 13, zs[i]))
        a = fan[i]
        mlimb(m, f"legL{i}", leg, (11, 13, zs[i]), [(8, 1.8, (a, 0, -60)), (13, 1.5, (a * 0.5, 0, -160), sh2), (5, 0.9, (a * 0.3, 0, -178), "white_terracotta")])
    # admiral's dress on the shell: gold epaulettes with fringe, a sash and medals across the front
    for s_ in (1, -1):
        m.c("body", "gold_block", (11 * s_, 18.6, 3), (5, 0.8, 4.4))
        for k in range(4):
            m.c("body", "gold_block", (13.4 * s_, 17.6, 1.4 + k * 1.1), (0.4, 1.6, 0.4))
    m.c("body", "blue_concrete", (0, 15.6, 10.8), (16, 1.6, 0.6), (0, 0, -12))
    for k, c in enumerate(("gold_block", "lapis_block", "gold_block", "emerald_block")):
        m.c("body", c, (-5 + k * 2.2, 13.6, 10.9), (1.2, 1.4, 0.4))
        m.c("body", "red_concrete", (-5 + k * 2.2, 15, 10.85), (0.8, 0.8, 0.3))
    # barnacles and darker spots on the shell, a frill of seaweed caught on the back
    for (x, z) in ((-9, -4), (9, -6), (-5, -8), (6, 6), (-10, 4), (2, -8)):
        m.c("body", "white_terracotta", (x, 18.4, z), (1.6, 1.2, 1.6))
        m.c("body", "light_gray_concrete", (x, 19, z), (0.6, 0.4, 0.6))
    for (x, z) in ((-3, 5), (3, -2), (-7, 0), (8, 1)):
        m.c("body", "red_terracotta", (x, 18.2, z), (2.4, 0.4, 2.4))
    for k, x in enumerate((-8, -4, 3, 8)):
        m.c("body", "green_terracotta" if k % 2 else "lime_terracotta", (x, 13.4, -10.4), (1.6, 6 - k % 2 * 2, 0.4), (10, 0, 6 - k * 4))
    # claw teeth along the pincers, joints on the claws
    for s_, b, k in ((1, "fangL", 1.4), (-1, "fangR", 1.0)):
        cx, cy, cz = 13 * s_, 14.6, 20
        for t in range(3):
            m.c(b, "white_terracotta", (cx - 1.4 * s_, cy - 0.4 * k, cz + (3 + t * 1.6) * k), (0.8 * k, 1.2 * k, 0.8 * k), (45, 0, 0))
        m.c(b, "red_terracotta", (cx, cy, cz - 3 * k), (3.6 * k, 3.6 * k, 1.4))
    # the sandcastle grows two more turrets with flags and a shell door
    for x, c in ((-7, "red_concrete"), (7, "yellow_concrete")):
        m.c("abdomen", "sandstone", (x, 24, -9), (3, 4, 3))
        m.c("abdomen", "smooth_sandstone", (x, 26.4, -9), (3.6, 0.8, 3.6))
        m.c("abdomen", "spruce_log", (x, 28.6, -9), (0.4, 3.6, 0.4))
        m.c("abdomen", c, (x + 1.2, 29.6, -9), (2, 1.4, 0.2))
    for k in range(4):
        m.c("abdomen", "smooth_sandstone", (-4.5 + k * 3, 32.2, -4), (1.6, 1.4, 1.6))
    m.c("abdomen", "pink_terracotta", (0, 25.6, 1.15), (2.6, 1.6, 0.3))
    m.c("head", "white_concrete", (0, 26, 10.7), (11.2, 0.4, 0.2))
    # eye-stalk rings and a pipe
    for s_ in (1, -1):
        m.c("head", "orange_terracotta", (3.2 * s_, 20.6, 10.6), (1.8, 0.6, 1.8))
    m.c("head", "brown_terracotta", (-3, 11.6, 13), (0.6, 0.6, 3))
    m.c("head", "brown_terracotta", (-3, 12.8, 14.4), (1.4, 1.8, 1.4))
    m.attacks = {"leap": "leap", "minions": "drum", "pull": "rearup", "volley": "spit"}
    m.melee = "fang"
    return m


@model
def brain_freeze():
    """A walking ice-cream cone with a headache: a waffle cone body, three scoops for a head (vanilla,
    strawberry with an angry face, chocolate with rows of sprinkles), whipped cream and a cherry, ice shards
    sticking out of its skull from the brain freeze. It swings a giant spoon and a rocket ice lolly."""
    m = Model("brain_freeze", "biped", 1.8)
    biped(m, hip=10, legx=3.6, neck=27, shoulder=24, armx=10.4)
    m.bone("spoon", "armR", (-10.4, 9.6, 2))
    m.bone("lolly", "armL", (10.4, 9.6, 2))
    m.hold = {"spoon": 18, "lolly": 10}
    m.bend = -40
    WF, WF2, VA, ST, CH, CR = "orange_terracotta", "brown_terracotta", "white_terracotta", "pink_concrete", "brown_concrete", "white_concrete"
    # legs: little wafer cones dipped in chocolate
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.6 * s
        stack(m, b, WF, x, 2.4, 0, [(3, 2.6, 3), (3.8, 2.6, 3.8), (4.6, 2.6, 4.6)])
        m.c(b, WF2, (x, 5, 0), (3.6, 0.4, 3.6))
        m.c(b, CH, (x, 1.2, 0.6), (5, 2.4, 6))
        m.c(b, CH, (x + 1.2 * s, 2.8, 2.4), (1, 1.6, 1))
    # the cone: point at the hips, widening up to a thick rolled rim, waffle lines all round
    stack(m, "hips", WF, 0, 7.6, 0, [(5, 1.6, 5), (7, 2, 7)])
    ys = stack(m, "body", WF, 0, 11.2, 0, [(9, 3, 8.4), (11, 3, 10), (13, 3, 11.4), (15, 3, 13), (17, 2.6, 14.4)])
    for k, (w, d) in enumerate(((9, 8.4), (11, 10), (13, 11.4), (15, 13))):
        m.c("body", WF2, (0, 14.2 + k * 3, 0), (w + 0.3, 0.5, d + 0.3))
    for k, (w, d, y) in enumerate(((11, 10, 15.7), (13, 11.4, 18.7), (15, 13, 21.7), (17, 14.4, 24.5))):
        for t in (-0.3, 0, 0.3):
            m.c("body", WF2, (t * w, y, d / 2 + 0.1), (0.5, 2.8, 0.3))
            m.c("body", WF2, (t * w, y, -d / 2 - 0.1), (0.5, 2.8, 0.3))
    bevel(m, "body", WF, (0, 26, 0), (18.6, 2.4, 15.6), 0.8)
    m.c("body", WF2, (0, 25.2, 0), (18.8, 0.4, 15.8))
    # melted vanilla running down over the rim
    for k, (x, h) in enumerate(((-7, 5), (-4, 3), (-0.6, 6.5), (3, 2.6), (6.4, 4.4))):
        m.c("body", VA, (x, 26 - h / 2, 7.4), (1.6, h, 0.6))
        m.c("body", VA, (x, 26 - h, 7.5), (2, 1.2, 0.8))
    for x, h in ((-5, 4), (2, 6), (6.6, 3)):
        m.c("body", VA, (x, 26 - h / 2, -7.4), (1.6, h, 0.6))
    # arms: soft-serve swirls, wafer cuffs, chocolate fists
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10.4 * s
        for k in range(3):
            m.c(a, CR if k % 2 else VA, (x, 22 - k * 2.4, 0), (5.4 - k * 0.3, 2.6, 5.4 - k * 0.3), (0, k * 30, 0))
        m.c(a, VA, (x, 15, 0.6), (4.4, 4, 4.4))
        m.c(a, WF, (x, 12.4, 0.8), (5, 1.6, 5))
        m.c(a, WF2, (x, 12.4, 0.8), (5.2, 0.4, 5.2))
        bevel(m, a, CH, (x, 10, 1.2), (4.2, 3.6, 4.2), 0.6)
    # the head: three scoops stacked, each overhanging the one below
    bevel(m, "head", VA, (0, 30.6, 0), (19, 7.6, 16.6), 2)
    for k, (x, z) in enumerate(((-7.6, 6), (7, 6.4), (-8.4, -5), (8.6, -4), (0, -7.8), (0, 7.8))):
        m.c("head", VA, (x, 27.4, z), (3, 2, 3), (0, k * 25, 0))
    bevel(m, "head", ST, (0, 37.6, 0.4), (16.4, 8, 14.4), 2)
    for k, (x, z) in enumerate(((-6.4, 6.4), (6, 6.4), (0, -6.6), (-7.6, -3))):
        m.c("head", ST, (x, 33.6, z), (2.6, 1.6, 2.6), (0, k * 25, 0))
    bevel(m, "head", CH, (0, 44.4, 0.2), (13, 7, 11.6), 2)
    # strawberry face: furious brows, ice-blue eyes squeezed by the headache, gritted teeth
    paint(m, "head", "front", (0, 38.4, 7.6), [
        "KKK.....KKK",
        ".KKK...KKK.",
        "..BB...BB..",
        "...........",
        "..WWWWWWW..",
        "..KWKWKWK..",
    ], {"K": "black_concrete", "B": ("light_blue_concrete", 0.4, True), "W": CR}, px=1.0, depth=0.3)
    for s in (1, -1):
        m.c("head", "red_concrete", (6 * s, 36, 7.5), (2, 1, 0.2))
    # rows of sprinkles on the chocolate, evenly spaced, each a little bar in a fixed colour order
    cols = ("red_concrete", "yellow_concrete", "lime_concrete", "light_blue_concrete", "white_concrete")
    k = 0
    for row, y in enumerate((42.6, 45.4)):
        for x in (-4.6, -1.6, 1.4, 4.4):
            m.c("head", cols[k % 5], (x + row * 1.4, y, 6.05), (1.4, 0.5, 0.3), (0, 0, 35 if (k % 2) else -35))
            k += 1
    for x, z in ((-3.6, -2), (0, 2.2), (3.4, -2.6), (-1, -4.6), (2.6, 3.4)):
        m.c("head", cols[k % 5], (x, 48, z), (1.4, 0.3, 0.5), (0, k * 40, 0))
        k += 1
    # brain freeze: shards of ice jammed into the chocolate, a frosty glow on top
    for s in (1, -1):
        m.c("head", "packed_ice", (6.8 * s, 46, 0), (1.4, 4, 1.4), (0, 0, -40 * s))
        m.c("head", "blue_ice", (6.6 * s, 43, -3), (1.2, 3, 1.2), (20, 0, -60 * s))
    # whipped cream swirl and a cherry
    stack(m, "head", CR, 0, 47.9, 0, [(8, 1.6, 7), (6, 1.6, 5.4), (3.6, 1.4, 3.4)])
    m.c("head", "red_concrete", (0, 53.6, 0), (3, 3, 3))
    m.c("head", "white_concrete", (-0.7, 54.4, 1.55), (0.6, 0.6, 0.1))
    m.c("head", "green_concrete", (0.6, 56.2, 0), (0.5, 2.6, 0.5), (0, 0, -20))
    # chocolate sauce running down from the top scoop
    for x, h in ((-4.6, 3), (1.6, 4.6), (5, 2.4)):
        m.c("head", CH, (x, 41 - h / 2, 6.0), (1.2, h, 0.5))
    # the giant spoon
    m.c("spoon", "iron_block", (-10.4, 18, 2), (1.2, 22, 0.6))
    m.c("spoon", "iron_block", (-10.4, 31, 2), (4.4, 6, 1))
    m.c("spoon", "light_gray_concrete", (-10.4, 31, 2.6), (3.4, 4.6, 0.3))
    m.c("spoon", VA, (-10.4, 30, 2.9), (2.6, 2.4, 0.6))
    # the rocket ice lolly: red, white and blue bands on a wooden stick
    m.c("lolly", "stripped_birch_log", (10.4, 11, 2), (1, 8, 1))
    for k, c in enumerate(("blue_concrete", "white_concrete", "red_concrete")):
        m.c("lolly", c, (10.4, 17 + k * 3.4, 2), (4 - k * 0.8, 3.4, 4 - k * 0.8))
    m.c("lolly", "red_concrete", (10.4, 23.6, 2), (1.2, 1.4, 1.2))
    m.c("lolly", "light_blue_stained_glass", (11.8, 14.6, 3.6), (0.8, 2.4, 0.8), light=True)
    m.attacks = {"freeze": "cast", "spoon": "slam", "sprinkles": "double", "minions": "roar"}
    m.melee = "swipe"
    return m


# ================================================================================================== EASTER

def egg(m, bone, color, stripe, center, size, rot=(0, 0, 0), stripe2=None):
    """A painted Easter egg: a rounded body, one stripe round the middle and a band of dots."""
    x, y, z = center
    w, h, d = size
    bevel(m, bone, color, center, size, min(w, d) / 4, rot, center)
    m.c(bone, stripe, (x, y, z), (w + 0.2, h * 0.16, d + 0.2), rot, center)
    if stripe2:
        m.c(bone, stripe2, (x, y + h * 0.26, z), (w * 0.9 + 0.2, h * 0.1, d * 0.9 + 0.2), rot, center)


@model
def clucksworth():
    """A huge hen dressed up for Easter and very angry about it: puffed white feathers with grey scale
    marks on the breast, a big red comb and wattle, an Easter bonnet with a pastel ribbon, a bandolier of
    painted eggs she throws like grenades, and feathered wings she slams the ground with."""
    m = Model("clucksworth", "biped", 1.8)
    biped(m, hip=11, legx=3.8, neck=26, shoulder=24, armx=8.6)
    m.bone("tail", "body", (0, 20, -8))
    m.no_elbows = False
    m.bend = -10
    WH, WH2, RD, BK, YE, OR = "white_concrete", "light_gray_concrete", "red_concrete", "black_concrete", "yellow_concrete", "orange_concrete"
    # legs: scaly yellow shanks, three toes forward and one back, dark talons
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.8 * s
        m.c(b, WH, (x, 10.4, 0), (4.4, 3, 4.4))
        m.c(b, YE, (x, 6, 0), (1.8, 7, 1.8))
        for k in range(3):
            m.c(b, "orange_terracotta", (x, 4.4 + k * 2, 0), (2.1, 0.4, 2.1))
        for k, r in enumerate((-28, 0, 28)):
            m.c(b, YE, (x + math.sin(math.radians(r)) * 2, 0.6, 2.2), (1.2, 1.2, 4), (0, r, 0))
            m.c(b, BK, (x + math.sin(math.radians(r)) * 4, 0.5, 4.2), (0.8, 0.8, 1), (0, r, 0))
        m.c(b, YE, (x, 0.6, -1.6), (1.2, 1.2, 2.6))
    # body: a round puffed chest, grey scale marks, a fluffy rump
    bevel(m, "hips", WH, (0, 13, -1), (13, 4, 13), 1.4)
    bevel(m, "body", WH, (0, 19.6, 0), (16, 12, 16), 3)
    bevel(m, "body", WH, (0, 18.6, 5.4), (12, 9, 6), 2)
    paint(m, "body", "front", (0, 18.4, 8.45), [
        "W.W.W.W",
        ".W.W.W.",
        "W.W.W.W",
        ".W.W.W.",
    ], {"W": WH2}, px=1.2, depth=0.2)
    tufts(m, "body", WH, [(-4, 25.6, 6), (0, 26, 6.4), (4, 25.6, 6), (-7.6, 22, 3), (7.6, 22, 3)], 2.4, alt=WH2)
    # the bandolier of painted eggs across the chest
    m.c("body", "brown_terracotta", (0, 19.6, 8.4), (1.6, 18, 0.6), (0, 0, -42))
    for k, (cs, st) in enumerate((("pink_concrete", "magenta_concrete"), ("light_blue_concrete", "white_concrete"), (YE, "lime_concrete"), ("lime_concrete", "pink_concrete"))):
        t = (k - 1.5) * 3.2
        egg(m, "body", cs, st, (t * 0.74, 19.6 + t * 0.67, 9.6), (2.2, 2.8, 1.8))
    # tail: a fan of stiff feathers sticking up at the back
    for k, r in enumerate((-36, -18, 0, 18, 36)):
        rr = math.radians(r)
        m.c("tail", WH if k % 2 else WH2, (math.sin(rr) * 3, 25 + math.cos(rr) * 2, -9.4), (2.6, 9, 1.2), (-30, 0, -r), (math.sin(rr) * 1, 22, -8.6))
    # wings: three layers of feathers, longest at the bottom, tips grey
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8.6 * s
        bevel(m, a, WH, (x + 0.6 * s, 20.6, 0), (2.4, 8, 11), 0.8)
        for k, (y, L, z) in enumerate(((17.4, 6, -1.6), (14.4, 7, -2.6), (11.6, 7, -3.6))):
            for f in range(3):
                m.c(a, WH2 if (f == 2 or k == 2) else WH, (x + 0.6 * s + 0.2 * s * k, y - f * 0.6, z + 3.4 - f * 3.4 + 2), (1.6, L - f * 1.2, 3.2))
    # the head: feathered, an orange beak, a three-lobed comb, a dangling wattle, red angry eyes
    bevel(m, "head", WH, (0, 30.8, 3.4), (8, 8.4, 8.6), 1.4)
    m.c("head", WH, (0, 26.6, 2.4), (7, 2, 7))
    paint(m, "head", "front", (0, 32, 7.75), ["KK...KK", ".KK.KK.", ".R...R."], {"K": BK, "R": ("redstone_block", 0.4, True)}, px=0.9, depth=0.3)
    m.c("head", OR, (0, 30, 9), (3, 1.4, 3))
    m.c("head", "yellow_terracotta", (0, 29, 8.6), (2.4, 0.8, 2.2))
    m.c("head", OR, (0, 30.4, 10.6), (1.6, 0.8, 1))
    for k, (z, h) in enumerate(((5.4, 3), (3.6, 4), (1.6, 3.4), (-0.2, 2.4))):
        m.c("head", RD, (0, 35 + h / 2, z), (1.4, h, 1.8))
    m.c("head", RD, (0, 27, 8.4), (1.4, 2.6, 1.2))
    m.c("head", RD, (0, 25.6, 8.6), (1.8, 1.4, 1.4))
    # the Easter bonnet: a straw brim tipped on the head, a pastel ribbon and a flower
    m.c("head", "yellow_terracotta", (0, 35, 1.6), (12, 0.8, 11), (-12, 0, 8))
    m.c("head", "yellow_terracotta", (1.6, 36.6, 0.6), (6, 3, 6), (-12, 0, 8))
    m.c("head", "pink_concrete", (1.6, 35.8, 0.6), (6.3, 1, 6.3), (-12, 0, 8))
    m.c("head", "pink_concrete", (5, 33, -3.6), (1.4, 5, 0.4), (10, 0, -20))
    m.c("head", "light_blue_concrete", (5.8, 33.4, -3.2), (1.4, 4.4, 0.4), (10, 0, 10))
    for k, (dx, dz) in enumerate(((0, 1), (1, 0), (0, -1), (-1, 0))):
        m.c("head", WH, (-2 + dx * 0.9, 37.2, 3.4 + dz * 0.9), (1.2, 0.6, 1.2))
    m.c("head", YE, (-2, 37.4, 3.4), (0.8, 0.8, 0.8))
    # three yellow chicks riding on her back, peeping over her shoulders
    for (x, z, r) in ((-4.4, -5.6, 20), (0.4, -7, 0), (4.6, -5.4, -25)):
        y = 26 + (1 if x == 0.4 else 0)
        bevel(m, "body", "yellow_concrete", (x, y, z), (3.2, 2.8, 3.2), 0.6, (0, r, 0), (x, y, z))
        m.c("body", "yellow_concrete", (x, y + 2.4, z + 0.4), (2.2, 2.2, 2.2), (0, r, 0), (x, y, z))
        fx, fz = math.sin(math.radians(r)), math.cos(math.radians(r))
        m.c("body", OR, (x + fx * 1.5, y + 2.2, z + 0.4 + fz * 1.5), (0.8, 0.5, 0.8), (0, r, 0))
        m.c("body", BK, (x + fx * 1.15 + fz * 0.6, y + 2.8, z + 0.4 + fz * 1.15 - fx * 0.6), (0.4, 0.4, 0.2), (0, r, 0))
        m.c("body", BK, (x + fx * 1.15 - fz * 0.6, y + 2.8, z + 0.4 + fz * 1.15 + fx * 0.6), (0.4, 0.4, 0.2), (0, r, 0))
    for s_ in (1, -1):
        m.c("head", "pink_concrete", (3.4 * s_, 29.8, 7.7), (1.2, 0.8, 0.2))
        m.c("head", WH2, (4.05 * s_, 31.6, 3.4), (0.2, 4, 5))
    m.attacks = {"eggs": "double", "slam": "slam", "minions": "roar", "peck": "lunge"}
    m.melee = "swipe"
    # the egg she hatches out of: a painted Easter egg built as rings of shell, gone once she breaks out
    m.bone("shell", "root", (0, 0, 0))
    bands = ("white_terracotta", "pink_concrete", "white_terracotta", "light_blue_concrete", "white_terracotta", "yellow_concrete", "white_terracotta", "lime_concrete")
    for k, (y, r) in enumerate(((3, 12.5), (8.5, 14.5), (14, 15), (19.5, 14.8), (25, 14), (30.5, 12.4), (36, 10), (41, 7))):
        blk = bands[k]
        m.c("shell", blk, (0, y, r), (2 * r, 5.6, 1.4))
        m.c("shell", blk, (0, y, -r), (2 * r, 5.6, 1.4))
        m.c("shell", blk, (r, y, 0), (1.4, 5.6, 2 * r - 1.4))
        m.c("shell", blk, (-r, y, 0), (1.4, 5.6, 2 * r - 1.4))
    m.c("shell", "white_terracotta", (0, 44.4, 0), (10, 1.6, 10))
    m.c("shell", "white_terracotta", (0, 0.4, 0), (24, 0.8, 24))
    return m


@model
def killer_bunny():
    """A rabbit that has had enough of Easter: matted white fur, one ear torn and flopped over, red eyes,
    two huge buck teeth, a pink bow with a bell gone grubby, a leather strap with an iron pauldron, huge
    hind feet, a carrot as long as a sword and a basket of eggs it hurls."""
    m = Model("killer_bunny", "biped", 1.7)
    biped(m, hip=12, legx=4, neck=29, shoulder=27, armx=8.4)
    m.bone("earL", "head", (2.4, 36.6, 0))
    m.bone("earR", "head", (-2.4, 36.6, 0))
    m.bone("carrot", "armR", (-8.4, 13, 2))
    m.bone("basket", "armL", (8.4, 13, 2))
    m.hold = {"carrot": 24, "basket": 0}
    m.bend = -44
    m.rest("body", (-8, 0, 0))
    m.rest("head", (8, 0, 0))
    FU, FU2, PK, RD, BK = "white_wool", "light_gray_wool", "pink_concrete", "redstone_block", "black_concrete"
    # legs: thick thighs, long rabbit feet flat on the ground with pink pads under the toes
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 4 * s
        bevel(m, b, FU, (x, 9.4, -0.6), (5.6, 6, 7), 1)
        m.c(b, FU, (x, 4.6, -1.4), (4, 5, 4))
        bevel(m, b, FU, (x, 1.3, 2.4), (4.6, 2.6, 10), 0.6)
        m.c(b, FU2, (x, 1.3, 7.3), (4.4, 2, 0.4))
        for t in (-1.2, 1.2):
            m.c(b, PK, (x + t, 0.05, 6), (1.2, 0.1, 1.4))
    # body: a fluffy torso, a pale chest tuft, a round pompom tail
    bevel(m, "hips", FU, (0, 13.4, -0.6), (11, 4, 9), 1.2)
    bevel(m, "body", FU, (0, 20.4, 0), (11.4, 12, 8.6), 1.4)
    bevel(m, "body", "white_concrete", (0, 19.4, 4.3), (6, 7, 0.8), 0.6)
    bevel(m, "hips", FU, (0, 14, -6.4), (5, 5, 4), 1.2)
    tufts(m, "hips", FU2, [(-1.4, 15.4, -8.4), (1.4, 13, -8.4)], 1.6)
    # a leather strap over one shoulder, a grubby bow and bell at the neck
    m.c("body", "brown_terracotta", (0, 21, 4.5), (1.4, 14, 0.4), (0, 0, 38))
    m.c("body", "brown_terracotta", (0, 21, -4.5), (1.4, 14, 0.4), (0, 0, -38))
    m.c("body", PK, (0, 26.4, 0), (7.4, 1.6, 7))
    for s in (1, -1):
        m.c("body", PK, (2.2 * s, 26.6, 4.2), (2.8, 2, 0.8), (0, 0, 20 * s))
        m.c("body", "magenta_concrete", (2.4 * s, 25.2, 4.2), (0.8, 2.6, 0.4), (0, 0, -12 * s))
    m.c("body", "gold_block", (0, 25.2, 4.3), (1.6, 1.6, 1.6))
    m.c("body", BK, (0, 24.8, 5.15), (0.6, 0.4, 0.1))
    # arms: furry, with pink-padded paws and claws
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8.4 * s
        bevel(m, a, FU, (x, 23.6, 0), (4, 7, 4.4), 0.8)
        bevel(m, a, FU, (x, 17, 0.6), (4, 7, 4.4), 0.8)
        m.c(a, FU2, (x, 13.6, 1.2), (3.6, 2.4, 3.6))
        for t in (-1, 0, 1):
            m.c(a, BK, (x + t * 1.1, 12.2, 2.9), (0.4, 1.2, 0.4))
    # the head: round cheeks, red eyes with a furious brow, a pink nose, two great buck teeth, whiskers
    bevel(m, "head", FU, (0, 32.6, 0.8), (9.6, 8, 8.4), 1.4)
    for s in (1, -1):
        bevel(m, "head", FU, (3.4 * s, 30.4, 3.6), (4, 3.2, 3.2), 0.8)
    paint(m, "head", "front", (0, 34.4, 5.05), ["KKK.KKK", ".KR.RK.", "..R.R.."], {"K": BK, "R": (RD, 0.4, True)}, px=0.95, depth=0.3)
    m.c("head", PK, (0, 31.6, 5.35), (1.6, 1.2, 0.4))
    m.c("head", BK, (0, 30.2, 5.25), (2.6, 0.4, 0.2))
    for s in (1, -1):
        m.c("head", "white_concrete", (0.75 * s, 28.8, 5.2), (1.3, 2.6, 0.6))
        for t in (0, 1):
            m.c("head", FU2, (5.8 * s, 30.6 - t * 0.9, 4.4), (3.4, 0.25, 0.25), (0, 0, (10 - t * 20) * s))
    m.c("head", "red_terracotta", (-3.6, 35.4, 5.1), (0.4, 2.6, 0.2), (0, 0, 30))
    # ears: the left stands tall with a pink inside, the right is torn and flops forward
    m.c("earL", FU, (2.4, 41.6, 0), (2.6, 10, 1.6), (0, 0, -8), (2.4, 36.6, 0))
    m.c("earL", PK, (2.6, 41.8, 0.85), (1.4, 8, 0.2), (0, 0, -8), (2.4, 36.6, 0))
    tip = limb(m, "earR", FU, (-2.4, 36.6, 0), [(5.8, 2.2, (0, 0, 8)), (4.6, 2.2, (115, 0, 8))])
    m.c("earR", PK, (-2.75, 39.4, 1.05), (1.4, 4.4, 0.2), (0, 0, 8), (-2.4, 36.6, 0))
    m.c("earR", "red_terracotta", (tip[0], tip[1], tip[2]), (1.4, 1, 0.8), (115, 0, 8))
    m.c("earR", FU2, (-3.2, 42.4, 0.4), (2.6, 1.2, 2.4), (0, 0, 8))
    # the carrot: a huge root held by its thin tip like a club, widening up to the top, rings drawn on it,
    # the leafy top sprouting out of the end
    m.c("carrot", "orange_concrete", (-8.4, 13, 2), (1.2, 4, 1.2))
    for k in range(5):
        w = 1.6 + k * 0.45
        m.c("carrot", "orange_concrete", (-8.4, 16.6 + k * 3.6, 2), (w, 3.6, w))
        m.c("carrot", "orange_terracotta", (-8.4, 18.2 + k * 3.6, 2), (w + 0.1, 0.3, w + 0.1))
    for k, r in enumerate((-25, 0, 25)):
        m.c("carrot", "green_concrete" if k != 1 else "lime_concrete", (-8.4, 37 + (1 - abs(r) * 0.03), 2), (1, 5, 1), (0, 0, r), (-8.4, 34.6, 2))
    # the egg basket: hanging straight under the fist by its handle, woven brown sides, grass and four
    # painted eggs piled in
    m.c("basket", "brown_terracotta", (8.4, 5, 2), (6.4, 4, 6.4))
    for k in range(3):
        m.c("basket", "oak_planks", (8.4, 3.6 + k * 1.4, 2), (6.6, 0.4, 6.6))
    for s in (1, -1):
        m.c("basket", "brown_terracotta", (8.4 + 2.9 * s, 9.6, 2), (0.6, 5.6, 0.6), (0, 0, 28 * s))
    m.c("basket", "brown_terracotta", (8.4, 12.4, 2), (2.4, 0.6, 0.6))
    m.c("basket", "lime_concrete", (8.4, 7.2, 2), (5.8, 0.6, 5.8))
    for (dx, dz, c, st) in ((-1.4, -1, "pink_concrete", "white_concrete"), (1.4, 1, "light_blue_concrete", "yellow_concrete"), (1.4, -1.6, "yellow_concrete", "magenta_concrete"), (-1.2, 1.6, "lime_concrete", "light_blue_concrete")):
        egg(m, "basket", c, st, (8.4 + dx, 8.6, 2 + dz), (2, 2.6, 2), (0, 0, dx * 6))
    # battle wear: a stitched scar across the chest, fur tufts on the shoulders and cheeks, foot claws
    m.c("body", "red_terracotta", (-2.6, 22.6, 4.45), (4, 0.5, 0.3), (0, 0, -30))
    for k in range(3):
        m.c("body", "black_concrete", (-3.6 + k * 1.1, 22.4 + k * 0.6 - 0.6, 4.6), (0.25, 1.2, 0.2), (0, 0, -30))
    tufts(m, "armR", FU2, [(-10.4, 26.6, 1), (-10.4, 25, -1.4)], 1.8)
    tufts(m, "head", FU2, [(5.6, 30.4, 2.6), (-5.6, 30.4, 2.6)], 1.6)
    for s_, b in ((1, "legL"), (-1, "legR")):
        for t in (-1.4, 0, 1.4):
            m.c(b, "black_concrete", (4 * s_ + t, 0.8, 7.7), (0.5, 0.6, 0.6))
    m.attacks = {"eggs": "double", "carrot": "sweep", "leap": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def cocoa_colossus():
    """A chocolate egg golem: a giant hollow egg with half its gold and purple foil still on, cracked open
    across the chest where a glowing caramel heart shows, arms and legs made of chocolate-bar squares and a
    smaller egg for a head with a jagged crack for a face."""
    m = Model("cocoa_colossus", "biped", 1.7)
    biped(m, hip=12, legx=5, neck=34, shoulder=30, armx=13)
    m.bend = -24
    CH, CH2, CH3, FO, FO2, CA = "brown_concrete", "brown_terracotta", "brown_wool", "gold_block", "purple_concrete", "orange_concrete"
    # legs: chocolate bar blocks stacked, each square scored, foil scrap round one ankle
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 5 * s
        for k, y in enumerate((2, 6.4, 10.4)):
            bevel(m, b, CH, (x, y, 0.4 if k == 0 else 0), (6.4, 4 if k else 4, 6.4 + (1.6 if k == 0 else 0)), 0.5)
            m.c(b, CH2, (x, y + 2.05, 0), (6.6, 0.3, 6.6))
        m.c(b, CH2, (x, 6.4, 3.25), (0.3, 4, 0.3))
    m.c("legL", FO, (5, 2.6, 0.4), (6.8, 1.4, 8.4))
    # the egg body: wide in the middle, narrower at top and bottom
    stack(m, "hips", CH, 0, 11.4, 0, [(12, 2, 10)])
    for y, w, d in ((14.6, 15, 12), (18.4, 17, 14), (22.6, 18, 15), (26.8, 17, 14), (30.4, 14, 12), (33, 10, 9)):
        m.c("body", CH, (0, y, 0), (w, 4.2 if y < 30 else 3, d))
    # foil: the gold wrapper still covers the lower right and the back, torn edges, purple band
    for y, w, d in ((14.6, 15.2, 12.2), (18.4, 17.2, 14.2)):
        m.c("body", FO, (-w / 4, y, 0), (w / 2, 4.3, d))
    hem(m, "body", FO, -8.4, 0, 22.2, 7.1, 0.3, 5, long=3, short=1.2, seed=1)
    m.c("body", FO2, (-4.3, 16.6, 0), (8.8, 1.2, 14.5))
    m.c("body", FO, (0, 24.6, -7.2), (13, 14, 0.4))
    hem(m, "body", FO, -6.5, 6.5, 31.6, -7.4, 0.3, 6, long=2.4, short=0.8, seed=3)
    paint(m, "body", "back", (0, 24, -7.6), ["P...P", ".PPP.", "PPPPP", ".PPP.", "P...P"], {"P": FO2}, px=1.2, depth=0.2)
    # the crack across the chest: jagged broken shell edges round a glowing caramel heart
    m.c("body", CA, (2.4, 23, 6.6), (7, 6, 1.6), light=True)
    m.c("body", "yellow_concrete", (2.4, 23, 7.3), (3.6, 3, 0.6), light=True)
    for (x, y, w, h) in ((-1.6, 25.4, 1.4, 2.6), (0.4, 26.6, 1.4, 1.6), (3, 26.2, 1.6, 2.2), (5.6, 25.8, 1.2, 2.6), (-1.4, 20.4, 1.6, 2.4), (1.4, 19.6, 1.4, 1.6), (4.4, 20, 1.6, 2.4), (6.2, 22, 1, 2.4)):
        m.c("body", CH2, (x, y, 7.7), (w, h, 0.8))
    crack(m, "body", "front", (0, 23, 7.5), [(-7, 3), (-4, 3), (-4, 0), (-2.4, 0)], block=CA, width=0.6)
    # white-chocolate piping: a zigzag band round the top of the egg and dots on the shoulders
    for k in range(9):
        x = -7 + k * 1.75
        if -2 < x < 7.5:
            continue
        m.c("body", "white_concrete", (x, 29.6 + (0.5 if k % 2 else -0.5), 7.05), (1.7, 0.6, 0.3), (0, 0, 35 if k % 2 else -35))
    for k in range(6):
        m.c("body", "white_concrete", (8.55, 29.6 + (0.5 if k % 2 else -0.5), -5 + k * 2), (0.3, 0.6, 2), (35 if k % 2 else -35, 0, 0))
        m.c("body", "white_concrete", (-8.55, 29.6 + (0.5 if k % 2 else -0.5), -5 + k * 2), (0.3, 0.6, 2), (35 if k % 2 else -35, 0, 0))
    for s_, a in ((1, "armL"), (-1, "armR")):
        for t in (-2, 2):
            m.c(a, "white_concrete", (13 * s_ + t, 32.5, 2), (0.8, 0.3, 0.8))
    # drips of melted caramel down the shell
    for x, h in ((1, 4), (4.6, 2.6)):
        m.c("body", CA, (x, 19 - h / 2, 7.4), (1, h, 0.4), light=True)
    # shoulders: chunky chocolate squares; arms made of bar pieces, broken jagged fists
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 13 * s
        bevel(m, a, CH, (x, 29.4, 0), (7, 6, 7), 0.8)
        m.c(a, CH2, (x, 29.4, 3.55), (0.3, 6, 0.3))
        m.c(a, CH2, (x, 29.4, 3.55), (7, 0.3, 0.3))
        for k, y in enumerate((23.4, 18.8)):
            bevel(m, a, CH, (x, y, 0.4), (5.6, 4.4, 5.6), 0.5)
            m.c(a, CH2, (x, y + 2.25, 0.4), (5.8, 0.3, 5.8))
        bevel(m, a, CH, (x, 12.8, 1), (7.4, 7, 7.4), 1)
        for t in (-2, 0, 2):
            m.c(a, CH3, (x + t, 9, 3.4), (1.6, 1.6, 1.6), (45, 0, 0))
        m.c(a, CH2, (x, 12.8, 4.75), (7.4, 0.3, 0.3))
        m.c(a, CH2, (x, 12.8, 4.75), (0.3, 7, 0.3))
    m.c("armR", FO, (-13, 19.6, 0.4), (6, 1.6, 6))
    m.c("armR", FO2, (-13, 20.6, 0.4), (6, 0.6, 6))
    # the head: a small egg with a crack for a face, caramel light inside, a bunny-ear foil bow on top
    for y, w, d in ((35.4, 7, 7), (38.6, 8.4, 8.2), (41.8, 7.4, 7.2), (44.2, 5, 5)):
        m.c("head", CH, (0, y, 0.4), (w, 3.2 if y < 44 else 1.8, d))
    crack(m, "head", "front", (0, 39, 4.6), [(-3, 1.2), (-1.8, 1.2), (-1.8, 0.2), (-0.6, 0.2)], block=CA, width=0.8)
    crack(m, "head", "front", (0, 39, 4.6), [(3, 1.2), (1.8, 1.2), (1.8, 0.2), (0.6, 0.2)], block=CA, width=0.8)
    crack(m, "head", "front", (0, 36.4, 4.6), [(-2.6, 0), (-1.4, 0), (-1.4, -0.8), (0, -0.8), (0, 0), (1.4, 0), (1.4, -0.8), (2.6, -0.8)], block=CA, width=0.6)
    for s in (1, -1):
        m.c("head", FO2, (1.6 * s, 47, 0.4), (1.6, 4, 0.6), (0, 0, -18 * s))
        m.c("head", FO, (1.6 * s, 47.2, 0.75), (0.8, 2.6, 0.2), (0, 0, -18 * s))
    m.c("head", FO, (0, 45.4, 0.4), (1.8, 1.4, 1.8))
    m.attacks = {"slam": "slam", "caramel": "cast", "quake": "stomp", "minions": "roar"}
    m.melee = "swipe"
    return m


# ================================================================================================= HALLOWEEN

@model
def great_gourd():
    """A scarecrow whose pumpkin head came alive: a huge carved jack-o'-lantern lit from inside, a curled
    stem with leaves, a patched burlap shirt stuffed with straw that pokes out at the cuffs and collar, a
    rope belt, a tattered dark coat, a crow on its shoulder and a rusty pitchfork."""
    m = Model("great_gourd", "biped", 1.8)
    biped(m, hip=14, legx=3.8, neck=31, shoulder=29, armx=10)
    m.bone("jaw", "head", (0, 33, 6))
    m.bone("fork", "armR", (-10, 12, 2))
    m.bone("crow", "armL", (10.6, 31.4, 0))
    m.hold = {"fork": 4}
    m.bend = -40
    PU, PU2, BU, BU2, HY, CT, RO = "orange_concrete", "orange_terracotta", "brown_wool", "white_terracotta", "hay_block", "gray_concrete", "yellow_terracotta"
    # legs: burlap trousers tied at the ankle with straw bursting out, old boots
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3.8 * s
        bevel(m, b, "brown_terracotta", (x, 10, 0), (4.6, 8, 4.6), 0.6)
        m.c(b, RO, (x, 6.4, 0), (4.8, 0.8, 4.8))
        tufts(m, b, HY, [(x + 1.4 * s, 5.4, 1.6), (x - 1.2 * s, 5.4, -1.4), (x, 5.2, 2.2)], 1.4)
        bevel(m, b, "dark_oak_planks", (x, 2.2, 0.8), (4.8, 4.4, 6), 0.6)
        m.c(b, "spruce_planks", (x, 0.4, 1), (5, 0.8, 6.4))
    m.c("legL", BU, (4.6, 11, 2.35), (2, 2, 0.2))
    # body: burlap shirt with stitched patches, a rope belt, straw spilling from the collar
    bevel(m, "hips", BU2, (0, 13.4, 0), (10, 3, 6), 0.6)
    bevel(m, "body", BU2, (0, 21.4, 0), (10.6, 13, 6.4), 0.8)
    paint(m, "body", "front", (-2.4, 23.6, 3.25), ["PPP", "P.P", "PPP"], {"P": "green_terracotta"}, px=1.1, depth=0.2)
    paint(m, "body", "front", (2.6, 18.6, 3.25), ["PP", "PP"], {"P": "purple_terracotta"}, px=1.2, depth=0.2)
    for k in range(3):
        m.c("body", "black_concrete", (-3.6 + k * 1.2, 25.4, 3.45), (0.25, 0.8, 0.2))
    m.c("body", RO, (0, 15.8, 0), (10.8, 1.2, 6.6))
    m.c("body", RO, (1.6, 13.8, 3.4), (0.8, 3, 0.8), (0, 0, -10))
    tufts(m, "body", HY, [(-3, 28.6, 2.4), (0, 29, 2.8), (3, 28.6, 2.4), (-3.4, 28.4, -2.4), (3, 28.4, -2.4)], 1.8)
    # the coat: dark, open at the front, tattered tails
    for s in (1, -1):
        m.c("body", CT, (4.4 * s, 21, 0), (2.4, 14, 7.2))
    m.c("body", CT, (0, 21, -3.4), (11.2, 14, 0.8))
    hem(m, "body", CT, -5.6, 5.6, 14, -3.4, 0.8, 6, long=4, short=1.4)
    for s in (1, -1):
        hem(m, "body", CT, -3.4, 3.4, 14, 4.4 * s + 0.6 * s, 2.2, 2, long=3, short=1.4, face_z=False, seed=1 if s > 0 else 3)
    # arms: coat sleeves, straw bursting from the cuffs, stick fingers
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 10 * s
        bevel(m, a, CT, (x, 25.4, 0), (4.4, 8, 4.6), 0.6)
        bevel(m, a, CT, (x, 18, 0.6), (4, 7, 4.4), 0.6)
        tufts(m, a, HY, [(x + 1.4 * s, 13.8, 1.8), (x - 1.2 * s, 13.8, -0.4), (x, 13.4, 2.6)], 1.6)
        for t in (-1, 0, 1):
            m.c(a, "spruce_log", (x + t * 1.1, 11.4, 1.4), (0.7, 3.4, 0.7), (0, 0, t * 12))
    # the pumpkin head: ribbed, carved face lit from inside, stem with a curl and two leaves
    for k, (dx, w) in enumerate(((-4.6, 4), (0, 6), (4.6, 4))):
        bevel(m, "head", PU if k == 1 else PU2, (dx, 36.6, 0.6), (w, 10, 13), 1.4)
    bevel(m, "head", PU, (0, 36.6, 0.6), (15, 9, 11), 1.6)
    m.c("head", "shroomlight", (0, 36.6, 0.6), (12, 7, 10), light=True)
    paint(m, "head", "front", (0, 37.4, 7.15), [
        "KK.....KK",
        "KYK...KYK",
        "KKK...KKK",
        "....K....",
        "K.......K",
        "KYYKYYKYK",
        ".KYYKYYK.",
    ], {"K": "black_concrete", "Y": ("yellow_concrete", 0.4, True)}, px=1.2, depth=0.3)
    m.c("head", "dark_oak_log", (0, 43, 0.6), (2, 3, 2), (0, 0, 10))
    m.c("head", "dark_oak_log", (0.8, 44.8, 0.6), (1.4, 1.4, 2), (0, 0, -30))
    m.c("head", "green_concrete", (-3, 42.2, 2), (4, 0.6, 3), (0, 30, 15))
    m.c("head", "green_terracotta", (3.4, 42, -1.4), (3.4, 0.6, 2.6), (0, -20, -12))
    m.c("head", "green_concrete", (-5.6, 41.4, 3.4), (0.6, 0.6, 3), (30, 0, 0))
    # a crow perched on the left shoulder
    bevel(m, "crow", "black_concrete", (10.6, 33.4, 0), (2.6, 2.4, 4), 0.5)
    m.c("crow", "black_concrete", (10.6, 35.2, 1.4), (2.2, 2.2, 2.2))
    m.c("crow", "gray_concrete", (10.6, 35, 3), (0.8, 0.8, 1.4))
    m.c("crow", "red_concrete", (11.75, 35.6, 1.8), (0.1, 0.5, 0.5), light=True)
    m.c("crow", "black_concrete", (10.6, 33.6, -2.6), (2, 0.6, 2.4), (-20, 0, 0))
    # the pitchfork: a long shaft, a rusty head with three tines
    m.c("fork", "spruce_log", (-10, 18, 2), (1, 30, 1))
    m.c("fork", "iron_block", (-10, 33.4, 2), (5, 1, 1))
    for t in (-2, 0, 2):
        m.c("fork", "iron_block" if t else "raw_iron_block", (-10 + t, 36.6, 2), (0.8, 5.4, 0.8))
    m.c("fork", "orange_terracotta", (-11.6, 33.2, 2.5), (1, 0.8, 0.2))
    # vines creeping out from under the pumpkin and down the chest, two little lanterns on the belt
    for k, (x, y, z, r) in enumerate(((-3.4, 30, 3.4, 20), (-4.2, 27.4, 3.4, -10), (3.6, 29.6, 3.4, -25), (4.4, 26.4, 3.4, 15), (-4.6, 24.4, 3.4, 30))):
        m.c("body", "green_concrete" if k % 2 else "green_terracotta", (x, y, z), (0.7, 3, 0.4), (0, 0, r))
    for (x, y) in ((-4.8, 30.6), (4.6, 30.2), (-3, 25.6)):
        m.c("body", "lime_concrete", (x, y, 3.6), (1.4, 0.8, 0.3), (0, 0, 30))
    for x in (-4, 4):
        bevel(m, "hips", PU, (x, 12.4, 3.8), (2.4, 2.2, 2.4), 0.4)
        m.c("hips", "yellow_concrete", (x, 12.4, 5.05), (1.2, 0.6, 0.1), light=True)
        m.c("hips", RO, (x, 14.2, 3.8), (0.4, 1.4, 0.4))
    m.attacks = {"seeds": "double", "fork": "sweep", "minions": "roar", "fire": "cast"}
    m.melee = "swipe"
    return m


@model
def headless_horseman():
    """A headless rider on a nightmare horse: the horse is black with a bone mask and ribs showing, a mane
    and tail of fire and burning hooves, under a ragged purple caparison with orange trim. The rider wears
    a dark coat with a ruffled collar and a tattered cape; flames rise from his neck, he holds up his own
    carved jack-o'-lantern head in one hand and a long notched sabre in the other."""
    m = Model("headless_horseman", "quad", 1.5)
    quad(m, body_y=21, legx=4.4, legz_front=9, legz_back=-10, neck_y=30, neck_z=11)
    RY = 33
    m.bone("rider", "body", (0, RY, -1))
    m.bone("riderArmR", "rider", (-6, RY + 13, -1))
    m.bone("riderArmL", "rider", (6, RY + 13, -1))
    HB, HB2, BN, FL, FL2, PU, OR, CO = "black_concrete", "polished_blackstone", "bone_block", "orange_concrete", "yellow_concrete", "purple_concrete", "orange_terracotta", "gray_concrete"
    # legs: lean, white bone showing at the knee, hooves wreathed in fire
    for s, (b, z) in ((1, ("legFL", 9)), (-1, ("legFR", 9)), (1, ("legBL", -10)), (-1, ("legBR", -10))):
        x = 4.4 * s
        bevel(m, b, HB, (x, 17, z), (3.8, 7, 4.2), 0.6)
        m.c(b, BN, (x, 13, z + 1.5), (2.2, 1.8, 1.4))
        m.c(b, HB2, (x, 8, z), (2.6, 8, 2.8))
        m.c(b, HB, (x, 3.6, z), (3, 1.6, 3.2))
        m.c(b, FL, (x, 1.4, z + 0.4), (3.6, 2.8, 4), light=True)
        m.c(b, FL2, (x, 3.6, z - 0.8), (1.4, 2, 1.4), (0, 0, 12 * s), light=True)
    # body: a long barrel, deep chest, ribs showing on both flanks
    bevel(m, "body", HB, (0, 24.6, 4.6), (10.4, 10, 12), 2)
    bevel(m, "body", HB, (0, 25, -7), (10, 9.6, 12), 2)
    for z in (0, 3, 6):
        for s in (1, -1):
            m.c("body", BN, (5.25 * s, 23.6, z), (0.4, 5.6, 1))
    # the caparison: a ragged purple blanket over the back with orange trim, the saddle on top
    m.c("body", PU, (0, 29.8, -3), (11, 0.8, 12))
    for s in (1, -1):
        m.c("body", PU, (5.6 * s, 26.6, -3), (0.6, 6, 12))
        hem(m, "body", PU, -9, 3, 23.6, 5.6 * s, 0.6, 5, long=3, short=1.2, face_z=False, seed=2 if s > 0 else 4)
        m.c("body", OR, (5.95 * s, 29.4, -3), (0.3, 0.8, 12))
        paint(m, "body", "left" if s > 0 else "right", (5.9 * s, 26.6, -3), [".O.", "OOO", ".O."], {"O": (OR, 0.2, True)}, px=1.1, depth=0.2)
    m.c("body", "dark_oak_planks", (0, 30.8, -1.6), (6.4, 1.4, 7))
    m.c("body", "dark_oak_planks", (0, 32, 1.8), (4.4, 1.6, 1.2))
    m.c("body", "dark_oak_planks", (0, 31.8, -5), (5.4, 1.2, 1))
    # neck and head: a thick arched neck with a mane of fire, the long horse head held high, a bone mask
    # over the face, burning eyes, flared nostrils, ears laid back, a chain bridle
    bevel(m, "head", HB, (0, 31.4, 11.6), (5.4, 11, 6), 1.0, (-32, 0, 0), (0, 27, 9.4))
    bevel(m, "head", HB, (0, 36.6, 17.4), (5.2, 5.2, 10.6), 1.0, (32, 0, 0), (0, 37.4, 14))
    hx, hy, hz = 0, 36.4, 15
    head_tip = (0, 33.4, 21.4)
    m.c("head", BN, (0, 37.7, 17.4), (5.4, 3.2, 8), (32, 0, 0), (0, 37.4, 14))
    m.c("head", HB2, (0, 33.6, 21.8), (4.4, 2.6, 2.4), (32, 0, 0), (0, 37.4, 14))
    for s in (1, -1):
        m.c("head", "black_concrete", (1.2 * s, 33.4, 23.0), (0.8, 0.8, 0.3), (32, 0, 0), (0, 37.4, 14))
        m.c("head", FL, (2.75 * s, 38.6, 15.4), (0.3, 1.2, 1.8), light=True)
        m.c("head", FL2, (2.85 * s, 38.6, 15.4), (0.2, 0.5, 0.8), light=True)
        m.c("head", HB, (1.6 * s, 41.4, 12.6), (1.4, 3, 1.2), (-35, 0, 10 * s))
        m.c("head", "chain", (2.75 * s, 35.4, 18.4), (0.3, 0.4, 6.4), (32, 0, 0), (0, 37.4, 14))
    for k in range(6):
        y, z = 29 + k * 2.2, 8.6 + k * 1.3
        m.c("head", FL2 if k % 2 else FL, (0, y + 1.4, z - 2.4), (1.4, 3.4 - k * 0.2, 2.2), (-30, 0, 0), light=True)
    bevel(m, "jaw", HB, (0, head_tip[1] - 1.6, head_tip[2] - 3.2), (3.6, 1.6, 5), 0.5, (40, 0, 0), (0, head_tip[1] - 1.6, head_tip[2] - 3.2))
    # tail of fire
    limb(m, "tail", FL, (0, 27, -13), [(5, 2.6, (-140, 0, 0)), (4, 2, (-160, 0, 10), FL2), (3, 1.4, (-175, 0, -10))], light=True)
    # the rider: legs astride in tall boots with stirrups, a dark coat with gold buttons and a purple waistcoat
    for s in (1, -1):
        m.c("rider", CO, (4.4 * s, RY - 0.4, 0.6), (2.6, 3.6, 5), (0, 0, 22 * s))
        m.c("rider", "brown_terracotta", (6.2 * s, RY - 5.4, 1.4), (2.4, 6, 3))
        m.c("rider", "brown_terracotta", (6.2 * s, RY - 8.2, 2.6), (2.4, 1.4, 4))
        m.c("rider", "iron_block", (6.4 * s, RY - 9.2, 2.6), (1.6, 0.4, 3))
    bevel(m, "rider", CO, (0, RY + 6.4, -1), (8.6, 11, 5.4), 0.8)
    m.c("rider", PU, (0, RY + 6, 1.75), (2.4, 9, 0.2))
    for y in (RY + 8.4, RY + 6, RY + 3.6):
        m.c("rider", "gold_block", (-2.4, y, 1.8), (0.6, 0.6, 0.3))
        m.c("rider", "gold_block", (2.4, y, 1.8), (0.6, 0.6, 0.3))
    m.c("rider", "white_concrete", (0, RY + 10.4, 1.85), (2.4, 2.6, 0.6))
    for k in range(3):
        m.c("rider", "white_concrete", (0, RY + 11.2 - k * 1.1, 2.2), (3.4 - k * 0.6, 0.6, 0.4))
    band(m, "rider", "brown_terracotta", (0, RY + 1.4, -1), (8.8, 1.2, 5.6))
    m.c("rider", BN, (0, RY + 1.4, 1.95), (1.6, 1.6, 0.4))
    for s in (1, -1):
        bevel(m, "rider", CO, (5.4 * s, RY + 11.4, -1), (3.6, 2.6, 5.6), 0.6)
        m.c("rider", "gold_block", (5.4 * s, RY + 12.8, -1), (3.4, 0.4, 5.2))
    # the neck: a ragged stump with fire roaring up out of it
    m.c("rider", "black_wool", (0, RY + 12.4, -1), (4, 1.4, 4))
    m.c("rider", "white_concrete", (0, RY + 12.0, 1.1), (4.4, 1.2, 0.4))
    for k, (dx, dz, h) in enumerate(((0, 0, 6), (-1.2, 0.8, 3.8), (1.2, -0.6, 4.2), (0.4, 1, 2.6))):
        m.c("rider", FL2 if k == 0 else FL, (dx, RY + 13 + h / 2, -1 + dz), (1.8 - k * 0.15, h, 1.8 - k * 0.15), (0, k * 30, dx * 6), light=True)
    # the cape: tattered black with a purple lining, hanging back over the horse
    m.c("rider", HB, (0, RY + 4, -4.4), (9, 15, 0.6), (18, 0, 0), (0, RY + 12, -4))
    m.c("rider", PU, (0, RY + 4, -4), (8, 14, 0.2), (18, 0, 0), (0, RY + 12, -4))
    hem(m, "rider", HB, -4.5, 4.5, RY - 2.6, -6.8, 0.6, 5, long=3, short=1.2)
    # arms: the right holds up the sabre, the left holds out the glowing jack-o'-lantern head
    for s, a in ((1, "riderArmL"), (-1, "riderArmR")):
        m.c(a, CO, (6.6 * s, RY + 8.4, -1), (2.8, 9, 3))
        m.c(a, "white_concrete", (6.6 * s, RY + 4.2, -1), (3, 0.8, 3.2))
        m.c(a, HB2, (6.6 * s, RY + 3, -1), (2.4, 1.8, 2.4))
    # his own head, held out by the stem: a real carved pumpkin with ribs, a curling stem, triangle eyes and
    # a jagged grin with the fire inside shining through
    PX, PY, PZ = 7, RY - 2.4, 0.6
    bevel(m, "riderArmL", FL, (PX, PY, PZ), (6, 5.6, 6), 1.0)
    for dx in (-1.6, 1.6):
        m.c("riderArmL", OR, (PX + dx, PY, PZ), (0.5, 5.7, 6.1))
    m.c("riderArmL", "green_terracotta", (PX, PY + 3.4, PZ), (1, 1.6, 1))
    m.c("riderArmL", "green_terracotta", (PX + 0.6, PY + 4.2, PZ), (1.4, 0.6, 0.6))
    paint(m, "riderArmL", "front", (PX, PY - 0.2, PZ + 3.05), [
        "......",
        ".K..K.",
        "KK..KK",
        "......",
        "KKKKKK",
        ".K.K.K",
    ], {"K": (FL2, 0.3, True)}, px=0.95, depth=0.3)
    m.c("riderArmL", "shroomlight", (PX, PY, PZ), (4.4, 3.4, 4.4), light=True)
    m.c("riderArmR", HB2, (-6.6, RY + 1.2, -1), (0.8, 2.6, 0.8))
    m.c("riderArmR", "gold_block", (-6.6, RY + 2.6, -1), (1.2, 0.8, 3))
    m.c("riderArmR", "iron_block", (-6.6, RY - 7, 0.2), (0.6, 16, 2), (-8, 0, 0))
    m.c("riderArmR", FL, (-6.6, RY - 7, 1.25), (0.7, 14, 0.3), (-8, 0, 0), light=True)
    for k in range(3):
        m.c("riderArmR", HB, (-6.6, RY - 4 - k * 3.4, -0.85), (0.7, 0.8, 0.4), (-8, 0, 0))
    m.rest("riderArmR", (-120, 0, 0))
    m.attacks = {"charge": "charge", "fire": "rear", "minions": "howl", "heads": "toss"}
    m.melee = "bite"
    return m


@model
def hexmother():
    """A crone of a witch: green warty skin, a long hooked nose, wild grey hair, a tall bent hat with a
    buckle and a spider web, a ragged purple dress with potion bottles on the belt, a black cat riding her
    shoulder and a gnarled staff topped with a skull and a bubbling green cauldron-fire."""
    m = Model("hexmother", "biped", 1.8)
    biped(m, hip=13, legx=3, neck=31, shoulder=29, armx=8)
    m.bone("jaw", "head", (0, 32, 4))
    m.bone("hat", "head", (0, 39.6, 0.4))
    m.bone("staff", "armR", (-8, 11, 2))
    m.hold = {"staff": 0}
    m.bend = -50
    m.rest("body", (-10, 0, 0))
    m.rest("head", (12, 0, 0))
    SK, SK2, DR, DR2, BK, HA, GL = "lime_terracotta", "green_terracotta", "purple_concrete", "black_wool", "black_concrete", "light_gray_wool", "lime_concrete"
    # pointed black boots peeping out under a long dress with a torn hem
    for s, b in ((1, "legL"), (-1, "legR")):
        x = 3 * s
        m.c(b, BK, (x, 1.2, 1.4), (3, 2.4, 5))
        m.c(b, BK, (x, 1.8, 4.6), (1.6, 1.4, 2), (-30, 0, 0))
        m.c(b, "gray_concrete", (x, 2.6, 0.6), (3.2, 0.6, 3.2))
    stack(m, "hips", DR, 0, 1.8, 0, [(13, 3, 10), (12, 3, 9.4), (11, 3, 8.6), (10, 3, 8)])
    hem(m, "hips", DR, -6.5, 6.5, 2.2, 5.1, 0.6, 8, long=2.2, short=0.8)
    hem(m, "hips", DR2, -6, 6, 2, -5.1, 0.6, 6, long=2, short=0.8, seed=2)
    for (x, y) in ((-3, 6), (3.6, 8.6), (-1, 10.4)):
        m.c("hips", DR2, (x, y, 4.75), (2, 2, 0.3))
    # belt of potions: a rope belt with four glowing bottles of different brews
    band(m, "hips", "brown_terracotta", (0, 13.4, 0), (10.4, 1.2, 8.4))
    for x, c in ((-4, "magenta_stained_glass"), (-1.4, "lime_stained_glass"), (1.4, "orange_stained_glass"), (4, "light_blue_stained_glass")):
        m.c("hips", c, (x, 11.6, 4.6), (1.6, 2.4, 1.6), light=True)
        m.c("hips", "brown_terracotta", (x, 13.2, 4.6), (0.8, 0.6, 0.8))
    # body: a lace-up bodice and a ragged black shawl
    bevel(m, "body", DR, (0, 20.6, 0), (9.6, 11, 6.4), 0.8)
    for k in range(4):
        m.c("body", BK, (0, 17 + k * 2, 3.3), (2.4, 0.4, 0.2), (0, 0, 30 if k % 2 else -30))
    m.c("body", BK, (0, 27, 0), (11.4, 3, 7.6))
    hem(m, "body", BK, -5.6, 5.6, 25.6, 3.9, 0.4, 5, long=2.4, short=1)
    hem(m, "body", BK, -5.6, 5.6, 25.6, -3.9, 0.4, 5, long=3, short=1, seed=3)
    # arms: bony green arms in ragged sleeves, long nails
    for s, a in ((1, "armL"), (-1, "armR")):
        x = 8 * s
        bevel(m, a, DR, (x, 24.4, 0), (3.6, 8, 4), 0.5)
        hem(m, a, DR2, x - 1.8, x + 1.8, 20.6, 2.1, 0.4, 3, long=2.4, short=1, seed=1)
        m.c(a, SK, (x, 16.6, 0.6), (2.2, 7, 2.2))
        m.c(a, SK, (x, 12.6, 1), (2.6, 2.4, 2.6))
        for t in (-0.8, 0, 0.8):
            m.c(a, BK, (x + t, 10.8, 1.8), (0.4, 1.4, 0.4))
    # the face: a long hooked nose with a wart, sunken glowing eyes, a crooked grin with one tooth, a chin
    bevel(m, "head", SK, (0, 35.2, 0.6), (7.6, 8, 7.6), 1)
    paint(m, "head", "front", (0, 36.6, 4.45), ["KK...KK", ".GK.KG.", "......."], {"K": BK, "G": (GL, 0.4, True)}, px=0.9, depth=0.3)
    m.c("head", SK, (0, 35.4, 5.6), (1.6, 2, 2.4))
    m.c("head", SK, (0, 34.2, 7.4), (1.2, 2, 1.6), (40, 0, 0))
    m.c("head", SK2, (0.7, 35.6, 6.4), (0.6, 0.6, 0.6))
    m.c("jaw", SK, (0, 31.6, 3.6), (4, 2, 3))
    m.c("jaw", SK, (0, 31, 5.2), (1.6, 1.4, 1.4))
    m.c("head", BK, (0, 32.8, 4.45), (3.6, 0.6, 0.2))
    m.c("head", "white_terracotta", (0.8, 32.6, 4.6), (0.6, 0.8, 0.2))
    # wild grey hair hanging out under the hat on both sides and down the back
    for s in (1, -1):
        for k in range(3):
            m.c("head", HA, (4.2 * s, 35 - k * 2.4, -0.6 + k * 0.4), (1.4, 3.6, 4.6 - k), (0, 0, (8 + k * 6) * s))
    m.c("head", HA, (0, 33.6, -3.6), (7.6, 9, 1.4))
    hem(m, "head", HA, -3.8, 3.8, 29.4, -3.6, 1.2, 4, long=2.2, short=0.8)
    # the hat: a wide floppy brim, a tall cone that bends and kinks, a buckle band and a cobweb
    m.c("hat", BK, (0, 39.8, 0.4), (14, 0.8, 13))
    m.c("hat", BK, (0, 40.2, 0.4), (11, 0.8, 10))
    stack(m, "hat", BK, 0, 40.4, 0.4, [(8, 3, 8), (6.4, 3, 6.4)])
    m.c("hat", "purple_concrete", (0, 41.4, 0.4), (8.2, 1.2, 8.2))
    m.c("hat", "gold_block", (0, 41.4, 4.5), (2, 1.6, 0.3))
    m.c("hat", BK, (0, 41.4, 4.7), (1, 0.8, 0.2))
    m.c("hat", BK, (-0.6, 48, -0.6), (4.6, 4, 4.6), (-14, 0, 10), (0, 46.4, 0.4))
    m.c("hat", BK, (-2, 51, -2.4), (3, 3.4, 3), (-34, 0, 24), (-1, 49.6, -1.4))
    m.c("hat", BK, (-3.6, 52.6, -4.6), (1.8, 2.6, 1.8), (-70, 0, 34), (-3, 52, -3.8))
    m.c("hat", "white_stained_glass", (3.8, 43, 3.2), (0.2, 3, 3), (0, 45, 0))
    m.c("hat", "white_concrete", (3.6, 43.6, 3.2), (0.2, 0.2, 2.6), (0, 45, 30))
    m.c("hat", BK, (3.9, 42.6, 3.3), (0.6, 0.6, 0.6))
    # the black cat on her shoulder, green eyes, curled tail
    bevel(m, "armL", BK, (8.6, 31, -0.6), (3.4, 2.6, 5), 0.6)
    m.c("armL", BK, (8.6, 33, 2.2), (3, 2.6, 2.4))
    for s in (1, -1):
        m.c("armL", BK, (8.6 + 0.9 * s, 34.6, 2.2), (0.8, 1, 0.8))
        m.c("armL", GL, (8.6 + 0.7 * s, 33.3, 3.45), (0.6, 0.6, 0.1), light=True)
    m.c("armL", BK, (8.6, 33, -3.6), (0.8, 4, 0.8), (-30, 0, 0))
    # the staff: twisted wood, a skull on top with green fire in its eyes and a hanging charm
    for k in range(4):
        m.c("staff", "dark_oak_log", (-8 + (0.4 if k % 2 else -0.4), 4 + k * 7, 2), (1.2, 7.4, 1.2), (0, 0, 6 if k % 2 else -6))
    bevel(m, "staff", "bone_block", (-8, 33.6, 2), (3.4, 3.4, 3.4), 0.6)
    m.c("staff", BK, (-8.7, 34, 3.75), (0.8, 0.8, 0.1))
    m.c("staff", BK, (-7.3, 34, 3.75), (0.8, 0.8, 0.1))
    m.c("staff", GL, (-8, 36.4, 2), (1.6, 2.4, 1.6), light=True)
    m.c("staff", "lime_stained_glass", (-8, 37.6, 2), (2.6, 3.6, 2.6), light=True)
    m.c("staff", "brown_terracotta", (-9.6, 29, 2), (0.3, 3, 0.3))
    m.c("staff", "bone_block", (-9.6, 27.2, 2), (0.8, 1.2, 0.6))
    # a small iron cauldron strapped to her back, green brew bubbling over the rim
    bevel(m, "body", "polished_blackstone", (0, 20, -6.4), (6, 5, 5), 0.8)
    m.c("body", "polished_blackstone", (0, 22.8, -6.4), (6.6, 0.8, 5.6))
    m.c("body", GL, (0, 23, -6.4), (5, 0.6, 4), light=True)
    for (x, z, w) in ((-1.4, -6, 1.2), (1.2, -7, 1), (0.4, -5.4, 0.8)):
        m.c("body", "lime_stained_glass", (x, 24 + w, z), (w, w, w), light=True)
    m.c("body", "lime_stained_glass", (2.6, 21.4, -4.0), (0.8, 2.4, 0.6), light=True)
    for s_ in (1, -1):
        m.c("body", "brown_terracotta", (3.4 * s_, 22.6, -1.2), (0.6, 0.6, 9), (-20, 0, 0))
    # a bat circling the bent tip of the hat
    m.c("hat", BK, (-6, 50.4, -4.4), (1.2, 1.2, 1.6))
    for s_ in (1, -1):
        m.c("hat", BK, (-6 + 1.6 * s_, 50.8, -4.4), (2, 0.3, 1.4), (0, 0, 25 * s_))
    m.attacks = {"hex": "cast", "potions": "double", "minions": "roar", "blink": "cast"}
    m.melee = "swipe"
    return m
