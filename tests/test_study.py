"""The registered-study harness: predictions first, a committed (and pushed) registration before
any run, and a ledger the order check accepts."""

import json
import subprocess
from pathlib import Path

import pytest

from lattice_lab import cli
from lattice_lab.ledger import Ledger, check_order
from lattice_lab.study import Study, StudyError, append_records, load, register, resume, run


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


STUDY_FILE = """
from pathlib import Path

from lattice_lab.study import Study, append_records


def execute(path, workers):
    append_records(path, [{{"x": x, "y": 2 * x}} for x in (3, 4, 5)])


def rerun(record):
    return {{"x": record["x"], "y": {factor} * record["x"]}}


STUDY = Study(
    Path(__file__).resolve().parent,
    lambda: {{"id": "toy", "title": "Is y twice x?"}},
    lambda: [{{"law": "y = 2x"}}],
    execute,
    lambda rows, predictions: {{"rows": len(rows)}},
    {rerun}
)
"""


def _lab(directory: Path, factor: int = 2, rerun: str = "rerun=rerun,") -> Study:
    directory.mkdir()
    _git(directory, "init", "-q")
    (directory / "study.py").write_text(STUDY_FILE.format(factor=factor, rerun=rerun))
    study = load(directory)
    register(study)
    _git(directory, "add", "ledger.jsonl")
    _git(directory, "commit", "-q", "-m", "register")
    run(study)
    return study


def test_verify_reruns_the_records_of_a_study_that_can_rerun_them(tmp_path, capsys):
    study = _lab(tmp_path / "sound")
    assert study.rerun({"x": 7}) == {"x": 7, "y": 14} and load(tmp_path / "sound") is study
    assert cli.main(["verify", "--lab", str(tmp_path / "sound"), "--rerun", "2"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["problems"] == [] and out["reruns"] == {
        "checked": 2,
        "identical": 2,
        "different": [],
    }
    assert not any("not rerun" in w for w in out["warnings"])


def test_verify_fails_when_a_rerun_record_differs(tmp_path, capsys):
    _lab(tmp_path / "moved", factor=3)  # the study's code no longer gives what was recorded
    assert cli.main(["verify", "--lab", str(tmp_path / "moved"), "--rerun", "5"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["reruns"]["checked"] == 3 and out["reruns"]["identical"] == 0
    assert out["problems"] == ["3 rerun record(s) differ from the stored ones"]


def test_a_study_without_rerun_or_one_that_does_not_load_is_only_warned_about(tmp_path, capsys):
    _lab(tmp_path / "plain", rerun="")
    assert cli.main(["verify", "--lab", str(tmp_path / "plain")]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["warnings"] == ["question 0: no loop spec, so its records were not rerun"]

    def copy(name: str, source: str) -> Path:
        lab = tmp_path / name
        lab.mkdir()
        for file in ("ledger.jsonl", "records.jsonl"):
            (lab / file).write_bytes((tmp_path / "plain" / file).read_bytes())
        (lab / "study.py").write_text(source)
        return lab

    # a study.py that names the hook but cannot be imported: said, not fatal
    broken = copy("broken", "import a_module_that_is_not_there\nrerun = None\n")
    assert cli.main(["verify", "--lab", str(broken)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["reruns"]["checked"] == 0
    assert "did not load (ModuleNotFoundError" in out["warnings"][0]
    # one that never mentions the hook is not imported at all
    old = copy("old", "raise SystemExit('a study from before the hook: importing it is avoided')\n")
    assert cli.main(["verify", "--lab", str(old)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["warnings"] == ["question 0: no loop spec, so its records were not rerun"]
    assert load(tmp_path / "no-such-lab") is None
