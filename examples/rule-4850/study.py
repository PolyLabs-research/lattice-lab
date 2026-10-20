"""
A registered test of whether rule 4850's ninth powers at m = 37 are a coincidence.

    uv run --no-sync python examples/rule-4850/study.py register
    uv run --no-sync python examples/rule-4850/study.py run
    uv run --no-sync lattice-lab verify --lab examples/rule-4850

Rule 4850 is the only rule of the square family (radius 4) whose nonzero eigenvalues at 37 are
all ninth powers that mechanisms 1 to 4 do not explain. Two Fable consultations
(consultations/2026-10-20-rule-4850) found no mechanism; one gave a certificate (every line's
projection, alone or twisted with a hub, is a product of cyclotomic polynomials mod x^37 - 1),
the other calibrated chance (each of the eight generic classes a ninth power about one time in
nine, independently, the diagonal 0.47, so about 1.1e-8 per rule) and proposed this test:

    extend the family to the 21 orbits with 0 <= b <= a <= 5 (2^21 - 1 rules) at m = 37; under
    "4850 is a coincidence", the ninth-power rules among the new ones that mechanisms 1 to 4 do
    not explain, and that are not images of 4850, number 0 (expected about 0.02); two or more
    mean a mechanism.

- New rules: those using at least one orbit of radius 5 (2^21 - 2^15 of them). The 32,767 of
  radius at most 4 are seen.
- Confinement: census.py, every class's value looked up in a table of discrete logs; checked on
  the radius-4 family, where it gives the 110 cube, 21 ninth-power and 4 27th-power rules found
  by the group-ring computation.
- Explained: the atlas procedure (atlas3.predict: monomials, dilations, powers 3, 5, 7,
  splitting) predicts an odd part dividing 29,127 = (2^18 - 1)/9, or finds that the rule splits
  (mixed splits included, as in the sixth pilot's census). On the radius-4 family this marks the
  other 20 ninth-power rules explained and 4850 not.
- Images of 4850: an invertible map of the exponents mod 37 with entries in [-6, 6] that sends
  4850's support onto the rule's.
"""

from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "linear-atlas-3"))

import atlas3  # noqa: E402
import census  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

RADIUS, SEEN_RADIUS = 5, 4
NINTH = (2**18 - 1) // 9  # 29,127


def question() -> dict:
    return {
        "id": "rule-4850-radius-5",
        "title": "Is rule 4850's ninth-power confinement at m = 37 a coincidence?",
        "statement": "Among the rules of the radius-5 square family that use an orbit of radius "
        "5, count those whose nonzero eigenvalues at m = 37 are all ninth powers, that the atlas "
        "procedure (mechanisms 1 to 4) does not explain, and that are not images of rule 4850 "
        "under an invertible exponent map. A coincidence predicts 0 or 1 (expected about 0.02); "
        "2 or more mean a mechanism.",
        "source": "Claude Fable, consulted 2026-10-20 (consultations/2026-10-20-rule-4850, "
        "fable-r2, prediction P1)",
        "sizes": [37],
        "excluded_seen": ["the 32,767 rules of radius at most 4 (the sixth pilot's family)"],
        "checker": "census.py (class values, discrete logs mod 27) and atlas3.predict",
        "hypotheses": {
            "coincidence": "at most 1 unexplained new ninth-power rule",
            "mechanism": "at least 2",
        },
    }


def predictions() -> list[dict]:
    return [{"test": "unexplained new ninth-power rules at 37, radius 5",
             "predicted": "0 or 1 (coincidence); 2 or more would mean a mechanism"}]  # fmt: skip


def _explained(f: frozenset) -> tuple[bool, int | None, str]:
    odd, why = atlas3.predict(f, 37)
    return ("splits" in why or (odd is not None and NINTH % odd == 0)), odd, why


def _image_of_4850(f: frozenset) -> list[int] | None:
    target = frozenset((p % 37, q % 37) for p, q in f)
    source = census.rule(4850)
    for a, b, c, d in itertools.product(range(-6, 7), repeat=4):
        if (a * d - b * c) % 37 == 0:
            continue
        if frozenset(((a * p + b * q) % 37, (c * p + d * q) % 37) for p, q in source) == target:
            return [a, b, c, d]
    return None


def execute(path: Path, workers: int) -> None:
    if path.exists() and path.read_text().strip():
        return  # one pass, a few minutes: rerun from scratch rather than resume
    start = time.time()
    logs = census.class_logs(RADIUS)
    n = logs.shape[1]
    ids = np.arange(n)
    new = ids >= 1 << len(census.orbits(SEEN_RADIUS))
    masks = {q: census.confined(logs, q) for q in (3, 9, 27)}
    # the per-class null, measured on the new rules: each class a ninth power (or zero) with
    # its own rate, independently
    ok9 = (logs == census.ZERO) | (logs % 9 == 0)
    rates = ok9[:, new].mean(axis=1)
    rows = []
    for rid in np.flatnonzero(masks[9] & new):
        f = census.rule(int(rid))
        explained, odd, why = _explained(f)
        rows.append({
            "test": "hit", "id": int(rid),
            "orbits": [list(o) for i, o in enumerate(census.orbits(RADIUS)) if rid >> i & 1],
            "logs": [int(v) for v in logs[:, rid]], "q27": bool(masks[27][rid]),
            "procedure": why, "predicted_odd": odd, "explained": explained,
            "image_of_4850": None if explained else _image_of_4850(f),
        })  # fmt: skip
    summary = {
        "test": "summary", "new_rules": int(new.sum()),
        "confined_new": {str(q): int((masks[q] & new).sum()) for q in (3, 9, 27)},
        "confined_seen": {str(q): int((masks[q] & ~new).sum()) - 1 for q in (3, 9, 27)},
        "class_rates_new": [round(float(r), 4) for r in rates],
        "expected_by_chance_new": float(new.sum() * np.prod(rates)),
        "seconds": round(time.time() - start, 1),
    }  # fmt: skip
    append_records(path, rows + [summary])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    hits = [r for r in rows if r["test"] == "hit"]
    summary = next((r for r in rows if r["test"] == "summary"), None)
    unexplained = [r for r in hits if not r["explained"] and not r["image_of_4850"]]
    return {
        "missing": [] if summary else ["summary"],
        "ninth_power_new": len(hits),
        "explained": sum(r["explained"] for r in hits),
        "images_of_4850": [r["id"] for r in hits if r["image_of_4850"]],
        "unexplained": [r["id"] for r in unexplained],
        "expected_by_chance": summary and summary["expected_by_chance_new"],
        "coincidence": "supported" if summary and len(unexplained) <= 1 else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
