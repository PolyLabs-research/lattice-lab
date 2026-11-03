"""Is the envelope an extreme-value (lottery) statistic or a sharp edge?
Per torus (one per isomorphism group, the one with most data), over CONNECTED classes:
  N        number of connected classes with k > 0
  at_max   classes whose exact d equals the torus's best d (any k)
  near     classes whose d (stage 3a: exact) or window upper bound (stages 3b-4) equals best-2
           (stages 3b-4: an upper bound on the count, since upper >= true d)
Then: does E(n) (per-n max) sit higher where more classes are available?  Residual of E(n)
against the THR power-law / sqrt(n ln n) envelope, regressed on log N(n) (deduplicated by group).
"""
import json, glob, math, collections
import numpy as np
from pathlib import Path
from load import per_n, group, REPO
from models import f, fit_ls

tor = {}
for p in glob.glob(str(REPO / 'qec-census-3' / 'data' / '*.jsonl')):
    L = [json.loads(x) for x in open(p) if x.strip()]
    h = L[0]
    ds = [r['d'] for r in L[1:] if r.get('connected') and r['status'] == 'complete']
    if not ds:
        continue
    dm = max(ds)
    tor[(h['l'], h['m'])] = {'n': h['n'], 'N': len(ds), 'dmax': dm, 'at_max': ds.count(dm),
                             'near': ds.count(dm - 2), 'near4': ds.count(dm - 4), 'src': '3a(exact)'}
for st in ('qec-census-3b', 'qec-census-3c', 'qec-census-4'):
    for x in open(REPO / st / 'records.jsonl'):
        r = json.loads(x)
        if r.get('job') != 'torus' or not r.get('rows'):
            continue
        conn = [y for y in r['rows'] if y.get('connected')]
        if not conn:
            continue
        ex = [y['exact']['d'] for y in conn if y.get('exact') and y['exact'].get('status') == 'complete']
        best = max([v['d'] for v in r['best']['connected'].values() if v.get('d')] or [0])
        if best == 0:
            continue
        # value per class: exact if known else window upper bound
        val = [(y['exact']['d'] if (y.get('exact') and y['exact'].get('status') == 'complete') else y.get('upper')) for y in conn]
        val = [v for v in val if v is not None]
        tor[(r['l'], r['m'])] = {'n': r['n'], 'N': len(conn), 'dmax': best, 'at_max': ex.count(best),
                                 'near': sum(1 for v in val if v == best - 2),
                                 'near4': sum(1 for v in val if v == best - 4), 'src': st[-2:] + '(upper)'}

# stage 3d settled the k=4 (and 3x49's k=6) entries of 9 tori at d = 24 (records in 3c show 22)
S3D = [(3, 45), (5, 27), (2, 69), (3, 46), (6, 23), (3, 47), (2, 72), (4, 36), (3, 49)]
c3d = collections.Counter()
for x in open(REPO / 'qec-census-3d' / 'records.jsonl'):
    r = json.loads(x)
    if 'class' in r and r.get('distqldpc', {}).get('d') == 24:
        c3d[tuple(r['class']['torus'])] += 1
for t in S3D:
    if t in tor:
        tor[t]['dmax'] = 24; tor[t]['at_max'] = c3d[t]; tor[t]['src'] = '3c+3d'
# dedupe by group: keep one torus per group (max N)
byg = {}
for t, v in tor.items():
    g = (v['n'], group(*t))
    if g not in byg or v['N'] > byg[g][1]['N']:
        byg[g] = (t, v)

rows = per_n()
En = {r['n']: r['d'] for r in rows}; Rn = {r['n']: r['R'] for r in rows}
print('Per group (one torus each), on-staircase n only (E==R) and n>=90:')
print(f"{'n':>4s} {'torus':>7s} {'src':>12s} {'N conn':>7s} {'dmax':>4s} {'#=dmax':>6s} {'#=dmax-2':>8s} {'#=dmax-4':>8s} {'tail frac':>9s}")
for (n, g), (t, v) in sorted(byg.items()):
    if n >= 90 and v['dmax'] == En[n] == Rn[n]:
        print(f"{n:4d} {str(t):>7s} {v['src']:>12s} {v['N']:7d} {v['dmax']:4d} {v['at_max']:6d} {v['near']:8d} {v['near4']:8d} {v['at_max']/v['N']:9.2e}")

# residual vs log N(n) over staircase n, N = total connected classes over distinct groups at n
Nn = collections.defaultdict(int)
for (n, g), (t, v) in byg.items():
    Nn[n] += v['N']
TH = []
for d in range(6, 40, 2):
    idx = [i for i, r in enumerate(rows) if r['d'] >= d]
    if not idx:
        break
    i = idx[0]; TH.append((rows[i]['n'] + rows[i - 1]['n']) / 2); TH[-1] = (TH[-1], d)
thn = np.array([a for a, b in TH]); thd = np.array([b for a, b in TH], float)
for name in ('a*n^b', 'c*sqrt(n ln n)', 'A*sqrt(n)+B'):
    p, _ = fit_ls(name, thn, thd)
    ns = np.array([n for n in sorted(Nn) if n >= 60 and En[n] == Rn[n]], float)
    res = np.array([En[int(n)] + 1 - f(name, n, p) for n in ns])
    lN = np.log(np.array([Nn[int(n)] for n in ns], float))
    b, a = np.polyfit(lN, res, 1)
    rho = np.corrcoef(lN, res)[0, 1]
    # also: all n (including below-staircase), E - f
    ns2 = np.array([n for n in sorted(Nn) if n >= 60], float)
    res2 = np.array([En[int(n)] + 1 - f(name, n, p) for n in ns2]); lN2 = np.log([Nn[int(n)] for n in ns2])
    rho2 = np.corrcoef(lN2, res2)[0, 1]; b2 = np.polyfit(lN2, res2, 1)[0]
    print(f"{name:18s} fit on all thresholds (d>=6, n<=384): p={np.round(p,4)}  staircase n: slope d-resid per e-fold of N = {b:+.3f} (r={rho:+.2f}, m={len(ns)});  all n: slope {b2:+.3f} (r={rho2:+.2f}, m={len(ns2)})")

# within-n comparison across non-isomorphic groups: does the group with more classes reach higher d?
print('\nWithin-n, across non-isomorphic groups (both with >= 1 connected class): pairs by class count')
byn = collections.defaultdict(list)
for (n, g), (t, v) in byg.items():
    byn[n].append((v['N'], v['dmax'], t))
import sys
MINN = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = eq = lo = 0
ex = []
for n, L in sorted(byn.items()):
    if len(L) < 2:
        continue
    L.sort()
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            (Na, da, ta), (Nb, db, tb) = L[i], L[j]   # Nb >= Na
            if Nb < 2 * Na or Na < MINN:
                continue  # only pairs whose class counts differ by >= 2x
            if db > da: hi += 1
            elif db == da: eq += 1
            else: lo += 1; ex.append((n, tb, Nb, db, ta, Na, da))
print(f'  (smaller group N >= {MINN}) pairs with N ratio >= 2: larger-N group higher d: {hi}, equal: {eq}, lower: {lo}')
print('  cases where the larger-N group is LOWER:', ex)
