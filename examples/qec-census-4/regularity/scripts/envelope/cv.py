"""Model ranking by cross-validation on n <= 300, plus forward-chaining (train n <= N, predict the next
band) which is the extrapolation-relevant score.  Two targets as in fit_all.py: THR (threshold
points (n_x(d), d)) and MID (R(n)+1 at every n with codes).  Bands of 50 in n.
Scores:
  THR: held-out threshold residual in d units, f(n_x) - d, and in n units n*(d) - n_x.
  MID: held-out RMSE of f - (R+1); fraction of held-out n with evenfloor(f) == R ('hit').
"""
import numpy as np, json, math, sys
from load import per_n
from models import MODELS, f, fit_ls, crossing

NMIN = int(sys.argv[1]) if len(sys.argv) > 1 else 30
rows = per_n()
nn = np.array([r['n'] for r in rows], float); E = np.array([r['d'] for r in rows], float)
R = np.array([r['R'] for r in rows], float)


def thresholds():
    out = []
    for d in range(2, 40, 2):
        idx = [i for i, r in enumerate(rows) if r['d'] >= d]
        if not idx:
            break
        i = idx[0]
        out.append((d, rows[i]['n'], rows[i - 1]['n'] if i else rows[i]['n']))
    return [(d, nf, npv, 0.5 * (nf + npv)) for d, nf, npv in out]


TH = [t for t in thresholds() if t[1] >= NMIN]
thd = np.array([t[0] for t in TH], float); thn = np.array([t[3] for t in TH]); thf = np.array([t[1] for t in TH])
evenfloor = lambda x: 2 * np.floor(np.asarray(x) / 2 + 1e-4)

bands = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300)]
res = {}
for name in MODELS:
    lobo_thr, lobo_thr_n, lobo_mid, lobo_hit = [], [], [], []
    for lo, hi in bands:
        # THR
        tin = (thf > lo) & (thf <= hi); ttr = (~tin) & (thf <= 300)
        if tin.any() and ttr.sum() >= 3:
            p, _ = fit_ls(name, thn[ttr], thd[ttr])
            lobo_thr += list(f(name, thn[tin], p) - thd[tin])
            lobo_thr_n += [crossing(name, p, d) - x for d, x in zip(thd[tin], thn[tin])]
        # MID
        mtr = (nn >= NMIN) & (nn <= 300) & ~((nn > lo) & (nn <= hi))
        mte = (nn >= NMIN) & (nn > lo) & (nn <= hi)
        if mte.any():
            p, _ = fit_ls(name, nn[mtr], R[mtr] + 1)
            lobo_mid += list(f(name, nn[mte], p) - (R[mte] + 1))
            lobo_hit += list(evenfloor(f(name, nn[mte], p)) == R[mte])
    fwd = {}
    for N in (150, 200, 250, 300):
        hi = N + 50 if N < 300 else 400
        ttr = (thf <= N); tte = (thf > N) & (thf <= hi)
        p, _ = fit_ls(name, thn[ttr], thd[ttr])
        mtr = (nn >= NMIN) & (nn <= N); mte = (nn > N) & (nn <= hi)
        q, _ = fit_ls(name, nn[mtr], R[mtr] + 1)
        fwd[N] = {'thr_res_d': [round(float(x), 2) for x in f(name, thn[tte], p) - thd[tte]],
                  'thr_res_n': [round(float(crossing(name, p, d) - x), 1) for d, x in zip(thd[tte], thn[tte])],
                  'mid_rmse': float(np.sqrt(np.mean((f(name, nn[mte], q) - (R[mte] + 1)) ** 2))),
                  'mid_bias': float(np.mean(f(name, nn[mte], q) - (R[mte] + 1))),
                  'mid_hit': float(np.mean(evenfloor(f(name, nn[mte], q)) == R[mte])),
                  'mid_viol': int(np.sum(E[mte] > evenfloor(f(name, nn[mte], q))))}
    res[name] = {'lobo_thr_rmse_d': float(np.sqrt(np.mean(np.square(lobo_thr)))),
                 'lobo_thr_rmse_n': float(np.sqrt(np.mean(np.square(lobo_thr_n)))),
                 'lobo_mid_rmse': float(np.sqrt(np.mean(np.square(lobo_mid)))),
                 'lobo_mid_hit': float(np.mean(lobo_hit)), 'fwd': fwd}

json.dump(res, open(f'cv_nmin{NMIN}.json', 'w'), indent=1)
print(f'NMIN={NMIN}; LOBO over 50-bands of n<=300; forward-chain train n<=N -> next band (N=300 -> stage 4, n 302-384)')
print(f"{'model':28s} {'LOBO THR rmse_d':>15s} {'rmse_n':>7s} {'MID rmse':>8s} {'hit':>5s} | fwd MID rmse (bias) N=150,200,250,300 | fwd THR resid (d) N=150..300")
for name, r in res.items():
    fw = r['fwd']
    s1 = ' '.join(f"{fw[N]['mid_rmse']:.2f}({fw[N]['mid_bias']:+.2f})" for N in (150, 200, 250, 300))
    s2 = ' '.join(str(fw[N]['thr_res_d']) for N in (150, 200, 250, 300))
    print(f"{name:28s} {r['lobo_thr_rmse_d']:15.3f} {r['lobo_thr_rmse_n']:7.1f} {r['lobo_mid_rmse']:8.3f} {r['lobo_mid_hit']:5.2f} | {s1} | {s2}")
