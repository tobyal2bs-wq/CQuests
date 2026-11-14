"""Dev preview: builds the chosen models into a copy of the viewer and renders turnaround pictures.
python3 tools/dev/dev.py module id [id...]"""
import json, os, re, sys, subprocess, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "models"))
import anims, models
mod = importlib.import_module(sys.argv[1])
for extra in os.environ.get("ALSO", "").split(","):
    if extra: importlib.import_module(extra)
ids = sys.argv[2:]
out = {}
fns = {f.__name__: f for f in models.MODELS}
for id in ids:
    m = fns[id]()
    if m.rig in ("biped", "float") and not getattr(m, "no_elbows", False): m.elbows(bend=getattr(m, "bend", -38), weapons=getattr(m, "hold", None))
    if m.rig in ("biped", "quad"): m.knees()
    m.zones()
    j = m.json()
    import v2_recipes as _r
    j["spawn"] = getattr(mod, "SPAWN", {}).get(id) or _r.SPAWN.get(id, [{"op": "pose", "at": 0}])
    j["death"] = getattr(mod, "DEATH", {}).get(id) or _r.DEATH.get(id, [{"op": "flash", "at": 0, "dur": 3}])
    out[id] = j
    import palette as _p
    miss = sorted({c["k"].split("[")[0] for c in j["cubes"]} - set(_p.P))
    if miss: print("  !! no palette colour (shows purple):", miss)
    print(id, len(j["cubes"]), "cubes", round(j["height"] * j["scale"] / 16, 1), "blocks tall")
html = open(os.path.join(ROOT, "docs/viewer.html")).read()
i = html.find("const DATA = ") + len("const DATA = ")
data, n = json.JSONDecoder().raw_decode(html[i:])
data["models"].update(out); data["rigs"] = anims.RIGS
import palette; data["palette"] = {a: list(b) for a, b in palette.P.items()}
have = {b["id"] for b in data["bosses"]}
for id in ids:
    if id not in have:
        data["bosses"].insert(0, dict(data["bosses"][0], id=id, name=id, season="", chapter=0, kind="world", movement="walk"))
html = html[:i] + json.dumps(data, separators=(",", ":")) + html[i + n:]
dst = os.environ.get("DEV_OUT", "/tmp/claude-0/-home-claude/0a4cdc6c-2611-5b03-9f9a-fb9d5065fdf9/scratchpad/dev")
os.makedirs(dst, exist_ok=True)
open(os.path.join(dst, "viewer.html"), "w").write(html)
