# Part 3b: global surfaces incl. additive/Singleton-like forms; fit (least squares in d) on n<=300, test n>300
from load import *
from scipy import optimize
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float)
N,K,Dd=pts.T
L=np.log
M={
 'P1  c n^b k^-1/2           [2p]':(lambda p,n,k:p[0]*n**p[1]*k**-0.5,[1,0.6]),
 'P2  c n^b k^-g             [3p]':(lambda p,n,k:p[0]*n**p[1]*k**-p[2],[1,0.6,0.5]),
 'P3  c (n/k)^b              [2p]':(lambda p,n,k:p[0]*(n/k)**p[1],[1,0.6]),
 'A1  c n^b - k              [2p]':(lambda p,n,k:p[0]*n**p[1]-k,[0.5,0.65]),
 'A1s c sqrt(n ln n) - k     [1p]':(lambda p,n,k:p[0]*np.sqrt(n*np.log(n))-k,[0.7]),
 'A2  c n^b - a k            [3p]':(lambda p,n,k:p[0]*n**p[1]-p[2]*k,[0.5,0.65,1]),
 'L1  c n^b (1-k/K)          [3p]':(lambda p,n,k:p[0]*n**p[1]*(1-k/p[2]),[0.5,0.65,30]),
 'S1  c n^b sqrt(1-k/K)      [3p]':(lambda p,n,k:p[0]*n**p[1]*np.sqrt(np.clip(1-k/p[2],1e-9,None)),[0.5,0.65,40]),
 'S2  sqrt(c n^b - s k)      [3p]':(lambda p,n,k:np.sqrt(np.clip(p[0]*n**p[1]-p[2]*k,1e-9,None)),[0.3,1.3,10]),
}
def even(x): return 2*np.maximum(1,np.round(x/2))
res={}
for kcap in (99,20):
  print(f"\n===== frontier points with k <= {kcap}")
  base=(K<=kcap)
  for name,(f,p0) in M.items():
    tr=base&(N<=300); te=base&(N>300)
    sol=optimize.least_squares(lambda p:f(p,N[tr],K[tr])-Dd[tr],p0,max_nfev=20000)
    p=sol.x; pr=f(p,N,K)
    def st(m):
        e=Dd[m]-pr[m]; pe=even(pr[m])
        return np.sqrt(np.mean(e**2)),np.mean(e),np.mean(np.abs(pe-Dd[m])<=2),np.mean(pe==Dd[m]),m.sum()
    a=st(tr);b=st(te)
    res[(kcap,name)]=(p,pr)
    print(f"{name} p=({', '.join(f'{x:.3g}' for x in p)})  TRAIN rms={a[0]:.2f}  | TEST N={b[4]} rms={b[0]:.2f} bias(d-pred)={b[1]:+.2f} |err|<=2:{b[2]:.2f} exact:{b[3]:.2f}")
pickle.dump((pts,res),open('part3b.pkl','wb'))
for name in ('A1  c n^b - k              [2p]','S1  c n^b sqrt(1-k/K)      [3p]','A2  c n^b - a k            [3p]'):
  p,pr=res[(99,name)]
  print('\n',name,'(k all) residual d - pred by k: TRAIN mean | TEST points n:d/pred_even')
  for kk in sorted(set(K)):
    m1=(K==kk)&(N<=300); m2=(K==kk)&(N>300)
    s=f"  k={int(kk):2d} train mean {np.mean(Dd[m1]-pr[m1]) if m1.any() else float('nan'):+.2f} (N={m1.sum()}) | "
    s+=' '.join(f"{int(n)}:{int(d)}/{int(even(q))}" for n,d,q in zip(N[m2],Dd[m2],pr[m2]))
    print(s)
