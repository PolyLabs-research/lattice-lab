"""Step 9: G = pi * f (mod x^37 - 1, y^37 - 1), pi = (x + 1/x)(y + 1/y), for 10491524, 20982139, 178279803.
Its support, its decomposition into <D4, T>-orbits (T: (p, q) -> (10 p, 26 q)), the sparsest
Frobenius form G = g^(2^k) (g = G dilated by 2^-k), and the exact (polynomial) product pi * f."""
import json
import numpy as np
import nf

m = 37
def rule_pts(n, r):
    pts = {}
    for o in nf.rule_orbits(n, r):
        a, b = o
        for p, q in {(sp * x, sq * y) for x, y in ((a, b), (b, a)) for sp in (1, -1) for sq in (1, -1)}:
            pts[(p, q)] = pts.get((p, q), 0) ^ 1
    return {k for k, v in pts.items() if v}
def mul_pts(A, B, mod=None):
    out = {}
    for p, q in A:
        for r, s in B:
            k = (p + r, q + s) if mod is None else ((p + r) % mod, (q + s) % mod)
            out[k] = out.get(k, 0) ^ 1
    return {k for k, v in out.items() if v}
PI = {(1, 1), (1, -1), (-1, 1), (-1, -1)}
def red(S):
    return {(p % m, q % m) for p, q in S}
def centered(p):
    p %= m
    return p - m if p > m // 2 else p
def orbit_T(pt):
    p, q = pt
    out = set()
    for c in (1, 10, 26):
        ci = pow(c, -1, m)
        for sp_ in (1, -1):
            for sq in (1, -1):
                x, y = sp_ * c * p % m, sq * ci * q % m
                out.add((x, y)); out.add((y, x))
    return frozenset(out)
res = {}
for n in (10491524, 20982139, 178279803):
    f = rule_pts(n, 6)
    Gpoly = mul_pts(f, PI)               # exact Laurent product
    G = red(Gpoly)                        # mod 37 (no wrap at radius 7 < 18.5 anyway)
    Tinv = all(orbit_T(p) <= G for p in G)
    orbs = sorted({orbit_T(p) for p in G}, key=lambda o: min(abs(centered(x)) + abs(centered(y)) for x, y in o))
    # Frobenius forms: dilate by 2^-k
    best = None
    for k in range(36):
        dk = pow(2, -k, m)
        g = {(dk * p % m, dk * q % m) for p, q in G}
        rad = max(max(abs(centered(x)), abs(centered(y))) for x, y in g)
        if best is None or rad < best[0]:
            best = (rad, k, sorted((centered(x), centered(y)) for x, y in g))
    # D4-orbit description of the best g
    gor = sorted({(max(abs(x), abs(y)), min(abs(x), abs(y))) for x, y in best[2]})
    print(n, '|f| =', len(f), '|pi f| =', len(Gpoly), ' radius of pi f:', max(max(abs(x), abs(y)) for x, y in Gpoly))
    print('    pi f orbits (D4):', sorted({(max(abs(x), abs(y)), min(abs(x), abs(y))) for x, y in Gpoly}))
    print('    T-invariant support mod 37:', Tinv, ' #<D4,T>-orbits:', len(orbs), ' sizes:', [len(o) for o in orbs])
    print('    sparsest dilation g = G^(2^-k): k =', best[1], ' radius', best[0], ' D4 orbits of g:', gor)
    res[n] = dict(pif_orbits=sorted({(max(abs(x), abs(y)), min(abs(x), abs(y))) for x, y in Gpoly}),
                  T_invariant=Tinv, n_T_orbits=len(orbs), best_k=best[1], best_radius=best[0], g_orbits=gor)
json.dump(res, open('step9_piG.json', 'w'), indent=1)
