import json, glob, math, collections
import numpy as np
from scipy import stats
groups={}
for f in sorted(glob.glob('/home/user/lattice-lab/examples/qec-census-3/data/*.jsonl')):
    L=open(f).read().splitlines(); head=json.loads(L[0]); l,m,n=head['l'],head['m'],head['n']
    recs=[json.loads(x) for x in L[1:]]
    ds=[r['d'] for r in recs if r.get('connected') and r['k']==4 and r.get('status')=='complete' and r['d']]
    key=(math.gcd(l,m), l*m//math.gcd(l,m))
    if len(ds)>=20 and (key not in groups or len(ds)>len(groups[key][2])): groups[key]=(f"{l}x{m}",n,ds)
R=sorted(groups.values(),key=lambda t:t[1])
n=np.array([t[1] for t in R],float)
def stat(fn): return np.array([fn(np.array(t[2])) for t in R],float)
M=stat(len); mean=stat(np.mean); med=stat(np.median); q90=stat(lambda d:np.quantile(d,.9)); mx=stat(np.max); sd=stat(np.std)
z=(mx-mean)/sd
print("groups:",len(R),"n range",n.min(),n.max())
for name,y in [('mean d',mean),('median d',med),('q90 d',q90),('max d',mx),('sd d',sd)]:
    for lo in (0,60,100):
        s=n>=lo
        b=np.polyfit(np.log(n[s]),np.log(y[s]),1)
        print(f"{name:9s} n>={lo:3d}: d ~ n^{b[0]:.3f}  (groups {s.sum()})")
print("corr(z, sqrt(2 ln M)) =", stats.pearsonr(z,np.sqrt(2*np.log(M))))
print("mean z = %.2f, mean sqrt(2lnM) = %.2f"%(z.mean(),np.sqrt(2*np.log(M)).mean()))
# fraction of classes within 2 of max
fr=stat(lambda d:(d>=d.max()-2).mean())
print("fraction of k=4 classes with d >= dmax-2: median %.3f range %.3f-%.3f"%(np.median(fr),fr.min(),fr.max()))
for t,f_ in zip(R,fr): print(t[0],t[1],len(t[2]),'dmax',max(t[2]),'counts top3', collections.Counter(t[2]).most_common()[:0] or sorted(collections.Counter(t[2]).items())[-3:])
