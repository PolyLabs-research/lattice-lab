"""Lottery sensitivity inside fully-exact (stage 3a) tori: expected max of a random subset of the
connected classes, vs subset size. Exact via hypergeometric: P(subset of size s misses all c_v
classes at levels >= v)."""
import json, sys, math, collections
import numpy as np
sys.path.insert(0, '.')
from load3 import load, grp
from scipy.special import gammaln
T, _ = load()
def lchoose(a, b): return gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1)
def emax(ds, s):
    """E[max of random s-subset] for list ds."""
    N = len(ds); c = collections.Counter(ds); levels = sorted(c)
    # P(max >= v) = 1 - C(N - #>=v, s)/C(N, s)
    e = levels[0]
    for i in range(1, len(levels)):
        ge = sum(c[w] for w in levels[i:])
        pmiss = math.exp(lchoose(N-ge, s) - lchoose(N, s)) if N-ge >= s else 0.0
        e += (levels[i]-levels[i-1]) * (1 - pmiss)
    return e
seen = set(); out = []
for t, v in sorted(T.items(), key=lambda x: x[1]['n']):
    if v['src'] != '3a': continue
    ds = [d for k, d, u in v['cl']]
    N = len(ds)
    if N < 300: continue
    g = (v['n'], grp(*t))
    if g in seen: continue
    seen.add(g)
    full = max(ds)
    c = collections.Counter(ds)
    e2 = emax(ds, N//2); e10 = emax(ds, N//10); e_e = emax(ds, int(N/math.e))
    out.append((v['n'], t, N, full, c[full], c[full-2], c[full-4], full-e_e, full-e2, full-e10))
print(f"{'n':>4} {'torus':>8} {'N':>5} dmax #max #-2 #-4 | drop in E[max] for subset N/e, N/2, N/10")
for r in out:
    print(f"{r[0]:4d} {str(r[1]):>8} {r[2]:5d} {r[3]:4d} {r[4]:4d} {r[5]:4d} {r[6]:4d} | {r[7]:.2f} {r[8]:.2f} {r[9]:.2f}")
a = np.array([r[7] for r in out]); b = np.array([r[9] for r in out])
print(f"\nmean drop per e-fold (N -> N/e): {a.mean():.2f} (median {np.median(a):.2f}, range {a.min():.2f}-{a.max():.2f}), m={len(a)} groups")
print(f"mean drop for 10x fewer classes: {b.mean():.2f} (=> per e-fold {b.mean()/math.log(10):.2f})")
