"""
Round 2's four accidents, eigenvalue by eigenvalue. (Not registered.)

    uv run python examples/linear-atlas-2/subfield.py

At odd n a square rule's eigenvalues are f(zeta^j, zeta^k), for zeta a primitive n-th root of
unity in F(2^ord). Every rule here is a polynomial in a = x + 1/x and b = y + 1/y, so its
eigenvalues are F(t_j, t_k), with t_j = zeta^j + zeta^-j rule 90's eigenvalues, which lie in
F(2^sord). This computes every eigenvalue of the four rules that failed once in round 2 and
reports their multiplicative orders. For A4+C4 and A4+C4+self it also asks whether
q(t) = t^3 + t^2 + t lies in F(8). Those two rules are additively separable, q(a) + q(b) and
1 + q(a) + q(b), since x^2 + x^-2 = a^2 and x^3 + x^-3 = a^3 + a. Writes subfield.json.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import sympy

HERE = Path(__file__).resolve().parent


class Field:
    """F(2^d) as F2[z] modulo an irreducible factor of the n-th cyclotomic polynomial, so z is a
    primitive n-th root of unity. Elements are bitmasks."""

    def __init__(self, n: int):
        z = sympy.Symbol("z")
        _, factors = sympy.Poly(sympy.cyclotomic_poly(n, z), z, modulus=2).factor_list()
        g = factors[0][0]
        self.mod = sum((int(c) % 2) << e for (e,), c in g.terms())
        self.degree = self.mod.bit_length() - 1
        self.order = 2**self.degree - 1
        self.n = n

    def mul(self, a: int, b: int) -> int:
        r, top = 0, self.mod.bit_length() - 1
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> top & 1:
                a ^= self.mod
        return r

    def power(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a, e = self.mul(a, a), e >> 1
        return r

    def element_order(self, a: int) -> int:
        o = self.order
        for p in sympy.primefactors(self.order):
            while o % p == 0 and self.power(a, o // p) == 1:
                o //= p
        return o

    def rule90(self) -> list[int]:
        zeta = 2
        inverse = self.power(zeta, self.n - 1)
        return [self.power(zeta, j) ^ self.power(inverse, j) for j in range(self.n)]


def rules(F: Field):
    m = F.mul

    def sq(a):
        return m(a, a)

    def q(a):
        return m(sq(a), a) ^ sq(a) ^ a  # x^2 + x^-2 + x^3 + x^-3 in terms of a = x + 1/x

    return {
        "A4+C4": lambda a, b: q(a) ^ q(b),
        "A4+C4+self": lambda a, b: 1 ^ q(a) ^ q(b),
        # A4 = a^2 + b^2, K8 = ab(a + b), B4 = a^2 b^2, C4 = a^3 + a + b^3 + b
        "A4+K8+B4+C4+self": lambda a, b: (
            1
            ^ sq(a)
            ^ sq(b)
            ^ m(m(a, b), a ^ b)
            ^ m(sq(a), sq(b))
            ^ m(sq(a), a)
            ^ a
            ^ m(sq(b), b)
            ^ b
        ),
        "A4+K8+B4+self": lambda a, b: 1 ^ sq(a) ^ sq(b) ^ m(m(a, b), a ^ b) ^ m(sq(a), sq(b)),
    }, q


def main() -> None:
    out = {}
    for n, names in [(13, ["A4+C4", "A4+C4+self", "A4+K8+B4+C4+self"]), (37, ["A4+K8+B4+self"])]:
        F = Field(n)
        t = F.rule90()
        fs, q = rules(F)
        for name in names:
            values = {fs[name](t[j], t[k]) for j in range(n) for k in range(n)}
            orders = sorted({F.element_order(v) for v in values if v})
            out[f"{name} at {n}"] = {
                "field": f"F(2^{F.degree})",
                "distinct eigenvalues": len(values),
                "orders": orders,
                "period": math.lcm(*orders),
            }
        if n == 13:
            out["q(t_j) in F(8), j = 1..12"] = all(F.power(q(v), 8) == q(v) for v in t[1:])
    (HERE / "subfield.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
