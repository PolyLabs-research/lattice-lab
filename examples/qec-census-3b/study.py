"""
Census stage 3b: a registered test, on the held-out tori, of the patterns stage 3a
(examples/qec-census-3) found among every weight-6 bivariate bicycle code on the stage-1 tori.

    uv run --no-sync python examples/qec-census-3b/study.py register
    uv run --no-sync python examples/qec-census-3b/study.py run --workers 4
    uv run --no-sync python examples/qec-census-3b/study.py resume --workers 4  (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-3b

**The family** is stage 3a's: A and B each three distinct monomials of Z_l x Z_m. **Nothing of
this family has been computed on these tori.** Stage 2 (examples/qec-census-2, -2b) computed its
trinomial subfamily there, and those results are known. Stage 3a's data and docs/code-census.md
record what was seen before this registration.

**The tori** (holdout.json):
- RANDOM: the 22 of held_out_random, lm 56 to 100;
- EXTRAPOLATION: the 79 of held_out_extrapolation not in exposed_extrapolation, lm 101 to 150;
- EXPOSED: the 21 exposed ones, 12 x 12 among them, reported and not judged, as in stage 2.

**The instruments** (fast.py, checked against stage 3a on stage-1 tori: tests and
docs/census-stage3b-draft.md):
- classes from orbit representatives, with census.c's key;
- k by the common-zero rule, then bb.k_linalg for each class;
- per k, the best d by a checked window bound for every class and the exact packing search
  (stage 3a's deep_distance) for every class whose bound exceeds the best found, with a limit of
  LIMIT seconds per exact run. A best d is "settled" when no unfinished class could exceed it.

**Criterion E (proved).** Some weight-6 code on Z_l x Z_m has k > 0 exactly when, for some e > 1
dividing the exponent of the odd part, mu_e holds an a != 1 with 1 + a in mu_e
(docs/census-stage3b-draft.md gives the argument).

**The predictions** (judged on RANDOM and EXTRAPOLATION):
- **P0, instruments (decisive).**
  - Criterion E holds on every torus: classes with k > 0 exist exactly where E says.
  - On a fixed random sample of K_SAMPLE raw codes per torus, the common-zero rule agrees with
    bb.k_linalg > 0.
  - No job fails (a failed witness check raises, and so does a k = 0 class).
- **P1, monotonicity (decisive).** On every torus with connected codes, the settled best d of a
  connected code is non-increasing in k.
- **P2, the envelope (decisive).** The best d of a connected code on a torus is at most the
  largest even number <= 1.40 sqrt(n).
- **P3, no new record (decisive).** The highest k d^2/n of a connected code is at most 12.0 on
  every RANDOM torus, and at most 13.5 on every EXTRAPOLATION torus.
- **P4, [[192,8,16]] (decisive).** On 2 x 48 (Z_2 x Z_48, the group of Liang et al.'s
  twisted-torus [[192,8,16]]), the settled best d of a connected code with k = 8 is 16.
- **Reported:** the frontier by (n, k), stage 2's trinomial frontier against it, and the
  EXPOSED tori.

**The verdict.** "hold" when P0 to P4 pass; "fail" when any fails; "incomplete" when a needed
best d is not settled, or a job is missing, and nothing has failed. A prediction that cannot be
judged for want of a settled value makes it incomplete, not failed.

**The guard.** Stage 1's census.guard refuses every held-out torus. Here it is replaced, in this
study's run process only and only while `execute` runs (after the harness has checked that the
registration is committed and pushed), by a guard that also admits the registered tori.
census.py, census3.py and every earlier study's files are unchanged.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import sys
import traceback
from contextlib import contextmanager
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


fast = _load("qec_census_stage3b_fast", HERE / "fast.py")
c3, census, bb = fast.c3, fast.census, fast.bb

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-census-stage3b"
LIMIT = 1800.0
K_SAMPLE = 50
P2_CONSTANT = 1.40
P3_RANDOM, P3_EXTRAPOLATION = 12.0, 13.5
P4_TORUS, P4_K, P4_D = (2, 48), 8, 16
SETTINGS = {"limit": LIMIT, "k_sample": K_SAMPLE, "window_seconds": fast.WINDOW_SECONDS,
            "window_retry": fast.WINDOW_RETRY, "window_seed": fast.WINDOW_SEED}  # fmt: skip
HASHED = {
    "study_py": HERE / "study.py",
    "fast_py": HERE / "fast.py",
    "census3_py": HERE.parent / "qec-census-3" / "census3.py",
    "census_py": HERE.parent / "qec-census" / "census.py",
    "census_c": census.CENSUS_C,
    "search_pack_c": c3.pack.SEARCH_C,
    "window_c": c3.pack.plain.WINDOW_C,
    "distance_py": Path(c3.distance.__file__),
    "bb_py": Path(bb.__file__),
    "tests_py": ROOT / "tests" / "test_qec_census_3b.py",
}


def code_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in HASHED.items()}


def _holdout() -> dict:
    return json.loads(census.HOLDOUT.read_text())


def tori() -> dict[str, list[tuple[int, int]]]:
    h = _holdout()
    exposed = {tuple(t) for t in h["exposed_extrapolation"]}
    extra = [tuple(t) for t in h["held_out_extrapolation"] if tuple(t) not in exposed]
    key = lambda t: (t[0] * t[1], t)  # noqa: E731
    return {"random": sorted((tuple(t) for t in h["held_out_random"]), key=key),
            "extrapolation": sorted(extra, key=key), "exposed": sorted(exposed, key=key)}  # fmt: skip


def group_of(ell: int, m: int) -> str:
    for g, ts in tori().items():
        if (ell, m) in ts:
            return g
    raise KeyError((ell, m))


_ORIGINAL_GUARD = census.guard


@contextmanager
def opened():
    """Inside a registered run: admit the study's tori to census.guard (and so to census3's and
    fast's guards, which call it)."""
    allowed = {t for ts in tori().values() for t in ts}

    def guard(ell, m, allow_isomorphic=False):
        if (int(ell), int(m)) in allowed:
            return
        return _ORIGINAL_GUARD(ell, m, allow_isomorphic)

    census.guard = guard
    try:
        yield
    finally:
        census.guard = _ORIGINAL_GUARD


def criterion_e(ell: int, m: int) -> bool:
    """docs/census-stage3b-draft.md's criterion: some e > 1 dividing the odd part's exponent with
    an a != 1 in mu_e such that 1 + a is in mu_e."""
    lo, mo = bb.two_part(ell)[1], bb.two_part(m)[1]
    E = math.lcm(lo, mo)
    for e in range(3, E + 1, 2):
        if E % e:
            continue
        F = bb._field(e)
        mu = {F.pow(F.zeta, i) for i in range(e)}
        if any((1 ^ a) in mu for a in mu if a != 1):
            return True
    return False


def k_sample(ell: int, m: int) -> dict:
    """K_SAMPLE raw codes drawn with a seed from the torus: the common-zero rule against
    bb.k_linalg > 0."""
    pairs, masks = c3.zero_masks(ell, m)
    rng = random.Random(f"{ID} k sample {ell}x{m}")
    bad = 0
    for _ in range(K_SAMPLE):
        i, j = sorted((rng.randrange(len(pairs)), rng.randrange(len(pairs))))
        meet = bool((masks[i] & masks[j]).any())
        A, B = c3.polynomial(pairs[i], m), c3.polynomial(pairs[j], m)
        bad += meet != (bb.k_linalg(A, B, ell, m) > 0)
    return {"sampled": K_SAMPLE, "disagree": bad}


def question() -> dict:
    t = tori()
    return {"id": ID, "title": "Census stage 3b: stage 3a's patterns on the held-out tori",
            "tori": {g: [list(x) for x in ts] for g, ts in t.items()},
            "settings": SETTINGS, "sha256": code_hashes(),
            "seen_before": ["stage 3a's data and write-up (docs/code-census.md, stage 3a)",
                            "stage 2's trinomial results on these tori",
                            "the leaderboard's [[192,8,16]] (Liang et al., an upper bound)"],
            "draft": "docs/census-stage3b-draft.md"}  # fmt: skip


def predictions() -> list[dict]:
    return [
        {"part": "P0", "predict": "criterion E decides k > 0 on every torus; the common-zero "
         "rule agrees with k_linalg on every sampled raw code; no job fails"},
        {"part": "P1", "predict": "the settled best d of connected codes is non-increasing in k"},
        {"part": "P2", "predict": f"best connected d <= largest even <= {P2_CONSTANT} sqrt(n)",
         "constant": P2_CONSTANT},
        {"part": "P3", "predict": f"max connected k d^2/n <= {P3_RANDOM} (random), "
         f"<= {P3_EXTRAPOLATION} (extrapolation)", "random": P3_RANDOM,
         "extrapolation": P3_EXTRAPOLATION},
        {"part": "P4", "predict": f"on {P4_TORUS[0]}x{P4_TORUS[1]} the settled best connected d "
         f"at k = {P4_K} is {P4_D}", "torus": list(P4_TORUS), "k": P4_K, "d": P4_D},
        {"part": "H", "predict": "every record made by the registered code and settings",
         "settings": SETTINGS, "sha256": code_hashes()},
    ]  # fmt: skip


def _rows(path: Path) -> list[dict]:
    return [json.loads(x) for _, _, x in record_lines(Path(path))]


def execute(path: Path, workers: int) -> None:
    done = {(r["l"], r["m"]) for r in _rows(path)}
    order = [t for g in ("random", "extrapolation", "exposed") for t in tori()[g]]
    with opened():
        for ell, m in order:
            if (ell, m) in done:
                continue
            rec = {"job": "torus", "id": ID, "l": ell, "m": m, "n": 2 * ell * m,
                   "group": group_of(ell, m), "settings": SETTINGS,
                   "sha256": {k: v for k, v in code_hashes().items()
                              if k in ("fast_py", "census3_py", "search_pack_c")}}  # fmt: skip
            try:
                rec["criterion_e"] = criterion_e(ell, m)
                rec["k_sample"] = k_sample(ell, m)
                f = fast.frontier(ell, m, workers=workers, limit=LIMIT,
                                  log=lambda s: print(s, flush=True))  # fmt: skip
                rec |= {"classes": len(f["classes"]), "best": f["best"],
                        "rows": [{k: r.get(k) for k in ("key", "A", "B", "k", "connected",
                                                        "upper", "exact")}
                                 for r in f["classes"]],
                        **{k: f[k] for k in ("orbit_reps", "classes_seconds", "bound_seconds",
                                             "exact_runs", "exact_seconds")}}  # fmt: skip
            except Exception:
                rec["error"] = traceback.format_exc()[-2000:]
            append_records(path, [rec])


def _bests(rec: dict) -> dict[int, dict]:
    return {int(k): v for k, v in rec.get("best", {}).get("connected", {}).items()}


def judge_torus(rec: dict) -> dict:
    """Each prediction on one torus: 'pass', 'fail' or 'incomplete', with the values used."""
    out = {}
    if "error" in rec:
        return {"P0": "fail", "error": True}
    has = rec["classes"] > 0
    p0 = rec["criterion_e"] == has and rec["k_sample"]["disagree"] == 0
    out["P0"] = "pass" if p0 else "fail"
    best = _bests(rec)
    if not best:
        return out | {"P1": "pass", "P2": "pass", "P3": "pass"}
    settled = all(v["settled"] for v in best.values())
    ks = sorted(best)
    ds = [best[k]["d"] for k in ks]
    known = [(k, best[k]["d"]) for k in ks if best[k]["settled"]]
    mono = all(a[1] >= b[1] for a, b in zip(known, known[1:]))
    out["P1"] = "fail" if not mono else ("pass" if settled else "incomplete")
    n = rec["n"]
    cap = 2 * math.floor(P2_CONSTANT * math.sqrt(n) / 2)
    dmax = max(d for d in ds if d is not None)
    out["P2"] = "fail" if dmax > cap else ("pass" if settled else "incomplete")
    out["P2_values"] = {"d_max": dmax, "cap": cap}
    score = max(k * best[k]["d"] ** 2 / n for k in ks if best[k]["d"] is not None)
    limit = P3_RANDOM if rec["group"] == "random" else P3_EXTRAPOLATION
    out["P3"] = "fail" if score > limit + 1e-9 else ("pass" if settled else "incomplete")
    out["P3_values"] = {"score": round(score, 4), "limit": limit}
    if (rec["l"], rec["m"]) == P4_TORUS:
        b = best.get(P4_K)
        out["P4"] = ("incomplete" if b is None or not b["settled"]
                     else "pass" if b["d"] == P4_D else "fail")  # fmt: skip
        out["P4_values"] = b
    return out


def decide(rows: list[dict], registered: list[dict]) -> dict:
    t = tori()
    judged = {(r["l"], r["m"]): judge_torus(r) for r in rows if r.get("job") == "torus"}
    parts = {}
    for p in ("P0", "P1", "P2", "P3"):
        vals = [judged[x].get(p) for g in ("random", "extrapolation") for x in t[g]
                if x in judged]  # fmt: skip
        missing = sum(1 for g in ("random", "extrapolation") for x in t[g] if x not in judged)
        parts[p] = ("fail" if "fail" in vals else "incomplete" if missing or "incomplete" in vals
                    else "pass")  # fmt: skip
    p4 = judged.get(P4_TORUS, {}).get("P4")
    parts["P4"] = p4 or "incomplete"
    problems = []
    hashes = code_hashes()
    for r in rows:
        if r.get("settings") != SETTINGS:
            problems.append(f"{r.get('l')}x{r.get('m')}: other settings")
        for k, v in r.get("sha256", {}).items():
            if v != hashes[k]:
                problems.append(f"{r['l']}x{r['m']}: another {k}")
    if registered and registered[-1].get("sha256") not in (None, hashes):
        problems.append("the code differs from the registration")
    parts["H"] = "fail" if problems else "pass"
    vals = list(parts.values())
    verdict = "fail" if "fail" in vals else "hold" if all(v == "pass" for v in vals) else \
        "incomplete"  # fmt: skip
    exposed = {f"{x[0]}x{x[1]}": judged[x] for x in t["exposed"] if x in judged}
    return {"verdict": verdict, **parts, "problems": problems,
            "per_torus": {f"{a}x{b}": v for (a, b), v in judged.items()},
            "exposed": exposed}  # fmt: skip


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
