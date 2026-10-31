import json, sys, re
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from story import R, DAILY
out_dir = sys.argv[2]
q = json.dumps
assert len(R) == 100, len(R)
ids = [r[0] for r in R]
assert len(set(ids)) == 100

SKIN = {"PLAINS":"PLAINS","DESERT":"DESERT","JUNGLE":"JUNGLE","SAVANNA":"SAVANNA","SWAMP":"SWAMP","TAIGA":"TAIGA",
        "SNOWY_TAIGA":"SNOW","SNOWY_PLAINS":"SNOW","RIVER":"PLAINS","BEACH":"PLAINS","OCEAN":"PLAINS","WARM_OCEAN":"PLAINS",
        "DEEP_OCEAN":"PLAINS","FLOWER_FOREST":"PLAINS","FOREST":"PLAINS","BADLANDS":"DESERT","MOUNTAINS":"TAIGA",
        "CRIMSON_FOREST":"SAVANNA","NETHER_WASTES":"SAVANNA","SOUL_SAND_VALLEY":"SAVANNA","BASALT_DELTAS":"SAVANNA",
        "END":"PLAINS","DEEP_DARK":"TAIGA","LUSH_CAVES":"JUNGLE","MUSHROOM_FIELDS":"SWAMP","DARK_FOREST":"TAIGA"}
TIERS = [(9, ["BREAD 8","TORCH 16","IRON_INGOT 2","COOKED_BEEF 6","APPLE 6"]),
         (19,["IRON_INGOT 4","GOLD_INGOT 3","ARROW 32","BAKED_POTATO 12","LANTERN 4"]),
         (34,["IRON_INGOT 8","GOLD_INGOT 6","EMERALD 3","EXPERIENCE_BOTTLE 8","NAME_TAG 1"]),
         (49,["DIAMOND 1","EMERALD 6","EXPERIENCE_BOTTLE 16","GOLDEN_CARROT 16","SADDLE 1"]),
         (69,["DIAMOND 2","EXPERIENCE_BOTTLE 24","GOLDEN_APPLE 1","BLAZE_ROD 6","ENDER_PEARL 4"]),
         (89,["DIAMOND 3","GOLDEN_APPLE 2","EXPERIENCE_BOTTLE 32","EMERALD_BLOCK 1","SHULKER_SHELL 2"]),
         (99,["DIAMOND 4","NETHERITE_SCRAP 1","GOLDEN_APPLE 3","EXPERIENCE_BOTTLE 48","DIAMOND_BLOCK 1"])]
SPECIAL = {"wade": (6000, ["DIAMOND_BLOCK 1"]),
           "aldis": (8000, ["NETHERITE_INGOT 1", "GOLDEN_APPLE 4"]),
           "aldric": (10000, ["DIAMOND 8"])}
# A few villagers are children, and a few are player shaped NPCs (Minecraft 1.21.9+, villager on older servers).
# player-skin takes any Minecraft username; "default" uses the plain Steve and Alex skins.
BABY = {"benny", "kip", "daisy"}
SKINNED = {"cecil": "default", "ned": "default", "wade": "default", "aldric": "default"}

def side_required(i):
    """Side quests for the previous villager before story quest i opens. Chapter openers are the big walls."""
    if i < 5:
        return 0  # the first steps are a tutorial: straight from villager to villager
    if i % 20 == 0:
        return 20
    if i % 5 == 4:
        return 2  # a short stretch of story every few steps
    return 4 + (i // 20 + 1)

def items_for(level, i):
    for mx, items in TIERS:
        if level <= mx:
            return [items[i % len(items)]]

def lst(lines, indent):
    pad = " " * indent
    return "".join(f"{pad}- {q(x)}\n" for x in lines)

npcs = ["# The villagers. Act 1 (14 story villagers + the daily one) stands at spawn. Act 2 lives out in the world and is personal:",
        "# a personal villager is only visible to players who need it for a quest or have met it.",
        "#",
        "# profession: ARMORER BUTCHER CARTOGRAPHER CLERIC FARMER FISHERMAN FLETCHER LEATHERWORKER",
        "#             LIBRARIAN MASON NITWIT NONE SHEPHERD TOOLSMITH WEAPONSMITH",
        "# skin:       PLAINS DESERT JUNGLE SAVANNA SNOW SWAMP TAIGA",
        "# level:      shown on the name tag; the robe badge goes stone > iron > gold > emerald > diamond every 20 levels",
        "# intro:      said the first time a player clicks the villager",
        "# idle:       one of these is said when the villager has nothing for you",
        "# baby:       true for a baby villager",
        "# player-skin: a Minecraft username (or default) to use a player shaped NPC with that skin on 1.21.9+",
        "", "npcs:"]
def npc_block(id, name, prof, skin, title, level, act, personal, daily, intro, idle):
    s = f"  {id}:\n    name: {q(name)}\n    title: {q(title)}\n    profession: {prof}\n    skin: {SKIN.get(skin, 'PLAINS')}\n"
    s += f"    level: {level}\n    act: {act}\n"
    if id in BABY: s += "    baby: true\n"
    if id in SKINNED: s += f"    player-skin: {q(SKINNED[id])}\n"
    if personal: s += "    personal: true\n"
    if daily: s += "    daily: true\n"
    s += "    intro:\n" + lst(intro, 6) + "    idle:\n" + lst(idle if isinstance(idle, list) else [idle], 6)
    return s

d = DAILY
npcs.append(npc_block(d[0], d[1], d[2], d[3], d[4], 50, 1, False, True, d[5], d[6]))
for i, r in enumerate(R):
    (id, name, prof, skin, title, intro, qname, objs, offer, desc, complete, idle) = r
    act = 1 if i < 14 else 2
    npcs.append(npc_block(id, name, prof, skin, title, i, act, act == 2, False, intro, idle))

# Keep the optional 1.1 villagers when regenerating Claude's original story.
extras = Path(__file__).with_name("side-villagers.yml").read_text(encoding="utf-8")
extra_ids = re.findall(r"^  ([a-z0-9_]+):", extras, re.M)
assert len(extra_ids) == len(set(extra_ids))
assert not set(extra_ids).intersection(ids + [DAILY[0]])
npcs.append(extras.rstrip() + "\n")

qs = ["# Story quests: the linked chain through all 100 villagers, done in order. Finishing the last one plays the ending.",
      "# big: true plays a celebration (the last quest of each chapter always does). Before a story quest opens, players",
      "# do side-required side quests for the previous villager (default: quests.side-quests-per-chapter in config.yml).",
      "# requires: defaults to the story quest above it, so new quests and chapters can simply be added at the bottom.",
      "# Side quests and the daily pool are generated from generator.yml.",
      "#",
      "# objectives (one per line):",
      "#   KILL <entity> <amount> [label]        MINE / HARVEST / PLACE <block> <amount> [label]",
      "#   CRAFT / SMELT / FISH / CONSUME <item> <amount> [label]",
      "#   BREED / TAME / SHEAR <entity> <amount> [label]       ENCHANT ANY <amount> [label]",
      "#   DELIVER <item> <amount> [to:<npc>] [label]   (items are taken when you click the villager)",
      "#   TALK <npc>                            (counts once the other objectives are done)",
      "# Targets accept A|B, wildcards like *_LOG, groups like @IRON (config.yml) or ANY.",
      "# turn-in: who you return to. Defaults to the giver, or the TALK villager if the last objective is TALK.",
      "# {npc:id}, {player} and {server} are filled in inside text.",
      "",
      "# Chapter names, shown in the journal and on the title card when a chapter ends.",
      "chapters:",
      "  1: \"The Wanderers' Camp\"",
      "  2: \"Shadows at the Gate\"",
      "  3: \"The Elder's Charge\"",
      "  4: \"The Five Keys\"",
      "  5: \"The King Wakes\"",
      "", "quests:"]
def quest_block(id, name, level, order, giver, requires, objs, desc, offer, complete, money, items, big=False, chapter=1, side=None):
    s = f"  {id}:\n    name: {q(name)}\n    level: {level}\n    order: {order}\n    giver: {q(giver)}\n"
    s += f"    chapter: {chapter}\n"
    if side is not None: s += f"    side-required: {side}\n"
    if big: s += "    big: true\n"
    if requires: s += f"    requires: [{requires}]\n"
    s += "    objectives:\n" + lst(objs, 6)
    s += f"    description: {q(desc)}\n"
    if offer: s += "    offer:\n" + lst(offer, 6)
    s += "    complete:\n" + lst(complete, 6)
    s += f"    rewards:\n      money: {money}\n"
    if items: s += "      items:\n" + lst(items, 8)
    return s

qs.append(quest_block("welcome", "Welcome to {server}", 0, 0, "", None, ["TALK stephan"],
    "Talk to {npc:stephan} just ahead of /spawn.", None,
    ["There you are! Welcome to {server}, {player}."], 250, ["BREAD 8"]))
prev = "welcome"
for i, r in enumerate(R):
    (id, name, prof, skin, title, intro, qname, objs, offer, desc, complete, idle) = r
    complete = list(complete)
    if i + 1 < len(R) and id != "marcus":
        nxt = R[i + 1][0]
        # TALK quests finish at the next villager, who then points onward themselves.
        if not objs[-1].startswith("TALK"):
            complete.append("Go and see {npc:%s} next. They could use you." % nxt)
    big = id in ('marcus', 'wade', 'holly', 'aldis', 'osric')
    money = int(round((300 + i * 25) / 50.0)) * 50 * (2 if big else 1)
    money, items = SPECIAL.get(id, (money, items_for(i, i)))
    qid = "story_" + id
    chapter = i // 20 + 1
    qs.append(quest_block(qid, qname, i, i + 1, id, prev, objs, desc, offer, complete, money, items, big, chapter, side_required(i)))
    prev = qid

open(out_dir + "/npcs.yml", "w").write("\n".join(npcs[:npcs.index("npcs:") + 1]) + "\n" + "".join(npcs[npcs.index("npcs:") + 1:]))
open(out_dir + "/quests.yml", "w").write("\n".join(qs[:qs.index("quests:") + 1]) + "\n" + "".join(qs[qs.index("quests:") + 1:]))
print("ok")
