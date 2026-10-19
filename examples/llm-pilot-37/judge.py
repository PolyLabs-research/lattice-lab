"""
Judge the m = 37 pilot, independently of the agent's own report.

    uv run python examples/llm-pilot-37/judge.py <round> [<branch>]

The question is open, so there is no pinned theorem. The agent submits a mechanism as
`condition(f, m)` in mechanism.py (CARD.md), and the judge checks it:

1. **Library unchanged.** Against the base commit, the branch changes only Pilot.lean, files
   under proofs/LatticeProofs/Pilot/, the deliverables (mechanism.py, proposal.md, proposal.py,
   report.md) and files under scratch/. Every file in manifest.json still has its sha256 there.
2. **Explains**: what `condition` claims for the six unexplained rules at m = 37.
3. **Sound**: `condition` runs on all 1,274 rules at every m of the grid, each m in a process of
   its own (evaluate.py). The grid is the census's sizes (odd m from 9 to 161 with ord_m(2) even)
   and the registered study's held-out sizes. Every claim q > 1 is checked with census.confined,
   the orchestrator's own eigenvalue computation. One false claim refutes the mechanism as stated.
4. **Reach**: how many claims hold, how many of those the known mechanisms do not account for,
   and how many of the census's unexplained entries (training and held-out) the claims cover.
5. **Lean**, if Pilot.lean changed: it builds against the real library, and every theorem's
   axioms are listed.

It also runs the agent's proposal.py, for the record, and writes judgements/round-<n>.json. Only
checks 1, 2, 5 and the training part of 3 may be reported back to the agent; never the held-out
results.
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
CLONE = Path("/home/user/pilot-sandbox-37")
BRANCH = "pilot-37-submission"
WORK = Path("/tmp/claude-0/pilot-judge-37")
PYTHON = REPO / ".venv" / "bin" / "python"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
ALLOWED = (
    "proofs/LatticeProofs/Pilot.lean",
    "mechanism.py",
    "proposal.md",
    "proposal.py",
    "report.md",
)
ALLOWED_DIRS = ("proofs/LatticeProofs/Pilot/", "scratch/")
SIX = [
    ("square", "A4+K8+B4+self"),
    ("triangle", "VS+T9+T13+self"),
    ("square", "K8+M8+E4"),
    ("square", "C4+L8+M8"),
    ("square", "C4+L8+M8+E4"),
    ("square", "A4+B4+C4+L8+E4+self"),
]
PER_M_TIMEOUT = 600
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}

sys.path.insert(0, str(HERE))
import census  # noqa: E402


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
    tree = WORK / "tree"
    tree.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "archive", head], cwd=CLONE, check=True, capture_output=True
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(tree)], input=archive, check=True)
    return tree


def declared(source: str) -> list[str]:
    """Full names of the theorems a Lean file declares, through its namespace blocks."""
    stack, out = [], []
    for line in source.splitlines():
        if m := re.match(r"namespace\s+([\w.]+)", line):
            stack.append(m.group(1))
        elif (m := re.match(r"end\s+([\w.]+)", line)) and stack and stack[-1] == m.group(1):
            stack.pop()
        elif m := re.match(r"(?:theorem|lemma)\s+([\w.']+)", line):
            out.append(".".join([*stack, m.group(1)]))
    return out


def lean_check(tree: Path, base: str, head: str) -> dict:
    lean = [p for _, p in library_check(base, head)["touched"] if p.endswith(".lean")]
    if not lean:
        return {"present": False}
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
    (proj / ".lake").mkdir()
    (proj / ".lake" / "packages").symlink_to(PROOFS / ".lake" / "packages")
    shutil.copytree(PROOFS / ".lake" / "build", proj / ".lake" / "build", symlinks=True)
    pilot = proj / "LatticeProofs"
    sources = [(pilot / "Pilot.lean").read_text()]
    sources += [p.read_text() for p in pilot.glob("Pilot/**/*.lean")]
    forbidden = [w for w in ["axiom ", "native_decide"] if any(w in s for s in sources)]
    build = run(["lake", "build", "LatticeProofs.Pilot"], proj, 3600)
    names = sorted({n for s in sources for n in declared(s)})
    (proj / "AllAxioms.lean").write_text(
        "import LatticeProofs.Pilot\n" + "".join(f"#print axioms {n}\n" for n in names)
    )
    every = run(["lake", "env", "lean", "AllAxioms.lean"], proj, 1800)
    found = re.findall(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", every["output"])
    axioms = {n: sorted(a.strip() for a in ax.split(",")) for n, ax in found}
    for n in re.findall(r"'([\w.']+)' does not depend on any axioms", every["output"]):
        axioms[n] = []
    standard = [n for n, ax in axioms.items() if set(ax) <= STANDARD]
    return {
        "present": True,
        "builds": build["returncode"] == 0,
        "forbidden_words": forbidden,
        "theorems": axioms,
        "standard": standard,
        "build": build,
    }


def grid() -> tuple[list[int], list[int]]:
    train = census.cube_sizes(9, 161)
    ledger = (HERE / "ledger.jsonl").read_text().splitlines()
    heldout = json.loads(ledger[0])["body"]["sizes"]
    return train, heldout


def census_rows() -> dict[str, set[tuple[int, str, str]]]:
    """The unexplained confinements found by the census: training, and held-out (the study)."""
    out = {"train": set(), "heldout": set()}
    with open(HERE / "data" / "unexplained.csv") as f:
        for row in csv.DictReader(f):
            out["train"].add((int(row["m"]), row["lattice"], row["shells"]))
    records = HERE / "records.jsonl"
    if records.exists():
        for line in records.read_text().splitlines():
            for row in json.loads(line)["unexplained"]:
                out["heldout"].add((row["m"], row["lattice"], row["shells"]))
    return out


def mechanism_check(tree: Path) -> dict:
    if not (tree / "mechanism.py").exists():
        return {"present": False}
    rules = census.rules()
    rules_json = tree / "data" / "rules.json"
    train, heldout = grid()
    per_m, claims = {}, []
    for m in sorted(set(train) | set(heldout) | {37}):
        out = WORK / f"eval-{m}.json"
        r = run([str(PYTHON), str(HERE / "evaluate.py"), str(tree), str(rules_json), str(m),
                 str(out)], tree, PER_M_TIMEOUT)  # fmt: skip
        if r["returncode"] != 0 or not out.exists():
            per_m[m] = {"ok": False, "run": r}
            continue
        result = json.loads(out.read_text())
        per_m[m] = {"ok": True, "seconds": result["seconds"], "errors": len(result["errors"]),
                    "first_error": next(iter(result["errors"].values()), None)}  # fmt: skip
        for rid, q in result["claims"].items():
            lattice, shells, f = rules[int(rid)]
            holds = census.confined(f, m, q)
            known = holds and census.explained(f, m, q, (lattice, shells))
            claims.append({"m": m, "lattice": lattice, "shells": "+".join(shells), "q": q,
                           "holds": holds, "known_mechanism": known,
                           "split": "heldout" if m in heldout else "train"})  # fmt: skip
    six = {f"{lat} {sh}": next((c["q"] for c in claims if c["m"] == 37 and c["lattice"] == lat
                                and c["shells"] == sh), 1) for lat, sh in SIX}  # fmt: skip
    rows = census_rows()
    covered = {
        split: sorted(
            k
            for k in rows[split]
            if any(
                (c["m"], c["lattice"], c["shells"]) == k and c["holds"] and c["q"] % 3 == 0
                for c in claims
            )  # fmt: skip
        )
        for split in rows
    }

    def tally(split):
        cs = [c for c in claims if c["split"] == split]
        return {
            "claims": len(cs),
            "false": [c for c in cs if not c["holds"]],
            "hold": sum(c["holds"] for c in cs),
            "beyond_known": sum(c["holds"] and not c["known_mechanism"] for c in cs),
        }

    return {
        "present": True,
        "six": six,
        "explains_six": all(q > 1 and q % 3 == 0 for q in six.values()),
        "train": tally("train"),
        "heldout": tally("heldout"),
        "census_covered": {k: (len(v), len(rows[k])) for k, v in covered.items()},
        "census_covered_rows": covered,
        "per_m": per_m,
        "all_ran": all(v["ok"] and not v["errors"] for v in per_m.values()),
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
    result = {
        "round": round_no,
        "branch": branch,
        "base": base,
        "head": head,
        "library": library_check(base, head),
        "mechanism": mechanism_check(tree),
        "lean": lean_check(tree, base, head),
        "proposal": proposal_run(tree),
    }
    mech = result["mechanism"]
    result["sound"] = mech.get("present", False) and not mech["train"]["false"] and not mech[
        "heldout"]["false"]  # fmt: skip
    out = HERE / "judgements" / f"round-{round_no}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    summary = {
        "head": head[:12],
        "library_ok": result["library"]["ok"],
        "mechanism": mech.get("present", False) and {
            "explains_six": mech["explains_six"], "six": mech["six"], "all_ran": mech["all_ran"],
            "train": {k: (len(v) if k == "false" else v) for k, v in mech["train"].items()},
            "heldout": {k: (len(v) if k == "false" else v) for k, v in mech["heldout"].items()},
            "census_covered": mech["census_covered"],
        },
        "sound": result["sound"],
        "lean": result["lean"].get("present") and {
            "builds": result["lean"]["builds"], "standard": result["lean"]["standard"],
            "theorems": list(result["lean"]["theorems"]),
        },
        "proposal_returncode": result["proposal"].get("returncode"),
    }  # fmt: skip
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
