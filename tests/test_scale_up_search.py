"""The search for worlds that organise themselves (examples/scale-up-search): the correlation
area on made-up fields whose answer is known, on worlds known from the literature, and the
search's own sorting.

The real worlds here are small (side 128) and start from seed 9001, which no study uses.
"""

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-search"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ORG = _load("scale_up_search_organised", LAB / "organised.py")
SEARCH = _load("scale_up_search_search", LAB / "search.py")
CONTESTS = _load("scale_up_search_contests", LAB / "contests.py")
CONFIRM = _load("scale_up_search_confirm", LAB / "confirm.py")
PICTURES = _load("scale_up_search_pictures", LAB / "pictures.py")
LONG = _load("scale_up_search_long", LAB / "long.py")
RIVALS = _load("scale_up_search_rivals", LAB / "rivals.py")


# --- the correlation area, where the answer is known ---------------------------------------------


def test_independent_cells_have_an_area_of_one_at_every_block():
    rng = np.random.default_rng(9001)
    for share in (0.1, 0.5, 0.8):
        field = (rng.random((512, 512)) < share).astype(np.int8)
        for block in ORG.BLOCKS:
            assert abs(ORG.area(field, block) - 1) < 0.25, (share, block)
            for mask in ORG.MASKS:
                assert abs(ORG.area(field, block, mask) - 1) < 0.25, (share, block, mask)


def test_tiles_have_the_area_of_a_tile():
    """Tiles of 8 x 8 cells, each all 0 or all 1 by a fair coin: the area is the block's own
    while blocks are inside a tile, and a tile's from there on."""
    rng = np.random.default_rng(9001)
    tiles = np.repeat(np.repeat((rng.random((64, 64)) < 0.5).astype(np.int8), 8, 0), 8, 1)
    areas = [ORG.area(tiles, block) for block in ORG.BLOCKS]
    assert all(
        math.isclose(a, b * b, rel_tol=0.01) for a, b in zip(areas[:3], (2, 4, 8), strict=True)
    )
    assert all(abs(a - 64) < 12 for a in areas[3:])
    assert math.isclose(ORG.scaling(areas, ORG.BLOCKS, 2, 8), 2.0, abs_tol=0.01)
    assert abs(ORG.scaling(areas, ORG.BLOCKS, 8, 32)) < 0.15


def test_a_chequerboard_is_ordered_only_against_its_own_mask():
    board = (np.indices((64, 64)).sum(axis=0) % 2 == 0).astype(np.int8)
    assert [ORG.area(board, block) for block in ORG.BLOCKS] == [0.0] * 5
    assert [ORG.area(board, block, "chequered") for block in ORG.BLOCKS] == [4, 16, 64, 256, 1024]
    assert ORG.area(board, 8, "rows") == ORG.area(board, 8, "columns") == 0
    stripes = np.zeros((64, 64), dtype=np.int8)
    stripes[::2] = 1
    assert ORG.area(stripes, 8, "rows") == 64 and ORG.area(stripes, 8, "chequered") == 0
    assert ORG.signs(4, "columns").tolist() == [[1, -1, 1, -1]] * 4


def test_a_field_all_but_empty_or_full_has_no_area():
    field = np.zeros((64, 64), dtype=np.int8)
    assert ORG.area(field, 8) is None
    field[:1, :20] = 1  # twenty live cells in 4,096: under one in a hundred
    assert ORG.area(field, 8) is None and ORG.area(1 - field, 8) is None
    assert ORG.scaling([1.0, None, 3.0], (2, 4, 8), 2, 4) is None
    assert ORG.growth([1.0, None, 3.0], (1, 2, 4)) is None and ORG.growth([2.0], (1,)) is None


def test_growth_is_the_power_of_time():
    times = (128, 256, 512)
    assert math.isclose(ORG.growth([t**0.5 for t in times], times), 0.5)
    assert math.isclose(ORG.growth([7.0, 7.0, 7.0], times), 0.0, abs_tol=1e-12)
    assert math.isclose(ORG.scaling([3.0, 12.0, 48.0], (4, 8, 16), 4, 16), 2.0)


def test_the_clock_that_goes_with_a_zoom_out():
    """A made-up world whose domains have a side of the square root of its age: seen through
    blocks twice the size, four times later, it is the same picture; twice later is too soon,
    eight times later too late. A world of patches has no such clock at all."""
    blocks, times = (4, 8, 16, 32, 64), (64, 128, 256, 512, 1024, 2048)

    def picture(block, time, power=0.5):
        x = block / time**power
        return block * block / (1 + x * x)  # block^2 inside a domain, the domain's area beyond

    areas = [[picture(b, t) for b in blocks] for t in times]
    assert all(math.isclose(q, 1) for q in ORG.clock(areas, blocks, times, 4))
    assert len(ORG.clock(areas, blocks, times, 4)) == 4 * 4  # four pairs of times, four of blocks
    assert all(q < 0.99 for q in ORG.clock(areas, blocks, times, 2))
    assert all(q > 1.01 for q in ORG.clock(areas, blocks, times, 8))
    light = [[picture(b, t, power=1.0) for b in blocks] for t in times]
    assert all(math.isclose(q, 1) for q in ORG.clock(light, blocks, times, 2))
    patches = [[6.0] * len(blocks)] * len(times)
    assert ORG.clock(patches, blocks, times, 4) == []  # under eight cells: the grain
    assert set(ORG.clock(patches, blocks, times, 4, least=1.0)) == {0.25}
    gaps = [[None] * len(blocks)] * len(times)
    assert ORG.clock(gaps, blocks, times, 4) == [] and ORG.clock(areas, blocks, times, 3) == []


# --- worlds whose kind is known ------------------------------------------------------------------


def test_the_measure_tells_known_worlds_apart():
    """On a 128 x 128 grid: Life is patches of a few cells; Vote forms domains and stops;
    Anneal's domains keep growing."""
    times = (32, 64, 128, 256)
    found = {
        name: ORG.profile((rule,), "standoff", 128, 9001, times)
        for name, rule in (("Life", "B3/S23"), ("Vote", "B5678/S45678"),
                           ("Anneal", "B4678/S35678"))
    }  # fmt: skip
    for name, record in found.items():
        assert record["times"] == list(times) and record["blocks"] == list(ORG.BLOCKS), name
        assert set(record["fields"]) == {"live", "live, chequered", "live, rows", "live, columns"}
    at_16 = {name: [row[3] for row in r["fields"]["live"]["area"]] for name, r in found.items()}
    assert max(at_16["Life"]) < 16
    assert at_16["Vote"][-1] > 16 and found["Vote"]["changed"] == 0  # domains, and stopped
    assert at_16["Vote"][-1] == at_16["Vote"][-2]
    assert at_16["Anneal"][-1] > 60 and at_16["Anneal"][-1] > 1.5 * at_16["Anneal"][0]
    assert ORG.growth(at_16["Anneal"][-3:], times[-3:]) > 0.25
    assert found["Anneal"]["changed"] > 0
    # several species are read one by one as well as together
    pair = ORG.profile(("B3/S23", "B36/S23"), "standoff", 64, 9001, (16, 32))
    assert {"live", "species 1", "species 2"} <= set(pair["fields"])
    again = ORG.profile(("B3/S23", "B36/S23"), "standoff", 64, 9001, (16, 32))
    assert again == pair and len(pair["final_sha256"]) == 64


# --- the search ----------------------------------------------------------------------------------


def test_the_search_covers_what_it_says():
    worlds = SEARCH.worlds()
    families = [w["family"] for w in worlds]
    assert len(worlds) == 2407 and len({SEARCH.key(w) for w in worlds}) == 2407
    assert {f: families.count(f) for f in set(families)} == {
        "known": 7, "soup 2": 300, "soup 3": 300, "soup 5": 300, "rule": 1200,
        "near-majority": 300,
    }  # fmt: skip
    assert [len(w["rules"]) for w in worlds if w["family"] == "soup 3"][:2] == [3, 3]
    # the same rule set under both tie-breaks
    first, second = (w for w in worlds if w["family"] == "soup 5" and w["index"] == 50001)
    assert first["rules"] == second["rules"]
    assert {first["tie_break"], second["tie_break"]} == {"random", "standoff"}
    # some draws repeat a rule: the write-up counts each rule once
    drawn = {family: [w["rules"][0] for w in worlds if w["family"] == family]
             for family in ("rule", "near-majority")}  # fmt: skip
    assert len(set(drawn["rule"])) == 1196 and len(set(drawn["near-majority"])) == 172
    # the draws are the same every time, and even over the rules
    assert SEARCH.random_rule(7) == SEARCH.random_rule(7) != SEARCH.random_rule(8)
    births = [SEARCH.random_rule(i).split("/")[0][1:] for i in SEARCH.RULES]
    assert 4.3 < sum(map(len, births)) / len(births) < 4.7
    # a near-majority rule is two thresholds with at most two counts changed
    for index in range(1, 40):
        birth, survive = SEARCH.near_majority(index)[1:].split("/S")
        changed = 0
        for counts in (birth, survive):
            have = {int(c) for c in counts}
            best = min(len(have ^ set(range(t, 9))) for t in range(0, 10))
            changed += best
        assert changed <= 2, SEARCH.near_majority(index)


def _record(areas_32, share=0.5, changed=0.01, family="rule", name=None, species=()):
    """A made-up record whose live cells have these areas at block 32, reading by reading.
    With `species`, a world of that many species holding those shares of the grid at the end,
    each with the live cells' areas."""
    area = [[1.0, 1.0, a / 4, a / 2, a] for a in areas_32]
    fields = {"live": {"share": [share] * 5, "area": area},
              "live, rows": {"share": [share] * 5, "area": [[1.0] * 5] * 5}}  # fmt: skip
    for number, held in enumerate(species, start=1):
        fields[f"species {number}"] = {"share": [held] * 5, "area": area}
    return {
        "family": family, "index": 1, "name": name, "tie_break": "standoff",
        "rules": ["B3/S23"] * max(1, len(species)),
        "side": 256, "times": [32, 64, 128, 256, 512], "blocks": [2, 4, 8, 16, 32],
        "changed": changed, "fields": fields,
    }  # fmt: skip


def test_what_the_search_calls_a_world():
    patches = SEARCH.describe(_record([6, 6, 7, 6, 6]))
    assert patches["called"] == "patches" and patches["field"] == "live" and patches["area"] == 6
    stopped = SEARCH.describe(_record([30, 40, 50, 50, 50], changed=0.0))
    assert stopped["called"] == "organised" and stopped["growth"] == 0
    growing = SEARCH.describe(_record([20, 40, 80, 160, 320]))
    assert growing["called"] == "growing" and math.isclose(growing["growth"], 1.0)
    assert math.isclose(growing["scaling"], 1.0) and growing["area_over_time"][-1] == 320
    dead = _record([6] * 5)
    for field in dead["fields"].values():
        field["area"] = [[None] * 5] * 5
    assert SEARCH.describe(dead)["called"] == "dead"
    # the field with the largest area is the one a world is called by
    masked = _record([6] * 5)
    masked["fields"]["live, rows"]["area"] = [[1.0, 4.0, 16.0, 60.0, 200.0]] * 5
    assert SEARCH.describe(masked)["field"] == "live, rows"
    told = SEARCH.summarise([_record([6] * 5), _record([20, 40, 80, 160, 320]),
                             _record([6] * 5, family="known", name="Life")])  # fmt: skip
    assert told["families"]["rule"] == {"worlds": 2, "dead": 0, "patches": 1, "organised": 0,
                                        "growing": 1, "contested": 0,
                                        "growing and contested": 0}  # fmt: skip
    assert len(told["growing"]) == 1 and told["known"][0]["name"] == "Life"


def test_a_world_is_contested_only_if_two_species_hold_ground():
    """One cell in twenty or more at the end. A soup whose second species has all but gone is
    a one-species world, whatever it is called."""
    alone = SEARCH.describe(_record([6] * 5, share=0.4))
    assert alone["shares"] == [0.4] and alone["holding"] == 1
    lone = SEARCH.describe(_record([20, 40, 80, 160, 320], species=(0.45, 0.004)))
    assert lone["called"] == "growing" and lone["shares"] == [0.45, 0.004]
    assert lone["holding"] == 1
    shared = SEARCH.describe(_record([20, 40, 80, 160, 320], species=(0.3, 0.05, 0.049)))
    assert shared["holding"] == 2
    told = SEARCH.summarise([_record([20, 40, 80, 160, 320], family="soup 2",
                                     species=shares)
                             for shares in ((0.45, 0.004), (0.3, 0.2), (0.3, 0.2))])  # fmt: skip
    assert told["families"]["soup 2, standoff"] == {
        "worlds": 3, "dead": 0, "patches": 0, "organised": 0, "growing": 3, "contested": 2,
        "growing and contested": 2,
    }  # fmt: skip
    # one field of a world, read on its own
    one = SEARCH.reading(_record([20, 40, 80, 160, 320]), "live, rows")
    assert one["called"] == "patches" and one["area"] == 1 and one["field"] == "live, rows"


# --- the contests --------------------------------------------------------------------------------


def _found(rules, area, called="growing", shares=None, family="rule", index=1):
    """A world as the screen describes it, as far as the contests read it."""
    shares = shares or [0.5] * len(rules)
    return {"family": family, "index": index, "tie_break": "standoff", "rules": list(rules),
            "called": called, "field": "live", "area": area, "growth": 0.5, "shares": shares,
            "holding": sum(share >= 0.05 for share in shares)}  # fmt: skip


def test_the_rules_that_get_a_rival():
    """Every one-species rule that grew, and the species left alone in a soup that grew: each
    once, the largest area first."""
    found = [
        _found(["B4678/S35678"], 455.0),
        _found(["B3/S23"], 11.0, called="patches"),
        _found(["B5/S67", "B013/S1"], 438.0, shares=[0.0, 0.44], family="soup 2", index=20032),
        _found(["B015/S1", "B15/S7"], 18.0, shares=[0.275, 0.087], family="soup 2"),  # shared
        _found(["B013/S1"], 300.0, index=7),  # the same rule again, with less area
        _found(["B3678/S34678"], 525.0, family="known", index=7),
    ]
    rules = CONTESTS.growers(found)
    assert [r["rule"] for r in rules] == ["B3678/S34678", "B4678/S35678", "B013/S1"]
    assert rules[2]["area"] == 438.0 and "the species left" in rules[2]["source"]
    assert rules[0]["source"] == "known 7"
    # the share of the grid each rule's own cells started with, where it grew
    assert [r["density"] for r in rules] == [0.5, 0.5, 0.25]
    worlds = CONTESTS.worlds(rules)
    assert len(worlds) == len({CONTESTS.key(w) for w in worlds}) == 3 * 2 * 2 + 3 * 2
    own = [w for w in worlds if w["family"] == "contest" and w["index"] == 3]
    assert {tuple(w["rules"]) for w in own} == {("B013/S1", "B013/S1")}
    assert sorted((w["density"], w["tie_break"]) for w in own) == [
        (0.5, "random"), (0.5, "standoff"), (1.0, "random"), (1.0, "standoff"),
    ]  # fmt: skip
    pairs = [w for w in worlds if w["family"] == "pair"]
    assert {w["index"] for w in pairs} == {102, 103, 203}
    assert all(w["density"] == 1.0 and len(set(w["rules"])) == 2 for w in pairs)
    # only the strongest rules start half-full too, and only the strongest meet each other
    many = [{"rule": f"B{i}/S", "source": "", "field": "live", "area": 1.0, "growth": 0.5}
            for i in range(200)]  # fmt: skip
    worlds = CONTESTS.worlds(many)
    contests = [w for w in worlds if w["family"] == "contest"]
    assert len(contests) == 2 * (CONTESTS.MOST + CONTESTS.HALF)
    assert len(worlds) - len(contests) == CONTESTS.PAIRED * (CONTESTS.PAIRED - 1)


def test_what_a_contest_comes_to():
    def contest(areas_32, species, live=1.0, quiet=None):
        """Two species whose cells have these areas at block 32, on a grid whose live cells
        have the area `live` at the end: small where a block holds one species or the other
        (the live cells are then spread evenly), large where the two share their ground."""
        record = _record(areas_32, family="contest", species=species)
        record |= {"density": 1.0, "source": "made up", "name": "a rule against itself"}
        record["fields"]["live"] = {"share": [sum(species)] * 5, "area": [[live] * 5] * 5}
        if quiet is not None:  # the second species' cells in patches
            record["fields"]["species 2"]["area"] = [[1.0] * 5] * 5
        return CONTESTS.describe(record)

    growing = contest([20, 40, 80, 160, 320], (0.25, 0.25))
    assert growing["verdict"] == "growing territories" and growing["holding"] == 2
    assert growing["apart"] < -0.99
    assert growing["territories"][0] == {"called": "growing", "area": 320, "scaling": 1.0,
                                         "growth": 1.0}  # fmt: skip
    assert contest([50] * 5, (0.25, 0.25))["verdict"] == "standing territories"
    # the same areas where the two species come and go together: no territories
    shared = contest([20, 40, 80, 160, 320], (0.25, 0.25), live=960.0)
    assert shared["verdict"] == "together" and shared["apart"] > 0.99
    # one species organised and the other in patches: nothing is kept apart
    loose = contest([20, 40, 80, 160, 320], (0.25, 0.25), live=233.0, quiet=True)
    assert loose["verdict"] == "together" and -0.35 < loose["apart"] < -0.25
    assert contest([6] * 5, (0.3, 0.3))["verdict"] == "mixed"
    assert contest([20, 40, 80, 160, 320], (0.9, 0.01))["verdict"] == "one left"
    assert contest([6] * 5, (0.01, 0.02))["verdict"] == "dead"
    found = [contest([20, 40, 80, 160, 320], (0.25, 0.25)),
             contest([40, 80, 160, 320, 640], (0.25, 0.25)),
             contest([6] * 5, (0.3, 0.3))]  # fmt: skip
    told = CONTESTS.summarise(found, [])
    assert told["tallies"] == {"contest, full start, standoff": {
        "contests": 3, "dead": 0, "one left": 0, "growing territories": 2,
        "standing territories": 0, "together": 0, "mixed": 1}}  # fmt: skip
    assert [f["territories"][0]["area"] for f in told["growing territories"]] == [640, 320]
    assert told["standing territories"] == []


def test_the_rules_that_meet_each_other_afterwards():
    """Every rule that held territories against its copy, growing or standing, in any of its
    contests: each once, two at a time, under both tie-breaks."""

    def told(rule, verdict, family="contest"):
        return {"family": family, "rules": [rule, rule], "verdict": verdict}

    found = [told("B2378/S25678", "growing territories"), told("B2378/S25678", "mixed"),
             told("B4678/S35678", "dead"), told("B2/S0", "standing territories"),
             told("B013/S1", "together"), told("B015/S1", "growing territories"),
             told("B9/S9", "growing territories", family="pair")]  # fmt: skip
    worlds = CONTESTS.crosses(found)
    assert [(w["name"], w["tie_break"]) for w in worlds] == [
        ("B2378/S25678 against B2/S0", "random"), ("B2378/S25678 against B2/S0", "standoff"),
        ("B2378/S25678 against B015/S1", "random"), ("B2378/S25678 against B015/S1", "standoff"),
        ("B2/S0 against B015/S1", "random"), ("B2/S0 against B015/S1", "standoff"),
    ]  # fmt: skip
    assert {w["family"] for w in worlds} == {"cross"} and {w["density"] for w in worlds} == {1.0}
    assert len({CONTESTS.key(w) for w in worlds}) == 6
    assert CONTESTS.crosses([told("B4678/S35678", "dead")]) == []


def test_species_that_keep_apart_on_a_real_grid():
    """The measure of keeping apart against grids made by hand: tiles of one species or
    another, 32 cells wide, and tiles in which the species are mixed."""
    rng = np.random.default_rng(9001)
    side, blocks = 256, (8, 16, 32)

    def record(grid, species=2):
        fields = {}
        for name, field in ORG.fields(grid, species).items():
            fields[name] = {"share": [float(field.mean())],
                            "area": [[ORG.area(field, b) for b in blocks]]}  # fmt: skip
        return {"blocks": list(blocks), "rules": ["B3/S23"] * species, "fields": fields}

    def tiles(values):
        return np.repeat(np.repeat(values, 32, 0), 32, 1)

    thin = rng.random((side, side)) < 0.5
    own = tiles(rng.integers(1, 3, (8, 8)))  # each tile one species or the other
    assert CONTESTS.apart(record(np.where(thin, own, 0))) < -0.95
    lit = tiles(rng.random((8, 8)) < 0.5)  # live tiles and empty ones
    mixed = np.where(lit & thin, rng.integers(1, 3, (side, side)), 0)
    assert CONTESTS.apart(record(mixed)) > 0.95
    alone = np.where(thin, 1, 0)  # no second species at all
    assert CONTESTS.apart(record(alone)) is None
    # three species that share the grid out: a pair goes together as -1 / (3 - 1)
    three = tiles(np.arange(64).reshape(8, 8) % 3 + 1)
    assert abs(CONTESTS.apart(record(np.where(thin, three, 0), 3)) + 0.5) < 0.05
    mixed = np.where(lit & thin, rng.integers(1, 4, (side, side)), 0)
    assert CONTESTS.apart(record(mixed, 3)) > 0.9


def test_the_copies_that_are_run_afterwards():
    found = [{"family": "contest", "rules": ["B2378/S25678"] * 2, "verdict": v}
             for v in ("growing territories", "mixed")]  # fmt: skip
    found += [{"family": "contest", "rules": ["B4678/S35678"] * 2, "verdict": "dead"}]
    worlds = CONTESTS.copies(found)
    assert [(w["family"], w["tie_break"], len(w["rules"])) for w in worlds] == [
        ("3 copies", "random", 3), ("3 copies", "standoff", 3),
        ("5 copies", "random", 5), ("5 copies", "standoff", 5),
    ]  # fmt: skip
    assert {w["rules"][0] for w in worlds} == {"B2378/S25678"}
    assert {w["density"] for w in worlds} == {1.0}
    assert len({CONTESTS.key(w) for w in worlds}) == 4


def test_the_rules_one_count_away():
    near = CONTESTS.neighbours("B2378/S25678")
    assert len(near) == len(set(near)) == 18 and "B2378/S25678" not in near
    assert near[0] == "B02378/S25678" and near[2] == "B378/S25678"  # 0 put in, 2 taken out
    assert near[9] == "B2378/S025678" and near[17] == "B2378/S2567"
    assert CONTESTS.neighbours("B/S")[:2] == ["B0/S", "B1/S"]
    found = [{"family": "contest", "rules": [rule] * 2, "verdict": verdict}
             for rule, verdict in (("B015/S1", "growing territories"),
                                   ("B2378/S25678", "growing territories"),
                                   ("B2378/S25678", "growing territories"),
                                   ("B2/S0", "standing territories"))]  # fmt: skip
    worlds = CONTESTS.variants(found)
    assert len(worlds) == len({CONTESTS.key(w) for w in worlds}) == 36
    assert {w["rules"][0] for w in worlds} == {"B2378/S25678"}  # the rule with the most
    assert {w["rules"][1] for w in worlds} == set(near)
    assert {w["density"] for w in worlds} == {1.0}
    assert CONTESTS.variants([{"family": "contest", "rules": ["B3/S23"] * 2,
                               "verdict": "mixed"}]) == []  # fmt: skip


# --- every rule against its copy -----------------------------------------------------------------


def test_every_rule_of_the_draw_gets_a_rival():
    rules = RIVALS.rules()
    assert len(rules) == len({r["rule"] for r in rules}) == 1196
    assert rules[0] == {"index": 1, "rule": SEARCH.random_rule(1)}
    assert {"index": 1107, "rule": "B2378/S25678"} in rules  # under the number it was drawn at
    worlds = RIVALS.worlds()
    assert len(worlds) == len({CONTESTS.key(w) for w in worlds}) == 4 * 1196
    assert {w["density"] for w in worlds[: 2 * 1196]} == {1.0}  # the full starts first
    assert {w["density"] for w in worlds[2 * 1196 :]} == {0.5}
    first = worlds[:2]
    assert [w["tie_break"] for w in first] == ["random", "standoff"]
    assert all(w["rules"] == [rules[0]["rule"]] * 2 and w["family"] == "copy" for w in first)


def test_what_the_rules_come_to_against_their_copies():
    def told(rule, index, density, kind, verdict, area=0.0):
        territories = [{"area": area}, {"area": area / 2}]
        return {"rules": [rule, rule], "index": index, "density": density, "tie_break": kind,
                "verdict": verdict, "territories": territories}  # fmt: skip

    found = [
        # territories under both tie-breaks, growing under one
        told("B2378/S25678", 1, 1.0, "random", "growing territories", 100.0),
        told("B2378/S25678", 1, 1.0, "standoff", "standing territories", 160.0),
        told("B2378/S25678", 1, 0.5, "random", "mixed"),
        told("B2378/S25678", 1, 0.5, "standoff", "mixed"),
        # under the standoff only, and only from the half-full start
        told("B2/S0", 2, 1.0, "random", "mixed"),
        told("B2/S0", 2, 1.0, "standoff", "dead"),
        told("B2/S0", 2, 0.5, "random", "together", 30.0),
        told("B2/S0", 2, 0.5, "standoff", "standing territories", 26.0),
        # under the draw only
        told("B3/S23", 3, 1.0, "random", "standing territories", 20.0),
        told("B3/S23", 3, 1.0, "standoff", "one left"),
        # neither
        told("B4678/S35678", 4, 1.0, "random", "dead"),
        told("B4678/S35678", 4, 1.0, "standoff", "dead"),
    ]
    entries = RIVALS.by_rule(found)
    assert [(e["rule"], e["holds"]) for e in entries] == [
        ("B2378/S25678", "both"), ("B2/S0", "standoff only"), ("B3/S23", "draw only"),
        ("B4678/S35678", "neither"),
    ]  # fmt: skip
    assert [e["territory"] for e in entries] == [160.0, 26.0, 20.0, 0.0]  # not the 30 held together
    assert [e["growing"] for e in entries] == [True, False, False, False]
    assert entries[0]["verdicts"]["full start, standoff"] == "standing territories"
    assert entries[1]["verdicts"]["half-full start, random"] == "together"
    alone = {"B2378/S25678": {"called": "growing", "changed": 0.4},
             "B2/S0": {"called": "patches", "changed": 0.3},
             "B3/S23": {"called": "patches", "changed": 0.004}}  # fmt: skip
    summary = RIVALS.summarise(found, alone)
    assert summary["rules"] == 4 and summary["growing"] == 1
    assert summary["holds"] == {"both": 1, "standoff only": 1, "draw only": 1, "neither": 1}
    assert summary["tallies"]["full start, standoff"] == {
        "contests": 4, "dead": 2, "one left": 1, "growing territories": 0,
        "standing territories": 1, "together": 0, "mixed": 0,
    }  # fmt: skip
    assert summary["alone"]["patches"] == {"both": 0, "standoff only": 1, "draw only": 1,
                                           "neither": 0}  # fmt: skip
    assert summary["alone"]["not screened"]["neither"] == 1
    assert summary["alone"]["dead"] == dict.fromkeys(RIVALS.HOLDS, 0)  # every call has its row
    # how busy each rule is alone, and the fewest of its own kind a birth needs
    assert summary["activity alone"]["busy"] == {"both": 1, "standoff only": 1, "draw only": 0,
                                                 "neither": 0}  # fmt: skip
    assert summary["activity alone"]["still"]["draw only"] == 1
    least = summary["least birth"]
    assert least["2"] == {"both": 1, "standoff only": 1, "draw only": 0, "neither": 0}
    assert least["3"]["draw only"] == 1 and least["4 or more"]["neither"] == 1
    assert least["0"] == least["1"] == least["never born"] == dict.fromkeys(RIVALS.HOLDS, 0)
    few = summary["least birth 2 or 3"]  # B2378/S25678 and B3/S23 survive on 2, B2/S0 does not
    assert few["survives on 1 or 2"] == {"both": 1, "standoff only": 0, "draw only": 1,
                                         "neither": 0}  # fmt: skip
    assert few["survives on neither"]["standoff only"] == 1
    assert sum(sum(row.values()) for row in few.values()) == 3  # Anneal needs four: left out
    # the two cuts together, with the rules that die in every contest set aside
    assert [e["dies"] for e in entries] == [False, False, False, True]
    assert summary["needs its own kind"] == {
        "rules": 1, "die in every contest": 0,
        "of the rest": {"both": 0, "standoff only": 1, "draw only": 0, "neither": 0},
    }  # fmt: skip
    assert summary["does not"]["rules"] == 3 and summary["does not"]["die in every contest"] == 1
    assert summary["does not"]["of the rest"] == {"both": 1, "standoff only": 0, "draw only": 1,
                                                  "neither": 0}  # fmt: skip
    # the first cut apart for the rules it was read off and the others: none of these four
    # made-up rules is among the first 458 of the draw, so all sit with the others
    assert summary["least birth, the other rules"] == least
    read_off = summary["least birth, the rules it was read off"]
    assert all(row == dict.fromkeys(RIVALS.HOLDS, 0) for row in read_off.values())
    assert [e["rule"] for e in summary["territories"]] == ["B2378/S25678", "B2/S0", "B3/S23"]
    # which counts the rules with territories share: birth on 2 in two of the three, of
    # three in four of all the rules; survival on 8 in one of three
    birth = {c["count"]: (c["all"], c["chosen"]) for c in summary["counts"]["birth"]}
    assert birth[2] == (0.5, 0.667) and birth[3] == (0.5, 0.667) and birth[4] == (0.25, 0.0)
    survival = {c["count"]: (c["all"], c["chosen"]) for c in summary["counts"]["survival"]}
    assert survival[8] == (0.5, 0.333) and survival[0] == (0.25, 0.333)
    assert summary["counts under both"]["birth"][7]["chosen"] == 1.0
    assert RIVALS.counts(entries, [])["birth"][0]["chosen"] is None


def test_the_three_ways_of_cutting_the_rules():
    assert [RIVALS.least_birth(r) for r in ("B0147/S128", "B15/S7", "B2378/S25678", "B3/S23",
                                            "B4678/S35678", "B8/S", "B/S23")] == [
        "0", "1", "2", "3", "4 or more", "4 or more", "never born",
    ]  # fmt: skip
    assert RIVALS.survives_on_few("B3/S23") and RIVALS.survives_on_few("B2/S1")
    assert not RIVALS.survives_on_few("B2/S0") and not RIVALS.survives_on_few("B2/S345678")
    assert not RIVALS.survives_on_few("B12/S")  # the counts of the birth set do not count
    assert RIVALS.needs_its_own_kind("B2/S0") and RIVALS.needs_its_own_kind("B3568/S0346")
    assert not RIVALS.needs_its_own_kind("B2378/S25678")  # survives on two
    assert not RIVALS.needs_its_own_kind("B1/S5") and not RIVALS.needs_its_own_kind("B4/S5")
    busy = [RIVALS.activity({"called": c, "changed": x})
            for c, x in (("dead", 0.0), ("patches", 0.0), ("patches", 0.009), ("organised", 0.01),
                         ("patches", 0.199), ("growing", 0.2), ("patches", 0.5))]  # fmt: skip
    assert busy == ["dead or full", "still", "still", "quiet", "quiet", "busy", "busy"]


# --- the candidates again ------------------------------------------------------------------------


def _run(side_of_domain, seed=1, species=(), tilt=1.0, live=None):
    """A made-up run on the larger grid whose domains have a side of `side_of_domain(time)`:
    every field has the area a block of each size would then show. `live` is the live cells'
    share of the grid at each reading, a half throughout if not given."""
    times, blocks = list(CONFIRM.TIMES), list(CONFIRM.BLOCKS)
    live = live or [0.5] * len(times)

    def area(block, time):
        x = block / side_of_domain(time)
        return tilt * block * block / (1 + x * x)

    areas = [[area(b, t) for b in blocks] for t in times]
    fields = {
        "live": {"share": list(live), "area": areas},
        "live, rows": {"share": list(live), "area": [[1.0] * len(blocks)] * 6},
    }
    for number, held in enumerate(species, start=1):
        fields[f"species {number}"] = {"share": [held] * len(times), "area": areas}
    return {"family": "alone", "index": 1, "name": "made up", "tie_break": "standoff",
            "rules": ["B3/S23"] * max(1, len(species)), "density": 0.5, "why": "a test",
            "seed": seed, "times": times, "blocks": blocks, "changed": 0.01,
            "fields": fields}  # fmt: skip


def test_a_candidate_over_its_starts():
    """Domains whose side is half the square root of the age: the area grows as the first
    power of time while the blocks are larger than the domains, and four times the wait goes
    with twice the block."""
    runs = [_run(lambda t: 0.5 * t**0.5, seed, tilt=tilt)
            for seed, tilt in ((1, 0.9), (2, 1.0), (3, 1.1))]  # fmt: skip
    told = CONFIRM.describe(runs)
    assert told["called"] == "keeps growing" and told["field"] == "live" and told["starts"] == 3
    assert told["holding"] == 1 and told["shares"] == [0.5] and told["territories"] == []
    assert told["share"] == [0.5] * 6 and told["drift"] == 0
    assert math.isclose(told["area"][-1], 128 * 128 / (1 + 128 * 128 / 512), abs_tol=0.01)
    assert math.isclose(told["length"][-1], math.sqrt(told["area"][-1]), abs_tol=0.01)
    assert told["area_spread"][-1] > 0 and len(told["area"]) == len(CONFIRM.TIMES)
    assert (
        0.9 < told["growth_late"] < 1.0
        and told["growth_late_by_start"] == [told["growth_late"]] * 3
    )
    assert 0 < told["scaling"] < 0.5  # blocks of 32 to 128 against domains of 23 cells
    assert told["clock"]["4"]["median"] == 1 and told["clock"]["4"]["pairs"] > 5
    assert told["clock"]["2"]["median"] < 0.8 and told["clock"]["8"]["median"] > 1.2
    # a world of patches, and one that has stopped
    assert CONFIRM.describe([_run(lambda t: 2.0)])["called"] == "patches"
    stopped = CONFIRM.describe([_run(lambda t: 12.0), _run(lambda t: 12.0, 2)])
    assert stopped["called"] == "organised" and stopped["growth_late"] == 0
    assert stopped["area_spread"][-1] == 0
    # several species: each one's territory is read, and how many hold ground
    shared = CONFIRM.describe([_run(lambda t: 0.5 * t**0.5, species=(0.5, 0.45, 0.01))])
    assert shared["holding"] == 2 and shared["shares"] == [0.5, 0.45, 0.01]
    assert shared["apart"] is not None and told["apart"] is None  # one species: nothing to keep
    assert [t["called"] for t in shared["territories"]] == ["keeps growing"] * 3
    assert shared["area_spread"][-1] is None  # one start has no spread
    # the same growth while one kind of ground takes the grid: by a fifth of the grid, or by
    # halving the smaller side
    grows = lambda t: 0.5 * t**0.5  # noqa: E731
    far = CONFIRM.describe([_run(grows, live=[0.5, 0.45, 0.4, 0.35, 0.3, 0.28])])
    assert far["called"] == "taking over" and far["drift"] == -0.22
    thin = CONFIRM.describe([_run(grows, live=[0.9, 0.92, 0.93, 0.94, 0.95, 0.96])])
    assert thin["called"] == "taking over" and thin["drift"] == 0.06
    steady = CONFIRM.describe([_run(grows, live=[0.5, 0.52, 0.55, 0.57, 0.58, 0.59])])
    assert steady["called"] == "keeps growing"
    # and when it has taken it: nothing has an area at the end, and something had
    over = _run(grows, live=[0.3, 0.2, 0.1, 0.02, 0.004, 0.0])
    for field in over["fields"].values():
        field["area"] = field["area"][:4] + [[None] * 6] * 2
    gone = CONFIRM.describe([over])
    assert gone["called"] == "taken over" and gone["field"] == "live"
    assert gone["peak"] == {"area": round(128 * 128 / (1 + 128 * 128 / 128), 2),
                            "generation": 512}  # fmt: skip
    assert gone["area"][-2:] == [None, None] and gone["share"][-1] == 0
    # or it has all but taken it: little is left to scatter, where there was plenty
    nearly = _run(lambda t: 12.0 if t < 1024 else 2.0, live=[0.5, 0.55, 0.7, 0.9, 0.96, 0.96])
    filled = CONFIRM.describe([nearly])
    assert filled["called"] == "taken over" and filled["peak"]["generation"] == 512
    assert filled["area"][-1] < 16 <= filled["peak"]["area"]
    faded = _run(lambda t: 12.0 if t < 1024 else 2.0)  # the same areas, the share unmoved
    assert CONFIRM.describe([faded])["called"] == "patches"
    # a world of patches whose live cells thin out is not a takeover: it never had 64 cells
    ash = _run(lambda t: 5.0 if t < 1024 else 2.0, live=[0.14, 0.1, 0.07, 0.05, 0.03, 0.02])
    thinned = CONFIRM.describe([ash])
    assert 16 <= thinned["peak"]["area"] < 64 and thinned["called"] == "patches"
    for field in ash["fields"].values():
        field["area"] = field["area"][:1] + [[None] * 6] * 5
    assert CONFIRM.describe([ash])["called"] == "dead"
    never = _run(lambda t: 2.0)
    for field in never["fields"].values():
        field["area"] = [[None] * 6] * 6
    assert CONFIRM.describe([never])["called"] == "dead"
    # the mean over the starts has a gap wherever one start has one
    holed = [_run(lambda t: 2.0), _run(lambda t: 2.0, 2)]
    holed[1]["fields"]["live"]["area"] = [[None] * 6] * 6
    assert CONFIRM.table(holed, "live")[0] == [None] * 6
    assert CONFIRM.describe(holed)["field"] == "live, rows"


def test_which_candidates_get_more_starts():
    """Two more starts only for a known world, a rule alone, a contest or a pair whose first
    start keeps growing."""
    grows = lambda t: 0.5 * t**0.5  # noqa: E731
    assert CONFIRM.again(CONFIRM.describe([_run(grows)]))  # a rule alone that keeps growing
    for family, more in (("known", True), ("contest", True), ("pair", True), ("soup", False),
                         ("left", False), ("copies", False)):  # fmt: skip
        assert CONFIRM.again(CONFIRM.describe([_run(grows) | {"family": family}])) is more
    assert not CONFIRM.again(CONFIRM.describe([_run(lambda t: 12.0)]))  # organised, and stopped
    moving = [0.5, 0.45, 0.4, 0.35, 0.3, 0.28]
    assert not CONFIRM.again(CONFIRM.describe([_run(grows, live=moving)]))  # taking over
    assert not CONFIRM.again(CONFIRM.describe([_run(lambda t: 2.0)]))  # patches
    over = _run(grows)
    for field in over["fields"].values():
        field["area"] = field["area"][:4] + [[None] * 6] * 2
    assert not CONFIRM.again(CONFIRM.describe([over]))  # taken over: nothing left to measure
    assert CONFIRM.STARTS == (12001, 12002, 12003)


def test_the_candidates_that_are_run_again():
    screen = [
        _found(["B3/S23"], 11.0, called="patches", family="known", index=1) | {"name": "Life"},
        _found(["B4678/S35678"], 455.0, family="known", index=6) | {"name": "Anneal"},
        _found(["B4678/S35678"], 300.0, family="near-majority", index=9),  # known: not twice
        _found(["B013/S1"], 400.0, family="rule", index=3),
        _found(["B5/S67", "B138/S123"], 150.0, shares=[0.001, 0.48], family="soup 2"),
        _found(["B015/S1", "B15/S7"], 18.0, shares=[0.275, 0.087], family="soup 2", index=20093),
    ]
    # ten more rules with larger areas than the one whose contest is picked below
    screen += [_found([f"B{i}/S"], 500.0 + i, index=100 + i) for i in range(10)]
    screen += [_found(["B2378/S25678"], 65.0, index=1107)]

    def grew(rule, kind, density, family="contest", **more):
        return {"family": family, "rules": [rule] * 2, "density": density, "index": 1,
                "tie_break": kind, "name": f"{rule} against itself"} | more  # fmt: skip

    contested = {"growing territories": [
        grew("B2378/S25678", "standoff", 0.5), grew("B2378/S25678", "random", 1.0),
        grew("B2/S0", "standoff", 0.5),
        grew("B013/S1", "standoff", 1.0, family="pair", rules=["B013/S1", "B4678/S35678"],
             index=102, name="B013/S1 against B4678/S35678"),
        grew("B2378/S25678", "standoff", 1.0, family="5 copies", rules=["B2378/S25678"] * 5,
             name="5 copies of B2378/S25678"),
        grew("B2378/S25678", "random", 1.0, family="5 copies", rules=["B2378/S25678"] * 5,
             name="5 copies of B2378/S25678"),  # the largest territories only: the first
        grew("B2378/S25678", "random", 1.0, family="3 copies", rules=["B2378/S25678"] * 3),
    ]}  # fmt: skip
    worlds = CONFIRM.candidates(screen, contested)
    assert [w["name"] for w in worlds if w["family"] == "known"] == ["Life", "Anneal"]
    alone = [w["name"] for w in worlds if w["family"] == "alone"]
    # the ten largest areas, then the rule of a picked contest that is not among them; a rule
    # that never grew alone (B2/S0 here) cannot be added
    assert alone == [f"B{i}/S" for i in range(9, -1, -1)] + ["B2378/S25678"]
    assert [w["name"] for w in worlds if w["family"] == "soup"] == ["soup 2 20093"]
    # a soup with one species left is run as the soup it was
    left = [w for w in worlds if w["family"] == "left"]
    assert [(w["name"], w["rules"]) for w in left] == [("soup 2 1", ["B5/S67", "B138/S123"])]
    picked = [(w["name"], w["tie_break"], w["density"]) for w in worlds
              if w["family"] == "contest"]  # fmt: skip
    assert picked == [
        ("B2378/S25678 against itself", "random", 1.0),  # it grew from a full start: full
        ("B2378/S25678 against itself", "standoff", 1.0),
        ("B2/S0 against itself", "random", 0.5),  # only from a half-full one
        ("B2/S0 against itself", "standoff", 0.5),
    ]
    assert [w["name"] for w in worlds if w["family"] == "pair"] == ["B013/S1 against B4678/S35678"]
    five = [w for w in worlds if w["family"] == "copies"]
    assert [(w["name"], w["tie_break"], len(w["rules"])) for w in five] == [
        ("5 copies of B2378/S25678", "standoff", 5)
    ]
    assert len({CONFIRM.key(w) for w in worlds}) == len(worlds)
    assert {w["density"] for w in worlds if w["family"] in ("known", "alone", "soup")} == {0.5}
    # the wider screen adds its best rules, each under both tie-breaks and alone; the worlds
    # picked before it stay as they were, in their order
    four = ("full start, random", "full start, standoff", "half-full start, random",
            "half-full start, standoff")  # fmt: skip
    grows = dict.fromkeys(four, "growing territories")
    entries = [{"rule": f"B{i}/S", "index": 100 + i, "holds": "both", "growing": True,
                "territory": 10.0 * i, "verdicts": grows} for i in range(1, 9)]  # fmt: skip
    # larger territories, but not growing in every one of the four contests: not picked
    entries += [{"rule": "B9/S", "index": 9, "holds": "standoff only", "growing": True,
                 "territory": 999.0, "verdicts": grows | {four[0]: "mixed"}},
                {"rule": "B8/S8", "index": 8, "holds": "both", "growing": True,
                 "territory": 999.0, "verdicts": grows | {four[3]: "standing territories"}},
                {"rule": "B7/S7", "index": 7, "holds": "both", "growing": True,
                 "territory": 999.0, "verdicts": {four[0]: "growing territories"}}]  # fmt: skip
    wider = CONFIRM.candidates(screen, contested, {"territories": entries})
    assert wider[: len(worlds)] == worlds
    added = wider[len(worlds) :]
    rivals = [w for w in added if w["family"] == "rival"]
    assert [w["index"] for w in rivals] == [108, 108, 107, 107, 106, 106, 105, 105, 104, 104,
                                             103, 103]  # fmt: skip
    assert [w["tie_break"] for w in rivals[:2]] == ["random", "standoff"]
    assert {w["density"] for w in rivals} == {1.0} and rivals[0]["rules"] == ["B8/S"] * 2
    alone = [w for w in added if w["family"] == "rival alone"]
    assert [w["rules"] for w in alone] == [[f"B{i}/S"] for i in range(8, 2, -1)]
    assert len(added) == 18 and len({CONFIRM.key(w) for w in wider}) == len(wider)


def test_the_worlds_that_are_followed_for_longer():
    """Anneal as the anchor; the four contests or pairs with the largest territories at the
    end of confirm's first start, if they have 16 cells or more; and the world of copies."""

    def world(family, name, areas, index=1, kind="standoff"):
        return {"family": family, "index": index, "name": name, "rules": ["B3/S23"] * 2,
                "tie_break": kind, "density": 1.0, "called": "keeps growing",
                "territories": [{"area": [1.0, a]} for a in areas]}  # fmt: skip

    found = [
        world("known", "Life", []),
        world("known", "Anneal", [], index=6),
        world("alone", "B2378/S25678", []),
        world("contest", "a", [300.0, 250.0]),
        world("contest", "b", [12.0, 15.9], index=2),
        world("contest", "c", [900.0, None], index=3),
        world("contest", "d", [50.0, 40.0], index=4),
        world("contest", "e", [70.0, 60.0], index=5),
        world("contest", "f", [20.0, 80.0], index=6),
        world("pair", "g", [500.0, 2.0], index=102),
        world("copies", "five", [100.0] * 5),
        world("copies", "thin", [3.0] * 5, index=2),
    ]
    picked = LONG.picks(found)
    assert [w["name"] for w in picked] == ["Anneal", "c", "g", "a", "f", "five"]
    assert set(picked[0]) == {"family", "index", "name", "rules", "tie_break", "density"}
    assert LONG.SIDE * LONG.SIDE * LONG.TIMES[-1] == 2 * 1024 * 1024 * 2048  # twice a confirm run
    assert all(LONG.SIDE % block == 0 for block in LONG.BLOCKS) and LONG.SEED == 12001


# --- the pictures --------------------------------------------------------------------------------


def test_a_grid_is_drawn_a_cell_to_a_pixel():
    """The image is a valid PNG of the grid's size whose pixels are the species' colours."""
    import struct
    import zlib

    grid = np.array([[0, 1, 2], [3, 0, 1]], dtype=np.int8)
    image = PICTURES.frame(grid)
    assert image[:8] == b"\x89PNG\r\n\x1a\n" and image[12:16] == b"IHDR"
    width, height, depth, colour = struct.unpack(">IIBB", image[16:26])
    assert (width, height, depth, colour) == (3, 2, 8, 2)  # eight bits of red, green, blue
    length = struct.unpack(">I", image[33:37])[0]
    assert image[37:41] == b"IDAT"
    rows = zlib.decompress(image[41 : 41 + length])
    assert len(rows) == 2 * (1 + 3 * 3)  # a filter byte and three pixels a row
    first = [tuple(rows[1 + 3 * i : 4 + 3 * i]) for i in range(3)]
    assert first == [PICTURES.COLOURS[0], PICTURES.COLOURS[1], PICTURES.COLOURS[2]]
    assert len(set(PICTURES.COLOURS)) == 4  # empty and three species, all different
    # every chunk carries the checksum of its own bytes
    assert struct.unpack(">I", image[41 + length : 45 + length])[0] == zlib.crc32(
        image[37 : 41 + length]
    )


def test_the_page_of_pictures():
    worlds = [("A made-up pair", ("B3/S23", "B36/S23"), "standoff", 0.5, "A note <here>.")]
    page = PICTURES.page(worlds, side=16, seed=9001, times=(0, 2))
    assert page.count("<img ") == 2 and page.count("data:image/png;base64,") == 2
    assert "generation 0" in page and "generation 2" in page
    assert "A note &lt;here&gt;." in page and "ties by the standoff" in page
    assert page.count('class="key"') == 2  # one swatch for each species, beside its rule
    assert "species 1, B3/S23" in page and "species 2, B36/S23" in page
    alone = PICTURES.page([("One", ("B3/S23",), "standoff", 1.0, "")], 16, 9001, (1,))
    assert "every cell live" in alone and "ties by" not in alone and "species 1" not in alone
    with pytest.raises(ValueError, match="no more than 3 species"):
        PICTURES.page([("Soup", ("B3/S23",) * 4, "random", 0.5, "")], 16, 9001, (1,))
    # every world it is set to draw can be drawn
    assert all(len(rules) <= 3 for _, rules, _, _, _ in PICTURES.WORLDS)


# --- what was found: the files the write-up quotes -----------------------------------------------


def _summary(name: str) -> dict:
    path = LAB / name / "summary.json"
    if not path.exists():
        pytest.skip(f"{name} has not been run")
    return json.loads(path.read_text())


def test_the_search_found_what_the_summary_says():
    summary = _summary("screen")
    assert sum(t["worlds"] for t in summary["families"].values()) == 2407
    known = {k["name"]: k["called"] for k in summary["known"]}
    assert known["Life"] == known["Life against HighLife"] == "patches"
    assert known["Vote"] == "organised" and known["Anneal"] == "growing"
    assert len(summary["growing"]) == 42
    assert summary["families"]["near-majority"]["growing"] == 0
    soups = [t for family, t in summary["families"].items() if family.startswith("soup")]
    assert sum(t["growing"] for t in soups) == 20
    assert sum(t["growing and contested"] for t in soups) == 10
    assert sum(t["contested"] for t in soups) == 552


def test_the_contests_found_what_the_write_up_says():
    summary = _summary("contests")
    tallies = summary["tallies"]
    assert len(summary["rules"]) == 29
    assert sum(t["contests"] for t in tallies.values()) == 312

    def over(prefix: str, verdict: str, kind: str = "") -> int:
        return sum(t[verdict] for group, t in tallies.items()
                   if group.startswith(prefix) and group.endswith(kind))  # fmt: skip

    # a rule against its copy: mostly mixed, never one left, territories mostly by the standoff
    assert over("contest", "contests") == 116 and over("contest", "mixed") == 93
    assert over("contest", "dead") == 10 and over("contest", "one left") == 0
    assert over("contest", "growing territories") == 9
    assert over("contest", "growing territories", "standoff") == 7
    grew = {f["rules"][0] for f in summary["growing territories"] if f["family"] == "contest"}
    assert grew == {"B2378/S25678", "B015/S1", "B237/S025678", "B2/S0"}
    # different rules: one pair of 66 holds territories, and the four against each other never
    assert over("pair", "contests") == 132 and over("pair", "growing territories") == 1
    assert over("pair", "one left") == 45 and over("pair", "mixed") == 77
    assert over("cross", "contests") == 12 == over("cross", "one left")
    # three and five copies, and the rules one count away
    five = [f for f in summary["growing territories"]
            if f["family"] == "5 copies" and f["rules"][0] == "B2378/S25678"]  # fmt: skip
    assert len(five) == 2 and all(f["holding"] == 5 for f in five)
    assert all(abs(f["apart"] + 0.25) < 0.01 for f in five)  # the grid shared out among five
    assert over("variant", "contests") == 36 and over("variant", "growing territories") == 9
    assert over("variant", "one left") == 27


def test_the_wider_screen_found_what_the_write_up_says():
    summary = _summary("rivals")
    assert summary["rules"] == 1196
    assert sum(t["contests"] for t in summary["tallies"].values()) == 4784
    assert all(t["contests"] == 1196 for t in summary["tallies"].values())
    assert summary["holds"] == {"both": 112, "standoff only": 77, "draw only": 13, "neither": 994}
    assert summary["growing"] == 175

    def holding(row: dict) -> int:
        return sum(row.values()) - row["neither"]

    # territories go with how few of its own kind a cell needs to be born
    least = {group: holding(row) for group, row in summary["least birth"].items()}
    assert least == {"0": 28, "1": 41, "2": 91, "3": 41, "4 or more": 1, "never born": 0}
    sizes = {group: sum(row.values()) for group, row in summary["least birth"].items()}
    assert sizes == {"0": 593, "1": 279, "2": 159, "3": 82, "4 or more": 81, "never born": 2}
    # and it does so on the rules that cut was not read from
    other = summary["least birth, the other rules"]
    assert sum(sum(row.values()) for row in other.values()) == 1196 - RIVALS.READ_OFF
    rate = {group: holding(row) / sum(row.values()) for group, row in other.items()}
    assert rate["0"] < 0.06 and rate["1"] < 0.2 and rate["4 or more"] < 0.05
    assert rate["2"] > 0.5 and rate["3"] > 0.45
    # the two cuts together
    own = summary["needs its own kind"]
    assert own["rules"] == 57 and own["die in every contest"] == 10
    assert own["of the rest"] == {"both": 37, "standoff only": 5, "draw only": 2, "neither": 3}
    rest = summary["does not"]
    assert rest["rules"] == 1139 and holding(rest["of the rest"]) == 158
    # they come from rules that are patches alone, not from the ones that grow alone
    assert holding(summary["alone"]["patches"]) == 191
    assert holding(summary["alone"]["growing"]) == 2
    assert holding(summary["activity alone"]["busy"]) == 144
    sturdy = [e for e in summary["territories"]
              if set(e["verdicts"].values()) == {"growing territories"}]  # fmt: skip
    assert len(sturdy) == 78 and all(len(e["verdicts"]) == 4 for e in sturdy)
    assert "B2378/S25678" in {e["rule"] for e in sturdy}


def test_a_contest_run_twice_comes_out_the_same():
    """contests.py and rivals.py both ran the 20 rules of the draw that grow alone, against
    their copies: the same world must end on the same grid, cell for cell."""
    paths = [LAB / name / "records.jsonl" for name in ("contests", "rivals")]
    if not all(path.exists() for path in paths):
        pytest.skip("the contests have not been run")
    ends = []
    for path in paths:
        with path.open() as lines:
            records = map(json.loads, lines)
            ends.append({(r["rules"][0], r["tie_break"], r["density"]): r["final_sha256"]
                         for r in records if r["family"] in ("contest", "copy")})  # fmt: skip
    shared = set(ends[0]) & set(ends[1])
    assert len(shared) == 80 and all(ends[0][k] == ends[1][k] for k in shared)


def test_the_candidates_came_out_as_the_write_up_says():
    summary = _summary("confirm")
    worlds = {(w["family"], w["name"], w["tie_break"]): w for w in summary["worlds"]}
    assert len(worlds) == 56 and sum(w["starts"] for w in summary["worlds"]) == 74
    assert {w["starts"] for w in summary["worlds"]} == {1, 3}
    first = [w for w in summary["worlds"] if not w["family"].startswith("rival")]
    assert len(first) == 38 and sum(w["starts"] for w in first) == 56  # before the wider screen

    def called(family: str, name: str, kind: str = "standoff") -> str:
        return worlds[(family, name, kind)]["called"]

    assert called("known", "Anneal") == called("known", "Day and Night") == "keeps growing"
    assert called("known", "Life against HighLife") == called("known", "HighLife") == "patches"
    assert called("known", "Vote") == "organised"
    # of the 13 rules alone, one keeps growing; the two best rivals take the whole grid alone
    alone = [w["called"] for w in summary["worlds"] if w["family"] == "alone"]
    assert len(alone) == 13 and alone.count("keeps growing") == 1
    assert alone.count("taking over") == 4 and alone.count("taken over") == 4
    assert called("alone", "B012457/S14") == "keeps growing"
    assert called("alone", "B2378/S25678") == called("alone", "B237/S025678") == "taken over"
    # territories under the standoff for all four rules, under the draw for one
    for rule in ("B015/S1", "B237/S025678", "B2/S0"):
        assert called("contest", f"{rule} against itself") == "keeps growing"
        assert called("contest", f"{rule} against itself", "random") == "patches"
    assert called("contest", "B2378/S25678 against itself", "random") == "keeps growing"
    assert called("contest", "B2378/S25678 against itself") == "keeps growing"
    assert called("copies", "5 copies of B2378/S25678") == "keeps growing"
    # a zoom-out by two goes with four times the wait where the grounds are level
    for name in ("Anneal", "Day and Night"):
        assert abs(worlds[("known", name, "standoff")]["clock"]["4"]["median"] - 1) < 0.05
    assert abs(worlds[("alone", "B012457/S14", "standoff")]["clock"]["4"]["median"] - 1) < 0.05
    slow = worlds[("contest", "B015/S1 against itself", "standoff")]
    assert slow["clock"]["4"]["median"] < 1 < slow["clock"]["8"]["median"]
    assert slow["apart"] < -0.99 and abs(slow["shares"][0] - slow["shares"][1]) < 0.05
    # the six sturdiest rules of the wider screen: five keep growing under both tie-breaks
    # with the clock at four, one sets; alone, none of them is anything
    rivals = [w for w in summary["worlds"] if w["family"] == "rival"]
    assert len(rivals) == 12 and {w["density"] for w in rivals} == {1.0}
    grows = [w for w in rivals if w["called"] == "keeps growing"]
    sets = {w["name"] for w in rivals if w["called"] == "organised"}
    assert len(grows) == 10 and sets == {"B2578/S135678 against itself"}
    assert all(w["apart"] < -0.99 and w["holding"] == 2 for w in rivals)
    assert sum(abs(w["clock"]["4"]["median"] - 1) < 0.12 for w in grows) == 9
    still = worlds[("rival", "B245678/S3678 against itself", "random")]
    assert still["live"][-1] > 0.95 and still["changed"] < 0.05 and still["area"][-1] > 3000
    busy = worlds[("rival", "B23467/S4568 against itself", "standoff")]
    assert busy["changed"] > 0.3 and abs(busy["shares"][0] - busy["shares"][1]) < 0.02
    alone = [w["called"] for w in summary["worlds"] if w["family"] == "rival alone"]
    assert len(alone) == 6 and set(alone) <= {"dead", "patches"}


def test_the_longer_look_came_out_as_the_write_up_says():
    summary = _summary("long")
    worlds = {(w["name"], w["tie_break"]): w for w in summary["worlds"]}
    assert len(worlds) == 6 and summary["times"][-1] == 16384 and summary["side"] == 512
    # the filling-in ends and the territories go on: by the end a block of 64 is mostly inside one
    for kind in ("random", "standoff"):
        world = worlds[("B2378/S25678 against itself", kind)]
        assert world["live"][0] < 0.5 and world["live"][-1] > 0.95
        for territory in world["territories"]:
            assert territory["area"][-1] > territory["area"][4] > territory["area"][0]
            assert territory["area"][-1] > 0.7 * 64 * 64
    steady = worlds[("B015/S1 against itself", "standoff")]
    assert max(steady["live"]) - min(steady["live"]) < 0.01
    assert worlds[("Anneal", "standoff")]["live"][-1] > 0.9  # one ground has the grid
