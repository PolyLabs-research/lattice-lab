"""Soundness / scope of the hexagon mechanism across sizes.  For odd primes m = 1 mod 3 (so sqrt(-3) in F_m)
and small (p, q) with q^2 + 3 p^2 = 0 mod m ('-3 type': the two hexagons of f_{p,q} share a 120-degree
rotation M in SL2(F_m)), test confinement of f_{p,q} at m: cube / ninth (when 3 resp. 9 divide 2^d - 1,
d = ord_m(2)).  Controls: f_{2,5} (= 4850) and f_{1,2}, f_{3,1} at the same m when they are not '-3 type'.
Also records whether the cube root of unity of F_m lies in <2> mod m (then M is a partial Frobenius)."""
import sys, json, math
import sympy
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
from gf2 import Field
from hexfamily import f_pq, confinement


def ordm(m):
    return sympy.n_order(2, m)


out = []
for m in sympy.primerange(7, 140):
    if m % 3 != 1:
        continue
    d = ordm(m)
    if d > 54:
        continue
    w = next(x for x in range(2, m) if pow(x, 3, m) == 1)
    two_pows = {pow(2, e, m) for e in range(d)}
    w_in_2 = w in two_pows
    cands = sorted([(max(2 * p, q), p, q) for p in range(1, 10) for q in range(1, 20)
                    if (q * q + 3 * p * p) % m == 0 and math.gcd(p, q) == 1])[:2]
    Fd = Field(m)
    for _, p, q in cands:
        c = confinement(f_pq(p, q), m, Fd)
        rec = dict(m=m, d=d, three_divides=(2 ** d - 1) % 3 == 0, nine_divides=(2 ** d - 1) % 9 == 0,
                   omega_in_2=w_in_2, p=p, q=q, kind='-3', **c)
        out.append(rec); print(rec, flush=True)
    for p, q in ((2, 5), (1, 2), (3, 1)):
        if (q * q + 3 * p * p) % m == 0:
            continue
        c = confinement(f_pq(p, q), m, Fd)
        rec = dict(m=m, d=d, three_divides=(2 ** d - 1) % 3 == 0, nine_divides=(2 ** d - 1) % 9 == 0,
                   omega_in_2=w_in_2, p=p, q=q, kind='control', **c)
        out.append(rec)
json.dump(out, open('hexsizes.json', 'w'), indent=1)
print('controls cube-confined:', [(r['m'], r['p'], r['q']) for r in out if r['kind'] == 'control' and r['cube']])
print('-3 type cube-confined:', [(r['m'], r['p'], r['q']) for r in out if r['kind'] == '-3' and r['cube']])
print('-3 type NOT cube-confined (3 | 2^d-1):', [(r['m'], r['p'], r['q'], r['omega_in_2']) for r in out if r['kind'] == '-3' and r['cube'] is False])
