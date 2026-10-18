"""The registered-study harness: predictions first, a committed (and pushed) registration before
any run, and a ledger the order check accepts."""

import json
import subprocess
from pathlib import Path

import pytest

from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, StudyError, append_records, register, resume, run


def _git(path: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
    )


def _study(directory: Path) -> Study:
    def execute(path: Path, workers: int) -> None:
        append_records(path, [{"x": x, "y": 2 * x} for x in (3, 4)])

    def decide(rows, predictions):
        predicted = predictions[0]["predictions"]
        return {
            "outcomes": {
                str(r["x"]): "confirmed" if predicted[str(r["x"])] == r["y"] else "refuted"
                for r in rows
            }
        }

    return Study(
        directory=directory,
        question=lambda: {"id": "toy", "title": "Is y twice x?"},
        predictions=lambda: [{"law": "y = 2x", "predictions": {"3": 6, "4": 9}}],
        execute=execute,
        decide=decide,
    )


def test_a_study_runs_only_after_its_registration_is_committed(tmp_path):
    _git(tmp_path, "init", "-q")
    study = _study(tmp_path)
    register(study)
    with pytest.raises(StudyError, match="already"):
        register(study)
    with pytest.raises(StudyError, match="commit"):
        run(study)
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    verdict = run(study)
    assert verdict["outcomes"] == {"3": "confirmed", "4": "refuted"}
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert [e["kind"] for e in ledger.entries] == [
        "question",
        "prediction",
        "run_started",
        "observations",
        "verdict",
    ]
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    assert ledger.entries[0]["body"]["records_file"] == "records.jsonl"
    with pytest.raises(StudyError, match="registration"):
        run(study)


def test_the_order_check_catches_a_changed_record(tmp_path):
    _git(tmp_path, "init", "-q")
    study = _study(tmp_path)
    register(study)
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    run(study)
    records = tmp_path / "records.jsonl"
    lines = records.read_text().splitlines()
    lines[0] = json.dumps({"x": 3, "y": 7})
    records.write_text("\n".join(lines) + "\n")
    assert check_order(Ledger(tmp_path / "ledger.jsonl"), tmp_path)


def test_an_interrupted_run_resumes_without_repeating_work(tmp_path):
    _git(tmp_path, "init", "-q")
    calls = []

    def execute(path: Path, workers: int) -> None:
        done = (
            {json.loads(line)["x"] for line in path.read_text().splitlines()}
            if path.exists()
            else set()
        )
        for x in (3, 4):
            if x in done:
                continue
            calls.append(x)
            append_records(path, [{"x": x, "y": 2 * x}])
            if len(calls) == 1:
                raise KeyboardInterrupt  # the process is stopped after one record

    study = _study(tmp_path)
    study.execute = execute
    register(study)
    _git(tmp_path, "add", "ledger.jsonl")
    _git(tmp_path, "commit", "-q", "-m", "register")
    with pytest.raises(KeyboardInterrupt):
        run(study)
    with pytest.raises(StudyError, match="registration"):
        run(study)
    verdict = resume(study)
    assert calls == [3, 4]
    assert verdict["outcomes"] == {"3": "confirmed", "4": "refuted"}
    ledger = Ledger(tmp_path / "ledger.jsonl")
    assert [e["kind"] for e in ledger.entries] == [
        "question",
        "prediction",
        "run_started",
        "run_resumed",
        "observations",
        "verdict",
    ]
    assert ledger.verify() == [] and check_order(ledger, tmp_path) == []
    with pytest.raises(StudyError, match="no observations"):
        resume(study)
