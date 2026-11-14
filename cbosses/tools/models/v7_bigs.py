"""v7: the big bosses from the user's reference pictures (refs/ref33-39 in project files). Painted boxes on a
code-drawn Sheet; every face gets a picture with shading on its edges, so each box reads as a shape."""
import math
from models import model, biped, quad, limb
from build import Model
from texpaint import paintbox, Sheet, load, snap, autopal

SPAWN, DEATH = {}, {}


def pb(m, s, bone, uv, lo, lit=(), **kw):
    kw.setdefault("passes", 0)
    return paintbox(m, bone, s.img, uv, lo, s.sizes[uv], allowed=sorted(s.used), lit=lit, **kw)


def shade(s, uv, K, top=None, bottom=None, left=None, right=None, faces=("front", "back", "left", "right")):
    """Edge shading on the side faces: a light top row and dark bottom row, optional dark sides."""
    for f in faces:
        fu, fv, fw, fh = s.face(uv, f)
        if top: s.rect(uv, f, 0, 0, fw, 1, K[top])
        if bottom: s.rect(uv, f, 0, fh - 1, fw, 1, K[bottom])
        if left: s.rect(uv, f, 0, 0, 1, fh, K[left])
        if right: s.rect(uv, f, fw - 1, 0, 1, fh, K[right])


def setpivot(m, name, p):
    for b in m.bones:
        if b["name"] == name: b["pivot"] = list(p)


@model
def old_wizard():
    """An old wizard in a tall purple hat with a brown band and a gold buckle, the tip bent over. Bushy
    white brows hide his eyes, a big nose sits over a long white beard, his purple robe is belted, he
    leans on a crooked staff topped with a glowing crystal and holds a heavy open spell book."""
    m = Model("old_wizard", "biped", 2.5)
    biped(m, hip=9, legx=2.6, neck=21, shoulder=19, armx=7)
    m.bone("hat", "head", (0, 31, 0))
    m.bone("staff", "armR", (-7.5, 9, 2))
    m.bone("book", "armL", (7.5, 10, 4))
    m.hold = {"staff": 0, "book": 50}
    m.bend = -55
    PU, PD, PS, BR, AU, SK, SD, WH, LG, BT, KK, WD, CR = ("purple_concrete", "purple_terracotta", "purple_wool", "brown_terracotta",
        "gold_block", "white_terracotta", "pink_terracotta", "white_concrete", "light_gray_concrete", "cyan_terracotta",
        "black_concrete", "dark_oak_planks", "light_blue_concrete")
    K = {"p": PU, "d": PD, "v": PS, "b": BR, "g": AU, "s": SK, "r": SD, "w": WH, "l": LG, "t": BT, "k": KK, "o": "orange_terracotta",
         "y": "yellow_concrete", "c": CR, "n": "brown_concrete"}
    s = Sheet(256, 256)

    # head: skin, white brows over small dark eyes, rosy cheeks, white hair at the sides and back
    hd = s.box(10, 9, 9, SK)
    s.draw(hd, "front", 0, 0, ["wwssssssww", "wwwwssswww", "wslwssswlw", "wskksskksw", "wrssssssrw", "wwssssssww",
                               "wwwssssww w".replace(" ", "w")[:10], "wwwwwwwwww", "wwwwwwwwww"], K)
    for f in ("left", "right"):
        s.draw(hd, f, 0, 0, ["sssssssss", "wwwwwwsss", "wwwwwwwss", "wwwwwwwss", "wwwwwwwws", "wwwwwwwws", "wwwwwwwww", "lwwwwwwww", "lllwwwwww"], K)
    s.draw(hd, "back", 0, 0, ["ssssssssss", "wwwwwwwwww", "wwwwwwwwww", "wwwwwwwwww", "wwwwwwwwww", "wwwwwwwwww", "wwwwwwwwww", "lwwwwwwwwl", "llwwwwwwll"], K)
    pb(m, s, "head", hd, (-5, 21, -4.5))
    nose = s.box(3, 4, 3, SK)
    s.draw(nose, "front", 0, 0, ["sss", "sss", "rsr", "rrr"], K)
    pb(m, s, "head", nose, (-1.5, 24.5, 4.5))
    # moustache and the long beard falling over the chest
    must = s.box(8, 2, 2, WH)
    s.draw(must, "front", 0, 0, ["wwwlwwww", "lw....wl"], K)
    pb(m, s, "head", must, (-4, 23.4, 4.7))
    beard = s.box(9, 11, 3, WH)
    s.draw(beard, "front", 0, 0, ["wwwwwwwww", "wwwwwwwww", "lwwlwwlww", "lwwlwwlwl", "lwwlwwlwl", "wwwlwwlwl", "wlwlwwwwl",
                                  ".lwwwlww.", ".lwwwlww.", "..wwwlw..", "...www..."], K)
    for f in ("left", "right"):
        s.draw(beard, f, 0, 0, ["www", "www", "www", "lww", "lww", "lww", "www", "www", "...", "...", "..."], K)
    pb(m, s, "head", beard, (-4.5, 13.5, 3.6))

    # hat: a wide dark brim, a crown with a brown band and gold buckle, then two tilted tiers and the tip
    brim = s.box(17, 1, 17, PU, top=PU)
    pb(m, s, "hat", brim, (-8.5, 29.6, -8.5))
    crown = s.box(11, 6, 11, PU)
    for f in ("front", "back", "left", "right"):
        s.draw(crown, f, 0, 0, ["...........", "...........", "...........", "bbbbbbbbbbb", "nnnnnnnnnnn", "ddddddddddd"], K)
    s.draw(crown, "front", 4, 2, ["ggg", "gog", "ggg"], K)
    pb(m, s, "hat", crown, (-5.5, 30.6, -5.5))
    t2 = s.box(8, 5, 8, PU)
    for f in ("front", "back", "left", "right"):
        s.draw(t2, f, 0, 0, ["........", "........", "........", "........", "dddddddd"], K)
    pb(m, s, "hat", t2, (-4, 35.5, -4.5), rot=(-12, 0, 0), origin=(0, 35.5, 0))
    t3 = s.box(5, 4, 5, PU)
    for f in ("front", "back", "left", "right"):
        s.draw(t3, f, 0, 0, [".....", ".....", ".....", "ddddd"], K)
    pb(m, s, "hat", t3, (-2.5, 39.5, -6.5), rot=(-35, 0, 0), origin=(0, 39.5, -4))
    m.c("hat", PD, (0, 42.6, -10.2), (3, 3, 3), (-70, 0, 0), (0, 41.5, -8.5))

    # robe: purple with a darker hem, a brown belt with a gold buckle, and a fold down the front
    robe = s.box(10, 11, 7, PU)
    s.draw(robe, "front", 0, 0, ["dddwwwwddd", "....ww....", "....ww....", ".....d....", ".....d....", "bbbbbbbbbb", "nnnnggnnnn",
                                 "....gg....", ".....d....", ".....d....", "dddddddddd"], K)
    s.draw(robe, "back", 0, 0, ["dddddddddd", "..........", "..........", "..........", "..........", "bbbbbbbbbb", "nnnnnnnnnn",
                                "..........", "..........", "..........", "dddddddddd"], K)
    for f in ("left", "right"):
        s.draw(robe, f, 0, 0, ["ddddddd", ".......", ".......", ".......", ".......", "bbbbbbb", "nnnnnnn", ".......", ".......", ".......", "ddddddd"], K)
    pb(m, s, "body", robe, (-5, 10, -3.5))
    skirt = s.box(11, 4, 8, PU)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(skirt, f)
        s.draw(skirt, f, 0, 0, ["." * fw, "." * fw, "." * fw, "d" * fw], K)
    pb(m, s, "body", skirt, (-5.5, 7, -4))

    # legs and old teal boots
    for side, leg in ((1, "legL"), (-1, "legR")):
        lg = s.box(4, 5, 4, "blue_terracotta")
        pb(m, s, leg, lg, (side * 2.6 - 2, 2.2, -2))
        bt = s.box(4, 3, 6, BT)
        s.draw(bt, "front", 0, 0, ["kkkk", "....", "kkkk"], K)
        for f in ("left", "right"):
            s.draw(bt, f, 0, 0, ["kkkkkk", "......", "kkkkkk"], K)
        pb(m, s, leg, bt, (side * 2.6 - 2, 0, -2.4))

    # arms: wide sleeves with a dark cuff, old hands
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 7.5
        sl = s.box(4, 10, 5, PU)
        for f in ("front", "back", "left", "right"):
            fu, fv, fw, fh = s.face(sl, f)
            s.draw(sl, f, 0, 0, ["." * fw] * 7 + ["d" * fw, "b" * fw, "d" * fw], K)
        pb(m, s, arm, sl, (x - 2, 10.5, -2.5))
        hand = s.box(3, 3, 3, SK)
        s.draw(hand, "front", 0, 0, ["sss", "rsr", "rrr"], K)
        pb(m, s, arm, hand, (x - 1.5, 8, -1.5))

    # the staff: crooked dark wood with bands, a claw holding a glowing crystal
    sx, sz = -7.5, 2
    m.c("staff", BR, (sx, 15, sz), (1.4, 30, 1.4))
    for y in (6, 19, 26):
        m.c("staff", "red_terracotta", (sx, y, sz), (1.8, 1.4, 1.8))
    m.c("staff", BR, (sx + 0.8, 30.8, sz), (1.2, 3, 1.2), (0, 0, -30))
    m.c("staff", BR, (sx - 0.8, 30.8, sz), (1.2, 3, 1.2), (0, 0, 30))
    m.c("staff", CR, (sx, 32.5, sz), (2.6, 2.6, 2.6), (45, 45, 0), light=True)
    m.c("staff", WH, (sx, 32.5, sz), (1.2, 1.2, 3.0), (45, 45, 0), light=True)
    m.c("staff", BR, (sx, 0.6, sz), (1.8, 1.2, 1.8))

    # the open spell book: two covers, cream pages with lines of writing, gold corners
    bx, by, bz = 7.5, 10, 7.5
    for sgn in (1, -1):
        m.c("book", "red_terracotta", (bx + sgn * 2.6, by, bz), (5.2, 0.5, 7), (0, 0, sgn * 14), (bx, by, bz))
        pg = s.box(5, 1, 6, "white_wool")
        s.draw(pg, "top", 0, 0, [".....", ".lll.", ".....", ".ll..", ".....", ".lll."], K)
        pb(m, s, "book", pg, (bx + (0 if sgn > 0 else -5), by + 0.25, bz - 3), rot=(0, 0, sgn * 14), origin=(bx, by, bz))
        for dz in (-3.3, 3.3):
            m.c("book", AU, (bx + sgn * 4.9, by + 0.6 + 0.6, bz + dz), (0.8, 0.6, 0.8), (0, 0, sgn * 14), (bx, by, bz))
    m.c("book", "orange_concrete", (bx, by + 2.4, bz), (0.8, 0.8, 0.8), (45, 45, 0), light=True)
    m.attacks = {"spells": "cast", "blink": "sweep", "summon": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


@model
def hollow_mage():
    """A small shadow-faced mage under a huge battered straw hat with a green band and a crumpled crown
    folding forward. Under the brim there is only darkness and two glowing yellow eyes. A tall-collared
    blue coat with crossed leather straps and a pale blue buckle, white sleeves with a green stripe,
    striped trousers, big brown shoes, and a bent wooden staff."""
    m = Model("hollow_mage", "biped", 2.7)
    biped(m, hip=7, legx=2.2, neck=19, shoulder=17, armx=7)
    m.bone("hat", "head", (0, 27, 0))
    m.bone("staff", "armR", (-7.5, 7, 2))
    m.hold = {"staff": 30}
    m.bend = -45
    YE, YT, YD, GR, GD, BK, YL, BL, BD, LB, BR, WH, WG, SH, ST = ("yellow_terracotta", "yellow_concrete", "orange_terracotta", "lime_concrete",
        "green_concrete", "black_concrete", "yellow_concrete", "blue_concrete", "blue_terracotta", "light_blue_concrete", "brown_terracotta",
        "white_concrete", "lime_terracotta", "brown_concrete", "terracotta")
    K = {"y": "sandstone_x", "Y": YE, "o": YD, "g": GR, "G": GD, "k": BK, "e": YL, "b": BL, "B": BD, "l": LB, "r": BR, "w": WH,
         "s": SH, "t": ST, "c": "cyan_concrete", "n": "light_gray_concrete", "p": "purple_concrete"}
    K["y"] = "smooth_sandstone"
    s = Sheet(256, 256)

    # face: a dark void with glowing eyes and a faint purple glow round the bottom
    hd = s.box(9, 8, 8, BK)
    s.draw(hd, "front", 0, 0, [".........", ".........", "..e...e..", "..e...e..", "..o...o..", ".........", ".........", "........."], K)
    pb(m, s, "head", hd, (-4.5, 19, -4), lit={YL, YD})

    # the straw hat: a huge brim, a green band, a crumpled crown folding forward
    brim = s.box(22, 1, 22, "bamboo_planks", top="bamboo_planks")
    rows = []
    for y in range(22):
        r = ""
        for x in range(22):
            d = max(abs(x - 10.5), abs(y - 10.5))
            r += "Y" if d > 10 else "."
        rows.append(r)
    s.draw(brim, "top", 0, 0, rows, K)
    pb(m, s, "hat", brim, (-11, 26.5, -11))
    band = s.box(11, 2, 11, GD)
    for f in ("front", "back", "left", "right"):
        s.draw(band, f, 0, 0, ["ggggggggggg", "..........."], K)
    pb(m, s, "hat", band, (-5.5, 27.5, -5.5))
    cr = s.box(10, 7, 10, "bamboo_planks")
    for f in ("front", "back", "left", "right"):
        s.draw(cr, f, 0, 0, ["..........", "..........", "..........", "..........", "..........", "..........", "YYYYYYYYYY"], K)
    pb(m, s, "hat", cr, (-5, 29.5, -5))
    top = s.box(8, 5, 8, "bamboo_planks")
    for f in ("front", "back", "left", "right"):
        s.draw(top, f, 0, 0, ["........", "........", "........", "........", "YYYYYYYY"], K)
    pb(m, s, "hat", top, (-4, 35.5, -3), rot=(28, 0, 6), origin=(0, 35.5, 1))
    m.c("hat", "bamboo_planks", (0.6, 39.6, 5), (5, 4, 5), (60, 0, 10), (0, 38.5, 3))

    # coat: tall collar, crossed straps, a pale blue buckle, a dark open front
    coat = s.box(12, 11, 8, BL)
    s.draw(coat, "front", 0, 0, ["bbbbbBBbbbbb", "..r......r..", "...r....r...", "....r..r....", ".....rr.....", "....r..r....",
                                 "...r.kk.r...", "....lllll...", "....lkkl....", "....lllll...", "BBBBBkkBBBBB"], K)
    s.draw(coat, "back", 0, 0, ["bbbbbbbbbbbb", "............", "..r......r..", "...r....r...", "............", "............",
                                "............", "BBBBBBBBBBBB", "............", "............", "BBBBBBBBBBBB"], K)
    for f in ("left", "right"):
        s.draw(coat, f, 0, 0, ["bbbbbbbb", "........", "........", ".B......", "........", "........", "........", "BBBBBBBB",
                               "........", "........", "BBBBBBBB"], K)
    pb(m, s, "body", coat, (-6, 8, -4))
    for sgn in (1, -1):
        col = s.box(4, 5, 2, BL)
        s.draw(col, "front", 0, 0, ["bbbb", "....", "..B.", "....", "BBBB"], K)
        pb(m, s, "body", col, (sgn * 3.6 - 2, 18, 3.2), rot=(-12, 0, sgn * -14), origin=(sgn * 3.6, 18, 4))
        m.c("body", BL, (sgn * 5.2, 20, -1), (2, 5, 9), (0, 0, sgn * -12))
    # coat tails flaring out
    skirt = s.box(14, 4, 9, BL)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(skirt, f)
        s.draw(skirt, f, 0, 0, ["." * fw, "." * fw, "B" * fw, "B" * fw], K)
    s.draw(skirt, "front", 6, 0, ["kk", "kk", "kk", "kk"], K)
    pb(m, s, "body", skirt, (-7, 5, -4.5))

    # striped trousers and big shoes
    for side, leg in ((1, "legL"), (-1, "legR")):
        x = side * 2.2
        lg = s.box(3, 4, 3, GD)
        for f in ("front", "back", "left", "right"):
            s.draw(lg, f, 0, 0, ["w.w", "w.w", "w.w", "w.w"], K)
        pb(m, s, leg, lg, (x - 1.5, 2, -1.5))
        sh = s.box(4, 2, 6, SH)
        s.draw(sh, "front", 0, 0, ["tttt", "rrrr"], K)
        s.draw(sh, "top", 0, 0, ["....", "....", "....", "....", "tttt", "tttt"], K)
        pb(m, s, leg, sh, (x - 2, 0, -2))

    # arms: white sleeves with a green stripe at the cuff
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 7.5
        sl = s.box(4, 9, 4, BL)
        pb(m, s, arm, sl, (x - 2, 9.5, -2))
        cf = s.box(5, 3, 5, WH)
        for f in ("front", "back", "left", "right"):
            s.draw(cf, f, 0, 0, ["ggggg", ".....", "nnnnn"], K)
        pb(m, s, arm, cf, (x - 2.5, 7, -2.5))
        m.c(arm, BK, (x, 6.2, 0), (2.4, 1.6, 2.4))

    # a bent wooden staff with a wrapped grip
    sx, sz = -7.5, 2
    limb(m, "staff", BR, (sx, 0, sz + 2), [(10, 1.4, (-8, 0, 0)), (10, 1.4, (4, 0, 0)), (7, 1.4, (30, 0, 0))])
    m.c("staff", "white_wool", (sx, 7, sz + 1.4), (1.8, 2.6, 1.8))
    m.c("staff", GR, (sx, 6.5, sz + 1.4), (1.9, 0.6, 1.9))
    m.c("staff", YL, (sx, 26.2, sz + 6), (1.6, 1.6, 1.6), (45, 45, 0), light=True)
    m.attacks = {"spells": "cast", "fire": "roar", "blink": "sweep", "slam": "slam"}
    m.melee = "swipe"
    return m


@model
def horned_brute():
    """A squat mountain brute: a huge boxy tan body with mottled hide, a heavy head with thick dark brows,
    a long striped snout, two stubby white tusks and great curled black horns. Long arms hang to the
    ground, a ragged hide loincloth hangs in strips and he drags an iron-headed spear."""
    m = Model("horned_brute", "biped", 2.6)
    biped(m, hip=6, legx=5, neck=20, shoulder=19, armx=13)
    m.bone("horns", "head", (0, 29, 2))
    m.bone("spear", "armR", (-13, 3, 3))
    m.hold = {"spear": 0}
    m.bend = -30
    L, M, D, B, X, W, H, H2, IR, IG = ("stripped_birch_log", "stripped_oak_log", "stripped_spruce_log", "brown_terracotta",
        "dark_oak_planks", "white_concrete", "blackstone", "black_wool", "iron_block", "light_gray_concrete")
    K = {"l": L, "m": M, "d": D, "b": B, "x": X, "w": W, "h": H, "k": H2, "i": IR, "g": IG, "e": "black_concrete",
         "s": "smooth_stone", "y": "yellow_concrete"}
    s = Sheet(256, 256)

    # the body: a big tan block with lighter chest plates, a belly band, a navel and dark hide patches
    bd = s.box(22, 16, 14, M)
    s.draw(bd, "front", 0, 0, [
        "mmmmmmmmmmmmmmmmmmmmmm",
        "mllllllmmmbmmmlllllllm",
        "mllllllldmbmdllllllllm",
        "mllllllldmbmdllllllllm",
        "mllllllmmmbmmmlllllllm",
        "mmmmmmmmmmmmmmmmmmmmmm",
        "mmmmmmmmmmmmmmmmmmmmmm",
        "mmllllllllllllllllllmm",
        "mmllllllllllllllllllmm",
        "mmllllllllbbllllllllmm",
        "mmmmmmmmmmmmmmmmmmmmmm",
        "dddddddddddddddddddddd",
        "dddddddddddddddddddddd",
        "bbbbbbbbbbbbbbbbbbbbbb"], K)
    for f in ("left", "right", "back"):
        fu, fv, fw, fh = s.face(bd, f)
        s.rect(bd, f, 0, 1, fw, 3, L)
        s.rect(bd, f, 0, fh - 3, fw, 2, D); s.rect(bd, f, 0, fh - 1, fw, 1, B)
    s.draw(bd, "top", 0, 0, ["l" * 22] * 14, K)
    pb(m, s, "body", bd, (-11, 5, -7))
    # loincloth strips hanging under the belly
    for i, (x, L2) in enumerate(((-8, 5), (-5, 7), (-2, 6), (1, 7), (4, 5), (7, 6))):
        st = s.box(2, L2, 1, B)
        s.draw(st, "front", 0, 0, ["dd", "bb"] + ["xb" if i % 2 else "bx"] * (L2 - 3) + ["xx"], K)
        pb(m, s, "body", st, (x, 6 - L2, 6.4), rot=(-6 + i % 3 * 4, 0, 0), origin=(x, 6, 6.5))
    for x in (-9, -3, 3, 8):
        m.c("body", B, (x, 2.5, -6.8), (2, 6, 0.8))

    # short heavy legs and wide feet
    for side, leg in ((1, "legL"), (-1, "legR")):
        x = side * 5
        lg = s.box(6, 6, 6, D)
        for f in ("front", "back", "left", "right"):
            s.rect(lg, f, 0, 1, 6, 3, M)
        pb(m, s, leg, lg, (x - 3, 1, -3))
        ft = s.box(7, 2, 8, B)
        s.draw(ft, "front", 0, 0, [".......", "xxxxxxx"], K)
        pb(m, s, leg, ft, (x - 3.5, 0, -3))
        for t in (-2, 0, 2):
            m.c(leg, "black_concrete", (x + t, 0.5, 5.2), (1.2, 1, 0.8))

    # long arms hanging nearly to the ground, with big hands
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 14
        sh = s.box(7, 7, 8, M, top=L)
        for f in ("front", "back", "left", "right"):
            fu, fv, fw, fh = s.face(sh, f)
            s.rect(sh, f, 0, 1, fw, 3, L); s.rect(sh, f, 0, fh - 1, fw, 1, D)
        pb(m, s, arm, sh, (x - 3.5, 14, -4))
        ar = s.box(6, 10, 6, M)
        for f in ("front", "back", "left", "right"):
            s.rect(ar, f, 1, 1, 3, 4, L); s.rect(ar, f, 0, 7, 6, 3, D)
        pb(m, s, arm, ar, (x - 3, 4, -3))
        hd = s.box(7, 4, 7, D)
        s.draw(hd, "front", 0, 0, [".......", ".......", ".......", "bebebeb"], K)
        pb(m, s, arm, hd, (x - 3.5, 0.5, -3.5))
        # leather wrap at the wrist
        m.c(arm, B, (x, 5, 0), (6.6, 1.4, 6.6))

    # the head: a heavy tan block pushed forward, brows, eyes, a long striped snout, tusks and ears
    hz = 3
    hd = s.box(12, 10, 10, M)
    s.draw(hd, "front", 0, 0, [
        "mmllllllllmm",
        "mllllllllllm",
        "xxxxxlxxxxxm",
        "xxxxxlxxxxxx",
        "eewmmmmmmwee",
        "mmmmmmmmmmmm",
        "lmmmmmmmmmml",
        "mmmmmmmmmmmm",
        "dmmmmmmmmmmd",
        "ddmmmmmmmmdd"], K)
    for f in ("left", "right", "back"):
        fu, fv, fw, fh = s.face(hd, f)
        s.rect(hd, f, 0, 1, fw, 2, L); s.rect(hd, f, 0, fh - 2, fw, 2, D)
    s.draw(hd, "top", 0, 0, ["llllllllllll"] * 10, K)
    pb(m, s, "head", hd, (-6, 20.5, -5 + hz))
    # thick brows sticking out
    for side in (1, -1):
        br = s.box(5, 2, 3, X)
        s.draw(br, "front", 0, 0, ["bbbbb", "xxxxx"], K)
        pb(m, s, "head", br, (side * 3.2 - 2.5, 26, 4.6 + hz), rot=(0, 0, side * -8), origin=(side * 3.2, 27, 5 + hz))
    # the snout: a striped column running down the face
    sn = s.box(4, 8, 3, D)
    s.draw(sn, "front", 0, 0, ["dddd", "bbbb", "dddd", "dddd", "bbbb", "dddd", "dddd", "bbbb"], K)
    s.draw(sn, "bottom", 0, 0, ["bxxb", "bxxb", "bbbb"], K)
    pb(m, s, "head", sn, (-2, 18.5, 5 + hz))
    # tusks
    for side in (1, -1):
        tk = s.box(2, 4, 2, W)
        s.draw(tk, "front", 0, 0, ["ww", "ww", "gg", "gw"], K)
        pb(m, s, "head", tk, (side * 3.8 - 1, 20.5, 5 + hz), rot=(-10, 0, side * -6), origin=(side * 3.8, 20.5, 6 + hz))
    # floppy ears
    for side in (1, -1):
        er = s.box(2, 6, 4, M)
        s.draw(er, "left" if side > 0 else "right", 0, 0, ["mmmm", "mddm", "mddm", "mddm", "mbbm", "dddd"], K)
        pb(m, s, "head", er, (side * 6.8 - 1, 22, -1 + hz), rot=(0, 0, side * -25), origin=(side * 6, 28, 1 + hz))
    # curled horns: out sideways, then up, with ribbed segments
    for side in (1, -1):
        base = s.box(6, 4, 4, H)
        for f in ("front", "back", "top", "bottom"):
            fu, fv, fw, fh = s.face(base, f)
            for i in range(0, fw, 2): s.rect(base, f, i, 0, 1, fh, H2)
        pb(m, s, "horns", base, (side * 8.5 - 3, 27.5, 0 + hz - 2))
        up = s.box(5, 9, 5, H)
        for f in ("front", "back", "left", "right"):
            s.draw(up, f, 0, 0, ["kkkkk", "hhhhh", "hhhhh", "kkkkk", "hhhhh", "hhhhh", "kkkkk", "hhhhh", "ggggg".replace("g", "h")], K)
        pb(m, s, "horns", up, (side * 12.5 - 2.5, 27, 0 + hz - 2.5), rot=(0, 0, side * -8), origin=(side * 12.5, 27, hz))
        tip = s.box(4, 4, 4, H2)
        pb(m, s, "horns", tip, (side * 12 - 2, 35.5, hz - 3), rot=(-25, 0, side * 20), origin=(side * 12.5, 35.5, hz - 1))
        tip2 = s.box(2, 3, 3, H2)
        pb(m, s, "horns", tip2, (side * 11 - 1, 38.5, hz - 4.5), rot=(-40, 0, side * 40), origin=(side * 11.5, 38.5, hz - 3))
        # gold ring on each horn
        m.c("horns", "gold_block", (side * 12.6, 30.5, hz), (5.6, 1, 5.6), (0, 0, side * -8))
    # a bone necklace round the neck
    for k in range(9):
        a = math.pi * (0.1 + 0.8 * k / 8)
        m.c("body", W if k % 2 else "bone_block", (-8.5 * math.cos(a), 20.2 - 2.2 * math.sin(a), 6.8 + 1.2 * math.sin(a)), (1.4, 2.2, 1.2),
            (0, 0, math.degrees(a) - 90))

    # the spear: a long wooden shaft, wrapped grip, a stone-and-iron head and a tuft of feathers
    sx, sz = -14, 3
    limb(m, "spear", "stripped_spruce_log", (sx, -3, sz - 14), [(34, 1.4, (65, 0, 0))])
    for t in (12, 15):
        d = math.radians(65)
        m.c("spear", B, (sx, -3 + math.cos(d) * t, sz - 14 + math.sin(d) * t), (1.9, 1.2, 1.9), (65, 0, 0))
    hx, hy, hz2 = sx, -3 + math.cos(math.radians(65)) * 34, sz - 14 + math.sin(math.radians(65)) * 34
    m.c("spear", IR, (hx, hy + 0.4, hz2 + 1), (2.6, 2.6, 2.6), (65, 0, 0))
    m.c("spear", IG, (hx, hy + 2.4, hz2 + 5), (0.6, 3.2, 7), (65, 0, 0))
    m.c("spear", "light_gray_concrete", (hx, hy + 2.4, hz2 + 5), (3.2, 0.6, 7), (65, 0, 0))
    m.c("spear", IR, (hx, hy + 3.3, hz2 + 8.5), (1.6, 1.6, 2), (65, 0, 0))
    for k, c in enumerate(("red_concrete", "white_concrete", "red_concrete")):
        m.c("spear", c, (hx + (k - 1) * 0.9, hy - 1.5, hz2 - 1.2), (0.6, 3.5, 0.6), (20 + k * 10, 0, (k - 1) * 25))
    m.attacks = {"slam": "slam", "charge": "lunge", "toss": "sweep", "roar": "roar", "stomp": "stomp"}
    m.melee = "swipe"
    return m


@model
def rotting_giant():
    """A towering rotting giant: a small green head with sunken black eyes on a broad body, a torn cyan
    shirt stained with moss and rot, ragged purple trousers torn off at the knee, and long gangly green
    arms and legs. Flies and a rot cloud hang round him."""
    m = Model("rotting_giant", "biped", 2.6)
    biped(m, hip=22, legx=4.5, neck=37, shoulder=35, armx=11)
    SK, SD, SG, LB, CY, CD, PL, PB, PD, KK = ("lime_terracotta", "green_terracotta", "green_wool", "light_blue_wool", "cyan_wool",
        "cyan_concrete", "purple_wool", "blue_wool", "blue_concrete", "black_concrete")
    K = {"s": SK, "d": SD, "g": SG, "l": LB, "c": CY, "C": CD, "p": PL, "b": PB, "B": PD, "k": KK, "w": "white_terracotta"}
    s = Sheet(256, 256)

    # head
    hd = s.box(10, 10, 10, SK)
    s.draw(hd, "front", 0, 0, ["gggggggggg", "gsssssssgg", "ssssssssss", "ssssssssss", "skkksskkks", "sdddssddds",
                               "ssssddssss", "sssddddsss", "ssdsssssds", "gggssssggg"], K)
    for f in ("left", "right", "back"):
        s.rect(hd, f, 0, 0, 10, 2, SG); s.rect(hd, f, 0, 8, 10, 2, SD)
    s.draw(hd, "top", 0, 0, ["g" * 10] * 10, K)
    pb(m, s, "head", hd, (-5, 37, -5))

    # torso: torn cyan shirt with rot stains spreading from the collar, skin at the hem
    bd = s.box(18, 14, 9, CY)
    s.draw(bd, "front", 0, 0, [
        "llllllggggggllllll",
        "lllcgggggggggcclll",
        "cccccgggddgggccccc",
        "cccccgcgdggcgccccc",
        "ccccccgcccccgccccc",
        "ccccccgcccccgccccc",
        "cccccccccccccccccc",
        "cccccccccccccccccc",
        "cccccccccccccccccc",
        "cccccccccccccccccc",
        "CCCCCCCCCCCCCCCCCC",
        "CCsCCCCsCCCCsCCCCC",
        "sssssssssssssssss.",
        "ssssssssssssssssss"], K)
    for f in ("left", "right", "back"):
        fu, fv, fw, fh = s.face(bd, f)
        s.rect(bd, f, 0, 0, fw, 2, LB); s.rect(bd, f, 0, 10, fw, 2, CD); s.rect(bd, f, 0, 12, fw, 2, SK)
    s.draw(bd, "top", 0, 0, ["l" * 18] * 9, K)
    pb(m, s, "body", bd, (-9, 23, -4.5))

    # trousers: purple, torn at the knee in ragged teeth
    pt = s.box(18, 3, 9, PB)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(pt, f)
        s.rect(pt, f, 0, 0, fw, 1, PL); s.rect(pt, f, 0, fh - 1, fw, 1, PD)
    pb(m, s, "body", pt, (-9, 21, -4.5))
    for side, leg in ((1, "legL"), (-1, "legR")):
        x = side * 4.5
        th = s.box(8, 10, 8, PB)
        for f in ("front", "back", "left", "right"):
            s.draw(th, f, 0, 0, ["pppppppp", "........", "........", "........", "........", "........", "........", "BBBBBBBB", "sB.sBB.s", "ssBssBss"], K)
        pb(m, s, leg, th, (x - 4, 12, -4))
        sh = s.box(7, 12, 7, SK)
        for f in ("front", "back", "left", "right"):
            s.draw(sh, f, 0, 0, [".......", "...g...", "...g...", ".......", ".......", ".......", ".....g.", ".....g.", ".......", ".......", "ddddddd", "ddddddd"], K)
        pb(m, s, leg, sh, (x - 3.5, 0, -3.5))
        m.c(leg, SD, (x, 0.3, 4.2), (6, 0.6, 1.4))

    # long gangly arms with ragged sleeves
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 12.5
        sl = s.box(7, 7, 7, CY)
        for f in ("front", "back", "left", "right"):
            s.draw(sl, f, 0, 0, ["lllllll", ".......", "..g....", ".......", ".....g.", "CCCCCCC", "C.CC.CC"], K)
        s.draw(sl, "top", 0, 0, ["lllllll"] * 7, K)
        pb(m, s, arm, sl, (x - 3.5, 29, -3.5))
        # long arms that hang almost to the ground, ending in plain fists (no fingers)
        ar = s.box(6, 28, 6, SK)
        for f in ("front", "back", "left", "right"):
            s.rect(ar, f, 1, 3, 1, 4, SG); s.rect(ar, f, 4, 11, 1, 5, SG); s.rect(ar, f, 0, 24, 6, 4, SD)
        pb(m, s, arm, ar, (x - 3, 2, -3))

    # a dark rot drip down the chest and a few flies (lit specks of black)
    for i, (x, y, z) in enumerate(((-7, 49, 4), (6, 52, -3), (0, 54, 5), (-3, 47, -6), (8, 46, 2))):
        m.c("head", KK, (x, y, z), (0.6, 0.6, 0.6))
    m.attacks = {"slam": "slam", "stomp": "stomp", "charge": "lunge", "roar": "roar", "toss": "sweep"}
    m.melee = "swipe"
    return m


@model
def dusk_scorpion():
    """A giant slate-purple scorpion: a long plated body with glowing red eye clusters, two heavy pincers
    held forward, ragged fins along its sides, eight thin legs, and a segmented tail that arches right
    over its back to a blocky stinger."""
    from models import mlimb
    m = Model("dusk_scorpion", "spider", 2.4)
    m.bone("body", "root", (0, 9, 0))
    m.bone("abdomen", "body", (0, 11, -12))
    m.bone("head", "body", (0, 9, 10))
    m.bone("fangL", "head", (6, 8, 13))
    m.bone("fangR", "head", (-6, 8, 13))
    P, D, L, KK, R = "polished_blackstone", "blackstone", "polished_deepslate", "black_concrete", "red_concrete"
    K = {"p": P, "d": D, "l": L, "k": KK, "r": R, "o": "orange_concrete"}
    s = Sheet(256, 256)

    # body: three plated segments, each with a lighter top edge and a dark seam
    for i, (z, w) in enumerate(((2, 14), (-6, 15), (-14, 13))):
        seg = s.box(w, 7, 8, P)
        for f in ("front", "back", "left", "right"):
            fu, fv, fw, fh = s.face(seg, f)
            s.rect(seg, f, 0, 0, fw, 1, L); s.rect(seg, f, 0, fh - 1, fw, 1, KK)
        s.draw(seg, "top", 0, 0, ["l" * w, "p" * w, "p" * w, "p" * w, "p" * w, "p" * w, "p" * w, "k" * w], K)
        pb(m, s, "body" if i < 2 else "abdomen", seg, (-w / 2, 6.5, z - 4))
    # head with the red eye clusters
    hd = s.box(12, 6, 7, P)
    s.draw(hd, "front", 0, 0, ["llllllllllll", "prpprppprppr", "rrpprrrpprrp", "pppppppppppp", "pkpkpkpkpkpk", "kkkkkkkkkkkk"], K)
    s.draw(hd, "top", 0, 0, ["pppppppppppp", "pprrpppprrpp", "pporppproppp", "pppppppppppp", "llllllllllll", "pppppppppppp", "kkkkkkkkkkkk"], K)
    pb(m, s, "head", hd, (-6, 6, 6), lit={R, "orange_concrete"})
    # mouth parts
    for sx in (1, -1):
        m.c("head", D, (sx * 2, 6.5, 13.6), (1.6, 2.6, 1.6), (20, 0, 0))

    # pincers: an arm out from the head, a big claw block with two jaws
    for sx, b in ((1, "fangL"), (-1, "fangR")):
        limb(m, b, P, (sx * 6, 8, 11), [(7, 2.6, (-80, 0, -20 * sx)), (5, 2.6, (-100, 0, 30 * sx))], joint=D)
        cx, cz = sx * 8, 23
        cl = s.box(6, 5, 7, P)
        for f in ("front", "back", "left", "right"):
            fu, fv, fw, fh = s.face(cl, f)
            s.rect(cl, f, 0, 0, fw, 1, L); s.rect(cl, f, 0, fh - 1, fw, 1, KK)
        pb(m, s, b, cl, (cx - 3, 5.5, cz - 3.5))
        jw = s.box(3, 3, 7, P)
        s.draw(jw, "front", 0, 0, ["lll", "ppp", "kkk"], K)
        pb(m, s, b, jw, (cx + sx * 0.5 - 1.5, 7.2, cz + 3.4), rot=(0, sx * -10, 0), origin=(cx, 8, cz + 3.4))
        jw2 = s.box(3, 2, 6, D)
        pb(m, s, b, jw2, (cx - sx * 1.5 - 1.5, 5.4, cz + 3.4), rot=(0, sx * 12, 0), origin=(cx, 6, cz + 3.4))
        m.c(b, KK, (cx - sx * 0.2, 6.8, cz + 6.5), (1, 1, 3))

    # ragged fins along both sides of the back, taller in the middle
    for sx in (1, -1):
        for k, (z, h) in enumerate(((5, 4), (1, 6), (-3, 7), (-7, 6), (-11, 5), (-15, 4))):
            m.c("body" if z > -10 else "abdomen", P if k % 2 else D, (sx * 6.2, 13.5 + h / 2, z), (0.5, h, 3), (sx * -10, 0, sx * -25))

    # eight thin jointed legs
    zs = {1: 5, 2: 1, 3: -4, 4: -9}
    fan = {1: 30, 2: 10, 3: -12, 4: -32}
    for i in (1, 2, 3, 4):
        m.bone(f"legL{i}", "body", (7, 9, zs[i]))
        m.bone(f"legR{i}", "body", (-7, 9, zs[i]))
        a = fan[i]
        mlimb(m, f"legL{i}", P, (7, 9, zs[i]), [(8, 1.4, (a, 0, -55)), (11, 1.2, (a * 0.5, 0, -160), D), (3, 0.8, (a * 0.3, 0, -178), KK)])

    # the tail: segments rising from the back of the abdomen, arching forward over the body
    x, y, z = 0, 11, -18
    segs = [(5, 5.5, 30), (5, 5, 10), (5, 4.6, -15), (5, 4.4, -40), (5, 4.2, -70), (4, 4, -100)]
    for k, (L2, t, a) in enumerate(segs):
        r = math.radians(a)
        dy, dz = math.cos(r), -math.sin(r) * -1
        dz = math.sin(r)
        cy, cz = y + dy * L2 / 2, z + dz * L2 / 2
        tl = s.box(round(t), L2, round(t), P)
        for f in ("front", "back", "left", "right"):
            fu, fv, fw, fh = s.face(tl, f)
            s.rect(tl, f, 0, 0, fw, 1, KK); s.rect(tl, f, 0, 1, fw, 1, L)
        pb(m, s, "abdomen", tl, (x - round(t) / 2, cy - L2 / 2, cz - round(t) / 2), rot=(a, 0, 0), origin=(x, cy, cz))
        y, z = y + dy * L2, z + dz * L2
    # the stinger: a heavy block, a dark bulb and a curved barb pointing down-forward, glowing tip
    sg = s.box(6, 6, 7, P)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(sg, f)
        s.rect(sg, f, 0, 0, fw, 1, L); s.rect(sg, f, 0, fh - 1, fw, 1, KK)
    pb(m, s, "abdomen", sg, (-3, y - 3, z - 1), rot=(-20, 0, 0), origin=(0, y, z + 2))
    limb(m, "abdomen", D, (0, y - 2, z + 5), [(3, 1.6, (120, 0, 0)), (3, 1.1, (160, 0, 0), KK)])
    m.c("abdomen", R, (0, y - 6.5, z + 7), (0.8, 0.8, 0.8), light=True)
    m.attacks = {"sting": "fang", "charge": "fang", "slam": "fang"}
    m.melee = "fang"
    return m
