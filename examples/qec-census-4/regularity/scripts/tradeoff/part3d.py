# Part 3d: extreme-value check (does the A1 residual grow with the number of groups at (n,k)?), torus shape effects,
# and extrapolation to published larger codes
from load import *
from scipy import optimize, stats
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
cnt=collections.Counter((e['n'],e['k']) for e in U)
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
f=lambda p,n,k:p[0]*n**p[1]-k
tr=N<=300; p=optimize.least_squares(lambda p:f(p,N[tr],K[tr])-Dd[tr],[2.3,0.44]).x
r=Dd-f(p,N,K); c=np.array([cnt[(int(a),int(b))] for a,b in zip(N,K)])
for lab,m in (('all',K>0),('k<=16',K<=16),('k=4',K==4)):
    s=stats.spearmanr(c[m],r[m]); print(f"{lab}: Spearman(resid, #groups at (n,k)) = {s.correlation:.2f} p={s.pvalue:.3f}; mean resid by #groups:",
          {int(g):round(float(np.mean(r[m&(c==g)])),2) for g in sorted(set(c[m]))})
# per-entry (group-level) residual vs torus shape: thin (min side <=3) vs fat
ent=np.array([(e['n'],e['k'],e['d'],min(e['g'][0],1) ,e['g'][0]) for e in U],float)
ra=ent[:,2]-f(p,ent[:,0],ent[:,1])
print("group-level residual by gcd(l,m) (all deduped entries, k<=16):",{int(g):(round(float(np.mean(ra[(ent[:,4]==g)&(ent[:,1]<=16)])),2),int(np.sum((ent[:,4]==g)&(ent[:,1]<=16)))) for g in sorted(set(ent[:,4]))})
for nm,n,k,dlo,dhi in (('[[360,12,24]]',360,12,24,24),('[[756,16,30..34]]',756,16,30,34)):
    print(f"A1 extrapolation {nm}: pred {f(p,n,k):.1f}  vs d in [{dlo},{dhi}]")
# compare per-k power law extrapolation for k=12/16 from part1
