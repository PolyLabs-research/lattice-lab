# Part 3: one surface d(n,k) for the (n,k)-frontier; fit n<=300, test n>300 (stage 4)
from load import *
from scipy import optimize
import pickle
F,_=pickle.load(open('part1.pkl','rb'))
pts=[(n,k,F[k][n]) for k in F for n in F[k]]
pts=np.array(sorted(pts),float)
N,K,Dd=pts[:,0],pts[:,1],pts[:,2]
tr=N<=300; te=N>300
print(f"(n,k)-frontier points: {len(N)}  train {tr.sum()}  test {te.sum()}  (test n: {int(N[te].min())}-{int(N[te].max())})")
L=np.log
models={
 'M0 c n^b (no k)            [2p]': (lambda p,n,k: p[0]+p[1]*L(n), [0,0.6]),
 'M1 c n^b k^-1/2            [2p]': (lambda p,n,k: p[0]+p[1]*L(n)-0.5*L(k), [0,0.6]),
 'M2 c n^1/2 k^-g            [2p]': (lambda p,n,k: p[0]+0.5*L(n)-p[1]*L(k), [0,0.3]),
 'M4 c sqrt(n ln n) k^-g     [2p]': (lambda p,n,k: p[0]+0.5*L(n*L(n))-p[1]*L(k), [0,0.3]),
 'M5 c (n/k)^b               [2p]': (lambda p,n,k: p[0]+p[1]*L(n/k), [0,0.6]),
 'M6 sqrt(S n/k)             [1p]': (lambda p,n,k: 0.5*(p[0]+L(n/k)), [1]),
 'M7 sqrt(S n ln n/k)        [1p]': (lambda p,n,k: 0.5*(p[0]+L(n*L(n)/k)), [1]),
 'M3 c n^b k^-g              [3p]': (lambda p,n,k: p[0]+p[1]*L(n)-p[2]*L(k), [0,0.6,0.3]),
 'M8 c n^b k^-g, k<=16 only  [3p]': (lambda p,n,k: p[0]+p[1]*L(n)-p[2]*L(k), [0,0.6,0.3]),
 'M9 c n^b k^-1/2, k<=16     [2p]': (lambda p,n,k: p[0]+p[1]*L(n)-0.5*L(k), [0,0.6]),
 'M10 c n^b k^-g n-dep: c n^b k^-(g0 - g1 ln n) ... skipped': None,
}
def even(x): return 2*np.maximum(1,np.round(x/2))
out={}
for name,mdl in models.items():
    if mdl is None: continue
    f,p0=mdl
    sel=tr.copy()
    if 'k<=16' in name: sel&=(K<=16)
    r=lambda p: f(p,N[sel],K[sel])-L(Dd[sel])
    sol=optimize.least_squares(r,p0)
    p=sol.x
    pr=np.exp(f(p,N,K))
    def stats_(m):
        e=Dd[m]-pr[m]; el=L(Dd[m])-L(pr[m]); pe=even(pr[m])
        return dict(rms=np.sqrt(np.mean(e**2)),bias=np.mean(e),rmsl=np.sqrt(np.mean(el**2)),
                    exact=np.mean(pe==Dd[m]),within2=np.mean(np.abs(pe-Dd[m])<=2),N=m.sum())
    s_tr=stats_(sel); 
    te_sel=te&(K<=16) if 'k<=16' in name else te
    s_te=stats_(te_sel)
    out[name]=(p,pr,te_sel)
    ps=' '.join(f'{x:.3f}' for x in ([math.exp(p[0])]+list(p[1:])))
    print(f"{name} params(c,..)={ps:24s} TRAIN rms_d={s_tr['rms']:.2f} rmslog={s_tr['rmsl']:.3f} | TEST(N={s_te['N']}) rms_d={s_te['rms']:.2f} bias={s_te['bias']:+.2f} rmslog={s_te['rmsl']:.3f} exact-even={s_te['exact']:.2f} within+-2={s_te['within2']:.2f}")
pickle.dump((pts,out),open('part3.pkl','wb'))
# detailed residuals of the best 2p model on test, by k
for name in ('M1 c n^b k^-1/2            [2p]','M3 c n^b k^-g              [3p]','M9 c n^b k^-1/2, k<=16     [2p]'):
    p,pr,ts=out[name]
    print('\n',name,'test residuals d - pred (pred rounded to even):')
    for kk in sorted(set(K[te])):
        m=te&(K==kk)
        print(f"  k={int(kk):2d}: "+' '.join(f"{int(n)}:{int(d)}/{int(even(q))}" for n,d,q in zip(N[m],Dd[m],pr[m])))
    # train residual by k
    print('  train mean log-residual by k:',' '.join(f"{int(kk)}:{np.mean(L(Dd[tr&(K==kk)])-L(pr[tr&(K==kk)])):+.2f}" for kk in sorted(set(K[tr]))))
