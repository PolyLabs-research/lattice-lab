"""The scale-up instrument (examples/scale-up-linear): zooming out a LatticeLife torus, the
closure test, and what the group ring says the test must show.

Everything here runs on fine sides 12, 16, 18 and 24 with seeds from 9001. The registered study
leaves those sides out and declares them as seen (`SEEN_SIDES`, the question's `excluded_seen`),
so nothing in this file computes a registered case.
"""

import importlib.util
import math
import subprocess
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np
import pytest
from latticelife.core.geometries import build_adjacency

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, register, run

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-linear"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("scale_up_linear_study", LAB / "study.py")
scaleup, mismatch = S.scaleup, S.mismatch
World, Projection, Diagram = scaleup.World, scaleup.Projection, scaleup.Diagram

WORLDS = [(shape, rule) for shape in scaleup.SHAPES for rule in S.RULES[shape]]
BLOCKS = [("square", 12, 2), ("square", 12, 3), ("square", 12, 4), ("square", 24, 4),
          ("hexagon", 12, 2), ("hexagon", 12, 3), ("hexagon", 24, 4)]  # fmt: skip


def _rows(array: np.ndarray) -> list[list[int]]:
    return [sorted(row) for row in array.tolist()]


def _mismatches(shape, rule, side, block, clock, coarse_rule, seed) -> int:
    """The supercells that differ after one coarse generation, by decimation."""
    test = Diagram(
        World(shape, rule, side),
        World(shape, coarse_rule, scaleup.coarse_side(shape, side, block)),
        Projection("decimate", block),
        clock,
    )
    results, _ = scaleup.closure([test], scaleup.random_start(shape, side, seed), 1)
    return results[0].mismatches[0]


# --- geometry ----------------------------------------------------------------------------------


@pytest.mark.parametrize("shape", scaleup.SHAPES)
@pytest.mark.parametrize("side", [12, 24])
def test_one_step_away_is_latticelifes_own_adjacency(shape, side):
    own = build_adjacency(shape, side, side, True)
    assert _rows(scaleup.dilated_adjacency(shape, side, 1)) == _rows(own)
    assert np.array_equal(scaleup.adjacency(World(shape, "B/S", side)), own)


@pytest.mark.parametrize("shape,side,block", BLOCKS)
def test_the_cosets_of_a_block_partition_the_grid(shape, side, block):
    cells = scaleup.block_cells(shape, side, block)
    coarse = scaleup.coarse_side(shape, side, block)
    assert cells.shape == (block * block, coarse * coarse)
    assert sorted(cells.ravel().tolist()) == list(range(side * side))


@pytest.mark.parametrize("shape,side,block", BLOCKS)
def test_the_sampled_cells_are_a_coarse_grid_of_the_same_shape(shape, side, block):
    """A supercell's neighbours on the coarse grid sit `block` steps from it on the fine grid."""
    coarse = scaleup.coarse_side(shape, side, block)
    sampled = scaleup.sample_cells(shape, side, block)
    coarse_neighbours = build_adjacency(shape, coarse, coarse, True)
    far = scaleup.dilated_adjacency(shape, side, block)
    assert _rows(sampled[coarse_neighbours]) == _rows(far[sampled])


def test_a_hexagon_block_needs_an_even_coarse_side():
    with pytest.raises(ValueError, match="divisible by 8"):
        scaleup.coarse_side("hexagon", 12, 4)
    with pytest.raises(ValueError, match="does not divide"):
        scaleup.coarse_side("square", 12, 5)
    with pytest.raises(ValueError, match="at least"):
        scaleup.coarse_side("square", 12, 6)  # LatticeLife has no wrapped 2 x 2 square grid


@pytest.mark.parametrize("shape", scaleup.SHAPES)
@pytest.mark.parametrize("kind", ["decimate", "parity"])
def test_zooming_out_twice_is_zooming_out_once(shape, kind):
    cells = scaleup.random_start(shape, 24, 9001)
    once = scaleup.project(shape, 24, Projection(kind, 4), cells)
    half = scaleup.project(shape, 24, Projection(kind, 2), cells)
    assert np.array_equal(scaleup.project(shape, 12, Projection(kind, 2), half), once)
    assert 0 < once.sum() < once.size


# --- the two known answers, on small grids -------------------------------------------------------


@pytest.mark.parametrize("shape,rule", WORLDS)
@pytest.mark.parametrize("side,k", [(12, 2), (12, 4), (12, 8), (16, 8), (24, 16)])
def test_two_to_the_k_generations_are_one_generation_with_neighbours_that_far(shape, rule, side, k):
    """Frobenius, on LatticeLife's engine. At side 16 and k = 8 opposite neighbours land on the
    same cell and are counted twice."""
    test = Diagram(World(shape, rule, side), World(shape, rule, side, k), Projection("identity"), k)
    results, _ = scaleup.closure([test], scaleup.random_start(shape, side, 9001), 3)
    assert results[0].mismatches == (0, 0, 0)
    if side != 16:  # a parity rule on a torus of side 2^e dies, or stands still
        assert all(0 < live < side * side for live in results[0].live)


@pytest.mark.parametrize("shape,rule", WORLDS)
@pytest.mark.parametrize("side,block", [(12, 2), (24, 2), (24, 4)])
def test_zooming_out_by_a_power_of_two_is_exact(shape, rule, side, block):
    coarse = scaleup.coarse_side(shape, side, block)
    tests = [
        Diagram(World(shape, rule, side), World(shape, rule, coarse), projection, block)
        for projection in (
            Projection("decimate", block),
            Projection("decimate", block, (block - 1, block // 2)),
            Projection("parity", block),
        )
    ]
    results, _ = scaleup.closure(tests, scaleup.random_start(shape, side, 9002), 4)
    for result in results:
        assert result.mismatches == (0, 0, 0, 0)
        assert result.supercells == coarse * coarse and all(result.live)


@pytest.mark.parametrize("shape,rule", WORLDS)
def test_a_block_of_three_is_a_fair_coin(shape, rule):
    law = mismatch.law(shape, rule, 24, 3, 3, rule)
    assert law["supercells"] == law["rank"] == 64  # 64 independent coins
    seeds = range(9001, 9041)
    total = sum(_mismatches(shape, rule, 24, 3, 3, rule, seed) for seed in seeds)
    low, high = mismatch.pooled_acceptance(64, 0, len(seeds), 1e-6)
    assert low <= total <= high and low > 0.4 * 64 * len(seeds)


@pytest.mark.parametrize("shape,rule", WORLDS)
def test_one_constraint_on_the_coins_makes_every_count_even(shape, rule):
    """A clock one generation early at block 2: rank N - 1, and the constraint is the sum of
    all the coins. The wrong coarse rule has rank N, and its counts come out odd as well."""
    early = mismatch.law(shape, rule, 24, 2, 1, rule)
    assert early["supercells"] - early["rank"] == 1 and early["even"]
    counts = [_mismatches(shape, rule, 24, 2, 1, rule, seed) for seed in range(9001, 9021)]
    assert all(count % 2 == 0 for count in counts) and min(counts) > 0
    other = S.OTHER[rule]
    wrong = mismatch.law(shape, rule, 24, 2, 2, other)
    assert wrong["rank"] == wrong["supercells"] and wrong["terms"] == 1 and not wrong["even"]
    counts = [_mismatches(shape, rule, 24, 2, 2, other, seed) for seed in range(9001, 9021)]
    assert any(count % 2 for count in counts)


def _engine_rank(shape, rule, side, block, clock, coarse_rule) -> int:
    """The rank of start -> mismatch vector, from the engine alone: one start per fine cell."""
    coarse = World(shape, coarse_rule, scaleup.coarse_side(shape, side, block))
    fine, projection = World(shape, rule, side), Projection("decimate", block)
    rows = [0] * coarse.cells
    for cell in range(side * side):
        start = np.zeros(side * side, dtype=np.int8)
        start[cell] = 1
        zoomed = scaleup.project(shape, side, projection, scaleup.Run(fine, start).advance(clock))
        ran = scaleup.Run(coarse, scaleup.project(shape, side, projection, start)).advance(1)
        for supercell in np.flatnonzero(zoomed != ran):
            rows[supercell] |= 1 << cell
    return mismatch.rank(rows)


@pytest.mark.parametrize("shape,rule", WORLDS)
@pytest.mark.parametrize("block,clock,swap", [(2, 2, False), (3, 3, False), (2, 1, False),
                                              (2, 3, False), (2, 2, True)])  # fmt: skip
def test_the_group_ring_gives_the_rank_the_engine_shows(shape, rule, block, clock, swap):
    coarse_rule = S.OTHER[rule] if swap else rule
    law = mismatch.law(shape, rule, 12, block, clock, coarse_rule)
    measured = _engine_rank(shape, rule, 12, block, clock, coarse_rule)
    assert measured == (0 if law["zero"] else law["rank"])
    assert law["zero"] == (block == clock == 2 and not swap)


# --- the intervals -------------------------------------------------------------------------------


def _tail(trials: int, below: int) -> Fraction:
    """P(X < below) for X ~ Binomial(trials, 1/2), exactly."""
    return Fraction(sum(math.comb(trials, k) for k in range(below)), 2**trials)


@pytest.mark.parametrize("trials,alpha", [(10, 0.1), (1000, 1e-3), (4096, 1e-6)])
def test_the_acceptance_interval_is_the_narrowest_with_its_tails(trials, alpha):
    low, high = mismatch.acceptance(trials, alpha)
    assert high == trials - low
    assert _tail(trials, low) <= Fraction(alpha) / 2 < _tail(trials, low + 1)
    if trials == 10:
        assert (low, high) == (2, 8)


def test_the_interval_for_even_counts_holds_their_exact_distribution():
    """Rank N - 1: each start's mismatches are a uniform even-weight vector. Enumerated for 6
    supercells and 3 starts, the registered kind of interval is left less often than alpha."""
    supercells, starts, alpha = 6, 3, 0.2
    weights = [sum(v) for v in product((0, 1), repeat=supercells) if sum(v) % 2 == 0]
    low, high = mismatch.pooled_acceptance(supercells, 1, starts, alpha)
    totals = [sum(t) for t in product(weights, repeat=starts)]
    outside = sum(not low <= total <= high for total in totals)
    assert 0 < outside and Fraction(outside, len(totals)) <= Fraction(alpha)
    with pytest.raises(ValueError, match="above 1"):
        mismatch.pooled_acceptance(supercells, 2, starts, alpha)


# --- the study -----------------------------------------------------------------------------------


def test_the_study_registers_what_it_says():
    cases = S.cases()
    assert [c["case"] for c in cases] == list(range(len(cases)))
    count = {h: sum(c["hypothesis"] == h for c in cases) for h in ("H0", "H1", "H2")}
    assert count == {"H0": 32, "H1": 228, "H2": 36}
    assert not {c["side"] for c in cases} & set(S.SEEN_SIDES)
    for case in cases:
        zero = case["predicted"] == "zero"
        assert zero == (case["hypothesis"] != "H2")
        if zero:
            # a parity rule dies, or stands still, on a torus of side 2^e: none is registered
            assert case["coarse_side"] & (case["coarse_side"] - 1)
            assert case["clock"] == case["block"] * case["coarse_dilation"]
            assert case["clock"] & (case["clock"] - 1) == 0
        else:
            low, high = case["accept"]
            assert case["supercells"] - case["rank"] in (0, 1)
            assert low < case["trials"] / 2 < high and high - low < 0.04 * case["trials"]
    assert max(c["clock"] for c in cases if c["predicted"] == "zero") == 128
    left_out = S.question()["controls_left_out"]["controls"]
    assert len(left_out) == 4 and {c["kind"] for c in left_out} == {"one generation late"}


def test_the_ledger_holds_the_registration():
    path = LAB / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    cases = S.cases()
    assert kinds[: len(cases) + 1] == ["question"] + ["prediction"] * len(cases)
    question = ledger.entries[0]
    for entry, case in zip(ledger.entries[1:], cases, strict=False):
        assert entry["body"] == {"question": question["hash"], **case}
    if "verdict" not in kinds:  # between registration and the run, the code must not move
        assert question["body"]["sha256"] == S.question()["sha256"]


def test_the_registered_run_calibrated_the_instrument():
    """The run of 2026-11-23: every case held. No supercell differed where the scales match, and
    every control's total lay inside the interval registered with it."""
    path = LAB / "ledger.jsonl"
    if not path.exists() or Ledger(path).entries[-1]["kind"] != "verdict":
        pytest.skip("not run yet")
    ledger = Ledger(path)
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[-3:] == ["run_started", "observations", "verdict"] and len(kinds) == 300
    verdict = ledger.entries[-1]["body"]
    assert verdict["verdict"] == "calibrated" and verdict["not_holding"] == []
    assert {h: (c["cases"], c["holds"]) for h, c in verdict["hypotheses"].items()} == {
        "H0": (32, 32),
        "H1": (228, 228),
        "H2": (36, 36),
    }
    cases = {e["body"]["case"]: e["body"] for e in ledger.entries if e["kind"] == "prediction"}
    rows = ledger.entries[-2]["body"]["rows"]
    zero = [r for r in rows if cases[r["case"]]["predicted"] == "zero"]
    half = [r for r in rows if cases[r["case"]]["predicted"] == "half"]
    assert len(zero) == 780 and len(half) == 2304
    assert sum(sum(r["mismatches"]) for r in zero) == 0
    assert sum(r["supercells"] * len(r["mismatches"]) for r in zero) == 10_105_746
    assert all(0 < live < r["supercells"] for r in zero for live in r["live"])
    assert sum(r["supercells"] for r in half) == 1_640_448
    assert sum(r["mismatches"][0] for r in half) == 820_478
    for control in verdict["controls"]:
        assert control["accept"][0] <= control["total"] <= control["accept"][1]
    # where the group ring gave rank N - 1, every start's count is even; at rank N about half are
    constrained = [r for r in half if cases[r["case"]]["supercells"] > cases[r["case"]]["rank"]]
    free = [r for r in half if cases[r["case"]]["supercells"] == cases[r["case"]]["rank"]]
    assert len(constrained) == 768 and not any(r["mismatches"][0] % 2 for r in constrained)
    assert sum(r["mismatches"][0] % 2 for r in free) == 760 and len(free) == 1536


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def small(monkeypatch):
    """The study's own tables, cut down to the sides this file is allowed to run."""
    monkeypatch.setattr(S, "SEEN_SIDES", ())
    monkeypatch.setattr(S, "MECHANISM", {"square": ((12, 2), (24, 16)), "hexagon": ((12, 8),)})
    monkeypatch.setattr(S, "COARSE", {"square": (6,), "hexagon": (6,)})
    monkeypatch.setattr(S, "BLOCKS", (2, 4))
    monkeypatch.setattr(S, "LARGE", {"square": ((3, 4),), "hexagon": ()})
    monkeypatch.setattr(S, "CONTROL_COARSE", (6,))
    monkeypatch.setattr(S, "ZERO_SEEDS", (9001, 9002))
    monkeypatch.setattr(S, "CONTROL_SEEDS", tuple(range(9001, 9017)))
    return S


def test_the_study_registers_runs_and_judges_on_small_grids(small, tmp_path):
    _git(tmp_path, "init", "-q")
    study = Study(tmp_path, small.question, small.predictions, small.execute, small.decide)
    entries = register(study)
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert verdict["verdict"] == "calibrated" and verdict["not_holding"] == []
    for counts in verdict["hypotheses"].values():
        assert counts["cases"] == counts["holds"] > 0
    assert len(verdict["controls"]) == verdict["hypotheses"]["H2"]["cases"]
    assert all(0.35 < c["fraction"] < 0.65 for c in verdict["controls"])
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    assert len(ledger.entries) == len(entries) + 3
    # the census dashboards' reader gives every prediction of this verdict as held
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    rows, summary = readers.READERS["scale-up-linear"](bodies, verdict, {})
    assert len(rows) == len(bodies) and {r["outcome"] for r in rows} == {"held"}
    assert summary.startswith("calibrated: H0 ")
    failed = {**verdict, "not_holding": [{"case": 0, "outcome": "fails"}]}
    rows, _ = readers.READERS["scale-up-linear"](bodies, failed, {})
    assert [r["outcome"] for r in rows[:2]] == ["failed", "held"]
    # run again over the records already there: nothing is computed twice
    before = (tmp_path / "records.jsonl").read_bytes()
    small.execute(tmp_path / "records.jsonl", 1)
    assert (tmp_path / "records.jsonl").read_bytes() == before


def test_the_judge_tells_a_failure_from_a_gap(small):
    cases = small.cases()
    zero = next(c for c in cases if c["hypothesis"] == "H1")
    half = next(c for c in cases if c["hypothesis"] == "H2")
    group = next(g for g in small.bundles(cases) if zero in g)
    rows = [r for seed in zero["seeds"] for r in small.run_bundle((group, seed))]
    mine = [r for r in rows if r["case"] == zero["case"]]
    assert small.judge(zero, mine) == {"outcome": "holds"}
    assert small.judge(zero, mine[:1])["outcome"] == "missing"
    broken = [{**r, "mismatches": [0, 3] + r["mismatches"][2:]} for r in mine]
    assert small.judge(zero, broken)["outcome"] == "fails"
    dead = [{**r, "live": [0] * len(r["live"])} for r in mine]
    assert small.judge(zero, dead)["outcome"] == "untested"
    # a control whose routes agree everywhere fails: zero is far outside its interval
    silent = [{"case": half["case"], "seed": seed, "mismatches": [0]} for seed in half["seeds"]]
    assert small.judge(half, silent)["outcome"] == "fails"
    verdict = small.decide(broken, cases)
    assert verdict["verdict"] == "not calibrated"
    assert small.decide(mine, cases)["verdict"] == "incomplete"
