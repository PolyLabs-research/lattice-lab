# Exhaustive k-set of CONNECTED weight-6 codes on a group with at most one even side,
# k = 2|Z(A') & Z(B')| over the odd part G' (term 1 for connected codes), by characters.
import numpy as np, itertools, json, sys
from math import gcd
from gf import partner_table, primes, ordmod
def oddpart(x):
    while x%2==0: x//=2
    return x
def kset_odd(n1,n2):
    """G' = Z_n1 x Z_n2, n1 | n2, both odd. Returns sorted k-set (connected codes, k>0)."""
    assert n2%n1==0
    N=n2
    if N==1: return []
    part=np.array(partner_table(N))
    els=[(a,b) for a in range(n1) for b in range(n2)]
    chars=[(i,j) for i in range(n1) for j in range(n2)]
    ci=np.array([c[0] for c in chars]); cj=np.array([c[1] for c in chars])
    def ev(u): return (ci*u[0]*(N//n1)+cj*u[1])%N
    E={u:ev(u) for u in els}
    ps=primes(n2)
    def sig(vs):
        # span of images in G'/pG' for each p, encoded canonically
        out=[]
        for p in ps:
            if n1%p==0:
                vecs=[(v[0]%p,v[1]%p) for v in vs]
                # rank over F_p of 2-dim vectors, and the line if rank 1
                nz=[w for w in vecs if w!=(0,0)]
                if not nz: out.append((0,)); continue
                w0=nz[0]
                rk2=any((w0[0]*w[1]-w0[1]*w[0])%p for w in nz)
                if rk2: out.append((2,)); continue
                # normalize line
                if w0[0]%p: inv=pow(w0[0],-1,p); out.append((1,1,(w0[1]*inv)%p))
                else: out.append((1,0,1))
            else:
                out.append((1,) if any(v[1]%p for v in vs) else (0,))
        return tuple(out)
    combos={}
    nz=[u for u in els if u!=(0,0)]
    for u,v in itertools.combinations(nz,2):
        eu,evv=E[u],E[v]
        z=(part[eu]==evv)
        if not z.any(): continue
        mask=int(''.join('1' if b else '0' for b in z),2) if False else z.tobytes()
        s=sig([u,v])
        combos.setdefault(mask,set()).add(s)
    masks=list(combos)
    marr=[np.frombuffer(m,dtype=bool) for m in masks]
    def gen(s1,s2):
        for p,a,b in zip(ps,s1,s2):
            if n1%p==0:
                if a[0]==2 or b[0]==2: continue
                if a[0]==1 and b[0]==1 and a!=b: continue
                return False
            else:
                if a[0]==1 or b[0]==1: continue
                return False
        return True
    ks=set()
    for i in range(len(masks)):
        for j in range(i,len(masks)):
            inter=int((marr[i]&marr[j]).sum())
            if inter==0: continue
            if 2*inter in ks: continue
            if any(gen(s1,s2) for s1 in combos[masks[i]] for s2 in combos[masks[j]]):
                ks.add(2*inter)
    return sorted(ks)
if __name__=='__main__':
    print(kset_odd(1,3),kset_odd(3,3),kset_odd(1,7),kset_odd(1,21),kset_odd(1,15))
