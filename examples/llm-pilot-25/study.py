"""
The m = 25 pilot's registered test: the square family's census at held-out sizes.

    uv run python examples/llm-pilot-25/study.py register
    uv run python examples/llm-pilot-25/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot-25

The question is open, so the agent's answer cannot be registered before it gives it. What is
registered, before the agent starts, is the grid and the orchestrator's expectation there. The
agent's condition, fixed in its submission, is then judged against these records, which it is
never shown.

- The grid: every odd m from 27 to 75 at which the cubes are a proper subgroup of the
  eigenvalues' field (14 sizes). The agent's data stops at 25.
- The census at each m (cubes25.census_at): every rule of the family (all 32,767 symmetric
  square rules within distance 4) whose nonzero eigenvalues are all cubes, which the atlas
  procedure does not predict and which no symmetry forces; and the chance model's expected
  count, computed in the same pass. Each such rule is then put to the m = 37 pilot's condition
  (llm-pilot-37/submission/mechanism.py), and those it explains are counted apart.
- The expectation: from the census remainder, unexplained structure was found at m = 25 alone,
  so at each held-out m the orchestrator expects the rest to be chance: at most the expected
  count plus three standard deviations, plus one.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cubes25  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402


def _sord(m: int) -> int:
    return next(j for j in range(1, m) if pow(2, j, m) in (1, m - 1))


# The cubes are a proper subgroup of the symmetric rules' eigenvalue field F(2^sord(m)) exactly
# when sord(m) is even; elsewhere every such eigenvalue is a cube and there is nothing to find.
SIZES = [m for m in cubes25.census.cube_sizes(27, 75) if _sord(m) % 2 == 0]


def question() -> dict:
    return {
        "id": "llm-pilot-25",
        "title": "Unexplained cube confinement in the square family at held-out odd m",
        "statement": "At each odd m in the grid, the symmetric square rules within distance 4 that "
        "are confined to the cubes, beyond the atlas procedure, forced subfields and the m = 37 "
        "pilot's half-Frobenius mechanism, number no more than chance gives (the orchestrator's "
        "expectation). The records list every such rule, for judging the agent's mechanism.",
        "rules": "the square family: all 32,767 unions of the D4 orbits of the translations with "
        "coordinates in [-4, 4] (tools/family.py)",
        "sizes": SIZES,
        "excluded_seen": [
            "the atlas's 1,022 square rules, which are family members, at every size here "
            "(census-remainder/expected.jsonl): beyond known mechanisms, confined only at 37, "
            "five rules, all explained by the m = 37 pilot",
            "a random 1,500 of the family at m = 29 (census-remainder/calibrate.py, seed 1): "
            "none confined, 0.26 expected",
        ],
        "checker": "cubes25.census_at(m), then the m = 37 pilot's condition on each confined rule",
        "hypotheses": {
            "chance": "at every m, the confined rules no known mechanism explains number at most "
            "expected + 3 sd + 1"
        },
    }


def predictions() -> list[dict]:
    return [{"m": m, "predicted": "at most expected + 3 sd + 1"} for m in SIZES]


def _pilot4():
    import importlib.util

    tools = cubes25.EX / "llm-pilot-37" / "tools"
    sys.path.insert(0, str(tools))
    path = cubes25.EX / "llm-pilot-37" / "submission" / "mechanism.py"
    spec = importlib.util.spec_from_file_location("pilot37_mechanism", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.path.remove(str(tools))
    return module


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {json.loads(line)["m"] for line in path.read_text().splitlines() if line}
    pilot4 = _pilot4()
    for body in predictions():
        m = body["m"]
        if m in done:
            continue
        start = time.time()
        r = cubes25.census_at(m)
        for hit in r["hits"]:
            hit["pilot4_q"] = int(pilot4.condition(cubes25.family.rule(hit["id"]), m))
        unexplained = [h for h in r["hits"] if h["pilot4_q"] % 3]
        record = {**body, **r, "unexplained": len(unexplained)}
        append_records(path, [{**record, "seconds": round(time.time() - start)}])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by_m = {r["m"]: r for r in rows}
    missing = [p["m"] for p in registered if p["m"] not in by_m]
    beyond = [
        m for m, r in sorted(by_m.items()) if r["unexplained"] > r["expected"] + 3 * r["sd"] + 1
    ]
    return {
        "missing": missing,
        "sizes_beyond_chance": beyond,
        "unexplained": {m: r["unexplained"] for m, r in sorted(by_m.items())},
        "explained_by_pilot4": {m: r["observed"] - r["unexplained"] for m, r in by_m.items()},
        "chance": "supported" if not beyond and not missing else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
