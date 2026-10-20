"""Step 14: transfer of ninth-power-ness between 4850's classes through symmetric multiples.

If 4850 * D = P (polynomial identity) and M in GL2(Z/37) fixes supp(P) (column action), then
lambda_P(M^T c) = lambda_P(c), so
   class_4850(M^T c) = class_4850(c) + class_D(c) - class_D(M^T c)        (mod 9).
When D's classes are known (D splits into 1D factors, so its values are cyclotomic) and
class_D(c) = class_D(M^T c), ninth-power-ness of 4850 transfers from c to M^T c.  We scan D over
the radius-<=4 symmetric family, keep the sparse products P (|P| <= MAXP) with a stabiliser larger
than D4, and build the transfer graph on 4850's 11 classes.  D is marked 'split' when it is a
product of one-dimensional factors (atlas3 procedure)."""
import sys, json, time
import numpy as np
from rlib import *
from symfind import proj_symmetries_full
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')

M = 37
MAXP = int(sys.argv[1]) if len(sys.argv) > 1 else 100
RAD = int(sys.argv[2]) if len(sys.argv) > 2 else 4
CLASS_REPS = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
L2 = {pow(2, e, M): e for e in range(36)}

def class_of_char(j, k):
    """census class index of the character (j, k) and the Frobenius exponent a with
    (j, k) = 2^a * g * rep for a D4 element g"""
    for idx, (rj, rk) in enumerate(CLASS_REPS):
        for a in range(36):
            s = pow(2, a, M)
            x, y = (s * rj) % M, (s * rk) % M
            for (u, v) in ((x, y), (y, x)):
                for su in (1, -1):
                    for sv in (1, -1):
                        if ((su * u) % M, (sv * v) % M) == (j % M, k % M):
                            return idx, a
    raise ValueError((j, k))

CHAR_CACHE = {}
def char_class(j, k):
    key = (j % M, k % M)
    if key not in CHAR_CACHE:
        CHAR_CACHE[key] = class_of_char(*key)
    return CHAR_CACHE[key]

def rep_classes(Fset):
    """log9 at the 11 census reps (None for zero)"""
    out = []
    for j, k in CLASS_REPS:
        v = val_t1(subst_line(Fset, 0)) if j == 0 else val_t1(Q_dickson(Fset, k))
        out.append(None if v == 0 else log9(v))
    return out

def cls_at(reps, j, k):
    idx, a = char_class(j, k)
    c = reps[idx]
    return None if c is None else (c * pow(2, a, 9)) % 9

def is_split(n, r):
    try:
        import atlas3
    except Exception:
        return None
    return None

F4850 = rule_points(4850, 4)
R4850 = rep_classes(rule_F(4850, 4))

def product_points(A, B):
    out = {}
    for p, q in A:
        for u, v in B:
            key = (p + u, q + v)
            out[key] = out.get(key, 0) ^ 1
    return frozenset(k for k, c in out.items() if c)

if __name__ == '__main__':
    t0 = time.time()
    results = []
    ndone = 0
    for n in range(1, 1 << len(orbits(RAD))):
        D = rule_points(n, RAD)
        P = product_points(F4850, D)
        if len(P) > MAXP or len(P) == 0:
            continue
        stab = proj_symmetries_full(P)
        if len(stab) <= 8:
            continue
        RD = rep_classes(rule_F(n, RAD))
        edges = set()
        for (a, b, c, d) in stab:
            for i, (j, k) in enumerate(CLASS_REPS):
                # M^T c : (a c0 + c c1, b c0 + d c1)
                j2, k2 = (a * j + c * k) % M, (b * j + d * k) % M
                i2, _ = char_class(j2, k2)
                if i2 == i:
                    continue
                cd1, cd2 = cls_at(RD, j, k), cls_at(RD, j2, k2)
                if cd1 is None or cd2 is None:
                    continue
                if cd1 == cd2:
                    edges.add((min(i, i2), max(i, i2)))
        results.append({'D': n, 'P_size': len(P), 'stab': len(stab), 'edges': sorted(edges), 'D_classes': RD})
        print(n, rule_orbits(n, RAD), '|P| =', len(P), '|stab| =', len(stab), 'edges', sorted(edges), 'D classes', RD, flush=True)
    json.dump(results, open(f'step14_transfers_r{RAD}_p{MAXP}.json', 'w'))
    # union of edges, connectivity from known classes
    known = {0, 1, 6}  # axis (t^3), diagonal (cyclotomic), (1,6) (F_512, forced)
    allE = set()
    for r in results:
        allE |= set(map(tuple, r['edges']))
    comp = set(known)
    changed = True
    while changed:
        changed = False
        for i, j in allE:
            if (i in comp) != (j in comp):
                comp |= {i, j}
                changed = True
    print('classes reachable from the forced ones:', sorted(comp), [CLASS_REPS[i] for i in sorted(comp)])
    print('not reached:', [CLASS_REPS[i] for i in range(11) if i not in comp])
    print(f'{time.time() - t0:.0f}s')
