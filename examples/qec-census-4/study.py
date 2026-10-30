"""
Census stage 4: the laws refitted to stages 3a-3d, tested on tori nobody has computed on,
n = 302 to 400.

    uv run --no-sync python examples/qec-census-4/study.py register
    uv run --no-sync python examples/qec-census-4/study.py run --workers 32
    uv run --no-sync python examples/qec-census-4/study.py resume --workers 32   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-4

**The family** is stage 3a's: A and B each three distinct monomials of Z_l x Z_m.

**The tori.** Every l x m with 2 <= l <= m and 150 < lm <= 200 (n = 302 to 400): 110 tori.
- FRESH: the 104 that no earlier work mentions. No code's d has been computed on them. Stage
  2b computed k for every raw trinomial code on 3 x 51 and 2 x 80 (examples/qec-census-2b), so
  their k > 0 classes, and 10 x 16's (the group of 2 x 80), are known; that bears on P0 only.
  Only 53 of the 104 can have codes at all (both odd parts > 1), in 37 distinct groups. Six
  share a group with an EXPOSED torus (2 x 77 and 7 x 22 with 11 x 14; 3 x 52 and 4 x 39 with
  12 x 13; 2 x 91 and 7 x 26 with 13 x 14); 2 x 77, 2 x 91 and 4 x 39 have no codes. Codes on
  isomorphic tori are the same codes, but nothing was computed on the exposed tori either.
- EXPOSED: 6, reported and not judged. 11 x 14, 12 x 13, 13 x 13, 13 x 14 and 14 x 14 are
  named in holdout.json's development_sizes_mentioned. 6 x 30 is the torus of the published
  [[360,12,<=24]] (examples/qec-open-distance).

**The instrument** is fast4.py:
- stage 3b's classes and window bounds, plus a third, longer window before any exact run;
- DistQLDPC's cluster engine as the exact engine, with a witness of weight d checked by
  distance.verify_witness for every exact d;
- the parity of d (d is even for this family) in every comparison of bounds;
- census4.c for lm <= 200.
LIMIT is DistQLDPC's limit per class.

**Validation** (validate4.py, on 32-vCPU pods; records and compare.json in validation/). Before
this registration, fast4.py reran 16 stage 3b/3c tori: all five n = 300 tori, 3 x 49, 7 x 21,
2 x 72, 4 x 36, 3 x 48, the P2 tori and four random ones.
- Every best d equals stage 3b/3c's, and every entry is settled, including the formerly
  incomplete ones.
- All 528 classes both instruments finished agree on d. No class was left unverified.
- Each torus took 1 to 16 minutes (3 x 49: 14 minutes, against about 50 core-hours of exact
  search in stage 3b). The peak memory of any process was 151 MB.
- The third window was added afterwards (fast4.py's docstring), and is not part of that run.

**Cost, and what it means for the predictions.** DistQLDPC's time per class grew about 8 times
for each +2 in d in the validation: a median of 4 s at d = 20, 29 s at d = 22, and 4 minutes at
d = 24. Extrapolated, that is about 35 minutes at d = 26, 4.5 hours at d = 28 and a day and a
half at d = 30. The fits put the best d at n = 350 to 400 around 26 to 28. So, with LIMIT =
4 hours:
- many classes at d = 28, and every class at d = 30, will not finish. A torus whose best is not
  settled leaves E and S2 "incomplete" there.
- G and S1 need only a code that is found, so they can still pass.
The expected run is several days on one 32-vCPU pod.

**The predictions**, fitted by fits.py on stages 3a-3d (157 tori with codes, n <= 300). Each
is judged on FRESH.
- **P0, instruments (decisive).** Criterion E (stage 3b, proved) decides which tori have
  classes with k > 0. On a fixed random sample of K_SAMPLE raw codes per torus, the common-zero
  rule agrees with bb.k_linalg > 0. No job fails.
- **E, the envelope (decisive).** On every torus, the best connected d is at most the largest
  even number <= C_ENV n^B. Here B = 0.6074 is the fitted growth exponent of the best d with n,
  and C_ENV = 0.8011 is the largest d_max / n^B in stages 3a-3d, at 3 x 28.
- **G, growth past sqrt(n) (decisive).** Some torus has a connected code with
  d / sqrt(n) > G_RECORD = 1.4606. That is stages 3a-3d's largest value, at 3 x 45 and 5 x 27,
  and the band maximum has risen in every band of 50 in n so far.
- **S1, the record falls (decisive).** Some torus has a connected code with k d^2 / n >
  S_RECORD = 13.6054. That is the [[294,10,20]]'s value. A line through the band maxima gives
  about 15 at n = 350.
- **S2, a ceiling (decisive).** No torus has a connected code with k d^2 / n > S_CEILING = 17.0.
  That is the band-maxima line at n = 400 (16.0), plus 1.

**E and G together.** Both can hold only if some torus reaches d = cap(n) exactly, where cap(n)
> 1.4606 sqrt(n). That is possible on 50 of the tori, with one even d each.

**Settled and unsettled.** A best d that the instrument did not settle is a lower bound on the
torus's best, as in stage 3b. It can prove E or S2 false and G or S1 true, never the other way.
A prediction that needs a settled value it does not have is "incomplete".

**The verdict.** "hold" when every prediction passes; "fail" when any fails; "incomplete"
otherwise.

**The guard.** census.guard refuses every torus outside stage 1. fast4.opened admits this
study's tori, in this study's run process only, while execute runs. That is after the harness
has checked that the registration is committed and pushed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fast4 = _load("qec_census_stage4_fast", HERE / "fast4.py")
s3b = _load("qec_census_stage3b_study", HERE.parent / "qec-census-3b" / "study.py")
fits = _load("qec_census_stage4_fits", HERE / "fits.py")
bb, c3, census = fast4.bb, fast4.c3, fast4.census

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-census-stage4"
LIMIT = 14400  # 4 h per class: d = 24 took 4 min, and each +2 in d about 8 times longer
K_SAMPLE = 50
B, C_ENV = 0.6074, 0.8011
G_RECORD, S_RECORD, S_CEILING = 1.4606, 13.6054, 17.0
EXPOSED = [(6, 30), (11, 14), (12, 13), (13, 13), (13, 14), (14, 14)]
SETTINGS = {"limit": LIMIT, "witness_windows": fast4.WITNESS_WINDOWS, "k_sample": K_SAMPLE,
            "window_seconds": fast4.WINDOW_SECONDS, "window_retry": fast4.WINDOW_RETRY,
            "window_long": fast4.WINDOW_LONG,
            "window_seed": fast4.WINDOW_SEED}  # fmt: skip
HASHED = {"study_py": HERE / "study.py", "fast4_py": HERE / "fast4.py", "fits_py": HERE / "fits.py",
          "census4_c": fast4.CENSUS4_C, "fast_py": HERE.parent / "qec-census-3b" / "fast.py",
          "census3_py": HERE.parent / "qec-census-3" / "census3.py",
          "census_py": HERE.parent / "qec-census" / "census.py",
          "s3b_study_py": HERE.parent / "qec-census-3b" / "study.py",
          "s3c_study_py": HERE.parent / "qec-census-3c" / "study.py",
          "distq_py": HERE.parent / "qec-census-3b" / "spotcheck" / "distq.py",
          "parts_py": HERE.parent / "qec-open-distance" / "parts.py",
          "pack_py": HERE.parent / "qec-open-distance-2" / "pack.py",
          "distance_py": Path(c3.distance.__file__), "bb_py": Path(bb.__file__),
          "tests_py": ROOT / "tests" / "test_qec_census_4.py",
          "tests_study_py": ROOT / "tests" / "test_qec_census_4_study.py",
          "window_c": fast4.pack.plain.WINDOW_C, "search_pack_c": fast4.pack.SEARCH_C,
          "holdout_json": fast4.census.HOLDOUT,
          "retest_py": HERE.parent / "qec-distance-2" / "study.py"}  # fmt: skip
DISTQLDPC_COMMIT = "8fe913e2ca79bda37cb755975b06b1b60416a418"


def code_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in HASHED.items()}


def tori() -> dict[str, list[tuple[int, int]]]:
    every = sorted(((ell, m) for ell in range(2, 15) for m in range(ell, 101)
                    if 150 < ell * m <= 200), key=lambda t: (t[0] * t[1], t))  # fmt: skip
    return {"fresh": [t for t in every if t not in EXPOSED],
            "exposed": [t for t in every if t in EXPOSED]}  # fmt: skip


def group_of(ell: int, m: int) -> str:
    return "exposed" if (ell, m) in EXPOSED else "fresh"


def cap(n: int) -> int:
    x = math.floor(C_ENV * n**B)
    return x - (x % 2)


def k_sample(ell: int, m: int) -> dict:
    pairs, masks = c3.zero_masks(ell, m)
    rng = random.Random(f"{ID} k sample {ell}x{m}")
    bad = 0
    for _ in range(K_SAMPLE):
        i, j = sorted((rng.randrange(len(pairs)), rng.randrange(len(pairs))))
        meet = bool((masks[i] & masks[j]).any())
        A, B_ = c3.polynomial(pairs[i], m), c3.polynomial(pairs[j], m)
        bad += meet != (bb.k_linalg(A, B_, ell, m) > 0)
    return {"sampled": K_SAMPLE, "disagree": bad}


def question() -> dict:
    t = tori()
    return {"id": ID, "title": "Census stage 4: the refitted laws on n = 302 to 400",
            "tori": {g: [list(x) for x in ts] for g, ts in t.items()},
            "settings": SETTINGS, "sha256": code_hashes(), "distqldpc_commit": DISTQLDPC_COMMIT,
            "fits": fits.fit(),
            "seen_before": ["stages 1-3d's data and write-ups (docs/code-census.md)",
                            "stage 2b's k for every raw trinomial code on 3x51 and 2x80",
                            "the published [[360,12,<=24]] on 6 x 30 (exposed)",
                            "validate4.py's run of fast4.py on 16 stage 3b/3c tori "
                            "(validation/), nothing on a stage 4 torus"]}  # fmt: skip


def predictions() -> list[dict]:
    return [
        {"part": "P0", "predict": "criterion E decides k > 0 on every torus; the common-zero "
         "rule agrees with k_linalg on every sampled raw code; no job fails"},
        {"part": "E", "predict": f"best connected d <= largest even <= {C_ENV} n^{B}",
         "c": C_ENV, "b": B},
        {"part": "G", "predict": f"some torus has a connected code with d/sqrt(n) > {G_RECORD}",
         "record": G_RECORD},
        {"part": "S1", "predict": f"some torus has a connected code with k d^2/n > {S_RECORD}",
         "record": S_RECORD},
        {"part": "S2", "predict": f"no torus has a connected code with k d^2/n > {S_CEILING}",
         "ceiling": S_CEILING},
        {"part": "H", "predict": "every record made by the registered code and settings",
         "settings": SETTINGS, "sha256": code_hashes()},
    ]  # fmt: skip


def _rows(path: Path) -> list[dict]:
    return [json.loads(x) for _, _, x in record_lines(Path(path))]


def consistency() -> list[str]:
    """What must still be as registered: the code and the tori."""
    from lattice_lab.ledger import Ledger

    entries = Ledger(HERE / "ledger.jsonl").entries
    if not entries:
        return ["stage 4 is not registered"]
    q = entries[0]["body"]
    problems = []
    if q["sha256"] != code_hashes():
        problems.append("the code differs from the registration")
    if q["tori"] != {g: [list(x) for x in ts] for g, ts in tori().items()}:
        problems.append("the tori differ from the registration")
    return problems


def distqldpc_commit() -> str | None:
    """DistQLDPC's commit, or None if its checkout has local changes or cannot be read."""
    try:
        git = ["git", "-C", str(fast4.distq.DISTQ)]
        status = git + ["status", "--porcelain", "--untracked-files=no"]
        dirty = subprocess.run(status, capture_output=True, text=True, check=True).stdout.strip()
        head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()  # fmt: skip
        return None if dirty else head
    except Exception:
        return None


CHECKPOINT = HERE / "exact-checkpoint.jsonl"


def _checkpoint(ell: int, m: int) -> dict:
    """The exact results already found on this torus by this run (a stopped run's work)."""
    out = {}
    if CHECKPOINT.exists():
        for line in CHECKPOINT.read_text().splitlines():
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue  # a line cut short by a stop
            if (c["l"], c["m"]) == (ell, m) and c.get("sha256") == code_hashes():
                out[c["key"]] = c["exact"]
    return out


def _save(ell: int, m: int, key: str, res: dict) -> None:
    line = {"l": ell, "m": m, "key": key, "exact": res, "sha256": code_hashes()}
    with CHECKPOINT.open("a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")


def execute(path: Path, workers: int) -> None:
    commit = distqldpc_commit()
    if commit != DISTQLDPC_COMMIT:
        raise RuntimeError(f"DistQLDPC at {commit}, registered {DISTQLDPC_COMMIT}")
    done = {(r["l"], r["m"]) for r in _rows(path)} if Path(path).exists() else set()
    order = [x for g in ("fresh", "exposed") for x in tori()[g]]
    with fast4.opened(order):
        for ell, m in order:
            if (ell, m) in done:
                continue
            rec = {"job": "torus", "id": ID, "l": ell, "m": m, "n": 2 * ell * m,
                   "group": group_of(ell, m), "settings": SETTINGS, "distqldpc_commit": commit,
                   "sha256": {k: v for k, v in code_hashes().items()
                              if k in ("study_py", "fast4_py", "census4_c")}}  # fmt: skip
            try:
                rec["criterion_e"] = s3b.criterion_e(ell, m)
                rec["k_sample"] = k_sample(ell, m)
                f = fast4.frontier(ell, m, workers=workers, limit=LIMIT,
                                   log=lambda s: print(s, flush=True),
                                   cache=_checkpoint(ell, m),
                                   on_exact=lambda key, res, t=(ell, m): _save(*t, key,
                                                                               res))  # fmt: skip
                rec |= {"classes": len(f["classes"]), "best": f["best"],
                        "rows": [{k: r.get(k) for k in ("key", "A", "B", "k", "connected",
                                                        "upper", "exact")}
                                 for r in f["classes"]],
                        **{k: f[k] for k in ("orbit_reps", "classes_seconds", "bound_seconds",
                                             "exact_runs", "exact_seconds")}}  # fmt: skip
            except Exception:
                rec["error"] = traceback.format_exc()[-2000:]
            append_records(path, [rec])
            print(f"{ell}x{m}: done{' ERROR' if 'error' in rec else ''}", flush=True)


def judge_torus(rec: dict) -> dict:
    """Each prediction on one torus: 'pass', 'fail', 'incomplete' (E, S2), or for the
    existential G and S1 whether this torus witnesses them ('yes', 'no', 'open')."""
    if "error" in rec:
        return {"P0": "fail", "E": "incomplete", "S2": "incomplete", "G": "open", "S1": "open",
                "error": True}  # fmt: skip
    has = rec["classes"] > 0
    out = {"P0": "pass" if rec["criterion_e"] == has and rec["k_sample"]["disagree"] == 0
           else "fail"}  # fmt: skip
    best = s3b._bests(rec)
    n = rec["n"]
    settled = all(v["settled"] for v in best.values())
    low = {k: v["d"] for k, v in best.items() if v["d"] is not None}
    dmax = max(low.values(), default=None)
    score = max((k * d * d / n for k, d in low.items()), default=None)
    ratio = None if dmax is None else dmax / math.sqrt(n)

    def universal(failed: bool) -> str:
        return "fail" if failed else ("pass" if settled else "incomplete")

    def existential(hit: bool) -> str:
        return "yes" if hit else ("no" if settled else "open")

    out["E"] = universal(dmax is not None and dmax > cap(n))
    out["S2"] = universal(score is not None and score > S_CEILING + 1e-9)
    out["G"] = existential(ratio is not None and ratio > G_RECORD + 1e-9)
    out["S1"] = existential(score is not None and score > S_RECORD + 1e-9)
    out["values"] = {"d_max": dmax, "cap": cap(n), "d_over_sqrt_n": None if ratio is None
                     else round(ratio, 4), "score": None if score is None else round(score, 4),
                     "settled": settled}  # fmt: skip
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    t = tori()
    judged = {(r["l"], r["m"]): judge_torus(r) for r in rows if r.get("job") == "torus"}
    fresh = t["fresh"]
    missing = [x for x in fresh if x not in judged]
    parts = {}
    for p in ("P0", "E", "S2"):
        vals = [judged[x][p] for x in fresh if x in judged]
        parts[p] = "fail" if "fail" in vals else "incomplete" if missing or \
            "incomplete" in vals else "pass"  # fmt: skip
    for p in ("G", "S1"):
        vals = [judged[x][p] for x in fresh if x in judged]
        parts[p] = "pass" if "yes" in vals else "incomplete" if missing or "open" in vals \
            else "fail"  # fmt: skip
    problems = []
    hashes = code_hashes()
    for r in rows:
        if r.get("settings") != SETTINGS:
            problems.append(f"{r.get('l')}x{r.get('m')}: other settings")
        for k, v in r.get("sha256", {}).items():
            if v != hashes[k]:
                problems.append(f"{r['l']}x{r['m']}: another {k}")
        if r.get("distqldpc_commit") not in (None, DISTQLDPC_COMMIT):
            problems.append(f"{r['l']}x{r['m']}: DistQLDPC at {r['distqldpc_commit']}")
    if registered and registered[-1].get("sha256") not in (None, hashes):
        problems.append("the code differs from the registration")
    parts["H"] = "fail" if problems else "pass"
    vals = list(parts.values())
    verdict = "fail" if "fail" in vals else "hold" if all(v == "pass" for v in vals) else \
        "incomplete"  # fmt: skip
    return {"verdict": verdict, **parts, "problems": problems, "missing": len(missing),
            "per_torus": {f"{a}x{b}": v for (a, b), v in judged.items()},
            "frontier": s3b.frontier_by_nk(rows),
            "exposed": {f"{a}x{b}": judged[(a, b)] for a, b in t["exposed"]
                        if (a, b) in judged}}  # fmt: skip


STUDY = Study(directory=HERE, question=question, predictions=predictions, execute=execute,
              decide=decide)  # fmt: skip

if __name__ == "__main__":
    main(STUDY)
