"""Rules with known behaviour, through real LatticeLife runs: the loop must agree with them.

- B/S (nothing born, nothing survives) dies at once on every torus: settling time 1, so the law
  is a constant.
- B1357/S1357 on the square (Moore) lattice is linear over GF(2): every cell's next state is the
  parity of its eight neighbours. Its transient and period are computed here independently of
  LatticeLife's stepping and cycle detection (numpy rolls on a 2D array), and LatticeLife's
  records must match exactly.
"""

import json

import numpy as np
import pytest
from latticelife.core.rules import Rule
from latticelife.experiments.harness import single_species_session
from latticelife.experiments.observables import settling_time
from latticelife.experiments.sweeps import SweepTask, sweep_point

from lattice_lab.experiment import LatticeExperimenter, question_config, rerun_record
from lattice_lab.ledger import Ledger, check_order
from lattice_lab.loop import ask
from lattice_lab.question import Question


def test_the_empty_rule_settles_at_once_and_the_loop_says_constant(tmp_path):
    q = Question(
        id="empty-rule",
        rule="B/S",
        shape="square",
        fit_sizes=(4, 5, 6, 7, 8),
        heldout_pool=(10, 12),
        seeds=3,
        heldout_per_round=2,
        max_rounds=1,
    )
    ledger = Ledger(tmp_path / "ledger.jsonl")
    experimenter = LatticeExperimenter(q, tmp_path / "records.jsonl")
    outcome = ask(q, experimenter, ledger, records_file="records.jsonl")
    fit_rows = ledger.entries[2]["body"]["rows"]
    assert {row["y"] for row in fit_rows} == {1.0}
    assert (outcome.verdict, outcome.law) == ("found", "constant")
    assert check_order(ledger, tmp_path) == []


def _parity_transient(occupancy: np.ndarray, steps: int) -> tuple[int, int] | None:
    """(period, transient) of next = XOR of the 8 Moore neighbours on a torus, by brute force."""
    grid = occupancy.astype(bool)
    seen = {grid.tobytes(): 0}
    for t in range(1, steps):
        nxt = np.zeros_like(grid)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    nxt ^= np.roll(np.roll(grid, dr, axis=0), dc, axis=1)
        grid = nxt
        key = grid.tobytes()
        if key in seen:
            return t - seen[key], seen[key]
        seen[key] = t
    return None


@pytest.mark.parametrize("size", [5, 6, 7, 8, 9, 10])
def test_a_linear_rule_matches_an_independent_computation(size):
    q = Question(
        id="parity", rule="B1357/S1357", shape="square", fit_sizes=(5, 6, 7, 8), heldout_pool=(10,)
    )
    config = question_config(q)
    rule = Rule.from_bs_string(q.rule)
    for seed in (1, 2, 3):
        start = single_species_session(config, rule, "square", size, 0.5, seed)
        occupancy = start.grid.occupancy.reshape(size, size) != 0
        exact = _parity_transient(occupancy, 5000)
        assert exact is not None
        period, transient = exact
        record = sweep_point(SweepTask(config, q.rule, "square", size, 0.5, seed, 5000))
        assert settling_time(record.to_json()) == transient
        if record.extinction_step is not None:
            # Died out: 0 is not in B, so the sweep stops at the empty grid, a fixed point.
            assert period == 1 and record.extinction_step == transient
        else:
            assert (record.period, record.transient) == (period, transient)


def test_records_rerun_byte_for_byte(tmp_path):
    q = Question(
        id="rerun",
        rule="B2/S34",
        shape="hexagon",
        fit_sizes=(8, 10, 12, 16),
        heldout_pool=(20,),
        seeds=2,
    )
    experimenter = LatticeExperimenter(q, tmp_path / "records.jsonl")
    experimenter.measure([8, 10], 1e12)
    config = question_config(q)
    for line in (tmp_path / "records.jsonl").read_text().splitlines():
        assert rerun_record(json.loads(line), config) == line
