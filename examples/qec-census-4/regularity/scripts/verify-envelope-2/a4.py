import numpy as np
from base2 import *
TH=thresholds()
def table(th,label):
    x=np.array([(a+b)/2 for d,a,b in th]); y=np.array([d for d,a,b in th],float)
    A={m:aicc(fit(m,x,y)[1],len(x),len(MODELS[m][1])) for m in KEYS}
    b=min(A.values())
    print(f'{label:34s} m={len(x):2d} '+'  '.join(f'{m.split()[0][:14]}:{A[m]-b:5.2f}' for m in KEYS), ' winner:',min(A,key=A.get))
print('dAICc by start (dmin) and data range; columns:',KEYS)
for nmax in (300,10**9):
    for dmin in (6,8,10,12,14,16):
        th=[t for t in TH if t[0]>=dmin and t[2]<=nmax]
        table(th,f'd>={dmin} (n_x>={[ (a+b)/2 for d,a,b in th][0]}) nmax={nmax if nmax<1e6 else 384}')
print('\nLeave-one-threshold-out, d>=6 all data: dAICc of A sqrt(n)+B vs best')
th=[t for t in TH if t[0]>=6]
for i in range(len(th)):
    t2=th[:i]+th[i+1:]
    x=np.array([(a+b)/2 for d,a,b in t2]); y=np.array([d for d,a,b in t2],float)
    A={m:aicc(fit(m,x,y)[1],len(x),len(MODELS[m][1])) for m in KEYS}
    print(f'  drop d={th[i][0]:2d}: dAICc(A sqrt n+B)={A["A sqrt(n)+B"]-min(A.values()):5.2f}  dAICc(sqrt(n ln n))={A["sqrt(n ln n)"]-min(A.values()):5.2f}')
