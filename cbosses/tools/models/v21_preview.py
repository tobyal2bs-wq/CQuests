"""v21: design previews. These bosses are NOT in the plugin: the module is only loaded when PREVIEW=1 is set,
to render pictures for the owner to pick from. An approved one moves into v20_mob with a real slot."""
from build import Model
from v14_studio import new_mini
from v14_kit import standard_anims, idle_biped, humanoid, wave
from v20_mob import bx, part, paint, lit, litbox, moves, joints, emboss, unfight, calm


def preview(id, name, title):
    def deco(fn):
        def run():
            m = fn()
            m.flat = m.sculpted = True
            m.post = lambda m: (calm(m), joints(m), emboss(m), unfight(m))
            return m
        run.__name__, run.__doc__ = fn.__name__, fn.__doc__
        return new_mini(id, "<bold>%s</bold>" % name, title)(run)
    return deco


@preview("preview_coco", "Coco", "King of the Palm Beach")
def preview_coco():
    """Coco, a palm tree that pulled up its roots: a ringed trunk for a body, big coconut fists, a crown of
    drooping fronds, dark sunglasses, a flower lei and flip-flops."""
    m = Model("preview_coco", "biped", 1.7)
    humanoid(m, hip=10, legx=3.2, neck=27, shoulder=25, armx=8.6)
    m.bone("fronds", "head", (0, 35, 0))
    BARK, BARK_D, BARK_L, NUT, NUT_D, LEAF, LEAF_D = "stripped_oak_log", "spruce_planks", "stripped_birch_log", "brown_terracotta", "black_terracotta", "lime_terracotta", "green_terracotta"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.2
        part(m, leg, (x, 6.2, 0), (4.0, 7.6, 4.2), BARK, dark=BARK_D, band=0.25)
        part(m, leg, (x, 0.5, 1.2), (4.8, 1.0, 7.0), "light_blue_concrete")                       # flip-flops
        bx(m, leg, (x, 1.4, 2.2), (3.4, 0.8, 0.8), "yellow_concrete")
        part(m, leg, (x, 1.6, 0.4), (3.6, 1.6, 4.4), BARK_L)
    # the trunk: four ringed segments, each a little narrower, with a darker ring between them
    for i, (y, w) in enumerate(((12.0, 12.0), (16.2, 11.2), (20.4, 10.4), (24.4, 9.6))):
        part(m, "hips" if i == 0 else "body", (0, y, 0), (w, 4.2, w - 3.0), BARK)
        bx(m, "hips" if i == 0 else "body", (0, y - 2.0, 0), (w + 0.6, 0.9, w - 2.4), BARK_D)
    # the lei: flowers round the chest
    for i, x in enumerate((-4.4, -2.2, 0, 2.2, 4.4)):
        bx(m, "body", (x, 23.6 - (2 - abs(i - 2)) * 0.8, 3.9), (1.8, 1.8, 0.8), ("pink_concrete", "yellow_concrete", "magenta_concrete")[i % 3])
    # arms: bark, with coconut fists
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 8.6
        part(m, arm, (x, 21.6, 0), (3.4, 7.2, 3.6), BARK, dark=BARK_D, band=0.2)
        part(m, arm, (x, 16.0, 0.2), (3.0, 4.4, 3.2), BARK_L)
        part(m, arm, (x, 11.6, 0.4), (5.4, 5.0, 5.4), NUT, dark=NUT_D, band=0.3)
        for dx, dy in ((-1.0, 0.6), (1.0, 0.6), (0, -0.8)):
            bx(m, arm, (x + dx, 11.6 + dy, 3.2), (0.8, 0.8, 0.4), NUT_D)                          # the three coconut eyes
    # the head: a round coconut face, sunglasses, a grin
    part(m, "head", (0, 31.0, 0.4), (9.6, 7.6, 8.6), NUT, dark=NUT_D, band=0.16)
    for sd in (1, -1):
        bx(m, "head", (sd * 2.5, 32.0, 4.8), (3.6, 2.4, 0.5), "black_concrete")
        bx(m, "head", (sd * 3.2, 32.6, 5.1), (0.9, 0.7, 0.4), "white_concrete")
        bx(m, "head", (sd * 4.9, 32.4, 2.4), (0.5, 0.8, 5.0), "black_concrete")
    bx(m, "head", (0, 32.4, 4.8), (1.6, 0.7, 0.5), "black_concrete")
    bx(m, "head", (0, 29.2, 4.8), (5.0, 1.2, 0.5), "white_concrete")
    for x in (-1.3, 0, 1.3):
        bx(m, "head", (x, 29.2, 5.0), (0.3, 1.2, 0.4), "black_concrete")
    # fronds: six long leaves that droop outward, each in two pieces
    part(m, "fronds", (0, 35.4, 0.2), (4.6, 1.8, 4.6), LEAF_D)
    for k, (dx, dz) in enumerate(((1, 0), (-1, 0), (0, -1), (0.7, -0.7), (-0.7, -0.7), (0.7, 0.5), (-0.7, 0.5))):
        rot = (28 * dz, 0, -28 * dx)
        bx(m, "fronds", (dx * 5.0, 35.6, 0.2 + dz * 5.0), (2.6 + abs(dx) * 6.0, 0.9, 2.6 + abs(dz) * 6.0), LEAF if k % 2 else LEAF_D, rot=rot, origin=(dx * 1.5, 36.0, 0.2 + dz * 1.5))
        if dz > 0: continue                              # nothing droops over the face
        bx(m, "fronds", (dx * 9.6, 33.0, 0.2 + dz * 9.6), (2.0 + abs(dx) * 3.6, 0.8, 2.0 + abs(dz) * 3.6), LEAF_D if k % 2 else LEAF, rot=(55 * dz, 0, -55 * dx), origin=(dx * 8.0, 34.4, 0.2 + dz * 8.0))
    standard_anims(m, heavy=1.1, extra={"idle": idle_biped(4.0, 14, breath=0.03, extra={"fronds": {"rot": wave(2, 5, 4.0)}})})
    moves(m, dict(length=1.2, swing=22, arm=22, bob=1.0, sway=6))
    m.attacks = {"slam": "slam", "leap": "lunge"}
    m.melee = "swipe"
    return m


@preview("preview_patch", "Old Patch", "He Was Left in the Field Too Long")
def preview_patch():
    """Old Patch, a scarecrow: a burlap sack head with button eyes and a stitched grin, a floppy straw hat, a
    checked shirt and patched dungarees stuffed with straw, a pitchfork and a crow sitting on his shoulder."""
    m = Model("preview_patch", "biped", 1.8)
    humanoid(m, hip=13, legx=3.0, neck=30, shoulder=28.4, armx=7.6)
    m.bone("hat", "head", (0, 37.6, 0)); m.bone("crow", "body", (7.6, 30, 0)); m.bone("fork", "armR", (-7.8, 12, 2))
    m.hold = {"fork": 0}
    SACK, SACK_D, STRAW, DENIM, DENIM_D, SHIRT, SHIRT_D = "smooth_sandstone", "packed_mud", "hay_block", "blue_terracotta", "black_terracotta", "red_terracotta", "brown_terracotta"
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.0
        part(m, leg, (x, 8.0, 0), (4.0, 10.0, 4.2), DENIM, dark=DENIM_D, band=0.12)
        bx(m, leg, (x, 2.4, 0), (3.0, 1.6, 3.2), STRAW)                                         # straw at the ankle
        part(m, leg, (x, 0.9, 0.8), (4.2, 1.8, 5.6), "brown_terracotta")
    bx(m, "legL", (3.0, 8.4, 2.3), (2.4, 2.4, 0.5), "yellow_terracotta")                         # a knee patch
    part(m, "hips", (0, 14.6, 0), (10.6, 4.0, 6.8), DENIM, dark=DENIM_D, band=0.3)
    # checked shirt: red body with darker bands, the dungaree bib and straps over it
    part(m, "body", (0, 22.6, 0), (10.2, 12.4, 6.4), SHIRT)
    for y in (19.0, 22.6, 26.2):
        bx(m, "body", (0, y, 0), (10.5, 1.0, 6.7), SHIRT_D)
    for x in (-3.4, 0, 3.4):
        bx(m, "body", (x, 22.6, 0), (1.0, 12.5, 6.7), SHIRT_D)
    part(m, "body", (0, 20.4, 3.3), (6.4, 6.4, 0.8), DENIM)
    for sd in (1, -1):
        bx(m, "body", (sd * 2.6, 26.0, 3.3), (1.2, 5.2, 0.8), DENIM)
        bx(m, "body", (sd * 2.6, 23.4, 3.8), (0.9, 0.9, 0.4), "gold_block")
    bx(m, "body", (0, 29.4, 0), (6.0, 1.6, 5.0), STRAW)                                          # the straw neck
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 7.6
        part(m, arm, (x, 23.8, 0), (3.4, 9.6, 3.6), SHIRT, dark=SHIRT_D, band=0.12)
        bx(m, arm, (x, 18.2, 0), (2.6, 2.0, 2.8), STRAW)
        part(m, arm, (x, 16.0, 0.4), (3.0, 2.8, 3.0), SACK)
    # the sack head: tied at the neck, button eyes, a stitched grin, a carrot-less patch for a nose
    part(m, "head", (0, 34.0, 0.2), (8.4, 7.2, 7.6), SACK, dark=SACK_D, band=0.14)
    bx(m, "head", (2.2, 35.2, 4.1), (1.8, 1.8, 0.5), "black_concrete"); bx(m, "head", (2.2, 35.2, 4.3), (0.6, 0.6, 0.4), "white_concrete")
    bx(m, "head", (-2.2, 35.0, 4.1), (1.4, 1.4, 0.5), "black_concrete")
    bx(m, "head", (0, 33.8, 4.1), (1.4, 1.4, 0.5), "red_terracotta")
    bx(m, "head", (0, 32.0, 4.1), (5.6, 0.5, 0.5), "black_concrete")
    for x in (-2.2, -0.7, 0.7, 2.2):
        bx(m, "head", (x, 32.0, 4.2), (0.4, 1.4, 0.4), "black_concrete")
    # the hat: a wide floppy brim, a dented crown, a band, straw poking out underneath
    part(m, "hat", (0, 37.9, 0.2), (13.0, 0.9, 12.0), STRAW)
    part(m, "hat", (0, 39.8, 0.2), (7.4, 3.2, 6.8), STRAW, rot=(-5, 0, 6), origin=(0, 38.4, 0.2))
    bx(m, "hat", (0, 38.9, 0.2), (7.7, 0.9, 7.1), "red_terracotta", rot=(-5, 0, 6), origin=(0, 38.4, 0.2))
    for sd in (1, -1):
        bx(m, "head", (sd * 4.5, 36.4, 0.2), (0.8, 2.0, 4.0), STRAW)
    # the crow
    part(m, "crow", (7.6, 30.8, 0), (2.6, 2.6, 4.0), "black_concrete")
    part(m, "crow", (7.6, 32.6, 1.6), (2.2, 2.0, 2.2), "black_concrete")
    bx(m, "crow", (7.6, 32.4, 3.1), (0.8, 0.7, 1.2), "orange_concrete")
    for sd in (1, -1):
        bx(m, "crow", (7.6 + sd * 1.15, 32.9, 2.2), (0.3, 0.5, 0.5), "white_concrete")
    bx(m, "crow", (7.6, 30.6, -2.6), (1.6, 0.8, 1.8), "black_concrete", rot=(20, 0, 0), origin=(7.6, 30.6, -2.0))
    # the pitchfork
    bx(m, "fork", (-7.8, 18.0, 2), (1.1, 30.0, 1.1), "stripped_spruce_log")
    bx(m, "fork", (-7.8, 33.4, 2), (5.0, 1.0, 1.0), "iron_block")
    for t in (-2.0, 0, 2.0):
        bx(m, "fork", (-7.8 + t, 36.0, 2), (0.8, 4.4, 0.8), "iron_block")
    m.bend = -45
    standard_anims(m, heavy=0.9, extra={"idle": idle_biped(4.0, 20, breath=0.02, extra={
        "hat": {"rot": wave(2, 5, 4.0)}, "crow": {"rot": wave(1, 18, 2.0)}})})
    moves(m, dict(length=1.1, swing=30, arm=26, bob=0.6, sway=7))
    m.attacks = {"minions": "roar", "leap": "lunge"}
    m.melee = "swipe"
    return m


@preview("preview_crumb", "Sir Crumb", "Knight of the Biscuit Tin")
def preview_crumb():
    """Sir Crumb, a gingerbread knight: a flat biscuit body with white icing trim and gumdrop buttons, a big
    round head with icing eyes and a smile, a candy cane sword and a peppermint shield."""
    m = Model("preview_crumb", "biped", 1.6)
    humanoid(m, hip=9, legx=3.4, neck=24, shoulder=22.6, armx=8.4)
    m.bone("sword", "armR", (-8.6, 10.4, 2)); m.bone("shield", "armL", (9.4, 14, 2.6))
    m.hold = {"sword": 30}
    GB, GB_D, ICE = "brown_terracotta", "black_terracotta", "white_concrete"
    def trim(bone, x, y, z, w):                      # a zig-zag of icing: three raised dabs
        for i in (-1, 0, 1):
            bx(m, bone, (x + i * w / 3, y + (0.4 if i == 0 else -0.4), z), (w / 3 - 0.3, 0.9, 0.5), ICE)
    for sd, leg in ((1, "legL"), (-1, "legR")):
        x = sd * 3.4
        part(m, leg, (x, 5.0, 0), (5.0, 10.0, 4.4), GB, dark=GB_D, band=0.12)
        trim(leg, x, 2.6, 2.3, 4.6)
    part(m, "hips", (0, 10.6, 0), (12.0, 3.4, 4.6), GB)
    part(m, "body", (0, 17.6, 0), (12.6, 11.0, 4.8), GB, dark=GB_D, band=0.1)
    for y, c in ((20.4, "red_concrete"), (17.6, "lime_concrete"), (14.8, "light_blue_concrete")):
        part(m, "body", (0, y, 2.7), (1.8, 1.8, 0.9), c)                                          # gumdrop buttons
    bx(m, "body", (0, 12.4, 2.5), (11.0, 0.9, 0.5), ICE)
    for sd, arm in ((1, "armL"), (-1, "armR")):
        x = sd * 8.4
        part(m, arm, (x, 17.4, 0), (4.4, 10.4, 4.2), GB, dark=GB_D, band=0.12)
        trim(arm, x, 14.0, 2.2, 4.0)
    part(m, "head", (0, 28.6, 0), (11.6, 9.2, 5.2), GB, dark=GB_D, band=0.1)
    for sd in (1, -1):
        bx(m, "head", (sd * 2.6, 30.0, 2.7), (2.0, 2.0, 0.5), ICE)
        bx(m, "head", (sd * 2.6, 29.8, 2.9), (0.9, 0.9, 0.4), "black_concrete")
        bx(m, "head", (sd * 4.0, 27.6, 2.7), (1.4, 1.0, 0.5), "pink_concrete")                    # cheeks
        bx(m, "head", (sd * 2.4, 27.0, 2.7), (1.0, 0.8, 0.5), ICE)
    bx(m, "head", (0, 26.4, 2.7), (4.0, 0.8, 0.5), ICE)
    trim("head", 0, 32.4, 2.7, 9.0)
    # a tin helmet: a jelly mould with a cherry
    part(m, "head", (0, 34.0, 0), (8.0, 1.6, 4.6), "iron_block")
    part(m, "head", (0, 35.4, 0), (5.0, 1.4, 3.6), "iron_block")
    part(m, "head", (0, 36.8, 0), (1.8, 1.6, 1.8), "red_concrete")
    # candy cane sword: red and white bands, a hooked top
    for i in range(8):
        bx(m, "sword", (-8.6, 11.4 + i * 2.2, 2), (1.6, 2.2, 1.6), "red_concrete" if i % 2 else ICE)
    bx(m, "sword", (-7.2, 29.0, 2), (4.4, 1.6, 1.6), "red_concrete")
    bx(m, "sword", (-5.6, 27.6, 2), (1.6, 2.0, 1.6), ICE)
    # peppermint shield: a white disc with a red swirl
    part(m, "shield", (10.9, 14.0, 2.6), (1.0, 9.0, 9.0), ICE)
    for dy, dz in ((2.4, 0), (-2.4, 0), (0, 2.4), (0, -2.4)):
        bx(m, "shield", (11.5, 14.0 + dy, 2.6 + dz), (0.5, 2.4 if dy else 1.6, 2.4 if dz else 1.6), "red_concrete")
    bx(m, "shield", (11.5, 14.0, 2.6), (0.6, 2.0, 2.0), "red_concrete")
    standard_anims(m, heavy=0.8, extra={"idle": idle_biped(3.6, 14, breath=0.02)})
    moves(m, dict(length=0.9, swing=26, arm=20, bob=0.8, sway=7))
    m.attacks = {"slam": "slam", "leap": "lunge"}
    m.melee = "swipe"
    return m
