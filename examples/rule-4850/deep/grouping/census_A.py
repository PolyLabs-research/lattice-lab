"""
Step 5: census of property (A) and its consequences.

(A) for a symmetric rule f at 37: the 27th-power residue symbol R27(f) = f^9709 is fixed by
    g1 = [[14, 24], [24, 14]] = 14 [[1, 7], [7, 1]]   (x^v -> x^(g1 v)),
the conjugate by the 45-degree rotation rho = [[1,1],[1,-1]] of the partial Frobenius
diag(1, 27) (27 = 2^6).  Equivalently f(g1-image)/f is 27th-power valued (zeros allowed: zero
characters must map to zero characters).

Lemma (proved in the report): (A) + D4 symmetry => R27(f) is fixed by g1 g2 = sigma_27 = Frob^6,
so R27^63 = 1 and every nonzero eigenvalue is a cube.  This script tests the lemma and measures
P(A), P(ninth | A), P(27th | A) over the radius-4 family (exhaustive, group ring, exact) and the
radius-5 family (exhaustive, from census.py's class logs mod 27 and the line/Frobenius bookkeeping,
cross-checked against the group ring on radius 4), and lists the rules with (A).
Also the "twisted" variants g1 composed with a scalar 2^k (k = 0..17).
Writes census_A.json.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

C = gr.census
M = 37
G1 = ((14, 24), (24, 14))
LINES = [(1, k) for k in range(M)] + [(0, 1)]


def log2(n):
    x = 1
    for e in range(36):
        if x == n % M:
            return e
        x = 2 * x % M
    raise ValueError(n)


def line_of(v):
    """(index of the line rep c' = (1, k) or (0, 1), n) with v = n c'."""
    a, b = v[0] % M, v[1] % M
    if a == 0:
        return 37, b
    return (b * pow(a, -1, M)) % M, a


def class_map():
    """for each line rep: (class index, e) with log at that rep = 2^e * log at the class rep."""
    chars = C.characters()
    out = {}
    for li, (j, k) in enumerate(LINES):
        found = None
        for ci, (cj, ck) in enumerate(chars):
            # images of the class rep under D4 and scalars
            for p, q in ((cj, ck), (ck, cj)):
                for sp in (1, -1):
                    for sq in (1, -1):
                        v = (sp * p, sq * q)
                        idx, n = line_of(v)
                        if idx == (li if li < 37 else 37):
                            # value at v = value at class rep (D4); v = n * rep  =>  val(rep) = val(v)^(2^-log n)
                            found = (ci, (-log2(n)) % 36)
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        assert found, (j, k)
        out[li] = found
    return out


def g1_map():
    """for each line rep c: (line index of g1^T c's line, log2 of the scalar n) with g1^T c = n c'."""
    gT = ((G1[0][0], G1[1][0]), (G1[0][1], G1[1][1]))
    out = {}
    for li, (j, k) in enumerate(LINES):
        v = (gT[0][0] * j + gT[0][1] * k, gT[1][0] * j + gT[1][1] * k)
        idx, n = line_of(v)
        out[li] = (idx, log2(n))
    return out


def A_from_logs(logs, twist=0):
    """logs: (11, N) uint8 class logs mod 27 (255 = zero).  Returns bool (N,) for property (A) with
    g1 composed with the scalar 2^twist."""
    cm, gm = class_map(), g1_map()
    N = logs.shape[1]
    L = np.zeros((38, N), dtype=np.int64)
    Z = np.zeros((38, N), dtype=bool)
    for li in range(38):
        ci, e = cm[li]
        row = logs[ci].astype(np.int64)
        Z[li] = row == 255
        L[li] = (row * pow(2, e, 27)) % 27
    ok = np.ones(N, dtype=bool)
    for li in range(38):
        lj, s = gm[li]
        # R27 at g1^T c = R27(n c') = R27(c')^(2^s), required = R27(c)^(2^twist)
        lhs = (L[lj] * pow(2, s, 27)) % 27
        rhs = (L[li] * pow(2, twist, 27)) % 27
        ok &= (Z[lj] == Z[li]) & (Z[li] | (lhs == rhs))
    return ok


def main():
    out = {}
    t0 = time.time()
    # group ring, radius 4, exhaustive
    gr_A = np.zeros(1 << 15, dtype=bool)
    for n in range(1, 1 << 15):
        f = gr.rule_array(n)
        R27 = gr.power(f, 9709)
        gr_A[n] = np.array_equal(gr.act(R27, G1), R27)
    logs4 = C.class_logs(4)
    A4 = A_from_logs(logs4)
    A4[0] = False
    agree = int((A4[1:] == gr_A[1:]).sum())
    out["radius4_groupring_vs_logs_agree"] = agree
    print("radius 4: (A) by group ring vs by log bookkeeping agree on %d of %d (%.0fs)" % (agree, (1 << 15) - 1, time.time() - t0))
    cube4, nine4, t27_4 = (C.confined(logs4, q) for q in (3, 9, 27))
    for name, A, cube, nine, t27, start in (("radius4", gr_A, cube4, nine4, t27_4, 1),):
        S = np.flatnonzero(A[start:]) + start
        out[name] = {"rules": int(len(A) - start), "A": int(len(S)), "A_and_cube": int(cube[S].sum()),
                     "A_and_ninth": int(nine[S].sum()), "A_and_27th": int(t27[S].sum()),
                     "A_rules_ninth": [int(n) for n in S if nine[n]],
                     "A_not_cube": [int(n) for n in S if not cube[n]][:20],
                     "cube_total": int(cube[start:].sum()), "ninth_total": int(nine[start:].sum())}
        print(name, {k: v for k, v in out[name].items()})
    # radius 5 from logs
    t1 = time.time()
    logs5 = C.class_logs(5)
    new = np.arange(1 << 21) >= (1 << 15)  # rules using a radius-5 orbit
    A5 = A_from_logs(logs5)
    cube5, nine5, t27_5 = (C.confined(logs5, q) for q in (3, 9, 27))
    S = np.flatnonzero(A5 & new)
    out["radius5_new"] = {"rules": int(new.sum()), "A": int(len(S)), "A_and_cube": int(cube5[S].sum()),
                          "A_and_ninth": int(nine5[S].sum()), "A_and_27th": int(t27_5[S].sum()),
                          "A_rules_ninth": [int(n) for n in S if nine5[n]][:50],
                          "A_not_cube": [int(n) for n in S if not cube5[n]][:20],
                          "cube_total": int(cube5[new].sum()), "ninth_total": int(nine5[new].sum())}
    print("radius 5 (new rules):", out["radius5_new"], "(%.0fs)" % (time.time() - t1))
    # twisted variants on radius 5: how many rules have (A) twisted by 2^k
    tw = {}
    for k in range(18):
        Ak = A_from_logs(logs5, twist=k) & new
        tw[k] = {"A": int(Ak.sum()), "cube": int(cube5[Ak].sum()), "ninth": int(nine5[Ak].sum())}
    out["radius5_twisted"] = tw
    print("twisted (A) with scalar 2^k, radius 5 new rules:", tw)
    # recorded radius-6 ninth rules: (A) in the group ring
    rec = json.load(open(os.path.join(gr.HERE, "baselines.json")))["recorded"]
    r6 = {}
    for r in rec:
        if r["rule"] >= (1 << 21) and r["ninth_confined"]:
            f = gr.rule_array(r["rule"])
            R27 = gr.power(f, 9709)
            r6[r["rule"]] = bool(np.array_equal(gr.act(R27, G1), R27))
    out["radius6_recorded_ninth_with_A"] = [n for n, v in r6.items() if v]
    print("recorded radius-6 ninth-confined rules with (A):", out["radius6_recorded_ninth_with_A"], "of", len(r6))
    with open(os.path.join(gr.HERE, "census_A.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
