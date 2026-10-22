"""
A census of bivariate bicycle codes of the published form, stage 1: an exploratory survey, not a
registered test. Its patterns are meant to feed a registered stage 2 on the held-out tori.

    uv run --no-sync python examples/qec-census/census.py run          (2 workers; --workers N)
    uv run --no-sync python examples/qec-census/census.py summary
    uv run --no-sync python examples/qec-census/census.py classes L M   (k and classes only)

**The family.** A = x^a + y^b + y^c and B = y^d + x^e + x^f on the l x m torus, with b != c in
Z_m, e != f in Z_l, and a in Z_l, d in Z_m arbitrary: the form of Bravyi et al.'s codes
(examples/qec-bb/codes.json). A *raw code* is one pair (A, B) of the form, a choice of a, d and
of the sets {b, c} and {e, f}, so a torus has l C(m, 2) m C(l, 2) of them (`raw_parameters`,
in census.c's order). Distinct choices give distinct pairs: when A has three monomials, the one
off the y-axis, or (0, 0) when all three are on it, fixes a. When a = 0 and 0 is in {b, c}, two
monomials cancel and A is a monomial, a unit, so k = 0 (likewise B); every code with k > 0 has
weights 3 and 3.

**The tori** are holdout.json's stage1_tori, 2 <= l <= m and lm <= 100 (n = 2lm <= 200). The
orientation m x l would give nothing new: exchanging x and y carries the form on l x m to the
form on m x l with the roles of A and B exchanged, and swapping A and B is an equivalence (it
swaps the blocks), so each code on m x l is equivalent to one on l x m. So l <= m suffices.

**The hold-out** (`guard`). Nothing here computes anything, not even k, on a torus of
holdout.json's held_out_random or held_out_extrapolation, or on one of them in the other
orientation. Every function here that computes anything on a torus's codes calls `guard` first,
the helpers of `structure` and of the distances included, and `summarize` calls it on every
file's torus before reading its rows; `guard` also refuses every torus outside stage1_tori. By
default it refuses, too, the 8 stage-1 tori that are isomorphic as groups to a held-out torus
(`isomorphic_held_out`; for example 6 x 11 and 2 x 33 are both Z_66): codes on isomorphic tori
correspond under the isomorphism (distance.torus_type), so a census of 6 x 11 would compute codes
equivalent to some of the held-out 2 x 33's codes, with their distances. holdout.json does not
exclude them, and `allow_isomorphic` (run's --allow-isomorphic) includes them; the choice is
recorded in every file's header. For this family the overlap is smaller than that, by the lemma
below. 3 of the 8 (2 x 36, 4 x 14, 6 x 16) have no code of the family with k > 0. The held-out
tori isomorphic to 3 x 26, 5 x 14, 6 x 13 and 7 x 10 are 2 x 39 and 2 x 35, where the family has
none either; k is invariant, so no code of the family with k > 0 on those four is equivalent to
a code of the family there. Only 6 x 11 overlaps: x -> x'y'^11, y -> y'^2 carries Z_6 x Z_11
onto Z_3 x Z_22, and the family's codes with a, e and f even onto codes of the family on the
held-out 3 x 22. Refusing all 8 remains the default; torus_type's rule argues for it whenever
stage 2 may test codes beyond this form. Stage 2 (examples/qec-census-2) computes on the
held-out tori through one narrow exception, added after stage 1 ran (stage 1's files record the
census.py they were made with): `Stage2Permit`, which opens a registered held-out torus to guard
only inside stage 2's job function, and only while stage 2's ledger holds its registration and a
run that has started. Nothing else changed here; the 8 refused tori stay refused.

**k** (`ranks`, census.c). k = 2lm - rank H_X - rank H_Z, by Gaussian elimination on bitset rows
in C, over every raw code of a torus in one call. rank H_Z = rank H_X for every bivariate
bicycle code (H_Z = P H_X Φ, distance.py's docstring), so the census computes rank H_X only and
k = 2lm - 2 rank H_X; the tests compute both ranks on every raw code of several tori and compare
k with bb.k_linalg and bb.k_characters on random raw codes.

**A lemma: where l or m is a power of 2, every code of the family has k = 0.** k is
2 Σ dim L/(A_χ, B_χ), summed over the characters χ of the torus's odd part (bb.local_terms), and
a term is 0 when A_χ or B_χ is a unit of the local ring L, that is, when its residue A(α, β) or
B(α, β) is nonzero. When l is a power of 2, its odd part is 1, so α = 1 at every χ and B's
residue is β^d + 1 + 1 = β^d (e != f), which is nonzero; when m is, A's residue is α^a. 66 of the
116 tori the census runs on by default are of this kind, and they are 66 of the 81 at which it
finds k = 0 throughout; the other 15 (10 x 10, 9 x 11 and 5 x 5 among them) have no such
reason. The tests check the lemma on small tori. It holds on held-out tori too, by their sizes
alone: 16 of the 22 in held_out_random and 45 of the 100 in held_out_extrapolation have l or m a
power of 2, so the family has no code with k > 0 there. A stage 2 on this family must weigh that
(widen the family, or choose tori where it can have k > 0).

**Classes** (`classes`). The codes with k > 0 are grouped under the equivalences of
examples/qec-distance-2's equivalence_key: monomial factors on A and on B, swapping A and B, and
automorphisms of Z_l x Z_m. census.c computes that key (its docstring says how), and the tests
check that it is equivalence_key's on random pairs and on every code of the family with k > 0 at
small tori, and that the classes are exactly the orbits of that group among the family's codes
(`orbit_partition`, which applies every group element). Equivalent codes have the same n, k and
distances. Codes in different classes may still be equivalent under some other permutation of
the qubits (equivalence_key's docstring): the classes are an upper bound on the number of codes
up to equivalence, not the number. Each class records its representative (the least raw code of
it, in census.c's order), its size (the number of raw codes in it), its k, and that k is the
same for all of its raw codes (checked at run time).

**Distances** (`class_distance`, `ilp_selection`, `compare`, `recheck`). For each class
representative,
distance.distance_search of kind Z (d = d_Z = d_X for these codes, distance.py's docstring),
deepening, from the anchors (0, lm), with a time limit of `Options.search_limit`. A search that
completes gives d exactly (resting on its argument, its code and the translation argument); one
stopped at its limit gives bounds, which are recorded: the largest bound of a pass that ended
with nothing found (lower; None if none ended, so d >= 1 only) and the lightest logical found
(upper; None if none); the class then goes to the program, below, and the summary lists it as
open wherever its bounds leave room above the best at its n. Every witness is checked with
distance.verify_witness. Then distance.distance_ilp (SCIP with
distance.SCIP_FIX, seed distance.SEED) runs, with a limit of `Options.ilp_limit`, on (i) every
class of the torus whose exact d gives the torus's best k d^2 / n, ties included (so every class
best at its n, over all tori of that n, is among them), (ii) every class whose search stopped
at its limit, and (iii) a random sample of the rest, `Options.sample` of them rounded up and at
least one where the rest is not empty (random.Random(f"qec-census stage1 sample {l}x{m}")).
The two intervals must meet: an instrument's interval is [lower, upper], upper being the weight
of its witness when that witness passes verify_witness and unbounded otherwise. The cross-check
is "agree" when both are exact (search complete, program optimal) with the same d and both
witnesses pass verify_witness, "consistent" when the intervals meet otherwise, and "disagree"
when they do not. A disagreement, or a witness that fails, is recorded in the class's row,
printed to stderr, and listed first by `summary`. (iv) Each class of (i) whose cross-check is
not "agree" (in development, the best classes at d >= 16, where the program stops at its limit
with 12 <= d or 13 <= d) gets a second search, `recheck`: distance_search of kind X from every
qubit, with the search's limit, compared with the first search in the same way. It rests on
neither the translation argument nor d_X = d_Z, though it shares search.c with the first.

**Structure, per class** (for later analysis; `structure`). The characters of the torus's odd
part at which the local term dim L/(A_χ, B_χ) is nonzero, with their terms (bb.local_terms;
2 Σ terms must equal k, and the row records it); their Frobenius orbits (χ -> χ^2) with sizes
and terms; the weights (3 and 3); and, from census.c, the number of torus automorphisms φ with
φ(A) ~ A and φ(B) ~ B (P ~ Q: Q is a monomial times P; identity included) and the number with
φ(A) ~ B and φ(B) ~ A, from which the stabiliser of (A, B) in the equivalence group follows; and
the dilations (x, y) -> (x^u, y^u), u != 1, that fix the code in that sense (the half-Frobenius
mechanism is u = 2). Each such φ gives a permutation of the qubits that preserves the code.
The torus's 2-part and odd part are in the file's header. The stabiliser is
(fixes + swaps) |Stab_T(A)| |Stab_T(B)|, with Stab_T(P) the translations fixing P: for each such
φ, the monomial factors that finish the job form cosets of those stabilisers. The tests count it
by brute force on small tori.

**The summary** (`summarize`, `print_summary`). summary.json holds every torus's counts, every
problem (disagreements first), and the frontier: for each n, the best [[n, k, d]] by k d^2 / n
among classes whose d is established (ties listed), the best d for each k, and the open classes.
d is established (`established`) where the intersection of the instruments' intervals is a single
point: by the search alone (it completed), by the program alone (optimal), by both, or only by
their bounds together. Each entry of the best and of the best d for each k says which ("d_by"),
with the cross-check, the program's [lower, upper], whether the search's witness passed
verify_witness, and the second search's outcome, so a d that the program only brackets (in
development, the best at n = 180 to 198) shows as resting on the search. A class with a
disagreement, a witness that fails or a k at odds is left out of the frontier and listed under
its n's "excluded" (and, like every problem, first). A class is open where its interval is not a
point and leaves room above the best. Classes on isomorphic tori of the census (6 x 15 and
3 x 30, for example: the census keeps each torus apart, and their families differ) are matched by
carrying each key onto one torus of the type (`cross_torus`), and counted once in each n's
"distinct". The published entries of ../qec-bb/codes.json, in the l <= m orientation, are placed
by their equivalence_key: in the census or not, and if so with their rank by k d^2 / n among the
distinct classes at their n and among the classes of their torus. [[288,12,18]] is on the
held-out 12 x 12 and is not placed (nothing is computed for it).

**Running** (`run`, `census_torus`). One worker process per torus, each on one core, 2 at a time
by default (--workers). The tori that took longest in development (`COSTLY`) go first, then the
rest, the largest first; the order changes no result, only what a stop cuts short. The worker
writes data/LxM.jsonl when the torus is done (a header line, then one line per class), by
writing a temporary file and renaming it, so a stop loses only the tori in flight. --data is
resolved against the working directory before the workers start. Resume (run again) skips every
torus with a file, and refuses to mix files made under other options, apart from
allow_isomorphic, which changes which tori run, not how a torus is computed: a later run with
--allow-isomorphic adds the 8. The header records the solver version, SCIP_FIX, the sha256 of
search.c, census.c, census.py and holdout.json, the seeds and the limits. Linux kills a worker
when the run's process dies.

**Limits and time** (development timings, 2026-10-22, on single cores of this 4-core machine).
- **k** for every raw code of the 116 tori the census runs on by default (5,472,121 codes) took
  32 s, about 170,000 codes/s (115,000/s at lm = 100). The classes, with census.c's canonical
  form, took 74 s more for all of them. Only 35 of those tori have any code with k > 0, 3,330
  classes in all: the form has k = 0 throughout at the other 81 (10 x 10, 9 x 11 and 2 x 50
  among them).
- **The search.** Every one of the 3,330 classes completed in development, in 1,084 s in all,
  the slowest in 26 s (d = 18): 3 x 33 (253 classes, n = 198) in 457 s, 6 x 15 (680, n = 180)
  in 308 s, 3 x 30 (529, n = 180) in 167 s. search_limit (600 s) is therefore a guard, not a
  working limit.
- **The second search** (kind X, from every qubit) costs about 11 times the first, nearly all of
  it from searching from every qubit (on 6 x 15's best class, 21.5 s from every qubit and 1.9 s
  from (0, lm), for either kind): 25 s on 6 x 15's best class, 23 s on 3 x 33's, 223 s on
  7 x 14's (d = 18). By the development data it falls on those 4 best classes at d >= 16, about
  5 minutes in all.
- **The program.** At n = 180 to 198 it took up to 8.5 s for d <= 10, 26 to 47 s for d = 12
  and 121 to 230 s for d = 14 (121 s on a class of 3 x 30, 214 s at n = 198), and stopped at
  600 s with 12 <= d or 13 <= d for every d = 16 or 18 tried (5 codes); every one of those runs
  met the search. In the whole-torus runs below, d = 14 took 186 s at n = 162 and 299 s at
  n = 196. ilp_limit is 600 s: a d = 14 class at n <= 200 finishes within it, and the classes
  at d >= 16, which do not, are the best of the largest tori and some of their samples.
- **Whole tori** (`torus`, all stages, default options, before the second search): 7 x 14
  (lm = 98, 156 classes, 9 programs) took 1,709 s, 1,613 of it in the program (two programs at
  their limit, on d = 16 and 18); 5 x 18 (lm = 90, 28 classes, 15 programs: 14 tied for best at
  d = 12) 643 s; 9 x 9 (lm = 81, 68 classes, 5 programs) 320 s, 294 of it in the program; 6 x 9
  (lm = 54, 188 classes) 66 s; 6 x 12 (lm = 72, 331 classes, 18 programs) 47 s; 3 x 18 (lm = 54,
  164 classes, 11 programs) 47 s; 6 x 6 (47 classes, 4 programs) 2 s. Every program met its
  search.
- **The estimate.** Replaying `ilp_selection` on the development search of every class of the
  35 tori gives 297 programs. At about 1 s for d <= 6, 5 to 10 s for d = 8 and 10, 45 s for
  d = 12, 250 s for d = 14 and the 600 s limit for d >= 16, the run needs about 5.3 CPU hours:
  6 x 15 about 90 minutes (35 programs, 7 at d = 14 and 5 at d = 16), the longest job; 3 x 33
  about 65 (15 programs: its 2 best, at d = 16, and 13 samples, 2 at d = 8, 4 at 10, 1 at 12,
  4 at 14 and 2 at 16); 3 x 30 about 50; 7 x 14 about 30; 3 x 27 about 20; 9 x 10 about 17
  (22 classes tied for best at d = 12); 5 x 18 about 11; 3 x 24 about 10; minutes or less for the
  rest, and a few seconds for each of the 81 tori without classes. With 2 workers (the default:
  the machine is shared) and COSTLY first, that is about 2.6 hours of wall clock (about 1.5
  with 4). A cloud session's background command stops at two hours, so expect one resume; by
  this estimate the tori in flight at the stop are 7 x 14 and 3 x 27, about 35 minutes of work
  redone, so about 3.2 hours in all (largest first, 6 x 15 would have been in flight, about 45
  minutes lost). The worst case, every program at n >= 180 stopping at its limit, would make
  6 x 15's 35 programs alone about 6 hours. Both are below the 8-hour budget, so no rule cuts
  the work by default. Two options are there for a tighter budget, recorded in every header:
  --distance-kmin K (no distances for classes with k < K; at 3 x 33, 7 x 14, 3 x 30 and 6 x 15,
  68 to 89% of the classes have the torus's least k, 4, or 6 at 7 x 14) and --ilp-limit. The 8
  tori isomorphic to held-out ones (included only with --allow-isomorphic) were not timed,
  since timing them would compute on them; by the lemma, 3 of them have no class at all.

**What is not established.** The census covers one family of one form, and the classes are an
upper bound on its inequivalent codes. d rests on the search where it completes; the program
checks it on a selection only, and its lower bounds rest on SCIP with SCIP_FIX. Where the
program only brackets a best class, its d rests on search.c alone (the second search removes
the translation argument and d_X = d_Z from under it, not search.c). A class whose instruments
leave an interval has bounds, not d. Nothing here bears on performance under circuit noise.
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import hashlib
import importlib.util
import json
import math
import os
import platform
import random
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qec-bb"))
sys.path.insert(0, str(HERE.parent / "qec-distance"))

import bb  # noqa: E402
import distance  # noqa: E402

# examples/qec-distance-2, for equivalence_key and the automorphisms of the torus (_isomorphisms)
_spec = importlib.util.spec_from_file_location(
    "qec_distance_retest", HERE.parent / "qec-distance-2" / "study.py"
)
retest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(retest)

HOLDOUT = HERE / "holdout.json"
CENSUS_C = HERE / "census.c"
DATA = HERE / "data"
SUMMARY = HERE / "summary.json"
PUBLISHED = HERE.parent / "qec-bb" / "codes.json"
PYTHON = HERE.parent.parent / ".venv" / "bin" / "python"
SAMPLE_SEED = "qec-census stage1 sample {l}x{m}"
WEIGHTS = (3, 3)


@dataclasses.dataclass(frozen=True)
class Options:
    """The census's limits and rules, recorded in every file's header. search_limit and
    ilp_limit are wall-clock seconds per class; sample is the fraction of the remaining classes
    of a torus that the program cross-checks; distance_kmin skips the distances (search and
    program) of classes with k below it (0: every class), the budget rule; allow_isomorphic
    includes the stage-1 tori isomorphic to a held-out torus (module docstring)."""

    search_limit: float = 600.0
    ilp_limit: float = 600.0
    sample: float = 0.05
    distance_kmin: int = 0
    allow_isomorphic: bool = False

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


DEFAULTS = Options()


# ---------------------------------------------------------------- the hold-out


class HeldOut(ValueError):
    """A torus the census must not compute anything on."""


@functools.cache
def holdout() -> dict:
    return json.loads(HOLDOUT.read_text())


def _tori(key: str) -> list[tuple[int, int]]:
    return [(int(a), int(b)) for a, b in holdout()[key]]


def stage1_tori() -> list[tuple[int, int]]:
    return _tori("stage1_tori")


def held_out_tori() -> set[tuple[int, int]]:
    """Every held-out torus, in both orientations."""
    out = set()
    for key in ("held_out_random", "held_out_extrapolation"):
        for a, b in _tori(key):
            out |= {(a, b), (b, a)}
    return out


def isomorphic_held_out(ell: int, m: int) -> list[tuple[int, int]]:
    """The held-out tori (l <= m) isomorphic to Z_l x Z_m as groups (distance.torus_type)."""
    kind = distance.torus_type(ell, m)
    return sorted(t for t in held_out_tori() if t[0] <= t[1] and distance.torus_type(*t) == kind)


def guard(ell: int, m: int, allow_isomorphic: bool = False) -> None:
    """Refuse (HeldOut) a held-out torus in either orientation, any torus outside stage1_tori
    (l <= m), and, unless allow_isomorphic, a stage-1 torus isomorphic to a held-out one. Every
    function here that computes on a torus's codes calls it first (raw_count, torus_file and
    ilp_selection, which count, name a file or choose among rows, compute nothing on codes), and
    summarize calls it on every file's torus. The one exception is a held-out torus, in
    holdout.json's l <= m orientation, inside a Stage2Permit (below): stage 2's registered run."""
    ell, m = int(ell), int(m)
    if (ell, m) in held_out_tori():
        if (ell, m) in _STAGE2_OPEN:
            return
        raise HeldOut(f"{ell}x{m} is held out of stage 1 (holdout.json)")
    if (ell, m) not in set(stage1_tori()):
        raise HeldOut(f"{ell}x{m} is not a stage-1 torus (holdout.json's stage1_tori, l <= m)")
    if not allow_isomorphic and isomorphic_held_out(ell, m):
        names = ", ".join(f"{a}x{b}" for a, b in isomorphic_held_out(ell, m))
        raise HeldOut(f"{ell}x{m} is isomorphic to the held-out {names} (allow_isomorphic)")


# ---------------------------------------------------------------- stage 2's permit

STAGE2 = HERE.parent / "qec-census-2"
STAGE2_STUDY = STAGE2 / "study.py"
STAGE2_LEDGER = STAGE2 / "ledger.jsonl"
STAGE2_ID = "qec-census-stage2"
_STAGE2_OPEN: frozenset = frozenset()  # the held-out tori a Stage2Permit has opened


def stage2_registration_problem(tori, ledger_path: Path | None = None) -> str | None:
    """Why stage 2's ledger does not permit computing on `tori`, or None when it does: the
    ledger's hash chain verifies, and it holds stage 2's registration (a question with id
    STAGE2_ID, then its predictions) followed by run_started and nothing but run_resumed
    entries (a run that has started and has not yet written its observations), and every torus
    of `tori` is a held-out torus (l <= m) listed in the question's "tori"."""
    from lattice_lab.ledger import Ledger, LedgerError

    path = Path(ledger_path) if ledger_path is not None else STAGE2_LEDGER
    if not path.is_file():
        return f"{path} does not exist: stage 2 is not registered"
    try:
        ledger = Ledger(path)
    except LedgerError as exc:
        return f"{path} is not a ledger: {exc}"
    if ledger.verify():
        return f"{path} does not verify: {ledger.verify()[:3]}"
    kinds = [e["kind"] for e in ledger.entries]
    if "run_started" not in kinds:
        return f"{path} has no run_started: the registered run has not started"
    start = kinds.index("run_started")
    if (start < 2 or kinds[:start] != ["question"] + ["prediction"] * (start - 1)
            or any(k != "run_resumed" for k in kinds[start + 1 :])):  # fmt: skip
        return f"{path} is not a registration with a run in progress: {kinds}"
    question = ledger.entries[0]["body"]
    if question.get("id") != STAGE2_ID:
        return f"{path}'s question is not {STAGE2_ID}"
    registered = {(int(a), int(b)) for a, b in question.get("tori", [])}
    held = {t for t in held_out_tori() if t[0] <= t[1]}
    for t in tori:
        if t not in held:
            return f"{t[0]}x{t[1]} is not a held-out torus in holdout.json's orientation"
        if t not in registered:
            return f"{t[0]}x{t[1]} is not among the registered tori"
    return None


class Stage2Permit:
    """The one way to compute on a held-out torus: `with Stage2Permit([(l, m)]):` opens those
    tori to `guard` until the block ends, and only when (1) the `with` statement is in a function
    named `job` defined in examples/qec-census-2/study.py (the registered study's job, which its
    worker processes call), and (2) stage2_registration_problem finds nothing (stage 2 registered,
    its run started, these tori registered). Otherwise it raises HeldOut and opens nothing. The
    tori stay in holdout.json's l <= m orientation; the other orientation, and every refused or
    non-stage-1 torus, stay refused. The check of the caller is by its code object's name and
    file: it keeps anything else here from computing on a held-out torus by accident, and is not
    a defence against code written to get round it. Permits do not nest."""

    def __init__(self, tori):
        self.tori = frozenset((int(a), int(b)) for a, b in tori)

    def __enter__(self):
        global _STAGE2_OPEN
        caller = sys._getframe(1).f_code
        if caller.co_name != "job" or Path(caller.co_filename).resolve() != STAGE2_STUDY:
            raise HeldOut("a Stage2Permit is for examples/qec-census-2/study.py's job only, not "
                          f"{caller.co_name} in {caller.co_filename}")  # fmt: skip
        if _STAGE2_OPEN:
            raise HeldOut("a Stage2Permit is already open")
        problem = stage2_registration_problem(self.tori)
        if problem:
            raise HeldOut(f"no Stage2Permit: {problem}")
        _STAGE2_OPEN = self.tori
        return self

    def __exit__(self, *exc) -> bool:
        global _STAGE2_OPEN
        _STAGE2_OPEN = frozenset()
        return False


def census_tori(allow_isomorphic: bool = False) -> list[tuple[int, int]]:
    """The tori the census runs on, the largest (lm) first."""
    tori = [t for t in stage1_tori() if allow_isomorphic or not isomorphic_held_out(*t)]
    return sorted(tori, key=lambda t: (-t[0] * t[1], t))


# ---------------------------------------------------------------- the raw codes and k (C)


def raw_count(ell: int, m: int) -> int:
    return ell * math.comb(m, 2) * m * math.comb(ell, 2)


def raw_parameters(ell: int, m: int, allow_isomorphic: bool = False) -> np.ndarray:
    """Every raw code (a, b, c, d, e, f), b < c, e < f, one row each, in census.c's order:
    a, then (b, c), then d, then (e, f), the last varying fastest."""
    guard(ell, m, allow_isomorphic)
    bc = np.array([(b, c) for b in range(m) for c in range(b + 1, m)], dtype=np.int64)
    ef = np.array([(e, f) for e in range(ell) for f in range(e + 1, ell)], dtype=np.int64)
    ia, ibc, idd, ief = (
        g.ravel()
        for g in np.meshgrid(
            np.arange(ell), np.arange(len(bc)), np.arange(m), np.arange(len(ef)), indexing="ij"
        )
    )
    return np.column_stack([ia, bc[ibc, 0], bc[ibc, 1], idd, ef[ief, 0], ef[ief, 1]])


def polynomials(params) -> tuple[list[list[int]], list[list[int]]]:
    """(A, B) of a raw code (a, b, c, d, e, f), as exponent pairs (unreduced)."""
    a, b, c, d, e, f = (int(v) for v in params)
    return [[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.cache
def _census_binary() -> str:
    """census.c compiled with the system's cc into a temporary directory (removed when the
    process exits), once per process."""
    import atexit

    directory = Path(tempfile.mkdtemp(prefix="qec-census-"))
    atexit.register(shutil.rmtree, directory, True)
    binary = directory / "census"
    subprocess.run(["cc", "-O2", "-o", str(binary), str(CENSUS_C)], check=True,
                   capture_output=True)  # fmt: skip
    return str(binary)


def ranks(ell: int, m: int, check: bool = False, allow_isomorphic: bool = False) -> np.ndarray:
    """rank_GF2(H_X) of every raw code, in raw_parameters' order, by census.c; with `check`,
    an array of shape (count, 2) holding rank H_X and rank H_Z."""
    guard(ell, m, allow_isomorphic)
    args = [_census_binary(), "k", str(ell), str(m)] + (["check"] if check else [])
    out = subprocess.run(args, check=True, capture_output=True).stdout
    r = np.frombuffer(out, dtype=np.uint8).astype(np.int64)
    width = 2 if check else 1
    if len(r) != width * raw_count(ell, m):
        raise RuntimeError(f"census.c gave {len(r)} ranks for {raw_count(ell, m)} codes")
    return r.reshape(-1, 2) if check else r


def k_all(ell: int, m: int, allow_isomorphic: bool = False) -> np.ndarray:
    """k = 2lm - 2 rank H_X for every raw code (rank H_Z = rank H_X: module docstring)."""
    return 2 * ell * m - 2 * ranks(ell, m, allow_isomorphic=allow_isomorphic)


# ---------------------------------------------------------------- the classes


def automorphisms(ell: int, m: int, allow_isomorphic: bool = False) -> tuple:
    """Every automorphism of Z_l x Z_m, as the images of (1, 0) and (0, 1) (qec-distance-2's
    _isomorphisms)."""
    guard(ell, m, allow_isomorphic)
    return retest._isomorphisms((ell, m), (ell, m))


def _key_pairs(indices, m: int) -> tuple:
    return tuple(tuple((t // m, t % m) for t in indices[i : i + 3]) for i in (0, 3))


def canonical(codes, ell: int, m: int, allow_isomorphic: bool = False) -> list[tuple]:
    """For each code (A, B), each of three distinct monomials mod (l, m), census.c's
    (key, fixes, swaps): key in equivalence_key's form; fixes, the number of automorphisms φ
    with φ(A) ~ A and φ(B) ~ B; swaps, the number with φ(A) ~ B and φ(B) ~ A."""
    guard(ell, m, allow_isomorphic)
    auts = automorphisms(ell, m, allow_isomorphic)
    lines = [str(len(auts))]
    lines += [f"{g0} {g1} {h0} {h1}" for (g0, g1), (h0, h1) in auts]
    lines.append(str(len(codes)))
    for A, B in codes:
        for P in (A, B):
            reduced = retest._reduce(P, ell, m)
            if len(reduced) != 3:
                raise ValueError(f"not three monomials: {P}")
            lines.append(" ".join(f"{p} {q}" for p, q in reduced))
    out = subprocess.run([_census_binary(), "canon", str(ell), str(m)], input="\n".join(lines),
                         check=True, capture_output=True, text=True).stdout  # fmt: skip
    rows = [list(map(int, line.split())) for line in out.splitlines()]
    if len(rows) != len(codes) or any(len(r) != 8 for r in rows):
        raise RuntimeError("census.c gave a malformed canonical form")
    return [(_key_pairs(r[:6], m), r[6], r[7]) for r in rows]


def _translation_stabilizer(P, ell: int, m: int, allow_isomorphic: bool = False) -> int:
    """The number of translations t with P + t = P."""
    guard(ell, m, allow_isomorphic)
    P = [tuple(u) for u in retest._reduce(P, ell, m)]
    first = {((p - P[0][0]) % ell, (q - P[0][1]) % m) for p, q in P}
    return sum({((p - u[0]) % ell, (q - u[1]) % m) for p, q in P} == first for u in P)


def classes(ell: int, m: int, allow_isomorphic: bool = False) -> dict:
    """The torus's raw codes, their k, and the classes of those with k > 0: a dict with the
    counts (raw codes, raw codes by k, classes by k) and `classes`, a list of dicts, one per
    class, the largest k first: representative (the least raw index, its parameters and
    polynomials), key, size, k, fixes and swaps (census.c's, at the representative)."""
    guard(ell, m, allow_isomorphic)
    start = time.time()
    params = raw_parameters(ell, m, allow_isomorphic)
    k = k_all(ell, m, allow_isomorphic)
    k_seconds = time.time() - start
    keep = np.flatnonzero(k > 0)
    codes = [polynomials(params[i]) for i in keep]
    for A, B in codes:
        if [len(retest._reduce(P, ell, m)) for P in (A, B)] != list(WEIGHTS):
            raise RuntimeError(f"a code with k > 0 not of weights {WEIGHTS}: {A}, {B}")
    canon = canonical(codes, ell, m, allow_isomorphic) if codes else []
    groups: dict[tuple, list[int]] = {}
    for i, (key, _, _) in zip(keep.tolist(), canon, strict=True):
        groups.setdefault(key, []).append(i)
    by_index = {int(i): c for i, c in zip(keep.tolist(), canon, strict=True)}
    out = []
    for key, members in groups.items():
        ks = {int(k[i]) for i in members}
        rep = min(members)
        A, B = polynomials(params[rep])
        _, fixes, swaps = by_index[rep]
        out.append({"key": [list(map(list, P)) for P in key], "rep": rep,
                    "params": params[rep].tolist(), "A": A, "B": B, "size": len(members),
                    "k": int(k[rep]), "k_constant": len(ks) == 1, "fixes": fixes,
                    "swaps": swaps})  # fmt: skip
    out.sort(key=lambda c: (-c["k"], c["rep"]))
    for i, c in enumerate(out):
        c["class"] = i
    raw_by_k = Counter(k.tolist())
    return {"l": ell, "m": m, "n": 2 * ell * m, "raw_codes": len(k),
            "raw_k_positive": int(len(keep)),
            "raw_by_k": {str(a): raw_by_k[a] for a in sorted(raw_by_k)},
            "classes_by_k": {str(a): b for a, b in sorted(Counter(c["k"] for c in out).items())},
            "k_seconds": round(k_seconds, 3), "seconds": round(time.time() - start, 3),
            "classes": out}  # fmt: skip


def orbit_partition(ell: int, m: int, codes, allow_isomorphic: bool = False) -> list[set]:
    """The orbits, among `codes` (raw parameter tuples), of the group of monomial factors on A
    and on B, swapping A and B, and automorphisms of the torus, by applying its elements: for
    every code, automorphism φ and swap s, every pair of translations (g, h) whose image
    (g φ(A), h φ(B)), swapped by s, is a code of the list joins the two (union-find). The
    translations are tried for A and for B apart and paired when both land on a polynomial of
    the list, which skips no image in the list. For the tests, at small tori: it shares with
    `classes` only the automorphisms and the reduction of exponents."""
    guard(ell, m, allow_isomorphic)
    auts = automorphisms(ell, m, allow_isomorphic)
    pairs = {}
    for t in codes:
        A, B = polynomials(t)
        pairs[(frozenset(map(tuple, retest._reduce(A, ell, m))),
               frozenset(map(tuple, retest._reduce(B, ell, m))))] = tuple(t)  # fmt: skip
    parent = {t: t for t in pairs.values()}

    def find(t):
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    lefts = {P for P, _ in pairs} | {Q for _, Q in pairs}
    shifts = [(g0, g1) for g0 in range(ell) for g1 in range(m)]
    for (A, B), t in pairs.items():
        for f in auts:
            fa, fb = (frozenset(retest._mapped(P, f, ell, m)) for P in (A, B))
            ga = [s for s in (frozenset(((p + g0) % ell, (q + g1) % m) for p, q in fa)
                              for g0, g1 in shifts) if s in lefts]  # fmt: skip
            hb = [s for s in (frozenset(((p + g0) % ell, (q + g1) % m) for p, q in fb)
                              for g0, g1 in shifts) if s in lefts]  # fmt: skip
            for x in ga:
                for y in hb:
                    for image in ((x, y), (y, x)):
                        if image in pairs:
                            parent[find(pairs[image])] = find(t)
    blocks: dict[tuple, set] = {}
    for t in parent:
        blocks.setdefault(find(t), set()).add(t)
    return list(blocks.values())


# ---------------------------------------------------------------- structure


def _odd(n: int) -> int:
    return bb.two_part(n)[1]


def frobenius_orbits(terms, ell: int, m: int, allow_isomorphic: bool = False) -> list[dict]:
    """The Frobenius orbits (χ -> χ^2) of the characters with a nonzero local term: each with
    its size, its term (the same at every character of an orbit) and its least character."""
    guard(ell, m, allow_isomorphic)
    lo, mo = _odd(ell), _odd(m)
    term = {tuple(c): t for c, t in terms}
    seen, out = set(), []
    for c in sorted(term):
        if c in seen:
            continue
        orbit, x = [], c
        while x not in orbit:
            orbit.append(x)
            x = ((2 * x[0]) % lo, (2 * x[1]) % mo)
        seen |= set(orbit)
        values = {term.get(y) for y in orbit}
        out.append({"size": len(orbit), "term": term[c] if len(values) == 1 else None,
                    "first": list(c)})  # fmt: skip
    return out


def dilations(A, B, ell: int, m: int, allow_isomorphic: bool = False) -> dict:
    """The dilations (x, y) -> (x^u, y^u), 1 < u < lcm(l, m) with u prime to l and m, under
    which A ~ A and B ~ B (fixing) or A ~ B and B ~ A (swapping), ~ up to a monomial factor."""
    guard(ell, m, allow_isomorphic)
    N = math.lcm(ell, m)
    norm = functools.partial(retest._translates, ell=ell, m=m)
    ta, tb = norm(retest._reduce(A, ell, m)), norm(retest._reduce(B, ell, m))
    fixing, swapping = [], []
    for u in range(2, N):
        if math.gcd(u, ell) != 1 or math.gcd(u, m) != 1:
            continue
        f = ((u % ell, 0), (0, u % m))
        ua = norm(retest._mapped(retest._reduce(A, ell, m), f, ell, m))
        ub = norm(retest._mapped(retest._reduce(B, ell, m), f, ell, m))
        if (ua, ub) == (ta, tb):
            fixing.append(u)
        if (ua, ub) == (tb, ta):
            swapping.append(u)
    return {"fixing": fixing, "swapping": swapping}


def structure(c: dict, ell: int, m: int, group_order: int, allow_isomorphic: bool = False) -> dict:
    """The structure recorded for a class (module docstring)."""
    guard(ell, m, allow_isomorphic)
    A, B, iso = c["A"], c["B"], allow_isomorphic
    terms = bb.local_terms(A, B, ell, m)
    sa, sb = (_translation_stabilizer(P, ell, m, iso) for P in (A, B))
    stabilizer = (c["fixes"] + c["swaps"]) * sa * sb
    return {"characters": [[j, kk, t] for (j, kk), t in terms],
            "k_characters": 2 * sum(t for _, t in terms),
            "frobenius_orbits": frobenius_orbits(terms, ell, m, iso),
            "weights": [len(retest._reduce(P, ell, m)) for P in (A, B)],
            "aut_fixing": c["fixes"], "aut_swapping": c["swaps"],
            "translation_stabilizers": [sa, sb], "stabilizer": stabilizer,
            "orbit_size": group_order // stabilizer,
            "dilations": dilations(A, B, ell, m, iso)}  # fmt: skip


# ---------------------------------------------------------------- distances


def _verified(A, B, ell: int, m: int, witness, kind: str = "Z",
              allow_isomorphic: bool = False) -> bool | None:  # fmt: skip
    guard(ell, m, allow_isomorphic)
    if not witness:
        return None
    return bool(distance.verify_witness(A, B, ell, m, kind, witness)["logical"])


def class_distance(A, B, ell: int, m: int, limit: float, allow_isomorphic: bool = False,
                   kind: str = "Z", every_qubit: bool = False) -> dict:  # fmt: skip
    """distance_search, deepening, with its witness checked: by default of kind Z from (0, lm);
    `recheck` uses kind X from every qubit."""
    guard(ell, m, allow_isomorphic)
    anchors = None if every_qubit else (0, ell * m)
    r = distance.distance_search(A, B, ell, m, kind, anchors=anchors, time_limit=limit,
                                 deepen=True)  # fmt: skip
    return {"status": r["status"], "d": r["d"], "lower": r["lower"], "upper": r["upper"],
            "witness": r["witness"],
            "verified": _verified(A, B, ell, m, r["witness"], kind, allow_isomorphic),
            "k": r["k"], "nodes": r["nodes"], "passes": len(r["passes"]), "kind": kind,
            "anchors": r["anchors"], "seconds": r["seconds"]}  # fmt: skip


def recheck(A, B, ell: int, m: int, limit: float, allow_isomorphic: bool = False) -> dict:
    """The second search (module docstring): kind X, from every qubit."""
    return class_distance(A, B, ell, m, limit, allow_isomorphic, kind="X", every_qubit=True)


def program_distance(A, B, ell: int, m: int, limit: float, allow_isomorphic: bool = False) -> dict:
    """distance_ilp of kind Z under SCIP_FIX, with its witness checked."""
    guard(ell, m, allow_isomorphic)
    r = distance.distance_ilp(A, B, ell, m, "Z", time_limit=limit)
    return {"status": r["status"], "d": r["d"], "lower": r["lower"], "upper": r["upper"],
            "witness": r["witness"],
            "verified": _verified(A, B, ell, m, r["witness"], "Z", allow_isomorphic),
            "k": r["k"], "nodes": r["nodes"], "scip_fix": r["scip_fix"], "seed": r["seed"],
            "seconds": r["seconds"]}  # fmt: skip


def _failed(exc: Exception) -> dict:
    """An instrument's row when it raised: no bounds, and a problem in the class's row."""
    return {"status": "error", "error": f"{type(exc).__name__}: {exc}"[:2000], "d": None,
            "lower": None, "upper": None, "witness": None, "verified": None, "k": None}  # fmt: skip


def interval(r: dict) -> tuple[int, float]:
    """An instrument's interval: [lower (1 if none: a logical is nonzero), the weight of its
    witness if the witness passes verify_witness (unbounded otherwise)]."""
    lower = r.get("lower") or 1
    upper = r["upper"] if r.get("verified") and r.get("upper") is not None else math.inf
    return lower, upper


def compare(first: dict, second: dict) -> str:
    """The outcome of two instruments (the search and the program, or the two searches): "agree"
    (both exact, a search complete or a program optimal, with equal d and both witnesses passing
    verify_witness), "consistent" (the intervals meet, otherwise), or "disagree" (they do not
    meet)."""
    (a, b), (c, d) = interval(first), interval(second)
    if max(a, c) > min(b, d):
        return "disagree"
    exact = all(r["status"] in ("complete", "optimal") and r.get("verified") is True
                for r in (first, second))  # fmt: skip
    if exact and first["d"] is not None and first["d"] == second["d"]:
        return "agree"
    return "consistent"


def score(k: int, d, n: int) -> float | None:
    return None if d is None else k * d * d / n


def ilp_selection(rows: list[dict], ell: int, m: int, fraction: float) -> dict[int, str]:
    """The classes the program cross-checks, by class index, with the reason: "best" (exact d
    giving the torus's best k d^2 / n, ties included), "timelimit" (the search stopped; "search
    error" if it raised), or "sample" (`fraction` of the rest rounded up, at least one if any
    remain)."""
    n = 2 * ell * m
    searched = [r for r in rows if r.get("search")]
    scores = {r["class"]: score(r["k"], r["search"]["d"], n) for r in searched}
    best = max((s for s in scores.values() if s is not None), default=None)
    out = {}
    for r in searched:
        if best is not None and scores[r["class"]] == best:
            out[r["class"]] = "best"
        elif r["search"]["status"] != "complete":
            status = r["search"]["status"]
            out[r["class"]] = "timelimit" if status == "timelimit" else f"search {status}"
    rest = sorted(r["class"] for r in searched if r["class"] not in out)
    if rest:
        rng = random.Random(SAMPLE_SEED.format(l=ell, m=m))
        for i in rng.sample(rest, max(1, math.ceil(fraction * len(rest)))):
            out[i] = "sample"
    return out


# ---------------------------------------------------------------- one torus


def _usage() -> dict:
    own = resource.getrusage(resource.RUSAGE_SELF)
    kids = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = own.ru_utime + own.ru_stime + kids.ru_utime + kids.ru_stime
    return {"cpu_seconds": round(cpu, 1), "load": [round(x, 2) for x in os.getloadavg()]}


def provenance() -> dict:
    """What a file's results rest on: versions, sha256s, seeds."""
    compiler = subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout
    return {"solver": distance.scip_version(), "scip_fix": distance.SCIP_FIX,
            "scip_seed": distance.SEED, "memory_mb": distance.MEMORY_MB,
            "search_c_sha256": _sha256(distance.SEARCH_C), "census_c_sha256": _sha256(CENSUS_C),
            "census_py_sha256": _sha256(Path(__file__)), "holdout_sha256": _sha256(HOLDOUT),
            "distance_py_sha256": _sha256(Path(distance.__file__)),
            "compiler": compiler.splitlines()[0] if compiler else "cc",
            "python": platform.python_version(), "numpy": np.__version__}  # fmt: skip


def census_torus(ell: int, m: int, options: Options = DEFAULTS, log=None) -> list[dict]:
    """The census of one torus: its header and one row per class (module docstring)."""
    iso = options.allow_isomorphic
    guard(ell, m, iso)
    start = time.time()
    say = log or (lambda text: None)
    n = 2 * ell * m
    found = classes(ell, m, iso)
    auts = len(automorphisms(ell, m, iso))
    group_order = auts * (ell * m) ** 2 * 2
    say(f"{ell}x{m}: {found['raw_k_positive']} of {found['raw_codes']} raw codes with k > 0, "
        f"{len(found['classes'])} classes")  # fmt: skip
    stages = {"classes": time.time() - start, "structure": 0.0, "search": 0.0, "program": 0.0,
              "recheck": 0.0}  # fmt: skip
    rows = []
    for c in found["classes"]:
        began = time.time()
        row = {"type": "class", "l": ell, "m": m, "n": n,
               **{key: c[key] for key in ("class", "rep", "params", "A", "B", "key", "size", "k",
                                          "k_constant")},
               **structure(c, ell, m, group_order, iso)}  # fmt: skip
        stages["structure"] += time.time() - began
        began = time.time()
        if c["k"] >= options.distance_kmin:
            try:
                row["search"] = class_distance(c["A"], c["B"], ell, m, options.search_limit, iso)
            except Exception as exc:  # recorded as a problem; the torus goes on
                row["search"] = _failed(exc)
        else:
            row["search"] = None
        stages["search"] += time.time() - began
        rows.append(row)
    say(f"{ell}x{m}: searches done in {time.time() - start:.0f} s")
    chosen = ilp_selection(rows, ell, m, options.sample)
    for row in rows:
        row["program"] = row["crosscheck"] = row["recheck"] = None
        if row["class"] in chosen:
            began = time.time()
            try:
                p = program_distance(row["A"], row["B"], ell, m, options.ilp_limit, iso)
            except Exception as exc:  # recorded as a problem; the torus goes on
                p = _failed(exc)
            stages["program"] += time.time() - began
            row["program"] = {**p, "reason": chosen[row["class"]]}
            row["crosscheck"] = compare(row["search"], p)
            why, bounds = chosen[row["class"]], f"[{p['lower']}, {p['upper']}]"
            say(f"{ell}x{m}: class {row['class']} ({why}): program {p['status']} {bounds} "
                f"in {p.get('seconds', 0):.0f} s, {row['crosscheck']}")  # fmt: skip
        if chosen.get(row["class"]) == "best" and row["crosscheck"] != "agree":
            began = time.time()
            try:
                r = recheck(row["A"], row["B"], ell, m, options.search_limit, iso)
            except Exception as exc:  # recorded as a problem; the torus goes on
                r = _failed(exc)
            stages["recheck"] += time.time() - began
            row["recheck"] = {**r, "outcome": compare(row["search"], r)}
            say(f"{ell}x{m}: class {row['class']}: second search {r['status']} "
                f"[{r['lower']}, {r['upper']}], {row['recheck']['outcome']}")  # fmt: skip
    flags = []
    for row in rows:
        problems = []
        if not row["k_constant"]:
            problems.append("k differs within the class")
        if row["k_characters"] != row["k"]:
            problems.append(f"k_characters {row['k_characters']} != k {row['k']}")
        for name in ("search", "program", "recheck"):
            r = row.get(name)
            if r and r.get("status") == "error":
                problems.append(f"{name} failed: {r['error']}")
                continue
            if r and r.get("k") != row["k"]:
                problems.append(f"{name} found {r.get('k')} logicals, k = {row['k']}")
            if r and r.get("verified") is False:
                problems.append(f"{name}'s witness fails verify_witness")
        if row["crosscheck"] == "disagree":
            problems.append(f"DISAGREEMENT: search {interval(row['search'])}, program "
                            f"{interval(row['program'])}")  # fmt: skip
        if row["recheck"] and row["recheck"]["outcome"] == "disagree":
            problems.append(f"DISAGREEMENT: search {interval(row['search'])}, second search "
                            f"{interval(row['recheck'])}")  # fmt: skip
        row["problems"] = problems
        if problems:
            flags.append((row["class"], problems))
            print(f"census {ell}x{m} class {row['class']}: {'; '.join(problems)}", file=sys.stderr)
    lo, mo = _odd(ell), _odd(m)
    header = {"type": "header", "l": ell, "m": m, "n": n,
              "torus_type": list(distance.torus_type(ell, m)),
              "two_part": [bb.two_part(ell)[0], bb.two_part(m)[0]], "odd_part": [lo, mo],
              "automorphisms": auts, "group_order": group_order,
              "isomorphic_held_out": [list(t) for t in isomorphic_held_out(ell, m)],
              **{key: found[key] for key in ("raw_codes", "raw_k_positive", "raw_by_k",
                                             "classes_by_k", "k_seconds")},
              "classes": len(rows), "options": options.as_dict(),
              "limits": {"search_seconds": options.search_limit,
                         "ilp_seconds": options.ilp_limit},
              "seeds": {"scip": distance.SEED, "sample": SAMPLE_SEED.format(l=ell, m=m)},
              "search": {"kind": "Z", "deepen": True, "anchors": [0, ell * m]},
              "crosschecks": dict(Counter(r["crosscheck"] for r in rows if r["crosscheck"])),
              "rechecks": dict(Counter(r["recheck"]["outcome"] for r in rows if r["recheck"])),
              "problems": len(flags), **provenance(),
              "stage_seconds": {key: round(v, 1) for key, v in stages.items()},
              "programs": len(chosen), "seconds": round(time.time() - start, 1),
              **_usage()}  # fmt: skip
    return [header, *rows]


def torus_file(data: Path, ell: int, m: int) -> Path:
    return Path(data) / f"{ell}x{m}.jsonl"


def write_torus(data: Path, lines: list[dict]) -> Path:
    """Write a torus's lines to data/LxM.jsonl by way of a temporary file and a rename."""
    header = lines[0]
    path = torus_file(data, header["l"], header["m"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w") as out:
        for line in lines:
            out.write(json.dumps(line, sort_keys=True, separators=(",", ":")) + "\n")
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp, path)
    return path


def read_torus(path: Path) -> tuple[dict, list[dict]]:
    lines = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    if not lines or lines[0].get("type") != "header":
        raise ValueError(f"{path} has no header line")
    return lines[0], lines[1:]


# ---------------------------------------------------------------- the run


# The tori that took longest in development (minutes at the default options, the module
# docstring's estimate), which `run` starts first. The order changes no result.
COSTLY = ((6, 15), (3, 33), (3, 30), (7, 14), (3, 27), (9, 10), (5, 18), (3, 24))


def run_order(tori: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """`tori` with the COSTLY ones first, in that order, then the rest in their given order."""
    first = [t for t in COSTLY if t in tori]
    return first + [t for t in tori if t not in first]


def _worker_command(ell: int, m: int, data: Path, options: Options) -> list[str]:
    python = str(PYTHON) if PYTHON.exists() else sys.executable
    args = [python, str(Path(__file__)), "torus", str(ell), str(m), "--data", str(data),
            "--search-limit", str(options.search_limit), "--ilp-limit", str(options.ilp_limit),
            "--sample", str(options.sample), "--distance-kmin", str(options.distance_kmin),
            "--parent", str(os.getpid())]  # fmt: skip
    return args + (["--allow-isomorphic"] if options.allow_isomorphic else [])


def _computed_as(options: dict) -> dict:
    """The options that bear on how a torus is computed: all but allow_isomorphic, which only
    says which tori run."""
    return {key: v for key, v in options.items() if key != "allow_isomorphic"}


def run(data: Path, workers: int, options: Options) -> None:
    """Every census torus without a file in `data`, in run_order, one worker process per torus,
    `workers` at a time. Refuses to resume over files made under other options (allow_isomorphic
    apart). A relative `data` is taken from the working directory."""
    data = Path(data).resolve()
    todo = []
    current = provenance()
    hashes = ("census_py_sha256", "census_c_sha256", "search_c_sha256", "distance_py_sha256")
    for ell, m in run_order(census_tori(options.allow_isomorphic)):
        path = torus_file(data, ell, m)
        if path.exists():
            header, _ = read_torus(path)
            if _computed_as(header["options"]) != _computed_as(options.as_dict()):
                raise SystemExit(
                    f"{path} was made with options {header['options']}, not "
                    f"{options.as_dict()}: move it or rerun with those options"
                )
            changed = [key for key in hashes if header.get(key) != current[key]]
            if changed:
                print(f"warning: {path} was made by other code ({', '.join(changed)})", flush=True)
            continue
        todo.append((ell, m))
    print(f"{len(todo)} tori to run, {len(census_tori(options.allow_isomorphic)) - len(todo)} "
          f"done; options {options.as_dict()}", flush=True)  # fmt: skip
    start = time.time()

    def one(t):
        ell, m = t
        began = time.time()
        proc = subprocess.run(_worker_command(ell, m, data, options), cwd=HERE)
        return t, proc.returncode, time.time() - began

    failed = []
    with ThreadPoolExecutor(max(1, workers)) as pool:
        for future in as_completed([pool.submit(one, t) for t in todo]):
            (ell, m), code, seconds = future.result()
            ok = code == 0 and torus_file(data, ell, m).exists()
            if not ok:
                failed.append((ell, m))
            print(f"{ell}x{m} {'done' if ok else f'FAILED (exit {code})'} in {seconds:.0f} s "
                  f"({time.time() - start:.0f} s into the run)", flush=True)  # fmt: skip
    if failed:
        raise SystemExit(f"failed tori: {failed}")


def _worker(args) -> None:
    if args.parent and sys.platform == "linux":
        import ctypes
        import signal

        ctypes.CDLL(None).prctl(1, signal.SIGKILL)  # PR_SET_PDEATHSIG: die with the run
        if os.getppid() != args.parent:
            sys.exit("the run's process is gone")
    options = _options(args)
    lines = census_torus(args.l, args.m, options,
                         log=lambda text: print(text, file=sys.stderr, flush=True))  # fmt: skip
    write_torus(Path(args.data), lines)


# ---------------------------------------------------------------- the summary


def _transposed(P) -> list[list[int]]:
    return [[q, p] for p, q in P]


def published_codes() -> list[dict]:
    """The published entries (../qec-bb/codes.json), in the l <= m orientation (exchanging x
    and y transposes the exponents; the code is equivalent)."""
    out = []
    for c in json.loads(PUBLISHED.read_text())["codes"]:
        A = c.get("A") or bb.pi_poly(c["pi_A"])
        B = c.get("B") or bb.pi_poly(c["pi_B"])
        ell, m = c["l"], c["m"]
        if ell > m:
            A, B, ell, m = _transposed(A), _transposed(B), m, ell
        out.append({"name": c["name"], "l": ell, "m": m, "A": [list(u) for u in A],
                    "B": [list(u) for u in B], "n": c["n"], "k": c["k"], "d": c["d"]})  # fmt: skip
    return out


_ERRORS = tuple(f"{name} failed: " for name in ("search", "program", "recheck"))


def _doubtful(row: dict) -> bool:
    """A row the frontier leaves out: one with a problem other than an instrument that raised
    (a disagreement, a witness that fails verify_witness, or a k at odds)."""
    return any(not p.startswith(_ERRORS) for p in row.get("problems") or [])


def bounds(row: dict) -> tuple[int, float]:
    """The intersection of the intervals of the search and the program, those that ran without
    error ([1, unbounded] if neither did)."""
    ivs = [interval(row[name]) for name in ("search", "program")
           if row.get(name) and row[name].get("status") != "error"]  # fmt: skip
    return max((a for a, _ in ivs), default=1), min((b for _, b in ivs), default=math.inf)


def established(row: dict) -> tuple[int | None, str | None]:
    """(d, what gives it) where `bounds` is a single point: "search" or "program" when that
    instrument's own interval is the point, "search, program" when both are, and "bounds" when
    only their intersection is. (None, None) otherwise, and for a doubtful row."""
    lower, upper = bounds(row)
    if _doubtful(row) or lower != upper:
        return None, None
    ran = [name for name in ("search", "program")
           if row.get(name) and row[name].get("status") != "error"]  # fmt: skip
    alone = [name for name in ran if interval(row[name]) == (lower, upper)]
    return lower, ", ".join(alone) or "bounds"


def _d(row: dict):
    return established(row)[0]


def _evidence(row: dict) -> dict:
    """What a frontier entry's d rests on (module docstring)."""
    p, s, r = row.get("program"), row.get("search"), row.get("recheck")
    return {"d_by": established(row)[1], "crosscheck": row.get("crosscheck"),
            "program": [p.get("lower"), p.get("upper")] if p else None,
            "search_verified": s.get("verified") if s else None,
            "recheck": r["outcome"] if r else None}  # fmt: skip


def _ranked(rows: list[dict], among: list[dict] | None = None) -> dict[tuple, int]:
    """Rank by k d^2 / n among rows with established d: 1 + the number of rows of `among`
    (default: `rows`) with a strictly larger score."""

    def scored(group):
        out = [(score(r["k"], _d(r), r["n"]), (r["l"], r["m"], r["class"])) for r in group]
        return [(s, key) for s, key in out if s is not None]

    pool = [s for s, _ in scored(rows if among is None else among)]
    return {key: 1 + sum(t > s for t in pool) for s, key in scored(rows)}


def _row_key(r: dict) -> tuple:
    return tuple(tuple(tuple(u) for u in P) for P in r["key"])


def cross_torus(tori: list[dict], rows: list[dict]) -> tuple[list[dict], dict]:
    """Classes equivalent across isomorphic tori (the census keeps each torus apart, so a code
    can appear on two tori of one type): for each type with more than one torus in the data,
    every class's key carried onto the least of them (qec-distance-2's _carried_key). Returns
    one entry per type (its tori, the classes on each, the distinct classes among them) and, for
    each class with an equivalent on another torus, those equivalents."""
    by_type: dict[tuple, list] = {}
    for h in tori:
        guard(h["l"], h["m"], allow_isomorphic=True)
        by_type.setdefault(distance.torus_type(h["l"], h["m"]), []).append((h["l"], h["m"]))
    groups, same = [], {}
    for kind, ts in sorted(by_type.items()):
        ts = sorted(ts)
        if len(ts) < 2:
            continue
        ref, carried = ts[0], {}
        for r in rows:
            t = (r["l"], r["m"])
            if t not in ts:
                continue
            key = _row_key(r) if t == ref else retest._carried_key(r["A"], r["B"], t, ref)
            carried.setdefault(key, []).append((r["l"], r["m"], r["class"]))
        for members in carried.values():
            for x in members:
                others = [list(y) for y in members if y[:2] != x[:2]]
                if others:
                    same[x] = others
        counts = Counter((r["l"], r["m"]) for r in rows if (r["l"], r["m"]) in ts)
        shared = sum(len({y[:2] for y in v}) > 1 for v in carried.values())
        groups.append({"type": list(kind), "tori": [list(t) for t in ts],
                       "classes": {f"{a}x{b}": counts[(a, b)] for a, b in ts},
                       "distinct": len(carried), "shared": shared})  # fmt: skip
    return groups, same


def summarize(data: Path) -> dict:
    """summary.json's content from the files in `data`: per torus counts, the frontier at each
    n, the cross-checks (disagreements and failed witnesses first), and the published codes."""
    tori, rows = [], []
    for path in sorted(Path(data).glob("*x*.jsonl")):
        header, lines = read_torus(path)
        guard(header["l"], header["m"], allow_isomorphic=True)  # before its rows are used
        if any((r["l"], r["m"]) != (header["l"], header["m"]) for r in lines):
            raise ValueError(f"{path} holds rows of another torus than its header's")
        tori.append(header)
        rows += lines
    problems = [{"l": r["l"], "m": r["m"], "class": r["class"], "problems": r["problems"]}
                for r in rows if r.get("problems")]  # fmt: skip
    disagreements = [p for p in problems if any("DISAGREEMENT" in x for x in p["problems"])]
    by_n: dict[int, list[dict]] = {}
    for r in rows:
        by_n.setdefault(r["n"], []).append(r)
    isomorphic, same = cross_torus(tori, rows)
    frontier, distinct_at = [], {}
    for n in sorted(by_n):
        group = by_n[n]
        exact = [r for r in group if _d(r) is not None]
        best_score = max((score(r["k"], _d(r), n) for r in exact), default=None)
        best = [r for r in exact if score(r["k"], _d(r), n) == best_score]
        open_ = []
        for r in group:
            if r.get("search") is None or _d(r) is not None or _doubtful(r):
                continue
            lower, upper = bounds(r)
            if best_score is None or upper == math.inf or score(r["k"], upper, n) > best_score:
                open_.append({"l": r["l"], "m": r["m"], "class": r["class"], "k": r["k"],
                              "lower": lower,
                              "upper": None if upper == math.inf else upper})  # fmt: skip
        per_k = {}
        for r in exact:
            d = _d(r)
            cur = per_k.get(r["k"])
            if cur is None or d > cur["d"]:
                per_k[r["k"]] = {"d": d, "codes": []}
            if per_k[r["k"]]["d"] == d:
                per_k[r["k"]]["codes"].append({"l": r["l"], "m": r["m"], "class": r["class"],
                                               **_evidence(r)})  # fmt: skip
        unsearched = sum(1 for r in group if r.get("search") is None)
        # a class with an equivalent on a torus earlier in (l, m) order is not counted again
        ids = [(r["l"], r["m"], r["class"]) for r in group]
        distinct_at[n] = [r for r, x in zip(group, ids, strict=True)
                          if not any(tuple(y) < x for y in same.get(x, []))]  # fmt: skip
        frontier.append({
            "n": n, "classes": len(group), "distinct": len(distinct_at[n]),
            "exact": len(exact), "unsearched": unsearched,
            "best": [{"l": r["l"], "m": r["m"], "class": r["class"], "k": r["k"], "d": _d(r),
                      "score": round(best_score, 4), "A": r["A"], "B": r["B"], **_evidence(r),
                      "same_as": same.get((r["l"], r["m"], r["class"]), [])} for r in best],
            "best_d_by_k": {str(k): per_k[k] for k in sorted(per_k)},
            "open": open_,
            "excluded": [[r["l"], r["m"], r["class"]] for r in group if _doubtful(r)],
        })  # fmt: skip
    ranks_n = {}
    for n, group in by_n.items():
        ranks_n.update(_ranked(group, distinct_at[n]))
    placed = []
    index = {(r["l"], r["m"], _row_key(r)): r for r in rows}
    done = {(h["l"], h["m"]) for h in tori}
    for c in published_codes():
        entry = {"name": c["name"], "l": c["l"], "m": c["m"], "published": [c["n"], c["k"], c["d"]]}
        try:
            guard(c["l"], c["m"], allow_isomorphic=True)
        except HeldOut as exc:
            placed.append({**entry, "status": f"not placed: {exc}"})
            continue
        if (c["l"], c["m"]) not in done:
            placed.append({**entry, "status": "torus not in the data"})
            continue
        key = retest.equivalence_key(c["A"], c["B"], c["l"], c["m"])
        r = index.get((c["l"], c["m"], key))
        if r is None:
            placed.append({**entry, "status": "not in the census (not of the family's form up "
                                               "to equivalence, or k = 0)"})  # fmt: skip
            continue
        same_torus = [x for x in rows if (x["l"], x["m"]) == (c["l"], c["m"])]
        rank_t = _ranked(same_torus).get((r["l"], r["m"], r["class"]))
        placed.append({**entry, "status": "in the census", "class": r["class"], "k": r["k"],
                       "d": _d(r), "d_by": established(r)[1], "size": r["size"],
                       "rank_at_n": ranks_n.get((r["l"], r["m"], r["class"])),
                       "classes_at_n": len(distinct_at[r["n"]]), "rank_in_torus": rank_t,
                       "classes_in_torus": len(same_torus)})  # fmt: skip
    crosschecks = Counter(r["crosscheck"] for r in rows if r.get("crosscheck"))
    rechecks = Counter(r["recheck"]["outcome"] for r in rows if r.get("recheck"))
    reasons = Counter(r["program"]["reason"] for r in rows if r.get("program"))
    statuses = Counter(r["search"]["status"] for r in rows if r.get("search"))
    refused = [list(t) for t in stage1_tori() if isomorphic_held_out(*t)]
    return {
        "note": "Stage 1 of the census (census.py's docstring): exploratory, not registered.",
        "problems": problems, "disagreements": disagreements,
        "tori": [{key: h[key] for key in ("l", "m", "n", "raw_codes", "raw_k_positive",
                                          "classes", "classes_by_k", "crosschecks", "problems",
                                          "seconds", "options", "isomorphic_held_out")}
                 for h in tori],
        "tori_done": len(tori), "stage1_tori": len(stage1_tori()),
        "isomorphic_to_held_out": refused,
        "classes": len(rows), "isomorphic_tori": isomorphic,
        "search_statuses": dict(statuses),
        "crosschecks": dict(crosschecks), "crosscheck_reasons": dict(reasons),
        "rechecks": dict(rechecks), "frontier": frontier, "published": placed,
    }  # fmt: skip


def print_summary(s: dict, out=sys.stdout) -> None:
    say = functools.partial(print, file=out)
    if s["disagreements"]:
        say("!!! DISAGREEMENTS between the instruments (search, program, second search):")
        for p in s["disagreements"]:
            say(f"!!!   {p['l']}x{p['m']} class {p['class']}: {'; '.join(p['problems'])}")
    other = [p for p in s["problems"] if p not in s["disagreements"]]
    if other:
        say("!!! Other problems:")
        for p in other:
            say(f"!!!   {p['l']}x{p['m']} class {p['class']}: {'; '.join(p['problems'])}")
    say(f"{s['tori_done']} of {s['stage1_tori']} stage-1 tori done; {s['classes']} classes; "
        f"searches {s['search_statuses']}; cross-checks {s['crosschecks']} "
        f"({s['crosscheck_reasons']}); second searches {s['rechecks']}")  # fmt: skip
    say("n     classes  best [[n, k, d]] by k d^2/n (torus#class)    best d for each k")
    say("      (classes/distinct: codes equivalent across isomorphic tori counted once; * no")
    say("      agreement, so d rests on one instrument: summary.json's d_by, bounds, recheck)")
    for f in s["frontier"]:
        mark = {True: "", False: "*"}
        best = ", ".join(f"[[{f['n']},{b['k']},{b['d']}]]{mark[b['crosscheck'] == 'agree']} "
                         f"{b['l']}x{b['m']}#{b['class']}"
                         for b in f["best"][:3]) or "-"  # fmt: skip
        if len(f["best"]) > 3:
            best += f" (+{len(f['best']) - 3} ties)"
        per_k = " ".join(f"k{k}:d{v['d']}" for k, v in f["best_d_by_k"].items())
        extra = f"  open {len(f['open'])}" if f["open"] else ""
        extra += f"  excluded {len(f['excluded'])}" if f["excluded"] else ""
        classes = f"{f['classes']}" + (f"/{f['distinct']}" if f["distinct"] != f["classes"] else "")
        say(f"{f['n']:<5} {classes:<8} {best:<44} {per_k}{extra}")
    say("Published codes:")
    for p in s["published"]:
        where = p["status"]
        if p["status"] == "in the census":
            where += (f": class {p['class']}, [[{2 * p['l'] * p['m']},{p['k']},{p['d']}]], rank "
                      f"{p['rank_at_n']} of {p['classes_at_n']} at its n, {p['rank_in_torus']} "
                      f"of {p['classes_in_torus']} on its torus")  # fmt: skip
        say(f"  {p['name']} ({p['l']}x{p['m']}): {where}")


# ---------------------------------------------------------------- command line


def _options(args) -> Options:
    return Options(
        search_limit=args.search_limit,
        ilp_limit=args.ilp_limit,
        sample=args.sample,
        distance_kmin=args.distance_kmin,
        allow_isomorphic=args.allow_isomorphic,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Census of bivariate bicycle codes, stage 1")
    sub = parser.add_subparsers(dest="step", required=True)
    defaults = DEFAULTS

    def limits(p):
        p.add_argument("--data", default=str(DATA))
        p.add_argument("--search-limit", type=float, default=defaults.search_limit)
        p.add_argument("--ilp-limit", type=float, default=defaults.ilp_limit)
        p.add_argument("--sample", type=float, default=defaults.sample)
        p.add_argument("--distance-kmin", type=int, default=defaults.distance_kmin)
        p.add_argument("--allow-isomorphic", action="store_true")

    p = sub.add_parser("run", help="every census torus without a file, the largest first")
    limits(p)
    p.add_argument("--workers", type=int, default=2)  # one core each (module docstring)
    p = sub.add_parser("torus", help="one torus (the run's worker)")
    p.add_argument("l", type=int)
    p.add_argument("m", type=int)
    p.add_argument("--parent", type=int, default=0)
    limits(p)
    p = sub.add_parser("classes", help="k and the classes of one torus, no distances")
    p.add_argument("l", type=int)
    p.add_argument("m", type=int)
    p.add_argument("--allow-isomorphic", action="store_true")
    p = sub.add_parser("summary", help="summary.json and the frontier")
    p.add_argument("--data", default=str(DATA))
    p.add_argument("--out", default=str(SUMMARY))
    args = parser.parse_args(argv)
    if args.step == "run":
        run(Path(args.data), args.workers, _options(args))
    elif args.step == "torus":
        _worker(args)
    elif args.step == "classes":
        found = classes(args.l, args.m, args.allow_isomorphic)
        print(json.dumps({key: v for key, v in found.items() if key != "classes"}))
    elif args.step == "summary":
        s = summarize(Path(args.data))
        Path(args.out).write_text(json.dumps(s, indent=1, sort_keys=True) + "\n")
        print_summary(s)


if __name__ == "__main__":
    main()
