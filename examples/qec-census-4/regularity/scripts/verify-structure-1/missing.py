import json
from math import gcd
from kset import oddpart
A=json.load(open('admissible.json')); exact=A['exact']
rows=json.load(open('rows.json')); have={tuple(eval(r['group'])) for r in rows}
allg={}
for l in range(2,201):
    for m in range(l,201):
        if l*m>200: break
        g=gcd(l,m); allg.setdefault((g,l*m//g),[]).append((l,m))
withcodes={k:v for k,v in allg.items() if any(oddpart(k[1])%t==0 for t in exact)}
print('groups lm<=200:',len(allg),'with admissible t:',len(withcodes),'in data:',len(have&set(withcodes)),'data not predicted:',have-set(withcodes))
miss=sorted(set(withcodes)-have,key=lambda k:k[0]*k[1])
print('missing (presumably stage-4 pending):',len(miss))
for k in miss: print(' ',k,'n=',2*k[0]*k[1],withcodes[k])
json.dump([list(k) for k in miss],open('missing.json','w'))
