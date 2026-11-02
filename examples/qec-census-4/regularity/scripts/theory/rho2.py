# Effective 2D stencil "diameter" of a BB code: min over homomorphisms phi: Z^2 -> G=Z_l x Z_m
# of max over A,B of the l_inf diameter of the embedded 3-point support {0,p1,p2}.
# phi(e1)=g1, phi(e2)=g2. Code is a quotient of a 2D-local TI code with this stencil.
import json, math, collections, itertools, sys
import numpy as np
D=json.load(open('/tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/census-data.json'))
E=D['entries']
R=7
V=np.array([(i,j) for i in range(-R,R+1) for j in range(-R,R+1)])
Vinf=np.abs(V).max(1)
def diam(ps):
    # ps: list of arrays of candidate preimages for s1 (P1) and s2 (P2); returns min max(|p1|,|p2|,|p1-p2|)
    P1,P2=ps
    if len(P1)==0 or len(P2)==0: return 99
    a=np.abs(P1).max(1)[:,None]; b=np.abs(P2).max(1)[None,:]
    c=np.abs(P1[:,None,:]-P2[None,:,:]).max(2)
    return int(np.maximum(np.maximum(a,b),c).min())
def rho2(l,m,A,B):
    N=l*m
    def red(p): return ((p[0]%l),(p[1]%m))
    def steps(P):
        p0=P[0]; return [red((P[1][0]-p0[0],P[1][1]-p0[1])), red((P[2][0]-p0[0],P[2][1]-p0[1]))]
    SA=steps(A); SB=steps(B)
    best=99; arg=None
    els=[(a,b) for a in range(l) for b in range(m)]
    for g1 in els:
        for g2 in els:
            img0=(V[:,0]*g1[0]+V[:,1]*g2[0])%l
            img1=(V[:,0]*g1[1]+V[:,1]*g2[1])%m
            code=img0*m+img1
            def pre(s): return V[code==s[0]*m+s[1]]
            dA=diam([pre(SA[0]),pre(SA[1])])
            if dA>=best: continue
            dB=diam([pre(SB[0]),pre(SB[1])])
            r=max(dA,dB)
            if r<best: best=r; arg=(g1,g2)
    return best,arg
byn=collections.defaultdict(list)
for e in E: byn[e['n']].append(e)
out=[]
for n in sorted(byn):
    mx=max(byn[n],key=lambda e:(e['d'],-e['k']))
    r,arg=rho2(mx['l'],mx['m'],mx['A'],mx['B'])
    out.append((n,mx['d'],mx['k'],f"{mx['l']}x{mx['m']}",r))
    print(n,mx['d'],mx['k'],f"{mx['l']}x{mx['m']}",'rho2_inf_diam=',r,arg,mx['A'],mx['B'],flush=True)
json.dump(out,open('rho2_out.json','w'))
