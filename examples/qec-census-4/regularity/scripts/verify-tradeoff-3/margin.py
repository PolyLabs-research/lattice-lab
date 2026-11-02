import json
from collections import defaultdict
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
best=defaultdict(lambda: defaultdict(list))
for e in E: best[e['n']][e['k']].append(e)
risky=[]
for n in sorted(best):
    ks=sorted(best[n]); kmin=ks[0]
    dk={k:max(x['d'] for x in best[n][k]) for k in ks}
    st={k:all(x['settled'] for x in best[n][k] if x['d']==dk[k]) and all(x['settled'] for x in best[n][k]) for k in ks}
    others=[(dk[k],k,st[k]) for k in ks[1:]]
    if not others: 
        print(n,'only k',kmin, dk[kmin]); continue
    dmo=max(o[0] for o in others)
    gap=dk[kmin]-dmo
    stages=sorted(set(x['stage'] for k in ks for x in best[n][k]))
    unsettled=[(k,dk[k]) for k in ks if not st[k]]
    line=f"n={n} kmin={kmin} d={dk[kmin]} settled={st[kmin]} next-best={dmo} gap={gap} stages={stages} unsettled={unsettled} ks={[(k,dk[k]) for k in ks]}"
    if gap<=2 or unsettled: print(line)
# settled counts by stage
c=defaultdict(lambda:[0,0])
for e in E: c[e['stage']][e['settled']]+=1
print(dict(c))
print(sorted(set(e['n'] for e in E if e['stage']=='4')))
print(min(e['n'] for e in E), max(e['n'] for e in E))
print(sorted(set(e['k'] for e in E)))
