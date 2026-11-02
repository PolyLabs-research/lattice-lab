import json, math, collections
SP='/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad'
D=json.load(open(SP+'/census-data.json'))
print(D.keys())
E=D['entries']; print(len(E))
print(collections.Counter((e['stage'],e['settled']) for e in E))
print({k:v for k,v in D.items() if k not in ('entries',)} if len(str(D.get('laws')))<3000 else str(D['laws'])[:3000])
