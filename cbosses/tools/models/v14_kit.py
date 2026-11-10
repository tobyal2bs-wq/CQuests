"""v14 studio kit: helpers for the hand-built redesigns (v14_studio.py).

Style rules, learned from the user's target pictures (the red googly-eyed critter and the mandrake):
  * big readable shapes in one hue, two tones at most (a lit top, a shaded bottom), on blocks with grain;
  * faces are built, not painted: eyeballs stick out of the head, pupils sit on the eyeball with a white
    catch light, brows are their own slab, a mouth is a real opening with a dark inside and teeth;
  * every part that should move has its own bone; nothing floats; feet are flat.
Units are model pixels (16 = one block at scale 1). x is the model's left, y up, z its front."""
import math
import zlib
import random

# ----------------------------------------------------------------------------------------------- geometry


def B(m, bone, block, lo, size, rot=None, origin=None, light=False, g=None):
    """A box from its low corner and size."""
    f = list(lo)
    t = [lo[i] + size[i] for i in range(3)]
    m.box(bone, block, f, t, rot, origin, light)
    if g: m.cubes[-1]["g"] = g
    return m.cubes[-1]


def C(m, bone, block, center, size, rot=None, origin=None, light=False, g=None):
    """A box from its centre and size; rotations turn round the centre unless origin is given."""
    m.c(bone, block, center, size, rot, origin or (center if rot else None), light)
    if g: m.cubes[-1]["g"] = g
    return m.cubes[-1]


def MB(m, bone, block, lo, size, rot=None, light=False, g=None):
    """B on the left and its mirror on the right (bone names ending in L get their R twin)."""
    B(m, bone, block, lo, size, rot, None, light, g)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone
    mlo = (-(lo[0] + size[0]), lo[1], lo[2])
    mr = None if not rot else (rot[0], -rot[1], -rot[2])
    B(m, rb, block, mlo, size, mr, None, light, g)


def MC(m, bone, block, center, size, rot=None, light=False, g=None):
    C(m, bone, block, center, size, rot, None, light, g)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone
    mr = None if not rot else (rot[0], -rot[1], -rot[2])
    C(m, rb, block, (-center[0], center[1], center[2]), size, mr, None, light, g)


def shaded(m, bone, lo, size, base, top=None, bottom=None, band=1.0, side=None):
    """A box with a lighter cap and a darker foot, drawn as stacked slices (no painted plates): reads as
    sculpted light at a distance. side: a darker block for the back half (cheap rim shading)."""
    x, y, z = lo
    w, h, d = size
    yb, yt = y, y + h
    if bottom and h > band * 2.5:
        B(m, bone, bottom, (x, y, z), (w, band, d)); yb = y + band
    if top and h > band * 2.5:
        B(m, bone, top, (x, yt - band, z), (w, band, d)); yt = yt - band
    B(m, bone, base, (x, yb, z), (w, yt - yb, d))


def eye(m, bone, cx, cy, zf, w=3, h=3, out=1.0, white="white_concrete", pupil="black_concrete", pw=None, ph=None,
        look=(0, 0), catch=True, rim=None, lid=None, glow=False):
    """An eyeball that sticks out of a face at zf (the face's front plane): a white box, a pupil plate on
    it (shifted by look), a one-pixel catch light, an optional rim plate behind and a lid plate on top."""
    pw = pw or max(1, w * 0.5)
    ph = ph or max(1, h * 0.55)
    if rim:
        B(m, bone, rim, (cx - w / 2 - 0.4, cy - h / 2 - 0.4, zf - 0.2), (w + 0.8, h + 0.8, out + 0.15))
    B(m, bone, white, (cx - w / 2, cy - h / 2, zf - 0.3), (w, h, out + 0.3), light=glow)
    px, py = cx + look[0], cy + look[1] - 0.15
    px = max(cx - w / 2 + pw / 2, min(cx + w / 2 - pw / 2, px))
    py = max(cy - h / 2 + ph / 2, min(cy + h / 2 - ph / 2, py))
    B(m, bone, pupil, (px - pw / 2, py - ph / 2, zf + out), (pw, ph, 0.12), light=glow)
    if catch:
        c = min(0.7, pw * 0.4)
        B(m, bone, "white_concrete", (px + pw / 2 - c - 0.05, py + ph / 2 - c - 0.05, zf + out + 0.1), (c, c, 0.06), light=True)
    if lid:
        B(m, bone, lid, (cx - w / 2 - 0.15, cy + h / 2 - 0.9, zf - 0.2), (w + 0.3, 1.1, out + 0.5))


def teeth(m, bone, x0, x1, y, zf, block="white_concrete", n=None, h=1.6, w=1.0, down=True, gap=None, d=0.8, jag=False):
    """A row of teeth between x0 and x1 at height y (hanging down if down, else standing up)."""
    span = x1 - x0
    n = n or max(2, int(span // 2))
    step = span / n
    for i in range(n):
        cx = x0 + step * (i + 0.5)
        hh = h * (0.7 if jag and i % 2 else 1.0)
        base, tip = hh * 0.6, hh * 0.4
        if down:
            B(m, bone, block, (cx - w / 2, y - base, zf - d), (w, base, d))
            B(m, bone, block, (cx - w / 4, y - hh, zf - d * 0.8), (w / 2, tip, d * 0.8))
        else:
            B(m, bone, block, (cx - w / 2, y, zf - d), (w, base, d))
            B(m, bone, block, (cx - w / 4, y + base, zf - d * 0.8), (w / 2, tip, d * 0.8))


def brow(m, bone, cx, cy, zf, w, block, tilt=0, h=1.0, d=1.2):
    """A slab brow over an eye; tilt in degrees (positive raises the outer end on the left side)."""
    C(m, bone, block, (cx, cy, zf + d / 2 - 0.2), (w, h, d), (0, 0, tilt) if tilt else None)


def tex(seed, rate):
    r = random.Random(zlib.crc32(repr(seed).encode()))
    return lambda: r.random() < rate


def speckle(m, bone, lo, size, face, blocks, n, seed, depth=0.05, cell=1.0, keep=()):
    """A few flush single-pixel plates on one face of a box: freckles, rivets, dirt. face: front/back/left/right/top."""
    rnd = random.Random(zlib.crc32(repr(seed).encode()))
    x, y, z = lo
    w, h, d = size
    for _ in range(n):
        b = rnd.choice(blocks)
        if face in ("front", "back"):
            px, py = x + rnd.random() * (w - cell), y + rnd.random() * (h - cell)
            pz = z + d if face == "front" else z - depth
            B(m, bone, b, (px, py, pz), (cell, cell, depth), g="detail")
        elif face in ("left", "right"):
            pz, py = z + rnd.random() * (d - cell), y + rnd.random() * (h - cell)
            px = x + w if face == "left" else x - depth
            B(m, bone, b, (px, py, pz), (depth, cell, cell), g="detail")
        else:
            px, pz = x + rnd.random() * (w - cell), z + rnd.random() * (d - cell)
            B(m, bone, b, (px, y + h, pz), (cell, depth, cell), g="detail")


def plank_rows(m, bone, lo, size, face, rows, keys, px=1.0, depth=0.06):
    """Pixel art on one face as merged plates: rows of characters, '.' is empty, keys map chars to blocks.
    The picture is centred on the face; px is the pixel size."""
    x, y, z = lo
    w, h, d = size
    H = len(rows)
    W = max(len(r) for r in rows)
    if face in ("front", "back"):
        ox = x + (w - W * px) / 2
    else:
        ox = z + (d - W * px) / 2
    oy = y + (h - H * px) / 2
    for j, r in enumerate(rows):
        i = 0
        while i < len(r):
            ch = r[i]
            if ch in ". ":
                i += 1; continue
            k = i
            while k < len(r) and r[k] == ch: k += 1
            yy = oy + (H - 1 - j) * px
            run = (k - i) * px
            if face == "front":
                B(m, bone, keys[ch], (ox + (W * px - (i * px) - run) if False else ox + i * px, yy, z + d), (run, px, depth))
            elif face == "back":
                B(m, bone, keys[ch], (ox + (W - k) * px, yy, z - depth), (run, px, depth))
            elif face == "left":
                B(m, bone, keys[ch], (x + w, yy, ox + (W - k) * px), (depth, px, run))
            elif face == "right":
                B(m, bone, keys[ch], (x - depth, yy, ox + i * px), (depth, px, run))
            i = k


def chain(m, bone, block, base, segs, light=False):
    """Pieces end to end: segs = [(length, (w, d), (rx, ry, rz), block or None)]; rotations are absolute (Z*Y*X,
    degrees). Each piece starts where the last ended, so a curved horn or leaf never comes apart."""
    from models import dirof
    x, y, z = base
    for seg in segs:
        L, (w, d), rot = seg[0], seg[1], seg[2]
        blk = seg[3] if len(seg) > 3 and seg[3] else block
        dx, dy, dz = dirof(rot)
        cx, cy, cz = x + dx * L / 2, y + dy * L / 2, z + dz * L / 2
        m.c(bone, blk, (cx, cy, cz), (w, L * 1.06, d), rot, (cx, cy, cz), light)
        x, y, z = x + dx * L, y + dy * L, z + dz * L
    return x, y, z


def front_art(m, bone, lo, size, rows, keys, px=1.0, depth=0.06):
    """Pixel art on the front face, x mirrored so the picture reads as drawn (left of the string is the
    viewer's left, which is the model's right, -x)."""
    x, y, z = lo
    w, h, d = size
    H = len(rows)
    W = max(len(r) for r in rows)
    ox = x + (w - W * px) / 2
    oy = y + (h - H * px) / 2
    for j, r in enumerate(rows):
        i = 0
        while i < len(r):
            ch = r[i]
            if ch in ". ":
                i += 1; continue
            k = i
            while k < len(r) and r[k] == ch: k += 1
            yy = oy + (H - 1 - j) * px
            # viewer's left = -x: column 0 is the lowest x
            B(m, bone, keys[ch], (ox + i * px, yy, z + d), ((k - i) * px, px, depth))
            i = k


# ----------------------------------------------------------------------------------------------- animation

def K(*pairs):
    return [[round(t, 4), [round(v, 3) for v in val]] for t, val in pairs]


Z = (0, 0, 0)


def wave(axis, amt, length, phase=0.0, base=(0, 0, 0), n=8):
    keys = []
    for k in range(n + 1):
        t = length * k / n
        r = list(base)
        r[axis] += amt * math.sin(2 * math.pi * (k / n + phase))
        keys.append((t, r))
    return K(*keys)


def wave2(amts, length, phase=0.0, base=(0, 0, 0), n=8):
    """All three axes at once: amts = (x, y, z) amplitudes; y is a quarter turn behind x for a figure-eight."""
    keys = []
    for k in range(n + 1):
        t = length * k / n
        a = 2 * math.pi * (k / n + phase)
        keys.append((t, (base[0] + amts[0] * math.sin(a), base[1] + amts[1] * math.sin(a + math.pi / 2), base[2] + amts[2] * math.sin(a * 2))))
    return K(*keys)


def ease_keys(times, values):
    return K(*zip(times, values))


def breathe(length, amt=0.03):
    return K((0, (1, 1, 1)), (length / 2, (1 + amt * 0.6, 1 + amt * 0.4, 1 + amt)), (length, (1, 1, 1)))


def bobpos(length, amt, phase=0.0, n=8):
    return wave(1, amt, length, phase, n=n)


def attack(length, hit, bones):
    return {"length": length, "hit": hit, "bones": bones}


def loop(length, bones):
    return {"length": length, "loop": True, "bones": bones}


# Biped attack set used by the redesigns: anticipation, a fast strike, a held impact and a slow recovery,
# with the hips and the off arm doing their share, so a hit reads from across an arena.
def biped_set(heavy=1.0, weapon="R"):
    W, O = ("armR", "armL") if weapon == "R" else ("armL", "armR")
    WF, OF = ("foreR", "foreL") if weapon == "R" else ("foreL", "foreR")
    sx = 1 if weapon == "R" else -1
    h = heavy
    return {
        # big overhead smash with both fists / the weapon
        "slam": attack(1.5, 0.82, {
            "armL": {"rot": K((0, Z), (0.55, (-165, 0, -14)), (0.72, (-172, 0, -10)), (0.82, (-30, 0, -6)), (1.1, (-26, 0, -6)), (1.5, Z))},
            "armR": {"rot": K((0, Z), (0.55, (-165, 0, 14)), (0.72, (-172, 0, 10)), (0.82, (-30, 0, 6)), (1.1, (-26, 0, 6)), (1.5, Z))},
            "foreL": {"rot": K((0, Z), (0.55, (-40, 0, 0)), (0.82, (10, 0, 0)), (1.5, Z))},
            "foreR": {"rot": K((0, Z), (0.55, (-40, 0, 0)), (0.82, (10, 0, 0)), (1.5, Z))},
            "body": {"rot": K((0, Z), (0.55, (-14 * h, 0, 0)), (0.72, (-16 * h, 0, 0)), (0.82, (26 * h, 0, 0)), (1.1, (24 * h, 0, 0)), (1.5, Z))},
            "head": {"rot": K((0, Z), (0.55, (-18, 0, 0)), (0.82, (8, 0, 0)), (1.5, Z))},
            "hips": {"pos": K((0, Z), (0.55, (0, 1.2, -0.8)), (0.82, (0, -3.0 * h, 1.2)), (1.1, (0, -2.8 * h, 1.2)), (1.5, Z))},
            "legL": {"rot": K((0, Z), (0.82, (-24, 0, -4)), (1.1, (-22, 0, -4)), (1.5, Z))},
            "legR": {"rot": K((0, Z), (0.82, (14, 0, 4)), (1.1, (12, 0, 4)), (1.5, Z))},
            "jaw": {"rot": K((0, Z), (0.55, (14, 0, 0)), (0.82, (22, 0, 0)), (1.5, Z))}}),
        # one-armed diagonal swing
        "swipe": attack(0.95, 0.46, {
            W: {"rot": K((0, Z), (0.32, (-150, -18 * sx, 30 * sx)), (0.46, (-20, 24 * sx, -12 * sx)), (0.62, (10, 30 * sx, -18 * sx)), (0.95, Z))},
            WF: {"rot": K((0, Z), (0.32, (-36, 0, 0)), (0.46, (20, 0, 0)), (0.95, Z))},
            O: {"rot": K((0, Z), (0.32, (-30, 0, -20 * sx)), (0.46, (18, 0, -6 * sx)), (0.95, Z))},
            "body": {"rot": K((0, Z), (0.32, (-6, -28 * sx, 0)), (0.46, (10, 26 * sx, 0)), (0.62, (12, 30 * sx, 0)), (0.95, Z))},
            "head": {"rot": K((0, Z), (0.32, (-4, 16 * sx, 0)), (0.46, (6, -10 * sx, 0)), (0.95, Z))},
            "hips": {"pos": K((0, Z), (0.32, (0, -0.4, -0.8)), (0.46, (0, -1.4, 1.4)), (0.62, (0, -1.4, 1.4)), (0.95, Z))},
            "legL": {"rot": K((0, Z), (0.46, (-18, 0, 0)), (0.7, (-16, 0, 0)), (0.95, Z))},
            "legR": {"rot": K((0, Z), (0.46, (12, 0, 0)), (0.7, (10, 0, 0)), (0.95, Z))}}),
        # chest out, arms wide, head thrown back then forward with the jaw open
        "roar": attack(1.6, 0.6, {
            "armL": {"rot": K((0, Z), (0.35, (-20, 0, -35)), (0.6, (-40, 0, -70)), (1.2, (-36, 0, -66)), (1.6, Z))},
            "armR": {"rot": K((0, Z), (0.35, (-20, 0, 35)), (0.6, (-40, 0, 70)), (1.2, (-36, 0, 66)), (1.6, Z))},
            "foreL": {"rot": K((0, Z), (0.6, (-50, 0, 0)), (1.2, (-46, 0, 0)), (1.6, Z))},
            "foreR": {"rot": K((0, Z), (0.6, (-50, 0, 0)), (1.2, (-46, 0, 0)), (1.6, Z))},
            "body": {"rot": K((0, Z), (0.35, (8, 0, 0)), (0.6, (-14, 0, 0)), (1.2, (-12, 0, 0)), (1.6, Z)),
                     "scl": K((0, (1, 1, 1)), (0.6, (1.06, 1.04, 1.08)), (1.2, (1.05, 1.03, 1.06)), (1.6, (1, 1, 1)))},
            "head": {"rot": K((0, Z), (0.35, (14, 0, 0)), (0.6, (-24, 0, 0)), (0.8, (-20, 8, 0)), (1.0, (-20, -8, 0)), (1.2, (-18, 0, 0)), (1.6, Z))},
            "jaw": {"rot": K((0, Z), (0.35, (4, 0, 0)), (0.6, (34, 0, 0)), (1.2, (30, 0, 0)), (1.6, Z))},
            "hips": {"pos": K((0, Z), (0.35, (0, -1.2, 0)), (0.6, (0, 0.6, 0)), (1.6, Z))}}),
        # a spell: gather at the chest, thrust both hands out
        "cast": attack(1.5, 0.9, {
            "armL": {"rot": K((0, Z), (0.5, (-50, 0, 30)), (0.75, (-60, 0, 36)), (0.9, (-95, 0, -10)), (1.2, (-90, 0, -8)), (1.5, Z))},
            "armR": {"rot": K((0, Z), (0.5, (-50, 0, -30)), (0.75, (-60, 0, -36)), (0.9, (-95, 0, 10)), (1.2, (-90, 0, 8)), (1.5, Z))},
            "foreL": {"rot": K((0, Z), (0.5, (-60, 0, 0)), (0.9, (-6, 0, 0)), (1.5, Z))},
            "foreR": {"rot": K((0, Z), (0.5, (-60, 0, 0)), (0.9, (-6, 0, 0)), (1.5, Z))},
            "body": {"rot": K((0, Z), (0.5, (-8, 0, 0)), (0.9, (10, 0, 0)), (1.5, Z))},
            "head": {"rot": K((0, Z), (0.5, (-12, 0, 0)), (0.9, (6, 0, 0)), (1.5, Z))},
            "hips": {"pos": K((0, Z), (0.5, (0, 0.8, -0.6)), (0.9, (0, -1.0, 1.0)), (1.5, Z))},
            "cape": {"rot": K((0, Z), (0.9, (30, 0, 0)), (1.5, Z))},
            "hat": {"rot": K((0, Z), (0.5, (-10, 0, 0)), (0.9, (8, 0, 0)), (1.5, Z))}}),
        # stamp: lift a knee high, crash down
        "stomp": attack(1.25, 0.72, {
            "legL": {"rot": K((0, Z), (0.45, (-70, 0, -6)), (0.6, (-74, 0, -6)), (0.72, (2, 0, 0)), (1.25, Z))},
            "shinL": {"rot": K((0, Z), (0.45, (60, 0, 0)), (0.72, (0, 0, 0)), (1.25, Z))},
            "body": {"rot": K((0, Z), (0.45, (-10, 0, -8)), (0.72, (18, 0, 4)), (1.0, (14, 0, 2)), (1.25, Z))},
            "armL": {"rot": K((0, Z), (0.45, (-40, 0, -40)), (0.72, (20, 0, -20)), (1.25, Z))},
            "armR": {"rot": K((0, Z), (0.45, (-30, 0, 40)), (0.72, (20, 0, 20)), (1.25, Z))},
            "head": {"rot": K((0, Z), (0.45, (-12, 0, 6)), (0.72, (12, 0, 0)), (1.25, Z))},
            "hips": {"pos": K((0, Z), (0.45, (0.6, 1.2, 0)), (0.72, (0, -2.4 * h, 0.6)), (1.0, (0, -2.0 * h, 0.6)), (1.25, Z))},
            "jaw": {"rot": K((0, Z), (0.72, (18, 0, 0)), (1.25, Z))}}),
        # lunge forward with the weapon arm
        "lunge": attack(1.1, 0.55, {
            W: {"rot": K((0, Z), (0.35, (-30, 0, 10 * sx)), (0.55, (-90, 0, -4 * sx)), (0.8, (-86, 0, -4 * sx)), (1.1, Z))},
            WF: {"rot": K((0, Z), (0.35, (-70, 0, 0)), (0.55, (0, 0, 0)), (1.1, Z))},
            O: {"rot": K((0, Z), (0.35, (-20, 0, -20 * sx)), (0.55, (30, 0, -10 * sx)), (1.1, Z))},
            "body": {"rot": K((0, Z), (0.35, (-10, -20 * sx, 0)), (0.55, (20, 14 * sx, 0)), (0.8, (18, 12 * sx, 0)), (1.1, Z))},
            "hips": {"pos": K((0, Z), (0.35, (0, 0.4, -1.5)), (0.55, (0, -1.8, 3.0)), (0.8, (0, -1.8, 3.0)), (1.1, Z))},
            "legL": {"rot": K((0, Z), (0.55, (-32, 0, 0)), (0.8, (-30, 0, 0)), (1.1, Z))},
            "legR": {"rot": K((0, Z), (0.55, (22, 0, 0)), (0.8, (20, 0, 0)), (1.1, Z))}}),
    }


def walk_biped(length=1.1, swing=26, arm=20, bob=0.9, sway=3):
    q = length / 4
    return loop(length, {
        "legL": {"rot": K((0, (swing, 0, 0)), (2 * q, (-swing, 0, 0)), (length, (swing, 0, 0)))},
        "legR": {"rot": K((0, (-swing, 0, 0)), (2 * q, (swing, 0, 0)), (length, (-swing, 0, 0)))},
        "shinL": {"rot": K((0, (0, 0, 0)), (q, (24, 0, 0)), (2 * q, (6, 0, 0)), (3 * q, (0, 0, 0)), (length, (0, 0, 0)))},
        "shinR": {"rot": K((0, (6, 0, 0)), (q, (0, 0, 0)), (2 * q, (0, 0, 0)), (3 * q, (24, 0, 0)), (length, (6, 0, 0)))},
        "armL": {"rot": K((0, (-arm, 0, -3)), (2 * q, (arm, 0, -3)), (length, (-arm, 0, -3)))},
        "armR": {"rot": K((0, (arm, 0, 3)), (2 * q, (-arm, 0, 3)), (length, (arm, 0, 3)))},
        "foreL": {"rot": K((0, (-12, 0, 0)), (2 * q, (0, 0, 0)), (length, (-12, 0, 0)))},
        "foreR": {"rot": K((0, (0, 0, 0)), (2 * q, (-12, 0, 0)), (length, (0, 0, 0)))},
        "hips": {"pos": K((0, Z), (q, (0, bob, 0)), (2 * q, Z), (3 * q, (0, bob, 0)), (length, Z)),
                 "rot": K((0, (0, 0, sway)), (2 * q, (0, 0, -sway)), (length, (0, 0, sway)))},
        "body": {"rot": K((0, (2, 5, 0)), (2 * q, (2, -5, 0)), (length, (2, 5, 0)))},
        "head": {"rot": K((0, (0, -4, 0)), (2 * q, (0, 4, 0)), (length, (0, -4, 0)))},
        "cape": {"rot": K((0, (14, 0, 0)), (2 * q, (20, 0, 0)), (length, (14, 0, 0)))},
    })


def idle_biped(length=4.0, look=20, breath=0.03, extra=None, arms=1.0):
    b = {
        "hips": {"pos": K((0, Z), (length / 4, (0.25, -0.4, 0)), (length / 2, Z), (3 * length / 4, (-0.25, -0.4, 0)), (length, Z)),
                 "rot": K((0, Z), (length / 4, (0, 0, 1.6)), (length / 2, Z), (3 * length / 4, (0, 0, -1.6)), (length, Z))},
        "body": {"rot": K((0, Z), (length / 4, (2.5, 1.5, -1.5)), (length / 2, (1, 0, 0)), (3 * length / 4, (2.5, -1.5, 1.5)), (length, Z)),
                 "scl": K((0, (1, 1, 1)), (length / 4, (1 + breath * 0.6, 1 + breath * 0.4, 1 + breath)), (length / 2, (1, 1, 1)),
                          (3 * length / 4, (1 + breath * 0.6, 1 + breath * 0.4, 1 + breath)), (length, (1, 1, 1)))},
        "head": {"rot": K((0, (0, -3, 0)), (0.2 * length, (-3, -look, 3)), (0.42 * length, (-3, -look, 3)), (0.62 * length, (2, look * 0.8, -4)),
                          (0.82 * length, (2, look * 0.8, -4)), (length, (0, -3, 0)))},
        "armL": {"rot": K((0, (2 * arms, 0, -4)), (length / 4, (-4 * arms, 0, -7)), (length / 2, (2 * arms, 0, -5)), (3 * length / 4, (-2 * arms, 0, -7)), (length, (2 * arms, 0, -4)))},
        "armR": {"rot": K((0, (-2 * arms, 0, 4)), (length / 4, (3 * arms, 0, 7)), (length / 2, (-3 * arms, 0, 5)), (3 * length / 4, (4 * arms, 0, 8)), (length, (-2 * arms, 0, 4)))},
        "foreL": {"rot": wave(0, 4, length, 0.1, base=(-6, 0, 0))},
        "foreR": {"rot": wave(0, 4, length, 0.35, base=(-6, 0, 0))},
        "jaw": {"rot": K((0, Z), (length * 0.25, (5, 0, 0)), (length * 0.35, Z), (length * 0.75, (3, 0, 0)), (length, Z))},
        "cape": {"rot": wave(0, 4, length, 0.2, base=(7, 0, 0))},
    }
    if extra: b.update(extra)
    return loop(length, b)


# ----------------------------------------------------------------------------------------------- bodies

def legs(m, x, top, w, d, block, foot=None, foot_h=1.6, toe=1.0, shin=None, knee_at=0.5, z=0.0):
    """Two legs from y=0 to top: thigh, shin (gen_models splits at the knee) and a flat foot that sticks out
    forward by toe."""
    for sd, leg in ((1, "legL"), (-1, "legR")):
        cx = sd * x
        kh = top * knee_at
        B(m, leg, block, (cx - w / 2, kh, z - d / 2), (w, top - kh, d))
        B(m, leg, shin or block, (cx - w / 2 + 0.1, foot_h, z - d / 2 + 0.1), (w - 0.2, kh - foot_h + 0.01, d - 0.2))
        if foot:
            B(m, leg, foot, (cx - w / 2 - 0.3, 0, z - d / 2 - 0.3), (w + 0.6, foot_h, d + 0.6 + toe))


def arms(m, x, top, w, d, upper, fore, hand, length, hand_h=None, fore_block=None, z=0.0, spread=0.0, hand_w=None):
    """Two arms hanging from the shoulder at (±x, top): upper arm, forearm and a fist (gen_models splits the
    elbow halfway). spread pushes the hands outward."""
    hh = hand_h or w
    hw = hand_w or w + 0.6
    for sd, arm in ((1, "armL"), (-1, "armR")):
        cx = sd * x
        up = length * 0.5
        B(m, arm, upper, (cx - w / 2, top - up, z - d / 2), (w, up, d))
        B(m, arm, fore_block or fore, (cx - w / 2 + 0.15 + sd * spread, top - length + hh * 0.6, z - d / 2 + 0.15), (w - 0.3, length - up - hh * 0.6 + 0.01, d - 0.3))
        B(m, arm, hand, (cx - hw / 2 + sd * spread, top - length - hh * 0.4, z - (d + 0.6) / 2), (hw, hh, d + 0.6))


def set_pivot(m, name, p):
    for b in m.bones:
        if b["name"] == name:
            b["pivot"] = [round(v, 3) for v in p]
            return
    raise KeyError(name)


def humanoid(m, hip, legx, neck, shoulder, armx, jaw=None):
    m.bone("hips", "root", (0, hip, 0))
    m.bone("legL", "hips", (legx, hip, 0)); m.bone("legR", "hips", (-legx, hip, 0))
    m.bone("body", "hips", (0, hip + 1, 0))
    m.bone("head", "body", (0, neck, 0))
    if jaw: m.bone("jaw", "head", jaw)
    m.bone("armL", "body", (armx, shoulder, 0)); m.bone("armR", "body", (-armx, shoulder, 0))


def standard_anims(m, heavy=1.0, weapon="R", idle=None, walk=None, extra=None, look=18):
    a = {"idle": idle or idle_biped(4.0, look), "walk": walk or walk_biped()}
    a.update(biped_set(heavy, weapon))
    if extra: a.update(extra)
    m.anims = a
