"""Step 1: the cube-plus-square form of 10491524 (= 4850 rotated) at every character of m = 37.
F' = pi^3 + Y^2,  pi = ab, s = a+b, e = (1+a)(1+b), Z = 1 + s e, Y = s Z,  a = t_j, b = t_k.
For each character: v27 of pi, s, Z, Y, F'; whether Y is a cube; if so the three factors
pi + w^i c (c^3 = Y^2, c in K) and their v27; if not, z = pi + c in L = F(2^54) and v81(z)."""
import json, collections
import numpy as np
import nf

J, Kk = nf.grid()
a, b = nf.vt(J), nf.vt(Kk)
pi = nf.vmul(a, b); s = a ^ b; e = nf.vmul(1 ^ a, 1 ^ b)
Z = 1 ^ nf.vmul(s, e); Y = nf.vmul(s, Z)
lam = nf.vpow(pi, 3) ^ nf.vmul(Y, Y)
assert np.array_equal(lam, nf.vrule(10491524, 6))
V = nf.V27()
EXP, LOG = nf.tables()
NK = nf.NK
w = nf.kpow(nf.gen(), NK // 3)   # primitive cube root of 1
assert nf.kmul(w, w) ^ w ^ 1 == 0

# cube root in L
n81 = nf.NL // 81
e3 = pow(3, -1, n81)
def lcbrt(W):
    r = nf.lpow(W, e3)
    zt = nf.lmul(nf.lpow(r, 3), nf.linv(W))   # in mu27
    vz = nf._xpow81()[zt]   # zt in mu81: its log base x
    assert vz % 3 == 0
    # theta = x^s with theta^3 = zt^-1 : 3 s = -vz mod 81
    sx = (-vz // 3) % 27
    c = nf.lmul(r, nf.lpow(2, sx))
    assert nf.lpow(c, 3) == W
    return c

rows = []
for idx in range(len(J)):
    j, k = int(J[idx]), int(Kk[idx])
    if j == 0 and k == 0:
        continue
    row = dict(j=j, k=k, L=[nf.legendre(j), nf.legendre(k), nf.legendre(j + k), nf.legendre(j - k)],
               pi=int(V[pi[idx]]), s=int(V[s[idx]]), Z=int(V[Z[idx]]), Y=int(V[Y[idx]]), lam=int(V[lam[idx]]))
    if Y[idx] == 0 or pi[idx] == 0:
        row['zero'] = True
        rows.append(row); continue
    Y2 = nf.kmul(int(Y[idx]), int(Y[idx]))
    if V[Y[idx]] % 3 == 0:
        lg = int(LOG[Y2]); assert lg % 3 == 0
        c = int(EXP[(lg // 3)])
        assert nf.kpow(c, 3) == Y2
        fac = [int(pi[idx]) ^ nf.kmul(nf.kpow(w, i), c) for i in range(3)]
        prod = nf.kmul(nf.kmul(fac[0], fac[1]), fac[2])
        assert prod == lam[idx]
        row['Ycube'] = True
        row['fac'] = sorted(int(V[f]) for f in fac)
    else:
        c = lcbrt(nf.embed(Y2))
        z = nf.embed(int(pi[idx])) ^ c
        # check the norm
        Nz = nf.lmul(nf.lmul(z, nf.lpow(z, 1 << 18)), nf.lpow(z, 1 << 36))
        assert Nz == nf.embed(int(lam[idx])), 'norm'
        row['Ycube'] = False
        row['v81z'] = nf.v81(z)
        row['v81c'] = nf.v81(c)
    rows.append(row)

json.dump(rows, open('step1_cubesq.json', 'w'))
# summaries
cnt = collections.Counter()
for r in rows:
    if r.get('zero'):
        cnt['zero (pi or Y)'] += 1; continue
    cnt[('Ycube', r['Ycube'])] += 1
print('counts', dict(cnt))
print('lam ninth everywhere (nonzero):', all(r['lam'] % 9 == 0 for r in rows if r['lam'] >= 0))
# class reps
for (j, k) in nf.CLASSES:
    r = next(r for r in rows if r['j'] == j and r['k'] == k)
    print((j, k), {kk: r[kk] for kk in r if kk not in ('j', 'k')})
# distribution of factor triples mod 9 (cube case)
tri = collections.Counter(tuple(sorted(x % 9 for x in r['fac'])) for r in rows if r.get('Ycube'))
print('Y cube: factor v27 mod 9 triples:', dict(tri))
tri27 = collections.Counter(tuple(r['fac']) for r in rows if r.get('Ycube'))
print('Y cube: factor v27 triples (mod 27):', dict(tri27))
nc = collections.Counter((r['v81z'] % 27, r['v81c'] % 27) for r in rows if r.get('Ycube') is False)
print('Y non-cube: (v81 z mod 27, v81 c mod 27):', dict(nc))
print('Y v27 mod 9 dist:', collections.Counter(r['Y'] % 9 for r in rows if r['Y'] >= 0))
print('Z v27 mod 9 dist:', collections.Counter(r['Z'] % 9 for r in rows if r['Z'] >= 0))
print('s v27 mod 9 dist:', collections.Counter(r['s'] % 9 for r in rows if r['s'] >= 0))
