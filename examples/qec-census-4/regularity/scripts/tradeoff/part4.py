# Part 4: which k carry the envelope (in d and in score); S(k) by band; A1 robustness
from load import *
from scipy import optimize, stats
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
ns=sorted(set(n for k in F for n in F[k]))
strict_exceed=0; ties=collections.Counter(); carriers=collections.Counter(); notmin=[]
scar=[]
for n in ns:
    present=sorted(k for k in F if n in F[k]); kmin=present[0]
    env=max(F[k][n] for k in present); car=[k for k in present if F[k][n]==env]
    carriers[tuple(car)]+=1
    if kmin not in car: notmin.append((n,kmin,car))
    sc={k:k*F[k][n]**2/n for k in present}; ks=max(sc,key=sc.get)
    scar.append((n,ks,sc[ks],kmin,len(present)))
print("envelope carried by smallest k present at that n in", len(ns)-len(notmin),"of",len(ns),"n; exceptions:",notmin)
print("carrier sets:",dict(carriers))
print("n with kmin=k for each k:",{k:[n for n in ns if min(kk for kk in F if n in F[kk])==k] for k in (6,10,16,18)})
print("\nscore k d^2/n: carrier k at each n where >=3 k values present:")
print(' '.join(f"{n}:k{k}({s:.1f})" for n,k,s,km,np_ in scar if np_>=3))
# S(k) by n band
bands=[(0,100),(100,200),(200,300),(300,400)]
print("\nmax k d^2/n per k per band (dedup frontier):")
for k in sorted(F):
    row=[]
    for a,b in bands:
        v=[k*F[k][n]**2/n for n in F[k] if a<n<=b]
        row.append(f"{max(v):5.2f}" if v else "    .")
    print(f" k={k:2d}: "+' '.join(row))
print(" band maxima of score over all k:",[round(max(s for n,k,s,_,_ in scar if a<n<=b),2) for a,b in bands])
print(" score-optimal k by band (list):",[[k for n,k,s,_,np_ in scar if a<n<=b and np_>=3] for a,b in bands])
# A1 robustness: fit on n<=200, test 200<n<=300 and n>300; bootstrap over n on n<=300
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
f=lambda p,n,k:p[0]*n**p[1]-k
g=lambda p,n,k:p[0]*n**p[1]*k**-0.5
def ev(m,pr):
    e=Dd[m]-pr[m]; pe=2*np.maximum(1,np.round(pr[m]/2)); return f"N={m.sum()} rms={np.sqrt(np.mean(e**2)):.2f} bias={np.mean(e):+.2f} within2={np.mean(np.abs(pe-Dd[m])<=2):.2f}"
for nm,fun,p0 in (('A1 c n^b - k',f,[2,0.45]),('P1 c n^b/sqrt(k)',g,[1,0.6])):
    tr=N<=200; p=optimize.least_squares(lambda p:fun(p,N[tr],K[tr])-Dd[tr],p0).x; pr=fun(p,N,K)
    print(f"\n{nm} fit n<=200: c={p[0]:.3f} b={p[1]:.3f} | test 200-300: {ev((N>200)&(N<=300),pr)} | test >300: {ev(N>300,pr)}")
rng=np.random.default_rng(1); un=np.unique(N[N<=300]); B=[]
for i in range(2000):
    s=rng.choice(un,len(un)); idx=np.concatenate([np.where(N==x)[0] for x in s])
    B.append(optimize.least_squares(lambda p:f(p,N[idx],K[idx])-Dd[idx],[2.3,0.44]).x)
B=np.array(B); print(f"A1 bootstrap (resample n values, n<=300): c 95% [{np.percentile(B[:,0],2.5):.2f},{np.percentile(B[:,0],97.5):.2f}] b 95% [{np.percentile(B[:,1],2.5):.3f},{np.percentile(B[:,1],97.5):.3f}]")
# A1 with free slope on k, bootstrap slope
B2=[]
for i in range(1000):
    s=rng.choice(un,len(un)); idx=np.concatenate([np.where(N==x)[0] for x in s])
    B2.append(optimize.least_squares(lambda p:p[0]*N[idx]**p[1]-p[2]*K[idx]-Dd[idx],[2.0,0.45,0.9]).x)
B2=np.array(B2); print(f"A2 slope on k bootstrap 95% [{np.percentile(B2[:,2],2.5):.2f},{np.percentile(B2[:,2],97.5):.2f}] median {np.median(B2[:,2]):.2f}")
# Effective local exponent of D(n)=d+k on the frontier
y=Dd+K; r=stats.linregress(np.log(N[K<=16]),np.log(y[K<=16])); print(f"log(d+k) vs log n (frontier, k<=16): slope {r.slope:.3f}+-{r.stderr:.3f}")
for a,b in [(0,150),(150,300),(300,400)]:
    m=(N>a)&(N<=b)&(K<=16); r=stats.linregress(np.log(N[m]),np.log(y[m])); print(f"   band {a}-{b}: slope {r.slope:.3f}+-{r.stderr:.3f}")
