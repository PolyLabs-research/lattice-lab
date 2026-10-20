"""The D4-symmetric Legendre basis at the class level.

For a direction orbit O (D4 acting on projective directions w), S_O(c) = sum_{g in D4} chi((g w_O) . c),
a D4-invariant, scaling-odd function of the character c (S_O(uc) = chi(u) S_O(c)).  Evaluated at the
11 census class representatives and reduced mod 3 it gives an 11 x 11 matrix over Z/3 (rows: the
direction orbits in the order of step2_transform, columns: census classes).  The (6, 1) orbit gives
S = 0 identically (chi(6) = -1), class (1, 6) is forced 0, and the other ten rows are a basis of
the symmetric odd functions (checked: rank 10).  A digit vector d on the classes is written uniquely
as d = sum_O eps_O S_O; the weight of d is the number of orbits with eps_O != 0.
"""
import numpy as np

import tlib
from tlib import M, chi, LINES

D4 = [(lambda p, q, a=a, b=b, s=s: ((a * (q if s else p)), (b * (p if s else q))))
      for a in (1, -1) for b in (1, -1) for s in (0, 1)]


def direction_orbits():
    seen, orbs = set(), []
    for wi, w in enumerate(LINES):
        if wi in seen:
            continue
        orb = set()
        for g in D4:
            li, _ = tlib.line_of(*g(*w))
            orb.add(li)
        seen |= orb
        orbs.append(sorted(orb))
    return orbs


ORBITS = direction_orbits()
ORBIT_REP = [LINES[o[0]] for o in ORBITS]
SHORT = {(1, 0): "(1,0)", (0, 1): "(1,0)"}


def S_function(w0):
    """S_O as a 37 x 37 array of integers (sum of chi over the 8 D4 images of w0)."""
    out = np.zeros((M, M), dtype=np.int64)
    for g in D4:
        w = g(*w0)
        out += chi[(w[0] * tlib.JJ + w[1] * tlib.KK) % M]
    return out


def S_matrix():
    """rows: orbits, columns: census classes, entries mod 3."""
    S = np.zeros((len(ORBITS), 11), dtype=np.int64)
    for oi, w0 in enumerate(ORBIT_REP):
        F = S_function(w0)
        for ci, (j, k) in enumerate(tlib.CENSUS_REPS):
            S[oi, ci] = F[j, k] % 3
    return S


def solve_mod3(S, d):
    """eps with eps @ S = d (mod 3), using rows != (6,1)-orbit; returns None if inconsistent."""
    rows = [i for i in range(S.shape[0]) if S[i].any()]
    A = S[rows].T % 3  # 11 x 10: d = A eps
    aug = np.concatenate([A, np.asarray(d).reshape(-1, 1) % 3], axis=1)
    n, m = A.shape
    r = 0
    piv = []
    aug = aug.copy()
    for c in range(m):
        p = next((i for i in range(r, n) if aug[i, c] % 3), None)
        if p is None:
            continue
        aug[[r, p]] = aug[[p, r]]
        aug[r] = (aug[r] * aug[r, c]) % 3  # inverse of 1 is 1, of 2 is 2
        for i in range(n):
            if i != r and aug[i, c]:
                aug[i] = (aug[i] - aug[i, c] * aug[r]) % 3
        piv.append(c)
        r += 1
    if any(aug[i, m] for i in range(r, n)):
        return None
    eps = np.zeros(S.shape[0], dtype=np.int64)
    for i, c in enumerate(piv):
        eps[rows[c]] = aug[i, m]
    return eps


def inverse_map(S):
    """a 11 x 11 integer matrix P with eps = d @ P (mod 3) for every consistent d (d[(1,6)] = 0)."""
    P = np.zeros((11, S.shape[0]), dtype=np.int64)
    for ci in range(11):
        if ci == 6:
            continue
        d = np.zeros(11, dtype=np.int64)
        d[ci] = 1
        e = solve_mod3(S, d)
        assert e is not None
        P[ci] = e
    return P


if __name__ == "__main__":
    S = S_matrix()
    print("orbit reps:", ORBIT_REP)
    print(S)
    import sympy
    print("rank mod 3:", sympy.Matrix(S).rank(iszerofunc=lambda x: x % 3 == 0))
