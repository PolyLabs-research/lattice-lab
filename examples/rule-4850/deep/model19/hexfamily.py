"""The hexagon family.  For integers p, q > 0 let Hex_{p,q} = sum of x^e over the hexagon
e in {+-(2p, 0), +-(p, q), +-(p, -q)}, and f_{p,q} = (Hex_{p,q}(x,y) + Hex_{p,q}(y,x)) / s,
s = x + 1/x + y + 1/y (s always divides; f is a D4-symmetric Laurent polynomial).  4850 = f_{2,5}.
Mod m the two hexagons have a common 120-degree rotation M in SL2(F_m) iff q^2 = -3 p^2 (form j^2-k^2)
or q^2 = 3 p^2 (form j^2+k^2) mod m.  Here: build f_{p,q}, confirm f_{2,5} = 4850, and compute the
power-confinement (cube / ninth / 27th) at m = 37 for all p, q <= 12, with an F(2^36) field."""
import sys, json, math
import numpy as np
import sympy
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
from gf2 import Field
import census

X, Y = sympy.symbols('x y')


def hex_pts(p, q):
    return {(2 * p, 0), (-2 * p, 0), (p, q), (-p, -q), (p, -q), (-p, q)}


def f_pq(p, q):
    G = hex_pts(p, q) ^ {(b, a) for a, b in hex_pts(p, q)}
    R = max(2 * p, q) + 1
    num = sympy.Poly(sum(X ** (a + R) * Y ** (b + R) for a, b in G), X, Y, modulus=2)
    den = sympy.Poly((X + Y) * (1 + X * Y), X, Y, modulus=2)   # = s * x * y
    quo, rem = sympy.div(num, den)
    assert rem.is_zero
    # quo = f * x^(R-1) y^(R-1)
    pts = set()
    for (a, b), c in quo.terms():
        if int(c) % 2:
            pts.add((a - (R - 1), b - (R - 1)))
    return frozenset(pts)


def confinement(fset, m=37, Fd=None):
    Fd = Fd or Field(m)
    N = Fd.order
    z = Fd.zeta
    zp = [1]
    for i in range(m - 1):
        zp.append(Fd.mul(zp[-1], z))
    seen = set(); vals = []
    for j in range(m):
        for k in range(m):
            if (j, k) in seen or (j, k) == (0, 0):
                continue
            c = (j, k)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            v = 0
            for a, b in fset:
                v ^= zp[(a * j + b * k) % m]
            vals.append(v)
    nz = [v for v in vals if v]
    level = {}
    for q in (3, 9, 27):
        level[q] = all(Fd.pow(v, N // q) == 1 for v in nz) if N % q == 0 else None
    return dict(zeros=len(vals) - len(nz), cube=level[3], ninth=level[9], q27=level[27])


if __name__ == '__main__':
    f25 = f_pq(2, 5)
    print('f_{2,5} == rule 4850:', f25 == census.rule(4850, 4), ' |f_{2,5}| =', len(f25))
    F37 = Field(37)
    out = []
    for p in range(1, 13):
        for q in range(1, 13):
            rel = ('-3' if (q * q + 3 * p * p) % 37 == 0 else '') + ('+3' if (q * q - 3 * p * p) % 37 == 0 else '')
            f = f_pq(p, q)
            c = confinement(f, 37, F37)
            rec = dict(p=p, q=q, terms=len(f), radius=max(max(abs(a), abs(b)) for a, b in f), M_at_37=rel, **c)
            out.append(rec)
            if rel or c['ninth']:
                print(rec, flush=True)
    print('ninth-confined at 37 among p,q <= 12:', [(r['p'], r['q'], r['M_at_37']) for r in out if r['ninth']])
    print('cube-confined at 37:', [(r['p'], r['q'], r['M_at_37']) for r in out if r['cube']])
    json.dump(out, open('hexfamily.json', 'w'), indent=1)
