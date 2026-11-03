import json, random, sys, time, collections
import numpy as np
from stencil import min_diam, connected
def gf2rank(M):
    M=M.copy()%2; r=0; rows,cols=M.shape
    for c in range(cols):
        piv=np.nonzero(M[r:,c])[0]
        if len(piv)==0: continue
        p=r+piv[0]
        if p!=r: M[[r,p]]=M[[p,r]]
        nz=np.nonzero(M[:,c])[0]; nz=nz[nz!=r]
        M[nz]^=M[r]
        r+=1
        if r==rows: break
    return r
def circ(l,m,P):
    N=l*m; M=np.zeros((N,N),dtype=np.uint8)
    for i in range(l):
        for j in range(m):
            row=i*m+j
            for (a,b) in P:
                M[row,((i+a)%l)*m+(j+b)%m]^=1
    return M
def kval(l,m,A,B):
    H=np.concatenate([circ(l,m,A),circ(l,m,B)],axis=1)
    return 2*l*m-2*gf2rank(H)
tori=[tuple(map(int,t.split('x'))) for t in sys.argv[1].split(',')]
R=int(sys.argv[2]); seed=int(sys.argv[3])
random.seed(seed)
res={}
for (l,m) in tori:
    els=[(a,b) for a in range(l) for b in range(m)]
    rows=[]
    t=time.time()
    while len(rows)<R:
        A=random.sample(els,3); B=random.sample(els,3)
        if not connected(l,m,A,B): continue
        k=kval(l,m,A,B)
        D,_=min_diam(l,m,A,B)
        rows.append((k,D))
    res[f'{l}x{m}']=rows
    c=collections.Counter(D for k,D in rows); ck=collections.Counter(D for k,D in rows if k>0)
    print(l,m,'N',l*m,'all',dict(sorted(c.items())),'k>0',dict(sorted(ck.items())),'n_k>0',sum(1 for k,D in rows if k>0),round(time.time()-t,1),flush=True)
json.dump(res,open(f'rand_{seed}.json','w'))
