from load import *
import numpy as np, json
from scipy import stats
from scipy.special import gammaln
t=load()
G={}
for (l,m),v in sorted(t.items()):
    if not v['rows']: continue
    g=grp(l,m)
    if g in G: continue
    G[g]=dict(n=v['n'], d=np.array([r['d'] for r in v['rows']]))
sel=sorted([(g,v) for g,v in G.items() if len(v['d'])>=20], key=lambda x:x[1]['n'])
n=np.array([v['n'] for g,v in sel],float); N=np.array([len(v['d']) for g,v in sel],float)
def lC(a,b): return gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1) if a>=b else -np.inf
def emax_sub(d,N0):
    d=np.sort(d); N=len(d); vals=np.unique(d); E=0.0; prev=0.0
    for v in vals:
        cnt=(d<=v).sum(); P=np.exp(lC(cnt,N0)-lC(N,N0)) if cnt>=N0 else 0.0  # P(max<=v)
        E+=v*(P-prev); prev=P
    return E
def fit(x,y,lab):
    r=stats.linregress(np.log(x),np.log(y)); print(f"  {lab:28s} slope={r.slope:.3f} +-{1.96*r.stderr:.3f}")
    return r.slope
print("groups",len(sel))
fit(n,N,'N (classes) vs n')
mx=np.array([v['d'].max() for g,v in sel],float); med=np.array([np.median(v['d']) for g,v in sel])
mean=np.array([v['d'].mean() for g,v in sel])
for N0 in (20,):
    e=np.array([emax_sub(v['d'],N0) for g,v in sel])
    print(f"fixed-N0={N0} expected max:")
    fit(n,e,f'E[max of {N0}] vs n'); fit(n,mx,'actual max vs n')
    print("   mean (actual max - E[max of 20]) =", np.mean(mx-e).round(3), " corr with logN:", stats.pearsonr(np.log(N),mx-e))
# multiple regression: log stat = a + b log n + c log N
X=np.column_stack([np.ones_like(n),np.log(n),np.log(N)])
import numpy.linalg as la
for lab,y in [('max',mx),('median',med),('mean',mean),('p90',np.array([np.percentile(v['d'],90) for g,v in sel]))]:
    Y=np.log(y); beta,res,rk,sv=la.lstsq(X,Y,rcond=None)
    resid=Y-X@beta; s2=resid@resid/(len(Y)-3); cov=s2*la.inv(X.T@X); se=np.sqrt(np.diag(cov))
    print(f"  log {lab:6s} = {beta[0]:.2f} + {beta[1]:.3f}(+-{1.96*se[1]:.3f}) log n + {beta[2]:.3f}(+-{1.96*se[2]:.3f}) log N   t_N={beta[2]/se[2]:.2f}")
# subsets n>=100
s=n>=100
print("n>=100 groups:",s.sum())
for lab,y in [('mean',mean),('median',med),('p90',np.array([np.percentile(v['d'],90) for g,v in sel])),('max',mx)]:
    fit(n[s],y[s],lab+' n>=100')
e20=np.array([emax_sub(v['d'],20) for g,v in sel]); fit(n[s],e20[s],'E[max of 20] n>=100')
# same-n pairs
print("same-n comparisons (n: [(group,N,median,max)])")
from collections import defaultdict
byn=defaultdict(list)
for g,v in sel: byn[v['n']].append((g,len(v['d']),float(np.median(v['d'])),int(v['d'].max()),round(float(v['d'].mean()),2)))
for k_,L in sorted(byn.items()):
    if len(L)>1: print(k_,sorted(L,key=lambda x:x[1]))
# isolated maxima
iso=[(g,v['n'],len(v['d']),int((v['d']==v['d'].max()).sum())) for g,v in sel if (v['d']==v['d'].max()).sum()<=2]
print("groups whose max is held by <=2 classes:",len(iso),iso)
fr=np.array([np.mean(v['d']>=v['d'].max()-2) for g,v in sel])
print("corr(frac within one step of max, log N):",stats.pearsonr(np.log(N),fr), stats.spearmanr(N,fr))
big=N>=500
print("frac within one step, groups N>=500:",np.round(fr[big],2), "median",np.median(fr[big]))
