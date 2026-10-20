"""
Bivariate bicycle codes and the torus's group ring: the number of logical qubits, two ways.

A bivariate bicycle code (Bravyi et al. 2024) takes two polynomials A and B in
R = GF(2)[x, y] / (x^l - 1, y^m - 1), the group ring of the l x m torus: the ring this
repository's linear rules live in. Its checks are H_X = [A | B] and H_Z = [B^T | A^T], with A
and B acting on GF(2)^(lm) by multiplication (x shifts the first coordinate, y the second), so
n = 2lm and k = n - rank H_X - rank H_Z = 2 dim(ker A ∩ ker B).

- `k_linalg` computes the two ranks over GF(2), directly.
- `k_characters` reads k off the torus's characters, as this repository reads periods. Since
  R is commutative, ker A ∩ ker B is the annihilator of the ideal (A, B), and since a group ring
  is a Frobenius algebra, that annihilator has dimension dim R/(A, B). Over a field F holding the
  roots of unity needed, R splits over the l'm' characters χ of the torus's odd part
  (l = 2^a l', m = 2^b m', l' and m' odd) into the local rings L = F[s, t]/(s^(2^a) - 1,
  t^(2^b) - 1), with x -> χ(x) s and y -> χ(y) t. So

      k = 2 Σ_χ dim_F L / (A_χ, B_χ).

  At odd sizes L = F, and a term is 1 exactly when A and B both vanish at χ: k is twice the
  number of common zeros among the eigenvalues. At even sizes a term is the multiplicity of a
  common zero in the 2-part, which is what the library's even-size reduction is about.

Polynomials are lists of exponent pairs (p, q) for the monomials x^p y^q, reduced mod (l, m).
"""

from __future__ import annotations

import math
from functools import cache

# ---------------------------------------------------------------- GF(2) linear algebra


def _monomials(poly, ell, m) -> list[tuple[int, int]]:
    """The monomials of a GF(2) polynomial on the l x m torus (repeats cancel in pairs)."""
    out: set = set()
    for p, q in poly:
        out ^= {(p % ell, q % m)}
    return sorted(out)


def _matrix_rows(poly, ell, m, transpose=False) -> list[int]:
    """The lm x lm matrix of multiplication by poly over GF(2), one int bitmask per row; row
    (i, j) of A v is Σ v[(i - p, j - q)] over the monomials (p, q). Transposed: (i + p, j + q)."""
    mons = _monomials(poly, ell, m)
    sign = -1 if transpose else 1
    rows = []
    for i in range(ell):
        for j in range(m):
            r = 0
            for p, q in mons:
                r ^= 1 << (((i - sign * p) % ell) * m + (j - sign * q) % m)
            rows.append(r)
    return rows


def rank_gf2(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    rank = 0
    for r in rows:
        while r:
            top = r.bit_length() - 1
            if top in pivots:
                r ^= pivots[top]
            else:
                pivots[top] = r
                rank += 1
                break
    return rank


def k_linalg(A, B, ell: int, m: int) -> int:
    n = 2 * ell * m
    lm = ell * m
    a_rows, b_rows = _matrix_rows(A, ell, m), _matrix_rows(B, ell, m)
    a_cols, b_cols = _matrix_rows(A, ell, m, True), _matrix_rows(B, ell, m, True)
    hx = [a | (b << lm) for a, b in zip(a_rows, b_rows, strict=True)]
    hz = [b | (a << lm) for a, b in zip(a_cols, b_cols, strict=True)]
    return n - rank_gf2(hx) - rank_gf2(hz)


# ---------------------------------------------------------------- the field F(2^d)


def _deg(a: int) -> int:
    return a.bit_length() - 1


def _pmod(a: int, p: int) -> int:
    dp = _deg(p)
    while a and _deg(a) >= dp:
        a ^= p << (_deg(a) - dp)
    return a


def _irreducible(d: int) -> int:
    """The smallest irreducible polynomial of degree d over GF(2), by trial division."""
    for p in range((1 << d) | 1, 1 << (d + 1), 2):
        if all(_pmod(p, f) for f in range(2, 1 << (d // 2 + 1)) if _deg(f) >= 1):
            return p
    raise ValueError(d)


class Field:
    """F(2^d) with d = ord_N(2), and a primitive N-th root of unity zeta (N odd)."""

    def __init__(self, N: int):
        self.N = N
        self.d = 1 if N == 1 else next(d for d in range(1, N + 1) if pow(2, d, N) == 1)
        self.poly = _irreducible(self.d) if self.d > 1 else 0b10
        self.order = (1 << self.d) - 1
        primes = [p for p in range(2, N + 1) if N % p == 0 and all(p % r for r in range(2, p))]
        for g in range(2, 1 << self.d) if self.d > 1 else [1]:
            z = self.pow(g, self.order // N)
            if all(self.pow(z, N // p) != 1 for p in primes):
                self.zeta = z
                break

    def mul(self, a: int, b: int) -> int:
        if self.d == 1:
            return a & b
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.d & 1:
                a ^= self.poly
        return r

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        return self.pow(a, self.order - 1)


def rank_field(F: Field, rows: list[list[int]]) -> int:
    rows = [list(r) for r in rows]
    rank, cols = 0, len(rows[0]) if rows else 0
    for c in range(cols):
        piv = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = F.inv(rows[rank][c])
        rows[rank] = [F.mul(inv, v) for v in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][c]:
                f = rows[i][c]
                rows[i] = [v ^ F.mul(f, w) for v, w in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


# ---------------------------------------------------------------- k from the characters


def two_part(n: int) -> tuple[int, int]:
    """n = 2^a n' with n' odd: (2^a, n')."""
    t = n & -n
    return t, n // t


@cache
def _field(N: int) -> Field:
    return Field(N)


def local_terms(A, B, ell: int, m: int) -> list[tuple[tuple[int, int], int]]:
    """(character, dim L/(A_χ, B_χ)) for each character χ = (j, k) of the odd part with a
    nonzero term; the characters are ζ^(j N/l') on x and ζ^(k N/m') on y, N = lcm(l', m')."""
    (sa, lo), (sb, mo) = two_part(ell), two_part(m)
    N = math.lcm(lo, mo)
    F = _field(N)
    roots = [F.pow(F.zeta, e) for e in range(N)]
    mons_a, mons_b = _monomials(A, ell, m), _monomials(B, ell, m)
    size = sa * sb
    out = []
    for j in range(lo):
        for k in range(mo):

            def local(mons, j=j, k=k):
                # A_χ in the basis s^i t^u of L (s^sa = 1, t^sb = 1): the coefficient of
                # s^(p mod sa) t^(q mod sb) gains χ(x)^p χ(y)^q
                v = [0] * size
                for p, q in mons:
                    e = (j * (N // lo) * p + k * (N // mo) * q) % N
                    v[(p % sa) * sb + q % sb] ^= roots[e]
                return v

            def shifts(v):
                # v times every monomial s^i t^u: a cyclic shift of the coefficients
                for i in range(sa):
                    for u in range(sb):
                        w = [0] * size
                        for idx, c in enumerate(v):
                            if c:
                                w[((idx // sb + i) % sa) * sb + (idx % sb + u) % sb] = c
                        yield w

            gens = list(shifts(local(mons_a))) + list(shifts(local(mons_b)))
            term = size - rank_field(F, gens)
            if term:
                out.append(((j, k), term))
    return out


def k_characters(A, B, ell: int, m: int) -> int:
    return 2 * sum(t for _, t in local_terms(A, B, ell, m))


def pi_poly(exponents) -> list[tuple[int, int]]:
    """A polynomial in π = xy (the coprime codes): π^e = x^e y^e."""
    return [(e, e) for e in exponents]
