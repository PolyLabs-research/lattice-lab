import json, math
from collections import defaultdict
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
# per (n,k): best d over all tori with that n (frontier entries are per torus,k)
best=defaultdict(dict)  # n -> k -> (d, list of entries)
for e in E:
    n,k,d=e['n'],e['k'],e['d']
    cur=best[n].get(k)
    if cur is None or d>cur[0]:
        best[n][k]=(d,[e])
    elif d==cur[0]:
        cur[1].append(e)
ns=sorted(best)
print("number of distinct n:",len(ns))
viol=[];ties=[];summary=defaultdict(list)
for n in ns:
    ks=sorted(best[n])
    kmin=ks[0]
    dmax=max(best[n][k][0] for k in ks)
    dkmin=best[n][kmin][0]
    argmax=[k for k in ks if best[n][k][0]==dmax]
    if dkmin<dmax:
        viol.append((n,kmin,dkmin,argmax,dmax))
    if len(argmax)>1: ties.append((n,argmax,dmax))
    summary[kmin].append(n)
    settled_kmin=all(x['settled'] for x in best[n][kmin][1])
print("violations:",viol)
print("ties at max:",ties)
for k in sorted(summary):
    print("kmin",k,":",summary[k])
