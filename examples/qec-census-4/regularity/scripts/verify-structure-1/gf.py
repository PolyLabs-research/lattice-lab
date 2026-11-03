# Minimal GF(2^r) arithmetic with Python ints; primitive N-th root of unity; partner table.
import random
from math import gcd
def pdeg(a): return a.bit_length()-1
def pmod(a,b):
    db=pdeg(b)
    while a and pdeg(a)>=db: a^=b<<(pdeg(a)-db)
    return a
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def pmulmod(a,b,f): return pmod(pmul(a,b),f)
def ppowmod(a,e,f):
    r=1; a=pmod(a,f)
    while e:
        if e&1: r=pmulmod(r,a,f)
        a=pmulmod(a,a,f); e>>=1
    return r
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def primes(x):
    p=2; s=[]
    while p*p<=x:
        if x%p==0:
            s.append(p)
            while x%p==0: x//=p
        p+=1
    if x>1: s.append(x)
    return s
def frob_iter(a,k,f):
    for _ in range(k): a=pmulmod(a,a,f)
    return a
def irreducible(f):
    r=pdeg(f); x=2
    if frob_iter(x,r,f)!=x: return False
    for q in primes(r):
        h=frob_iter(x,r//q,f)^x
        if pdeg(pgcd(f,h))>0 or pgcd(f,h)==f: return False
    return True
def ordmod(N):
    if N==1: return 1
    r=1; v=2%N
    while v!=1: v=v*2%N; r+=1
    return r
_cache={}
def field_root(N,seed=1):
    """Return (f, pw) with f irreducible of degree r=ord_N(2) and pw[e]=zeta^e for a primitive N-th root zeta."""
    if N in _cache: return _cache[N]
    r=ordmod(N); rng=random.Random(seed*1000003+N)
    while True:
        f=(1<<r)|rng.getrandbits(r)|1
        if irreducible(f): break
    Q=(1<<r)-1; assert Q%N==0
    while True:
        a=rng.getrandbits(r) or 1
        z=ppowmod(a,Q//N,f)
        if z!=1 and all(ppowmod(z,N//p,f)!=1 for p in primes(N)) : break
    pw=[1]
    for _ in range(N-1): pw.append(pmulmod(pw[-1],z,f))
    assert pmulmod(pw[-1],z,f)==1 and len(set(pw))==N
    _cache[N]=(f,pw)
    return f,pw
def partner_table(N):
    """partner[p] = q with 1+zeta^p = zeta^q, or -1."""
    f,pw=field_root(N)
    idx={v:i for i,v in enumerate(pw)}
    return [idx.get(1^pw[p],-1) for p in range(N)]
