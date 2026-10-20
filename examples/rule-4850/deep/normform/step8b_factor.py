"""Step 8b: factor 4850, 10491524, 20982139, 178279803 over GF(2), in (a, b) and in (s, P), and the
differences of the relatives from 10491524 (every factorization verified by multiplying back)."""
import sympy as sp
from gf2poly import factor2
import step8_relatives_lib as L
a, b, s_, P_ = L.a, L.b, L.s_, L.P_
for n, r in [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6)]:
    poly = L.rulepoly(n, r)
    sP = L.in_sP(poly)
    print(n, 'in (a,b):', factor2(poly, a, b))
    print('     in (s,P):', factor2(sP, s_, P_))
p0 = L.rulepoly(10491524, 6)
for n in (20982139, 178279803):
    dsP = L.in_sP(L.rulepoly(n, 6) - p0)
    print(n, '- 10491524 in (s,P):', dsP.as_expr(), ' factors:', factor2(dsP, s_, P_))
