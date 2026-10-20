"""
A registered test of Claude Fable's criterion for rule 90's cube confinement.

    uv run python examples/fable-units/study.py register
    uv run python examples/fable-units/study.py run
    uv run lattice-lab verify --lab examples/fable-units

Fable, consulted on the m = 37 cubes (docs/consultations.md), claimed: for a prime p = 5 (mod 8)
at which 2 is a primitive root, 1 + zeta is a cube in F(2^(p-1)), equivalently rule 90 is
confined to the cubes at p, exactly when eps^h lies in Z[sqrt p] (eps the fundamental unit, h the
class number of Q(sqrt p)); and at p = i^2 + 1 where this holds, the pyramid rule (centre and
square rings at radii 2, 4, ..., i/2 - 1) is confined to the cubes, while the next-smaller
pyramid is not. It checked p < 200 itself.

The predictions are computed from eps and h alone (units.predicted: Pell's equation and reduced
quadratic forms, no cyclotomic arithmetic) and registered before anything is computed at these
primes. The run then decides each case directly (units.confined: the norm of 1 + zeta to F(4);
units.pyramid_confined: every eigenvalue of the pyramid).

- The grid: every eligible prime from 302 to 20,000 (405), and the pyramid primes among them
  below 10,000 (677, 4357, 5477, 8837).
- Seen: every eligible prime up to 301. Fable checked p < 200; the orchestrator checked p < 200
  again today; and the sixth pilot's agent listed the m <= 301 at which rule 90 is confined to the
  cubes (37, 95, 101, 111, 141, 197, 203, 269), which settles every eligible prime up to 301.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import units  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

LO, HI, PYRAMID_HI = 302, 20000, 10000


def question() -> dict:
    return {
        "id": "fable-units",
        "title": "Fable's unit criterion for rule 90's cube confinement, and its pyramid rules",
        "statement": "For each prime p = 5 (mod 8) with 2 a primitive root, 302 <= p < 20000: rule "
        "90 is confined to the cubes at p (1 + zeta is a cube in F(2^(p-1))) exactly when eps^h "
        "lies in Z[sqrt p]. At p = i^2 + 1 below 10000 where it holds, the pyramid with rings at "
        "radii 2, 4, ..., i/2 - 1 is confined to the cubes, and the pyramid without its largest "
        "ring is not.",
        "source": "Claude Fable, consulted 2026-10-20 on the m = 37 cubes (docs/consultations.md)",
        "sizes": units.eligible(LO, HI),
        "excluded_seen": [
            "every eligible prime up to 301: Fable and the orchestrator checked p < 200, and the "
            "sixth pilot's agent listed where rule 90 is confined to the cubes for m <= 301"
        ],
        "checker": "units.confined (norm of 1 + zeta to F(4)); units.pyramid_confined (every "
        "eigenvalue of the pyramid, as a norm to F(4))",
        "hypotheses": {
            "criterion": "predicted == observed at every prime of the grid",
            "pyramids": "every predicted pyramid is confined and every neighbour is not",
        },
    }


def predictions() -> list[dict]:
    out = []
    for p in units.eligible(LO, HI):
        a, b = units.fundamental_unit(p)
        h = units.class_number(p)
        out.append({"test": "unit", "p": p, "eps_parity": [a % 2, b % 2],
                    "eps_digits": len(str(a)), "h": h, "predicted": units.predicted(p)})  # fmt: skip
    for p, i in units.pyramid_primes(LO, PYRAMID_HI):
        if units.predicted(p):
            rings = list(units.pyramid_rings(i))
            out.append({"test": "pyramid", "p": p, "i": i, "rings": rings, "predicted": True})
            out.append({"test": "pyramid neighbour", "p": p, "i": i, "rings": rings[:-1],
                        "predicted": False})  # fmt: skip
    return out


def execute(path: Path, workers: int) -> None:
    done = set()
    if path.exists():
        done = {(r["test"], r["p"]) for r in map(json.loads, path.read_text().splitlines())}
    for body in predictions():
        if (body["test"], body["p"]) in done:
            continue
        start = time.time()
        if body["test"] == "unit":
            observed = units.confined(body["p"])
        else:
            observed = units.pyramid_confined(body["p"], tuple(body["rings"]))
        append_records(path, [{**body, "observed": observed,
                               "seconds": round(time.time() - start, 2)}])  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by = {(r["test"], r["p"]): r for r in rows}
    missing = [(p["test"], p["p"]) for p in registered if (p["test"], p["p"]) not in by]
    wrong = [{"test": t, "p": p, "predicted": r["predicted"], "observed": r["observed"]}
             for (t, p), r in sorted(by.items()) if r["predicted"] != r["observed"]]  # fmt: skip
    unit = [r for r in rows if r["test"] == "unit"]
    return {
        "missing": missing,
        "wrong": wrong,
        "unit": {
            "primes": len(unit),
            "agree": sum(r["predicted"] == r["observed"] for r in unit),
            "confined": sum(r["observed"] for r in unit),
        },  # fmt: skip
        "criterion": "supported"
        if not missing and not [w for w in wrong if w["test"] == "unit"]
        else "refuted",
        "pyramids": "supported"
        if not missing and not [w for w in wrong if w["test"] != "unit"]
        else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
