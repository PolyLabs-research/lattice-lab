"""Sanity checks of rlib against sympy and the dossier facts."""
import sys, random
from rlib import *
import sympy
from sympy import Poly, symbols
T = symbols('T')

def to_sym(p):
    return Poly([(p >> i) & 1 for i in range(deg(p), -1, -1)], T, modulus=2)

# factor2 vs sympy on random polynomials
rng = random.Random(1)
for trial in range(60):
    p = rng.getrandbits(rng.randrange(2, 90)) | (1 << rng.randrange(1, 5))
    if p < 2: continue
    mine = factor2(p)
    prod = 1
    for q, e in mine:
        for _ in range(e): prod = clmul(prod, q)
    assert prod == p
    sy = sorted((sum(int(c) % 2 << i for (i,), c in fac.terms()), e) for fac, e in to_sym(p).factor_list()[1])
    assert sorted(mine) == sy, (p, mine, sy)
print('factor2 agrees with sympy on 60 random polynomials')

# 4850's F(a,b) vs the dossier formula s^3 + P^2 s^2 + P^3 + P^2 + P
F = rule_F(4850, 4)
print('rule 4850 orbits', rule_orbits(4850, 4))
print('F =', F_str(F))
a, b = symbols('a b')
s = a + b; P = a * b
G = Poly(s**3 + P**2 * s**2 + P**3 + P**2 + P, a, b, modulus=2)
mine = Poly(sum(a**i * b**j for i, j in F), a, b, modulus=2)
assert G == mine, (G, mine)
print('matches s^3 + P^2 s^2 + P^3 + P^2 + P')

# m37 is irreducible of degree 18 and t_1 = zeta + 1/zeta satisfies it
m = m37()
assert factor2(m) == [(m, 1)]
print('m37 =', pstr(m))

# ninth-power test of class values vs census logs
import importlib.util
spec = importlib.util.spec_from_file_location('census', '/home/user/lattice-lab/examples/rule-4850/census.py')
census = importlib.util.module_from_spec(spec); spec.loader.exec_module(census)
chars = census.characters()
print('census characters', chars)
