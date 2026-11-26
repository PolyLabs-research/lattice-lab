"""The registered test of worlds of territories, zoomed out
(examples/scale-up-closure-territories/study.py) and the measures it shares with its sizing
look (ladder.py): on made-up worlds whose answer is known, against the first look's own code,
and end to end on worlds small enough to run here.
"""

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

from lattice_lab.ledger import canonical

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
STUDY = _load("scale_up_closure_territories_study", LAB / "study.py")
LADDER = STUDY.ladder
ZOOM = LADDER.zoom


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


def _pairs(frames: np.ndarray, tick: int, first: int, last: int):
    """The transitions `ladder.tally` reads from frames kept every generation."""
    at = np.array(LADDER.instants(1, tick, first, last))
    return frames[at], frames[at + tick]


# --- clocks, ticks and windows -------------------------------------------------------------------


def test_the_clocks_the_ticks_and_the_windows():
    assert [LADDER.square(b) for b in LADDER.BLOCKS] == [4, 16, 64, 256]
    for block, ticks in LADDER.TICKS.items():
        assert block in ticks and LADDER.square(block) in ticks
        assert all(tick % block == 0 for tick in ticks)  # a tick is read where the block is
    # the windows follow one another, and a rule is run on over the last
    spans = list(LADDER.WINDOWS.values())
    assert all(a[1] == b[0] for a, b in zip(spans, spans[1:], strict=False))
    assert spans[0][0] == 64 and spans[-1][1] == LADDER.GENERATIONS and LADDER.FROM == 1024
    assert LADDER.EARLY + LADDER.LATE == LADDER.WHOLE == tuple(LADDER.WINDOWS)
    # no transition reaches past its window, at any block and tick
    for block, ticks in LADDER.TICKS.items():
        for tick in ticks:
            for first, last in spans:
                at = LADDER.instants(block, tick, first, last)
                assert all(first <= t and t + tick <= last and t % block == 0 for t in at)
    # at matched ages blocks of 4 and of 8 give as many transitions, blocks of 16 a quarter
    seen = {block: len(LADDER.instants(block, LADDER.square(block), *LADDER.WINDOWS[name]))
            * (LADDER.SIDE // block) ** 2 for block, (name,) in LADDER.MATCHED.items()}  # fmt: skip
    assert seen[4] == seen[8] == 4 * seen[16] == 786432


# --- tallies, and rules from them ----------------------------------------------------------------


def test_a_tally_is_the_instruments_table():
    world = _voters(0.5, 70, 9001)
    counts = LADDER.tally(world, 1, 2, 3, 70)
    own, after = _pairs(world, 2, 3, 70)
    assert own.shape[0] == 5  # every sixteen generations from the third
    table = ZOOM.CoarseRule.empty(3).learn(np.stack([own[0], after[0]])).tables["total"]
    for a, b in zip(own[1:], after[1:], strict=True):
        table = table.plus(ZOOM.CoarseRule.empty(3).learn(np.stack([a, b])).tables["total"])
    dense = np.zeros((243, 3), dtype=np.int64)
    dense[table.rows] = table.counts
    assert np.array_equal(counts, dense.reshape(3, 9, 9, 3)) and counts.sum() == 5 * 48 * 48
    # no block has more than eight neighbours, and written down and read back it is the same
    n1, n2 = np.indices((9, 9))
    assert counts[:, n1 + n2 > 8].sum() == 0
    rows = LADDER.sparse(counts)
    assert json.loads(json.dumps(rows)) == rows and len(rows) < 243
    assert np.array_equal(LADDER.dense(rows), counts)
    assert LADDER.dense([]).sum() == 0
    # changing hands, read off the tally, is what the first look counts from the grids
    assert np.array_equal(LADDER.hands(counts), LOOK.hands(own, after))


def test_changing_hands_by_how_many_neighbours_the_rival_leads():
    world = _voters(0.8, 400, 9002)
    counts = LADDER.tally(world, 1, 1, 0, 400)
    found = LADDER.hands(counts)
    assert found[0, 1] == 0  # no rival around: no change, by the made-up rule
    for near in range(1, 8):
        if found[near, 0] > 2000:
            assert abs(LADDER.changes(counts, near) - 0.8 * near / 8) < 0.04, near
    assert LADDER.changes(np.zeros((3, 9, 9, 3)), 5) is None


def test_a_rule_from_a_tally_is_the_instruments_rule():
    world = _voters(0.4, 200, 9003)
    counts = LADDER.tally(world, 1, 1, 0, 200)
    rule = LADDER.rule_of(counts)
    grid = _voters(0.4, 3, 9004)[-1]
    grid[0, :5] = 0  # some blocks nobody leads
    around = ZOOM.ring(grid)
    n1, n2 = (around == 1).sum(axis=0), (around == 2).sum(axis=0)
    for kind in ("nothing", "own", "total"):
        theirs = rule.chances(kind, grid, around)
        ours = LADDER.chances(counts, kind)[grid, n1, n2]
        assert np.allclose(theirs, ours, rtol=0, atol=1e-15), kind
        assert np.allclose(LADDER.chances(counts, kind).sum(axis=-1), 1)
    with pytest.raises(ValueError):
        LADDER.chances(counts, "full")
    # and it scores another run as the instrument does
    other = _voters(0.4, 60, 9005)
    trial = LADDER.tally(other, 1, 1, 0, 60)
    own, after = _pairs(other, 1, 0, 60)
    for kind in ("nothing", "own", "total"):
        theirs, ours = LOOK.score(rule, kind, own, after), LADDER.score(counts, trial, kind)
        assert theirs["transitions"] == ours["transitions"] == 4 * 48 * 48
        assert theirs["right"] == ours["right"] and math.isclose(theirs["bits"], ours["bits"])
    # drawn from, it steps as the instrument's rule does
    learned = ZOOM.CoarseRule.empty(3)
    for a, b in zip(*_pairs(world, 1, 0, 200), strict=True):
        learned = learned.learn(np.stack([a, b]))
    assert np.array_equal(rule.step("total", grid, np.random.default_rng(5)),
                          learned.step("total", grid, np.random.default_rng(5)))  # fmt: skip


def test_a_rule_from_elsewhere_serves_or_does_not():
    def counts(pull, seed, steps=600):
        return LADDER.tally(_voters(pull, steps, seed), 1, 1, 0, steps)

    trial = counts(0.4, 9010)
    same = LADDER.excess(counts(0.4, 9011), counts(0.4, 9012), trial)
    slower = LADDER.excess(counts(0.2, 9011), counts(0.4, 9012), trial)
    faster = LADDER.excess(counts(0.8, 9011), counts(0.4, 9012), trial)
    assert abs(same) < 0.01 and slower > 0.03 and faster > 0.1
    assert LADDER.excess(trial, trial, trial) == 0
    assert math.isnan(LADDER.excess(trial, trial, np.zeros_like(trial)))
    # the neighbours tell: the block alone has more surprise than the block with its counts
    assert LADDER.surprise(trial, trial, "total") < LADDER.surprise(trial, trial, "own")


def test_a_rule_scaled_down_to_as_much_data():
    large = LADDER.tally(_voters(0.4, 600, 9020), 1, 1, 0, 600)
    small = LADDER.tally(_voters(0.4, 60, 9021), 1, 1, 0, 60)
    scaled = LADDER.as_much(large, small)
    assert math.isclose(scaled.sum(), small.sum()) and scaled.dtype == float
    assert np.allclose(scaled * large.sum(), large * small.sum())  # the same shares
    assert np.array_equal(LADDER.as_much(small, large), small)  # never scaled up
    # a rule that has learned from less leans more on the coarser view: a block of species 1
    # with all eight neighbours its own never changes hands in the made-up world, but a block
    # of species 1 at large does about one time in eight
    view, stays = (1, 8, 0), 1
    fine = LADDER.chances(large)[view][stays]
    coarse = LADDER.chances(large, "own")[1, 0, 0][stays]
    thin = LADDER.chances(large * 1e-4)[view][stays]
    assert fine > 0.999 and 0.8 < coarse < 0.95
    assert coarse < thin < fine and thin - coarse < fine - thin
    # and one that has learned from nothing gives every next leader the same chance
    assert np.allclose(LADDER.chances(large * 0), 1 / 3)


# --- a rule run on by itself ---------------------------------------------------------------------


def test_a_rule_run_on_by_itself():
    world = _voters(0.3, 72, 9030)
    stay = np.zeros((3, 9, 9, 3), dtype=np.int64)
    for leader in (1, 2):
        stay[leader, :, :, leader] = 10**9  # a rule under which nothing changes hands
    found = LADDER.ahead(world, stay, 1, 2, (1, 2, 3), first=8, generations=72)
    assert found["generations_on"] == [2, 4, 8, 16, 32, 64] and found["from_generation"] == 8
    assert found["block"] == 1 and found["tick"] == 2 and len(found["rule_sha256"]) == 64
    # its world is the start: as far from the real world as the start is, with the start's walls
    assert found["apart_rule"] == found["apart_start"] and set(found["apart_twin"]) == {0.0}
    assert set(found["walls_rule"]) == {round(LADDER.walls(world[8]), 6)}
    assert found["walls_world"][-1] == round(LADDER.walls(world[72]), 6)
    assert found["apart_start"][-1] == round(float((world[8] != world[72]).mean()), 6)
    # the world's own rule: two runs part company, and the same draws give the same run
    own = LADDER.tally(world, 1, 2, 0, 72)
    first = LADDER.ahead(world, own, 1, 2, (1, 2, 3), first=8, generations=72)
    assert first == LADDER.ahead(world, own, 1, 2, (1, 2, 3), first=8, generations=72)
    assert first != LADDER.ahead(world, own, 1, 2, (1, 2, 4), first=8, generations=72)
    assert first["apart_twin"][0] > 0 and first["rule_sha256"] != found["rule_sha256"]
    assert json.loads(json.dumps(first)) == first


def test_the_walls_between_leaders():
    halves = np.ones((4, 8), dtype=np.int8)
    halves[:, 4:] = 2
    assert LADDER.walls(halves) == (2 / 8 + 0) / 2
    assert LADDER.walls(np.ones((4, 4), dtype=np.int8)) == 0
    assert LADDER.walls(halves) == LOOK.walls(halves)


# --- the claims ----------------------------------------------------------------------------------


def test_the_claims_the_study_registers():
    claims = STUDY.claims()
    labels = [c["label"] for c in claims]
    assert len(labels) == len(set(labels)) == 89
    by_family = {f: sum(c["family"] == f for c in claims) for f in "NTRXBCUZ"}
    assert by_family == {"N": 6, "T": 6, "R": 14, "X": 4, "B": 10, "C": 27, "U": 18, "Z": 4}
    for c in claims:
        assert c["at_least"] is not None or c["at_most"] is not None, c["label"]
        assert c["world"] in STUDY.WORLDS and c["claim"] and c["quantity"]
        # what a claim stands on: its world keeping on growing, or, for the control, set;
        # and, where a rule is run on, a block small beside the territories
        needs = c["needs"]
        assert needs["world"] == c["world"]
        assert (needs["state"] == "has set") == (c["family"] == "Z"), c["label"]
        run_on = c["quantity"].startswith(("amiss", "walls kept")) and c["family"] != "Z"
        assert needs["block"] == (c["block"] if run_on else None), c["label"]
        assert json.loads(json.dumps(c)) == c
    # the three worlds never zoomed out are claimed of alike, and only in families C and U
    for world in STUDY.UNSEEN:
        mine = [c for c in claims if c["world"] == world]
        assert {c["family"] for c in mine} == {"C", "U"} and len(mine) == 9
    assert STUDY.predictions() == claims
    # the claims of the first look's two worlds alone are what the sizing look works out
    two = STUDY.claims({w: STUDY.WORLDS[w] for w in STUDY.SEEN})
    assert {c["family"] for c in two} == set("NTRXBC") and len(two) == 58


def test_the_design():
    plan = STUDY.design()
    assert set(plan) == set(STUDY.WORLDS) == {*STUDY.SEEN, *STUDY.UNSEEN, STUDY.CONTROL}
    seeds = [s for w in plan.values() for s in w["learn"] + w["try"]]
    assert len(seeds) == len(set(seeds)) == 44 and min(seeds) == 16001  # no start is shared
    assert all(len(w["learn"]) == len(w["try"]) for w in plan.values())
    jobs = STUDY.start_jobs()
    assert sorted(jobs) == sorted((name, s) for name, w in plan.items()
                                  for s in w["learn"] + w["try"])  # fmt: skip
    assert [name for name, _ in jobs[:6]] == list(STUDY.WORLDS)  # the worlds take turns
    # the first look's worlds are run on with their own rule at every block, the others at 8
    # and 16; and the still world's rule is run on everywhere but in the still world
    runs = STUDY.RUN_ON
    assert (STUDY.OWN, 4, 4) in runs["still"] and (STUDY.OWN, 32, 256) in runs["busy"]
    assert (STUDY.OWN, 8, 8) in runs["still"] and (STUDY.OWN, 8, 8) not in runs["near"]
    for world in ("busy", *STUDY.UNSEEN, STUDY.CONTROL):
        assert {(STUDY.STILLS, 8, 16), (STUDY.STILLS, 16, 64)} <= set(runs[world])
    assert all(whose == STUDY.OWN for whose, _, _ in runs["still"])
    assert all(whose == STUDY.STILLS for whose, _, _ in runs[STUDY.CONTROL])


def test_the_judge():
    claim = {"at_least": 0.2, "at_most": 0.5}
    assert STUDY.judge(0.3, claim, True) == "holds"
    assert STUDY.judge(0.2, claim, True) == STUDY.judge(0.5, claim, True) == "holds"
    assert STUDY.judge(0.19, claim, True) == STUDY.judge(0.51, claim, True) == "fails"
    # nothing to stand on, or no number: not tested, never failed
    assert STUDY.judge(0.9, claim, False) == STUDY.judge(0.3, claim, False) == "not tested"
    assert STUDY.judge(None, claim, True) == STUDY.judge(float("nan"), claim, True) == "not tested"
    assert STUDY.judge(float("inf"), claim, True) == "not tested"
    assert STUDY.judge(-5.0, {"at_least": None, "at_most": 0.0}, True) == "holds"
    assert STUDY.judge(0.01, {"at_least": 0.05, "at_most": None}, True) == "fails"


def _made_up(walls: dict, moved: float, world: str = "near") -> "STUDY.Measures":
    """Records that say only what a claim stands on: a world's walls at each block at the
    generation a rule is run on from and at the last, and the share of blocks of 16 that
    changed leader meanwhile."""
    plan = {world: {"learn": [1], "try": [2]}}
    kept = {str(b): {"1024": at, "4096": end} for b, (at, end) in walls.items()}
    start = {"kind": "start", "world": world, "seed": 2, "walls": kept}
    whose = STUDY.STILLS if world == STUDY.CONTROL else STUDY.OWN
    ahead = {"kind": "ahead", "world": world, "seed": 2, "rule": whose, "block": 16, "tick": 64,
             "apart_start": [moved]}  # fmt: skip
    return STUDY.Measures([start, ahead], plan, {})


def test_what_a_claim_stands_on():
    grows = _made_up({8: (0.09, 0.05), 16: (0.18, 0.09), 32: (0.32, 0.18)}, 0.21)
    assert grows.coarsens("near") and not grows.has_set("near")
    assert grows.fits("near", 8) and grows.fits("near", 16) and not grows.fits("near", 32)
    where = {"needs": {"world": "near", "state": "keeps growing", "block": 16}}
    assert grows.stands(where) and not grows.stands({"needs": {**where["needs"], "block": 32}})
    assert grows.stands({"needs": {**where["needs"], "block": None}})
    assert not grows.stands({"needs": {**where["needs"], "state": "has set"}})
    # walls that fall by under a fifth, or too few blocks changing leader: not growing
    assert not _made_up({16: (0.18, 0.15)}, 0.21).coarsens("near")
    assert not _made_up({16: (0.18, 0.09)}, 0.04).coarsens("near")
    assert _made_up({16: (0.18, 0.144)}, 0.05).coarsens("near")
    # the control has set: its walls where they were, and next to no block with a new leader
    still = _made_up({8: (0.26, 0.26), 16: (0.39, 0.388)}, 0.001, STUDY.CONTROL)
    assert still.has_set(STUDY.CONTROL) and not still.coarsens(STUDY.CONTROL)
    assert still.stands({"needs": {"world": STUDY.CONTROL, "state": "has set", "block": None}})
    # its territories are small, but a claim about the control does not ask that a block fit
    assert not still.fits(STUDY.CONTROL, 8)
    assert all(c["needs"]["block"] is None for c in STUDY.claims() if c["family"] == "Z")
    assert not _made_up({16: (0.39, 0.36)}, 0.001, STUDY.CONTROL).has_set(STUDY.CONTROL)
    assert not _made_up({16: (0.39, 0.39)}, 0.03, STUDY.CONTROL).has_set(STUDY.CONTROL)
    # a world with no record of it stands on nothing
    assert not grows.coarsens("another") and not grows.fits("another", 8)


# --- end to end, on worlds small enough to run here ----------------------------------------------


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Every world on a grid of side 64 for 1,024 generations, from two starts each."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(LADDER, "SIDE", 64)
    monkeypatch.setattr(LADDER, "GENERATIONS", 1024)
    monkeypatch.setattr(LADDER, "WINDOWS", {"A": (64, 128), "B": (128, 256), "C": (256, 1024)})
    monkeypatch.setattr(LADDER, "FROM", 256)
    worlds = {name: {**w, "first": 9100 + 10 * i, "starts": 2}
              for i, (name, w) in enumerate(STUDY.WORLDS.items())}  # fmt: skip
    monkeypatch.setattr(STUDY, "WORLDS", worlds)
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    # reference rules from two more small runs of the first look's worlds
    rules = {}
    for name in STUDY.SEEN:
        w = worlds[name]
        found = LADDER.fine(f"reference-{name}", w["rule"], w["density"], 9190, 64, 1024)
        tallies = LADDER.tallies(found, 1024)
        rules[name] = {where: LADDER.sparse(sum(LADDER.dense(rows) for rows in by.values()))
                       for where, by in tallies.items()}  # fmt: skip
    kept = tmp_path / "reference.json"
    kept.write_text(json.dumps({"rules": rules}))
    monkeypatch.setattr(STUDY, "REFERENCE", kept)
    return tmp_path


def test_one_fine_run_on_record(small):
    record = STUDY.run_start(("busy", 9110))
    assert record == STUDY.run_start(("busy", 9110))  # the second time from the leaders kept
    assert (small / "cache" / "registered-busy-64-1024-9110.npz").exists()
    assert record["kind"] == "start" and record["world"] == "busy" and record["seed"] == 9110
    assert (record["side"], record["generations"]) == (64, 1024)
    assert json.loads(canonical(record)) == record
    assert set(record["live"]) == set(record["larger"]) == {"64", "128", "256", "1024"}
    assert 0.5 < record["live"]["1024"] < 0.9 and record["larger"]["64"] <= record["live"]["64"]
    assert set(record["walls"]) == {"4", "8", "16", "32"}
    assert set(record["tally"]) == {LADDER.key(b, t) for b in LADDER.BLOCKS
                                    for t in LADDER.TICKS[b]}  # fmt: skip
    for where, by_window in record["tally"].items():
        block, tick = map(int, where.split())
        assert set(by_window) == {"A", "B", "C"}
        for name, rows in by_window.items():
            seen = len(LADDER.instants(block, tick, *LADDER.WINDOWS[name])) * (64 // block) ** 2
            assert LADDER.dense(rows).sum() == seen, (where, name)
    # the leaders kept are the first look's reading of the same cells: who has more of a block
    kept = LADDER.fine("busy", "B23467/S4568", 1.0, 9110, 64, 1024)
    assert kept[4].shape == (257, 16, 16) and set(np.unique(kept[4])) <= {0, 1, 2}
    assert kept["shares"].shape == (16, 2)
    # a half-full start is half full, a full one full
    sparse = LADDER.fine("sparse", "B2/S0", 0.5, 9140, 64, 64)
    full = LADDER.fine("still", "B245678/S3678", 1.0, 9100, 64, 64)
    assert (full[4][0] == 0).mean() < 0.3 and sparse["shares"][-1].sum() < 0.5


def test_the_study_end_to_end_on_small_worlds(small):
    path = STUDY.RECORDS
    STUDY.execute(path, 1)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    plan = STUDY.design()
    starts = [r for r in rows if r["kind"] == "start"]
    ahead = [r for r in rows if r["kind"] == "ahead"]
    assert len(starts) == 12 and len(ahead) == sum(len(r) for r in STUDY.RUN_ON.values())
    assert all(r["seed"] in plan[r["world"]]["try"] for r in ahead)
    assert {r["rule"] for r in ahead} == {STUDY.OWN, STUDY.STILLS}
    # run again, it finds everything done
    STUDY.execute(path, 1)
    assert len(path.read_text().splitlines()) == len(rows)
    # every record comes out the same computed again
    for record in (starts[0], starts[-1], ahead[0], ahead[-1]):
        assert canonical(STUDY.rerun(record)) == canonical(record)
    with pytest.raises(ValueError):
        STUDY.rerun({**ahead[0], "block": 32, "tick": 32})
    # the verdict: every claim judged, none missing, every number worked out
    claims = STUDY.claims()
    found = STUDY.decide(rows, claims)
    assert found["missing"] == [] and set(found["outcomes"]) == {c["label"] for c in claims}
    assert set(found["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert set(found["verdict"]) == set("NTRXBCUZ")
    assert json.loads(json.dumps(found)) == found
    for c in claims:
        value = found["measured"][c["label"]]["value"]
        assert value is None or math.isfinite(value), c["label"]
        if c["quantity"] == "rule from elsewhere, best tick":
            assert found["measured"][c["label"]]["tick"] in LADDER.TICKS[c["block"]]
    # a claim is not tested where it has nothing to stand on
    for world, told in found["worlds"].items():
        state = "has set" if world == STUDY.CONTROL else "keeps growing"
        for c in claims:
            if c["needs"]["world"] != world:
                continue
            stands = told[state] and (c["needs"]["block"] is None or c["needs"]["block"]
                                      in told["blocks small beside its territories"])  # fmt: skip
            assert (found["outcomes"][c["label"]] == "not tested") >= (not stands), c["label"]
        assert set(told["changes hands"]) == set(starts[0]["tally"])
        assert len(told["walls"]["16"]) == 2
    # the same numbers from the measures directly
    m = STUDY.Measures(rows, plan, STUDY.reference())
    x = next(c for c in claims if c["label"] == "X still, block 8")
    assert found["measured"][x["label"]]["value"] == STUDY.number(m.value(x))
    assert STUDY.number(float("nan")) is None and STUDY.number(None) is None
    assert STUDY.number(0.1234567) == 0.12346 and STUDY.over(1.0, 0.0) is None
    assert STUDY.over(1.0, 4.0) == 0.25 and STUDY.over(None, 4.0) is None
    assert STUDY.over(1.0, -4.0) is None and STUDY.over(float("nan"), 1.0) is None
    assert m.from_elsewhere("still", "still", 8) == m.from_elsewhere("still", "still", 8, 16)
    best, tick = m.best_tick("near", "still", 8)
    assert best == min(m.from_elsewhere("near", "still", 8, t) for t in LADDER.TICKS[8])
    # a run with a record missing says so, and judges nothing
    short = STUDY.decide(rows[:-1], claims)
    assert short["missing"] and set(short["outcomes"].values()) == {"missing"}
    assert set(short["verdict"].values()) == {"missing"}


# --- what was written down before the run --------------------------------------------------------


def test_the_bounds_were_drawn_outside_what_the_first_look_gave():
    """Every number the sizing look worked out, whichever way the first look's starts were
    dealt, lies inside the bound the claim carries: with room to spare for the claims that
    are a share or a ratio."""
    sizing = json.loads((LAB / "sizing.json").read_text())
    two = {c["label"]: c for c in STUDY.claims({w: STUDY.WORLDS[w] for w in STUDY.SEEN})}
    drawn = sizing["what the bounds were drawn from"]
    assert set(drawn) == set(two) and len(sizing["splits"]) == 6 and len(sizing["fresh"]) == 2
    for label, row in drawn.items():
        claim = two[label]
        assert row["bound"] == {"at_least": claim["at_least"], "at_most": claim["at_most"]}
        both = (row["the first look's starts dealt six ways"]
                + row["a rule from four starts, fresh rules from two"])  # fmt: skip
        values = [v for v in both if v is not None]
        assert len(values) == 8, label
        for v in values:
            assert STUDY.judge(v, claim, True) == "holds", (label, v)
    # the first look's own split gives the numbers the plan quotes of it
    first = {
        label: row["the first look's starts dealt six ways"][0] for label, row in drawn.items()
    }
    assert 0.44 < first["N still, block 4: the neighbours"] < 0.445
    assert 0.002 < first["T still, block 4"] < 0.003
    assert first["B the still world's rule in the busy world, block 8"] < 0.005
    assert first["X still, block 8"] == 0  # there the rule from elsewhere is the rule itself
    # the control: its leaders stop changing, the still world's rule is far off as it is, and
    # at its shortest tick it comes within a twentieth at blocks of 16
    control = sizing["the control"]
    assert control["side"] == 512 and control["starts"] == [15101, 15102]
    for block, told in control["blocks"].items():
        by_tick = told["the still world's rule, by tick"]
        assert by_tick[str(LADDER.square(int(block)))] > STUDY.FAR_OFF
        assert min(by_tick, key=by_tick.get) == block  # the shortest tick serves best
        assert told["run on: changed meanwhile"] < 0.002
        assert told["run on: amiss at the end"] - told["run on: changed meanwhile"] > STUDY.FURTHER
    assert control["blocks"]["16"]["the still world's rule, by tick"]["16"] < 0.05
    assert abs(control["walls"]["16"]["4096"] / control["walls"]["16"]["1024"] - 1) < 0.01


def test_the_reference_rules_are_the_first_looks():
    kept = STUDY.reference()
    assert set(kept) == set(STUDY.SEEN)
    wanted = {LADDER.key(b, t) for b in LADDER.BLOCKS for t in LADDER.TICKS[b]}
    for world, rules in kept.items():
        assert set(rules) == wanted
        for where, counts in rules.items():
            block, tick = map(int, where.split())
            # all eight of the first look's runs, over all three windows
            seen = sum(len(LADDER.instants(block, tick, *span)) for span in LADDER.WINDOWS.values())
            assert counts.sum() == 8 * seen * (LADDER.SIDE // block) ** 2, (world, where)
    # a block changes hands by being surrounded, in both, with the chances the first look gave
    for world in STUDY.SEEN:
        counts = kept[world][LADDER.key(4, 4)]
        assert LADDER.changes(counts, 0) < 0.0001 and 0.36 < LADDER.changes(counts, 5) < 0.38


def test_the_registration():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    question = entries[0]["body"]
    registered = [e["body"] for e in entries if e["kind"] == "prediction"]
    assert entries[0]["kind"] == "question" and len(registered) == 89
    assert [e["kind"] for e in entries[1:90]] == ["prediction"] * 89
    # the claims in the ledger are the claims the code makes, and the files are the files
    claims = STUDY.claims()
    for body, claim in zip(registered, claims, strict=True):
        assert {k: body[k] for k in claim} == claim
    for name, digest in question["sha256"].items():
        assert STUDY.sha(LAB / name) == digest, name
    assert question["runs"] == 44 + 108 and question["side"] == 1024
    assert set(question["worlds"]) == set(STUDY.WORLDS)
    unseen = {w for w, told in question["worlds"].items() if not told["seen_zoomed_out"]}
    assert unseen == set(STUDY.UNSEEN)
    assert question["worlds"]["sparse"]["density"] == 0.5
    assert len(question["excluded_seen"]) == 4
    verdicts = [e["body"] for e in entries if e["kind"] == "verdict"]
    if verdicts:  # run: nothing missing, and every claim judged one of three ways
        assert verdicts[0]["missing"] == []
        assert set(verdicts[0]["outcomes"].values()) <= {"holds", "fails", "not tested"}
