# Independent recomputation of the "tradeoff" claim: d = c n^b - k fitted on n<=300 frontier, scored on n>300
import json, math, collections, sys
import numpy as np
from scipy import optimize
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
E=json.load(open(SP+'/census-data.json'))['entries']
# group key (gcd, lcm): invariant factors of Z_l x Z_m
grp=lambda e:(math.gcd(e['l'],e['m']), e['l']*e['m']//math.gcd(e['l'],e['m']))
# consistency of isomorphic duplicates
byg=collections.defaultdict(set)
for e in E: byg[(grp(e),e['k'])].add(e['d'])
print('isomorphic duplicate groups with inconsistent d:',[ (g,s) for g,s in byg.items() if len(s)>1])
F={}
for e in E:
    key=(e['n'],e['k']); F[key]=max(F.get(key,0),e['d'])
pts=np.array(sorted((n,k,d) for (n,k),d in F.items()),float)
N,K,D=pts.T
print('frontier points',len(pts),' n<=300:',int((N<=300).sum()),' n>300:',int((N>300).sum()), 'test n range',N[N>300].min(),N[N>300].max())
print('test k counts',collections.Counter(K[N>300].astype(int)))
def even(x): return 2*np.maximum(1,np.round(x/2))
M={
 'A1 c n^b - k [2p]':(lambda p,n,k:p[0]*n**p[1]-k,[0.5,0.65]),
 'A2 c n^b - a k [3p]':(lambda p,n,k:p[0]*n**p[1]-p[2]*k,[0.5,0.65,1]),
 'A0 c sqrt(n) - k [1p]':(lambda p,n,k:p[0]*np.sqrt(n)-k,[1.5]),
 'A3 c sqrt(n)+e-k [2p]':(lambda p,n,k:p[0]*np.sqrt(n)+p[1]-k,[1.5,0]),
 'P1 c n^b k^-1/2 [2p]':(lambda p,n,k:p[0]*n**p[1]*k**-0.5,[1,0.6]),
 'P2 c n^b k^-g [3p]':(lambda p,n,k:p[0]*n**p[1]*k**-p[2],[1,0.6,0.5]),
 'Z0 c n^b (no k) [2p]':(lambda p,n,k:p[0]*n**p[1],[1,0.6]),
}
def stats(pred,d):
    e=d-pred; pe=even(pred)
    return dict(N=len(d),rms=float(np.sqrt(np.mean(e**2))),bias=float(np.mean(e)),w2=float(np.mean(np.abs(pe-d)<=2)),ex=float(np.mean(pe==d)),
                nclamp_exact=int(np.sum((pred<1)&(pe==d))))
def run(trmask,temask,label,models=M,verbose=True):
    out={}
    for name,(f,p0) in models.items():
        s=optimize.least_squares(lambda p:f(p,N[trmask],K[trmask])-D[trmask],p0,max_nfev=20000)
        p=s.x; pr=f(p,N,K)
        a=stats(pr[trmask],D[trmask]); b=stats(pr[temask],D[temask])
        out[name]=(p,pr,a,b)
        if verbose: print(f"  {name:24s} p=({', '.join(f'{x:.4g}' for x in p)}) train N={a['N']} rms={a['rms']:.2f} | test N={b['N']} rms={b['rms']:.2f} bias={b['bias']:+.2f} w2={b['w2']:.2f} exact={b['ex']:.2f} (exact via clamp<1: {b['nclamp_exact']})")
    return out
print('\n=== CLAIMED SPLIT: train n<=300, test n>300, all k')
R=run(N<=300,N>300,'claim')
p,pr,_,_=R['A1 c n^b - k [2p]']
te=N>300
print('\nA1 test residuals by k (d - pred), and even-rounded pred:')
for kk in sorted(set(K[te])):
    m=te&(K==kk)
    print(f"  k={int(kk):2d}: "+' '.join(f"{int(n)}:{int(d)}/{int(even(q))}({d-q:+.1f})" for n,d,q in zip(N[m],D[m],pr[m])))
# by k-stratum
for lo,hi in ((4,8),(10,16),(18,40)):
    m=te&(K>=lo)&(K<=hi)
    for nm in ('A1 c n^b - k [2p]','P1 c n^b k^-1/2 [2p]','Z0 c n^b (no k) [2p]'):
        s=stats(R[nm][1][m],D[m]); print(f"  test k in [{lo},{hi}] {nm:24s} N={s['N']} rms={s['rms']:.2f} bias={s['bias']:+.2f} w2={s['w2']:.2f} ex={s['ex']:.2f}")
import pickle; pickle.dump((pts,F),open(SP+'/regularity/verify-tradeoff-0/frontier.pkl','wb'))
