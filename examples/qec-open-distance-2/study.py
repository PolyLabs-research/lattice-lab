"""
A registered test of the packing cut (search_pack.c, pack.py) and, with it, a lower bound on the
distance of [[756,16,<=34]] beyond the 24 of examples/qec-open-distance.

    uv run --no-sync python examples/qec-open-distance-2/study.py register
    uv run --no-sync python examples/qec-open-distance-2/study.py run --workers 4
    uv run --no-sync python examples/qec-open-distance-2/study.py resume --workers 4  (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-open-distance-2

**Where the cut came from.** A consultation (consultations/2026-10-23-756-symmetry, Claude Fable,
$1.12) found what our own check confirmed: the code's automorphism group is its 378 translations,
which the search already uses, so symmetry cannot speed it up. It proposed a stronger admissible
cut: the unsatisfied checks whose candidate sets are pairwise disjoint each need a qubit of their
own. In development (that consultation's checks.md) the cut cut nodes 130 times and time 24
times on [[756,16]] at bound 20, and agreed with enumeration on 150 small codes and with the
unpacked search on 24 codes up to d = 12.

**The parts.**
- **A1, against enumeration (registered, decisive).** A1_PER_SIZE fresh codes at each size of
  A1_SIZES (none used in the cut's development, nor isomorphic to one), A and B each three
  distinct random monomials, k > 0 and lm + k/2 <= distance.BRUTE_CAP. For each: distance_brute
  (kind Z), and the packing search, deepening from 2, from (0, lm) and from every qubit, with
  A_PARTS parts. Prediction: both searches give the enumeration's d.
- **A2, against the unpacked search (registered, decisive).** A2_PER_SIZE fresh codes of the
  published trinomial form at each size of A2_SIZES, k > 0, with every exponent nonzero and
  terms whose differences generate the torus (`generates`: no disjoint copies of a smaller
  code). For each: the packing search and the unpacked search (study 1's search_parts.c),
  both deepening from 2 from (0, lm), with a limit of A2_LIMIT each. Prediction: their
  intervals meet, and where both complete they give the same d; reported apart, how often both
  complete, and the packing search's speedup.
- **B, known answers (not blind).** The gross code [[144,12,12]] and [[288,12,18]] (published,
  d known), and [[360,12]] (d = 24, study 1), each by the packing search from (0, lm) with
  PARTS parts: passes deepening from 2 find their first logical at weight 12 and 18, and for
  [[360,12]] the passes up to 24 find nothing (its witness of weight 24 is study 1's).
- **C, [[756,16]] (registered).** The packing search from (0, lm), PARTS parts, passes b = 2, 3,
  ... up to 34 (the window's witness, study 1), with a budget of C_BUDGET seconds of wall clock
  over the passes that finished. d is even (A and B have odd weight), so a pass at b without a
  find gives d >= b rounded up to even.
  - C1 (decisive): no pass finds a logical below 30; a find at w < 30 gives d = w, which refutes
    the claimed d >= 30 and fails C1.
  - C2 (the cost, decisive): the pass at 29 finishes within the budget, so d >= 30. Estimated
    from development: about 8 hours to there, the passes growing about 2.8 times per bound.
  - Reported: the largest finished pass, and so the lower bound reached; a find at 30 to 33 gives
    d exactly.

**The verdict.** "hold" when A1, A2 and B pass and C1 and C2 hold; "fail" when any fails (A or B
an instrument failure, C1 a find below 30, C2 a budget that ends before the pass at 29, H a record
made otherwise than registered); "incomplete" when jobs are missing and nothing has failed.

**What it rests on.** As study 1, plus the packing argument (search_pack.c's docstring). A1 and
A2 test the cut on codes it was not developed on; B checks known values; nothing certifies C's
lower bound beyond the argument and those tests.

**Development (excluded_seen).** The cut was developed on the codes of the consultation's
checks.md: 150 random weight-3 codes at 3x4, 3x7, 4x6, 2x9, 3x6, 3x8 and 6x3 (seed 7), the
published entries of n <= 300 but 288, 20 random trinomials at 6x9, 5x12 and 4x15 (seed 5), and
passes at bounds 15 to 18 of [[288,12,18]] and 17 to 20 of [[756,16]] (whose answers, no find,
study 1 had recorded).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
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


pack = _load("qec_open_pack", HERE / "pack.py")
bb, distance = pack.bb, pack.distance

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-open-distance-2"
KIND = "Z"
A1_SIZES = [(2, 6), (2, 7), (3, 5)]  # Z2xZ2xZ3, Z14, Z15: no development torus
A1_PER_SIZE = 30
A_PARTS = 4
A2_SIZES = [(6, 12), (6, 15), (9, 12), (9, 10), (10, 12)]
A2_PER_SIZE = 4
A2_LIMIT = 1200.0
PARTS = 16
DEPTH = 6
C_BUDGET = 108000.0
KNOWN = {
    "144": {"l": 12, "m": 6, "A": [[3, 0], [0, 1], [0, 2]], "B": [[0, 3], [1, 0], [2, 0]],
            "d": 12},
    "288": {"l": 12, "m": 12, "A": [[3, 0], [0, 2], [0, 7]], "B": [[0, 3], [1, 0], [2, 0]],
            "d": 18},
    "360": {"l": 30, "m": 6, "A": [[9, 0], [0, 1], [0, 2]], "B": [[0, 3], [25, 0], [26, 0]],
            "d": 24},
}  # fmt: skip
TARGET = {"l": 21, "m": 18, "A": [[3, 0], [0, 10], [0, 17]], "B": [[0, 5], [3, 0], [19, 0]],
          "k": 16, "last": 34}  # fmt: skip
SETTINGS = {"kind": KIND, "parts": PARTS, "depth": DEPTH, "a_parts": A_PARTS,
            "a2_limit": A2_LIMIT, "c_budget": C_BUDGET, "anchors": "(0, lm)"}  # fmt: skip
HASHED = {
    "search_pack_c": pack.SEARCH_C,
    "pack_py": HERE / "pack.py",
    "study_py": HERE / "study.py",
    "parts_py": pack.OPEN / "parts.py",
    "search_parts_c": pack.plain.SEARCH_C,
    "distance_py": Path(distance.__file__),
    "bb_py": Path(bb.__file__),
    "tests_py": ROOT / "tests" / "test_qec_open_distance_2.py",
}
EXCLUDED_SEEN = [
    "the cut's development: consultations/2026-10-23-756-symmetry/checks.md (150 random weight-3 "
    "codes at 3x4, 3x7, 4x6, 2x9, 3x6, 3x8, 6x3; the published entries of n <= 300 but 288; 20 "
    "random trinomials at 6x9, 5x12, 4x15; passes 15-18 of [[288,12,18]] and 17-20 of "
    "[[756,16]], answers already recorded by study 1)",
    "tests/test_qec_open_distance_2.py: the gross code and random codes at the development sizes",
    "study 1 (examples/qec-open-distance): [[756,16]] has no logical below 24 and a checked one "
    "of weight 34; [[360,12]] has d = 24",
]
SEEN_CLAIMS = [
    "[[756,16]]: a lower bound of 30 claimed by a tool called DistQLDPC (one engine, not "
    "cross-validated), as summarised secondhand before study 1; not read directly",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_hashes() -> dict[str, str]:
    return {name: _sha256_file(path) for name, path in HASHED.items()}


def _poly(terms) -> list[tuple[int, int]]:
    return [tuple(t) for t in terms]


def _seed(name: str) -> int:
    return int(hashlib.sha256(f"{ID}:{name}".encode()).hexdigest()[:16], 16)


def a1_codes() -> list[dict]:
    out = []
    for ell, m in A1_SIZES:
        rng, found, seen = random.Random(_seed(f"A1:{ell}x{m}")), [], set()
        while len(found) < A1_PER_SIZE:
            A = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
            B = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
            if len(A) < 3 or len(B) < 3 or (tuple(A), tuple(B)) in seen:
                continue
            k = bb.k_linalg(A, B, ell, m)
            if k == 0 or ell * m + k // 2 > distance.BRUTE_CAP:
                continue
            seen.add((tuple(A), tuple(B)))
            found.append({"key": f"A1:{ell}x{m}:{len(found)}", "l": ell, "m": m, "k": k,
                          "A": [list(t) for t in A], "B": [list(t) for t in B]})  # fmt: skip
        out += found
    return out


def generates(A, B, ell: int, m: int) -> bool:
    """True when the differences of A's terms and of B's terms generate Z_l x Z_m, so that the
    code is not a disjoint union of copies of a code on a smaller torus."""
    steps = {((p[0] - q[0]) % ell, (p[1] - q[1]) % m) for P in (A, B) for p in P for q in P}
    reached, frontier = {(0, 0)}, [(0, 0)]
    while frontier:
        x = frontier.pop()
        for g in steps:
            y = ((x[0] + g[0]) % ell, (x[1] + g[1]) % m)
            if y not in reached:
                reached.add(y)
                frontier.append(y)
    return len(reached) == ell * m


def a2_codes() -> list[dict]:
    out = []
    for ell, m in A2_SIZES:
        rng, found, seen = random.Random(_seed(f"A2:{ell}x{m}")), [], set()
        while len(found) < A2_PER_SIZE:
            a, e, f = (rng.randrange(1, ell) for _ in range(3))
            b, c, d = (rng.randrange(1, m) for _ in range(3))
            A, B = [(a, 0), (0, b), (0, c)], [(0, d), (e, 0), (f, 0)]
            if len(set(A)) < 3 or len(set(B)) < 3 or (tuple(A), tuple(B)) in seen:
                continue
            if not generates(A, B, ell, m):
                continue
            k = bb.k_linalg(A, B, ell, m)
            if k == 0:
                continue
            seen.add((tuple(A), tuple(B)))
            found.append({"key": f"A2:{ell}x{m}:{len(found)}", "l": ell, "m": m, "k": k,
                          "A": [list(t) for t in A], "B": [list(t) for t in B]})  # fmt: skip
        out += found
    return out


def question() -> dict:
    return {
        "id": ID,
        "title": "A packing cut for the exhaustive distance search, tested, and a lower bound on "
        "the distance of [[756,16,<=34]]",
        "statement": "Does the packing cut keep the search exact (against enumeration and the "
        "unpacked search on fresh codes, and on known distances), and does it reach d >= 30 for "
        "[[756,16]] within the budget, finding nothing below 30?",
        "consultation": "consultations/2026-10-23-756-symmetry",
        "a1_codes": a1_codes(),
        "a2_codes": a2_codes(),
        "known": KNOWN,
        "target": TARGET,
        "settings": SETTINGS,
        "sha256": code_hashes(),
        "excluded_seen": EXCLUDED_SEEN,
        "seen_claims": SEEN_CLAIMS,
    }


def predictions() -> list[dict]:
    return [
        {"part": "A1", "predict": "the packing search, from (0, lm) and from every qubit, gives "
         "distance_brute's d on every A1 code"},
        {"part": "A2", "predict": "the packing and unpacked searches' intervals meet on every A2 "
         "code, and give the same d where both complete"},
        {"part": "B", "predict": "the packing search gives d = 12 for [[144,12,12]] and 18 for "
         "[[288,12,18]], and its passes up to 24 find nothing on [[360,12]]"},
        {"part": "C1", "predict": "no pass on [[756,16]] finds a logical below 30"},
        {"part": "C2", "predict": "the pass at 29 on [[756,16]] finishes within the budget, so "
         "d >= 30", "estimate_hours_to_29": 8},
        {"part": "H", "predict": "every record was made by the registered settings and code",
         "settings": SETTINGS, "sha256": code_hashes()},
    ]  # fmt: skip


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for _, _, line in record_lines(Path(path))]


def _record(code: dict, result: dict) -> dict:
    keep = ("status", "d", "lower", "upper", "witness", "seconds", "first", "last", "parts",
            "depth", "anchors", "search_c", "search_c_sha256")  # fmt: skip
    return {key: result.get(key) for key in keep} | {
        "nodes": sum(x["nodes"] or 0 for p in result["passes"] for x in p["parts"])
    }


def execute(path: Path, workers: int, budget: float | None = None) -> None:
    budget = C_BUDGET if budget is None else budget
    done = {r["key"] for r in _rows(path) if "key" in r}
    for code in a1_codes():
        if code["key"] in done:
            continue
        A, B, ell, m = _poly(code["A"]), _poly(code["B"]), code["l"], code["m"]
        lm = ell * m
        runs = {"brute": pack.brute(A, B, ell, m, KIND)}
        for name, anchors in (("pack_lm", (0, lm)), ("pack_all", None)):
            r = pack.search(A, B, ell, m, KIND, anchors=anchors, parts=A_PARTS, depth=3,
                            workers=workers, time_limit=600)  # fmt: skip
            runs[name] = _record(code, r)
        append_records(path, [{"job": "A1", "key": code["key"], "id": ID, **code, "runs": runs}])
    for code in a2_codes():
        if code["key"] in done:
            continue
        A, B, ell, m = _poly(code["A"]), _poly(code["B"]), code["l"], code["m"]
        runs = {}
        for name, fn in (("pack", pack.search), ("plain", pack.reference)):
            r = fn(A, B, ell, m, KIND, anchors=(0, ell * m), parts=A_PARTS, depth=DEPTH,
                   workers=workers, time_limit=A2_LIMIT)  # fmt: skip
            runs[name] = _record(code, r)
        append_records(path, [{"job": "A2", "key": code["key"], "id": ID, **code, "runs": runs}])
    for name, code in KNOWN.items():
        key = f"B:{name}"
        if key in done:
            continue
        A, B, ell, m = _poly(code["A"]), _poly(code["B"]), code["l"], code["m"]
        last = code["d"] if name == "360" else distance.SEARCH_BOUND
        r = pack.search(A, B, ell, m, KIND, anchors=(0, ell * m), last=last, parts=PARTS,
                        depth=DEPTH, workers=workers, time_limit=36000)  # fmt: skip
        append_records(path, [{"job": "B", "key": key, "id": ID, "code": name,
                               **_record(code, r)}])  # fmt: skip
    rows = _rows(path)
    if any(r.get("job") == "C_end" for r in rows):
        return
    A, B, ell, m = _poly(TARGET["A"]), _poly(TARGET["B"]), TARGET["l"], TARGET["m"]
    passes = [r for r in rows if r.get("job") == "C_pass"]
    used = sum(p["seconds"] for p in passes)
    first = passes[-1]["bound"] + 1 if passes else 2
    if passes and passes[-1]["found"] or first > TARGET["last"]:
        result = {"status": "complete" if passes and passes[-1]["found"] else "bound"}
    else:

        def on_pass(entry):
            sha = pack.sha256(pack.SEARCH_C)
            append_records(path, [{"job": "C_pass", "id": ID, "settings": SETTINGS,
                                   "search_c_sha256": sha, **entry}])  # fmt: skip

        result = pack.search(A, B, ell, m, KIND, anchors=(0, ell * m), first=first,
                             last=TARGET["last"], parts=PARTS, depth=DEPTH, workers=workers,
                             time_limit=budget - used, on_pass=on_pass)  # fmt: skip
    append_records(path, [{"job": "C_end", "id": ID, "first": first, "budget": budget,
                           "used_before": used, "settings": SETTINGS,
                           **{key: result.get(key) for key in ("status", "seconds",
                                                               "search_c_sha256")}}])  # fmt: skip


def _a1(rows: list[dict]) -> tuple[str, list[str]]:
    rows_ = [r for r in rows if r.get("job") == "A1"]
    bad = []
    for r in rows_:
        want = r["runs"]["brute"]
        for name in ("pack_lm", "pack_all"):
            got = r["runs"][name]
            if got["status"] != "complete" or got["d"] != want:
                bad.append(f"{r['key']} {name}: {got['status']} d = {got['d']}, brute {want}")
    if bad:
        return "fail", bad
    return ("pass" if len(rows_) == len(a1_codes()) else "incomplete"), bad


def _interval(run: dict) -> tuple[int, float]:
    lo = run["lower"] if run["lower"] is not None else 1
    hi = run["upper"] if run["upper"] is not None else float("inf")
    return lo, hi


def _a2(rows: list[dict]) -> tuple[str, list[str], dict]:
    rows_ = [r for r in rows if r.get("job") == "A2"]
    bad, both, speed = [], 0, []
    for r in rows_:
        p, q = r["runs"]["pack"], r["runs"]["plain"]
        (lp, hp), (lq, hq) = _interval(p), _interval(q)
        if max(lp, lq) > min(hp, hq):
            bad.append(f"{r['key']}: [{lp}, {hp}] and [{lq}, {hq}] do not meet")
        if p["status"] == q["status"] == "complete":
            both += 1
            if p["d"] != q["d"]:
                bad.append(f"{r['key']}: d {p['d']} and {q['d']}")
            speed.append(round(q["seconds"] / max(p["seconds"], 1e-3), 1))
    status = "fail" if bad else ("pass" if len(rows_) == len(a2_codes()) else "incomplete")
    return status, bad, {"both_complete": both, "of": len(rows_), "speedups": speed}


def _b(rows: list[dict]) -> tuple[str, list[str]]:
    bad, have = [], {r["code"]: r for r in rows if r.get("job") == "B"}
    for name, code in KNOWN.items():
        r = have.get(name)
        if r is None:
            continue
        if name == "360":
            if r["status"] != "bound" or r["lower"] != 24:
                bad.append(f"360: {r['status']}, lower {r['lower']}")
        elif r["status"] != "complete" or r["d"] != code["d"]:
            bad.append(f"{name}: {r['status']}, d = {r['d']}")
    if bad:
        return "fail", bad
    return ("pass" if len(have) == len(KNOWN) else "incomplete"), bad


def _c(rows: list[dict]) -> dict:
    passes = [r for r in rows if r.get("job") == "C_pass"]
    end = next((r for r in rows if r.get("job") == "C_end"), None)
    problems = []
    if [p["bound"] for p in passes] != list(range(2, 2 + len(passes))):
        problems.append("C: the passes are not consecutive from 2")
    A, B = _poly(TARGET["A"]), _poly(TARGET["B"])
    found = next((p for p in passes if p["found"]), None)
    if found:
        check = distance.verify_witness(A, B, TARGET["l"], TARGET["m"], KIND, found["witness"])
        if not check["logical"] or check["weight"] != found["least"]:
            problems.append("C: the find's witness fails verify_witness")
    lower = max((p["bound"] for p in passes if not p["found"]), default=None)
    even = None if lower is None else lower + lower % 2
    d = found["least"] if found else None
    c1 = "fail" if d is not None and d < 30 else ("pass" if end or (lower and lower >= 29) else
                                                    "incomplete")  # fmt: skip
    if d is not None and d >= 30 or lower is not None and lower >= 29:
        c2 = "pass"
    elif end:
        c2 = "fail"
    else:
        c2 = "incomplete"
    return {
        "C1": c1,
        "C2": c2,
        "largest_pass_without_find": lower,
        "d_at_least": d or even,
        "d": d,
        "passes": len(passes),
        "status": end["status"] if end else None,
        "seconds": round(sum(p["seconds"] for p in passes), 1),
        "problems": problems,
    }


def _h(rows: list[dict], registered: list[dict]) -> list[str]:
    problems, hashes = [], code_hashes()
    for r in rows:
        if r.get("job") in ("A1", "A2", "B"):
            runs = r["runs"].values() if "runs" in r else [r]
            for x in runs:
                if not isinstance(x, dict):
                    continue
                want = hashes["search_pack_c"] if x["search_c"] == "search_pack.c" else \
                    hashes["search_parts_c"]  # fmt: skip
                if x["search_c_sha256"] != want:
                    problems.append(f"{r['key']}: ran another {x['search_c']}")
        if r.get("job") in ("C_pass", "C_end"):
            if r.get("settings") != SETTINGS:
                problems.append(f"{r['job']}: other settings")
            if r.get("search_c_sha256") not in (None, hashes["search_pack_c"]):
                problems.append(f"{r['job']}: ran another search_pack.c")
        if r.get("job") == "C_end" and r.get("budget") != C_BUDGET:
            problems.append("C: the budget is not the registered one")
    if registered and registered[-1].get("sha256") not in (None, hashes):
        problems.append("the code differs from the registration")
    return problems


def decide(rows: list[dict], registered: list[dict]) -> dict:
    a1, a1_bad = _a1(rows)
    a2, a2_bad, a2_info = _a2(rows)
    b, b_bad = _b(rows)
    c = _c(rows)
    h_problems = _h(rows, registered) + c["problems"]
    h = "fail" if h_problems else "pass"
    parts_ = {"A1": a1, "A2": a2, "B": b, "C1": c["C1"], "C2": c["C2"], "H": h}
    if "fail" in parts_.values():
        verdict = "fail"
    elif all(v == "pass" for v in parts_.values()):
        verdict = "hold"
    else:
        verdict = "incomplete"
    return {"verdict": verdict, **parts_, "A1_problems": a1_bad, "A2_problems": a2_bad,
            "A2_report": a2_info, "B_problems": b_bad, "C": c,
            "H_problems": h_problems}  # fmt: skip


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
