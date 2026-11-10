"""Turn a mob texture (box UV, the way Java entity models are laid out) into painted skinboxes.

Used for bosses that copy a real mob's look, and for bosses drawn as small texture sheets."""
import os
from PIL import Image
from skin import skinbox

HERE = os.path.dirname(__file__)
COLOURS = {}


def _load_colours():
    from palette import P
    for k, v in P.items():
        if True:
            h = v[1].lstrip("#")
            COLOURS[k] = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def nearest(rgb, allowed):
    if not COLOURS: _load_colours()
    best, bd = None, 1e18
    r, g, b = rgb
    for k in allowed:
        cr, cg, cb = COLOURS[k]
        rm = (r + cr) / 2
        d = (2 + rm / 256) * (r - cr) ** 2 + 4 * (g - cg) ** 2 + (2 + (255 - rm) / 256) * (b - cb) ** 2
        if d < bd: best, bd = k, d
    return best


def region(img, u, v, w, h, step=1):
    """Pixels of one face as a grid of rgb or None (transparent), averaged over step x step cells."""
    out = []
    for y in range(0, h, step):
        row = []
        for x in range(0, w, step):
            acc, n, a = [0, 0, 0], 0, 0
            for yy in range(y, min(h, y + step)):
                for xx in range(x, min(w, x + step)):
                    p = img.getpixel((u + xx, v + yy))
                    if p[3] > 100:
                        acc[0] += p[0]; acc[1] += p[1]; acc[2] += p[2]; n += 1
                    a += 1
            row.append(tuple(c // n for c in acc) if n * 2 >= a else None)
        out.append(row)
    return out


def smooth(grid, passes=1, keep=()):
    """Majority filter: a pixel takes the most common key of its 3 x 3 block when it is alone."""
    h, w = len(grid), len(grid[0]) if grid else 0
    for _ in range(passes):
        new = [r[:] for r in grid]
        for y in range(h):
            for x in range(w):
                me = grid[y][x]
                if me is None or me in keep: continue
                cnt = {}
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if (dx or dy) and 0 <= y + dy < h and 0 <= x + dx < w and grid[y + dy][x + dx] is not None:
                            k = grid[y + dy][x + dx]
                            cnt[k] = cnt.get(k, 0) + 1
                if cnt.get(me, 0) <= 1 and cnt:
                    best = max(cnt, key=cnt.get)
                    if cnt[best] >= 4: new[y][x] = best
        grid = new
    return grid


def downsample(g, st):
    """Most common key in each st x st cell, kept at full size (so the picture still fits the face)."""
    h, w = len(g), len(g[0])
    out = [r[:] for r in g]
    for y in range(0, h, st):
        for x in range(0, w, st):
            cnt = {}
            for yy in range(y, min(h, y + st)):
                for xx in range(x, min(w, x + st)):
                    cnt[g[yy][xx]] = cnt.get(g[yy][xx], 0) + 1
            k = max(cnt, key=cnt.get)
            for yy in range(y, min(h, y + st)):
                for xx in range(x, min(w, x + st)):
                    out[yy][xx] = k
    return out


def despeck(g, n, lit):
    """Pixels in a same-colour patch of n pixels or fewer take their neighbours' colour (lit ones stay)."""
    h, w = len(g), len(g[0])
    seen = [[False] * w for _ in range(h)]
    out = [r[:] for r in g]
    for y in range(h):
        for x in range(w):
            if seen[y][x] or g[y][x] is None: continue
            k = g[y][x]
            stack, patch = [(x, y)], []
            seen[y][x] = True
            while stack:
                a, b = stack.pop(); patch.append((a, b))
                for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c, d = a + da, b + db
                    if 0 <= c < w and 0 <= d < h and not seen[d][c] and g[d][c] == k:
                        seen[d][c] = True; stack.append((c, d))
            if len(patch) <= n and k not in lit:
                cnt = {}
                for a, b in patch:
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        c, d = a + da, b + db
                        if 0 <= c < w and 0 <= d < h and g[d][c] not in (None, k):
                            cnt[g[d][c]] = cnt.get(g[d][c], 0) + 1
                if cnt:
                    nk = max(cnt, key=cnt.get)
                    for a, b in patch: out[b][a] = nk
    return out


def box_faces(img, u, v, w, h, d, mirror=False):
    """The six face regions of a box UV at (u, v) for a box w wide, h tall, d deep."""
    F = {
        "top": (u + d, v, w, d),
        "bottom": (u + d + w, v, w, d),
        "right": (u, v + d, d, h),
        "front": (u + d, v + d, w, h),
        "left": (u + d + w, v + d, d, h),
        "back": (u + d + w + d, v + d, w, h),
    }
    if mirror:
        F["left"], F["right"] = F["right"], F["left"]
    return F


def paintbox(m, bone, img, uv, lo, size, allowed, lit=(), mirror=False, step=1, passes=1, skip=(), base=None, shell=True, plane=None, scale=1.0, merge=None, coarse=(), speck=0, rot=None, origin=None, keep=(), extent=None):
    """A box painted from the texture. lo is its low corner in model pixels (our axes), size its (w, h, d)
    in texture pixels; scale stretches the box (not the picture). allowed are the blocks it may use, lit
    the ones that glow. plane='front' paints only that face as a flat sheet (tendrils, ribcage)."""
    w, h, d = size
    u, v = uv
    faces = box_faces(img, u, v, w, h, d, mirror)
    grids, tally = {}, {}
    for face, (fu, fv, fw, fh) in faces.items():
        if face in skip or fw == 0 or fh == 0: continue
        if plane and face != plane: continue
        st = step * (2 if face in coarse else 1)
        g = region(img, fu, fv, fw, fh, 1)
        g = [[nearest(p, allowed) if p else None for p in row] for row in g]
        if merge:
            g = [[merge.get(k, k) for k in row] for row in g]
        g = smooth(g, passes, set(lit) | set(keep))
        if st > 1:
            g = downsample(g, st)
        if speck:
            g = despeck(g, speck, set(lit) | set(keep))
        if mirror:
            g = [r[::-1] for r in g]
        grids[face] = g
        for row in g:
            for k in row:
                if k: tally[k] = tally.get(k, 0) + 1
    if not tally: return
    main = base or max(tally, key=tally.get)
    chars, keys = {}, {}
    def ch(k):
        if k is None: return "."
        if k == main and shell: return "."
        if k not in chars:
            c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"[len(chars)]
            chars[k] = c
            keys[c] = (k, k in lit)
        return chars[k]
    faces_rows = {}
    for face, g in grids.items():
        rows = ["".join(ch(k) for k in row) for row in g]
        if plane:
            face = "plane" if plane in ("front", "back") else ("planey" if plane in ("top", "bottom") else "planex")
        faces_rows[face] = rows
    hi = [lo[0] + w * scale, lo[1] + h * scale, lo[2] + d * scale] if not extent else [lo[i] + extent[i] for i in range(3)]
    if plane:
        # a flat sheet: give it a little thickness
        if plane in ("front", "back"):
            hi[2] = lo[2] + 0.5
        elif plane in ("top", "bottom"):
            hi[1] = lo[1] + 0.5
        else:
            hi[0] = lo[0] + 0.5
    skinbox(m, bone, lo, hi, main, faces_rows, keys, rot=rot, origin=origin, light=main in lit, shell=shell)
    return main


def load(name):
    return Image.open(os.path.join(HERE, "tex", name)).convert("RGBA")


def rgb(block):
    if not COLOURS: _load_colours()
    return COLOURS[block] + (255,)


class Sheet:
    """A texture drawn in code, laid out like a Blockbench box-UV sheet. Colours are block names, so
    every painted pixel maps back to exactly that block."""

    def __init__(self, w=256, h=256):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.x, self.y, self.row = 0, 0, 0
        self.used = set()
        self.sizes = {}

    def box(self, w, h, d, block, shade=None, edge=None, top=None, bottom=None):
        """Allocate a box (w, h, d) and fill it with block. shade darkens the bottom rows of the sides;
        edge outlines every face; top/bottom colour those faces."""
        W, H = 2 * (w + d), h + d
        if self.x + W > self.img.width:
            self.x, self.y, self.row = 0, self.y + self.row, 0
        uv = (self.x, self.y)
        assert self.y + H <= self.img.height, "sheet full"
        self.x += W
        self.row = max(self.row, H)
        self.sizes[uv] = (w, h, d)
        for face, (fu, fv, fw, fh) in box_faces(self.img, uv[0], uv[1], w, h, d).items():
            k = top if face == "top" and top else bottom if face == "bottom" and bottom else block
            self.fill(fu, fv, fw, fh, k)
            if edge:
                for i in range(fw):
                    self.put(fu + i, fv, edge); self.put(fu + i, fv + fh - 1, edge)
                for j in range(fh):
                    self.put(fu, fv + j, edge); self.put(fu + fw - 1, fv + j, edge)
            if shade and face in ("front", "back", "left", "right"):
                for i in range(fw):
                    self.put(fu + i, fv + fh - 1, shade)
        return uv

    def put(self, x, y, block):
        if block is None: return
        self.used.add(block)
        self.img.putpixel((x, y), rgb(block))

    def fill(self, x, y, w, h, block):
        for j in range(h):
            for i in range(w):
                self.put(x + i, y + j, block)

    def face(self, uv, face):
        w, h, d = self.sizes[uv]
        return box_faces(self.img, uv[0], uv[1], w, h, d)[face]

    def draw(self, uv, face, x, y, rows, keys):
        """Stamp rows (one char per pixel, '.' or ' ' skip) on a face at (x, y) from its top-left.
        Negative x / y count from the right / bottom."""
        fu, fv, fw, fh = self.face(uv, face)
        if x < 0: x = fw + x - max(len(r) for r in rows) + 1
        if y < 0: y = fh + y - len(rows) + 1
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c in ". " or not (0 <= x + i < fw and 0 <= y + j < fh): continue
                self.put(fu + x + i, fv + y + j, keys[c])

    def rect(self, uv, face, x, y, w, h, block):
        fu, fv, fw, fh = self.face(uv, face)
        for j in range(h):
            for i in range(w):
                if 0 <= x + i < fw and 0 <= y + j < fh:
                    self.put(fu + x + i, fv + y + j, block)

    def all(self, uv, fn, faces=("front", "back", "left", "right", "top", "bottom")):
        for f in faces:
            fu, fv, fw, fh = self.face(uv, f)
            fn(f, fu, fv, fw, fh)


def moss(img, rects, seed, cover=0.35, blocks=("moss_block", "green_terracotta", "lime_terracotta"), flowers=("yellow_concrete",), flower_rate=0.02, top_bias=0.0, cell=2):
    """Grow patches of moss over texture regions (fu, fv, fw, fh), thicker near the top of each when
    top_bias > 0, with a few flowers. The blobs are chunky (2 x 2 cells) so they stay cheap in blocks."""
    import random
    R = random.Random(seed)
    cols = [rgb(b) for b in blocks]
    for (fu, fv, fw, fh) in rects:
        cells_w, cells_h = (fw + cell - 1) // cell, (fh + cell - 1) // cell
        grid = [[0] * cells_w for _ in range(cells_h)]
        n = max(1, int(cells_w * cells_h * cover / 6))
        for _ in range(n):
            cy = int((R.random() ** (1 + top_bias * 2)) * cells_h)
            cx = R.randrange(cells_w)
            for _ in range(R.randint(3, 9)):
                if 0 <= cy < cells_h and 0 <= cx < cells_w:
                    grid[cy][cx] = 1 + (R.random() < 0.3)
                d = R.choice(((1, 0), (-1, 0), (0, 1), (0, -1), (0, 1)))
                cx += d[0]; cy += d[1]
        for j in range(cells_h):
            for i in range(cells_w):
                if not grid[j][i]: continue
                c = cols[0] if grid[j][i] == 1 else cols[1 + R.randrange(len(cols) - 1)]
                fl = rgb(R.choice(flowers)) if flowers and R.random() < flower_rate else None
                for yy in range(cell):
                    for xx in range(cell):
                        x, y = fu + i * cell + xx, fv + j * cell + yy
                        if x < fu + fw and y < fv + fh and img.getpixel((x, y))[3] > 0:
                            img.putpixel((x, y), fl if fl and xx == cell // 2 and yy == cell // 2 else c)


def snap(img, allowed, rects=None):
    """Snap every opaque pixel (in rects, or the whole image) to its nearest allowed block colour, so
    later paint in other colours stays exactly where it was put."""
    rects = rects or [(0, 0, img.width, img.height)]
    cache = {}
    for (fu, fv, fw, fh) in rects:
        for y in range(fv, fv + fh):
            for x in range(fu, fu + fw):
                p = img.getpixel((x, y))
                if p[3] <= 100: continue
                k = cache.get(p[:3])
                if k is None:
                    k = cache[p[:3]] = nearest(p[:3], allowed)
                img.putpixel((x, y), rgb(k))


FLAT = [k + s for k in ("white", "light_gray", "gray", "black", "brown", "red", "orange", "yellow", "lime", "green", "cyan",
                        "light_blue", "blue", "purple", "magenta", "pink") for s in ("_concrete", "_terracotta", "_wool")] + [
    "terracotta", "smooth_stone", "quartz_block", "calcite", "mushroom_stem", "snow_block", "smooth_sandstone",
    "iron_block", "gold_block", "packed_ice", "polished_andesite", "polished_granite", "polished_deepslate",
    "polished_blackstone", "pale_oak_planks", "resin_block"]


def autopal(img, n, must=(), pool=None, rects=None):
    """Pick the n blocks (plus must) that copy the texture best: greedy, each step adds the block that
    lowers the summed colour error the most. rects limits it to some UV areas."""
    if not COLOURS: _load_colours()
    pool = [k for k in (pool or FLAT) if k in COLOURS]
    hist = {}
    px = img.load()
    areas = rects or [(0, 0, img.width, img.height)]
    for (x0, y0, w, h) in areas:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                p = px[x, y]
                if p[3] > 0: hist[p[:3]] = hist.get(p[:3], 0) + 1

    def dist(c, k):
        r, g, b = c; cr, cg, cb = COLOURS[k]; rm = (r + cr) / 2
        return (2 + rm / 256) * (r - cr) ** 2 + 4 * (g - cg) ** 2 + (2 + (255 - rm) / 256) * (b - cb) ** 2
    D = {k: {c: dist(c, k) for c in hist} for k in pool}
    chosen = list(must)
    best = {c: min((D[k][c] for k in chosen if k in D), default=1e12) for c in hist}
    while len(chosen) < n + len(must):
        top, tk = None, None
        for k in pool:
            if k in chosen: continue
            e = sum(min(best[c], D[k][c]) * w for c, w in hist.items())
            if top is None or e < top: top, tk = e, k
        chosen.append(tk)
        for c in hist: best[c] = min(best[c], D[tk][c])
    return chosen
