"""v12: the final pass. Ten big bosses the user wanted gone are replaced by new ones (same ids, so arenas,
schedules and player data stay), Frost Yeti, the Cinder Devil and Horngut grow into big bosses, and the minis
are redrawn. Every model is textured (grain blocks, 2-3 tone patches), has a real face, bends at its joints,
stands on its own centre and moves while it stands. Two-body bosses are two separate models that fight on
their own (see PARTNERS)."""
import zlib
from models import model, biped, limb, horn
from build import Model
from texpaint import Sheet
from v2_recipes import S, fx, gone
from v11_new import tb as _tb, mottle, boss_recipe, legs2, arms2
import v9_minis


def tb(*a, rate=0.22, **kw):
    """Mostly clean colour: a light touch of a second tone, not a patchwork."""
    return _tb(*a, rate=rate * 0.3, **kw)
import anims
from anims import K, Z

SPAWN, DEATH = {}, {}
BIG_INFO = {}       # id -> bosses.yml values for the new and promoted big bosses
MINI_INFO = {}      # id -> bosses.yml values for redrawn minis (name, title, entity, theme, bar, extra, movement)
PARTNERS = {}       # main id -> partner id (the second body of a two-body boss)
PARTNER_INFO = {}   # partner id -> bosses.yml values
REVISED = set()     # ids whose bosses.yml entry is replaced on servers that already have it (rewards are kept)

# ---------------------------------------------------------------------------------------------------- helpers


def face(w, h, ey=None, gap=None, ew=2, eh=2, brow=True, angry=True, mouth="grin", mw=None, my=None, nose=0, cheeks=False,
         glow=False, catch=True):
    """A face picture w x h: eyes with a light catch, brows, a nose and a mouth, as rows of keys
    (s skin, k pupil, w white, b brow, m mouth, t tooth, n nose, c cheek, e glowing eye)."""
    g = [["s"] * w for _ in range(h)]

    def put(x, y, c):
        if 0 <= x < w and 0 <= y < h: g[y][x] = c
    ey = max(1, h // 3) if ey is None else ey
    gap = max(1, w // 4) if gap is None else gap
    lx = (w - gap) // 2 - ew
    rx = lx + ew + gap
    for x0, side in ((lx, 1), (rx, -1)):
        for j in range(eh):
            for i in range(ew):
                put(x0 + i, ey + j, "e" if glow else "k")
        if catch and not glow: put(x0 + (ew - 1 if side == 1 else 0), ey, "w")
        if brow:
            for i in range(-1, ew + 1):
                inner = (i >= ew - 1) if side == 1 else (i <= 0)
                put(x0 + i, ey - 1 if (inner or not angry) else ey - 2, "b")
        if cheeks: put(x0 - 1 if side == 1 else x0 + ew, ey + eh + 1, "c")
    ny = ey + eh
    if nose:
        for i in range(2):
            for j in range(nose):
                put(w // 2 - 1 + i, ny - 1 + j, "n")
    mw = mw or max(2, w // 2)
    my = ny + nose + (1 if nose else 1) if my is None else my
    x0 = (w - mw) // 2
    if mouth == "grin":
        for i in range(mw): put(x0 + i, my, "t" if i % 2 else "m")
        for i in range(1, mw - 1): put(x0 + i, my + 1, "m")
    elif mouth == "teeth":
        for i in range(mw): put(x0 + i, my, "t")
        for i in range(mw): put(x0 + i, my + 1, "m")
    elif mouth == "fangs":
        for i in range(mw): put(x0 + i, my, "m")
        put(x0, my + 1, "t"); put(x0 + mw - 1, my + 1, "t")
    elif mouth == "frown":
        for i in range(1, mw - 1): put(x0 + i, my, "m")
        put(x0, my + 1, "m"); put(x0 + mw - 1, my + 1, "m")
    elif mouth == "smile":
        put(x0, my, "m"); put(x0 + mw - 1, my, "m")
        for i in range(1, mw - 1): put(x0 + i, my + 1, "m")
    elif mouth == "o":
        for i in range(mw): put(x0 + i, my, "m"); put(x0 + i, my + 1, "m")
    elif mouth == "line":
        for i in range(mw): put(x0 + i, my, "m")
    return ["".join(r) for r in g]


def idle(rig, extra, length=None):
    base = anims.RIGS[rig]["idle"]
    out = {"length": length or base["length"], "loop": True, "bones": dict(base["bones"])}
    out["bones"].update(extra)
    return {"idle": out}


def sway(axis, amt, length=4.0, phase=0.0, base=(0, 0, 0)):
    """A smooth back and forth on one axis (0 x, 1 y, 2 z) for loose parts: hats, tails, chains, capes.
    phase (0..1) shifts it in time so neighbouring parts lag behind each other."""
    import math
    keys = []
    for k in range(9):
        t = length * k / 8
        r = list(base); r[axis] += round(amt * math.sin(2 * math.pi * (k / 8 + phase)), 2)
        keys.append((t, tuple(r)))
    return K(*keys)


def bob(amt, length=3.0, phase=0.0):
    a, b = (0, amt * 0.0, 0), (0, amt, 0)
    if phase:
        return K((0, b), (length / 2, a), (length, b))
    return K((0, a), (length / 2, b), (length, a))


def quad4(m, body_y, legx, zf, zb, neck_y, neck_z, head_z):
    """Four legs, a neck and a head (the head turns on the neck), a jaw and a tail."""
    m.bone("body", "root", (0, body_y, 0))
    m.mbone("legFL", "body", (legx, body_y, zf))
    m.mbone("legBL", "body", (legx, body_y, zb))
    m.bone("neck", "body", (0, neck_y, neck_z))
    m.bone("head", "neck", (0, neck_y, head_z))
    m.bone("jaw", "head", (0, neck_y - 2, head_z + 2))
    m.bone("tail", "body", (0, body_y + 4, zb - 4))


def big(id, name, title, entity, theme, bar, extra=(), minion=None, items=(), top=(), money=60000, recipe=None, movement=None, fly=None,
        damage=12, armor=8, speed=None, revised=True):
    def deco(fn):
        BIG_INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, minions=3 if minion else 0,
                            extra=list(extra), items=list(items), top_items=list(top), money=money, top_money=money * 3,
                            damage=damage, armor=armor, **({"movement": movement} if movement else {}), **({"fly_height": fly} if fly else {}),
                            **({"speed": speed} if speed else {}))
        if revised: REVISED.add(id)
        SPAWN[id], DEATH[id] = recipe
        return model(fn)
    return deco


def mini(id, name, title, entity="ZOMBIE", theme="nature", bar="GREEN", extra=(), minion=None, recipe=None, movement=None):
    """A redrawn mini: replaces the old one with this id (or adds it), keeps its place in the list."""
    def deco(fn):
        if id not in v9_minis.MINIS: v9_minis.MINIS.append(id)
        v9_minis.INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, extra=list(extra),
                                 **({"movement": movement} if movement else {}))
        sp, de = recipe or v9_minis.generic()
        v9_minis.SPAWN[id], v9_minis.DEATH[id] = sp, de
        REVISED.add(id)
        return model(fn)
    return deco


def partner(main, id, name, title, entity="ZOMBIE", theme="nature", bar="GREEN", extra=(), recipe=None, movement=None, speed=None, tier="mini"):
    """The second body of a two-body boss: its own model, its own health bar and its own target."""
    def deco(fn):
        # 1.3.2: the little ones are their own mini bosses now, not second bodies
        REVISED.add(main)
        return mini(id, name, title, entity, theme, bar, extra, None, recipe, movement)(fn)
        PARTNERS[main] = id
        PARTNER_INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, extra=list(extra), tier=tier,
                                **({"movement": movement} if movement else {}), **({"speed": speed} if speed else {}))
        sp, de = recipe or v9_minis.generic()
        SPAWN[id], DEATH[id] = sp, de
        REVISED.add(id)
        return model(fn)
    return deco


def drop(old):
    """Takes a mini out of the mini list (it became a big boss)."""
    if old in v9_minis.MINIS: v9_minis.MINIS.remove(old)
    v9_minis.INFO.pop(old, None)


def gen(part, sin, sdie, block, pin=1.2, anim="roar", die="die_front"):
    return v9_minis.generic(part, sin, sdie, block, pin, anim, die)


# palettes: (base, tones) with 2-3 tones of the same hue so faces read as pixel texture, not plastic
FUR_W = ("white_wool", [("snow_block", 3), ("light_gray_wool", 2), ("white_concrete", 1)])
FUR_D = ("gray_wool", [("black_wool", 2), ("gray_concrete", 2), ("light_gray_wool", 1)])
FUR_B = ("brown_wool", [("brown_terracotta", 3), ("brown_concrete", 2), ("terracotta", 1)])
BARK = ("dark_oak_log", [("spruce_log", 2), ("brown_terracotta", 2), ("dark_oak_planks", 1)])
STUMP = ("stripped_oak_log", [("oak_planks", 2), ("birch_planks", 1), ("stripped_birch_log", 1)])
MOSS = ("moss_block", [("green_terracotta", 3), ("lime_terracotta", 1), ("azalea_leaves", 1)])
RED = ("red_terracotta", [("red_concrete", 2), ("nether_bricks", 1), ("brown_terracotta", 1)])
NAVY = ("gray_concrete", [("black_concrete", 3), ("cyan_concrete", 1), ("cyan_terracotta", 2)])
ROBE = ("black_wool", [("gray_wool", 2), ("black_concrete", 2), ("blue_terracotta", 1)])
IRON = ("iron_block", [("light_gray_concrete", 2), ("smooth_stone", 2), ("andesite", 1)])
ORC = ("green_terracotta", [("lime_terracotta", 2), ("moss_block", 2), ("green_concrete", 1)])
LEATHER = ("brown_terracotta", [("brown_concrete", 2), ("terracotta", 2), ("spruce_planks", 1)])
SKIN = ("pink_terracotta", [("terracotta", 2), ("white_terracotta", 1)])
BONE = ("bone_block", [("white_terracotta", 2), ("diorite", 2), ("birch_planks", 1)])
GOLD = ("gold_block", [("yellow_concrete", 2), ("orange_terracotta", 1)])


def T(m, s, bone, size, lo, pal, rate=0.24, cell=2, **kw):
    """tb with a palette tuple. Patches are kept chunky (cell 2) and sparse enough to stay in budget."""
    return tb(m, s, bone, size, lo, pal[0], pal[1], rate=rate * getattr(s, 'rate', RATE), cell=cell, **kw)


RATE = 0.6


def eyes_lit(*blocks):
    return list(blocks)


# ================================================================================================ big bosses


@big("abyssal_eye", "<gradient:#0b3d91:#ffe066><bold>The Lantern Angler</bold></gradient>", "Light at the Bottom of the Sea", "BLAZE", "water", "BLUE",
     extra=["frost", "pull"], minion="DROWNED", movement="hover", fly=3, items=["PRISMARINE_SHARD 24", "SEA_LANTERN 6", "DIAMOND 3"], top=["HEART_OF_THE_SEA 1"],
     recipe=boss_recipe("BUBBLE", "ENTITY_ELDER_GUARDIAN_AMBIENT", "ENTITY_ELDER_GUARDIAN_DEATH", "dark_prismarine", 0.7, "pulse", "die_drop", ground_block="PRISMARINE"))
def abyssal_eye():
    """A deep sea anglerfish swimming through the air: a huge dark round head with a jutting underbite
    full of needle teeth, small glowing yellow eyes, a glowing lure on a stalk that bends over its face,
    side fins that paddle and a tail that sweeps from side to side."""
    m = Model("abyssal_eye", "float", 2.0)
    m.bone("core", "root", (0, 16, 0))
    m.bone("head", "core", (0, 18, 2))
    m.bone("jaw", "head", (0, 12, 4))
    m.bone("armL", "core", (10, 16, 0)); m.bone("armR", "core", (-10, 16, 0))
    m.bone("ring1", "core", (0, 16, 0))
    m.bone("lure1", "head", (0, 30, 2)); m.bone("lure2", "lure1", (0, 36, 6)); m.bone("lure3", "lure2", (0, 36, 13))
    m.bone("tail1", "core", (0, 18, -8)); m.bone("tail2", "tail1", (0, 18, -16))
    s = Sheet(512, 256)
    KK = {"s": "gray_concrete", "k": "black_concrete", "e": "yellow_concrete", "t": "white_concrete", "m": "black_concrete", "b": "cyan_concrete"}
    # the head-body: dark navy with lighter belly and a few glowing freckles
    T(m, s, "head", (18, 16, 18), (-9, 12, -8), NAVY, 0.22, front=[
        "ssssssssssssssssss", "ssssssssssssssssss", "ssbbbsssssssbbbsss", "ssskeessssseeksss"[:18], "sssseessssssseesss", "ssssssssssssssssss",
        "ssssssssssssssssss", "ssssssssssssssssss"], K=KK, lit=["yellow_concrete"])
    tb(m, s, "head", (16, 4, 16), (-8, 11, -7), "cyan_terracotta", [("light_gray_concrete", 2), ("cyan_concrete", 1)], rate=0.25)
    for x, y, z in ((6, 26, 4), (-5, 24, 8), (8, 20, -4), (-8, 18, 2), (2, 27, -6)):
        m.c("head", "sea_lantern", (x, y, z + 0.1), (1, 1, 1), light=True)
    # the jutting underbite with a row of needle teeth pointing up and a dark gullet
    tb(m, s, "jaw", (20, 5, 12), (-10, 7, 4), "gray_concrete", [("cyan_terracotta", 2), ("black_concrete", 1)], rate=0.2, D="black_concrete")
    tb(m, s, "jaw", (18, 1, 10), (-9, 12, 5), "black_concrete", ())
    for i in range(9):
        x = -8 + i * 2
        m.c("jaw", "white_concrete", (x, 13.6 + (i % 2), 14.4), (1, 2.6 + (i % 2) * 1.4, 1))
    for i in range(7):
        m.c("head", "white_concrete", (-6 + i * 2, 11.4, 9.6), (1, 2, 1))
    # the lure: three bending stalk pieces and a glowing bulb
    m.c("lure1", "black_concrete", (0, 32, 2), (1.4, 5, 1.4), (20, 0, 0))
    m.c("lure2", "black_concrete", (0, 37, 9), (1.2, 1.2, 7), (-10, 0, 0))
    m.c("lure3", "black_concrete", (0, 34, 13.5), (1, 4, 1))
    m.c("lure3", "shroomlight", (0, 31, 13.5), (3, 3, 3), light=True)
    m.c("lure3", "yellow_concrete", (0, 31, 13.5), (3.6, 1, 1), light=True)
    # side fins and the tail
    for side, arm in ((1, "armL"), (-1, "armR")):
        tb(m, s, arm, (1, 7, 6), (side * 9.5 - 0.5 + side * 0.5, 12, -3), "cyan_concrete", [("cyan_terracotta", 1)], rate=0.3)
    T(m, s, "tail1", (10, 10, 8), (-5, 13, -16), NAVY, 0.25)
    tb(m, s, "tail2", (1, 14, 8), (-0.5, 11, -24), "cyan_concrete", [("cyan_terracotta", 2), ("gray_concrete", 1)], rate=0.3)
    tb(m, s, "head", (1, 5, 10), (-0.5, 28, -6), "cyan_concrete", [("cyan_terracotta", 1)], rate=0.3)
    m.no_elbows = True
    m.anims = idle("float", {
        "jaw": {"rot": K((0, Z), (1.0, (14, 0, 0)), (1.6, (14, 0, 0)), (2.4, Z), (4.0, Z))},
        "lure1": {"rot": sway(0, 8, 4.0)}, "lure2": {"rot": sway(0, 14, 4.0, 0.15)}, "lure3": {"rot": sway(2, 18, 2.0)},
        "tail1": {"rot": sway(1, 16, 2.0)}, "tail2": {"rot": sway(1, 24, 2.0, 0.2)},
        "armL": {"rot": sway(1, 25, 1.0)}, "armR": {"rot": sway(1, 25, 1.0, 0.5)},
        "head": {"rot": sway(0, 4, 4.0)}}, 4.0)
    m.attacks = {"frost": "pulse", "pull": "raise", "charge": "dive"}
    m.melee = "swipe"
    return m


@big("hollow_king", "<gradient:#1b1b1b:#9ccc65><bold>The Antler King</bold></gradient>", "He Wears the Forest", "WITHER_SKELETON", "nature", "GREEN",
     extra=["darkness", "spikes"], minion="SKELETON", items=["BONE_BLOCK 16", "MOSS_BLOCK 16", "DIAMOND 3"], top=["TOTEM_OF_UNDYING 1"],
     recipe=boss_recipe("SPORE_BLOSSOM_AIR", "ENTITY_WITHER_SKELETON_AMBIENT", "ENTITY_WITHER_SKELETON_DEATH", "moss_block", 0.5, "roar", "die_kneel"))
def hollow_king():
    """A tall gaunt king in a ragged black robe with a pale bone mask for a face, green fire in its eye
    slits, enormous branching antlers with moss hanging from them, long clawed arms and a lantern of
    green fire swinging from one hand."""
    m = Model("hollow_king", "biped", 2.0)
    biped(m, hip=12, legx=3, neck=30, shoulder=29, armx=7)
    m.bone("cape", "body", (0, 29, -3))
    m.bone("lantern", "armR", (-7.5, 12, 0))
    m.hold = {"lantern": 0}
    KK = {"s": "bone_block", "e": "lime_concrete", "k": "black_concrete", "b": "black_concrete", "m": "black_concrete", "t": "bone_block", "n": "white_terracotta"}
    s = Sheet(512, 256)
    legs2(m, s, (3, 11, 3), 3, "black_wool", ROBE[1], boot="black_concrete")
    # robe: long skirt on the hips, chest with green trim and a belt of bones
    T(m, s, "hips", (13, 9, 8), (-6.5, 4, -4), ROBE, 0.28, D="green_terracotta")
    T(m, s, "body", (11, 17, 7), (-5.5, 13, -3.5), ROBE, 0.22, front=[
        "...........", "...........", "...ggggg...", "....ggg....", ".....g.....", "...........", "...........", "...........",
        "...........", "...........", "...........", "...........", "...........", "...........", "wbwbwbwbwbw"], K={"g": "green_terracotta", "w": "bone_block", "b": "black_concrete"})
    T(m, s, "body", (15, 3, 9), (-7.5, 27, -4.5), ("black_wool", [("moss_block", 3), ("green_terracotta", 1)]), 0.45)
    tb(m, s, "cape", (12, 22, 1), (-6, 7, -5), "black_wool", [("gray_wool", 2), ("black_concrete", 1)], rate=0.3,
       back=["............", "............"] + ["............"] * 17 + ["b.bb.b.bb.b."[:12], "b..b..b..b.."[:12], "...b.....b.."[:12]], K={"b": "black_wool"})
    arms2(m, s, (3, 14, 3), 29, 7.5, "black_wool", ROBE[1], hand="bone_block", hand_tones=[("white_terracotta", 1)], hand_size=(3, 4, 3))
    # the mask: a long bone face with green eye slits
    tb(m, s, "head", (8, 10, 7), (-4, 30, -3.5), BONE[0], BONE[1], rate=0.15, front=[
        "ssssssss", "ssssssss", "bsssssbs"[:8], "seessees", "ssssssss", "sssnnsss", "ssssssss", "smtmtmts"[:8], "ssmmmmss", "ssssssss"], K=KK, lit=["lime_concrete"])
    tb(m, s, "head", (10, 3, 9), (-5, 39, -4.5), "black_wool", [("gray_wool", 1)], rate=0.3)
    # antlers: two big branching racks
    for sd in (1, -1):
        horn(m, "head", "stripped_spruce_log", (sd * 3.5, 41, 0), 4, (0, 0, -32 * sd), (0, 0, 14 * sd), 1.8, 0.85)
        horn(m, "head", "stripped_spruce_log", (sd * 7, 44.5, 0), 3, (-10, 0, -70 * sd), (0, 0, 22 * sd), 1.3, 0.85)
        horn(m, "head", "stripped_spruce_log", (sd * 9.5, 49, 0), 2, (0, 0, -10 * sd), (0, 0, -10 * sd), 1.1, 0.85)
        horn(m, "head", "spruce_log", (sd * 5.5, 46, 0.4), 2, (20, 0, 10 * sd), (0, 0, 0), 1.0, 0.85)
        m.c("head", "moss_block", (sd * 6.5, 42.5, 0.6), (2, 1.2, 2))
        m.c("head", "green_terracotta", (sd * 9.5, 46.8, 0.6), (1, 2.6, 1))
    m.c("lantern", "chain", (-7.5, 10, 0), (0.8, 3, 0.8))
    m.c("lantern", "iron_block", (-7.5, 8, 0), (3, 0.8, 3))
    m.c("lantern", "lime_stained_glass", (-7.5, 6, 0), (2.6, 3.2, 2.6), light=True)
    m.c("lantern", "iron_block", (-7.5, 4, 0), (3, 0.8, 3))
    m.anims = idle("biped", {"cape": {"rot": sway(0, 6, 4.0, base=(8, 0, 0))}, "lantern": {"rot": sway(0, 18, 2.0)},
                             "head": {"rot": K((0, Z), (1.2, (6, 18, 8)), (2.2, (6, 18, 8)), (3.2, (-4, -12, -6)), (4.0, Z))}}, 4.0)
    m.attacks = {"darkness": "cast", "spikes": "slam", "minions": "roar"}
    m.melee = "swipe"
    return m


@big("fenrir", "<gradient:#263238:#80d8ff><bold>Grimfang</bold></gradient>", "The Wolf the Chains Could Not Hold", "WOLF", "frost", "BLUE",
     extra=["roar", "leap"], minion="WOLF", items=["BONE 32", "CHAIN 16", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"], speed=0.32,
     recipe=boss_recipe("SNOWFLAKE", "ENTITY_WOLF_GROWL", "ENTITY_WOLF_DEATH", "packed_ice", 0.6, "howl", "die_side", ground_block="SNOW_BLOCK"))
def fenrir():
    """A huge shaggy dire wolf in charcoal and grey fur with a pale belly and muzzle, a thick mane, ice blue
    glowing eyes, white fangs, and a broken iron collar with chain ends swinging under its neck."""
    m = Model("fenrir", "quad", 2.0)
    quad4(m, 14, 4.5, 7, -8, 18, 12, 15)
    m.bone("chain", "neck", (0, 13, 13))
    s = Sheet(512, 256)
    KK = {"s": "gray_wool", "k": "black_concrete", "e": "light_blue_concrete", "w": "white_concrete", "b": "black_wool", "m": "black_concrete", "t": "white_concrete", "n": "black_concrete"}
    for leg, z in (("legFL", 7), ("legBL", -8)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            T(m, s, lg, (4, 13, 4), (sd * 4.5 - 2, 1.5, z - 2), FUR_D, 0.3, D="black_wool")
            tb(m, s, lg, (5, 2, 6), (sd * 4.5 - 2.5, 0, z - 2.5), "light_gray_wool", [("gray_wool", 1)], rate=0.3)
    T(m, s, "body", (12, 11, 22), (-6, 11, -12), FUR_D, 0.3, L="gray_concrete")
    tb(m, s, "body", (10, 2, 18), (-5, 10, -10), "light_gray_wool", [("white_wool", 1), ("gray_wool", 1)], rate=0.3)
    # the mane and neck
    T(m, s, "neck", (14, 13, 8), (-7, 11, 6), FUR_D, 0.35, L="light_gray_wool")
    # head with a long muzzle, ears, glowing eyes and fangs
    T(m, s, "head", (10, 8, 8), (-5, 15, 11), FUR_D, 0.25, front=face(10, 8, ey=2, gap=2, mouth=None, brow=True, glow=True), K=KK, lit=["light_blue_concrete"])
    tb(m, s, "head", (6, 3, 6), (-3, 16, 19), "light_gray_wool", [("white_wool", 1)], rate=0.3, front=["..kk..", "......", "t....t"], K=KK)
    m.c("head", "black_concrete", (0, 19.2, 25.1), (2, 1, 0.4))
    tb(m, s, "jaw", (6, 2, 6), (-3, 13.6, 19), "light_gray_wool", [], front=["t....t", "......"], K=KK)
    for sd in (1, -1):
        m.c("head", "gray_wool", (sd * 3, 24.5, 13), (2.4, 3, 1.6), (0, 0, -10 * sd))
        m.c("head", "black_wool", (sd * 3, 26.2, 13), (1.4, 1.6, 1.2), (0, 0, -10 * sd))
    # broken collar and swinging chain ends
    m.c("neck", "iron_block", (0, 12.6, 12), (12, 2, 3))
    for x in (-3, 2):
        m.c("chain", "chain", (x, 9.5, 13), (1, 5, 1))
        m.c("chain", "iron_block", (x, 6.6, 13), (1.6, 1.6, 1.6))
    # bushy tail
    T(m, s, "tail", (5, 5, 12), (-2.5, 14, -22), FUR_D, 0.35)
    tb(m, s, "tail", (4, 4, 3), (-2, 14.5, -25), "light_gray_wool", [("white_wool", 1)], rate=0.3)
    m.anims = idle("quad", {"chain": {"rot": sway(0, 14, 2.0)}, "jaw": {"rot": K((0, Z), (2.0, (10, 0, 0)), (2.6, Z), (4.0, Z))}})
    m.attacks = {"roar": "howl", "leap": "pounce", "frost": "bite"}
    m.melee = "bite"
    return m


@big("tide_tyrant", "<gradient:#bf360c:#ff8a65><bold>King Shellback</bold></gradient>", "The Crab Who Took the Reef", "IRON_GOLEM", "water", "RED",
     extra=["frost", "minions"], minion="DROWNED", items=["NAUTILUS_SHELL 3", "PRISMARINE_CRYSTALS 16", "DIAMOND 3"], top=["HEART_OF_THE_SEA 1"],
     recipe=boss_recipe("BUBBLE", "ENTITY_TURTLE_AMBIENT_LAND", "ENTITY_TURTLE_DEATH", "dead_brain_coral_block", 0.6, "rear", "die_side", ground_block="SAND"))
def tide_tyrant():
    """A giant red crab king: a wide speckled shell crusted with barnacles and a crown of pink and yellow
    coral, eyes on stalks that twitch, one huge crusher claw and one quick little claw, and six
    pointed legs that tap while it waits."""
    m = Model("tide_tyrant", "quad", 2.0)
    quad4(m, 12, 11, 4, -4, 14, 9, 10)
    m.bone("clawL", "body", (12, 14, 8)); m.bone("clawR", "body", (-11, 14, 8))
    m.bone("eyeL", "head", (3, 20, 10)); m.bone("eyeR", "head", (-3, 20, 10))
    m.bone("legML", "body", (12, 12, 0)); m.bone("legMR", "body", (-12, 12, 0))
    s = Sheet(512, 256)
    SH = ("red_terracotta", [("orange_terracotta", 3), ("red_concrete", 2), ("brown_terracotta", 1)])
    T(m, s, "body", (26, 9, 18), (-13, 10, -9), SH, 0.3, L="orange_terracotta", D="brown_terracotta")
    T(m, s, "body", (20, 3, 14), (-10, 19, -7), SH, 0.3)
    tb(m, s, "body", (24, 2, 16), (-12, 8.4, -8), "white_terracotta", [("pink_terracotta", 1)], rate=0.25)
    for x, z in ((-8, -3), (6, 2), (-2, -6), (9, -5), (-11, 4)):
        m.c("body", "light_gray_concrete", (x, 19.6, z), (2, 1, 2)); m.c("body", "white_concrete", (x, 20.2, z), (1, 0.8, 1))
    for x, b, h in ((-4, "pink_concrete", 6), (-1, "yellow_concrete", 8), (2, "pink_concrete", 7), (5, "magenta_terracotta", 5), (0.5, "yellow_concrete", 4)):
        m.c("body", b, (x, 22 + h / 2, -1), (1.6, h, 1.6)); m.c("body", b, (x + 0.8, 22 + h * 0.7, -1), (1.6, 1.2, 1.2))
    # head front: a small face with a mouth of bubbles
    tb(m, s, "head", (10, 5, 2), (-5, 11, 9), "red_terracotta", [("orange_terracotta", 1)], rate=0.3, front=["..........", "..........", "..mmmmmm..", "...tmmt...", ".........."], K={"m": "black_concrete", "t": "white_concrete"})
    for sd, e in ((1, "eyeL"), (-1, "eyeR")):
        m.c(e, "orange_terracotta", (sd * 3, 22, 10), (1.2, 4, 1.2))
        m.c(e, "black_concrete", (sd * 3, 25, 10), (2.4, 2.4, 2.4)); m.c(e, "white_concrete", (sd * 3 + 0.4 * sd, 25.6, 11.1), (0.8, 0.8, 0.4))
    # the big crusher claw (left) and the small one (right)
    T(m, s, "clawL", (5, 5, 8), (11, 11, 4), SH, 0.3)
    T(m, s, "clawL", (9, 8, 9), (10, 10, 11), SH, 0.3, L="orange_terracotta")
    tb(m, s, "clawL", (4, 4, 7), (11, 17, 15), "red_terracotta", [("orange_terracotta", 1)], rate=0.3)
    tb(m, s, "clawL", (8, 1, 2), (10.5, 9.6, 18.5), "white_terracotta", [])
    T(m, s, "clawR", (3, 3, 6), (-14, 12, 4), SH, 0.3)
    T(m, s, "clawR", (5, 4, 6), (-15, 11, 9), SH, 0.3)
    tb(m, s, "clawR", (2, 3, 4), (-14, 15, 12), "red_terracotta", [], rate=0.3)
    # six legs
    for leg, z in (("legFL", 4), ("legML", 0), ("legBL", -4)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            m.c(lg, "red_terracotta", (sd * 15, 10, z), (6, 2, 2), (0, 0, -30 * sd))
            m.c(lg, "orange_terracotta", (sd * 18.5, 5, z), (2, 9, 2), (0, 0, 12 * sd))
            m.c(lg, "brown_terracotta", (sd * 19.4, 0.6, z), (1.2, 2, 1.2))
    m.anims = idle("quad", {
        "eyeL": {"rot": sway(2, 12, 2.0)}, "eyeR": {"rot": sway(2, 12, 2.0, 0.3)},
        "clawL": {"rot": K((0, Z), (1.0, (-12, 0, 0)), (1.3, (-4, 0, 0)), (1.6, (-12, 0, 0)), (2.0, Z), (4.0, Z))},
        "clawR": {"rot": K((0, Z), (0.3, (-18, 0, 0)), (0.5, Z), (0.8, (-18, 0, 0)), (1.0, Z), (2.6, (-18, 0, 0)), (2.8, Z), (4.0, Z))},
        "legML": {"rot": sway(0, 8, 1.0)}, "legMR": {"rot": sway(0, 8, 1.0, 0.5)}, "neck": {"rot": K((0, Z), (4.0, Z))}})
    m.attacks = {"frost": "rear", "minions": "toss", "slam": "charge"}
    m.melee = "bite"
    return m


@big("storm_herald", "<gradient:#37474f:#ffee58><bold>The Thunder Ram</bold></gradient>", "It Brings the Storm on Its Back", "RAVAGER", "storm", "YELLOW",
     extra=["lightning", "charge"], items=["COPPER_BLOCK 12", "LIGHTNING_ROD 6", "DIAMOND 3"], top=["TRIDENT 1"],
     recipe=boss_recipe("ELECTRIC_SPARK", "ENTITY_GOAT_SCREAMING_RAM_IMPACT", "ENTITY_GOAT_SCREAMING_DEATH", "light_gray_wool", 0.6, "roar", "die_back", ground_block="LIGHT_GRAY_WOOL"))
def storm_herald():
    """A towering ram-headed giant with blue-grey wool, two huge curled horns, a thundercloud of grey wool
    on its shoulders with glowing yellow lightning bolts, copper bracers, a copper rod in its fist and
    cloven hooves."""
    m = Model("storm_herald", "biped", 2.0)
    biped(m, hip=11, legx=3.6, neck=28, shoulder=27, armx=9)
    m.bone("cloud", "body", (0, 30, 0))
    m.bone("rod", "armR", (-10, 12, 0))
    m.hold = {"rod": 4}
    s = Sheet(512, 256)
    WOOL = ("light_gray_wool", [("gray_wool", 2), ("light_blue_terracotta", 1), ("white_wool", 1)])
    legs2(m, s, (4, 10, 4), 3.6, "gray_wool", WOOL[1], boot="black_terracotta", boot_tones=[("brown_terracotta", 1)])
    T(m, s, "body", (15, 15, 9), (-7.5, 12, -4.5), WOOL, 0.3, front=[".............."] * 9 + ["ccccccccccccccc", "cyccccccccccycc"[:15], "ccccccccccccccc"], K={"c": "cut_copper", "y": "yellow_concrete"})
    T(m, s, "hips", (14, 4, 8), (-7, 8.5, -4), ("brown_terracotta", [("brown_concrete", 1)]), 0.3)
    arms2(m, s, (5, 13, 5), 27, 10, "light_gray_wool", WOOL[1], hand="gray_terracotta", hand_size=(5, 4, 5))
    for sd in (1, -1):
        tb(m, s, "armL" if sd == 1 else "armR", (6, 3, 6), (sd * 10 - 3, 17, -3), "cut_copper", [("oxidized_copper", 1)], rate=0.4)
    # the head: a long ram face, pale muzzle and glowing eyes
    tb(m, s, "head", (8, 10, 8), (-4, 28, -2), "gray_wool", [("light_gray_wool", 2), ("gray_concrete", 1)], rate=0.3, front=[
        "ssssssss", "bbssssbb", "seesssee"[:8], "ssssssss", "ssllllss", "sllllllss"[:8], "slnnnnls", "ssllllss", "sslmmlss", "ssllllss"],
        K={"s": "gray_wool", "b": "black_wool", "e": "yellow_concrete", "l": "light_gray_wool", "n": "pink_terracotta", "m": "black_concrete"}, lit=["yellow_concrete"])
    for sd in (1, -1):
        horn(m, "head", "dripstone_block", (sd * 4.5, 36, 0), 6, (0, 0, -75 * sd), (-48, 0, 6 * sd), 2.4, 0.84)
    # the thundercloud on its shoulders with bolts
    for x, y, z, w in ((-7, 30, -1, 7), (0, 32, -3, 9), (7, 30, -1, 7), (-3, 33.5, -5, 6), (4, 33, 2, 5)):
        T(m, s, "cloud", (w, 4, w - 1), (x - w / 2, y, z - (w - 1) / 2), ("gray_wool", [("light_gray_wool", 2), ("gray_concrete", 2)]), 0.4)
    for x, z, rot in ((-6, 1, 20), (6, 0, -25)):
        m.c("cloud", "yellow_concrete", (x, 27.5, z), (1, 4, 1), (0, 0, rot), light=True)
        m.c("cloud", "yellow_concrete", (x + 1, 24.5, z), (1, 3, 1), (0, 0, -rot), light=True)
    m.c("rod", "cut_copper", (-10, 16, 0), (1.4, 22, 1.4))
    m.c("rod", "lightning_rod", (-10, 27.5, 0), (2, 2, 2))
    m.c("rod", "yellow_concrete", (-10, 29.2, 0), (1, 1, 1), light=True)
    m.anims = idle("biped", {"cloud": {"pos": bob(0.8, 2.0), "rot": sway(1, 6, 4.0)}, "rod": {"rot": sway(0, 6, 4.0)}}, 4.0)
    m.attacks = {"lightning": "cast", "charge": "lunge", "shockwave": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


@big("ember_queen", "<gradient:#4e342e:#ff6d00><bold>The Forge Mother</bold></gradient>", "Her Belly Is a Furnace", "IRON_GOLEM", "fire", "RED",
     extra=["fire_ring", "meteor"], minion="MAGMA_CUBE", items=["IRON_BLOCK 4", "BLAST_FURNACE 2", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"],
     recipe=boss_recipe("LAVA", "BLOCK_ANVIL_LAND", "BLOCK_ANVIL_DESTROY", "magma_block", 0.7, "slam", "die_kneel", ground_block="BLACKSTONE"))
def ember_queen():
    """A broad smith giantess with soot-dark skin, two thick copper braids, a scorched leather apron over a
    furnace in her belly that glows through an iron grate, heavy gloves and a huge forge hammer."""
    m = Model("ember_queen", "biped", 2.0)
    biped(m, hip=10, legx=4, neck=27, shoulder=25, armx=9)
    m.bone("hammer", "armR", (-10.5, 10, 0))
    m.bone("braidL", "head", (4, 31, -3)); m.bone("braidR", "head", (-4, 31, -3))
    m.hold = {"hammer": 8}
    s = Sheet(512, 256)
    SOOT = ("brown_terracotta", [("terracotta", 2), ("brown_concrete", 1)])
    legs2(m, s, (5, 9, 5), 4, "black_terracotta", [("gray_terracotta", 1)], boot="blackstone", boot_tones=[("polished_blackstone", 1)])
    T(m, s, "body", (17, 15, 10), (-8.5, 11, -5), SOOT, 0.25)
    # the apron with the furnace grate
    tb(m, s, "body", (13, 16, 1), (-6.5, 6, 5), "brown_terracotta", [("spruce_planks", 2), ("black_terracotta", 1)], rate=0.25, front=[
        "a...........a", ".............", ".............", ".ggggggggggg.", ".gfoyofoyofg.", ".gooooooooog.", ".gfyofyofyog.", ".ggggggggggg.",
        ".............", ".............", ".............", ".............", ".............", ".............", ".............", "............."],
        K={"a": "iron_block", "g": "iron_bars" if False else "gray_concrete", "f": "orange_concrete", "o": "shroomlight", "y": "yellow_concrete"}, lit=["shroomlight", "orange_concrete", "yellow_concrete"])
    arms2(m, s, (5, 12, 5), 25, 10.5, "brown_terracotta", SOOT[1], hand="black_terracotta", hand_tones=[("gray_terracotta", 1)], hand_size=(6, 5, 6))
    tb(m, s, "head", (9, 9, 8), (-4.5, 27, -4), SOOT[0], SOOT[1], rate=0.12,
       front=face(9, 9, ey=3, gap=3, mouth="frown", mw=4, nose=1, cheeks=False), K={"s": "brown_terracotta", "k": "black_concrete", "w": "white_concrete", "b": "orange_terracotta",
       "m": "black_terracotta", "t": "white_concrete", "n": "terracotta", "c": "red_terracotta"})
    tb(m, s, "head", (10, 3, 9), (-5, 35, -4.5), "orange_terracotta", [("red_terracotta", 2), ("orange_concrete", 1)], rate=0.4)
    tb(m, s, "head", (10, 7, 2), (-5, 29, -5.5), "orange_terracotta", [("red_terracotta", 2)], rate=0.4)
    for sd, b in ((1, "braidL"), (-1, "braidR")):
        for i in range(4):
            m.c(b, "orange_terracotta" if i % 2 else "red_terracotta", (sd * 4.5, 29 - i * 3, -3.5 + i * 0.3), (2.6, 3, 2.6))
        m.c(b, "gold_block", (sd * 4.5, 17.8, -2.4), (2, 1.2, 2))
    # hammer: a long handle and a big iron head with a glowing face
    m.c("hammer", "dark_oak_log", (-10.5, 14, 0), (1.8, 18, 1.8))
    tb(m, s, "hammer", (8, 6, 6), (-14.5, 21, -3), "iron_block", IRON[1], rate=0.3)
    m.c("hammer", "orange_concrete", (-10.5, 24, 3.1), (6, 4, 0.4), light=True)
    m.anims = idle("biped", {"braidL": {"rot": sway(0, 6, 4.0)}, "braidR": {"rot": sway(0, 6, 4.0, 0.3)}, "hammer": {"rot": sway(0, 5, 4.0)}}, 4.0)
    m.attacks = {"fire_ring": "slam", "meteor": "cast", "slam": "double"}
    m.melee = "swipe"
    return m


@big("gravelord", "<gradient:#263238:#80cbc4><bold>The Bone Collector</bold></gradient>", "He Comes With an Empty Sack", "WITHER_SKELETON", "soul", "WHITE",
     extra=["skulls", "pull"], minion="SKELETON", items=["BONE_BLOCK 16", "SOUL_LANTERN 4", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"],
     recipe=boss_recipe("SOUL", "ENTITY_SKELETON_AMBIENT", "ENTITY_SKELETON_DEATH", "bone_block", 0.5, "roar", "die_front", ground_block="SOUL_SOIL"))
def gravelord():
    """A hunched grey-green ghoul with long clawed fingers, a torn black hood and a huge burlap sack of skulls
    on its back that sways as it shuffles, holding a soul lantern that glows blue."""
    m = Model("gravelord", "biped", 2.0)
    biped(m, hip=11, legx=3, neck=26, shoulder=25, armx=7.5)
    m.bone("sack", "body", (0, 26, -5))
    m.bone("lantern", "armL", (7.5, 9, 0))
    m.hold = {"lantern": 0}
    s = Sheet(512, 256)
    GH = ("gray_terracotta", [("green_terracotta", 2), ("light_gray_terracotta", 1), ("cyan_terracotta", 1)])
    legs2(m, s, (3, 10, 3), 3, "gray_terracotta", GH[1], boot="black_terracotta")
    T(m, s, "hips", (11, 5, 7), (-5.5, 7, -3.5), ROBE, 0.3)
    T(m, s, "body", (12, 14, 8), (-6, 12, -4), ROBE, 0.25, front=[".........."] * 10 + ["rrrrrrrrrrrr", "............"], K={"r": "brown_terracotta"})
    m.rest("body", (18, 0, 0))
    arms2(m, s, (3, 15, 3), 25, 7.5, "black_wool", ROBE[1], hand="gray_terracotta", hand_tones=GH[1], hand_size=(4, 4, 4))
    for sd in (1, -1):
        for i in range(3):
            m.c("armL" if sd == 1 else "armR", "white_terracotta", (sd * 7.5 - 1 + i, 5.4, 1.6), (0.6, 3, 0.6))
    tb(m, s, "head", (8, 8, 8), (-4, 26, -3), GH[0], GH[1], rate=0.2, front=face(8, 8, ey=2, gap=2, mouth="grin", mw=6, glow=True, brow=False),
       K={"s": "gray_terracotta", "e": "cyan_concrete", "m": "black_concrete", "t": "bone_block", "b": "black_concrete"}, lit=["cyan_concrete"])
    tb(m, s, "head", (10, 9, 9), (-5, 28, -4.6), "black_wool", [("gray_wool", 1)], rate=0.25, faces=("back", "left", "right", "top"),
       front=["kkkkkkkkkk", "k........k", "k........k", "k........k", "k........k", "k........k", "k........k", "k........k", "k........k"], K={"k": "black_wool"})
    # the sack of skulls
    T(m, s, "sack", (14, 15, 9), (-7, 18, -14), ("brown_terracotta", [("spruce_planks", 2), ("brown_wool", 2), ("terracotta", 1)]), 0.35)
    m.c("sack", "spruce_planks", (0, 33.5, -9.5), (6, 2, 4))
    for x, y, z in ((-3, 34.5, -10), (3, 35, -9), (0, 36, -11)):
        tb(m, s, "sack", (4, 4, 4), (x - 2, y - 1, z - 2), "bone_block", [("white_terracotta", 1)], rate=0.2, front=["....", ".kk.", "....", "k..k"], K={"k": "black_concrete"})
    m.c("sack", "chain", (-6, 28, -5), (1, 8, 1), (30, 0, 0))
    m.c("lantern", "chain", (7.5, 7.5, 0), (0.8, 3, 0.8))
    m.c("lantern", "soul_lantern", (7.5, 4.6, 0), (2.6, 3, 2.6), light=True)
    m.anims = idle("biped", {"sack": {"rot": sway(2, 6, 4.0), "pos": bob(0.5, 2.0)}, "lantern": {"rot": sway(0, 16, 2.0)},
                             "head": {"rot": K((0, (10, 0, 0)), (1.4, (14, 20, 8)), (2.4, (14, 20, 8)), (3.2, (6, -16, -6)), (4.0, (10, 0, 0)))}}, 4.0)
    m.attacks = {"skulls": "cast", "pull": "sweep", "minions": "roar"}
    m.melee = "swipe"
    return m


@big("bloodtusk", "<gradient:#4e342e:#ef5350><bold>Old Tusker</bold></gradient>", "The War Boar of the Red Banner", "HOGLIN", "blood", "RED",
     extra=["charge", "minions"], minion="PIGLIN", items=["PORKCHOP 32", "GOLD_INGOT 16", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"], speed=0.3,
     recipe=boss_recipe("CRIMSON_SPORE", "ENTITY_HOGLIN_ANGRY", "ENTITY_HOGLIN_DEATH", "crimson_nylium", 0.7, "rear", "die_side", ground_block="NETHERRACK"))
def bloodtusk():
    """A great bristly war boar in dark brown with a ridge of stiff hair, two huge curved white tusks, red war
    paint stripes, iron plates strapped over its back and a tall red banner that flaps above it."""
    m = Model("bloodtusk", "quad", 2.0)
    quad4(m, 13, 6, 7, -9, 17, 12, 14)
    m.bone("flag", "body", (0, 28, -6))
    s = Sheet(512, 256)
    s.rate = 0.4
    HAIR = ("brown_wool", [("brown_terracotta", 3), ("spruce_planks", 1), ("black_terracotta", 1)])
    for leg, z in (("legFL", 7), ("legBL", -9)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            T(m, s, lg, (5, 12, 5), (sd * 6 - 2.5, 1.5, z - 2.5), HAIR, 0.3)
            tb(m, s, lg, (5, 2, 5), (sd * 6 - 2.5, 0, z - 2.5), "black_terracotta", [], rate=0)
    T(m, s, "body", (16, 13, 24), (-8, 10, -13), HAIR, 0.3, side=["............"] * 4 + ["rr..rr..rr..rr..rr..rr.."[:24]] + ["........................"] * 2,
      K={"r": "red_concrete"})
    for i in range(6):
        m.c("body", "black_wool", (0, 24 + (i % 2), -10 + i * 3.6), (2, 3 + (i % 3), 2))
    tb(m, s, "body", (18, 2, 14), (-9, 22.6, -9), "iron_block", IRON[1], rate=0.35)
    for x in (-9.5, 9.5):
        tb(m, s, "body", (1, 6, 12), (x - 0.5, 17, -8), "iron_block", IRON[1], rate=0.35)
    T(m, s, "neck", (14, 12, 6), (-7, 10, 9), HAIR, 0.3)
    T(m, s, "head", (12, 10, 9), (-6, 9, 13), HAIR, 0.25, front=face(12, 10, ey=2, gap=4, mouth=None, glow=False), K={"s": "brown_wool", "k": "black_concrete",
      "w": "red_concrete", "b": "black_terracotta"})
    tb(m, s, "head", (8, 5, 3), (-4, 9.5, 22), "pink_terracotta", [("terracotta", 1)], rate=0.3, front=["........", ".kk..kk.", "........", "........", "........"], K={"k": "brown_terracotta"})
    for sd in (1, -1):
        horn(m, "head", "bone_block", (sd * 4.5, 11, 22), 4, (-40, 0, -20 * sd), (-30, 0, -6 * sd), 2.2, 0.82)
        m.c("head", "red_concrete", (sd * 3.5, 16, 22.1), (1, 4, 0.3))
        m.c("head", "brown_wool", (sd * 6.5, 19.5, 15), (2.6, 3.4, 1.6), (0, 0, -25 * sd))
    m.c("flag", "dark_oak_log", (0, 33, -6), (1.4, 18, 1.4))
    tb(m, s, "flag", (1, 9, 8), (-0.5, 33, -15), "red_wool", [("red_concrete", 2), ("red_terracotta", 1)], rate=0.25,
       side=["........", "...yy...", "..y..y..", "...yy...", "........", "........", "........", "........", "........"], K={"y": "yellow_concrete"})
    m.anims = idle("quad", {"flag": {"rot": sway(1, 18, 2.0)}})
    m.attacks = {"charge": "charge", "minions": "rear", "shockwave": "toss"}
    m.melee = "bite"
    return m


@big("old_ironroot", "<gradient:#5d4037:#c5e1a5><bold>The Stump Warden</bold></gradient>", "The Oldest Tree Got Up", "IRON_GOLEM", "nature", "GREEN",
     extra=["spikes", "heal"], minion="SPIDER", items=["OAK_LOG 32", "MOSS_BLOCK 32", "DIAMOND 3"], top=["ENCHANTED_GOLDEN_APPLE 1"],
     recipe=boss_recipe("SPORE_BLOSSOM_AIR", "BLOCK_WOOD_BREAK", "ENTITY_IRON_GOLEM_DEATH", "oak_log", 0.5, "roar", "die_kneel", ground_block="MOSS_BLOCK"))
def old_ironroot():
    """A walking tree stump with ring-cut wood on top, mushrooms and a sapling growing out of its moss,
    glowing amber knot-hole eyes over a mossy beard, and arms and legs of thick twisting roots."""
    m = Model("old_ironroot", "biped", 2.0)
    biped(m, hip=9, legx=5, neck=24, shoulder=24, armx=12)
    m.bone("sapling", "head", (2, 38, 0))
    s = Sheet(512, 256)
    s.rate = 0.38
    # root legs: twisted, splayed toes
    legs2(m, s, (5, 8, 5), 5, BARK[0], BARK[1], boot="spruce_log", boot_tones=[("dark_oak_log", 1)], toe=2)
    for sd in (1, -1):
        m.c("legL" if sd == 1 else "legR", "dark_oak_log", (sd * 7.5, 1, 2), (3, 2, 2), (0, 30 * sd, 0))
    # the trunk: bark sides, a face of knot-hole eyes, a moss beard
    T(m, s, "body", (22, 26, 18), (-11, 9, -9), BARK, 0.3, front=[
        "......................", "......................", "......................", "......................", "....kkk........kkk....",
        "...kooook.....koooo k."[:22], "....kkk........kkk....", "......................", "..........kk..........", "......................",
        ".....m..........m....."] + ["......................"] * 15, K={"k": "black_concrete", "o": "orange_concrete", "m": "black_terracotta"}, lit=["orange_concrete"])
    tb(m, s, "body", (14, 8, 2), (-7, 17, 8.6), "moss_block", MOSS[1], rate=0.4, front=["wwwwwwwwwwwwww", "wwwwwwwwwwwwww", ".wwwwwwwwwwww.", ".wwwwwwwwwwww.", "..wwwwwwwwww..",
        "..wwwwwwwwww..", "...wwwwwwww...", "....ww..ww...."], K={"w": "moss_block"})
    # top: ring-cut wood rimmed with moss, two red mushrooms, a little sapling
    tb(m, s, "head", (20, 2, 16), (-10, 35, -8), "stripped_oak_log", STUMP[1], rate=0.2, top=["...................."] * 3 + ["...oooooooooooo....", "..o............o...", "..o..oooooooo..o...",
        "..o..o......o..o...", "..o..o..oo..o..o...", "..o..o......o..o...", "..o..oooooooo..o...", "..o............o...", "...oooooooooooo...."], K={"o": "oak_planks"})
    T(m, s, "head", (22, 2, 18), (-11, 34, -9), MOSS, 0.4)
    for x, z, w, c in ((-7, 4, 5, "red_concrete"), (-4, -5, 3, "red_concrete"), (6, -4, 4, "brown_concrete")):
        m.c("head", "white_terracotta", (x, 38, z), (1.4, 3, 1.4))
        m.c("head", c, (x, 40, z), (w, 1.6, w))
        m.c("head", "white_concrete", (x + 0.6, 40.9, z + 0.4), (1, 0.4, 1))
    m.c("sapling", "oak_log", (2, 40, 0), (1, 6, 1))
    T(m, s, "sapling", (5, 4, 5), (-0.5, 42, -2.5), ("oak_leaves", [("azalea_leaves", 2), ("moss_block", 1)]), 0.4)
    # root arms
    arms2(m, s, (6, 10, 6), 32, 13, BARK[0], BARK[1])
    for sd, a in ((1, "armL"), (-1, "armR")):
        for i, dx in enumerate((-1.5, 0, 1.5)):
            m.c(a, "spruce_log", (sd * 13 + dx, 19.5 - (i % 2), 1), (1.4, 5, 1.4), (10, 0, dx * 8))
        m.c(a, "moss_block", (sd * 13, 32.5, 0), (7, 1.4, 7))
    m.anims = idle("biped", {"sapling": {"rot": sway(2, 14, 2.0)}}, 4.0)
    m.attacks = {"spikes": "slam", "heal": "roar", "minions": "stomp"}
    m.melee = "swipe"
    m.bend = -20
    return m


@big("gate_shade", "<gradient:#212121:#b0bec5><bold>The Gatekeeper</bold></gradient>", "Nothing Passes Without the Key", "VEX", "soul", "WHITE",
     extra=["blink", "darkness"], minion="VEX", items=["IRON_INGOT 16", "DIAMOND 1", "ENDER_PEARL 4"], movement="hover", fly=2,
     recipe=boss_recipe("SOUL", "ENTITY_VEX_AMBIENT", "ENTITY_VEX_DEATH", "deepslate_tiles", 0.6, "raise", "die_drop", ground_block="SOUL_SOIL"))
def gate_shade():
    """A hooded gatekeeper with no feet, its long tattered grey cloak drifting below it, two white eyes in
    the dark of its hood, a chain of padlocks across its chest, a huge iron key in one hand and a lantern
    in the other."""
    m = Model("gate_shade", "float", 2.0)
    m.bone("core", "root", (0, 14, 0))
    m.bone("head", "core", (0, 30, 0))
    m.bone("armL", "core", (8, 28, 0)); m.bone("armR", "core", (-8, 28, 0))
    m.bone("ring1", "core", (0, 14, 0))
    m.bone("tat1", "core", (0, 10, 0)); m.bone("tat2", "tat1", (0, 4, 0))
    m.bone("key", "armR", (-9, 17, 2)); m.bone("lamp", "armL", (9, 17, 2))
    s = Sheet(512, 256)
    CL = ("gray_wool", [("light_gray_wool", 2), ("gray_concrete", 2), ("black_wool", 1)])
    T(m, s, "core", (14, 18, 10), (-7, 12, -5), CL, 0.3, front=[".............."] * 6 + ["c.c.c.c.c.c.c.", ".l.......l...."[:14], "..cc.....cc...", "..............", "..............",
       ".............."], K={"c": "chain", "l": "iron_block"})
    T(m, s, "tat1", (16, 8, 12), (-8, 4, -6), CL, 0.35)
    T(m, s, "tat2", (14, 5, 10), (-7, 0, -5), CL, 0.35, front=["..............", "..............", "c.cc.cc.c.cc.c"[:14], "c..c..c..c..c."[:14], "c.....c......c"[:14]], K={"c": "gray_wool"})
    T(m, s, "head", (11, 11, 10), (-5.5, 29, -5), CL, 0.3, front=["sssssssssss", "skkkkkkkkks", "kkkkkkkkkkk", "kkkkkkkkkkk", "kkekkkkekkk", "kkekkkkekkk", "kkkkkkkkkkk",
       "kkkkkkkkkkk", "kkkkkkkkkkk", "skkkkkkkkks", "sssssssssss"], K={"s": "gray_wool", "k": "black_concrete", "e": "white_concrete"}, lit=["white_concrete"])
    m.c("head", "gray_wool", (0, 41, -2), (6, 2, 6))
    for sd, a in ((1, "armL"), (-1, "armR")):
        T(m, s, a, (4, 12, 4), (sd * 9 - 2, 17, -2), CL, 0.3)
        tb(m, s, a, (3, 3, 3), (sd * 9 - 1.5, 14.5, -1.5), "gray_terracotta", [("light_gray_terracotta", 1)], rate=0.3)
    m.c("key", "iron_block", (-9, 8, 2), (1.6, 16, 1.6))
    tb(m, s, "key", (5, 5, 2), (-11.5, 16, 1), "iron_block", IRON[1], rate=0.3, front=[".....", ".kkk.", ".k.k.", ".kkk.", "....."], K={"k": "gray_concrete"})
    m.c("key", "iron_block", (-7.5, 1.5, 2), (2, 1.6, 1.6)); m.c("key", "iron_block", (-7.5, 4, 2), (2, 1.6, 1.6))
    m.c("lamp", "chain", (9, 13, 2), (0.8, 3, 0.8))
    m.c("lamp", "lantern", (9, 10, 2), (3, 3.4, 3), light=True)
    m.no_elbows = True
    m.anims = idle("float", {"tat1": {"rot": sway(0, 10, 3.0)}, "tat2": {"rot": sway(0, 16, 3.0, 0.2)}, "lamp": {"rot": sway(0, 18, 1.5)},
                             "key": {"rot": sway(0, 6, 3.0)}}, 3.0)
    m.attacks = {"blink": "spin", "darkness": "raise", "minions": "pulse"}
    m.melee = "swipe"
    return m


# ---------------------------------------------------------------------------- minis grown into big bosses
drop("frost_yeti"); drop("cinder_imp"); drop("bog_orc"); drop("cluck_rider")
REMOVED = ['fenrir', 'ironhide_behemoth', 'void_walker', "cluck_rider", "hollow_king", "ender_wyrm", "gale_sovereign", "ghost_jelly", "orc_bruiser", "cyclops_ogre", "cinder_imp",
           "boo_twins", "shulker_matriarch", "pink_burrower"]
for _r in ("ghost_jelly", "pink_burrower", "boo_twins"): drop(_r)
BIG_INFO.pop("cinder_imp", None)
BIG_INFO.pop("hollow_king", None)


@big("frost_yeti", "<gradient:#90caf9:#ffffff><bold>The Frost Yeti</bold></gradient>", "Keeper of the Ice Cave", "IRON_GOLEM", "frost", "WHITE",
     extra=["frost", "shockwave", "volley"], minion="STRAY", items=["PACKED_ICE 32", "BLUE_ICE 8", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"],
     recipe=boss_recipe("SNOWFLAKE", "ENTITY_POLAR_BEAR_WARNING", "ENTITY_POLAR_BEAR_DEATH", "packed_ice", 0.6, "roar", "die_front", ground_block="SNOW_BLOCK"))
def frost_yeti():
    """A huge shaggy white yeti hunched forward on long arms, thick fur in white and pale grey, a blue-grey
    face with a heavy brow, a wide mouth with two fangs, short curled horns, icicles hanging off its
    shoulders and a fist frozen into a block of ice."""
    m = Model("frost_yeti", "biped", 2.0)
    biped(m, hip=10, legx=5, neck=28, shoulder=27, armx=12)
    s = Sheet(512, 256)
    s.rate = 0.22
    legs2(m, s, (6, 9, 6), 5, FUR_W[0], FUR_W[1], boot="light_gray_concrete", boot_tones=[("stone", 1)])
    T(m, s, "hips", (16, 4, 10), (-8, 7.5, -5), FUR_W, 0.35)
    T(m, s, "body", (20, 17, 12), (-10, 11, -6), FUR_W, 0.32, L="snow_block", D="light_gray_wool")
    tb(m, s, "body", (12, 10, 1), (-6, 13, 6), "light_gray_concrete", [("stone", 1)], rate=0.2)
    m.rest("body", (12, 0, 0))
    arms2(m, s, (7, 18, 7), 28, 13, FUR_W[0], FUR_W[1], hand="light_gray_concrete", hand_tones=[("stone", 1)], hand_size=(7, 4, 7))
    tb(m, s, "armR", (9, 8, 9), (-17.5, 2, -4.5), "packed_ice", [("ice", 2), ("blue_ice", 1)], rate=0.35)
    for sd in (1, -1):
        T(m, s, "body", (8, 4, 12), (sd * 11 - 4, 26, -6), FUR_W, 0.4)
        for i in range(3):
            m.c("body", "ice", (sd * (8 + i * 2.5), 24.5 - (i % 2), 5.5), (1, 3 + (i % 2) * 2, 1))
    tb(m, s, "head", (12, 11, 9), (-6, 27, 0), "light_gray_concrete", [("stone", 1)], rate=0.1,
       front=face(12, 11, ey=3, gap=3, mouth="fangs", mw=8, nose=1), K={"s": "light_gray_concrete", "k": "black_concrete", "w": "white_concrete", "b": "white_wool",
       "m": "black_concrete", "t": "white_concrete", "n": "gray_concrete", "c": "light_gray_concrete"})
    T(m, s, "head", (14, 4, 11), (-7, 37, -1), FUR_W, 0.35)
    T(m, s, "head", (14, 9, 4), (-7, 28, -2), FUR_W, 0.35)
    for sd in (1, -1):
        horn(m, "head", "white_terracotta", (sd * 6, 39.5, 3), 4, (0, 0, -70 * sd), (-25, 0, 20 * sd), 2.2, 0.8)
    m.anims = idle("biped", {}, 4.0)
    m.attacks = {"frost": "roar", "slam": "slam", "shockwave": "stomp", "volley": "double"}
    m.melee = "swipe"
    m.bend = -25
    return m


@big("cinder_imp", "<gradient:#8b0000:#ffab40><bold>The Cinder Devil</bold></gradient>", "Horned Trouble From Below", "PIGLIN_BRUTE", "fire", "RED",
     extra=["fire_ring", "leap", "meteor"], minion="BLAZE", items=["BLAZE_ROD 12", "MAGMA_CREAM 16", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"],
     recipe=boss_recipe("FLAME", "ENTITY_BLAZE_AMBIENT", "ENTITY_BLAZE_DEATH", "netherrack", 0.7, "roar", "die_back", ground_block="NETHERRACK"))
def cinder_imp():
    """A big red devil with black curling horns, glowing yellow eyes under an angry brow, a toothy grin and
    a pointed beard, bat wings that flex behind it, goat legs ending in black hooves, a whipping tail with
    an arrow tip and a black pitchfork with glowing prongs."""
    m = Model("cinder_imp", "biped", 2.0)
    biped(m, hip=11, legx=3.6, neck=27, shoulder=26, armx=9)
    m.bone("wingL", "body", (4, 24, -4)); m.bone("wingR", "body", (-4, 24, -4))
    m.bone("tail1", "hips", (0, 10, -4)); m.bone("tail2", "tail1", (0, 8, -10)); m.bone("tail3", "tail2", (0, 6, -16))
    m.bone("fork", "armR", (-9.5, 11, 0))
    m.hold = {"fork": 4}
    s = Sheet(512, 256)
    KK = {"s": "red_terracotta", "k": "black_concrete", "e": "yellow_concrete", "w": "white_concrete", "b": "black_concrete", "m": "black_concrete", "t": "white_concrete", "n": "red_concrete", "c": "red_concrete"}
    legs2(m, s, (4, 10, 5), 3.6, "black_terracotta", [("brown_terracotta", 2), ("gray_terracotta", 1)], boot="black_concrete")
    T(m, s, "hips", (12, 4, 7), (-6, 8, -3.5), ("black_terracotta", [("brown_terracotta", 1)]), 0.3)
    T(m, s, "body", (14, 15, 8), (-7, 12, -4), RED, 0.22, front=[".............."] * 3 + ["..dd......dd..", "...dd....dd...", "..............", "......dd......", "......dd......",
       "..............", ".....dddd.....", ".............."], K={"d": "nether_bricks"})
    arms2(m, s, (4, 13, 4), 26, 9.5, RED[0], RED[1], hand="black_terracotta", hand_size=(4, 3, 4))
    tb(m, s, "head", (10, 10, 9), (-5, 27, -4.5), RED[0], RED[1], rate=0.12, front=face(10, 10, ey=3, gap=2, mouth="grin", mw=6, nose=1, glow=True), K=KK, lit=["yellow_concrete"])
    tb(m, s, "head", (4, 4, 2), (-2, 24, 4), "black_concrete", [("black_terracotta", 1)], rate=0.3, front=["kkkk", ".kk.", ".kk.", "..k."], K={"k": "black_concrete"})
    for sd in (1, -1):
        horn(m, "head", "black_concrete", (sd * 4, 36, 0), 5, (0, 0, -55 * sd), (-18, 0, 26 * sd), 2.4, 0.78)
        m.c("head", "red_terracotta", (sd * 5.6, 33, 0), (1.4, 3, 2), (0, 0, -20 * sd))
    for sd, w in ((1, "wingL"), (-1, "wingR")):
        m.c(w, "black_terracotta", (sd * 9, 30, -5), (12, 1.4, 1.4), (0, 0, 20 * sd))
        tb(m, s, w, (12, 10, 1), (sd * 9 - 6, 21, -5.8), "red_concrete", [("red_terracotta", 2), ("nether_bricks", 1)], rate=0.3,
           front=["kkkkkkkkkkkk", "............", "............", "....k.......", "....k...k...", "....k...k...", "...........k", "k...k.......", "k...k...k...", "kk.kkk.kkkk."],
           K={"k": "black_terracotta"}, rot=(0, 25 * sd, 20 * sd), origin=(sd * 4, 30, -5))
    m.c("tail1", "red_terracotta", (0, 9, -8), (1.6, 1.6, 8), (-20, 0, 0))
    m.c("tail2", "red_terracotta", (0, 7, -14), (1.4, 1.4, 6), (20, 0, 0))
    m.c("tail3", "black_concrete", (0, 7.5, -17.5), (3, 3, 1.2), (0, 0, 45))
    m.c("fork", "black_concrete", (-9.5, 12, 0), (1.2, 26, 1.2))
    for dx in (-2, 0, 2):
        m.c("fork", "orange_concrete", (-9.5 + dx, 27, 0), (0.8, 4, 0.8), light=True)
    m.c("fork", "black_concrete", (-9.5, 25, 0), (5.2, 1, 1))
    m.anims = idle("biped", {"wingL": {"rot": sway(1, 20, 2.0)}, "wingR": {"rot": sway(1, 20, 2.0, 0.0, base=(0, 0, 0))},
                             "tail1": {"rot": sway(1, 18, 2.0)}, "tail2": {"rot": sway(1, 26, 2.0, 0.15)}, "tail3": {"rot": sway(1, 30, 2.0, 0.3)}}, 4.0)
    m.anims["idle"]["bones"]["wingR"] = {"rot": K((0, Z), (0.5, (0, -20, 0)), (1.0, Z), (1.5, (0, 20, 0)), (2.0, Z))}
    m.attacks = {"fire_ring": "slam", "leap": "lunge", "meteor": "cast", "breath": "roar"}
    m.melee = "swipe"
    return m


@big("bog_orc", "<gradient:#2e7d32:#e0e0e0><bold>Horngut</bold></gradient>", "Bully of the Swamp", "ZOMBIE", "toxic", "GREEN",
     extra=["slam", "poison", "minions"], minion="ZOMBIE", items=["SLIME_BALL 16", "IRON_INGOT 16", "DIAMOND 3"], top=["NETHERITE_SCRAP 1"],
     recipe=boss_recipe("ITEM_SLIME", "ENTITY_RAVAGER_ROAR", "ENTITY_RAVAGER_DEATH", "mud", 0.7, "roar", "die_back", ground_block="MUD"))
def bog_orc():
    """A huge pot-bellied swamp orc with mottled green skin, an iron helmet with two bull horns, an underbite
    with tusks, a fur pelt over one shoulder, swamp moss on its belt, rope-wrapped wrists and a spiked
    wooden club over its shoulder."""
    m = Model("bog_orc", "biped", 2.0)
    biped(m, hip=10, legx=4.5, neck=27, shoulder=26, armx=11)
    m.bone("club", "armR", (-12.5, 10, 0))
    m.hold = {"club": 40}
    s = Sheet(512, 256)
    s.rate = 0.15
    KK = {"s": "green_terracotta", "k": "black_concrete", "w": "yellow_concrete", "b": "black_terracotta", "m": "black_concrete", "t": "white_concrete", "n": "green_concrete", "c": "lime_terracotta"}
    legs2(m, s, (6, 9, 6), 4.5, ORC[0], [("lime_terracotta", 1)], boot="brown_terracotta", boot_tones=[])
    T(m, s, "hips", (16, 6, 11), (-8, 6, -5.5), LEATHER, 0.3, front=["................", "................", ".m.m..m...m..m.."] + ["................"] * 3, K={"m": "moss_block"})
    T(m, s, "body", (19, 15, 12), (-9.5, 11, -6), ORC, 0.25)
    tb(m, s, "body", (13, 9, 3), (-6.5, 11, 5), "lime_terracotta", [("green_terracotta", 1)], rate=0.25)
    T(m, s, "body", (10, 6, 13), (2, 21, -6.5), FUR_B, 0.4)
    arms2(m, s, (7, 14, 7), 26, 12.5, ORC[0], [("lime_terracotta", 1)], hand=ORC[0], hand_tones=[], hand_size=(7, 4, 7))
    for sd in (1, -1):
        tb(m, s, "armL" if sd == 1 else "armR", (8, 2, 8), (sd * 12.5 - 4, 15, -4), "spruce_planks", [("brown_terracotta", 1)], rate=0.4)
    tb(m, s, "head", (11, 10, 9), (-5.5, 26, -2), ORC[0], ORC[1], rate=0.15, front=face(11, 10, ey=4, gap=3, mouth="teeth", mw=7, nose=1), K=KK)
    for sd in (1, -1):
        m.c("head", "white_concrete", (sd * 3, 28.6, 7.4), (1.2, 3, 1.2))
    tb(m, s, "head", (12, 4, 10), (-6, 34, -2.5), "iron_block", IRON[1], rate=0.35, D="gray_concrete")
    for sd in (1, -1):
        horn(m, "head", "white_terracotta", (sd * 6, 36, 2), 4, (0, 0, -80 * sd), (0, 0, 30 * sd), 2.4, 0.8)
    m.c("club", "dark_oak_log", (-12.5, 15, 0), (2.4, 12, 2.4))
    tb(m, s, "club", (5, 9, 5), (-15, 20, -2.5), "dark_oak_log", [("spruce_log", 2), ("brown_terracotta", 1)], rate=0.35)
    for dy, dx, dz in ((23, 3, 0), (26, -3, 0), (24, 0, 3), (27, 0, -3)):
        m.c("club", "iron_block", (-12.5 + dx, dy, dz), (1, 1, 1))
    m.anims = idle("biped", {}, 4.0)
    m.attacks = {"slam": "slam", "poison": "roar", "minions": "stomp", "shockwave": "double"}
    m.melee = "swipe"
    return m


# ===================================================================================================== minis


def remake(id, recipe=None, **change):
    """A new model for an existing mini; its name, attacks and opening stay unless changed here."""
    def deco(fn):
        REVISED.add(id)
        # 1.3.3: only the minis the user named get the clean redraw; the rest keep their older look
        if id not in FIX: return fn
        if recipe: v9_minis.SPAWN[id], v9_minis.DEATH[id] = recipe
        if change: v9_minis.INFO[id].update(change)
        return model(fn)
    return deco


FIX = {"hay_golem", "moss_imp", "gilded_mimic", "mossling", "garden_gnome", "snapjaw", "stumpy"}


def fk(skin, eye="black_concrete", brow=None, mouth="black_concrete", tooth="white_concrete", nose=None, cheek="pink_concrete", glow="yellow_concrete"):
    return {"s": skin, "k": eye, "w": "white_concrete", "b": brow or eye, "m": mouth, "t": tooth, "n": nose or skin, "c": cheek, "e": glow}


def kid(m, s, hip, leg, body, head, arm, pants, cloth, skin, boots=None, fc=None, K=None, body_front=None, hand=None, armx=None, head_z=0.0, legx=None):
    """A small humanoid: legs with boots, a body, hanging arms with hands and a head with a face.
    Sizes are (w, h, d). Returns (neck, shoulder) heights."""
    lw, lh, ld = leg
    bw, bh, bd = body
    hw, hh, hd = head
    aw, ah, ad = arm
    neck, shoulder = hip + bh, hip + bh - 0.5
    lx = legx if legx is not None else max(lw / 2 + 0.2, bw / 4)
    ax = armx if armx is not None else bw / 2 + aw / 2
    biped(m, hip=hip, legx=lx, neck=neck, shoulder=shoulder, armx=ax)
    for sd, lg in ((1, "legL"), (-1, "legR")):
        T(m, s, lg, (lw, hip, ld), (sd * lx - lw / 2, 0, -ld / 2), pants, 0.3)
        if boots: T(m, s, lg, (lw + 1, 2, ld + 1), (sd * lx - (lw + 1) / 2, 0, -ld / 2 - 0.5 + 0.6), boots, 0.3)
    T(m, s, "body", (bw, bh, bd), (-bw / 2, hip, -bd / 2), cloth, 0.3, front=body_front, K=K)
    for sd, a in ((1, "armL"), (-1, "armR")):
        T(m, s, a, (aw, ah, ad), (sd * ax - aw / 2, shoulder - ah + 0.5, -ad / 2), cloth, 0.3)
        T(m, s, a, (aw, 2, ad), (sd * ax - aw / 2, shoulder - ah - 1.3, -ad / 2), hand or skin, 0.2)
    T(m, s, "head", (hw, hh, hd), (-hw / 2, neck, -hd / 2 + head_z), skin, 0.15, front=face(hw, hh, **(fc or {})), K=K)
    return neck, shoulder


def base_idle(m, rig="biped", extra=None, length=4.0):
    m.anims = idle(rig, extra or {}, length)


HAY = ("hay_block", [("yellow_terracotta", 2), ("orange_terracotta", 1), ("yellow_concrete", 1)])
BURLAP = ("white_terracotta", [("birch_planks", 2), ("smooth_sandstone", 1)])


@remake("hay_golem")
def hay_golem():
    """A scarecrow golem of tied hay bales with straw sticking out at the joints, a burlap sack head with
    stitched button eyes and a sewn grin, a crooked straw hat, a rope belt and a pitchfork."""
    m = Model("hay_golem", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = {"s": "white_terracotta", "k": "black_concrete", "w": "white_concrete", "b": "brown_terracotta", "m": "brown_terracotta", "t": "white_terracotta", "c": "white_terracotta", "n": "orange_terracotta", "r": "brown_concrete"}
    neck, sh = kid(m, s, 8, (4, 8, 4), (12, 11, 7), (9, 9, 8), (4, 10, 4), HAY, HAY, BURLAP, fc=dict(ey=3, gap=3, mouth="grin", mw=7, brow=False, catch=False), K=KK,
                   body_front=["............"] * 6 + ["rrrrrrrrrrrr", "rrrrrrrrrrrr"] + ["............"] * 3, hand=HAY)
    KK["r"] = "brown_concrete"
    for x, y, rot in ((-6, 16, 40), (6, 15, -40), (-3.5, 18.5, 15), (3.5, 18.5, -15), (0, 18.6, 0)):
        m.c("body", "yellow_concrete", (x, y, 0), (1, 3, 1), (0, 0, rot))
    for sd, a in ((1, "armL"), (-1, "armR")):
        for dz in (-1, 1):
            m.c(a, "yellow_concrete", (sd * 8, 7.2, dz), (0.8, 2.4, 0.8), (0, 0, 20 * sd))
    m.c("head", "brown_concrete", (0, neck + 0.4, 0), (8, 0.8, 7))
    T(m, s, "head", (13, 1, 12), (-6.5, neck + 8.6, -6), ("yellow_terracotta", [("hay_block", 2), ("orange_terracotta", 1)]), 0.4)
    T(m, s, "head", (8, 4, 7), (-4, neck + 9.6, -3.5), ("yellow_terracotta", [("hay_block", 2)]), 0.4, rot=(0, 0, -8), origin=(0, neck + 9.6, 0))
    m.bone("fork", "armR", (-8, 6, 0)); m.hold = {"fork": 10}
    m.c("fork", "spruce_planks", (-8, 9, 0), (1, 20, 1))
    for dx in (-1.5, 0, 1.5):
        m.c("fork", "iron_block", (-8 + dx, 20.5, 0), (0.6, 3, 0.6))
    m.c("fork", "iron_block", (-8, 19, 0), (3.6, 0.6, 0.6))
    base_idle(m)
    m.attacks = {"fire_ring": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


@remake("snapjaw", recipe=gen("SPORE_BLOSSOM_AIR", "BLOCK_BIG_DRIPLEAF_TILT_DOWN", "BLOCK_BIG_DRIPLEAF_BREAK", "moss_block", 0.8))
def snapjaw():
    """A hungry flower rooted in a mossy clump: a thick bending stem in three parts, wide leaves that flap,
    and a purple-spotted head that splits into a jaw full of white teeth and snaps at anything near."""
    m = Model("snapjaw", "biped", 1.2)
    m.bone("hips", "root", (0, 4, 0)); m.bone("body", "hips", (0, 5, 0))
    m.bone("stem2", "body", (0, 11, 0)); m.bone("head", "stem2", (0, 17, 1)); m.bone("jaw", "head", (0, 19, -2))
    m.bone("leafL", "body", (2, 6, 0)); m.bone("leafR", "body", (-2, 6, 0))
    s = Sheet(512, 256)
    s.rate = 1.25
    T(m, s, "hips", (12, 4, 12), (-6, 0, -6), MOSS, 0.4)
    T(m, s, "hips", (14, 2, 14), (-7, 0, -7), ("rooted_dirt", [("coarse_dirt", 2), ("mud", 1)]), 0.4)
    for sd, z in ((1, 5), (-1, -5), (1, -4), (-1, 4)):
        m.c("hips", "mangrove_roots" if False else "brown_terracotta", (sd * 6.5, 1, z), (3, 1.4, 1.4), (0, 0, -25 * sd))
    T(m, s, "body", (4, 7, 4), (-2, 4, -2), ("green_terracotta", [("lime_terracotta", 2), ("moss_block", 1)]), 0.4)
    T(m, s, "stem2", (3, 7, 3), (-1.5, 10.5, -1.5), ("green_terracotta", [("lime_terracotta", 2)]), 0.4)
    for sd, lf in ((1, "leafL"), (-1, "leafR")):
        T(m, s, lf, (8, 1, 4), (sd * 6 - 4, 6, -2), ("lime_terracotta", [("green_terracotta", 2), ("lime_concrete", 1)]), 0.45, rot=(0, 0, 25 * sd), origin=(sd * 2, 6, 0))
        T(m, s, lf, (6, 1, 3), (sd * 5 - 3, 9, -1.5), ("lime_terracotta", [("green_terracotta", 2)]), 0.45, rot=(0, 30 * sd, 35 * sd), origin=(sd * 2, 9, 0))
    PUR = ("purple_terracotta", [("magenta_terracotta", 2), ("purple_concrete", 1), ("white_terracotta", 1)])
    T(m, s, "head", (10, 5, 10), (-5, 19, -4), PUR, 0.55, L="magenta_terracotta")
    tb(m, s, "head", (9, 1, 9), (-4.5, 18.6, -3.5), "red_concrete", [("red_terracotta", 1)], rate=0.3)
    tb(m, s, "head", (10, 2, 2), (-5, 21, 5.6), "purple_terracotta", [], front=["..........", ".k.....k.."], K={"k": "yellow_concrete"}, lit=["yellow_concrete"])
    for i in range(5):
        m.c("head", "white_concrete", (-4 + i * 2, 18.4, 5.4), (1, 1.6, 1))
    T(m, s, "jaw", (10, 4, 10), (-5, 14.6, -4), PUR, 0.55, D="purple_concrete")
    tb(m, s, "jaw", (9, 1, 9), (-4.5, 18.4, -3.5), "red_concrete", [], rate=0)
    for i in range(5):
        m.c("jaw", "white_concrete", (-3 + i * 1.6, 19.4, 5.4), (1, 1.6, 1))
    m.no_elbows = True
    m.anims = {"idle": {"length": 3.0, "loop": True, "bones": {
        "body": {"rot": sway(2, 8, 3.0)}, "stem2": {"rot": sway(2, 12, 3.0, 0.15)}, "head": {"rot": sway(1, 18, 3.0, 0.3)},
        "jaw": {"rot": K((0, Z), (0.4, (-30, 0, 0)), (0.6, Z), (1.6, Z), (1.9, (-34, 0, 0)), (2.1, Z), (3.0, Z))},
        "leafL": {"rot": sway(2, 14, 1.5)}, "leafR": {"rot": sway(2, 14, 1.5, 0.5)}}}}
    m.attacks = {"poison": "roar", "pull": "swipe"}
    m.melee = "swipe"
    return m


@remake("pack_goblin")
def pack_goblin():
    """Snik the cutpurse goblin: green skin, huge pointed ears that twitch, a long nose, sly yellow eyes and
    a crooked grin, a brown hooded cloak, a bulging loot sack on his back and a little curved dagger."""
    m = Model("pack_goblin", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("lime_terracotta", eye="black_concrete", brow="green_terracotta", nose="green_terracotta")
    KK["e"] = "yellow_concrete"
    neck, sh = kid(m, s, 7, (3, 7, 3), (9, 9, 6), (9, 8, 8), (3, 9, 3), LEATHER, ("brown_wool", [("brown_terracotta", 2), ("spruce_planks", 1)]),
                   ("lime_terracotta", [("green_terracotta", 2), ("lime_concrete", 1)]), boots=("black_terracotta", [("brown_terracotta", 1)]),
                   fc=dict(ey=3, gap=3, mouth="grin", mw=5, nose=2, glow=True, brow=True), K=KK)
    m.bone("earL", "head", (4.5, neck + 4, 0)); m.bone("earR", "head", (-4.5, neck + 4, 0))
    for sd, e in ((1, "earL"), (-1, "earR")):
        m.c(e, "lime_terracotta", (sd * 7, neck + 4.5, 0), (5, 2.4, 1.4), (0, 0, 20 * sd))
        m.c(e, "green_terracotta", (sd * 9.4, neck + 5.6, 0), (2, 1.4, 1), (0, 0, 30 * sd))
    m.c("head", "green_terracotta", (0, neck + 2.6, 4.8), (2, 2, 2.4))
    T(m, s, "head", (10, 3, 9), (-5, neck + 7, -4.5), ("brown_wool", [("brown_terracotta", 2)]), 0.4)
    T(m, s, "head", (10, 6, 2), (-5, neck + 2, -5), ("brown_wool", [("brown_terracotta", 2)]), 0.4)
    m.bone("sack", "body", (0, 14, -4))
    T(m, s, "sack", (8, 8, 6), (-4, 9, -9), ("white_terracotta", [("birch_planks", 2), ("smooth_sandstone", 1)]), 0.4)
    m.c("sack", "gold_block", (1, 17.4, -6), (2, 1.2, 2)); m.c("sack", "emerald_block", (-1.5, 17.2, -6.5), (1.4, 1.4, 1.4))
    m.bone("dagger", "armR", (-6, 2, 1)); m.hold = {"dagger": 60}
    m.c("dagger", "brown_terracotta", (-6, 2, 1), (1, 2, 1)); m.c("dagger", "iron_block", (-6, 5, 1), (0.8, 4, 0.5), (0, 0, 10))
    base_idle(m, extra={"earL": {"rot": K((0, Z), (1.8, Z), (2.0, (0, 0, 20)), (2.2, Z), (4.0, Z))},
                        "earR": {"rot": K((0, Z), (2.6, Z), (2.8, (0, 0, -20)), (3.0, Z), (4.0, Z))}, "sack": {"rot": sway(2, 5, 2.0)}})
    m.attacks = {"volley": "double", "blink": "lunge"}
    m.melee = "swipe"
    return m


@remake("garden_gnome")
def garden_gnome():
    """Mister Pebbles, a garden gnome come to life: a tall red pointed hat that flops as he walks, a big
    white beard, a round pink nose and rosy cheeks, a blue coat with a black belt, brown boots and a
    tiny shovel."""
    m = Model("garden_gnome", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("pink_terracotta", nose="pink_concrete", cheek="red_terracotta", brow="white_wool")
    KK.update({"y": "gold_block"})
    neck, sh = kid(m, s, 5, (3, 5, 3), (10, 8, 7), (9, 7, 8), (3, 7, 3), ("blue_wool", [("blue_terracotta", 1)]), ("blue_wool", [("blue_concrete", 2), ("light_blue_terracotta", 1)]),
                   SKIN, boots=("brown_terracotta", [("brown_concrete", 1)]), fc=dict(ey=2, gap=3, mouth=None, nose=2, cheeks=True), K=KK,
                   body_front=[".........."] * 4 + ["kkkkkkkkkk", "kkkkyykkkk"] + [".........."] * 2)
    KK.update({"y": "gold_block"})
    T(m, s, "head", (9, 6, 2), (-4.5, neck - 3, 3), ("white_wool", [("snow_block", 2), ("light_gray_wool", 1)]), 0.4,
      front=["w.......w", "ww.....ww", "wwwwwwwww", "wwwwwwwww", ".wwwwwww.", "..wwwww.."], K={"w": "white_wool"})
    m.bone("hat1", "head", (0, neck + 7, 0)); m.bone("hat2", "hat1", (0, neck + 11, 0)); m.bone("hat3", "hat2", (0, neck + 15, 0))
    RH = ("red_wool", [("red_concrete", 2), ("red_terracotta", 1)])
    T(m, s, "hat1", (10, 4, 9), (-5, neck + 6.5, -4.5), RH, 0.35)
    T(m, s, "hat2", (7, 4, 6), (-3.5, neck + 10.5, -3), RH, 0.35)
    T(m, s, "hat3", (4, 4, 4), (-2, neck + 14.5, -2), RH, 0.35)
    m.c("hat3", "red_terracotta", (0, neck + 19.5, 0), (2, 2, 2))
    m.bone("shovel", "armL", (6.5, 2, 0)); m.hold = {"shovel": 10}
    m.c("shovel", "spruce_planks", (6.5, 5, 0), (0.8, 10, 0.8)); m.c("shovel", "iron_block", (6.5, 11, 0), (2.4, 3, 0.6))
    base_idle(m, extra={"hat1": {"rot": sway(2, 5, 4.0)}, "hat2": {"rot": sway(2, 9, 4.0, 0.1)}, "hat3": {"rot": sway(2, 16, 4.0, 0.2)}})
    m.attacks = {"spikes": "slam", "heal": "roar"}
    m.melee = "swipe"
    return m


@remake("pink_burrower")
def pink_burrower():
    """A plump pink naked mole the size of a pig: wrinkled pink hide, tiny squinting eyes, two long yellow
    buck teeth, a twitching snout, big shovel claws for digging and clumps of dirt on its back."""
    m = Model("pink_burrower", "quad", 1.2)
    quad4(m, 7, 4.5, 5, -5, 9, 7, 9)
    s = Sheet(512, 256)
    s.rate = 1.25
    PK = ("pink_terracotta", [("pink_concrete", 2), ("white_terracotta", 2), ("terracotta", 1)])
    for leg, z in (("legFL", 5), ("legBL", -5)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            T(m, s, lg, (3, 7, 3), (sd * 4.5 - 1.5, 0.6, z - 1.5), PK, 0.4)
            for dx in (-1, 0, 1):
                m.c(lg, "white_terracotta", (sd * 4.5 + dx, 0.3, z + 2), (0.6, 0.6, 2))
    T(m, s, "body", (12, 10, 18), (-6, 5, -10), PK, 0.4, L="pink_concrete")
    T(m, s, "body", (8, 2, 6), (-4, 15, -6), ("coarse_dirt", [("rooted_dirt", 2), ("dirt", 1)]), 0.5)
    m.c("body", "dirt", (3, 16, 2), (3, 1.4, 3)); m.c("body", "coarse_dirt", (-3.5, 15.6, -9), (3, 1.4, 3))
    T(m, s, "neck", (10, 8, 4), (-5, 6, 7), PK, 0.4)
    T(m, s, "head", (9, 7, 7), (-4.5, 6.5, 10), PK, 0.3, front=["sssssssss", "sssssssss", "skkssskks", "sssssssss", "sssnnnsss", "ssssmssss", "ssssyssss"],
      K={"s": "pink_terracotta", "k": "black_concrete", "n": "pink_concrete", "m": "red_terracotta", "y": "yellow_concrete"})
    for x in (-0.6, 0.6):
        m.c("jaw", "yellow_concrete", (x, 5, 17.2), (1, 3, 0.8))
    m.c("head", "pink_concrete", (0, 10, 17.4), (3, 2, 1))
    T(m, s, "tail", (2, 2, 5), (-1, 9, -14), PK, 0.4)
    m.anims = idle("quad", {"head": {"rot": K((0, Z), (0.3, (6, 0, 0)), (0.6, Z), (0.9, (6, 0, 0)), (1.2, Z), (4.0, Z))}})
    m.attacks = {"minions": "rear", "quake": "toss"}
    m.melee = "bite"
    return m


@remake("moss_imp")
def moss_imp():
    """A little old imp grown over with moss: a round green body, leaf ears that flick, two twig horns, a
    red cap mushroom sprouting from its head, big glowing amber eyes over a toothy grin and a bark loincloth."""
    m = Model("moss_imp", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("moss_block", brow="green_terracotta", mouth="black_concrete", glow="orange_concrete")
    neck, sh = kid(m, s, 5, (3, 5, 3), (10, 8, 8), (10, 8, 8), (3, 8, 3), MOSS, MOSS, MOSS, boots=("brown_terracotta", [("spruce_planks", 1)]),
                   fc=dict(ey=2, gap=2, ew=3, eh=2, mouth="grin", mw=6, glow=True), K=KK, hand=("green_terracotta", []))
    T(m, s, "hips", (11, 3, 9), (-5.5, 3.5, -4.5), BARK, 0.4)
    m.bone("earL", "head", (5, neck + 5, 0)); m.bone("earR", "head", (-5, neck + 5, 0))
    for sd, e in ((1, "earL"), (-1, "earR")):
        T(m, s, e, (5, 3, 1), (sd * 7.5 - 2.5, neck + 4, -0.5), ("lime_terracotta", [("green_terracotta", 2)]), 0.4, rot=(0, 0, 25 * sd), origin=(sd * 5, neck + 5, 0))
        horn(m, "head", "spruce_log", (sd * 3, neck + 8, 0), 3, (0, 0, -20 * sd), (-15, 0, 15 * sd), 1.2, 0.8)
    m.c("head", "white_terracotta", (-2, neck + 9, -1), (1.2, 2, 1.2))
    m.c("head", "red_concrete", (-2, neck + 10.4, -1), (4, 1.4, 4)); m.c("head", "white_concrete", (-1.4, neck + 11.2, -0.6), (1, 0.4, 1))
    base_idle(m, extra={"earL": {"rot": K((0, Z), (1.0, (0, 0, 15)), (1.2, Z), (4.0, Z))}, "earR": {"rot": K((0, Z), (2.4, (0, 0, -15)), (2.6, Z), (4.0, Z))}})
    m.attacks = {"levitate": "cast", "pull": "swipe"}
    m.melee = "swipe"
    return m


@remake("mossling")
def mossling():
    """A round moss bush that hatched legs: a fat leafy ball with two big shiny black eyes, a little open
    mouth, a pink flower and a white flower on top, stubby brown legs and leafy arms that wave."""
    m = Model("mossling", "biped", 1.2)
    biped(m, hip=5, legx=2.6, neck=12, shoulder=11, armx=7.5)
    s = Sheet(512, 256)
    s.rate = 1.25
    for sd, lg in ((1, "legL"), (-1, "legR")):
        T(m, s, lg, (3, 5, 3), (sd * 2.6 - 1.5, 0, -1.5), LEATHER, 0.3)
        T(m, s, lg, (4, 1, 5), (sd * 2.6 - 2, 0, -2), ("brown_terracotta", []), 0.1)
    LEAF = ("moss_block", [("azalea_leaves", 2), ("green_terracotta", 2), ("lime_terracotta", 1)])
    T(m, s, "body", (14, 12, 13), (-7, 4, -6.5), LEAF, 0.55, front=["..............", "..............", "...kkk...kkk..", "..kkwkk.kkwkk.", "..kkkkk.kkkkk.", "...kkk...kkk..",
      "..............", "......mm......", "......mm......", "..............", "..............", ".............."], K={"k": "black_concrete", "w": "white_concrete", "m": "black_terracotta"})
    m.c("head", "moss_block", (0, 16.4, 0), (10, 1.2, 9))
    m.c("head", "green_terracotta", (2, 17.6, 1), (0.8, 2, 0.8)); m.c("head", "pink_concrete", (2, 18.8, 1), (2.4, 1, 2.4)); m.c("head", "yellow_concrete", (2, 19.3, 1), (0.8, 0.6, 0.8))
    m.c("head", "green_terracotta", (-3, 17.4, -2), (0.8, 1.6, 0.8)); m.c("head", "white_concrete", (-3, 18.4, -2), (2, 1, 2))
    for sd, a in ((1, "armL"), (-1, "armR")):
        T(m, s, a, (2, 6, 2), (sd * 7.5 - 1, 5, -1), LEAF, 0.4)
        T(m, s, a, (4, 3, 2), (sd * 8 - 2, 3, -1), ("azalea_leaves", [("moss_block", 1)]), 0.4)
    base_idle(m, extra={"armL": {"rot": sway(2, 25, 1.5, base=(0, 0, 10))}, "armR": {"rot": sway(2, 25, 1.5, 0.5, base=(0, 0, -10))}}, length=3.0)
    m.attacks = {"leap": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@remake("bark_ape")
def bark_ape():
    """A cheeky jungle ape in dark brown fur with plates of bark grown over its shoulders and back, a pale
    tan face with a wide nose and a toothy grin, long knuckle-dragging arms and a curled tail."""
    m = Model("bark_ape", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("white_terracotta", brow="brown_terracotta", nose="brown_terracotta", cheek="pink_terracotta")
    neck, sh = kid(m, s, 6, (4, 6, 4), (12, 10, 8), (9, 8, 8), (4, 12, 4), FUR_B, FUR_B, FUR_B, fc=dict(), K=KK, hand=("brown_terracotta", []), armx=8)
    T(m, s, "head", (7, 6, 1), (-3.5, neck, 4), ("white_terracotta", [("pink_terracotta", 1)]), 0.2, front=face(7, 6, ey=1, gap=1, mouth="grin", mw=5, nose=1), K=KK)
    for sd in (1, -1):
        m.c("head", "brown_wool", (sd * 5, neck + 4, 0), (1.4, 3, 3)); m.c("head", "pink_terracotta", (sd * 5.4, neck + 4, 0), (0.6, 2, 2))
    for x, y, z, w, h in ((-5, 14, 0, 4, 3), (5, 14.5, 0, 4, 3), (0, 12, -4.4, 8, 6)):
        T(m, s, "body", (w, h, 2 if z else 8), (x - w / 2, y, z - (1 if z else 4)), BARK, 0.4)
    m.rest("body", (12, 0, 0))
    m.bone("tail", "hips", (0, 6, -4))
    m.c("tail", "brown_wool", (0, 7, -6), (1.4, 1.4, 4), (-30, 0, 0)); m.c("tail", "brown_wool", (0, 9.6, -7.8), (1.4, 3, 1.4), (20, 0, 0))
    base_idle(m, extra={"tail": {"rot": sway(1, 20, 2.0)}})
    m.attacks = {"leap": "lunge", "volley": "double"}
    m.melee = "swipe"
    m.bend = -20
    return m


@remake("old_blindman")
def old_blindman():
    """Old Hoodlum, a stooped old man in a patched brown hood and cloak: a long grey beard to his belt, a
    big nose, a grey cloth tied over his eyes, a rope belt with a pouch and a crooked walking stick with a
    lantern hanging from the top."""
    m = Model("old_blindman", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("pink_terracotta", eye="light_gray_wool", brow="light_gray_wool", nose="terracotta")
    CLK = ("brown_wool", [("brown_terracotta", 2), ("spruce_planks", 1), ("terracotta", 1)])
    neck, sh = kid(m, s, 7, (3, 7, 3), (10, 11, 6), (8, 8, 7), (3, 11, 3), CLK, CLK, SKIN, boots=("black_terracotta", []),
                   fc=dict(ey=2, gap=2, ew=2, eh=1, mouth=None, nose=2, brow=False, catch=False), K=KK)
    tb(m, s, "head", (8, 1, 1), (-4, neck + 5, 3.5), "light_gray_wool", [], rate=0)
    T(m, s, "head", (8, 7, 2), (-4, neck - 4, 3.2), ("light_gray_wool", [("white_wool", 2), ("gray_wool", 1)]), 0.45,
      front=["gggggggg", "gggggggg", "gggggggg", ".gggggg.", ".gggggg.", "..gggg..", "...gg..."], K={"g": "light_gray_wool"})
    T(m, s, "head", (10, 2, 9), (-5, neck + 8, -4.6), CLK, 0.35)
    T(m, s, "head", (10, 9, 1), (-5, neck - 1, -4.6), CLK, 0.35)
    for sd in (1, -1):
        T(m, s, "head", (1, 9, 8), (sd * 4.5 - 0.5, neck - 1, -3.6), CLK, 0.35)
    m.rest("body", (16, 0, 0))
    m.c("body", "spruce_planks", (0, 9.4, 0), (10.4, 1, 6.4)); m.c("body", "brown_concrete", (3, 8, 3.4), (2.4, 2.4, 1.4))
    m.bone("stick", "armR", (-6.5, 4, 0)); m.hold = {"stick": 0}
    m.c("stick", "dark_oak_log", (-6.5, 8, 0), (1.2, 18, 1.2)); m.c("stick", "dark_oak_log", (-5.5, 17.2, 0), (2.4, 1, 1))
    m.bone("lamp", "stick", (-4.6, 16.6, 0))
    m.c("lamp", "chain", (-4.6, 15.6, 0), (0.6, 2, 0.6)); m.c("lamp", "lantern", (-4.6, 13.6, 0), (2, 2.4, 2), light=True)
    base_idle(m, extra={"lamp": {"rot": sway(2, 16, 2.0)}, "head": {"rot": K((0, Z), (1.5, (0, 30, 6)), (2.2, (0, 30, 6)), (3.2, (0, -25, -4)), (4.0, Z))}})
    m.attacks = {"darkness": "cast", "pull": "swipe"}
    m.melee = "swipe"
    return m


def ghost(id, eyes, tint, arm_up=False):
    """One ghost kid: a wide flat head with hollow eyes, a ragged sheet body and dangling legs."""
    m = Model(id, "float", 1.2)
    m.bone("core", "root", (0, 8, 0))
    m.bone("head", "core", (0, 16, 0))
    m.bone("armL", "core", (4, 15, 0)); m.bone("armR", "core", (-4, 15, 0))
    m.bone("ring1", "core", (0, 8, 0))
    m.bone("legs", "core", (0, 8, 0))
    m.no_elbows = True
    s = Sheet(512, 256)
    s.rate = 1.9
    GH = (tint, [("white_wool", 2), ("light_gray_terracotta", 1), ("gray_wool", 1)])
    T(m, s, "head", (12, 8, 9), (-6, 16, -4.5), GH, 0.35, L="white_wool", front=eyes,
      K={"w": tint, "k": "black_concrete", "b": "light_blue_concrete", "g": "gray_concrete"}, lit=["light_blue_concrete"])
    T(m, s, "core", (8, 8, 6), (-4, 8.6, -3), GH, 0.4, D="gray_wool")
    for i in range(7):
        m.c("core", "gray_wool", (-3.6 + i * 1.2, 8.2 - (i % 2) * 0.6, 2.6), (1, 1.2 + (i % 2) * 0.8, 0.8))
        m.c("core", "light_gray_wool", (-3.6 + i * 1.2, 8.2 - ((i + 1) % 2) * 0.6, -2.6), (1, 1.2 + ((i + 1) % 2) * 0.8, 0.8))
    for sd, a in ((1, "armL"), (-1, "armR")):
        T(m, s, a, (2, 7, 2), (sd * 5 - 1, 9, -1), GH, 0.4, rot=(0, 0, (35 if arm_up else 20) * sd), origin=(sd * 4, 15, 0))
    for sd in (1, -1):
        T(m, s, "legs", (2, 6, 2), (sd * 1.8 - 1, 2.6, -1), GH, 0.45, D="gray_wool")
    m.anims = {"idle": {"length": 2.4, "loop": True, "bones": {
        "core": {"pos": K((0, Z), (0.6, (0, 2.4, 0)), (1.2, Z), (1.8, (0, -1, 0)), (2.4, Z)), "rot": sway(2, 8, 2.4)},
        "head": {"rot": K((0, (0, -14, 0)), (1.2, (6, 14, 4)), (2.4, (0, -14, 0)))},
        "legs": {"rot": sway(0, 14, 1.2)}, "armL": {"rot": sway(2, 16, 1.2)}, "armR": {"rot": sway(2, 16, 1.2, 0.5)}}}}
    m.attacks = {"darkness": "pulse", "blink": "spin", "dive": "dive"}
    m.melee = "swipe"
    return m


@remake("boo_twins", name="<gradient:#bdbdbd:#ffffff><bold>Boo</bold></gradient>", title="The Older Twin")
def boo_twins():
    """Boo, the older of the Boo Twins: a pale ghost kid with a wide flat head, round hollow eyes with a
    blue glint, a ragged sheet body and dangling legs. It bobs and drifts; its twin hunts someone else."""
    return ghost("boo_twins", ["wwwwwwwwwwww", "wwwwwwwwwwww", "wwkkwwwwkkww", "wwkbwwwwbkww", "wwkkwwwwkkww", "wwwwwkkwwwww", "wwwwwkkwwwww", "wwwwwwwwwwww"], "light_gray_wool")


@partner("boo_twins", "boo_twin_b", "<gradient:#e0e0e0:#b3e5fc><bold>Hoo</bold></gradient>", "The Younger Twin", entity="VEX", theme="soul", bar="WHITE",
         extra=["darkness", "blink"], movement="hover", speed=0.34,
         recipe=gen("SOUL", "ENTITY_VEX_AMBIENT", "ENTITY_VEX_DEATH", "white_wool", 1.6, "pulse", "die_drop"))
def boo_twin_b():
    """Hoo, the younger Boo Twin: smaller and whiter, with tall oval eyes and a wobbly open mouth, arms
    raised to scare. Quicker than Boo, it darts around and goes after a different player."""
    return ghost("boo_twin_b", ["wwwwwwwwwwww", "wwkkkwwkkkww", "wwkkkwwkkkww", "wwkkkwwkkkww", "wwwwwwwwwwww", "wwwwkkkkwwww", "wwwwkwwkwwww", "wwwwwwwwwwww"], "snow_block", arm_up=True)


def toadstool(id, cap, spots, size, face_kw):
    m = Model(id, "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    sc = size
    STALK = ("white_terracotta", [("birch_planks", 2), ("smooth_sandstone", 1), ("diorite", 1)])
    KK = fk("white_terracotta", brow="brown_terracotta", cheek="pink_terracotta")
    neck, sh = kid(m, s, round(4 * sc), (3, round(4 * sc), 3), (round(9 * sc), round(8 * sc), round(7 * sc)), (round(9 * sc), round(6 * sc), round(7 * sc)),
                   (3, round(6 * sc), 3), STALK, STALK, STALK, boots=("brown_terracotta", []), fc=face_kw, K=KK)
    cw = round(16 * sc)
    T(m, s, "head", (cw, round(4 * sc), cw), (-cw / 2, neck + round(5 * sc), -cw / 2), cap, 0.3, L=cap[1][0][0],
      top=[("".join("w" if (x * 7 + y * 3) % 11 == 0 else "." for x in range(cw))) for y in range(cw)] if spots else None, K={"w": "white_concrete"})
    T(m, s, "head", (cw - 4, 2, cw - 4), (-(cw - 4) / 2, neck + round(9 * sc), -(cw - 4) / 2), cap, 0.3)
    tb(m, s, "head", (cw - 2, 1, cw - 2), (-(cw - 2) / 2, neck + round(5 * sc) - 0.6, -(cw - 2) / 2), "white_terracotta", [("pink_terracotta", 1)], rate=0.3,
       front=None)
    if spots:
        for x, z in ((-cw / 3, 0), (cw / 4, cw / 4), (0, -cw / 3), (cw / 3, -cw / 5)):
            m.c("head", "white_concrete", (x, neck + round(5 * sc) + round(4 * sc) + 0.3, z), (2, 0.8, 2))
    return m, neck


@remake("cap_brothers", name="<gradient:#b71c1c:#ffccbc><bold>Toadstool</bold></gradient>", title="The Grumpier Mushroom")
def cap_brothers():
    """Toadstool, the big brother: a stout walking mushroom with a wide red cap spotted white, a pale
    stalk body with a cross little face, stubby legs and a puff of spores when it stomps. His brother
    Puffball fights beside him."""
    m, neck = toadstool("cap_brothers", ("red_concrete", [("red_terracotta", 2), ("red_wool", 1)]), True, 1.0,
                        dict(ey=2, gap=2, mouth="frown", mw=4))
    base_idle(m, extra={"head": {"rot": K((0, Z), (1.0, (0, 0, 6)), (2.0, Z), (3.0, (0, 0, -6)), (4.0, Z))}})
    m.attacks = {"poison": "roar", "minions": "stomp"}
    m.melee = "swipe"
    return m


@partner("cap_brothers", "cap_little", "<gradient:#6d4c41:#ffe0b2><bold>Puffball</bold></gradient>", "The Little Mushroom", entity="ZOMBIE", theme="toxic", bar="YELLOW",
         extra=["poison", "leap"], speed=0.33, recipe=gen("SPORE_BLOSSOM_AIR", "ENTITY_SLIME_JUMP_SMALL", "ENTITY_SLIME_DEATH_SMALL", "brown_mushroom_block", 1.6))
def cap_little():
    """Puffball, the little brother: a short mushroom with a round brown cap, a happy face and quick
    feet. He hops around and chases a different player from his brother."""
    m, neck = toadstool("cap_little", ("brown_mushroom_block", [("brown_terracotta", 2), ("brown_concrete", 1), ("terracotta", 1)]), False, 0.85,
                        dict(ey=2, gap=2, mouth="smile", mw=4, cheeks=True))
    base_idle(m, extra={"hips": {"pos": K((0, Z), (0.3, (0, 1.2, 0)), (0.6, Z), (2.0, Z), (2.3, (0, 1.2, 0)), (2.6, Z), (4.0, Z))}})
    m.attacks = {"poison": "roar", "leap": "lunge"}
    m.melee = "swipe"
    return m


@partner("gnome_brothers", "gnome_little", "<gradient:#c62828:#ffcdd2><bold>Thimble</bold></gradient>", "The Little Brother", entity="ZOMBIE", theme="nature", bar="GREEN",
         extra=["leap", "volley"], speed=0.32, tier="big", recipe=gen("HAPPY_VILLAGER", "ENTITY_VILLAGER_YES", "ENTITY_VILLAGER_DEATH", "moss_block", 1.6))
def gnome_little():
    """Thimble, the little Gnome Brother: a tall red hat that flops, a checked white beard, a green coat and
    a peach face with a round nose. He darts about on his own while Bramble fights."""
    m = Model("gnome_little", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("pink_terracotta", nose="pink_concrete", cheek="red_terracotta", brow="white_wool")
    neck, sh = kid(m, s, 5, (3, 5, 3), (10, 8, 7), (9, 7, 8), (3, 7, 3), ("brown_terracotta", [("brown_concrete", 1)]), ("green_terracotta", [("green_concrete", 2), ("lime_terracotta", 1)]),
                   SKIN, boots=("dark_oak_planks", []), fc=dict(ey=2, gap=3, mouth=None, nose=2, cheeks=True), K=KK)
    chk = lambda w, h: ["".join("g" if (x // 2 + y // 2) % 2 else "w" for x in range(w)) for y in range(h)]
    T(m, s, "head", (9, 7, 2), (-4.5, neck - 4, 3), ("white_wool", []), 0.1, front=chk(9, 7), K={"w": "white_wool", "g": "light_gray_wool"})
    m.bone("hat1", "head", (0, neck + 7, 0)); m.bone("hat2", "hat1", (0, neck + 12, 0)); m.bone("hat3", "hat2", (0, neck + 17, 0))
    RH = ("red_terracotta", [("red_concrete", 2), ("brown_terracotta", 1)])
    T(m, s, "hat1", (10, 5, 9), (-5, neck + 6.5, -4.5), RH, 0.35)
    T(m, s, "hat2", (7, 5, 6), (-3.5, neck + 11.5, -3), RH, 0.35)
    T(m, s, "hat3", (4, 5, 4), (-2, neck + 16.5, -2), RH, 0.35)
    base_idle(m, extra={"hat1": {"rot": sway(2, 6, 3.0)}, "hat2": {"rot": sway(2, 10, 3.0, 0.1)}, "hat3": {"rot": sway(2, 18, 3.0, 0.2)},
                        "hips": {"pos": K((0, Z), (0.4, (0, 1.4, 0)), (0.8, Z), (1.6, Z), (2.0, (0, 1.4, 0)), (2.4, Z), (3.0, Z))}}, length=3.0)
    m.attacks = {"leap": "lunge", "volley": "double"}
    m.melee = "swipe"
    return m


import v11_new as _v11
_old_gnomes = _v11.gnome_brothers


def gnome_brothers():
    """Bramble, the big Gnome Brother: a tall green bent hat that sways, a checked white beard, a peach
    nose and a red coat. His little brother Thimble fights beside him and goes after someone else."""
    m = _old_gnomes()
    little = {"little", "lhead", "lhat1", "lhat2"}
    m.cubes = [c for c in m.cubes if c["b"] not in little]
    m.bones = [b for b in m.bones if b["name"] not in little]
    m.names -= little
    for b in little: m.anims["idle"]["bones"].pop(b, None)
    return m


REVISED.add("gnome_brothers")  # back to the v11 two-brother model


@remake("king_oldbeard")
def king_oldbeard():
    """King Oldbeard, a stout dwarf king: a gold crown with red gems, a huge braided ginger beard tied with
    gold rings, a red royal cape that sways, a fur collar, iron boots and a double-headed axe."""
    m = Model("king_oldbeard", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("pink_terracotta", brow="orange_terracotta", nose="terracotta")
    neck, sh = kid(m, s, 5, (4, 5, 4), (12, 9, 8), (9, 8, 8), (4, 9, 4), ("brown_terracotta", [("brown_concrete", 1)]), ("red_wool", [("red_terracotta", 2), ("red_concrete", 1)]),
                   SKIN, boots=IRON, fc=dict(ey=2, gap=3, mouth=None, nose=2), K=KK)
    BE = ("orange_terracotta", [("red_terracotta", 1), ("orange_concrete", 1)])
    T(m, s, "head", (9, 6, 2), (-4.5, neck - 3, 3), BE, 0.4)
    for sd in (1, -1):
        m.c("body", "orange_terracotta", (sd * 2, neck - 6, 4.6), (2, 4, 1.6)); m.c("body", "gold_block", (sd * 2, neck - 8.4, 4.6), (2.2, 1, 1.8))
    T(m, s, "body", (13, 2, 9), (-6.5, neck - 1, -4.5), ("white_wool", [("light_gray_wool", 2), ("snow_block", 1)]), 0.45)
    tb(m, s, "head", (10, 3, 9), (-5, neck + 7.6, -4.5), "gold_block", [("yellow_concrete", 1)], rate=0.3, front=["g.g.g.g.g.", "gggrggrggg"[:10], "gggggggggg"],
       K={"g": "gold_block", "r": "red_concrete"})
    m.bone("cape", "body", (0, sh, -4))
    T(m, s, "cape", (12, 13, 1), (-6, 1, -5), ("red_wool", [("red_concrete", 2), ("red_terracotta", 1)]), 0.35)
    m.bone("axe", "armR", (-8, 2, 0)); m.hold = {"axe": 10}
    m.c("axe", "dark_oak_log", (-8, 6, 0), (1.2, 16, 1.2))
    tb(m, s, "axe", (6, 5, 1), (-11, 11, -0.5), "iron_block", IRON[1], rate=0.4)
    base_idle(m, extra={"cape": {"rot": sway(0, 6, 4.0, base=(6, 0, 0))}})
    m.attacks = {"minions": "roar", "orbs": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@remake("straw_farmer")
def straw_farmer():
    """Farmer Grimbly, an illager farmer: grey-green skin, a long nose and one thick brow, a wide frayed straw
    hat, a checked shirt under blue overalls, muddy boots and a scythe over his shoulder."""
    m = Model("straw_farmer", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("light_gray_terracotta", brow="black_terracotta", nose="gray_terracotta")
    neck, sh = kid(m, s, 7, (3, 7, 3), (10, 10, 6), (8, 10, 8), (3, 10, 3), ("blue_wool", [("blue_terracotta", 1)]),
                   ("red_terracotta", [("white_terracotta", 1), ("red_wool", 1)]), ("light_gray_terracotta", [("gray_terracotta", 1)]),
                   boots=("brown_terracotta", [("mud", 1)]), fc=dict(ey=3, gap=2, mouth="line", mw=4, nose=3), K=KK)
    tb(m, s, "body", (8, 7, 1), (-4, 7, 3), "blue_wool", [("blue_terracotta", 1)], rate=0.3, front=["s......s", "s......s", "........", "........", "...yy...", "........", "........"],
       K={"s": "gold_block", "y": "blue_terracotta"})
    T(m, s, "head", (16, 1, 16), (-8, neck + 9.6, -8), HAY, 0.4)
    T(m, s, "head", (9, 3, 9), (-4.5, neck + 10.4, -4.5), HAY, 0.4)
    m.c("head", "red_terracotta", (0, neck + 10.9, 0), (9.4, 1, 9.4))
    m.bone("scythe", "armR", (-6.5, 4, 0)); m.hold = {"scythe": 0}
    m.c("scythe", "spruce_planks", (-6.5, 10, 0), (1, 22, 1))
    tb(m, s, "scythe", (9, 2, 1), (-6.5, 19, -0.5), "iron_block", IRON[1], rate=0.4)
    base_idle(m)
    m.attacks = {"minions": "roar", "volley": "sweep"}
    m.melee = "swipe"
    return m


@remake("gilded_mimic")
def gilded_mimic():
    """A treasure chest that bites: dark wood planks banded with gold, a gold lock plate with a red jewel, a
    lid that lifts to show rows of white teeth, a long red tongue lolling out and little gold coins
    spilling round its feet."""
    m = Model("gilded_mimic", "slime", 1.2)
    m.bone("body", "root", (0, 6, 0)); m.bone("lid", "body", (0, 11, -6)); m.bone("tongue", "body", (0, 9, 4))
    s = Sheet(512, 256)
    s.rate = 1.6
    WOOD = ("dark_oak_planks", [("spruce_planks", 2), ("brown_terracotta", 1)])
    T(m, s, "body", (16, 10, 12), (-8, 1, -6), WOOD, 0.4, front=["g..............g"] * 2 + ["gggggggggggggggg"] + ["g..............g"] * 5 + ["gggggggggggggggg", "g..............g"],
      K={"g": "gold_block"})
    T(m, s, "lid", (16, 5, 12), (-8, 11, -6), WOOD, 0.4, front=["gggggggggggggggg", "g......r.......g", "g.....ggg......g", "g..............g", "gggggggggggggggg"],
      K={"g": "gold_block", "r": "red_concrete"})
    for i in range(7):
        m.c("body", "white_concrete", (-6 + i * 2, 11.6, 5.4), (1, 1.6, 1)); m.c("lid", "white_concrete", (-5 + i * 2, 10.6, 5.4), (1, 1.6, 1))
    m.c("body", "red_concrete", (0, 11, 0), (13, 0.6, 9))
    m.c("tongue", "red_concrete", (0, 9.5, 8), (3, 0.8, 6), (30, 0, 0)); m.c("tongue", "pink_concrete", (0, 6.5, 10.6), (3, 3, 0.8))
    for x, z in ((-9, 4), (8, 6), (5, 9), (-6, 8), (10, -3)):
        m.c("body", "gold_block", (x, 0.3, z), (1.6, 0.6, 1.6))
    m.anims = {"idle": {"length": 3.0, "loop": True, "bones": {
        "lid": {"rot": K((0, Z), (0.5, (-22, 0, 0)), (0.8, (-4, 0, 0)), (1.1, (-22, 0, 0)), (1.6, Z), (3.0, Z))},
        "tongue": {"rot": sway(1, 16, 1.5)}, "body": {"pos": K((0, Z), (1.5, (0, 0.6, 0)), (3.0, Z))}}}}
    m.attacks = {"orbs": "spit", "leap": "hop", "slam": "slam"}
    m.melee = "hop"
    return m


@remake("apple_crab", recipe=gen("HAPPY_VILLAGER", "ENTITY_SPIDER_AMBIENT", "ENTITY_SPIDER_DEATH", "red_concrete", 1.4, "rear", "die_side"))
def apple_crab():
    """A crab wearing a big red apple as its shell, a green leaf and stalk on top, beady eyes on stalks,
    orange pincers that click and six little legs that tap."""
    m = Model("apple_crab", "quad", 1.2)
    quad4(m, 5, 6, 3, -3, 6, 5, 6)
    m.bone("clawL", "body", (7, 6, 5)); m.bone("clawR", "body", (-7, 6, 5))
    m.bone("legML", "body", (7, 5, 0)); m.bone("legMR", "body", (-7, 5, 0))
    s = Sheet(512, 256)
    s.rate = 1.25
    AP = ("red_concrete", [("red_terracotta", 2), ("red_wool", 1), ("orange_terracotta", 1)])
    T(m, s, "body", (13, 9, 12), (-6.5, 4, -6), AP, 0.45, L="red_wool")
    T(m, s, "body", (9, 2, 8), (-4.5, 13, -4), AP, 0.45)
    m.c("body", "brown_terracotta", (0, 16, 0), (1, 3, 1)); m.c("body", "lime_terracotta", (2, 16.4, 0), (4, 0.8, 2.4), (0, 0, 15))
    tb(m, s, "head", (8, 3, 2), (-4, 4.6, 5.6), "orange_terracotta", [("red_terracotta", 1)], rate=0.3, front=["........", ".mmmmmm.", "..m..m.."], K={"m": "black_concrete"})
    for sd in (1, -1):
        m.c("head", "orange_terracotta", (sd * 2, 9, 6.4), (0.8, 3, 0.8)); m.c("head", "black_concrete", (sd * 2, 11, 6.4), (1.6, 1.6, 1.6))
        m.c("head", "white_concrete", (sd * 2 + 0.3 * sd, 11.4, 7.1), (0.6, 0.6, 0.3))
    for sd, c in ((1, "clawL"), (-1, "clawR")):
        T(m, s, c, (4, 3, 5), (sd * 8 - 2, 4, 5), ("orange_terracotta", [("red_terracotta", 1)]), 0.4)
        T(m, s, c, (2, 2, 3), (sd * 8.5 - 1, 6.6, 8.4), ("orange_terracotta", []), 0.2)
    for leg, z in (("legFL", 3), ("legML", 0), ("legBL", -3)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            m.c(lg, "orange_terracotta", (sd * 8, 4.6, z), (4, 1.2, 1.2), (0, 0, -30 * sd)); m.c(lg, "red_terracotta", (sd * 10, 2, z), (1.2, 4, 1.2), (0, 0, 15 * sd))
    m.anims = idle("quad", {"clawL": {"rot": K((0, Z), (0.3, (-20, 0, 0)), (0.5, Z), (0.8, (-20, 0, 0)), (1.0, Z), (4.0, Z))},
                            "clawR": {"rot": K((0, Z), (2.0, Z), (2.3, (-20, 0, 0)), (2.5, Z), (4.0, Z))},
                            "legML": {"rot": sway(0, 10, 1.0)}, "legMR": {"rot": sway(0, 10, 1.0, 0.5)}, "neck": {"rot": K((0, Z), (4.0, Z))}})
    m.attacks = {"charge": "charge", "spikes": "rear"}
    m.melee = "bite"
    return m


@remake("puffneck")
def puffneck():
    """A puffed-up pigeon with a huge round chest of grey and violet-green sheen, a little head bobbing on its
    neck, orange eyes, a white cere over a dark beak, pink feet and wings that flick."""
    m = Model("puffneck", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.3
    G = ("light_gray_wool", [("gray_wool", 2), ("light_gray_concrete", 1)])
    bird_body = ("gray_wool", [("light_gray_wool", 2), ("cyan_terracotta", 1), ("purple_terracotta", 1)])
    bird_helper(m, s, bird_body, G, ("purple_terracotta", [("cyan_terracotta", 2), ("green_terracotta", 1)]), "black_terracotta", 3, "pink_terracotta")
    m.c("beak", "white_concrete", (0, 16.4, 7.4), (2, 0.8, 1.6))
    m.anims = idle("biped", {"neck": {"pos": K((0, Z), (0.25, (0, 0, 1.6)), (0.5, Z), (0.75, (0, 0, 1.6)), (1.0, Z))},
                             "armL": {"rot": K((0, Z), (2.0, Z), (2.1, (0, 0, 40)), (2.2, Z), (4.0, Z))}, "armR": {"rot": K((0, Z), (2.0, Z), (2.1, (0, 0, -40)), (2.2, Z), (4.0, Z))}}, 1.0)
    m.no_elbows = True
    m.attacks = {"levitate": "cast", "volley": "double"}
    m.melee = "swipe"
    return m


def bird_helper(m, s, body_pal, head_pal, belly, beak, neck_len, legs):
    m.bone("hips", "root", (0, 5, 0))
    m.mbone("legL", "hips", (2.2, 5, 0))
    m.bone("body", "hips", (0, 6, 0))
    m.bone("neck", "body", (0, 13, 1))
    m.bone("head", "neck", (0, 13 + neck_len, 1))
    m.mbone("armL", "body", (5.5, 13, 0))
    m.bone("beak", "head", (0, 14 + neck_len, 5))
    m.bone("tail", "body", (0, 8, -5))
    for sd, lg in ((1, "legL"), (-1, "legR")):
        m.c(lg, legs, (sd * 2.2, 3, 0), (1, 6, 1)); m.c(lg, legs, (sd * 2.2, 0.3, 1), (3, 0.6, 4))
    T(m, s, "body", (11, 10, 12), (-5.5, 5, -6), body_pal, 0.5)
    T(m, s, "body", (8, 7, 2), (-4, 6, 5.4), belly, 0.45)
    for sd, a in ((1, "armL"), (-1, "armR")):
        T(m, s, a, (1, 7, 9), (sd * 6 - 0.5, 6.5, -5), body_pal, 0.5)
    T(m, s, "tail", (7, 2, 5), (-3.5, 8, -10), body_pal, 0.5, rot=(-25, 0, 0), origin=(0, 8, -5))
    T(m, s, "neck", (6, neck_len + 1, 6), (-3, 14, -1.5), head_pal, 0.4)
    T(m, s, "head", (7, 6, 7), (-3.5, 13 + neck_len, -1.5), head_pal, 0.3, front=["sssssss", "skwsskw", "skksskk", "sssssss", "sssssss", "sssssss"],
      K={"s": head_pal[0], "k": "black_concrete", "w": "white_concrete"})
    tb(m, s, "beak", (3, 2, 3), (-1.5, 14 + neck_len, 5.4), beak, [], rate=0)


@remake("mallard")
def mallard():
    """Sir Mallard, a proud drake: a glossy green head with a white neck ring, a yellow bill, a chestnut
    breast, grey body with a blue wing patch, a curled black tail feather and orange webbed feet."""
    m = Model("mallard", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.3
    bird_helper(m, s, ("light_gray_wool", [("gray_wool", 2), ("light_gray_terracotta", 1)]), ("green_terracotta", [("green_concrete", 2), ("lime_terracotta", 1)]),
                ("brown_terracotta", [("terracotta", 2), ("brown_concrete", 1)]), "yellow_concrete", 2, "orange_concrete")
    m.c("neck", "white_concrete", (0, 15, 1.5), (6.4, 0.8, 6.4))
    for sd in (1, -1):
        m.c("armL" if sd == 1 else "armR", "blue_concrete", (sd * 6.3, 9, -1), (0.6, 2, 3))
    m.c("tail", "black_concrete", (0, 10.6, -10), (1, 3, 1), (-30, 0, 0))
    m.anims = idle("biped", {"neck": {"rot": sway(0, 10, 2.0)}, "tail": {"rot": sway(1, 20, 1.0)}}, 2.0)
    m.no_elbows = True
    m.attacks = {"minions": "roar", "charge": "lunge"}
    m.melee = "swipe"
    return m


@remake("piggy_farmer")
def piggy_farmer():
    """Farmer Trotter, a pig standing on his hind legs: pink snout with nostrils, floppy ears, a straw hat,
    blue dungarees over a white shirt, muddy trotters and a pitchfork."""
    m = Model("piggy_farmer", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    PK = ("pink_terracotta", [("pink_concrete", 2), ("white_terracotta", 1)])
    KK = fk("pink_terracotta", nose="pink_concrete", cheek="red_terracotta")
    neck, sh = kid(m, s, 6, (4, 6, 4), (11, 9, 8), (9, 8, 8), (4, 8, 4), ("blue_wool", [("blue_terracotta", 1)]), ("white_wool", [("light_gray_wool", 1), ("snow_block", 1)]),
                   PK, boots=("mud", [("brown_terracotta", 1)]), fc=dict(ey=2, gap=4, mouth=None, nose=0), K=KK, hand=("mud", []))
    tb(m, s, "head", (5, 4, 2), (-2.5, neck + 1, 4), "pink_concrete", [], rate=0, front=[".....", ".k.k.", ".....", "....."], K={"k": "red_terracotta"})
    for sd in (1, -1):
        m.c("head", "pink_terracotta", (sd * 4, neck + 7.6, 1), (3, 1, 3), (0, 0, -30 * sd))
    tb(m, s, "body", (9, 6, 1), (-4.5, 6, 4), "blue_wool", [("blue_terracotta", 1)], rate=0.3, front=["s.......s", "s.......s", ".........", ".........", ".........", "........."], K={"s": "gold_block"})
    T(m, s, "head", (14, 1, 14), (-7, neck + 8.4, -7), HAY, 0.4)
    T(m, s, "head", (8, 3, 8), (-4, neck + 9.2, -4), HAY, 0.4)
    m.bone("fork", "armR", (-7.5, 3, 0)); m.hold = {"fork": 10}
    m.c("fork", "spruce_planks", (-7.5, 7, 0), (1, 18, 1))
    for dx in (-1.5, 0, 1.5): m.c("fork", "iron_block", (-7.5 + dx, 17, 0), (0.6, 3, 0.6))
    m.c("fork", "iron_block", (-7.5, 15.6, 0), (3.6, 0.6, 0.6))
    m.bone("tail", "hips", (0, 6, -4))
    m.c("tail", "pink_concrete", (0, 7, -4.6), (1, 1, 1.4)); m.c("tail", "pink_concrete", (0, 8, -5.4), (1, 1.4, 1))
    base_idle(m, extra={"tail": {"rot": sway(1, 30, 0.8)}})
    m.attacks = {"minions": "roar", "charge": "lunge"}
    m.melee = "swipe"
    return m


@remake("ghost_jelly")
def ghost_jelly():
    """Jellyboo, a floating ghost jellyfish: a see-through violet bell with pale glowing spots and two
    sleepy eyes, a frilled rim, and long ribbon tentacles that ripple in waves under it."""
    m = Model("ghost_jelly", "float", 1.2)
    m.bone("core", "root", (0, 14, 0)); m.bone("head", "core", (0, 18, 0)); m.bone("ring1", "core", (0, 14, 0))
    m.bone("armL", "core", (3, 12, 0)); m.bone("armR", "core", (-3, 12, 0))
    s = Sheet(512, 256)
    s.rate = 1.6
    BELL = ("purple_stained_glass", [("magenta_stained_glass", 2), ("purple_terracotta", 1)])
    T(m, s, "head", (14, 8, 14), (-7, 15, -7), BELL, 0.4, front=["..............", "..............", "...kk....kk...", "..............", "......mm......", "..............",
      "..............", ".............."], K={"k": "black_concrete", "m": "black_concrete"})
    T(m, s, "head", (10, 3, 10), (-5, 23, -5), BELL, 0.4)
    for x, y, z in ((-4, 21, 7.2), (4, 20, 7.2), (0, 25.6, 3), (-5, 24, -3)):
        m.c("head", "white_stained_glass", (x, y, z), (1, 1, 0.4), light=True)
    for i in range(10):
        a = i * 36
        import math
        x, z = 6.2 * math.cos(math.radians(a)), 6.2 * math.sin(math.radians(a))
        m.c("head", "magenta_terracotta", (x, 14.6, z), (2, 1.2, 2))
    for k, (x, z) in enumerate(((-3, -3), (3, -3), (-3, 3), (3, 3), (0, 0))):
        b = "t%d" % k
        m.bone(b, "core", (x, 14, z)); m.bone(b + "b", b, (x, 9, z))
        T(m, s, b, (1, 5, 1), (x - 0.5, 9, z - 0.5), ("magenta_stained_glass", [("purple_stained_glass", 1)]), 0.5)
        T(m, s, b + "b", (1, 6, 1), (x - 0.5, 3, z - 0.5), ("pink_stained_glass", [("magenta_stained_glass", 1)]), 0.5)
    m.no_elbows = True
    tent = {}
    for k in range(5):
        tent["t%d" % k] = {"rot": sway(0, 14, 2.0, k * 0.15)}
        tent["t%db" % k] = {"rot": sway(0, 22, 2.0, k * 0.15 + 0.2)}
    tent["head"] = {"scl": K((0, (1, 1, 1)), (1.0, (1.08, 0.92, 1.08)), (2.0, (1, 1, 1)))}
    m.anims = idle("float", tent, 2.0)
    m.attacks = {"darkness": "pulse", "blink": "spin"}
    m.melee = "swipe"
    return m


@remake("baby_minotaur")
def baby_minotaur():
    """Little Moo, a baby minotaur: a brown furry bull head too big for his body with stubby cream horns, a
    pink muzzle with a gold nose ring, big shiny eyes, a fur kilt, hooves and a wooden toy club."""
    m = Model("baby_minotaur", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    KK = fk("brown_wool", brow="black_terracotta", nose="pink_terracotta")
    neck, sh = kid(m, s, 5, (3, 5, 3), (10, 8, 7), (11, 9, 9), (3, 7, 3), FUR_B, ("brown_terracotta", [("terracotta", 1)]), FUR_B,
                   boots=("black_terracotta", []), fc=dict(ey=2, gap=3, ew=2, eh=2, mouth=None), K=KK, hand=FUR_B)
    tb(m, s, "head", (7, 4, 2), (-3.5, neck, 4.5), "pink_terracotta", [("white_terracotta", 1)], rate=0.3, front=[".......", ".k...k.", ".......", "...m..."],
       K={"k": "brown_terracotta", "m": "black_terracotta"})
    m.c("head", "gold_block", (0, neck - 0.4, 6.6), (2.4, 1.6, 0.6))
    for sd in (1, -1):
        horn(m, "head", "white_terracotta", (sd * 5, neck + 7, 1), 2, (0, 0, -70 * sd), (0, 0, 40 * sd), 1.6, 0.8)
        m.c("head", "brown_wool", (sd * 6.2, neck + 5, 0), (2, 1.2, 2))
    T(m, s, "hips", (11, 3, 8), (-5.5, 3.6, -4), FUR_W, 0.4)
    m.bone("club", "armR", (-6.5, 2, 0)); m.hold = {"club": 30}
    m.c("club", "oak_log", (-6.5, 5, 0), (1.4, 8, 1.4)); T(m, s, "club", (3, 5, 3), (-8, 8, -1.5), ("oak_planks", [("stripped_oak_log", 1)]), 0.4)
    base_idle(m, extra={"head": {"rot": K((0, Z), (1.0, (6, 15, 6)), (2.0, Z), (3.0, (6, -15, -6)), (4.0, Z))}})
    m.attacks = {"charge": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@remake("mandrake")
def mandrake():
    """A mandrake root pulled from the ground screaming: a knobbly tan root body with root arms and legs,
    a wide-open screaming mouth and squeezed-shut eyes, and a big tuft of leaves for hair that shakes."""
    m = Model("mandrake", "biped", 1.2)
    s = Sheet(512, 256)
    s.rate = 1.25
    ROOT = ("white_terracotta", [("terracotta", 2), ("brown_terracotta", 1), ("birch_planks", 1)])
    KK = fk("white_terracotta", eye="brown_terracotta", brow="brown_terracotta", mouth="black_concrete")
    neck, sh = kid(m, s, 5, (2, 5, 2), (9, 8, 7), (9, 8, 8), (2, 7, 2), ROOT, ROOT, ROOT, fc=dict(ey=2, gap=3, ew=2, eh=1, mouth="o", mw=4, catch=False, brow=True), K=KK)
    m.bone("leaves", "head", (0, neck + 8, 0))
    for i, (x, z, rot) in enumerate(((0, 0, (0, 0, 0)), (-2.5, 0, (0, 0, 25)), (2.5, 0, (0, 0, -25)), (0, -2, (-25, 0, 0)), (0, 2, (25, 0, 0)), (-2, 2, (20, 0, 20)), (2, -2, (-20, 0, -20)))):
        T(m, s, "leaves", (3, 7, 1), (x - 1.5, neck + 8, z - 0.5), ("lime_terracotta", [("green_terracotta", 2), ("moss_block", 1)]), 0.5, rot=rot, origin=(x, neck + 8, z))
    for sd in (1, -1):
        m.c("body", "brown_terracotta", (sd * 3, 6, 3.6), (1, 2, 0.6)); m.c("legL" if sd == 1 else "legR", "brown_terracotta", (sd * 2.3, 0.3, 1.5), (1, 0.6, 2))
    base_idle(m, extra={"leaves": {"rot": K((0, Z), (0.1, (0, 0, 12)), (0.2, (0, 0, -12)), (0.3, Z), (2.0, Z), (2.1, (0, 0, 12)), (2.2, (0, 0, -12)), (2.3, Z), (4.0, Z))}})
    m.attacks = {"roar": "roar", "poison": "swipe"}
    m.melee = "swipe"
    return m


@remake("mossy_turtle")
def mossy_turtle():
    """Old Shellby, an old turtle with a high domed shell of brown plates overgrown with moss and a red
    flower, a wrinkly green head with sleepy eyes that pokes out and looks around, and thick scaly legs."""
    m = Model("mossy_turtle", "quad", 1.2)
    quad4(m, 6, 6, 5, -5, 7, 7, 9)
    s = Sheet(512, 256)
    s.rate = 1.25
    SK = ("lime_terracotta", [("green_terracotta", 2), ("moss_block", 1)])
    for leg, z in (("legFL", 5), ("legBL", -5)):
        for sd in (1, -1):
            lg = leg[:-1] + ("L" if sd == 1 else "R")
            T(m, s, lg, (4, 6, 4), (sd * 6 - 2, 0, z - 2), SK, 0.4)
    SH = ("brown_terracotta", [("spruce_planks", 2), ("terracotta", 1), ("brown_concrete", 1)])
    T(m, s, "body", (16, 6, 18), (-8, 4, -9), SH, 0.4, side=["kkkkkkkkkkkkkkkkkk", "..k.....k.....k...", "..k.....k.....k...", "..k.....k.....k...", "kkkkkkkkkkkkkkkkkk", ".................."],
      K={"k": "dark_oak_planks"})
    T(m, s, "body", (12, 3, 14), (-6, 10, -7), SH, 0.4)
    T(m, s, "body", (8, 2, 9), (-4, 13, -4.5), MOSS, 0.5)
    T(m, s, "body", (14, 1, 16), (-7, 9.6, -8), MOSS, 0.5)
    m.c("body", "green_terracotta", (2, 15.5, 1), (0.6, 2, 0.6)); m.c("body", "red_concrete", (2, 16.8, 1), (2, 0.8, 2))
    T(m, s, "neck", (5, 4, 4), (-2.5, 5, 7), SK, 0.4)
    T(m, s, "head", (7, 6, 6), (-3.5, 5, 10), SK, 0.3, front=["sssssss", "sssssss", "kks.skk"[:7], "sssssss", ".mmmmm.", "sssssss"],
      K={"s": "lime_terracotta", "k": "black_concrete", "m": "green_terracotta"})
    m.anims = idle("quad", {"neck": {"pos": K((0, Z), (1.0, (0, 0, 2)), (2.6, (0, 0, 2)), (3.4, Z), (4.0, Z))}})
    m.attacks = {"shockwave": "rear", "heal": "howl"}
    m.melee = "bite"
    return m


@remake("stumpy")
def stumpy():
    """Stumpy, what is left of the old oak: a short cut stump with tree rings on top, a cross face carved in
    the bark with glowing green eyes, a shelf mushroom on its side, little root feet and twig arms."""
    m = Model("stumpy", "biped", 1.2)
    biped(m, hip=3, legx=3, neck=16, shoulder=11, armx=7)
    s = Sheet(512, 256)
    s.rate = 1.7
    for sd, lg in ((1, "legL"), (-1, "legR")):
        T(m, s, lg, (3, 3, 4), (sd * 3 - 1.5, 0, -2), BARK, 0.4)
        m.c(lg, "spruce_log", (sd * 3, 0.5, 2.6), (2, 1, 2))
    T(m, s, "body", (12, 13, 12), (-6, 3, -6), BARK, 0.35, front=["............", "............", "..kkk..kkk..", "..kek..kek..", "..kkk..kkk..", "............", "............",
      "...mmmmmm...", "....m..m....", "............", "............", "............", "............"], K={"k": "black_concrete", "e": "lime_concrete", "m": "black_terracotta"}, lit=["lime_concrete"])
    tb(m, s, "head", (12, 1, 12), (-6, 16, -6), "stripped_oak_log", STUMP[1], rate=0.2, top=["............", ".oooooooooo.", ".o........o.", ".o.oooooo.o.", ".o.o....o.o.", ".o.o.oo.o.o.",
       ".o.o.oo.o.o.", ".o.o....o.o.", ".o.oooooo.o.", ".o........o.", ".oooooooooo.", "............"], K={"o": "oak_planks"})
    m.c("head", "brown_terracotta", (6.6, 10, 2), (2.4, 1, 4)); m.c("head", "brown_concrete", (6.4, 8, -1), (2, 0.8, 3))
    m.c("head", "moss_block", (-3, 17.2, 3), (4, 1, 3))
    for sd, a in ((1, "armL"), (-1, "armR")):
        m.c(a, "spruce_log", (sd * 7.5, 8, 0), (1.2, 6, 1.2), (0, 0, 20 * sd))
        m.c(a, "spruce_log", (sd * 9, 5.4, 0), (0.8, 2, 0.8), (0, 0, -20 * sd))
        m.c(a, "oak_leaves", (sd * 9, 11, 0), (2, 2, 2))
    base_idle(m, extra={"head": {"rot": K((0, Z), (4.0, Z))}})
    m.attacks = {"spikes": "slam", "heal": "roar"}
    m.melee = "swipe"
    return m
