"""Step 8: the radius-6 relatives 20982139 and 178279803.
(a) their polynomials F(a, b) and their pi, s decompositions; (b) cube-plus-square form? (c) exact
T-invariance of lambda * u for small units u (is f * u = G with G T-invariant, as pi * 10491524 = h^4?);
(d) support of f * u mod 37 and whether it is a union of <D4, T>-orbits; (e) the same with M0."""
import json
import numpy as np
import sympy as sp
import nf

a, b = sp.symbols('a b')
def dick(n, z):
    D = [sp.Integer(0), z]
    for i in range(1, n):
        D.append(sp.expand(z * D[i] - D[i - 1]))
    return D[n]
def orbpoly(o):
    p, q = o
    if p == 0 and q == 0:
        return sp.Integer(1)
    if q == 0:
        return dick(p, a) + dick(p, b)
    if p == q:
        return dick(p, a) * dick(p, b)
    return dick(p, a) * dick(q, b) + dick(q, a) * dick(p, b)
def rulepoly(n, r):
    return sp.Poly(sum(orbpoly(o) for o in nf.rule_orbits(n, r)), a, b, modulus=2)
s_, P_ = sp.symbols('s P')
def in_sP(poly):
    """write a symmetric poly in a, b as a poly in s = a + b, P = ab over GF(2)."""
    rem = poly
    out = sp.Integer(0)
    while not rem.is_zero:
        (i, j), c = max(rem.terms(), key=lambda t: (t[0][0], t[0][1]))
        # leading a^i b^j with i >= j: subtract s^(i-j) P^j
        term = sp.Poly(sp.expand((a + b) ** (i - j) * (a * b) ** j), a, b, modulus=2)
        out += s_ ** (i - j) * P_ ** j
        rem = rem - term
    return sp.Poly(out, s_, P_, modulus=2)
rows = {}
for n, r in [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6)]:
    poly = rulepoly(n, r)
    sP = in_sP(poly)
    print(n, 'orbits', nf.rule_orbits(n, r))
    print('   in (s, P):', sP.as_expr())
    rows[n] = dict(orbits=nf.rule_orbits(n, r), sP=str(sP.as_expr()))
# differences from 10491524
p0 = rulepoly(10491524, 6)
for n in (20982139, 178279803):
    d = rulepoly(n, 6) - p0
    print(n, '- 10491524 =', in_sP(d).as_expr(), '  orbits:', sorted(set(nf.rule_orbits(n, 6)) ^ set(nf.rule_orbits(10491524, 6))))
    sPd = in_sP(d)
    rows[n]['diff_sP'] = str(sPd.as_expr())
# (c) exact T-invariance of lambda * u
m = 37
T = nf.tvec()
J, K = nf.grid()
def Tmap(c):  # index of T(c) = (10 j, 26 k)
    return (10 * J % m) * m + (26 * K % m)
units = {'1': np.ones(J.shape, dtype=np.int64), 'pi=t_a t_b': nf.vmul(nf.vt(J), nf.vt(K)),
         's=t_a+t_b': nf.vt(J) ^ nf.vt(K), 'e=(1+t_a)(1+t_b)': nf.vmul(1 ^ nf.vt(J), 1 ^ nf.vt(K)),
         'pi^2': nf.vpow(nf.vmul(nf.vt(J), nf.vt(K)), 2)}
idxT = Tmap(None)
for n in (10491524, 20982139, 178279803, 4850):
    lam = nf.vrule(n, 6 if n != 4850 else 4)
    for name, u in units.items():
        G = nf.vmul(lam, u)
        inv = np.array_equal(G[idxT], G)
        # also up to Frobenius: G(Tc) = G(c)^(2^k)?
        fro = [k for k in range(18) if np.array_equal(G[idxT], nf.vpow(G, 1 << k))]
        print(n, 'lambda *', name, ': exactly T-invariant:', inv, ' T-invariant up to Frobenius^k, k =', fro)
json.dump(rows, open('step8_relatives.json', 'w'), indent=1)
