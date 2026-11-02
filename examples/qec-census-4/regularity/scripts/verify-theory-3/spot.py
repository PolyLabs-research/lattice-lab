# spot-check selected achievers: brute-force D over all phi (vectorised over g2), and GF(2) k
import json, itertools, numpy as np
from random_baseline_lib import kval
rows=[json.loads(l) for l in open('jobs_out.jsonl')]
def brute(l,m,A,B,R=5):
    st=lambda P:[((P[i][0]-P[0][0])%l,(P[i][1]-P[0][1])%m) for i in (1,2)]
    sa,sb=st(A),st(B)
    V=np.array([(i,j) for i in range(-R,R+1) for j in range(-R,R+1)]); Vn=np.abs(V).max(1)
    best=99
    for g1 in itertools.product(range(l),range(m)):
        for g2 in itertools.product(range(l),range(m)):
            code=((V[:,0]*g1[0]+V[:,1]*g2[0])%l)*m+(V[:,1]*g2[1]+V[:,0]*g1[1])%m
            def dm(s):
                P=V[code==s[0][0]*m+s[0][1]]; Q=V[code==s[1][0]*m+s[1][1]]
                if len(P)==0 or len(Q)==0: return 99
                return int(np.maximum(np.maximum(np.abs(P).max(1)[:,None],np.abs(Q).max(1)[None,:]),np.abs(P[:,None]-Q[None]).max(2)).min())
            a=dm(sa)
            if a>=best: continue
            r=max(a,dm(sb)); best=min(best,r)
    return best
picks=[]
for n,want in [(308,2),(258,4),(384,3),(354,3),(372,3)]:
    c=[r for r in rows if r[0]=='ach' and r[3]==n and r[8]==want]
    picks.append(c[0])
for r in picks:
    kind,l,m,n,k,d,A,B,D=r
    print(n,l,m,'k',k,'d',d,'D(stencil.py)',D,'D(brute)',brute(l,m,A,B),'k(gf2)',kval(l,m,A,B),A,B,flush=True)
