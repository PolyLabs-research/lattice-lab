# Part 2: within single tori (deduplicated by group), best d vs k
from load import *
from scipy import stats
byg=collections.defaultdict(dict)
rep={}
for e in U:
    byg[e['g']][e['k']]=e['d']; rep.setdefault(e['g'],(e['l'],e['m'],e['n'],e['stage']))
rows=[]
print("torus  n   #k  k:d list | gamma(all k) +-se | gamma(k<=16,d>2) | gamma(kmin..kmin*4) | argmax kd^2/n (k, score) | score at kmin")
for g,kd in sorted(byg.items(), key=lambda t:rep[t[0]][2]):
    if len(kd)<5: continue
    ks=np.array(sorted(kd),float); ds=np.array([kd[k] for k in sorted(kd)],float)
    r=stats.linregress(np.log(ks),np.log(ds))
    m=(ds>2)&(ks<=16)
    r2=stats.linregress(np.log(ks[m]),np.log(ds[m])) if m.sum()>=3 else None
    kmin=ks.min(); m3=(ks<=4*kmin)
    r3=stats.linregress(np.log(ks[m3]),np.log(ds[m3])) if m3.sum()>=3 else None
    n=rep[g][2]; sc=ks*ds**2/n; i=int(np.argmax(sc))
    rows.append(dict(g=g,torus=rep[g][:2],n=n,nk=len(ks),gam=-r.slope,se=r.stderr,gam2=(-r2.slope if r2 else np.nan),gam3=(-r3.slope if r3 else np.nan),
                     kbest=int(ks[i]),sbest=sc[i],kmin=int(kmin),smin=sc[0],ks=ks,ds=ds))
    print(f"{rep[g][0]}x{rep[g][1]:<3d} {n:3d} {len(ks):2d} "+' '.join(f'{int(a)}:{int(b)}' for a,b in zip(ks,ds))+
          f" | {-r.slope:.2f}+-{r.stderr:.2f} | {(-r2.slope if r2 else float('nan')):.2f} | {(-r3.slope if r3 else float('nan')):.2f} | k={int(ks[i])} {sc[i]:.2f} | {sc[0]:.2f}")
G=np.array([r['gam'] for r in rows]); G2=np.array([r['gam2'] for r in rows]); G3=np.array([r['gam3'] for r in rows])
print(f"\n{len(rows)} rich groups (>=5 k values)")
for name,arr in (('all k',G),('k<=16 & d>2',G2),('kmin..4kmin',G3)):
    a=arr[~np.isnan(arr)]
    print(f"gamma [{name}]: n={len(a)} median={np.median(a):.2f} IQR=({np.percentile(a,25):.2f},{np.percentile(a,75):.2f}) min={a.min():.2f} max={a.max():.2f}")
# pooled within-torus slope (torus fixed effects), k<=16, d>2
X=[];Y=[];grp=[]
for i,r in enumerate(rows):
    m=(r['ds']>2)&(r['ks']<=16)
    for k,d in zip(r['ks'][m],r['ds'][m]): X.append(math.log(k));Y.append(math.log(d));grp.append(i)
X=np.array(X);Y=np.array(Y);grp=np.array(grp)
Xc=X.copy();Yc=Y.copy()
for i in set(grp): Xc[grp==i]-=X[grp==i].mean(); Yc[grp==i]-=Y[grp==i].mean()
sl=(Xc@Yc)/(Xc@Xc); print(f"pooled within-torus slope (fixed effects, k<=16, d>2): gamma={-sl:.3f}")
X=[];Y=[];grp=[]
for i,r in enumerate(rows):
    for k,d in zip(r['ks'],r['ds']): X.append(math.log(k));Y.append(math.log(d));grp.append(i)
X=np.array(X);Y=np.array(Y);grp=np.array(grp)
Xc=X.copy();Yc=Y.copy()
for i in set(grp): Xc[grp==i]-=X[grp==i].mean(); Yc[grp==i]-=Y[grp==i].mean()
sl=(Xc@Yc)/(Xc@Xc); print(f"pooled within-torus slope (fixed effects, all k): gamma={-sl:.3f}")
print("where the in-torus score kd^2/n peaks:",collections.Counter((r['kbest']//r['kmin']) for r in rows), "(as multiple of kmin)")
print("ratio best score / score at kmin: median",np.median([r['sbest']/r['smin'] for r in rows]))
# also all groups with >=3 k values
