"""v5 bosses: big painted boxes in the Blockbench style. Each box carries a pixel-art picture on every
face (texpaint), so a boss is a handful of solid shapes with real detail instead of a pile of small cubes."""
from models import model, biped
from build import Model
from texpaint import load, paintbox, moss, box_faces, Sheet, rgb, snap
from skin import skinbox

SPAWN, DEATH = {}, {}


@model
def old_ironroot():
    """An iron golem left standing in a meadow for a hundred years: the vanilla golem's build, its plates
    gone pale, moss and dandelions grown over its shoulders, back and legs, and a sapling in a clump of
    moss rooted on its left shoulder."""
    m = Model("old_ironroot", "biped", 2.3)
    biped(m, hip=15, legx=4.5, neck=33, shoulder=33, armx=11)
    m.no_elbows = True
    img = load("iron_golem.png")
    boxes = [((0, 0), (8, 10, 8)), ((0, 40), (18, 12, 11)), ((60, 21), (4, 30, 6)), ((60, 58), (4, 30, 6)), ((37, 0), (6, 16, 5)), ((60, 0), (6, 16, 5))]
    rects = []
    for uv, (w, h, d) in boxes:
        for face, r in box_faces(img, uv[0], uv[1], w, h, d).items():
            if face != "bottom": rects.append((face, r))
    snap(img, ["white_concrete", "quartz_block", "light_gray_concrete", "gray_concrete", "black_concrete", "red_concrete", "green_terracotta", "lime_terracotta"])
    # the moss: heavy on the top and shoulders, patchy down the front, thick over the back
    moss(img, [r for f, r in rects if f == "top"], 11, cover=1.5, flower_rate=0.08, cell=3)
    moss(img, [r for f, r in rects if f in ("left", "right", "back")], 12, cover=0.4, top_bias=1.0, flower_rate=0.05, cell=3)
    face = box_faces(img, 0, 0, 8, 10, 8)["front"]
    moss(img, [r for f, r in rects if f == "front" and r != face], 13, cover=0.3, top_bias=1.5, flower_rate=0.1, cell=3)
    A = ["white_concrete", "quartz_block", "white_terracotta", "light_gray_concrete", "light_gray_terracotta", "gray_concrete",
         "moss_block", "green_terracotta", "lime_terracotta", "yellow_concrete", "red_concrete", "black_concrete", "brown_terracotta"]
    kw = dict(allowed=A, speck=5, merge={"light_gray_terracotta": "light_gray_concrete", "gray_concrete": "light_gray_concrete", "quartz_block": "white_concrete", "brown_terracotta": "light_gray_concrete", "lime_terracotta": "moss_block"}, keep={"red_concrete", "yellow_concrete", "black_concrete"})
    paintbox(m, "head", img, (0, 0), (-4, 33, -0.5), (8, 10, 8), base="white_concrete", **dict(kw, speck=2))
    paintbox(m, "head", img, (24, 0), (-1, 32, 7.5), (2, 4, 2), **kw)
    paintbox(m, "body", img, (0, 40), (-9, 21, -5), (18, 12, 11), base="white_concrete", **kw)
    paintbox(m, "body", img, (0, 70), (-5, 15.5, -3.5), (9, 5, 6), scale=10 / 9, **kw)
    paintbox(m, "armR", img, (60, 21), (-13, 3.5, -3), (4, 30, 6), base="white_concrete", **kw)
    paintbox(m, "armL", img, (60, 58), (9, 3.5, -3), (4, 30, 6), base="white_concrete", **kw)
    paintbox(m, "legR", img, (37, 0), (-7.5, 0, -2), (6, 16, 5), base="white_concrete", **kw)
    paintbox(m, "legL", img, (60, 0), (1.5, 0, -2), (6, 16, 5), mirror=True, base="white_concrete", **kw)
    # a clump of moss on the left shoulder with a sapling growing out of it
    s = Sheet(64, 64)
    clump = s.box(6, 4, 6, "moss_block", shade="green_terracotta")
    s.draw(clump, "front", 1, 1, ["y..", "..g"], {"y": "yellow_concrete", "g": "lime_terracotta"})
    trunk = s.box(1, 6, 1, "spruce_planks")
    crown = s.box(5, 4, 5, "green_concrete", shade="green_terracotta")
    s.draw(crown, "front", 0, 0, [".l.l.", "l...l"], {"l": "lime_terracotta"})
    k2 = dict(allowed=sorted(s.used), speck=0)
    paintbox(m, "armL", s.img, clump, (8.5, 33, -3), (6, 4, 6), **k2)
    paintbox(m, "armL", s.img, trunk, (11, 37, 0), (1, 6, 1), **k2)
    paintbox(m, "armL", s.img, crown, (9, 42, -2), (5, 4, 5), **k2)
    m.attacks = {"slam": "slam", "toss": "swipe", "roots": "stomp", "quake": "stomp"}
    m.melee = "swipe"
    return m


@model
def grave_marshal():
    """A skeleton general from a lost war: the vanilla skeleton's skull and ribs inside dark purple plate,
    with huge frayed pauldrons, armoured boots and bracers, a stone war hammer in its right hand and a
    tower shield on its left arm with the arrows of its last battle still stuck in it."""
    m = Model("grave_marshal", "biped", 2.1)
    biped(m, hip=14, legx=2.6, neck=26, shoulder=25, armx=6.4)
    m.bone("hammer", "armR", (-6.4, 13.5, 0.5))
    m.bone("shield", "armL", (8.6, 15, 0))
    m.hold = {"hammer": 55, "shield": 0}
    m.bend = -30
    sk = load("skeleton.png")
    snap(sk, ["white_concrete", "light_gray_concrete", "gray_concrete", "black_concrete"])
    bone = dict(allowed=["white_concrete", "light_gray_concrete", "gray_concrete", "black_concrete"], speck=2, keep={"black_concrete", "gray_concrete"})
    P, P2, PD, BK, TR, GM = "blue_terracotta", "purple_terracotta", "black_terracotta", "black_concrete", "yellow_terracotta", "magenta_concrete"
    s = Sheet(128, 128)
    K = {"p": P, "q": P2, "d": PD, "k": BK, "t": TR, "g": GM, "w": "white_concrete", "l": "light_gray_concrete"}
    # skull and bones from the vanilla skeleton
    paintbox(m, "head", sk, (0, 0), (-4, 26, -4), (8, 8, 8), **bone)
    paintbox(m, "body", sk, (16, 16), (-4, 14, -2), (8, 12, 4), **bone)
    for side, b, x in ((1, "legL", 1.6), (-1, "legR", -3.6)):
        paintbox(m, b, sk, (0, 16), (x, 5, -1), (2, 9, 2), **bone)
        boot = s.box(4, 6, 5, P, shade=PD, top=PD)
        s.draw(boot, "front", 0, 0, ["tttt", "pqqp"], K)
        s.rect(boot, "front", 0, 4, 4, 2, BK)
        paintbox(m, b, s.img, boot, (x - 1, 0, -2), (4, 6, 5), allowed=sorted(s.used))
    # chest plate over the upper ribs, a belt with a magenta gem, a ragged tabard
    plate = s.box(9, 6, 5, P, shade=PD, edge=None, top=PD)
    s.draw(plate, "front", 0, 0, ["ddddddddd", "dpppqpppd", ".ppqqqpp.", "..ppqpp..", "...ppp..."], K)
    s.draw(plate, "back", 0, 0, ["ddddddddd", "dpppppppd"], K)
    paintbox(m, "body", s.img, plate, (-4.5, 20, -2.5), (9, 6, 5), allowed=sorted(s.used))
    belt = s.box(9, 2, 5, BK)
    s.draw(belt, "front", 3, 0, ["tgt", "tgt"], K)
    paintbox(m, "body", s.img, belt, (-4.5, 14, -2.5), (9, 2, 5), allowed=sorted(s.used), keep={GM})
    tab = s.box(4, 6, 1, P, shade=PD)
    s.draw(tab, "front", 0, 0, ["dddd", "....", ".gg.", ".gg.", "....", "q.q."], K)
    paintbox(m, "body", s.img, tab, (-2, 8, 2.2), (4, 6, 1), allowed=sorted(s.used), keep={GM})
    # pauldrons: wide, heavy, frayed along the bottom edge
    for side, a in ((1, "armL"), (-1, "armR")):
        pd = s.box(6, 5, 7, P, shade=PD, top=P)
        for f in ("front", "back", "left", "right"):
            s.draw(pd, f, 0, 0, ["d" * 7], K)
            fw = s.face(pd, f)[2]
            s.draw(pd, f, 0, 4, [("k." * 4)[:fw]], K)
        s.draw(pd, "top", 0, 0, ["dddddd", "dppppd", "dppppd", "dppppd", "dppppd", "dppppd", "dddddd"], K)
        x = 6.4 * side
        paintbox(m, a, s.img, pd, (x - 3 + side * 0.6, 22.5, -3.5), (6, 5, 7), allowed=sorted(s.used))
        paintbox(m, a, sk, (40, 16), (x - 1, 13, -1), (2, 12, 2), **bone)
        br = s.box(3, 5, 3, PD, shade=BK)
        s.draw(br, "front", 0, 0, ["ttt"], K)
        paintbox(m, a, s.img, br, (x - 1.5, 13, -1.5), (3, 5, 3), allowed=sorted(s.used))
    # the war hammer: a dark haft through the right fist, a big stone head
    haft = s.box(1, 15, 1, "dark_oak_planks")
    paintbox(m, "hammer", s.img, haft, (-6.9, 10, 0), (1, 15, 1), allowed=sorted(s.used))
    hd = s.box(8, 6, 6, "polished_andesite", shade="gray_concrete", top="smooth_stone")
    s.draw(hd, "front", 0, 0, ["llllllll"], K)
    for f in ("left", "right", "back"):
        s.draw(hd, f, 0, 0, ["llllllll"], K)
    paintbox(m, "hammer", s.img, hd, (-10.4, 23, -2.5), (8, 6, 6), allowed=sorted(s.used))
    # the tower shield: dark planks in a gold frame, a purple boss, three arrows stuck in it
    sh = s.box(1, 16, 12, "dark_oak_planks")
    face = ["t" * 12] + ["t" + "." * 10 + "t" for _ in range(14)] + ["t" * 12]
    s.draw(sh, "left", 0, 0, face, K)
    s.draw(sh, "left", 4, 6, ["dppd", "pqqp", "pqqp", "dppd"], K)
    s.draw(sh, "right", 0, 0, face, K)
    paintbox(m, "shield", s.img, sh, (9.6, 7, -6), (1, 16, 12), allowed=sorted(s.used))
    for (y, z, a) in ((19, 3, 20), (12, -3, -15), (9.5, 2.5, 35)):
        m.c("shield", "dark_oak_planks", (13.4, y, z), (6, 0.4, 0.4), (0, a, 8), (10.6, y, z))
        m.c("shield", "white_concrete", (15.8, y + 0.3, z + 2.4 * (a / 90)), (1.6, 1.0, 0.2), (0, a, 8), (10.6, y, z))
    m.attacks = {"slam": "slam", "charge": "lunge", "volley": "cast", "shockwave": "swipe"}
    m.melee = "swipe"
    return m


@model
def mayor_grumble():
    """The mayor as the meme: one big villager head walking on two stubby legs that stand right in front
    of its face, with flat feet poking forward. A thick dark unibrow sticks out over the eyes, the left leg
    stands where the nose would be, the right one at the corner of the face, the mouth peeks out between."""
    m = Model("mayor_grumble", "biped", 4.2)
    biped(m, hip=5, legx=1, neck=1, shoulder=6, armx=0)
    for b in m.bones:
        if b["name"] == "legL": b["pivot"] = [3.7, 5, 5]
        if b["name"] == "legR": b["pivot"] = [-1.1, 5, 5]
    m.no_elbows = True
    SK, SK2, SK3, BR = "terracotta", "white_terracotta", "brown_terracotta", "black_terracotta"
    s = Sheet(64, 64)
    K = {"a": SK2, "b": SK3, "w": "white_concrete", "g": "green_concrete", "m": "red_terracotta", "k": BR, "p": "packed_mud", "d": "packed_mud"}
    head = s.box(8, 8, 8, SK)
    # the face under the brow: white and green eyes, the dark mouth
    s.draw(head, "front", 0, 0, [
        "........",
        "........",
        "........",
        "........",
        "gw...wg.",
        "gw...wg.",
        ".....m..",
        ".....m..",
    ], K)
    used = lambda: sorted(s.used)
    paintbox(m, "head", s.img, head, (-4, 0.8, -4), (8, 8, 8), allowed=used(), keep=set(K.values()))
    # the unibrow: a dark slab across the whole face, sticking out over the eyes
    m.c("head", BR, (0, 5.3, 4.3), (8.0, 1.0, 0.6))
    # the legs: the left one where the nose would be, the right one at the corner of the face, both with
    # a flat foot pointing forward
    for b, x, fx in (("legR", -1.0, -1.8), ("legL", 4.2, 4.0)):
        leg = s.box(2, 5, 2, SK)
        paintbox(m, b, s.img, leg, (x - 0.85, 0.6, 4.05), (2, 5, 2), scale=0.85, allowed=used(), keep=set(K.values()))
        foot = s.box(3, 1, 4, SK, top=SK)
        paintbox(m, b, s.img, foot, (fx - 1.2, 0, 4.4), (3, 1, 4), scale=0.85, allowed=used(), keep=set(K.values()))
    m.attacks = {"minions": "roar", "volley": "cast", "quake": "stomp", "roar": "roar"}
    m.melee = "stomp"
    return m
