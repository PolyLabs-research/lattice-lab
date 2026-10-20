"""
Step 4: rule 4850's relatives at 37, in the group ring.

For R1 = R(10491524) (4850 rotated by 45 degrees), R2 = R(20982139), R3 = R(178279803):
  * orbits, the polynomial F(a, b) (a = x + 1/x, b = y + 1/y) and its factorisation over GF(2),
    for these and for the differences R2 + R1, R3 + R1, R2 + R3;
  * zero eigenvalues (count, F(2^36) evaluation on all 38 lines);
  * the exact group-ring ratios rho_i = R_i / R1 (R1 is a unit off the trivial character):
    weight, rho^9709 = 1 (27th powers), sigma_6-invariance (F(2^9)-valued?), rho^511 (its mu_19
    part), stabilisers; also u, u^3, u^19 of each and the identities u^19(R_i) = u^19(R1);
  * full discrete logs at the 11 classes (f18, independent of the group ring), logs mod 27 and
    the 19-parts.
Writes relatives.json.
"""
import json
import os
import sys
import time

import numpy as np
import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
M = 37
a_, b_ = sympy.symbols("a b")


def dickson(n):
    d0, d1 = sympy.Integer(0), a_
    if n == 0:
        return sympy.Integer(0)
    for _ in range(n - 1):
        d0, d1 = d1, sympy.expand(a_ * d1 + d0)
    return d1


def ab_poly(n):
    """F(a, b) with R(n) = F(x + 1/x, y + 1/y), over GF(2)."""
    out = sympy.Integer(0)
    for i, (p, q) in enumerate(gr.census.orbits(7)):
        if not (n >> i & 1):
            continue
        if p == 0 and q == 0:
            term = sympy.Integer(1)
        elif q == 0:
            term = dickson(p) + dickson(p).subs(a_, b_)
        elif p == q:
            term = dickson(p) * dickson(p).subs(a_, b_)
        else:
            term = dickson(p) * dickson(q).subs(a_, b_) + dickson(q) * dickson(p).subs(a_, b_)
        out += term
    return sympy.Poly(out, a_, b_, modulus=2)


def factor2(P):
    """Bivariate factorisation over GF(2) by Kronecker substitution b -> a^D and recombination of
    the univariate factors (all subsets, up to 2^16): returns [[factor, multiplicity], ...]."""
    import itertools
    da, db = P.degree(a_), P.degree(b_)
    D = da + 1
    T = sympy.Symbol("T")
    rem = P
    found = []
    while rem.total_degree() > 0:
        da = rem.degree(a_)
        D = da + 1
        uni = sympy.Poly(rem.as_expr().subs(b_, T**D).subs(a_, T), T, modulus=2)
        facs = []
        for g, e in sympy.factor_list(uni.as_expr(), modulus=2)[1]:
            facs += [sympy.Poly(g, T, modulus=2)] * e
        best = None
        if len(facs) > 16:
            return found + [[str(rem.as_expr()), 1, "unfactored"]]
        for r in range(1, len(facs) + 1):
            for sub in itertools.combinations(range(len(facs)), r):
                prod = sympy.Poly(1, T, modulus=2)
                for i in sub:
                    prod = prod * facs[i]
                # inverse Kronecker: T^(i + D j) -> a^i b^j
                expr = sum(a_**(k % D) * b_**(k // D) for (k,), c in prod.terms() if c % 2)
                cand = sympy.Poly(expr, a_, b_, modulus=2)
                if cand.total_degree() == 0:
                    continue
                q, r_ = sympy.div(rem, cand)
                if r_.is_zero:
                    best = cand
                    break
            if best is not None:
                break
        if best is None:
            found.append([str(rem.as_expr()), 1])
            break
        found.append([str(best.as_expr()), 1])
        rem = sympy.div(rem, best)[0]
    # merge multiplicities
    merged = {}
    for g in found:
        merged[g[0]] = merged.get(g[0], 0) + 1
    return [[g, e] for g, e in merged.items()]


def orbits_of(n):
    return [o for i, o in enumerate(gr.census.orbits(7)) if n >> i & 1]


def zero_lines(f):
    lines = [(1, k) for k in range(M)] + [(0, 1)]
    return [jk for jk in lines if gr.eig(f, *jk) == 0]


def main():
    t0 = time.time()
    out = {}
    R = {n: gr.rule_array(n) for n in (4850, 10491524, 20982139, 178279803)}
    for n in R:
        P = ab_poly(n)
        out[str(n)] = {"orbits": orbits_of(n), "F(a,b)": str(P.as_expr()),
                       "factors": factor2(P),
                       "zero_lines": zero_lines(R[n]), "weight": gr.weight(R[n])}
        print(n, out[str(n)]["orbits"], "\n  F =", P.as_expr(), "\n  factors:", out[str(n)]["factors"],
              "\n  zero lines:", out[str(n)]["zero_lines"])
    # check ab_poly against the group ring for 4850: F(t(x), t(y)) evaluated at a character
    F = gr._field()
    z = gr._zeta_pows()
    for n in R:
        P = ab_poly(n)
        for (j, k) in [(1, 2), (3, 5), (0, 1)]:
            ta = z[j % M] ^ z[(-j) % M]
            tb = z[k % M] ^ z[(-k) % M]
            v = 0
            for (i1, i2), c in P.terms():
                if c % 2:
                    v ^= F.mul(F.pow(ta, i1), F.pow(tb, i2))
            assert v == gr.eig(R[n], j, k), (n, j, k)
    print("F(a, b) forms agree with the group ring at sample characters")

    for n2, n1 in ((20982139, 10491524), (178279803, 10491524), (178279803, 20982139), (10491524, 4850)):
        d = n2 ^ n1
        P = ab_poly(n2) + ab_poly(n1)
        key = f"{n2}+{n1}"
        out[key] = {"orbits": orbits_of(d), "rule": d, "F": str(P.as_expr()),
                    "factors": factor2(P)}
        print("difference", key, "= rule", d, out[key]["orbits"], "\n  F =", P.as_expr(), "\n  factors:",
              out[key]["factors"])

    # ratios in the group ring
    f1 = R[10491524]
    inv1 = gr.inverse_nontrivial(f1)
    assert np.array_equal(gr.mul(f1, inv1), gr.ONE ^ gr.JJ)
    u = {n: gr.u_of(R[n]) for n in R}
    for n in (20982139, 178279803):
        rho = gr.mul(R[n], inv1)
        rho = gr.unitise(rho, R[n]) if False else rho ^ gr.JJ if (int(rho.sum()) & 1) == 0 else rho
        rec = {"weight": gr.weight(rho),
               "rho^9709==1": bool(np.array_equal(gr.power(rho, 9709), gr.ONE)),
               "rho^511==1 (F(2^9)-valued)": bool(np.array_equal(gr.power(rho, 511), gr.ONE)),
               "rho^(511*19)==1": bool(np.array_equal(gr.power(rho, 511 * 19), gr.ONE)),
               "sigma6_invariant": gr.invariant_under(rho, 6),
               "stab_rho": int(len(gr.stabiliser(rho))),
               "w_rho^511": gr.weight(gr.power(rho, 511)),
               "u19_equal_to_R1": bool(np.array_equal(gr.power(u[n], 19), gr.power(u[10491524], 19))),
               "u3_equal_to_R1": bool(np.array_equal(gr.power(u[n], 3), gr.power(u[10491524], 3)))}
        out[f"rho_{n}"] = rec
        print("rho =", n, "/ 10491524:", rec)
    # 4850 vs its rotation: u^19 of the rotation is the rotated u^19
    rot = ((1, 1), (1, M - 1))  # x^v -> x^(M v), M = [[1,1],[1,-1]]: (x,y) -> (xy, x/y)
    rf = gr.act(R[4850], rot)
    out["rotation_maps_4850_to_10491524"] = bool(np.array_equal(rf, R[10491524]))
    print("act([[1,1],[1,-1]]) R(4850) == R(10491524):", out["rotation_maps_4850_to_10491524"])

    # full discrete logs (f18): classes, logs mod 27, 19-parts
    import f18  # noqa: E402
    t1 = time.time()
    f18.full_log_table()
    print("log table", round(time.time() - t1, 1), "s")
    logs = {}
    for n in R:
        L = [f18.log(gr.eig(R[n], j, k)) for (j, k) in gr.census.characters()]
        logs[n] = L
        out[str(n)]["class_logs_full"] = L
        out[str(n)]["mod27"] = [None if l is None else l % 27 for l in L]
        out[str(n)]["mod513"] = [None if l is None else l % 513 for l in L]
        print(n, "mod 27", out[str(n)]["mod27"], "mod 513", out[str(n)]["mod513"])
    for n in (20982139, 178279803):
        d = [(logs[n][i] - logs[10491524][i]) % (2**18 - 1) for i in range(11)]
        out[f"ratio_logs_{n}"] = {"mod27": [x % 27 for x in d], "19part": [(x // 27) % 19 if x % 27 == 0 else None for x in d],
                                  "mod19": [x % 19 for x in d]}
        print("ratio", n, out[f"ratio_logs_{n}"])
    with open(os.path.join(gr.HERE, "relatives.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
