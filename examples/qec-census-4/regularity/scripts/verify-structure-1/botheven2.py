# Biased sampler for both-even groups: odd projections share a zero at a character of order t_min,
# 2-components random; exact k by GF(2) rank; connected codes only.
import random, json, sys, time
from gf import partner_table, ordmod, primes
from kset import oddpart
from botheven import k_of, connected
A_=json.load(open('admissible.json')); exact=A_['exact']
def v2(x):
    s=0
    while x%2==0: x//=2; s+=1
    return s
def crt(r2,m2,ro,mo):
    for x in range(m2*mo):
        if x%m2==r2 and x%mo==ro: return x
def run(n1,n2,tries,seed=0):
    rng=random.Random(seed)
    s,t=v2(n1),v2(n2); o1,o2=oddpart(n1),oddpart(n2)
    N=o2; adm=[q for q in exact if N%q==0]; tm=min(adm)
    part=partner_table(N)
    chi=(0,N//tm)  # character of order tm on Z_o1 x Z_o2
    def e(u): return (chi[0]*u[0]*(N//o1)+chi[1]*u[1])%N
    odd_els=[(a,b) for a in range(o1) for b in range(o2) if (a,b)!=(0,0)]
    good=[(u,v) for i,u in enumerate(odd_els) for v in odd_els[i+1:] if part[e(u)]==e(v)]
    lift1={(r2,ro):crt(r2,2**s,ro,o1) for r2 in range(2**s) for ro in range(o1)}
    lift2={(r2,ro):crt(r2,2**t,ro,o2) for r2 in range(2**t) for ro in range(o2)}
    def lift(u): return (lift1[(rng.randrange(2**s),u[0])], lift2[(rng.randrange(2**t),u[1])])
    ks={}
    for _ in range(tries):
        (u,v)=rng.choice(good); (w,z)=rng.choice(good)
        A=[(0,0),lift(u),lift(v)]; B=[(0,0),lift(w),lift(z)]
        if len(set(A))<3 or len(set(B))<3 or not connected(A,B,n1,n2): continue
        k=k_of(A,B,n1,n2); ks[k]=ks.get(k,0)+1
    return tm,adm,ks
if __name__=='__main__':
    tries=int(sys.argv[1])
    for gs in sys.argv[2:]:
        n1,n2=map(int,gs.split('x')); t0=time.time()
        tm,adm,ks=run(n1,n2,tries)
        print((n1,n2),'n=',2*n1*n2,'adm',adm,'pred kmin',2*ordmod(tm),'k-values (count)',dict(sorted(ks.items())),'time',round(time.time()-t0,1),flush=True)
