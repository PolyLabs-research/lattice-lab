import json, math, collections
import numpy as np
from scipy import optimize
P=np.load('frontier.npy'); N,K,D=P.T
ns=sorted(set(N.astype(int)))
env={n:D[N==n].max() for n in ns}; kmin={n:int(K[N==n].min()) for n in ns}
nA=np.array(ns,float); eA=np.array([env[n] for n in ns]); kA=np.array([kmin[n] for n in ns],float)
bands=[(a,a+50) for a in range(0,400,50)]
def bandcmp(f,label):
    out=[]
    for a,b in bands:
        idx=[i for i,n in enumerate(ns) if a<n<=b]
        o=eA[idx]/np.sqrt(nA[idx]); j=idx[int(np.argmax(o))]
        out.append(o.max()-f(nA[j],kA[j])/math.sqrt(nA[j]))
    out=np.array(out)
    print(f'  {label:52s} band diffs ' + ' '.join(f'{x:+.3f}' for x in out) + f' | max|.| {np.abs(out).max():.3f}  #>0.03: {(np.abs(out)>0.03).sum()}')
    return out
tr=nA<=300
print('Band-max diffs (observed band max of env/sqrt n minus model at the same n), 8 bands:')
bandcmp(lambda n,k:1.692*math.sqrt(n)-k,'claimed: 1.692 sqrt n - kmin (fit k<=16 frontier)')
# k-free envelope models fitted only on envelope n<=300
def fit(g,p0,label):
    p=optimize.least_squares(lambda p:g(p,nA[tr])-eA[tr],p0).x
    r=eA-g(p,nA)
    print(f'{label}: p={np.round(p,4)} | env in-sample rms {np.sqrt(np.mean(r[tr]**2)):.2f} | env n>300 rms {np.sqrt(np.mean(r[~tr]**2)):.2f} bias {r[~tr].mean():+.2f} within2 {np.mean(np.abs(r[~tr])<=2):.2f}')
    bandcmp(lambda n,k:g(p,n),'   k-free '+label)
fit(lambda p,n:p[0]*np.sqrt(n)-p[1],[1.6,4],'a sqrt n - b')
fit(lambda p,n:p[0]*n**p[1],[0.8,0.6],'c n^b')
fit(lambda p,n:p[0]*np.sqrt(n*np.log(n))+p[1],[0.6,0],'c sqrt(n ln n) + e')
fit(lambda p,n:p[0]*np.sqrt(n*np.log(n)),[0.6],'c sqrt(n ln n) [1p]')
fit(lambda p,n:p[0]*n**0.6,[0.8],'c n^0.6 [1p]')
fit(lambda p,n:p[0]*np.sqrt(n),[1.3],'c sqrt n [1p, no offset]')
bandcmp(lambda n,k:0.8011*n**0.6074,'registered envelope 0.8011 n^0.6074')
# free-coefficient k model on the frontier (k<=16, n<=300), applied with kmin
s=(K<=16)&(N<=300)
X=np.c_[np.sqrt(N[s]),-K[s],np.ones(s.sum())]; b,*_=np.linalg.lstsq(X,D[s],rcond=None)
bandcmp(lambda n,k:b[0]*math.sqrt(n)-b[1]*k+b[2],f'free fit c sqrt n - a k + e = ({b[0]:.3f},{b[1]:.3f},{b[2]:+.2f})')
X=np.c_[np.sqrt(N[s]),-K[s]]; b2,*_=np.linalg.lstsq(X,D[s],rcond=None)
bandcmp(lambda n,k:b2[0]*math.sqrt(n)-b2[1]*k,f'free fit c sqrt n - a k = ({b2[0]:.3f},{b2[1]:.3f})')
X=np.c_[np.sqrt(N[s]),np.ones(s.sum())]; b3,*_=np.linalg.lstsq(X,D[s]+K[s],rcond=None)
bandcmp(lambda n,k:b3[0]*math.sqrt(n)+b3[1]-k,f'c sqrt n + e - k = ({b3[0]:.3f},{b3[1]:+.2f})')
# misspecification: (d+k)/sqrt n vs n, per k (k<=16)
print('\n(d+k)/sqrt(n) on the frontier, mean by 50-band (k<=16) and per-k slope vs n:')
for a,bb in bands:
    m=(K<=16)&(N>a)&(N<=bb)
    if m.sum(): print(f'  ({a},{bb}] N={m.sum():3d} mean {np.mean((D[m]+K[m])/np.sqrt(N[m])):.3f}')
from scipy import stats
for k in sorted(set(K[K<=16].astype(int))):
    m=K==k
    if m.sum()>=6:
        r=stats.linregress(N[m],(D[m]+k)/np.sqrt(N[m]))
        print(f'  k={k:2d} N={m.sum():2d} slope per 100 n {100*r.slope:+.3f} +- {100*r.stderr:.3f}')
# kmin=4 points only: d/sqrt n = c - 4/sqrt n  <=> (d+4)/sqrt n const
m=(K==4)
r=stats.linregress(N[m],(D[m]+4)/np.sqrt(N[m])); print(f'  k=4 only: (d+4)/sqrt n slope per 100n {100*r.slope:+.4f}+-{100*r.stderr:.4f}')
