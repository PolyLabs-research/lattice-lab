from load import *
import numpy as np
from scipy import stats
t=load()
G={}
for (l,m),v in sorted(t.items()):
    if not v['rows']: continue
    g=grp(l,m)
    if g in G: continue  # isomorphic duplicate, identical distribution (checked)
    G[g]=dict(n=v['n'], d=np.array([r['d'] for r in v['rows']]), size=np.array([r['size'] for r in v['rows']]), tor=(l,m))
def emax_gauss(N):
    # E[max of N iid N(0,1)] by numeric integration
    x=np.linspace(-10,10,20001); F=stats.norm.cdf(x); f=stats.norm.pdf(x)
    return np.trapezoid(x*N*F**(N-1)*f,x)
rows=[]
for g,v in G.items():
    d=v['d']; N=len(d)
    rows.append(dict(g=g,n=v['n'],N=N,mean=d.mean(),med=np.median(d),p90=np.percentile(d,90),mx=d.max(),sd=d.std(ddof=1) if N>1 else np.nan,
        frac_top=np.mean(d>=d.max()-2), frac_max=np.mean(d==d.max()), nmax=int((d==d.max()).sum()), eg=emax_gauss(N)))
rows.sort(key=lambda r:(r['n'],r['N']))
for r in rows:
    print(f"{str(r['g']):9s} n={r['n']:3d} N={r['N']:5d} mean={r['mean']:5.2f} med={r['med']:4.1f} p90={r['p90']:4.1f} max={r['mx']:2d} nmax={r['nmax']:4d} sd={r['sd']:.2f} z={(r['mx']-r['mean'])/r['sd'] if r['sd']>0 else float('nan'):.2f} Egauss={r['eg']:.2f} fracTop2={r['frac_top']:.2f}")
import json
json.dump([{k:(list(v) if isinstance(v,tuple) else (float(v) if isinstance(v,(np.floating,np.integer)) else v)) for k,v in r.items()} for r in rows], open('rows.json','w'))
