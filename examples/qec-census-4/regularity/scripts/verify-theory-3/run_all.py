import json, time, math
from stencil import min_diam, connected
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=[e for e in D['entries'] if e['A'] is not None]
out=[]
t=time.time()
for i,e in enumerate(E):
    l,m=e['l'],e['m']
    A=[tuple(p) for p in e['A']]; B=[tuple(p) for p in e['B']]
    con=connected(l,m,A,B)
    dd,sj=min_diam(l,m,A,B)
    r=dict(l=l,m=m,n=e['n'],k=e['k'],d=e['d'],stage=e['stage'],settled=e['settled'],score=e['score'],D=dd,surj=sj,conn=con,g=math.gcd(l,m))
    out.append(r)
    if i%25==0: print(i,len(E),round(time.time()-t,1),r,flush=True)
json.dump(out,open('all_D.json','w'))
print('done',time.time()-t)
