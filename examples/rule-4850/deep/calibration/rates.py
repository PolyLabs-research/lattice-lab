"""
Step 1: per-class ninth-power (and cube) rates per family, and the dependence between classes,
pairwise and at every order, from the exact joint histograms of sweep.py (sweep_stats.npz).

For a set S of classes, O_S = number of rules all of whose classes in S are ninth-OK (a ninth power
or zero), E_S = N * prod_{c in S} p_c (independence). The ratio O_S / E_S is the dependence at order
|S|; z = (O_S - E_S)/sqrt(E_S) its Poisson significance (a binomial sd would be slightly smaller).

    python rates.py  ->  rates.json, printed summary
"""
from __future__ import annotations

import itertools
import sys
import json

import numpy as np

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
NAMES = ["axis", "(1,1)", "(1,2)", "(1,3)", "(1,4)", "(1,5)", "(1,6)", "(1,7)", "(1,8)", "(1,10)", "(1,13)"]
FREE = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]  # every class but the forced (1,6)
GEN = [2, 3, 4, 5, 7, 8, 9, 10]


def subset_counts(ind: np.ndarray) -> np.ndarray:
    """sup[mask] = number of rules whose indicator vector contains mask (superset sum, zeta transform)."""
    sup = ind.astype(np.float64).copy()
    for b in range(11):
        bit = 1 << b
        idx = np.arange(2048)
        hi = idx[(idx & bit) != 0]
        sup[hi ^ bit] += sup[hi]
    return sup


def analyse(ind: np.ndarray, label: str) -> dict:
    N = ind.sum()
    sup = subset_counts(ind)
    p = np.array([sup[1 << c] / N for c in range(11)])
    out = {"N": int(N), "rates": [round(float(x), 5) for x in p]}
    # pairwise
    pair = {}
    for i, j in itertools.combinations(FREE, 2):
        o = sup[(1 << i) | (1 << j)]
        e = N * p[i] * p[j]
        pair[f"{NAMES[i]}-{NAMES[j]}"] = (round(float(o / e), 4), round(float((o - e) / np.sqrt(e)), 2))
    out["pairs"] = pair
    # every order
    orders = {}
    for k in range(2, len(FREE) + 1):
        rows = []
        for S in itertools.combinations(FREE, k):
            mask = sum(1 << c for c in S)
            o = sup[mask]
            e = N * np.prod(p[list(S)])
            rows.append((o / e, (o - e) / np.sqrt(e), o, e, S))
        r = np.array([x[0] for x in rows])
        z = np.array([x[1] for x in rows])
        worst = max(rows, key=lambda x: abs(x[1]))
        orders[k] = {
            "subsets": len(rows), "ratio_min": round(float(r.min()), 3), "ratio_median": round(float(np.median(r)), 3),
            "ratio_max": round(float(r.max()), 3), "z_rms": round(float(np.sqrt((z**2).mean())), 2),
            "worst": {"S": [NAMES[c] for c in worst[4]], "obs": float(worst[2]), "exp": round(float(worst[3]), 3),
                      "z": round(float(worst[1]), 2)},
        }
    out["orders"] = orders
    # the generic eight only, and with the axis and diagonal
    for name, S in (("generic8", GEN), ("all10", FREE)):
        mask = sum(1 << c for c in S)
        o = sup[mask]
        e = N * np.prod(p[S])
        out[name] = {"obs": float(o), "exp": float(e), "ratio": float(o / e) if e else None}
    # conditional: the eight generic classes given axis and diagonal ninth-OK
    ad = (1 << 0) | (1 << 1)
    Nad = sup[ad]
    pc = np.array([sup[ad | (1 << c)] / Nad for c in range(11)])
    o = sup[ad | sum(1 << c for c in GEN)]
    e = Nad * np.prod(pc[GEN])
    out["generic8_given_ad"] = {"N_ad": float(Nad), "rates_given_ad": [round(float(x), 5) for x in pc],
                                "obs": float(o), "exp": float(e)}
    return out


def main():
    S = np.load(f"{HERE}/sweep_stats.npz")
    res = {}
    for fam in ("r4", "r5n", "r6n"):
        res[fam] = {"ninth": analyse(S[f"ind9_{fam}"], fam), "cube": analyse(S[f"ind3_{fam}"], fam)}
        # marginal distribution of log mod 27 among ninth-OK values, per class (for the pattern null)
        marg = S[f"marg_{fam}"].astype(np.float64)
        cond = []
        for c in range(11):
            row = marg[c]
            nine = row[[0, 9, 18]]
            tot = nine.sum() + row[27]
            cond.append([round(float(x / tot), 5) for x in list(nine) + [row[27]]])
        res[fam]["mod27_given_ninth"] = cond  # P(log = 0, 9, 18 mod 27, zero | ninth-OK)
        res[fam]["zero_rate"] = [float(marg[c, 27] / marg[c].sum()) for c in range(11)]
    json.dump(res, open(f"{HERE}/rates.json", "w"), indent=1)
    for fam in res:
        for kind in ("ninth", "cube"):
            a = res[fam][kind]
            print(f"== {fam} {kind}: N = {a['N']}")
            print("   rates", a["rates"])
            print("   generic8", a["generic8"], " all10", a["all10"])
            print("   generic8 | axis, diag ok", {k: v for k, v in a["generic8_given_ad"].items() if k != "rates_given_ad"})
            for k, v in a["orders"].items():
                print(f"   order {k:2d}: n={v['subsets']:4d} ratio min/med/max {v['ratio_min']}/{v['ratio_median']}/"
                      f"{v['ratio_max']}  z_rms {v['z_rms']}  worst {v['worst']}")
        print("   P(log mod 27 = 0,9,18, zero | ninth-OK):", res[fam]["mod27_given_ninth"])


if __name__ == "__main__" and "--refined" not in sys.argv:
    main()


def refined():
    """Dependence among the rules that are NOT confined at all ten free classes: for every subset S,
    (O_S - O_FREE) / E_S, by order. Mechanism rules are confined everywhere, so they inflate every
    O_S equally; this removes them (and the few chance-confined ones, a negligible bias)."""
    S = np.load(f"{HERE}/sweep_stats.npz")
    out = {}
    for fam in ("r4", "r5n", "r6n"):
        for kind in ("ind9", "ind3"):
            ind = S[f"{kind}_{fam}"]
            N = ind.sum()
            sup = subset_counts(ind)
            p = np.array([sup[1 << c] / N for c in range(11)])
            o_all = sup[sum(1 << c for c in FREE)]
            rows = {}
            for k in range(2, len(FREE)):
                r, z = [], []
                for Sset in itertools.combinations(FREE, k):
                    mask = sum(1 << c for c in Sset)
                    e = N * np.prod(p[list(Sset)])
                    o = sup[mask] - o_all
                    r.append(o / e)
                    z.append((o - e) / np.sqrt(e))
                r, z = np.array(r), np.array(z)
                rows[k] = [round(float(r.min()), 3), round(float(np.median(r)), 3), round(float(r.max()), 3),
                           round(float(np.sqrt((z**2).mean())), 2)]
            out[f"{fam}-{kind}"] = rows
            print(fam, kind, "order: [min, median, max ratio, z_rms] after removing the", int(o_all), "fully confined:")
            for k, v in rows.items():
                print("    ", k, v)
    json.dump(out, open(f"{HERE}/rates_refined.json", "w"), indent=1)


if __name__ == "__main__" and "--refined" in sys.argv:
    refined()
