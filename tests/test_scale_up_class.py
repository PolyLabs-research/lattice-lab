"""The registered test of how wide the class is (examples/scale-up-class/study.py): how its
worlds are chosen, its measures on made-up records whose answer is known, and the whole of it
end to end on worlds small enough to run here.
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
LAB = ROOT / "examples" / "scale-up-class"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


STUDY = _load("scale_up_class_study", LAB / "study.py")
LADDER = STUDY.ladder
STILL = STUDY.STILL


# --- the worlds ----------------------------------------------------------------------------------


def test_the_worlds_are_chosen_from_step_4cs_records():
    chosen = STUDY.select()
    assert len(chosen) == 38 and len({w["rule"] for w in chosen}) == 38
    bands = [w["band"] for w in chosen]
    wanted = {"fills": 11, "0.0 to 0.3": 3, "0.3 to 0.5": 10, "0.5 to 0.7": 10,
              "0.7 to 0.9": 4}  # fmt: skip
    assert {b: bands.count(b) for b in set(bands)} == wanted
    grew = STUDY.grew()
    assert len(grew) == 207
    assert [w["drawn"] for w in grew] == sorted(w["drawn"] for w in grew)
    # every world that fills is taken, wherever it was drawn; the rest are of the even draw,
    # the first drawn of each band
    assert [w["rule"] for w in chosen[:11]] == [w["rule"] for w in grew if w["live"] >= 0.9]
    for w in chosen[11:]:
        assert w["drawn"] <= STUDY.EVEN_DRAW and w["live"] < 0.9
        low, high = map(float, w["band"].split(" to "))
        assert low <= w["live"] < high
        earlier = [g for g in grew if g["band"] == w["band"] and g["drawn"] < w["drawn"]]
        assert all(g["rule"] in {c["rule"] for c in chosen} for g in earlier)
    # how many rules of the even draw each band stands for
    assert STUDY.population() == {"fills": 4, "0.0 to 0.3": 3, "0.3 to 0.5": 30,
                                  "0.5 to 0.7": 38, "0.7 to 0.9": 5}  # fmt: skip
    # none of them is a world step 4e ran
    before = {"B245678/S3678", "B23467/S4568", "B24678/S34678", "B3568/S124678", "B2/S0",
              "B2578/S135678"}  # fmt: skip
    assert not before & {w["rule"] for w in chosen} and STILL in before
    # and what is written down is what the rule gives
    kept = json.loads((LAB / "worlds.json").read_text())
    assert kept["worlds"] == chosen and STUDY.worlds() == {w["rule"]: w for w in chosen}
    assert kept["of the even draw's rules that grow territories, each band stands for"] == (
        STUDY.population())  # fmt: skip


def test_the_design():
    plan = STUDY.design()
    assert len(plan) == 39 and plan[STILL] == {"learn": [17901, 17902, 17903, 17904],
                                               "try": [17905, 17906, 17907, 17908]}  # fmt: skip
    seeds = [s for w in plan.values() for s in w["learn"] + w["try"]]
    assert len(seeds) == len(set(seeds)) == 8 + 38 * 4 and min(seeds) == 17001
    assert all(len(w["learn"]) == len(w["try"]) == 2 for rule, w in plan.items() if rule != STILL)
    jobs = STUDY.start_jobs(plan)
    assert len(jobs) == 160 and [w for w, _ in jobs[:8]] == [STILL] * 8
    assert [w for w, _ in jobs[8:46]] == list(STUDY.worlds())  # the worlds take turns


def test_the_paces_a_rule_is_kept_at():
    assert STUDY.ticks(8) == (4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64)
    assert STUDY.ticks(16) == (16, 32, 48, 64, 80, 96, 112, 128, 160, 192, 256)
    for block in STUDY.BLOCKS:
        # every tick is one the block's readings can give, and the square clock's is among them
        assert all(t % STUDY.EVERY[block] == 0 for t in STUDY.ticks(block))
        assert LADDER.square(block) in STUDY.ticks(block)
        assert block % STUDY.EVERY[block] == 0
    assert STUDY.nearest(0.54) == 0.5 and STUDY.nearest(0.73) == 0.75 and STUDY.nearest(1.09) == 1
    assert STUDY.nearest(0.01) == 0.25 and STUDY.nearest(9.0) == 4.0
    assert STUDY.nearest(0.61) == 0.5 and STUDY.nearest(0.62) == 0.75  # nearest by ratio


def test_where_a_curve_is_least():
    def bowl(at):
        return {p: 0.01 + 0.2 * math.log2(p / at) ** 2 for p in STUDY.RATIOS}

    for at in (0.5, 0.6, 0.9, 1.0, 1.4, 2.2):
        assert math.isclose(STUDY.vertex(bowl(at)), at, rel_tol=1e-9), at
    # a curve still falling at the last pace, or rising from the first: the end itself
    assert STUDY.vertex({p: 1 / p for p in STUDY.RATIOS}) == 4.0
    assert STUDY.vertex({p: p for p in STUDY.RATIOS}) == 0.25
    # two paces all but level: the bottom lies between them, and never beyond the neighbours
    assert 1.3 < STUDY.vertex({0.5: 0.3, 1.0: 0.1, 2.0: 0.1001, 4.0: 0.5}) < 1.5
    assert STUDY.vertex({0.5: 1e9, 1.0: 0.1, 2.0: 0.10001, 4.0: 0.5}) <= 2.0
    assert isinstance(STUDY.vertex(bowl(0.6)), float)
    assert STUDY.vertex({}) is None and STUDY.vertex({1.0: None}) is None
    assert STUDY.vertex({0.5: None, 1.0: 0.2, 2.0: float("nan")}) == 1.0


def test_the_rank_correlation():
    assert STUDY.rank_correlation([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1)
    assert STUDY.rank_correlation([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1)
    assert STUDY.rank_correlation([1, 2, 3, 4], [1, 3, 2, 4]) == pytest.approx(0.8)
    assert STUDY.rank_correlation([1, 2], [1, 2]) is None
    assert STUDY.rank_correlation([1, 1, 1], [1, 2, 3]) is None


# --- the measures, on made-up records ------------------------------------------------------------


def _made_up(worlds: dict) -> "STUDY.Measures":
    """Records that hold only what the clock, the pace by the walls and what a claim stands
    on are read from: per world its walls at blocks of 8 at generations 1,024 and 4,096, and
    the larger species' share of the live cells."""
    plan, rows = {}, []
    for i, (world, (at, end, larger)) in enumerate(worlds.items()):
        seeds = list(range(10 * i, 10 * i + 4))
        plan[world] = {"learn": seeds[:2], "try": seeds[2:]}
        for seed in seeds:
            rows.append({"kind": "start", "world": world, "seed": seed,
                         "walls": {"8": {"1024": at, "4096": end}},
                         "live": {"4096": 0.9}, "larger": {"4096": 0.9 * larger}})  # fmt: skip
    return STUDY.Measures(rows, plan)


def test_a_worlds_clock_and_its_pace_by_its_walls():
    m = _made_up({
        STILL: (0.08, 0.04, 0.55),
        "half": (0.08 / 0.5**0.5, 0.04 / 0.5**0.5, 0.55),  # the still world at half the pace
        "slow": (0.2, 0.2 * 4**-0.25, 0.55),  # walls that thin as the quarter power
        "between": (0.2, 0.2 * 4**-0.36, 0.55),
        "taken": (0.08, 0.04, 0.95),  # one species has all but taken the grid
        "wide": (0.21, 0.07, 0.55),  # territories too small for blocks of 8 at the start
        "gone": (0.08, 0.0, 0.55),  # no walls left
        "far": (0.8, 0.4, 0.55),  # the square-root clock, at a hundredth of the pace
    })  # fmt: skip
    assert m.power(STILL) == pytest.approx(0.5) and m.power("slow") == pytest.approx(0.25)
    assert m.pace_by_walls(STILL) == pytest.approx(1) and m.grid_pace(STILL) == 1.0
    assert m.pace_by_walls("half") == pytest.approx(0.5) and m.grid_pace("half") == 0.5
    assert m.power("gone") is None and m.pace_by_walls("gone") is None
    assert m.grid_pace("gone") is None
    # what a claim stands on
    assert m.holds_ground("half") and not m.holds_ground("taken")
    assert m.square_root("half") and not m.square_root("slow") and not m.square_root("between")
    assert m.fits("half") and not m.fits("wide")
    assert m.on_the_clock() == ["half", "wide"]
    # a pace the paces a rule is kept at do not come near is no pace to try a rule at
    assert m.power("far") == pytest.approx(0.5) and m.pace_by_walls("far") == pytest.approx(0.01)
    assert not m.square_root("far")
    assert not m.stands({"world": "far", "needs": "a clock that says"})

    def stands(world, needs):
        return m.stands({"world": world, "needs": needs})

    assert stands("taken", "nothing") and not stands("taken", "two species")
    assert stands("half", "a clock that says") and stands("slow", "a clock that says")
    assert not stands("between", "a clock that says") and not stands("gone", "a clock that says")
    assert stands("half", "the square-root clock") and not stands("slow", "the square-root clock")
    fits = "the square-root clock and a block that fits"
    assert stands("half", fits) and not stands("wide", fits) and not stands("taken", fits)
    with pytest.raises(ValueError):
        stands("half", "something else")


def test_the_judge():
    served = {"quantity": "paces apart", "at_least": None, "at_most": 1.5}
    assert STUDY.judge(1.2, served, True) == "holds"
    assert STUDY.judge(1.6, served, True) == "fails"
    assert STUDY.judge(1.2, served, False) == STUDY.judge(None, served, True) == "not tested"
    assert STUDY.judge(float("nan"), served, True) == "not tested"
    # a filling world's clock: the square root or more, or set; it fails only between
    fills = {"quantity": "its clock", "at_least": None, "at_most": None, "between": [0.1, 0.4]}
    assert STUDY.judge(0.47, fills, True) == STUDY.judge(0.0, fills, True) == "holds"
    assert STUDY.judge(0.4, fills, True) == STUDY.judge(0.1, fills, True) == "holds"
    assert STUDY.judge(0.27, fills, True) == "fails"
    assert STUDY.judge(0.27, fills, False) == "not tested"
    # a claim of family A is judged against the bound the world's clock picks
    clock = {"quantity": "served, by its clock", "at_least": None, "at_most": None}
    assert STUDY.judge(0.005, clock, True, 0.47) == "holds"  # square-root clock, and served
    assert STUDY.judge(0.03, clock, True, 0.47) == "fails"  # square-root clock, not served
    assert STUDY.judge(0.6, clock, True, 0.27) == "holds"  # another clock, and not served
    assert STUDY.judge(0.03, clock, True, 0.27) == "fails"  # another clock, yet nearly served
    assert STUDY.judge(0.005, clock, True, None) == "not tested"
    assert STUDY.judge(0.005, clock, False, 0.47) == "not tested"
    assert STUDY.number(float("inf")) is None and STUDY.number(0.123456789, 3) == 0.123
    assert STUDY.over(1.0, 0.0) is None and STUDY.over(3.0, 4.0) == 0.75


def test_the_claims_the_study_registers():
    claims = STUDY.claims()
    labels = [c["label"] for c in claims]
    assert len(labels) == len(set(labels)) == 38 * 3 + 11 + 1 + 2
    by_family = {f: sum(c["family"] == f for c in claims) for f in "AFPKRX"}
    assert by_family == {"A": 38, "F": 11, "P": 38, "K": 38, "R": 1, "X": 2}
    needs = {"A": "a clock that says", "F": "two species", "P": "the square-root clock",
             "K": "the square-root clock and a block that fits", "R": "nothing",
             "X": "nothing"}  # fmt: skip
    chosen = STUDY.worlds()
    for c in claims:
        assert c["needs"] == needs[c["family"]], c["label"]
        assert (c["world"] in chosen) == (c["family"] in "AFPK")
        # a claim of family A takes its bound from the world's clock, one of family F fails
        # between two powers, and the others carry a bound
        assert (c["at_least"] is None and c["at_most"] is None) == (c["family"] in "AF")
        assert ("between" in c) == (c["family"] == "F")
        assert json.loads(json.dumps(c)) == c
    assert {c["world"] for c in claims if c["family"] == "F"} == {
        rule for rule, w in chosen.items() if w["band"] == "fills"}  # fmt: skip
    assert STUDY.predictions() == claims


# --- end to end, on worlds small enough to run here ----------------------------------------------


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Three worlds and the still world on a grid of side 64 for 1,024 generations."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(LADDER, "SIDE", 64)
    monkeypatch.setattr(LADDER, "GENERATIONS", 1024)
    monkeypatch.setattr(LADDER, "WINDOWS", {"A": (64, 128), "B": (128, 256), "C": (256, 1024)})
    monkeypatch.setattr(LADDER, "FROM", 256)
    monkeypatch.setattr(STUDY, "STILL_STARTS", (9901, 9902, 9903, 9904))
    chosen = [{"rule": rule, "drawn": i + 1, "live": live, "band": band, "first": 9801 + 20 * i}
              for i, (rule, live, band) in enumerate((
                  ("B24678/S34678", 0.97, "fills"), ("B23467/S4568", 0.71, "0.7 to 0.9"),
                  ("B2578/S135678", 0.95, "fills")))]  # fmt: skip
    kept = tmp_path / "worlds.json"
    kept.write_text(json.dumps({"worlds": chosen}))
    monkeypatch.setattr(STUDY, "WORLDS", kept)
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    return tmp_path


def test_one_fine_run_on_record(small):
    record = STUDY.run_start((STILL, 9901))
    assert record == STUDY.run_start((STILL, 9901))  # the second time from the leaders kept
    assert (small / "cache" / "class-B245678-S3678-64-1024-9901.npz").exists()
    assert json.loads(canonical(record)) == record
    assert (record["kind"], record["world"], record["seed"]) == ("start", STILL, 9901)
    # the still world is tallied at every pace, any other world at the square clock alone
    assert set(record["tally"]) == {LADDER.key(b, t) for b in STUDY.BLOCKS
                                    for t in STUDY.ticks(b)}  # fmt: skip
    other = STUDY.run_start(("B23467/S4568", 9821))
    assert set(other["tally"]) == {"8 16", "16 64"}
    for where, by_window in {**record["tally"], **other["tally"]}.items():
        block, tick = map(int, where.split())
        for name, rows in by_window.items():
            # a transition is read every sixteen generations at most, whatever the tick
            seen = len(LADDER.instants(4, tick, *LADDER.WINDOWS[name])) * (64 // block) ** 2
            assert LADDER.dense(rows).sum() == seen, (where, name)
    assert set(record["walls"]) == {"8", "16"} and set(record["live"]) == {
        "64", "128", "256", "1024"}  # fmt: skip
    # blocks of 8 are read every four generations, blocks of 16 every sixteen
    kept = STUDY.fine(STILL, 9901)
    assert kept[8].shape == (257, 8, 8) and kept[16].shape == (65, 4, 4)
    # the tally at the square clock is the one step 4e's reading gives
    again = LADDER.fine("check", STILL, 1.0, 9901, 64, 1024)
    assert np.array_equal(kept[8][::2], again[8]) and np.array_equal(kept[16], again[16])
    theirs = LADDER.tallies(again, 1024)["8 16"]
    assert record["tally"]["8 16"] == theirs


def test_the_study_end_to_end_on_small_worlds(small):
    path = STUDY.RECORDS
    STUDY.execute(path, 1)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    starts = [r for r in rows if r["kind"] == "start"]
    ahead = [r for r in rows if r["kind"] == "ahead"]
    # four starts of the still world and of each of three worlds; three rules run on at two
    # blocks on each world's two trial starts
    assert len(starts) == 16 and len(ahead) == 3 * 3 * 2 * 2
    assert {r["rule"] for r in ahead} == {STUDY.OWN, STUDY.AS_IT_IS, STUDY.AT_PACE}
    assert all(r["block"] in STUDY.BLOCKS and r["tick"] == LADDER.square(r["block"])
               for r in ahead)  # fmt: skip
    for r in ahead:
        if r["rule"] != STUDY.AT_PACE:
            assert r["rule_tick"] == r["tick"]
        else:
            assert r["rule_tick"] in STUDY.ticks(r["block"])
    STUDY.execute(path, 1)  # run again, it finds everything done
    assert len(path.read_text().splitlines()) == len(rows)
    for record in (starts[0], starts[-1], ahead[0], ahead[-1]):
        assert canonical(STUDY.rerun(record)) == canonical(record)
    with pytest.raises(ValueError):
        STUDY.rerun({**ahead[0], "rule": "nobody's"})
    claims = STUDY.claims()
    assert len(claims) == 3 * 3 + 2 + 1 + 2
    found = STUDY.decide(rows, claims)
    assert found["missing"] == [] and set(found["outcomes"]) == {c["label"] for c in claims}
    assert set(found["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert set(found["verdict"]) == set("AFPKRX") and json.loads(json.dumps(found)) == found
    ranks = "R the faster by its walls is the faster by the rule"
    assert found["outcomes"][ranks] == "not tested"  # three worlds are too few to rank
    # every number comes out the same from the measures directly
    plan = STUDY.design()
    m = STUDY.Measures(rows, plan)
    for world, told in found["worlds"].items():
        assert set(told["more surprise than its own rule, by pace"]) == {
            str(r) for r in STUDY.RATIOS}  # fmt: skip
        if world != STILL:
            assert told["least"]["8"] == STUDY.number(m.least(world))
            by_pace = [v for v in told["more surprise than its own rule, by pace"].values()
                       if v is not None]  # fmt: skip
            assert told["least"]["8"] == (min(by_pace) if by_pace else None)
    # the still world's rule here has seen the still world's trial starts: tried on them it is
    # no worse than the rule learned from the other starts
    still = found["worlds"][STILL]
    assert still["as it is"] < 0.02 and still["pace by its walls"] > 0
    # the summary counts the chosen worlds by band
    wide = found["how wide"]
    assert wide["of"] == 3 and sum(row["worlds"] for row in wide["by band"].values()) == 3
    assert 0 <= wide["served"] <= 3
    # a run with a record missing says so, and judges nothing
    short = STUDY.decide(rows[:-1], claims)
    assert short["missing"] and set(short["outcomes"].values()) == {"missing"}


# --- what was written down before the run --------------------------------------------------------


def test_the_bounds_were_drawn_from_step_4es_worlds():
    sizing = json.loads((LAB / "sizing.json").read_text())
    known = sizing["step 4e's worlds"]
    assert set(known) == {"still", "busy", "near", "another", "sparse", "set"}
    clock = "walls thin as time to the power, blocks of 8"
    for world in ("still", "busy", "near", "another"):
        told = known[world]
        # on the square-root clock, served at some pace, and the two paces within the factor
        assert told[clock]["the mean over its starts"] >= STUDY.SQUARE_ROOT
        assert told["least of those"] <= STUDY.SERVES
        assert told["the two paces apart by a factor of"] <= STUDY.PACE_AGREES
        assert told["walls at blocks of 8, generation 1,024"] <= STUDY.BLOCK_FITS
    for world in ("sparse", "set"):
        told = known[world]
        assert told[clock]["the mean over its starts"] <= STUDY.ANOTHER_CLOCK
        assert told["least of those"] >= STUDY.DOES_NOT
    assert all(told["larger species' share of the live, most of one start"] < STUDY.HOLDS_GROUND
               for told in known.values())  # fmt: skip
    # the run-ons step 4e made: as it is in the near world, at half its pace in the other
    near, another = (known[w]["run on at blocks of 8, amiss over changed"]
                     for w in ("near", "another"))  # fmt: skip
    assert near["the still world's rule, as it is"] <= STUDY.WHERE
    assert another["the still world's rule, at half its pace"] <= STUDY.WHERE
    assert another["the still world's rule, as it is"] > STUDY.WHERE
    assert STUDY.nearest(known["another"]["pace by its walls"]) == 0.5
    assert set(sizing["what the bounds were drawn from"]) == {
        "A, the clock", "F, a filling world's clock", "P, the pace two ways",
        "K, run on at its walls' pace", "X, the anchor", "what a claim stands on"}  # fmt: skip
    # the filling worlds step 4e ran: three by the square root, and the control set
    for world, fills in (("still", True), ("near", True), ("another", True), ("set", True)):
        power = known[world][clock]["the mean over its starts"]
        assert fills and not STUDY.HAS_SET < power < STUDY.SQUARE_ROOT, world


def test_the_registration():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    question = entries[0]["body"]
    registered = [e["body"] for e in entries if e["kind"] == "prediction"]
    assert entries[0]["kind"] == "question" and len(registered) == 128
    for body, claim in zip(registered, STUDY.claims(), strict=True):
        assert {k: body[k] for k in claim} == claim
    files = {"study.py": LAB / "study.py", "worlds.json": LAB / "worlds.json",
             "sizing.json": LAB / "sizing.json"}  # fmt: skip
    for name, digest in question["sha256"].items():
        assert STUDY.sha(files.get(name, LAB / name)) == digest, name
    assert question["runs"] == 160 + 456 and len(question["worlds"]) == 38
    assert question["side"] == 1024 and question["generations"] == 4096


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
    again = STUDY.decide(rows, STUDY.claims())
    assert again["missing"] == [] and set(again) == set(verdict) - {"question", "cites"}
    for part in again:
        assert again[part] == verdict[part], part


def test_the_registered_run_found_what_the_plan_says():
    verdict = _verdict()
    assert verdict["missing"] == []
    counts = verdict["counts"]
    assert counts == {"A": {"holds": 17, "fails": 20, "not tested": 1},
                      "F": {"holds": 8, "fails": 3},
                      "K": {"holds": 19, "fails": 10, "not tested": 9},
                      "P": {"holds": 8, "fails": 21, "not tested": 9},
                      "R": {"fails": 1}, "X": {"holds": 2}}  # fmt: skip
    words = list(verdict["outcomes"].values())
    assert (words.count("holds"), words.count("fails"), words.count("not tested")) == (54, 55, 19)
    worlds = {w: t for w, t in verdict["worlds"].items() if w != STILL}
    assert len(worlds) == 38 and all(t["two species hold ground"] for t in worlds.values())

    def power(t):
        return t["walls thin as time to the power"]["8"]

    def run_on(t, whose):
        return t["run on, amiss over changed"][f"{whose}, blocks of 8"]

    # the clock is common: 29 worlds thin their walls as about the square root of the time
    clock = {w: t for w, t in worlds.items() if power(t) >= STUDY.SQUARE_ROOT}
    assert len(clock) == 29 and max(power(t) for t in clock.values()) < 0.55
    assert sum(power(t) <= STUDY.HAS_SET for t in worlds.values()) == 5  # five have set
    # the rule is not: it serves ten of them within 1%, four more within 2%, and misses fifteen
    served = {w for w, t in clock.items() if t["least"]["8"] <= 0.01}
    near = {w for w, t in clock.items() if 0.01 < t["least"]["8"] <= 0.02}
    missed = set(clock) - served - near
    assert (len(served), len(near), len(missed)) == (10, 4, 15)
    assert min(clock[w]["least"]["8"] for w in missed) > 0.035
    assert verdict["how wide"]["served"] == 10
    assert verdict["how wide"]["served, by the sample weighted"] == 0.231
    # no world off the clock is served
    assert all(t["least"]["8"] > 0.045 for w, t in worlds.items() if w not in clock)
    # what marks the class is how full the world is
    assert min(clock[w]["live at the end"] for w in served) > 0.55
    assert max(clock[w]["live at the end"] for w in missed) < 0.62
    assert sum(clock[w]["live at the end"] > 0.52 for w in missed) == 2
    lives = [t["live at the end"] for t in clock.values()]
    least = [t["least"]["8"] for t in clock.values()]
    assert STUDY.rank_correlation(lives, least) < -0.8
    # run on at its walls' pace, the still world's rule keeps 19 of the 29, and beats the
    # world's own rule in 23; in the fifteen it misses the world's own rule does not run
    assert all(t["a block of 8 fits"] for t in clock.values())
    kept = {w for w, t in clock.items() if run_on(t, STUDY.AT_PACE) <= STUDY.WHERE}
    assert len(kept) == 19 and len(kept & served) == 9 and near <= kept
    assert len(kept & missed) == 6
    assert sum(run_on(t, STUDY.OWN) <= STUDY.WHERE for t in clock.values()) == 14
    assert sum(run_on(t, STUDY.AT_PACE) < run_on(t, STUDY.OWN) for t in clock.values()) == 23
    assert sum(run_on(clock[w], STUDY.OWN) > 1 for w in missed) == 7
    # the pace two ways: loosely inside the class, not outside it
    apart = {w: max(t["pace by the rule"]["8"] / t["pace by its walls"],
                    t["pace by its walls"] / t["pace by the rule"]["8"])
             for w, t in clock.items()}  # fmt: skip
    assert sum(apart[w] <= STUDY.PACE_AGREES for w in served) == 8
    assert verdict["measured"]["R the faster by its walls is the faster by the rule"]["value"] < 0
    # three filling worlds keep a slower clock, one has set, seven are on the clock
    fills = {w: power(t) for w, t in worlds.items() if t["band"] == "fills"}
    between = {w for w, pw in fills.items() if STUDY.HAS_SET < pw < STUDY.SQUARE_ROOT}
    assert between == {"B2356/S025678", "B347/S0125678", "B358/S035678"}
    assert sum(pw >= STUDY.SQUARE_ROOT for pw in fills.values()) == 7
    # the anchor
    assert all(abs(verdict["measured"][f"X the still world, block {b}"]["value"]) < 0.002
               for b in (8, 16))  # fmt: skip
