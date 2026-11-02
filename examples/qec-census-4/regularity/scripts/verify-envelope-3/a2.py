"""Within-n pairs of non-isomorphic groups: does more classes -> higher dmax? Threshold sensitivity.
Dedup: one row per (n, group); prefer a torus whose dmax is settled (no class possibly above)."""
import json, collections, math, itertools
from scipy.stats import binomtest
R = json.load(open('torus_rows.json'))
rows = list(R.values())
byg = {}
for r in rows:
    key = (r['n'], tuple(r['g']))
    # choose the torus with smallest 'above' (settled), then largest dmax
    cand = (r['above'], -r['dmax'])
    if key not in byg or cand < byg[key][0]: byg[key] = (cand, r)
G = [v[1] for v in byg.values()]
print('distinct (n,group) with connected classes:', len(G), ' unsettled kept:', [(g['t'], g['above']) for g in G if g['above']])
byn = collections.defaultdict(list)
for g in G: byn[g['n']].append(g)

def pairs(minN=0, ratio=2.0, settled_only=True, nmin=0):
    hi = eq = lo = 0; L = []
    for n, gs in byn.items():
        if n < nmin: continue
        for a, b in itertools.combinations(gs, 2):
            if settled_only and (a['above'] or b['above']): continue
            if a['N'] > b['N']: a, b = b, a
            if a['N'] < minN or b['N'] < ratio * a['N']: continue
            s = (b['dmax'] > a['dmax']) - (b['dmax'] < a['dmax'])
            hi += s > 0; eq += s == 0; lo += s < 0
            L.append((n, a['t'], a['N'], a['dmax'], b['t'], b['N'], b['dmax'], round(b['N']/a['N'], 1)))
    return hi, eq, lo, L

for settled in (False, True):
    print(f"\nsettled_only={settled}; ratio>=2")
    for mn in (0, 1, 50, 100, 200, 300, 500, 700, 1000, 1500, 2000, 3000):
        hi, eq, lo, L = pairs(mn, 2.0, settled)
        p = binomtest(hi, hi+lo, 0.5).pvalue if hi+lo else float('nan')
        print(f"  minN>={mn:5d}: higher {hi:3d} equal {eq:3d} lower {lo:3d}  (pairs {len(L):3d}; sign-test p={p:.3g}); median ratio {sorted(x[-1] for x in L)[len(L)//2] if L else None}")
hi, eq, lo, L = pairs(1000, 2.0, False)
print('\nminN>=1000 pairs (all):')
for x in sorted(L): print('  ', x)
print('\nratio>=1 (all pairs with N differing), various minN:')
for mn in (0, 500, 1000, 2000):
    hi, eq, lo, L = pairs(mn, 1.0001, True)
    print(f"  minN>={mn}: higher {hi} equal {eq} lower {lo}")
