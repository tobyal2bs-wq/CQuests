#!/usr/bin/env python3
"""The Thorn Serpent uncoils when it moves: it lies out flat like a real snake and slithers.

python3 tools/slither.py models.json

At rest the model is a raised coil. The walk clip turns every coil bone so the chain lies in one line on the
ground, then sends a wave down it from head to tail. The walk blends in with speed, so the snake uncoils as it
sets off and coils up again when it stops. The same pose, faster, is its lunge-charge (slither_rush).
Run once (slither-revision).
"""
import json, math, sys
import numpy as np

CHAIN = ["coil0", "coil1", "coil2", "coil3", "coil4", "coil5", "coil6", "coil7"]


def rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler(M):
    """x, y, z in degrees with M = Rz * Ry * Rx, the order the rig uses."""
    y = -math.asin(max(-1, min(1, M[2][0])))
    x = math.atan2(M[2][1], M[2][2]); z = math.atan2(M[1][0], M[0][0])
    return [math.degrees(x), math.degrees(y), math.degrees(z)]


def straight(d):
    """Rotation that lays direction d along +z, turning about the vertical first so the segment keeps its top up."""
    yaw = math.atan2(d[0], d[2]); flat = math.hypot(d[0], d[2]); pitch = math.atan2(d[1], flat)
    return rx(pitch) @ ry(-yaw)


def near(e, prev):
    return [v + 360 * round((p - v) / 360) for v, p in zip(e, prev)]


def clip(m, length, amp, lift=0.0):
    piv = {b["name"]: np.array(b["pivot"], float) for b in m["bones"]}
    pts = [piv[b] for b in CHAIN] + [piv["head"]]
    base = [straight(pts[i + 1] - pts[i]) for i in range(len(CHAIN))]
    total = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(CHAIN)))
    n, bones = 12, {b: {"rot": []} for b in CHAIN + ["head", "hoodL", "hoodR"]}
    prev = {b: [0, 0, 0] for b in bones}
    for k in range(n + 1):
        t = length * k / n
        yaw = [math.radians(amp) * math.sin(2 * math.pi * (k / n - i / 3.2)) for i in range(len(CHAIN) + 1)]
        world = [ry(yaw[i]) @ base[i] for i in range(len(CHAIN))]
        up = rx(-math.radians(lift))
        last = np.eye(3)
        for i, b in enumerate(CHAIN):
            w = world[i] if i < 6 else ry(yaw[i]) @ (up if i == 7 else rx(-math.radians(lift) / 2)) @ base[i]
            world[i] = w
            e = near(euler(last.T @ w), prev[b]); prev[b] = e
            bones[b]["rot"].append([round(t, 3), [round(v, 2) for v in e]]); last = w
        head = ry(yaw[-1] * 0.6)
        for b in ("head", "hoodL", "hoodR"):
            e = near(euler(last.T @ head), prev[b]); prev[b] = e
            bones[b]["rot"].append([round(t, 3), [round(v, 2) for v in e]])
    p0 = pts[0]
    bones["root"] = {"pos": [[0, [round(-p0[0], 2), 0, round(-p0[2] - total / 2, 2)]], [length, [round(-p0[0], 2), 0, round(-p0[2] - total / 2, 2)]]]}
    return {"length": length, "bones": bones, "loop": True}


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    m = d["models"]["thorncoil_basilisk"]
    if not m.get("slither-revision"):
        m["anims"]["walk"] = clip(m, 1.2, 24)
        rush = clip(m, 0.5, 34, lift=18); rush.pop("loop"); rush["length"] = 1.5; rush["hit"] = 0.9
        for ch in rush["bones"].values():      # three fast waves, then back to the coil
            for kind in ch:
                one = ch[kind]
                ch[kind] = [[round(k[0] + 0.5 * j, 3), k[1]] for j in range(2) for k in one[(1 if j else 0):]] + [[1.5, [0, 0, 0]]]
                ch[kind].insert(0, [0, [0, 0, 0]]) if ch[kind][0][0] > 0 else None
                ch[kind][0] = [0, [0, 0, 0]]; ch[kind][1][0] = max(ch[kind][1][0], 0.18)
        rush["bones"]["jaw"] = {"rot": [[0, [0, 0, 0]], [0.8, [28, 0, 0]], [1.0, [0, 0, 0]]]}
        m["anims"]["slither_rush"] = rush
        m["attacks"]["charge"] = "slither_rush"
        m["slither-revision"] = 1
        print("thorn serpent slithers")
    json.dump(d, open(sys.argv[1], "w"), separators=(",", ":"))
