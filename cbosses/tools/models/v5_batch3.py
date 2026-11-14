"""v5 batch 3: the rest of the normal bosses, imported from the vanilla Java models with vmodel."""
import math
from models import model, biped, quad
from build import Model
from texpaint import load, paintbox, Sheet, snap, autopal
from vmodel import vbuild

SPAWN, DEATH = {}, {}
R = math.radians


def setpivot(m, name, p):
    for b in m.bones:
        if b["name"] == name: b["pivot"] = list(p)


@model
def old_tusker():
    """An ancient hoglin: the vanilla hoglin, gone grey in the mane and muzzle, one tusk snapped off and
    the other grown long, crimson fungus sprouting on its back and a heavy gold-chain collar."""
    m = Model("old_tusker", "quad", 2.7)
    quad(m, body_y=17, legx=4, legz_front=8.5, legz_back=-10, neck_y=22, neck_z=12)
    setpivot(m, "legFL", (4, 14, 8.5)); setpivot(m, "legFR", (-4, 14, 8.5))
    setpivot(m, "legBL", (5, 11, -10)); setpivot(m, "legBR", (-5, 11, -10))
    img = load("hoglin.png")
    A = autopal(img, 4, must=("black_concrete", "white_concrete"))
    snap(img, A)
    P = {
        "body": (None, (0, 7, 0), (0, 0, 0), [((1, 1), (-8, -7, -13), (16, 14, 26))]),
        "mane": ("body", (0, -14, -5), (0, 0, 0), [((90, 33), (0, 0, -9), (0, 10, 19))]),
        "head": (None, (0, 2, -12), (0.87266, 0, 0), [((61, 1), (-7, -3, -19), (14, 6, 19))]),
        "earR": ("head", (-6, -2, -3), (0, 0, -0.698), [((1, 1), (-6, -1, -2), (6, 1, 4))]),
        "earL": ("head", (6, -2, -3), (0, 0, 0.698), [((1, 6), (0, -1, -2), (6, 1, 4))]),
        "hornR": ("head", (-7, 2, -12), (0, 0, 0), [((10, 13), (-1, -11, -1), (2, 11, 2))]),
        "hornL": ("head", (7, 2, -12), (0, 0, 0), [((1, 13), (-1, -11, -1), (2, 11, 2))]),
        "legFR": (None, (-4, 10, -8.5), (0, 0, 0), [((66, 42), (-3, 0, -3), (6, 14, 6))]),
        "legFL": (None, (4, 10, -8.5), (0, 0, 0), [((41, 42), (-3, 0, -3), (6, 14, 6))]),
        "legBR": (None, (-5, 13, 10), (0, 0, 0), [((21, 45), (-2.5, 0, -2.5), (5, 11, 5))]),
        "legBL": (None, (5, 13, 10), (0, 0, 0), [((0, 45), (-2.5, 0, -2.5), (5, 11, 5))]),
    }
    # the broken tusk: only a stump of the right horn is left
    P["hornR"] = ("head", (-7, 2, -12), (0, 0, 0), [((10, 13), (-1, -4, -1), (2, 4, 2))])
    bones = {"mane": "body", "earR": "head", "earL": "head", "hornR": "head", "hornL": "head"}
    kw = dict(allowed=A, speck=3, keep={"black_concrete", "white_concrete"})
    piv = vbuild(m, img, P, bones, **kw)
    setpivot(m, "head", piv["head"])
    # crimson fungus and nether wart on the back
    for x, z, s in ((-4, 4, 1.0), (3, -3, 1.3), (-2, -8, 0.8), (5, 6, 0.7)):
        m.c("body", "crimson_stem", (x, 24 + 1.2 * s, z), (0.8 * s, 2.4 * s, 0.8 * s))
        m.c("body", "nether_wart_block", (x, 24 + 2.6 * s, z), (3 * s, 1 * s, 3 * s))
        m.c("body", "shroomlight", (x + 0.6 * s, 24 + 2.0 * s, z + 0.6 * s), (0.6 * s, 0.6 * s, 0.6 * s), light=True)
    # a heavy gold chain collar behind the head
    for k in range(9):
        a = math.pi * (k / 8)
        m.c("body", "gold_block", (8.4 * math.cos(a), 12 + 9 * math.sin(a) + 3, 11.5), (1.6, 1.6, 1.2))
    # angry red eyes
    m.attacks = {"slam": "rear", "charge": "charge", "toss": "toss", "roar": "howl"}
    m.melee = "bite"
    return m


@model
def siegebreaker():
    """The ravager the illagers send at walls: the vanilla ravager in iron siege armour, a battering-ram
    plate bolted over its head, chains across its back and a war banner on a pole."""
    m = Model("siegebreaker", "quad", 1.9)
    quad(m, body_y=30, legx=8, legz_front=5, legz_back=-18, neck_y=31, neck_z=0)
    img = load("ravager.png")
    A = autopal(img, 5, must=("black_concrete",))
    snap(img, A)
    P = {
        "neck": (None, (0, -7, 5.5), (0, 0, 0), [((68, 73), (-5, -1, -18), (10, 10, 18))]),
        "head": ("neck", (0, 16, -17), (0, 0, 0), [((0, 0), (-8, -20, -14), (16, 20, 16)), ((0, 0), (-2, -6, -18), (4, 8, 4))]),
        "hornR": ("head", (-10, -14, -8), (1.0996, 0, 0), [((74, 55), (0, -14, -2), (2, 14, 4))]),
        "hornL": ("head", (8, -14, -8), (1.0996, 0, 0), [((74, 55), (0, -14, -2), (2, 14, 4), 0, True)]),
        "jaw": ("head", (0, -2, 2), (0, 0, 0), [((0, 36), (-8, 0, -16), (16, 3, 16))]),
        "body": (None, (0, 1, 2), (math.pi / 2, 0, 0), [((0, 55), (-7, -10, -7), (14, 16, 20)), ((0, 91), (-6, 6, -7), (12, 13, 18))]),
        "legBR": (None, (-8, -13, 18), (0, 0, 0), [((96, 0), (-4, 0, -4), (8, 37, 8))]),
        "legBL": (None, (8, -13, 18), (0, 0, 0), [((96, 0), (-4, 0, -4), (8, 37, 8), 0, True)]),
        "legFR": (None, (-8, -13, -5), (0, 0, 0), [((64, 0), (-4, 0, -4), (8, 37, 8))]),
        "legFL": (None, (8, -13, -5), (0, 0, 0), [((64, 0), (-4, 0, -4), (8, 37, 8), 0, True)]),
    }
    bones = {"neck": "body", "hornR": "head", "hornL": "head"}
    kw = dict(allowed=A, speck=6, keep={"black_concrete"}, coarse=("left", "right", "back", "top", "bottom"))
    piv = vbuild(m, img, P, bones, **kw)
    for n in ("head", "jaw", "legBR", "legBL", "legFR", "legFL"):
        setpivot(m, n, piv[n])
    setpivot(m, "head", piv["neck"])
    m.attacks = {"slam": "rear", "charge": "charge", "toss": "toss", "roar": "howl"}
    m.melee = "bite"
    return m
