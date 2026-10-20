"""Step 9: Hilbert-90 certificates for the norm identities.

N_{F(2^18)/F_64}(f2) = N(f1) at every nonzero character  <=>  f2/f1 = g^63 = g^64/g pointwise for
some g  <=>  f2 * g = f1 * g(x^10, y^10)  (mod x^37-1, y^37-1, and the trivial character).
The solution space in the symmetric group ring is about 63-dimensional (an F_64-line at each
class) inside about 190 dimensions, so a solution g supported on the orbits of radius <= R would
be a sparse certificate; by chance one expects none once #orbits(R) + 63 < 190.
We solve for g in the span of the D4-orbits of radius <= R (R up to 12), for the pairs
(10491524, 20982139), (10491524, 178279803), (20982139, 178279803), and as controls for pairs
that are NOT norm-equivalent (4850 with each of them; random rules)."""
import numpy as np, random
from rlib import rule_points, orbits, points
from gring import *
from gf2lin import kernel

def rp(n):
    r = 4 if n < 2**15 else (5 if n < 2**21 else 6)
    return rule_points(n, r)

JJ = np.ones((M, M), dtype=np.uint8)

def solve(f2, f1, R):
    """basis of g in span of orbits radius <= R with f2*g + f1*g(10.) in F_2 JJ"""
    orbs = orbits(R)
    cols = []
    for o in orbs:
        e = elem(points(o))
        w = mul(f2, e) ^ mul(f1, dil(e, 10))
        cols.append(w.reshape(-1))
    cols.append(JJ.reshape(-1))
    A = np.array(cols, dtype=np.uint8).T
    ker = kernel(A)
    sols = [x[:-1] for x in ker if x[:-1].any()]
    return orbs, sols

pairs = [(20982139, 10491524), (178279803, 10491524), (178279803, 20982139), (10491524, 20982139),
         (4850, 10491524), (20982139, 4850)]
rng = random.Random(3)
for _ in range(2):
    pairs.append((rng.randrange(1, 1 << 28), 10491524))
for a, b in pairs:
    fa, fb = elem(rp(a)), elem(rp(b))
    for R in (6, 9, 12):
        orbs, sols = solve(fa, fb, R)
        if sols:
            ws = sorted(int(s.sum()) for s in sols)
            print(f'f2={a} f1={b} R={R}: {len(orbs)} orbits, kernel dim {len(sols)}; orbit-weights {ws[:8]}')
            best = min(sols, key=lambda s: s.sum())
            print('     lightest g: orbits', [orbs[i] for i in np.flatnonzero(best)])
            break
        else:
            print(f'f2={a} f1={b} R={R}: {len(orbs)} orbits, no solution')
