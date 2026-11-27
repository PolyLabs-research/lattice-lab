"""
Sizing for the registered test of whether a rule that remembers carries the class.
Exploratory: nothing here is registered.

    uv run --no-sync python examples/scale-up-class-memory/sizing.py run --workers 2
    uv run --no-sync python examples/scale-up-class-memory/sizing.py

**What is run** (`run`). Eleven of the 29 worlds and the still world, each from starts that
step 4f had already run, so runs I had seen, put through the study's own run
(`study.execute`): the fine runs read every two generations, each world's tick from its
walls, its tallies on that clock, and the run-ons of its four rules. It is done twice, the
starts changing places: what a world learns from one way round it is tried on the other.
The still world and two others have four starts (two to learn from and two to try on, as
the registered run will have); the rest have two.

**Which worlds.** Five of the ten that step 4f found served, the fullest and the thinnest
of them among these; one of the four nearly served; five of the ten it found missed, the
nearest to served and the furthest among these. None of the five just missed. That leaves
eighteen of the 29 worlds that this look did not see.

**What is kept.** The records go to ~/lattice-lab-runs/class-memory/ (they are not
registered). Without `run`, the summary is made from them: every claim the study makes of a
sized world, with the value each way round gave and whether it would have held; and for
each bound, the least and the most that the worlds carrying it gave. That goes to
sizing.json, which the registration carries.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _module(name: str, path: Path):
    """A module from its file, under a name of its own: the examples hold several study.py."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


study = _module("scale_up_class_memory_study", HERE / "study.py")

OUT = HERE / "sizing.json"
KEPT = Path.home() / "lattice-lab-runs" / "class-memory"
STILL_SEEN = 17901  # the first of the still world's starts in step 4f
SIZED = {  # a world, and how many of its starts in step 4f it is run from here
    study.STILL: 4,
    "B345/S02457": 4,  # served
    "B23456/S34678": 2,  # served, and the slowest of the served
    "B34568/S247": 2,  # served, and the thinnest of them
    "B356/S2456": 2,  # served
    "B23456/S4678": 2,  # served, and the fastest
    "B24567/S0135678": 2,  # nearly served
    "B13458/S358": 2,  # missed, and the nearest to served
    "B2478/S1467": 2,  # missed
    "B25/S078": 4,  # missed, and the furthest
    "B24678/S1348": 2,  # missed, slow
    "B25/S678": 2,  # missed, and the thinnest
}
WAYS = ("the first half to learn from", "the last half to learn from")


def seen() -> dict[str, list[int]]:
    """The starts of step 4f that each sized world is run from here."""
    before = json.loads((study.STEP_4F / "worlds.json").read_text())["worlds"]
    first = {w["rule"]: w["first"] for w in before} | {study.STILL: STILL_SEEN}
    return {rule: list(range(first[rule], first[rule] + n)) for rule, n in SIZED.items()}


def chosen() -> dict[str, dict]:
    """The sized worlds, with what step 4f found of each (as worlds.json will hold them)."""
    found = {w["rule"]: w for w in study.select()}
    return {rule: found[rule] for rule in SIZED}


def plans() -> dict[str, dict]:
    """Which starts each world learns from and is tried on, each way round."""
    out: dict = {way: {} for way in WAYS}
    for rule, seeds in seen().items():
        half = len(seeds) // 2
        out[WAYS[0]][rule] = {"learn": seeds[:half], "try": seeds[half:]}
        out[WAYS[1]][rule] = {"learn": seeds[half:], "try": seeds[:half]}
    return out


def records(way: str) -> Path:
    return KEPT / f"sizing-records-{WAYS.index(way) + 1}.jsonl"


def run(workers: int) -> None:
    """The study's own run on the sized worlds, each way round."""
    KEPT.mkdir(parents=True, exist_ok=True)
    for way, plan in plans().items():
        study.execute(records(way), workers, plan)
        print(f"{way}: {len(records(way).read_text().splitlines())} records", flush=True)


def bound_of(claim: dict) -> str:
    """A claim's name without its world: what the claims of one bound share."""
    world = claim["world"]
    label = claim["label"] if world is None else claim["label"].replace(f" {world}", "", 1)
    return label


def summary() -> dict:
    sized = chosen()
    registered = study.claims(sized)
    claims: dict = {c["label"]: {"at least": c["at_least"], "at most": c["at_most"]}
                    for c in registered}  # fmt: skip
    worlds: dict = {rule: {"group": "the still world" if rule == study.STILL
                           else study.group(sized[rule]), "starts": seeds}
                    for rule, seeds in seen().items()}  # fmt: skip
    bounds: dict = {}
    for way, plan in plans().items():
        rows = [json.loads(line) for line in records(way).read_text().splitlines()]
        m = study.Measures(rows, plan, chosen=sized)
        for c in registered:
            value = m.value(c)
            would = study.judge(value, c, m.stands(c["world"]))
            claims[c["label"]][way] = {"value": study.number(value), "would": would}
            b = bounds.setdefault(
                bound_of(c),
                {"at least": c["at_least"], "at most": c["at_most"], "values": [], "would": []},
            )
            b["values"].append(value)
            b["would"].append(would)
        for rule in SIZED:
            worlds[rule][way] = study.told(m, rule)
    drawn = {}
    for name, b in bounds.items():
        values = [v for v in b["values"] if v is not None]
        drawn[name] = {
            "at least": b["at least"],
            "at most": b["at most"],
            "the sized worlds gave, both ways round": {
                "values": len(values),
                "least": study.number(min(values)) if values else None,
                "most": study.number(max(values)) if values else None,
                "would have held": b["would"].count("holds"),
                "would have failed": b["would"].count("fails"),
                "not tested": b["would"].count("not tested"),
            },
        }  # fmt: skip
    return {
        "what": "the sizing look for the registered test of this folder (sizing.py, "
                "exploratory): the study's own run and measures on worlds and starts that step "
                "4f had already run, twice, the starts a world learns from and is tried on "
                "changing places",
        "what the bounds were drawn from": drawn | NOTES,
        "the sized worlds": worlds,
        "the study's claims of the sized worlds": claims,
    }  # fmt: skip


# what the numbers above do not say by themselves (written once they were in)
NOTES: dict = {
    "where the runs were made": "on a rented pod (2026-11-27; the thirty fine runs side by "
    "side and both ways round in 18 minutes), this machine being taken by another job. "
    "Twelve of the thirty had been made here first: their leaders and shares are the pod's, "
    "entry for entry. And the records of four worlds, made again here from the kept runs "
    "with the study's code as registered, are the pod's byte for byte",
    "two starts or four": "the still world, B345/S02457 and B25/S078 have two starts to "
    "learn from and two to try on, as the registered run has; the other nine have one and "
    "one. Those three read with one and one as well (four ways each) give, on average: the "
    "share of surprise that how long removes 0.6 to 1.0 points lower (a rule with more in "
    "view has more to learn); the look's rule with how long in view 0.9 to 1.1 points of "
    "surprise better beside the world's own in the first two (a world's own rule that has "
    "learned from less is the worse rule), and 9 points in B25/S078, where it is 150% "
    "worse; the look's plain rule beside the world's own the same to 0.3 points; and every "
    "run-on and every ratio of run-ons the same to 0.01, a single trial start lying up to "
    "0.05 from that. So in the registered run the nine should remove nearly a point more "
    "than here, and the look's remembering rule should stand a point less well beside the "
    "world's own, one tick ahead",
    "the worlds between": "one of the four nearly served was sized, and none of the five "
    "just missed. The claims J of those five rest on no run of them. In the nine sized "
    "worlds where step 4f found the still world's rule 0.48% or more from the "
    "world's own at its best pace, the look's plain rule on the world's own clock is 1.3 to "
    "2.2 times as far. With how long in view it is 2.3 and 2.4 points nearer in the world "
    "nearly served, and 1 to 88 points further in the five missed. Step 4f missed the five "
    "between by 3.8% to 6.9%",
    "what a claim stands on": "in every sized world the larger species has 0.52 to 0.57 of "
    "the live cells at generation 4,096 (the bound is 0.8), and every one has a tick, the "
    "longest 64 generations (the bound is 80)",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("step", nargs="?", choices=["run"], help="make the runs first")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.step == "run":
        run(args.workers)
    found = summary()
    OUT.write_text(json.dumps(found, indent=1) + "\n")
    for name, b in found["what the bounds were drawn from"].items():
        print(name, json.dumps(b))


if __name__ == "__main__":
    main()
