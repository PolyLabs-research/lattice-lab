"""
Step 3: decode Fable's round-2 congruence R(4850) * D10 * D26 = D8 * D6 * D23 (fable-r2.md JSON).

1. Parse D6, D8, D10, D23, D26 from the JSON and compare each with the dilation f(x^n, y^n) of
   f = R(4850) (and with orbit sums of scalar subgroups).
2. The exponent bookkeeping: for symmetric f at 37, f(x^n, y^n) = f^(2^k) with n = +-2^k (mod 37).
   So LHS = f^(1 + 2^6 + 2^12) = N_{F(2^18)/F(2^6)}(f) and RHS = f^(2^3 + 2^9 + 2^15) = N^8: the
   congruence says N^7 = 1 wherever f != 0, i.e. lambda^29127 = 1: ninth-power confinement.
3. Exhaustive check over the radius-4 family (32,767 rules): the congruence holds in the group
   ring iff census.py says the rule is ninth-confined (zeros allowed).  Also over the radius-6
   records and random radius-6 rules.  And the analogous cube congruence (N_{18/2} in F2).
4. The eigenvalues of D_n: lambda(nc), Frobenius conjugates of lambda (so ninth powers exactly
   when 4850's are); checked in F(2^36) at the class representatives.
Writes fable_congruence.json.
"""
import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

M = 37
MD = "/home/user/lattice-lab/consultations/2026-10-20-rule-4850/round-1/fable-r2.md"


def parse_json_block():
    text = open(MD).read()
    start = text.index("```json") + len("```json")
    end = text.index("```", start)
    return json.loads(text[start:end])


def parse_poly(s):
    a = np.zeros((M, M), dtype=np.uint8)
    for term in s.split("+"):
        term = term.strip()
        mx = re.search(r"x\^(-?\d+)", term)
        my = re.search(r"y\^(-?\d+)", term)
        p = int(mx.group(1)) if mx else (1 if re.search(r"\bx\b", term) else 0)
        q = int(my.group(1)) if my else (1 if re.search(r"\by\b", term) else 0)
        a[p % M, q % M] ^= 1
    return a


def k_of(n):
    """k with n = +-2^k (mod 37), 0 <= k < 18."""
    x = 1
    for k in range(36):
        if x == n % M:
            return k % 18
        x = 2 * x % M
    raise ValueError(n)


def congruence(f):
    lhs = gr.mul(gr.mul(f, gr.dilate(f, 10)), gr.dilate(f, 26))
    rhs = gr.mul(gr.mul(gr.dilate(f, 8), gr.dilate(f, 6)), gr.dilate(f, 23))
    return bool(np.array_equal(lhs, rhs))


def cube_congruence(f):
    """N_{18/2}(f) = f^(sum 4^i, i<9) lies in F2: N^2 = N.  Equivalent to cube confinement."""
    N = gr.ONE.copy()
    for i in range(9):
        N = gr.mul(N, gr.dilate(f, pow(4, i, M)))
    return bool(np.array_equal(gr.dilate(N, 2), N))


def main():
    out = {}
    js = parse_json_block()
    defs = js["definitions"]
    f = gr.rule_array(4850)
    D = {}
    for name in ("D6", "D8", "D10", "D23", "D26"):
        n = int(name[1:])
        D[n] = parse_poly(defs[name])
        same = bool(np.array_equal(D[n], gr.dilate(f, n)))
        out[f"{name}_equals_f(x^{n},y^{n})"] = same
        out[f"{name}_weight"] = gr.weight(D[n])
        out[f"{name}_k"] = k_of(n)
        # is it f^(2^k) in the group ring?
        out[f"{name}_equals_f^(2^k)"] = bool(np.array_equal(D[n], gr.power(f, 2 ** k_of(n))))
        # orbit-sum test: is D_n invariant under some nontrivial scalar subgroup?
        out[f"{name}_scalar_invariance"] = [h for h in (2, 3, 4, 6, 9, 12, 18) if
                                            gr.invariant_under(D[n], pow(2, 36 // h, M))]
        print(name, "= f(x^n, y^n):", same, "weight", gr.weight(D[n]), "k =", k_of(n),
              "= f^(2^k):", out[f"{name}_equals_f^(2^k)"], "scalar-orbit invariance (orders):",
              out[f"{name}_scalar_invariance"])
    lhs = gr.mul(gr.mul(f, D[10]), D[26])
    rhs = gr.mul(gr.mul(D[8], D[6]), D[23])
    out["congruence_holds_4850"] = bool(np.array_equal(lhs, rhs))
    out["lhs_weight"] = gr.weight(lhs)
    print("congruence holds for 4850:", out["congruence_holds_4850"], "LHS weight", gr.weight(lhs))
    # the exponents
    ks_l = [0, k_of(10), k_of(26)]
    ks_r = [k_of(8), k_of(6), k_of(23)]
    el = sum(2**k for k in ks_l)
    er = sum(2**k for k in ks_r)
    out["lhs_exponent"], out["rhs_exponent"] = el, er
    out["rhs_over_lhs"] = er / el
    print("LHS = f^%d (k = %s), RHS = f^%d (k = %s); RHS exponent = 8 * LHS exponent: %s; (8-1)*%d = %d"
          % (el, ks_l, er, ks_r, er == 8 * el, el, 7 * el))
    assert er == 8 * el and 7 * el == 29127

    # eigenvalues of D_n at the class representatives: lambda(n c) = lambda(c)^(2^k)
    F = gr._field()
    for n in D:
        for (j, k) in gr.census.characters():
            lam = gr.eig(f, j, k)
            assert gr.eig(D[n], j, k) == F.pow(lam, 2 ** k_of(n)) == gr.eig(f, n * j, n * k)
    out["D_eigenvalues_are_frobenius_conjugates"] = True
    print("eigenvalues of D_n = lambda^(2^k) at all 11 class representatives (F(2^36) check)")

    # exhaustive radius-4 check against the census
    t0 = time.time()
    logs = gr.census.class_logs(4)
    ninth = gr.census.confined(logs, 9)
    cube = gr.census.confined(logs, 3)
    agree9 = agree3 = 0
    holds = []
    mismatch = []
    for n in range(1, 1 << 15):
        g = gr.rule_array(n)
        c9 = congruence(g)
        if c9:
            holds.append(n)
        if c9 == bool(ninth[n]):
            agree9 += 1
        else:
            mismatch.append(n)
    out["radius4_rules"] = (1 << 15) - 1
    out["radius4_congruence_holds"] = len(holds)
    out["radius4_census_ninth_confined"] = int(ninth[1:].sum())
    out["radius4_agree"] = agree9
    out["radius4_mismatch"] = mismatch
    out["radius4_holds_list"] = holds
    print("radius 4: congruence holds for %d rules; census ninth-confined %d; agree on %d of %d; %.1fs"
          % (len(holds), int(ninth[1:].sum()), agree9, (1 << 15) - 1, time.time() - t0))
    # cube analogue on a sample (it is slower: 9 products)
    rng = np.random.default_rng(5)
    sample = sorted(set(rng.integers(1, 1 << 15, 3000).tolist()) | set(np.flatnonzero(cube).tolist()) - {0})
    for n in sample:
        if cube_congruence(gr.rule_array(n)) == bool(cube[n]):
            agree3 += 1
    out["radius4_cube_congruence_sample"] = len(sample)
    out["radius4_cube_congruence_agree"] = agree3
    print("cube analogue N_{18/2}(f) in F2: agrees with census cube confinement on %d of %d rules"
          % (agree3, len(sample)))

    # radius 6: the two unexplained rules, the relatives, and random rules
    r6 = {}
    for n in (20982139, 178279803, 10491524, 482758, 8438150, 43250486):
        r6[n] = congruence(gr.rule_array(n))
    out["relatives_congruence"] = r6
    print("relatives:", r6)
    rng = np.random.default_rng(6)
    rand = [int(n) for n in rng.integers(1, 1 << 28, 2000)]
    out["random_r6_congruence_holds"] = sum(congruence(gr.rule_array(n)) for n in rand)
    print("random radius-6 rules satisfying it:", out["random_r6_congruence_holds"], "of", len(rand))
    with open(os.path.join(gr.HERE, "fable_congruence.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
