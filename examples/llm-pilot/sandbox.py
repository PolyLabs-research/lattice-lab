"""
Build the pilot's sandbox: the problem card, the tools, and the Lean library, without the
write-ups.

    uv run python examples/llm-pilot/sandbox.py [--force]

The sandbox (/home/user/pilot-sandbox) holds:
- CARD.md, the problem card;
- tools/, the numeric tools;
- proofs/, the Lean project's sources and Axioms.lean, with Pilot.lean (the target, with
  `sorry`) and PilotCheck.lean (the pinned statement). It does not include generate.py, which
  needs the atlas code. Its .lake/build is a copy, and .lake/packages (mathlib) is a link to the
  built one;
- python, a wrapper that runs the repository's venv interpreter, with numpy and sympy;
- manifest.json, the sha256 of every library file copied, for the judge.

docs/ and examples/ are left out: docs/ holds the hand proof of the hexagon law's 2-part.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROOFS = REPO / "proofs"
SANDBOX = Path("/home/user/pilot-sandbox")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_files(root: Path) -> list[Path]:
    """The Lean sources and project files the sandbox carries over, relative to root."""
    files = [root / "lakefile.toml", root / "lean-toolchain", root / "lake-manifest.json"]
    files += [root / "LatticeProofs.lean", root / "Axioms.lean", root / "check.sh"]
    files += sorted((root / "LatticeProofs").glob("*.lean"))
    # HexTwoPart.lean is the pilot's own answer, and TriTwoPart.lean and VOT13Law.lean the later
    # pilots', all added to the library afterwards.
    later = ("Pilot.lean", "HexTwoPart.lean", "TriTwoPart.lean", "VOT13Law.lean")
    return [f.relative_to(root) for f in files if f.name not in later]


def build(force: bool) -> dict:
    if SANDBOX.exists():
        if not force:
            raise SystemExit(f"{SANDBOX} exists; pass --force to rebuild it")
        shutil.rmtree(SANDBOX)
    (SANDBOX / "proofs" / "LatticeProofs").mkdir(parents=True)
    shutil.copy(HERE / "card.md", SANDBOX / "CARD.md")
    shutil.copytree(HERE / "tools", SANDBOX / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    manifest = {}
    for rel in library_files(PROOFS):
        target = SANDBOX / "proofs" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(PROOFS / rel, target)
        manifest[str(rel)] = sha256(target)
    shutil.copy(HERE / "Pilot.lean", SANDBOX / "proofs" / "LatticeProofs" / "Pilot.lean")
    shutil.copy(HERE / "PilotCheck.lean", SANDBOX / "proofs" / "PilotCheck.lean")
    manifest["PilotCheck.lean"] = sha256(SANDBOX / "proofs" / "PilotCheck.lean")
    lake = SANDBOX / "proofs" / ".lake"
    lake.mkdir()
    (lake / "packages").symlink_to(PROOFS / ".lake" / "packages")
    shutil.copytree(PROOFS / ".lake" / "build", lake / "build", symlinks=True)
    # A wrapper, not a symlink: through a symlink the interpreter does not find the venv, so the
    # first pilot ran without sympy (log.md). Called by its venv path, it does.
    venv_python = REPO / ".venv" / "bin" / "python"
    (SANDBOX / "python").write_text(f'#!/bin/sh\nexec "{venv_python}" "$@"\n')
    (SANDBOX / "python").chmod(0o755)
    (SANDBOX / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    manifest = build(parser.parse_args().force)
    print(f"built {SANDBOX}: {len(manifest)} library files")


if __name__ == "__main__":
    main()
