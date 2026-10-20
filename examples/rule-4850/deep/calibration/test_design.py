"""
Numbers for the two registered tests proposed in the report (nothing here is a census).

T1 (radius 7, D4 family at 37): the axis and diagonal ninth-OK rates at radius 7 are exact (the axis
value is c0 + sum_i c_i D_i(t_1), i <= 7, and the diagonal is the square of c0 + sum c_ii D_i(t_1));
the eight generic classes are taken at 1/9 each, independently (decoy.json: calibrated to 0.1% at
radius 6). From these: the chance count of ninth-power rules among the new radius-7 rules, and the
chance count landing on one of the 16 patterns of the 4850 cluster (triple.json), with the
per-class distribution given ninth-OK (generic classes 1/3 each mod 27; axis and diagonal exact).
Cost: timed on the radius-6 sweep (sweep.log).

T2 (the <swap, -I> family at 37, radius 4): the class structure (lines up to k <-> 1/k: 20 classes,
none forced) and the chance count of ninth-power rules among its non-D4 rules.
Writes test_design.json.
"""
from __future__ import annotations

import itertools
import json
import math
import sys

import numpy as np

sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import census  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
M = 37


def axis_values(r):
    """Coordinates of D_i(t_1) = zeta^i + zeta^-i, i = 0..r (D_0 := 1)."""
    zeta = [census.power(2, e) for e in range(M)]
    out = [census.coord(1)]
    for i in range(1, r + 1):
        out.append(census.coord(zeta[i % M] ^ zeta[(-i) % M]))
    return out


def ninth_ok_set(r):
    """For every bit vector c_0..c_r: is c_0 + sum c_i D_i(t_1) ninth-OK, and its log mod 27."""
    vals = axis_values(r)
    T = census.log_table()
    res = []
    for mask in range(1 << (r + 1)):
        v = 0
        for i in range(r + 1):
            if mask >> i & 1:
                v ^= vals[i]
        lg = int(T[v])
        res.append(lg)
    return res


def main():
    out = {}
    for r in (4, 5, 6, 7):
        L = ninth_ok_set(r)
        ok = [lg == 255 or lg % 9 == 0 for lg in L]
        # axis bits: c_00 and c_i0; diagonal bits: c_00 and c_ii; shared: c_00
        n = 1 << r
        both = 0
        for c0 in (0, 1):
            a = sum(ok[(m << 1) | c0] for m in range(n))
            b = a  # the diagonal is the square of the same polynomial in the c_ii: same counts
            both += a * b
        p_ad = both / (2 * n * n)
        out[r] = {"axis_rate": sum(ok) / len(ok), "P(axis and diagonal ninth-OK)": p_ad}
    S = np.load(f"{HERE}/sweep_stats.npz")
    # check against the sweep at radius 6: the census rates and the (axis, diag) joint
    ind = S["ind9_r6n"]
    sup_ad = sum(ind[m] for m in range(2048) if m & 3 == 3) / ind.sum()
    out["check_r6_P_ad_census"] = float(sup_ad)
    N7 = (1 << 36) - (1 << 28)
    p_gen = (1 / 9) ** 8
    lam7 = N7 * out[7]["P(axis and diagonal ninth-OK)"] * p_gen
    # pattern probabilities at radius 7 for the 16 noticeable cluster patterns
    trip = json.load(open(f"{HERE}/triple.json"))
    pats = {tuple(v) for k, v in trip["patterns"].items() if not k.startswith(("2098", "1782"))}
    L7 = ninth_ok_set(7)
    # conditional distribution of the axis symbol (log mod 27 or zero) given ninth-OK at radius 7
    ax = {}
    for lg in L7:
        if lg == 255 or lg % 9 == 0:
            ax[lg] = ax.get(lg, 0) + 1
    tot = sum(ax.values())
    pax = {k: v / tot for k, v in ax.items()}
    diag = {(-1 if k == 255 else (2 * k) % 27): v for k, v in pax.items()}  # the diagonal is the square
    diag = {(255 if k == -1 else k): v for k, v in diag.items()}

    def p_pat(pat):
        pr = pax.get(pat[0], 0) * diag.get(pat[1], 0)
        for c in (2, 3, 4, 5, 7, 8, 9, 10):
            pr *= 1 / 3 if pat[c] != 255 else 0
        pr *= 1.0 if pat[6] in (0, 255) else 0
        return pr

    sumK = sum(p_pat(p) for p in pats)
    out["T1"] = {
        "new_rules_radius7": N7, "chance_ninth_rules_radius7": lam7,
        "sum_p(pattern in the 16 cluster patterns | ninth)": sumK,
        "chance_rules_on_cluster_patterns": lam7 * sumK,
        "P(>=2 by chance)": 1 - math.exp(-lam7 * sumK) * (1 + lam7 * sumK),
        "cost_core_hours": round(N7 / ((1 << 28) - (1 << 21)) * 117 / 3600, 1),
        "cost_wall_hours_4_cores": round(N7 / ((1 << 28) - (1 << 21)) * 117 / 3600 / 4, 1),
    }
    # T2: the <swap, -I> family of radius 4
    pts = [(p, q) for p in range(-4, 5) for q in range(-4, 5)]
    orb = set()
    for p, q in pts:
        orb.add(min((p, q), (q, p), (-p, -q), (-q, -p)))
    n_orb = len(orb)
    lines = {}
    for k in range(M):
        key = min(k, pow(k, -1, M)) if k else 0
        lines[key] = 1
    n_cls = len(lines)  # k = 0 (with the other axis), the pairs {k, 1/k}, k = +-1 alone
    n_rules = (1 << n_orb) - 1
    n_d4 = (1 << 15) - 1
    p_rule = (1 / 3) ** 3 * (1 / 9) ** (n_cls - 3)  # axis, diagonal, antidiagonal ~1/3, the rest 1/9
    out["T2"] = {"orbits": n_orb, "classes": n_cls, "rules": n_rules, "non_D4_rules": n_rules - n_d4,
                 "chance_per_rule": p_rule, "chance_count": (n_rules - n_d4) * p_rule}
    json.dump(out, open(f"{HERE}/test_design.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
