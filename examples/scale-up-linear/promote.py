"""
The gate of the scale-up plan's step 1 (docs/scale-up-plan.md): LatticeLife's own
`experiments.coarse`, the instrument's new home, must reproduce every record of this study's
registered run.

    uv run --no-sync python examples/scale-up-linear/promote.py [--workers 1]

The registered run (2026-11-23) went through this directory's scaleup.py. This reads the
registered cases from the ledger and the records as they were written, runs every case again
through `latticelife.experiments.coarse.closure` from the start its seed names, and compares each
record with the stored line as canonical JSON. It writes promotion.json and exits with status 1
if any record differs.

Not registered: nothing here is a prediction. A difference would be a fault in the move.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from latticelife.experiments import coarse

HERE = Path(__file__).resolve().parent


def canonical(record: dict) -> str:
    """One record as its line in records.jsonl (lattice_lab.ledger.canonical, for plain JSON)."""
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def registered_cases() -> dict[int, dict]:
    entries = map(json.loads, (HERE / "ledger.jsonl").read_text().splitlines())
    return {e["body"]["case"]: e["body"] for e in entries if e["kind"] == "prediction"}


def stored_lines() -> dict[tuple[int, int], str]:
    lines = (HERE / "records.jsonl").read_text().splitlines()
    return {(r["case"], r["seed"]): line for line in lines for r in [json.loads(line)]}


def diagram(case: dict) -> coarse.Diagram:
    fine = coarse.World(case["shape"], case["rule"], case["side"])
    small = coarse.World(
        case["shape"], case["coarse_rule"], case["coarse_side"], case["coarse_dilation"]
    )
    projection = coarse.Projection(case["projection"], case["block"], tuple(case["offset"]))
    return coarse.Diagram(fine, small, projection, case["clock"])


def bundles(cases: dict[int, dict]) -> list[tuple[list[dict], int]]:
    """(cases that share a fine run, seed), as the registered run grouped them."""
    groups: dict[tuple, list[dict]] = {}
    for case in cases.values():
        key = (case["shape"], case["rule"], case["side"], case["clock"], case["coarse_steps"],
               tuple(case["seeds"]))  # fmt: skip
        groups.setdefault(key, []).append(case)
    jobs = [(group, seed) for group in groups.values() for seed in group[0]["seeds"]]
    return sorted(jobs, key=lambda job: -(job[0][0]["side"] ** 2) * job[0][0]["clock"])


def rerun(job: tuple[list[dict], int]) -> list[dict]:
    group, seed = job
    first = group[0]
    start = coarse.uniform_start(first["shape"], first["side"], seed)
    results, last = coarse.closure([diagram(c) for c in group], start, first["coarse_steps"])
    return [
        {
            "case": case["case"],
            "seed": seed,
            "supercells": result.supercells,
            "mismatches": list(result.mismatches),
            "live": list(result.live),
            "start_sha256": coarse.digest(start),
            "fine_sha256": last,
        }
        for case, result in zip(group, results, strict=True)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--out", type=Path, default=HERE / "promotion.json")
    args = parser.parse_args(argv)
    cases, stored = registered_cases(), stored_lines()
    jobs = bundles(cases)
    began = time.time()
    if args.workers <= 1:
        batches = map(rerun, jobs)
    else:
        pool = ProcessPoolExecutor(args.workers)
        batches = pool.map(rerun, jobs)
    seen, different = set(), []
    for batch in batches:
        for record in batch:
            key = (record["case"], record["seed"])
            seen.add(key)
            if stored.get(key) != canonical(record):
                different.append({"case": key[0], "seed": key[1]})
    try:
        from lattice_lab.provenance import provenance

        code = provenance()
    except ImportError:  # run from an environment without lattice-lab: the comparison stands
        code = None
    report = {
        "through": "latticelife.experiments.coarse.closure",
        "cases": len(cases),
        "records": len(stored),
        "rerun": len(seen),
        "identical": len(seen) - len(different),
        "different": different[:20],
        "not_rerun": len(set(stored) - seen),
        "seconds": round(time.time() - began),
        "provenance": code,
    }
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "provenance"}))
    return 0 if not different and seen == set(stored) else 1


if __name__ == "__main__":
    sys.exit(main())
