"""Exports every boss model as a Blockbench project (.bbmodel), so a model can be opened, edited and animated
in Blockbench (File > Open Model) and dropped back into the server.

    python3 tools/blockbench.py                 # all models into blockbench/
    python3 tools/blockbench.py gorehorn mallard

What is in a file:
- one group per bone (same name and pivot), one cube per block display, named after its block;
- the model's animations (idle, walk, attacks, hurt, opening and death) as Blockbench animations, with a
  timeline marker on the frame where an attack hits;
- a small texture with one tile per block, coloured like the block, so the model reads in Blockbench.
  The game ignores it: what a cube shows in game is the block in its name.

Editing rules:
- Rename a cube to change its block (any block id, e.g. "mossy_cobblestone"). Add "|lit" to make it glow and
  "|trim" or "|detail" to let low detail drop it, e.g. "red_wool|trim".
- Groups are bones; keep the bone names the animations use (body, head, armL, legL...).
- Save as .bbmodel and put it in plugins/CBosses/models/<id>.bbmodel, then /cbosses reload. The id is the file
  name; attacks, entrance, death and hit zones come from the built-in model with that id.
"""
import base64
import json
import os
import struct
import sys
import uuid
import zlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools", "models"))
import palette  # noqa: E402

TILE = 16


def _uuid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "cbosses/" + "/".join(map(str, parts))))


def _png(w, h, rows):
    """rows: list of bytes (RGBA). A minimal PNG writer, so the exporter needs no image library."""
    raw = b"".join(b"\0" + r for r in rows)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _rgb(hexc):
    hexc = hexc.lstrip("#")
    return tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))


def _base(block):
    b = block
    for suffix in ("_powder",):
        if b.endswith(suffix) and b[:-len(suffix)] in palette.P: return b[:-len(suffix)]
    return b


def _colours(block):
    p = palette.P.get(block) or palette.P.get(_base(block))
    if not p: return (200, 200, 200), (170, 170, 170)
    return _rgb(p[1]), _rgb(p[2])


def atlas(blocks):
    """One 16x16 tile per block in a square grid, a light and a dark tone in a fixed dither so faces read."""
    n = max(1, len(blocks))
    cols = 1
    while cols * cols < n: cols += 1
    rows_n = -(-n // cols)
    w, h = cols * TILE, rows_n * TILE
    px = [[(0, 0, 0, 0)] * w for _ in range(h)]
    where = {}
    for i, b in enumerate(blocks):
        tx, ty = i % cols * TILE, i // cols * TILE
        a, d = _colours(b)
        for y in range(TILE):
            for x in range(TILE):
                dark = ((x * 7 + y * 13 + (x // 4) * 5 + i) % 11) < 3
                px[ty + y][tx + x] = d + (255,) if dark else a + (255,)
        where[b] = (tx, ty)
    data = _png(w, h, [bytes(v for p in row for v in p) for row in px])
    return w, h, where, "data:image/png;base64," + base64.b64encode(data).decode()


def to_bb(id, m, rig_anims):
    blocks = list(dict.fromkeys(c["k"] for c in m["cubes"]))
    w, h, where, src = atlas(blocks)
    elements, by_bone = [], {}
    for i, c in enumerate(m["cubes"]):
        name = c["k"] + ("|" + c["g"] if c.get("g") else "") + ("|lit" if c.get("l") else "")
        tx, ty = where[c["k"]]
        uv = [tx, ty, tx + TILE, ty + TILE]
        e = {"name": name, "box_uv": False, "rescale": False, "locked": False, "light_emission": 15 if c.get("l") else 0,
             "render_order": "default", "allow_mirror_modeling": True, "from": c["f"], "to": c["t"], "autouv": 0, "color": i % 8,
             "origin": c.get("o") or [(a + b) / 2 for a, b in zip(c["f"], c["t"])], "rotation": c.get("r", [0, 0, 0]),
             "faces": {f: {"uv": uv, "texture": 0} for f in ("north", "east", "south", "west", "up", "down")},
             "type": "cube", "uuid": _uuid(id, "cube", i)}
        elements.append(e)
        by_bone.setdefault(c["b"], []).append(e["uuid"])
    groups = {}
    for b in m["bones"]:
        groups[b["name"]] = {"name": b["name"], "origin": b["pivot"], "rotation": b.get("rest", [0, 0, 0]), "color": 0,
                             "uuid": _uuid(id, "bone", b["name"]), "export": True, "mirror_uv": False, "isOpen": False,
                             "locked": False, "visibility": True, "autouv": 0, "children": list(by_bone.get(b["name"], []))}
    top = []
    for b in m["bones"]:
        g = groups[b["name"]]
        if b.get("parent") and b["parent"] in groups: groups[b["parent"]]["children"].append(g)
        else: top.append(g)
    anims = dict(rig_anims)
    anims.update(m.get("anims", {}))
    out_anims = []
    for name, a in anims.items():
        animators = {}
        for bone, ch in a.get("bones", {}).items():
            if bone not in groups: continue
            keys = []
            for chan, bb_chan, sign in (("rot", "rotation", (-1, -1, 1)), ("pos", "position", (-1, 1, 1)), ("scl", "scale", (1, 1, 1))):
                for k, (t, v) in enumerate(ch.get(chan) or []):
                    keys.append({"channel": bb_chan, "data_points": [{"x": v[0] * sign[0], "y": v[1] * sign[1], "z": v[2] * sign[2]}],
                                 "uuid": _uuid(id, name, bone, chan, k), "time": t, "color": -1, "interpolation": "linear"})
            if keys: animators[groups[bone]["uuid"]] = {"name": bone, "type": "bone", "keyframes": keys}
        out_anims.append({"uuid": _uuid(id, "anim", name), "name": name, "loop": "loop" if a.get("loop") else "once", "override": False,
                          "length": a.get("length", 1), "snapping": 20, "selected": False, "anim_time_update": "", "blend_weight": "",
                          "start_delay": "", "loop_delay": "", "animators": animators,
                          "markers": [{"color": 0, "time": a["hit"]}] if a.get("hit", -1) >= 0 else []})
    return {
        "meta": {"format_version": "4.10", "model_format": "free", "box_uv": False},
        "name": id, "model_identifier": id, "visible_box": [1, 1, 0], "variable_placeholders": "", "variable_placeholder_buttons": [],
        "timeline_setups": [], "unhandled_root_fields": {}, "resolution": {"width": w, "height": h},
        "elements": elements, "outliner": top,
        "textures": [{"path": "", "name": "blocks.png", "folder": "", "namespace": "", "id": "0", "width": w, "height": h,
                      "uv_width": w, "uv_height": h, "particle": False, "use_as_default": True, "layers_enabled": False,
                      "sync_to_project": "", "render_mode": "default", "render_sides": "auto", "frame_time": 1, "frame_order_type": "loop",
                      "frame_order": "", "frame_interpolate": False, "visible": True, "internal": True, "saved": False,
                      "uuid": _uuid(id, "texture"), "source": src}],
        "animations": out_anims,
    }


def main(ids):
    data = json.load(open(os.path.join(ROOT, "src", "main", "resources", "models.json")))
    dest = os.path.join(ROOT, "blockbench")
    os.makedirs(dest, exist_ok=True)
    for id in ids or sorted(data["models"]):
        m = data["models"][id]
        with open(os.path.join(dest, id + ".bbmodel"), "w") as f:
            json.dump(to_bb(id, m, data["rigs"].get(m["rig"], {})), f, separators=(",", ":"))
    print(f"wrote {len(ids or data['models'])} Blockbench models to {os.path.relpath(dest)}")


if __name__ == "__main__":
    main(sys.argv[1:])
