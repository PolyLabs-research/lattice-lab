# Part 2b: within-torus shape of d(k): linear (d = D - a k) vs power (d = C k^-g), and invariants d+k, k d^2, k d
from load import *
from scipy import stats
byg=collections.defaultdict(dict); rep={}
for e in U:
    byg[e['g']][e['k']]=e['d']; rep.setdefault(e['g'],(e['l'],e['m'],e['n']))
def fitlin(ks,ds):
    r=stats.linregress(ks,ds); p=r.intercept+r.slope*ks; return r.intercept,-r.slope,np.sqrt(np.mean((ds-p)**2))
def fitpow(ks,ds):
    r=stats.linregress(np.log(ks),np.log(ds)); p=np.exp(r.intercept+r.slope*np.log(ks)); return math.exp(r.intercept),-r.slope,np.sqrt(np.mean((ds-p)**2))
for minK in (4,3):
  for kcap in (99,20):
    rows=[]
    for g,kd in byg.items():
        ks=np.array(sorted(x for x in kd if x<=kcap),float)
        if len(ks)<minK: continue
        ds=np.array([kd[int(k)] for k in ks],float)
        D,a,rl=fitlin(ks,ds); C,gm,rp=fitpow(ks,ds)
        cv=lambda v: np.std(v)/np.mean(v)
        rows.append(dict(n=rep[g][2],t=rep[g][:2],nk=len(ks),D=D,a=a,rl=rl,rp=rp,gm=gm,
            cv_sum=cv(ds+ks),cv_kd2=cv(ks*ds**2),cv_kd=cv(ks*ds),cv_d=cv(ds),
            spread_sum=(ds+ks).max()-(ds+ks).min()))
    R=lambda key: np.array([r[key] for r in rows])
    print(f"\n== groups with >= {minK} k values (k <= {kcap}): {len(rows)} groups")
    print(f" linear d = D - a k : median a = {np.median(R('a')):.2f} (IQR {np.percentile(R('a'),25):.2f}-{np.percentile(R('a'),75):.2f}); median rms_d = {np.median(R('rl')):.2f}")
    print(f" power  d = C k^-g  : median g = {np.median(R('gm')):.2f} (IQR {np.percentile(R('gm'),25):.2f}-{np.percentile(R('gm'),75):.2f}); median rms_d = {np.median(R('rp')):.2f}")
    print(f" linear beats power in {np.sum(R('rl')<R('rp'))}/{len(rows)} groups")
    print(f" median coefficient of variation across k:  d+k {np.median(R('cv_sum')):.3f} | k d^2 {np.median(R('cv_kd2')):.3f} | k d {np.median(R('cv_kd')):.3f} | d {np.median(R('cv_d')):.3f}")
    print(f" spread max-min of (d+k) within torus: median {np.median(R('spread_sum')):.1f}, distribution {sorted(collections.Counter(R('spread_sum').astype(int)).items())}")
    if minK==4 and kcap==99:
        print(" per group (n, torus, #k, D, a, rms lin, rms pow, d+k values):")
        for r in sorted(rows,key=lambda r:r['n']):
            g=[gg for gg in byg if rep[gg][:2]==r['t']][0]
            kd=byg[g]
            print(f"  n={r['n']:3d} {r['t'][0]}x{r['t'][1]:<3d} #k={r['nk']:2d} D={r['D']:.1f} a={r['a']:.2f} rms_lin={r['rl']:.2f} rms_pow={r['rp']:.2f}  d+k: "+' '.join(f'{k}:{kd[k]+k}' for k in sorted(kd)))
