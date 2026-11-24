"""
A rule against a copy of itself, on one grid from one start, and what a set of such contests
says about its rules: the shared design of the sizing look (sizing.py) and of the registered
test (study.py).

Everything here is what examples/scale-up-search/rivals.py does, with the start left open and
the records cut down to what the judge reads: a rule's four contests (the full start and the
half-full one, under the random draw and under the standoff), judged as contests.py judges a
contest, and the rule alone, judged as the screen judges a world.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEARCH = HERE.parent / "scale-up-search"
sys.path.insert(0, str(SEARCH))

import contests  # noqa: E402
import organised  # noqa: E402
import rivals  # noqa: E402
import search  # noqa: E402

SIDE, TIMES = search.SIDE, search.TIMES
DENSITIES = (1.0, 0.5)  # the full start, then the half-full one
KINDS = contests.KINDS


def jobs(rules: list[dict], start: int, alone: bool = True) -> list[tuple]:
    """Every run for a list of rules ({"index", "rule"}): each rule alone (unless told not
    to), then every contest from the full start, then every contest from the half-full one."""
    out: list[tuple] = [("alone", r["index"], r["rule"], start) for r in rules] if alone else []
    for density in DENSITIES:
        for r in rules:
            out += [("contest", r["index"], r["rule"], start, density, kind) for kind in KINDS]
    return out


def key(record: dict) -> tuple:
    """A record as the job that makes it."""
    head = (record["kind"], record["index"], record["rule"], record["start"])
    return head if record["kind"] == "alone" else (*head, record["density"], record["tie_break"])


def run_one(job: tuple) -> dict:
    """One run, as the record kept of it."""
    if job[0] == "alone":
        _, index, rule, start = job
        found = organised.profile([rule], "standoff", SIDE, start, TIMES, density=search.DENSITY)
        told = search.describe({"family": "rule", "index": index, "rules": [rule],
                                "tie_break": "standoff", **found})  # fmt: skip
        return {"kind": "alone", "index": index, "rule": rule, "start": start,
                "called": told["called"], "field": told["field"], "area": told["area"],
                "growth": told["growth"], "live": told["live"], "changed": told["changed"],
                "final_sha256": found["final_sha256"]}  # fmt: skip
    _, index, rule, start, density, kind = job
    found = organised.profile([rule, rule], kind, SIDE, start, TIMES, density=density)
    world = {"family": "copy", "index": index, "rules": [rule, rule], "tie_break": kind,
             "density": density, "source": ""}  # fmt: skip
    told = contests.describe({**world, **found})
    return {"kind": "contest", "index": index, "rule": rule, "start": start, "density": density,
            "tie_break": kind, "verdict": told["verdict"], "shares": told["shares"],
            "apart": told["apart"], "territories": told["territories"],
            "final_sha256": found["final_sha256"]}  # fmt: skip


def entries(records: list[dict]) -> list[dict]:
    """One entry a rule from its contests, as rivals.by_rule gives it: its verdicts, whether it
    holds territories under both tie-breaks, one or neither, and whether it dies in all of
    them. With `alone`, what the screen's judge calls the rule by itself, where that was run."""
    found = [{"rules": [r["rule"], r["rule"]], "index": r["index"], "density": r["density"],
              "tie_break": r["tie_break"], "verdict": r["verdict"],
              "territories": r["territories"]}
             for r in records if r["kind"] == "contest"]  # fmt: skip
    alone = {r["rule"]: r["called"] for r in records if r["kind"] == "alone"}
    out = rivals.by_rule(found)
    for entry in out:
        entry["alone"] = alone.get(entry["rule"])
    return out


def share(group: list[dict], test) -> dict:
    """How many of a group pass a test, and what share of it that is."""
    have = sum(bool(test(entry)) for entry in group)
    return {"of": len(group), "have": have, "share": round(have / len(group), 4) if group else None}


def holds(entry: dict) -> bool:
    return entry["holds"] != "neither"


def birth(entry: dict) -> str:
    """The group a rule is in by the fewest of its own kind a cell needs to be born."""
    least = rivals.least_birth(entry["rule"])
    return {"0": "none", "1": "one", "2": "two or three", "3": "two or three"}.get(
        least, "four or more"
    )


def measure(records: list[dict]) -> dict:
    """Every number the test's claims are about, from a set of records."""
    rules = entries(records)
    by_birth = {name: [e for e in rules if birth(e) == name]
                for name in ("none", "one", "two or three", "four or more")}  # fmt: skip
    middle = by_birth["two or three"]
    lasting = [e for e in middle if rivals.survives_on_few(e["rule"])]
    fragile = [e for e in middle if not rivals.survives_on_few(e["rule"])]
    holders = [e for e in rules if holds(e)]
    screened = [e for e in rules if e["alone"] is not None]
    out = {
        "rules": len(rules),
        "all": share(rules, holds),
        "birth": {name: share(group, holds) for name, group in by_birth.items()},
        "cannot last on one or two": share(fragile, holds),
        "can last on one or two": share(lasting, holds),
        "needs its own kind and lives": share([e for e in fragile if not e["dies"]], holds),
        "needs its own kind and dies in every contest": sum(e["dies"] for e in fragile),
        "holds": {name: sum(e["holds"] == name for e in rules) for name in rivals.HOLDS},
        "growing": sum(e["growing"] for e in rules),
        "holders, patches alone": share([e for e in holders if e["alone"] is not None],
                                        lambda e: e["alone"] == "patches"),
        "grow alone": share([e for e in screened if e["alone"] == "growing"], holds),
        "organise alone": share([e for e in screened if e["alone"] in ("organised", "growing")],
                                holds),
        "alone": {call: sum(e["alone"] == call for e in screened)
                  for call in ("dead", "patches", "organised", "growing")},
    }  # fmt: skip
    return out
