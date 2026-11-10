"""v5 batch 2: painted-box bosses built on the vanilla mob models."""
import copy
import anims
from models import model, biped, quad
from build import Model
from texpaint import load, paintbox, box_faces, Sheet, rgb, snap, moss
from skin import skinbox

SPAWN, DEATH = {}, {}


def ominous_banner(s):
    """The raid captain's banner as a picture: white cloth, the grey and black illager face, a cyan band."""
    b = s.box(10, 18, 1, "white_wool")
    art = [
        "..........",
        "..........",
        "cccccccccc",
        "..........",
        "..kkkkkk..",
        "..kggggk..",
        "..g.gg.g..",
        "..gkggkg..",
        "..gggggg..",
        "...gkkg...",
        "...gggg...",
        "....gg....",
        "..........",
        "..k....k..",
        "...k..k...",
        "....kk....",
        "..........",
        "..........",
    ]
    K = {"k": "black_concrete", "g": "light_gray_concrete", "c": "cyan_concrete"}
    s.draw(b, "front", 0, 0, art, K)
    s.draw(b, "back", 0, 0, [r[::-1] for r in art], K)
    return b


@model
def pillager_captain():
    """The raid captain: the vanilla pillager scaled up, a heavy crossbow in hand and the ominous banner
    carried high on a pole strapped to his back."""
    m = Model("pillager_captain", "biped", 2.3)
    biped(m, hip=12, legx=2, neck=24, shoulder=22, armx=5)
    m.bone("bow", "armR", (-5, 11, 0.5))
    m.bone("banner", "body", (0, 24, -4))
    m.hold = {"bow": 0}
    m.bend = -40
    img = load("pillager.png")
    A = ["gray_concrete", "light_gray_concrete", "cyan_terracotta", "gray_terracotta", "black_concrete", "brown_terracotta",
         "dark_oak_planks", "white_concrete", "green_concrete", "light_gray_terracotta", "blue_terracotta"]
    snap(img, A)
    kw = dict(allowed=A, speck=3, keep={"black_concrete", "green_concrete", "white_concrete"})
    paintbox(m, "head", img, (0, 0), (-4, 24, -4), (8, 10, 8), **kw)
    paintbox(m, "head", img, (24, 0), (-1, 23, 4), (2, 4, 2), **kw)
    paintbox(m, "body", img, (16, 20), (-4, 12, -3), (8, 12, 6), **kw)
    paintbox(m, "body", img, (0, 38), (-4.5, 3.5, -3.5), (8, 20, 6), scale=9 / 8, skip=("top",), **kw)
    paintbox(m, "armR", img, (40, 46), (-8, 10, -2), (4, 12, 4), **kw)
    paintbox(m, "armL", img, (40, 46), (4, 10, -2), (4, 12, 4), mirror=True, **kw)
    paintbox(m, "legR", img, (0, 22), (-4, 0, -2), (4, 12, 4), **kw)
    paintbox(m, "legL", img, (0, 22), (0, 0, -2), (4, 12, 4), mirror=True, **kw)
    s = Sheet(128, 64)
    K = {"i": "iron_block", "k": "black_concrete", "d": "dark_oak_planks", "s": "white_wool"}
    # crossbow: a dark stock through the fist, two bent limbs and the string, a loaded arrow
    stock = s.box(1, 1, 10, "dark_oak_planks")
    paintbox(m, "bow", s.img, stock, (-5.5, 8.6, -3), (1, 1, 10), allowed=sorted(s.used))
    for side in (1, -1):
        limb = s.box(5, 1, 1, "spruce_planks")
        s.draw(limb, "front", 0, 0, ["i...."] if side > 0 else ["....i"], K)
        x0 = -5 + (0.5 if side > 0 else -5.5)
        paintbox(m, "bow", s.img, limb, (x0, 8.6, 5.4), (5, 1, 1), rot=(0, -22 * side, 0), origin=(-5, 9.1, 5.9), allowed=sorted(s.used))
    m.c("bow", "white_wool", (-5, 9.1, 4.1), (8.6, 0.25, 0.25))
    m.c("bow", "iron_block", (-5, 9.9, 6.2), (0.6, 0.6, 1.2))
    m.c("bow", "spruce_planks", (-5, 9.9, 2.8), (0.4, 0.4, 6.6))
    # the banner on its pole
    pole = s.box(1, 26, 1, "dark_oak_planks")
    paintbox(m, "banner", s.img, pole, (-0.5, 12, -4.5), (1, 26, 1), allowed=sorted(s.used))
    bar = s.box(11, 1, 1, "dark_oak_planks")
    paintbox(m, "banner", s.img, bar, (-5.5, 37, -4.5), (11, 1, 1), allowed=sorted(s.used))
    ban = ominous_banner(s)
    paintbox(m, "banner", s.img, ban, (-5, 19, -5.4), (10, 18, 1), allowed=sorted(s.used), shell=True, keep=set(K.values()) | {"cyan_concrete", "light_gray_concrete"})
    m.attacks = {"volley": "cast", "meteor": "roar", "shockwave": "stomp", "charge": "lunge"}
    m.melee = "swipe"
    return m


@model
def frostmaw():
    """A polar bear from the far north grown huge: the vanilla bear, with blue-white ice grown along its
    spine in jagged plates, ice caps on its shoulders, frosted paws and pale glowing eyes."""
    m = Model("frostmaw", "quad", 2.6)
    quad(m, body_y=14, legx=4, legz_front=7, legz_back=-8, neck_y=14, neck_z=13)
    for b in m.bones:
        if b["name"] == "legFL": b["pivot"] = [3.5, 10, 7]
        if b["name"] == "legFR": b["pivot"] = [-3.5, 10, 7]
        if b["name"] == "legBL": b["pivot"] = [4.5, 10, -8]
        if b["name"] == "legBR": b["pivot"] = [-4.5, 10, -8]
        if b["name"] == "jaw": b["pivot"] = [0, 12, 19]
    img = load("polarbear.png")
    A = ["white_concrete", "snow_block", "light_gray_concrete", "white_terracotta", "black_concrete", "gray_concrete", "quartz_block"]
    snap(img, A)
    kw = dict(allowed=A, speck=3, keep={"black_concrete", "gray_concrete"}, merge={"quartz_block": "white_concrete", "snow_block": "white_concrete"})
    o, r = (0, 15, -12), (90, 0, 0)
    paintbox(m, "body", img, (0, 19), (-7, 14, -16), (14, 14, 11), rot=r, origin=o, **kw)
    paintbox(m, "body", img, (39, 0), (-6, 28, -15), (12, 12, 10), rot=r, origin=o, **kw)
    paintbox(m, "head", img, (0, 0), (-3.5, 10, 12), (7, 7, 7), **kw)
    paintbox(m, "jaw", img, (0, 44), (-2.5, 10, 19), (5, 3, 3), **kw)
    paintbox(m, "head", img, (26, 0), (-4.5, 16, 16), (2, 2, 1), **kw)
    paintbox(m, "head", img, (26, 0), (2.5, 16, 16), (2, 2, 1), mirror=True, **kw)
    for b, x, z, uv, d in (("legBR", -6.5, -12, (50, 22), 8), ("legBL", 2.5, -12, (50, 22), 8), ("legFR", -5.5, 4, (50, 40), 6), ("legFL", 1.5, 4, (50, 40), 6)):
        paintbox(m, b, img, uv, (x, 0, z), (4, 10, d), mirror=x > 0, **kw)
        m.c(b, "packed_ice", (x + 2, 0.6, z + d / 2 + 0.2), (4.3, 1.2, d + 0.6))
    # ice along the spine: jagged plates leaning back, tallest over the shoulders
    for k, (z, h) in enumerate(((10, 6), (6, 7.5), (2, 6.5), (-2, 5.5), (-6, 4.5), (-10, 3.5))):
        blk = "blue_ice" if k % 2 else "packed_ice"
        m.c("body", blk, (0, 19 + h / 2 - 0.5, z), (2.6, h, 2.6), (-22, 0, 0), light=False)
        m.c("body", "packed_ice", (2.4 * (1 if k % 2 else -1), 18.6 + h / 4, z - 0.6), (1.6, h / 2, 1.6), (-18, 0, 14 * (1 if k % 2 else -1)))
    for s in (1, -1):
        m.c("body", "packed_ice", (4.8 * s, 17.6, 9), (3, 1.6, 5), (0, 0, -18 * s))
    for x in (-1.6, 1.6):
        m.c("head", "light_blue_concrete", (x, 14.2, 19.06), (0.9, 0.7, 0.1), light=True)
    m.attacks = {"slam": "rear", "frost": "howl", "charge": "charge", "toss": "toss"}
    m.melee = "bite"
    return m


@model
def bogged_hunter():
    """A bogged, the swamp skeleton, grown tall: its mossy bones and the mushrooms on its skull from the
    vanilla textures, a ragged moss cloak, a vine-wrapped bow and a quiver of poison arrows."""
    m = Model("bogged_hunter", "biped", 2.4)
    biped(m, hip=12, legx=2, neck=24, shoulder=22, armx=5)
    m.bone("bow", "armL", (5, 11, 0.5))
    m.bone("cape", "body", (0, 24, -2))
    m.hold = {"bow": 0}
    m.bend = -24
    img = load("bogged.png")
    img.alpha_composite(load("bogged_overlay.png"))
    A = ["white_concrete", "light_gray_concrete", "lime_terracotta", "green_terracotta", "moss_block", "brown_terracotta",
         "black_concrete", "gray_concrete", "red_concrete", "brown_mushroom_block"]
    snap(img, A)
    kw = dict(allowed=A, speck=2, keep={"black_concrete", "gray_concrete", "red_concrete"})
    paintbox(m, "head", img, (0, 0), (-4, 24, -4), (8, 8, 8), **kw)
    paintbox(m, "body", img, (16, 16), (-4, 12, -2), (8, 12, 4), **kw)
    paintbox(m, "armR", img, (40, 16), (-6, 10, -1), (2, 12, 2), **kw)
    paintbox(m, "armL", img, (40, 16), (4, 10, -1), (2, 12, 2), mirror=True, **kw)
    paintbox(m, "legR", img, (0, 16), (-3, 0, -1), (2, 12, 2), **kw)
    paintbox(m, "legL", img, (0, 16), (1, 0, -1), (2, 12, 2), mirror=True, **kw)
    s = Sheet(128, 64)
    K = {"m": "moss_block", "g": "green_terracotta", "l": "lime_terracotta", "r": "red_concrete", "w": "white_concrete", "b": "brown_terracotta", "k": "black_concrete"}
    # mushrooms growing out of the skull: a red one and a brown one
    for (x, z, col, w) in ((-2, 0, "red_concrete", 3), (2.4, -1.4, "brown_mushroom_block", 2.4)):
        m.c("head", "white_terracotta", (x, 33, z), (0.8, 2, 0.8))
        m.c("head", col, (x, 34.3, z), (w, 1, w))
    m.c("head", "white_concrete", (-2.6, 34.85, 0.4), (0.6, 0.15, 0.6))
    # ragged moss cloak hanging from the shoulders
    cape = s.box(10, 16, 1, "moss_block")
    rows = ["gggggggggg"] + ["m.m..m..lm"] + ["." * 10] * 9 + [".l....m..."] + ["....l....."] + ["m.......m."] + ["mm.m.mm.m."] + ["g..g..g..g"]
    s.draw(cape, "back", 0, 0, rows, K)
    s.draw(cape, "front", 0, 0, rows, K)
    paintbox(m, "cape", s.img, cape, (-5, 8, -3.6), (10, 16, 1), allowed=sorted(s.used), keep=set(K.values()))
    collar = s.box(10, 2, 6, "moss_block", shade="green_terracotta")
    s.draw(collar, "front", 0, 0, ["l..l..l..l"], K)
    paintbox(m, "body", s.img, collar, (-5, 22, -3), (10, 2, 6), allowed=sorted(s.used))
    # vine bow: a bent stave of dark wood wrapped in vines, a taut string
    for k, (dy, a) in enumerate(((0, 0), (3.4, 18), (-3.4, -18), (6.4, 34), (-6.4, -34))):
        blk = "dark_oak_planks" if k % 2 == 0 else "green_terracotta"
        m.c("bow", blk, (5, 9 + dy, 1.6 + abs(dy) * -0.12), (0.9, 3.4, 0.9), (a, 0, 0))
    m.c("bow", "white_wool", (5, 9, -0.6), (0.2, 13, 0.2))
    # quiver on the back
    q = s.box(2, 7, 2, "brown_terracotta")
    s.draw(q, "back", 0, 0, ["gg", "..", "gg"], K)
    paintbox(m, "body", s.img, q, (1, 16, -4.4), (2, 7, 2), rot=(0, 0, -25), origin=(2, 19, -3.4), allowed=sorted(s.used))
    for dx in (-0.4, 0.4):
        m.c("body", "lime_concrete", (2.6 + dx, 24.4, -3.4), (0.4, 1.6, 0.4), (0, 0, -25), light=True)
    m.attacks = {"volley": "cast", "poison": "swipe", "vines": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m


@model
def shulker_matriarch():
    """The mother of the shulkers: the vanilla shulker grown huge, purpur shell half open on her pale
    head, four little shulkers orbiting her, and a ring of end rods along the lid."""
    m = Model("shulker_matriarch", "float", 2.8)
    m.bone("core", "root", (0, 8, 0))
    m.bone("head", "core", (0, 6, 0))
    m.bone("lid", "core", (0, 8, -8))
    m.bone("ring1", "core", (0, 10, 0))
    img = load("shulker.png")
    A = ["purpur_block", "purple_terracotta", "end_stone", "black_concrete", "white_terracotta"]
    snap(img, A)
    kw = dict(allowed=A, speck=4, keep={"black_concrete"}, merge={"white_terracotta": "end_stone"})
    paintbox(m, "core", img, (0, 28), (-8, 0, -8), (16, 8, 16), **kw)
    paintbox(m, "lid", img, (0, 0), (-8, 8, -8), (16, 12, 16), **kw)
    paintbox(m, "head", img, (0, 52), (-3, 6, -3), (6, 6, 6), **kw)
    for k in range(6):
        x = -6.6 + k * 2.64
        m.c("lid", "end_rod", (x, 21.2, 7.4), (0.5, 2.4, 0.5), light=True)
    # four small shulkers orbiting
    for k, (x, z) in enumerate(((13, 0), (-13, 0), (0, 13), (0, -13))):
        m.c("ring1", "purpur_block", (x, 10, z), (4, 2, 4))
        m.c("ring1", "purple_terracotta", (x, 12, z), (4, 2.4, 4), (-20, 0, 0), (x, 12, z - 2))
        m.c("ring1", "end_stone", (x, 11.2, z + 0.4), (1.6, 1.6, 1.6))
    m.rest("lid", (-26, 0, 0))
    m.no_elbows = True
    m.attacks = {"orbs": "spin", "levitate": "raise", "shockwave": "pulse", "dive": "dive"}
    m.melee = "pulse"
    return m


@model
def weeping_ghast():
    """A ghast that never stops crying: the vanilla ghast, huge, its tear-streaked face glowing blue where the
    tears run, nine long tentacles drifting under it, and soul-fire teardrops falling from its eyes."""
    m = Model("weeping_ghast", "float", 3.0)
    m.bone("core", "root", (0, 22, 0))
    m.bone("head", "core", (0, 22, 0))
    img = load("ghast.png")
    A = ["white_concrete", "light_gray_concrete", "gray_concrete", "black_concrete", "white_terracotta", "light_blue_concrete", "snow_block"]
    snap(img, A)
    # the tear streaks under the eyes glow pale blue
    fu, fv, fw, fh = box_faces(img, 0, 0, 16, 16, 16)["front"]
    for y in range(fv, fv + fh):
        for x in range(fu, fu + fw):
            p = img.getpixel((x, y))[:3]
            if p == rgb("gray_concrete")[:3] and y > fv + 7:
                img.putpixel((x, y), rgb("light_blue_concrete"))
    # tears: two streaks running from the closed eyes down the cheeks
    for (x, y0, y1) in ((4, 6, 13), (11, 6, 12), (5, 8, 10), (10, 8, 11)):
        for y in range(y0, y1):
            img.putpixel((fu + x, fv + y), rgb("light_blue_concrete"))
    kw = dict(allowed=A, speck=0, passes=0, lit={"light_blue_concrete"}, merge={"snow_block": "white_concrete"})
    paintbox(m, "head", img, (0, 0), (-8, 14, -8), (16, 16, 16), **kw)
    lengths = [12, 9, 13, 10, 14, 8, 11, 13, 9]
    for i in range(9):
        x = ((i % 3) - 1) * 5 - (i // 3 % 2) * 1.5 + 0.75
        z = ((i // 3) - 1) * 5
        b = "tent%d" % i
        m.bone(b, "head", (x, 14, z))
        L = lengths[i]
        paintbox(m, b, img, (0, 0), (x - 1, 14 - L, z - 1), (2, L, 2), **kw)
    idle = copy.deepcopy(anims.RIGS["float"]["idle"])
    for i in range(9):
        a, bb, sg = 8 + i % 3 * 3, 6 + i % 2 * 4, 1 if i % 2 else -1
        idle["bones"]["tent%d" % i] = {"rot": anims.K((0, (a * sg, 0, bb * sg)), (1.5, (-a * sg, 0, -bb * sg)), (3.0, (a * sg, 0, bb * sg)))}
    m.anims = {"idle": idle}
    m.no_elbows = True
    m.attacks = {"meteor": "pulse", "roar": "raise", "orbs": "spin", "dive": "dive"}
    m.melee = "pulse"
    return m


@model
def cinderheart():
    """A magma cube the size of a house: eight stacked slices of dark crusted magma with lava glowing in the
    seams, the molten core visible between them, two burning eyes. When it hops the slices spread apart."""
    m = Model("cinderheart", "slime", 7.0)
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 4, 0))
    m.bone("mouth", "body", (0, 3, 4))
    s = Sheet(128, 128)
    K = {"n": "nether_bricks", "r": "red_nether_bricks", "m": "magma_block", "o": "orange_concrete", "y": "yellow_concrete", "k": "black_concrete", "s": "shroomlight"}
    sl = []
    for i in range(8):
        b = "slice%d" % i
        m.bone(b, "body", (0, 7.5 - i, 0))
        box = s.box(8, 1, 8, "nether_bricks", top="red_nether_bricks" if i == 0 else "nether_bricks")
        # glowing seams run round each slice in short lava runs
        for f in ("front", "back", "left", "right"):
            pat = ("..o.....", ".....o..", "o......o", "...oo...", "........", ".o....o.", "....o...", "..o..o..")[(i * 3 + len(f)) % 8]
            if f == "front" and i in (2, 3, 4): pat = "........"
            s.draw(box, f, 0, 0, [pat], K)
        if i == 3:
            s.draw(box, "front", 0, 0, [".yo..oy."], K)
        paintbox(m, b, s.img, box, (-4, 7 - i, -4), (8, 1, 8), allowed=sorted(s.used), lit={"yellow_concrete", "orange_concrete"}, keep=set(K.values()))
    core = s.box(4, 4, 4, "shroomlight")
    paintbox(m, "inner", s.img, core, (-2, 2, -2), (4, 4, 4), allowed=sorted(s.used), lit={"shroomlight"})
    hop = copy.deepcopy(anims.RIGS["slime"].get("hop") or anims.RIGS["slime"]["idle"])
    hop.setdefault("bones", {})
    for i in range(8):
        spread = (3.5 - i) * -0.6
        hop["bones"]["slice%d" % i] = {"pos": anims.K((0, (0, 0, 0)), (0.3, (0, spread, 0)), (0.7, (0, spread, 0)), (1.0, (0, 0, 0)))}
    m.anims = {"hop": hop}
    m.attacks = {"minions": "burst", "slam": "slam", "volley": "spit", "leap": "hop"}
    m.melee = "slam"
    return m
