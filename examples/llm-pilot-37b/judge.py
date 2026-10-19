"""
Judge the sixth pilot (the square family at m = 37), independently of the agent's own report.

    uv run python examples/llm-pilot-37b/judge.py <round> [<branch>]

The question is open, so there is no pinned theorem. The agent submits a mechanism as
`condition(f, m)` in mechanism.py (CARD.md), and the judge checks it:

1. **Library unchanged.** Against the base commit, the branch changes only Pilot.lean, files
   under proofs/LatticeProofs/Pilot/, the deliverables (mechanism.py, proposal.md, proposal.py,
   report.md) and files under scratch/. Every file in manifest.json still has its sha256 there.
2. **Explains**: what `condition` claims for the 19 targets (data/targets.json): the 16 family
   rules confined to the cubes at m = 37 that neither earlier pilot's condition explains, and
   three of them again at m = 61.
3. **Sound**: `condition` runs, each m in a process of its own (evaluate.py), on
   - the atlas's 1,274 rules at every census size (odd m from 9 to 161 with ord_m(2) even) and at
     the m = 37 pilot's held-out sizes (163 to 333);
   - family rules at m = 21 and 25, at the fifth pilot's census sizes (29 to 75), which are this
     agent's data, and at this pilot's registered held-out sizes (77 to 125): a fixed sample of
     2,000 (cubes37b.sample) and every confined rule the censuses found there.
   Every claim q > 1 is checked with census.confined, the orchestrator's own eigenvalue
   computation. One false claim refutes the mechanism as stated.
4. **Reach**: how many claims hold, how many the atlas procedure does not account for, and how
   many unexplained confinements they cover: the census remainder's 45, the family's at the
   training sizes (those neither earlier condition explains), and the family's at the held-out
   sizes (the registered study's records).
5. **Lean**, if Pilot.lean changed: it builds against the real library, and every theorem's
   axioms are listed.

It also runs the agent's proposal.py, for the record, and writes judgements/round-<n>.json. Only
checks 1, 2, 5 and the training part of 3 may be reported back to the agent; never the held-out
results.
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
CLONE = Path("/home/user/pilot-sandbox-37b")
BRANCH = "pilot-37b-submission"
WORK = Path("/tmp/claude-0/pilot-judge-37b")
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
PER_M_TIMEOUT = 600
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}

sys.path.insert(0, str(HERE))
import cubes37b  # noqa: E402

census = cubes37b.census
family = cubes37b.family


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


def grids() -> dict[str, list[int]]:
    ledger = (HERE / "ledger.jsonl").read_text().splitlines()
    pilot4 = (HERE.parent / "llm-pilot-37" / "ledger.jsonl").read_text().splitlines()
    return {
        "atlas_train": census.cube_sizes(9, 161),
        "atlas_heldout": json.loads(pilot4[0])["body"]["sizes"],
        "family_train": [
            s["m"] for s in json.loads((HERE / "data" / "family.json").read_text())["sizes"]
        ],  # fmt: skip
        "family_heldout": json.loads(ledger[0])["body"]["sizes"],
    }


def family_hits() -> dict[int, list[int]]:
    """The family's confinements that no known mechanism explains: at the training sizes (the
    agent's data/family.json, neither earlier condition) and at the held-out sizes (the
    registered study's records, which also count split rules apart)."""
    out = {}
    for s in json.loads((HERE / "data" / "family.json").read_text())["sizes"]:
        out[s["m"]] = [h["id"] for h in s["hits"] if (h["pilot4_q"] * h["pilot5_q"]) % 3]
    records = HERE / "records.jsonl"
    if records.exists():
        for line in records.read_text().splitlines():
            r = json.loads(line)
            out[r["m"]] = [
                h["id"]
                for h in r["hits"]
                if h["known_q"] % 3 and not h["procedure"].startswith("splits")
            ]
    return out


def evaluate(tree: Path, rules: list[dict], m: int, tag: str) -> dict:
    rules_path = WORK / f"rules-{tag}-{m}.json"
    rules_path.write_text(json.dumps(rules))
    out = WORK / f"eval-{tag}-{m}.json"
    r = run([str(PYTHON), str(HERE / "evaluate.py"), str(tree), str(rules_path), str(m), str(out)],
            tree, PER_M_TIMEOUT)  # fmt: skip
    if r["returncode"] != 0 or not out.exists():
        return {"ok": False, "run": r, "claims": {}}
    result = json.loads(out.read_text())
    return {"ok": True, "seconds": result["seconds"], "errors": len(result["errors"]),
            "first_error": next(iter(result["errors"].values()), None),
            "claims": result["claims"]}  # fmt: skip


def mechanism_check(tree: Path) -> dict:
    if not (tree / "mechanism.py").exists():
        return {"present": False}
    g, hits = grids(), family_hits()
    atlas = {r["id"]: r for r in cubes37b.atlas_rules()}
    claims, per_m = [], {}

    def check(name, f, m, q, split, key=None):
        holds = census.confined(f, m, q)
        known = holds and census.explained(f, m, q, key)
        claims.append({"m": m, "rule": name, "q": q, "holds": holds, "known_mechanism": known,
                       "split": split})  # fmt: skip

    for split in ("train", "heldout"):
        for m in g[f"atlas_{split}"]:
            r = evaluate(tree, list(atlas.values()), m, "atlas")
            per_m[f"atlas {m}"] = {k: v for k, v in r.items() if k != "claims"}
            for rid, q in r["claims"].items():
                rule = atlas[int(rid)]
                key = (rule["lattice"], tuple(rule["shells"]))
                f = frozenset(map(tuple, rule["terms"]))
                check(f"{rule['lattice']} {'+'.join(rule['shells'])}", f, m, q, split, key)
        for m in g[f"family_{split}"]:
            ids = sorted(set(cubes37b.sample()) | set(hits.get(m, [])))
            rules = [{"id": b, "terms": sorted(map(list, family.rule(b)))} for b in ids]
            r = evaluate(tree, rules, m, "family")
            per_m[f"family {m}"] = {k: v for k, v in r.items() if k != "claims"} | {
                "rules": len(ids)
            }
            for rid, q in r["claims"].items():
                check(f"family {rid}", family.rule(int(rid)), m, q, split)

    def covered(m, name):
        return any(c["m"] == m and c["rule"] == name and c["holds"] and c["q"] % 3 == 0
                   for c in claims)  # fmt: skip

    targets = [(m, f"family {b}") for m, b in cubes37b.targets()]
    explained = [t for t in targets if covered(*t)]
    remainder = [
        (e["m"], f"{e['lattice']} {e['shells']}") for e in cubes37b.cubes25.remainder_rows()
    ]
    coverage = {
        "remainder": [r for r in remainder if covered(*r)],
        "family_train": [
            (m, b) for m in g["family_train"] for b in hits.get(m, []) if covered(m, f"family {b}")
        ],
        "family_heldout": [
            (m, b)
            for m in g["family_heldout"]
            for b in hits.get(m, [])
            if covered(m, f"family {b}")
        ],  # fmt: skip
    }
    totals = {"remainder": len(remainder),
              "family_train": sum(len(hits.get(m, [])) for m in g["family_train"]),
              "family_heldout": sum(len(hits.get(m, [])) for m in g["family_heldout"])}  # fmt: skip

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
        "targets": {"explained": len(explained), "of": len(targets), "rules": explained},
        "train": tally("train"),
        "heldout": tally("heldout"),
        "coverage": {k: (len(v), totals[k]) for k, v in coverage.items()},
        "coverage_rows": coverage,
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
            "targets": f"{mech['targets']['explained']} of {mech['targets']['of']}",
            "all_ran": mech["all_ran"],
            "train": {k: (len(v) if k == "false" else v) for k, v in mech["train"].items()},
            "heldout": {k: (len(v) if k == "false" else v) for k, v in mech["heldout"].items()},
            "coverage": mech["coverage"],
        },
        "sound": result["sound"],
        "lean": result["lean"].get("present") and {
            "builds": result["lean"]["builds"], "forbidden": result["lean"]["forbidden_words"],
            "theorems": len(result["lean"]["theorems"]),
            "standard": len(result["lean"]["standard"]),
        },
        "proposal_returncode": result["proposal"].get("returncode"),
    }  # fmt: skip
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
