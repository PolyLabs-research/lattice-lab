"""
Finite fields of characteristic 2 containing a primitive m-th root of unity, for odd m.

    from gf2 import Field
    F = Field(15)          # F(2^d), d = ord_15(2) = 4
    z = F.zeta             # a primitive 15th root of unity
    F.mul(z, F.inv(z)) == F.one

Elements are ints: polynomials over GF(2) in the field's generator, reduced modulo an
irreducible factor of the m-th cyclotomic polynomial. Addition is xor.
"""

from __future__ import annotations

import functools

import sympy


@functools.cache
def _modulus(m: int) -> int:
    z = sympy.Symbol("z")
    _, factors = sympy.Poly(sympy.cyclotomic_poly(m, z), z, modulus=2).factor_list()
    g = factors[0][0]
    return sum((int(c) % 2) << e for (e,), c in g.terms())


class Field:
    """F(2^d) with d = ord_m(2), and zeta, a primitive m-th root of unity in it."""

    def __init__(self, m: int):
        if m < 1 or m % 2 == 0:
            raise ValueError("m must be odd and positive")
        self.m = m
        self.mod = _modulus(m) if m > 1 else 0b11  # m = 1: F(2), zeta = 1
        self.degree = self.mod.bit_length() - 1
        self.zero, self.one = 0, 1
        self.zeta = 0b10 if m > 1 else 1
        self.order = 2**self.degree - 1  # of the multiplicative group

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        r, top = 0, self.degree
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> top & 1:
                a ^= self.mod
        return r

    def pow(self, a: int, e: int) -> int:
        if e < 0:
            return self.pow(self.inv(a), -e)
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a, e = self.mul(a, a), e >> 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("0 has no inverse")
        return self.pow(a, self.order - 1)

    def sum(self, values) -> int:
        out = 0
        for v in values:
            out ^= v
        return out
