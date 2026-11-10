"""v15: every older mini rebuilt by hand. The user found loose bits on the old ones (fur tufts scattered as
tilted cubes, stray props), so each mini here is drawn from scratch with the v14 kit: big clean shapes,
built faces, and only pieces that belong to something (a horn, a leaf, a strap). Tilted pieces only ever
come in joined chains (horns, leaves, ears), never on their own. Ids, attacks and abilities stay the same,
so servers keep their settings."""
from build import Model
from v14_studio import studio
from v14_kit import (legs, arms, humanoid, standard_anims, chain, B, C, MB, eye, teeth, brow, K, Z, wave, wave2,
                     attack, loop, idle_biped, walk_biped)


def mini(id):
    return studio(id, revise=False)


def side():
    return ((1, "L"), (-1, "R"))


# ------------------------------------------------------------------------------------------------ mandrake

@mini("mandrake")
def mandrake():
    """A pale knobbly root with a scrunched, screaming little face, rosy cheeks, root arms flung up, stubby
    root legs and a big fan of leaves on its head."""
    m = Model("mandrake", "biped", 1.0)
    SK, DK, LT = "white_terracotta", "terracotta", "smooth_sandstone"
    G, GL, GD = "green_concrete", "lime_concrete", "green_terracotta"
    humanoid(m, hip=4, legx=2.2, neck=9, shoulder=12, armx=5)
    m.bone("tuft", "head", (0, 17.5, 0))
    for sd, s in side():
        leg = "leg" + s
        B(m, leg, SK, (sd * 2.2 - 1.2, 1.0, -1.2), (2.4, 4.0, 2.4))
        B(m, leg, SK, (sd * 2.2 - 1.1, 0, -1.1), (2.2, 1.2, 3.6))
        B(m, leg, DK, (sd * 2.2 - 0.6, 0, 2.5), (1.2, 0.8, 0.9))
    # the root: a fat bulb, narrower at the bottom and the top
    B(m, "body", SK, (-3.6, 3.2, -3.2), (7.2, 1.0, 6.4))
    B(m, "body", SK, (-4.6, 4.2, -4.0), (9.2, 5.0, 8.0))
    B(m, "head", SK, (-5.0, 9.0, -4.4), (10.0, 6.8, 8.8))
    B(m, "head", SK, (-4.2, 15.8, -3.8), (8.4, 1.2, 7.6))
    B(m, "head", LT, (-2.8, 17.0, -2.6), (5.6, 0.6, 5.2))
    # knobbles and root lines, flush on the surface
    B(m, "body", SK, (4.6, 5.4, -1.2), (0.6, 1.8, 2.0))
    B(m, "head", SK, (-5.6, 10.4, 0.2), (0.6, 2.0, 2.2))
    B(m, "body", DK, (-2.6, 4.8, 4.0), (0.4, 2.6, 0.1))
    B(m, "body", DK, (1.8, 4.4, 4.0), (0.4, 1.8, 0.1))
    B(m, "head", DK, (3.4, 15.0, 4.4), (0.4, 1.6, 0.1))
    # face: squeezed-shut eyes under pinched brows, a wide screaming mouth, pink cheeks
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 2.3 - 1.1, 13.0, 4.4), (2.2, 0.7, 0.2))
        B(m, "head", "black_concrete", (sd * 2.3 - (1.1 if sd > 0 else -0.5), 13.6, 4.4), (0.6, 0.6, 0.2))
        brow(m, "head", sd * 2.3, 14.6, 4.4, 2.6, DK, tilt=-18 * sd, h=0.7, d=0.5)
        B(m, "head", "pink_terracotta", (sd * 3.5 - 0.9, 11.4, 4.4), (1.8, 1.0, 0.15))
    B(m, "head", "black_concrete", (-1.6, 9.6, 4.4), (3.2, 2.8, 0.25))
    B(m, "head", "black_concrete", (-1.1, 9.2, 4.4), (2.2, 0.4, 0.25))
    B(m, "head", "red_terracotta", (-1.1, 9.7, 4.6), (2.2, 1.2, 0.1))
    # leaves fanning from the crown
    B(m, "tuft", GD, (-1.2, 17.4, -1.2), (2.4, 1.2, 2.4))
    for rx, rz, n in ((-4, 0, 6.5), (24, 6, 5.5), (-28, -6, 5.5), (6, -32, 6.0), (6, 32, 6.0), (-10, -58, 4.5), (-10, 58, 4.5)):
        a = n * 0.45
        chain(m, "tuft", G, (0, 18.4, 0), [(a, (1.0, 1.0), (rx, 0, rz), GD), (n - a, (3.0, 0.6), (rx * 1.3, 0, rz * 1.25), G),
                                          (2.0, (2.0, 0.5), (rx * 1.6, 0, rz * 1.5), GL), (1.0, (0.9, 0.4), (rx * 1.8, 0, rz * 1.7), GL)])
    # root arms flung up and out, with a forked tip
    for sd, s in side():
        end = chain(m, "arm" + s, SK, (sd * 4.4, 12, 0), [(3.4, (2.2, 2.2), (0, 0, -58 * sd)), (3.0, (1.7, 1.7), (0, 0, -40 * sd)), (2.0, (1.3, 1.3), (0, 0, -20 * sd))])
        chain(m, "arm" + s, DK, end, [(1.6, (0.9, 0.9), (0, 0, -50 * sd))])
        chain(m, "arm" + s, DK, end, [(1.4, (0.8, 0.8), (0, 0, 10 * sd))])
    m.no_elbows = m.no_knees = True
    standard_anims(m, heavy=0.4, extra={"idle": idle_biped(2.4, 14, breath=0.05, extra={"tuft": {"rot": wave2((5, 0, 7), 2.4)}})})
    m.attacks = {"roar": "roar", "poison": "cast"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ apple crab

@mini("apple_crab")
def apple_crab():
    """A crab whose shell is a shiny red apple with a stalk and a leaf, two black eyes on stalks peeking over
    the front, big pale pink pincers and eight jointed legs."""
    m = Model("apple_crab", "spider", 1.0)
    R, RL, RD, P, PT = "red_concrete", "red_wool", "red_terracotta", "pink_terracotta", "white_terracotta"
    m.bone("body", "root", (0, 5, 0))
    m.bone("abdomen", "body", (0, 8, -4))
    m.bone("head", "body", (0, 9, 5))
    m.bone("fangL", "head", (4.6, 6, 4)); m.bone("fangR", "head", (-4.6, 6, 4))
    zs = (3.0, 1.0, -1.2, -3.4)
    for i, z in enumerate(zs, 1):
        m.bone("legL%d" % i, "body", (5.6, 6, z)); m.bone("legR%d" % i, "body", (-5.6, 6, z))
    # the apple
    B(m, "body", RD, (-5.0, 3.6, -4.6), (10, 0.8, 9.2))
    B(m, "body", R, (-6.0, 4.4, -5.4), (12, 7.6, 10.8))
    B(m, "body", R, (-6.6, 5.4, -4.4), (13.2, 5.6, 8.8))
    B(m, "body", RL, (-5.0, 5.4, -6.0), (10, 5.6, 12.0))
    B(m, "body", R, (-5.0, 12.0, -4.4), (10, 1.0, 8.8))
    B(m, "body", RD, (-1.4, 12.95, -1.4), (2.8, 0.1, 2.8))
    B(m, "body", "white_concrete", (2.0, 9.0, 6.02), (1.4, 1.6, 0.1), light=True)
    B(m, "body", "white_concrete", (3.6, 10.6, 6.02), (0.7, 0.7, 0.1), light=True)
    end = chain(m, "abdomen", "dark_oak_planks", (0, 12.8, 0), [(1.8, (0.9, 0.9), (-8, 0, -6)), (1.4, (0.8, 0.8), (-24, 0, -16))])
    chain(m, "abdomen", "lime_concrete", (0.2, 13.8, 0), [(2.4, (0.5, 2.2), (0, 0, -58)), (1.8, (0.5, 1.4), (0, 0, -80), "green_concrete")])
    # mouth under the front rim
    B(m, "head", "black_concrete", (-1.6, 5.6, 6.0), (3.2, 0.7, 0.15))
    # eyes on stalks
    for sd in (1, -1):
        B(m, "head", P, (sd * 2.2 - 0.5, 10.0, 5.9), (1.0, 3.6, 1.0))
        B(m, "head", "black_concrete", (sd * 2.2 - 1.1, 13.4, 5.3), (2.2, 2.2, 2.2))
        B(m, "head", "white_concrete", (sd * 2.2 + (0.2 if sd > 0 else -0.9), 14.6, 7.5), (0.7, 0.7, 0.1), light=True)
    # pincers: arm out to the side, forearm forward, a big claw with a top and a bottom finger
    MB(m, "fangL", P, (4.8, 5.0, 3.2), (3.0, 2.0, 2.0))
    MB(m, "fangL", P, (6.8, 5.0, 4.2), (2.0, 2.0, 3.6))
    MB(m, "fangL", P, (6.2, 4.2, 7.6), (3.4, 3.4, 3.6))
    MB(m, "fangL", P, (6.5, 6.0, 11.2), (2.8, 1.6, 2.8))
    MB(m, "fangL", P, (6.5, 4.2, 11.2), (2.8, 1.0, 2.2))
    MB(m, "fangL", PT, (6.5, 6.0, 14.0), (2.8, 1.2, 0.8))
    MB(m, "fangL", PT, (6.5, 4.2, 13.4), (2.8, 0.8, 0.8))
    # legs: up and out from the shell, then down to the ground
    for i, z in enumerate(zs, 1):
        rx = (18, 6, -6, -18)[i - 1]
        for sd, s in side():
            e = chain(m, "leg%s%d" % (s, i), P, (sd * 5.6, 6, z), [(3.6, (1.4, 1.4), (rx, 0, -58 * sd))])
            C(m, "leg%s%d" % (s, i), PT, e, (1.6, 1.6, 1.6))
            chain(m, "leg%s%d" % (s, i), P, e, [(7.6, (1.2, 1.2), (rx * 0.6, 0, -163 * sd))])
    m.anims = {
        "idle": loop(2.4, {
            "body": {"rot": wave(2, 2, 2.4), "pos": K((0, Z), (0.6, (0, -0.3, 0)), (1.2, Z), (1.8, (0, -0.3, 0)), (2.4, Z))},
            "head": {"rot": K((0, Z), (0.6, (0, 8, 0)), (1.2, Z), (1.8, (0, -8, 0)), (2.4, Z))},
            "abdomen": {"rot": wave(0, 3, 1.2)},
            "fangL": {"rot": K((0, Z), (0.3, (-12, 10, 0)), (0.5, Z), (1.4, Z), (1.6, (-12, 10, 0)), (1.8, Z), (2.4, Z))},
            "fangR": {"rot": K((0, Z), (0.9, Z), (1.1, (-12, -10, 0)), (1.3, Z), (2.4, Z))}}),
        "fang": attack(0.8, 0.4, {
            "fangL": {"rot": K((0, Z), (0.25, (-40, 30, 0)), (0.4, (10, -12, 0)), (0.55, (8, -10, 0)), (0.8, Z))},
            "fangR": {"rot": K((0, Z), (0.25, (-40, -30, 0)), (0.4, (10, 12, 0)), (0.55, (8, 10, 0)), (0.8, Z))},
            "body": {"rot": K((0, Z), (0.25, (-10, 0, 0)), (0.4, (10, 0, 0)), (0.8, Z))},
            "root": {"pos": K((0, Z), (0.25, (0, 0, -1)), (0.4, (0, 0, 2.5)), (0.8, Z))}}),
    }
    m.attacks = {"charge": "fang", "spikes": "fang"}
    m.melee = "fang"
    return m


# ------------------------------------------------------------------------------------------------ snapjaw

@mini("snapjaw")
def snapjaw():
    """A hungry flytrap rooted in a mossy clump: a thick stem in two parts, wide leaves, and a purple-spotted
    head that splits into a jaw full of white teeth, with two little angry yellow eyes."""
    m = Model("snapjaw", "biped", 1.0)
    P, PD, PS, G, GL = "purple_concrete", "purple_terracotta", "magenta_concrete", "green_concrete", "lime_concrete"
    m.bone("hips", "root", (0, 3, 0))
    m.bone("body", "hips", (0, 3.4, 0))
    m.bone("neck", "body", (0, 8.4, 0))
    m.bone("head", "neck", (0, 14, -3))
    m.bone("jaw", "head", (0, 14.6, -3.4))
    m.bone("armL", "hips", (1.6, 3.6, 0)); m.bone("armR", "hips", (-1.6, 3.6, 0))
    # the clump it grows from
    B(m, "hips", "coarse_dirt", (-5.6, 0, -5.6), (11.2, 0.8, 11.2))
    B(m, "hips", "moss_block", (-6.0, 0.8, -6.0), (12.0, 1.8, 12.0))
    B(m, "hips", "moss_block", (-4.4, 2.6, -4.4), (8.8, 0.9, 8.8))
    B(m, "hips", "cobblestone", (3.6, 2.6, 2.8), (1.8, 0.8, 1.6))
    B(m, "hips", "cobblestone", (-4.8, 2.6, -3.6), (1.4, 0.6, 1.4))
    # stem
    B(m, "body", G, (-1.5, 3.4, -1.5), (3.0, 5.2, 3.0))
    B(m, "body", GL, (-1.8, 8.0, -1.8), (3.6, 0.8, 3.6))
    B(m, "neck", G, (-1.3, 8.6, -1.3), (2.6, 4.6, 2.6))
    B(m, "neck", G, (-3.0, 12.8, -3.2), (6.0, 1.2, 6.0))
    for sd in (1, -1):
        B(m, "neck", GL, (sd * 3.0 - (1.6 if sd > 0 else 0), 12.8, -0.8), (1.6, 0.8, 1.6))
    # head: upper jaw with spots, red mouth, a row of teeth along the rim, little eyes on the front
    B(m, "head", P, (-5.0, 15.0, -4.0), (10, 4.6, 9.6))
    B(m, "head", P, (-4.4, 15.4, 5.6), (8.8, 3.8, 1.0))
    B(m, "head", P, (-4.2, 19.6, -3.4), (8.4, 0.9, 8.4))
    B(m, "head", "red_concrete", (-4.6, 14.9, -3.6), (9.2, 0.2, 9.6))
    for x, z, w in ((-3.0, 1.0, 1.8), (1.4, -1.6, 2.2), (2.2, 3.2, 1.4), (-1.6, -2.8, 1.4)):
        B(m, "head", PS, (x, 20.5, z), (w, 0.1, w))
    for sd in (1, -1):
        B(m, "head", PS, (sd * 5.0 - (0.1 if sd > 0 else 0), 16.4, 0.4), (0.1, 1.6, 1.6))
    teeth(m, "head", -4.0, 4.0, 15.0, 6.2, n=5, h=1.4, w=0.9, d=0.7)
    for sd in (1, -1):
        for z in (1.4, -1.2):
            B(m, "head", "white_concrete", (sd * 4.3 - 0.4, 13.8, z), (0.8, 1.2, 0.8))
        eye(m, "head", sd * 2.4, 18.0, 6.6, w=2.0, h=1.6, out=0.4, white="yellow_concrete", pw=0.9, ph=1.2)
        brow(m, "head", sd * 2.4, 19.2, 6.6, 2.6, PD, tilt=-22 * sd, h=0.7, d=0.6)
    # lower jaw
    B(m, "jaw", P, (-4.6, 12.0, -3.6), (9.2, 2.8, 9.6))
    B(m, "jaw", P, (-4.0, 12.4, 6.0), (8.0, 2.2, 0.8))
    B(m, "jaw", PD, (-4.0, 11.4, -3.0), (8.0, 0.6, 8.6))
    B(m, "jaw", "red_concrete", (-4.0, 14.8, -3.0), (8.0, 0.2, 8.8))
    teeth(m, "jaw", -3.4, 3.4, 14.8, 5.6, n=4, h=1.2, w=0.9, d=0.7, down=False)
    # leaves: two big ones that swat, two small ones fixed in the clump
    for sd, s in side():
        chain(m, "arm" + s, G, (sd * 1.6, 3.6, 0), [(3.4, (0.6, 3.0), (0, 0, -60 * sd)), (3.2, (0.6, 2.8), (0, 0, -76 * sd), GL),
                                                    (1.8, (0.5, 1.4), (0, 0, -96 * sd))])
    for rx in (62, -62):
        chain(m, "hips", G, (0, 3.4, 0.0), [(3.0, (2.4, 0.6), (rx, 0, 0)), (1.6, (1.4, 0.5), (rx * 1.3, 0, 0), GL)])
    m.no_elbows = m.no_knees = True
    snap = attack(0.9, 0.42, {
        "neck": {"rot": K((0, Z), (0.28, (-20, 0, 0)), (0.42, (24, 0, 0)), (0.6, (22, 0, 0)), (0.9, Z))},
        "body": {"rot": K((0, Z), (0.28, (-8, 0, 0)), (0.42, (8, 0, 0)), (0.9, Z))},
        "head": {"rot": K((0, Z), (0.28, (-26, 0, 0)), (0.42, (-10, 0, 0)), (0.9, Z))},
        "jaw": {"rot": K((0, Z), (0.28, (46, 0, 0)), (0.42, (0, 0, 0)), (0.5, (6, 0, 0)), (0.6, Z), (0.9, Z))}})
    sway = {"body": {"rot": wave2((3, 4, 4), 3.0)}, "neck": {"rot": wave2((4, 6, 3), 3.0, 0.3)},
            "head": {"rot": K((0, Z), (0.8, (0, 18, 0)), (1.4, (0, 18, 0)), (2.0, (0, -18, 0)), (2.6, (0, -18, 0)), (3.0, Z))},
            "jaw": {"rot": K((0, (16, 0, 0)), (0.4, (30, 0, 0)), (0.55, (4, 0, 0)), (1.6, (16, 0, 0)), (1.75, (28, 0, 0)), (1.9, (4, 0, 0)), (3.0, (16, 0, 0)))},
            "armL": {"rot": wave(2, 8, 3.0)}, "armR": {"rot": wave(2, 8, 3.0, 0.5)}}
    walk = loop(0.8, {"hips": {"rot": K((0, (0, 0, 5)), (0.4, (0, 0, -5)), (0.8, (0, 0, 5)))},
                      "neck": {"rot": K((0, (8, 0, -5)), (0.4, (8, 0, 5)), (0.8, (8, 0, -5)))},
                      "armL": {"rot": K((0, (0, 0, 12)), (0.4, (0, 0, -6)), (0.8, (0, 0, 12)))},
                      "armR": {"rot": K((0, (0, 0, 6)), (0.4, (0, 0, -12)), (0.8, (0, 0, 6)))}})
    standard_anims(m, heavy=0.4, idle=loop(3.0, sway), walk=walk, extra={"snap": snap})
    m.attacks = {"poison": "roar", "pull": "swipe"}
    m.melee = "snap"
    return m


# ------------------------------------------------------------------------------------------------ piggy farmer

@mini("piggy_farmer")
def piggy_farmer():
    """Farmer Trotter: a pink pig standing up in blue dungarees over a red shirt, a straw hat, a big snout,
    small grumpy eyes, floppy ears, muddy boots and a muddy shovel."""
    m = Model("piggy_farmer", "biped", 1.0)
    PK, PS, PD, BL, BD = "pink_wool", "pink_concrete", "pink_terracotta", "blue_concrete", "blue_terracotta"
    humanoid(m, hip=8, legx=2.3, neck=19, shoulder=18, armx=6.4)
    m.bone("hat", "head", (0, 27.4, 0))
    m.bone("earL", "head", (3.6, 27, 0.8)); m.bone("earR", "head", (-3.6, 27, 0.8))
    legs(m, 2.3, 8, 3.6, 3.6, BL, foot="brown_terracotta", foot_h=1.8, toe=0.8)
    for sd, s in side():
        B(m, "leg" + s, "mud", (sd * 2.3 - 1.0, 2.4, 1.85), (2.0, 1.6, 0.1))
        B(m, "leg" + s, "brown_concrete", (sd * 2.3 - 2.15, 1.8, -2.15), (4.3, 0.6, 4.3))
    B(m, "hips", BL, (-4.6, 6.4, -2.6), (9.2, 2.6, 5.2))
    # body: red shirt, dungaree bib with straps and buttons, a pocket
    B(m, "body", "red_concrete", (-5.0, 9.0, -3.0), (10.0, 9.4, 6.0))
    B(m, "body", BL, (-5.2, 8.4, -3.2), (10.4, 3.6, 6.4))
    B(m, "body", BL, (-3.6, 12.0, 2.9), (7.2, 4.6, 0.5))
    B(m, "body", BD, (-1.6, 12.6, 3.4), (3.2, 2.4, 0.12))
    for sd in (1, -1):
        B(m, "body", BL, (sd * 2.6 - 0.8, 16.6, -3.3), (1.6, 1.9, 6.6))
        B(m, "body", BL, (sd * 2.6 - 0.8, 12.0, -3.4), (1.6, 4.6, 0.3))
        B(m, "body", "gold_block", (sd * 2.6 - 0.5, 15.6, 3.4), (1.0, 1.0, 0.2), light=True)
    B(m, "body", "mud", (1.8, 9.0, 3.25), (2.2, 1.6, 0.1))
    # head
    B(m, "head", PK, (-5.0, 18.4, -4.6), (10, 9.0, 9.2))
    B(m, "head", PS, (-2.6, 19.4, 4.6), (5.2, 3.4, 2.0))
    for sd in (1, -1):
        B(m, "head", PD, (sd * 1.2 - 0.5, 20.4, 6.6), (1.0, 1.4, 0.1))
        B(m, "head", "black_concrete", (sd * 2.7 - 0.7, 23.2, 4.6), (1.4, 1.8, 0.2))
        B(m, "head", "white_concrete", (sd * 2.7 - (0.1 if sd > 0 else 0.6), 24.4, 4.8), (0.5, 0.5, 0.1), light=True)
        brow(m, "head", sd * 2.7, 25.3, 4.6, 2.6, PD, tilt=-14 * sd, h=0.7, d=0.5)
        B(m, "head", PS, (sd * 3.9 - 0.7, 21.2, 4.6), (1.4, 0.8, 0.12))
    B(m, "head", PD, (-1.6, 18.8, 4.6), (3.2, 0.5, 0.15))
    for sd, s in side():
        chain(m, "ear" + s, PK, (sd * 3.6, 27.0, 0.8), [(2.0, (3.0, 1.0), (40, 0, -30 * sd)), (2.0, (2.6, 0.8), (90, 0, -40 * sd))])
    # straw hat pushed back
    B(m, "hat", "hay_block", (-7.4, 27.0, -6.6), (14.8, 0.9, 13.4))
    B(m, "hat", "hay_block", (-4.6, 27.9, -4.6), (9.2, 3.4, 8.6))
    B(m, "hat", "brown_concrete", (-4.7, 27.9, -4.7), (9.4, 1.0, 8.8))
    B(m, "hat", "hay_block", (-4.0, 31.3, -4.0), (8.0, 0.4, 7.4))
    # arms: red sleeves rolled up, pink forearms, dark trotters
    arms(m, 6.4, 18, 3.0, 3.2, "red_concrete", PK, PK, 9, hand_h=2.2)
    for sd, s in side():
        B(m, "arm" + s, "white_concrete", (sd * 6.4 - 1.7, 13.0, -1.8), (3.4, 1.0, 3.6))
        B(m, "arm" + s, "brown_terracotta", (sd * 6.4 - 1.85, 7.9, -1.95), (3.7, 0.8, 3.9))
    # shovel through the right fist
    B(m, "armR", "spruce_planks", (-6.9, 2.6, 2.4), (1.0, 15.0, 1.0))
    B(m, "armR", "spruce_planks", (-7.6, 17.4, 2.3), (2.4, 0.9, 1.2))
    B(m, "armR", "iron_block", (-8.0, 0.6, 2.4), (3.2, 2.8, 0.9))
    B(m, "armR", "mud", (-8.05, 0.6, 2.35), (3.3, 1.1, 1.0))
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(3.4, 16, extra={"earL": {"rot": wave(0, 8, 1.7)}, "earR": {"rot": wave(0, 8, 1.7, 0.4)},
                                                                         "hat": {"rot": wave(2, 2, 3.4)}})})
    m.attacks = {"minions": "roar", "charge": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ goblin king

@mini("goblin_king")
def goblin_king():
    """King Snivel: a fat green goblin king, a gold crown slipping over one ear, long drooping ears, a big
    nose over a crooked grin, a purple cape with a white ermine collar, a gold belt with a ruby and a
    crooked sceptre."""
    m = Model("goblin_king", "biped", 1.0)
    SK, SD, PU, PUD = "lime_terracotta", "green_terracotta", "purple_concrete", "purple_terracotta"
    humanoid(m, hip=7, legx=2.6, neck=17, shoulder=16, armx=7.2)
    m.bone("cape", "body", (0, 17, -4.2))
    m.bone("earL", "head", (4.8, 21.5, 0)); m.bone("earR", "head", (-4.8, 21.5, 0))
    m.bone("crown", "head", (0, 25, 0))
    legs(m, 2.6, 7, 3.4, 3.6, "brown_concrete", foot=SK, foot_h=1.6, toe=1.4)
    for sd, s in side():
        B(m, "leg" + s, SD, (sd * 2.6 - 1.4, 0, 2.6), (2.8, 0.6, 1.4))
    # belly, belt, loincloth
    B(m, "body", SK, (-6.0, 7.4, -4.0), (12, 8.6, 8.2))
    B(m, "body", SK, (-5.4, 16.0, -3.6), (10.8, 1.2, 7.2))
    B(m, "body", SD, (-0.5, 11.6, 4.2), (1.0, 1.0, 0.1))
    B(m, "body", "gold_block", (-6.2, 7.6, -4.2), (12.4, 1.4, 8.6))
    B(m, "body", "gold_block", (-1.5, 7.2, 4.3), (3.0, 2.2, 0.4), light=True)
    B(m, "body", "redstone_block", (-0.7, 7.7, 4.65), (1.4, 1.2, 0.15), light=True)
    B(m, "hips", "brown_terracotta", (-2.6, 4.6, 3.8), (5.2, 3.0, 0.5))
    B(m, "hips", "brown_terracotta", (-4.8, 5.6, -3.4), (9.6, 2.0, 7.2))
    # cape with an ermine collar
    B(m, "cape", PU, (-6.6, 3.6, -5.4), (13.2, 13.0, 1.0))
    B(m, "cape", PUD, (-6.7, 3.4, -5.5), (13.4, 1.0, 1.2))
    B(m, "cape", "gold_block", (-6.7, 4.4, -5.5), (13.4, 0.4, 1.2))
    B(m, "body", "white_wool", (-6.6, 15.4, -5.0), (13.2, 2.4, 9.2))
    for x, z in ((-4.0, 4.2), (3.0, 4.2), (-0.6, 4.2)):
        B(m, "body", "black_wool", (x, 16.0, z), (0.8, 1.0, 0.1))
    # head
    B(m, "head", SK, (-5.0, 17.0, -4.4), (10, 8.0, 8.8))
    B(m, "head", SD, (-5.2, 22.0, 4.2), (10.4, 1.2, 1.0))
    for sd in (1, -1):
        eye(m, "head", sd * 2.4, 21.0, 4.4, w=2.6, h=1.8, out=0.4, white="yellow_concrete", pw=1.0, ph=1.4, look=(-0.4 * sd, 0))
    B(m, "head", SK, (-1.1, 18.8, 4.4), (2.2, 2.8, 2.0))
    B(m, "head", SK, (-0.8, 18.4, 6.4), (1.6, 1.6, 0.8))
    B(m, "head", "black_concrete", (-3.6, 17.6, 4.4), (7.2, 1.0, 0.2))
    for x, h in ((-3.0, 1.2), (-1.4, 0.8), (1.6, 1.3), (2.8, 0.7)):
        B(m, "head", "white_terracotta", (x, 18.6 - h, 4.5), (0.9, h, 0.3))
    B(m, "head", SD, (-3.0, 17.0, 4.3), (6.0, 0.6, 0.2))
    for sd, s in side():
        chain(m, "ear" + s, SK, (sd * 4.8, 21.6, 0), [(3.0, (2.6, 1.0), (0, 0, -82 * sd)), (2.8, (1.8, 0.8), (0, 0, -100 * sd)),
                                                     (1.6, (1.0, 0.6), (0, 0, -112 * sd), SD)])
    # the crown, slipped over his left ear
    tilt, o = (0, 0, -14), (0, 25, 0)
    B(m, "crown", "gold_block", (-3.6, 24.6, -3.4), (7.2, 2.0, 6.8), tilt, o)
    for x, z in ((-3.6, -3.4), (2.4, -3.4), (-3.6, 2.2), (2.4, 2.2), (-0.6, 2.2)):
        B(m, "crown", "gold_block", (x, 26.6, z), (1.2, 1.6, 1.2), tilt, o)
    B(m, "crown", "redstone_block", (-0.7, 25.0, 3.4), (1.4, 1.2, 0.2), tilt, o, light=True)
    B(m, "crown", "lapis_block", (-3.2, 25.2, 3.4), (1.0, 0.8, 0.2), tilt, o)
    B(m, "crown", "lapis_block", (2.2, 25.2, 3.4), (1.0, 0.8, 0.2), tilt, o)
    # arms and a crooked sceptre in the right hand
    arms(m, 7.2, 16, 3.2, 3.4, SK, SK, SK, 9.6, hand_h=2.6)
    for sd, s in side():
        B(m, "arm" + s, "gold_block", (sd * 7.2 - 1.6, 9.2, -1.6), (3.2, 0.8, 3.2))
    e = chain(m, "armR", "dark_oak_planks", (-7.2, 5.4, 1.2), [(3.8, (1.0, 1.0), (14, 0, 0)), (3.6, (1.0, 1.0), (-6, 0, 8)), (3.0, (1.0, 1.0), (16, 0, -6))])
    C(m, "armR", "gold_block", (e[0], e[1] + 1.0, e[2]), (2.4, 2.4, 2.4))
    C(m, "armR", "emerald_block", (e[0], e[1] + 1.0, e[2] + 1.25), (1.2, 1.2, 0.3), light=True)
    standard_anims(m, heavy=1.0, extra={"idle": idle_biped(3.6, 16, extra={"earL": {"rot": wave(2, 6, 1.8)}, "earR": {"rot": wave(2, 6, 1.8, 0.5)}})})
    m.attacks = {"minions": "roar", "volley": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ moss imp

@mini("moss_imp")
def moss_imp():
    """A little old imp grown over with moss: a round green body, leaf ears, twig horns, a red mushroom on
    top, glowing amber eyes over a toothy grin, a bark loincloth and long thin arms."""
    m = Model("moss_imp", "biped", 1.0)
    MO, SD, LF, LL = "moss_block", "green_terracotta", "green_concrete", "lime_concrete"
    humanoid(m, hip=5, legx=2.4, neck=10.4, shoulder=10.4, armx=5.6)
    m.bone("earL", "head", (5.2, 14, 0)); m.bone("earR", "head", (-5.2, 14, 0))
    m.bone("cap", "head", (0.6, 17.4, -2))
    legs(m, 2.4, 5, 2.6, 2.8, SD, foot=SD, foot_h=1.2, toe=1.0)
    B(m, "body", MO, (-4.2, 4.2, -3.8), (8.4, 0.8, 7.6))
    B(m, "body", MO, (-5.0, 5.0, -4.4), (10, 5.4, 8.8))
    B(m, "body", "spruce_log", (-5.2, 4.6, -4.6), (10.4, 1.8, 9.2))
    B(m, "body", "spruce_log", (-2.0, 2.8, 4.2), (4.0, 2.4, 0.6))
    B(m, "head", MO, (-5.2, 10.4, -4.6), (10.4, 6.2, 9.2))
    B(m, "head", MO, (-4.4, 16.6, -3.8), (8.8, 0.9, 7.6))
    # face
    for sd in (1, -1):
        B(m, "head", SD, (sd * 2.5 - 1.7, 12.3, 4.5), (3.4, 2.8, 0.2))
        eye(m, "head", sd * 2.5, 13.7, 4.6, w=2.6, h=2.2, out=0.4, white="orange_concrete", pupil="black_concrete", pw=0.8, ph=1.8, glow=True)
        brow(m, "head", sd * 2.5, 15.3, 4.6, 3.0, SD, tilt=-20 * sd, h=0.8, d=0.8)
    B(m, "head", "black_concrete", (-3.2, 10.9, 4.5), (6.4, 1.5, 0.2))
    teeth(m, "head", -2.8, 2.8, 12.4, 4.7, n=5, h=0.8, w=0.7, d=0.3)
    for sd in (1, -1):
        B(m, "head", "white_concrete", (sd * 2.2 - 0.35, 10.9, 4.7), (0.7, 0.8, 0.3))
    # leaf ears, twig horns and the mushroom
    for sd, s in side():
        chain(m, "ear" + s, LF, (sd * 5.2, 14, 0), [(3.0, (0.7, 3.4), (0, 0, -70 * sd)), (2.8, (0.6, 2.6), (0, 0, -50 * sd), LL), (1.4, (0.5, 1.2), (0, 0, -30 * sd))])
        chain(m, "head", "dark_oak_log", (sd * 2.8, 17.4, 1.4), [(1.8, (1.2, 1.2), (0, 0, -18 * sd)), (1.6, (0.9, 0.9), (-14, 0, -36 * sd)), (1.0, (0.6, 0.6), (-30, 0, -52 * sd))])
    B(m, "cap", "mushroom_stem", (-0.2, 17.4, -2.8), (1.6, 2.2, 1.6))
    B(m, "cap", "red_mushroom_block", (-1.6, 19.6, -4.2), (4.4, 1.6, 4.4))
    B(m, "cap", "red_mushroom_block", (-0.8, 21.2, -3.4), (2.8, 0.7, 2.8))
    # long thin arms with dark claws
    arms(m, 5.6, 10.4, 2.0, 2.2, MO, SD, SD, 8.0, hand_h=1.6)
    for sd, s in side():
        for z in (-0.6, 0.6):
            B(m, "arm" + s, "brown_terracotta", (sd * 5.6 - 0.35 + sd * 0.4, 0.9, z - 0.35), (0.7, 0.8, 0.7))
    standard_anims(m, heavy=0.5, extra={"idle": idle_biped(2.8, 16, breath=0.05, extra={"earL": {"rot": K((0, Z), (0.2, (0, 0, -14)), (0.4, Z), (2.8, Z))},
                                                                                  "earR": {"rot": K((0, Z), (1.4, Z), (1.6, (0, 0, 14)), (1.8, Z), (2.8, Z))},
                                                                                  "cap": {"rot": wave(2, 4, 2.8)}})})
    m.attacks = {"levitate": "cast", "pull": "swipe"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ baby minotaur

@mini("baby_minotaur")
def baby_minotaur():
    """Little Moo: a chubby baby minotaur with a big brown bull head, curved ivory horns, a pink muzzle with
    a gold nose ring, a shaggy fringe over big angry eyes, a tiny body in a leather kilt and dark hooves."""
    m = Model("baby_minotaur", "biped", 1.0)
    F, FD, FW, L, LD = "brown_concrete", "brown_terracotta", "brown_wool", "orange_terracotta", "dark_oak_planks"
    humanoid(m, hip=7, legx=2.4, neck=14.6, shoulder=14.4, armx=5.8)
    legs(m, 2.4, 7, 3.0, 3.2, F, foot="black_terracotta", foot_h=1.4, toe=0.4)
    for sd, s in side():
        B(m, "leg" + s, FD, (sd * 2.4 - 0.15, 0, 1.6), (0.3, 1.4, 0.75))
    # kilt and belt
    B(m, "hips", L, (-4.4, 4.2, -2.9), (8.8, 3.4, 5.8))
    B(m, "hips", LD, (-4.6, 6.8, -3.1), (9.2, 1.0, 6.2))
    B(m, "hips", "gold_block", (-1.0, 6.6, 3.0), (2.0, 1.4, 0.3), light=True)
    for x in (-3.4, 0.6):
        B(m, "hips", "brown_terracotta", (x, 4.2, 2.9), (0.4, 2.6, 0.1))
    # body
    B(m, "body", F, (-4.0, 7.6, -2.6), (8.0, 7.0, 5.2))
    B(m, "body", "terracotta", (-2.6, 8.6, 2.6), (5.2, 4.6, 0.2))
    B(m, "body", L, (1.4, 7.6, 2.65), (1.4, 7.0, 0.3))
    B(m, "body", L, (1.4, 7.6, -2.95), (1.4, 7.0, 0.3))
    arms(m, 5.8, 14.4, 2.6, 2.8, F, F, FD, 7.0, hand_h=2.0)
    # head
    B(m, "head", F, (-5.0, 14.4, -4.4), (10, 9.0, 8.8))
    B(m, "head", F, (-4.4, 23.4, -3.8), (8.8, 0.8, 7.6))
    B(m, "head", "pink_terracotta", (-3.0, 14.8, 4.4), (6.0, 4.0, 2.4))
    for sd in (1, -1):
        B(m, "head", FD, (sd * 1.4 - 0.5, 16.8, 6.8), (1.0, 1.0, 0.1))
        B(m, "head", "gold_block", (sd * 1.2 - 0.25, 14.6, 6.85), (0.5, 1.9, 0.5), light=True)
    B(m, "head", "gold_block", (-1.2, 14.2, 6.85), (2.4, 0.5, 0.5), light=True)
    for sd in (1, -1):
        eye(m, "head", sd * 2.6, 20.0, 4.4, w=2.4, h=2.4, out=0.4, pw=1.2, ph=1.4, look=(-0.3 * sd, -0.2))
        brow(m, "head", sd * 2.6, 21.5, 4.4, 2.8, FD, tilt=-20 * sd, h=0.8, d=0.8)
    # fringe
    B(m, "head", FW, (-4.6, 22.0, 4.2), (9.2, 1.8, 1.0))
    B(m, "head", FW, (-3.8, 21.4, 4.3), (2.2, 0.6, 0.9))
    B(m, "head", FW, (0.4, 21.5, 4.3), (2.6, 0.5, 0.9))
    B(m, "head", FW, (-3.0, 23.2, -2.0), (6.0, 1.2, 6.4))
    # ears and horns
    for sd in (1, -1):
        B(m, "head", F, (sd * 5.0 - (0 if sd > 0 else 2.4), 19.6, -0.8), (2.4, 1.4, 2.0))
        B(m, "head", "pink_terracotta", (sd * 5.0 - (-0.4 if sd > 0 else 2.0), 19.9, 1.15), (1.6, 0.8, 0.1))
        chain(m, "head", "bone_block", (sd * 4.6, 22.4, 0), [(2.4, (2.2, 2.2), (0, 0, -78 * sd)), (2.2, (1.7, 1.7), (0, 0, -34 * sd)),
                                                            (1.8, (1.2, 1.2), (10, 0, 6 * sd), "white_concrete")])
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(3.0, 14)})
    m.attacks = {"charge": "lunge", "quake": "stomp"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ boo twin

@mini("boo_twin_b")
def boo_twin_b():
    """Hoo, the younger Boo Twin: a small white ghost with tall oval eyes, a wobbly open mouth, pale blue
    cheeks, a wavy hem and both arms raised to scare."""
    m = Model("boo_twin_b", "float", 1.0)
    W, WS = "white_concrete", "light_gray_concrete"
    m.bone("core", "root", (0, 6, 0))
    m.bone("head", "core", (0, 12, 0))
    m.bone("armL", "core", (5.2, 10, 0)); m.bone("armR", "core", (-5.2, 10, 0))
    for i in (1, 2, 3): m.bone("ring%d" % i, "core", (0, 6, 0))
    B(m, "core", W, (-5.5, 4.0, -5.0), (11, 8.0, 10))
    B(m, "core", WS, (-5.0, 3.6, -4.5), (10, 0.4, 9))
    # wavy hem: three tails, the middle one shorter
    for x0, x1, low in ((-5.5, -2.0, 0.6), (-1.8, 1.8, 1.8), (2.0, 5.5, 0.0)):
        B(m, "core", W, (x0, low, -5.0), (x1 - x0, 4.0 - low, 10))
        B(m, "core", WS, (x0 + 0.2, low, -4.8), (x1 - x0 - 0.4, 0.4, 9.6))
    B(m, "head", W, (-5.0, 12.0, -4.5), (10, 4.0, 9))
    B(m, "head", W, (-4.4, 16.0, -3.9), (8.8, 1.4, 7.8))
    B(m, "head", W, (-3.2, 17.4, -2.8), (6.4, 0.7, 5.6))
    # face on the front plane
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 2.3 - 0.9, 10.2, 5.0), (1.8, 4.6, 0.2))
        B(m, "head", "black_concrete", (sd * 2.3 - 1.3, 11.0, 5.0), (2.6, 3.0, 0.2))
        B(m, "head", "white_concrete", (sd * 2.3 + 0.0, 13.4, 5.2), (0.7, 0.7, 0.1), light=True)
        B(m, "head", "light_blue_concrete", (sd * 3.8 - 0.8, 9.2, 5.0), (1.6, 0.8, 0.12))
    B(m, "head", "black_concrete", (-1.3, 6.8, 5.0), (2.6, 2.4, 0.2))
    B(m, "head", "black_concrete", (-0.9, 6.2, 5.0), (1.8, 0.6, 0.2))
    B(m, "head", "black_concrete", (-1.7, 7.4, 5.0), (0.4, 1.2, 0.2))
    B(m, "head", "pink_concrete", (-0.7, 6.5, 5.15), (1.4, 0.8, 0.1))
    for sd, s in side():
        e = chain(m, "arm" + s, W, (sd * 5.2, 9.6, 0.4), [(2.6, (2.8, 2.8), (30, 0, -70 * sd)), (2.4, (2.4, 2.4), (40, 0, -30 * sd))])
        C(m, "arm" + s, W, e, (2.4, 1.6, 2.4))
        for k in (-0.8, 0.8):
            C(m, "arm" + s, WS, (e[0] + k * 0.9, e[1] + 0.9, e[2] + 0.3), (0.7, 1.0, 0.7))
    # a little curl on top of the head
    chain(m, "head", W, (0.4, 18.0, -0.6), [(1.2, (1.6, 1.6), (0, 0, 0)), (1.2, (1.2, 1.2), (-40, 0, -30)), (1.0, (0.9, 0.9), (-100, 0, -50))])
    m.anims = {}
    m.attacks = {"darkness": "pulse", "blink": "spin", "dive": "dive"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ bark ape

@mini("bark_ape")
def bark_ape():
    """The Bark Ape, a cheeky jungle thief: shaggy brown fur, a pale heart-shaped face with a wide muzzle,
    big round ears, long arms that hang to its knuckles, short bowed legs and a curled tail."""
    m = Model("bark_ape", "biped", 1.0)
    F, FD, FC, PL = "brown_wool", "brown_terracotta", "terracotta", "white_terracotta"
    humanoid(m, hip=8, legx=2.6, neck=17, shoulder=16.6, armx=6.8, jaw=(0, 18.6, 4))
    m.bone("tail", "hips", (0, 8, -3))
    legs(m, 2.6, 8, 3.2, 3.4, F, foot=FD, foot_h=1.4, toe=1.2)
    B(m, "hips", F, (-4.6, 6.6, -2.8), (9.2, 2.4, 5.6))
    B(m, "body", F, (-5.2, 8.6, -3.4), (10.4, 8.2, 6.8))
    B(m, "body", F, (-4.4, 16.8, -3.0), (8.8, 1.2, 6.0))
    B(m, "body", FC, (-3.0, 9.6, 3.4), (6.0, 5.6, 0.3))
    B(m, "body", FD, (-5.4, 13.2, -3.6), (10.8, 3.4, 1.0))
    # head with a heart-shaped face and a muzzle on the jaw
    B(m, "head", F, (-4.6, 17.0, -4.2), (9.2, 8.2, 8.2))
    B(m, "head", F, (-3.8, 25.2, -3.4), (7.6, 0.8, 6.6))
    for sd in (1, -1):
        B(m, "head", PL, (sd * 1.9 - 1.8, 20.0, 4.0), (3.6, 3.4, 0.3))
        eye(m, "head", sd * 1.9, 21.6, 4.3, w=2.0, h=2.0, out=0.3, pw=1.1, ph=1.3, look=(-0.2 * sd, 0))
        B(m, "head", F, (sd * 4.6 - (0 if sd > 0 else 1.4), 19.6, -1.4), (1.4, 3.6, 3.2))
        B(m, "head", PL, (sd * 4.6 - (-0.2 if sd > 0 else 1.6), 20.2, 0.0), (1.4, 2.4, 1.6))
    B(m, "head", FD, (-4.2, 23.4, 4.0), (8.4, 1.2, 1.2))
    B(m, "head", PL, (-3.2, 18.6, 4.0), (6.4, 1.6, 2.4))
    B(m, "head", FD, (-1.4, 19.4, 6.4), (1.0, 0.6, 0.1)); B(m, "head", FD, (0.4, 19.4, 6.4), (1.0, 0.6, 0.1))
    B(m, "jaw", PL, (-3.0, 17.0, 4.0), (6.0, 1.6, 2.2))
    B(m, "jaw", "black_concrete", (-2.4, 18.4, 6.0), (4.8, 0.4, 0.3))
    # long arms with dark hands
    arms(m, 6.8, 16.6, 3.2, 3.4, F, F, FD, 13.0, hand_h=2.4)
    for sd, s in side():
        B(m, "arm" + s, PL, (sd * 6.8 - 1.4, 1.6, 1.85), (2.8, 1.4, 0.2))
    # curled tail
    chain(m, "tail", F, (0, 8, -2.8), [(3.0, (1.8, 1.8), (-100, 0, 0)), (3.4, (1.6, 1.6), (-40, 0, 0)), (2.6, (1.4, 1.4), (10, 0, 0)), (1.8, (1.2, 1.2), (70, 0, 0), FD)])
    standard_anims(m, heavy=0.9, extra={"idle": idle_biped(2.6, 22, extra={"tail": {"rot": wave(2, 10, 2.6)}})})
    m.attacks = {"leap": "lunge", "volley": "double", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ old blindman

@mini("old_blindman")
def old_blindman():
    """The Old Blindman: a tall hermit under a deep brown hood that hides his eyes in shadow, a big nose and
    a white moustache poking out, a long grey beard down to his belt, a patched brown cloak tied with a
    rope and a dark staff with a gold band."""
    m = Model("old_blindman", "biped", 1.0)
    CL, CD, HD = "brown_concrete", "brown_terracotta", "dark_oak_planks"
    humanoid(m, hip=10, legx=2.2, neck=21.6, shoulder=21, armx=5.8)
    m.bone("beard", "head", (0, 23, 4))
    m.bone("cape", "body", (0, 21, -3.4))
    legs(m, 2.2, 10, 3.6, 4.0, CD, foot="black_terracotta", foot_h=1.4, toe=0.6)
    B(m, "hips", CL, (-4.6, 7.0, -3.0), (9.2, 4.0, 6.0))
    B(m, "body", CL, (-4.6, 10.6, -3.0), (9.2, 11.0, 6.0))
    B(m, "body", "birch_planks", (-4.8, 13.4, -3.2), (9.6, 0.8, 6.4))
    B(m, "body", "birch_planks", (2.2, 11.4, 3.2), (0.8, 2.0, 0.4))
    B(m, "body", "brown_wool", (-3.8, 16.0, 3.0), (2.6, 2.4, 0.1))
    B(m, "hips", "brown_wool", (1.0, 7.8, 3.0), (2.4, 2.2, 0.1))
    B(m, "cape", CD, (-5.4, 8.0, -4.2), (10.8, 13.6, 1.0))
    B(m, "cape", CD, (-5.6, 20.0, -4.2), (11.2, 2.0, 7.6))
    # the hood, its dark opening, the nose and moustache inside
    B(m, "head", CD, (-5.0, 21.4, -4.8), (10.0, 9.2, 9.4))
    B(m, "head", CD, (-3.6, 30.6, -4.2), (7.2, 1.2, 6.6))
    B(m, "head", CD, (-2.4, 30.0, -6.2), (4.8, 2.0, 1.6))
    B(m, "head", "black_concrete", (-3.6, 22.0, 4.6), (7.2, 6.4, 0.2))
    for sd in (1, -1):
        B(m, "head", CD, (sd * 4.3 - 0.7, 21.4, 4.6), (1.4, 7.4, 1.0))
    B(m, "head", CD, (-5.0, 28.0, 4.6), (10.0, 1.6, 1.2))
    B(m, "head", "white_terracotta", (-1.0, 23.4, 4.8), (2.0, 3.0, 2.0))
    B(m, "head", "white_terracotta", (-0.8, 23.0, 6.8), (1.6, 1.4, 0.4))
    B(m, "head", "white_wool", (-2.8, 22.2, 4.8), (5.6, 1.1, 1.4))
    # the beard in steps down the chest
    B(m, "beard", "light_gray_wool", (-3.4, 18.4, 3.6), (6.8, 4.0, 1.6))
    B(m, "beard", "light_gray_wool", (-3.0, 22.0, 4.7), (6.0, 0.6, 1.0))
    B(m, "beard", "light_gray_wool", (-2.8, 15.0, 3.4), (5.6, 3.4, 1.4))
    B(m, "beard", "light_gray_wool", (-2.0, 12.2, 3.2), (4.0, 2.8, 1.2))
    B(m, "beard", "white_wool", (-1.0, 10.8, 3.1), (2.0, 1.4, 1.0))
    # sleeves and staff
    arms(m, 5.8, 21, 2.8, 3.0, CL, CL, "white_terracotta", 9.0, hand_h=2.2)
    for sd, s in side():
        B(m, "arm" + s, CD, (sd * 5.8 - 1.8, 12.4, -1.9), (3.6, 1.8, 3.8))
    B(m, "armR", HD, (-6.3, 1.0, 2.0), (1.1, 26.0, 1.1))
    B(m, "armR", "gold_block", (-6.5, 19.0, 1.8), (1.5, 1.2, 1.5), light=True)
    chain(m, "armR", HD, (-5.75, 27.0, 2.55), [(1.6, (1.4, 1.4), (0, 0, 20)), (1.4, (1.2, 1.2), (-30, 0, 60))])
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(4.4, 10, extra={"beard": {"rot": wave(0, 3, 2.2)}})})
    m.attacks = {"pull": "cast", "darkness": "roar", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ straw farmer

@mini("straw_farmer")
def straw_farmer():
    """Farmer Grimbly, an illager of the wheat field: grey skin, the long illager nose under one heavy black
    brow, a wide straw hat, brown dungarees over a pale shirt, boots and an iron pitchfork."""
    m = Model("straw_farmer", "biped", 1.0)
    SK, DU, DD, SH = "light_gray_concrete", "brown_concrete", "brown_terracotta", "white_terracotta"
    humanoid(m, hip=10, legx=2.2, neck=21, shoulder=20.6, armx=5.6)
    m.bone("hat", "head", (0, 30, 0))
    legs(m, 2.2, 10, 3.4, 3.6, DU, foot="black_terracotta", foot_h=1.6, toe=0.6)
    B(m, "hips", DU, (-4.4, 8.6, -2.6), (8.8, 2.6, 5.2))
    B(m, "body", SH, (-4.4, 11.0, -2.6), (8.8, 10.0, 5.2))
    B(m, "body", DU, (-4.6, 10.4, -2.8), (9.2, 3.4, 5.6))
    B(m, "body", DU, (-3.0, 13.8, 2.6), (6.0, 4.2, 0.4))
    for sd in (1, -1):
        B(m, "body", DU, (sd * 2.2 - 0.7, 18.0, -2.8), (1.4, 3.0, 5.6))
        B(m, "body", "iron_block", (sd * 2.2 - 0.45, 17.0, 3.0), (0.9, 0.9, 0.2))
    B(m, "body", DD, (-1.2, 14.6, 3.0), (2.4, 2.0, 0.1))
    # head: long face, nose, unibrow
    B(m, "head", SK, (-4.0, 21.0, -4.0), (8.0, 9.6, 8.0))
    B(m, "head", SK, (-1.0, 22.0, 4.0), (2.0, 4.0, 2.0))
    B(m, "head", "gray_concrete", (-3.6, 26.6, 4.0), (7.2, 1.2, 0.6))
    for sd in (1, -1):
        B(m, "head", "white_concrete", (sd * 2.0 - 1.0, 25.0, 4.0), (2.0, 1.4, 0.2))
        B(m, "head", "green_terracotta", (sd * 2.0 - (0.2 if sd > 0 else 0.8), 25.0, 4.1), (1.0, 1.4, 0.15))
    B(m, "head", "gray_concrete", (-2.0, 21.8, 4.0), (4.0, 0.5, 0.2))
    # straw hat
    B(m, "hat", "hay_block", (-7.6, 29.6, -7.6), (15.2, 0.9, 15.2))
    B(m, "hat", "hay_block", (-4.4, 30.5, -4.4), (8.8, 3.0, 8.8))
    B(m, "hat", "red_terracotta", (-4.5, 30.5, -4.5), (9.0, 0.9, 9.0))
    B(m, "hat", "hay_block", (-3.4, 33.5, -3.4), (6.8, 0.5, 6.8))
    arms(m, 5.6, 20.6, 2.8, 3.0, SH, SH, SK, 9.4, hand_h=2.2)
    # pitchfork
    B(m, "armR", "spruce_planks", (-6.1, 3.0, 2.0), (1.0, 20.0, 1.0))
    B(m, "armR", "iron_block", (-7.9, 23.0, 2.05), (4.6, 0.8, 0.9))
    for x in (-7.9, -6.05, -4.2):
        B(m, "armR", "iron_block", (x, 23.8, 2.1), (0.8, 3.6, 0.8))
    standard_anims(m, heavy=0.7, extra={"idle": idle_biped(4.0, 16, extra={"hat": {"rot": wave(2, 2, 4.0)}})})
    m.attacks = {"minions": "roar", "volley": "double", "charge": "lunge"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ gilded mimic

@mini("gilded_mimic")
def gilded_mimic():
    """The Gilded Mimic: a dark wood treasure chest banded in gold with a gold lock and a red jewel. The lid
    hangs open on rows of white teeth, two yellow eyes glow in the dark inside and a long red tongue lolls
    out over the front."""
    m = Model("gilded_mimic", "slime", 1.0)
    WD, WL, GO = "dark_oak_planks", "spruce_planks", "gold_block"
    m.bone("body", "root", (0, 0, 0))
    m.bone("lid", "body", (0, 7.4, -6))
    m.bone("tongue", "body", (0, 7, 2))
    # the base
    B(m, "body", WD, (-7.0, 0.0, -6.0), (14, 7.4, 12))
    B(m, "body", GO, (-7.2, 0.0, -6.2), (14.4, 0.8, 12.4))
    B(m, "body", GO, (-7.2, 6.6, -6.2), (14.4, 0.8, 12.4))
    for x in (-4.6, 3.4):
        B(m, "body", GO, (x, 0.8, 5.9), (1.2, 5.8, 0.4)); B(m, "body", GO, (x, 0.8, -6.3), (1.2, 5.8, 0.4))
    for sd in (1, -1):
        B(m, "body", GO, (sd * 7.0 - (0 if sd > 0 else 0.4), 0.8, -1.0), (0.4, 5.8, 2.0))
    B(m, "body", "red_terracotta", (-6.4, 7.3, -5.4), (12.8, 0.15, 10.8))
    teeth(m, "body", -6.0, 6.0, 7.4, 5.0, n=7, h=1.4, w=1.0, d=0.8, down=False)
    B(m, "body", GO, (-1.6, 3.4, 6.0), (3.2, 3.4, 0.5), light=True)
    B(m, "body", "redstone_block", (-0.6, 4.4, 6.45), (1.2, 1.2, 0.15), light=True)
    B(m, "body", "black_concrete", (-0.25, 3.7, 6.45), (0.5, 0.6, 0.15))
    # the lid, opened, with teeth along its front edge and eyes under it
    B(m, "lid", WD, (-7.0, 7.4, -6.0), (14, 4.2, 12))
    B(m, "lid", WL, (-6.6, 11.6, -5.6), (13.2, 0.9, 11.2))
    B(m, "lid", GO, (-7.2, 7.4, -6.2), (14.4, 0.8, 12.4))
    for x in (-4.6, 3.4):
        B(m, "lid", GO, (x, 8.2, 5.9), (1.2, 3.4, 0.4)); B(m, "lid", GO, (x, 11.6, -5.0), (1.2, 1.0, 10.8))
    B(m, "lid", "red_terracotta", (-6.4, 7.35, -5.4), (12.8, 0.15, 10.8))
    teeth(m, "lid", -6.0, 6.0, 7.4, 5.0, n=6, h=1.6, w=1.1, d=0.8)
    for sd in (1, -1):
        B(m, "lid", "yellow_concrete", (sd * 2.6 - 0.9, 6.0, -4.6), (1.8, 1.0, 0.3), light=True)
    B(m, "body", "black_concrete", (-6.0, 3.0, -4.8), (12.0, 4.3, 0.2))
    # tongue
    chain(m, "tongue", "red_concrete", (0, 7.4, 1.0), [(3.6, (3.4, 0.8), (78, 0, 0)), (2.6, (3.0, 0.7), (120, 0, 0)), (1.8, (2.4, 0.6), (165, 0, 0), "pink_concrete")])
    m.anims = {
        "idle": loop(3.0, {
            "lid": {"rot": K((0, (-28, 0, 0)), (0.8, (-34, 0, 0)), (1.0, (-20, 0, 0)), (1.2, (-30, 0, 0)), (2.2, (-26, 0, 0)), (3.0, (-28, 0, 0)))},
            "tongue": {"rot": wave2((6, 8, 4), 1.5)},
            "body": {"scl": K((0, (1, 1, 1)), (0.75, (1.02, 0.97, 1.02)), (1.5, (1, 1, 1)), (2.25, (1.02, 0.97, 1.02)), (3.0, (1, 1, 1)))}}),
        "spit": attack(1.1, 0.6, {
            "lid": {"rot": K((0, (-28, 0, 0)), (0.4, (-70, 0, 0)), (0.6, (-80, 0, 0)), (0.8, (-10, 0, 0)), (1.1, (-28, 0, 0)))},
            "tongue": {"rot": K((0, Z), (0.4, (-40, 0, 0)), (0.6, (-60, 0, 0)), (1.1, Z))},
            "body": {"rot": K((0, Z), (0.4, (-8, 0, 0)), (0.6, (6, 0, 0)), (1.1, Z))}}),
    }
    m.attacks = {"orbs": "spit", "leap": "hop", "slam": "slam"}
    m.melee = "hop"
    return m


# ------------------------------------------------------------------------------------------------ mossling

def flower(m, bone, cx, top, cz, petal, centre, stem=2.0):
    B(m, bone, "green_concrete", (cx - 0.3, top, cz - 0.3), (0.6, stem, 0.6))
    y = top + stem
    B(m, bone, centre, (cx - 0.6, y, cz - 0.6), (1.2, 0.8, 1.2), light=True)
    for dx, dz in ((1.2, 0), (-1.2, 0), (0, 1.2), (0, -1.2)):
        B(m, bone, petal, (cx + dx - 0.6, y + 0.1, cz + dz - 0.6), (1.2, 0.6, 1.2))


@mini("mossling")
def mossling():
    """The Mossling, a round moss bush that hatched legs: a fat leafy ball with two big shiny black eyes, a
    small open mouth, a pink and a white flower on top, leafy arms and stubby brown legs."""
    m = Model("mossling", "biped", 1.0)
    MO, MD = "moss_block", "green_terracotta"
    humanoid(m, hip=4, legx=3.0, neck=4.4, shoulder=11, armx=7.2)
    legs(m, 3.0, 4, 2.8, 3.0, "dark_oak_log", foot="dark_oak_planks", foot_h=1.2, toe=0.8)
    B(m, "head", MO, (-6.0, 4.0, -5.4), (12, 1.0, 10.8))
    B(m, "head", MO, (-7.0, 5.0, -6.2), (14, 10.4, 12.4))
    B(m, "head", MO, (-6.0, 15.4, -5.4), (12, 1.2, 10.8))
    B(m, "head", MO, (-7.6, 6.4, -4.8), (15.2, 7.6, 9.6))
    B(m, "head", MO, (-5.6, 6.4, -6.8), (11.2, 7.6, 13.6))
    for sd in (1, -1):
        eye(m, "head", sd * 3.0, 11.0, 6.8, w=3.6, h=4.2, out=0.4, white="black_concrete", pupil="black_concrete", pw=3.6, ph=4.2, catch=False)
        B(m, "head", "white_concrete", (sd * 3.0 + (0.3 if sd > 0 else -1.5), 12.0, 7.25), (1.2, 1.2, 0.1), light=True)
        B(m, "head", "white_concrete", (sd * 3.0 + (-0.9 if sd > 0 else 0.4), 9.6, 7.25), (0.5, 0.5, 0.1), light=True)
        B(m, "head", "pink_terracotta", (sd * 5.0 - 0.8, 8.6, 6.8), (1.6, 0.8, 0.12))
    B(m, "head", "black_concrete", (-0.9, 7.4, 6.8), (1.8, 1.6, 0.2))
    B(m, "head", "red_terracotta", (-0.5, 7.5, 6.95), (1.0, 0.7, 0.1))
    B(m, "head", MD, (-6.0, 4.6, -5.4), (12, 0.4, 10.8))
    flower(m, "head", -2.0, 16.6, 0.8, "pink_concrete", "yellow_concrete")
    flower(m, "head", 2.4, 16.6, -1.6, "white_concrete", "orange_concrete", stem=1.4)
    for sd, s in side():
        chain(m, "arm" + s, MO, (sd * 7.2, 11, 0), [(2.8, (2.4, 2.6), (0, 0, -100 * sd)), (2.2, (2.0, 2.2), (0, 0, -128 * sd), "green_concrete"), (1.2, (1.4, 1.6), (0, 0, -150 * sd), "lime_concrete")])
    m.no_elbows = True
    standard_anims(m, heavy=0.5, extra={"idle": idle_biped(2.0, 10, breath=0.05)})
    m.attacks = {"leap": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ gnomes

def gnome(m, coat, coat_d, beard, beard_alt, hat_len=1.0, belt="black_concrete", tool=None):
    SKIN = "white_terracotta"
    humanoid(m, hip=6, legx=2.4, neck=16, shoulder=15.4, armx=6.0)
    m.bone("hat", "head", (0, 25.6, 0))
    m.bone("beard", "head", (0, 18, 4))
    legs(m, 2.4, 6, 3.2, 3.4, coat_d, foot="brown_terracotta", foot_h=1.8, toe=1.4)
    B(m, "hips", coat, (-4.6, 4.6, -3.0), (9.2, 2.4, 6.0))
    B(m, "body", coat, (-4.6, 6.6, -2.8), (9.2, 9.4, 5.6))
    B(m, "body", coat_d, (-4.8, 4.4, -3.0), (9.6, 1.2, 6.0))
    B(m, "body", belt, (-4.8, 8.0, -3.0), (9.6, 1.2, 6.0))
    B(m, "body", "gold_block", (-1.0, 7.8, 3.0), (2.0, 1.6, 0.3), light=True)
    B(m, "head", SKIN, (-4.4, 15.6, -3.8), (8.8, 9.0, 7.6))
    for sd in (1, -1):
        eye(m, "head", sd * 2.0, 21.2, 3.8, w=1.6, h=1.8, out=0.2, pw=1.0, ph=1.2)
        B(m, "head", beard, (sd * 2.0 - 1.4, 22.4, 3.9), (2.8, 0.9, 0.6))
        B(m, "head", "pink_terracotta", (sd * 3.2 - 0.8, 19.2, 3.8), (1.6, 1.0, 0.12))
        B(m, "head", beard, (sd * 4.4 - (0 if sd > 0 else 1.0), 15.6, -2.0), (1.0, 5.4, 5.4))
    B(m, "head", "pink_terracotta", (-1.3, 18.2, 3.8), (2.6, 2.6, 1.8))
    B(m, "head", "pink_concrete", (-0.5, 19.6, 5.55), (0.8, 0.6, 0.1))
    B(m, "beard", beard, (-4.4, 12.6, 3.4), (8.8, 5.8, 1.6))
    B(m, "beard", beard_alt, (-3.4, 10.4, 3.4), (6.8, 2.2, 1.4))
    B(m, "beard", beard, (-2.0, 9.2, 3.2), (4.0, 1.2, 1.2))
    B(m, "beard", beard, (-2.6, 17.4, 3.8), (5.2, 1.0, 1.3))
    B(m, "hat", "red_concrete", (-4.8, 24.4, -4.2), (9.6, 2.6, 8.4))
    B(m, "hat", "red_wool", (-5.0, 24.0, -4.4), (10.0, 1.0, 8.8))
    L = hat_len
    chain(m, "hat", "red_concrete", (0, 27.0, 0), [(4.0 * L, (7.6, 6.8), (-4, 0, 0)), (3.6 * L, (5.6, 5.0), (-12, 0, 0)), (3.0 * L, (3.8, 3.4), (-28, 0, 0), "red_wool"),
                                                 (2.4 * L, (2.4, 2.2), (-64, 0, 0)), (1.6 * L, (1.4, 1.3), (-104, 0, 0), "red_wool")])
    arms(m, 6.0, 15.4, 2.8, 3.0, coat, coat, SKIN, 8.4, hand_h=2.2)
    for sd, s in side():
        B(m, "arm" + s, coat_d, (sd * 6.0 - 1.6, 9.0, -1.7), (3.2, 1.0, 3.4))
    if tool == "shovel":
        B(m, "armR", "spruce_planks", (-6.5, 3.4, 1.7), (0.9, 11.0, 0.9))
        B(m, "armR", "iron_block", (-7.4, 1.0, 1.75), (2.7, 2.6, 0.8))


@mini("garden_gnome")
def garden_gnome():
    """Mister Pebbles, a garden gnome come to life: a tall red hat that flops over, a big white beard, a round
    pink nose, rosy cheeks, a blue coat with a black belt and a gold buckle, brown boots and a little shovel."""
    m = Model("garden_gnome", "biped", 1.0)
    gnome(m, "blue_concrete", "blue_terracotta", "white_wool", "white_concrete", tool="shovel")
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(3.0, 16, extra={"hat": {"rot": wave(2, 5, 3.0)}, "beard": {"rot": wave(0, 3, 1.5)}})})
    m.attacks = {"spikes": "slam", "heal": "roar"}
    m.melee = "swipe"
    return m


@mini("gnome_little")
def gnome_little():
    """Thimble, the little Gnome Brother: a tall red hat that flops, a checked white and grey beard, a green
    coat with a brown belt and a peach face with a round nose."""
    m = Model("gnome_little", "biped", 1.0)
    gnome(m, "green_concrete", "green_terracotta", "white_wool", "light_gray_wool", hat_len=1.2, belt="brown_concrete")
    for k, x in enumerate((-3.4, -1.0, 1.4)):
        B(m, "beard", "light_gray_wool", (x, 14.0 + (k % 2) * 1.6, 5.0), (1.6, 1.6, 0.1))
    standard_anims(m, heavy=0.5, extra={"idle": idle_biped(2.4, 20, extra={"hat": {"rot": wave(2, 7, 2.4)}})})
    m.attacks = {"leap": "lunge", "volley": "double"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ mushrooms

def mushroom(m, cap, cap_d, w, cap_h, stalk_h, face):
    STEM = "mushroom_stem"
    humanoid(m, hip=4, legx=2.2, neck=4 + stalk_h, shoulder=4 + stalk_h * 0.7, armx=w * 0.32 + 1.6)
    m.bone("cap", "head", (0, 4 + stalk_h, 0))
    legs(m, 2.2, 4, 2.8, 3.0, STEM, foot="white_terracotta", foot_h=1.2, toe=0.6)
    sw = w * 0.6
    B(m, "body", STEM, (-sw / 2, 4.0, -sw / 2 + 0.2), (sw, stalk_h * 0.55, sw - 0.4))
    B(m, "head", STEM, (-sw / 2 - 0.3, 4 + stalk_h * 0.55, -sw / 2), (sw + 0.6, stalk_h * 0.45, sw))
    y = 4 + stalk_h
    B(m, "cap", "white_terracotta", (-w / 2 + 0.6, y - 0.4, -w / 2 + 0.6), (w - 1.2, 0.4, w - 1.2))
    B(m, "cap", cap, (-w / 2, y, -w / 2), (w, cap_h, w))
    B(m, "cap", cap, (-w / 2 + 1.4, y + cap_h, -w / 2 + 1.4), (w - 2.8, 1.4, w - 2.8))
    B(m, "cap", cap_d, (-w / 2 + 3.2, y + cap_h + 1.4, -w / 2 + 3.2), (w - 6.4, 0.7, w - 6.4))
    zf = sw / 2 + 0.3
    fy = 4 + stalk_h * 0.62
    for sd in (1, -1):
        if face == "cross":
            B(m, "head", "black_concrete", (sd * 1.6 - 0.6, fy + 1.0, zf - 0.3), (1.2, 1.4, 0.4))
            brow(m, "head", sd * 1.6, fy + 2.4, zf - 0.3, 2.2, "brown_terracotta", tilt=-24 * sd, h=0.6, d=0.5)
        else:
            B(m, "head", "black_concrete", (sd * 1.6 - 0.6, fy + 1.0, zf - 0.3), (1.2, 1.6, 0.4))
            B(m, "head", "white_concrete", (sd * 1.6 - (0.0 if sd > 0 else 0.5), fy + 2.0, zf + 0.05), (0.5, 0.5, 0.1), light=True)
        B(m, "head", "pink_terracotta", (sd * 2.8 - 0.6, fy + 0.2, zf - 0.3), (1.2, 0.7, 0.35))
    if face == "cross":
        B(m, "head", "black_concrete", (-1.2, fy - 0.6, zf - 0.3), (2.4, 0.5, 0.4))
        B(m, "head", "black_concrete", (-1.6, fy - 1.0, zf - 0.3), (0.5, 0.5, 0.4)); B(m, "head", "black_concrete", (1.1, fy - 1.0, zf - 0.3), (0.5, 0.5, 0.4))
    else:
        B(m, "head", "black_concrete", (-1.2, fy - 0.8, zf - 0.3), (2.4, 1.0, 0.4))
        B(m, "head", "red_terracotta", (-0.7, fy - 0.8, zf - 0.1), (1.4, 0.5, 0.25))
    arms(m, sw / 2 + 0.9, 4 + stalk_h * 0.7, 1.8, 2.0, STEM, STEM, "white_terracotta", stalk_h * 0.45, hand_h=1.6)


@mini("cap_brothers")
def cap_brothers():
    """Toadstool, the grumpier mushroom: a stout pale stalk with a cross little face, a wide red cap with
    white spots, stubby legs, and his small brown-capped brother clinging to his back."""
    m = Model("cap_brothers", "biped", 1.0)
    mushroom(m, "red_mushroom_block", "red_concrete", 17, 3.0, 12, "cross")
    m.bone("rider", "body", (0, 9, -4))
    # little brother on his back: a brown cap, a stalk and two arms over the shoulders
    B(m, "rider", "mushroom_stem", (-1.8, 6.6, -7.6), (3.6, 4.6, 3.0))
    B(m, "rider", "brown_mushroom_block", (-3.2, 11.2, -9.0), (6.4, 1.6, 5.8))
    B(m, "rider", "brown_mushroom_block", (-2.2, 12.8, -8.2), (4.4, 0.8, 4.2))
    for sd in (1, -1):
        B(m, "rider", "black_concrete", (sd * 0.9 - 0.4, 9.4, -9.0), (0.8, 1.0, 0.3))
        B(m, "rider", "mushroom_stem", (sd * 2.2 - 0.6, 10.0, -5.6), (1.2, 1.0, 1.6))
    m.anims = None
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(3.2, 12, extra={"cap": {"rot": wave(2, 2, 3.2)}, "rider": {"rot": wave(2, 6, 1.6)}})})
    m.attacks = {"poison": "roar", "minions": "cast"}
    m.melee = "swipe"
    return m


@mini("cap_little")
def cap_little():
    """Puffball, the little brother: a short pale stalk with a round brown cap, a happy face with pink cheeks
    and quick little feet."""
    m = Model("cap_little", "biped", 1.0)
    mushroom(m, "brown_mushroom_block", "brown_terracotta", 13, 3.4, 9, "happy")
    # a fallen leaf stuck on his cap and a little satchel
    chain(m, "cap", "orange_terracotta", (2.0, 16.4, 1.0), [(2.0, (1.6, 0.4), (-80, 30, -20)), (1.4, (1.0, 0.3), (-95, 30, -30), "red_terracotta")])
    B(m, "body", "brown_terracotta", (-4.6, 5.4, -2.4), (1.0, 5.0, 0.6))
    B(m, "body", "spruce_planks", (-5.4, 4.8, -1.4), (1.6, 2.4, 2.8))
    standard_anims(m, heavy=0.4, extra={"idle": idle_biped(1.8, 16, breath=0.05, extra={"cap": {"rot": wave(2, 4, 1.8)}})})
    m.attacks = {"poison": "roar", "leap": "lunge"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ birds
# The goose, the mallard and Puffneck keep exactly two pupils tagged eye_pupil (CQuests looks for them).

def pupil(m, bone, x, y, z, side_face=True, h=1.0, w=1.0):
    if side_face:
        B(m, bone, "black_concrete", (x - 0.08, y, z), (0.16, h, w), g="eye_pupil")
    else:
        B(m, bone, "black_concrete", (x, y, z - 0.08), (w, h, 0.16), g="eye_pupil")


def waddle(length=0.7):
    q = length / 2
    return loop(length, {
        "legL": {"rot": K((0, (24, 0, 0)), (q, (-24, 0, 0)), (length, (24, 0, 0)))},
        "legR": {"rot": K((0, (-24, 0, 0)), (q, (24, 0, 0)), (length, (-24, 0, 0)))},
        "hips": {"rot": K((0, (0, 0, 7)), (q, (0, 0, -7)), (length, (0, 0, 7))), "pos": K((0, Z), (q / 2, (0, 0.6, 0)), (q, Z), (q * 1.5, (0, 0.6, 0)), (length, Z))},
        "body": {"rot": K((0, (0, 6, 0)), (q, (0, -6, 0)), (length, (0, 6, 0)))},
        "armL": {"rot": K((0, (0, 0, 4)), (q, (0, 0, 10)), (length, (0, 0, 4)))},
        "armR": {"rot": K((0, (0, 0, -10)), (q, (0, 0, -4)), (length, (0, 0, -10)))}})


@mini("angry_goose")
def angry_goose():
    """The Goose: a big white goose with a long neck in three bending pieces that weave and dip as it hisses,
    a grey back and wing tips, an orange beak with a black knob, angry eyes and wide orange feet."""
    m = Model("angry_goose", "biped", 1.0)
    W, GR, OR = "white_concrete", "light_gray_concrete", "orange_concrete"
    m.bone("hips", "root", (0, 4, 0))
    m.bone("legL", "hips", (2, 4, 0)); m.bone("legR", "hips", (-2, 4, 0))
    m.bone("body", "hips", (0, 6, 0))
    m.bone("neck", "body", (0, 9.4, 4.6)); m.bone("neck2", "neck", (0, 13.2, 5.0)); m.bone("neck3", "neck2", (0, 17, 5.2))
    m.bone("head", "neck3", (0, 20, 5.4))
    m.bone("jaw", "head", (0, 20.0, 8.2))
    m.bone("armL", "body", (4, 10, 0)); m.bone("armR", "body", (-4, 10, 0))
    m.bone("tail", "body", (0, 8.5, -6))
    for sd, s in side():
        B(m, "leg" + s, OR, (sd * 2 - 0.45, 0.6, -0.45), (0.9, 3.8, 0.9))
        B(m, "leg" + s, OR, (sd * 2 - 1.6, 0, -1.2), (3.2, 0.6, 4.0))
    B(m, "body", W, (-4.0, 4.2, -6.0), (8.0, 6.4, 11.0))
    B(m, "body", W, (-3.4, 4.8, 5.0), (6.8, 5.2, 1.4))
    B(m, "body", W, (-3.4, 3.6, -5.0), (6.8, 0.6, 9.0))
    B(m, "body", GR, (-3.6, 10.6, -5.6), (7.2, 0.7, 8.6))
    B(m, "tail", GR, (-2.4, 7.6, -8.2), (4.8, 2.6, 2.4))
    B(m, "tail", W, (-1.8, 9.6, -9.0), (3.6, 1.6, 1.4))
    for sd, s in side():
        B(m, "arm" + s, W, (sd * 4 - (0 if sd > 0 else 1.0), 5.4, -4.6), (1.0, 4.8, 8.4))
        B(m, "arm" + s, GR, (sd * 4 - (0 if sd > 0 else 1.0), 5.4, -6.6), (1.0, 3.4, 2.2))
        B(m, "arm" + s, "gray_concrete", (sd * 4 - (-0.05 if sd > 0 else 1.05), 5.4, -7.4), (1.0, 2.0, 1.0))
    B(m, "neck", W, (-1.3, 9.4, 3.6), (2.6, 4.2, 2.6))
    B(m, "neck2", W, (-1.2, 13.2, 3.8), (2.4, 4.2, 2.4))
    B(m, "neck3", W, (-1.2, 17.0, 4.0), (2.4, 3.4, 2.4))
    B(m, "head", W, (-1.8, 19.6, 3.6), (3.6, 3.2, 4.8))
    B(m, "head", OR, (-1.2, 20.4, 8.4), (2.4, 1.2, 3.0))
    B(m, "head", "black_concrete", (-0.8, 20.8, 7.6), (1.6, 1.4, 1.2))
    B(m, "jaw", OR, (-1.0, 19.6, 8.4), (2.0, 0.8, 2.8))
    for sd in (1, -1):
        pupil(m, "head", sd * 1.8, 21.0, 6.2)
        B(m, "head", "gray_concrete", (sd * 1.8 - 0.06, 22.0, 5.6), (0.12, 0.5, 1.8), (-18 * sd, 0, 0))
    m.no_elbows = m.no_knees = True
    weave = {"neck": {"rot": wave2((8, 10, 4), 2.0)}, "neck2": {"rot": wave2((10, 8, 0), 2.0, 0.2)}, "neck3": {"rot": wave2((-12, 6, 0), 2.0, 0.4)},
             "jaw": {"rot": K((0, Z), (0.4, (20, 0, 0)), (0.8, (20, 0, 0)), (1.0, Z), (2.0, Z))}, "tail": {"rot": wave(1, 12, 1.0)}}
    hiss = attack(1.0, 0.5, {
        "neck": {"rot": K((0, Z), (0.3, (-30, 0, 0)), (0.5, (60, 0, 0)), (0.7, (56, 0, 0)), (1.0, Z))},
        "neck2": {"rot": K((0, Z), (0.3, (-10, 0, 0)), (0.5, (14, 0, 0)), (1.0, Z))},
        "neck3": {"rot": K((0, Z), (0.3, (20, 0, 0)), (0.5, (-40, 0, 0)), (1.0, Z))},
        "jaw": {"rot": K((0, Z), (0.3, (34, 0, 0)), (0.5, (10, 0, 0)), (0.6, (30, 0, 0)), (1.0, Z))},
        "armL": {"rot": K((0, Z), (0.3, (0, 0, 70)), (0.5, (0, 0, 40)), (1.0, Z))}, "armR": {"rot": K((0, Z), (0.3, (0, 0, -70)), (0.5, (0, 0, -40)), (1.0, Z))},
        "root": {"pos": K((0, Z), (0.3, (0, 0, -1)), (0.5, (0, 0, 4)), (1.0, Z))}})
    standard_anims(m, heavy=0.5, idle=loop(2.0, weave), walk=waddle(), extra={"lunge": hiss})
    m.attacks = {"charge": "lunge", "leap": "lunge", "slam": "slam"}
    m.melee = "swipe"
    return m


@mini("mallard")
def mallard():
    """Sir Mallard, a chunky drake: a glossy green head, a broad yellow bill, a white collar ring, a chestnut
    breast, a grey body with a blue wing patch, a curl of black tail and orange feet."""
    m = Model("mallard", "biped", 1.0)
    GR, GD, OR = "light_gray_concrete", "gray_concrete", "orange_concrete"
    m.bone("hips", "root", (0, 3, 0))
    m.bone("legL", "hips", (2.2, 3, 1)); m.bone("legR", "hips", (-2.2, 3, 1))
    m.bone("body", "hips", (0, 4, 0))
    m.bone("neck", "body", (0, 10, 3.6))
    m.bone("head", "neck", (0, 12, 3.6))
    m.bone("jaw", "head", (0, 13.2, 8.2))
    m.bone("armL", "body", (5, 9, -1)); m.bone("armR", "body", (-5, 9, -1))
    m.bone("tail", "body", (0, 8, -6))
    for sd, s in side():
        B(m, "leg" + s, OR, (sd * 2.2 - 0.5, 0.6, 0.5), (1.0, 3.0, 1.0))
        B(m, "leg" + s, OR, (sd * 2.2 - 1.7, 0, -0.4), (3.4, 0.6, 4.2))
    B(m, "body", GR, (-5.0, 3.6, -6.0), (10, 7.0, 11.6))
    B(m, "body", GD, (-4.4, 10.6, -5.4), (8.8, 0.8, 8.0))
    B(m, "body", "brown_concrete", (-4.6, 4.4, 5.6), (9.2, 6.0, 1.4))
    B(m, "body", "white_concrete", (-4.4, 3.2, -5.4), (8.8, 0.4, 10.8))
    for sd, s in side():
        B(m, "arm" + s, GD, (sd * 5 - (0 if sd > 0 else 1.0), 5.0, -5.4), (1.0, 4.8, 9.0))
        B(m, "arm" + s, "blue_concrete", (sd * 5 - (-0.05 if sd > 0 else 1.05), 6.2, -3.4), (1.0, 1.6, 3.0))
        B(m, "arm" + s, "white_concrete", (sd * 5 - (-0.06 if sd > 0 else 1.06), 7.8, -3.4), (1.0, 0.4, 3.0))
        B(m, "arm" + s, "black_concrete", (sd * 5 - (0 if sd > 0 else 1.0), 5.0, -6.6), (1.0, 2.6, 1.2))
    B(m, "tail", "white_concrete", (-3.4, 5.6, -8.0), (6.8, 3.6, 2.0))
    B(m, "tail", "black_concrete", (-2.6, 6.4, -8.8), (5.2, 2.8, 1.0))
    chain(m, "tail", "black_concrete", (0, 9.0, -8.2), [(1.4, (1.2, 1.0), (-10, 0, 0)), (1.2, (1.0, 0.9), (40, 0, 0)), (1.0, (0.8, 0.8), (100, 0, 0))])
    B(m, "neck", "green_concrete", (-2.6, 10.0, 1.6), (5.2, 2.6, 4.6))
    B(m, "neck", "white_concrete", (-2.7, 10.4, 1.5), (5.4, 0.8, 4.8))
    B(m, "head", "green_concrete", (-3.0, 12.4, 1.4), (6.0, 5.6, 6.6))
    B(m, "head", "lime_terracotta", (-3.05, 15.2, 2.6), (6.1, 1.2, 3.0))
    B(m, "head", "yellow_concrete", (-2.0, 13.2, 8.0), (4.0, 1.6, 3.6))
    B(m, "head", "yellow_terracotta", (-0.6, 13.6, 11.5), (1.2, 0.9, 0.3))
    B(m, "jaw", "yellow_concrete", (-1.8, 12.6, 8.0), (3.6, 0.7, 3.2))
    for sd in (1, -1):
        pupil(m, "head", sd * 3.0, 15.0, 5.4, h=1.2, w=1.2)
        B(m, "head", "white_concrete", (sd * 3.06 - 0.06, 15.8, 6.2), (0.12, 0.4, 0.4), light=True)
    m.no_elbows = m.no_knees = True
    idle = loop(3.0, {"neck": {"rot": wave(0, 6, 3.0)}, "head": {"rot": K((0, Z), (0.8, (0, 26, 0)), (1.3, (0, 26, 0)), (1.8, (0, -26, 0)), (2.4, (0, -26, 0)), (3.0, Z))},
                      "tail": {"rot": wave(1, 14, 0.75)}, "body": {"rot": wave(2, 3, 3.0)},
                      "jaw": {"rot": K((0, Z), (2.4, Z), (2.5, (20, 0, 0)), (2.6, Z), (2.7, (20, 0, 0)), (2.8, Z), (3.0, Z))}})
    standard_anims(m, heavy=0.5, idle=idle, walk=waddle(0.8))
    m.attacks = {"minions": "roar", "charge": "lunge"}
    m.melee = "swipe"
    return m


@mini("puffneck")
def puffneck():
    """Puffneck, a tall stalk creature: two leaf feet, a long green neck with leaves, and a round white
    dandelion clock for a head with a little yellow face, sleepy eyes and a small smile set in it."""
    m = Model("puffneck", "biped", 1.0)
    G, GL, PF = "green_concrete", "lime_concrete", "white_wool"
    m.bone("hips", "root", (0, 2, 0))
    m.bone("legL", "hips", (1.6, 2, 0)); m.bone("legR", "hips", (-1.6, 2, 0))
    m.bone("body", "hips", (0, 2.4, 0))
    m.bone("neck", "body", (0, 8, 0))
    m.bone("head", "neck", (0, 14, 0))
    m.bone("jaw", "head", (0, 17, 5))
    m.bone("armL", "body", (1.2, 7, 0)); m.bone("armR", "body", (-1.2, 7, 0))
    for sd, s in side():
        B(m, "leg" + s, G, (sd * 1.6 - 0.6, 0.6, -0.6), (1.2, 1.8, 1.2))
        B(m, "leg" + s, GL, (sd * 1.6 - 1.4, 0, -1.4), (2.8, 0.6, 3.8))
    B(m, "hips", G, (-2.2, 1.8, -1.4), (4.4, 1.2, 2.8))
    B(m, "body", G, (-1.2, 2.6, -1.2), (2.4, 5.6, 2.4))
    B(m, "neck", G, (-1.0, 8.0, -1.0), (2.0, 6.4, 2.0))
    B(m, "neck", GL, (-1.3, 10.6, -1.3), (2.6, 0.7, 2.6))
    for sd, s in side():
        chain(m, "arm" + s, G, (sd * 1.2, 7, 0), [(2.4, (0.5, 2.0), (0, 0, -60 * sd)), (2.2, (0.4, 1.6), (0, 0, -82 * sd), GL), (1.0, (0.4, 0.8), (0, 0, -100 * sd))])
    # the clock: a round white puff in layers
    B(m, "head", PF, (-5.0, 15.0, -4.5), (10, 9.6, 9.0))
    B(m, "head", PF, (-5.8, 16.4, -3.4), (11.6, 6.8, 6.8))
    B(m, "head", PF, (-4.0, 16.4, -5.3), (8.0, 6.8, 10.6))
    B(m, "head", PF, (-3.6, 14.2, -3.2), (7.2, 0.8, 6.4))
    B(m, "head", PF, (-3.6, 24.6, -3.2), (7.2, 0.8, 6.4))
    B(m, "head", G, (-1.6, 13.6, -1.6), (3.2, 0.8, 3.2))
    for x, y in ((-4.2, 22.6), (3.4, 21.2), (-2.4, 25.4), (1.8, 25.2)):
        B(m, "head", "light_gray_concrete", (x, y, 4.55), (0.8, 0.8, 0.1))
    # the face
    B(m, "head", "yellow_concrete", (-2.8, 16.0, 5.3), (5.6, 4.6, 0.5))
    for sd in (1, -1):
        pupil(m, "head", sd * 1.3 - 0.6, 18.4, 5.8, side_face=False, h=0.4, w=1.2)
        B(m, "head", "yellow_terracotta", (sd * 1.3 - 0.7, 18.8, 5.8), (1.4, 0.4, 0.12))
        B(m, "head", "orange_concrete", (sd * 2.0 - 0.4, 17.0, 5.8), (0.8, 0.5, 0.1))
    B(m, "jaw", "brown_terracotta", (-0.8, 16.8, 5.8), (1.6, 0.4, 0.12))
    m.no_elbows = m.no_knees = True
    idle = loop(3.6, {"neck": {"rot": wave2((6, 0, 8), 3.6)}, "body": {"rot": wave2((3, 0, 4), 3.6, 0.5)},
                      "head": {"rot": wave2((4, 10, 4), 3.6, 0.2)}, "armL": {"rot": wave(2, 10, 1.8)}, "armR": {"rot": wave(2, 10, 1.8, 0.5)}})
    standard_anims(m, heavy=0.4, idle=idle, walk=waddle(0.9))
    m.attacks = {"levitate": "cast", "volley": "double"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ pack goblin

@mini("pack_goblin")
def pack_goblin():
    """The Pack Goblin: a lanky green goblin with long ears, a floppy brown hat, a red vest, purple trousers
    and a grin full of crooked teeth, bent under a huge stolen pack with a frying pan and a rolled blanket
    tied on."""
    m = Model("pack_goblin", "biped", 1.0)
    SK, SD = "lime_terracotta", "green_terracotta"
    humanoid(m, hip=10, legx=2.0, neck=20, shoulder=19.4, armx=5.4)
    m.bone("hat", "head", (0, 27.6, 0))
    m.bone("pack", "body", (0, 17, -3))
    m.bone("earL", "head", (4.0, 24, 0)); m.bone("earR", "head", (-4.0, 24, 0))
    legs(m, 2.0, 10, 2.6, 2.8, "purple_terracotta", foot=SK, foot_h=1.2, toe=1.6)
    B(m, "hips", "purple_terracotta", (-3.6, 8.8, -2.2), (7.2, 2.0, 4.4))
    B(m, "body", SK, (-3.6, 10.6, -2.2), (7.2, 9.0, 4.4))
    B(m, "body", "red_concrete", (-3.8, 12.0, -2.4), (7.6, 7.6, 4.8))
    B(m, "body", SK, (-1.0, 13.0, 2.3), (2.0, 6.6, 0.2))
    B(m, "body", "brown_concrete", (-3.9, 10.6, -2.5), (7.8, 1.2, 5.0))
    for y in (16.6, 14.2):
        B(m, "body", "gold_block", (1.2, y, 2.45), (0.7, 0.7, 0.1))
    # head
    B(m, "head", SK, (-3.8, 19.6, -3.4), (7.6, 7.2, 7.0))
    B(m, "head", SD, (-4.0, 24.0, 3.4), (8.0, 1.0, 0.8))
    for sd in (1, -1):
        eye(m, "head", sd * 1.8, 23.0, 3.6, w=2.2, h=1.6, out=0.3, white="yellow_concrete", pw=0.9, ph=1.2, look=(0.3 * sd, 0))
    B(m, "head", SK, (-0.9, 21.2, 3.6), (1.8, 2.6, 2.4))
    B(m, "head", "black_concrete", (-3.0, 20.2, 3.6), (6.0, 0.9, 0.2))
    for x, h in ((-2.6, 0.9), (-0.8, 1.3), (1.0, 0.7), (2.2, 1.1)):
        B(m, "head", "white_terracotta", (x, 21.1 - h, 3.7), (0.8, h, 0.3))
    for sd, s in side():
        chain(m, "ear" + s, SK, (sd * 3.8, 24, 0), [(3.0, (2.4, 0.9), (0, 0, -70 * sd)), (2.8, (1.6, 0.7), (0, 0, -60 * sd)), (1.4, (0.9, 0.5), (0, 0, -48 * sd), SD)])
    # floppy hat
    B(m, "hat", "brown_concrete", (-5.6, 26.6, -5.0), (11.2, 0.8, 10.0))
    B(m, "hat", "brown_concrete", (-3.8, 27.4, -3.6), (7.6, 2.6, 7.2))
    chain(m, "hat", "brown_concrete", (0, 30.0, 0), [(1.6, (5.0, 5.0), (-10, 0, 0)), (1.6, (3.2, 3.2), (-60, 0, 0), "brown_terracotta")])
    B(m, "hat", "brown_terracotta", (-3.9, 27.4, -3.7), (7.8, 0.7, 7.4))
    # the pack
    B(m, "pack", "spruce_planks", (-4.6, 9.6, -9.6), (9.2, 11.0, 7.0))
    B(m, "pack", "dark_oak_planks", (-4.9, 18.4, -9.9), (9.8, 2.6, 7.6))
    B(m, "pack", "brown_wool", (-5.6, 21.0, -9.0), (11.2, 2.6, 2.6))
    B(m, "pack", "red_wool", (-4.0, 21.0, -9.1), (1.0, 2.8, 2.8))
    B(m, "pack", "red_wool", (2.8, 21.0, -9.1), (1.0, 2.8, 2.8))
    B(m, "pack", "black_concrete", (4.6, 12.0, -7.6), (0.6, 4.6, 4.6))
    B(m, "pack", "black_concrete", (5.0, 13.9, -6.2), (0.6, 0.8, 4.2))
    B(m, "pack", "dark_oak_planks", (5.0, 14.0, -2.6), (0.6, 0.6, 2.4))
    for sd in (1, -1):
        B(m, "pack", "dark_oak_planks", (sd * 2.4 - 0.6, 11.0, -2.6), (1.2, 8.6, 5.2))
    B(m, "pack", "iron_block", (-1.2, 13.0, -9.9), (2.4, 2.4, 0.3))
    arms(m, 5.4, 19.4, 2.2, 2.4, "red_concrete", SK, SK, 11.0, hand_h=1.8)
    standard_anims(m, heavy=0.7, extra={"idle": idle_biped(3.0, 22, extra={"earL": {"rot": wave(2, 8, 1.5)}, "earR": {"rot": wave(2, 8, 1.5, 0.5)},
                                                                         "pack": {"rot": wave(0, 3, 1.5)}})})
    m.attacks = {"leap": "lunge", "volley": "double", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ ring frog

@mini("ring_frog")
def ring_frog():
    """Floaty Frog, the pool party crasher: a tall mottled green frog standing upright with bulging eyes on
    top of a wide head, a pale wide mouth line, a pale belly, long arms with webbed hands, and a red and
    white swim ring round his middle."""
    m = Model("ring_frog", "biped", 1.0)
    G, GD, GL, BE = "lime_terracotta", "green_terracotta", "lime_concrete", "white_terracotta"
    humanoid(m, hip=7, legx=2.8, neck=18, shoulder=17, armx=6.0, jaw=(0, 19.4, 4.2))
    m.bone("ring", "body", (0, 11, 0))
    legs(m, 2.8, 7, 3.0, 3.4, G, foot=GL, foot_h=0.8, toe=2.2)
    B(m, "hips", G, (-4.4, 5.4, -2.8), (8.8, 2.4, 5.6))
    B(m, "body", G, (-4.6, 7.6, -3.0), (9.2, 10.6, 6.0))
    B(m, "body", BE, (-3.4, 8.0, 3.0), (6.8, 8.4, 0.3))
    for x, y, z in ((3.2, 15.4, -3.1), (-4.0, 9.6, -3.1), (-1.0, 12.0, -3.1)):
        B(m, "body", GD, (x, y, z), (1.6, 1.6, 0.1))
    # wide head with eyes on top
    B(m, "head", G, (-5.4, 18.0, -4.0), (10.8, 5.6, 8.2))
    B(m, "head", G, (-4.6, 23.6, -3.4), (9.2, 0.8, 6.6))
    B(m, "head", BE, (-5.2, 18.6, 4.2), (10.4, 0.8, 0.2))
    B(m, "jaw", G, (-5.0, 17.0, -3.4), (10.0, 1.6, 7.8))
    B(m, "jaw", BE, (-4.6, 16.8, 2.4), (9.2, 0.6, 2.0))
    for sd in (1, -1):
        B(m, "head", G, (sd * 3.0 - 1.9, 23.4, -0.4), (3.8, 2.4, 3.6))
        eye(m, "head", sd * 3.0, 24.8, 3.2, w=3.0, h=2.6, out=0.4, white="yellow_concrete", pw=2.2, ph=1.0)
        B(m, "head", GD, (sd * 3.0 - 1.9, 25.8, -0.4), (3.8, 0.4, 3.8))
        B(m, "head", GD, (sd * 1.0 - 0.3, 20.6, 4.2), (0.6, 0.6, 0.1))
        B(m, "head", GD, (sd * 4.0 - 0.8, 21.6, -4.1), (1.6, 1.4, 0.1))
    # swim ring
    for x0, z0, w, d, blk in ((-7.0, -5.0, 14.0, 2.4, "red_concrete"), (-7.0, 2.6, 14.0, 2.4, "red_concrete"),
                              (-7.0, -2.6, 2.4, 5.2, "white_concrete"), (4.6, -2.6, 2.4, 5.2, "white_concrete")):
        B(m, "ring", blk, (x0, 9.6, z0), (w, 2.8, d))
    for x in (-2.0, 1.0):
        B(m, "ring", "white_concrete", (x, 9.6, 4.95), (1.6, 2.8, 0.1))
        B(m, "ring", "white_concrete", (x, 9.6, -5.05), (1.6, 2.8, 0.1))
    arms(m, 6.0, 17, 2.4, 2.6, G, G, GL, 10.0, hand_h=1.4, hand_w=3.6)
    for sd, s in side():
        for k in (-1.2, 0, 1.2):
            B(m, "arm" + s, GL, (sd * 6.0 - 0.4 + k, 5.4, 1.2), (0.8, 0.6, 1.2))
    standard_anims(m, heavy=0.7, extra={"idle": idle_biped(2.4, 14, breath=0.05, extra={"jaw": {"rot": K((0, Z), (1.8, Z), (2.0, (8, 0, 0)), (2.2, Z), (2.4, Z))},
                                                                                  "ring": {"rot": wave(2, 3, 2.4)}})})
    m.attacks = {"leap": "lunge", "pull": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ mossy turtle

@mini("mossy_turtle")
def mossy_turtle():
    """The Mossy Turtle: a stocky turtle with a tall brown shell ringed in plates, a pale rim, moss and a
    little flower on top, a bright green head with sleepy eyes and a beak, and chunky green legs."""
    m = Model("mossy_turtle", "quad", 1.0)
    SH, SD, RIM, SK, SKD = "brown_terracotta", "dark_oak_planks", "yellow_terracotta", "lime_concrete", "lime_terracotta"
    m.bone("body", "root", (0, 4, 0))
    for n, x, z in (("legFL", 4.4, 3.6), ("legFR", -4.4, 3.6), ("legBL", 4.4, -4.6), ("legBR", -4.4, -4.6)):
        m.bone(n, "body", (x, 4, z))
        B(m, n, SK, (x - 1.6, 0.6, z - 1.6), (3.2, 4.0, 3.2))
        B(m, n, SKD, (x - 1.8, 0, z - 1.6), (3.6, 0.8, 4.0))
    m.bone("head", "body", (0, 5, 6.6))
    m.bone("jaw", "head", (0, 4.4, 9.4))
    m.bone("tail", "body", (0, 4.6, -8))
    # shell
    B(m, "body", RIM, (-6.4, 3.2, -7.6), (12.8, 1.4, 15.0))
    B(m, "body", SH, (-6.0, 4.6, -7.2), (12.0, 5.0, 14.2))
    B(m, "body", SH, (-5.0, 9.6, -6.0), (10.0, 2.2, 11.8))
    B(m, "body", SH, (-3.4, 11.8, -4.4), (6.8, 1.0, 8.6))
    for x0, w in ((-6.05, 0.1), (5.95, 0.1)):
        for z0 in (-5.6, -1.2, 3.2):
            B(m, "body", SD, (x0, 5.4, z0), (w, 3.4, 3.6))
    for x0 in (-4.6, -1.2, 2.2):
        B(m, "body", SD, (x0, 5.4, 7.0), (2.4, 3.4, 0.1)); B(m, "body", SD, (x0, 5.4, -7.3), (2.4, 3.4, 0.1))
    for x0, z0 in ((-3.8, -4.4), (0.4, -4.4), (-3.8, 0.4), (0.4, 0.4)):
        B(m, "body", SD, (x0 + 0.2, 11.85, z0 + 0.2), (3.0, 0.1, 3.6))
    B(m, "body", "moss_block", (-3.0, 12.8, -3.8), (6.0, 0.5, 6.0))
    B(m, "body", "moss_block", (-4.6, 11.8, -1.0), (2.0, 0.4, 3.2))
    flower(m, "body", 1.0, 13.3, -1.0, "pink_concrete", "yellow_concrete", stem=1.2)
    # head and beak
    B(m, "head", SK, (-2.6, 3.4, 6.0), (5.2, 4.6, 5.0))
    B(m, "head", SKD, (-2.6, 7.4, 6.2), (5.2, 0.6, 4.4))
    B(m, "head", "yellow_terracotta", (-1.6, 4.6, 10.8), (3.2, 1.8, 1.2))
    B(m, "jaw", SKD, (-2.2, 3.0, 9.2), (4.4, 1.2, 2.2))
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 2.6 - 0.08, 5.6, 8.6), (0.16, 1.0, 1.2))
        B(m, "head", SKD, (sd * 2.62 - 0.1, 6.4, 8.4), (0.2, 0.6, 1.6))
    B(m, "tail", SK, (-1.0, 3.8, -9.4), (2.0, 1.4, 2.2))
    m.anims = {}
    m.attacks = {"shockwave": "rear", "heal": "howl", "charge": "charge"}
    m.melee = "bite"
    return m


# ------------------------------------------------------------------------------------------------ stumpy

@mini("stumpy")
def stumpy():
    """Stumpy, what is left of the old oak: a short cut stump whose top shows the tree rings, a cross face
    carved in the bark with glowing green eyes, a shelf mushroom on one side, a sprout on top, little root
    feet and twig arms with forked ends."""
    m = Model("stumpy", "biped", 1.0)
    LOG, DK, RT = "oak_log", "dark_oak_log", "stripped_oak_log"
    humanoid(m, hip=3, legx=3.2, neck=10, shoulder=10, armx=6.2)
    for sd, s in side():
        B(m, "leg" + s, LOG, (sd * 3.2 - 1.4, 0.6, -1.4), (2.8, 2.6, 2.8))
        B(m, "leg" + s, DK, (sd * 3.2 - 1.2, 0, 0.6), (2.4, 1.0, 3.2))
        B(m, "leg" + s, DK, (sd * 3.2 + (0.6 if sd > 0 else -2.2), 0, -1.0), (1.6, 0.8, 1.6))
    B(m, "body", LOG, (-6.0, 3.0, -6.0), (12, 7.0, 12))
    B(m, "body", DK, (-6.3, 3.0, -6.3), (12.6, 1.6, 12.6))
    B(m, "head", LOG, (-6.0, 10.0, -6.0), (12, 6.0, 12))
    # the carved face: dark sockets with lit green eyes, heavy carved brows, a frown
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 2.6 - 1.4, 11.4, 5.9), (2.8, 2.4, 0.2))
        B(m, "head", "lime_concrete", (sd * 2.6 - 0.7, 11.8, 6.0), (1.4, 1.4, 0.15), light=True)
        brow(m, "head", sd * 2.6, 14.4, 6.0, 3.6, DK, tilt=-16 * sd, h=1.0, d=0.8)
    B(m, "body", "black_concrete", (-2.8, 7.6, 5.9), (5.6, 1.0, 0.2))
    B(m, "body", "black_concrete", (-3.4, 6.8, 5.9), (1.0, 1.0, 0.2)); B(m, "body", "black_concrete", (2.4, 6.8, 5.9), (1.0, 1.0, 0.2))
    B(m, "body", RT, (-0.8, 8.6, 5.9), (1.6, 0.6, 0.2))
    # shelf mushrooms on the right side, moss and a sprout on top
    B(m, "body", "brown_mushroom_block", (-8.6, 7.4, -3.6), (2.8, 1.0, 5.2))
    B(m, "body", "brown_mushroom_block", (-7.8, 9.6, -2.6), (1.8, 0.8, 3.4))
    B(m, "head", "moss_block", (-6.1, 15.4, -6.1), (5.0, 0.8, 12.2))
    B(m, "head", "moss_block", (-6.15, 13.4, -6.1), (0.2, 2.0, 7.0))
    B(m, "head", "dark_oak_planks", (1.8, 16.0, -1.4), (0.8, 1.6, 0.8))
    chain(m, "head", "lime_concrete", (2.2, 17.4, -1.0), [(1.6, (0.4, 1.4), (0, 0, -60)), (0.8, (0.4, 0.8), (0, 0, -80))])
    chain(m, "head", "green_concrete", (2.2, 17.4, -1.0), [(1.4, (0.4, 1.2), (0, 0, 60)), (0.8, (0.4, 0.8), (0, 0, 80))])
    # twig arms
    for sd, s in side():
        e = chain(m, "arm" + s, "spruce_log", (sd * 6.0, 10, 0), [(2.6, (1.4, 1.4), (0, 0, -110 * sd)), (2.2, (1.1, 1.1), (0, 0, -140 * sd))])
        chain(m, "arm" + s, "spruce_log", e, [(1.4, (0.7, 0.7), (0, 0, -170 * sd))])
        chain(m, "arm" + s, "spruce_log", e, [(1.2, (0.6, 0.6), (40, 0, -120 * sd))])
    m.no_elbows = m.no_knees = True
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(4.0, 8, breath=0.02)})
    m.attacks = {"spikes": "slam", "heal": "roar"}
    m.melee = "swipe"
    return m
