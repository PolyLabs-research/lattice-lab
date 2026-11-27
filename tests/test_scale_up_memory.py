"""A coarse rule that remembers (examples/scale-up-memory/look.py): its readings of a block's
past, its tallies and rules on made-up runs whose answer is known, its run-ons beside the
instrument's own, the whole look end to end on worlds small enough to run here, and what the
look found.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-memory"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LOOK = _load("scale_up_memory_look", LAB / "look.py")
STUDY, LADDER = LOOK.study, LOOK.ladder
PLAIN, BEFORE, Age = LOOK.PLAIN, LOOK.BEFORE, LOOK.Age


def _random_run(seed: int = 5, readings: int = 40, side: int = 12) -> np.ndarray:
    """Leaders of a made-up run: blocks that mostly keep their leader, read every generation."""
    rng = np.random.default_rng(seed)
    frames = [rng.integers(0, 3, size=(side, side))]
    for _ in range(readings - 1):
        keep = rng.random((side, side)) < 0.8
        frames.append(np.where(keep, frames[-1], rng.integers(0, 3, size=(side, side))))
    return np.stack(frames).astype(np.int8)


def test_what_each_reading_sees_of_a_blocks_past():
    frames = _random_run()
    at = np.array([20, 24, 31])
    block, tick = 1, 2  # read every generation; a tick is two of them
    assert not PLAIN.code(frames, block, tick, at).any() and PLAIN.size == 1
    assert np.array_equal(BEFORE.code(frames, block, tick, at), frames[at - 2])
    with pytest.raises(ValueError):
        BEFORE.code(frames, block, tick, np.array([1]))
    # how long: counted the slow way, one block at a time
    for cap in (1, 2, 4, 8):
        seen = Age(cap).code(frames, block, tick, at)
        for i, g in enumerate(at):
            for r in range(frames.shape[1]):
                for c in range(frames.shape[2]):
                    ticks = 1
                    while ticks < cap and frames[g - ticks * tick, r, c] == frames[g, r, c]:
                        ticks += 1
                    assert seen[i, r, c] == ticks - 1
    # a run younger than the cap: a block is as old as the run lets it be
    young = Age(16).code(frames, block, tick, np.array([6]))
    assert young.max() <= 3
    with pytest.raises(ValueError):
        Age(0)
    # one tick on: the leader one tick before is the old leader; how long goes up or starts anew
    old, new = frames[20], frames[22]
    assert np.array_equal(BEFORE.moved(BEFORE.code(frames, 1, 2, np.array([20]))[0], old, new),
                          old)  # fmt: skip
    for cap in (2, 4, 8):
        code = Age(cap).code(frames, 1, 2, np.array([20]))[0]
        assert np.array_equal(Age(cap).moved(code, old, new),
                              Age(cap).code(frames, 1, 2, np.array([22]))[0])  # fmt: skip


def test_the_tallies_are_the_instruments_own_with_more_in_view():
    frames = _random_run(readings=60)
    span = (1, 2, 34, 56)  # block, tick, first and last generation
    plain = LADDER.tally(frames, *span)
    assert np.array_equal(LOOK.tally(PLAIN, frames, *span)[0], plain)
    before = LOOK.tally(BEFORE, frames, *span)
    long = LOOK.tally(Age(16), frames, *span)
    assert before.shape == (3, 3, 9, 9, 3) and long.shape == (16, 3, 9, 9, 3)
    assert np.array_equal(before.sum(axis=0), plain) and np.array_equal(long.sum(axis=0), plain)
    for cap in (1, 2, 4, 8, 16):
        assert np.array_equal(Age(cap).of(long), LOOK.tally(Age(cap), frames, *span))
    assert np.array_equal(PLAIN.of(long)[0], plain) and np.array_equal(PLAIN.of(before)[0], plain)
    # a block led by the same one tick before is one that has had its leader two ticks or more
    held = sum(before[kind, kind] for kind in (1, 2))
    assert np.array_equal(held, Age(2).of(long)[1, 1:].sum(axis=0))
    with pytest.raises(ValueError):
        BEFORE.of(long)
    with pytest.raises(ValueError):
        Age(8).of(Age(4).of(long))
    # changing hands, by the past: together they are the instrument's
    assert np.array_equal(LOOK.hands(long).sum(axis=0), LADDER.hands(plain))


def test_a_rule_with_more_in_view_falls_back_on_one_with_less():
    frames = _random_run(readings=60)
    span = (1, 2, 34, 56)
    plain = LADDER.chances(LADDER.tally(frames, *span))
    for reading in (BEFORE, Age(2), Age(4), Age(8)):
        counts = LOOK.tally(reading, frames, *span)
        chance = reading.chances(counts)
        assert chance.shape == counts.shape and np.allclose(chance.sum(axis=-1), 1)
        assert (chance > 0).all()
    assert np.array_equal(Age(1).chances(LOOK.tally(Age(1), frames, *span))[0], plain)
    assert np.array_equal(PLAIN.chances(LOOK.tally(PLAIN, frames, *span))[0], plain)
    # a view never seen with its past answers as the rule with less in view does
    counts = LOOK.tally(BEFORE, frames, *span)
    counts[2, 1, 3, 4] = 0
    assert np.allclose(
        BEFORE.chances(counts)[2, 1, 3, 4], LADDER.chances(counts.sum(axis=0))[1, 3, 4]
    )
    # and one seen a great many times answers with what it saw
    counts[2, 1, 3, 4] = [9000, 1000, 0]
    assert np.allclose(BEFORE.chances(counts)[2, 1, 3, 4], [0.9, 0.1, 0.0], atol=1e-3)
    # how long: a span never seen answers as the same with a cap one tick lower
    long = LOOK.tally(Age(4), frames, *span)
    long[3] = 0
    shorter = Age(3).chances(Age(3).of(long))
    assert np.allclose(Age(4).chances(long)[3], shorter[2])


def _beats(period: tuple[int, ...], ticks: int = 1040, side: int = 6) -> np.ndarray:
    """A made-up world with a memory: every block has the same leader, which goes round
    `period` for ever, one step a tick. Read every sixteen generations, which is its tick."""
    return np.stack([np.full((side, side), period[t % len(period)], dtype=np.int8)
                     for t in range(ticks)])  # fmt: skip


BEAT = (16, 16)  # the made-up worlds' block and tick: a reading every tick
LEARN = (*BEAT, 16 * 16, 1000 * 16)  # a rule learns from 984 ticks
AHEAD = (1000 * 16, 1008 * 16)  # and is run on for eight: its tallies leave it no doubt


def test_a_world_with_a_memory_is_foretold_only_by_a_rule_that_remembers():
    """Leaders that go 1, 1, 2, 2 for ever: a block led by 1 stays if it has just come over
    and goes over if it has held. The rule as it is can only toss a coin for it; with the
    leader one tick before in view there is nothing left to guess."""
    frames = _beats((1, 1, 2, 2))
    two, four = Age(2), Age(4)
    learn = {r: LOOK.tally(r, frames, *LEARN) for r in (PLAIN, BEFORE, two, four)}
    assert learn[PLAIN].sum() == 984 * 36
    assert LOOK.surprise(PLAIN, learn[PLAIN], learn[PLAIN]) == pytest.approx(1.0, abs=0.001)
    for reading in (BEFORE, two, four):
        assert LOOK.surprise(reading, learn[reading], learn[reading]) < 0.001
    # a tally with more in view scores a rule with less
    assert LOOK.surprise(PLAIN, learn[four], learn[four]) == pytest.approx(1.0, abs=0.001)
    # leaders that go 1, 1, 1, 2, 2, 2: one tick of the past cannot tell the second tick of a
    # lead from the third; how long it has been does
    slow = _beats((1, 1, 1, 2, 2, 2))
    before = LOOK.tally(BEFORE, slow, *LEARN)
    assert LOOK.surprise(BEFORE, before, before) > 0.6
    long = LOOK.tally(four, slow, *LEARN)
    assert LOOK.surprise(four, long, long) < 0.001
    assert LOOK.surprise(two, long, long) > 0.6
    # run on by itself, the rule that remembers keeps the made-up world to the block, and
    # goes back as often as it does (never: a block that changes hands stays a tick)
    found = LOOK.ahead(BEFORE, frames, learn[BEFORE], *BEAT, (1, 2, 3), *AHEAD)
    assert found["apart_rule"][-1] == 0 and found["apart_other"] == 0
    assert found["apart_twin"][-1] == 0 and found["apart_start"][-1] == 0
    assert found["changes_world"] == found["changes_rule"] == 0.5
    assert found["returns_world"] == found["returns_rule"] == 0
    assert found["generations_on"] == [16, 32, 64, 128] and found["rule_sha256"] is None
    kept = LOOK.ahead(four, slow, long, *BEAT, (1, 2, 3), *AHEAD)  # and so does how long
    assert kept["apart_rule"][-1] == 0 and kept["changes_rule"] == kept["changes_world"]
    lost = LOOK.ahead(PLAIN, frames, learn[PLAIN], *BEAT, (1, 2, 3), *AHEAD)
    assert lost["apart_rule"][-1] > 0.3 and lost["returns_rule"] > 0.3
    assert lost["rule_sha256"] == LADDER.digest(learn[PLAIN][0])
    # a world that goes 1, 2, 1, 2: every change of hands is a going back
    there = _beats((1, 2))
    back = LOOK.ahead(BEFORE, there, LOOK.tally(BEFORE, there, *LEARN), *BEAT, (1,), *AHEAD)
    assert back["returns_world"] == back["returns_rule"] == 1 and back["apart_rule"][-1] == 0
    assert LOOK.going_back(there[0], there[1], there[2]) == (36, 36)
    assert LOOK.going_back(frames[1], frames[2], frames[3]) == (0, 0)
    assert LOOK.going_back(frames[0], frames[1], frames[2]) == (36, 0)


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Both worlds on a grid of side 128 for 1,024 generations, two starts each, the rungs'
    ages shrunk to fit (as the next-rung study's own tests run it)."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(STUDY, "SIDE", 128)
    monkeypatch.setattr(STUDY, "GENERATIONS", 1024)
    monkeypatch.setattr(STUDY, "STARTS", 2)
    monkeypatch.setattr(STUDY, "AGES", {4: (64, 128), 8: (128, 256), 16: (256, 512),
                                        32: (512, 1024)})  # fmt: skip
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    monkeypatch.setattr(LOOK, "PAIRS", 2)
    return tmp_path


def test_a_run_on_with_nothing_of_the_past_in_view_is_the_instruments_own(small):
    frames = STUDY.fine("busy", 18101)
    for block in (8, 16):
        first, last = STUDY.AGES[block]
        tick = LADDER.square(block)
        counts = LADDER.tally(frames[block], block, tick, first, last)
        theirs = LADDER.ahead(frames[block], counts, block, tick, (18101, block, 0), first, last)
        mine = LOOK.ahead(PLAIN, frames[block], counts[None], block, tick, (18101, block, 0),
                          first, last)  # fmt: skip
        assert {key: mine[key] for key in theirs} == theirs
        again = LOOK.ahead(PLAIN, frames[block], counts[None], block, tick, (18101, block, 0),
                           first, last, pair=1)  # fmt: skip
        assert again["apart_rule"] != mine["apart_rule"]  # other draws
        assert again["apart_start"] == mine["apart_start"]  # of the same world
        assert again["returns_world"] == mine["returns_world"]


def test_the_look_end_to_end_on_small_worlds(small):
    STUDY.execute(STUDY.RECORDS, 1)
    records = [json.loads(line) for line in STUDY.RECORDS.read_text().splitlines()]
    assert LOOK.missing() == []
    worlds = {name: LOOK.World(name, records=records) for name in STUDY.WORLDS}
    still, busy = worlds["still"], worlds["busy"]
    assert still.splits() == [((18001,), (18002,)), ((18002,), (18001,))]
    assert LOOK.halves((1, 2, 3, 4)) == [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    assert LOOK.halves((7,)) == [(7,)]
    # what a rule sheds by learning from twice as much, worked out by hand for four starts
    # that are two starts twice over
    trial = busy.counts(BEFORE, busy.seeds, 8)
    a, b = (still.counts(BEFORE, (seed,), 8) for seed in still.seeds)

    def bits(rule):
        return LOOK.surprise(BEFORE, rule, trial)

    one = (bits(a) + bits(b)) / 2
    two = (4 * bits(a + b) + bits(2 * a) + bits(2 * b)) / 6
    four = bits(2 * a + 2 * b)
    assert LOOK.shed(still, BEFORE, (*still.seeds, *still.seeds), 8, trial) == pytest.approx(
        (one - two, two - four))  # fmt: skip
    assert LOOK.learned(still, BEFORE, still.seeds, 8, trial) == pytest.approx(
        (bits(a + b), 2 * bits(a + b) - (bits(a) + bits(b)) / 2))  # fmt: skip
    # the leaders kept give the registered tallies; leaders that do not are refused
    wrong = [dict(r, tally={b: [[0, 0, 0, 0, 1]] for b in r["tally"]}) if r["kind"] == "start"
             else r for r in records]  # fmt: skip
    with pytest.raises(ValueError):
        LOOK.World("still", records=wrong)
    m = STUDY.Measures(records, STUDY.design())
    for world in (still, busy):
        ahead = LOOK.one_tick(world)
        hands = LOOK.changing(world)
        gaps = LOOK.rungs(world)
        assert set(ahead) == set(hands) == {"4", "8", "16", "32"} and set(gaps) == {"8", "16", "32"}
        for block in STUDY.BLOCKS:
            told = ahead[str(block)]
            learn = world.counts(PLAIN, world.plan["learn"], block)[0]
            trial = world.counts(PLAIN, world.plan["try"], block)[0]
            assert np.array_equal(learn, m.rule(world.name, "learn", block))
            assert told["transitions tried on"] == int(trial.sum())
            plain = told["the registered choice, bits a block"][PLAIN.name]
            assert plain == round(LADDER.surprise(learn, trial), 6)
            assert set(told["every choice"]) == {r.name for r in LOOK.READINGS}
            # with one start to learn from there is no half of it: endless data is what there is
            for found in told["every choice"].values():
                assert found["bits a block"] == found["bits a block, with endless data"]
                assert "bits shed by learning from twice as much" not in found
            # changing hands as it is: the instrument's own; and by the past, the same blocks
            both = world.counts(PLAIN, world.seeds, block)[0]
            rows = hands[str(block)]
            assert rows["blocks"]["as it is"] == [int(n) for n in LADDER.hands(both)[:, 0]]
            spans = [f"has had its leader for {name} ticks" for name in LOOK.SPANS]
            assert [sum(rows["blocks"][s][n] for s in spans) for n in range(9)] == rows["blocks"][
                "as it is"]  # fmt: skip
            assert sum(rows["share of blocks, by how long they have had their leader"].values()
                       ) == pytest.approx(1, abs=1e-3)  # fmt: skip
        # the mix of young and old leads: at the top rung it is the rule as it is
        mixed = LOOK.mix(world)
        assert set(mixed) == {"3", "4", "5", "6"}
        for near, told in mixed.items():
            top = told["32"]
            if top["as it is"] is not None:
                assert top["as it is"] == pytest.approx(
                    top["with this rung's mix and the top rung's chances"], abs=1e-4)  # fmt: skip
            for block in STUDY.BLOCKS:
                both = LADDER.hands(world.counts(PLAIN, world.seeds, block)[0])[int(near)]
                assert told[str(block)]["as it is"] == (
                    round(float(both[1] / both[0]), 4) if both[0] else None)  # fmt: skip
        for block in STUDY.BLOCKS:
            rows = hands[str(block)]
            both = world.counts(PLAIN, world.seeds, block)[0]
            changed = LADDER.hands(both)[:, 1].sum()
            none = both[1, :, :, 0].sum() + both[2, :, :, 0].sum()
            assert rows["of the blocks that changed hands, the share left with no leader"] == round(
                float(none / changed), 4)  # fmt: skip
        for block in LOOK.RUNGS:
            # step 4g's gap, to the figure, for the rule as it is
            plain = gaps[str(block)][PLAIN.name]
            assert plain["step 4g's way, the registered choice, more surprise"] == STUDY.number(
                m.gap(world.name, block))  # fmt: skip
    ran = LOOK.run_on(busy)  # checks the plain rule's first run against the registered run-on
    assert set(ran) == {"8", "16", "32"}
    below_over_own = "blocks amiss, the rule from the rung below over the rung's own"
    for block in ran:
        assert set(ran[block]) == {r.name for r in LOOK.RUN}
        for name, told in ran[block].items():
            for whose in (LOOK.OWN, LOOK.BELOW):
                found = told[whose]
                (amiss,), (changed,) = found["amiss, start by start"], found[
                    "changed, start by start"]  # one trial start  # fmt: skip
                assert found["amiss over changed"] == pytest.approx(amiss / changed, abs=1e-4)
                world = found["blocks that change hands in a tick"]["the world"]
                assert 0 <= world < 1 and 0 <= found["of those, going back"]["the world"] <= 1
            ratio = told[below_over_own]
            assert ratio["the least and the most of one start"] == [ratio["together"]] * 2
            assert ratio["together"] == pytest.approx(
                told[LOOK.BELOW]["amiss, start by start"][0]
                / told[LOOK.OWN]["amiss, start by start"][0], abs=1e-4)  # fmt: skip
            assert ("blocks amiss, over the rule as it is" in told) == (name != PLAIN.name)
            # one start to learn from has no half
            assert "blocks amiss, its own learned from half its starts over from all" not in told
    # a registered run-on that is not what the leaders give is refused
    rule = busy.counts(PLAIN, busy.plan["learn"], 8)
    LOOK.ran(busy, PLAIN, 8, rule, LOOK.OWN)
    assert LOOK.ran(busy, PLAIN, 8, rule, LOOK.OWN) is ran["8"][PLAIN.name][LOOK.OWN]  # kept
    busy.ran.clear()
    busy.registered = {key: dict(row, apart_rule=[9.0] * len(row["apart_rule"]))
                       for key, row in busy.registered.items()}  # fmt: skip
    with pytest.raises(ValueError):
        LOOK.ran(busy, PLAIN, 8, rule, LOOK.OWN)
    # a rule with a past in view, or one from another world, has no registered run-on to be
    LOOK.ran(busy, BEFORE, 8, busy.counts(BEFORE, busy.plan["learn"], 8), LOOK.OWN)
    LOOK.ran(busy, PLAIN, 8, still.counts(PLAIN, still.plan["learn"], 8), None)
    other = LOOK.between(still, busy)
    assert set(other) == {"4", "8", "16", "32"}
    for block, told in other.items():
        assert set(told) == {r.name for r in LOOK.READINGS}
        for reading in LOOK.RUN:
            assert ("run on, amiss over changed" in told[reading.name]) == (block != "4")
    assert json.loads(json.dumps([ahead, hands, gaps, ran, other]))


def test_the_picture_of_the_table_by_a_blocks_past():
    """The page of charts is drawn from the look's summary: a line for each rung where blocks
    enough stand behind it, a table of every value, and nothing from outside the page."""
    pictures = _load("scale_up_memory_pictures", LAB / "pictures.py")
    spans = [f"has had its leader for {name} ticks" for name in LOOK.SPANS]
    assert tuple(LOOK.SPANS) == pictures.SPANS and len(pictures.SHORT) == len(pictures.SPANS)
    chance = {name: [0.0, 0.0, 0.001, 0.05 / (i + 1), 0.2 / (i + 1), 0.5, 0.6, None, None]
              for i, name in enumerate(["as it is", *spans])}  # fmt: skip
    rungs = {block: {"chance": chance} for block in pictures.BLOCKS}
    summary = {"worlds": {world: {"changing hands, by a block's past": rungs}
                          for world in pictures.WORLDS}}  # fmt: skip
    assert pictures.chances(summary, "still", 4) == [[0.2 / (i + 2) for i in range(6)]] * 4
    page = pictures.page(summary)
    assert page.count("<figure data-chart=") == 6 and page.count("<polyline") == 6 * 4
    assert page.count('class="dot"') == 6 * 4 * 6 and "The values as a table" in page
    assert page.count("<tr>") == 1 + 2 * 3 * 7  # the head, and every row of the table
    assert "http" not in page.replace("http-equiv", "")  # needs nothing but a browser
    # a chance of nought or with too few blocks behind it breaks its line and draws no point
    chance[spans[2]][3] = None
    chance[spans[3]][3] = 0.0
    broken = pictures.page(summary)
    assert broken.count('class="dot"') == 6 * 4 * 6 - 2 * 4 * 2
    # the chances are on a scale of tenfolds, the same in every chart
    assert pictures.y_at(1.0) == pictures.TOP
    assert pictures.y_at(0.1) - pictures.y_at(1.0) == pytest.approx(
        pictures.y_at(0.001) - pictures.y_at(0.01))  # fmt: skip
    assert pictures.y_at(0.0) == pictures.y_at(pictures.LOW) == pictures.HEIGHT - pictures.BOTTOM


# --- what the look found -------------------------------------------------------------------------

REMEMBERS = "and how long it has had its leader, up to 8 ticks"
SHORTER = "and how long it has had its leader, up to 4 ticks"


def _summary() -> dict:
    path = LAB / "look" / "summary.json"
    if not path.exists():
        pytest.skip("the look has not been run")
    return json.loads(path.read_text())["worlds"]


def test_the_look_found_what_the_plan_says_of_the_table():
    """Items 1, 2 and 7 of step 4h in the plan: the table by a block's past, rung by rung."""
    worlds = _summary()
    assert set(worlds) == {"still", "busy"}
    rungs = ("4", "8", "16", "32")
    spans = [f"has had its leader for {name} ticks" for name in LOOK.SPANS]
    old, new = spans[-1], spans[0]
    for name, world in worlds.items():
        table = {b: world["changing hands, by a block's past"][b] for b in rungs}
        chance = {b: table[b]["chance"] for b in rungs}
        # item 1: the longer a block has had its leader, the less it changes hands
        for near in (3, 4, 5):
            ladder = [chance["16"][span][near] for span in spans]
            assert ladder == sorted(ladder, reverse=True), (name, near)
            assert ladder[-1] < chance["16"]["as it is"][near] < ladder[0]
        assert 0.30 < chance["16"][new][4] < 0.33 and 0.038 < chance["16"][old][4] < 0.042
        assert chance["16"]["as it is"][4] == pytest.approx(0.076, abs=0.0005)
        # blocks that have just changed hands are one or two in a hundred, fewer up the ladder
        just = [table[b]["share of blocks, by how long they have had their leader"]["1"]
                for b in rungs]  # fmt: skip
        assert just == sorted(just, reverse=True) and 0.007 < just[-1] < just[0] < 0.024
        # item 2: at five rival neighbours an old lead's chance is the same from blocks of 16
        # to 32 (in the busy world from blocks of 8), while the rule as it is falls
        five = [chance[b][old][5] for b in rungs]
        assert five[3] == pytest.approx(five[2], rel=0.01)
        plain = [chance[b]["as it is"][5] for b in rungs]
        assert 0.29 < 1 - plain[3] / plain[0] < 0.42
        # and the fall is the mix of young and old leads
        mix = world["the mix of young and old leads"]
        for b in rungs:
            told = mix["5"][b]
            assert told["with this rung's mix and the top rung's chances"] == pytest.approx(
                told["as it is"], rel=0.04)  # fmt: skip

        def share(near: str, block: str, mix=mix) -> float:
            """How much of the plain rule's fall from a rung to the top the mix accounts for."""
            top, here = mix[near]["32"]["as it is"], mix[near][block]
            return (here["with this rung's mix and the top rung's chances"] - top) / (
                here["as it is"] - top)  # fmt: skip

        for b in ("4", "8", "16"):
            assert 0.30 < share("4", b) < 0.43 and 0.06 < share("3", b) < 0.14
            assert share("5", b) > 1.0
        # at three the chance itself falls at every rung, young lead and old
        young = [chance[b][new][3] for b in rungs]
        aged = [chance[b][old][3] for b in rungs]
        for before, after in zip(young, young[1:], strict=False):
            assert 0.5 < after / before < 0.84
        for before, after in zip(aged, aged[1:], strict=False):
            assert after / before < 0.42
        # for an old lead at four the steps halve
        four = [chance[b][old][4] for b in rungs]
        steps = [a - b for a, b in zip(four, four[1:], strict=False)]
        assert all(
            0.4 < after / before < 0.6 for before, after in zip(steps, steps[1:], strict=False)
        )
        assert 0.025 < four[3] - steps[2] < 0.031  # where halving steps would end
    # item 7: the bottom rung has ties
    ties = {name: [world["changing hands, by a block's past"][b][
        "of the blocks that changed hands, the share left with no leader"] for b in rungs]
        for name, world in worlds.items()}  # fmt: skip
    assert [round(t, 2) for t in ties["still"]] == [0.30, 0.09, 0.03, 0.01]
    assert [round(t, 2) for t in ties["busy"]] == [0.37, 0.13, 0.04, 0.01]
    still = worlds["still"]["changing hands, by a block's past"]["16"]["chance"]
    assert [still[span][5] for span in spans] == [0.551, 0.4419, 0.3918, 0.3076, 0.1866, 0.1569]
    busy = worlds["busy"]["changing hands, by a block's past"]
    assert [round(busy[b]["chance"][old][5], 3) for b in rungs] == [0.203, 0.19, 0.19, 0.19]


def test_the_look_found_what_the_plan_says_one_tick_ahead():
    """Items 1, 3 and 6 of step 4h in the plan, and the check on its correction."""
    worlds = _summary()
    registered = json.loads((LOOK.RUNG / "ledger.jsonl").read_text().splitlines()[-1])["body"]
    gap = "gap: the rule from the rung below, more surprise"
    endless = "with endless data, more surprise"
    found = {}
    for name, world in worlds.items():
        for block in ("8", "16", "32"):
            told = world["between rungs"][block]
            # with nothing of the past in view, step 4g's way gives step 4g's registered gap
            assert told[PLAIN.name]["step 4g's way, the registered choice, more surprise"] == (
                registered["worlds"][name]["rungs"][block][gap])  # fmt: skip
            for reading in LOOK.READINGS:
                found[name, block, reading.name] = told[reading.name][endless]["mean"]
        # a block's past removes this share of the plain rule's surprise
        for block, told in world["one tick ahead"].items():
            every = told["every choice"]
            removed = "share of the plain rule's surprise removed"
            assert 0.045 < every[BEFORE.name][removed]["mean"] < 0.08, (name, block)
            for reading in (SHORTER, REMEMBERS):
                assert 0.055 < every[reading][removed]["mean"] < 0.115, (name, block)
    shown = {key: round(100 * value, 1) for key, value in found.items()}
    # the table of item 3
    assert [shown["still", b, PLAIN.name] for b in ("8", "16", "32")] == [8.6, 2.8, 1.5]
    assert [shown["still", b, BEFORE.name] for b in ("8", "16", "32")] == [8.0, 2.6, 1.2]
    assert [shown["still", b, SHORTER] for b in ("8", "16", "32")] == [7.3, 2.3, 1.1]
    assert [shown["still", b, REMEMBERS] for b in ("8", "16", "32")] == [7.0, 2.1, 0.6]
    assert [shown["busy", b, PLAIN.name] for b in ("8", "16", "32")] == [5.6, 3.0, 1.8]
    assert [shown["busy", b, BEFORE.name] for b in ("8", "16", "32")] == [5.8, 2.7, 1.3]
    assert [shown["busy", b, SHORTER] for b in ("8", "16", "32")] == [5.8, 2.5, 0.8]
    assert [shown["busy", b, REMEMBERS] for b in ("8", "16", "32")] == [5.7, 2.2, -0.4]
    # at blocks of 32 the spread between choices of starts is as wide as the differences
    for name in worlds:
        told = worlds[name]["between rungs"]["32"]
        assert told[REMEMBERS][endless]["spread"] > 0.009 > told[PLAIN.name][endless]["spread"]
        assert worlds[name]["between rungs"]["16"][PLAIN.name][endless]["spread"] < 0.001
    # the check on the correction: at blocks of 16 and 32 a rule sheds less than twice as much
    # from one start to two as from two to four, in all but one case of the sixteen
    ratios = sorted(
        told["bits shed by learning from twice as much"]["the first over the second"]
        for world in worlds.values() for block in ("16", "32")
        for told in world["one tick ahead"][block]["every choice"].values())  # fmt: skip
    assert len(ratios) == 16 and 1.25 < ratios[0] and ratios[14] < 1.85 and ratios[15] == 2.25
    # item 6: the other world's rule, one tick ahead
    for world in worlds.values():
        other = world["the other world's rule"]
        for block in ("8", "16", "32"):
            assert 0.0015 < other[block][PLAIN.name]["more surprise"]["mean"] < 0.0045
        for block in ("8", "16"):
            assert 0.0045 < other[block][SHORTER]["more surprise"]["mean"] < 0.0085


def test_the_look_found_what_the_plan_says_of_the_run_ons():
    """Items 4, 5 and 6 of step 4h in the plan."""
    worlds = _summary()
    rungs = ("8", "16", "32")
    readings = (PLAIN.name, BEFORE.name, REMEMBERS)
    below_over_own = "blocks amiss, the rule from the rung below over the rung's own"

    def told(name, what, whose=LOOK.OWN):
        return [[round(what(worlds[name]["run on"][b][reading][whose]), 2) for b in rungs]
                for reading in readings]  # fmt: skip

    # item 4: blocks amiss over blocks that changed, and the walls kept
    assert told("still", lambda r: r["amiss over changed"]) == [
        [0.60, 0.54, 0.51], [0.50, 0.46, 0.47], [0.44, 0.43, 0.47]]  # fmt: skip
    assert told("busy", lambda r: r["amiss over changed"]) == [
        [0.51, 0.46, 0.38], [0.42, 0.41, 0.37], [0.40, 0.41, 0.39]]  # fmt: skip
    assert told("still", lambda r: r["walls kept"]) == [
        [0.86, 0.89, 0.93], [0.94, 0.97, 0.99], [1.01, 1.03, 1.04]]  # fmt: skip
    assert told("busy", lambda r: r["walls kept"]) == [
        [0.89, 0.93, 1.00], [0.98, 1.02, 1.06], [1.04, 1.07, 1.10]]  # fmt: skip
    # it wavers as the world does: the plain rule goes back under half as often as the world
    back = "of those, going back"
    for name in worlds:
        for b in rungs:
            run = worlds[name]["run on"][b]
            world = run[PLAIN.name][LOOK.OWN][back]["the world"]
            assert 0.16 < world < 0.28
            assert run[PLAIN.name][LOOK.OWN][back]["the rule's world"] < 0.45 * world
            assert abs(run[REMEMBERS][LOOK.OWN][back]["the rule's world"] - world) < 0.04
    assert told("still", lambda r: r[back]["the rule's world"]) == [
        [0.11, 0.07, 0.05], [0.27, 0.26, 0.22], [0.27, 0.26, 0.23]]  # fmt: skip
    # fewer blocks amiss than the plain rule: in every start at blocks of 8 and 16
    as_it_is = "blocks amiss, over the rule as it is"
    over_plain = {(name, b): worlds[name]["run on"][b][REMEMBERS][as_it_is][LOOK.OWN]
                  for name in worlds for b in rungs}  # fmt: skip
    assert [round(over_plain[n, b]["together"], 2) for b in rungs for n in ("still", "busy")] == [
        0.73, 0.77, 0.80, 0.89, 0.91, 1.02]  # fmt: skip
    for name in worlds:
        for b in ("8", "16"):
            low, high = over_plain[name, b]["the least and the most of one start"]
            assert 0.72 < low <= high < 0.905
    assert over_plain["still", "32"]["the least and the most of one start"][1] < 0.94
    assert over_plain["busy", "32"]["the least and the most of one start"][1] > 1

    # item 5: the ladder's own test
    def ladder(name):
        return [[round(worlds[name]["run on"][b][reading][below_over_own]["together"], 2)
                 for b in rungs] for reading in readings]  # fmt: skip

    assert ladder("still") == [[1.20, 1.15, 1.12], [1.20, 1.11, 1.06], [1.14, 1.03, 0.99]]
    assert ladder("busy") == [[1.09, 1.13, 1.10], [1.09, 1.05, 1.01], [1.03, 0.98, 0.97]]
    for name in worlds:
        for b in rungs:
            run = worlds[name]["run on"][b]
            # the plain rule from below pays in every start; the remembering one, at blocks
            # of 16 and 32, is within a few percent of the rung's own
            assert run[PLAIN.name][below_over_own]["the least and the most of one start"][0] > 1.05
            if b != "8":
                assert abs(run[REMEMBERS][below_over_own]["together"] - 1) < 0.035
            # and it runs the rung on no worse than the rung's own plain rule does
            assert run[REMEMBERS][LOOK.BELOW]["amiss over changed"] < (
                run[PLAIN.name][LOOK.OWN]["amiss over changed"])  # fmt: skip
            # though it changes hands more often than the rung's own
            changes = "blocks that change hands in a tick"
            more = (run[REMEMBERS][LOOK.BELOW][changes]["the rule's world"]
                    / run[REMEMBERS][LOOK.OWN][changes]["the rule's world"])  # fmt: skip
            assert more > 1.3
            # a rung has enough to learn from: half its starts run the world on as well
            for reading in readings:
                half = run[reading][
                    "blocks amiss, its own learned from half its starts over from all"
                ]
                assert 0.975 < half["together"] < 1.012
    # item 6: each world's remembering rule runs the other
    over_own = "run on, blocks amiss over the world's own rule's"
    for b in rungs:
        assert 0.955 < worlds["still"]["the other world's rule"][b][REMEMBERS][over_own][
            "together"] < 0.985  # fmt: skip
        assert 1.035 < worlds["busy"]["the other world's rule"][b][REMEMBERS][over_own][
            "together"] < 1.065  # fmt: skip
