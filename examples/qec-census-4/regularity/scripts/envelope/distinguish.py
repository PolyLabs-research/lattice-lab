"""How large must n be to tell the leading envelope models apart?
(1) Deterministic: fit each model by THR on ALL thresholds d >= 6 (n <= 384, stages 3a-4), then
    find where the fitted curves differ by one even quantum (2) and by two (4).
(2) Power analysis: simulate censuses up to N_max under model T (its fit to the real data):
    for each even d, threshold location n_x(d) = f_T^{-1}(d + eta) rounded UP to the grid of rich
    n (multiples of 6) and moved back by half a grid step, eta ~ N(0, s); s is tuned so the
    simulated threshold residual rms matches the real one.  Fit both models (THR), record
    dAICc = AICc(wrong) - AICc(true).  Report P(dAICc > 4) and P(wrong model's 2-quantum
    prediction error), 200 sims each.
"""
import numpy as np, math, sys
from load import per_n
from models import MODELS, f, fit_ls, crossing

rng = np.random.default_rng(1)
rows = per_n()
TH = []
DMIN = int(sys.argv[2]) if len(sys.argv) > 2 else 6
print(f'threshold points d >= {DMIN}')
for d in range(DMIN, 40, 2):
    idx = [i for i, r in enumerate(rows) if r['d'] >= d]
    if not idx:
        break
    i = idx[0]; TH.append(((rows[i]['n'] + rows[i - 1]['n']) / 2, d))
thn = np.array([a for a, b in TH]); thd = np.array([b for a, b in TH], float)

KEY = ['a*n^b', 'c*sqrt(n ln n)', 'A*sqrt(n)+B', 'sqrt(n)*(a+b*sqrt(ln n))', 'c*sqrt(n)*(ln n)^p', 'c*sqrt(n)']
P = {}
for m in KEY:
    p, r = fit_ls(m, thn, thd)
    P[m] = p
    res = f(m, thn, p) - thd
    print(f"{m:26s} p={np.round(p,4)}  rms resid (d) = {np.sqrt(np.mean(res**2)):.3f}  ratio d/sqrt(n) at 1e3,1e4,1e5: "
          f"{f(m,1e3,p)/1e3**.5:.3f}, {f(m,1e4,p)/1e4**.5:.3f}, {f(m,1e5,p)/1e5**.5:.3f}")
obs_rms = np.sqrt(np.mean((f('a*n^b', thn, P['a*n^b']) - thd) ** 2))

grid = np.unique(np.concatenate([np.arange(300, 2000, 2), np.geomspace(2000, 1e6, 3000)]))
print('\nWhere fitted curves (all data, THR) differ by 2 and 4 (one / two even quanta):')
pairs = [('a*n^b', 'c*sqrt(n ln n)'), ('a*n^b', 'A*sqrt(n)+B'), ('c*sqrt(n ln n)', 'A*sqrt(n)+B'),
         ('c*sqrt(n ln n)', 'sqrt(n)*(a+b*sqrt(ln n))'), ('a*n^b', 'c*sqrt(n)*(ln n)^p'), ('c*sqrt(n ln n)', 'c*sqrt(n)*(ln n)^p')]
for a, b in pairs:
    dlt = f(a, grid, P[a]) - f(b, grid, P[b])
    out = []
    for q in (1, 2, 4):
        i = np.where(np.abs(dlt) >= q)[0]
        out.append(f'|D|>={q}: n~{grid[i[0]]:.0f} (d~{f(a, grid[i[0]], P[a]):.0f})' if len(i) else f'|D|>={q}: >1e6')
    print(f"  {a:14s} vs {b:26s}: " + ';  '.join(out))


def simulate(T, nmax, s):
    ds, ns = [], []
    for d in range(DMIN, 2000, 2):
        x = crossing(T, P[T], d + rng.normal(0, s), lo=5, hi=1e7)
        if x > nmax:
            break
        g = 6 * math.ceil(x / 6)  # first rich n at or after the crossing
        ns.append(g - 3.0); ds.append(d)
    return np.array(ns), np.array(ds, float)


def aicc(rss, m, k):
    return m * math.log(rss / m) + 2 * k + 2 * k * (k + 1) / max(m - k - 1, 1)


# tune s so that the simulated residual rms (true model) ~ observed rms over n<=384
for s in (0.1, 0.15, 0.2):
    rr = []
    for _ in range(50):
        ns, ds = simulate('a*n^b', 384, s)
        p, _ = fit_ls('a*n^b', ns, ds)
        rr.append(np.sqrt(np.mean((f('a*n^b', ns, p) - ds) ** 2)))
    print(f'noise s={s}: simulated rms {np.mean(rr):.3f} (observed {obs_rms:.3f})')
s = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15

print(f'\nPower analysis (s={s}): fraction of 200 simulated censuses up to N_max in which the WRONG model loses by dAICc>4')
NMAXES = [400, 700, 1000, 2000, 5000, 10000]
for T, W in [('c*sqrt(n ln n)', 'A*sqrt(n)+B'), ('A*sqrt(n)+B', 'c*sqrt(n ln n)'), ('a*n^b', 'c*sqrt(n ln n)'),
             ('c*sqrt(n ln n)', 'a*n^b'), ('a*n^b', 'A*sqrt(n)+B'), ('A*sqrt(n)+B', 'a*n^b')]:
    line = []
    for nmax in NMAXES:
        win = 0; nsim = 200 if nmax <= 2000 else 80
        for _ in range(nsim):
            ns, ds = simulate(T, nmax, s)
            pt, _ = fit_ls(T, ns, ds); pw, _ = fit_ls(W, ns, ds)
            at = aicc(np.sum((f(T, ns, pt) - ds) ** 2), len(ns), len(P[T]))
            aw = aicc(np.sum((f(W, ns, pw) - ds) ** 2), len(ns), len(P[W]))
            win += (aw - at) > 4
        line.append(f'{nmax}:{win / nsim:.2f}')
    print(f'  true {T:16s} wrong {W:16s} ' + '  '.join(line))
