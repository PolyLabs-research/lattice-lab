"""Step 12: the core rule f0 = h / pi, h = sum_{u in mu6(F37), e = +-1} x^u y^(e/u) = orbit(1,1) + orbit(11,10)
(lifted to centred representatives), pi = (x + 1/x)(y + 1/y).  Checks:
 (a) f0 is a Laurent polynomial (exact division over GF(2)); its D4 orbits; radius
 (b) its class logs at 37 (nf and census.logs_of-style independent F(2^36) model), ninth-confinement, axes
 (c) the core statement in Legendre form: W^29127 = rho^(chi(al) + chi(be)), rho = sum_{u nonres} zeta^u
 (d) the reductions, at every off-axis character (eigenvalues, exact):
       10491524  = pi^3 * f0^4
       20982139  = e^2 * f0(3 al, 3 be)              (e = (1 + t_al)(1 + t_be), a ninth power)
       178279803 = t_al^3 (1 + t_be)^2 * f0(4 al, 3 be)
 (e) the axis classes of the three rules (where pi = 0)."""
import sys, json
import numpy as np
import sympy as sp
import nf
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census, eigen

m = 37
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
def cen(p):
    p %= m
    return p - m if p > m // 2 else p
hpts = {(cen(u), cen(e * pow(u, -1, m))) for u in mu6 for e in (1, -1)}
print('h support:', sorted(hpts))
# exact division by pi over GF(2) with sympy (shift to polynomials)
x, y = sp.symbols('x y')
R = 12
hp = sp.Poly(sum(x ** (p + R) * y ** (q + R) for p, q in hpts), x, y, modulus=2)
pip = sp.Poly((x ** 2 + 1) * (y ** 2 + 1), x, y, modulus=2)      # = pi * x y
q, r = sp.div(hp, pip)
assert r.is_zero
f0 = set()
for (i, j), c in q.terms():
    if int(c) % 2:
        f0.add((i - (R - 1), j - (R - 1)))
f0 = frozenset(f0)
orbs = sorted({(max(abs(p), abs(q_)), min(abs(p), abs(q_))) for p, q_ in f0})
radius = max(max(abs(p), abs(q_)) for p, q_ in f0)
print('f0 = h / pi: terms', len(f0), ' radius', radius, ' D4 orbits:', orbs)
# family number of f0 at its radius
ol = nf.orbits(radius)
num = sum(1 << ol.index(o) for o in orbs)
assert census.rule(num, radius) == f0
print('f0 is family rule', num, 'of radius', radius)
# (b) class logs, two models
lt = census.log_table()
zeta = [census.power(2, e) for e in range(m)]
cl = []
for j, k in census.characters():
    v = 0
    for p, q_ in f0:
        v ^= zeta[(p * j + q_ * k) % m]
    cl.append(int(lt[census.coord(v)]))
vals = nf.vrule(num, radius)
print('f0 class logs mod 27 (census model):', cl, ' (nf model):', nf.class_v27(vals))
print('f0 ninth-confined at all characters (nf):', nf.is_ninth_confined(vals))
op = eigen.odd_part(f0, m)
print('eigen.odd_part(f0, 37) =', op, ' divides 29127:', 29127 % op == 0)
# (c) Legendre form
J, K = nf.grid()
T = nf.tvec()
W = nf.vorbit((1, 1)) ^ nf.vorbit((11, 10))
F = nf.tables()
rho = 0
for u in range(1, m):
    if nf.legendre(u) == -1:
        rho ^= nf.kpow(nf.kpow(nf.t1(), 1) , 0) if False else 0
# rho = sum over nonresidues of zeta^u = sum over nonresidues u <= 18 of t_u (37 = 1 mod 4: -1 is a residue)
rho = 0
for u in range(1, 19):
    if nf.legendre(u) == -1:
        rho ^= T[u]
assert nf.kmul(rho, rho) ^ rho ^ 1 == 0, 'rho is a primitive cube root of 1'
ok = True
for idx in range(len(J)):
    al, be = int(J[idx]), int(K[idx])
    if al == 0 or be == 0:
        continue
    lhs = nf.kpow(int(W[idx]), 29127)
    rhs = nf.kpow(rho, (nf.legendre(al) + nf.legendre(be)) % 3)
    if lhs != rhs:
        ok = False
print('W^29127 = rho^(chi(al)+chi(be)) at all off-axis characters:', ok)
# t^29127 = rho^chi check (the dossier's Legendre statement, same rho convention)
print('t_j^29127 = rho^chi(j) for all j != 0:', all(nf.kpow(T[j], 29127) == nf.kpow(rho, nf.legendre(j) % 3) for j in range(1, m)))
# (d) reductions
idx_of = lambda A, B: (A % m) * m + (B % m)
f0v = vals
pi = nf.vmul(nf.vt(J), nf.vt(K)); e = nf.vmul(1 ^ nf.vt(J), 1 ^ nf.vt(K))
off = (J != 0) & (K != 0)
r1 = nf.vrule(10491524, 6); r2 = nf.vrule(20982139, 6); r3 = nf.vrule(178279803, 6)
f0_33 = f0v[idx_of(3 * J, 3 * K)]; f0_43 = f0v[idx_of(4 * J, 3 * K)]
c1 = np.array_equal(r1[off], nf.vmul(nf.vpow(pi, 3), nf.vpow(f0v, 4))[off])
c2 = np.array_equal(r2[off], nf.vmul(nf.vpow(e, 2), f0_33)[off])
c3 = np.array_equal(r3[off], nf.vmul(nf.vmul(nf.vpow(nf.vt(J), 3), nf.vpow(1 ^ nf.vt(K), 2)), f0_43)[off])
print('10491524 = pi^3 f0^4 off axes:', c1, ';  20982139 = e^2 f0(3c) off axes:', c2, ';  178279803 = t_al^3 (1+t_be)^2 f0(4al,3be) off axes:', c3)
# classes of the multipliers (they must be ninth powers)
V = nf.V27()
print('pi^3, e^2, t^3 (1+t)^2 ninth powers off axes:', bool(np.all(V[nf.vpow(pi, 3)[off]] % 9 == 0)), bool(np.all(V[nf.vpow(e, 2)[off]] % 9 == 0)),
      bool(np.all(V[nf.vmul(nf.vpow(nf.vt(J), 3), nf.vpow(1 ^ nf.vt(K), 2))[off]] % 9 == 0)))
# (e) axes
for n in (10491524, 20982139, 178279803):
    rv = nf.vrule(n, 6)
    ax = [(0, b) for b in range(1, m)]
    print(n, 'axis values v27:', sorted({int(V[rv[idx_of(*c)]]) for c in ax}), ' (f0 axis v27:', sorted({int(V[f0v[idx_of(*c)]]) for c in ax}), ')')
json.dump({'f0_rule': num, 'f0_radius': radius, 'f0_orbits': orbs, 'f0_terms': len(f0), 'f0_logs27_census': cl,
           'odd_part': op, 'legendre_form': ok, 'reductions': [c1, c2, c3]}, open('step12_core.json', 'w'), indent=1)
