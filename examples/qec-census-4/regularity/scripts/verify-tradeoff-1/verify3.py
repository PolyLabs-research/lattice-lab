import math, numpy as np
from scipy import optimize
P=np.load('frontier.npy'); N,K,D=P.T
ns=sorted(set(N.astype(int)))
env={n:D[N==n].max() for n in ns}; kmin={n:int(K[N==n].min()) for n in ns}
bands=[(a,a+50) for a in range(0,400,50)]
def bandcmp(f,label):
    out=[]
    for a,b in bands:
        idx=[n for n in ns if a<n<=b]
        o={n:env[n]/math.sqrt(n) for n in idx}; j=max(o,key=o.get)
        out.append(o[j]-f(j,kmin[j])/math.sqrt(j))
    out=np.array(out)
    print(f'  {label:58s} ' + ' '.join(f'{x:+.3f}' for x in out) + f' | max|.| {np.abs(out).max():.3f} #>0.03 {(np.abs(out)>0.03).sum()}')
# k=4 frontier only, fit n<=300, models with no k at all
m=(K==4)&(N<=300); n4=N[m]; d4=D[m]
print('k=4 frontier points n<=300:',m.sum(),' all:',(K==4).sum())
def fit(g,p0,lab):
    p=optimize.least_squares(lambda p:g(p,n4)-d4,p0).x
    t=(K==4)&(N>300); r=D[t]-g(p,N[t])
    bandcmp(lambda n,k:g(p,n),f'k=4-only {lab} p={np.round(p,3)} [k=4 test rms {np.sqrt(np.mean(r**2)):.2f}]')
fit(lambda p,n:p[0]*np.sqrt(n)-4,[1.7],'c sqrt n - 4 [1p]')
fit(lambda p,n:p[0]*np.sqrt(n)+p[1],[1.7,-4],'a sqrt n + b')
fit(lambda p,n:p[0]*n**p[1],[0.8,0.6],'c n^b')
fit(lambda p,n:p[0]*np.sqrt(n*np.log(n))+p[1],[0.6,0],'c sqrt(n ln n)+e')
fit(lambda p,n:p[0]*np.sqrt(n*np.log(n)),[0.6],'c sqrt(n ln n) [1p]')
fit(lambda p,n:p[0]*n**0.6,[0.8],'c n^0.6 [1p]')
fit(lambda p,n:p[0]*n**0.6+p[1],[0.8,0],'c n^0.6 + e')
# how much of the claimed agreement is the k=4 constant: claimed model at kmin=4 is 1.692 sqrt n - 4
print('band-max carriers kmin:',[ (a,max((env[n]/math.sqrt(n),n) for n in ns if a<n<=b)) for a,b in bands])
# In-sample vs out-of-sample bands for the claimed model
