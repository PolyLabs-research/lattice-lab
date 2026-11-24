"""
The search's candidates again, on a larger grid from fresh starts. Exploratory: nothing here
is registered.

    uv run --no-sync python examples/scale-up-search/confirm.py [--workers 2]

search.py sorts 2,407 worlds, and contests.py some hundreds more, on a 256 x 256 grid from one
start each. A world picked out of thousands for its reading has a reading that flatters it, so
the picked worlds are run again here where the reading did not pick them: side 1,024, 2,048
generations, from a fresh start (12001), read at generations 64 to 2,048 through blocks of 4
to 128. A known world, a rule alone, a contest or a pair whose first start keeps growing is
run from two more starts (12002 and 12003), for a spread. The rest are settled by the one:
patches, nothing, a set pattern or a takeover on a grid sixteen times the screen's do not
need a spread to be told apart, and the soups and the world of five copies cost too much to
repeat here (five species cost four times what one does).

**Which worlds** (`candidates`, kept in `confirm/candidates.json`):

    known     the seven known worlds of the screen, as anchors
    alone     the one-species rules with the largest areas among those the screen called
              growing (the first ten that are not known worlds), and the rule of every
              contest below, so that each contest can be set beside its rule alone. A rule
              that grew as the last species of a soup starts from the share of the grid it
              had there (a quarter in a soup of two), since a half is another start
    soup      the soups the screen called growing in which two or more species hold ground
              (the four with the largest areas)
    left      the soups the screen called growing in which one species is left (the four
              rule sets with the largest areas, each under the tie-break it did best under).
              The soup itself, not its last species alone: the species that die in the first
              generations shape the start the last one grows from
    contest   rules against a copy of themselves whose territories the contests found growing
              (four rules, the largest territories first): each from a full start if it grew
              from one and from a half-full start if not, under both tie-breaks
    pair      two different rules whose territories the contests found growing (two at most)
    copies    five species with one rule whose territories the contests found growing (the
              one world with the largest territories)

**What is reported** for each world, from the field of its with the largest area at the end
and, for a world of several species, from each species' own cells (its territory):

- the correlation area through blocks of 128 at every reading, as the mean over the starts
  with their spread, and its square root, the side of the patch of cells that go together;
- the power of time the area grows as, over the last three readings and over all of them;
- the power of the block it grows as at the end: near 0 where the blocks are larger than the
  domains, which is where the area can be trusted, and 2 where a block sits inside one;
- **the clock that goes with a zoom-out** (organised.clock): whether the world seen through
  blocks twice the size is the same picture 2, 4 or 8 times later;
- for a world of several species, whether they **keep apart** (contests.apart, over the
  blocks of 128 at the end).

**What a world is called**, by the screen's thresholds on the mean of the starts:

    keeps growing   an area of 16 cells or more at the end, growing as the 0.25 power of time
                    or faster over the last three readings, while the field keeps its share
                    of the grid
    taking over     the same, but the field's share of the grid has moved by a fifth of the
                    grid or more since the first reading, or its smaller side (the field or
                    its gaps) has halved: one kind of ground is taking the grid, and the
                    growth ends when it has it
    taken over      it has: the field had 64 cells or more at an earlier reading, and at
                    the end it has no area at all, or under 16 cells with its share moved as
                    above
    organised       16 cells or more at the end, no longer growing
    patches         less than 16 cells at the end
    dead            no field has an area at the end, and none ever had 64 cells
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contests  # noqa: E402
import organised  # noqa: E402
import search  # noqa: E402

OUT = HERE / "confirm"
SIDE, TIMES, BLOCKS = 1024, (64, 128, 256, 512, 1024, 2048), (4, 8, 16, 32, 64, 128)
STARTS = (12001, 12002, 12003)
ALONE, SOUPS, LEFT, CONTESTS, PAIRS, COPIES = 10, 4, 4, 4, 2, 1
WAITS = (2, 4, 8)
DRIFT, HALVED, TAKEN = 0.2, 0.5, 64.0
MORE = ("known", "alone", "contest", "pair")


def candidates(screen: list[dict], contested: dict) -> list[dict]:
    """The worlds to run again. `screen` is the screen's worlds as search.describe gives them,
    `contested` the summary of contests.py."""
    out = [{"family": "known", "index": f["index"], "name": f["name"], "rules": f["rules"],
            "tie_break": f["tie_break"], "density": 0.5, "why": "a known world"}
           for f in screen if f["family"] == "known"]  # fmt: skip
    known = {tuple(w["rules"]) for w in out}
    grew = [f for f in contested["growing territories"] if f["family"] == "contest"]
    rivals = list(dict.fromkeys(f["rules"][0] for f in grew))[:CONTESTS]
    growers = [g for g in contests.growers(screen) if (g["rule"],) not in known]
    alone = growers[:ALONE] + [g for g in growers[ALONE:] if g["rule"] in rivals]
    for index, grower in enumerate(alone, start=1):
        out.append({"family": "alone", "index": index, "name": grower["rule"],
                    "rules": [grower["rule"]], "tie_break": "standoff",
                    "density": grower["density"],
                    "why": f"grew alone in the screen ({grower['source']})"})  # fmt: skip
    soups = sorted((f for f in screen if f["family"].startswith("soup")
                    and f["called"] == "growing" and f["holding"] > 1),
                   key=lambda f: -f["area"])[:SOUPS]  # fmt: skip
    for f in soups:
        out.append({"family": "soup", "index": f["index"], "name": f"{f['family']} {f['index']}",
                    "rules": f["rules"], "tie_break": f["tie_break"], "density": 0.5,
                    "why": "a soup that grew in the screen with two species or more"})  # fmt: skip
    left: list[dict] = []
    for f in sorted((f for f in screen if f["family"].startswith("soup")
                     and f["called"] == "growing" and f["holding"] == 1),
                    key=lambda f: -f["area"]):  # fmt: skip
        if all(f["rules"] != other["rules"] for other in left):
            left.append(f)
    for f in left[:LEFT]:
        out.append({"family": "left", "index": f["index"], "name": f"{f['family']} {f['index']}",
                    "rules": f["rules"], "tie_break": f["tie_break"], "density": 0.5,
                    "why": "a soup that grew in the screen with one species left"})  # fmt: skip
    for index, rule in enumerate(rivals, start=1):
        full = any(f["rules"][0] == rule and f["density"] == 1.0 for f in grew)
        for kind in contests.KINDS:
            out.append({"family": "contest", "index": index, "name": f"{rule} against itself",
                        "rules": [rule, rule], "tie_break": kind,
                        "density": 1.0 if full else 0.5,
                        "why": "its territories grew in the contests"})  # fmt: skip
    pairs = [f for f in contested["growing territories"] if f["family"] == "pair"][:PAIRS]
    for f in pairs:
        out.append({"family": "pair", "index": f["index"], "name": f["name"], "rules": f["rules"],
                    "tie_break": f["tie_break"], "density": f["density"],
                    "why": "two rules whose territories grew in the contests"})  # fmt: skip
    five = [f for f in contested["growing territories"] if f["family"] == "5 copies"][:COPIES]
    for f in five:
        out.append({"family": "copies", "index": f["index"], "name": f["name"],
                    "rules": f["rules"], "tie_break": f["tie_break"], "density": f["density"],
                    "why": "five species with one rule whose territories grew"})  # fmt: skip
    return out


def key(world: dict) -> tuple:
    return (world["family"], world["index"], world["tie_break"], world["density"])


def run(job: tuple[dict, int]) -> dict:
    world, seed = job
    found = organised.profile(
        world["rules"], world["tie_break"], SIDE, seed, TIMES, BLOCKS, world["density"]
    )
    return {**world, "side": SIDE, "seed": seed, **found}


def table(runs: list[dict], name: str) -> list[list[float | None]]:
    """One field's correlation areas, by reading and then by block, as the mean over the
    starts. None where any start has none."""
    out = []
    for i in range(len(runs[0]["times"])):
        row = []
        for k in range(len(runs[0]["blocks"])):
            values = [r["fields"][name]["area"][i][k] for r in runs if name in r["fields"]]
            whole = len(values) == len(runs) and all(v is not None for v in values)
            row.append(statistics.fmean(values) if whole else None)
        out.append(row)
    return out


def reading(runs: list[dict], name: str) -> dict:
    """One field of a world over its starts: what it is called and the numbers behind it."""
    times, blocks = runs[0]["times"], runs[0]["blocks"]
    mean = table(runs, name)
    largest = [row[-1] for row in mean]
    share = [round(statistics.fmean(r["fields"][name]["share"][i] for r in runs), 5)
             for i in range(len(times))]  # fmt: skip
    seen = [(a, t) for a, t in zip(largest, times, strict=True) if a is not None]
    peak, when = max(seen, default=(0.0, None))
    highest = {"area": round(peak, 2), "generation": when}
    if largest[-1] is None:
        return {
            "field": name,
            "called": "taken over" if peak >= TAKEN else "dead",
            "share": share,
            "area": [None if a is None else round(a, 2) for a in largest],
            "peak": highest,
        }
    by_start = [[r["fields"][name]["area"][i][-1] for r in runs] for i in range(len(times))]
    spread = [statistics.stdev(v) if len(v) > 1 and None not in v else None for v in by_start]
    late = organised.growth(largest[-3:], times[-3:])
    late_by_start = [organised.growth([row[s] for row in by_start[-3:]], times[-3:])
                     for s in range(len(runs))]  # fmt: skip
    scaling = organised.scaling(mean[-1], blocks, blocks[-3], blocks[-1])
    clocks = {}
    for wait in WAITS:
        ratios = organised.clock(mean, blocks, times, wait)
        clocks[str(wait)] = {"pairs": len(ratios),
                             "median": round(statistics.median(ratios), 3) if ratios else None,
                             "least": round(min(ratios), 3) if ratios else None,
                             "most": round(max(ratios), 3) if ratios else None}  # fmt: skip
    drift = share[-1] - share[0]
    smaller = [min(p, 1 - p) for p in (share[0], share[-1])]
    moving = abs(drift) >= DRIFT or smaller[1] < HALVED * smaller[0]
    if largest[-1] < search.LARGE:
        called = "taken over" if peak >= TAKEN and moving else "patches"
    elif late is None or late < search.STILL_GROWING:
        called = "organised"
    else:
        called = "taking over" if moving else "keeps growing"

    def tidy(value: float | None, places: int = 2) -> float | None:
        return None if value is None else round(value, places)

    return {
        "field": name,
        "called": called,
        "share": share,
        "drift": round(drift, 5),
        "area": [tidy(a) for a in largest],
        "peak": highest,
        "area_spread": [tidy(s) for s in spread],
        "length": [None if a is None else round(math.sqrt(a), 2) for a in largest],
        "growth_late": tidy(late, 3),
        "growth_late_by_start": [tidy(g, 3) for g in late_by_start],
        "growth_overall": tidy(organised.growth(largest, times), 3),
        "scaling": tidy(scaling, 3),
        "area_by_block_at_end": [tidy(a) for a in mean[-1]],
        "clock": clocks,
    }


def describe(runs: list[dict]) -> dict:
    """One world over its starts: by the field with the largest mean area at the end (or, if
    none has an area then, the field that had the largest one at any reading), and by each
    species' territory."""
    first = runs[0]
    several = len(first["rules"]) > 1
    names = [f"species {s + 1}" for s in range(len(first["rules"]))] if several else ["live"]
    shares = [round(statistics.fmean(r["fields"][n]["share"][-1] for r in runs), 5) for n in names]
    out = {k: first[k] for k in ("family", "index", "name", "rules", "tie_break", "density",
                                 "why")}  # fmt: skip
    kept = [contests.apart(r) for r in runs] if several else [None]
    out |= {
        "starts": len(runs),
        "live": [round(statistics.fmean(r["fields"]["live"]["share"][i] for r in runs), 5)
                 for i in range(len(first["times"]))],
        "shares": shares,
        "holding": sum(share >= search.HOLDS for share in shares),
        "apart": None if None in kept else round(statistics.fmean(kept), 3),
        "changed": round(statistics.fmean(r["changed"] for r in runs), 6),
    }  # fmt: skip
    at_end = {name: table(runs, name)[-1][-1] for name in first["fields"]}
    ever = {name: max((row[-1] for row in table(runs, name) if row[-1] is not None), default=0.0)
            for name in first["fields"]}  # fmt: skip
    if any(a is not None for a in at_end.values()):
        best = max((n for n in at_end if at_end[n] is not None), key=at_end.__getitem__)
    else:
        best = max(ever, key=ever.__getitem__)
    territories = [reading(runs, name) for name in names] if several else []
    return {**out, **reading(runs, best), "territories": territories}


def again(first: dict) -> bool:
    """Whether a world is run from the other starts too: only a known world, a rule alone, a
    contest or a pair whose first start, as `describe` gives it, keeps growing."""
    return first["called"] == "keeps growing" and first["family"] in MORE


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    picked = OUT / "candidates.json"
    if not picked.exists():  # picked once: a later look at the screen must not change the list
        screen = [search.describe(json.loads(line))
                  for line in (search.OUT / "records.jsonl").read_text().splitlines()]  # fmt: skip
        contested = json.loads((contests.OUT / "summary.json").read_text())
        picked.write_text(json.dumps(candidates(screen, contested), indent=1) + "\n")
    worlds = json.loads(picked.read_text())
    path = OUT / "records.jsonl"

    def finish(jobs: list[tuple[dict, int]]) -> dict[tuple, list[dict]]:
        """Run what has not been run, and give every world's records, in the order run."""
        done = set()
        if path.exists():
            done = {(*key(r), r["seed"]) for r in map(json.loads, path.read_text().splitlines())}
        todo = [(w, seed) for w, seed in jobs if (*key(w), seed) not in done]
        with ProcessPoolExecutor(args.workers) as pool, path.open("a") as sink:
            for record in pool.map(run, todo):
                sink.write(json.dumps(record) + "\n")
                sink.flush()
        by_world: dict[tuple, list[dict]] = {}
        for record in map(json.loads, path.read_text().splitlines()):
            by_world.setdefault(key(record), []).append(record)
        return by_world

    by_world = finish([(w, STARTS[0]) for w in worlds])
    firsts = {key(w): [r for r in by_world[key(w)] if r["seed"] == STARTS[0]] for w in worlds}
    more = [w for w in worlds if again(describe(firsts[key(w)]))]
    by_world = finish([(w, seed) for seed in STARTS[1:] for w in more])
    wanted = {key(w): STARTS if w in more else STARTS[:1] for w in worlds}
    found = [describe([r for r in by_world[k] if r["seed"] in seeds])
             for k, seeds in wanted.items()]  # fmt: skip
    summary = {"side": SIDE, "times": list(TIMES), "blocks": list(BLOCKS),
               "starts": list(STARTS), "large_area": search.LARGE,
               "still_growing": search.STILL_GROWING, "worlds": found}  # fmt: skip
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    for f in found:
        clocks = {wait: c["median"] for wait, c in f.get("clock", {}).items()}
        print(f"{f['called']}: {f['family']} {f['index']} {f['name']} ({f['tie_break']}, "
              f"density {f['density']:.3g}, {f['starts']} starts): {f['field']}, holding "
              f"{f['holding']}, share {f['share'][0]} to {f['share'][-1]}, area {f['area']}, "
              f"growth late {f.get('growth_late')} overall {f.get('growth_overall')}, scaling "
              f"{f.get('scaling')}, clock {clocks}")  # fmt: skip


if __name__ == "__main__":
    main()
