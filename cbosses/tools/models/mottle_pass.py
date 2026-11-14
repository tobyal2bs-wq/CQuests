"""Skin pass for the hand-built models: the reference pictures are pixel skins with two or three tones of
the same colour in chunky patches, while a hand-built box is one flat block. This lays flush patches of a
darker and a lighter block of the same hue over the big front and side faces, the way a Blockbench skin is
painted, so a body reads as fur, bark or cloth and not as plastic.

- Patches are 2x2 (3x3 on big faces) texture pixels, merged with their neighbours into bigger plates.
- They never cover another piece (eyes, mouths, belts, buttons) and never sit on a face that is hidden
  inside another box, so features stay crisp and nothing floats.
- Back faces stay plain (nobody looks there and it halves the cost) and every model stays at 300 blocks
  or less; every patch is tagged "trim" so low detail drops it first.
- Seeds come from zlib.crc32, never hash(), so block counts never drift between builds."""
import colorsys
import random
import zlib
import palette

COLOURS = ["white", "light_gray", "gray", "black", "brown", "red", "orange", "yellow", "lime", "green", "cyan",
           "light_blue", "blue", "purple", "magenta", "pink"]
CANDIDATES = [f"{c}_{k}" for c in COLOURS for k in ("concrete", "terracotta", "wool")] + [
    "terracotta", "mud", "packed_mud", "dirt", "coarse_dirt", "granite", "tuff", "andesite", "stone", "moss_block",
    "stripped_oak_log", "stripped_spruce_log", "stripped_dark_oak_log", "stripped_birch_log", "smooth_sandstone",
    "mushroom_stem", "bone_block", "dripstone_block", "nether_wart_block", "warped_wart_block", "deepslate"]
CANDIDATES = [c for c in CANDIDATES if c in palette.P]
SKIP_BLOCK = ("black_concrete", "glass", "lantern", "glowstone", "shroomlight", "sea_lantern", "froglight", "torch")
DEPTH = 0.12      # px a patch stands proud of its face
BUDGET = 300


def _hsl(block):
    hexc = palette.P[block][1].lstrip("#")
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


# hand-picked (dark, light) pairs for the common blocks; anything else is matched by colour
HAND = {
    "red_concrete": ("red_terracotta", "red_wool"), "red_wool": ("red_terracotta", "red_concrete"),
    "red_terracotta": ("brown_terracotta", "red_concrete"),
    "orange_concrete": ("orange_terracotta", "orange_wool"), "orange_terracotta": ("brown_terracotta", "orange_concrete"),
    "yellow_concrete": ("yellow_terracotta", "yellow_wool"), "yellow_terracotta": ("orange_terracotta", "yellow_concrete"),
    "lime_concrete": ("lime_terracotta", "lime_wool"), "lime_terracotta": ("green_terracotta", "lime_concrete"),
    "green_concrete": ("green_terracotta", "lime_terracotta"), "green_terracotta": ("brown_terracotta", "lime_terracotta"),
    "green_wool": ("green_terracotta", "lime_terracotta"), "moss_block": ("green_concrete", "lime_terracotta"),
    "cyan_concrete": ("cyan_terracotta", "cyan_wool"), "cyan_terracotta": ("gray_concrete", "cyan_concrete"),
    "light_blue_concrete": ("light_blue_terracotta", "light_blue_wool"), "blue_concrete": ("blue_terracotta", "blue_wool"),
    "blue_terracotta": ("black_terracotta", "blue_concrete"),
    "purple_concrete": ("purple_terracotta", "magenta_concrete"), "purple_terracotta": ("black_terracotta", "purple_concrete"),
    "magenta_concrete": ("purple_concrete", "magenta_wool"), "magenta_terracotta": ("purple_terracotta", "magenta_concrete"),
    "pink_concrete": ("pink_terracotta", "pink_wool"), "pink_terracotta": ("red_terracotta", "pink_concrete"),
    "brown_concrete": ("brown_terracotta", "brown_wool"), "brown_wool": ("brown_terracotta", "brown_concrete"),
    "brown_terracotta": ("black_terracotta", "terracotta"), "terracotta": ("brown_terracotta", "orange_terracotta"),
    "white_concrete": ("white_terracotta", "white_wool"), "white_wool": ("light_gray_concrete", "white_concrete"),
    "white_terracotta": ("light_gray_terracotta", "smooth_sandstone"), "smooth_sandstone": ("white_terracotta", "birch_planks"),
    "light_gray_concrete": ("light_gray_terracotta", "light_gray_wool"), "light_gray_wool": ("andesite", "white_concrete"),
    "gray_concrete": ("gray_terracotta", "gray_wool"), "gray_wool": ("gray_terracotta", "light_gray_concrete"),
    "stripped_oak_log": ("stripped_spruce_log", "birch_planks"), "spruce_planks": ("dark_oak_planks", "stripped_spruce_log"),
    "oak_planks": ("spruce_planks", "birch_planks"), "mud": ("packed_mud", "dirt"), "dirt": ("coarse_dirt", "packed_mud"),
    "mushroom_stem": ("white_terracotta", "white_concrete"), "bone_block": ("smooth_sandstone", "white_concrete"),
}
_TONES = {}


def tones(block):
    """The nearest darker and lighter block of the same hue, or () when nothing close enough exists."""
    if block in _TONES: return _TONES[block]
    out = ()
    if block in HAND:
        out = tuple(b for b in HAND[block] if b in palette.P)
    elif block in palette.P and not any(k in block for k in SKIP_BLOCK):
        h, s, l = _hsl(block)
        best = {}
        for c in CANDIDATES:
            if c == block: continue
            ch, cs, cl = _hsl(c)
            dh = min(abs(ch - h), 1 - abs(ch - h))
            grey = s < 0.12 and cs < 0.14
            if not grey and (s < 0.12) != (cs < 0.14): continue
            if not grey and dh > 0.06: continue
            dl = cl - l
            for name, lo, hi in (("dark", -0.26, -0.06), ("light", 0.05, 0.22)):
                if lo <= dl <= hi:
                    score = dh * 4 + abs(cs - s) + abs(abs(dl) - 0.12)
                    if name not in best or score < best[name][0]: best[name] = (score, c)
        if "dark" in best:
            out = (best["dark"][1],) + ((best["light"][1],) if "light" in best else ())
    _TONES[block] = out
    return out


def _overlap(a, b, eps=0.02):
    return all(a[0][i] < b[1][i] - eps and b[0][i] < a[1][i] - eps for i in range(3))


def _faces(c):
    """(axis, sign, u axis, v axis) for front (+z), left (+x) and right (-x)."""
    return ((2, 1, 0, 1), (0, 1, 2, 1), (0, -1, 2, 1))


def skin(m, rate=None, budget=BUDGET, skip_bones=()):
    cubes = list(m.cubes)
    if rate is None: rate = 0.4 if len(cubes) < 90 else 0.3
    boxes = [(c["f"], c["t"]) for c in cubes]
    free = budget - len(cubes)
    if free <= 8: return 0
    plates = []
    for i, c in enumerate(cubes):
        if c.get("r") or c.get("l") or str(c.get("g", "")).startswith(("face:", "eye")) or c["b"] in skip_bones: continue
        tk = tones(c["k"])
        if not tk: continue
        f, t = c["f"], c["t"]
        size = [t[j] - f[j] for j in range(3)]
        for ax, sg, ua, va in _faces(c):
            fu, fv = size[ua], size[va]
            if fu < 3 or fv < 3 or size[ax] < 1.2: continue
            cell = 3 if max(fu, fv) >= 14 else 2 if max(fu, fv) >= 8 else 1.5
            nu, nv = int(fu // cell), int(fv // cell)
            if nu < 2 or nv < 2: continue
            ou, ov = f[ua] + (fu - nu * cell) / 2, f[va] + (fv - nv * cell) / 2
            plane = t[ax] if sg > 0 else f[ax]
            rnd = random.Random(zlib.crc32(repr((m.id, i, ax, sg, c["k"])).encode()))

            def cell_box(u0, u1, v0, v1):
                pf, pt = [0, 0, 0], [0, 0, 0]
                pf[ua], pt[ua] = ou + u0 * cell, ou + (u1 + 1) * cell
                pf[va], pt[va] = ov + v0 * cell, ov + (v1 + 1) * cell
                pf[ax], pt[ax] = (plane, plane + DEPTH) if sg > 0 else (plane - DEPTH, plane)
                return pf, pt

            def blocked(pf, pt):
                # anything touching the patch (a feature on the face, or a box the face is buried in) keeps it off
                lo, hi = list(pf), list(pt)
                lo[ax] = plane - (0.05 if sg > 0 else 0.6)
                hi[ax] = plane + (0.6 if sg > 0 else 0.05)
                return any(j != i and _overlap((lo, hi), boxes[j]) for j in near)

            near = [j for j in range(len(boxes)) if _overlap(([f[q] - 1 for q in range(3)], [t[q] + 1 for q in range(3)]), boxes[j], 0)]
            grid = {}
            for v in range(nv):
                for u in range(nu):
                    if rnd.random() > rate or blocked(*cell_box(u, u, v, v)): continue
                    # light patches near the top, dark ones lower down, like light from above
                    up = 1 - v / max(1, nv - 1)
                    grid[(u, v)] = tk[1] if len(tk) > 1 and rnd.random() < 0.15 + 0.55 * up else tk[0]
            # merge runs of the same tone along u (at most 3 cells), then identical runs along v (at most 2 rows)
            runs = []
            for v in range(nv):
                u = 0
                while u < nu:
                    k = grid.get((u, v))
                    if not k: u += 1; continue
                    e = u
                    while e + 1 < nu and grid.get((e + 1, v)) == k and e - u < 2: e += 1
                    runs.append([u, e, v, v, k]); u = e + 1
            merged = []
            for r in runs:
                for q in merged:
                    if q[0] == r[0] and q[1] == r[1] and q[3] == r[2] - 1 and q[4] == r[4] and q[3] - q[2] < 1:
                        q[3] = r[2]; break
                else: merged.append(r)
            for u0, u1, v0, v1, k in merged:
                pf, pt = cell_box(u0, u1, v0, v1)
                plates.append({"b": c["b"], "k": k, "f": [round(x, 3) for x in pf], "t": [round(x, 3) for x in pt], "g": "trim"})
    if len(plates) > free:
        rnd = random.Random(zlib.crc32(m.id.encode()))
        rnd.shuffle(plates)
        plates = plates[:free]
    m.cubes.extend(plates)
    return len(plates)
