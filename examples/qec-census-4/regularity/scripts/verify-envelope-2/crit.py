import math
def odd(x):
    while x%2==0: x//=2
    return x
def pmod(a,b):
    db=b.bit_length()
    while a and a.bit_length()>=db:
        a^=b<<(a.bit_length()-db)
    return a
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1;b>>=1
    return r
def xp1pow(N):  # (x+1)^N
    r=1;base=0b11
    while N:
        if N&1:r=pmul(r,base)
        base=pmul(base,base);N>>=1
    return r
def critE(l,m):
    lp,mp=odd(l),odd(m)
    if lp==1 or mp==1: return False
    N=lp*mp//math.gcd(lp,mp)
    P=xp1pow(N)^1
    return pgcd((1<<lp)|1,P).bit_length()>1 and pgcd((1<<mp)|1,P).bit_length()>1
if __name__=='__main__':
    for t in [(11,14),(12,13),(13,13),(6,30),(13,14),(4,48),(6,32),(8,24),(12,16)]:
        print(t,2*t[0]*t[1],critE(*t))
    # sanity vs data: every torus in data must pass
    import json
    D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
    tori={(e['l'],e['m']) for e in D['entries']}
    print('data tori failing critE:',[t for t in tori if not critE(*t)])
    import json as j
    R=[j.loads(x) for x in open('/home/user/lattice-lab/examples/qec-census-4/records.jsonl')]
    print('stage4 records mismatch critE:',[(r['l'],r['m']) for r in R if r['criterion_e']!=critE(r['l'],r['m'])])
