"""v16: models painted like Minecraft mob skins. The user's pictures are Blockbench mobs: a few boxes on a
strict one-pixel grid, every face painted pixel by pixel in two or three flat tones of one colour. Earlier
builds mixed odd fractional pieces, stuck-on patches and grainy powder blocks, which read as generated.

Rules here:
- one model unit is one skin pixel and every box has whole-pixel sizes and positions;
- every visible face carries a hand-drawn picture (skin.skinbox), one character per pixel;
- flat blocks only (m.flat), picked by their real texture colour, so the pixel pattern is what you see;
- features are part of the picture or whole-pixel boxes (a nose, tusks, a staff), never thin stickers."""
from build import Model
from skin import skinbox
from v14_studio import studio
from v14_kit import humanoid, standard_anims, idle_biped, wave, wave2, K, Z, attack, loop


def pix(id):
    return studio(id, revise=False)


def box(m, bone, lo, size, base, keys, **faces):
    """A whole-pixel box from its low corner and size, with a picture on each face given."""
    lo = [float(v) for v in lo]
    hi = [lo[i] + size[i] for i in range(3)]
    for f, rows in faces.items():
        w = size[0] if f in ("front", "back", "top", "bottom") else size[2]
        h = size[2] if f in ("top", "bottom") else size[1]
        assert len(rows) == h and all(len(r) == w for r in rows), (m.id, bone, f, len(rows), [len(r) for r in rows], (w, h))
    skinbox(m, bone, lo, hi, base, faces=faces, keys=keys, depth=0.06)


def sides(rows):
    """The same picture for the left and the right face (right is seen from the other side, so mirrored)."""
    return {"left": rows, "right": [r[::-1] for r in rows]}


# ------------------------------------------------------------------------------------------------ the hermit

@pix("old_blindman")
def old_blindman():
    """The hermit from the picture: one tall brown-hooded figure, a bare pink-brown forehead, a single black
    slit for eyes, a long villager nose resting on a grey beard that covers the whole front down to the hem,
    brown sleeves with bare hands, little brown boots, and a thick black staff with a gold band."""
    m = Model("old_blindman", "biped", 1.0)
    m.flat = True
    HOOD = "brown_terracotta"
    k = {"s": "terracotta", "p": "orange_terracotta", "K": "black_concrete", "g": "light_gray_concrete_powder", "c": "diorite",
         "a": "light_gray_wool", "b": HOOD, "l": "brown_concrete", "d": "black_terracotta", "B": "blackstone",
         "P": "polished_blackstone", "Y": "gold_block", "t": "terracotta", "r": "brown_concrete_powder"}
    humanoid(m, hip=3, legx=2, neck=15, shoulder=17, armx=6.5)
    # boots poking out under the robe
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x0 = 1 if sd > 0 else -4
        box(m, leg, (x0, 0, -2), (3, 3, 7), "terracotta", k,
            front=["ttt", "ttt", "ddd"], **sides(["ttttttt", "ttttttt", "ddddddd"]))
    # the robe (body): grey beard over the whole front, brown folds on the sides and back
    box(m, "body", (-5, 3, -4), (10, 12, 8), HOOD, k,
        front=["ggaggggagg",
               "ggaggggagg",
               "gggggagagg",
               "aggggagggg",
               "aggaggggga",
               "ggga ggagga".replace(" ", ""),
               "gggaggaggg",
               "agggggaggg",
               "aggaggggag",
               "gggaggagag",
               "bgbgagbggb",
               "bbbgbbbabb"],
        back=["bbblbbbbbb", "bbblbbblbb", "bbbbbbblbb", "blbbbbbbbb", "blbbblbbbb", "bbbbblbbbb",
              "bbbbbbbblb", "bblbbbbblb", "bblbbbbbbb", "bbbbblbbbb", "dbbbbbbbbd", "dddddddddd"],
        **sides(["bbblbbbb", "bblbbbbb", "bblbbblb", "bbbbbblb", "blbbbbbb", "blbbbbbb",
                 "bbbblbbb", "bbbblbbb", "bbbbbbbl", "blbbbbbl", "bbbbbbbb", "dddddddd"]))
    # the head inside the hood: forehead, eye slit, the top of the beard
    box(m, "head", (-5, 15, -4), (10, 10, 8), HOOD, k,
        front=["ssssssssss",
               "ssssssssss",
               "ssssssssss",
               "ssssssssss",
               "ssssssssss",
               "ssssssssss",
               "ssssssssss",
               "sKKKKKKKKs",
               "gggggggagg",
               "ggaggggagg"],
        back=["bbbbbbbbbb", "bblbbbblbb", "bbbbbbbbbb", "bbbbblbbbb", "blbbbbbbbb", "bbbbbbbblb",
              "bbbblbbbbb", "bbbbbbbbbb", "bblbbbbbbb", "bbbbbbblbb"],
        top=["bbbbbbbbbb", "bblbbbbbbb", "bbbbbblbbb", "bbbbbbbbbb", "blbbbbbbbb", "bbbbblbbbb", "bbbbbbbblb",
             "llllllllll"],
        **sides(["lbbbbbbb", "lbbbbbbb", "lbbbbblb", "lbblbbbb", "lbbbbbbb", "lbbbbbbb",
                 "lbbbblbb", "lbbbbbbb", "lblbbbbb", "lbbbbbbb"]))
    # the nose, resting on the beard
    box(m, "head", (-1, 11, 4), (3, 5, 2), "terracotta", k,
        front=["sss", "sss", "sss", "sss", "sss"], top=["sss", "sss"])
    # sleeves and hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x0 = 5 if sd > 0 else -8
        box(m, arm, (x0, 11, -2), (3, 7, 4), HOOD, k,
            front=["bbb", "blb", "bbb", "bbl", "bbb", "lll", "ddd"], back=["bbb", "bbb", "blb", "bbb", "bbb", "bbb", "ddd"],
            **sides(["bbbb", "blbb", "bbbb", "bbbl", "bbbb", "llll", "dddd"]))
        box(m, arm, (x0, 8, -1.5 + 0.5), (3, 3, 3), "terracotta", k,
            front=["sss", "sss", "sss"])
    # the staff in the right hand
    box(m, "armR", (-9, 0, 1), (2, 20, 2), "blackstone", k,
        front=["PP", "BB", "BP", "BB", "BB", "PB", "BB", "BB", "BP", "BB", "YY", "BB", "PB", "BB", "BB", "BP", "BB", "BB", "PB", "BB"],
        **sides(["PP", "BB", "PB", "BB", "BB", "BP", "BB", "BB", "PB", "BB", "YY", "BB", "BP", "BB", "BB", "PB", "BB", "BB", "BP", "BB"]))
    m.no_elbows = m.no_knees = True
    standard_anims(m, heavy=0.6, idle=idle_biped(4.4, 10, breath=0.02))
    m.attacks = {"pull": "cast", "darkness": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the ogre

@pix("brewgut")
def brewgut():
    """The ogre from the picture, kept as the tavern brute: a hunched square green head pushed forward over the
    chest, small white eyes under a heavy brow, a wide nose, two pale tusks over the lip and stubby ears; a
    white shirt under an open brown vest, a ragged white apron on a dark belt, mauve trousers, dark boots,
    puffed white sleeves over thick green forearms, and a wooden tankard in the right fist."""
    m = Model("brewgut", "biped", 1.6)
    m.flat = True
    k = {"G": "lime_terracotta", "g": "green_terracotta", "m": "lime_terracotta", "W": "white_concrete", "w": "white_concrete",
         "c": "white_concrete", "V": "brown_concrete", "v": "brown_terracotta", "u": "brown_concrete",
         "b": "black_terracotta", "K": "black_concrete", "P": "pink_terracotta", "T": "end_stone", "L": "light_gray_terracotta",
         "l": "brown_terracotta", "D": "gray_terracotta", "o": "spruce_planks", "O": "dark_oak_planks"}
    humanoid(m, hip=14, legx=3, neck=23, shoulder=25, armx=7)
    m.bone("mug", "armR", (-7, 12, 2))
    # boots and trousers
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x0 = 1 if sd > 0 else -5
        box(m, leg, (x0 - 0.5, 0, -2), (5, 3, 6), "gray_terracotta", k,
            front=["DDDDD", "DbDDD", "bbbbb"], top=["DDDDD"] * 6, **sides(["DDDDDD", "DDbDDD", "bbbbbb"]))
        box(m, leg, (x0, 3, -2), (4, 11, 4), "light_gray_terracotta", k,
            front=["LLLL", "LlLL", "LlLL", "LlLL", "LlLL", "LlLL", "LLLL", "LLLL", "LLlL", "LLlL", "LLlL"],
            back=["LLLL", "LLlL", "LLlL", "LLlL", "LLlL", "LLLL", "LLLL", "LlLL", "LlLL", "LlLL", "LLLL"],
            **sides(["LLLL", "LLlL", "LLlL", "LLlL", "LLLL", "LLLL", "lLLL", "lLLL", "lLLL", "LLLL", "LLLL"]))
    # the apron: a dark belt, white cloth, a ragged hem
    box(m, "hips", (-6, 10, -4), (12, 6, 8), "white_concrete", k,
        front=["bbbbbbbbbbbb", "WWWWwWWWWWcW", "WcWWWWWWwWWW", "WWWWWcWWWWWW", "WwWWWWWcWWWW", "cWcWcWWcWcWc"],
        back=["bbbbbbbbbbbb", "WWWWWWWWWWWW", "WWcWWWWWcWWW", "WWWWWwWWWWWW", "WWWWWWWWWWWW", "cWWcWcWWcWWc"],
        **sides(["bbbbbbbb", "WWWWWWWW", "WWcWWWWW", "WWWWWWcW", "WwWWWWWW", "WcWWcWWc"]))
    for x in (-5, -2, 2, 4):
        box(m, "hips", (x, 8, 3), (1, 2, 1), "white_concrete", k, front=["W", "c"])
    # chest: white shirt under an open brown vest
    box(m, "body", (-6, 15, -3), (12, 11, 6), "brown_concrete", k,
        front=["VVVVWWWWVVVV",
               "VuVVWWwWVVuV",
               "VVVVWWWWVVVV",
               "VvVVVWwVVVvV",
               "VVVVVWWVVVVV",
               "VVuVVWWVVuVV",
               "VVVVVWWVVVVV",
               "VvVVVWcVVVvV",
               "VVVVVVVVVVVV",
               "VVvVVVVVVvVV",
               "VVVVVVVVVVVV"],
        back=["VVVVVVVVVVVV", "VVuVVVVVVuVV", "VVVVVVVVVVVV", "VvVVVuVVVVvV", "VVVVVVVVVVVV", "VVVVvVVVVVVV",
              "VuVVVVVVuVVV", "VVVVVVVVVVVV", "VVvVVVVvVVVV", "VVVVVVVVVVVV", "VVVVVVVVVVVV"],
        top=["WWWWWWWWWWWW"] * 6,
        **sides(["WWWWWW", "WWwWWW", "VVVVVV", "VuVVVV", "VVVVVV", "VVVVuV", "VVVVVV", "VVvVVV", "VVVVVV", "VVVVVV", "VVVVVV"]))
    # the head, pushed forward and low between the shoulders
    box(m, "head", (-4, 22, 0), (8, 8, 8), "lime_terracotta", k,
        front=["GGGgGGmG",
               "GmGGGGGG",
               "GggGGggG",
               "GWKGGKWG",
               "GGGggGGG",
               "GgGGGGgG",
               "GbbbbPbG",
               "gGGGGGGg"],
        back=["GGmGGGGG", "GGGGgGGm", "mGGGGGGG", "GGGGGmGG", "GgGGGGGG", "GGGGGGgG", "GGmGGGGG", "gGGGGGGg"],
        top=["GGGmGGGG", "GmGGGGgG", "GGGGGGGG", "GGgGGmGG", "GGGGGGGG", "mGGGGGGm", "GGGGgGGG", "GGGGGGGG"],
        **sides(["GGGGGGmG", "GGmGGGGG", "GGGGGGGG", "GGGGgGGG", "GmGGGGGG", "GGGGGGgG", "GGGGGGGG", "ggggggGg"]))
    box(m, "head", (-1, 25, 8), (2, 2, 1), "lime_terracotta", k, front=["GG", "gg"])                     # nose
    for x in (-3, 2):
        box(m, "head", (x, 23, 8), (1, 1, 1), "end_stone", k)                                            # tusks
    for sd in (1, -1):
        box(m, "head", (4 if sd > 0 else -5, 26, 3), (1, 2, 2), "lime_terracotta", k)                 # ears
    # arms: puffed white sleeves, thick green forearms with darker knuckles
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x0 = 6 if sd > 0 else -11
        box(m, arm, (x0, 19, -2.5), (5, 7, 5), "white_concrete", k,
            front=["WWWWW", "WwWWW", "WWWcW", "WWWWW", "WcWWW", "WWWWw", "ccccc"],
            back=["WWWWW", "WWWWW", "WcWWW", "WWWWW", "WWWcW", "WWWWW", "ccccc"],
            **sides(["WWWWW", "WWWwW", "WcWWW", "WWWWW", "WWWWc", "WWWWW", "ccccc"]))
        box(m, arm, (x0 + 0.5, 10, -2), (4, 9, 4), "lime_terracotta", k,
            front=["GGGG", "GmGG", "GGGg", "GGGG", "gGGG", "GGmG", "GGGG", "gGgG", "gggg"],
            back=["GGGG", "GGGm", "GGGG", "GgGG", "GGGG", "mGGG", "GGGG", "GGGg", "gggg"],
            **sides(["GGGG", "GGmG", "GGGG", "gGGG", "GGGG", "GGGg", "GGGG", "GgGG", "gggg"]))
    # the tankard
    box(m, "mug", (-11, 6, 2), (4, 5, 4), "spruce_planks", k,
        front=["oooo", "OOOO", "oooo", "oooo", "OOOO"], top=["WWWW", "WwWW", "WWWW", "WWwW"],
        **sides(["oooo", "OOOO", "oooo", "oooo", "OOOO"]))
    m.no_elbows = m.no_knees = True
    swig = attack(1.6, 1.0, {
        "armR": {"rot": K((0, Z), (0.5, (-150, 0, 0)), (0.9, (-160, 0, 10)), (1.1, (-60, 0, 0)), (1.6, Z))},
        "head": {"rot": K((0, Z), (0.5, (-30, 0, 0)), (0.9, (-34, 0, 0)), (1.1, (14, 0, 0)), (1.6, Z))},
        "body": {"rot": K((0, Z), (0.5, (-10, 0, 0)), (1.0, (14, 0, 0)), (1.6, Z))}})
    standard_anims(m, heavy=1.2, extra={"swig": swig, "idle": idle_biped(4.0, 18)})
    m.attacks = {"slam": "slam", "charge": "lunge", "roar": "swig"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ the gnome elder

def bumps(m, bone, block, cells, d=0.5):
    """Voxel relief: single-pixel cubes standing proud of a face, like the picture's knobbly cloth and hat.
    cells = [(x, y, z, axis, sign)]: a 1x1 pixel at that corner, pushed out along axis."""
    for x, y, z, ax, sg in cells:
        lo, size = [x, y, z], [1, 1, 1]
        size[ax] = d
        if sg < 0: lo[ax] -= d
        box(m, bone, lo, size, block, {})


@pix("old_pip")
def old_pip():
    """The gnome elder from the picture, built as voxel art: a stepped red hat of knobbly cubes in three reds,
    a white fringe under it, little green eyes, a long brown villager nose over a chunky white beard, a teal
    tunic with knobbly two-tone cloth, a dark belt with a big glowing emerald buckle, and small brown boots."""
    m = Model("old_pip", "biped", 1.0)
    m.flat = True
    k = {"s": "white_terracotta", "S": "terracotta", "r": "red_concrete_powder", "R": "red_concrete", "q": "red_concrete",
         "W": "white_wool", "w": "white_concrete", "E": "lime_concrete", "K": "black_concrete", "n": "terracotta",
         "N": "brown_terracotta", "t": "oxidized_copper", "T": "prismarine", "d": "dark_prismarine", "b": "dark_oak_planks",
         "B": "black_terracotta", "e": "emerald_block"}
    humanoid(m, hip=4, legx=2, neck=13, shoulder=13, armx=6.5)
    m.bone("hat", "head", (0, 22, 0))
    m.bone("beard", "head", (0, 15, 4))
    # boots and legs
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x0 = 0.5 if sd > 0 else -3.5
        box(m, leg, (x0, 0, -1.5), (3, 2, 5), "black_terracotta", k)
        box(m, leg, (x0, 2, -1.5), (3, 3, 3), "dark_oak_planks", k)
    # tunic with a dark belt and the emerald buckle
    box(m, "body", (-5, 4, -3.5), (10, 9, 7), "oxidized_copper", k,
        front=["TTtttTttTT", "tTttdtttTt", "ttdtttTttd", "TtttttttdT", "tttTtdtttt", "BBBBBBBBBB", "dtttdttdtt", "tdttttdttd", "dddtddtddd"],
        back=["tttttttttt", "tttttttttt", "tttttttttt", "tttttttttt", "tttttttttt", "BBBBBBBBBB", "tttttttttt", "tttttttttt", "dddddddddd"],
        **sides(["tTttTtt", "ttdtttT", "Ttttdtt", "ttTtttt", "tdttTtd", "BBBBBBB", "ttdtttd", "dttdttt", "ddtdddd"]))
    bumps(m, "body", "prismarine", [(-4, 11, 3.5, 2, 1), (2, 12, 3.5, 2, 1), (-1, 10, 3.5, 2, 1), (3, 9, 3.5, 2, 1), (5, 10, 1, 0, 1), (-5, 11, -1, 0, -1)])
    box(m, "body", (-2, 7, 3.5), (4, 4, 0.6), "emerald_block", k, front=["eeee", "eKKe", "eKKe", "eeee"])
    # arms: teal sleeves, bare hands
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x0 = 5 if sd > 0 else -8
        box(m, arm, (x0, 7, -1.5), (3, 6, 3), "oxidized_copper", k,
            front=["TTt", "ttt", "tdt", "ttt", "ttd", "ddd"], **sides(["tTt", "ttt", "dtt", "ttt", "tdt", "ddd"]))
        box(m, arm, (x0, 5, -1.5), (3, 2, 3), "white_terracotta", k, front=["sss", "SSS"], **sides(["sss", "SSS"]))
    # the head: skin, a white fringe, green eyes
    box(m, "head", (-4, 13, -4), (8, 9, 8), "white_terracotta", k,
        front=["WWWWWWWW",
               "WWsssWWW",
               "WWsssssW",
               "sEwssEws",
               "ssssssss",
               "ssssssss",
               "SsssssSs",
               "ssssssss",
               "SSssssSS"],
        back=["WWWWWWWW", "WWWWWWWW", "WWWWWWWW", "WWWWWWWW", "WWWWWWWW", "WWWWwWWW", "WWWWWWWW", "WwWWWWwW", "WWWWWWWW"],
        **sides(["WWWWWWWW", "WWWWWWWW", "WWWWWWss", "WWWWWsss", "WWWWsssS", "WWWsssss", "WWsssSss", "WWssssss", "WWWSssss"]))
    # beard in chunky white voxels, the long nose resting on it
    box(m, "beard", (-4, 9, 4), (8, 6, 1), "white_wool", k,
        front=["WWWWWWWW", "WwWWWWwW", "WWWWWWWW", "wWWWWWWW", "WWWwWWWW", "WWWWWWWw"], top=["WWWWWWWW"], bottom=["WWWWWWWW"])
    box(m, "beard", (-3, 8, 4), (6, 1, 1), "white_wool", k)
    box(m, "beard", (-2, 7, 4), (4, 1, 1), "white_wool", k)
    for sd in (1, -1):
        box(m, "beard", (3 if sd > 0 else -4, 15, 4), (1, 3, 1), "white_wool", k)
        bumps(m, "beard", "white_concrete", [((2 if sd > 0 else -3), 13, 5, 2, 1)])
    box(m, "head", (-1, 13, 4), (2, 5, 3), "terracotta", k, front=["nn", "nn", "nn", "nn", "NN"], top=["nn", "nn", "nn"])
    # the stepped hat: five shrinking layers in three reds, with knobbly cubes on the steps
    layers = [(12, 2, 11), (10, 2, 9), (7, 2, 7), (4, 2, 4), (2, 1, 2)]
    y = 21.5
    pics = {12: ["rRrrqrrRrrqr", "qqrqqqrqqqrq"], 10: ["rrRrrrqrrR", "qrqqrqqqrq"], 7: ["RrrrRrr", "qqrqqqr"], 4: ["rRrr", "qqqr"], 2: ["rR"]}
    for w, h, d in layers:
        p = pics[w]
        box(m, "hat", (-w / 2, y, -d / 2 + 0.5), (w, h, d), "red_concrete_powder", k,
            front=p, back=[r[::-1] for r in p], **sides([(r * 2)[:d] for r in p]))
        y += h
    bumps(m, "hat", "red_concrete", [(-5, 22.5, 6, 2, 1), (2, 22.5, 6, 2, 1), (-3, 24.5, 5, 2, 1), (1, 26.5, 4, 2, 1), (6, 22.5, -2, 0, 1), (-6, 22.5, 1, 0, -1)])
    m.no_elbows = m.no_knees = True
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(3.0, 18, extra={"hat": {"rot": wave(2, 4, 3.0)}, "beard": {"rot": wave(0, 3, 1.5)}})})
    m.attacks = {"volley": "cast", "blink": "stomp"}
    m.melee = "swipe"
    return m
