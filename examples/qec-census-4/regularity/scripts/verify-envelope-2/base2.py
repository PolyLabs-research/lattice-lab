"""Independent re-derivation (verify-envelope-2). Read-only on the data."""
import json, math, numpy as np
from scipy.optimize import least_squares, minimize, brentq
DATA='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
D=json.load(open(DATA)); ENT=D['entries']
def envelope(nmax=10**9):
    E={}
    for e in ENT:
        if e['settled'] and e['n']<=nmax: E[e['n']]=max(E.get(e['n'],0),e['d'])
    ns=sorted(E); Es=[E[n] for n in ns]
    R=list(np.maximum.accumulate(Es))
    return np.array(ns,float), np.array(Es,float), np.array(R,float)
def thresholds(nmax=10**9):
    ns,Es,R=envelope(nmax)
    out=[]
    for d in range(2,60,2):
        i=np.where(Es>=d)[0]
        if len(i)==0: break
        i=i[0]
        out.append((d, ns[i-1] if i>0 else ns[i], ns[i]))
    return out  # (d, n_prev, n_first)
L=np.log
MODELS={
 'pow  a n^b':          (lambda n,p: p[0]*n**p[1],                     [0.8,0.6]),
 'sqrt(n ln n)':        (lambda n,p: p[0]*np.sqrt(n*L(n)),             [0.6]),
 'sqrt(n)(ln n)^p':     (lambda n,p: p[0]*np.sqrt(n)*L(n)**p[1],       [0.5,0.6]),
 'sqrt(n)(a+b sqrtln)': (lambda n,p: np.sqrt(n)*(p[0]+p[1]*np.sqrt(L(n))),[0,0.7]),
 'A sqrt(n)+B':         (lambda n,p: p[0]*np.sqrt(n)+p[1],             [1.7,-4]),
}
KEYS=list(MODELS)
def f(m,n,p): return MODELS[m][0](np.asarray(n,float),p)
def fit(m,x,y,w=None):
    fn,p0=MODELS[m]; w=np.ones_like(y) if w is None else w
    r=least_squares(lambda p:(fn(x,p)-y)*w,p0,max_nfev=20000)
    return r.x, float(np.sum((fn(x,r.x)-y)**2))
def aicc(rss,m,k):
    return m*math.log(rss/m)+2*k+2*k*(k+1)/max(m-k-1,1)
def first_diff(ma,pa,mb,pb,q,lo=12,hi=1e7):
    g=np.unique(np.concatenate([np.arange(lo,5000,1.0),np.geomspace(5000,hi,20000)]))
    dl=np.abs(f(ma,g,pa)-f(mb,g,pb))
    i=np.where(dl>=q)[0]
    return g[i] if len(i) else None
def crossing(m,p,d,lo=5,hi=1e8):
    try: return brentq(lambda n: f(m,n,p)-d, lo, hi)
    except ValueError: return float('nan')
