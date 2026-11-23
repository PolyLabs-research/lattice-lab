"""The registered scale-up test (examples/scale-up-sizes and examples/scale-up-sizes-large): what
each part registers, and how a claim is judged.

The judge is tried on made-up runs whose answer is known. The runner is tried on grids of side
32 and 48 from starts 2001 and up, which the step-2 laws used and the registered parts do not.
"""

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import load, register, run

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-sizes"
LARGE = ROOT / "examples" / "scale-up-sizes-large"
COMPETE = ROOT / "examples" / "scale-up-compete"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PART1 = _load("scale_up_sizes_study", LAB / "study.py")
PART2 = _load("scale_up_sizes_large_study", LARGE / "study.py")
S = PART1.sizes

# Eight values with mean 0 and unit spread, to scatter made-up starts by.
SCATTER = [-1.4, -0.9, -0.4, -0.1, 0.1, 0.4, 0.9, 1.4]
SCATTER = [v / (sum(x * x for x in SCATTER) / 7) ** 0.5 for v in SCATTER]
SEEDS = tuple(range(1, 9))


def _run(seed, live=0.3, share=0.5, unlike=0.2, rare=8, lost=(), world="w", cells=10**8):
    """A made-up run of four species: its live fraction, species 1's share of the live cells,
    the unlike share of adjacent pairs and species 4's cells are as given at every sample."""
    alive = round(live * cells)
    first = round(share * alive)
    counts = [first, alive - first - rare - 10, 10, rare]
    return {
        "world": world,
        "side": 10000,
        "seed": seed,
        "cells": cells,
        "generations": [0, 20, 40],
        "alive": [[count] * 3 for count in counts],
        "unlike": [round(unlike * 10**8)] * 3,
        "like": [10**8 - round(unlike * 10**8)] * 3,
        "births": [100, 100, 100, 100],
        "contested": 40,
        "extinct_at": [5 if i in lost else None for i in range(4)],
    }


def _claim(family, **body):
    return {"label": f"w, side 10000: {family}", "family": family, "world": "w", "side": 10000,
            "starts": 8, **body}  # fmt: skip


# --- the pieces ----------------------------------------------------------------------------------


def test_how_few_starts_a_chance_allows():
    assert S.at_least(32, 1.0) == 32 and S.at_least(16, 1.0) == 16
    # one failure in 32 has a chance of 0.0018 at 0.999944 each: it cannot be ruled out
    assert S.at_least(32, 0.999944) == 31
    assert S.at_least(32, 0.997431) == 30
    assert S.at_least(32, 0.5) == 7  # P(at most 6 of 32) is 0.0003, P(at most 7) is 0.0011
    assert S.at_least(8, 0.05) == 0
    assert math.isclose(S.Z, 3.2905, abs_tol=1e-4)


def test_the_band_of_a_spread_is_taken_in_logarithms():
    low, high = S.band(0.004, 0.05, 8)
    width = S.Z * math.sqrt(0.05**2 + 1 / 14)
    assert math.isclose(low, 0.004 * math.exp(-width), rel_tol=1e-5)
    assert math.isclose(low * high, 0.004**2, rel_tol=1e-5)
    wide, narrow = S.band(1.0, 0.05, 16), S.band(1.0, 0.05, 32)
    assert wide[0] < narrow[0] < 1 < narrow[1] < wide[1]


def test_a_mean_is_judged_against_the_constant():
    claim = _claim("mean", quantity="live", predicted=0.3, se=0.001)
    level = [_run(s, live=0.3 + 0.004 * z) for s, z in zip(SEEDS, SCATTER, strict=True)]
    result = S.judge(claim, level, {})
    assert result["outcome"] == "holds" and abs(result["score"]) < 0.01
    assert math.isclose(result["se"], 0.004 / 8**0.5, rel_tol=1e-3)
    moved = [_run(s, live=0.31 + 0.004 * z) for s, z in zip(SEEDS, SCATTER, strict=True)]
    result = S.judge(claim, moved, {})
    assert result["outcome"] == "fails"
    assert math.isclose(result["score"], 0.01 / math.hypot(0.001, 0.004 / 8**0.5), rel_tol=1e-2)
    # the rare species is judged by its own share of the grid
    rare = _claim("mean", quantity="rare", species=4, predicted=8e-8, se=1e-8)
    assert S.judge(rare, level, {})["outcome"] == "holds"
    assert S.judge({**rare, "predicted": 2e-7}, level, {})["outcome"] == "fails"
    assert S.measured(level[0], rare) == 8e-8


def test_a_spread_is_judged_in_logarithms():
    claim = _claim("spread", quantity="share", predicted=0.004, se_log=0.05,
                   accept=S.band(0.004, 0.05, 8))  # fmt: skip

    def runs(spread):
        return [_run(s, share=0.5 + spread * z) for s, z in zip(SEEDS, SCATTER, strict=True)]

    result = S.judge(claim, runs(0.004), {})
    assert result["outcome"] == "holds" and abs(result["score"]) < 0.01
    assert S.judge(claim, runs(0.008), {})["outcome"] == "holds"  # within a factor of 2.4
    wide = S.judge(claim, runs(0.012), {})
    assert wide["outcome"] == "fails"
    assert math.isclose(wide["score"], math.log(3) / math.sqrt(0.05**2 + 1 / 14), abs_tol=0.02)
    assert S.judge(claim, runs(0.001), {})["outcome"] == "fails"
    still = S.judge(claim, runs(0.0), {})
    assert still["outcome"] == "fails" and still["measured"] == 0 and "score" not in still


def test_survival_counts_the_starts_that_keep_every_species():
    claim = _claim("survival", predicted=0.99, low=0.9, at_least=7)
    one = [_run(s, lost=(3,) if s == 2 else ()) for s in SEEDS]
    assert S.judge(claim, one, {}) == {"outcome": "holds", "measured": 7, "of": 8}
    two = [_run(s, lost=(3,) if s in (2, 5) else ()) for s in SEEDS]
    assert S.judge(claim, two, {})["outcome"] == "fails"
    other = [_run(s, lost=(0,) if s in (2, 5) else ()) for s in SEEDS]  # any species counts
    assert S.judge(claim, other, {})["measured"] == 6


def _relaxing(seed, z, c=0.7, a=-0.3, tau=40.0, cells=10**8):
    """A made-up run whose live fraction relaxes to c as c + a exp(-t / tau), a little lower or
    higher from start to start."""
    generations = list(range(0, 401, 20))
    live = [(c + a * math.exp(-t / tau)) * (1 + 0.002 * z) for t in generations]
    record = _run(seed)
    record["generations"] = generations
    record["alive"] = [[round(v * cells) for v in live], [0] * len(generations)]
    return record


def test_the_law_against_time_is_refitted_at_the_new_side():
    runs = [_relaxing(s, z) for s, z in zip(SEEDS, SCATTER, strict=True)]
    found = S.time_constants(runs, "relaxation")
    assert math.isclose(found["tau"][0], 40.0, rel_tol=1e-3) and found["tau"][1] < 0.5
    assert math.isclose(found["c"][0], 0.7, rel_tol=1e-3)
    tau = _claim("time", law="relaxation", constant="tau", predicted=40.0, se=0.5)
    refits = {}
    assert S.judge(tau, runs, refits)["outcome"] == "holds" and ("w", 10000) in refits
    assert S.judge({**tau, "predicted": 30.0}, runs, refits)["outcome"] == "fails"
    settles = _claim("time", law="relaxation", constant="c", predicted=0.7, se=0.001)
    assert S.judge(settles, runs, refits)["outcome"] == "holds"
    # a fit that cannot be made is not a test
    assert S.judge(tau, runs, {("w", 10000): None})["outcome"] == "not tested"


def test_the_verdict_counts_the_claims_by_family_and_side():
    registered = [
        _claim("mean", quantity="live", predicted=0.3, se=0.001),
        _claim("spread", quantity="live", predicted=0.004, se_log=0.05,
               accept=S.band(0.004, 0.05, 8)),
        _claim("survival", predicted=1.0, low=1.0, at_least=8),
        {**_claim("mean", quantity="rare", species=4, predicted=8e-8, se=1e-8),
         "label": "w, side 10000: mean rare"},
    ]  # fmt: skip
    rows = [_run(s, live=0.3 + 0.004 * z) for s, z in zip(SEEDS, SCATTER, strict=True)]
    verdict = S.decide(rows, registered, SEEDS)
    assert verdict["verdict"] == {
        "mean": "holds", "spread": "holds", "survival": "holds", "time": "holds"
    }  # fmt: skip
    assert verdict["claims"]["mean"] == {"holds": 2, "fails": 0, "not tested": 0, "missing": 0}
    assert verdict["by_side"] == {"10000": {"holds": 4, "fails": 0, "not tested": 0, "missing": 0}}
    assert verdict["missing"] == [] and set(verdict["details"]) == set(verdict["outcomes"])
    told = verdict["reported"]["w, side 10000"]
    assert told["starts"] == 8 and told["starts_losing_each_species"] == [0, 0, 0, 0]
    assert told["contested_share_of_births"] == 0.1
    assert told["rare_species"] == {
        "species": 4, "cells_at_the_end": [8, 8], "every_count_a_multiple_of": 8,
        "unchanged_from_generation": 0,
    }  # fmt: skip
    # a start that loses a species fails the survival claim alone
    lost = S.decide([_run(1, lost=(3,))] + rows[1:], registered[2:3], SEEDS)
    assert lost["verdict"]["survival"] == "fails" and lost["verdict"]["mean"] == "holds"
    # a start short, or one run twice, and the side is missing
    for short in (rows[:-1], rows + rows[:1]):
        verdict = S.decide(short, registered, SEEDS)
        assert set(verdict["outcomes"].values()) == {"missing"}
        assert verdict["missing"] == ["w, side 10000"] and verdict["reported"] == {}
        assert verdict["verdict"]["mean"] == "missing" and verdict["verdict"]["time"] == "holds"


# --- what is registered --------------------------------------------------------------------------


def test_what_each_part_registers():
    fitted = json.loads((COMPETE / "laws" / "results.json").read_text())["worlds"]
    for part, sides, starts in ((PART1, (512, 1024), 32), (PART2, (2048, 4096), 16)):
        claims = part.STUDY.predictions()
        assert part.SIDES == sides and len(part.SEEDS) == starts
        assert len(claims) == 62 and len({c["label"] for c in claims}) == 62
        assert [sum(c["family"] == f for c in claims) for f in S.FAMILIES] == [22, 22, 6, 12]
        assert {c["starts"] for c in claims} == {starts} and {c["level"] for c in claims} == {0.999}
        assert all(isinstance(c["claim"], str) and len(c["claim"]) < 240 for c in claims)
        by = {c["label"]: c for c in claims}
        for side in sides:
            # the means are the constants, whatever the side
            mean = by[f"soup random, side {side}: mean live"]
            assert (mean["predicted"], mean["se"]) == (0.766152, 0.000131)
            # the spreads are an amplitude over the side
            spread = by[f"pair standoff, side {side}: spread share"]
            amplitude = fitted["pair standoff"]["against_size"]["share"]["spread"]["inverse"]["a"]
            assert math.isclose(spread["predicted"], amplitude / side, rel_tol=1e-5)
            assert spread["accept"][0] < spread["predicted"] < spread["accept"][1]
            assert spread["accept"] == S.band(spread["predicted"], spread["se_log"], starts)
            # the rare species: a density, and a Poisson number of blocks of four
            for world, per_million in (("soup random", 174.452), ("soup standoff", 109.84)):
                rare = by[f"{world}, side {side}: mean rare"]
                assert rare["species"] == 4 and math.isclose(rare["predicted"] * 1e6, per_million)
                scatter = by[f"{world}, side {side}: spread rare"]
                assert math.isclose(
                    scatter["predicted"], math.sqrt(4 * rare["predicted"]) / side, rel_tol=1e-5
                )
                assert math.isclose(scatter["se_log"], rare["se"] / rare["predicted"] / 2,
                                    rel_tol=1e-5)  # fmt: skip
            assert f"pair standoff, side {side}: mean rare" not in by
            # the law against time: where it settles and how fast
            assert by[f"pair standoff, side {side}: time b"]["law"] == "algebraic_relaxation"
            assert by[f"soup standoff, side {side}: time tau"]["predicted"] == 15.120013
    # survival: the pair loses nobody; the soup may lose its rare species on side 512 alone
    fewest = {c["label"]: c["at_least"] for c in PART1.STUDY.predictions() if "at_least" in c}
    assert fewest == {
        "pair standoff, side 512: survival": 32,
        "pair standoff, side 1024: survival": 32,
        "soup random, side 512: survival": 31,
        "soup random, side 1024: survival": 32,
        "soup standoff, side 512: survival": 30,
        "soup standoff, side 1024: survival": 32,
    }
    assert {c["at_least"] for c in PART2.STUDY.predictions() if "at_least" in c} == {16}


def test_the_parts_use_fresh_starts_and_one_set_of_laws():
    laws = S.laws
    tie = _load("scale_up_tie_break_study", ROOT / "examples/scale-up-tie-break/study.py")
    look = _load("scale_up_compete_first_look", COMPETE / "first_look.py")
    seen = set(laws.SEEDS) | set(tie.PAIR_SEEDS) | set(tie.SOUP_SEEDS) | set(look.PAIR_SEEDS)
    assert PART1.SEEDS == tuple(range(3001, 3033)) and PART2.SEEDS == tuple(range(4001, 4017))
    assert not (set(PART1.SEEDS) | set(PART2.SEEDS)) & seen
    assert not set(PART1.SEEDS) & set(PART2.SEEDS)
    assert min(PART1.SIDES + PART2.SIDES) > max(laws.SIDES)
    first, second = PART1.STUDY.question(), PART2.STUDY.question()
    assert (first["id"], second["id"]) == ("scale-up-sizes", "scale-up-sizes-large")
    assert first["laws_sha256"] == second["laws_sha256"] and first["worlds"] == second["worlds"]
    assert first["sha256"]["sizes.py"] == second["sha256"]["sizes.py"]
    assert first["sha256"]["study.py"] != second["sha256"]["study.py"]
    assert (first["runs"], second["runs"]) == (192, 96) and len(first["excluded_seen"]) == 4
    assert list(first["worlds"]) == list(laws.WORLDS)
    # the smaller side is run first
    jobs = S.jobs(PART2.SIDES, PART2.SEEDS)
    assert jobs[0] == ("pair standoff", 2048, 4001) and jobs[-1] == ("soup standoff", 4096, 4016)


def test_the_runner_runs_the_worlds_the_laws_were_fitted_on():
    """One start of each world on a 32 x 32 grid ends on the grid the step-2 run ended on."""
    path = COMPETE / "laws" / "records.jsonl"
    if not path.exists():
        pytest.skip("laws.py has not been run")
    stored = {}
    for line in path.read_text().splitlines():
        record = json.loads(line)
        if record["cells"] == 1024 and record["seed"] == 2001:
            stored[S.laws.world_of(record)] = record
    for world in S.laws.WORLDS:
        row = S.run_one((world, 32, 2001))
        assert row["final_sha256"] == stored[world]["final_sha256"]
        assert row["alive"] == stored[world]["alive"] and row["unlike"] == stored[world]["unlike"]
        assert (row["world"], row["side"], row["seed"], row["cells"]) == (world, 32, 2001, 1024)


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_a_part_registers_runs_and_judges_on_small_grids(tmp_path):
    seeds = tuple(range(2001, 2007))
    (tmp_path / "study.py").write_text("# a part on small grids\n")
    study = S.build(tmp_path, (32, 48), seeds, "a test")
    _git(tmp_path, "init", "-q")
    assert len(register(study)) == 63
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert set(verdict["verdict"]) == set(S.FAMILIES) and verdict["missing"] == []
    assert set(verdict["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert len(verdict["outcomes"]) == 62 and len(verdict["reported"]) == 6
    told = verdict["reported"]["soup random, side 48"]
    assert told["rare_species"]["species"] == 4 and told["starts"] == 6
    assert set(told["live_against_time"]) == {"c", "a", "tau"}
    assert "rare_species" not in verdict["reported"]["pair standoff, side 48"]
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    rows = ledger.entries[-2]["body"]["rows"]
    assert len(rows) == 3 * 2 * 6 and [r["side"] for r in rows] == [32] * 18 + [48] * 18
    assert study.rerun(rows[0]) == rows[0] and study.rerun(rows[-1]) == rows[-1]
    # running again adds nothing: every run is already recorded
    before = (tmp_path / "records.jsonl").read_text()
    study.execute(tmp_path / "records.jsonl", 1)
    assert (tmp_path / "records.jsonl").read_text() == before
    # the census dashboards' reader gives each prediction its outcome
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    table, summary = readers.READERS["scale-up-sizes"](bodies, verdict, {})
    assert [r["label"] for r in table] == [b["label"] for b in bodies]
    assert {r["outcome"] for r in table} <= {"held", "failed", "not tested"}
    assert summary.startswith("mean ") and readers.READERS["scale-up-sizes-large"]


# --- what else the runs show (exploratory) -------------------------------------------------------


def test_the_extras_count_blocks_and_scores():
    extras = _load("scale_up_sizes_extras", LAB / "extras.py")
    counts = [0, 1, 1, 2, 2, 2, 3, 5]
    runs = [_run(s, rare=4 * n, cells=10**6) for s, n in zip(SEEDS, counts, strict=True)]
    found = extras.blocks(runs, 3)
    assert found["blocks_per_run"] == 2.0 and found["per_million_cells"] == 2.0
    assert found["starts_with_none"] == 1 and found["every_count_a_multiple_of_four"]
    assert math.isclose(found["variance_over_mean"], 1.14, abs_tol=0.005)  # 16 / 7 over 2
    odd = extras.blocks([_run(1, rare=6), _run(2, rare=8)], 3)
    assert not odd["every_count_a_multiple_of_four"]
    assert extras.blocks([_run(1, rare=0), _run(2, rare=0)], 3)["variance_over_mean"] is None
    verdict = {"details": {"a": {"score": 0.5}, "b": {"score": -2.5}, "c": {"measured": 32},
                           "d": {"score": 3.1}}}  # fmt: skip
    told = extras.scores(verdict)
    assert (told["comparisons"], told["beyond_2"], told["beyond_3"]) == (3, 2, 1)
    assert told["largest"] == 3.1 and told["expected_beyond_2"] == 0.1


def test_the_extras_say_whether_large_grids_agree():
    extras = _load("scale_up_sizes_extras", LAB / "extras.py")
    level = {side: [0.3 + 0.004 * 512 / side * z for z in SCATTER] for side in (512, 1024, 2048)}
    same = extras.agreement(level)
    assert same["sides"] == [512, 1024, 2048] and same["dof"] == 2
    assert same["chi2"] == 0 and same["chance"] == 1 and same["widest_gap"]["standard_errors"] == 0
    assert math.isclose(same["weighted_mean"][0], 0.3) and same["mean"] == [0.3, 0.3, 0.3]
    # the errors fall as one over the side, so the largest grid weighs most
    assert math.isclose(same["se"][0] / same["se"][2], 4, rel_tol=1e-4)
    moved = extras.agreement({**level, 4096: [0.301 + 0.0005 * z for z in SCATTER]})
    gap = 0.001 / math.hypot(0.001 / 8**0.5, 0.0005 / 8**0.5)
    assert moved["widest_gap"]["sides"] == [2048, 4096]
    assert math.isclose(moved["widest_gap"]["standard_errors"], gap, abs_tol=0.01)
    assert moved["chi2"] > 6 and moved["chance"] < 0.12 and moved["dof"] == 3
    # a straight line against the number of doublings: level, and then rising
    assert abs(same["change_per_doubling"][0]) < 1e-12 and same["change_per_doubling"][1] > 0
    slope, error = moved["change_per_doubling"]
    assert 0.0002 < slope < 0.001 and slope > 2 * error


def test_the_extras_set_fresh_starts_beside_the_registered_ones(tmp_path, monkeypatch):
    extras = _load("scale_up_sizes_extras", LAB / "extras.py")
    monkeypatch.setattr(extras, "RECHECK", tmp_path / "none.jsonl")
    assert extras.rechecks({}) == []
    fresh = []
    for seed, z in zip(SEEDS, SCATTER, strict=True):
        run = _run(seed, live=0.31 + 0.004 * z)
        fresh.append({**run, "rules": ["a", "b"], "tie_break": "standoff"})
    path = tmp_path / "records.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in fresh))
    monkeypatch.setattr(extras, "RECHECK", path)
    registered = [_run(s, live=0.3 + 0.004 * z) for s, z in zip(SEEDS, SCATTER, strict=True)]
    (row,) = extras.rechecks({("pair standoff", 10000): registered})
    assert (row["world"], row["side"], row["starts"], row["seeds"]) == (
        "pair standoff",
        10000,
        8,
        [1, 8],
    )
    live = row["live"]
    assert math.isclose(live["fresh"][0], 0.31) and math.isclose(live["registered"][0], 0.3)
    assert math.isclose(live["gap_in_standard_errors"], 0.01 / (0.004 / 2), abs_tol=0.01)
    assert math.isclose(live["together"][0], 0.305)
    (alone,) = extras.rechecks({})
    assert "registered" not in alone["live"] and math.isclose(alone["share"]["fresh"][0], 0.5)


def test_the_extras_put_every_start_of_the_pair_together(tmp_path, monkeypatch):
    extras = _load("scale_up_sizes_extras", LAB / "extras.py")
    monkeypatch.setattr(extras, "GAP", tmp_path / "no-ledger.jsonl")
    fresh = []
    for seed, z in zip(SEEDS, SCATTER, strict=True):
        run = _run(seed, live=0.31 + 0.004 * z, cells=2048**2)
        fresh.append({**run, "rules": ["a", "b"], "tie_break": "standoff"})
    path = tmp_path / "records.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in fresh))
    monkeypatch.setattr(extras, "RECHECK", path)
    own = {
        ("pair standoff", side): [
            _run(s, live=0.3 + 0.004 * z) for s, z in zip(SEEDS, SCATTER, strict=True)
        ]
        for side in (256, 2048, 4096)
    }
    own["soup random", 4096] = own["pair standoff", 4096]
    found = extras.every_start(own)
    assert found["samples"] == ["the scale-up test", "the re-check"]
    live = found["quantities"]["live"]
    assert set(live["by_side"]) == {"2048", "4096"}  # the pair, at the large sides only
    wide = live["by_side"]["2048"]
    assert (
        wide["the scale-up test"][0] == wide["the re-check"][0] == 8 and wide["together"][0] == 16
    )
    assert math.isclose(wide["the re-check"][1], 0.31, rel_tol=1e-4)
    assert math.isclose(wide["together"][1], 0.305, rel_tol=1e-4)
    assert set(live["by_side"]["4096"]) == {"the scale-up test", "together"}
    assert live["sides_agree"]["sides"] == [2048, 4096] and live["sides_agree"]["dof"] == 1


# --- the ledgers ---------------------------------------------------------------------------------


@pytest.mark.parametrize("part", [PART1, PART2], ids=["sizes", "sizes-large"])
def test_the_ledger_holds_the_registration(part):
    path = part.HERE / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, part.HERE) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[:63] == ["question"] + ["prediction"] * 62
    question = ledger.entries[0]
    now = part.STUDY.question()
    if question["body"]["laws_sha256"] == now["laws_sha256"]:  # the laws as they were registered
        for entry, claim in zip(ledger.entries[1:63], part.STUDY.predictions(), strict=True):
            assert entry["body"] == {"question": question["hash"], **claim}
    if "verdict" not in kinds:  # between registration and the run, nothing may move
        assert question["body"]["sha256"] == now["sha256"]
        assert question["body"]["laws_sha256"] == now["laws_sha256"]


def test_the_registered_run_at_sides_512_and_1024_held():
    """The run of 2026-11-23: all 62 predictions held. No comparison was as far as 2.3 standard
    errors, every species survived all 192 runs, and the rare species was left as blocks of
    four, as dense as on the small grids."""
    path = LAB / "ledger.jsonl"
    if not path.exists() or Ledger(path).entries[-1]["kind"] != "verdict":
        pytest.skip("not run yet")
    ledger = Ledger(path)
    assert [e["kind"] for e in ledger.entries[-3:]] == ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["verdict"] == dict.fromkeys(S.FAMILIES, "holds")
    assert set(verdict["outcomes"].values()) == {"holds"} and len(verdict["outcomes"]) == 62
    assert verdict["missing"] == [] and len(ledger.entries[-2]["body"]["rows"]) == 192
    details = verdict["details"]
    scores = {label: abs(d["score"]) for label, d in details.items() if "score" in d}
    assert len(scores) == 56 and sum(s > 2 for s in scores.values()) == 2
    assert max(scores, key=scores.get) == "pair standoff, side 512: spread share"
    assert max(scores.values()) == 2.26
    assert max(s for label, s in scores.items() if ": mean " in label) == 1.12
    for label, found in details.items():
        if label.endswith("survival"):
            assert (found["measured"], found["of"]) == (32, 32)
    # the soup's live fraction under the draw is the small grids', to four places
    for side in (512, 1024):
        live = details[f"soup random, side {side}: mean live"]
        assert abs(live["measured"] - 0.76615) < 1e-4 and live["se"] < 1e-4
    # the rare species: blocks of four, settled by the first sample, at the small grids' density
    for name, told in verdict["reported"].items():
        assert told["starts"] == 32 and not any(told["starts_losing_each_species"])
        if name.startswith("soup"):
            rare = told["rare_species"]
            assert rare["every_count_a_multiple_of"] == 4 and rare["cells_at_the_end"][0] >= 8
            assert rare["unchanged_from_generation"] == 20
    for world, per_million in (("soup random", 174.452), ("soup standoff", 109.84)):
        for side in (512, 1024):
            found = details[f"{world}, side {side}: mean rare"]
            assert math.isclose(found["predicted"] * 1e6, per_million)
            assert abs(found["measured"] * 1e6 - per_million) < 14
    # the pair's law against time: both sides give the same constants, about two standard
    # errors below those of side 256, which the looser fit there allows
    for name, value in (("b", 1.086), ("c", 0.0395)):
        found = [details[f"pair standoff, side {side}: time {name}"] for side in (512, 1024)]
        assert all(math.isclose(f["measured"], value, rel_tol=2e-3) for f in found)
        assert all(-2.2 < f["score"] < -1.7 for f in found)


def test_the_registered_run_at_sides_2048_and_4096_held():
    """The run of 2026-11-23, on a rented machine: all 62 predictions held there too. No
    comparison was as far as 2.5 standard errors, every species survived all 96 runs, and the
    rare species' blocks were as dense as on the small grids."""
    path = LARGE / "ledger.jsonl"
    if not path.exists() or Ledger(path).entries[-1]["kind"] != "verdict":
        pytest.skip("not run yet")
    ledger = Ledger(path)
    assert [e["kind"] for e in ledger.entries[-3:]] == ["run_started", "observations", "verdict"]
    verdict = ledger.entries[-1]["body"]
    assert verdict["verdict"] == dict.fromkeys(S.FAMILIES, "holds")
    assert set(verdict["outcomes"].values()) == {"holds"} and len(verdict["outcomes"]) == 62
    assert verdict["missing"] == [] and len(ledger.entries[-2]["body"]["rows"]) == 96
    # it ran from a clean checkout of the registered code, on another machine
    code = ledger.entries[-3]["body"]["provenance"]["lattice_lab"]
    assert (
        code["dirty"] is False
        and code["source"] != "file:///home/michael/Documents/dev/lattice-lab"
    )
    details = verdict["details"]
    scores = {label: abs(d["score"]) for label, d in details.items() if "score" in d}
    assert len(scores) == 56 and sum(s > 2 for s in scores.values()) == 1
    assert max(scores, key=scores.get) == "soup standoff, side 4096: spread rare"
    assert max(scores.values()) == 2.44
    assert max(s for label, s in scores.items() if ": mean " in label) == 1.38
    for label, found in details.items():
        if label.endswith("survival"):
            assert (found["measured"], found["of"]) == (16, 16)
    for name, told in verdict["reported"].items():
        assert told["starts"] == 16 and not any(told["starts_losing_each_species"])
        if name.startswith("soup"):
            rare = told["rare_species"]
            assert rare["every_count_a_multiple_of"] == 4 and rare["cells_at_the_end"][0] >= 432
            assert rare["unchanged_from_generation"] == 20
    # the rare species' density, now known to a few parts in a hundred
    for world, per_million in (("soup random", 166.3), ("soup standoff", 114.2)):
        found = details[f"{world}, side 4096: mean rare"]
        assert math.isclose(found["measured"] * 1e6, per_million, abs_tol=0.05)
        assert found["se"] * 1e6 < 2.1 and abs(found["score"]) < 0.6
    # the pair's law against time: about one and a half standard errors below side 256, as at
    # sides 512 and 1024
    for side in (2048, 4096):
        c = details[f"pair standoff, side {side}: time c"]
        b = details[f"pair standoff, side {side}: time b"]
        assert 0.0401 < c["measured"] < 0.0405 and 1.11 < b["measured"] < 1.17
        assert -1.7 < c["score"] < -1.4 and -1.7 < b["score"] < -1.2
    # each claim compares a large grid with the small grids' constant and its error. Set beside
    # each other, the pair's live fraction at the two sides is five of their own errors apart
    # (docs/scale-up-plan.md says what fresh starts made of that)
    wide, wider = (details[f"pair standoff, side {side}: mean live"] for side in (2048, 4096))
    gap = (wide["measured"] - wider["measured"]) / math.hypot(wide["se"], wider["se"])
    assert math.isclose(gap, 5.11, abs_tol=0.01)


def test_both_parts_were_registered_before_either_was_run():
    paths = [LAB / "ledger.jsonl", LARGE / "ledger.jsonl"]
    if not all(p.exists() for p in paths):
        pytest.skip("not registered yet")
    first, second = (Ledger(p).entries for p in paths)
    registered = max(e["time"] for e in first[:63] + second[:63])
    started = [e["time"] for e in first + second if e["kind"] == "run_started"]
    assert all(registered < time for time in started)
    assert first[0]["body"]["laws_sha256"] == second[0]["body"]["laws_sha256"]


def test_verify_can_rerun_both_parts_records():
    assert load(LAB).rerun is not None and load(LARGE).rerun is not None
