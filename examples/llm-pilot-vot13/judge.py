"""
Judge the VO + T13 pilot, independently of the agent's own report.

    uv run python examples/llm-pilot-vot13/judge.py <round> [<branch>]

The agent pushes to a branch grown from the sandbox's base commit (base.txt), by default
`pilot-vot13-submission`. The agent chooses the law itself (`vot13TwoExp`), so besides the proof
the judge checks the law:

1. **Library unchanged.** Against the base commit, the branch changes only Pilot.lean, files
   under proofs/LatticeProofs/Pilot/, the deliverables (proposal.md, proposal.py, report.md) and
   files under scratch/. Every file in manifest.json still has its sha256 there.
2. **The proof builds against the real library**, and the repository's own PilotCheck.lean
   elaborates the pinned statement with the agent's `vot13TwoExp`. Its `#print axioms` must show
   only propext, Classical.choice and Quot.sound. The axioms of every other theorem in the
   agent's files are listed too, for partial results.
3. **The law is a formula.** `#eval` must compute `vot13TwoExp` at every (v, m) of the data and
   of the registered sizes, and at very large arguments, within the time limit.
4. **The law against the engine**, for the record: the period it implies,
   2^vot13TwoExp(v, m) L(m) with L(m) the odd part from eigenvalues, against the data it was given
   and against the registered study's observed periods at sizes it never saw.

It also runs the agent's proposal.py, for the record, and writes judgements/round-<n>.json. The
agent is told only about checks 1 to 3, never the held-out comparison.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROOFS = REPO / "proofs"
CLONE = Path("/home/user/pilot-sandbox-vot13")
BRANCH = "pilot-vot13-submission"
WORK = Path("/tmp/claude-0/pilot-judge-vot13")
PYTHON = REPO / ".venv" / "bin" / "python"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
THEOREM = "atlasTriPeriod_triVOT13_law"
ALLOWED = ("proofs/LatticeProofs/Pilot.lean", "proposal.md", "proposal.py", "report.md")
ALLOWED_DIRS = ("proofs/LatticeProofs/Pilot/", "scratch/")
LARGE = [(1000, 1000001), (100000, 999999999), (1, 10**18 + 9)]
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=CLONE, check=True, capture_output=True, text=True
    ).stdout


def fetch(branch: str) -> str:
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.strip()
    git("fetch", "-q", url, f"refs/heads/{branch}")
    return git("rev-parse", "FETCH_HEAD").strip()


def library_check(base: str, head: str) -> dict:
    changes = [line.split("\t") for line in git("diff", "--name-status", base, head).splitlines()]
    touched = [(status, path) for status, *paths in changes for path in paths]
    bad = [
        (status, path)
        for status, path in touched
        if not (path in ALLOWED or path.startswith(ALLOWED_DIRS)) or status.startswith("D")
    ]
    manifest = json.loads(git("show", f"{base}:manifest.json"))
    changed = []
    for rel, digest in manifest.items():
        try:
            blob = subprocess.run(
                ["git", "show", f"{head}:{rel}"], cwd=CLONE, check=True, capture_output=True
            ).stdout
        except subprocess.CalledProcessError:
            changed.append(rel)
            continue
        if hashlib.sha256(blob).hexdigest() != digest:
            changed.append(rel)
    return {
        "ok": not bad and not changed,
        "touched": touched,
        "not_allowed": bad,
        "manifest_changed": changed,
    }


def run(cmd: list[str], cwd: Path, timeout: int) -> dict:
    start = time.time()
    try:
        out = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=timeout)
        code, text = out.returncode, out.stdout + out.stderr
    except subprocess.TimeoutExpired as e:
        code, text = -1, f"timeout after {timeout} s\n{e.stdout or ''}{e.stderr or ''}"
    return {"returncode": code, "seconds": round(time.time() - start, 1), "output": text[-20000:]}


def checkout(head: str) -> Path:
    """The branch's tree at head, in WORK/tree."""
    tree = WORK / "tree"
    tree.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "archive", head], cwd=CLONE, check=True, capture_output=True
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
    return tree


def project(tree: Path) -> Path:
    """A fresh copy of the repository's proofs/, with the agent's Pilot files in it."""
    proj = WORK / "proofs"
    proj.mkdir()
    for item in ["lakefile.toml", "lean-toolchain", "lake-manifest.json", "LatticeProofs.lean"]:
        shutil.copy(PROOFS / item, proj / item)
    shutil.copytree(PROOFS / "LatticeProofs", proj / "LatticeProofs")
    shutil.copy(tree / "proofs" / "LatticeProofs" / "Pilot.lean", proj / "LatticeProofs")
    if (tree / "proofs" / "LatticeProofs" / "Pilot").is_dir():
        shutil.copytree(
            tree / "proofs" / "LatticeProofs" / "Pilot", proj / "LatticeProofs" / "Pilot"
        )
    shutil.copy(HERE / "PilotCheck.lean", proj / "PilotCheck.lean")
    (proj / ".lake").mkdir()
    (proj / ".lake" / "packages").symlink_to(PROOFS / ".lake" / "packages")
    shutil.copytree(PROOFS / ".lake" / "build", proj / ".lake" / "build", symlinks=True)
    return proj


def axioms_of(output: str) -> dict[str, list[str]]:
    found = re.findall(r"'LatticeProofs\.([\w.']+)' depends on axioms: \[([^\]]*)\]", output)
    return {name: sorted(a.strip() for a in axioms.split(",")) for name, axioms in found}


def lean_check(proj: Path) -> dict:
    pilot = proj / "LatticeProofs"
    sources = [(pilot / "Pilot.lean").read_text()]
    sources += [p.read_text() for p in pilot.glob("Pilot/**/*.lean")]
    forbidden = [
        w for w in ["sorry", "axiom ", "native_decide", "admit"] if any(w in s for s in sources)
    ]
    build = run(["lake", "build", "LatticeProofs.Pilot"], proj, 3600)
    check = run(["lake", "env", "lean", "PilotCheck.lean"], proj, 1800)
    axioms = axioms_of(check["output"]).get(THEOREM)
    names = sorted(
        {n for s in sources for n in re.findall(r"^(?:theorem|lemma)\s+([\w.']+)", s, re.M)}
    )
    listing = "import LatticeProofs.Pilot\n" + "".join(
        f"#print axioms LatticeProofs.{n}\n" for n in names
    )
    (proj / "AllAxioms.lean").write_text(listing)
    every = run(["lake", "env", "lean", "AllAxioms.lean"], proj, 1800)
    ok = (
        build["returncode"] == 0
        and check["returncode"] == 0
        and axioms is not None
        and set(axioms) <= STANDARD
        and "error" not in check["output"]
    )
    return {
        "ok": ok,
        "forbidden_words": forbidden,
        "axioms": axioms,
        "every_theorem": axioms_of(every["output"]),
        "build": build,
        "check": check,
    }


def split(n: int) -> tuple[int, int]:
    v = (n & -n).bit_length() - 1
    return v, n >> v


def data_rows() -> list[dict]:
    with open(HERE / "data" / "vot13_periods.csv") as f:
        return [{k: int(x) for k, x in row.items()} for row in csv.DictReader(f)]


def heldout_rows() -> list[dict]:
    path = HERE / "records.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def law_eval(proj: Path, points: list[tuple[int, int]]) -> dict:
    grid = ", ".join(f"({v}, {m})" for v, m in points)
    big = "".join(f"#eval LatticeProofs.vot13TwoExp {v} {m}\n" for v, m in LARGE)
    source = (
        "import LatticeProofs.Pilot\n"
        f"#eval ([{grid}] : List (ℕ × ℕ)).map (fun p => LatticeProofs.vot13TwoExp p.1 p.2)\n" + big
    )
    (proj / "LawEval.lean").write_text(source)
    out = run(["lake", "env", "lean", "LawEval.lean"], proj, 600)
    # Lean wraps a long list across lines.
    lists = re.findall(r"^\[([\d,\s]*)\]", out["output"], re.M)
    values = [int(x) for x in lists[0].split(",")] if lists and lists[0].strip() else None
    ok = (
        out["returncode"] == 0
        and "error" not in out["output"]
        and values is not None
        and len(values) == len(points)
    )
    return {
        "computable": ok,
        "values": dict(zip([f"{v},{m}" for v, m in points], values or [], strict=False)),
        "run": out,
    }


def odd_part(m: int) -> int:
    if m == 1:
        return 1
    sys.path.insert(0, str(HERE.parent / "linear-atlas-3"))
    import atlas3
    import eigen

    return eigen.odd_part(atlas3.polynomial("triangle", ("VO", "T13")), m)


def law_compare(values: dict[str, int]) -> dict:
    def implied(n: int) -> int | None:
        v, m = split(n)
        e = values.get(f"{v},{m}")
        return None if e is None else 2**e * odd_part(m)

    given = [(r["n"], r["period"], implied(r["n"])) for r in data_rows()]
    unseen = [(r["n"], r["period"], implied(r["n"])) for r in heldout_rows()]
    return {
        "data": {
            "agree": sum(p == q for _, p, q in given),
            "of": len(given),
            "disagree": [(n, p, q) for n, p, q in given if p != q],
        },  # fmt: skip
        "heldout": {
            "agree": sum(p == q for _, p, q in unseen),
            "of": len(unseen),
            "disagree": [(n, p, q) for n, p, q in unseen if p != q],
        },  # fmt: skip
    }


def proposal_run(tree: Path) -> dict:
    if not (tree / "proposal.py").exists():
        return {"present": False}
    return {"present": True, **run([str(PYTHON), "proposal.py"], tree, 3600)}


def main() -> None:
    round_no = int(sys.argv[1])
    branch = sys.argv[2] if len(sys.argv) > 2 else BRANCH
    base = (HERE / "base.txt").read_text().strip()
    head = fetch(branch)
    if git("merge-base", base, head).strip() != base:
        raise SystemExit(f"{branch} does not grow from the base commit {base[:12]}")
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    tree = checkout(head)
    proj = project(tree)
    registered = json.loads((HERE / "ledger.jsonl").read_text().splitlines()[0])["body"]["sizes"]
    points = sorted({split(r["n"]) for r in data_rows()} | {split(n) for n in registered})
    lean = lean_check(proj)  # builds Pilot, which the law's #eval needs
    law = law_eval(proj, points)
    result = {
        "round": round_no,
        "branch": branch,
        "base": base,
        "head": head,
        "library": library_check(base, head),
        "lean": lean,
        "law": law,
        "law_vs_engine": law_compare(law["values"]) if law["computable"] else None,
        "proposal": proposal_run(tree),
    }
    result["passed"] = result["library"]["ok"] and result["lean"]["ok"] and law["computable"]
    out = HERE / "judgements" / f"round-{round_no}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        "passed": result["passed"],
        "head": head[:12],
        "library_ok": result["library"]["ok"],
        "lean_ok": result["lean"]["ok"],
        "axioms": result["lean"]["axioms"],
        "law_computable": law["computable"],
        "law_vs_engine": result["law_vs_engine"]
        and {k: f"{v['agree']}/{v['of']}" for k, v in result["law_vs_engine"].items()},
        "proposal_returncode": result["proposal"].get("returncode"),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
