# Part 3c: where A1 (d = c n^b - k, fit n<=300) fails; full scatter; published codes
from load import *
from scipy import optimize
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
who=collections.defaultdict(list)
for e in U: who[(e['n'],e['k'])].append(e)
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
f=lambda p,n,k:p[0]*n**p[1]-k
tr=N<=300; p=optimize.least_squares(lambda p:f(p,N[tr],K[tr])-Dd[tr],[2.3,0.44]).x
print("A1 params c=%.4f b=%.4f"%tuple(p))
pr=f(p,N,K); r=Dd-pr
ix=np.argsort(-np.abs(r))
print("largest |residual| frontier points (n,k,d,pred,resid, achieving tori):")
for i in ix[:22]:
    n,k,d=int(N[i]),int(K[i]),int(Dd[i])
    tor=[f"{e['l']}x{e['m']}" for e in who[(n,k)] if e['d']==d]
    print(f"  n={n:3d} k={k:2d} d={d:2d} pred={pr[i]:5.1f} resid={r[i]:+5.1f} {'TEST' if n>300 else 'train'} {tor}")
# residual summary by k range, train/test
for lab,m in (('k=4',K==4),('k=6..16',(K>=6)&(K<=16)),('k>=18',K>=18)):
    for s,mm in (('train',m&tr),('test',m&~tr)):
        if mm.sum(): print(f" {lab:8s} {s:5s} N={mm.sum():3d} mean resid {np.mean(r[mm]):+.2f} rms {np.sqrt(np.mean(r[mm]**2)):.2f} |r|<=2 {np.mean(np.abs(2*np.maximum(1,np.round(pr[mm]/2))-Dd[mm])<=2):.2f}")
# both sides even tori (terms vary): residuals
print("frontier points achieved only on tori with both l,m even:")
for i in range(len(N)):
    n,k,d=int(N[i]),int(K[i]),int(Dd[i]); es=[e for e in who[(n,k)] if e['d']==d]
    if all(e['l']%2==0 and e['m']%2==0 for e in es): print(f"  n={n} k={k} d={d} pred={pr[i]:.1f} resid={r[i]:+.1f} {[(e['l'],e['m']) for e in es]}")
# full scatter (all non-dedup entries, as plotted)
allE=np.array([(e['n'],e['k'],e['d']) for e in E],float)
pa=f(p,allE[:,0],allE[:,1]); ra=allE[:,2]-pa
print(f"\nfull scatter (all {len(E)} entries incl. duplicates): fraction with d <= pred+2: {np.mean(ra<=2):.3f}; above pred+2: {np.sum(ra>2)}; within +-2: {np.mean(np.abs(ra)<=2):.2f}; median resid {np.median(ra):+.2f}")
print(" entries above pred+2:",[(int(a),int(b),int(c),round(float(d),1)) for (a,b,c),d in zip(allE,pa) if c-d>2])
print("\npublished codes vs A1:")
for q in D['published']:
    print(f"  {q['name']:40s} n={q['n']} k={q['k']} d={q['d']} A1 pred={f(p,q['n'],q['k']):.1f} resid={q['d']-f(p,q['n'],q['k']):+.1f}; census frontier at (n,k): {F.get(q['k'],{}).get(q['n'])}")
print("tori present at n=360:",sorted({(e['l'],e['m']) for e in E if e['n']==360}))
