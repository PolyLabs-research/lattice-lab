"""Parity rules on the hexagonal and triangular lattices (examples/parity-lattices and
examples/parity-lattices-hexagon): the exact engine agrees with LatticeLife, two hexagon
generations are three passes of rule 90, and the ledgers hold the verdicts the write-up reports."""

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from lattice_lab.ledger import Ledger, check_order

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
ROUND_1 = EXAMPLES / "parity-lattices"
ROUND_2 = EXAMPLES / "parity-lattices-hexagon"
sys.path.insert(0, str(ROUND_1))
sys.path.insert(0, str(EXAMPLES / "xor-periods-algebra"))

import algebra  # noqa: E402
import lattices  # noqa: E402


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def _laurent_mul(a: Counter, b: Counter) -> Counter:
    out = Counter()
    for (i, j), x in a.items():
        for (k, m), y in b.items():
            out[i + k, j + m] += x * y
    return Counter({e: 1 for e, c in out.items() if c % 2})


def test_two_hexagon_steps_are_three_rule_90_passes_as_polynomials():
    """sigma(x, y)^2 = (x + 1/x)(y + 1/y)(x/y + y/x) over F2."""
    sigma = Counter({step: 1 for step in lattices.AXIAL_STEPS})
    cx, cy = Counter({(1, 0): 1, (-1, 0): 1}), Counter({(0, 1): 1, (0, -1): 1})
    cxy = Counter({(1, -1): 1, (-1, 1): 1})
    assert _laurent_mul(sigma, sigma) == _laurent_mul(_laurent_mul(cx, cy), cxy)


@pytest.mark.parametrize("n", [8, 10, 12])
def test_two_hexagon_steps_are_three_rule_90_passes_in_latticelife(n):
    from latticelife.config import DEFAULT_CONFIG_PATH, load_config
    from latticelife.core.rules import Rule
    from latticelife.experiments.harness import single_species_session

    config = load_config(DEFAULT_CONFIG_PATH)
    session = single_species_session(config, Rule.from_bs_string("B135/S135"), "hexagon", n, 0.5, 7)
    start = session.grid.occupancy.copy()
    session.step()
    session.step()
    ring, _ = lattices.hexagon(n)
    state = ring.zero()
    for cell in np.flatnonzero(start):
        r, c = divmod(int(cell), n)  # LatticeLife's index r * width + c, odd-q offset columns
        state[ring.index(c, r - c // 2)] = 1
    for i, j in ((1, 0), (0, 1), (1, -1)):  # rule 90 along each lattice direction
        state = ring.mul(state, (ring.monomial(i, j) + ring.monomial(-i, -j)) % 2)
    passes = np.zeros(n * n, dtype=start.dtype)
    for r in range(n):
        for c in range(n):
            passes[r * n + c] = state[ring.index(c, r - c // 2)]
    assert np.array_equal(passes, session.grid.occupancy)


def test_the_engine_reproduces_the_simulations():
    simulated = {(r["lattice"], r["n"]): r for r in _rows(ROUND_1 / "discovery.jsonl")}
    for lattice in ("hexagon", "triangle-edge", "triangle-edge+vertex"):
        for n in (10, 16, 18, 24):
            exact = lattices.period(lattice, n)
            assert (exact["period"], exact["transient"]) == (
                simulated[lattice, n]["period"],
                simulated[lattice, n]["transient"],
            )


def test_round_1_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(ROUND_1 / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, ROUND_1) == []
    assert [e["kind"] for e in ledger.entries] == [
        "question",
        "prediction",
        "prediction",
        "run_started",
        "observations",
        "verdict",
    ]
    verdict = ledger.entries[-1]["body"]
    assert verdict["law"]["confirmed"] == 207 and verdict["law"]["errors"] == []
    assert sorted(verdict["law"]["refuted_at"]) == ["hexagon 148", "hexagon 190", "hexagon 74"]
    assert verdict["hexagon_transient_refuted_at"] == []
    for key in verdict["law"]["refuted_at"]:
        outcome = verdict["outcomes"][key]
        assert outcome["predicted"] == 3 * outcome["period"]


def test_the_hexagon_odd_period_is_rule_90s_at_every_size_computed():
    rows = _rows(ROUND_1 / "discovery.jsonl") + _rows(ROUND_1 / "records.jsonl")
    hexagon = [r for r in rows if r["lattice"] == "hexagon"]
    assert len(hexagon) == 98
    for row in hexagon:
        m = lattices.odd_part(row["n"])
        assert lattices.odd_part(row["period"]) == (algebra.rule90_period(m) if m > 1 else 1)


def test_round_2_ledger_is_intact_and_the_verdict_holds():
    ledger = Ledger(ROUND_2 / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, ROUND_2) == []
    assert [e["kind"] for e in ledger.entries] == ["question"] + ["prediction"] * 4 + [
        "run_started",
        "observations",
        "verdict",
    ]
    verdict = ledger.entries[-1]["body"]
    assert verdict["hexagon_law"] == {"confirmed": 100, "refuted": 0, "refuted_at": []}
    assert verdict["triangle_law"] == {"confirmed": 14, "refuted": 0, "refuted_at": []}
    shortfalls = [202, 222, 282, 296, 380, 394, 398]
    assert verdict["rival_refuted_at"] == [f"hexagon {n}" for n in shortfalls]
    assert verdict["hexagon_transient_refuted_at"] == [] and verdict["errors"] == []
    rival = ledger.entries[2]["body"]["predictions"]["hexagon"]
    for n in shortfalls:
        hexagon = verdict["outcomes"][f"hexagon {n}"]["period"]
        assert rival[str(n)] == (7 if n == 398 else 3) * hexagon
        for lattice in ("triangle-edge", "triangle-edge+vertex"):
            assert verdict["outcomes"][f"{lattice} {n}"]["period"] == rival[str(n)]


def _sum(ring, steps):
    x = ring.zero()
    for i, j in steps:
        x = (x + ring.monomial(i, j)) % 2
    return x


NEAREST = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
NEXT_NEAREST = ((1, 2), (-1, -2), (2, 1), (-2, -1), (1, -1), (-1, 1))


@pytest.mark.parametrize("n", [6, 8, 12, 18, 30, 64])
def test_both_triangle_rules_square_to_scalars(n):
    """Two edge generations are 1 + the six nearest neighbours; two edge+vertex generations are
    the twelve nearest and next-nearest (on each orientation separately)."""
    ring, edge = lattices.triangle(n, "edge")
    _, both = lattices.triangle(n, "edge+vertex")
    zero = ring.zero()
    f_edge = (ring.monomial(0, 0) + _sum(ring, NEAREST)) % 2
    f_both = _sum(ring, NEAREST + NEXT_NEAREST)
    assert edge * edge == lattices.Matrix(ring, [[f_edge, zero], [zero, f_edge]])
    assert both * both == lattices.Matrix(ring, [[f_both, zero], [zero, f_both]])


def test_the_tori_as_groups_and_where_the_steps_go():
    for n in range(6, 41, 2):
        h = n // 2
        # hexagon: (q, r) -> (q + 2r mod 2n, r mod n/2) kills Lambda and has n^2 elements
        assert all(((q + 2 * r) % (2 * n), r % h) == (0, 0) for q, r in ((n, -h), (0, n)))
        # triangle: (x, y) -> (x - y mod n, y mod n/2) kills Lambda and has n^2 / 2 elements
        assert all(((x - y) % n, y % h) == (0, 0) for x, y in ((h, -h), (h, h)))
    # times 2^(v-1), a hexagon step lands on g^((q + 2r) mod 4) in Z/4
    assert {s: (s[0] + 2 * s[1]) % 4 for s in lattices.AXIAL_STEPS} == {
        (1, 0): 1,
        (-1, 0): 3,
        (0, 1): 2,
        (0, -1): 2,
        (1, -1): 3,
        (-1, 1): 1,
    }
    # and a triangle translation on z exactly when x - y is odd
    assert [(x - y) % 2 for x, y in NEAREST] == [1, 1, 1, 1, 0, 0]
    assert [(x - y) % 2 for x, y in NEXT_NEAREST] == [1, 1, 1, 1, 0, 0]


def test_the_proved_laws_hold_at_every_size_computed():
    rows = (
        _rows(ROUND_1 / "discovery.jsonl")
        + _rows(ROUND_1 / "records.jsonl")
        + _rows(ROUND_2 / "records.jsonl")
    )
    seen = Counter()
    for row in rows:
        n, period, lattice = row["n"], row["period"], row["lattice"]
        m = lattices.odd_part(n)
        two_v = n // m
        seen[lattice] += 1
        if lattice == "hexagon":
            expected = 1 if m == 1 else two_v if m == 3 else 2 * two_v * algebra.rule90_period(m)
            assert period == expected
        elif m == 1:
            assert period == (n if lattice == "triangle-edge" else 1)
        else:
            odd = lattices.odd_part(period)
            assert period == 2 * two_v * odd
            assert (2 ** lattices.suborder(m) - 1) % odd == 0
    assert seen == {"hexagon": 198, "triangle-edge": 105, "triangle-edge+vertex": 105}
