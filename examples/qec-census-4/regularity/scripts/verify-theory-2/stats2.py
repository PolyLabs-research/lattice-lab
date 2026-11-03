import json, numpy as np
from scipy import stats
R=json.load(open('rows.json'))
def report(sel, label):
    n=np.array([r['n'] for r in sel],float); N=np.array([r['N'] for r in sel],float)
    print(f"== {label}: {len(sel)} groups, n {int(n.min())}-{int(n.max())}, N {int(N.min())}-{int(N.max())}")
    for key in ['mean','med','p90','mx']:
        y=np.array([r[key] for r in sel],float)
        res=stats.linregress(np.log(n),np.log(y))
        print(f"  {key:4s} slope={res.slope:.3f} +- {1.96*res.stderr:.3f} (95%)  r2={res.rvalue**2:.3f}")
    z=np.array([(r['mx']-r['mean'])/r['sd'] for r in sel]); eg=np.array([r['eg'] for r in sel])
    print(f"  mean z={z.mean():.3f}  mean E_gauss={eg.mean():.3f}  median E_gauss={np.median(eg):.2f}")
    for xn,x in [('N',N),('logN',np.log(N))]:
        pr=stats.pearsonr(x,z); sp=stats.spearmanr(x,z)
        print(f"  corr(z,{xn}) pearson r={pr[0]:.3f} p={pr[1]:.2f}; spearman={sp[0]:.3f} p={sp[1]:.2f}")
    ft=np.array([r['frac_top'] for r in sel])
    print(f"  frac within one even step of max: mean={ft.mean():.3f} median={np.median(ft):.3f} min={ft.min():.2f} max={ft.max():.2f}")
    # pooled over classes
    tot=sum(r['N'] for r in sel); top=sum(r['frac_top']*r['N'] for r in sel)
    print(f"  pooled over classes: {top/tot:.3f}")
    return n,N
base=[r for r in R if r['N']>1 and r['sd']>0]
report([r for r in base if r['n']>=42], 'n>=42')
report([r for r in base if r['n']>=42 and r['N']>=20], 'n>=42, N>=20')
report(base, 'all n (sd>0)')
report([r for r in base if r['N']>=20], 'N>=20 all n')
