"""(library part of step 8) the radius-6 relatives 20982139 and 178279803.
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
