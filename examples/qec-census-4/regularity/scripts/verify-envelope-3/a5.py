"""Across n: E(n)=max settled dmax over groups; Ntot(n)=sum of connected classes over distinct groups.
Residual-on-lnN slope (all n vs staircase-only), joint fit, and collinearity of ln N with n."""
import json, collections, math
import numpy as np
from scipy.optimize import curve_fit
R = json.load(open('torus_rows.json'))
byg = {}
for r in R.values():
    key = (r['n'], tuple(r['g'])); cand = (r['above'], -r['dmax'])
    if key not in byg or cand < byg[key][0]: byg[key] = (cand, r)
G = [v[1] for v in byg.values()]
E = collections.defaultdict(int); Nt = collections.defaultdict(int); Nmax = collections.defaultdict(int)
for g in G:
    Nt[g['n']] += g['N']; Nmax[g['n']] = max(Nmax[g['n']], g['N'])
    if g['above'] == 0: E[g['n']] = max(E[g['n']], g['dmax'])
ns = np.array(sorted(n for n in E if n >= 60), float)
e = np.array([E[int(n)] for n in ns], float); lN = np.log([Nt[int(n)] for n in ns])
run = np.maximum.accumulate(np.array([E[n] for n in sorted(E)], float))
runmap = dict(zip(sorted(E), run)); stair = np.array([E[int(n)] == runmap[int(n)] for n in ns])
print('n>=60 points:', len(ns), ' staircase:', stair.sum())
print('corr(ln n, ln Ntot) =', np.corrcoef(np.log(ns), lN)[0, 1].round(3), '; ln Ntot range', lN.min().round(2), lN.max().round(2))
models = {'a n^b': (lambda n, a, b: a*n**b, [0.8, 0.6]), 'c sqrt(n ln n)': (lambda n, c: c*np.sqrt(n*np.log(n)), [0.6]),
          'A sqrt n + B': (lambda n, A, B: A*np.sqrt(n)+B, [1.6, -3])}
for name, (f, p0) in models.items():
    p, _ = curve_fit(f, ns, e, p0=p0)
    res = e - f(ns, *p)
    b_all = np.polyfit(lN, res, 1)[0]; b_st = np.polyfit(lN[stair], res[stair], 1)[0]
    # joint fit: f(n) + beta*(lnN)
    g = lambda X, *q: f(X[0], *q[:-1]) + q[-1]*X[1]
    q, cov = curve_fit(g, np.vstack([ns, lN]), e, p0=list(p)+[0.0])
    print(f"{name:15s} resid slope/e-fold: all n {b_all:+.3f}, staircase {b_st:+.3f};  joint fit beta={q[-1]:+.3f} +- {math.sqrt(cov[-1,-1]):.3f}  params {np.round(q[:-1],3)}")
# staircase n: ln Ntot at first and last
st_n = ns[stair]
print('staircase n range', st_n.min(), st_n.max(), ' ln Ntot there:', lN[stair].min().round(2), '..', lN[stair].max().round(2))
# growth of Ntot with n (trend absorbed by any envelope in n)
pp = np.polyfit(np.log(ns), lN, 1)
print(f"ln Ntot ~ {pp[0]:.2f} ln n + {pp[1]:.2f};  from n=90 to 384 trend rises {pp[0]*math.log(384/90):.2f} e-folds")
for n in (90, 144, 204, 270, 306, 354, 384): print('  n', n, 'Ntot', Nt[n], 'E', E[n])
