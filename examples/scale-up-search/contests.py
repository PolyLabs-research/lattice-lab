"""
The one-species rules the search found growing, each given a rival. Exploratory: nothing here
is registered.

    uv run --no-sync python examples/scale-up-search/contests.py [--workers 2]

A rule whose domains keep growing while it has the grid to itself is not yet a competition.
Here it gets a rival. In this lab a species counts only its own neighbours, so two species
meet in two ways only: a cell holds one of them at a time, and where both would be born into
the same empty cell the tie-break settles it.

**Which rules** (`growers`): every one-species world the screen called growing, and the rule
of the species left alone in a soup the screen called growing. Each rule once, the largest
correlation area first.

**Which contests**, on the screen's grid (side 256, 512 generations, the same readings):

    contest   a rule against a copy of itself, under the random draw and under the standoff,
              from a full start (every cell live, half of them each species: each species
              starts from the kind of field it grew from alone, with its rival in the gaps)
              and, for the 40 strongest rules, from a half-full start as well
    pair      the 12 strongest rules against each other, two at a time, from a full start,
              under both tie-breaks
    cross     the rules that held territories against a copy of themselves, against each
              other, two at a time, from a full start, under both tie-breaks: picked by the
              contests above, so run after them
    copies    the same rules as three species and as five, all with the one rule, from a full
              start, under both tie-breaks: does a world of territories take more than two
    variant   the rule that held growing territories in the most contests, against each of
              the 18 rules that differ from it by one count (one more or one fewer in the
              birth set or the survival set), from a full start, under both tie-breaks: must
              the two species be the same for territories to hold

**What a contest comes to**, from the screen's own thresholds and from whether the species
keep apart (`apart`: how one species' count in a block goes with another's, over the blocks
of 32 at the end; for two species -1 where a block holds one or the other and +1 where they
come and go together, and for n species that share the grid out, -1 / (n - 1)):

    dead                   no species holds ground at the end (one cell in twenty)
    one left               one does
    growing territories    two or more do, they keep apart (half way to sharing the grid out,
                           or further: -0.5 or under for two species), and the cells of one
                           of them have a correlation area of 16 or more that is still growing
    standing territories   the same, with an area that has stopped growing
    together               two or more do and one has an area of 16 or more, but they do not
                           keep apart: what is organised is where anything lives, not who
    mixed                  two or more do, in patches
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import organised  # noqa: E402
import search  # noqa: E402

OUT = HERE / "contests"
SCREEN = HERE / "screen" / "records.jsonl"
KINDS = ("random", "standoff")
MOST, HALF, PAIRED = 150, 40, 12
APART = -0.5
VERDICTS = ("dead", "one left", "growing territories", "standing territories", "together",
            "mixed")  # fmt: skip


def growers(found: list[dict]) -> list[dict]:
    """The one-species rules that grew in the screen, each once, the largest area first.
    `found` is the screen's worlds as search.describe gives them. `density` is the share of
    the grid the rule's own cells had at the start of the world it grew in: a half where it
    was alone, and a half split between the species where it was one of several."""
    rules: dict[str, dict] = {}
    for f in found:
        if f["called"] != "growing":
            continue
        if len(f["rules"]) == 1:
            rule, source = f["rules"][0], f"{f['family']} {f['index']}"
        elif f["holding"] == 1:
            lone = max(range(len(f["shares"])), key=f["shares"].__getitem__)
            rule = f["rules"][lone]
            source = f"{f['family']} {f['index']} ({f['tie_break']}), the species left"
        else:
            continue
        if rule not in rules or f["area"] > rules[rule]["area"]:
            rules[rule] = {"rule": rule, "source": source, "field": f["field"],
                           "area": f["area"], "growth": f["growth"],
                           "density": search.DENSITY / len(f["rules"])}  # fmt: skip
    return sorted(rules.values(), key=lambda r: (-r["area"], r["rule"]))


def worlds(rules: list[dict]) -> list[dict]:
    """Every contest: a rule against itself, and the strongest rules against each other."""
    out = []
    for index, grower in enumerate(rules[:MOST], start=1):
        for density in (1.0, 0.5) if index <= HALF else (1.0,):
            for kind in KINDS:
                out.append({"family": "contest", "index": index,
                            "name": f"{grower['rule']} against itself",
                            "rules": [grower["rule"]] * 2, "tie_break": kind,
                            "density": density, "source": grower["source"]})  # fmt: skip
    strongest = list(enumerate(rules[:PAIRED], start=1))
    for (i, a), (j, b) in itertools.combinations(strongest, 2):
        for kind in KINDS:
            out.append({"family": "pair", "index": 100 * i + j,
                        "name": f"{a['rule']} against {b['rule']}",
                        "rules": [a["rule"], b["rule"]], "tie_break": kind, "density": 1.0,
                        "source": f"{a['source']}; {b['source']}"})  # fmt: skip
    return out


def _held(found: list[dict]) -> list[str]:
    """The rules that held territories, growing or standing, against a copy of themselves."""
    held: list[str] = []
    for f in found:
        own = f["family"] == "contest" and f["verdict"].endswith("territories")
        if own and f["rules"][0] not in held:
            held.append(f["rules"][0])
    return held


def crosses(found: list[dict]) -> list[dict]:
    """The rules that held territories against a copy of themselves, against each other.
    `found` is the contests as `describe` gives them."""
    out = []
    for (i, a), (j, b) in itertools.combinations(enumerate(_held(found), start=1), 2):
        for kind in KINDS:
            out.append({"family": "cross", "index": 100 * i + j, "name": f"{a} against {b}",
                        "rules": [a, b], "tie_break": kind, "density": 1.0,
                        "source": "each held territories against a copy of itself"})  # fmt: skip
    return out


def copies(found: list[dict]) -> list[dict]:
    """The rules that held territories against one copy of themselves, as three species and
    as five with the one rule. `found` is the contests as `describe` gives them."""
    out = []
    for index, rule in enumerate(_held(found), start=1):
        for species in (3, 5):
            for kind in KINDS:
                out.append({"family": f"{species} copies", "index": index,
                            "name": f"{species} copies of {rule}", "rules": [rule] * species,
                            "tie_break": kind, "density": 1.0,
                            "source": "held territories against one copy of itself"})  # fmt: skip
    return out


def neighbours(rule: str) -> list[str]:
    """The 18 rules that differ from `rule` by one count: each neighbour count put into or
    taken out of the birth set, then the survival set."""
    birth, survive = ({int(c) for c in part[1:]} for part in rule.split("/"))
    out = []
    for which in (0, 1):
        for count in range(9):
            sets = [set(birth), set(survive)]
            sets[which] ^= {count}
            out.append("B{}/S{}".format(*("".join(map(str, sorted(x))) for x in sets)))
    return out


def variants(found: list[dict]) -> list[dict]:
    """The rule that held growing territories in the most contests against its copy, against
    each of its 18 neighbours. `found` is the contests as `describe` gives them."""
    wins: dict[str, int] = {}
    for f in found:
        if f["family"] == "contest" and f["verdict"] == "growing territories":
            wins[f["rules"][0]] = wins.get(f["rules"][0], 0) + 1
    if not wins:
        return []
    rule = max(wins, key=wins.__getitem__)
    out = []
    for index, other in enumerate(neighbours(rule), start=1):
        for kind in KINDS:
            out.append({"family": "variant", "index": index, "name": f"{rule} against {other}",
                        "rules": [rule, other], "tie_break": kind, "density": 1.0,
                        "source": "one count away from the best territory rule"})  # fmt: skip
    return out


def key(world: dict) -> tuple:
    return (world["family"], world["index"], world["tie_break"], world["density"])


def run(world: dict) -> dict:
    found = organised.profile(
        world["rules"], world["tie_break"], search.SIDE, search.SEED, search.TIMES,
        density=world["density"],
    )  # fmt: skip
    return {**world, "side": search.SIDE, "seed": search.SEED, **found}


def apart(record: dict) -> float | None:
    """How the species' counts in a block go together, over the largest blocks at the end.
    For two species it is the correlation of the two block sums: -1 where a block holds one
    species or the other and +1 where the two come and go together. For more it is the same
    thing averaged over the pairs (each pair weighted by the two species' scatter), which is
    -1 / (n - 1) for n species that share the grid out between them. Read off the recorded
    areas: the live cells' block sum is the species' added, so its variance is theirs plus
    what the pairs share. None where a species has no area."""
    block = record["blocks"][-1]

    def scatter(name: str) -> float | None:
        field = record["fields"][name]
        area, share = field["area"][-1][-1], field["share"][-1]
        return None if area is None else area * block * block * share * (1 - share)

    own = [scatter(f"species {s + 1}") for s in range(len(record["rules"]))]
    both = scatter("live")
    if both is None or any(v is None or v <= 0 for v in own):
        return None
    pairs = sum(math.sqrt(a * b) for a, b in itertools.permutations(own, 2))
    return (both - sum(own)) / pairs


def describe(record: dict) -> dict:
    """What a contest comes to: the screen's description of the world, each species'
    territory read on its own, whether they keep apart, and the verdict."""
    out = search.describe(record)
    species = len(record["rules"])
    territories = [search.reading(record, f"species {s + 1}") for s in range(species)]
    kinds = {t["called"] for t in territories}
    kept = apart(record)
    if out["holding"] == 0:
        verdict = "dead"
    elif out["holding"] == 1:
        verdict = "one left"
    elif not kinds & {"growing", "organised"}:
        verdict = "mixed"
    elif kept is None or kept > APART / (species - 1):
        verdict = "together"
    else:
        verdict = "growing territories" if "growing" in kinds else "standing territories"
    return {
        **out,
        "density": record["density"],
        "source": record["source"],
        "verdict": verdict,
        "apart": None if kept is None else round(kept, 3),
        "territories": [
            {k: t[k] for k in ("called", "area", "scaling", "growth")} for t in territories
        ],
    }


def summarise(found: list[dict], rules: list[dict]) -> dict:
    tallies: dict[str, dict[str, int]] = {}
    for f in found:
        group = f"{f['family']}, {'full' if f['density'] == 1.0 else 'half-full'} start, "
        group += f["tie_break"]
        tally = tallies.setdefault(group, {"contests": 0, **dict.fromkeys(VERDICTS, 0)})
        tally["contests"] += 1
        tally[f["verdict"]] += 1

    def territory(f: dict) -> float:
        return max(t["area"] or 0.0 for t in f["territories"])

    def having(verdict: str) -> list[dict]:
        return sorted((f for f in found if f["verdict"] == verdict), key=lambda f: -territory(f))

    return {
        "side": search.SIDE,
        "times": list(search.TIMES),
        "start": search.SEED,
        "rules": rules,
        "tallies": tallies,
        "growing territories": having("growing territories"),
        "standing territories": having("standing territories"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    screen = [search.describe(json.loads(line)) for line in SCREEN.read_text().splitlines()]
    rules = growers(screen)
    path = OUT / "records.jsonl"

    def finish(wanted: list[dict]) -> list[dict]:
        """Run what has not been run, and describe every one of the wanted contests."""
        done = set()
        if path.exists():
            done = {key(json.loads(line)) for line in path.read_text().splitlines()}
        todo = [w for w in wanted if key(w) not in done]
        with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
            for record in pool.map(run, todo, chunksize=4):
                sink.write(json.dumps(record) + "\n")
                sink.flush()
        keys = {key(w) for w in wanted}
        records = [json.loads(line) for line in path.read_text().splitlines()]
        return [describe(r) for r in records if key(r) in keys]

    found = finish(worlds(rules))
    found += finish(crosses(found) + copies(found) + variants(found))
    summary = summarise(found, rules)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"{len(rules)} rules grow alone; {len(found)} contests")
    for group, tally in summary["tallies"].items():
        print(f"{group}: {tally}")
    for f in summary["growing territories"][:40]:
        print(f"growing territories: {f['name']} ({f['tie_break']}, density {f['density']}): "
              f"shares {f['shares']}, apart {f['apart']}, {f['territories']}")  # fmt: skip


if __name__ == "__main__":
    main()
