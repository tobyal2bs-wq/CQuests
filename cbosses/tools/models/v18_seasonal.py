"""Seasonal decorations like the carved pumpkins: gingerbread people for Christmas and painted eggs for Easter.
Each one sits on a block, pulls faces (mostly happy, now and then sad) and hops in place now and then
(the hop is played by the plugin's Decor). Built from stacked plus-shaped slices, like the bosses."""
import roster
from build import Model
from v14_kit import B, C, K, Z
from v14_studio import studio
from v8_recipes import SPAWN, DEATH, DECOR_SPAWN, DECOR_DEATH

# one row of a face per string; '.' is empty. k eyes and mouth, w icing, p cheeks, b a tear
GINGER_FACES = {
    "idle":      [".k...k.", ".......", ".......", ".wwwww."],
    "happy":     [".k...k.", ".......", "p.....p", ".w...w.", "..www.."],
    "wink":      [".ww..k.", ".......", "p.....p", ".w...w.", "..www.."],
    "surprised": [".k...k.", ".......", "...w...", "..w.w..", "...w..."],
    "sad":       [".k...k.", ".b.....", ".......", "..www..", ".w...w."],
}
EGG_FACES = {
    "idle":      [".k...k.", ".......", ".......", "..kkk.."],
    "happy":     [".k...k.", ".......", "p.....p", ".k...k.", "..kkk.."],
    "wink":      [".kk..k.", ".......", "p.....p", ".k...k.", "..kkk.."],
    "surprised": [".k...k.", ".......", "...k...", "..k.k..", "...k..."],
    "sad":       [".k...k.", ".b.....", ".......", "..kkk..", ".k...k."],
}
INK = {"k": "black_concrete", "w": "white_concrete", "p": "pink_concrete", "b": "light_blue_concrete"}


def face(m, bone, cx, cy, z, rows, state, px):
    """One face plate on the front (z, or z(y_low, y_high) for a curved front), runs of a colour merged into one
    strip, tagged so only one shows."""
    H, W = len(rows), max(len(r) for r in rows)
    zf = z if callable(z) else (lambda a, b: z)
    ox, top = cx - W * px / 2, cy + H * px / 2
    for j, r in enumerate(rows):
        i = 0
        while i < len(r):
            if r[i] == ".":
                i += 1; continue
            k = i
            while k < len(r) and r[k] == r[i]: k += 1
            y0 = top - (j + 1) * px
            B(m, bone, INK[r[i]], (ox + i * px, y0, zf(y0, y0 + px)), ((k - i) * px, px, 0.08), g="face:" + state)
            i = k


def plus(m, bone, block, cx, y, cz, w, h, d, cut=1.0):
    """A slice with its corners cut: two crossed boxes."""
    B(m, bone, block, (cx - w / 2, y, cz - d / 2 + cut), (w, h, d - 2 * cut))
    B(m, bone, block, (cx - w / 2 + cut, y, cz - d / 2), (w - 2 * cut, h, d))


def decor_model(id, build, faces):
    @studio(id, revise=False)
    def fn():
        m = Model(id, "slime", 1.0)
        m.bone("body", "root", (0, 0, 0))
        build(m)
        m.anims = {"idle": {"length": 3.0, "loop": True, "bones": {"body": {"rot": K((0, Z), (3.0, Z))}}}}
        m.attacks, m.melee = {}, "hop"
        return m
    fn.__name__ = id
    SPAWN[id], DEATH[id] = DECOR_SPAWN, DECOR_DEATH
    if id not in roster.DECOR:
        roster.DECOR.append(id); roster.ALL.append(id)
    return fn


def gingerbread(girl):
    def build(m):
        dough, d = "terracotta", 3.2
        # legs, a little apart, with icing cuffs and rounded feet
        for sd in (1, -1):
            C(m, "body", dough, (sd * 2.3, 2.6, 0), (3.0, 5.0, d), (0, 0, 8 * sd))
            C(m, "body", dough, (sd * 2.6, 0.6, 0), (3.6, 1.2, d - 0.6))
            C(m, "body", "white_concrete", (sd * 2.45, 1.9, d / 2 + 0.05), (2.6, 0.35, 0.1), (0, 0, 8 * sd))
        # body, arms out and a bit raised, icing at the wrists
        plus(m, "body", dough, 0, 4.4, 0, 7.6, 5.6, d, 0.6)
        for sd in (1, -1):
            C(m, "body", dough, (sd * 5.6, 8.0, 0), (4.6, 2.8, d), (0, 0, 18 * sd))
            C(m, "body", dough, (sd * 7.6, 8.7, 0), (1.4, 2.4, d - 0.6), (0, 0, 18 * sd))
            C(m, "body", "white_concrete", (sd * 6.6, 8.35, d / 2 + 0.05), (0.35, 2.5, 0.1), (0, 0, 18 * sd))
        # gumdrop buttons, and a bow tie or a skirt of icing
        for k, (y, b) in enumerate(((5.6, "red_concrete"), (7.6, "lime_concrete"))):
            C(m, "body", b, (0, y, d / 2 + 0.25), (1.3, 1.3, 0.5))
        if girl:
            C(m, "body", "white_concrete", (0, 4.6, d / 2 + 0.06), (6.2, 0.35, 0.1))
            for x in (-2.7, -0.9, 0.9, 2.7):
                C(m, "body", "white_concrete", (x, 4.2, d / 2 + 0.05), (0.9, 0.9, 0.1), (0, 0, 45))
        else:
            for sd in (1, -1):
                C(m, "body", "red_concrete", (sd * 1.0, 9.6, d / 2 + 0.2), (1.8, 1.4, 0.4), (0, 0, 20 * sd))
            C(m, "body", "red_concrete", (0, 9.6, d / 2 + 0.3), (0.8, 0.8, 0.4))
        # the head: a round cookie, slightly darker baked rim behind
        plus(m, "body", dough, 0, 10.0, 0, 7.0, 6.2, d, 0.5)
        plus(m, "body", dough, 0, 10.8, 0, 8.0, 4.6, d - 0.2, 0.5)
        if girl:
            for sd in (1, -1):
                C(m, "body", "pink_concrete", (sd * 1.3, 16.4, 0), (2.2, 1.6, 1.2), (0, 0, -22 * sd))
            C(m, "body", "pink_concrete", (0, 16.3, 0), (0.9, 0.9, 1.3))
        for state, rows in GINGER_FACES.items():
            face(m, "body", 0, 13.1, d / 2 + 0.02, rows, state, 0.75)
    return build


def egg(base, band, dots):
    # width of each 1.2 tall slice from the bottom up: an egg, wider low than high
    widths = [6.0, 8.0, 9.2, 9.8, 10.0, 9.8, 9.4, 8.8, 8.0, 6.8, 5.2, 3.0]
    def build(m):
        for i, w in enumerate(widths):
            block = band if i in (3, 8) else base
            plus(m, "body", block, 0, i * 1.2, 0, w, 1.2, w, w * 0.18)
        # little dots round the upper band
        r = widths[8] / 2 + 0.06
        for x in (-1.3, 1.3):
            for cx, cz, ry in ((x, r, 0), (x, -r, 0), (r, x, 90), (-r, x, 90)):
                C(m, "body", dots, (cx, 10.2, cz), (0.9, 0.9, 0.12), (0, ry, 45))
        front = lambda a, b: max(widths[min(len(widths) - 1, int(y / 1.2))] for y in (a + 0.01, b - 0.01)) / 2 + 0.02
        for state, rows in EGG_FACES.items():
            face(m, "body", 0, 6.6, front, rows, state, 0.7)
    return build


decor_gingerbread = decor_model("decor_gingerbread", gingerbread(False), GINGER_FACES)
decor_gingerbread_girl = decor_model("decor_gingerbread_girl", gingerbread(True), GINGER_FACES)
decor_egg_pink = decor_model("decor_egg_pink", egg("pink_concrete", "yellow_concrete", "white_concrete"), EGG_FACES)
decor_egg_blue = decor_model("decor_egg_blue", egg("light_blue_concrete", "white_concrete", "pink_concrete"), EGG_FACES)
decor_egg_mint = decor_model("decor_egg_mint", egg("lime_concrete", "purple_concrete", "yellow_concrete"), EGG_FACES)
