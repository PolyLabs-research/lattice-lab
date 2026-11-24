"""The zoom-out instrument for worlds of several species (examples/scale-up-closure/zoom.py):
its readings against LatticeLife's own, its tables on made-up runs whose rule is known, and its
two known answers on real worlds.

The worlds here are small (sides 32 to 128) and start from seeds 9001 and up, which no
registered study uses.
"""

import importlib.util
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from latticelife.experiments.coarse import block_counts, leading_species

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, load, register, run

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-closure"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"
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
    # two tables' tallies together, and two rules'
    other = Z.Table.empty(3).add(np.array([1, 5]), np.array([2, 0]))
    both = table.plus(other)
    assert both.rows.tolist() == [1, 2, 5, 9]
    assert both.counts.tolist() == [[0, 0, 1], [1, 0, 0], [2, 0, 2], [0, 2, 0]]
    first, second = _made_up_run(9001), _made_up_run(9002)
    apart = Z.CoarseRule.empty(3).learn(first).plus(Z.CoarseRule.empty(3).learn(second))
    together = Z.CoarseRule.empty(3).learn(first).learn(second)
    for kind in Z.KINDS:
        assert np.array_equal(apart.tables[kind].rows, together.tables[kind].rows)
        assert np.array_equal(apart.tables[kind].counts, together.tables[kind].counts)
    # a window of a run: the transitions from one coarse generation up to another
    early = Z.CoarseRule.empty(3).learn(first, 0, 4).tables["nothing"].counts.sum()
    late = Z.CoarseRule.empty(3).learn(first, 4).tables["nothing"].counts.sum()
    assert (early, late) == (4 * 1600, 8 * 1600)


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


# --- the first look's own arithmetic -------------------------------------------------------------


LOOK = _load("scale_up_closure_look", LAB / "look.py")


def test_the_first_look_parts_a_run_into_an_early_and_a_late_period():
    assert LOOK.periods(0, 8, 1024) == {"early": (0, 32), "late": (32, 128)}
    assert LOOK.periods(1, 32, 1024) == {"early": (1, 8), "late": (8, 32)}
    assert LOOK.periods(1, 4, 256) == {"early": (1, 32), "late": (32, 64)}  # a short run halves
    assert Z.horizons(1) == [1] and Z.horizons(8) == [1, 2, 4, 8]
    assert Z.horizons(11) == [1, 2, 4, 8, 11]
    assert set(LOOK.LEARN) & set(LOOK.TRY) == set() and min(LOOK.LEARN) == 7001


def test_the_first_look_says_what_a_finer_view_removes():
    scores = {
        "nothing": {"transitions": 1000, "right": 600, "bits": 900.0},
        "own": {"transitions": 1000, "right": 900, "bits": 400.0},
        "total": {"transitions": 1000, "right": 950, "bits": 300.0},
    }
    assert LOOK.removed(scores, "total") == {"errors": 0.5, "bits": 0.25}
    assert LOOK.removed(scores, "own", "nothing") == {"errors": 0.75, "bits": 0.5556}
    assert LOOK.tidy(scores["own"]) == {
        "transitions": 1000, "wrong_per_thousand": 100.0, "bits_each": 0.4,
    }  # fmt: skip


def test_a_coarse_rule_run_on_by_itself_is_set_beside_the_fine_world():
    """The made-up rule is its own coarse rule, so run on from any generation it never differs
    from the run it came from; a rule that knows only the supercell soon does."""
    rule = Z.CoarseRule.empty(3)
    for seed in (9001, 9002, 9003):
        rule = rule.learn(_made_up_run(seed))
    fresh = _made_up_run(9004)
    kept = LOOK.follow(rule, "total", fresh, 2, 9004)
    assert kept["horizon"] == [1, 2, 4, 8, 10]
    assert kept["differ"] == [0.0] * 5 and kept["likely"] == kept["fine"]
    assert min(kept["drifted"]) > 0.5  # the run itself moves on from where it was
    alone = LOOK.follow(rule, "own", fresh, 2, 9004)
    assert alone["fine"] == kept["fine"] and min(alone["differ"]) > 0.4
    both = LOOK.average([kept, alone])
    assert both["horizon"] == kept["horizon"]
    assert math.isclose(both["differ"][0], alone["differ"][0] / 2, abs_tol=1e-6)
    # the drawn run's movement as a share of the fine world's, start by start
    one = {**kept, "drawn": [2 * v for v in kept["fine"]]}
    two = {**kept, "drawn": [4 * v for v in kept["fine"]]}
    told = LOOK.average([one, two])
    assert told["drawn_over_fine"] == [3.0] * 5
    assert all(math.isclose(v, 2**0.5, abs_tol=1e-4) for v in told["drawn_over_fine_spread"])


# --- the registered study ------------------------------------------------------------------------


S = _load("scale_up_closure_study", LAB / "study.py")


def test_a_tally_stands_for_the_rule_the_instrument_learns():
    """The study keeps only tallies of [was it moving][moving neighbours][does it move]. A rule
    made from a tally gives the chances, and scores another tally, exactly as the instrument's
    own rule learned from the zoomed-out runs."""
    runs = []
    for seed in (9001, 9002, 9003):
        start = Z.mixed_start(128, seed, 2)
        found = Z.histories((LIFE, HIGHLIFE), "standoff", 128, start, 256, (4,))
        runs.append(Z.states(found[4], "moved")[0])
    learned = Z.CoarseRule.empty(2).learn(runs[0], 1).learn(runs[1], 1)
    counts = S.tally(runs[0], 1, 64) + S.tally(runs[1], 1, 64)
    assert counts.shape == (2, 9, 2) and counts.sum() == 2 * 63 * 32 * 32
    assert counts[0, 0, 1] == 0  # stillness is stable
    made = S.rule_of(counts)
    for kind in ("nothing", "own", "total"):
        assert np.array_equal(made.tables[kind].counts, learned.tables[kind].counts[:18])
        ours = S.score(counts, S.tally(runs[2], 1, 64), kind)
        theirs = learned.score(kind, runs[2], 1)
        assert ours["transitions"] == theirs["transitions"] and ours["right"] == theirs["right"]
        assert math.isclose(ours["bits"], theirs["bits"], rel_tol=1e-9)
    chance = S.chances(made, "total")
    assert chance.shape == (2, 9, 2) and np.allclose(chance.sum(axis=-1), 1)
    assert chance[0, 0, 1] < 1e-4 and chance[1, 8, 1] > chance[0, 1, 1]
    # a window of the run, and the places where stillness could have broken
    assert S.tally(runs[0], 1, 16).sum() == 15 * 32 * 32
    assert S.quiet(found[4]) > 0 and Z.unstable(found[4]) == 0


def test_what_the_closure_study_registers():
    claims = S.predictions()
    assert len(claims) == 45 and len({c["label"] for c in claims}) == 45
    assert [sum(c["family"] == f for c in claims) for f in "SNTXEH"] == [10, 10, 6, 4, 5, 10]
    assert all(isinstance(c["claim"], str) and len(c["claim"]) < 240 for c in claims)
    by = {c["label"]: c for c in claims}
    # the bands are the first look's numbers, give or take
    look = S.first_look()
    summary = S.json.loads(S.LOOK.read_text())["worlds"][S.PAIR]["blocks"]
    for block, share in S.REMOVED.items():
        late = summary[str(block)]["moved"]["one_generation"]["late rule, late period"]
        found = 1 - late["total"]["bits_each"] / late["own"]["bits_each"]
        assert abs(found - share) < 0.002, block
        band = by[f"N block {block}: surprise"]
        assert math.isclose(band["low"], share - 0.02) and math.isclose(band["high"], share + 0.02)
        still = np.asarray(look[block])[0, 1]
        assert 0.006 < still[1] / still.sum() < 0.011
        assert by[f"X block {block}"]["rule_tally"] == look[block]
    assert (by["N block 64: surprise"]["low"], by["N block 64: surprise"]["high"]) == (0.02, 0.08)
    assert (by["E block 64"]["low"], by["E block 64"]["high"]) == (0.005, 0.012)
    assert "X block 64" not in by and "T block 32: alone" not in by
    assert "H block 8: dies early" in by and "H block 16: dies early" not in by
    # fresh starts, and a torus and a block the first look did not use
    question = S.question()
    assert question["id"] == "scale-up-closure" and question["runs"] == 16 + 4 + 2 + 32
    assert question["worlds"][S.PAIR]["side"] == 2048 == 2 * LOOK.WORLDS[S.PAIR]["side"]
    assert max(question["worlds"][S.PAIR]["blocks"]) == 64 == 2 * max(LOOK.BLOCKS)
    assert not set(S.LEARN + S.TRY) & set(LOOK.LEARN + LOOK.TRY) and min(S.LEARN) == 8001
    assert set(S.LEARN) & set(S.TRY) == set() and len(question["excluded_seen"]) == 4


def _made_up_rows(monkeypatch, change=None):
    """Records in which every start is the first look itself: the same tallies learned from and
    tried on, at blocks 4 to 32, and run-ons that do what the first look's did. `change` edits
    the rows before they are judged."""
    worlds = {**S.WORLDS, S.PAIR: {**S.WORLDS[S.PAIR], "blocks": (4, 8, 16, 32)}}
    monkeypatch.setattr(S, "WORLDS", worlds)
    blocks = S.json.loads(S.LOOK.read_text())["worlds"][S.PAIR]["blocks"]
    rows = []
    for name, seed in S.start_jobs():
        entry = {}
        for block in S.WORLDS[name]["blocks"]:
            rule = blocks[str(block)]["moved"]["rule_for_movement"]
            entry[str(block)] = {
                "quiet": 1000, "moved_from_stillness": 0,
                "tally": {"early": rule["early"]["tally"], "late": rule["late"]["tally"]},
                "moving": {"128": 0.3, "256": 0.15},
            }  # fmt: skip
        rows.append({"kind": "start", "world": name, "seed": seed, "blocks": entry})
    for seed in S.CONTROL["starts"]:
        rows.append({"kind": "control", "world": S.PAIR, "seed": seed, "block": 4,
                     "quiet": 1000, "moved_from_stillness": 7})  # fmt: skip
    for seed in S.TRY:
        for block in S.RUN_ON:
            rows.append({
                "kind": "ahead", "world": S.PAIR, "seed": seed, "block": block,
                "horizon": [1, 2, 4, 8, 16], "fine": [0.5, 0.4, 0.3, 0.2, 0.02],
                "with_neighbours": [0.5, 0.4, 0.3, 0.21, 0.001 if block <= 8 else 0.02],
                "alone": [0.5, 0.4, 0.3, 0.2, 0.2],
            })  # fmt: skip
    if change:
        change(rows)
    return rows


def test_the_judge_passes_what_the_first_look_found(monkeypatch):
    rows = _made_up_rows(monkeypatch)
    claims = S.predictions()
    assert len(claims) == 41  # no block of 64 in the made-up world
    verdict = S.decide(rows, claims)
    assert verdict["missing"] == [] and set(verdict["outcomes"]) == {c["label"] for c in claims}
    assert verdict["verdict"] == dict.fromkeys("EHNSTX", "holds"), verdict["measured"]
    measured = verdict["measured"]
    assert measured["S control"] == {"moved_from_stillness": 14, "of": 2000}
    assert measured["S pair standoff, block 4"]["of"] == 16000
    assert math.isclose(measured["X block 8"]["measured"], 1.0)  # the same rule on both tori
    assert math.isclose(measured["T block 4: with neighbours"]["measured"], 1.004, abs_tol=0.002)
    assert math.isclose(measured["E block 16"]["measured"], 0.00776, abs_tol=1e-4)
    assert measured["H block 4: keeps up"] == {
        "measured": 1.05, "fine": 0.2, "coarse": 0.21, "generation": 128 + 8 * 4,
    }  # fmt: skip
    assert verdict["rule_for_movement"]["4"]["moves_next_after_still"][0] == 0.0


def test_the_judge_fails_each_family_for_its_own_reason(monkeypatch):
    def broken(rows):  # one block moved where nothing around it had
        rows[0]["blocks"]["8"]["moved_from_stillness"] = 1

    def quiet_control(rows):
        for row in rows:
            if row["kind"] == "control":
                row["moved_from_stillness"] = 0

    def flat(rows):  # the neighbours stop mattering: every row of the trial tallies alike
        for row in rows:
            if row["kind"] == "start" and row["world"] == S.PAIR and row["seed"] in S.TRY:
                late = np.asarray(row["blocks"]["4"]["tally"]["late"])
                each = late.sum(axis=1, keepdims=True) // 9
                row["blocks"]["4"]["tally"]["late"] = np.broadcast_to(each, late.shape).tolist()

    def lingering(rows):  # run on with its neighbours, the rule keeps too much movement
        for row in rows:
            if row["kind"] == "ahead":
                row["with_neighbours"] = [0.5, 0.4, 0.3, 0.3, 0.02]

    cases = (
        (broken, "S", {"S pair standoff, block 8"}),
        (quiet_control, "S", {"S control"}),
        (flat, "N", None),
        (lingering, "H", {"H block 4: keeps up", "H block 8: keeps up", "H block 16: keeps up",
                          "H block 32: keeps up", "H block 4: dies early",
                          "H block 8: dies early"}),
    )  # fmt: skip
    for change, family, labels in cases:
        verdict = S.decide(_made_up_rows(monkeypatch, change), S.predictions())
        failed = {label for label, word in verdict["outcomes"].items() if word == "fails"}
        assert verdict["verdict"][family] == "fails", change.__name__
        if labels is not None:
            assert failed == labels, change.__name__
        else:
            assert "N block 4: surprise" in failed
    # a start short and everything is missing
    rows = _made_up_rows(monkeypatch)
    verdict = S.decide(rows[1:], S.predictions())
    assert verdict["missing"] == ["pair standoff from start 8001"]
    assert set(verdict["outcomes"].values()) == {"missing"}
    assert set(verdict["verdict"].values()) == {"missing"}


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_the_closure_study_registers_runs_and_judges_on_small_grids(monkeypatch, tmp_path):
    worlds = {
        S.PAIR: {"rules": (LIFE, HIGHLIFE), "side": 128, "generations": 256, "blocks": (4, 8, 16)},
        S.SOUP: {**S.WORLDS[S.SOUP], "side": 64, "generations": 128, "blocks": (4, 8)},
    }
    monkeypatch.setattr(S, "WORLDS", worlds)
    monkeypatch.setattr(S, "LEARN", (9001, 9002))
    monkeypatch.setattr(S, "TRY", (9003, 9004))
    monkeypatch.setattr(S, "SOUP_STARTS", (9001,))
    monkeypatch.setattr(S, "CONTROL", {"side": 128, "generations": 256, "block": 4, "clock": 16,
                                       "starts": (9001,)})  # fmt: skip
    monkeypatch.setattr(S, "SPLIT", 64)
    monkeypatch.setattr(S, "FROM", 32)
    monkeypatch.setattr(S, "RUN_ON", (4, 8))
    monkeypatch.setattr(S, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(S, "RECORDS", tmp_path / "records.jsonl")
    _git(tmp_path, "init", "-q")
    study = Study(tmp_path, S.question, S.predictions, S.execute, S.decide, rerun=S.rerun)
    claims = S.predictions()
    assert len(register(study)) == len(claims) + 1 == 31
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert verdict["missing"] == [] and set(verdict["verdict"]) == set("EHNSTX")
    assert set(verdict["outcomes"].values()) <= {"holds", "fails"}
    assert len(verdict["outcomes"]) == len(claims)
    # the known answer holds on any grid: stillness, and its control
    assert verdict["verdict"]["S"] == "holds"
    assert verdict["measured"]["S control"]["moved_from_stillness"] > 0
    assert verdict["rule_for_movement"]["4"]["moves_next_after_still"][0] == 0.0
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    rows = ledger.entries[-2]["body"]["rows"]
    kinds = [r["kind"] for r in rows]
    assert kinds == ["start"] * 5 + ["control"] + ["ahead"] * 4
    assert S.rerun(rows[0]) == rows[0] and S.rerun(rows[5]) == rows[5]
    assert S.rerun(rows[-1]) == rows[-1] and rows[-1]["horizon"] == [1, 2, 4, 8, 16, 28]
    # running again adds nothing: every run is already recorded
    before = (tmp_path / "records.jsonl").read_text()
    study.execute(tmp_path / "records.jsonl", 1)
    assert (tmp_path / "records.jsonl").read_text() == before
    # the census dashboards' reader gives each prediction its outcome
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    table, summary = readers.READERS["scale-up-closure"](bodies, verdict, {})
    assert [r["label"] for r in table] == [b["label"] for b in bodies]
    assert {r["outcome"] for r in table} <= {"held", "failed"} and summary.startswith("E ")


def test_the_closure_ledger_holds_the_registration():
    path = LAB / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[:46] == ["question"] + ["prediction"] * 45
    question = ledger.entries[0]
    if question["body"]["sha256"] == S.question()["sha256"]:  # the first look as registered
        for entry, claim in zip(ledger.entries[1:46], S.predictions(), strict=True):
            assert entry["body"] == {"question": question["hash"], **claim}
    if "verdict" not in kinds:  # between registration and the run, nothing may move
        assert question["body"]["sha256"] == S.question()["sha256"]


def test_verify_can_rerun_the_closure_studys_records():
    assert load(LAB).rerun is not None
