"""check-chain c1: the F2[x] certificate of steps (2)-(3), recomputed from scratch.

(a) sigma = Frob^6 acts on indices as 2^6 = 27; on even functions (t) as w = -27 = 10; cosets (log2 mod 6)
    of 1-w, 2-w, 2-w^2.
(b) the aux relation eta(x) eta((1-w)x) = eta((2-w)x) + eta((2-w^2)x) derived at the group-ring level from the
    product rule eta(x)eta(y) = sum_{v in mu6} eta(x + y v) (exact multiset bookkeeping, mod 2).
(c) gcd(x^24 + x^9 + 1, x^63 + 1), its factorisation, the sextic m, m | x^21 + 1, order of x mod m.
(d) eta_0 not in F8 and eta_0 != 0: from irreducibility of Phi_37 over F2 (zeta^1..zeta^36 a basis).
(e) for each d: (*)_d(x) reduced mod m, compared with (x * x^(2^d))^n(d), WITHOUT reducing exponents mod 63
    (negative n handled by multiplying through); and the full set of n mod 21 that work.
"""
import json
import collections
import clib
from clib import pmod, pmul, ppowmod, pgcd, pstr, p

out = {}
mu6 = clib.mu(6)
mu3 = clib.mu(3)
L2 = clib.LOG2
coset = lambda x: L2[x % p] % 6

# (a)
s_mult = pow(2, 6, p)
w = (-s_mult) % p
assert pow(w, 3, p) == 1 and w != 1
cos = dict(a=coset(1 - w), b=coset(2 - w), b2=coset(2 - w * w))
out['(a) sigma multiplier 2^6 mod 37, w'] = [s_mult, w]
out['(a) cosets (a, b, b2) of 1-w, 2-w, 2-w^2'] = [cos['a'], cos['b'], cos['b2']]
# mu6 = coset 0 of log2 mod 6 (i.e. 2^6 generates mu6): needed for eta(2^c x) = eta(x)^(2^c) bookkeeping
out['(a) mu6 == <2^6>'] = sorted(pow(2, 6 * i, p) for i in range(6)) == mu6
# with the other generator w^2 of mu3 the formula's data: a same, {b, b2} swapped (so (*) is unchanged)
w2 = w * w % p
out['(a) cosets with w^2 instead'] = [coset(1 - w2), coset(2 - w2), coset(2 - w2 * w2)]
print(out)

# (b) eta(x) eta(y) = sum_{u,u' in mu6} z^(x u + y u') = sum_{v in mu6} eta(x + y v); with x = 1, y = 1 - w:
cnt = collections.Counter()
for v in mu6:
    c = (1 + (1 - w) * v) % p
    cnt['zero' if c == 0 else coset(c)] += 1
odd = sorted(k for k, n in cnt.items() if n % 2)
out['(b) product rule multiset of cosets of 1 + (1-w) v'] = dict(cnt)
out['(b) odd-multiplicity cosets'] = odd
assert odd == sorted([cos['b'], cos['b2']]), odd
# also check the product rule itself as an exact group-ring identity in Z[Z/37] for all x, y
def eta_vec(x):
    v = [0] * p
    for u in mu6:
        v[x * u % p] += 1
    return v
def conv(a, b):
    o = [0] * p
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    o[(i + j) % p] += ai * bj
    return o
pr_ok = True
for x in range(1, p):
    for y in range(1, p):
        lhs = conv(eta_vec(x), eta_vec(y))
        rhs = [0] * p
        for v in mu6:
            ev = eta_vec((x + y * v) % p)
            rhs = [r + e for r, e in zip(rhs, ev)]
        if lhs != rhs:
            pr_ok = False
out['(b) product rule exact in Z[Z/37] for all x,y'] = pr_ok
print('(b)', out['(b) odd-multiplicity cosets'], pr_ok)

# (c)
A, B, B2 = cos['a'], cos['b'], cos['b2']
aux_full = (1 << (1 + 2 ** A)) ^ (1 << 2 ** B) ^ (1 << 2 ** B2)          # x^17 + x^8 + x^32
low = (aux_full & -aux_full).bit_length() - 1
aux = aux_full >> low
out['(c) aux relation x^(1+2^a) + x^(2^b) + x^(2^b2) = x^%d * (%s)' % (low, pstr(aux))] = True
x63 = (1 << 63) | 1
g = pgcd(aux, x63)
facs = clib.irreducible_factors(g)
out['(c) gcd(aux, x^63+1)'] = pstr(g)
out['(c) factors'] = [pstr(f) for f in facs]
sext = [f for f in facs if f.bit_length() - 1 == 6]
assert len(sext) == 1
m = sext[0]
out['(c) sextic m'] = pstr(m)
out['(c) m irreducible (Rabin)'] = clib.is_irreducible(m)
out['(c) m | x^21 + 1'] = pmod((1 << 21) | 1, m) == 0
ordx = next(k for k in range(1, 64) if ppowmod(2, k, m) == 1)
out['(c) multiplicative order of x mod m'] = ordx
cub = [f for f in facs if f.bit_length() - 1 == 3]
out['(c) cubic factor has roots in F8 (divides x^7+1)'] = [pmod((1 << 7) | 1, f) == 0 for f in cub]
print('(c)', out['(c) gcd(aux, x^63+1)'], out['(c) factors'], 'order of x mod m:', ordx)

# (d) Phi_37 irreducible over F2  <=>  ord_37(2) = 36; then zeta^1..zeta^36 is an F2-basis of F(2^36), so a sum of
# a nonempty proper subset of {zeta^i : i != 0} is nonzero.  eta_0 + eta_3 is such a sum (mu6 and 8 mu6 disjoint).
phi37 = (1 << 37) - 1
out['(d) Phi_37 irreducible over F2'] = clib.is_irreducible(phi37)
S0 = set(mu6)
S3 = {8 * u % p for u in mu6}
out['(d) mu6 and 8*mu6 disjoint, 0 not in either'] = (not S0 & S3) and 0 not in S0 | S3
print('(d)', out['(d) Phi_37 irreducible over F2'], out['(d) mu6 and 8*mu6 disjoint, 0 not in either'])

# (e) the certificate
n_claim = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
def star_poly(d):
    """(*) with X = x, Y = x^(2^d), X^(c) := x^(2^c): returns the multiset of true integer exponents."""
    D = 2 ** d
    X, Y = 1, D
    Xa, Ya = 2 ** A, 2 ** A * D
    Xb, Yb = 2 ** B, 2 ** B * D
    Xc, Yc = 2 ** B2, 2 ** B2 * D
    terms = [
        # X^2 Y^2 (1 + X + Y)
        2 * X + 2 * Y, 3 * X + 2 * Y, 2 * X + 3 * Y,
        # X Y (X Ya + Xa Y)
        X + Y + X + Ya, X + Y + Xa + Y,
        # X Y Xa Ya
        X + Y + Xa + Ya,
        # Xa Ya (X + Y)
        Xa + Ya + X, Xa + Ya + Y,
        # Xb Yb + Xb' Yb'
        Xb + Yb, Xc + Yc,
    ]
    f = 0
    for e in terms:
        f ^= 1 << e
    return f, terms

cert = {}
for d in range(6):
    f, terms = star_poly(d)
    fr = pmod(f, m)
    n = n_claim[d]
    e = (1 + 2 ** d) * abs(n)
    if n >= 0:
        ok = pmod(f ^ (1 << e), m) == 0
    else:
        ok = pmod(pmul(f, 1 << e), m) == 1
    # which exponents E (mod ord x = 21) have x^E == (*)_d mod m, and which n solve (1+2^d) n = E mod 21
    Es = [E for E in range(ordx) if ppowmod(2, E, m) == fr]
    ns = sorted(nn for nn in range(ordx) if any((1 + 2 ** d) * nn % ordx == E for E in Es))
    cert[d] = dict(ok=ok, star_mod_m=pstr(fr), log_x=Es, n_mod_21_solutions=ns,
                   claimed_n_mod_21=n % ordx, max_true_exponent=max(terms),
                   XY_order=ordx // __import__('math').gcd(1 + 2 ** d, ordx))
    print('d=%d' % d, cert[d])
out['(e) certificate per d'] = cert
out['(e) all d certified'] = all(c['ok'] for c in cert.values())
json.dump(out, open('c1_certificate.json', 'w'), indent=1, default=str)
print('ALL d certified:', out['(e) all d certified'])
