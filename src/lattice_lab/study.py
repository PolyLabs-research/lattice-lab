"""Registered studies: a question answered once, with its predictions written down first.

The loop (`loop.ask`) chooses its own held-out sizes as it goes. A study is the other shape of
test: the predictions are worked out beforehand, by whatever means (a law fitted earlier, a
mechanism, an exact formula), written to the ledger, committed and pushed, and only then is the
experiment run and judged. The examples under `examples/` that test period laws were each
written that way by hand; this module is that procedure, once.

A study names four things:

    question()     the question entry's body (provenance is added here)
    predictions()  the bodies of the prediction entries, in order
    execute(path, workers)   run the experiment, appending JSONL records to `path`
    decide(rows, predictions)   the verdict's body, from the records written by this run and
                                the registered prediction bodies

and `register` and `run` do the rest:

    register(study)   ledger: question, then one prediction entry per body. Refuses if the
                      ledger already has entries.
    run(study)        refuses unless the ledger holds exactly that registration, committed, and
                      (when the branch tracks a remote) pushed; then appends run_started (where
                      the records file ends), runs `execute`, appends observations (every record
                      written since, by offset and hash) and the verdict, citing all of them.

`lattice-lab verify --lab DIR` checks a study's ledger like any other: the chain, and that every
prediction precedes the run and every record used follows its start. If the question body holds
the loop's `spec` and `records_file`, verify also reruns sample records byte for byte.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from lattice_lab.ledger import Ledger, canonical, record_lines
from lattice_lab.provenance import provenance


class StudyError(RuntimeError):
    """A study asked to do something out of order."""


@dataclass
class Study:
    directory: Path
    question: Callable[[], dict]
    predictions: Callable[[], list[dict]]
    execute: Callable[[Path, int], None]
    decide: Callable[[list[dict], list[dict]], dict]
    records: str = "records.jsonl"
    ledger: str = "ledger.jsonl"

    @property
    def ledger_path(self) -> Path:
        return Path(self.directory) / self.ledger

    @property
    def records_path(self) -> Path:
        return Path(self.directory) / self.records


def _git(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)


def committed(path: Path) -> bool:
    """True when `path` is tracked by git and has no uncommitted changes."""
    path = Path(path)
    tracked = _git(path.parent, "ls-files", "--error-unmatch", str(path))
    status = _git(path.parent, "status", "--porcelain", "--", str(path))
    return tracked.returncode == 0 and status.returncode == 0 and not status.stdout.strip()


def unpushed(path: Path) -> bool:
    """True when the branch tracks a remote and has commits that are not on it. A branch with no
    upstream cannot be checked, and is not refused for it."""
    ahead = _git(Path(path).parent, "rev-list", "--count", "@{u}..HEAD")
    return ahead.returncode == 0 and ahead.stdout.strip() not in ("", "0")


def register(study: Study) -> list[dict]:
    """Write the question and its predictions. Nothing may have been run yet."""
    ledger = Ledger(study.ledger_path)
    if len(ledger):
        raise StudyError(f"{study.ledger_path} already has entries: already registered")
    question = ledger.append(
        "question", {**study.question(), "records_file": study.records, "provenance": provenance()}
    )
    entries = [question]
    for body in study.predictions():
        entries.append(ledger.append("prediction", {"question": question["hash"], **body}))
    return entries


def run(study: Study, workers: int = 1, require_pushed: bool = True) -> dict:
    """Run the registered experiment and judge it (see the module docstring)."""
    ledger = Ledger(study.ledger_path)
    kinds = [e["kind"] for e in ledger.entries]
    if len(kinds) < 2 or kinds != ["question"] + ["prediction"] * (len(kinds) - 1):
        raise StudyError(
            f"expected exactly a registration (a question, then predictions), found {kinds}"
        )
    if not committed(study.ledger_path):
        raise StudyError("commit the registered predictions before running")
    if require_pushed and unpushed(study.ledger_path):
        raise StudyError("push the registered predictions before running")
    question = ledger.entries[0]
    predictions = ledger.entries[1:]
    path = study.records_path
    started = ledger.append(
        "run_started",
        {
            "question": question["hash"],
            "records_file": study.records,
            "records_offset": path.stat().st_size if path.exists() else 0,
            "provenance": provenance(),
        },
    )
    study.execute(path, workers)
    refs, rows = [], []
    for offset, digest, line in record_lines(path):
        if offset >= started["body"]["records_offset"]:
            refs.append({"offset": offset, "sha256": digest})
            rows.append(json.loads(line))
    observed = ledger.append(
        "observations", {"question": question["hash"], "records": refs, "rows": rows}
    )
    body = study.decide(rows, [p["body"] for p in predictions])
    verdict = ledger.append(
        "verdict",
        {
            "question": question["hash"],
            "cites": {
                "predictions": [p["hash"] for p in predictions],
                "run_started": started["hash"],
                "heldout_observations": observed["hash"],
            },
            **body,
        },
    )
    return verdict["body"]


def append_records(path: Path, records) -> None:
    """Append records (dicts) to a JSONL file, one canonical line each, flushed as they come."""
    with Path(path).open("a") as out:
        for record in records:
            out.write(canonical(record) + "\n")
            out.flush()


def main(study: Study, argv: list[str] | None = None) -> None:
    """`python study.py register|run [--workers N]` for a study script."""
    parser = argparse.ArgumentParser(description=(study.question().get("title") or "a study"))
    parser.add_argument("step", choices=("register", "run"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        if args.step == "register":
            entries = register(study)
            print(json.dumps({"registered": len(entries), "ledger": str(study.ledger_path)}))
        else:
            print(json.dumps(run(study, args.workers), indent=1)[:4000])
    except StudyError as exc:
        sys.exit(f"study: {exc}")
