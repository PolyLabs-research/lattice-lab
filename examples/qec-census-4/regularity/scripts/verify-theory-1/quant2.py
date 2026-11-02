import json, collections, numpy as np
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
F=collections.defaultdict(int)
for e in D['entries']: F[e['n']]=max(F[e['n']],e['d'])
ns=np.array(sorted(F)); R=np.maximum.accumulate(np.array([F[x] for x in ns]))
s=ns>=48; n=ns[s].astype(float); Rn=R[s]
def mm(f):
    p=2*np.floor(f/2); bad=p!=Rn; return int(bad.sum()), [(int(a),int(b),int(c)) for a,b,c in zip(n[bad],Rn[bad],p[bad])]
def best_c(g, lo, hi):
    cs=np.exp(np.linspace(np.log(lo),np.log(hi),20001)); r=[(mm(c*g)[0],c) for c in cs]; m=min(x[0] for x in r)
    c=[x[1] for x in r if x[0]==m]; c=c[len(c)//2]; return m,c,mm(c*g)[1]
print('sqrt(n ln n):',best_c(np.sqrt(n*np.log(n)),0.5,0.7))
for b in [0.600,0.607,0.61,0.6225,0.63,0.635,0.64,0.6413]:
    print('n^%.4f:'%b,best_c(n**b,0.3,1.5))
# envelope with c fixed so curve is an upper staircase (never below R): smallest c s.t. 2floor(f/2)>=R everywhere
for name,g in [('sqrt(n ln n)',np.sqrt(n*np.log(n))),('n^0.6225',n**0.6225),('n^0.641',n**0.6413),('n^0.607',n**0.607)]:
    c=np.max(Rn/g); print(name,'tightest upper envelope c=%.4f'%c, 'overshoot count',mm(c*g*(1+1e-9))[0])
