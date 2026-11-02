# Independent computation of "exact admissible orders": t = lcm(ord zeta, ord(1+zeta)), zeta != 1,
# using GF(2) cyclotomic polynomials Phi_f(x) and Phi_h(x+1) (ints as bit-vectors).
from math import gcd
import json
def pdeg(a): return a.bit_length()-1
def pmod(a,b):
    db=pdeg(b)
    while a and pdeg(a)>=db: a^=b<<(pdeg(a)-db)
    return a
def pdivmod(a,b):
    q=0; db=pdeg(b)
    while a and pdeg(a)>=db:
        s=pdeg(a)-db; q|=1<<s; a^=b<<s
    return q,a
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def compose_xplus1(p):
    # p(x+1)
    r=0; pw=1  # (x+1)^i
    for i in range(pdeg(p)+1):
        if (p>>i)&1: r^=pw
        pw=pmul(pw,0b11)
    return r
import sys
MAXT=int(sys.argv[1]) if len(sys.argv)>1 else 401
cyc={}
for f in range(1,MAXT+1,2):
    p=(1<<f)|1  # x^f+1 = x^f-1
    for d in range(1,f):
        if f%d==0:
            q,r=pdivmod(p,cyc[d]); assert r==0; p=q
    cyc[f]=p
assert cyc[1]==0b11 and cyc[3]==0b111
shift={h:compose_xplus1(cyc[h]) for h in cyc}
pairs=[]
for f in range(3,MAXT+1,2):
    for h in range(1,MAXT+1,2):
        g=pgcd(cyc[f],shift[h])
        if pdeg(g)>0: pairs.append((f,h,pdeg(g)))
def lcm(a,b): return a*b//gcd(a,b)
exact=sorted(set(lcm(f,h) for f,h,_ in pairs))
print('pairs (f,h,#zeta):',[p for p in pairs if lcm(p[0],p[1])<=401])
print('exact admissible t <= 401:',[t for t in exact if t<=401])
# brute check for small t directly in GF(2^r): does zeta of order f have 1+zeta of order h
json.dump({'pairs':pairs,'exact':exact},open('admissible.json','w'))
