"""Openings and deaths for the v6-v8 bosses (the user's reference pictures, the pumpkins and the minis).
Same language as v2_recipes: ticks, blocks, vh = fraction of the boss's height."""
from v2_recipes import S, fx, gone

SPAWN, DEATH = {}, {}

# ----------------------------------------------------------------------------------------- big bosses
SPAWN["old_wizard"] = [S("shrink", 0, s=0), fx(0, "ENCHANT", 120, "BLOCK_ENCHANTMENT_TABLE_USE", 0.6, y=0.2, spread=2, ring=3),
    S("pose", 4, 6, order="up", stagger=36, only="!hat"), fx(24, "WITCH", 60, "ENTITY_EVOKER_PREPARE_SUMMON", 0.8, y=0.6),
    S("move", 40, vh=[0, 1.6, 0], only="hat"), S("pose", 42, 14, only="hat"), S("spin", 42, 14, deg=360, only="hat"),
    S("light", 58, on=True, only="lit"), fx(60, "END_ROD", 40, "BLOCK_AMETHYST_BLOCK_CHIME", 1.2, y=0.9), S("anim", 64, 30, name="cast")]
DEATH["old_wizard"] = [S("flash", 0, 4, block="purple_concrete"), fx(0, sound="ENTITY_EVOKER_DEATH", pitch=0.7), S("anim", 0, 30, name="die_kneel"),
    S("fling", 16, power=2, up=5, tilt=200, only="hat"), S("drop", 20, 12, tilt=40, only="book"), fx(24, "ENCHANT", 120, "BLOCK_ENCHANTMENT_TABLE_USE", 0.5, y=0.4, spread=2),
    S("swap", 34, block="purple_stained_glass", order="up", stagger=26), fx(60, "WITCH", 60, "ENTITY_ILLUSIONER_MIRROR_MOVE", 0.6, y=0.5), gone(66, 14)]

SPAWN["hollow_mage"] = [S("shrink", 0, s=0), fx(0, "SQUID_INK", 60, "ENTITY_PHANTOM_AMBIENT", 0.5, y=0.3, spread=1.5),
    S("pose", 2, 4, only="hat"), S("move", 2, vh=[0, 0.7, 0], only="hat"), S("move", 6, 30, vh=[0, -0.7, 0], only="hat"),
    S("pose", 30, 6, order="up", stagger=20, only="!hat"), S("light", 52, on=True, only="lit"), fx(52, "WAX_OFF", 20, "BLOCK_RESPAWN_ANCHOR_CHARGE", 1.4, y=0.8),
    S("anim", 56, 26, name="cast")]
DEATH["hollow_mage"] = [S("flash", 0, 3, block="black_concrete"), fx(0, sound="ENTITY_PHANTOM_DEATH", pitch=0.6), S("light", 2, on=False, only="lit"),
    S("anim", 0, 24, name="die_back"), S("scale", 20, 24, s=[1.0, 0.05, 1.0], only="!hat"), fx(24, "SQUID_INK", 120, "BLOCK_SCULK_CATALYST_BLOOM", 0.5, y=0.2, spread=1.5),
    S("drop", 34, 16, tilt=30, only="hat"), fx(50, "POOF", 30, "BLOCK_BAMBOO_BREAK", 0.8, y=0), gone(64, 12)]

SPAWN["horned_brute"] = [S("move", 0, v=[0, 18, -6]), fx(0, "CLOUD", 40, "ENTITY_RAVAGER_ROAR", 0.6, y=1.0, spread=2),
    S("move", 6, 14, v=[0, -18, 6]), fx(20, "EXPLOSION", 3, "ENTITY_GENERIC_EXPLODE", 0.6, y=0, spread=3),
    fx(21, "BLOCK", 160, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0, spread=3.5, block="COARSE_DIRT"), S("shake", 22, 12),
    S("anim", 34, 30, name="roar"), fx(40, "CRIT", 40, "ENTITY_HOGLIN_ANGRY", 0.6, y=0.9)]
DEATH["horned_brute"] = [S("flash", 0, 4), fx(0, sound="ENTITY_RAVAGER_DEATH", pitch=0.6), S("anim", 0, 34, name="die_front"),
    S("fling", 14, power=3, up=4, tilt=300, only="spear"), S("fling", 26, power=2, up=4, tilt=220, only="horns"),
    fx(30, "BLOCK", 140, "ENTITY_GENERIC_BIG_FALL", 0.6, y=0, spread=3, block="COARSE_DIRT"), S("swap", 44, block="coarse_dirt", order="down", stagger=24), gone(74, 14)]

def climb_out(soil="PODZOL", sound="ENTITY_ZOMBIE_AMBIENT", pitch=0.5):
    """Climbs out of the ground: buried, he hauls
    himself up in three heaves, with dirt bursting up at every heave."""
    return [S("move", 0, vh=[0, -1.0, 0]), fx(0, "BLOCK", 120, "BLOCK_ROOTED_DIRT_BREAK", 0.5, y=0, spread=2.5, block=soil, ring=3),
            fx(8, "BLOCK", 80, "BLOCK_GRAVEL_BREAK", 0.6, y=0.2, spread=1.5, block=soil),
            S("move", 14, 18, vh=[0, 0.35, 0]), fx(16, "BLOCK", 90, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0.2, spread=2, block=soil),
            S("move", 36, 18, vh=[0, 0.35, 0]), fx(38, "BLOCK", 90, "BLOCK_ROOTED_DIRT_BREAK", 0.6, y=0.2, spread=2, block=soil),
            S("move", 58, 18, vh=[0, 0.3, 0]), fx(60, "BLOCK", 140, sound, pitch, y=0.1, spread=3, block=soil, ring=4),
            S("pose", 76, 6), S("anim", 82, 30, name="roar")]


SPAWN["rotting_giant"] = climb_out("PODZOL", "ENTITY_ZOMBIE_BREAK_WOODEN_DOOR", 0.5) + [fx(90, "SNEEZE", 60, "ENTITY_ZOMBIE_VILLAGER_CONVERTED", 0.4, y=0.9, spread=2)]
DEATH["rotting_giant"] = [S("flash", 0, 4, block="lime_concrete"), fx(0, sound="ENTITY_ZOMBIE_DEATH", pitch=0.4), S("anim", 0, 40, name="die_front"),
    S("drop", 22, 14, tilt=60, rand=2, only="armL"), S("drop", 26, 14, tilt=60, rand=2, only="armR"), fx(36, "BLOCK", 200, "ENTITY_GENERIC_BIG_FALL", 0.4, y=0, spread=4, block="MUD"),
    S("swap", 42, block="mud", order="up", stagger=30), S("scale", 70, 24, s=[1.3, 0.05, 1.3]), fx(74, "SNEEZE", 80, "BLOCK_MUD_BREAK", 0.5, y=0.1, spread=3), gone(94, 12)]

SPAWN["dusk_scorpion"] = [S("move", 0, vh=[0, -1.1, 0]), fx(0, "BLOCK", 120, "BLOCK_SAND_BREAK", 0.5, y=0, spread=3, block="SAND", ring=4),
    S("move", 4, 40, vh=[0, 1.1, 0]), S("light", 44, on=True, only="lit"), fx(44, "DUST", 30, "ENTITY_SPIDER_AMBIENT", 0.4, y=0.4, color="#ff3020"),
    S("anim", 50, 24, name="fang"), fx(60, "SWEEP_ATTACK", 4, "ENTITY_PLAYER_ATTACK_SWEEP", 0.6, y=0.4)]
DEATH["dusk_scorpion"] = [S("flash", 0, 3, block="red_concrete"), fx(0, sound="ENTITY_SPIDER_DEATH", pitch=0.4), S("anim", 0, 30, name="die_curl"),
    S("light", 10, on=False, only="lit"), S("shatter", 34, pieces=3, power=2, up=2, only="abdomen"),
    fx(36, "BLOCK", 120, "BLOCK_DEEPSLATE_BREAK", 0.6, y=0.2, spread=2.5, block="BLACKSTONE"), gone(60, 14)]

SPAWN["gourd_king"] = [S("shrink", 0, s=0), fx(0, "FLAME", 40, "BLOCK_PUMPKIN_CARVE", 0.6, y=0, spread=2, ring=3),
    S("pose", 4, 6, order="up", stagger=40, only="!head"), fx(20, "BLOCK", 80, "BLOCK_GRASS_BREAK", 0.6, y=0.2, spread=2, block="VINE"),
    S("move", 44, v=[0, 8, 0], only="head"), S("pose", 46, 16, only="head"), S("spin", 46, 16, deg=720, only="head"),
    S("light", 62, on=True, only="lit"), fx(62, "FLAME", 60, "ENTITY_BLAZE_SHOOT", 0.6, y=0.9, spread=1.2), S("anim", 66, 30, name="roar"),
    fx(72, sound="ENTITY_WITCH_CELEBRATE", pitch=0.5)]
DEATH["gourd_king"] = [S("flash", 0, 4, block="orange_concrete"), fx(0, sound="ENTITY_WITCH_DEATH", pitch=0.5), S("anim", 0, 30, name="die_kneel"),
    S("light", 20, on=False, only="lit"), S("fling", 26, power=2, up=6, tilt=400, only="head"),
    S("swap", 30, block="moss_block", order="up", stagger=24, only="!head"), fx(40, "BLOCK", 160, "BLOCK_PUMPKIN_CARVE", 0.6, y=0.5, spread=2, block="PUMPKIN"),
    S("shatter", 56, pieces=4, power=2, up=3, only="head"), fx(58, "FLAME", 60, "ENTITY_GENERIC_EXPLODE", 0.7, y=0.8), gone(76, 14)]


def generic(theme_particle, sound_in, sound_die, block, anim_in="roar", die="die_front"):
    """A plain rise-from-the-ground opening and fall-and-crumble death for a mini boss."""
    sp = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "BLOCK", 60, "BLOCK_ROOTED_DIRT_BREAK", 0.7, y=0, spread=1.5, block=block.upper(), ring=2),
          S("move", 4, 30, vh=[0, 1.05, 0]), fx(20, theme_particle, 30, sound_in, 1.1, y=0.6, spread=1), S("anim", 36, 20, name=anim_in)]
    de = [S("flash", 0, 3), fx(0, sound=sound_die, pitch=1.1), S("anim", 0, 24, name=die), fx(16, theme_particle, 40, None, 1.0, y=0.4, spread=1.2),
          S("swap", 24, block=block, order="up", stagger=16), gone(44, 10)]
    return sp, de


DECOR_SPAWN = [S("shrink", 0, s=0), S("pose", 2, 10), fx(2, "POOF", 10, "BLOCK_PUMPKIN_CARVE", 1.0, y=0.3)]
DECOR_DEATH = [S("flash", 0, 2), gone(2, 6)]
for d in ("decor_pumpkin_tall", "decor_pumpkin_flat", "decor_pumpkin_cube"):
    SPAWN[d], DEATH[d] = DECOR_SPAWN, DECOR_DEATH

SPAWN["clockwork_colossus"] = [S("shrink", 0, s=0), fx(0, "SMOKE", 60, "BLOCK_PISTON_EXTEND", 0.6, y=0.2, spread=2),
    S("pose", 4, 6, order="up", stagger=44), fx(16, "ELECTRIC_SPARK", 40, "BLOCK_COPPER_BULB_TURN_ON", 0.8, y=0.4, spread=1.5),
    fx(30, sound="BLOCK_CHAIN_PLACE", pitch=0.6), S("spin", 50, 20, deg=720, only="key"), fx(52, sound="BLOCK_IRON_TRAPDOOR_OPEN", pitch=0.5),
    S("light", 70, on=True, only="lit"), fx(72, "CLOUD", 40, "ENTITY_IRON_GOLEM_REPAIR", 0.5, y=1.0, spread=0.8), S("anim", 76, 28, name="stomp")]
DEATH["clockwork_colossus"] = [S("flash", 0, 3, block="copper_block"), fx(0, sound="ENTITY_IRON_GOLEM_DEATH", pitch=0.5), S("spin", 0, 30, deg=-540, only="key"),
    S("anim", 4, 34, name="die_kneel"), fx(10, "ELECTRIC_SPARK", 80, "BLOCK_COPPER_BULB_TURN_OFF", 0.6, y=0.6, spread=1.5),
    S("light", 30, on=False, only="lit"), S("fling", 36, power=3, up=6, tilt=300, only="key"), S("swap", 40, block="oxidized_copper", order="up", stagger=24),
    S("shatter", 66, pieces=3, power=2, up=2), fx(66, "LARGE_SMOKE", 80, "ENTITY_GENERIC_EXPLODE", 0.6, y=0.5, spread=2), gone(84, 12)]

SPAWN["mossback"] = [S("move", 0, vh=[0, -1.05, 0]), fx(0, "SPLASH", 160, "ENTITY_TURTLE_AMBIENT_LAND", 0.4, y=0, spread=4, ring=5),
    S("move", 6, 80, vh=[0, 1.05, 0]), fx(40, "SPORE_BLOSSOM_AIR", 80, "BLOCK_AZALEA_LEAVES_PLACE", 0.6, y=1.0, spread=3),
    S("anim", 90, 30, name="howl"), fx(96, "FALLING_SPORE_BLOSSOM", 60, "ENTITY_TURTLE_AMBIENT_LAND", 0.3, y=1.2, spread=3)]
DEATH["mossback"] = [S("flash", 0, 4, block="moss_block"), fx(0, sound="ENTITY_TURTLE_DEATH", pitch=0.3), S("anim", 0, 40, name="die_collapse"),
    S("swap", 30, block="moss_block", order="down", stagger=40), fx(40, "SPORE_BLOSSOM_AIR", 120, "BLOCK_MOSS_PLACE", 0.5, y=0.6, spread=4),
    S("scale", 80, 30, s=[1.1, 0.3, 1.1]), gone(110, 14)]


def _swap(steps, table):
    out = []
    for st in steps:
        st = dict(st)
        o = st.get("only")
        if o:
            neg = o.startswith("!")
            key = o[1:] if neg else o
            if key in table: st["only"] = ("!" if neg else "") + table[key]
        out.append(st)
    return out


import v4_recipes as _v4
# the v5 rebuilds of these bosses have different bone names than the recipes were written for
for _id, _t in (("the_listener", {"heart": "lit"}), ("withered_tyrant", {"ring2": "tail", "ring3": "core"})):
    SPAWN[_id], DEATH[_id] = _swap(_v4.SPAWN[_id], _t), _swap(_v4.DEATH[_id], _t)
