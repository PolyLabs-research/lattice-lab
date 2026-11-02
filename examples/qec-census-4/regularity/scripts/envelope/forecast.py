"""Forecast for the stage-4 tori still to run (n = 384 rest, 390, 392, 396; n = 386-388, 394, 398, 400
have no codes by criterion E), and what each outcome for the d = 30 level would do to the ranking.
Fits: THR on all thresholds d >= 6 through n = 384 (d = 26 at 306, d = 28 at 354)."""
import math
import numpy as np
from load import per_n
from models import f, fit_ls, crossing

rows = per_n()
def thr(dmin, extra=()):
    T = []
    for d in range(dmin, 40, 2):
        idx = [i for i, r in enumerate(rows) if r['d'] >= d]
        if not idx:
            break
        i = idx[0]; T.append(((rows[i]['n'] + rows[i - 1]['n']) / 2, d))
    T += list(extra)
    return np.array([a for a, b in T]), np.array([b for a, b in T], float)

KEY = ['a*n^b', 'c*sqrt(n ln n)', 'c*sqrt(n)*(ln n)^p', 'sqrt(n)*(a+b*sqrt(ln n))', 'A*sqrt(n)+B']
ef = lambda x: int(2 * math.floor(x / 2 + 1e-4))
def aicc(rss, m, k):
    return m * math.log(rss / m) + 2 * k + 2 * k * (k + 1) / (m - k - 1)
for dmin in (6, 14):
    n_, d_ = thr(dmin)
    print(f'\nfits on thresholds d >= {dmin} (n <= 384):')
    for m in KEY:
        p, _ = fit_ls(m, n_, d_)
        fc = ' '.join(f'{n}:{f(m, n, p):.2f}->{ef(f(m, n, p))}' for n in (384, 390, 392, 396))
        print(f'  {m:26s} n*(30)={crossing(m, p, 30):6.1f} n*(32)={crossing(m, p, 32):6.1f} | f(n)->even: {fc}')
    print('  scenario: first d=30 at ... -> AICc of each model (lower is better)')
    for lab, extra in (('390 (after 384)', [((384 + 390) / 2, 30)]), ('396 (after 392)', [((392 + 396) / 2, 30)]),
                       ('not by 396 (next n with codes >= 402; take 405 as a stand-in)', [((396 + 414) / 2, 30)])):
        n2, d2 = thr(dmin, extra)
        out = []
        for m in KEY:
            p, _ = fit_ls(m, n2, d2)
            rss = np.sum((f(m, n2, p) - d2) ** 2); k = len(p)
            out.append((aicc(rss, len(n2), k), m))
        best = min(a for a, _ in out)
        print(f'    {lab:60s} ' + '  '.join(f'{m.split("*")[0] if False else m}: {a - best:+.1f}' for a, m in out))
