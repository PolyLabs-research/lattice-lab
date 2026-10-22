"""
Stage 2 of the code census: a registered test of stage 1's findings (docs/code-census.md) on the
122 tori held out of stage 1 (../qec-census/holdout.json's held_out_random, 22 tori with
50 <= lm <= 100, and held_out_extrapolation, the 100 with 100 < lm <= 150).

    uv run --no-sync python examples/qec-census-2/study.py register
    uv run --no-sync python examples/qec-census-2/study.py run --workers 4
    uv run --no-sync python examples/qec-census-2/study.py resume --workers 4   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-2

The family is stage 1's: A = x^a + y^b + y^c, B = y^d + x^e + x^f on the l x m torus, its codes
with k > 0 grouped into classes by census.classes (monomial factors, swapping A and B,
automorphisms of the torus; an upper bound on the inequivalent codes).

**The predictions** are computed by rules.py from l and m and stage-1 results only (summary.json's
k-sets, and data/'s bests for H9), before anything is computed on a held-out torus, and written
into the registration torus by torus. Nothing in the registration computes a code, k, a class or
a distance on any torus (the tests check it with every such primitive stubbed to raise).
- **H1 (proved, decisive).** Some raw code has k > 0 exactly where criterion 1 holds (result 1:
  gcd(x^l' + 1, (x + 1)^N + 1) and gcd(x^m' + 1, (x + 1)^N + 1) nontrivial over GF(2),
  N = lcm(l', m')). It predicts codes on 29 of the 122 tori. The observation is census.c's k of
  every raw code.
- **H2 (proved; decisive where a value is given).** The maximum k: 2^(s+t) M(l', m') with M from
  stage 1 where l' x m' is a stage-1 torus, and 8lm/9 where 3 | l and 3 | m (results 2 and 3;
  where both apply they agree, on all 15 stage-1 tori too). Where neither fixes it (3x31, 3x35,
  3x49, 5x21, 5x27, 7x15, 7x21, all odd) the registration gives only the proved bound,
  max k <= 8lm/9, and the structure (a multiple of 2^(s+t+1)); decide records the value found and
  checks only those.
- **H3 (pattern, decisive).** The minimum k is twice the least Frobenius orbit among the
  admissible character types (result 5; the bound is proved, equality held on 35 of 35).
- **H4 (proved, decisive).** On a torus with exactly one even side, the k-set is the odd torus's
  times 2^j, j = 0..s+t (result 4): the odd torus's k-set from stage 1, or, for 3x42 and 6x21,
  whose odd torus 3x21 is held out too, from this run's record of 3x21.
- **H5 (pattern, decisive).** On every class of every torus with codes, the deepening search
  with bound 3 (passes 2 and 3) finds a checked weight-2 logical exactly when condition (i) or
  (ii) of result 7 holds, evaluated from A, B and the class's common zeros (bb.local_terms).
- **H6 (proved, decisive; tests the instruments).** On every class: every exact d is even
  (result 6); no lower bound exceeds the quotient bound of result 8 or a forced bound of
  result 9 with m/q odd, and their explicit logicals pass verify_witness with the bound's weight;
  every witness passes; every search and program finds k logicals; 2 Σ local terms is k; and all
  of a class's intervals meet, from every instrument and every job. A disagreement fails the
  instruments, as in examples/qec-distance-2. Judged on every torus with codes, exposed ones
  included: a torus is "not tested" without its torus job's record, and "unresolved" while any
  of its registered jobs is missing or failed (then not every instrument ran on it).
- **H7 (risky, quantitative).** The linear law (Patterns): on each instance, the largest d over
  the classes with a common zero of its type equals 2m/q. The instances follow from l, m and the
  admissible types (rules.forced_types): 19, from (3,31) on 3x31 (value 2) to (3,5) on 3x50 and
  (5,3) on 5x30 (value 20), 18 of them not exposed. Three are certain by proof: (3,31), (3,35)
  and (3,49) on 3x31, 3x35 and 3x49 have m/q = 1, so value 2, and every d is at least 2 while
  the forced vector proves d <= 2. They are reported ("proved"), must come out equal (anything
  else resolved is a fault), and are left out of the threshold, which rests on the other 15 not
  exposed. Each instance is equal (some class has a lower bound >= its value and every class an
  upper bound <= it), above (a class has a lower bound above it), below (every class has an
  upper bound below it) or unresolved; an instance whose job failed or has no record counts as
  unresolved. **The threshold**: the law fails if any instance is above or a fault; otherwise
  the test is inconclusive if fewer than 75% of the 15 resolve, and the law holds when at least
  80% of the resolved ones are equal, and fails if not. Why: stage 1 had 13 equal of its 14
  instances with m/q > 1 (its three with m/q = 1, 3x5 (3,5), 3x7 (3,7) and 3x25 (3,25), were
  certain too); 80% leaves room for three misses in 15. "Above" is decisive at once: for odd
  m/q it contradicts result 9's proof (an instrument fault), and for even m/q no stage-1 class
  of these types exceeded the value (113 classes). The extrapolation is real: stage 1 reached
  m/q = 6, and here m/q goes to 10.
  **The representative.** "A class with a zero of the type" is read at its representative, as
  stage 1 read it. Where gcd(l, m) > 1 that depends on the representative: an automorphism can
  mix the torus's factors (rules.type_is_class_invariant). Stage 1's one miss is of this kind:
  on 3x15 two k = 8 classes at d = 6 = 2m/q have codes with a (3,5) zero, but their
  representatives' zeros are of type (3,15), so by representatives the instance's one class is
  the k = 24 class at d = 2 (development, on 3x15; read by codes, stage 1's instances are all
  equal). The registered law keeps the reading by representatives; 5 of the 15 judged
  instances are on such tori (3x21, 3x42, 3x45, 5x30, 7x21). Where gcd(l, m) = 1 an admissible
  type is proved to be a zero of some code (result 1's converse), so a torus with no class of
  the type is a fault; elsewhere such an instance is not tested.
- **H8 and H9 (patterns, judged where affordable).** H8: on each torus with 3 | l, 3 | m and
  lm >= 27, every class at the torus's best k d^2/n reduces mod (3, 3) to the [[18,8,2]] base
  (rules.reduces_to_base, stage 1's test). H9: at each n of such a torus, the best k d^2/n over
  the tori with codes at that n, held out or stage 1's, is on such a torus (ties count).
  **Both are judged only on the tori with n <= 252** (3x21, 3x36, 3x39, 3x42 and the exposed
  6x18, 6x21, 9x12; H9 at n = 126, 216, 234 and 252), a rule by n fixed before registration
  ("Why n <= 252" below). H9 is contested at 126 by stage 1's 7x9 (its best, [[126,12,6]],
  k d^2 = 432, a look-up in data/7x9.jsonl, exact by the search and the program) and at 252 by
  7x18 and the exposed 9x14; at 216 and 234 no other torus has codes, and decide reports those
  as "uncontested". On the strictly clean tori ("strict") H8 covers only 3x21 and 3x39, and H9
  is contested only at 126: at 252 every torus is exposed or isomorphic to an exposed one.

**Exposure.** These are computed and reported beside the verdict, which rests on the others:
the tori of holdout.json's exposed_extrapolation, each with what the earlier studies record
computing there (rules.DEVELOPMENT_ON_EXPOSED: k of this family's codes on most; distances or
the program's bounds of particular codes of the family on 6x18, 6x24, 7x15, 9x12 and 12x12);
those docs/code-census.md's exposure section names (12x12, 8x18, 6x24, 9x16, and 2x48 and 3x29
for (L)'s records on their groups); and 8x11 and 10x13, where examples/qec-distance-2 computed
the toric code's distance, which holdout.json missed. That is 25 tori in all (rules.exposure,
with each one's reasons in the question). (L)'s list of [[n,k,d]] up to n = 200 also covers the
n of the held-out random tori; it is recorded (rules.L_LIST_EXPOSURE), and those tori are judged
as clean. 18 held-out tori are isomorphic as groups to an exposed one (3x36 to 9x12, 3x42 to
6x21, 3x45 to 9x15, 3x35 and 5x21 to 7x15, 5x30 to 10x15, 7x18 to 9x14, and 11 without codes;
rules.ISOMORPHIC_NOTE says what was computed on each twin). What was seen on the exposed torus
concerns particular codes there, most of whose images are not of this family's form, so these
are judged with the clean tori; every part is also reported on the strictly clean tori
("strict").

**The instruments.** Every distance is distance_search of kind Z from the anchors (0, lm) (its
argument, its code and the translation argument; d = d_Z for these codes), with its witness
checked by verify_witness, or distance_ilp under SCIP_FIX at seed 0, or an explicit logical of
results 8 and 9 checked by verify_witness. A class's interval is the intersection of every run's
interval (census.interval: the lower bound a run proves, 1 if none, and the weight of its
checked witness, unbounded if none). Every d of the family is even (result 6, proved), so the
ranking and the outcomes round a lower bound up to the next even number (a deepening search
stopped after pass 17 shows d >= 18); the records keep the raw bounds, and H6 checks those. The
runs:
- **d2** (every class of every torus): the deepening search with bound 3, 60 s.
- **scan** (every class of an H8/H9 torus, in 4 jobs per torus): the deepening search, bound
  min(64, the class's checked structural upper bound), 3 s. In the calibration (below) it gave
  an exact d on 237 of 253 classes of 3x33 and 676 of 680 of 6x15.
- **probe**: one pass (deepen=False) with bound b, 20 s: it finds any logical lighter than b if
  it runs to its end, and keeps the lightest it found when stopped. In development, with b near
  1.3 to 1.5 d it found a weight-d logical within 3 to 10 s on classes with d = 16 to 18 that the
  deepening search needs 2 to 22 s to finish, and with b = 64 it found little; so the ranking
  probes at a class's exclusion threshold.
- **deep**: the deepening search, bound min(64, the class's checked upper bound), 45 minutes.
- **law scan, law probe, law deep** (H7): 3 s, 60 s and 15 minutes, with the bounds below.
- **program** (the cross-checks): distance_ilp, kind Z, SCIP_FIX, 600 s.
decide checks every run against its instrument's registered settings, and every search's bound
against its rule where the records fix it (protocol_failures, deep_bound_failures).

**H8 and H9's ranking** (frontier_round), "exact d for the top candidates, witness upper bounds
for the rest". With L the largest lower score k lo^2 over a torus's classes and U a class's upper
score k up^2, a class is a candidate for the best while it is not exact and its U >= L; one
below L cannot be the best, since its interval is certified. A round re-ranks after every
action. It first probes every candidate that can still be probed at its exclusion threshold b
(the least b with k b^2 >= L, when b is above its lower bound; at most two probes per class, at
different b), the largest U first (unbounded first), then the largest lower score, so that a
witness lighter than b puts the class below L; only when no probe is left does it run the deep
search (once per class) on the candidate with the largest lower score. An action starts only if
its whole limit fits in the round's budget (50 minutes); there are 4 rounds per torus, each its
own job, which reads the earlier jobs' records. Then a cross-check job runs the program on the
torus's best classes (at most 2, the least indices, and of them at most one with d >= 16, where
stage 1's program only bracketed: 13 of 13 stopped at 600 s) and a sample (5% of the other exact
classes with d >= 4, at least 1 and at most 2, from random.Random('qec-census stage2 sample
LxM')); their intervals must meet. H8 holds on a torus when every candidate for the best reduces
to the base; fails when a class that does not reduce is exact with a score no class can exceed;
is unresolved otherwise. H9 holds at n when the best lower score on tori with 3 | l and 3 | m is
at least every upper score on the others, fails when an other torus's lower score exceeds every
upper score on those, and is unresolved otherwise (a stage-1 torus's score is exact).

**H7's procedure** (law_record), on the classes of the instance's type, V = 2m/q: (0) the law
scan on each, with bound V + 1, or its checked upper bound where that is <= V; (1) on each class
without a checked upper bound <= V, a law probe with bound V + 1, then if still open a law deep
with bound V + 1, which ends with an exact d <= V or the lower bound V + 1 (above); (2) while no
class has a lower bound >= V, the law deep with bound V on the class with the largest lower
bound that could reach V. For odd m/q every class has the forced vector (proved, checked), so
only step (2) costs anything. The searches have a budget of 30 minutes; then the program runs on
the class at the largest exact d and on one sampled class with exact d >= 4 (seeded as above).

**The hold-out and its one exception.** census.guard refuses every held-out torus, either
orientation, and the 8 stage-1 tori isomorphic to one, before anything is computed. Every
function here that computes on a torus calls it first. The registered run alone opens a torus:
job() enters census.Stage2Permit, which opens the job's torus (holdout.json's orientation only)
only when it is entered from this file's `job` and stage 2's ledger verifies and holds this
registration followed by run_started (and run_resumed) entries only, with the torus among the
registered tori. Outside that block, and on every other torus, the guard refuses as before.
**The registered code.** The registration hashes this file, rules.py, the tests, census.py and
the instruments (HASHED); execute and job() refuse to run, and decide reports and withholds
"hold", when any of them differs from what was registered.

**Running it** (execute). Each job runs in its own worker process, which Linux kills when the
study's process dies, up to --workers at a time; whenever a worker is free, the first job in
jobs() order whose `after` jobs all have records and whose timeout fits in the window starts:
the frontier rounds and cross-checks as soon as they can, then the torus jobs and scans of the
H8/H9 tori, the H7 instances (largest value first), the other torus jobs (largest first). Each
record is appended when its job ends; resume skips every job with a record (a failed job's
error row included: the verdict is then incomplete at best) and restarts a job cut off by a
stop. **The window.** A cloud session's background command stops at two hours. Every job's
timeout is at most 55 minutes, and execute starts a job only if its timeout fits before the end
of a window of 115 minutes from its start (QEC_CENSUS2_WINDOW sets it, in seconds; 0 for none);
when nothing more fits and nothing runs, it stops with a StudyError, before the observations, and
resume continues in a new window. A frontier torus's chain (its torus job and scans, 4 rounds,
its cross-check) then fits in 3 windows when every round uses its budget and a worker is free
for each job, about 6 hours with the stops. The limits are wall clock, so other load weakens
what stops at a limit: run it when nothing else heavy shares the machine.

**The verdict** (VERDICT_RULE, in the registration): fail when the instruments fail (H6 finds a
problem, a run was not made by the registered protocol, a job has two records, an H7 instance
is a fault) or a part fails; hold when every part holds (or is not applicable), every
registered job has a record, no job failed (an error row, or a failed earlier job named in a
record's prior_errors) and the code is the registered code; incomplete otherwise.

**Cost** (COST_ESTIMATE, from stage-1 timings; nothing was timed on a held-out torus). Stage 1's
search from (0, lm) took (medians by d and n) 0.03 s at d = 12, 0.2 s at 14, 2 s at 16 and
22 s at 18, flat in n from 144 to 198 (at d = 16: 2.2, 1.9, 1.8 and 2.0 s at n = 162, 180, 196
and 198; at d = 18: 22.3, 21.9 and 22.4 s at n = 180, 196 and 198), and the current search.c
(sha256 d353ead3..., stage 1's) takes 18 s on [[288,12,18]] at n = 288 (docs/code-distances.md;
its 3 minutes were the search before examples/qec-distance-2's fix): about x10 per +2 in d,
with no sign of growth in n. Extrapolated: about 4 minutes at d = 20, 40 minutes at 22 and
6 hours at 24. The program took 28 to 44 s (medians) at d = 12, 113 to 314 s at d = 14, and
stopped at 600 s at d >= 16 (13 of 13). On 3 x m, stage 1's best d of a k = 8 class was 6, 10,
10, 12, 14, 16 at m = 9, 15, 18, 24, 27, 33 (from 0.67 m down to 0.48 m), and its k = 4
classes' about 0.55 m.
- **H1 to H6, the torus jobs:** 38.3 million raw codes (stage 1: 5.5 million in 32 s), the
  classes, and 15 to 30 ms per class for the structure, the explicit logicals and the d2 search
  (the calibration's torus jobs: 5.8 s for 3x27's 179 classes, 10.2 s for 6x15's 680): about
  0.5 CPU hours for the 122 tori.
- **H7:** for odd m/q one search to V: seconds for V <= 16, under a minute for V = 18 (3x45,
  5x27); for even m/q also the classes without a checked forced vector (82 of 113 had one in
  stage 1), each with a probe and perhaps a search with bound V + 1, about 4 to 6 minutes at
  V = 20 (3x50, 5x30) by the extrapolation; and two programs per instance, up to 10 minutes each
  at d >= 16. About 2 to 4 CPU hours; at most 19 x 55 minutes if every job used its whole budget.
- **H8 and H9:** the calibration on stage-1 tori took 5 minutes per torus without programs at
  n = 180 to 198 (with these rounds and limits: 3x33, scan 215 s, then one round of 5 probes in
  69 s; 6x15, 235 s, then 4 probes in 53 s; both found stage 1's best). At n = 216 to 252 the
  best's d is expected near 18 to 20 (22 s to 4 minutes per deep search), and the k = 4
  classes' near 20 to 23, which the 3-s scan leaves open, so each needs a probe, and a deep
  search where its probe finds nothing light enough:
  about 1 to 2 CPU hours per large torus (3x36, 6x18, 6x21, 3x42 by stage-1 analogues of 400 to
  1,400 classes), less for 3x21, 3x39, 9x12, 7x18 and 9x14, plus up to 40 minutes of programs
  each: about 6 to 12 CPU hours; at most 9 x (4 x 50 + 40) minutes = 36 CPU hours.
- **In all** about 9 to 18 CPU hours: 3 to 5 hours of wall clock with 4 workers, 2 or 3 windows.
  If every budget were used, about 65 CPU hours, some 10 windows. Expect resumes; a resumed job
  starts again from its beginning.

**Why n <= 252.** H8 and H9 need every candidate for a torus's best resolved. With the corrected
cost, the search does not single out n = 252: on the trend above, the best's d at n = 270 and
288 (3x45, 3x48) is near 20 to 24, 4 minutes to 6 hours per deep search, beyond the 45-minute
limit only at the upper end, and the k = 4 classes' near 24 to 26, whose exclusion rests on
probes at about 1.2 d, below what development tried (1.3 to 1.5 d, at d <= 18). The cutoff is a
choice of run length: the two sizes add six frontier chains (3x45, the exposed 9x15 and 5x27 at
270; 3x48 and the exposed 6x24 and 12x12 at 288), up to about 24 CPU hours if every budget is
used, to a run that already needs several windows, and every torus left unresolved leaves H8
incomplete. What it gives up: H8 on 3x45 (isomorphic to the exposed 9x15) and 3x48 (clean), a
contested H9 size at 270 (3x45 against the clean 5x27), and the uncontested 288.

**What it does not establish.** One family of one form; classes are an upper bound on its
inequivalent codes. d rests on search.c from (0, lm) where it completes and on checked witnesses
for upper bounds; the program's lower bounds rest on SCIP with SCIP_FIX, and at d >= 16 it only
brackets. H8 and H9 are judged on 7 and 4 of their possible tori and sizes (n <= 252); H9 is
contested only at n = 126 and 252. H7 reads a class's type at its representative (above). The
rules' proofs are by hand. Nothing here bears on performance under circuit noise.

**Development (excluded_seen in the question)** lists everything computed while building this
study: on stage-1 tori and synthetic data only, and arithmetic on the held-out l and m.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import random
import resource
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CENSUS_DIR = HERE.parent / "qec-census"


def _load(name: str, path: Path):
    """A module from its file, registered under `name` (once per process: the tests load
    census.py under the same name, and share it)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up there
    spec.loader.exec_module(module)
    return module


census = _load("qec_census", CENSUS_DIR / "census.py")
rules = _load("qec_census_stage2_rules", HERE / "rules.py")
bb, distance = census.bb, census.distance

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, StudyError, append_records, main  # noqa: E402

ID = census.STAGE2_ID
PYTHON = ROOT / ".venv" / "bin" / "python"
RECORDS = HERE / "records.jsonl"
BOUND = distance.SEARCH_BOUND  # 64, search.c's largest bound

# ---------------------------------------------------------------- limits (wall clock, seconds)

D2_BOUND, D2_LIMIT = 3, 60.0  # H5: the deepening search with bound 3 (passes 2 and 3)
SCAN_LIMIT = 3.0  # H8/H9: the first, short deepening search on every class
SCAN_PARTS = 4  # scan jobs per frontier torus (classes i with i mod 4 = part)
PROBE_LIMIT = 20.0  # H8/H9: a single pass at a class's exclusion threshold
DEEP_LIMIT = 45 * 60.0  # H8/H9: a deepening search on a candidate for the best
ROUND_BUDGET = 50 * 60.0  # H8/H9: one round of the ranking (two rounds fit in a window)
ROUNDS = 4  # rounds per frontier torus, each its own job
PROBES_PER_CLASS = 2
LAW_SCAN_LIMIT = 3.0  # H7: the short deepening search on every class of the type
LAW_PROBE_LIMIT = 60.0  # H7: a single pass with bound 2m/q + 1
LAW_LIMIT = 15 * 60.0  # H7: a deepening search on one class
LAW_BUDGET = 30 * 60.0  # H7: the searches of one instance
PROGRAM_LIMIT = 600.0  # the cross-checks: distance_ilp under SCIP_FIX
CROSSCHECK_BESTS = 2  # at most this many best classes per torus (the least indices) ...
PROGRAM_BRACKETS_AT = 16  # ... of which at most one with d >= 16, where stage 1's program
# stopped at its 600 s limit on 13 of 13 classes
SAMPLE_FRACTION, SAMPLE_MAX = 0.05, 2  # and a random sample of the rest with d >= 4
SAMPLE_SEED = "qec-census stage2 sample {name}"
GRACE = 5 * 60.0  # a job's timeout beyond its budget: process start, the last action's overrun
WINDOW = 115 * 60.0  # execute's window: a cloud session's background command stops at 2 hours
FRONTIER_MAX_N = 252  # H8/H9 are judged on the tori with n <= 252 (module docstring)
# H7's threshold (module docstring); registered in H7's prediction, which decide reads
H7_EQUAL, H7_RESOLVED = 0.8, 0.75

# The protocol: what decide checks every run against (it is in the predictions).
INSTRUMENTS = {
    "d2": {"deepen": True, "bound": D2_BOUND, "limit": D2_LIMIT},
    "scan": {"deepen": True, "limit": SCAN_LIMIT},
    "probe": {"deepen": False, "limit": PROBE_LIMIT},
    "deep": {"deepen": True, "limit": DEEP_LIMIT},
    "law scan": {"deepen": True, "limit": LAW_SCAN_LIMIT},
    "law probe": {"deepen": False, "limit": LAW_PROBE_LIMIT},
    "law deep": {"deepen": True, "limit": LAW_LIMIT},
    "program": {"limit": PROGRAM_LIMIT},
}
STRUCTURAL = ("quotient", "forced")  # explicit logicals of results 8 and 9, checked
PROTOCOL = {
    "scip_fix": distance.SCIP_FIX,
    "scip_seed": distance.SEED,
    "kind": "Z",
    "anchors": "(0, lm)",
    "instruments": INSTRUMENTS,
}


def _name(ell: int, m: int) -> str:
    return f"{ell}x{m}"


def _torus(name: str) -> tuple[int, int]:
    a, b = name.split("x")
    return int(a), int(b)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- the registered sets


def exposure_status(ell: int, m: int) -> str:
    """ "exposed", "isomorphic" (to an exposed torus) or "clean" (rules.exposure)."""
    if (ell, m) in rules.exposure():
        return "exposed"
    if (ell, m) in rules.isomorphic_to_exposed():
        return "isomorphic"
    return "clean"


def with_codes() -> list[tuple[int, int]]:
    """The held-out tori where criterion 1 predicts codes with k > 0."""
    return [t for t in rules.held_out() if rules.criterion(*t)]


def law_instances() -> list[dict]:
    """H7's instances (rules.forced_types on every held-out torus), each with `proved` (m/q = 1:
    value 2, and d = 2 is certain, every d being at least 2 and the forced vector a logical) and
    `type_invariant` (rules.type_is_class_invariant: whether the classes of the type do not
    depend on their representatives)."""
    out = []
    for ell, m in rules.held_out():
        for f in rules.forced_types(ell, m):
            p, q = f["type"]
            out.append(
                {
                    "torus": _name(ell, m),
                    "l": ell,
                    "m": m,
                    "n": 2 * ell * m,
                    **f,
                    "key": f"law {ell}x{m} ({p},{q})",
                    "exposure": exposure_status(ell, m),
                    "proved": m // q == 1,
                    "type_invariant": rules.type_is_class_invariant(ell, m),
                }
            )
    return out


def frontier_plan() -> dict:
    """H8's tori and H9's sizes. H8: the held-out tori with 3 | l, 3 | m and lm >= 27 and
    n <= FRONTIER_MAX_N; the others are listed with the reason. H9: each n of an H8 torus, with
    the held-out tori with codes at that n, of both kinds (`three`: 3 | l and 3 | m; `other`),
    and the stage-1 tori with codes there (`stage1`, rules.stage1_at: each one's best class and
    its exact score k d^2, a look-up)."""
    h8, excluded = [], []
    for ell, m in rules.held_out():
        if not rules.frontier_torus(ell, m):
            continue
        if 2 * ell * m <= FRONTIER_MAX_N:
            h8.append(_name(ell, m))
        else:
            excluded.append(
                {
                    "torus": _name(ell, m),
                    "n": 2 * ell * m,
                    "reason": f"n > {FRONTIER_MAX_N}: a choice of run length (module "
                    "docstring, 'Why n <= 252')",
                }
            )
    sizes = sorted({2 * a * b for a, b in map(_torus, h8)})
    h9 = {}
    for n in sizes:
        at = [t for t in with_codes() if 2 * t[0] * t[1] == n]
        h9[str(n)] = {
            "three": [_name(*t) for t in at if t[0] % 3 == 0 and t[1] % 3 == 0],
            "other": [_name(*t) for t in at if t[0] % 3 or t[1] % 3],
            "stage1": rules.stage1_at(n),
        }
    tori = sorted(
        {x for v in h9.values() for x in v["three"] + v["other"]},
        key=lambda s: (-_torus(s)[0] * _torus(s)[1], _torus(s)),
    )
    return {"h8": h8, "excluded": excluded, "h9": h9, "tori": tori}


# ---------------------------------------------------------------- instruments on a class
#
# Every function here that computes on a torus's codes calls census.guard first, as census.py's
# do. Within job() a Stage2Permit opens the job's held-out torus; nowhere else is one open.


def _verify(A, B, ell: int, m: int, support) -> dict:
    census.guard(ell, m)
    v = distance.verify_witness(A, B, ell, m, "Z", support)
    return {"weight": v["weight"], "verified": bool(v["logical"])}


def structure(c: dict, ell: int, m: int) -> dict:
    """A class's common zeros (bb.local_terms, with 2 Σ terms, which must be k), result 7's
    conditions, result 8's quotient bound and result 9's forced vectors with their explicit
    logicals checked by verify_witness, and whether it reduces mod (3, 3) to the base (where
    3 | l and 3 | m)."""
    census.guard(ell, m)
    A, B = c["A"], c["B"]
    zeros = [[j, k, t] for (j, k), t in bb.local_terms(A, B, ell, m)]
    q = rules.quotient_bound(A, B, zeros, ell, m)
    quotient = None
    if q is not None:
        quotient = {
            **{key: q[key] for key in ("bound", "order", "form", "g")},
            **_verify(A, B, ell, m, q["support"]),
        }
    forced = [
        {
            **{key: f[key] for key in ("type", "value", "proved")},
            **_verify(A, B, ell, m, f["support"]),
        }
        for f in rules.forced_bounds(A, B, zeros, ell, m)
    ]
    base = rules.reduces_to_base(A, B, ell, m) if ell % 3 == 0 and m % 3 == 0 else None
    return {
        "zeros": zeros,
        "k_characters": 2 * sum(t for _, _, t in zeros),
        "cond_i": rules.condition_i(A, B, ell, m),
        "cond_ii": rules.condition_ii(A, B, zeros, ell, m),
        "quotient": quotient,
        "forced": forced,
        "base": base,
    }


def structural_runs(s: dict) -> list[dict]:
    """The explicit logicals of a class's structure as runs: an upper bound each, where
    verify_witness passed."""
    out = []
    if s["quotient"] is not None:
        q = s["quotient"]
        out.append(
            {
                "instrument": "quotient",
                "status": "witness",
                "d": None,
                "lower": None,
                "upper": q["weight"],
                "verified": q["verified"],
                "bound": q["bound"],
            }
        )
    for f in s["forced"]:
        out.append(
            {
                "instrument": "forced",
                "status": "witness",
                "d": None,
                "lower": None,
                "upper": f["weight"],
                "verified": f["verified"],
                "type": f["type"],
                "proved": f["proved"],
            }
        )
    return out


def search(A, B, ell: int, m: int, instrument: str, bound: int, limit: float) -> dict:
    """distance_search of kind Z from the anchors (0, lm), as the instrument says (deepening,
    or one pass with deepen=False), its witness checked; a run's fields."""
    census.guard(ell, m)
    deepen = INSTRUMENTS[instrument]["deepen"]
    bound = max(2, min(BOUND, int(bound)))
    try:
        r = distance.distance_search(
            A, B, ell, m, "Z", bound=bound, anchors=(0, ell * m), time_limit=limit, deepen=deepen
        )
        verified = census._verified(A, B, ell, m, r["witness"])
    except Exception as exc:  # recorded (the witness's check included); the job goes on
        return {
            "instrument": instrument,
            **census._failed(exc),
            "bound": bound,
            "deepen": deepen,
            "limit": limit,
        }
    return {
        "instrument": instrument,
        "status": r["status"],
        "d": r["d"],
        "lower": r["lower"],
        "upper": r["upper"],
        "witness": r["witness"],
        "verified": verified,
        "k": r["k"],
        "bound": bound,
        "deepen": r["deepen"],
        "anchors": r["anchors"],
        "limit": limit,
        "nodes": r["nodes"],
        "seconds": r["seconds"],
    }


def program(A, B, ell: int, m: int, limit: float = PROGRAM_LIMIT) -> dict:
    """distance_ilp of kind Z under SCIP_FIX, its witness checked; a run's fields."""
    census.guard(ell, m)
    try:
        r = distance.distance_ilp(A, B, ell, m, "Z", time_limit=limit)
        verified = census._verified(A, B, ell, m, r["witness"])
    except Exception as exc:  # recorded (the witness's check included); the job goes on
        return {"instrument": "program", **census._failed(exc), "limit": limit}
    fix = {key: r["settings"].get(key) for key in distance.SCIP_FIX}
    return {
        "instrument": "program",
        "status": r["status"],
        "d": r["d"],
        "lower": r["lower"],
        "upper": r["upper"],
        "witness": r["witness"],
        "verified": verified,
        "k": r["k"],
        "scip_fix": r["scip_fix"],
        "settings": fix,
        "seed": r["seed"],
        "limit": limit,
        "nodes": r["nodes"],
        "seconds": r["seconds"],
    }


# ---------------------------------------------------------------- intervals and scores


def interval(runs, even: bool = True) -> tuple[int, float]:
    """The intersection of the runs' intervals (census.interval: [lower, or 1; the weight of a
    witness that passed verify_witness, or unbounded]); runs that raised are left out. With
    `even` (the default, for the ranking and the outcomes) the lower bound is rounded up to the
    next even number: every d of the family is even (result 6, proved), so d >= 17 gives
    d >= 18. H6 checks the raw bounds (even=False), and the records keep them."""
    ivs = [census.interval(r) for r in runs if r.get("status") not in (None, "error")]
    lo = max((a for a, _ in ivs), default=1)
    if even:
        lo += lo % 2
    return lo, min((b for _, b in ivs), default=math.inf)


def exact(runs) -> int | None:
    lo, up = interval(runs)
    return lo if lo == up else None


def _score(k: int, d) -> float:
    """k d^2: k d^2 / n times n, which is the same for every class of a torus or an n."""
    return math.inf if d == math.inf else k * d * d


def _threshold(k: int, target: float) -> int:
    """The least weight b with k b^2 >= target: a logical lighter than b puts the class below."""
    if target == math.inf:
        return BOUND
    b = math.isqrt(int(target) // k)
    while k * b * b < target:
        b += 1
    return b


def merge(records: list[dict], ell: int, m: int) -> dict[int, dict]:
    """Every class of l x m that the records name, with its rep and k (which must agree across
    records: `conflicts`), its base flag where known, and all its runs."""
    out: dict[int, dict] = {}
    for rec in records:
        if rec.get("l") != ell or rec.get("m") != m or "error" in rec:
            continue
        for c in rec.get("classes", []):
            i = c["class"]
            cur = out.setdefault(
                i,
                {
                    "class": i,
                    "rep": c["rep"],
                    "k": c["k"],
                    "runs": [],
                    "base": None,
                    "conflicts": [],
                },
            )
            if (c["rep"], c["k"]) != (cur["rep"], cur["k"]):
                cur["conflicts"].append(f"{rec['key']}: rep {c['rep']}, k {c['k']}")
            if c.get("structure", {}).get("base") is not None:
                cur["base"] = c["structure"]["base"]
            if c.get("base") is not None:
                cur["base"] = c["base"]
            cur["runs"] += c.get("runs", [])
    return out


def ranking(state: dict[int, dict]) -> dict:
    """The ranking by k d^2 / n from the classes' intervals: L, the largest lower score (k lo^2);
    U, the largest upper score; the candidates for the best (not exact, upper score >= L); and,
    when the best score is determined (U == L), the classes at it."""
    lower = {i: _score(s["k"], interval(s["runs"])[0]) for i, s in state.items()}
    upper = {i: _score(s["k"], interval(s["runs"])[1]) for i, s in state.items()}
    big_l = max(lower.values(), default=0)
    big_u = max(upper.values(), default=0)
    cands = [i for i in state if exact(state[i]["runs"]) is None and upper[i] >= big_l]
    best = [i for i in state if lower[i] == big_l == upper[i]] if big_u == big_l else None
    return {
        "L": big_l,
        "U": big_u,
        "candidates": sorted(cands),
        "best": best,
        "lower": lower,
        "upper": upper,
    }


# ---------------------------------------------------------------- the jobs' computations


def _classes(ell: int, m: int) -> list[dict]:
    census.guard(ell, m)
    return census.classes(ell, m)["classes"]


def _usage() -> dict:
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime
    return {"cpu_seconds": round(cpu, 1), "load": [round(x, 2) for x in os.getloadavg()]}


def torus_record(ell: int, m: int) -> dict:
    """The torus job (H1 to H6): k of every raw code (census.c), the classes, and per class its
    structure, its explicit logicals and the d = 2 test (the deepening search with bound 3)."""
    census.guard(ell, m)
    start = time.time()
    found = census.classes(ell, m)
    rows = []
    for c in found["classes"]:
        s = structure(c, ell, m)
        d2 = search(c["A"], c["B"], ell, m, "d2", D2_BOUND, D2_LIMIT)
        rows.append(
            {
                "class": c["class"],
                "rep": c["rep"],
                "params": c["params"],
                "k": c["k"],
                "size": c["size"],
                "k_constant": c["k_constant"],
                "structure": s,
                "runs": [d2, *structural_runs(s)],
            }
        )
    ks = sorted({c["k"] for c in found["classes"]})
    return {
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "torus_type": list(rules.torus_type(ell, m)),
        **{
            key: found[key]
            for key in ("raw_codes", "raw_k_positive", "raw_by_k", "classes_by_k", "k_seconds")
        },
        "kset": ks,
        "max_k": max(ks, default=0),
        "min_k": min(ks, default=None),
        "classes": rows,
        "seconds": round(time.time() - start, 1),
    }


def _bound_for(runs, cap: int = BOUND) -> int:
    """A deepening search's bound: the class's verified upper bound, if any, capped."""
    up = interval(runs)[1]
    return int(min(cap, up)) if up != math.inf else cap


def scan_record(ell: int, m: int, part: int, parts: int = SCAN_PARTS) -> dict:
    """A scan job (H8/H9): the short deepening search on every class i with i mod parts = part,
    with its bound at the class's structural upper bound where it has one."""
    census.guard(ell, m)
    start = time.time()
    rows = []
    for c in _classes(ell, m):
        if c["class"] % parts != part:
            continue
        own = structural_runs(structure(c, ell, m))
        r = search(c["A"], c["B"], ell, m, "scan", _bound_for(own), SCAN_LIMIT)
        rows.append({"class": c["class"], "rep": c["rep"], "k": c["k"], "runs": [r]})
    return {
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "part": part,
        "parts": parts,
        "classes": rows,
        "seconds": round(time.time() - start, 1),
    }


def _probe_bound(state: dict, i: int, big_l: float) -> int | None:
    """A candidate's pending probe: the bound b of a single pass at its exclusion threshold,
    when b is above its lower bound and it has had fewer than PROBES_PER_CLASS probes, none at
    b; None otherwise."""
    s = state[i]
    lo, _ = interval(s["runs"])
    probed = [r.get("bound") for r in s["runs"] if r.get("instrument") == "probe"]
    b = min(BOUND, max(2, _threshold(s["k"], big_l)))
    if b > lo and b not in probed and len(probed) < PROBES_PER_CLASS:
        return b
    return None


def _next_action(state: dict, cands: list[int], skip: set, big_l: float):
    """A round's next action on the candidates not in `skip`, as (class, kind, bound), or None
    when none is left. First a probe (_probe_bound), on the candidate with the largest upper
    score (unbounded first), then the largest lower score, the largest k and the least index;
    only when no candidate has a probe left, the deep search (once per class, bound
    _bound_for), on the candidate with the largest lower score, then the largest k and the least
    index."""
    open_ = [i for i in cands if i not in skip]
    scores = {}
    for i in open_:
        lo, up = interval(state[i]["runs"])
        scores[i] = (_score(state[i]["k"], lo), _score(state[i]["k"], up))
    for i in sorted(open_, key=lambda i: (-scores[i][1], -scores[i][0], -state[i]["k"], i)):
        b = _probe_bound(state, i, big_l)
        if b is not None:
            return i, "probe", b
    deep = [i for i in open_ if not any(r.get("instrument") == "deep" for r in state[i]["runs"])]
    if not deep:
        return None
    i = min(deep, key=lambda i: (-scores[i][0], -state[i]["k"], i))
    return i, "deep", _bound_for(state[i]["runs"])


def frontier_round(
    ell: int,
    m: int,
    rnd: int,
    prior: list[dict],
    budget: float = ROUND_BUDGET,
    clock=time.monotonic,
) -> dict:
    """One round of the ranking (H8/H9) on l x m, from the runs in `prior` (the torus job, the
    scans and the earlier rounds): while some class is a candidate for the best (ranking), the
    next action (_next_action: every pending probe before any deep search), re-ranking after
    each, as long as the action's whole limit fits in what is left of the round's budget."""
    census.guard(ell, m)
    start = clock()
    by_index = {c["class"]: c for c in _classes(ell, m)}
    state = merge(prior, ell, m)
    missing = sorted(set(by_index) - set(state))
    conflicts = {i: s["conflicts"] for i, s in state.items() if s["conflicts"]}
    for i, s in state.items():
        if i not in by_index or by_index[i]["rep"] != s["rep"]:
            conflicts.setdefault(i, []).append("rep differs from this job's classes")
    new: dict[int, list[dict]] = {}
    actions, skip, stopped = [], set(conflicts), "resolved"
    while True:
        rank = ranking(state)
        action = _next_action(state, rank["candidates"], skip, rank["L"])
        if action is None:
            stopped = "stuck" if rank["candidates"] else "resolved"
            break
        i, kind, bound = action
        limit = PROBE_LIMIT if kind == "probe" else DEEP_LIMIT
        if clock() - start + limit > budget:
            stopped = "budget"
            break
        c = by_index[i]
        r = search(c["A"], c["B"], ell, m, kind, bound, limit)
        state[i]["runs"].append(r)
        new.setdefault(i, []).append(r)
        actions.append([i, kind, bound, r["status"], r.get("lower"), r.get("upper")])
    rank = ranking(state)
    return {
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "round": rnd,
        "classes": [
            {"class": i, "rep": by_index[i]["rep"], "k": by_index[i]["k"], "runs": runs}
            for i, runs in sorted(new.items())
        ],
        "actions": actions,
        "stopped": stopped,
        "missing": missing,
        "conflicts": conflicts,
        "L": rank["L"],
        "U": rank["U"],
        "candidates": rank["candidates"],
        "best": rank["best"],
        "seconds": round(clock() - start, 1),
    }


def _sample(pool: list[int], name: str) -> list[int]:
    """SAMPLE_FRACTION of `pool`, rounded up, at least one if any and at most SAMPLE_MAX, from
    random.Random(SAMPLE_SEED with the torus or instance's name)."""
    pool = sorted(pool)
    if not pool:
        return []
    size = min(SAMPLE_MAX, max(1, math.ceil(SAMPLE_FRACTION * len(pool))))
    return sorted(random.Random(SAMPLE_SEED.format(name=name)).sample(pool, size))


def crosscheck_choice(state: dict, name: str) -> dict[int, str]:
    """The classes the program cross-checks: the best (exact d at the largest exact score; at
    most CROSSCHECK_BESTS, the least indices, of which at most one with d >= PROGRAM_BRACKETS_AT,
    where the program only brackets) and _sample of the other exact ones with d >= 4."""
    exacts = {i: exact(s["runs"]) for i, s in state.items()}
    exacts = {i: d for i, d in exacts.items() if d is not None}
    top = max((_score(state[i]["k"], d) for i, d in exacts.items()), default=None)
    bests = sorted(i for i, d in exacts.items() if _score(state[i]["k"], d) == top)
    out, high = {}, 0
    for i in bests:
        if len(out) == CROSSCHECK_BESTS:
            break
        if exacts[i] >= PROGRAM_BRACKETS_AT:
            if high:
                continue
            high += 1
        out[i] = "best"
    pool = [i for i, d in exacts.items() if d >= 4 and i not in out]
    out.update({i: "sample" for i in _sample(pool, name)})
    return out


def meets(runs) -> bool:
    """Whether the runs' raw intervals meet (as H6 checks them)."""
    lo, up = interval(runs, even=False)
    return lo <= up


def crosscheck_record(ell: int, m: int, prior: list[dict]) -> dict:
    """The cross-check job (H8/H9): the program on crosscheck_choice's classes; each class's
    intervals must still meet with the program's."""
    census.guard(ell, m)
    start = time.time()
    by_index = {c["class"]: c for c in _classes(ell, m)}
    state = merge(prior, ell, m)
    chosen = crosscheck_choice(state, _name(ell, m))
    rows = []
    for i, why in sorted(chosen.items()):
        c = by_index[i]
        p = {**program(c["A"], c["B"], ell, m), "reason": why}
        rows.append(
            {
                "class": i,
                "rep": c["rep"],
                "k": c["k"],
                "runs": [p],
                "meets": meets(state[i]["runs"] + [p]),
            }
        )
    return {
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "classes": rows,
        "seconds": round(time.time() - start, 1),
    }


def law_record(
    ell: int, m: int, p: int, q: int, budget: float = LAW_BUDGET, clock=time.monotonic
) -> dict:
    """An H7 job: the classes with a common zero of type (p, q), and their distances as far as
    the instance needs, V = 2m/q (module docstring): (0) the short deepening search on each,
    its bound V + 1, or its verified upper bound where that is at most V; (1) on each class
    without a verified upper bound <= V, a single pass with bound V + 1 and then, if still
    unbounded, a deepening search with bound V + 1 (so an exact d <= V, or a lower bound V + 1:
    above V); (2) while no class has a lower bound >= V and some class could reach it, a
    deepening search with bound V on the class with the largest lower bound. An action starts
    only if its whole limit fits in the budget. Then the program on the class at the largest
    exact d and on one sampled class with exact d >= 4."""
    census.guard(ell, m)
    start = clock()
    value = 2 * m // q
    rows, state = {}, {}
    for c in _classes(ell, m):
        s = structure(c, ell, m)
        if not rules.has_type(s["zeros"], p, q, ell, m):
            continue
        rows[c["class"]] = c
        state[c["class"]] = {
            "k": c["k"],
            "runs": structural_runs(s),
            "new": [],
            "forced": s["forced"],
            "quotient": s["quotient"],
        }
    order = sorted(state, key=lambda i: (state[i]["k"], i))
    stopped = "done"

    def run(i, instrument, bound, limit):
        r = search(rows[i]["A"], rows[i]["B"], ell, m, instrument, bound, limit)
        state[i]["runs"].append(r)
        state[i]["new"].append(r)
        return r

    def fits(limit):
        return clock() - start + limit <= budget

    for i in order:  # (0)
        up = interval(state[i]["runs"])[1]
        bound = int(up) if up <= value else value + 1
        if not fits(LAW_SCAN_LIMIT):
            stopped = "budget"
            break
        run(i, "law scan", bound, LAW_SCAN_LIMIT)
    steps = [
        (i, instrument, limit)
        for i in order
        for instrument, limit in (("law probe", LAW_PROBE_LIMIT), ("law deep", LAW_LIMIT))
    ]
    for i, instrument, limit in steps if stopped != "budget" else []:  # (1)
        lo, up = interval(state[i]["runs"])
        if up <= value or lo > value or lo == up:
            continue
        if not fits(limit):
            stopped = "budget"
            break
        run(i, instrument, value + 1, limit)
    while stopped != "budget":  # (2)
        ivs = {i: interval(state[i]["runs"]) for i in order}
        if any(lo >= value for lo, _ in ivs.values()):
            break
        tried = {
            i
            for i in order
            if any(
                r["instrument"] == "law deep" and r.get("bound") == value for r in state[i]["runs"]
            )
        }
        reach = [
            i for i in order if ivs[i][1] >= value and ivs[i][0] < ivs[i][1] and i not in tried
        ]
        if not reach:
            break
        i = min(reach, key=lambda x: (-ivs[x][0], state[x]["k"], x))
        if not fits(LAW_LIMIT):
            stopped = "budget"
            break
        run(i, "law deep", value, LAW_LIMIT)
    exacts = {i: exact(state[i]["runs"]) for i in order}
    exacts = {i: d for i, d in exacts.items() if d is not None}
    chosen = {}
    if exacts:
        top = max(exacts.values())
        chosen[min(i for i, d in exacts.items() if d == top)] = "max"
        pool = [i for i, d in exacts.items() if d >= 4 and i not in chosen]
        chosen.update({i: "sample" for i in _sample(pool, f"{ell}x{m} ({p},{q})")})
    for i, why in sorted(chosen.items()):
        if exacts[i] >= 4:
            r = {**program(rows[i]["A"], rows[i]["B"], ell, m), "reason": why}
            state[i]["runs"].append(r)
            state[i]["new"].append(r)
    return {
        "l": ell,
        "m": m,
        "n": 2 * ell * m,
        "type": [p, q],
        "value": value,
        "classes": [
            {
                "class": i,
                "rep": rows[i]["rep"],
                "k": state[i]["k"],
                "runs": structural_runs(
                    {"quotient": state[i]["quotient"], "forced": state[i]["forced"]}
                )
                + state[i]["new"],
            }
            for i in order
        ],
        "stopped": stopped,
        "seconds": round(clock() - start, 1),
    }


# ---------------------------------------------------------------- jobs


def jobs() -> list[dict]:
    """Every job, in the order the scheduler prefers among those ready (execute): the frontier
    rounds and cross-checks (each waits for its torus's earlier jobs, `after`), the torus jobs
    of the frontier tori, their scans, the H7 instances (largest value first), then every other
    torus, the largest first."""
    plan = frontier_plan()
    out = []
    for name in plan["tori"]:
        ell, m = _torus(name)
        first = [f"torus {name}"]
        first += [f"scan {name} part {i}/{SCAN_PARTS}" for i in range(SCAN_PARTS)]
        rounds = [f"frontier {name} round {r}" for r in range(1, ROUNDS + 1)]
        for r, key in enumerate(rounds, 1):
            out.append(
                {
                    "test": "frontier",
                    "key": key,
                    "l": ell,
                    "m": m,
                    "round": r,
                    "after": first + rounds[: r - 1],
                }
            )
        out.append(
            {
                "test": "crosscheck",
                "key": f"crosscheck {name}",
                "l": ell,
                "m": m,
                "after": first + rounds,
            }
        )
    frontier = [_torus(name) for name in plan["tori"]]
    out += [{"test": "torus", "key": f"torus {_name(*t)}", "l": t[0], "m": t[1]} for t in frontier]
    out += [
        {
            "test": "scan",
            "key": f"scan {_name(*t)} part {i}/{SCAN_PARTS}",
            "l": t[0],
            "m": t[1],
            "part": i,
            "parts": SCAN_PARTS,
        }
        for t in frontier
        for i in range(SCAN_PARTS)
    ]
    laws = sorted(law_instances(), key=lambda x: (-x["value"], -x["n"], x["key"]))
    out += [
        {
            "test": "law",
            "key": x["key"],
            "l": x["l"],
            "m": x["m"],
            "type": x["type"],
            "value": x["value"],
        }
        for x in laws
    ]
    rest = sorted(
        (t for t in rules.held_out() if t not in frontier), key=lambda t: (-t[0] * t[1], t)
    )
    return out + [
        {"test": "torus", "key": f"torus {_name(*t)}", "l": t[0], "m": t[1]} for t in rest
    ]


# Each at most 55 minutes, so that two jobs fit in a window (WINDOW).
TIMEOUTS = {
    "torus": 30 * 60.0,
    "scan": 50 * 60.0,
    "frontier": ROUND_BUDGET + GRACE,
    "crosscheck": (CROSSCHECK_BESTS + SAMPLE_MAX) * PROGRAM_LIMIT + GRACE,
    "law": LAW_BUDGET + 2 * PROGRAM_LIMIT + GRACE,
}


def prior_records(spec: dict, path: Path) -> list[dict]:
    """The records of the jobs `spec` waits for (its `after`), read from the records file:
    complete lines only, the last record of each key."""
    wanted, out = set(spec.get("after", [])), {}
    for _, _, line in record_lines(path):
        r = json.loads(line)
        if r.get("key") in wanted:
            out[r["key"]] = r
    return [out[key] for key in spec.get("after", []) if key in out]


def _dispatch(spec: dict, path: Path) -> dict:
    """The job's computation, within job()'s permit."""
    ell, m, test = spec["l"], spec["m"], spec["test"]
    if test == "torus":
        return torus_record(ell, m)
    if test == "scan":
        return scan_record(ell, m, spec["part"], spec["parts"])
    if test == "law":
        return law_record(ell, m, *spec["type"])
    prior = prior_records(spec, path)
    used = {
        "prior": [r["key"] for r in prior],
        "prior_errors": [r["key"] for r in prior if "error" in r],
    }
    if test == "frontier":
        return {**frontier_round(ell, m, spec["round"], prior), **used}
    if test == "crosscheck":
        return {**crosscheck_record(ell, m, prior), **used}
    raise ValueError(f"unknown test {test!r}")


def code_hashes() -> dict[str, str]:
    """The sha256 of every file the registration pins (HASHED)."""
    return {key: _sha256_file(path) for key, path in HASHED.items()}


def registered_code_problem(ledger_path: Path | None = None) -> str | None:
    """Why the pinned files (HASHED) are not those the registration hashed, or None: stage 2's
    ledger (census.STAGE2_LEDGER) must hold a question whose sha256 equals code_hashes()."""
    from lattice_lab.ledger import Ledger

    path = Path(ledger_path) if ledger_path is not None else census.STAGE2_LEDGER
    if not path.is_file():
        return f"{path} does not exist: stage 2 is not registered"
    entries = Ledger(path).entries
    if not entries or entries[0]["kind"] != "question":
        return f"{path} holds no question"
    want, now = entries[0]["body"].get("sha256") or {}, code_hashes()
    changed = sorted(key for key in set(want) | set(now) if want.get(key) != now.get(key))
    if changed:
        return f"changed since the registration (or not hashed by it): {', '.join(changed)}"
    return None


def job(spec: dict, records: str | None = None) -> dict:
    """Run one job and return its record (execute calls it in a worker process). The job's
    torus is opened to census.guard by a Stage2Permit, which census.py grants only here and
    only while the ledger holds stage 2's registration and its started run; then, before
    anything is computed, the pinned files must be those registered (registered_code_problem)."""
    path = Path(records) if records else RECORDS
    began = time.time()
    with census.Stage2Permit([(spec["l"], spec["m"])]):
        problem = registered_code_problem()
        if problem:
            raise StudyError(problem)
        body = _dispatch(spec, path)
    solver = {"solver": distance.scip_version(), "scip_fix": distance.SCIP_FIX}
    return {**spec, **body, **solver, "job_seconds": round(time.time() - began, 1), **_usage()}


# The worker asks Linux to kill it when the study's process dies (PR_SET_PDEATHSIG is 1), and
# exits at once if that process is already gone.
WORKER = """
import ctypes, importlib.util, json, os, signal, sys
if sys.platform == "linux":
    ctypes.CDLL(None).prctl(1, signal.SIGKILL)
    if os.getppid() != int(sys.argv[2]):
        sys.exit("the study's process is gone")
spec = importlib.util.spec_from_file_location("qec_census_stage2", {path!r})
study = importlib.util.module_from_spec(spec)
sys.modules["qec_census_stage2"] = study
spec.loader.exec_module(study)
print(json.dumps(study.job(json.loads(sys.argv[1]), sys.argv[3])))
"""


def _run(spec: dict, path: Path) -> dict:
    """One job in its own worker process. Any failure is returned as an error row (the job is
    then not tested, and resume does not retry it)."""
    code = WORKER.format(path=str(HERE / "study.py"))
    timeout = TIMEOUTS[spec["test"]]
    try:
        out = subprocess.run(
            [str(PYTHON), "-c", code, json.dumps(spec), str(os.getpid()), str(path)],
            cwd=HERE,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if out.returncode:
            return {**spec, "error": out.stderr[-2000:]}
        return json.loads(out.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {**spec, "error": f"subprocess timeout after {timeout} s"}
    except Exception as exc:
        return {**spec, "error": f"{type(exc).__name__}: {exc}"}


def _window() -> float:
    """execute's window in seconds: QEC_CENSUS2_WINDOW if set (0 for none), else WINDOW."""
    value = os.environ.get("QEC_CENSUS2_WINDOW")
    return WINDOW if value is None else float(value)


def execute(path: Path, workers: int, run=None, window: float | None = None, clock=None) -> None:
    """Run every job without a record in `path` (a failed job's error row counts as a record),
    at most `workers` at a time: whenever a worker is free, the first job in jobs() order whose
    `after` jobs all have records and whose timeout fits in what is left of the window
    (`window` seconds from the start, _window() by default; 0 for none). When jobs are left and
    none can start before the window ends, it waits for the running ones and stops with a
    StudyError, before the observations, so that resume continues in a new window. Each record
    is appended as its job finishes, so resume (which runs this again) skips every job done; a
    job cut off by a stop runs again from its start. A file ending in an incomplete line (a
    record cut off as the study's process was killed writing it) is refused, with the offset of
    that line, as in examples/qec-distance-2. The real run (no `run` given) first refuses
    pinned files that differ from the registration (registered_code_problem)."""
    path = Path(path)
    if run is None:
        problem = registered_code_problem()
        if problem:
            raise StudyError(problem)
    run = run or _run
    window = _window() if window is None else window
    clock = clock or time.monotonic
    start = clock()

    def fits(spec: dict) -> bool:
        return window <= 0 or clock() - start + TIMEOUTS[spec["test"]] <= window

    done = set()
    if path.exists():
        data = path.read_bytes()
        if data and not data.endswith(b"\n"):
            start = data.rfind(b"\n") + 1
            raise StudyError(
                f"{path} ends with an incomplete line at byte {start} ({len(data) - start} bytes "
                f"after the last complete line): truncate it to {start} bytes, then resume"
            )
        done = {json.loads(line)["key"] for _, _, line in record_lines(path)}
    todo = [j for j in jobs() if j["key"] not in done]
    slots = max(1, workers)
    running = {}
    with ThreadPoolExecutor(slots) as pool:
        while todo or running:
            while len(running) < slots:
                ready = next(
                    (j for j in todo if all(a in done for a in j.get("after", [])) and fits(j)),
                    None,
                )
                if ready is None:
                    break
                todo.remove(ready)
                running[pool.submit(run, ready, path)] = ready
            if not running:
                if any(all(a in done for a in j.get("after", [])) for j in todo):
                    raise StudyError(
                        f"the window ends: {len(todo)} jobs left, none of whose timeouts fits in "
                        "what is left of it; resume continues"
                    )
                waiting = [j["key"] for j in todo]
                raise StudyError(f"jobs wait on records no job will write: {waiting}")
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in finished:
                spec = running.pop(future)
                append_records(path, [future.result()])
                done.add(spec["key"])


# ---------------------------------------------------------------- the registration

SOURCES = {
    "H1": "docs/code-census.md, Structure, result 1 (criterion 1), proved; 116 of 116",
    "H2": "docs/code-census.md, Structure, results 2 and 3, proved; 35 of 35",
    "H3": "docs/code-census.md, Structure, result 5: the bound proved, equality 35 of 35",
    "H4": "docs/code-census.md, Structure, result 4, proved; 18 of 18",
    "H5": "docs/code-census.md, Structure, result 7: 'if' proved, 'only if' 3,330 of 3,330",
    "H6": "docs/code-census.md, Structure, results 6, 8 and 9, proved",
    "H7": "docs/code-census.md, Patterns, 'A linear distance law': 16 of 17 stage-1 instances "
    "by representatives, 13 of the 14 with m/q > 1 (3x15 the miss, an artefact of the "
    "representative: module docstring); result 9 proves the upper bound for odd m/q",
    "H8": "docs/code-census.md, Patterns, 'The best codes reduce to one small code': 20 of 20 "
    "classes on 13 tori",
    "H9": "docs/code-census.md, Patterns, 'What the best codes look like': 10 of 10 n, 2 of "
    "them contested",
}
HASHED = {
    "census_py": CENSUS_DIR / "census.py",
    "census_c": census.CENSUS_C,
    "distance_py": Path(distance.__file__),
    "search_c": distance.SEARCH_C,
    "bb_py": Path(bb.__file__),
    "retest_py": HERE.parent / "qec-distance-2" / "study.py",
    "holdout_json": census.HOLDOUT,
    "summary_json": census.SUMMARY,
    "rules_py": HERE / "rules.py",
    "study_py": HERE / "study.py",
    "tests_py": ROOT / "tests" / "test_qec_census_2.py",
}
VERDICT_RULE = (
    "fail when the instruments fail (H6 finds a problem; a run was not made by the registered "
    "protocol, settings or bound rules; a job has two records; an H7 instance is a fault) or a "
    "part fails; hold when every part holds or is not applicable, every registered job has a "
    "record, no job failed (an error row, or a failed earlier job named in a record's "
    "prior_errors), and the pinned files are those registered; incomplete otherwise. A part "
    "over its judged items (not exposed): fails if one fails, holds if every one holds (and "
    "there is one), incomplete otherwise; H6 over every torus with codes, exposed ones included, "
    "'not tested' if none was tested; H7 by its registered threshold. 'instruments' is fail as "
    "above, hold when H6 holds, and otherwise H6's outcome (not tested, or incomplete)."
)
# From stage-1 timings and the development calibration (module docstring, "Cost")
COST_ESTIMATE = {
    "basis": "stage 1's search from (0, lm), medians by d and n: 0.03 s at d = 12, 0.2 s at 14, "
    "2 s at 16, 22 s at 18, flat in n from 144 to 198; the current search.c (sha256 "
    "d353ead3..., stage 1's) takes 18 s on [[288,12,18]] at n = 288 (docs/code-distances.md; "
    "the 3 minutes there were the search before examples/qec-distance-2's fix); so about x10 "
    "per +2 in d with no sign of growth in n, extrapolated to about 4 minutes at d = 20, 40 at "
    "22 and 6 hours at 24; the program 28 to 44 s at d = 12, 113 to 314 s at 14 (medians), its "
    "600 s limit at d >= 16 (13 of 13); best d of a k = 8 class on 3 x m from 0.67 m down to "
    "0.48 m (m = 9 to 33), of a k = 4 class about 0.55 m",
    "calibration": "the H8/H9 pipeline without programs on stage-1 tori, with these rounds and "
    "limits: 3x33 292 s (scan 215 s, one round of 5 probes), 6x15 297 s (scan 235 s, 4 probes), "
    "each finding stage 1's best (with the earlier round order: 3x27 51 s, all exact after the "
    "scan); law_record on 7 stage-1 instances, 0.6 to 154 s each with programs",
    "H1-H6 torus jobs": "about 0.5 CPU hours (38.3 million raw codes; 15 to 30 ms per class)",
    "H7 law jobs": "about 2 to 4 CPU hours; at most 19 x 55 minutes; at V = 20 (3x50 (3,5), "
    "5x30 (5,3)) a search with bound V + 1 about 4 to 6 minutes by the extrapolation",
    "H8/H9 scans, rounds and cross-checks": "about 6 to 12 CPU hours on the 9 tori with "
    "n <= 252; at most 9 x (4 x 50 + 40) minutes, 36 CPU hours, if every budget is used",
    "n = 270 and 288 (not judged)": "best d expected near 20 to 24, 4 minutes to 6 hours per "
    "deep search; six more frontier chains, up to about 24 CPU hours (module docstring, 'Why "
    "n <= 252')",
    "total": "about 9 to 18 CPU hours, 3 to 5 hours of wall clock with 4 workers (2 or 3 "
    "windows); about 65 CPU hours, some 10 windows, if every budget were used",
    "windows": "every job's timeout at most 55 minutes; a job starts only if its timeout fits in "
    "the 115-minute window; a frontier torus's chain fits in 3 windows when every round uses "
    "its budget and a worker is free for each job",
}
EXCLUDED_SEEN = [
    "nothing was computed on any held-out torus or on the 8 refused stage-1 tori: no code, k, "
    "class or distance; the held-out names appear in development only in arithmetic on l and m "
    "and in tests with every computing primitive stubbed to raise",
    "arithmetic on the held-out l and m, as the registration does: criterion 1, admissible types, "
    "orbit sizes, the max-k and min-k rules (with stage-1 look-ups), the k-set rule, the forced "
    "types and their values, the H8/H9 plan, exposure and torus types; and bb.Field(135) and "
    "bb.Field(147), the fields of 5x27 and 3x49, built for timing (no torus)",
    "rules.py on stage-1 data: criterion, min and max k and the k-set rule on all 116 stage-1 "
    "tori (summary.json); conditions (i) and (ii), the quotient bound, the forced bounds, the base "
    "reduction and the linear-law table on all 3,330 stage-1 classes (data/*.jsonl: A, B, "
    "characters, the search's d); verify_witness on all 146 forced vectors and on the quotient "
    "logicals of 600 random stage-1 classes (437 with a bound)",
    "the single-pass search as a witness finder, on stage-1 classes: 3x33 #118, #120, #137 "
    "(k = 4, d = 18) and #15, #16 (k = 8, d = 16) with bound 1.5 d and 1.3 d, 10 s; 3x33 #118, "
    "#15, 6x15 #142, #318 and 7x14 #113, #59 with bound 1.5 d at 1 s and 3 s, and the deepening "
    "search with bound d (300 s); the 3 largest-d classes and one d = 14 class of 3x33, 6x15 and "
    "7x14 with bounds 64 and 40, 5 s; the bound-3 search and bb.local_terms on the first 50 "
    "classes of 3x33, 6x15 and 7x14 (timing)",
    "the study's computations on stage-1 tori: torus_record on 3x9, 6x6, 3x10, 7x7 and 3x18 "
    "against stage-1 data; the H8/H9 pipeline (torus job, 4 scans, rounds) on 3x27, 3x33 and "
    "6x15, and crosscheck_record on 3x27 (stopped by a 19-minute shell limit during its "
    "programs); law_record on 3x15 (3,5), 3x20 (3,5), 3x25 (3,5) and (3,25), 5x18 (5,3), "
    "7x12 (7,3) and 3x30 (3,5), with their programs",
    "the review (another agent, before registration): its own derivation of the rules on "
    "stage-1 data (data/ headers) and on the held-out l and m (arithmetic only); its own class "
    "conditions, GF(2) checks of the quotient and forced vectors and base test on all 3,330 "
    "stage-1 classes, and verify_witness on 300 stage-1 witnesses; decide on synthetic records "
    "and frontier_round with a stand-in search and clock, the computing primitives stubbed",
    "applying the review: stage-1 search and program times tabulated by d and n from data/; "
    "on the stage-1 tori 3x15, 5x15 and 3x30, census.classes' raw codes and canonical keys and "
    "bb.local_terms at every raw code with k > 0, to see whether a zero of type (3,5) or (5,3) "
    "is a class invariant (it is not: rules.type_is_class_invariant), no distance computed; and "
    "the H8/H9 pipeline (torus job, 4 scans, rounds; no programs) rerun on 3x33 and 6x15 with "
    "the new round order and limits",
    "tests/test_qec_census_2.py: stage-1 data and summary.json (the rules); torus_record on 3x9; "
    "the H8/H9 pipeline on 3x12; law_record on 3x10 (3,5), 5x6 (5,3) and 3x15 (3,5); bb.Field's "
    "roots of unity for q <= 25; synthetic records for decide, the scheduler and the frontier "
    "round (with a stand-in search and classes); search() on 3x9 with its instruments stubbed; "
    "the permit with temporary ledgers; the worker process on a 3x9 spec, which the permit "
    "refuses before computing anything; every computing primitive stubbed to raise wherever a "
    "held-out name appears",
    "census.py's guard gained the Stage2Permit exception after stage 1 ran; stage 1's files "
    "record the census.py they were made with (sha256 5f652666...)",
]
KNOWN_LIMITATIONS = [
    "one family of one form; the classes are an upper bound on its inequivalent codes",
    "d rests on distance_search from (0, lm) (its argument, its code and the translation "
    "argument) where it completes; upper bounds rest on witnesses checked by verify_witness; the "
    "program's lower bounds rest on SCIP with SCIP_FIX; at d >= 16 the program brackets at best",
    "every limit is wall clock, so other load on the machine weakens what stops at a limit; the "
    "limits are set from stage-1 timings extrapolated to d = 20 to 24, not timed on any "
    "held-out torus",
    "H8 and H9 are judged only on the tori with n <= 252 (a choice of run length), and H9 is "
    "contested only at n = 126 (by stage 1's 7x9) and 252; on the strictly clean tori H8 covers "
    "only 3x21 and 3x39 and H9 is contested only at 126; H7 extrapolates to m/q = 10 where "
    "stage 1 reached 6",
    "H7 reads a class's type at its representative, as stage 1 did; where gcd(l, m) > 1 that "
    "depends on the representative (rules.type_is_class_invariant), and stage 1's one miss, "
    "3x15, is of this kind; 5 of the 15 judged instances are on such tori",
    "the tori isomorphic to an exposed torus are judged with the clean ones; each part is also "
    "reported on the strictly clean tori",
    "the proofs behind H1 to H6 are by hand (docs/code-census.md), not formalised",
]


def question() -> dict:
    plan = frontier_plan()
    return {
        "id": ID,
        "title": "Stage 2 of the code census: a registered test of stage 1's findings on the 122 "
        "held-out tori",
        "statement": "For codes of the form A = x^a + y^b + y^c, B = y^d + x^e + x^f on the "
        "held-out tori (holdout.json's held_out_random and held_out_extrapolation), stage 1's "
        "proved results and patterns predict, from l and m and stage-1 results only: which tori "
        "have codes with k > 0 (H1), the maximum and minimum k (H2, H3), the k-sets of tori with "
        "one even side (H4), which classes have d = 2 (H5), that the instruments respect the "
        "proved bounds (H6), the linear distance law on its forced types (H7), and, on the tori "
        "with n <= 252, that the best classes reduce to the [[18,8,2]] base (H8) and that the "
        "best at each such n is on a torus with 3 | l and 3 | m (H9).",
        "family": "A = x^a + y^b + y^c, B = y^d + x^e + x^f on Z_l x Z_m, b != c, e != f; "
        "H_X = [A | B], H_Z = [B^T | A^T], n = 2lm (examples/qec-census/census.py)",
        "classes": "census.classes: codes with k > 0 grouped under monomial factors on A and "
        "on B, swapping A and B, and automorphisms of Z_l x Z_m; an upper bound on inequivalent "
        "codes",
        "tori": [list(t) for t in rules.held_out()],
        "held_out_random": [list(t) for t in rules.held_out_random()],
        "held_out_extrapolation": [list(t) for t in rules.held_out_extrapolation()],
        "never_computed": "the 8 stage-1 tori isomorphic to a held-out torus (2x36, 3x26, "
        "4x14, 5x14, 6x11, 6x13, 6x16, 7x10) and every torus outside holdout.json's lists; "
        "census.guard refuses them, and Stage2Permit opens only the registered tori",
        "rules": {part: {"source": SOURCES[part]} for part in SOURCES},
        "rules_code": "rules.py (hashed below): criterion, admissible, orbit_size, min_k, "
        "max_k, kset_rule, forced_types, type_is_class_invariant, stage1_at, condition_i, "
        "condition_ii, quotient_bound, forced_bounds, reduces_to_base",
        "instruments": {
            "k": "census.ranks (census.c): rank H_X of every raw code, k = 2lm - 2 rank H_X",
            "zeros": "bb.local_terms at each class's representative; 2 Σ terms must be k",
            "d2": f"distance_search, kind Z, anchors (0, lm), deepening, bound {D2_BOUND}, "
            f"{D2_LIMIT:.0f} s",
            "scan": f"distance_search, kind Z, (0, lm), deepening, bound min(64, the class's "
            f"checked structural upper bound), {SCAN_LIMIT:.0f} s",
            "probe": "distance_search, kind Z, (0, lm), one pass (deepen=False) with bound the "
            f"class's exclusion threshold, {PROBE_LIMIT:.0f} s: a witness lighter than the "
            "threshold puts the class below the best",
            "deep": "distance_search, kind Z, (0, lm), deepening, bound min(64, the class's "
            f"checked upper bound), {DEEP_LIMIT:.0f} s",
            "law scan, law probe, law deep": f"the same, {LAW_SCAN_LIMIT:.0f} s, "
            f"{LAW_PROBE_LIMIT:.0f} s and {LAW_LIMIT:.0f} s, with the bounds of law_record",
            "program": f"distance_ilp, kind Z, SCIP_FIX, seed {distance.SEED}, "
            f"{PROGRAM_LIMIT:.0f} s",
            "quotient, forced": "the explicit logicals of results 8 and 9, checked by "
            "verify_witness",
            "witnesses": "every witness is checked by distance.verify_witness",
            "even": "the ranking and the outcomes round a lower bound up to an even number "
            "(result 6); H6 checks the raw bounds",
        },
        "limits": {
            "round_budget": ROUND_BUDGET,
            "rounds": ROUNDS,
            "scan_parts": SCAN_PARTS,
            "probes_per_class": PROBES_PER_CLASS,
            "law_budget": LAW_BUDGET,
            "crosscheck_bests": CROSSCHECK_BESTS,
            "program_brackets_at": PROGRAM_BRACKETS_AT,
            "sample_fraction": SAMPLE_FRACTION,
            "sample_max": SAMPLE_MAX,
            "sample_seed": SAMPLE_SEED,
            "timeouts": TIMEOUTS,
            "window": WINDOW,
        },
        "protocol": PROTOCOL,
        "scip_fix": distance.SCIP_FIX,
        "solver": distance.scip_version(),
        "search_compiler": distance._search_binary()[1],
        "memory_limit_mb": distance.MEMORY_MB,
        "sha256": code_hashes(),
        "exposure": {_name(*t): why for t, why in rules.exposure().items()},
        "exposure_of_random_n": rules.L_LIST_EXPOSURE,
        "isomorphic_to_exposed": {
            _name(*t): [_name(*e) for e in es] for t, es in rules.isomorphic_to_exposed().items()
        },
        "isomorphic_note": rules.ISOMORPHIC_NOTE,
        "exposure_rule": "exposed tori are computed and reported beside the verdict, which rests "
        "on the other tori; tori isomorphic to an exposed torus are judged with the clean ones, "
        "and each part is also reported on the strictly clean tori ('strict'), where H8 covers "
        "only 3x21 and 3x39 and H9 is contested only at n = 126",
        "frontier_plan": plan,
        "law_instances": law_instances(),
        "jobs": len(jobs()),
        "verdict_rule": VERDICT_RULE,
        "cost_estimate": COST_ESTIMATE,
        "excluded_seen": EXCLUDED_SEEN,
        "known_limitations": KNOWN_LIMITATIONS,
    }


H7_RULE = (
    "on the instances not exposed and not proved (m/q > 1): fails if any instance is above, or "
    "any instance (proved ones included) is a fault; otherwise inconclusive if fewer than "
    "resolved_fraction of them resolve (equal or below; an instance whose job failed or has no "
    "record, or that is not tested, counts as unresolved); otherwise holds when at least "
    "equal_fraction of the resolved ones are equal, and fails if not. A proved instance (m/q = 1) "
    "must be equal: resolved otherwise, it is a fault. A fault is also: the torus job and the "
    "law job disagree on the classes of the type, or, where gcd(l, m) = 1, no class has the "
    "type; where gcd(l, m) > 1 and no representative has the type, the instance is not tested"
)


def predictions() -> list[dict]:
    tori = rules.held_out()
    coded = with_codes()
    plan = frontier_plan()
    return [
        {
            "part": "H1",
            "kind": "proved, decisive",
            "source": SOURCES["H1"],
            "predicted": {_name(*t): rules.criterion(*t) for t in tori},
            "rule": "some raw code has k > 0 exactly when gcd(x^l' + 1, (x + 1)^N + 1) and "
            "gcd(x^m' + 1, (x + 1)^N + 1) are both nontrivial over GF(2), N = lcm(l', m')",
        },
        {
            "part": "H2",
            "kind": "proved, decisive where a value is given",
            "source": SOURCES["H2"],
            "predicted": {_name(*t): rules.max_k(*t) for t in coded},
            "rule": "max k = 2^(s+t) M(l', m'): a value from stage 1 where l' x m' is a stage-1 "
            "torus, 8lm/9 where 3 | l and 3 | m; elsewhere ('open') only max k <= bound, max k "
            "divisible by 2 * multiple = 2^(s+t+1), and, where multiple > 1 and l' x m' is a "
            "held-out torus, max k = multiple * this run's max k of l' x m'",
        },
        {
            "part": "H3",
            "kind": "pattern, decisive",
            "source": SOURCES["H3"],
            "predicted": {_name(*t): rules.min_k(*t) for t in coded},
            "rule": "min k = twice the least Frobenius orbit size among the admissible types",
        },
        {
            "part": "H4",
            "kind": "proved, decisive",
            "source": SOURCES["H4"],
            "predicted": {_name(*t): rules.kset_rule(*t) for t in coded if rules.kset_rule(*t)},
            "rule": "with exactly one side even, the k-set is the odd torus's k-set times 2^j, "
            "j = 0..s+t; the odd torus's k-set from stage 1, or from this run's record of it",
        },
        {
            "part": "H5",
            "kind": "pattern, decisive",
            "source": SOURCES["H5"],
            "tori": [_name(*t) for t in coded],
            "predicted": "on every class of every held-out torus with codes, the d2 search finds "
            "a checked weight-2 logical exactly when condition (i) or (ii) of result 7 holds",
            "protocol": PROTOCOL,
        },
        {
            "part": "H6",
            "kind": "proved, decisive; tests the instruments",
            "source": SOURCES["H6"],
            "tori": [_name(*t) for t in coded],
            "predicted": "on every class of every torus: every exact d is even; no lower bound "
            "exceeds the quotient bound or a proved forced bound, whose explicit logicals pass "
            "verify_witness; every witness passes; every instrument finds k logicals; all of a "
            "class's intervals meet (a disagreement, the program's included, fails the "
            "instruments)",
            "outcomes": "per torus with codes: fails (a problem), not tested (no torus job "
            "record), unresolved (a registered job on it missing or failed, or a run that "
            "raised), holds; the part holds when every torus holds",
            "protocol": PROTOCOL,
        },
        {
            "part": "H7",
            "kind": "risky, quantitative",
            "source": SOURCES["H7"],
            "instances": law_instances(),
            "predicted": "on each instance, the largest d over the classes whose representative "
            "has a common zero of its type equals its value 2m/q",
            "outcomes": "equal (a class has lower bound >= value and every class an upper bound "
            "<= value), above (a class has lower bound > value), below (every class has an upper "
            "bound < value), unresolved, not tested, fault (H7_RULE); lower bounds rounded up to "
            "even",
            "threshold": {
                "equal_fraction": H7_EQUAL,
                "resolved_fraction": H7_RESOLVED,
                "rule": H7_RULE,
            },
            "protocol": PROTOCOL,
        },
        {
            "part": "H8",
            "kind": "pattern, judged where affordable",
            "source": SOURCES["H8"],
            "tori": plan["h8"],
            "excluded": plan["excluded"],
            "predicted": "on each torus, every class at the torus's best k d^2/n reduces mod "
            "(3, 3) to the [[18,8,2]] base (rules.reduces_to_base)",
            "outcomes": "holds (every candidate for the best reduces), fails (a class that does "
            "not reduce is certainly at the best: exact, with a score no class can exceed), "
            "unresolved",
            "protocol": PROTOCOL,
        },
        {
            "part": "H9",
            "kind": "pattern, judged where affordable",
            "source": SOURCES["H9"],
            "sizes": plan["h9"],
            "predicted": "at each n, the best k d^2/n over the tori with codes at that n, held "
            "out (three, other) or stage 1's (stage1, exact scores looked up), is on a torus with "
            "3 | l and 3 | m (ties count as on it)",
            "outcomes": "holds (the best lower score on such tori >= every upper score on the "
            "others; 'uncontested' when no other torus at that n has codes), fails (an other "
            "torus's lower score exceeds every upper score on such tori), unresolved",
            "protocol": PROTOCOL,
        },
        {
            "part": "protocol",
            "kind": "the registered procedure (not a prediction): what decide judges by",
            "jobs": jobs(),
            "sha256": code_hashes(),
            "verdict_rule": VERDICT_RULE,
        },
    ]


# ---------------------------------------------------------------- the verdict

SEARCH_STATUSES = ("complete", "timelimit")
PROGRAM_STATUSES = ("optimal", "timelimit", "memlimit")


def _rule_bounds(name: str, rec: dict, c: dict, structural: dict | None):
    """The bounds a search run of instrument `name` on class row `c` of record `rec` may have
    by its registered rule, where the record (and the torus job's structural runs, `structural`:
    class -> runs) fixes it; None where it does not (a probe's threshold, a deep search's bound,
    which deep_bound_failures checks, or a scan without its torus job's record)."""
    if name == "d2":
        return {D2_BOUND}
    if name == "scan":
        if structural is None or c["class"] not in structural:
            return None
        return {_bound_for(structural[c["class"]])}
    if name in ("law scan", "law probe", "law deep"):
        value = rec.get("value")
        if not isinstance(value, int):
            return None
        if name == "law probe":
            return {value + 1}
        if name == "law deep":
            return {value, value + 1}
        own = [r for r in c.get("runs", []) if r.get("instrument") in STRUCTURAL]
        up = interval(own)[1]
        return {max(2, min(BOUND, int(up) if up <= value else value + 1))}
    return None


def protocol_failures(
    rec: dict, spec: dict | None, protocol: dict, structural: dict | None = None
) -> list[str]:
    """Why a record was not made by the registered protocol: it is not a registered job, its l
    and m are not its job's, or a run of it did not use its instrument's settings (deepening or
    one pass, from (0, lm), with the registered limit; the program under SCIP_FIX at the
    registered seed), or a search's bound is outside 2..64, below its own lower bound, or not
    its rule's (_rule_bounds). [] for an error row."""
    if "error" in rec:
        return []
    out = []
    if spec is None:
        return [f"{rec.get('key')}: not a registered job"]
    if (rec.get("l"), rec.get("m")) != (spec["l"], spec["m"]):
        out.append(f"l x m = {rec.get('l')}x{rec.get('m')}, registered {spec['l']}x{spec['m']}")
    lm = spec["l"] * spec["m"]
    settings = protocol["instruments"]
    for c in rec.get("classes", []):
        for r in c.get("runs", []):
            name = r.get("instrument")
            if name in STRUCTURAL:
                continue
            want = settings.get(name)
            if want is None:
                out.append(f"class {c['class']}: unknown instrument {name}")
                continue
            if r.get("status") == "error":
                continue
            if r.get("limit") != want["limit"]:
                out.append(f"class {c['class']} {name}: limit {r.get('limit')}")
            if name == "program":
                fix = protocol["scip_fix"]
                if r.get("scip_fix") is not True or r.get("settings") != fix:
                    out.append(f"class {c['class']} program: not under SCIP_FIX")
                if r.get("seed") != protocol["scip_seed"]:
                    out.append(f"class {c['class']} program: seed {r.get('seed')}")
                continue
            if r.get("deepen") != want["deepen"] or r.get("anchors") != [0, lm]:
                out.append(
                    f"class {c['class']} {name}: deepen {r.get('deepen')}, anchors "
                    f"{r.get('anchors')}"
                )
            bound = r.get("bound")
            if not isinstance(bound, int) or not 2 <= bound <= BOUND:
                out.append(f"class {c['class']} {name}: bound {bound}")
                continue
            if r.get("lower") is not None and r["lower"] > bound:
                out.append(f"class {c['class']} {name}: lower {r['lower']} above its bound {bound}")
            if "bound" in want and bound != want["bound"]:
                out.append(f"class {c['class']} {name}: bound {bound}")
                continue
            allowed = _rule_bounds(name, rec, c, structural)
            if allowed is not None and bound not in allowed:
                out.append(f"class {c['class']} {name}: bound {bound}, rule {sorted(allowed)}")
    return out


def deep_bound_failures(recs: list[dict]) -> dict[str, list[str]]:
    """A torus's deep searches whose bound is not min(64, the class's checked upper bound) from
    the runs the round saw before it (the torus job, the scans, the earlier rounds and its own
    earlier actions on the class), by record key."""
    order = [r for r in recs if r.get("test") in ("torus", "scan") and "error" not in r]
    rounds = [r for r in recs if r.get("test") == "frontier" and "error" not in r]
    order += sorted(rounds, key=lambda r: r.get("round", 0))
    seen: dict[int, list[dict]] = {}
    out: dict[str, list[str]] = {}
    for rec in order:
        for c in rec.get("classes", []):
            runs = seen.setdefault(c["class"], [])
            for r in c.get("runs", []):
                if r.get("instrument") == "deep" and r.get("status") != "error":
                    want = _bound_for(runs)
                    if r.get("bound") != want:
                        out.setdefault(rec.get("key"), []).append(
                            f"class {c['class']} deep: bound {r.get('bound')}, rule {want}"
                        )
                runs.append(r)
    return out


def run_problems(state: dict, structure_rows: dict) -> dict[int, list[str]]:
    """H6's checks on a torus's classes (merge's state; the torus job's rows by class), on the
    raw bounds: each class's intervals meet; every exact d is even; every search's and program's
    witness passes verify_witness and each finds k logicals; no lower bound exceeds the quotient
    bound or a proved forced bound, and their explicit logicals pass with the bound's weight;
    2 Σ terms is k and k is constant on the class; the class's rep and k agree across records."""
    out: dict[int, list[str]] = {}
    for i, s in state.items():
        found = list(s["conflicts"])
        lo, up = interval(s["runs"], even=False)
        if lo > up:
            found.append(f"DISAGREEMENT: the intervals meet nowhere, [{lo}, {up}]")
        if lo == up and lo % 2:
            found.append(f"odd d = {lo}")
        for r in s["runs"]:
            name = r.get("instrument")
            if name in STRUCTURAL or r.get("status") == "error":
                continue
            if r.get("witness") and r.get("verified") is not True:
                found.append(f"{name}: its witness fails verify_witness")
            if r.get("k") is not None and r["k"] != s["k"]:
                found.append(f"{name}: {r['k']} logicals, k = {s['k']}")
        row = structure_rows.get(i)
        if row is not None:
            st = row["structure"]
            if st["k_characters"] != s["k"] or not row["k_constant"]:
                found.append(
                    f"k_characters {st['k_characters']}, k {s['k']}, constant {row['k_constant']}"
                )
            q = st["quotient"]
            if q is not None:
                if not q["verified"] or q["weight"] != q["bound"]:
                    found.append("the quotient bound's logical fails verify_witness")
                if lo > q["bound"]:
                    found.append(f"lower bound {lo} above the quotient bound {q['bound']}")
            for f in st["forced"]:
                if f["proved"] and (not f["verified"] or f["weight"] != f["value"]):
                    found.append(f"the forced bound's logical {f['type']} fails verify_witness")
                if f["proved"] and lo > f["value"]:
                    found.append(f"lower bound {lo} above the forced bound {f['value']}")
        if found:
            out[i] = found
    return out


def _errors(state: dict) -> int:
    return sum(r.get("status") == "error" for s in state.values() for r in s["runs"])


def _over(vals: list[str]) -> str:
    """A part's outcome over its items' outcomes: fails if one fails, holds if every one holds
    (and there is one), incomplete otherwise ("not applicable" when there is none)."""
    if any(v == "fails" for v in vals):
        return "fails"
    if vals and all(v == "holds" for v in vals):
        return "holds"
    return "incomplete" if vals else "not applicable"


def _part(items: dict[str, str], tori_of=None) -> dict:
    """A part's outcome over items (torus or n -> "holds", "fails", "unresolved" or "not
    tested"), apart by exposure: "judged" (not exposed: the verdict), "strict" (clean only) and
    "exposed" (reported beside it), each by _over."""
    tori_of = tori_of or (lambda key: [key])
    status = {k: [exposure_status(*_torus(t)) for t in tori_of(k)] for k in items}
    judged = [k for k in items if "exposed" not in status[k]]
    strict = [k for k in judged if all(s == "clean" for s in status[k])]
    exposed = [k for k in items if "exposed" in status[k]]
    return {
        "outcome": _over([items[k] for k in judged]),
        "strict": _over([items[k] for k in strict]),
        "exposed": _over([items[k] for k in exposed]),
        "items": items,
        "counts": dict(Counter(items[k] for k in judged)),
        "exposed_items": {k: items[k] for k in exposed},
    }


def _law_outcome(state: dict, classes: list[int], value: int) -> str:
    """H7's outcome for one instance from its classes' intervals (lower bounds rounded up to
    even)."""
    ivs = [interval(state[i]["runs"]) for i in classes if i in state]
    if not ivs:
        return "not tested"
    if any(lo > value for lo, _ in ivs):
        return "above"
    if all(up <= value for _, up in ivs) and any(lo >= value for lo, _ in ivs):
        return "equal"
    if all(up < value for _, up in ivs):
        return "below"
    return "unresolved"


def _law_verdict(outcomes: dict[str, str], threshold: dict, proved=()) -> str:
    """H7's registered threshold (H7_RULE) over a set of instances: `outcomes` by key, the
    keys in `proved` (m/q = 1) left out of the fractions."""
    vals = list(outcomes.values())
    if not vals:
        return "not applicable"
    if "above" in vals or "fault" in vals:
        return "fails"
    judged = [v for key, v in outcomes.items() if key not in set(proved)]
    if not judged:
        return "not applicable"
    resolved = [v for v in judged if v in ("equal", "below")]
    if len(resolved) < threshold["resolved_fraction"] * len(judged):
        return "inconclusive"
    equal = sum(v == "equal" for v in resolved)
    return "holds" if equal >= threshold["equal_fraction"] * len(resolved) else "fails"


def _frontier_outcome(state: dict) -> dict:
    """H8's outcome on one torus (module docstring)."""
    if not state:
        return {"outcome": "not tested"}
    rank = ranking(state)
    if any(state[i]["base"] is None for i in state):
        return {"outcome": "not tested", "why": "a class's reduction is unknown"}
    cands = [i for i in state if rank["upper"][i] >= rank["L"]]
    if all(state[i]["base"] for i in cands):
        outcome = "holds"
    elif any(
        not state[i]["base"] and rank["lower"][i] == rank["upper"][i] >= rank["U"] for i in cands
    ):
        outcome = "fails"
    else:
        outcome = "unresolved"
    return {
        "outcome": outcome,
        "L": rank["L"],
        "U": rank["U"],
        "best": rank["best"],
        "candidates": sorted(cands),
        "not_reducing": sorted(i for i in cands if not state[i]["base"]),
    }


def _scores(state: dict) -> tuple[float, float]:
    rank = ranking(state)
    return rank["L"], rank["U"]


def _h7(preds: dict, records: dict, state: dict, structure_rows: dict) -> tuple[dict, dict]:
    """H7's outcome per instance (H7_RULE), and why where it is a fault or not tested for want
    of a class."""
    h7, why = {}, {}
    for x in preds["H7"]["instances"]:
        key = x["key"]
        rec = records.get(key)
        if rec is None or "error" in rec:
            h7[key] = "not tested"
            why[key] = "no record" if rec is None else "the job failed"
            continue
        classes = sorted(c["class"] for c in rec["classes"])
        rows_t = structure_rows.get(x["torus"])
        typed = None
        if rows_t is not None:
            typed = sorted(
                i
                for i, c in rows_t.items()
                if rules.has_type(c["structure"]["zeros"], *x["type"], x["l"], x["m"])
            )
        if typed is not None and typed != classes:
            h7[key], why[key] = "fault", "the torus job and the law job disagree on its classes"
            continue
        if not classes:
            if x["type_invariant"]:
                h7[key] = "fault"
                why[key] = (
                    "no class has a zero of this admissible type, which some code has (result "
                    "1's converse) and every code of its class then has (gcd(l, m) = 1)"
                )
            else:
                h7[key] = "not tested"
                why[key] = "no representative has a zero of the type (gcd(l, m) > 1)"
            continue
        out = _law_outcome(state.get(x["torus"], {}), classes, x["value"])
        if x["proved"] and out in ("above", "below"):
            h7[key], why[key] = "fault", f"{out}, where d = 2 is proved"
            continue
        h7[key] = out
    return h7, why


def decide(rows: list[dict], registered: list[dict]) -> dict:
    preds = {p["part"]: p for p in registered}
    protocol = preds["H5"]["protocol"]
    reg = preds["protocol"]
    specs = {j["key"]: j for j in reg["jobs"]}
    records, duplicates = {}, []
    for r in rows:
        if r.get("key") in records:
            duplicates.append(r.get("key"))
        records[r.get("key")] = r
    missing = [key for key in specs if key not in records]
    failed_jobs = sorted(key for key, r in records.items() if "error" in r)
    prior_failed = sorted(
        {e for r in records.values() if "error" not in r for e in r.get("prior_errors") or []}
    )
    now = code_hashes()
    code_changed = sorted(
        key for key in set(reg["sha256"]) | set(now) if reg["sha256"].get(key) != now.get(key)
    )
    torus_rec = {}
    for r in records.values():
        if r.get("test") == "torus" and "error" not in r:
            torus_rec[_name(r["l"], r["m"])] = r
    by_torus: dict[str, list[dict]] = {}
    for r in records.values():
        if "l" in r and "error" not in r:
            by_torus.setdefault(_name(r["l"], r["m"]), []).append(r)
    state = {name: merge(recs, *_torus(name)) for name, recs in by_torus.items()}
    structure_rows = {name: {c["class"]: c for c in r["classes"]} for name, r in torus_rec.items()}
    structural = {
        name: {
            i: [x for x in c["runs"] if x.get("instrument") in STRUCTURAL]
            for i, c in by_class.items()
        }
        for name, by_class in structure_rows.items()
    }
    off_protocol = {}
    for key, r in records.items():
        torus = _name(r["l"], r["m"]) if "l" in r and "m" in r else None
        f = protocol_failures(r, specs.get(key), protocol, structural.get(torus))
        if f:
            off_protocol[key] = f
    for recs in by_torus.values():
        for key, f in deep_bound_failures(recs).items():
            off_protocol.setdefault(key, []).extend(f)
    # a torus is complete when every registered job on it has a record that is not an error row
    # and names no failed earlier job
    unfinished = set()
    for key, spec in specs.items():
        r = records.get(key)
        if r is None or "error" in r or r.get("prior_errors"):
            unfinished.add(_name(spec["l"], spec["m"]))

    # H1: codes exist
    h1 = {}
    for name, want in preds["H1"]["predicted"].items():
        r = torus_rec.get(name)
        h1[name] = (
            "not tested"
            if r is None
            else ("holds" if (r["raw_k_positive"] > 0) == want else "fails")
        )
    # H2: max k
    h2, found_max = {}, {}
    for name, want in preds["H2"]["predicted"].items():
        r = torus_rec.get(name)
        if r is None:
            h2[name] = "not tested"
            continue
        got = r["max_k"]
        found_max[name] = got
        if want["value"] is not None:
            h2[name] = "holds" if got == want["value"] else "fails"
            continue
        ok = got <= want["bound"] and got % (2 * want["multiple"]) == 0
        odd_name = _name(*want["odd_torus"])
        if want["multiple"] > 1 and odd_name in torus_rec:
            ok = ok and got == want["multiple"] * torus_rec[odd_name]["max_k"]
        h2[name] = "holds" if ok else "fails"
    # H3: min k
    h3 = {}
    for name, want in preds["H3"]["predicted"].items():
        r = torus_rec.get(name)
        h3[name] = "not tested" if r is None else ("holds" if r["min_k"] == want else "fails")
    # H4: k-sets with one even side
    h4, h4_sets = {}, {}
    for name, want in preds["H4"]["predicted"].items():
        r = torus_rec.get(name)
        if r is None or want["source"] == "not tested":
            h4[name] = "not tested"
            continue
        if want["source"] == "this run":
            odd_rec = torus_rec.get(_name(*want["odd_torus"]))
            if odd_rec is None:
                h4[name] = "not tested"
                continue
            expected = rules.lifted_kset(odd_rec["kset"], *_torus(name))
        else:
            expected = want["kset"]
        h4_sets[name] = {"expected": expected, "found": r["kset"], "source": want["source"]}
        h4[name] = "holds" if r["kset"] == expected else "fails"
    # H5: d = 2 exactly when (i) or (ii)
    h5, h5_detail = {}, {}
    for name, r in torus_rec.items():
        if not r["classes"]:
            continue
        mismatch, unresolved = [], []
        for c in r["classes"]:
            want = c["structure"]["cond_i"] or c["structure"]["cond_ii"]
            d2 = next((x for x in c["runs"] if x.get("instrument") == "d2"), None)
            if d2 is None or d2.get("status") != "complete":
                unresolved.append(c["class"])
                continue
            got = d2["d"] == 2 and d2.get("verified") is True
            if d2["d"] is None and d2.get("lower") != D2_BOUND:
                unresolved.append(c["class"])
            elif got != want:
                mismatch.append(c["class"])
        h5[name] = "fails" if mismatch else ("unresolved" if unresolved else "holds")
        h5_detail[name] = {
            "classes": len(r["classes"]),
            "mismatch": mismatch,
            "unresolved": unresolved,
            "d2": sum(c["structure"]["cond_i"] or c["structure"]["cond_ii"] for c in r["classes"]),
        }
    for name in preds["H5"]["tori"]:
        h5.setdefault(name, "not tested" if name not in torus_rec else "holds")
    # H6: the proved bounds and the instruments, on every torus with codes
    h6_tori = sorted(
        set(preds["H6"]["tori"]) | {name for name, r in torus_rec.items() if r["classes"]},
        key=lambda t: (_torus(t)[0] * _torus(t)[1], _torus(t)),
    )
    h6, h6_problems = {}, {}
    for name in h6_tori:
        st = state.get(name, {})
        probs = run_problems(st, structure_rows.get(name, {}))
        if probs:
            h6_problems[name] = probs
            h6[name] = "fails"
        elif name not in torus_rec:
            h6[name] = "not tested"
        elif name in unfinished or _errors(st):
            h6[name] = "unresolved"
        else:
            h6[name] = "holds"
    h6_all = list(h6.values())
    if "fails" in h6_all:
        h6_outcome = "fails"
    elif h6_all and all(v == "holds" for v in h6_all):
        h6_outcome = "holds"
    elif all(v == "not tested" for v in h6_all):
        h6_outcome = "not tested"
    else:
        h6_outcome = "incomplete"
    # H7: the linear law
    h7, h7_why = _h7(preds, records, state, structure_rows)
    thr = preds["H7"]["threshold"]
    status7 = {x["key"]: exposure_status(x["l"], x["m"]) for x in preds["H7"]["instances"]}
    proved = sorted(x["key"] for x in preds["H7"]["instances"] if x["proved"])
    faults = sorted(key for key, v in h7.items() if v == "fault")

    def law(keep):
        return _law_verdict({k: v for k, v in h7.items() if keep(status7[k])}, thr, proved)

    h7_part = {
        "outcome": law(lambda s: s != "exposed"),
        "strict": law(lambda s: s == "clean"),
        "exposed": law(lambda s: s == "exposed"),
        "items": h7,
        "why": h7_why,
        "proved": {k: h7[k] for k in proved},
        "faults": faults,
        "counts": dict(
            Counter(v for k, v in h7.items() if status7[k] != "exposed" and k not in proved)
        ),
        "threshold": thr,
    }
    # H8: the best classes reduce to the base
    h8, h8_detail = {}, {}
    for name in preds["H8"]["tori"]:
        if name not in torus_rec:
            h8[name] = "not tested"
            continue
        st = state.get(name, {})
        for i, row in structure_rows[name].items():
            st.setdefault(
                i,
                {
                    "class": i,
                    "rep": row["rep"],
                    "k": row["k"],
                    "runs": [],
                    "base": row["structure"]["base"],
                    "conflicts": [],
                },
            )
        d = _frontier_outcome(st)
        h8_detail[name] = d
        h8[name] = d["outcome"]
    # H9: the best at n is on a torus with 3 | l and 3 | m (stage-1 tori: exact, looked up)
    h9, h9_detail = {}, {}
    for n, at in preds["H9"]["sizes"].items():
        tori = at["three"] + at["other"]
        if any(t not in torus_rec for t in tori):
            h9[n] = "not tested"
            continue
        stage1 = at.get("stage1", {})

        def scores(names, kind, stage1=stage1):
            ls = [_scores(state.get(t, {})) for t in names if state.get(t)]
            ls += [(v["score"], v["score"]) for v in stage1.values() if v["kind"] == kind]
            return max((a for a, _ in ls), default=0), max((b for _, b in ls), default=0), ls

        out = {}
        for label, keep in (
            ("judged", lambda t: exposure_status(*_torus(t)) != "exposed"),
            ("strict", lambda t: exposure_status(*_torus(t)) == "clean"),
            ("all", lambda t: True),
        ):
            three = [t for t in at["three"] if keep(t)]
            other = [t for t in at["other"] if keep(t)]
            l3, u3, s3 = scores(three, "three")
            lo_, uo, so = scores(other, "other")
            if not s3:
                out[label] = {"outcome": "not applicable"}
                continue
            if not so:
                out[label] = {"outcome": "holds", "uncontested": True, "L3": l3, "U3": u3}
                continue
            verdict = "holds" if l3 >= uo else ("fails" if lo_ > u3 else "unresolved")
            out[label] = {
                "outcome": verdict,
                "uncontested": False,
                "L3": l3,
                "U3": u3,
                "L_other": lo_,
                "U_other": uo,
            }
        h9_detail[n] = out
        h9[n] = out["judged"]["outcome"]
    h9_part = {
        "outcome": "fails"
        if "fails" in h9.values()
        else (
            "holds"
            if h9 and all(v in ("holds", "not applicable") for v in h9.values())
            else "incomplete"
        ),
        "items": h9,
        "detail": h9_detail,
        "with_exposed": {n: d["all"]["outcome"] for n, d in h9_detail.items()},
        "strict": {n: d["strict"]["outcome"] for n, d in h9_detail.items()},
    }

    parts = {
        "H1": _part(h1),
        "H2": {**_part(h2), "found": found_max},
        "H3": _part(h3),
        "H4": {**_part(h4), "sets": h4_sets},
        "H5": {**_part(h5), "detail": h5_detail},
        "H6": {
            **_part(h6),
            "outcome": h6_outcome,
            "problems": h6_problems,
            "note": "judged on every torus with codes, exposed ones included: it tests the "
            "instruments, which exposure does not bear on",
        },
        "H7": h7_part,
        "H8": {**_part(h8), "detail": h8_detail},
        "H9": h9_part,
    }
    instruments_fail = bool(h6_problems or off_protocol or duplicates or faults)
    if instruments_fail:
        instruments = "fail"
    else:
        instruments = {"holds": "hold", "not tested": "not tested"}.get(h6_outcome, "incomplete")
    outcomes = {p: v["outcome"] for p, v in parts.items()}
    if instruments_fail or "fails" in outcomes.values():
        overall = "fail"
    elif all(v in ("holds", "not applicable") for v in outcomes.values()) and not (
        missing or failed_jobs or prior_failed or code_changed
    ):
        overall = "hold"
    else:
        overall = "incomplete"
    return {
        "verdict": overall,
        "parts": outcomes,
        "instruments": instruments,
        "missing": missing,
        "failed_jobs": failed_jobs,
        "prior_failed": prior_failed,
        "code_changed": code_changed,
        "duplicates": duplicates,
        "protocol_failures": off_protocol,
        "detail": parts,
        "verdict_rule": reg["verdict_rule"],
        "exposed_note": "exposed tori are reported beside the verdict (each part's 'exposed'); "
        "tori isomorphic to an exposed torus are judged, and each part's 'strict' leaves them "
        "out",
        "known_limitations": KNOWN_LIMITATIONS,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
