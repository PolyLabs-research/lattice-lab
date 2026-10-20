"""Step 5 (norms): the closed form at m = 37 and a field-free certificate for it.

Claim (37):  N_{K/F64} W(al, be) = (eta(al) eta(be))^n(d),  d = log2(be/al) mod 6,
             n(d) = 2, -1, -4, 2, -4, -1   for d = 0..5,
hence for the core f0 (lambda = W/(t_al t_be), N(t_x) = eta(x)^2):  N(lambda) = (eta(al) eta(be))^(3 m(d)),
m(d) = 0, -1, -2, 0, -2, -1, a cube of an element of mu21, i.e. an element of F8* = the ninth powers of F64*.

(A) numerical check at all 1296 characters in our GF(2^36);
(B) certificate in F2[x] only (no field model):
    1. aux relation: x * x^16 = x^8 + x^32  (forced by the cosets (a, b, b') = (4, 3, 5) of 1-w, 2-w, 2-w^2,
       via eta(x) eta((1-w)x) = eta((2-w)x) + eta((2-w^2)x) mod 2), i.e. x^8 (x^24 + x^9 + 1) = 0;
    2. factor g = gcd(x^24 + x^9 + 1, x^63 + 1) over F2 and identify its sextic factor m(x); show m | x^21 + 1
       (every root has order | 21: eta is a cube);  m = minimal polynomial of eta_0 (checked in (A));
    3. for each d: (*)_d(x) + (x * x^(2^d))^(n(d) mod 63) = 0 mod m(x), exponents mod 63 (x^63 = 1 on F64*),
       where (*)_d is formula (*) with X = x, Y = x^(2^d), X^(c) = x^(2^c).
    4. also the additive forms: N = eta(4 al^2/be) (QR), theta(8 al^2/be) (d = +-1), theta(4 al^2/be) (d = 3)."""
import json
import nlib

# ---------------- F2[x] arithmetic on int bitmasks
def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m):
    dm = m.bit_length()
    while a and a.bit_length() >= dm:
        a ^= m << (a.bit_length() - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def pdivexact(a, b):
    q = 0
    db = b.bit_length()
    while a and a.bit_length() >= db:
        s = a.bit_length() - db
        q ^= 1 << s
        a ^= b << s
    assert a == 0
    return q


def mono(e):
    return 1 << e


def factor_sqfree(f):
    """naive factorisation over F2 by trial division with all irreducibles of degree <= deg/2."""
    facs = []
    deg = f.bit_length() - 1
    d = 1
    while f.bit_length() - 1 >= 2 * d:
        for c in range(1 << d, 1 << (d + 1)):
            if c & 1 == 0:
                continue
            # irreducibility of c by trial division by lower degree polys
            if any(pmod(c, q) == 0 for q in range(2, 1 << d) if q.bit_length() - 1 >= 1 and q != c):
                continue
            while pmod(f, c) == 0:
                facs.append(c)
                f = pdivexact(f, c)
        d += 1
    if f != 1:
        facs.append(f)
    return facs


def pstr(f):
    return ' + '.join(('x^%d' % i if i > 1 else ('x' if i == 1 else '1')) for i in range(f.bit_length() - 1, -1, -1) if f >> i & 1)


out = {}
# ---------------- (B) certificate
aux = mono(24) ^ mono(9) ^ 1
g = pgcd(aux, mono(63) ^ 1)
facs = factor_sqfree(g)
out['gcd(x^24+x^9+1, x^63+1)'] = pstr(g)
out['factors'] = [pstr(f) for f in facs]
print('gcd(x^24 + x^9 + 1, x^63 + 1) =', pstr(g), ' factors:', [pstr(f) for f in facs])
sext = [f for f in facs if f.bit_length() - 1 == 6]
assert len(sext) == 1
mpoly = sext[0]
print('the sextic factor m(x) =', pstr(mpoly), '  m | x^21 + 1:', pmod(mono(21) ^ 1, mpoly) == 0)
out['m'] = pstr(mpoly)
out['m divides x^21+1'] = pmod(mono(21) ^ 1, mpoly) == 0

n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
A_, B_, B2_ = 4, 3, 5


def star_exponents(d):
    D = pow(2, d, 63)
    pa, pb, pb2 = pow(2, A_, 63), pow(2, B_, 63), pow(2, B2_, 63)
    X, Y = 1, D
    E = [2 * X + 2 * Y, 3 * X + 2 * Y, 2 * X + 3 * Y,
         X + Y + X + pa * D, X + Y + pa + Y, X + Y + pa + pa * D,
         pa + pa * D + X, pa + pa * D + Y, pb + pb * D, pb2 + pb2 * D]
    return [e % 63 for e in E]


cert = {}
for d in range(6):
    poly = 0
    for e in star_exponents(d):
        poly ^= mono(e)
    target = mono(((1 + pow(2, d, 63)) * n[d]) % 63)
    ok = pmod(poly ^ target, mpoly) == 0
    cert[d] = ok
    print('d=%d: (*)_d(x) = (x * x^(2^d))^%d  mod m(x):' % (d, n[d]), ok)
out['certificate_mod_m'] = cert

# ---------------- (A) numerics at all characters
p = 37
S = nlib.Setting(p)
F = S.F
lg = S.two
eta = lambda x: S.eta(x % p)
theta = lambda x: eta(x) ^ eta(8 * x)
eta0 = eta(1)
# minimal polynomial of eta0 == m ?
val = 0
for i in range(7):
    if mpoly >> i & 1:
        val ^= F.pow(eta0, i)
out['m(eta_0) = 0'] = val == 0
print('m(eta_0) = 0 in GF(2^36):', val == 0)
okN = okadd = okf0 = True
inv = lambda z: pow(z, -1, p)
for al in range(1, p):
    for be in range(1, p):
        d = (lg[be] - lg[al]) % 6
        X, Y = eta(al), eta(be)
        N = S.norm_Kk(S.W(al, be))
        if N != F.pow(F.mul(X, Y), n[d] % F.order):
            okN = False
        if d % 2 == 0:
            add = eta(4 * al * al * inv(be))
        elif d == 3:
            add = theta(4 * al * al * inv(be))
        else:
            add = theta(8 * al * al * inv(be))
        if N != add:
            okadd = False
        lam = F.mul(S.W(al, be), F.inv(F.mul(S.t[al], S.t[be])))
        Nl = S.norm_Kk(lam)
        if not (F.frob(Nl, 3) == Nl):
            okf0 = False
out['N = (eta(al) eta(be))^n(d) at all 1296 characters'] = okN
out['additive forms at all characters'] = okadd
out['N(W/(t t)) in F8 at all characters'] = okf0
print('N(W) = (eta(al) eta(be))^n(d) at all characters:', okN)
print('additive forms (QR: eta(4al^2/be); d=3: theta(4al^2/be); d=+-1: theta(8al^2/be)):', okadd)
print('core f0: N(W/(t_al t_be)) in F8 at all off-axis characters:', okf0)
print('theta_2 = eta_0^-3 :', theta(4) == F.pow(eta0, F.order - 3), '  (theta_k = eta(2^k) + eta(2^(k+3)))')
out['theta_2 = eta_0^-3'] = theta(4) == F.pow(eta0, F.order - 3)
json.dump(out, open('s5_closed_form.json', 'w'), indent=1)
