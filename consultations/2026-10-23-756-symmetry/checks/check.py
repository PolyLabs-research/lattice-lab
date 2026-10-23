import sys
sys.path.insert(0,'/home/user/lattice-lab/examples/qec-bb'); sys.path.insert(0,'/home/user/lattice-lab/examples/qec-distance')
import distance as D
L,M=21,18; A=[(3,0),(0,10),(0,17)]; B=[(0,5),(3,0),(19,0)]
lm=L*M; n=2*lm
hx,hz=D._bit_rows(A,B,L,M)
# Tanner graph: vertices 0..n-1 qubits, n..n+lm-1 X checks, n+lm.. Z checks
adj=[[] for _ in range(n+2*lm)]
for r,row in enumerate(hx):
    for t in range(n):
        if row>>t&1: adj[t].append(n+r); adj[n+r].append(t)
for r,row in enumerate(hz):
    for t in range(n):
        if row>>t&1: adj[t].append(n+lm+r); adj[n+lm+r].append(t)
def refine(col):
    while True:
        sig=[(col[v],tuple(sorted(col[u] for u in adj[v]))) for v in range(len(adj))]
        ids={s:i for i,s in enumerate(sorted(set(sig)))}
        new=[ids[s] for s in sig]
        if len(set(new))==len(set(col)): return new
        col=new
base=[0]*n+[1]*lm+[2]*lm
c0=refine(base); print('cells without individualizing:',len(set(c0)))
ind=list(base); ind[0]=3
c=refine(ind); print('cells after individualizing qubit 0:',len(set(c)),'of',len(adj))
# 1b: orbit of qubit 0 is at most the cell of qubit 0 under unindividualized refinement
print('qubits in qubit 0 cell (unindividualized):', sum(1 for v in range(n) if c0[v]==c0[0]))
# BZ information-set ranks: greedy disjoint information sets of ker H_X (Z-logical code)
ker=D._kernel_bits(hx,n); K=len(ker); print('dim ker H_X', K)
cols_left=list(range(n)); ranks=[]
import random
def rank_cols(cols):
    # rank of the generator matrix restricted to columns cols
    rows=[sum(((v>>c)&1)<<i for i,c in enumerate(cols)) for v in ker]
    piv={}
    for r in rows:
        while r:
            p=r.bit_length()-1
            if p not in piv: piv[p]=r; break
            r^=piv[p]
    return len(piv)
used=set(); rem=list(range(n))
while False:
    # greedily choose an information set (max rank subset) from remaining columns
    chosen=[]; piv={}
    for c in rem:
        v=sum(((x>>c)&1)<<i for i,x in enumerate(ker))
        while v:
            p=v.bit_length()-1
            if p not in piv: piv[p]=v; chosen.append(c); break
            v^=piv[p]
        if len(chosen)==K: break
    ranks.append(len(chosen)); rem=[c for c in rem if c not in set(chosen)]
print('greedy disjoint information-set ranks:', ranks)
from collections import Counter
def hist(t):
    ind=list(base); ind[t]=3
    col=ind
    hists=[]
    while True:
        sig=[(col[v],tuple(sorted(col[u] for u in adj[v]))) for v in range(len(adj))]
        hists.append(tuple(sorted(Counter(sig).values())))
        ids={s:i for i,s in enumerate(sorted(set(sig)))}
        new=[ids[s] for s in sig]
        if len(set(new))==len(set(col)): return hists
        col=new
print('refinement histories of qubit 0 and qubit lm agree:', hist(0)==hist(lm))
def final(t):
    ind=list(base); ind[t]=3; return refine(ind)
c0, c1 = final(0), final(lm)
inv1 = {col:v for v,col in enumerate(c1)}
if set(c0)!=set(c1): print('colour sets differ: no automorphism maps 0 to lm')
else:
    perm=[inv1[col] for col in c0]
    E={(v,u) for v in range(len(adj)) for u in adj[v]}
    ok=all((perm[v],perm[u]) in E for (v,u) in E)
    print('colour-matching bijection 0 -> lm is an automorphism:', ok)
