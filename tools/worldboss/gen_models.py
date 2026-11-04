import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import anims, models, palette, bipeds, quads, others, recipes
out = {"version": 1, "rigs": anims.RIGS, "models": {}}
used = set()
for fn in models.MODELS:
    m = fn()
    j = m.json()
    j["spawn"] = recipes.SPAWN[m.id]
    j["death"] = recipes.DEATH[m.id]
    out["models"][m.id] = j
    used |= {palette.base(c["k"]) for c in m.cubes}
missing = sorted(b for b in used if b not in palette.P)
if missing: print("no preview colour for", missing)
dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../../src/main/resources/worldboss-models.json")
json.dump(out, open(dest, "w"), separators=(",", ":"))
for id, m in out["models"].items(): print(f"{id:20s} {len(m['cubes']):3d} cubes  {m['height'] * m['scale'] / 16:.1f} blocks tall")
# preview data
pv = {"rigs": anims.RIGS, "models": out["models"], "palette": {k: list(v) for k, v in palette.P.items()}}
open("/tmp/claude-0/wb/v2/data.js", "w").write("const DATA=" + json.dumps(pv, separators=(",", ":")) + ";")
