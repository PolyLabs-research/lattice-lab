# Part 3f: with the additive -k fixed, which n-function? (k<=16, fit n<=300, test n>300); all 2-param
from load import *
from scipy import optimize
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
sel=K<=16
M={'c n^b - k':(lambda p,n:p[0]*n**p[1],[2.3,0.44]),
   'c sqrt(n) + e - k':(lambda p,n:p[0]*np.sqrt(n)+p[1],[1.5,2]),
   'c sqrt(n ln n) + e - k':(lambda p,n:p[0]*np.sqrt(n*np.log(n))+p[1],[0.6,2]),
   'c n^0.6 + e - k':(lambda p,n:p[0]*n**0.6+p[1],[0.8,2]),
   'c sqrt(n ln n) - k [1p]':(lambda p,n:p[0]*np.sqrt(n*np.log(n)),[0.6]),
   'c sqrt(n) - k [1p]':(lambda p,n:p[0]*np.sqrt(n),[1.5])}
for cut in (300,200):
  print(f"--- fit k<=16, n<={cut}; test n>{cut} (k<=16)")
  tr=sel&(N<=cut); te=sel&(N>cut)
  for nm,(g,p0) in M.items():
    p=optimize.least_squares(lambda p:g(p,N[tr])-K[tr]-Dd[tr],p0).x; pr=g(p,N)-K
    e=Dd[te]-pr[te]; pe=2*np.maximum(1,np.round(pr[te]/2))
    et=Dd[tr]-pr[tr]
    print(f"  {nm:26s} p=({', '.join(f'{x:.3f}' for x in p)}) train rms {np.sqrt(np.mean(et**2)):.2f} | test N={te.sum()} rms {np.sqrt(np.mean(e**2)):.2f} bias {np.mean(e):+.2f} within2 {np.mean(np.abs(pe-Dd[te])<=2):.2f} exact {np.mean(pe==Dd[te]):.2f}")
