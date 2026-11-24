"""The registered test of which rules hold territories against a copy of themselves
(examples/scale-up-territories): its rules, what it registers, and how a claim is judged.

The judge is tried on made-up contests whose answer is known, and the whole study on a handful
of rules on a grid of side 64.
"""

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest
from scipy import stats

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, load, register, run

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "examples" / "scale-up-territories"
DASHBOARDS = ROOT / "examples" / "qec-census-4" / "dashboards"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


S = _load("scale_up_territories_study", LAB / "study.py")
T = S.territories

FOUR = [(density, kind) for density in (1.0, 0.5) for kind in ("random", "standoff")]


# --- the rules -----------------------------------------------------------------------------------


def test_the_rules_are_fresh():
    """600 rules of the screen's own draw that no run has used, and for the second cut the
    rules that need two or three for a birth among the 1,200 drawn after them."""
    rules, more = S.fresh(), S.further()
    assert len(rules) == 600 and len({r["rule"] for r in rules}) == 600
    assert rules[0] == {"index": 1201, "rule": S.search.random_rule(1201)}
    assert all(r["rule"] == S.search.random_rule(r["index"]) for r in rules + more)
    assert [r["index"] for r in rules] == sorted(r["index"] for r in rules)
    used = S.seen()
    assert not used & {r["rule"] for r in rules + more}
    # what has been used: the screen's draws, the near-majority draws, the known worlds, the
    # soups' species, the rules of the contests and the rules a count away from them
    assert {S.search.random_rule(1), S.search.near_majority(1), "B3/S23", "B4678/S35678"} <= used
    assert {"B2378/S25678", "B015/S1", "B2/S0", "B238/S25678"} <= used
    assert len(more) == 242 and not {r["rule"] for r in rules} & {r["rule"] for r in more}
    assert {T.birth(r) for r in more} == {"two or three"}
    assert min(r["index"] for r in more) > max(r["index"] for r in rules)
    assert S.groups(rules) == {
        "none": 292, "one": 148, "two or three": 117, "four or more": 43,
        "two or three, cannot last on one or two": 31,
        "two or three, can last on one or two": 86,
    }  # fmt: skip
    wider = S.groups(rules + more)
    assert wider["two or three"] == 359
    assert wider["two or three, cannot last on one or two"] == 102


def test_every_run_of_the_test():
    jobs = S.jobs()
    assert len(jobs) == len(set(jobs)) == 600 * 5 + 242 * 4 == 3968
    assert {job[3] for job in jobs} == {14001}  # one start, which no run has used
    alone = [job for job in jobs if job[0] == "alone"]
    assert jobs[:600] == alone and len(alone) == 600  # the further rules are not run alone
    first = S.fresh()[0]
    mine = [job for job in jobs if job[2] == first["rule"]]
    assert mine[0] == ("alone", 1201, first["rule"], 14001)
    assert [job[4:] for job in mine[1:]] == FOUR
    record = {"kind": "contest", "index": 1201, "rule": first["rule"], "start": 14001,
              "density": 0.5, "tie_break": "standoff", "verdict": "mixed"}  # fmt: skip
    assert T.key(record) == ("contest", 1201, first["rule"], 14001, 0.5, "standoff") in jobs
    assert T.key({"kind": "alone", "index": 1201, "rule": first["rule"], "start": 14001}) in jobs


# --- one run -------------------------------------------------------------------------------------


@pytest.fixture
def small(monkeypatch):
    """The design on a grid of side 64 for 64 generations."""
    monkeypatch.setattr(T, "SIDE", 64)
    monkeypatch.setattr(T, "TIMES", (8, 16, 32, 64))


def test_one_run_is_the_record_kept_of_it(small):
    job = ("contest", 7, "B2378/S25678", 9001, 1.0, "standoff")
    record = T.run_one(job)
    assert T.key(record) == job and T.run_one(job) == record
    assert set(record) == {"kind", "index", "rule", "start", "density", "tie_break", "verdict",
                           "shares", "apart", "territories", "final_sha256"}  # fmt: skip
    assert record["verdict"] in S.contests.VERDICTS and len(record["territories"]) == 2
    assert len(record["final_sha256"]) == 64 and len(record["shares"]) == 2
    assert json.loads(json.dumps(record)) == record
    alone = T.run_one(("alone", 7, "B2378/S25678", 9001))
    assert alone["kind"] == "alone" and alone["called"] in ("dead", "patches", "organised",
                                                             "growing")  # fmt: skip
    assert T.key(alone) == ("alone", 7, "B2378/S25678", 9001)
    assert S.rerun(record) == record and S.rerun(alone) == alone
    # another start is another world
    assert T.run_one((*job[:3], 9002, *job[4:]))["final_sha256"] != record["final_sha256"]


# --- the judge, on made-up contests --------------------------------------------------------------


def _rows(rule, index, verdicts, alone="patches", start=14001):
    """A rule's records: its four contests with these verdicts (a word for all four, or four
    words in the order of FOUR), and the rule alone unless `alone` is None."""
    if isinstance(verdicts, str):
        verdicts = [verdicts] * 4
    territory = {"called": "growing", "area": 100.0, "scaling": 1.0, "growth": 0.5}
    out = [{"kind": "contest", "index": index, "rule": rule, "start": start, "density": density,
            "tie_break": kind, "verdict": verdict, "shares": [0.25, 0.25], "apart": -0.99,
            "territories": [territory] * 2, "final_sha256": "0" * 64}
           for (density, kind), verdict in zip(FOUR, verdicts, strict=True)]  # fmt: skip
    if alone is not None:
        out.append({"kind": "alone", "index": index, "rule": rule, "start": start,
                    "called": alone})  # fmt: skip
    return out


GROWS, MIXED, DEAD = "growing territories", "mixed", "dead"
ONLY_STANDOFF = [MIXED, GROWS, MIXED, MIXED]
ONLY_DRAW = [GROWS, MIXED, MIXED, MIXED]


def test_what_a_set_of_contests_says_about_its_rules():
    rows = (
        _rows("B0/S2", 1, MIXED)                        # born on none
        + _rows("B1/S2", 2, ONLY_STANDOFF)              # on one: holds, under the standoff only
        + _rows("B2/S0", 3, GROWS)                      # on two, cannot last on one or two
        + _rows("B3/S4", 4, DEAD)                       # on three, cannot last, dies everywhere
        + _rows("B3/S12", 5, MIXED, alone="growing")    # on three, can last
        + _rows("B23/S2", 6, ONLY_DRAW, alone="organised")  # on two, can last, the draw only
        + _rows("B45/S5", 7, MIXED, alone="dead")       # on four or more
        + _rows("B/S23", 8, "standing territories")     # no births: with four or more
    )  # fmt: skip
    found = T.measure(rows)
    assert found["rules"] == 8 and found["all"] == {"of": 8, "have": 4, "share": 0.5}
    assert found["birth"] == {
        "none": {"of": 1, "have": 0, "share": 0.0},
        "one": {"of": 1, "have": 1, "share": 1.0},
        "two or three": {"of": 4, "have": 2, "share": 0.5},
        "four or more": {"of": 2, "have": 1, "share": 0.5},
    }
    assert found["cannot last on one or two"] == {"of": 2, "have": 1, "share": 0.5}
    assert found["can last on one or two"] == {"of": 2, "have": 1, "share": 0.5}
    assert found["needs its own kind and lives"] == {"of": 1, "have": 1, "share": 1.0}
    assert found["needs its own kind and dies in every contest"] == 1
    assert found["holds"] == {"both": 2, "standoff only": 1, "draw only": 1, "neither": 4}
    assert found["growing"] == 3  # the standing territories are held, not growing
    assert found["organise alone"] == {"of": 2, "have": 1, "share": 0.5}
    assert found["grow alone"] == {"of": 1, "have": 0, "share": 0.0}
    assert found["alone"] == {"dead": 1, "patches": 5, "organised": 1, "growing": 1}
    numbers = S.quantities(found, found)
    assert numbers["all"] == {"value": 0.5, "of": 8, "have": 4}
    assert numbers["two or three over one"] == {"value": -0.5, "of": 1, "shares": [0.5, 1.0]}
    assert numbers["one over none"]["value"] == 1.0
    assert numbers["cannot last over can"] == {"value": 0.0, "of": 2, "shares": [0.5, 0.5]}
    assert numbers["standoff only, of one tie-break only"] == {"value": 0.5, "of": 2, "have": 1}
    assert numbers["organise alone"]["value"] == 0.5
    assert set(numbers) == {claim[2] for claim in S.CLAIMS}
    # a rule that was not run alone is left out of what is said of rules alone
    more = T.measure(rows + _rows("B2/S", 9, GROWS, alone=None))
    assert more["rules"] == 9 and more["alone"] == found["alone"]
    assert more["holders, patches alone"]["of"] == 4
    empty = S.quantities(T.measure(_rows("B0/S2", 1, MIXED)), T.measure([]))
    assert empty["cannot last over can"] == {"value": None, "of": 0}
    assert empty["standoff only, of one tie-break only"] == {"value": None, "of": 0, "have": 0}


def test_a_claim_holds_fails_or_is_not_tested():
    found = {"value": 0.25, "of": 40}
    assert S.judge(found, 0.25, None, 20) == "holds" and S.judge(found, 0.26, None, 20) == "fails"
    assert S.judge(found, None, 0.25, 20) == "holds" and S.judge(found, None, 0.24, 20) == "fails"
    assert S.judge(found, 0.11, 0.24, 20) == "fails" and S.judge(found, 0.11, 0.26, 20) == "holds"
    # too few rules to say, or none at all
    assert S.judge(found, 0.99, None, 41) == "not tested"
    assert S.judge({"value": None, "of": 0}, 0.1, None, 0) == "not tested"
    # two thirds, written as a fraction, is on the bound
    assert S.judge({"value": round(30 / 45, 4), "of": 45}, 2 / 3, None, 15) == "holds"


def _made_up(monkeypatch, standoff_only=9, draw_only=2):
    """Sixty made-up rules whose contests come out as the screen's did, in small."""

    def rules(birth, survive, count, first):
        return [{"index": first + i, "rule": f"B{birth}{'8' * (i % 2)}/S{survive}"}
                for i in range(count)]  # fmt: skip

    groups = [  # rules, and how many of them hold
        (rules("0", "23", 2, 0) + rules("03", "5", 2, 2) + rules("04", "6", 2, 4)
         + rules("05", "7", 2, 6) + rules("06", "23", 2, 8), 0),            # none: 0 of 10
        (rules("1", "3", 2, 10) + rules("13", "4", 2, 12) + rules("14", "5", 2, 14)
         + rules("15", "6", 2, 16) + rules("16", "7", 2, 18), 2),           # one: 2 of 10
        (rules("2", "0", 2, 20) + rules("3", "4", 2, 22) + rules("23", "5", 2, 24)
         + rules("24", "6", 2, 26) + rules("35", "7", 2, 28), 9),           # cannot last: 9 of 10
        (rules("2", "1", 2, 30) + rules("3", "2", 2, 32) + rules("23", "12", 2, 34)
         + rules("24", "15", 2, 36) + rules("35", "26", 2, 38), 5),         # can last: 5 of 10
        (rules("4", "5", 2, 40) + rules("5", "5", 2, 42) + rules("6", "6", 2, 44)
         + rules("7", "7", 2, 46) + rules("45", "8", 2, 48), 0),            # four or more: 0 of 10
    ]  # fmt: skip
    listed = [r for group, _ in groups for r in group]
    assert len({r["rule"] for r in listed}) == 50
    monkeypatch.setattr(S, "fresh", lambda: listed)
    monkeypatch.setattr(S, "further", lambda: [])
    rows, single = [], [ONLY_STANDOFF] * standoff_only + [ONLY_DRAW] * draw_only
    for group, holding in groups:
        for i, rule in enumerate(group):
            if i < holding:
                verdicts = single.pop(0) if single else GROWS
            else:
                verdicts = MIXED
            alone = "growing" if rule["index"] % 10 == 9 else "patches"
            rows += _rows(rule["rule"], rule["index"], verdicts, alone=alone)
    return rows


def _eased(needs=5):
    """The registered claims, with groups of five or more allowed."""
    return [{**claim, "needs": min(claim["needs"], needs)} for claim in S.predictions()]


def test_the_judge_passes_rules_that_are_like_the_screens(monkeypatch):
    rows = _made_up(monkeypatch)
    verdict = S.decide(rows, _eased())
    assert verdict["missing"] == 0 and set(verdict["outcomes"]) == {c[0] for c in S.CLAIMS}
    assert verdict["verdict"] == {"A": "holds", "B": "holds", "K": "holds", "L": "holds",
                                  "R": "fails"}  # fmt: skip
    numbers = verdict["quantities"]
    assert numbers["R1"]["value"] == 0.32  # 16 of 50: more than the band, in this made-up set
    assert numbers["B1"]["value"] == 0.0 and numbers["B2"]["value"] == 0.7
    assert numbers["B3"]["value"] == 0.0 and numbers["B4"]["value"] == 0.5
    assert numbers["B5"]["value"] == 0.2 and numbers["L1"]["value"] == 0.4
    assert numbers["L2"] == {"value": 0.9, "of": 10, "have": 9}
    assert numbers["K1"] == {"value": round(9 / 11, 4), "of": 11, "have": 9}
    assert numbers["A1"] == {"value": 0.0, "of": 5, "have": 0}
    assert verdict["measured"]["rules"] == 50
    assert verdict["measured for the second cut"]["rules"] == 20
    # with the registered sizes most of these groups are too small to say anything
    strict = S.decide(rows, S.predictions())
    assert strict["outcomes"] == {
        "R1": "not tested", "B1": "not tested", "B2": "holds", "B3": "not tested",
        "B4": "not tested", "B5": "not tested", "L1": "not tested", "L2": "holds",
        "K1": "not tested", "A1": "not tested",
    }  # fmt: skip
    # a family holds if a claim of it does and none fails
    assert strict["verdict"] == {"A": "not tested", "B": "holds", "K": "not tested",
                                 "L": "holds", "R": "not tested"}  # fmt: skip


def test_the_judge_fails_what_is_not_so(monkeypatch):
    # the tie-break: as many under the draw only as under the standoff only
    even = S.decide(_made_up(monkeypatch, standoff_only=5, draw_only=5), _eased())
    assert even["outcomes"]["K1"] == "fails" and even["verdict"]["K"] == "fails"
    assert {k for k, word in even["outcomes"].items() if word == "fails"} == {"K1", "R1"}
    # rules born on no neighbours that hold territories after all
    rows = _made_up(monkeypatch)
    for row in rows:
        if row["kind"] == "contest" and row["index"] < 2:
            row["verdict"] = GROWS
    wrong = S.decide(rows, _eased())
    assert wrong["quantities"]["B1"]["value"] == 0.2 and wrong["outcomes"]["B1"] == "fails"
    assert wrong["outcomes"]["B5"] == "fails" and wrong["verdict"]["B"] == "fails"
    assert wrong["outcomes"]["B2"] == "holds" and wrong["verdict"]["L"] == "holds"
    # the second cut: the rules that cannot last hold no more often than those that can
    rows = _made_up(monkeypatch)
    for row in rows:
        if row["kind"] == "contest" and 23 <= row["index"] < 29:
            row["verdict"] = MIXED
    level = S.decide(rows, _eased())
    assert level["quantities"]["L1"]["value"] == -0.2 and level["outcomes"]["L1"] == "fails"
    assert level["outcomes"]["L2"] == "fails" and level["verdict"]["L"] == "fails"
    # every rule that grows alone holds territories
    rows = _made_up(monkeypatch)
    for row in rows:
        if row["kind"] == "contest" and row["index"] % 10 == 9:
            row["verdict"] = GROWS
    guess = S.decide(rows, _eased())
    assert guess["quantities"]["A1"]["value"] == 1.0 and guess["outcomes"]["A1"] == "fails"


def test_a_run_cut_short_is_missing(monkeypatch):
    rows = _made_up(monkeypatch)
    verdict = S.decide(rows[:-1], _eased())
    assert verdict["missing"] == 1 and set(verdict["outcomes"].values()) == {"missing"}
    assert verdict["verdict"] == dict.fromkeys("ABKLR", "missing")
    assert "measured" not in verdict


def test_the_second_cut_is_judged_on_the_further_rules_too(monkeypatch):
    rows = _made_up(monkeypatch)
    extra = [{"index": 100 + i, "rule": f"B2{i + 4}/S0{i + 3}"} for i in range(4)]
    monkeypatch.setattr(S, "further", lambda: extra)
    assert all(T.birth(r) == "two or three" for r in extra)
    assert len(S.jobs()) == 50 * 5 + 4 * 4
    for rule in extra:  # none of the four holds, and none is run alone
        rows += _rows(rule["rule"], rule["index"], MIXED, alone=None)
    verdict = S.decide(rows, _eased())
    assert verdict["missing"] == 0 and verdict["measured"]["rules"] == 50
    assert verdict["measured for the second cut"]["rules"] == 24
    assert verdict["quantities"]["L2"] == {"value": round(9 / 14, 4), "of": 14, "have": 9}
    assert verdict["quantities"]["B2"]["value"] == 0.7  # the first cut on the fifty alone


# --- what is registered --------------------------------------------------------------------------


def test_what_is_registered():
    claims = S.predictions()
    assert [c["label"] for c in claims] == ["R1", "B1", "B2", "B3", "B4", "B5", "L1", "L2", "K1",
                                           "A1"]  # fmt: skip
    assert [c["family"] for c in claims] == list("RBBBBBLLKA")
    assert all(len(c["claim"]) < 240 for c in claims)
    assert all((c["at_least"] is None) != (c["at_most"] is None) for c in claims[1:])
    assert (claims[0]["at_least"], claims[0]["at_most"]) == (0.11, 0.24)
    bounds = {c["label"]: c["at_least"] if c["at_most"] is None else c["at_most"]
              for c in claims[1:]}  # fmt: skip
    assert bounds == {"B1": 0.10, "B2": 0.40, "B3": 0.08, "B4": 0.20, "B5": 0.03, "L1": 0.10,
                      "L2": 0.70, "K1": 2 / 3, "A1": 0.35}  # fmt: skip
    question = S.question()
    assert question["id"] == "scale-up-territories" and question["runs"] == 3968
    assert question["start"] == 14001 and question["rules"]["count"] == 600
    assert question["rules"]["first"]["index"] == 1201
    assert question["further_rules"]["kept"] == 242
    assert question["world"] == {
        "side": 256, "generations": 512, "read_at": [32, 64, 128, 256, 512],
        "starts": [1.0, 0.5], "tie_breaks": ["random", "standoff"],
    }  # fmt: skip
    assert len(question["excluded_seen"]) == 4 and set(question["sha256"]) == {
        "study.py", "territories.py", "organised.py", "search.py", "contests.py", "rivals.py",
    }  # fmt: skip
    assert set(S.SCREEN) == {c["quantity"] for c in claims}


def test_the_bounds_sit_between_the_screen_and_nothing():
    """Each claim's chance of passing, if the fresh rules are like the screen's and if the cut
    it tests were worth nothing."""
    design = S.design()
    claims = design["claims"]
    assert design["groups"]["two or three"] == 117
    assert design["groups for the second cut"]["two or three, cannot last on one or two"] == 102
    assert all(row["passes if like the screen"] > 0.98 for row in claims.values())
    # a cut worth nothing passes its claim one time in twenty or less, B5 one in eight
    worthless = {label: row["passes if worth nothing"] for label, row in claims.items()
                 if "passes if worth nothing" in row and label != "A1"}  # fmt: skip
    assert set(worthless) == {"B1", "B2", "B3", "B4", "B5", "L1", "L2", "K1"}
    assert max(v for k, v in worthless.items() if k != "B5") < 0.06 and worthless["B5"] < 0.13
    # A1 cannot tell "no likelier" from "less likely": what it can refuse is the first guess
    assert claims["A1"]["passes if worth nothing"] > 0.95
    assert claims["A1"]["passes if one in two of them held"] < 0.15
    # the screen's own numbers
    assert S.SCREEN["birth on two or three"][0] == round(132 / 241, 3)
    assert S.SCREEN["needs its own kind and lives"] == (round(44 / 47, 3), round(132 / 223, 3))
    assert S.SCREEN["standoff only, of one tie-break only"][0] == round(77 / 90, 3)


def test_the_chances_are_binomial():
    assert math.isclose(S.chance(0.3, 20, 0.25, None), stats.binom.sf(4, 20, 0.3))
    assert math.isclose(S.chance(0.3, 20, None, 0.25), stats.binom.cdf(5, 20, 0.3))
    assert math.isclose(S.chance(0.5, 10, 0.3, 0.6), stats.binom.cdf(6, 10, 0.5)
                        - stats.binom.cdf(2, 10, 0.5))  # fmt: skip
    assert S.chance(0.5, 10, 0.75, 0.72) == 0.0
    # a difference of two shares, against counting every case
    exact = sum(stats.binom.pmf(a, 6, 0.7) * stats.binom.pmf(b, 4, 0.2)
                for a in range(7) for b in range(5) if a / 6 - b / 4 >= 0.25 - 1e-9)  # fmt: skip
    assert math.isclose(S.chance_over((0.7, 6), (0.2, 4), 0.25), exact)
    assert math.isclose(S.chance_over((0.5, 5), (0.5, 5), 0.0), 1 - (1 - sum(
        stats.binom.pmf(k, 5, 0.5) ** 2 for k in range(6))) / 2)  # fmt: skip


# --- the whole study, on a small grid ------------------------------------------------------------


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def test_the_study_registers_runs_and_judges_on_a_small_grid(monkeypatch, tmp_path, small):
    monkeypatch.setattr(S, "RULES", 6)
    monkeypatch.setattr(S, "MORE", 12)
    monkeypatch.setattr(S, "START", 9001)
    rules, more = S.fresh(), S.further()
    assert len(rules) == 6 and all(T.birth(r) == "two or three" for r in more)
    _git(tmp_path, "init", "-q")
    study = Study(tmp_path, S.question, S.predictions, S.execute, S.decide, rerun=S.rerun)
    assert len(register(study)) == 11
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study, workers=1)
    assert set(verdict["verdict"]) == set("ABKLR") and verdict["missing"] == 0
    assert set(verdict["outcomes"]) == {c[0] for c in S.CLAIMS}
    assert set(verdict["outcomes"].values()) <= {"holds", "fails", "not tested"}
    assert verdict["outcomes"]["R1"] == "not tested"  # six rules are too few to say
    assert verdict["measured"]["rules"] == 6
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    rows = ledger.entries[-2]["body"]["rows"]
    assert len(rows) == 6 * 5 + len(more) * 4
    assert [r["kind"] for r in rows[:6]] == ["alone"] * 6
    assert S.rerun(rows[0]) == rows[0] and S.rerun(rows[-1]) == rows[-1]
    # running again adds nothing: every run is already recorded
    before = (tmp_path / "records.jsonl").read_text()
    study.execute(tmp_path / "records.jsonl", 1)
    assert (tmp_path / "records.jsonl").read_text() == before
    # the census dashboards' reader gives each prediction its outcome
    readers = _load("census_dashboards_studies", DASHBOARDS / "studies.py")
    bodies = [e["body"] for e in ledger.entries if e["kind"] == "prediction"]
    table, summary = readers.READERS["scale-up-territories"](bodies, verdict, {})
    assert [r["label"] for r in table] == [b["label"] for b in bodies]
    assert {r["outcome"] for r in table} <= {"held", "failed", "not tested"}
    assert summary.startswith("A ")


def test_the_ledger_holds_the_registration():
    path = LAB / "ledger.jsonl"
    if not path.exists():
        pytest.skip("not registered yet")
    ledger = Ledger(path)
    assert ledger.verify() == [] and check_order(ledger, LAB) == []
    claims = S.predictions()
    kinds = [e["kind"] for e in ledger.entries]
    assert kinds[:11] == ["question"] + ["prediction"] * 10
    question = ledger.entries[0]
    for entry, claim in zip(ledger.entries[1:11], claims, strict=True):
        assert entry["body"] == {"question": question["hash"], **claim}
    if "verdict" not in kinds:  # between registration and the run, the code must not move
        assert question["body"]["sha256"] == S.question()["sha256"]


def test_verify_can_rerun_the_studys_records():
    assert load(LAB).rerun is not None
