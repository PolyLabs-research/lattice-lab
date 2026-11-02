import json, math
from collections import defaultdict
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
def canon(l,m):
    # invariant factors of Z_l x Z_m: (gcd, lcm)
    g=math.gcd(l,m); return (g, l*m//g)
def oddpart(x):
    while x%2==0: x//=2
    return x
def pmod(a,b):
    db=b.bit_length()-1
    while a and a.bit_length()-1>=db:
        a^=b<<(a.bit_length()-1-db)
    return a
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def ppow(p,e,mod=None):
    r=1
    for _ in range(e):
        # multiply r by p
        x=0;q=p;rr=r
        while rr:
            if rr&1: x^=q
            rr>>=1;q<<=1
        r=x
    return r
def critE(g,N):
    e=math.lcm(oddpart(g),oddpart(N))
    if e==1: return False
    a=(1<<e)|1  # x^e+1
    b=ppow(0b11,e)^1  # (x+1)^e+1
    return pgcd(a,b)!=1
present=defaultdict(set); tor=defaultdict(set)
for e in E:
    present[e['n']].add(canon(e['l'],e['m'])); tor[e['n']].add((e['l'],e['m']))
print("min l present:",min(e['l'] for e in E))
# expected groups for n<=400
missing=[]
for n in range(4,401,2):
    N=n//2
    exp=set()
    for g in range(1,N+1):
        if N%g==0 and (N//g)%g==0:
            if critE(g,N//g): exp.add((g,N//g))
    # restrict cyclic (g=1) to N expressible as coprime l,m>=2? keep all and flag
    got=present.get(n,set())
    if exp-got or got-exp:
        missing.append((n,sorted(exp-got),sorted(got-exp)))
for x in missing: print(x)
