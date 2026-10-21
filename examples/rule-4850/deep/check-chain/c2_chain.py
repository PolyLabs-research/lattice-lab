"""check-chain c2: steps (3)-(4) in an independent GF(2^36) (dense random modulus, own zeta, own periods).

(1) eta_0 facts: in F64, not in F8, nonzero, m(eta_0) = 0 for the sextic m of c1, eta_0^21 = 1.
(2) N(t_x) = eta(x)^2: exact identity prod_{u in mu3} t_{ux} = sum_{u in mu3} (z^{2ux} + z^{-2ux}) in F2[Z/37],
    and in the field at every x.
(3) N(W(al,be)) = (eta(al) eta(be))^n(d) at every (al, be) in (F37*)^2; formula (*) at every (al, be).
(4) rule 4850 built from its orbit list: lambda(j,k) * t_al * t_be = W(al,be)^4 at every off-diagonal character
    (al = (j+k)/2, be = (j-k)/2 both nonzero); N(lambda) = (XY)^(4n(d)-2); N(lambda) in F8*.
(5) criterion: 4161 = (2^18-1)/63; z^4161 = z z^64 z^4096; N(g) has order 63 for a generator g of K*;
    z^29127 = 1  <=>  N(z) in F8*  (random sample of K* and every eigenvalue).
"""
import json
import random
import clib
from clib import p

F = clib.GF36()
out = {'modulus': clib.pstr(F.P), 'modulus_weight': bin(F.P).count('1')}
print('GF(2^36) modulus:', out['modulus'])
z = [F.pow(F.zeta, i) for i in range(p)]
t = [z[i] ^ z[(-i) % p] for i in range(p)]
mu6, mu3 = clib.mu(6), clib.mu(3)
L2 = clib.LOG2
eta = lambda x: (lambda s: s)(__import__('functools').reduce(lambda a, b: a ^ b, (z[x * u % p] for u in mu6), 0))
n_claim = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
inF8 = lambda v: F.in_sub(v, 3)
inK = lambda v: F.in_sub(v, 18)

# (1)
e0 = eta(1)
m = 0b1110101   # x^6 + x^5 + x^4 + x^2 + 1 (from c1)
mval = 0
for i in range(7):
    if m >> i & 1:
        mval ^= F.pow(e0, i)
out['(1) eta_0 in F64'] = F.in_sub(e0, 6)
out['(1) eta_0 in F8'] = inF8(e0)
out['(1) eta_0 != 0'] = e0 != 0
out['(1) m(eta_0) = 0'] = mval == 0
out['(1) eta_0^21 = 1'] = F.pow(e0, 21) == 1
out['(1) eta(2^c) = eta_0^(2^c), all c'] = all(eta(pow(2, c, p)) == F.frob(e0, c) for c in range(36))
print(out)

# (2)
def gr_mul(a, b):   # F2[Z/37] as sets of exponents (symmetric difference convolution)
    o = set()
    for i in a:
        for j in b:
            o ^= {(i + j) % p}
    return o
nt_exact = True
for x in range(1, p):
    prod = {0}
    for u in mu3:
        prod = gr_mul(prod, {u * x % p, (-u * x) % p})
    rhs = set()
    for u in mu3:
        rhs ^= {2 * u * x % p, (-2 * u * x) % p}
    nt_exact &= prod == rhs
out['(2) prod_{u in mu3} t_{ux} = eta(2x) exactly in F2[Z/37]'] = nt_exact
out['(2) N_{K/k}(t_x) = eta(x)^2 in field, all x'] = all(F.norm_K_k(t[x]) == F.mul(eta(x), eta(x)) for x in range(1, p))
out['(2) sigma = Frob^6 acts on t as x -> 10x'] = all(F.frob(t[x], 6) == t[10 * x % p] for x in range(p))
print('(2)', nt_exact, out['(2) N_{K/k}(t_x) = eta(x)^2 in field, all x'], out['(2) sigma = Frob^6 acts on t as x -> 10x'])

# (3)
def W(al, be):
    v = 0
    inv = lambda u: pow(u, -1, p)
    for u in mu3:
        v ^= F.mul(t[u * al % p], t[be * inv(u) % p])
    return v
w = 10
def star(al, be):
    X, Y = eta(al), eta(be)
    Xa, Ya = eta((1 - w) * al % p), eta((1 - w) * be % p)
    Xb, Yb = eta((2 - w) * al % p), eta((2 - w) * be % p)
    Xc, Yc = eta((2 - w * w) * al % p), eta((2 - w * w) * be % p)
    mm = F.mul
    XY = mm(X, Y)
    v = mm(mm(XY, XY), 1 ^ X ^ Y)
    v ^= mm(XY, mm(X, Ya) ^ mm(Xa, Y))
    v ^= mm(XY, mm(Xa, Ya))
    v ^= mm(mm(Xa, Ya), X ^ Y)
    v ^= mm(Xb, Yb) ^ mm(Xc, Yc)
    return v
etas = {x: eta(x) for x in range(1, p)}
Wv = {}
bad_closed = bad_star = 0
for al in range(1, p):
    for be in range(1, p):
        Wab = W(al, be)
        Wv[al, be] = Wab
        assert inK(Wab)
        N = F.norm_K_k(Wab)
        d = (L2[be] - L2[al]) % 6
        XY = F.mul(etas[al], etas[be])
        if N != F.pow(XY, n_claim[d]):
            bad_closed += 1
        if N != star(al, be):
            bad_star += 1
out['(3) N(W) = (XY)^n(d) failures /1296'] = bad_closed
out['(3) N(W) = (*) failures /1296'] = bad_star
print('(3)', bad_closed, bad_star)

# (4)
pts = clib.rule_points(clib.RULE4850_ORBITS)
out['(4) |rule 4850 exponent set|'] = len(pts)
h = pow(2, -1, p)
def lam(j, k):
    v = 0
    for a, b in pts:
        v ^= z[(a * j + b * k) % p]
    return v
bad_hex = bad_Nl = not_F8 = off = zero = 0
eig = {}
for j in range(p):
    for k in range(p):
        if (j, k) == (0, 0):
            continue
        L = lam(j, k)
        eig[j, k] = L
        if L == 0:
            zero += 1
            continue
        al, be = (j + k) * h % p, (j - k) * h % p
        if al == 0 or be == 0:
            continue
        off += 1
        if F.mul(L, F.mul(t[al], t[be])) != F.pow(Wv[al, be], 4):
            bad_hex += 1
        d = (L2[be] - L2[al]) % 6
        XY = F.mul(etas[al], etas[be])
        NL = F.norm_K_k(L)
        if NL != F.pow(XY, 4 * n_claim[d] - 2):
            bad_Nl += 1
        if not inF8(NL):
            not_F8 += 1
out['(4) off-diagonal characters'] = off
out['(4) zero eigenvalues (nontrivial chars)'] = zero
out['(4) lambda t_al t_be = W^4 failures'] = bad_hex
out['(4) N(lambda) = (XY)^(4n-2) failures'] = bad_Nl
out['(4) N(lambda) not in F8 (off-diagonal)'] = not_F8
out['(4) exponents 4n(d)-2'] = {d: 4 * n_claim[d] - 2 for d in range(6)}
out['(4) all exponents divisible by 3'] = all((4 * n_claim[d] - 2) % 3 == 0 for d in range(6))
print('(4)', off, zero, bad_hex, bad_Nl, not_F8)

# (5)
out['(5) 4161 == (2^18-1)/63'] = 4161 * 63 == clib.N18
g = F.g18
Ng = F.norm_K_k(g)
out['(5) N(g) == g^4161'] = Ng == F.pow(g, 4161)
ordNg = next(k for k in (1, 3, 7, 9, 21, 63) if F.pow(Ng, k) == 1)
out['(5) order of N(g) (63 = surjective onto F64*)'] = ordNg
out['(5) g generates K* (order 2^18-1)'] = all(F.pow(g, clib.N18 // q) != 1 for q in (3, 7, 19, 73)) and F.pow(g, clib.N18) == 1
rng = random.Random(7)
agree = 0
nsamp = 400
nn = 0
for _ in range(nsamp):
    e = rng.randrange(clib.N18)
    zz = F.pow(g, e)
    ninth = F.pow(zz, 29127) == 1
    crit = inF8(F.norm_K_k(zz))
    assert ninth == (e % 9 == 0)
    agree += ninth == crit
    nn += ninth
out['(5) random K*: (ninth power) == (N in F8*)'] = '%d/%d agree (%d ninth powers in sample)' % (agree, nsamp, nn)
ev_agree = all((F.pow(L, 29127) == 1) == inF8(F.norm_K_k(L)) for L in eig.values() if L)
out['(5) at every eigenvalue: (ninth power) == (N in F8*)'] = ev_agree
print('(5)', out['(5) 4161 == (2^18-1)/63'], out['(5) N(g) == g^4161'], ordNg, out['(5) random K*: (ninth power) == (N in F8*)'], ev_agree)
json.dump(out, open('c2_chain.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
