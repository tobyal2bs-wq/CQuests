"""Hand-modelling kit for the bosses. Every helper places blocks with a purpose: pixel art painted onto a
face (eyes, brows, teeth, emblems, glowing cracks), layered plates, fur tufts, torn hems, studded bands and
detailed weapons. Units are model pixels (16 = one block at scale 1). The model faces +z, its left is +x.

paint() is the workhorse. It takes rows of characters like a sprite, merges equal neighbours into as few
rectangles as possible and lays them as thin plates on one face of a part, so a face can carry real detail
without hundreds of blocks."""
from build import Model


def rects(rows):
    """Greedy merge of a character grid into rectangles: [(char, col, row, w, h)]."""
    H = len(rows)
    W = max(len(r) for r in rows)
    g = [list(r.ljust(W, ".")) for r in rows]
    used = [[False] * W for _ in range(H)]
    out = []
    for y in range(H):
        for x in range(W):
            ch = g[y][x]
            if ch in ". " or used[y][x]:
                continue
            w = 1
            while x + w < W and g[y][x + w] == ch and not used[y][x + w]:
                w += 1
            h = 1
            while y + h < H and all(g[y + h][x + k] == ch and not used[y + h][x + k] for k in range(w)):
                h += 1
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    used[yy][xx] = True
            out.append((ch, x, y, w, h))
    return out


def paint(m, bone, face, center, rows, key, px=1.0, depth=0.3, out=0.0):
    """Paint rows onto a face of a part.

    face    "front" (+z), "back" (-z), "left" (+x), "right" (-x), "top" (+y), "bottom" (-y)
    center  the middle of the picture, lying on the face's surface
    rows    strings, top row first, read as you look at that face
    key     char -> block, or char -> (block, depth, light)
    out     how far the plates stand out from the surface (negative sinks them in)"""
    H = len(rows)
    W = max(len(r) for r in rows)
    cx, cy, cz = center
    for ch, x, y, w, h in rects(rows):
        k = key[ch]
        blk, d, light = (k, depth, False) if isinstance(k, str) else (k[0], k[1] if len(k) > 1 else depth, k[2] if len(k) > 2 else False)
        u = (x + w / 2 - W / 2) * px      # across, left to right as seen
        v = (H / 2 - y - h / 2) * px      # up
        sw, sh = w * px, h * px
        o = out + d / 2
        if face == "front":
            m.c(bone, blk, (cx + u, cy + v, cz + o), (sw, sh, d), light=light)
        elif face == "back":
            m.c(bone, blk, (cx - u, cy + v, cz - o), (sw, sh, d), light=light)
        elif face == "left":
            m.c(bone, blk, (cx + o, cy + v, cz - u), (d, sh, sw), light=light)
        elif face == "right":
            m.c(bone, blk, (cx - o, cy + v, cz + u), (d, sh, sw), light=light)
        elif face == "top":
            m.c(bone, blk, (cx + u, cy + o, cz - v), (sw, d, sh), light=light)
        elif face == "bottom":
            m.c(bone, blk, (cx + u, cy - o, cz + v), (sw, d, sh), light=light)
        else:
            raise ValueError(face)


def mirror_rows(rows):
    """Rows for the other side of a symmetric part."""
    return [r[::-1] for r in rows]


def plate(m, bone, block, center, size, lip=None, lip_block=None, light=False):
    """A plate with a raised rim on its outer edge: shoulder guards, chest plates, greaves."""
    m.c(bone, block, center, size, light=light)
    if lip:
        x, y, z = center
        w, h, d = size
        m.c(bone, lip_block or block, (x, y - h / 2 + lip / 2, z), (w + 0.4, lip, d + 0.4))


def band(m, bone, block, center, size, studs=0, stud_block="iron_block", face="front", stud=0.9):
    """A strap or band around a part, with evenly spaced studs on its front."""
    m.c(bone, block, center, size)
    if studs:
        x, y, z = center
        w, h, d = size
        for i in range(studs):
            t = (i + 0.5) / studs - 0.5
            if face == "front":
                m.c(bone, stud_block, (x + t * (w - 1.5), y, z + d / 2 + 0.15), (stud, stud, 0.4))
            else:
                m.c(bone, stud_block, (x + d / 2 + 0.15, y, z + t * (w - 1.5)), (0.4, stud, stud))


def hem(m, bone, block, x0, x1, y, z, depth, teeth, long=2.6, short=1.0, seed=0, face_z=True, alt=None):
    """A torn or toothed bottom edge for a kilt, cloak or fur: teeth of two lengths in a fixed rhythm."""
    pattern = [long, short * 1.4, long * 0.75, short, long * 0.9, short * 1.2]
    w = (x1 - x0) / teeth
    for i in range(teeth):
        L = pattern[(i + seed) % len(pattern)]
        blk = alt if alt and (i + seed) % 3 == 1 else block
        cx = x0 + w * (i + 0.5)
        if face_z:
            m.c(bone, blk, (cx, y - L / 2, z), (w * 0.86, L, depth))
        else:
            m.c(bone, blk, (z, y - L / 2, cx), (depth, L, w * 0.86))


def tufts(m, bone, block, points, size=2.2, alt=None, tilt=18):
    """Fur or feather tufts: small tilted blocks at the given points, alternating tilt so they read as fur."""
    for i, p in enumerate(points):
        s = size * (1.0 if i % 2 == 0 else 0.8)
        r = tilt if i % 2 == 0 else -tilt
        m.c(bone, alt if alt and i % 3 == 2 else block, p, (s, s * 1.15, s), (r * 0.5, 0, r))


def spikes(m, bone, block, base_points, direction_rot, length=3.0, size=1.2):
    """Short tapered spikes (two blocks each) pointing along a rotation."""
    from models import dirof
    for p in base_points:
        dx, dy, dz = dirof(direction_rot)
        a = (p[0] + dx * length * 0.3, p[1] + dy * length * 0.3, p[2] + dz * length * 0.3)
        b = (p[0] + dx * length * 0.75, p[1] + dy * length * 0.75, p[2] + dz * length * 0.75)
        m.c(bone, block, a, (size, length * 0.6, size), direction_rot, a)
        m.c(bone, block, b, (size * 0.55, length * 0.45, size * 0.55), direction_rot, b)


def crack(m, bone, face, center, path, block="orange_concrete", width=0.8, depth=0.25, out=0.0):
    """A glowing crack drawn on a face as connected straight runs. path: list of (u, v) points on the face,
    relative to center, in pixels. Horizontal and vertical runs only, like the cracks in a stone golem."""
    cx, cy, cz = center
    for (u0, v0), (u1, v1) in zip(path, path[1:]):
        if u0 == u1:
            u, v, sw, sh = u0, (v0 + v1) / 2, width, abs(v1 - v0) + width
        else:
            u, v, sw, sh = (u0 + u1) / 2, v0, abs(u1 - u0) + width, width
        o = out + depth / 2
        if face == "front":
            m.c(bone, block, (cx + u, cy + v, cz + o), (sw, sh, depth), light=True)
        elif face == "back":
            m.c(bone, block, (cx - u, cy + v, cz - o), (sw, sh, depth), light=True)
        elif face == "left":
            m.c(bone, block, (cx + o, cy + v, cz - u), (depth, sh, sw), light=True)
        elif face == "right":
            m.c(bone, block, (cx - o, cy + v, cz + u), (depth, sh, sw), light=True)
        elif face == "top":
            m.c(bone, block, (cx + u, cy + o, cz - v), (sw, depth, sh), light=True)


def stack(m, bone, block, x, y0, z, layers, light=False):
    """Stacked slabs [(w, h, d)] from y0 up: tapering bodies, crowns, chimneys."""
    y = y0
    for w, h, d in layers:
        m.c(bone, block, (x, y + h / 2, z), (w, h, d), light=light)
        y += h
    return y


def bevel(m, bone, block, center, size, e=1.0, rot=None, origin=None, light=False):
    """A box with stepped (chamfered) edges, three blocks: reads rounded instead of boxy."""
    x, y, z = center
    w, h, d = size
    e = min(e, w / 3, h / 3, d / 3)
    m.c(bone, block, center, (w, h - 2 * e, d - 2 * e), rot, origin, light)
    m.c(bone, block, center, (w - 2 * e, h, d - 2 * e), rot, origin, light)
    m.c(bone, block, center, (w - 2 * e, h - 2 * e, d), rot, origin, light)
