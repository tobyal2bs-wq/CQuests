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

    def height(self):
        return max(c["t"][1] for c in self.cubes)

    def json(self):
        bn = {b["name"] for b in self.bones}
        for c in self.cubes: assert c["b"] in bn
        return {"rig": self.rig, "scale": self.scale, "height": round(self.height(), 2), "bones": self.bones, "cubes": self.cubes,
                "attacks": self.attacks, "melee": self.melee, "spawn": self.spawn, "death": self.death}
