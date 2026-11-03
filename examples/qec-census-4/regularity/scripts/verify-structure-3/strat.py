"""Stratified exact test (n <= 200, strata = order, exact-d groups only): are non-cyclic k_min classes
less likely than cyclic ones to reach the cyclic top?  Conditional on each stratum's total at top,
the non-cyclic count at top is hypergeometric; sum over strata, compare with Monte Carlo of the null."""
import pickle, math
import numpy as np
from collections import defaultdict
from scipy.stats import fisher_exact
T = pickle.load(open("tori.pkl", "rb"))
def gkey(l, m):
    g = math.gcd(l, m); return (g, l * m // g)
pop = {}
for (l, m), v in sorted(T.items(), key=lambda t: (t[1]["stage"] != "3a", t[0])):
    G = gkey(l, m)
    if G in pop: continue
    conn = [r for r in v["rows"] if r["conn"]]
    if not conn: continue
    kmin = min(r["k"] for r in conn)
    pop[G] = [r["d"] for r in conn if r["k"] == kmin]
byN = defaultdict(list)
for G in pop: byN[G[0] * G[1]].append(G)
strata = []
for N, Gs in sorted(byN.items()):
    if 2 * N > 200: continue
    cyc = [G for G in Gs if G[0] == 1]
    if not cyc or len(Gs) == 1: continue
    if any(None in pop[G] for G in Gs): continue  # exact-only strata
    top = max(pop[cyc[0]])
    c = pop[cyc[0]]; nc = [d for G in Gs if G[0] > 1 for d in pop[G]]
    a = sum(d >= top for d in nc); b = len(nc); x = sum(d >= top for d in c); y = len(c)
    p = fisher_exact([[a, b - a], [x, y - x]], alternative="less")[1]
    strata.append((2 * N, a, b, x, y, p))
    print("n=%d non-cyclic at cyclic top %d/%d, cyclic %d/%d, one-sided Fisher p=%.3f" % (2 * N, a, b, x, y, p))
rng = np.random.default_rng(0)
obs = sum(s[1] for s in strata)
sims = np.zeros(200000)
for (_, a, b, x, y, _) in strata:
    K = a + x; Ntot = b + y
    sims += rng.hypergeometric(K, Ntot - K, b, size=sims.size)
exp = sum((s[1] + s[3]) * s[2] / (s[2] + s[4]) for s in strata)
print("strata", len(strata), "observed non-cyclic classes at cyclic top", obs, "expected under no-difference null %.1f" % exp,
      "P(sim <= obs) = %.4f" % (sims <= obs).mean())
