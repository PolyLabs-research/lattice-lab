# Part 3e: is the additive -k the key ingredient? other n-functions with additive k (2 params each)
from load import *
from scipy import optimize
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
M={'A1  c n^b - k':(lambda p,n,k:p[0]*n**p[1]-k,[2.3,0.44]),
   'B1  c sqrt(n) - a k':(lambda p,n,k:p[0]*np.sqrt(n)-p[1]*k,[1.5,1]),
   'B2  c sqrt(n ln n) - a k':(lambda p,n,k:p[0]*np.sqrt(n*np.log(n))-p[1]*k,[0.6,1]),
   'B3  c n^0.6 - a k':(lambda p,n,k:p[0]*n**0.6-p[1]*k,[0.8,1]),
   'B4  c sqrt(n) + e - k (offset)':(lambda p,n,k:p[0]*np.sqrt(n)+p[1]-k,[1.5,2]),
   'P1  c n^b k^-1/2':(lambda p,n,k:p[0]*n**p[1]*k**-0.5,[1,0.6])}
tr=N<=300; te=~tr
for nm,(f,p0) in M.items():
    p=optimize.least_squares(lambda p:f(p,N[tr],K[tr])-Dd[tr],p0).x; pr=f(p,N,K)
    def s(m):
        e=Dd[m]-pr[m]; pe=2*np.maximum(1,np.round(pr[m]/2)); return np.sqrt(np.mean(e**2)),np.mean(e),np.mean(np.abs(pe-Dd[m])<=2)
    a=s(tr); b=s(te); b16=s(te&(K<=16))
    print(f"{nm:32s} p=({', '.join(f'{x:.3f}' for x in p)}) train rms {a[0]:.2f} | test rms {b[0]:.2f} bias {b[1]:+.2f} within2 {b[2]:.2f} | test k<=16 rms {b16[0]:.2f} bias {b16[1]:+.2f} within2 {b16[2]:.2f}")
