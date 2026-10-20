"""Step 13: on which lines does N = e(4,0)+e(5,2) take values that are products of rule-90 values
t_u = zeta^u + zeta^-u?  For each line (1, k), k = 0..36, and the axis, search products of at most
four t_u (u in 1..18) equal to N(1, k) (exact equality in F(2^18)).  Same for 4850 itself and for
e(1,0) (which is t_{(1+k)/2} t_{(1-k)/2} by the product formula)."""
import itertools
from rlib import *

M = 37
def t(u):
    return val_t1(dickson(u % M if u % M <= 18 else M - u % M)) if u % M else 0

T = {u: t(u) for u in range(1, 19)}
inv = {}
def products(maxlen):
    out = {}
    for r in range(1, maxlen + 1):
        for combo in itertools.combinations_with_replacement(range(1, 19), r):
            v = 1
            for u in combo:
                v = f18_mul(v, T[u])
            out.setdefault(v, combo)
    return out

PR = products(4)
print('distinct products of <= 4 rule-90 values:', len(PR))

def Nval(F, k):
    return val_t1(subst_line(F, 0)) if k is None else val_t1(Q_dickson(F, k))

Nset = set()
for o in ((4, 0), (5, 2)):
    Nset ^= orbit_F(o)
for name, F in (('N', frozenset(Nset)), ('4850', rule_F(4850, 4)), ('e(1,0)', orbit_F((1, 0)))):
    res = {}
    for k in [None] + list(range(37)):
        v = Nval(F, k)
        res['axis' if k is None else k] = 'zero' if v == 0 else PR.get(v)
    print(name, res)
