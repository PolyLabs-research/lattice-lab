"""(1) Within-n (n fixed effects) regression of group dmax on ln N.
(2) Lottery-null for the within-n pairs: pool the two groups' classes at the top level and assign
labels at random (hypergeometric); expected higher/equal/lower vs observed.
(3) Across-n: E(n) residual vs ln(total N at n), all n vs staircase-only."""
import json, collections, itertools, math
import numpy as np
from scipy.special import gammaln
R = json.load(open('torus_rows.json'))
byg = {}
for r in R.values():
    key = (r['n'], tuple(r['g'])); cand = (r['above'], -r['dmax'])
    if key not in byg or cand < byg[key][0]: byg[key] = (cand, r)
G = [v[1] for v in byg.values() if v[1]['above'] == 0]   # settled groups only
byn = collections.defaultdict(list)
for g in G: byn[g['n']].append(g)
# (1) FE regression
def fe(minN=0, nmin=0, nmax=10**9):
    X = []; Y = []
    for n, gs in byn.items():
        gs = [g for g in gs if g['N'] >= minN]
        if len(gs) < 2 or not (nmin <= n <= nmax): continue
        x = np.log([g['N'] for g in gs]); y = np.array([g['dmax'] for g in gs], float)
        X += list(x - x.mean()); Y += list(y - y.mean())
    X = np.array(X); Y = np.array(Y)
    b = (X @ Y) / (X @ X)
    # cluster-robust-ish: bootstrap over n
    return b, len(X)
for minN in (0, 100, 300, 1000):
    for (lo, hi) in ((0, 400), (0, 200), (202, 400)):
        b, m = fe(minN, lo, hi)
        print(f"FE slope d per e-fold of N: minN>={minN:4d}, n in [{lo},{hi}]: {b:+.3f}  (groups used {m})")
# bootstrap CI for minN=1000 and minN=0 over n-clusters
rng = np.random.default_rng(0)
def fe_boot(minN, B=4000):
    ns = [n for n, gs in byn.items() if len([g for g in gs if g['N'] >= minN]) >= 2]
    bs = []
    for _ in range(B):
        samp = rng.choice(ns, len(ns), replace=True)
        X = []; Y = []
        for n in samp:
            gs = [g for g in byn[n] if g['N'] >= minN]
            x = np.log([g['N'] for g in gs]); y = np.array([g['dmax'] for g in gs], float)
            X += list(x - x.mean()); Y += list(y - y.mean())
        X = np.array(X); Y = np.array(Y)
        if X @ X > 0: bs.append((X @ Y) / (X @ X))
    return np.percentile(bs, [2.5, 50, 97.5]), len(ns)
for mn in (0, 300, 1000):
    ci, k = fe_boot(mn)
    print(f"  bootstrap over n (minN>={mn}, {k} n-values): 95% CI {ci[0]:+.2f} .. {ci[2]:+.2f}")

# (2) lottery null for pairs (ratio>=2, both N>=minN); uses top-level counts (lo and hi bounds)
def lch(a, b): return gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1)
def null_probs(a, b, which):
    M = max(a['dmax'], b['dmax'])
    ca = (a[which] if a['dmax'] == M else 0); cb = (b[which] if b['dmax'] == M else 0)
    c = ca + cb; Na, Nb = a['N'], b['N']; Nt = Na + Nb
    # P(a gets none of the c top classes) = C(Nt-c, Na)/C(Nt, Na)
    pa0 = math.exp(lch(Nt-c, Na) - lch(Nt, Na)) if Nt - c >= Na else 0.0
    pb0 = math.exp(lch(Nt-c, Nb) - lch(Nt, Nb)) if Nt - c >= Nb else 0.0
    return pa0, pb0, 1 - pa0 - pb0   # P(b higher-or-at-least-only-b-reaches), P(a only), P(both)
for minN in (0, 300, 1000):
    obs = [0, 0, 0]; ex_lo = np.zeros(3); ex_hi = np.zeros(3); cnt = 0
    for n, gs in byn.items():
        for a, b in itertools.combinations(gs, 2):
            if a['N'] > b['N']: a, b = b, a
            if a['N'] < minN or b['N'] < 2 * a['N']: continue
            cnt += 1
            s = (b['dmax'] > a['dmax']) - (b['dmax'] < a['dmax'])
            obs[0 if s > 0 else (1 if s == 0 else 2)] += 1
            for which, acc in (('lo_max', ex_lo), ('hi_max', ex_hi)):
                pa0, pb0, pboth = null_probs(a, b, which)
                acc += [pa0, pboth, pb0]
    print(f"\npairs minN>={minN} ratio>=2 (settled only, {cnt} pairs): observed higher/equal/lower = {obs}")
    print(f"   lottery null (top-count lower bounds): expected {np.round(ex_lo,1)}   (top-count upper bounds): {np.round(ex_hi,1)}")
