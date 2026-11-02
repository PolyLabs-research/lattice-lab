import json, math, collections
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
print('n range', min(e['n'] for e in E), max(e['n'] for e in E))
print('stages', collections.Counter(e['stage'] for e in E))
print('unsettled', [(e['l'],e['m'],e['n'],e['k'],e['d'],e['stage']) for e in E if not e['settled']])
byn=collections.defaultdict(list)
for e in E: byn[e['n']].append(e)
ns=sorted(byn)
print('n with codes:', ns)
print('non-multiples of 6:', [n for n in ns if n%6])
print('multiples of 6 in [12,384] missing:', [n for n in range(12,385,6) if n not in byn])
for n in ns:
    s=[e for e in byn[n] if e['settled']]
    dm=max(e['d'] for e in s) if s else None
    dl=max(e['d'] for e in byn[n])
    grps=set((math.gcd(e['l'],e['m']), e['l']*e['m']//math.gcd(e['l'],e['m'])) for e in byn[n])
    tori=set((e['l'],e['m']) for e in byn[n])
    print(n, 'Esettled',dm,'Eall',dl, 'tori',len(tori),'groups',len(grps), 'stage', set(e['stage'] for e in byn[n]))
