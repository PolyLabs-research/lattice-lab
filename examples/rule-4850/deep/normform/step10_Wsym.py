"""Step 10: the full twisted symmetry group of the Kloosterman element h (support S = {(u, e/u): u in mu6,
e = +-1} in (Z/37)^2), i.e. all g in GL2(F37) with g S = 2^k S (then W(g^T c) = W(c)^(2^k) for all c),
and the symmetry group of the class function of W pi^2 that it induces (pi's classes are Legendre)."""
import itertools, json
import numpy as np
import nf

m = 37
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
S = frozenset((u % m, e * pow(u, -1, m) % m) for u in mu6 for e in (1, -1))
assert len(S) == 12
dil = {}
for k in range(36):
    D = frozenset((pow(2, k, m) * p % m, pow(2, k, m) * q % m) for p, q in S)
    dil.setdefault(D, k)
print('distinct dilates 2^k S:', len(dil))
pts = sorted(S)
p1, p2 = (1, 1), (1, m - 1)    # two independent points of S
assert p1 in S and p2 in S
U = sorted(set().union(*dil.keys()))
found = []
for D, k in dil.items():
    Dl = sorted(D)
    for i1 in Dl:
        for i2 in Dl:
            # g p1 = i1, g p2 = i2 ;  p1 = (1,1), p2 = (1,-1): g = [i1 i2] [p1 p2]^-1
            inv2 = pow(2, -1, m)
            # [p1 p2] = [[1,1],[1,-1]] ; inverse = (1/2)[[1,1],[1,-1]]
            a = (i1[0] + i2[0]) * inv2 % m; b = (i1[0] - i2[0]) * inv2 % m
            c = (i1[1] + i2[1]) * inv2 % m; d = (i1[1] - i2[1]) * inv2 % m
            if (a * d - b * c) % m == 0:
                continue
            img = frozenset(((a * p + b * q) % m, (c * p + d * q) % m) for p, q in S)
            if img == D:
                found.append((((a, b), (c, d)), k))
print('|Stab(S) up to dilation| =', len(found))
ks = sorted({k % 18 for g, k in found})
print('dilation exponents k (mod 18) realised:', ks)
k0 = [g for g, k in found if k % 36 == 0]
print('#elements with g S = S:', len(k0))
# which are not in <D4, T>?
D4 = [((1, 0), (0, 1)), ((m - 1, 0), (0, 1)), ((1, 0), (0, m - 1)), ((m - 1, 0), (0, m - 1)),
      ((0, 1), (1, 0)), ((0, m - 1), (1, 0)), ((0, 1), (m - 1, 0)), ((0, m - 1), (m - 1, 0))]
def mm(g, h):
    return tuple(tuple(sum(g[i][t] * h[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
DT = set()
for g in D4:
    for c in mu6:
        DT.add(mm(g, ((c, 0), (0, pow(c, -1, m)))))
extra = [g for g in k0 if g not in DT]
print('|<D4, T_mu6>| =', len(DT), ' elements fixing S outside it:', extra[:10])
nontriv = [(g, k) for g, k in found if k % 36 != 0]
print('examples of g S = 2^k S, k != 0:', nontriv[:6])
json.dump({'n_found': len(found), 'ks_mod18': ks, 'n_fix': len(k0), 'extra_fix': [list(map(list, g)) for g in extra],
           'examples': [[list(map(list, g)), k] for g, k in nontriv[:20]]}, open('step10_Wsym.json', 'w'), indent=1)
