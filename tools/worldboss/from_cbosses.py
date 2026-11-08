"""Brings the CBosses roster into CQuests: copies the block models into worldboss-models.json and writes
worldbosses.yml for the world bosses (the 25 general bosses, the four legends and the 12 seasonal ones;
chapter bosses and the finale stay in CBosses). Abilities CQuests does not have are turned into the closest
one it has, and each model's attack moves follow, so every ability still plays the boss's own move.
Run from the CQuests repo root: python3 tools/worldboss/from_cbosses.py ../CBosses"""
import json, re, sys, os, yaml

CB = sys.argv[1] if len(sys.argv) > 1 else "../CBosses"
models = json.load(open(os.path.join(CB, "src/main/resources/models.json")))
cb = yaml.safe_load(open(os.path.join(CB, "src/main/resources/bosses.yml")))["bosses"]
old = yaml.safe_load(open("src/main/resources/worldbosses.yml"))["bosses"]

HAVE = ["lightning", "shockwave", "minions", "fire_ring", "pull", "leap", "poison", "blink", "frost", "volley", "darkness",
        "levitate", "heal", "quake", "detonate", "roar", "meteor"]
SWAP = {"charge": ["leap"], "slam": ["shockwave", "quake"], "sonic_boom": ["roar", "darkness"], "skulls": ["volley"], "breath": ["fire_ring"],
        "spikes": ["quake", "shockwave"], "orbs": ["volley", "levitate"], "gifts": ["volley"], "eggs": ["volley"], "sprinkles": ["volley"],
        "dive": ["leap", "blink"]}
THEME = {"soul": "SOUL_FIRE_FLAME", "fire": "FLAME", "frost": "SNOWFLAKE", "nature": "HAPPY_VILLAGER", "gold": "WAX_ON", "water": "BUBBLE_POP",
         "storm": "ELECTRIC_SPARK", "earth": "CAMPFIRE_COSY_SMOKE", "blood": "CRIMSON_SPORE", "toxic": "ITEM_SLIME", "void": "PORTAL", "witch": "WITCH",
         "sand": "WAX_OFF", "bone": "WHITE_ASH", "sculk": "SCULK_SOUL", "wither": "SMOKE", "dragon": "PORTAL", "holiday": "SNOWFLAKE",
         "candy": "CHERRY_LEAVES", "pumpkin": "FLAME", "feather": "CLOUD", "iron": "CRIT", "wind": "CLOUD"}


def convert(abilities):
    out = []
    for a in abilities:
        if a in HAVE:
            if a not in out: out.append(a)
            continue
        for t in SWAP.get(a, []):
            if t not in out:
                out.append(t); break
    return out


ids = [i for i, b in cb.items() if not b.get("chapter") and i != "the_unmaker"]
# models: every CBosses model, attack moves renamed to CQuests abilities
out_models = {"version": models.get("version", 1), "rigs": models["rigs"], "models": {}}
for i in ids:
    m = dict(models["models"][i])
    att = {}
    for k, a in m["attacks"].items():
        if k in HAVE:
            att.setdefault(k, a)
    for k, a in m["attacks"].items():
        if k in HAVE: continue
        for t in SWAP.get(k, []):
            if t not in att:
                att[t] = a; break
    m["attacks"] = att
    out_models["models"][i] = m
json.dump(out_models, open("src/main/resources/worldboss-models.json", "w"), separators=(",", ":"))


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def lst(v):
    return "[" + ", ".join(q(x) for x in v) + "]"


head = open("src/main/resources/worldbosses.yml").read().split("\nbosses:")[0]
head = re.sub(r"# abilities:.*?\n(#\s+levitate.*?\n)", "# abilities: lightning, shockwave, minions, fire_ring, pull, leap, poison, blink, frost, volley, darkness,\n#            levitate, heal, quake, detonate, roar, meteor (falling rocks that leave broken pieces for a while)\n", head, flags=re.S)
lines = [head, "bosses:"]
for i in ids:
    b, o = cb[i], old.get(i, {})
    ab = convert(b["abilities"])
    if "meteor" not in ab and b["theme"] in ("fire", "dragon", "void", "wither", "storm", "pumpkin") and "meteor" in b["abilities"]:
        ab.append("meteor")
    cols = re.findall(r"#[0-9a-fA-F]{6}", b["name"])
    r = b.get("rewards", {})
    lines.append(f"  {i}:")
    lines.append(f"    name: {q(b['name'])}")
    lines.append(f"    title: {q(b.get('title', ''))}")
    lines.append(f"    entity: {b['entity']}")
    lines.append(f"    health: {b['health']}")
    lines.append(f"    scale: {o.get('scale', 1.6)}")
    lines.append(f"    damage: {b['damage']}")
    lines.append(f"    armor: {b.get('armor', 0)}")
    lines.append(f"    bar: {b.get('bar', 'RED')}")
    lines.append(f"    glow: {str(o.get('glow', True)).lower()}")
    lines.append(f"    particle: {o.get('particle') or THEME.get(b['theme'], 'FLAME')}")
    lines.append(f"    color: {q(o.get('color') or (cols[-1] if cols else '#ff5500'))}")
    if o.get("equipment"):
        lines.append("    equipment:")
        for k, v in o["equipment"].items(): lines.append(f"      {k}: {v}")
    if b.get("minion"):
        lines.append(f"    minion: {b['minion']}")
        lines.append(f"    minions: {min(8, b.get('minions', 3))}")
    if b.get("season"): lines.append(f"    season: {b['season']}")
    lines.append(f"    ability-seconds: {max(3, b.get('ability-seconds', 7))}")
    lines.append(f"    abilities: [{', '.join(ab)}]")
    lines.append("    rewards:")
    lines.append(f"      money: {r.get('money', 0)}")
    lines.append(f"      top-money: {r.get('top-money', 0)}")
    lines.append(f"      items: {lst(r.get('items', []))}")
    lines.append(f"      top-items: {lst(r.get('top-items', []))}")
    lines.append(f"      commands: {lst(r.get('commands', []))}")
    lines.append(f"      top-commands: {lst(r.get('top-commands', []))}")
open("src/main/resources/worldbosses.yml", "w").write("\n".join(lines) + "\n")
print(len(ids), "world bosses,", len(out_models["models"]), "models")
