"""Painted boxes: the Blockbench way of building a mob, done with blocks.

A boss is a handful of big boxes, and every face of a box carries a little pixel-art picture: shading
along the edges, plates, eyes, belts, cracks. skinbox() fills the box with its main block, then lays
each picture over the faces as thin plates, merging runs of the same colour into one plate so a whole
painted face costs only a few cubes.

Pictures are lists of strings, one character per pixel, row 0 at the top. '.' (or the base key) is the
box's own block. Side pictures are seen from outside the box: column 0 is on the viewer's left. The top
picture is seen from above with the front at the bottom row; the bottom picture is seen from below with
the front at the top row.

Pixel size: a picture is stretched over its face, so a 6 x 4 picture on a 12 x 8 face makes 2 x 2 pixels.
"""

FACES = ("front", "back", "left", "right", "top", "bottom")


def _rects(grid, base):
    """Greedy merge: each non-base character into the fewest rectangles (row-major, widest first)."""
    h = len(grid)
    w = max(len(r) for r in grid) if h else 0
    g = [list(r.ljust(w, ".")) for r in grid]
    done = [[False] * w for _ in range(h)]
    out = []
    for y in range(h):
        for x in range(w):
            k = g[y][x]
            if done[y][x] or k in (".", base, " "):
                continue
            x2 = x
            while x2 + 1 < w and g[y][x2 + 1] == k and not done[y][x2 + 1]:
                x2 += 1
            y2 = y
            while y2 + 1 < h and all(g[y2 + 1][i] == k and not done[y2 + 1][i] for i in range(x, x2 + 1)):
                y2 += 1
            for yy in range(y, y2 + 1):
                for xx in range(x, x2 + 1):
                    done[yy][xx] = True
            out.append((k, x, y, x2 + 1, y2 + 1, w, h))
    return out


def skinbox(m, bone, f, t, block, faces=None, keys=None, rot=None, origin=None, light=False, depth=0.1, shell=True):
    """A box from f to t in block, with pictures on its faces.

    faces: {face: rows}; keys: {char: block or (block, lit)}. depth is how far the plates stand out.
    shell=False draws only the pictures (no filled box), for flat things like wings, fins and capes."""
    lo = [min(a, b) for a, b in zip(f, t)]
    hi = [max(a, b) for a, b in zip(f, t)]
    org = origin or [(a + b) / 2 for a, b in zip(lo, hi)]
    if shell:
        m.box(bone, block, lo, hi, rot, org, light)
    keys = keys or {}
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    inset = 0.03
    for face, rows in (faces or {}).items():
        for k, a, b, a2, b2, w, h in _rects(rows, None):
            kb = keys.get(k, k)
            lit = False
            if isinstance(kb, tuple):
                kb, lit = kb[0], kb[1]
            if kb == block and shell:
                continue
            # u: 0..1 across the picture (left to right as seen), v: 0..1 down the picture
            u0, u1, v0, v1 = a / w, a2 / w, b / h, b2 / h
            if face == "front":    # +z, viewer's left is -x
                p, q = (x0 + (x1 - x0) * u0, y1 - (y1 - y0) * v1, z1 - inset), (x0 + (x1 - x0) * u1, y1 - (y1 - y0) * v0, z1 + depth)
            elif face == "back":   # -z, viewer's left is +x
                p, q = (x1 - (x1 - x0) * u1, y1 - (y1 - y0) * v1, z0 - depth), (x1 - (x1 - x0) * u0, y1 - (y1 - y0) * v0, z0 + inset)
            elif face == "left":   # +x, viewer's left is +z (front)
                p, q = (x1 - inset, y1 - (y1 - y0) * v1, z1 - (z1 - z0) * u1), (x1 + depth, y1 - (y1 - y0) * v0, z1 - (z1 - z0) * u0)
            elif face == "right":  # -x, viewer's left is -z (back)
                p, q = (x0 - depth, y1 - (y1 - y0) * v1, z0 + (z1 - z0) * u0), (x0 + inset, y1 - (y1 - y0) * v0, z0 + (z1 - z0) * u1)
            elif face == "top":    # from above, front at the bottom row, viewer's left is -x
                p, q = (x0 + (x1 - x0) * u0, y1 - inset, z0 + (z1 - z0) * v0), (x0 + (x1 - x0) * u1, y1 + depth, z0 + (z1 - z0) * v1)
            elif face == "bottom": # from below, front at the top row
                p, q = (x0 + (x1 - x0) * u0, y0 - depth, z1 - (z1 - z0) * v1), (x0 + (x1 - x0) * u1, y0 + inset, z1 - (z1 - z0) * v0)
            elif face == "plane":  # shell=False flat picture in the x-y plane at the box's middle z
                p, q = (x0 + (x1 - x0) * u0, y1 - (y1 - y0) * v1, z0), (x0 + (x1 - x0) * u1, y1 - (y1 - y0) * v0, z1)
            elif face == "planex":  # flat picture in the z-y plane (seen from +x, front on the left)
                p, q = (x0, y1 - (y1 - y0) * v1, z1 - (z1 - z0) * u1), (x1, y1 - (y1 - y0) * v0, z1 - (z1 - z0) * u0)
            elif face == "planey":  # flat picture in the x-z plane (seen from above, front at the bottom)
                p, q = (x0 + (x1 - x0) * u0, y0, z0 + (z1 - z0) * v0), (x0 + (x1 - x0) * u1, y1, z0 + (z1 - z0) * v1)
            else:
                raise ValueError(face)
            m.box(bone, kb, p, q, rot, org, lit or (light and kb == block))


def mirror(rows):
    return [r[::-1] for r in rows]


def frame(w, h, edge="d", fill=".", top=None, bottom=None, left=None, right=None):
    """A w x h picture with a one-pixel border (shading). top/bottom/left/right override that edge's key."""
    rows = []
    for y in range(h):
        r = []
        for x in range(w):
            k = fill
            if y == 0: k = top if top is not None else edge
            elif y == h - 1: k = bottom if bottom is not None else edge
            elif x == 0: k = left if left is not None else edge
            elif x == w - 1: k = right if right is not None else edge
            r.append(k)
        rows.append("".join(r))
    return rows


def over(rows, art, x, y):
    """Stamp art (rows, '.' = keep) onto rows at column x, row y."""
    out = [list(r) for r in rows]
    for j, line in enumerate(art):
        for i, ch in enumerate(line):
            if ch != " " and ch != "," and 0 <= y + j < len(out) and 0 <= x + i < len(out[y + j]):
                if ch != ".":
                    out[y + j][x + i] = ch
    return ["".join(r) for r in out]


def count(rows, base="."):
    return len(_rects(rows, base))
