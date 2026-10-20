"""Step 10b: G = e(4,4)+e(7,3) is divisible by F(10491524); the quotient K, and the same for
G' = e(3,3)+e(7,4) by F(20982139) and G'' = e(7,7)+e(4,3) by F(178279803).  Exact division in
GF(2)[a, b] (sympy div with modulus 2 and zero remainder)."""
from sympy import symbols, Poly, div, factor_list
from rlib import *
a, b = symbols('a b')

def P(Fset):
    return Poly(sum(a**i * b**j for i, j in Fset), a, b, modulus=2)

def orbsum(*orbs):
    out = set()
    for o in orbs:
        out ^= orbit_F(o)
    return P(out)

F1, F2, F3 = P(rule_F(10491524, 6)), P(rule_F(20982139, 6)), P(rule_F(178279803, 6))
F4850 = P(rule_F(4850, 4))
G, G1, G2 = orbsum((4, 4), (7, 3)), orbsum((3, 3), (7, 4)), orbsum((7, 7), (4, 3))
for name, num, den in [('G/F1', G, F1), ("G'/F2", G1, F2), ("G''/F3", G2, F3)]:
    q, r = div(num, den)
    print(name, '= ', q.as_expr(), '   remainder zero:', r.is_zero)
# univariate factor of K
q, r = div(G, F1)
print('K as expression:', q.as_expr())
# K in terms of a, b: factor via substitution b = a (diagonal) and b = 0 for orientation
print('K(a, 0) =', Poly(q.as_expr().subs(b, 0), a, modulus=2).factor_list())
print('K(a, a) =', Poly(q.as_expr().subs(b, a), a, modulus=2).factor_list())
print('G =', G.as_expr())
