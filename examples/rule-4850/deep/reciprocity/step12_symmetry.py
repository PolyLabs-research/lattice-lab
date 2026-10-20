"""Step 12: the full GL2(Z/37) symmetry groups of N = e(4,0)+e(5,2) (rule 132096), of 4850, of
e(1,0) (rule 2) and of the rotated G = e(4,4)+e(7,3), and what they force on the classes:
pilot 7's tools/chance.py (full_symmetries, partition, analyse), run on our rules.
Also the class values (logs mod 27 via our full log table) of N, e(1,0) and 4850."""
import sys
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
import chance
import numpy as np
from rlib import rule_points, rule_F, orbit_F, points, subst_line, Q_dickson, val_t1, log9
from fulllog import log_table, CLASS_K, class_value

def pts(*orbs):
    out = set()
    for o in orbs:
        out ^= points(o)
    return frozenset(out)

def Fset(*orbs):
    out = set()
    for o in orbs:
        out ^= orbit_F(o)
    return frozenset(out)

LOG = log_table()
cases = {
    'N = e(4,0)+e(5,2)': (pts((4, 0), (5, 2)), Fset((4, 0), (5, 2))),
    '4850': (rule_points(4850, 4), rule_F(4850, 4)),
    'e(1,0) = rule 2': (pts((1, 0)), Fset((1, 0))),
    'G = e(4,4)+e(7,3)': (pts((4, 4), (7, 3)), Fset((4, 4), (7, 3))),
}
for name, (f, F) in cases.items():
    sym = chance.full_symmetries(f, 37)
    parts = chance.partition(37, sym)
    logs = [None if class_value(F, k) == 0 else int(LOG[class_value(F, k)]) % 27 for k in CLASS_K]
    print(f'{name}: |Sym| = {len(sym)}; classes under Sym+Frobenius: {len(parts)}')
    print('    (rep, size, forced degree):', [(p[0], p[1], p[2]) for p in parts])
    print('    census-class logs mod 27:', logs)
