import json, math, collections
import numpy as np
from scipy.optimize import curve_fit
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
byn=collections.defaultdict(int)
for e in D['entries']: byn[e['n']]=max(byn[e['n']],e['d'])
# frontier = running envelope: first n at which each d is reached (upper staircase)
ns=np.array(sorted(byn)); ds=np.array([byn[n] for n in ns],float)
sel=ns>=48
# use upper envelope points: n where d_max(n) >= all d_max at smaller n (record points)
rec=[(n,d) for i,(n,d) in enumerate(zip(ns,ds)) if d>=ds[:i].max(initial=0) and n>=48]
rn=np.array([r[0] for r in rec],float); rd=np.array([r[1] for r in rec])
forms={
 'c*sqrt(n)':lambda n,c:c*np.sqrt(n),
 'c*sqrt(n ln n)':lambda n,c:c*np.sqrt(n*np.log(n)),
 'c*n^b':lambda n,c,b:c*n**b,
 'c*n^(2/3)':lambda n,c:c*n**(2/3),
 'c*n^(3/4)':lambda n,c:c*n**0.75,
 'sqrt(n)*(a+b ln n)':lambda n,a,b:np.sqrt(n)*(a+b*np.log(n)),
}
print("record points (n,d):",list(zip(rn.astype(int),rd.astype(int))))
fits={}
for name,f in forms.items():
    p0=[1.0] if f.__code__.co_argcount==2 else [1.0,0.6]
    p,_=curve_fit(f,rn,rd,p0=p0)
    res=rd-f(rn,*p); fits[name]=(f,p)
    print(f"{name:22s} params={np.round(p,4)} rms={np.sqrt(np.mean(res**2)):.3f} maxabs={np.abs(res).max():.2f} pred@1000={f(1000,*p):.1f} @10^4={f(1e4,*p):.1f}")
f1,p1=fits['c*sqrt(n ln n)']; f2,p2=fits['c*n^b']
for N in [400,1000,2000,5000,1e4,1e5]:
    print(N, 'sqrt(n ln n) fit %.1f   n^b fit %.1f  diff %.1f'%(f1(N,*p1),f2(N,*p2),f2(N,*p2)-f1(N,*p1)))
# ratio flatness over [50,400]
nn=np.linspace(50,400,200); r=np.sqrt(nn*np.log(nn))/nn**0.607
print("sqrt(n ln n)/n^0.607 over [50,400]: min %.4f max %.4f (rel spread %.2f%%)"%(r.min(),r.max(),100*(r.max()/r.min()-1)))
