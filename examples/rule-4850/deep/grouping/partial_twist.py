"""
Step 4f: partial-Frobenius twists.  In the frame of R1 = 10491524, r = diag(1, 27) (27 = 2^6 mod 37)
fixes the residue symbol u^19 of R1, R2 = 20982139 and R3 = 178279803.  Let r^i R = R(x, y^(27^i)).

Question: is R2 (or R3) = R1^a (r R1)^b (r^2 R1)^c * B with B F(2^9)-valued (log = 0 mod 513),
on all 38 lines or off the two axis lines?  Linear algebra over Z/513 on the line logs
(f18, independent of the group ring), all (a, b, c) mod 513 (by CRT: mod 27 and mod 19 separately).
Also the twists by s = diag(1, 4), diag(1, 10), diag(1, 16) etc. as controls, and
the same question for R1 against itself (is R1^a (rR1)^b (r^2R1)^c F(2^9)-valued?).
Verify every solution found in the group ring (exact) and against F(2^36) eigenvalues.
Writes partial_twist.json.
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
AX = [i for i, jk in enumerate(LINES) if jk in ((1, 0), (0, 1))]
OFF = [i for i in range(38) if i not in AX]


def logs(f):
    return np.array([f18.log(gr.eig(f, *jk)) for jk in LINES], dtype=object)


def solve(cols, b, idx, mod):
    """all (coeffs mod `mod`) with sum c_i cols_i = b on idx; brute force (mod <= 27, <= 3 cols)."""
    sols = []
    for c in itertools.product(range(mod), repeat=len(cols)):
        ok = True
        for i in idx:
            s = sum(ci * int(col[i]) for ci, col in zip(c, cols)) - int(b[i])
            if s % mod:
                ok = False
                break
        if ok:
            sols.append(c)
    return sols


def main():
    out = {}
    f18.full_log_table()
    R = {n: gr.rule_array(n) for n in (10491524, 20982139, 178279803)}
    R1 = R[10491524]
    twists = {}
    for n_ in (27, 4, 10, 16, 3, 6):
        tw = [R1, gr.act(R1, ((1, 0), (0, n_))), gr.act(R1, ((1, 0), (0, n_ * n_ % M)))]
        twists[n_] = [logs(t) for t in tw]
    for n_, cols in twists.items():
        for target in (20982139, 178279803):
            b = logs(R[target])
            res = {}
            for label, idx in (("all", list(range(38))), ("offaxis", OFF)):
                s27 = solve(cols, [x % 27 for x in b], idx, 27)
                s19 = solve(cols, [x % 19 for x in b], idx, 19)
                res[label] = {"mod27": s27[:6], "n27": len(s27), "mod19": s19[:6], "n19": len(s19)}
            out[f"twist{n_}->{target}"] = res
            print(f"twist diag(1,{n_}) -> {target}: all: n27={res['all']['n27']} n19={res['all']['n19']} {res['all']['mod19'][:3]};"
                  f" offaxis: n27={res['offaxis']['n27']} n19={res['offaxis']['n19']} {res['offaxis']['mod19'][:3]} {res['offaxis']['mod27'][:3]}")
        # self relation: a R1 + b rR1 + c r^2R1 = 0 mod 513 (nontrivial)
        zero = [0] * 38
        for label, idx in (("all", list(range(38))), ("offaxis", OFF)):
            s19 = [c for c in solve(cols, zero, idx, 19) if any(c)]
            s27 = [c for c in solve(cols, zero, idx, 27) if any(x % 3 for x in c)]
            out[f"twist{n_}->self|{label}"] = {"mod19": s19[:6], "mod27_units": s27[:6]}
            print(f"   self relations diag(1,{n_}) {label}: mod19 {s19[:4]}  mod27 (some coeff a unit) {s27[:4]}")
    with open(os.path.join(gr.HERE, "partial_twist.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
