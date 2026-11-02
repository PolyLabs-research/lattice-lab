import json
from collections import defaultdict, Counter
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
best=defaultdict(dict); tori=defaultdict(set)
for e in E:
    best[e['n']][e['k']]=max(best[e['n']].get(e['k'],0),e['d']); tori[e['n']].add((e['l'],e['m']))
single=[n for n in best if len(best[n])==1]
multi=sorted(n for n in best if len(best[n])>1)
print("n with one k only:",len(single)); print("n with >=2 k:",len(multi))
gaps=Counter(); strict=0
for n in multi:
    ks=sorted(best[n]); g=best[n][ks[0]]-max(best[n][k] for k in ks[1:]); gaps[g]+=1
print("gap distribution (d_kmin - best other):",sorted(gaps.items()))
# stage 4 n's with tori listing
for n in sorted(best):
    if n>300: print(n, sorted(tori[n]), sorted(best[n].items()))
# Is d non-increasing in k at every n? (stronger statement)
nonmono=[]
for n in multi:
    ks=sorted(best[n]); ds=[best[n][k] for k in ks]
    for i in range(len(ks)-1):
        if ds[i+1]>ds[i]: nonmono.append((n,ks[i],ds[i],ks[i+1],ds[i+1]))
print("non-monotone adjacent pairs:",nonmono)
# by isomorphism class of group: g=gcd(l,m)
import math
grp=defaultdict(dict)
for e in E:
    g=math.gcd(e['l'],e['m']); key=(e['n'],g)
    grp[key][e['k']]=max(grp[key].get(e['k'],0),e['d'])
v=[]
for key,dd in grp.items():
    ks=sorted(dd)
    if dd[ks[0]]<max(dd.values()): v.append((key,sorted(dd.items())))
print("per-group (n,gcd) violations:",v)
print("groups total",len(grp),"multi-k groups",sum(1 for dd in grp.values() if len(dd)>1))
