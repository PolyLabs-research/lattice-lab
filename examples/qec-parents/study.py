"""
A registered test: do the census's best codes above 300 qubits share planar parents with the
frontier below 300, more than their neighbours do?

    uv run --no-sync python examples/qec-parents/study.py register
    uv run --no-sync python examples/qec-parents/study.py run --workers 4
    uv run --no-sync lattice-lab verify --lab examples/qec-parents

**The idea.** A bivariate bicycle code on a torus is a pair of planar check shapes wrapped up
(parents.py). On the plane the pair has Q independent excitations (planar.py), and every wrapping
has k <= 2 Q. If good codes come from a few good planar pairs, the frontier above 300 qubits
should reuse the pairs of the frontier below 300, and the census could be extended by choosing
tori for known pairs instead of sweeping every code.

**Populations**, all from the census's own files (parents.cells):
- *early*: every frontier class of every cell of stages 3a, 3b and 3c (n <= 300);
- *late records*: for each n of stage 4 (302 to 400), the cells with the highest k d^2 / n, and
  their frontier classes;
- *control*: for each late record cell, up to CONTROL of its other connected classes (same torus,
  same k, not on the frontier), drawn by `control_sample`.

A class's parents are the keys of its shortest planar forms (parents.shortest_forms). A class
*descends* when one of its parents is a parent of some early class.

**Predictions.**
1. *Method.* For every parent of every late record frontier class, k <= 2 Q <= 2 (mixed area).
   These are theorems; a failure is a fault in the tools. So is a class of the population that
   is not connected or has no form.
2. *Descent.* At least half of the late record cells have a frontier class that descends.
3. *Specific.* Pooled over the late record cells, the fraction of frontier classes that descend
   is at least twice the fraction of control classes that descend (and is not zero).

Reported without a prediction: the same fractions for every late cell, the early cells that
account for the most late record cells, and each shared parent's Q and periods.

**What the registration had seen** is in the question's `excluded_seen`.
"""

from __future__ import annotations

import hashlib
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import parents  # noqa: E402
import planar  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

EARLY, LATE = ("3a", "3b", "3c"), "4"
CONTROL = 200
BATCH = 100


def control_sample(cell_key, others: list) -> list:
    """Up to CONTROL of a cell's non-frontier classes: a sample of the sorted list, seeded by
    the cell."""
    others = sorted(others)
    if len(others) <= CONTROL:
        return others
    stage, ell, m, k = cell_key
    return random.Random(f"qec-parents {ell}x{m} k={k}").sample(others, CONTROL)


def population() -> list[dict]:
    """Every class the test computes on, in order: early, late (every stage-4 cell's frontier,
    the record cells marked), control."""
    cs = parents.cells()
    records = set(parents.record_cells(cs, LATE))
    out = []
    for c in sorted(cs):
        stage, ell, m, k = c
        base = {"stage": stage, "l": ell, "m": m, "n": cs[c]["n"], "k": k, "d": cs[c]["d"]}
        group = "early" if stage in EARLY else "late"
        for A, B in sorted(cs[c]["frontier"]):
            out.append({**base, "group": group, "record": c in records, "A": A, "B": B})
    for c in sorted(records):
        stage, ell, m, k = c
        base = {"stage": stage, "l": ell, "m": m, "n": cs[c]["n"], "k": k, "d": cs[c]["d"]}
        for A, B in control_sample(c, cs[c]["others"]):
            out.append({**base, "group": "control", "record": True, "A": A, "B": B})
    return out


def _census_files() -> dict:
    files = sorted((parents.EX / "qec-census-3" / "data").glob("*.jsonl"))
    files += [
        parents.EX / f / "records.jsonl" for f in ("qec-census-3b", "qec-census-3c", "qec-census-4")
    ]
    h = hashlib.sha256()
    for f in files:
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return {"files": len(files), "sha256_of_sha256s": h.hexdigest()}


def question() -> dict:
    return {
        "id": "qec-planar-parents",
        "title": "Do the census's record codes above 300 qubits share planar parents with the "
        "frontier below 300?",
        "statement": "A class's parents are the keys of its shortest planar forms over every "
        "homomorphism Z^2 -> Z_l x Z_m (parents.py, forms.c). A class descends when it shares a "
        "parent with a frontier class of a cell of stages 3a, 3b or 3c. Tested on the frontier "
        "classes of the stage-4 record cells (the best k d^2 / n at each n) against up to 200 "
        "other connected classes of the same torus and k.",
        "source": "an exploratory session on 2026-11-19: planar parents of the census frontier",
        "census": _census_files(),
        "sha256": {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest()
                   for f in ("forms.c", "parents.py", "planar.py")},
        "control_per_cell": CONTROL,
        "excluded_seen": [
            "exploration, before this test was designed: for one stored frontier class of each "
            "cell of every stage (574 cells, the late ones included), up to 24 shortest forms in "
            "the torus's own l x m coordinates, with their Q and mixed area; the forms of the 14 "
            "highest-scoring cells were read; k against torus size for four planar pairs (the "
            "gross code's and those of [[360,12,24]], [[384,12,24]], [[294,10,20]])",
            "that the gross code's pair and the shortest l x m form of [[360,12,24]] both have "
            "Q = 8 and periods 12 and 12",
            "development: parents.shortest_forms on the frontier classes of stage 3a only "
            "(1,865 classes: ranges 1 to 4, 1,125 distinct parents); four hand-picked codes "
            "through forms.c, among them [[360,12,24]] and two classes of [[372,10,24]]",
            "not seen: any class's parents in the form used here at stages 3b, 3c or 4 (but for "
            "those four codes), any comparison of parents between classes, any control class",
        ],
        "limits": [
            "stages 3b, 3c and 4 ran exact distances only for the classes their bounds could "
            "not rule out, so a cell's frontier classes are those with a completed exact run at "
            "the best d; ties the census did not run are missing",
            "a cell whose best d is not settled is used at its best completed d",
        ],
        "hypotheses": {
            "method": "k <= 2 Q <= 2 (mixed area) for every parent of a late record frontier class",
            "descent": "at least half of the late record cells have a descending frontier class",
            "specific": "the frontier classes of late record cells descend at least twice as "
            "often as the control classes",
        },
    }  # fmt: skip


def predictions() -> list[dict]:
    return [
        {"test": "method", "predicted": "no parent of a late record frontier class has "
         "k > 2 Q or Q > mixed area, and every Q is finite"},
        {"test": "descent", "predicted": "at least 50% of the late record cells have a "
         "frontier class that shares a parent with an early frontier class"},
        {"test": "specific", "predicted": "pooled over the late record cells, the fraction of "
         "frontier classes that descend is greater than 0 and at least 2 times the fraction of "
         "control classes that descend"},
    ]  # fmt: skip


def _forms(batch: list[dict]) -> list[dict]:
    res = parents.shortest_forms([(r["l"], r["m"], r["A"], r["B"]) for r in batch])
    return [{"test": "class", **r, "range": rng, "parents": keys,
             "connected": parents.connected(r["l"], r["m"], r["A"], r["B"])}
            for r, (rng, keys) in zip(batch, res, strict=True)]  # fmt: skip


def _signature(text: str) -> dict:
    ta, tb = parents.key_parse(text)
    return {"test": "parent", "parent": text, **planar.signature(ta, tb)}


def execute(path: Path, workers: int) -> None:
    if path.exists() and path.read_text().strip():
        return
    pop = population()
    batches = [pop[i : i + BATCH] for i in range(0, len(pop), BATCH)]
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        rows = [r for part in pool.map(_forms, batches) for r in part]
        wanted = sorted({p for r in rows if r["group"] == "late" and r["record"]
                         for p in r["parents"]})  # fmt: skip
        rows += list(pool.map(_signature, wanted, chunksize=8))
    append_records(path, rows)


def _cell(r: dict) -> tuple:
    return (r["l"], r["m"], r["k"])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    classes = [r for r in rows if r["test"] == "class"]
    sig = {r["parent"]: r for r in rows if r["test"] == "parent"}
    early: dict = {}  # parent -> the early cells that have it
    for r in classes:
        if r["group"] == "early":
            for p in r["parents"]:
                early.setdefault(p, set()).add((r["n"], *_cell(r), r["d"]))

    def descends(r) -> bool:
        return any(p in early for p in r["parents"])

    late = [r for r in classes if r["group"] == "late"]
    rec = [r for r in late if r["record"]]
    control = [r for r in classes if r["group"] == "control"]
    rec_cells = sorted({_cell(r) for r in rec})
    hit_cells = sorted({_cell(r) for r in rec if descends(r)})
    f_front = sum(descends(r) for r in rec) / len(rec) if rec else 0.0
    f_control = sum(descends(r) for r in control) / len(control) if control else 0.0

    bad = []
    for r in rec:
        for p in r["parents"]:
            s = sig.get(p)
            if s is None or s["Q"] is None or r["k"] > 2 * s["Q"] or s["Q"] > s["mixed_area"]:
                bad.append({"cell": _cell(r), "parent": p})
    unconnected = [[*_cell(r), r["group"]] for r in classes if r["range"] < 0 or not r["connected"]]

    # the early cells that account for the most late record cells, greedily
    reach: dict = {}
    for r in rec:
        for p in r["parents"]:
            for e in early.get(p, ()):
                reach.setdefault(e, set()).add(_cell(r))
    cover, left = [], set(hit_cells)
    while left:
        e = max(sorted(reach), key=lambda e: len(reach[e] & left))
        cover.append({"early_cell": list(e), "late_record_cells": len(reach[e] & left)})
        left -= reach[e]
    shared = sorted({p for r in rec for p in r["parents"] if p in early})

    late_cells = sorted({_cell(r) for r in late})
    late_hit = sorted({_cell(r) for r in late if descends(r)})
    expected = len(population())
    return {
        "missing": [] if len(classes) == expected and len(rec_cells) > 0 else ["records"],
        "unconnected": unconnected,
        "method": "holds" if not bad and not unconnected else "fails",
        "method_failures": bad[:20],
        "late_record_cells": len(rec_cells),
        "late_record_cells_descending": len(hit_cells),
        "descent": "holds" if rec_cells and 2 * len(hit_cells) >= len(rec_cells) else "fails",
        "frontier_classes": len(rec),
        "frontier_fraction": round(f_front, 4),
        "control_classes": len(control),
        "control_fraction": round(f_control, 4),
        "specific": "holds" if f_front > 0 and f_front >= 2 * f_control else "fails",
        "all_late_cells": len(late_cells),
        "all_late_cells_descending": len(late_hit),
        "all_late_fraction": round(sum(descends(r) for r in late) / len(late), 4) if late else 0.0,
        "cover": cover[:10],
        "cover_size": len(cover),
        "not_descending": [list(c) for c in rec_cells if c not in set(hit_cells)],
        "shared_parents": [{"parent": p, "Q": sig[p]["Q"], "period_x": sig[p]["period_x"],
                            "period_y": sig[p]["period_y"],
                            "early_cells": len(early[p])} for p in shared][:60],
        "shared_parent_count": len(shared),
    }  # fmt: skip


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
