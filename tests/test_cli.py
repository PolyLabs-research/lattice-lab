"""The `lattice-lab` command end to end, on a question small enough to run in seconds."""

import json
from pathlib import Path

from lattice_lab import cli

ROOT = Path(__file__).resolve().parent.parent
QUESTION = """id = "tiny"
rule = "B2/S34"
shape = "hexagon"
seeds = 3
fit_sizes = [8, 10, 12, 16]
heldout_pool = [20, 24]
heldout_per_round = 2
max_rounds = 1
"""


def _ask(tmp_path, capsys):
    question = tmp_path / "tiny.toml"
    question.write_text(QUESTION)
    lab = tmp_path / "lab"
    assert cli.main(["ask", str(question), "--lab", str(lab)]) == 0
    return lab, json.loads(capsys.readouterr().out)


def test_ask_verify_and_report(tmp_path, capsys):
    lab, summary = _ask(tmp_path, capsys)
    assert summary["verdict"] in ("found", "fragile", "inconclusive", "none fits")
    report = Path(summary["report"])
    assert report.is_file() and report.read_text().startswith("# How does settling time grow")
    assert (lab / "records" / "tiny-0.jsonl").is_file()

    assert cli.main(["verify", "--lab", str(lab), "--rerun", "2"]) == 0
    checked = json.loads(capsys.readouterr().out)
    assert checked["problems"] == [] and checked["reruns"]["identical"] == 2

    report.unlink()
    assert cli.main(["report", "--lab", str(lab), "--question", "tiny"]) == 0
    assert Path(json.loads(capsys.readouterr().out)["report"]).is_file()


def test_verify_fails_on_a_tampered_ledger(tmp_path, capsys):
    lab, _ = _ask(tmp_path, capsys)
    path = lab / "ledger.jsonl"
    lines = path.read_text().splitlines()
    entry = json.loads(lines[-1])
    entry["body"]["verdict"] = "rewritten after the fact"
    lines[-1] = json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")
    assert cli.main(["verify", "--lab", str(lab), "--rerun", "0"]) == 1
    assert json.loads(capsys.readouterr().out)["problems"]


def test_bad_question_exits_2(tmp_path, capsys):
    question = tmp_path / "bad.toml"
    question.write_text(QUESTION.replace("[8, 10, 12, 16]", "[8, 9, 12, 16]"))
    assert cli.main(["ask", str(question), "--lab", str(tmp_path / "lab")]) == 2
    assert "even width" in capsys.readouterr().err


def test_laws_and_a_reduced_selfcheck(tmp_path, capsys):
    assert cli.main(["laws"]) == 0
    assert "power" in capsys.readouterr().out
    out = tmp_path / "selfcheck.md"
    status = cli.main(
        [
            "selfcheck",
            "--thresholds",
            str(ROOT / "thresholds.toml"),
            "--replicates",
            "1",
            "--out",
            str(out),
        ]
    )
    result = json.loads(capsys.readouterr().out)
    assert status == (0 if result["passed"] else 1)
    assert not result["full_run"] and "reduced run" in out.read_text()
    assert {row["law"] for row in result["normal"]} == {
        "constant",
        "logarithmic",
        "linear",
        "power",
        "exponential",
        "exponential_area",
    }
