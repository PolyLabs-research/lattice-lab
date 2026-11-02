import json, math, collections
R=[json.loads(l) for l in open('/home/user/lattice-lab/examples/qec-census-4/records.jsonl')]
done={(r['l'],r['m']):r for r in R if 'l' in r}
print('records',len(R),'tori',len(done))
every=sorted((l,m) for l in range(2,15) for m in range(l,101) if 150<l*m<=200)
print('all tori',len(every))
grp=lambda l,m:(math.gcd(l,m),l*m//math.gcd(l,m))
ce={t:r['criterion_e'] for t,r in done.items()}
print('done w/ criterion E true:',sum(ce.values()))
rem=[t for t in every if t not in done]
# criterion E: exists e>1 dividing exponent of odd part with a in mu_e, a!=1, 1+a in mu_e -> e divisible by 3? (1+a root of unity with a root of unity: a = primitive cube root ... 1+w = -w^2 is a 6th root; in mu_e needs e with -w^2 in mu_e: e odd -> -w^2 order 6? )
# Determine empirically which remaining tori share group with done tori
G_done={grp(*t):ce[t] for t in done}
for t in rem:
    g=grp(*t); print('remaining',t,'n',2*t[0]*t[1],'group',g,'iso to done:',G_done.get(g,'?'))
from critE import critE
mism=[t for t in done if critE(*t)!=ce[t]]
print('critE mismatches on done stage-4 tori:',mism)
print('REMAINING tori with codes (critE true):')
inc=collections.defaultdict(list)
for t in rem:
    if critE(*t):
        g=grp(*t); isodone=g in G_done
        print('  ',t,'n',2*t[0]*t[1],'group',g,'iso-to-done' if isodone else 'NEW GROUP')
        if not isodone: inc[2*t[0]*t[1]].append(t)
print('n values whose frontier is incomplete:',dict(inc))
json.dump({str(k):v for k,v in inc.items()},open('incomplete_n.json','w'))
