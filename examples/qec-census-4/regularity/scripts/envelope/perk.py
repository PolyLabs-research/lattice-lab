"""Does the same envelope SHAPE hold per k (separate tracks), or only for the overall max?
For k = 4, 6, 8, 12: per-n max settled d at that k; threshold points (first n with d_k >= level,
midpoint with previous n that has a k-code); THR fits of a*n^b, c*sqrt(n ln n), A*sqrt(n)+B on
ALL n (and on n <= 300 with a stage-4 check)."""
import json, collections
import numpy as np
from load import ENTRIES
from models import f, fit_ls, crossing

for k in (4, 6, 8, 12):
    best = collections.defaultdict(int)
    for e in ENTRIES:
        if e['k'] == k and e['settled']:
            best[e['n']] = max(best[e['n']], e['d'])
    ns = sorted(best)
    th = []
    for d in range(6, 40, 2):
        idx = [i for i, n in enumerate(ns) if best[n] >= d]
        if not idx:
            break
        i = idx[0]
        th.append(((ns[i] + ns[i - 1]) / 2 if i else ns[i], d, ns[i]))
    thn = np.array([t[0] for t in th]); thd = np.array([t[1] for t in th], float); thf = np.array([t[2] for t in th])
    print(f"\nk={k}: {len(ns)} n values; first appearances (d:n) " + ' '.join(f'{d}:{n}' for _, d, n in th))
    if len(th) < 4:
        continue
    for name in ('a*n^b', 'c*sqrt(n ln n)', 'A*sqrt(n)+B', 'c*sqrt(n)'):
        p, _ = fit_ls(name, thn, thd)
        rms = np.sqrt(np.mean((f(name, thn, p) - thd) ** 2))
        tr = thf <= 300
        s = ''
        if tr.sum() >= 3 and (~tr).any():
            q, _ = fit_ls(name, thn[tr], thd[tr])
            s = 'n<=300 fit -> stage-4 thresholds resid (d): ' + ', '.join(f'{x:+.2f}' for x in f(name, thn[~tr], q) - thd[~tr])
        print(f"   {name:14s} p={np.round(p, 4)!s:22s} rms={rms:.3f}   {s}")
