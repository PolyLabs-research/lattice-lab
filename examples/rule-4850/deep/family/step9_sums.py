"""Step 9. Unions of two M-invariant numerators at m = 37 (and 13): (H_1 + H_2)/s where each H_i is a hexagon
numerator (eigenvalue W(A_i c)) or a 24-point numerator (eigenvalue W(A al, A lam be) + W(A lam al, A be)).
Eigenvalue off the diagonals: (X_1 + X_2)/(t_al t_be).  Report every pair whose off-diagonal values are confined
beyond generic (3-adic level >= 1), with its level.  (Diagonal classes depend on integer representatives; omitted.)"""
import json, sys
import numpy as np
import famlib as L
from sizes_engine import Size, v3arr
from step4_lambda import W_values, lam_classes

res = {}
for m in [int(x) for x in sys.argv[1:]] or [37, 13]:
    S = Size(m)
    A3, Q = S.A, 3 ** S.A
    r = S.roots[0]
    Wv, u = W_values(S, r)
    reps, mu6 = lam_classes(m, u)
    idx = np.arange(m)
    al = idx[:, None] * np.ones((1, m), dtype=np.int64)
    be = np.ones((m, 1), dtype=np.int64) * idx[None, :]
    off = (al > 0) & (be > 0)
    units = []
    for x in S.units:
        if (m - x) not in units:
            units.append(x)
    # numerators: list of (name, grid of field values)
    nums = []
    for lam in reps:
        for Aa in units:
            G = np.zeros((m, m), dtype=object)
            for x in range(1, m):
                for y in range(1, m):
                    if lam in mu6:
                        G[x, y] = Wv[Aa * x % m, Aa * y % m]
                    else:
                        G[x, y] = Wv[Aa * x % m, Aa * lam * y % m] ^ Wv[Aa * lam * x % m, Aa * y % m]
            nums.append(((lam, Aa), G))
    print(m, 'numerators:', len(nums), flush=True)
    vt = S.vt
    vpi = (vt[al] + vt[be]) % Q
    found = []
    logcache = {}
    F = S.F

    def lg(v):
        if v not in logcache:
            logcache[v] = F.log3(v)
        return logcache[v]
    # Frobenius classes of characters suffice: one representative per orbit of (x,y) -> (2x,2y), with D4
    reps_c = []
    seen = set()
    for x in range(1, m):
        for y in range(1, m):
            if (x, y) in seen:
                continue
            c = (x, y)
            while c not in seen:
                seen.add(c); seen.add((y, x) if False else c)
                c = (2 * c[0] % m, 2 * c[1] % m)
            reps_c.append((x, y))
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            (n1, G1), (n2, G2) = nums[i], nums[j]
            worst = 0
            nz = 0
            for (x, y) in reps_c:
                v = G1[x, y] ^ G2[x, y]
                if v == 0:
                    continue
                nz += 1
                Lc = (lg(v) - int(vpi[x, y])) % Q
                e = A3 - L.v3(Lc, A3) - (A3 - int(S.a[x, y]))
                worst = max(worst, e)
                if S.agen - worst < 1:
                    break
            lev = S.agen - worst
            if lev >= 1 and nz:
                found.append(dict(n1=n1, n2=n2, level=lev, nonzero_classes=nz))
    res[m] = found
    print(m, 'pairs confined off-diagonal:', len(found))
    for f in found[:60]:
        print('   ', f)
json.dump({str(k): v for k, v in res.items()}, open('step9_sums.json', 'w'), indent=1)
