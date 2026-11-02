import json, math, collections, sys
import numpy as np
from scipy import stats, optimize
P='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
E=json.load(open(P))['entries']
def inv(l,m):
    g=math.gcd(l,m); return (g, l*m//g)
# dedupe isomorphic tori: per (group,k) keep max d
best={}
for e in E:
    key=(inv(e['l'],e['m']),e['k'])
    if key not in best or e['d']>best[key]['d']: best[key]=e
grp=collections.defaultdict(dict); N={}; ST={}
for (g,k),e in best.items():
    grp[g][k]=e['d']; N[g]=e['n']; ST.setdefault(g,set()).add(e['stage'])
def cv(v): return np.std(v)/np.mean(v)
def nls(f,p0,ks,ds):
    best=None
    for p in p0:
        try:
            s=optimize.least_squares(lambda p:f(p,ks)-ds,p,max_nfev=5000)
            if best is None or s.cost<best.cost: best=s
        except Exception: pass
    return best
def run(minK=4, kcap=999, nmax=999, drop_d2=False, verbose=False, label=''):
    rows=[]
    for g,kd in grp.items():
        if N[g]>nmax: continue
        ks=np.array(sorted(k for k in kd if k<=kcap and not (drop_d2 and kd[k]<=2)),float)
        if len(ks)<minK: continue
        ds=np.array([kd[int(k)] for k in ks],float)
        r={}
        r['g']=g; r['n']=N[g]; r['nk']=len(ks); r['ks']=ks; r['ds']=ds
        r['cv_sum']=cv(ds+ks); r['cv_kd2']=cv(ks*ds**2); r['cv_kd']=cv(ks*ds); r['cv_d']=cv(ds)
        # log-space spread (scale-free) for invariants: std of log(invariant), converted to d-equivalent log units
        r['sl_sum']=np.std(np.log(ds+ks)); r['sl_kd2']=np.std(np.log(ks*ds**2))/2; r['sl_kd']=np.std(np.log(ks*ds))
        # 1-param models, rms in d units (LSQ in d space)
        r['rms1_add']=np.std(ds+ks)                    # d=C-k
        S=nls(lambda p,k:np.sqrt(np.abs(p[0])/k),[[np.mean(ks*ds**2)]],ks,ds); r['rms1_kd2']=np.sqrt(2*S.cost/len(ks))
        S=nls(lambda p,k:p[0]/k,[[np.mean(ks*ds)]],ks,ds); r['rms1_kd']=np.sqrt(2*S.cost/len(ks))
        r['rms1_const']=np.std(ds)
        # 2-param models
        lr=stats.linregress(ks,ds); r['a']=-lr.slope; r['D']=lr.intercept
        r['rms_lin']=np.sqrt(np.mean((ds-(lr.intercept+lr.slope*ks))**2))
        lp=stats.linregress(np.log(ks),np.log(ds)); r['gam_log']=-lp.slope
        r['rms_pow_logfit']=np.sqrt(np.mean((ds-np.exp(lp.intercept+lp.slope*np.log(ks)))**2))
        S=nls(lambda p,k:p[0]*k**(-p[1]),[[math.exp(lp.intercept),-lp.slope],[30,0.5],[30,1.5]],ks,ds); r['rms_pow']=np.sqrt(2*S.cost/len(ks)); r['gam']=S.x[1]
        S=nls(lambda p,k:p[0]*np.sqrt(np.clip(1-k/p[1],0,None)),[[lr.intercept,max(ks)*1.2],[lr.intercept*1.1,max(ks)*2],[40,60]],ks,ds); r['rms_sqs']=np.sqrt(2*S.cost/len(ks))
        # LOO cross-validation (predict held-out point) for lin vs pow vs d+k=C
        el=[];ep=[];ea=[];ek2=[]
        for i in range(len(ks)):
            m=np.ones(len(ks),bool); m[i]=False
            l2=stats.linregress(ks[m],ds[m]); el.append(ds[i]-(l2.intercept+l2.slope*ks[i]))
            S=nls(lambda p,k:p[0]*k**(-p[1]),[[30,0.5],[30,1.0]],ks[m],ds[m]); ep.append(ds[i]-S.x[0]*ks[i]**(-S.x[1]))
            ea.append(ds[i]-(np.mean(ds[m]+ks[m])-ks[i]))
            S2=np.mean(ks[m]*ds[m]**2); ek2.append(ds[i]-np.sqrt(S2/ks[i]))
        r['loo_lin']=np.sqrt(np.mean(np.square(el))); r['loo_pow']=np.sqrt(np.mean(np.square(ep))); r['loo_add']=np.sqrt(np.mean(np.square(ea))); r['loo_kd2']=np.sqrt(np.mean(np.square(ek2)))
        # extrapolation: fit on all but largest k, predict largest k
        m=ks<ks.max()
        l2=stats.linregress(ks[m],ds[m]); r['ex_lin']=ds[-1]-(l2.intercept+l2.slope*ks[-1])
        S=nls(lambda p,k:p[0]*k**(-p[1]),[[30,0.5],[30,1.0]],ks[m],ds[m]); r['ex_pow']=ds[-1]-S.x[0]*ks[-1]**(-S.x[1])
        r['ex_add']=ds[-1]-(np.mean(ds[m]+ks[m])-ks[-1])
        r['ex_kd2']=ds[-1]-np.sqrt(np.mean(ks[m]*ds[m]**2)/ks[-1])
        rows.append(r)
    R=lambda k: np.array([r[k] for r in rows])
    print(f"\n===== {label} minK={minK} kcap={kcap} nmax={nmax} drop_d2={drop_d2}: {len(rows)} groups, n range {R('n').min()}-{R('n').max()}")
    print(f" median CV:  d+k {np.median(R('cv_sum')):.3f} | kd^2 {np.median(R('cv_kd2')):.3f} | kd {np.median(R('cv_kd')):.3f} | d {np.median(R('cv_d')):.3f}")
    print(f" median log-sd (d-equivalent): log(d+k) {np.median(R('sl_sum')):.3f} | log(kd^2)/2 {np.median(R('sl_kd2')):.3f} | log(kd) {np.median(R('sl_kd')):.3f}")
    print(f" 1-param rms_d (median): d=C-k {np.median(R('rms1_add')):.2f} | d=sqrt(S/k) {np.median(R('rms1_kd2')):.2f} | d=S/k {np.median(R('rms1_kd')):.2f} | d=C {np.median(R('rms1_const')):.2f}")
    print(f"   wins d=C-k vs sqrt(S/k): {np.sum(R('rms1_add')<R('rms1_kd2'))}/{len(rows)}")
    print(f" 2-param rms_d (median): lin {np.median(R('rms_lin')):.2f} | pow(logfit) {np.median(R('rms_pow_logfit')):.2f} | pow(NLS d-space) {np.median(R('rms_pow')):.2f} | sqrt-Singleton {np.median(R('rms_sqs')):.2f}")
    print(f"   lin beats pow(logfit) {np.sum(R('rms_lin')<R('rms_pow_logfit'))}/{len(rows)} ; lin beats pow(NLS) {np.sum(R('rms_lin')<R('rms_pow'))}/{len(rows)} ; lin beats sqrt-Singleton {np.sum(R('rms_lin')<R('rms_sqs'))}/{len(rows)}")
    print(f" median a={np.median(R('a')):.2f} IQR {np.percentile(R('a'),25):.2f}-{np.percentile(R('a'),75):.2f} range {R('a').min():.2f}-{R('a').max():.2f}; median gamma(NLS)={np.median(R('gam')):.2f}")
    sp=stats.spearmanr(R('n'),R('a')); print(f" Spearman(n,a)={sp.correlation:.2f} p={sp.pvalue:.4f};  Spearman(n, a/D)={stats.spearmanr(R('n'),R('a')/R('D')).correlation:.2f};  Spearman(n,cv_sum)={stats.spearmanr(R('n'),R('cv_sum')).correlation:.2f}")
    print(f" LOO rms_d (median): lin {np.median(R('loo_lin')):.2f} | pow {np.median(R('loo_pow')):.2f} | d+k=C {np.median(R('loo_add')):.2f} | kd^2=S {np.median(R('loo_kd2')):.2f};  lin<pow LOO in {np.sum(R('loo_lin')<R('loo_pow'))}/{len(rows)}, add<lin LOO {np.sum(R('loo_add')<R('loo_lin'))}/{len(rows)}")
    print(f" extrapolate largest k (median |err|, mean err): lin {np.median(np.abs(R('ex_lin'))):.2f} ({np.mean(R('ex_lin')):+.2f}) | pow {np.median(np.abs(R('ex_pow'))):.2f} ({np.mean(R('ex_pow')):+.2f}) | d+k=C {np.median(np.abs(R('ex_add'))):.2f} ({np.mean(R('ex_add')):+.2f}) | kd^2=S {np.median(np.abs(R('ex_kd2'))):.2f} ({np.mean(R('ex_kd2')):+.2f})")
    if verbose:
        for r in sorted(rows,key=lambda r:r['n']):
            print(f"  n={r['n']:3d} G={r['g']} nk={r['nk']} a={r['a']:.2f} D={r['D']:.1f} cv_sum={r['cv_sum']:.3f} rms lin/pow/sqs={r['rms_lin']:.2f}/{r['rms_pow']:.2f}/{r['rms_sqs']:.2f} k:d "+' '.join(f"{int(k)}:{int(d)}" for k,d in zip(r['ks'],r['ds'])))
    return rows
rows=run(verbose=True,label='BASE')
run(minK=3,label='>=3 k')
run(kcap=20,label='k<=20')
run(nmax=300,label='n<=300 (stages 3 only)')
run(drop_d2=True,label='drop d=2 points')
run(minK=5,label='>=5 k')
