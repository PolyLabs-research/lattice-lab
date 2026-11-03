"""
Census stage 4d: the classes stage 4 leaves unfinished at its registered 4-hour limit, rerun with
DistQLDPC's cluster engine and no practical limit, and stage 4's frontier entries settled.

    uv run --no-sync python examples/qec-census-4d/study.py register
    uv run --no-sync python examples/qec-census-4d/study.py run --workers 32
    uv run --no-sync python examples/qec-census-4d/study.py resume --workers 32  (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-4d

**Why.** Stage 4 (examples/qec-census-4, registered 2026-10-30) gives each class's exact search
4 hours (its LIMIT, a registered setting). A class at the limit keeps only DistQLDPC's lower
bound, and its frontier entry can stay a lower bound. Lifting the limit inside stage 4 would break
its registration (its part H: every record made by the registered code and settings). This study
reruns those classes instead, as stage 3d did for stage 3b/3c, and leaves stage 4's verdict as it
is.

**Registered before any class reached the limit.** At registration stage 4 had 92 of its 110 tori,
11,551 exact runs, every one complete; the longest took 12,845 s (a d = 28 class on 3 x 63). The
classes this study reruns are therefore not known when it is registered: they are selected by the
rule below, from stage 4's own files, as stage 4 writes them.

**The selection.** Every class that stage 4's registered run (its run_started entry, named in the
question as STAGE4_RUN) recorded with an exact status other than "complete":
- "timelimit": DistQLDPC reached the limit (or failed) and left a lower bound;
- "unverified": DistQLDPC gave an exact d, but no logical of that weight was found to check it.
It reads both stage 4 files: the torus records (examples/qec-census-4/records.jsonl) and the
checkpoint of exact results (exact-checkpoint.jsonl, lines with that run's hash), which has each
result within minutes of its run. A class's torus record, once written, decides its status.

**The job, per class.**
- "timelimit": DistQLDPC (env DISTQLDPC, at DISTQLDPC_COMMIT) with -engine=cc and a CPU limit of
  LIMIT, 14 days, which no class is expected to reach (a d = 30 class should take one to two
  days at stage 4's rate of about 7 times per +2 in d).
- "unverified": DistQLDPC is not run again; its d is stage 4's.
- Then a witness of weight d: window.c (kind Z) with seeds 0 and 1 for 600 s each, then seeds 2
  to 9 for 3,600 s each, stopping at the first logical of weight at most d; the lightest found is
  checked by distance.verify_witness.

**Polling.** While stage 4 runs, the run takes each newly selected class as soon as it appears
(the pod pulls the branch every two minutes), up to `workers` at once. It ends when stage 4's
ledger holds its verdict and every selected class has a record here, or at the stop rule: no
class is started more than STOP_DAYS after this run's run_started.

**The predictions.**
- **D1.** Every selected class is settled: an exact d (DistQLDPC's, exit 0) and a verified
  Z-logical of weight d. It fails if a verified logical is lighter than an exact d, or a d
  exceeds stage 4's verified window bound for that class; it is incomplete if a class lacks an
  exact d or a weight-d witness.
- **B.** Every exact d found here is even, at least stage 4's recorded lower bound rounded up to
  even, and at most stage 4's window bound for the class. It fails at the first exception.
- **R (reported, not judged).** Each torus with a selected class, its frontier entries amended
  with these d's (an unsettled entry rises to the largest d found and is settled when every
  selected class at its k is), and stage 4's judge_torus on the amended record.

The verdict: "not applicable" when no class is selected; "pass" when D1 and B pass; "fail" when
either fails; "incomplete" otherwise; "invalid" if the code, stage 4's run or DistQLDPC differ
from the registration. Stage 4's registered verdict is not changed; this study reports beside it.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
S4 = HERE.parent / "qec-census-4"
S3B = HERE.parent / "qec-census-3b"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s4 = _load("qec_census_stage4_study", S4 / "study.py")
distq = _load("spotcheck_distq", S3B / "spotcheck" / "distq.py")
parts = _load("qec_open_parts", HERE.parent / "qec-open-distance" / "parts.py")
distance = parts.distance

from lattice_lab.ledger import Ledger, record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-census-stage4d"
STAGE4_RUN = "ba38b6d91c6d1481cc6d368a335cf7a98872d228584b2636964d4ff19a7a092d"
DISTQLDPC_COMMIT = "8fe913e2ca79bda37cb755975b06b1b60416a418"  # stage 4's and stage 3d's
LIMIT = 14 * 86400  # CPU seconds per class: no practical limit
STOP_DAYS = 21
POLL = 60.0
UNFINISHED = ("timelimit", "unverified")
WINDOW_FIRST = ((0, 1), 600.0)
WINDOW_MORE = (tuple(range(2, 10)), 3600.0)
S4_RECORDS = S4 / "records.jsonl"
S4_CHECKPOINT = S4 / "exact-checkpoint.jsonl"
S4_LEDGER = S4 / "ledger.jsonl"
HASHED = {"study_py": HERE / "study.py", "tests_py": ROOT / "tests" / "test_qec_census_4d.py",
          "distq_py": S3B / "spotcheck" / "distq.py", "parts_py": parts.__file__,
          "window_c": parts.WINDOW_C, "distance_py": distance.__file__,
          "s4_study_py": S4 / "study.py"}  # fmt: skip


def code_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in HASHED.items()}


def even_up(x: int | None) -> int | None:
    return None if x is None else x + (x % 2)


def _lines(path: Path):
    """Whole JSON lines; a line cut short (a write in progress, or a stop) is skipped."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def key(c: dict) -> str:
    return f"{c['torus'][0]}x{c['torus'][1]}:{c['class_key']}"


def _d4(e: dict) -> int | None:
    """Stage 4's exact d for an 'unverified' class: DistQLDPC's, which fast4 also keeps as
    the class's lower bound."""
    if e.get("status") != "unverified":
        return None
    return (e.get("distqldpc") or {}).get("d") or e.get("lower")


_SELECTED: dict = {}


def selected() -> list[dict]:
    """The classes to rerun (module docstring, "The selection"), in a fixed order. Stage 4's
    files are read again only when they change."""
    stamp = (STAGE4_RUN, *((str(p), p.stat().st_mtime_ns, p.stat().st_size) if p.exists()
                           else (str(p), 0, 0) for p in (S4_CHECKPOINT, S4_RECORDS)))  # fmt: skip
    if _SELECTED.get("stamp") == stamp:
        return _SELECTED["rows"]
    out: dict[str, dict] = {}
    for c in _lines(S4_CHECKPOINT):
        e = c.get("exact") or {}
        if c.get("run") != STAGE4_RUN or e.get("status") not in UNFINISHED:
            continue
        item = {"torus": [c["l"], c["m"]], "n": 2 * c["l"] * c["m"], "k": None,
                "A": c["A"], "B": c["B"], "class_key": c["key"], "status": e["status"],
                "lower": e.get("lower"), "d4": _d4(e), "upper": None, "connected": None,
                "from": "checkpoint"}  # fmt: skip
        out[key(item)] = item
    for r in _lines(S4_RECORDS):
        if r.get("job") != "torus":
            continue
        for row in r.get("rows") or []:
            e = row.get("exact") or {}
            k = f"{r['l']}x{r['m']}:{json.dumps(row['key'])}"
            if e.get("status") not in UNFINISHED:
                out.pop(k, None)  # the torus record decides
                continue
            out[k] = {"torus": [r["l"], r["m"]], "n": r["n"], "k": row["k"], "A": row["A"],
                      "B": row["B"], "class_key": json.dumps(row["key"]), "status": e["status"],
                      "lower": e.get("lower"), "d4": _d4(e), "upper": row.get("upper"),
                      "connected": row.get("connected"), "from": "records"}  # fmt: skip
    rows = [out[k] for k in sorted(out)]
    _SELECTED.update(stamp=stamp, rows=rows)
    return rows


def stage4_ended() -> bool:
    entries = [e for e in _lines(S4_LEDGER)]
    return bool(entries) and entries[-1]["kind"] == "verdict"


def question() -> dict:
    return {"id": ID, "title": "Census stage 4d: the classes stage 4 leaves at its 4-hour limit, "
                               "rerun with DistQLDPC and no practical limit",
            "continues": ["examples/qec-census-4"], "stage4_run": STAGE4_RUN,
            "selection": "every class stage 4's registered run (stage4_run) records with exact "
                         "status 'timelimit' or 'unverified', from its torus records and its "
                         "checkpoint; a torus record, once written, decides a class's status",
            "known_at_registration": "no stage 4 class had reached the limit: 92 of 110 tori, "
                                     "11,551 exact runs, all complete, the longest 12,845 s "
                                     "(3x63, d = 28). d is even for this family "
                                     "(docs/code-census.md, Proved 6). Stage 4's rate is about "
                                     "7 times per +2 in d (its records), so a d = 30 class "
                                     "should take one to two days.",
            "seen_before": "nothing: no class has been selected, and this study's instrument "
                           "(DistQLDPC's cc engine at the commit below, window.c, "
                           "verify_witness) is stage 3d's, run on no stage 4 class",
            "distqldpc_commit": DISTQLDPC_COMMIT, "limit": LIMIT, "stop_days": STOP_DAYS,
            "window": {"first": WINDOW_FIRST, "more": WINDOW_MORE},
            "sha256": code_hashes()}  # fmt: skip


def predictions() -> list[dict]:
    return [{"id": "D1", "claim": "every selected class is settled: an exact d by DistQLDPC's cc "
                                  "engine (exit 0; stage 4's for an 'unverified' class) and a "
                                  "verified Z-logical of weight d",
             "fails_if": "a verified logical is lighter than an exact d, or a d exceeds stage "
                         "4's window bound for its class",
             "incomplete_if": "a selected class lacks an exact d or a weight-d witness"},
            {"id": "B", "claim": "every exact d is even, at least stage 4's recorded lower bound "
                                 "rounded up to even, and at most stage 4's window bound"},
            {"id": "R", "claim": "reported, not judged: each affected torus's amended "
                                 "frontier entries and stage 4's judge_torus on its amended "
                                 "record"}]  # fmt: skip


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
        return ["stage 4d is not registered"]
    problems = []
    if q["sha256"] != code_hashes():
        problems.append("the code differs from the registration")
    run4 = next((e["hash"] for e in _lines(S4_LEDGER) if e["kind"] == "run_started"), None)
    if run4 != STAGE4_RUN or q.get("stage4_run") != STAGE4_RUN:
        problems.append(f"stage 4's run is {run4}, registered {q.get('stage4_run')}")
    return problems


def witness(A, B, ell: int, m: int, d: int, schedule=None) -> dict:
    """window.c for a logical of weight at most d (module docstring); the lightest found. Each
    window runs its full time per seed; the schedule stops at the first that reaches d."""
    windows = []
    for seeds, seconds in schedule or (WINDOW_FIRST, WINDOW_MORE):
        w = parts.window(A, B, ell, m, "Z", seeds=seeds, seconds=seconds, workers=1)
        windows.append({k: w[k] for k in ("upper", "witness", "runs", "seconds")})
        if w["upper"] is not None and w["upper"] <= d:
            break
    best = min((w for w in windows if w["witness"]), key=lambda w: w["upper"], default=None)
    check = distance.verify_witness(A, B, ell, m, "Z", best["witness"]) if best else None
    return {"window": windows, "witness": best["witness"] if best else None,
            "witness_check": check}  # fmt: skip


def job(c: dict, limit: int = LIMIT, schedule=None) -> dict:
    """One class (module docstring, "The job")."""
    A, B = [tuple(t) for t in c["A"]], [tuple(t) for t in c["B"]]
    ell, m = c["torus"]
    t0 = time.time()
    out = {"key": key(c), "class": c, "study": ID, "sha256": code_hashes(),
           "pod": os.environ.get("RUNPOD_POD_ID")}  # fmt: skip
    try:
        if c["status"] == "unverified" and c.get("d4"):
            d = int(c["d4"])
            out["d_from"] = "stage 4"
        else:
            r = distq.run(A, B, ell, m, engine="cc", limit=int(limit))
            r["commit"] = distqldpc_commit()
            out["distqldpc"] = r
            d = r["d"] if r["returncode"] == 0 else None
            out["d_from"] = "DistQLDPC"
        out["d"] = d
        if d is not None:
            out |= witness(A, B, ell, m, d, schedule)
    except Exception:
        out["error"] = traceback.format_exc()[-2000:]
    out["seconds"] = round(time.time() - t0, 1)
    return out


RETRIES = 2  # a class whose job raised is tried this many times in all


def _done(path: Path) -> set[str]:
    """Classes finished here: a record without an error, or RETRIES records with one."""
    if not path.exists():
        return set()
    ok, errors = set(), {}
    for _, _, x in record_lines(path):
        r = json.loads(x)
        if "error" in r:
            errors[r["key"]] = errors.get(r["key"], 0) + 1
        else:
            ok.add(r["key"])
    return ok | {k for k, n in errors.items() if n >= RETRIES}


def _started_at() -> float | None:
    entries = Ledger(HERE / "ledger.jsonl").entries
    t = next((e["time"] for e in entries if e["kind"] == "run_started"), None)
    return None if t is None else dt.datetime.fromisoformat(t).timestamp()


def execute(path: Path, workers: int) -> None:
    problems = consistency()
    if problems:
        raise RuntimeError("; ".join(problems))
    if distqldpc_commit() != DISTQLDPC_COMMIT:
        raise RuntimeError(f"DistQLDPC at {distqldpc_commit()}, registered {DISTQLDPC_COMMIT}")
    started = _started_at() or time.time()
    deadline = started + STOP_DAYS * 86400
    running: dict = {}
    # a worker killed outright (out of memory) raises BrokenProcessPool here rather than hanging;
    # the pod script then resumes, which skips every class already recorded
    ctx = multiprocessing.get_context("fork")
    with ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as pool:
        while True:
            done = _done(path)
            todo = [c for c in selected() if key(c) not in done and key(c) not in running]
            if time.time() < deadline:
                for c in todo[: max(0, workers - len(running))]:
                    running[key(c)] = pool.submit(job, c)
                    print(f"started {key(c)} ({c['status']}, lower {c['lower']})", flush=True)
            for k in [k for k, f in running.items() if f.done()]:
                rec = running.pop(k).result()
                append_records(path, [rec])
                w = rec.get("witness_check") or {}
                print(f"{k}: d={rec.get('d')} witness={w.get('weight')}"
                      f"{' ERROR' if 'error' in rec else ''}", flush=True)  # fmt: skip
            waiting = [c for c in selected() if key(c) not in _done(path)]
            if not running and (time.time() >= deadline or (stage4_ended() and not waiting)):
                break
            time.sleep(POLL)


def assess(rec: dict | None, c: dict) -> str:
    """'settled', 'contradiction' or 'open' for one selected class."""
    if rec is None:
        return "open"
    d, w = rec.get("d"), rec.get("witness_check")
    r = rec.get("distqldpc") or {}
    lighter = w is not None and w["logical"] and d is not None and w["weight"] < d
    above = d is not None and c.get("upper") is not None and d > c["upper"]
    bounds = w is not None and w["logical"] and r.get("lower") is not None and \
        r["lower"] > w["weight"]  # fmt: skip
    if lighter or above or bounds:
        return "contradiction"
    if "error" in rec or d is None:
        return "open"
    if w and w["logical"] and w["weight"] == d:
        return "settled"
    return "open"


def in_bounds(d: int, c: dict) -> bool:
    lo = even_up(c.get("lower"))
    return d % 2 == 0 and (lo is None or d >= lo) and (c.get("upper") is None or d <= c["upper"])


def amended(rec: dict, ds: dict[int, list[int | None]]) -> dict:
    """Stage 4's torus record with each unsettled best entry raised to the largest d found here,
    and settled when every selected class at that k has one."""
    rec = copy.deepcopy(rec)
    for k, v in rec["best"]["connected"].items():
        got = ds.get(int(k))
        if not v["settled"] and got:
            known = [d for d in got if d is not None]
            if known:
                v["d"] = max([v["d"] or 0, *known])
            if len(known) == len(got):
                v.update(settled=True, unresolved=0)
    return rec


def report(sel: list[dict], last: dict[str, dict]) -> dict[str, dict]:
    """R: each affected torus's amended frontier and stage 4's judge_torus on it."""
    by_torus: dict[str, dict[int, list]] = {}
    for c in sel:
        if c.get("k") is None or not c.get("connected"):
            continue
        rec = last.get(key(c))
        d = rec.get("d") if rec and assess(rec, c) == "settled" else None
        name = f"{c['torus'][0]}x{c['torus'][1]}"
        by_torus.setdefault(name, {}).setdefault(c["k"], []).append(d)
    out = {}
    for r in _lines(S4_RECORDS):
        name = f"{r.get('l')}x{r.get('m')}"
        if r.get("job") != "torus" or name not in by_torus:
            continue
        a = amended(r, by_torus[name])
        j = s4.judge_torus(a)
        out[name] = {"best": {k: {"d": v["d"], "settled": v["settled"]} for k, v in
                              a["best"]["connected"].items()},
                     "judge": {p: j[p] for p in ("P0", "E", "S2", "G", "S1")}}  # fmt: skip
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    problems = consistency()
    # a class's record without an error counts over its failed attempts
    last: dict[str, dict] = {}
    for r in rows:
        if r["key"] not in last or "error" in last[r["key"]]:
            last[r["key"]] = r
    sel = selected()
    states = {key(c): assess(last.get(key(c)), c) for c in sel}
    commits = sorted({last[k]["distqldpc"].get("commit") for k in states
                      if k in last and "distqldpc" in last[k]}, key=str)  # fmt: skip
    if commits not in ([DISTQLDPC_COMMIT], []):
        problems.append(f"DistQLDPC commits {commits}")
    contradictions = [k for k, s in states.items() if s == "contradiction"]
    open_ = [k for k, s in states.items() if s == "open"]
    outside = [key(c) for c in sel if (last.get(key(c)) or {}).get("d") is not None
               and not in_bounds(last[key(c)]["d"], c)]  # fmt: skip
    if not sel:
        d1 = b = "not applicable"
    else:
        d1 = "fail" if contradictions else ("incomplete" if open_ else "pass")
        b = "fail" if outside else ("pass" if not open_ else "incomplete")
    verdict = "invalid" if problems else "not applicable" if not sel else \
        "fail" if "fail" in (d1, b) else "pass" if d1 == b == "pass" else "incomplete"  # fmt: skip
    return {"D1": d1, "B": b, "verdict": verdict, "selected": len(sel),
            "settled": sum(s == "settled" for s in states.values()),
            "contradictions": contradictions, "open": open_, "outside_bounds": outside,
            "R": report(sel, last), "problems": problems, "distqldpc_commits": commits,
            "stage4_ended": stage4_ended(),
            "seconds_max": max((last[k]["seconds"] for k in states if k in last),
                               default=None)}  # fmt: skip


STUDY = Study(directory=HERE, question=question, predictions=predictions, execute=execute,
              decide=decide)  # fmt: skip

if __name__ == "__main__":
    main(STUDY)
