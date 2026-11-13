#!/usr/bin/env python3
"""Gives every boss its own entrance and its own death, built from block steps and loose prop blocks.

python3 tools/entrances.py models.json bosses.yml

Each boss gets one (kind, variant) pair nobody else has, picked from the kinds that suit its theme.
The model's own opening_<id> and death_<id> clips are kept and played inside the new steps.
Hand-made entrances and deaths (KEEP_SPAWN, KEEP_DEATH) are left alone. Safe to run twice.
"""
import json, sys, zlib
import yaml

KEEP_SPAWN = {"clucksworth", "rotting_giant", "ember_queen"}
KEEP_DEATH = {"keywarden", "clockwork_colossus", "hollow_mage", "mayor_grumble", "sunscorch", "gourd_king",
              "headless_horseman", "hexmother", "thunderback", "gorehorn", "the_unmaker"}
ORDERS = ["up", "out", "random", "down", "in"]
# the bosses people meet first get the entrance and death that says most about them
PICK = {"slagheart": ("meteor", "burn"), "frost_yeti": ("spikes", "freeze"), "old_wizard": ("unfold", "ascend"), "mossback": ("sprout", "petrify"),
        "gravelord": ("grave", "crumble"), "tide_tyrant": ("rainin", "melt"), "mossy_turtle": ("grow", "sink")}

# theme: (prop block, lit, second prop block, landing sound, entrances that fit, deaths that fit)
THEMES = {
    "fire": ("magma_block", True, "blackstone", "ENTITY_GENERIC_EXPLODE", "meteor skyfall core swarm", "burn explode melt ash"),
    "earth": ("cobblestone", False, "stone", "BLOCK_STONE_BREAK", "rubble tiers spikes tip", "crumble petrify shatter topple"),
    "nature": ("moss_block", False, "oak_leaves", "BLOCK_GRASS_BREAK", "sprout tiers rainin grow spikes", "wilt scatter sink crumble deflate"),
    "toxic": ("slime_block", False, "lime_concrete", "BLOCK_SLIME_BLOCK_PLACE", "grow core swarm unfold", "melt pop deflate implode"),
    "water": ("prismarine", False, "ice", "ENTITY_GENERIC_SPLASH", "rainin vortex grow skyfall", "melt sink ascend scatter"),
    "gold": ("gold_block", False, "yellow_concrete", "BLOCK_AMETHYST_BLOCK_CHIME", "tiers rainin core vortex", "shatter melt scatter petrify"),
    "blood": ("nether_wart_block", False, "red_concrete", "ENTITY_RAVAGER_STEP", "core swarm grave meteor", "melt implode pop topple"),
    "witch": ("amethyst_block", True, "purple_concrete", "ENTITY_ILLUSIONER_CAST_SPELL", "vortex unfold core turn", "implode ascend whirl ash"),
    "frost": ("packed_ice", False, "snow_block", "BLOCK_GLASS_BREAK", "rainin spikes tiers skyfall", "freeze shatter crumble topple"),
    "storm": ("light_blue_concrete", True, "white_concrete", "ENTITY_LIGHTNING_BOLT_THUNDER", "skyfall vortex meteor", "explode ascend whirl"),
    "soul": ("soul_sand", False, "bone_block", "PARTICLE_SOUL_ESCAPE", "grave rubble unfold", "ascend ash whirl"),
    "void": ("obsidian", False, "purple_concrete", "ENTITY_ENDERMAN_TELEPORT", "core vortex unfold", "implode whirl ash"),
    "bone": ("bone_block", False, "white_concrete", "ENTITY_SKELETON_STEP", "grave rubble tiers", "crumble scatter topple"),
    "candy": ("pink_concrete", False, "white_concrete", "BLOCK_HONEY_BLOCK_PLACE", "rainin grow swarm", "pop melt scatter"),
    "pumpkin": ("pumpkin", False, "orange_concrete", "BLOCK_WOOD_BREAK", "sprout tip swarm", "pop deflate scatter"),
    "sand": ("sandstone", False, "yellow_concrete", "BLOCK_SAND_BREAK", "rubble vortex", "crumble ash"),
    "iron": ("iron_block", False, "gray_concrete", "BLOCK_ANVIL_LAND", "tiers skyfall", "topple shatter"),
    "sculk": ("sculk", False, "black_concrete", "BLOCK_SCULK_SHRIEKER_SHRIEK", "spikes core", "implode ash"),
    "wither": ("coal_block", False, "black_concrete", "ENTITY_WITHER_AMBIENT", "meteor grave", "ash explode"),
    "holiday": ("snow_block", False, "red_concrete", "BLOCK_SNOW_BREAK", "rainin tiers", "pop scatter"),
    "feather": ("white_wool", False, "yellow_concrete", "ENTITY_CHICKEN_STEP", "skyfall swarm", "scatter pop"),
    "wind": ("white_concrete", False, "light_blue_concrete", "ENTITY_PHANTOM_FLAP", "vortex skyfall", "whirl ascend"),
}
ALL_IN = "meteor rubble core tiers grave sprout vortex skyfall grow swarm rainin unfold tip spikes turn".split()
ALL_OUT = "crumble explode shatter implode melt petrify ascend ash burn freeze scatter whirl topple deflate pop wilt sink".split()


def fx(at, y=0.5, spread=0.5, **k):
    return {"op": "fx", "at": at, "y": y, "spread": spread, **k}


def prop(at, mode, block, count, dur, **k):
    return {"op": "prop", "at": at, "dur": dur, "mode": mode, "block": block, "count": count, **k}


def entrance(kind, v, T, P):
    """Steps before the opening clip, and the tick the body is whole again."""
    order, alt = ORDERS[v % 5], v // 5 % 2
    b1, lit, b2 = T[0], T[1], T[2]
    part, sound, land = P["particle"], P["sound"], T[3]
    hide = {"op": "shrink", "at": 0, "s": 0}
    if kind == "meteor":      # a burning rock falls in; the boss grows out of the crater
        return [hide, {"op": "toward", "at": 0, "k": 1, "y": 0.05},
                prop(0, "fall", b1, 1, 14, size=1.5 + 0.2 * alt, r=0.05, lean=2, lit=lit, linger=2),
                prop(3 + alt * 3, "fall", b2, 4 + v % 3, 12, size=0.45, r=1.1, stagger=8, lit=lit),
                fx(14, 0.1, 1.2, particle="EXPLOSION", count=3, sound=land, pitch=0.7),
                {"op": "pose", "at": 15, "dur": 7, "order": order, "stagger": 10}], 32
    if kind == "rubble":      # a heap of its own blocks rolls together and stacks up
        return [{"op": "shrink", "at": 0, "s": 0.9}, {"op": "drop", "at": 0, "tilt": 120, "rand": 1.2 + 0.3 * alt},
                prop(2, "wave", b1, 5 + v % 3, 12, size=0.5, r=1.2, linger=14),
                fx(2, 0.1, 1, particle="BLOCK", block=b1.upper(), count=30, sound=land, pitch=0.8),
                {"op": "pose", "at": 12, "dur": 6, "order": order, "stagger": 18}], 36
    if kind == "core":        # everything is packed into one small core that swells and opens
        return [{"op": "shrink", "at": 0, "s": 0.25}, {"op": "toward", "at": 0, "k": 0.92, "y": 0.5},
                prop(0, "orbit", b1 if alt else b2, 5 + v % 2, 18, size=0.35, r=1.3, y=0.5, turns=1.5, lit=lit),
                {"op": "shake", "at": 6, "dur": 10},
                fx(17, 0.5, 0.8, particle=part, count=40, sound=land, pitch=1.2),
                {"op": "pose", "at": 18, "dur": 6, "order": order, "stagger": 8}], 32
    if kind == "tiers":       # built in three courses, bottom to top, each one stamped down
        steps = [hide, {"op": "move", "at": 0, "vh": [0, 0.5, 0]}]
        for j in range(3):
            steps += [{"op": "pose", "at": 3 + j * 8, "dur": 4, "order": "up", "part": [j / 3, (j + 1) / 3]},
                      fx(7 + j * 8, 0.15 + j * 0.3, 0.6, particle="BLOCK", block=b1.upper(), count=14, sound=land, pitch=0.8 + j * 0.2 + alt * 0.1)]
        steps += [prop(1, "rise" if alt else "rain", b2, 4 + v % 3, 10, size=0.4, r=1.0, stagger=12, tall=1.6)]
        return steps, 29
    if kind == "grave":       # lies flat on its back under grave markers, then is pulled upright
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "tilt", "at": 0, "axis": "x", "deg": -90, "pivot": [0, 0, -P["hz"]]},
                prop(0, "rise", b2 if alt else b1, 3 + v % 3, 8, size=0.55, r=0.9, tall=1.8, linger=22),
                fx(4, 0.1, 1, particle="BLOCK", block="DIRT", count=40, sound="BLOCK_ROOTED_DIRT_BREAK", pitch=0.7),
                {"op": "pose", "at": 12, "dur": 12, "order": order, "stagger": 5}], 31
    if kind == "sprout":      # pressed flat into the soil, it grows up through a ring of shoots
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "scale", "at": 0, "s": [1.15, 0.03, 1.15]},
                prop(0, "rise", b2, 6 + v % 3, 10, size=0.3, r=0.9, tall=2.4 + alt, stagger=10, linger=18),
                fx(6, 0.2, 0.9, particle=part, count=30, sound=land, pitch=1.1),
                {"op": "pose", "at": 8, "dur": 10, "order": order, "stagger": 12}], 32
    if kind == "vortex":      # its blocks whirl in from a wide ring and lock together
        return [{"op": "shrink", "at": 0, "s": 0.6}, {"op": "burst", "at": 0, "power": 3.5 + alt, "up": 1.5, "tilt": 90},
                {"op": "spin", "at": 0, "deg": 150},
                prop(0, "orbit", b1, 6 + v % 3, 22, size=0.4, r=1.6, y=0.3 + 0.4 * alt, turns=2, lit=lit),
                fx(0, 0.6, 1.5, particle=part, count=40, sound=sound, pitch=0.8),
                {"op": "pose", "at": 6, "dur": 10, "order": order, "stagger": 14}], 32
    if kind == "skyfall":     # drops out of the sky, lands hard and throws rubble
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "move", "at": 0, "vh": [0, 3.2 + 0.4 * alt, 0]},
                {"op": "pose", "at": 3, "dur": 7},
                fx(10, 0.05, 1.3, particle="EXPLOSION", count=2, sound=land, pitch=0.6, lightning=bool(lit and alt)),
                prop(10, "wave", b1, 6 + v % 3, 10, size=0.45, r=1.4, linger=16, lit=lit),
                {"op": "scale", "at": 10, "dur": 2, "s": [1.18, 0.8, 1.18]},
                {"op": "pose", "at": 13, "dur": 4, "order": order, "stagger": 4}], 22
    if kind == "grow":        # swells up from a seed, overshoots and settles
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "scale", "at": 0, "s": [0.06, 0.06, 0.06]},
                prop(0, "rain" if alt else "wave", b2, 5 + v % 3, 12, size=0.35, r=1.0, stagger=10),
                {"op": "scale", "at": 2, "dur": 14, "s": [19, 19, 19]},
                fx(16, 0.5, 0.8, particle=part, count=30, sound=land, pitch=1.3),
                {"op": "pose", "at": 17, "dur": 5, "order": order, "stagger": 5}], 28
    if kind == "swarm":       # scattered far and wide, the pieces fly home one after another
        return [{"op": "shrink", "at": 0, "s": 0.5}, {"op": "burst", "at": 0, "power": 5 + alt, "up": 2.5, "tilt": 160, "rand": 1.5},
                fx(0, 0.5, 2, particle=part, count=50, sound=sound, pitch=1.2),
                prop(4, "fall", b1, 3 + v % 3, 12, size=0.4, r=1.3, stagger=10, lean=0.6, lit=lit),
                {"op": "pose", "at": 4, "dur": 8, "order": order, "stagger": 20}], 34
    if kind == "rainin":      # the blocks rain down from above and stack in place
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "move", "at": 0, "vh": [0, 3, 0], "rand": 1.0 + alt},
                prop(0, "rain", b2, 7 + v % 3, 10, size=0.3, r=1.3, stagger=22),
                {"op": "pose", "at": 2, "dur": 6, "order": order, "stagger": 22},
                fx(26, 0.1, 1, particle=part, count=30, sound=land, pitch=1.0)], 32
    if kind == "unfold":      # opens out of a thin sheet, like a page turning
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "scale", "at": 0, "s": [0.03, 1, 1] if alt else [1, 1, 0.03]},
                {"op": "spin", "at": 0, "deg": 90},
                prop(0, "orbit", b2, 4 + v % 3, 16, size=0.3, r=1.1, y=0.8, turns=1, lit=lit),
                fx(2, 0.5, 0.6, particle=part, count=30, sound=sound, pitch=1.4),
                {"op": "pose", "at": 4, "dur": 12, "order": order, "stagger": 6}], 24
    if kind == "tip":         # lies on its side like a felled log and rocks upright
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "tilt", "at": 0, "axis": "z", "deg": 90 if alt else -90, "pivot": [-P["hx"] if alt else P["hx"], 0, 0]},
                prop(0, "wave", b1, 4 + v % 3, 10, size=0.4, r=1.2, linger=20),
                {"op": "pose", "at": 6, "dur": 11, "order": order, "stagger": 3},
                fx(17, 0.05, 1, particle="BLOCK", block=b1.upper(), count=30, sound=land, pitch=0.7)], 22
    if kind == "spikes":      # spikes punch out of the floor in a ring and the boss rises between them
        return [hide, {"op": "scale", "at": 0, "s": [1, 0.05, 1]},
                prop(0, "rise", b1, 7 + v % 3, 6, size=0.4, r=1.0, tall=3 + alt, stagger=10, linger=20, lit=lit),
                fx(0, 0.1, 1.2, particle="BLOCK", block=b1.upper(), count=40, sound=land, pitch=0.6),
                {"op": "pose", "at": 12, "dur": 9, "order": order, "stagger": 8}], 31
    if kind == "turn":        # stands with its back turned, small, then swings round at full size
        return [{"op": "shrink", "at": 0, "s": 1}, {"op": "spin", "at": 0, "deg": 179}, {"op": "scale", "at": 0, "s": [0.7, 0.7, 0.7]},
                prop(2, "fall" if alt else "rain", b2, 4 + v % 3, 10, size=0.35, r=1.2, stagger=8, lit=lit),
                fx(8, 0.6, 0.8, particle=part, count=30, sound=sound, pitch=0.9),
                {"op": "pose", "at": 10, "dur": 10, "order": order, "stagger": 4}], 26
    raise KeyError(kind)


def death(kind, v, T, P, start):
    """Steps after the body stops moving at tick `start`; returns them and the tick everything is gone."""
    order, alt = ORDERS[v % 5], v // 5 % 2
    b1, lit, b2 = T[0], T[1], T[2]
    part, sound = P["particle"], P["dsound"]
    s = start
    end_fx = lambda at, **k: fx(at, 0.4, 0.8, particle=k.pop("particle", part), count=30, sound=sound, pitch=k.pop("pitch", 0.8), **k)
    if kind == "crumble":     # falls apart from the top into a heap
        return [{"op": "drop", "at": s, "dur": 8, "tilt": 140, "rand": 0.9 + 0.3 * alt, "order": order, "stagger": 16},
                end_fx(s + 4), prop(s + 6, "wave", b1, 5 + v % 3, 10, size=0.4, r=1.2, linger=14)], s + 38
    if kind == "explode":     # blows apart: every block is thrown and bounces
        return [{"op": "scale", "at": s, "dur": 4, "s": [1.15, 1.15, 1.15]},
                {"op": "fling", "at": s + 5, "dur": 14, "power": 5 + alt, "up": 3, "tilt": 200, "order": order, "stagger": 3},
                fx(s + 5, 0.5, 1, particle="EXPLOSION", count=4, sound="ENTITY_GENERIC_EXPLODE", pitch=0.8),
                prop(s + 5, "wave", b1, 7 + v % 3, 12, size=0.4, r=1.8, lit=lit), end_fx(s + 8)], s + 40
    if kind == "shatter":     # cracks into shards that skitter across the floor
        return [{"op": "shake", "at": s, "dur": 6}, {"op": "shatter", "at": s + 6, "pieces": 2 + alt, "power": 3, "up": 2.5, "order": order, "stagger": 8},
                end_fx(s + 6, particle="BLOCK", block=b1.upper())], s + 44
    if kind == "implode":     # sucked into its own middle and gone with a snap
        return [prop(s, "orbit", b2, 6 + v % 3, 14, size=0.35, r=1.5, y=0.5, turns=2, lit=lit),
                {"op": "toward", "at": s, "dur": 9, "k": 0.95, "y": 0.5, "order": order, "stagger": 8},
                end_fx(s + 17, pitch=1.6 - 0.2 * alt)], s + 20
    if kind == "melt":        # sags and runs out into a puddle
        return [{"op": "scale", "at": s, "dur": 18, "s": [1.5 + 0.2 * alt, 0.05, 1.5 + 0.2 * alt]},
                {"op": "swap", "at": s + 6, "block": b1, "order": order, "stagger": 12},
                prop(s + 8, "wave", b1, 5 + v % 3, 12, size=0.3, r=1.1, linger=10, lit=lit), end_fx(s + 10)], s + 30
    if kind == "petrify":     # turns to stone from the feet up, then the statue breaks
        return [{"op": "swap", "at": s, "block": "stone" if alt else "cobblestone", "order": order, "stagger": 14},
                fx(s, 0.5, 0.6, particle="BLOCK", block="STONE", count=20, sound="BLOCK_STONE_PLACE", pitch=0.6),
                {"op": "drop", "at": s + 20, "dur": 7, "tilt": 100, "rand": 0.8, "order": "down", "stagger": 10}, end_fx(s + 22)], s + 44
    if kind == "ascend":      # the blocks let go one by one and drift up out of sight
        return [{"op": "move", "at": s, "dur": 22, "vh": [0, 2.6 + 0.4 * alt, 0], "rand": 0.8, "order": order, "stagger": 16},
                {"op": "light", "at": s, "on": True}, prop(s, "orbit", b2, 4 + v % 3, 24, size=0.3, r=0.9, y=1.2, turns=1.5, lit=True),
                end_fx(s + 6, pitch=1.5)], s + 34
    if kind == "ash":         # burns black and blows away from the head down
        return [{"op": "swap", "at": s, "block": "coal_block" if alt else "black_concrete", "order": order, "stagger": 10},
                {"op": "burst", "at": s + 12, "dur": 2, "power": 1.2, "up": 0.6, "rand": 0.6, "order": order, "stagger": 16},
                end_fx(s + 12, particle="ASH")], s + 34
    if kind == "burn":        # glows from inside, turns to magma and bursts
        return [{"op": "swap", "at": s, "block": "magma_block", "order": order, "stagger": 12}, {"op": "light", "at": s + 6, "on": True},
                {"op": "scale", "at": s + 12, "dur": 5, "s": [1.2, 1.2, 1.2]},
                {"op": "shatter", "at": s + 18, "pieces": 2, "power": 3 + alt, "up": 3, "order": "random", "stagger": 4},
                prop(s + 18, "fall", "magma_block", 4 + v % 3, 10, size=0.45, r=1.5, stagger=8, lit=True),
                end_fx(s + 18, particle="LAVA")], s + 50
    if kind == "freeze":      # frosts over block by block, then the ice breaks
        return [{"op": "swap", "at": s, "block": "packed_ice" if alt else "ice", "order": order, "stagger": 12},
                prop(s + 2, "rise", "packed_ice", 5 + v % 3, 8, size=0.35, r=1.0, tall=2.5, linger=18),
                {"op": "shatter", "at": s + 18, "pieces": 3, "power": 2.5, "up": 2, "order": "random", "stagger": 3},
                end_fx(s + 18, particle="SNOWFLAKE", pitch=1.4)], s + 50
    if kind == "scatter":     # bursts into loose pieces that roll away in every direction
        return [{"op": "burst", "at": s, "dur": 12, "power": 3.5 + alt, "up": 1.5, "tilt": 160, "order": order, "stagger": 10},
                end_fx(s + 2), prop(s + 2, "rain", b2, 6 + v % 3, 12, size=0.3, r=1.4, stagger=10)], s + 36
    if kind == "whirl":       # spins faster and thinner until nothing is left
        return [{"op": "spin", "at": s, "dur": 8, "deg": 170}, {"op": "scale", "at": s + 2, "dur": 14, "s": [0.3, 1.5 + 0.3 * alt, 0.3]},
                prop(s, "orbit", b1, 6 + v % 3, 18, size=0.35, r=1.4, y=0.6, turns=2.5, lit=lit),
                {"op": "move", "at": s + 10, "dur": 8, "vh": [0, 1.5, 0], "order": order, "stagger": 6}, end_fx(s + 12, pitch=1.3)], s + 28
    if kind == "topple":      # keels over stiff as a statue and breaks on the floor
        return [{"op": "tilt", "at": s, "dur": 9, "axis": "z" if alt else "x", "deg": 88, "pivot": [-P["hx"], 0, 0] if alt else [0, 0, P["hz"]]},
                fx(s + 9, 0.05, 1.2, particle="BLOCK", block=b1.upper(), count=40, sound="ENTITY_IRON_GOLEM_DAMAGE", pitch=0.6),
                {"op": "fling", "at": s + 10, "dur": 12, "power": 2.5, "up": 1.5, "tilt": 120, "order": order, "stagger": 6}, end_fx(s + 12)], s + 40
    if kind == "deflate":     # puffs up, then wrinkles down to nothing
        return [{"op": "scale", "at": s, "dur": 5, "s": [1.25, 1.1, 1.25]}, {"op": "scale", "at": s + 6, "dur": 14, "s": [0.5 + 0.1 * alt, 0.08, 0.5 + 0.1 * alt]},
                {"op": "shrink", "at": s + 12, "dur": 6, "s": 0.4, "order": order, "stagger": 10}, end_fx(s + 8, pitch=1.5)], s + 30
    if kind == "pop":         # swells and pops; the bits rain back down
        return [{"op": "scale", "at": s, "dur": 6, "s": [1.3, 1.3, 1.3]}, {"op": "shake", "at": s, "dur": 6},
                {"op": "shatter", "at": s + 7, "pieces": 2, "power": 4, "up": 4 + alt, "order": order, "stagger": 2},
                prop(s + 10, "rain", b1, 8 + v % 3, 12, size=0.3, r=1.6, stagger=12, lit=lit), end_fx(s + 7, pitch=1.7)], s + 42
    if kind == "wilt":        # browns and dries from the top, then the husk drops
        return [{"op": "swap", "at": s, "block": "brown_concrete" if alt else "dripstone_block", "order": order, "stagger": 14},
                {"op": "scale", "at": s + 8, "dur": 10, "s": [0.85, 0.7, 0.85]},
                {"op": "drop", "at": s + 20, "dur": 6, "tilt": 60, "rand": 0.5, "order": "down", "stagger": 8},
                prop(s + 4, "rain", b2, 6 + v % 3, 14, size=0.25, r=1.2, stagger=14), end_fx(s + 20)], s + 42
    if kind == "sink":        # goes soft and drains away in a slow turn
        return [{"op": "spin", "at": s, "dur": 16, "deg": 120 if alt else -120}, {"op": "scale", "at": s + 2, "dur": 16, "s": [0.9, 0.04, 0.9]},
                prop(s + 2, "orbit", b1, 5 + v % 3, 16, size=0.3, r=1.2, y=0.05, turns=1.5, lit=lit),
                {"op": "toward", "at": s + 12, "dur": 8, "k": 0.9, "y": 0.02, "order": order, "stagger": 4}, end_fx(s + 10)], s + 28
    raise KeyError(kind)


def first(steps, key, default):
    return next((s[key] for s in steps if s.get(key)), default)


def run(models, bosses):
    used_in, used_out = set(), set()
    ids = [i for i in models if i in bosses]
    ids.sort(key=lambda i: i not in PICK)
    for i in ids:
        m, theme = models[i], bosses[i].get("theme", "earth")
        T = THEMES.get(theme, THEMES["earth"])
        seed = zlib.crc32(i.encode())
        old_spawn, old_death = m["spawn"], m["death"]
        # the boss's own particle and voice, remembered from the first run so a second run changes nothing
        P = m.setdefault("fxkit", {"particle": first(old_spawn, "particle", "CLOUD"), "sound": first(old_spawn, "sound", "ENTITY_GENERIC_EXPLODE"),
                                   "dsound": first(old_death, "sound", "ENTITY_GENERIC_DEATH")})
        k = m["scale"] / 16
        P = dict(P, hx=round(max(max(abs(c["f"][0]), abs(c["t"][0])) for c in m["cubes"]) * k, 2),
                 hz=round(max(max(abs(c["f"][2]), abs(c["t"][2])) for c in m["cubes"]) * k, 2))
        if i not in KEEP_SPAWN:
            pref = T[4].split(); pref = pref[seed % len(pref):] + pref[:seed % len(pref)]
            if i in PICK: pref = [PICK[i][0]] + pref
            kinds = pref + [k for k in ALL_IN[seed % 15:] + ALL_IN[:seed % 15] if k not in pref]
            kind, v = next((k, (seed + j) % 10) for k in kinds for j in range(10) if (k, (seed + j) % 10) not in used_in)
            used_in.add((kind, v))
            steps, whole = entrance(kind, v, T, P)
            clip = next(s for s in old_spawn if s["op"] == "anim")
            steps += [{"op": "anim", "at": whole, "dur": clip["dur"], "name": clip["name"]}, {"op": "pose", "at": whole + clip["dur"] + 3, "dur": 3}]
            m["spawn"], m["entrance"] = steps, kind
        if i not in KEEP_DEATH:
            pref = T[5].split(); pref = pref[seed % len(pref):] + pref[:seed % len(pref)]
            if i in PICK: pref = [PICK[i][1]] + pref
            kinds = pref + [k for k in ALL_OUT[seed % 17:] + ALL_OUT[:seed % 17] if k not in pref]
            kind, v = next((k, (seed + j) % 10) for k in kinds for j in range(10) if (k, (seed + j) % 10) not in used_out)
            used_out.add((kind, v))
            clip = next(s for s in old_death if s["op"] == "anim")
            flash = next((s for s in old_death if s["op"] == "flash"), {"op": "flash", "at": 4, "dur": 2, "only": "all", "block": "gray_concrete"})
            # half of them stay on their feet: only the first stagger of the clip plays, then the blocks take over
            stands = kind in ("explode", "implode", "ascend", "whirl", "topple", "pop", "burn", "freeze", "petrify", "deflate") or (seed >> 4) % 3 == 0 and kind != "crumble"
            length = min(clip["dur"], 14) if stands else clip["dur"]
            body, gone = death(kind, v, T, P, length - 2)
            m["death"] = [{"op": "anim", "at": 0, "dur": length, "name": clip["name"]}, dict(flash, at=min(flash.get("at", 4), 5))] + body \
                + [{"op": "shrink", "at": gone, "dur": 8, "s": 0}]
            m["ending"] = kind
    return len(used_in), len(used_out)


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    bosses = yaml.safe_load(open(sys.argv[2]))
    print(run(data["models"], bosses.get("bosses", bosses)))
    json.dump(data, open(sys.argv[1], "w"), separators=(",", ":"))
