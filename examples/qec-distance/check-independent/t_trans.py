"""The premise of the translation row, on the builder's own matrices: T_g commutes with H_X and
H_Z (block-diagonal shift), so T_g preserves ker and rowspaces; and Phi swaps them."""
import random, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import distance as D
import mydist as M
rng = random.Random("checker-independent translation")
cnt = 0
for _ in range(40):
    ell, m = rng.choice([(1, 7), (2, 7), (4, 4), (2, 9), (3, 9), (5, 6), (4, 7), (6, 7), (1, 1), (2, 2)])
    A = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(0, 5))]
    B = [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(0, 5))]
    M.guard(A, B, ell, m)
    hx, hz = D.check_matrices(A, B, ell, m)
    lm = ell * m
    for a in range(ell):
        for b in range(m):
            T = M.mult([(a, b)], ell, m)  # shift by x^a y^b
            TT = np.zeros((2 * lm, 2 * lm), dtype=np.uint8); TT[:lm, :lm] = T; TT[lm:, lm:] = T
            for H in (hx, hz):
                assert np.array_equal((H.astype(int) @ TT) % 2, (T.astype(int) @ H) % 2)
            cnt += 1
    P, Phi = D.inversion_swap(ell, m)
    assert np.array_equal((P.astype(int) @ hx @ Phi) % 2, hz)
print("translations checked", cnt)
