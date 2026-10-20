"""
Judge the seventh pilot (ninth powers at m = 37), independently of the agent's own report.

    uv run --no-sync python examples/llm-pilot-37c/judge.py <round> [<branch>]

The question is open, so there is no pinned theorem. The agent submits a mechanism as
`condition(f, m)` in mechanism.py (CARD.md), and the judge checks it:

1. **Library unchanged.** Against the base commit, the branch changes only Pilot.lean, files
   under proofs/LatticeProofs/Pilot/, the deliverables (mechanism.py, proposal.md, proposal.py,
   report.md) and files under scratch/. Every file in manifest.json still has its sha256 there.
2. **Explains**: a claim with q divisible by 9, at m = 37, for the five targets
   (4850, 699738, 985232, 1431278, 1968276).
3. **Sound**: `condition` runs, each set in a process of its own (evaluate.py), on
   - the atlas's 1,274 rules at every census size (odd m from 9 to 161 with ord_m(2) even) and at
     the fourth pilot's held-out sizes (163 to 333);
   - square rules of radius 4 at the sizes of the agent's cube data (21, 25, 29 to 125): a fixed
     sample of 2,000 and every confinement those censuses left unexplained;
   - at 37, the agent's 42 ninth-power rules of radius 4 and 5 and a sample of 2,000 of radius 5;
   - held out: at 37, every ninth-power rule of the registered radius-6 census (study.py) and a
     sample of 2,000 of radius 6; and a sample of 2,000 of radius 5 at the odd m from 127 to 161
     with ord_m(2) even.
   Every claim q > 1 is checked with census.confined, the orchestrator's own eigenvalue
   computation. One false claim refutes the mechanism as stated.
4. **Reach**: how many claims hold, how many of them the atlas procedure does not account for,
   and how many unexplained confinements they cover: the radius-6 census's (held out), the cube
   census remainder at the training sizes, and the atlas census remainder.
5. **Lean**, if Pilot.lean changed: it builds against the real library, and every theorem's
   axioms are listed.

It also runs the agent's proposal.py, for the record, and writes judgements/round-<n>.json. Only
checks 1, 2, 5 and the training part of 3 may be reported back to the agent; never the held-out
results.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PROOFS = REPO / "proofs"
CLONE = Path("/home/user/pilot-sandbox-37c")
BRANCH = "pilot-37c-submission"
WORK = Path("/tmp/claude-0/pilot-judge-37c")
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

sys.path.insert(0, str(HERE.parent / "llm-pilot-37b"))
import cubes37b  # noqa: E402

# this pilot's study.py (the registered radius-6 census, and the fast census it uses), by path,
# since the sixth pilot's directory, on the path for cubes37b, has a study.py of its own
_spec = importlib.util.spec_from_file_location("pilot37c_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

census = cubes37b.census
family = cubes37b.family
# the fast census at 37 (rule-4850/census.py), by path too: "census" here is the fourth pilot's
_spec = importlib.util.spec_from_file_location("rule4850_census",
                                               HERE.parent / "rule-4850" / "census.py")  # fmt: skip
fast = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fast)


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
    if os.environ.get("JUDGE_QUICK"):  # for testing the judge itself: a few sizes of each kind
        return {"atlas_train": [37, 61], "atlas_heldout": [163], "family_train": [37, 61],
                "square5_heldout": [127]}  # fmt: skip
    pilot4 = (HERE.parent / "llm-pilot-37" / "ledger.jsonl").read_text().splitlines()
    data = HERE / "data"
    family_sizes = [s["m"] for s in json.loads((data / "family.json").read_text())["sizes"]]
    family_sizes += [s["m"] for s in json.loads((data / "family_77_125.json").read_text())["sizes"]]
    return {
        "atlas_train": census.cube_sizes(9, 161),
        "atlas_heldout": json.loads(pilot4[0])["body"]["sizes"],
        "family_train": family_sizes,
        "square5_heldout": census.cube_sizes(127, 161),
    }


def cube_hits() -> dict[int, list[int]]:
    """The radius-4 family's cube confinements that no known mechanism explains, at the sizes of
    the agent's data (the fifth and sixth pilots' censuses)."""
    data = HERE / "data"
    out = {}
    for s in json.loads((data / "family.json").read_text())["sizes"]:
        out[s["m"]] = [h["id"] for h in s["hits"] if (h["pilot4_q"] * h["pilot5_q"]) % 3]
    for r in json.loads((data / "family_77_125.json").read_text())["sizes"]:
        out[r["m"]] = [h["id"] for h in r["hits"]
                       if h["known_q"] % 3 and not h["procedure"].startswith("splits")]  # fmt: skip
    return out


def ninth_sets() -> dict[str, list[tuple[int, int]]]:
    """(radius, rule id) at 37: the agent's ninth-power rules (radius 4 and 5) with a radius-5
    sample; and, held out, the registered radius-6 census's ninth-power rules with a radius-6
    sample. Also the unexplained ones, for coverage."""
    rng = random.Random(375)
    data = json.loads((HERE / "data" / "ninth37.json").read_text())
    train = [(fam["radius"], h["id"]) for fam in data["families"] for h in fam["ninth_power_rules"]]
    train += [(5, n) for n in rng.sample(range(1, 1 << 21), 2000)]
    targets = [(4 if n < 1 << 15 else 5, n) for n in study.TARGETS]
    rows = [json.loads(line) for line in (HERE / "records.jsonl").read_text().splitlines()]
    hits = [r for r in rows if r["test"] == "hit"]
    rng6 = random.Random(376)
    heldout = [(6, r["id"]) for r in hits] + [(6, n) for n in rng6.sample(range(1, 1 << 28), 2000)]
    new = [r for r in hits if not (r["explained"] or r["image_of"] or r["multiple_of"])]
    unexplained = [(6, r["id"]) for r in new]
    return {"train": train, "heldout": heldout, "targets": targets, "unexplained": unexplained}


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
    g, hits, nine = grids(), cube_hits(), ninth_sets()
    atlas = {r["id"]: r for r in cubes37b.atlas_rules()}
    claims, per_m = [], {}

    def check(name, f, m, q, split, key=None):
        holds = census.confined(f, m, q)
        known = holds and census.explained(f, m, q, key)
        claims.append({"m": m, "rule": name, "q": q, "holds": holds, "known_mechanism": known,
                       "split": split})  # fmt: skip

    def square(entries, m, tag, split):
        rules = [{"id": f"r{rad}:{n}", "terms": sorted(map(list, fast.rule(n, rad)))}
                 for rad, n in entries]  # fmt: skip
        r = evaluate(tree, rules, m, tag)
        per_m[f"{tag} {m}"] = {k: v for k, v in r.items() if k != "claims"} | {"rules": len(rules)}
        for rid, q in r["claims"].items():
            rad, n = rid[1:].split(":")
            check(f"square r{rad} {n}", fast.rule(int(n), int(rad)), m, q, split)

    for split in ("train", "heldout"):
        for m in g[f"atlas_{split}"]:
            r = evaluate(tree, list(atlas.values()), m, "atlas")
            per_m[f"atlas {m}"] = {k: v for k, v in r.items() if k != "claims"}
            for rid, q in r["claims"].items():
                rule = atlas[int(rid)]
                key = (rule["lattice"], tuple(rule["shells"]))
                f = frozenset(map(tuple, rule["terms"]))
                check(f"{rule['lattice']} {'+'.join(rule['shells'])}", f, m, q, split, key)
    for m in g["family_train"]:
        ids = sorted(set(cubes37b.sample()) | set(hits.get(m, [])))
        square([(4, b) for b in ids], m, "family", "train")
    square(sorted(set(nine["train"])), 37, "ninth37", "train")
    square(sorted(set(nine["heldout"])), 37, "radius6", "heldout")
    rng = random.Random(161)
    sample5 = [(5, n) for n in rng.sample(range(1, 1 << 21), 2000)]
    for m in g["square5_heldout"]:
        square(sample5, m, "square5", "heldout")

    def covered(m, name, q=9):
        return any(c["m"] == m and c["rule"] == name and c["holds"] and c["q"] % q == 0
                   for c in claims)  # fmt: skip

    targets = [(37, f"square r{rad} {n}") for rad, n in nine["targets"]]
    explained = [t for t in targets if covered(*t)]
    coverage = {
        "radius6_unexplained": [
            n for rad, n in nine["unexplained"] if covered(37, f"square r{rad} {n}")
        ],  # fmt: skip
        "cube_hits_train": [
            (m, b)
            for m in g["family_train"]
            for b in hits.get(m, [])
            if covered(m, f"square r4 {b}", 3)
        ],  # fmt: skip
        "remainder": [
            (e["m"], e["lattice"], e["shells"])
            for e in cubes37b.cubes25.remainder_rows()
            if covered(e["m"], f"{e['lattice']} {e['shells']}", 3)
        ],  # fmt: skip
    }
    totals = {"radius6_unexplained": len(nine["unexplained"]),
              "cube_hits_train": sum(len(hits.get(m, [])) for m in g["family_train"]),
              "remainder": len(cubes37b.cubes25.remainder_rows())}  # fmt: skip

    def tally(split):
        cs = [c for c in claims if c["split"] == split]
        return {
            "claims": len(cs),
            "false": [c for c in cs if not c["holds"]],
            "hold": sum(c["holds"] for c in cs),
            "beyond_known": sum(c["holds"] and not c["known_mechanism"] for c in cs),
            "ninth_or_more": sum(c["holds"] and c["q"] % 9 == 0 for c in cs),
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
    # "local:<ref>" judges a ref of the local clone (for testing the judge); otherwise fetch
    head = git("rev-parse", branch[6:]).strip() if branch.startswith("local:") else fetch(branch)
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
