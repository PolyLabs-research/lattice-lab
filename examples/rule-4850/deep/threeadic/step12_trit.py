"""Step 12: the one trit left by the reduction of step 11 -- the class (1,3) of 4850.
Its line restriction G_3(T) (lambda(1,3) = G_3(t_1)) factors over GF(2) (pilot 7: t^2 * quintic factor of
Psi_31 * septic factor of Psi_127).  Here: the factorisation, the 3-adic digits of each factor's value at
t_1, and of the other factors of Psi_31, Psi_127 (are the individual partial-cyclotomic factors cubes /
ninth powers?).  Writes step12_trit.json."""
import json
import sympy
import numpy as np
import tlib
from tlib import M
X = sympy.symbols("x")
T_ = sympy.symbols("T")

def sym_reduce(coeffs):
    """symmetric Laurent polynomial sum c_e x^e (dict e -> 1) -> polynomial in T = x + 1/x over GF(2)."""
    # D_n(T) = x^n + x^-n
    D = {0: sympy.Integer(0), 1: T_}
    D[2] = sympy.expand(T_**2)
    def Dn(n):
        if n not in D:
            D[n] = sympy.expand(T_ * Dn(n - 1) + Dn(n - 2))
        return D[n]
    poly = sympy.Integer(0)
    for e, c in coeffs.items():
        if not c or e < 0:
            continue
        poly += 1 if e == 0 else Dn(e)
    return sympy.Poly(poly, T_, modulus=2)

def value_at_t1(P):
    v = 0
    t1 = int(tlib.T[1])
    for c in reversed(P.all_coeffs()):
        pass
    acc = 0
    for c in P.all_coeffs():
        acc = tlib.mul(acc, t1) ^ (int(c) % 2)
    return acc

import sys
sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
import census37 as C
f = C.rule(4850, 4)
coeffs = {}
for p, q in f:
    e = p + 3 * q
    coeffs[e] = coeffs.get(e, 0) ^ 1
G3 = sym_reduce(coeffs)
lam = tlib.logs(tlib.rule_values(4850, 4))[1, 3]
out = {"G3": str(G3.as_expr())}
v = value_at_t1(G3)
print("G_3(t_1) log:", int(tlib.LOG[v]), "lambda(1,3) log:", int(lam), "(must agree)")
fac = sympy.factor_list(G3.as_expr(), modulus=2)
rows = []
for P, e in fac[1]:
    P = sympy.Poly(P, T_, modulus=2)
    lv = int(tlib.LOG[value_at_t1(P)])
    rows.append(dict(factor=str(P.as_expr()), deg=int(P.degree()), mult=int(e), log27=lv % 27, digits=[lv % 3, (lv // 3) % 3, (lv // 9) % 3]))
    print("factor", P.as_expr(), "^%d" % e, "deg", P.degree(), "log mod 27 at t_1:", lv % 27)
out["factors"] = rows
# all factors of Psi_31 and Psi_127 (Phi_e(x) = x^(phi/2) Psi_e(x + 1/x))
for e in (31, 127):
    ph = sympy.Poly(sympy.cyclotomic_poly(e, X), X, modulus=2)
    cf = {i: int(c) % 2 for i, c in enumerate(reversed(ph.all_coeffs()))}
    half = ph.degree() // 2
    psi = sym_reduce({i - half: c for i, c in cf.items() if i >= half})
    fl = sympy.factor_list(psi.as_expr(), modulus=2)
    lst = []
    for P, m in fl[1]:
        P = sympy.Poly(P, T_, modulus=2)
        lv = int(tlib.LOG[value_at_t1(P)])
        lst.append(dict(factor=str(P.as_expr()), log27=lv % 27))
    tot = int(tlib.LOG[value_at_t1(psi)])
    out["Psi%d" % e] = dict(factors=lst, total_log27=tot % 27)
    print("Psi_%d factors' logs mod 27 at t_1:" % e, [x["log27"] for x in lst], "| Psi_%d(t_1) log mod 27:" % e, tot % 27)
json.dump(out, open("step12_trit.json", "w"), indent=1)
