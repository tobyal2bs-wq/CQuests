"""Import a vanilla Java entity model (the way Mojang writes them in code) into painted boxes.

Write the parts the way the game does: a parent, a pivot, a rotation in radians and box-UV boxes, all in
the model's own space (y down, front towards -z, 24 = the ground). vbuild() walks the parent chain, turns
every box into our space (y up, front +z, 0 = the ground) and paints it from the texture.

    P = {
      "body": (None, (0, 7, 0), (0, 0, 0), [((1, 1), (-8, -7, -13), (16, 14, 26))]),
      "head": ("body", (0, 2, -12), (0.87, 0, 0), [((61, 1), (-7, -3, -19), (14, 6, 19))]),
    }
    pivots = vbuild(m, img, P, {"body": "body", "head": "head"}, allowed=[...])

A box is (uv, origin, size) with optional inflate and mirror: (uv, origin, size, inflate, mirror).
A part's boxes go to the bone named in bones (or the part's own name). The return value maps each part
to its pivot in our space, handy for placing bones."""
import math
from texpaint import paintbox


def _mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _vec(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]


def _rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Y = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Z = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return _mat_mul(_mat_mul(Z, Y), X)


def _euler_zyx(R):
    """Degrees (x, y, z) with R = Rz * Ry * Rx."""
    b = math.asin(max(-1, min(1, -R[2][0])))
    if abs(math.cos(b)) > 1e-6:
        a = math.atan2(R[2][1], R[2][2])
        c = math.atan2(R[1][0], R[0][0])
    else:
        a, c = math.atan2(-R[1][2], R[1][1]), 0
    return tuple(round(math.degrees(t), 3) for t in (a, b, c))


S = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]


def world(parts):
    """Each part's world pivot and rotation in model space."""
    out = {}

    def get(n):
        if n in out: return out[n]
        parent, pivot, rot, _ = parts[n][:4]
        R = _rot(*rot)
        if parent:
            pp, pr = get(parent)
            P = [pp[i] + _vec(pr, pivot)[i] for i in range(3)]
            Rw = _mat_mul(pr, R)
        else:
            P, Rw = list(pivot), R
        out[n] = (P, Rw)
        return out[n]

    for n in parts: get(n)
    return out


def to_ours(p):
    return (p[0], 24 - p[1], -p[2])


def vbuild(m, img, parts, bones=None, skip=(), extra=None, **kw):
    """Paint every box of every part. bones maps part -> our bone. extra maps part -> extra paintbox kwargs."""
    bones = bones or {}
    W = world(parts)
    pivots = {}
    for n, spec in parts.items():
        P, R = W[n]
        O = to_ours(P)
        pivots[n] = O
        if n in skip: continue
        Rs = _mat_mul(_mat_mul(S, R), S)
        rot = _euler_zyx(Rs)
        if all(abs(t) < 1e-3 for t in rot): rot = None
        for box in spec[3]:
            uv, org, size = box[0], box[1], box[2]
            inflate = box[3] if len(box) > 3 else 0
            mirror = box[4] if len(box) > 4 else False
            w, h, d = size
            # the box in part space, inflated, then flipped into our axes around the pivot
            lo_m = [org[i] - inflate for i in range(3)]
            hi_m = [org[i] + size[i] + inflate for i in range(3)]
            a = [lo_m[0], -hi_m[1], -hi_m[2]]
            b = [hi_m[0], -lo_m[1], -lo_m[2]]
            lo = [O[i] + a[i] for i in range(3)]
            ext = [b[i] - a[i] for i in range(3)]
            plane = None
            if d == 0: plane = "front"
            elif w == 0: plane = "right"
            elif h == 0: plane = "top"
            args = dict(kw)
            args.update((extra or {}).get(n, {}))
            if plane:
                args["shell"] = False
                args["plane"] = plane
                if plane == "front": lo[2] -= 0.25
                elif plane == "top": lo[1] -= 0.25
                else: lo[0] -= 0.25
            paintbox(m, bones.get(n, n), img, uv, lo, (w, h, d), mirror=mirror, rot=rot, origin=O if rot else None,
                     extent=ext, **args)
    return pivots
