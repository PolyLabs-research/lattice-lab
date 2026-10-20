"""Step 10: the exact identities behind the norm equalities, as polynomials in a, b over GF(2).

G  = e(4,4) + e(7,3) = D4(a)D4(b) + D7(a)D3(b) + D3(a)D7(b)
G' = e(3,3) + e(7,4) = D3(a)D3(b) + D7(a)D4(b) + D4(a)D7(b)     (= G(x^10, y^10) mod 37)
G''= e(7,7) + e(4,3)                                             (= G(x^26, y^26) mod 37)
Claims (checked here in GF(2)[a, b], no reduction):
   F(20982139) * G = F(10491524) * G'      and     F(178279803) * G = F(10491524) * G''.
Hence, at m = 37, lambda(20982139) = lambda(10491524) * G^63 and lambda(178279803) =
lambda(10491524) * G^4095 at every character where G != 0, both ninth powers times; and since
10491524 is 4850 composed with (x, y) -> (xy, x/y), all three are ninth-power confined iff 4850 is.
Also: factorisations of all these polynomials over GF(2), the zeros of G at 37, and G's classes."""
import sympy
from sympy import symbols, Poly
from rlib import *

a, b = symbols('a b')

def P(Fset):
    return Poly(sum(a**i * b**j for i, j in Fset), a, b, modulus=2) if Fset else Poly(0, a, b, modulus=2)

def orbsum(*orbs):
    out = set()
    for o in orbs:
        out ^= orbit_F(o)
    return P(out)

F1, F2, F3, F4850 = P(rule_F(10491524, 6)), P(rule_F(20982139, 6)), P(rule_F(178279803, 6)), P(rule_F(4850, 4))
G = orbsum((4, 4), (7, 3))
G1 = orbsum((3, 3), (7, 4))
G2 = orbsum((7, 7), (4, 3))
print('F2*G == F1*G\'  :', (F2 * G - F1 * G1).is_zero)
print('F3*G == F1*G\'\':', (F3 * G - F1 * G2).is_zero)
print('F3*G\' == F2*G\'\':', (F3 * G1 - F2 * G2).is_zero)
# (bivariate factorisation over GF(2) is not available in sympy; the quotients are computed in
# step10b_quotient.py instead)
