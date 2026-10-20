"""Step 18: the literal cube-plus-square shape as a candidate mechanism.  F = pi^3 + Y^2 with
pi = ab and Y any symmetric polynomial of radius <= 3 (a union of D4-orbits (p,q), p <= 3), so F has radius <= 6.
Which are ninth-confined at 37?  Which of them are pi*F = (T-orbit union) (the Kloosterman shape)?
Also F = c * pi^3 + Y^2 with c in {1, e, ...} is skipped: the point is whether 'pi^3 + square' forces anything."""
import json
import numpy as np
import nf

V = nf.V27()
J, K = nf.grid()
nz = ~((J == 0) & (K == 0))
orbs3 = nf.orbits(3)
pi = nf.vmul(nf.vt(J), nf.vt(K))
pi3 = nf.vpow(pi, 3)
Yvals = {}
conf = []
cube = []
for n in range(1 << len(orbs3)):
    Y = np.zeros(J.shape, dtype=np.int64)
    for i, o in enumerate(orbs3):
        if n >> i & 1:
            Y ^= nf.vorbit(o)
    F = pi3 ^ nf.vmul(Y, Y)
    v = V[F[nz]]
    ok9 = bool(np.all((v < 0) | (v % 9 == 0)))
    ok3 = bool(np.all((v < 0) | (v % 3 == 0)))
    if ok9:
        conf.append((n, [o for i, o in enumerate(orbs3) if n >> i & 1], int((v < 0).sum())))
    if ok3:
        cube.append(n)
print('Y over all 1024 unions of radius-3 orbits: F = pi^3 + Y^2 ninth-confined for', len(conf), '; cube-confined for', len(cube))
for n, o, z in conf:
    print('   Y orbits', o, ' zeros', z)
json.dump(dict(ninth=conf, n_cube=len(cube)), open('step18_cubesq_family.json', 'w'), indent=1)
