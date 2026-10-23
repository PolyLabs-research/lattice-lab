"""
A registered attempt at the distances of the two larger published bivariate bicycle codes whose
d the source gives only as an upper bound: [[360,12,<=24]] and [[756,16,<=34]] (Bravyi et al.
2024, Table 3).

    uv run --no-sync python examples/qec-open-distance/study.py register
    uv run --no-sync python examples/qec-open-distance/study.py run --workers 4
    uv run --no-sync python examples/qec-open-distance/study.py resume --workers 4   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-open-distance

**The codes** (CODES; sources in the question). [[360,12]]: l = 30, m = 6, A = x^9 + y + y^2,
B = y^3 + x^25 + x^26. [[756,16]]: l = 21, m = 18, A = x^3 + y^10 + y^17, B = y^5 + x^3 + x^19.
They were read from text copies of the paper's table (arXiv, Nature and Zenodo were not
reachable from this session), and their k (12 and 16, by bb.k_linalg) was computed when they
were sourced: k is known, not predicted. Nothing else was computed on either code before this
registration. Later work claims, secondhand (not read from the works themselves), that d = 24
for [[360,12]], and 30 <= d <= 34 for [[756,16]]; those claims were seen before registration
and are recorded in the question, so the 360 prediction is not blind to them.

**The instruments** (parts.py, which builds on examples/qec-distance's distance.py; the
module docstring of parts.py gives the arguments). For each code, kind Z only: d_X = d_Z for
every bivariate bicycle code (distance.py's module docstring).

1. The window (window.c): an upper bound with a checked witness, by random information sets,
   WINDOW_SEEDS seeds of WINDOW_SECONDS each, in parallel.
2. The split search (search_parts.c, examples/qec-distance's search.c with a split): passes
   b = 2, 3, ..., each shared among PARTS processes at split depth DEPTH, from anchors (0, lm)
   (distance_ilp's translation argument), at most --workers at once, up to the window's upper
   bound U: a pass at b without a find shows d >= b, so a pass at U without one shows d = U;
   a pass with a find gives d exactly. The search has a budget of SEARCH_BUDGET seconds of wall
   clock per code, counted over the passes that finished (a pass cut off by a stop or by the
   budget is not counted, and resume runs it again from its start).

The integer program (distance_ilp) is not used: at n = 288 it stopped at 90 minutes with
13 <= d <= 18 (examples/qec-distance), so at these sizes its lower bound would be far below the
search's.

**The predictions.**
- H1 ([[360,12]]): the window finds a logical of weight 24 and none lighter, and the search's
  passes up to 24 find nothing, within the budget: d = 24. Fails on a lighter logical (window or
  search), or a window least weight above 24 (24 not reached); incomplete when the search's
  budget ends before its pass at 24 finishes.
- H2 ([[756,16]], upper bound): the window's least weight is 34. Fails otherwise (a lighter
  logical would improve the published bound; a heavier least means the window did not reach it).
- H3 ([[756,16]], lower bound, reported and not judged): the search's passes find nothing below
  34, and the largest finished pass is estimated at 18 to 24, from the growth of the passes'
  work on [[288,12,18]] (about 11 times per 2 of bound, with n larger here). A find is reported
  as d exactly, and would fail H2 too, being lighter than 34.
- H4 (the instruments): every witness passes verify_witness; each code's k is the source's; the
  search's passes are consecutive from 2 and no pass's least weight is below an earlier pass's
  bound; and every record was made by the registered settings.

**The verdict.** "hold" when H1, H2 and H4 pass; "fail" when any fails; "incomplete" when
nothing fails and H1 is incomplete or a job is missing.

**Running it.** execute does the windows of both codes, then the search of [[360,12]], then of
[[756,16]], appending a record for each window, each finished pass, and each search's end.
resume skips what has a record and starts each search at the pass after its last. The budgets
are wall clock, so other load lowers what the search reaches: run it when nothing else heavy
shares the machine. At 4 workers the windows take about an hour; the searches up to their
budgets.

**Development (excluded_seen).** The instruments were developed and timed on [[288,12,18]] and
the gross code (published, d known) and on random small codes (tests/test_qec_open_distance.py),
never on the two codes here.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    """A module from its file, registered under `name` (once per process)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


parts = _load("qec_open_parts", HERE / "parts.py")
bb, distance = parts.bb, parts.distance

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-open-distance-1"
CODES = {
    "360": {"name": "[[360,12,<=24]]", "l": 30, "m": 6, "A": [[9, 0], [0, 1], [0, 2]],
            "B": [[0, 3], [25, 0], [26, 0]], "k": 12, "published_upper": 24},
    "756": {"name": "[[756,16,<=34]]", "l": 21, "m": 18, "A": [[3, 0], [0, 10], [0, 17]],
            "B": [[0, 5], [3, 0], [19, 0]], "k": 16, "published_upper": 34},
}  # fmt: skip
ORDER = ("360", "756")
KIND = "Z"
WINDOW_SEEDS = (0, 1, 2, 3)
WINDOW_SECONDS = 1800.0
PARTS = 16
DEPTH = 6
SEARCH_BUDGET = {"360": 36000.0, "756": 28800.0}
SETTINGS = {"kind": KIND, "window_seeds": list(WINDOW_SEEDS), "window_seconds": WINDOW_SECONDS,
            "parts": PARTS, "depth": DEPTH, "search_budget": SEARCH_BUDGET,
            "anchors": "(0, lm)"}  # fmt: skip
HASHED = {
    "parts_py": HERE / "parts.py",
    "search_parts_c": parts.SEARCH_C,
    "window_c": parts.WINDOW_C,
    "study_py": HERE / "study.py",
    "distance_py": Path(distance.__file__),
    "bb_py": Path(bb.__file__),
    "tests_py": ROOT / "tests" / "test_qec_open_distance.py",
}
SOURCES = [
    "Bravyi, Cross, Gambetta, Maslov, Rall, Yoder, 'High-threshold and low-overhead "
    "fault-tolerant quantum memory', Nature 627 (2024), arXiv:2308.07915, Table 3: the codes "
    "and the bounds d <= 24 and d <= 34 (read from text copies, below; the paper itself was "
    "not reachable from this session)",
    "github.com/Omer-Sella/qecc, polynomialCodes.py: a copy of Table 3's polynomials",
    "the LaTeX source of a later paper by Chen et al. listing the same codes",
    "github.com/QEC-pages/dist-m4ri, BENCHMARK.md: the codes in a distance benchmark",
    "github.com/gongaa/SlidingWindowDecoder: the codes' polynomials in a decoder repository",
]
SEEN_CLAIMS = [
    "[[360,12]]: d = 24 exactly, claimed by later work (Zenodo 10.5281/zenodo.23352655; a "
    "'DistQLDPC' tool, 1993 s; Zenodo 23382175), as summarised by the sourcing agent, not "
    "read directly",
    "[[756,16]]: open; DistQLDPC claims a lower bound of 30 (one engine, not cross-validated) "
    "and the upper bound 34, as summarised by the sourcing agent, not read directly",
]
EXCLUDED_SEEN = [
    "k of both codes by bb.k_linalg (12 and 16), when they were sourced",
    "parts.py's instruments developed and timed on [[288,12,18]] (search from (0, 144) to "
    "d = 18 in 23 s unsplit, 14 s at 8 parts; window weight 18 in 30 s at each of 4 seeds) "
    "and on the gross code [[144,12,12]], both published with d known",
    "tests/test_qec_open_distance.py: random small codes (3x4, 3x7, 4x6, 2x9, 3x6, 3x8) and "
    "the gross code",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_hashes() -> dict[str, str]:
    return {name: _sha256_file(path) for name, path in HASHED.items()}


def _poly(terms) -> list[tuple[int, int]]:
    return [tuple(t) for t in terms]


def _code(key: str):
    c = CODES[key]
    return _poly(c["A"]), _poly(c["B"]), c["l"], c["m"]


def question() -> dict:
    return {
        "id": ID,
        "title": "The distances of the published bivariate bicycle codes [[360,12,<=24]] and "
        "[[756,16,<=34]]",
        "statement": "By a split exhaustive search (lower bounds, exact when it meets an upper "
        "bound) and random information sets (upper bounds with checked witnesses), within a "
        "stated budget: is d = 24 for [[360,12]], and is 34 the least weight found for "
        "[[756,16]], and how far up does an exhaustive lower bound reach?",
        "codes": CODES,
        "sources": SOURCES,
        "seen_claims": SEEN_CLAIMS,
        "settings": SETTINGS,
        "sha256": code_hashes(),
        "excluded_seen": EXCLUDED_SEEN,
        "no_computation_before": "nothing but k was computed on either code before this "
        "registration",
    }


def predictions() -> list[dict]:
    return [
        {"part": "H1", "code": "360", "predict": "d = 24: the window's least weight is 24 and "
         "the search's passes up to 24 find nothing within the budget", "d": 24},
        {"part": "H2", "code": "756", "predict": "the window's least weight is 34",
         "upper": 34},
        {"part": "H3", "code": "756", "predict": "reported, not judged: the search finds "
         "nothing below 34, and its largest finished pass is 18 to 24", "lower_range": [18, 24]},
        {"part": "H4", "predict": "every witness passes verify_witness; each k is the "
         "source's; passes are consecutive from 2; every record was made by the registered "
         "settings", "settings": SETTINGS, "sha256": code_hashes()},
    ]  # fmt: skip


def _rows(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    return [json.loads(line) for _, _, line in record_lines(Path(path))]


def execute(path: Path, workers: int, budget: dict | None = None, seconds=None) -> None:
    """The windows of both codes, then each code's search, skipping what has a record."""
    budget = budget or SEARCH_BUDGET
    seconds = WINDOW_SECONDS if seconds is None else seconds
    rows = _rows(path)
    for key in ORDER:
        if any(r["job"] == "window" and r["code"] == key for r in rows):
            continue
        A, B, ell, m = _code(key)
        w = parts.window(A, B, ell, m, KIND, seeds=WINDOW_SEEDS, seconds=seconds,
                         workers=workers)  # fmt: skip
        append_records(path, [{"job": "window", "code": key, "id": ID, **w}])
    rows = _rows(path)
    for key in ORDER:
        if any(r["job"] == "search_end" and r["code"] == key for r in rows):
            continue
        A, B, ell, m = _code(key)
        upper = next(r["upper"] for r in rows if r["job"] == "window" and r["code"] == key)
        done = [r for r in rows if r["job"] == "pass" and r["code"] == key]
        used = sum(r["seconds"] for r in done)
        first = done[-1]["bound"] + 1 if done else 2
        last = upper if upper is not None else distance.SEARCH_BOUND

        def on_pass(entry, key=key):
            append_records(path, [{"job": "pass", "code": key, "id": ID, **entry}])

        if done and done[-1]["found"]:
            result = {"status": "complete"}
        elif first > last:
            result = {"status": "bound"}
        else:
            result = parts.search(A, B, ell, m, KIND, anchors=(0, ell * m), first=first,
                                  last=last, parts=PARTS, depth=DEPTH, workers=workers,
                                  time_limit=budget[key] - used, on_pass=on_pass)  # fmt: skip
        summary = {key2: result.get(key2) for key2 in ("status", "seconds", "compiler",
                                                        "search_parts_c_sha256")}  # fmt: skip
        append_records(path, [{"job": "search_end", "code": key, "id": ID, "first": first,
                               "last": last, "budget": budget[key], "used_before": used,
                               **summary}])  # fmt: skip
        rows = _rows(path)


def summarise(rows: list[dict], key: str) -> dict:
    """One code's bounds from its records: the window's upper, the search's passes, and d."""
    A, B, ell, m = _code(key)
    window = next((r for r in rows if r["job"] == "window" and r["code"] == key), None)
    passes = [r for r in rows if r["job"] == "pass" and r["code"] == key]
    end = next((r for r in rows if r["job"] == "search_end" and r["code"] == key), None)
    problems = []
    for r in [window, *passes]:
        if r and r.get("witness"):
            check = distance.verify_witness(A, B, ell, m, KIND, r["witness"])
            want = r.get("upper", r.get("least"))
            if not check["logical"] or check["weight"] != want:
                problems.append(f"{key}: a witness fails verify_witness")
    if window and window["k"] != CODES[key]["k"]:
        problems.append(f"{key}: k = {window['k']}, the source's is {CODES[key]['k']}")
    if [p["bound"] for p in passes] != list(range(2, 2 + len(passes))):
        problems.append(f"{key}: the passes are not consecutive from 2")
    for i, p in enumerate(passes):
        if p["found"] and (i != len(passes) - 1 or p["least"] < p["bound"] - 1):
            problems.append(f"{key}: pass {p['bound']} found weight {p['least']}")
        if p["parts"] and len(p["parts"]) != PARTS:
            problems.append(f"{key}: pass {p['bound']} has {len(p['parts'])} parts")
    if window and (window["runs"] and [x["seed"] for x in window["runs"]] != list(WINDOW_SEEDS)
                   or window["seconds"] != WINDOW_SECONDS):  # fmt: skip
        problems.append(f"{key}: the window was not run with the registered settings")
    upper = window["upper"] if window else None
    lower = max((p["bound"] for p in passes if not p["found"]), default=None)
    found = next((p["least"] for p in passes if p["found"]), None)
    if found is not None:
        d = found
    elif upper is not None and lower is not None and lower >= upper:
        d = upper
    else:
        d = None
    if found is not None and upper is not None and found > upper:
        problems.append(f"{key}: the search found {found}, above the window's {upper}")
    return {"code": key, "window_upper": upper, "lower": d if d is not None else lower,
            "upper": min(x for x in (upper, found) if x is not None) if (upper or found) else None,
            "d": d, "passes": len(passes), "search_status": end["status"] if end else None,
            "search_seconds": round(sum(p["seconds"] for p in passes), 1),
            "problems": problems}  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    s = {key: summarise(rows, key) for key in ORDER}
    problems = [p for key in ORDER for p in s[key]["problems"]]
    if registered and registered[-1].get("sha256") not in (None, code_hashes()):
        problems.append("the code differs from the registration")
    a = s["360"]
    if a["upper"] is not None and a["upper"] < 24:
        h1 = "fail"
    elif a["window_upper"] is not None and a["window_upper"] > 24:
        h1 = "fail"
    elif a["d"] == 24:
        h1 = "pass"
    else:
        h1 = "incomplete"
    b = s["756"]
    if b["window_upper"] is None:
        h2 = "incomplete"
    else:
        h2 = "pass" if b["window_upper"] == 34 else "fail"
    h3 = {"lower": b["lower"], "found_below_34": b["d"] is not None and b["d"] < 34,
          "in_range": b["lower"] is not None and 18 <= b["lower"] <= 24}  # fmt: skip
    h4 = "fail" if problems else "pass"
    ended = all(any(r["job"] == "search_end" and r["code"] == k for r in rows) for k in ORDER)
    if "fail" in (h1, h2, h4):
        verdict = "fail"
    elif h1 == "pass" and h2 == "pass" and ended:
        verdict = "hold"
    else:
        verdict = "incomplete"
    return {"verdict": verdict, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "problems": problems,
            "codes": s}  # fmt: skip


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
