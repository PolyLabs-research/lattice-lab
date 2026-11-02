# Part 4b: the 1-parameter surface d = c sqrt(n) - k vs the envelope and its band maxima of d/sqrt(n)
from load import *
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
pts=np.array(sorted((n,k,F[k][n]) for k in F for n in F[k]),float); N,K,Dd=pts.T
for lab,sel in (('all k',K>0),('k<=16',K<=16)):
    tr=sel&(N<=300)
    c=np.sum((Dd[tr]+K[tr])*np.sqrt(N[tr]))/np.sum(N[tr])  # LS for d+k = c sqrt(n)
    pr=c*np.sqrt(N)-K; te=sel&(N>300)
    e=Dd[te]-pr[te]; pe=2*np.maximum(1,np.round(pr[te]/2))
    print(f"[{lab}] c={c:.4f} (fit n<=300) | test N={te.sum()} rms {np.sqrt(np.mean(e**2)):.2f} bias {np.mean(e):+.2f} within2 {np.mean(np.abs(pe-Dd[te])<=2):.2f} exact {np.mean(pe==Dd[te]):.2f}")
c=1.692
ns=sorted(set(N.astype(int)))
env={n:max(F[k][n] for k in F if n in F[k]) for n in ns}
kmin={n:min(k for k in F if n in F[k]) for n in ns}
pe={n:c*math.sqrt(n)-kmin[n] for n in ns}
r=np.array([env[n]-pe[n] for n in ns])
print(f"envelope (86 n): d_max - (1.692 sqrt(n) - kmin(n)): rms {np.sqrt(np.mean(r**2)):.2f}, mean {r.mean():+.2f}, within +-2: {np.mean(np.abs(r)<=2):.2f}, max |r| {np.abs(r).max():.2f} at n={ns[int(np.argmax(np.abs(r)))]}")
print("band (50-wide) maxima of d/sqrt(n) on envelope vs model 1.692 - 4/sqrt(n) at band top:")
for a in range(0,400,50):
    v=[(env[n]/math.sqrt(n),n) for n in ns if a<n<=a+50]
    if v:
        m=max(v); print(f"  ({a},{a+50}]: observed max {m[0]:.3f} at n={m[1]} (k={kmin[m[1]]}); model c - kmin/sqrt(n) at that n: {c-kmin[m[1]]/math.sqrt(m[1]):.3f}; at band top {c-4/math.sqrt(a+50):.3f}")
# score implications
print("max score under d=c sqrt(n)-k: 4c^3 sqrt(n)/27 at k=c sqrt(n)/3:",{n:(round(4*c**3*math.sqrt(n)/27,1),round(c*math.sqrt(n)/3,1)) for n in (100,150,200,250,300,350,384)})
