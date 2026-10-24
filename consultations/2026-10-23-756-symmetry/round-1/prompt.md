You are being consulted on a mathematics research project. The project studies linear cellular automata over GF(2) on tori: which rules have every nonzero eigenvalue in a given subgroup (a cube, say) at a given size, why, and what laws their periods follow. Its rule is that nothing counts until a machine has checked it: identities are multiplied out again, claims about eigenvalues are recomputed, proofs go into Lean, and predictions are registered before they are tested. Other models are being asked the same question independently.

So that your answer can be checked: state each claim precisely, with the quantifiers and the sizes it covers; say for each whether you proved it, checked it by computation (and how far), or conjecture it; give proofs or arguments where you have them; and where you can, make predictions at cases the documents below do not settle, which can then be registered and tested. If you can run code, use it to check every identity and computation before you state it. Say plainly where you think the project is wrong or missing something.

<documents>
<document path="docs/code-distances.md">
# Code distances: the published bivariate bicycle codes, reproduced

**Result (registered test `examples/qec-distance`, run 2026-10-21): all 12 published distances
are reproduced.**
- **How.** An exhaustive search written for this project reproduced every one exactly. The
  integer program agrees on 11 and brackets the twelfth.
- **The method prediction failed once.** On 1 of 200 random test codes, the integer program,
  solved by SCIP, reported a wrong optimum. So the program alone is not trusted as a proof of a
  lower bound, and the published distances rest on the search.

**Then both instruments were fixed and a second registered test (`examples/qec-distance-2`, run
2026-10-22) passed in full.**
- **The fault.** It is in SCIP 10.0's presolving of the XOR constraints it builds from the
  program's parity rows. The fix turns that presolving and SCIP's rapid learning off.
- **The search** now deepens its bound step by step, so it no longer stalls.
- **The re-test.** On fresh codes at sizes no development touched, both fixed instruments held
  on every registered part. SCIP's unfixed defaults, run beside them as a control, were wrong on
  3 fresh codes.

This is step 2 of [next-direction.md](next-direction.md), which began with distance: nothing in
the project computed it before.

## What was computed

A code's **distance** d is the weight of its lightest undetectable error: the fewest qubits whose
errors change the stored information without tripping any check. For a bivariate bicycle code
(A, B) on the l x m torus, a Z-type logical is a vector c with H_X c = 0 that is not in the
rowspace of H_Z, and d_Z is the least weight of one. d_X is defined the same way with the two
check matrices exchanged. For every bivariate bicycle code d_X = d_Z: swapping the two blocks and
inverting the torus carries one problem onto the other (`distance.py`'s docstring). So d = d_Z.

Two instruments compute d_Z exactly. They share nothing but the check matrices.
- **The integer program** (`distance_ilp`, solved by SCIP 10 through pyscipopt 6.3).
  - Variables: binary c.
  - Constraints: H_X c = 2s; L · c = 2t + z for a basis L of the X-logicals; Σ z ≥ 1; and a
    translation row, c at (0,0) of either block. The translation row is sound because translating
    a logical keeps it a logical of the same weight.
  - Objective: minimise Σ c. At a time limit it reports a lower bound (its dual bound) and an
    upper bound (its best solution).
- **The exhaustive search** (`distance_search`, `search.c`).
  - It grows a set from an anchor qubit, branching over the qubits of one unsatisfied check, and
    prunes by weight.
  - It is exact, by an argument in its docstring: some branch stays inside a lightest logical
    until it is complete, and the pruning never cuts that branch.
  - It uses integer arithmetic only, no LP and no floating point.
  - From the anchors (0, lm) it rests on the same translation argument. From every qubit it rests
    on nothing else.
  - It was written by an independent checker during development, as a check on the program, and
    added to the rediscovery before registration because it closed d = 18 at n = 198 in about a
    minute where the program stalled.

Every upper bound is certified: each witness is checked separately (`verify_witness`, with
bb.py's bitmask rows and ranks). A lower bound is not: it rests on SCIP for the program, and on
the argument and its code for the search.

## The registered test

Predictions were committed and pushed before any distance of a published code was computed
(`ledger.jsonl`, `excluded_seen` in the question). Development used only toric codes and codes on
tori of no published type. An independent checker reimplemented the computation (its own
enumeration, an LP-free search, and a program per logical in HiGHS and SCIP) and agreed with the
tools on 170 development codes.

**Rediscovery: 12 of 12 reproduced.**

| Code | n | k | published d | program | search, from (0, lm) |
| --- | --- | --- | --- | --- | --- |
| [[72,12,6]] | 72 | 12 | 6 | optimal 6, 0.4 s | 6, 0.16 s |
| [[90,8,10]] | 90 | 8 | 10 | optimal 10, 3.7 s | 10, 0.15 s |
| [[108,8,10]] | 108 | 8 | 10 | optimal 10, 6.5 s | 10, 0.21 s |
| [[144,12,12]], the gross code | 144 | 12 | 12 | optimal 12, 36 s | 12, 0.20 s |
| [[288,12,18]] | 288 | 12 | 18 | time limit (90 min): 13 ≤ d ≤ 18 | **18, 3 min** (2.6 billion nodes) |
| [[30,4,6]] | 30 | 4 | 6 | optimal 6, 0.13 s | 6, 0.14 s |
| [[42,6,6]] | 42 | 6 | 6 | optimal 6, 0.36 s | 6, 0.27 s |
| [[70,6,8]] | 70 | 6 | 8 | optimal 8, 0.58 s | 8, 0.15 s |
| [[108,12,6]], poster version | 108 | 12 | 6 | optimal 6, 0.29 s | 6, 0.12 s |
| [[108,12,6]], Quantum version | 108 | 12 | 6 | optimal 6, 0.32 s | 6, 0.15 s |
| [[126,12,10]], poster version | 126 | 12 | 10 | optimal 10, 7.7 s | 10, 0.13 s |
| [[126,12,10]], Quantum version | 126 | 12 | 10 | optimal 10, 5.5 s | 10, 0.15 s |

The two published versions of each coprime code have different polynomials, and both give the
published k (the earlier test) and the published d.

**Method checks.**
- **Toric codes: 14 of 14.** The program gave d = min(l, m) at every registered size, n = 60 to
  576, d up to 16 (544 qubits in 15 minutes).
- **Program against search: 7 agree, 2 consistent, 0 disagree.** The 9 trinomial codes at n =
  162 to 216 had d from 4 to 14. On the two marked consistent (d = 4 and 6, by the program in
  under 4 s), the search found no logical within its 30-minute limit, from every qubit or from
  (0, lm). That is a weakness, not a contradiction: it starts with its bound at 64, and its
  depth-first descent can go very deep before it meets a nontrivial logical. Iterative deepening
  (bounds 2, 3, ...) would fix it.
- **Program against enumeration: failed at 1 of 200 codes.** d_Z agreed with the enumeration on
  all 200, but on one code d_X did not.

## The failure

The code is A = x y^2 + x^3 y^2, B = x^2 y^3 + x^3 y^3 on the 4 x 5 torus, with k = 10. Its
d_Z = d_X = 2.
- **The evidence for 2.** The enumeration gives 2 for both kinds, the search gives 2, and a
  weight-2 X-logical, (0,0) and (2,0) of the right block, passes the witness check.
- **What the program said.** At the registered seed it reported d_X = 3, status optimal, with
  dual bound 3.

What was found afterwards:
- **It depends on the random seed.** With SCIP's default settings, seeds 0, 2 and 4 give 3;
  seeds 1, 3, 5, 6 and 7 give 2.
- **It needs two things at once.** Each of these gives 2 at every seed tried:
  - turning off presolve;
  - turning off SCIP's weak or its strong dual reductions;
  - removing the translation row.

  Turning off any single presolver, propagator or constraint handler's dual presolving does not
  fix it, and turning off SCIP's symmetry handling does not either. The fault therefore sits in
  how SCIP's dual reductions interact with the program when the translation row is present. It
  was not isolated further.
- **It is rare.** A scan of 280 further development codes at 7 sizes (4 x 4 to 2 x 11), both
  kinds and 5 seeds each, compared each run with the enumeration: 2,800 runs in each setting.
  It found no other wrong optimum, with SCIP's defaults, without its dual reductions, or
  without the translation row. (An eighth size was stopped unfinished.)

The translation row itself is sound: the constrained program's true optimum is 2, since the
weight-2 logical above meets it. So this is a wrong answer from the solver, not from the
formulation. Without an independent certificate a program's "optimal" was always a claim about
SCIP. This test shows the claim can be false, which is what the registered method check was for.

### What it turned out to be

A wider hunt and a reading of SCIP's source (distance.py's `distance_ilp` docstring) found the
cause, and showed that the account above was incomplete.
- **The hunt.**
  - It covered 2,476 development codes (n = 8 to 50, both kinds, seeds 0 to 19): 99,040 runs.
  - SCIP's defaults returned a wrong "optimal" in 292 of them (0.29%), on 48 programs of 37
    codes.
  - Every wrong value was too high, by 1 or 2. Every one came with a genuine logical as its
    witness, so the witness check cannot catch it: only the lower bound is wrong.
  - Later hunts found it at d = 5 as well.
- **The cause.**
  - SCIP turns the program's parity rows into XOR constraints. On a program where some variables
    are already fixed, its presolving of those constraints can wrongly conclude that the program
    is infeasible, or cut off every optimum.
  - The wrong conclusion reaches the answer by two routes. One is rapid learning, which solves a
    copy of the problem in a sub-SCIP and passes back bounds and conflicts. The other is the main
    presolve after a restart.
  - A reduced reproduction, with dual reductions and rapid learning both off, still declares a
    feasible program infeasible in presolve.
- **Why the switches above seemed to fix it.** Turning off dual reductions or the translation row
  changes which fixings happen. It does not remove the fault.
  - Without the translation row, SCIP was still wrong on 3 programs.
  - With dual reductions off, stress tests that add fixings while keeping a lightest logical
    feasible still produced a false "infeasible".
- **Why no single presolver was to blame.** Turning one off in the main SCIP did not reach rapid
  learning's sub-SCIP, which resets presolving to SCIP's defaults.

**The fix** (`distance.SCIP_FIX`, now distance_ilp's default and recorded in every result):
constraints/xor/maxprerounds = 0 and separating/rapidlearning/freq = -1.
- **The evidence.** No wrong answer:
  - on the 48 programs and the registered code at 20 seeds;
  - in 5,520 stress solves;
  - in a re-run of the whole hunt at 10 seeds (49,520 runs);
  - in an independent verifier's hunt of 33,682 runs and 10,710 stress solves.
- **The cost.** It was no slower: 0.79 times the defaults' total time on 16 hard runs (d = 12 to
  16).

**The search.** It now runs passes with bound 2, 3, 4, ... in one process and stops at the first
logical found, whose weight is then d.
- **Speed.** The two stalled codes take 0.13 s, and [[288,12,18]] 18 s (180 s before). From (0, lm),
  two sets of hard development codes took 10 and 33 times less time in total, and every code
  finished where the old search had timed out on 17. From every qubit it can cost up to about
  1.35 times the single pass.
- **A lower bound.** A run stopped at its limit now has one: the last bound whose pass completed
  with nothing found.

## The re-test (`examples/qec-distance-2`)

Registered and pushed before it ran, on codes, sizes and seeds that no development had touched.
The verdict: **the instruments hold**, with no failure in any part.

| Part | What | Result |
| --- | --- | --- |
| (a) against enumeration | 50 fresh codes at 2x13 and 3x9: both kinds of d, the program at 5 seeds, the search from every qubit and from (0, lm) | 50 of 50 |
| (b) the known faults (a regression) | the 38 fault codes, both kinds, 20 seeds each | 38 of 38 right |
| (c) program against search | 14 fresh trinomial codes at 7 sizes, n = 96 to 210, d = 4 to 16 | 12 agree, 2 consistent (the program at its 20-minute limit with 13 ≤ d ≤ 16, both searches 16), 0 disagree; both searches completed on all 14 |
| (d) known answers (not blind) | the 12 published codes and the 2 codes the old search stalled on | 14 of 14 reproduced ([[288,12,18]] by the search in 18 s; the program at its 60-minute limit with 13 ≤ d ≤ 18) |
| (e) the toric code | 6 new sizes, n = 90 to 510, three instruments | 6 of 6 |
| (f) power against the fault | 142 fresh high-k codes, n = 56 to 80, of the families where the fault lives; the program at 20 seeds under the fix, and under SCIP's defaults as an unjudged control | 142 of 142 right under the fix; the defaults were wrong on 3 codes in 20 of 5,680 runs (3 for d = 2, 6 for d = 5, 5 for d = 4) |

Part (f) shows that the test could see the fault, on codes nobody had looked at, and that the fix
removed it there. The run was interrupted once by a container restart; resume rerun the one
unfinished job.

## What this establishes

- **The published distances.** All twelve, including d = 18 for [[288,12,18]], hold by an exact
  method built here and checked independently, run blind to the published values. The gross
  code's distance takes the search 0.2 s.
- **The tools.** Both instruments, as fixed, passed a registered test on fresh codes.
  - The search is the fast one on codes like these.
  - The program, with SCIP_FIX, gives exact values and checked bounds. Its lower bound still rests
    on SCIP, now on a setting tested hard against the fault.
  - Where the two run together, their intervals must meet, which guards each against the other's
    errors.
- **Not established.**
  - The search's lower bounds rest on its argument and its code. Two registered tests checked them
    against other methods, but nothing certifies them independently.
  - SCIP's fault is fixed for this program by switching features off, not repaired in SCIP; a
    different program might meet another fault.
  - The codes.json entries are still transcriptions from search summaries of the papers, now
    consistent with both their published k and their published d.

## The open distances (`examples/qec-open-distance`)

**Result (registered, run 2026-10-23): [[360,12]] has distance exactly 24, and [[756,16]] has
24 <= d <= 34.** Bravyi et al. give both distances only as upper bounds, [[360,12,<=24]] and
[[756,16,<=34]].

- **The codes.**
  - [[360,12]]: l = 30, m = 6, A = x^9 + y + y^2, B = y^3 + x^25 + x^26.
  - [[756,16]]: l = 21, m = 18, A = x^3 + y^10 + y^17, B = y^5 + x^3 + x^19.
  - They were read from several text copies of the paper's table, since the paper was not
    reachable from here. Their k (12 and 16) was the only thing computed on them before
    registration.
- **The instruments**, both new and both checked against enumeration on small codes first.
  - **The window.** Random information sets give light logicals, so it yields upper bounds, each
    with a witness checked independently.
  - **The split search.** The exhaustive search above, with each pass shared among 16 processes
    on 4 cores by a hash of the search node. A pass at bound b with no find proves d >= b.
- **[[360,12]]: d = 24.**
  - All 4 window seeds reached weight 24 in 30 minutes, and none went lower.
  - The search's passes up to bound 24 found nothing, in 1.9 hours. The pass at 24 alone took
    70 minutes and 2.5 x 10^11 nodes.
  - So no logical is lighter than 24, and a checked one weighs 24.
- **[[756,16]]: 24 <= d <= 34.**
  - Three of the four window seeds reached 34, the fourth 36, and none went lower. That gives a
    checked witness for the published bound, but no improvement.
  - The search proved d >= 24 in 2.4 hours. Its pass at 25 ran for the remaining 5.6 hours of
    its 8-hour budget without finishing, so it shows nothing. (d is even for codes of this form,
    as proved in the census, so d >= 23 already gives d >= 24.)
- **The verdict: hold.** H1 (d = 24 for [[360,12]]) and H2 (the window's least is 34 for
  [[756,16]]) hold. H4 (every witness checked, k as published, passes consecutive, every
  record made by the registered settings and code) holds. H3, reported and not judged, estimated
  the [[756,16]] lower bound at 18 to 24; it reached 24. `lattice-lab verify` finds the ledger
  sound.
- **What is not new.**
  - Later work claims d = 24 for [[360,12]], and a lower bound of 30 for [[756,16]], with other
    tools. Both claims were seen secondhand before registration, so ours is an
    independent confirmation of the first, by an exhaustive search and a checked witness.
  - Our lower bound for [[756,16]] is below that claim, and so adds no new bound.
- **What it rests on.** The lower bounds rest on the search's argument and code, the
  translation argument behind the anchors (0, lm), and the split's coverage. The tests check the
  split against enumeration, and check that the parts add up to the unsplit pass.

## Next

1. **Done:** both instruments fixed and retested (above).
2. **The census of code families** (step 2 of next-direction.md), with the search for exact
   distances, the program as a cross-check, and both together where a code is hard. Stage 1 is
   done ([code-census.md](code-census.md)), and stage 2 is being registered.
3. **Done: the open distances of larger published codes** (below): [[360,12]] has d = 24;
   [[756,16]] has 24 <= d <= 34.
4. **[[756,16]] beyond 24.** The search's next pass (bound 25, which would show d >= 26, d being
   even) needs about 7 hours on 4 cores, and the cost grows about tenfold per 2 of bound, so the
   pass at 29 (which would show d >= 30) would take about a month. A stronger lower-bound method would need
   more of the code's symmetry than the translations the anchors (0, lm) use, or a different
   method altogether.
</document>
<document path="examples/qec-open-distance/parts.py">
"""
Two instruments for codes too large for examples/qec-distance's search on one core: that search
with each pass shared among processes (`search`, search_parts.c), and an upper bound by random
information sets (`window`, window.c). Both build their input from examples/qec-distance's
distance.py (bb's bitmask rows and `_logicals_bits`), in the format of its search.c, and every
witness either reports is checked by distance.verify_witness.

**The split search.** search_parts.c is search.c with a split: given (depth, parts, part), a
node whose set S has `depth` qubits is searched only by the part chosen by a hash of S's qubits
in the order they were added, and every part searches every node above that depth. A node's
place in the tree, and so its set and order, does not depend on the traversal: the children of
a node are the candidates of its check of fewest candidates, which depends on S, the exclusions
and the anchor, not on the best so far. Pruning does depend on the best so far, but only removes
subtrees, so a node at the split depth that one part reaches is the same node, with the same
subtree below it, in any part that reaches it. The parts' subtrees at that depth are therefore
disjoint, and every node at that depth that the unsplit pass would search (with the best it would
have) is searched by its own part. `search` runs passes b = first, first + 1, ... in turn, each
as `parts` processes of one pass with bound b (search.c's single pass: first = bound = b, which
lowers its bound to each find), at most `workers` at once, and stops after the first pass in
which some part finds a logical, or when the time is up.

- A pass in which no part finds a logical shows that no logical of the kind has weight below b:
  the unsplit pass with bound b keeps no leaf (search.c's argument), since each of its nodes at
  the split depth was searched by its own part with the same best (b, no part having lowered
  it), and its nodes above that depth by every part.
- A pass in which some part finds one gives the least weight below b exactly: each part ends
  with the least weight of a logical in its subtrees (or b), since a part lowers its bound only
  to weights it has found, and so prunes only subtrees with nothing lighter than its best; the
  least over parts is the least below b.
So d >= b after a pass at b with no find, and d = the least weight found in the first pass that
finds one, whatever the earlier passes did; earlier passes only bound the work. A pass stopped
by the time limit shows nothing; the lower bound is the largest b of a finished pass without a
find. Anchors: (0, lm) by distance_ilp's translation argument (distance.py), or every qubit.

**The window.** window.c draws a random order of the qubits and reduces a basis of ker H_X (kind
Z) to the reduced echelon form whose pivots come first in that order; each row is a codeword, and
each row with a nonzero logical label is a logical. A logical whose support meets the pivots in
one position is a row of that iteration. It gives upper bounds only: the lightest logical found
in its time, with its witness, which `window` checks. Seeds are given, so a run is repeatable up
to the number of iterations the time allows.
"""

from __future__ import annotations

import atexit
import functools
import hashlib
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))
sys.path.insert(0, str(HERE.parent / "qec-distance"))

import bb  # noqa: E402
import distance  # noqa: E402

SEARCH_C = HERE / "search_parts.c"
WINDOW_C = HERE / "window.c"


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.cache
def binary(source: str) -> tuple[str, str]:
    """`source` compiled with the system's cc into a temporary directory (removed when the
    process exits), once per process; and the compiler's version line."""
    directory = Path(tempfile.mkdtemp(prefix="qec-parts-"))
    atexit.register(shutil.rmtree, directory, True)
    out = directory / Path(source).stem
    subprocess.run(["cc", "-O2", "-o", str(out), source], check=True, capture_output=True)
    version = subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout
    return str(out), version.splitlines()[0] if version else "cc"


def _code(A, B, ell: int, m: int, kind: str):
    """The checks (as bitmask rows) and the logical labels of each qubit, as search.c reads them,
    checked against bb.k_linalg."""
    if kind not in distance.KINDS:
        raise ValueError(kind)
    n = 2 * ell * m
    hx, hz = distance._bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    labels = distance._logicals_bits(stabilizers, checks, n)
    k = bb.k_linalg(A, B, ell, m)
    if len(labels) != k:
        raise RuntimeError(f"{len(labels)} logicals found, but k = {k}")
    if not labels or len(labels) > 128 or n > 2048 or len(checks) > 1024:
        raise ValueError("no logicals, or beyond the C programs' limits")
    rows = []
    for row in checks:
        support = [t for t in range(n) if row >> t & 1]
        rows.append(" ".join(map(str, [len(support), *support])))
    marks = []
    for t in range(n):
        x = sum((v >> t & 1) << j for j, v in enumerate(labels))
        marks.append(f"{x & (2**64 - 1):x} {x >> 64:x}")
    return n, len(checks), k, rows, marks


def _run(argv: list[str], text: str, limit: float):
    """Run a C program with `text` on stdin for at most `limit` seconds: (stdout, finished)."""
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)  # fmt: skip
    try:
        stdout, stderr = proc.communicate(text, timeout=max(limit, 0.001))
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, _ = proc.communicate()
        return stdout, False
    if proc.returncode:
        raise RuntimeError(f"{argv[0]} failed: {stderr.strip()}")
    return stdout, True


def _finds(stdout: str) -> list[list[int]]:
    out = []
    for words in map(str.split, stdout.splitlines()):
        if words[:1] == ["best"] and len(words) >= 2 and len(words) == int(words[1]) + 2:
            out.append([int(q) for q in words[2:]])
    return out


def search(A, B, ell: int, m: int, kind: str = "Z", anchors=None, first: int = 2,
           last: int = distance.SEARCH_BOUND, parts: int = 4, depth: int = 6, workers: int = 4,
           time_limit: float = 3600.0, on_pass=None) -> dict:  # fmt: skip
    """The least weight of a logical of the given kind, by passes b = first, ..., last of the
    split search (module docstring), each pass as `parts` processes, at most `workers` at once.
    `on_pass(entry)` is called after each finished pass with its record (bound, found, the
    least weight found or None, its witness, its wall-clock seconds, and each part's nodes
    and seconds).

    Returns status ("complete": a pass found a logical, and d is exact; "bound": the passes ran
    to `last` without a find, so d >= last; "timelimit"); d; lower (d, or the largest bound of a
    finished pass without a find, or None); upper and witness (verified, or an error is raised);
    passes; and the settings."""
    if anchors is None:
        starts = list(range(2 * ell * m))
    else:
        starts = [int(a) for a in anchors]
    n, r, k, rows, marks = _code(A, B, ell, m, kind)
    exe, compiler = binary(str(SEARCH_C))
    start = time.time()
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": k, "first": first, "last": last,
           "parts": parts, "depth": depth, "workers": workers,
           "anchors": "all" if anchors is None else starts, "time_limit": time_limit,
           "compiler": compiler, "search_parts_c_sha256": sha256(SEARCH_C)}  # fmt: skip
    passes, lower, status, witness = [], None, "bound", None
    for b in range(first, last + 1):
        text = "\n".join([f"{n} {r} {k} {b} {b} {len(starts)}", " ".join(map(str, starts)),
                          *rows, *marks]) + "\n"  # fmt: skip

        t_pass = time.time()

        def part(p, b=b, text=text):
            t0 = time.time()
            stdout, done = _run([exe, str(depth), str(parts), str(p)], text,
                                time_limit - (time.time() - start))  # fmt: skip
            nodes = None
            for words in map(str.split, stdout.splitlines()):
                if words[:1] == ["done"] and len(words) == 2:
                    nodes = int(words[1])
            if done and nodes is None:
                raise RuntimeError("search_parts.c ended without finishing")
            finds = _finds(stdout)
            return {"part": p, "finished": done, "nodes": nodes,
                    "seconds": round(time.time() - t0, 3),
                    "least": len(finds[-1]) if finds else None,
                    "witness": finds[-1] if finds else None}  # fmt: skip

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(part, range(parts)))
        if not all(x["finished"] for x in results):
            status = "timelimit"
            break
        found = [x for x in results if x["witness"]]
        best = min(found, key=lambda x: x["least"]) if found else None
        if best:
            check = distance.verify_witness(A, B, ell, m, kind, best["witness"])
            if not check["logical"] or check["weight"] != best["least"] or best["least"] >= b:
                raise RuntimeError(f"part {best['part']} of pass {b} gave a bad witness")
            witness = best["witness"]
        entry = {"bound": b, "found": bool(best), "least": best["least"] if best else None,
                 "witness": witness if best else None, "seconds": round(time.time() - t_pass, 3),
                 "parts": [{key: x[key] for key in ("part", "nodes", "seconds", "least")}
                           for x in results]}  # fmt: skip
        passes.append(entry)
        if on_pass:
            on_pass(entry)
        if best:
            status = "complete"
            break
        lower = b
    d = len(witness) if status == "complete" else None
    return {**out, "status": status, "d": d, "lower": d if d is not None else lower,
            "upper": d, "witness": witness, "passes": passes,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


def window(A, B, ell: int, m: int, kind: str = "Z", seeds=(0,), seconds: float = 60.0,
           workers: int = 4) -> dict:  # fmt: skip
    """The lightest logical of the given kind found by window.c in `seconds` of wall clock for
    each seed (in parallel, at most `workers` at once): an upper bound, with its witness checked
    by distance.verify_witness. Returns upper, witness, and for each seed its least weight,
    iterations and the weights it found in turn."""
    n, r, k, rows, marks = _code(A, B, ell, m, kind)
    exe, compiler = binary(str(WINDOW_C))
    lm = ell * m

    def one(seed):
        text = "\n".join([f"{n} {r} {k} {int(seed)} {float(seconds)}", *rows, *marks]) + "\n"
        stdout, done = _run([exe], text, seconds + 600)
        if not done:
            raise RuntimeError("window.c did not stop")
        dim = iterations = None
        for words in map(str.split, stdout.splitlines()):
            if words[:1] == ["dim"]:
                dim = int(words[1])
            elif words[:1] == ["done"]:
                iterations = int(words[1])
        if dim != lm + k // 2 or iterations is None:
            raise RuntimeError(f"window.c: kernel dimension {dim}, expected {lm + k // 2}")
        finds = _finds(stdout)
        for f in finds:
            check = distance.verify_witness(A, B, ell, m, kind, f)
            if not check["logical"]:
                raise RuntimeError(f"window.c seed {seed} gave a bad witness")
        return {"seed": int(seed), "iterations": iterations,
                "weights": [len(f) for f in finds],
                "least": len(finds[-1]) if finds else None,
                "witness": finds[-1] if finds else None}  # fmt: skip

    with ThreadPoolExecutor(max_workers=workers) as pool:
        runs = list(pool.map(one, seeds))
    best = min((x for x in runs if x["witness"]), key=lambda x: x["least"], default=None)
    return {"kind": kind, "l": ell, "m": m, "n": n, "k": k, "seconds": seconds,
            "upper": best["least"] if best else None, "witness": best["witness"] if best else None,
            "runs": [{key: x[key] for key in ("seed", "iterations", "weights", "least")}
                     for x in runs],
            "compiler": compiler, "window_c_sha256": sha256(WINDOW_C)}  # fmt: skip
</document>
<document path="examples/qec-open-distance/search_parts.c">
/*
 * examples/qec-distance/search.c with one addition, the split (below); otherwise unchanged.
 *
 * The least weight of a nontrivial codeword, by an exhaustive check-driven search whose bound is
 * raised one at a time (iterative deepening). distance.py (distance_search) builds the input,
 * runs this program and states why the search is exact. Integer arithmetic only: no LP, no
 * floating point.
 *
 * Input on stdin, whitespace separated:
 *   n r k first bound a  qubits, checks, logical labels (k <= 128), the first and the last
 *                        search bounds (1 <= first <= bound <= 64), and the number of anchors
 *   a anchors            the qubits to search from, each in turn as the least qubit of a codeword
 *   r rows: w q_1..q_w   the support of each check (w <= 64)
 *   n labels: lo hi      for each qubit, the bits j of the logicals L_j that contain it, as two
 *                        hexadecimal 64-bit words
 * Output, each line flushed at once, so that a run stopped from outside keeps what it found:
 *   "best w q_1 .. q_w"  each time a lighter nontrivial codeword is found;
 *   "pass b nodes ms"    when the pass with bound b ends without finding one, so that none has
 *                        weight below b (the pass's nodes and milliseconds of wall clock);
 *   "done nodes"         when the search ends (the nodes of every pass).
 *
 * The passes run with bounds b = first, first + 1, ..., bound, and stop after the first pass
 * that finds a nontrivial codeword. `proven` is the weight that no nontrivial codeword is known
 * to be below: 1 at the start (a nontrivial codeword is nonzero), then b after a pass with bound
 * b that found none. The search ends at once when a find's weight equals it. With first = bound
 * there is one pass, which keeps lowering its bound to each find.
 *
 * A pass with bound b, for an anchor a, grows a set S from {a}. While S has a nonzero syndrome
 * it takes the unsatisfied check with the fewest candidates (qubits above a, not in S, not
 * excluded) and branches on each candidate in turn, excluding it from the later branches. A set
 * with zero syndrome is a leaf, recorded when its label is nonzero and it is lighter than the
 * best so far (b at the start of the pass). A branch stops when |S| + ceil(unsatisfied / maxcol)
 * reaches the best so far (maxcol: the most checks any qubit is in).
 *
 * A split (three arguments: depth, parts, part) shares a pass among parts processes. A node
 * whose set S has `depth` qubits is searched only by the part that a hash of its qubits, in the
 * order they were added, picks; the nodes above that depth are searched by every part. The hash
 * depends on the node alone, not on the order of the traversal, so the parts' subtrees at that
 * depth are disjoint and together are all of them, whatever each part's best so far.
 */
#ifdef __linux__
#define _GNU_SOURCE
#include <signal.h>
#include <sys/prctl.h>
#endif
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 2048
#define MAXR 1024
#define MAXW 64
#define WN (MAXN / 64)
#define WR (MAXR / 64)

static int n, r, best, proven, stop, maxcol, anchor, wn, wr;
static int rowsz[MAXR], rows[MAXR][MAXW];
static uint64_t colmask[MAXN][WR];
static uint64_t lab_lo[MAXN], lab_hi[MAXN];
static int S[MAXW];
static long long nodes;
static int split_depth, split_parts = 1, split_part;

static int excluded(const uint64_t *ex, int q) { return (int)((ex[q >> 6] >> (q & 63)) & 1); }

static long long milliseconds(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (long long)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}

static void record(int size) {
    best = size;
    printf("best %d", size);
    for (int i = 0; i < size; i++) printf(" %d", S[i]);
    printf("\n");
    fflush(stdout);
    if (size <= proven) stop = 1; /* nothing lighter exists */
}

static int other_part(int size) {
    uint64_t h = 1469598103934665603ULL; /* FNV-1a over the qubits of S, in order */
    for (int i = 0; i < size; i++) {
        h ^= (uint64_t)S[i];
        h *= 1099511628211ULL;
    }
    return (int)(h % (uint64_t)split_parts) != split_part;
}

static void search(int size, const uint64_t *syn, uint64_t llo, uint64_t lhi, const uint64_t *ex) {
    if (split_parts > 1 && size == split_depth && other_part(size)) return;
    nodes++;
    int u = 0;
    for (int w = 0; w < wr; w++) u += __builtin_popcountll(syn[w]);
    if (u == 0) {
        if ((llo | lhi) && size < best) record(size);
        return;
    }
    if (size + (u + maxcol - 1) / maxcol >= best) return;
    int check = -1, fewest = MAXW + 1;
    for (int w = 0; w < wr; w++) {
        for (uint64_t x = syn[w]; x; x &= x - 1) {
            int c = w * 64 + __builtin_ctzll(x), count = 0;
            for (int t = 0; t < rowsz[c]; t++) {
                int q = rows[c][t];
                count += q > anchor && !excluded(ex, q);
            }
            if (count == 0) return;
            if (count < fewest) {
                fewest = count;
                check = c;
            }
        }
    }
    uint64_t child_ex[WN], child_syn[WR];
    memcpy(child_ex, ex, sizeof(uint64_t) * wn);
    for (int t = 0; t < rowsz[check] && !stop; t++) {
        int q = rows[check][t];
        if (q <= anchor || excluded(child_ex, q)) continue;
        child_ex[q >> 6] |= 1ULL << (q & 63);
        for (int w = 0; w < wr; w++) child_syn[w] = syn[w] ^ colmask[q][w];
        S[size] = q;
        search(size + 1, child_syn, llo ^ lab_lo[q], lhi ^ lab_hi[q], child_ex);
    }
}

static int fail(const char *why) {
    fprintf(stderr, "search: %s\n", why);
    return 1;
}

int main(int argc, char **argv) {
    int k, first, bound, count;
    if (argc == 4) {
        split_depth = atoi(argv[1]);
        split_parts = atoi(argv[2]);
        split_part = atoi(argv[3]);
        if (split_depth < 2 || split_parts < 1 || split_part < 0 || split_part >= split_parts)
            return fail("bad split");
    } else if (argc != 1)
        return fail("usage: search [depth parts part]");
#ifdef __linux__
    prctl(PR_SET_PDEATHSIG, SIGKILL); /* die with the process that started the search */
#endif
    if (scanf("%d %d %d %d %d %d", &n, &r, &k, &first, &bound, &count) != 6)
        return fail("bad header");
    if (n < 1 || n > MAXN || r < 0 || r > MAXR || k < 0 || k > 128 || first < 1 ||
        first > bound || bound > MAXW)
        return fail("size out of range");
    if (count < 0 || count > n) return fail("bad anchor count");
    int *anchors = malloc(sizeof(int) * (count ? count : 1));
    for (int i = 0; i < count; i++)
        if (scanf("%d", &anchors[i]) != 1 || anchors[i] < 0 || anchors[i] >= n)
            return fail("bad anchor");
    wn = (n + 63) / 64;
    wr = (r + 63) / 64;
    for (int i = 0; i < r; i++) {
        if (scanf("%d", &rowsz[i]) != 1 || rowsz[i] < 0 || rowsz[i] > MAXW)
            return fail("bad row weight");
        for (int t = 0; t < rowsz[i]; t++) {
            int q;
            if (scanf("%d", &q) != 1 || q < 0 || q >= n) return fail("bad row entry");
            rows[i][t] = q;
            colmask[q][i >> 6] ^= 1ULL << (i & 63);
        }
    }
    maxcol = 1;
    for (int q = 0; q < n; q++) {
        unsigned long long lo, hi;
        if (scanf("%llx %llx", &lo, &hi) != 2) return fail("bad label");
        lab_lo[q] = lo;
        lab_hi[q] = hi;
        int column = 0;
        for (int w = 0; w < wr; w++) column += __builtin_popcountll(colmask[q][w]);
        if (column > maxcol) maxcol = column;
    }
    long long total = 0;
    proven = 1;
    for (int b = first; b <= bound; b++) {
        long long start = milliseconds();
        best = b;
        nodes = 0;
        for (int i = 0; i < count && !stop; i++) {
            uint64_t syn[WR], ex[WN];
            anchor = anchors[i];
            memset(ex, 0, sizeof ex);
            ex[anchor >> 6] |= 1ULL << (anchor & 63);
            memcpy(syn, colmask[anchor], sizeof syn);
            S[0] = anchor;
            search(1, syn, lab_lo[anchor], lab_hi[anchor], ex);
        }
        total += nodes;
        if (best < b) break; /* a pass that finds a codeword ends at the least weight */
        proven = b;
        printf("pass %d %lld %lld\n", b, nodes, milliseconds() - start);
        fflush(stdout);
    }
    printf("done %lld\n", total);
    free(anchors);
    return 0;
}
</document>
<document path="examples/qec-distance/distance.py">
"""
Exact distances of bivariate bicycle codes: an integer program solved by SCIP, an enumeration
and a search that share nothing with it, and an independent check of the programs' witnesses.

A bivariate bicycle code (examples/qec-bb/bb.py) is a pair A, B in R = GF(2)[x, y] /
(x^l - 1, y^m - 1), acting on GF(2)^(lm) in bb's convention: (A v)(i, j) = Σ v(i - p, j - q)
over the monomials x^p y^q of A, and A^T is multiplication by A* = A(x^-1, y^-1). The checks are
H_X = [A | B] and H_Z = [B^T | A^T], on n = 2lm qubits (the left block, then the right; position
(i, j) of a block is index i m + j). Since AB = BA, H_X H_Z^T = 0, and k = n - rank H_X -
rank H_Z (bb.k_linalg).

- **Definitions.** A Z-logical is a vector c with H_X c = 0 and c not in the rowspace of H_Z; an
  X-logical has H_Z c = 0 and c not in the rowspace of H_X. d_Z and d_X are their least weights,
  and the code's distance is d = min(d_X, d_Z). A code with k = 0 has no logicals, and no
  distance. Since the rowspace of H_Z is the orthogonal complement of ker H_Z, and ker H_Z is the
  rowspace of H_X plus the span of the X-logicals, a vector c in ker H_X is a Z-logical exactly
  when L·c = 1 for some vector L of a basis of the X-logicals modulo the rowspace of H_X
  (`logical_basis`); the integer program uses that test, and the enumeration the other one.
- **d_X = d_Z for every bivariate bicycle code.** Let P be the inversion of the torus,
  (P u)(i, j) = u(-i, -j), and Φ(u, v) = (P v, P u): swap the two blocks and invert both. In
  bb's convention P A P = A^T, since (P A P v)(i, j) = Σ (P v)(-i - p, -j - q) =
  Σ v(i + p, j + q) = (A^T v)(i, j), and likewise for B. So
  P H_X Φ (u, v) = P A P v + P B P u = B^T u + A^T v = H_Z (u, v), that is, H_Z = P H_X Φ.
  P is invertible and Φ is a symmetric involution, so ker H_Z = Φ ker H_X and the rowspace of
  H_Z is Φ applied to the rowspace of H_X. Φ therefore maps the Z-logicals onto the
  X-logicals, and it permutes coordinates, so it keeps weight: d_X = d_Z, and d = d_Z.
  `inversion_swap` builds P and Φ; the tests check H_Z = P H_X Φ entry by entry, and
  d_X = d_Z by computation.
- **What a result rests on.** An upper bound is certified: each comes with a witness, and
  `verify_witness` checks it with bb's bitmask rows and ranks (bb.rank_gf2), not with the numpy
  algebra the program is built from. A lower bound, and so optimality, rests on SCIP: its
  presolve (which turns the parity rows into its XOR constraints and adds its own symmetry
  handling), its branch and bound, its floating-point LP solver within its tolerances, and its
  conclusion that the objective is integral, all applied to the formulation in `distance_ilp`,
  whose soundness is argued there. SCIP 10.0 was found to be wrong on this formulation: its
  presolving of the XOR constraints cut off every optimal solution of some programs with fixed
  variables, and its "optimal" was then too high, with a witness that passes the check. The
  program therefore runs with XOR presolving and rapid learning off (SCIP_FIX, recorded in
  every result's settings; `distance_ilp` gives the fault and the evidence for the fix). The
  lower bound then rests on those two being the routes by which that presolving reaches the
  answer; the fault's place in SCIP's code was not found. It also rests on `logical_basis`
  (numpy elimination) being complete: with fewer than k logicals the program would miss some
  Z-logicals, and its optimum and dual bound could exceed d_Z. The program records the basis's
  size as k, and the study compares it with bb.k_linalg at run time. Nothing in the program
  certifies a lower bound independently. Where the enumeration is feasible (`distance_brute`,
  dim ker H_X at most BRUTE_CAP), it gives the exact value by a route that shares no code with
  the program but bb's matrices; where the search completes (`distance_search`, a C program),
  so does it, with integer arithmetic only, no LP and no floating point.
"""

from __future__ import annotations

import atexit
import functools
import math
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))

import bb  # noqa: E402

KINDS = ("Z", "X")
SEED = 0  # SCIP's randomization/randomseedshift
# Against SCIP 10.0's fault in presolving XOR constraints (distance_ilp's docstring): no XOR
# presolving in the main SCIP, and no rapid learning, whose sub-SCIP presolves with SCIP's
# defaults. Neither changes the program or its optimum.
SCIP_FIX = {"constraints/xor/maxprerounds": 0, "separating/rapidlearning/freq": -1}
# SCIP's limits/memory, in MB. It bounds SCIP's own estimate of its memory, which SCIP's
# parameter documentation says is lower than real use, not the process's RSS; 3000 leaves four
# runs at once a margin of about 3 GB below 15 GB for that difference.
MEMORY_MB = 3000
BRUTE_CAP = 28  # the largest dim ker H_X that distance_brute enumerates: 2^28 vectors, ~2 s
SEARCH_C = HERE / "search.c"
SEARCH_BOUND = 64  # the largest bound search.c accepts


# ---------------------------------------------------------------- the check matrices (numpy)


def multiplication(poly, ell: int, m: int) -> np.ndarray:
    """The lm x lm matrix of multiplication by poly over GF(2), in bb's convention: row (i, j)
    has a 1 in column (i - p, j - q) for each monomial x^p y^q. Repeated monomials cancel."""
    M = np.zeros((ell * m, ell * m), dtype=np.uint8)
    rows = np.arange(ell * m)
    i, j = rows // m, rows % m
    for p, q in poly:
        M[rows, ((i - p) % ell) * m + (j - q) % m] ^= 1
    return M


def check_matrices(A, B, ell: int, m: int) -> tuple[np.ndarray, np.ndarray]:
    """(H_X, H_Z) = ([A | B], [B^T | A^T]) as uint8 arrays of shape (lm, 2lm)."""
    a, b = multiplication(A, ell, m), multiplication(B, ell, m)
    return np.hstack([a, b]), np.hstack([b.T, a.T])


def inversion_swap(ell: int, m: int) -> tuple[np.ndarray, np.ndarray]:
    """(P, Φ): the torus's inversion (P u)(i, j) = u(-i, -j), lm x lm, and Φ(u, v) = (P v, P u),
    2lm x 2lm. H_Z = P H_X Φ (module docstring)."""
    lm = ell * m
    P = np.zeros((lm, lm), dtype=np.uint8)
    idx = np.arange(lm)
    P[idx, ((-(idx // m)) % ell) * m + (-(idx % m)) % m] = 1
    Phi = np.zeros((2 * lm, 2 * lm), dtype=np.uint8)
    Phi[:lm, lm:] = P
    Phi[lm:, :lm] = P
    return P, Phi


# ---------------------------------------------------------------- GF(2) linear algebra (numpy)


def rref(M: np.ndarray) -> tuple[np.ndarray, list[int]]:
    """The reduced row echelon form of M over GF(2) (nonzero rows only) and its pivot columns."""
    M = (np.asarray(M) % 2).astype(np.uint8)
    pivots: list[int] = []
    r = 0
    for c in range(M.shape[1]):
        if r == M.shape[0]:
            break
        below = np.flatnonzero(M[r:, c])
        if not below.size:
            continue
        p = r + int(below[0])
        if p != r:
            M[[r, p]] = M[[p, r]]
        hit = np.flatnonzero(M[:, c])
        M[hit[hit != r]] ^= M[r]
        pivots.append(c)
        r += 1
    return M[:r], pivots


def rank(M: np.ndarray) -> int:
    return len(rref(M)[1])


def kernel(M: np.ndarray) -> np.ndarray:
    """A basis of {v : M v = 0} over GF(2), one vector per row."""
    R, pivots = rref(M)
    n, pivot_set = M.shape[1], set(pivots)
    free = [c for c in range(n) if c not in pivot_set]
    K = np.zeros((len(free), n), dtype=np.uint8)
    K[np.arange(len(free)), free] = 1
    if pivots:
        K[:, pivots] = R[:, free].T
    return K


def logical_basis(A, B, ell: int, m: int, kind: str) -> np.ndarray:
    """k vectors, one per row, whose classes form a basis of the logicals of the given kind:
    ker H_Z modulo the rowspace of H_X for kind "X", ker H_X modulo the rowspace of H_Z for "Z".
    A kernel vector is kept when it is not in the span of the stabilizers and the vectors kept
    before it, and is stored reduced against them (still a logical of that kind)."""
    if kind not in KINDS:
        raise ValueError(kind)
    hx, hz = check_matrices(A, B, ell, m)
    of, stabilizers = (hz, hx) if kind == "X" else (hx, hz)
    R, pivots = rref(stabilizers)
    rows, pivots, out = list(R), list(pivots), []
    for v in kernel(of):
        w = v.copy()
        for p, row in zip(pivots, rows, strict=True):
            if w[p]:
                w ^= row
        if w.any():
            rows.append(w)
            pivots.append(int(np.flatnonzero(w)[0]))
            out.append(w)
    return np.array(out, dtype=np.uint8).reshape(len(out), of.shape[1])


# ---------------------------------------------------------------- the integer program (SCIP)


def scip_version() -> str:
    from pyscipopt import Model

    return f"SCIP {Model().version()} (pyscipopt {_pyscipopt_version()})"


def _pyscipopt_version() -> str:
    import pyscipopt

    return pyscipopt.__version__


def _non_default(model) -> dict:
    from pyscipopt import Model

    default = Model().getParams()
    return {k: v for k, v in sorted(model.getParams().items()) if default.get(k) != v}


def distance_ilp(
    A,
    B,
    ell: int,
    m: int,
    kind: str = "Z",
    time_limit: float = 600.0,
    memory_mb: float = MEMORY_MB,
    seed: int = SEED,
    translation: bool = True,
    configure=None,
    scip_fix: bool = True,
) -> dict:
    """The least weight of a logical of the given kind ("Z": H_X c = 0, c not in the rowspace
    of H_Z; "X": the same with H_X and H_Z exchanged), by one integer program solved by SCIP.

    The program, for kind Z (kind X exchanges H_X and H_Z): binary c_1..c_n; for each row h of
    H_X, h·c = 2 s_h with s_h an integer in [0, |h|/2]; for each vector L of
    logical_basis(..., "X"), L·c = 2 t_L + z_L with t_L an integer and z_L binary; Σ z_L >= 1;
    and, with `translation`, c_(0,0) + c_(lm + (0,0)) >= 1. Minimise Σ c. The parity rows say
    H_X c = 0 and the z's say L·c = 1 for some L, which for c in ker H_X is exactly "c is not in
    the rowspace of H_Z" (module docstring). So without the translation row, the optimum is d_Z.

    The translation row keeps the optimum. For g = x^a y^b, let T_g shift both blocks by g,
    T_g(u, v) = (g u, g v). R is commutative, so g commutes with A, B, A* and B*:
    H_X T_g (u, v) = g (A u + B v) = g H_X (u, v), and T_g (B w, A w) = (B g w, A g w). So T_g
    maps ker H_X into itself, and the rowspace of H_Z, {(B w, A w)}, into itself; being
    invertible, onto both. It therefore maps Z-logicals to Z-logicals, and it permutes
    coordinates, so it keeps weight. If c is a least-weight Z-logical and (i, j) is in the support
    of either block, T_g with g = x^-i y^-j moves that position to (0, 0): a least-weight
    Z-logical satisfying the row. The constrained optimum is therefore d_Z, and a lower bound for
    the constrained program is a lower bound for d_Z. (For kind X the same holds with A* and B*.)

    SCIP's fault, and the settings against it. SCIP's presolve turns the parity rows into its XOR
    constraints, and in SCIP 10.0 their presolving can cut off every optimal solution of a program
    in which some variables are already fixed, or declare it infeasible. SCIP makes such fixings
    itself (reduced-cost fixing, once a heuristic has found a solution), and the wrong conclusion
    reaches the answer by two routes: rapid learning, which solves a copy of the program in a
    sub-SCIP whose presolving it first resets to SCIP's defaults, and passes back a dual bound,
    conflicts or bound changes; and the main SCIP's own presolve after a restart. The registered
    test (examples/qec-distance) met it on a 4 x 5 code with d_X = 2: d_X = 3, status optimal, at
    seeds 0, 2 and 4. A hunt over 2,476 development codes (n = 8 to 50, both kinds, seeds 0 to 19)
    then found 292 wrong optima in 99,040 runs, on 48 (code, kind) programs of 37 codes, every one
    too high, by 1 or 2, at d from 2 to 4 (the range that hunt met, not a bound: a later one, over
    2,058 development codes with n = 8 to 156, found the defaults wrong at d = 5 too), and every one
    with a witness that passes verify_witness: only the lower bound was wrong. With `scip_fix` (the
    default) the program runs with SCIP_FIX, XOR presolving off (constraints/xor/maxprerounds 0) and
    rapid learning off (separating/rapidlearning/freq -1), both recorded in the settings. Neither
    changes the program. Under them the 48 programs and the 4 x 5 code gave the right d at every
    seed from 0 to 19 (1,000 runs), the whole hunt gave no wrong answer at seeds 0 to 9 (49,520
    runs), and 16 runs at d = 12 to 16 took 2,359 s in all against the defaults' 2,968 s (single
    runs on a shared machine). Turning off SCIP's dual reductions, the fix first proposed, gave the
    right d on those programs but not on one of 2,760 variants with further fixings, and about
    doubled the time. The XOR constraints and their propagation stay. In SCIP's source the XOR
    handler's presolving routines (applyFixings, and its pairwise, hash and clique presolving) run
    only in presolving. Its propagation stays on, the Gauss propagator among it
    (constraints/xor/gausspropfreq 5), which runs from propagation, reads the current fixings, fixes
    variables and can cut off a node; it was tested under stress: on 119 programs (those of the
    hunt's failures and of high k) with 30 variants each that fix further variables, SCIP_FIX gave
    no wrong answer in 10,710 solves, with the Gauss propagator or without it, where the defaults
    gave 23, and the later hunts' 33,682 runs under SCIP_FIX gave none. That the two routes are the
    only ones rests on reading SCIP's source (its other sub-SCIPs presolve nothing, or only propose
    solutions, which the main SCIP checks); the faulty statement itself was not found.
    scip_fix=False gives SCIP's defaults, the registered test's settings.

    Returns a dict: k (the number of logicals logical_basis found: the program is sound only if
    it is the code's k); status (SCIP's: "optimal", "timelimit", "memlimit", ..., or
    "no_logicals" when k = 0); d (the optimum, when optimal); upper (the best solution's weight,
    None if none was found) and lower (SCIP's dual bound less 1e-4, rounded up, the objective
    being integral: the slack absorbs a dual bound a rounding error above an integer, such as
    8.000000000000002, and can only weaken the bound, by one, for a dual bound less than 1e-4
    above an integer);
    witness (the best solution's support: a least-weight logical when optimal); seconds (wall
    clock, building the program included); nodes; the SCIP version; seed; scip_fix; the
    parameters set here (settings, SCIP_FIX among them); and every parameter that differs from
    SCIP's defaults (parameters). SCIP's time limit is wall clock (timing/clocktype 2). SCIP runs
    on one thread, its randomness comes from the fixed seed (randomization/randomseedshift), and
    a run with the same inputs and parameters is deterministic up to where a limit stops it.
    `configure`, if given, is called with the SCIP model before solving (for development;
    whatever it changes is recorded in parameters, not in settings).
    """
    from pyscipopt import Model, quicksum

    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    hx, hz = check_matrices(A, B, ell, m)
    checks = hx if kind == "Z" else hz
    detectors = logical_basis(A, B, ell, m, "X" if kind == "Z" else "Z")
    n, lm = 2 * ell * m, ell * m
    model = Model(f"distance-{kind}")
    model.hideOutput()
    settings = {"limits/time": float(time_limit), "limits/memory": float(memory_mb),
                "timing/clocktype": 2, "randomization/randomseedshift": int(seed),
                **(SCIP_FIX if scip_fix else {})}  # fmt: skip
    for name, value in settings.items():
        model.setParam(name, value)
    if configure is not None:
        configure(model)
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": len(detectors), "time_limit": time_limit,
           "memory_mb": memory_mb, "seed": seed, "translation": translation,
           "scip_fix": scip_fix, "solver": scip_version(), "settings": settings,
           "parameters": _non_default(model)}  # fmt: skip
    if not len(detectors):
        return {**out, "status": "no_logicals", "d": None, "upper": None, "lower": None,
                "dual_bound": None, "witness": None, "nodes": 0, "solving_seconds": 0.0,
                "seconds": round(time.time() - start, 3)}  # fmt: skip
    c = [model.addVar(f"c{i}", vtype="B") for i in range(n)]
    for r, row in enumerate(checks):
        support = np.flatnonzero(row).tolist()
        s = model.addVar(f"s{r}", vtype="I", lb=0, ub=len(support) // 2)
        model.addCons(quicksum(c[i] for i in support) == 2 * s)
    zs = []
    for j, row in enumerate(detectors):
        support = np.flatnonzero(row).tolist()
        t = model.addVar(f"t{j}", vtype="I", lb=0, ub=len(support) // 2)
        z = model.addVar(f"z{j}", vtype="B")
        model.addCons(quicksum(c[i] for i in support) == 2 * t + z)
        zs.append(z)
    model.addCons(quicksum(zs) >= 1)
    if translation:
        model.addCons(c[0] + c[lm] >= 1)
    model.setObjective(quicksum(c), "minimize")
    model.optimize()
    status = model.getStatus()
    witness = upper = None
    if model.getNSols():
        best = model.getBestSol()
        witness = [i for i in range(n) if model.getSolVal(best, c[i]) > 0.5]
        upper = len(witness)
    dual = model.getDualbound()
    lower = max(1, math.ceil(dual - 1e-4)) if math.isfinite(dual) and dual < 1e19 else None
    if status == "optimal":
        lower = upper
    return {**out, "status": status, "d": upper if status == "optimal" else None,
            "upper": upper, "lower": lower, "dual_bound": dual, "witness": witness,
            "nodes": model.getNTotalNodes(), "solving_seconds": round(model.getSolvingTime(), 3),
            "seconds": round(time.time() - start, 3)}  # fmt: skip


# ---------------------------------------------------------------- independent checks (bitmasks)


def _bit_rows(A, B, ell: int, m: int) -> tuple[list[int], list[int]]:
    """H_X and H_Z as bb builds them in k_linalg: one int per row, bit t for qubit t."""
    lm = ell * m
    a_rows, b_rows = bb._matrix_rows(A, ell, m), bb._matrix_rows(B, ell, m)
    a_cols, b_cols = bb._matrix_rows(A, ell, m, True), bb._matrix_rows(B, ell, m, True)
    hx = [a | (b << lm) for a, b in zip(a_rows, b_rows, strict=True)]
    hz = [b | (a << lm) for a, b in zip(a_cols, b_cols, strict=True)]
    return hx, hz


def verify_witness(A, B, ell: int, m: int, kind: str, support) -> dict:
    """Check, with bb's bitmask rows and bb.rank_gf2 only, that the vector with this support is
    a logical of the given kind: for Z, every row of H_X meets it evenly, and adding it to the
    rows of H_Z raises their rank (it is not in their span); for X, the same with H_X and H_Z
    exchanged. A support that passes certifies its weight as an upper bound on d of that kind."""
    if kind not in KINDS:
        raise ValueError(kind)
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    support = [int(i) for i in support]
    valid = len(set(support)) == len(support) and all(0 <= i < 2 * ell * m for i in support)
    c = sum(1 << i for i in set(support))
    in_kernel = all((row & c).bit_count() % 2 == 0 for row in checks)
    nontrivial = bb.rank_gf2([*stabilizers, c]) > bb.rank_gf2(stabilizers)
    return {"weight": len(set(support)), "valid_support": valid, "in_kernel": in_kernel,
            "nontrivial": nontrivial, "logical": valid and in_kernel and nontrivial}  # fmt: skip


def _kernel_bits(rows: list[int], n: int) -> list[int]:
    """A basis of {v : r·v = 0 for every row r}, by elimination on int bitmasks."""
    pivots: dict[int, int] = {}
    for r in rows:
        for p, prow in pivots.items():
            if r >> p & 1:
                r ^= prow
        if r:
            p = r.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= r
            pivots[p] = r
    return [(1 << f) | sum(1 << p for p, prow in pivots.items() if prow >> f & 1)
            for f in range(n) if f not in pivots]  # fmt: skip


def _words(x: int, count: int) -> list[int]:
    return [(x >> (64 * w)) & ((1 << 64) - 1) for w in range(count)]


def distance_brute(A, B, ell: int, m: int, kind: str = "Z", cap: int = BRUTE_CAP) -> dict:
    """The least weight of a logical of the given kind, by enumerating all of ker H_X (kind Z;
    ker H_Z for X). It shares nothing with distance_ilp but bb's matrices: bases of ker H_X and
    ker H_Z by elimination on bb's bitmask rows, and the test that c in ker H_X is outside the
    rowspace of H_Z exactly when z·c = 1 for some z in a basis of ker H_Z (the rowspace being
    ker H_Z's orthogonal complement). The 2^dim vectors are formed by XOR in numpy, as a table of
    all combinations of the first (up to 16) basis vectors, shifted by each combination of the
    rest. Refuses (ValueError) when dim exceeds `cap`. d is None when no vector is a logical
    (k = 0)."""
    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    n = 2 * ell * m
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    basis = _kernel_bits(checks, n)
    dual = _kernel_bits(stabilizers, n)
    dim = len(basis)
    if dim > cap:
        raise ValueError(f"dim ker = {dim} exceeds the enumeration cap {cap}")
    syndromes = [sum(((c & z).bit_count() & 1) << j for j, z in enumerate(dual)) for c in basis]
    wv, ws = (n + 63) // 64, max(1, (len(dual) + 63) // 64)
    vec = np.array([_words(c, wv) for c in basis], dtype=np.uint64).reshape(dim, wv)
    syn = np.array([_words(s, ws) for s in syndromes], dtype=np.uint64).reshape(dim, ws)
    low = min(dim, 16)
    tv = np.zeros((1 << low, wv), dtype=np.uint64)
    ts = np.zeros((1 << low, ws), dtype=np.uint64)
    for i in range(low):
        h = 1 << i
        tv[h : 2 * h] = tv[:h] ^ vec[i]
        ts[h : 2 * h] = ts[:h] ^ syn[i]
    weights = np.bitwise_count(tv).sum(axis=1, dtype=np.int64)
    best, witness = None, None
    hv, hs = np.zeros(wv, dtype=np.uint64), np.zeros(ws, dtype=np.uint64)
    for step in range(1 << (dim - low)):
        if step:  # Gray code over the remaining basis vectors: flip one per step
            flip = low + (step & -step).bit_length() - 1
            hv, hs = hv ^ vec[flip], hs ^ syn[flip]
        nontrivial = (ts ^ hs).any(axis=1)
        if not nontrivial.any():
            continue
        w = np.bitwise_count(tv ^ hv).sum(axis=1, dtype=np.int64) if step else weights
        w = np.where(nontrivial, w, n + 1)
        i = int(np.argmin(w))
        if best is None or w[i] < best:
            best = int(w[i])
            bits = _join(tv[i] ^ hv)
            witness = [t for t in range(n) if bits >> t & 1]
    return {"kind": kind, "d": best, "witness": witness, "dim": dim, "vectors": 1 << dim,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


def _join(words: np.ndarray) -> int:
    return sum(int(w) << (64 * i) for i, w in enumerate(words))


# ---------------------------------------------------------------- the search (C, bitmasks)


def _logicals_bits(of: list[int], stabilizers: list[int], n: int) -> list[int]:
    """A basis of ker(of) modulo the span of `stabilizers`, by elimination on int bitmasks: each
    kernel vector is reduced by leading bits against the stabilizers and the vectors kept before
    it, and kept, reduced, when something remains. Shares no code with logical_basis."""
    basis: dict[int, int] = {}

    def add(v: int) -> int:
        while v:
            p = v.bit_length() - 1
            if p not in basis:
                basis[p] = v
                return v
            v ^= basis[p]
        return 0

    for row in stabilizers:
        add(row)
    return [w for w in map(add, _kernel_bits(of, n)) if w]


@functools.cache
def _search_binary() -> tuple[str, str]:
    """search.c compiled with the system's cc into a temporary directory (removed when the
    process exits), once per process; and the compiler's version line."""
    directory = Path(tempfile.mkdtemp(prefix="qec-search-"))
    atexit.register(shutil.rmtree, directory, True)
    binary = directory / "search"
    subprocess.run(["cc", "-O2", "-o", str(binary), str(SEARCH_C)], check=True, capture_output=True)
    version = subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout
    return str(binary), version.splitlines()[0] if version else "cc"


def distance_search(
    A,
    B,
    ell: int,
    m: int,
    kind: str = "Z",
    bound: int = SEARCH_BOUND,
    anchors=None,
    time_limit: float = 1200.0,
    deepen: bool = True,
) -> dict:
    """The least weight of a logical of the given kind, if it is below `bound`, by an exhaustive
    check-driven search (search.c) whose bound is raised one at a time. It shares nothing with
    distance_ilp but bb's matrices: the checks are bb's bitmask rows, a vector c with H_X c = 0
    (kind Z) is nontrivial exactly when L·c = 1 for some L of a basis of the X-logicals modulo the
    rowspace of H_X found by bitmask elimination (`_logicals_bits`, whose size must be
    bb.k_linalg), and the search uses integer arithmetic only. For kind X, H_X and H_Z exchange.

    A pass with bound b. For each anchor a it grows a set S from {a}: while S has a nonzero
    syndrome it branches over the qubits above a of one unsatisfied check, each branch excluding
    the earlier ones; a set with zero syndrome is a leaf, kept when nontrivial and lighter than
    the best so far (b at the start); a branch stops when |S| + ceil(u / maxcol) reaches the best
    so far (u unsatisfied checks, each qubit in at most maxcol checks). Every leaf kept is a
    logical, so the best is an upper bound with its witness. The pass is exhaustive below b: let
    c be a least-weight logical, of weight w < b, whose least qubit is an anchor a. Some branch
    keeps S inside the support of c and its excluded qubits outside it, since c meets each check
    evenly and so meets the chosen unsatisfied one outside S, above a; the first such qubit in the
    check is a branch with that property. Its syndrome becomes zero only at S = c: an S strictly
    inside c with zero syndrome would make S and c + S codewords lighter than c, one of them
    nontrivial. It is not cut while the best exceeds w, since the qubits of c outside S must clear
    the u unsatisfied checks, so |S| + ceil(u / maxcol) <= w. So a pass keeps a leaf whenever
    some logical is lighter than b (c itself, if it keeps none before), and one that runs to its
    end ends with the best at w. A pass that keeps no leaf shows that no logical is lighter
    than b.

    The passes. Write d for the least weight of a logical of the kind. With `deepen` (the
    default) the passes run with b = 2, 3, ..., `bound` in turn, and the search stops at its
    first leaf kept. Pass b runs only after pass b - 1 kept none, so d >= b - 1 (d >= 1 before
    pass 2: a logical is nonzero). If d >= b, pass b keeps no leaf (each would be a logical
    lighter than b), and ends having shown d >= b. If d < b, then d = b - 1, and pass b keeps a
    leaf, whose weight w has b - 1 <= d <= w < b: w = d. So the first logical found has weight
    exactly d, and the passes before it show that nothing is lighter. A time-out stops a pass,
    not the argument: each pass that ended without a leaf still shows d >= its b, so the largest
    such b is a lower bound. Without `deepen` there is one pass, with b = `bound`, which runs to
    its end (unless it keeps a leaf of weight 1, which nothing can be lighter than): the search
    that study.py registered, which reaches d by lowering its bound from `bound` to each leaf
    kept, and so can go very deep before it meets a logical.

    `anchors`: None searches from every qubit, so every logical has its least qubit among them.
    (0, lm) is enough too, by distance_ilp's translation argument: a least-weight logical moved
    to contain qubit 0, if it meets the left block, has least qubit 0; one in the right block
    alone, moved to contain lm, has least qubit lm. The second rests on that argument, the first
    on nothing but the search.

    Returns a dict: status ("complete", "timelimit" when stopped after `time_limit` seconds of
    wall clock, or "no_logicals" when k = 0); d (exact, when complete and below the bound);
    lower (d; or the bound, when complete with nothing below it; at a time-out the largest b of
    a pass that ended without a leaf, None if there is none); upper and witness (the lightest
    logical found, None if none); nodes (of every pass, when complete); passes (for each pass
    that ended without a leaf, in order: its bound, nodes and seconds); deepen; k; bound;
    anchors; seconds; and the compiler. Requires a C compiler as `cc`."""
    if kind not in KINDS:
        raise ValueError(kind)
    start = time.time()
    n = 2 * ell * m
    hx, hz = _bit_rows(A, B, ell, m)
    checks, stabilizers = (hx, hz) if kind == "Z" else (hz, hx)
    labels = _logicals_bits(stabilizers, checks, n)
    if len(labels) != bb.k_linalg(A, B, ell, m):
        raise RuntimeError(f"{len(labels)} logicals found, but k = {bb.k_linalg(A, B, ell, m)}")
    starts = list(range(n)) if anchors is None else [int(a) for a in anchors]
    binary, compiler = _search_binary()
    out = {"kind": kind, "l": ell, "m": m, "n": n, "k": len(labels), "bound": bound,
           "deepen": deepen, "anchors": "all" if anchors is None else starts,
           "time_limit": time_limit, "compiler": compiler}  # fmt: skip
    if not labels:
        return {**out, "status": "no_logicals", "d": None, "lower": None, "upper": None,
                "witness": None, "nodes": 0, "passes": [],
                "seconds": round(time.time() - start, 3)}  # fmt: skip
    if not 1 <= bound <= SEARCH_BOUND or len(labels) > 128 or n > 2048 or len(checks) > 1024:
        raise ValueError("beyond search.c's limits")
    first = min(2, bound) if deepen else bound
    header = f"{n} {len(checks)} {len(labels)} {first} {bound} {len(starts)}"
    lines = [header, " ".join(map(str, starts))]
    for row in checks:
        support = [t for t in range(n) if row >> t & 1]
        lines.append(" ".join(map(str, [len(support), *support])))
    for t in range(n):
        x = sum((v >> t & 1) << j for j, v in enumerate(labels))
        lines.append(f"{x & (2**64 - 1):x} {x >> 64:x}")
    proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)  # fmt: skip
    try:
        stdout, stderr = proc.communicate("\n".join(lines) + "\n", timeout=time_limit)
        status = "complete"
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        status = "timelimit"
    if status == "complete" and proc.returncode:
        raise RuntimeError(f"search.c failed: {stderr.strip()}")
    witness, nodes, passes = None, None, []
    for words in map(str.split, stdout.splitlines()):
        if words[:1] == ["best"] and len(words) >= 2 and len(words) == int(words[1]) + 2:
            witness = [int(q) for q in words[2:]]
        elif words[:1] == ["pass"] and len(words) == 4:
            b, count, ms = map(int, words[1:])
            passes.append({"bound": b, "nodes": count, "seconds": ms / 1000})
        elif words[:1] == ["done"] and len(words) == 2:
            nodes = int(words[1])
    if status == "complete" and nodes is None:
        raise RuntimeError("search.c ended without finishing")
    upper = len(witness) if witness else None
    proven = passes[-1]["bound"] if passes else None
    if upper is not None and proven is not None and upper < proven:
        raise RuntimeError(f"search.c found weight {upper} after a pass with bound {proven}")
    if status == "complete" and upper is None and proven != bound:
        raise RuntimeError(f"search.c ended without a pass at its bound {bound}")
    exact = status == "complete" and upper is not None
    if status == "complete":
        lower = upper if exact else bound
    else:
        lower = proven
    return {**out, "status": status, "d": upper if exact else None, "lower": lower,
            "upper": upper, "witness": witness, "nodes": nodes, "passes": passes,
            "seconds": round(time.time() - start, 3)}  # fmt: skip


# ---------------------------------------------------------------- tori


def torus_type(ell: int, m: int) -> tuple[int, ...]:
    """The isomorphism type of Z_l x Z_m: its prime-power cyclic factors, sorted. Codes on
    isomorphic tori correspond under the isomorphism (it carries the group ring along), so a
    held-out size excludes every size of the same type, not only (l, m) and (m, l). The converse
    does not hold: codes on non-isomorphic groups of the same order can in principle be
    equivalent under a permutation of qubits, so a different type alone does not show that two
    codes differ. n and k are invariants of that equivalence, and the study's development record
    (study.py, EXCLUDED_SEEN) uses them."""
    out = []
    for n in (ell, m):
        p = 2
        while n > 1:
            if n % p == 0:
                q = 1
                while n % p == 0:
                    n //= p
                    q *= p
                out.append(q)
            p += 1
    return tuple(sorted(out))
</document>
</documents>

<question>
# Question: a stronger lower bound on the distance of [[756,16,<=34]], using symmetry

**The code.** A bivariate bicycle code in the convention of the attached distance.py: l = 21,
m = 18, A = x^3 + y^10 + y^17, B = y^5 + x^3 + x^19, n = 756, k = 16. Qubit (i, j) of the left
block is index i*m + j, of the right block lm + i*m + j. d_X = d_Z (distance.py's module
docstring), and d is even (A and B have odd weight).

**What we have** (docs/code-distances.md, "The open distances"; the instruments are the attached
parts.py and search_parts.c):
- an upper bound 34, with a checked witness, from random information sets;
- a lower bound d >= 24 from the attached exhaustive check-driven search, iterative deepening,
  anchors (0, lm) by the translation argument, each pass split across 16 processes on 4 cores.
  Pass times (wall clock, 4 cores) at bounds 20 to 24: 47 s, 222 s, 480 s, 2355 s, 5396 s, with
  2.3e9, 1.1e10, 2.4e10, 1.2e11, 2.6e11 nodes. The pass at 25 did not finish in 5.6 hours.
  So the pass at 29 (which would give d >= 30) would cost roughly 1000 times the pass at 24.
- An unverified secondhand claim (one tool, not cross-validated) of d >= 30 exists; we have not
  read how it was obtained.

**The question.** We want a lower bound of 26, and ideally 30 or more, within a few days on 4
cores, by a method whose correctness we can state as an argument and check on small codes
against enumeration (as we did for the split). We are looking first at symmetry.
1. **The automorphism group.** Which qubit permutations preserve this code's Z-logicals (map
   ker H_X to itself and the row space of H_Z to itself), beyond the lm translations the search
   already uses? Please compute it (or a large subgroup) for this code with code, e.g. torus
   automorphisms (x, y) -> (x^a y^b, x^c y^d) combined with the block swap and inversion, or a
   general permutation-group computation on the Tanner graph. Give its order and generators
   explicitly as permutations or maps, so we can verify each one by machine.
2. **Using it soundly in this search.** The search fixes an anchor as the least qubit of the
   logical and branches on the candidates of the unsatisfied check with fewest candidates. How
   would you exploit a group G of automorphisms here: orbit representatives of anchors (already
   done for translations), lexicographic or canonical-augmentation pruning, symmetry-breaking at
   deeper levels? State the argument that nothing is lost, and estimate the speedup factor for
   this G (roughly |G|/lm if only anchors can be reduced, more if deeper pruning works).
3. **Other routes**, if symmetry alone cannot reach 26 or 30 in days: e.g. a Brouwer-Zimmermann
   style bound adapted to CSS codes, bounds from quotient or punctured codes, linear-programming
   or SDP bounds, or splitting the search by the logical's projection to a quotient torus. Which
   do you expect to reach 30 here, at what cost, and on what argument?

Please mark every claim proved, computed or conjectured, and check the group computation by
running code. We will verify every generator and every argument independently before using it.
</question>
