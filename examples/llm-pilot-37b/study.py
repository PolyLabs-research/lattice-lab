"""
The sixth pilot's registered test: the square family's census at held-out sizes.

    uv run python examples/llm-pilot-37b/study.py register
    uv run python examples/llm-pilot-37b/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot-37b

As in the fifth pilot, the question is open, so what is registered before the agent starts is
the grid and the orchestrator's expectation there. The agent's condition, fixed in its
submission, is then judged against these records, which it is never shown.

- The grid: every odd m from 77 to 125 at which the cubes are a proper subgroup of the symmetric
  rules' eigenvalue field (17 sizes). The agent's data stops at 75.
- The census at each m (cubes25.census_at): every family rule confined to the cubes that the
  atlas procedure does not predict and no symmetry forces, and the chance model's expected
  count. Each such rule is then put to the fourth and fifth pilots' conditions (cubes37b.known_q),
  and those they explain are counted apart. So are rules the procedure finds to split into
  one-dimensional factors: its split step predicts one factor's period, which is too large when
  the factors' eigenvalues are correlated (as at m = 115, docs/census-remainder.md), so a
  confined split rule is a known mechanism the procedure mispredicts, not an unexplained one.
- The expectation: at each m, the rest is chance: at most the expected count plus three standard
  deviations, plus one. The fifth pilot's census refuted this expectation at 37 and 61 (and, with
  pilot 4's condition alone counted, at four more sizes); this registers it again, with both
  pilots' conditions counted, at sizes nobody has computed.

The census's slow steps (atlas3's split search and root test) do not depend on m. The run warms
their caches at m = 21, a size already in the agent's data, and then forks workers that share
them, one size each.
"""

from __future__ import annotations

import json
import multiprocessing
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import cubes37b  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402


def _sord(m: int) -> int:
    return next(j for j in range(1, m) if pow(2, j, m) in (1, m - 1))


SIZES = [m for m in cubes37b.census.cube_sizes(77, 125) if _sord(m) % 2 == 0]
WARM = 21


def question() -> dict:
    return {
        "id": "llm-pilot-37b",
        "title": "Unexplained cube confinement in the square family at odd m from 77 to 125",
        "statement": "At each odd m in the grid, the symmetric square rules within distance 4 that "
        "are confined to the cubes, beyond the atlas procedure, forced subfields and the fourth "
        "and fifth pilots' conditions, number no more than chance gives (the orchestrator's "
        "expectation). The records list every such rule, for judging the agent's mechanism.",
        "rules": "the square family: all 32,767 unions of the D4 orbits of the translations with "
        "coordinates in [-4, 4] (tools/family.py)",
        "sizes": SIZES,
        "excluded_seen": [
            "the atlas's 1,022 square rules, which are family members, at every census size up to "
            "161 (census-remainder/expected.jsonl): beyond known mechanisms, confined only at 37 "
            "and 115 among these sizes, both explained",
            "the family at m = 21, 25 and 29 to 75 (the fifth pilot's census), which is the "
            "agent's data",
        ],
        "checker": "cubes25.census_at(m), then cubes37b.known_q on each confined rule",
        "hypotheses": {
            "chance": "at every m, the confined rules no known mechanism explains number at most "
            "expected + 3 sd + 1"
        },
    }


def predictions() -> list[dict]:
    return [{"m": m, "predicted": "at most expected + 3 sd + 1"} for m in SIZES]


def split(hit: dict) -> bool:
    return hit["procedure"].startswith("splits")


def _one(m: int) -> dict:
    start = time.time()
    r = cubes37b.cubes25.census_at(m)
    for hit in r["hits"]:
        f = cubes37b.family.rule(hit["id"])
        hit["known_q"] = int(cubes37b.known_q(f, m))
        hit["procedure"] = cubes37b.cubes25.atlas3.predict(f, m)[1]
    unexplained = [h for h in r["hits"] if h["known_q"] % 3 and not split(h)]
    return {"m": m, "predicted": "at most expected + 3 sd + 1", **r,
            "unexplained": len(unexplained), "seconds": round(time.time() - start)}  # fmt: skip


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {json.loads(line)["m"] for line in path.read_text().splitlines() if line}
    todo = [m for m in SIZES if m not in done]
    if not todo:
        return
    for _, f in cubes37b.family.rules():  # warm the m-independent caches at a seen size
        cubes37b.cubes25.atlas3.predict(f, WARM)
    cubes37b.conditions()
    with multiprocessing.get_context("fork").Pool(max(1, workers)) as pool:
        for record in pool.imap_unordered(_one, sorted(todo, reverse=True)):
            append_records(path, [record])


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
        "explained_by_known": {m: r["observed"] - r["unexplained"] for m, r in by_m.items()},
        "splits": {m: sum(split(h) for h in r["hits"]) for m, r in by_m.items()},
        "chance": "supported" if not beyond and not missing else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
