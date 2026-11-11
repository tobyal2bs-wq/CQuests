import os
"""Builds models.json from the boss modules: the 25 general bosses, the seasonal ones, the chapter bosses and
the legends. Every model gets its elbows and hit zones, its small pieces are tagged so low detail can drop
them, and its own opening and death from v2_recipes. Checks that every step points at real blocks and
real animations, so a typo shows up here and not on a server."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import anims, models, palette, roster
import v14_kit
import mottle_pass
# the shared biped attacks get the studio set: a wind-up before every hit, weight through the hips and legs,
# and a follow-through, instead of arms swinging on a stiff body
anims.BIPED.update(v14_kit.biped_set(1.0))
for _clip in anims.BIPED.values():                       # hips hang off the root: move the whole body, not the hips
    _h = _clip["bones"].get("hips")
    if _h and "pos" in _h:
        _clip["bones"].setdefault("root", {}).setdefault("pos", _h.pop("pos"))

SELECTORS = {"", "all", "lit", "unlit", "detail", "trim", "vein", "plain"}


def tag(m):
    """Small pieces get a tag: "detail" for the tiniest (dropped first), "trim" for small thin plates."""
    for c in m.cubes:
        if c.get("g") or c.get("l"):
            continue
        w, h, d = (b - a for a, b in zip(c["f"], c["t"]))
        big, small, vol = max(w, h, d), min(w, h, d), w * h * d
        if big <= 1.6:
            c["g"] = "detail"
        elif vol <= 4 and small <= 0.6:
            c["g"] = "trim"
    # every model must lose something on low detail: tag its smallest untagged tenth
    if not any(c.get("g") in ("detail", "trim") for c in m.cubes):
        vol = lambda c: (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2])
        free = sorted((c for c in m.cubes if not c.get("g") and not c.get("l")), key=vol)
        for c in free[:max(1, len(free) // 10)]:
            c["g"] = "detail"


ABILITIES = ["lightning", "shockwave", "minions", "fire_ring", "pull", "leap", "poison", "blink", "frost", "volley", "darkness", "levitate",
             "heal", "quake", "detonate", "roar", "charge", "slam", "meteor", "sonic_boom", "skulls", "breath", "spikes", "orbs", "gifts",
             "sprinkles", "dive", "eggs"]
# a model names its attacks in its own words (hatchets, coal, hymn); each becomes the first fight ability it fits that the
# model does not already use, so every ability the boss casts plays its own move
ALIAS = {"vex": ["minions"], "beam": ["sonic_boom", "orbs"], "fangs": ["spikes"], "souls": ["skulls", "orbs"], "shards": ["volley", "spikes"],
         "shield": ["heal", "charge"], "vines": ["pull", "spikes"], "web": ["pull"], "venom": ["poison"], "wave": ["shockwave"],
         "curse": ["darkness"], "sand": ["spikes", "poison"], "chains": ["pull", "slam"], "fire": ["fire_ring", "breath"], "cannon": ["meteor"],
         "steam": ["darkness", "poison"], "coal": ["meteor", "volley"], "hook": ["pull", "charge"], "snowballs": ["volley"], "slide": ["charge"],
         "blizzard": ["frost", "levitate", "volley"], "freeze": ["frost", "levitate"], "spoon": ["slam"], "carrot": ["charge"], "peck": ["charge"], "caramel": ["orbs"],
         "seeds": ["volley"], "fork": ["charge"], "heads": ["meteor"], "hex": ["darkness"], "potions": ["orbs", "poison"],
         "hatchets": ["volley", "slam", "charge"], "coins": ["volley"], "bite": ["slam", "charge"], "flail": ["slam"], "roots": ["spikes"],
         "thorns": ["volley", "spikes"], "anchor": ["slam"], "hymn": ["darkness", "orbs"], "bell": ["shockwave", "slam"], "sonic": ["sonic_boom"],
         "claws": ["charge", "slam"], "blast": ["shockwave", "orbs"], "gust": ["shockwave", "levitate"], "charges": ["orbs"], "dash": ["charge"],
         "smash": ["slam"], "blade": ["charge"], "orb": ["orbs"], "crown": ["meteor"], "toss": ["slam", "shockwave"], "pounce": ["leap"],
         "sword": ["charge"], "spin": ["blink", "shockwave"], "sweep": ["shockwave", "slam"], "sting": ["poison", "charge"],
         "stomp": ["quake", "shockwave"], "spells": ["orbs", "darkness"], "summon": ["minions"], "magic": ["orbs", "levitate"], "bolt": ["lightning"], "shards2": ["volley"]}


def fight_attacks(m):
    out = {}
    for k, a in m.attacks.items():
        if k in ABILITIES and k not in out:
            out[k] = a
    for k, a in m.attacks.items():
        if k in ABILITIES:
            continue
        for t in ALIAS.get(k, []):
            if t not in out:
                out[t] = a
                break
        else:
            raise SystemExit(f"{m.id}: attack {k} has no fight ability to stand for")
    return out


KEEP_FLAT = {"black_concrete"}


def powder(k):
    """Flat concrete becomes its speckled powder twin, so every face shows pixel texture in game."""
    b = base(k)
    if b.endswith("_concrete") and b not in KEEP_FLAT:
        return b + "_powder" + k[len(b):]
    return k


def texturize(m):
    if getattr(m, "flat", False): return
    for c in m.cubes:
        if not c.get("l"): c["k"] = powder(c["k"])


# how tall each kind of boss stands in game, in blocks: [smallest, biggest]; a model keeps its own place inside the range
SIZE = {"mini": (1.5, 2.0), "big": (3.0, 3.5), "mythic": (4.0, 5.0), "decor": (1.0, 1.6)}
HITBOX = 0.9


def size_class(id):
    if id.startswith("decor_"): return "decor"
    if id in roster.MYTHIC: return "mythic"
    if id in roster.minis() or id in roster.partners(): return "mini"
    return "big"


def normalize(id, j):
    """Stands every model on the ground with its weight over the mob: the volume centre of its blocks goes to
    x = z = 0 and its lowest block to y = 0, then it is scaled to its class height and its hitbox fits it."""
    cubes = [c for c in j["cubes"] if not str(c.get("g", "")).startswith("face:") or c.get("g") == "face:idle"]
    vol = lambda c: max(0.01, (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2]))
    tv = sum(vol(c) for c in cubes)
    cx = sum(vol(c) * (c["f"][0] + c["t"][0]) / 2 for c in cubes) / tv
    cz = sum(vol(c) * (c["f"][2] + c["t"][2]) / 2 for c in cubes) / tv
    y0 = min(min(c["f"][1], c["t"][1]) for c in j["cubes"])
    d = (round(cx, 2), round(y0, 2), round(cz, 2))
    sh = lambda v: [round(v[0] - d[0], 3), round(v[1] - d[1], 3), round(v[2] - d[2], 3)]
    for c in j["cubes"]:
        c["f"], c["t"] = sh(c["f"]), sh(c["t"])
        if "o" in c: c["o"] = sh(c["o"])
    for b in j["bones"]: b["pivot"] = sh(b["pivot"])
    for z in j.get("zones", []): z["c"] = sh(z["c"])
    top = max(max(c["f"][1], c["t"][1]) for c in j["cubes"])
    wide = max(max(abs(c["f"][i]), abs(c["t"][i])) for c in cubes for i in (0, 2)) * 2
    j["height"] = round(top, 2)
    # wide, low models (crabs, turtles, wolves) are sized by their length too, so they don't become giants
    span = max(top, 0.7 * wide)
    lo, hi = SIZE[size_class(id)]
    now = span * j["scale"] / 16
    want = min(hi, max(lo, lo + (hi - lo) * min(1, max(0, (now - lo) / (hi * 2 - lo)))))
    j["scale"] = round(want * 16 / span, 4)
    j["hitbox"] = HITBOX if top >= span * 0.8 else round(max(0.45, top / span), 3)


def base(k):
    return k.split("[")[0]


def check(m, j, steps, what):
    rig = dict(anims.RIGS[m.rig], **(getattr(m, "anims", None) or {}))
    bones = [b["name"] for b in m.bones]
    blocks = {base(c["k"]) for c in m.cubes}
    problems = []
    for s in steps:
        only = s.get("only", "")
        sel = only[1:] if only.startswith("!") else only
        if sel not in SELECTORS and sel not in blocks and not any(b.startswith(sel) for b in bones):
            problems.append(f"{what} {s['op']}@{s['at']}: only={only} matches nothing")
        if s["op"] == "anim" and s.get("name") not in rig:
            problems.append(f"{what} anim {s.get('name')} is not in the {m.rig} rig")
    return problems


out = {"version": 2, "rigs": anims.RIGS, "models": {}}
used, problems = set(), []
SPAWN, DEATH = roster.recipes()

# ---- one entrance for every boss. Walkers appear small high above their spot, grow to full size in the air,
# drop and land with a squash and a puff of dust, then roar. Flyers swirl in from a speck. Only the zombie climbs out.
CLIMBERS = {"rotting_giant"}
try:
    import yaml as _yaml
    _YML = _yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "..", "src", "main", "resources", "bosses.yml")))["bosses"]
except Exception:
    _YML = {}
_THEMES = {k: v.get("theme", "earth") for k, v in _YML.items()}
_FLIERS = {k for k, v in _YML.items() if v.get("movement") in ("fly", "hover")}
_BURST = {"fire": "FLAME", "frost": "SNOWFLAKE", "soul": "SOUL_FIRE_FLAME", "nature": "CHERRY_LEAVES", "water": "SPLASH", "storm": "ELECTRIC_SPARK",
          "gold": "WAX_ON", "toxic": "ITEM_SLIME", "blood": "CRIMSON_SPORE", "void": "PORTAL", "witch": "WITCH", "sculk": "SCULK_SOUL",
          "wither": "SMOKE", "candy": "CHERRY_LEAVES", "holiday": "SNOWFLAKE", "pumpkin": "FLAME", "feather": "CLOUD", "wind": "CLOUD",
          "earth": "CLOUD", "iron": "CLOUD", "bone": "CLOUD", "sand": "CLOUD"}


def entrance(id, old):
    sound = next((st["sound"] for st in old if st.get("op") == "fx" and st.get("sound")), "ENTITY_EVOKER_PREPARE_SUMMON")
    pitch = next((st.get("pitch", 1.0) for st in old if st.get("op") == "fx" and st.get("sound")), 1.0)
    roar = next((st["name"] for st in old if st.get("op") == "anim" and st.get("name") not in ("walk",)), None)
    p = _BURST.get(_THEMES.get(id, "earth"), "CLOUD")
    if id in _FLIERS:
        steps = [{"op": "shrink", "at": 0, "s": 0.05}, {"op": "spin", "at": 0, "deg": -150}, {"op": "move", "at": 0, "vh": [0, 0.5, 0]},
                 {"op": "fx", "at": 0, "y": 0.9, "spread": 0.6, "particle": p, "count": 30, "sound": sound, "pitch": pitch},
                 {"op": "pose", "at": 2, "dur": 16},
                 {"op": "fx", "at": 10, "y": 0.6, "spread": 1.2, "particle": p, "count": 30},
                 {"op": "fx", "at": 18, "y": 0.5, "spread": 0.2, "particle": "FLASH", "count": 1, "sound": "ENTITY_PHANTOM_FLAP", "pitch": 0.6}]
        start = 20
    else:
        steps = [{"op": "shrink", "at": 0, "s": 0.05}, {"op": "move", "at": 0, "vh": [0, 1.5, 0]},
                 {"op": "fx", "at": 0, "y": 1.9, "spread": 0.5, "particle": p, "count": 30, "sound": sound, "pitch": pitch},
                 {"op": "shrink", "at": 2, "dur": 10, "s": 20},
                 {"op": "fx", "at": 8, "y": 1.9, "spread": 1.0, "particle": p, "count": 24},
                 {"op": "pose", "at": 14, "dur": 5},
                 {"op": "fx", "at": 19, "y": 0.02, "spread": 1.6, "particle": "CLOUD", "count": 40, "sound": "ENTITY_GENERIC_EXPLODE", "pitch": 0.6},
                 {"op": "fx", "at": 19, "y": 0.1, "spread": 1.2, "particle": p, "count": 30},
                 {"op": "scale", "at": 19, "dur": 2, "s": [1.12, 0.82, 1.12]},
                 {"op": "pose", "at": 21, "dur": 4}]
        start = 26
    return steps + ([{"op": "anim", "at": start, "dur": 24, "name": roar}] if roar else [])


def weight(clip):
    """Every attack gets its body behind it: the whole model leans back as it winds up, drives forward into the
    hit and settles, unless the clip already moves the root itself."""
    h, L = clip.get("hit"), clip["length"]
    root = clip["bones"].setdefault("root", {})
    if not h or "rot" in root or h >= L: return
    root["rot"] = [[0, [0, 0, 0]], [round(h * 0.65, 4), [-6, 0, 0]], [round(h, 4), [8, 0, 0]],
                   [round(h + (L - h) * 0.35, 4), [5, 0, 0]], [L, [0, 0, 0]]]


# grubnose and mudclub carry their own painted mottling (v14_studio.hide_detail)
import v14_studio
SKINNED_BY_HAND = {"grubnose", "mudclub"}

for id, fn in roster.builders().items():
    m = fn()
    if hasattr(m, "approved"):
        out["models"][m.id] = m.approved
        out["rigs"].setdefault(m.approved["rig"], {})
        used |= {base(c["k"]) for c in m.approved["cubes"]}
        continue
    if m.rig in ("biped", "float") and not getattr(m, "no_elbows", False):
        m.elbows(bend=getattr(m, "bend", -38), weapons=getattr(m, "hold", None))
    if m.rig in ("biped", "quad"): m.knees()
    m.zones()
    tag(m)
    if m.id in v14_studio.STUDIO and m.id not in SKINNED_BY_HAND and not m.id.startswith("decor_") and not getattr(m, "flat", False) and not getattr(m, "sculpted", False): mottle_pass.skin(m)
    texturize(m)
    m.attacks = fight_attacks(m)
    j = m.json()
    if m.id not in SPAWN or m.id not in DEATH:
        problems.append(f"{m.id}: no opening or death written")
        continue
    fixo = lambda s: dict(s, **{f: (s[f][0] + powder(s[f][1:]) if s[f].startswith("!") else powder(s[f])) for f in ("only",) if isinstance(s.get(f), str) and s[f] and not getattr(m, "flat", False) and powder(s[f].lstrip("!")) in {base(c["k"]) for c in m.cubes}})
    spawn = [fixo(s) for s in SPAWN[m.id]]
    # a model with parts that only show during its entrance (the egg Clucksworth hatches from) keeps its own
    if m.id not in CLIMBERS and not m.id.startswith("decor_") and not any("shell" in str(st.get("only", "")) or st.get("op") in ("hide", "reveal") for st in spawn): spawn = entrance(m.id, spawn)
    end = max(st["at"] + st.get("dur", 0) for st in spawn)
    spawn.append({"op": "pose", "at": end + 2, "dur": 4})   # whatever the opening did, it ends in the model's own shape
    j["spawn"], j["death"] = spawn, [fixo(s) for s in DEATH[m.id]]
    problems += [f"{m.id}: {p}" for p in check(m, j, j["spawn"], "spawn") + check(m, j, j["death"], "death")]
    if not any(s["op"] == "flash" for s in j["death"]):
        problems.append(f"{m.id}: death has no flash")
    for a in set(m.attacks.values()) | ({m.melee} if m.melee else set()):
        if a not in anims.RIGS[m.rig] and a not in (getattr(m, "anims", None) or {}):
            problems.append(f"{m.id}: attack anim {a} not in {m.rig}")
    normalize(m.id, j)
    out["models"][m.id] = j
    used |= {base(c["k"]) for c in m.cubes}

missing = sorted(b for b in used if b not in palette.P)
if missing: print("no preview colour for", missing)
if problems:
    print("\n".join(problems))
    sys.exit(1)
import polish
import v13_approved
import v14_studio
# hand-built studio models carry their own moves and joints; the older automatic passes would cut and move them
HANDMADE = set(v13_approved.APPROVED) | v14_studio.STUDIO
for model_id, data in out["models"].items():
    if model_id not in HANDMADE: polish.apply(model_id, data, out["rigs"])
import refine
for model_id, data in out["models"].items():
    if model_id not in HANDMADE: refine.apply(model_id, data, out["rigs"])


_OPENINGS = set()


def _key(c):
    import json
    return str(c["length"]) + json.dumps(c["bones"], sort_keys=True)


def studio_finish(id, m, rigs):
    """Studio models keep their own moves, entrance and death, and get what the shared engine needs on top:
    a hurt, an opening and a death clip of their own, no ring effects, no attack that slides an attached bone
    off its hinge (the root moves the whole body instead), and rest geometry standing on y=0."""
    import zlib, copy
    seed = zlib.crc32(id.encode())
    tweak = 1 + (zlib.crc32((id + ":hurt").encode()) % 9973) / 40000
    rig = dict(rigs[m["rig"]], **(m.get("anims") or {}))
    names = {b["name"]: b for b in m["bones"]}
    top = {b["name"] for b in m["bones"] if b.get("parent") == "root"}
    anims_ = m.setdefault("anims", {})

    def own(clip, factor):
        c = copy.deepcopy(clip)
        c["length"] = round(c["length"] * factor, 6)
        if "hit" in c: c["hit"] = round(c["hit"] * factor, 6)
        for ch in c["bones"].values():
            for keys in ch.values():
                for k in keys: k[0] = round(k[0] * factor, 6)
        return c

    attacks = {n for n, c in rig.items() if not c.get("loop") and not n.startswith(("die", "death", "opening")) and n != "hurt"}
    for name in attacks:
        clip = copy.deepcopy(rig[name])
        bones = {n: ch for n, ch in clip["bones"].items() if n in names or n == "root"}
        for n in list(bones):
            ch = bones[n]
            if n == "root" or "pos" not in ch: continue
            moved = ch.pop("pos")
            if n in top and "pos" not in bones.setdefault("root", {}): bones["root"]["pos"] = moved
            if not ch: bones.pop(n)
        clip["bones"] = bones
        anims_[name] = clip
    anims_["hurt"] = own(rig["hurt"], tweak)
    side = (seed % 9) - 4                                          # each one flinches to its own side
    for ch in anims_["hurt"]["bones"].values():
        for keys in ch.get("rot", [])[1:-1]:
            keys[1] = [keys[1][0], keys[1][1] + side, keys[1][2] - side * 0.5]
    for st in m["spawn"]:
        st.pop("ring", None)
    sp = next((st for st in m["spawn"] if st["op"] == "anim"), None)
    src = sp["name"] if sp and sp.get("name") in rig else "idle"
    f = 1 + (seed // 7 % 991) / 6000
    opening = own(rig[src], f)
    while _key(opening) in _OPENINGS:                               # two ids can land on the same factor
        f += 0.00071
        opening = own(rig[src], f)
    _OPENINGS.add(_key(opening))
    opening.pop("loop", None)
    anims_["opening_" + id] = opening
    if sp: sp["name"] = "opening_" + id
    else: m["spawn"].append({"op": "anim", "at": 4, "dur": round(opening["length"] * 20), "name": "opening_" + id})
    for st in m["death"]: st.pop("ring", None)
    dp = next((st for st in m["death"] if st["op"] == "anim"), None)
    dsrc = dp["name"] if dp and dp.get("name") in rig else next(n for n in rig if n.startswith("die"))
    anims_["death_" + id] = own(rig[dsrc], 1 + (seed // 13 % 983) / 5000)
    if dp: dp["name"] = "death_" + id
    else: m["death"].insert(0, {"op": "anim", "at": 0, "dur": round(anims_["death_" + id]["length"] * 20), "name": "death_" + id})
    floor = min(c["f"][1] for c in m["cubes"] if not c["b"].startswith("shell") and not c.get("g", "").startswith("face:"))
    if abs(floor) > 1e-4:
        for b in m["bones"]: b["pivot"][1] = round(b["pivot"][1] - floor, 5)
        for c in m["cubes"]:
            c["f"][1] = round(c["f"][1] - floor, 5); c["t"][1] = round(c["t"][1] - floor, 5)
            if "o" in c: c["o"][1] = round(c["o"][1] - floor, 5)
        for z in m.get("zones", []): z["c"][1] = round(z["c"][1] - floor, 5)


for model_id, data in out["models"].items():
    if model_id in v14_studio.STUDIO and not model_id.startswith("decor_"): studio_finish(model_id, data, out["rigs"])
_ATTACK = lambda n, c: not c.get("loop") and c.get("hit") and n not in ("hurt", "roar", "howl") and not n.startswith(("die", "death", "opening"))
for rig in out["rigs"].values():
    for n, c in rig.items():
        if _ATTACK(n, c): weight(c)
for model_id, data in out["models"].items():
    if model_id.startswith("decor_"): continue
    for n, c in (data.get("anims") or {}).items():
        if _ATTACK(n, c): weight(c)
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../../src/main/resources/models.json")
json.dump(out, open(dest, "w"), separators=(",", ":"))
for id, m in out["models"].items():
    tags = sum(1 for c in m["cubes"] if c.get("g"))
    print(f"{id:20s} {len(m['cubes']):3d} cubes ({tags} small)  {m['height'] * m['scale'] / 16:.1f} blocks tall  {m['rig']}")
print(len(out["models"]), "models")
pv = {"rigs": out["rigs"], "models": out["models"], "palette": {k: list(v) for k, v in palette.P.items()}}
pd = os.environ.get("PREVIEW_DATA", os.path.join(os.path.dirname(__file__), "../../build/preview-data.js"))
os.makedirs(os.path.dirname(pd), exist_ok=True)
open(pd, "w").write("const DATA=" + json.dumps(pv, separators=(",", ":")) + ";")
