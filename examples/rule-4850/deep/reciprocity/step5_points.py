"""Step 5: the most reduced form of a class condition.

F(2^18) = F_512(t_1), and F_512* consists of 27th powers, so the ninth-power character chi factors
through F(2^18)*/F_512*, which is P^1(F_512) (513 points) and is cyclic (the norm-one torus mu_513).
Writing a class value as lam = A t_1 + B (A, B in F_512), its class is that of the point
c = B/A in P^1(F_512) (c = inf when A = 0).  lam is a ninth power iff c lies in the 57-point set
G57 = {c : t_1 + c in F_512* mu_57}.  Here we compute:
  - the table kappa(c) = chi(t_1 + c) mod 9 for all 512 c, and the set G57;
  - whether G57 has visible structure (subfield F_8, additive/multiplicative closure, Frobenius);
  - the points c_k for the target rules' class values, and whether they lie in F_8, F_64-ish sets.
Output: step5_points.txt"""
from rlib import *

m = m37()
t1 = 0b10
t6 = f18_pow(t1, 512)
assert t6 == val_t1(dickson(6)), 't_1^512 = t_6'
F512 = [v for v in range(1 << 18) if False]  # placeholder (built below)

# build F_512 inside F(2^18): v^512 = v.  Use a generator: g^(N18/511)... elements = 0 and powers of u
g = f18_generator()
u = f18_pow(g, N18 // 511)  # order 511
F512 = [0]
x = 1
for e in range(511):
    F512.append(x)
    x = f18_mul(x, u)
assert x == 1 and len(set(F512)) == 512
idx = {v: i for i, v in enumerate(F512)}  # index (0 for zero, 1 + e for u^e)

def point(lam):
    """c in P^1(F_512) with lam = A t_1 + B, as an element of F(2^18) (or None for infinity)"""
    lb = f18_pow(lam, 512)
    s = lam ^ lb
    A = f18_mul(s, f18_pow(t1 ^ t6, N18 - 1))
    B = lam ^ f18_mul(A, t1)
    assert f18_pow(A, 512) == A and f18_pow(B, 512) == B
    if A == 0:
        return None
    return f18_mul(B, f18_pow(A, N18 - 1))

kappa = {c: log9(t1 ^ c) for c in F512}
G57 = [c for c in F512 if kappa[c] == 0]
print('points c in F_512 with t_1 + c a ninth power:', len(G57), '(+ infinity) =', len(G57) + 1)
F8 = [c for c in F512 if f18_pow(c, 8) == c]
print('F_8 elements:', len(F8), ' kappa on F_8:', sorted(kappa[c] for c in F8))
# Frobenius: does c -> c^2 preserve G57?  (it does not have to: it moves t_1)
print('G57 closed under c -> c^2:', all(f18_mul(c, c) in set(G57) for c in G57))
print('G57 closed under c -> c + 1:', all((c ^ 1) in set(G57) for c in G57))
# kappa distribution
from collections import Counter
print('kappa distribution over F_512:', sorted(Counter(kappa.values()).items()))

RULES = [(4850, 4), (482758, 5), (10491524, 6), (8438150, 6), (43250486, 6), (20982139, 6), (178279803, 6)]
KS = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13]
for n, r in RULES:
    F = rule_F(n, r)
    out = []
    for k in KS:
        lam = val_t1(Q_dickson(F, k))
        c = point(lam)
        inF8 = c is None or f18_pow(c, 8) == c
        out.append(('inf' if c is None else idx[c], 'F8' if inF8 else '', log9(lam)))
    print(n, out)
