import json,collections
rows=json.load(open('rows.json'))
def primes(x):
    p=2; s=set()
    while p*p<=x:
        while x%p==0: s.add(p); x//=p
        p+=1
    if x>1: s.add(x)
    return s
tab=collections.Counter()
mono_fail=[]
for r in rows:
    g,L=eval(r['group'])
    both_even = g%2==0
    nadm=len(r['adm'])
    r1 = nadm==1 and all(g%p for p in primes(r['adm'][0]))
    tab[(('bothEven' if both_even else 'le1Even'), 'nadm=%d'%nadm, 'rank1' if r1 else ('rank2' if nadm==1 else '-'), 'SINGLE' if r['single'] else 'multi')]+=1
    kd={int(k):v for k,v in r['kd'].items()}
    ks=sorted(kd)
    if any(kd[ks[i]]<kd[ks[i+1]] for i in range(len(ks)-1)): mono_fail.append((r['group'],r['tori'],kd))
for k,v in sorted(tab.items()): print(k,v)
print('non-monotone groups',len(mono_fail))
for m in mono_fail: print(' ',m)
# multi-point groups: how many strictly top at min k
multi=[r for r in rows if not r['single']]
print('multi-point groups',len(multi))
# stage composition
print(collections.Counter(tuple(sorted(r['stages'])) for r in rows))
print(collections.Counter((tuple(sorted(r['stages'])), r['single']) for r in rows))
