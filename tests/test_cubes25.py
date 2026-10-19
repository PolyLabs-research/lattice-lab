"""The fifth LLM pilot's answer for m = 25 (examples/llm-pilot-25): its cube certificates and
twisted pairs, checked with the orchestrator's own arithmetic rather than the agent's code, the
five rules against eigen.py, and the held-out census's ledger."""

import sys
from collections import Counter
from math import gcd
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "llm-pilot-25"
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402


def mul(a, b):
    counts = Counter((p[0] + q[0], p[1] + q[1]) for p in a for q in b)
    return frozenset(k for k, v in counts.items() if v % 2)


def add(*polys):
    counts = Counter(k for f in polys for k in f)
    return frozenset(k for k, v in counts.items() if v % 2)


def dilate(a, r):
    return frozenset((r * x, r * y) for x, y in a)


def reduce(a, m):
    counts = Counter((x % m, y % m) for x, y in a)
    return frozenset(k for k, v in counts.items() if v % 2)


def orbit(a, b):
    signs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    return frozenset((sx * p, sy * q) for p, q in ((a, b), (b, a)) for sx, sy in signs)


def family(*orbits):
    return add(*(orbit(a, b) for a, b in orbits))


def square(*shells):
    return frozenset(atlas3.polynomial("square", shells))


T = mul(frozenset({(1, 0), (-1, 0)}), frozenset({(0, 1), (0, -1)}))  # rule 90 along x times along y
R3096 = family((2, 0), (2, 1), (4, 0), (4, 1))
R23608 = family((2, 0), (2, 1), (2, 2), (4, 0), (4, 1), (4, 2), (4, 4))
CERTIFICATES = {
    "3096": (R3096, family((3, 1), (4, 1), (7, 1), (7, 3), (7, 4))),
    "23608": (R23608, family((1, 1), (3, 1), (4, 1), (7, 3), (7, 4), (7, 7))),
}
R32184 = family((2, 0), (2, 1), (2, 2), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4))
PAIRS = {
    "1227": (family((0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (4, 0)), square("N4", "self")),
    "21029": (family((0, 0), (1, 1), (2, 2), (3, 3), (4, 2), (4, 4)), square("D4", "self")),
    "32184": (R32184, square("N4", "D4")),
}


def test_the_cube_certificates_hold_exactly():
    for f, b in CERTIFICATES.values():
        assert mul(f, mul(T, mul(T, T))) == b


def test_the_certificates_are_invariant_under_the_half_frobenius_at_25():
    m = 25
    assert pow(2, 5, m) == 7 and 7 * 7 % m == m - 1 and (2**5 - 1) % 3
    for _, b in CERTIFICATES.values():
        assert reduce(dilate(b, 7), m) == reduce(b, m)


def test_on_the_axes_the_certificates_rules_are_t_times_t_of_z_cubed():
    # f(1, z) = t^2 (t + 1)^2 = t(z) t(z^3), and z^3 + z^-3 = t^(2^7) at 25
    t = frozenset({1, -1})
    one = frozenset({0})

    def mul1(a, b):
        return frozenset(k for k, v in Counter(p + q for p in a for q in b).items() if v % 2)

    target = mul1(mul1(t, t), mul1(t ^ one, t ^ one))
    for f, _ in CERTIFICATES.values():
        line = frozenset(k for k, v in Counter(b for _, b in f).items() if v % 2)
        assert line == target == mul1(t, frozenset({3, -3}))
    assert pow(2, 7, 25) == 3


def test_three_rules_are_twisted_pairs():
    for f, c in PAIRS.values():
        assert f == mul(c, dilate(c, 3))


def test_the_five_are_cubes_at_25():
    rules = [f for f, _ in CERTIFICATES.values()] + [f for f, _ in PAIRS.values()]
    assert all(341 % eigen.odd_part(f, 25) == 0 for f in rules)


def test_the_twisted_pairs_are_cubes_where_three_is_two_to_an_odd_power():
    # the held-out census found exactly these three at 35, 53 and 55 (and at 29)
    for m in (29, 35, 53, 55):
        k = next(k for k in range(1, m) if pow(2, k, m) in (3, m - 3))
        assert k % 2 == 1
        s = next(j for j in range(1, m) if pow(2, j, m) in (1, m - 1))
        cubes = (2**s - 1) // 3
        for f, _ in PAIRS.values():
            assert gcd(eigen.odd_part(f, m), 2**s - 1) == eigen.odd_part(f, m)
            assert cubes % eigen.odd_part(f, m) == 0


def test_the_held_out_census_ledger_is_intact():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
