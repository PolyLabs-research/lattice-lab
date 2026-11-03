# Part 1: per-k frontiers d_k(n) = max d over (deduplicated) groups at n with that k
from load import *
from scipy import optimize, stats
byk=collections.defaultdict(dict)
for e in U:
    byk[e['k']].setdefault(e['n'],[]).append(e)
F={k:{n:max(x['d'] for x in v) for n,v in byk[k].items()} for k in byk}

def records(fr):
    # strict running-max (upper staircase) points
    out=[];best=-1
    for n in sorted(fr):
        if fr[n]>best: out.append(n); best=fr[n]
    return out

def fit_power(ns,ds):
    x=np.log(ns); y=np.log(ds)
    r=stats.linregress(x,y)
    return math.exp(r.intercept), r.slope, r.stderr, np.sqrt(np.mean((y-(r.intercept+r.slope*x))**2))

def rms_d(pred,ds): return float(np.sqrt(np.mean((np.asarray(pred)-np.asarray(ds))**2)))

print("k  #n  nrange   | power fit (all frontier n): c, b+-se, rmslog | power fit (records only) b | "
      "1-par sqrt(S n/k): S, rms_d | 1-par a*sqrt(n ln n/k): a', rms_d | 1-par c n^0.6/..: rms_d | max kd^2/n (at n)")
res={}
for k in sorted(F):
    fr=F[k]; ns=np.array(sorted(fr),float); ds=np.array([fr[n] for n in sorted(fr)],float)
    if len(ns)<5: 
        sc=[k*fr[n]**2/n for n in fr]; nm=max(fr,key=lambda n:k*fr[n]**2/n)
        print(f"{k:2d} {len(ns):3d} {int(ns.min())}-{int(ns.max())}  (too few n)  max score {max(sc):.2f} at n={nm} d={fr[nm]}")
        continue
    c,b,se,rl=fit_power(ns,ds)
    rn=records(fr); cr,br,ser,_=fit_power(np.array(rn,float),np.array([fr[n] for n in rn],float))
    # one-parameter fits in log space (geometric mean of ratio)
    S=math.exp(np.mean(np.log(ds**2*k/ns)))
    a=math.exp(np.mean(np.log(ds/np.sqrt(ns*np.log(ns)/k))))
    rS=rms_d(np.sqrt(S*ns/k),ds); ra=rms_d(a*np.sqrt(ns*np.log(ns)/k),ds)
    rp=rms_d(c*ns**b,ds)
    sc=ds**2*k/ns; im=int(np.argmax(sc))
    # trend of score with n
    t1=stats.linregress(np.log(ns),np.log(sc))
    t2=stats.linregress(np.log(ns),np.log(sc/np.log(ns)))
    res[k]=dict(c=c,b=b,se=se,br=br,ser=ser,S=S,a=a,rS=rS,ra=ra,rp=rp)
    print(f"{k:2d} {len(ns):3d} {int(ns.min())}-{int(ns.max())} | c={c:.3f} b={b:.3f}+-{se:.3f} rmslog={rl:.3f} rms_d={rp:.2f} | rec b={br:.3f}+-{ser:.3f} (#{len(rn)}) "
          f"| S={S:.2f} rms_d={rS:.2f} | a={a:.3f} rms_d={ra:.2f} | max score {sc[im]:.2f} @n={int(ns[im])},d={int(ds[im])} "
          f"| slope log(kd2/n) vs log n = {t1.slope:.3f}+-{t1.stderr:.3f}; of kd2/(n ln n) = {t2.slope:.3f}+-{t2.stderr:.3f}")
import pickle; pickle.dump((F,res),open('part1.pkl','wb'))
