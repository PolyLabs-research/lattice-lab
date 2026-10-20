"""Step 20: class statistics inside the structured family V (rules f of radius <= 12 with f*e(1,0)
invariant under R3 mod 37; 2047 rules), to calibrate how much the structure explains.
For each tie group (axis+(1,7); (1,1); (1,4)+(1,6); B = (1,2),(1,8),(1,10); C = (1,3),(1,5),(1,13))
the fraction of rules whose class there is a ninth power (zero counts as ninth), and joint counts."""
import itertools
import numpy as np
from rlib import *
from step18_subspace import solve_space, classes9

R3 = (18, 29, 29, 18)
for label, Dpts, Mt, R in [('4850 frame: D = e(1,0), M = R3', points((1, 0)), R3, 12),
                           ('axis frame: D = e(1,1), M = diag(10,26)', points((1, 1)), (10, 0, 0, 26), 12)]:
    orbs, basis = solve_space(Dpts, Mt, R)
    B = np.array(basis, dtype=np.uint8)
    rows = []
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
        rows.append([c is None or c % 9 == 0 for c in cl])
    A = np.array(rows)
    names = ['axis', '(1,1)', '(1,2)', '(1,3)', '(1,4)', '(1,5)', '(1,6)', '(1,7)', '(1,8)', '(1,10)', '(1,13)']
    print(label, ': rules', len(A))
    print('   per-class ninth-power rates:', {n: round(float(A[:, i].mean()), 3) for i, n in enumerate(names)})
    if label.startswith('4850'):
        groups = {'A': 0, 'diag': 1, 'D': 4, 'B': 2, 'C': 3}
    else:
        groups = {n: i for i, n in enumerate(names)}
    rates = {g: float(A[:, i].mean()) for g, i in groups.items()}
    pred = np.prod(list(rates.values())) * len(A)
    allc = int(A.all(axis=1).sum())
    print('   group rates:', {g: round(r, 3) for g, r in rates.items()}, ' independent-model expected confined:',
          round(float(pred), 2), ' observed:', allc)
    if label.startswith('4850'):
        others = A[:, [0, 1, 2, 4]].all(axis=1)
        print('   rules ninth at every group except C:', int(others.sum()), ' of these, also ninth at C:', int((others & A[:, 3]).sum()))
