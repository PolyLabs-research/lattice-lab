"""
Census stage 3d: the classes stage 3b/3c left unfinished on its 9 "incomplete" tori, settled
with a second implementation (DistQLDPC's cluster engine), and those tori judged again by stage
3b's registered rules.

    uv run --no-sync python examples/qec-census-3d/study.py register
    uv run --no-sync python examples/qec-census-3d/study.py run --workers 32
    uv run --no-sync python examples/qec-census-3d/study.py resume --workers 32  (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-3d

**Why.** Stage 3b/3c judged 9 extrapolation tori "incomplete" for P1-P3. On each, some connected
classes at one k (k = 4; and k = 6 on 3 x 49) did not finish their exact search within 30
minutes. 154 such classes are listed in the question, by their records. Every one has a search
lower bound of 23 and a verified window upper bound of 24. The spot-check
(docs/census-stage3b-spotcheck-plan.md) found DistQLDPC's cluster engine settles codes like these
in minutes.

**Known at registration** (the question says so). For this family d is even (A and B have odd
weight, so the all-ones vector lies in the row space of H_X: docs/code-census.md, "Proved", 6).
So 23 <= d <= 24 already gives d = 24 for every listed class. This study does not depend on that
argument: it measures each d with an instrument written apart from this project, and checks a
weight-24 witness with this project's own verify_witness. What it tests is the instruments,
stage 3b's lower bounds above all. The per-torus outcomes that follow from d = 24 were computed
at registration and are prediction T.

**The job, per class.**
- DistQLDPC (env DISTQLDPC, at the commit pinned in DISTQLDPC_COMMIT, checked before the run)
  with -engine=cc and a 2-hour limit, through examples/qec-census-3b/spotcheck/distq.py.
- A witness: window.c (examples/qec-open-distance/parts.py) for kind Z, seeds 0 and 1, 120 s
  each; if neither reaches weight 24, seeds 2-9 for 900 s each. Its lightest logical is checked by
  distance.verify_witness.

**The predictions.**
- **D1.** Every listed class has d = 24: DistQLDPC returns exactly 24 (exit 0), and a verified
  Z-logical of weight 24 is found. It fails if any DistQLDPC result excludes 24 (an exact value
  other than 24, or bounds that exclude it) or any verified logical is lighter than 24. It is
  incomplete if any class has no exact DistQLDPC value or no weight-24 witness.
- **T.** Stage 3b's judge_torus, on each torus's record with the unsettled best entries replaced
  by the maximum of the recorded best and this run's d's (and settled when every listed class at
  that k is exact), gives the outcomes in T_EXPECTED.

The verdict passes when both pass; it is "invalid" if the code, the cited records or the
DistQLDPC commit differ from the registration. Stage 3b/3c's registered verdict is not changed;
this study reports beside it.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
S3B = HERE.parent / "qec-census-3b"
S3C = HERE.parent / "qec-census-3c"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s3b = _load("qec_census_stage3b_study", S3B / "study.py")
distq = _load("spotcheck_distq", S3B / "spotcheck" / "distq.py")
parts = _load("qec_open_parts", HERE.parent / "qec-open-distance" / "parts.py")
distance = parts.distance

from lattice_lab.ledger import Ledger, record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-census-stage3d"
TORI = [(3, 45), (5, 27), (2, 69), (3, 46), (6, 23), (3, 47), (2, 72), (4, 36), (3, 49)]
DISTQLDPC_COMMIT = "8fe913e2ca79bda37cb755975b06b1b60416a418"  # the spot-check's
LIMIT = 7200
D_EXPECTED = 24
WINDOW_FIRST = ((0, 1), 120.0)
WINDOW_MORE = (tuple(range(2, 10)), 900.0)
RECORDS = [S3B / "records.jsonl", S3C / "records.jsonl"]
HASHED = {"study_py": HERE / "study.py", "tests_py": ROOT / "tests" / "test_qec_census_3d.py",
          "distq_py": S3B / "spotcheck" / "distq.py", "parts_py": parts.__file__,
          "window_c": parts.WINDOW_C, "distance_py": distance.__file__,
          "s3b_study_py": S3B / "study.py"}  # fmt: skip


def code_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in HASHED.items()}


def torus_records() -> list[tuple[str, int, str, dict]]:
    """(file, offset, sha256, record) of each of the 9 tori's stage 3b/3c records."""
    out = []
    for path in RECORDS:
        for offset, digest, line in record_lines(path):
            r = json.loads(line)
            if r.get("job") == "torus" and (r["l"], r["m"]) in TORI:
                out.append((path.parent.name, offset, digest, r))
    return out


def unsettled(rec: dict) -> dict[int, dict]:
    return {int(k): v for k, v in rec["best"]["connected"].items() if not v["settled"]}


def classes() -> list[dict]:
    """The listed classes: on each torus and unsettled k, every connected class whose exact
    search did not finish and whose upper bound exceeds the recorded best d."""
    out = []
    for _, _, _, rec in torus_records():
        for k, best in sorted(unsettled(rec).items()):
            for row in rec["rows"]:
                e = row.get("exact") or {}
                if row["connected"] and row["k"] == k and e.get("status") != "complete" \
                        and (row["upper"] is None or row["upper"] > best["d"]):  # fmt: skip
                    out.append({"torus": [rec["l"], rec["m"]], "n": rec["n"], "k": k,
                                "A": row["A"], "B": row["B"], "lower": e.get("lower"),
                                "upper": row["upper"], "best_recorded": best["d"]})  # fmt: skip
    return out


def key(c: dict) -> str:
    return f"{c['torus'][0]}x{c['torus'][1]}:k={c['k']}:{c['A']}:{c['B']}"


def amended(rec: dict, ds: dict[int, list[int | None]]) -> dict:
    """The torus record with each unsettled best entry replaced by the maximum of the recorded
    best and the d's measured here, settled when every listed class at that k has a d."""
    rec = copy.deepcopy(rec)
    for k, v in rec["best"]["connected"].items():
        got = ds.get(int(k))
        if not v["settled"] and got:
            known = [d for d in got if d is not None]
            v["d"] = max([v["d"], *known])
            if len(known) == len(got):
                v.update(settled=True, unresolved=0)
    return rec


def rejudge(ds_by_torus: dict[str, dict[int, list]]) -> dict[str, dict]:
    out = {}
    for _, _, _, rec in torus_records():
        name = f"{rec['l']}x{rec['m']}"
        j = s3b.judge_torus(amended(rec, ds_by_torus.get(name, {})))
        out[name] = {p: j[p] for p in ("P1", "P2", "P3")}
    return out


def t_expected() -> dict[str, dict]:
    """T: the outcomes if every listed class has d = 24 (computed, not typed)."""
    ds: dict[str, dict[int, list]] = {}
    for c in classes():
        ds.setdefault(f"{c['torus'][0]}x{c['torus'][1]}", {}).setdefault(c["k"], []).append(24)
    return rejudge(ds)


def question() -> dict:
    cs = classes()
    return {"id": ID, "title": "Census stage 3d: the unfinished classes on stage 3b/3c's 9 "
                               "incomplete tori, settled with DistQLDPC",
            "continues": ["examples/qec-census-3b", "examples/qec-census-3c"],
            "records": [{"file": f, "offset": o, "sha256": s, "torus": f"{r['l']}x{r['m']}"}
                        for f, o, s, r in torus_records()],
            "classes": len(cs), "class_keys": [key(c) for c in cs],
            "bounds_recorded": sorted({(c["lower"], c["upper"]) for c in cs}),
            "known_at_registration": "d is even for this family (docs/code-census.md, Proved 6), "
                                     "so lower 23 and upper 24 already give d = 24 for every "
                                     "listed class; T is computed from that. The run measures "
                                     "each d with DistQLDPC and a witness, independently of "
                                     "the parity argument. The spot-check ran DistQLDPC on 20 "
                                     "other frontier codes beforehand, all in agreement.",
            "distqldpc_commit": DISTQLDPC_COMMIT, "limit": LIMIT,
            "window": {"first": WINDOW_FIRST, "more": WINDOW_MORE},
            "sha256": code_hashes()}  # fmt: skip


def predictions() -> list[dict]:
    return [{"id": "D1", "claim": f"every listed class has d = {D_EXPECTED}: DistQLDPC's cc "
                                  "engine returns exactly 24 and a verified weight-24 Z-logical "
                                  "is found",
             "fails_if": "any DistQLDPC result excludes 24, or a verified logical is lighter",
             "incomplete_if": "any class lacks an exact DistQLDPC value or a weight-24 witness"},
            {"id": "T", "claim": "stage 3b's judge_torus on the amended records gives these "
                                 "outcomes", "expected": t_expected()}]  # fmt: skip


def _registered() -> dict | None:
    entries = Ledger(HERE / "ledger.jsonl").entries
    return entries[0]["body"] if entries else None


def distqldpc_commit() -> str | None:
    try:
        argv = ["git", "-C", str(distq.DISTQ), "rev-parse", "HEAD"]
        return subprocess.run(argv, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def consistency() -> list[str]:
    q = _registered()
    if q is None:
        return ["stage 3d is not registered"]
    problems = []
    if q["sha256"] != code_hashes():
        problems.append("the code differs from the registration")
    now = question()
    for k in ("records", "class_keys"):
        if q[k] != now[k]:
            problems.append(f"{k} differ from the registration")
    return problems


def job(c: dict) -> dict:
    """One class: DistQLDPC, then a witness (module docstring)."""
    A, B = [tuple(t) for t in c["A"]], [tuple(t) for t in c["B"]]
    ell, m = c["torus"]
    t0 = time.time()
    out = {"key": key(c), "class": c, "study": ID, "sha256": code_hashes(),
           "pod": os.environ.get("RUNPOD_POD_ID")}  # fmt: skip
    try:
        r = distq.run(A, B, ell, m, engine="cc", limit=LIMIT)
        r["commit"] = distqldpc_commit()
        out["distqldpc"] = r
        windows = []
        for seeds, seconds in (WINDOW_FIRST, WINDOW_MORE):
            w = parts.window(A, B, ell, m, "Z", seeds=seeds, seconds=seconds, workers=1)
            windows.append({k: w[k] for k in ("upper", "witness", "runs", "seconds")})
            if w["upper"] is not None and w["upper"] <= D_EXPECTED:
                break
        best = min((w for w in windows if w["witness"]), key=lambda w: w["upper"], default=None)
        out["window"] = windows
        out["witness"] = best["witness"] if best else None
        out["witness_check"] = distance.verify_witness(A, B, ell, m, "Z", best["witness"]) \
            if best else None  # fmt: skip
    except Exception:
        out["error"] = traceback.format_exc()[-2000:]
    out["seconds"] = round(time.time() - t0, 1)
    return out


def _done(path: Path) -> set[str]:
    return {json.loads(x)["key"] for _, _, x in record_lines(path)} if path.exists() else set()


def execute(path: Path, workers: int) -> None:
    problems = consistency()
    if problems:
        raise RuntimeError("; ".join(problems))
    if distqldpc_commit() != DISTQLDPC_COMMIT:
        raise RuntimeError(f"DistQLDPC at {distqldpc_commit()}, registered {DISTQLDPC_COMMIT}")
    done = _done(path)
    todo = [c for c in classes() if key(c) not in done]
    print(f"{len(todo)} classes to run, {workers} at once", flush=True)
    # a worker killed outright (out of memory) raises BrokenProcessPool here rather than hanging;
    # the pod script then resumes, which skips every class already recorded
    ctx = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as pool:
        for future in as_completed([pool.submit(job, c) for c in todo]):
            rec = future.result()
            append_records(path, [rec])
            print(f"{rec['key']}: d={rec.get('distqldpc', {}).get('d')} "
                  f"witness={rec.get('witness_check', {}) and rec['witness_check']['weight']}"
                  f"{' ERROR' if 'error' in rec else ''}", flush=True)  # fmt: skip


def assess(rec: dict) -> str:
    """'24' (exact 24 with a verified weight-24 witness), 'contradiction', or 'open'. A
    DistQLDPC result that excludes 24 is a contradiction even if the witness step then failed."""
    r, w = rec.get("distqldpc"), rec.get("witness_check")
    if r is None:
        return "open"
    lighter = w is not None and w["logical"] and w["weight"] < D_EXPECTED
    excluded = (r["d"] is not None and r["d"] != D_EXPECTED) or \
        (r["lower"] is not None and r["lower"] > D_EXPECTED) or \
        (r["upper"] is not None and r["upper"] < D_EXPECTED)  # fmt: skip
    if lighter or excluded:
        return "contradiction"
    if "error" in rec:
        return "open"
    if r["d"] == D_EXPECTED and r["returncode"] == 0 and w and w["logical"] \
            and w["weight"] == D_EXPECTED:  # fmt: skip
        return "24"
    return "open"


def decide(rows: list[dict], registered: list[dict]) -> dict:
    problems = consistency()
    last = {r["key"]: r for r in rows}
    expected = [key(c) for c in classes()]
    missing = [k for k in expected if k not in last]
    states = {k: assess(last[k]) for k in expected if k in last}
    commits = sorted({last[k]["distqldpc"].get("commit") for k in states
                      if "distqldpc" in last[k]}, key=str)  # fmt: skip
    if commits not in ([DISTQLDPC_COMMIT], []):
        problems.append(f"DistQLDPC commits {commits}")
    contradictions = [k for k, s in states.items() if s == "contradiction"]
    open_ = [k for k, s in states.items() if s == "open"] + missing
    d1 = "fail" if contradictions else ("incomplete" if open_ else "pass")
    ds: dict[str, dict[int, list]] = {}
    for c in classes():
        rec = last.get(key(c))
        d = rec["distqldpc"]["d"] if rec and "distqldpc" in rec else None
        ds.setdefault(f"{c['torus'][0]}x{c['torus'][1]}", {}).setdefault(c["k"], []).append(d)
    got = rejudge(ds)
    expected_t = next(p["expected"] for p in registered if p["id"] == "T")
    t = "pass" if got == expected_t else ("incomplete" if open_ and not contradictions else "fail")
    # a deployment problem (changed code or records, another DistQLDPC) makes the run invalid,
    # which is not the same as a refutation
    verdict = "invalid" if problems else "fail" if "fail" in (d1, t) else (
        "pass" if d1 == t == "pass" else "incomplete")  # fmt: skip
    return {"D1": d1, "T": t, "verdict": verdict, "per_torus": got,
            "contradictions": contradictions, "open": open_, "problems": problems,
            "classes": len(expected), "settled_at_24": sum(s == "24" for s in states.values()),
            "distqldpc_commits": commits,
            "seconds_max": max((last[k]["seconds"] for k in states), default=None)}  # fmt: skip


STUDY = Study(directory=HERE, question=question, predictions=predictions, execute=execute,
              decide=decide)  # fmt: skip

if __name__ == "__main__":
    main(STUDY)
