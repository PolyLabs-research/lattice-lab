import sys; sys.path.insert(0,'tools')
from tori import S_VOT13
from collections import Counter
lam=Counter(); mu=Counter()
for d1,d2 in S_VOT13:
    lam[-d1]+=1
    if (d1-d2)%2: mu[-d1]+=1
print({k:v%2 for k,v in sorted(lam.items()) if v%2})
print({k:v%2 for k,v in sorted(mu.items()) if v%2})
# fibers on Z/4xZ/2 and Z/8xZ/4
for M in (2,4):
    c=Counter(((d1-d2)%(2*M), d2%M) for d1,d2 in S_VOT13)
    print(M,{k:v%2 for k,v in c.items() if v%2})
