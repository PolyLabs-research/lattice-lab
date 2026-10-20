"""Step 22: can class C = {(1,3),(1,5),(1,13)} be tied to another class through a multiple of 4850
by a unit whose eigenvalues are all ninth powers?  If 4850 * U = P with U ninth-power valued
(rule-150 type factors 1 + t along lines) and M fixes supp(P), then 4850's ninth-power status is
M-invariant, whatever M is.  We take U among products of the line units
   L(p,q) = prod over the D4-images (p',q') of the line of (1 + x^p' y^q' + x^-p' y^-q')
for directions (p,q) in {(1,0), (1,1), (2,1), (3,1), (3,2)} with multiplicities 0..2 (and the
same times e(1,0)), compute P = 4850 * U and the full stabiliser of supp(P) mod 37, and report every
stabiliser larger than D4 together with the classes it ties."""
import itertools, math, time
import numpy as np
from rlib import rule_points, points
from step21_other_sizes import stab
from step14_transfers import char_class, CLASS_REPS

M = 37
def lmul(A, B):
    out = {}
    for p, q in A:
        for u, v in B:
            k = (p + u, q + v)
            out[k] = out.get(k, 0) ^ 1
    return frozenset(k for k, c in out.items() if c)

def line_unit(p, q):
    """D4-symmetric product of Phi_3 along the lines of (p, q)"""
    dirs = set()
    for (u, v) in {(p, q), (p, -q), (q, p), (q, -p)}:
        if (-u, -v) not in dirs:
            dirs.add((u, v))
    U = frozenset({(0, 0)})
    for u, v in dirs:
        U = lmul(U, frozenset({(u, v), (0, 0), (-u, -v)}))
    return U

F = rule_points(4850, 4)
E10 = points((1, 0))
atoms = {d: line_unit(*d) for d in [(1, 0), (1, 1), (2, 1), (3, 1), (3, 2)]}
t0 = time.time()
found = []
names = list(atoms)
for mults in itertools.product(range(3), repeat=len(names)):
    if sum(mults) > 3:
        continue
    for with_e in (False, True):
        U = frozenset({(0, 0)})
        for d, k in zip(names, mults):
            for _ in range(k):
                U = lmul(U, atoms[d])
        if with_e:
            U = lmul(U, E10)
        P = lmul(F, U)
        if len(P) > 700:
            continue
        st = stab(P, M)
        if st and len(st) > 8:
            ties = set()
            for (a, b, c, d) in st:
                for i, (j, k) in enumerate(CLASS_REPS):
                    i2, _ = char_class((a * j + c * k) % M, (b * j + d * k) % M)
                    if i2 != i:
                        ties.add((min(i, i2), max(i, i2)))
            found.append((mults, with_e, len(P), len(st), sorted(ties)))
            print('U =', dict(zip(names, mults)), '* e(1,0)' if with_e else '', '|P| =', len(P), '|Stab| =', len(st), 'ties', sorted(ties), flush=True)
print(f'scanned in {time.time() - t0:.0f}s; hits: {len(found)}')
