import random, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
import mydist as M
rng = random.Random("checker-independent encoding X")
bad = tot = 0
for trial in range(40):
    ell, m = rng.choice([(1, 7), (2, 7), (4, 4), (2, 9), (3, 9), (5, 6), (4, 7), (6, 7)])
    A = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 5))]
    B = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 5))]
    M.guard(A, B, ell, m)
    hx, hz = D.check_matrices(A, B, ell, m)
    for kind, Hc, Hs, det in (("Z", hx, hz, "X"), ("X", hz, hx, "Z")):
        L = D.logical_basis(A, B, ell, m, det)
        K = M.kernel(Hc); rs = M.rank(Hs)
        for _ in range(30):
            if rng.random() < 0.4:
                c = (np.array([rng.randrange(2) for _ in range(Hs.shape[0])]) @ Hs) % 2
            else:
                c = (np.array([rng.randrange(2) for _ in range(K.shape[0])]) @ K) % 2
            c = c.astype(np.uint8)
            enc = bool(((L.astype(int) @ c) % 2).any()) if len(L) else False
            truth = M.rank(np.vstack([Hs, c[None, :]])) > rs
            tot += 1; bad += enc != truth
print("checked", tot, "mismatches", bad)
