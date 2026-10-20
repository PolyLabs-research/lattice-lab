"""Pilot 7's explanation of four of the five ninth-power rules at m = 37, rechecked by the
orchestrator: the exact factorisations into line units times the fourth pilot's half-Frobenius
cores, the cores' identities, the dilation at 37 that puts their right sides in F(2^9), and the
exponent of the Psi_5 unit that lifts the units from cubes to ninth powers."""

import sys
from collections import Counter
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "rule-4850"))

import census  # noqa: E402

ONE = frozenset({(0, 0)})


def mul(*fs: frozenset) -> frozenset:
    def two(f, g):
        c = Counter((p + r, q + s) for p, q in f for r, s in g)
        return frozenset(k for k, v in c.items() if v % 2)

    return reduce(two, fs, ONE)


def add(*fs: frozenset) -> frozenset:
    return reduce(frozenset.symmetric_difference, fs, frozenset())


def shells(*orbits) -> frozenset:
    return add(*(frozenset(census.points(o)) for o in orbits))


def scale(f: frozenset, r: int) -> frozenset:
    return frozenset((r * p, r * q) for p, q in f)


def t(w) -> frozenset:
    return frozenset({w, (-w[0], -w[1])})


A, B = t((1, 0)), t((0, 1))
PSI5 = mul(add(mul(A, A), A, ONE), add(mul(B, B), B, ONE))  # Psi_5(a) Psi_5(b), Psi_5 = t^2+t+1
W = shells((0, 0), (2, 0), (2, 1), (2, 2))  # A4 + K8 + B4 + self
V = shells((3, 0), (3, 1), (3, 2), (3, 3))  # C4 + L8 + M8 + E4


def test_the_four_radius_5_rules_are_line_units_times_a_core():
    assert mul(PSI5, add(A, B), W) == census.rule(699738)
    assert mul(A, A, B, B, add(A, B), W) == census.rule(985232)
    assert mul(PSI5, V) == census.rule(1431278)
    assert mul(A, A, B, B, V) == census.rule(1968276)


def test_the_cores_half_frobenius_identities_hold_exactly():
    rule90 = mul(t((1, 0)), t((0, 1)))
    assert mul(scale(W, 2), rule90, t((1, 1)), t((1, -1))) == shells((7, 5))
    assert mul(scale(V, 2), rule90) == shells((7, 7), (5, 5))


def test_at_37_the_right_sides_are_fixed_by_the_frobenius_of_f_2_9():
    m = 37
    assert pow(2, 9, m) == m - 6 and 6 * 6 % m == m - 1
    for right in (shells((7, 5)), shells((7, 7), (5, 5))):
        support = {(p % m, q % m) for p, q in right}
        assert {(6 * p % m, 6 * q % m) for p, q in support} == support


def test_psi_5_of_a_rule_90_value_is_a_power_with_exponent_2_23_minus_1():
    """Psi_5(t)^2 = t^(2^23 - 1) for every nonzero rule-90 value t at 37, since 5 = 2^23 mod 37;
    the net exponent 2^23 - 2 of Psi_5(t)^2 / t has 3-adic valuation exactly 1."""
    assert pow(2, 23, 37) == 5
    for j in range(1, 37):
        v = census.power(2, j) ^ census.power(2, 37 - j)
        psi = census.mul(v, v) ^ v ^ 1
        assert census.mul(psi, psi) == census.power(v, 2**23 - 1)
    assert (2**23 - 2) % 3 == 0 and (2**23 - 2) % 9
