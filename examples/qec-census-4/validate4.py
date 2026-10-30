"""
Validation of census stage 4's instrument (fast4.py) on tori stage 3b/3c already computed, before
it runs on any stage 4 torus. It also measures what the stage 4 run will cost.

    python examples/qec-census-4/validate4.py run --workers 32    (resumable: skips done tori)
    python examples/qec-census-4/validate4.py compare

For each torus in TORI, fast4.frontier is run and its record appended to
validation/records.jsonl. `compare` checks it against stage 3b/3c's record of the same torus:
- **best:** every best connected and overall d that stage 3b/3c settled must be equal. One
  stage 3b/3c left unsettled must be at least its recorded d (stage 3d found 24 on the 9
  formerly incomplete tori).
- **classes:** every class both instruments finished must have the same d.
- **settling:** every entry must be settled (reported).
It reports, per torus, the time taken and the number of exact runs.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import resource
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "validation" / "records.jsonl"
S3 = [
    HERE.parent / "qec-census-3b" / "records.jsonl",
    HERE.parent / "qec-census-3c" / "records.jsonl",
]
TORI = [(2, 75), (3, 50), (5, 30), (6, 25), (10, 15), (3, 49), (7, 21), (2, 72), (4, 36),
        (3, 48), (2, 51), (3, 40), (2, 48), (3, 35), (5, 21), (8, 15)]  # fmt: skip
LIMIT = 3600


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def stage3() -> dict[tuple[int, int], dict]:
    out = {}
    for p in S3:
        for line in p.read_text().splitlines():
            r = json.loads(line)
            if r.get("job") == "torus":
                out[(r["l"], r["m"])] = r
    return out


def read(path: Path = OUT) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def run(workers: int) -> None:
    F = _load("qec_census_stage4_fast", HERE / "fast4.py")
    OUT.parent.mkdir(exist_ok=True)
    done = {(r["l"], r["m"]) for r in read()}
    for t in TORI:
        if t in done:
            continue
        rec = {"l": t[0], "m": t[1], "n": 2 * t[0] * t[1], "limit": LIMIT, "workers": workers}
        t0 = time.time()
        try:
            with F.opened(TORI):
                f = F.frontier(*t, workers=workers, limit=LIMIT, log=lambda s: print(s, flush=True))
            rec |= {"best": f["best"], "exact_runs": f["exact_runs"],
                    "exact_seconds": f["exact_seconds"], "bound_seconds": f["bound_seconds"],
                    "classes": len(f["classes"]),
                    "rows": [{k: r.get(k) for k in ("key", "k", "connected", "upper", "exact")}
                             for r in f["classes"] if "exact" in r]}  # fmt: skip
        except Exception:
            rec["error"] = traceback.format_exc()[-2000:]
        rec["seconds"] = round(time.time() - t0, 1)
        # the largest resident memory of any finished child (DistQLDPC, window.c), in MB
        rec["child_max_rss_mb"] = round(
            resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024
        )
        rec["by"] = {}
        for x in rec.get("rows", []):
            b = x["exact"].get("by") or x["exact"]["status"]
            rec["by"][b] = rec["by"].get(b, 0) + 1
        with OUT.open("a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        print(f"{t}: {rec['seconds']} s, {rec.get('exact_runs')} exact runs"
              f"{' ERROR' if 'error' in rec else ''}", flush=True)  # fmt: skip


def compare(path: Path = OUT) -> dict:
    old = stage3()
    report, problems = {}, []
    for r in read(path):
        t = (r["l"], r["m"])
        name = f"{t[0]}x{t[1]}"
        if "error" in r:
            problems.append(f"{name}: error")
            continue
        o = old[t]
        for label in ("connected", "all"):
            for k, v in o["best"][label].items():
                new = r["best"][label].get(k)
                if new is None:
                    problems.append(f"{name} {label} k={k}: missing")
                elif v["settled"] and new["d"] != v["d"]:
                    problems.append(f"{name} {label} k={k}: {new['d']} vs settled {v['d']}")
                elif not v["settled"] and v["d"] is not None and (new["d"] or 0) < v["d"]:
                    problems.append(f"{name} {label} k={k}: {new['d']} below {v['d']}")
            extra = set(r["best"][label]) - set(o["best"][label])
            if extra:
                problems.append(f"{name} {label}: new k's {sorted(extra)}")
        oldd = {json.dumps(x["key"]): x["exact"]["d"] for x in o["rows"]
                if (x.get("exact") or {}).get("status") == "complete"}  # fmt: skip
        both = agree = 0
        for x in r["rows"]:
            if x["exact"]["status"] == "complete" and json.dumps(x["key"]) in oldd:
                both += 1
                if x["exact"]["d"] == oldd[json.dumps(x["key"])]:
                    agree += 1
                else:
                    problems.append(f"{name}: class {x['key']} d {x['exact']['d']} vs "
                                    f"{oldd[json.dumps(x['key'])]}")  # fmt: skip
        unsettled = [k for k, v in r["best"]["connected"].items() if not v["settled"]]
        report[name] = {"seconds": r["seconds"], "exact_runs": r["exact_runs"],
                        "classes_both_exact": both, "agree": agree, "unsettled": unsettled,
                        "old_exact_seconds": o.get("exact_seconds")}  # fmt: skip
    return {"tori": len(report), "problems": problems, "report": report}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("run", "compare"))
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    if a.action == "run":
        run(a.workers)
    else:
        print(json.dumps(compare(), indent=1))


if __name__ == "__main__":
    main()
