"""
A search of the lab's rule sets for worlds that organise themselves over a growing distance.
Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-search/search.py [--workers 2] [--quick]

Steps 2 to 4 of the scale-up plan found that the two worlds they followed are made of
independent patches: nothing in them is organised over more than a few cells. This looks for
worlds that are different, with the measure of organised.py: the correlation area of the live
cells and of each species, how it scales with the block, and whether it is still growing.

**What is searched**, each world once from a half-full mixed start on a wrapped square grid of
side 256, for 512 generations, read at generations 32, 64, 128, 256 and 512:

    soups           rule sets for 2, 3 and 5 species drawn as `latticelife autorun` draws them
                    (a birth set and a survival set of one to four neighbour counts each), 150
                    of each, under the random draw and under the standoff
    rules           1,200 rules for one species drawn evenly from all 262,144: each neighbour
                    count is in the birth set, and in the survival set, with chance one half
                    (1,196 different rules: four are drawn twice)
    near-majority   300 draws of a rule for one species that is born and survives at or above
                    a threshold, with up to two counts changed: rules of the kind known to
                    form domains, looked at on purpose. The family has 2,056 rules and a
                    third of its draws change no count, so the 300 draws are 172 different
                    rules; a rule drawn twice is run twice and comes out the same
    known           Life, HighLife, the pair and soup 19 of the earlier steps, and three rules
                    known from the literature: Vote (B5678/S45678), Anneal (B4678/S35678) and
                    Day and Night (B3678/S34678)

**What a world is called**, from the field of its that has the largest area at the end:

    dead        nothing alive at the end, or nothing dead
    growing     an area of 16 cells or more, growing as the 0.25 power of time or faster over
                the last three readings
    organised   an area of 16 cells or more that is no longer growing
    patches     everything else: what the worlds of steps 2 to 4 are

A world of several species is also asked how many of them **hold ground** at the end, one cell
in twenty or more: a soup in which one species is left alone is a one-species world, however
it began, and a world is **contested** only if two or more hold ground.

The thresholds are for sorting, not for claiming: a world called growing here is a candidate,
and confirm.py runs the candidates again on a larger grid from fresh starts.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scale-up-compete"))

import organised  # noqa: E402
from first_look import HIGHLIFE, LIFE, soup_rules  # noqa: E402

OUT = HERE / "screen"
SIDE, TIMES, SEED, DENSITY = 256, (32, 64, 128, 256, 512), 11001, 0.5
QUICK = {"side": 64, "times": (16, 32, 64, 128)}
KNOWN = {
    1: ("Life", (LIFE,)),
    2: ("HighLife", (HIGHLIFE,)),
    3: ("Life against HighLife", (LIFE, HIGHLIFE)),
    4: ("soup 19", soup_rules(19)),
    5: ("Vote", ("B5678/S45678",)),
    6: ("Anneal", ("B4678/S35678",)),
    7: ("Day and Night", ("B3678/S34678",)),
}
SOUPS = {2: range(20001, 20151), 3: range(30001, 30151), 5: range(50001, 50151)}
RULES = range(1, 1201)
NEAR = range(1, 301)
LARGE, STILL_GROWING, HOLDS = 16.0, 0.25, 0.05


def random_rule(index: int) -> str:
    """Rule `index` of the even draw from all outer-totalistic rules of eight neighbours."""
    rng = np.random.default_rng([20261124, 4, index])
    birth = [k for k in range(9) if rng.random() < 0.5]
    survive = [k for k in range(9) if rng.random() < 0.5]
    return f"B{''.join(map(str, birth))}/S{''.join(map(str, survive))}"


def near_majority(index: int) -> str:
    """Rule `index` of the near-majority family: born at or above one threshold (3 to 6),
    surviving at or above another (2 to 6), with none, one or two counts changed."""
    rng = np.random.default_rng([20261124, 5, index])
    sets = [set(range(int(rng.integers(3, 7)), 9)), set(range(int(rng.integers(2, 7)), 9))]
    for _ in range(int(rng.integers(0, 3))):
        sets[int(rng.integers(0, 2))] ^= {int(rng.integers(0, 9))}
    birth, survive = (sorted(s) for s in sets)
    return f"B{''.join(map(str, birth))}/S{''.join(map(str, survive))}"


def worlds() -> list[dict]:
    """Every world of the search: its family, its number in it, its rules and its tie-break."""
    out = [
        {"family": "known", "index": i, "name": name, "rules": list(rules), "tie_break": "standoff"}
        for i, (name, rules) in KNOWN.items()
    ]
    for species, indices in SOUPS.items():
        for index in indices:
            rules = list(soup_rules(index, species))
            for kind in ("random", "standoff"):
                out.append({"family": f"soup {species}", "index": index, "rules": rules,
                            "tie_break": kind})  # fmt: skip
    out += [{"family": "rule", "index": i, "rules": [random_rule(i)], "tie_break": "standoff"}
            for i in RULES]  # fmt: skip
    out += [{"family": "near-majority", "index": i, "rules": [near_majority(i)],
             "tie_break": "standoff"} for i in NEAR]  # fmt: skip
    return out


def key(world: dict) -> tuple:
    return (world["family"], world["index"], world["tie_break"])


def run(job: tuple[dict, int, tuple[int, ...]]) -> dict:
    world, side, times = job
    found = organised.profile(world["rules"], world["tie_break"], side, SEED, times,
                              density=DENSITY)  # fmt: skip
    return {**world, "side": side, "seed": SEED, **found}


def reading(record: dict, name: str) -> dict:
    """One field of a world: its correlation area at the largest block at the end, the power
    of the block that grows as over the last three blocks, the power of time it grows as over
    the last three readings, and what that makes it."""
    blocks, times = record["blocks"], record["times"]
    field = record["fields"][name]
    over_time = [row[-1] for row in field["area"]]
    most = over_time[-1]
    if most is None:
        return {"called": "dead", "field": name, "area": None, "scaling": None, "growth": None,
                "area_over_time": over_time}  # fmt: skip
    scaling = organised.scaling(field["area"][-1], blocks, blocks[-3], blocks[-1])
    growth = organised.growth(over_time[-3:], times[-3:])
    if most >= LARGE:
        called = "growing" if growth is not None and growth >= STILL_GROWING else "organised"
    else:
        called = "patches"
    return {
        "called": called,
        "field": name,
        "area": round(most, 2),
        "scaling": None if scaling is None else round(scaling, 3),
        "growth": None if growth is None else round(growth, 3),
        "area_over_time": over_time,
    }


def describe(record: dict) -> dict:
    """What a world is called, and the three numbers behind it, for the field of its with the
    largest correlation area at the end; and how many of its species hold ground."""
    live = record["fields"]["live"]["share"][-1]
    several = len(record["rules"]) > 1
    shares = [record["fields"][f"species {s + 1}"]["share"][-1] if several else live
              for s in range(len(record["rules"]))]  # fmt: skip
    best, most = None, 0.0
    for name, field in record["fields"].items():
        last = field["area"][-1][-1]
        if last is not None and last > most:
            best, most = name, last
    out = {
        "family": record["family"],
        "index": record["index"],
        "name": record.get("name"),
        "rules": record["rules"],
        "tie_break": record["tie_break"],
        "live": live,
        "shares": shares,
        "holding": sum(share >= HOLDS for share in shares),
        "changed": record["changed"],
    }
    if best is None:
        return {**out, "called": "dead", "field": None, "area": None, "scaling": None,
                "growth": None}  # fmt: skip
    return {**out, **reading(record, best)}


def summarise(records: list[dict]) -> dict:
    found = [describe(r) for r in records]
    families: dict[str, dict[str, int]] = {}
    for f in found:
        group = f["family"] if f["family"].startswith(("known", "rule", "near")) else (
            f"{f['family']}, {f['tie_break']}")  # fmt: skip
        tally = families.setdefault(group, {"worlds": 0, "dead": 0, "patches": 0, "organised": 0,
                                            "growing": 0, "contested": 0,
                                            "growing and contested": 0})  # fmt: skip
        tally["worlds"] += 1
        tally[f["called"]] += 1
        tally["contested"] += f["holding"] > 1
        tally["growing and contested"] += f["called"] == "growing" and f["holding"] > 1
    growing = sorted((f for f in found if f["called"] == "growing"),
                     key=lambda f: (-f["growth"], -f["area"]))  # fmt: skip
    organised_ = sorted((f for f in found if f["called"] == "organised"), key=lambda f: -f["area"])
    return {
        "side": records[0]["side"],
        "times": records[0]["times"],
        "blocks": records[0]["blocks"],
        "start": SEED,
        "large_area": LARGE,
        "still_growing": STILL_GROWING,
        "families": families,
        "known": [f for f in found if f["family"] == "known"],
        "growing": growing,
        "organised": organised_,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--quick", action="store_true", help="side 64, 128 generations")
    args = parser.parse_args()
    side, times = (QUICK["side"], QUICK["times"]) if args.quick else (SIDE, TIMES)
    out = OUT.with_name("screen-quick") if args.quick else OUT
    out.mkdir(exist_ok=True)
    path = out / "records.jsonl"
    done = set()
    if path.exists():
        done = {key(json.loads(line)) for line in path.read_text().splitlines()}
    todo = [(w, side, times) for w in worlds() if key(w) not in done]
    if args.quick:
        todo = todo[:60]
    with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
        for record in pool.map(run, todo, chunksize=4):
            sink.write(json.dumps(record) + "\n")
            sink.flush()
    records = [json.loads(line) for line in path.read_text().splitlines()]
    summary = summarise(records)
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    for family, tally in summary["families"].items():
        print(f"{family}: {tally}")
    for f in summary["known"]:
        print(f"known: {f['name']}: {f['called']}, {f['field']}, area {f['area']}, scaling "
              f"{f['scaling']}, growth {f['growth']}")  # fmt: skip
    for f in summary["growing"][:40]:
        print(f"growing: {f['family']} {f['index']} {f['tie_break']} {f['rules']}: {f['field']}, "
              f"area {f['area']}, scaling {f['scaling']}, growth {f['growth']}, holding "
              f"{f['holding']}")  # fmt: skip


if __name__ == "__main__":
    main()
