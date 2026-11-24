"""The zoom-out instrument for worlds of several species (examples/scale-up-closure/zoom.py):
its readings against LatticeLife's own, its tables on made-up runs whose rule is known, and its
two known answers on real worlds.

The worlds here are small (sides 32 to 128) and start from seeds 9001 and up, which no
registered study uses.
"""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from latticelife.experiments.coarse import block_counts, leading_species

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-closure"
LIFE, HIGHLIFE = "B3/S23", "B36/S23"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


Z = _load("scale_up_closure_zoom", LAB / "zoom.py")


# --- readings ------------------------------------------------------------------------------------


def test_a_block_is_read_as_latticelife_reads_it():
    start = Z.mixed_start(48, 9001, 3)
    for block in (2, 4, 8):
        ours = Z.read(start, 48, block, 3)
        theirs = block_counts("square", 48, block, start, (1, 2, 3))
        assert np.array_equal(ours.reshape(3, -1), theirs)
        leaders = leading_species(theirs, (1, 2, 3))
        assert np.array_equal(Z.leaders(ours).reshape(-1), leaders)
    # nobody leads an empty block, or one where two species are level
    counts = np.array([[[0, 3, 2]], [[0, 3, 5]]], dtype=np.uint16)
    assert Z.leaders(counts).tolist() == [[0, 0, 2]]


def test_the_ring_is_the_eight_neighbours_in_order_on_a_wrapped_grid():
    grid = np.arange(20).reshape(4, 5)
    around = Z.ring(grid)
    assert around.shape == (8, 4, 5)
    # the supercell in row 1, column 2 holds 7: N, NE, E, SE, S, SW, W, NW
    assert around[:, 1, 2].tolist() == [2, 3, 8, 13, 12, 11, 6, 1]
    # the corner wraps round
    assert around[:, 0, 0].tolist() == [15, 16, 1, 6, 5, 9, 4, 19]
    stack = Z.ring(np.stack([grid, grid + 100]))
    assert stack.shape == (8, 2, 4, 5) and stack[2, 1, 1, 2] == 108


def test_a_view_has_one_code_whichever_way_the_square_is_turned():
    rng = np.random.default_rng(9001)
    for q in (2, 3, 6):
        grid = rng.integers(0, q, size=(12, 12))
        for kind in Z.KINDS:
            base = Z.codes(kind, grid, Z.ring(grid), q)
            for turns in range(4):
                for flip in (False, True):
                    moved = np.rot90(grid, turns)
                    moved = moved[:, ::-1] if flip else moved
                    seen = Z.codes(kind, moved, Z.ring(moved), q)
                    back = seen[:, ::-1] if flip else seen
                    assert np.array_equal(np.rot90(back, -turns), base), (q, kind, turns, flip)
    # with two symbols there are 51 rings up to the square's symmetries, and 9 neighbour counts
    grid = rng.integers(0, 2, size=(200, 200))
    around = Z.ring(grid)
    assert np.unique(Z.codes("full", grid, around, 2)).size == 2 * 51
    assert np.unique(Z.codes("total", grid, around, 2)).size == 2 * 9
    assert np.unique(Z.codes("own", grid, around, 2)).size == 2
    assert np.unique(Z.codes("nothing", grid, around, 2)).size == 1
    # different rings that the symmetries do not join keep different codes
    a = np.zeros((3, 3), dtype=int)
    b = a.copy()
    a[0, 1] = a[0, 0] = 1  # N and NW: neighbours of each other
    b[0, 1] = b[2, 1] = 1  # N and S: opposite
    centre = (slice(1, 2), slice(1, 2))
    assert Z.codes("full", a, Z.ring(a), 2)[centre] != Z.codes("full", b, Z.ring(b), 2)[centre]
    assert Z.codes("total", a, Z.ring(a), 2)[centre] == Z.codes("total", b, Z.ring(b), 2)[centre]


# --- tables, on made-up runs ---------------------------------------------------------------------


def _made_up_run(seed, steps=12, side=40):
    """A run of a made-up rule of three symbols that looks only at the supercell and at how
    many of its neighbours are each symbol: next = (own + twos + 2 * (ones > 2)) mod 3."""
    rng = np.random.default_rng(seed)
    grids = [rng.integers(0, 3, size=(side, side)).astype(np.int8)]
    for _ in range(steps):
        now = grids[-1]
        around = Z.ring(now)
        ones, twos = (around == 1).sum(axis=0), (around == 2).sum(axis=0)
        grids.append(((now + twos + 2 * (ones > 2)) % 3).astype(np.int8))
    return np.stack(grids)


def test_a_table_tallies_what_came_next():
    table = Z.Table.empty(3)
    table = table.add(np.array([5, 5, 5, 9]), np.array([0, 2, 2, 1]))
    table = table.add(np.array([[9, 2]]), np.array([[1, 0]]))
    assert table.rows.tolist() == [2, 5, 9]
    assert table.counts.tolist() == [[1, 0, 0], [1, 0, 2], [0, 2, 0]]
    seen = table.after(np.array([[5, 7], [9, 2]]))
    assert seen.tolist() == [[[1, 0, 2], [0, 0, 0]], [[0, 2, 0], [1, 0, 0]]]
    assert Z.Table.empty(3).after(np.array([1, 2])).tolist() == [[0, 0, 0], [0, 0, 0]]


def test_a_rule_that_looks_at_neighbour_counts_is_learned_back():
    rule = Z.CoarseRule.empty(3)
    for seed in (9001, 9002, 9003):
        rule = rule.learn(_made_up_run(seed))
    fresh = _made_up_run(9004)
    scores = {kind: rule.score(kind, fresh) for kind in Z.KINDS}
    transitions = 12 * 40 * 40
    assert {s["transitions"] for s in scores.values()} == {transitions}
    # the views that hold the neighbour counts call every transition; the others cannot
    assert scores["total"]["right"] == transitions
    assert scores["full"]["right"] > 0.97 * transitions  # a few rings it has not met in place
    assert scores["own"]["right"] < 0.5 * transitions > scores["nothing"]["right"]
    assert scores["total"]["bits"] < 0.02 * transitions < scores["own"]["bits"]
    # and the learned table runs the rule: twelve generations on, cell for cell
    grid = fresh[0]
    for after in fresh[1:]:
        grid = rule.step("total", grid)
        assert np.array_equal(grid, after)


def test_noise_cannot_be_foretold_by_any_view():
    rng = np.random.default_rng(9001)
    rule = Z.CoarseRule.empty(3)
    for _ in range(3):
        rule = rule.learn(rng.choice(3, size=(13, 40, 40), p=[0.5, 0.3, 0.2]).astype(np.int8))
    fresh = rng.choice(3, size=(13, 40, 40), p=[0.5, 0.3, 0.2]).astype(np.int8)
    entropy = -sum(p * math.log2(p) for p in (0.5, 0.3, 0.2))
    for kind in Z.KINDS:
        found = rule.score(kind, fresh)
        assert abs(found["right"] / found["transitions"] - 0.5) < 0.02, kind
        # no view does better than the odds themselves; the finer ones do a little worse
        assert found["bits"] / found["transitions"] > entropy - 0.02, kind
    coarse = rule.score("nothing", fresh)
    assert math.isclose(coarse["bits"] / coarse["transitions"], entropy, abs_tol=0.02)
    assert rule.score("full", fresh)["bits"] > coarse["bits"]


def test_a_rule_can_be_run_by_its_likeliest_symbol_or_by_its_chances():
    rng = np.random.default_rng(9001)
    runs = rng.choice(2, size=(40, 30, 30), p=[0.8, 0.2]).astype(np.int8)
    rule = Z.CoarseRule.empty(2).learn(runs)
    grid = runs[0]
    assert not rule.step("own", grid).any()  # the likeliest symbol is always 0
    drawn = np.mean([rule.step("own", grid, rng).mean() for _ in range(40)])
    assert abs(drawn - 0.2) < 0.02  # a draw follows the chances
    chance = rule.chances("nothing", grid, Z.ring(grid))
    assert chance.shape == (30, 30, 2) and np.allclose(chance.sum(axis=-1), 1)
    assert abs(chance[0, 0, 1] - runs[1:].mean()) < 1e-3
    # a view never seen falls back on the coarser one
    assert np.allclose(Z.CoarseRule.empty(2).chances("full", grid, Z.ring(grid)), 0.5)
    with pytest.raises(ValueError, match="unknown kind"):
        Z.codes("half", grid, Z.ring(grid), 2)


# --- a fine world, zoomed out --------------------------------------------------------------------


def test_a_fine_run_is_read_through_several_blocks_at_once():
    start = Z.mixed_start(64, 9001, 2)
    found = Z.histories((LIFE, HIGHLIFE), "standoff", 64, start, 32, (4, 8, 16))
    assert set(found) == {4, 8, 16}
    assert (found[4].steps, found[8].steps, found[16].steps) == (8, 4, 2)
    assert found[4].counts.shape == (9, 2, 16, 16) and found[16].moved.shape == (3, 4, 4)
    assert np.array_equal(found[8].counts[0], Z.read(start, 64, 8, 2))
    assert not found[8].moved[0].any() and found[8].moved[1].any()
    # the blocks of 16 hold what their four blocks of 8 hold, at the generations they share
    fine, wide = found[8].counts[::2], found[16].counts
    assert np.array_equal(fine.reshape(3, 2, 4, 2, 4, 2).sum(axis=(3, 5)), wide)
    for alphabet in Z.ALPHABETS:
        symbols, q, first = Z.states(found[8], alphabet)
        assert symbols.shape == (5, 8, 8) and symbols.max() < q
        assert first == (1 if "moved" in alphabet else 0)
    with pytest.raises(ValueError, match="does not divide"):
        Z.histories((LIFE,), "standoff", 64, start, 30, (4,))
    with pytest.raises(ValueError, match="unknown alphabet"):
        Z.states(found[8], "colour")


def test_stillness_is_stable_in_a_world_that_is_a_function_of_its_grid():
    """A block whose 3 x 3 neighbourhood did not change over the last coarse generation does
    not change over the next, when the clock is no longer than the block."""
    start = Z.mixed_start(128, 9001, 2)
    found = Z.histories((LIFE, HIGHLIFE), "standoff", 128, start, 512, (4, 8, 16))
    for block, history in found.items():
        moved = history.moved
        quiet = ~(moved[1:-1] | Z.ring(moved[1:-1]).any(axis=0))
        assert quiet.sum() > 100, block  # there are still neighbourhoods to try it on
        assert Z.unstable(history) == 0, block
    # with a clock four times the block, movement arrives from beyond the neighbours
    late = Z.histories((LIFE, HIGHLIFE), "standoff", 128, start, 512, (4,), clocks={4: 16})
    assert Z.unstable(late[4]) > 0


def test_a_world_with_far_neighbours_is_its_own_zoom_out():
    """Dilation b, a start uniform on every block, clock 1: the blocks stay uniform, the
    zoomed-out run is the same rules on the small grid, and the table learned from it is those
    rules, which look only at the supercell and at how many neighbours are each species."""
    rules, block, side = (LIFE, HIGHLIFE, "B2/S"), 4, 96
    rule = Z.CoarseRule.empty(4)
    for seed in (9001, 9002, 9003, 9004):
        start = Z.uniform_blocks(side, block, seed, 3)
        found = Z.histories(
            rules, "standoff", side, start, 12, (block,), {block: 1}, dilation=block
        )
        history = found[block]
        # every block is one species or empty, at every generation
        assert set(np.unique(history.counts)) <= {0, block * block}
        small = Z.histories(rules, "standoff", side // block, Z.mixed_start(side // block, seed, 3),
                            12, (1,))  # fmt: skip
        zoomed, q, _ = Z.states(history, "leader")
        direct, _, _ = Z.states(small[1], "leader")
        assert q == 4 and np.array_equal(zoomed, direct)
        if seed != 9004:
            rule = rule.learn(zoomed)
    # every view of the supercell and its neighbour counts was followed by one thing only
    table = rule.tables["total"]
    assert ((table.counts > 0).sum(axis=1) == 1).all() and table.rows.size > 150
    # on a start it did not learn from, it is right wherever it has met the view before
    met = wrong = 0
    for own, around, after in Z.transitions(zoomed):
        tally = table.after(Z.codes("total", own, around, 4))
        known = tally.sum(axis=-1) > 0
        met += int(known.sum())
        wrong += int((tally.argmax(axis=-1) != after)[known].sum())
    assert wrong == 0 and met > 0.99 * 12 * 24 * 24
    found = rule.score("total", zoomed)
    assert found["transitions"] == 12 * 24 * 24 and found["right"] > 0.99 * found["transitions"]
    assert rule.score("own", zoomed)["right"] < 0.8 * found["transitions"]
    # with the wrong clock the blocks are still uniform, but the small world is not followed
    slow = Z.histories(rules, "standoff", side, start, 12, (block,), {block: 2}, dilation=block)
    twice, _, _ = Z.states(slow[block], "leader")
    assert not np.array_equal(twice[1], direct[1]) and np.array_equal(twice[1], direct[2])
