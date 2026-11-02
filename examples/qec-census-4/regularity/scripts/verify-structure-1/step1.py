import json,collections
from math import gcd
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
bytorus=collections.defaultdict(dict)
meta={}
for e in E:
    bytorus[(e['l'],e['m'])][e['k']]=(e['d'],e['stage'],e['settled'])
def gkey(l,m):
    g=gcd(l,m); return (g, l*m//g)
groups=collections.defaultdict(list)
for t in bytorus: groups[gkey(*t)].append(t)
# consistency across isomorphic tori
incons=0
for g,ts in groups.items():
    sets=[{k:v[0] for k,v in bytorus[t].items()} for t in ts]
    if any(s!=sets[0] for s in sets):
        incons+=1; print('INCONSISTENT',g,ts,sets)
print('inconsistent groups',incons)
# group frontier: k -> max d
res={}
for g,ts in groups.items():
    kd=collections.defaultdict(int); st=set(); sett=True
    for t in ts:
        for k,(d,s,se) in bytorus[t].items():
            kd[k]=max(kd[k],d); st.add(s); sett&=se
    res[g]=(dict(sorted(kd.items())),st,sett,ts)
json.dump({str(k):[v[0],sorted(v[1]),v[2],v[3]] for k,v in res.items()},open('groups_mine.json','w'))
# claim a: top of column = smallest-k entry
strict=weak=0; fails=[]
for g,(kd,st,se,ts) in res.items():
    kmin=min(kd); dmax=max(kd.values())
    if kd[kmin]==dmax:
        weak+=1
        if sum(1 for k in kd if kd[k]==dmax)==1: strict+=1
    else: fails.append((g,kd))
print('groups',len(res),'smallest-k attains max d:',weak,'uniquely:',strict)
for f in fails: print('FAIL',f)
# ties
ties=[(g,kd) for g,(kd,st,se,ts) in res.items() if sum(1 for k in kd if kd[k]==max(kd.values()))>1]
print('ties at top',len(ties))
for t in ties: print(' ',t)
single=[g for g,(kd,*_) in res.items() if len(kd)==1]
print('single-point groups',len(single))
