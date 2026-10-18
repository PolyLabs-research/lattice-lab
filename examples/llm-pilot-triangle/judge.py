"""
Judge the triangle pilot's proofs, independently of the agent's own report.

    uv run python examples/llm-pilot-triangle/judge.py <round>

The agent pushes to `pilot-triangle-submission`, a branch grown from the sandbox's base commit
(base.txt).

1. **Library unchanged.** Against the base commit, the branch changes only Pilot.lean, files
   under proofs/LatticeProofs/Pilot/, the deliverables (proposal.md, proposal.py, report.md) and
   files under scratch/. Every file in manifest.json still has its sha256 there.
2. **The proofs build against the real library.** Pilot.lean and proofs/LatticeProofs/Pilot/ are
   copied into a fresh copy of the repository's proofs/, and `lake build LatticeProofs.Pilot`
   runs.
3. **The statements are the pinned ones, and the axioms are standard.** The repository's own
   PilotCheck.lean, not the branch's, is compiled. It restates both theorems, and both
   `#print axioms` lines must show only propext, Classical.choice and Quot.sound.

It also runs the agent's proposal.py, for the record only, and writes judgements/round-<n>.json.
"""

from __future__ import annotations

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
CLONE = Path("/home/user/pilot-sandbox-triangle")
BRANCH = "pilot-triangle-submission"
WORK = Path("/tmp/claude-0/pilot-judge-triangle")
PYTHON = REPO / ".venv" / "bin" / "python"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
THEOREMS = ["atlasTriPeriod_triE_exact", "atlasTriPeriod_triEVOVS_exact"]
ALLOWED = ("proofs/LatticeProofs/Pilot.lean", "proposal.md", "proposal.py", "report.md")
ALLOWED_DIRS = ("proofs/LatticeProofs/Pilot/", "scratch/")
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=CLONE, check=True, capture_output=True, text=True
    ).stdout


def fetch() -> str:
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=REPO, check=True, capture_output=True, text=True
    ).stdout.strip()
    git("fetch", "-q", url, f"refs/heads/{BRANCH}")
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


def lean_check(tree: Path) -> dict:
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
    pilot = proj / "LatticeProofs"
    sources = [(pilot / "Pilot.lean").read_text()]
    sources += [p.read_text() for p in pilot.glob("Pilot/**/*.lean")]
    forbidden = [
        w for w in ["sorry", "axiom ", "native_decide", "admit"] if any(w in s for s in sources)
    ]
    build = run(["lake", "build", "LatticeProofs.Pilot"], proj, 3600)
    check = run(["lake", "env", "lean", "PilotCheck.lean"], proj, 1800)
    found = dict(
        re.findall(r"'LatticeProofs\.(\w+)' depends on axioms: \[([^\]]*)\]", check["output"])
    )
    axioms = {t: sorted(a.strip() for a in found[t].split(",")) for t in THEOREMS if t in found}
    ok = (
        build["returncode"] == 0
        and check["returncode"] == 0
        and set(axioms) == set(THEOREMS)
        and all(set(a) <= STANDARD for a in axioms.values())
        and "error" not in check["output"]
    )
    return {
        "ok": ok,
        "forbidden_words": forbidden,
        "axioms": axioms,
        "build": build,
        "check": check,
    }


def proposal_run(tree: Path) -> dict:
    if not (tree / "proposal.py").exists():
        return {"present": False}
    return {"present": True, **run([str(PYTHON), "proposal.py"], tree, 3600)}


def main() -> None:
    round_no = int(sys.argv[1])
    base = (HERE / "base.txt").read_text().strip()
    head = fetch()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    tree = checkout(head)
    result = {
        "round": round_no,
        "base": base,
        "head": head,
        "library": library_check(base, head),
        "lean": lean_check(tree),
        "proposal": proposal_run(tree),
    }
    result["passed"] = result["library"]["ok"] and result["lean"]["ok"]
    out = HERE / "judgements" / f"round-{round_no}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        "passed": result["passed"],
        "head": head[:12],
        "library_ok": result["library"]["ok"],
        "lean_ok": result["lean"]["ok"],
        "axioms": result["lean"]["axioms"],
        "forbidden": result["lean"]["forbidden_words"],
        "proposal_returncode": result["proposal"].get("returncode"),
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
