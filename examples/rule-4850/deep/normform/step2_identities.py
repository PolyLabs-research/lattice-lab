"""Step 2: exact identities behind the cube-plus-square form of 10491524 (4850 rotated).
 (a) polynomial identities in F2[a, b] (a = x + 1/x, b = y + 1/y; D_n Dickson, orbit (p,q) = D_p(a)D_q(b) + D_q(a)D_p(b)):
       Y = s(1 + s e) = (a^3+a^2+1)(b+1) + (a+1)(b^3+b^2+1)
       pi * Y^2 = orbit(7,3),   pi^4 = orbit(4,4),   so  pi * F' = orbit(4,4) + orbit(7,3)   (exact, all m)
 (b) at m = 37: orbit(4,4) + orbit(7,3) = h^4 in F2[(Z/37)^2], h = sum_{u in mu6, e = +-1} x^u y^(e/u)
 (c) the eigenvalue form: F'(t_al, t_be) * t_al t_be = W^4,  W = sum_{u in mu3} t_{u al} t_{be/u}."""
import sympy as sp
import numpy as np
import nf

a, b = sp.symbols('a b')
def P2(e):
    return sp.Poly(sp.expand(e), a, b, modulus=2)
def dick(n, z):
    D = [sp.Integer(0), z]   # D_0 = 2 = 0 mod 2, D_1 = z
    for i in range(1, n):
        D.append(sp.expand(z * D[i] - D[i - 1]))
    return D[n]
def orb(p, q):
    if p == q:
        return dick(p, a) * dick(p, b)
    return dick(p, a) * dick(q, b) + dick(q, a) * dick(p, b)
s = a + b; pi = a * b; e = (1 + a) * (1 + b)
Y = s * (1 + s * e)
Fp = pi ** 3 + Y ** 2
# 10491524 from the census orbits
orbs = nf.rule_orbits(10491524, 6)
F_rule = sum((sp.Integer(1) if o == (0, 0) else (dick(o[0], a) + dick(o[0], b) if o[1] == 0 else orb(*o))) for o in orbs)
print('10491524 orbits:', orbs)
print('F\' = pi^3 + Y^2 equals rule 10491524 :', P2(F_rule - Fp).is_zero)
print('Y = (a^3+a^2+1)(b+1) + (a+1)(b^3+b^2+1) :', P2(Y - ((a**3 + a**2 + 1) * (b + 1) + (a + 1) * (b**3 + b**2 + 1))).is_zero)
print('pi * Y^2 = orbit(7,3) :', P2(pi * Y ** 2 - orb(7, 3)).is_zero)
print('pi^4 = orbit(4,4) :', P2(pi ** 4 - orb(4, 4)).is_zero)
print('pi * F\' = orbit(4,4) + orbit(7,3) :', P2(pi * Fp - orb(4, 4) - orb(7, 3)).is_zero)
# 4850 in the original frame
orbs4850 = nf.rule_orbits(4850, 4)
F4850 = sum((dick(o[0], a) + dick(o[0], b) if o[1] == 0 else orb(*o)) for o in orbs4850)
S = a + b; P = a * b
print('4850 = S^3 + P^2 S^2 + P^3 + P^2 + P :', P2(F4850 - (S**3 + P**2 * S**2 + P**3 + P**2 + P)).is_zero)
print('4850 * S = orbit(4,0) + orbit(5,2) :', P2(F4850 * S - (dick(4, a) + dick(4, b)) - orb(5, 2)).is_zero)
pass  # multivariate factoring over GF(2) is not available in sympy


# (b) group-ring identity at 37
m = 37
mu6 = sorted(u for u in range(1, m) if pow(u, 6, m) == 1)
mu3 = sorted(u for u in range(1, m) if pow(u, 3, m) == 1)
print('mu6 =', mu6, 'mu3 =', mu3)
def pts_orbit(p, q):
    return {(sp_ * x % m, sq * y % m) for x, y in ((p, q), (q, p)) for sp_ in (1, -1) for sq in (1, -1)}
h = {}
for u in mu6:
    for ee in (1, -1):
        key = (u % m, ee * pow(u, -1, m) % m)
        h[key] = h.get(key, 0) ^ 1
hs = {k for k, v in h.items() if v}
h4 = {(4 * x % m, 4 * y % m) for x, y in hs}   # Frobenius^2: squaring twice is the dilation by 4 in char 2
target = pts_orbit(4, 4) ^ pts_orbit(7, 3)
print('|h| =', len(hs), ' h^4 support == orbit(4,4)+orbit(7,3) mod 37:', h4 == target)
# h is invariant under the anti-diagonal dilation T_c: (x, y) -> (x^c, y^(1/c)), c in mu6
print('h invariant under T_c, c in mu6:', all({(c * x % m, pow(c, -1, m) * y % m) for x, y in hs} == hs for c in mu6))

# (c) eigenvalue form
T = nf.tvec()
lam = nf.vrule(10491524, 6)
ok = True; zeroW = 0
for al in range(37):
    for be in range(37):
        Wv = 0
        for u in mu3:
            Wv ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
        lhs = nf.kmul(int(lam[nf.cls_index(al, be)]), nf.kmul(T[al], T[be]))
        if lhs != nf.kpow(Wv, 4):
            ok = False
        zeroW += Wv == 0
print('lambda\'(al,be) t_al t_be = W^4 at all 1369 characters:', ok, ' (W = 0 at', zeroW, 'characters: the axes)')
