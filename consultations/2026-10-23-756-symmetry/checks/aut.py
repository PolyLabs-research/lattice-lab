import sys, itertools, time
sys.path.insert(0,'/home/user/lattice-lab/examples/qec-bb'); sys.path.insert(0,'/home/user/lattice-lab/examples/qec-distance')
import bb, distance as D
L, M = int(sys.argv[1]), int(sys.argv[2])
A = eval(sys.argv[3]); B = eval(sys.argv[4])
lm = L*M; n = 2*lm
hx, hz = D._bit_rows(A, B, L, M)
def basis(rows):
    piv = {}
    for r in rows:
        while r:
            p = r.bit_length()-1
            if p not in piv: piv[p]=r; break
            r ^= piv[p]
    return piv
def reduce(piv, r):
    while r:
        p = r.bit_length()-1
        if p not in piv: return r
        r ^= piv[p]
    return 0
BX, BZ = basis(hx), basis(hz)
def permute(row, perm):
    out = 0
    while row:
        t = (row & -row).bit_length()-1; row &= row-1
        out |= 1 << perm[t]
    return out
def preserves(perm):
    return all(reduce(BX, permute(r, perm))==0 for r in hx) and all(reduce(BZ, permute(r, perm))==0 for r in hz)
# torus automorphisms: (i,j) -> (a i + c j mod L, b i + d j mod M) as a group hom Z_L x Z_M -> itself
def homs():
    for a in range(L):
        for b in range(M):
            if (L*a) % L or (L*b) % M: continue
            for c in range(L):
                for d in range(M):
                    if (M*c) % L or (M*d) % M: continue
                    img = {((a*i+c*j)%L, (b*i+d*j)%M) for i in range(L) for j in range(M)}
                    if len(img) == lm: yield (a,b,c,d)
auts = list(homs()); print('torus automorphisms', len(auts), flush=True)
found = []
t0=time.time()
for (a,b,c,d) in auts:
    f = lambda i,j: ((a*i+c*j)%L, (b*i+d*j)%M)
    for swap in (0,1):
        for (s,t) in itertools.product(range(L), range(M)):
            perm = [0]*n
            for i in range(L):
                for j in range(M):
                    u,v = f(i,j); u2,v2 = (u+s)%L, (v+t)%M
                    li, ri = i*M+j, lm+i*M+j
                    if not swap: perm[li] = u*M+v; perm[ri] = lm+u2*M+v2
                    else: perm[li] = lm+u*M+v; perm[ri] = u2*M+v2
            if preserves(perm): found.append(((a,b,c,d),swap,(s,t)))
print('symmetries (mod common translation):', len(found), 'time', round(time.time()-t0), flush=True)
for f_ in found[:40]: print(f_)
