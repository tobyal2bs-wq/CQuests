"""v9: the mini bosses from the user's pictures (refs 01-32). Small (about 2-3.5 blocks), 3000 health, they
wake on the mini timer. Every one is drawn on a Sheet with shaded edges and a proper face: eyes with a
light catch, brows, a mouth, cheeks, so they read at a distance. Original designs in the spirit of the refs."""
import math
from models import model, biped, quad, limb
from build import Model
from texpaint import paintbox, Sheet
from v2_recipes import S, fx, gone

SPAWN, DEATH = {}, {}
MINIS = []
INFO = {}   # id -> dict(name, title, entity, theme, bar, minion, extra abilities, colours)


def pb(m, s, bone, uv, lo, lit=(), **kw):
    kw.setdefault("passes", 0)
    return paintbox(m, bone, s.img, uv, lo, s.sizes[uv], allowed=sorted(s.used), lit=lit, **kw)


def bx(m, s, bone, size, lo, c, L=None, D=None, front=None, back=None, side=None, top=None, K=None, lit=(), rot=None, origin=None, edge=True):
    """A shaded box: lighter top face and top row, darker bottom row, optional pictures on its faces."""
    w, h, d = size
    uv = s.box(w, h, d, c, top=L or c, bottom=D or c)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(uv, f)
        if edge and L and fh > 2: s.rect(uv, f, 0, 0, fw, 1, L)
        if edge and D and fh > 2: s.rect(uv, f, 0, fh - 1, fw, 1, D)
    for f, rows in (("front", front), ("back", back), ("left", side), ("right", side), ("top", top)):
        if rows: s.draw(uv, f, 0, 0, rows, K)
    kw = {}
    if rot: kw = dict(rot=rot, origin=origin)
    pb(m, s, bone, uv, lo, lit=lit, **kw)
    return uv


def mini(id, name, title, entity="ZOMBIE", theme="nature", bar="GREEN", minion=None, extra=(), recipe=None):
    """Registers a mini: its yml entry and its opening and death."""
    def deco(fn):
        MINIS.append(id)
        INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, extra=list(extra))
        sp, de = recipe or generic()
        SPAWN[id], DEATH[id] = sp, de
        return model(fn)
    return deco


def generic(part="HAPPY_VILLAGER", sin="ENTITY_ZOMBIE_AMBIENT", sdie="ENTITY_ZOMBIE_DEATH", block="moss_block", pin=1.3, anim="roar", die="die_front"):
    sp = [S("shrink", 0, s=0), fx(0, "POOF", 30, "ENTITY_PLAYER_BURP", 0.5, y=0, spread=1.2, ring=2), S("pose", 4, 8, order="up", stagger=18),
          fx(14, part, 30, sin, pin, y=0.7, spread=0.8), S("anim", 26, 20, name=anim)]
    de = [S("flash", 0, 3), fx(0, sound=sdie, pitch=pin), S("anim", 0, 22, name=die), fx(14, part, 40, None, 1.0, y=0.4, spread=1.0),
          S("swap", 22, block=block, order="up", stagger=14), fx(36, "POOF", 20, "ENTITY_CHICKEN_EGG", 0.6, y=0.3), gone(40, 10)]
    return sp, de


def arms(m, s, size, y, x, c, L, D, hand=None, K=None, sleeve=None):
    w, h, d = size
    for side, arm in ((1, "armL"), (-1, "armR")):
        ax = side * x
        bx(m, s, arm, size, (ax - w / 2, y - h, -d / 2), c, L, D, K=K)
        if hand: bx(m, s, arm, (w, 2, d), (ax - w / 2, y - h - 1.6, -d / 2), hand, None, None)


def legs(m, s, size, x, c, L, D, boot=None, bh=2, K=None):
    w, h, d = size
    for side, leg in ((1, "legL"), (-1, "legR")):
        lx = side * x
        bx(m, s, leg, (w, h, d), (lx - w / 2, 0, -d / 2), c, L, D, K=K)
        if boot: bx(m, s, leg, (w, bh, d + 1), (lx - w / 2, -0.05, -d / 2), boot, None, None)


# ============================================================================================== batch 1
@mini("bark_ape", "<gradient:#5d3a1a:#c8a27a><bold>Bark Ape</bold></gradient>", "The Jungle Thief", entity="ZOMBIE", theme="nature", bar="YELLOW",
      extra=["leap", "volley"], recipe=generic("HAPPY_VILLAGER", "ENTITY_PANDA_AGGRESSIVE_AMBIENT", "ENTITY_PANDA_DEATH", "jungle_log"))
def bark_ape():
    """A cheeky brown ape with a pale face and big ears, long arms that drag its knuckles, and a curled tail."""
    m = Model("bark_ape", "biped", 1.5)
    biped(m, hip=7, legx=2.2, neck=17, shoulder=16, armx=6)
    m.bone("tail", "body", (0, 9, -3))
    B, BL, BD, F, FD, KK, W = "brown_terracotta", "terracotta", "brown_concrete", "white_terracotta", "pink_terracotta", "black_concrete", "white_concrete"
    K = {"b": B, "l": BL, "d": BD, "f": F, "p": FD, "k": KK, "w": W}
    s = Sheet(128, 128)
    legs(m, s, (3, 7, 3), 2.2, B, BL, BD)
    bx(m, s, "body", (8, 9, 5), (-4, 7, -2.5), B, BL, BD, front=["bbbbbbbb", "bbffffbb", "bfffffb.", "bffffffb", ".bffffb.", "..bffb..", "........"], K=K)
    arms(m, s, (3, 11, 3), 16, 5.5, B, BL, BD, hand=BD)
    bx(m, s, "head", (8, 7, 7), (-4, 16, -3.5), B, BL, BD, K=K, front=[
        "bbbbbbbb", "bddbbddb", "bfwkfwkb", "bffffffb", "bffppffb", "ffkffkff", ".ffffff."])
    bx(m, s, "head", (4, 2, 2), (-2, 16.6, 3.4), F, None, FD, front=["fkkf", "pppp"], K=K)
    for sd in (1, -1):
        bx(m, s, "head", (1, 3, 3), (sd * 4.6 - 0.5, 19, -1.5), F, None, FD, side=["ppp", "pfp", "ppp"], K=K)
    limb(m, "tail", B, (0, 9, -3), [(5, 1.4, (-130, 0, 0)), (4, 1.2, (-170, 0, 0)), (3, 1.0, (140, 0, 0))])
    m.attacks = {"leap": "lunge", "volley": "double", "slam": "slam"}
    m.melee = "swipe"
    return m


@mini("old_blindman", "<gradient:#8d6e63:#ffe0b2><bold>Old Blindman</bold></gradient>", "He Hears Every Step", entity="ZOMBIE", theme="bone", bar="WHITE",
      extra=["pull", "darkness"], recipe=generic("ASH", "ENTITY_VILLAGER_AMBIENT", "ENTITY_VILLAGER_DEATH", "white_wool", 0.6, "cast", "die_kneel"))
def old_blindman():
    """A bald old hermit with a huge white beard and milky eyes, a ragged brown robe, bare feet, and a
    crooked staff wrapped in a vine that he taps on the ground to find you."""
    m = Model("old_blindman", "biped", 1.5)
    biped(m, hip=7, legx=1.8, neck=17, shoulder=15.5, armx=5.5)
    m.bone("staff", "armR", (-5.5, 6, 2))
    m.hold = {"staff": 0}
    m.bend = -40
    SK, SL, SD, W, LG, R, RL, RD = "white_terracotta", "smooth_sandstone", "pink_terracotta", "white_concrete", "light_gray_concrete", "brown_terracotta", "terracotta", "brown_concrete"
    K = {"s": SK, "l": SL, "d": SD, "w": W, "g": LG, "r": R, "q": RL, "n": RD, "k": "black_concrete"}
    s = Sheet(128, 128)
    legs(m, s, (3, 7, 3), 1.8, SK, None, SD)
    bx(m, s, "body", (8, 9, 5), (-4, 6, -2.5), R, RL, RD, front=["rrrqrrrr", "rrrqrrrr", "rrrqrrrr", "nnnnnnnn", "rrrrqrrr", "rrrrqrrr", "rrrrqrrr", "rrrrqrrr", "nnnnnnnn"], K=K)
    arms(m, s, (3, 8, 3), 15.5, 5.5, R, RL, RD, hand=SK)
    bx(m, s, "head", (7, 7, 7), (-3.5, 15.5, -3.5), SK, SL, SD, K=K, front=[
        "lssssss", "sssssss", "wwssssw", "gwgssgw", "sssdsss", "swwwwws", "wwwwwww"],
        side=["lssssss", "sssssss", "wssssss", "wwsssss", "wwwssss", "wwwwsss", "wwwwwws"], back=["lllllll", "sssssss", "wsssssw", "wwssssw", "wwwwwww", "wwwwwww", "wwwwwww"])
    bx(m, s, "head", (7, 7, 2), (-3.5, 10, 3), W, None, LG, front=["wwwwwww", "wwgwwgw", "wwwwwww", "wgwwwgw", ".wwwww.", ".wwgww.", "..www.."], K=K)
    limb(m, "staff", "dark_oak_log", (-5.5, -1, 3), [(9, 1.2, (-8, 0, 0)), (9, 1.2, (6, 0, -6)), (4, 1.2, (40, 0, -30))])
    for y in (4, 8, 12):
        m.c("staff", "green_terracotta", (-5.5, y, 3.6), (1.5, 0.8, 1.5), (0, 45, 0))
    m.attacks = {"pull": "cast", "darkness": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


@mini("bog_orc", "<gradient:#2e7d32:#a5d6a7><bold>Bog Orc</bold></gradient>", "Bully of the Swamp", entity="ZOMBIE", theme="toxic", bar="GREEN",
      extra=["charge", "shockwave"], recipe=generic("ITEM_SLIME", "ENTITY_RAVAGER_AMBIENT", "ENTITY_RAVAGER_DEATH", "mud", 1.2))
def bog_orc():
    """A hunched green orc, all shoulders and fists, with a heavy brow, tusks poking up from a jutting jaw,
    a leather strap across its chest and torn brown trousers."""
    m = Model("bog_orc", "biped", 1.6)
    biped(m, hip=7, legx=2.6, neck=17, shoulder=16, armx=7)
    G, GL, GD, B, BD, W, KK, R = "green_terracotta", "lime_terracotta", "green_concrete", "brown_terracotta", "brown_concrete", "white_concrete", "black_concrete", "red_concrete"
    K = {"g": G, "l": GL, "d": GD, "b": B, "n": BD, "w": W, "k": KK, "r": R}
    s = Sheet(128, 128)
    legs(m, s, (4, 7, 4), 2.6, B, None, BD, boot=BD)
    bx(m, s, "body", (11, 10, 6), (-5.5, 7, -3), G, GL, GD, front=["gggggggggbb", "ggggggggbbg", "lllgggbbggg", "llllgbbgggg", "lllgbbggggg", "ggbbggggggg", "gbbgggggggg",
                                                                  "nnnnnnnnnnn", "bbbbbbbbbbb", "bbbbnbbbbbb"], K=K)
    bx(m, s, "body", (13, 3, 7), (-6.5, 15, -3.5), G, GL, GD)
    arms(m, s, (4, 11, 4), 17, 7.5, G, GL, GD, hand=GD)
    bx(m, s, "head", (7, 7, 6), (-3.5, 16.5, -1), G, GL, GD, K=K, front=[
        "lllllll", "ddddddd", "wkgggkw", "ggglggg", "ggggggg", "wgkkkgw", "wgggggw"])
    m.attacks = {"charge": "lunge", "slam": "slam", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@mini("king_oldbeard", "<gradient:#b71c1c:#ffd54f><bold>King Oldbeard</bold></gradient>", "Ruler of One Village", entity="VINDICATOR", theme="gold", bar="RED",
      minion="VILLAGER", extra=["minions", "orbs"], recipe=generic("WAX_ON", "ENTITY_VILLAGER_CELEBRATE", "ENTITY_VILLAGER_DEATH", "gold_block", 0.8, "cast", "die_back"))
def king_oldbeard():
    """An old villager king: the big villager nose, bushy white brows and a long white beard, a gold crown
    with red gems, a red robe trimmed with white fur and gold, and a gold sceptre topped with a sun."""
    m = Model("king_oldbeard", "biped", 1.6)
    biped(m, hip=6, legx=2, neck=17, shoulder=16, armx=6)
    m.bone("crown", "head", (0, 26, 0))
    m.bone("sceptre", "armR", (-6, 6, 2))
    m.hold = {"sceptre": 20}
    SK, SD, W, LG, R, RD, AU, AD, KK = "pink_terracotta", "brown_terracotta", "white_concrete", "light_gray_concrete", "red_concrete", "red_terracotta", "gold_block", "yellow_terracotta", "black_concrete"
    K = {"s": SK, "d": SD, "w": W, "g": LG, "r": R, "e": RD, "a": AU, "o": AD, "k": KK, "c": "green_concrete", "b": "light_blue_concrete"}
    s = Sheet(128, 128)
    legs(m, s, (3, 6, 3), 2, RD, None, None, boot=SD)
    bx(m, s, "body", (9, 10, 6), (-4.5, 6, -3), R, None, RD, front=["wwwwwwwww", "rrrwawrrr", "rrrwwwrrr", "rrrwawrrr", "aaaaaaaaa", "rrrwwwrrr", "rrrwawrrr", "rrrwwwrrr", "rrrwwwrrr", "wwwwwwwww"], K=K)
    bx(m, s, "body", (11, 2, 7), (-5.5, 15, -3.5), W, None, LG)
    arms(m, s, (3, 8, 3), 16, 6, R, None, RD, hand=SK)
    bx(m, s, "head", (8, 9, 8), (-4, 16.5, -4), SK, None, SD, K=K, front=[
        "gwwwwwwg", "wwwwwwww", "ssbkskbs", "ssssssss", "wwwssww w".replace(" ", "w")[:8], "wwwwwwww", "wwwwwwww", ".wwwwww.", "..wwww.."])
    bx(m, s, "head", (2, 4, 2), (-1, 18.6, 4), SK, None, SD)
    bx(m, s, "head", (6, 6, 2), (-3, 11.5, 2.8), W, None, LG, front=["wwwwww", "wgwwgw", "wwwwww", ".wwww.", ".wgww.", "..ww.."], K=K)
    bx(m, s, "crown", (9, 3, 9), (-4.5, 25.5, -4.5), AU, None, AD, front=["a.a.a.a.a"[:9], "aaaaaaaaa", "aaraabaaa"], back=["a.a.a.a.a", "aaaaaaaaa", "aaaacaaaa"], side=["a.a.a.a.a", "aaaaaaaaa", "aaaraaaaa"], K=K)
    for x, z in ((-4, -4), (4, -4), (-4, 4), (4, 4), (0, 4.3), (0, -4.3), (4.3, 0), (-4.3, 0)):
        m.c("crown", AU, (x * 0.95, 29.3, z * 0.95), (1.2, 1.4, 1.2))
    limb(m, "sceptre", AU, (-6, 1, 3), [(12, 1.0, (10, 0, 0))])
    m.c("sceptre", AU, (-6, 13.5, 5.2), (3, 3, 1), (10, 0, 0), light=True)
    for a in range(0, 360, 45):
        m.c("sceptre", AD, (-6 + 2.2 * math.cos(math.radians(a)), 13.5 + 2.2 * math.sin(math.radians(a)), 5.2), (0.8, 0.8, 0.8))
    m.attacks = {"minions": "cast", "orbs": "double", "slam": "slam"}
    m.melee = "swipe"
    return m


@mini("frost_yeti", "<gradient:#90caf9:#ffffff><bold>Frost Yeti</bold></gradient>", "Keeper of the Ice Cave", entity="ZOMBIE", theme="frost", bar="WHITE",
      extra=["frost", "shockwave"], recipe=generic("SNOWFLAKE", "ENTITY_POLAR_BEAR_WARNING", "ENTITY_POLAR_BEAR_DEATH", "packed_ice", 0.8))
def frost_yeti():
    """A shaggy white yeti with a blue-grey face, a wide fanged mouth, two short curved horns, frost
    tufts on its shoulders and a block of ice frozen to one fist."""
    m = Model("frost_yeti", "biped", 1.8)
    biped(m, hip=7, legx=3, neck=19, shoulder=17, armx=7.5)
    W, WL, WD, F, FD, KK, IC, HN = "white_concrete", "snow_block", "light_gray_concrete", "light_blue_terracotta", "cyan_terracotta", "black_concrete", "packed_ice", "white_terracotta"
    K = {"w": W, "l": WL, "d": WD, "f": F, "c": FD, "k": KK, "r": "red_concrete", "i": IC, "h": HN}
    s = Sheet(128, 128)
    legs(m, s, (4, 7, 4), 3, W, None, WD, boot=WD)
    bx(m, s, "body", (12, 12, 7), (-6, 7, -3.5), W, WL, WD, front=["llllllllllll", "wwwwwwwwwwww", "wwwwwwwwwwww", "wwwwwwwwwwww", "wwwwwwwwwwww", "wwwwwwwwwwww",
                                                                  "wwwwwwwwwwww", "wwwwwwwwwwww", "wwwwwwwwwwww", "wdwwdwwdwwdw", "dwdwdwdwdwdw", "dddddddddddd"], K=K)
    arms(m, s, (5, 12, 5), 18, 8, W, WL, WD, hand=F)
    bx(m, s, "armR", (6, 5, 6), (-11, 1.5, -3), IC, None, None)
    bx(m, s, "head", (9, 8, 7), (-4.5, 18, -2.5), W, WL, WD, K=K, front=[
        "wwwwwwwww", "wfffffffw", "wfwkfkwfw", "wfffffffw", "wckkkkkcw", "whkrrrkhw", "wfkkkkkfw", "wwwwwwwww"])
    for sd in (1, -1):
        limb(m, "head", HN, (sd * 3.5, 25.5, 1), [(3, 1.6, (0, 0, -40 * sd)), (3, 1.3, (0, 0, -5 * sd))])
        m.c("body", WL, (sd * 6.5, 19.4, 0), (4, 1.4, 6), (0, 0, -15 * sd))
    m.attacks = {"frost": "roar", "slam": "slam", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@mini("straw_farmer", "<gradient:#6d4c41:#ffe082><bold>Farmer Grimbly</bold></gradient>", "Illager of the Wheat Field", entity="VINDICATOR", theme="earth", bar="YELLOW",
      minion="VINDICATOR", extra=["minions", "volley"], recipe=generic("COMPOSTER", "ENTITY_VINDICATOR_AMBIENT", "ENTITY_VINDICATOR_DEATH", "hay_block", 1.0))
def straw_farmer():
    """A grumpy illager farmer: grey skin, the long illager nose and a heavy unibrow, a wide straw hat,
    brown dungarees over a pale shirt, and a pitchfork."""
    m = Model("straw_farmer", "biped", 1.6)
    biped(m, hip=6, legx=2, neck=17, shoulder=16, armx=6)
    m.bone("hat", "head", (0, 25, 0))
    m.bone("fork", "armR", (-6, 6, 2))
    m.hold = {"fork": 0}
    SK, SD, BR, BD, SH, SL, KK, HAT = "light_gray_concrete", "gray_concrete", "brown_terracotta", "brown_concrete", "white_terracotta", "white_concrete", "black_concrete", "bamboo_planks"
    K = {"s": SK, "d": SD, "b": BR, "n": BD, "h": SH, "w": SL, "k": KK, "y": HAT, "o": "yellow_terracotta", "g": "lime_concrete"}
    s = Sheet(128, 128)
    legs(m, s, (3, 6, 3), 2, BR, None, BD, boot=KK)
    bx(m, s, "body", (8, 10, 5), (-4, 6, -2.5), SH, None, None, front=["hbhhhhbh", "hbhhhhbh", "hbbbbbbh", "hbbobbbh", "hbbbbbbh", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "nnnnnnnn"], K=K)
    arms(m, s, (3, 8, 3), 16, 6, SH, None, None, hand=SK)
    bx(m, s, "head", (7, 9, 7), (-3.5, 16, -3.5), SK, None, SD, K=K, front=[
        "sssssss", "nnnnnnn", "swkswks", "sssssss", "sssssss", "sssssss", "sdddddd".replace("sdddddd", "ssdddss"), "sssssss", "sssssss"])
    bx(m, s, "head", (2, 4, 2), (-1, 15.5, 3.5), SK, None, SD)
    bx(m, s, "hat", (15, 1, 15), (-7.5, 24.5, -7.5), HAT, None, None, top=["o" * 15] + ["o" + "." * 13 + "o"] * 13 + ["o" * 15], K=K)
    bx(m, s, "hat", (8, 3, 8), (-4, 25.5, -4), HAT, None, None, front=["yyyyyyyy", "yyyyyyyy", "gggggggg"], back=["yyyyyyyy", "yyyyyyyy", "gggggggg"], side=["yyyyyyyy", "yyyyyyyy", "gggggggg"], K=K)
    limb(m, "fork", "stripped_spruce_log", (-6, -2, 3), [(16, 1.0, (0, 0, 0))])
    m.c("fork", "iron_block", (-6, 14.2, 3), (4, 0.6, 0.6))
    for x in (-1.6, 0, 1.6):
        m.c("fork", "iron_block", (-6 + x, 15.6, 3), (0.5, 3, 0.5))
    m.attacks = {"minions": "roar", "volley": "double", "charge": "lunge"}
    m.melee = "swipe"
    return m


@mini("gilded_mimic", "<gradient:#ff8f00:#fff176><bold>Gilded Mimic</bold></gradient>", "Too Shiny to Trust", entity="SLIME", theme="gold", bar="YELLOW",
      extra=["orbs", "leap"], recipe=generic("WAX_ON", "BLOCK_CHEST_OPEN", "BLOCK_CHEST_CLOSE", "gold_block", 0.7, "hop", "die_deflate"))
def gilded_mimic():
    """A golden treasure chest on stubby legs: a crown of gold studs on the lid, purple gems, a grin full
    of white teeth inside, and a long red tongue lolling out."""
    m = Model("gilded_mimic", "slime", 1.6)
    m.bone("body", "root", (0, 0, 0))
    m.bone("jaw", "body", (0, 6, -5))
    AU, AL, AD, P, W, R, KK = "gold_block", "yellow_concrete", "yellow_terracotta", "purple_concrete", "white_concrete", "red_concrete", "black_concrete"
    K = {"a": AU, "l": AL, "d": AD, "p": P, "w": W, "r": R, "k": KK, "m": "nether_wart_block"}
    s = Sheet(128, 128)
    bx(m, s, "body", (12, 6, 10), (-6, 1, -5), AU, AL, AD, front=["aaaaaaaaaaaa", "adaaaaaaaada", "aaaapppaaaaa", "aaaapppaaaaa", "adaaaaaaaada", "dddddddddddd"], K=K)
    bx(m, s, "body", (10, 1, 8), (-5, 6.9, -4), "nether_wart_block", None, None)
    bx(m, s, "jaw", (12, 5, 10), (-6, 7, -5), AU, AL, AD, front=["llllllllllll", "aaaaaaaaaaaa", "aaakaaaakaaa", "aaaaaaaaaaaa", "wawawawawawa"], K=K,
       top=["lllllllllll" + "l"] + ["laaaaaaaaaal"] * 8 + ["llllllllllll"])
    for x in (-4, 0, 4):
        m.c("jaw", P, (x, 12.4, 0), (1.6, 1.2, 1.6), light=True)
    for x in range(-5, 6, 2):
        m.c("body", W, (x, 7.4, 4.4), (1, 1.2, 0.8))
    limb(m, "body", R, (0, 7.2, 4), [(4, 2.4, (100, 0, 0)), (3, 2.2, (150, 0, 0))])
    for x, z in ((-4, -3), (4, -3), (-4, 3), (4, 3)):
        m.c("body", AD, (x, 0.5, z), (2.4, 1, 2.4))
    m.attacks = {"orbs": "spit", "leap": "hop", "slam": "slam"}
    m.melee = "hop"
    return m


@mini("plump_pigeon", "<gradient:#78909c:#80cbc4><bold>Sir Coo</bold></gradient>", "The Plump Pigeon", entity="ZOMBIE", theme="feather", bar="WHITE",
      minion="CHICKEN", extra=["minions", "dive"], recipe=generic("CLOUD", "ENTITY_PARROT_AMBIENT", "ENTITY_PARROT_DEATH", "light_gray_wool", 0.7))
def plump_pigeon():
    """A very round city pigeon: grey with a shining green and purple neck, an orange eye, pink feet, two
    dark bars on each wing and a small grey beak with a white cere."""
    m = Model("plump_pigeon", "biped", 1.6)
    biped(m, hip=4, legx=2, neck=11, shoulder=10, armx=5)
    G, GL, GD, NK, NP, PK, KK, OR, W = "light_gray_concrete", "light_gray_wool", "gray_concrete", "green_terracotta", "purple_terracotta", "pink_terracotta", "black_concrete", "orange_concrete", "white_concrete"
    K = {"g": G, "l": GL, "d": GD, "n": NK, "p": NP, "k": KK, "o": OR, "w": W}
    s = Sheet(128, 128)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, PK, (sd * 2, 2, 0), (0.8, 4, 0.8))
        m.c(leg, PK, (sd * 2, 0.3, 0.8), (2, 0.6, 2.4))
    bx(m, s, "body", (10, 8, 11), (-5, 4, -6), G, GL, GD, front=["nnnnnnnnnn", "pnpnpnpnpn", "gggggggggg", "gggggggggg", "gggggggggg", "gggggggggg", "gggggggggg", "dddddddddd"], K=K,
       top=["nnnnnnnnnn", "pnpnpnpnpn"] + ["gggggggggg"] * 9)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        bx(m, s, arm, (2, 6, 9), (sd * 5.4 - 1, 5, -5.5), G, GL, GD, side=["ggggggggg", "ggggggggg", "gkkggkkgg", "ggggggggg", "ggggggggg", "ddddddddd"], K=K)
    bx(m, s, "head", (6, 6, 6), (-3, 10.5, 0), G, GL, GD, K=K, front=["gggggg", "gggggg", "okgggo".replace("okgggo", "gkoko g".replace(" ", "")[:6]), "gggggg", "nnnnnn", "pnpnpn"],
       side=["gggggg", "gggggg", "ggokgg", "gggggg", "nnnnnn", "pnpnpn"])
    bx(m, s, "head", (2, 1, 2), (-1, 13, 5.8), GD, None, None)
    m.c("head", W, (0, 14, 6.2), (1.4, 0.6, 1))
    bx(m, s, "body", (6, 2, 5), (-3, 5, -10), GD, None, None)
    m.attacks = {"minions": "roar", "dive": "lunge"}
    m.melee = "swipe"
    return m


# ============================================================================================== batch 2
@mini("cinder_imp", "<gradient:#8b0000:#ff7043><bold>Cinder Imp</bold></gradient>", "Little Horned Trouble", entity="ZOMBIE", theme="fire", bar="RED",
      extra=["fire_ring", "leap"], recipe=generic("FLAME", "ENTITY_BLAZE_AMBIENT", "ENTITY_BLAZE_DEATH", "netherrack", 1.4))
def cinder_imp():
    """A small red demon with curved black horns, glowing yellow eyes, a wide fanged grin, dark bat wings
    and a thin tail ending in a spade."""
    m = Model("cinder_imp", "biped", 1.5)
    biped(m, hip=7, legx=2, neck=16, shoulder=15, armx=5.5)
    m.bone("wingL", "body", (2, 14, -2.5)); m.bone("wingR", "body", (-2, 14, -2.5))
    R, RL, RD, KK, Y, W, BH = "red_terracotta", "red_concrete", "brown_terracotta", "black_concrete", "yellow_concrete", "white_concrete", "blackstone"
    K = {"r": R, "l": RL, "d": RD, "k": KK, "y": Y, "w": W}
    s = Sheet(128, 128)
    legs(m, s, (3, 7, 3), 2, R, None, RD, boot=KK)
    bx(m, s, "body", (7, 9, 4), (-3.5, 7, -2), R, RL, RD, front=["rrrrrrr", "rlrrrlr", "rrdrdrr", "rrrrrrr", "rrrdrrr", "rrrrrrr", "rrrdrrr", "rrrrrrr", "ddddddd"], K=K)
    arms(m, s, (2, 8, 2), 15, 4.5, R, RL, RD, hand=KK)
    bx(m, s, "head", (7, 7, 6), (-3.5, 15.5, -3), R, RL, RD, K=K, front=["rrrrrrr", "kkrrrkk", "ryyrryy".replace("ryyrryy", "rykrykr"), "rrrrrrr", "rkkkkkr", "rkwkwkr", "rrrrrrr"], lit={Y})
    for sd in (1, -1):
        limb(m, "head", BH, (sd * 3, 22, 0), [(3, 1.4, (0, 0, -60 * sd)), (3, 1.1, (0, 0, -10 * sd)), (2, 0.8, (0, 0, 30 * sd))])
        wb = "wingL" if sd > 0 else "wingR"
        for k, (L, a) in enumerate(((9, 60), (8, 85), (7, 110))):
            limb(m, wb, BH, (sd * 2, 14, -2.5), [(L, 0.8, (0, 30 * sd, -a * sd))])
        m.c(wb, "black_terracotta", (sd * 6, 15, -3.2), (8, 6, 0.4), (0, 30 * sd, -10 * sd))
    m.bone("tail", "body", (0, 8, -2))
    limb(m, "tail", R, (0, 8, -2), [(5, 0.8, (-120, 0, 0)), (4, 0.8, (-160, 0, 0))])
    m.c("tail", KK, (0, 11.6, -10.6), (2, 2, 0.6), (0, 0, 45))
    m.attacks = {"fire_ring": "cast", "leap": "lunge"}
    m.melee = "swipe"
    return m


@mini("apple_crab", "<gradient:#c62828:#aed581><bold>Applecrab</bold></gradient>", "Orchard Pincher", entity="SPIDER", theme="nature", bar="RED",
      extra=["charge", "spikes"], recipe=generic("HAPPY_VILLAGER", "ENTITY_SPIDER_AMBIENT", "ENTITY_SPIDER_DEATH", "red_concrete", 1.4, "fang", "die_curl"))
def apple_crab():
    """A crab whose shell is a shiny red apple with a stalk and a green leaf, pale pink claws and legs,
    and two black stalk eyes peeking over the rim."""
    from models import mlimb
    m = Model("apple_crab", "spider", 1.6)
    m.bone("body", "root", (0, 4, 0)); m.bone("abdomen", "body", (0, 6, -3)); m.bone("head", "body", (0, 5, 4))
    m.bone("fangL", "head", (5, 4, 4)); m.bone("fangR", "head", (-5, 4, 4))
    R, RL, RD, P, PD, KK, G = "red_concrete", "red_wool", "red_terracotta", "pink_terracotta", "white_terracotta", "black_concrete", "lime_concrete"
    K = {"r": R, "l": RL, "d": RD, "p": P, "k": KK, "w": "white_concrete"}
    s = Sheet(128, 128)
    bx(m, s, "body", (12, 7, 11), (-6, 3, -5.5), R, RL, RD, front=["rrrrrrrrrrrr", "rwrrrrrrrrrr", "rrrrrrrrrrrr", "rrrrrrrrrrrr", "rrrrrrrrrrrr", "drrrrrrrrrrd", "dddddddddddd"],
       top=["rrrrrrrrrrrr", "rwwrrrrrrrrr", "rwrrrrrrrrrr", "rrrrrddrrrrr", "rrrrdddrrrrr", "rrrrrddrrrrr"] + ["rrrrrrrrrrrr"] * 5, K=K)
    m.c("body", "dark_oak_log", (0, 11, 0), (1, 2.6, 1), (0, 0, 10))
    m.c("body", G, (1.6, 12, 0), (3, 0.5, 2), (0, 20, -15))
    for sd in (1, -1):
        m.c("head", P, (sd * 2, 10.5, 5), (0.8, 3, 0.8))
        m.c("head", KK, (sd * 2, 12.4, 5), (1.6, 1.6, 1.6))
        m.c("head", "white_concrete", (sd * 2 + 0.3, 12.8, 5.7), (0.6, 0.6, 0.4))
    for sd, b in ((1, "fangL"), (-1, "fangR")):
        limb(m, b, P, (sd * 5, 5, 4), [(4, 1.6, (-70, 0, -30 * sd)), (3, 1.6, (-100, 0, 20 * sd))])
        m.c(b, P, (sd * 7.5, 5, 10), (3.4, 2.6, 3.6)); m.c(b, PD, (sd * 7.2, 5.6, 12.6), (1.4, 1, 2.4), (0, -15 * sd, 0)); m.c(b, PD, (sd * 7.8, 4.2, 12.4), (1.4, 0.8, 2.2), (0, 15 * sd, 0))
    zs = {1: 3, 2: 1, 3: -1, 4: -3}
    for i in (1, 2, 3, 4):
        m.bone(f"legL{i}", "body", (6, 5, zs[i])); m.bone(f"legR{i}", "body", (-6, 5, zs[i]))
        mlimb(m, f"legL{i}", P, (6, 5, zs[i]), [(4, 1, (20 - i * 10, 0, -50)), (5, 0.9, (10 - i * 5, 0, -160))])
    m.attacks = {"charge": "fang", "spikes": "fang"}
    m.melee = "fang"
    return m


@mini("pink_burrower", "<gradient:#f48fb1:#fce4ec><bold>The Pink Burrower</bold></gradient>", "It Came Up Through the Lawn", entity="SILVERFISH", theme="earth", bar="PINK",
      minion="SILVERFISH", extra=["minions", "quake"], recipe=generic("BLOCK", "ENTITY_SILVERFISH_AMBIENT", "ENTITY_SILVERFISH_DEATH", "pink_terracotta", 0.8, "howl", "die_collapse"))
def pink_burrower():
    """A long pink grub-worm with a blunt face, tiny black eyes, a little smile, soft ridges down its back
    and four stubby feet; it rears its head up when angry."""
    m = Model("pink_burrower", "quad", 2.3)
    quad(m, body_y=4, legx=3, legz_front=4, legz_back=-6, neck_y=6, neck_z=7)
    P, PL, PD, KK, W = "pink_terracotta", "pink_concrete", "magenta_terracotta", "black_concrete", "white_concrete"
    K = {"p": P, "l": PL, "d": PD, "k": KK, "w": W}
    s = Sheet(128, 128)
    for k, (z, w) in enumerate(((3, 7), (-1, 7), (-5, 6), (-9, 6), (-13, 5))):
        bone = "body" if k < 4 else "tail"
        bx(m, s, bone, (w, 6, 4), (-w / 2, 1, z - 2), P, PL, PD, top=["l" * w, "p" * w, "p" * w, "d" * w], K=K)
    bx(m, s, "head", (8, 7, 6), (-4, 2, 5), P, PL, PD, K=K, front=["pppppppp", "pppppppp", "pwkppwkp", "pppppppp", "pdpppppd".replace("pdpppppd", "pldppdlp"), "ppdddppp".replace("ppdddppp", "pppddppp"), "pppppppp"])
    for nm, x, z in (("legFL", 3, 4), ("legFR", -3, 4), ("legBL", 3, -6), ("legBR", -3, -6)):
        m.c(nm, PD, (x, 0.7, z), (2, 1.4, 2))
    m.attacks = {"minions": "howl", "quake": "rear", "charge": "charge"}
    m.melee = "bite"
    return m


@mini("moss_imp", "<gradient:#558b2f:#d7ccc8><bold>Moss Imp</bold></gradient>", "Small and Very Old", entity="ZOMBIE", theme="nature", bar="GREEN",
      extra=["levitate", "pull"], recipe=generic("HAPPY_VILLAGER", "ENTITY_ALLAY_AMBIENT_WITHOUT_ITEM", "ENTITY_ALLAY_DEATH", "moss_block", 1.2, "cast", "die_back"))
def moss_imp():
    """A tiny wrinkled green creature with enormous pointed ears, big dark eyes with a shine, a few white
    wisps of hair and a baggy tan robe with a rope belt. It lifts you with its mind."""
    m = Model("moss_imp", "biped", 1.3)
    biped(m, hip=4, legx=1.6, neck=12, shoulder=11, armx=4)
    G, GL, GD, T, TL, TD, KK, W = "lime_terracotta", "lime_concrete", "green_terracotta", "white_terracotta", "smooth_sandstone", "brown_terracotta", "black_concrete", "white_concrete"
    K = {"g": G, "l": GL, "d": GD, "t": T, "s": TL, "b": TD, "k": KK, "w": W}
    s = Sheet(128, 128)
    legs(m, s, (2, 4, 2), 1.6, T, None, TD)
    bx(m, s, "body", (7, 8, 6), (-3.5, 3, -3), T, TL, TD, front=["ttttttt", "tsttsts", "ttttttt", "bbbbbbb", "ttttttt", "tsttstt", "ttttttt", "bbbbbbb"], K=K)
    arms(m, s, (2, 6, 2), 11, 4.4, T, TL, TD, hand=G)
    bx(m, s, "head", (8, 7, 7), (-4, 11, -3.5), G, GL, GD, K=K, front=["gwgggwgg", "dddgdddg".replace("dddgdddg", "gdggggdg"), "kkwggkkw".replace("kkwggkkw", "gkwggkwg"), "gkkggkkg", "gggddggg", "gggggggg", "ggdddggg"])
    for sd in (1, -1):
        bx(m, s, "head", (7, 3, 1), (sd * 7 - 3.5, 14.5, -0.5), G, GL, GD, front=["gggggdd", "lggggdd", "gggg..."] if sd > 0 else ["ddggggg", "ddggggl", "...gggg"], K=K,
           rot=(0, 0, 15 * sd), origin=(sd * 4, 16, 0))
    m.attacks = {"levitate": "cast", "pull": "roar"}
    m.melee = "swipe"
    return m


@mini("garden_gnome", "<gradient:#2e7d32:#e53935><bold>Gnome Twins</bold></gradient>", "Do Not Kick the Gnome", entity="ZOMBIE", theme="earth", bar="GREEN",
      extra=["quake", "volley"], recipe=generic("COMPOSTER", "BLOCK_DECORATED_POT_HIT", "BLOCK_DECORATED_POT_SHATTER", "terracotta", 1.2))
def garden_gnome():
    """A garden gnome: a tall pointed green hat that flops over at the tip, a huge white beard, a round red
    nose, a blue tunic and brown boots; a little red-hatted twin rides on its shoulder."""
    m = Model("garden_gnome", "biped", 1.5)
    biped(m, hip=4, legx=1.8, neck=12, shoulder=11, armx=4.5)
    m.bone("hat", "head", (0, 18, 0))
    G, GD, R, RD, W, LG, SK, B, BD, BR = "green_concrete", "green_terracotta", "red_concrete", "red_terracotta", "white_concrete", "light_gray_concrete", "pink_terracotta", "blue_concrete", "blue_terracotta", "brown_concrete"
    K = {"g": G, "d": GD, "r": R, "e": RD, "w": W, "l": LG, "s": SK, "b": B, "n": BD, "o": BR, "k": "black_concrete"}
    s = Sheet(128, 128)
    legs(m, s, (3, 4, 3), 1.8, BD, None, None, boot=BR)
    bx(m, s, "body", (8, 8, 6), (-4, 4, -3), B, None, BD, front=["bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "oooooooo", "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "nnnnnnnn"], K=K)
    arms(m, s, (2, 6, 2), 11, 5, B, None, BD, hand=SK)
    bx(m, s, "head", (7, 6, 7), (-3.5, 11.5, -3.5), SK, None, None, K=K, front=["sssssss", "skssks s".replace(" ", "")[:7], "sssrsss", "wwwwwww", "wwwwwww", "wwwwwww"])
    bx(m, s, "head", (7, 6, 2), (-3.5, 6.5, 2.5), W, None, LG, front=["wwwwwww", "wlwwwlw", "wwwwwww", ".wwlww.", ".wwwww.", "..www.."], K=K)
    for k, (w, h, y, rx) in enumerate(((8, 3, 17, 0), (6, 3, 20, 8), (4, 3, 23, 20), (3, 3, 25.5, 50))):
        bx(m, s, "hat", (w, h, w), (-w / 2, y, -w / 2 - k * 0.6), G, None, GD, rot=(-rx, 0, 0) if rx else None, origin=(0, y, -k * 0.6))
    m.c("head", R, (0, 14.2, 3.9), (1.6, 1.6, 1.4))
    # the little twin on the shoulder
    m.c("body", SK, (5.5, 13.2, 0), (2.6, 2.4, 2.6)); m.c("body", W, (5.5, 12.2, 1.3), (2.6, 2, 0.8))
    m.c("body", R, (5.5, 15.2, 0), (3, 1.6, 3)); m.c("body", R, (5.5, 16.8, -0.3), (2, 1.6, 2)); m.c("body", RD, (5.5, 18, -0.8), (1.2, 1.2, 1.2))
    m.attacks = {"quake": "stomp", "volley": "double"}
    m.melee = "swipe"
    return m


@mini("angry_goose", "<gradient:#eceff1:#ff9800><bold>The Goose</bold></gradient>", "Peace Was Never an Option", entity="ZOMBIE", theme="feather", bar="WHITE",
      extra=["charge", "roar"], recipe=generic("CLOUD", "ENTITY_PARROT_IMITATE_RAVAGER", "ENTITY_CHICKEN_DEATH", "white_wool", 0.6))
def angry_goose():
    """A big white goose with a long neck, an orange beak and feet, beady black eyes under an angry brow,
    grey wingtips, and a honk that shakes the ground."""
    m = Model("angry_goose", "biped", 1.6)
    biped(m, hip=5, legx=2, neck=11, shoulder=10, armx=4.5)
    W, WL, WD, OR, OD, KK = "white_concrete", "snow_block", "light_gray_concrete", "orange_concrete", "orange_terracotta", "black_concrete"
    K = {"w": W, "l": WL, "d": WD, "o": OR, "e": OD, "k": KK, "g": "gray_concrete"}
    s = Sheet(128, 128)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, OR, (sd * 2, 2.5, 0), (1, 5, 1)); m.c(leg, OR, (sd * 2, 0.3, 1), (3, 0.6, 4))
    bx(m, s, "body", (9, 7, 12), (-4.5, 5, -7), W, WL, WD, K=K)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        bx(m, s, arm, (1, 5, 10), (sd * 4.8 - 0.5, 6, -6.5), W, WL, WD, side=["wwwwwwwwww"] * 3 + ["ddddwwwwww", "gggddwwwww"], K=K)
    m.c("body", WD, (0, 9, -8.5), (5, 3, 3), (30, 0, 0))
    limb(m, "head", W, (0, 10, 4), [(6, 3, (-10, 0, 0)), (4, 3, (10, 0, 0))])
    bx(m, s, "head", (4, 4, 6), (-2, 19, 1.5), W, WL, WD, K=K, side=["wwwwww", "wkkwww".replace("wkkwww", "wwwkkw"), "wwwkww".replace("wwwkww", "wwwwkw"), "wwwwww"],
       front=["wwww", "kwwk", "wwww", "wwww"])
    bx(m, s, "head", (2, 2, 4), (-1, 19.5, 7.5), OR, None, OD)
    m.c("head", KK, (0, 21.6, 7.4), (2, 0.6, 1), (0, 0, 0))
    m.attacks = {"charge": "lunge", "roar": "roar"}
    m.melee = "swipe"
    return m


@mini("pack_goblin", "<gradient:#33691e:#8d6e63><bold>Pack Goblin</bold></gradient>", "Carries Everything He Stole", entity="ZOMBIE", theme="earth", bar="GREEN",
      extra=["volley", "leap"], recipe=generic("CRIT", "ENTITY_PILLAGER_AMBIENT", "ENTITY_PILLAGER_DEATH", "oak_planks", 1.3))
def pack_goblin():
    """A hunched olive goblin in a patched brown tunic, long arms, pointy ears and yellow eyes, carrying a
    huge wooden backpack stacked with a chest, a bedroll and a lantern."""
    m = Model("pack_goblin", "biped", 1.7)
    biped(m, hip=6, legx=2, neck=15, shoulder=14, armx=5.5)
    G, GL, GD, BR, BL, BD, Y, KK, WD = "green_terracotta", "lime_terracotta", "green_concrete", "brown_terracotta", "terracotta", "brown_concrete", "yellow_concrete", "black_concrete", "spruce_planks"
    K = {"g": G, "l": GL, "d": GD, "b": BR, "t": BL, "n": BD, "y": Y, "k": KK}
    s = Sheet(128, 128)
    legs(m, s, (3, 6, 3), 2, BD, None, KK)
    bx(m, s, "body", (8, 9, 5), (-4, 6, -2.5), BR, BL, BD, front=["bbbbbbbb", "bbtbbbbb", "bbbbbbtb", "nnnnnnnn", "bbbbbbbb", "btbbbbbb", "bbbbtbbb", "bbbbbbbb", "nnnnnnnn"], K=K)
    arms(m, s, (2, 9, 2), 14, 5, G, GL, GD, hand=GD)
    bx(m, s, "head", (7, 6, 6), (-3.5, 14.5, -2), G, GL, GD, K=K, front=["lllllll", "ddggddg".replace("ddggddg", "gddgddg"), "gykgykg", "ggglggg", "gkkkkkg", "ggggggg"], lit={Y})
    for sd in (1, -1):
        bx(m, s, "head", (4, 2, 1), (sd * 5 - 2, 18, 0.5), G, None, GD, rot=(0, 0, 20 * sd), origin=(sd * 3.5, 19, 1))
    bx(m, s, "body", (8, 11, 5), (-4, 7, -8), WD, None, None)
    bx(m, s, "body", (7, 4, 5), (-3.5, 18, -8), "oak_planks", None, "spruce_planks")
    m.c("body", "red_wool", (0, 7, -10.2), (9, 3, 3))
    m.c("body", "iron_block", (4.6, 13, -10), (1.6, 2, 1.6)); m.c("body", "shroomlight", (4.6, 11.6, -10), (1.4, 1.4, 1.4), light=True)
    for x in (-3, 3):
        m.c("body", BD, (x, 13, 2.7), (1, 9, 0.5))
    m.attacks = {"volley": "double", "leap": "lunge"}
    m.melee = "swipe"
    return m


@mini("goblin_king", "<gradient:#558b2f:#ffd54f><bold>King Snivel</bold></gradient>", "Goblin King of the Ditch", entity="ZOMBIE", theme="gold", bar="GREEN",
      minion="ZOMBIE", extra=["minions", "charge"], recipe=generic("WAX_ON", "ENTITY_PIGLIN_ANGRY", "ENTITY_PIGLIN_DEATH", "gold_block", 1.3, "roar", "die_back"))
def goblin_king():
    """A pot-bellied goblin king: green with huge sideways ears, a grin of crooked teeth, a dented gold
    crown, a red cloak with a gold clasp and a gnawed bone for a sceptre."""
    m = Model("goblin_king", "biped", 1.6)
    biped(m, hip=5, legx=2.2, neck=14, shoulder=13, armx=5.5)
    m.bone("crown", "head", (0, 21, 0))
    G, GL, GD, R, RD, AU, AD, W, KK = "lime_terracotta", "lime_concrete", "green_terracotta", "red_concrete", "red_terracotta", "gold_block", "yellow_terracotta", "white_concrete", "black_concrete"
    K = {"g": G, "l": GL, "d": GD, "r": R, "e": RD, "a": AU, "o": AD, "w": W, "k": KK}
    s = Sheet(128, 128)
    legs(m, s, (3, 5, 3), 2.2, G, None, GD, boot=RD)
    bx(m, s, "body", (9, 9, 7), (-4.5, 5, -3.5), G, GL, GD, front=["rrggggggr".replace("rrggggggr", "raggggggr"), "rgggggggr", "rgglllggr", "rglllllgr", "rglllllgr", "rgglllggr", "rgggggggr", "eeeeeeeee", "rgggggggr"], K=K)
    bx(m, s, "body", (11, 10, 1), (-5.5, 4, -4.4), R, None, RD)
    arms(m, s, (2, 7, 2), 13, 5.5, G, GL, GD, hand=GD)
    bx(m, s, "head", (8, 7, 7), (-4, 13.5, -3.5), G, GL, GD, K=K, front=["llllllll", "gddggddg", "gkwggkwg", "gggllggg", "gggggggg", "gwkwwkwg", "ggkkkkgg"])
    for sd in (1, -1):
        bx(m, s, "head", (6, 3, 1), (sd * 6.5 - 3, 16.5, -0.5), G, GL, GD, rot=(0, 0, 10 * sd), origin=(sd * 4, 18, 0))
    bx(m, s, "crown", (8, 3, 8), (-4, 20.4, -4), AU, None, AD, front=["a.aa.a.a", "aaaaaaaa", "aaoaraoa"], back=["a.a.aa.a", "aaaaaaaa", "aaaaaaaa"], side=["a.a.aa.a", "aaaaaaaa", "aaaaraaa"], K=K,
       rot=(0, 0, 8), origin=(0, 21, 0))
    limb(m, "armR", "bone_block", (-5.5, 2, 2), [(8, 1.0, (20, 0, 0))])
    m.c("armR", "bone_block", (-5.5, 9.6, 4.6), (2.4, 1.6, 1.6))
    m.attacks = {"minions": "roar", "charge": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


def floater(m, core_y, arm_y, armx):
    m.bone("core", "root", (0, core_y, 0))
    m.bone("head", "core", (0, core_y + 4, 0))
    m.bone("armL", "core", (armx, arm_y, 0)); m.bone("armR", "core", (-armx, arm_y, 0))
    m.bone("ring1", "core", (0, core_y, 0))


# ============================================================================================== batch 3
@mini("sprout_sprite", "<gradient:#33691e:#ccff90><bold>Sprout Sprite</bold></gradient>", "A Seedling With a Grudge", entity="VEX", theme="nature", bar="GREEN",
      extra=["spikes", "heal"], recipe=generic("HAPPY_VILLAGER", "BLOCK_AZALEA_LEAVES_PLACE", "BLOCK_AZALEA_LEAVES_BREAK", "moss_block", 1.4, "raise", "die_drop"))
def sprout_sprite():
    """A floating green seed-pod spirit with a big sprouting leaf on a long stem, two leaf arms, round dark
    eyes and a tiny frown."""
    m = Model("sprout_sprite", "float", 1.6)
    floater(m, 6, 8, 4)
    G, GL, GD, KK, W = "lime_concrete", "lime_terracotta", "green_concrete", "black_concrete", "white_concrete"
    K = {"g": G, "l": GL, "d": GD, "k": KK, "w": W}
    s = Sheet(128, 128)
    bx(m, s, "head", (8, 7, 7), (-4, 4, -3.5), G, GL, GD, K=K, front=["gggggggg", "gggggggg", "gwkggwkg", "gkkggkkg", "gggggggg", "gggddggg", "dddddddd"])
    bx(m, s, "core", (5, 3, 5), (-2.5, 1.5, -2.5), GD, None, None)
    limb(m, "head", GD, (0, 11, 0), [(4, 1, (0, 0, 0)), (4, 1, (15, 0, 0)), (3, 1, (-10, 0, 0))])
    for a in (-35, 35):
        m.c("head", G, (math.sin(math.radians(a)) * 3, 21, 0.5), (5, 0.6, 3), (0, 0, -a))
    for sd, arm in ((1, "armL"), (-1, "armR")):
        m.c(arm, GL, (sd * 6, 7, 0), (5, 0.6, 2.6), (0, 0, 25 * sd))
    m.attacks = {"spikes": "raise", "heal": "pulse"}
    m.melee = "swipe"
    return m


@mini("cap_brothers", "<gradient:#b71c1c:#ffccbc><bold>Toadstool</bold></gradient>", "The Grumpier Mushroom", entity="ZOMBIE", theme="toxic", bar="RED",
      minion="SILVERFISH", extra=["poison", "minions"], recipe=generic("SPORE_BLOSSOM_AIR", "BLOCK_FUNGUS_PLACE", "BLOCK_FUNGUS_BREAK", "red_mushroom_block", 1.0))
def cap_brothers():
    """A stout walking mushroom with a wide red cap spotted white, a pale stalk body with a cross little
    face, stubby legs, and a smaller brown-capped brother clinging to its back."""
    m = Model("cap_brothers", "biped", 1.7)
    biped(m, hip=4, legx=2, neck=11, shoulder=10, armx=4.5)
    R, RL, RD, W, WL, WD, KK, B, BD = "red_concrete", "red_wool", "red_terracotta", "white_terracotta", "smooth_sandstone", "light_gray_terracotta", "black_concrete", "brown_terracotta", "brown_concrete"
    K = {"r": R, "l": RL, "d": RD, "w": "white_concrete", "s": W, "t": WL, "g": WD, "k": KK, "b": B, "n": BD, "p": "pink_terracotta"}
    s = Sheet(128, 128)
    legs(m, s, (3, 4, 3), 2, W, None, WD)
    bx(m, s, "body", (8, 7, 7), (-4, 4, -3.5), W, WL, WD)
    arms(m, s, (2, 5, 2), 10, 5, W, WL, WD)
    bx(m, s, "head", (8, 6, 7), (-4, 10.5, -3.5), W, WL, WD, K=K, front=["ssssssss", "skkssk ks".replace(" ", "")[:8], "swksswks", "ssssssss", "spsnnsps", "ssssssss"])
    cap = ["rrrrrrrrrrrrrr", "rwwrrrrrrrwwrr", "rwwrrrrrrrwwrr", "rrrrrwwrrrrrrr", "rrrrrwwrrrrrrr", "rrrrrrrrrrrrrr", "rwwrrrrrrwwrrr", "rwwrrrrrrwwrrr",
           "rrrrrrrrrrrrrr", "rrrrwwrrrrrrrr", "rrrrwwrrrrrwwr", "rrrrrrrrrrrwwr", "rrrrrrrrrrrrrr", "rrrrrrrrrrrrrr"]
    bx(m, s, "head", (14, 3, 14), (-7, 16, -7), R, RL, RD, top=cap, front=["rwwrrrrrrrwwrr", "rrrrrrrrrrrrrr", "dddddddddddddd"], back=["rrrrrwwrrrrrrr", "rrrrrrrrrrrrrr", "dddddddddddddd"],
       side=["rrrwwrrrrrrrrr", "rrrrrrrrrrrrrr", "dddddddddddddd"], K=K)
    bx(m, s, "head", (10, 2, 10), (-5, 19, -5), R, RL, RD, top=["rrrrrrrrrr", "rrwwrrrrrr", "rrwwrrrrrr", "rrrrrrrwwr", "rrrrrrrwwr", "rrrrrrrrrr", "rwwrrrrrrr", "rwwrrrrrrr", "rrrrrrrrrr", "rrrrrrrrrr"], K=K)
    # the little brother on its back
    m.c("body", W, (0, 8, -5), (3.4, 3.4, 2.4)); m.c("body", B, (0, 10.8, -5), (6, 1.6, 4)); m.c("body", "white_concrete", (1.6, 11.7, -4), (1, 0.3, 1))
    m.c("body", KK, (-0.7, 8.6, -6.25), (0.6, 0.8, 0.2)); m.c("body", KK, (0.7, 8.6, -6.25), (0.6, 0.8, 0.2))
    m.attacks = {"poison": "roar", "minions": "cast"}
    m.melee = "swipe"
    return m


@mini("puffneck", "<gradient:#7cb342:#f5f5f5><bold>Puffneck</bold></gradient>", "Blows Away in the Wind", entity="ZOMBIE", theme="wind", bar="WHITE",
      extra=["levitate", "volley"], recipe=generic("CLOUD", "ENTITY_BREEZE_IDLE_GROUND", "ENTITY_BREEZE_DEATH", "white_wool", 1.3, "cast", "die_back"))
def puffneck():
    """A tall stalk creature: a long green neck with leaves, a little yellow face with sleepy eyes and a
    round white dandelion clock for a head that sheds seeds when it is hit."""
    m = Model("puffneck", "biped", 1.6)
    biped(m, hip=4, legx=1.6, neck=14, shoulder=12, armx=3)
    G, GL, GD, Y, YD, W, WL, KK = "lime_concrete", "lime_terracotta", "green_concrete", "yellow_terracotta", "brown_terracotta", "white_concrete", "light_gray_concrete", "black_concrete"
    K = {"g": G, "l": GL, "d": GD, "y": Y, "o": YD, "w": W, "a": WL, "k": KK}
    s = Sheet(128, 128)
    legs(m, s, (2, 4, 2), 1.6, GD, None, None)
    bx(m, s, "body", (4, 10, 4), (-2, 4, -2), G, GL, GD)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        m.c(arm, GL, (sd * 4.6, 10, 0.5), (5, 0.6, 3), (0, 0, -30 * sd))
    limb(m, "head", G, (0, 14, 0), [(5, 2.2, (0, 0, 0)), (4, 2.2, (12, 0, 0))])
    bx(m, s, "head", (5, 4, 4), (-2.5, 21.5, 1), Y, None, YD, K=K, front=["yyyyy", "kkykk", "yyyyy", "yyoyy"])
    puff = ["awwwwwwwwa", "wwwwawwwww", "wwwwwwwaww", "wawwwwwwww", "wwwwwwwwww", "wwwwawwwww", "wwwwwwwwaw", "wwawwwwwww", "wwwwwwwwww", "awwwwwwwwa"]
    bx(m, s, "head", (10, 10, 10), (-5, 25, -3), W, None, WL, front=puff, back=puff, side=puff, top=puff, K=K)
    for x, y, z in ((5.6, 31, 0), (-5.6, 29, 3), (0, 35.6, 2), (2, 30, 7.6), (-3, 33, -3.6)):
        m.c("head", W, (x, y, z), (0.8, 0.8, 0.8))
    m.attacks = {"levitate": "cast", "volley": "double"}
    m.melee = "swipe"
    return m


@mini("mallard", "<gradient:#1b5e20:#ffeb3b><bold>Sir Mallard</bold></gradient>", "Crosses Any Road", entity="ZOMBIE", theme="water", bar="GREEN",
      minion="CHICKEN", extra=["minions", "charge"], recipe=generic("SPLASH", "ENTITY_PARROT_AMBIENT", "ENTITY_CHICKEN_DEATH", "white_wool", 0.8))
def mallard():
    """A chunky mallard drake: a glossy green head, a broad yellow bill, a white collar ring, a chestnut
    breast, a grey body, a curl of black tail and orange feet."""
    m = Model("mallard", "biped", 1.8)
    biped(m, hip=4, legx=2, neck=10, shoulder=9, armx=4.5)
    G, GL, GD, Y, YD, W, CH, GR, KK, OR = "green_concrete", "lime_concrete", "green_terracotta", "yellow_concrete", "yellow_terracotta", "white_concrete", "brown_terracotta", "light_gray_concrete", "black_concrete", "orange_concrete"
    K = {"g": G, "l": GL, "d": GD, "y": Y, "o": YD, "w": W, "c": CH, "a": GR, "k": KK, "e": "gray_concrete"}
    s = Sheet(128, 128)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, OR, (sd * 2, 2, 0), (1, 4, 1)); m.c(leg, OR, (sd * 2, 0.3, 1), (3, 0.6, 3))
    bx(m, s, "body", (8, 6, 10), (-4, 4, -5), GR, None, "gray_concrete", front=["wwwwwwww", "cccccccc", "cccccccc", "cccccccc", "aaaaaaaa", "eeeeeeee"], K=K)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        bx(m, s, arm, (1, 4, 8), (sd * 4.3 - 0.5, 5.5, -4.5), "white_terracotta", None, "gray_concrete", side=["oooooooo".replace("o", "a"), "aaaaabbb".replace("b", "l"), "aaaaaaaa", "eeeeeeee"], K=K)
    bx(m, s, "head", (6, 6, 6), (-3, 10, -1), G, GL, GD, K=K, front=["lggggggl"[:6], "gggggg", "wkggkw".replace("wkggkw", "kwggkw"), "gggggg", "gggggg", "wwwwww"],
       side=["gggggg", "gggggg", "ggkwgg", "gggggg", "gggggg", "wwwwww"])
    bx(m, s, "head", (6, 2, 4), (-3, 11, 5), Y, None, YD, K=K, top=["yyyyyy", "yyyyyy", "yyyyyy", "oyyyyo"])
    m.c("body", KK, (0, 9.2, -6), (2, 2, 1.4), (-30, 0, 0))
    m.attacks = {"minions": "roar", "charge": "lunge"}
    m.melee = "swipe"
    return m


@mini("piggy_farmer", "<gradient:#f48fb1:#ffe082><bold>Farmer Trotter</bold></gradient>", "Owns the Mud Patch", entity="ZOMBIE", theme="earth", bar="PINK",
      minion="PIG", extra=["minions", "charge"], recipe=generic("CRIT", "ENTITY_PIG_AMBIENT", "ENTITY_PIG_DEATH", "mud", 0.7))
def piggy_farmer():
    """A pink pig standing up in blue dungarees and a check shirt, a straw hat pushed back, a big snout,
    small black eyes and floppy ears, and a muddy shovel."""
    m = Model("piggy_farmer", "biped", 1.5)
    biped(m, hip=5, legx=2, neck=13, shoulder=12, armx=5)
    m.bone("hat", "head", (0, 20, 0))
    P, PL, PD, B, BD, R, KK, HAT = "pink_terracotta", "pink_concrete", "magenta_terracotta", "blue_concrete", "blue_terracotta", "red_concrete", "black_concrete", "bamboo_planks"
    K = {"p": P, "l": PL, "d": PD, "b": B, "n": BD, "r": R, "w": "white_concrete", "k": KK, "y": HAT, "o": "yellow_terracotta"}
    s = Sheet(128, 128)
    legs(m, s, (3, 5, 3), 2, B, None, BD, boot=KK)
    bx(m, s, "body", (8, 8, 5), (-4, 5, -2.5), R, None, None, front=["rwrwrwrw", "wbrwrwbr".replace("wbrwrwbr", "rbwrwrbw"), "rbbbbbbw", "rbbobbbw".replace("rbbobbbw", "wbbobbbr"), "bbbbbbbb", "bbbbbbbb", "bbbbbbbb", "nnnnnnnn"], K=K)
    arms(m, s, (2, 6, 2), 12, 5, R, None, None, hand=P)
    bx(m, s, "head", (8, 7, 7), (-4, 12.5, -3.5), P, PL, PD, K=K, front=["pppppppp", "pppppppp", "pkppppkp", "pppppppp", "ppddddpp".replace("ppddddpp", "pplllpp p".replace(" ", "")[:8]), "pppppppp", "pppppppp"])
    bx(m, s, "head", (4, 3, 2), (-2, 13.5, 3.4), PL, None, PD, front=["llll", "dlld", "llll"], K=K)
    for sd in (1, -1):
        bx(m, s, "head", (3, 3, 1), (sd * 4 - 1.5, 17.5, 0), P, None, PD, rot=(30, 0, 30 * sd), origin=(sd * 4, 19, 0))
    bx(m, s, "hat", (12, 1, 12), (-6, 19.2, -6), HAT, None, None, top=["o" * 12] + ["o" + "." * 10 + "o"] * 10 + ["o" * 12], K=K, rot=(-12, 0, 0), origin=(0, 20, 0))
    bx(m, s, "hat", (7, 3, 7), (-3.5, 20, -3.8), HAT, None, None, rot=(-12, 0, 0), origin=(0, 20, 0))
    limb(m, "armR", "stripped_spruce_log", (-5, 1, 2), [(10, 0.8, (15, 0, 0))])
    m.c("armR", "iron_block", (-5, 11, 4.8), (2.4, 3, 0.6), (15, 0, 0))
    m.attacks = {"minions": "roar", "charge": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


@mini("ring_frog", "<gradient:#558b2f:#ffeb3b><bold>Floaty Frog</bold></gradient>", "Pool Party Crasher", entity="SLIME", theme="water", bar="GREEN",
      extra=["leap", "volley"], recipe=generic("SPLASH", "ENTITY_FROG_AMBIENT", "ENTITY_FROG_DEATH", "lime_wool", 1.0, "hop", "die_deflate"))
def ring_frog():
    """A fat green frog sitting in a yellow rubber-duck swim ring, a pink flower behind one eye, a wide
    content smile, and a tiny turtle friend riding on its head."""
    m = Model("ring_frog", "slime", 1.8)
    m.bone("body", "root", (0, 0, 0)); m.bone("mouth", "body", (0, 6, 4)); m.bone("inner", "body", (0, 4, 0))
    G, GL, GD, Y, YD, OR, KK, PK = "lime_terracotta", "lime_concrete", "green_terracotta", "yellow_concrete", "yellow_terracotta", "orange_concrete", "black_concrete", "pink_concrete"
    K = {"g": G, "l": GL, "d": GD, "y": Y, "o": YD, "r": OR, "k": KK, "p": PK, "w": "white_concrete"}
    s = Sheet(128, 128)
    bx(m, s, "body", (10, 8, 9), (-5, 0, -4.5), G, GL, GD, K=K, front=["gggggggggg", "wkgggggwkg", "kkggggggkk", "gggggggggg", "gdgggggggd".replace("gdgggggggd", "ggdddddddg"), "gggggggggg", "llllllllll", "llllllllll"])
    for sd in (1, -1):
        bx(m, s, "body", (3, 3, 3), (sd * 3 - 1.5, 7.5, 1), G, GL, GD, front=["ggg", "wkg" if sd < 0 else "gwk", "ggg"], K=K)
    ring = s.box(14, 3, 13, Y, top=Y)
    s.draw(ring, "front", 0, 0, ["yyyyyyyyyyyyyy", "yyyyyyyyyyyyyy", "oooooooooooooo"], K)
    pb(m, s, "body", ring, (-7, 1, -6.5))
    bx(m, s, "body", (4, 4, 4), (-2, 2, 6), Y, None, YD, K=K, front=["yyyy", "kyyk", "rrrr", "yyyy"])
    m.c("body", PK, (4.6, 11, 1), (2, 2, 0.6)); m.c("body", Y, (4.6, 11, 1.3), (0.6, 0.6, 0.4))
    m.c("body", "green_concrete", (0, 9.4, -1), (3, 1.2, 3)); m.c("body", "brown_terracotta", (0, 10.4, -1), (2.4, 1, 2.4))
    m.attacks = {"leap": "hop", "volley": "spit"}
    m.melee = "hop"
    return m


@mini("ghost_jelly", "<gradient:#7e57c2:#e1f5fe><bold>Jellyboo</bold></gradient>", "The Floating Fright", entity="VEX", theme="void", bar="PURPLE",
      extra=["darkness", "blink"], recipe=generic("END_ROD", "ENTITY_ALLAY_AMBIENT_WITH_ITEM", "ENTITY_ALLAY_DEATH", "purple_stained_glass", 1.4, "pulse", "die_drop"))
def ghost_jelly():
    """A floating jelly ghost: a soft lilac-to-white dome with two big round eyes and a little open mouth,
    long wavy ribbon tentacles trailing under it, glowing faintly."""
    m = Model("ghost_jelly", "float", 1.7)
    floater(m, 8, 9, 3)
    P, PL, W, LB, KK = "purple_concrete", "purple_wool", "white_concrete", "light_blue_concrete", "black_concrete"
    K = {"p": "magenta_terracotta", "v": PL, "w": W, "b": LB, "k": KK, "l": "light_blue_terracotta", "c": "white_terracotta"}
    s = Sheet(128, 128)
    top = ["vvvvvvvvvv"] * 10
    bx(m, s, "head", (10, 7, 9), (-5, 9, -4.5), "lilac_x" if False else "light_blue_terracotta", None, None, K=K, top=top,
       front=["vvvvvvvvvv", "vvvvvvvvvv", "llllllllll", "lwwklwwkll".replace("lwwklwwkll", "lwkllwkll l".replace(" ", "")[:10]), "lkklllkkll".replace("lkklllkkll", "lkkllkkl l".replace(" ", "")[:10]), "llllkkllll", "cccccccccc"])
    bx(m, s, "head", (8, 2, 7), (-4, 16, -3.5), PL, None, None)
    for k, x in enumerate((-4, -1.5, 1.5, 4)):
        limb(m, "core", W if k % 2 else LB, (x, 9, 0), [(3, 0.8, (0, 0, 180 + 20)), (3, 0.8, (0, 0, 180 - 20)), (3, 0.8, (0, 0, 180 + 20))], light=True)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        limb(m, arm, W, (sd * 4, 9, 2), [(4, 0.8, (30, 0, -150 * sd)), (3, 0.8, (60, 0, -120 * sd))], light=True)
    m.attacks = {"darkness": "pulse", "blink": "spin"}
    m.melee = "swipe"
    return m


@mini("hay_golem", "<gradient:#f9a825:#8d6e63><bold>Hay Golem</bold></gradient>", "The Scarecrow Walks", entity="IRON_GOLEM", theme="earth", bar="YELLOW",
      extra=["fire_ring", "slam"], recipe=generic("COMPOSTER", "BLOCK_GRASS_BREAK", "ENTITY_IRON_GOLEM_DEATH", "hay_block", 0.7))
def hay_golem():
    """A golem of bound hay bales: a straw head with a stitched burlap face and button eyes, red twine
    bands round the chest and limbs, straw poking out everywhere and a crown of wheat."""
    m = Model("hay_golem", "biped", 1.7)
    biped(m, hip=7, legx=2.6, neck=18, shoulder=17, armx=7)
    H, HL, HD, R, RD, KK, BU = "bamboo_planks", "yellow_concrete", "yellow_terracotta", "red_concrete", "red_terracotta", "black_concrete", "white_terracotta"
    K = {"h": H, "l": HL, "d": HD, "r": R, "e": RD, "k": KK, "b": BU}
    s = Sheet(128, 128)
    legs(m, s, (4, 7, 4), 2.6, H, None, HD)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, R, (sd * 2.6, 4, 0), (4.4, 1, 4.4))
    bx(m, s, "body", (11, 11, 7), (-5.5, 7, -3.5), H, None, HD, front=["hhhhhhhhhhh", "hhhhhhhhhhh", "rrrrrrrrrrr", "hhhhhhhhhhh", "hhhhhhhhhhh", "hhhhhhhhhhh", "hhhhhhhhhhh", "rrrrrrrrrrr", "hhhhhhhhhhh", "hhhhhhhhhhh", "ddddddddddd"],
       side=["hhhhhhh", "hhhhhhh", "rrrrrrr", "hhhhhhh", "hhhhhhh", "hhhhhhh", "hhhhhhh", "rrrrrrr", "hhhhhhh", "hhhhhhh", "ddddddd"], back=["hhhhhhhhhhh", "hhhhhhhhhhh", "rrrrrrrrrrr", "hhhhhhhhhhh", "hhhhhhhhhhh", "hhhhhhhhhhh", "hhhhhhhhhhh", "rrrrrrrrrrr", "hhhhhhhhhhh", "hhhhhhhhhhh", "ddddddddddd"], K=K)
    arms(m, s, (4, 10, 4), 17, 7.5, H, None, HD, hand=HD)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        m.c(arm, R, (sd * 7.5, 10, 0), (4.4, 1, 4.4))
    bx(m, s, "head", (8, 8, 7), (-4, 17.5, -3.5), H, None, HD, K=K, front=["hhhhhhhh", "hbbbbbbh", "hbkbbkbh", "hbbbbbbh", "hbbbbbbh", "hbkekekh".replace("hbkekekh", "hbekekbh"), "hbbbbbbh", "hhhhhhhh"])
    for k in range(7):
        a = k * 2 * math.pi / 7
        m.c("head", HD, (3 * math.cos(a), 27, 2.6 * math.sin(a)), (0.6, 3, 0.6), (math.degrees(math.sin(a)) * 0.3, 0, -math.degrees(math.cos(a)) * 0.3))
    for x, y, z in ((5.6, 14, 2), (-5.8, 10, -1), (6, 9, -2), (-5.6, 15, 3)):
        m.c("body", HL, (x, y, z), (2.4, 0.4, 0.4), (0, 0, 20))
    m.attacks = {"slam": "slam", "fire_ring": "stomp"}
    m.melee = "swipe"
    return m


# ============================================================================================== batch 4
@mini("fisher_duck", "<gradient:#fbc02d:#4fc3f7><bold>Captain Quackers</bold></gradient>", "Has Caught Bigger Things Than You", entity="ZOMBIE", theme="water", bar="YELLOW",
      extra=["pull", "volley"], recipe=generic("SPLASH", "ENTITY_FISHING_BOBBER_SPLASH", "ENTITY_CHICKEN_DEATH", "yellow_wool", 1.0))
def fisher_duck():
    """A round yellow duckling in a green bucket hat, an orange bill, a smug half-lidded look and a fishing
    rod with a red-and-white bobber; it reels players in."""
    m = Model("fisher_duck", "biped", 1.7)
    biped(m, hip=3, legx=1.8, neck=11, shoulder=9, armx=4.5)
    m.bone("rod", "armR", (-4.5, 6, 2))
    m.hold = {"rod": 30}
    Y, YL, YD, OR, OD, G, GD, KK = "yellow_concrete", "yellow_wool", "yellow_terracotta", "orange_concrete", "orange_terracotta", "lime_terracotta", "green_terracotta", "black_concrete"
    K = {"y": Y, "l": YL, "d": YD, "o": OR, "e": OD, "g": G, "n": GD, "k": KK, "w": "white_concrete"}
    s = Sheet(128, 128)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        m.c(leg, OR, (sd * 1.8, 1.5, 0), (1, 3, 1)); m.c(leg, OR, (sd * 1.8, 0.3, 1), (2.6, 0.6, 3))
    bx(m, s, "body", (8, 7, 8), (-4, 3, -4), Y, YL, YD)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        bx(m, s, arm, (1, 4, 5), (sd * 4.3 - 0.5, 4.5, -2.5), Y, YL, YD)
    bx(m, s, "head", (7, 6, 6), (-3.5, 9.5, -3), Y, YL, YD, K=K, front=["yyyyyyy", "ddydddy".replace("ddydddy", "yddyddy"), "ykkykky".replace("ykkykky", "ywkywky"), "yyyyyyy", "yyyyyyy", "yyyyyyy"])
    bx(m, s, "head", (5, 2, 3), (-2.5, 10.5, 3), OR, None, OD)
    bx(m, s, "head", (10, 1, 10), (-5, 15.2, -5), G, None, GD)
    bx(m, s, "head", (7, 3, 7), (-3.5, 15.6, -3.5), G, None, GD, front=["ggggggg", "ggggggg", "nnnnnnn"], back=["ggggggg", "ggggggg", "nnnnnnn"], side=["ggggggg", "ggggggg", "nnnnnnn"], K=K)
    limb(m, "rod", "stripped_spruce_log", (-4.5, 3, 3), [(8, 0.6, (40, 0, 0)), (8, 0.5, (60, 0, 0))])
    m.c("rod", "light_gray_concrete", (-4.5, 11.5, 15.5), (0.2, 6, 0.2))
    m.c("rod", "red_concrete", (-4.5, 8.4, 15.5), (1.4, 0.8, 1.4)); m.c("rod", "white_concrete", (-4.5, 7.6, 15.5), (1.4, 0.8, 1.4))
    m.attacks = {"pull": "cast", "volley": "double"}
    m.melee = "swipe"
    return m


@mini("baby_minotaur", "<gradient:#4e342e:#ffccbc><bold>Little Moo</bold></gradient>", "Baby of the Labyrinth", entity="ZOMBIE", theme="earth", bar="RED",
      extra=["charge", "shockwave"], recipe=generic("CRIT", "ENTITY_COW_AMBIENT", "ENTITY_COW_DEATH", "brown_wool", 1.4, "roar", "die_front"))
def baby_minotaur():
    """A chubby little minotaur: a big brown bull head with white curved horns, a pink muzzle with a gold
    nose ring, a shaggy fringe, and a tiny body in a leather kilt; small but it charges hard."""
    m = Model("baby_minotaur", "biped", 1.6)
    biped(m, hip=4, legx=2, neck=11, shoulder=10, armx=5)
    B, BL, BD, P, PD, W, AU, KK = "brown_terracotta", "terracotta", "brown_concrete", "pink_terracotta", "magenta_terracotta", "white_concrete", "gold_block", "black_concrete"
    K = {"b": B, "l": BL, "d": BD, "p": P, "m": PD, "w": W, "a": AU, "k": KK}
    s = Sheet(128, 128)
    legs(m, s, (3, 4, 3), 2, B, None, BD, boot=KK)
    bx(m, s, "body", (8, 7, 5), (-4, 4, -2.5), B, BL, BD, front=["bbbbbbbb", "bblbblbb", "bbbbbbbb", "dddddddd", "dbdbdbdb", "dbdbdbdb", "dddddddd"], K=K)
    arms(m, s, (2, 6, 2), 10.5, 5, B, BL, BD, hand=BD)
    bx(m, s, "head", (10, 8, 8), (-5, 10.5, -4), B, BL, BD, K=K, front=["dddddddddd", "dbdddddbdd", "bbbbbbbbbb", "bwkbbbbwkb", "bbbbbbbbbb", "bbbbbbbbbb", "bbbbbbbbbb", "bbbbbbbbbb"])
    bx(m, s, "head", (6, 4, 3), (-3, 10.5, 3.6), P, None, PD, front=["pppppp", "pmppmp", "pppppp", "pppppp"], K=K)
    m.c("head", AU, (0, 11.4, 6.8), (2.4, 2.4, 0.5))
    for sd in (1, -1):
        limb(m, "head", W, (sd * 5, 16, 0), [(3, 1.6, (0, 0, -80 * sd)), (3, 1.3, (0, 0, -20 * sd)), (2, 1.0, (0, 0, 20 * sd))])
        m.c("head", B, (sd * 6, 15, -1), (2, 1, 3), (0, 0, -30 * sd))
    m.attacks = {"charge": "lunge", "stomp": "stomp"}
    m.melee = "swipe"
    return m


@mini("boo_twins", "<gradient:#eceff1:#90a4ae><bold>The Boo Twins</bold></gradient>", "Two Sheets to the Wind", entity="VEX", theme="soul", bar="WHITE",
      extra=["blink", "darkness"], recipe=generic("SOUL", "ENTITY_VEX_AMBIENT", "ENTITY_VEX_DEATH", "white_wool", 1.2, "spin", "die_drop"))
def boo_twins():
    """Two little bedsheet ghosts holding hands, one taller with round black eyes, one smaller with oval
    eyes and a wobbly mouth; their sheets ripple at the hem."""
    m = Model("boo_twins", "float", 1.6)
    floater(m, 2, 9, 4)
    W, WL, WD, KK = "white_concrete", "snow_block", "light_gray_concrete", "black_concrete"
    K = {"w": W, "l": WL, "d": WD, "k": KK}
    s = Sheet(128, 128)
    bx(m, s, "head", (7, 13, 7), (-7, 2, -3.5), W, WL, WD, K=K, front=["wwwwwww", "wwwwwww", "wwwwwww", "wkkwkkw", "wkkwkkw", "wwwwwww", "wwwkwww", "wwwwwww", "wwwwwww", "wwwwwww", "wwwwwww", "wdwwdww", "d.dd.dd"])
    bx(m, s, "head", (6, 10, 6), (2, 2, -3), W, WL, WD, K=K, front=["wwwwww", "wwwwww", "wkwwkw", "wkwwkw", "wwwwww", "wkwkww".replace("wkwkww", "wwkkww"), "wwwwww", "wwwwww", "wdwwdw", ".d.dd."])
    m.c("head", W, (-0.5, 7, 0), (4, 1.4, 1.4))
    m.attacks = {"blink": "spin", "darkness": "pulse"}
    m.melee = "swipe"
    return m


@mini("mandrake", "<gradient:#a1887f:#c5e1a5><bold>Mandrake</bold></gradient>", "Do Not Pull It Up", entity="ZOMBIE", theme="nature", bar="GREEN",
      extra=["roar", "poison"], recipe=generic("HAPPY_VILLAGER", "ENTITY_GHAST_SCREAM", "ENTITY_GHAST_DEATH", "rooted_dirt", 1.8))
def mandrake():
    """A pale knobbly root with a scrunched little face, stubby root arms and legs and a big tuft of leaves
    on its head. Its scream hurts."""
    m = Model("mandrake", "biped", 1.5)
    biped(m, hip=3, legx=1.4, neck=10, shoulder=9, armx=3.5)
    T, TL, TD, G, GL, KK = "white_terracotta", "smooth_sandstone", "light_gray_terracotta", "lime_concrete", "lime_terracotta", "black_concrete"
    K = {"t": T, "l": TL, "d": TD, "k": KK, "p": "pink_terracotta"}
    s = Sheet(128, 128)
    legs(m, s, (2, 3, 2), 1.4, T, None, TD)
    bx(m, s, "body", (6, 7, 5), (-3, 3, -2.5), T, TL, TD, front=["tttttt", "tttttt", "tdtttt", "tttttt", "tttdtt", "tttttt", "dddddd"], K=K)
    arms(m, s, (1, 5, 1), 9, 3.6, T, None, TD)
    bx(m, s, "head", (6, 5, 5), (-3, 9.5, -2.5), T, TL, TD, K=K, front=["tttttt", "tkttkt", "ptttpt".replace("ptttpt", "pttttp"), "ttkktt", "tttttt"])
    for k, (a, L) in enumerate(((-30, 7), (-10, 9), (10, 8), (30, 6), (0, 10))):
        limb(m, "head", G if k % 2 else GL, (0, 14.5, 0), [(L * 0.5, 1.2, (k * 8 - 16, 0, a)), (L * 0.5, 1.0, (k * 12 - 24, 0, a * 1.6))])
    m.attacks = {"roar": "roar", "poison": "cast"}
    m.melee = "swipe"
    return m


@mini("mossy_turtle", "<gradient:#2e7d32:#8d6e63><bold>Old Shellby</bold></gradient>", "Slow, Stubborn, Armoured", entity="ZOMBIE", theme="water", bar="GREEN",
      extra=["shockwave", "heal"], recipe=generic("SPLASH", "ENTITY_TURTLE_AMBIENT_LAND", "ENTITY_TURTLE_DEATH", "moss_block", 0.8, "howl", "die_side"))
def mossy_turtle():
    """A stocky turtle with a tall brown shell ringed in plates, moss and a little flower on top, a bright
    green head with sleepy eyes and a beak, and chunky green legs."""
    m = Model("mossy_turtle", "quad", 1.8)
    quad(m, body_y=4, legx=4, legz_front=4, legz_back=-4, neck_y=5, neck_z=7)
    G, GL, GD, B, BL, BD, KK, MS = "lime_concrete", "lime_terracotta", "green_concrete", "brown_terracotta", "terracotta", "brown_concrete", "black_concrete", "moss_block"
    K = {"g": G, "l": GL, "d": GD, "b": B, "t": BL, "n": BD, "k": KK, "w": "white_concrete"}
    s = Sheet(128, 128)
    shell = ["bbbbbbbbbbbb", "btttbbbtttbb", "btbtbbbtbtbb", "btttbbbtttbb", "bbbbnnnbbbbb", "nnnnbbbnnnnn"]
    bx(m, s, "body", (12, 6, 13), (-6, 2, -6.5), B, BL, BD, front=shell, back=shell, side=["bbbbbbbbbbbbb", "btttbbbtttbbb", "btbtbbbtbtbbb", "btttbbbtttbbb", "bbbbnnnbbbbbb", "nnnnnnnnnnnnn"], K=K)
    bx(m, s, "body", (8, 2, 9), (-4, 8, -4.5), B, BL, BD)
    m.c("body", MS, (0, 10.3, 0), (6, 0.6, 6)); m.c("body", "pink_concrete", (1.5, 11, 1), (1, 1, 1))
    bx(m, s, "head", (5, 4, 5), (-2.5, 3, 6), G, GL, GD, K=K, front=["ggggg", "kgggk", "ggggg", "gdddg"], side=["ggggg", "ggggk", "ggggg", "ddddd"])
    for nm, x, z in (("legFL", 4, 4), ("legFR", -4, 4), ("legBL", 4, -4), ("legBR", -4, -4)):
        bx(m, s, nm, (3, 3, 3), (x - 1.5, 0, z - 1.5), G, GL, GD)
    m.attacks = {"shockwave": "rear", "heal": "howl", "charge": "charge"}
    m.melee = "bite"
    return m


@mini("stumpy", "<gradient:#5d4037:#aed581><bold>Stumpy</bold></gradient>", "What's Left of the Old Oak", entity="ZOMBIE", theme="nature", bar="GREEN",
      extra=["spikes", "heal"], recipe=generic("HAPPY_VILLAGER", "BLOCK_WOOD_HIT", "BLOCK_WOOD_BREAK", "oak_log", 0.7, "roar", "die_back"))
def stumpy():
    """A walking tree stump: rough bark with deep grooves, two big white eyes with dark pupils carved into
    the trunk, a sapling growing out of its flat top, stubby root feet and twiggy arms."""
    m = Model("stumpy", "biped", 1.7)
    biped(m, hip=3, legx=2.4, neck=12, shoulder=10, armx=5)
    B, BL, BD, W, KK, G = "brown_terracotta", "terracotta", "brown_concrete", "white_concrete", "black_concrete", "lime_concrete"
    K = {"b": B, "l": BL, "d": BD, "w": W, "k": KK}
    s = Sheet(128, 128)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        bx(m, s, leg, (3, 3, 4), (sd * 2.4 - 1.5, 0, -2), BD, None, None)
    bark = ["bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "dddddddddd"]
    bx(m, s, "body", (10, 11, 9), (-5, 3, -4.5), B, BL, BD, K=K, front=["bdbbdbbdbb", "bdbbdbbdbb", "bwwwbbwwwb", "bwkwbbwkwb", "bwwwbbwwwb", "bdbbdbbdbb", "bbdddddbbb", "bdbbdbbdbb", "bdbbdbbdbb", "bdbbdbbdbb", "dddddddddd"],
       back=bark, side=[r[:9] for r in bark], top=["llllllllll", "lddddddddl", "ldllllllll", "ldldddddll", "ldldlllldl", "ldldllddll", "ldllllllll", "lddddddddl", "llllllllll"])
    m.c("body", "oak_log", (0, 15, 0), (1, 3, 1)); m.c("body", G, (0, 17.2, 0), (3, 1.4, 3)); m.c("body", G, (0, 18.4, 0), (2, 1, 2))
    for sd, arm in ((1, "armL"), (-1, "armR")):
        limb(m, arm, BD, (sd * 5, 10, 0), [(4, 1, (0, 0, -120 * sd)), (3, 0.8, (0, 0, -160 * sd))])
        m.c(arm, G, (sd * 8.6, 8, 0), (1.6, 1.6, 1.6))
    m.attacks = {"spikes": "slam", "heal": "roar"}
    m.melee = "swipe"
    return m
