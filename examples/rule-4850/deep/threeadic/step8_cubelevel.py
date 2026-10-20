"""Step 8: 4850's cube level -- how rare is digit1 = 0 among the unexplained cube-confined rules?

Data: step3_census.json (zero-free cube-confined rules of radius <= 5 with digit1 per class and the
explained status from atlas3.predict and the seventh pilot's condition).
For every unexplained rule: its line-explained classes (line restriction = monomial x full cyclotomic
polynomials, exact factorisation over GF(2)), whose digits are fixed by one-variable structure.
Model: on the remaining free classes (not line-explained, not (1,6)), digit1 is uniform and independent.
  expected number of rules with digit1 = 0 everywhere
      = sum over rules whose line-explained classes already have digit1 = 0 of 3^-(#free classes).
Checks of the model: per-class frequencies of digit1 = 0 on free classes; weight distribution of
eps1 (Legendre-basis coordinates) against Binomial(10, 2/3).
Writes step8_cubelevel.json.
"""
import json
import math
from collections import Counter

import numpy as np
import sympy

import tlib

X = sympy.symbols("x")
PHIS = {e: sympy.Poly(sympy.cyclotomic_poly(e, X), X, modulus=2) for e in range(1, 400) if sympy.totient(e) <= 200}


def cyclotomic_classes(n, r):
    import sys
    sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
    import census37 as C
    f = C.rule(n, r)
    out = []
    for ci, (j, k) in enumerate(tlib.CENSUS_REPS):
        if (j, k) == (0, 1):
            j, k = 1, 0
        coeffs = {}
        exps = [p * j + q * k for p, q in f]
        lo = min(exps)
        for e in exps:
            coeffs[e - lo] = coeffs.get(e - lo, 0) ^ 1
        g = sympy.Poly(sum(X**e for e, c in coeffs.items() if c), X, modulus=2)
        if g.is_zero:
            out.append(False)
            continue
        while g.eval(0) == 0:
            g = sympy.Poly(sympy.quo(g.as_expr(), X), X, modulus=2)
        for e, P in PHIS.items():
            if P.degree() > g.degree():
                continue
            while g.degree() >= P.degree() and g.rem(P).is_zero:
                g = g.quo(P)
        out.append(g.degree() == 0)
    return out


if __name__ == "__main__":
    st3 = json.load(open("step3_census.json"))
    unex = [x for x in st3["cube"] if not x["cube_explained"]]
    expected = 0.0
    per_class = Counter()
    per_class_n = Counter()
    rows = []
    for x in unex:
        cyc = cyclotomic_classes(x["id"], x["radius"])
        d1 = x["digit1"]
        free = [c for c in range(11) if c != 6 and not cyc[c]]
        fixed_ok = all(d1[c] == 0 for c in range(11) if cyc[c])
        contrib = 3.0 ** -len(free) if fixed_ok else 0.0
        expected += contrib
        for c in free:
            per_class_n[c] += 1
            per_class[c] += d1[c] == 0
        rows.append(dict(id=x["id"], cyclotomic=[c for c in range(11) if cyc[c]], n_free=len(free),
                         fixed_ok=fixed_ok, all_zero=all(v == 0 for v in d1), w1=x["w1"]))
    obs = [r["id"] for r in rows if r["all_zero"]]
    freq = {tlib.CENSUS_REPS[c]: round(per_class[c] / per_class_n[c], 3) for c in sorted(per_class_n)}
    nfree = Counter(r["n_free"] for r in rows)
    w = Counter(x["w1"] for x in unex if x["id"] not in obs)
    base = [math.comb(10, k) * (2 / 3) ** k * (1 / 3) ** (10 - k) for k in range(11)]
    exp_w = {k: round(len([x for x in unex if x["id"] not in obs]) * base[k], 1) for k in range(11)}
    chi2 = sum((w.get(k, 0) - e) ** 2 / e for k, e in exp_w.items() if e > 0.5)
    print("unexplained zero-free cube-confined rules, radius <= 5:", len(unex))
    print("number of free (not line-explained) classes:", dict(sorted(nfree.items())))
    print("P(digit1 = 0) per free class:", freq)
    print("expected number with digit1 = 0 everywhere (uniform model):", round(expected, 4), "; observed:", obs)
    print("eps1 weights (excluding the observed):", dict(sorted(w.items())), "expected:", exp_w,
          "chi2 = %.1f" % chi2)
    out = dict(n_unexplained=len(unex), free_class_counts=dict(nfree), per_class_zero_rate={str(k): v for k, v in freq.items()},
               expected_all_zero=expected, observed_all_zero=obs, weights=dict(w), expected_weights=exp_w, chi2=chi2,
               rows=rows)
    json.dump(out, open("step8_cubelevel.json", "w"), indent=0, default=int)
