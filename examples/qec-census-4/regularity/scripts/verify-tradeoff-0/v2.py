import json, math, collections, pickle
import numpy as np
from scipy import optimize
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
E=json.load(open(SP+'/census-data.json'))['entries']
pts,F=pickle.load(open(SP+'/regularity/verify-tradeoff-0/frontier.pkl','rb'))
N,K,D=pts.T
def even(x): return 2*np.maximum(1,np.round(x/2))
def st(pred,d):
    e=d-pred; pe=even(pred)
    return f"N={len(d)} rms={np.sqrt(np.mean(e**2)):.2f} bias={np.mean(e):+.2f} w2={np.mean(np.abs(pe-d)<=2):.2f} ex={np.mean(pe==d):.2f}"
def fit(f,p0,tr):
    return optimize.least_squares(lambda p:f(p,N[tr],K[tr])-D[tr],p0,max_nfev=20000).x
A1=(lambda p,n,k:p[0]*n**p[1]-k,[0.5,0.65]); A0=(lambda p,n,k:p[0]*np.sqrt(n)-k,[1.5])
P1=(lambda p,n,k:p[0]*n**p[1]*k**-0.5,[1,0.6]); P2=(lambda p,n,k:p[0]*n**p[1]*k**-p[2],[1,0.6,0.5])
A2=(lambda p,n,k:p[0]*n**p[1]-p[2]*k,[0.5,0.65,1])
print('=== naive baselines on the claimed split (train n<=300, test n>300)')
tr=N<=300; te=N>300
# B1 persistence: last training frontier value with same k
# B2 per-k scaled persistence: running max over training n of d * sqrt(n/n')
# B3 per-k own power law fit c_k n^b_k (log space) on training
# B4 A1-shape but fitted on k=4 only, then shifted -(k-4)
preds={}
for name in ('persist','persist_sqrt','perk_maxsqrt','perk_power'):
    pr=np.full(len(N),np.nan)
    for i in np.where(te)[0]:
        m=tr&(K==K[i])
        if not m.any(): continue
        ns,ds=N[m],D[m]
        j=np.argmax(ns)
        if name=='persist': pr[i]=ds[j]
        elif name=='persist_sqrt': pr[i]=ds[j]*math.sqrt(N[i]/ns[j])
        elif name=='perk_maxsqrt': pr[i]=np.max(ds/np.sqrt(ns))*math.sqrt(N[i])  # envelope of d/sqrt(n) per k
        elif name=='perk_power':
            if m.sum()>=3:
                b,a=np.polyfit(np.log(ns),np.log(ds),1); pr[i]=math.exp(a)*N[i]**b
            else: pr[i]=ds[j]*math.sqrt(N[i]/ns[j])
    ok=te&~np.isnan(pr)
    preds[name]=pr
    print(f"  {name:14s} covers {ok.sum()}/{te.sum()}: {st(pr[ok],D[ok])}")
p=fit(A1[0],A1[1],tr); a1=A1[0](p,N,K)
ok=te&~np.isnan(preds['persist'])
print(f"  A1 on same covered points: {st(a1[ok],D[ok])}")
m4=tr&(K==4); b,a=np.polyfit(np.log(N[m4]),np.log(D[m4]),1)
shift=np.exp(a)*N**b-(K-4)
print(f"  k=4 power law (c={np.exp(a):.3f},b={b:.3f}) shifted by -(k-4): {st(shift[te],D[te])}")
print(f"  k=4 power law, no shift (ignore k)             : {st((np.exp(a)*N**b)[te],D[te])}")

print('\n=== alternative splits (fit on n<=T, test on T<n<=300 or all n>T)')
for T,hi in ((200,300),(250,300),(200,400),(250,400),(300,400)):
    tr=N<=T; te=(N>T)&(N<=hi)
    out=[]
    for nm,(f,p0) in (('A1',A1),('A0',A0),('A2',A2),('P1',P1),('P2',P2)):
        p=fit(f,p0,tr); out.append(f"{nm}[{', '.join(f'{x:.3g}' for x in p)}] {st(f(p,N,K)[te],D[te])}")
    print(f" train n<={T}, test {T}<n<={hi}:"); [print('   ',o) for o in out]
print('\n=== how robust is the exponent b in A1? profile of train SSE over b (n<=300)')
tr=N<=300
for b in (0.40,0.42,0.4426,0.46,0.48,0.5,0.55):
    X=N[tr]**b; c=np.sum(X*(D[tr]+K[tr]))/np.sum(X*X); r=D[tr]-(c*X-K[tr])
    pr=c*N[N>300]**b-K[N>300]
    print(f"  b={b:.4f} c={c:.3f} train rms={np.sqrt(np.mean(r**2)):.3f} | test {st(pr,D[N>300])}")
# bootstrap CI for b
rng=np.random.default_rng(1); idx=np.where(tr)[0]; bs=[]
for _ in range(500):
    s=rng.choice(idx,len(idx)); 
    q=optimize.least_squares(lambda p:p[0]*N[s]**p[1]-K[s]-D[s],[2.3,0.44]).x; bs.append(q[1])
print('  bootstrap b 2.5/50/97.5%:',np.percentile(bs,[2.5,50,97.5]).round(3))
