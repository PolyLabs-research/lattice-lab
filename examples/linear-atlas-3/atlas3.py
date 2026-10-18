"""
Round 3 of the linear-rule atlas: the refined statement, as a procedure, on new rules.

Round 2 (examples/linear-atlas-2) refuted the factorisation pattern. Its failures pointed to a
sharper statement: a rule's period reaches the full bound unless something confines its
eigenvalues. Here that statement is a procedure, `predict(f, m)`, which takes the rule's polynomial
f and an odd m and returns the odd part of the rule's period on a torus whose odd part is m. On
the triangle, f is s, where the rule's matrix squares to s I. The steps are tried in order:

0. **Wrapping.** If two of f's exponents agree modulo m, f is not faithful on (Z/m)^2: no
   prediction.
1. **Zero, or a monomial.** f = 0 dies (1); x^a y^b has the order of (a, b) in (Z/m)^2.
2. **Dilation.** If every exponent is divisible by a prime p, then f = h(x^p, y^p). The answer is
   predict(h, m / p) if p divides m, and predict(h, m) if not.
3. **Odd prime power.** If f = g^k for an odd prime k, the answer is q / gcd(q, k), where
   q = predict(g, m).
4. **Splits completely into one kind of 1D factor g.** The period of the symmetric 1D rule made
   from g on m cells (`atlas2.p_1d`): rule 90's for g = 1 + u, rule 150's for 1 + u + u^2.
5. **Splits into factors of more than one kind.** No prediction.
6. **Otherwise: the full bound.** 2^sord(m) - 1 if f is symmetric under (x, y) -> (1/x, 1/y),
   and 2^ord(m) - 1 if not.

Steps 1 to 3 are theorems, given a correct answer for h or g. Steps 4 and 6 are the conjecture.

Why the odd part suffices: F2[T] modulo its radical is F2[T_odd], and T_odd = (Z/m)^2 on all three
tori here. So the odd part of the period at n is the period at the odd part m, and each m needs
testing only once: n = m on the square, n = 2m on the hexagon and the triangle.
"""

from __future__ import annotations

import functools
import itertools
import math
import random
import sys
from pathlib import Path

import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "linear-atlas-2"))
sys.path.insert(0, str(ROOT / "linear-atlas"))

import atlas2  # noqa: E402
import engine  # noqa: E402
import factor  # noqa: E402
from lattices import AXIAL_STEPS, GroupRing, Matrix, _tau  # noqa: E402

_pm = engine._pm

SQUARE = {
    **atlas2.SQUARE,
    "L8": _pm((1, 3), (3, 1), (1, -3), (3, -1)),
    "M8": _pm((2, 3), (3, 2), (2, -3), (3, -2)),
    "E4": _pm((3, 3), (3, -3)),
}
HEXAGON = {
    **engine.HEXAGON_SHELLS,
    "H4": _pm((2, 1), (1, 2), (3, -1), (3, -2), (1, -3), (2, -3)),
    "H5": _pm((3, 0), (0, 3), (3, -3)),
    "H13": _pm((3, 1), (1, 3), (4, -1), (4, -3), (1, -4), (3, -4)),
}
TRIANGLE = {
    **engine.TRIANGLE_SHELLS,
    "T7": {
        "up": ((-1, -2), (-1, 2), (0, -3), (0, 3), (2, -1), (2, 1)),
        "down": ((-2, -1), (-2, 1), (0, -3), (0, 3), (1, -2), (1, 2)),
    },
    "T9": {
        "up": ((-2, 0), (-1, -3), (-1, 3), (1, -3), (1, 3), (2, 0)),
        "down": ((-2, 0), (-1, -3), (-1, 3), (1, -3), (1, 3), (2, 0)),
    },
    "T13": {
        "up": ((-2, -1), (-2, 1), (1, -4), (1, 4), (2, -3), (2, 3)),
        "down": ((-2, -3), (-2, 3), (-1, -4), (-1, 4), (2, -1), (2, 1)),
    },
}
SHELLS = {"square": SQUARE, "hexagon": HEXAGON, "triangle": TRIANGLE}
NEW = {
    "square": ("L8", "M8", "E4"),
    "hexagon": ("H4", "H5", "H13"),
    "triangle": ("T7", "T9", "T13"),
}

# Odd parts tested: every odd m from 9 to 61, and those from 63 to 141 where rule 90's or rule
# 150's period differs from the full bound. Below 9 the widest shells would wrap onto themselves.
SIZES = list(range(9, 62, 2)) + [m for m in range(63, 142, 2) if atlas2.decisive(m)]


def name(lattice: str, shells: tuple[str, ...]) -> str:
    return f"{lattice} {'+'.join(shells)}"


def all_rules(lattice: str) -> list[tuple[str, ...]]:
    names = list(SHELLS[lattice])
    out = []
    for r in range(1, len(names) + 1):
        for combo in itertools.combinations(names, r):
            out += [combo, (*combo, "self")]
    return out


# --- polynomials -------------------------------------------------------------------------------


def _triangle_entries(shells: tuple[str, ...]):
    """The 2 x 2 matrix's entries as plane polynomials, as engine.build lays them out."""
    uu, ud, du, dd = set(), set(), set(), set()
    for shell in shells:
        if shell == "self":
            uu ^= {(0, 0)}
            dd ^= {(0, 0)}
            continue
        for dr, dc in TRIANGLE[shell]["up"]:
            if (dr + dc) % 2 == 0:
                i, j = _tau(dr, dc)
                uu ^= {(-i, -j)}
            else:
                i, j = _tau(dr, dc - 1)
                ud ^= {(-i, -j)}
        for dr, dc in TRIANGLE[shell]["down"]:
            if (dr + dc) % 2 == 0:
                i, j = _tau(dr, dc)
                dd ^= {(-i, -j)}
            else:
                i, j = _tau(dr, dc + 1)
                du ^= {(-i, -j)}
    return uu, ud, du, dd


def polynomial(lattice: str, shells: tuple[str, ...]) -> frozenset:
    """f for the square and hexagon; s, with M^2 = s I, for the triangle."""
    if lattice == "triangle":
        uu, ud, du, dd = _triangle_entries(shells)
        t = factor._times
        a, b = t(uu, uu) ^ t(ud, du), t(uu, ud) ^ t(ud, dd)
        c, d = t(du, uu) ^ t(dd, du), t(du, ud) ^ t(dd, dd)
        if b or c or a != d:
            raise ArithmeticError(f"{name(lattice, shells)}: M^2 is not scalar")
        return frozenset(a)
    terms: set = set()
    for shell in shells:
        terms ^= {(0, 0)} if shell == "self" else set(SHELLS[lattice][shell])
    return frozenset(terms)


def build(lattice: str, shells: tuple[str, ...], n: int) -> tuple[GroupRing, Matrix]:
    """engine.build, with this round's shells."""
    if lattice == "triangle":
        ring = GroupRing((n // 2, -(n // 2)), (n // 2, n // 2))
        entries = []
        for part in _triangle_entries(shells):
            e = ring.zero()
            for i, j in part:
                e[ring.index(i, j)] += 1
            entries.append(e % 2)
        uu, ud, du, dd = entries
        return ring, Matrix(ring, [[uu, ud], [du, dd]])
    ring = GroupRing((n, 0), (0, n)) if lattice == "square" else GroupRing((n, -(n // 2)), (0, n))
    poly = ring.zero()
    for i, j in polynomial(lattice, shells):
        poly[ring.index(i, j)] += 1
    return ring, Matrix(ring, [[poly % 2]])


def size(lattice: str, m: int) -> int:
    return m if lattice == "square" else 2 * m


# --- the procedure -----------------------------------------------------------------------------


def _symmetric(f: frozenset) -> bool:
    return f == frozenset((-i, -j) for i, j in f)


def _kronecker(f: frozenset) -> tuple[sympy.Poly, int, int, int]:
    i0, j0 = min(i for i, _ in f), min(j for _, j in f)
    base = max(i for i, _ in f) - i0 + 1
    x = sympy.Symbol("x")
    poly = sympy.Poly(sum(x ** ((i - i0) + base * (j - j0)) for i, j in f), x, modulus=2)
    return poly, i0, j0, base


@functools.cache
def root(f: frozenset, k: int) -> frozenset | None:
    """g with g^k = f, if there is one. f(x, x^B) is factored over GF(2); f is a k-th power
    exactly when every multiplicity is divisible by k, and then g is read back off the digits in
    base B and checked."""
    if len(f) < 2:
        return None
    poly, i0, j0, base = _kronecker(f)
    _, factors = poly.factor_list()
    if not factors or any(e % k for _, e in factors):
        return None
    g = sympy.Poly(1, poly.gens[0], modulus=2)
    for p, e in factors:
        g *= p ** (e // k)
    terms = set()
    for (power,), coeff in g.terms():
        if int(coeff) % 2:
            j, i = divmod(power, base)
            terms.add((i, j))
    if not terms:
        return None
    # g's exponents are known up to a shift: put its lowest corner at (i0, j0) / k
    if i0 % k or j0 % k:
        return None
    candidate = frozenset((i + i0 // k, j + j0 // k) for i, j in terms)
    cube = {(0, 0)}
    for _ in range(k):
        cube = factor._times(cube, set(candidate))
    return candidate if frozenset(cube) == f else None


def _order(a: int, b: int, m: int) -> int:
    return m // math.gcd(a, b, m)


@functools.cache
def predict(f: frozenset, m: int) -> tuple[int | None, str]:
    """The odd part of the period at odd part m, and the step that decided it."""
    if not f:
        return 1, "zero"
    if len({(i % m, j % m) for i, j in f}) < len(f):
        return None, f"wraps at {m}"
    if len(f) == 1:
        ((a, b),) = f
        return _order(a, b, m), "monomial"
    g = math.gcd(*(c for e in f for c in e))
    for p in sympy.primefactors(g):
        h = frozenset((i // p, j // p) for i, j in f)
        value, why = predict(h, m // p) if m % p == 0 else predict(h, m)
        return value, f"dilation by {p}{' (p | m)' if m % p == 0 else ''}; {why}"
    for k in (3, 5, 7):
        g = root(f, k)
        if g is not None:
            q, why = predict(g, m)
            return (None if q is None else q // math.gcd(q, k)), f"power {k}; {why}"
    result = factor.split(set(f))
    types = {tuple(x["g"]) for x in result["factors"]}
    if result["splits"]:
        if len(types) == 1:
            (g1,) = types
            return atlas2.p_1d(g1, m), f"splits into {factor._name(g1)}"
        return None, "splits into mixed factors"
    order = atlas2.sord(m) if _symmetric(f) else int(sympy.n_order(2, m))
    return 2**order - 1, "full bound" + ("" if _symmetric(f) else " (ord: not symmetric)")


# --- the exact check of an odd part ------------------------------------------------------------


class OddExact:
    """The odd part of a rule's period, checked exactly. N = M^(2^E), with 2^E the 2-part of
    engine.bound's C, has period the odd part of M's on the late states; the odd part is then
    checked as atlas2.Exact checks a period, with C's odd part as the bound."""

    def __init__(self, lattice: str, shells: tuple[str, ...], n: int):
        _, M = build(lattice, shells, n)
        self.late = M.power(4 * n)
        C, primes = engine.bound(lattice, n)
        E = (C & -C).bit_length() - 1
        self.N = M.power(2**E)
        self.C, self.primes = C >> E, [q for q in primes if q != 2]

    def _fixes(self, X: Matrix) -> bool:
        return self.late * X == self.late

    def _proper(self, X: Matrix, primes: list[int]) -> int | None:
        if len(primes) == 1:
            return primes[0] if self._fixes(X) else None
        half = len(primes) // 2
        left, right = primes[:half], primes[half:]
        return self._proper(X.power(math.prod(right)), left) or self._proper(
            X.power(math.prod(left)), right
        )

    def check(self, predicted: int) -> dict:
        if self.late.is_zero():
            return {"is_odd_part": predicted == 1, "reason": "the torus dies: period 1"}
        if predicted < 1 or self.C % predicted:
            return {"is_odd_part": False, "reason": "does not divide the bound's odd part"}
        if not self._fixes(self.N.power(predicted)):
            return {"is_odd_part": False, "reason": "N does not repeat after it"}
        primes = [q for q in self.primes if predicted % q == 0]
        if primes:
            q = self._proper(self.N.power(predicted // math.prod(primes)), primes)
            if q is not None:
                return {"is_odd_part": False, "reason": f"N already repeats after predicted / {q}"}
        return {"is_odd_part": True, "reason": "repeats, and at no proper divisor"}

    def odd_part(self) -> int:
        if self.late.is_zero():
            return 1
        p = self.C
        if not self._fixes(self.N.power(p)):
            raise ArithmeticError("bound fails")
        for q in self.primes:
            while p % q == 0 and self._fixes(self.N.power(p // q)):
                p //= q
        return p


# --- which rules -------------------------------------------------------------------------------

SAMPLE_SEED, SAMPLE_SIZE = 3, 100


def new_rules(lattice: str) -> list[tuple[str, ...]]:
    """Every rule using a new shell. On the square there are 896, so this keeps all the rules
    whose call is not the full bound, and a random sample (seed 3) of 100 of the others."""
    rules = [r for r in all_rules(lattice) if set(r) & set(NEW[lattice])]
    if lattice != "square":
        return rules
    full = [r for r in rules if predict(polynomial(lattice, r), 9)[1] == "full bound"]
    other = [r for r in rules if r not in set(full)]
    return other + sorted(random.Random(SAMPLE_SEED).sample(full, SAMPLE_SIZE))


def _sanity() -> None:
    assert AXIAL_STEPS
    assert polynomial("hexagon", ("H5",)) == frozenset((3 * i, 3 * j) for i, j in AXIAL_STEPS)
