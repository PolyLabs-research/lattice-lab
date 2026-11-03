"""Per-torus top-of-distribution counts with honest bounds; record-setting n; group dedup check."""
import json, collections, math, sys
sys.path.insert(0, '.')
from load3 import load, grp, evdown
T, d3 = load()
# apply 3d: classes with lower 23/upper 24 -> exact 24 (they were unfinished in 3b/3c)
fix = {}
for t, L in d3.items():
    for r in L:
        if r['distqldpc'].get('d') == 24:
            fix[(t, json.dumps(r['class']['A']), json.dumps(r['class']['B']), r['class']['k'])] = 24
# need A,B in classes; reload with A,B
import glob
from pathlib import Path
EX = Path('/home/user/lattice-lab/examples')
for st in ('qec-census-3b', 'qec-census-3c'):
    for x in open(EX/st/'records.jsonl'):
        r = json.loads(x)
        t = (r.get('l'), r.get('m'))
        if r.get('job') != 'torus' or t not in d3: continue
        cl = []; nfix = 0
        for y in r['rows']:
            if not y.get('connected') or y['k'] <= 0: continue
            e = y.get('exact'); d = e['d'] if (e and e.get('status') == 'complete') else None
            kk = (t, json.dumps(y['A']), json.dumps(y['B']), y['k'])
            if kk in fix: d = fix[kk]; nfix += 1
            cl.append((y['k'], d, y.get('upper')))
        T[t]['cl'] = cl; T[t]['src'] += '+3d'; T[t]['nfix'] = nfix

rows = {}
for t, v in T.items():
    cl = v['cl']
    if not cl: continue
    ex = [d for k, d, u in cl if d is not None]
    dmax = max(ex)
    # can any non-exact class exceed dmax? (upper > dmax)
    above = sum(1 for k, d, u in cl if d is None and (u is None or evdown(u) > dmax))
    lo_max = sum(1 for d in ex if d == dmax)
    hi_max = lo_max + sum(1 for k, d, u in cl if d is None and (u is None or evdown(u) >= dmax))
    lo_m2 = sum(1 for d in ex if d == dmax-2)
    hi_m2 = lo_m2 + sum(1 for k, d, u in cl if d is None and (u is None or evdown(u) >= dmax-2))
    upeq_m2 = sum(1 for k, d, u in cl if (d if d is not None else evdown(u)) == dmax-2)  # analyst-style
    rows[t] = dict(t=t, n=v['n'], g=grp(*t), src=v['src'], N=len(cl), dmax=dmax, above=above,
                   lo_max=lo_max, hi_max=hi_max, lo_m2=lo_m2, hi_m2=hi_m2, upeq_m2=upeq_m2,
                   nexact=len(ex), nfix=v.get('nfix', 0))
json.dump({str(k): v for k, v in rows.items()}, open('torus_rows.json', 'w'), default=list)
# isomorphic duplicates: same N, same dmax?
byg = collections.defaultdict(list)
for t, r in rows.items(): byg[(r['n'], r['g'])].append(r)
print('isomorphic groups with >1 torus:')
for g, L in sorted(byg.items()):
    if len(L) > 1:
        print('  ', g, [(r['t'], r['src'], r['N'], r['dmax'], r['lo_max']) for r in L])
print('tori with non-exact classes possibly above dmax:', [(r['t'], r['above']) for r in rows.values() if r['above']])
# E(n) from census-data.json (settled best connected over all k)
D = json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
En = collections.defaultdict(int)
for e in D['entries']:
    if e['settled']: En[e['n']] = max(En[e['n']], e['d'])
rec = []; run = 0
for n in sorted(En):
    if En[n] > run: rec.append(n); run = En[n]
print('record-setting n (first n with each new E):', [(n, En[n]) for n in rec])
# my per-torus dmax vs census-data E(n)
myE = collections.defaultdict(int)
for r in rows.values(): myE[r['n']] = max(myE[r['n']], r['dmax'])
diff = [(n, En[n], myE[n]) for n in sorted(set(En) | set(myE)) if En.get(n, 0) != myE.get(n, 0)]
print('E(n) mismatches census-data vs mine:', diff)
print('\nAt record-setting n (n>=60), every group at that n reaching E(n):')
print(f"{'n':>4} {'torus':>8} {'src':>7} {'N':>6} {'dmax':>4} {'#dmax lo..hi':>14} {'#dmax-2 lo..hi':>16} {'exact/N':>9}")
for n in rec:
    if n < 60: continue
    for r in sorted(rows.values(), key=lambda r: -r['N']):
        if r['n'] == n and r['dmax'] == En[n]:
            print(f"{n:4d} {str(r['t']):>8} {r['src']:>7} {r['N']:6d} {r['dmax']:4d} {r['lo_max']:6d}..{r['hi_max']:<6d} {r['lo_m2']:7d}..{r['hi_m2']:<7d} {r['nexact']:4d}/{r['N']}")
