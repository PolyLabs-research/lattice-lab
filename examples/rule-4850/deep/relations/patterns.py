"""
How surprising is it that 10491524, 20982139 and 178279803 share one exact mod-27 class pattern?

1. The empirical pattern distribution of the 125 ninth-power rules of radius <= 6 (records of the
   dossier): multiplicities, collision probabilities, twist classes (x2 swaps 9 <-> 18).
2. A chance model from the whole radius <= 6 family (268,435,455 rules, mod-27 logs by the census
   method with census37's own table): per-class distributions of log mod 27, the probability of
   the shared pattern under independence, and direct counts of rules matching the pattern on
   every subset of classes obtained by dropping up to two of the eight classes i = 1..8 (tests
   the independence model and looks for a cluster of near-misses that a mechanism would leave).

    python patterns.py     -> patterns.json
"""
from __future__ import annotations

import collections
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext6  # noqa: E402
import tables  # noqa: E402

C = tables.C
LL = "/home/user/lattice-lab/examples"
PAT = (9, 9, 18, 18, 18, 9, 0, 18, 0, 9, 9)
OFF = [2, 3, 4, 5, 7, 8, 9, 10]


def records():
    d = json.load(open(f"{LL}/llm-pilot-37c/data/ninth37.json"))
    recs = []
    for fam in d["families"]:
        for r in fam["ninth_power_rules"]:
            recs.append((r["id"], tuple(255 if v is None else v for v in r["logs"]), bool(r.get("explained"))))
    for line in open(f"{LL}/llm-pilot-37c/records.jsonl"):
        x = json.loads(line)
        if x["test"] == "hit":
            recs.append((x["id"], tuple(255 if v is None else v for v in x["logs"]), bool(x["explained"])))
    return recs


def twist(p):
    return tuple(v if v in (0, 255) else 27 - v for v in p)


def main():
    out = {}
    recs = records()
    assert len(recs) == 125
    cnt = collections.Counter(p for _, p, _ in recs)
    n = len(recs)
    out["distinct_patterns"] = len(cnt)
    out["multiplicities"] = sorted(cnt.values(), reverse=True)
    out["pattern_count"] = cnt[PAT]
    out["twisted_pattern_count"] = cnt[twist(PAT)]
    out["collision_prob_pair"] = sum((c / n) ** 2 for c in cnt.values())
    out["collision_prob_triple"] = sum((c / n) ** 3 for c in cnt.values())
    # twist classes
    tc = collections.Counter(min(p, twist(p)) for _, p, _ in recs)
    out["distinct_twist_classes"] = len(tc)
    # patterns shared by >= 3 rules: how many of them consist of explained rules
    groups = collections.defaultdict(list)
    for i, p, e in recs:
        groups[p].append((i, e))
    out["patterns_with_3_or_more"] = [
        {"pattern": list(p), "rules": [i for i, _ in g], "explained": [e for _, e in g]}
        for p, g in groups.items() if len(g) >= 3]
    zero_free = [p for _, p, _ in recs if 255 not in p]
    cz = collections.Counter(zero_free)
    out["zero_free_rules"] = len(zero_free)
    out["zero_free_distinct"] = len(cz)
    # empirical per-class distribution among the 125 (zero-free ones)
    emp = []
    for c in range(11):
        cc = collections.Counter(p[c] for p in zero_free)
        emp.append({str(k): v / len(zero_free) for k, v in cc.items()})
    out["empirical_class_dist_125"] = emp
    p_emp_indep = float(np.prod([emp[c].get(str(PAT[c]), 0.0) for c in range(11)]))
    out["P_pattern_indep_empirical_marginals"] = p_emp_indep

    # ---- chance model from the whole family (mod 27 with census37's table)
    t27 = C.log_table()  # uint8 mod 27, 255 for zero
    c5 = ext6.coords5()
    c6 = ext6.coords6_extra()
    hist = np.zeros((11, 256), dtype=np.int64)
    drop_sets = [()] + [(d,) for d in OFF] + list(itertools.combinations(OFF, 2))
    match_counts = {ds: 0 for ds in drop_sets}
    full_rules = []
    near = collections.defaultdict(list)
    total = 0
    pat = np.array(PAT)
    for j in range(128):
        lg = t27[c5 ^ c6[:, j: j + 1]]  # (11, 2^21)
        if j == 0:
            lg[:, 0] = 255  # rule 0 (empty) is not a rule
        for c in range(11):
            hist[c] += np.bincount(lg[c], minlength=256)
        eq = lg[OFF] == pat[OFF][:, None]  # (8, 2^21)
        s = eq.sum(axis=0)
        total += lg.shape[1] - (1 if j == 0 else 0)
        for ds in drop_sets:
            keep = [i for i, c in enumerate(OFF) if c not in ds]
            m = eq[keep].all(axis=0)
            match_counts[ds] += int(m.sum())
            if len(ds) == 1:
                for i in np.flatnonzero(m):
                    near[ds[0]].append(int(i + (j << 21)))
        for i in np.flatnonzero(s == 8):
            full_rules.append({"rule": int(i + (j << 21)), "axis": int(lg[0, i]),
                               "diag": int(lg[1, i])})
    out["family_rules"] = total
    dist = []
    for c in range(11):
        h = hist[c]
        nz = h[:255].sum()
        dist.append({"P(zero)": h[255] / total, "P(0 mod 9)": h[:255:9].sum() / total,
                     "P(r|9th)": {str(r): (h[r] / h[:255:9].sum()) if h[:255:9].sum() else 0
                                  for r in (0, 9, 18)},
                     "P(r)": {str(r): h[r] / total for r in (0, 9, 18)}, "nonzero": int(nz)})
    out["family_class_dist"] = dist
    p_off = float(np.prod([dist[c]["P(r)"][str(PAT[c])] for c in OFF]))
    p_all = p_off * dist[0]["P(r)"][str(PAT[0])] * dist[1]["P(r)"][str(PAT[1])]
    out["P_random_rule_has_pattern_on_8_classes"] = p_off
    out["P_random_rule_has_full_pattern"] = p_all
    out["expected_rules_with_pattern_on_8"] = p_off * total
    out["expected_rules_with_full_pattern"] = p_all * total
    # conditional: a chance ninth-power rule has this pattern
    p9 = float(np.prod([dist[c]["P(r|9th)"][str(PAT[c])] for c in range(11) if c != 6]))
    out["P_chance_ninth_rule_has_pattern"] = p9
    out["P_two_chance_ninth_rules_both_match"] = p9**2
    exp_counts = {}
    for ds in drop_sets:
        keep = [c for c in OFF if c not in ds]
        e = total * float(np.prod([dist[c]["P(r)"][str(PAT[c])] for c in keep]))
        exp_counts[",".join(map(str, ds)) or "none"] = {"observed": match_counts[ds],
                                                         "expected_indep": e}
    out["match_on_subsets"] = exp_counts
    out["rules_matching_all_8"] = full_rules
    out["near_misses_drop_one"] = {str(k): v[:50] for k, v in near.items()}
    json.dump(out, open(os.path.join(HERE, "patterns.json"), "w"), indent=1, default=float)
    for k, v in out.items():
        if k in ("family_class_dist", "empirical_class_dist_125", "near_misses_drop_one"):
            continue
        print(k, ":", v)


if __name__ == "__main__":
    main()
