"""Step 10: (a) how often does a random symmetric ninth-power digit pattern have ANY partial-Frobenius
symmetry (g = 1..17, frames A and B)?  (b) the 19-part of the twist ratio rho(c) = lambda(Pc)/lambda(c)
for 10491524, P = diag(1, 27): its psi-transform support over the 38 directions (a unit product in
few directions would explain the symmetry), against random symmetric rules' twist ratios.
Writes step10_symnull.json."""
import json
import numpy as np
import tlib, sbasis
from tlib import M, LINES
from step9_partialfrob import residue_all, PERMS, NZ, partial
from step4_vacuity import matrices

S = sbasis.S_matrix()
rng = np.random.default_rng(99)
NS, CH = 60000, 5000
per = {"g=%d,%s" % key: 0 for key in PERMS}
anyhit, nonzero = [], []
for start in range(0, NS, CH):
    eps = rng.integers(0, 3, (CH, 11)); eps[:, 6] = 0
    d = (eps @ S) % 3                      # (CH, 11) digit2 patterns
    R = residue_all((9 * d).T)             # log mod 27 = 9 d at every character
    a = np.zeros(CH, dtype=bool)
    for key, p in PERMS.items():
        h = np.all((R[p] - R) % 27 == 0, axis=0)
        per["g=%d,%s" % key] += int(h.sum())
        a |= h
    anyhit.append(a); nonzero.append(np.any(d != 0, axis=1))
anyhit = np.concatenate(anyhit); nonzero = np.concatenate(nonzero)
out = {"n": NS, "any_partial_symmetry": int(anyhit.sum()), "rate": float(anyhit.mean()),
       "rate_nonzero_patterns": float(anyhit[nonzero].mean()), "per_key": per}
print("random symmetric digit2 patterns:", out)
# (b) twist ratio 19-parts
X, Y, Yb = matrices()
inv37 = pow(37, -1, 19)
def ratio_support(n, r, P):
    v = tlib.rule_values(n, r)
    L = tlib.logs(v)
    if (L[1:, :] < 0).any() or (L[0, 1:] < 0).any():
        return None
    lv = np.array([L[j, k] for j, k in LINES])
    lp = np.array([L[(P[0][0]*j + P[0][1]*k) % M, (P[1][0]*j + P[1][1]*k) % M] for j, k in LINES])
    g = (lp - lv) % 19
    t3 = (lp - lv) % 27
    x = (Yb @ g) * inv37 % 19
    return int(np.count_nonzero(x)), bool(np.all(t3 == 0))
P = partial(6, "A")
res = {"10491524": ratio_support(10491524, 6, P), "20982139": ratio_support(20982139, 6, P),
       "178279803": ratio_support(178279803, 6, P), "4850_frameB": ratio_support(4850, 4, partial(6, "B"))}
base = []
for n in rng.integers(1, 1 << 15, 60):
    s = ratio_support(int(n), 4, P)
    if s:
        base.append(s[0])
res["random_r4_support_hist"] = {int(k): base.count(k) for k in sorted(set(base))}
print("psi-support (of 38 directions) of the 19-part of lambda(Pc)/lambda(c), and whether its 3-part vanishes:", res)
out["twist_ratio"] = res
json.dump(out, open("step10_symnull.json", "w"), indent=1)
