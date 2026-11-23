"""The tie-break comparison (examples/scale-up-tie-break): its intervals, what a record measures,
and how the registered claims are judged.

The runs here are on grids of side 32 from starts and rule sets 9001 and up, which the registered
study does not use.
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
LAB = ROOT / "examples" / "scale-up-tie-break"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("scale_up_tie_break_study", LAB / "study.py")


# --- intervals and observables -------------------------------------------------------------------


def test_the_difference_interval_is_welchs():
    first = [0.50, 0.52, 0.47, 0.55, 0.49, 0.51, 0.53, 0.48]
    second = [0.40, 0.46, 0.35, 0.44, 0.52, 0.38, 0.41]
    ours = S.difference(first, second, 0.99)
    theirs = stats.ttest_ind(second, first, equal_var=False).confidence_interval(0.99)
    assert math.isclose(ours["low"], theirs.low) and math.isclose(ours["high"], theirs.high)
    assert math.isclose(ours["difference"], sum(second) / 7 - sum(first) / 8)
    still = S.difference([0.5, 0.5, 0.5], [0.4, 0.4, 0.4], 0.99)
    assert still["se"] == 0 and math.isclose(still["low"], -0.1) and still["low"] == still["high"]


def test_the_mean_interval_is_students():
    values = [0.50, 0.52, 0.47, 0.55, 0.49, 0.51, 0.53, 0.48]
    ours = S.mean_interval(values, 0.999)
    low, high = stats.t.interval(0.999, 7, loc=sum(values) / 8, scale=stats.sem(values))
    assert math.isclose(ours["low"], low) and math.isclose(ours["high"], high) and ours["n"] == 8


def test_what_a_record_measures():
    record = {
        "cells": 100,
        "generations": [0, 100, 200],
        "alive": [[30, 12, 6], [20, 8, 2]],
        "unlike": [40, 3, 1],
        "like": [60, 27, 9],
        "births": [300, 100],
        "contested": 20,
    }
    assert S.observe(record, "live@100") == 0.2 and S.observe(record, "live@200") == 0.08
    assert S.observe(record, "share_1@200") == 0.75
    assert S.observe(record, "unlike@100") == 0.1
    assert S.observe(record, "contested") == 0.05
    with pytest.raises(ValueError, match="unknown observable"):
        S.observe(record, "dead@100")


# --- the judge, on made-up records ---------------------------------------------------------------


def _row(world, kind, seed, live, share=0.5, unlike=0.03, contested=0.0, cells=10000):
    """A record whose live fraction, species balance, mixing and contested share are as given
    at every sampled generation."""
    alive = round(live * cells)
    first = round(share * alive)
    pairs = 1000
    return {
        "world": world,
        "kind": kind,
        "seed": seed,
        "cells": cells,
        "generations": [0, 100, 200, 300, 400, 500, 600],
        "alive": [[first] * 7, [alive - first] * 7],
        "unlike": [round(unlike * pairs)] * 7,
        "like": [pairs - round(unlike * pairs)] * 7,
        "births": [1000, 1000],
        "contested": round(contested * 2000),
        "extinct_at": [None, None],
    }


def _made_up(monkeypatch, effect=-0.1, rare_effect=0.0, pair_effect=0.0, tilt=0.0, common=8):
    """Two pairs and ten soups, eight starts each. In `common` soups 30% of births are
    contested, and the standoff shifts their live fraction by `effect`; in the others nothing
    is contested, and the shift is `rare_effect`. The pairs' live fraction shifts by
    `pair_effect`, and species 1's share sits at one half plus `tilt`."""
    seeds = tuple(range(1, 9))
    worlds = {
        name: {"rules": ["B3/S23"] * 2, "side": 100, "steps": 600, "seeds": seeds}
        for name in ("life-life", "life-highlife")
    }
    for index in range(1, 11):
        worlds[f"soup-{index:02d}"] = {
            "rules": ["B3/S23"] * 5,
            "side": 100,
            "steps": 200,
            "seeds": seeds,
        }
    monkeypatch.setattr(S, "worlds", lambda: worlds)
    wobble = [-0.003, 0.002, -0.001, 0.003, 0.001, -0.002, 0.0, 0.0]
    rows = []
    for name in worlds:
        soup = name.startswith("soup-")
        contested = 0.3 if soup and int(name[-2:]) <= common else 0.0
        for kind in S.KINDS:
            shift = 0.0
            if kind == "standoff":
                shift = (effect if contested else rare_effect) if soup else pair_effect
            for seed, w in zip(seeds, wobble, strict=True):
                live = (0.5 if soup else 0.06) + shift + w
                rows.append(_row(name, kind, seed, live, 0.5 + tilt + 10 * w, 0.03, contested))
    return rows


def test_the_judge_passes_what_the_predictions_describe(monkeypatch):
    verdict = S.decide(_made_up(monkeypatch), S.predictions())
    assert verdict["verdict"] == {"S": "holds", "A": "holds", "B": "holds"}
    assert set(verdict["outcomes"]) == {p["label"] for p in S.predictions()}
    assert set(verdict["outcomes"].values()) == {"holds"} and verdict["missing"] == []
    soups = verdict["soups"]
    assert (soups["common"], soups["common_differ"], soups["common_lowered"]) == (8, 8, 8)
    assert (soups["rare"], soups["rare_level"]) == (2, 2)
    assert [s["contested"] for s in soups["table"]] == [0.0, 0.0] + [0.3] * 8
    assert math.isclose(soups["table"][-1]["difference"], -0.1)
    assert math.isclose(verdict["known_answer"]["random"]["mean"], 0.5, abs_tol=1e-3)


@pytest.mark.parametrize(
    ("change", "claim", "labels"),
    [
        ({"effect": 0.0}, "B", {"B1", "B2"}),  # common contests, and nothing moves
        ({"effect": -0.01}, "B", {"B2"}),  # it moves, by less than the effect
        ({"effect": 0.1}, "B", {"B2"}),  # it moves the other way
        ({"rare_effect": 0.05}, "B", {"B0"}),  # rare contests, and it moves
        ({"pair_effect": 0.02}, "A", None),  # the pairs' live fraction moves
        ({"tilt": 0.1}, "S", {"S random", "S standoff"}),  # identical species do not end level
    ],
)
def test_the_judge_fails_each_claim_for_its_own_reason(monkeypatch, change, claim, labels):
    verdict = S.decide(_made_up(monkeypatch, **change), S.predictions())
    assert verdict["verdict"][claim] == "fails"
    failed = {label for label, outcome in verdict["outcomes"].items() if outcome == "fails"}
    if labels is None:
        assert failed == {f"A {pair} live@{g}" for pair in S.PAIRS for g in (100, 300, 600)}
    else:
        assert failed == labels
    others = {c: v for c, v in verdict["verdict"].items() if c != claim}
    assert set(others.values()) == {"holds"}


def test_too_few_soups_of_a_kind_is_not_a_test_and_a_gap_is_missing(monkeypatch):
    few = S.decide(_made_up(monkeypatch, common=5), S.predictions())
    assert few["outcomes"]["B1"] == few["outcomes"]["B2"] == "not tested"
    assert few["outcomes"]["B0"] == "holds" and few["verdict"]["B"] == "not tested"
    rows = _made_up(monkeypatch)
    gap = [r for r in rows if not (r["world"] == "soup-03" and r["kind"] == "standoff")]
    verdict = S.decide(gap[:-1], S.predictions())
    assert verdict["missing"] == ["soup-03 standoff", "soup-10 standoff"]
    assert verdict["verdict"] == {"S": "holds", "A": "holds", "B": "missing"}


# --- the study -----------------------------------------------------------------------------------


def test_the_study_registers_what_it_says():
    worlds, claims = S.worlds(), S.predictions()
    assert len(worlds) == 26 and len(S.jobs()) == 2 * (2 * 128 + 24 * 64) == 3584
    assert [c["label"] for c in claims][:2] == ["S random", "S standoff"] and len(claims) == 15
    assert len({c["label"] for c in claims}) == 15
    for name, world in worlds.items():
        assert min(world["seeds"]) == 101 and len(world["rules"]) == (5 if "soup" in name else 2)
    # the first look's rule sets are not the registered ones
    look = _load("scale_up_compete_first_look", ROOT / "examples/scale-up-compete/first_look.py")
    seen = {look.soup_rules(index) for index in look.SOUP_SETS}
    assert not seen & {tuple(w["rules"]) for w in worlds.values()}
    assert not set(look.PAIR_SEEDS) & set(S.PAIR_SEEDS)
    assert look.soup_rules(1) == look.soup_rules(1) != look.soup_rules(2)
    for rule in look.soup_rules(7):
        birth, survive = rule[1:].split("/S")
        assert 1 <= len(birth) <= 4 and 1 <= len(survive) <= 4


def test_the_ledger_holds_the_registration():
    path = LAB / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    claims = S.predictions()
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[: len(claims) + 1] == ["question"] + ["prediction"] * len(claims)
    question = ledger.entries[0]
    for entry, claim in zip(ledger.entries[1:], claims, strict=False):
        assert entry["body"] == {"question": question["hash"], **claim}
    if "verdict" not in kinds:  # between registration and the run, the code must not move
        assert question["body"]["sha256"] == S.question()["sha256"]


def test_the_registered_run_found_the_tie_break_matters_only_where_contests_are_common():
    """The run of 2026-11-23: every prediction held. Identical species ended level; the pairs
    showed no difference beyond their margins; the five soups with rare contests were level,
    and in all nine with common contests the standoff lowered the live fraction."""
    path = LAB / "ledger.jsonl"
    if not path.exists() or Ledger(path).entries[-1]["kind"] != "verdict":
        pytest.skip("not run yet")
    ledger = Ledger(path)
    assert [e["kind"] for e in ledger.entries[-3:]] == ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["verdict"] == {"S": "holds", "A": "holds", "B": "holds"}
    assert set(verdict["outcomes"].values()) == {"holds"} and len(verdict["outcomes"]) == 15
    assert verdict["missing"] == [] and len(ledger.entries[-2]["body"]["rows"]) == 3584
    for kind in S.KINDS:
        known = verdict["known_answer"][kind]
        assert known["n"] == 128 and known["low"] < 0.5 < known["high"]
    for claims in verdict["pairs"].values():
        for result in claims.values():
            assert -result["margin"] < result["low"] and result["high"] < result["margin"]
    soups = verdict["soups"]
    assert (soups["rare"], soups["rare_level"]) == (5, 5)
    assert (soups["common"], soups["common_differ"], soups["common_lowered"]) == (9, 9, 9)
    common = [s for s in soups["table"] if s["contested"] >= S.COMMON]
    assert -0.46 < min(s["difference"] for s in common) < -0.45
    assert -0.05 < max(s["difference"] for s in common) < -0.04
    rare = [s for s in soups["table"] if s["contested"] <= S.RARE]
    assert max(abs(s["difference"]) for s in rare) < 0.002
    # not registered: the more of a soup's births are contested, the more the standoff lowers it
    order = stats.spearmanr(
        [s["contested"] for s in soups["table"]], [s["difference"] for s in soups["table"]]
    )
    assert -0.83 < order.statistic < -0.81


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_the_study_registers_runs_and_judges_on_small_grids(monkeypatch, tmp_path):
    monkeypatch.setattr(S, "PAIR_SIDE", 32)
    monkeypatch.setattr(S, "SOUP_SIDE", 32)
    monkeypatch.setattr(S, "PAIR_SEEDS", tuple(range(9001, 9007)))
    monkeypatch.setattr(S, "SOUP_SEEDS", tuple(range(9001, 9005)))
    monkeypatch.setattr(S, "SOUP_SETS", tuple(range(9001, 9005)))
    _git(tmp_path, "init", "-q")
    study = Study(tmp_path, S.question, S.predictions, S.execute, S.decide, rerun=S.rerun)
    register(study)
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert set(verdict["verdict"]) == {"S", "A", "B"} and verdict["missing"] == []
    words = {"holds", "fails", "not tested"}
    assert set(verdict["outcomes"].values()) <= words
    assert verdict["outcomes"]["B1"] == "not tested"  # four soups cannot make six common ones
    assert len(verdict["soups"]["table"]) == 4
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    rows = ledger.entries[-2]["body"]["rows"]
    assert len(rows) == 2 * (2 * 6 + 4 * 4)
    assert S.rerun(rows[0]) == rows[0] and S.rerun(rows[-1]) == rows[-1]
    # every run of a world starts from the same grid under both tie-breaks
    starts = {(r["world"], r["seed"]): set() for r in rows}
    for r in rows:
        starts[r["world"], r["seed"]].add(r["start_sha256"])
    assert all(len(found) == 1 for found in starts.values())
    # the census dashboards' reader gives each prediction its outcome
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    table, summary = readers.READERS["scale-up-tie-break"](bodies, verdict, {})
    assert [r["label"] for r in table] == [p["label"] for p in S.predictions()]
    assert {r["outcome"] for r in table} <= {"held", "failed", "not tested"}
    assert summary.startswith("S ")


def test_verify_can_rerun_the_studys_records():
    assert load(LAB).rerun is not None
