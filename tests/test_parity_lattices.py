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
