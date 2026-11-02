# Population-level check: is d+k~const a property of the max (extreme value) only, or of the whole class population?
import json, math, collections, numpy as np
from scipy import stats
from classes import load, inv
P='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
E=json.load(open(P))['entries']
best={}
for e in E:
    key=(inv(e['l'],e['m']),e['k'])
    if key not in best or e['d']>best[key]['d']: best[key]=e
fr=collections.defaultdict(dict); N={}
for (g,k),e in best.items(): fr[g][k]=e['d']; N[g]=e['n']
T=load()
# one representative torus per group (the one with most rows) - classes on isomorphic tori are the same codes
pop=collections.defaultdict(lambda: collections.defaultdict(list))
rep={}
for t,v in T.items():
    g=inv(*t)
    if g not in rep or len(v['rows'])>len(T[rep[g]]['rows']): rep[g]=t
for g,t in rep.items():
    for r in T[t]['rows']:
        if not r['conn']: continue
        val=r['d'] if r['complete'] else r['upper']
        if val is None: continue
        pop[g][r['k']].append(val)
groups=[g for g in fr if len(fr[g])>=4]
print('groups',len(groups))
cnt_rho=[]; res=[]
for g in sorted(groups,key=lambda g:N[g]):
    ks=sorted(fr[g]); 
    cnts=[len(pop[g][k]) for k in ks]
    mx=[max(pop[g][k]) if pop[g][k] else None for k in ks]
    med=[np.median(pop[g][k]) if pop[g][k] else None for k in ks]
    q90=[np.percentile(pop[g][k],90) if pop[g][k] else None for k in ks]
    ok = all(c>0 for c in cnts)
    line=f"n={N[g]:3d} G={g} stage={T[rep[g]]['stage']}  k:(#classes, frontier d, max-in-pop, median, q90) "+' '.join(f"{k}:({c},{fr[g][k]},{m},{md},{q})" for k,c,m,md,q in zip(ks,cnts,mx,med,q90))
    print(line)
    if ok and len(ks)>=4:
        cnt_rho.append(stats.spearmanr(ks,cnts).correlation)
        K=np.array(ks,float)
        for name,vals in (('frontier',[fr[g][k] for k in ks]),('median',med),('q90',q90)):
            v=np.array(vals,float); lr=stats.linregress(K,v)
            res.append((g,name,-lr.slope,np.std(v+K)/np.mean(v+K), N[g]))
print('\nSpearman(k, #classes) within group: median',np.median(cnt_rho),' fraction negative',np.mean(np.array(cnt_rho)<0), 'n=',len(cnt_rho))
for name in ('frontier','median','q90'):
    a=np.array([r[2] for r in res if r[1]==name]); c=np.array([r[3] for r in res if r[1]==name]); n=np.array([r[4] for r in res if r[1]==name])
    print(f"{name:8s}: groups={len(a)} median slope a={np.median(a):.2f} IQR {np.percentile(a,25):.2f}-{np.percentile(a,75):.2f}; median CV(v+k)={np.median(c):.3f}; Spearman(n,a)={stats.spearmanr(n,a).correlation:.2f}")
