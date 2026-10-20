"""
Step 4c: is the mu_19 relation R3 R1^7 = R2^8 (mod F(2^9)-valued, off the axis lines) chance?

* Null 1: random unit rules of radius 6 (triples): the best linear relation c1 v1 + c2 v2 + c3 v3 = 0
  (mod 19) over the 38 lines, and on how many lines it holds.
* Null 2: (R1, R2, X) and (R1, X, R3) with X random radius-6 rules.
* The group-ring element Z = R3 sigma_8(R1) / (R1 sigma_8(R2)): Z^511 (the F(2^9) test) on all lines,
  and the axis restrictions F_i(0, b) of the three rules, factored over GF(2).
Writes mu19_calib.json.
"""
import itertools
import json
import os
import sys

import numpy as np
import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
LINES = [(1, k) for k in range(M)] + [(0, 1)]
REL = [c for c in itertools.product(range(19), repeat=3) if c != (0, 0, 0) and next(x for x in c if x) == 1]


def vec(f):
    ll = [f18.log(gr.eig(f, *jk)) for jk in LINES]
    if any(x is None for x in ll):
        return None
    return np.array([x % 19 for x in ll])


def best(V):
    A = np.array(REL)  # (381, 3)
    S = (A @ np.stack(V)) % 19  # (381, 38)
    k = (S == 0).sum(axis=1)
    i = int(k.argmax())
    return int(k[i]), tuple(int(x) for x in A[i])


def main():
    out = {}
    f18.full_log_table()
    R1, R2, R3 = (gr.rule_array(n) for n in (10491524, 20982139, 178279803))
    V1, V2, V3 = vec(R1), vec(R2), vec(R3)
    out["observed"] = best([V1, V2, V3])
    print("observed best relation:", out["observed"])
    rng = np.random.default_rng(11)
    pool = []
    while len(pool) < 240:
        n = int(rng.integers(1, 1 << 28))
        v = vec(gr.rule_array(n))
        if v is not None:
            pool.append((n, v))
    h = []
    for i in range(0, 240, 3):
        h.append(best([pool[i][1], pool[i + 1][1], pool[i + 2][1]])[0])
    out["null_random_triples"] = {str(k): h.count(k) for k in sorted(set(h))}
    print("random triples, best #lines:", out["null_random_triples"])
    h2 = [best([V1, V2, v])[0] for _, v in pool[:120]] + [best([V1, v, V3])[0] for _, v in pool[120:]]
    out["null_R1_R2_X"] = {str(k): h2.count(k) for k in sorted(set(h2))}
    print("(R1, R2, X) / (R1, X, R3) with X random, best #lines:", out["null_R1_R2_X"])

    # Z in the group ring
    inv = lambda f: gr.inverse_nontrivial(f)  # noqa: E731
    Z = gr.mul(gr.mul(R3, gr.dilate(R1, 8)), gr.mul(inv(R1), inv(gr.dilate(R2, 8))))
    Z = Z ^ gr.JJ if (int(Z.sum()) & 1) == 0 else Z
    Z511 = gr.power(Z, 511)
    bad = [jk for jk in LINES if gr.eig(Z511, *jk) != 1]
    out["Z_weight"], out["Z511_weight"], out["Z511_not_one_lines"] = gr.weight(Z), gr.weight(Z511), bad
    print("Z weight", gr.weight(Z), "; Z^511 != 1 on lines", bad)
    # on the axes: the residual mu-part
    F = gr._field()
    for jk in ((0, 1), (1, 0)):
        lz = f18.log(gr.eig(Z, *jk))
        out[f"Z_log_{jk}"] = [lz % 27, lz % 19, lz % 513]
        print("Z at", jk, "log mod 27, 19, 513:", lz % 27, lz % 19, lz % 513)

    # axis restrictions
    T = sympy.Symbol("T")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import relatives  # noqa: E402
    for n in (4850, 10491524, 20982139, 178279803):
        P = relatives.ab_poly(n)
        ax = sympy.Poly(P.as_expr().subs(relatives.a_, 0).subs(relatives.b_, T), T, modulus=2)
        fac = sympy.factor_list(ax.as_expr(), modulus=2)
        out[f"axis_{n}"] = [str(ax.as_expr()), [[str(g), int(e)] for g, e in fac[1]]]
        print("axis restriction F(0, T) of", n, ":", ax.as_expr(), "=", fac[1])
    # Psi_e table for identification
    psi = {}
    for e in (3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 25, 27, 31, 33, 35):
        # Psi_e(z + 1/z) = z^(-phi/2) Phi_e(z): compute via sympy in z
        z = sympy.Symbol("z")
        ph = sympy.Poly(sympy.cyclotomic_poly(e, z), z, modulus=2)
        # find Psi by solving: degree phi/2 polynomial; brute force through Dickson expansion
        d = ph.degree() // 2
        coeffs = [int(c) % 2 for c in ph.all_coeffs()]
        # Phi_e is palindromic; Phi_e(z)/z^d = sum_k c_k (z^k + z^-k) + c_0 term
        mid = coeffs[d]
        expr = sympy.Integer(mid)
        for k in range(1, d + 1):
            if coeffs[d - k]:
                expr += relatives.dickson(k).subs(relatives.a_, T)
        psi[e] = sympy.Poly(expr, T, modulus=2)
    for n in (20982139, 178279803):
        P = relatives.ab_poly(n)
        ax = sympy.Poly(P.as_expr().subs(relatives.a_, 0).subs(relatives.b_, T), T, modulus=2)
        for e, pe in psi.items():
            if pe == ax:
                print("  axis of", n, "= Psi_%d" % e)
                out[f"axis_{n}_is"] = f"Psi_{e}"
    with open(os.path.join(gr.HERE, "mu19_calib.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
