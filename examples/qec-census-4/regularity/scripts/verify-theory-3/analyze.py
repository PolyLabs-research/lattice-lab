import json, collections, math
import numpy as np
from scipy import stats
R=json.load(open('all_D.json'))
print('all conn',all(r['conn'] for r in R),'all surj',all(r['surj'] for r in R), 'D None', sum(r['D'] is None for r in R))
byn=collections.defaultdict(list)
for r in R: byn[r['n']].append(r)
def grp(r): g=math.gcd(r['l'],r['m']); return (g, r['l']*r['m']//g)
print('\n== Their selection: max d per n (tie: smaller k) ==')
rows=[]
for n in sorted(byn):
    mx=max(byn[n],key=lambda e:(e['d'],-e['k']))
    ms=max(byn[n],key=lambda e:e['score'])
    rows.append((n,mx['d'],mx['k'],mx['D'],f"{mx['l']}x{mx['m']}",ms['k'],ms['d'],ms['score'],ms['D'],min(e['D'] for e in byn[n] if e['d']==mx['d'])))
for x in rows: print(x)
N=np.array([x[0]/2 for x in rows]); Dmx=np.array([x[3] for x in rows]); Dsc=np.array([x[8] for x in rows]); Dmin=np.array([x[9] for x in rows])
print('maxd-code D counts by n band:')
for lo in range(0,401,50):
    sel=(2*N>lo)&(2*N<=lo+50)
    if sel.any(): print(lo,lo+50,'maxd',dict(collections.Counter(Dmx[sel].tolist())),'bestscore',dict(collections.Counter(Dsc[sel].tolist())),'min D among tied max-d',dict(collections.Counter(Dmin[sel].tolist())))
print('spearman D(maxd) vs N',stats.spearmanr(N,Dmx))
print('spearman D(bestscore) vs N',stats.spearmanr(N,Dsc))
print('\n== All entries, D distribution by n band ==')
for lo in range(0,401,50):
    s=[r for r in R if lo<r['n']<=lo+50]
    print(lo,lo+50,len(s),dict(sorted(collections.Counter(r['D'] for r in s).items())))
print('\n== All entries, dedup by (n,group,k) ==')
dd={}
for r in R:
    key=(r['n'],grp(r),r['k'])
    if key not in dd or r['D']<dd[key]['D']: dd[key]=r
for lo in range(0,401,50):
    s=[r for r in dd.values() if lo<r['n']<=lo+50]
    print(lo,lo+50,len(s),dict(sorted(collections.Counter(r['D'] for r in s).items())))
print('\n== Per k: D of settled frontier entries vs n ==')
for k in sorted({r['k'] for r in R}):
    s=sorted([r for r in R if r['k']==k],key=lambda r:r['n'])
    if len(s)>=8: print(k,[(r['n'],r['d'],r['D']) for r in s][-12:])
