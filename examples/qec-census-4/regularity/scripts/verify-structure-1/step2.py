import json,collections
from math import gcd
G=json.load(open('groups_mine.json'))
A=json.load(open('admissible.json'))
exact=[t for t in A['exact'] if t<=400]
def odd(x):
    while x%2==0: x//=2
    return x
def ordmod(t):
    r=1; v=2%t
    while v!=1: v=v*2%t; r+=1
    return r
def primes(x):
    p=2; s=set()
    while p*p<=x:
        while x%p==0: s.add(p); x//=p
        p+=1
    if x>1: s.add(x)
    return s
rows=[]
okb=okb2=0; badb=[]
okc=0; badc=[]
for key,(kd,stages,sett,tori) in G.items():
    g,L=eval(key)
    kd={int(k):v for k,v in kd.items()}
    Eodd=odd(L)  # exponent of odd part = odd part of lcm
    adm=[t for t in exact if Eodd%t==0]
    kmin=min(kd)
    pred_smallest_t = 2*ordmod(min(adm)) if adm else None
    pred_min_ord = 2*min(ordmod(t) for t in adm) if adm else None
    if kmin==pred_smallest_t: okb+=1
    else: badb.append((key,tori,kd,adm,pred_smallest_t))
    if kmin==pred_min_ord: okb2+=1
    even_sides_le1 = (g%2==1)
    if len(adm)==1:
        t=adm[0]; rank1=all(g%p!=0 for p in primes(t))
    else: rank1=False
    pred_single = even_sides_le1 and len(adm)==1 and rank1
    single = len(kd)==1
    if pred_single==single: okc+=1
    else: badc.append((key,tori,kd,adm,even_sides_le1,rank1,sorted(stages)))
    rows.append(dict(group=key,n=2*g*L,tori=tori,kd=kd,adm=adm,kmin=kmin,pred=pred_smallest_t,single=single,pred_single=pred_single,stages=stages))
print('groups',len(G))
print('(b) kmin == 2 ord_t(2), t = smallest admissible:',okb,' ; == 2 min ord:',okb2)
for b in badb: print('  B-FAIL',b)
print('kmin distribution', collections.Counter(r['kmin'] for r in rows))
print('smallest t distribution', collections.Counter(min(r['adm']) for r in rows))
print('(c) single-point iff condition:',okc)
for b in badc: print('  C-FAIL',b)
print('single count',sum(r['single'] for r in rows),'pred single',sum(r['pred_single'] for r in rows))
json.dump(rows,open('rows.json','w'),default=list)
