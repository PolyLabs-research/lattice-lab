"""Step 4: the norm to F64 = F(2^6).  For z in K* = F(2^18)*:
   z is a ninth power  <=>  N_{K/F64}(z) = z^4161 lies in mu7 = F8*  (4161 = 1 + 64 + 64^2 = 3*19*73).
For 10491524: lambda' = W^4 / (t_al t_be), so N(lambda') = N(W)^4 / (eta_al^2 eta_be^2), with
   N(t_al) = t_al t_{10al} t_{26al} = eta_al^2,  eta_al = Tr_{K/F64}(t_al) = sum_{u in mu6} zeta^(al u) (Gauss period, index 6)
   N(W)(al, be) = prod_{c in mu3} W(al, c be)   (mu6 x mu6 invariant).
Check all of it, tabulate P(i, j) = N(lambda')(2^i, 2^j) for i, j in Z/6, and find the free conditions."""
import json, itertools
import numpy as np
import nf

m = 37
T = nf.tvec()
mu3 = [1, 10, 26]
inv = lambda u: pow(u, -1, m)
def N64(z):
    return nf.kpow(z, 4161)
def inF8(z):
    return nf.kpow(z, 8) == z
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * inv(u) % m])
    return v
lam = nf.vrule(10491524, 6)
# (1) criterion vs v27, for many random field elements and for lambda'
EXP, LOG = nf.tables()
V = nf.V27()
rng = np.random.default_rng(0)
ok = True
for z in rng.integers(1, 1 << 18, 3000):
    z = int(z)
    if (V[z] % 9 == 0) != (N64(z) != 0 and nf.kpow(N64(z), 7) == 1):
        ok = False
print('ninth power <=> N_{K/F64} in mu7, on 3000 random elements:', ok)
# (2) N(t_al) = eta^2, eta in F64
eta = {}
for al in range(1, m):
    e = 0
    for u in mu3:
        e ^= T[u * al % m]
    assert nf.kpow(e, 64) == e
    eta[al] = e
    assert N64(T[al]) == nf.kmul(e, e)
print('N(t_al) = eta_al^2 with eta_al = Tr(t_al) in F64: ok')
# (3) N(W) invariance and P table
lg2 = {pow(2, i, m): i for i in range(36)}
NW = {}
for al in range(1, m):
    for be in range(1, m):
        w3 = 1
        for c in mu3:
            w3 = nf.kmul(w3, W(al, c * be % m))
        assert N64(W(al, be)) == w3
        NW[(al, be)] = w3
inv_ok = all(NW[(al, be)] == NW[(u * al % m, v * be % m)] for al in range(1, m) for be in range(1, m)
             for u in (1, 10, 26, 36) for v in (1, 10, 26, 36))
print('N(W) invariant under mu6 x mu6:', inv_ok)
P = {}
for (al, be), w3 in NW.items():
    Pv = nf.kmul(nf.kpow(w3, 4), nf.kinv(nf.kmul(nf.kpow(eta[al], 2), nf.kpow(eta[be], 2))))
    assert Pv == N64(int(lam[nf.cls_index(al, be)]))
    P[(lg2[al] % 6, lg2[be] % 6)] = Pv
print('N(lambda\') = N(W)^4 / (eta_al eta_be)^2 at all off-axis characters: ok')
# F64 log table relative to a generator of F64*
g64 = nf.kpow(nf.gen(), 4161)
l64 = {}
x = 1
for e in range(63):
    l64[x] = e; x = nf.kmul(x, g64)
print('P(i, j) as log in F64* (mod 63);  in F8 <=> log = 0 mod 9:')
for i in range(6):
    print('  i=%d:' % i, [l64[P[(i, j)]] for j in range(6)], ' mod 9:', [l64[P[(i, j)]] % 9 for j in range(6)])
# relate: d = j - i classes
print('eta_i logs in F64*:', [l64[eta[pow(2, i, m)]] for i in range(6)])
print('NW(0, d) logs:', [l64[NW[(1, pow(2, d, m))]] for d in range(6)])
json.dump({'P_log63': {f'{i},{j}': l64[P[(i, j)]] for i in range(6) for j in range(6)},
           'NW_log63_0d': [l64[NW[(1, pow(2, d, m))]] for d in range(6)],
           'eta_log63': [l64[eta[pow(2, i, m)]] for i in range(6)]}, open('step4_f64.json', 'w'), indent=1)
