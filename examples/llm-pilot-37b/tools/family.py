"""
The symmetric square rules within distance 4: every union of D4 orbits of the translations with
coordinates in [-4, 4]. There are 15 orbits, (0, 0) (the cell itself) included, so 2^15 - 1 =
32,767 nonempty rules; a rule's id is its bit mask over ORBITS. The atlas's 1,022 square rules
are among them.

    ORBITS                 the 15 orbit representatives (a, b), 0 <= b <= a <= 4
    orbit(a, b)            the orbit's translations
    rule(bits)             the polynomial of rule `bits`, a frozenset of exponent pairs
    orbits_of(bits)        its orbit representatives
    rules()                (bits, polynomial) for every rule
"""

from __future__ import annotations

import functools
import itertools

ORBITS = sorted({tuple(sorted((abs(a), abs(b)), reverse=True))
                 for a, b in itertools.product(range(-4, 5), repeat=2)})  # fmt: skip


def orbit(a: int, b: int) -> frozenset:
    return frozenset((s * x, t * y) for x, y in ((a, b), (b, a)) for s in (1, -1) for t in (1, -1))


def orbits_of(bits: int) -> list[tuple[int, int]]:
    return [o for i, o in enumerate(ORBITS) if bits >> i & 1]


@functools.cache
def rule(bits: int) -> frozenset:
    return frozenset().union(*(orbit(*o) for o in orbits_of(bits)))


def bits_of(orbits) -> int:
    return sum(1 << ORBITS.index(tuple(o)) for o in orbits)


def rules():
    for bits in range(1, 2 ** len(ORBITS)):
        yield bits, rule(bits)
