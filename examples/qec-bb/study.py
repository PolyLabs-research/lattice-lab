"""
A registered rediscovery test: the torus's characters give a bivariate bicycle code's logical
qubits, for published codes and for random ones.

    uv run --no-sync python examples/qec-bb/study.py register
    uv run --no-sync python examples/qec-bb/study.py run
    uv run --no-sync lattice-lab verify --lab examples/qec-bb

The first step of docs/next-direction.md. A bivariate bicycle code is a pair of polynomials A, B
in the group ring of the l x m torus, the ring of this repository's linear rules, and its number
of logical qubits is k = 2 dim(ker A ∩ ker B). bb.py computes k two ways: by ranks over GF(2)
(`k_linalg`), and from the torus's characters (`k_characters`): twice the number of common
zeros of A and B at odd sizes, and at even sizes the sum of their local multiplicities in the
2-part. The second is the repository's eigenvalue machinery applied to codes; this test checks
it before anything is built on it.

1. **Method.** k_characters = k_linalg for the twelve published entries (codes.json) and for
   3,000 random codes: 150 at each of 20 sizes (100 with the trinomial form the published codes
   use, A = x^a + y^b + y^c and B = y^d + x^e + x^f, and 50 with two to six random terms each).
   Development used only sizes with l, m <= 4; none of those is here.
2. **Rediscovery.** k_characters equals the published k for each entry. A mismatch where
   k_linalg agrees with k_characters is reported as a discrepancy in the source or in its
   transcription (codes.json says how the entries were transcribed), not as a failure of the
   method.

Each record also lists the characters that carry k, for the next step.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bb  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

SIZES = [
    (3, 5),
    (3, 7),
    (5, 7),
    (7, 9),
    (15, 3),
    (5, 5),
    (9, 9),
    (11, 3),
    (13, 3),
    (7, 7),
    (6, 6),
    (9, 6),
    (12, 6),
    (12, 12),
    (2, 27),
    (10, 5),
    (8, 8),
    (6, 10),
    (16, 3),
    (4, 12),
]
TRINOMIALS, RANDOM = 100, 50  # fmt: skip


def codes() -> list[dict]:
    out = []
    for c in json.loads((HERE / "codes.json").read_text())["codes"]:
        A = c["A"] if "A" in c else bb.pi_poly(c["pi_A"])
        B = c["B"] if "B" in c else bb.pi_poly(c["pi_B"])
        out.append({**c, "A": A, "B": B})
    return out


def sample(ell: int, m: int) -> list[tuple[str, list, list]]:
    rng = random.Random(f"qec-bb {ell}x{m}")
    out = []
    for _ in range(TRINOMIALS):
        a, e, f = rng.sample(range(ell), 3) if ell >= 3 else [rng.randrange(ell) for _ in range(3)]
        d, b, c = rng.sample(range(m), 3) if m >= 3 else [rng.randrange(m) for _ in range(3)]
        out.append(("trinomial", [(a, 0), (0, b), (0, c)], [(0, d), (e, 0), (f, 0)]))
    for _ in range(RANDOM):
        terms = [[(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.randint(2, 6))]
                 for _ in range(2)]  # fmt: skip
        out.append(("random", terms[0], terms[1]))
    return out


def question() -> dict:
    return {
        "id": "qec-bb-rediscovery",
        "title": "The torus's characters give a bivariate bicycle code's logical qubits",
        "statement": "For a bivariate bicycle code (A, B) on the l x m torus, k computed from "
        "the characters (twice the sum over the odd part's characters of dim L/(A_chi, B_chi), "
        "L the 2-part's local ring) equals k computed from ranks over GF(2), on twelve "
        "published entries and 3,000 random codes at 20 sizes, and equals the published k.",
        "source": "docs/next-direction.md, step 1",
        "sizes": [list(s) for s in SIZES],
        "codes_file": "codes.json",
        "codes_sha256": hashlib.sha256((HERE / "codes.json").read_bytes()).hexdigest(),
        "excluded_seen": ["development used only sizes with l, m <= 4"],
        "checker": "bb.k_linalg (ranks of H_X and H_Z over GF(2))",
        "hypotheses": {"method": "k_characters = k_linalg on every code",
                       "rediscovery": "k_characters = published k on every entry"},
    }  # fmt: skip


def predictions() -> list[dict]:
    return [
        {"test": "method", "predicted": "k_characters = k_linalg on all 12 published entries and "
         "all 3,000 random codes"},
        {"test": "rediscovery", "predicted": "k_characters = the published k on each of the 12 "
         "entries; a mismatch where k_linalg agrees is a source or transcription discrepancy"},
    ]  # fmt: skip


def execute(path: Path, workers: int) -> None:
    if path.exists() and path.read_text().strip():
        return
    rows = []
    for c in codes():
        start = time.time()
        terms = bb.local_terms(c["A"], c["B"], c["l"], c["m"])
        rows.append({"test": "published", "name": c["name"], "l": c["l"], "m": c["m"],
                     "published_k": c["k"], "k_linalg": bb.k_linalg(c["A"], c["B"], c["l"], c["m"]),
                     "k_characters": 2 * sum(t for _, t in terms),
                     "characters": [[list(ch), t] for ch, t in terms],
                     "seconds": round(time.time() - start, 2)})  # fmt: skip
    for ell, m in SIZES:
        start = time.time()
        counts = {"codes": 0, "agree": 0, "k_positive": 0}
        mismatches = []
        for kind, A, B in sample(ell, m):
            a, c = bb.k_linalg(A, B, ell, m), bb.k_characters(A, B, ell, m)
            counts["codes"] += 1
            counts["agree"] += a == c
            counts["k_positive"] += a > 0
            if a != c:
                mismatches.append({"kind": kind, "A": A, "B": B, "k_linalg": a, "k_characters": c})
        rows.append({"test": "random", "ell": ell, "m": m, **counts, "mismatches": mismatches,
                     "seconds": round(time.time() - start, 2)})  # fmt: skip
    append_records(path, rows)


def decide(rows: list[dict], registered: list[dict]) -> dict:
    pub = [r for r in rows if r["test"] == "published"]
    rnd = [r for r in rows if r["test"] == "random"]
    method_bad = [r["name"] for r in pub if r["k_characters"] != r["k_linalg"]]
    method_bad += [f"{r['ell']}x{r['m']}: {len(r['mismatches'])}" for r in rnd if r["mismatches"]]
    reproduced = [r["name"] for r in pub if r["k_characters"] == r["published_k"]]
    discrepancies = [r["name"] for r in pub if r["k_characters"] != r["published_k"]
                     and r["k_linalg"] == r["k_characters"]]  # fmt: skip
    return {
        "missing": [] if len(pub) == 12 and len(rnd) == len(SIZES) else ["records"],
        "method": "holds" if not method_bad else "fails",
        "method_failures": method_bad,
        "random_codes": sum(r["codes"] for r in rnd),
        "random_agree": sum(r["agree"] for r in rnd),
        "rediscovery": f"{len(reproduced)} of {len(pub)}",
        "reproduced": reproduced,
        "source_discrepancies": discrepancies,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
