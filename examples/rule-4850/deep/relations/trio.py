"""
The relation found by ext6.py among 10491524, 20982139 and 178279803, verified exactly.

Claim (off the axis class): with sigma the dilation (x, y) -> (x^10, y^10), i.e. the Frobenius
x -> x^(2^6) (2^6 = 64 = 27 = -10 mod 37; 10 is a primitive cube root of 1 mod 37), and
U = 18436 = ab(1+a)(1+b)(1+a+a^2)(1+b+b^2) (a pure line-unit product),
    20982139  =  sigma(10491524)   * U(x^4, y^4)       * B1,
    178279803 =  sigma^2(10491524) * U(x^32, y^32)     * B2,
B1, B2 F(2^9)-valued, at every character where U is nonzero (everything but the axis class).
In the group ring this is the log-free identity, for G = 20982139 and P = 10491524(x^27) U(x^4):
    G(x^512) P = G P(x^512)      in F2[x,y]/(x^37 - 1, y^37 - 1)
(both sides vanish where U does). The script checks:
  1. the exact polynomial identity U = ab(1+a)(1+b)(1+a+a^2)(1+b+b^2);
  2. the group-ring identities for both rules (and the 873 / 27268 variants);
  3. the same at all 1369 characters by eigenvalues in eigen.py's own field (independent code);
  4. the log form: L(g) - 2^(6j) L(10491524) = c * L(ab) on the off-axis classes, c a multiple of 9;
  5. the axis classes: 20982139, 178279803 and 10491524 restrict to cyclotomic polynomials in t.

    python trio.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util  # noqa: E402

import ab_forms  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "atlas_eigen", "/home/user/lattice-lab/examples/linear-atlas-3/eigen.py")
eigen = importlib.util.module_from_spec(_spec)  # the independent checker, by path
sys.path.insert(0, "/home/user/lattice-lab/examples/linear-atlas-3")
_spec.loader.exec_module(eigen)
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402

C = tables.C
M = 37


def dense(n):
    return S.dense(RT.expset(n))


def dil(A, d):
    return S.dilate(A, d % M)


def gr_identity(g, f, gp_f, u, dp_u):
    """G(x^512) P = G P(x^512) with P = f(x^(2^gp_f)) u(x^(2^dp_u))."""
    G = dense(g)
    P = S.gmul(dil(dense(f), pow(2, gp_f, M)), dil(dense(u), pow(2, dp_u, M)))
    s = 512 % M
    return bool((S.gmul(dil(G, s), P) == S.gmul(G, dil(P, s))).all())


def eig_check(g, f, gp_f, u, dp_u):
    """at all 1369 characters, in eigen.py's field: (l_g / (l_f^(2^gp) l_u^(2^dp)))^511 = 1
    wherever l_u != 0; returns (#characters checked, #failures, #characters with l_u = 0)."""
    mod, d = eigen.field(M)
    mul = lambda x, y: eigen._mul(x, y, mod, d)  # noqa: E731
    pw = lambda x, e: eigen._pow(x, e, mod, d)  # noqa: E731
    zeta = [pw(2, e) for e in range(M)]
    G, F, U = RT.expset(g), RT.expset(f), RT.expset(u)

    def val(h, j, k):
        v = 0
        for p, q in h:
            v ^= zeta[(p * j + q * k) % M]
        return v

    checked = fail = uzero = 0
    for j in range(M):
        for k in range(M):
            vg, vf, vu = val(G, j, k), val(F, j, k), val(U, j, k)
            if vu == 0:
                uzero += 1
                continue
            if vg == 0 or vf == 0:
                fail += (vg == 0) != (vf == 0)
                continue
            lhs = pw(vg, 511)
            rhs = pw(mul(pw(vf, 2**gp_f), pw(vu, 2**dp_u)), 511)
            checked += 1
            fail += lhs != rhs
    return checked, fail, uzero


def main():
    a, b = sympy.symbols("a b")
    U = ab_forms.ab_poly(18436).as_expr()
    rhs = sympy.expand(a * b * (1 + a) * (1 + b) * (1 + a + a**2) * (1 + b + b**2))
    ok = sympy.Poly(U - rhs, a, b, modulus=2).is_zero
    print("1. 18436 = ab(1+a)(1+b)(1+a+a^2)(1+b+b^2) exactly:", ok)
    print("   2^6 mod 37 =", pow(2, 6, M), "; 10^3 mod 37 =", pow(10, 3, M))

    rels = [  # (g, f, gp_f, u, dp_u): g = f^(2^gp_f) u^(2^dp_u) * F(2^9) off the axis
        (20982139, 10491524, 6, 18436, 2),
        (178279803, 10491524, 12, 18436, 5),
    ]
    # the ext6 hits also give 873 (zero-free) and 27268 in place of 18436; derive their twists
    L = tables.L5()
    off = S.MODES["off"]
    Lf = {n: tables.logs513(RT.expset(n)).astype(np.int64) for n in (10491524, 20982139, 178279803)}
    for g, gpf in ((20982139, 6), (178279803, 12)):
        for u in (873, 27268):
            for dp in range(18):
                v = (Lf[g] - pow(2, gpf, 513) * Lf[10491524] - pow(2, dp, 513) * L[:, u]) % 513
                if (v[off] == 0).all():
                    rels.append((g, 10491524, gpf, u, dp))
    print("2./3. relations (g = f^(2^gp) u^(2^dp) F(2^9) where u != 0):")
    for g, f, gp, u, dp in rels:
        gr = gr_identity(g, f, gp, u, dp)
        ec = eig_check(g, f, gp, u, dp)
        print(f"   {g} = {f}^(2^{gp}) * {u}^(2^{dp}) * F(2^9): group-ring identity {gr};"
              f" eigenvalues at 1369 characters (checked, failures, u = 0): {ec}")

    # 4. the log form with the unit ab (rule 4)
    lab = L[:, 4].astype(np.int64)
    for g, gpf in ((20982139, 6), (178279803, 12)):
        diff = (Lf[g] - pow(2, gpf, 513) * Lf[10491524]) % 513
        cs = [c for c in range(513) if (((c * lab - diff) % 513)[[1, 2, 3, 4, 5, 7, 8, 9, 10]] == 0).all()]
        print(f"4. L({g}) - 2^{gpf} L(10491524) = c L(ab) on all classes but the axis, c =", cs,
              "(c mod 9 =", [c % 9 for c in cs], "); difference vector:", diff.tolist())
    # 5. axis restrictions F(0, t)
    t = sympy.symbols("t")
    for n in (10491524, 20982139, 178279803, 4850):
        P = ab_forms.ab_poly(n).as_expr().subs(a, 0)
        print(f"5. axis of {n}: F(0,t) =", sympy.factor_list(sympy.expand(P.subs(b, t)), modulus=2))
    for e in (3, 5, 7, 9, 13):
        z = sympy.symbols("z")
        phi = sympy.cyclotomic_poly(e, z)
        # Psi_e(z + 1/z) = z^(-phi/2) Phi_e(z): recover Psi_e by matching
        deg = sympy.degree(phi, z) // 2
        cs = sympy.symbols(f"c0:{deg + 1}")
        cand = sum(cs[i] * (z + 1 / z) ** i for i in range(deg + 1))
        eqs = sympy.Poly(sympy.expand((cand - phi / z**deg) * z**deg), z).all_coeffs()
        sol = sympy.solve(eqs, cs, dict=True)[0]
        psi = sympy.Poly(sum(int(sol[cs[i]]) % 2 * t**i for i in range(deg + 1)), t, modulus=2)
        print(f"   Psi_{e}(t) =", psi.as_expr())


if __name__ == "__main__":
    main()
