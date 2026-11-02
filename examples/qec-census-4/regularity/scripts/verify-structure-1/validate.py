import json,time
from kset import kset_odd, oddpart
rows=json.load(open('rows.json'))
ok=bad=0; t0=time.time(); cache={}
for r in rows:
    g,L=eval(r['group'])
    if g%2==0: continue
    key=(g,oddpart(L))
    if key not in cache: cache[key]=kset_odd(*key)
    mine=cache[key]; data=sorted(int(k) for k in r['kd'])
    if mine==data: ok+=1
    else: bad+=1; print('MISMATCH',r['group'],r['tori'],'data',data,'mine',mine)
print('le1-even groups: match',ok,'mismatch',bad,'time',round(time.time()-t0,1))
