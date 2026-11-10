"""v5 mythic bosses, painted from the real mob textures onto big blocks."""
from models import model, biped
from build import Model
from texpaint import load, paintbox, box_faces
from PIL import Image

SPAWN, DEATH = {}, {}


@model
def the_listener():
    m = Model("the_listener", "biped", 2.6)
    biped(m, hip=13, legx=5.9, neck=34, shoulder=34, armx=13)
    m.mbone("tendrilL", "head", (8, 46, 0))
    img = load("warden.png")
    glow = load("warden_bioluminescent_layer.png")
    heart = load("warden_heart.png")
    img.alpha_composite(heart)
    for x in range(128):
        for y in range(128):
            p = glow.getpixel((x, y))
            if p[3] > 60:
                img.putpixel((x, y), (40, 220, 230, 255))
    A = ["sculk", "black_concrete", "gray_concrete", "cyan_concrete", "light_blue_concrete", "cyan_terracotta",
         "bone_block", "warped_wart_block", "light_gray_concrete"]
    L = {"cyan_concrete", "light_blue_concrete"}
    kw = dict(allowed=A, lit=L, speck=2, merge={"black_concrete": "sculk", "gray_concrete": "sculk"})
    paintbox(m, "legR", img, (76, 48), (-9, 0, -3), (6, 13, 6), **kw)
    paintbox(m, "legL", img, (76, 76), (3, 0, -3), (6, 13, 6), **kw)
    paintbox(m, "body", img, (0, 0), (-9, 13, -7), (18, 21, 11), **kw)
    paintbox(m, "body", img, (90, 11), (-9, 13, 4.15), (9, 21, 0), plane="front", shell=False, **kw)
    paintbox(m, "body", img, (90, 11), (0, 13, 4.15), (9, 21, 0), plane="front", shell=False, mirror=True, **kw)
    paintbox(m, "head", img, (0, 32), (-8, 34, -5), (16, 16, 10), **kw)
    paintbox(m, "tendrilR", img, (52, 32), (-24, 43, -0.25), (16, 16, 0), plane="front", shell=False, **kw)
    paintbox(m, "tendrilL", img, (58, 0), (8, 43, -0.25), (16, 16, 0), plane="front", shell=False, **kw)
    paintbox(m, "armR", img, (44, 50), (-17, 6, -5), (8, 28, 8), **kw)
    paintbox(m, "armL", img, (0, 58), (9, 6, -5), (8, 28, 8), **kw)
    m.no_elbows = True
    m.attacks = {"sonic_boom": "roar", "slam": "slam", "quake": "stomp", "darkness": "cast"}
    m.melee = "swipe"
    return m


@model
def withered_tyrant():
    m = Model("withered_tyrant", "float", 3.0)
    m.bone("core", "root", (0, 18, 0))
    m.bone("head", "core", (0, 20, 0))
    m.bone("armL", "core", (9, 21, 1))
    m.bone("armR", "core", (-9, 21, 1))
    m.bone("tail", "core", (-0.5, 7.3, -1.5))
    img = load("wither.png")
    # mythic: a nether star set in the middle skull's brow
    A = ["black_concrete", "gray_concrete", "light_gray_concrete", "polished_deepslate", "white_concrete", "cyan_terracotta", "black_terracotta"]
    kw = dict(allowed=A, speck=1, merge={"black_terracotta": "black_concrete"})
    paintbox(m, "core", img, (0, 16), (-10, 17.1, -2.5), (20, 3, 3), **kw)
    sp = (-2, 17.1, 0.5)
    paintbox(m, "core", img, (0, 22), (-2, 7.1, -2.5), (3, 10, 3), rot=(11.7, 0, 0), origin=sp, **kw)
    for y in (13.6, 11.1, 8.6):
        paintbox(m, "core", img, (24, 22), (-6, y, -2), (11, 2, 2), rot=(11.7, 0, 0), origin=sp, **kw)
    paintbox(m, "tail", img, (12, 22), (-2, 1.3, -4.5), (3, 6, 3), rot=(47.7 + 11.7, 0, 0), origin=(-0.5, 7.3, -1.5), **kw)
    paintbox(m, "head", img, (0, 0), (-4, 20, -4), (8, 8, 8), **kw)
    m.c("head", "white_concrete", (0, 26.6, 4.06), (1.6, 1.6, 0.12), (0, 0, 45), light=True)
    m.c("head", "light_blue_concrete", (0, 26.6, 4.12), (0.7, 0.7, 0.12), (0, 0, 45), light=True)
    paintbox(m, "armR", img, (32, 0), (-12, 18, -2), (6, 6, 6), **kw)
    paintbox(m, "armL", img, (32, 0), (6, 18, -2), (6, 6, 6), **kw)
    m.no_elbows = True
    m.attacks = {"skulls": "spin", "blast": "pulse", "minions": "raise", "charge": "dive"}
    m.melee = "swipe"
    return m


def _seg(P, L, a):
    """End of a segment hanging L down from P, swung by a degrees about x (positive swings it back)."""
    import math
    r = math.radians(a)
    return (P[0], P[1] - L * math.cos(r), P[2] - L * math.sin(r))


@model
def ender_wyrm():
    import v2_legends  # registers the dragon rig
    m = Model("ender_wyrm", "dragon", 1.0)
    img = load("dragon.png")
    eyes = load("dragon_eyes.png")
    for x in range(256):
        for y in range(256):
            p = eyes.getpixel((x, y))
            if p[3] > 60 and p[0] + p[2] > 200:
                img.putpixel((x, y), (200, 60, 230, 255))
    A = ["black_concrete", "gray_concrete", "light_gray_concrete", "polished_deepslate", "magenta_concrete", "purple_concrete", "black_terracotta", "cyan_terracotta"]
    L = {"magenta_concrete", "purple_concrete"}
    kw = dict(allowed=A, lit=L, speck=3, merge={"black_terracotta": "black_concrete", "polished_deepslate": "gray_concrete", "cyan_terracotta": "gray_concrete"})
    by = 44  # belly height
    Bz0, Bz1 = -36, 28
    m.bone("body", "root", (0, by + 12, 0))
    m.rest("body", (-8, 0, 0))
    fl, hl = (12, by + 4, 18), (14, by + 8, -14)
    m.mbone("legFL", "body", fl)
    m.mbone("legBL", "body", hl)
    m.bone("head", "body", (0, by + 18, Bz1))
    m.bone("tail", "body", (0, by + 14, Bz0))
    m.mbone("wingL", "body", (12, by + 19, 20))
    Hy, Hz = by + 34, 82
    m.bone("jaw", "head", (0, Hy - 4, Hz + 8))
    # body and its three dorsal plates
    paintbox(m, "body", img, (0, 0), (-12, by, Bz0), (24, 24, 64), coarse=("bottom",), **kw)
    for z in (10, -10, -30):
        paintbox(m, "body", img, (220, 53), (-1, by + 24, z), (2, 6, 12), **kw)
    # neck: five joints rising to the head, a plate on each
    for k in range(5):
        cy, cz = by + 15 + k * 3.6, Bz1 + 5 + k * 9.4
        paintbox(m, "head", img, (192, 104), (-5, cy - 5, cz - 5), (10, 10, 10), coarse=("bottom", "top", "back"), **kw)
        paintbox(m, "head", img, (48, 0), (-1, cy + 5, cz - 3), (2, 4, 6), **kw)
    # head
    paintbox(m, "head", img, (112, 30), (-8, Hy - 8, Hz - 6), (16, 16, 16), **kw)
    paintbox(m, "head", img, (176, 44), (-6, Hy - 4, Hz + 8), (12, 5, 16), **kw)
    paintbox(m, "jaw", img, (176, 65), (-6, Hy - 8, Hz + 8), (12, 4, 16), **kw)
    for x in (-5, 3):
        paintbox(m, "head", img, (112, 0), (x, Hy + 1, Hz + 18), (2, 2, 4), **kw)
        paintbox(m, "head", img, (0, 0), (x, Hy + 8, Hz - 2), (2, 4, 6), **kw)
    # two long horns sweeping back off the skull, dark at the root and pale at the tips
    for sx in (1, -1):
        for k, (dy, dz, w, blk) in enumerate(((7, -4, 2.6, "black_concrete"), (9, -9, 2.2, "gray_concrete"), (10.5, -14, 1.7, "light_gray_concrete"), (11.2, -18.4, 1.2, "bone_block"))):
            m.c("head", blk, (5.4 * sx, Hy + dy, Hz + dz), (w, w, 5.4), (-18 - 8 * k, 0, 0))
    # tail: twelve joints, sagging then lifting at the tip
    for k in range(12):
        cy = by + 14 - 1.6 * k + 0.12 * k * k
        cz = Bz0 - 5 - 10 * k
        paintbox(m, "tail", img, (192, 104), (-5, cy - 5, cz - 5), (10, 10, 10), coarse=("bottom", "top", "back", "front"), **kw)
        paintbox(m, "tail", img, (48, 0), (-1, cy + 5, cz - 3), (2, 4, 6), **kw)
    # legs: thigh, shin and foot, the hind legs folded like a hound's
    for s, (fb, hb) in ((1, ("legFL", "legBL")), (-1, ("legFR", "legBR"))):
        P = (hl[0] * s, hl[1], hl[2])
        paintbox(m, hb, img, (0, 0), (P[0] - 8, P[1] - 30, P[2] - 8), (16, 32, 16), rot=(-30, 0, 0), origin=P, coarse=("back", "top", "bottom"), **kw)
        Q = _seg(P, 26, -30)
        paintbox(m, hb, img, (196, 0), (Q[0] - 6, Q[1] - 30, Q[2] - 6), (12, 32, 12), rot=(32, 0, 0), origin=Q, coarse=("back", "top", "bottom"), **kw)
        R = _seg(Q, 28, 32)
        paintbox(m, hb, img, (112, 0), (R[0] - 9, R[1] - 6, R[2] - 8), (18, 6, 24), coarse=("bottom",), **kw)
        # four pale claws curling over the toes
        for t in (-6.5, -2.2, 2.2, 6.5):
            m.c(hb, "bone_block", (R[0] + t, R[1] - 3.5, R[2] + 17), (2.2, 2.6, 3.4), (20, 0, 0))
            m.c(hb, "bone_block", (R[0] + t, R[1] - 4.6, R[2] + 19.2), (1.4, 1.4, 1.8), (40, 0, 0))
    # wings: a finger bone and a black membrane, then the tip; spread and lifted a little
    for s, b in ((1, "wingL"), (-1, "wingR")):
        x0 = 12 * s
        lift = (0, 0, 4 * s)
        o = (x0, by + 19, 20)
        lo = lambda x, w: x if s > 0 else -x - w
        bk = dict(allowed=["gray_concrete", "black_concrete"], merge={"black_concrete": "gray_concrete"}, speck=8)
        paintbox(m, b, img, (112, 88), (lo(12, 56), by + 15, 16), (56, 8, 8), rot=lift, origin=o, mirror=s < 0, **bk)
        paintbox(m, b, img, (112, 136), (lo(68, 56), by + 17, 18), (56, 4, 4), rot=lift, origin=o, mirror=s < 0, **bk)
        for u0, xs in ((88, 12), (144, 68)):
            mem = membrane(img, (0, u0))
            if s < 0: mem = [r[::-1] for r in mem]
            _sheet(m, b, mem, (lo(xs, 56), by + 18.6, 20 - 56), (56, 0.6, 56), lift, o)
    m.attacks = {"breath": "howl", "charge": "charge", "bite": "bite", "minions": "rear"}
    m.melee = "bite"
    return m


def membrane(img, uv, C=7):
    """The wing membrane picture: 'M' membrane, 'B' finger bone, '.' open air (coarsened to 4 x 4 cells)."""
    u, v = uv
    rows = []
    for y in range(0, 56, C):
        r = ""
        for x in range(0, 56, C):
            n, grey, op = 0, 0, 0
            for yy in range(y, y + C):
                for xx in range(x, x + C):
                    p = img.getpixel((u + xx, v + yy))
                    n += 1
                    if p[3] > 100:
                        op += 1
                        if p[0] > 70: grey += 1
            r += "." if op * 2 < n else "B" if grey * 3 >= op else "M"
        rows.append(r)
    # the trailing edge of the membrane glows with the End's purple: the backmost cell of each column
    out = [list(r) for r in rows]
    for i in range(len(rows[0])):
        for j in range(len(rows)):
            if rows[j][i] != ".":
                if rows[j][i] == "M": out[j][i] = "E"
                break
    out = ["".join(r) for r in out]
    return out


def _sheet(m, bone, rows, lo, size, rot, origin):
    from skin import skinbox
    hi = (lo[0] + size[0], lo[1] + size[1], lo[2] + size[2])
    skinbox(m, bone, lo, hi, "black_concrete", {"planey": rows}, {"M": "black_concrete", "B": "gray_concrete", "E": ("purple_concrete", True)}, rot=rot, origin=origin, shell=False)
