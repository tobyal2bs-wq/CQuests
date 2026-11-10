"""v14: the studio pass. Hand-built redesigns of the bosses the user called bugged or ugly, new bosses and minis
from the user's pictures (two of them copied 1:1), and variants of the Hollow Mage.

Every model here is built by hand with the v14 kit: built eyes and mouths, clean one-hue parts on grain blocks,
its own idle, walk and attack moves. They skip the automatic polish and refine passes (gen_models), which
were written for the older models and cut or moved parts of these."""
import models as _models
from build import Model
import roster
import v9_minis
import v12_final
from v2_recipes import S, fx, gone
from v14_kit import (legs, arms, humanoid, standard_anims, set_pivot, chain, B, C, MB, MC, shaded, eye, teeth, brow, speckle, front_art, K, Z, wave, wave2, breathe, bobpos,
                     attack, loop, biped_set, walk_biped, idle_biped)

STUDIO = set()      # ids built here: no polish/refine pass
REVISED4 = set()    # ids whose bosses.yml entry is replaced on servers (revision 4), rewards and on/off kept
NEW_BIG = []        # new weekly bosses, in order
NEW_MINI = []


def studio(id, revise=True):
    def deco(fn):
        STUDIO.add(id)
        if revise: REVISED4.add(id)
        return _models.model(fn)
    return deco


def recipe(part, sin, sdie, pin=1.0, roar="roar", die="die_front", ground="moss_block"):
    sp = [S("shrink", 0, s=0), fx(0, part, 40, sin, pin, y=0.5, spread=1.2, ring=2), S("pose", 2, 12), fx(10, part, 30, y=0.8, spread=1.0),
          S("anim", 16, 24, name=roar)]
    de = [S("flash", 0, 4), fx(0, sound=sdie, pitch=pin), S("anim", 0, 30, name=die), fx(16, part, 60, None, 1.0, y=0.8, spread=1.4),
          S("swap", 30, block=ground, order="up", stagger=14), fx(44, "POOF", 30, "BLOCK_GRAVEL_BREAK", 0.7, y=0.4, spread=1.2), gone(48, 12)]
    return sp, de


def new_big(id, name, title, entity, theme, bar, extra=(), minion=None, items=(), top=(), money=60000, movement=None, fly=None,
            damage=12, armor=8, speed=None, rec=None):
    def deco(fn):
        v12_final.BIG_INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, minions=3 if minion else 0,
                                      extra=list(extra), items=list(items), top_items=list(top), money=money, top_money=money * 3,
                                      damage=damage, armor=armor, **({"movement": movement} if movement else {}),
                                      **({"fly_height": fly} if fly else {}), **({"speed": speed} if speed else {}))
        v12_final.SPAWN[id], v12_final.DEATH[id] = rec or recipe("CLOUD", "ENTITY_RAVAGER_ROAR", "ENTITY_RAVAGER_DEATH")
        if id not in roster.GENERAL:
            roster.GENERAL.append(id); roster.ALL.append(id)
        NEW_BIG.append(id)
        return studio(id, revise=False)(fn)
    return deco


def new_mini(id, name, title, entity="ZOMBIE", theme="nature", bar="GREEN", extra=(), minion=None, movement=None, rec=None):
    def deco(fn):
        if id not in v9_minis.MINIS: v9_minis.MINIS.append(id)
        v9_minis.INFO[id] = dict(name=name, title=title, entity=entity, theme=theme, bar=bar, minion=minion, extra=list(extra),
                                 **({"movement": movement} if movement else {}))
        v9_minis.SPAWN[id], v9_minis.DEATH[id] = rec or recipe("POOF", "ENTITY_SLIME_SQUISH", "ENTITY_SLIME_DEATH", 1.4)
        NEW_MINI.append(id)
        return studio(id, revise=False)(fn)
    return deco


# ================================================================================================ new minis

@new_mini("redeye", "<gradient:#c62828:#ffcdd2><bold>Peeper</bold></gradient>", "Two Big Eyes and No Manners", entity="ZOMBIE", theme="blood", bar="RED",
          extra=["leap"], rec=recipe("CRIMSON_SPORE", "ENTITY_FROG_AMBIENT", "ENTITY_FROG_DEATH", 1.6, "shriek", "die_back", "red_wool"))
def redeye():
    """Peeper, a little red blob that is mostly head: two huge goggling eyes that stick out over its brow and
    roll around on their own, a wide dark frown, stubby arms flung out to the sides and two short legs."""
    m = Model("redeye", "biped", 1.0)
    m.bone("hips", "root", (0, 4, 0))
    m.bone("legL", "hips", (2.6, 4, 0)); m.bone("legR", "hips", (-2.6, 4, 0))
    m.bone("body", "hips", (0, 4, 0))
    m.bone("head", "body", (0, 10, 0))
    m.bone("eyeL", "head", (3.1, 11, 4)); m.bone("eyeR", "head", (-3.1, 11, 4))
    m.bone("pupils", "head", (0, 13, 6.6))
    m.bone("armL", "body", (6, 7.5, 0)); m.bone("armR", "body", (-6, 7.5, 0))
    m.bone("jaw", "head", (0, 8, 4))
    RED, LIT, DARK, MOUTH = "red_wool", "red_concrete", "red_terracotta", "nether_wart_block"
    # legs: short and thick, flat feet
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, RED, (sd * 2.6 - 1.6, 0.8, -1.6), (3.2, 3.4, 3.2))
        B(m, leg, DARK, (sd * 2.6 - 1.8, 0, -1.8), (3.6, 1.0, 4.0))
    # the body is the head: a big rounded block, lighter on top, darker underneath
    B(m, "body", DARK, (-5.5, 4, -4.5), (11, 1, 9))
    B(m, "body", RED, (-6, 5, -5), (12, 4, 10))
    B(m, "head", RED, (-6, 9, -5), (12, 4.5, 10))
    B(m, "head", RED, (-5.5, 13.5, -4.5), (11, 1, 9))
    B(m, "head", LIT, (-5, 14.5, -4), (10, 0.6, 8))
    # rounded front and side edges
    B(m, "head", RED, (-6.4, 6, -4.4), (12.8, 7.5, 8.8))
    # the mouth: a wide dark frown under the eyes, with a lighter lower lip
    B(m, "jaw", MOUTH, (-4.6, 5.8, 4.6), (9.2, 3.2, 0.6))
    B(m, "jaw", MOUTH, (-5.4, 5.2, 4.6), (1.2, 1.4, 0.6))
    B(m, "jaw", MOUTH, (4.2, 5.2, 4.6), (1.2, 1.4, 0.6))
    B(m, "jaw", "red_nether_bricks", (-3.8, 6.0, 4.75), (7.6, 1.6, 0.6))
    B(m, "jaw", LIT, (-3.6, 5.2, 4.9), (7.2, 0.6, 0.3))
    # the eyes: two big boxes standing out of the brow and up over the top of the head
    for sd, b in ((1, "eyeL"), (-1, "eyeR")):
        B(m, b, "snow_block", (sd * 3.1 - 2.6, 10.2, 2.4), (5.2, 6.4, 3.4))
        B(m, b, "white_concrete", (sd * 3.1 - 2.4, 10.4, 5.8), (4.8, 6.0, 0.25))
        B(m, b, "light_gray_concrete", (sd * 3.1 - 2.6, 10.2, 5.81), (5.2, 0.7, 0.3))
        B(m, b, "light_gray_concrete", (sd * 3.1 + (2.0 if sd > 0 else -2.6), 10.2, 5.82), (0.6, 6.4, 0.3))
    # pupils live on their own bone so they roll round the eye whites
    for sd in (1, -1):
        B(m, "pupils", "black_concrete", (sd * 3.1 - 1.3, 11.8, 6.05), (2.6, 3.0, 0.2))
        B(m, "pupils", "white_concrete", (sd * 3.1 - 1.0, 13.9, 6.2), (0.7, 0.7, 0.1), light=True)
    # stubby arms flung out to the sides
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, RED, (sd * 6 - (0 if sd > 0 else 4.5), 5.6, -1.4), (4.5, 2.6, 2.8), (0, 0, -18 * sd), (sd * 6, 7, 0))
        B(m, a, DARK, (sd * 10 - (0 if sd > 0 else 1.6), 4.3, -1.6), (1.6, 2.8, 3.2), (0, 0, -18 * sd), (sd * 6, 7, 0))
    m.no_elbows = True
    m.no_knees = True
    look = K((0, Z), (0.6, (1.0, 0.2, 0)), (1.3, (1.0, 0.2, 0)), (1.6, (-1.0, -0.3, 0)), (2.5, (-1.0, -0.3, 0)), (2.8, (0, 0.5, 0)), (3.4, (0, 0.5, 0)), (4.0, Z))
    m.anims = {
        "idle": loop(4.0, {
            "hips": {"pos": K((0, Z), (0.5, (0, -0.4, 0)), (1.0, Z), (2.0, Z), (2.5, (0, -0.4, 0)), (3.0, Z), (4.0, Z))},
            "body": {"scl": K((0, (1, 1, 1)), (0.5, (1.05, 0.94, 1.05)), (1.0, (1, 1, 1)), (2.5, (1.05, 0.94, 1.05)), (3.0, (1, 1, 1)), (4.0, (1, 1, 1))),
                     "rot": wave(2, 3, 4.0)},
            "head": {"rot": K((0, Z), (1.0, (0, 10, 3)), (1.8, (0, 10, 3)), (2.4, (0, -12, -3)), (3.2, (0, -12, -3)), (4.0, Z))},
            "pupils": {"pos": look},
            "eyeL": {"rot": wave(2, 4, 2.0)}, "eyeR": {"rot": wave(2, 4, 2.0, 0.5)},
            "armL": {"rot": wave(2, 10, 2.0, base=(0, 0, 0))}, "armR": {"rot": wave(2, 10, 2.0, 0.5)},
            "jaw": {"pos": K((0, Z), (3.0, Z), (3.2, (0, -0.4, 0)), (3.6, Z), (4.0, Z))}}),
        "walk": loop(0.6, {
            "legL": {"rot": K((0, (30, 0, 0)), (0.3, (-30, 0, 0)), (0.6, (30, 0, 0)))},
            "legR": {"rot": K((0, (-30, 0, 0)), (0.3, (30, 0, 0)), (0.6, (-30, 0, 0)))},
            "hips": {"pos": K((0, Z), (0.15, (0, 1.2, 0)), (0.3, Z), (0.45, (0, 1.2, 0)), (0.6, Z)),
                     "rot": K((0, (0, 0, 8)), (0.3, (0, 0, -8)), (0.6, (0, 0, 8)))},
            "armL": {"rot": K((0, (0, 0, 20)), (0.3, (0, 0, -10)), (0.6, (0, 0, 20)))},
            "armR": {"rot": K((0, (0, 0, 10)), (0.3, (0, 0, -20)), (0.6, (0, 0, 10)))},
            "eyeL": {"rot": K((0, (0, 0, 6)), (0.3, (0, 0, -6)), (0.6, (0, 0, 6)))},
            "eyeR": {"rot": K((0, (0, 0, -6)), (0.3, (0, 0, 6)), (0.6, (0, 0, -6)))}}),
        # a flat-out leap with arms thrown up, landing in a squash
        "pounce": attack(1.0, 0.6, {
            "hips": {"pos": K((0, Z), (0.25, (0, -1.5, 0)), (0.45, (0, 6, 3)), (0.6, (0, 0, 5)), (0.75, (0, -1.2, 5)), (1.0, Z))},
            "body": {"scl": K((0, (1, 1, 1)), (0.25, (1.15, 0.8, 1.15)), (0.45, (0.9, 1.15, 0.9)), (0.6, (1.2, 0.75, 1.2)), (0.8, (1, 1, 1)), (1.0, (1, 1, 1))),
                     "rot": K((0, Z), (0.45, (-15, 0, 0)), (0.6, (12, 0, 0)), (1.0, Z))},
            "armL": {"rot": K((0, Z), (0.45, (0, 0, 60)), (0.6, (0, 0, -10)), (1.0, Z))},
            "armR": {"rot": K((0, Z), (0.45, (0, 0, -60)), (0.6, (0, 0, 10)), (1.0, Z))},
            "pupils": {"pos": K((0, Z), (0.25, (0, -0.6, 0)), (0.5, (0, 0.6, 0)), (1.0, Z))}}),
        # a shriek: eyes bulge, mouth drops, arms shake
        "shriek": attack(1.2, 0.5, {
            "jaw": {"pos": K((0, Z), (0.3, (0, -1.4, 0)), (0.9, (0, -1.4, 0)), (1.2, Z))},
            "eyeL": {"scl": K((0, (1, 1, 1)), (0.3, (1.2, 1.25, 1.2)), (0.9, (1.2, 1.25, 1.2)), (1.2, (1, 1, 1)))},
            "eyeR": {"scl": K((0, (1, 1, 1)), (0.3, (1.2, 1.25, 1.2)), (0.9, (1.2, 1.25, 1.2)), (1.2, (1, 1, 1)))},
            "pupils": {"scl": K((0, (1, 1, 1)), (0.3, (0.7, 0.7, 1)), (0.9, (0.7, 0.7, 1)), (1.2, (1, 1, 1)))},
            "armL": {"rot": K((0, Z), (0.3, (0, 0, 50)), (0.45, (0, 0, 35)), (0.6, (0, 0, 50)), (0.75, (0, 0, 35)), (0.9, (0, 0, 50)), (1.2, Z))},
            "armR": {"rot": K((0, Z), (0.3, (0, 0, -50)), (0.45, (0, 0, -35)), (0.6, (0, 0, -50)), (0.75, (0, 0, -35)), (0.9, (0, 0, -50)), (1.2, Z))},
            "body": {"rot": K((0, Z), (0.3, (-10, 0, 0)), (0.9, (-8, 0, 0)), (1.2, Z))}}),
        "swat": attack(0.7, 0.35, {
            "armR": {"rot": K((0, Z), (0.2, (-20, 0, -60)), (0.35, (40, 0, 30)), (0.7, Z))},
            "body": {"rot": K((0, Z), (0.2, (0, 20, 0)), (0.35, (6, -20, 0)), (0.7, Z))}}),
    }
    m.attacks = {"leap": "pounce", "roar": "shriek"}
    m.melee = "swat"
    return m


# ================================================================================================ new big bosses

@new_big("rootmaw", "<gradient:#8d6e63:#d4e157><bold>Rootmaw</bold></gradient>", "The Mandrake That Woke Up Hungry", "RAVAGER", "nature", "GREEN",
         extra=["spikes", "poison"], minion=None, items=["MOSS_BLOCK 32", "ROOTED_DIRT 16", "DIAMOND 3"], top=["ENCHANTED_GOLDEN_APPLE 1"],
         rec=recipe("CHERRY_LEAVES", "BLOCK_ROOTED_DIRT_BREAK", "BLOCK_MANGROVE_ROOTS_BREAK", 0.6, "roar", "die_front", "rooted_dirt"))
def rootmaw():
    """Rootmaw, a mandrake root the size of a hut: a square trunk of pale knotted wood with a cracked crown,
    two glowing yellow eyes under a heavy brow, a huge mouth of jagged white teeth with a red gullet, two
    long root arms that split into twig fingers and drag on the ground, and a tuft of long yellow-green
    leaves that whip about on top."""
    m = Model("rootmaw", "biped", 1.6)
    W, LIGHT, DARK, CRACK = "stripped_birch_log", "birch_planks", "stripped_oak_log", "dark_oak_planks"
    m.bone("hips", "root", (0, 2, 0))
    m.bone("body", "hips", (0, 2, 0))
    m.bone("head", "body", (0, 16, 0))
    m.bone("jaw", "body", (0, 14, -3))
    m.bone("armL", "body", (10, 22, 0)); m.bone("armR", "body", (-10, 22, 0))
    m.bone("foreL", "armL", (19, 15, 2)); m.bone("foreR", "armR", (-19, 15, 2))
    for i, (x, z, yaw) in enumerate(((0, 0, 0), (5, -3, 40), (-5, -3, -40), (3, 4, 15), (-4, 3, -20))):
        m.bone(f"leaf{i}", "head", (x * 0.6, 32, z * 0.6))
    # little root feet under the trunk so it stands, not floats
    m.bone("legL", "hips", (5, 2, 0)); m.bone("legR", "hips", (-5, 2, 0))
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, DARK, (sd * 5 - 2.5, 0, -3), (5, 3, 6))
        B(m, leg, W, (sd * 7.5 - (0 if sd > 0 else 3), 0, -1.5), (3, 1.5, 3), (0, 0, -15 * sd))
        B(m, leg, W, (sd * 4 - 1, 0, 2.5), (2, 1.2, 3.5), (-10, 0, 0))
    # the lower trunk and jaw: a deep box with the lower teeth standing on its rim
    B(m, "jaw", W, (-11, 3, -9), (22, 8, 18))
    B(m, "jaw", DARK, (-11.2, 3, -9.2), (22.4, 1.2, 18.4))
    B(m, "jaw", "red_nether_bricks", (-9, 10.5, -5), (18, 0.6, 13))
    B(m, "jaw", "red_concrete", (-3, 10.9, -1), (6, 0.8, 7))
    teeth(m, "jaw", -8, 8, 11, 9.2, "white_concrete", n=4, h=4.0, w=2.2, down=False, jag=True, d=1.6)
    B(m, "jaw", "bone_block", (-10.5, 10.6, 7.2), (21, 0.6, 1.8))
    # the upper head: the trunk with the brow, eyes and upper teeth; the mouth opening between is dark red
    B(m, "body", "red_nether_bricks", (-9.5, 10, -6), (19, 9, 13))
    B(m, "body", "red_concrete", (-8.5, 11, -6.5), (17, 7, 15.3))
    B(m, "body", "nether_wart_block", (-6, 12, -6.6), (12, 5, 15.6))
    B(m, "head", W, (-11, 18, -9), (22, 12, 18))
    B(m, "head", LIGHT, (-10.4, 29.6, -8.4), (20.8, 0.8, 16.8))
    # cracked crown: uneven splinters on top
    for i, (x, z, h) in enumerate(((-8, -5, 4), (-4, 2, 2.5), (1, -4, 5), (5, 3, 3), (8, -2, 4.5), (-1, 5, 2), (9, 6, 2.5), (-9, 5, 3))):
        B(m, "head", W if i % 2 else DARK, (x - 1.5, 30, z - 1.5), (3, h, 3))
    B(m, "head", CRACK, (-0.6, 18, 9.0), (1.2, 6, 0.2))
    B(m, "head", CRACK, (-5, 26, 9.0), (0.8, 3.5, 0.2))
    B(m, "head", CRACK, (6, 18.5, 9.0), (0.8, 3, 0.2))
    # brow and glowing eyes, set deep under it
    B(m, "head", DARK, (-10, 25, 8.4), (20, 2.2, 1.6))
    B(m, "head", "black_concrete", (-9, 21.6, 8.95), (7.4, 3.6, 0.2))
    B(m, "head", "black_concrete", (1.6, 21.6, 8.95), (7.4, 3.6, 0.2))
    B(m, "head", "yellow_concrete", (-8.6, 22.0, 9.05), (6.6, 2.6, 0.3), light=True)
    B(m, "head", "yellow_concrete", (2.0, 22.0, 9.05), (6.6, 2.6, 0.3), light=True)
    B(m, "head", "white_concrete", (-8.2, 23.6, 9.3), (1.2, 0.8, 0.1), light=True)
    B(m, "head", "white_concrete", (2.4, 23.6, 9.3), (1.2, 0.8, 0.1), light=True)
    B(m, "head", DARK, (-9.2, 24.6, 8.9), (3, 1.2, 1.0), (0, 0, -12))
    B(m, "head", DARK, (6.2, 24.6, 8.9), (3, 1.2, 1.0), (0, 0, 12))
    # upper teeth hanging over the mouth, a big tusk at each corner
    B(m, "head", "bone_block", (-10.5, 17.6, 7.6), (21, 0.8, 1.6))
    teeth(m, "head", -9, 9, 18, 9.2, "white_concrete", n=5, h=4.6, w=2.2, down=True, jag=True, d=1.4)
    for sd in (1, -1):
        B(m, "head", "white_concrete", (sd * 9.8 - 1.2, 12.0, 6.6), (2.4, 6.0, 2.4))
    # long root arms that hang and drag, split into twig fingers
    for sd, a, f in ((1, "armL", "foreL"), (-1, "armR", "foreR")):
        C(m, a, W, (sd * 14.5, 19, 1), (11, 5, 5), (0, 0, -32 * sd))
        C(m, a, DARK, (sd * 11.2, 21, 1), (3, 5.6, 5.6), (0, 0, -32 * sd))
        C(m, f, W, (sd * 21.5, 9.5, 2.5), (4.4, 14, 4.4), (14, 0, 10 * sd))
        C(m, f, LIGHT, (sd * 21.8, 15.5, 2.4), (4.8, 1.2, 4.8), (14, 0, 10 * sd))
        for k, (dx, dz, ang) in enumerate(((-1.4, 1.2, -18), (1.2, 1.4, 14), (0, -1.4, 4), (2.0, -0.4, 30))):
            C(m, f, W if k % 2 == 0 else DARK, (sd * (23.0 + dx), 1.8, 3.8 + dz), (1.2, 4.2, 1.2), (20, 0, sd * ang))
        C(m, f, W, (sd * 24.2, 3.2, 1.0), (1.0, 3.2, 1.0), (-10, 0, sd * 40))
    # leaves: long blades that arch out and droop, each its own bone so they whip; every piece starts where
    # the last one ended
    LEAF, LEAF2, VEIN = "lime_concrete", "lime_terracotta", "yellow_concrete"
    blades = ((0, 0, 0.15, 7), (5, -3, 1.6, 7), (-5, -3, -1.6, 7), (3, 4, 1.0, 6), (-4, 3, -1.1, 6))
    for i, (x, z, out, L) in enumerate(blades):
        b = f"leaf{i}"
        x0, z0 = x * 0.6, z * 0.6
        C(m, b, "green_terracotta", (x0, 31.5, z0), (2.4, 3, 2.4))
        ang = out * 30
        tilt = -12 if z < 0 else 14 if z > 0 else 0
        segs = [(L, (3.6, 1.0), (tilt, 0, -ang * 0.4)), (L, (3.4, 1.0), (tilt * 1.5, 0, -ang * 1.0)),
                (L * 0.9, (2.8, 1.0), (tilt * 2.0, 0, -ang * 1.9)), (L * 0.8, (2.0, 1.0), (tilt * 2.4, 0, -ang * 2.7)), (L * 0.5, (1.2, 1.0), (tilt * 2.6, 0, -ang * 3.2))]
        chain(m, b, LEAF, (x0, 32.5, z0), [(sg[0], sg[1], sg[2], LEAF if k % 2 == 0 else LEAF2) for k, sg in enumerate(segs)])
        chain(m, b, VEIN, (x0, 32.5, z0 + 0.55), [(sg[0], (0.6, 0.2), sg[2]) for sg in segs[:3]])
    # moss and little sprouts on the shoulders and feet
    for sd in (1, -1):
        B(m, "head", "moss_block", (sd * 10 - 2, 28.6, -6), (4, 1.2, 5))
        B(m, "jaw", "moss_block", (sd * 9 - 2.5, 3, 7), (5, 1.4, 2.4))
    m.no_elbows = True
    m.no_knees = True
    leafwave = lambda i: {"rot": wave2((6 + i, 4, 5 + i), 4.0, i * 0.17)}
    idle = {
        "hips": {"pos": K((0, Z), (1.0, (0, -0.6, 0)), (2.0, Z), (3.0, (0, -0.6, 0)), (4.0, Z))},
        "body": {"rot": wave(2, 2.5, 4.0), "scl": breathe(2.0, 0.025)},
        "head": {"rot": K((0, (-9, 0, 0)), (1.0, (-12, 8, 2)), (2.0, (-12, 8, 2)), (3.0, (-7, -8, -2)), (4.0, (-9, 0, 0)))},
        "jaw": {"rot": K((0, Z), (0.8, (-4, 0, 0)), (1.2, Z), (2.6, (-6, 0, 0)), (3.0, Z), (4.0, Z))},
        "armL": {"rot": wave(0, 6, 4.0, base=(0, 0, 0))}, "armR": {"rot": wave(0, 6, 4.0, 0.5)},
        "foreL": {"rot": wave(0, 8, 4.0, 0.2)}, "foreR": {"rot": wave(0, 8, 4.0, 0.7)},
    }
    for i in range(5): idle[f"leaf{i}"] = leafwave(i)
    walk = {
        "hips": {"pos": K((0, Z), (0.35, (0, 1.4, 0)), (0.7, Z), (1.05, (0, 1.4, 0)), (1.4, Z)), "rot": K((0, (0, 0, 6)), (0.7, (0, 0, -6)), (1.4, (0, 0, 6)))},
        "legL": {"rot": K((0, (24, 0, 0)), (0.7, (-24, 0, 0)), (1.4, (24, 0, 0)))},
        "legR": {"rot": K((0, (-24, 0, 0)), (0.7, (24, 0, 0)), (1.4, (-24, 0, 0)))},
        "armL": {"rot": K((0, (-14, 0, 0)), (0.7, (14, 0, 0)), (1.4, (-14, 0, 0)))},
        "armR": {"rot": K((0, (14, 0, 0)), (0.7, (-14, 0, 0)), (1.4, (14, 0, 0)))},
        "body": {"rot": K((0, (4, 6, 0)), (0.7, (4, -6, 0)), (1.4, (4, 6, 0)))},
    }
    for i in range(5): walk[f"leaf{i}"] = {"rot": wave(0, 14, 0.7, i * 0.1, base=(-8, 0, 0))}
    roar = {
        "head": {"rot": K((0, Z), (0.4, (6, 0, 0)), (0.7, (-26, 0, 0)), (1.3, (-24, 0, 0)), (1.7, Z))},
        "jaw": {"rot": K((0, Z), (0.4, (-4, 0, 0)), (0.7, (10, 0, 0)), (1.3, (8, 0, 0)), (1.7, Z))},
        "armL": {"rot": K((0, Z), (0.7, (-30, 0, -40)), (1.3, (-28, 0, -38)), (1.7, Z))},
        "armR": {"rot": K((0, Z), (0.7, (-30, 0, 40)), (1.3, (-28, 0, 38)), (1.7, Z))},
        "body": {"rot": K((0, Z), (0.4, (8, 0, 0)), (0.7, (-10, 0, 0)), (1.3, (-8, 0, 0)), (1.7, Z))},
    }
    for i in range(5): roar[f"leaf{i}"] = {"rot": K((0, Z), (0.7, (-30 + i * 10, 0, (i - 2) * 14)), (1.0, (-20, 0, (i - 2) * 20)), (1.3, (-30, 0, (i - 2) * 14)), (1.7, Z))}
    m.anims = {
        "idle": loop(4.0, idle), "walk": loop(1.4, walk), "roar": attack(1.7, 0.7, roar),
        # both root arms rise and slam the ground, the mouth gapes
        "slam": attack(1.6, 0.9, {
            "armL": {"rot": K((0, Z), (0.6, (-120, 0, -30)), (0.75, (-125, 0, -30)), (0.9, (-10, 0, 0)), (1.2, (-12, 0, 0)), (1.6, Z))},
            "armR": {"rot": K((0, Z), (0.6, (-120, 0, 30)), (0.75, (-125, 0, 30)), (0.9, (-10, 0, 0)), (1.2, (-12, 0, 0)), (1.6, Z))},
            "foreL": {"rot": K((0, Z), (0.6, (-40, 0, 0)), (0.9, (30, 0, 0)), (1.6, Z))},
            "foreR": {"rot": K((0, Z), (0.6, (-40, 0, 0)), (0.9, (30, 0, 0)), (1.6, Z))},
            "body": {"rot": K((0, Z), (0.6, (-12, 0, 0)), (0.9, (18, 0, 0)), (1.2, (16, 0, 0)), (1.6, Z))},
            "head": {"rot": K((0, Z), (0.6, (-16, 0, 0)), (0.9, (-6, 0, 0)), (1.6, Z))},
            "hips": {"pos": K((0, Z), (0.6, (0, 2, -1)), (0.9, (0, -1.6, 1)), (1.2, (0, -1.4, 1)), (1.6, Z))}}),
        # a lunging bite: rock back, throw the head forward, jaws snap
        "bite": attack(1.1, 0.55, {
            "body": {"rot": K((0, Z), (0.3, (-14, 0, 0)), (0.55, (22, 0, 0)), (0.75, (20, 0, 0)), (1.1, Z))},
            "head": {"rot": K((0, Z), (0.3, (-22, 0, 0)), (0.5, (-22, 0, 0)), (0.55, (4, 0, 0)), (1.1, Z))},
            "hips": {"pos": K((0, Z), (0.3, (0, 0, -2)), (0.55, (0, -1, 4)), (0.75, (0, -1, 4)), (1.1, Z))},
            "armL": {"rot": K((0, Z), (0.3, (20, 0, -20)), (0.55, (-40, 0, 10)), (1.1, Z))},
            "armR": {"rot": K((0, Z), (0.3, (20, 0, 20)), (0.55, (-40, 0, -10)), (1.1, Z))}}),
        # one arm sweeps the ground in a wide arc
        "sweep": attack(1.3, 0.7, {
            "armR": {"rot": K((0, Z), (0.45, (-40, -30, 50)), (0.7, (-50, 50, 30)), (0.9, (-44, 60, 20)), (1.3, Z))},
            "foreR": {"rot": K((0, Z), (0.45, (-30, 0, 0)), (0.7, (20, 0, 0)), (1.3, Z))},
            "body": {"rot": K((0, Z), (0.45, (0, -30, 0)), (0.7, (6, 30, 0)), (0.9, (6, 34, 0)), (1.3, Z))}}),
    }
    m.attacks = {"slam": "slam", "spikes": "sweep", "poison": "roar", "charge": "bite"}
    m.melee = "bite"
    return m


# ================================================================================================ redesigned bosses

@studio("grubnose")
def grubnose():
    """Grubnose the Troll: a hunched ochre troll that is all shoulders and long arms, with a big bulbous nose
    hanging over a lipless grin and two stubby tusks, a heavy brow over small black eyes, pointed ears, rag
    wraps round its forearms, and a leather loincloth on a belt strung with bones and a little skull."""
    m = Model("grubnose", "biped", 1.6)
    SK, SKL, SKD, NOSE, NOSED = "yellow_terracotta", "smooth_sandstone", "brown_mushroom_block", "terracotta", "red_terracotta"
    LEA, LEAD = "brown_terracotta", "spruce_planks"
    humanoid(m, hip=13, legx=5.5, neck=31, shoulder=32, armx=14, jaw=(0, 32, 4))
    m.bone("cloth", "hips", (0, 13, 6))
    legs(m, 5.5, 13, 7, 7.5, SK, foot=SK, foot_h=2, toe=1.4, shin=SK)
    for sd in (1, -1):                         # toes
        for k in range(3):
            B(m, "legL" if sd > 0 else "legR", SKL, (sd * 5.5 - 3 + k * 2.1, 0, 4.4), (1.6, 1.2, 1.4))
    # belt, loincloth and the bone trinkets
    B(m, "hips", LEA, (-9.5, 11.5, -6.5), (19, 3.2, 13))
    B(m, "hips", LEAD, (-9.7, 12.5, -6.7), (19.4, 0.8, 13.4))
    B(m, "cloth", LEA, (-4.5, 4, 6.2), (9, 8.6, 0.9))
    B(m, "cloth", LEAD, (-4.5, 4, 6.4), (9, 1.0, 0.8))
    B(m, "hips", LEA, (-5, 5, -7.2), (10, 7, 0.9))
    for x, h in ((-7.5, 3), (-6, 2.4), (6, 2.6), (7.6, 3.2)):
        B(m, "hips", "bone_block", (x - 0.5, 11.2 - h, 6.3), (1.0, h, 1.0))
    B(m, "hips", "bone_block", (-1.6, 10.2, 6.6), (3.2, 3, 2.4))          # skull buckle
    B(m, "hips", "black_concrete", (-1.2, 11.4, 9.01), (1.0, 0.9, 0.1)); B(m, "hips", "black_concrete", (0.2, 11.4, 9.01), (1.0, 0.9, 0.1))
    # belly and the big hunched chest
    B(m, "body", SK, (-9, 14, -6), (18, 10, 12.5))
    B(m, "body", SK, (-11, 23, -7), (22, 12, 14))
    for sd in (1, -1):                         # shoulder humps
        B(m, "body", SK, (sd * 11.5 - 5, 26, -6.5), (10, 8.5, 13))
        B(m, "body", SKL, (sd * 11.5 - 4.5, 34.5, -6), (9, 0.6, 12))
    speckle(m, "body", (-11, 23, -7), (22, 12, 14), "back", [SKD, SKL], 6, "grub-back", cell=1.6)
    speckle(m, "body", (-11, 23, -7), (22, 12, 14), "front", [SKD], 3, "grub-front", cell=1.4)
    # head pushed forward between the shoulders
    B(m, "head", SK, (-7.5, 31, -2), (15, 12, 12))
    B(m, "head", SKL, (-7, 42.6, -1.5), (14, 0.7, 11))
    B(m, "head", SKD, (-8, 38.6, 9.4), (16, 2.4, 2.2))                  # heavy brow
    B(m, "head", "black_concrete", (-6.0, 36.4, 9.95), (4.6, 2.2, 0.2))
    B(m, "head", "black_concrete", (1.4, 36.4, 9.95), (4.6, 2.2, 0.2))
    eye(m, "head", 3.6, 37.3, 10, 2.2, 1.6, 0.3, pw=1.2, ph=1.3, look=(-0.3, 0))
    eye(m, "head", -3.6, 37.3, 10, 2.2, 1.6, 0.3, pw=1.2, ph=1.3, look=(0.3, 0))
    C(m, "head", NOSE, (0, 35.4, 11.6), (4.6, 5.0, 3.6))                # the nose
    C(m, "head", NOSE, (0, 33.4, 13.6), (4.0, 3.4, 2.6))
    C(m, "head", NOSED, (0, 32.0, 13.2), (3.0, 0.8, 2.2))
    B(m, "head", "granite", (-1.6, 36.4, 13.4), (1.4, 1.4, 0.2))
    for sd in (1, -1):                                                  # pointed ears
        C(m, "head", SK, (sd * 8.6, 37.5, 3), (2.4, 3.6, 2.6), (0, 0, -25 * sd))
        C(m, "head", SKD, (sd * 10.0, 39.2, 3), (1.4, 2.2, 1.4), (0, 0, -40 * sd))
    # the jaw with its grin and tusks
    B(m, "jaw", SK, (-7, 28.4, 0), (14, 4.2, 10.4))
    B(m, "jaw", "black_concrete", (-5.6, 32.0, 9.9), (11.2, 1.1, 0.4))
    B(m, "jaw", "nether_wart_block", (-4.4, 31.4, 10.0), (8.8, 0.6, 0.4))
    for sd in (1, -1):
        B(m, "jaw", "bone_block", (sd * 4.4 - 0.8, 31.8, 9.3), (1.6, 2.8, 1.4))
    # long arms with huge fists and rag wraps
    arms(m, 14.5, 33, 7.5, 7.5, SK, SK, SK, 26, hand_h=8, hand_w=9.5)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, "mushroom_stem", (sd * 14.5 - 3.95, 13.5, -3.95), (7.9, 2.2, 7.9))
        B(m, a, "mushroom_stem", (sd * 14.5 - 3.95, 17.5, -3.95), (7.9, 1.4, 7.9))
        for k in range(3):                     # knuckles
            B(m, a, SKL, (sd * 14.5 - 4 + k * 2.8, 1.6, 4.2), (2.2, 2.2, 0.6))
    m.rest("body", (12, 0, 0))
    m.rest("head", (-10, 0, 0))
    m.bend = -16
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(4.0, 16, extra={"cloth": {"rot": wave(0, 6, 2.0, base=(4, 0, 0))}})})
    m.anims["walk"]["bones"]["cloth"] = {"rot": K((0, (14, 0, 0)), (0.55, (-6, 0, 0)), (1.1, (14, 0, 0)))}
    m.attacks = {"slam": "slam", "shockwave": "stomp", "charge": "lunge"}
    m.melee = "swipe"
    return m


@studio("mudclub")
def mudclub():
    """Mudclub, a horned bog ogre: mossy dark green hide, two curved pale horns, a scowling brow over red
    eyes, a wide grin full of square white teeth over a black goatee, a ragged brown loincloth, iron bands
    on its wrists and a heavy knotted log club with iron studs."""
    m = Model("mudclub", "biped", 1.6)
    SK, SKL, SKD = "green_terracotta", "moss_block", "black_terracotta"
    humanoid(m, hip=13, legx=5.5, neck=33, shoulder=33, armx=13.5, jaw=(0, 34, 5))
    m.bone("cloth", "hips", (0, 13, 6))
    m.bone("club", "armR", (-13.5, 8, 2))
    m.hold = {"club": 30}
    legs(m, 5.5, 14, 7.5, 7.5, SK, foot=SKD, foot_h=2, toe=1.0)
    B(m, "hips", "brown_terracotta", (-9.5, 12, -6.5), (19, 3, 13))
    B(m, "cloth", "brown_wool", (-6, 3, 6.0), (12, 10, 0.9))
    for x in (-5, -2, 1.5, 4.5):
        B(m, "cloth", "brown_wool", (x - 0.75, 1.6, 6.0), (1.5, 1.5, 0.9))   # ragged hem
    B(m, "hips", "brown_wool", (-6, 4, -7.4), (12, 9, 0.9))
    B(m, "body", SK, (-9.5, 15, -6), (19, 9, 12))
    B(m, "body", SK, (-11.5, 23, -7), (23, 12, 14))
    B(m, "body", SKL, (-11, 31, -6.5), (22, 1.2, 13.6))
    for sd in (1, -1):
        B(m, "body", SK, (sd * 11.5 - 4.5, 27, -6.5), (9, 7.5, 13))
        B(m, "body", SKL, (sd * 11.5 - 4, 34.5, -6), (8, 0.8, 12))
    speckle(m, "body", (-11.5, 23, -7), (23, 12, 14), "front", [SKL], 5, "mud-chest", cell=1.8)
    speckle(m, "body", (-11.5, 23, -7), (23, 12, 14), "back", [SKL, SKD], 6, "mud-back", cell=1.8)
    # head with brow, red eyes and the horns
    B(m, "head", SK, (-6, 33, -4), (12, 10, 10))
    B(m, "head", SKL, (-5.5, 42.6, -3.5), (11, 0.8, 9))
    B(m, "head", SKD, (-6.4, 39.4, 5.6), (5.8, 1.6, 1.4), (0, 0, -14), (-3.5, 40, 6))
    B(m, "head", SKD, (0.6, 39.4, 5.6), (5.8, 1.6, 1.4), (0, 0, 14), (3.5, 40, 6))
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 3 - 1.4, 37.4, 6.0), (2.8, 1.8, 0.2))
        B(m, "head", "red_concrete", (sd * 3 - (1.0 if sd > 0 else 0.4), 37.6, 6.1), (1.4, 1.4, 0.2), light=True)
    C(m, "head", SK, (0, 36.6, 6.6), (2.6, 3, 1.6))                         # nose
    B(m, "head", SKD, (-0.9, 35.4, 7.3), (0.6, 0.6, 0.2)); B(m, "head", SKD, (0.3, 35.4, 7.3), (0.6, 0.6, 0.2))
    for sd in (1, -1):
        chain(m, "head", "bone_block", (sd * 5.5, 41, 0), [(3, (2.6, 2.6), (0, 0, -70 * sd)), (3, (2.2, 2.2), (0, 0, -30 * sd)),
                                                         (2.6, (1.8, 1.8), (0, 0, 0)), (2, (1.2, 1.2), (-10, 0, 35 * sd), "white_concrete")])
    # the grin: upper teeth on the head, lower jaw with teeth and goatee
    B(m, "head", "black_concrete", (-4.6, 33.2, 5.9), (9.2, 2.2, 0.3))
    for k in range(5):
        B(m, "head", "white_concrete", (-4.2 + k * 1.75, 34.0, 6.0), (1.4, 1.3, 0.4))
    B(m, "jaw", SK, (-5.6, 30, -2), (11.2, 4, 8.2))
    for k in range(4):
        B(m, "jaw", "white_concrete", (-3.4 + k * 1.75, 33.1, 6.0), (1.4, 1.0, 0.4))
    B(m, "jaw", "black_wool", (-2.6, 27.4, 4.6), (5.2, 3.2, 1.8))
    B(m, "jaw", "black_wool", (-1.4, 26.2, 4.8), (2.8, 1.4, 1.4))
    arms(m, 14, 34, 7.5, 7.5, SK, SK, SKD, 26, hand_h=7, hand_w=9)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, "iron_block", (sd * 14 - 4.0, 9.5, -4.0), (8.0, 1.6, 8.0))
    # the club: a log that gets thicker, with iron studs and a knot
    C(m, "club", "spruce_log", (-13.5, 11, 2), (2.6, 12, 2.6))
    C(m, "club", "stripped_spruce_log", (-13.5, 22, 2), (4.6, 12, 4.6))
    C(m, "club", "spruce_log", (-13.5, 29, 2), (5.6, 3.2, 5.6))
    C(m, "club", "spruce_log", (-11.2, 24, 2), (1.2, 2.4, 2.4))
    for y, x, z in ((19, -16.0, 2), (23, -11.0, 3), (21, -13.5, 4.5), (25, -13.5, -0.5), (27, -16.0, 1)):
        C(m, "club", "iron_block", (x, y, z), (1.2, 1.2, 1.2))
    m.rest("body", (8, 0, 0)); m.rest("head", (-8, 0, 0))
    m.bend = -20
    standard_anims(m, heavy=1.2, extra={"idle": idle_biped(4.0, 18, extra={"cloth": {"rot": wave(0, 5, 2.0, base=(3, 0, 0))}})})
    m.anims["walk"]["bones"]["cloth"] = {"rot": K((0, (14, 0, 0)), (0.55, (-6, 0, 0)), (1.1, (14, 0, 0)))}
    m.attacks = {"slam": "slam", "leap": "lunge", "shockwave": "stomp"}
    m.melee = "swipe"
    return m


@studio("king_oldbeard")
def king_oldbeard():
    """King Oldbeard, an old villager king: the long villager head with its big nose, bushy white brows and a
    beard down to his belt, a gold crown with red gems, a red robe with a spotted white fur collar and trim, a
    gold belt, brown boots and a gold sceptre topped with a sun."""
    m = Model("king_oldbeard", "biped", 1.0)
    SKIN, SKD, ROBE, ROBED, FUR, GOLD = "brown_mushroom_block", "terracotta", "red_wool", "red_terracotta", "white_wool", "gold_block"
    humanoid(m, hip=8, legx=2.2, neck=20, shoulder=19.5, armx=5.5)
    m.bone("beard", "head", (0, 20, 4))
    m.bone("cape", "body", (0, 19, -3))
    m.bone("staff", "armR", (-5.5, 5, 1.5))
    m.hold = {"staff": 0}
    legs(m, 2.2, 8, 3.8, 4, ROBED, foot="brown_terracotta", foot_h=1.6, toe=0.8, shin="brown_terracotta")
    # robe: a long skirt and chest, gold belt, fur trim down the front
    B(m, "hips", ROBE, (-5, 3, -3), (10, 6, 6))
    B(m, "hips", FUR, (-5.2, 2.4, -3.2), (10.4, 1.2, 6.4))
    B(m, "body", ROBE, (-4.5, 9, -2.8), (9, 11, 5.6))
    B(m, "body", GOLD, (-4.7, 9.4, -3.0), (9.4, 1.2, 6.0))
    B(m, "body", "emerald_block", (-0.6, 9.5, 3.0), (1.2, 1.0, 0.2))
    B(m, "hips", FUR, (-1.2, 3.6, 3.0), (2.4, 5.4, 0.3))
    # the fur collar: spotted ermine over the shoulders
    B(m, "body", FUR, (-6.4, 16.6, -3.6), (12.8, 3.6, 7.2))
    for x, z in ((-4.6, 3.65), (-1.0, 3.65), (2.6, 3.65), (5.5, 1.0), (-5.9, -1.5), (0.8, -3.65)):
        B(m, "body", "black_wool", (x, 18.0, z), (0.8, 0.8, 0.1) if abs(z) > 3 else (0.1, 0.8, 0.8))
    B(m, "cape", ROBE, (-5.5, 3.2, -4.2), (11, 14, 1))
    B(m, "cape", FUR, (-5.6, 2.6, -4.3), (11.2, 1.0, 1.2))
    # the villager head with its nose, brows, beard and crown
    B(m, "head", SKIN, (-4, 20, -4), (8, 10, 8))
    B(m, "head", SKD, (-4.05, 20, -4.05), (8.1, 1.0, 8.1))
    C(m, "head", SKIN, (0, 22.4, 5.2), (2.4, 4.4, 2.4))
    C(m, "head", SKD, (0, 21.0, 5.1), (2.0, 0.8, 1.8))
    eye(m, "head", 2, 25.0, 4, 2, 1.2, 0.2, white="white_concrete", pupil="green_concrete", pw=1.0, ph=1.2, look=(-0.5, 0))
    eye(m, "head", -2, 25.0, 4, 2, 1.2, 0.2, white="white_concrete", pupil="green_concrete", pw=1.0, ph=1.2, look=(0.5, 0))
    B(m, "head", FUR, (-4.2, 26.0, 3.9), (3.6, 1.4, 1.2), (0, 0, 8), (-2.5, 26.5, 4))
    B(m, "head", FUR, (0.6, 26.0, 3.9), (3.6, 1.4, 1.2), (0, 0, -8), (2.5, 26.5, 4))
    B(m, "beard", FUR, (-4.1, 13, 3.6), (8.2, 9, 1.6))
    B(m, "beard", FUR, (-3.2, 11, 3.8), (6.4, 2.2, 1.4))
    B(m, "beard", FUR, (-1.8, 9.6, 3.9), (3.6, 1.6, 1.2))
    B(m, "beard", "light_gray_wool", (-1.2, 18.6, 5.1), (2.4, 1.0, 0.3))
    B(m, "head", FUR, (-4.3, 20.5, -3.5), (1.4, 6, 6))                       # side and back hair
    B(m, "head", FUR, (2.9, 20.5, -3.5), (1.4, 6, 6))
    B(m, "head", FUR, (-4.3, 20.5, -4.4), (8.6, 7, 1.2))
    B(m, "head", GOLD, (-4.4, 29.6, -4.4), (8.8, 2.0, 8.8))
    for x, z in ((-4.4, -4.4), (-0.7, -4.4), (3.0, -4.4), (-4.4, 3.0), (-0.7, 3.0), (3.0, 3.0), (-4.4, -0.7), (3.0, -0.7)):
        B(m, "head", GOLD, (x, 31.6, z), (1.4, 1.6, 1.4))
    for x in (-2.4, 1.4):
        B(m, "head", "red_concrete", (x, 30.1, 4.4), (1.0, 1.0, 0.2), light=True)
    B(m, "head", "blue_concrete", (-0.5, 30.1, 4.4), (1.0, 1.0, 0.2), light=True)
    # arms in red sleeves with fur cuffs
    arms(m, 5.8, 19.5, 3.4, 3.6, ROBE, ROBE, SKIN, 11, hand_h=2.6)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, FUR, (sd * 5.8 - 2.0, 10.4, -2.1), (4.0, 1.4, 4.2))
    # the sceptre: gold rod with a sun on top
    C(m, "staff", GOLD, (-5.8, 9, 3.6), (1.0, 18, 1.0))
    C(m, "staff", GOLD, (-5.8, 18.8, 3.6), (3.0, 3.0, 3.0))
    C(m, "staff", "yellow_concrete", (-5.8, 18.8, 3.6), (4.4, 1.0, 1.0), light=True)
    C(m, "staff", "yellow_concrete", (-5.8, 18.8, 3.6), (1.0, 4.4, 1.0), light=True)
    C(m, "staff", "orange_concrete", (-5.8, 18.8, 5.15), (1.4, 1.4, 0.2), light=True)
    m.bend = -30
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(4.0, 16, extra={"beard": {"rot": wave(0, 4, 2.0, base=(2, 0, 0))}})})
    m.attacks = {"minions": "roar", "orbs": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@studio("hay_golem")
def hay_golem():
    """A golem of stacked hay bales tied with red twine: a square bale body, a smaller bale head crowned with
    straw spikes, two dark slit eyes, thick bale arms and stumpy legs, straw sticking out of every joint."""
    m = Model("hay_golem", "biped", 1.2)
    HAY, TW, TWD = "hay_block", "red_terracotta", "red_wool"
    humanoid(m, hip=6, legx=3.2, neck=19, shoulder=17.5, armx=8)
    legs(m, 3.2, 6.5, 4.6, 5, HAY, foot=HAY, foot_h=1.4, toe=0.4)
    B(m, "body", HAY, (-6.5, 6, -5), (13, 13, 10))
    for y in (8.5, 14.0):
        B(m, "body", TW, (-6.6, y, -5.1), (13.2, 1.4, 10.2))
    B(m, "body", TWD, (-1.0, 9.9, 5.0), (2.0, 4.1, 0.2))
    B(m, "head", HAY, (-4.5, 19, -4.2), (9, 7, 8.4))
    B(m, "head", TW, (-4.6, 21.0, -4.3), (9.2, 1.0, 8.6))
    B(m, "head", "black_concrete", (-3.2, 23.0, 4.21), (2.2, 1.0, 0.2))
    B(m, "head", "black_concrete", (1.0, 23.0, 4.21), (2.2, 1.0, 0.2))
    B(m, "head", "yellow_concrete", (-2.6, 23.1, 4.32), (0.8, 0.6, 0.1), light=True)
    B(m, "head", "yellow_concrete", (1.6, 23.1, 4.32), (0.8, 0.6, 0.1), light=True)
    # the straw crown: thin spikes of different heights, leaning out
    spikes = ((-3.5, -3, 5, -12), (-1.5, -3.2, 7, -4), (0.5, -3, 6, 4), (2.8, -3, 5, 10), (-3.6, -0.5, 6, -14), (-1.2, -0.6, 8, -2),
              (1.3, -0.4, 7.5, 6), (3.4, -0.6, 5.5, 14), (-3.4, 2.2, 4.5, -10), (-0.8, 2.4, 6, -2), (1.6, 2.2, 5, 8), (3.6, 2.4, 4, 16))
    for x, z, h, tilt in spikes:
        C(m, "head", HAY if h > 5 else "yellow_terracotta", (x, 26 + h / 2, z), (1.4, h, 1.4), (0, 0, -tilt), (x, 26, z))
    # straw tufts at the joints
    for sd in (1, -1):
        for dz in (-2, 1.5):
            C(m, "body", "yellow_terracotta", (sd * 7.2, 18.4, dz), (0.8, 2.6, 0.8), (0, 0, -30 * sd))
    arms(m, 8.6, 18, 4.4, 5, HAY, HAY, HAY, 13, hand_h=4)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, TW, (sd * 8.6 - 2.3, 6.2, -2.6), (4.6, 1.2, 5.2))
    m.bend = -20
    standard_anims(m, heavy=1.0)
    m.attacks = {"fire_ring": "stomp", "slam": "slam"}
    m.melee = "swipe"
    return m


@studio("gravelord")
def gravelord():
    """The Bone Collector: a hunched grey ghoul in a torn black hood, with sunken black eye pits lit by two
    soul-blue sparks, a long crooked nose and a jagged grin, long thin arms ending in hooked claws, a rope
    belt, and a huge patched burlap sack of skulls on its back that sways as it shuffles. A soul lantern
    hangs from one hand on a chain."""
    m = Model("gravelord", "biped", 1.6)
    SK, SKD, HOOD, HOODL, SACK, SACKD = "cyan_terracotta", "gray_terracotta", "black_wool", "gray_wool", "packed_mud", "brown_terracotta"
    humanoid(m, hip=13, legx=4, neck=33, shoulder=31.5, armx=10, jaw=(0, 34, 3))
    m.bone("sack", "body", (0, 30, -7))
    m.bone("hem", "hips", (0, 12, 0))
    m.bone("lantern", "armL", (10.5, 4, 2))
    m.hold = {"lantern": 0}
    legs(m, 4, 13, 4.2, 4.4, SK, foot=SKD, foot_h=1.4, toe=1.6, shin=SK)
    for sd in (1, -1):
        for k in range(3):
            B(m, "legL" if sd > 0 else "legR", "bone_block", (sd * 4 - 1.9 + k * 1.4, 0, 5.4), (0.8, 0.8, 1.2))
    # the robe: a ragged skirt, a rope belt and the hunched back
    B(m, "hips", HOOD, (-6.5, 10, -4.5), (13, 6, 9))
    for i, x in enumerate((-6.0, -3.5, -1.0, 1.5, 4.0)):
        B(m, "hem", HOOD if i % 2 else HOODL, (x, 4.5 + (i % 3) * 1.2, -4.7), (2.5, 6 - (i % 3) * 1.2, 9.4))
    B(m, "hips", "brown_terracotta", (-6.7, 14.2, -4.7), (13.4, 1.2, 9.4))
    B(m, "hips", "brown_terracotta", (2.4, 10.4, 4.6), (1.0, 3.8, 0.6))
    B(m, "body", HOOD, (-7, 15, -5), (14, 16, 10))
    B(m, "body", HOODL, (-7.2, 15.2, 5.0), (3.0, 14, 0.3))
    B(m, "body", HOODL, (4.2, 15.2, 5.0), (3.0, 14, 0.3))
    B(m, "body", SK, (-2.5, 25, 5.0), (5, 5, 0.4))                     # bare chest showing ribs
    for y in (26, 27.6):
        B(m, "body", SKD, (-2.2, y, 5.4), (4.4, 0.5, 0.1))
    # the hood: plates round a gaunt grey face that juts forward
    B(m, "head", SK, (-4.5, 31.5, -2.5), (9, 9, 8))
    B(m, "head", HOOD, (-5.6, 31, -4.5), (1.2, 12, 10.5))
    B(m, "head", HOOD, (4.4, 31, -4.5), (1.2, 12, 10.5))
    B(m, "head", HOOD, (-5.6, 40.6, -4.5), (11.2, 2.4, 10.5))
    B(m, "head", HOOD, (-5.6, 31, -5.6), (11.2, 11, 1.2))
    B(m, "head", HOOD, (-1.2, 42.6, -5.4), (2.4, 2.2, 3), (-30, 0, 0))   # the hood's point
    B(m, "head", HOODL, (-4.6, 40.0, 5.4), (9.2, 0.8, 0.6))
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 2.2 - 1.5, 36.2, 5.5), (3.0, 2.6, 0.2))
        B(m, "head", "light_blue_concrete", (sd * 2.2 - 0.5, 36.9, 5.6), (1.0, 1.0, 0.2), light=True)
        B(m, "head", SKD, (sd * 2.2 - 1.6, 38.6, 5.4), (3.2, 0.8, 0.6))
    C(m, "head", SK, (0, 35.2, 6.6), (1.8, 3.4, 2.4), (-20, 0, 0))          # crooked nose
    C(m, "head", SKD, (0.2, 33.8, 7.6), (1.4, 1.2, 1.4))
    B(m, "jaw", SK, (-3.8, 31.0, -1.5), (7.6, 2.4, 7.0))
    B(m, "jaw", "black_concrete", (-3, 32.6, 5.4), (6, 0.9, 0.2))
    teeth(m, "jaw", -3, 3, 32.6, 5.8, "bone_block", n=4, h=1.2, w=0.8, down=False, jag=True, d=0.4)
    # long thin arms with hooked claws
    arms(m, 9.5, 31, 3.6, 3.6, HOOD, SK, SK, 24, hand_h=3)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, HOODL, (sd * 9.5 - 2.1, 17.6, -2.1), (4.2, 1.4, 4.2))
        for k in range(3):
            C(m, a, "bone_block", (sd * 9.5 + (k - 1) * 1.1, 4.4, 1.8), (0.7, 2.6, 0.7), (25, 0, 0))
    # the sack of skulls on its back
    B(m, "sack", SACK, (-9, 15, -20), (18, 19, 14))
    B(m, "sack", SACK, (-10, 18, -19), (20, 13, 12))
    B(m, "sack", SACK, (-7.5, 34, -18.5), (15, 3, 11))
    B(m, "sack", SACKD, (-9.1, 24, -20.1), (18.2, 1.2, 14.2))
    B(m, "sack", "stripped_oak_log", (-5, 19, -20.4), (5, 5, 0.4))       # a patch
    for x in (-4.4, -0.6): B(m, "sack", SACKD, (x, 21.4, -20.6), (0.6, 0.6, 0.2))
    B(m, "sack", "brown_terracotta", (-2.6, 36.6, -15.4), (5.2, 1.6, 5.2))  # the tie
    for x, z, y in ((-4, -16, 37.2), (3, -14.5, 37.6), (0, -18, 38.4)):
        B(m, "sack", "bone_block", (x - 1.6, y, z - 1.5), (3.2, 2.8, 3))
        B(m, "sack", "black_concrete", (x - 1.2, y + 1.2, z + 1.51), (0.9, 0.9, 0.1))
        B(m, "sack", "black_concrete", (x + 0.3, y + 1.2, z + 1.51), (0.9, 0.9, 0.1))
    B(m, "sack", "bone_block", (7.6, 30, -12), (1.2, 8, 1.2), (0, 0, -24))  # a bone poking out
    C(m, "sack", "bone_block", (11.4, 37.4, -11.4), (2.2, 1.6, 2.2), (0, 0, -24))
    for sd in (1, -1):                                                    # straps over the shoulders
        B(m, "body", "brown_terracotta", (sd * 4 - 1, 15, 4.9), (2, 16, 0.5))
        B(m, "body", "brown_terracotta", (sd * 4 - 1, 30.4, -5.5), (2, 0.8, 10.6))
    # the soul lantern on its chain
    C(m, "lantern", "chain", (10.5, 4.6, 2), (0.8, 2.0, 0.8))
    C(m, "lantern", "soul_lantern", (10.5, 2.6, 2), (3.4, 3.8, 3.4), light=True)
    m.rest("body", (16, 0, 0)); m.rest("head", (-14, 0, 0))
    m.bend = -26
    standard_anims(m, heavy=0.9, weapon="R", extra={
        "idle": idle_biped(4.0, 22, extra={"sack": {"rot": wave2((5, 3, 4), 4.0)}, "lantern": {"rot": wave(2, 14, 2.0)},
                                            "hem": {"rot": wave(0, 4, 2.0)}}),
    })
    m.anims["walk"]["bones"]["sack"] = {"rot": K((0, (6, 0, 5)), (0.55, (2, 0, -5)), (1.1, (6, 0, 5)))}
    m.anims["walk"]["bones"]["lantern"] = {"rot": K((0, (-15, 0, 0)), (0.55, (15, 0, 0)), (1.1, (-15, 0, 0)))}
    m.attacks = {"skulls": "cast", "pull": "lunge", "minions": "roar"}
    m.melee = "swipe"
    return m


@studio("ember_queen")
def ember_queen():
    """The Forge Mother: a broad smith giantess with soot-dark skin, two thick copper braids bound with gold
    rings, a scorched leather apron over a furnace in her belly that glows through an iron grate, rolled
    sleeves, heavy black gloves, iron boots and a huge forge hammer with a glowing hot face."""
    m = Model("ember_queen", "biped", 1.6)
    SK, SKL, HAIR, HAIRD, APRON, APD, GLOVE = "brown_terracotta", "terracotta", "orange_terracotta", "cut_copper", "brown_wool", "spruce_planks", "black_wool"
    humanoid(m, hip=13, legx=5, neck=33, shoulder=32, armx=12.5, jaw=(0, 35, 4))
    m.bone("braidL", "head", (5, 40, -2)); m.bone("braidR", "head", (-5, 40, -2))
    m.bone("apron", "body", (0, 16, 6))
    m.bone("hammer", "armR", (-12.5, 6, 2))
    m.hold = {"hammer": 20}
    legs(m, 5, 13, 6.4, 6.8, "black_wool", foot="dark_oak_planks", foot_h=2.4, toe=1.4, shin="brown_terracotta")
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, "dark_oak_planks", (sd * 5 - 3.5, 6.6, -3.6), (7.0, 1.4, 7.2))                   # boot cuffs
        B(m, leg, "gold_block", (sd * 5 - 0.6, 4.0, 3.45), (1.2, 1.2, 0.2))
    B(m, "hips", "black_wool", (-8.5, 11, -5.5), (17, 5, 11))
    B(m, "hips", "brown_terracotta", (-8.7, 14.6, -5.7), (17.4, 1.4, 11.4))
    B(m, "hips", "gold_block", (-1.2, 14.4, 5.5), (2.4, 1.8, 0.4))
    # torso: a broad chest, the furnace belly with its grate
    B(m, "body", SK, (-9.5, 16, -6), (19, 17, 12))
    B(m, "body", "gray_wool", (-9.7, 26, -6.2), (19.4, 7, 12.4))               # vest
    B(m, "apron", APRON, (-7, 4, 6.0), (14, 25, 1.0))
    B(m, "apron", APD, (-7.1, 4, 6.2), (14.2, 1.0, 1.0))
    B(m, "apron", "blackstone", (-3.0, 5, 6.3), (2.4, 2.4, 0.2))               # scorch marks
    B(m, "apron", "blackstone", (3.0, 9, 6.3), (1.6, 1.6, 0.2))
    B(m, "apron", "polished_blackstone", (-5, 14.5, 6.5), (10, 9, 0.6))        # the furnace door
    B(m, "apron", "magma_block", (-4, 15.5, 6.6), (8, 7, 0.6), light=True)
    B(m, "apron", "shroomlight", (-2.5, 16.5, 6.7), (5, 4, 0.6), light=True)
    for k in range(4):
        B(m, "apron", "netherite_block", (-4 + k * 2.4, 15.5, 7.1), (0.8, 7, 0.4))
    B(m, "apron", "netherite_block", (-5, 18.6, 7.1), (10, 0.8, 0.4))
    for sd in (1, -1):                                                         # apron straps
        B(m, "body", APRON, (sd * 4.5 - 1, 29, 6.0), (2, 4, 0.6))
        B(m, "body", SK, (sd * 9.5 - (2.4 if sd > 0 else 1.6), 27, -4.5), (4, 6, 9))  # shoulders
    # head: a broad face, ember eyes, a stern mouth, and the copper hair with braids
    B(m, "head", SK, (-5.5, 33, -4.5), (11, 11, 10))
    B(m, "head", HAIR, (-5.8, 42, -4.8), (11.6, 2.6, 10.0))
    B(m, "head", HAIR, (-5.8, 35, -4.8), (11.6, 6, 2.6))
    B(m, "head", HAIR, (-5.8, 41.6, 3.2), (11.6, 1.6, 2.0))
    B(m, "head", HAIR, (-5.8, 39.8, 3.6), (4.2, 2.0, 1.8), (0, 0, 14), (-3.7, 40.8, 4.5))          # a swept fringe
    B(m, "head", HAIRD, (1.0, 41.0, 5.1), (4.6, 0.8, 0.3))
    C(m, "head", HAIR, (0, 45.4, -1.5), (5.6, 2.6, 5.0))                                           # top knot
    C(m, "head", "gold_block", (0, 44.4, -1.5), (6.0, 0.8, 5.4))
    for sd in (1, -1):
        B(m, "head", HAIR, (sd * 5.8 - (1.4 if sd > 0 else 0), 34, -4.8), (1.4, 8, 9))
        eye(m, "head", sd * 2.4, 38.2, 5.5, 2.6, 1.6, 0.3, white="white_concrete", pupil="orange_concrete", pw=1.4, ph=1.4, look=(-0.4 * sd, 0))
        B(m, "head", "black_terracotta", (sd * 2.4 - 1.6, 39.4, 5.5), (3.2, 0.9, 0.6), (0, 0, -10 * sd))
        B(m, "head", "black_terracotta", (sd * 3.5 - 0.6, 35.6, 5.55), (1.2, 0.6, 0.1))   # soot smudge
    C(m, "head", SKL, (0, 36.8, 6.0), (2.0, 2.4, 1.4))
    B(m, "jaw", SK, (-4.5, 32.6, -3), (9, 3, 7.6))
    B(m, "jaw", "black_concrete", (-2.4, 34.6, 4.5), (4.8, 0.7, 0.2))
    for sd, br in ((1, "braidL"), (-1, "braidR")):
        for k in range(5):
            C(m, br, HAIR if k % 2 == 0 else HAIRD, (sd * 5.4, 38.6 - k * 3, -5.6 - k * 0.3), (2.8, 3.2, 2.8))
        C(m, br, "gold_block", (sd * 5.4, 35.3, -5.9), (3.2, 0.9, 3.2))
        C(m, br, "gold_block", (sd * 5.4, 26.5, -7.0), (3.0, 0.9, 3.0))
    # arms: bare and strong, rolled sleeves, heavy gloves
    arms(m, 12.5, 32.5, 6.4, 6.4, SK, SK, GLOVE, 24, hand_h=6.4, hand_w=7.6)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, "gray_wool", (sd * 12.5 - 3.4, 27.5, -3.4), (6.8, 5, 6.8))
        B(m, a, GLOVE, (sd * 12.5 - 3.5, 8.0, -3.5), (7.0, 3.2, 7.0))
    # the forge hammer
    C(m, "hammer", "stripped_dark_oak_log", (-12.5, 14, 2), (1.8, 26, 1.8))
    C(m, "hammer", "netherite_block", (-12.5, 27, 2), (5, 5, 10))
    C(m, "hammer", "polished_deepslate", (-12.5, 27, -0.5), (5.4, 5.4, 1.0))
    C(m, "hammer", "polished_deepslate", (-12.5, 27, 4.5), (5.4, 5.4, 1.0))
    C(m, "hammer", "gold_block", (-12.5, 23.6, 2), (2.4, 1.0, 2.4))
    C(m, "hammer", "orange_concrete", (-12.5, 27, 7.1), (4, 4, 0.3), light=True)
    m.rest("body", (4, 0, 0))
    m.bend = -24
    standard_anims(m, heavy=1.3, extra={"idle": idle_biped(4.0, 16, extra={
        "braidL": {"rot": wave(0, 5, 2.0, base=(4, 0, 0))}, "braidR": {"rot": wave(0, 5, 2.0, 0.4, base=(4, 0, 0))},
        "apron": {"rot": wave(0, 3, 4.0, base=(2, 0, 0))}})})
    m.anims["walk"]["bones"]["apron"] = {"rot": K((0, (8, 0, 0)), (0.55, (-3, 0, 0)), (1.1, (8, 0, 0)))}
    m.attacks = {"fire_ring": "stomp", "meteor": "cast", "slam": "slam"}
    m.melee = "swipe"
    return m


@studio("clockwork_colossus")
def clockwork_colossus():
    """The Clockwork Colossus: a riveted copper and iron giant wound up by a great gold key turning in its back.
    Its chest is a round glass window onto a turning gold gear with a glowing core; its eyes are two lit
    slits in a domed iron helm with a steam whistle on top, twin exhaust stacks puff behind its shoulders,
    and its arms are iron pistons that end in heavy riveted fists."""
    m = Model("clockwork_colossus", "biped", 1.6)
    CU, CUL, CUD, FE, FED = "cut_copper", "copper_block", "exposed_copper", "netherite_block", "polished_deepslate"
    humanoid(m, hip=13, legx=5.5, neck=33, shoulder=31, armx=13)
    m.bone("gear", "body", (0, 24.5, 6.5))
    m.bone("key", "body", (0, 25, -7))
    m.bone("whistle", "head", (0, 42, 0))
    legs(m, 5.5, 13, 6, 6.4, FED, foot=CU, foot_h=2.6, toe=1.4, shin=CU)
    for sd in (1, -1):
        B(m, "legL" if sd > 0 else "legR", FE, (sd * 5.5 - 3.4, 6, -3.4), (6.8, 2.2, 6.8))     # knee plates
    B(m, "hips", CUD, (-8, 11, -5), (16, 5, 10))
    B(m, "hips", FE, (-8.2, 13.4, -5.2), (16.4, 1.2, 10.4))
    # the barrel chest: copper plates, rivets, the glass window over the gear
    B(m, "body", CU, (-10, 16, -6.5), (20, 16, 13))
    B(m, "body", CUL, (-10.2, 30, -6.7), (20.4, 2.4, 13.4))
    B(m, "body", FE, (-6.5, 19.5, 6.4), (13, 10, 0.5))
    B(m, "body", FE, (-5.5, 18.5, 6.4), (11, 12, 0.5))
    B(m, "body", "black_concrete", (-5, 20, 6.7), (10, 9, 0.2))
    import math as _m
    C(m, "gear", "gold_block", (0, 24.5, 7.1), (6.4, 6.4, 0.4))
    C(m, "gear", "gold_block", (0, 24.5, 7.1), (6.4, 6.4, 0.4), (0, 0, 45))
    for k in range(8):
        a = k * 45
        C(m, "gear", "raw_gold_block", (3.9 * _m.sin(_m.radians(a)), 24.5 + 3.9 * _m.cos(_m.radians(a)), 7.1), (1.6, 1.6, 0.4), (0, 0, -a))
    C(m, "gear", "black_concrete", (0, 24.5, 7.3), (2.6, 2.6, 0.1))
    C(m, "gear", "shroomlight", (0, 24.5, 7.35), (1.6, 1.6, 0.2), light=True)
    B(m, "body", "light_blue_stained_glass", (-5, 20, 7.4), (10, 9, 0.2))
    for x, y in ((-9, 17), (8, 17), (-9, 28.6), (8, 28.6), (-7.5, 31), (6.5, 31)):
        B(m, "body", "gold_block", (x, y, 6.5), (1, 1, 0.3))
    for x, y, w, h in ((-10.1, 16.5, 3, 4), (7.4, 26, 2.8, 3), (-10.1, 27, 0.3, 3)):            # verdigris patina
        B(m, "body", "weathered_copper", (x, y, 6.45), (w, h, 0.2))
    B(m, "body", "oxidized_copper", (10.05, 18, -3), (0.2, 4, 5))
    for sd in (1, -1):                                         # pauldrons and exhaust stacks
        B(m, "body", CUL, (sd * 12 - 4.5, 27, -6), (9, 6, 12))
        B(m, "body", FE, (sd * 12 - 4.6, 32.6, -6.1), (9.2, 1, 12.2))
        B(m, "body", FED, (sd * 5 - 1.6, 30, -9.5), (3.2, 11, 3.2))
        B(m, "body", "blackstone", (sd * 5 - 1.8, 40.5, -9.7), (3.6, 1, 3.6))
    # the helm: a domed iron head with lit eye slits and a whistle
    B(m, "head", FE, (-6, 33, -5), (12, 9, 10))
    B(m, "head", FE, (-5, 42, -4), (10, 1.6, 8))
    B(m, "head", FED, (-6.2, 33, -5.2), (12.4, 1.2, 10.4))
    B(m, "head", "black_concrete", (-5, 37, 5.0), (10, 2.6, 0.2))
    B(m, "head", "yellow_concrete", (-4.4, 37.5, 5.1), (3.6, 1.6, 0.2), light=True)
    B(m, "head", "yellow_concrete", (0.8, 37.5, 5.1), (3.6, 1.6, 0.2), light=True)
    B(m, "head", FED, (-0.6, 34, 5.0), (1.2, 7.6, 0.5))
    for x in (-3.6, -1.2, 1.2, 3.6):
        B(m, "head", "black_concrete", (x - 0.3, 34.0, 5.05), (0.6, 1.8, 0.2))                 # mouth grille
    C(m, "whistle", CUL, (0, 44.6, 0), (2.2, 2.4, 2.2))
    C(m, "whistle", "gold_block", (0, 46.4, 0), (1.2, 1.4, 1.2))
    # piston arms with riveted fists
    arms(m, 13.5, 31.5, 6, 6, FED, FE, CU, 25, hand_h=6.6, hand_w=8)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, CUL, (sd * 13.5 - 3.4, 18.5, -3.4), (6.8, 1.8, 6.8))
        B(m, a, "polished_deepslate", (sd * 13.5 - 1.2, 9.6, 3.0), (2.4, 9, 0.6))
    # the wind-up key: shaft and a bow of two loops
    C(m, "key", "gold_block", (0, 25, -9), (2, 2, 4))
    C(m, "key", "gold_block", (0, 25, -12.2), (11, 3, 1.4))
    C(m, "key", "gold_block", (0, 25, -12.2), (3, 8, 1.4))
    C(m, "key", "raw_gold_block", (0, 25, -12.2), (3.6, 3.6, 1.6))
    m.bend = -20
    spin = K((0, Z), (1.0, (0, 0, 90)), (2.0, (0, 0, 180)), (3.0, (0, 0, 270)), (4.0, (0, 0, 360)))
    keyspin = K((0, Z), (1.0, (0, 0, -90)), (2.0, (0, 0, -180)), (3.0, (0, 0, -270)), (4.0, (0, 0, -360)))
    standard_anims(m, heavy=1.4, extra={"idle": idle_biped(4.0, 14, breath=0.012, extra={"gear": {"rot": spin}, "key": {"rot": keyspin},
                                                                                              "whistle": {"pos": K((0, Z), (3.4, Z), (3.6, (0, 0.6, 0)), (4.0, Z))}})})
    m.anims["walk"]["bones"]["gear"] = {"rot": K((0, Z), (0.55, (0, 0, 90)), (1.1, (0, 0, 180)))}
    m.attacks = {"slam": "slam", "charge": "lunge", "blink": "stomp", "darkness": "roar"}
    m.melee = "swipe"
    return m


@studio("mayor_grumble")
def mayor_grumble():
    """Mayor Grumble, the village mayor as a person: the long villager head with its big nose, one thick
    unibrow over green eyes and a grumpy frown, a tall black top hat with a red band, a green coat with gold
    buttons, a red sash, a gold chain of office with a big emerald, grey trousers and polished black shoes,
    and a heavy wooden gavel."""
    m = Model("mayor_grumble", "biped", 1.6)
    SKIN, SKD, COAT, COATD, SASH = "brown_mushroom_block", "terracotta", "green_wool", "green_terracotta", "red_wool"
    humanoid(m, hip=13, legx=3.4, neck=31, shoulder=30.5, armx=8.5)
    m.bone("hat", "head", (0, 47, 0))
    m.bone("tails", "hips", (0, 14, -4))
    m.bone("gavel", "armR", (-8.5, 9, 1.5))
    m.hold = {"gavel": 25}
    legs(m, 3.4, 13, 5.2, 5.4, "gray_wool", foot="black_concrete", foot_h=1.6, toe=1.6, shin="gray_wool")
    B(m, "hips", COAT, (-7, 11, -4.2), (14, 5, 8.4))
    B(m, "tails", COAT, (-6.5, 5, -4.6), (13, 9, 1.0))
    B(m, "tails", COATD, (-0.3, 5, -4.7), (0.6, 8, 0.2))
    # coat with a red sash, gold buttons and the chain of office
    B(m, "body", COAT, (-7.5, 15, -4.5), (15, 16, 9))
    B(m, "body", "white_wool", (-1.8, 22, 4.4), (3.6, 9, 0.3))                 # shirt front
    for y in (17, 19.5, 22):
        B(m, "body", "gold_block", (-0.5, y, 4.6), (1, 1, 0.3))
    B(m, "body", SASH, (-7.7, 15.4, -4.7), (15.4, 2.4, 9.4))
    B(m, "body", SASH, (3.5, 12.4, 4.4), (2.4, 3.6, 0.5))
    B(m, "body", "gold_block", (-5.5, 28, 4.5), (11, 0.9, 0.4))
    B(m, "body", "gold_block", (-4.5, 26.3, 4.5), (1, 2, 0.4)); B(m, "body", "gold_block", (3.5, 26.3, 4.5), (1, 2, 0.4))
    B(m, "body", "gold_block", (-1.6, 23.4, 4.6), (3.2, 3.2, 0.5))
    B(m, "body", "emerald_block", (-1.0, 24.0, 5.1), (2.0, 2.0, 0.3), light=True)
    for sd in (1, -1):
        B(m, "body", COATD, (sd * 4.5 - 1.5, 15.2, 4.5), (3, 15.6, 0.2))       # lapels
        B(m, "body", COAT, (sd * 8 - 2.5, 27, -4.2), (5, 4, 8.4))
        B(m, "body", "gold_block", (sd * 8 - 2.5, 30.8, -4.2), (5, 0.6, 8.4))    # epaulettes
    # the villager head: tall, big nose, unibrow, grumpy
    B(m, "head", SKIN, (-5, 31, -5), (10, 12, 10))
    B(m, "head", SKD, (-5.05, 31, -5.05), (10.1, 1.2, 10.1))
    C(m, "head", SKIN, (0, 33.8, 6.4), (2.6, 5.6, 2.8))
    C(m, "head", SKD, (0, 31.6, 6.5), (2.6, 1.0, 2.6))
    eye(m, "head", 2.5, 37.4, 5, 2.6, 1.6, 0.3, white="white_concrete", pupil="green_concrete", pw=1.2, ph=1.6, look=(-0.6, 0))
    eye(m, "head", -2.5, 37.4, 5, 2.6, 1.6, 0.3, white="white_concrete", pupil="green_concrete", pw=1.2, ph=1.6, look=(0.6, 0))
    B(m, "head", "black_terracotta", (-4.6, 38.6, 5.0), (9.2, 1.4, 0.9))
    B(m, "head", "black_terracotta", (-0.8, 38.2, 5.4), (1.6, 0.8, 0.5))
    B(m, "head", "black_terracotta", (-2.0, 32.0, 5.05), (4.0, 0.6, 0.2))
    B(m, "head", "black_terracotta", (-2.4, 31.4, 5.05), (0.8, 0.8, 0.2)); B(m, "head", "black_terracotta", (1.6, 31.4, 5.05), (0.8, 0.8, 0.2))
    for sd in (1, -1):
        B(m, "head", "light_gray_wool", (sd * 5 - (0.8 if sd > 0 else 0), 37, -4), (0.8, 3, 6))   # grey sideburns
    # the top hat
    B(m, "hat", "black_wool", (-7.5, 43, -7.5), (15, 1.2, 15))
    B(m, "hat", "black_wool", (-5.2, 44.2, -5.2), (10.4, 10, 10.4))
    B(m, "hat", "red_wool", (-5.3, 44.4, -5.3), (10.6, 1.8, 10.6))
    B(m, "hat", "gold_block", (2.0, 44.5, 5.35), (1.6, 1.6, 0.2))
    B(m, "hat", "gray_wool", (-5.0, 53.8, -5.0), (10, 0.6, 10))
    # arms in green sleeves, white cuffs
    arms(m, 9.5, 30.5, 4.6, 4.8, COAT, COAT, SKIN, 16, hand_h=4)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, "white_wool", (sd * 9.5 - 2.5, 16.6, -2.6), (5.0, 1.2, 5.2))
    # the gavel
    C(m, "gavel", "stripped_dark_oak_log", (-9.5, 13, 3.0), (1.2, 10, 1.2))
    C(m, "gavel", "dark_oak_planks", (-9.5, 18.8, 3.0), (3.6, 3.6, 7))
    C(m, "gavel", "gold_block", (-9.5, 18.8, 3.0), (3.8, 3.8, 0.8))
    m.bend = -28
    standard_anims(m, heavy=0.9, extra={"idle": idle_biped(4.0, 18, extra={"hat": {"rot": wave(2, 3, 4.0, 0.2)}, "tails": {"rot": wave(0, 4, 2.0, base=(4, 0, 0))}})})
    m.anims["walk"]["bones"]["tails"] = {"rot": K((0, (14, 0, 0)), (0.55, (6, 0, 0)), (1.1, (14, 0, 0)))}
    m.attacks = {"minions": "roar", "volley": "cast", "quake": "slam", "roar": "stomp"}
    m.melee = "swipe"
    return m


@studio("bloodtusk")
def bloodtusk():
    """Old Tusker, the war boar of the red banner: a great bristly boar in dark brown with a black ridge of
    stiff hair down its back, a broad pink snout, two huge curved tusks, little angry eyes, red war paint
    stripes, an iron plate saddle strapped over its back and a tall red banner on a pole that flaps above it."""
    m = Model("bloodtusk", "quad", 1.6)
    FUR, FURD, FURL, SNOUT, PAINT = "brown_wool", "brown_terracotta", "spruce_planks", "pink_terracotta", "red_terracotta"
    m.bone("body", "root", (0, 16, 0))
    for sd, s in ((1, "L"), (-1, "R")):
        m.bone("legF" + s, "body", (sd * 6.5, 14, 9))
        m.bone("legB" + s, "body", (sd * 6.5, 14, -10))
    m.bone("neck", "body", (0, 20, 12))
    m.bone("head", "neck", (0, 19, 15))
    m.bone("jaw", "head", (0, 10.4, 17))
    m.bone("tail", "body", (0, 22, -15))
    m.bone("flag", "body", (0, 32, -8))
    for sd, s in ((1, "L"), (-1, "R")):
        for leg, z in (("legF" + s, 9), ("legB" + s, -10)):
            B(m, leg, FUR, (sd * 6.5 - 2.8, 6, z - 2.8), (5.6, 10, 5.6))
            B(m, leg, FURD, (sd * 6.5 - 2.5, 2, z - 2.5), (5.0, 4.2, 5.0))
            B(m, leg, "black_terracotta", (sd * 6.5 - 2.8, 0, z - 2.6), (5.6, 2.0, 6.0))
            B(m, leg, "gray_terracotta", (sd * 6.5 - 0.4, 0, z + 2.4), (0.8, 2.0, 1.0))      # cloven hoof
    # the body: deep and front-heavy, a bristle ridge down the spine
    B(m, "body", FUR, (-9, 12, -15), (18, 14, 28))
    B(m, "body", FUR, (-10, 14, 1), (20, 15, 13))
    B(m, "body", FURD, (-8.5, 11.6, -13), (17, 1, 24))
    for k in range(7):
        z = 11 - k * 4
        h = 4.5 - abs(k - 2) * 0.5
        B(m, "body", "black_wool", (-1.6, 29 if z > 0 else 26, z - 1.6), (3.2, h, 3.4))
    # war paint and the plate saddle
    for z in (6, 0):
        B(m, "body", PAINT, (-10.1, 18, z), (0.2, 9, 1.6)); B(m, "body", PAINT, (9.9, 18, z), (0.2, 9, 1.6))
    B(m, "body", "iron_block", (-9.6, 25.6, -10), (19.2, 1.4, 12))
    B(m, "body", "polished_andesite", (-10.2, 19, -9.5), (1.2, 7, 11)); B(m, "body", "polished_andesite", (9.0, 19, -9.5), (1.2, 7, 11))
    B(m, "body", "red_wool", (-8.5, 27, -9), (17, 1.0, 10))
    B(m, "body", "brown_terracotta", (-10.3, 12.5, -5), (20.6, 14.6, 1.6))                  # girth strap
    for x in (-8.6, 7.6):
        B(m, "body", "gold_block", (x, 26.0, -1.2), (1.0, 1.0, 1.0))
    # neck and the big head with its snout, tusks and eyes
    B(m, "neck", FUR, (-8, 14, 9), (16, 14, 8))
    B(m, "head", FUR, (-8, 9, 13), (16, 15, 10))
    B(m, "head", FUR, (-6.5, 9.5, 22.5), (13, 10, 3))                                          # the muzzle
    B(m, "head", FURL, (-7.5, 23.6, 13.5), (15, 0.8, 9))
    B(m, "head", "black_wool", (-2, 24, 13.5), (4, 2.4, 8))                                        # bristle crest
    B(m, "head", SNOUT, (-5, 9.5, 25.2), (10, 6.5, 2.6))
    B(m, "head", "black_terracotta", (-3.4, 12.4, 27.75), (2.0, 2.2, 0.2)); B(m, "head", "black_terracotta", (1.4, 12.4, 27.75), (2.0, 2.2, 0.2))
    B(m, "head", "brown_terracotta", (-5.2, 15.8, 25.0), (10.4, 0.6, 2.9))
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 4.6 - 1.3, 19.4, 22.9), (2.6, 2.0, 0.2))
        B(m, "head", "red_concrete", (sd * 4.6 - (0.7 if sd > 0 else 0.1), 19.9, 23.0), (0.8, 1.0, 0.2), light=True)
        C(m, "head", "black_wool", (sd * 4.6, 21.9, 23.1), (4.2, 1.2, 0.8), (0, 0, -18 * sd))
        C(m, "head", FUR, (sd * 8, 23, 17), (3.2, 4.4, 1.6), (20, 0, -30 * sd))                  # ears
        C(m, "head", SNOUT, (sd * 8.5, 22.6, 17.6), (1.4, 2.4, 0.4), (20, 0, -30 * sd))
        B(m, "head", PAINT, (sd * 7.3 - 0.6, 16, 22.95), (1.2, 4.6, 0.2))                     # cheek stripes
        chain(m, "jaw", "bone_block", (sd * 5.6, 10.6, 25.0), [(3.0, (2.4, 2.4), (75, 0, -35 * sd)), (3.4, (2.0, 2.0), (35, 0, -25 * sd)),
                                                          (3.0, (1.6, 1.6), (-5, 0, -10 * sd)), (2.2, (1.1, 1.1), (-35, 0, 5 * sd), "white_concrete")])
    B(m, "jaw", FURD, (-5.5, 8.0, 17), (11, 2.4, 10))
    B(m, "jaw", "pink_terracotta", (-4.5, 10.2, 20), (9, 0.4, 6.5))
    # the tail and the banner on its pole
    chain(m, "tail", FUR, (0, 23, -15), [(3, (1.4, 1.4), (-130, 0, 0)), (3, (1.2, 1.2), (-160, 0, 0)), (1.6, (2.2, 2.2), (-170, 0, 0), "black_wool")])
    C(m, "flag", "stripped_dark_oak_log", (0, 39, -8), (1.2, 26, 1.2))
    C(m, "flag", "gold_block", (0, 52.6, -8), (1.8, 1.8, 1.8))
    B(m, "flag", "red_wool", (-0.4, 40, -16.5), (0.8, 11, 8))
    B(m, "flag", "red_wool", (-0.4, 37.5, -16.5), (0.8, 2.5, 3.5))
    B(m, "flag", "black_wool", (-0.5, 43.5, -13.8), (1.0, 4, 3))                               # a tusk sign on it
    B(m, "flag", "white_wool", (-0.55, 44.5, -13.1), (1.1, 2, 1.6))
    m.no_knees = True
    look = K((0, (0, -6, 0)), (1.2, (6, -14, 4)), (2.0, (6, -14, 4)), (3.0, (-2, 14, -4)), (4.0, (0, -6, 0)))
    m.anims = {
        "idle": loop(4.0, {
            "body": {"pos": K((0, Z), (1.0, (0, 0.5, 0)), (2.0, Z), (3.0, (0, 0.5, 0)), (4.0, Z)), "scl": breathe(2.0, 0.02)},
            "neck": {"rot": K((0, Z), (1.2, (8, -6, 0)), (2.0, (8, -6, 0)), (3.0, (-4, 8, 0)), (4.0, Z))},
            "head": {"rot": look},
            "jaw": {"rot": K((0, Z), (0.6, (6, 0, 0)), (0.9, Z), (2.6, (4, 0, 0)), (3.0, Z), (4.0, Z))},
            "tail": {"rot": wave(1, 24, 1.0)},
            "flag": {"rot": wave2((4, 10, 3), 2.0)}}),
        "walk": loop(0.9, {
            "legFL": {"rot": K((0, (26, 0, 0)), (0.45, (-26, 0, 0)), (0.9, (26, 0, 0)))},
            "legBR": {"rot": K((0, (26, 0, 0)), (0.45, (-26, 0, 0)), (0.9, (26, 0, 0)))},
            "legFR": {"rot": K((0, (-26, 0, 0)), (0.45, (26, 0, 0)), (0.9, (-26, 0, 0)))},
            "legBL": {"rot": K((0, (-26, 0, 0)), (0.45, (26, 0, 0)), (0.9, (-26, 0, 0)))},
            "body": {"pos": K((0, Z), (0.225, (0, 0.9, 0)), (0.45, Z), (0.675, (0, 0.9, 0)), (0.9, Z)), "rot": K((0, (0, 0, 2)), (0.45, (0, 0, -2)), (0.9, (0, 0, 2)))},
            "head": {"rot": K((0, (4, 0, 0)), (0.45, (-4, 0, 0)), (0.9, (4, 0, 0)))},
            "tail": {"rot": wave(1, 20, 0.45)},
            "flag": {"rot": K((0, (-8, 0, 0)), (0.45, (-4, 6, 0)), (0.9, (-8, 0, 0)))}}),
        # head down, paw the ground, then charge
        "charge": attack(1.5, 1.0, {
            "body": {"rot": K((0, Z), (0.6, (10, 0, 0)), (1.0, (6, 0, 0)), (1.5, Z))},
            "root": {"pos": K((0, Z), (0.6, (0, 0, -4)), (1.0, (0, 0, 22)), (1.2, (0, 0, 22)), (1.5, Z))},
            "head": {"rot": K((0, Z), (0.6, (28, 0, 0)), (1.0, (-18, 0, 0)), (1.5, Z))},
            "legFL": {"rot": K((0, Z), (0.2, (-30, 0, 0)), (0.35, (20, 0, 0)), (0.5, (-30, 0, 0)), (0.65, (20, 0, 0)), (1.0, (-40, 0, 0)), (1.5, Z))},
            "legFR": {"rot": K((0, Z), (0.8, (-40, 0, 0)), (1.0, (30, 0, 0)), (1.5, Z))},
            "legBL": {"rot": K((0, Z), (0.8, (40, 0, 0)), (1.0, (-30, 0, 0)), (1.5, Z))},
            "legBR": {"rot": K((0, Z), (0.8, (40, 0, 0)), (1.0, (-30, 0, 0)), (1.5, Z))},
            "flag": {"rot": K((0, Z), (1.0, (-25, 0, 0)), (1.5, Z))}}),
        # rear up and crash down on the front hooves
        "rear": attack(1.6, 1.0, {
            "body": {"rot": K((0, Z), (0.7, (-34, 0, 0)), (1.0, (8, 0, 0)), (1.25, (6, 0, 0)), (1.6, Z)),
                     "pos": K((0, Z), (0.7, (0, 5, -3)), (1.0, Z), (1.6, Z))},
            "legFL": {"rot": K((0, Z), (0.7, (-70, 0, 0)), (1.0, (16, 0, 0)), (1.6, Z))},
            "legFR": {"rot": K((0, Z), (0.7, (-82, 0, 0)), (1.0, (16, 0, 0)), (1.6, Z))},
            "legBL": {"rot": K((0, Z), (0.7, (34, 0, 0)), (1.0, (-8, 0, 0)), (1.6, Z))},
            "legBR": {"rot": K((0, Z), (0.7, (34, 0, 0)), (1.0, (-8, 0, 0)), (1.6, Z))},
            "head": {"rot": K((0, Z), (0.7, (-14, 0, 0)), (1.0, (18, 0, 0)), (1.6, Z))},
            "jaw": {"rot": K((0, Z), (0.7, (24, 0, 0)), (1.1, Z), (1.6, Z))},
            "flag": {"rot": K((0, Z), (0.7, (30, 0, 0)), (1.0, (-20, 0, 0)), (1.6, Z))}}),
        # a hooking toss of the tusks
        "toss": attack(1.1, 0.55, {
            "head": {"rot": K((0, Z), (0.35, (30, -10, 0)), (0.55, (-45, 14, 0)), (0.8, (-34, 10, 0)), (1.1, Z))},
            "neck": {"rot": K((0, Z), (0.35, (14, 0, 0)), (0.55, (-14, 0, 0)), (1.1, Z))},
            "body": {"rot": K((0, Z), (0.35, (6, 0, 0)), (0.55, (-6, 0, 0)), (1.1, Z))}}),
        "bite": attack(0.8, 0.4, {
            "head": {"rot": K((0, Z), (0.25, (-18, 0, 0)), (0.4, (22, 0, 0)), (0.8, Z))},
            "jaw": {"rot": K((0, Z), (0.25, (30, 0, 0)), (0.4, Z), (0.8, Z))},
            "body": {"pos": K((0, Z), (0.25, (0, 0, -2)), (0.4, (0, 0, 4)), (0.8, Z))}}),
    }
    m.attacks = {"charge": "charge", "minions": "rear", "shockwave": "toss"}
    m.melee = "bite"
    return m


@studio("sunscorch")
def sunscorch():
    """Sunscorch, a little sun on its summer holiday: a cube of glowing orange jelly around a white-hot core,
    a crown of flame rays, big pink heart sunglasses, a wide melting grin with its tongue out, drips running
    down its sides and a yellow duck swim ring round its middle."""
    m = Model("sunscorch", "slime", 1.6)
    m.bone("body", "root", (0, 0, 0))
    m.bone("inner", "body", (0, 10, 0))
    m.bone("mouth", "body", (0, 9, 9))
    m.bone("ring", "body", (0, 6, 0))
    m.bone("rays", "body", (0, 21, 0))
    JEL, JELD = "orange_stained_glass", "orange_terracotta"
    # the jelly: a thick glass shell with a lit core inside
    C(m, "inner", "shroomlight", (0, 10.5, 0), (9, 9, 9), light=True)
    B(m, "body", "orange_concrete", (-9, 0.6, -9), (18, 19, 18))
    B(m, "body", "orange_concrete", (-8, 19.6, -8), (16, 1, 16))
    B(m, "body", "orange_terracotta", (-9.1, 0.6, -9.1), (18.2, 2.0, 18.2))
    B(m, "body", "yellow_concrete", (-7.8, 17.2, 9.05), (3.4, 1.4, 0.1), light=True)               # shine
    B(m, "body", "yellow_concrete", (-7.8, 15.4, 9.05), (1.4, 1.4, 0.1), light=True)
    B(m, "body", "yellow_concrete", (-9.05, 17.2, 4), (0.1, 1.4, 3.4), light=True)
    B(m, "body", "orange_concrete", (-9.2, 0, -9.2), (18.4, 0.8, 18.4))
    for x, z, h in ((-9.1, 3, 6), (-9.1, -4, 4), (9.1, -2, 7), (9.1, 5, 3.5), (-3, -9.1, 5), (5, -9.1, 3)):
        if abs(x) > 9:
            B(m, "body", "orange_concrete", (x - 0.4, 10 - h, z), (0.8, h, 1.4))
            B(m, "body", "orange_concrete", (x - 0.6, 10 - h - 1.2, z + 0.1), (1.2, 1.3, 1.2))
        else:
            B(m, "body", "orange_concrete", (x, 10 - h, z - 0.4), (1.4, h, 0.8))
    # face on the front: heart sunglasses, the grin and tongue
    for sd in (1, -1):
        cx = sd * 4.2
        B(m, "body", "pink_concrete", (cx - 3.4, 12, 9.0), (6.8, 4.6, 0.8))
        B(m, "body", "pink_concrete", (cx - 2.6, 11.0, 9.0), (5.2, 1.2, 0.8))
        B(m, "body", "pink_concrete", (cx - 1.2, 10.0, 9.0), (2.4, 1.2, 0.8))
        B(m, "body", "magenta_stained_glass", (cx - 2.6, 12.6, 9.7), (5.2, 3.0, 0.3))
        B(m, "body", "white_concrete", (cx - 1.8, 14.6, 10.0), (1.2, 0.6, 0.1), light=True)
        B(m, "body", "pink_concrete", (cx - 3.4, 16.4, 9.0), (2.6, 0.9, 0.8)); B(m, "body", "pink_concrete", (cx + 0.8, 16.4, 9.0), (2.6, 0.9, 0.8))
        B(m, "body", "pink_concrete", (sd * 8.4 - 0.5, 14.6, 1), (1.0, 0.8, 8.4))                 # arms of the glasses
    B(m, "body", "pink_concrete", (-1.0, 14.2, 9.0), (2.0, 0.9, 0.8))
    B(m, "mouth", "black_concrete", (-5.5, 5.4, 9.0), (11, 3.4, 0.4))
    B(m, "mouth", "black_concrete", (-6.5, 6.6, 9.0), (1.2, 2.4, 0.4)); B(m, "mouth", "black_concrete", (5.3, 6.6, 9.0), (1.2, 2.4, 0.4))
    teeth(m, "mouth", -5, 5, 8.8, 9.6, "white_concrete", n=5, h=1.2, w=1.4, down=True, d=0.5)
    B(m, "mouth", "red_concrete", (-2.4, 3.4, 9.2), (4.8, 3.0, 0.8))
    B(m, "mouth", "pink_concrete", (-0.4, 3.8, 10.0), (0.8, 2.0, 0.1))
    # the crown of flame rays
    for k in range(8):
        import math
        a = k * math.pi / 4
        x, z = math.cos(a) * 6.2, math.sin(a) * 6.2
        tall = 5.5 if k % 2 == 0 else 3.8
        C(m, "rays", "yellow_concrete", (x, 21 + tall / 2, z), (2.6, tall, 2.6), light=True)
        C(m, "rays", "orange_concrete", (x, 21 + tall + 0.8, z), (1.4, 1.8, 1.4), light=True)
    # the duck swim ring
    for x, z, w, d in ((-10, -12, 20, 3), (-10, 9, 20, 3), (-12, -10, 3, 20), (9, -10, 3, 20)):
        B(m, "ring", "yellow_concrete", (x, 1, z), (w, 3.4, d))
    for x, z in ((-12.1, -5), (-12.1, 4), (11.1, -5), (11.1, 4)):
        B(m, "ring", "white_concrete", (x, 1.2, z), (1.0, 3.0, 2))
    B(m, "ring", "yellow_concrete", (9.5, 2.5, 6.5), (5, 6, 5))                                    # duck head, off to the side
    B(m, "ring", "yellow_concrete", (10, 4, 4), (4, 2.6, 2.6))
    B(m, "ring", "orange_concrete", (11, 4.2, 11.5), (3, 1.4, 2.4))
    B(m, "ring", "black_concrete", (9.4, 6.4, 9.5), (0.2, 1, 1)); B(m, "ring", "black_concrete", (14.4, 6.4, 9.5), (0.2, 1, 1))
    m.anims = {
        "idle": loop(2.0, {
            "body": {"scl": K((0, (1, 1, 1)), (1.0, (1.05, 0.94, 1.05)), (2.0, (1, 1, 1)))},
            "inner": {"rot": K((0, Z), (1.0, (0, 45, 0)), (2.0, (0, 90, 0))), "scl": K((0, (1, 1, 1)), (0.5, (1.1, 1.1, 1.1)), (1.0, (1, 1, 1)), (1.5, (1.1, 1.1, 1.1)), (2.0, (1, 1, 1)))},
            "rays": {"rot": K((0, Z), (2.0, (0, 45, 0)))},
            "ring": {"rot": wave(2, 3, 2.0), "pos": bobpos(2.0, 0.4)},
            "mouth": {"scl": K((0, (1, 1, 1)), (1.0, (1.05, 1.15, 1)), (2.0, (1, 1, 1)))}}),
        "walk": loop(1.0, {
            "body": {"scl": K((0, (1, 1, 1)), (0.3, (1.12, 0.84, 1.12)), (0.55, (0.92, 1.12, 0.92)), (1.0, (1, 1, 1)))},
            "root": {"pos": K((0, Z), (0.3, Z), (0.6, (0, 5, 0)), (0.9, Z), (1.0, Z))},
            "ring": {"pos": K((0, Z), (0.6, (0, -1.5, 0)), (1.0, Z))},
            "rays": {"rot": K((0, Z), (1.0, (0, 45, 0)))}}),
        "hop": attack(0.8, 0.55, {
            "body": {"scl": K((0, (1, 1, 1)), (0.2, (1.15, 0.8, 1.15)), (0.4, (0.9, 1.15, 0.9)), (0.55, (1.2, 0.75, 1.2)), (0.8, (1, 1, 1)))},
            "root": {"pos": K((0, Z), (0.2, Z), (0.4, (0, 10, 6)), (0.55, (0, 0, 10)), (0.8, Z))}}),
        "slam": attack(1.5, 1.0, {
            "body": {"scl": K((0, (1, 1, 1)), (0.4, (1.25, 0.65, 1.25)), (0.6, (0.85, 1.25, 0.85)), (0.95, (1, 1, 1)), (1.0, (1.4, 0.55, 1.4)), (1.5, (1, 1, 1)))},
            "root": {"pos": K((0, Z), (0.4, Z), (0.75, (0, 40, 0)), (1.0, Z), (1.5, Z))},
            "rays": {"rot": K((0, Z), (1.0, (0, 180, 0)), (1.5, (0, 270, 0)))}}),
        "burst": attack(1.1, 0.65, {
            "body": {"scl": K((0, (1, 1, 1)), (0.5, (0.85, 0.85, 0.85)), (0.65, (1.3, 1.2, 1.3)), (1.1, (1, 1, 1)))},
            "rays": {"scl": K((0, (1, 1, 1)), (0.5, (0.8, 0.8, 0.8)), (0.65, (1.5, 1.8, 1.5)), (1.1, (1, 1, 1)))},
            "inner": {"rot": K((0, Z), (0.65, (0, 180, 0)), (1.1, (0, 360, 0)))}}),
        "spit": attack(1.0, 0.6, {
            "body": {"rot": K((0, Z), (0.45, (-14, 0, 0)), (0.6, (10, 0, 0)), (1.0, Z))},
            "mouth": {"scl": K((0, (1, 1, 1)), (0.45, (1.1, 1.4, 1)), (0.6, (1.3, 1.8, 1)), (1.0, (1, 1, 1)))}}),
    }
    m.attacks = {"leap": "slam", "quake": "hop", "fire_ring": "burst", "volley": "spit"}
    m.melee = "hop"
    return m


# ------------------------------------------------------------------------------------------------ pumpkins
# Carved faces drawn as pixel art on the front of a ribbed pumpkin: k is the dark carved hole, r its rim,
# g the candle glow seen through it (lit), o pumpkin flesh (teeth left in the cut).
PUMPKIN_FACES = {
    "idle": ["..............", "..r........r..", ".rkr......rkr.", "rkkkr....rkkkr", "..............", "..............",
             "rr..........rr", ".rkkkkkkkkkkr.", "..rkokkkkokr..", "....rrrrrr...."],
    "happy": ["..............", "...r......r...", "..rkr....rkr..", ".rkgkr..rkgkr.", "..............", "r............r",
              "rkr........rkr", ".rkkkkkkkkkkr.", "..rkkokkokkr..", "....rrrrrr...."],
    "surprised": [".rr........rr.", "rkkr......rkkr", "rkgr......rgkr", ".rr........rr.", "..............", ".....rrrr.....",
                  "....rkkkkr....", "....rkggkr....", "....rkkkkr....", ".....rrrr....."],
    "angry": ["rr..........rr", ".rkr......rkr.", "..rkr....rkr..", "..rkgr..rgkr..", "...rr....rr...", "..............",
              ".rkkkkkkkkkkr.", ".rkokkokkokkr.", "..rkkkkkkkkr..", "...rrrrrrrr..."],
    "sleepy": ["..............", "..............", ".rrrr....rrrr.", "..kkr....rkk..", "..............", "..............",
               "...rrrrrrrr...", "...rkkkkkkr...", "....rrrrrr....", ".............."],
    "wink": ["..............", "...r..........", "..rkr...rrrr..", ".rkgkr...kk...", "..............", "r............r",
             "rkr........rkr", ".rkkkkkkkkkkr.", "..rkkkk..rr...", "....rrr.rppr..", "........rppr.."],
    "hurt": ["..............", "rr.........rr.", ".rkr.....rkr..", "..rkr...rkr...", ".rkr.....rkr..", "..............",
             ".....rrrr.....", "....rkkkkr....", "...rkkkkkkr...", "....rrrrrr...."],
    "rage": ["rr..........rr", "rgkr......rkgr", ".rggr....rggr.", "..rgkr..rkgr..", "..............", "r............r",
             "rgr..r..r..rgr", ".rggggggggggr.", "..rgogggogrr..", "...rrrrrrrr..."],
    "dead": ["..............", ".rkr.r..r.rkr.", "..rkr....rkr..", ".rkr.r..r.rkr.", "..............", "..............",
             "...rrrrrrrr...", "..rkkkkkkkkr..", "..............", ".............."],
}


def pumpkin(m, bone, cx, y0, cz, w, h, d, faces, stem=True, glow=False, base="orange_concrete", rib="orange_terracotta", px=1.0, tag_all=True):
    """A ribbed pumpkin: a core with rounded edges, darker grooves down every side, a curly stem and leaf on top,
    and one carved face plate for each state (tagged face:<state>, only one shows at a time)."""
    x0, z0 = cx - w / 2, cz - d / 2
    B(m, bone, base, (x0, y0 + 1, z0), (w, h - 2, d))
    B(m, bone, base, (x0 + 1, y0, z0 + 1), (w - 2, h, d - 2))
    B(m, bone, base, (x0 - 0.6, y0 + 2, z0 + 1.5), (w + 1.2, h - 4, d - 3))
    B(m, bone, base, (x0 + 1.5, y0 + 2, z0 - 0.6), (w - 3, h - 4, d + 1.2))
    B(m, bone, base, (x0 + w * 0.22, y0 + 3, z0 - 1.0), (w * 0.56, h - 6, d + 1.6))
    B(m, bone, base, (x0 - 1.0, y0 + 3, z0 + d * 0.22), (w + 2.0, h - 6, d * 0.56))
    B(m, bone, rib, (x0 + 1.5, y0 - 0.1, z0 + 1.5), (w - 3, 0.3, d - 3))
    n = max(2, int(w // 4))
    for k in range(1, n):
        gx = x0 + w * k / n
        B(m, bone, rib, (gx - 0.4, y0 + 1.6, z0 - 1.1 if 0.22 * w < gx - x0 < 0.78 * w else z0 - 0.7), (0.8, h - 3.2, 0.2))
        B(m, bone, rib, (gx - 0.4, y0 + 0.6, z0 + d + 0.5), (0.8, 1.2, 0.2))
        B(m, bone, rib, (gx - 0.4, y0 + h - 1.8, z0 + d + 0.5), (0.8, 1.2, 0.2))
        B(m, bone, rib, (gx - 0.4, y0 + h + 0.0, z0 + 1.5), (0.8, 0.1, d - 3))
    for k in range(1, max(2, int(d // 4))):
        gz = z0 + d * k / max(2, int(d // 4))
        o = 0.4 if 0.22 * d < gz - z0 < 0.78 * d else 0
        B(m, bone, rib, (x0 - 0.8 - o, y0 + 1.6, gz - 0.4), (0.2, h - 3.2, 0.8)); B(m, bone, rib, (x0 + w + 0.6 + o, y0 + 1.6, gz - 0.4), (0.2, h - 3.2, 0.8))
    if stem:
        C(m, bone, "dark_oak_log", (cx, y0 + h + 1.2, cz), (2, 2.6, 2))
        C(m, bone, "dark_oak_log", (cx + 1.0, y0 + h + 2.8, cz), (1.6, 1.4, 1.4), (0, 0, -30))
        C(m, bone, "green_terracotta", (cx - 2.2, y0 + h + 0.5, cz + 1), (3.2, 0.6, 2.4), (0, 20, 12))
    keys = {"k": "black_concrete", "r": "brown_terracotta", "g": "yellow_concrete", "o": base, "p": "red_concrete"}
    lit = {"g", "p"} if True else set()
    for state in faces:
        rows = PUMPKIN_FACES[state]
        H, W = len(rows), max(len(r) for r in rows)
        sx = (w - 1.5) / W if px is None else px
        ox, oy = cx - W * sx / 2, y0 + h / 2 + 0.5 - H * sx / 2
        for j, r in enumerate(rows):
            i = 0
            while i < len(r):
                ch = r[i]
                if ch in ". ":
                    i += 1; continue
                k = i
                while k < len(r) and r[k] == ch: k += 1
                yy = oy + (H - 1 - j) * sx
                c = B(m, bone, keys[ch], (ox + i * sx, yy, z0 + d + 0.62), ((k - i) * sx, sx, 0.08), light=(ch in lit and (glow or state == "rage")))
                c["g"] = "face:" + state
                i = k


def decor_pumpkin(id, w, h, d, faces, docs):
    @studio(id, revise=False)
    def build():
        m = Model(id, "slime", 1.0)
        m.bone("body", "root", (0, 0, 0))
        pumpkin(m, "body", 0, 0, 0, w, h, d, faces)
        m.anims = {"idle": loop(3.0, {"body": {"scl": K((0, (1, 1, 1)), (1.5, (1.03, 0.97, 1.03)), (3.0, (1, 1, 1))),
                                               "rot": K((0, Z), (0.75, (0, 0, 3)), (1.5, Z), (2.25, (0, 0, -3)), (3.0, Z))}})}
        m.attacks = {}
        m.melee = "hop"
        return m
    build.__name__ = id
    build.__doc__ = docs
    return build


decor_pumpkin_tall = decor_pumpkin("decor_pumpkin_tall", 16, 18, 15, ["idle", "happy", "surprised", "angry", "sleepy", "wink"],
                                   "A tall goofy pumpkin that pulls faces: happy, surprised, angry, sleepy and a cheeky wink.")
decor_pumpkin_flat = decor_pumpkin("decor_pumpkin_flat", 18, 11, 16, ["idle", "happy", "surprised", "angry", "sleepy", "wink"],
                                   "A squat wide goofy pumpkin that pulls faces.")
decor_pumpkin_cube = decor_pumpkin("decor_pumpkin_cube", 15, 15, 15, ["idle", "happy", "surprised", "angry", "sleepy", "wink"],
                                   "A round goofy pumpkin that pulls faces.")


@studio("gourd_king")
def gourd_king():
    """The Gourd King: a giant ribbed pumpkin head with a carved face that changes as he fights (a toothy grin, a
    snarl when he attacks, a yelp when hit, a burning glare below half health), a cloak of dark leaves over a body
    of twisted green vines, a glowing ember heart in his chest, thorny vine arms and a lantern of embers on a chain."""
    m = Model("gourd_king", "biped", 1.6)
    V, VD, LEAF = "green_terracotta", "moss_block", "dark_oak_leaves"
    humanoid(m, hip=13, legx=4.2, neck=31, shoulder=30, armx=10)
    m.bone("cloak", "body", (0, 30, -4))
    m.bone("lantern", "armL", (10.5, 9.5, 2.6))
    m.hold = {"lantern": 0}
    legs(m, 4.2, 13, 4.6, 4.8, V, foot=VD, foot_h=1.8, toe=1.6)
    for sd in (1, -1):
        chain(m, "legL" if sd > 0 else "legR", VD, (sd * 4.2, 13, 2.6), [(5, (1.2, 1.2), (10, 0, 30 * sd)), (5, (1.0, 1.0), (-10, 0, -20 * sd))])
    B(m, "hips", V, (-6, 11, -3.5), (12, 5, 7))
    # a body of twisted vines round the ember heart
    for i, (x, rz) in enumerate(((-4.5, 8), (-1.5, -6), (1.5, 6), (4.5, -8))):
        C(m, "body", V if i % 2 else VD, (x, 23, 0), (3.2, 15, 4.4), (0, 0, rz))
    B(m, "body", V, (-7, 26, -3.5), (14, 5, 7))
    C(m, "body", "shroomlight", (0, 22, 1.5), (4, 4, 3), light=True)
    C(m, "body", "orange_concrete", (0, 22, 3.2), (2.4, 2.4, 0.3), light=True)
    # leaf cloak and leafy shoulders
    B(m, "cloak", "green_wool", (-7.5, 12, -5.0), (15, 18, 1.0))
    for x in (-6, -3, 0, 3, 6):
        B(m, "cloak", "green_wool", (x - 1.2, 10.5 - abs(x) * 0.15, -5.0), (2.4, 2, 1.0))
    for sd in (1, -1):
        C(m, "body", "green_wool", (sd * 8, 30.5, 0), (8, 2, 8), (0, 0, -14 * sd))
        C(m, "body", "lime_terracotta", (sd * 10.5, 29.4, 0), (4, 1.4, 6), (0, 0, -26 * sd))
    # the pumpkin head with all the faces
    pumpkin(m, "head", 0, 31, 0.5, 18, 15, 16, ["idle", "angry", "hurt", "rage", "dead"], glow=True)
    # a little crown of thorns round the stem
    for k, (x, z) in enumerate(((-4, -3), (0, -4.5), (4, -3), (-3, 3), (3, 3))):
        C(m, "head", "dark_oak_log", (x, 47, z + 0.5), (1.0, 2.4, 1.0), (0, 0, (k - 2) * 12))
    # vine arms with thorns and leaf hands
    arms(m, 10.5, 30, 3.6, 3.6, V, VD, V, 22, hand_h=3.6)
    for sd, a in ((1, "armL"), (-1, "armR")):
        for y in (25, 19, 13):
            C(m, a, "dark_oak_log", (sd * (10.5 + 2.0), y, 0), (1.4, 0.6, 0.6), (0, 0, -30 * sd))
        for k in range(3):
            C(m, a, VD, (sd * 10.5 + (k - 1) * 1.2, 5.4, 1.6), (0.8, 2.6, 0.8), (20, 0, (k - 1) * 12))
    C(m, "lantern", "chain", (10.5, 8.6, 2.6), (0.8, 2.4, 0.8))
    C(m, "lantern", "spruce_planks", (10.5, 7.3, 2.6), (4.4, 0.6, 4.4))
    C(m, "lantern", "lantern", (10.5, 4.6, 2.6), (4.2, 4.8, 4.2), light=True)
    C(m, "lantern", "spruce_planks", (10.5, 1.9, 2.6), (4.6, 0.6, 4.6))
    m.bend = -24
    standard_anims(m, heavy=1.1, extra={"idle": idle_biped(4.0, 16, extra={"cloak": {"rot": wave(0, 5, 4.0, base=(6, 0, 0))},
                                                                              "lantern": {"rot": wave(2, 14, 2.0)}})})
    m.attacks = {"slam": "slam", "fire_ring": "cast", "minions": "roar", "volley": "swipe", "leap": "lunge"}
    m.melee = "swipe"
    return m


# ------------------------------------------------------------------------------------------------ hollow mages
# One small, round wizard with nothing under the hat but the dark and two eyes. The four mages share the build
# and differ in palette and in the trinkets on the hat and staff.
HOLLOW = {
    "hollow_mage": dict(hat="bamboo_planks", hatd="sandstone", band="green_concrete", bandl="lime_concrete", coat="blue_concrete", coatd="blue_wool",
                        coatl="light_blue_concrete", eye="yellow_concrete", eyed="orange_concrete", leg="green_concrete", stripe="white_concrete",
                        sleeve="white_wool", cuff="green_concrete", staff="orange_terracotta", wrap="lime_terracotta", tip=None),
    "cinder_hollow": dict(hat="nether_bricks", hatd="red_nether_bricks", band="orange_concrete", bandl="shroomlight", coat="red_concrete", coatd="red_wool",
                          coatl="orange_concrete", eye="orange_concrete", eyed="red_concrete", leg="black_concrete", stripe="orange_concrete",
                          sleeve="gray_wool", cuff="orange_concrete", staff="crimson_planks", wrap="black_wool", tip="fire"),
    "rime_hollow": dict(hat="snow_block", hatd="white_concrete", band="light_blue_concrete", bandl="packed_ice", coat="cyan_concrete", coatd="cyan_wool",
                        coatl="light_blue_concrete", eye="light_blue_concrete", eyed="blue_concrete", leg="blue_concrete", stripe="white_concrete",
                        sleeve="white_wool", cuff="light_blue_concrete", staff="birch_planks", wrap="light_blue_wool", tip="ice"),
    "bramble_hollow": dict(hat="spruce_planks", hatd="dark_oak_planks", band="red_concrete", bandl="red_wool", coat="green_concrete", coatd="moss_block",
                           coatl="lime_concrete", eye="lime_concrete", eyed="green_concrete", leg="brown_concrete", stripe="lime_concrete",
                           sleeve="mushroom_stem", cuff="green_concrete", staff="dark_oak_log", wrap="moss_block", tip="moss"),
}


def hollow(id, p):
    m = Model(id, "biped", 2.7)
    humanoid(m, hip=9, legx=2.8, neck=23, shoulder=21, armx=9)
    m.bone("hat", "head", (0, 34, 0))
    m.bone("tip", "hat", (0, 46, -1))
    m.bone("collar", "body", (0, 22, 2))
    m.bone("staff", "armL", (11, 10, 3.5))
    m.hold = {"staff": 20}
    # little legs in striped trousers and big boots
    legs(m, 2.8, 9, 4.2, 4.4, p["leg"], foot="brown_terracotta", foot_h=2.2, toe=2.2)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, p["stripe"], (sd * 2.8 - 0.8, 2.2, 2.22), (1.6, 6.8, 0.1))
        B(m, leg, "terracotta", (sd * 2.8 - 1.6, 0, 3.6), (3.2, 2.0, 1.4))                     # toe cap
    B(m, "hips", p["leg"], (-5, 7.5, -2.4), (10, 2.5, 4.8))
    # the coat: a big bell with a split at the front, a deep hem, flecks of a lighter blue
    B(m, "body", "black_concrete", (-5, 9, -3), (10, 13, 6))
    B(m, "body", p["coat"], (-9.5, 11, -6), (19, 11, 11))
    B(m, "body", p["coat"], (-10.5, 7, -6.5), (8.6, 5, 12)); B(m, "body", p["coat"], (1.9, 7, -6.5), (8.6, 5, 12))
    B(m, "body", p["coat"], (-10.5, 7, -6.5), (21, 5, 7))
    B(m, "body", p["coat"], (-11.5, 6.4, -7.2), (9.5, 3.2, 13.4)); B(m, "body", p["coat"], (2.0, 6.4, -7.2), (9.5, 3.2, 13.4))   # flared hem
    B(m, "body", p["coat"], (-11.5, 6.4, -7.2), (23, 3.2, 7))
    B(m, "body", p["coatd"], (-11.7, 6.0, -7.4), (9.7, 1.6, 13.8)); B(m, "body", p["coatd"], (2.0, 6.0, -7.4), (9.7, 1.6, 13.8))
    B(m, "body", p["coatd"], (-11.7, 6.0, -7.4), (23.4, 1.6, 7))
    B(m, "body", p["coatd"], (-2.2, 7, 5.0), (1.0, 13, 0.6)); B(m, "body", p["coatd"], (1.2, 7, 5.0), (1.0, 13, 0.6))   # front edges
    B(m, "body", "black_concrete", (-1.2, 7, 4.8), (2.4, 9, 0.6))                                  # the split
    B(m, "body", "black_concrete", (-0.7, 16, 4.8), (1.4, 2, 0.6))
    speckle(m, "body", (-9.5, 12, 5.0), (19, 9, 0), "front", [p["coatl"]], n=7, seed=hash(id) % 97, depth=0.1, cell=1.2)
    speckle(m, "body", (-10.6, 9, -5), (0, 12, 10), "left", [p["coatl"]], n=4, seed=11, depth=0.1, cell=1.2)
    speckle(m, "body", (10.6, 9, -5), (0, 12, 10), "right", [p["coatl"]], n=4, seed=12, depth=0.1, cell=1.2)
    # belt and buckle in the split
    B(m, "body", "brown_terracotta", (-5.1, 9.5, 2.9), (10.2, 1.6, 2.2))
    B(m, "body", "light_blue_terracotta", (-1.6, 8.9, 4.9), (3.2, 2.8, 0.6))
    B(m, "body", "black_concrete", (-0.7, 9.8, 5.45), (1.4, 1.0, 0.1))
    # the crossed straps on the chest
    C(m, "body", "spruce_planks", (0, 18.5, 5.2), (1.4, 8, 0.5), (0, 0, 38)); C(m, "body", "spruce_planks", (0, 18.5, 5.3), (1.4, 8, 0.5), (0, 0, -38))
    C(m, "body", "light_gray_concrete", (0, 18.5, 5.6), (1.2, 1.2, 0.2))
    # a tall turned-up collar that the face sinks into
    for sd in (1, -1):
        C(m, "collar", p["coat"], (sd * 5.8, 25.5, 3.0), (6, 9, 2), (-16, -20 * sd, -12 * sd))
        C(m, "collar", p["coatd"], (sd * 5.8, 25.5, 4.1), (4.4, 7.4, 0.2), (-16, -20 * sd, -12 * sd))
        C(m, "collar", p["coatl"], (sd * 6.4, 27.5, 4.3), (1.2, 1.2, 0.2), (-16, -20 * sd, -12 * sd))
        C(m, "collar", p["coat"], (sd * 7.4, 24.5, -2), (2, 8, 7), (0, 0, -10 * sd))
    C(m, "collar", p["coat"], (0, 24.6, -4.4), (13, 7.5, 2), (10, 0, 0))
    # the dark where the face should be, and the two eyes
    B(m, "head", "black_concrete", (-5.5, 22.5, -4.5), (11, 11.5, 9))
    B(m, "head", "black_wool", (-5.6, 31.8, -4.6), (11.2, 2.4, 9.2))
    for sd in (1, -1):
        B(m, "head", p["eye"], (sd * 2.7 - 1.1, 28, 4.55), (2.2, 3.0, 0.2), light=True)
        B(m, "head", p["eyed"], (sd * 2.7 - 1.1, 27.4, 4.55), (2.2, 0.7, 0.2), light=True)
        c = B(m, "head", "black_concrete", (sd * 2.7 - 1.1, 30.0, 4.6), (2.2, 1.0, 0.2)); c["g"] = "face:angry"
        c = B(m, "head", "black_concrete", (sd * 2.7 - 1.1, 27.2, 4.6), (2.2, 1.8, 0.2)); c["g"] = "face:hurt"
    B(m, "head", "purple_terracotta", (-1.8, 25.6, 4.55), (3.6, 0.6, 0.1))
    # the hat: a broad brim, a band and a tall crown that slumps over to one side
    B(m, "hat", p["hat"], (-13, 34, -12), (26, 2, 25))
    B(m, "hat", p["hatd"], (-12.5, 33.6, -11.5), (25, 0.5, 24))
    B(m, "hat", p["hat"], (-13.4, 34.4, 10.5), (26.8, 1.2, 3.0))
    B(m, "hat", p["band"], (-8, 36, -7), (16, 3, 14))
    B(m, "hat", p["bandl"], (1.5, 36.4, 6.95), (3, 2.2, 0.2))
    B(m, "hat", p["hat"], (-7, 39, -6), (14, 7, 12))
    B(m, "hat", p["hatd"], (-7.05, 39.0, -2), (0.1, 7, 1.2)); B(m, "hat", p["hatd"], (6.95, 39.0, 1), (0.1, 7, 1.2))
    B(m, "tip", p["hat"], (-6, 46, -5.5), (12, 6, 10), (0, 0, -14), (0, 46, -1))
    B(m, "tip", p["hat"], (2, 47, -4.5), (7, 6, 8), (0, 0, -50), (2, 47, -1))
    B(m, "tip", p["hatd"], (7.0, 44.4, -3.8), (4, 3.4, 6.4), (0, 0, -80), (7, 45, -1))
    # little white sleeves with green stripes, the arms held out from the coat
    arms(m, 10.5, 21, 4.4, 4.6, p["sleeve"], p["sleeve"], "black_concrete", 9, hand_h=1.5, spread=2.0)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, p["cuff"], (sd * 11.5 - 2.4, 14.0, -2.4), (4.8, 1.0, 4.8))
        B(m, a, p["cuff"], (sd * 11.5 - 2.4, 16.4, -2.4), (4.8, 0.6, 4.8))
        B(m, a, p["coat"], (sd * 10.5 - 3.2, 17.5, -3.2), (6.4, 4.2, 6.4))                     # the coat shoulder over it
    # the crook staff: down at an angle to the ground, hook at the top, wrapped grip
    S0 = (11.5, 11, 4)
    chain(m, "staff", p["staff"], S0, [(10.6, (2.2, 2.2), (160, 0, -10))])
    top = chain(m, "staff", p["staff"], S0, [(7, (2.2, 2.2), (14, 0, 8)), (3, (2.0, 2.0), (60, 0, 8)), (3, (1.8, 1.8), (120, 0, 8)), (2, (1.6, 1.6), (165, 0, 8))])
    B(m, "staff", p["wrap"], (S0[0] - 1.3, S0[1] + 4.2, S0[2] - 0.2), (2.6, 0.8, 2.6), (14, 0, 8), S0)
    for k in range(3):
        C(m, "staff", p["wrap"] if k != 1 else p["stripe"], (11.5 + 0.35 * k * -0.2, 11 - k * 1.2 - 0.6, 4 + k * 0.5), (2.0, 0.9, 2.0), (25, 0, -12))
    tipat = (top[0], top[1] - 1.8, top[2])
    if p["tip"] == "fire":
        C(m, "staff", "shroomlight", tipat, (2.4, 2.4, 2.4), light=True); C(m, "staff", "orange_concrete", (tipat[0], tipat[1] + 1.8, tipat[2]), (1.4, 1.6, 1.4), light=True)
    elif p["tip"] == "ice":
        C(m, "staff", "packed_ice", tipat, (2.2, 3.4, 2.2), (0, 45, 20)); C(m, "staff", "light_blue_concrete", tipat, (1.0, 1.0, 1.0), light=True)
    elif p["tip"] == "moss":
        C(m, "staff", "moss_block", tipat, (3.0, 1.6, 3.0)); C(m, "staff", "red_mushroom_block", (tipat[0], tipat[1] + 1.4, tipat[2]), (2.6, 1.2, 2.6))
        for x, z in ((-11, 6), (10, -8), (-8, -9)):                                                # mushrooms on the brim
            C(m, "hat", "mushroom_stem", (x, 36.8, z), (1.0, 1.6, 1.0)); C(m, "hat", "red_mushroom_block", (x, 38.0, z), (2.6, 1.0, 2.6))
    else:
        C(m, "staff", "lantern", tipat, (2.6, 3.0, 2.6), light=True)
    m.bend = 0
    cast = attack(1.4, 0.85, {
        "armL": {"rot": K((0, Z), (0.6, (-150, 0, -10)), (0.85, (-60, 0, 10)), (1.0, (-55, 0, 10)), (1.4, Z))},
        "staff": {"rot": K((0, Z), (0.6, (-30, 0, 0)), (0.85, (20, 0, 0)), (1.4, Z))},
        "armR": {"rot": K((0, Z), (0.6, (-40, 0, 30)), (0.85, (-70, 0, -10)), (1.4, Z))},
        "body": {"rot": K((0, Z), (0.6, (-8, 10, 0)), (0.85, (10, -8, 0)), (1.4, Z))},
        "hat": {"rot": K((0, Z), (0.6, (-6, 0, 0)), (0.85, (8, 0, 0)), (1.0, (-4, 0, 0)), (1.4, Z))},
        "tip": {"rot": K((0, Z), (0.65, (0, 0, 14)), (0.95, (0, 0, -16)), (1.2, (0, 0, 6)), (1.4, Z))},
        "root": {"pos": K((0, Z), (0.6, (0, 1.5, 0)), (0.85, Z), (1.4, Z))}})
    blink = attack(1.0, 0.5, {
        "root": {"scl": K((0, (1, 1, 1)), (0.35, (1.15, 0.7, 1.15)), (0.5, (0.05, 1.6, 0.05)), (0.65, (1.1, 0.85, 1.1)), (1.0, (1, 1, 1)))},
        "hat": {"pos": K((0, Z), (0.45, (0, 4, 0)), (0.65, Z), (1.0, Z))}})
    standard_anims(m, heavy=0.7, weapon="L", extra={
        "idle": idle_biped(4.0, 16, extra={"tip": {"rot": wave(2, 6, 4.0)}, "hat": {"rot": wave(2, 2, 4.0, 0.3)},
                                            "collar": {"scl": breathe(4.0, 0.02)}}),
        "cast": cast, "blink": blink})
    m.anims["walk"]["bones"]["tip"] = {"rot": K((0, (0, 0, 6)), (0.55, (0, 0, -6)), (1.1, (0, 0, 6)))}
    m.attacks = {"blink": "blink", "slam": "slam", "orbs": "cast", "fire_ring": "roar", "frost": "cast", "poison": "cast", "spikes": "stomp"}
    m.attacks = {k: v for k, v in m.attacks.items() if k in ("blink", "slam", "orbs", "fire_ring") or k in HOLLOW_EXTRA.get(id, ())}
    m.melee = "swipe"
    return m


HOLLOW_EXTRA = {"cinder_hollow": (), "rime_hollow": ("frost",), "bramble_hollow": ("poison", "spikes")}


@studio("hollow_mage")
def hollow_mage():
    """The Hollow Mage: a round little wizard in a huge mustard hat with a green band, the tall crown slumped over
    to one side. Under the brim there is only dark and two glowing yellow eyes. A blue coat with a tall collar,
    crossed straps and a buckle, white sleeves with green cuffs, striped green trousers and a crook staff."""
    return hollow("hollow_mage", HOLLOW["hollow_mage"])


@new_big("cinder_hollow", "<gradient:#3e0d0d:#ff8a3d><bold>The Cinder Hollow</bold></gradient>", "The Hat Is Still Smoking", "WITCH", "fire", "RED",
         extra=["fire_ring", "meteor"], items=["BLAZE_ROD 16", "MAGMA_CREAM 16", "DIAMOND 3"], top=["TOTEM_OF_UNDYING 1"],
         rec=recipe("FLAME", "ENTITY_BLAZE_AMBIENT", "ENTITY_BLAZE_DEATH", 0.8, "cast", "die_back", "magma_block"))
def cinder_hollow():
    """The Cinder Hollow, the hollow mage who tried fire magic once too often: a charred nether-brick hat with a
    glowing orange band, a red coat, orange eyes in the dark and a staff that ends in a burning ember."""
    return hollow("cinder_hollow", HOLLOW["cinder_hollow"])


@new_big("rime_hollow", "<gradient:#0d3a4a:#b3f0ff><bold>The Rime Hollow</bold></gradient>", "Snow on the Brim, Frost in the Eyes", "WITCH", "frost", "BLUE",
         extra=["frost", "levitate"], items=["PACKED_ICE 32", "BLUE_ICE 8", "DIAMOND 3"], top=["TOTEM_OF_UNDYING 1"],
         rec=recipe("SNOWFLAKE", "BLOCK_POWDER_SNOW_STEP", "BLOCK_GLASS_BREAK", 1.2, "cast", "die_back", "snow_block"))
def rime_hollow():
    """The Rime Hollow, the hollow mage from the far north: a hat of packed snow with an ice band, a cyan coat,
    pale blue eyes in the dark and a birch crook tipped with a shard of ice."""
    return hollow("rime_hollow", HOLLOW["rime_hollow"])


@new_big("bramble_hollow", "<gradient:#1b3a12:#c5e1a5><bold>The Bramble Hollow</bold></gradient>", "Mushrooms Grow on the Hat", "WITCH", "nature", "GREEN",
         extra=["poison", "spikes"], items=["MOSS_BLOCK 32", "RED_MUSHROOM 16", "DIAMOND 3"], top=["TOTEM_OF_UNDYING 1"],
         rec=recipe("SPORE_BLOSSOM_AIR", "BLOCK_MOSS_BREAK", "BLOCK_MOSS_BREAK", 0.8, "cast", "die_back", "moss_block"))
def bramble_hollow():
    """The Bramble Hollow, the hollow mage who fell asleep in the woods for a hundred years: a spruce hat with
    red toadstools growing on the brim, a mossy green coat, lime eyes in the dark and a crook staff gone to moss."""
    return hollow("bramble_hollow", HOLLOW["bramble_hollow"])


# ------------------------------------------------------------------------------------------------ new from refs2
@new_mini("bogwart", "<gradient:#2e5d1a:#c5e17a><bold>Bogwart</bold></gradient>", "Sits in the Reeds and Waits", entity="DROWNED", theme="nature", bar="GREEN",
          extra=["leap", "poison"], rec=recipe("FALLING_WATER", "ENTITY_FROG_AMBIENT", "ENTITY_FROG_DEATH", 0.6, "roar", "die_back", "mud"))
def bogwart():
    """Bogwart, a slouching frog-man of the swamp: a wide flat head with two big eye bumps on top under heavy
    lids, a pale tan throat and lip, a hunched mottled green body, long arms with webbed three-finger hands
    and frog legs bent under him."""
    m = Model("bogwart", "biped", 1.0)
    G, GD, GL, TAN = "lime_terracotta", "green_terracotta", "lime_wool", "smooth_sandstone"
    humanoid(m, hip=11, legx=3.4, neck=24, shoulder=23, armx=7.5, jaw=(0, 25, 3))
    legs(m, 3.4, 11, 4.2, 4.6, G, foot=GD, foot_h=1.4, toe=2.6)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        for k in (-1, 0, 1):
            C(m, leg, GD, (sd * 3.4 + k * 1.4, 0.6, 4.4 + abs(k) * -0.4), (1.0, 1.2, 2.2), (0, k * 18, 0))      # webbed toes
    B(m, "hips", G, (-5, 9, -3), (10, 4, 6))
    B(m, "body", G, (-6, 12, -3.5), (12, 12, 7))
    B(m, "body", G, (-6.5, 18, -4.5), (13, 6, 6.5), (16, 0, 0), (0, 18, 0))                      # hunched back
    B(m, "body", TAN, (-4, 13, 3.4), (8, 9, 0.4))
    speckle(m, "body", (-6, 12, -3.6), (12, 12, 0), "back", [GD, GL], n=8, seed=4, depth=0.1, cell=1.2)
    speckle(m, "body", (-6.1, 12, -3), (0, 12, 6), "left", [GD], n=4, seed=5, depth=0.1, cell=1.2)
    speckle(m, "body", (6.1, 12, -3), (0, 12, 6), "right", [GD], n=4, seed=6, depth=0.1, cell=1.2)
    # the wide head, pushed forward on the hunch
    B(m, "head", G, (-6.5, 25, -3), (13, 5, 10))
    B(m, "jaw", TAN, (-6, 22, -1.5), (12, 3, 8.5))
    B(m, "jaw", G, (-6.6, 22.6, -2), (13.2, 2.4, 6))
    B(m, "head", TAN, (-6.2, 24.6, 6.4), (12.4, 1.0, 0.8))                                       # the lip line
    B(m, "head", "black_terracotta", (-5.2, 24.8, 7.0), (10.4, 0.4, 0.2))
    for sd in (1, -1):
        B(m, "head", G, (sd * 3.6 - 2.6, 29.5, 0), (5.2, 3.2, 5.6))                               # eye bump
        B(m, "head", "black_concrete", (sd * 3.6 - 1.4, 30.0, 5.55), (2.8, 1.6, 0.2))
        B(m, "head", "yellow_terracotta", (sd * 3.6 - (0.2 if sd > 0 else 1.2), 30.2, 5.6), (1.0, 0.8, 0.2), light=True)
        B(m, "head", GD, (sd * 3.6 - 2.8, 31.4, 0.4), (5.6, 1.4, 5.8))                            # heavy lid
        B(m, "head", GD, (sd * 1.4 - 0.3, 28.0, 6.95), (0.6, 0.6, 0.1))                            # nostril
    speckle(m, "head", (-6.5, 30, -3), (13, 0, 10), "top", [GD, GL], n=6, seed=9, depth=0.1, cell=1.2)
    arms(m, 7.8, 23, 3.0, 3.2, G, G, GD, 14, hand_h=2.0, spread=0.6)
    for sd, a in ((1, "armL"), (-1, "armR")):
        for k in (-1, 0, 1):
            C(m, a, GD, (sd * 8.4 + k * 1.0, 8.2, 1.0 + k * 0.6), (0.8, 2.4, 0.8), (20, 0, k * 22 * sd))
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(3.0, 16, breath=0.05, extra={"jaw": {"rot": K((0, Z), (1.4, Z), (1.6, (8, 0, 0)), (1.8, Z), (3.0, Z))}})})
    hop = attack(1.1, 0.6, {
        "root": {"pos": K((0, Z), (0.3, (0, -2, 0)), (0.6, (0, 9, 8)), (0.85, (0, 0, 12)), (1.1, Z))},
        "legL": {"rot": K((0, Z), (0.3, (-40, 0, 0)), (0.6, (30, 0, 0)), (0.85, (-20, 0, 0)), (1.1, Z))},
        "legR": {"rot": K((0, Z), (0.3, (-40, 0, 0)), (0.6, (30, 0, 0)), (0.85, (-20, 0, 0)), (1.1, Z))},
        "armL": {"rot": K((0, Z), (0.3, (30, 0, 0)), (0.6, (-120, 0, -20)), (0.85, (-40, 0, 0)), (1.1, Z))},
        "armR": {"rot": K((0, Z), (0.3, (30, 0, 0)), (0.6, (-120, 0, 20)), (0.85, (-40, 0, 0)), (1.1, Z))}})
    croak = attack(1.0, 0.5, {
        "jaw": {"rot": K((0, Z), (0.3, (30, 0, 0)), (0.7, (30, 0, 0)), (1.0, Z)), "scl": K((0, (1, 1, 1)), (0.5, (1.25, 1.4, 1.2)), (0.8, (1, 1, 1)), (1.0, (1, 1, 1)))},
        "head": {"rot": K((0, Z), (0.3, (-20, 0, 0)), (0.7, (-20, 0, 0)), (1.0, Z))}})
    m.anims.update({"hop": hop, "croak": croak})
    m.attacks = {"leap": "hop", "poison": "croak"}
    m.melee = "swipe"
    return m


@new_big("brewgut", "<gradient:#33691e:#c0ca33><bold>Brewgut</bold></gradient>", "Last Orders at the Bent Tankard", "VINDICATOR", "nature", "GREEN",
         extra=["slam", "charge", "roar"], items=["HONEY_BOTTLE 16", "IRON_INGOT 32", "DIAMOND 3"], top=["TOTEM_OF_UNDYING 1"],
         rec=recipe("CLOUD", "ENTITY_VINDICATOR_CELEBRATE", "ENTITY_RAVAGER_DEATH", 0.6, "roar", "die_back", "barrel"))
def brewgut():
    """Brewgut, the orc who runs the tavern: a big square green head with an underbite and two yellow tusks,
    small dark eyes under a heavy brow and a notched ear, a rolled-up white shirt under a brown vest, a belt,
    a ragged shirt hem, maroon trousers, huge green forearms and a barrel tankard in one fist."""
    m = Model("brewgut", "biped", 1.6)
    G, GD, GL = "lime_terracotta", "green_terracotta", "moss_block"
    SH, SHD, VEST = "white_wool", "light_gray_wool", "brown_terracotta"
    humanoid(m, hip=13, legx=4.2, neck=30, shoulder=29.5, armx=10, jaw=(0, 33.5, 3))
    m.bone("mug", "armR", (-11, 9, 2))
    m.hold = {"mug": 0}
    legs(m, 4.2, 13, 5.4, 5.6, "red_terracotta", foot="dark_oak_planks", foot_h=2.0, toe=1.4, shin="red_terracotta")
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, "brown_terracotta", (sd * 4.2 - 2.9, 2, -2.9), (5.8, 1.4, 5.8))
    B(m, "hips", "red_terracotta", (-7, 11, -3.5), (14, 4, 7))
    # the shirt, vest and belt
    B(m, "body", SH, (-8, 14, -4.5), (16, 16, 9))
    B(m, "body", SH, (-8.5, 15, -4), (17, 3, 9.5))
    for k, x in enumerate(range(-8, 8, 2)):                                                          # ragged hem
        B(m, "body", SH if k % 2 else SHD, (x, 11.0 - (k % 3) * 0.8, -4.6), (2, 3.2 + (k % 3) * 0.8, 9.2))
    B(m, "body", VEST, (-8.3, 18.5, -4.8), (5.2, 11.6, 9.6)); B(m, "body", VEST, (3.1, 18.5, -4.8), (5.2, 11.6, 9.6))
    B(m, "body", VEST, (-8.3, 18.5, -4.8), (16.6, 11.6, 2))
    B(m, "body", "dark_oak_planks", (-8.6, 15.4, -4.9), (17.2, 1.8, 10))
    B(m, "body", "gold_block", (-1.2, 15.2, 5.0), (2.4, 2.2, 0.3))
    B(m, "body", "black_terracotta", (-0.5, 15.8, 5.2), (1.0, 1.0, 0.2))
    for x in (-6.5, -4.6): B(m, "body", "dark_oak_planks", (x, 24, 4.75), (0.8, 0.8, 0.1))           # vest patches / stitching
    B(m, "body", "spruce_planks", (4.0, 20.5, 4.75), (2.6, 2.6, 0.1))
    # the head: big, square, underbite, tusks
    B(m, "head", G, (-6.5, 30, -5), (13, 12, 11))
    B(m, "head", GD, (-6.6, 38.6, 5.9), (13.2, 1.6, 0.4))                                          # brow
    B(m, "head", G, (-4, 33.6, 6), (8, 3.6, 2))                                                      # snout
    B(m, "head", GD, (-2.4, 34.8, 7.9), (1.4, 1.2, 0.2)); B(m, "head", GD, (1.0, 34.8, 7.9), (1.4, 1.2, 0.2))
    for sd in (1, -1):
        B(m, "head", "black_concrete", (sd * 3.6 - 1.0, 36.6, 6.0), (2.0, 1.8, 0.2))
        B(m, "head", "white_concrete", (sd * 3.6 - (0.0 if sd > 0 else 1.0), 37.4, 6.05), (1.0, 1.0, 0.2))
        C(m, "head", G, (sd * 8.2, 37, 0), (3.4, 4.2, 1.4), (0, -20 * sd, -30 * sd))                  # ears
    B(m, "head", GD, (7.6, 38.4, -0.8), (1.6, 1.0, 1.6))                                             # the notch
    B(m, "jaw", G, (-6.0, 30.5, -1), (12, 3.6, 8.6))
    B(m, "jaw", GD, (-6.1, 30.3, 7.4), (12.2, 0.6, 0.4))
    teeth(m, "jaw", -4.5, 4.5, 34.1, 7.6, "bone_block", n=4, h=0.8, w=1.0, d=0.4)
    for sd in (1, -1):
        chain(m, "jaw", "bone_block", (sd * 4.4, 33.8, 7.0), [(2.2, (1.8, 1.4), (10, 0, 14 * sd)), (1.4, (1.2, 1.0), (-10, 0, 26 * sd), "smooth_sandstone")])
    speckle(m, "head", (-6.5, 30, -5.05), (13, 12, 0), "back", [GD, GL], n=6, seed=21, depth=0.1, cell=1.4)
    speckle(m, "head", (-6.5, 42.0, -5), (13, 0, 11), "top", [GD, GL], n=5, seed=22, depth=0.1, cell=1.4)
    # rolled sleeves, huge green forearms
    arms(m, 10.5, 29.5, 5.2, 5.6, SH, G, G, 17, hand_h=4.4, spread=1.0)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, SHD, (sd * 10.5 - 2.9, 20.4, -3.1), (5.8, 1.4, 6.2))
        speckle(m, a, (sd * 10.5 - 2.6, 6, 2.85), (5.2, 13, 0), "front", [GD, GL], n=4, seed=30 + sd, depth=0.1, cell=1.2)
    C(m, "mug", "barrel", (-11.5, 6.2, 3.6), (5, 6, 5))
    C(m, "mug", "white_wool", (-11.5, 9.6, 3.6), (5.2, 1.2, 5.2))
    C(m, "mug", "spruce_planks", (-14.4, 6.2, 3.6), (1.2, 4, 1.2))
    m.bend = -14
    swig = attack(1.6, 1.0, {
        "armR": {"rot": K((0, Z), (0.5, (-150, 0, 0)), (0.9, (-160, 0, 10)), (1.1, (-60, 0, 0)), (1.6, Z))},
        "head": {"rot": K((0, Z), (0.5, (-30, 0, 0)), (0.9, (-34, 0, 0)), (1.1, (14, 0, 0)), (1.6, Z))},
        "jaw": {"rot": K((0, Z), (0.9, Z), (1.05, (28, 0, 0)), (1.3, (28, 0, 0)), (1.6, Z))},
        "body": {"rot": K((0, Z), (0.5, (-10, 0, 0)), (1.0, (14, 0, 0)), (1.6, Z))}})
    standard_anims(m, heavy=1.2, extra={"swig": swig, "idle": idle_biped(4.0, 18, extra={"jaw": {"rot": wave(0, 3, 4.0)}})})
    m.attacks = {"slam": "slam", "charge": "lunge", "roar": "swig"}
    m.melee = "swipe"
    return m


@new_mini("old_pip", "<gradient:#b71c1c:#a5d6a7><bold>Old Pip</bold></gradient>", "Gnome Elder of the Garden", entity="ZOMBIE", theme="nature", bar="GREEN",
          extra=["volley", "blink"], rec=recipe("HAPPY_VILLAGER", "ENTITY_VILLAGER_AMBIENT", "ENTITY_VILLAGER_DEATH", 1.6, "roar", "die_back", "moss_block"))
def old_pip():
    """Old Pip, the gnome elder: a tall floppy red hat over bushy white brows, little green eyes, a huge
    nose that hangs over a long white beard, rosy cheeks, a teal tunic, a brown belt with an emerald buckle
    and little brown boots."""
    m = Model("old_pip", "biped", 1.0)
    SKIN, HAT, HATD, TUN, TUND = "white_terracotta", "red_concrete", "red_wool", "cyan_concrete", "cyan_wool"
    humanoid(m, hip=6, legx=2.4, neck=17, shoulder=16, armx=6.5)
    m.bone("hat", "head", (0, 28, 0))
    m.bone("beard", "head", (0, 19, 4))
    legs(m, 2.4, 6, 3.4, 3.6, "brown_concrete", foot="brown_terracotta", foot_h=1.8, toe=1.4)
    B(m, "hips", "brown_concrete", (-4, 5, -2.6), (8, 2, 5.2))
    B(m, "body", TUN, (-5, 6.4, -3), (10, 11, 6))
    B(m, "body", TUND, (-5.4, 6.0, -3.4), (10.8, 2.0, 6.8))
    B(m, "body", "brown_terracotta", (-5.2, 8.5, -3.2), (10.4, 1.4, 6.4))
    B(m, "body", "emerald_block", (-1.2, 8.0, 3.2), (2.4, 2.4, 0.4), light=True)
    B(m, "body", "black_concrete", (-0.5, 8.7, 3.55), (1.0, 1.0, 0.1))
    # head, beard, nose
    B(m, "head", SKIN, (-4.5, 17, -4), (9, 11, 8))
    B(m, "head", "white_wool", (-4.7, 22.8, 3.9), (3.8, 1.2, 0.6)); B(m, "head", "white_wool", (0.9, 22.8, 3.9), (3.8, 1.2, 0.6))   # brows
    for sd in (1, -1):
        B(m, "head", "lime_concrete", (sd * 2.4 - 0.8, 21.4, 3.95), (1.6, 1.4, 0.2), light=True)
        B(m, "head", "black_concrete", (sd * 2.4 - (0.0 if sd > 0 else 0.8), 21.4, 4.0), (0.8, 0.8, 0.2))
        B(m, "head", "pink_concrete", (sd * 3.4 - 0.8, 19.6, 3.95), (1.6, 1.0, 0.1))
        B(m, "head", "white_wool", (sd * 4.5 - 0.6, 17, -2.5), (1.2, 6, 6.5))                     # side whiskers
    B(m, "beard", "white_wool", (-4.5, 13.5, 3.6), (9, 5.5, 1.6))
    B(m, "beard", "white_wool", (-3.5, 11.0, 3.6), (7, 2.6, 1.4))
    B(m, "beard", "white_wool", (-2.0, 9.5, 3.4), (4, 1.6, 1.2))
    B(m, "beard", "light_gray_wool", (-1.0, 9.0, 3.4), (2, 0.8, 1.1))
    B(m, "beard", "white_wool", (-4.5, 17, 3.6), (9, 2.0, 1.0))
    B(m, "head", "terracotta", (-1.6, 16.0, 4.0), (3.2, 5.6, 2.4))                                  # the nose
    B(m, "head", "brown_terracotta", (-1.4, 15.4, 4.2), (2.8, 0.8, 2.0))
    # floppy pointed hat
    B(m, "hat", HAT, (-5, 26.5, -4.5), (10, 3, 9))
    B(m, "hat", HATD, (-5.2, 26.3, -4.7), (10.4, 1.0, 9.4))
    chain(m, "hat", HAT, (0, 29.5, 0), [(4, (8, 7.6), (-6, 0, 0)), (3.6, (6, 5.6), (-16, 0, 0)), (3, (4.2, 4), (-34, 0, 0), HATD),
                                       (2.6, (2.8, 2.6), (-70, 0, 0)), (2.0, (1.8, 1.6), (-110, 0, 0), HATD)])
    arms(m, 6.6, 16, 3.0, 3.2, TUN, TUN, SKIN, 9, hand_h=2.4)
    for sd, a in ((1, "armL"), (-1, "armR")):
        B(m, a, TUND, (sd * 6.6 - 1.7, 9.4, -1.8), (3.4, 1.0, 3.6))
    standard_anims(m, heavy=0.6, extra={"idle": idle_biped(3.0, 18, extra={"hat": {"rot": wave(2, 5, 3.0)}, "beard": {"rot": wave(0, 3, 1.5)}})})
    m.attacks = {"volley": "cast", "blink": "stomp"}
    m.melee = "swipe"
    return m


@new_mini("sproutbeak", "<gradient:#2e7d32:#a1887f><bold>Sproutbeak</bold></gradient>", "A Hedge With Legs and a Backpack", entity="ZOMBIE", theme="nature", bar="GREEN",
          extra=["charge"], rec=recipe("COMPOSTER", "BLOCK_AZALEA_LEAVES_BREAK", "BLOCK_AZALEA_LEAVES_BREAK", 1.4, "roar", "die_back", "moss_block"))
def sproutbeak():
    """Sproutbeak, a little round hedge that walks: a cube of leafy green on two long thin legs with big flat
    feet, a beady eye on each side, a tiny beak, stubby leaf wings, a leather backpack strapped on with a
    buckle at the front."""
    m = Model("sproutbeak", "biped", 1.0)
    G, GD, GL = "green_concrete", "green_terracotta", "lime_concrete"
    humanoid(m, hip=10, legx=3, neck=14, shoulder=17, armx=7.5)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        B(m, leg, "smooth_sandstone", (sd * 3 - 0.7, 1, -0.7), (1.4, 9.4, 1.4))
        B(m, leg, "smooth_sandstone", (sd * 3 - 2.0, 0, -1.2), (4.0, 1.0, 5.6))
        B(m, leg, "sandstone", (sd * 3 - 2.2, 0, 3.6), (4.4, 1.0, 1.0))
    B(m, "body", G, (-7, 10, -6), (14, 13, 13))
    B(m, "body", GD, (-7.2, 10, -6.2), (14.4, 1.6, 13.4))
    B(m, "head", G, (-6.6, 22.6, -5.6), (13.2, 2.4, 12.2))
    speckle(m, "body", (-7, 11, 7.0), (14, 12, 0), "front", [GD, GL], n=9, seed=41, depth=0.12, cell=1.6)
    speckle(m, "head", (-6.6, 25.0, -5.6), (13.2, 0, 12.2), "top", [GD, GL], n=6, seed=42, depth=0.12, cell=1.6)
    for sd in (1, -1):
        speckle(m, "body", (sd * 7.05, 11, -5), (0, 11, 11), "left" if sd > 0 else "right", [GD, GL], n=5, seed=43 + sd, depth=0.12, cell=1.6)
        B(m, "head", "black_concrete", (sd * 7.0 - 0.1, 19.5, 2.5), (0.2, 1.6, 1.6))
        B(m, "head", "white_concrete", (sd * 7.05 - 0.1, 20.4, 3.3), (0.2, 0.6, 0.6))
    # backpack and straps
    B(m, "body", "spruce_planks", (-6, 11, -10), (12, 11, 4))
    B(m, "body", "dark_oak_planks", (-6.3, 19, -10.3), (12.6, 3.2, 4.6))
    B(m, "body", "dark_oak_planks", (-1.2, 16.4, -10.4), (2.4, 2.6, 0.4))
    for sd in (1, -1):
        B(m, "body", "dark_oak_planks", (sd * 4 - 0.8, 10.5, -6.2), (1.6, 12.6, 13.4))
    B(m, "body", "dark_oak_planks", (-7.1, 13, 6.9), (14.2, 1.6, 0.3))
    B(m, "body", "light_gray_concrete", (-1.4, 12.2, 7.15), (2.8, 3.2, 0.3))
    B(m, "body", "black_concrete", (-0.5, 13.0, 7.4), (1.0, 1.6, 0.1))
    arms(m, 7.5, 17, 2.2, 3.6, G, G, GL, 6, hand_h=2.0)
    m.no_knees = True
    standard_anims(m, heavy=0.5, extra={"idle": idle_biped(2.0, 10, breath=0.04)})
    m.attacks = {"charge": "lunge"}
    m.melee = "swipe"
    return m
