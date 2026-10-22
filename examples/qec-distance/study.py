"""
A registered rediscovery test: the published distances of the twelve bivariate bicycle codes in
../qec-bb/codes.json, by two exact methods, integer programming and an exhaustive search.

    uv run --no-sync python examples/qec-distance/study.py register
    uv run --no-sync python examples/qec-distance/study.py run --workers 4
    uv run --no-sync python examples/qec-distance/study.py resume --workers 4   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-distance

Step 2 of docs/next-direction.md begins with distance, which nothing in the project computed
before. distance.py computes the least weight of a Z-logical, d_Z, with one integer program
solved by SCIP; for every bivariate bicycle code d_X = d_Z (distance.py's docstring), so that
is the code's distance d. This test checks the method, then applies it to the published codes.

1. **Method (registered, all decisive).**
   (a) On 200 random codes, 25 at each of the 8 sizes in METHOD_SIZES, the program's d_Z
       equals the enumeration's (distance_brute, which shares no code with the program but
       bb's matrices), and the program's d_X equals its d_Z. The sizes are of no published
       torus type, and development ran no random code at any of them (only the toric code,
       at 3x4, 3x6, 4x5 and 4x6); the codes come from seeds no earlier step used
       (`method_codes`, hashed into the question). Each program must end optimal and find k
       logicals, and each witness (the program's for both kinds, and the enumeration's) must
       pass verify_witness. What this covers: n from 24 to 50 only (the enumeration's cap),
       and mostly polynomials of two to six random terms. Only 9 of the 200 are trinomials of
       the published form, all at 3x6 (most draws of that form have k = 0 or exceed the cap);
       k is 2 for 110 of them (all 25 at 5x5), 4 for 70, 6 for 6, 8 for 12, 10 for 1 and 18
       for 1.
   (b) On the toric code, A = 1 + x and B = 1 + y, at each of the 14 sizes in TORIC_SIZES
       (n from 60 to 576, d from 3 to 16), the program ends optimal with d = min(l, m), a
       classical theorem, finds k = 2 logicals, and returns a witness that passes
       verify_witness. No size here repeats a development run on the toric code (those are in
       excluded_seen; six sizes that did, 3x7 and 12x12 to 16x16, were replaced by 3x10 and
       12x13 to 16x17). The toric code has weight-4 checks and k = 2: it tests the program at
       the published entries' n and d, not on codes like theirs.
   (c) On 9 trinomial codes of the published form (A = x^a + y^b + y^c, B = y^d + x^e + x^f)
       with k from 4 to 12 (the published range), 3 at each size in SEARCH_SIZES (n = 162,
       180 and 216: of no published order, no method type, and no torus type at which
       development computed the distance of a non-toric code), from seeds no earlier step
       used (`search_codes`, hashed into the question; their k are 4, 8, 8 at 3x27, 12, 8, 4
       at 6x15 and 4, 8, 8 at 6x18): the program's d_Z, with a limit of SEARCH_PROGRAM_LIMIT,
       against distance_search's, with a limit of SEARCH_LIMIT. The search is an exhaustive
       check-driven search in C from every qubit: it shares nothing with the program but bb's
       matrices, uses no LP and no floating point, and does not rest on the translation row.
       These codes' distances are not known in advance. The independent checker's codes of
       this weight at n = 162 to 198 had d from 4 to 18; on them the search took at most
       3 minutes, the program reached d = 14 in 2 to 4.5 minutes and stopped at a 15-minute
       limit at d = 16 and d = 18, its bounds containing d. The prediction: on each code no
       exact value lies outside the other method's bounds (so where both are exact they are
       equal), every witness passes verify_witness, both find k logicals, and the program
       ends optimal or at a limit. A code on which either method stops at its limit is
       reported as unresolved, not as a failure. The search also runs from the two anchors
       (0, lm) alone, as it does in part 2 (that rests on the translation argument): its exact
       value, where it has one, must lie within the other two methods' bounds as well.
2. **Rediscovery.** For each of the 12 entries of ../qec-bb/codes.json, built exactly as
   ../qec-bb/study.py codes() builds them (pi_A and pi_B through bb.pi_poly), two instruments
   compute d_Z, each with a wall-clock limit of LIMIT seconds (90 minutes): the program, with a
   memory limit of distance.MEMORY_MB, and distance_search from the anchors (0, lm). The second
   was added to part 2 before registration, after the independent checker found that the
   search closed d = 18 at n = 198 in about a minute where the program stalled; it needs no
   published d (its bound is its default, SEARCH_BOUND). Each instrument on each entry runs in
   its own subprocess, the largest n first, up to --workers at a time, and its record is
   appended when it finishes, so that resume skips the jobs already recorded. A record holds
   the code (A, B, and the hash of codes.json), k (bb.k_linalg) and the number of logicals the
   instrument found, its status, its bounds, the witness's support and its check, the seconds,
   the node count, the CPU seconds and the load average. The method's jobs (one per code of
   part 1 (c), one per toric size, one per method size) follow in the same pool.

**Running it.** Each worker process asks Linux to kill it when the study's process dies (as
does the search's C process with its worker), so a killed run leaves no workers behind; check
with `pgrep -f qec_distance_study` before resume all the same. resume skips every job that has
a record, a failed one included: a failure is recorded as not tested, and is not retried. The
limits are wall clock, so other load on the machine weakens the bounds of whatever stops at a
limit: run the study when no other heavy computation shares the machine.

**Reproducing the run.** distance.py changed after this test ran (examples/qec-distance-2):
distance_ilp now runs SCIP with distance.SCIP_FIX by default, and distance_search deepens its
bound and, at a time-out, reports a lower bound where the run's search reported none (which
`interval` counts as 1). The jobs here call both with their defaults, so reproducing a record
of the run needs scip_fix=False and deepen=False. The run's search.c (search_c_sha256 in the
ledger, 02d5133b...) is in git history (the run started at commit e51556f, clean); the current
search.c with deepen=False is its single pass, and gave the same status, d, nodes, witness and
bounds on 600 of 600 development runs.

**Time.** Development timings (on other codes, four runs at once; see excluded_seen): d = 10
at n = 98 to 216 in 6 to 10 s; d = 12 at n = 162 to 288 in 35 s to 5 min; d = 14 at n = 162
to 216 in 3.5 to 5 min; d = 16 at n = 162 and 216 in 17 to 18 min; the toric code, d = 16
at n = 512, in 11 min. Each 2 added to d multiplied the time by about 5. The search was
faster at high d (the independent checker: d = 18 at n = 198 in 51 s from (0, lm), 172 s
from every qubit). With 4 workers the run should take about LIMIT plus a few minutes, since
the largest entry's two instruments may use their whole limits while the rest finish beside
them (part 1 (c) adds at most 9 x 75 minutes of work, and likely much less). On the
program's timings d = 18 at n = 288 may not finish within 90 minutes; if the search does not
finish either, the entry is consistent but unresolved, with its bounds reported. LIMIT stays
below 100 minutes because a cloud session's background commands stop at two hours, and resume
restarts an unfinished job from the beginning. Memory: at n = 288 and d >= 16, SCIP's memory grew by
about 0.7 MB/s, so the largest entry may reach distance.MEMORY_MB (3000 MB of SCIP's own
estimate, which is below the process's real use; four runs at once on 15 GB) late in its
limit. SCIP switches to memory-saving node selection at 80% of it, and a stop at the memory
limit is a stop at a limit like a time-out: its bounds are classified the same way.

**Predictions.** One per entry: d = the published d, as registered. decide judges each entry
against the registered value, not against codes.json at run time, and reports any record
whose code (codes.json's hash, or a method code's) or published d differs from the
registration. Each instrument that ran gives an interval [lower, upper] for d: upper is its
checked witness's weight (unbounded when there is none); lower is the program's dual bound
(its optimum when optimal), or the search's d when it completes (1 when it stops at its
limit). The entry's interval is the intersection, and each entry is classified, by a
registered rule:
- *reproduced*: the interval is the single value of the published d (one instrument exact,
  or the program's lower bound meeting a witness);
- *consistent but unresolved*: the interval holds the published d and more;
- *contradicted*: the interval excludes the published d;
- *method error*: an instrument found a number of logicals other than k (bb.k_linalg), ended
  with a status other than an exact end or a limit (infeasible among them), or returned a
  witness that fails verify_witness (or none with an exact value); or the two instruments'
  intervals do not meet. Such an entry says nothing about the published d, and it fails the
  method;
- *not tested*: neither instrument's subprocess gave a result.
decide also reports each instrument's classification alone.
A contradiction is a discrepancy to investigate (the source, the transcription in codes.json,
the other published version of the same code), and is reported, not hidden. The method
predictions are 1 (a), (b) and (c): any disagreement, method error or failed job there, and
for (a) and (b) any non-optimal end, fails the method.

**What a result rests on.** An upper bound is certified by its witness. The program's lower
bound, and so "optimal", rests on SCIP (distance.py's docstring), on the formulation's
soundness (the translation row, argued in distance_ilp), and on logical_basis finding all k
logicals, which is checked against bb.k_linalg for every code at run time. The search's
exact value rests on its argument (distance_search), on the translation argument for the
anchors (0, lm), and on its own bitmask basis of the logicals, checked against bb.k_linalg
likewise. Part 1 is the evidence that these are right on codes whose distances are known by
other means.

**Development (excluded_seen in the question).** Development computed distances only for
toric codes or at sizes of no published torus type, and never for a published entry; question()
lists exactly what it touched. Torus type is not all of equivalence (distance.torus_type), so
two invariants of equivalence settle it: the toric code has k = 2, which no published entry
has, and every other development code whose distance was computed has an n that no published
entry has (30, 42, 70, 72, 90, 108, 126, 144 or 288), except the builder's codes at 6x24
(n = 288), whose k was 4, 8, 16 or 24, never the published entry's 12. The same holds for
the codes of part 1 (c). One exception predates this step: the feasibility probe ran random
trinomial codes on the 12 x 12 torus, a published size (seeds not recorded); they had d = 12,
and the published entry at that size has d = 18.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import resource
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))
sys.path.insert(0, str(HERE))

import bb  # noqa: E402
import distance  # noqa: E402

from lattice_lab.ledger import canonical  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

CODES = HERE.parent / "qec-bb" / "codes.json"
PYTHON = HERE.parent.parent / ".venv" / "bin" / "python"
LIMIT = 90 * 60  # SCIP's wall-clock limit for each published entry and each toric size
METHOD_LIMIT = 600  # for each program on a random code of part 1 (a)
SEARCH_LIMIT = 30 * 60  # for distance_search on each code of part 1 (c)
SEARCH_PROGRAM_LIMIT = 15 * 60  # for the program on each code of part 1 (c)
GRACE = 15 * 60  # the subprocess's own timeout is the limit plus this
LIMITS = ("timelimit", "memlimit")  # SCIP's statuses for a stop at a limit
PROGRAM_STATUSES = ("optimal", *LIMITS)
SEARCH_STATUSES = ("complete", "timelimit")
CLASSES = ("reproduced", "consistent but unresolved", "contradicted", "method error", "not tested")
OUTCOMES = ("agree", "consistent", "disagree", "method error", "not tested")  # part 1 (c)

PUBLISHED_SIZES = [(6, 6), (15, 3), (9, 6), (12, 6), (12, 12), (3, 5), (3, 7), (5, 7), (2, 27),
                   (7, 9)]  # fmt: skip
METHOD_SIZES = [(3, 4), (2, 8), (3, 6), (4, 5), (2, 10), (3, 8), (4, 6), (5, 5)]
PER_SIZE, MAX_DRAWS = 25, 20000  # fmt: skip
TORIC_SIZES = [(3, 10), (4, 9), (5, 11), (6, 13), (8, 10), (7, 16), (10, 14), (11, 12), (12, 13),
               (9, 32), (13, 14), (14, 15), (15, 16), (16, 17)]  # fmt: skip
TORIC = [(0, 0), (1, 0)], [(0, 0), (0, 1)]
SEARCH_SIZES = [(3, 27), (6, 15), (6, 18)]
SEARCH_PER_SIZE = 3

EXCLUDED_SEEN = [
    "the feasibility probe, before this step: the toric code at 12x12, and random trinomial "
    "codes on the 12x12 torus (a published size; seeds not recorded), whose distances it found "
    "to be 12; no published entry",
    "tests/test_qec_distance.py: random codes from random.Random(1) to random.Random(5) at "
    "2x2, 2x3, 2x4, 3x3, 2x5, 2x6 and 4x4 (the program, the enumeration and the search); the "
    "toric code at 2x5, 3x3, 4x4, 3x6, 4x6, 5x6, 6x8, 3x4 and 10x10",
    "a smoke test: codes from random.Random('qec-distance dev smoke') at 2x3, 3x3, 2x4, 4x4 and "
    "2x6; the toric code at 5x7 and 10x10",
    "enumeration timing: the toric code at 4x5, 3x7, 5x5, 3x9 and 4x7",
    "program timing: the toric code at 6x6, 8x8, 10x10, 12x12, 9x16, 13x13, 14x14, 15x15 and "
    "16x16 (and 13x13 without the translation row)",
    "program timing: trinomial codes with k >= 4 from random.Random('qec-distance development "
    "LxM'), the first 16 at each of 7x7, 6x10, 9x9, 7x14, 12x9 and 6x24 (15 s each), and longer "
    "runs (up to 1100 s) of 9x9 #1, #2, #3, #10, 12x9 #4, #11, #12, 7x14 #2, #4 and 6x24 #3, #4, "
    "#9, #10, #13, #15, #16",
    "formulation variants (sparser logicals, parity cuts, one program per logical, SCIP "
    "emphasis settings, no translation row, a repeat for determinism) on 7x7 #9, #12, 9x9 #1, "
    "#9 and 12x9 #16 of the same codes",
    "k only, no distances: trinomial draws from the same seeds at 8x8, 10x10, 8x12, 10x14, "
    "8x18, 11x13 and 9x16; the sampling rule's yields at the method sizes and 2x7, 2x9 and 1x16 "
    "from random.Random('qec-distance development yield LxM')",
    "the method codes themselves were drawn, their k computed and hashed, to fix them; no "
    "distance of any of them",
    "the review: the program on the toric code at 4x4 (through _run), 13x13 (3 s limit) and "
    "10x10 (twice); k only for the probe's 12x12 draws at integer seeds 0 to 59; check "
    "matrices only, no distances, at 2x3, 2x5, 3x3 and 4x4 from random.Random('qec-distance "
    "review exponents')",
    "the independent checker (its own enumeration, a check-driven search, one program per "
    "logical in HiGHS and SCIP, and distance_ilp with and without the translation row; "
    "distances of both kinds): the 164 codes from random.Random('checker-independent LxM') at "
    "1x7, 1x9, 2x7, 4x4, 2x9, 1x22, 2x11, 2x13, 3x9, 4x7, 5x6, 4x8, 3x11, 3x13, 4x10, 6x7, "
    "4x11, 6x8, 7x7, 5x10, 7x8, 6x10, 8x8, 7x11, 8x10, 9x9, 7x12, 7x13, 8x12 and 10x10 "
    "(recorded for the first 101, through 7x7; a comparison of search variants iterated over "
    "the rest), and the 72 codes from random.Random('checker-independent w6 LxM') at 3x9, 5x6, "
    "6x7, 3x13, 7x7, 7x8, 6x10, 5x12, 9x9, 7x12, 6x14, 7x13, 9x11, 3x11 and 6x8. Its guard "
    "refused every non-toric code at a group order of a published entry (15, 21, 35, 36, 45, "
    "54, 63, 72, 144) or a torus type of METHOD_SIZES",
    "the independent checker: edge cases (zero, cancelling, repeated and unreduced polynomials, "
    "k = 0), distances included, at 1x1, 2x2, 2x3, 3x3, 1x2, 1x7, 7x1, 1x9, 2x7, 2x9 and 4x4; "
    "logical-basis, encoding and translation checks, no distances, at 1x1, 2x2, 1x7, 2x7, 4x4, "
    "2x9, 2x11, 3x9, 5x6, 4x7 and 6x7; the toric code at 1x7, 2x7, 3x4, 4x4, 2x9, 3x9, 4x7, "
    "5x6, 6x7, 7x7, 8x8, 9x10, 10x10, 12x12, 9x16, 4x11, 7x12, 9x11, 8x13, 11x11, 6x20, 13x13, "
    "11x14, 15x15 and 17x17",
    "applying the review: distance_search on the toric code at 2x5, 3x3, 4x4, 3x6, 4x6, 5x6, "
    "6x8 and 10x10, on codes from random.Random(4) at the test sizes, and on the independent "
    "checker's w6 codes #42 to #64 (9x9, 7x12, 7x13, 6x14, 9x11); k only, no distances, for "
    "300 trinomial draws each from random.Random('qec-distance development tier yield LxM') "
    "at 6x15, 3x27, 6x18, 7x15, 9x10, 5x15, 9x14, 6x16, 9x15, 6x21, 3x30, 12x10, 10x12, 9x13, "
    "6x20, 5x18, 6x11, 3x16, 6x13, 3x25 and 10x15; the codes of part 1 (c) drawn, their k "
    "computed and hashed, to fix them; no distance of any of them; and, through _run, the "
    "program on the toric code at 3x4 and 16x16 (the second stopped after 8 s, to check that "
    "a worker dies with the study's process)",
    "the orchestrator, adding the search to part 2 before registration: job() on the toric code "
    "at 5x7 (both published-entry instruments, with codes() replaced) and at 4x6 (part 1 (c)'s "
    "job, with search_codes() replaced); no published entry and no part 1 (c) code",
]


def codes() -> list[dict]:
    """The published entries, built as ../qec-bb/study.py codes() builds them."""
    out = []
    for c in json.loads(CODES.read_text())["codes"]:
        A = c["A"] if "A" in c else bb.pi_poly(c["pi_A"])
        B = c["B"] if "B" in c else bb.pi_poly(c["pi_B"])
        out.append({**c, "A": A, "B": B})
    return out


def _sha256(obj) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def _codes_sha256() -> str:
    return hashlib.sha256(CODES.read_bytes()).hexdigest()


def _three(rng: random.Random, size: int) -> list[int]:
    return rng.sample(range(size), 3) if size >= 3 else [rng.randrange(size) for _ in range(3)]


def method_codes(ell: int, m: int) -> list[dict]:
    """The first PER_SIZE codes, from the seeded sequence, with k > 0 and dim ker H_X =
    lm + k/2 within distance.BRUTE_CAP. Each draw is, with probability 1/2, a trinomial of the
    published form (A = x^a + y^b + y^c, B = y^d + x^e + x^f), and otherwise two polynomials of
    two to six random terms. The filters keep few trinomials: 9 of the 200, all at 3x6."""
    rng = random.Random(f"qec-distance study {ell}x{m}")
    out, draws = [], 0
    while len(out) < PER_SIZE and draws < MAX_DRAWS:
        draws += 1
        if rng.random() < 0.5:
            family = "trinomial"
            (a, e, f), (d, b, c) = _three(rng, ell), _three(rng, m)
            A, B = [[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]
        else:
            family = "random"
            A, B = [[[rng.randrange(ell), rng.randrange(m)] for _ in range(rng.randint(2, 6))]
                    for _ in range(2)]  # fmt: skip
        k = bb.k_linalg(A, B, ell, m)
        if k and ell * m + k // 2 <= distance.BRUTE_CAP:
            out.append({"family": family, "A": A, "B": B, "k": k})
    return out


def search_codes(ell: int, m: int) -> list[dict]:
    """The first SEARCH_PER_SIZE distinct trinomials of the published form (A = x^a + y^b + y^c,
    B = y^d + x^e + x^f, with a, e, f distinct and b, c, d distinct) with k from 4 to 12, the
    published entries' range, from the seeded sequence, in at most MAX_DRAWS draws. Nothing
    about them but k is known."""
    rng = random.Random(f"qec-distance study search {ell}x{m}")
    out, seen, draws = [], set(), 0
    while len(out) < SEARCH_PER_SIZE and draws < MAX_DRAWS:
        draws += 1
        (a, e, f), (d, b, c) = rng.sample(range(ell), 3), rng.sample(range(m), 3)
        A, B = [[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]
        key = canonical([sorted(A), sorted(B)])
        k = bb.k_linalg(A, B, ell, m)
        if 4 <= k <= 12 and key not in seen:
            seen.add(key)
            out.append({"A": A, "B": B, "k": k})
    return out


def _method_sha256() -> str:
    return _sha256({f"{ell}x{m}": method_codes(ell, m) for ell, m in METHOD_SIZES})


def _search_sha256() -> str:
    return _sha256({f"{ell}x{m}": search_codes(ell, m) for ell, m in SEARCH_SIZES})


def code_hashes() -> dict:
    """The sha256 of the codes each method job runs, by job key: what the method predictions
    register, and what each record of part 1 (a) and (c) carries."""
    out = {f"random {ell}x{m}": _sha256(method_codes(ell, m)) for ell, m in METHOD_SIZES}
    for ell, m in SEARCH_SIZES:
        for i, c in enumerate(search_codes(ell, m)):
            out[f"search {ell}x{m} #{i + 1}"] = _sha256(c)
    return out


def interval(result: dict, k_linalg: int, statuses: tuple) -> tuple[int, int | None] | None:
    """One instrument's result as an interval (lower, upper) for d, upper being its checked
    witness's weight (None when there is none); or None for a method error: other than k
    logicals, a status outside `statuses`, a witness that fails verify_witness, or none with an
    exact value (the program optimal, or the search with a d)."""
    check = result["witness_check"]
    exact = result["status"] == "optimal" or result.get("d") is not None
    if (
        result["k"] != k_linalg
        or result["status"] not in statuses
        or (check is not None and not check["logical"])
        or (exact and check is None)
    ):
        return None
    upper = result["upper"] if check is not None else None
    lower = result["lower"] if result["lower"] is not None else 1
    return lower, upper


def classify(program: dict | None, search: dict | None, predicted: int) -> str:
    """The registered rule (module docstring) for one published entry, from the records of its
    two instruments (None, or an error row, for one that gave no result), against the
    registered d."""
    results = []
    for row, statuses in ((program, PROGRAM_STATUSES), (search, SEARCH_STATUSES)):
        if row is not None and "status" in row:
            results.append(interval(row, row["k_linalg"], statuses))
    if not results:
        return "not tested"
    if None in results:
        return "method error"
    lower = max(lo for lo, _ in results)
    uppers = [up for _, up in results if up is not None]
    upper = min(uppers) if uppers else None
    if upper is not None and lower > upper:
        return "method error"  # the two instruments' intervals do not meet
    if upper == lower:
        return "reproduced" if upper == predicted else "contradicted"
    if (upper is not None and upper < predicted) or lower > predicted:
        return "contradicted"
    return "consistent but unresolved"


def search_outcome(row: dict) -> str:
    """Part 1 (c)'s rule for one code's record: "agree" (the program and the full search exact
    and equal), "consistent" (one or both stopped at a limit, and no exact value or bound
    contradicts another), "disagree" (some two of the program, the full search and the search
    from (0, lm) have intervals that do not meet), "method error" (a method found other than k
    logicals, ended with another status, or returned a witness that fails verify_witness, or
    none with an exact value) or "not tested" (the job failed)."""
    if "error" in row:
        return "not tested"
    program, search, anchored = row["program"], row["search"], row["search_anchored"]
    results = [
        interval(program, row["k_linalg"], PROGRAM_STATUSES),
        interval(search, row["k_linalg"], SEARCH_STATUSES),
        interval(anchored, row["k_linalg"], SEARCH_STATUSES),
    ]
    if None in results:
        return "method error"
    lower = max(lo for lo, _ in results)
    uppers = [up for _, up in results if up is not None]
    if uppers and lower > min(uppers):
        return "disagree"
    return "agree" if program["d"] is not None and program["d"] == search["d"] else "consistent"


def question() -> dict:
    return {
        "id": "qec-distance-rediscovery",
        "title": "Exact distances of the published bivariate bicycle codes, by integer "
        "programming and an exhaustive search",
        "statement": "distance.distance_ilp, one integer program solved by SCIP, computes d_Z "
        "exactly: it equals an exhaustive enumeration on 200 random codes at 8 small sizes "
        "(n <= 50), equals d_X on the same codes, gives min(l, m) on the toric code at 14 sizes "
        "up to n = 576 and d = 16 that development did not run, and agrees, within its bounds "
        "where it stops at its limit, with an LP-free exhaustive search (distance_search, from "
        "every qubit and from (0, lm)) on 9 trinomial codes of the published form at n = 162 to "
        "216. Applied to the 12 entries of ../qec-bb/codes.json, the program and the search "
        "from (0, lm), each with a 90-minute limit, give the published distance d: each entry "
        "is reproduced, consistent but unresolved, contradicted, or a method error, by the "
        "registered rule.",
        "source": "docs/next-direction.md, step 2 (distance); ../qec-bb/codes.json",
        "codes_file": "../qec-bb/codes.json",
        "codes_sha256": _codes_sha256(),
        "published_sizes": [list(s) for s in PUBLISHED_SIZES],
        "method_sizes": [list(s) for s in METHOD_SIZES],
        "method_codes": f"method_codes(l, m): the first {PER_SIZE} codes with k > 0 and "
        f"lm + k/2 <= {distance.BRUTE_CAP} from random.Random('qec-distance study LxM'), "
        f"at most {MAX_DRAWS} draws; 191 of the 200 are random polynomials of 2 to 6 terms and "
        "9 trinomials (at 3x6); k is 2 for 110, 4 for 70, 6 for 6, 8 for 12, 10 for 1, 18 for 1",
        "method_codes_sha256": _method_sha256(),
        "toric_sizes": [list(s) for s in TORIC_SIZES],
        "search_sizes": [list(s) for s in SEARCH_SIZES],
        "search_codes": f"search_codes(l, m): the first {SEARCH_PER_SIZE} distinct trinomials "
        "of the published form with 4 <= k <= 12 from random.Random('qec-distance study search "
        f"LxM'), at most {MAX_DRAWS} draws",
        "search_codes_sha256": _search_sha256(),
        "search": "distance.distance_search: an exhaustive check-driven search (search.c, "
        "compiled with the system's cc) from every qubit, labels from a bitmask basis of the "
        "X-logicals, integer arithmetic only",
        "search_compiler": distance._search_binary()[1],
        "search_c_sha256": hashlib.sha256(distance.SEARCH_C.read_bytes()).hexdigest(),
        "time_limit_seconds": LIMIT,
        "published_instruments": "distance_ilp (kind Z, the translation row) and "
        "distance_search (kind Z, anchors (0, lm), bound SEARCH_BOUND), each with "
        "time_limit_seconds",
        "search_bound": distance.SEARCH_BOUND,
        "method_time_limit_seconds": METHOD_LIMIT,
        "search_time_limit_seconds": SEARCH_LIMIT,
        "search_program_time_limit_seconds": SEARCH_PROGRAM_LIMIT,
        "memory_limit_mb": distance.MEMORY_MB,
        "scip_seed": distance.SEED,
        "enumeration_cap": distance.BRUTE_CAP,
        "solver": distance.scip_version(),
        "formulation": "binary c; H_X c = 2 s; L.c = 2 t_L + z_L for a basis L of the "
        "X-logicals, z_L binary, sum z_L >= 1; c_(0,0) + c_(lm+(0,0)) >= 1; minimise sum c",
        "classification": {
            "interval": "each instrument: lower = the program's dual bound (its optimum when "
            "optimal) or the search's d when complete (1 at its limit); upper = its checked "
            "witness's weight; the entry's interval is the intersection",
            "reproduced": "the interval is exactly the registered d",
            "consistent but unresolved": "the interval holds the registered d and more",
            "contradicted": "the interval excludes the registered d (a discrepancy to "
            "investigate, reported)",
            "method error": "an instrument found logicals != bb.k_linalg, ended with a status "
            "other than exact or a limit, or returned a witness that fails verify_witness (or "
            "none with an exact value); or the two instruments' intervals do not meet; fails "
            "the method",
            "not tested": "neither instrument's subprocess gave a result",
        },
        "excluded_seen": EXCLUDED_SEEN,
        "hypotheses": {
            "method": "distance_ilp = distance_brute (kind Z) and d_X = d_Z on all 200 random "
            "codes, distance_ilp = min(l, m) on the toric code at every registered size, every "
            "run optimal with k logicals and every witness checked; and on the 9 codes of part "
            "1 (c), no exact value of distance_ilp or distance_search outside the other's "
            "bounds, every witness checked, k logicals each",
            "rediscovery": "for each entry d_Z, from the program and the search, is the "
            "published d",
        },
    }


def predictions() -> list[dict]:
    hashes = code_hashes()
    method = [
        {
            "test": "method-enumeration",
            "predicted": "distance_ilp (kind Z) = distance_brute (kind Z) on all 200 random "
            "codes, every program optimal with k logicals, every witness checked",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("random")},
        },
        {
            "test": "method-dx-dz",
            "predicted": "distance_ilp (kind X) = distance_ilp (kind Z) on the same 200 codes",
        },
        {
            "test": "method-toric",
            "predicted": "distance_ilp = min(l, m) on the toric code at each registered size, "
            "optimal, k = 2 logicals, witness checked",
        },
        {
            "test": "method-search",
            "predicted": "on each of the 9 codes of part 1 (c), no exact value of distance_ilp, "
            "distance_search from every qubit or distance_search from (0, lm) outside another's "
            "bounds, all with k logicals, every witness checked, the program optimal or at a "
            "limit",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("search")},
        },
    ]
    return method + [
        {"test": "rediscovery", "name": c["name"], "l": c["l"], "m": c["m"], "n": c["n"],
         "k": c["k"], "predicted_d": c["d"], "codes_sha256": _codes_sha256()}
        for c in codes()
    ]  # fmt: skip


# ---------------------------------------------------------------- jobs


def jobs() -> list[dict]:
    """Every job, in the order they start: the published entries by decreasing n (the program,
    then the search, for each), then the codes of part 1 (c), then the toric sizes by
    decreasing n, then the method sizes."""
    pub = sorted(codes(), key=lambda c: (-c["n"], c["name"]))
    toric = sorted(TORIC_SIZES, key=lambda s: (-s[0] * s[1], s))
    return (
        [
            job
            for c in pub
            for job in (
                {"test": "published", "key": c["name"]},
                {"test": "published-search", "key": c["name"] + " (search)", "name": c["name"]},
            )
        ]
        + [
            {"test": "search", "key": f"search {ell}x{m} #{i + 1}", "l": ell, "m": m, "i": i}
            for ell, m in SEARCH_SIZES
            for i in range(len(search_codes(ell, m)))
        ]
        + [{"test": "toric", "key": f"toric {ell}x{m}", "l": ell, "m": m} for ell, m in toric]
        + [
            {"test": "random", "key": f"random {ell}x{m}", "l": ell, "m": m}
            for ell, m in METHOD_SIZES
        ]
    )


def _checked(A, B, ell: int, m: int, kind: str, witness) -> dict | None:
    return distance.verify_witness(A, B, ell, m, kind, witness) if witness else None


def _program(A, B, ell: int, m: int, limit: float) -> dict:
    """The program's result for d_Z, its witness checked, as a record's fields."""
    r = distance.distance_ilp(A, B, ell, m, "Z", limit)
    keep = ("kind", "translation", "k", "status", "d", "lower", "upper", "dual_bound",
            "witness", "seconds", "solving_seconds", "nodes", "time_limit", "settings",
            "parameters")  # fmt: skip
    return {
        **{key: r[key] for key in keep},
        "witness_check": _checked(A, B, ell, m, "Z", r["witness"]),
    }


def _searched(A, B, ell: int, m: int, limit: float, anchors) -> dict:
    """distance_search's result for d_Z, its witness checked."""
    s = distance.distance_search(A, B, ell, m, "Z", anchors=anchors, time_limit=limit)
    keep = ("status", "d", "lower", "upper", "witness", "k", "nodes", "bound", "anchors",
            "time_limit", "seconds", "compiler")  # fmt: skip
    return {
        **{key: s[key] for key in keep},
        "witness_check": _checked(A, B, ell, m, "Z", s["witness"]),
    }


def _brief(r: dict) -> dict:
    keep = ("status", "d", "lower", "upper", "witness", "k", "nodes", "seconds")
    return {key: r[key] for key in keep if key in r}


def _method_code(A, B, ell: int, m: int, k: int) -> dict:
    brute = distance.distance_brute(A, B, ell, m, "Z")
    z = distance.distance_ilp(A, B, ell, m, "Z", METHOD_LIMIT)
    x = distance.distance_ilp(A, B, ell, m, "X", METHOD_LIMIT)
    checks = {
        "brute": bool((_checked(A, B, ell, m, "Z", brute["witness"]) or {}).get("logical")),
        "Z": bool((_checked(A, B, ell, m, "Z", z["witness"]) or {}).get("logical")),
        "X": bool((_checked(A, B, ell, m, "X", x["witness"]) or {}).get("logical")),
    }
    optimal = z["status"] == x["status"] == "optimal"
    return {
        "dim": brute["dim"],
        "brute": {"d": brute["d"], "witness": brute["witness"]},
        "ilp_z": _brief(z),
        "ilp_x": _brief(x),
        "checks": checks,
        "agree": optimal
        and all(checks.values())
        and z["k"] == x["k"] == k
        and z["d"] == brute["d"] == x["d"],
        "seconds": round(brute["seconds"] + z["seconds"] + x["seconds"], 3),
    }


def _usage() -> dict:
    """The job's CPU seconds (its process and its children) and the load average as it ends:
    the limits are wall clock, so load bears on whatever stopped at one."""
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime
    return {"cpu_seconds": round(cpu, 1), "load": [round(x, 2) for x in os.getloadavg()]}


def job(spec: dict) -> dict:
    """Run one job and return its record (execute calls it in a subprocess)."""
    solver = {"solver": distance.scip_version(), "seed": distance.SEED}
    if spec["test"] == "published":
        c = next(c for c in codes() if c["name"] == spec["key"])
        A, B, ell, m = c["A"], c["B"], c["l"], c["m"]
        return {"test": "published", "key": c["name"], "name": c["name"], "l": ell, "m": m,
                "n": c["n"], "A": A, "B": B, "codes_sha256": _codes_sha256(),
                "published_k": c["k"], "published_d": c["d"],
                "k_linalg": bb.k_linalg(A, B, ell, m), **_program(A, B, ell, m, LIMIT),
                **solver, **_usage()}  # fmt: skip
    if spec["test"] == "published-search":
        c = next(c for c in codes() if c["name"] == spec["name"])
        A, B, ell, m = c["A"], c["B"], c["l"], c["m"]
        return {"test": "published-search", "key": spec["key"], "name": c["name"], "l": ell,
                "m": m, "n": c["n"], "A": A, "B": B, "codes_sha256": _codes_sha256(),
                "published_k": c["k"], "published_d": c["d"],
                "k_linalg": bb.k_linalg(A, B, ell, m),
                **_searched(A, B, ell, m, LIMIT, (0, ell * m)), **_usage()}  # fmt: skip
    ell, m = spec["l"], spec["m"]
    if spec["test"] == "toric":
        return {"test": "toric", "key": spec["key"], "l": ell, "m": m, "n": 2 * ell * m,
                "expected_d": min(ell, m), **_program(*TORIC, ell, m, LIMIT), **solver,
                **_usage()}  # fmt: skip
    if spec["test"] == "search":
        c = search_codes(ell, m)[spec["i"]]
        A, B = c["A"], c["B"]
        return {"test": "search", "key": spec["key"], "l": ell, "m": m, "n": 2 * ell * m,
                "A": A, "B": B, "codes_sha256": _sha256(c), "k_linalg": bb.k_linalg(A, B, ell, m),
                "search": _searched(A, B, ell, m, SEARCH_LIMIT, None),
                "search_anchored": _searched(A, B, ell, m, SEARCH_LIMIT, (0, ell * m)),
                "program": _program(A, B, ell, m, SEARCH_PROGRAM_LIMIT), **solver,
                **_usage()}  # fmt: skip
    method = method_codes(ell, m)
    rows = [{**c, **_method_code(c["A"], c["B"], ell, m, c["k"])} for c in method]
    return {
        "test": "random",
        "key": spec["key"],
        "l": ell,
        "m": m,
        "codes_sha256": _sha256(method),
        "codes": len(rows),
        "agree": sum(r["agree"] for r in rows),
        "distances": sorted({r["brute"]["d"] for r in rows}),
        "rows": rows,
        "time_limit": METHOD_LIMIT,
        **solver,
        **_usage(),
    }


# The worker asks Linux to kill it when the study's process dies (PR_SET_PDEATHSIG is 1), and
# exits at once if that process is already gone.
WORKER = """
import ctypes, importlib.util, json, os, signal, sys
if sys.platform == "linux":
    ctypes.CDLL(None).prctl(1, signal.SIGKILL)
    if os.getppid() != int(sys.argv[2]):
        sys.exit("the study's process is gone")
spec = importlib.util.spec_from_file_location("qec_distance_study", {path!r})
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
print(json.dumps(study.job(json.loads(sys.argv[1]))))
"""


def _run(spec: dict) -> dict:
    """One job in its own worker process. Any failure is returned as an error row (the job is
    then not tested, and resume does not retry it)."""
    timeout = LIMIT + GRACE
    code = WORKER.format(path=str(HERE / "study.py"))
    try:
        out = subprocess.run([str(PYTHON), "-c", code, json.dumps(spec), str(os.getpid())],
                             cwd=HERE, capture_output=True, text=True, timeout=timeout)  # fmt: skip
        if out.returncode:
            return {**spec, "error": out.stderr[-2000:]}
        return json.loads(out.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {**spec, "error": f"subprocess timeout after {timeout} s"}
    except Exception as exc:
        return {**spec, "error": f"{type(exc).__name__}: {exc}"}


def execute(path: Path, workers: int) -> None:
    """Run every job without a record in `path` (a failed job's error row counts as a record)."""
    done = set()
    if path.exists():
        done = {json.loads(line)["key"] for line in path.read_text().splitlines() if line.strip()}
    todo = [j for j in jobs() if j["key"] not in done]
    with ThreadPoolExecutor(max(1, workers)) as pool:
        for future in as_completed([pool.submit(_run, j) for j in todo]):
            append_records(path, [future.result()])


def _method_failures(rnd: list[dict], toric: list[dict], search: dict) -> list[str]:
    bad = [r["key"] for r in rnd if "error" in r or not r["agree"] == r["codes"] == PER_SIZE]
    for r in toric:
        if "error" in r or r["status"] != "optimal" or r["d"] != r["expected_d"] or r["k"] != 2:
            bad.append(r["key"])
        elif not (r["witness_check"] or {}).get("logical"):
            bad.append(r["key"])
    return bad + [key for key, o in search.items() if o not in ("agree", "consistent")]


def _entry_interval(program: dict | None, search: dict | None) -> list | None:
    """The entry's interval [lower, upper] (upper None when no witness), from the instruments
    whose results are sound; None when there are none."""
    results = []
    for row, statuses in ((program, PROGRAM_STATUSES), (search, SEARCH_STATUSES)):
        if row is not None and "status" in row:
            results.append(interval(row, row["k_linalg"], statuses))
    results = [r for r in results if r is not None]
    if not results:
        return None
    uppers = [up for _, up in results if up is not None]
    return [max(lo for lo, _ in results), min(uppers) if uppers else None]


def decide(rows: list[dict], registered: list[dict]) -> dict:
    predicted = {p["name"]: p for p in registered if p.get("test") == "rediscovery"}
    hashes = {}  # the registered hashes of the method codes, by job key
    for p in registered:
        if p.get("test", "").startswith("method"):
            hashes.update(p.get("codes_sha256", {}))
    expected = list(predicted) + [j["key"] for j in jobs() if j["test"] != "published"]
    keys = {r["key"] for r in rows}
    program = {r["key"]: r for r in rows if r["test"] == "published" and r["key"] in predicted}
    searched = {
        r["name"]: r for r in rows if r["test"] == "published-search" and r["name"] in predicted
    }
    pub = list(program.values()) + list(searched.values())
    toric = [r for r in rows if r["test"] == "toric"]
    rnd = [r for r in rows if r["test"] == "random"]
    search = {r["key"]: search_outcome(r) for r in rows if r["test"] == "search"}
    names = [name for name in predicted if name in program or name in searched]
    classes = {
        name: classify(program.get(name), searched.get(name), predicted[name]["predicted_d"])
        for name in names
    }
    alone = {
        name: {
            "program": classify(program.get(name), None, predicted[name]["predicted_d"]),
            "search": classify(None, searched.get(name), predicted[name]["predicted_d"]),
        }
        for name in names
    }
    errors = [key for key, c in classes.items() if c == "method error"]
    bad = _method_failures(rnd, toric, search) + errors
    tested = [r for r in pub if "error" not in r]
    changed = [
        r["key"]
        for r in tested
        if r["codes_sha256"] != predicted[r.get("name", r["key"])]["codes_sha256"]
        or r["published_d"] != predicted[r.get("name", r["key"])]["predicted_d"]
    ] + [
        r["key"]
        for r in rows
        if r["test"] in ("random", "search")
        and "error" not in r
        and r["codes_sha256"] != hashes.get(r["key"])
    ]
    missing = [key for key in expected if key not in keys]
    return {
        "missing": missing,
        "method": "fails" if bad else ("incomplete" if missing else "holds"),
        "method_failures": bad,
        "random_codes": sum(r.get("codes", 0) for r in rnd),
        "random_agree": sum(r.get("agree", 0) for r in rnd),
        "toric_sizes": len(toric),
        "search": search,
        "search_counts": {o: sum(v == o for v in search.values()) for o in OUTCOMES},
        "rediscovery": classes,
        "rediscovery_by_instrument": alone,
        "counts": {c: sum(v == c for v in classes.values()) for c in CLASSES},
        "contradicted": [key for key, c in classes.items() if c == "contradicted"],
        "method_errors": errors,
        "intervals": {
            name: _entry_interval(program.get(name), searched.get(name)) for name in names
        },
        "witness_failures": [
            r["key"] for r in pub if r.get("witness_check") and not r["witness_check"]["logical"]
        ],
        "k_mismatches": [
            r["key"] for r in tested if r["k_linalg"] != predicted[r.get("name", r["key"])]["k"]
        ],
        "unregistered": [
            r["key"]
            for r in rows
            if r["test"] in ("published", "published-search")
            and r.get("name", r["key"]) not in predicted
        ],
        "registration_mismatches": changed,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
