exec(open('stats4.py').read().split('# gap regressions')[0].split('sk=np.array')[0])
import math
from scipy.special import gammaln
def lC(a,b): return gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1)
def emax_sub(d,N0):
    d=np.sort(d); Nn=len(d); E=0; prev=0
    for v in np.unique(d):
        c=(d<=v).sum(); P=math.exp(lC(c,N0)-lC(Nn,N0)) if c>=N0 else 0.0; E+=v*(P-prev); prev=P
    return E
for N0 in (20,50,100):
    s=[(g,v) for g,v in sel if len(v['d'])>=N0]
    nn=np.log([v['n'] for g,v in s]); mx=np.log([v['d'].max() for g,v in s]); e=np.log([emax_sub(v['d'],N0) for g,v in s])
    r1=stats.linregress(nn,mx); r2=stats.linregress(nn,e)
    print(f"N0={N0}: groups {len(s)} n {min(v['n'] for g,v in s)}-{max(v['n'] for g,v in s)}: max slope {r1.slope:.3f}+-{1.96*r1.stderr:.3f}, E[max of N0] slope {r2.slope:.3f}+-{1.96*r2.stderr:.3f}")
