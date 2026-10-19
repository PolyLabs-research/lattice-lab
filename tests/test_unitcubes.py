"""The sixth LLM pilot's answer (examples/llm-pilot-37b): nine square-family rules are a unit times
a cube, checked with the orchestrator's own arithmetic rather than the agent's code; their odd
parts at 37 and 61 against eigen.py; and the held-out census's ledger."""

import json
import sys
from collections import Counter
from pathlib import Path

from lattice_lab.ledger import Ledger, check_order

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "llm-pilot-37b"
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402


def mul(a, b):
    counts = Counter((p[0] + q[0], p[1] + q[1]) for p in a for q in b)
    return frozenset(k for k, v in counts.items() if v % 2)


def add(*polys):
    counts = Counter(k for f in polys for k in f)
    return frozenset(k for k, v in counts.items() if v % 2)


def orbit(a, b):
    signs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    return frozenset((sx * p, sy * q) for p, q in ((a, b), (b, a)) for sx, sy in signs)


def family(bits):
    """The square family's rule with this id: the union of the D4 orbits its bits select."""
    orbits = sorted({(a, b) for a in range(5) for b in range(a + 1)})
    return add(*(orbit(*o) for i, o in enumerate(orbits) if bits >> i & 1))


def square(*shells):
    return frozenset(atlas3.polynomial("square", shells))


ONE = frozenset({(0, 0)})
A = frozenset({(1, 0), (-1, 0)})  # a = x + 1/x
B = frozenset({(0, 1), (0, -1)})  # b = y + 1/y
UNITS = {"a+b": add(A, B), "ab": mul(A, B), "(a+1)(b+1)": mul(add(A, ONE), add(B, ONE))}
CUBED = {
    "N4+self": square("N4", "self"),
    "D4+self": square("D4", "self"),
    "N4+D4": square("N4", "D4"),
}
NINE = {
    ("a+b", "N4+self"): 1112, ("a+b", "D4+self"): 10498, ("a+b", "N4+D4"): 13584,
    ("ab", "N4+self"): 2436, ("ab", "D4+self"): 17056, ("ab", "N4+D4"): 28944,
    ("(a+1)(b+1)", "N4+self"): 3461, ("(a+1)(b+1)", "D4+self"): 26883,
    ("(a+1)(b+1)", "N4+D4"): 18246,
}  # fmt: skip


def test_the_cubed_factors_are_the_bidegree_one_non_units():
    assert CUBED["N4+self"] == add(A, B, ONE)
    assert CUBED["D4+self"] == add(mul(A, B), ONE)
    assert CUBED["N4+D4"] == add(mul(A, B), A, B)


def test_nine_family_rules_are_a_unit_times_a_cube():
    for (u, g), rid in NINE.items():
        c = CUBED[g]
        assert family(rid) == mul(UNITS[u], mul(c, mul(c, c)))


def test_the_nine_are_cubes_at_37():
    assert eigen.odd_part(frozenset({(1, 0), (-1, 0)}), 37) == 87381  # rule 90, confined
    assert all(87381 % eigen.odd_part(family(rid), 37) == 0 for rid in NINE.values())


def test_only_the_unit_a_plus_one_b_plus_one_survives_at_61():
    # rule 90 is not confined at 61, but 3 = 2^6 makes (t + 1)^2 = t^63 a cube
    assert pow(2, 6, 61) == 3 and eigen.odd_part(frozenset({(1, 0), (-1, 0)}), 61) == 2**30 - 1
    cubes = (2**30 - 1) // 3
    for (u, _), rid in NINE.items():
        confined = cubes % eigen.odd_part(family(rid), 61) == 0
        assert confined == (u == "(a+1)(b+1)")


def test_the_held_out_census_found_exactly_the_nine_beyond_known_mechanisms():
    rows = [json.loads(line) for line in (LAB / "records.jsonl").read_text().splitlines()]
    assert len(rows) == 17
    for r in rows:
        unexplained = {h["id"] for h in r["hits"]
                       if h["known_q"] % 3 and not h["procedure"].startswith("splits")}  # fmt: skip
        assert unexplained == (set(NINE.values()) if r["m"] in (95, 101, 111) else set())


def test_the_held_out_census_ledger_is_intact():
    ledger = Ledger(LAB / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
