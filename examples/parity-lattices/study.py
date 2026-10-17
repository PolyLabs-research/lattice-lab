"""
A pre-registered test of the parity rules' period law on hexagonal and triangular tori.

    uv run python examples/parity-lattices/study.py preregister
    uv run python examples/parity-lattices/study.py run
    uv run lattice-lab verify --lab examples/parity-lattices

The law was found by Kepler from simulations on n = 6..60 (discover.py, laws.json):
P(n) = 2 * 2^v(n) * (2^sord(n) - 1), with the small families seen there (lattices.law). It is
tested at every even n from 62 to 200 on all three lattices, by the exact computation in
lattices.py, which first reproduced all 84 simulated periods and transients. The predictions are
written here and pushed before that computation runs on any of these sizes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lattices  # noqa: E402

from lattice_lab.ledger import Ledger, canonical, record_lines  # noqa: E402
from lattice_lab.provenance import provenance  # noqa: E402

LEDGER = HERE / "ledger.jsonl"
RECORDS = "records.jsonl"
LATTICES = ("hexagon", "triangle-edge", "triangle-edge+vertex")
SIZES = list(range(62, 201, 2))


def hexagon_transient(n: int) -> int:
    two_v = n // lattices.odd_part(n)
    return n // 2 if lattices.odd_part(n) == 1 else 2 * two_v


def committed(path: Path) -> bool:
    status = subprocess.run(
        ["git", "-C", str(HERE), "status", "--porcelain", "--", str(path)],
        capture_output=True,
        text=True,
    )
    tracked = subprocess.run(
        ["git", "-C", str(HERE), "ls-files", "--error-unmatch", str(path)],
        capture_output=True,
        text=True,
    )
    return status.returncode == 0 and not status.stdout.strip() and tracked.returncode == 0


def preregister() -> None:
    ledger = Ledger(LEDGER)
    if len(ledger):
        sys.exit("already registered: the ledger has entries")
    question = ledger.append(
        "question",
        {
            "id": "parity-lattices",
            "title": "Periods of the parity rules on hexagonal and triangular n x n tori, "
            "n = 62..200",
            "rules": {
                "hexagon": "B135/S135",
                "triangle-edge": "B13/S13",
                "triangle-edge+vertex": "B1,3,5,7,9,11/S1,3,5,7,9,11",
            },
            "sizes": SIZES,
            "discovery": "discover.py: simulations on n = 6..60 and Kepler's find_integer_laws "
            "(laws.json), "
            "committed before this registration",
            "method": "lattices.period: the rule as a matrix over F2[Z^2 / Lambda], exact powers "
            "by FFT "
            "convolution, the period as an order; it reproduced all 84 simulated (period, "
            "transient) pairs and LatticeLife's one-step adjacency cell for cell",
            "provenance": provenance(),
        },
    )
    q = question["hash"]
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "2 * 2^v(n) * (2^sord(n) - 1); odd part 1: hexagon and edge+vertex die, "
            "edge has "
            "period n; hexagon with odd part 3: 2^v(n)",
            "predictions": {lat: {str(n): lattices.law(lat, n) for n in SIZES} for lat in LATTICES},
            "decision": "confirmed at (lattice, n) when the exact longest period equals the "
            "prediction",
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "hexagon transient: 2 * 2^v(n), or n/2 when n is a power of 2",
            "predictions": {"hexagon": {str(n): hexagon_transient(n) for n in SIZES}},
            "decision": "confirmed at n when the exact transient equals the prediction",
        },
    )
    print(json.dumps({"registered": len(ledger), "sizes": len(SIZES), "lattices": LATTICES}))


def _job(args):
    lattice, n = args
    began = time.time()
    try:
        result = lattices.period(lattice, n)
    except Exception as exc:  # reported, never hidden
        result = {"error": repr(exc)}
    return {"lattice": lattice, "n": n, **result}, time.time() - began


def run(workers: int) -> None:
    ledger = Ledger(LEDGER)
    kinds = [e["kind"] for e in ledger.entries]
    if kinds != ["question", "prediction", "prediction"]:
        sys.exit(f"expected exactly the registration (entries 0-2), found {kinds}")
    if not committed(LEDGER):
        sys.exit("commit (and push) the registered predictions before running")
    question = ledger.entries[0]
    path = HERE / RECORDS
    started = ledger.append(
        "run_started",
        {
            "question": question["hash"],
            "records_file": RECORDS,
            "records_offset": path.stat().st_size if path.exists() else 0,
            "provenance": provenance(),
        },
    )
    jobs = sorted(((lat, n) for lat in LATTICES for n in SIZES), key=lambda j: -j[1])
    with Pool(workers) as pool, path.open("a") as out:
        for record, seconds in pool.imap_unordered(_job, jobs):
            out.write(canonical(record) + "\n")
            out.flush()
            print(
                f"{record['lattice']} n={record['n']}: {record.get('period')} "
                f"(transient {record.get('transient')}, {seconds:.0f}s)",
                flush=True,
            )
    refs, rows = [], []
    for offset, digest, line in record_lines(path):
        if offset >= started["body"]["records_offset"]:
            refs.append({"offset": offset, "sha256": digest})
            rows.append(json.loads(line))
    observed = ledger.append(
        "observations", {"question": question["hash"], "records": refs, "rows": rows}
    )
    periods = ledger.entries[1]["body"]["predictions"]
    transients = ledger.entries[2]["body"]["predictions"]["hexagon"]
    outcomes, refuted, errors = {}, [], []
    for row in rows:
        key = f"{row['lattice']} {row['n']}"
        if "error" in row:
            errors.append(key)
            continue
        ok = row["period"] == periods[row["lattice"]][str(row["n"])]
        outcome = {
            "period": row["period"],
            "predicted": periods[row["lattice"]][str(row["n"])],
            "transient": row["transient"],
            "law": "confirmed" if ok else "refuted",
        }
        if row["lattice"] == "hexagon":
            outcome["transient_law"] = (
                "confirmed" if row["transient"] == transients[str(row["n"])] else "refuted"
            )
        outcomes[key] = outcome
        if not ok:
            refuted.append(key)
    ledger.append(
        "verdict",
        {
            "question": question["hash"],
            "cites": {
                "predictions": [e["hash"] for e in ledger.entries[1:3]],
                "run_started": started["hash"],
                "heldout_observations": observed["hash"],
            },
            "outcomes": outcomes,
            "law": {
                "confirmed": len(outcomes) - len(refuted),
                "refuted": len(refuted),
                "refuted_at": refuted,
                "errors": errors,
            },
            "hexagon_transient_refuted_at": [
                k for k, o in outcomes.items() if o.get("transient_law") == "refuted"
            ],
        },
    )
    print(json.dumps(ledger.entries[-1]["body"]["law"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="pre-registered test of the parity-lattice law")
    parser.add_argument("step", choices=("preregister", "run"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    preregister() if args.step == "preregister" else run(args.workers)


if __name__ == "__main__":
    main()
