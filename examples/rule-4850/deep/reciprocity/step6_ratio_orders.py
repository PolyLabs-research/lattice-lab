"""The ratios of class values among 10491524 (4850 rotated), 20982139 and 178279803: their orders
and their p-parts for p | 2^18 - 1 = 3^3 * 7 * 19 * 73, class by class (census representatives),
and the same for every line (1, k), k in Z/37, and the axis (0, 1)."""
from rlib import *
import sympy

def order(v):
    o = N18
    for p in (3, 7, 19, 73):
        while o % p == 0 and f18_pow(v, o // p) == 1:
            o //= p
    return o

KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
base = rule_F(10491524, 6)
for n in (20982139, 178279803, 4850):
    F = rule_F(n, 6 if n > 10**6 else 4)
    out = []
    for k in KS + [0]:
        a = val_t1(Q_dickson(base, k)) if k else val_t1(subst_line(base, 0))
        b = val_t1(Q_dickson(F, k)) if k else val_t1(subst_line(F, 0))
        rho = f18_mul(b, f18_pow(a, N18 - 1))
        out.append((k if k else 'axis', sympy.factorint(order(rho))))
    print(f'{n}/10491524 orders per class:', out)

# all lines k = 0..36 (character (1,k)) using the exponent form, for completeness
def lineval(F, k):
    return val_t1(Q_dickson(F, k)) if k else val_t1(subst_line(F, 0))

for n in (20982139, 178279803):
    F = rule_F(n, 6)
    os = set()
    for k in range(37):
        rho = f18_mul(lineval(F, k), f18_pow(lineval(base, k), N18 - 1))
        os.add(order(rho))
    print(n, 'set of ratio orders over all 37 lines (1,k):', sorted(os), [sympy.factorint(o) for o in sorted(os)])
