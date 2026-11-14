"""v8: the goofy pumpkins (ref29). Three decorations that sit and pull faces, and the Gourd King boss whose
face changes as it fights. Face pieces are tagged "face:<state>"; the plugin shows one face at a time
(idle, angry when attacking, hurt when hit, rage below half health, dead in its death)."""
import math
from models import model, biped, limb
from build import Model
from texpaint import paintbox, Sheet

SPAWN, DEATH = {}, {}
OR, LT, RB, DK, MO, EY, TT, TG, ST, LF = ("orange_concrete", "honeycomb_block", "red_terracotta", "brown_terracotta", "nether_wart_block",
                                          "black_concrete", "yellow_terracotta", "pink_terracotta", "green_terracotta", "lime_terracotta")
K = {"o": OR, "l": LT, "r": RB, "d": DK, "m": MO, "k": EY, "t": TT, "p": TG, "s": ST, "f": LF, "w": "white_concrete"}


def pb(m, s, bone, uv, lo, lit=(), **kw):
    kw.setdefault("passes", 0)
    return paintbox(m, bone, s.img, uv, lo, s.sizes[uv], allowed=sorted(s.used), lit=lit, **kw)


def ribs(w, h, step=4, off=1):
    """Rows of a ribbed pumpkin face: dark ribs, a light stripe beside each, light top, dark bottom."""
    rows = []
    for y in range(h):
        r = ""
        for x in range(w):
            c = "o"
            if (x - off) % step == 0: c = "r"
            elif (x - off) % step == 2 and 2 <= y < h - 3: c = "l"
            if y >= h - 2: c = "d" if y == h - 1 or c == "r" else "r" if c == "r" else "o"
            r += c
        rows.append(r)
    return rows


def body(m, s, bone, w, h, d, lo, step=4):
    """A ribbed pumpkin block."""
    b = s.box(w, h, d, OR)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(b, f)
        s.draw(b, f, 0, 0, ribs(fw, fh, step), K)
    top = []
    for z in range(d):
        top.append("".join("r" if (x - 1) % step == 0 and z in (0, d - 1) or (z - 1) % step == 0 and x in (0, w - 1) else "l" if abs(x - w / 2 + 0.5) + abs(z - d / 2 + 0.5) < 3 else "o" for x in range(w)))
    s.draw(b, "top", 0, 0, top, K)
    pb(m, s, bone, b, lo)
    return b


def face(m, s, bone, state, w, h, lo, rows, lit=()):
    """One carved face: a sheet just in front of the pumpkin holding only the eyes and mouth, shown only for state."""
    plate = s.box(w, h, 1, OR)
    fu, fv, fw, fh = s.face(plate, "front")
    for y in range(fh):
        for x in range(fw):
            s.img.putpixel((fu + x, fv + y), (0, 0, 0, 0))
    s.draw(plate, "front", 0, 0, rows, K)
    n0 = len(m.cubes)
    pb(m, s, bone, plate, lo, lit=lit, plane="front", shell=False)
    for c in m.cubes[n0:]:
        c["g"] = "face:" + state


def stem(m, bone, x, y, z, curl=1, tall=5):
    limb(m, bone, ST, (x, y, z), [(2, 1.6, (0, 0, 0)), (2, 1.4, (0, 0, 25 * curl)), (2, 1.2, (0, 0, -20 * curl)), (tall - 4, 1, (0, 0, 35 * curl))])
    m.c(bone, ST, (x, y + 0.4, z), (4, 0.8, 4))
    m.c(bone, LF, (x + 2 * curl, y + 1.8, z + 1), (3, 0.5, 2), (0, 30, -20 * curl))


def pad(rows, w, h, top=0):
    out = ["." * w] * top + [r.ljust(w, ".")[:w] for r in rows]
    return (out + ["." * w] * h)[:h]


# ------------------------------------------------------------------------- faces, drawn per pumpkin size
def faces_tall(w=12, h=16):
    """Tall pumpkin: one squinty eye, a lopsided mouth with a snaggle tooth."""
    return {
        "idle":      pad(["", "", "", "", "", "", ".k......k...", ".k......k...", "", "......mmmm..", ".....mmtmm..", ".....mmmmm..", "......mmm..."], w, h),
        "happy":     pad(["", "", "", "", "", "", ".k.......k..", "k.k.....k.k.", "", "..m.....m...", "...mmmmmm...", "....mtmm....", ""], w, h),
        "surprised": pad(["", "", "", "", "", ".kk.....kk..", ".kk.....kk..", "", "....mmmm....", "...mmmmmm...", "...mmmmmm...", "....mmmm....", ""], w, h),
        "angry":     pad(["", "", "", "", "k.......k...", ".kk....kk...", "..k....k....", "", "..mmmmmmm...", "..mtmtmtm...", "..mmmmmmm...", "", ""], w, h),
        "sleepy":    pad(["", "", "", "", "", "", "", ".kkk...kkk..", "", "", ".....mm.....", ".....mm.....", ""], w, h),
        "wink":      pad(["", "", "", "", "", "", ".kk.....k...", ".kk....k.k..", "", "..mmmmmm....", "...mmmmp....", "......pp....", ""], w, h),
    }


def faces_flat(w=14, h=9):
    """Wide flat pumpkin: a huge toothy grin."""
    return {
        "idle":      pad(["", "", "..k........k..", "..k........k..", "", ".m..........m.", ".mmmtmmmmtmmm.", "..mmmmtmmmmm..", ""], w, h),
        "happy":     pad(["", ".k.k......k.k.", "..k........k..", "", ".m..........m.", "..mmmmmmmmmm..", "...mtmmmtmm...", "....mmmmmm....", ""], w, h),
        "surprised": pad(["", "..kk......kk..", "..kk......kk..", "", ".....mmmm.....", "....mmmmmm....", "....mmmmmm....", ".....mmmm.....", ""], w, h),
        "angry":     pad([".k..........k.", "..kk......kk..", "...k......k...", "", "..mmmmmmmmmm..", "..mtmtmtmtmm..", "..mmmmmmmmmm..", "", ""], w, h),
        "sleepy":    pad(["", "", "", "..kkk....kkk..", "", "", "......mm......", "", ""], w, h),
        "wink":      pad(["", "..kk......k...", "..kk.....k.k..", "", ".m..........m.", "..mmmmmmmmmm..", "...mmmmmpp....", "........pp....", ""], w, h),
    }


def faces_cube(w=12, h=12):
    """Cube pumpkin: little eyes high up and a gaping mouth, tongue hanging out."""
    return {
        "idle":      pad(["", "", ".k........k.", "", ".mmmmmmmmm..", ".mmmmmmmtm..", ".mmmmmmmmm..", ".mmmmmmmmm..", "..mmmpppmm..", "....ppp.....", "....pp......", ""], w, h),
        "happy":     pad(["", ".k.k....k.k.", "", "", ".m........m.", "..mmmmmmmm..", "..mmmtmmmm..", "...mmpppm...", "....ppp.....", "", "", ""], w, h),
        "surprised": pad(["", ".kk......kk.", ".kk......kk.", "", "...mmmmmm...", "..mmmmmmmm..", "..mmmmmmmm..", "..mmmmmmmm..", "...mmmmmm...", "", "", ""], w, h),
        "angry":     pad([".k........k.", "..kk....kk..", "", ".mmmmmmmmmm.", ".mtmtmtmtmm.", ".mmmmmmmmmm.", ".mmtmtmtmtm.", ".mmmmmmmmmm.", "", "", "", ""], w, h),
        "sleepy":    pad(["", "", "", ".kkk....kkk.", "", "", ".....mm.....", ".....mm.....", "", "", "", ""], w, h),
        "wink":      pad(["", ".kk.....k...", ".kk....k.k..", "", "..mmmmmmmm..", "..mmmmmmmm..", "...mmpppm...", "....ppp.....", "....pp......", "", "", ""], w, h),
    }


def decor(name, w, h, d, faces, step, stem_at, curl, tall):
    m = Model(name, "slime", 1.0)
    m.bone("body", "root", (0, 0, 0))
    s = Sheet(256, 256)
    body(m, s, "body", w, h, d, (-w / 2, 0, -d / 2), step)
    for st, rows in faces.items():
        face(m, s, "body", st, w, h, (-w / 2, 0, d / 2 - 0.3), rows)
    stem(m, "body", stem_at[0], h, stem_at[1], curl, tall)
    m.attacks = {}
    m.melee = "hop"
    return m


@model
def decor_pumpkin_tall():
    """A tall ribbed pumpkin with a squint and a snaggle tooth. It sits and pulls faces."""
    return decor("decor_pumpkin_tall", 12, 16, 12, faces_tall(), 5, (0, 0), 1, 8)


@model
def decor_pumpkin_flat():
    """A wide flat pumpkin with a huge toothy grin. It sits and pulls faces."""
    return decor("decor_pumpkin_flat", 14, 9, 12, faces_flat(), 5, (0, 0), -1, 5)


@model
def decor_pumpkin_cube():
    """A square pumpkin with its mouth hanging open and its tongue out. It sits and pulls faces."""
    m = decor("decor_pumpkin_cube", 12, 12, 12, faces_cube(), 5, (0, 0), 1, 7)
    return m


def faces_king(w=16, h=14):
    return {
        "idle":  pad(["", "", "", "..kkk.....kkk...", "..kk.......kk...", "", "", "..m..........m..", "..mmmtmmmmtmmm..", "...mmmmmmmmmm...", "....mmtmmtmm....", "", ""], w, h),
        "angry": pad(["", "", ".k..........k...", "..kkk.....kkk...", "...kkk...kkk....", "", "", "..mmmmmmmmmmmm..", "..mtmtmtmtmtmm..", "..mmmmmmmmmmmm..", "..mmtmtmtmtmtm..", "..mmmmmmmmmmmm..", ""], w, h),
        "hurt":  pad(["", "", "", "..k.k.....k.k...", "...k.......k....", "..k.k.....k.k...", "", "", ".....mmmmm......", "....mmmmmmm.....", "....mmmmmmm.....", ".....mmmmm......", ""], w, h),
        "rage":  pad(["", "", ".y..........y...", "..yyy.....yyy...", "...yyy...yyy....", "", "", "..yyyyyyyyyyyy..", "..ytytytytytyy..", "..yyyyyyyyyyyy..", "..yytytytytyty..", "..yyyyyyyyyyyy..", ""], w, h),
        "dead":  pad(["", "", "", "..k.k.....k.k...", "...k.......k....", "..k.k.....k.k...", "", "", "", "...mmmmmmmmm....", "", "", ""], w, h),
    }


@model
def gourd_king():
    """The Gourd King: a giant ribbed pumpkin head on a body of twisted vines, a lantern of embers glowing in
    its chest, leaves for shoulders and a lantern on a chain. Its face changes as it fights: a toothy grin,
    a snarl when it attacks, a yelp when it is hit, burning eyes and mouth below half health. Two of the
    goofy pumpkins ride its shoulders and pull faces of their own."""
    m = Model("gourd_king", "biped", 2.6)
    biped(m, hip=10, legx=3.2, neck=22, shoulder=20, armx=8)
    m.bone("lantern", "armL", (8.5, 8, 1))
    m.bend = -40
    m.hold = {"lantern": 20}
    K["y"] = "shroomlight"
    K["e"] = "ochre_froglight"
    VG, VL, VD = "green_terracotta", "lime_terracotta", "green_concrete"
    s = Sheet(256, 256)

    # the head: a big ribbed pumpkin with five faces
    body(m, s, "head", 16, 14, 16, (-8, 22, -8), 5)
    for st, rows in faces_king().items():
        face(m, s, "head", st, 16, 14, (-8, 22, 8 - 0.3), rows, lit={"shroomlight", "yellow_terracotta"} if st == "rage" else ())
    stem(m, "head", 0, 36, 0, 1, 9)
    # a crown of thorny vines round the stem
    for k in range(8):
        a = k * math.pi / 4
        m.c("head", VD, (3.4 * math.cos(a), 36.6, 3.4 * math.sin(a)), (1, 2.2 if k % 2 else 1.4, 1), (0, -math.degrees(a), 12))

    # torso: woven vines round a cage with embers glowing through
    tor = s.box(12, 11, 8, VG)
    rows = []
    for y in range(11):
        rows.append("".join("f" if x % 3 == 1 and y % 5 != 4 else "s" if y % 5 == 4 else "." for x in range(12)))
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(tor, f)
        s.draw(tor, f, 0, 0, [r[:fw] for r in rows], K)
    s.draw(tor, "front", 4, 3, ["eyye", "yeey", "eyye"], K)
    pb(m, s, "body", tor, (-6, 11, -4), lit={"shroomlight", "ochre_froglight"})
    m.c("body", "shroomlight", (0, 16, 0), (8, 6, 5), light=True)
    # leaf shoulders and a vine collar
    for sx in (1, -1):
        m.c("body", VL, (sx * 9, 20.4, 0), (9, 1, 7), (0, 0, sx * -10))
        m.c("body", VD, (sx * 7.5, 21, 3.2), (5, 0.8, 3), (20, 20 * sx, sx * -25))
        m.c("body", VD, (sx * 7.5, 21, -3.2), (5, 0.8, 3), (-20, -20 * sx, sx * -25))
    m.c("body", VD, (0, 22.3, 0), (11, 1.4, 9))

    # legs: twisted vine trunks with root toes
    for side, leg in ((1, "legL"), (-1, "legR")):
        x = side * 3.2
        limb(m, leg, VG, (x, 10, 0), [(5, 3.6, (0, 0, 180 + 4 * side)), (5, 3.2, (0, 0, 180 - 3 * side))])
        for y in (8.5, 5.5, 2.5):
            m.c(leg, VL, (x, y, 0), (4, 0.8, 4), (0, 45, 0))
        for a in (-35, 0, 35):
            m.c(leg, VD, (x + math.sin(math.radians(a)) * 2.6, 0.5, 1.8 + math.cos(math.radians(a)) * 1.6), (1.4, 1, 4), (0, a, 0))
        m.c(leg, VD, (x, 0.8, -1.4), (3, 1.6, 3))

    # arms: long vines ending in leafy claws
    for side, arm in ((1, "armL"), (-1, "armR")):
        x = side * 8.5
        limb(m, arm, VG, (x, 20, 0), [(6, 2.6, (0, 0, 180 + 8 * side)), (6, 2.2, (0, 0, 180 - 4 * side))])
        for y in (17, 13):
            m.c(arm, VL, (x + side * 0.3, y, 0), (3.2, 0.8, 3.2), (0, 45, 0))
        for a in (-30, 0, 30):
            m.c(arm, VL, (x + math.sin(math.radians(a)) * 1.5, 6.4, 1 + math.cos(math.radians(a)) * 1.2), (1.2, 3.4, 0.8), (20, a, 0))
    # the lantern on a chain: an orange glow in an iron cage
    for k in range(3):
        m.c("lantern", "chain", (8.5, 7 - k * 1.6, 1), (0.6, 1.6, 0.6))
    m.c("lantern", "iron_block", (8.5, 2.6, 1), (3.4, 0.6, 3.4))
    m.c("lantern", "shroomlight", (8.5, 0.8, 1), (2.6, 3, 2.6), light=True)
    m.c("lantern", "iron_block", (8.5, -1, 1), (3.4, 0.6, 3.4))

    # two goofy pumpkins riding the shoulders, pulling faces with the king
    for sx, ff, w, h in ((1, faces_flat, 14, 9), (-1, faces_cube, 12, 12)):
        sc = 0.42
        bw, bh = round(w * sc), round(h * sc)
        bx = sx * 12 - bw / 2
        body(m, s, "body", bw, bh, bw, (bx, 21, -bw / 2), 3)
        small = {"idle": "idle", "angry": "angry", "hurt": "surprised", "rage": "angry", "dead": "sleepy"}
        allf = ff(bw, bh)
        mini = {"idle": pad(["", ".k..k" if bw < 6 else ".k...k", "", ".mmm" if bw < 6 else ".mmmm"], bw, bh),
                "angry": pad([".k..k" if bw < 6 else ".k...k", "", ".mtm" if bw < 6 else ".mtmm", ".mmm"], bw, bh),
                "hurt": pad(["", ".k..k" if bw < 6 else ".k...k", "..m.", "..m."], bw, bh),
                "rage": pad([".k..k" if bw < 6 else ".k...k", "", ".mtm" if bw < 6 else ".mtmm", ".mmm"], bw, bh),
                "dead": pad(["", ".k..k" if bw < 6 else ".k...k", "", "..mm"], bw, bh)}
        for st, rows in mini.items():
            face(m, s, "body", st, bw, bh, (bx, 21, bw / 2 - 0.3), rows)
        m.c("body", VD, (sx * 12, 21 + bh + 0.6, 0), (0.8, 1.6, 0.8), (0, 0, 20 * sx))

    m.attacks = {"slam": "slam", "fire_ring": "cast", "minions": "roar", "volley": "double", "leap": "lunge"}
    m.melee = "swipe"
    return m
