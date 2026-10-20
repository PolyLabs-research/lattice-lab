"""
Step 4b: a multiplicative relation among the mu_19-parts of 10491524 (R1), 20982139 (R2),
178279803 (R3), found in relatives.py's class logs:  log R2 - log R1 = 12 (log R3 - log R1) (mod 19)
at every class except the axis.  Check it independently on all 38 lines (f18 logs of the F(2^36)
eigenvalues), then in the group ring with the mu_19-projections P19(f) = f^e19
(e19 = 1 mod 19, 0 mod (2^18-1)/19), and measure how often such relations occur by chance:
for triples of random ninth-confined-like vectors, and for actual rule triples.
Also: for g in the stabiliser of u^19(R1), is R2/(g R1) F(2^9)-valued, or mu_19-related?
Writes mu19_relation.json.
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
N18 = 2**18 - 1
LINES = [(1, k) for k in range(M)] + [(0, 1)]


def line_logs(f):
    return [f18.log(gr.eig(f, *jk)) for jk in LINES]


def main():
    out = {}
    R1, R2, R3 = (gr.rule_array(n) for n in (10491524, 20982139, 178279803))
    R0 = gr.rule_array(4850)
    L = {n: line_logs(gr.rule_array(n)) for n in (4850, 10491524, 20982139, 178279803)}
    v1, v2, v3 = (np.array([l % 19 for l in L[n]]) for n in (10491524, 20982139, 178279803))
    lhs = (v2 - v1) % 19
    rhs = (12 * (v3 - v1)) % 19
    holds = [LINES[i] for i in range(38) if lhs[i] == rhs[i]]
    fails = [LINES[i] for i in range(38) if lhs[i] != rhs[i]]
    out["relation_lines_hold"] = len(holds)
    out["relation_lines_fail"] = fails
    print("log R2 - log R1 = 12 (log R3 - log R1) mod 19 holds on", len(holds), "of 38 lines; fails on", fails)

    # every relation c1 v1 + c2 v2 + c3 v3 = 0 (mod 19) and on how many lines it holds
    best = []
    for c in itertools.product(range(19), repeat=3):
        if c == (0, 0, 0):
            continue
        # normalise projectively: first nonzero = 1
        first = next(x for x in c if x)
        if first != 1:
            continue
        r = (c[0] * v1 + c[1] * v2 + c[2] * v3) % 19
        best.append((int((r == 0).sum()), c))
    best.sort(reverse=True)
    out["best_relations"] = best[:5]
    print("best relations (lines holding, (c1, c2, c3)):", best[:5])

    # group ring: mu_19 projections
    q = N18 // 19
    e19 = q * pow(q, -1, 19)
    assert e19 % 19 == 1 and e19 % q == 0
    P = {}
    for name, f in (("R1", R1), ("R2", R2), ("R3", R3)):
        P[name] = gr.power(f, e19) ^ gr.ONE ^ gr.support_idempotent(f)
    X = gr.mul(gr.mul(P["R2"], gr.power(P["R1"], 11)), gr.power(P["R3"], 7))
    out["X_weight"] = gr.weight(X)
    # X should be 1 off the axes: X = 1 + (g(x)-1) J_y + (g(y)-1) J_x
    Jx = np.zeros((M, M), dtype=np.uint8); Jx[:, 0] = 1  # sum_i x^i : eigenvalue 1 iff j = 0
    Jy = np.zeros((M, M), dtype=np.uint8); Jy[0, :] = 1
    Y = gr.mul(X ^ gr.ONE, gr.ONE ^ Jx ^ Jy ^ gr.ONE)  # placeholder (not used)
    offaxis = [jk for jk in LINES if gr.eig(X, *jk) != 1]
    out["X_not_one_on_lines"] = offaxis
    print("X = P19(R2) P19(R1)^11 P19(R3)^7: weight", gr.weight(X), "; eigenvalue != 1 on lines", offaxis)
    print("X support:", gr.pts(X)[:60])
    out["X_support"] = gr.pts(X)

    # chance calibration: random triples of rules with the same structure? Use the recorded
    # radius-6 ninth-confined unexplained-pattern rules and random ninth-confined rules: how often
    # does some relation hold on >= 36 of 38 lines among three rules?
    with open(os.path.join(gr.HERE, "baselines.json")) as fh:
        base = json.load(fh)
    conf = [r["rule"] for r in base["recorded"] if r["ninth_confined"] and r["rule"] not in
            (10491524, 20982139, 178279803, 4850, 482758, 8438150, 43250486)]
    rng = np.random.default_rng(3)
    vecs = {}
    for n in conf:
        ll = line_logs(gr.rule_array(n))
        if any(x is None for x in ll):
            continue
        vecs[n] = np.array([x % 19 for x in ll])
    keys = sorted(vecs)
    counts = []
    trials = 0
    for _ in range(300):
        a, b, c = rng.choice(len(keys), 3, replace=False)
        V = [vecs[keys[a]], vecs[keys[b]], vecs[keys[c]]]
        bestk = 0
        for cc in itertools.product(range(19), repeat=3):
            if cc == (0, 0, 0) or next(x for x in cc if x) != 1:
                continue
            r = (cc[0] * V[0] + cc[1] * V[1] + cc[2] * V[2]) % 19
            bestk = max(bestk, int((r == 0).sum()))
        counts.append(bestk)
        trials += 1
    out["chance_best_relation_hist_confined_triples"] = {str(k): counts.count(k) for k in sorted(set(counts))}
    print("other ninth-confined unit rules: best relation line count over", trials, "random triples:",
          out["chance_best_relation_hist_confined_triples"])
    with open(os.path.join(gr.HERE, "mu19_relation.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
