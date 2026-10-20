"""Exact polynomial relations among the 4850 cluster and the two radius-6 relatives (GF(2), x^6 y^6 shift):
gcds and orbit differences (sympy cannot factor bivariate over GF(2)). Light check, sympy."""
import sys, json
sys.path[:0] = ["/home/user/lattice-lab/examples/rule-4850", "/home/user/lattice-lab/examples/linear-atlas-3"]
import sympy
import census
x, y = sympy.symbols("x y")
def poly(rid, r=6, shift=6):
    f = census.rule(rid, r)
    return sympy.Poly(sum(x**(p+shift) * y**(q+shift) for p, q in f), x, y, modulus=2)
R = {n: poly(n) for n in (4850, 482758, 10491524, 8438150, 43250486, 20982139, 178279803)}
out = {}
for n, P in R.items():
    print(n, len(census.rule(n, 6)), "terms")
for a in (10491524, 20982139, 178279803):
    for b in (10491524, 20982139, 178279803):
        if a < b:
            g = sympy.gcd(R[a], R[b])
            print("gcd", a, b, "degree", g.total_degree())
# orbit sets and the XOR of the relatives with 10491524
orbs = census.orbits(6)
for n in (10491524, 20982139, 178279803):
    print(n, [orbs[i] for i in range(28) if n >> i & 1])
for n in (20982139, 178279803):
    d = n ^ 10491524
    print("xor", n, "with 10491524:", d, [orbs[i] for i in range(28) if d >> i & 1])
print("xor 20982139 178279803:", [orbs[i] for i in range(28) if (20982139 ^ 178279803) >> i & 1])
