"""The registered test of whether a rule that remembers carries the class
(examples/scale-up-class-memory): a world's own clock, the design, the measures on made-up
records whose answer is known, the claims, and the whole of it end to end on worlds small
enough to run here.
"""

import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from lattice_lab.ledger import canonical

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-class-memory"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


STUDY = _load("scale_up_class_memory_study", LAB / "study.py")
CLOCK, LOOK, LADDER, MEMORY = STUDY.clock, STUDY.look, STUDY.ladder, STUDY.memory
PLAIN, HOW, OWN, LOOKS = STUDY.PLAIN, STUDY.HOW, STUDY.OWN, STUDY.LOOKS
STILL = STUDY.STILL
SERVED, NEAR, JUST, FAR = STUDY.SERVED, STUDY.NEAR, STUDY.JUST, STUDY.FAR


# --- a world's own clock -------------------------------------------------------------------------


def _thinning(reach: float, power: float = 0.5, generations: int = 5120) -> list[float]:
    """Walls every 64 generations that thin as a power of time and are at the still world's
    share at generation `reach`."""
    return [CLOCK.STARTS_AT * (g / reach) ** -power for g in range(64, generations + 1, 64)]


def test_a_worlds_clock():
    assert (CLOCK.SIDE, CLOCK.GENERATIONS, CLOCK.BLOCK, CLOCK.EVERY) == (1024, 5120, 8, 2)
    assert (CLOCK.FIRST_TICK, CLOCK.LAST_TICK, CLOCK.STILL_TICK, CLOCK.LONGEST) == (16, 64, 16, 80)
    # walls at the still world's share at generation 256 give the still world's tick and window
    assert CLOCK.reaches(_thinning(256)) == pytest.approx(256)
    assert CLOCK.tick_of(_thinning(256)) == 16 and CLOCK.window(16) == (256, 1024)
    # between two readings the walls are taken to thin as a power of time, whatever the power
    assert CLOCK.reaches(_thinning(300)) == pytest.approx(300)
    assert CLOCK.reaches(_thinning(300, power=0.3)) == pytest.approx(300)
    assert CLOCK.reaches(_thinning(300), share=CLOCK.STARTS_AT / 2) == pytest.approx(1200)
    # half the pace is twice the tick, and a tick is a whole number of readings
    assert CLOCK.tick_of(_thinning(512)) == 32 and CLOCK.window(32) == (512, 2048)
    assert CLOCK.tick_of(_thinning(300)) == 18 and CLOCK.tick_of(_thinning(310)) == 20
    assert CLOCK.tick_of(_thinning(70)) == 4 and CLOCK.tick_of(_thinning(65)) == 4
    # the longest tick ends its window with the run; a longer one is no tick here
    assert CLOCK.tick_of(_thinning(1280)) == 80 and CLOCK.window(80) == (1280, 5120)
    assert CLOCK.reaches(_thinning(1320)) == pytest.approx(1320)
    assert CLOCK.tick_of(_thinning(1320)) is None
    # walls below the share at the first reading, or never there, or none: no tick
    assert CLOCK.reaches(_thinning(32)) is None and CLOCK.tick_of(_thinning(32)) is None
    assert CLOCK.reaches([0.5] * 80) is None and CLOCK.tick_of([0.5] * 80) is None
    assert CLOCK.reaches([]) is None
    # walls that do not fall between the two readings: the later one
    assert CLOCK.reaches([0.3, 0.3, CLOCK.STARTS_AT, 0.1]) == pytest.approx(192)


def _brute(leaders: np.ndarray, tick: int, cap: int) -> np.ndarray:
    """A tally over a window counted block by block, by how long (up to `cap` ticks)."""
    first, last = CLOCK.window(tick)
    side = leaders.shape[1]
    counts = np.zeros((cap, 3, 9, 9, 3), dtype=np.int64)
    at = lambda g: leaders[g // CLOCK.EVERY]  # noqa: E731
    for g in range(first, last, tick):
        now, after = at(g), at(g + tick)
        for i in range(side):
            for j in range(side):
                around = [now[(i + a) % side, (j + b) % side]
                          for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]  # fmt: skip
                ticks = 1
                while ticks < cap and at(g - ticks * tick)[i, j] == now[i, j]:
                    ticks += 1
                    if any(at(g - k * tick)[i, j] != now[i, j] for k in range(1, ticks)):
                        ticks -= 1
                        break
                counts[ticks - 1, now[i, j], around.count(1), around.count(2), after[i, j]] += 1
    return counts


def test_a_tally_on_a_worlds_own_clock():
    rng = np.random.default_rng(5)
    tick = 6  # a window from generation 96 to 384, read every 6 generations
    first, last = CLOCK.window(tick)
    # leaders that mostly stay, so that some blocks have had theirs for long
    frames = [rng.integers(0, 3, size=(6, 6))]
    for _ in range(last // CLOCK.EVERY):
        change = rng.random((6, 6)) < 0.08
        frames.append(np.where(change, rng.integers(0, 3, size=(6, 6)), frames[-1]))
    leaders = np.stack(frames).astype(np.int8)
    for reading, cap in ((LOOK.PLAIN, 1), (LOOK.Age(8), 8), (STUDY.LONG, 16)):
        counts = CLOCK.tally(reading, leaders, tick)
        assert counts.shape == (cap, 3, 9, 9, 3) and counts.sum() == 48 * 36
        assert np.array_equal(counts, _brute(leaders, tick, cap))
    # what a coarser reading sees is the finer tally summed
    long = CLOCK.tally(STUDY.LONG, leaders, tick)
    assert np.array_equal(LOOK.Age(8).of(long), CLOCK.tally(LOOK.Age(8), leaders, tick))
    assert np.array_equal(LOOK.PLAIN.of(long), CLOCK.tally(LOOK.PLAIN, leaders, tick))
    assert long[4:].sum() > 0  # and some blocks did hold for five ticks and more
    # at a tick of 16 it is the look's tally of the same leaders kept every 8 generations
    tick = 16
    first, last = CLOCK.window(tick)
    frames = [rng.integers(0, 3, size=(6, 6))]
    for _ in range(last // CLOCK.EVERY):
        change = rng.random((6, 6)) < 0.05
        frames.append(np.where(change, rng.integers(0, 3, size=(6, 6)), frames[-1]))
    leaders = np.stack(frames).astype(np.int8)
    assert np.array_equal(CLOCK.tally(STUDY.LONG, leaders, tick),
                          LOOK.tally(STUDY.LONG, leaders[::4], 8, tick, first, last))  # fmt: skip
    assert np.array_equal(CLOCK.tally(LOOK.PLAIN, leaders, tick)[0],
                          LADDER.tally(leaders[::4], 8, tick, first, last))  # fmt: skip


# --- the design ----------------------------------------------------------------------------------


def test_the_worlds_are_step_4fs_that_keep_the_clock():
    chosen = STUDY.worlds()
    assert list(chosen.values()) == STUDY.select()  # worlds.json is what select gives
    assert len(chosen) == 30 and list(chosen)[0] == STILL == "B245678/S3678"
    assert chosen[STILL]["first"] == 20901 and chosen[STILL]["group"] == "the still world"
    others = [w for rule, w in chosen.items() if rule != STILL]
    assert [w["first"] for w in others] == [20001 + 20 * i for i in range(29)]
    # every one kept the still world's clock in step 4f, and no world that did is left out
    before = _load("scale_up_class_study", ROOT / "examples" / "scale-up-class" / "study.py")
    entries = [json.loads(line) for line in (before.HERE / "ledger.jsonl").read_text().splitlines()]
    told = next(e["body"] for e in entries if e["kind"] == "verdict")["worlds"]
    power = "walls thin as time to the power"
    kept = [rule for rule, found in told.items()
            if rule != STILL and (found[power]["8"] or 0) >= STUDY.ON_THE_CLOCK]  # fmt: skip
    assert sorted(kept) == sorted(w["rule"] for w in others) and len(told) == 39
    for w in others:
        found = told[w["rule"]]
        assert w["power in step 4f"] >= 0.40 and w[STUDY.MISSED] == round(found["least"]["8"], 4)
        assert w["pace by its walls in step 4f"] == round(found["pace by its walls"], 3)
        assert w["group"] == STUDY.group(w)
    assert Counter(w["group"] for w in others) == {SERVED: 10, NEAR: 4, JUST: 5, FAR: 10}
    assert (
        STUDY.group({STUDY.MISSED: 0.01}) == SERVED and STUDY.group({STUDY.MISSED: 0.0101}) == NEAR
    )
    assert STUDY.group({STUDY.MISSED: 0.02}) == NEAR and STUDY.group({STUDY.MISSED: 0.1}) == JUST
    assert STUDY.group({STUDY.MISSED: 0.11}) == FAR
    # no start here was used by an earlier step (step 4i's went up to 19116)
    assert min(w["first"] for w in chosen.values()) == 20001


def test_the_design():
    plan = STUDY.design()
    assert plan[STILL] == {"learn": [20901, 20902], "try": [20903, 20904]}
    assert plan["B23456/S4678"] == {"learn": [20001, 20002], "try": [20003, 20004]}
    jobs = STUDY.start_jobs(plan)
    assert len(jobs) == 120 and len(set(jobs)) == 120
    assert jobs[:2] == [(STILL, 20901), ("B23456/S4678", 20001)] and jobs[30] == (STILL, 20902)
    # two rules of the look's, as it is and with how long in view, and the world's own two
    assert STUDY.READINGS[PLAIN].size == 1 and STUDY.READINGS[HOW].size == 8
    assert STUDY.LONG.size == 16 and STUDY.PAIRS == 8
    lent = STUDY.looks_rule()
    seen = len(LADDER.instants(8, 16, 256, 1024)) * (2048 // 8) ** 2
    assert lent.shape == (16, 3, 9, 9, 3) and lent.sum() == 8 * seen
    assert (STUDY.EARLY, STUDY.LATE) == (1024, 4096)


# --- the measures, on made-up records ------------------------------------------------------------


def _tally(table: dict) -> np.ndarray:
    """A made-up tally by how long: `table` gives, by (ticks, rival neighbours), how many
    blocks species 1 led and how many of them had another leader one tick on."""
    counts = np.zeros((16, 3, 9, 9, 3), dtype=np.int64)
    for (ticks, near), (blocks, changed) in table.items():
        counts[ticks - 1, 1, 8 - near, near] = [0, blocks - changed, changed]
    return counts


def _records(world: str, tallies: dict, ahead: dict | None = None, reach: float = 256,
             larger: float = 0.5, seeds=(1, 2)) -> list[dict]:  # fmt: skip
    """Records of one world with one start to learn from and one to try on: walls that reach
    the still world's share at generation `reach`, the tallies given by seed, and run-ons
    given by (reading, whose) as (amiss, changed)."""
    thin = [round(v, 6) for v in _thinning(reach)]
    tick = CLOCK.tick_of(thin)
    marks = [str(g) for g in (STUDY.EARLY, STUDY.LATE, CLOCK.GENERATIONS)]
    rows = [{"kind": "start", "world": world, "seed": seed, "walls": thin,
             "live": dict.fromkeys(marks, 0.6), "larger": dict.fromkeys(marks, 0.6 * larger)}
            for seed in seeds]  # fmt: skip
    for seed in seeds:
        if tick is None:
            rows.append(STUDY.no_clock("tally", world, seed))
        else:
            rows.append({"kind": "tally", "world": world, "seed": seed, "tick": tick,
                         "window": list(CLOCK.window(tick)), "walls": [0.166, 0.09],
                         "tally": STUDY.sparse(tallies[seed])})  # fmt: skip
    for (reading, whose), (amiss, changed) in (ahead or {}).items():
        rows.append({"kind": "ahead", "world": world, "seed": seeds[1], "tick": tick,
                     "reading": reading, "rule": whose, "amiss": [[amiss, amiss]],
                     "changed": changed})  # fmt: skip
    return rows


def _measures(worlds: dict, lent: np.ndarray) -> "STUDY.Measures":
    """Measures of made-up worlds: `worlds` gives each world's records and what step 4f is
    said to have found of it."""
    rows, plan, chosen = [], {}, {}
    for world, (records, found) in worlds.items():
        rows += records
        plan[world] = {"learn": [1], "try": [2]}
        chosen[world] = {"rule": world, **found}
    return STUDY.Measures(rows, plan, lent=lent, chosen=chosen)


def _bits(chance: float) -> float:
    return -(chance * math.log2(chance) + (1 - chance) * math.log2(1 - chance))


def test_the_measures_on_made_up_records():
    # a world where a block's past matters: at five rival neighbours a lead of one tick
    # changes hands half the time and one of sixteen ticks a tenth of the time
    past = _tally({(1, 5): (100000, 50000), (16, 5): (100000, 10000)})
    # and one where it does not: three times in ten, whatever the block's past
    none = _tally({(1, 5): (100000, 30000), (16, 5): (100000, 30000)})
    run = {(PLAIN, OWN): (0.06, 0.10), (HOW, OWN): (0.04, 0.10),
           (PLAIN, LOOKS): (0.05, 0.10), (HOW, LOOKS): (0.045, 0.10)}  # fmt: skip
    found = {STUDY.MISSED: 0.005, "pace by its walls in step 4f": 0.8}
    m = _measures({"with a past": (_records("with a past", {1: past, 2: past}, run), found),
                   "without": (_records("without", {1: none, 2: none}, reach=512), found),
                   "one sided": (_records("one sided", {1: past, 2: past}, larger=0.9), found),
                   "too slow": (_records("too slow", {}, reach=1400), found)},
                  lent=past)  # fmt: skip
    # a world's clock
    assert m.tick("with a past") == 16 and m.pace("with a past") == 1.0
    assert m.tick("without") == 32 and m.pace("without") == 0.5
    assert m.tick("too slow") is None and m.pace("too slow") is None
    assert m.power("without") == pytest.approx(0.5, abs=1e-4)
    assert m.walls_at("with a past", 256) == pytest.approx(CLOCK.STARTS_AT, abs=1e-6)
    assert m.held("with a past") == pytest.approx(0.5) and m.held("one sided") == pytest.approx(0.9)
    assert m.window_walls("with a past", 0) == 0.166 and m.window_walls("with a past", 1) == 0.09
    assert m.window_walls("too slow", 0) is None
    # what a claim stands on: a tick, and two species holding ground
    assert m.stands("with a past") and m.stands("without")
    assert not m.stands("one sided") and not m.stands("too slow")
    assert not m.stands(None)  # too few worlds to rank
    # one tick ahead: the plain rule sees three in ten, the remembering rule the two chances
    plain = _bits(0.3)
    how = (_bits(0.5) + _bits(0.1)) / 2
    assert m.bits("with a past", PLAIN) == pytest.approx(plain, abs=2e-4)
    assert m.bits("with a past", HOW) == pytest.approx(how, abs=2e-4)
    assert m.removed("with a past") == pytest.approx(1 - how / plain, abs=3e-4)
    assert m.removed("without") == pytest.approx(0.0, abs=3e-4)
    assert m.bits("too slow", PLAIN) is None and m.removed("too slow") is None
    # the look's rule is this world's own: no more surprise; in the world without a past
    # its plain rule is the same too, and its remembering rule is wrong at every age
    assert m.from_look("with a past", PLAIN) == pytest.approx(0.0, abs=3e-4)
    assert m.from_look("with a past", HOW) == pytest.approx(0.0, abs=3e-4)
    assert m.from_look("without", PLAIN) == pytest.approx(0.0, abs=3e-4)
    cross = -(0.3 * (math.log2(0.5) + math.log2(0.1)) + 0.7 * (math.log2(0.5) + math.log2(0.9))) / 2
    assert m.from_look("without", HOW) == pytest.approx(cross / plain - 1, abs=1e-3)
    assert m.from_look("too slow", HOW) is None
    # the table
    assert m.chance("with a past", MEMORY.NEW, 5) == 0.5
    assert m.chance("with a past", MEMORY.OLD, 5) == 0.1
    assert m.chance("with a past", None, 5) == pytest.approx(0.3)
    assert m.chance("with a past", "2", 5) is None and m.chance("with a past", None, 4) is None
    # run on
    assert m.amiss("with a past", PLAIN, OWN) == pytest.approx(0.6)
    assert m.amiss("with a past", HOW, LOOKS) == pytest.approx(0.45)
    assert m.gain("with a past") == pytest.approx(0.9) and m.gain("without") is None
    assert m.amiss("without", PLAIN, OWN) is None
    # every quantity a claim can name
    value = m.value
    world = {"world": "with a past"}
    assert value({**world, "quantity": "tick"}) == 16.0
    assert value({"world": "too slow", "quantity": "tick"}) is None
    assert value({**world, "quantity": "surprise removed"}) == pytest.approx(
        1 - how / plain, abs=3e-4
    )
    assert value({**world, "quantity": "walls at the end of its window over the start"}) == (
        pytest.approx(0.09 / 0.166))  # fmt: skip
    assert value({**world, "quantity": "pace here over the pace in step 4f",
                  "before": 0.8}) == pytest.approx(1.25)  # fmt: skip
    assert value({**world, "quantity": "amiss over changed", "reading": HOW,
                  "rule_of": OWN}) == pytest.approx(0.4)  # fmt: skip
    assert value({"world": "without", "quantity": "the look's rule",
                  "reading": HOW}) == pytest.approx(cross / plain - 1, abs=1e-3)  # fmt: skip
    assert value({"world": "without", "quantity":
                  "the look's rule, with how long in view less as it is"}) == pytest.approx(
        cross / plain - 1, abs=1e-3)  # fmt: skip
    assert value(
        {**world, "quantity": "amiss, the look's remembering rule over its plain one"}
    ) == pytest.approx(0.9)
    assert value({**world, "quantity":
                  "amiss, the look's remembering rule over the world's own"}) == pytest.approx(
        0.045 / 0.04)  # fmt: skip
    assert value(
        {**world, "quantity": "amiss, the look's plain rule over the world's own"}
    ) == pytest.approx(0.05 / 0.06)
    with pytest.raises(ValueError):
        value({**world, "quantity": "something else"})
    # every world against the same bars, whatever is claimed of it
    past, served, how_serves, keeps, runs, gains, as_own = STUDY.bars(m, "with a past").values()
    assert (past, served, how_serves, keeps, runs) == (True, True, True, True, True)
    assert (gains, as_own) == (False, False)  # 0.9 is over 0.85, and 1.125 over 1.12
    assert list(STUDY.bars(m, "without").values()) == [False, True, False, None, None, None, None]
    assert set(STUDY.bars(m, "too slow").values()) == {None}
    # and counted over the worlds that stand: the one-sided world and the slow one are left out
    counted = STUDY.counted(m)
    assert set(counted) == set(STUDY.bars(m, "without"))
    assert counted["a block's past matters"] == {SERVED: [1, 2]}
    assert counted["one tick ahead, the look's rule as it is serves"] == {SERVED: [2, 2]}
    assert counted["one tick ahead, the look's rule with how long in view serves"] == {
        SERVED: [1, 2]}  # fmt: skip
    assert counted["run on, remembering gains"] == {SERVED: [0, 1]}
    assert counted["run on, the look's plain rule keeps it"] == {SERVED: [1, 1]}


def test_the_ranks_over_the_worlds():
    assert STUDY.rank_correlation([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert STUDY.rank_correlation([1, 2, 3, 4], [9, 7, 5, 1]) == pytest.approx(-1.0)
    assert STUDY.rank_correlation([1, 2, 3, 4], [2, 1, 4, 3]) == pytest.approx(0.6)
    assert STUDY.rank_correlation([1, 2], [2, 1]) is None  # too few
    assert STUDY.rank_correlation([1, 2, 3], [5, 5, 5]) is None  # nothing to rank
    # nine worlds: the more step 4f's rule missed one, the less its blocks' past matters and
    # the less the remembering rule gains
    worlds = {}
    for k in range(9):
        young, old = 50000 - 2500 * k, 10000 + 2500 * k  # the two chances close up
        tally = _tally({(1, 5): (100000, young), (16, 5): (100000, old)})
        run = {(PLAIN, LOOKS): (0.05, 0.10), (HOW, LOOKS): (0.040 + 0.001 * k, 0.10),
               (PLAIN, OWN): (0.05, 0.10), (HOW, OWN): (0.04, 0.10)}  # fmt: skip
        name = f"world {k}"
        found = {STUDY.MISSED: 0.01 * (k + 1), "pace by its walls in step 4f": 1.0}
        worlds[name] = (_records(name, {1: tally, 2: tally}, run), found)
    m = _measures(worlds, lent=_tally({(1, 5): (100000, 50000), (16, 5): (100000, 10000)}))
    assert m.stands(None) and len(m.ranked()) == 9
    removed = [m.removed(w) for w in worlds]
    assert removed == sorted(removed, reverse=True) and removed[-1] == pytest.approx(0, abs=3e-4)
    assert m.value(
        {"world": None, "quantity": "ranks: missed in step 4f against surprise removed"}
    ) == pytest.approx(-1.0)
    assert m.value({"world": None, "quantity":
                    "ranks: surprise removed against the gain from remembering"}) == (
        pytest.approx(-1.0))  # fmt: skip
    # the still world is not ranked, nor a world that does not stand
    worlds[STILL] = worlds.pop("world 0")
    assert STILL not in _measures(worlds, lent=_tally({(1, 5): (10, 5)})).ranked()


def test_the_judge():
    claim = {"at_least": 0.9, "at_most": 1.1}
    assert STUDY.judge(1.0, claim, True) == "holds"
    assert STUDY.judge(0.89, claim, True) == STUDY.judge(1.11, claim, True) == "fails"
    assert STUDY.judge(1.0, claim, False) == STUDY.judge(None, claim, True) == "not tested"
    assert STUDY.judge(float("nan"), claim, True) == "not tested"
    assert STUDY.judge(5.0, {"at_least": None, "at_most": 1.1}, True) == "fails"
    assert STUDY.judge(-5.0, {"at_least": None, "at_most": 1.1}, True) == "holds"


def test_the_claims_the_study_registers():
    claims = STUDY.claims()
    labels = [c["label"] for c in claims]
    assert len(labels) == len(set(labels)) == len(claims)
    chosen = STUDY.worlds()
    by_family = Counter(c["family"] for c in claims)
    assert len(claims) == 223 and by_family == {
        "X": 4, "S": 29, "T": 29, "K": 29, "P": 20, "O": 40, "J": 10, "D": 30, "W": 10,
        "B": 20, "G": 2}  # fmt: skip
    for c in claims:
        assert c["at_least"] is not None or c["at_most"] is not None, c["label"]
        assert c["world"] is None or c["world"] in chosen
        assert (c["world"] is None) == (c["family"] == "G")
        assert json.loads(json.dumps(c)) == c
    # the still world carries X alone; every other world S, T and K; the worlds step 4f found
    # served carry P, O and D, those it missed by a tenth or more P, O, W and B, the five it
    # just missed J, and the four nearly served nothing more
    carried = {rule: Counter(c["family"] for c in claims if c["world"] == rule) for rule in chosen}
    assert carried[STILL] == {"X": 4}
    wanted = {SERVED: {"S": 1, "T": 1, "K": 1, "P": 1, "O": 2, "D": 3},
              FAR: {"S": 1, "T": 1, "K": 1, "P": 1, "O": 2, "W": 1, "B": 2},
              NEAR: {"S": 1, "T": 1, "K": 1}, JUST: {"S": 1, "T": 1, "K": 1, "J": 2}}  # fmt: skip
    for rule, w in chosen.items():
        if rule != STILL:
            assert carried[rule] == wanted[w["group"]], rule
    # the two groups are told apart: what must matter in one must not in the other
    assert STUDY.PAST_DOES_NOT < STUDY.PAST_MATTERS and STUDY.SERVES < STUDY.DOES_NOT
    assert STUDY.GAINS < STUDY.NO_GAIN
    bounds = {c["label"]: (c["at_least"], c["at_most"]) for c in claims}
    assert bounds["O B345/S02457: the look's rule as it is serves"] == (None, 0.025)
    assert bounds["J B2458/S578: the look's rule with how long in view does not serve it"] == (
        0.025, None)  # fmt: skip
    assert bounds["O B25/S078: the look's plain rule does not serve"] == (0.05, None)
    assert bounds["D B345/S02457: as well as the world's own"] == (0.90, 1.12)
    assert bounds["X and as well as the still world's own"] == (0.93, 1.07)
    assert bounds["T B345/S02457: its tick is the pace step 4f read"] == (0.7692, 1.3)
    assert STUDY.predictions() == claims
    # every quantity a claim names is one the measures know
    empty = STUDY.Measures([], STUDY.design(), lent=STUDY.looks_rule(), chosen=chosen)
    for c in claims:
        assert empty.value(c) is None, c["label"]
        assert STUDY.judge(empty.value(c), c, empty.stands(c["world"])) == "not tested"


# --- end to end ----------------------------------------------------------------------------------

SMALL = (STILL, "B345/S02457", "B2378/S1348")


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Three worlds on a grid of side 128 for 1,536 generations, one start to learn from and
    one to try on, and one pair of run-ons from each trial start."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(CLOCK, "SIDE", 128)
    monkeypatch.setattr(CLOCK, "GENERATIONS", 1536)
    monkeypatch.setattr(CLOCK, "LONGEST", 1536 // CLOCK.LAST_TICK)
    monkeypatch.setattr(STUDY, "EARLY", 256)
    monkeypatch.setattr(STUDY, "LATE", 1024)
    monkeypatch.setattr(STUDY, "STARTS_EACH", 2)
    monkeypatch.setattr(STUDY, "PAIRS", 1)
    chosen = [w for w in json.loads((LAB / "worlds.json").read_text())["worlds"]
              if w["rule"] in SMALL]  # fmt: skip
    (tmp_path / "worlds.json").write_text(json.dumps({"worlds": chosen}))
    monkeypatch.setattr(STUDY, "WORLDS", tmp_path / "worlds.json")
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    return tmp_path


def test_one_fine_run_on_record(small):
    seed = STUDY.worlds()[STILL]["first"]
    record = STUDY.run_start((STILL, seed))
    assert record == STUDY.run_start((STILL, seed))  # the second time from the leaders kept
    assert (small / "cache" / f"clock-B245678-S3678-128-1536-{seed}.npz").exists()
    assert json.loads(canonical(record)) == record
    kept = CLOCK.fine(STILL, seed)
    assert kept["leaders"].shape == (1536 // 2 + 1, 16, 16) and kept["shares"].shape == (24, 2)
    assert len(record["walls"]) == 24 and set(record["live"]) == {"256", "1024", "1536"}
    assert record["walls"][3] == round(LADDER.walls(kept["leaders"][128]), 6)
    assert record["live"]["1024"] == pytest.approx(kept["shares"][15].sum(), abs=1e-6)
    assert record["larger"]["1536"] == pytest.approx(kept["shares"][23].max(), abs=1e-6)
    # it is the reading step 4e's own code gives of the same world, every 8 generations
    again = LADDER.fine("check", STILL, 1.0, seed, 128, 1536, blocks=(8,))
    assert np.array_equal(kept["leaders"][::4], again[8])
    # its tally at a tick of 16, with nothing of the past in view, is the instrument's
    tally = STUDY.run_tally((STILL, seed, 16))
    assert tally["tick"] == 16 and tally["window"] == [256, 1024]
    assert tally["walls"] == [record["walls"][3], record["walls"][15]]
    counts = STUDY.dense(tally["tally"], 16)
    assert np.array_equal(counts.sum(axis=0), LADDER.tally(again[8], 8, 16, 256, 1024))
    assert STUDY.run_tally((STILL, seed, None)) == {
        "kind": "tally", "world": STILL, "seed": seed, "tick": None}  # fmt: skip


def test_the_study_end_to_end_on_small_worlds(small):
    path = STUDY.RECORDS
    plan = STUDY.design()
    assert {w: len(p["learn"]) + len(p["try"]) for w, p in plan.items()} == dict.fromkeys(SMALL, 2)
    STUDY.execute(path, 1)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    kinds = Counter(r["kind"] for r in rows)
    # three worlds of two starts; four rules run on from each world's one trial start
    assert kinds == {"start": 6, "tally": 6, "ahead": 12}
    assert [r["kind"] for r in rows] == ["start"] * 6 + ["tally"] * 6 + ["ahead"] * 12
    m = STUDY.Measures(rows, plan)
    ticks = {w: m.tick(w) for w in SMALL}
    assert ticks[STILL] is not None and ticks["B2378/S1348"] is None, ticks
    for r in rows:
        if r["kind"] != "start":
            assert r["tick"] == ticks[r["world"]]
    # a world whose walls give it no tick leaves records that say so and hold nothing else
    slow = [r for r in rows if r["world"] == "B2378/S1348" and r["kind"] != "start"]
    assert len(slow) == 2 + 4 and all(set(r) <= {"kind", "world", "seed", "tick", "reading",
                                                 "rule"} for r in slow)  # fmt: skip
    ahead = [r for r in rows if r["kind"] == "ahead" and r["tick"] is not None]
    assert {(r["reading"], r["rule"]) for r in ahead} == {
        (PLAIN, OWN), (PLAIN, LOOKS), (HOW, OWN), (HOW, LOOKS)}  # fmt: skip
    for r in ahead:
        first, last = CLOCK.window(r["tick"])
        assert r["from_generation"] == first and r["generations_on"] == last - first
        assert len(r["amiss"]) == len(r["twin"]) == 1 and r["seed"] in plan[r["world"]]["try"]
    # the look's plain rule's run-on is the look's own, on leaders kept every two generations
    mine = next(r for r in ahead if (r["world"], r["reading"], r["rule"]) == (STILL, PLAIN, LOOKS))
    tick = ticks[STILL]
    theirs = LOOK.ahead(LOOK.PLAIN, CLOCK.fine(STILL, mine["seed"])["leaders"],
                        LOOK.PLAIN.of(STUDY.looks_rule()), CLOCK.EVERY, tick,
                        (mine["seed"], 8, 1), *CLOCK.window(tick))  # fmt: skip
    assert mine["amiss"][0] == [theirs["apart_rule"][-1], theirs["apart_other"]]
    assert mine["changed"] == theirs["apart_start"][-1]
    # a world's own rule is learned from the start it learns from, on its own clock
    own = STUDY.pooled(rows, STILL, plan[STILL]["learn"])
    learn = CLOCK.fine(STILL, plan[STILL]["learn"][0])["leaders"]
    assert np.array_equal(own, CLOCK.tally(STUDY.LONG, learn, tick))
    STUDY.execute(path, 1)  # run again, it finds everything done
    assert len(path.read_text().splitlines()) == len(rows)
    for record in (rows[0], rows[5], rows[6], rows[11], ahead[0], ahead[-1], slow[0], slow[-1]):
        assert canonical(STUDY.rerun(record)) == canonical(record)
    with pytest.raises(ValueError):
        STUDY.rerun({**ahead[0], "seed": 5})
    claims = STUDY.claims()
    found = STUDY.decide(rows, claims)
    assert found["missing"] == [] and set(found["outcomes"]) == {c["label"] for c in claims}
    assert set(found["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert json.loads(json.dumps(found)) == found
    assert sum(sum(words.values()) for words in found["counts"].values()) == len(claims)
    # nothing is claimed of the world without a clock, nor of ranks over so few worlds
    for c in claims:
        if c["world"] in ("B2378/S1348", None):
            assert found["outcomes"][c["label"]] == "not tested", c["label"]
    told = found["worlds"]
    assert told["B2378/S1348"]["tick"] is None and not told["B2378/S1348"]["stands"]
    assert "run on" not in told["B2378/S1348"] and told[STILL]["window"] == list(CLOCK.window(tick))
    assert set(told[STILL]["run on"]) == {f"{reading}, {whose}" for reading in (PLAIN, HOW)
                                          for whose in (OWN, LOOKS)}  # fmt: skip
    assert told[STILL]["bits a block"][PLAIN] == STUDY.number(m.bits(STILL, PLAIN), 6)
    assert told[STILL]["against the bars"] == STUDY.bars(m, STILL)
    met = found["worlds met a bar, of those with the number, by group"]
    assert met == STUDY.counted(m) and set(met) == set(STUDY.bars(m, STILL))
    for by_group in met.values():  # the still world is not counted, nor the world without a clock
        assert sum(of for _, of in by_group.values()) <= 1
    # a record short, or a tally at another tick than the walls give: nothing is judged
    short = STUDY.decide(rows[:-1], claims)
    assert short["missing"] and set(short["outcomes"].values()) == {"missing"}
    assert STUDY.decide(rows[:3], claims)["missing"][0] == f"{STILL} from start 20902"
    wrong = [dict(r, tick=tick + 2) if r["kind"] == "tally" and r["world"] == STILL else r
             for r in rows]  # fmt: skip
    assert "at a tick of" in STUDY.decide(wrong, claims)["missing"][0]


# --- the sizing and the registration -------------------------------------------------------------

WAYS = ("the first half to learn from", "the last half to learn from")


def test_the_bounds_were_sized_on_seen_runs():
    sizing = json.loads((LAB / "sizing.json").read_text())
    sized, chosen = sizing["the sized worlds"], STUDY.worlds()
    # twelve worlds from starts step 4f had run: five served, one nearly, five missed
    assert len(sized) == 12 and set(sized) <= set(chosen)
    assert Counter(w["group"] for w in sized.values()) == {
        "the still world": 1, SERVED: 5, NEAR: 1, FAR: 5}  # fmt: skip
    for rule, w in sized.items():
        assert w["group"] == chosen[rule]["group"] and len(w["starts"]) in (2, 4)
        assert 17001 <= min(w["starts"]) and max(w["starts"]) <= 17908  # step 4f's own
        assert set(WAYS) <= set(w)
    # every claim the study makes of a sized world, both ways round, against today's bounds
    seen = sizing["the study's claims of the sized worlds"]
    claims = {c["label"]: c for c in STUDY.claims({rule: chosen[rule] for rule in sized})}
    assert set(seen) == set(claims)
    amiss = set()
    for label, told in seen.items():
        claim = claims[label]
        assert (told["at least"], told["at most"]) == (claim["at_least"], claim["at_most"]), label
        for way in WAYS:
            assert told[way]["would"] == STUDY.judge(
                told[way]["value"], claim, told[way]["would"] != "not tested"), label  # fmt: skip
            if told[way]["would"] != "holds":
                amiss.add(label)
    assert amiss == SIZED_AMISS
    # and for each bound what the sized worlds gave
    drawn = sizing["what the bounds were drawn from"]
    for name, found in drawn.items():
        if "the sized worlds gave, both ways round" in found:
            gave = found["the sized worlds gave, both ways round"]
            assert gave["values"] and gave["least"] <= gave["most"], name


SIZED_AMISS: set = set()  # the claims that would not have held on the sized worlds


def test_the_registration():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    question = entries[0]["body"]
    registered = [e["body"] for e in entries if e["kind"] == "prediction"]
    assert entries[0]["kind"] == "question" and len(registered) == len(STUDY.claims())
    for body, claim in zip(registered, STUDY.claims(), strict=True):
        assert {k: body[k] for k in claim} == claim
    for name, digest in question["sha256"].items():
        assert STUDY.sha(LAB / name) == digest, name
    assert question["runs"] == 120 + 120 + 240 and question["side"] == 1024
    assert question["generations"] == 5120 and question["run_ons_of_a_rule_from_a_start"] == 16
    assert len(question["worlds"]) == 30
    assert sum(w["in_the_sizing_look"] for w in question["worlds"].values()) == 12


# --- what the run found --------------------------------------------------------------------------


def _verdict():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    verdicts = [e["body"] for e in entries if e["kind"] == "verdict"]
    if not verdicts:
        pytest.skip("not run yet")
    return verdicts[0]


def test_the_verdict_is_what_the_records_give():
    """Judged again here from the records in the repository: the ledger's verdict, to the
    last figure."""
    verdict = _verdict()
    rows = [json.loads(line) for line in (LAB / "records.jsonl").read_text().splitlines()]
    assert Counter(r["kind"] for r in rows) == {"start": 120, "tally": 120, "ahead": 240}
    again = STUDY.decide(rows, STUDY.claims())
    assert again["missing"] == [] and set(again) == set(verdict) - {"question", "cites"}
    for part in again:
        assert again[part] == verdict[part], part


def test_the_registered_run_found_what_the_plan_says():
    verdict = _verdict()
    assert verdict["missing"] == [] and len(verdict["outcomes"]) == 223
    assert Counter(verdict["outcomes"].values()) == {"holds": 222, "fails": 1}
    failed = [label for label, word in verdict["outcomes"].items() if word != "holds"]
    assert failed == ["D B34567/S012457: remembering gains"]
    held = {"X": 4, "S": 29, "T": 29, "K": 29, "P": 20, "O": 40, "J": 10, "W": 10, "B": 20, "G": 2}
    wanted = {family: {"holds": n} for family, n in held.items()}
    assert verdict["counts"] == {"D": {"holds": 29, "fails": 1}, **wanted}
    measured = {label: found["value"] for label, found in verdict["measured"].items()}
    # the anchor, the gradient and the one failure
    assert measured["X the still world's tick"] == 16
    assert round(measured["X the still world's past matters"], 3) == 0.082
    assert round(measured["X the look's remembering rule runs the still world better"], 2) == 0.72
    assert round(measured["X and as well as the still world's own"], 2) == 0.99
    assert (
        round(
            measured["G the more the old rule missed a world, the less its blocks' past matters"], 2
        )
        == -0.94
    )
    assert round(measured["G the more a block's past matters, the more remembering gains"], 2) == (
        -0.86)  # fmt: skip
    assert round(measured["D B34567/S012457: remembering gains"], 2) == 0.94
    assert round(measured["T B34567/S012457: its tick is the pace step 4f read"], 3) == 0.773
    # what the plan tells of each group of worlds
    chosen, told = STUDY.worlds(), verdict["worlds"]
    groups = (SERVED, NEAR, JUST, FAR)

    def spans(read, places=3):
        out = []
        for group in groups:
            values = [read(told[w]) for w in chosen if chosen[w]["group"] == group]
            out.append((round(min(values), places), round(max(values), places)))
        return out

    def ran(reading, whose):
        return lambda t: t["run on"][f"{reading}, {whose}"]["amiss over changed"]

    assert spans(lambda t: t["tick"], 0) == [(16, 44), (20, 32), (22, 80), (24, 70)]
    assert spans(lambda t: t["share of the plain rule's surprise that how long removes"]) == [
        (0.077, 0.108), (0.056, 0.085), (0.051, 0.066), (0.005, 0.03)]  # fmt: skip
    assert spans(lambda t: t["the look's rule, more surprise"][PLAIN]) == [
        (0.0, 0.015), (0.027, 0.037), (0.067, 0.088), (0.171, 0.613)]  # fmt: skip
    assert spans(lambda t: t["the look's rule, more surprise"][HOW]) == [
        (-0.015, 0.0), (-0.002, 0.022), (0.036, 0.063), (0.184, 1.441)]  # fmt: skip
    assert spans(ran(PLAIN, LOOKS), 2) == [(0.47, 0.64), (0.51, 0.57), (0.53, 0.58), (0.65, 0.73)]
    assert spans(ran(HOW, LOOKS), 2) == [(0.40, 0.48), (0.41, 0.47), (0.45, 0.51), (0.59, 0.74)]
    gain = "blocks amiss, the look's remembering rule over its plain one"
    assert spans(lambda t: t[gain], 2) == [
        (0.67, 0.94), (0.80, 0.85), (0.84, 0.89), (0.90, 1.04)]  # fmt: skip
    assert spans(lambda t: ran(HOW, LOOKS)(t) / ran(HOW, OWN)(t), 2) == [
        (0.94, 1.11), (0.96, 1.09), (0.89, 0.92), (0.83, 0.92)]  # fmt: skip
    assert spans(lambda t: ran(PLAIN, LOOKS)(t) / ran(PLAIN, OWN)(t), 2) == [
        (0.87, 1.12), (0.83, 1.26), (0.76, 0.79), (0.78, 0.85)]  # fmt: skip
    walls = "walls at the start and the end of its window"
    assert spans(lambda t: t[walls][1] / t[walls][0], 2) == [
        (0.49, 0.55), (0.50, 0.52), (0.52, 0.54), (0.54, 0.59)]  # fmt: skip
    for world in chosen:
        assert told[world]["stands"] and 0.5 <= told[world][
            "the larger species' share of the live"] <= 0.57, world  # fmt: skip
    # every world against the same bars
    met = verdict["worlds met a bar, of those with the number, by group"]
    counted = {bar: [by[group][0] for group in groups] for bar, by in met.items()}
    assert all(by[group][1] == size for by in met.values()
               for group, size in zip(groups, (10, 4, 5, 10), strict=True))  # fmt: skip
    assert counted == {
        "a block's past matters": [10, 3, 2, 0],
        "one tick ahead, the look's rule as it is serves": [10, 0, 0, 0],
        "one tick ahead, the look's rule with how long in view serves": [10, 4, 0, 0],
        "run on, the look's plain rule keeps it": [10, 4, 5, 10],
        "run on, the look's remembering rule runs it": [10, 4, 5, 0],
        "run on, remembering gains": [9, 4, 1, 0],
        "run on, the look's remembering rule does as the world's own": [10, 4, 3, 1],
    }


def test_what_was_read_after_the_verdict():
    """extras.json is what extras.py reads off the ledger and the records, and says what the
    plan quotes from it."""
    verdict = _verdict()
    kept = json.loads((LAB / "extras.json").read_text())
    chosen = STUDY.worlds()
    again = EXTRAS.summary(verdict, chosen)
    for part in again:
        assert kept[part] == json.loads(json.dumps(again[part])), part
    rows = [json.loads(line) for line in (LAB / "records.jsonl").read_text().splitlines()]
    plan, lent = STUDY.design(), STUDY.looks_rule()
    more = kept["one more number"]["worlds"]
    assert more == EXTRAS.one_more_number(rows, plan, chosen, lent) and len(more) == 30
    beside = kept["the yardstick"]["worlds"]
    assert beside == EXTRAS.with_endless_data(rows, plan, chosen, lent)
    # what marks the worlds: how full a world is, less than how its blocks change hands
    ranks = {name: found["rank correlation"] for name, found in kept["rank correlations"].items()}
    assert ranks[f"{EXTRAS.FULL}, against {EXTRAS.MISSED}"] == -0.819
    assert ranks[f"{EXTRAS.FLICKER}, against {EXTRAS.MISSED}"] == 0.92
    assert ranks[f"{EXTRAS.YOUNG}, against {EXTRAS.MISSED}"] == -0.944
    apart = kept["do they tell served from missed"]
    assert apart[EXTRAS.FLICKER]["range by group"] == {
        SERVED: [0.0016, 0.0091], NEAR: [0.0006, 0.0122], JUST: [0.0205, 0.0267],
        FAR: [0.0484, 0.1701]}  # fmt: skip

    # one more number: how many worlds each family brings within the study's bar, and 4%
    def within(family, bar):
        return sum(found[family]["more surprise"] <= bar for world, found in more.items()
                   if world != STILL)  # fmt: skip

    assert sum(found["the look's rule as it is"] <= 0.025 for world, found in more.items()
               if world != STILL) == 10  # fmt: skip
    assert [within(family, 0.025) for family in (EXTRAS.TAKEN, EXTRAS.NEIGHBOUR, EXTRAS.BOTH)] == [
        18, 12, 20]  # fmt: skip
    assert within(EXTRAS.BOTH, 0.04) == 25
    assert more[STILL][EXTRAS.BOTH]["fitted"] == [1.0, 0.0]
    just = [found[EXTRAS.TAKEN]["fitted"][0] for found in more.values() if found["group"] == JUST]
    assert min(just) == 1.9 and max(just) == 2.0
    # the yardstick: with a world's own rule told as with endless data, thirteen served
    served = kept["the yardstick"]
    assert served["served, as registered"][HOW][NEAR] == [4, 4]
    assert served["served, beside its own with endless data"][HOW][NEAR] == [3, 4]
    assert served["served, beside its own with endless data"][PLAIN][NEAR] == [0, 4]
    assert beside[STILL][HOW] == {"as registered": -0.0158,
                                  "beside its own with endless data": -0.0078}  # fmt: skip
    # and who held a block for most of a tick, in the sizing's worlds
    held = json.loads((LAB / "held.json").read_text())["worlds"]
    flat = "an old lead beside a flat wall changes hands"
    assert len(held) == 12 and held["B25/S078"][HELD.AT][flat] == 0.1843
    assert held["B25/S078"][HELD.MOST][flat] == 0.1449


# --- read after the verdict (exploratory) --------------------------------------------------------

EXTRAS = _load("scale_up_class_memory_extras", LAB / "extras.py")


def test_one_more_number_on_made_up_tallies():
    around = EXTRAS.neighbours()
    assert around.shape == (3, 9, 9, 3)
    # three neighbours under species 1 and five under species 2: nobody, 3/8, 5/8
    assert np.allclose(around[1, 3, 5], [0, 3 / 8, 5 / 8]) and np.allclose(around[0], around[2])
    assert np.allclose(around[2, 2, 2], [4 / 8, 2 / 8, 2 / 8])
    views = np.add.outer(np.arange(9), np.arange(9)) <= 8
    assert np.allclose(around.sum(axis=-1)[1][views], 1) and not around[1][~views].any()
    # a rule taken once is itself; taken twice, a block keeps its leader with the square of
    # the chance, and what is left goes where it went before
    rng = np.random.default_rng(7)
    base = rng.random((3, 9, 9, 3)) + 0.05
    base /= base.sum(axis=-1, keepdims=True)
    assert np.allclose(EXTRAS.taken(base, 1.0), base)
    twice = EXTRAS.taken(base, 2.0)
    assert np.allclose(twice.sum(axis=-1), 1) and np.allclose(
        twice[1, :, :, 1], base[1, :, :, 1] ** 2
    )
    assert np.allclose(twice[1, :, :, 0] / twice[1, :, :, 2], base[1, :, :, 0] / base[1, :, :, 2])
    # the bits of a tally under a table
    tally = np.zeros((3, 9, 9, 3))
    tally[1, 4, 4] = [0, 30, 10]
    table = np.full((3, 9, 9, 3), 1 / 3)
    table[1, 4, 4] = [0.0, 0.5, 0.5]
    assert EXTRAS.bits(table, tally) == pytest.approx(1.0)
    # a made-up world that is the look's rule with a chance of 0.2 of taking a neighbour's
    # leader: the fit finds the 0.2, and with it the look's rule is the world's own
    lent = np.zeros((16, 3, 9, 9, 3), dtype=np.int64)
    goes = (0, 1000, 3000, 10000, 100000, 250000, 500000, 800000, 950000)  # in a million
    for near in range(9):  # a block seldom changes hands until rivals are half its neighbours
        stays = 1000000 - goes[near]
        lent[0, 1, 8 - near, near] = [0, stays, goes[near]]
        lent[0, 2, near, 8 - near] = [0, goes[near], stays]
    rule = STUDY.look.PLAIN.chances(STUDY.look.PLAIN.of(lent))[0]
    mixed = 0.8 * rule + 0.2 * around
    seen = np.zeros((16, 3, 9, 9, 3), dtype=np.int64)
    for near in range(9):
        seen[0, 1, 8 - near, near] = np.round(400000 * mixed[1, 8 - near, near])
        seen[0, 2, near, 8 - near] = np.round(400000 * mixed[2, near, 8 - near])
    rows = _records("rough", {1: seen, 2: seen}) + _records("smooth", {1: lent, 2: lent})
    plan = {w: {"learn": [1], "try": [2]} for w in ("rough", "smooth")}
    chosen = {w: {"group": FAR} for w in plan}
    found = EXTRAS.one_more_number(rows, plan, chosen, lent)
    rough, smooth = found["rough"], found["smooth"]
    assert rough["the look's rule as it is"] > 0.05
    assert rough[EXTRAS.NEIGHBOUR]["fitted"] == [0.2]
    assert rough[EXTRAS.NEIGHBOUR]["more surprise"] == pytest.approx(0.0, abs=1e-4)
    assert rough[EXTRAS.TAKEN]["more surprise"] > rough[EXTRAS.NEIGHBOUR]["more surprise"] + 0.001
    assert rough[EXTRAS.BOTH]["fitted"] == [1.0, 0.2]
    assert smooth[EXTRAS.NEIGHBOUR]["fitted"] == [0.0] and smooth[EXTRAS.TAKEN]["fitted"] == [1.0]
    assert smooth["the look's rule as it is"] == pytest.approx(0.0, abs=1e-4)
    # a world with no tallies is left out
    assert EXTRAS.one_more_number(_records("slow", {}, reach=1400), {
        "slow": {"learn": [1], "try": [2]}}, {"slow": {"group": FAR}}, lent) == {}  # fmt: skip


def test_what_marks_a_world_on_made_up_verdicts():
    def told(group, live, old, young, removed, gain):
        return {"tick": 16, "stands": True, "group": group, "live at generation 4,096": live,
                EXTRAS.TABLE: {EXTRAS.OLD: [old, 0.05, 0.2], EXTRAS.NEW: [0.1, young, 0.5]},
                "share of the plain rule's surprise that how long removes": removed,
                "the look's rule, more surprise": {PLAIN: 0.01, HOW: 0.0},
                "blocks amiss, the look's remembering rule over its plain one": gain}  # fmt: skip

    verdict = {"worlds": {
        STILL: told("the still world", 0.98, 0.004, 0.32, 0.086, 0.73),
        "a": told(SERVED, 0.6, 0.004, 0.35, 0.10, 0.75),
        "b": told(SERVED, 0.9, 0.006, 0.30, 0.08, 0.80),
        "c": told(FAR, 0.7, 0.10, 0.10, 0.01, 1.0),
        "d": told(FAR, 0.3, 0.20, 0.06, 0.00, 1.02),
        "e": {"tick": None, "stands": False},
    }}  # fmt: skip
    missed = (0.002, 0.004, 0.2, 0.3, 0.1)
    chosen = {w: {STUDY.MISSED: m} for w, m in zip("abcde", missed, strict=True)}
    found = EXTRAS.summary(verdict, chosen)
    assert set(found["worlds"]) == set("abcd") and found["the still world"][EXTRAS.FULL] == 0.98
    assert (
        found["worlds"]["a"][EXTRAS.YOUNG] == 7.0 and found["worlds"]["d"][EXTRAS.FLICKER] == 0.20
    )
    apart = found["do they tell served from missed"]
    # how full a world is does not tell these four apart (0.6 and 0.9 against 0.7 and 0.3)
    assert apart[EXTRAS.FULL]["served and missed stand clear"] is False
    assert apart[EXTRAS.FLICKER]["served and missed stand clear"] is True
    assert apart[EXTRAS.FLICKER]["range by group"][FAR] == [0.10, 0.20]
    ranks = found["rank correlations"]
    assert ranks[f"{EXTRAS.FLICKER}, against {EXTRAS.MISSED}"] == {
        "worlds": 4, "rank correlation": 1.0}  # fmt: skip
    assert ranks[f"{EXTRAS.FLICKER}, against {EXTRAS.REMOVED}"]["rank correlation"] == -1.0


HELD = _load("scale_up_class_memory_held", LAB / "held.py")


def test_who_held_a_block_for_most_of_a_tick():
    tick = 8  # four readings to a tick
    leaders = np.zeros((64 * 4 + 1, 1, 3), dtype=np.int8)
    leaders[:, 0, 0] = 1  # the first block is species 1's throughout
    for reading in range(1, leaders.shape[0]):
        # the second is species 2's for three readings of four, and 1's at the tick's end;
        # the third is each one's for two of the four
        leaders[reading, 0, 1] = (2, 2, 2, 1)[(reading - 1) % 4]
        leaders[reading, 0, 2] = (1, 1, 2, 2)[(reading - 1) % 4]
    at, most = HELD.instant(leaders, tick), HELD.held_most(leaders, tick)
    assert at.shape == most.shape == (65, 1, 3) and np.array_equal(most[0], leaders[0])
    assert (most[:, 0, 0] == 1).all() and (at[:, 0, 0] == 1).all()
    # read at an instant the second block is species 1's; it was 2's for most of every tick
    assert (at[1:, 0, 1] == 1).all() and (most[1:, 0, 1] == 2).all()
    assert (most[1:, 0, 2] == 2).all()  # a tie goes to whoever leads at the end of the tick
