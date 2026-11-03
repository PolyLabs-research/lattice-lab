import json, math, collections, numpy as np
from scipy import stats, optimize
P='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
E=json.load(open(P))['entries']
def inv(l,m):
    g=math.gcd(l,m); return (g,l*m//g)
best={}
for e in E:
    key=(inv(e['l'],e['m']),e['k'])
    if key not in best or e['d']>best[key]['d']: best[key]=e
fr=collections.defaultdict(dict); N={}
for (g,k),e in best.items(): fr[g][k]=e['d']; N[g]=e['n']
G=[(N[g],np.array(sorted(fr[g]),float),np.array([fr[g][k] for k in sorted(fr[g])],float)) for g in fr if len(fr[g])>=4]
G.sort(key=lambda x:x[0])
ev2=lambda x: 2*np.round(x/2)
# 1) synthetic nulls for the CV statistic: what CV(d+k), CV(kd^2) would each "truth" give on the same k-grids?
def cvs(ks,ds): return np.std(ds+ks)/np.mean(ds+ks), np.std(ks*ds**2)/np.mean(ks*ds**2), np.std(ks*ds)/np.mean(ks*ds)
out=collections.defaultdict(list)
for n,ks,ds in G:
    S2=np.mean(ks*ds**2); C=np.mean(ds+ks)
    out['obs'].append(cvs(ks,ds))
    out['truth kd^2=S (even-rounded)'].append(cvs(ks,np.maximum(2,ev2(np.sqrt(S2/ks)))))
    out['truth d+k=C (even-rounded)'].append(cvs(ks,np.maximum(2,ev2(C-ks))))
    out['truth d=C const'].append(cvs(ks,np.full_like(ks,np.mean(ds))))
print('median CV of (d+k, kd^2, kd) on the real k-grids under synthetic truths:')
for k,v in out.items(): v=np.array(v); print(f'  {k:32s} {np.median(v[:,0]):.3f} {np.median(v[:,1]):.3f} {np.median(v[:,2]):.3f}')
# 2) one-shared-shape-parameter families: d = C - c k (C per group), d = D(1-k/K), d = D k^-g, d = D sqrt(1-k/K)
def per_group_rms(model, theta):
    r=[]
    for n,ks,ds in G:
        f=model(theta,ks)   # shape, scale fitted per group by LSQ
        if model is add: C=np.mean(ds+theta*ks); p=C-theta*ks
        else: s=np.dot(f,ds)/np.dot(f,f); p=s*f
        r.append(np.sqrt(np.mean((ds-p)**2)))
    return np.array(r)
add=lambda c,k: None
fams={'d=C-c*k':(add,np.linspace(0.3,2,35)),
      'd=D(1-k/K)':(lambda K,k:1-k/K,np.linspace(16,80,65)),
      'd=D k^-g':(lambda g,k:k**(-g),np.linspace(0.1,1.5,57)),
      'd=D sqrt(1-k/K)':(lambda K,k:np.sqrt(np.clip(1-k/K,0,None)),np.linspace(24,120,97)),
      'd=D exp(-k/K)':(lambda K,k:np.exp(-k/K),np.linspace(5,80,76))}
print('\nshared-shape families (1 per-group scale + 1 global shape param), rms_d over 30 groups:')
for name,(f,grid) in fams.items():
    vals=[np.mean(per_group_rms(f,t)**2) for t in grid]; i=int(np.argmin(vals)); th=grid[i]
    r=per_group_rms(f,th)
    print(f'  {name:18s} best shape={th:.2f}  pooled rms={np.sqrt(vals[i]):.2f} median rms={np.median(r):.2f}')
    if name=='d=C-c*k':
        for c in (0.5,0.75,1.0,1.25,1.5): print(f'      c={c}: pooled rms={np.sqrt(np.mean(per_group_rms(f,c)**2)):.2f}  median CV(d+c k)={np.median([np.std(ds+c*ks)/np.mean(ds+c*ks) for n,ks,ds in G]):.3f}')
# 3) slope by n band
print('\nper-group OLS slope a by n band:')
A=np.array([-stats.linregress(ks,ds).slope for n,ks,ds in G]); Ns=np.array([g[0] for g in G]); CVs=np.array([np.std(ds+ks)/np.mean(ds+ks) for n,ks,ds in G])
for lo,hi in ((0,150),(150,300),(300,400)):
    m=(Ns>lo)&(Ns<=hi); print(f'  n in ({lo},{hi}]: groups={m.sum()} median a={np.median(A[m]):.2f} range {A[m].min():.2f}-{A[m].max():.2f}  median CV(d+k)={np.median(CVs[m]):.3f}  mean (d+k)(kmax)-(d+k)(kmin) = {np.mean([ (ds+ks)[-1]-(ds+ks)[0] for (n,ks,ds),mm in zip(G,m) if mm]):+.2f}')
# 4) a vs n: is it just that groups at larger n include a larger-k "cliff" point? slope on k<=12 only
A12=[];N12=[]
for n,ks,ds in G:
    m=ks<=12
    if m.sum()>=3: A12.append(-stats.linregress(ks[m],ds[m]).slope); N12.append(n)
print(f'\nslope on k<=12 only: groups={len(A12)} median a={np.median(A12):.2f} Spearman(n,a)={stats.spearmanr(N12,A12).correlation:.2f} p={stats.spearmanr(N12,A12).pvalue:.3f}')
# 5) concavity: second differences / curvature sign from quadratic fit
curv=[np.polyfit(ks,ds,2)[0] for n,ks,ds in G]
print(f'quadratic coefficient sign: concave(<0) {sum(c<0 for c in curv)}/{len(curv)}, median {np.median(curv):.3f}')
# 6) d+k at k_min vs k_max
diff=np.array([(ds+ks)[-1]-(ds+ks)[0] for n,ks,ds in G]); print('(d+k)(k_max)-(d+k)(k_min) distribution:',sorted(collections.Counter(diff.astype(int)).items()))
