from load import *
import numpy as np, math
from scipy import stats
from scipy.special import gammaln
t=load()
G={}
for (l,m),v in sorted(t.items()):
    if not v['rows']: continue
    g=grp(l,m)
    if g in G: continue
    G[g]=dict(n=v['n'], d=np.array([r['d'] for r in v['rows']]), tor=(l,m))
sel=sorted([(g,v) for g,v in G.items() if len(v['d'])>=20], key=lambda x:x[1]['n'])
n=np.array([v['n'] for g,v in sel],float); N=np.array([len(v['d']) for g,v in sel],float)
sk=np.array([stats.skew(v['d']) for g,v in sel])
print("skewness of d per group: mean %.2f, #negative %d/%d"%(sk.mean(),(sk<0).sum(),len(sk)))
# Gaussian E[max] exact vs sqrt(2lnN)
x=np.linspace(-12,12,40001)
def eg(M): F=stats.norm.cdf(x); f=stats.norm.pdf(x); return np.trapezoid(x*M*F**(M-1)*f,x)
EG=np.array([eg(int(M)) for M in N]); print("mean exact Gaussian E[max]=%.3f ; mean sqrt(2 ln N)=%.3f"%(EG.mean(),np.sqrt(2*np.log(N)).mean()))
z0=np.array([(v['d'].max()-v['d'].mean())/v['d'].std() for g,v in sel]); print("mean z (ddof=0)=%.3f"%z0.mean())
# Monte Carlo: a left-skewed discrete distribution null -- resample within group (bootstrap) z of max of N draws
# Robust-frontier: band maxima of d/sqrt(n) using value held by >=r classes
def topval(d,r):
    vals=sorted(set(d),reverse=True)
    for v in vals:
        if (d>=v).sum()>=r: return v
allg=sorted(G.items(), key=lambda x:x[1]['n'])
for r in (1,3,5,10):
    out=[]
    for lo in (0,50,100,150):
        best=max(((topval(v['d'],r)/math.sqrt(v['n']),v['tor'],v['n'],topval(v['d'],r)) for g,v in allg if lo<v['n']<=lo+50 and len(v["d"])>=r), default=None)
        out.append((round(best[0],3),best[1],best[3]))
    print(f"band max of d_r/sqrt(n), d_r = largest d held by >={r} classes:",out)
# percentile version: 99th percentile
for q in (99,95):
    out=[]
    for lo in (0,50,100,150):
        best=max(((np.percentile(v['d'],q,method='higher')/math.sqrt(v['n']),v['tor']) for g,v in allg if lo<v['n']<=lo+50))
        out.append((round(best[0],3),best[1]))
    print(f"band max of p{q}/sqrt(n):",out)
# gap regressions
X=np.column_stack([np.ones_like(n),np.log(n),np.log(N)])
import numpy.linalg as la
for lab,y in [('(max-median)/2',np.array([(v['d'].max()-np.median(v['d']))/2 for g,v in sel])),('(max-p90)/2',np.array([(v['d'].max()-np.percentile(v['d'],90))/2 for g,v in sel])),('log(max/median)',np.array([math.log(v['d'].max()/np.median(v['d'])) for g,v in sel]))]:
    beta=la.lstsq(X,y,rcond=None)[0]; res=y-X@beta; s2=res@res/(len(y)-3); se=np.sqrt(np.diag(s2*la.inv(X.T@X)))
    print(f"  {lab:16s} ~ {beta[1]:.3f}(t={beta[1]/se[1]:.2f}) log n + {beta[2]:.3f}(t={beta[2]/se[2]:.2f}) log N")
# paired bootstrap over groups: slope(max) - slope(median), slope(max)-slope(E[max of 20])
def lC(a,b): return gammaln(a+1)-gammaln(b+1)-gammaln(a-b+1)
def emax_sub(d,N0):
    d=np.sort(d); Nn=len(d); E=0; prev=0
    for v in np.unique(d):
        c=(d<=v).sum(); P=math.exp(lC(c,N0)-lC(Nn,N0)) if c>=N0 else 0.0; E+=v*(P-prev); prev=P
    return E
mx=np.array([v['d'].max() for g,v in sel],float); med=np.array([np.median(v['d']) for g,v in sel]); mean=np.array([v['d'].mean() for g,v in sel]); e20=np.array([emax_sub(v['d'],20) for g,v in sel])
rng=np.random.default_rng(1); B=5000; ln=np.log(n)
def sl(idx,y): return np.polyfit(ln[idx],np.log(y[idx]),1)[0]
for lab,y2 in [('median',med),('mean',mean),('E[max of 20]',e20)]:
    diffs=[]
    for _ in range(B):
        idx=rng.integers(0,len(n),len(n)); diffs.append(sl(idx,mx)-sl(idx,y2))
    diffs=np.array(diffs); print(f"slope(max)-slope({lab}): {sl(np.arange(len(n)),mx)-sl(np.arange(len(n)),y2):.3f}  95% CI [{np.percentile(diffs,2.5):.3f},{np.percentile(diffs,97.5):.3f}]")
# fraction of excess over 0.5 explained
print("excess slope over 0.5: max %.3f, E[max20] %.3f, mean %.3f, median %.3f"%(sl(np.arange(len(n)),mx)-.5,sl(np.arange(len(n)),e20)-.5,sl(np.arange(len(n)),mean)-.5,sl(np.arange(len(n)),med)-.5))
