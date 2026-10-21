"""Edge cases against the builder's functions: tiny tori, zero / cancelling / repeated / unreduced
polynomials, A = B, k = 0; logical basis properties; the z-encoding of nontriviality."""
import random, sys
from pathlib import Path
import numpy as np
import mydist as M
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
import bb

cases = [
    ("zero A,B 1x1", [], [], 1, 1),
    ("A=1,B=0 1x1", [(0, 0)], [], 1, 1),
    ("A=0,B=0 2x2", [], [], 2, 2),
    ("A cancels 2x3", [(0, 0), (2, 3)], [(1, 1)], 2, 3),  # (2,3) == (0,0) mod (2,3): A = 0
    ("A=B 3x3", [(0, 0), (1, 0), (0, 1)], [(0, 0), (1, 0), (0, 1)], 3, 3),
    ("A=B 1x7", [(0, 0), (0, 1), (0, 3)], [(0, 0), (0, 1), (0, 3)], 1, 7),
    ("repeat 1x7", [(0, 0), (0, 0), (0, 0), (0, 1), (0, 3)], [(0, 2), (0, 9), (0, -5)], 1, 7),
    ("unreduced 2x9", [(-1, 0), (0, 10), (0, 11)], [(3, 2), (4, 0), (0, -2)], 2, 9),
    ("l=1 1x9 1+y", [(0, 0), (0, 1)], [(0, 0), (0, 3)], 1, 9),
    ("m=1 7x1", [(0, 0), (1, 0), (3, 0)], [(0, 0), (2, 0), (3, 0)], 7, 1),
    ("2x2 toric", [(0, 0), (1, 0)], [(0, 0), (0, 1)], 2, 2),
    ("1x2", [(0, 0), (0, 1)], [(0, 0)], 1, 2),
    ("1x2 k>0", [(0, 0), (0, 1)], [(0, 0), (0, 1)], 1, 2),
    ("A=0 2x7", [], [(0, 0), (1, 1), (0, 3)], 2, 7),
    ("A=1 B=1 2x7", [(0, 0)], [(0, 0)], 2, 7),
    ("4x4 x2+y2", [(0, 0), (2, 0)], [(0, 0), (0, 2)], 4, 4),
    ("2x7 A=1+x B=1+x", [(0, 0), (1, 0)], [(0, 0), (1, 0)], 2, 7),
]
bad = 0
for name, A, B, ell, m in cases:
    M.guard(A, B, ell, m)
    k = bb.k_linalg(A, B, ell, m)
    assert k == M.k_of(A, B, ell, m)
    res = [name, f"k={k}"]
    for kind in "ZX":
        Hc, Hs = M.pair(kind, A, B, ell, m)
        hx, hz = D.check_matrices(A, B, ell, m)
        mx, mz = M.checks(A, B, ell, m)
        assert np.array_equal(hx, mx) and np.array_equal(hz, mz)
        z = D.distance_ilp(A, B, ell, m, kind, time_limit=60)
        zt = D.distance_ilp(A, B, ell, m, kind, time_limit=60, translation=False)
        try:
            b = D.distance_brute(A, B, ell, m, kind)["d"]
        except ValueError:
            b = "cap"
        mine = M.distance_brute(Hc, Hs) if M.kernel(Hc).shape[0] <= 27 else None
        dfs = M.dfs_c(Hc, Hs, min(64, 2 * ell * m + 1))[0] if k else None
        if dfs is not None and dfs > 2 * ell * m:
            dfs = None
        ok = z["d"] == zt["d"] == b == mine == dfs if b != "cap" else z["d"] == zt["d"] == mine == dfs
        if k == 0:
            ok = ok and z["status"] == "no_logicals"
        bad += not ok
        res.append(f"{kind}: ilp={z['status']},{z['d']} notrans={zt['d']} brute={b} mine={mine} dfs={dfs} {'OK' if ok else 'DISAGREE'}")
    print(" | ".join(res))
print("disagreements", bad)

# logical basis: exactly k, in the kernel, independent mod stabilizers; z-encoding vs rank test
rng = random.Random("checker-independent logicals")
nb = 0
for trial in range(60):
    ell, m = rng.choice([(1, 7), (2, 7), (4, 4), (2, 9), (2, 11), (3, 9), (5, 6), (4, 7), (6, 7)])
    A = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 5))]
    B = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 5))]
    M.guard(A, B, ell, m)
    k = bb.k_linalg(A, B, ell, m)
    hx, hz = D.check_matrices(A, B, ell, m)
    for kind in "XZ":
        L = D.logical_basis(A, B, ell, m, kind)
        of, st = (hz, hx) if kind == "X" else (hx, hz)
        assert L.shape[0] == k, (L.shape, k)
        assert not ((of.astype(int) @ L.T) % 2).any()
        assert M.rank(np.vstack([st, L])) == M.rank(st) + k
    # z-encoding: for random c in ker H_X: (some LX.c odd) <=> c not in rowspace H_Z
    LX = D.logical_basis(A, B, ell, m, "X")
    K = M.kernel(hx)
    rz = M.rank(hz)
    for _ in range(40):
        coef = np.array([rng.randrange(2) for _ in range(K.shape[0])], dtype=np.uint8)
        if rng.random() < 0.5:  # make it a stabilizer sometimes
            w = np.array([rng.randrange(2) for _ in range(hz.shape[0])], dtype=np.uint8)
            c = (w.astype(int) @ hz) % 2
        else:
            c = (coef.astype(int) @ K) % 2
        c = c.astype(np.uint8)
        enc = bool(((LX.astype(int) @ c) % 2).any()) if len(LX) else False
        truth = M.rank(np.vstack([hz, c[None, :]])) > rz
        if enc != truth:
            nb += 1
            print("ENCODING MISMATCH", ell, m, A, B)
print("encoding mismatches", nb)
