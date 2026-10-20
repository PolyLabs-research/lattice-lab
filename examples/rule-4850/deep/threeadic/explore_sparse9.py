"""Explicit sparse mod-9 solutions found in step 5 for 4850 and 43250486 (all solutions by brute force)."""
import itertools, numpy as np
from step5_support import Phi_matrix, logt_classes, ORB_VECS
import sbasis, tlib
P9 = Phi_matrix(9)
for n, r, T, V in ((4850, 4, [0, 1, 7], [1]), (43250486, 6, [1, 7], [1]), (482758, 5, [0, 1, 7], [1]),
                   (8438150, 6, [0, 1, 7], [1]), (10491524, 6, [0, 1, 9], [0])):
    t9 = logt_classes(n, r, 9)
    cls = [c for c in range(11) if c not in V and c != 6]
    sols = []
    for ell in itertools.product(range(9), repeat=len(T)):
        if all((sum(e * P9[o, c] for e, o in zip(ell, T)) + t9[c]) % 9 == 0 for c in cls):
            sols.append(ell)
    print(n, "T =", [sbasis.ORBIT_REP[o] for o in T], "vectors", [ORB_VECS[o] for o in T], "V =", [tlib.CENSUS_REPS[c] for c in V])
    print("   log_t f mod 9 per class:", t9)
    print("   solutions ell (mod 9):", sols)
    print("   Phi rows (mod 9):", [P9[o].tolist() for o in T])
