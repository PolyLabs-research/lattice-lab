import itertools, numpy as np
from base2 import *
TH=thresholds()
print('thresholds (d, n_prev, n_first):',[(d,int(a),int(b)) for d,a,b in TH])
ns,Es,R=envelope()
print('max n', ns.max(), ' R(384)=',R[-1])
def run(dmin, nmax_data, label, how='mid'):
    th=[t for t in thresholds(nmax_data) if t[0]>=dmin]
    x=np.array([(a+b)/2 for d,a,b in th]); y=np.array([d for d,a,b in th],float)
    P={};A={}
    print(f'\n=== {label}: thresholds d>={dmin}, data n<={nmax_data}, m={len(x)} points (x range {x.min()}..{x.max()})')
    for m in KEYS:
        p,rss=fit(m,x,y); P[m]=p; A[m]=aicc(rss,len(x),len(p))
    best=min(A.values())
    for m in KEYS:
        print(f'  {m:22s} p={np.round(P[m],4)}  rms={np.sqrt(np.mean((f(m,x,P[m])-y)**2)):.3f}  dAICc={A[m]-best:6.2f}  n*30={crossing(m,P[m],30):7.1f}  f(384)={f(m,384,P[m]):.2f} f(1000)={f(m,1000,P[m]):.1f} f(2000)={f(m,2000,P[m]):.1f}')
    print('  pairwise first n with |diff| >= 1 / 2 / 4 (and max |diff| on n<=384):')
    rows=[]
    for a,b in itertools.combinations(KEYS,2):
        g=np.arange(12,385); mx=np.max(np.abs(f(a,g,P[a])-f(b,g,P[b]))[g>=30])
        s=[]
        for q in (1,2,4):
            r=first_diff(a,P[a],b,P[b],q,lo=30)
            s.append(f'{r[0]:9.0f}' if r is not None else '    >1e7')
        rows.append((a,b,s,mx))
        print(f'   {a:20s} vs {b:20s}: {"  ".join(s)}   max|D| n in[30,384]: {mx:.2f}')
    return P,A
for dmin in (6,14):
    run(dmin,10**9,f'ALL data')
for dmin in (6,14):
    run(dmin,300,f'TRAIN n<=300')
