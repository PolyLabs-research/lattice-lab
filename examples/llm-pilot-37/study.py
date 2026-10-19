"""
The m = 37 pilot's registered test: the census of unexplained cube confinements at held-out sizes.

    uv run python examples/llm-pilot-37/study.py register
    uv run python examples/llm-pilot-37/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot-37

The question is open, so nothing the agent will claim can be registered before it claims it.
What is registered, before the agent starts, is the held-out grid and the orchestrator's own
expectation there. The agent's mechanism, fixed in its submission, is then judged against these
records, which it never sees.

- The grid: the odd m from 163 to 225 with ord_m(2) even (where the cubes are a proper subgroup),
  and the multiples 259 and 333 of 37. The census the agent is given stops at 161.
- The expectation: from the census up to 161, unexplained cube confinement is a small-field
  effect below 37, and above 37 it is rare (one rule at 69 so far). So at each held-out m the
  orchestrator predicts **none**.

Each record holds every rule that is confined at that m and not accounted for by the known
mechanisms (census.unexplained), so any mechanism can be scored against it.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import census  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

SIZES = census.cube_sizes(163, 225) + [m for m in (259, 333) if m in census.cube_sizes(259, 333)]


def question() -> dict:
    return {
        "id": "llm-pilot-37",
        "title": "Unexplained cube confinement at held-out odd m",
        "statement": "At each odd m in the grid, no shell rule of the atlas has all its nonzero "
        "eigenvalues cubes unless the known mechanisms (splitting, powers, dilations, the twisted "
        "power) account for it (the orchestrator's expectation). The records list every exception "
        "found, for judging the agent's mechanism.",
        "rules": "all 1,274 shell rules (atlas3.all_rules on square, triangle, hexagon)",
        "sizes": SIZES,
        "excluded_seen": [],
        "checker": "census.unexplained(m, q=3)",
        "hypotheses": {"none": "no unexplained cube confinement at any held-out m"},
    }


def predictions() -> list[dict]:
    return [{"m": m, "predicted_unexplained": 0} for m in SIZES]


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {json.loads(line)["m"] for line in path.read_text().splitlines() if line}
    for body in predictions():
        if body["m"] in done:
            continue
        start = time.time()
        rows = census.unexplained(body["m"])
        append_records(path, [{**body, "unexplained": rows, "count": len(rows),
                               "seconds": round(time.time() - start, 1)}])  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by_m = {r["m"]: r for r in rows}
    missing = [p["m"] for p in registered if p["m"] not in by_m]
    exceptions = [r for m in sorted(by_m) for r in by_m[m]["unexplained"]]
    return {
        "missing": missing,
        "exceptions": len(exceptions),
        "sizes_with_exceptions": sorted({r["m"] for r in exceptions}),
        "none": "supported" if not exceptions and not missing else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
