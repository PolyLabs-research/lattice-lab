"""Pool the fixed-k tracks (k = 4, 6, 8): one SHAPE shared across k, a constant per k.
  J-pow : d = c_k n^b              (shared b)
  J-sl  : d = c_k sqrt(n ln n)
  J-aff : d = A sqrt(n) + B_k      (shared asymptotic ratio A)
  J-lnp : d = c_k sqrt(n) (ln n)^p (shared p)
  J-ev  : d = sqrt(n)(a_k + b sqrt(ln n))   (shared b)
Fit on thresholds with n_first <= 300 (THR), score stage-4 thresholds; AICc on all thresholds."""
import collections, math
import numpy as np
from scipy.optimize import least_squares
from load import ENTRIES

KS = (4, 6, 8)
TH = []
for k in KS:
    best = collections.defaultdict(int)
    for e in ENTRIES:
        if e['k'] == k and e['settled']:
            best[e['n']] = max(best[e['n']], e['d'])
    ns = sorted(best)
    for d in range(6, 40, 2):
        idx = [i for i, n in enumerate(ns) if best[n] >= d]
        if not idx:
            break
        i = idx[0]
        TH.append((k, (ns[i] + ns[i - 1]) / 2 if i else ns[i], d, ns[i]))
K = np.array([t[0] for t in TH]); N = np.array([t[1] for t in TH]); D = np.array([t[2] for t in TH], float); NF = np.array([t[3] for t in TH])
ki = np.array([KS.index(k) for k in K])
S, L = np.sqrt, np.log
M = {
    'J-pow': (lambda p, n, i: p[1 + i] * n ** p[0], [0.6, .8, .7, .5]),
    'J-sl':  (lambda p, n, i: p[i] * S(n * L(n)), [.6, .6, .5]),
    'J-aff': (lambda p, n, i: p[0] * S(n) + p[1 + i], [1.6, -3, -4, -5]),
    'J-lnp': (lambda p, n, i: p[1 + i] * S(n) * L(n) ** p[0], [0.55, .55, .5, .45]),
    'J-ev':  (lambda p, n, i: S(n) * (p[1 + i] + p[0] * S(L(n))), [0.7, -.1, -.2, -.4]),
}
def aicc(rss, m, k):
    return m * math.log(rss / m) + 2 * k + 2 * k * (k + 1) / (m - k - 1)
tr = NF <= 300
print(f'{len(TH)} threshold points ({tr.sum()} with n<=300) over k = {KS}')
for name, (fn, p0) in M.items():
    r = least_squares(lambda p: fn(p, N[tr], ki[tr]) - D[tr], p0)
    res_te = fn(r.x, N[~tr], ki[~tr]) - D[~tr]
    ra = least_squares(lambda p: fn(p, N, ki) - D, p0)
    rss = np.sum(ra.fun ** 2)
    print(f"{name:6s} train p={np.round(r.x, 4)!s:36s} stage-4 resid (k,d:res) " +
          ' '.join(f'{k},{int(d)}:{x:+.2f}' for k, d, x in zip(K[~tr], D[~tr], res_te)) +
          f" | mean {res_te.mean():+.2f} rms {np.sqrt(np.mean(res_te**2)):.2f} | all-data p={np.round(ra.x, 4)} AICc={aicc(rss, len(D), len(p0)):.1f}")
