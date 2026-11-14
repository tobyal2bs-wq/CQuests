"""Model builder: bones and cubes in model pixels (16 = one block at scale 1). The model faces +z,
its left side is +x, the origin is the centre of its feet."""
import json, math

class Model:
    def __init__(self, id, rig, scale):
        self.id, self.rig, self.scale = id, rig, scale
        self.bones, self.cubes, self.names = [], [], set()
        self.bone("root", None, (0, 0, 0))
        self.attacks, self.melee, self.spawn, self.death = {}, None, None, None

    def bone(self, name, parent, pivot):
        assert name not in self.names, name
        assert parent is None or parent in self.names, parent
        self.names.add(name)
        self.bones.append({"name": name, "parent": parent, "pivot": [round(v, 3) for v in pivot]})
        return name

    def box(self, bone, block, f, t, rot=None, origin=None, light=False):
        assert bone in self.names, bone
        f, t = [min(a, b) for a, b in zip(f, t)], [max(a, b) for a, b in zip(f, t)]
        assert all(b - a > 0 for a, b in zip(f, t)), (bone, f, t)
        c = {"b": bone, "k": block, "f": [round(v, 3) for v in f], "t": [round(v, 3) for v in t]}
        if rot and any(rot):
            c["r"] = [round(v, 2) for v in rot]
            c["o"] = [round(v, 3) for v in (origin or [(a + b) / 2 for a, b in zip(f, t)])]
        if light: c["l"] = 1
        self.cubes.append(c)

    def c(self, bone, block, center, size, rot=None, origin=None, light=False):
        """A cube by centre and size."""
        f = [p - s / 2 for p, s in zip(center, size)]
        t = [p + s / 2 for p, s in zip(center, size)]
        self.box(bone, block, f, t, rot, origin, light)

    def m(self, bone, block, center, size, rot=None, origin=None, light=False):
        """A cube on the left (+x) and its mirror on the right. Bones ending in L get their R twin."""
        self.c(bone, block, center, size, rot, origin, light)
        rb = bone[:-1] + "R" if bone.endswith("L") else bone.replace("L", "R", 1) if bone[-2:-1] == "L" else bone
        mc = (-center[0], center[1], center[2])
        mr = None if not rot else (rot[0], -rot[1], -rot[2])
        mo = None if not origin else (-origin[0], origin[1], origin[2])
        self.c(rb, block, mc, size, mr, mo, light)

    def mbone(self, name, parent, pivot):
        """A left bone and its right twin (names end in L / R)."""
        self.bone(name, parent, pivot)
        rp = parent[:-1] + "R" if parent and parent.endswith("L") else parent
        self.bone(name[:-1] + "R", rp, (-pivot[0], pivot[1], pivot[2]))

    def rest(self, bone, rot):
        """A resting rotation (degrees) added to whatever the animations do: bent elbows, a raised weapon."""
        for b in self.bones:
            if b["name"] == bone:
                b["rest"] = [round(v, 2) for v in rot]
                return
        raise KeyError(bone)

    def elbows(self, bend=-38, frac=0.5, weapons=None):
        """Splits each arm at the elbow into arm (upper) and fore (forearm and hand), bends the elbow and
        hands every bone held in that hand (a weapon) to the forearm. weapons maps a held bone to the
        extra forward tilt it gets on top of undoing the elbow bend: 0 keeps it upright (staffs),
        more points it forward like a raised sword."""
        weapons = weapons or {}
        for side in "LR":
            arm = "arm" + side
            if arm not in self.names: continue
            piv = next(b for b in self.bones if b["name"] == arm)["pivot"]
            mine = [c for c in self.cubes if c["b"] == arm]
            if not mine: continue
            low = min(c["f"][1] for c in mine)
            ey = piv[1] - (piv[1] - low) * frac
            lower = [c for c in mine if (c["f"][1] + c["t"][1]) / 2 < ey]
            if not lower: continue
            ex = sum((c["f"][0] + c["t"][0]) / 2 for c in lower) / len(lower)
            ez = sum((c["f"][2] + c["t"][2]) / 2 for c in lower) / len(lower)
            fore = "fore" + side
            # insert right after the arm so parents still come first
            i = next(k for k, b in enumerate(self.bones) if b["name"] == arm)
            self.names.add(fore)
            self.bones.insert(i + 1, {"name": fore, "parent": arm, "pivot": [round(ex, 3), round(ey, 3), round(ez, 3)], "rest": [bend, 0, 0]})
            for c in lower: c["b"] = fore
            for b in self.bones:
                if b["parent"] == arm and b["name"] != fore:
                    b["parent"] = fore
                    tilt = weapons.get(b["name"], 25)
                    tx, ty, tz = tilt if isinstance(tilt, (tuple, list)) else (tilt, 0, 0)
                    b["rest"] = [round(-bend + tx, 2), ty, tz]

    LEGS = ("legL", "legR", "legFL", "legFR", "legBL", "legBR", "legML", "legMR")

    def knees(self, frac=0.5, foot=0.22):
        """Splits each leg at the knee into leg (thigh), shin<side> and foot<side>. The shin bends in the
        walk; the foot is kept level with the ground by the renderer, so feet stay flat when the boss
        leans or crouches."""
        pv = {b["name"]: b for b in self.bones}
        for leg in self.LEGS:
            if leg not in self.names or getattr(self, "no_knees", False): continue
            mine = [c for c in self.cubes if c["b"] == leg]
            if len(mine) < 2: continue
            top = pv[leg]["pivot"][1]
            low = min(c["f"][1] for c in mine)
            if top - low < 4: continue
            ky = low + (top - low) * frac
            cy = lambda c: (c["f"][1] + c["t"][1]) / 2
            lower = [c for c in mine if cy(c) < ky]
            if not lower or len(lower) == len(mine): continue
            suf = leg[3:]
            sx = sum((c["f"][0] + c["t"][0]) / 2 for c in lower) / len(lower)
            sz = sum((c["f"][2] + c["t"][2]) / 2 for c in lower) / len(lower)
            i = next(k for k, b in enumerate(self.bones) if b["name"] == leg)
            shin, ft = "shin" + suf, "foot" + suf
            self.names.update((shin, ft))
            fy = low + max(1.0, (ky - low) * foot)
            self.bones.insert(i + 1, {"name": shin, "parent": leg, "pivot": [round(sx, 3), round(ky, 3), round(sz, 3)]})
            self.bones.insert(i + 2, {"name": ft, "parent": shin, "pivot": [round(sx, 3), round(fy, 3), round(sz, 3)], "level": 1})
            for c in lower:
                c["b"] = ft if c["t"][1] <= fy + 0.05 else shin
            for b in self.bones:
                if b["parent"] == leg and b["name"] not in (shin,): b["parent"] = shin

    METAL = ("iron_block", "gold_block", "netherite_block", "polished_deepslate", "chain", "anvil", "copper", "polished_blackstone", "raw_gold_block", "raw_iron_block")

    def zones(self):
        """Hit zones from the cubes: head, weak spot (the biggest glowing piece on the body), body, each
        arm, tail and the held weapon. Legs are left to the real mob, whose hitbox covers the lower part."""
        parent = {b["name"]: b["parent"] for b in self.bones}
        def chain(b):
            out = []
            while b: out.append(b); b = parent[b]
            return out
        def cat(b):
            ch = chain(b)
            for i, n in enumerate(ch):
                if n.startswith("fore") and i > 0: return "weapon"
            for n in ch:
                if n in ("head",) : return "head"
                if n in ("armL", "foreL", "riderArmL"): return "armL"
                if n in ("armR", "foreR", "riderArmR"): return "armR"
                if n.startswith("leg") or n == "cape" or n.startswith("ring") or n.startswith("shell"): return None
                if n == "tail": return "tail"
            return "body"
        groups = {}
        for c in self.cubes:
            k = cat(c["b"])
            if k: groups.setdefault(k, []).append(c)
        H = self.height()
        zones = []
        mult = {"head": 1.5, "body": 1.0, "armL": 0.8, "armR": 0.8, "tail": 0.8, "weapon": 0.3}
        for k, cs in groups.items():
            if len(cs) < 2 and k != "head": continue
            # the solid mass only: horns, feathers and trims would blow the box up
            vol = lambda c: (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2])
            if k != "weapon":
                big = max(vol(c) for c in cs)
                cs = [c for c in cs if vol(c) >= big * (0.3 if k == "head" else 0.15)]
            lo = [min(c["f"][i] for c in cs) for i in range(3)]
            hi = [max(c["t"][i] for c in cs) for i in range(3)]
            d = [b - a for a, b in zip(lo, hi)]
            cen = [(a + b) / 2 for a, b in zip(lo, hi)]
            bones = {}
            for c in cs: bones[c["b"]] = bones.get(c["b"], 0) + 1
            bone = max(bones, key=bones.get)
            if k == "body": w = min(d[0], d[2]) + 1
            elif k == "weapon": w = sorted(d)[1]
            else: w = max(d[0], d[2])
            metal = sum(1 for c in cs if any(c["k"].startswith(x) for x in self.METAL)) / len(cs)
            kind = "armor" if k == "body" and metal > 0.5 else "helmet" if k == "head" and metal > 0.5 else k.rstrip("LR") if k.startswith("arm") else k
            m = {"armor": 0.6, "helmet": 1.2}.get(kind, mult[k])
            zones.append({"kind": kind, "b": bone, "c": [round(v, 2) for v in cen], "w": round(max(3, w), 2), "h": round(max(3, d[1]), 2), "mult": m})
        # the weak spot: the biggest glowing piece on the body (or anywhere but the weapon)
        lit = [c for c in groups.get("body", []) if c.get("l")] or [c for k, cs in groups.items() if k != "weapon" for c in cs if c.get("l")]
        if lit:
            c = max(lit, key=lambda c: (c["t"][0] - c["f"][0]) * (c["t"][1] - c["f"][1]) * (c["t"][2] - c["f"][2]))
            d = [b - a for a, b in zip(c["f"], c["t"])]
            cen = [(a + b) / 2 for a, b in zip(c["f"], c["t"])]
            cen[2] += 1.5
            zones.append({"kind": "weak", "b": c["b"], "c": [round(v, 2) for v in cen], "w": round(max(5, max(d) + 1), 2), "h": round(max(5, d[1] + 1), 2), "mult": 2.5})
        self.zone_list = zones
        if self.rig == "biped":
            hip = next(b for b in self.bones if b["name"] == "hips")["pivot"][1]
            self.hitbox = round(max(0.4, min(0.7, hip / H + 0.08)), 3)
        else:
            self.hitbox = 0.5

    def hands(self):
        """Fingers on every hand: the lowest piece of each forearm is the fist. A hand holding something
        gets a row of knuckles wrapped round the grip and a thumb over it; an empty hand gets three
        fingers and a thumb."""
        for side, sx in (("L", 1), ("R", -1)):
            fore = "fore" + side
            if fore not in self.names: continue
            mine = [c for c in self.cubes if c["b"] == fore and "r" not in c]
            if not mine: continue
            h = min(mine, key=lambda c: (c["f"][1] + c["t"][1]) / 2)
            f, t = h["f"], h["t"]
            w, ht, d = t[0] - f[0], t[1] - f[1], t[2] - f[2]
            if w < 1.6 or ht < 1.6: continue
            cx, cz = (f[0] + t[0]) / 2, (f[2] + t[2]) / 2
            block = h["k"]
            holds = any(b["parent"] == fore for b in self.bones)
            inner = -sx  # toward the body
            if holds:
                self.c(fore, block, (cx, f[1] + ht * 0.45, t[2] + 0.3), (w * 0.96, ht * 0.5, 0.6))
                for k in range(3):
                    self.c(fore, block, (cx + (k - 1) * w * 0.3, f[1] + ht * 0.45, t[2] + 0.75), (w * 0.22, ht * 0.38, 0.4))
                self.c(fore, block, (cx + inner * w * 0.42, f[1] + ht * 0.7, t[2] + 0.2), (w * 0.24, ht * 0.3, 1.2))
            else:
                for k in range(3):
                    self.c(fore, block, (cx + (k - 1) * w * 0.3, f[1] - ht * 0.18, cz + d * 0.18), (w * 0.24, ht * 0.42, d * 0.3), (-20, 0, 0))
                self.c(fore, block, (cx + inner * w * 0.5, f[1] + ht * 0.2, cz + d * 0.3), (w * 0.22, ht * 0.4, d * 0.28), (0, 0, inner * -25))

    def height(self):
        return max(c["t"][1] for c in self.cubes if not c["b"].startswith("shell"))

    def json(self):
        bn = {b["name"] for b in self.bones}
        for c in self.cubes: assert c["b"] in bn
        return {"rig": self.rig, "scale": self.scale, "height": round(self.height(), 2), "bones": self.bones, "cubes": self.cubes,
                "attacks": self.attacks, "melee": self.melee, "spawn": self.spawn, "death": self.death,
                "zones": getattr(self, "zone_list", []), "hitbox": getattr(self, "hitbox", 1),
                **({"anims": self.anims} if getattr(self, "anims", None) else {})}
