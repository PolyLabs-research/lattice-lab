"""
A pre-registered test of the XOR rule's period law on n x n tori.

    uv run python examples/xor-periods/study.py preregister   # write the predictions (entries 0-3)
    uv run python examples/xor-periods/study.py run           # run, observe, judge (entries 4-6)
    uv run lattice-lab verify --lab examples/xor-periods      # chain and order check

The law under test was found by Kepler's `find_integer_laws` from LatticeLife runs on n = 3..30
and committed, with its results, in lattice-lab 8d7bc58 (2026-10-16):

    period(n) = 2^v(n) * (2^sord(n) - 1)

for B1357/S1357 (a cell's next state is the parity of its eight neighbours) on an n x n torus, n
not a power of 2; 2^v(n) is the largest power of 2 dividing n and sord(n) the least j with
2^j = +-1 modulo the odd part of n. The rival is that the torus's period equals that of the 1D
rule 90 on an n-cycle (computed here exactly, in GF(2)[x]/(x^n - 1)). They differ where rule 90
falls short of 2^sord - 1: n = 37, 74 and 95 between 36 and 100.

`preregister` writes the predictions into ledger.jsonl before any of these runs exist; the
predictions are then committed and pushed, so their time is on record outside this repository.
`run` refuses to start unless the predictions are committed. Records are deterministic (no
timings), so they can be rerun and compared.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.harness import single_species_session
from latticelife.experiments.periodicity import CycleDetector

from lattice_lab.ledger import Ledger, canonical, record_lines
from lattice_lab.provenance import provenance

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ledger.jsonl"
RECORDS = "records.jsonl"
RULE = "B1357/S1357"
SEEDS = (1, 2, 3)
DENSITY = 0.5
BUDGET = 4e9  # cell-generations per run, law(n) * n^2


def odd_part(n: int) -> int:
    while n % 2 == 0:
        n //= 2
    return n


def suborder(m: int) -> int:
    if m <= 3:
        return 1
    k, v = 1, 2 % m
    while v not in (1, m - 1):
        v, k = v * 2 % m, k + 1
    return k


def law(n: int) -> int:
    return (n // odd_part(n)) * (2 ** suborder(odd_part(n)) - 1)


def _mul(a: int, b: int, n: int) -> int:
    """Product in GF(2)[x]/(x^n - 1), polynomials as integers."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a = (a ^ (1 << n)) | 1
    return r


def _pow(a: int, e: int, n: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = _mul(r, a, n)
        a = _mul(a, a, n)
        e >>= 1
    return r


def rule90_period(n: int) -> int:
    """Rule 90's period on an n-cycle from a single live cell, its longest (Martin, Odlyzko and
    Wolfram 1984): the least d dividing law(n) with T^(t+d) = T^t past the transient."""
    step = (1 << 1) | (1 << (n - 1))  # x + x^-1
    base = _pow(step, n, n)  # past any transient (at most 2^v(n) <= n)
    if base == 0:
        return 1
    bound = law(n)
    divisors = sorted(
        {d for i in range(1, int(bound**0.5) + 1) if bound % i == 0 for d in (i, bound // i)}
    )
    for d in divisors:
        if _pow(step, n + d, n) == base:
            return d
    raise RuntimeError(f"rule 90 period at n={n} does not divide {bound}")


def sizes() -> list[int]:
    """The sizes tested, by a rule fixed before the run: every n from 36 to 100 that is not a
    power of 2 and whose predicted period costs at most BUDGET cell-generations, except 37, which
    was measured on 2026-10-17 before this ledger existed."""
    return [n for n in range(36, 101) if n & (n - 1) and law(n) * n * n <= BUDGET and n != 37]


def committed(path: Path) -> bool:
    out = subprocess.run(
        ["git", "-C", str(HERE), "status", "--porcelain", "--", str(path)],
        capture_output=True,
        text=True,
    )
    tracked = subprocess.run(
        ["git", "-C", str(HERE), "ls-files", "--error-unmatch", str(path)],
        capture_output=True,
        text=True,
    )
    return out.returncode == 0 and not out.stdout.strip() and tracked.returncode == 0


def preregister() -> None:
    ledger = Ledger(LEDGER)
    if len(ledger):
        sys.exit("already registered: the ledger has entries")
    tested = sizes()
    question = ledger.append(
        "question",
        {
            "id": "xor-periods",
            "title": f"Periods of {RULE} on n x n square tori, n = 36..100",
            "rule": RULE,
            "shape": "square",
            "design": {
                "sizes": tested,
                "seeds": list(SEEDS),
                "density": DENSITY,
                "starts": {
                    "soup": "random soup at the density, one per seed",
                    "columns": "seed 1: a random column vector repeated along y (constant in "
                    "y), which evolves exactly as rule 90 on the n-cycle",
                },
                "cap": "2 * law(n) + n + 10 generations, so a period up to twice the law is seen",
                "selection": sizes.__doc__.strip(),
            },
            "law": {
                "expression": "2^v(n)*(2^sord(n) - 1)",
                "found_by": "kepler.find_integer_laws on LatticeLife runs, n = 3..30",
                "committed_in": "lattice-lab 8d7bc58, 2026-10-16T21:50:20Z, "
                "examples/capabilities/results.json and docs/capabilities.md",
            },
            "background": {
                "n37": "Measured on 2026-10-17 after the law was committed, but not entered in "
                "a ledger beforehand: three soups gave period 262143 (the law); a "
                "column-constant start gave 87381 (rule 90's published value). It is not "
                "part of this test.",
                "prior_work": "McLaughlin (West Chester) lists the periods of this rule on odd "
                "tori up to 23, as a conjecture; Martin, Odlyzko and Wolfram (1984) proved "
                "the analogous structure for 1D rule 90, which first falls short of "
                "2^sord - 1 at n = 37.",
            },
            "provenance": provenance(),
        },
    )
    q = question["hash"]
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "2^v(n)*(2^sord(n) - 1)",
            "predictions": {str(n): law(n) for n in tested},
            "transient": {"odd n": "at most 1 for every start", "even n": "no prediction"},
            "decision": "confirmed at n when the longest period over the three soups equals the "
            "prediction; refuted at n when any soup's period does not divide it (a "
            "period above it, or an unsettled run, does not divide it); short at n when "
            "every period divides it but none equals it",
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "rival: the period of rule 90 on an n-cycle",
            "predictions": {str(n): rule90_period(n) for n in tested},
            "decision": "refuted at n when any soup's period is not a divisor of the prediction",
            "differs_from_law_at": [n for n in tested if rule90_period(n) != law(n)],
        },
    )
    ledger.append(
        "prediction",
        {
            "question": q,
            "law": "control: a column-constant start evolves as rule 90",
            "predictions": {str(n): rule90_period(n) for n in tested},
            "decision": "passes at n when the column start's period divides the prediction "
            "(equality expected for a generic column)",
        },
    )
    print(
        json.dumps(
            {
                "registered": len(ledger),
                "sizes": tested,
                "law": {n: law(n) for n in tested},
                "rival_differs_at": [n for n in tested if rule90_period(n) != law(n)],
            }
        )
    )


def measure(job: tuple[int, str, int]) -> tuple[dict, float]:
    n, start, seed = job
    config = load_config(DEFAULT_CONFIG_PATH)
    session = single_species_session(config, Rule.from_bs_string(RULE), "square", n, DENSITY, seed)
    if start == "columns":
        column = np.random.default_rng(seed).integers(0, 2, n).astype(session.grid.occupancy.dtype)
        session.grid.occupancy[:] = np.tile(column, n)  # cell (x, y) at y*n + x: constant in y
    cap = 2 * law(n) + n + 10
    detector = CycleDetector()
    detector.observe(session.grid.occupancy, 0)
    began = time.time()
    found = None
    for step in range(1, cap):
        session.step()
        found = detector.observe(session.grid.occupancy, step)
        if found is not None:
            break
    record = {
        "rule": RULE,
        "shape": "square",
        "grid": n,
        "density": DENSITY,
        "seed": seed,
        "start": start,
        "cap": cap,
        "period": found[0] if found else None,
        "transient": found[1] if found else None,
    }
    return record, time.time() - began


def run(workers: int) -> None:
    ledger = Ledger(LEDGER)
    kinds = [e["kind"] for e in ledger.entries]
    if kinds != ["question", "prediction", "prediction", "prediction"]:
        sys.exit(f"expected exactly the registration (entries 0-3), found {kinds}")
    if not committed(LEDGER):
        sys.exit("commit (and push) the registered predictions before running")
    question = ledger.entries[0]
    tested = question["body"]["design"]["sizes"]
    records_path = HERE / RECORDS
    started = ledger.append(
        "run_started",
        {
            "question": question["hash"],
            "records_file": RECORDS,
            "records_offset": records_path.stat().st_size if records_path.exists() else 0,
            "sizes": tested,
            "provenance": provenance(),
        },
    )
    jobs = [(n, "soup", s) for n in tested for s in SEEDS] + [(n, "columns", 1) for n in tested]
    jobs.sort(key=lambda j: -law(j[0]) * j[0] ** 2)  # longest first
    with ProcessPoolExecutor(workers) as pool, records_path.open("a") as out:
        futures = [pool.submit(measure, job) for job in jobs]
        for future in as_completed(futures):
            record, seconds = future.result()
            out.write(canonical(record) + "\n")
            out.flush()
            print(
                f"n={record['grid']} {record['start']} seed {record['seed']}: period "
                f"{record['period']} transient {record['transient']} ({seconds:.0f}s)",
                flush=True,
            )

    refs, rows = [], []
    for offset, digest, line in record_lines(records_path):
        if offset >= started["body"]["records_offset"]:
            refs.append({"offset": offset, "sha256": digest})
            rows.append(json.loads(line))
    observed = ledger.append(
        "observations", {"question": question["hash"], "records": refs, "rows": rows}
    )
    law_p, rival_p, control_p = (e["body"]["predictions"] for e in ledger.entries[1:4])
    outcomes = {}
    for n in tested:
        key = str(n)
        soups = [r["period"] for r in rows if r["grid"] == n and r["start"] == "soup"]
        column = next(r["period"] for r in rows if r["grid"] == n and r["start"] == "columns")
        transients = [r["transient"] for r in rows if r["grid"] == n]
        divides = all(p is not None and law_p[key] % p == 0 for p in soups)
        outcomes[key] = {
            "predicted": law_p[key],
            "rival": rival_p[key],
            "soups": soups,
            "column": column,
            "law": (
                "refuted" if not divides else "confirmed" if max(soups) == law_p[key] else "short"
            ),
            "rival_refuted": any(p is None or rival_p[key] % p for p in soups),
            "control": "passes" if column is not None and control_p[key] % column == 0 else "fails",
            "control_equal": column == control_p[key],
            "transient_odd_ok": None
            if n % 2 == 0
            else all(t is not None and t <= 1 for t in transients),
        }
    tally = {
        k: sum(o["law"] == k for o in outcomes.values()) for k in ("confirmed", "short", "refuted")
    }
    ledger.append(
        "verdict",
        {
            "question": question["hash"],
            "cites": {
                "predictions": [e["hash"] for e in ledger.entries[1:4]],
                "run_started": started["hash"],
                "heldout_observations": observed["hash"],
            },
            "outcomes": outcomes,
            "law": tally,
            "rival_refuted_at": [int(k) for k, o in outcomes.items() if o["rival_refuted"]],
            "controls_pass": all(o["control"] == "passes" for o in outcomes.values()),
            "odd_transients_ok": all(
                o["transient_odd_ok"] in (None, True) for o in outcomes.values()
            ),
        },
    )
    print(
        json.dumps(
            {"law": tally, "rival_refuted_at": ledger.entries[-1]["body"]["rival_refuted_at"]}
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="pre-registered test of the XOR period law")
    parser.add_argument("step", choices=("preregister", "run"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    preregister() if args.step == "preregister" else run(args.workers)


if __name__ == "__main__":
    main()
