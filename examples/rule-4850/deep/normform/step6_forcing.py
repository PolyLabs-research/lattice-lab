"""Step 6: symmetry forcing.  Let Gamma be a group of pairs (g, k), g in GL2(F37) acting on characters,
k in Z/18, with v(g c) = 2^k v(c) (mod 27) for v = v27(lambda).  Every symmetric rule has
Gamma_0 = <(D4, 0), (2I, 1)>.  If (g, k) in Gamma fixes c (g c = c), then (2^k - 1) v(c) = 0 mod 27:
   k odd -> v(c) = 0 mod 27;  k even, 3 !| k -> v = 0 mod 9;  k = 6, 12 mod 18 -> v = 0 mod 3.
Compute, for Gamma_0 and for Gamma_0 + (M, 0) with M = T = diag(10, 26) (rotated frame) and
M = M0 = [[18,29],[29,18]] (4850's frame), the forced 3-adic level at each census class."""
import json
import numpy as np

m = 37
D4 = [((1, 0), (0, 1)), ((m - 1, 0), (0, 1)), ((1, 0), (0, m - 1)), ((m - 1, 0), (0, m - 1)),
      ((0, 1), (1, 0)), ((0, m - 1), (1, 0)), ((0, 1), (m - 1, 0)), ((0, m - 1), (m - 1, 0))]
def mm(g, h):
    return tuple(tuple(sum(g[i][t] * h[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
def act(g, c):
    return ((g[0][0] * c[0] + g[0][1] * c[1]) % m, (g[1][0] * c[0] + g[1][1] * c[1]) % m)
def closure(gens):
    I = ((1, 0), (0, 1))
    seen = {(I, 0)}
    frontier = [(I, 0)]
    while frontier:
        nxt = []
        for g, k in frontier:
            for h, kh in gens:
                e = (mm(h, g), (k + kh) % 18)
                if e not in seen:
                    seen.add(e); nxt.append(e)
        frontier = nxt
    return seen
CLASSES = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
def forced(G):
    out = []
    for c in CLASSES:
        ks = sorted({k for g, k in G if act(g, c) == c})
        lvl = 1
        for k in ks:
            v3 = 0
            x = (pow(2, k, 27 * 81) - 1) % 27
            # forced: v = 0 mod 27 / gcd(2^k - 1, 27)
            from math import gcd
            lvl = max(lvl, 27 // gcd(pow(2, k) - 1, 27))
        out.append((c, ks, lvl))
    return out
base = [(g, 0) for g in D4] + [(((2, 0), (0, 2)), 1)]
res = {}
for name, extra in (('Gamma0 (all symmetric rules)', []), ('Gamma0 + T (rotated frame)', [(((10, 0), (0, 26)), 0)]),
                    ('Gamma0 + M0 (4850 frame)', [(((18, 29), (29, 18)), 0)])):
    G = closure(base + extra)
    f = forced(G)
    print(name, '|Gamma| =', len(G))
    for c, ks, lvl in f:
        print('   class', c, 'stabilizer multipliers', ks, '-> forced v = 0 mod', lvl)
    res[name] = {'order': len(G), 'forced': {str(c): lvl for c, ks, lvl in f}}
json.dump(res, open('step6_forcing.json', 'w'), indent=1)
