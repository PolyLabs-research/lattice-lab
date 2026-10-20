"""Step 11: 4850 * (a + b) = e(4,0) + e(5,2) exactly, and the symmetries of the 12-point support.

Checks the identity F_4850 * (a+b) = D4(a) + D4(b) + D5(a)D2(b) + D2(a)D5(b) in GF(2)[a, b], and its
rotated form F_10491524 * ab = e(4,4) + e(7,3).  Then finds every M in GL2(Z/37) with
S M = d S (mod 37) for a unit d, where S = supp(e(4,0) + e(5,2)) (12 points): such M give
lambda_N(M^T c) = lambda_N(d c) = lambda_N(c)^(2^log2(d)), extra structure beyond D4."""
import itertools
import numpy as np
from sympy import symbols, Poly
from rlib import *
a, b = symbols('a b')

def P(Fset):
    return Poly(sum(a**i * b**j for i, j in Fset), a, b, modulus=2)

def orbsum(*orbs):
    out = set()
    for o in orbs:
        out ^= orbit_F(o)
    return P(out)

F = P(rule_F(4850, 4))
N = orbsum((4, 0), (5, 2))
print('F_4850 * (a+b) == e(4,0) + e(5,2):', (F * Poly(a + b, a, b, modulus=2) - N).is_zero)
F1 = P(rule_F(10491524, 6))
print('F_10491524 * ab == e(4,4) + e(7,3):', (F1 * Poly(a * b, a, b, modulus=2) - orbsum((4, 4), (7, 3))).is_zero)
print('rule id of e(4,0)+e(5,2) in the radius-5 family:', (1 << orbits(5).index((4, 0))) | (1 << orbits(5).index((5, 2))))

m = 37
S = sorted({(p % m, q % m) for p, q in points((4, 0)) | points((5, 2))})
Sset = set(S)
Sarr = np.array(S)
found = []
# all invertible M = [[A, B], [C, D]] acting on row vectors s -> s M
vals = np.arange(m)
A, B, C, D = np.meshgrid(vals, vals, vals, vals, indexing='ij')
A, B, C, D = A.ravel(), B.ravel(), C.ravel(), D.ravel()
det = (A * D - B * C) % m
inv = det != 0
A, B, C, D = A[inv], B[inv], C[inv], D[inv]
# image of S: for each M, the set {(s0 A + s1 C, s0 B + s1 D)}; check image == d S for some d
codes = lambda X, Y: (X % m) * m + (Y % m)
Scodes = {d: np.array(sorted(((d * p) % m) * m + (d * q) % m for p, q in S)) for d in range(1, m)}
img = np.stack([codes(s0 * A + s1 * C, s0 * B + s1 * D) for s0, s1 in S], axis=1)
img.sort(axis=1)
for d in range(1, m):
    ok = (img == Scodes[d][None, :]).all(axis=1)
    for i in np.flatnonzero(ok):
        found.append((d, (int(A[i]), int(B[i]), int(C[i]), int(D[i]))))
print('matrices M with S M = d S:', len(found))
from collections import Counter
print('by d:', sorted(Counter(d for d, _ in found).items()))
print('stabiliser (d = 1):', [M for d, M in found if d == 1])
print('non-D4 examples:', [x for x in found if x[0] != 1][:12])
