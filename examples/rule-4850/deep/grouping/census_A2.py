"""
Step 5b: property (A) in both frames, the rules that have it, and the conditional reduction.

(A_g1): R27(f) = f^9709 fixed by g1 = 14 [[1,7],[7,1]]   (4850's frame)
(A_D):  R27(f) fixed by D = diag(1, 27)                     (the rotated frame of 10491524)
(A_D') with D' = diag(27, 1) is equivalent to (A_D) for symmetric f.

For radius 4 (exhaustive) and radius 5 (new rules, exhaustive) via census.py's class logs mod 27
(the bookkeeping of census_A.py, validated there against the group ring on all 32,767 radius-4
rules), list the rules with each property, whether each is cube/ninth/27th-confined, and the
procedure/explanation recorded for the ninth-confined ones.  Also the rotated-frame reduction:
under (A_D), R27 is determined by chi(d) = R27(1, 2^d), d mod 6, and the axis value psi; chi(3) = 1
is forced; ninth-confinement <=> chi(0), chi(1), chi(2), psi in mu_3.
Writes census_A2.json.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402
import census_A as CA  # noqa: E402

C = gr.census
M = 37


def A_from_logs_g(logs, G, twist=0):
    CA.G1 = G
    return CA.A_from_logs(logs, twist)


def main():
    out = {}
    LAB = "/home/user/lattice-lab/examples"
    d = json.load(open(f"{LAB}/llm-pilot-37c/data/ninth37.json"))
    proc = {r["id"]: (r["procedure"], r["explained"]) for fam in d["families"] for r in fam["ninth_power_rules"]}
    for radius in (4, 5):
        logs = C.class_logs(radius)
        lo = 1 if radius == 4 else 1 << 15
        cube, nine, t27 = (C.confined(logs, q) for q in (3, 9, 27))
        for name, G in (("A_g1", ((14, 24), (24, 14))), ("A_D", ((1, 0), (0, 27)))):
            A = A_from_logs_g(logs, G)
            S = [int(n) for n in np.flatnonzero(A) if n >= lo]
            rows = [{"rule": n, "cube": bool(cube[n]), "ninth": bool(nine[n]), "q27": bool(t27[n]),
                     "procedure": proc.get(n, [None])[0], "explained": proc.get(n, [None, None])[1]} for n in S]
            out[f"r{radius}_{name}"] = rows
            print(f"radius {radius} {name}: {len(S)} rules; cube {sum(r['cube'] for r in rows)}, ninth "
                  f"{sum(r['ninth'] for r in rows)}, 27th {sum(r['q27'] for r in rows)}")
            for r in rows:
                if r["ninth"]:
                    print("    ninth:", r["rule"], r["procedure"], "explained" if r["explained"] else "UNEXPLAINED")
            print("    not ninth:", [r["rule"] for r in rows if not r["ninth"]])
        # both
        A1 = A_from_logs_g(logs, ((14, 24), (24, 14)))
        A2 = A_from_logs_g(logs, ((1, 0), (0, 27)))
        both = [int(n) for n in np.flatnonzero(A1 & A2) if n >= lo]
        out[f"r{radius}_both"] = both
        print(f"radius {radius}: rules with both A_g1 and A_D:", both)
        out[f"r{radius}_totals"] = {"cube": int(cube[lo:].sum()), "ninth": int(nine[lo:].sum())}

    # rotated-frame reduction for R1, R2, R3 and the (A_D) rules: chi(d) and psi
    sys.path.insert(0, '/home/user/pilot-37c-round2/scratch')
    import f18  # noqa: E402
    f18.full_log_table()
    red = {}
    for n in (10491524, 20982139, 178279803):
        f = gr.rule_array(n)
        chi = [f18.log(gr.eig(f, 1, pow(2, dd, M))) % 27 for dd in range(6)]
        psi = f18.log(gr.eig(f, 0, 1)) % 27
        red[n] = {"chi(d) log mod 27, d=0..5": chi, "psi": psi}
        print(n, "chi:", chi, "psi:", psi)
    out["rotated_reduction"] = red
    with open(os.path.join(gr.HERE, "census_A2.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
