"""
More starts of one world at one side, to check something the registered runs showed.
Exploratory: nothing here is registered, and the starts are ones no other run used.

    uv run --no-sync python examples/scale-up-sizes/recheck.py "pair standoff" 2048 5001 5016

Runs the world of that name (as in examples/scale-up-compete/laws.py) at that side from every
start in the range, and adds the records to recheck/records.jsonl (LatticeLife's own,
resumable). Why it exists: in the large part of the scale-up test the pair's live fraction at
generation 1,000 came out higher at side 2048 than at side 4096 by five standard errors, with
16 starts each. Each registered claim held, because it was judged against the small grids'
constant and its much larger error; but two large grids should agree with each other, so the
side-2048 runs were repeated from fresh starts.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

from latticelife.experiments.competition import CompetitionTask, run_competition
from latticelife.experiments.harness import read_jsonl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scale-up-compete"))

import laws  # noqa: E402

OUT = HERE / "recheck"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("world", choices=list(laws.WORLDS))
    parser.add_argument("side", type=int)
    parser.add_argument("first", type=int)
    parser.add_argument("last", type=int)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    rules, kind, steps, every = laws.WORLDS[args.world]
    tasks = [
        CompetitionTask(tuple(rules), "square", args.side, 0.5, seed, steps, tie_break=kind,
                        sample_every=every)
        for seed in range(args.first, args.last + 1)
    ]  # fmt: skip
    OUT.mkdir(exist_ok=True)
    for _ in run_competition(tasks, str(OUT / "records.jsonl"), args.workers):
        pass
    runs = [
        r
        for r in read_jsonl(OUT / "records.jsonl")
        if laws.world_of(r) == args.world and r["cells"] == args.side**2
    ]
    for quantity in ("live", "share", "unlike"):
        values = [laws.measure(r, quantity, -1) for r in runs]
        spread = statistics.stdev(values)
        print(
            f"{args.world}, side {args.side}, {len(runs)} starts: {quantity} "
            f"{statistics.fmean(values):.6f} ± {spread / math.sqrt(len(runs)):.6f}"
            f" (spread {spread:.6f})"
        )


if __name__ == "__main__":
    main()
