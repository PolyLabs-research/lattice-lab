import math, numpy as np
from scipy import optimize
P=np.load('frontier.npy'); N,K,D=P.T
r=D-(1.692*np.sqrt(N)-K)
print('claimed-model mean residual by k (k<=16) and by n-band for k=4:')
for k in (4,6,8,10,12,14,16):
    m=K==k; print(f'  k={k:2d} N={m.sum():2d} mean {r[m].mean():+.2f}  n<=150 {r[m&(N<=150)].mean():+.2f}  150<n<=300 {r[m&(N>150)&(N<=300)].mean():+.2f}  n>300 {r[m&(N>300)].mean() if (m&(N>300)).any() else float("nan"):+.2f}')
for a in range(0,400,50):
    m=(K==4)&(N>a)&(N<=a+50); print(f'  k=4 ({a},{a+50}] N={m.sum()} mean resid {r[m].mean():+.2f}')
s=K<=16; tr=s&(N<=300); te=s&(N>300)
M={'c sqrt n - k [1p]':(lambda p,n:p[0]*np.sqrt(n),[1.6]),
   'c sqrt n + e - k':(lambda p,n:p[0]*np.sqrt(n)+p[1],[1.5,0]),
   'c sqrt(n ln n) + e - k':(lambda p,n:p[0]*np.sqrt(n*np.log(n))+p[1],[0.6,0]),
   'c n^0.6 + e - k':(lambda p,n:p[0]*n**0.6+p[1],[0.8,0])}
for nm,(g,p0) in M.items():
    p=optimize.least_squares(lambda p:g(p,N[tr])-K[tr]-D[tr],p0).x
    e=D-(g(p,N)-K)
    print(f'{nm:24s} p={np.round(p,3)} train rms {np.sqrt(np.mean(e[tr]**2)):.2f} test N={te.sum()} rms {np.sqrt(np.mean(e[te]**2)):.2f} bias {e[te].mean():+.2f}')
