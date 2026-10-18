"""
Build the VO + T13 pilot's sandbox and push it as an orphan branch of this repository.

    uv run python examples/llm-pilot-vot13/sandbox.py [--force] [--push]

The agent works in its own cloud session, whose container clones only this branch
(`pilot-sandbox-vot13`, depth 1). It holds no docs/ or examples/, so none of the write-ups or
hand proofs, and no history: the branch has a single commit with no parent. The tree:

- CARD.md, the problem card, tools/, the numeric tools, and data/vot13_periods.csv, VO + T13's
  exact periods at every even n from 4 to 64 (make_data.py);
- setup.sh, which makes the Python environment, installs the Lean toolchain and builds mathlib in
  the fresh container, and python, which runs the environment's interpreter by its real path;
- proofs/, the Lean project's sources (everything in proofs/LatticeProofs, including the first
  two pilots' HexTwoPart.lean and TriTwoPart.lean, now part of the library), with Pilot.lean (the
  law to define and the theorem, with `sorry`) and PilotCheck.lean (the pinned statement). It
  does not include generate.py, which needs the atlas code;
- manifest.json, the sha256 of every file the agent may not change, for the judge.

The base commit is written to base.txt here, and pushed both as the sandbox branch and as the
agent's branch, `pilot-vot13-submission`. The judge diffs the agent's branch against it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROOFS = REPO / "proofs"
SANDBOX = Path("/home/user/pilot-sandbox-vot13")
BRANCH = "pilot-sandbox-vot13"
SUBMISSION = "pilot-vot13-submission"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_files(root: Path) -> list[Path]:
    """The Lean sources and project files the sandbox carries over, relative to root."""
    files = [root / "lakefile.toml", root / "lean-toolchain", root / "lake-manifest.json"]
    files += [root / "LatticeProofs.lean", root / "Axioms.lean", root / "check.sh"]
    files += sorted((root / "LatticeProofs").glob("*.lean"))
    # VOT13Law.lean is this pilot's own answer, added to the library afterwards.
    return [f.relative_to(root) for f in files if f.name not in ("Pilot.lean", "VOT13Law.lean")]


def build(force: bool) -> dict:
    if SANDBOX.exists():
        if not force:
            raise SystemExit(f"{SANDBOX} exists; pass --force to rebuild it")
        shutil.rmtree(SANDBOX)
    (SANDBOX / "proofs" / "LatticeProofs").mkdir(parents=True)
    shutil.copy(HERE / "card.md", SANDBOX / "CARD.md")
    shutil.copytree(HERE / "tools", SANDBOX / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(HERE / "data", SANDBOX / "data")
    for name in ["setup.sh", "python"]:
        shutil.copy(HERE / "sandbox" / name, SANDBOX / name)
    shutil.copy(HERE / "sandbox" / "gitignore", SANDBOX / ".gitignore")
    for rel in library_files(PROOFS):
        target = SANDBOX / "proofs" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(PROOFS / rel, target)
    shutil.copy(HERE / "Pilot.lean", SANDBOX / "proofs" / "LatticeProofs" / "Pilot.lean")
    shutil.copy(HERE / "PilotCheck.lean", SANDBOX / "proofs" / "PilotCheck.lean")
    protected = sorted(
        str(p.relative_to(SANDBOX))
        for p in SANDBOX.rglob("*")
        if p.is_file() and p.relative_to(SANDBOX).as_posix() != "proofs/LatticeProofs/Pilot.lean"
    )
    manifest = {rel: sha256(SANDBOX / rel) for rel in protected}
    (SANDBOX / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=SANDBOX, check=True, capture_output=True, text=True
    ).stdout.strip()


def commit_and_push(push: bool) -> str:
    git("init", "-q", "-b", BRANCH)
    git("add", "-A")
    git(
        "-c", "user.name=lattice-lab pilot", "-c", "user.email=pilot@lattice-lab.invalid",
        "commit", "-q", "-m", "The VO + T13 pilot's sandbox: card, data, tools, library, target",
    )  # fmt: skip
    base = git("rev-parse", "HEAD")
    (HERE / "base.txt").write_text(base + "\n")
    if push:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=REPO, check=True, capture_output=True,
            text=True,
        ).stdout.strip()  # fmt: skip
        git("push", "-q", url, f"HEAD:refs/heads/{BRANCH}", f"HEAD:refs/heads/{SUBMISSION}")
    return base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    manifest = build(args.force)
    base = commit_and_push(args.push)
    where = f"pushed to {BRANCH}" if args.push else "not pushed"
    print(f"built {SANDBOX}: {len(manifest)} protected files, base {base[:12]}, {where}")


if __name__ == "__main__":
    main()
