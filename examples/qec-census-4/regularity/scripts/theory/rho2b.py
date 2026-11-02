import json, collections, random, math
import numpy as np
exec(open('rho2.py').read().split("byn=collections")[0])  # reuse rho2()
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=[e for e in D['entries'] if e['A'] is not None]
byn=collections.defaultdict(list)
for e in E: byn[e['n']].append(e)
random.seed(1)
def gens_ok(l,m,steps):
    # check steps generate Z_l x Z_m via BFS closure
    seen={(0,0)}; fr=[(0,0)]
    while fr:
        a=fr.pop()
        for s in steps:
            for sg in (1,-1):
                b=((a[0]+sg*s[0])%l,(a[1]+sg*s[1])%m)
                if b not in seen: seen.add(b); fr.append(b)
    return len(seen)==l*m
def rand_code(l,m):
    while True:
        els=[(a,b) for a in range(l) for b in range(m)]
        A=random.sample(els,3); B=random.sample(els,3)
        st=[((A[i][0]-A[0][0])%l,(A[i][1]-A[0][1])%m) for i in (1,2)]+[((B[i][0]-B[0][0])%l,(B[i][1]-B[0][1])%m) for i in (1,2)]
        if gens_ok(l,m,st): return A,B
for n in [270,276,288,300,306,324,354,360,384]:
    if n not in byn: continue
    mx=max(byn[n],key=lambda e:(e['d'],-e['k']))
    r,_=rho2(mx['l'],mx['m'],mx['A'],mx['B'])
    rs=[rho2(mx['l'],mx['m'],*rand_code(mx['l'],mx['m']))[0] for _ in range(6)]
    print(n,mx['d'],mx['k'],f"{mx['l']}x{mx['m']}",'best',r,'random',rs,'N^(1/4)=%.2f'%((n/2)**.25),flush=True)
for (l,m) in [(3,11),(3,20),(7,7),(2,45)]:
    rs=[rho2(l,m,*rand_code(l,m))[0] for _ in range(6)]
    print('random',l,m,rs,'N^(1/4)=%.2f'%((l*m)**.25),flush=True)
