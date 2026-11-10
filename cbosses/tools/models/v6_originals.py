"""v6: original bosses. None of these copy a vanilla mob: each is its own creature with one big idea,
drawn as painted boxes on a code-drawn Sheet."""
import math
from models import model, biped, quad
from build import Model
from texpaint import paintbox, Sheet

SPAWN, DEATH = {}, {}


def pb(m, s, bone, uv, lo, lit=(), **kw):
    """Paint a Sheet box. Sheet pictures are clean, so no smoothing or despeckle."""
    kw.setdefault("passes", 0)
    return paintbox(m, bone, s.img, uv, lo, s.sizes[uv], allowed=sorted(s.used), lit=lit, **kw)


def disc(cx, cy, w, h, layers):
    """A w x h picture of rings around (cx, cy): layers is [(radius, key)], smallest radius first."""
    rows = []
    for y in range(h):
        r = ""
        for x in range(w):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            k = "."
            for rad, key in layers:
                if d < rad:
                    k = key
                    break
            r += k
        rows.append(r)
    return rows


def gear(cx, cy, w, h, r_in, r_out, teeth, key, hub=None, hub_r=1.2, hole="."):
    """A gear picture: a toothed ring between r_in and r_out with a hub in the middle."""
    rows = []
    for y in range(h):
        r = ""
        for x in range(w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            tooth = math.cos(a * teeth) > 0.2
            k = "."
            if hub and d < hub_r: k = hub
            elif d < r_in - 1.2: k = hole if (abs(dx) > 0.9 and abs(dy) > 0.9) else key
            elif d < r_in: k = key
            elif d < r_out and tooth: k = key
            r += k
        rows.append(r)
    return rows


@model
def clockwork_colossus():
    """A copper and iron giant wound up by a great key in its back. Its chest is a round window onto a
    turning gold gear with a glowing core; its eyes are lit slits in an iron helm with a steam whistle on
    top, and twin exhaust stacks rise behind its shoulders."""
    m = Model("clockwork_colossus", "biped", 2.4)
    biped(m, hip=13, legx=3.8, neck=29, shoulder=27, armx=11.5)
    m.bone("key", "body", (0, 22, -5))
    CU, CT, EX, AU, FE, BK, GR, GL = ("copper_block", "cut_copper", "exposed_copper", "gold_block", "iron_block",
                                      "black_concrete", "gray_concrete", "orange_concrete")
    K = {"c": CT, "e": EX, "g": AU, "f": FE, "k": BK, "r": GR, "o": GL, "y": "yellow_concrete", "u": CU}
    s = Sheet(256, 256)

    # chest: a round window onto a gold gear with a glowing core
    chest = s.box(16, 13, 10, CU, shade=CT, top=CT)
    for x, y in ((1, 1), (14, 1), (1, 11), (14, 11)):
        s.draw(chest, "front", x, y, ["g"], K)
    s.draw(chest, "front", 0, 0, ["cccccccccccccccc"], K)
    for f in ("left", "right"):
        s.draw(chest, f, 0, 0, ["cccccccccc", "..........", "g...cc...g", "....cc....", "....cc....",
                                "....cc....", "....cc....", "....cc....", "....cc....", "g...cc...g", "....cc....",
                                "eeeeeeeeee", "cccccccccc"], K)
    s.draw(chest, "back", 0, 0, ["cccccccccccccccc", ".g............g.", "....rrrrrrrr....", "....rkkkkkkr....",
                                 "....rrrrrrrr....", "................", ".....eeeeee.....", ".g............g."], K)
    pb(m, s, "body", chest, (-8, 16, -5), lit={GL})
    # the window: octagons made of two squares turned 45 degrees, a gear of crossed bars over a black hole
    cy, fz = 22.5, 5
    for a in (0, 45):
        m.c("body", AU, (0, cy, fz + 0.1), (10.4, 10.4, 0.3), (0, 0, a))
        m.c("body", BK, (0, cy, fz + 0.2), (8.6, 8.6, 0.3), (0, 0, a))
    for a in (0, 30, 60, 90, 120, 150):
        m.c("body", AU, (0, cy, fz + 0.4), (7.8, 1.3, 0.3), (0, 0, a))
    for a in (0, 45):
        m.c("body", AU, (0, cy, fz + 0.5), (4.6, 4.6, 0.3), (0, 0, a))
        m.c("body", BK, (0, cy, fz + 0.6), (2.8, 2.8, 0.3), (0, 0, a))
    m.c("body", GL, (0, cy, fz + 0.7), (1.6, 1.6, 0.3), (0, 0, 45), light=True)

    # waist: a dark gear belt
    waist = s.box(12, 3, 8, GR)
    for f in ("front", "back", "left", "right"):
        s.draw(waist, f, 0, 1, ["ffffffffffff"], K)
    pb(m, s, "body", waist, (-6, 13, -4))

    # helm: iron with lit eye slits, a riveted brow and a speaker grille
    helm = s.box(9, 8, 9, FE, shade=GR, top=FE)
    s.draw(helm, "front", 0, 0, ["ccccccccc", ".........", ".kkk.kkk.", ".kyy.yyk.", ".kkk.kkk.",
                                 ".........", "..rkrkr..", "..rkrkr.."], K)
    for f in ("left", "right"):
        s.draw(helm, f, 0, 0, ["ccccccccc", ".........", "...ggg...", "..g.k.g..", "...ggg..."], K)
    s.draw(helm, "back", 0, 0, ["ccccccccc"], K)
    pb(m, s, "head", helm, (-4.5, 29, -4.5), lit={"yellow_concrete"})
    # steam whistle
    m.c("head", CU, (0, 38.2, -1), (2, 2.4, 2))
    m.c("head", AU, (0, 39.8, -1), (2.6, 0.8, 2.6))

    # shoulders: round copper pauldrons with a gold rim and a gear on top
    for side, arm in ((1, "armL"), (-1, "armR")):
        pd = s.box(7, 5, 8, CU, top=CU)
        for f in ("front", "back"):
            s.draw(pd, f, 0, 0, ["ggggggg", ".......", ".......", ".......", "eeeeeee"], K)
        for f in ("left", "right"):
            s.draw(pd, f, 0, 0, ["gggggggg", "........", "........", "........", "eeeeeeee"], K)
        pb(m, s, arm, pd, (side * 11.5 - 3.5, 25, -4))
        m.c(arm, AU, (side * 11.5, 30.4, 0), (3.2, 0.8, 3.2), (0, 0, 0))
        m.c(arm, AU, (side * 11.5, 30.4, 0), (3.2, 0.8, 3.2), (0, 45, 0))
        # upper arm, elbow joint, forearm
        up = s.box(5, 7, 5, CU, shade=CT)
        pb(m, s, arm, up, (side * 11.5 - 2.5, 18, -2.5))
        m.c(arm, GR, (side * 11.5, 17.5, 0), (5.6, 1.6, 5.6))
        m.c(arm, AU, (side * 11.5 + side * 2.9, 17.5, 0), (0.4, 2.4, 2.4))
        fa = s.box(6, 7, 6, CU, shade=EX, top=CT)
        for f in ("front", "back", "left", "right"):
            s.draw(fa, f, 0, 0, ["cccccc", "......", "......", "......", "......", "eeeeee", "cccccc"], K)
        pb(m, s, arm, fa, (side * 11.5 - 3, 10, -3))
        # iron clamp hand: palm and three fingers
        hand = s.box(5, 3, 5, FE, shade=GR)
        pb(m, s, arm, hand, (side * 11.5 - 2.5, 7, -2.5))
        for dz in (-1.6, 0, 1.6):
            m.c(arm, FE, (side * 11.5, 5.6, dz), (1.6, 2.8, 1.2))
        m.c(arm, FE, (side * 11.5 - side * 2, 6, 0), (1.2, 2.4, 1.6))

    # legs: copper with a piston in front of the knee, iron boots
    for side, leg in ((1, "legL"), (-1, "legR")):
        x = side * 3.8
        lg = s.box(5, 10, 5, CU, shade=CT)
        for f in ("left", "right", "back"):
            s.draw(lg, f, 0, 0, ["ccccc", ".....", ".....", ".....", ".....", "rrrrr"], K)
        s.draw(lg, "front", 0, 0, ["ccccc", ".....", ".....", ".....", ".....", "rrrrr"], K)
        pb(m, s, leg, lg, (x - 2.5, 3, -2.5))
        m.c(leg, FE, (x, 8, 2.9), (1.2, 7, 0.8))
        m.c(leg, GR, (x, 11.5, 2.9), (2, 1.2, 1.2))
        bt = s.box(6, 3, 8, FE, shade=GR, top=FE)
        s.draw(bt, "front", 0, 0, ["cccccc", ".g..g.", "rrrrrr"], K)
        for f in ("left", "right"):
            s.draw(bt, f, 0, 0, ["cccccccc", "........", "rrrrrrrr"], K)
        pb(m, s, leg, bt, (x - 3, 0, -3))

    # the wind-up key in the back
    m.c("key", AU, (0, 22, -6.6), (1.6, 1.6, 3.2))
    m.c("key", AU, (0, 22, -8.6), (1.2, 7, 1.2))
    for sgn in (1, -1):
        cy = 22 + sgn * 2.6
        m.c("key", AU, (0, cy + sgn * 1.6, -8.6), (1.2, 0.8, 4.4))
        m.c("key", AU, (0, cy, -8.6 - 1.8), (1.2, 4, 0.8))
        m.c("key", AU, (0, cy, -8.6 + 1.8), (1.2, 4, 0.8))
    # twin exhaust stacks behind the shoulders
    for x in (-4.5, 4.5):
        m.c("body", CU, (x, 31, -4.2), (2.2, 8, 2.2))
        m.c("body", EX, (x, 35.4, -4.2), (3, 1, 3))
        m.c("body", BK, (x, 35.95, -4.2), (1.6, 0.1, 1.6))
    m.hold = {}
    m.attacks = {"slam": "slam", "spin": "sweep", "steam": "roar", "charge": "lunge"}
    m.melee = "swipe"
    return m


@model
def lanternmaw():
    """A gaunt black stalker on four stilt legs. Where its head should be hangs a huge iron lantern
    cage, and inside it burns a soul flame with a face. The cage's floor is its jaw; a little lantern
    swings on the end of its chain tail."""
    from models import limb
    m = Model("lanternmaw", "quad", 2.1)
    quad(m, body_y=27, legx=5, legz_front=6, legz_back=-8, neck_y=36, neck_z=14)
    BK, DS, GR, CY, LB, WH, AU = ("black_concrete", "polished_deepslate", "gray_concrete", "cyan_concrete",
                                  "light_blue_concrete", "white_concrete", "gold_block")
    K = {"k": BK, "d": DS, "g": GR, "c": CY, "l": LB, "w": WH}
    s = Sheet(128, 128)
    # body: a lean ribbed torso
    body = s.box(9, 7, 18, BK, shade=DS, top=DS)
    for f in ("left", "right"):
        s.draw(body, f, 0, 0, ["..................", "...g..g..g..g.....", "...g..g..g..g.....", "...g..g..g..g....."], K)
    pb(m, s, "body", body, (-4.5, 24, -10))
    for k, z in enumerate((5, 1, -3, -7)):
        m.c("body", DS, (0, 31.6, z), (1.6, 2.2, 1.6), (-20, 0, 0))
    # stilt legs with a knee knob and splayed claws
    for leg, x, z in (("legFL", 5, 6), ("legFR", -5, 6), ("legBL", 5, -8), ("legBR", -5, -8)):
        sx = 1 if x > 0 else -1
        tip = limb(m, leg, BK, (x, 25, z), [(13, 2.2, (0, 0, 180 + sx * 14)), (13, 1.8, (0, 0, 180 - sx * 14))], joint=DS)
        for a in (-35, 0, 35):
            m.c(leg, DS, (tip[0] + sx * 0.2, 0.4, tip[2]), (1, 0.8, 3.4), (0, a, 0), (tip[0], 0.4, tip[2]))
    # neck
    limb(m, "body", BK, (0, 28, 7), [(6, 3, (40, 0, 0)), (5, 2.6, (15, 0, 0))])
    # the lantern cage: corner posts, a band round the middle, a stepped roof with a ring
    hx, hy, hz = 0, 38, 15
    w, h = 12, 13
    for x in (-w / 2, w / 2):
        for z in (hz - w / 2, hz + w / 2):
            m.c("head", BK, (x, hy + h / 2, z), (1.4, h, 1.4))
    for y in (hy + 0.5, hy + h * 0.55):
        for z in (hz - w / 2, hz + w / 2):
            m.c("head", BK, (0, y, z), (w, 1, 1))
        for x in (-w / 2, w / 2):
            m.c("head", BK, (x, y, hz), (1, 1, w))
    for x in (-2, 2):
        for z in (hz - w / 2, hz + w / 2):
            m.c("head", DS, (x, hy + h / 2, z), (0.6, h, 0.6))
        m.c("head", DS, (w / 2, hy + h / 2, hz + x), (0.6, h, 0.6))
        m.c("head", DS, (-w / 2, hy + h / 2, hz + x), (0.6, h, 0.6))
    roof = s.box(14, 2, 14, BK, shade=DS)
    pb(m, s, "head", roof, (-7, hy + h, hz - 7))
    m.c("head", BK, (0, hy + h + 2.8, hz), (9, 1.6, 9))
    m.c("head", DS, (0, hy + h + 4.2, hz), (4, 1.2, 4))
    for a in (0, 90):
        m.c("head", GR, (0, hy + h + 6.6, hz), (4, 0.8, 0.8), (0, a, 0))
        m.c("head", GR, (0, hy + h + 5.8, hz), (0.8, 2, 0.8))
    m.c("head", GR, (0, hy + h + 7.4, hz), (4, 0.8, 0.8), (0, 0, 0))
    for x in (-2, 2):
        m.c("head", GR, (x, hy + h + 6.6, hz), (0.8, 2.4, 0.8))
    # the soul flame with a face
    fl = s.box(7, 6, 7, CY, top=LB)
    s.draw(fl, "front", 0, 0, [".......", ".kk.kk.", ".kw.kw.", ".......", "..kkk..", "......."], K)
    pb(m, s, "head", fl, (-3.5, hy + 2, hz - 3.5), lit={CY, LB, WH})
    m.c("head", LB, (0, hy + 9.5, hz - 0.5), (4.4, 3, 4.4), light=True)
    m.c("head", WH, (0.4, hy + 11.6, hz - 0.8), (2, 1.8, 2), light=True)
    # jaw: the cage floor with iron teeth
    m.c("jaw", BK, (0, hy - 0.4, hz), (w + 1.4, 1.2, w + 1.4))
    for x in (-4.5, -1.5, 1.5, 4.5):
        m.c("jaw", GR, (x, hy - 1.8, hz + w / 2 + 0.2), (1, 2, 1))
    # chain tail with a little lantern
    tip = limb(m, "tail", BK, (0, 30, -10), [(5, 1.4, (-120, 0, 0)), (5, 1.2, (-150, 0, 0)), (4, 1, (-175, 0, 0))], joint=DS)
    m.c("tail", BK, (tip[0], tip[1] - 1.6, tip[2]), (3, 3.2, 3))
    m.c("tail", CY, (tip[0], tip[1] - 1.6, tip[2]), (3.2, 1.8, 2), light=True)
    m.c("tail", CY, (tip[0], tip[1] - 1.6, tip[2]), (2, 1.8, 3.2), light=True)
    m.attacks = {"fire": "roar", "pounce": "charge", "slam": "rear", "sweep": "toss"}
    m.melee = "bite"
    return m


@model
def mossback():
    """An old tortoise the size of a house that has slept so long a ruined watchtower and a tree grew on
    its shell. Its shell is ringed with dark scutes, moss spills over the rim, and its wrinkled head peers
    out with tired yellow eyes."""
    m = Model("mossback", "quad", 2.2)
    quad(m, body_y=10, legx=9, legz_front=9, legz_back=-9, neck_y=10, neck_z=15)
    BR, DB, GT, MO, LG, YT, SB, MS, CB, BK = ("brown_terracotta", "black_terracotta", "green_terracotta", "moss_block",
                                              "lime_terracotta", "yellow_terracotta", "stone_bricks", "mossy_stone_bricks",
                                              "cracked_stone_bricks", "black_concrete")
    K = {"b": BR, "d": DB, "g": GT, "m": MO, "l": LG, "y": YT, "k": BK, "w": "white_concrete", "o": "orange_terracotta"}
    s = Sheet(256, 256)
    # shell: three stepped rings, each with scute seams and moss on the upper edge
    rim = s.box(26, 4, 30, BR, top=GT)
    for f, n in (("front", 26), ("back", 26), ("left", 30), ("right", 30)):
        s.draw(rim, f, 0, 0, ["".join("d" if i % 6 == 0 else "m" if (i * 7) % 5 == 0 else "." for i in range(n)),
                              "".join("d" if i % 6 == 0 else "." for i in range(n)),
                              "".join("d" if i % 6 == 0 else "." for i in range(n)), "d" * n], K)
    pb(m, s, "body", rim, (-13, 7, -15))
    mid = s.box(22, 5, 26, BR, top=MO)
    for f, n in (("front", 22), ("back", 22), ("left", 26), ("right", 26)):
        s.draw(mid, f, 0, 0, ["m" * n, "".join("m" if (i * 3) % 4 == 0 else "d" if i % 7 == 3 else "." for i in range(n)),
                              "".join("d" if i % 7 == 3 else "." for i in range(n)),
                              "".join("d" if i % 7 == 3 else "." for i in range(n)), "d" * n], K)
    pb(m, s, "body", mid, (-11, 11, -13))
    top = s.box(16, 3, 20, MO, top=MO)
    for f, n in (("front", 16), ("back", 16), ("left", 20), ("right", 20)):
        s.draw(top, f, 0, 0, ["l" * n, "".join("l" if i % 3 else "." for i in range(n)), "g" * n], K)
    s.draw(top, "top", 0, 0, ["................", "..l....g....l...", "......l.........", ".g.........l....",
                              "....l...g.......", "..........l...g.", "..g..l..........", "........g...l...",
                              "...l............", ".......l....g...", ".g.....g........", "....l......l....",
                              "............g...", "..l..g...l......", ".........l......", ".g..........l...",
                              ".....l..g.......", "..........l.....", "...g...l.....g..", "................"], K)
    pb(m, s, "body", top, (-8, 16, -10))
    # belly plate
    m.c("body", YT, (0, 6.6, 0), (24, 1.2, 28))
    # the ruined watchtower
    tw = s.box(7, 11, 7, SB)
    for f in ("front", "back", "left", "right"):
        s.draw(tw, f, 0, 0, [".......", ".......", "...k...", "...k...", ".......", "..m....", ".......",
                             "....k..", ".......", ".mm....", "mmmmmmm"], K)
    pb(m, s, "body", tw, (-1, 19, -6))
    for x, z in ((-1, -6), (4.6, -6), (-1, -0.4), (4.6, -0.4)):
        m.c("body", MS, (x + 0.7, 30.7, z + 0.7), (1.4, 1.4, 1.4))
    m.c("body", CB, (2.5, 30.2, -2.5), (7.2, 0.4, 7.2))
    m.c("body", "dark_oak_planks", (2.5, 31.6, -2.5), (0.8, 3, 0.8), (0, 0, 14))
    # a small tree on the front of the shell
    m.c("body", "oak_log", (-4, 21.5, 5), (1.6, 5, 1.6))
    m.c("body", "azalea_leaves", (-4, 25.5, 5), (6, 3.4, 6))
    m.c("body", "flowering_azalea_leaves", (-4, 27.6, 5), (3.6, 1.8, 3.6))
    # moss hanging over the rim
    for x, z, h in ((-12.6, 6, 3), (-12.6, -5, 2), (12.6, 2, 3.4), (12.6, -9, 2), (6, 14.6, 2.6), (-7, -14.6, 2.2)):
        sx, sz = (0.5, 3) if abs(x) > 12 else (3, 0.5)
        m.c("body", MO, (x, 7 - h / 2 + 0.6, z), (sx, h, sz))
    # head: wrinkled, a dark beak and tired yellow eyes
    hd = s.box(8, 7, 9, GT, shade=DB, top=GT)
    s.draw(hd, "front", 0, 0, ["........", ".l....l.", "........", "........", "...dd...", "..dddd..", "........"], K)
    for f in ("left", "right"):
        s.draw(hd, f, 0, 0, [".........", ".........", "...wyk...", "...ddd...", ".l..l..l.", "dddddd...", "........."], K)
    pb(m, s, "head", hd, (-4, 8, 16))
    nk = s.box(6, 5, 6, GT)
    s.draw(nk, "left", 0, 0, ["......", ".l..l.", "......", "l..l..", "......"], K)
    s.draw(nk, "right", 0, 0, ["......", ".l..l.", "......", "l..l..", "......"], K)
    pb(m, s, "body", nk, (-3, 8, 12))
    # stubby legs with pale claws
    for leg, x, z in (("legFL", 9, 9), ("legFR", -9, 9), ("legBL", 9, -9), ("legBR", -9, -9)):
        lg = s.box(6, 8, 6, GT, shade=DB)
        for f in ("front", "back", "left", "right"):
            s.draw(lg, f, 0, 0, ["......", ".l..l.", "......", "l..l..", "......", ".l..l."], K)
        pb(m, s, leg, lg, (x - 3, 0, z - 3))
        for dx in (-1.8, 0, 1.8):
            m.c(leg, "white_terracotta", (x + dx, 0.5, z + 3.3), (1, 1, 1))
    m.c("tail", GT, (0, 6, -16.5), (3, 2.4, 4), (-15, 0, 0))
    m.attacks = {"slam": "rear", "spin": "charge", "quake": "howl", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def prismheart():
    """A golem grown out of a geode. Its body is amethyst armoured in faceted plates, a pink heart gem
    burns in its open chest, crystal spires burst from its shoulders and back, and its fists are raw
    crystal clusters. Shards float around it."""
    m = Model("prismheart", "biped", 2.5)
    biped(m, hip=11, legx=4.5, neck=27, shoulder=25, armx=12)
    AM, PU, PT, MT, MG, BK, PK, WH = ("amethyst_block", "purple_concrete", "purple_terracotta", "magenta_terracotta",
                                      "magenta_concrete", "black_concrete", "pink_concrete", "white_concrete")
    K = {"p": PU, "t": PT, "m": MT, "g": MG, "k": BK, "i": PK, "w": WH, "a": AM}
    s = Sheet(256, 256)
    ch = s.box(18, 14, 11, PT, shade=MT, top=PU)
    s.draw(ch, "front", 0, 0, ["pppppppppppppppppp", "p.......pp.......p", "p..tttt....tttt..p", "...t..........t...",
                               "......kkkkkk......", ".....kk....kk.....", ".....k......k.....", ".....k......k.....",
                               ".....kk....kk.....", "......kkkkkk......", "..t............t..", "..tt..........tt..",
                               "mmmmmmmmmmmmmmmmmm", "mmmmmmmmmmmmmmmmmm"], K)
    for f in ("left", "right"):
        s.draw(ch, f, 0, 0, ["ppppppppppp", "p.........p", "..t..t..t..", ".tt..t..tt.", "...........",
                             "..t.....t..", "...........", "....ttt....", "...........", "..........."], K)
    s.draw(ch, "back", 0, 0, ["pppppppppppppppppp", "..................", "..tt...tttt...tt..", "......tt..tt......"], K)
    pb(m, s, "body", ch, (-9, 13, -5.5))
    # the heart gem: two squares turned into an octagon, pink and glowing, in the dark chest hole
    for a in (0, 45):
        m.c("body", PK, (0, 20.5, 5.6), (3.8, 3.8, 1.2), (0, 0, a), light=True)
    m.c("body", WH, (0, 20.5, 6.1), (1.4, 1.4, 0.4), (0, 0, 45), light=True)
    # head sunk between the shoulders with one glowing eye slit and a crystal crown
    hd = s.box(8, 6, 7, PT, top=PU)
    s.draw(hd, "front", 0, 0, ["pppppppp", "........", ".kkkkkk.", ".kiiwik.", ".kkkkkk.", "........"], K)
    pb(m, s, "head", hd, (-4, 27, -2.5), lit={PK, WH})
    for x, h, a in ((-2.5, 4, 18), (0, 6, 0), (2.5, 4, -18)):
        m.c("head", AM, (x, 33 + h / 2 - 0.5, 0), (1.6, h, 1.6), (0, 45, a), light=False)
    # crystal spires out of the shoulders and back
    for x, y, z, h, rx, rz in ((10, 29, 1, 9, 10, -25), (12.5, 28, -2, 6, -15, -40), (8, 28, -3, 5, -25, -10),
                               (-10, 29, 1, 8, 10, 25), (-12.5, 28, -2, 6, -15, 40), (-7, 28, -3, 6, -25, 10),
                               (0, 26, -6, 8, -40, 0), (3, 22, -6, 5, -55, -15), (-3, 21, -6, 5, -55, 15)):
        m.c("body", AM, (x, y + h / 2 - 1, z), (2.4, h, 2.4), (rx, 45, rz), (x, y, z))
        m.c("body", MG, (x, y + h - 1.2, z), (1.2, 1.6, 1.2), (rx, 45, rz), (x, y, z), light=True)
    # arms: plated, with raw crystal cluster fists
    for side, arm in ((1, "armL"), (-1, "armR")):
        sh = s.box(7, 6, 8, PU, shade=PT)
        for f in ("front", "back", "left", "right"):
            s.draw(sh, f, 0, 0, ["mmmmmmmm", "........", "..t..t..", "........", "........", "tttttttt"], K)
        pb(m, s, arm, sh, (side * 12 - 3.5, 22, -4))
        ua = s.box(5, 9, 5, PT, shade=MT)
        pb(m, s, arm, ua, (side * 12 - 2.5, 13, -2.5))
        fist = s.box(7, 6, 7, AM)
        pb(m, s, arm, fist, (side * 12 - 3.5, 7, -3.5))
        for dx, dz, h, a in ((0, 3, 4, 30), (side * 3, 0, 3.5, 0), (0, -3, 3, -30), (side * 2, 2, 3, 20)):
            m.c(arm, AM, (side * 12 + dx, 9.5, dz), (1.8, h, 1.8), (a, 45, side * -60 if dx else 0), (side * 12, 9.5, 0))
    # legs
    for side, leg in ((1, "legL"), (-1, "legR")):
        lg = s.box(6, 11, 6, PT, shade=MT, top=PU)
        for f in ("front", "back", "left", "right"):
            s.draw(lg, f, 0, 0, ["......", "......", "......", "pppppp", "......", "......", "......", "......",
                                 "......", "mmmmmm", "mmmmmm"], K)
        pb(m, s, leg, lg, (side * 4.5 - 3, 0, -3))
    # floating shards
    for x, y, z, a in ((-17, 30, 4, 20), (17, 18, 6, -30), (-15, 12, -6, 45), (14, 34, -6, -15)):
        m.c("body", AM, (x, y, z), (1.8, 4.5, 1.8), (a, 45, a / 2))
        m.c("body", MG, (x, y, z), (0.8, 2, 2.2), (a, 45, a / 2), light=True)
    m.attacks = {"slam": "slam", "shards": "roar", "spin": "spin", "charge": "charge"}
    m.melee = "swipe"
    return m


# ---------------------------------------------------------------- rough concept builds (to be finished)

def _face(m, bone, s, uv, lo, K, front=None, sides=None, back=None, lit=()):
    if front: s.draw(uv, "front", 0, 0, front, K)
    for f in ("left", "right"):
        if sides: s.draw(uv, f, 0, 0, sides, K)
    if back: s.draw(uv, "back", 0, 0, back, K)
    pb(m, s, bone, uv, lo, lit=lit)


@model
def rust_knight():
    """An empty suit of copper armour, green with rust in patches, with a lightning-rod lance and a tall
    plume of chain. Its visor shows only a crackling blue light."""
    m = Model("rust_knight", "biped", 2.4)
    biped(m, hip=12, legx=3, neck=26, shoulder=24, armx=8.5)
    m.bone("lance", "armR", (-8.5, 12, 1))
    m.hold = {"lance": 0}
    CU, CT, OX, WE, BK, LB = "copper_block", "cut_copper", "oxidized_copper", "weathered_copper", "black_concrete", "light_blue_concrete"
    K = {"c": CT, "o": OX, "w": WE, "k": BK, "l": LB, "g": "gold_block"}
    s = Sheet(128, 128)
    _face(m, "body", s, s.box(12, 13, 7, CU, shade=CT), (-6, 13, -3.5), K,
          front=["cccccccccccc", "c....cc....c", "c....cc..o.c", ".....cc.ooo.", "..o..cc..o..", ".ooo.cc.....",
                 "..o..cc.....", ".....cc.....", "cccccccccccc", "kkkkkgkkkkkk", "cccccccccccc", "..w......w..", "............"],
          sides=["ccccccc", ".......", "..oo...", ".ooo...", ".......", ".......", "....w..", ".......", "ccccccc", "kkkkkkk"])
    _face(m, "head", s, s.box(8, 9, 8, CU, shade=CT, top=CT), (-4, 26, -4), K,
          front=["cccccccc", "........", "........", "kkkkkkkk", "klllllkk", "kkkkkkkk", "..k..k..", "..k..k..", "...oo..."],
          sides=["cccccccc", "........", "..o.....", ".ooo....", "........", "........", "......w.", "........", "........"], lit={LB})
    for k in range(5):
        m.c("head", "chain", (0, 35.5 + k * 0.4, -1 - k * 1.3), (1, 2, 1.2), (-50 - k * 12, 0, 0))
    for side, arm in ((1, "armL"), (-1, "armR")):
        _face(m, arm, s, s.box(7, 5, 7, CU, shade=CT, top=CT), (side * 8.5 - 3.5, 22, -3.5), K,
              front=["ccccccc", ".......", "..o....", ".ooo...", "......."], sides=["ccccccc", ".......", ".....o.", "....oo.", "......."])
        _face(m, arm, s, s.box(4, 11, 4, CU, shade=CT), (side * 8.5 - 2, 11, -2), K, front=["....", "....", "....", "....", "cccc", ".o..", "oo.."])
        m.c(arm, WE, (side * 8.5, 10, 0), (4.6, 2.4, 4.6))
    for side, leg in ((1, "legL"), (-1, "legR")):
        _face(m, leg, s, s.box(5, 12, 5, CU, shade=CT), (side * 3 - 2.5, 0, -2.5), K,
              front=[".....", ".....", ".....", ".....", "ccccc", "..o..", ".....", ".....", ".....", ".w...", "ccccc", "ccccc"])
    # lance: a lightning rod with a copper guard
    m.c("lance", "lightning_rod", (-8.5, 18, 1), (1.6, 26, 1.6))
    m.c("lance", CU, (-8.5, 13, 1), (4, 1.4, 4))
    m.c("lance", LB, (-8.5, 31.6, 1), (0.8, 2, 0.8), light=True)
    m.attacks = {"charge": "charge", "lightning": "roar", "slam": "slam", "spin": "spin"}
    m.melee = "swipe"
    return m


@model
def the_puppeteer():
    """A tall thin figure in a long purple coat and a white mask with a painted smile. Its two huge hands
    float apart from it, and strings hang from every finger."""
    m = Model("the_puppeteer", "float", 2.6)
    m.bone("core", "root", (0, 14, 0))
    m.bone("head", "core", (0, 30, 0))
    m.bone("handL", "core", (12, 26, 2)); m.bone("handR", "core", (-12, 26, 2))
    PU, DP, WH, BK, RD, GO = "purple_concrete", "purple_terracotta", "white_concrete", "black_concrete", "red_concrete", "gold_block"
    K = {"p": PU, "d": DP, "w": WH, "k": BK, "r": RD, "g": GO}
    s = Sheet(128, 128)
    # coat: a long tapered robe, buttons and a hem
    _face(m, "core", s, s.box(8, 12, 5, PU, shade=DP), (-4, 18, -2.5), K, front=["dddddddd", "...gg...", "........", "...gg...", "........", "...gg..."])
    _face(m, "core", s, s.box(10, 8, 7, PU, shade=DP), (-5, 10, -3.5), K, front=["...gg...."[:10] + ".", "..........", "...gg.....", "dddddddddd"])
    _face(m, "core", s, s.box(12, 8, 9, DP, shade=BK), (-6, 2, -4.5), K, front=["dddddddddddd", "............", "....pp......", "kkkkkkkkkkkk"])
    m.c("core", BK, (0, 30.5, 0), (2, 1.5, 2))
    # mask head with a top hat
    _face(m, "head", s, s.box(6, 7, 6, WH), (-3, 31, -3), K, front=["......", ".k..k.", ".k..k.", "......", "r....r", ".rrrr.", "......"])
    m.c("head", BK, (0, 38.4, 0), (8, 0.8, 8))
    m.c("head", BK, (0, 41, 0), (5, 4.6, 5))
    m.c("head", RD, (0, 39.4, 0), (5.2, 1, 5.2))
    # floating hands with strings
    for side, b in ((1, "handL"), (-1, "handR")):
        x = side * 13
        m.c(b, WH, (x, 26, 2), (5, 1.6, 5))
        for k in range(4):
            fx = x - 1.8 + k * 1.2
            m.c(b, WH, (fx, 24.6, 4.8), (0.9, 2.4, 0.9), (20, 0, 0))
            m.c(b, "white_wool", (fx, 15, 5.4), (0.15, 16, 0.15))
        m.c(b, PU, (x, 27.4, 2), (5.4, 1.4, 5.4))
    m.no_elbows = True
    m.attacks = {"strings": "spin", "slam": "dive", "summon": "raise", "throw": "pulse"}
    m.melee = "pulse"
    return m


@model
def deepink():
    """A giant octopus in an old brass diving helmet with a round glass window. Eight curling arms with
    pale suckers hang below it."""
    m = Model("deepink", "float", 2.6)
    m.bone("core", "root", (0, 16, 0))
    m.bone("head", "core", (0, 20, 0))
    RD, DR, PK, CU, AU, BK, LB = "red_terracotta", "brown_terracotta", "pink_terracotta", "cut_copper", "gold_block", "black_concrete", "light_blue_concrete"
    K = {"r": RD, "d": DR, "p": PK, "k": BK, "w": "white_concrete", "y": "yellow_concrete"}
    s = Sheet(128, 128)
    _face(m, "core", s, s.box(14, 10, 14, RD, shade=DR, top=RD), (-7, 14, -7), K,
          front=["..............", "..............", "..ppp....ppp..", "..pyk....kyp..", "..ppp....ppp..", "..............", ".....dddd.....", "..............", "..............", ".............."],
          sides=["..............", "...p......p...", "..............", ".......p......", ".p............", "..............", "....p.....p..."])
    # diving helmet
    m.c("head", CU, (0, 26.5, 0), (13, 4, 13))
    m.c("head", CU, (0, 29.5, 0), (10, 2.4, 10))
    m.c("head", AU, (0, 24.6, 0), (14.4, 1.2, 14.4))
    m.c("head", AU, (0, 26.8, 6.6), (6, 3.6, 0.6))
    m.c("head", LB, (0, 26.8, 6.8), (4.4, 2.4, 0.4), light=False)
    m.c("head", AU, (0, 31.2, 0), (2, 1.4, 2))
    # eight curling arms
    from models import limb
    for k in range(8):
        a = k * 45 + 22.5
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        b = m.bone("arm%d" % k, "core", (ca * 5, 15, sa * 5))
        segs = [(5, 2.6, (0, 0, 0), RD), (5, 2.2, (0, 0, 0), RD), (4, 1.8, (0, 0, 0), PK), (3, 1.4, (0, 0, 0), RD)]
        bends = (150, 165, 200, 235)
        out = []
        for (L, th, _, blk), bd in zip(segs, bends):
            # tilt outward around the axis perpendicular to the arm direction
            out.append((L, th, (bd * sa / 1.0 if False else 0, 0, 0), blk))
        x, y, z = ca * 5, 15, sa * 5
        tilt = (160, 140, 120, 95)
        for (L, th, _, blk), t in zip(segs, tilt):
            dx, dy = math.sin(math.radians(t)), math.cos(math.radians(t))
            cx, cy, cz = x + ca * dx * L / 2, y + dy * L / 2, z + sa * dx * L / 2
            phi = math.degrees(math.atan2(ca, sa))
            m.c(b, blk, (cx, cy, cz), (th, L, th), (t, phi, 0), (cx, cy, cz))
            x, y, z = x + ca * dx * L, y + dy * L, z + sa * dx * L
    m.no_elbows = True
    m.attacks = {"ink": "pulse", "grab": "spin", "slam": "dive", "whirl": "raise"}
    m.melee = "pulse"
    return m


@model
def old_bellows():
    """A walking forge. Its belly is a furnace with a glowing grate, its fists are anvils, a brick chimney
    rises from its back and its little head is a blackened iron pot with ember eyes."""
    m = Model("old_bellows", "biped", 2.4)
    biped(m, hip=10, legx=4.5, neck=27, shoulder=24, armx=11)
    BR, DS, BK, OR, YE, GR, FE = "bricks_x", "polished_deepslate", "black_concrete", "orange_concrete", "yellow_concrete", "gray_concrete", "iron_block"
    BR = "red_terracotta"
    K = {"b": "brown_terracotta", "d": DS, "k": BK, "o": OR, "y": YE, "g": GR, "r": "red_concrete"}
    s = Sheet(128, 128)
    _face(m, "body", s, s.box(16, 15, 11, DS, shade=BK, top=DS), (-8, 11, -5.5), K,
          front=["gggggggggggggggg", "................", "..kkkkkkkkkkkk..", "..kooooooooook..", "..kgogogogogok..", "..koyyyyyyyyok..",
                 "..kgygygygygyk..", "..koyyyyyyyyok..", "..kgogogogogok..", "..kkkkkkkkkkkk..", "................", "...g........g...",
                 "gggggggggggggggg", "................", "kkkkkkkkkkkkkkkk"],
          sides=["ggggggggggg", "...........", "..g.....g..", "...........", "...........", "..g.....g..", "...........", "ggggggggggg"], lit={OR, YE})
    # chimney
    m.c("body", BR, (0, 30, -3.5), (4.5, 10, 4.5))
    m.c("body", BK, (0, 35.2, -3.5), (5.4, 1, 5.4))
    m.c("body", OR, (0, 35.6, -3.5), (3, 0.3, 3), light=True)
    # pot head with ember eyes
    _face(m, "head", s, s.box(8, 6, 7, BK, top=DS), (-4, 26, -2), K, front=["dddddddd", "........", ".oo..oo.", "........", "..kkkk..", "........"], lit={OR})
    m.c("head", DS, (0, 32.4, 1.5), (9, 0.8, 8))
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 11
        m.c(arm, "black_terracotta", (x, 22, 0), (6, 6, 6))
        m.c(arm, DS, (x, 15.5, 0), (4.4, 8, 4.4))
        m.c(arm, "anvil", (x, 9, 0), (7, 5, 5))
    for side, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, DS, (side * 4.5, 6, 0), (5.4, 8, 5.4))
        m.c(leg, BK, (side * 4.5, 1.2, 0.8), (6.4, 2.4, 7.4))
    m.attacks = {"slam": "slam", "fire": "roar", "throw": "spin", "charge": "charge"}
    m.melee = "swipe"
    return m


@model
def sporelord():
    """A hunched mushroom king under a huge red spotted cap, with a beard of hanging gills, two pale
    glowing eyes in the shade of the cap and a staff of brown mushrooms."""
    m = Model("sporelord", "biped", 2.5)
    biped(m, hip=8, legx=2.5, neck=20, shoulder=18, armx=6.5)
    m.bone("staff", "armR", (-6.5, 8, 1))
    m.hold = {"staff": 0}
    ST, RD, WH, BK, BR, LG = "mushroom_stem", "red_mushroom_block", "white_concrete", "black_concrete", "brown_mushroom_block", "light_gray_concrete"
    K = {"w": WH, "k": BK, "g": LG, "y": "lime_concrete"}
    s = Sheet(128, 128)
    _face(m, "body", s, s.box(9, 11, 7, ST, shade=LG), (-4.5, 9, -3.5), K, front=[".........", ".........", "g.g.g.g.g", ".g.g.g.g.", "g.g.g.g.g", "........."])
    # cap: wide and domed, white spots
    m.c("head", RD, (0, 24.5, 0), (22, 3, 22))
    m.c("head", RD, (0, 27.5, 0), (17, 3, 17))
    m.c("head", RD, (0, 30, 0), (10, 2, 10))
    for x, y, z, sz in ((6, 26.2, 9.2, 3), (-7, 26.2, 8.8, 2.4), (9.2, 26.2, -3, 2.6), (-9.2, 26.2, 2, 2.6), (2, 29.2, 7.2, 2.4),
                        (-5, 29.2, -6, 2.2), (4, 31.1, -1, 2.4), (-8.6, 29.2, -1, 2), (0, 26.2, -11.1, 3)):
        m.c("head", WH, (x, y, z), (sz if abs(z) < 8.5 else sz, sz * 0.7, sz if abs(x) < 8.5 else sz))
    m.c("head", "brown_terracotta", (0, 22.6, 0), (20, 0.8, 20))
    _face(m, "head", s, s.box(7, 4, 6, ST), (-3.5, 19, -3), K, front=[".......", ".yy.yy.", ".......", "......."], lit={"lime_concrete"})
    for x in (-2.5, -1, 0.5, 2):
        m.c("head", LG, (x, 16.5, 3.2), (0.8, 5, 0.6))
    for side, arm in ((1, "armL"), (-1, "armR")):
        m.c(arm, ST, (side * 6.5, 13.5, 0), (3, 9, 3))
    for side, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, ST, (side * 2.5, 4, 0), (3.6, 8, 3.6))
    m.c("staff", "dark_oak_planks", (-6.5, 14, 1), (1.2, 22, 1.2))
    m.c("staff", BR, (-6.5, 25.5, 1), (5, 1.6, 5))
    m.c("staff", BR, (-6.5, 27, 1), (3, 1.4, 3))
    m.attacks = {"spores": "roar", "slam": "slam", "summon": "spin", "charge": "charge"}
    m.melee = "swipe"
    return m


@model
def jackknife():
    """A grinning jester on long thin legs, in a red and purple diamond suit with a three-pointed bell
    hat, juggling lit TNT above his head."""
    m = Model("jackknife", "biped", 2.3)
    biped(m, hip=15, legx=2, neck=27, shoulder=25, armx=6)
    RD, PU, WH, BK, AU = "red_concrete", "purple_concrete", "white_concrete", "black_concrete", "gold_block"
    K = {"r": RD, "p": PU, "w": WH, "k": BK, "g": AU}
    s = Sheet(128, 128)
    _face(m, "body", s, s.box(8, 11, 5, RD), (-4, 16, -2.5), K,
          front=["wwwwwwww", "pppp....", "pppp....", "pppp....", "pppp....", "pppp....", "....pppp", "....pppp", "....pppp", "....pppp", "gggggggg"],
          sides=["wwwww", ".....", ".....", ".....", ".....", ".....", "ppppp", "ppppp", "ppppp", "ppppp", "ggggg"])
    m.c("body", WH, (0, 27, 0), (10, 1.2, 7))
    _face(m, "head", s, s.box(7, 7, 7, WH), (-3.5, 28, -3.5), K, front=[".......", ".k...k.", ".r...r.", ".......", "k.....k", ".kkkkk.", "......."])
    for a, blk in ((-55, RD), (0, PU), (55, RD)):
        m.c("head", blk, (0, 37, 0), (3, 8, 3), (0, 0, a), (0, 35, 0))
        r = math.radians(a)
        m.c("head", AU, (-math.sin(r) * 9.5, 35 + math.cos(r) * 9.5 - 0.5, 0), (1.6, 1.6, 1.6))
    for side, arm, blk in ((1, "armL", PU), (-1, "armR", RD)):
        m.c(arm, blk, (side * 6, 20, 0), (2.6, 10, 2.6))
        m.c(arm, WH, (side * 6, 14.6, 0), (3, 1.4, 3))
    for side, leg, blk in ((1, "legL", RD), (-1, "legR", PU)):
        m.c(leg, blk, (side * 2, 7.5, 0), (2.6, 15, 2.6))
        m.c(leg, BK, (side * 2, 0.6, 1.4), (3, 1.2, 5.4))
        m.c(leg, AU, (side * 2, 1.6, 4.4), (1, 1, 1))
    for x, y in ((-5, 41), (0, 45), (5, 41)):
        m.c("body", "tnt", (x, y, 2), (3, 3, 3), (0, 20, 15))
        m.c("body", "yellow_concrete", (x, y + 2, 2), (0.6, 1, 0.6), light=True)
    m.attacks = {"tnt": "spin", "blink": "charge", "copies": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


@model
def sunscarab():
    """A giant golden beetle. Its wing shells are carved sandstone with a sun pattern, a glowing ruby gem
    sits on its horned head, and its six legs are black and hooked."""
    m = Model("sunscarab", "quad", 2.4)
    quad(m, body_y=8, legx=8, legz_front=6, legz_back=-6, neck_y=9, neck_z=12)
    m.mbone("legML", "body", (8, 8, 0))
    AU, SS, CS, BK, RD, OR = "gold_block", "smooth_sandstone", "cut_sandstone", "black_concrete", "red_concrete", "orange_terracotta"
    K = {"g": AU, "k": BK, "o": OR, "y": "yellow_terracotta", "s": SS}
    s = Sheet(128, 128)
    for side in (1, -1):
        shell = s.box(8, 6, 20, SS, shade=OR, top=SS)
        s.draw(shell, "top", 0, 0, ["........", ".oooooo.", ".o....o.", ".o.yy.o.", ".o.yy.o.", ".o....o.", ".oooooo.", "........",
                                     "...o....", "..ooo...", "...o....", "........", ".o....o.", "..o..o..", "...oo...", "..o..o..",
                                     ".o....o.", "........", "........", "........"], K)
        s.draw(shell, "left" if side > 0 else "right", 0, 0, ["oooooooooooooooooooo", "...................."], K)
        pb(m, s, "body", shell, (side * 4.1 - 4, 8, -11))
    m.c("body", AU, (0, 9, 0), (15, 5, 20))
    m.c("body", BK, (0, 13.7, 0), (0.6, 0.8, 20))
    _face(m, "head", s, s.box(9, 5, 6, AU, shade=OR), (-4.5, 6, 9), K, front=[".........", ".kk...kk.", ".........", "....k....", "........."])
    m.c("head", AU, (0, 12.5, 15), (2, 6, 2), (30, 0, 0), (0, 10, 14))
    m.c("head", RD, (0, 11.5, 12), (2.6, 2.6, 2.6), (0, 45, 0), light=True)
    for x in (-3, 3):
        m.c("jaw", BK, (x, 6.5, 16), (1, 1, 3), (0, -20 * (1 if x > 0 else -1), 0))
    for leg, x, z in (("legFL", 8, 6), ("legFR", -8, 6), ("legML", 8, 0), ("legMR", -8, 0), ("legBL", 8, -6), ("legBR", -8, -6)):
        sx = 1 if x > 0 else -1
        m.c(leg, BK, (x + sx * 2.5, 8, z), (6, 1.4, 1.4), (0, 0, sx * -25))
        m.c(leg, BK, (x + sx * 5, 3.5, z), (1.2, 8, 1.2), (0, 0, sx * 12))
    m.attacks = {"burrow": "rear", "charge": "charge", "sand": "howl", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def waxmother():
    """A tall candle woman of white wax melting down her sides, wearing a holder of old gold. Her hair is
    a living flame and her eyes are two dark drips."""
    m = Model("waxmother", "float", 2.5)
    m.bone("core", "root", (0, 0, 0))
    m.bone("head", "core", (0, 28, 0))
    WX, CR, AU, BK, OR, YE = "white_terracotta", "white_concrete", "gold_block", "black_concrete", "orange_concrete", "yellow_concrete"
    K = {"w": CR, "k": BK, "g": AU, "c": "light_gray_concrete"}
    s = Sheet(128, 128)
    _face(m, "core", s, s.box(10, 22, 10, WX), (-5, 6, -5), K,
          front=["wwwwwwwwww", "w.ww..w.ww", "w..w....w.", "w..w......", "...w......", "..........", "......c...", "..........",
                 "..........", "...c......", "..........", "........c.", "..........", ".........."],
          sides=["wwwwwwwwww", "ww.w.ww..w", ".w.w..w...", ".w....w...", "......w...", "..........", "..c......."])
    m.c("core", AU, (0, 4.5, 0), (14, 3, 14))
    m.c("core", AU, (0, 2, 0), (8, 2, 8))
    m.c("core", AU, (0, 0.5, 0), (16, 1, 16))
    m.c("core", AU, (8.2, 4.5, 0), (2.4, 0.8, 3), (0, 0, 0))
    _face(m, "head", s, s.box(8, 7, 8, WX), (-4, 28, -4), K, front=["wwwwwwww", "........", ".kk..kk.", ".k....k.", "........", "...kk...", "........"])
    m.c("head", BK, (0, 35.6, 0), (0.8, 1.6, 0.8))
    m.c("head", OR, (0, 38, 0), (6, 4, 6), light=True)
    m.c("head", YE, (0, 41, 0), (4, 3, 4), light=True)
    m.c("head", "white_concrete", (0, 43.5, 0), (2, 2.4, 2), light=True)
    for x, z, h in ((-5.3, 2, 6), (5.3, -1, 8), (2, 5.3, 5), (-2, -5.3, 7)):
        sx, sz = (0.6, 1.4) if abs(x) > 5 else (1.4, 0.6)
        m.c("core", CR, (x, 28 - h / 2, z), (sx, h, sz))
    m.no_elbows = True
    m.attacks = {"fire": "pulse", "wax": "spin", "slam": "dive", "rise": "raise"}
    m.melee = "pulse"
    return m


@model
def thornback():
    """A wolf-shaped beast woven from dark vines, thorns jutting from its back, red berries in the tangle
    and two glowing green eyes."""
    m = Model("thornback", "quad", 2.4)
    quad(m, body_y=12, legx=4, legz_front=7, legz_back=-7, neck_y=15, neck_z=10)
    GT, DG, MO, BR, RD, LI = "green_terracotta", "dark_oak_log", "moss_block", "brown_terracotta", "red_concrete", "lime_concrete"
    K = {"d": "black_terracotta", "m": MO, "b": BR, "r": RD, "l": LI, "k": "black_concrete"}
    s = Sheet(128, 128)
    _face(m, "body", s, s.box(10, 9, 20, GT, shade=BR, top=GT), (-5, 9, -10), K,
          sides=["....m.......m.......", ".b......r....b......", "...b.b......b...r...", "......m.....b.......", "..r....b.b......m...", ".b.......m......b...",
                 "....b.r.......b.....", "..........b.........", "bbbbbbbbbbbbbbbbbbbb"])
    _face(m, "head", s, s.box(8, 7, 8, GT, shade=BR), (-4, 11, 9), K, front=["....m...", "........", ".ll..ll.", ".kl..lk.", "........", ".bbbbbb.", ".k.kk.k."], lit={LI})
    m.c("head", GT, (0, 12.5, 18), (5, 3.5, 3))
    m.c("head", "black_concrete", (0, 13.6, 19.6), (2, 1, 0.3))
    for x in (-3, 3):
        m.c("head", BR, (x, 19.5, 11), (1.2, 3, 1.2), (-20, 0, 15 * (1 if x < 0 else -1)))
    for z, h, a in ((7, 6, -25), (3, 7, -30), (-1, 6, -30), (-5, 5, -35), (-9, 4, -40)):
        for x in (-2, 2):
            m.c("body", BR, (x, 18 + h / 2 - 0.5, z), (1.2, h, 1.2), (a, 0, -x * 6), (x, 18, z))
    for leg, x, z in (("legFL", 4, 7), ("legFR", -4, 7), ("legBL", 4, -7), ("legBR", -4, -7)):
        m.c(leg, GT, (x, 5, z), (3.4, 10, 3.4))
        m.c(leg, BR, (x, 0.6, z + 0.8), (3.8, 1.2, 4.6))
    from models import limb
    limb(m, "tail", GT, (0, 16, -10), [(5, 2.4, (-130, 0, 0)), (5, 2, (-110, 0, 0)), (3, 1.4, (-80, 0, 0), BR)])
    m.attacks = {"thorns": "howl", "pounce": "charge", "slam": "rear", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def thunderhoot():
    """A huge storm owl with dark blue feathers lit by yellow lightning lines, big round glowing eyes in
    a pale face disc and wings half spread."""
    m = Model("thunderhoot", "float", 2.6)
    m.bone("core", "root", (0, 6, 0))
    m.bone("head", "core", (0, 20, 0))
    m.mbone("wingL", "core", (7, 18, 0))
    BL, DB, YE, WH, BK, LG = "blue_terracotta", "blue_concrete", "yellow_concrete", "white_concrete", "black_concrete", "light_gray_concrete"
    K = {"b": DB, "y": YE, "w": WH, "k": BK, "g": LG, "o": "orange_concrete"}
    s = Sheet(128, 128)
    _face(m, "core", s, s.box(12, 14, 10, BL, shade=DB), (-6, 6, -5), K,
          front=["............", "..g.g..g.g..", "...g.g.g.g..", "..g.g..g.g..", "...g.g.g.g..", "..g.g..g.g..", "...g.g.g.g..", "..g.g..g.g..", "............"],
          sides=["..........", "..y.......", "...y......", "...yy.....", ".....y....", "......y...", "......yy..", "........y."], lit={YE})
    _face(m, "head", s, s.box(12, 9, 9, BL, top=DB), (-6, 20, -4.5), K,
          front=["b..........b", "............", ".gggg..gggg.", "gwwyyggyywwg", "gwykkggkkywg", "gwykkggkkywg", "ggwwwoowwwgg", "....g..g....", "............"], lit={YE})
    for x in (-4.5, 4.5):
        m.c("head", DB, (x, 30.5, -1), (2, 3, 2), (0, 0, 12 * (1 if x < 0 else -1)))
    for side, w in ((1, "wingL"), (-1, "wingR")):
        sh = s.box(14, 12, 1, BL)
        s.draw(sh, "front", 0, 0, ["..............", "...y..........", "....y.........", "....yy........", "......y.......", ".......yy.....", ".........y....", "bbbbbbbbbbbbbb", "b.b.b.b.b.b.b.", "b.b.b.b.b.b.b.", "b...b...b...b.", ".............."], K)
        pb(m, s, w, sh, (side * 6 - (0 if side > 0 else 14), 8, -3), lit={YE}, rot=(0, -25 * side, -20 * side), origin=(side * 7, 18, 0))
    for x in (-2.5, 2.5):
        m.c("core", "orange_terracotta", (x, 5, 1), (2, 2, 3))
    m.no_elbows = True
    m.attacks = {"lightning": "pulse", "swoop": "dive", "gust": "spin", "screech": "raise"}
    m.melee = "pulse"
    return m


@model
def tundrus():
    """A woolly mammoth out of the far north: shaggy brown fur heavy with frost, long curling ice tusks
    and a raised trunk."""
    m = Model("tundrus", "quad", 2.2)
    quad(m, body_y=14, legx=6, legz_front=8, legz_back=-9, neck_y=24, neck_z=14)
    BR, DB, WH, PI, BI, BK = "brown_wool", "brown_terracotta", "white_concrete", "packed_ice", "blue_ice", "black_concrete"
    K = {"d": DB, "w": WH, "s": "snow_block", "k": BK, "l": "light_gray_wool"}
    s = Sheet(256, 128)
    _face(m, "body", s, s.box(18, 18, 26, BR, shade=DB, top=BR), (-9, 12, -13), K,
          sides=["ssswsssswssssswssssswssssw", ".s..s..w...s..s...w..s..s.", "..........................", ".d...d...d...d...d...d...d",
                 "..........................", "d...d...d...d...d...d...d.", "..........................", "...d...d...d...d...d...d..",
                 "..........................", "..........................", "..........................", "..........................",
                 "..........................", "..........................", "..........................", ".d.d.d.d.d.d.d.d.d.d.d.d.d",
                 "dddddddddddddddddddddddddd", "d.d.d.d.d.d.d.d.d.d.d.d.d."],
          back=["ssswsssswsssssws", "..................", ".d...d...d...d....", "......"])
    m.c("body", BR, (0, 31.5, 6), (12, 3, 10))
    m.c("body", "snow_block", (0, 33.2, 6), (10, 0.6, 8))
    _face(m, "head", s, s.box(12, 12, 9, BR, shade=DB), (-6, 18, 12), K,
          front=["ssssssssssss", "............", "............", ".kd......dk.", "............", "............", "............", "............", "............", "....dddd....", "....d..d....", "............"])
    from models import limb
    limb(m, "jaw", BR, (0, 19, 20), [(5, 4, (160, 0, 0)), (5, 3.2, (175, 0, 0)), (4, 2.6, (200, 0, 0)), (3, 2.2, (240, 0, 0), DB)])
    for side in (1, -1):
        limb(m, "head", PI, (side * 4.5, 20, 19), [(5, 2.4, (100, 0, side * -30)), (5, 2, (60, 0, side * -30)), (4, 1.6, (10, 0, side * -10), BI)])
    for leg, x, z in (("legFL", 6, 8), ("legFR", -6, 8), ("legBL", 6, -9), ("legBR", -6, -9)):
        m.c(leg, BR, (x, 7, z), (6, 14, 6))
        m.c(leg, DB, (x, 1, z), (6.6, 2, 6.6))
        m.c(leg, "snow_block", (x, 2.3, z), (6.8, 0.6, 6.8))
    m.c("tail", BR, (0, 22, -14.5), (1.6, 6, 1.6), (-20, 0, 0))
    m.attacks = {"stomp": "rear", "charge": "charge", "ice": "howl", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def mossheart_stag():
    """A forest stag the size of a hill: mossy green-brown coat, a white chest ruff, and huge antlers of
    living branches hung with moss, leaves and glowing mushrooms."""
    m = Model("mossheart_stag", "quad", 2.3)
    quad(m, body_y=17, legx=4, legz_front=8, legz_back=-8, neck_y=26, neck_z=13)
    BR, DB, MO, WH, BK, LO = "brown_terracotta", "black_terracotta", "moss_block", "white_terracotta", "black_concrete", "dark_oak_log"
    K = {"d": DB, "m": MO, "w": WH, "k": BK, "g": "green_terracotta", "y": "lime_concrete"}
    s = Sheet(256, 128)
    _face(m, "body", s, s.box(11, 11, 22, BR, shade=DB, top=MO), (-5.5, 15, -11), K,
          sides=["mmmgmmmmgmmmmgmmmgmmmm", "m.m..g.m...m..g..m..m.", "...........m..........", "......................", "..w..w..w.............", ".........w..w..w......", "......................", "dddddddddddddddddddddd"])
    # neck up to the head, white chest ruff
    m.c("body", BR, (0, 25, 12), (6, 10, 6), (25, 0, 0))
    m.c("body", WH, (0, 21, 13.5), (6.6, 5, 3), (25, 0, 0))
    _face(m, "head", s, s.box(6, 6, 9, BR, shade=DB, top=BR), (-3, 27, 13), K, front=["......", "......", "......", "......", ".kkkk.", "......"],
          sides=["mmmmmmmmm", ".........", "..kyk....", "...k.....", ".........", "........."], lit={"lime_concrete"})
    for x in (-3.5, 3.5):
        m.c("head", BR, (x, 33, 14), (1.2, 2.6, 0.8), (0, 0, 40 * (1 if x > 0 else -1)))
    from models import limb
    for side in (1, -1):
        t1 = limb(m, "head", LO, (side * 2, 33, 17), [(5, 1.4, (0, 0, side * -35)), (5, 1.2, (0, 0, side * -15)), (5, 1, (0, 0, side * -45))])
        limb(m, "head", LO, (side * 4.5, 36.5, 17), [(4, 1, (-30, 0, side * 10))])
        limb(m, "head", LO, (side * 6.5, 40, 17), [(3.5, 0.9, (-20, 0, side * 30))])
        m.c("head", "azalea_leaves", (t1[0], t1[1], 17), (3.4, 2.4, 3.4))
        m.c("head", MO, (side * 4.4, 35.6, 17), (0.6, 2.4, 0.6))
        m.c("head", "shroomlight", (side * 6.2, 39, 17.6), (1.2, 1, 1.2), light=True)
    for leg, x, z in (("legFL", 4, 8), ("legFR", -4, 8), ("legBL", 4, -8), ("legBR", -4, -8)):
        m.c(leg, BR, (x, 8.5, z), (3, 13, 3))
        m.c(leg, DB, (x, 1, z + 0.3), (3.4, 2, 3.8))
        m.c(leg, WH, (x, 2.4, z), (3.4, 0.8, 3.4))
    m.c("tail", WH, (0, 23, -11.6), (2.4, 3, 1.4), (-30, 0, 0))
    m.attacks = {"roots": "howl", "charge": "charge", "rear": "rear", "toss": "toss"}
    m.melee = "bite"
    return m
