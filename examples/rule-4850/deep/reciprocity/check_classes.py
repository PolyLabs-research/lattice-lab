"""Check rlib's class values (via the Dickson line polynomials G_k(T) = F(T, D_k(T)) at t_1) against
the census's mod-27 logs: ninth-power pattern for random radius-4 rules, and the three target rules."""
import importlib.util, random, sys
import numpy as np
from rlib import *
spec = importlib.util.spec_from_file_location('census', '/home/user/lattice-lab/examples/rule-4850/census.py')
census = importlib.util.module_from_spec(spec); spec.loader.exec_module(census)
chars = census.characters()

def class_values(F):
    out = []
    for j, k in chars:
        if j == 0:
            Q = subst_line(F, 0)        # F(T, 0) at t_1  (axis: F(t_1, t_0) with t_0 = 0) ; symmetric
        else:
            Q = Q_dickson(F, k)
        out.append(val_t1(Q))
    return out

logs = census.class_logs(4)
rng = random.Random(7)
ids = [4850] + [rng.randrange(1, 1 << 15) for _ in range(400)]
bad = 0
for n in ids:
    assert rule_points(n, 4) == census.rule(n, 4)
    F = rule_F(n, 4)
    vals = class_values(F)
    for c, v in enumerate(vals):
        L = int(logs[c, n])
        if L == census.ZERO:
            ok = v == 0
        else:
            ok = v != 0 and (is_ninth(v) == (L % 9 == 0)) and ((f18_pow(v, N18 // 3) == 1) == (L % 3 == 0))
        if not ok:
            bad += 1
print('radius-4 rules checked:', len(ids), 'disagreements:', bad)
# targets at radius 6 (census rule(n, 6) points)
for n, r in ((4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)):
    assert rule_points(n, r) == census.rule(n, r)
    F = rule_F(n, r)
    vals = class_values(F)
    print(n, 'r', r, 'ninth at all classes:', all(v == 0 or is_ninth(v) for v in vals),
          'log mod 9:', [None if v == 0 else log9(v) for v in vals])
