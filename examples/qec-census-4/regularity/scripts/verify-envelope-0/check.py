"""Independent check of: 0.615 sqrt(n ln n), fitted on n<=300 thresholds, floor-even, hits 13/14 stage-4 record n."""
import json, math, sys
import numpy as np
from collections import defaultdict
D=json.load(open(sys.argv[1]))
E=D['entries']
mx=defaultdict(int); stage={}
for e in E:
    mx[e['n']]=max(mx[e['n']],e['d']); stage.setdefault(e['n'],set()).add(e['stage'])
ns=sorted(mx)
# running record & transitions
rec=0; trans=[]  # (D, n_prev, n_first)
prev=None
for n in ns:
    if mx[n]>rec:
        for Dd in range(rec+2, mx[n]+1, 2):
            trans.append((Dd, prev, n))
        rec=mx[n]
    prev=n
print('transitions (d, last n below, first n reaching):'); print(trans)
g=lambda n,c=1.0: c*np.sqrt(n*np.log(n))
fe=lambda x: 2*np.floor(x/2)
train=[(d,a,b) for d,a,b in trans if 6<=d<=24]
nx=np.array([(a+b)/2 for d,a,b in train]); dv=np.array([d for d,a,b in train],float)
print('n_x', nx.tolist())
G=g(nx); c=(G@dv)/(G@G)
res=dv-c*G; s=np.sqrt(res@res/(len(dv)-1)); se=s/np.sqrt(G@G)
print(f'c (LS, midpoints) = {c:.5f}  resid sd {s:.3f}  SE(c) {se:.5f}')
# alternative anchor choices
for name,pts in [('first-seen n',[b for d,a,b in train]),('last-below n',[a for d,a,b in train])]:
    Gp=g(np.array(pts,float)); print(name, 'c =', round((Gp@dv)/(Gp@Gp),5))
# feasible c that makes each transition land in its window: c*g(n_prev) < d <= c*g(n_first)
print('per-transition feasible c window [d/g(first), d/g(prev)):')
lo_all=0; hi_all=9
for d,a,b in trans:
    if d<6: continue
    lo,hi=d/g(b), d/g(a)
    tag='train' if d<=24 else 'TEST'
    print(f'  d={d:2d} ({a},{b}] c in [{lo:.4f},{hi:.4f})  {tag}  ok@c={lo<=c<hi}')
    if d<=24: lo_all=max(lo_all,lo); hi_all=min(hi_all,hi)
print(f'c consistent with ALL 10 train transitions: [{lo_all:.4f},{hi_all:.4f})', 'EMPTY' if lo_all>=hi_all else '')
def cross(Dd,c):
    from scipy.optimize import brentq
    return brentq(lambda n: c*math.sqrt(n*math.log(n))-Dd, 3, 1e5)
print(f'crossings at c={c:.4f}: 26->{cross(26,c):.1f}, 28->{cross(28,c):.1f}, 30->{cross(30,c):.1f}')
for cc in (c-se, c+se, c-2*se, c+2*se):
    print(f'  c={cc:.4f}: 26->{cross(26,cc):.1f} 28->{cross(28,cc):.1f}')
# stage 4 evaluation
s4=[n for n in ns if '4' in stage[n]]
running=24; hits=0; tot=0; hits_all=0
print('stage-4: n, actual, running record, pred, ok')
for n in s4:
    pred=int(fe(g(n,c)))
    is_rec = mx[n]>=running
    running=max(running,mx[n])
    ok=pred==mx[n]
    if is_rec: tot+=1; hits+=ok
    hits_all+=ok
    print(f'  {n} {mx[n]} rec={is_rec} pred={pred} ok={ok}  f={g(n,c):.2f}')
print(f'hits at record n: {hits}/{tot}; at all stage-4 n: {hits_all}/{len(s4)}')
# compare one-parameter family c*n^b for fixed b, same threshold fit, count record hits
print('same recipe, other one-parameter shapes c*n^b (b fixed) and c*sqrt(n)*(ln n)^p:')
def evalshape(h,label):
    H=h(nx); cc=(H@dv)/(H@H); running=24; hh=0; tt=0; trv=0
    for d,a,b in train:
        if not (cc*h(np.array([a]))[0] < d <= cc*h(np.array([b]))[0]): trv+=1
    for n in s4:
        is_rec=mx[n]>=running; running=max(running,mx[n])
        if is_rec:
            tt+=1; hh+= int(fe(cc*h(np.array([n]))[0]))==mx[n]
    print(f'  {label:28s} c={cc:.4f} train transitions missed {trv}/10  test record hits {hh}/{tt}')
for b in (0.55,0.57,0.58,0.59,0.60,0.61,0.62,0.63,0.65):
    evalshape(lambda n,b=b: n**b, f'n^{b}')
for p in (0.25,0.5,0.75):
    evalshape(lambda n,p=p: np.sqrt(n)*np.log(n)**p, f'sqrt(n)(ln n)^{p}')
evalshape(lambda n: np.sqrt(n), 'sqrt(n)')
evalshape(lambda n: n/np.log(n), 'n/ln n')
evalshape(lambda n: np.sqrt(n*np.log(n)), 'sqrt(n ln n) [claim]')
# rolling origin: fit thresholds with d<=Dmax, predict next transitions' windows
print('rolling-origin (same recipe, fit on transitions up to Dmax, predict next ones):')
allt=[(d,a,b) for d,a,b in trans if d>=6]
for Dmax in (14,16,18,20,22,24):
    tr=[(d,a,b) for d,a,b in allt if d<=Dmax]
    X=g(np.array([(a+b)/2 for d,a,b in tr])); y=np.array([d for d,a,b in tr],float)
    cc=(X@y)/(X@X)
    out=[]
    for d,a,b in allt:
        if d<=Dmax: continue
        nc=cross(d,cc); out.append(f'{d}:{nc:.0f} in ({a},{b}] {"HIT" if a<nc<=b else "miss"}')
    print(f'  Dmax={Dmax} c={cc:.4f} ', '; '.join(out))
