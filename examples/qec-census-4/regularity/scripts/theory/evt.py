import json, glob, math, os, collections
import numpy as np
rows=[]
for f in sorted(glob.glob('/home/user/lattice-lab/examples/qec-census-3/data/*.jsonl')):
    L=open(f).read().splitlines()
    head=json.loads(L[0]); l,m,n=head['l'],head['m'],head['n']
    recs=[json.loads(x) for x in L[1:]]
    for kk in ['k4','all']:
        ds=[r['d'] for r in recs if r.get('connected') and r['k']>0 and r.get('status')=='complete' and r['d'] is not None and (kk=='all' or r['k']==4)]
        inc=sum(1 for r in recs if r.get('connected') and r['k']>0 and r.get('status')!='complete' and (kk=='all' or r['k']==4))
        if len(ds)<5: continue
        x=np.array(ds)/math.sqrt(n)
        rows.append(dict(torus=f"{l}x{m}",l=l,m=m,n=n,g=math.gcd(l,m),kk=kk,M=len(ds),inc=inc,mean=x.mean(),sd=x.std(),q90=np.quantile(x,.9),mx=x.max(),dmax=max(ds)))
json.dump(rows,open('evt_rows.json','w'))
# dedupe by group (g, lm/g) keep the torus with more classes
for kk in ['k4','all']:
    R=[r for r in rows if r['kk']==kk]
    byg={}
    for r in R:
        key=(r['g'],r['l']*r['m']//r['g'])
        if key not in byg or r['M']>byg[key]['M']: byg[key]=r
    R=sorted(byg.values(),key=lambda r:r['n'])
    print(f"== {kk}: {len(R)} groups (dedup)")
    print("torus n M mean sd max (max-mean)/sd sqrt(2lnM)")
    for r in R:
        z=(r['mx']-r['mean'])/r['sd'] if r['sd']>0 else float('nan')
        print(f"{r['torus']:6s} {r['n']:4d} {r['M']:5d} {r['mean']:.3f} {r['sd']:.3f} {r['mx']:.3f} {z:5.2f} {math.sqrt(2*math.log(r['M'])):5.2f} inc={r['inc']}")
    n=np.array([r['n'] for r in R]); M=np.array([r['M'] for r in R]); mean=np.array([r['mean'] for r in R]); mx=np.array([r['mx'] for r in R]); sd=np.array([r['sd'] for r in R])
    sel=M>=20
    for name,y in [('mean',mean),('max',mx),('sd',sd),('M',M)]:
        b=np.polyfit(np.log(n[sel]),np.log(y[sel]),1)
        print(name,'log-log slope vs n (groups with M>=20): %.3f'%b[0])
