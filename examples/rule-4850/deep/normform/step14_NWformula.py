"""Step 14: a closed formula for N_{K/F64}(W(al, be)) at every off-axis character.
eta(x) = sum_{u in mu6} zeta^(x u)  (index-6 Gauss period of the class of x),
theta(x) = eta(x) + eta(8x) = sum_{u in mu12} zeta^(x u) (index-3 period).
Tests: chi(be/al) = +1: N(W) = eta(4 al^2 / be)?   chi(be/al) = -1: N(W) = theta(x) for which x (monomial al^r be^s c)?"""
import json, itertools
import nf

m = 37
T = nf.tvec()
mu3 = [1, 10, 26]
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
def eta(x):
    v = 0
    for u in mu3:
        v ^= T[x * u % m]
    return v
def theta(x):
    return eta(x) ^ eta(8 * x % m)
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
    return v
def NW(al, be):
    v = 1
    for c in mu3:
        v = nf.kmul(v, W(al, c * be % m))
    return v
inv = lambda z: pow(z, -1, m)
qr_ok = True; nqr = {}
for al in range(1, m):
    for be in range(1, m):
        n = NW(al, be)
        if nf.legendre(be * inv(al)) == 1:
            if n != eta(4 * al * al * inv(be) % m):
                qr_ok = False
        else:
            nqr[(al, be)] = n
print('chi(be/al) = +1:  N(W)(al, be) = eta(4 al^2 / be) at all such characters:', qr_ok)
# search theta(c al^r be^s), r, s in -3..3, c in F37*
found = []
for r in range(-3, 4):
    for s_ in range(-3, 4):
        for c in range(1, m):
            if all(n == theta(c * pow(al, r % 36, m) * pow(be, s_ % 36, m) % m) for (al, be), n in nqr.items()):
                found.append((c, r, s_))
print('chi(be/al) = -1:  N(W) = theta(c al^r be^s) for (c, r, s) in', found[:12], '... total', len(found))
# also: is it eta-valued + something?  check theta-ness
print('all NQR values are index-3 periods (in F8 and of the form eta(x)+eta(8x)):',
      all(any(n == theta(x) for x in range(1, m)) for n in nqr.values()))
json.dump({'qr_formula': qr_ok, 'nqr_theta_monomials': found}, open('step14_NWformula.json', 'w'), indent=1)
