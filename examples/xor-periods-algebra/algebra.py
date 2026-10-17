"""
Exact periods of the parity rule B1357/S1357 on n x n tori, without simulating them.

The rule is linear over GF(2): a configuration is a polynomial in x and y modulo x^n - 1 and
y^n - 1, and one generation multiplies it by

    tau = (1 + x + 1/x)(1 + y + 1/y) - 1        (the eight neighbours)

so the state at generation t, from a single live cell, is tau^t. The ring is commutative, so
every configuration c evolves as c tau^t: if tau^(t0 + p) = tau^t0 then every orbit repeats with
a period dividing p from generation t0 on. The single cell therefore has the torus's longest
period and longest transient, which is what the simulations' "longest over three soups" estimate
from below.

The period is found as an order: tau^(t0 + P) = tau^t0 for a candidate P (the law under test),
then every prime q of P is divided out while tau^(t0 + P/q) = tau^t0 still holds. Only P's prime
factors are needed, not P generations: 2^99 - 1 is about 6 x 10^29, but its powers take about
200 multiplications. Products are cyclic 2D convolutions, computed by FFT and rounded; every
product checks that no entry is further than 0.25 from an integer, so the rounding is exact.

The same method gives rule 90's period on an n-cycle (multiplication by x + 1/x in
GF(2)[x]/(x^n - 1), with polynomials as integers).
"""

from __future__ import annotations

import numpy as np
import sympy


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


def suborder(m: int) -> int:
    """The least j >= 1 with 2^j = +-1 modulo m (1 for m <= 3)."""
    if m <= 3:
        return 1
    k, v = 1, 2 % m
    while v not in (1, m - 1):
        v, k = v * 2 % m, k + 1
    return k


def law(n: int) -> int:
    """The law under test: 2^v(n) (2^sord(n) - 1); 1 for a power of 2 (every soup dies)."""
    if n & (n - 1) == 0:
        return 1
    return (n // odd_part(n)) * (2 ** suborder(odd_part(n)) - 1)


def primes_of(m: int) -> list[int]:
    return sorted(sympy.factorint(m))


# --- the 2D ring ------------------------------------------------------------------------------


class Torus:
    """GF(2)[x, y] / (x^n - 1, y^n - 1), elements as n x n 0/1 arrays."""

    def __init__(self, n: int):
        self.n = n
        tau = np.zeros((n, n))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    tau[dx % n, dy % n] = 1
        self.tau = tau
        self.one = np.zeros((n, n))
        self.one[0, 0] = 1

    def mul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        n = self.n
        c = np.fft.irfft2(np.fft.rfft2(a) * np.fft.rfft2(b), s=(n, n))
        r = np.rint(c)
        if np.max(np.abs(c - r)) >= 0.25:
            raise ArithmeticError(f"FFT rounding not exact at n={n}")
        return (r.astype(np.int64) & 1).astype(np.float64)

    def power(self, e: int) -> np.ndarray:
        result, base = self.one, self.tau
        while e:
            if e & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            e >>= 1
        return result


def _order(repeats, candidate: int) -> int | None:
    """The least divisor p of `candidate` for which repeats(p) holds, given that repeats is true
    exactly for the multiples of the period; None if it fails for `candidate` itself."""
    if not repeats(candidate):
        return None
    period = candidate
    for q in primes_of(candidate) if candidate > 1 else []:
        while period % q == 0 and repeats(period // q):
            period //= q
    return period


def torus_period(n: int) -> dict:
    """The longest period and transient of B1357/S1357 on the n x n torus, exactly."""
    ring = Torus(n)
    t0 = 2 * n  # past every transient: the computed transient below must be smaller
    late = ring.power(t0)
    if not late.any():  # tau is nilpotent: everything dies
        transient = next(t for t in range(t0 + 1) if not ring.power(t).any())
        return {"period": 1, "transient": transient, "dies": True, "candidate": "zero"}

    def repeats(p: int) -> bool:
        return np.array_equal(ring.mul(late, ring.power(p)), late)

    period, candidate = None, None
    for label, value in (
        ("law", law(n)),
        ("2^v (2^ord - 1)", (n // odd_part(n)) * (2 ** sympy.n_order(2, odd_part(n)) - 1)),
    ):
        period = _order(repeats, value)
        if period is not None:
            candidate = label
            break
    if period is None:
        raise RuntimeError(f"n={n}: no candidate is a multiple of the period")
    shift = ring.power(period)
    state = ring.one
    transient = 0
    while not np.array_equal(ring.mul(state, shift), state):
        state = ring.mul(state, ring.tau)
        transient += 1
        if transient > t0:
            raise RuntimeError(f"n={n}: transient beyond {t0}")
    return {"period": period, "transient": transient, "dies": False, "candidate": candidate}


# --- rule 90 on an n-cycle --------------------------------------------------------------------


def _mul1(a: int, b: int, n: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a = (a ^ (1 << n)) | 1
    return r


def _pow1(a: int, e: int, n: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = _mul1(r, a, n)
        a = _mul1(a, a, n)
        e >>= 1
    return r


def rule90_period(n: int) -> int:
    """Rule 90's longest period on an n-cycle (from a single cell), exactly."""
    step = (1 << 1) | (1 << (n - 1))
    late = _pow1(step, 2 * n, n)
    if late == 0:
        return 1
    period = _order(lambda p: _mul1(late, _pow1(step, p, n), n) == late, law(n))
    if period is None:
        raise RuntimeError(f"rule 90 at n={n}: period does not divide {law(n)}")
    return period
