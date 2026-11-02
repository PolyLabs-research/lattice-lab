# Part 2c: other 2-param within-torus shapes, and does the slope a depend on n?
from load import *
from scipy import stats, optimize
byg=collections.defaultdict(dict); rep={}
for e in U:
    byg[e['g']][e['k']]=e['d']; rep.setdefault(e['g'],(e['l'],e['m'],e['n']))
shapes={'lin D-a k':lambda p,k:p[0]-p[1]*k,'pow C k^-g':lambda p,k:p[0]*k**(-p[1]),
        'log C-a ln k':lambda p,k:p[0]-p[1]*np.log(k),'exp C e^(-k/k0)':lambda p,k:p[0]*np.exp(-k/p[1]),
        'sqrt-Singleton D sqrt(1-k/K)':lambda p,k:p[0]*np.sqrt(np.clip(1-k/p[1],1e-9,None))}
p0={'lin D-a k':[20,1],'pow C k^-g':[30,0.5],'log C-a ln k':[30,5],'exp C e^(-k/k0)':[30,20],'sqrt-Singleton D sqrt(1-k/K)':[30,40]}
rms={s:[] for s in shapes}; A=[];Ns=[];Ds=[];Ks=[]
for g,kd in byg.items():
    if len(kd)<4: continue
    ks=np.array(sorted(kd),float); ds=np.array([kd[int(k)] for k in ks],float)
    for s,f in shapes.items():
        sol=optimize.least_squares(lambda p:f(p,ks)-ds,p0[s]); rms[s].append(np.sqrt(np.mean(sol.fun**2)))
    r=stats.linregress(ks,ds); A.append(-r.slope); Ns.append(rep[g][2]); Ds.append(r.intercept); Ks.append(r.intercept/(-r.slope))
for s in shapes: print(f"{s:32s} median rms_d={np.median(rms[s]):.2f} mean={np.mean(rms[s]):.2f}")
wins=collections.Counter(min(shapes,key=lambda s:rms[s][i]) for i in range(len(A)))
print('best shape per torus:',dict(wins))
A=np.array(A);Ns=np.array(Ns);Ds=np.array(Ds);Ks=np.array(Ks)
r=stats.spearmanr(Ns,A); print(f"slope a vs n: Spearman rho={r.correlation:.2f} p={r.pvalue:.3f}; a~n^beta: beta={stats.linregress(np.log(Ns),np.log(A)).slope:.2f}")
print(f"K=D/a (zero-crossing k): median {np.median(Ks):.1f}, IQR {np.percentile(Ks,25):.1f}-{np.percentile(Ks,75):.1f}; Spearman K vs n {stats.spearmanr(Ns,Ks).correlation:.2f}")
print(f"D (intercept) ~ n^b: b={stats.linregress(np.log(Ns),np.log(Ds)).slope:.3f}")
