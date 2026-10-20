"""Look-elsewhere for the hexagon mechanism: among radius-4 rules f with |f*u| <= 16 (u = s or ab),
which have f*u invariant (as an exponent set mod 37) under an element of SL2(F37) of order 3 (mod +-1)
that is NOT in the D4 symmetry group?  Report them with their confinement at 37."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census
from sparsequot import grid, conv, S, AB
from sl2search import sl2

P = 37
mats = sl2()
# order 3 up to sign: M^3 = +-I, M != +-I
def mpow(M, k):
    R = np.eye(2, dtype=np.int64)
    for _ in range(k):
        R = (R @ M) % P
    return R
o3 = []
for m in mats:
    M = np.array(m).reshape(2, 2)
    M3 = mpow(M, 3)
    if (np.array_equal(M3, np.eye(2, dtype=np.int64)) or np.array_equal(M3, (P - 1) * np.eye(2, dtype=np.int64))) and not (
            np.array_equal(M, np.eye(2, dtype=np.int64)) or np.array_equal(M, (P - 1) * np.eye(2, dtype=np.int64))):
        o3.append(M)
o3 = np.array(o3)
print('order-3 (mod sign) elements of SL2(F37):', len(o3))
logs4 = census.class_logs(4)
found = []
for n in range(1, 1 << 15):
    f = grid(census.rule(n, 4), 4)
    for name, u in (('s', S), ('ab', AB)):
        G = conv(f, u)
        w = int(G.sum())
        if w > 16 or w == 0:
            continue
        R = (G.shape[0] - 1) // 2
        pts = np.array([(i - R, j - R) for i, j in zip(*np.nonzero(G))]) % P   # exponent vectors
        key = set(map(tuple, pts))
        # transform exponents by A^T for each M: (p,q) -> (M00 p + M10 q, M01 p + M11 q)
        tp = (o3[:, 0, 0][:, None] * pts[None, :, 0] + o3[:, 1, 0][:, None] * pts[None, :, 1]) % P
        tq = (o3[:, 0, 1][:, None] * pts[None, :, 0] + o3[:, 1, 1][:, None] * pts[None, :, 1]) % P
        codes = tp * P + tq
        kc = np.array(sorted(p * P + q for p, q in key))
        inv = np.array([np.array_equal(np.sort(c), kc) for c in codes])
        if inv.any():
            L = logs4[:, n]; nz = L[L != 255]
            found.append(dict(rule=n, u=name, weight=w, n_M=int(inv.sum()), cube=bool(np.all(nz % 3 == 0)),
                              ninth=bool(np.all(nz % 9 == 0)), logs=[int(x) for x in L]))
for fnd in found:
    print(fnd)
json.dump(found, open('minv_census.json', 'w'), indent=1)
