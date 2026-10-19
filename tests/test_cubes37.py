"""The fourth LLM pilot's answer for m = 37 (examples/llm-pilot-37): the half-Frobenius identities,
checked with the atlas's own polynomials rather than the agent's code, and the census's six rules
against eigen.py."""

import sys
from collections import Counter
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "llm-pilot-37"
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402


def mul(a, b):
    counts = Counter((p[0] + q[0], p[1] + q[1]) for p in a for q in b)
    return frozenset(k for k, v in counts.items() if v % 2)


def dilate(a, r):
    return frozenset((r * x, r * y) for x, y in a)


def t(w):
    return frozenset({w, (-w[0], -w[1])})


def square(*shells):
    return frozenset(atlas3.polynomial("square", shells))


ONE = frozenset({(0, 0)})
A, B = t((1, 0)), t((0, 1))
W = square("A4", "K8", "B4", "self")
SHELL75 = frozenset(
    {(sx * p, sy * q) for p, q in ((7, 5), (5, 7)) for sx in (1, -1) for sy in (1, -1)}
)


def test_w_at_x_squared_times_four_rule_90_passes_is_a_shell():
    left = mul(mul(mul(mul(dilate(W, 2), A), B), t((1, 1))), t((1, -1)))
    assert left == SHELL75


def test_three_of_the_six_are_w_times_rule_90_products():
    assert square("K8", "M8", "E4") == mul(mul(A, B), W)
    assert square("C4", "L8", "M8") == mul(A ^ B, W)
    assert square("A4", "B4", "C4", "L8", "E4", "self") == mul(mul(A ^ ONE, B ^ ONE), W)


def test_the_shell_is_invariant_under_the_half_frobenius_at_37():
    m = 37
    assert pow(2, 9, m) == m - 6 and (6 * 6) % m == m - 1

    def reduce(s):
        return frozenset((x % m, y % m) for x, y in s)

    assert reduce(dilate(SHELL75, 6)) == reduce(SHELL75)
    assert eigen.odd_part(SHELL75, m) == 2**9 - 1


def test_the_six_have_rule_90s_period_at_37():
    six = [square("A4", "K8", "B4", "self"), square("K8", "M8", "E4"), square("C4", "L8", "M8"),
           square("C4", "L8", "M8", "E4"), square("A4", "B4", "C4", "L8", "E4", "self"),
           frozenset(atlas3.polynomial("triangle", ("VS", "T9", "T13", "self")))]  # fmt: skip
    assert all(eigen.odd_part(f, 37) == 87381 == (2**18 - 1) // 3 for f in six)


def test_the_held_out_census_ledger_is_intact():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
