# Part 5 (stage 3a per-class data, n<=200, all classes exact): is the d-k trade-off structural or an extreme-value artefact?
import json, glob, math, collections, os
import numpy as np
from scipy import stats
DIR='/home/user/lattice-lab/examples/qec-census-3/data'
rows=[]; seen=set(); status=collections.Counter()
for f in sorted(glob.glob(DIR+'/*.jsonl')):
    L=[json.loads(x) for x in open(f)]
    h=L[0]; l,m,n=h['l'],h['m'],h['n']; g=(math.gcd(l,m),l*m//math.gcd(l,m))
    if g in seen: continue
    seen.add(g)
    for r in L[1:]:
        status[r.get('status')]+=1
        if r.get('connected') and r['k']>0: rows.append((l,m,n,g,r['k'],r['d'],r.get('size',1)))
print('status counts',dict(status),'groups',len(seen),'connected classes',len(rows))
T=collections.defaultdict(lambda: collections.defaultdict(list))
for l,m,n,g,k,d,s in rows: T[(l,m,n)][k].append(d)
# compare with census-data entries (frontier) as a consistency check
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
E=json.load(open(SP+'/census-data.json'))['entries']
fr={(e['l'],e['m'],e['k']):e['d'] for e in E if e['stage']=='3a'}
mism=[(t,k,max(v),fr.get((t[0],t[1],k))) for t in T for k,v in T[t].items() if (t[0],t[1],k) in fr and max(v)!=fr[(t[0],t[1],k)]]
print('frontier check vs census-data (3a):',len(mism),'mismatches', mism[:5])
# within-torus regressions with torus fixed effects: max d, median d, mean d on k, with and without log(#classes)
X=[];Ymax=[];Ymed=[];Ymean=[];LC=[];G=[];Ytop3=[]
for t,kd in T.items():
    if len(kd)<3: continue
    for k,v in kd.items():
        v=sorted(v,reverse=True)
        X.append(k);Ymax.append(v[0]);Ymed.append(np.median(v));Ymean.append(np.mean(v));LC.append(math.log(len(v)));G.append(t)
        Ytop3.append(np.mean(v[:3]) if len(v)>=3 else np.nan)
X=np.array(X,float);LC=np.array(LC);G=np.array([hash(g) for g in G])
def fe(y,cols):
    y=np.array(y,float); m=~np.isnan(y)
    Z=np.column_stack(cols)[m]; yy=y[m]; gg=G[m]
    for u in set(gg):
        s=gg==u; Z[s]-=Z[s].mean(0); yy[s]-=yy[s].mean()
    beta,res,_,_=np.linalg.lstsq(Z,yy,rcond=None)
    r=yy-Z@beta; dof=len(yy)-Z.shape[1]-len(set(gg)); se=np.sqrt(np.diag(np.linalg.inv(Z.T@Z))*(r@r)/dof)
    return beta,se,m.sum()
print(f"tori with >=3 k values: {len(set(G))}; (torus,k) cells: {len(X)}")
for nm,y in (('max d',Ymax),('mean of top-3 d',Ytop3),('median d',Ymed),('mean d',Ymean)):
    b,se,N=fe(y,[X]); b2,se2,_=fe(y,[X,LC])
    print(f"  {nm:16s}: slope on k = {b[0]:+.3f}+-{se[0]:.3f}  | with log(#classes): slope on k {b2[0]:+.3f}+-{se2[0]:.3f}, on log#classes {b2[1]:+.3f}+-{se2[1]:.3f}  (N={N})")
# k<=16 only
m16=X<=16
print(" restricted to k<=16:")
for nm,y in (('max d',Ymax),('median d',Ymed)):
    y=np.array(y,float); y[~m16]=np.nan
    b,se,N=fe(y,[X]); b2,se2,_=fe(y,[X,LC])
    print(f"  {nm:16s}: slope on k = {b[0]:+.3f}+-{se[0]:.3f}  | with log(#classes): k {b2[0]:+.3f}+-{se2[0]:.3f}, log#classes {b2[1]:+.3f}+-{se2[1]:.3f}  (N={N})")
# class counts by k
cc=collections.defaultdict(list)
for t,kd in T.items():
    for k,v in kd.items(): cc[k].append(len(v))
print(" median #connected classes per (torus,k):",{k:int(np.median(v)) for k,v in sorted(cc.items())})
# example tori
for t in [(3,21,126),(2,42,168),(3,35,105*2),(7,9,126),(6,12,144),(3,30,180)]:
    if t in T: print(' ',t,' '.join(f"k{k}:max{max(v)} med{np.median(v):.0f} n={len(v)}" for k,v in sorted(T[t].items())))
