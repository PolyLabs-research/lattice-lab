"""Step 24: explicit 'twisted trace' forms of the three rules (exact in F2[a, b]), from pi * f = 12-term orbit:
   f = sum over the three D4-representatives (p, q) of the T-orbit of (D_p(a)/a)(D_q(b)/b) (+ (q,p) term),
   with D_n(z)/z = g_n(z)^2 for odd n (g_3 = 1 + z, g_7 = z^3 + z^2 + 1) and D_4(z)/z = z^3:
 10491524  = (ab)^3 + (c(a) d(b) + d(a) c(b))^2                 [orbit (4,4) + (7,3)]
 20982139  = d(a)^2 d(b)^2 + b^3 c(a)^2 + a^3 c(b)^2           [orbit (3,3) + (7,4)]
 178279803 = c(a)^2 c(b)^2 + a^3 d(b)^2 + b^3 d(a)^2           [orbit (7,7) + (4,3)]
 with c(z) = z^3 + z^2 + 1, d(z) = 1 + z;  and f0 = 1 + b g11(a)^2 g5(b)^4 + a g5(a)^4 g11(b)^2  [orbit (1,1) + (11,10)]."""
import sympy as sp
import step8_relatives_lib as L
a, b = L.a, L.b
c = lambda z: z ** 3 + z ** 2 + 1
d = lambda z: 1 + z
forms = {10491524: (a * b) ** 3 + (c(a) * d(b) + d(a) * c(b)) ** 2,
         20982139: d(a) ** 2 * d(b) ** 2 + b ** 3 * c(a) ** 2 + a ** 3 * c(b) ** 2,
         178279803: c(a) ** 2 * c(b) ** 2 + a ** 3 * d(b) ** 2 + b ** 3 * d(a) ** 2}
for n, F in forms.items():
    print(n, 'explicit form equals the rule:', (L.rulepoly(n, 6) - sp.Poly(sp.expand(F), a, b, modulus=2)).is_zero)
# g_n with D_n(z) = z g_n(z)^2 for odd n
def g(n, z):
    q, r = sp.div(sp.Poly(L.dick(n, z), z, modulus=2), sp.Poly(z, z, modulus=2))
    assert r.is_zero
    sq = sp.sqrt(sp.Integer(1))  # placeholder
    # square root over GF(2): halve exponents
    terms = q.terms()
    assert all(e[0] % 2 == 0 for e, cc in terms if int(cc) % 2)
    return sum(z ** (e[0] // 2) for e, cc in terms if int(cc) % 2)
for n in (3, 5, 7, 11):
    print('g_%d(z) =' % n, g(n, a))
f0 = 1 + b * g(11, a) ** 2 * g(5, b) ** 4 + a * g(5, a) ** 4 * g(11, b) ** 2
f0_from_orbits = sp.Poly(sp.expand(1 + (L.dick(11, a) * L.dick(10, b) + L.dick(10, a) * L.dick(11, b)) / (a * b)), a, b, modulus=2)
print('f0 explicit form equals 1 + orbit(11,10)/(ab):', (f0_from_orbits - sp.Poly(sp.expand(f0), a, b, modulus=2)).is_zero)
