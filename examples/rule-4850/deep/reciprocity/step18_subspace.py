"""Step 18: the family of rules sharing 4850's structure, and tests (b) and (d).

Structure: f * D is invariant (mod 37) under a matrix M whose eigenvalues lie in {10, 26} (the cube
roots of 1 mod 37, = -2^6 and 2^12), with D split along M's eigenvectors.  Then
f(M^T c)/f(c) = D(c)/D(M^T c) is a 63rd power at every character, so f's classes mod 9 are
M-invariant (a 'twisted symmetry').  For 4850: D = e(1,0) = t_u t_v in the diagonal coordinates
u = (j+k)/2, v = (j-k)/2, and M = R3 = [[18,-8],[-8,18]] (R3 (1,1) = 10 (1,1), R3 (1,-1) = 26 (1,-1)).
The condition f*D = (f*D) o M is linear in f; we solve it over the D4-orbits of radius <= R and
enumerate the solution space V.  For each f in V we compute the 11 class logs mod 9 and check:
  (d) soundness: classes in the same R3-orbit {axis,(1,7)}, {(1,4),(1,6)}, {(1,2),(1,8),(1,10)},
      {(1,3),(1,5),(1,13)} have the SAME ninth-power status whenever D is nonzero there (theorem);
  (b) how often f in V is ninth-power confined, against the 1/9-per-class baseline.
Also the analogous structure in the axis frame: D = ab = e(1,1) and M = diag(10, 26)."""
import sys, itertools, json, time
import numpy as np
from rlib import *
from gring import elem, mul, dil
from gf2lin import kernel

M37 = 37
CLASS_K = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
NAMES = ['axis'] + [f'(1,{k})' for k in CLASS_K[1:]]

def apply_mat(a, Mt):
    """a o M: the element with support {M s : s in supp a} (column action)"""
    A, B, C, D = Mt
    out = np.zeros((M37, M37), dtype=np.uint8)
    for p, q in zip(*np.nonzero(a)):
        out[(A * p + B * q) % M37, (C * p + D * q) % M37] ^= 1
    return out

def classes9(Fset):
    out = []
    for k in CLASS_K:
        v = val_t1(subst_line(Fset, 0)) if k == 0 else val_t1(Q_dickson(Fset, k))
        out.append(None if v == 0 else log9(v))
    return out

def solve_space(Dpts, Mt, R):
    orbs = orbits(R)
    Del = elem(Dpts)
    cols = []
    for o in orbs:
        e = elem(points(o))
        P = mul(e, Del)
        cols.append((P ^ apply_mat(P, Mt)).reshape(-1))
    A = np.array(cols, dtype=np.uint8).T
    return orbs, kernel(A)

def run(label, Dpts, Mt, R, ties):
    t0 = time.time()
    orbs, basis = solve_space(Dpts, Mt, R)
    print(f'{label}: radius <= {R}: {len(orbs)} orbits, solution space dimension {len(basis)}')
    B = np.array(basis, dtype=np.uint8) if basis else np.zeros((0, len(orbs)), dtype=np.uint8)
    n_conf, n_tot, viol, n_cube = 0, 0, 0, 0
    conf_list = []
    Dcls = classes9(frozenset().union(*[]) if False else set())  # placeholder
    for coeffs in itertools.product((0, 1), repeat=len(basis)):
        if not any(coeffs):
            continue
        x = np.zeros(len(orbs), dtype=np.uint8)
        for c, b in zip(coeffs, B):
            if c:
                x ^= b
        Fset = set()
        for i in np.flatnonzero(x):
            Fset ^= orbit_F(orbs[i])
        cl = classes9(frozenset(Fset))
        n_tot += 1
        # soundness: within each tie group, ninth-power status must agree (where nonzero)
        for grp in ties:
            st = {cl[i] % 9 == 0 for i in grp if cl[i] is not None}
            if len(st) > 1:
                viol += 1
                break
        if all(c is None or c % 9 == 0 for c in cl):
            n_conf += 1
            rid = sum(1 << orbits(8).index(orbs[i]) for i in np.flatnonzero(x)) if R <= 8 else None
            conf_list.append((rid, [orbs[i] for i in np.flatnonzero(x)]))
        if all(c is None or c % 3 == 0 for c in cl):
            n_cube += 1
    print(f'   rules in V: {n_tot}; tie violations: {viol}; ninth-power confined: {n_conf}; cube-confined: {n_cube}  ({time.time() - t0:.0f}s)')
    for rid, ob in conf_list[:40]:
        print('     confined:', rid, ob)
    return n_tot, n_conf, viol

if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    R3 = (18, 29, 29, 18)  # [[18,-8],[-8,18]]
    ties_diag = [[0, 7], [4, 6], [2, 8, 9], [3, 5, 10]]  # census indices: axis=0,(1,1)=1,(1,2)=2,...
    run('D = e(1,0), M = R3', points((1, 0)), R3, R, ties_diag)
    # the axis frame: D = e(1,1) = ab, M = diag(10, 26) and diag(26, 10)
    run('D = e(1,1), M = diag(10,26)', points((1, 1)), (10, 0, 0, 26), R, [])
    run('D = e(1,1), M = diag(26,10)', points((1, 1)), (26, 0, 0, 10), R, [])
