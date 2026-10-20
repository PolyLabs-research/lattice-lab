"""Step 19: the Kloosterman shape inside the radius-6 census family.  A rule f of radius <= 6 has the shape
if pi * f (exact Laurent product, radius <= 7) has support a union of <D4, T>-orbits mod 37
(T = diag(10, 26)).  Enumerate: every <D4,T>-orbit whose centred lift lies in the box |p|, |q| <= 7 and avoids the
axes; every union G of such orbits; f = G / pi (exact division: G avoids the axes so a | G and b | G);
keep f of radius <= 6.  Then: ninth-confinement of each f at 37, and its D4-orbit decomposition / census number.
Also the same in 4850's frame: s * f = union of <D4, M0>-orbits with s = x + 1/x + y + 1/y."""
import itertools, json
import numpy as np
import sympy as sp
import nf

m = 37
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
def cen(p):
    p %= m
    return p - m if p > m // 2 else p
def orbit_pts(p, q, M):
    """<D4, M>-orbit of (p,q) mod 37 where M is a list of 2x2 matrices generating with D4."""
    pts = {(p % m, q % m)}
    frontier = list(pts)
    gens = [((0, 1), (1, 0)), ((m - 1, 0), (0, 1)), ((1, 0), (0, m - 1))] + M
    while frontier:
        nxt = []
        for (x, y) in frontier:
            for g in gens:
                z = ((g[0][0] * x + g[0][1] * y) % m, (g[1][0] * x + g[1][1] * y) % m)
                if z not in pts:
                    pts.add(z); nxt.append(z)
        frontier = nxt
    return frozenset(pts)
def small_orbits(M, box):
    out = set()
    for p in range(-box, box + 1):
        for q in range(-box, box + 1):
            O = orbit_pts(p, q, M)
            if all(abs(cen(x)) <= box and abs(cen(y)) <= box for x, y in O):
                out.add(O)
    return sorted(out, key=lambda o: sorted(o))
x, y = sp.symbols('x y')
def divide(G, den, shift_den):
    """exact division of the Laurent polynomial sum_{c in G} x^c by den (sympy poly times x^-s y^-s)."""
    R = 8
    num = sp.Poly(sum(x ** (cen(p) + R) * y ** (cen(q) + R) for p, q in G), x, y, modulus=2)
    qt, rm = sp.div(num, den)
    if not rm.is_zero:
        return None
    pts = set()
    for (i, j), c in qt.terms():
        if int(c) % 2:
            pts.add((i - (R - shift_den), j - (R - shift_den)))
    return frozenset(pts)
def census_number(f):
    r = max(max(abs(p), abs(q)) for p, q in f)
    ol = nf.orbits(r)
    orbs = {(max(abs(p), abs(q)), min(abs(p), abs(q))) for p, q in f}
    return sum(1 << ol.index(o) for o in orbs), r
results = {}
for frame, M, den, sd, unitname in (('T (rotated) frame, pi * f', [((10, 0), (0, 26))], sp.Poly((x ** 2 + 1) * (y ** 2 + 1), x, y, modulus=2), 1, 'pi'),
                                    ('M0 (4850) frame, s * f', [((18, 29), (29, 18))], sp.Poly((x ** 2 + 1) * y + (y ** 2 + 1) * x, x, y, modulus=2), 1, 's')):
    orbs = [O for O in small_orbits(M, 7) if all(cen(p) != 0 and cen(q) != 0 for p, q in O) or unitname == 's']
    if unitname == 's':
        orbs = small_orbits(M, 7)
    print(frame, ': orbits in the box:', len(orbs), [sorted({(max(abs(cen(p)), abs(cen(q))), min(abs(cen(p)), abs(cen(q)))) for p, q in O}) for O in orbs])
    rows = []
    for r in range(1, len(orbs) + 1):
        for combo in itertools.combinations(range(len(orbs)), r):
            G = frozenset().union(*[orbs[i] for i in combo])
            f = divide(G, den, sd)
            if f is None or not f:
                continue
            if max(max(abs(p), abs(q)) for p, q in f) > 6:
                continue
            n, rad = census_number(f)
            vals = nf.vrule(n, rad)
            conf = nf.is_ninth_confined(vals)
            rows.append(dict(orbits=[sorted({(max(abs(cen(p)), abs(cen(q))), min(abs(cen(p)), abs(cen(q)))) for p, q in orbs[i]}) for i in combo],
                             rule=n, radius=rad, ninth=conf, logs27=nf.class_v27(vals)))
    for row in rows:
        print('   G =', row['orbits'], ' f = rule', row['rule'], 'radius', row['radius'], ' ninth-confined:', row['ninth'], row['logs27'])
    results[frame] = rows
json.dump(results, open('step19_shape_census.json', 'w'), indent=1)
