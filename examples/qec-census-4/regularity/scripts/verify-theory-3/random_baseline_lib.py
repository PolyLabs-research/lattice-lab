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
