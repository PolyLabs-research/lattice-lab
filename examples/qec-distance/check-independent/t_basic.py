import random, time
import numpy as np
import mydist as M
import bb

# convention check vs bb._matrix_rows on several tori and polys, incl. repeats/cancellation
rng = random.Random(1)
for ell, m in [(1, 7), (2, 7), (4, 4), (3, 9), (2, 2), (1, 1), (5, 6)]:
    for _ in range(20):
        P = [(rng.randrange(-3, 2 * ell + 2), rng.randrange(-3, 2 * m + 2)) for _ in range(rng.randint(0, 6))]
        for tr in (False, True):
            rows = bb._matrix_rows(P, ell, m, tr)
            mat = M.mult(P, ell, m)
            if tr:
                mat = mat.T
            mine = [int(sum(int(b) << i for i, b in enumerate(r))) for r in mat]
            assert mine == rows, (ell, m, P, tr)
        # k agrees with bb
        Q = [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(0, 5))]
        assert M.k_of(P, Q, ell, m) == bb.k_linalg(P, Q, ell, m)
print("convention ok")

# toric codes
for ell, m in [(2, 7), (3, 4), (4, 4), (2, 9), (3, 7) if False else (4, 7), (5, 6)]:
    A, B = M.toric(ell, m)
    for kind in "ZX":
        Hc, Hs = M.pair(kind, A, B, ell, m)
        t = time.time()
        dd = M.distance_dfs(Hc, Hs, 2 * ell * m + 1)
        t1 = time.time() - t
        bf = M.distance_brute(Hc, Hs) if M.kernel(Hc).shape[0] <= 28 else None
        t2 = time.time() - t - t1
        print(ell, m, kind, "dfs", dd[0], dd[2], f"{t1:.2f}s", "brute", bf, f"{t2:.2f}s", "expect", min(ell, m))
