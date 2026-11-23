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
    assert LAWS.measure(record, "share", -1, 1) == 0.25
    assert LAWS.measure(record, "density", -1) == 0.06
    assert LAWS.measure(record, "density", 0, 1) == 0.2
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


def test_a_spread_as_an_amplitude_over_the_side():
    """The exponent held at -1, fitted in logarithms: exact data give the amplitude back with
    the error eight starts at each of seven sides allow, and scatter beyond that widens it."""
    sides = list(LAWS.SIDES)
    exact = LAWS.inverse_law(sides, [2.0 / side for side in sides], [8] * 7)
    assert math.isclose(exact["a"], 2.0) and exact["chi2_per_dof"] == 0
    assert math.isclose(exact["se_log"], (1 / (7 * 14)) ** 0.5, rel_tol=1e-5)
    value, low, high = exact["at_larger_sides"]["1024"]
    assert math.isclose(value, 2.0 / 1024, rel_tol=1e-5)  # stored to six figures
    assert math.isclose(low * high, value**2, rel_tol=1e-4)
    rough = LAWS.inverse_law(sides, [2.0 / side * (4 if side == 64 else 1) for side in sides],
                             [8] * 7)  # fmt: skip
    assert rough["chi2_per_dof"] > 1 and rough["se_log"] > exact["se_log"] and rough["a"] > 2
    by_side = {side: [0.5 + 2.0 / side * z for z in SCATTER] for side in LAWS.SIDES}
    assert math.isclose(LAWS.spread_law(by_side)["inverse"]["a"], 2.0, rel_tol=1e-6)


def _left(cells: int, *finals: int) -> list[dict]:
    """Made-up runs of three species on `cells` cells: the second ends with `finals` cells,
    reached by generation 20."""
    return [
        {
            "cells": cells,
            "rules": ["B3/S23", "B4/S3", "B36/S23"],
            "generations": [0, 20, 40, 60],
            "alive": [[500, 300, 300, 300], [100, final, final, final], [400, 200, 190, 180]],
        }
        for final in finals
    ]


def test_what_is_left_of_a_species_that_some_starts_lose():
    by_side = {50: _left(2500, 0, 4, 0, 0), 100: _left(10000, 4, 8, 0, 4)}
    law = LAWS.blocks_law(by_side, 1)
    assert law["species"] == 2 and law["rule"] == "B4/S3" and law["unit"] == 4
    assert law["units"] == 5 and law["grid_cells"] == 50000 and law["settled_by_generation"] == 20
    assert math.isclose(law["density"][0], 20 / 50000) and law["survived"] == [1, 3]
    assert law["cells_at_end"] == [1.0, 4.0]
    # five units on 50,000 cells: 0.25 expected on the small grid and 1 on the large one
    expected = [round(1 - math.exp(-0.25), 4), round(1 - math.exp(-1), 4)]
    assert law["survival_from_density"] == expected
    assert math.isclose(LAWS.block_spread(0.0004, 4, 100), 0.0004, rel_tol=1e-12)  # sqrt(1) units
    chance, low = LAWS.block_survival(0.0004, 0.0001, 4, 200)
    assert math.isclose(chance, 1 - math.exp(-4)) and low < chance
    # a species that is still changing has not settled by the first sample
    moving = {50: _left(2500, 4, 8)}
    moving[50][0]["alive"][1] = [100, 12, 8, 4]
    assert LAWS.blocks_law(moving, 1)["settled_by_generation"] == 60
    assert LAWS.blocks_law({50: _left(2500, 0, 0)}, 1)["law"] is None


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
    # every spread is an amplitude over the side, within the scatter seven sides allow
    for world in results["worlds"].values():
        for laws in world["against_size"].values():
            inverse = laws["spread"]["inverse"]
            assert inverse["chi2_per_dof"] < 3 and 0.048 <= inverse["se_log"] < 0.083
    # what is left of the soup's fourth species is blocks of four cells, settled by the first
    # sample, as many per cell at every size; their density gives the survival that was seen
    assert "blocks" not in pair
    for soup, per_million in ((draw, 174), (level, 110)):
        blocks = soup["blocks"]
        assert (blocks["species"], blocks["rule"], blocks["unit"]) == (4, "B4/S3", 4)
        assert blocks["settled_by_generation"] == 20 and 0.9 < blocks["dispersion"] < 1.2
        assert math.isclose(blocks["density"][0] * 1e6, per_million, abs_tol=1)
        for seen, starts, law in zip(
            blocks["survived"], blocks["starts"], blocks["survival_from_density"], strict=True
        ):
            assert abs(seen / starts - law) < 3.3 * (law * (1 - law) / starts) ** 0.5
        assert blocks["at_larger_sides"]["1024"]["survival"] == [1.0, 1.0]
    assert draw["blocks"]["survived"] == draw["survival"]["survived"]
    # under the standoff the smallest grid also lost other species, once or twice
    assert level["deaths_by_species"]["32"] == [1, 2, 0, 30, 1]
    assert level["blocks"]["survived"] == [2, 2, 2, 8, 15, 16, 26]
