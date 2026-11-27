"""The registered test of a coarse rule that remembers (examples/scale-up-memory/study.py):
its design, its tallies on record, its measures on made-up records whose answer is known, its
claims, and the whole of it end to end on worlds small enough to run here.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from lattice_lab.ledger import canonical

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


STUDY = _load("scale_up_memory_study", LAB / "study.py")
LOOK, LADDER = STUDY.look, STUDY.ladder
PLAIN, HOW = STUDY.PLAIN, STUDY.HOW
OWN, BELOW, LOOKS = STUDY.OWN, STUDY.BELOW, STUDY.LOOKS


def test_the_design():
    plan = STUDY.design()
    assert plan["still"] == {"learn": list(range(19001, 19009)), "try": list(range(19009, 19017))}
    assert plan["busy"] == {"learn": list(range(19101, 19109)), "try": list(range(19109, 19117))}
    jobs = STUDY.start_jobs(plan)
    assert len(jobs) == 32 and jobs[:3] == [("still", 19001), ("busy", 19101), ("still", 19002)]
    assert (STUDY.SIDE, STUDY.GENERATIONS, STUDY.BLOCKS) == (1024, 4096, (4, 8, 16))
    # the worlds and the matched ages are step 4g's, as far as this grid reaches
    rung = LOOK.study
    assert {n: w["rule"] for n, w in STUDY.WORLDS.items()} == {
        n: w["rule"] for n, w in rung.WORLDS.items()}  # fmt: skip
    assert STUDY.AGES == {b: rung.AGES[b] for b in STUDY.BLOCKS}
    for block in STUDY.BLOCKS:
        first, last = STUDY.AGES[block]
        tick = LADDER.square(block)
        assert (first // tick, last // tick) == (16, 64)  # so "how long" means the same
    # two rules: as it is, and with how long in view up to eight ticks
    assert STUDY.READINGS[PLAIN].size == 1 and STUDY.READINGS[HOW].size == 8
    assert STUDY.LONG.size == 16 and list(STUDY.SPANS)[0] == STUDY.NEW
    assert list(STUDY.SPANS)[-1] == STUDY.OLD
    # the look's rules: all eight of step 4g's starts, at blocks of 8 and 16
    looks = STUDY.reference()
    assert set(looks) == {(w, b) for w in STUDY.WORLDS for b in (8, 16)}
    for (_world, block), counts in looks.items():
        blocks = (2048 // block) ** 2
        seen = len(LADDER.instants(block, LADDER.square(block), *STUDY.AGES[block])) * blocks
        assert counts.shape == (16, 3, 9, 9, 3) and counts.sum() == 8 * seen


def test_a_tally_goes_on_record_and_comes_back():
    rng = np.random.default_rng(3)
    for size in (1, 8, 16):
        counts = rng.integers(0, 5, size=(size, 3, 9, 9, 3)) * (
            rng.random((size, 3, 9, 9, 1)) < 0.2
        )
        rows = STUDY.sparse(counts)
        assert len(rows) == int((counts.sum(axis=-1) > 0).sum())
        assert np.array_equal(STUDY.dense(rows, size), counts)
        assert json.loads(json.dumps(rows)) == rows
    assert STUDY.sparse(np.zeros((8, 3, 9, 9, 3), dtype=int)) == []


def _tally(table: dict) -> np.ndarray:
    """A made-up tally by how long: `table` gives, by (ticks, rival neighbours), how many
    blocks species 1 led and how many of them had another leader one tick on."""
    counts = np.zeros((16, 3, 9, 9, 3), dtype=np.int64)
    for (ticks, near), (blocks, changed) in table.items():
        counts[ticks - 1, 1, 8 - near, near] = [0, blocks - changed, changed]
    return counts


def _made_up(tallies: dict, ahead: dict | None = None, walls: float = 0.17) -> "STUDY.Measures":
    """Records of one world with one start to learn from and one to try on, holding the
    tallies given by block for each, and run-ons given by (block, reading, whose)."""
    plan = {"still": {"learn": [1], "try": [2]}}
    rows = [{"kind": "start", "world": "still", "seed": seed,
             "walls": {str(b): {str(g): walls for g in STUDY.AGES[b]} for b in STUDY.BLOCKS},
             "tally": {str(b): STUDY.sparse(tallies[b]) for b in tallies}}
            for seed in (1, 2)]  # fmt: skip
    for (block, reading, whose), told in (ahead or {}).items():
        rows.append({"kind": "ahead", "world": "still", "seed": 2, "block": block,
                     "reading": reading, "rule": whose, **told})  # fmt: skip
    return STUDY.Measures(rows, plan, looks={})


def test_the_table_and_the_mix_on_made_up_records():
    # at five rival neighbours a young lead changes hands half the time and an old one a
    # tenth of the time, at both rungs; blocks of 8 have more young leads than blocks of 16
    young, old = (1, 5), (16, 5)
    m = _made_up(
        {
            8: _tally(
                {young: (1000, 500), old: (1000, 100), (1, 3): (1000, 200), (16, 3): (4000, 80)}
            ),
            16: _tally({young: (250, 125), old: (750, 75), (1, 3): (500, 50), (16, 3): (4500, 45)}),
        }
    )  # two starts hold each tally, so every count below is doubled and no chance changes
    assert m.chance("still", 8, STUDY.NEW, 5) == 0.5 and m.chance("still", 16, STUDY.OLD, 5) == 0.1
    assert m.chance("still", 8, None, 5) == pytest.approx(0.30)  # the rule as it is
    assert m.chance("still", 16, None, 5) == pytest.approx(0.20)
    assert m.chance("still", 8, "2", 5) is None  # no block had its leader two ticks
    # no block's chance changed between the rungs: the whole fall is the mix
    assert m.mixed("still", 8, 5) is None  # some span at blocks of 16 has too few blocks
    value = m.value
    claim = {"world": "still", "block": 16, "near": 5}
    assert value({**claim, "quantity": "chance, this rung over the one below",
                  "span": STUDY.OLD}) == pytest.approx(1.0)  # fmt: skip
    assert value({**claim, "quantity": "chance, this rung over the one below",
                  "span": None}) == pytest.approx(2 / 3)  # fmt: skip
    assert value({**claim, "quantity": "a young lead over an old one"}) == pytest.approx(5.0)
    # at three both chances halve from blocks of 8 to 16
    falls = "chance, this rung over the one below"
    assert value({"world": "still", "block": 16, "near": 3, "span": STUDY.OLD,
                  "quantity": falls}) == pytest.approx(0.5)  # fmt: skip
    with pytest.raises(ValueError):
        value({"world": "still", "quantity": "something else"})
    # every span seen at both rungs, an older lead changing hands less often (0.6, 0.5, ...
    # 0.1), and blocks of 16 with more of the old: the mix alone, and its share of the fall
    spans = [low for low, _ in STUDY.SPANS.values()]
    assert spans == [1, 2, 3, 5, 9, 16]
    here = {(t, 5): (1000, 700 - 100 * k) for k, t in enumerate(spans, start=1)}
    above = {(t, 5): (300 * k, 210 * k - 30 * k * k) for k, t in enumerate(spans, start=1)}
    m = _made_up({8: _tally(here), 16: _tally(above)})
    plain_here, plain_above = 0.35, (0.7 * 21 - 0.1 * 91) / 21
    assert m.chance("still", 8, None, 5) == pytest.approx(plain_here)
    assert m.chance("still", 16, None, 5) == pytest.approx(plain_above)
    assert m.mixed("still", 8, 5) == pytest.approx(plain_here)  # no block's chance changed
    assert m.mix_share("still", 8, 5) == pytest.approx(1.0)  # so the whole fall is the mix
    # halve every chance at blocks of 16: the mix alone gives half the rule as it is
    halved = {key: (blocks, changed // 2) for key, (blocks, changed) in above.items()}
    m = _made_up({8: _tally(here), 16: _tally(halved)})
    assert m.mixed("still", 8, 5) == pytest.approx(plain_here / 2)
    alone = "the mix alone over the rule as it is"
    assert m.value({"world": "still", "block": 8, "near": 5, "quantity": alone}) == pytest.approx(
        0.5
    )
    assert m.mix_share("still", 8, 5) == pytest.approx(
        (plain_here / 2 - plain_above / 2) / (plain_here - plain_above / 2))  # fmt: skip
    # a rule that rises from one rung to the next has no fall to share out
    m = _made_up({8: _tally(above), 16: _tally(here)})
    assert m.mix_share("still", 8, 5) is None


def _ran(amiss: float, changed: float = 0.2, walls: float = 0.09, back: float = 0.25) -> dict:
    return {"amiss": [[amiss, amiss]], "changed": changed, "twin": [amiss],
            "walls_world": 0.09, "walls_rule": [[walls, walls]], "changes_world": 0.01,
            "returns_world": 0.25, "changes_rule": [0.01], "returns_rule": [back]}  # fmt: skip


def test_the_run_ons_on_made_up_records():
    m = _made_up({}, {
        (16, PLAIN, OWN): _ran(0.10, walls=0.081, back=0.10),
        (16, PLAIN, BELOW): _ran(0.115),
        (16, HOW, OWN): _ran(0.08, walls=0.0945, back=0.27),
        (16, HOW, BELOW): _ran(0.084),
        (16, HOW, LOOKS): _ran(0.082),
    })  # fmt: skip
    claim = {"world": "still", "block": 16}

    def value(quantity, **more):
        return m.value({**claim, "quantity": quantity, **more})

    assert value("amiss, with how long in view over as it is") == pytest.approx(0.8)
    assert value("walls kept", reading=PLAIN) == pytest.approx(0.9)
    assert value("walls kept", reading=HOW) == pytest.approx(1.05)
    assert value("going back, the rule's world less the real one") == pytest.approx(0.02)
    assert value("going back, the rule's world over the real one") == pytest.approx(0.4)
    ladder = "amiss, the rule from below over the rung's own"
    assert value(ladder, reading=HOW) == pytest.approx(1.05)
    assert value(ladder, reading=PLAIN) == pytest.approx(1.15)
    assert value("what the plain rule from below pays, less what the remembering one does"
                 ) == pytest.approx(0.10)  # fmt: skip
    assert value("amiss, the remembering rule from below over the rung's own plain rule"
                 ) == pytest.approx(0.84)  # fmt: skip
    assert value("amiss, the look's rule over the rung's own") == pytest.approx(1.025)
    assert value("amiss over changed", reading=PLAIN) == pytest.approx(0.5)
    assert value(ladder, reading=HOW, block=8) is None  # no run-on on record there
    # a run-on is read only through a block that fits
    assert m.fits("still", 16) and m.stands({"world": "still", "fits": 16})
    wide = _made_up({}, walls=0.25)
    assert not wide.fits("still", 16) and not wide.stands({"world": "still", "fits": 16})
    assert wide.stands({"world": "still", "fits": None})


def test_the_judge():
    claim = {"at_least": 0.9, "at_most": 1.1}
    assert STUDY.judge(1.0, claim, True) == "holds"
    assert STUDY.judge(0.89, claim, True) == STUDY.judge(1.11, claim, True) == "fails"
    assert STUDY.judge(1.0, claim, False) == STUDY.judge(None, claim, True) == "not tested"
    assert STUDY.judge(float("nan"), claim, True) == "not tested"
    assert STUDY.number(None) is None and STUDY.number(1 / 3, 2) == 0.33
    assert STUDY.over(1.0, 0.0) is None and STUDY.over(1.0, 4.0) == 0.25
    assert STUDY.less(1.0, None) is None and STUDY.less(1.0, 0.25) == 0.75


def test_the_claims_the_study_registers():
    claims = STUDY.claims()
    labels = [c["label"] for c in claims]
    assert len(labels) == len(set(labels)) == 74
    by_family = {f: sum(c["family"] == f for c in claims) for f in "ABCDERX"}
    assert by_family == {"A": 10, "B": 6, "C": 12, "D": 20, "E": 10, "R": 12, "X": 4}
    run_on = ("amiss", "walls kept", "going back", "what the plain rule from below pays")
    for c in claims:
        assert c["at_least"] is not None or c["at_most"] is not None, c["label"]
        # a run-on is read only through a block that fits, and only run-ons ask it
        assert (c["fits"] is not None) == c["quantity"].startswith(run_on), c["label"]
        assert c["fits"] in (None, c.get("block")) and c["world"] in STUDY.WORLDS
        assert json.loads(json.dumps(c)) == c
    assert STUDY.predictions() == claims
    # every quantity a claim names is one the measures know
    m = _made_up({})
    for c in claims:
        if c["world"] == "still":
            try:
                m.value(c)
            except KeyError:
                pass  # a tally the made-up records do not hold
            except ValueError as error:
                assert "no leaders" in str(error) or "tally" in str(error), c["label"]


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Both worlds on a grid of side 128 for 512 generations, two starts each, the rungs' ages
    shrunk to fit, and one pair of run-ons from each trial start."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(STUDY, "SIDE", 128)
    monkeypatch.setattr(STUDY, "GENERATIONS", 512)
    monkeypatch.setattr(STUDY, "STARTS", 2)
    monkeypatch.setattr(STUDY, "AGES", {4: (64, 128), 8: (128, 256), 16: (256, 512)})
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    monkeypatch.setattr(STUDY, "PAIRS", 1)
    return tmp_path


def test_one_fine_run_on_record(small):
    record = STUDY.run_start(("busy", 19101))
    assert record == STUDY.run_start(("busy", 19101))  # the second time from the leaders kept
    assert (small / "cache" / "memory-busy-128-512-19101.npz").exists()
    assert json.loads(canonical(record)) == record
    assert set(record["tally"]) == set(record["walls"]) == {"4", "8", "16"}
    kept = STUDY.fine("busy", 19101)
    assert [kept[b].shape[0] for b in STUDY.BLOCKS] == [33, 33, 33]
    for block in STUDY.BLOCKS:
        first, last = STUDY.AGES[block]
        tick = LADDER.square(block)
        counts = STUDY.dense(record["tally"][str(block)], 16)
        # with nothing of the past in view it is the instrument's own tally
        assert np.array_equal(
            counts.sum(axis=0), LADDER.tally(kept[block], block, tick, first, last)
        )
        assert set(record["walls"][str(block)]) == {str(first), str(last)}
    # and it is the reading step 4e's own code gives of the same world
    again = LADDER.fine("check", "B23467/S4568", 1.0, 19101, 128, 512, blocks=STUDY.BLOCKS)
    assert np.array_equal(kept[16], again[16]) and np.array_equal(kept[4], again[4][:33])


def test_the_study_end_to_end_on_small_worlds(small):
    path = STUDY.RECORDS
    STUDY.execute(path, 1)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    starts = [r for r in rows if r["kind"] == "start"]
    ahead = [r for r in rows if r["kind"] == "ahead"]
    # two starts of two worlds; at two rungs five rules run on, on each world's one trial start
    assert len(starts) == 4 and len(ahead) == 2 * 2 * 5
    assert {(r["reading"], r["rule"]) for r in ahead} == {
        (PLAIN, OWN), (PLAIN, BELOW), (HOW, OWN), (HOW, BELOW), (HOW, LOOKS)}  # fmt: skip
    plan = STUDY.design()
    for r in ahead:
        first, last = STUDY.AGES[r["block"]]
        assert r["from_generation"] == first and r["generations_on"] == last - first
        assert (
            len(r["amiss"]) == len(r["twin"]) == STUDY.PAIRS
            and r["seed"] in plan[r["world"]]["try"]
        )
    # the plain rule's first run is the instrument's own run-on
    mine = next(r for r in ahead if (r["world"], r["block"], r["reading"], r["rule"]) == (
        "busy", 8, PLAIN, OWN))  # fmt: skip
    counts = STUDY.pooled(rows, "busy", plan["busy"]["learn"], 8).sum(axis=0)
    theirs = LADDER.ahead(STUDY.fine("busy", mine["seed"])[8], counts, 8, LADDER.square(8),
                          (mine["seed"], 8, 0), *STUDY.AGES[8])  # fmt: skip
    assert mine["amiss"][0][0] == theirs["apart_rule"][-1]
    assert (
        mine["twin"][0] == theirs["apart_twin"][-1] and mine["changed"] == theirs["apart_start"][-1]
    )
    assert mine["walls_rule"][0][0] == theirs["walls_rule"][-1]
    STUDY.execute(path, 1)  # run again, it finds everything done
    assert len(path.read_text().splitlines()) == len(rows)
    for record in (starts[0], starts[-1], ahead[0], ahead[7], ahead[-1]):
        assert canonical(STUDY.rerun(record)) == canonical(record)
    with pytest.raises(ValueError):
        STUDY.rerun({**ahead[0], "block": 4})
    claims = STUDY.claims()
    found = STUDY.decide(rows, claims)
    assert found["missing"] == [] and set(found["outcomes"]) == {c["label"] for c in claims}
    assert set(found["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert set(found["verdict"]) == set("ABCDERX") and json.loads(json.dumps(found)) == found
    assert sum(sum(words.values()) for words in found["counts"].values()) == 74
    m = STUDY.Measures(rows, plan)
    for world, told in found["worlds"].items():
        assert set(told["rungs"]) == {"4", "8", "16"}
        for block in (8, 16):
            rung = told["rungs"][str(block)]
            assert rung["gap: the rule from the rung below, more surprise"][PLAIN] == STUDY.number(
                m.gap(world, block, PLAIN))  # fmt: skip
            assert set(rung["run on"]) == {f"{reading}, {whose}" for reading, whose in (
                (PLAIN, OWN), (PLAIN, BELOW), (HOW, OWN), (HOW, BELOW), (HOW, LOOKS))}  # fmt: skip
        assert "run on" not in told["rungs"]["4"]
        # with nothing of the past in view the gap is step 4g's own measure
        here, trial = (m.tally(world, part, 16).sum(axis=0) for part in ("learn", "try"))
        lower = LADDER.as_much(m.tally(world, "learn", 8).sum(axis=0), here)
        assert m.gap(world, 16, PLAIN) == pytest.approx(LADDER.excess(lower, here, trial))
    short = STUDY.decide(rows[:-1], claims)
    assert short["missing"] and set(short["outcomes"].values()) == {"missing"}
    assert STUDY.decide(rows[:3], claims)["missing"] == ["busy from start 19102"]


def test_the_bounds_were_sized_on_seen_runs():
    sizing = json.loads((LAB / "sizing.json").read_text())
    drawn = sizing["what the bounds were drawn from"]
    assert set(drawn) == {
        "A, a block's past", "B, the top of the table", "C, along the walls", "D, run on",
        "E, the ladder's own test", "R, the look's rules", "X, the anchor",
        "what a claim stands on"}  # fmt: skip
    assert drawn["D, run on"]["the walls the remembering rule keeps"] == list(STUDY.KEEPS)
    assert drawn["E, the ladder's own test"][
        "the remembering rule from below over the rung's own, at most"] == {
        str(b): bound for b, bound in STUDY.LADDER.items()}  # fmt: skip
    assert drawn["B, the top of the table"][
        "an old lead at five, blocks of 16 within this of 8"] == STUDY.SAME_TOP  # fmt: skip
    # every claim of the study, on step 4d's runs both ways round: all would hold
    seen = sizing["step 4d's runs through the study's measures"]
    claims = {c["label"]: c for c in STUDY.claims()}
    assert set(seen) == set(claims)
    for label, told in seen.items():
        assert (told["at least"], told["at most"]) == (
            claims[label]["at_least"], claims[label]["at_most"]), label  # fmt: skip
        ways = [told[way] for way in told if way not in ("at least", "at most")]
        assert len(ways) == 2 and all(way["would"] == "holds" for way in ways), label


def test_the_registration():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    question = entries[0]["body"]
    registered = [e["body"] for e in entries if e["kind"] == "prediction"]
    assert entries[0]["kind"] == "question" and len(registered) == 74
    for body, claim in zip(registered, STUDY.claims(), strict=True):
        assert {k: body[k] for k in claim} == claim
    for name, digest in question["sha256"].items():
        assert STUDY.sha(LAB / name) == digest, name
    assert question["runs"] == 32 + 160 and question["side"] == 1024
    assert question["generations"] == 4096 and question["run_ons_of_a_rule_from_a_start"] == 16


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
    assert verdict["missing"] == [] and len(verdict["outcomes"]) == 74
    assert set(verdict["outcomes"].values()) == {"holds"}
    assert verdict["verdict"] == {family: "holds" for family in "ABCDERX"}
    assert verdict["counts"] == {"A": {"holds": 10}, "B": {"holds": 6}, "C": {"holds": 12},
                                 "D": {"holds": 20}, "E": {"holds": 10}, "R": {"holds": 12},
                                 "X": {"holds": 4}}  # fmt: skip
    measured = {label: found["value"] for label, found in verdict["measured"].items()}

    def both(label: str, places: int = 2) -> list[float]:
        """A claim's number in the still world and in the busy one."""
        return [round(measured[label.format(w=w)], places) for w in ("still", "busy")]

    # A: a block's past says what it does next
    assert both("A {w}, block 8: a young lead changes hands far more often", 1) == [6.2, 6.9]
    assert both("A {w}, block 16: a young lead changes hands far more often", 1) == [8.0, 8.2]
    assert both("A {w}, block 4: its past removes surprise", 3) == [0.070, 0.074]
    assert both("A {w}, block 8: its past removes surprise", 3) == [0.095, 0.106]
    assert both("A {w}, block 16: its past removes surprise", 3) == [0.102, 0.102]
    # B: the top of the table is the same, and the plain rule's fall there is the mix
    assert both("B {w}: an old lead at five is the same at both rungs") == [0.95, 1.00]
    assert both("B {w}: the rule as it is falls at five") == [0.85, 0.88]
    assert both("B {w}: and the fall is the mix") == [0.99, 1.01]
    # C: along the walls it still changes
    assert both("C {w}: an old lead at three still falls") == [0.34, 0.37]
    assert both("C {w}: a young lead at three still falls") == [0.78, 0.66]
    assert both("C {w}: an old lead at four still falls") == [0.76, 0.80]
    assert both("C {w}: at three the fall is not the mix") == [0.19, 0.14]
    assert both("C {w}: one tick ahead the remembering rule still changes", 3) == [0.069, 0.052]
    assert both("C {w}: nearly as much as the plain rule") == [0.78, 0.93]
    # D: run on, the rule that remembers is the better rule
    assert both("D {w}, block 8: fewer blocks amiss") == [0.73, 0.77]
    assert both("D {w}, block 16: fewer blocks amiss") == [0.78, 0.88]
    assert both("D {w}, block 8: the plain rule loses walls") == [0.86, 0.89]
    assert both("D {w}, block 16: the plain rule loses walls") == [0.90, 0.93]
    assert both("D {w}, block 8: the remembering rule keeps them") == [1.02, 1.04]
    assert both("D {w}, block 16: the remembering rule keeps them") == [1.02, 1.05]
    assert both("D {w}, block 8: it goes back as often as the world", 3) == [0.014, 0.012]
    assert both("D {w}, block 16: it goes back as often as the world", 3) == [0.017, 0.015]
    assert both("D {w}, block 8: the plain rule does not") == [0.44, 0.43]
    assert both("D {w}, block 16: the plain rule does not") == [0.31, 0.30]
    # E: the ladder's own test
    assert both("E {w}, block 8: the remembering rule from below runs it on") == [1.14, 1.04]
    assert both("E {w}, block 16: the remembering rule from below runs it on") == [1.05, 1.00]
    assert both("E {w}, block 8: where the plain rule from below pays more") == [0.06, 0.04]
    assert both("E {w}, block 16: where the plain rule from below pays more") == [0.10, 0.13]
    assert both("E {w}: and it beats the rung's own plain rule") == [0.83, 0.88]
    # R: the look's rules serve unchanged (they have less surprise, having learned from more)
    for block in (8, 16):
        for reading in (PLAIN, HOW):
            still, busy = both(f"R {{w}}, block {block}: the look's rule {reading} serves", 4)
            assert -0.013 < min(still, busy) and max(still, busy) < 0
    assert both("R {w}, block 8: and runs the world on") == [1.00, 1.01]
    assert both("R {w}, block 16: and runs the world on") == [1.02, 1.01]
    # X: the anchor
    assert both("X {w}: the plain gap at blocks of 16", 3) == [0.027, 0.026]
    assert both("X {w}: the plain rule's own run-on at blocks of 16") == [0.56, 0.46]
    # what the plan tells beside the claims
    table = "chance of another leader one tick on, by rival neighbours"
    new, old = (f"has had its leader for {span} ticks" for span in (STUDY.NEW, STUDY.OLD))
    quoted = {"still": (0.31, 0.039, 0.165, 0.156), "busy": (0.33, 0.041, 0.190, 0.190)}
    for world, (young, aged, at_8, at_16) in quoted.items():
        rungs = verdict["worlds"][world]["rungs"]
        assert round(rungs["16"][table][new][4], 2) == young
        assert round(rungs["16"][table][old][4], 3) == aged
        assert round(rungs["8"][table][old][5], 3) == at_8
        assert round(rungs["16"][table][old][5], 3) == at_16
        for block in ("8", "16"):
            ran = rungs[block]["run on"]
            world_back, how_back = ran[f"{HOW}, {OWN}"][
                "going back, the world and the rule's world"
            ]
            plain_back = ran[f"{PLAIN}, {OWN}"]["going back, the world and the rule's world"][1]
            assert 0.245 <= world_back <= 0.271 and 0.26 <= how_back <= 0.283
            assert 0.075 <= plain_back < 0.12
            # the plain rule from the rung below pays 9% to 20%
            below = ran[f"{PLAIN}, {BELOW}"]["amiss over changed"]
            own = ran[f"{PLAIN}, {OWN}"]["amiss over changed"]
            assert 1.08 < below / own < 1.20
    # the table is the look's, entry by entry
    look = json.loads((LAB / "look" / "summary.json").read_text())["worlds"]
    apart = []
    for world in ("still", "busy"):
        for block in ("8", "16"):
            mine = verdict["worlds"][world]["rungs"][block][table]
            theirs = look[world]["changing hands, by a block's past"][block]["chance"]
            for name, row in mine.items():
                seen = theirs["as it is" if name == "the rule as it is" else name]
                apart += [abs(row[near] / seen[near] - 1) for near in (3, 4, 5)]
    assert len(apart) == 84 and sum(a <= 0.10 for a in apart) == 81 and max(apart) <= 0.125
