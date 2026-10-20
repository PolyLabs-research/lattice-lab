"""
Step 1b: the decoy calibration of the chance model at full order.

A rule's eight generic classes (census indices 2,3,4,5,7,8,9,10, i.e. (1, 2^i), i = 1..8) each have
a log mod 9; the vector gamma in (Z/9)^8 is the coset of the ninth-power subgroup that the rule's
values fall in. Ninth-power confinement of the generic classes is gamma = 0. The chance model says
the number of rules with a given gamma is N * prod_c P_c(gamma_c) (independent classes). That can be
checked exactly on every OTHER gamma: no mechanism prefers a coset pattern with a class that is not
a cube, so the "non-cube cells" (every gamma_c != 0 mod 3) are pure chance. If the model is right
there at full order (all eight classes jointly), it is calibrated for gamma = 0 too, and every
excess at gamma = 0 is structure.

h9_hist.npz [h9_<fam>]: rules whose axis and diagonal are ninth-OK; [h9all_<fam>]: all rules.
Marginals P_c are taken from the same histogram. Writes decoy.json.
"""
from __future__ import annotations

import json
import math

import numpy as np

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"


def analyse(h: np.ndarray, label: str) -> dict:
    H = h.reshape((9,) * 8).astype(np.float64)
    N = H.sum()
    P = []
    for c in range(8):
        axes = tuple(a for a in range(8) if a != c)
        P.append(H.sum(axis=axes) / N)
    O = h.astype(np.float64)
    # code = sum_d r_d 9^d, so axis a of the C-order reshape is digit d = 7 - a
    Pd = [P[7 - d] for d in range(8)]  # Pd[d] = distribution of digit d (class GEN[d])
    E = np.full(1, N)
    for d in range(8):  # index = sum_d r_d 9^d: digit 0 varies fastest (last axis)
        E = np.multiply.outer(Pd[d], E).reshape(-1)
    digits = np.array(np.unravel_index(np.arange(9**8), (9,) * 8))[::-1]  # digits[d] = r_d
    mod3 = digits % 3
    noncube = np.all(mod3 != 0, axis=0)
    cube = np.all(mod3 == 0, axis=0)
    zero = np.all(digits == 0, axis=0)
    cube_nz = cube & ~zero
    out = {"label": label, "N": N, "marginals": [[round(float(x), 5) for x in p] for p in Pd]}

    def block(mask, name):
        o, e = O[mask], E[mask]
        chi2 = float(((o - e) ** 2 / e).sum())
        n = int(mask.sum())
        # tail: number of cells with O >= k against the Poisson expectation
        from scipy.stats import poisson
        tail = {}
        for k in (1, 2, 3, 5, 10, 20, 50):
            exp_cells = float(poisson.sf(k - 1, e).sum())
            tail[k] = (int((o >= k).sum()), round(exp_cells, 3))
        # the largest standardized excess and its Poisson p-value
        z = (o - e) / np.sqrt(e)
        i = int(np.argmax(z))
        pmin = float(poisson.sf(o[i] - 1, e[i]))
        return {"cells": n, "obs": float(o.sum()), "exp": float(e.sum()), "chi2_per_cell": chi2 / n,
                "tail_obs_exp": tail, "max_z": float(z[i]), "max_cell_obs": float(o[i]),
                "max_cell_exp": float(e[i]), "max_cell_pvalue": pmin,
                "max_cell_pvalue_x_cells": pmin * n}

    out["noncube"] = block(noncube, "noncube")
    out["cube_nonzero"] = block(cube_nz, "cube_nonzero")
    out["all"] = block(np.ones_like(zero), "all")
    out["ninth_cell"] = {"obs": float(O[zero][0]), "exp": float(E[zero][0])}
    # the cube cells with the most excess (units times cubes show up here)
    idx = np.flatnonzero(cube_nz)
    z = (O[idx] - E[idx]) / np.sqrt(E[idx])
    top = idx[np.argsort(-z)[:12]]
    out["top_cube_cells"] = [{"gamma": [int(digits[d, i]) for d in range(8)], "obs": float(O[i]),
                              "exp": round(float(E[i]), 3)} for i in top]
    return out


def main():
    res = {}
    for fam in ("r4", "r5n", "r6n"):
        for kind, fn in (("ad", f"h9_{fam}"), ("all", f"h9all_{fam}")):
            h = np.load(f"{HERE}/h9_hist.npz")[fn]
            a = analyse(h, f"{fam}-{kind}")
            res[f"{fam}-{kind}"] = a
            print(f"== {fam} {kind}: N = {a['N']:.0f}")
            print("   ninth cell (gamma = 0):", a["ninth_cell"])
            for b in ("noncube", "cube_nonzero"):
                x = a[b]
                print(f"   {b}: cells {x['cells']} obs {x['obs']:.0f} exp {x['exp']:.1f} chi2/cell {x['chi2_per_cell']:.4f}"
                      f" max z {x['max_z']:.2f} (obs {x['max_cell_obs']:.0f} exp {x['max_cell_exp']:.3f},"
                      f" p {x['max_cell_pvalue']:.2e}, x cells {x['max_cell_pvalue_x_cells']:.3g})")
                print("      cells with O >= k (obs, Poisson exp):", x["tail_obs_exp"])
            print("   top cube cells:", a["top_cube_cells"][:6])
    json.dump(res, open(f"{HERE}/decoy.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
