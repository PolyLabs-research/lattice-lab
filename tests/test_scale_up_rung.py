"""The registered test of the next rung (examples/scale-up-rung/study.py): its design, its
measures on made-up records whose answer is known, and the whole of it end to end on worlds
small enough to run here.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from lattice_lab.ledger import canonical

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-rung"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


STUDY = _load("scale_up_rung_study", LAB / "study.py")
LADDER = STUDY.ladder


def test_the_design():
    plan = STUDY.design()
    assert plan == {"still": {"learn": [18001, 18002, 18003, 18004],
                              "try": [18005, 18006, 18007, 18008]},
                    "busy": {"learn": [18101, 18102, 18103, 18104],
                             "try": [18105, 18106, 18107, 18108]}}  # fmt: skip
    jobs = STUDY.start_jobs(plan)
    assert len(jobs) == 16 and jobs[:4] == [("still", 18001), ("busy", 18101), ("still", 18002),
                                            ("busy", 18102)]  # fmt: skip
    assert (STUDY.SIDE, STUDY.GENERATIONS) == (2048, 16384)
    # the worlds are the first look's two, and step 4e's records of them are where X looks
    assert {w["rule"] for w in STUDY.WORLDS.values()} == {"B245678/S3678", "B23467/S4568"}
    for world in STUDY.WORLDS:
        before = STUDY.before(world)
        assert before.sum() == 8 * 48 * 64 * 64  # eight starts, 48 coarse generations, side 1,024


def test_every_rung_at_the_age_that_matches_its_block():
    ages = STUDY.AGES
    assert ages == {4: (64, 256), 8: (256, 1024), 16: (1024, 4096), 32: (4096, 16384)}
    for block in STUDY.BLOCKS:
        first, last = ages[block]
        tick = LADDER.square(block)
        # four times later and four times longer for a block twice the size, as the clock is
        assert (first, last) == (4 * block * block, 16 * block * block)
        assert (last - first) // tick == 48 and first % block == 0
        if block > 4:
            assert ages[block][0] == ages[block // 2][1]  # each rung starts where the last ends
    # a transition is read every sixteen generations at most, so blocks of 4 and 8 give as many
    seen = {b: len(LADDER.instants(b, LADDER.square(b), *ages[b])) * (STUDY.SIDE // b) ** 2
            for b in STUDY.BLOCKS}  # fmt: skip
    assert seen == {4: 3145728, 8: 3145728, 16: 786432, 32: 196608}


def _made_up(walls: dict, changed: dict | None = None) -> "STUDY.Measures":
    """Records that hold only a world's walls at the ends of each rung's matched age, and (if
    given) what run-ons ended with: by (block, whose rule), blocks amiss and blocks changed."""
    plan = {"still": {"learn": [1], "try": [2]}}
    rows = [{"kind": "start", "world": "still", "seed": seed,
             "walls": {str(b): {str(g): w for g, w in zip(STUDY.AGES[b], walls[b], strict=True)}
                       for b in walls}} for seed in (1, 2)]  # fmt: skip
    for (block, whose), (amiss, moved) in (changed or {}).items():
        rows.append({"kind": "ahead", "world": "still", "seed": 2, "block": block, "rule": whose,
                     "apart_rule": [amiss], "apart_start": [moved], "apart_twin": [0.1],
                     "walls_rule": [0.09], "walls_world": [0.1]})  # fmt: skip
    return STUDY.Measures(rows, plan)


def test_the_measures_on_made_up_records():
    m = _made_up({8: (0.17, 0.09), 16: (0.18, 0.09), 32: (0.165, 0.09)},
                 {(32, STUDY.OWN): (0.10, 0.20), (32, STUDY.BELOW): (0.12, 0.20)})  # fmt: skip
    assert m.same_picture("still") == pytest.approx(0.18 / 0.165 - 1)
    assert m.fits("still", 32) and m.fits("still", 16)
    assert m.amiss("still", 32, STUDY.OWN) == pytest.approx(0.5)
    assert m.amiss("still", 32, STUDY.BELOW) == pytest.approx(0.6)
    assert m.amiss("still", 16, STUDY.OWN) is None  # no run-on on record there

    def value(quantity, **more):
        return m.value({"quantity": quantity, "world": "still", **more})

    assert value("walls at matched ages apart") == pytest.approx(0.0909, abs=1e-4)
    assert value("amiss over changed", block=32, rule=STUDY.BELOW) == pytest.approx(0.6)
    assert value("walls kept", block=32) == pytest.approx(0.9)
    assert value("amiss, the rule from below over the rung's own", block=32) == pytest.approx(1.2)
    with pytest.raises(ValueError):
        value("something else")
    # territories under five blocks across when the rule is started: the run-on is not read
    wide = _made_up({8: (0.17, 0.09), 16: (0.18, 0.09), 32: (0.25, 0.12)})
    assert not wide.fits("still", 32) and wide.fits("still", 16)
    assert not wide.stands({"world": "still", "fits": 32})
    assert wide.stands({"world": "still", "fits": None}) and wide.stands(
        {"world": "still", "fits": 16})  # fmt: skip


def test_the_judge():
    claim = {"at_least": 0.8, "at_most": None}
    assert STUDY.judge(0.84, claim, True) == "holds" and STUDY.judge(0.79, claim, True) == "fails"
    assert STUDY.judge(0.84, claim, False) == STUDY.judge(None, claim, True) == "not tested"
    assert STUDY.judge(float("nan"), claim, True) == "not tested"
    assert STUDY.judge(-0.01, {"at_least": None, "at_most": 0.0}, True) == "holds"
    assert STUDY.judge(0.01, {"at_least": None, "at_most": 0.0}, True) == "fails"
    assert STUDY.number(None) is None and STUDY.number(1 / 3, 2) == 0.33
    assert STUDY.over(1.0, 0.0) is None and STUDY.over(1.0, 4.0) == 0.25


def test_the_claims_the_study_registers():
    claims = STUDY.claims()
    labels = [c["label"] for c in claims]
    assert len(labels) == len(set(labels)) == 22
    by_family = {f: sum(c["family"] == f for c in claims) for f in "SXGHCL"}
    assert by_family == {"S": 2, "X": 2, "G": 4, "H": 2, "C": 4, "L": 8}
    for c in claims:
        assert c["at_least"] is not None or c["at_most"] is not None, c["label"]
        # a run-on is read only through a block that fits, and only run-ons ask it
        assert (c["fits"] is not None) == (c["family"] in "CL"), c["label"]
        assert c["fits"] in (None, c.get("block")) and c["world"] in STUDY.WORLDS
        assert json.loads(json.dumps(c)) == c
    assert STUDY.predictions() == claims


@pytest.fixture
def small(monkeypatch, tmp_path):
    """Both worlds on a grid of side 128 for 1,024 generations, two starts each, the rungs'
    ages shrunk to fit."""
    monkeypatch.setattr(LADDER, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(STUDY, "SIDE", 128)
    monkeypatch.setattr(STUDY, "GENERATIONS", 1024)
    monkeypatch.setattr(STUDY, "STARTS", 2)
    monkeypatch.setattr(STUDY, "AGES", {4: (64, 128), 8: (128, 256), 16: (256, 512),
                                        32: (512, 1024)})  # fmt: skip
    monkeypatch.setattr(STUDY, "RECORDS", tmp_path / "records.jsonl")
    return tmp_path


def test_one_fine_run_on_record(small):
    record = STUDY.run_start(("busy", 18101))
    assert record == STUDY.run_start(("busy", 18101))  # the second time from the leaders kept
    assert (small / "cache" / "rung-busy-128-1024-18101.npz").exists()
    assert json.loads(canonical(record)) == record
    assert set(record["tally"]) == set(record["walls"]) == {"4", "8", "16", "32"}
    for block in STUDY.BLOCKS:
        first, last = STUDY.AGES[block]
        seen = len(LADDER.instants(block, LADDER.square(block), first, last)) * (128 // block) ** 2
        assert LADDER.dense(record["tally"][str(block)]).sum() == seen
        assert set(record["walls"][str(block)]) == {str(first), str(last)}
    # each block is read up to the end of its matched age and no further
    kept = STUDY.fine("busy", 18101)
    assert [kept[b].shape[0] for b in STUDY.BLOCKS] == [33, 33, 33, 33]
    assert kept[32].shape == (33, 4, 4) and kept["shares"].shape == (16, 2)
    # and it is the reading step 4e's own code gives of the same world
    again = LADDER.fine("check", "B23467/S4568", 1.0, 18101, 128, 1024)
    assert np.array_equal(kept[32], again[32]) and np.array_equal(kept[8], again[8][:33])


def test_the_study_end_to_end_on_small_worlds(small):
    path = STUDY.RECORDS
    STUDY.execute(path, 1)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    starts = [r for r in rows if r["kind"] == "start"]
    ahead = [r for r in rows if r["kind"] == "ahead"]
    # two starts of two worlds; at three rungs two rules run on, on each world's one trial start
    assert len(starts) == 4 and len(ahead) == 2 * 3 * 2
    assert {(r["block"], r["rule"]) for r in ahead} == {
        (b, whose) for b in (8, 16, 32) for whose in (STUDY.OWN, STUDY.BELOW)}  # fmt: skip
    for r in ahead:
        first, last = STUDY.AGES[r["block"]]
        assert r["from_generation"] == first and r["tick"] == LADDER.square(r["block"])
        assert r["generations_on"][-1] <= last - first
    STUDY.execute(path, 1)  # run again, it finds everything done
    assert len(path.read_text().splitlines()) == len(rows)
    for record in (starts[0], starts[-1], ahead[0], ahead[-1]):
        assert canonical(STUDY.rerun(record)) == canonical(record)
    with pytest.raises(ValueError):
        STUDY.rerun({**ahead[0], "block": 4})
    claims = STUDY.claims()
    found = STUDY.decide(rows, claims)
    assert found["missing"] == [] and set(found["outcomes"]) == {c["label"] for c in claims}
    assert set(found["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert set(found["verdict"]) == set("SXGHCL") and json.loads(json.dumps(found)) == found
    m = STUDY.Measures(rows, STUDY.design())
    for world, told in found["worlds"].items():
        assert set(told["rungs"]) == {"4", "8", "16", "32"}
        for block in (8, 16, 32):
            rung = told["rungs"][str(block)]
            assert rung["gap: the rule from the rung below, more surprise"] == STUDY.number(
                m.gap(world, block))  # fmt: skip
            assert set(rung["run on, amiss over changed"]) == {STUDY.OWN, STUDY.BELOW}
        assert "run on, amiss over changed" not in told["rungs"]["4"]
    short = STUDY.decide(rows[:-1], claims)
    assert short["missing"] and set(short["outcomes"].values()) == {"missing"}


def test_the_bounds_were_drawn_from_the_first_three_rungs():
    sizing = json.loads((LAB / "sizing.json").read_text())
    assert set(sizing["what the bounds were drawn from"]) == {
        "S, the same picture", "X, another grid", "G, the gap", "H, the chances",
        "C, the new rung", "L, the ladder's own test"}  # fmt: skip
    for world, told in sizing["the first three rungs"].items():
        rungs = told["rungs"]
        starts = [rungs[b]["walls at its start and its end"][0] for b in ("8", "16")]
        starts.append(told["walls at blocks of 32, generation 4,096 (step 4e, side 1,024)"])
        # the same picture at matched ages, and every block fits
        assert max(starts) / min(starts) - 1 < STUDY.SAME_PICTURE, world
        assert max(starts) <= STUDY.BLOCK_FITS
        gap = "gap: the rule from the rung below, more surprise"
        assert STUDY.GAP_AT_16[0] < rungs["16"][gap] < STUDY.GAP_AT_16[1]
        assert rungs["16"][gap] < rungs["8"][gap]  # the gap shrank from the first rung to the next
        assert all(r >= 0.77 for r in told["chance at five, each rung over the one below"])
        assert told["chance at five, each rung over the one below"][1] >= STUDY.LEVELS
        ran = rungs["16"]
        assert ran["run on, amiss over changed"][STUDY.OWN] <= STUDY.WHERE
        assert ran["run on, amiss over changed"][STUDY.BELOW] <= STUDY.BELOW_WHERE
        assert ran["amiss, the rule from below over the rung's own"] <= STUDY.BELOW_OVER_OWN
        assert STUDY.WALLS[0] <= ran["run on, walls kept"][STUDY.OWN] <= STUDY.WALLS[1]


def test_the_registration():
    ledger = LAB / "ledger.jsonl"
    if not ledger.exists():
        pytest.skip("not registered yet")
    entries = [json.loads(line) for line in ledger.read_text().splitlines()]
    question = entries[0]["body"]
    registered = [e["body"] for e in entries if e["kind"] == "prediction"]
    assert entries[0]["kind"] == "question" and len(registered) == 22
    for body, claim in zip(registered, STUDY.claims(), strict=True):
        assert {k: body[k] for k in claim} == claim
    for name, digest in question["sha256"].items():
        assert STUDY.sha(LAB / name) == digest, name
    assert question["runs"] == 16 + 48 and question["side"] == 2048
    assert question["generations"] == 16384


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
