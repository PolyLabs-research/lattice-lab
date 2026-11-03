import json, math, collections
P='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'
D=json.load(open(P))
E=D['entries']
print(len(E), D.keys())
print(collections.Counter(e['stage'] for e in E))
print('settled', collections.Counter((e['stage'],e['settled']) for e in E))
print('k parity', collections.Counter(e['k']%2 for e in E), 'd parity', collections.Counter(e['d']%2 for e in E))
print('n range', min(e['n'] for e in E), max(e['n'] for e in E))
print('l<=m?', collections.Counter(e['l']<=e['m'] for e in E), 'l=1?', sum(e['l']==1 or e['m']==1 for e in E))
# group by invariant factors
def inv(l,m):
    g=math.gcd(l,m); return (g, l*m//g)
G=collections.defaultdict(lambda: collections.defaultdict(list))
for e in E:
    G[inv(e['l'],e['m'])][e['k']].append(e)
incons=[]
for g,kd in G.items():
    for k,lst in kd.items():
        ds=set(x['d'] for x in lst)
        if len(ds)>1: incons.append((g,k,[(x['l'],x['m'],x['d'],x['stage'],x['settled']) for x in lst]))
print('isomorphic-torus groups:',len(G),' tori:',len(set((e['l'],e['m']) for e in E)))
print('inconsistent (group,k) across isomorphic tori:',len(incons))
for x in incons: print('  ',x)
# multiplicity of tori per group
mult=collections.Counter(len(set((x['l'],x['m']) for lst in kd.values() for x in lst)) for kd in G.values())
print('tori per group', mult)
