"""The exploratory studies of several species (examples/scale-up-compete): the first look and
the laws against time and size. The fitting helpers are tried on made-up data whose law is
known; the last test reads the laws the real runs gave."""

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-compete"
sys.path.insert(0, str(LAB))


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LAWS = _load("scale_up_compete_laws", LAB / "laws.py")

# Eight values with mean 0 and unit spread, to scatter made-up starts by.
SCATTER = [-1.4, -0.9, -0.4, -0.1, 0.1, 0.4, 0.9, 1.4]
SCATTER = [v / (sum(x * x for x in SCATTER) / 7) ** 0.5 for v in SCATTER]


def test_what_is_measured_of_a_record():
    record = {
        "cells": 100,
        "alive": [[30, 6], [20, 2]],
        "unlike": [40, 1],
        "like": [60, 9],
        "extinct_at": [None, 7, None],
    }
    assert LAWS.measure(record, "live", 0) == 0.5 and LAWS.measure(record, "live", -1) == 0.08
    assert LAWS.measure(record, "share", -1) == 0.75 and LAWS.measure(record, "unlike", -1) == 0.1
    assert LAWS.measure(record, "left", 0) == 2.0
    with pytest.raises(ValueError, match="unknown quantity"):
        LAWS.measure(record, "dead", 0)
    assert LAWS.world_of({"rules": ["a", "b"], "tie_break": "standoff"}) == "pair standoff"
    assert LAWS.world_of({"rules": ["a"] * 5, "tie_break": "random"}) == "soup random"


def test_a_spread_that_falls_as_one_over_the_side_is_found():
    by_side = {side: [0.5 + 2.0 / side * z for z in SCATTER] for side in LAWS.SIDES}
    law = LAWS.spread_law(by_side)
    assert math.isclose(law["constants"]["b"][0], -1.0, abs_tol=1e-4)
    assert math.isclose(law["constants"]["a"][0], 2.0, rel_tol=1e-3)
    assert math.isclose(law["at_larger_sides"]["1024"][0], 2.0 / 1024, rel_tol=1e-3)
    assert LAWS.spread_law({32: [1.0, 1.0], 64: [1.0, 1.0]})["law"] is None


def test_a_mean_that_does_not_depend_on_the_side_is_called_constant():
    flat = {side: [0.3 + 0.01 * z for z in SCATTER] for side in LAWS.SIDES}
    law = LAWS.size_law(flat)
    assert law["law"] == "constant" and math.isclose(law["constants"]["a"][0], 0.3, abs_tol=1e-9)
    assert math.isclose(law["at_larger_sides"]["4096"][0], 0.3, abs_tol=1e-9)
    same = LAWS.size_law({side: [4.0] * 8 for side in LAWS.SIDES})
    assert same["law"] == "constant" and same["exact"]


def test_a_mean_that_grows_with_the_side_is_not_called_constant():
    growing = {side: [0.1 * side**0.5 + 0.01 * z for z in SCATTER] for side in LAWS.SIDES}
    law = LAWS.size_law(growing)
    assert law["law"] == "power" and math.isclose(law["constants"]["b"][0], 0.5, abs_tol=0.01)
    value, low, high = law["at_larger_sides"]["1024"]
    assert low < 0.1 * 32 < high and math.isclose(value, 3.2, rel_tol=0.02)


def test_a_power_law_in_time_is_chosen_and_its_exponent_recovered():
    generations = list(range(0, 1001, 50))
    runs = []
    for z in SCATTER:
        live = [0.5] + [0.8 * g**-0.4 * (1 + 0.03 * z) for g in generations[1:]]
        runs.append(
            {
                "cells": 10**6,
                "generations": generations,
                "alive": [[round(v * 10**6) for v in live], [0] * len(generations)],
            }
        )
    law = LAWS.time_law(runs, "live")
    assert law["law"] == "power" and law["starts"] == 8 and law["generations"] == [50, 1000]
    assert math.isclose(law["constants"]["b"][0], -0.4, abs_tol=0.005)
    low, high = law["intervals"]["b"]
    assert low <= law["constants"]["b"][0] <= high


def test_the_runs_are_the_two_worlds_at_seven_sizes():
    tasks = LAWS.tasks()
    assert len(tasks) == 3 * 7 * 32 and tasks[0].grid == 256 and tasks[-1].grid == 32
    assert {t.tie_break for t in tasks if len(t.rules) == 2} == {"standoff"}
    assert {t.tie_break for t in tasks if len(t.rules) == 5} == {"random", "standoff"}
    # the soup is number 19 of the tie-break test, and no start is one of that test's
    study = _load("scale_up_tie_break_study", ROOT / "examples/scale-up-tie-break/study.py")
    assert list(LAWS.SOUP_RULES) == study.worlds()["soup-19"]["rules"]
    assert not set(LAWS.SEEDS) & (set(study.PAIR_SEEDS) | set(study.SOUP_SEEDS))


def test_survival_against_size_is_fitted_with_a_binomial_likelihood():
    """Made-up counts from 1 - exp(-(side / 100)^2), the form independent patches give."""
    counts = {side: (round(200 * (1 - math.exp(-((side / 100) ** 2)))), 200) for side in LAWS.SIDES}
    law = LAWS.survival_law(counts)
    assert math.isclose(law["patches"]["d"][0], 2.0, abs_tol=0.1)
    assert 70 < law["half_survive_at_side"] < 95  # 100 sqrt(ln 2) = 83
    assert law["at_larger_sides"]["1024"][0] > 0.999
    assert LAWS.survival_law({32: (8, 8), 64: (8, 8)})["law"] is None


def test_the_laws_the_runs_gave():
    """The run of 2026-11-23 (exploratory): 32 starts at each of seven sizes. Means do not
    depend on the size, spreads fall as one over the side, and the soup's rare species
    survives on large grids."""
    path = LAB / "laws" / "results.json"
    if not path.exists():
        pytest.skip("laws.py has not been run")
    results = json.loads(path.read_text())
    assert results["sides"] == list(LAWS.SIDES)
    assert set(results["worlds"]) == set(LAWS.WORLDS)
    for world in results["worlds"].values():
        assert set(world["starts"].values()) == {32}
        for laws in world["against_size"].values():
            assert laws["mean"]["law"] == "constant"
            exponent, error = laws["spread"]["constants"]["b"]
            assert abs(exponent + 1) < 2 * error and error < 0.11
    pair, draw, level = (
        results["worlds"][w] for w in ("pair standoff", "soup random", "soup standoff")
    )
    assert pair["against_time"]["live"]["law"] == "algebraic_relaxation"
    assert pair["against_time"]["live"]["chosen"]["algebraic_relaxation"] == 1.0
    assert (
        draw["against_time"]["live"]["law"] == level["against_time"]["live"]["law"] == "relaxation"
    )
    assert math.isclose(
        pair["against_size"]["live"]["mean"]["constants"]["a"][0], 0.0486, abs_tol=5e-4
    )
    assert math.isclose(
        pair["against_size"]["share"]["mean"]["constants"]["a"][0], 0.5616, abs_tol=5e-4
    )
    assert math.isclose(
        draw["against_size"]["live"]["mean"]["constants"]["a"][0], 0.7662, abs_tol=5e-4
    )
    assert math.isclose(
        level["against_size"]["live"]["mean"]["constants"]["a"][0], 0.4999, abs_tol=5e-4
    )
    # nobody is lost in the pair; the soup's fourth species is, on small grids
    assert pair["survival"]["survived"] == [32] * 7 and pair["survival"]["law"] is None
    assert draw["survival"]["survived"] == [2, 2, 4, 11, 18, 22, 29]
    assert level["survival"]["survived"] == [1, 2, 2, 8, 15, 16, 26]
    assert draw["deaths_by_species"]["32"] == [0, 0, 0, 30, 0]
    assert 120 < draw["survival"]["half_survive_at_side"] < 128
    assert 150 < level["survival"]["half_survive_at_side"] < 163
    for soup in (draw, level):
        d, error = soup["survival"]["patches"]["d"]
        assert abs(d - 2) < error and soup["survival"]["at_larger_sides"]["1024"][0] > 0.98
