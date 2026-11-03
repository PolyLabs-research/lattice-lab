"""Envelope d_max(n): fit on n <= 300 (stages 3a, 3b/3c), test on stage 4 (n 302-400, partial).

Point sets (per n, n >= NMIN):
  E(n)  max settled best-connected d at n (all tori, all k)
  R(n)  running max of E (monotone staircase / upper hull)
  rec   points with E == R (n where the staircase is actually attained)
  thr   first appearance of each even d: n_first(d); crossing estimate n_x(d) = midpoint of
        n_first(d) and the previous n that has codes.
Fitting methods:
  THR  least squares of f(n_x(d)) = d over the threshold points    (quantisation-aware: the
       continuous envelope crosses the even level d between the two n's)
  MID  least squares of f(n) = R(n) + 1 over all n                  (midpoint of the even cell
       [R, R+2) that a continuous envelope with evenfloor(f) = R must lie in)
  UP   tightest upper envelope: min sum_rec (f - E) s.t. f(n) >= E(n) at every training n
Scoring on stage 4: P(n) = largest even <= f(n); violation = E(n) > P(n); hits = E == P on rec.
"""
import sys, json, math
import numpy as np
from load import per_n
from models import MODELS, NPAR, f, fit_ls, fit_upper, crossing

NMIN = int(sys.argv[1]) if len(sys.argv) > 1 else 30
TRAIN_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 300
QUIET = '-q' in sys.argv

rows = per_n()
nn = np.array([r['n'] for r in rows], float)
E = np.array([r['d'] for r in rows], float)
R = np.array([r['R'] for r in rows], float)
rec = E == R


def thresholds(nmax):
    out = []
    ns = [r['n'] for r in rows]
    for d in range(2, 40, 2):
        idx = [i for i, r in enumerate(rows) if r['d'] >= d]
        if not idx:
            break
        i = idx[0]
        nf = rows[i]['n']
        npv = rows[i - 1]['n'] if i > 0 else nf
        if nf <= nmax:
            out.append((d, nf, npv, 0.5 * (nf + npv)))
    return out


def evenfloor(x):
    return 2 * np.floor(np.asarray(x) / 2 + 1e-4)  # 2e-4 slack in d: LP solutions touch E exactly


tr = (nn >= NMIN) & (nn <= TRAIN_MAX)
te = nn > TRAIN_MAX
TH = [t for t in thresholds(TRAIN_MAX) if t[1] >= NMIN]
TH_all = thresholds(10 ** 9)
th_n = np.array([t[3] for t in TH]); th_d = np.array([t[0] for t in TH], float)


def ic(rss, m, k):
    s = rss / m
    aic = m * math.log(s) + 2 * k
    aicc = aic + 2 * k * (k + 1) / max(m - k - 1, 1)
    bic = m * math.log(s) + k * math.log(m)
    return aicc, bic


def fit_methods(name, mask=None, th=None):
    """Return {'THR': p, 'MID': p, 'UP': p} using training mask and threshold list."""
    mask = tr if mask is None else mask
    thn, thd = (th_n, th_d) if th is None else th
    out = {}
    out['THR'], r1 = fit_ls(name, thn, thd)
    out['MID'], r2 = fit_ls(name, nn[mask], R[mask] + 1)
    out['UP'] = fit_upper(name, nn[mask], E[mask], nn[mask & rec], E[mask & rec], out['MID'])
    return out


def score(name, p):
    ft = f(name, nn[te], p); P = evenfloor(ft)
    viol = [(int(n), int(e), int(q)) for n, e, q in zip(nn[te], E[te], P) if e > q]
    rr = rec[te]
    disc = E[te][rr] - P[rr]
    cont = (E[te][rr] + 1) - ft[rr]
    return {'viol': viol, 'n_rec': int(rr.sum()), 'hits': int((disc == 0).sum()),
            'mae_disc': float(np.mean(np.abs(disc))), 'max_disc': float(np.max(np.abs(disc))),
            'bias_cont': float(np.mean(cont)), 'rmse_cont': float(np.sqrt(np.mean(cont ** 2))),
            'max_cont': float(np.max(np.abs(cont))),
            'cross26': crossing(name, p, 26), 'cross28': crossing(name, p, 28),
            'cross30': crossing(name, p, 30), 'cross32': crossing(name, p, 32),
            'f400': float(f(name, 400, p)), 'f1000': float(f(name, 1000, p)),
            'f3000': float(f(name, 3000, p)), 'f10000': float(f(name, 10000, p))}


results = {}
for name in MODELS:
    fits = fit_methods(name)
    res = {}
    for meth, p in fits.items():
        if p is None:
            continue
        sc = score(name, p)
        # in-sample residuals
        if meth == 'THR':
            rss = float(np.sum((f(name, th_n, p) - th_d) ** 2)); m = len(th_n)
        else:
            rss = float(np.sum((f(name, nn[tr], p) - (R[tr] + 1)) ** 2)); m = int(tr.sum())
        aicc, bic = ic(rss, m, NPAR[name])
        tr_viol = int(np.sum(E[tr] > evenfloor(f(name, nn[tr], p))))
        res[meth] = {'p': [float(x) for x in p], 'rss': rss, 'm': m, 'aicc': aicc, 'bic': bic,
                     'train_viol': tr_viol, **sc}
    results[name] = res

# registered law for reference
reg = {}
for lab, a, b in (('registered envelope 0.8011 n^0.6074', 0.8011, 0.6074), ('registered LS 0.7186 n^0.6074', 0.7186, 0.6074)):
    reg[lab] = score('a*n^b', [a, b])

out = {'NMIN': NMIN, 'TRAIN_MAX': TRAIN_MAX, 'thresholds_all': TH_all, 'results': results, 'registered': reg,
       'test_points': [(int(a), int(b), int(c), bool(d)) for a, b, c, d in zip(nn[te], E[te], R[te], rec[te])]}
json.dump(out, open(f'fit_results_nmin{NMIN}_tr{TRAIN_MAX}.json', 'w'), indent=1, default=float)

if not QUIET:
    print(f'NMIN={NMIN}  TRAIN_MAX={TRAIN_MAX}  train n: {int(tr.sum())}  rec: {int((tr&rec).sum())}  thresholds: {len(TH)}')
    print('thresholds (d, n_first, n_prev, n_x):', TH_all)
    print('test points (n, E, R, on-staircase):', out['test_points'])
    for meth in ('THR', 'MID', 'UP'):
        print(f'\n=== method {meth} ===')
        print(f"{'model':28s} {'params':34s} {'AICc':>7s} {'BIC':>7s} {'trV':>3s} | {'viol(test)':16s} {'hits':>6s} {'MAEd':>5s} {'maxd':>4s} {'bias':>6s} {'rmse':>5s} | {'n*26':>6s} {'n*28':>6s} {'n*30':>6s} {'f(1e3)':>6s} {'f(1e4)':>6s}")
        for name, res in results.items():
            if meth not in res:
                continue
            r = res[meth]
            ps = ','.join(f'{x:.4g}' for x in r['p'])
            vv = ','.join(f'{v[0]}:{v[1]}>{v[2]}' for v in r['viol'][:3]) + ('..' if len(r['viol']) > 3 else '')
            print(f"{name:28s} {ps:34s} {r['aicc']:7.2f} {r['bic']:7.2f} {r['train_viol']:3d} | {len(r['viol']):2d} {vv:13s} {r['hits']:2d}/{r['n_rec']:2d} {r['mae_disc']:5.2f} {r['max_disc']:4.0f} {r['bias_cont']:6.2f} {r['rmse_cont']:5.2f} | {r['cross26']:6.1f} {r['cross28']:6.1f} {r['cross30']:6.1f} {r['f1000']:6.1f} {r['f10000']:6.1f}")
    for lab, r in reg.items():
        print(lab, 'viol', r['viol'], 'hits', r['hits'], '/', r['n_rec'], 'MAEd', round(r['mae_disc'], 2), 'n*26', round(r['cross26'], 1), 'n*28', round(r['cross28'], 1))
