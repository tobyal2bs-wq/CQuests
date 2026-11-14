"""Thorncoil Basilisk body, rebuilt: one smooth tapered body along the coil bones, a pale belly,
dorsal pattern bands, small thorns, a wedge head with slit eyes and a forked tongue.
Bones, pivots, zones and clips are kept, so every animation still fits."""
import json, math, sys
p = sys.argv[1]
d = json.load(open(p)); m = d['models']['thorncoil_basilisk']
piv = {b['name']: b['pivot'] for b in m['bones']}
chain = ['coil%d' % i for i in range(8)] + ['head']
W = [2.2, 3.0, 3.8, 4.4, 4.6, 4.4, 4.0, 3.6]
r2 = lambda v: [round(x, 4) for x in v]
cubes = []

def seg(bone, a, b, w, k, g=None, side=None, thick=None, shift=0.0, ext=0.0, shrink=0.0):
    dx, dy, dz = b[0]-a[0], b[1]-a[1], b[2]-a[2]
    L = math.sqrt(dx*dx+dy*dy+dz*dz); ux, uy, uz = dx/L, dy/L, dz/L
    ra = math.asin(max(-1, min(1, uz))); ca = math.cos(ra)
    rc = math.atan2(-ux, uy) if ca > 1e-6 else 0.0
    o = [(a[i]+b[i])/2 for i in range(3)]
    hx = hz = w/2 - shrink; hy = L/2 + ext
    off = [0, 0, 0]
    if side:  # a thin plate on one face: side = ('x'|'z', +1|-1)
        ax, sg = side; t = thick or 0.3
        if ax == 'x': off[0] = sg*(w/2 - t/2 + 0.04); hx = t/2
        else: off[2] = sg*(w/2 - t/2 + 0.04); hz = t/2
    off[1] = shift
    c = {'b': bone, 'k': k, 'f': r2([o[0]+off[0]-hx, o[1]+off[1]-hy, o[2]+off[2]-hz]), 't': r2([o[0]+off[0]+hx, o[1]+off[1]+hy, o[2]+off[2]+hz]),
         'r': r2([math.degrees(ra), 0, math.degrees(rc)]), 'o': r2(o)}
    if g: c['g'] = g
    return c, (ra, rc)

def axes(ra, rc):
    sa, ca, sc, cc = math.sin(ra), math.cos(ra), math.sin(rc), math.cos(rc)
    X = (cc, sc, 0.0); Z = (sa*sc, -sa*cc, ca)
    return X, Z

for i in range(8):
    bone = chain[i]; a = piv[bone]; b = piv[chain[i+1]]
    if bone == 'coil7': b = [b[0], b[1]-0.5, b[2]-0.5]
    w = W[i]
    body, (ra, rc) = seg(bone, a, b, w, 'green_terracotta', ext=w*0.42)
    cubes.append(body)
    X, Z = axes(ra, rc)
    dy = abs(b[1]-a[1]) / max(1e-6, math.dist(a, b))
    belly = (0, -(1-dy), dy)  # down when lying, forward when rising
    cand = [(sum(X[j]*belly[j] for j in range(3)), 'x'), (sum(Z[j]*belly[j] for j in range(3)), 'z')]
    sc_, ax = max(cand, key=lambda t: abs(t[0])); sg = 1 if sc_ > 0 else -1
    L = math.dist(a, b)
    # belly scutes: two pale plates with a seam between them
    for s in (-1, 1):
        c, _ = seg(bone, a, b, w, 'white_terracotta' if i < 2 else 'yellow_terracotta', side=(ax, sg), thick=0.25, shift=s*L*0.26, ext=-L*0.25)
        lo, hi = c['f'], c['t']
        # narrow the plate across the body
        other = 2 if ax == 'x' else 0
        mid = (lo[other]+hi[other])/2; half = w*0.32
        lo[other], hi[other] = round(mid-half, 4), round(mid+half, 4)
        cubes.append(c)
    # dorsal pattern: a darker saddle band on the back
    c, _ = seg(bone, a, b, w, 'black_terracotta' if i % 2 else 'lime_terracotta', g='trim', side=(ax, -sg), thick=0.22, ext=-L*0.3)
    other = 2 if ax == 'x' else 0
    mid = (c['f'][other]+c['t'][other])/2; half = w*0.36
    c['f'][other], c['t'][other] = round(mid-half, 4), round(mid+half, 4)
    cubes.append(c)
    # a small thorn on every other segment
    if i % 2 == 1 and i < 7:
        o = body['o']; up = [(-sg)*(X if ax == 'x' else Z)[j] for j in range(3)]
        tip = [o[j] + up[j]*(w/2+0.6) for j in range(3)]
        cubes.append({'b': bone, 'k': 'dark_oak_log', 'f': r2([tip[0]-0.35, tip[1]-0.7, tip[2]-0.35]), 't': r2([tip[0]+0.35, tip[1]+0.7, tip[2]+0.35]),
                      'r': [-25, 0, 0], 'o': r2(tip), 'g': 'detail'})

H = lambda f, t, k, b='head', g=None: dict({'b': b, 'k': k, 'f': f, 't': t}, **({'g': g} if g else {}))
cubes += [
    # skull, a lower brow ridge and a tapering snout
    H([-3.4, 20.2, 2.6], [3.4, 24.2, 8.6], 'green_terracotta'),
    H([-2.6, 20.2, 8.4], [2.6, 23.0, 11.6], 'green_terracotta'),
    H([-1.8, 20.3, 11.4], [1.8, 22.4, 13.0], 'green_terracotta'),
    H([-3.5, 23.6, 5.2], [3.5, 24.5, 8.4], 'lime_terracotta', g='trim'),
    H([-2.2, 24.15, 2.8], [2.2, 24.6, 6.6], 'black_terracotta', g='trim'),
    H([-0.9, 22.3, 12.6], [-0.4, 22.6, 13.05], 'black_concrete', g='detail'),
    H([0.4, 22.3, 12.6], [0.9, 22.6, 13.05], 'black_concrete', g='detail'),
    # upper lip line
    H([-2.65, 20.15, 8.2], [2.65, 20.45, 11.65], 'black_terracotta', g='trim'),
    # lower jaw, pale chin, fangs and a forked tongue
    H([-2.5, 19.0, 5.6], [2.5, 20.2, 11.4], 'yellow_terracotta', b='jaw'),
    H([-1.6, 18.9, 11.2], [1.6, 20.0, 12.6], 'yellow_terracotta', b='jaw'),
    H([-2.1, 19.4, 10.0], [-1.6, 21.0, 10.5], 'bone_block', b='head', g='detail'),
    H([1.6, 19.4, 10.0], [2.1, 21.0, 10.5], 'bone_block', b='head', g='detail'),
    H([-0.25, 19.95, 9.0], [0.25, 20.15, 14.2], 'red_concrete', b='jaw', g='detail'),
    H([-0.75, 19.95, 14.0], [-0.25, 20.15, 15.0], 'red_concrete', b='jaw', g='detail'),
    H([0.25, 19.95, 14.0], [0.75, 20.15, 15.0], 'red_concrete', b='jaw', g='detail'),
]
for s in (-1, 1):
    x0 = 3.4*s
    lo, hi = sorted([x0, x0+0.2*s])
    cubes += [
        H(r2(sorted([x0-0.05*s, x0+0.22*s])[:1] + [22.0, 7.0]), r2(sorted([x0-0.05*s, x0+0.22*s])[1:] + [23.6, 9.0]), 'black_terracotta', g='eye_socket'),
        H(r2([min(x0+0.1*s, x0+0.3*s), 22.2, 7.2]), r2([max(x0+0.1*s, x0+0.3*s), 23.4, 8.8]), 'yellow_concrete', g='eye_iris'),
        H(r2([min(x0+0.25*s, x0+0.38*s), 22.25, 7.85]), r2([max(x0+0.25*s, x0+0.38*s), 23.35, 8.15]), 'black_concrete', g='eye_pupil'),
        # small swept-back horn-thorns
        {'b': 'head', 'k': 'dark_oak_log', 'f': r2([2.2*s-0.4, 24.0, 2.6]), 't': r2([2.2*s+0.4, 26.6, 3.4]), 'r': [-40, 0, -18*s], 'o': r2([2.2*s, 24.4, 3.0]), 'g': 'detail'},
    ]
# hood: thin flaps, olive outside, pale inside with two dark eye-spots
for s, bone in ((-1, 'hoodR'), (1, 'hoodL')):
    o = [3.0*s, 19.5, 2.3]
    rot = {'r': [0, 0, -16*s], 'o': o}
    cubes += [
        dict({'b': bone, 'k': 'green_terracotta', 'f': r2([3.2*s-1.3, 16.4, 2.0]), 't': r2([3.2*s+1.3, 22.0, 2.6])}, **rot),
        dict({'b': bone, 'k': 'green_terracotta', 'f': r2([3.0*s-0.9, 22.0, 2.0]), 't': r2([3.0*s+0.9, 23.0, 2.6])}, **rot),
        dict({'b': bone, 'k': 'yellow_terracotta', 'f': r2([3.2*s-0.9, 17.0, 2.6]), 't': r2([3.2*s+0.9, 21.6, 2.8])}, **rot),
        dict({'b': bone, 'k': 'black_terracotta', 'f': r2([3.2*s-0.45, 19.0, 2.8]), 't': r2([3.2*s+0.45, 19.9, 2.9]), 'g': 'detail'}, **rot),
    ]
for c in cubes:
    for k in ('f', 't'):
        c[k] = [round(v, 4) for v in c[k]]
    if 'r' in c and all(abs(v) < 1e-9 for v in c['r']):
        del c['r']; c.pop('o', None)
m['cubes'] = cubes
m['height'] = max(c['t'][1] for c in cubes)
json.dump(d, open(p, 'w'), separators=(',', ':'))
print(len(cubes), 'cubes')
