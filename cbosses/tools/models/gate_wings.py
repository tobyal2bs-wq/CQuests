"""Gate Shade wings, rebuilt as stone bat wings: a stepped arm ridge, three finger struts and a
dark membrane whose lower edge scallops up between the struts."""
import json, sys
p = sys.argv[1]; d = json.load(open(p)); m = d['models']['gate_shade']
m['cubes'] = [c for c in m['cubes'] if c['b'] not in ('wingL', 'wingR')]
def wing(bone, s, px):
    o = [px, 24.4, -5.98]; rot = {'r': [0, 30*s, 0], 'o': o}
    X = lambda a, b: sorted([px + s*a, px + s*b])
    z0, z1 = -6.38, -5.98
    out = []
    def box(a, b, y0, y1, k, zz=(z0, z1), g=None):
        x = X(a, b); c = {'b': bone, 'k': k, 'f': [round(x[0], 3), y0, zz[0]], 't': [round(x[1], 3), y1, zz[1]]}; c.update(rot)
        if g: c['g'] = g
        out.append(c)
    # arm ridge, stepping up toward a hooked claw
    box(-0.1, 6.2, 27.8, 29.3, 'stone', (-6.6, -5.7))
    box(6.0, 11.5, 28.6, 30.0, 'stone', (-6.55, -5.75))
    box(11.3, 15.6, 29.4, 30.7, 'stone', (-6.5, -5.8))
    box(15.3, 16.3, 29.9, 32.2, 'andesite', (-6.45, -5.85), 'detail')
    # finger struts
    for a, y0 in ((6.0, 16.8), (11.3, 19.4), (15.3, 22.6)):
        box(a - 0.35, a + 0.35, y0, 29.6, 'stone', (-6.5, -5.85), 'trim')
    # membrane: panels between struts, longer next to each strut, short in the middle
    panels = ((0.3, 6.0, 18.2, 16.8), (6.0, 11.3, 21.0, 19.4), (11.3, 15.3, 24.2, 22.6))
    for a, b, mid, edge in panels:
        w = b - a
        box(a, b, mid, 29.0, 'polished_deepslate')
        box(a, a + w*0.22, edge, mid, 'polished_deepslate')
        box(b - w*0.22, b, edge + 0.4, mid, 'polished_deepslate')
        box(a + w*0.22, a + w*0.4, edge + 0.7, mid, 'polished_deepslate')
        box(b - w*0.4, b - w*0.22, edge + 1.0, mid, 'polished_deepslate')
        # a faint vein across each panel
        box(a + 0.4, b - 0.4, mid + 3.0, mid + 3.3, 'cobbled_deepslate', (-6.42, -6.34), 'detail')
    return out
m['cubes'] += wing('wingL', 1, 4.09) + wing('wingR', -1, -3.91)
json.dump(d, open(p, 'w'), separators=(',', ':'))
print(len(m['cubes']))
