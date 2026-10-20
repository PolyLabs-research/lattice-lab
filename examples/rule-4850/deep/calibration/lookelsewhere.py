"""
Step 3: look-elsewhere. Every (family, size, q) the project has examined where an unexplained
confinement as improbable as 4850's would have been noticed, with the chance expectation E_i of
unexplained confinements there, and the global probability that chance alone gives, somewhere,
an event whose local p-value is at most 4850's.

Sources (all read, nothing recomputed unless said):
  A  square family (radius <= 4 symmetric rules, ~32,720), cubes, m = 21..125:
     llm-pilot-37c/data/family.json, family_77_125.json (expected = old per-class chance model);
     at 37 the model's 0.62 is replaced by this directory's independence value with the real
     class rates (rates.json, 5.71).
  B  the atlas's 1,274 shell rules, cubes, m = 9..161: census-remainder/expected.jsonl; the
     held-out sizes 163..333 had nothing and E ~ 0 (not listed).
  C  square family at 37, ninth and 27th powers, radius 4, 5 (new), 6 (new): rates.json /
     decoy.json (this directory); and cubes at radius 5, 6 (new).
  D  the atlas at small m for q > 3 (round 3 and eigen.py compute the whole odd part, so any
     confinement would have been seen): computed here with census-remainder's class partition
     (forced subfields), each free class uniform in its field, rules with no free class dropped.

local p of 4850: P(Poisson(E_4850) >= 1), E_4850 = chance ninth-power rules expected at radius 4.
For each combo, P_i = P(the combo's count has local p-value <= p_4850) under Poisson(E_i); the
global p is 1 - prod(1 - P_i). Writes lookelsewhere.json.
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np
from scipy.stats import poisson

EX = "/home/user/lattice-lab/examples"
HERE = f"{EX}/rule-4850/deep/calibration"
sys.path[:0] = [f"{EX}/census-remainder", f"{EX}/llm-pilot-37", f"{EX}/linear-atlas-3"]


def p_at_most(E, p_obs):
    """P(count's upper-tail p-value <= p_obs) for count ~ Poisson(E)."""
    if E <= 0:
        return 0.0
    k = 1
    while poisson.sf(k - 1, E) > p_obs:  # smallest k with P(X >= k) <= p_obs
        k += 1
    return float(poisson.sf(k - 1, E))


def prime_powers(N, cap=10**6):
    out = []
    n, p = N, 2
    fac = {}
    while p * p <= n:
        while n % p == 0:
            fac[p] = fac.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        fac[n] = fac.get(n, 0) + 1
    for p, e in fac.items():
        for k in range(1, e + 1):
            if p**k <= cap:
                out.append(p**k)
    return sorted(out)


def part_d(sizes):
    import remainder
    from census import rules, setup
    rows = []
    R = rules()
    for m in sizes:
        t = time.time()
        mod, d, N, _, _ = setup(m)
        qs = [q for q in prime_powers(N) if q > 3]
        E = {q: 0.0 for q in qs}
        for lattice, shells, f in R:
            cs = [c for c in remainder.classes(f, m) if c["value"]]
            if not cs:
                continue
            for q in qs:
                probs = [math.gcd(2 ** c["degree"] - 1, N // q) / (2 ** c["degree"] - 1) for c in cs]
                if all(p == 1 for p in probs):
                    continue  # forced: structure, not chance
                E[q] += math.prod(probs)
        for q in qs:
            rows.append({"family": "atlas", "m": m, "q": q, "E": E[q], "source": "D"})
        print("D", m, {q: round(E[q], 5) for q in qs}, round(time.time() - t, 1), flush=True)
    return rows


def main():
    rates = json.load(open(f"{HERE}/rates.json"))
    decoy = json.load(open(f"{HERE}/decoy.json"))
    combos = []
    # A
    for fn in ("family.json", "family_77_125.json"):
        for s in json.load(open(f"{EX}/llm-pilot-37c/data/{fn}"))["sizes"]:
            E = s["expected"]
            if s["m"] == 37:
                E = rates["r4"]["cube"]["all10"]["exp"]
            combos.append({"family": "square r<=4", "m": s["m"], "q": 3, "E": E, "source": "A"})
    # B
    for line in open(f"{EX}/census-remainder/expected.jsonl"):
        s = json.loads(line)
        if s["population"]:
            combos.append({"family": "atlas", "m": s["m"], "q": 3, "E": s["expected"], "source": "B"})
    # C
    S = np.load(f"{HERE}/sweep_stats.npz")
    for fam, label in (("r4", "square r4"), ("r5n", "square r5 new"), ("r6n", "square r6 new")):
        E9 = decoy[f"{fam}-ad"]["ninth_cell"]["exp"]
        marg = S[f"marg_{fam}"].astype(np.float64)
        P = marg / marg.sum(axis=1, keepdims=True)
        E27 = float(marg[0].sum() * np.prod(P[:, 0] + P[:, 27]))
        combos.append({"family": label, "m": 37, "q": 9, "E": E9, "source": "C"})
        combos.append({"family": label, "m": 37, "q": 27, "E": E27, "source": "C"})
        if fam != "r4":
            combos.append({"family": label, "m": 37, "q": 3, "E": rates[fam]["cube"]["all10"]["exp"], "source": "C"})
    # D
    combos += part_d([13, 15, 17, 21, 25, 29, 35, 37])
    E4850 = decoy["r4-ad"]["ninth_cell"]["exp"]
    # the decoy occupancy at radius 4 (noncube cells, axis and diagonal ninth-OK) ran 11% above the
    # model; take the larger value, the side that favours chance
    occ = decoy["r4-ad"]["noncube"]["tail_obs_exp"]["1"]
    infl = max(1.0, occ[0] / occ[1])
    E4850 *= infl
    p_obs = 1 - math.exp(-E4850)
    for c in combos:
        c["P_comparable"] = p_at_most(c["E"], p_obs)
    others = [c for c in combos if not (c["family"] == "square r4" and c["m"] == 37 and c["q"] == 9)]
    p_global = 1 - math.prod(1 - c["P_comparable"] for c in others + [{"P_comparable": p_obs}])
    n_eff = sum(c["P_comparable"] for c in others) / p_obs
    big = sorted(others, key=lambda c: -c["P_comparable"])
    out = {"E_4850": E4850, "inflation_used": infl, "p_local_4850": p_obs, "combos": len(combos),
           "combos_with_E_ge_p_obs": sum(c["E"] >= p_obs for c in combos),
           "effective_trials_besides_4850": n_eff, "p_global": p_global,
           "top": big[:40], "all": combos}
    json.dump(out, open(f"{HERE}/lookelsewhere.json", "w"), indent=1)
    print("E_4850", E4850, "p_local", p_obs, "combos", len(combos), "with E >= p_obs", out["combos_with_E_ge_p_obs"])
    print("effective trials besides 4850:", round(n_eff, 2), " p_global:", round(p_global, 4))
    for c in big[:40]:
        print("  ", c)


if __name__ == "__main__":
    main()
