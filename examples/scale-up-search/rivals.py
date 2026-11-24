"""
Every rule of the even draw against a copy of itself. Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-search/rivals.py [--workers 2]

contests.py gave a rival only to the 29 rules that grow when they are alone, on the guess that
growing alone was what mattered. It was not. Of the four rules that held territories there,
two fill the grid when they are alone, one sets and one is patches; and the three rules that
keep growing alone with their grounds level die or mix against their copy. So "four of 29"
counts the wrong 29, and says little about why those four.

Here every rule gets its rival: the 1,196 different rules of the screen's even draw, each as
two species with the one rule, from a full start (every cell live, half of them each species)
and from a half-full one, under the random draw and under the standoff. That is 4,784 worlds
on the screen's grid (side 256, 512 generations, start 11001), each judged as contests.py
judges a contest.

**What is asked of the rules** (`summarise`):

- how many hold territories against their copy, growing or standing, and under which
  tie-break (`holds`: both, the standoff only, the draw only, neither);
- what those rules do alone, by the screen's own call, and by how busy they are alone (the
  share of cells that change over two generations at the end of the screen's run);
- what they have in common. Three ways of cutting the rules: by the fewest neighbours of its
  own kind a cell needs to be born (`least_birth`); among the rules that need two or three,
  by whether a cell survives on one or two of its own kind; and count by count (`counts`):
  for every count in the birth set and in the survival set, the share of the rules with
  territories that have it, beside the share of all the rules, which is a half by the way
  the rules were drawn.

**How far the cuts can be trusted.** They were read off these same runs, not predicted. The
first was read off the first 458 rules while the rest were still running, so the other 738
are rules it was not read from, and the summary gives the two groups apart. The second was
read off all 1,196 and has no such check: it describes these rules, and only fresh rules can
test it.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contests  # noqa: E402
import search  # noqa: E402

OUT = HERE / "rivals"
STARTS = (1.0, 0.5)  # the full start first, then the half-full one
HOLDS = ("both", "standoff only", "draw only", "neither")
LEAST = ("0", "1", "2", "3", "4 or more", "never born")
ACTIVITY = ("dead or full", "still", "quiet", "busy")
STILL, BUSY = 0.01, 0.2
READ_OFF = 458  # the cut by least birth was read off the first this-many rules


def rules() -> list[dict]:
    """The different rules of the screen's even draw, each under the first number it was
    drawn at."""
    seen: set[str] = set()
    out = []
    for index in search.RULES:
        rule = search.random_rule(index)
        if rule not in seen:
            seen.add(rule)
            out.append({"index": index, "rule": rule})
    return out


def worlds() -> list[dict]:
    """Every rule against its copy: all the full starts, then all the half-full ones."""
    out = []
    for density in STARTS:
        for drawn in rules():
            for kind in contests.KINDS:
                out.append({"family": "copy", "index": drawn["index"],
                            "name": f"{drawn['rule']} against itself",
                            "rules": [drawn["rule"]] * 2, "tie_break": kind,
                            "density": density, "source": f"rule {drawn['index']}"})  # fmt: skip
    return out


def least_birth(rule: str) -> str:
    """The fewest neighbours of its own kind an empty cell needs for a species to be born
    into it, as one of `LEAST`."""
    births = [int(count) for count in rule.split("/")[0][1:]]
    if not births:
        return "never born"
    return str(min(births)) if min(births) < 4 else "4 or more"


def survives_on_few(rule: str) -> bool:
    """Whether a cell survives with one or with two neighbours of its own kind."""
    return bool({"1", "2"} & set(rule.split("/")[1][1:]))


def needs_its_own_kind(rule: str) -> bool:
    """A cell needs two or three of its own kind at least to be born, and does not survive on
    one or two: the two cuts together."""
    return least_birth(rule) in ("2", "3") and not survives_on_few(rule)


def activity(alone: dict) -> str:
    """How busy a rule is when it is alone, from the screen's reading of it: dead or full if
    the screen called it dead, and otherwise still, quiet or busy by the share of cells that
    change over two generations at the end (under 1%, under 20%, 20% or more)."""
    if alone["called"] == "dead":
        return "dead or full"
    return "still" if alone["changed"] < STILL else "quiet" if alone["changed"] < BUSY else "busy"


def condition(found: dict) -> str:
    """The start and the tie-break of a contest, in words."""
    return f"{'full' if found['density'] == 1.0 else 'half-full'} start, {found['tie_break']}"


def by_rule(found: list[dict]) -> list[dict]:
    """One entry a rule: its verdict under each start and tie-break, the largest territory it
    held, and whether it holds territories under both tie-breaks, one, or neither. `found` is
    the contests as contests.describe gives them."""
    entries: dict[str, dict] = {}
    for f in found:
        entry = entries.setdefault(f["rules"][0], {"rule": f["rules"][0], "index": f["index"],
                                                   "verdicts": {}, "territory": 0.0,
                                                   "growing": False})  # fmt: skip
        entry["verdicts"][condition(f)] = f["verdict"]
        if f["verdict"].endswith("territories"):
            entry["territory"] = max([entry["territory"],
                                      *(t["area"] or 0.0 for t in f["territories"])])  # fmt: skip
            entry["growing"] |= f["verdict"] == "growing territories"
    for entry in entries.values():
        held = {kind: any(verdict.endswith("territories")
                          for where, verdict in entry["verdicts"].items()
                          if where.endswith(kind))
                for kind in contests.KINDS}  # fmt: skip
        entry["holds"] = ("both" if all(held.values()) else "standoff only" if held["standoff"]
                          else "draw only" if held["random"] else "neither")  # fmt: skip
        entry["dies"] = set(entry["verdicts"].values()) == {"dead"}
    return sorted(entries.values(), key=lambda e: e["index"])


def counts(entries: list[dict], chosen: list[dict]) -> dict[str, list[dict]]:
    """For every neighbour count in the birth set and in the survival set: the share of all
    the rules that have it, and the share of the chosen ones."""

    def share(group: list[dict], part: int, count: int) -> float | None:
        if not group:
            return None
        have = sum(str(count) in e["rule"].split("/")[part][1:] for e in group)
        return round(have / len(group), 3)

    return {name: [{"count": k, "all": share(entries, part, k), "chosen": share(chosen, part, k)}
                   for k in range(9)]
            for part, name in enumerate(("birth", "survival"))}  # fmt: skip


def summarise(found: list[dict], alone: dict[str, dict]) -> dict:
    """`alone` is what each rule does by itself in the screen: its rule to the screen's
    description of it (its call, and the share of its cells that change)."""
    tallies: dict[str, dict[str, int]] = {}
    for f in found:
        empty = {"contests": 0, **dict.fromkeys(contests.VERDICTS, 0)}
        tally = tallies.setdefault(condition(f), empty)
        tally["contests"] += 1
        tally[f["verdict"]] += 1
    entries = by_rule(found)
    held = [e for e in entries if e["holds"] != "neither"]

    def table(groups: tuple[str, ...], of) -> dict[str, dict[str, int]]:
        """How many rules hold territories, by the group `of` puts each rule in."""
        rows = {group: dict.fromkeys(HOLDS, 0) for group in groups}
        for entry in entries:
            group = of(entry["rule"])
            if group is not None:
                rows.setdefault(group, dict.fromkeys(HOLDS, 0))[entry["holds"]] += 1
        return rows

    def few(rule: str) -> str | None:
        if least_birth(rule) not in ("2", "3"):
            return None
        return "survives on 1 or 2" if survives_on_few(rule) else "survives on neither"

    def living(group: list[dict]) -> dict:
        """Of a group of rules: how many die in every contest, and what the rest hold."""
        alive = [e for e in group if not e["dies"]]
        rest = {name: sum(e["holds"] == name for e in alive) for name in HOLDS}
        return {"rules": len(group), "die in every contest": len(group) - len(alive),
                "of the rest": rest}  # fmt: skip

    order = [drawn["rule"] for drawn in rules()]
    early = set(order[:READ_OFF])
    own = [e for e in entries if needs_its_own_kind(e["rule"])]
    others = [e for e in entries if not needs_its_own_kind(e["rule"])]

    return {
        "side": search.SIDE,
        "times": list(search.TIMES),
        "start": search.SEED,
        "rules": len(entries),
        "tallies": tallies,
        "holds": {name: sum(e["holds"] == name for e in entries) for name in HOLDS},
        "growing": sum(e["growing"] for e in entries),
        "alone": table(("dead", "patches", "organised", "growing"),
                       lambda rule: alone[rule]["called"] if rule in alone else "not screened"),
        "activity alone": table(ACTIVITY, lambda rule: activity(alone[rule])
                                if rule in alone else "not screened"),
        "least birth": table(LEAST, least_birth),
        "least birth, the rules it was read off": table(
            LEAST, lambda rule: least_birth(rule) if rule in early else None),
        "least birth, the other rules": table(
            LEAST, lambda rule: None if rule in early else least_birth(rule)),
        "least birth 2 or 3": table(("survives on 1 or 2", "survives on neither"), few),
        "needs its own kind": living(own),
        "does not": living(others),
        "counts": counts(entries, held),
        "counts under both": counts(entries, [e for e in entries if e["holds"] == "both"]),
        "territories": sorted(held, key=lambda e: (HOLDS.index(e["holds"]), -e["territory"])),
    }  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    path = OUT / "records.jsonl"
    done = set()
    if path.exists():
        done = {contests.key(json.loads(line)) for line in path.read_text().splitlines()}
    todo = [w for w in worlds() if contests.key(w) not in done]
    with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
        for record in pool.map(contests.run, todo, chunksize=4):
            sink.write(json.dumps(record) + "\n")
            sink.flush()
    found = [contests.describe(json.loads(line)) for line in path.read_text().splitlines()]
    screen = (search.OUT / "records.jsonl").read_text().splitlines()
    alone = {f["rules"][0]: f for f in map(search.describe, map(json.loads, screen))
             if f["family"] == "rule"}  # fmt: skip
    summary = summarise(found, alone)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"{summary['rules']} rules, {len(found)} contests")
    for where, tally in summary["tallies"].items():
        print(f"{where}: {tally}")
    print(f"hold territories: {summary['holds']}; growing in {summary['growing']} rules")
    for name in ("alone", "activity alone", "least birth",
                 "least birth, the rules it was read off", "least birth, the other rules",
                 "least birth 2 or 3", "needs its own kind", "does not"):  # fmt: skip
        print(f"by {name}: {summary[name]}")
    for name in ("birth", "survival"):
        print(name, [(c["count"], c["all"], c["chosen"]) for c in summary["counts"][name]])
    for entry in summary["territories"][:60]:
        print(f"{entry['holds']}: rule {entry['index']} {entry['rule']}, territory "
              f"{entry['territory']}, {entry['verdicts']}")  # fmt: skip


if __name__ == "__main__":
    main()
