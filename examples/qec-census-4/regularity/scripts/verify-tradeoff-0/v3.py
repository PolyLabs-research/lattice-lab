# Which groups Z_g x Z_L (n = 2gL) should carry k>0 codes (criterion E), vs which appear in the data
import json, math, collections
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
E=json.load(open(SP+'/census-data.json'))['entries']
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def pmod(a,b):
    db=b.bit_length()
    while a.bit_length()>=db: a^=b<<(a.bit_length()-db)
    return a
def pgcd(a,b):
    while b: a,b=b,pmod(a,b)
    return a
def ppow(a,e):
    r=1
    while e:
        if e&1: r=pmul(r,a)
        a=pmul(a,a); e>>=1
    return r
def odd(x):
    while x%2==0: x//=2
    return x
def critE(l,m):
    lo,mo=odd(l),odd(m)
    if lo==1 or mo==1: return False
    Nn=lo*mo//math.gcd(lo,mo)
    Q=ppow(0b11,Nn)^1
    ok=lambda q: pgcd((1<<q)|1,Q).bit_length()>1
    return ok(lo) and ok(mo)
present=collections.defaultdict(set)
for e in E: present[(math.gcd(e['l'],e['m']),e['l']*e['m']//math.gcd(e['l'],e['m']))].add(e['stage'])
groups={}
for l in range(2,201):
    for m in range(l,201):
        n=2*l*m
        if n>400: continue
        g=(math.gcd(l,m),l*m//math.gcd(l,m))
        groups.setdefault(g,[]).append((l,m))
# check criterion vs data for n<=300
mis=[]
for g,tl in groups.items():
    n=2*g[0]*g[1]; c=critE(*tl[0])
    if n<=300 and c!=(g in present): mis.append((g,n,c,g in present))
print('n<=300 groups where criterion disagrees with data presence:',mis)
miss=[(2*g[0]*g[1],g,tl) for g,tl in groups.items() if 300<2*g[0]*g[1]<=400 and critE(*tl[0]) and g not in present]
have=[(2*g[0]*g[1],g) for g in present if 2*g[0]*g[1]>300]
print('stage-4 groups present:',len(have)); print('criterion-E groups with 302<=n<=400 MISSING from data:',len(miss))
for n,g,tl in sorted(miss): print('  n=%d group Z%d x Z%d  tori %s'%(n,g[0],g[1],tl))
