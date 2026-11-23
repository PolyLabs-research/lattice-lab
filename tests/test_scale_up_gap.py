"""The test of whether the large grids agree with each other (examples/scale-up-gap): its
interval, what it registers, and how a claim is judged.

The judge is tried on made-up runs whose answer is known, and the whole study on grids of side
32 to 64 from starts the step-2 laws used, which the registered study does not.
"""

import importlib.util
import math
import subprocess
import sys
from pathlib import Path

import pytest
from scipy import stats

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, load, register, run

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-gap"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("scale_up_gap_study", LAB / "study.py")

# Eight values with mean 0 and unit spread, to scatter made-up starts by.
SCATTER = [-1.4, -0.9, -0.4, -0.1, 0.1, 0.4, 0.9, 1.4]
SCATTER = [v / (sum(x * x for x in SCATTER) / 7) ** 0.5 for v in SCATTER]


def test_the_difference_interval_is_welchs():
    first = [0.50, 0.52, 0.47, 0.55, 0.49, 0.51, 0.53, 0.48]
    second = [0.40, 0.46, 0.35, 0.44, 0.52, 0.38, 0.41]
    ours = S.difference(first, second, 0.99)
    theirs = stats.ttest_ind(first, second, equal_var=False).confidence_interval(0.99)
    assert math.isclose(ours["low"], theirs.low) and math.isclose(ours["high"], theirs.high)
    assert math.isclose(ours["difference"], sum(first) / 8 - sum(second) / 7)
    still = S.difference([0.5, 0.5, 0.5], [0.4, 0.4, 0.4], 0.99)
    assert still["se"] == 0 and math.isclose(still["low"], 0.1) and still["low"] == still["high"]


def _row(side, seed, live, share=0.5615, unlike=0.0264, cells=10**9):
    """A made-up run of the pair whose live fraction, species balance and mixing are as given
    at every sampled generation."""
    alive = round(live * cells)
    first = round(share * alive)
    pairs = 10**8
    return {
        "world": S.WORLD,
        "side": side,
        "seed": seed,
        "cells": cells,
        "generations": [0, 200, 1000],
        "alive": [[first] * 3, [alive - first] * 3],
        "unlike": [round(unlike * pairs)] * 3,
        "like": [pairs - round(unlike * pairs)] * 3,
        "births": [100, 100],
        "contested": 2,
        "extinct_at": [None, None],
    }


def _made_up(monkeypatch, shift=None, spread=0.0002):
    """Eight starts at each side, scattered about the same means; `shift` moves one side's
    quantity: (side, quantity, by)."""
    monkeypatch.setattr(S, "STARTS", {1024: 8, 2048: 8, 4096: 8})
    rows = []
    for side in S.STARTS:
        for seed, z in zip(S.seeds(side), SCATTER, strict=True):
            values = {"live": 0.0483 + spread * z, "share": 0.5615 + 4 * spread * z,
                      "unlike": 0.0264 + spread * z / 2}  # fmt: skip
            if shift and shift[0] == side:
                values[shift[1]] += shift[2]
            rows.append(_row(side, seed, **values))
    return rows


def test_the_judge_passes_sides_that_agree(monkeypatch):
    # the spread is small enough that eight starts a side resolve the margins
    verdict = S.decide(_made_up(monkeypatch, spread=0.00003), S.predictions())
    assert verdict["verdict"] == {"live": "holds", "share": "holds", "unlike": "holds"}
    assert set(verdict["outcomes"]) == {p["label"] for p in S.predictions()}
    assert set(verdict["outcomes"].values()) == {"holds"} and verdict["missing"] == []
    gap = verdict["differences"]["live, sides 2048 and 4096"]
    assert abs(gap["difference"]) < 1e-9 and gap["margin"] == 0.0002
    assert math.isclose(gap["se"], 0.00003 * (2 / 8) ** 0.5, rel_tol=1e-3)
    assert verdict["means"]["live"]["4096"]["starts"] == 8
    assert math.isclose(verdict["means"]["live"]["4096"]["mean"], 0.0483, rel_tol=1e-6)
    told = verdict["reported"]
    assert told["live_fraction_at_generation"] == 200 and set(told["means"]) == {
        "1024",
        "2048",
        "4096",
    }
    assert told["starts_losing_a_species"] == {"1024": 0, "2048": 0, "4096": 0}


@pytest.mark.parametrize(
    ("shift", "failed"),
    [
        # the gap the scale-up test showed, if it were real
        ((2048, "live", 0.00034), {"live, sides 2048 and 4096", "live, sides 1024 and 2048"}),
        # a gap of exactly the margin does not pass: the whole interval must lie inside
        ((4096, "live", -0.0002), {"live, sides 2048 and 4096", "live, sides 1024 and 4096"}),
        ((1024, "share", 0.004), {"share, sides 1024 and 4096", "share, sides 1024 and 2048"}),
        ((4096, "unlike", 0.0007), {"unlike, sides 2048 and 4096", "unlike, sides 1024 and 4096"}),
    ],
)
def test_the_judge_fails_a_side_that_stands_apart(monkeypatch, shift, failed):
    verdict = S.decide(_made_up(monkeypatch, shift, spread=0.00003), S.predictions())
    assert {label for label, word in verdict["outcomes"].items() if word == "fails"} == failed
    assert verdict["verdict"][shift[1]] == "fails"
    others = {q: word for q, word in verdict["verdict"].items() if q != shift[1]}
    assert set(others.values()) == {"holds"}


def test_too_wide_a_spread_fails_and_a_short_side_is_missing(monkeypatch):
    # sides that agree, measured too loosely to say so, do not pass
    loose = S.decide(_made_up(monkeypatch, spread=0.0004), S.predictions())
    assert loose["verdict"]["live"] == "fails"
    assert abs(loose["differences"]["live, sides 2048 and 4096"]["difference"]) < 1e-9
    rows = _made_up(monkeypatch, spread=0.00003)
    short = [r for r in rows if not (r["side"] == 2048 and r["seed"] == S.FIRST)]
    verdict = S.decide(short, S.predictions())
    assert verdict["missing"] == ["side 2048"] and set(verdict["means"]["live"]) == {"1024", "4096"}
    assert verdict["outcomes"]["live, sides 1024 and 4096"] == "holds"
    assert verdict["outcomes"]["live, sides 2048 and 4096"] == "missing"
    assert verdict["verdict"] == {"live": "missing", "share": "missing", "unlike": "missing"}


def test_what_is_registered():
    claims = S.predictions()
    assert len(claims) == 9 and len({c["label"] for c in claims}) == 9
    assert [c["label"] for c in claims][:3] == [
        "live, sides 2048 and 4096", "live, sides 1024 and 4096", "live, sides 1024 and 2048",
    ]  # fmt: skip
    assert {c["quantity"]: c["margin"] for c in claims} == {
        "live": 0.0002, "share": 0.0028, "unlike": 0.00053,
    }  # fmt: skip
    assert {c["level"] for c in claims} == {0.99} and all(len(c["claim"]) < 240 for c in claims)
    # 384, 96 and 32 fresh starts, the largest grids first
    jobs = S.jobs()
    assert len(jobs) == 512 and jobs[0] == ("pair standoff", 4096, 6001)
    assert jobs[-1] == ("pair standoff", 1024, 6384)
    assert [sum(s == side for _, s, _ in jobs) for side in (4096, 2048, 1024)] == [32, 96, 384]
    laws = S.laws
    part1 = _load("scale_up_sizes_study", ROOT / "examples/scale-up-sizes/study.py")
    part2 = _load("scale_up_sizes_large_study", ROOT / "examples/scale-up-sizes-large/study.py")
    seen = set(laws.SEEDS) | set(part1.SEEDS) | set(part2.SEEDS) | set(range(5001, 5017))
    seen |= set(range(101, 229)) | set(range(9001, 9100))
    assert not {seed for _, _, seed in jobs} & seen
    question = S.question()
    assert question["id"] == "scale-up-gap" and question["runs"] == 512
    assert question["world"]["rules"] == list(laws.WORLDS["pair standoff"][0])
    assert question["starts"] == {"1024": [6001, 6384], "2048": [6001, 6096], "4096": [6001, 6032]}
    assert len(question["excluded_seen"]) == 5 and set(question["sha256"]) == {
        "study.py", "sizes.py", "laws.py",
    }  # fmt: skip


def test_the_numbers_of_starts_give_what_the_design_says():
    design = S.design()
    assert design["passes_if_the_gap_is_the_margin"] == 0.005
    chances = [
        pair["passes_if_the_sides_agree"]
        for quantity in S.MARGINS
        for pair in design[quantity].values()
    ]
    assert len(chances) == 9 and min(chances) > 0.99 and math.prod(chances) > 0.98
    # the three sides' means of the live fraction have about the same standard error
    errors = [0.536047 / side / math.sqrt(S.STARTS[side]) for side in S.STARTS]
    assert max(errors) / min(errors) < 1.2 and 2.2e-5 < min(errors) < max(errors) < 2.8e-5
    assert math.isclose(design["live"]["2048 and 4096"]["se"], math.hypot(errors[1], errors[2]),
                        rel_tol=0.01)  # fmt: skip


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_the_study_registers_runs_and_judges_on_small_grids(monkeypatch, tmp_path):
    monkeypatch.setattr(S, "STARTS", {32: 6, 48: 4, 64: 3})
    monkeypatch.setattr(S, "PAIRS", ((48, 64), (32, 64), (32, 48)))
    monkeypatch.setattr(S, "FIRST", 2001)
    _git(tmp_path, "init", "-q")
    study = Study(tmp_path, S.question, S.predictions, S.execute, S.decide, rerun=S.rerun)
    assert len(register(study)) == 10
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert set(verdict["verdict"]) == {"live", "share", "unlike"} and verdict["missing"] == []
    assert set(verdict["outcomes"].values()) <= {"holds", "fails"} and len(verdict["outcomes"]) == 9
    assert set(verdict["means"]["live"]) == {"32", "48", "64"}
    assert verdict["means"]["share"]["64"]["starts"] == 3
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    rows = ledger.entries[-2]["body"]["rows"]
    assert [r["side"] for r in rows] == [64] * 3 + [48] * 4 + [32] * 6
    assert S.rerun(rows[0]) == rows[0] and S.rerun(rows[-1]) == rows[-1]
    # running again adds nothing: every run is already recorded
    before = (tmp_path / "records.jsonl").read_text()
    study.execute(tmp_path / "records.jsonl", 1)
    assert (tmp_path / "records.jsonl").read_text() == before
    # the census dashboards' reader gives each prediction its outcome
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    table, summary = readers.READERS["scale-up-gap"](bodies, verdict, {})
    assert [r["label"] for r in table] == [b["label"] for b in bodies]
    assert {r["outcome"] for r in table} <= {"held", "failed"} and summary.startswith("live ")


def test_the_ledger_holds_the_registration():
    path = LAB / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    claims = S.predictions()
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[:10] == ["question"] + ["prediction"] * 9
    question = ledger.entries[0]
    for entry, claim in zip(ledger.entries[1:10], claims, strict=True):
        assert entry["body"] == {"question": question["hash"], **claim}
    if "verdict" not in kinds:  # between registration and the run, the code must not move
        assert question["body"]["sha256"] == S.question()["sha256"]


def test_the_registered_run_found_that_the_large_grids_agree():
    """The run of 2026-11-23, on a rented machine: all nine predictions held. On fresh starts
    the three sides' live fractions are within 0.00007 of each other, no difference is as far
    as two standard errors from zero, and the gap of 0.0002 is outside every 99% interval."""
    path = LAB / "ledger.jsonl"
    if not path.exists() or Ledger(path).entries[-1]["kind"] != "verdict":
        pytest.skip("not run yet")
    ledger = Ledger(path)
    assert [e["kind"] for e in ledger.entries[-3:]] == ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["verdict"] == {"live": "holds", "share": "holds", "unlike": "holds"}
    assert set(verdict["outcomes"].values()) == {"holds"} and len(verdict["outcomes"]) == 9
    assert verdict["missing"] == [] and len(ledger.entries[-2]["body"]["rows"]) == 512
    code = ledger.entries[-3]["body"]["provenance"]["lattice_lab"]
    assert code["dirty"] is False and code["source"] == "file:///root/run/lattice-lab"
    means = verdict["means"]["live"]
    assert [means[side]["starts"] for side in ("1024", "2048", "4096")] == [384, 96, 32]
    assert math.isclose(means["1024"]["mean"], 0.0483017) and means["1024"]["se"] < 2.9e-5
    assert math.isclose(means["2048"]["mean"], 0.0483301) and means["2048"]["se"] < 2.6e-5
    assert math.isclose(means["4096"]["mean"], 0.0482665) and means["4096"]["se"] < 2.4e-5
    # the pair of sides the question came from: 0.00006 apart, and at most 0.00016 at 99%
    gap = verdict["differences"]["live, sides 2048 and 4096"]
    assert math.isclose(gap["difference"], 6.36e-5, rel_tol=1e-3)
    assert math.isclose(gap["se"], 3.46e-5, rel_tol=1e-2) and -0.00003 < gap["low"]
    assert gap["high"] < 0.00016 < gap["margin"]
    scores = {label: d["difference"] / d["se"] for label, d in verdict["differences"].items()}
    assert max(scores, key=lambda label: abs(scores[label])) == "live, sides 2048 and 4096"
    assert math.isclose(max(map(abs, scores.values())), 1.84, abs_tol=0.005)
    for d in verdict["differences"].values():
        assert -d["margin"] < d["low"] < d["high"] < d["margin"]
    # at generation 200, where the gap first showed, the sides are level
    early = verdict["reported"]
    assert early["live_fraction_at_generation"] == 200
    assert max(abs(d["difference"]) for d in early["differences"].values()) < 2.5e-5
    assert early["starts_losing_a_species"] == {"1024": 0, "2048": 0, "4096": 0}


def test_verify_can_rerun_the_studys_records():
    assert load(LAB).rerun is not None
