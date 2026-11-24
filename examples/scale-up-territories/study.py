"""
A registered test: which rules hold territories against a copy of themselves?

    uv run --no-sync python examples/scale-up-territories/study.py register
    uv run --no-sync python examples/scale-up-territories/study.py run --workers 2
    uv run --no-sync lattice-lab verify --lab examples/scale-up-territories

**Why.** The search for a world that organises itself (examples/scale-up-search, step 4b of
docs/scale-up-plan.md) set every one of 1,196 randomly drawn rules against a copy of itself:
two species with the one rule, each counting only its own kind. 202 of them sorted into
territories. Two cuts were then read off those same runs. Territories go with how few of its
own kind a cell needs to be born: 5% of the rules that need none, 15% of those that need one,
55% of those that need two or three, 1% of those that need four or more. And among the rules
that need two or three, they go with whether a cell can last on one or two of its own kind:
77% of the rules where it cannot, 48% where it can. A pattern read off data looks better the
longer one looks, and the second cut has been tried on no rule it was not read from. This
tries both on rules that no run has used.

**What is run.** 600 fresh rules: the same even draw the screen used (every neighbour count
in the birth set, and in the survival set, with chance one half), from number 1,201 on,
leaving out any rule an earlier run of the search has used alone, in a soup or against a
rival. Each rule is run as the wider screen ran its rules (`territories.py`): alone from a
half-full start, and against a copy of itself from a full start and a half-full one, under
the random draw and under the standoff, on a wrapped square grid of side 256 for 512
generations. Every run begins from start 14001, which no run has used. The screen used 11001
throughout, so before these bounds were drawn `sizing.py` ran 200 of its rules again from a
second start: 199 held territories or not as they had, and 791 of the 800 contests came to
the same verdict. A rule's verdict is the rule's, not its start's.

The second cut lives among the rules that need two or three for a birth, and 600 rules hold
117 of them, 31 on its smaller side: too few to tell a real difference from none. So the
draw goes on for 1,200 fresh rules more, and of those the 242 that need two or three for a
birth meet their copies as well (they are not run alone). The second cut is judged on all
359 such rules; everything else on the 600. In all, 3,968 runs.

**A rule holds territories** if in at least one of its four contests both species hold
ground at the end (a cell in twenty each), their counts in a block go against each other (a
correlation of -0.5 or under over blocks of 32), and one of them has a correlation area of 16
cells or more at blocks of 32: the judge of examples/scale-up-search/contests.py, unchanged.

**Predictions**, ten, in five families (`CLAIMS`). Each is a share of a group of the fresh
rules, or a difference of two such shares, set against a bound:

    R  how common territories are over all the rules
    B  the first cut: the fewest of its own kind a cell needs to be born
    L  the second cut: whether a cell can last on one or two of its own kind
    K  the tie-break: rules that hold under one only hold mostly under the standoff
    A  alone: a rule that organises itself alone is no likelier to hold territories

A claim holds if its number is on the right side of its bound, fails if it is not, and is
**not tested** if its group has fewer rules than the claim names: a bound on a share of
three rules says nothing. The groups by a rule's counts are known before any run (they are
in the question, with the chance each claim has of passing if the fresh rules are like the
screen's and if the cut were worth nothing); the groups that depend on the runs are the
rules that live, the rules that hold under one tie-break only, and the rules that organise
alone.

**What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import territories  # noqa: E402
from territories import SEARCH, contests, rivals, search  # noqa: E402

sys.path.insert(0, str(HERE.parent / "scale-up-compete"))
from first_look import soup_rules  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

RULES, MORE, FIRST, START = 600, 1200, 1201, 14001

# label, family, the quantity (see `quantities`), at least, at most, the fewest rules its group
# may have, and the claim in words
CLAIMS = (
    ("R1", "R", "all", 0.11, 0.24, 100,
     "of all the fresh rules, between 11% and 24% hold territories against their copy"),
    ("B1", "B", "birth on none", None, 0.10, 20,
     "of the rules a cell of which is born with none of its own kind around it, at most 10% "
     "hold territories"),
    ("B2", "B", "birth on two or three", 0.40, None, 20,
     "of the rules that need two or three of their own kind for a birth, at least 40% hold "
     "territories"),
    ("B3", "B", "birth on four or more", None, 0.08, 20,
     "of the rules that need four or more of their own kind for a birth, or have no births, "
     "at most 8% hold territories"),
    ("B4", "B", "two or three over one", 0.20, None, 20,
     "the share of rules holding territories is higher by 0.20 or more among those that need "
     "two or three for a birth than among those that need one"),
    ("B5", "B", "one over none", 0.03, None, 20,
     "the share of rules holding territories is higher by 0.03 or more among those that need "
     "one of their own kind for a birth than among those that need none"),
    ("L1", "L", "cannot last over can", 0.10, None, 15,
     "among the rules that need two or three for a birth, the share holding territories is "
     "higher by 0.10 or more where a cell does not survive on one or two of its own kind than "
     "where it does"),
    ("L2", "L", "needs its own kind and lives", 0.70, None, 10,
     "of the rules that need two or three for a birth, whose cells do not survive on one or "
     "two, and that do not die in every one of their contests, at least 70% hold territories"),
    ("K1", "K", "standoff only, of one tie-break only", 2 / 3, None, 15,
     "of the rules that hold territories under one tie-break and not the other, at least two "
     "in three hold them under the standoff"),
    ("A1", "A", "organise alone", None, 0.35, 10,
     "of the rules that the screen's judge calls organised or growing when they are alone, "
     "at most 35% hold territories against their copy"),
)  # fmt: skip

# What the screen's 1,196 rules gave for each quantity (examples/scale-up-search/rivals), and
# what the quantity would be if the cut it tests were worth nothing: the base the bounds were
# set between.
SCREEN = {
    "all": (0.169, None),
    "birth on none": (0.047, 0.169),
    "birth on two or three": (0.548, 0.169),
    "birth on four or more": (0.012, 0.169),
    "two or three over one": (0.401, 0.0),
    "one over none": (0.100, 0.0),
    "cannot last over can": (0.294, 0.0),
    "needs its own kind and lives": (0.936, 0.592),
    "standoff only, of one tie-break only": (0.856, 0.5),
    "organise alone": (0.065, 0.169),
}


def seen() -> set[str]:
    """Every rule an earlier run of the search has used: alone, in a soup, or against a rival."""
    out = {search.random_rule(i) for i in search.RULES}
    out |= {search.near_majority(i) for i in search.NEAR}
    out |= {rule for _, rules in search.KNOWN.values() for rule in rules}
    out |= {rule for species, numbers in search.SOUPS.items()
            for number in numbers for rule in soup_rules(number, species)}  # fmt: skip
    best = json.loads((SEARCH / "contests" / "summary.json").read_text())["rules"]
    out |= {grower["rule"] for grower in best}
    out |= {near for grower in best for near in contests.neighbours(grower["rule"])}
    return out


def drawn(count: int) -> list[dict]:
    """The first `count` different rules of the even draw, from number FIRST on, that no
    earlier run has used."""
    used = seen()
    out: list[dict] = []
    index = FIRST
    while len(out) < count:
        rule = search.random_rule(index)
        if rule not in used:
            used.add(rule)
            out.append({"index": index, "rule": rule})
        index += 1
    return out


def fresh() -> list[dict]:
    """The rules of the test: the first RULES fresh rules of the draw."""
    return drawn(RULES)


def further() -> list[dict]:
    """Of the MORE fresh rules that follow, those that need two or three of their own kind
    for a birth: the rules the second cut is about."""
    return [r for r in drawn(RULES + MORE)[RULES:] if territories.birth(r) == "two or three"]


def jobs() -> list[tuple]:
    return territories.jobs(fresh(), START) + territories.jobs(further(), START, alone=False)


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {territories.key(r) for r in map(json.loads, path.read_text().splitlines())}
    todo = [job for job in jobs() if job not in done]
    if workers <= 1:
        for job in todo:
            append_records(path, [territories.run_one(job)])
        return
    with ProcessPoolExecutor(workers) as pool:
        for record in pool.map(territories.run_one, todo, chunksize=4):
            append_records(path, [record])


# --- the numbers the claims are about ------------------------------------------------------------


def quantities(measured: dict, second: dict) -> dict[str, dict]:
    """Each claim's number, with its value (None if a group is empty) and the size of the
    smallest group it rests on. `measured` is `territories.measure` of the 600 rules' records;
    `second` the same of every rule that needs two or three for a birth, the 600's and the
    further ones, which the second cut is judged on."""

    def one(found: dict) -> dict:
        return {"value": found["share"], "of": found["of"], "have": found["have"]}

    def over(first: dict, second: dict) -> dict:
        if not first["of"] or not second["of"]:
            return {"value": None, "of": min(first["of"], second["of"])}
        return {"value": round(first["share"] - second["share"], 4),
                "of": min(first["of"], second["of"]),
                "shares": [first["share"], second["share"]]}  # fmt: skip

    birth, held = measured["birth"], measured["holds"]
    single = held["standoff only"] + held["draw only"]
    return {
        "all": one(measured["all"]),
        "birth on none": one(birth["none"]),
        "birth on two or three": one(birth["two or three"]),
        "birth on four or more": one(birth["four or more"]),
        "two or three over one": over(birth["two or three"], birth["one"]),
        "one over none": over(birth["one"], birth["none"]),
        "cannot last over can": over(second["cannot last on one or two"],
                                     second["can last on one or two"]),
        "needs its own kind and lives": one(second["needs its own kind and lives"]),
        "standoff only, of one tie-break only": {
            "value": round(held["standoff only"] / single, 4) if single else None,
            "of": single, "have": held["standoff only"]},
        "organise alone": one(measured["organise alone"]),
    }  # fmt: skip


def judge(found: dict, at_least: float | None, at_most: float | None, needs: int) -> str:
    """holds, fails, or not tested where the group is too small to say."""
    if found["value"] is None or found["of"] < needs:
        return "not tested"
    low = at_least is None or found["value"] >= at_least - 1e-12
    high = at_most is None or found["value"] <= at_most + 1e-12
    return "holds" if low and high else "fails"


def predictions() -> list[dict]:
    return [{"label": label, "family": family, "quantity": quantity, "at_least": at_least,
             "at_most": at_most, "needs": needs, "claim": claim}
            for label, family, quantity, at_least, at_most, needs, claim in CLAIMS]  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    have = {territories.key(r) for r in rows}
    missing = [job for job in jobs() if job not in have]
    families = sorted({claim["family"] for claim in registered})
    if missing:
        return {"verdict": dict.fromkeys(families, "missing"),
                "outcomes": {claim["label"]: "missing" for claim in registered},
                "missing": len(missing)}  # fmt: skip
    main = {r["rule"] for r in fresh()}
    middle = {r["rule"] for r in further()} | {
        r["rule"] for r in fresh() if territories.birth(r) == "two or three"
    }
    measured = territories.measure([r for r in rows if r["rule"] in main])
    second = territories.measure([r for r in rows if r["rule"] in middle])
    found = quantities(measured, second)
    outcomes = {claim["label"]: judge(found[claim["quantity"]], claim["at_least"],
                                      claim["at_most"], claim["needs"])
                for claim in registered}  # fmt: skip

    def overall(family: str) -> str:
        words = {outcomes[c["label"]] for c in registered if c["family"] == family}
        return "fails" if "fails" in words else "holds" if "holds" in words else "not tested"

    return {
        "verdict": {family: overall(family) for family in families},
        "outcomes": outcomes,
        "quantities": {claim["label"]: found[claim["quantity"]] for claim in registered},
        "missing": 0,
        "measured": measured,
        "measured for the second cut": {
            name: second[name]
            for name in ("rules", "all", "cannot last on one or two", "can last on one or two",
                         "needs its own kind and lives",
                         "needs its own kind and dies in every contest", "holds")
        },
    }  # fmt: skip


# --- what the bounds were set by -----------------------------------------------------------------


def groups(rules: list[dict]) -> dict[str, int]:
    """The sizes of the groups a rule's counts put it in: known before any run."""
    entries = [{"rule": r["rule"]} for r in rules]
    by_birth = {name: sum(territories.birth(e) == name for e in entries)
                for name in ("none", "one", "two or three", "four or more")}  # fmt: skip
    middle = [e for e in entries if territories.birth(e) == "two or three"]
    fragile = sum(not rivals.survives_on_few(e["rule"]) for e in middle)
    return {**by_birth, "two or three, cannot last on one or two": fragile,
            "two or three, can last on one or two": len(middle) - fragile}  # fmt: skip


def chance(share: float, size: int, at_least: float | None, at_most: float | None) -> float:
    """The chance that a group of `size` rules, each holding with chance `share`, has a share
    inside the bounds."""
    low = 0 if at_least is None else math.ceil(at_least * size - 1e-9)
    high = size if at_most is None else math.floor(at_most * size + 1e-9)
    if low > high:
        return 0.0
    return float(stats.binom.cdf(high, size, share) - stats.binom.cdf(low - 1, size, share))


def chance_over(first: tuple[float, int], second: tuple[float, int], at_least: float) -> float:
    """The chance that the share of one group (its rules holding with chance `first[0]`, the
    group of size `first[1]`) is above the share of another by `at_least` or more."""
    (p, n), (q, m) = first, second
    if not n or not m:
        return 0.0
    total = 0.0
    for have in range(m + 1):
        need = math.ceil((have / m + at_least) * n - 1e-9)
        if need <= n:
            total += float(stats.binom.pmf(have, m, q)) * float(stats.binom.sf(need - 1, n, p))
    return total


# The claims whose groups depend on the runs: the size expected of each group, from the
# screen's counts scaled to the number of fresh rules.
EXPECTED = {"standoff only, of one tie-break only": 90, "organise alone": 46}
SCREENED = 1196


def design() -> dict:
    """What the bounds were set by: for each claim, what the screen gave, what the number
    would be if the cut it tests were worth nothing, the group it rests on, and the chance of
    passing in each case. For A1 "worth nothing" is the share of all rules that hold, and the
    claim passes then as well: what it can refuse is the guess the search began with, that
    organising alone is what makes a rule hold territories, put here at one rule in two."""
    sizes = groups(fresh())
    wider = groups(fresh() + further())
    fragile = wider["two or three, cannot last on one or two"]
    size_of = {"all": RULES, "birth on none": sizes["none"],
               "birth on two or three": sizes["two or three"],
               "birth on four or more": sizes["four or more"],
               # the screen's rules of that kind that lived, scaled to the rules of it here
               "needs its own kind and lives": round(fragile * 47 / 57)}  # fmt: skip
    pairs = {  # the two groups of a difference, each as (the screen's share, its size here)
        "two or three over one": ((0.548, sizes["two or three"]), (0.147, sizes["one"])),
        "one over none": ((0.147, sizes["one"]), (0.047, sizes["none"])),
        "cannot last over can": ((0.772, fragile),
                                 (0.478, wider["two or three, can last on one or two"])),
    }  # fmt: skip
    level = {"two or three over one": 0.292, "one over none": 0.079,
             "cannot last over can": 0.548}  # fmt: skip
    middle = {name: size for name, size in wider.items() if name.startswith("two or three")}
    out: dict = {"groups": sizes, "groups for the second cut": middle, "claims": {}}
    for label, _, quantity, at_least, at_most, needs, _ in CLAIMS:
        screen, nothing = SCREEN[quantity]
        row: dict = {"the screen gave": screen, "if the cut were worth nothing": nothing,
                     "needs": needs}  # fmt: skip
        if quantity in pairs:
            first, second = pairs[quantity]
            row["groups"] = [first[1], second[1]]
            row["passes if like the screen"] = round(chance_over(first, second, at_least), 4)
            same = level[quantity]
            row["passes if worth nothing"] = round(
                chance_over((same, first[1]), (same, second[1]), at_least), 4)  # fmt: skip
        else:
            if quantity in size_of:
                size = size_of[quantity]
            else:
                size = round(EXPECTED[quantity] * RULES / SCREENED)
            known = quantity in size_of and quantity != "needs its own kind and lives"
            row["group" if known else "group expected"] = size
            row["passes if like the screen"] = round(chance(screen, size, at_least, at_most), 4)
            if nothing is not None:
                row["passes if worth nothing"] = round(
                    chance(nothing, size, at_least, at_most), 4)  # fmt: skip
            if quantity == "organise alone":
                row["passes if one in two of them held"] = round(
                    chance(0.5, size, at_least, at_most), 4)  # fmt: skip
        out["claims"][label] = row
    return out


def question() -> dict:
    rules, extra = fresh(), further()
    listed = json.dumps([r["rule"] for r in rules + extra]).encode()
    files = {"study.py": HERE, "territories.py": HERE, "organised.py": SEARCH,
             "search.py": SEARCH, "contests.py": SEARCH, "rivals.py": SEARCH}  # fmt: skip
    return {
        "id": "scale-up-territories",
        "title": "Which rules hold territories against a copy of themselves?",
        "statement": "600 fresh rules of the even draw, each as two species with the one rule "
        "on a wrapped square grid of side 256 for 512 generations, from a full start and a "
        "half-full one, under the random draw and under the standoff, and each alone; and for "
        "the second cut, the rules that need two or three for a birth among 1,200 more. The "
        "share of rules that hold territories against their copy goes with how few of its own "
        "kind a cell needs to be born (few at none, most often at two or three, hardly any at "
        "four or more), and among the rules that need two or three, with whether a cell can "
        "last on one or two of its own kind. Rules that hold under one tie-break only do so "
        "mostly under the standoff, and a rule that organises itself alone is no likelier to "
        "hold territories.",
        "source": "docs/scale-up-plan.md, step 4b and decision D9; "
        "examples/scale-up-search/rivals.py",
        "rules": {"count": len(rules), "draw": "search.random_rule", "first": rules[0],
                  "last": rules[-1], "sha256": hashlib.sha256(listed).hexdigest()},
        "further_rules": {"draws": MORE, "kept": len(extra),
                          "first": extra[0] if extra else None,
                          "last": extra[-1] if extra else None,
                          "why": "the second cut is judged on every rule that needs two or "
                          "three of its own kind for a birth, among the 600 and among the "
                          "1,200 fresh rules drawn after them"},
        "start": START,
        "world": {"side": territories.SIDE, "generations": territories.TIMES[-1],
                  "read_at": list(territories.TIMES), "starts": list(territories.DENSITIES),
                  "tie_breaks": list(territories.KINDS)},
        "runs": len(jobs()),
        "holds_territories": "in at least one of a rule's four contests: both species hold a "
        "cell in twenty or more at the end, their block counts go against each other (-0.5 or "
        "under at blocks of 32), and one has a correlation area of 16 cells or more there",
        "not_tested": "a claim whose group has fewer rules than its `needs`",
        "design": design(),
        "sha256": {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                   for name, folder in files.items()},
        "excluded_seen": [
            "The wider screen (examples/scale-up-search/rivals.py): the 1,196 different rules "
            "of the even draw's numbers 1 to 1,200, each against its copy from start 11001. "
            "Both cuts were read off it: the first off its first 458 rules, where it then held "
            "on the other 738; the second off all 1,196. The bounds here were set between what "
            "it gave and what would mean nothing.",
            "The sizing look (sizing.py): the first 200 of those rules again from start 11002, "
            "to learn how far a rule's verdict hangs on its start: 199 held territories or not "
            "as they had from 11001. It tested no rule that the screen had not.",
            "The rest of the search: the one-species screen of the same 1,196 rules and of 172 "
            "near-majority rules, 450 soups, the contests of 29 rules and of the 18 rules one "
            "count from B2378/S25678, and the large-grid runs. No rule of any of them is among "
            "the 600: `seen()` lists them and `fresh()` leaves them out.",
            "No rule of this test (the draw's numbers 1,201 on) has been drawn into a run, and "
            "no run has begun from start 14001. The rules' counts were read to size the test: "
            "how many rules fall in each group is in `design`.",
        ],
    }  # fmt: skip


def rerun(record: dict) -> dict:
    """One stored record, computed again (for `lattice-lab verify`)."""
    return territories.run_one(territories.key(record))


STUDY = Study(
    directory=HERE,
    question=question,
    predictions=predictions,
    execute=execute,
    decide=decide,
    rerun=rerun,
)

if __name__ == "__main__":
    main(STUDY)
