import json, numpy as np
from scipy.optimize import least_squares
D=json.load(open('../../census-data.json'))['entries']
E={}
for e in D:
    if e['settled']: E[e['n']]=max(E.get(e['n'],0),e['d'])
ns=sorted(E); R=[];run=0
for n in ns: run=max(run,E[n]); R.append(run)
th=[]
for d in range(6,30,2):
    i=next(j for j,n in enumerate(ns) if E[n]>=d)
    th.append((d,ns[i-1],ns[i]))
print(th)
def fit(f,p0,nmin):
    T=[(d,(a+b)/2) for d,a,b in th if b>=nmin]
    dd=np.array([t[0] for t in T]); nn=np.array([t[1] for t in T])
    r=least_squares(lambda p:f(nn,p)-dd,p0); return r.x, np.sqrt(np.mean(r.fun**2))
M={
 'c*sqrt(n ln n)':(lambda n,p:p[0]*np.sqrt(n*np.log(n)),[0.6]),
 'a*n^b':(lambda n,p:p[0]*n**p[1],[0.8,0.6]),
 'A*sqrt(n)+B':(lambda n,p:p[0]*np.sqrt(n)+p[1],[1.6,-3]),
 'c*sqrt(n)':(lambda n,p:p[0]*np.sqrt(n),[1.4]),
}
grid=np.arange(390,2001,6)
for nmin in (30,100):
  print('--- fit start n>=',nmin,'(all thresholds to d=28)')
  for k,(f,p0) in M.items():
    p,rms=fit(f,p0,nmin)
    first={}
    for d in range(30,52,2):
        hit=[n for n in grid if f(n,p)>=d]; first[d]=hit[0] if hit else None
    vals={n:round(float(f(n,p)),2) for n in (396,450,504,600,702,804,1002)}
    print(k,np.round(p,4),'rms',round(rms,3),'first n (mult of 6) for d:',first, vals)
