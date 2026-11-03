import itertools, numpy as np
from base2 import *
from scipy.optimize import minimize
TH=thresholds()
# (1) interval (quantisation-exact) minimax: f(n_prev) < d <= f(n_first) for each threshold
def minimax(m, dmin, nmax=10**9):
    th=[t for t in TH if t[0]>=dmin and t[2]<=nmax]
    fn,p0=MODELS[m]
    def V(p):
        v=[max(d-fn(np.array(b),p), fn(np.array(a),p)-d, 0.0) for d,a,b in th]
        return max(v)
    best=None
    for s in np.linspace(0.6,1.4,9):
        p=np.array(fit(m,np.array([(a+b)/2 for d,a,b in th]),np.array([d for d,a,b in th],float))[0])
        r=minimize(V,p*([s]+[1]*(len(p)-1)),method='Nelder-Mead',options={'xatol':1e-9,'fatol':1e-10,'maxiter':40000})
        if best is None or r.fun<best.fun: best=r
    return best.fun, best.x, len(th)
print('Quantisation-exact test: minimal worst-case violation (in d units) of f(n_prev) < d <= f(n_first)')
for dmin in (6,14):
    for m in KEYS:
        v,p,k=minimax(m,dmin)
        print(f'  d>={dmin:2d} ({k} thresholds) {m:22s} worst violation {v:.3f}  p={np.round(p,4)}')
# (2) forward validation: fit thresholds with n_first<=300, predict d=26,28 crossings and d=30 status at 384
print('\nForward test: fit on thresholds up to n<=300, predict stage-4 thresholds (n_x 26: (300,306], 28: (350,354], 30: >384 so far)')
for dmin in (6,14):
    th=[t for t in thresholds(300) if t[0]>=dmin]
    x=np.array([(a+b)/2 for d,a,b in th]); y=np.array([d for d,a,b in th],float)
    for m in KEYS:
        p,_=fit(m,x,y)
        c=[crossing(m,p,d) for d in (26,28,30)]
        ok26=300<c[0]<=306; ok28=350<c[1]<=354; ok30=c[2]>384
        print(f'  d>={dmin:2d} {m:22s} n*26={c[0]:6.1f}{"*" if ok26 else " "} n*28={c[1]:6.1f}{"*" if ok28 else " "} n*30={c[2]:6.1f}{"*" if ok30 else " "}  (* = inside observed interval)')
