"""
The rules as polynomials in a = x + 1/x, b = y + 1/y over GF(2) (Dickson polynomials D_n), and
their decomposition F = (sum of odd-exponent monomials) + (a square): in characteristic 2 a
polynomial in a, b is a square iff every exponent is even. 10491524 = pi^3 + square (dossier).
    python ab_forms.py
"""
import sys
import sympy
sys.path.insert(0, "/home/user/lattice-lab/examples/rule-4850/deep/relations")
import tables  # noqa: E402

C = tables.C
a, b = sympy.symbols("a b")


def D(n, t):
    d0, d1 = 0, t
    if n == 0:
        return 0
    for _ in range(n - 1):
        d0, d1 = d1, sympy.expand(t * d1 + d0)
    return d1


def ab_poly(n, radius=6):
    s = 0
    for i, (p, q) in enumerate(C.orbits(radius)):
        if not n >> i & 1:
            continue
        if p == 0 and q == 0:
            s += 1
        elif q == 0:
            s += D(p, a) + D(p, b)
        elif p == q:
            s += D(p, a) * D(p, b)
        else:
            s += D(p, a) * D(q, b) + D(q, a) * D(p, b)
    return sympy.Poly(sympy.expand(s), a, b, modulus=2)


def split(P):
    odd = sum((sympy.Integer(1) * a**i * b**j for (i, j), c in P.terms() if (i % 2 or j % 2)), 0)
    even = sum((a**(i // 2) * b**(j // 2) for (i, j), c in P.terms() if not (i % 2 or j % 2)), 0)
    return sympy.Poly(odd, a, b, modulus=2) if odd else 0, sympy.Poly(even, a, b, modulus=2) if even else 0


if __name__ == "__main__":
    for n in (4850, 10491524, 20982139, 178279803, 8438150, 43250486, 482758):
        P = ab_poly(n)
        odd, root = split(P)
        print(n, "F =", P.as_expr())
        print("   non-square part:", odd.as_expr() if odd else 0)
        print("   square part = (", root.as_expr() if root else 0, ")^2")
