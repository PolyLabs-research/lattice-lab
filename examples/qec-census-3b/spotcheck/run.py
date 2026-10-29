"""
The stage 3b/3c spot-check (docs/census-stage3b-spotcheck-plan.md): draw the sample from the
records, run checks C1-C6 on it, and judge the results.

    python examples/qec-census-3b/spotcheck/run.py sample            # print the sample
    python examples/qec-census-3b/spotcheck/run.py run --workers 16  # run (or resume) the jobs
    python examples/qec-census-3b/spotcheck/run.py judge             # tiers and agreement

**The sample** (`sample`) is computed from stage 3b's and stage 3c's records, in record order
(3b's file, then 3c's), over the judged tori (groups random and extrapolation) with codes. A
code's value is its own exact distance (exact.status "complete"), whether or not its torus's
frontier was settled. The d_max code of a torus is the first class in record order, at the
torus's smallest connected k, whose exact d is the torus's best connected d at that k. The plan
gives the rules; `sample` applies them in this order, and a code already drawn is not drawn again:

1. the d_max codes of the 6 largest-n tori (ties in n by record order);
2. the d_max codes of the P2 counterexamples, one per isomorphism class of the group
   Z_l x Z_m (the first such torus in record order), up to 4;
3. 6 codes drawn by random.Random(SEED).sample from the (torus, k) frontier entries with
   d >= 14, in record order and k order, whose code (the first complete class with that d) is
   not drawn yet;
4. (the amendment) the P3 counterexample codes [[294,10,20]] on 3 x 49 and 7 x 21, and the
   two highest-scoring extrapolation codes on 288 qubits, [[288,8,22]] on 3 x 48 and
   [[288,12,18]] on 4 x 36.

C6 also runs on the frontier codes with 12 <= d <= 16 on the 6 smallest judged tori with codes.

**The jobs** (`jobs`): each is one call of an instrument with one limit, run in its own process.
Results are appended to records.jsonl as each job ends, so `run` resumes where it stopped.
At most SCIP_CAP integer programs and SAT_CAP SAT claims run at once (memory and proof disk).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import multiprocessing
import multiprocessing.connection
import os
import platform
import random
import signal
import socket
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECORDS = [ROOT / "examples" / "qec-census-3b" / "records.jsonl",
           ROOT / "examples" / "qec-census-3c" / "records.jsonl"]  # fmt: skip
OUT = HERE / "records.jsonl"
SEED = "qec-census-3b spot-check"
P2_CONSTANT = 1.40
AMENDED = [((3, 49), 10, 20), ((7, 21), 10, 20), ((3, 48), 8, 22), ((4, 36), 12, 18)]

WINDOW_SEEDS, WINDOW_SECONDS = tuple(range(8)), 900.0
LIMITS = {"C1": 7200.0, "C2": 7200.0, "C3": 7200.0, "C5": 7200, "C6": 14400.0}
ORDER = ("C4", "C3", "C6", "C5", "C1", "C2")  # the plan's order when time is short
SCIP_CAP, SAT_CAP = 6, 3
RETRIES = 2


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _instruments():
    """The instrument modules, loaded on first use (so `sample` needs none of them)."""
    pack = _load("qec_open_distance_2_pack", ROOT / "examples" / "qec-open-distance-2" / "pack.py")
    sat = _load("spotcheck_sat", HERE / "sat.py")
    distq = _load("spotcheck_distq", HERE / "distq.py")
    return pack, sat, distq


# ---------------------------------------------------------------------------------- the sample


def records() -> list[dict]:
    out = []
    for path in RECORDS:
        out += [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return out


def judged(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("job") == "torus" and "error" not in r
            and r["group"] in ("random", "extrapolation") and r["classes"] > 0]  # fmt: skip


def _best(rec: dict) -> dict[int, dict]:
    return {int(k): v for k, v in rec["best"]["connected"].items() if v["d"] is not None}


def _first_code(rec: dict, k: int, d: int) -> dict | None:
    """The first connected class in record order with this k and exact (complete) distance d."""
    for row in rec["rows"]:
        e = row.get("exact") or {}
        if row["connected"] and row["k"] == k and e.get("status") == "complete" and e["d"] == d:
            return row
    return None


def _code(rec: dict, row: dict, why: str) -> dict:
    return {"torus": [rec["l"], rec["m"]], "n": rec["n"], "k": row["k"], "d": row["exact"]["d"],
            "A": row["A"], "B": row["B"], "witness": row["exact"]["witness"],
            "group": rec["group"], "why": why}  # fmt: skip


def _name(c: dict) -> str:
    return f"{c['torus'][0]}x{c['torus'][1]}:[[{c['n']},{c['k']},{c['d']}]]:{c['A']}:{c['B']}"


def d_max_code(rec: dict, why: str) -> dict | None:
    best = _best(rec)
    if not best:
        return None
    k = min(best)
    row = _first_code(rec, k, best[k]["d"])
    return _code(rec, row, why) if row else None


def iso(ell: int, m: int) -> tuple[int, int]:
    """Z_l x Z_m is isomorphic to Z_g x Z_(lm/g), g = gcd(l, m): its invariant factors."""
    g = math.gcd(ell, m)
    return g, ell * m // g


def sample(rows: list[dict] | None = None) -> dict:
    """The codes the checks run on (module docstring): {"codes": [...], "c6_extra": [...]}."""
    tori = judged(records() if rows is None else rows)
    codes: list[dict] = []
    seen: set[str] = set()

    def add(c):
        if c is not None and _name(c) not in seen:
            seen.add(_name(c))
            codes.append(c)

    order = {id(r): i for i, r in enumerate(tori)}
    for r in sorted(tori, key=lambda r: (-r["n"], order[id(r)]))[:6]:
        add(d_max_code(r, "largest n"))
    p2, groups = [], set()
    for r in tori:
        best = _best(r)
        cap = 2 * math.floor(P2_CONSTANT * math.sqrt(r["n"]) / 2)
        if best and max(v["d"] for v in best.values()) > cap and iso(r["l"], r["m"]) not in groups:
            groups.add(iso(r["l"], r["m"]))
            p2.append(r)
    for r in p2[:4]:
        add(d_max_code(r, "P2 counterexample"))
    entries = []
    for r in tori:
        for k, v in sorted(_best(r).items()):
            if v["d"] >= 14:
                row = _first_code(r, k, v["d"])
                if row is not None:
                    entries.append(_code(r, row, "random frontier entry"))
    entries = [c for c in entries if _name(c) not in seen]
    for c in random.Random(SEED).sample(entries, min(6, len(entries))):
        add(c)
    by_torus = {(r["l"], r["m"]): r for r in tori}
    for torus, k, d in AMENDED:
        r = by_torus[torus]
        row = _first_code(r, k, d)
        if row is None:
            raise RuntimeError(f"no complete class [[{r['n']},{k},{d}]] on {torus}")
        add(_code(r, row, "amendment: P3 / top extrapolation score"))
    extra = []
    for r in sorted(tori, key=lambda r: (r["n"], order[id(r)]))[:6]:
        for k, v in sorted(_best(r).items()):
            if 12 <= v["d"] <= 16:
                row = _first_code(r, k, v["d"])
                if row is not None:
                    c = _code(r, row, "C6: smallest tori")
                    if _name(c) not in seen:
                        extra.append(c)
    return {"codes": codes, "c6_extra": extra}


# ---------------------------------------------------------------------------------- the jobs


def jobs(s: dict) -> list[dict]:
    """Every job, in the plan's order of priority (ORDER), then sample order."""
    out = []
    for c in s["codes"]:
        for kind in ("Z", "X"):
            for seed in WINDOW_SEEDS:
                out.append({"check": "C4", "code": c, "kind": kind, "seed": seed})
        out.append({"check": "C3", "code": c})
        if c["d"] <= 16:
            out.append({"check": "C6", "code": c})
        out.append({"check": "C5", "code": c, "engine": "cc"})
        out.append({"check": "C5", "code": c, "engine": "maxsat"})
        out.append({"check": "C1", "code": c})
        out.append({"check": "C2", "code": c})
    out += [{"check": "C6", "code": c} for c in s["c6_extra"]]
    for j in out:
        j["key"] = key(j)
    return sorted(out, key=lambda j: ORDER.index(j["check"]))


def key(j: dict) -> str:
    extra = "".join(f":{t}={j[t]}" for t in ("kind", "seed", "engine") if t in j)
    return f"{j['check']}:{_name(j['code'])}{extra}"


def _ab(c):
    return [tuple(t) for t in c["A"]], [tuple(t) for t in c["B"]]


def execute(j: dict) -> dict:
    """Run one job; returns its record (the job, the result, the time, and the machine)."""
    pack, sat, distq = _instruments()
    c = j["code"]
    A, B = _ab(c)
    ell, m = c["torus"]
    lm = ell * m
    t0 = time.time()
    try:
        if j["check"] == "C4":
            r = pack.plain.window(A, B, ell, m, j["kind"], seeds=(j["seed"],),
                                  seconds=WINDOW_SECONDS, workers=1)  # fmt: skip
        elif j["check"] == "C3":
            r = pack.search(A, B, ell, m, "X", anchors=(0, lm), parts=1, workers=1,
                            time_limit=LIMITS["C3"])  # fmt: skip
        elif j["check"] == "C2":
            r = pack.reference(A, B, ell, m, "Z", anchors=None, parts=1, workers=1,
                               time_limit=LIMITS["C2"])  # fmt: skip
        elif j["check"] == "C1":
            r = pack.distance.distance_ilp(A, B, ell, m, "Z", time_limit=LIMITS["C1"])
            if r["k"] != c["k"]:
                raise RuntimeError(f"distance_ilp found {r['k']} logicals, k = {c['k']}")
            if r.get("witness") is not None:
                r["witness_check"] = pack.distance.verify_witness(A, B, ell, m, "Z", r["witness"])
        elif j["check"] == "C5":
            r = distq.run(A, B, ell, m, engine=j["engine"], limit=LIMITS["C5"])
            r["distqldpc_commit"] = _git_head(distq.DISTQ)
        elif j["check"] == "C6":
            D = pack.distance
            hx, hz = D._bit_rows(A, B, ell, m)
            logicals = D._logicals_bits(hz, hx, 2 * lm)  # X-logicals
            if len(logicals) != c["k"]:
                raise RuntimeError(f"{len(logicals)} X-logicals, k = {c['k']}")
            r = sat.certify(hx, logicals, 2 * lm, c["d"] - 1, anchors=(0, lm),
                            limit=LIMITS["C6"])  # fmt: skip
            if r.get("support") is not None:
                r["support_check"] = D.verify_witness(A, B, ell, m, "Z", r["support"])
            r["witness_check"] = D.verify_witness(A, B, ell, m, "Z", c["witness"])
        else:
            raise ValueError(j["check"])
        r = {k: v for k, v in r.items() if k != "passes"} | (
            {"passes": len(r["passes"])} if "passes" in r else {})  # fmt: skip
        out = {"result": _plain(r)}
    except Exception:
        out = {"error": traceback.format_exc()[-2000:]}
    return {"key": j["key"], **{k: v for k, v in j.items() if k != "key"}, **out,
            "seconds": round(time.time() - t0, 1), "host": socket.gethostname(),
            "pod": os.environ.get("RUNPOD_POD_ID"), "sha256": code_hashes(),
            "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}  # fmt: skip


def _plain(x):
    """JSON-safe: tuples to lists, numpy scalars to Python numbers."""
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [_plain(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, str | bytes):
        x = x.item()
    if isinstance(x, float) and not math.isfinite(x):
        return None  # SCIP's dual bound before any bound is known
    return x


def _git_head(path: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()  # fmt: skip
    except Exception:
        return None


def code_hashes() -> dict[str, str]:
    files = {"run_py": HERE / "run.py", "sat_py": HERE / "sat.py", "distq_py": HERE / "distq.py"}
    return {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in files.items()}


def read(path: Path = OUT) -> list[dict]:
    """The records in `path`; a last line cut short (a write interrupted) is skipped."""
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def done_keys(path: Path = OUT) -> set[str]:
    return {r["key"] for r in read(path)}


def capped(j: dict, running: list[dict]) -> bool:
    count = lambda c: sum(r["check"] == c for r in running)  # noqa: E731
    return (j["check"] == "C1" and count("C1") >= SCIP_CAP) or \
        (j["check"] == "C6" and count("C6") >= SAT_CAP)  # fmt: skip


def _child(j: dict, out: str) -> None:
    os.setsid()  # its own process group, so the tools it starts can be killed with it
    tmp = Path(out + ".part")
    tmp.write_text(json.dumps(execute(j), sort_keys=True))
    tmp.rename(out)  # the result appears whole or not at all


def _kill_group(proc) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run(workers: int, path: Path = OUT, retries: int = RETRIES) -> None:
    """Run the jobs not yet in `path`, at most `workers` at once, each in a process of its own
    (forked), so a job that dies (out of memory, say) takes no other job with it. A job whose
    process dies without a result is run again, up to `retries` times, then recorded as an
    error."""
    todo = [j for j in jobs(sample()) if j["key"] not in done_keys(path)]
    print(f"{len(todo)} jobs to run, {workers} at once", flush=True)
    ctx = multiprocessing.get_context("fork")
    running: dict = {}  # sentinel -> (process, result file, job)
    deaths: dict[str, int] = {}

    def stop(signum, frame):  # a pod stop: end every job's process group, then exit
        for proc, _, _ in running.values():
            _kill_group(proc)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, stop)
    with tempfile.TemporaryDirectory(prefix="spotcheck-run-") as tmp:
        while todo or running:
            while len(running) < workers:
                nxt = next((j for j in todo if not capped(j, [x[2] for x in running.values()])),
                           None)  # fmt: skip
                if nxt is None:
                    break
                todo.remove(nxt)
                out = Path(tmp) / f"{len(deaths)}-{time.time_ns()}.json"
                proc = ctx.Process(target=_child, args=(nxt, str(out)), daemon=True)
                proc.start()
                running[proc.sentinel] = (proc, out, nxt)
                print(f"start {nxt['key']}", flush=True)
            for s in multiprocessing.connection.wait(list(running)):
                proc, out, j = running.pop(s)
                proc.join()
                _kill_group(proc)  # anything the job left running
                rec = None
                if out.exists():
                    try:
                        rec = json.loads(out.read_text())
                    except (OSError, json.JSONDecodeError):
                        rec = None
                    out.unlink(missing_ok=True)
                if rec is None:
                    deaths[j["key"]] = deaths.get(j["key"], 0) + 1
                    print(f"died  {j['key']} (exit {proc.exitcode})", flush=True)
                    if deaths[j["key"]] <= retries:
                        todo.append(j)
                        continue
                    rec = {"key": j["key"], **{k: v for k, v in j.items() if k != "key"},
                           "error": f"the job's process died {deaths[j['key']]} times "
                                    f"(last exit code {proc.exitcode})"}  # fmt: skip
                with path.open("a") as fh:
                    fh.write(json.dumps(rec, sort_keys=True) + "\n")
                print(f"done  {j['key']} ({'error' if 'error' in rec else 'ok'})", flush=True)


# ---------------------------------------------------------------------------------- judging


def assess(rec: dict) -> dict:
    """One job's result against the code's d: consistent (True/False), and what it reaches:
    'exact' (it found the same d), 'certified' (C6), or None (no conclusion)."""
    if "error" in rec:
        return {"consistent": None, "reaches": None, "note": "error"}
    d, r, check = rec["code"]["d"], rec["result"], rec["check"]
    if check == "C4":
        ok = r["upper"] is None or r["upper"] >= d
        return {"consistent": ok, "reaches": None}
    if check in ("C2", "C3"):
        if r["status"] == "complete":
            return {"consistent": r["d"] == d, "reaches": "exact" if r["d"] == d else None}
        return {"consistent": r["lower"] is None or r["lower"] <= d, "reaches": None}
    if check == "C1":
        if r["status"] in ("infeasible", "unbounded", "inforunbd"):
            # the program is feasible (the census's witness satisfies it): a wrong conclusion
            return {"consistent": False, "reaches": None, "note": r["status"]}
        upper = r["upper"]
        if upper is not None and not r["witness_check"]["logical"]:
            return {"consistent": None, "reaches": None, "note": "SCIP's solution is no logical"}
        ok = (r["lower"] is None or r["lower"] <= d) and (upper is None or upper >= d)
        if r["status"] == "optimal":
            ok = ok and r["d"] == d
            return {"consistent": ok, "reaches": "exact" if ok else None}
        return {"consistent": ok, "reaches": None}
    if check == "C5":
        ok = (r["lower"] is None or r["lower"] <= d) and (r["upper"] is None or r["upper"] >= d)
        if r["d"] is not None:
            ok = ok and r["d"] == d
            return {"consistent": ok, "reaches": "exact" if ok else None}
        return {"consistent": ok, "reaches": None}
    if check == "C6":
        witness = rec["result"]["witness_check"]
        good_witness = witness["logical"] and witness["weight"] == d
        if not good_witness:
            return {"consistent": False, "reaches": None, "note": "the census's witness fails"}
        if r["status"] == "sat":
            if r["support_check"]["logical"]:
                return {"consistent": False, "reaches": None, "note": "a lighter logical"}
            # an encoding fault, not evidence about d: no conclusion, flagged
            return {"consistent": None, "reaches": None, "note": "a SAT model that is no logical"}
        if r["status"] == "verified":
            return {"consistent": True, "reaches": "certified"}
        # a time limit, or a proof drat-trim did not verify: no conclusion either way
        return {"consistent": None, "reaches": None, "note": r["status"]}
    raise ValueError(check)


TIERS = ("certified", "second method", "second implementation", "search only")


def tier(recs: list[dict]) -> str:
    reached = {(r["check"], r.get("engine")) for r in recs if assess(r)["reaches"]}
    if ("C6", None) in reached:
        return "certified"
    if ("C1", None) in reached or ("C5", "maxsat") in reached:
        return "second method"
    if ("C5", "cc") in reached or ("C2", None) in reached:
        return "second implementation"
    return "search only"


def judge(path: Path = OUT) -> dict:
    """Agreement holds only when every expected job has a record, none errored, and none
    contradicts d. Records outside the job list are ignored; a key's last record counts."""
    expected = {j["key"] for j in jobs(sample())}
    last = {r["key"]: r for r in read(path) if r["key"] in expected}
    recs = list(last.values())
    by_code: dict[str, list[dict]] = {}
    for r in recs:
        by_code.setdefault(_name(r["code"]), []).append(r)
    contradictions = [r["key"] for r in recs if assess(r)["consistent"] is False]
    errors = [r["key"] for r in recs if "error" in r]
    finished = {c: sum(assess(r)["reaches"] is not None for r in recs if r["check"] == c)
                for c in ("C1", "C2", "C3", "C5", "C6")}  # fmt: skip
    notes = {r["key"]: assess(r)["note"] for r in recs if assess(r).get("note")}
    done = len(recs)
    return {"jobs": len(expected), "done": done,
            "agreement": not contradictions and not errors and done == len(expected),
            "contradictions": contradictions, "errors": errors, "notes": notes,
            "reached_d": finished,
            "tiers": {name: tier(rs) for name, rs in by_code.items()}}  # fmt: skip


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    p.add_argument("action", choices=("sample", "run", "judge"))
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    p.add_argument("--out", type=Path, default=OUT, help="the records file (default: %(default)s)")
    a = p.parse_args()
    if a.action == "sample":
        s = sample()
        for c in s["codes"]:
            print(f"{c['why']:42s} {_name(c)}")
        print(f"C6 extra: {len(s['c6_extra'])} codes")
        for c in s["c6_extra"]:
            print(f"{'':42s} {_name(c)}")
        print(f"{len(jobs(s))} jobs on {platform.node()}")
    elif a.action == "run":
        run(a.workers, a.out)
    else:
        print(json.dumps(judge(a.out), indent=2))


if __name__ == "__main__":
    main()
