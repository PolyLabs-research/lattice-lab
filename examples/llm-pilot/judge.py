"""
Judge the pilot's proof, independently of the agent's own report.

    uv run python examples/llm-pilot/judge.py <round>

1. **Library unchanged.** Every library file in the sandbox has the sha256 recorded when the
   sandbox was built, and nothing new sits outside Pilot.lean and LatticeProofs/Pilot/.
2. **The proof builds against the real library.** Pilot.lean and LatticeProofs/Pilot/ are copied
   into a fresh copy of the repository's proofs/, and `lake build LatticeProofs.Pilot` runs.
3. **The statement is the pinned one, and the axioms are standard.** The repository's own
   PilotCheck.lean, not the sandbox's, is compiled. It restates the theorem, and its
   `#print axioms` must show only propext, Classical.choice and Quot.sound.

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
SANDBOX = Path("/home/user/pilot-sandbox")
WORK = Path("/tmp/claude-0/pilot-judge")
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_check() -> dict:
    manifest = json.loads((SANDBOX / "manifest.json").read_text())
    changed = [rel for rel, h in manifest.items() if sha256(SANDBOX / "proofs" / rel) != h]
    allowed = set(manifest) | {"LatticeProofs/Pilot.lean"}
    new = []
    for path in (SANDBOX / "proofs").rglob("*.lean"):
        rel = str(path.relative_to(SANDBOX / "proofs"))
        if rel.startswith(".lake/"):
            continue
        if rel not in allowed and not rel.startswith("LatticeProofs/Pilot/"):
            new.append(rel)
    return {"ok": not changed and not new, "changed": changed, "unexpected_files": new}


def run(cmd: list[str], cwd: Path, timeout: int) -> dict:
    start = time.time()
    try:
        out = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True, timeout=timeout)
        code, text = out.returncode, out.stdout + out.stderr
    except subprocess.TimeoutExpired as e:
        code, text = -1, f"timeout after {timeout} s\n{e.stdout or ''}{e.stderr or ''}"
    return {"returncode": code, "seconds": round(time.time() - start, 1), "output": text[-20000:]}


def lean_check() -> dict:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    for item in ["lakefile.toml", "lean-toolchain", "lake-manifest.json", "LatticeProofs.lean"]:
        shutil.copy(PROOFS / item, WORK / item)
    shutil.copytree(PROOFS / "LatticeProofs", WORK / "LatticeProofs")
    shutil.copy(SANDBOX / "proofs" / "LatticeProofs" / "Pilot.lean", WORK / "LatticeProofs")
    if (SANDBOX / "proofs" / "LatticeProofs" / "Pilot").is_dir():
        shutil.copytree(
            SANDBOX / "proofs" / "LatticeProofs" / "Pilot", WORK / "LatticeProofs" / "Pilot"
        )
    shutil.copy(HERE / "PilotCheck.lean", WORK / "PilotCheck.lean")
    (WORK / ".lake").mkdir()
    (WORK / ".lake" / "packages").symlink_to(PROOFS / ".lake" / "packages")
    shutil.copytree(PROOFS / ".lake" / "build", WORK / ".lake" / "build", symlinks=True)
    source = (WORK / "LatticeProofs" / "Pilot.lean").read_text()
    sources = [source] + [p.read_text() for p in (WORK / "LatticeProofs").glob("Pilot/**/*.lean")]
    forbidden = [
        w for w in ["sorry", "axiom ", "native_decide", "admit"] if any(w in s for s in sources)
    ]
    build = run(["lake", "build", "LatticeProofs.Pilot"], WORK, 3600)
    check = run(["lake", "env", "lean", "PilotCheck.lean"], WORK, 1800)
    axioms = re.findall(r"depends on axioms: \[([^\]]*)\]", check["output"])
    used = {a.strip() for a in axioms[0].split(",")} if axioms else None
    ok = (
        build["returncode"] == 0
        and check["returncode"] == 0
        and used is not None
        and used <= STANDARD
        and "error" not in check["output"]
    )
    return {
        "ok": ok,
        "forbidden_words": forbidden,
        "axioms": sorted(used) if used is not None else None,
        "build": build,
        "check": check,
    }


def proposal_run() -> dict:
    if not (SANDBOX / "proposal.py").exists():
        return {"present": False}
    return {"present": True, **run([str(SANDBOX / "python"), "proposal.py"], SANDBOX, 1800)}


def main() -> None:
    round_no = int(sys.argv[1])
    result = {
        "round": round_no,
        "library": library_check(),
        "lean": lean_check(),
        "proposal": proposal_run(),
    }
    result["passed"] = result["library"]["ok"] and result["lean"]["ok"]
    out = HERE / "judgements" / f"round-{round_no}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        "passed": result["passed"],
        "library_ok": result["library"]["ok"],
        "lean_ok": result["lean"]["ok"],
        "axioms": result["lean"]["axioms"],
        "forbidden": result["lean"]["forbidden_words"],
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
