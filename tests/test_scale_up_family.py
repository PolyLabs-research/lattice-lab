"""The look at the worlds of step 4j beside the still world at every block and tick
(examples/scale-up-family/look.py): the readings of the still world, the measures on made-up
tallies whose answer is known, one made-up world from end to end, and what the look found.
"""

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-family"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LOOK = _load("scale_up_family_look", LAB / "look.py")
STUDY = LOOK.study
PLAIN, HOW = LOOK.PLAIN, LOOK.HOW
SEES = LOOK.SEES


def test_the_readings_of_the_still_world():
    # a block is read at every tick its kept leaders allow, up to four matched ticks
    assert LOOK.readings(2, 1) == [1, 2, 3, 4]
    assert LOOK.readings(4, 4) == [4, 8, 12, 16]
    assert LOOK.readings(8, 8) == [8, 16, 24, 32, 40, 48, 56, 64]
    assert len(LOOK.readings(16, 16)) == 16 and LOOK.readings(32, 32)[-1] == 1024
    assert LOOK.pace(8, 16) == 1.0 and LOOK.pace(4, 8) == 2.0 and LOOK.pace(16, 16) == 0.25
    assert LOOK.pace(2, 1) == 1.0 and LOOK.LOOKS == (8, 16)
    kin = LOOK.family()
    assert len(kin) == 64 and {block for block, _ in kin} == set(LOOK.BLOCKS) == {2, 4, 8, 16, 32}
    for (block, tick), found in kin.items():
        assert tick in LOOK.readings(block, 1 if block == 2 else block)
        assert found["tally"].shape == (8, 3, 9, 9, 3) and 0 < found["undone"] < found["changes"]
        # eight runs on side 2,048 (four for blocks of 2), read every tick while a transition
        # ends inside the block's matched age and seven ticks of its past can be seen
        first = max(4 * block * block, 7 * tick)
        first += (-first) % (1 if block == 2 else block)
        instants = len(range(first, 16 * block * block - tick + 1, tick))
        runs = 4 if block == 2 else 8
        assert found["tally"].sum() == runs * instants * (2048 // block) ** 2, (block, tick)
    # at blocks of 8 and 16 and their matched ticks they are the look's rules of step 4h,
    # which step 4i wrote down: the same runs over the same ages
    reference = STUDY.memory.reference()
    for block in (8, 16):
        mine = kin[block, block * block // 4]["tally"]
        assert np.array_equal(mine, LOOK.AGE.of(reference["still", block])), block
    # the smaller the block, the more often a block changes hands, and an old lead with it
    seen = {key: LOOK.things(found["tally"], found["changes"], found["undone"])
            for key, found in kin.items()}  # fmt: skip
    hands, _, old = LOOK.THINGS
    rungs = [(b, b * b // 4) for b in (2, 4, 8, 16, 32)]
    assert [round(seen[key][hands], 3) for key in rungs] == [0.085, 0.028, 0.015, 0.011, 0.009]
    assert [round(seen[key][old], 4) for key in rungs] == [0.1285, 0.0189, 0.0052, 0.0019, 0.0007]


def _brute(frames: np.ndarray, every: int, tick: int, first: int, last: int) -> np.ndarray:
    """A tally counted block by block, by how long (up to 8 ticks)."""
    side = frames.shape[1]
    counts = np.zeros((8, 3, 9, 9, 3), dtype=np.int64)
    at = lambda g: frames[g // every]  # noqa: E731
    for g in range(first, last - tick + 1, tick):
        now, after = at(g), at(g + tick)
        for i in range(side):
            for j in range(side):
                around = [now[(i + a) % side, (j + b) % side]
                          for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]  # fmt: skip
                ticks = 1
                while (ticks < 8 and g - ticks * tick >= 0
                       and at(g - ticks * tick)[i, j] == now[i, j]):  # fmt: skip
                    ticks += 1
                counts[ticks - 1, now[i, j], around.count(1), around.count(2), after[i, j]] += 1
    return counts


def test_a_tally_at_any_tick_and_what_is_undone():
    rng = np.random.default_rng(11)
    frames = [rng.integers(0, 3, size=(5, 5))]
    for _ in range(200):
        change = rng.random((5, 5)) < 0.1
        frames.append(np.where(change, rng.integers(0, 3, size=(5, 5)), frames[-1]))
    frames = np.stack(frames).astype(np.int8)  # leaders every 2 generations, to generation 400
    for tick, first, last in ((6, 42, 400), (8, 56, 256), (2, 14, 100)):
        counts = LOOK.tally(frames, 2, tick, first, last)
        assert counts.shape == (8, 3, 9, 9, 3)
        assert counts.sum() == 25 * len(range(first, last - tick + 1, tick))
        assert np.array_equal(counts, _brute(frames, 2, tick, first, last)), tick
    # a block that goes over and comes back at once, and one that goes over and stays
    frames = np.ones((9, 1, 2), dtype=np.int8)
    frames[2, 0, 0] = 2  # the first block is the rival's at the third reading only
    frames[4:, 0, 1] = 2  # the second from the fifth reading on
    changed, back = LOOK.undone(frames, 1, 1, 0, 8)
    assert (changed, back) == (3, 1)  # over, back and over: the first of them is undone
    assert LOOK.tick_at(22, 0.5) == 12 and LOOK.tick_at(22, 1.0) == 22 and LOOK.tick_at(16, 2) == 32
    assert LOOK.tick_at(22, 1 / 3) == 8 and LOOK.tick_at(4, 0.25) == 2


def _tally(table: dict) -> np.ndarray:
    """A made-up tally by how long: `table` gives, by (ticks, rival neighbours), how many
    blocks species 1 led and how many of them had another leader one tick on."""
    counts = np.zeros((8, 3, 9, 9, 3), dtype=np.int64)
    for (ticks, near), (blocks, changed) in table.items():
        counts[ticks - 1, 1, 8 - near, near] = [0, blocks - changed, changed]
    return counts


def _bits(chance: float) -> float:
    return -(chance * math.log2(chance) + (1 - chance) * math.log2(1 - chance))


def test_rules_scored_one_tick_ahead():
    young, old = (1, 4), (8, 4)
    tally = _tally({young: (100000, 50000), old: (100000, 10000)})
    plain, how = SEES[PLAIN], SEES[HOW]
    # a rule on its own tally: the plain rule sees three in ten, the remembering rule both
    assert LOOK.bits(plain, LOOK.rule(plain, tally), tally) == pytest.approx(_bits(0.3), abs=2e-4)
    assert LOOK.bits(how, LOOK.rule(how, tally), tally) == pytest.approx(
        (_bits(0.5) + _bits(0.1)) / 2, abs=2e-4)  # fmt: skip
    # with a chance e a block takes a neighbour's leader: four of its eight are the rival's
    chances = LOOK.rule(plain, tally)
    noisy = LOOK.mixed(chances, 0.2)
    assert noisy[0, 1, 4, 4, 2] == pytest.approx(0.8 * 0.3 + 0.2 * 0.5, abs=1e-4)
    assert np.allclose(noisy.sum(axis=-1)[0, 1, 4, 4], 1) and np.allclose(
        LOOK.mixed(chances, 0), chances
    )
    # beside the world's own rule: itself is no further, a rule that is wrong is
    same = LOOK.beside(plain, chances, [tally, tally], tally)
    assert same == {"more surprise": 0.0, "beside its own with endless data": 0.0}
    other = LOOK.rule(plain, _tally({young: (100000, 20000), old: (100000, 20000)}))
    cross = -(0.3 * math.log2(0.2) + 0.7 * math.log2(0.8))
    assert LOOK.beside(plain, other, [tally, tally], tally)["more surprise"] == pytest.approx(
        cross / _bits(0.3) - 1, abs=1e-3)  # fmt: skip
    # the nearest of a family of rules is the one the tally came from
    rules = {(8, 16): {PLAIN: chances}, (4, 8): {PLAIN: other}, (2, 1): {PLAIN: other}}
    assert LOOK.nearest(rules, tally) == (8, 16)
    assert LOOK.nearest(rules, tally, blocks=(2, 4)) in ((2, 1), (4, 8))
    assert LOOK.nearest(rules, _tally({young: (1000, 200), old: (1000, 200)})) != (8, 16)


def test_what_leaders_alone_say():
    # 200,000 blocks with three rival neighbours, a tenth of them changing hands; of the
    # old leads (eight ticks and more) one in fifty
    tally = _tally({(1, 3): (100000, 18000), (8, 3): (100000, 2000)})
    found = LOOK.things(tally, changes=1000, back=250)
    hands, undone, old = LOOK.THINGS
    assert found[hands] == pytest.approx(0.1) and found[undone] == 0.25 and found[old] == 0.02
    assert LOOK.apart(found, found) == 0.0
    twice = {hands: 0.2, undone: 0.25, old: 0.02}
    assert LOOK.apart(found, twice) == pytest.approx(math.log(2) / math.sqrt(3))
    assert LOOK.apart(found, {**twice, old: None}) is None
    few = LOOK.things(_tally({(1, 3): (1000, 100), (8, 3): (10, 1)}), 10, 5)
    assert few[old] is None  # too few old leads to tell a chance


@pytest.fixture
def made_up(monkeypatch):
    """A made-up world of 12 by 12 blocks whose walls' tick is 4 generations: its leaders
    every two generations to generation 256, from four starts; and a family of two rules."""
    monkeypatch.setattr(LOOK, "PAIRS", 1)
    rng = np.random.default_rng(3)
    runs = {}
    for seed in (1, 2, 3, 4):
        frames = [np.where(np.add.outer(np.arange(12), np.arange(12)) % 12 < 6, 1, 2)]
        for _ in range(128):
            now = frames[-1]
            # a block takes a neighbour's leader now and then: walls waver and move
            take = rng.random(now.shape) < 0.15
            frames.append(
                np.where(take, np.roll(now, rng.integers(-1, 2), axis=rng.integers(2)), now)
            )
        runs[seed] = np.stack(frames).astype(np.int8)
    plan = {"learn": [1, 2], "try": [3, 4]}
    at = LOOK.read_at(runs, plan, 4, (64, 256))
    own = sum(at["halves"])
    calm = _tally({(ticks, near): (1000, 10 * near) for ticks in range(1, 9) for near in range(9)})
    calm = calm + np.transpose(calm, (0, 1, 3, 2, 4))[:, [0, 2, 1]][..., [0, 2, 1]]
    kin = {(8, 16): calm, (4, 8): own, (4, 4): own}
    rules = {key: {reading: LOOK.rule(sees, t) for reading, sees in SEES.items()}
             for key, t in kin.items()}  # fmt: skip
    seen = {key: LOOK.things(t, 100.0, 25.0) for key, t in kin.items()}
    return runs, plan, rules, seen


def test_one_made_up_world_from_end_to_end(made_up):
    runs, plan, rules, seen = made_up
    found = LOOK.read(plan, 4, runs, rules, seen)
    assert json.loads(json.dumps(found)) == found and found["walls' tick"] == 4
    # the family holds the world's own table as the reading (4, 8): that is its nearest
    near = found["the nearest reading"]
    assert (near["block"], near["tick"], near["pace"]) == (4, 8, 2.0)
    assert near[PLAIN]["more surprise"] < 0.02 < found["the look's reading"][PLAIN]["more surprise"]
    assert near[PLAIN]["with a noise"]["e"] <= 0.01
    assert found["the look's reading"]["block"] == 8
    # read again at half and at twice its tick, and at its own tick: its walls' tick over
    # the nearest reading's pace, where the rung of that block is tried
    assert found["at half its walls' tick"]["read at"] == 2
    assert found["at twice its walls' tick"]["read at"] == 8
    own = found["the rung at its own tick"]
    assert (own["read at"], own["block"], own["tick"]) == (2, 4, 4)
    # five rules run on, as it is and with how long in view
    ran = found["run on"]
    assert set(ran) == {f"{name}, {reading}" for reading in (PLAIN, HOW) for name in (
        "the look's reading", "the nearest reading", "its own rule",
        "the rung, at its own tick", "its own rule, at its own tick")}  # fmt: skip
    for told in ran.values():
        assert 0 < told["amiss over changed"] < 3 and 0 < told["walls kept"] < 3
    # without the run-ons nothing else changes
    fast = LOOK.read(plan, 4, runs, rules, seen, run_ons=False)
    assert "run on" not in fast and fast == {k: v for k, v in found.items() if k != "run on"}
    # a rule that leaves every block as it is ends amiss in exactly the blocks that changed
    stay = np.zeros((1, 3, 9, 9, 3))
    for leader in range(3):
        stay[0, leader, :, :, leader] = 1.0
    still = LOOK.run_on(SEES[PLAIN], runs[3], stay, 4, 64, 256, (3, 0))
    assert still["amiss"] == still["changed"] > 0 and still["walls"] == pytest.approx(
        STUDY.ladder.walls(runs[3][32]))  # fmt: skip


# --- what the look found -------------------------------------------------------------------------


def test_what_the_look_found():
    """look/summary.json says what the plan quotes from it."""
    found = json.loads((LAB / "look" / "summary.json").read_text())
    worlds = found["worlds"]
    chosen = STUDY.worlds()
    assert set(worlds) == set(chosen) and len(worlds) == 30
    served, near, just, missed = STUDY.SERVED, STUDY.NEAR, STUDY.JUST, STUDY.FAR
    groups = (served, near, just, missed)
    more = "more surprise"

    def reading(world, where):
        return (worlds[world][where]["block"], worlds[world][where]["tick"])

    def spans(where, sees, noise=False, places=3):
        out = []
        for group in groups:
            told = [w[where][sees] for w in worlds.values() if w["group"] == group]
            values = [(t["with a noise"] if noise else t)[more] for t in told]
            out.append((round(min(values), places), round(max(values), places)))
        return out

    # 1. the nearest reading of the still world, by what step 4f found of a world
    placed = {group: sorted(reading(w, "the nearest reading") for w in worlds
                            if worlds[w]["group"] == group) for group in groups}  # fmt: skip
    assert reading(STUDY.STILL, "the nearest reading") == (8, 16)
    assert placed[served] == [(8, 16)] * 7 + [(8, 24)] * 3
    assert placed[near] == [(8, 8), (8, 8), (8, 24), (8, 32)]
    assert placed[just] == [(4, 8)] * 5
    assert placed[missed] == [(2, 4), (2, 4)] + [(4, 8)] * 7 + [(4, 12)]
    assert spans("the look's reading", PLAIN) == [
        (0.0, 0.015), (0.027, 0.037), (0.067, 0.088), (0.171, 0.62)]  # fmt: skip
    assert spans("the nearest reading", PLAIN) == [
        (0.0, 0.009), (0.014, 0.027), (0.02, 0.041), (0.069, 0.259)]  # fmt: skip
    assert spans("the nearest reading", HOW) == [
        (-0.015, 0.007), (0.01, 0.05), (0.018, 0.044), (0.079, 0.577)]  # fmt: skip
    assert spans("the look's reading", HOW)[2] == (0.04, 0.068)
    within = found["worlds within a bar, by group as [within, of]"]

    def count(name, sees, bar):
        return [within[f"{name}, {sees}"][f"within {bar}"][group][0] for group in groups]

    look, nearest = (
        "the look's reading, at its walls' tick",
        "the nearest reading, at its walls' tick",
    )
    assert count(look, PLAIN, "2.5%") == [10, 0, 0, 0] and count(look, PLAIN, "4.0%") == [
        10,
        4,
        0,
        0,
    ]
    assert count(look, HOW, "2.5%") == [10, 4, 0, 0]
    assert count(nearest, PLAIN, "2.5%") == [10, 3, 1, 0]
    assert count(nearest, PLAIN, "4.0%") == [10, 4, 4, 0]
    assert count(nearest, HOW, "2.5%") == [10, 2, 2, 0] and count(nearest, HOW, "4.0%") == [
        10,
        3,
        4,
        0,
    ]
    # 2. the likeness moves with the tick: [block kept, and the tick the right way, of]
    moved = found["does the nearest reading move with the tick, by group as [block kept, and "
                  "the tick the right way, of]"]  # fmt: skip
    half, twice = moved["at half its walls' tick"], moved["at twice its walls' tick"]
    assert [half[g] for g in ("the still world", *groups)] == [
        [1, 1, 1], [10, 9, 10], [4, 2, 4], [4, 4, 5], [8, 2, 10]]  # fmt: skip
    assert [twice[g] for g in ("the still world", *groups)] == [
        [1, 1, 1], [10, 10, 10], [2, 2, 4], [5, 5, 5], [9, 7, 10]]  # fmt: skip
    at_half = sorted(reading(w, "at half its walls' tick") for w in worlds
                     if worlds[w]["group"] == just)  # fmt: skip
    assert at_half == [(4, 4)] * 4 + [(8, 24)]
    assert {reading(w, "at twice its walls' tick") for w in worlds
            if worlds[w]["group"] == just} == {(4, 12)}  # fmt: skip
    # 3. the rung of its block at a world's own tick
    assert spans("the rung at its own tick", PLAIN)[2] == (0.021, 0.043)
    assert spans("the rung at its own tick", HOW)[2] == (0.017, 0.048)
    for world, told in worlds.items():
        rung = told["the rung at its own tick"]
        assert rung["tick"] == rung["block"] ** 2 // 4 and rung["pace"] == 1.0, world
        if told["group"] == just:
            assert rung["block"] == 4 and 0.5 <= rung["read at"] / told["walls' tick"] <= 0.55
    # 4. the ten missed: no block of the still world, and a noise for the plain table of seven
    nobody = "changes of hands to or from no leader"
    still = found["the still world's readings"]
    assert [still[key][nobody] for key in ("8 at 16", "4 at 4", "2 at 1")] == [
        0.174, 0.4657, 0.8393]  # fmt: skip
    thin = [w[nobody] for w in worlds.values() if w["group"] == missed]
    assert (min(thin), max(thin)) == (0.1258, 0.1834)
    noisy = sorted(w["the rung at its own tick"][PLAIN]["with a noise"][more]
                   for w in worlds.values() if w["group"] == missed)  # fmt: skip
    assert sum(value <= 0.031 for value in noisy) == 7 and noisy[7] == 0.0502
    assert count("the rung at its own tick with a noise", PLAIN, "4.0%") == [10, 3, 5, 7]
    assert count("the rung at its own tick with a noise", HOW, "4.0%") == [10, 2, 4, 1]

    # 5. run on: the nearest reading's rule does as the world's own; the look's ends nearer
    def ran(world, name, sees):
        return worlds[world]["run on"][f"{name}, {sees}"]["amiss over changed"]

    for world, told in worlds.items():
        if told["group"] == just:
            for sees, low, high in ((PLAIN, 0.71, 0.78), (HOW, 0.82, 0.89)):
                own, near_rule = (
                    ran(world, "its own rule", sees),
                    ran(world, "the nearest reading", sees),
                )
                looks = ran(world, "the look's reading", sees)
                assert (
                    1.0 < near_rule / own < 1.10
                    and low - 0.005 <= looks / near_rule <= high + 0.005
                )
        if told["group"] == missed:
            assert ran(world, "the look's reading", PLAIN) < ran(
                world, "the nearest reading", PLAIN
            )
            assert (
                ran(world, "the nearest reading", PLAIN) <= ran(world, "its own rule", PLAIN) + 0.03
            )
    # 6. what leaders alone say: [same reading, same block, of]
    by_leaders = found["placed by its leaders alone, by group as [same reading, same block, of]"]
    assert [by_leaders[g] for g in groups] == [[4, 7, 10], [0, 1, 4], [4, 5, 5], [0, 7, 10]]
