"""The first look at worlds of territories, zoomed out (examples/scale-up-closure-territories):
what a block is read as, the two clocks, and the measures, on made-up worlds whose answer is
known and on a real one small enough to run here.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-closure-territories"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LOOK = _load("scale_up_closure_territories_look", LAB / "look.py")
PICTURES = _load("scale_up_closure_territories_pictures", LAB / "pictures.py")
ZOOM = LOOK.zoom


# --- what a block is read as ---------------------------------------------------------------------


def test_a_block_is_one_of_five_symbols():
    """Neither leads; a species leads clearly; a species leads a block its rival holds a tenth
    or more of."""
    first = np.array([[0, 5, 16, 10, 9, 1, 0, 8, 91]])
    second = np.array([[0, 5, 0, 1, 1, 9, 3, 16, 9]])
    found = LOOK.symbols(np.stack([first, second]))
    #                           none tie  1   1  1c  2c  2  2c   1
    assert found.tolist() == [[0, 0, 1, 1, 3, 4, 2, 4, 1]]
    assert found.dtype == np.int8
    # a tenth exactly is contested (1 of 10); 1 of 11 is not; 9 of 100 is not
    assert LOOK.symbols(np.array([[[9]], [[1]]])).item() == 3
    assert LOOK.symbols(np.array([[[10]], [[1]]])).item() == 1
    assert LOOK.LEADER[found].tolist() == [[0, 0, 1, 1, 1, 2, 2, 2, 1]]


def test_the_two_clocks():
    assert [LOOK.clock("block", b) for b in LOOK.BLOCKS] == [4, 8, 16, 32]
    assert [LOOK.clock("square", b) for b in LOOK.BLOCKS] == [4, 16, 64, 256]
    # the square clock is four times slower for each doubling of the block, the block clock twice
    for below, block in zip(LOOK.BLOCKS, LOOK.BLOCKS[1:], strict=False):
        assert LOOK.clock("square", block) == 4 * LOOK.clock("square", below)
        assert LOOK.clock("block", block) == 2 * LOOK.clock("block", below)


def test_the_ages_that_match():
    """Four times later for each doubling of the block, as the square clock runs."""
    assert [LOOK.age(b) for b in LOOK.BLOCKS] == [(64, 256), (256, 1024), (1024, 4096),
                                                  (4096, 16384)]  # fmt: skip
    for block in LOOK.BLOCKS:
        first, last = LOOK.age(block)
        # the same number of coarse generations at every rung
        assert (last - first) // LOOK.clock("square", block) == 48


def test_when_a_transition_is_read():
    """One after another, but no more often than every sixteen generations, and always at a
    generation the block was read at."""
    assert LOOK.instants(4, 4, 64, 128) == [64, 80, 96, 112]
    assert LOOK.instants(8, 8, 64, 128) == [64, 80, 96, 112]
    assert LOOK.instants(8, 16, 64, 128) == [64, 80, 96, 112]
    assert LOOK.instants(16, 64, 64, 320) == [64, 128, 192, 256]
    assert LOOK.instants(32, 256, 64, 1024) == [64, 320, 576]
    assert LOOK.instants(32, 32, 70, 200) == [96, 128, 160]  # from the first reading after 70
    assert LOOK.instants(16, 64, 64, 100) == []
    for block in LOOK.BLOCKS:
        for name in LOOK.CLOCKS:
            tick = LOOK.clock(name, block)
            at = LOOK.instants(block, tick, LOOK.FROM, LOOK.GENERATIONS)
            assert at and all(t % block == 0 for t in at)
            assert at[-1] + tick <= LOOK.GENERATIONS


def test_a_runs_transitions_at_a_block_and_clock():
    frames = np.arange(9, dtype=np.int8)[:, None, None] % 5 * np.ones((1, 2, 2), dtype=np.int8)
    own, after = LOOK.pairs(frames, 16, 64, 0, 128, "leader+contested")  # frames every 16
    assert own[:, 0, 0].tolist() == [0, 4] and after[:, 0, 0].tolist() == [4, 3]
    own, after = LOOK.pairs(frames, 16, 16, 16, 64, "leader")
    assert own[:, 0, 0].tolist() == [1, 2, 1] and after[:, 0, 0].tolist() == [2, 1, 2]


# --- the measures, on made-up worlds -------------------------------------------------------------


def _voters(pull: float, steps: int, seed: int, side: int = 48) -> np.ndarray:
    """A made-up zoomed-out world: every block under one of two leaders, and at each step a
    block goes over to its rival with chance `pull` times the share of its eight neighbours
    the rival leads."""
    rng = np.random.default_rng(seed)
    grid = rng.integers(1, 3, (side, side)).astype(np.int8)
    out = [grid]
    for _ in range(steps):
        rival = np.where(grid == 1, 2, 1).astype(np.int8)
        near = (ZOOM.ring(grid) == rival).sum(axis=0)
        grid = np.where(rng.random(grid.shape) < pull * near / 8, rival, grid).astype(np.int8)
        out.append(grid)
    return np.stack(out)


def test_the_tallies_and_scores_are_the_instruments_own():
    world = _voters(0.5, 12, 9001)
    ours = LOOK.tally(ZOOM.CoarseRule.empty(3), world[:-1], world[1:])
    theirs = ZOOM.CoarseRule.empty(3).learn(world)
    for kind in ZOOM.KINDS:
        assert np.array_equal(ours.tables[kind].rows, theirs.tables[kind].rows)
        assert np.array_equal(ours.tables[kind].counts, theirs.tables[kind].counts)
    other = _voters(0.5, 12, 9002)
    for kind in ZOOM.KINDS:
        mine, its = LOOK.score(ours, kind, other[:-1], other[1:]), theirs.score(kind, other)
        assert mine["transitions"] == its["transitions"] == 12 * 48 * 48
        assert mine["right"] == its["right"] and np.isclose(mine["bits"], its["bits"])
    # a rule learned from a share of the transitions: about that share of the tallies
    rng = np.random.default_rng(9001)
    part = LOOK.tally(ZOOM.CoarseRule.empty(3), world[:-1], world[1:], 0.25, rng)
    whole, some = ours.tables["own"].counts.sum(), part.tables["own"].counts.sum()
    assert 0.23 * whole < some < 0.27 * whole
    assert {kind: table.counts.sum() for kind, table in part.tables.items()} == dict.fromkeys(
        ZOOM.KINDS, some
    )
    told = LOOK.tidy({"transitions": 2000, "right": 1900, "bits": 500.0})
    assert told == {"transitions": 2000, "wrong_per_thousand": 50.0, "bits_each": 0.25}
    assert LOOK.add({"a": 1, "b": 2.0}, {"a": 3, "b": 0.5}) == {"a": 4, "b": 2.5}


def test_changing_hands_by_how_many_neighbours_the_rival_leads():
    world = _voters(0.8, 40, 9001)
    found = LOOK.hands(world[:-1], world[1:])
    assert found.shape == (9, 2) and found[:, 0].sum() == 40 * 48 * 48
    assert found[0, 1] == 0  # no rival around: no change, by the made-up rule
    rate = found[1:, 1] / np.maximum(found[1:, 0], 1)
    for near in range(1, 8):  # the chance is 0.8 times an eighth for each rival neighbour
        if found[near, 0] > 2000:
            assert abs(rate[near - 1] - 0.8 * near / 8) < 0.04, near
    # a block with no leader is not counted, and going to no leader is a change
    own = np.array([[[1, 0, 2]]], dtype=np.int8)
    after = np.array([[[0, 1, 2]]], dtype=np.int8)
    assert LOOK.hands(own, after)[:, 0].sum() == 2 and LOOK.hands(own, after)[:, 1].sum() == 1


def test_the_walls_between_leaders():
    halves = np.ones((4, 8), dtype=np.int8)
    halves[:, 4:] = 2
    # across: two walls in each row of eight pairs (the grid wraps); down: none
    assert LOOK.walls(halves) == (2 / 8 + 0) / 2
    assert LOOK.walls(np.ones((4, 4), dtype=np.int8)) == 0
    board = (np.indices((4, 4)).sum(axis=0) % 2 + 1).astype(np.int8)
    assert LOOK.walls(board) == 1
    contested = np.where(halves == 1, 3, 4).astype(np.int8)  # the same leaders, contested
    assert LOOK.walls(contested) == LOOK.walls(halves)


def test_a_rule_from_elsewhere_serves_or_does_not():
    """The excess surprise of a rule tried on transitions it did not learn from: none if they
    come from the same made-up rule, plenty if they do not."""

    def learned(pull, seeds):
        rule = ZOOM.CoarseRule.empty(3)
        for seed in seeds:
            world = _voters(pull, 30, seed)
            rule = LOOK.tally(rule, world[:-1], world[1:])
        return rule

    tried = [(w[:-1], w[1:]) for w in (_voters(0.4, 30, seed) for seed in (9005, 9006))]
    same = LOOK.excess(learned(0.4, (9001, 9002)), learned(0.4, (9003, 9004)), tried)
    assert set(same) == set(LOOK.VIEWS) and abs(same["total"]) < 0.02 and abs(same["full"]) < 0.05
    slower = LOOK.excess(learned(0.2, (9001, 9002)), learned(0.4, (9003, 9004)), tried)
    assert slower["total"] > 0.03 and slower["full"] > 0.03
    faster = LOOK.excess(learned(0.8, (9001, 9002)), learned(0.4, (9003, 9004)), tried)
    assert faster["total"] > 0.1


# --- a real world, small -------------------------------------------------------------------------


@pytest.fixture
def small(monkeypatch, tmp_path):
    monkeypatch.setattr(LOOK, "CACHE", tmp_path)
    monkeypatch.setattr(LOOK, "LEARN", (9001, 9002))
    monkeypatch.setattr(LOOK, "TRY", (9003, 9004))
    monkeypatch.setattr(LOOK, "BLOCKS", (4, 8, 16))
    return 96, 384, (4, 8, 16)


def test_a_fine_run_is_read_through_every_block(small):
    side, generations, blocks = small
    path = Path(LOOK.run_fine(("still", 9001, side, generations)))
    assert path.exists() and LOOK.run_fine(("still", 9001, side, generations)) == str(path)
    kept = LOOK.load("still", 9001, side, generations)
    for block in blocks:
        frames = kept[block]
        assert frames.shape == (generations // block + 1, side // block, side // block)
        assert frames.dtype == np.int8 and set(np.unique(frames)) <= {0, 1, 2, 3, 4}
    # blocks of 8 read what four blocks of 4 hold between them: a block all of whose quarters
    # one species leads clearly is led by it, clearly
    quarters = kept[4][-1].reshape(side // 8, 2, side // 8, 2).transpose(0, 2, 1, 3)
    quarters = quarters.reshape(side // 8, side // 8, 4)
    for species in (1, 2):
        whole = (quarters == species).all(axis=-1)
        assert whole.any() and (kept[8][-1][whole] == species).all()
    assert kept["shares"].shape == (generations // 64, 2)
    assert 0.5 < kept["shares"][-1].sum() <= 1 and kept["shares"][-1].min() > 0.05
    # the start is a full grid, half each species: all but every block is contested or tied
    assert np.isin(kept[4][0], (0, 3, 4)).mean() > 0.95


def test_one_world_from_its_runs(small):
    side, generations, blocks = small
    for seed in (9001, 9002, 9003, 9004):
        LOOK.run_fine(("still", seed, side, generations))
    name, found = LOOK.analyse(("still", side, generations, blocks))
    assert name == "still" and found["blocks"] == [4, 8, 16] and found["split"] == 96
    assert json.loads(json.dumps(found)) == found
    assert len(found["shares"]["live"]) == generations // 64
    for alphabet in LOOK.ALPHABETS:
        rows = found[alphabet]
        assert set(rows) == {f"{name} {block}" for name in LOOK.CLOCKS for block in blocks}
        # the two clocks are one clock at blocks of 4
        assert rows["block 4"]["ahead"] == rows["square 4"]["ahead"]
        assert [rows[f"square {b}"]["clock"] for b in blocks] == [4, 16, 64]
        assert [rows[f"block {b}"]["clock"] for b in blocks] == [4, 8, 16]
        for where, row in rows.items():
            ahead = row["ahead"]
            assert set(ahead) == set(ZOOM.KINDS)
            assert len({view["transitions"] for view in ahead.values()}) == 1
            # knowing the block beats knowing nothing
            assert ahead["own"]["bits_each"] < ahead["nothing"]["bits_each"], where
            assert 0 < row["changed_per_thousand"] < 500
            assert ("rule from the rung below" in row) == (not where.endswith(" 4"))
            walls = row["walls"]
            assert walls["from generation"] == 96 and len(walls["fine"]) == len(walls["run on"])
            assert walls["generations on"][-1] <= generations - 96
            # the closure error, read where the walls are read
            apart = row["apart"]
            assert apart["generations on"] == walls["generations on"]
            for which in ("run on", "the start, frozen", "two runs of the rule"):
                assert len(apart[which]) == len(walls["fine"])
                assert all(0 <= share <= 1 for share in apart[which])
        # two runs of one rule from one start part company at once, by their draws alone
        assert rows["block 4"]["apart"]["two runs of the rule"][0] > 0
        # and the world has moved on from where it was by the end
        assert rows["block 4"]["apart"]["the start, frozen"][-1] > 0
        assert set(rows["square 8"]["rule from the rung below"]) == set(LOOK.VIEWS)
        assert set(rows["square 8"]["rule from the rung below, as much data"]) == set(LOOK.VIEWS)
        # at matched ages: blocks of 4 over generations 64 to 256, blocks of 8 over 256 to
        # 1,024, which this short run does not reach
        matched = rows["square 4"]["at matched ages"]
        assert matched["generations"] == [64, 256] and "rule from the rung below" not in matched
        assert matched["transitions"] == 2 * (side // 4) ** 2 * 12  # every 16 generations
        assert (
            "at matched ages" not in rows["square 8"] and "at matched ages" not in rows["block 4"]
        )
        assert ("hands" in matched) == (alphabet == "leader")
    hands = found["leader"]["block 4"]["hands"]
    assert len(hands["blocks"]) == 9 and hands["changed"][0] <= hands["blocks"][0]
    assert "hands" not in found["leader+contested"]["block 4"]
    # a block all of whose neighbours share its leader keeps it nearly always
    assert hands["changed"][0] < 0.01 * hands["blocks"][0]


def test_a_worlds_rule_tried_in_the_other_world(small, monkeypatch):
    side, generations, blocks = small
    for name in LOOK.WORLDS:
        for seed in (9001, 9002, 9003, 9004):
            LOOK.run_fine((name, seed, side, generations))
    found = LOOK.between((side, generations, blocks))
    assert json.loads(json.dumps(found)) == found and set(found) == set(LOOK.ALPHABETS)
    one, other = (
        "the still world's rule in the busy world",
        "the busy world's rule in the still world",
    )
    for rows in found.values():
        assert set(rows) == {f"{name} {block}" for name in LOOK.CLOCKS for block in blocks}
        assert rows["block 4"] == rows["square 4"]
        for row in rows.values():
            assert set(row) == {one, other}
            assert all(set(tried) == set(LOOK.VIEWS) for tried in row.values())
    # a world's rule tried in the same world under another name serves exactly as its own
    still = LOOK.WORLDS["still"]
    monkeypatch.setattr(LOOK, "WORLDS", {"one": still, "same": still})
    for name in LOOK.WORLDS:
        for seed in (9001, 9002, 9003, 9004):
            LOOK.run_fine((name, seed, side, generations))
    for rows in LOOK.between((side, generations, blocks)).values():
        for row in rows.values():
            assert all(excess == 0 for tried in row.values() for excess in tried.values())


def test_the_pictures_of_a_world_and_of_its_coarse_rule(small):
    side, generations, _ = small
    for seed in (9001, 9002, 9003, 9004):
        LOOK.run_fine(("still", seed, side, generations))
    found = PICTURES.ahead("still", 9003, 8, side, generations)
    # from generation 96, eighteen coarse generations of sixteen fine ones
    assert (found["from"], found["to"], found["coarse generations"]) == (96, 384, 18)
    kept = LOOK.load("still", 9003, side, generations)[8]
    assert np.array_equal(found["start"], LOOK.LEADER[kept[96 // 8]])
    assert np.array_equal(found["fine"], LOOK.LEADER[kept[384 // 8]])
    assert found["run on"].shape == (12, 12) and set(np.unique(found["run on"])) <= {0, 1, 2}
    assert found["walls"] == {
        which: LOOK.walls(found[which]) for which in ("start", "fine", "run on")
    }
    assert found["apart"]["start"] == (found["start"] != found["fine"]).mean()
    assert found["apart"]["run on"] == (found["run on"] != found["fine"]).mean()
    # the same start and the same draws give the same world again
    assert np.array_equal(
        PICTURES.ahead("still", 9003, 8, side, generations)["run on"], found["run on"]
    )
    page = PICTURES.page([("still", 8, found)], seed=9003)
    assert page.count("<img ") == 3 and page.count("<h2>") == 1 and page.count("<h3>") == 1
    assert "B245678/S3678 against a copy of itself" in page
    assert "one coarse generation is 16 fine ones, and the coarse rule runs for 18" in page
    assert "the coarse rule&#x27;s own world at generation 384" in page


def test_the_look_found_what_the_summary_says():
    """What the plan says the first look found, held to the summary it was read from. Every
    bound is loose enough to state a finding and tight enough to notice if it goes."""
    path = LAB / "look" / "summary.json"
    if not path.exists():
        pytest.skip("the look has not been run")
    summary = json.loads(path.read_text())
    assert set(summary) == {*LOOK.WORLDS, "between the worlds"}
    for name in LOOK.WORLDS:
        world = summary[name]
        assert world["side"] == 1024 and world["generations"] == 4096
        assert world["learn"] == [15001, 15002, 15003, 15004]
        assert world["try"] == [15005, 15006, 15007, 15008]
        for alphabet in LOOK.ALPHABETS:
            assert len(world[alphabet]) == 8
        rows = world["leader"]

        def rate(where, near, rows=rows):
            hands = rows[where]["hands"]
            return hands["changed"][near] / hands["blocks"][near]

        # the neighbours: over a third of the surprise at blocks of 4 and 8, few of the errors
        for where in ("block 4", "block 8", "square 8"):
            ahead = rows[where]["ahead"]
            assert ahead["total"]["bits_each"] < 0.67 * ahead["own"]["bits_each"], (name, where)
            assert ahead["total"]["wrong_per_thousand"] > 0.97 * ahead["own"]["wrong_per_thousand"]
        # a block changes hands by being surrounded
        assert rate("block 4", 0) < 0.0001 and rate("block 4", 2) < 0.003
        assert 0.14 < rate("block 4", 4) < 0.19 and 0.35 < rate("block 4", 5) < 0.39
        # one rule at every time, the better the smaller the block
        for clock in LOOK.CLOCKS:
            late = [rows[f"{clock} {b}"]["early rule late"]["total"] for b in (4, 8, 16)]
            assert late[0] < 0.005 and late[1] < 0.015 and late[2] < 0.035, (name, clock, late)
        # one rule at every rung: no, but nearer on the square clock, and nearer at each rung
        gap = {clock: [rows[f"{clock} {b}"]["rule from the rung below, as much data"]["total"]
                       for b in (8, 16, 32)] for clock in LOOK.CLOCKS}  # fmt: skip
        assert all(
            square < block for square, block in zip(gap["square"], gap["block"], strict=True)
        )
        assert gap["square"][0] > gap["square"][1] > gap["square"][2] > 0.02
        assert min(gap["block"]) > 0.06
        matched = [rows[f"square {b}"]["at matched ages"]["rule from the rung below, as much data"]
                   ["total"] for b in (8, 16)]  # fmt: skip
        assert 0.02 < matched[1] < 0.5 * matched[0]
        for near in (4, 5):
            block = [rate(f"block {b}", near) for b in LOOK.BLOCKS]
            square = [rate(f"square {b}", near) for b in LOOK.BLOCKS]
            # on the block clock a block twice the size changes hands about half as often
            assert all(1.75 < low / high < 2.6 for low, high in zip(block, block[1:], strict=False))
            # on the square clock the chances fall by less, and by less at the last rung
            falls = [low / high for low, high in zip(square, square[1:], strict=False)]
            assert all(1.15 < fall < 1.7 for fall in falls) and falls[2] < falls[0]
        # run on by itself on the square clock, to the last generation
        for block in LOOK.BLOCKS:
            walls, apart = rows[f"square {block}"]["walls"], rows[f"square {block}"]["apart"]
            kept = walls["run on"][-1] / walls["fine"][-1]
            # the rule adds its dice at once: nearer the world had nothing moved, at first
            assert apart["run on"][0] > apart["the start, frozen"][0]
            assert 0.19 < apart["the start, frozen"][-1] < 0.22  # a fifth of the blocks move on
            if block == 4:
                assert kept < 0.9  # it loses walls too fast
            if block in (16, 32):
                assert 0.94 < kept < 1.03
            if block in (4, 8, 16):  # and it knows where the territories will be
                assert apart["run on"][-1] < 0.6 * apart["the start, frozen"][-1], (name, block)
            if block in (8, 16):  # as near the world as another run of itself
                assert apart["run on"][-1] < 1.25 * apart["two runs of the rule"][-1]
            # the block clock is no better at any block
            slower = rows[f"block {block}"]["apart"]["run on"][-1]
            assert block == 4 or slower > apart["run on"][-1]
    # one rule for both worlds, from blocks of 8
    between = summary["between the worlds"]
    for row in between["leader"]["block 4"].values():
        assert 0.01 < row["total"] < 0.02
    for where in ("block 8", "block 16", "square 8", "square 16"):
        for told, row in between["leader"][where].items():
            assert 0 < row["total"] < 0.005, (where, told)
            # a symbol that looks inside the block tells the worlds apart more
            assert between["leader+contested"][where][told]["total"] > row["total"]
    for where in ("block 32", "square 32"):
        assert all(abs(row["total"]) < 0.01 for row in between["leader"][where].values())
