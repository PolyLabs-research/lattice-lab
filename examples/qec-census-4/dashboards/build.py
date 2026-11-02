"""
The data layer of the census dashboards: it reduces the census's records (stages 3a to 4, the
checks and the study ledgers, about 110 MB) to small datasets, one JSON file of row objects each,
for the dashboard pages (`docs/census-dashboards-plan.md`).

    python examples/qec-census-4/dashboards/build.py            (writes dashboards/data/*.json)
    python examples/qec-census-4/dashboards/build.py --check    (builds and checks, writes nothing)

Every dataset is a snapshot: `summary` names the commit it read and when. `check()` reconciles
the datasets with the records before anything is written (see tests/test_census_dashboards.py).

Words used in the columns:
- **torus** "lxm": the group Z_l x Z_m, n = 2lm qubits. Isomorphic tori (the same invariant
  factors g = gcd(l, m) and lm / g) carry the same codes; `primary` marks one of each.
- **frontier entry**: for one torus and one k, the largest d of a connected code (a code whose
  stencil generates the torus), as the census settled it.
- **stage**: "3a" (every class, exact, lm <= 100), "3b/3c" (the held-out tori, lm <= 150, with
  stage 3d settling its unfinished classes), "4" (150 < lm <= 200, running).
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import importlib.util
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EX = ROOT / "examples"
OUT = HERE / "data"

S3A = sorted(glob.glob(str(EX / "qec-census-3" / "data" / "*.jsonl")))
S3B = EX / "qec-census-3b" / "records.jsonl"
S3C = EX / "qec-census-3c" / "records.jsonl"
S3D = EX / "qec-census-3d" / "records.jsonl"
S4 = EX / "qec-census-4" / "records.jsonl"
SPOT = EX / "qec-census-3b" / "spotcheck" / "records.jsonl"
SPOT_JUDGE = EX / "qec-census-3b" / "spotcheck" / "judge.json"
CHECK310 = [EX / "qec-census-4" / "check-310" / "records.jsonl",
            EX / "qec-census-4" / "check-310" / "records-long.jsonl"]  # fmt: skip
CODES = EX / "qec-bb" / "codes.json"

# Stage 4's tori (study.tori(), restated here; the tests compare the two) and its exposed tori
S4_EXPOSED = {(6, 30), (11, 14), (12, 13), (13, 13), (13, 14), (14, 14)}
S4_TORI = sorted(((ell, m) for ell in range(2, 15) for m in range(ell, 101)
                  if 150 < ell * m <= 200), key=lambda t: (t[0] * t[1], t))  # fmt: skip
STOP_DAYS = 14

# The registered laws (their study and part) and the exploratory fits of the regularity
# analysis (examples/qec-census-4/regularity/README.md)
P2_C = 1.4  # stage 3b/3c P2: d <= largest even <= 1.4 sqrt(n)
P3_LIMIT = {"random": 12.0, "extrapolation": 13.5}  # stage 3b/3c P3
E_C, E_B = 0.8011, 0.6074  # stage 4 E: d <= largest even <= 0.8011 n^0.6074
G_RECORD, S_RECORD, S_CEILING = 1.4606, 13.6054, 17.0  # stage 4 G, S1, S2
EDGE_C = 0.617  # top edge: 2 floor(0.617 sqrt(n ln n) / 2)
POWER_A, POWER_B = 0.78, 0.613
AFFINE_A, AFFINE_B = 1.75, -4.6
LAYER_A, LAYER_B = 2.31, 0.443  # k layers: 2.31 n^0.443 - k

E_DIVISORS = (3, 7, 31, 85, 73)  # criterion E for lm <= 200, in the order of the k they set
TIER_ORDER = ("certified", "second method", "second implementation", "search only")
ENGINE = {None: "packing search", "small": "small weight", "small_weight": "small weight",
          "distqldpc-cc": "DistQLDPC cluster", "cc": "DistQLDPC cluster"}  # fmt: skip


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rel(p) -> str:
    return str(Path(p).resolve().relative_to(ROOT))


def even_down(x: float) -> int:
    f = math.floor(x)
    return f - (f % 2)


def edge(n: int) -> int:
    return 2 * math.floor(EDGE_C * math.sqrt(n * math.log(n)) / 2)


def layer(n: int, k: int) -> float:
    return LAYER_A * n**LAYER_B - k


def ord2(t: int) -> int:
    x, e = 2 % t, 1
    while x != 1:
        x, e = (x * 2) % t, e + 1
    return e


def group_info(ell: int, m: int) -> dict:
    g = math.gcd(ell, m)
    h = ell * m // g
    if g == 1:
        name, gtype = f"Z{h}", "cyclic"
    else:
        name = f"Z{g}×Z{h}"
        gtype = "Z3×Z3 part" if g % 3 == 0 else "non-cyclic"
    divs = [t for t in E_DIVISORS if (ell * m) % t == 0]
    return {"g": g, "iso_key": f"{g}x{h}", "group_name": name, "group_type": gtype,
            "e_divisors": ",".join(map(str, divs)), "e_first": divs[0] if divs else None,
            "k_top_theory": 2 * ord2(divs[0]) if divs else None}  # fmt: skip


def poly_text(P) -> str:
    """A monomial (i, j) is x^i y^j, as in Bravyi et al. (x shifts the l direction)."""
    out = []
    for i, j in P:
        t = ("x" if i else "") + (f"^{i}" if i > 1 else "") + \
            ("y" if j else "") + (f"^{j}" if j > 1 else "")  # fmt: skip
        out.append(t or "1")
    return " + ".join(out)


def _read_jsonl(path: Path):
    with open(path) as fh:
        for i, line in enumerate(fh, 1):
            if line.strip():
                yield i, json.loads(line)


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                          check=True).stdout.strip()  # fmt: skip


def _quantile(xs: list[float], q: float) -> float:
    xs = sorted(xs)
    if len(xs) == 1:
        return xs[0]
    pos = q * (len(xs) - 1)
    lo = math.floor(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


# --------------------------------------------------------------------------------------------
# reading the records


class Census:
    """Every torus the census has computed, with its frontier, class distribution and runs."""

    def __init__(self) -> None:
        self.tori: dict[tuple[int, int], dict] = {}
        self.frontier: list[dict] = []
        self.hist: Counter = Counter()  # (torus, stage, k, connected, kind, value) -> classes
        self.weight: Counter = Counter()  # the same key -> sum of class sizes (stage 3a)
        self.runs: defaultdict = defaultdict(list)  # (stage, engine, d or None) -> seconds
        self.timelimits: Counter = Counter()  # (stage, engine) -> runs that hit the limit
        self.s3d = self._stage3d()
        self._stage3a()
        for path, stage in ((S3B, "3b/3c"), (S3C, "3b/3c"), (S4, "4")):
            self._records(path, stage)

    # stage 3d: the 154 unfinished classes of stage 3b/3c's 9 incomplete tori
    @staticmethod
    def _stage3d() -> dict:
        out = {}
        for line, r in _read_jsonl(S3D):
            c = r["class"]
            key = (tuple(c["torus"]), c["k"], json.dumps(c["A"]), json.dumps(c["B"]))
            out[key] = {"d": r["distqldpc"]["d"], "witness": r["witness"], "line": line,
                        "seconds": r["seconds"], "ok": r["witness_check"]["logical"]
                        and r["witness_check"]["weight"] == r["distqldpc"]["d"]}  # fmt: skip
        return out

    def _torus(self, ell: int, m: int, stage: str, **kw) -> dict:
        t = {"torus": f"{ell}x{m}", "l": ell, "m": m, "n": 2 * ell * m, "lm": ell * m,
             "stage": stage, **group_info(ell, m), **kw}  # fmt: skip
        if (ell, m) in self.tori:
            raise ValueError(f"torus {ell}x{m} recorded twice")
        self.tori[(ell, m)] = t
        return t

    def _entry(self, t: dict, k: int, d: int, settled: bool, row: dict | None, line: int,
               settled_by: str, witness, instrument: str, source: str) -> None:  # fmt: skip
        n = t["n"]
        self.frontier.append({
            "id": f"{t['torus']}-k{k}", "code": f"[[{n},{k},{d}]]", "torus": t["torus"],
            "l": t["l"], "m": t["m"], "n": n,
            "k": k, "d": d, "settled": settled, "settled_by": settled_by, "stage": t["stage"],
            "study_group": t["study_group"], "exposed": t["exposed"],
            "g": t["g"], "iso_key": t["iso_key"], "group_name": t["group_name"],
            "group_type": t["group_type"],
            "score": round(k * d * d / n, 4), "ratio": round(d / math.sqrt(n), 4),
            "A": json.dumps(row["A"]) if row else None, "B": json.dumps(row["B"]) if row else None,
            "A_text": poly_text(row["A"]) if row else None,
            "B_text": poly_text(row["B"]) if row else None,
            "witness": json.dumps(witness) if witness else None,
            "edge": edge(n), "resid_edge": d - edge(n),
            "layer": round(layer(n, k), 2), "resid_layer": round(d - layer(n, k), 2),
            "cap_p2": even_down(P2_C * math.sqrt(n)), "cap_e": even_down(E_C * n**E_B),
            "source_file": source, "source_line": line, "instrument": instrument,
        })  # fmt: skip

    def _stage3a(self) -> None:
        for p in S3A:
            lines = list(_read_jsonl(Path(p)))
            _, head = lines[0]
            ell, m = head["l"], head["m"]
            t = self._torus(ell, m, "3a", study_group="stage 1", exposed=False,
                            classes=head["classes"], orbit_reps=None,
                            exact_runs=head["classes"], exact_seconds=head["distance_seconds"],
                            bound_seconds=None, classes_seconds=head["classes_seconds"],
                            criterion_e=head["classes"] > 0, source_file=rel(p), source_line=1,
                            instrument="census3.py " + head["census3_py_sha256"][:8]
                            + " + search_pack.c " + head["search_pack_c_sha256"][:8])  # fmt: skip
            best: dict[int, tuple[int, dict]] = {}
            for line, r in lines[1:]:
                key = (t["torus"], "3a", r["k"], r["connected"])
                if r["status"] == "complete":
                    self.hist[(*key, "exact", r["d"])] += 1
                    self.weight[(*key, "exact", r["d"])] += r["size"]
                    self.runs[("3a", "packing search", r["d"])].append(r["seconds"])
                    if r["connected"] and (r["k"] not in best or r["d"] > best[r["k"]][1]["d"]):
                        best[r["k"]] = (line, r)
                else:
                    self.timelimits[("3a", "packing search")] += 1
            for k, (line, r) in sorted(best.items()):
                self._entry(t, k, r["d"], True, r, line, "packing search", r["witness"],
                            t["instrument"], t["source_file"])  # fmt: skip
            self._summarise(t)

    def _records(self, path: Path, stage: str) -> None:
        for line, r in _read_jsonl(path):
            if r.get("job") != "torus":
                continue
            ell, m = r["l"], r["m"]
            group = r.get("group")
            if stage == "4":
                instrument = (f"fast4.py {r['sha256']['fast4_py'][:8]} + DistQLDPC "
                              f"{r['distqldpc_commit'][:8]}")  # fmt: skip
            else:
                instrument = f"fast.py {r['sha256']['fast_py'][:8]} + search_pack.c " \
                             f"{r['sha256']['search_pack_c'][:8]}"  # fmt: skip
            t = self._torus(ell, m, stage, study_group=group, exposed=group == "exposed",
                            classes=r["classes"], orbit_reps=r["orbit_reps"],
                            exact_runs=r["exact_runs"], exact_seconds=r["exact_seconds"],
                            bound_seconds=r["bound_seconds"],
                            classes_seconds=r["classes_seconds"], criterion_e=r["criterion_e"],
                            source_file=rel(path), source_line=line, instrument=instrument,
                            error="error" in r, class_errors=r.get("class_errors", 0))  # fmt: skip
            if "error" in r:
                self._summarise(t)
                continue
            rows = r.get("rows") or []
            s3d_hit: dict[int, list[dict]] = defaultdict(list)
            for y in rows:
                key = (t["torus"], stage, y["k"], y["connected"])
                if y.get("upper") is not None:
                    self.hist[(*key, "window", y["upper"])] += 1
                e = y.get("exact")
                if not e:
                    continue
                engine = ENGINE[e.get("engine") or e.get("method")]
                if e["status"] == "complete":
                    self.hist[(*key, "exact", e["d"])] += 1
                    self.runs[(stage, engine, e["d"])].append(e["seconds"])
                    continue
                self.timelimits[(stage, engine)] += 1
                hit = self.s3d.get(((ell, m), y["k"], json.dumps(y["A"]), json.dumps(y["B"])))
                if hit:
                    self.hist[(*key, "exact", hit["d"])] += 1
                    self.runs[("3d", "DistQLDPC cluster", hit["d"])].append(hit["seconds"])
                    if y["connected"]:
                        s3d_hit[y["k"]].append({**hit, "row": y})
            for ks, v in sorted(r["best"]["connected"].items(), key=lambda kv: int(kv[0])):
                k, d, settled = int(ks), v["d"], v["settled"]
                settled_by = "packing search" if stage != "4" else "DistQLDPC cluster"
                row = None
                witness = None
                if not settled and s3d_hit.get(k):
                    best3d = max(s3d_hit[k], key=lambda h: h["d"])
                    if all(h["ok"] for h in s3d_hit[k]) and (d is None or best3d["d"] >= d):
                        d, settled, settled_by = best3d["d"], True, "stage 3d (DistQLDPC)"
                        row, witness = best3d["row"], best3d["witness"]
                if d is None:
                    continue
                if row is None:
                    row = next((y for y in rows if y["connected"] and y["k"] == k
                                and (y.get("exact") or {}).get("status") == "complete"
                                and y["exact"]["d"] == d), None)  # fmt: skip
                    if row is not None:
                        witness = row["exact"]["witness"]
                        eng = ENGINE[row["exact"].get("engine") or row["exact"].get("method")]
                        if eng == "small weight":
                            settled_by = "small weight"
                self._entry(t, k, d, settled, row, line, settled_by, witness, instrument,
                            t["source_file"])  # fmt: skip
            self._summarise(t)

    def _summarise(self, t: dict) -> None:
        mine = [e for e in self.frontier if e["torus"] == t["torus"]]
        t["k_values"] = ",".join(str(e["k"]) for e in sorted(mine, key=lambda e: e["k"]))
        t["d_max"] = max((e["d"] for e in mine), default=None)
        t["best_score"] = max((e["score"] for e in mine), default=None)
        t["best_ratio"] = max((e["ratio"] for e in mine), default=None)
        t["frontier_entries"] = len(mine)
        if t.get("error"):
            t["status"] = "error"
        elif t["classes"] == 0:
            t["status"] = "no codes"
        else:
            t["status"] = "settled" if all(e["settled"] for e in mine) else "unsettled"


# --------------------------------------------------------------------------------------------
# the datasets


def tiers() -> dict[tuple[str, int, int], dict]:
    """(torus, k, d) -> the strongest tier any check gave a code at that entry, and its source."""
    run = _load("qec_census_3b_spotcheck_run", EX / "qec-census-3b" / "spotcheck" / "run.py")
    out: dict[tuple[str, int, int], dict] = {}

    def put(key, tier, source):
        old = out.get(key)
        if old is None or TIER_ORDER.index(tier) < TIER_ORDER.index(old["tier"]):
            out[key] = {"tier": tier, "source": source}

    pat = re.compile(r"^(\d+x\d+):\[\[(\d+),(\d+),(\d+)\]\]")
    for name, tier in json.loads(SPOT_JUDGE.read_text())["tiers"].items():
        torus, _, k, d = pat.match(name).groups()
        put((torus, int(k), int(d)), tier, "spot-check of stage 3b/3c")
    recs = [r for p in CHECK310 if p.exists() for _, r in _read_jsonl(p)]
    if recs:
        c = recs[0]["code"]
        put((f"{c['torus'][0]}x{c['torus'][1]}", c["k"], c["d"]), run.tier(recs),
            "independent check of [[310,10,22]]")  # fmt: skip
    return out


def published() -> list[dict]:
    rows = []
    for c in json.loads(CODES.read_text())["codes"]:
        n, k, d = c["n"], c["k"], c["d"]
        rows.append({"name": c["name"], "n": n, "k": k, "d": d, "l": c["l"], "m": c["m"],
                     "A_text": poly_text(c["A"]) if "A" in c else None,
                     "B_text": poly_text(c["B"]) if "B" in c else None,
                     "score": round(k * d * d / n, 4), "ratio": round(d / math.sqrt(n), 4),
                     "source": c["source"], "note": ""})  # fmt: skip
    rows.append({"name": "[[360,12,24]]", "n": 360, "k": 12, "d": 24, "l": 30, "m": 6,
                 "A_text": None, "B_text": None, "score": 19.2,
                 "ratio": round(24 / math.sqrt(360), 4),
                 "source": "Bravyi et al., Nature 627, 778 (2024), arXiv:2308.07915",
                 "note": "published with d <= 24; d = 24 by this project's registered study "
                         "(qec-open-distance, H1)"})  # fmt: skip
    return rows


def class_hist(c: Census) -> list[dict]:
    rows = []
    for (torus, stage, k, connected, kind, value), count in sorted(c.hist.items()):
        rows.append({"torus": torus, "stage": stage, "k": k, "connected": connected,
                     "kind": kind, "value": value, "classes": count,
                     "codes": c.weight.get((torus, stage, k, connected, kind, value))})  # fmt: skip
    return rows


def run_cost(c: Census) -> list[dict]:
    rows = []
    for (stage, engine, d), xs in sorted(c.runs.items(), key=lambda kv: (kv[0][0], kv[0][1],
                                                                          kv[0][2])):  # fmt: skip
        rows.append({"stage": stage, "engine": engine, "d": d, "runs": len(xs),
                     "median_s": round(statistics.median(xs), 3),
                     "p10_s": round(_quantile(xs, 0.1), 3), "p90_s": round(_quantile(xs, 0.9), 3),
                     "max_s": round(max(xs), 3), "total_s": round(sum(xs), 1)})  # fmt: skip
    for (stage, engine), count in sorted(c.timelimits.items()):
        rows.append({"stage": stage, "engine": engine, "d": None, "runs": count,
                     "median_s": None, "p10_s": None, "p90_s": None, "max_s": None,
                     "total_s": None, "timelimit": True})  # fmt: skip
    for r in rows:
        r.setdefault("timelimit", False)
    return rows


def pending_tori(c: Census) -> list[dict]:
    rows = []
    for ell, m in S4_TORI:
        if (ell, m) in c.tori:
            continue
        rows.append({"torus": f"{ell}x{m}", "l": ell, "m": m, "n": 2 * ell * m, "lm": ell * m,
                     "stage": "4", **group_info(ell, m),
                     "study_group": "exposed" if (ell, m) in S4_EXPOSED else "fresh",
                     "exposed": (ell, m) in S4_EXPOSED, "status": "pending",
                     "classes": None, "criterion_e": None, "frontier_entries": 0})  # fmt: skip
    return rows


def ledger(folder: str) -> list[dict]:
    p = EX / folder / "ledger.jsonl"
    return [r for _, r in _read_jsonl(p)] if p.exists() else []


def progress() -> list[dict]:
    """Each records commit of a run, with the count its message gives."""
    rows = []
    pat = re.compile(r"Census stage (\w+): records \((\d+) (tori|classes)\)")
    for folder in ("qec-census-3d", "qec-census-4"):
        log = _git("log", "--format=%H %cI %s", "--", f"examples/{folder}/records.jsonl")
        for x in log.splitlines():
            sha, when, msg = x.split(" ", 2)
            mt = pat.search(msg)
            if mt:
                rows.append({"run": f"stage {mt.group(1)}", "time": when, "done": int(mt.group(2)),
                             "unit": mt.group(3), "commit": sha[:10]})  # fmt: skip
    return sorted(rows, key=lambda r: (r["run"], r["time"]))


TORUS_RE = re.compile(rb'"l": ?(\d+), ?"m": ?(\d+), ?"n": ?')


def first_seen(out: Path = OUT) -> dict[str, str]:
    """When each torus's record first reached the branch (UTC, to the minute): the first commit
    of its records file that holds it (stages 3b to 4), or the commit that added its data file
    (stage 3a). The tori in each commit are cached by commit in first_seen_cache.json."""
    cache_path = out / "first_seen_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    seen: dict[str, dt.datetime] = {}

    def note(torus: str, when: str) -> None:
        t = dt.datetime.fromisoformat(when).astimezone(dt.UTC)
        if torus not in seen or t < seen[torus]:
            seen[torus] = t

    when = None
    log = _git("log", "--diff-filter=A", "--format=@%cI", "--name-only", "--",
               "examples/qec-census-3/data")  # fmt: skip
    for line in log.splitlines():
        if line.startswith("@"):
            when = line[1:]
        elif line.strip().endswith(".jsonl"):
            note(Path(line.strip()).stem, when)
    for path in (S3B, S3C, S4):
        relp = rel(path)
        for x in _git("log", "--reverse", "--format=%H %cI", "--", relp).splitlines():
            sha, when = x.split()
            key = f"{sha}:{relp}"
            if key not in cache:
                blob = subprocess.run(["git", "-C", str(ROOT), "show", key], capture_output=True,
                                      check=True).stdout  # fmt: skip
                cache[key] = sorted(
                    {f"{a.decode()}x{b.decode()}" for a, b in TORUS_RE.findall(blob)}
                )
            for torus in cache[key]:
                note(torus, when)
    out.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, sort_keys=True, separators=(",", ":")) + "\n")
    return {k: v.strftime("%Y-%m-%d %H:%M") for k, v in seen.items()}


def interim4(c: Census) -> dict:
    """Stage 4's predictions so far, by the registered judge's rules (study.judge_torus) restated:
    E and S2 fail on any torus over the cap or ceiling; G and S1 hold on any torus past the
    record; P0 fails on any torus where criterion E and the classes disagree."""
    fresh = [t for (ell, m), t in c.tori.items() if t["stage"] == "4" and not t["exposed"]]
    out = {"E": [], "S2": [], "G": [], "S1": [], "P0": []}
    for t in fresh:
        if t.get("error") or t.get("class_errors") or t["criterion_e"] != (t["classes"] > 0):
            out["P0"].append(t["torus"])
        if t["d_max"] is None:
            continue
        cap = even_down(E_C * t["n"] ** E_B)
        if t["d_max"] > cap:
            out["E"].append(f"{t['torus']}: d = {t['d_max']} > cap {cap}")
        if t["best_score"] > S_CEILING + 1e-9:
            out["S2"].append(f"{t['torus']}: k·d²/n = {t['best_score']}")
        if t["d_max"] / math.sqrt(t["n"]) > G_RECORD + 1e-9:
            out["G"].append(f"{t['torus']}: d/√n = {t['d_max'] / math.sqrt(t['n']):.4f}")
        if t["best_score"] > S_RECORD + 1e-9:
            out["S1"].append(f"{t['torus']}: k·d²/n = {t['best_score']}")
    return out


def fits(c: Census) -> list[dict]:
    q4 = next(e for e in ledger("qec-census-4") if e["kind"] == "question")
    f4 = q4["body"]["fits"]
    if (f4["b"], f4["c"]) != (E_B, E_C):
        raise ValueError("stage 4's registered E constants differ from build.py's")
    i4 = interim4(c)
    first = lambda xs: xs[0] if xs else None  # noqa: E731
    v3c = next(e for e in ledger("qec-census-3c") if e["kind"] == "verdict")["body"]
    tori3 = {(t["torus"]): t for t in c.tori.values()}

    # stage 3d rejudged its 9 tori on the amended records (its part T): those outcomes stand
    v3d = next(e for e in ledger("qec-census-3d") if e["kind"] == "verdict")["body"]
    per_torus = {**v3c["per_torus"], **{t: {**v3c["per_torus"][t], **v} for t, v in
                                        v3d["per_torus"].items()}}  # fmt: skip

    def failed_on(part: str) -> str:
        """Judged tori only: the exposed ones are reported beside the verdict, not judged."""
        bad = sorted((t for t, v in per_torus.items() if v[part] == "fail"),
                     key=lambda t: (tori3[t]["n"], tori3[t]["l"]))  # fmt: skip
        judged = [t for t in bad if t not in v3c["exposed"]]
        exposed = len(bad) - len(judged)
        return (f"fails on {len(judged)} judged tori (stage 3c, with stage 3d's), first "
                f"{judged[0]}" + (f"; also exceeded on {exposed} exposed tori" if exposed else "")
                ) if judged else ""  # fmt: skip

    if (v3c["P2"], v3c["P3"]) != ("fail", "fail"):
        raise ValueError("stage 3c's verdict on P2 and P3 is not what build.py states")
    rows = [
        {"id": "p2", "label": "P2: best connected d ≤ largest even ≤ 1.4·√n", "kind": "registered",
         "study": "qec-census-3b", "part": "P2", "a": P2_C, "b": 0.5, "c": None,
         "outcome": "failed", "interim": False,
         "decided_by": failed_on("P2")},
        {"id": "p3", "label": "P3: max connected k·d²/n ≤ 13.5 (extrapolation tori)",
         "kind": "registered", "study": "qec-census-3b", "part": "P3", "a": 13.5, "b": None,
         "c": None, "outcome": "failed", "interim": False,
         "decided_by": failed_on("P3")},
        {"id": "e", "label": "E: best connected d ≤ largest even ≤ 0.8011·n^0.6074",
         "kind": "registered", "study": "qec-census-4", "part": "E", "a": E_C, "b": E_B,
         "c": None, "outcome": "failed" if i4["E"] else "pending", "interim": True,
         "decided_by": first(i4["E"])},
        {"id": "g", "label": "G: some torus has d/√n > 1.4606", "kind": "registered",
         "study": "qec-census-4", "part": "G", "a": G_RECORD, "b": 0.5, "c": None,
         "outcome": "held" if i4["G"] else "pending", "interim": True,
         "decided_by": first(i4["G"])},
        {"id": "s1", "label": "S1: some torus has k·d²/n > 13.6054", "kind": "registered",
         "study": "qec-census-4", "part": "S1", "a": S_RECORD, "b": None, "c": None,
         "outcome": "held" if i4["S1"] else "pending", "interim": True,
         "decided_by": first(i4["S1"])},
        {"id": "s2", "label": "S2: no torus has k·d²/n > 17", "kind": "registered",
         "study": "qec-census-4", "part": "S2", "a": S_CEILING, "b": None, "c": None,
         "outcome": "failed" if i4["S2"] else "pending", "interim": True,
         "decided_by": first(i4["S2"])},
        {"id": "edge", "label": "Top edge: 2·⌊0.617·√(n ln n) / 2⌋", "kind": "exploratory",
         "study": "regularity analysis", "part": "", "a": EDGE_C, "b": None, "c": None,
         "outcome": "", "interim": False, "decided_by": None},
        {"id": "power", "label": "Top edge, power law: 0.78·n^0.613", "kind": "exploratory",
         "study": "regularity analysis", "part": "", "a": POWER_A, "b": POWER_B, "c": None,
         "outcome": "", "interim": False, "decided_by": None},
        {"id": "affine", "label": "Top edge, levelling off: 1.75·√n − 4.6",
         "kind": "exploratory", "study": "regularity analysis", "part": "", "a": AFFINE_A,
         "b": AFFINE_B, "c": None, "outcome": "", "interim": False, "decided_by": None},
        {"id": "layer", "label": "k layers: 2.31·n^0.443 − k", "kind": "exploratory",
         "study": "regularity analysis", "part": "", "a": LAYER_A, "b": LAYER_B, "c": None,
         "outcome": "", "interim": False, "decided_by": None},
    ]  # fmt: skip
    for r in rows:
        r["status"] = (r["outcome"] + (" (verdict pending)" if r["interim"] else "")
                       if r["outcome"] else "exploratory")  # fmt: skip
    return rows


def build() -> dict[str, list[dict]]:
    c = Census()
    tier = tiers()
    for e in c.frontier:
        hit = tier.get((e["torus"], e["k"], e["d"]))
        e["tier"] = hit["tier"] if hit else "not checked"
        e["tier_source"] = hit["source"] if hit else None
    # isomorphic tori: one primary torus per group, the computed one with the smallest (l, m)
    reps: dict[str, tuple[int, int]] = {}
    for key, t in sorted(c.tori.items()):
        reps.setdefault(t["iso_key"], key)
    for key, t in c.tori.items():
        rep = reps[t["iso_key"]]
        t["primary"] = key == rep
        t["iso_rep"] = f"{rep[0]}x{rep[1]}"
        t["iso_copies"] = sum(1 for x in c.tori.values() if x["iso_key"] == t["iso_key"])
    for e in c.frontier:
        t = c.tori[(e["l"], e["m"])]
        e["primary"], e["iso_rep"] = t["primary"], t["iso_rep"]
    # an entry left unsettled on one torus may be settled on an isomorphic one (the same codes):
    # 9x15 (stage 3c's exposed group, which stage 3d did not rerun) and 3x45 are the case
    twins: dict[tuple[str, int], dict] = {}
    for e in c.frontier:
        if e["settled"]:
            twins.setdefault((e["iso_key"], e["k"]), e)
    for e in c.frontier:
        twin = twins.get((e["iso_key"], e["k"])) if not e["settled"] else None
        e["iso_settled_d"] = twin["d"] if twin else None
        e["iso_settled_torus"] = twin["torus"] if twin else None
    tori = sorted(c.tori.values(), key=lambda t: (t["n"], t["l"])) + pending_tori(c)
    for t in tori:
        t.setdefault("primary", True)
        t.setdefault("iso_rep", t["torus"])
    seen = first_seen()
    for t in tori:
        t["first_seen"] = seen.get(t["torus"])
    for e in c.frontier:
        e["first_seen"] = seen.get(e["torus"])
    frontier = sorted(c.frontier, key=lambda e: (e["n"], e["l"], e["k"]))
    pub = published()
    return {"frontier": frontier, "tori": tori, "published": pub, "class_hist": class_hist(c),
            "run_cost": run_cost(c), "progress": progress(), "fits": fits(c),
            "summary": summary(c, frontier, tori, pub)}  # fmt: skip


def summary(c: Census, frontier: list[dict], tori: list[dict], pub: list[dict]) -> list[dict]:
    computed = [t for t in tori if t["status"] != "pending"]
    with_codes = [t for t in computed if t["classes"]]
    settled = [t for t in with_codes if t["status"] == "settled"]
    best = max(frontier, key=lambda e: (e["score"], -e["n"]))
    best_ratio = max(frontier, key=lambda e: (e["ratio"], -e["n"]))
    pub_below = max((p for p in pub if p["n"] <= best["n"]), key=lambda p: p["score"])
    s4 = [t for t in tori if t["stage"] == "4"]
    q4 = ledger("qec-census-4")
    started = next(e["time"] for e in q4 if e["kind"] == "run_started")
    stop = dt.datetime.fromisoformat(started) + dt.timedelta(days=STOP_DAYS)
    commit = _git("rev-parse", "HEAD")
    dirty = bool(_git("status", "--porcelain", "--", "examples/qec-census-3",
                      "examples/qec-census-3b", "examples/qec-census-3c", "examples/qec-census-3d",
                      "examples/qec-census-4/records.jsonl"))  # fmt: skip
    code = lambda e: f"[[{e['n']},{e['k']},{e['d']}]]"  # noqa: E731
    rows = [
        ("built_at", None, dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")),
        ("commit", None, commit[:10] + (" (records changed since)" if dirty else "")),
        ("tori_total", len(tori), None),
        ("tori_computed", len(computed), None),
        ("tori_pending", len(tori) - len(computed), None),
        ("tori_with_codes", len(with_codes), None),
        ("tori_settled", len(settled), None),
        ("settled_share", round(len(settled) / len(with_codes), 4), None),
        ("classes", sum(t["classes"] for t in computed), None),
        ("frontier_entries", len(frontier), None),
        ("distinct_entries", sum(e["primary"] for e in frontier), None),
        ("best_score", best["score"], code(best)),
        ("best_score_torus", None, best["torus"]),
        ("best_ratio", best_ratio["ratio"], code(best_ratio)),
        ("published_best_at_or_below", pub_below["score"], pub_below["name"]),
        ("published_best_at_or_below_n", pub_below["n"], None),
        ("stage4_done", sum(t["status"] != "pending" for t in s4), None),
        ("stage4_total", len(s4), None),
        ("stage4_started", None, started[:16].replace("T", " ") + " UTC"),
        ("stage4_stop", None, stop.strftime("%Y-%m-%d %H:%M UTC")),
        ("exact_runs", sum(t.get("exact_runs") or 0 for t in computed), None),
    ]
    return [{"metric": m, "value": v, "text": s} for m, v, s in rows]


# --------------------------------------------------------------------------------------------
# reconciliation


def check(data: dict[str, list[dict]]) -> list[str]:
    """Problems with the datasets, checked against the records independently of build()."""
    problems = []
    fr, tori = data["frontier"], data["tori"]
    names = [t["torus"] for t in tori]
    if len(names) != len(set(names)):
        problems.append("a torus appears twice")
    # every connected (torus, k) entry of the records, counted directly
    count = 0
    for p in S3A:
        lines = [json.loads(x) for x in open(p) if x.strip()]
        count += len({r["k"] for r in lines[1:] if r["connected"] and r["status"] == "complete"})
    for p in (S3B, S3C, S4):
        for _, r in _read_jsonl(p):
            if r.get("job") == "torus" and "error" not in r:
                count += sum(1 for v in r["best"]["connected"].values() if v["d"] is not None)
    if count != len(fr):
        problems.append(f"frontier: {len(fr)} entries, the records have {count}")
    # isomorphic tori carry the same codes: the same k's, the same settled d, and no unsettled
    # lower bound above a settled twin
    by_iso: dict[str, dict[str, dict[int, dict]]] = defaultdict(lambda: defaultdict(dict))
    for e in fr:
        by_iso[e["iso_key"]][e["torus"]][e["k"]] = e
    for key, per in by_iso.items():
        if len({tuple(sorted(v)) for v in per.values()}) > 1:
            problems.append(f"isomorphic tori {sorted(per)} ({key}) have different k's")
        for k in {k for v in per.values() for k in v}:
            es = [v[k] for v in per.values() if k in v]
            settled = {e["d"] for e in es if e["settled"]}
            if len(settled) > 1 or any(not e["settled"] and settled and e["d"] > min(settled)
                                       for e in es):  # fmt: skip
                problems.append(f"isomorphic tori {sorted(per)} ({key}) differ at k = {k}")
    # every checked code sits at a frontier entry, at or below its d (a check may predate the
    # entry's settling: stage 3d raised 3x47 and 3x49 from 22 to 24)
    best = {(e["torus"], e["k"]): e["d"] for e in fr}
    for torus, k, d in tiers():
        if (torus, k) not in best or d > best[(torus, k)]:
            problems.append(f"checked code {(torus, k, d)} is above or off the frontier")
    # stage 3d: the 9 tori it reran are settled at d = 24
    for e in fr:
        if e["settled_by"].startswith("stage 3d") and (e["d"] != 24 or not e["settled"]):
            problems.append(f"{e['id']}: stage 3d entry at d = {e['d']}")
    if len({e["torus"] for e in fr if e["settled_by"].startswith("stage 3d")}) != 9:
        problems.append("stage 3d should settle entries on 9 tori")
    # every d is even, every witness has weight d
    for e in fr:
        if e["d"] % 2:
            problems.append(f"{e['id']}: odd d")
        if e["witness"] and len(json.loads(e["witness"])) != e["d"]:
            problems.append(f"{e['id']}: witness weight differs from d")
    # stage 4's torus list agrees with the study's count
    if sum(t["stage"] == "4" for t in tori) != len(S4_TORI):
        problems.append("stage 4 torus count")
    return problems


def write(data: dict[str, list[dict]], out: Path = OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in data.items():
        (out / f"{name}.json").write_text(json.dumps(rows, separators=(",", ":"),
                                                     ensure_ascii=False) + "\n")  # fmt: skip


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="build and check, write nothing")
    p.add_argument("--out", type=Path, default=OUT)
    a = p.parse_args()
    data = build()
    problems = check(data)
    for name, rows in data.items():
        size = len(json.dumps(rows, separators=(",", ":"), ensure_ascii=False))
        print(f"{name}: {len(rows)} rows, {size / 1024:.0f} KB")
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        raise SystemExit(1)
    if not a.check:
        write(data, a.out)
        print(f"written to {rel(a.out)}")


if __name__ == "__main__":
    main()
