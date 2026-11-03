"""Noncentrality proxy for distinguishability: generate NOISE-FREE thresholds from the true model T
(fit to the real data), fit the wrong model W by LS, expected dAICc ~ RSS_W/s^2 (+ param-count term).
Optimistic (no extreme-value noise, no grid rounding). Report smallest N_max with E[dAICc] >= 4 and >= 10."""
import itertools, numpy as np
from base2 import *
NM=[400,600,800,1000,1500,2000,3000,5000,10000,20000,50000,1e5]
def thr_from(T,p,dmin,nmax):
    xs=[];ds=[]
    for d in range(dmin,4000,2):
        c=crossing(T,p,d)
        if not c==c or c>nmax: break
        xs.append(c); ds.append(d)
    return np.array(xs),np.array(ds,float)
for dmin in (6,14):
    th=[t for t in thresholds() if t[0]>=dmin]
    x=np.array([(a+b)/2 for d,a,b in th]); y=np.array([d for d,a,b in th],float)
    P={m:fit(m,x,y)[0] for m in KEYS}
    s=0.15
    print(f'\n--- fits on real thresholds d>={dmin}; s={s}; N_max where expected dAICc(W vs T) first >= 4 / >= 10 ---')
    for T,W in itertools.permutations(KEYS,2):
        hit4=hit10=None
        for N in NM:
            xs,ds=thr_from(T,P[T],dmin,N)
            pw,rss=fit(W,xs,ds)
            k=len(MODELS[W][1])-len(MODELS[T][1])
            dA=rss/s**2+2*k
            if hit4 is None and dA>=4: hit4=N
            if hit10 is None and dA>=10: hit10=N; break
        print(f'  true {T:20s} wrong {W:20s}: >=4 at N~{hit4}   >=10 at N~{hit10}')
