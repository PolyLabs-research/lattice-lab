# Both-even groups: sample connected weight-6 codes with a common zero, exact k by GF(2) rank of [A|B].
import random, json, sys, time
from math import gcd
from gf import primes, ordmod
from kset import oddpart
def rank_gf2(rows):
    r=0; piv={}
    for v in rows:
        while v:
            h=v.bit_length()-1
            if h in piv: v^=piv[h]
            else: piv[h]=v; r+=1; break
    return r
def k_of(A,B,n1,n2):
    N=n1*n2
    def idx(a,b): return (a%n1)*n2+(b%n2)
    rows=[]
    for a in range(n1):
        for b in range(n2):
            v=0
            for (p,q) in A: v|=1<<idx(a+p,b+q)
            for (p,q) in B: v|=1<<(N+idx(a+p,b+q))
            rows.append(v)
    return 2*N-2*rank_gf2(rows)
def connected(A,B,n1,n2):
    steps={((p[0]-q[0])%n1,(p[1]-q[1])%n2) for P in (A,B) for p in P for q in P}
    seen={(0,0)}; st=[(0,0)]
    while st:
        x=st.pop()
        for s in steps:
            y=((x[0]+s[0])%n1,(x[1]+s[1])%n2)
            if y not in seen: seen.add(y); st.append(y)
    return len(seen)==n1*n2
def sample(n1,n2,tries,seed=0,odd_zero_bias=True):
    rng=random.Random(seed)
    ks={}
    els=[(a,b) for a in range(n1) for b in range(n2)]
    # bias: pick u,v whose projections lie in a subgroup whose characters can vanish: use the smallest
    # admissible t: choose odd projections in the t-torsion with probability 1/2
    for _ in range(tries):
        A=[(0,0)]+rng.sample(els[1:],2)
        B=[(0,0)]+rng.sample(els[1:],2)
        if not connected(A,B,n1,n2): continue
        k=k_of(A,B,n1,n2)
        if k>0: ks.setdefault(k,(A,B))
    return ks
if __name__=='__main__':
    groups=[tuple(map(int,g.split('x'))) for g in sys.argv[2:]]
    tries=int(sys.argv[1])
    for g in groups:
        t0=time.time(); ks=sample(*g,tries)
        print(g,'n=',2*g[0]*g[1],'k-values found',sorted(ks),'time',round(time.time()-t0,1),flush=True)
