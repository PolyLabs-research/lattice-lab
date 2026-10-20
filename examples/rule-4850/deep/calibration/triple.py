"""
Step 2: the 4850 cluster, counted correctly, and the null probability of the relatives' shared pattern.

1. Checks (exact): 482758 = 4850 * R7, 8438150 = 4850 * R13, 43250486 = 4850 * R7^2 (as Laurent
   polynomials; R7 = (1+a)(1+b), R13 = (1+t(xy))(1+t(x/y)); Phi3(x)^2 Phi3(y)^2 and Phi3(xy) Phi3(x/y)
   are these times monomials), and 10491524 = 4850 o (x, y) -> (xy, x/y) mod 37.
2. Independent eigenvalue check (examples/linear-atlas-3/eigen.py odd_part) of all seven rules,
   and, from scratch in F(2^36), whether the relatives' ratios to 10491524 are 27th powers and
   whether they lie in F(2^9) at every class.
3. Class logs mod 27 of the cluster's GL2/Frobenius images (the patterns a relative could share).
4. The null: under "the two radius-6 relatives are chance ninth-power rules", each class's log mod 27
   is drawn from the family's own distribution given ninth-OK (r6n marginals, sweep_stats.npz),
   independently; also the empirical distribution of patterns among the 125 ninth-power rules.
Writes triple.json.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter

import numpy as np

sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import census  # noqa: E402
import eigen  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
M = 37
CLUSTER = [4850, 482758, 10491524, 8438150, 43250486]
REL = [20982139, 178279803]


def pmul(f, g):
    out = set()
    for a in f:
        for b in g:
            out ^= {(a[0] + b[0], a[1] + b[1])}
    return frozenset(out)


def logs27(support):
    """Class logs mod 27 (255 = zero) of any Laurent polynomial at the 11 class characters."""
    zeta = [census.power(2, e) for e in range(M)]
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in support:
            v ^= zeta[(p * j + q * k) % M]
        out.append(int(census.log_table()[census.coord(v)]))
    return out


def values(support):
    zeta = [census.power(2, e) for e in range(M)]
    out = []
    for j, k in census.characters():
        v = 0
        for p, q in support:
            v ^= zeta[(p * j + q * k) % M]
        out.append(v)
    return out


def main():
    res = {}
    R = {n: census.rule(n, 6) for n in CLUSTER + REL + [7, 13]}
    R7, R13 = R[7], R[13]
    res["482758 = 4850*R7"] = pmul(R[4850], R7) == R[482758]
    res["8438150 = 4850*R13"] = pmul(R[4850], R13) == R[8438150]
    res["43250486 = 4850*R7^2"] = pmul(pmul(R[4850], R7), R7) == R[43250486]
    rot = frozenset(((p + q) % M, (p - q) % M) for p, q in R[4850])
    res["10491524 = 4850 rotated 45 deg (mod 37)"] = rot == frozenset((p % M, q % M) for p, q in R[10491524])
    # independent odd parts
    res["odd_part"] = {n: eigen.odd_part(R[n], M) for n in CLUSTER + REL}
    res["odd_part_divides_29127"] = {n: 29127 % v == 0 for n, v in res["odd_part"].items()}
    # ratios of the relatives to 10491524, from scratch
    mod, d = eigen.field(M)
    inv = lambda v: eigen._pow(v, 2**d - 2, mod, d)  # noqa: E731
    base = values(R[10491524])
    for n in REL:
        vs = values(R[n])
        rat = [eigen._mul(a, inv(b), mod, d) for a, b in zip(vs, base)]
        res[f"ratio {n}/10491524"] = {
            "27th_power_at_every_class": all(eigen._pow(r, (2**18 - 1) // 27, mod, d) == 1 for r in rat),
            "in_F(2^9)_at_every_class": all(eigen._pow(r, 2**9, mod, d) == r for r in rat),
            "classes_in_F(2^9)": [eigen._pow(r, 2**9, mod, d) == r for r in rat],
        }
    # the patterns of the cluster, their 45-degree images and Frobenius doubles
    pats = {}
    for n in CLUSTER + REL:
        f = R[n]
        frot = frozenset((p + q, p - q) for p, q in f)
        for name, s in ((str(n), f), (f"{n}rot", frot)):
            L = logs27(s)
            pats[name] = L
            pats[name + "x2"] = [v if v == 255 else (2 * v) % 27 for v in L]
    res["patterns"] = pats
    target = pats["10491524"]
    res["triple_identical_pattern"] = pats["20982139"] == target and pats["178279803"] == target
    noticeable = {tuple(v) for k, v in pats.items() if not k.startswith(("2098", "1782"))}
    res["noticeable_patterns"] = len(noticeable)
    # null 1: per-class distribution given ninth-OK, from the radius-6 family
    S = np.load(f"{HERE}/sweep_stats.npz")
    marg = S["marg_r6n"].astype(np.float64)
    cond = np.zeros((11, 28))
    for c in range(11):
        okmask = np.array([s % 9 == 0 for s in range(27)] + [True])
        cond[c, okmask] = marg[c, okmask] / marg[c, okmask].sum()

    def p_pat(L):
        return float(np.prod([cond[c, 27 if v == 255 else v] for c, v in enumerate(L)]))

    p_t = p_pat(target)
    pn = {k: p_pat(list(v)) for k, v in zip(range(len(noticeable)), noticeable)}
    P_K = sum(pn.values())
    lam6 = 0.7465  # chance ninth-power rules expected at r6n with axis and diagonal ninth-OK (decoy.json)
    coll = float(np.prod([(cond[c] ** 2).sum() for c in range(11)]))
    res["null_per_class"] = {
        "p(pattern of 10491524 | ninth)": p_t,
        "P(two given chance ninth rules both have it)": p_t**2,
        "sum over the noticeable cluster patterns": P_K,
        "P(two given chance ninth rules share one noticeable pattern)": sum(v**2 for v in pn.values()),
        "P(two given chance ninth rules share ANY pattern)": coll,
        "lambda chance ninth rules r6n": lam6,
        "P(>=2 chance r6 rules on one noticeable pattern), Poisson": sum(
            1 - math.exp(-lam6 * v) * (1 + lam6 * v) for v in pn.values()),
        "P(>=2 chance r6 rules on any one common pattern)": (lam6**2 / 2) * coll,
    }
    # null 2: the empirical distribution of patterns among the 125 ninth-power rules (radius <= 6)
    rows = [json.loads(line) for line in open(f"{HERE}/condition.jsonl") if json.loads(line)["ninth"]]
    pat_of = {r["id"]: tuple(r["logs"]) for r in rows}
    cnt = Counter(pat_of.values())
    others = Counter(v for k, v in pat_of.items() if k not in REL)
    tot = sum(others.values())
    f_t = others[tuple(target)] / tot
    f_K = sum(others[p] for p in noticeable) / tot
    res["null_empirical"] = {
        "ninth_power_rules": len(pat_of), "distinct_patterns": len(cnt),
        "largest_pattern_classes": [[list(p), c] for p, c in cnt.most_common(8)],
        "freq(pattern of 10491524) among the other 123": f_t,
        "P(two draws both have it)": f_t**2,
        "freq(any noticeable cluster pattern) among the other 123": f_K,
        "P(two draws both in the noticeable set)": f_K**2,
        "collision probability sum f^2": sum((c / tot) ** 2 for c in others.values()),
        "unexplained_patterns": None,
    }
    unexpl = [json.loads(line) for line in open(f"{HERE}/condition.jsonl")]
    unexpl = [r for r in unexpl if r["ninth"] and not r["explained"]]
    res["null_empirical"]["unexplained_patterns"] = {r["id"]: r["logs"] for r in unexpl}
    json.dump(res, open(f"{HERE}/triple.json", "w"), indent=1, default=str)
    for k, v in res.items():
        if k != "patterns":
            print(k, ":", v)


if __name__ == "__main__":
    main()
