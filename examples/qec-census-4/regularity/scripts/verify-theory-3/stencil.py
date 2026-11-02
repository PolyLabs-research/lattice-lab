# Independent recomputation of the minimal 2D stencil diameter of a weight-6 BB code.
# Method (different from theory/rho2.py): enumerate lifted shapes {0,u,v} in Z^2 of l_inf diameter <= D,
# solve the linear system phi(u)=s1, phi(v)=s2 for phi=(g1,g2) in G^2 coordinatewise mod l and mod m,
# take the union of solution sets (as an OR of outer products = boolean matrix product), intersect A and B.
# Exact: no box-radius cutoff (all lifts automatically lie within distance D of the base point).
import numpy as np, math, json, sys
from functools import lru_cache

@lru_cache(None)
def shapes(D):
    pts=[(i,j) for i in range(-D,D+1) for j in range(-D,D+1)]
    S=[(u[0],u[1],v[0],v[1]) for u in pts for v in pts
       if u!=(0,0) and v!=(0,0) and u!=v and max(abs(u[0]-v[0]),abs(u[1]-v[1]))<=D]
    return np.array(S,dtype=np.int64)

def solset(S,q,s1,s2):
    # boolean (len(S), q*q): (g1,g2) in Z_q^2 with u.g = s1, v.g = s2 mod q
    g=np.arange(q); G1=np.repeat(g,q); G2=np.tile(g,q)
    a=(S[:,0:1]*G1[None]+S[:,1:2]*G2[None]-s1)%q==0
    b=(S[:,2:3]*G1[None]+S[:,3:4]*G2[None]-s2)%q==0
    return a&b

def phiset(S,l,m,s1,s2,chunk=3000):
    out=np.zeros((l*l,m*m),dtype=bool)
    for i in range(0,len(S),chunk):
        Sc=S[i:i+chunk]
        L=solset(Sc,l,s1[0],s2[0]).astype(np.float32)
        M=solset(Sc,m,s1[1],s2[1]).astype(np.float32)
        out|=(L.T@M)>0
    return out

def surj_mask(l,m):
    g=np.arange(l); a=np.repeat(g,l); b=np.tile(g,l)   # g1x, g2x
    h=np.arange(m); c=np.repeat(h,m); d=np.tile(h,m)   # g1y, g2y
    a=a[:,None]; b=b[:,None]; c=c[None,:]; d=d[None,:]
    gg=np.gcd.reduce([np.abs(a*d-b*c), l*c+0*a, a*m+0*c, l*d+0*b, b*m+0*d, np.full((l*l,m*m),l*m)])
    return gg==1

def steps(P,l,m):
    p0=P[0]
    return [((P[1][0]-p0[0])%l,(P[1][1]-p0[1])%m), ((P[2][0]-p0[0])%l,(P[2][1]-p0[1])%m)]

def connected(l,m,A,B):
    st=steps(A,l,m)+steps(B,l,m)
    seen={(0,0)}; fr=[(0,0)]
    while fr:
        x=fr.pop()
        for s in st:
            for sg in (1,-1):
                y=((x[0]+sg*s[0])%l,(x[1]+sg*s[1])%m)
                if y not in seen: seen.add(y); fr.append(y)
    return len(seen)==l*m

_SM={}
def min_diam(l,m,A,B,Dmax=8):
    if (l,m) not in _SM: _SM[(l,m)]=surj_mask(l,m)
    sa=steps(A,l,m); sb=steps(B,l,m)
    for D in range(1,Dmax+1):
        S=shapes(D)
        PA=phiset(S,l,m,sa[0],sa[1])
        if not PA.any(): continue
        PB=phiset(S,l,m,sb[0],sb[1])
        X=PA&PB
        if X.any():
            Xs=X&_SM[(l,m)]
            return D, bool(Xs.any())
    return None, None
