"""The 24 world boss models. Run gen_models.py to write src/main/resources/worldboss-models.json."""
from build import Model

MODELS = []
def model(fn):
    MODELS.append(fn)
    return fn

def biped(m, hip, legx, neck, shoulder, armx):
    """Standard humanoid bones; pivots only, cubes are added by each boss."""
    m.bone("hips", "root", (0, hip, 0))
    m.mbone("legL", "hips", (legx, hip, 0))
    m.bone("body", "hips", (0, hip + 1, 0))
    m.bone("head", "body", (0, neck, 0))
    m.mbone("armL", "body", (armx, shoulder, 0))

def horn(m, bone, block, base, segs, rot0, bend, size0, shrink=0.8, light=False):
    """A curved horn or spike: each segment continues from the tip of the last and turns by bend."""
    import math
    x, y, z = base
    rx, ry, rz = rot0
    s = size0
    for i in range(segs):
        L = s * 2.2
        # direction of a cube's local +y after its rotation (Z*Y*X)
        a, b, c = math.radians(rx), math.radians(ry), math.radians(rz)
        dx, dy, dz = 0.0, 1.0, 0.0
        dy, dz = dy * math.cos(a) - dz * math.sin(a), dy * math.sin(a) + dz * math.cos(a)
        dx, dz = dx * math.cos(b) + dz * math.sin(b), -dx * math.sin(b) + dz * math.cos(b)
        dx, dy = dx * math.cos(c) - dy * math.sin(c), dx * math.sin(c) + dy * math.cos(c)
        cx, cy, cz = x + dx * L / 2, y + dy * L / 2, z + dz * L / 2
        m.c(bone, block, (cx, cy, cz), (s, L, s), (rx, ry, rz), (cx, cy, cz), light)
        x, y, z = x + dx * L * 0.9, y + dy * L * 0.9, z + dz * L * 0.9
        rx, ry, rz = rx + bend[0], ry + bend[1], rz + bend[2]
        s *= shrink

def mhorn(m, bone, block, base, segs, rot0, bend, size0, shrink=0.8, light=False):
    horn(m, bone, block, base, segs, rot0, bend, size0, shrink, light)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone
    horn(m, rb, block, (-base[0], base[1], base[2]), segs, (rot0[0], -rot0[1], -rot0[2]), (bend[0], -bend[1], -bend[2]), size0, shrink, light)


def dirof(rot):
    import math
    a, b, c = (math.radians(v) for v in rot)
    dx, dy, dz = 0.0, 1.0, 0.0
    dy, dz = dy * math.cos(a) - dz * math.sin(a), dy * math.sin(a) + dz * math.cos(a)
    dx, dz = dx * math.cos(b) + dz * math.sin(b), -dx * math.sin(b) + dz * math.cos(b)
    dx, dy = dx * math.cos(c) - dy * math.sin(c), dx * math.sin(c) + dy * math.cos(c)
    return dx, dy, dz

def limb(m, bone, block, base, segs, light=False, joint=None):
    """A chain of rotated pieces: segs = [(length, thickness, (rx, ry, rz)), ...] with absolute rotations.
    Each piece starts where the last ended. joint adds a small knob block at each joint. Returns the tip."""
    x, y, z = base
    for i, seg in enumerate(segs):
        L, s, rot = seg[0], seg[1], seg[2]
        blk = seg[3] if len(seg) > 3 else block
        dx, dy, dz = dirof(rot)
        cx, cy, cz = x + dx * L / 2, y + dy * L / 2, z + dz * L / 2
        m.c(bone, blk, (cx, cy, cz), (s, L, s), rot, (cx, cy, cz), light)
        x, y, z = x + dx * L, y + dy * L, z + dz * L
        if joint and i < len(segs) - 1:
            m.c(bone, joint, (x, y, z), (s * 1.25, s * 1.25, s * 1.25), rot, (x, y, z))
    return x, y, z

def mlimb(m, bone, block, base, segs, light=False, joint=None):
    limb(m, bone, block, base, segs, light, joint)
    rb = bone[:-1] + "R" if bone.endswith("L") else bone[:-2] + "R" + bone[-1] if bone[-2:-1] == "L" else bone
    limb(m, rb, block, (-base[0], base[1], base[2]), [(s[0], s[1], (s[2][0], -s[2][1], -s[2][2])) + tuple(s[3:]) for s in segs], light, joint)

def taper(m, bone, block, x, y0, z, sizes, step, light=False):
    """Stacked boxes, one per (width, depth), each step high: robes, cones, tails."""
    y = y0
    for w, d in sizes:
        m.c(bone, block, (x, y + step / 2, z), (w, step, d), light=light)
        y += step

# ---------------------------------------------------------------------------------------------- quads

def quad(m, body_y, legx, legz_front, legz_back, neck_y, neck_z):
    m.bone("body", "root", (0, body_y, 0))
    m.mbone("legFL", "body", (legx, body_y, legz_front))
    m.mbone("legBL", "body", (legx, body_y, legz_back))
    m.bone("head", "body", (0, neck_y, neck_z))
    m.bone("jaw", "head", (0, neck_y - 3, neck_z + 4))
    m.bone("tail", "body", (0, body_y + 4, legz_back - 6))
