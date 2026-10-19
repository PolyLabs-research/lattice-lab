"""
Eigenvalues of linear rules on the square torus of odd side m, in finite fields of characteristic 2.

A rule is a Laurent polynomial f over GF(2), given as a set of exponent pairs (x, y): the
translations it reads (data/rules.json; on the triangle it is s, with M^2 = s I). On the torus
(Z/m)^2 its eigenvalues are f(zeta^j, zeta^k) for zeta a primitive m-th root of unity, in
F(2^d) with d = ord_m(2). The odd part of the period is the lcm of the orders of the nonzero
ones. Values at (j, k) and (2j, 2k) are Frobenius conjugates, so one per orbit is enough.

    F = Field(m)                       the field, with F.zeta, F.mul, F.pow, F.order (= 2^d - 1)
    eigenvalue(F, f, j, k)             f(zeta^j, zeta^k)
    orbits(m)                          one (j, k) per Frobenius orbit, with the orbit's size
    eigenvalues(F, f)                  {(j, k): value} over the orbit representatives
    order(F, a)                        the multiplicative order of a nonzero a
    is_power(F, a, q)                  whether a is a q-th power in F* (q dividing F.order)
    odd_part(f, m)                     the odd part of the rule's period at m
    full_bound(m)                      2^sord(m) - 1, with sord(m) the least j with 2^j = +-1 mod m

Field elements are ints (polynomials over GF(2) in the field's generator); addition is xor.
"""

from __future__ import annotations

import functools
import math

from gf2 import Field

__all__ = ["Field", "eigenvalue", "orbits", "eigenvalues", "order", "is_power", "odd_part",
           "full_bound"]  # fmt: skip


def eigenvalue(F: Field, f, j: int, k: int) -> int:
    value = 0
    for x, y in f:
        value ^= F.pow(F.zeta, (x * j + y * k) % F.m)
    return value


@functools.cache
def orbits(m: int) -> list[tuple[tuple[int, int], int]]:
    seen, out = set(), []
    for j in range(m):
        for k in range(m):
            if (j, k) in seen:
                continue
            a, b, size = j, k, 0
            while (a, b) not in seen:
                seen.add((a, b))
                a, b, size = 2 * a % m, 2 * b % m, size + 1
            out.append(((j, k), size))
    return out


def eigenvalues(F: Field, f) -> dict[tuple[int, int], int]:
    return {jk: eigenvalue(F, f, *jk) for jk, _ in orbits(F.m)}


@functools.cache
def _primes(n: int) -> tuple[int, ...]:
    out, p = [], 2
    while p * p <= n:
        if n % p == 0:
            out.append(p)
            while n % p == 0:
                n //= p
        p += 1
    return tuple(out + ([n] if n > 1 else []))


def order(F: Field, a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("0 has no order")
    n = F.order
    for p in _primes(F.order):
        while n % p == 0 and F.pow(a, n // p) == 1:
            n //= p
    return n


def is_power(F: Field, a: int, q: int) -> bool:
    if F.order % q:
        raise ValueError(f"{q} does not divide {F.order}")
    return F.pow(a, F.order // q) == 1


def odd_part(f, m: int) -> int:
    F = Field(m)
    period = 1
    for value in eigenvalues(F, f).values():
        if value:
            period = math.lcm(period, order(F, value))
    return period


def full_bound(m: int) -> int:
    j = 1
    while pow(2, j, m) not in (1, m - 1):
        j += 1
    return 2**j - 1
