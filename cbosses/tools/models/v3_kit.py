"""Shared helpers for the v3 bosses: organic patches (moss, rust, frost, fungus) grown on a face as pixel
art, hanging vines, flowers, and vanilla-style mob faces. Patches are grown from seeds with a fixed
random generator, so a model looks the same every build, and they are drawn with kit.paint so equal
neighbours merge into few blocks."""
import random
from kit import paint


def patch_rows(w, h, seed, cover=0.35, top=0.7, edge=None, blobs=None):
    """A w x h grid of '.', 'A' (main) and 'B' (darker edge) cells that looks like moss or rust grown
    on a surface: clumps that start from a few seeds, denser towards the top when top > 0.5 (things grow
    down from above). edge, when given, is a set of sides ('t', 'b', 'l', 'r') the patch hugs."""
    r = random.Random(seed)
    g = [[0] * w for _ in range(h)]
    n = blobs or max(2, int(w * h * cover / 14))
    for _ in range(n):
        y = int((r.random() ** (top * 2.2)) * h) if top > 0.5 else r.randrange(h)
        x = r.randrange(w)
        if edge and r.random() < 0.6:
            side = r.choice(sorted(edge))
            if side == "t": y = 0
            if side == "b": y = h - 1
            if side == "l": x = 0
            if side == "r": x = w - 1
        size = r.randint(3, 7)
        for _ in range(size * 3):
            if 0 <= x < w and 0 <= y < h: g[y][x] = 1
            d = r.randrange(4)
            x += (1, -1, 0, 0)[d]
            y += (0, 0, 1, 1 if r.random() < 0.6 else -1)[d]
            x = max(0, min(w - 1, x)); y = max(0, min(h - 1, y))
    # fill single holes and trim single specks, so the patch reads as clumps
    for _ in range(2):
        out = [row[:] for row in g]
        for y in range(h):
            for x in range(w):
                nb = sum(g[yy][xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < h and 0 <= xx < w)
                if g[y][x] == 0 and nb >= 3: out[y][x] = 1
                if g[y][x] == 1 and nb == 0: out[y][x] = 0
        g = out
    rows = []
    for y in range(h):
        s = ""
        for x in range(w):
            if not g[y][x]:
                s += "."
                continue
            nb = sum(g[yy][xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < h and 0 <= xx < w)
            s += "B" if nb <= 2 and (x + y + seed) % 2 == 0 else "A"
        rows.append(s)
    return rows


def sprinkle(rows, seed, ch="F", every=11, on="A"):
    """Put a few accent pixels (flowers, rivets, sparks) on cells of a patch."""
    r = random.Random(seed * 7 + 3)
    out = [list(s) for s in rows]
    cells = [(y, x) for y, s in enumerate(out) for x, c in enumerate(s) if c == on]
    r.shuffle(cells)
    for y, x in cells[: max(1, len(cells) // every)]:
        out[y][x] = ch
    return ["".join(s) for s in out]


def grow(m, bone, face, center, w, h, seed, key, cover=0.35, top=0.7, edge=None, px=1.0, depth=0.5, out=0.0, flowers=None, blobs=None):
    """Grow a patch on a face and paint it. key maps 'A', 'B' (and 'F' when flowers is a block)."""
    rows = patch_rows(w, h, seed, cover, top, edge, blobs)
    if flowers:
        rows = sprinkle(rows, seed, "F", 9)
        key = dict(key, F=flowers)
    paint(m, bone, face, center, rows, key, px=px, depth=depth, out=out)
    return rows


def vines(m, bone, xs, y, z, lengths, block="green_terracotta", tip="moss_block", w=0.6, face_z=True):
    """Thin vines hanging straight down from y, each ending in a small leaf."""
    for x, L in zip(xs, lengths):
        if face_z:
            m.c(bone, block, (x, y - L / 2, z), (w, L, w))
            m.c(bone, tip, (x, y - L - 0.4, z), (w * 1.8, 0.9, w * 1.4))
        else:
            m.c(bone, block, (z, y - L / 2, x), (w, L, w))
            m.c(bone, tip, (z, y - L - 0.4, x), (w * 1.4, 0.9, w * 1.8))


def flower(m, bone, at, petal="yellow_concrete", heart="orange_concrete", size=1.6, stem="green_concrete"):
    """A small flat flower facing up: four petals round a heart, on a short stem."""
    x, y, z = at
    p = size / 3
    m.c(bone, stem, (x, y + 0.5, z), (0.3, 1.0, 0.3))
    for dx, dz in ((p, 0), (-p, 0), (0, p), (0, -p)):
        m.c(bone, petal, (x + dx, y + 1.1, z + dz), (p, 0.35, p))
    m.c(bone, heart, (x, y + 1.15, z), (p, 0.4, p))
