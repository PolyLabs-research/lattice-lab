"""
Fable's criterion for rule 90's cube confinement, and the two ways of deciding it.

A consultation (docs/consultations.md) gave this claim, from Claude Fable, on the m = 37 cubes:
for a prime p = 5 (mod 8) at which 2 is a primitive root,

    (U)  1 + zeta is a cube in F(2^(p-1))   <=>   eps^h lies in Z[sqrt p],

where eps is the fundamental unit and h the class number of Q(sqrt p). (U) is the same as rule
90 (t = x + 1/x) being confined to the cubes at p, since t(zeta^c) = zeta^-c (1 + zeta^c)^2 and
every 1 + zeta^c is a Frobenius conjugate of 1 + zeta. Fable also predicted that at p = i^2 + 1
(i = 2 mod 4) where (U) holds, the "pyramid" rule (the centre and the square rings at radii
2, 4, ..., i/2 - 1) is confined to the cubes.

The two sides of the test are computed by unrelated means:

- predicted(p): number theory only. eps from the least solution of a^2 - p b^2 = -4 (a prime
  p = 1 mod 4 has a unit of norm -1; eps = (a + b sqrt p)/2), so eps lies in Z[sqrt p] exactly
  when a and b are even. Otherwise eps^3 does (2 is inert, and (O_K / 2)* has order 3). So
  eps^h lies in Z[sqrt p] iff a, b are even or 3 divides h. h is counted as the number of cycles
  of reduced binary quadratic forms of discriminant p (the narrow class number, equal to h since
  eps has norm -1), and cross-checked by the analytic class number formula.
- confined(p): direct. In GF(2)[x]/Phi_p (Phi_p is irreducible when 2 is a primitive root),
  1 + x is a cube iff its norm to F(4), the product of its conjugates (1 + x)^(4^i) =
  1 + x^(4^i mod p) for i < (p - 1)/2, is 1.
"""

from __future__ import annotations

import math
from functools import cache

import numpy as np
import sympy


def eligible(lo: int, hi: int) -> list[int]:
    """Primes p = 5 (mod 8) in [lo, hi) at which 2 is a primitive root."""
    return [p for p in sympy.primerange(lo, hi)
            if p % 8 == 5 and sympy.n_order(2, p) == p - 1]  # fmt: skip


# ---------------------------------------------------------------- the prediction (number theory)


@cache
def fundamental_unit(p: int) -> tuple[int, int]:
    """(a, b): eps = (a + b sqrt p)/2, the least solution of a^2 - p b^2 = +-4 with a, b > 0,
    by the continued fraction of (1 + sqrt p)/2, whose period gives the fundamental unit of
    Z[(1 + sqrt p)/2]."""
    # convergents of w = (1 + sqrt p)/2: P/Q with the recurrence on (m, d, a) for (sqrt p + 1)/2
    s = math.isqrt(p)
    m, d = 1, 2  # w = (m + sqrt p)/d
    h0, h1 = 1, (m + s) // d
    k0, k1 = 0, 1
    a0 = h1
    while True:
        # with x = h1, y = k1 a convergent of w, the candidate unit is (2x - y) + y sqrt p, over 2
        x, y = h1, k1
        aa, bb = 2 * x - y, y
        if aa * aa - p * bb * bb in (4, -4):
            return aa, bb
        m = a0 * d - m
        d = (p - m * m) // d
        a0 = (m + s) // d
        h0, h1 = h1, a0 * h1 + h0
        k0, k1 = k1, a0 * k1 + k0


def reduced_forms(D: int) -> list[tuple[int, int, int]]:
    """The reduced indefinite forms (a, b, c), b^2 - 4ac = D: 0 < b < sqrt D and
    sqrt D - b < 2|a| < sqrt D + b."""
    r = math.sqrt(D)
    out = []
    for b in range(1, math.isqrt(D) + 1):
        if (b * b - D) % 4:
            continue
        ac = (b * b - D) // 4  # negative
        for a in sympy.divisors(-ac):
            if r - b < 2 * a < r + b:
                out += [(a, b, ac // a), (-a, b, ac // -a)]
    return out


def _rho(form, D):
    a, b, c = form
    r = math.sqrt(D)
    ac = abs(c)
    # b' = -b (mod 2c), with sqrt D - 2|c| < b' < sqrt D
    t = (-b) % (2 * ac)
    while t <= r - 2 * ac:
        t += 2 * ac
    while t >= r:
        t -= 2 * ac
    return (c, t, (t * t - D) // (4 * c))


def class_number(p: int) -> int:
    """The number of cycles of reduced forms of discriminant p (= h, as eps has norm -1)."""
    forms = set(reduced_forms(p))
    cycles, seen = 0, set()
    for f in forms:
        if f in seen:
            continue
        cycles += 1
        g = f
        while g not in seen:
            seen.add(g)
            g = _rho(g, p)
    return cycles


def class_number_analytic(p: int) -> float:
    """h from Dirichlet's formula: h log eps = -(1/2) sum chi(a) log sin(pi a / p)."""
    a, b = fundamental_unit(p)
    log_eps = math.log((a + b * math.sqrt(p)) / 2)
    s = sum(sympy.legendre_symbol(k, p) * math.log(math.sin(math.pi * k / p)) for k in range(1, p))
    return -s / (2 * log_eps)


def predicted(p: int) -> bool:
    """Fable's criterion: eps^h lies in Z[sqrt p]."""
    a, b = fundamental_unit(p)
    return (a % 2 == 0 and b % 2 == 0) or class_number(p) % 3 == 0


# ---------------------------------------------------------------- the truth (direct)


def _reduce_phi(r: int, p: int) -> int:
    """r, a polynomial mod x^p - 1 (as a p-bit int), reduced mod Phi_p = 1 + x + ... + x^(p-1)."""
    if r >> (p - 1) & 1:
        r ^= (1 << p) - 1
    return r


def confined(p: int) -> bool:
    """Is 1 + zeta a cube in F(2^(p-1)) = GF(2)[x]/Phi_p? Its norm to F(4) is the product of
    1 + x^(4^i) for i < (p - 1)/2, computed mod x^p - 1 and then mod Phi_p."""
    mask = (1 << p) - 1
    r = 1
    e = 1
    for _ in range((p - 1) // 2):
        rot = ((r << e) | (r >> (p - e))) & mask  # r * x^e mod x^p - 1
        r ^= rot
        e = e * 4 % p
    return _reduce_phi(r, p) == 1


# ---------------------------------------------------------------- the pyramid rules


def pyramid_rings(i: int) -> tuple[int, ...]:
    """Fable's recipe at p = i^2 + 1: the square rings at radii 2, 4, ..., i/2 - 1."""
    return tuple(range(2, i // 2, 2))


def pyramid(rings: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    R = max(rings) if rings else 0
    return frozenset({(0, 0)} | {(x, y) for x in range(-R, R + 1) for y in range(-R, R + 1)
                                 if max(abs(x), abs(y)) in rings})  # fmt: skip


def pyramid_primes(lo: int, hi: int) -> list[tuple[int, int]]:
    """(p, i): eligible primes p = i^2 + 1 with i = 2 (mod 4), lo <= p < hi."""
    out = []
    i = 2
    while i * i + 1 < hi:
        p = i * i + 1
        if p >= lo and sympy.isprime(p) and p in set(eligible(p, p + 1)):
            out.append((p, i))
        i += 4
    return out


def _cyclic_mul(a: np.ndarray, b: np.ndarray, p: int) -> np.ndarray:
    """Product mod (x^p - 1) over GF(2) of 0/1 arrays of length p, by an exact FFT convolution."""
    n = 1 << (2 * p - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(a.astype(np.float64), n) * np.fft.rfft(b.astype(np.float64), n), n)
    c = np.rint(c[: 2 * p - 1]).astype(np.int64)
    out = c[:p].copy()
    out[: p - 1] += c[p:]
    return (out & 1).astype(np.uint8)


def _frobenius(a: np.ndarray, k: int, p: int) -> np.ndarray:
    """a(x)^(2^k) = a(x^(2^k)) mod x^p - 1: a permutation of the coefficients."""
    out = np.zeros(p, dtype=np.uint8)
    idx = (np.arange(p) * pow(2, k, p)) % p
    np.bitwise_xor.at(out, idx, a)
    return out


def _is_one_mod_phi(a: np.ndarray) -> bool:
    """Is a (mod x^p - 1) equal to 1 mod Phi_p? Reduce by adding Phi_p (all ones) if the top
    coefficient is set."""
    r = a ^ 1 if a[-1] else a
    return bool(r[0] == 1 and not r[1:].any())


def _norm_is_one(v: np.ndarray, p: int) -> bool:
    """Is v (an element of GF(2)[x]/Phi_p, as a 0/1 array mod x^p - 1) a cube? Its norm to F(4)
    is the product of v^(4^i), i < (p - 1)/2, by repeated doubling of the Frobenius power."""
    k = (p - 1) // 2  # norm = prod_{i<k} v^(4^i) = v^((4^k - 1)/3)
    # binary method on the "exponent" sum of 4^i: N_k = N_j * Frob^{2j}(N_{k-j})
    result = None
    acc, acc_len = v.copy(), 1  # acc = prod_{i < acc_len} v^(4^i)
    done = 0
    for bit in bin(k)[2:]:
        if result is None:
            result, done = acc.copy(), 1
            continue
        result = _cyclic_mul(result, _frobenius(result, 2 * done, p), p)
        done *= 2
        if bit == "1":
            result = _cyclic_mul(result, _frobenius(v, 2 * done, p), p)
            done += 1
    assert done == k
    return _is_one_mod_phi(result)


def pyramid_confined(p: int, rings: tuple[int, ...]) -> bool:
    """Is every nonzero eigenvalue of the pyramid at p a cube? Its eigenvalue at (j, k) is the
    polynomial sum x^(j u + k w) over its terms, mod x^p - 1, read in GF(2)[x]/Phi_p. One
    character per orbit of Frobenius (doubling) and the D4 symmetry is enough."""
    f = pyramid(rings)
    seen = np.zeros((p, p), dtype=bool)
    for j in range(p):
        for k in range(j, p):
            if seen[j, k]:
                continue
            a, b = j, k
            for _ in range(p - 1):  # mark the Frobenius orbit, with the D4 images
                for u, w in ((a, b), (b, a), (-a % p, b), (b, -a % p), (a, -b % p),
                             (-b % p, a), (-a % p, -b % p), (-b % p, -a % p)):  # fmt: skip
                    seen[u, w] = True
                a, b = 2 * a % p, 2 * b % p
                if (a, b) == (j, k):
                    break
            v = np.zeros(p, dtype=np.uint8)
            for x, y in f:
                v[(x * j + y * k) % p] ^= 1
            if not v.any() or (v[-1] and not (v ^ 1).any()):  # zero mod Phi_p
                continue
            if not _norm_is_one(v, p):
                return False
    return True
