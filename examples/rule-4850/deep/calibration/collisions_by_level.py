"""
Step 2d: full mod-27 pattern collisions split by the level of the shared pattern and by whether the
two rules share a polynomial factor (gcd_clusters.json), against independence (sweep marginals).

levels of a shared pattern (zero values allowed everywhere):
  ninth    every class a ninth power
  cube     every class a cube, not all ninth powers
  noncube  every generic class (i = 1..8) a non-cube: no confinement anywhere near; pure chance
  other    the rest
Expected pairs per level: C(N, 2) * product over classes of sum_{s allowed} P_c(s)^2.

For every pattern-sharing ninth-power pair it also asks, from scratch in F(2^36), whether the
ratio of the two rules' eigenvalues lies in F(2^9) at every class (what mechanism 5 gives:
same unit, F(2^9)-valued cores) or is only a 27th power. Writes collisions_by_level.json.
"""
from __future__ import annotations

import itertools
import json
import math
import sys

import numpy as np

sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import census  # noqa: E402
import eigen  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
GEN = [2, 3, 4, 5, 7, 8, 9, 10]
FAMS = {"r4": 32767, "r5n": (1 << 21) - (1 << 15), "r6n": (1 << 28) - (1 << 21)}
M = 37
MOD, D = eigen.field(M)
ZETA = [census.power(2, e) for e in range(M)]


def values(rid):
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in census.rule(rid, 6):
            v ^= ZETA[(p * j + q * k) % M]
        out.append(v)
    return out


def ratio_kind(a, b):
    va, vb = values(a), values(b)
    in9 = True
    for x, y in zip(va, vb):
        if x == 0 or y == 0:
            continue
        r = eigen._mul(x, eigen._pow(y, 2**D - 2, MOD, D), MOD, D)
        in9 &= eigen._pow(r, 2**9, MOD, D) == r
    return "F(2^9)" if in9 else "27th power only"


def level(logs):
    nz = [(c, v) for c, v in enumerate(logs) if v != 27]
    if all(v % 9 == 0 for _, v in nz):
        return "ninth"
    if all(v % 3 == 0 for _, v in nz):
        return "cube"
    if all(logs[c] != 27 and logs[c] % 3 != 0 for c in GEN):
        return "noncube"
    return "other"


def main():
    S = np.load(f"{HERE}/sweep_stats.npz")
    G = json.load(open(f"{HERE}/gcd_clusters.json"))
    out = {}
    for fam, N in FAMS.items():
        marg = S[f"marg_{fam}"].astype(np.float64)
        P = marg / marg.sum(axis=1, keepdims=True)
        pairs = N * (N - 1) / 2
        s9 = [s for s in range(28) if s == 27 or s % 9 == 0]
        s3 = [s for s in range(28) if s == 27 or s % 3 == 0]
        snc = [s for s in range(27) if s % 3 != 0]
        E_all = pairs * np.prod((P**2).sum(axis=1))
        E9 = pairs * np.prod((P[:, s9] ** 2).sum(axis=1))
        E3 = pairs * np.prod((P[:, s3] ** 2).sum(axis=1)) - E9
        Enc = pairs * np.prod([(P[c, snc] ** 2).sum() if c in GEN else (P[c] ** 2).sum() for c in range(11)])
        exp = {"ninth": E9, "cube": E3, "noncube": Enc, "other": E_all - E9 - E3 - Enc}
        obs = {lv: {"coprime": 0, "common_factor": 0} for lv in exp}
        ninth_pairs = []
        for cl in G[fam]["clusters"]:
            lv = level(cl["logs"])
            for a, b, d in cl["gcd_degrees"]:
                obs[lv]["coprime" if d == 0 else "common_factor"] += 1
                if lv == "ninth" and d == 0:
                    ninth_pairs.append((a, b, cl["logs"]))
        # ratio kind for every coprime ninth pair (cap the big all-zero cluster at 40 pairs)
        kinds = {}
        seen_zero = 0
        for a, b, logs in ninth_pairs:
            key = tuple(logs)
            if all(v in (0, 27) for v in logs):
                seen_zero += 1
                if seen_zero > 40:
                    continue
            kinds.setdefault(str(list(key)), []).append([a, b, ratio_kind(a, b)])
        out[fam] = {"expected_pairs": {k: float(v) for k, v in exp.items()}, "observed_pairs": obs,
                    "coprime_ninth_pairs_ratio_kind": kinds}
        print("==", fam)
        for lv in exp:
            print(f"   {lv:8s} expected {exp[lv]:10.3f}   observed coprime {obs[lv]['coprime']:5d}"
                  f"  common factor {obs[lv]['common_factor']:5d}")
        for k, v in kinds.items():
            c = {}
            for _, _, kind in v:
                c[kind] = c.get(kind, 0) + 1
            print("   ninth pattern", k, "coprime pairs:", c)
    json.dump(out, open(f"{HERE}/collisions_by_level.json", "w"), indent=1)


if __name__ == "__main__":
    main()
