import json, math, collections
import numpy as np
D=json.load(open('../../census-data.json')); E=D['entries']
n=np.arange(12,401)
a=0.6175*np.sqrt(n*np.log(n)); b=0.8346*n**0.6; c=0.772*n**0.615
print('max |sqrt(n ln n) curve - 0.8346 n^0.6| over 12..400: %.3f (in d units); rel %.2f%%'%(np.abs(a-b).max(), 100*np.abs(a/b-1).max()))
print('max |sqrt(n ln n) - 0.772 n^0.615|: %.3f'%np.abs(a-c).max())
for N in (1000,10000):
    print(N, 'sqrt(n ln n):%.1f  0.8346n^0.6:%.1f  0.772n^0.615:%.1f'%(0.6175*math.sqrt(N*math.log(N)),0.8346*N**0.6,0.772*N**0.615))
# local exponent of sqrt(n ln n)
for N in (30,100,300,400): print('local exponent at',N, round(0.5+1/(2*math.log(N)),3))
# groups per comb column vs residual
top={}
for e in E:
    if e['n'] not in top or e['d']>top[e['n']]: top[e['n']]=e['d']
grp=collections.defaultdict(set)
for e in E:
    g=math.gcd(e['l'],e['m']); grp[e['n']].add((g,e['l']*e['m']//g))
rows=[]
for N in sorted(top):
    if N%6: continue
    raw=0.6175*math.sqrt(N*math.log(N)); rows.append((N,len(grp[N]),top[N]-raw))
r=np.array(rows)
print('corr(#groups with entries, top - raw curve) on comb:',np.corrcoef(r[:,1],r[:,2])[0,1].round(3))
for x in rows:
    if x[0] in (138,144,306,312,336,360,384): print('  n=%d groups=%d resid=%+.2f'%x)
