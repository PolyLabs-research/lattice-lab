"""Lottery sensitivity of the frontier itself: at each n, pool the classes of all distinct groups
(settled) and ask how much E(n)=max would drop if only a fraction 1/e (or 1/10) of the classes were
available (top level only: 2*P(subset misses all c top classes); c = pooled count at E(n), lo..hi)."""
import json, collections, math
import numpy as np
R = json.load(open('torus_rows.json'))
byg = {}
for r in R.values():
    key = (r['n'], tuple(r['g'])); cand = (r['above'], -r['dmax'])
    if key not in byg or cand < byg[key][0]: byg[key] = (cand, r)
G = [v[1] for v in byg.values() if v[1]['above'] == 0]
byn = collections.defaultdict(list)
for g in G: byn[g['n']].append(g)
E = {n: max(g['dmax'] for g in gs) for n, gs in byn.items()}
run = 0; rec = set()
for n in sorted(E):
    if E[n] > run: rec.add(n); run = E[n]
rows = []
for n in sorted(byn):
    if n < 60: continue
    gs = byn[n]; Nt = sum(g['N'] for g in gs)
    clo = sum(g['lo_max'] for g in gs if g['dmax'] == E[n]); chi = sum(g['hi_max'] for g in gs if g['dmax'] == E[n])
    f = 1/math.e
    dlo = 2*(1-f)**chi; dhi = 2*(1-f)**clo   # drop per e-fold: bounds (more top classes => smaller drop)
    rows.append((n, Nt, E[n], clo, chi, dlo, dhi, n in rec, all(g['src'] == '3a' for g in gs)))
print(f"{'n':>4} {'Ntot':>6} {'E':>3} {'c_top lo..hi':>13} drop/e-fold lo..hi  record")
for r in rows:
    if r[7] or r[0] % 30 == 0:
        print(f"{r[0]:4d} {r[1]:6d} {r[2]:3d} {r[3]:6d}..{r[4]:<6d} {r[5]:.2f}..{r[6]:.2f}  {'REC' if r[7] else ''}")
a = np.array([[r[5], r[6]] for r in rows]); rr = np.array([[r[5], r[6]] for r in rows if r[7]])
print(f"\nall n>=60 ({len(rows)}): mean drop per e-fold of classes {a[:,0].mean():.2f}..{a[:,1].mean():.2f}")
print(f"record n ({len(rr)}): mean drop per e-fold {rr[:,0].mean():.2f}..{rr[:,1].mean():.2f}")
