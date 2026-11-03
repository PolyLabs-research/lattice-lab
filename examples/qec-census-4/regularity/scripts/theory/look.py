import json, math, collections
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
def grp(l,m):
    # invariant factors of Z_l x Z_m
    g=math.gcd(l,m); return (g, l*m//g)
best=collections.defaultdict(lambda:None)
for e in E:
    key=(e['n'],grp(e['l'],e['m']))
    if best[key] is None or e['d']>best[key]['d']: best[key]=e
# max d at each n
byn=collections.defaultdict(list)
for e in E: byn[e['n']].append(e)
print("n, maxd, d/sqrt n, d/sqrt(n ln n), #groups at n, k of best, torus, stage")
for n in sorted(byn):
    es=byn[n]; mx=max(es,key=lambda e:e['d'])
    groups={grp(e['l'],e['m']) for e in es}
    print(n, mx['d'], round(mx['d']/n**.5,3), round(mx['d']/math.sqrt(n*math.log(n)),3), len(groups), mx['k'], f"{mx['l']}x{mx['m']}", mx['stage'], mx['settled'])
