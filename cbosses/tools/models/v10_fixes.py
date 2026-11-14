"""v10: redone bosses. Grand Augur after ref38, Old Ironroot as the mossy golem of ref39, a human Mayor
Grumble with real legs and planted feet, a properly painted Shulker Matriarch, extra detail on the Hollow
Mage and King Gloop, and Mossback trimmed to about 250 blocks so it costs less to draw."""
import math
import random
from models import model, biped, limb
from build import Model
from texpaint import Sheet
from v9_minis import bx, pb
import v7_bigs
import v2_general
import v6_originals


def speckle(s, uv, faces, picks, seed, rate):
    """Scatter single pixels of the given blocks over faces: picks = [(block, weight)]."""
    rnd = random.Random(seed)
    tot = sum(w for _, w in picks)
    for f in faces:
        fu, fv, fw, fh = s.face(uv, f)
        for y in range(fh):
            for x in range(fw):
                if rnd.random() > rate: continue
                r = rnd.random() * tot
                for b, w in picks:
                    r -= w
                    if r <= 0:
                        s.put(fu + x, fv + y, b)
                        break


def vines(s, uv, faces, seed, cover, flowers=0.05, top_bias=1.0):
    """Moss that grows down from the top of each face in wandering strands, with dandelions."""
    rnd = random.Random(seed)
    for f in faces:
        fu, fv, fw, fh = s.face(uv, f)
        if f == "top":
            for y in range(fh):
                for x in range(fw):
                    if rnd.random() < cover:
                        s.put(fu + x, fv + y, rnd.choice(("moss_block", "moss_block", "green_terracotta")))
            continue
        n = max(1, int(fw * cover / 2))
        for _ in range(n):
            x = rnd.randrange(max(1, fw - 1))
            ln = int(fh * min(1.0, rnd.random() * top_bias + 0.3))
            for y in range(ln):
                for dx in (0, 1):
                    if x + dx < fw: s.put(fu + x + dx, fv + y, "moss_block" if rnd.random() < 0.8 else "green_terracotta")
                if rnd.random() < 0.2:
                    for dx in (-1, 2):
                        if 0 <= x + dx < fw: s.put(fu + x + dx, fv + y, "moss_block")
                if rnd.random() < 0.2: x = max(0, min(fw - 2, x + rnd.choice((-1, 1))))
            if rnd.random() < flowers * 8 and ln > 2:
                yy = rnd.randrange(ln - 1)
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    if x + dx < fw: s.put(fu + x + dx, fv + yy + dy, "yellow_concrete")


# ============================================================================================ Grand Augur
@model
def grand_augur():
    """The illager arch-sorcerer of ref38: a huge grey illager head with a hard black unibrow and a long
    nose, a tall open gold crown with a red and a blue gem, a blue coat with gold trim over a dark green
    tunic, a ruby amulet, big square gold cuffs, red pointed shoes, and a grey staff banded in red with a
    glowing gold crystal floating at its tip."""
    m = Model("grand_augur", "biped", 1.9)
    biped(m, hip=8, legx=2.2, neck=19.5, shoulder=18, armx=6.4)
    m.bone("crown", "head", (0, 30, 0.5))
    m.bone("staff", "armR", (-7, 9, 2))
    m.bone("gem", "staff", (-7, 36, 2))
    m.hold = {"staff": (0, 0, 30)}
    m.bend = -30
    m.rest("armR", (0, 0, -30))
    G, GL, GD, K_, W = "light_gray_concrete", "polished_andesite", "gray_concrete", "black_concrete", "white_concrete"
    BL, BD, AU, AD, GR, RD, RR, NS = "blue_concrete", "blue_terracotta", "gold_block", "orange_concrete", "green_terracotta", "red_concrete", "red_terracotta", "white_terracotta"
    K = {"g": G, "l": GL, "d": GD, "k": K_, "w": W, "b": BL, "B": BD, "a": AU, "o": AD, "t": GR, "r": RD, "R": RR, "n": NS,
         "c": "light_blue_concrete", "C": "cyan_concrete", "p": "pink_terracotta"}
    s = Sheet(256, 256)
    # legs: grey hose, gold ankle bands, red pointed shoes
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2.2
        bx(m, s, leg, (3, 7, 3), (x - 1.5, 1, -1.5), G, GL, GD)
        bx(m, s, leg, (3, 1, 3), (x - 1.5, 2, -1.5), AU, None, AD)
        bx(m, s, leg, (3, 1, 6), (x - 1.5, 0, -1.5), RD, None, RR, edge=False)
    # the coat skirt: blue panels split at the front over the dark tunic, gold edging
    bx(m, s, "hips", (10, 4, 7), (-5, 4, -3.5), BL, None, BD, front=["bbbaktttkabbb"[:10], "bbbattttabbb"[:10], "bbbattttabbb"[:10], "aaaattttaaaa"[:10]], K=K)
    bx(m, s, "hips", (10, 3, 7), (-5, 1.6, -3.5), BL, None, BD, front=["bbatttttab", "bbatttttab", "aaaaaaaaaa"], side=["bbbbbbb", "bbbbbbb", "aaaaaaa"], K=K)
    # chest
    bx(m, s, "body", (9, 10, 6), (-4.5, 8, -3), BL, None, BD, front=[
        "bbbakkabbb"[:9], "bbattttabb"[:9], "bbattttab", "bbattttab", "bbattttab", "bbattttab", "aaaaaaaaa", "BBBBBBBBB", "bbattttab", "bbattttab"], back=[
        "bbbbbbbbb", "bbbbbbbbb", "bbbbabbbb", "bbbbabbbb", "bbbbabbbb", "bbbbabbbb", "aaaaaaaaa", "BBBBBBBBB", "bbbbbbbbb", "bbbbbbbbb"], K=K)
    # collar fans up behind the head, the ruby amulet on a gold plate
    for sd in (1, -1):
        bx(m, s, "body", (3, 3, 1), (sd * 2.6 - 1.5, 17.4, 2.2), AU, None, AD, rot=(0, 18 * sd, -22 * sd), origin=(sd * 2.6, 17.4, 2.7))
    bx(m, s, "body", (8, 3, 1), (-4, 17.6, -3.4), AU, None, AD)
    bx(m, s, "body", (3, 3, 1), (-1.5, 13, 3), AU, None, AD, front=["aaa", "ara", "aRa"], K=K)
    m.c("body", RD, (0, 14.2, 3.7), (1.4, 1.4, 0.5), light=True)
    # arms: blue sleeves, gold square cuffs, grey hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        ax = sd * 6.4
        bx(m, s, arm, (3, 7, 3), (ax - 1.5, 11, -1.5), BL, None, BD)
        bx(m, s, arm, (5, 3, 5), (ax - 2.5, 9, -2.5), AU, None, AD, front=["aaaaa", "a...a", "aaaaa"], side=["aaaaa", "a...a", "aaaaa"], K=K)
        m.c(arm, BD, (ax, 10.5, 0), (3.6, 1.2, 3.6))
        bx(m, s, arm, (2, 3, 2), (ax - 1, 6.6, -1), G, None, GD)
    # head: big, grey, an angry black unibrow, white and black eyes, long nose
    bx(m, s, "head", (10, 9, 9), (-5, 19.5, -4.5), G, GL, GD, K=K, front=[
        "glllllllll", "gggggggggg", "kkkgggkkkg"[::-1][:10], "gkkkggkkkg", "gwkkggkkwg", "gwkggggkwg", "gggggggggg", "gggggggggg", "dddddddddd"],
        side=["lllllllll", "ggggggggg", "ggggdgggg", "ggggggggg", "gggggggdg", "ggggggggg", "ggggggggg", "ggggggggg", "ddddddddd"], back=[
        "llllllllll", "gggggggggg", "gggggggggg", "ggggdggggg", "gggggggggg", "gggggggggg", "gggdgggggg", "gggggggggg", "dddddddddd"])
    bx(m, s, "head", (2, 5, 2), (-1, 20.8, 4.4), "white_terracotta", None, "light_gray_concrete")
    bx(m, s, "head", (10, 1, 2), (-5, 24.6, 4.3), K_, None, None, edge=False)
    # crown: a tall open gold tube with notched points, a red and a blue gem
    for sd in (1, -1):
        bx(m, s, "crown", (1, 14, 5), (sd * 2.5 - 0.5, 28.5, -2), AU, None, AD, edge=False)
    bx(m, s, "crown", (5, 14, 1), (-2.5, 28.5, 2.5), AU, None, AD, front=[".....", ".aaa.", ".ooo.", ".aaa.", ".prr.", ".rRR.", ".rRR.", ".aaa.", ".aaa.", ".cCC.", ".cCC.", ".CCC.", ".aaa.", "....."], K=K)
    bx(m, s, "crown", (5, 14, 1), (-2.5, 28.5, -2.5), AU, None, AD)
    for x, z in ((-2.5, 2.5), (2.5, 2.5), (-2.5, -2.5), (2.5, -2.5), (0, 2.8), (0, -2.8)):
        m.c("crown", AD, (x, 43.3, z), (1.2, 1.8, 0.8), (0, 0, 8 if x >= 0 else -8))
    m.c("crown", RD, (0, 34.5, 3.2), (2.4, 2.4, 0.4), light=True)
    m.c("crown", "light_blue_concrete", (0, 38.6, 3.2), (2.4, 2.4, 0.4), light=True)
    # staff: grey shaft, two red bands, a gold butt and a cross bar, the crystal floats above
    limb(m, "staff", G, (-7, -4, 2), [(38, 1.4, (0, 0, 0))])
    for y in (16, 18, 22, 24):
        m.c("staff", RD if y in (16, 22) else RR, (-7, y, 2), (1.8, 2, 1.8))
    m.c("staff", AU, (-7, -3, 2), (1.8, 2, 1.8))
    m.c("staff", GL, (-7, 34.4, 2), (6, 1.2, 1.6))
    m.c("gem", AU, (-7, 38.5, 2), (4.2, 4.2, 4.2), (0, 45, 45), (-7, 38.5, 2), light=True)
    m.c("gem", "yellow_concrete", (-7, 38.5, 2), (2.6, 5.4, 2.6), (0, 45, 0), (-7, 38.5, 2), light=True)
    m.attacks = {"orbs": "cast", "volley": "cast", "minions": "roar", "blink": "sweep", "slam": "slam"}
    m.melee = "swipe"
    return m


# =========================================================================================== Old Ironroot
@model
def old_ironroot():
    """Ref39: an iron golem a hundred years in a meadow. Its plates have gone pale and rusty-pink at the
    seams, green vines run down every block with dandelions in them, its long arms are three stacked
    blocks with grey joints, and a sapling grows on its left shoulder."""
    m = Model("old_ironroot", "biped", 2.3)
    biped(m, hip=16, legx=4.5, neck=33, shoulder=33, armx=12)
    m.no_elbows = True
    W, WL, WT, LG, GY, PK, K_ = "white_concrete", "white_concrete_powder", "white_terracotta", "light_gray_concrete", "gray_concrete", "pink_terracotta", "black_concrete"
    S = Sheet(256, 256)
    iron = [(WT, 3), (LG, 2), (PK, 1)]

    def plate(bone, size, lo, seed, cover=0.3, joint=False, front=None, K=None):
        uv = S.box(*size, W if not joint else LG, top=W if not joint else LG, bottom=LG)
        if not joint:
            speckle(S, uv, ("front", "back", "left", "right", "top"), iron, seed, 0.0)
            vines(S, uv, ("front", "left", "right", "top"), seed + 7, cover * 0.6)
        else:
            speckle(S, uv, ("front", "back", "left", "right"), [(GY, 1)], seed, 0.4)
        if front: S.draw(uv, "front", 0, 0, front, K)
        pb(m, S, bone, uv, lo, speck=3, merge={PK: WT, LG: W})

    # legs: thigh, grey knee, shin, a pale flat foot
    for sd, leg, sh in ((1, "legL", 1), (-1, "legR", 2)):
        x = sd * 4.5
        plate(leg, (6, 6, 6), (x - 3, 10, -3), 10 + sh, 0.5)
        plate(leg, (5, 2, 5), (x - 2.5, 8, -2.5), 20 + sh, joint=True)
        plate(leg, (6, 6, 6), (x - 3, 2.2, -3), 30 + sh, 0.35)
        plate(leg, (7, 2, 8), (x - 3.5, 0, -3.5), 40 + sh, 0.0, front=["l.....l", "......."], K={"l": GY})
    # waist and chest
    plate("body", (9, 6, 6), (-4.5, 16, -3), 50, 0.45)
    plate("body", (18, 12, 11), (-9, 21, -5.5), 51, 0.45, front=[
        "..................", "..................", "....yy............", "...yooy...........", "...yooy...........", "....yy......y.....", "...........yoy....", "............y....."],
        K={"y": "yellow_concrete", "o": "orange_concrete"})
    # head: the golem's small head, long nose, red eyes, heavy brow
    plate("head", (8, 10, 8), (-4, 31, -0.5), 60, 0.1, front=[
        "........", "........", "kkkkkkkk", "rk....kr", "........", "........", "........", "........", "........", "........"],
        K={"k": GY, "r": "red_concrete"})
    bx(m, S, "head", (2, 4, 2), (-1, 31, 7.4), LG, None, GY)
    # arms: shoulder block, joint, forearm, joint, a big fist
    for sd, arm in ((1, "armL"), (-1, "armR")):
        ax = sd * 12
        plate(arm, (6, 9, 7), (ax - 3, 25, -3.5), 70 + sd, 0.6)
        plate(arm, (5, 2, 5), (ax - 2.5, 23, -2.5), 75 + sd, joint=True)
        plate(arm, (6, 9, 7), (ax - 3, 14, -3.5), 80 + sd, 0.35)
        plate(arm, (5, 2, 5), (ax - 2.5, 12, -2.5), 85 + sd, joint=True)
        plate(arm, (7, 8, 8), (ax - 3.5, 4, -4), 90 + sd, 0.2)
    # a sapling in a clump of moss on the left shoulder, a flower on the right
    bx(m, S, "armL", (6, 3, 6), (9, 34, -3), "moss_block", "lime_terracotta", "green_terracotta")
    limb(m, "armL", "dark_oak_log", (12, 37, 0), [(3, 1, (0, 0, -10)), (3, 0.8, (0, 0, 20))])
    bx(m, S, "armL", (7, 6, 7), (8.4, 41, -3.5), "lime_terracotta", "lime_concrete", "green_terracotta",
       front=["lllllll", "lllllll", "lllllll", "lglglgl", "g.g.g.g", "g...g.."], side=["lllllll", "lllllll", "lllllll", "glglglg", ".g.g.g.", "..g...g"],
       K={"l": "lime_terracotta", "g": "green_terracotta"})
    m.c("armR", "green_terracotta", (-13, 35, 0), (0.6, 3, 0.6))
    m.c("armR", "yellow_concrete", (-13, 37, 0), (2, 2, 2), (0, 45, 0))
    m.c("armR", "orange_concrete", (-13, 37, 0.7), (0.8, 0.8, 0.8))
    m.attacks = {"slam": "slam", "toss": "swipe", "roots": "stomp", "quake": "stomp"}
    m.melee = "swipe"
    return m


# ========================================================================================== Mayor Grumble
@model
def mayor_grumble():
    """The village mayor, now a person: the big villager head with the unibrow, green eyes and the long
    nose, a green coat with gold buttons and a red sash, a gold chain of office with a big emerald, a black
    top hat with a red band, a gavel in his hand, grey trousers and polished shoes planted flat."""
    m = Model("mayor_grumble", "biped", 2.4)
    biped(m, hip=8, legx=2.2, neck=19, shoulder=17.5, armx=6.4)
    m.bone("hat", "head", (0, 30, 0))
    m.bone("gavel", "armR", (-6.4, 8, 2))
    m.hold = {"gavel": 20}
    m.bend = -35
    SK, SL, SD, BR, GE, GW = "terracotta", "white_terracotta", "brown_terracotta", "black_terracotta", "green_concrete", "white_concrete"
    CO, CL, CD, AU, AD, RD, RR, TR, TD, SH = ("green_terracotta", "lime_terracotta", "black_terracotta", "gold_block", "yellow_terracotta",
                                             "red_concrete", "red_terracotta", "gray_concrete", "black_concrete", "black_concrete")
    K = {"s": SK, "l": SL, "d": SD, "k": BR, "e": GE, "w": GW, "c": CO, "L": CL, "D": CD, "a": AU, "o": AD, "r": RD, "R": RR, "t": TR,
         "x": "emerald_block", "m": "red_terracotta", "h": "black_concrete"}
    s = Sheet(256, 256)
    # trousers and shoes
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2.2
        bx(m, s, leg, (3, 7, 3), (x - 1.5, 1.4, -1.5), TR, "light_gray_concrete", TD, front=["ttt", "t.t", "ttt", "ttt", "ttt", "ttt", "ttt"], K=K)
        bx(m, s, leg, (3, 2, 5), (x - 1.5, 0, -1.5), SH, "gray_concrete", None, front=["hhh", "hhh"], K=K)
    # coat tails and waist
    bx(m, s, "hips", (9, 4, 6), (-4.5, 5, -3), CO, None, CD, front=["cccaacccc"[:9], "cccc.cccc", "ccc...ccc", "cc.....cc"], back=["ccccccccc", "ccccDcccc", "ccccDcccc", "ccccDcccc"], K=K)
    # chest with buttons, white shirt, the red sash from shoulder to hip
    bx(m, s, "body", (9, 10, 6), (-4.5, 9, -3), CO, CL, CD, front=[
        "ccwwwwwcc"[:9], "cccwwwccr", "cccwawcrr", "cccwwrrrc", "cccwarrcc", "cccrrrccc", "ccrrraccc", "crrcccccc", "aaaaaaaaa", "ccccacccc"], back=[
        "ccccccccc", "ccccccccr", "cccccccrr", "ccccccrrc", "cccccrrcc", "ccccrrccc", "cccrrcccc", "ccrrccccc", "aaaaaaaaa", "ccccccccc"], K=K)
    # gold chain of office with an emerald medallion
    for sd in (1, -1):
        m.c("body", AU, (sd * 2.3, 16.4, 3.2), (0.8, 3.6, 0.5), (0, 0, 28 * sd))
    bx(m, s, "body", (3, 3, 1), (-1.5, 12.6, 3), AU, None, AD, front=["aoa", "oxo", "aoa"], K=K)
    m.c("body", "emerald_block", (0, 14.1, 4.0), (1.2, 1.2, 0.4), light=True)
    # epaulettes
    for sd in (1, -1):
        bx(m, s, "body", (3, 1, 5), (sd * 5.4 - 1.5, 18.4, -2.5), AU, None, AD)
        for i in range(3):
            m.c("body", AD, (sd * 5.4 - 1 + i, 17.6, 2.2), (0.4, 1.2, 0.4))
    # arms: coat sleeves with gold cuffs, villager-coloured hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        ax = sd * 6.4
        bx(m, s, arm, (3, 7, 3), (ax - 1.5, 11, -1.5), CO, CL, CD)
        bx(m, s, arm, (3, 1, 3), (ax - 1.5, 10.4, -1.5), AU, None, AD, edge=False)
        bx(m, s, arm, (3, 3, 3), (ax - 1.5, 7.4, -1.5), SK, None, SD)
    # the big head: unibrow, green eyes, nose, a grumpy mouth, sideburns
    bx(m, s, "head", (10, 11, 9), (-5, 19, -4.5), SK, SL, SD, K=K, front=[
        "ssssssssss", "ssssssssss", "ssssssssss", "kkkkkkkkkk", "kkkkkkkkkk", "seweswewes"[:10], "sewessewes"[:10], "dsssssssds", "dsssssssds", "dssmmmmsds", "dssssssssd"],
        side=["sssssssss", "sssssssss", "sssssssss", "kkkssssss", "sssssssss", "sssssssss", "ssssdssss", "ssdddssss", "sddddssss", "sddddssss", "sssssssss"],
        back=["ssssssssss"] * 10 + ["dddddddddd"])
    bx(m, s, "head", (2, 5, 2), (-1, 20.2, 4.4), SK, SL, SD)
    bx(m, s, "head", (10, 2, 1), (-5, 25, 4.4), BR, None, None, edge=False)
    # top hat with a red band
    bx(m, s, "hat", (12, 1, 11), (-6, 30, -5.5), "black_concrete", "gray_concrete", None, edge=False)
    bx(m, s, "hat", (8, 2, 7), (-4, 31, -3.5), RD, None, RR, front=["rrrrrrrr", "rrraarrr"], K=K)
    bx(m, s, "hat", (8, 6, 7), (-4, 33, -3.5), "black_concrete", "gray_concrete", None)
    # the gavel
    limb(m, "gavel", "dark_oak_planks", (-6.4, 6, 2), [(9, 1, (60, 0, 0))])
    bx(m, s, "gavel", (3, 3, 6), (-7.9, 9, 7.4), "dark_oak_planks", "oak_planks", "dark_oak_log", front=["aaa", "...", "aaa"], back=["aaa", "...", "aaa"], K=K)
    m.attacks = {"minions": "roar", "volley": "cast", "quake": "slam", "roar": "roar"}
    m.melee = "slam"
    return m


# ===================================================================================== Shulker Matriarch
@model
def shulker_matriarch():
    """The mother of the shulkers, painted properly: a purpur shell with raised plates and dark seams,
    the lid lifted on her pale yellow head with black eyes, a crown of end rods along the lid, glowing
    purple runes along the seam, and four small shulkers with their own faces orbiting her."""
    m = Model("shulker_matriarch", "float", 2.6)
    m.bone("core", "root", (0, 8, 0))
    m.bone("head", "core", (0, 6, 0))
    m.bone("lid", "core", (0, 8, -8))
    m.bone("ring1", "core", (0, 10, 0))
    P, PL, PD, PS, HD, HL, HK = "purpur_block", "magenta_terracotta", "purple_terracotta", "purple_concrete", "end_stone", "yellow_terracotta", "black_concrete"
    K = {"p": P, "l": PL, "d": PD, "s": PS, "h": HD, "y": HL, "k": HK, "r": "magenta_concrete", "w": "white_concrete"}
    s = Sheet(256, 256)

    def seams(n, h, phase=0):
        rows = []
        for y in range(h):
            if y == h - 1 or y == 0: rows.append("d" * n); continue
            rows.append("".join("d" if (x + phase) % 4 == 0 else ("l" if y == 1 else "p") for x in range(n)))
        return rows
    base = s.box(16, 8, 16, P, top=PD, bottom=PD)
    for f in ("front", "back", "left", "right"):
        s.draw(base, f, 0, 0, seams(16, 8), K)
        s.draw(base, f, 0, 0, ["................", "..r.......r....."[:16]], K)
    pb(m, s, "core", base, (-8, 0, -8), lit={"magenta_concrete"})
    bx(m, s, "core", (18, 2, 18), (-9, -0.6, -9), PD, PS, PD)
    lid = s.box(16, 10, 16, P, top=PL, bottom=PD)
    for f in ("front", "back", "left", "right"):
        s.draw(lid, f, 0, 0, seams(16, 10, 2), K)
    tops = []
    for y in range(16):
        tops.append("".join("d" if (x % 5 == 0 or y % 5 == 0) else ("l" if (x + y) % 7 == 0 else "p") for x in range(16)))
    s.draw(lid, "top", 0, 0, tops, K)
    pb(m, s, "lid", lid, (-8, 8, -8))
    for sd in (1, -1):
        bx(m, s, "lid", (2, 6, 14), (sd * 8.6 - 1, 10, -7), PL, None, PD)
    # the head inside
    hd = s.box(8, 8, 8, HD, top=HL)
    s.draw(hd, "front", 0, 0, ["hhhhhhhh", "hyyyyyyh", "hkkhhkkh", "hkwhhkwh", "hhhhhhhh", "hhykkyhh", "hhhhhhhh", "yyyyyyyy"], K)
    pb(m, s, "head", hd, (-4, 6, -4), lit={"white_concrete"})
    # end rods along the lid
    for k in range(7):
        x = -6.6 + k * 2.2
        m.c("lid", "end_rod", (x, 19.6, 7.4), (0.6, 3.2 - abs(k - 3) * 0.4, 0.6), light=True)
    # four small shulkers with faces
    for k, (x, z) in enumerate(((14, 0), (-14, 0), (0, 14), (0, -14))):
        bx(m, s, "ring1", (4, 2, 4), (x - 2, 9, z - 2), P, None, PD, front=["dddd", "pppp"], K=K)
        bx(m, s, "ring1", (4, 2, 4), (x - 2, 11.6, z - 2), PL, None, PD, rot=(-20, 0, 0), origin=(x, 11.6, z - 2))
        bx(m, s, "ring1", (2, 2, 2), (x - 1, 10.4, z - 0.6), HD, None, None, front=["kk", "hh"], K=K, edge=False)
    m.rest("lid", (-26, 0, 0))
    m.no_elbows = True
    m.attacks = {"orbs": "spin", "levitate": "raise", "shockwave": "pulse", "dive": "dive"}
    m.melee = "pulse"
    return m


# ================================================================================ detail and trimming
@model
def hollow_mage():
    """The hollow mage with extra detail: patches stitched on the hat, fireflies drifting round the brim,
    brass buttons, and a lantern hung from the staff."""
    m = v7_bigs.hollow_mage()
    for i, (x, z, c) in enumerate(((4, 6, "brown_terracotta"), (-6, -3, "orange_terracotta"), (7, -5, "lime_terracotta"))):
        m.c("hat", c, (x, 27.1, z), (3, 0.3, 2.4))
        m.c("hat", "black_concrete", (x - 1.6, 27.15, z), (0.3, 0.3, 2.4))
    for a in range(0, 360, 45):
        r = 12.5
        m.c("hat", "yellow_concrete", (r * math.cos(math.radians(a)), 29 + (a % 90) / 30, r * math.sin(math.radians(a))), (0.5, 0.5, 0.5), light=True)
    for y in (12, 14, 16):
        m.c("body", "gold_block", (0, y, 3.3), (0.8, 0.8, 0.4))
    for k in range(6):
        m.c("staff", "chain", (-7.5, 26 - k * 0.7, 6), (0.3, 0.7, 0.3))
    m.c("staff", "dark_oak_planks", (-7.5, 21.5, 6), (2.2, 0.4, 2.2))
    m.c("staff", "yellow_concrete", (-7.5, 20.4, 6), (1.6, 2, 1.6), light=True)
    m.c("staff", "dark_oak_planks", (-7.5, 19.2, 6), (2.2, 0.4, 2.2))
    return m


@model
def king_gloop():
    """King Gloop with extra detail: bubbles rising inside the jelly, a ring of slimeballs round his crown
    and swallowed loot floating in his body."""
    m = v2_general.king_gloop()
    rnd = random.Random(5)
    for i in range(14):
        x, y, z = rnd.uniform(-10, 10), rnd.uniform(4, 24), rnd.uniform(-10, 10)
        sz = rnd.choice((0.8, 1.0, 1.4))
        m.c("body", "lime_stained_glass", (x, y, z), (sz, sz, sz))
    for (x, y, z, b) in ((-5, 9, 4, "iron_block"), (6, 14, -3, "gold_block"), (2, 6, -6, "bone_block"), (-7, 17, -2, "diamond_block")):
        m.c("body", b, (x, y, z), (1.6, 1.6, 0.6), (0, 30, 20))
    return m


@model
def mossback():
    """Mossback trimmed to about 250 blocks: the smallest loose bits go first, the head and glowing parts stay."""
    m = v6_originals.mossback()
    keep_bones = {"head", "neck"}
    vol = lambda c: abs((c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2]))
    extra = len(m.cubes) - 255
    if extra > 0:
        cands = sorted((i for i, c in enumerate(m.cubes) if c["b"] not in keep_bones and not c.get("l")), key=lambda i: vol(m.cubes[i]))
        drop = set(cands[:extra])
        m.cubes = [c for i, c in enumerate(m.cubes) if i not in drop]
    return m
