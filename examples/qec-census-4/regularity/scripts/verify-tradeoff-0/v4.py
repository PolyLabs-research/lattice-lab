import json, math, collections, pickle
import numpy as np
from scipy import optimize
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
pts,F=pickle.load(open(SP+'/regularity/verify-tradeoff-0/frontier.pkl','rb'))
N,K,D=pts.T
def even(x): return 2*np.maximum(1,np.round(x/2))
def st(pred,d):
    e=d-pred; pe=even(pred)
    return f"N={len(d)} rms={np.sqrt(np.mean(e**2)):.2f} bias={np.mean(e):+.2f} w2={np.mean(np.abs(pe-d)<=2):.3f} ({int(np.sum(np.abs(pe-d)<=2))}) ex={np.mean(pe==d):.3f} ({int(np.sum(pe==d))})"
tr=N<=300; te=N>300
p=optimize.least_squares(lambda p:p[0]*N[tr]**p[1]-K[tr]-D[tr],[2.3,0.44]).x
pr=p[0]*N**p[1]-K
print('A1 as claimed:',st(pr[te],D[te]))
# (1) known published member of the family on an unfinished torus: [[360,12,24]] on 30x6 (=6x30), d=24 exact (docs/code-distances.md)
D2=D.copy(); i=np.where((N==360)&(K==12))[0][0]; print('test value at (360,12):',D[i],' pred',round(pr[i],2)); D2[i]=24
print('A1 with (360,12)->24 (a lower bound on the true frontier):',st(pr[te],D2[te]))
inc=te&np.isin(N,[360,384])
print('test points on n whose groups are not all computed (360: Z6xZ30; 384: Z4xZ48, Z8xZ24):',int(inc.sum()),list(zip(N[inc].astype(int),K[inc].astype(int),D[inc].astype(int))))
print('A1 on test points at fully computed n only:',st(pr[te&~inc],D[te&~inc]))
# (2) residual mean by k, train vs test
print('\nA1 mean residual d-pred by k: train | test')
for kk in sorted(set(K)):
    a=(K==kk)&tr; b=(K==kk)&te
    print(f"  k={int(kk):2d} train {np.mean(D[a]-pr[a]) if a.any() else np.nan:+.2f} (N={a.sum():2d}) | test {np.mean(D[b]-pr[b]) if b.any() else np.nan:+.2f} (N={b.sum()})")
# (3) the coefficient of k is not stable: fit d = c n^b - a k on n-windows (descriptive, in-sample)
print('\nfitted k-coefficient a in d = c n^b - a k on n windows (k<=16 and all k):')
for lo,hi in ((0,150),(150,250),(200,300),(300,400),(0,300),(0,400)):
    for kc in (16,99):
        m=(N>lo)&(N<=hi)&(K<=kc)
        q=optimize.least_squares(lambda p:p[0]*N[m]**p[1]-p[2]*K[m]-D[m],[2,0.45,1]).x
        # within-n slope: d on k with n fixed effects
        X=[];Y=[]
        for n in set(N[m]):
            mm=m&(N==n)
            if mm.sum()>=2: X+=list(K[mm]-K[mm].mean()); Y+=list(D[mm]-D[mm].mean())
        X=np.array(X);Y=np.array(Y); s=-np.sum(X*Y)/np.sum(X*X) if len(X) else np.nan
        print(f"  n in ({lo},{hi}] k<={kc:2d}: pts={m.sum():3d}  a(global fit)={q[2]:.3f}  within-n slope -dd/dk={s:.3f}")
# (4) A1 out-of-range sanity: negative d predictions at training points
neg=tr&(pr<2); print('\ntraining points where A1 predicts d<2 (unphysical; every code has d>=2):',list(zip(N[neg].astype(int),K[neg].astype(int),D[neg].astype(int),pr[neg].round(1))))
# (5) A1's implied d/sqrt(n) at fixed k peaks near n* = (k/(c b... )) : d/sqrt n = c n^(b-1/2) - k n^-1/2
for kk in (4,8,12,16):
    ns=np.arange(50,5000); r=(p[0]*ns**p[1]-kk)/np.sqrt(ns); print(f"  k={kk}: A1-implied d/sqrt(n) peaks at n={ns[np.argmax(r)]} value {r.max():.3f}")
print('A1 at [[756,16]] (known 30<=d<=34):',round(p[0]*756**p[1]-16,2))
