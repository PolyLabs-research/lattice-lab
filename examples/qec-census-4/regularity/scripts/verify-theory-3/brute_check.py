# brute-force cross-check of stencil.min_diam on small tori
import random, itertools
from stencil import min_diam, connected, steps
def brute(l,m,A,B,Dmax=6):
    sa=steps(A,l,m); sb=steps(B,l,m)
    best=99
    for g1 in itertools.product(range(l),range(m)):
        for g2 in itertools.product(range(l),range(m)):
            # map of box
            pre={}
            R=Dmax
            for i in range(-R,R+1):
                for j in range(-R,R+1):
                    e=((i*g1[0]+j*g2[0])%l,(i*g1[1]+j*g2[1])%m)
                    pre.setdefault(e,[]).append((i,j))
            def dm(s):
                b=99
                for u in pre.get(s[0],[]):
                    for v in pre.get(s[1],[]):
                        b=min(b,max(abs(u[0]),abs(u[1]),abs(v[0]),abs(v[1]),abs(u[0]-v[0]),abs(u[1]-v[1])))
                return b
            r=max(dm(sa),dm(sb))
            best=min(best,r)
    return best
random.seed(7)
bad=0
for trial in range(40):
    l=random.choice([2,3,4,5,6]); m=random.choice([3,4,5,6,7,8])
    els=[(a,b) for a in range(l) for b in range(m)]
    while True:
        A=random.sample(els,3); B=random.sample(els,3)
        if connected(l,m,A,B): break
    d1,_=min_diam(l,m,A,B); d2=brute(l,m,A,B)
    if d1!=d2: bad+=1; print('MISMATCH',l,m,A,B,d1,d2)
print('trials 40, mismatches',bad)
