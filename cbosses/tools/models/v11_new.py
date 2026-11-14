"""v11: chapter 4-10 bosses and ten mini bosses rebuilt from the user's second set of pictures.
Every surface is textured: a base block with its own grain (concrete powder, wool, terracotta, moss, stone)
mottled with a second and third tone in chunky cells, so the pixel look of the pictures survives at block
scale. 150 to 300 blocks each, faces with eyes, brows, teeth and highlights, and idles that breathe, look
around, bob and sway so they never stand still like statues."""
import math
import random
import zlib
from models import model, biped, limb
from build import Model
from texpaint import Sheet
from v2_recipes import S, fx, gone
from v9_minis import pb
import v9_minis
import anims
from anims import K, Z

SPAWN, DEATH = {}, {}
CHAPTER_INFO = {}

# ------------------------------------------------------------------------------------------------ helpers


def mottle(s, uv, faces, tones, seed, rate=0.22, cell=2):
    """Chunky colour patches: tones = [(block, weight)]. cell is the patch size in texture pixels."""
    rnd = random.Random(seed)
    tot = sum(w for _, w in tones)
    for f in faces:
        fu, fv, fw, fh = s.face(uv, f)
        for y in range(0, fh, cell):
            for x in range(0, fw, cell):
                if rnd.random() > rate: continue
                r = rnd.random() * tot
                for b, w in tones:
                    r -= w
                    if r <= 0: break
                cw, ch = min(cell + rnd.choice((0, 0, 1)), fw - x), min(cell, fh - y)
                for j in range(ch):
                    for i in range(cw):
                        s.put(fu + x + i, fv + y + j, b)


def tb(m, s, bone, size, lo, c, tones=(), rate=0.22, cell=2, L=None, D=None, front=None, back=None, side=None, top=None, K=None,
       lit=(), rot=None, origin=None, seed=None, faces=("front", "back", "left", "right", "top")):
    """A textured, shaded box: base c, mottled with tones, lighter top row (L), darker bottom row (D), and
    pictures on its faces drawn last so features stay crisp."""
    w, h, d = size = tuple(max(1, int(round(v))) for v in size)
    uv = s.box(w, h, d, c, top=L or c, bottom=D or c)
    if tones:
        mottle(s, uv, faces, tones, seed if seed is not None else zlib.crc32(repr((bone, size, lo, c)).encode()), rate, cell)
    for f in ("front", "back", "left", "right"):
        fu, fv, fw, fh = s.face(uv, f)
        if L and fh > 3: s.rect(uv, f, 0, 0, fw, 1, L)
        if D and fh > 3: s.rect(uv, f, 0, fh - 1, fw, 1, D)
    for f, rows in (("front", front), ("back", back), ("left", side), ("right", side), ("top", top)):
        if rows: s.draw(uv, f, 0, 0, rows, K)
    kw = dict(rot=rot, origin=origin) if rot else {}
    pb(m, s, bone, uv, lo, lit=lit, **kw)
    return uv


def legs2(m, s, size, x, c, tones, L=None, D=None, boot=None, boot_tones=(), K=None, front=None, toe=1.2):
    """Two legs with a flat boot that sticks out forward, so the feet sit flat under the body."""
    w, h, d = size
    for side, leg in ((1, "legL"), (-1, "legR")):
        lx = side * x
        tb(m, s, leg, (w, h, d), (lx - w / 2, 1.6, -d / 2), c, tones, L=L, D=D, K=K, front=front)
        if boot:
            tb(m, s, leg, (w + 1, 2, d + 2), (lx - (w + 1) / 2, 0, -d / 2 - 0.4 + toe - 1.2), boot, boot_tones, rate=0.3, D=None)


def arms2(m, s, size, y, x, c, tones, L=None, D=None, hand=None, hand_tones=(), K=None, front=None, hand_size=None):
    w, h, d = size
    for side, arm in ((1, "armL"), (-1, "armR")):
        ax = side * x
        tb(m, s, arm, size, (ax - w / 2, y - h, -d / 2), c, tones, L=L, D=D, K=K, front=front)
        if hand:
            hw, hh, hd = hand_size or (w + 0.6, 3, d + 0.6)
            tb(m, s, arm, (hw, hh, hd), (ax - hw / 2, y - h - hh + 0.4, -hd / 2), hand, hand_tones, rate=0.3)


def boss_recipe(part, sin, sdie, block, pin=0.9, anim="roar", die="die_front", ground="BLOCK", ground_block="MOSS_BLOCK"):
    sp = [S("shrink", 0, s=0), fx(0, ground, 90, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0, spread=2.6, ring=3, block=ground_block),
          S("pose", 2, 14, order="up", stagger=26), fx(18, part, 60, sin, pin, y=1.0, spread=1.4), S("anim", 34, 26, name=anim),
          fx(40, "EXPLOSION", 2, "ENTITY_RAVAGER_ROAR", 0.7, y=1.2)]
    de = [S("flash", 0, 4), fx(0, sound=sdie, pitch=pin), S("anim", 0, 30, name=die), fx(16, part, 80, None, 1.0, y=0.8, spread=1.6),
          S("swap", 30, block=block, order="up", stagger=16), fx(46, "POOF", 40, "BLOCK_GRAVEL_BREAK", 0.6, y=0.4, spread=1.4), gone(50, 14)]
    return sp, de


def chapter(id, name, title, entity, theme, bar, minion=None, extra=(), recipe=None, items=(), money=0):
    def deco(fn):
        CHAPTER_INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, extra=list(extra),
                                items=list(items), money=money)
        SPAWN[id], DEATH[id] = recipe
        return model(fn)
    return deco


def remini(old, id, name, title, entity="ZOMBIE", theme="nature", bar="GREEN", minion=None, extra=(), recipe=None, movement=None):
    """Replace a v9 mini (old id) with a rebuilt one, keeping its place in the mini list."""
    def deco(fn):
        i = v9_minis.MINIS.index(old)
        v9_minis.MINIS[i] = id
        v9_minis.INFO.pop(old, None)
        v9_minis.INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, extra=list(extra),
                                 **({"movement": movement} if movement else {}))
        sp, de = recipe or v9_minis.generic()
        v9_minis.SPAWN[id], v9_minis.DEATH[id] = sp, de
        return model(fn)
    return deco


def breathe(bone, amt=0.03, length=3.0):
    return {bone: {"scl": K((0, (1, 1, 1)), (length / 2, (1 + amt, 1 + amt / 2, 1 + amt)), (length, (1, 1, 1)))}}


GREEN = [("green_terracotta", 3), ("lime_terracotta", 2), ("green_concrete", 1)]
MOSSY = [("moss_block", 3), ("green_terracotta", 2), ("lime_terracotta", 1)]
STONE = [("andesite", 3), ("cobblestone", 2), ("tuff", 2), ("gray_concrete", 1)]
BARK = [("brown_terracotta", 3), ("dark_oak_planks", 1), ("terracotta", 2)]
LEATHER = [("brown_terracotta", 3), ("brown_concrete", 2), ("terracotta", 1)]


# ======================================================================================== chapter bosses


@chapter("gnome_brothers", "<gradient:#2e7d32:#ffcdd2><bold>The Gnome Brothers</bold></gradient>", "Bramble and Thimble", "ZOMBIE", "nature", "GREEN",
         minion="SILVERFISH", extra=["minions", "leap"], items=["EMERALD 12", "GOLD_INGOT 12", "DIAMOND 1"], money=22000,
         recipe=boss_recipe("HAPPY_VILLAGER", "ENTITY_VILLAGER_YES", "ENTITY_VILLAGER_DEATH", "moss_block", 1.4, "roar", "die_back"))
def gnome_brothers():
    """Picture 1: a big gnome in a tall green bent hat with a checked white beard, a peach nose and a
    red coat, and his little brother in a taller red hat standing at his hip. Both hats sway and the
    little one bobs on his own."""
    m = Model("gnome_brothers", "biped", 2.2)
    biped(m, hip=6, legx=2.2, neck=16, shoulder=15, armx=5.6)
    m.bone("hat1", "head", (0, 25, 0))
    m.bone("hat2", "hat1", (0.4, 30, -0.6))
    m.bone("hat3", "hat2", (1, 34, -1.6))
    m.bone("little", "root", (8.5, 0, -3))
    m.bone("lhead", "little", (8.5, 8, -3))
    m.bone("lhat1", "lhead", (8.5, 13, -3))
    m.bone("lhat2", "lhat1", (8.5, 18, -3))
    s = Sheet(256, 256)
    G, GL, GD = "green_concrete", "lime_terracotta", "green_terracotta"
    R, RL, RD = "red_terracotta", "red_concrete", "brown_terracotta"
    W, WG, WD = "white_wool", "light_gray_wool", "light_gray_terracotta"
    P, PD = "pink_terracotta", "terracotta"
    K_ = {"w": W, "g": WG, "d": WD, "p": P, "q": PD, "k": "black_concrete", "e": "white_concrete", "r": R, "o": "brown_concrete", "b": "brown_terracotta"}
    checker = lambda wdt, hgt, off=0: ["".join("g" if (x // 2 + y // 2 + off) % 2 else "w" for x in range(wdt)) for y in range(hgt)]
    # legs in brown trousers, dark boots
    legs2(m, s, (3, 5, 3), 2.2, "brown_terracotta", LEATHER, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    # red coat body with a belt, the beard hangs over it
    tb(m, s, "body", (9, 9, 6), (-4.5, 6.5, -3), R, [("red_concrete", 2), ("brown_terracotta", 1)], rate=0.2, D=RD,
       front=[".........", ".........", ".........", ".........", ".........", "ooooooooo", "ooooyoooo", "........."], K=dict(K_, y="gold_block"))
    # the beard: a checked white curtain from the cheeks to the belly
    tb(m, s, "head", (9, 9, 2), (-4.5, 9, 2.6), W, (), front=checker(9, 9), side=checker(2, 9, 1), K=K_)
    tb(m, s, "head", (7, 3, 1), (-3.5, 7.2, 3.4), W, (), front=[".gwgwg.", "..wgw..", "...g..."], K=K_)
    arms2(m, s, (3, 6, 3), 15, 6, R, [("red_concrete", 1)], hand=P, hand_tones=[(PD, 1)])
    # head: peach face mostly hidden under the hat and beard, a big nose, little dark eyes
    tb(m, s, "head", (8, 6, 7), (-4, 16, -3.5), P, [(PD, 1)], rate=0.12,
       front=["pppppppp", "pkepekep"[:8], "pppppppp", "pppppppp", "wwwwwwww", "wwwwwwww"], K=K_)
    tb(m, s, "head", (3, 3, 2), (-1.5, 16.6, 3.4), P, [(PD, 1), ("pink_concrete", 1)], rate=0.3)
    for sd in (1, -1):
        tb(m, s, "head", (1, 2, 2), (sd * 4.3 - 0.5, 18, -0.5), P, ())
    # the hat: a wide brim and three tapering green sections, each a bone so it bends and sways
    tb(m, s, "hat1", (10, 2, 9), (-5, 21.6, -4.5), G, [(GD, 2), (GL, 1)], rate=0.3, D=GD)
    tb(m, s, "hat1", (8, 6, 7), (-4, 23.4, -3.5), G, [(GD, 2), (GL, 1)], rate=0.28)
    tb(m, s, "hat2", (6, 5, 5), (-2.6, 29.2, -3.2), G, [(GD, 2), (GL, 1)], rate=0.28)
    tb(m, s, "hat3", (4, 4, 4), (-1.2, 34, -3.8), G, [(GD, 2)], rate=0.3)
    m.c("hat3", GD, (1, 38.6, -2.4), (2, 1.6, 2))
    # the little brother: tall red hat, white beard, green coat
    tb(m, s, "little", (2, 3, 2), (7.2, 0, -4), "brown_terracotta", ())
    tb(m, s, "little", (2, 3, 2), (8.8, 0, -4), "brown_terracotta", ())
    tb(m, s, "little", (5, 5, 4), (6, 3, -5), "green_terracotta", [("green_concrete", 1)], rate=0.3)
    tb(m, s, "lhead", (5, 5, 1.4), (6, 4.6, -1.4), W, (), front=checker(5, 5, 1), K=K_)
    tb(m, s, "lhead", (5, 3, 4), (6, 8, -5), P, (), front=["ppppp", "kpppk", "wwwww"], K=K_)
    tb(m, s, "lhead", (2, 2, 1.4), (7.5, 8.4, -1.2), P, [(PD, 1)], rate=0.4)
    tb(m, s, "lhat1", (6, 1.4, 5), (5.5, 10.6, -5.5), R, [(RD, 1)], rate=0.3)
    tb(m, s, "lhat1", (4, 5, 4), (6.5, 12, -5), R, [(RL, 1), (RD, 1)], rate=0.3)
    tb(m, s, "lhat2", (3, 5, 3), (7, 17, -4.6), R, [(RL, 1), (RD, 1)], rate=0.3)
    tb(m, s, "lhat2", (2, 3, 2), (7.6, 22, -4.2), R, [(RD, 1)], rate=0.3)
    idle = {"length": 3.2, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"].update({
        "hat1": {"rot": K((0, (0, 0, -3)), (1.6, (4, 0, 3)), (3.2, (0, 0, -3)))},
        "hat2": {"rot": K((0, (-4, 0, -6)), (1.6, (8, 0, 6)), (3.2, (-4, 0, -6)))},
        "hat3": {"rot": K((0, (-8, 0, -10)), (1.6, (14, 0, 10)), (3.2, (-8, 0, -10)))},
        "little": {"pos": K((0, Z), (0.4, (0, 1.4, 0)), (0.8, Z), (1.6, Z), (2.0, (0, 1.4, 0)), (2.4, Z), (3.2, Z))},
        "lhead": {"rot": K((0, (0, 20, 0)), (1.6, (6, -20, 6)), (3.2, (0, 20, 0)))},
        "lhat1": {"rot": K((0, (0, 0, 6)), (1.6, (0, 0, -6)), (3.2, (0, 0, 6)))},
        "lhat2": {"rot": K((0, (0, 0, 12)), (1.6, (0, 0, -12)), (3.2, (0, 0, 12)))},
    })
    idle["length"] = 4.0
    m.anims = {"idle": idle}
    m.attacks = {"minions": "roar", "leap": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


@chapter("moss_spirit", "<gradient:#455a64:#69f0ae><bold>The Moss Spirit</bold></gradient>", "Two Faces in the Stone", "IRON_GOLEM", "nature", "GREEN",
         extra=["heal", "pull"], items=["MOSS_BLOCK 32", "AMETHYST_SHARD 8", "DIAMOND 2"], money=26000,
         recipe=boss_recipe("SPORE_BLOSSOM_AIR", "BLOCK_STONE_PLACE", "ENTITY_IRON_GOLEM_DEATH", "mossy_cobblestone", 0.6, "roar", "die_kneel", ground_block="MOSS_BLOCK"))
def moss_spirit():
    """Picture 2: a squat stone spirit with two faces, glowing blue eyes on its head and a second pair on
    its chest, moss and grass growing over its shoulders with a white flower, and a gnarled wooden staff
    wound with moss, set with a red crystal."""
    m = Model("moss_spirit", "biped", 2.4)
    biped(m, hip=8, legx=3.2, neck=22, shoulder=21, armx=8)
    m.bone("staff", "armR", (-9, 10, 2))
    m.bone("grass", "head", (0, 31, 0))
    m.hold = {"staff": 10}
    s = Sheet(256, 256)
    St, SL, SD = "stone", "andesite", "gray_concrete"
    B, E = "light_blue_concrete", "cyan_concrete"
    K_ = {"s": St, "l": SL, "d": SD, "b": B, "e": E, "k": "black_concrete", "m": "moss_block", "g": "green_terracotta", "w": "white_concrete", "y": "yellow_concrete"}
    legs2(m, s, (5, 6, 5), 3.2, St, STONE, D=SD, boot="cobblestone", boot_tones=[("andesite", 1)])
    # chest: the second face, blue eyes in dark sockets, moss across the top
    tb(m, s, "body", (14, 13, 9), (-7, 8, -4.5), St, STONE, rate=0.22, D=SD, front=[
        "mmgmmgmmmgmmmg", "gmmmgmmgmmmgmm", ".mm.g..m.g..m.", "..............", "..............", "..kkk....kkk..", "..kbb....bbk..",
        "..kbe....ebk..", "..kkk....kkk..", "..............", "..............", "..............", ".............."], K=K_, lit={B, E})
    tb(m, s, "body", (15, 3, 10), (-7.5, 19, -5), "moss_block", MOSSY, rate=0.45)
    # head: smaller stone block with the upper face
    tb(m, s, "head", (9, 8, 8), (-4.5, 22, -4), St, STONE, rate=0.3, D=SD, front=[
        ".........", ".........", ".kk...kk.", ".kb...bk.", ".ke...ek.", ".........", "..kkkkk..", "........."], K=K_, lit={B, E})
    tb(m, s, "grass", (10, 2, 9), (-5, 30, -4.5), "moss_block", MOSSY, rate=0.3)
    for i, (x, z, h) in enumerate(((-4, -3, 5), (-2, 2, 7), (0, -1, 9), (2, 3, 6), (4, -2, 8), (3, 1, 4), (-3, 1, 6), (1, -4, 5))):
        m.c("grass", "green_concrete" if i % 2 else "lime_concrete", (x, 32 + h / 2, z), (0.6, h, 0.6), (0, i * 40, (i % 3 - 1) * 12))
    # the white flower on the chest moss
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        m.c("body", "white_concrete", (3 + dx * 1.1, 19.6 + dy * 1.1, 5.4), (1.2, 1.2, 0.4))
    m.c("body", "yellow_concrete", (3, 19.6, 5.6), (1, 1, 0.4))
    # arms: stone blocks with mossy shoulders
    arms2(m, s, (5, 10, 5), 21, 9.5, St, STONE, D=SD, hand="cobblestone", hand_tones=[("andesite", 1)], hand_size=(6, 4, 6))
    for sd in (1, -1):
        tb(m, s, "armL" if sd > 0 else "armR", (6, 3, 6), (sd * 9.5 - 3, 20, -3), "moss_block", MOSSY, rate=0.5)
    # staff: a gnarled branch with moss bands and a red crystal near the top
    limb(m, "staff", "dark_oak_log", (-9, -6, 2), [(10, 1.6, (0, 0, -4)), (10, 1.5, (0, 0, 6)), (8, 1.4, (0, 0, -8)), (5, 1.3, (0, 0, 24))])
    for y in (3, 9, 16):
        m.c("staff", "moss_block", (-9, y, 2), (2.2, 1.4, 2.2))
    m.c("staff", "red_concrete", (-11.4, 18, 2), (2, 2, 2), (0, 45, 45), light=True)
    m.c("staff", "lime_concrete", (-8.2, 25.5, 2), (1.6, 1.6, 1.6), (0, 30, 20))
    idle = {"length": 4.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"]["grass"] = {"rot": K((0, (0, 0, -4)), (2.0, (3, 0, 4)), (4.0, (0, 0, -4)))}
    m.anims = {"idle": idle}
    m.attacks = {"heal": "cast", "pull": "cast", "slam": "slam", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@chapter("cyclops_ogre", "<gradient:#33691e:#ccff90><bold>Gulp the Cyclops</bold></gradient>", "One Eye, Two Fists", "ZOMBIE", "nature", "GREEN",
         extra=["shockwave", "slam"], items=["SLIME_BALL 16", "BONE 16", "DIAMOND 2"], money=30000,
         recipe=boss_recipe("ITEM_SLIME", "ENTITY_RAVAGER_AMBIENT", "ENTITY_RAVAGER_DEATH", "green_terracotta", 0.7, "roar", "die_back"))
def cyclops_ogre():
    """Picture 3: a big green cyclops ogre with one yellow eye, a gaping mouth full of teeth, a horn on
    its head, green and lime stripes over its body and arms, and a wooden barrel strapped to its fists
    with bone spikes through it."""
    m = Model("cyclops_ogre", "biped", 2.2)
    biped(m, hip=8, legx=3.4, neck=23, shoulder=22, armx=9)
    m.bone("jaw", "head", (0, 24, 2))
    s = Sheet(256, 256)
    G, GL, GD = "lime_terracotta", "lime_concrete", "green_terracotta"
    STR = [("green_terracotta", 3), ("green_concrete", 2), ("lime_concrete", 1)]
    K_ = {"g": G, "l": GL, "d": GD, "k": "black_concrete", "w": "white_concrete", "y": "yellow_concrete", "r": "red_terracotta", "o": "orange_concrete", "t": "white_terracotta", "n": "brown_terracotta"}
    stripes = lambda wd, hg: ["".join("d" if (x + y * 2) % 6 < 2 else ("l" if (x + y) % 9 == 0 else "g") for x in range(wd)) for y in range(hg)]
    legs2(m, s, (5, 7, 5), 3.4, G, STR, D=GD, boot="green_terracotta", boot_tones=[("green_concrete", 1)])
    tb(m, s, "hips", (13, 4, 9), (-6.5, 6.5, -4.5), "brown_terracotta", LEATHER, rate=0.3,
       front=["nnnnnnnnnnnnn", "n.n.n.n.n.n.n", ".............", "............."], K=K_)
    tb(m, s, "body", (14, 12, 9), (-7, 10, -4.5), G, STR, rate=0.25, cell=3, front=stripes(14, 12), K=K_)
    tb(m, s, "body", (12, 4, 2), (-6, 13, 4), GL, [(G, 1)], rate=0.3)   # belly
    arms2(m, s, (5, 11, 5), 22, 9.5, G, STR, hand=GD, hand_tones=[("green_concrete", 1)], hand_size=(6, 4, 6))
    # the barrel in both fists with bone spikes
    tb(m, s, "armR", (12, 6, 6), (-6, 7, 3), "spruce_planks", [("dark_oak_planks", 2), ("stripped_spruce_log", 1)], rate=0.3,
       front=["n...n...n...", "n...n...n...", "n...n...n...", "n...n...n...", "n...n...n...", "n...n...n..."], K=K_)
    for x in (-4, 0, 4):
        m.c("armR", "iron_block", (x, 10, 6.2), (0.6, 6.2, 0.4))
    for x, a in ((-5, -30), (-1, 10), (3, -15), (6, 25)):
        m.c("armR", "bone_block", (x, 14, 6), (1, 5, 1), (a, 0, 0), (x, 12, 6))
    # head: a big round block with one eye, the horn, the open mouth with a jaw
    tb(m, s, "head", (11, 8, 10), (-5.5, 25, -5), G, STR, rate=0.25, L=GL, front=[
        "llllllllll l".replace(" ", "l")[:11], "ggggggggggg", "ggggkkkgggg", "gggkwyykggg", "gggkyykkggg", "ggggkkkgggg", "ggggggggggg", "ddddddddddd"], K=K_)
    tb(m, s, "head", (11, 2, 1), (-5.5, 23.6, 4.6), "red_terracotta", (), front=["twtwtwtwtwt", "rrrrrrrrrrr"], K=K_)
    tb(m, s, "jaw", (11, 3, 10), (-5.5, 21, -5), G, STR, rate=0.25, front=["rrrrrrrrrrr", "wtwtwtwtwtw", "ggggggggggg"], K=K_)
    for sd in (1, -1):
        m.c("jaw", "white_terracotta", (sd * 3.5, 25, 4.7), (1.2, 3, 1.2), (0, 0, -10 * sd))
    limb(m, "head", "white_terracotta", (0, 33, 0), [(3, 2.2, (-10, 0, 0)), (3, 1.6, (-30, 0, 0)), (2, 1.0, (-55, 0, 0))])
    for sd in (1, -1):
        tb(m, s, "head", (2, 4, 1), (sd * 6 - 1, 27, 0), G, (), rot=(0, 0, -20 * sd), origin=(sd * 5.5, 28, 0))
    m.attacks = {"slam": "slam", "shockwave": "stomp", "charge": "lunge", "roar": "roar"}
    m.melee = "swipe"
    return m


@chapter("grubnose", "<gradient:#827717:#ffcc80><bold>Grubnose the Troll</bold></gradient>", "Under the Old Bridge", "ZOMBIE", "earth", "YELLOW",
         extra=["slam", "shockwave"], items=["BONE 24", "LEATHER 12", "DIAMOND 2"], money=34000,
         recipe=boss_recipe("BLOCK", "ENTITY_RAVAGER_AMBIENT", "ENTITY_RAVAGER_DEATH", "mud", 0.6, "roar", "die_front", ground_block="MUD"))
def grubnose():
    """Picture 4: a huge olive-yellow troll, all shoulders and long arms, a bulbous orange nose, a heavy
    brow over little eyes, a leather loincloth hung with bones, and lumpy mottled skin."""
    m = Model("grubnose", "biped", 2.3)
    biped(m, hip=9, legx=3.6, neck=24, shoulder=23, armx=10)
    s = Sheet(256, 256)
    Y, YL, YD = "lime_terracotta", "yellow_terracotta", "green_terracotta"
    SKIN = [("lime_terracotta", 3), ("green_terracotta", 2), ("yellow_terracotta", 1)]
    K_ = {"y": Y, "l": YL, "d": YD, "k": "black_concrete", "w": "white_concrete", "o": "orange_terracotta", "n": "brown_terracotta", "b": "bone_block", "r": "red_terracotta"}
    legs2(m, s, (6, 8, 6), 3.6, Y, SKIN, D=YD, boot=Y, boot_tones=SKIN)
    tb(m, s, "hips", (14, 5, 9), (-7, 7, -4.5), "brown_terracotta", LEATHER, rate=0.35,
       front=["nnnnnnnnnnnnnn", "nbnnnbnnnbnnnb", "..nnnnnnnnnn..", "...nnnnnnnn...", "....nnnnnn...."], K=K_)
    tb(m, s, "body", (15, 12, 10), (-7.5, 11, -5), Y, SKIN, rate=0.3, D=YD)
    tb(m, s, "body", (17, 5, 11), (-8.5, 19, -5.5), Y, SKIN, rate=0.3, L=YL)   # hunched shoulders
    # arms long enough to drag the knuckles
    arms2(m, s, (6, 15, 6), 24, 11, Y, SKIN, D=YD, hand=Y, hand_tones=SKIN, hand_size=(7, 5, 7))
    # head pushed forward under the shoulders
    tb(m, s, "head", (10, 9, 9), (-5, 21, -1), Y, SKIN, rate=0.25, front=[
        "llllllllll", "dddddddddd", "dkkddddkkd", "ywkyyyykwy", "yyyyyyyyyy", "yyyyyyyyyy", "ynnnnnnnny", "ywnwnwnwny", "yyyyyyyyyy"], K=K_)
    tb(m, s, "head", (4, 5, 4), (-2, 22.6, 7.6), "orange_terracotta", [("terracotta", 2), ("red_terracotta", 1)], rate=0.4)
    for sd in (1, -1):
        m.c("head", "bone_block", (sd * 3.5, 22, 8.2), (1, 2.6, 1), (0, 0, 15 * sd))
        tb(m, s, "head", (2, 3, 2), (sd * 5.6 - 1, 26, 2), Y, SKIN, rot=(0, 0, -25 * sd), origin=(sd * 5, 27, 3))
    m.attacks = {"slam": "slam", "shockwave": "stomp", "charge": "lunge"}
    m.melee = "swipe"
    m.bend = -20
    return m


@chapter("orc_bruiser", "<gradient:#558b2f:#f5f5f5><bold>Borka the Bruiser</bold></gradient>", "Shirt Torn, Tusks Out", "VINDICATOR", "earth", "GREEN",
         minion="ZOMBIE", extra=["minions", "charge"], items=["IRON_INGOT 16", "LEATHER 12", "DIAMOND 2"], money=38000,
         recipe=boss_recipe("CRIT", "ENTITY_VINDICATOR_CELEBRATE", "ENTITY_VINDICATOR_DEATH", "green_terracotta", 0.7, "roar", "die_back"))
def orc_bruiser():
    """Picture 5: a green orc with a heavy square head, mottled moss-green skin, ivory tusks poking up
    from the jaw, a torn white shirt under a brown leather vest with a rope belt, and brown trousers."""
    m = Model("orc_bruiser", "biped", 2.3)
    biped(m, hip=8, legx=2.8, neck=21, shoulder=20, armx=8)
    s = Sheet(256, 256)
    G = "green_terracotta"
    SKIN = [("green_concrete", 2), ("lime_terracotta", 2), ("moss_block", 1)]
    W, WD = "white_wool", "light_gray_wool"
    K_ = {"g": G, "l": "lime_terracotta", "d": "green_concrete", "k": "black_concrete", "w": "white_concrete", "t": "white_terracotta",
          "n": "brown_terracotta", "b": "brown_concrete", "s": W, "x": WD, "e": "light_blue_concrete"}
    legs2(m, s, (4, 7, 4), 2.8, "brown_terracotta", LEATHER, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    # shirt with ragged hem and the vest over it
    tb(m, s, "body", (12, 12, 7), (-6, 8, -3.5), W, [(WD, 2), ("white_terracotta", 1)], rate=0.25, front=[
        "nnnsssssnnnn"[:12], "nnnnsssnnnnn", "nnnnsssnnnnn", "nnnnnssnnnnn", "nnnnnsnnnnnn", "nnnnnnnnnnnn", "bbbbbbbbbbbb", "ssssssssssss",
        "ssssssssssss", "sxssxssxssxs", "s.ss.sxs.ss.", "............"], back=[
        "nnnnnnnnnnnn", "nnnnnnnnnnnn", "nnnnnnnnnnnn", "nnnnnnnnnnnn", "nnnnnnnnnnnn", "nnnnnnnnnnnn", "bbbbbbbbbbbb", "ssssssssssss",
        "ssssssssssss", "sxssxssxssxs", "s.ss.sxs.ss.", "............"], K=K_)
    arms2(m, s, (4, 6, 4), 20, 8.2, W, [(WD, 1)], hand=G, hand_tones=SKIN, hand_size=(4.6, 6, 4.6))
    # head: big square green head, brows, little eyes, tusks
    tb(m, s, "head", (10, 10, 9), (-5, 21, -4.5), G, SKIN, rate=0.35, L="lime_terracotta", front=[
        "llllllllll", "gggggggggg", "gddddgdddd"[:10], "gkwggggwkg", "gggggggggg", "ggggddgggg", "gggggggggg", "gtgggggtgg", "gtddddddtg", "gggggggggg"], K=K_)
    for sd in (1, -1):
        m.c("head", "white_terracotta", (sd * 3.2, 26, 4.8), (1.2, 3, 1.2), (0, 0, -8 * sd))
        tb(m, s, "head", (2, 3, 1), (sd * 6 - 1, 26, 0), G, SKIN, rot=(0, 0, -30 * sd), origin=(sd * 5.5, 27, 0))
    tb(m, s, "head", (3, 3, 2), (-1.5, 25.4, 4.4), G, SKIN, rate=0.5)
    m.attacks = {"minions": "roar", "charge": "lunge", "slam": "slam", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@chapter("mudclub", "<gradient:#3e2723:#9ccc65><bold>Mudclub</bold></gradient>", "Troll of the Dry Riverbed", "ZOMBIE", "earth", "GREEN",
         extra=["slam", "leap"], items=["MUD 32", "STICK 16", "DIAMOND 3"], money=42000,
         recipe=boss_recipe("BLOCK", "ENTITY_POLAR_BEAR_WARNING", "ENTITY_POLAR_BEAR_DEATH", "mud", 0.6, "roar", "die_front", ground_block="MUD"))
def mudclub():
    """Picture 6: a lanky hunched swamp troll with mossy green skin, brown rags hanging off its shoulders
    and hips, a pointed head with a long jaw, and a heavy log club dragged in one hand."""
    m = Model("mudclub", "biped", 2.4)
    biped(m, hip=9, legx=2.8, neck=21, shoulder=20, armx=7.5)
    m.bone("club", "armR", (-8, 6, 2))
    m.hold = {"club": 30}
    m.bend = -35
    s = Sheet(256, 256)
    G = "green_terracotta"
    SKIN = [("moss_block", 2), ("lime_terracotta", 2), ("green_concrete", 1)]
    RAG = [("brown_terracotta", 3), ("terracotta", 2), ("brown_concrete", 1)]
    K_ = {"g": G, "l": "lime_terracotta", "k": "black_concrete", "w": "white_concrete", "y": "yellow_concrete", "t": "white_terracotta", "n": "brown_terracotta", "r": "terracotta"}
    legs2(m, s, (4, 9, 4), 2.8, G, SKIN, boot=G, boot_tones=SKIN)
    tb(m, s, "hips", (10, 4, 7), (-5, 7, -3.5), "brown_terracotta", RAG, rate=0.35, front=["nnnnnnnnnn", "nrnnrnnrnn", "n.nn.n.nn.", "n..n...n.."], K=K_)
    tb(m, s, "body", (10, 11, 6), (-5, 10, -3), G, SKIN, rate=0.3)
    tb(m, s, "body", (11, 6, 7), (-5.5, 15, -3.5), "brown_terracotta", RAG, rate=0.35, front=["nnnnnnnnnnn", "nnrnnnnrnnn", "nnnnnnnnnnn", "rnnnnnnnnrn", "n.nnn.nnn.n", "..n.....n.."], K=K_)
    arms2(m, s, (3, 13, 3), 20, 7.5, G, SKIN, hand=G, hand_tones=SKIN, hand_size=(4, 4, 4))
    # head: long and pointed, the jaw jutting forward
    tb(m, s, "head", (7, 9, 7), (-3.5, 21, -2), G, SKIN, rate=0.3, front=[
        "lllllll", "ggggggg", "gkgggkg", "gygggyg", "ggglggg", "gnnnnng", "gwnwnwg", "ggggggg", "ggggggg"], K=K_)
    tb(m, s, "head", (5, 3, 3), (-2.5, 30, -1), G, SKIN, rate=0.3)
    tb(m, s, "head", (3, 3, 3), (-1.5, 33, 0), G, SKIN, rate=0.3)
    tb(m, s, "head", (3, 3, 2), (-1.5, 24.5, 4.6), G, SKIN, rate=0.4)
    for sd in (1, -1):
        tb(m, s, "head", (3, 2, 1), (sd * 4.5 - 1.5, 26, 1), G, SKIN, rot=(0, 0, -35 * sd), origin=(sd * 4, 27, 1))
    # the log club
    tb(m, s, "club", (3, 12, 3), (-9.5, -8, 0.5), "oak_log", [("stripped_oak_log", 1)], rate=0.2)
    tb(m, s, "club", (5, 7, 5), (-10.5, -15, -0.5), "oak_log", [("stripped_oak_log", 1), ("moss_block", 1)], rate=0.3)
    for y in (-14, -11):
        m.c("club", "dark_oak_log", (-8, y, 2), (1.2, 1.2, 4), (0, 0, 30))
    m.attacks = {"slam": "slam", "leap": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@chapter("ugor", "<gradient:#4e342e:#f8bbd0><bold>Ugor</bold></gradient>", "The Brute of the Last Chapter", "RAVAGER", "earth", "RED",
         minion="PIGLIN_BRUTE", extra=["minions", "charge", "quake"], items=["GOLD_BLOCK 2", "PORKCHOP 32", "DIAMOND 4"], money=52000,
         recipe=boss_recipe("BLOCK", "ENTITY_HOGLIN_ANGRY", "ENTITY_HOGLIN_DEATH", "mud_bricks", 0.6, "roar", "die_front", ground_block="PACKED_MUD"))
def ugor():
    """Picture 7: a huge brown-furred brute with a villager's build and a pig's snout, small dark eyes
    under a shaggy brow, tusks, a mane down its back, and fists like stumps. Breathes heavily."""
    m = Model("ugor", "biped", 2.4)
    biped(m, hip=9, legx=3.6, neck=24, shoulder=23, armx=10)
    s = Sheet(256, 256)
    F = "brown_terracotta"
    FUR = [("brown_concrete", 2), ("terracotta", 2), ("dark_oak_planks", 1)]
    P = "pink_terracotta"
    K_ = {"f": F, "d": "brown_concrete", "l": "terracotta", "p": P, "q": "pink_concrete", "k": "black_concrete", "w": "white_concrete", "t": "white_terracotta", "r": "red_terracotta"}
    legs2(m, s, (6, 8, 6), 3.6, F, FUR, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    tb(m, s, "body", (16, 15, 11), (-8, 9, -5.5), F, FUR, rate=0.22, cell=3, D="brown_concrete")
    tb(m, s, "body", (6, 12, 3), (-3, 14, -7.6), "brown_concrete", FUR, rate=0.4)   # the mane
    arms2(m, s, (6, 13, 6), 24, 11, F, FUR, hand="brown_concrete", hand_tones=[("terracotta", 1)], hand_size=(7, 5, 7))
    for sd in (1, -1):
        tb(m, s, "armL" if sd > 0 else "armR", (7, 4, 7), (sd * 11 - 3.5, 21, -3.5), "brown_concrete", FUR, rate=0.4)
    tb(m, s, "head", (11, 10, 10), (-5.5, 22, -3), F, FUR, rate=0.35, front=[
        "dddddddddd d".replace(" ", "d")[:11], "ddfdddddfdd", "fkkfffffkkf", "fwkfffffkwf", "fffffffffff", "fffffffffff",
        "fffffffffff", "ffffffffff f".replace(" ", "f")[:11], "fffffffffff", "fffffffffff"], K=K_)
    # the snout with two nostrils, tusks and a little mouth
    tb(m, s, "head", (6, 4, 3), (-3, 23.6, 6.8), P, [("pink_concrete", 1), ("terracotta", 1)], rate=0.3, front=["pppppp", "pkppkp", "pkppkp", "pppppp"], K=K_)
    for sd in (1, -1):
        m.c("head", "white_terracotta", (sd * 3.6, 24, 7.2), (1.2, 3, 1.2), (0, 0, -12 * sd))
        tb(m, s, "head", (3, 3, 2), (sd * 6.5 - 1.5, 30, 0), F, FUR, rot=(0, 0, -30 * sd), origin=(sd * 6, 30, 1))
    idle = {"length": 3.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"]["body"] = {"rot": K((0, Z), (1.5, (6, 0, 0)), (3.0, Z)), "scl": K((0, (1, 1, 1)), (1.5, (1.06, 1.03, 1.08)), (3.0, (1, 1, 1)))}
    m.anims = {"idle": idle}
    m.attacks = {"minions": "roar", "charge": "lunge", "quake": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


# ============================================================================================ minis


def mini_recipe(part="HAPPY_VILLAGER", sin="ENTITY_ZOMBIE_AMBIENT", sdie="ENTITY_ZOMBIE_DEATH", block="moss_block", pin=1.2, anim="roar", die="die_front"):
    return v9_minis.generic(part, sin, sdie, block, pin, anim, die)


@remini("pack_goblin", "pack_goblin", "<gradient:#558b2f:#ce93d8><bold>Snik</bold></gradient>", "Goblin Cutpurse", entity="ZOMBIE", theme="nature", bar="GREEN",
        extra=["leap", "volley"], recipe=mini_recipe("CRIT", "ENTITY_PILLAGER_AMBIENT", "ENTITY_PILLAGER_DEATH", "brown_wool", 1.6))
def pack_goblin():
    """Picture 8: a lanky green goblin with long ears, a brown hat, a red vest, purple trousers and a
    grin full of crooked teeth."""
    m = Model("pack_goblin", "biped", 1.5)
    biped(m, hip=7, legx=1.8, neck=17, shoulder=16, armx=5.2)
    m.bone("earL", "head", (4, 21, 0))
    m.bone("earR", "head", (-4, 21, 0))
    s = Sheet(256, 256)
    G = "lime_terracotta"
    SKIN = [("green_concrete", 2), ("lime_concrete", 1), ("green_terracotta", 2)]
    K_ = {"g": G, "d": "green_terracotta", "k": "black_concrete", "w": "white_concrete", "y": "yellow_concrete", "t": "white_terracotta",
          "r": "red_terracotta", "R": "red_concrete", "n": "brown_terracotta", "p": "purple_terracotta"}
    legs2(m, s, (3, 6, 3), 1.8, "purple_terracotta", [("purple_concrete", 1), ("magenta_terracotta", 1)], boot="brown_terracotta", boot_tones=LEATHER)
    tb(m, s, "body", (8, 9, 5), (-4, 7.5, -2.5), "red_terracotta", [("red_concrete", 1), ("brown_terracotta", 1)], rate=0.25, front=[
        "rrrggrrr", "rrrggrrr", "rrrggrrr", "rRrggrRr", "rrrggrrr", "nnnnnnnn", "nnynnnnn", "pppppppp", "pppppppp"], K=K_)
    arms2(m, s, (3, 8, 3), 16, 5.6, G, SKIN, hand=G, hand_tones=SKIN, hand_size=(3.4, 3, 3.4))
    tb(m, s, "head", (8, 8, 7), (-4, 16.5, -3.5), G, SKIN, rate=0.5, cell=1, front=[
        "gggggggg", "dddggddd", "gyk..ky.".replace(".", "g"), "gggddggg", "ggggdggg", "gkwkwkwg", "ggkkkkgg", "gggggggg"], K=K_)
    tb(m, s, "head", (2, 3, 2), (-1, 18.4, 3.4), G, SKIN, rate=0.4)
    tb(m, s, "body", (3, 3, 2), (1.6, 7.6, 2.4), "brown_terracotta", LEATHER, rate=0.5)
    limb(m, "armR", "iron_block", (-5.6, 5, 2), [(5, 0.8, (60, 0, 0))])
    m.c("armR", "dark_oak_planks", (-5.6, 5, 1.2), (1, 1, 2.4), (60, 0, 0))
    for sd, ear in ((1, "earL"), (-1, "earR")):
        tb(m, s, ear, (5, 2, 1), (sd * 4 + (0 if sd > 0 else -5), 20.4, -0.5), G, SKIN, rot=(0, 0, 18 * sd), origin=(sd * 4, 21, 0))
    tb(m, s, "head", (10, 1, 9), (-5, 24.4, -4.5), "brown_terracotta", LEATHER, rate=0.35)
    tb(m, s, "head", (7, 4, 6), (-3.5, 25.4, -3), "brown_terracotta", LEATHER, rate=0.35, front=["nnnnnnn", "nnnnnnn", "rrrrrrr", "nnnnnnn"], K=K_)
    idle = {"length": 2.4, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"].update({"earL": {"rot": K((0, Z), (0.3, (0, 0, 14)), (0.6, Z), (2.4, Z))},
                          "earR": {"rot": K((0, Z), (1.2, Z), (1.5, (0, 0, -14)), (1.8, Z), (2.4, Z))}})
    m.anims = {"idle": idle}
    m.attacks = {"leap": "lunge", "volley": "double", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("goblin_king", "goblin_king", "<gradient:#1b5e20:#ffd54f><bold>King Grizzlegrin</bold></gradient>", "Crown Too Big", entity="ZOMBIE", theme="nature", bar="YELLOW",
        minion="ZOMBIE", extra=["minions", "volley"], recipe=mini_recipe("CRIT", "ENTITY_PILLAGER_CELEBRATE", "ENTITY_PILLAGER_DEATH", "gold_block", 1.4))
def goblin_king():
    """Picture 8 again: the goblins' king, fatter, a gold crown slipping over one ear, a purple cape with
    a white fur collar, a gold belt and a crooked sceptre."""
    m = Model("goblin_king", "biped", 1.7)
    biped(m, hip=7, legx=2.2, neck=17, shoulder=16, armx=6)
    m.bone("cape", "body", (0, 16, -3))
    m.bone("sceptre", "armR", (-6, 7, 2))
    m.hold = {"sceptre": 20}
    s = Sheet(256, 256)
    G = "lime_terracotta"
    SKIN = [("green_concrete", 2), ("lime_concrete", 1), ("green_terracotta", 2)]
    K_ = {"g": G, "d": "green_terracotta", "k": "black_concrete", "w": "white_concrete", "y": "yellow_concrete", "a": "gold_block", "o": "yellow_terracotta",
          "p": "purple_terracotta", "P": "purple_concrete", "r": "red_concrete", "n": "brown_terracotta", "f": "white_wool"}
    legs2(m, s, (3, 6, 3), 2.2, "brown_terracotta", LEATHER, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    tb(m, s, "body", (10, 9, 7), (-5, 7.5, -3.5), G, SKIN, rate=0.3, front=[
        "ffffffffff", "gggggggggg", "gggggggggg", "gggggggggg", "aaaaoaaaaa", "aaaarraaaa", "nnnnnnnnnn", "nnnnnnnnnn", "nnnnnnnnnn"], K=K_)
    tb(m, s, "body", (12, 2, 8), (-6, 15.5, -4), "white_wool", [("light_gray_wool", 1)], rate=0.3)
    tb(m, s, "cape", (11, 12, 1), (-5.5, 4, -4.6), "purple_terracotta", [("purple_concrete", 2), ("magenta_terracotta", 1)], rate=0.3, D="gold_block")
    arms2(m, s, (3, 8, 3), 16, 6.4, G, SKIN, hand=G, hand_tones=SKIN, hand_size=(3.4, 3, 3.4))
    tb(m, s, "head", (9, 8, 8), (-4.5, 16.5, -4), G, SKIN, rate=0.3, front=[
        "ggggggggg", "dddgggddd", "gykgggkyg", "gggggdggg", "ggggggggg", "gkwkwkwkg", "gggkkkggg", "ggggggggg"], K=K_)
    tb(m, s, "head", (2, 3, 2), (-1, 18.4, 3.8), G, SKIN, rate=0.4)
    for sd in (1, -1):
        tb(m, s, "head", (5, 2, 1), (sd * 4.5 + (0 if sd > 0 else -5), 20.4, -0.5), G, SKIN, rot=(0, 0, 14 * sd), origin=(sd * 4.5, 21, 0))
    tb(m, s, "head", (9, 3, 9), (-4.5, 24.2, -4.5), "gold_block", [("yellow_terracotta", 1)], rate=0.2, rot=(0, 0, 10), origin=(0, 24, 0),
       front=["a.a.a.a.a", "aaaaraaaa", "aaaaaaaaa"], side=["a.a.a.a.a", "aaaaaaaaa", "aaaaaaaaa"], K=K_)
    limb(m, "sceptre", "stripped_spruce_log", (-6, 0, 3), [(6, 1, (6, 0, 0)), (5, 1, (-10, 0, 8))])
    m.c("sceptre", "gold_block", (-5.4, 11.6, 3.6), (2.4, 2.4, 2.4), (0, 45, 0))
    m.c("sceptre", "red_concrete", (-5.4, 11.6, 5), (1, 1, 1), light=True)
    m.attacks = {"minions": "roar", "volley": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("sprout_sprite", "snapjaw", "<gradient:#1b5e20:#ce93d8><bold>Snapjaw</bold></gradient>", "Hungry Flower", entity="ZOMBIE", theme="toxic", bar="PURPLE",
        extra=["poison", "pull"], movement="still", recipe=mini_recipe("SPORE_BLOSSOM_AIR", "BLOCK_BIG_DRIPLEAF_TILT_DOWN", "BLOCK_AZALEA_LEAVES_BREAK", "moss_block", 0.8, "pulse", "die_drop"))
def snapjaw():
    """Picture 9: a man-eating plant: a green stalk with spiky leaves, a purple flower head that opens on
    a red mouth full of white teeth, and it sways and snaps without ever moving its roots."""
    m = Model("snapjaw", "float", 1.8)
    m.bone("core", "root", (0, 0, 0))
    m.bone("stem1", "core", (0, 4, 0))
    m.bone("stem2", "stem1", (0, 12, 0))
    m.bone("head", "stem2", (0, 20, 1))
    m.bone("jaw", "head", (0, 21, 2))
    m.bone("armL", "stem1", (2, 8, 0))
    m.bone("armR", "stem1", (-2, 8, 0))
    m.no_elbows = True
    s = Sheet(256, 256)
    G, GL, GD = "green_concrete", "lime_concrete", "green_terracotta"
    P, PL, PD = "purple_concrete", "magenta_terracotta", "purple_terracotta"
    K_ = {"p": P, "l": PL, "d": PD, "r": "red_concrete", "R": "red_terracotta", "w": "white_concrete", "t": "white_terracotta", "k": "black_concrete", "y": "yellow_concrete", "g": G}
    # roots and the pot of moss
    tb(m, s, "core", (10, 3, 10), (-5, 0, -5), "moss_block", MOSSY, rate=0.4)
    for a in range(0, 360, 60):
        x, z = math.cos(math.radians(a)) * 5, math.sin(math.radians(a)) * 5
        m.c("core", "dark_oak_log", (x, 0.6, z), (3, 1.2, 1.2), (0, -a, 0))
    tb(m, s, "stem1", (2, 9, 2), (-1, 3, -1), G, [(GD, 1), (GL, 1)], rate=0.35)
    tb(m, s, "stem2", (2, 9, 2), (-1, 12, -1), G, [(GD, 1), (GL, 1)], rate=0.35)
    for i in range(8):
        y = 5 + i * 2.2
        a = i * 95
        m.c("stem1" if y < 12 else "stem2", "green_terracotta", (math.cos(math.radians(a)) * 1.3, y, math.sin(math.radians(a)) * 1.3), (0.6, 0.6, 1.6), (0, -a, 30))
    for i, (x, z, a) in enumerate(((4, 3, 30), (-4, 2, 150), (2, -4, 250), (-3, -3, 200), (5, -1, 340))):
        m.c("core", "green_concrete" if i % 2 else "lime_concrete", (x, 3.4, z), (5, 0.5, 2.4), (0, a, -12))
    # spiky leaves
    for bone, sd in (("armL", 1), ("armR", -1)):
        for i, (y, L, a) in enumerate(((7, 8, 20), (10, 6, 40))):
            m.c(bone, GL if i else G, (sd * (1 + L / 2), y, 0), (L, 0.6, 2.6), (0, 0, a * sd), (sd * 1, y, 0))
            for j in range(3):
                m.c(bone, GD, (sd * (2 + j * 2), y + (j + 1) * 0.6 * math.tan(math.radians(a)) + 0.2, 1.4), (0.8, 0.5, 0.8), (0, 0, a * sd))
    # the flower head: purple petals around a red mouth with teeth, the jaw hinges down
    tb(m, s, "head", (9, 5, 8), (-4.5, 21, -3), P, [(PD, 2), (PL, 1)], rate=0.5, cell=1, front=["ppppppppp", "pdpdpdpdp", "rrrrrrrrr", "wrwrwrwrw", "rrrrrrrrr"], K=K_)
    tb(m, s, "jaw", (9, 3, 8), (-4.5, 18, -3), P, [(PD, 2)], rate=0.3, front=["rrrrrrrrr", "wrwrwrwrw", "ppppppppp"], K=K_)
    for i in range(7):
        a = i * 360 / 7
        x, z = math.cos(math.radians(a)) * 5.4, math.sin(math.radians(a)) * 4.8
        m.c("head", PL if i % 2 else P, (x, 25, z), (3, 1, 3), (0, -a, 25), (x, 25, z))
    for x in (-2, 2):
        m.c("head", "yellow_concrete", (x, 26.2, -1), (1, 1, 1), light=True)
    for i in range(10):
        a = i * 36
        m.c("head", "green_terracotta", (math.cos(math.radians(a)) * 3, 20.6, math.sin(math.radians(a)) * 3), (1.2, 0.8, 1.2))
    idle = {"length": 3.0, "loop": True, "bones": {
        "stem1": {"rot": K((0, (0, 0, -6)), (1.5, (4, 0, 6)), (3.0, (0, 0, -6)))},
        "stem2": {"rot": K((0, (4, 0, -8)), (1.5, (-6, 0, 8)), (3.0, (4, 0, -8)))},
        "head": {"rot": K((0, (0, -20, 0)), (0.8, (10, 10, 0)), (1.5, (0, 25, 0)), (2.2, (8, -5, 0)), (3.0, (0, -20, 0)))},
        "jaw": {"rot": K((0, Z), (0.4, (30, 0, 0)), (0.6, Z), (1.8, Z), (2.0, (24, 0, 0)), (2.2, Z), (3.0, Z))},
        "armL": {"rot": K((0, (0, 0, 8)), (1.5, (0, 0, -6)), (3.0, (0, 0, 8)))},
        "armR": {"rot": K((0, (0, 0, -8)), (1.5, (0, 0, 6)), (3.0, (0, 0, -8)))},
    }}
    m.anims = {"idle": idle}
    m.attacks = {"poison": "pulse", "pull": "raise"}
    m.melee = "swipe"
    return m


@remini("boo_twins", "boo_twins", "<gradient:#bdbdbd:#ffffff><bold>The Boo Twins</bold></gradient>", "Nobody Home", entity="VEX", theme="soul", bar="WHITE",
        extra=["darkness", "blink"], recipe=mini_recipe("SOUL", "ENTITY_VEX_AMBIENT", "ENTITY_VEX_DEATH", "white_wool", 1.4, "pulse", "die_drop"))
def boo_twins():
    """Picture 10: two pale ghost kids with wide flat heads, hollow black eyes and a dark mouth, ragged
    grey bodies and dangling legs. They bob up and down out of step and lean toward each other."""
    m = Model("boo_twins", "float", 1.6)
    m.bone("core", "root", (0, 8, 0))
    for t, x in (("A", 6.5), ("B", -6.5)):
        m.bone("ghost" + t, "core", (x, 8, 0))
        m.bone("head" + t, "ghost" + t, (x, 16, 0))
        m.bone("legs" + t, "ghost" + t, (x, 8, 0))
    m.bone("head", "core", (0, 16, 0))
    m.no_elbows = True
    s = Sheet(256, 256)
    W, WL, WD = "light_gray_wool", "white_wool", "gray_wool"
    GH = [("white_wool", 2), ("light_gray_terracotta", 1), ("gray_wool", 1)]
    K_ = {"w": W, "l": WL, "d": WD, "k": "black_concrete", "g": "gray_concrete", "b": "light_blue_concrete"}
    for t, x, eyes in (("A", 6.5, ["wwwwwwwwww", "wkkwwwwkkw", "wkbwwwwbkw", "wkkwwwwkkw", "wwwwkkwwww", "wwwwkkwwww"]),
                       ("B", -6.5, ["wwwwwwwwww", "wkkkwwkkkw", "wkkkwwkkkw", "wwwwwwwwww", "wwwkkkkwww", "wwwwwwwwww"])):
        tb(m, s, "head" + t, (10, 6, 8), (x - 5, 16, -4), W, GH, rate=0.3, L=WL, front=eyes, K=K_, lit={"light_blue_concrete"})
        tb(m, s, "ghost" + t, (6, 7, 4), (x - 3, 9, -2), W, GH, rate=0.35, D=WD)
        for sd in (1, -1):
            tb(m, s, "ghost" + t, (2, 6, 2), (x + sd * 4 - 1, 10, -1), W, GH, rot=(0, 0, 20 * sd), origin=(x + sd * 3, 15, 0))
            tb(m, s, "legs" + t, (2, 7, 2), (x + sd * 1.6 - 1, 2, -1), W, GH, rate=0.4, D=WD)
        for i in range(5):
            m.c("ghost" + t, WD, (x - 2.4 + i * 1.2, 8.6, 1.6), (1, 1.2 + (i % 2) * 0.8, 0.6))
    m.c("core", "white_stained_glass", (0, 4, 0), (0.1, 0.1, 0.1))
    idle = {"length": 2.4, "loop": True, "bones": {
        "ghostA": {"pos": K((0, Z), (0.6, (0, 2.4, 0)), (1.2, Z), (1.8, (0, -1, 0)), (2.4, Z)), "rot": K((0, (0, 0, 6)), (1.2, (0, 0, 10)), (2.4, (0, 0, 6)))},
        "ghostB": {"pos": K((0, (0, 1.2, 0)), (0.6, (0, -1, 0)), (1.2, (0, 1.2, 0)), (1.8, (0, 2.6, 0)), (2.4, (0, 1.2, 0))), "rot": K((0, (0, 0, -6)), (1.2, (0, 0, -10)), (2.4, (0, 0, -6)))},
        "headA": {"rot": K((0, (0, -10, 0)), (1.2, (6, 10, 4)), (2.4, (0, -10, 0)))},
        "headB": {"rot": K((0, (0, 12, 0)), (1.2, (-4, -12, -4)), (2.4, (0, 12, 0)))},
        "legsA": {"rot": K((0, (10, 0, 0)), (1.2, (-12, 0, 0)), (2.4, (10, 0, 0)))},
        "legsB": {"rot": K((0, (-12, 0, 0)), (1.2, (10, 0, 0)), (2.4, (-12, 0, 0)))},
        "core": {"pos": K((0, Z), (1.2, (0, 1, 0)), (2.4, Z))},
    }}
    m.anims = {"idle": idle}
    m.attacks = {"darkness": "pulse", "blink": "spin", "dive": "dive"}
    m.melee = "swipe"
    return m


@remini("plump_pigeon", "mossling", "<gradient:#33691e:#ffcc80><bold>Mossling</bold></gradient>", "It Hatched From a Bush", entity="ZOMBIE", theme="nature", bar="GREEN",
        extra=["leap", "shockwave"], recipe=mini_recipe("COMPOSTER", "ENTITY_PARROT_AMBIENT", "ENTITY_PARROT_DEATH", "moss_block", 1.4, "roar", "die_back"))
def mossling():
    """Picture 11: a round green bird made of moss: a big mottled body that is mostly head, one beady
    black eye on each side, a brown band and a pale buckle across its belly, stubby wings, and long
    peach legs ending in wide flat duck feet."""
    m = Model("mossling", "biped", 1.6)
    biped(m, hip=8, legx=2.4, neck=9, shoulder=17, armx=7)
    m.no_elbows = True
    s = Sheet(256, 256)
    G = "green_concrete"
    K_ = {"g": G, "l": "lime_concrete", "d": "green_terracotta", "k": "black_concrete", "w": "white_concrete", "n": "brown_terracotta", "b": "light_gray_concrete", "o": "orange_terracotta"}
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2.4
        tb(m, s, leg, (1.4, 8, 1.4), (x - 0.7, 0.6, -0.7), "white_terracotta", [("pink_terracotta", 1)], rate=0.3)
        tb(m, s, leg, (4, 1, 5), (x - 2, 0, -1), "orange_terracotta", [("white_terracotta", 1)], rate=0.3, front=["oooo"], side=["ooooo"], K=K_)
    tb(m, s, "body", (12, 5, 11), (-6, 8.6, -5.5), "brown_terracotta", LEATHER, rate=0.3, front=["nnnnnnnnnnnn", "nnnnnbbnnnnn", "nnnnnbbnnnnn", "nnnnnnnnnnnn", "dddddddddddd"], K=K_)
    tb(m, s, "head", (12, 11, 11), (-6, 13.6, -5.5), G, [("lime_concrete", 2), ("green_terracotta", 3), ("moss_block", 1)], rate=0.55, cell=1,
       side=["ggggggggggg", "ggggggggggg", "ggggggggggg", "ggggggggkgg", "gggggggwkgg", "ggggggggggg", "ggggggggggg", "ggggggggggg", "ggggggggggg", "ggggggggggg", "ggggggggggg"], K=K_)
    tb(m, s, "head", (3, 2, 3), (-1.5, 18, 5.2), "orange_terracotta", [("yellow_terracotta", 1)], rate=0.3)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        tb(m, s, arm, (2, 7, 6), (sd * 7 - 1, 9, -3), "green_terracotta", [(G, 1), ("moss_block", 1)], rate=0.4)
    for i, (x, z) in enumerate(((-3, -2), (0, 1), (3, -1), (1, -4))):
        m.c("head", "moss_block" if i % 2 else "lime_concrete", (x, 25, z), (2, 1.2, 2))
    m.c("head", "green_terracotta", (0, 26.4, 0), (0.6, 2, 0.6), (0, 0, 15))
    for i in range(10):
        a = i * 36
        m.c("head", "lime_concrete" if i % 2 else "green_terracotta", (math.cos(math.radians(a)) * 6.2, 14 + (i % 3) * 3, math.sin(math.radians(a)) * 5.8), (1.2, 1.6, 1.2), (0, -a, 20))
    m.attacks = {"leap": "lunge", "shockwave": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("old_blindman", "old_blindman", "<gradient:#6d4c41:#e0e0e0><bold>Old Hoodlum</bold></gradient>", "He Hears Every Step", entity="ZOMBIE", theme="bone", bar="WHITE",
        extra=["pull", "darkness"], recipe=mini_recipe("ASH", "ENTITY_VILLAGER_AMBIENT", "ENTITY_VILLAGER_DEATH", "white_wool", 0.6, "cast", "die_kneel"))
def old_blindman():
    """Picture 12: a tall hermit under a deep brown hood that hides his eyes, a long ragged grey beard
    down to his knees, a big nose poking out, a patched brown cloak, and a dark staff with a gold band."""
    m = Model("old_blindman", "biped", 1.6)
    biped(m, hip=7, legx=1.8, neck=18, shoulder=17, armx=5.6)
    m.bone("staff", "armR", (-6, 8, 2))
    m.hold = {"staff": 0}
    m.bend = -40
    s = Sheet(256, 256)
    H = "brown_terracotta"
    CL = [("brown_concrete", 2), ("terracotta", 2), ("dark_oak_planks", 1)]
    B = [("white_wool", 2), ("light_gray_wool", 3), ("light_gray_terracotta", 1)]
    K_ = {"h": H, "d": "brown_concrete", "k": "black_concrete", "s": "pink_terracotta", "w": "white_wool", "g": "light_gray_wool", "t": "terracotta"}
    legs2(m, s, (3, 6, 3), 1.8, H, CL, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    tb(m, s, "body", (9, 11, 6), (-4.5, 6.5, -3), H, CL, rate=0.35, D="brown_concrete")
    tb(m, s, "body", (11, 3, 7), (-5.5, 7, -3.5), H, CL, rate=0.4, front=["hhhhhhhhhhh", "h.hhh.hhh.h", "..h...h...."], K=K_)
    arms2(m, s, (3, 10, 3), 17, 6, H, CL, hand="pink_terracotta", hand_tones=[("terracotta", 1)])
    # hood: deep, the face in shadow
    tb(m, s, "head", (9, 10, 9), (-4.5, 17.5, -4.5), H, CL, rate=0.35, front=[
        "hhhhhhhhh", "hdddddddh", "hkkkkkkkh", "hkkkkkkkh", "hdssssdhh"[:9], "hdssssdh h".replace(" ", "")[:9], "hgsssssgh", "hwwwwwwwh", "hwwwwwwwh", "hwwwwwwwh"], K=K_)
    tb(m, s, "head", (2, 4, 2), (-1, 20, 4.4), "pink_terracotta", [("terracotta", 1)], rate=0.4)
    # the long beard
    tb(m, s, "head", (7, 12, 2), (-3.5, 6.6, 3.4), "light_gray_wool", B, rate=0.45, cell=1,
       front=["wwwwwww", "wgwwgww", "wwwwwww", "gwwgwwg", "wwwwwww", "wgwwwgw", "wwwwwww", "gwgwwgw", ".wwwww.", ".wgwgw.", "..www..", "..w.w.."], K=K_)
    limb(m, "staff", "dark_oak_log", (-6, -6, 3), [(30, 1.4, (0, 0, 0))])
    m.c("staff", "gold_block", (-6, 4, 3), (1.8, 1.6, 1.8))
    m.c("staff", "brown_concrete", (-6, 24, 3), (2, 2, 2))
    m.attacks = {"pull": "cast", "darkness": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("garden_gnome", "garden_gnome", "<gradient:#c62828:#69f0ae><bold>Mister Pebbles</bold></gradient>", "The Gnome Who Bit Back", entity="ZOMBIE", theme="nature", bar="RED",
        extra=["leap", "volley"], recipe=mini_recipe("HAPPY_VILLAGER", "ENTITY_VILLAGER_NO", "ENTITY_VILLAGER_DEATH", "red_wool", 1.4))
def garden_gnome():
    """Picture 13: a villager gnome with a lumpy red hat, a long nose, bright green eyes, a white beard,
    a teal shirt and a glowing emerald buckle on his belt."""
    m = Model("garden_gnome", "biped", 1.6)
    biped(m, hip=6, legx=2, neck=16, shoulder=15, armx=5.6)
    m.bone("hat", "head", (0, 25, 0))
    s = Sheet(256, 256)
    R = "red_concrete"
    K_ = {"r": R, "s": "pink_terracotta", "q": "terracotta", "w": "white_wool", "g": "light_gray_wool", "e": "lime_concrete", "k": "black_concrete",
          "c": "cyan_terracotta", "b": "brown_terracotta", "x": "emerald_block", "n": "brown_concrete"}
    legs2(m, s, (3, 5, 3), 2, "brown_terracotta", LEATHER, boot="dark_oak_planks", boot_tones=[("brown_concrete", 1)])
    tb(m, s, "body", (9, 9, 6), (-4.5, 6.5, -3), "cyan_terracotta", [("light_blue_terracotta", 2), ("cyan_concrete", 1)], rate=0.3, front=[
        "ccccccccc", "ccccccccc", "ccccccccc", "ccccccccc", "ccccccccc", "nnnxxxnnn", "nnnx.xnnn", "nnnxxxnnn", "ccccccccc"], K=K_, lit={"emerald_block"})
    arms2(m, s, (3, 7, 3), 15, 6, "cyan_terracotta", [("light_blue_terracotta", 1)], hand="pink_terracotta", hand_tones=[("terracotta", 1)])
    tb(m, s, "head", (8, 8, 8), (-4, 15.5, -4), "pink_terracotta", [("terracotta", 1)], rate=0.15, front=[
        "ssssssss", "ssssssss", "wsessesw", "wseksekw"[:8], "wwssssww", "wwwwwwww", "wwwwwwww", "wwwwwwww"], K=K_, lit={"lime_concrete"})
    tb(m, s, "head", (2, 5, 3), (-1, 16, 3.6), "terracotta", [("pink_terracotta", 1), ("brown_terracotta", 1)], rate=0.4)
    tb(m, s, "head", (8, 5, 2), (-4, 11.6, 3), "white_wool", [("light_gray_wool", 1)], rate=0.4, cell=1)
    tb(m, s, "hat", (9, 3, 9), (-4.5, 23, -4.5), R, [("red_terracotta", 2), ("red_wool", 1)], rate=0.4)
    tb(m, s, "hat", (7, 4, 7), (-3.5, 26, -3.5), R, [("red_terracotta", 2), ("red_wool", 1)], rate=0.4)
    tb(m, s, "hat", (4, 4, 4), (-2, 30, -2.5), R, [("red_terracotta", 2)], rate=0.4)
    m.c("hat", "red_terracotta", (0.5, 35, -1), (2, 2, 2), (0, 0, -20))
    idle = {"length": 3.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"]["hat"] = {"rot": K((0, (0, 0, -6)), (1.5, (4, 0, 6)), (3.0, (0, 0, -6)))}
    m.anims = {"idle": idle}
    m.attacks = {"leap": "lunge", "volley": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("ring_frog", "ring_frog", "<gradient:#1b5e20:#c5e1a5><bold>Sir Croaksworth</bold></gradient>", "He Stands Up Straight", entity="ZOMBIE", theme="toxic", bar="GREEN",
        extra=["leap", "pull"], recipe=mini_recipe("ITEM_SLIME", "ENTITY_FROG_AMBIENT", "ENTITY_FROG_DEATH", "moss_block", 1.0))
def ring_frog():
    """Picture 14: a tall frog standing upright, mottled green all over, bulging eyes on top of a wide
    head, a pale wide mouth line, a pale belly, and long arms with webbed fingers."""
    m = Model("ring_frog", "biped", 1.6)
    biped(m, hip=8, legx=2.6, neck=18, shoulder=17, armx=6)
    m.bone("throat", "head", (0, 18.5, 3))
    s = Sheet(256, 256)
    G = "green_concrete"
    SK = [("lime_terracotta", 2), ("green_terracotta", 3), ("moss_block", 1), ("lime_concrete", 1)]
    K_ = {"g": G, "l": "lime_terracotta", "d": "green_terracotta", "k": "black_concrete", "y": "yellow_concrete", "w": "smooth_sandstone", "c": "lime_concrete"}
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2.6
        tb(m, s, leg, (4, 8, 4), (x - 2, 1.4, -2), G, SK, rate=0.45)
        tb(m, s, leg, (5, 1.4, 6), (x - 2.5, 0, -1.6), G, SK, rate=0.4, front=["d.d.d"], K=K_)
    tb(m, s, "body", (10, 11, 7), (-5, 8.5, -3.5), G, SK, rate=0.45, front=[
        "gggggggggg", "ggwwwwwwgg", "gwwwwwwwwg", "gwwlwwlwwg", "gwwwwwwwwg", "gwwwlwwwwg", "gwwwwwwwwg", "ggwwwwwwgg", "gggggggggg", "gggggggggg", "gggggggggg"], K=K_)
    arms2(m, s, (3, 11, 3), 18, 6.5, G, SK, hand=G, hand_tones=SK, hand_size=(4, 2, 4))
    for sd in (1, -1):
        for f in (-1, 0, 1):
            m.c("armL" if sd > 0 else "armR", "lime_terracotta", (sd * 6.5 + f * 1.3, 4.2, 1.6), (0.8, 2, 0.8))
    tb(m, s, "head", (11, 6, 10), (-5.5, 18.5, -4.5), G, SK, rate=0.45, front=[
        "ggggggggggg", "ggggggggggg", "ggggggggggg", "lwwwwwwwwwl", "gdddddddddg", "ggggggggggg"], K=K_)
    tb(m, s, "throat", (7, 2, 4), (-3.5, 17, 1.5), "smooth_sandstone", [("lime_terracotta", 1)], rate=0.3)
    for sd in (1, -1):
        tb(m, s, "head", (4, 4, 4), (sd * 3.4 - 2, 23.4, 0), G, SK, rate=0.4, front=["gggg", "gykg", "gkkg", "gggg"], side=["gggg", "gggg", "gggg", "gggg"], K=K_)
    idle = {"length": 3.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"]["throat"] = {"scl": K((0, (1, 1, 1)), (0.3, (1.3, 1.5, 1.4)), (0.6, (1, 1, 1)), (1.5, (1, 1, 1)), (1.8, (1.3, 1.5, 1.4)), (2.1, (1, 1, 1)), (3.0, (1, 1, 1)))}
    m.anims = {"idle": idle}
    m.attacks = {"leap": "lunge", "pull": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("fisher_duck", "cluck_rider", "<gradient:#ffffff:#ffb300><bold>Sir Clucks-a-Lot</bold></gradient>", "Brave in a Chicken Hat", entity="ZOMBIE", theme="earth", bar="WHITE",
        minion="CHICKEN", extra=["minions", "leap"], recipe=mini_recipe("CLOUD", "ENTITY_CHICKEN_AMBIENT", "ENTITY_CHICKEN_DEATH", "white_wool", 1.2))
def cluck_rider():
    """Picture 15: a zombie in a teal shirt wearing a chicken-head mask, white feathers, an orange beak
    and a red wattle, with a stuffed chicken body strapped to its belly as if riding it."""
    m = Model("cluck_rider", "biped", 1.6)
    biped(m, hip=7, legx=2, neck=17, shoulder=16, armx=6)
    m.bone("comb", "head", (0, 26, 0))
    s = Sheet(256, 256)
    Z_ = "green_terracotta"
    ZS = [("lime_terracotta", 1), ("green_concrete", 1)]
    K_ = {"w": "white_wool", "g": "light_gray_wool", "o": "orange_concrete", "y": "yellow_terracotta", "r": "red_concrete", "k": "black_concrete", "c": "cyan_concrete", "z": Z_}
    legs2(m, s, (3, 6, 3), 2, "blue_terracotta", [("light_blue_terracotta", 1), ("blue_concrete", 1)], boot="gray_concrete", boot_tones=[("gray_terracotta", 1)])
    tb(m, s, "body", (9, 10, 6), (-4.5, 7, -3), "cyan_concrete", [("cyan_terracotta", 2), ("light_blue_terracotta", 1)], rate=0.3)
    # the stuffed chicken on the belly
    tb(m, s, "body", (7, 6, 4), (-3.5, 7.6, 2.6), "white_wool", [("light_gray_wool", 1)], rate=0.3, cell=1)
    tb(m, s, "body", (3, 2, 3), (-1.5, 9, 6.4), "yellow_terracotta", [("orange_terracotta", 1)], rate=0.3)
    for sd in (1, -1):
        m.c("body", "yellow_terracotta", (sd * 1.6, 6.6, 5.4), (0.6, 2, 0.6))
    arms2(m, s, (3, 9, 3), 16, 6, "white_wool", [("light_gray_wool", 1)], hand=Z_, hand_tones=ZS)
    # zombie face under the mask
    tb(m, s, "head", (8, 4, 8), (-4, 17, -4), Z_, ZS, rate=0.3, front=["zzzzzzzz", "zkzzzzkz", "zzzzzzzz", "zzzzzzzz"], K=K_)
    # the chicken mask: white head with eyes, big beak and the wattle
    tb(m, s, "head", (9, 7, 9), (-4.5, 21, -4.5), "white_wool", [("light_gray_wool", 1), ("white_concrete", 1)], rate=0.35, cell=1,
       front=["wwwwwwwww", "wwwwwwwww", "wkwwwwwkw", "wkwwwwwkw", "wwwwwwwww", "wwwwwwwww", "ggggggggg"], K=K_)
    tb(m, s, "head", (6, 2, 4), (-3, 23, 4.4), "orange_terracotta", [("yellow_terracotta", 2)], rate=0.4)
    tb(m, s, "head", (6, 1.4, 3), (-3, 21.6, 4.4), "yellow_terracotta", [("orange_terracotta", 1)], rate=0.3)
    tb(m, s, "head", (2, 3, 1), (-1, 19, 5.6), "red_concrete", [("red_terracotta", 1)], rate=0.3)
    tb(m, s, "comb", (2, 3, 5), (-1, 28, -2), "red_concrete", [("red_terracotta", 1)], rate=0.3)
    idle = {"length": 2.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"]["head"] = {"rot": K((0, Z), (0.2, (0, 0, 0)), (0.3, (14, 0, 0)), (0.45, Z), (1.2, (0, 30, 0)), (1.3, (0, -20, 0)), (2.0, Z))}
    idle["bones"]["comb"] = {"rot": K((0, Z), (0.35, (-20, 0, 0)), (0.6, Z), (2.0, Z))}
    m.anims = {"idle": idle}
    m.attacks = {"minions": "roar", "leap": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("bog_orc", "bog_orc", "<gradient:#2e7d32:#e0e0e0><bold>Horngut</bold></gradient>", "Bully of the Swamp", entity="ZOMBIE", theme="toxic", bar="GREEN",
        extra=["charge", "shockwave"], recipe=mini_recipe("ITEM_SLIME", "ENTITY_RAVAGER_AMBIENT", "ENTITY_RAVAGER_DEATH", "mud", 1.2))
def bog_orc():
    """Picture 16: a dark green orc with two curved bone horns, a snarling grin of white teeth over a
    black beard, angry brows, a brown leather loincloth and thick arms."""
    m = Model("bog_orc", "biped", 1.6)
    biped(m, hip=8, legx=2.6, neck=19, shoulder=18, armx=7)
    s = Sheet(256, 256)
    G = "green_terracotta"
    SK = [("moss_block", 2), ("green_concrete", 1), ("gray_terracotta", 1)]
    K_ = {"g": G, "d": "gray_terracotta", "k": "black_concrete", "w": "white_concrete", "t": "white_terracotta", "n": "brown_terracotta", "b": "brown_concrete", "y": "yellow_concrete", "B": "black_wool"}
    legs2(m, s, (4, 8, 4), 2.6, G, SK, boot=G, boot_tones=SK)
    tb(m, s, "hips", (10, 5, 7), (-5, 6, -3.5), "brown_terracotta", LEATHER, rate=0.4, front=["bbbbbbbbbb", "nnnnnnnnnn", "nnnbnnnbnn", "nnnnnnnnn.", ".nnn..nnn."], K=K_)
    tb(m, s, "body", (11, 9, 7), (-5.5, 10, -3.5), G, SK, rate=0.4)
    arms2(m, s, (4, 10, 4), 19, 7.5, G, SK, hand=G, hand_tones=SK, hand_size=(5, 4, 5))
    for sd in (1, -1):
        tb(m, s, "armL" if sd > 0 else "armR", (5, 3, 5), (sd * 7.5 - 2.5, 17, -2.5), G, SK, rate=0.4)
    tb(m, s, "head", (9, 9, 8), (-4.5, 18.5, -4), G, SK, rate=0.35, front=[
        "ggggggggg", "gkkgggkkg", "ggkkgkkgg", "gyggggygg", "ggggggggg", "gktttttkg", "gtwtwtwtg", "gkBBBBBkg", "ggBBBBBgg"], K=K_)
    tb(m, s, "head", (5, 4, 2), (-2.5, 14.8, 3), "black_wool", [("gray_concrete", 1)], rate=0.3, front=["BBBBB", ".BBB.", ".BBB.", "..B.."], K=K_)
    for sd in (1, -1):
        limb(m, "head", "white_terracotta", (sd * 3.5, 27, 0), [(3, 1.8, (0, 0, -30 * sd)), (3, 1.4, (0, 0, -5 * sd)), (2.4, 1.0, (0, 0, 25 * sd))])
        tb(m, s, "head", (2, 2, 1), (sd * 5.4 - 1, 23, 0), G, SK, rot=(0, 0, -30 * sd), origin=(sd * 5, 24, 0))
    m.attacks = {"charge": "lunge", "shockwave": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


@remini("angry_goose", "angry_goose", "<gradient:#eceff1:#ff9800><bold>Honkus</bold></gradient>", "The Goose Who Owns This Bench", entity="ZOMBIE", theme="earth", bar="WHITE",
        extra=["charge", "leap"], recipe=mini_recipe("CLOUD", "ENTITY_PARROT_IMITATE_RAVAGER", "ENTITY_PARROT_DEATH", "white_wool", 1.4, "roar", "die_back"))
def angry_goose():
    """A big white goose with a long neck in four bending pieces that weave and dip as it hisses, a grey
    back, an orange beak with a black knob, angry eyes and wide orange feet."""
    m = Model("angry_goose", "biped", 1.8)
    biped(m, hip=7, legx=2, neck=14, shoulder=12, armx=5)
    m.bone("n1", "body", (0, 13, 4))
    m.bone("n2", "n1", (0, 16, 7))
    m.bone("n3", "n2", (0, 19, 8.5))
    m.bone("n4", "n3", (0, 22, 8))
    m.bone("tail", "body", (0, 11, -5))
    m.no_elbows = True
    s = Sheet(256, 256)
    W = [("white_wool", 3), ("white_concrete", 1), ("light_gray_wool", 1)]
    K_ = {"w": "white_wool", "g": "light_gray_wool", "o": "orange_concrete", "O": "orange_terracotta", "k": "black_concrete", "y": "yellow_concrete", "r": "red_concrete"}
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 2
        tb(m, s, leg, (1.4, 6, 1.4), (x - 0.7, 0.8, -0.7), "orange_terracotta", [("orange_concrete", 1)], rate=0.3)
        tb(m, s, leg, (4, 1, 5), (x - 2, 0, -1), "orange_concrete", [("orange_terracotta", 1)], rate=0.3, front=["O.O."], K=K_)
    tb(m, s, "body", (9, 7, 13), (-4.5, 7, -6), "white_wool", W, rate=0.35, cell=1)
    tb(m, s, "body", (10, 3, 10), (-5, 12, -6), "light_gray_wool", [("gray_wool", 1), ("white_wool", 1)], rate=0.4, cell=1)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        tb(m, s, arm, (1.4, 6, 9), (sd * 5 - 0.7, 8, -5), "light_gray_wool", [("gray_wool", 1)], rate=0.4, cell=1)
    tb(m, s, "tail", (6, 3, 4), (-3, 10, -9), "white_wool", W, rate=0.3, rot=(-30, 0, 0), origin=(0, 11, -5))
    for b, y, z, sz in (("n1", 13, 4.5, 3.6), ("n2", 16, 7, 3.2), ("n3", 19, 8.5, 3.0), ("n4", 22, 8, 3.0)):
        tb(m, s, b, (sz, 3.4, sz), (-sz / 2, y, z - sz / 2), "white_wool", W, rate=0.35, cell=1)
    tb(m, s, "n4", (5, 5, 6), (-2.5, 25, 5.5), "white_wool", W, rate=0.3, cell=1,
       side=["wwwwww", "wwwwgw", "wwkkkw", "wwwkyw", "wwwwww"], K=K_)
    tb(m, s, "n4", (3, 2, 4), (-1.5, 26, 11.5), "orange_concrete", [("orange_terracotta", 1)], rate=0.3)
    m.c("n4", "black_concrete", (0, 27.5, 12), (1.6, 1, 1.6))
    idle = {"length": 3.0, "loop": True, "bones": dict(anims.BIPED["idle"]["bones"])}
    idle["bones"].pop("head", None)
    idle["bones"].update({
        "n1": {"rot": K((0, (10, 0, 0)), (0.8, (24, -10, 0)), (1.6, (-6, 8, 0)), (2.3, (30, 0, 0)), (3.0, (10, 0, 0)))},
        "n2": {"rot": K((0, (-8, 0, 0)), (0.8, (12, -12, 0)), (1.6, (-10, 12, 0)), (2.3, (20, 0, 0)), (3.0, (-8, 0, 0)))},
        "n3": {"rot": K((0, (-6, 0, 0)), (0.8, (-14, -8, 0)), (1.6, (6, 10, 0)), (2.3, (-20, 0, 0)), (3.0, (-6, 0, 0)))},
        "n4": {"rot": K((0, (-4, 0, 0)), (0.8, (-18, 0, 0)), (1.6, (8, 0, 0)), (2.3, (-24, 0, 0)), (3.0, (-4, 0, 0)))},
        "tail": {"rot": K((0, (0, -14, 0)), (0.3, (0, 14, 0)), (0.6, (0, -14, 0)), (0.9, Z), (3.0, Z))},
    })
    m.anims = {"idle": idle}
    m.attacks = {"charge": "lunge", "leap": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m
