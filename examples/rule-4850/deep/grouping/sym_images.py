"""
Step 4e: the extra symmetry of u^19 and the mu_19 geometry of the relatives.

* In the frame of R1 = 10491524 (4850 rotated): the stabiliser of u^19(R1) in GL2(Z/37), its image in
  PGL2 and its extra elements; whether diag(1, 27) (27 = 2^6), the partial Frobenius^6 in one
  rotated coordinate, belongs to it (the residue symbol R27 = f^9709 then depends on (alpha, beta)
  only through log alpha, log beta mod 6).
* The same for 4850, 8438150, 20982139, 178279803; and a random-pattern calibration: among all
  mu_3-valued symmetric class functions with the forced classes, how often is the stabiliser > 72?
* The mu_19 line-log vectors (mod 19, 38 lines) of R1, R2, R3 and of their images g.R_i for g in
  the extra symmetry: the rank of the span, and all relations.
Writes sym_images.json.
"""
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
LINES = [(1, k) for k in range(M)] + [(0, 1)]


def pgl(g):
    g = [int(v) % M for v in g]
    inv = pow(next(v for v in g if v), -1, M)
    return tuple(v * inv % M for v in g)


def rank_mod(V, p):
    A = (np.array(V, dtype=np.int64) % p).copy()
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i, c]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        A[r] = A[r] * pow(int(A[r, c]), -1, p) % p
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
    return r


def main():
    out = {}
    f18.full_log_table()
    rules = {n: gr.rule_array(n) for n in (4850, 10491524, 8438150, 20982139, 178279803, 482758, 43250486)}
    D4img = None
    for n, f in rules.items():
        u19 = gr.power(gr.u_of(f), 19)
        S = gr.stabiliser(u19)
        img = sorted({pgl(g) for g in S})
        diag27 = bool(np.array_equal(gr.act(u19, ((1, 0), (0, 27))), u19))
        diag4 = bool(np.array_equal(gr.act(u19, ((1, 0), (0, 4))), u19))
        out[str(n)] = {"stab_order": len(S), "pgl_image": img, "diag(1,27)": diag27, "diag(1,4)": diag4}
        print(n, "stab", len(S), "PGL2 image", len(img), "diag(1,27) fixes u^19:", diag27, "diag(1,4):", diag4)
        print("    extra PGL2 elements:", [g for g in img if not (g[1] == 0 and g[2] == 0) and not (g[0] == 0 and g[3] == 0)])

    # calibration: random mu_3 class patterns.  Build u19-like elements from class values: the
    # residue symbol of a random rule is mu_27-valued; take random rules and cube their residue
    # symbol's exponent... simpler: R27(f)^9 is mu_3-valued for ANY f (it is f^(9709*9)).
    rng = np.random.default_rng(7)
    hist = {}
    for _ in range(300):
        n = int(rng.integers(1, 1 << 28))
        f = gr.rule_array(n)
        w = gr.power(gr.u_of(f), 19 * 9)  # mu_3-valued: the mod-3 part of the 27-adic log / 9
        s = len(gr.stabiliser(w))
        hist[s] = hist.get(s, 0) + 1
    out["random_mu3_pattern_stab_hist"] = {str(k): v for k, v in sorted(hist.items())}
    print("stabiliser orders of R27(f)^9 (a mu_3-valued symbol) for 300 random radius-6 rules:", out["random_mu3_pattern_stab_hist"])

    # mu_19 vectors of R_i and their images under the extra symmetry of u^19(R1)
    f1 = rules[10491524]
    u19 = gr.power(gr.u_of(f1), 19)
    S = gr.stabiliser(u19)
    extra = [g for g in S if pgl(g) not in {pgl(h) for h in gr.stabiliser(f1)} and pgl(g)[1] % M and pgl(g)[2] % M]
    g = extra[0]
    G = ((int(g[0]), int(g[1])), (int(g[2]), int(g[3])))
    out["g_used"] = [int(v) for v in g]
    vecs, names = [], []
    for n in (10491524, 20982139, 178279803):
        f = rules[n]
        for p in range(3):
            h = f
            for _ in range(p):
                h = gr.act(h, G)
            ll = [f18.log(gr.eig(h, *jk)) for jk in LINES]
            vecs.append([x % 19 for x in ll])
            names.append(f"g^{p} R({n})")
    r_all = rank_mod(vecs, 19)
    r_R = rank_mod(vecs[0::3], 19)
    off = [i for i, jk in enumerate(LINES) if jk not in ((1, 0), (0, 1))]
    r_R_off = rank_mod([[v[i] for i in off] for v in vecs[0::3]], 19)
    r_all_off = rank_mod([[v[i] for i in off] for v in vecs], 19)
    # ambient: rank of the mu_19 vectors of 60 random rules (dimension of symmetric functions)
    amb = []
    for _ in range(60):
        f = gr.rule_array(int(rng.integers(1, 1 << 28)))
        ll = [f18.log(gr.eig(f, *jk)) for jk in LINES]
        if any(x is None for x in ll):
            continue
        amb.append([x % 19 for x in ll])
    out.update({"g": G, "rank_mod19_R1R2R3": r_R, "rank_mod19_R_offaxis": r_R_off,
                "rank_mod19_with_g_images": r_all, "rank_mod19_with_g_images_offaxis": r_all_off,
                "ambient_rank_mod19_random_rules": rank_mod(amb, 19),
                "ambient_rank_mod19_random_rules_offaxis": rank_mod([[v[i] for i in off] for v in amb], 19)})
    print("g =", G, "; mu_19 ranks: R1,R2,R3:", r_R, "(off-axis", r_R_off, "); with g-images:", r_all,
          "(off-axis", r_all_off, "); ambient (random rules):", out["ambient_rank_mod19_random_rules"],
          "off-axis", out["ambient_rank_mod19_random_rules_offaxis"])
    with open(os.path.join(gr.HERE, "sym_images.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
