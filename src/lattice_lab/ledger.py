"""The ledger: an append-only, hash-chained record of everything the loop does.

One JSON object per line (`ledger.jsonl` in the lab directory), never rewritten. Each entry is

    {"seq": 7, "kind": "prediction", "time": "...", "prev": "<hash of entry 6>",
     "body": {...}, "hash": "<sha256 of the canonical JSON of seq, kind, time, prev, body>"}

so editing any entry, removing one or reordering them breaks every hash after it: `verify`
finds it. A prediction cannot be quietly edited after the run that tested it.

Kinds, in the order a question writes them:

    question       the question as asked, the code that answered it (provenance), the files
    run_started    a batch of experiments is about to run; where the records file ended then
    run_resumed    an interrupted batch continues: where the records file ends now, and who
    observations   what a batch measured: rows, and the offset and hash of every record used
    plan           a round's fits, ranking and the held-out sizes chosen, with why
    prediction     one law's predictions at the held-out sizes, written before they are run
    verdict        the judgement of a round, citing the predictions, run and observations

`check_order` is the order check: every verdict's predictions come before the run that tested
them, and every record of that run lies past the end the records file had when it started.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

GENESIS = "0" * 64
KINDS = ("question", "run_started", "run_resumed", "observations", "plan", "prediction", "verdict")


class LedgerError(Exception):
    """A ledger file that cannot be read as a ledger."""


def clean(obj: Any) -> Any:
    """`obj` as plain JSON: numpy scalars and arrays unwrapped, tuples as lists, non-finite
    floats as None (the ledger never holds NaN or Infinity)."""
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [clean(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return clean(obj.tolist())
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, float | np.floating):
        value = float(obj)
        return value if math.isfinite(value) else None
    if obj is None or isinstance(obj, str | int | bool):
        return obj
    return str(obj)


def canonical(obj: Any) -> str:
    return json.dumps(clean(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str | bytes) -> str:
    data = text.encode() if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def entry_hash(entry: dict) -> str:
    return sha256_text(canonical({k: entry[k] for k in ("seq", "kind", "time", "prev", "body")}))


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Ledger:
    """The ledger at `path` (None: in memory only, for the self-check and tests)."""

    def __init__(self, path: str | Path | None, clock: Callable[[], str] | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._clock = clock or _now
        self._entries: list[dict] = []
        self._by_hash: dict[str, dict] = {}
        self.truncated = False
        if self.path is not None and self.path.is_file():
            self._load()

    def _load(self) -> None:
        lines = self.path.read_bytes().split(b"\n")
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                if number == len(lines):  # an interrupted last write: the file's tail only
                    self.truncated = True
                    continue
                raise LedgerError(f"{self.path}:{number}: not JSON") from None
            if not isinstance(entry, dict) or not {"seq", "kind", "hash", "body"} <= set(entry):
                raise LedgerError(f"{self.path}:{number}: not a ledger entry")
            self._entries.append(entry)
            self._by_hash[entry["hash"]] = entry

    @property
    def entries(self) -> list[dict]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def get(self, digest: str) -> dict:
        try:
            return self._by_hash[digest]
        except KeyError:
            raise LedgerError(f"no entry with hash {digest}") from None

    def append(self, kind: str, body: dict) -> dict:
        if kind not in KINDS:
            raise ValueError(f"unknown ledger kind {kind!r}")
        if self.truncated:
            raise LedgerError(f"{self.path} ends in a partial line; repair it before appending")
        entry = {
            "seq": len(self._entries),
            "kind": kind,
            "time": self._clock(),
            "prev": self._entries[-1]["hash"] if self._entries else GENESIS,
            "body": clean(body),
        }
        entry["hash"] = entry_hash(entry)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a") as f:
                f.write(canonical(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        self._entries.append(entry)
        self._by_hash[entry["hash"]] = entry
        return entry

    def questions(self) -> list[dict]:
        return [e for e in self._entries if e["kind"] == "question"]

    def for_question(self, question_hash: str) -> list[dict]:
        """The question's own entry and every entry that names it."""
        return [
            e
            for e in self._entries
            if e["hash"] == question_hash or e["body"].get("question") == question_hash
        ]

    def verify(self) -> list[str]:
        """Problems with the chain itself: numbering, links and hashes. Empty when sound."""
        problems = []
        prev = GENESIS
        for index, entry in enumerate(self._entries):
            if entry.get("seq") != index:
                problems.append(f"entry {index}: numbered {entry.get('seq')}")
            if entry.get("prev") != prev:
                problems.append(f"entry {index}: does not link to the entry before it")
            if entry_hash(entry) != entry.get("hash"):
                problems.append(f"entry {index}: its content does not match its hash")
            prev = entry.get("hash")
        if self.truncated:
            problems.append("the file ends in a partial line (an interrupted write)")
        return problems


def record_lines(path: str | Path) -> list[tuple[int, str, bytes]]:
    """(byte offset, sha256, line bytes) of every complete line of a JSONL records file."""
    path = Path(path)
    if not path.is_file():
        return []
    data = path.read_bytes()
    out = []
    offset = 0
    for line in data.split(b"\n")[:-1]:  # the last piece follows the final newline
        if line.strip():
            out.append((offset, sha256_text(line), line))
        offset += len(line) + 1
    return out


def check_order(ledger: Ledger, lab_dir: str | Path) -> list[str]:
    """The order check: every verdict cites predictions written before the run that tested
    them, that run started before its observations and the verdict, and every record those
    observations used lies past the end the records file had when the run started, with the
    content its hash says. Empty when every verdict passes."""
    lab_dir = Path(lab_dir)
    problems = []
    for verdict in (e for e in ledger.entries if e["kind"] == "verdict"):
        cites = verdict["body"].get("cites") or {}
        if not cites.get("run_started"):
            continue  # nothing was tested: no held-out run to order
        where = f"verdict {verdict['seq']}"
        try:
            run = ledger.get(cites["run_started"])
            observed = ledger.get(cites["heldout_observations"])
            predictions = [ledger.get(h) for h in cites.get("predictions", [])]
        except (KeyError, LedgerError) as exc:
            problems.append(f"{where}: cites a missing entry ({exc})")
            continue
        if run["kind"] != "run_started" or observed["kind"] != "observations":
            problems.append(f"{where}: cites entries of the wrong kind")
            continue
        if not predictions:
            problems.append(f"{where}: tested held-out sizes without any prediction")
        for prediction in predictions:
            if prediction["kind"] != "prediction":
                problems.append(f"{where}: cites entry {prediction['seq']} as a prediction")
            elif prediction["seq"] >= run["seq"]:
                problems.append(
                    f"{where}: prediction {prediction['seq']} ({prediction['body'].get('law')}) "
                    f"was written after the run it was tested by started (entry {run['seq']})"
                )
        if not run["seq"] < observed["seq"] < verdict["seq"]:
            problems.append(f"{where}: run, observations and verdict are out of order")
        if not run["body"].get("records_file"):
            continue  # an in-memory run (the self-check) leaves no records file to check
        records_file = lab_dir / run["body"]["records_file"]
        start = int(run["body"]["records_offset"])
        lines = {offset: digest for offset, digest, _ in record_lines(records_file)}
        for ref in observed["body"].get("records", []):
            if ref["offset"] < start:
                problems.append(
                    f"{where}: a held-out record (offset {ref['offset']}) predates the run's "
                    f"start (offset {start})"
                )
            elif lines.get(ref["offset"]) != ref["sha256"]:
                problems.append(
                    f"{where}: the record at offset {ref['offset']} of {records_file.name} is "
                    "missing or changed"
                )
    return problems
