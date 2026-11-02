import json, math, collections
import numpy as np
D=json.load(open('../../census-data.json'))
E=D['entries']
top={}
for e in E:
    n=e['n']
    if n not in top or e['d']>top[n]: top[n]=e['d']
ns=sorted(top)
comb=[n for n in ns if n%6==0]
other=[n for n in ns if n%6]
N=np.array(comb,float); Dd=np.array([top[n] for n in comb])
def q(x): return 2*np.floor(x/2)
# (a) c-window for 2*floor(c sqrt(n ln n)/2)
g=np.sqrt(N*np.log(N))
cs=np.arange(0.55,0.70,0.00001)
hits=np.array([(q(c*g)==Dd).sum() for c in cs])
best=hits.max(); win=cs[hits==best]
print('(a) sqrt(n ln n) floor-even: max hits',best,'of',len(comb),'c window [%.5f, %.5f]'%(win.min(),win.max()))
for h in (60,59,58,57,55):
    w=cs[hits>=h]; print('   c range with >=%d hits: [%.4f,%.4f] (contiguous? %s)'%(h,w.min(),w.max(), np.all(np.diff(np.where(hits>=h)[0])==1)))
# round convention
hr=np.array([(2*np.round(c*g/2)==Dd).sum() for c in cs]); print('   round-to-even best',hr.max())
# (b) alternative families, in-sample max hits
def best1(fn, grid):
    b=(-1,None)
    for p in grid:
        h=(q(fn(N,*p))==Dd).sum()
        if h>b[0]: b=(h,p)
    return b
fams={
 'c*sqrt(n)': (lambda n,c: c*np.sqrt(n), [(c,) for c in np.arange(1.0,2.0,0.0005)]),
 'c*n^b': (lambda n,c,b: c*n**b, [(c,b) for c in np.arange(0.4,1.2,0.002) for b in np.arange(0.50,0.72,0.0025)]),
 'c*sqrt(n)*ln(n)^p (p free)': (lambda n,c,p: c*np.sqrt(n)*np.log(n)**p, [(c,p) for c in np.arange(0.2,1.5,0.002) for p in np.arange(0.2,0.8,0.01)]),
 'a*sqrt(n)+b': (lambda n,a,b: a*np.sqrt(n)+b, [(a,b) for a in np.arange(1.3,2.0,0.0025) for b in np.arange(-6,2,0.05)]),
 'c*sqrt(n)*ln(ln n)': (lambda n,c: c*np.sqrt(n)*np.log(np.log(n)), [(c,) for c in np.arange(0.5,1.5,0.0002)]),
 'c*n^0.6': (lambda n,c: c*n**0.6, [(c,) for c in np.arange(0.5,1.2,0.0002)]),
 'registered envelope 0.801 n^0.607 (no refit)': (lambda n: 0.8011*n**0.6074, [()]),
}
for k,(fn,grid) in fams.items():
    h,p=best1(fn,grid)
    miss=[int(n) for n,dd,pp in zip(N,Dd,q(fn(N,*p))) if dd!=pp]
    print('(b) %-45s best %d/63 at %s misses %s'%(k,h,tuple(round(float(x),4) for x in p),miss))
# monotone staircase upper bound
print('    best non-decreasing step function: 62/63 (only the dip at 312 must miss)')
# (c) honest OOS: fit on n<=300, test 302..384
tr=N<=300; te=~tr
print('(c) train cols',tr.sum(),'test cols',te.sum(), 'test n',[int(x) for x in N[te]])
def oos(fn,grid,name):
    res=[(int((q(fn(N[tr],*p))==Dd[tr]).sum()),p) for p in grid]
    m=max(r[0] for r in res); tied=[p for h,p in res if h==m]
    th=[int((q(fn(N[te],*p))==Dd[te]).sum()) for p in tied]
    print('    %-30s train %d/%d, %d tied params, test hits min %d max %d of %d'%(name,m,tr.sum(),len(tied),min(th),max(th),te.sum()))
oos(lambda n,c: c*np.sqrt(n*np.log(n)), [(c,) for c in np.arange(0.55,0.70,0.00005)],'c sqrt(n ln n)')
oos(lambda n,c,b: c*n**b, [(c,b) for c in np.arange(0.4,1.2,0.002) for b in np.arange(0.50,0.72,0.0025)],'c n^b')
oos(lambda n,c: c*n**0.6, [(c,) for c in np.arange(0.5,1.2,0.0001)],'c n^0.6')
oos(lambda n,a,b: a*np.sqrt(n)+b, [(a,b) for a in np.arange(1.3,2.0,0.0025) for b in np.arange(-6,2,0.05)],'a sqrt(n)+b')
oos(lambda n,c: c*np.sqrt(n), [(c,) for c in np.arange(1.0,2.0,0.0002)],'c sqrt(n)')
# naive persistence: predict test col = last train top (24)
print('    persistence (d=24 for all test cols): hits', int((Dd[te]==24).sum()))
# (d) non-6-comb columns
print('(d) non-multiple-of-6 columns:',len(other))
f=lambda n: 2*math.floor(0.6175*math.sqrt(n*math.log(n))/2)
dev=[]
for n in other:
    dev.append(top[n]-f(n))
    print('    n=%d top d=%d pred=%d diff=%+d'%(n,top[n],f(n),top[n]-f(n)))
print('    hits',sum(1 for x in dev if x==0),'of',len(other),'; mean diff',np.mean(dev))
print('    all columns: hits', sum(1 for n in ns if f(n)==top[n]),'of',len(ns))
# (e) band maxima of d/sqrt(n), all entries, all k
print('(e) band maxima')
for lo in range(0,400,50):
    B=[e for e in E if lo<e['n']<=lo+50]
    if not B: continue
    m=max(e['d']/math.sqrt(e['n']) for e in B)
    arg=sorted({(e['n'],e['k'],e['d']) for e in B if abs(e['d']/math.sqrt(e['n'])-m)<1e-9})
    # is it a step: first comb column with that d?
    n0=arg[0][0]; dd=arg[0][2]
    first=min(n for n in comb if top[n]>=dd)
    # second best in band and its k
    others=sorted({(round(e['d']/math.sqrt(e['n']),4),e['n'],e['k'],e['d']) for e in B},reverse=True)[:3]
    print('    (%d,%d]: max %.4f at %s ; first comb n with top>=d: %d ; top3 %s'%(lo,lo+50,m,arg,first,others))
ks=collections.Counter(e['k'] for e in E); print('    k values present:',sorted(ks.items()))
# best d per n by k: is k=4 always the max?
viol=[]
for n in ns:
    b4=max([e['d'] for e in E if e['n']==n and e['k']==4],default=None)
    if b4 is None or b4<top[n]: viol.append((n,b4,top[n],[ (e['k'],e['d']) for e in E if e['n']==n and e['d']==top[n]]))
print('    columns where top is not attained at k=4:',viol)
# (f) plateau drops
print('(f) plateaus along comb (first..last column with that top)')
lev=collections.defaultdict(list)
for n in comb: lev[top[n]].append(n)
for dd in sorted(lev):
    a,b=min(lev[dd]),max(lev[dd]); contig=[n for n in comb if a<=n<=b]
    print('    d=%2d n %d..%d cols=%d (%s) drop %.1f%%'%(dd,a,b,len(lev[dd]),'contiguous' if len(contig)==len(lev[dd]) else 'NOT contiguous: '+str([n for n in contig if top[n]!=dd]),100*(1-math.sqrt(a/b))))
