"""python3 export_bbmodel.py models.json texture_dir out_dir [ids]: writes one Blockbench .bbmodel per boss
(Generic Model format): every block as a cube with its vanilla block texture, grouped under its bone with the
bone's pivot, so the model can be opened, inspected and edited in Blockbench. Animations are not exported."""
import base64, json, os, sys, uuid

src, tex, out = sys.argv[1:4]
D = json.load(open(src))["models"]
ids = sys.argv[4].split(",") if len(sys.argv) > 4 else list(D)
os.makedirs(out, exist_ok=True)


def png(block, top=False):
    b = block.split("[")[0]
    for n in ([b + "_top"] if top else []) + [b, b + "_side", b + "_top"]:
        p = os.path.join(tex, n + ".png")
        if os.path.exists(p): return p


for id in ids:
    M = D[id]
    textures, index = [], {}
    def tid(block, top=False):
        p = png(block, top)
        if not p: return None
        if p not in index:
            index[p] = len(textures)
            textures.append({"name": os.path.basename(p), "id": str(len(textures)), "uuid": str(uuid.uuid4()), "width": 16, "height": 16,
                             "uv_width": 16, "uv_height": 16, "source": "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()})
        return index[p]
    elements, kids = [], {b["name"]: [] for b in M["bones"]}
    for i, c in enumerate(M["cubes"]):
        u = str(uuid.uuid4())
        side, top = tid(c["k"]), tid(c["k"], True)
        e = {"name": c["k"].split("[")[0], "type": "cube", "uuid": u, "from": c["f"], "to": c["t"], "box_uv": False, "autouv": 0,
             "origin": c.get("o", [(a + b) / 2 for a, b in zip(c["f"], c["t"])]), "rotation": c.get("r", [0, 0, 0]),
             "faces": {f: {"uv": [0, 0, 16, 16], "texture": top if f in ("up", "down") else side} for f in ("north", "east", "south", "west", "up", "down")}}
        elements.append(e); kids[c["b"]].append(u)
    groups = {b["name"]: {"name": b["name"], "uuid": str(uuid.uuid4()), "origin": b["pivot"], "rotation": b.get("rest", [0, 0, 0]),
                          "isOpen": b["name"] == "root", "children": kids[b["name"]]} for b in M["bones"]}
    roots = []
    for b in M["bones"]:
        (groups[b["parent"]]["children"] if b["parent"] else roots).append(groups[b["name"]])
    json.dump({"meta": {"format_version": "4.10", "model_format": "free", "box_uv": False}, "name": id, "resolution": {"width": 16, "height": 16},
               "elements": elements, "outliner": roots, "textures": textures}, open(os.path.join(out, id + ".bbmodel"), "w"))
    print(id, len(elements), "cubes", len(textures), "textures")
