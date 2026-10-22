"""
A registered re-test of the two exact distance instruments of examples/qec-distance, as fixed
after its run: the integer program with SCIP's XOR presolving and rapid learning off
(distance.SCIP_FIX), and the search with iterative deepening (distance_search, deepen=True).

    uv run --no-sync python examples/qec-distance-2/study.py register
    uv run --no-sync python examples/qec-distance-2/study.py run --workers 4
    uv run --no-sync python examples/qec-distance-2/study.py resume --workers 4   (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-distance-2

The registered test (examples/qec-distance, docs/code-distances.md) reproduced the 12 published
distances, and two of its method checks found defects. The program, solved by SCIP 10.0,
returned d_X = 3, status optimal, on a 4 x 5 code with d_X = 2: a fault in SCIP's presolving of
XOR constraints, which development then found on 48 more programs (distance_ilp's docstring).
And the search, whose bound started at 64, found no logical in 30 minutes on two codes whose
distances, 4 and 6, the program found at once. distance.py now runs SCIP with SCIP_FIX and the
search by iterative deepening. This test checks both on codes, sizes and seeds that nothing has
touched, and runs the known cases again.

(a) **Against enumeration (registered, decisive).** 25 fresh codes at each size of
    METHOD_SIZES. The test's sizes were reserved by the development rules, and of the eight
    small ones (2x13, 3x10, 4x7, 5x6, 2x14, 3x9, 4x8, 5x8) only 2x13 and 3x9 can hold a code that
    distance_brute enumerates: dim ker H_X = lm + k/2 must be at most distance.BRUTE_CAP (28),
    and k > 0 is even (H_Z = P H_X Φ gives rank H_Z = rank H_X), so lm <= 27. For each code:
    distance_brute of both kinds; the program of both kinds at SCIP seeds 0 to 4; and the search
    of kind Z from every qubit and from (0, lm). The prediction: d_X = d_Z by enumeration, every
    program optimal with k logicals and the enumeration's d, every search complete with k
    logicals and the enumeration's d, and every witness passing verify_witness. The codes
    (`method_codes`) come from five families, one drawn at random for each code: two
    polynomials of 2 to 6 random terms, or of 2 or 3; a common factor (A = f g, B = f h); one
    axis (a monomial times a polynomial in x alone, or in y alone), the family in which
    development found the fault most often; and trinomials of the published form. What this
    covers: n = 52 and 54 only; k = 2 for 38 codes and 4 for 12; at 2x13, 16 factor codes, 5
    random, 3 sparse and 1 one-axis, and at 3x9, 21 random, 3 factor and 1 sparse (the filters
    keep no trinomial). Development found the fault at k = 2 to 22, mostly in one-axis codes,
    so (a) has almost no power against it: SCIP's defaults gave no wrong answer in 5,110 runs of
    (a)'s protocol (seeds 0 to 4, both kinds) on 511 codes from its generator at development
    sizes (k <= 4, 10 of them one-axis). (a) checks the instruments; (f) is the part that can
    see the fault.
(b) **Known faults (a regression, not a prediction).** The 38 codes of fault_cases.json: the
    4 x 5 code of the registered run and the 37 on which development found SCIP's defaults wrong.
    For each, the program of both kinds at seeds 0 to 19 must end optimal with the d that
    distance_brute gives (recorded in the file, and computed again in the job). These answers,
    and the seeds at which the defaults failed, were known before this test was written, and
    the fix was chosen on them: passing shows that the fix is in place, not that it works on
    codes it was not chosen on. That is the job of (a), (c) and (f).
(c) **Program against search (registered, decisive), and the search's completion (registered,
    reported apart).** 2 fresh codes with 4 <= k <= 12, the published entries' range, at each
    size of TRINOMIAL_SIZES (n = 96 to 210), each run through three instruments with a limit of
    PAIR_LIMIT (20 minutes): the program, the search from every qubit (which does not rest on
    the translation argument) and the search from (0, lm). The codes are trinomials
    (`trinomial_codes`): of the published form (A = x^a + y^b + y^c, B = y^d + x^e + x^f) at
    3x28 and 7x15, and of weight 3 (A and B each three distinct monomials, the form of the
    independent checker's w3 codes) at the other sizes, where the published form has no such
    code. Of the eight sizes reserved for this part, the published form has k = 0 at 3x16 and
    4x15 for every choice (the only root of y^16 - 1, or of x^4 - 1, is 1, and A(x, 1) = x^a, or
    B(1, y) = y^d, is a unit), and in 3,000 draws each at 5x13, 7x10, 6x17 and 9x11; weight 3
    had k = 0 at 5x13 in 20,000 draws as well, so 5x13 is left out (k only, no distances). The
    prediction: the three intervals meet, so that no exact value lies outside another
    instrument's bounds and two exact values are equal; every witness passes; each instrument
    finds k logicals and ends exact or at its limit. Whether each instrument completed is
    recorded. Two further predictions make a stall visible: the search from (0, lm) completes,
    with a d, on every one of the 14 codes; and so does the search from every qubit. They are
    reported beside the verdict, not in it: a stall weakens the search, and does not make it
    wrong. A stall weakens (c) as a check on the program too: (c) can show a program fault only
    where a search completes, since an optimum above d (the fault's signature) lies inside the
    intervals of searches that stopped at their limits below it. At 9x11 the codes have the
    form, k and size of the checker's devcodes2 #63 to #65 (weight 3, k = 4), whose distances
    (18, 18 and 12) and search times development saw with the new instruments: those codes are
    excluded, but that form at that size is not unseen.
(d) **Known answers (not blind).** The 12 published entries of ../qec-bb/codes.json, through
    the program and the search from (0, lm), and the two codes on which the search stalled,
    through the program and the search from every qubit and from (0, lm), each instrument with a
    limit of LIMIT (60 minutes). Each entry is classified by examples/qec-distance's rule
    (reproduced, consistent but unresolved, contradicted, method error, not tested) against the
    published d, or, for the two stalled codes, the program's d (4 and 6) in that run. These
    answers are known and the first run's records are public, so this part checks that the fixed
    instruments still give them; it is not blind. A method error or a contradiction here fails
    the instruments: the 12 published d were reproduced by the registered search (and 11 by the
    program), and the stalled codes' d by the deepening search in development, so an interval
    that excludes a known d holds an instrument's wrong value.
(e) **The toric code (registered, decisive).** A = 1 + x, B = 1 + y at the 6 sizes of
    TORIC_SIZES (n = 90 to 510, d = 5 to 15), at none of which anything has run the toric code
    (examples/qec-distance's TORIC_SIZES and excluded_seen, and this test's excluded_seen). The
    program ends optimal with d = min(l, m), a classical theorem, and k = 2; the search, from
    every qubit and from (0, lm), completes with d = min(l, m) and k = 2; every witness passes.
    Each instrument has a limit of LIMIT.
(f) **Power against the fault (registered, decisive).** Fresh codes at each size of POWER_SIZES,
    the six reserved small sizes that (a) cannot enumerate (n = 56 to 80), of high k and
    structured as the codes on which SCIP's defaults failed (`power_codes`): POWER_PER_FAMILY
    (8) codes with k >= POWER_KMIN (4) of each of three families, one axis (as in (a)), A in x
    alone and B in y alone, each times a monomial (`hp`), and a common factor in one variable
    times one to three random terms (`factor1`). That is 142 codes, since one axis gave only 6
    classes with k >= 4 at 4x7 in its draws: 46 one-axis, 48 hp and 48 factor1, k = 4 to 40. The
    families are drawn apart so that one axis, where the fault was found most, is a third of
    them. For each code: the search of both kinds from every qubit, the reference (it rests on
    its argument only; in development the deepening search agreed with the enumeration on all
    6,255 runs of a check); the program of both kinds at the seeds POWER_SEEDS under SCIP_FIX;
    and the same programs under SCIP's defaults (scip_fix=False), the control. The prediction:
    both searches complete with k logicals and d_X = d_Z, and every program under SCIP_FIX is
    optimal with k logicals and the search's d; every witness passes. The control is recorded
    and not judged. A further prediction, reported beside the verdict, says that it is wrong at
    least once (an optimum other than d, a lower bound above it, or a status other than optimal
    or a limit), which shows that (f) can see the fault. In development the defaults were wrong
    on 5 of 100 one-axis programs at n = 66 to 156 (18 of their 600 runs, at 6 seeds), on 2 of
    228 at n <= 50, and on 1 of the 798 hp and factor1 programs, and SCIP_FIX on none; in a
    smoke test of this part's job on 10 development codes of its families at n = 66 and 76, the
    defaults gave 3 for d = 2 on one factor1 code with k = 22, in 28 of its 40 control runs.

**The verdict.** decide reports each part, and a verdict on the instruments: "hold" when (a),
(b), (c) (its intervals), (e) and (f) all pass, no entry of (d) is a method error or
contradicted, and every record was made by the registered protocol; "fail" when any of them
fails (a wrong value, a disagreement, a method error, a contradiction, a failed job, a record
whose code differs from the registration, or one made otherwise than registered); "incomplete"
when jobs are missing and nothing has failed. The completion predictions of (c), the power
prediction of (f) and the classes of (d) are reported beside it.

**The registered protocol.** The predictions carry PROTOCOL, and decide checks every record
against it: its l and m are its job's (or its entry's), a toric record's code is the toric code,
the programs of (a), (b) and (f) ran at the registered seeds, every program ran with SCIP_FIX in
its settings (and (f)'s control without it), and every search deepened, from every qubit or
from (0, lm) as its instrument says.

**An instrument's interval.** As in examples/qec-distance (its study.py, `interval`, reused
here): upper is the checked witness's weight (unbounded when there is none); lower is the
program's dual bound (its optimum when optimal), or the search's d when it completes. One thing
changed with the search: stopped at its limit, it now has a lower bound, the largest bound of a
pass that ended with nothing found (distance_search), where the registered search had none (1).
`interval` reads the record's lower, so its code is unchanged.

**What a result rests on.** As before (distance.py, and examples/qec-distance's study.py): the
program's lower bound on SCIP with SCIP_FIX, on the formulation's soundness and on
logical_basis; the search's on its argument (with the passes), its code, and, from (0, lm), on
the translation argument. Part (a) checks both against enumeration on new codes, at small n
only; part (f) checks the program against the search from every qubit, at n = 56 to 80, on the
codes where the fault lives; part (c) checks them against each other at n = 96 to 210; part (e)
checks both at the published entries' n and d, on a code unlike theirs.

**Fresh codes.** The codes of (a), (c) and (f) come from seeds no earlier step used
(`method_codes`, `trinomial_codes`, `power_codes`, hashed into the question), at sizes where no
development drew a random code. Two of (f)'s sizes, 3x10 and 5x6, are isomorphic tori (Z_30),
so a draw at 5x6 equivalent to one of 3x10's codes is skipped as well. Two kinds of earlier
code do sit at some of these sizes, or on isomorphic tori: the independent checker's
(check-independent/devcodes*.json, at 2x13, 3x9, 4x7, 4x8, 5x6 and 9x11, and at 5x12 and 7x12,
of the types of 4x15 and 3x28), whose distances it computed, and the toric code (which
examples/qec-distance ran at 3x10). A draw equivalent to one of them, or to an earlier draw, up
to monomial factors on A and on B, swapping A and B, and automorphisms of the torus group
(`equivalence_key`), is skipped. Other qubit
permutations are not checked (distance.torus_type); n and k are invariants of every one, and no
size here has the order of a published entry, so no code here is a published one.

**Running it.** As examples/qec-distance: each job (one instrument on one code in (c), (d) and
(e); one size in (a); one code in (b) and (f)) runs in its own worker process, which Linux kills
when the study's process dies, up to --workers at a time, the largest first; its record is
appended when it finishes, and resume skips every job that has a record, a failed one included
(it is then not tested, and is not retried). A study process killed while appending a record
leaves an incomplete last line, which no observation can cite (lattice_lab.ledger.record_lines
reads complete lines only); resume then stops and names it, rather than append after it. The
limits are wall clock, so other load weakens the bounds of whatever stops at one: run it when
nothing else heavy shares the machine.

**Time.** [[288,12,18]]'s program will likely use its whole hour (it stopped at 90 minutes in
the first run, with 13 <= d <= 18), and its search took 3 minutes there. In that run the program
took 15 minutes on the toric code at d = 16, n = 544, and 7.5 minutes at d = 15, n = 480; in
development, under SCIP_FIX, the toric code at 15x16 took 439 s, so part (e) takes about 10
minutes. Part (c)'s codes are new: at n = 162 to 216 the first run's trinomials had d from 4 to
14 and the program took up to 3 minutes, and in development the deepening search took at most
6 minutes, from (0, lm), on trinomials up to d = 20 at n = 288; but at 9x11 the program stopped
at a 15-minute limit on the checker's codes of that form with d = 18, in the first test's
development. Parts (a) and (b) take a few minutes. Part (f)'s job took 1 to 55 s per code in
its smoke test (10 development codes at n = 66 and 76), so (f) is about 40 minutes of work, most
of it in factor1 codes of higher d. With 4 workers the run should take about 1.2 to 1.5 hours,
the length of [[288,12,18]]'s program and what runs beside it. If part (c)'s 42 instrument jobs
all stop at their 20-minute limits (14 hours of work), the run takes about 4 hours: expect one
or two resumes, since a cloud session's background command stops at two hours (TIMEOUT stays
below that), and resume restarts an unfinished job from the beginning.

**Development (excluded_seen in the question)** lists everything computed on these instruments
since examples/qec-distance's registration, by the development of the fixes and of this test.
"""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIRST = HERE.parent / "qec-distance"
sys.path.insert(0, str(HERE.parent / "qec-bb"))
sys.path.insert(0, str(FIRST))

import bb  # noqa: E402
import distance  # noqa: E402

from lattice_lab.ledger import record_lines  # noqa: E402
from lattice_lab.study import Study, StudyError, append_records, main  # noqa: E402

# The registered test, for its rules (interval) and its published entries (codes).
_spec = importlib.util.spec_from_file_location("qec_distance_study", FIRST / "study.py")
first = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(first)

CASES = HERE / "fault_cases.json"
CHECKER = FIRST / "check-independent"
PYTHON = first.PYTHON
LIMIT = 60 * 60  # each instrument on each entry of part (d) and each size of part (e)
PAIR_LIMIT = 20 * 60  # each instrument on each code of part (c)
METHOD_LIMIT = 600  # each program and each search in parts (a) and (b)
GRACE = 15 * 60
TIMEOUT = LIMIT + GRACE  # each job's subprocess

RESERVED_SMALL = [(2, 13), (3, 10), (4, 7), (5, 6), (2, 14), (3, 9), (4, 8), (5, 8)]
# k > 0 is even, so dim ker H_X = lm + k/2 >= lm + 1
METHOD_SIZES = [(ell, m) for ell, m in RESERVED_SMALL if ell * m + 1 <= distance.BRUTE_CAP]
PER_SIZE, MAX_DRAWS = 25, 20000  # fmt: skip
METHOD_SEEDS = list(range(5))
FAULT_SEEDS = list(range(20))
FAMILIES = ("random", "sparse", "factor", "oneaxis", "trinomial")
RESERVED_PAIR = [(3, 16), (4, 15), (5, 13), (7, 10), (3, 28), (6, 17), (7, 15), (9, 11)]
# Part (c)'s form at each size: the published form where it has codes with 4 <= k <= 12, and
# otherwise weight 3; 5x13 has neither (module docstring).
TRINOMIAL_FORMS = {(3, 16): "weight 3", (4, 15): "weight 3", (7, 10): "weight 3",
                   (3, 28): "published", (6, 17): "weight 3", (7, 15): "published",
                   (9, 11): "weight 3"}  # fmt: skip
TRINOMIAL_SIZES = [s for s in RESERVED_PAIR if s in TRINOMIAL_FORMS]
TRINOMIAL_PER_SIZE = 2
TORIC_SIZES = [(5, 9), (8, 11), (10, 13), (12, 17), (14, 17), (15, 17)]
TORIC = [[0, 0], [1, 0]], [[0, 0], [0, 1]]
# Part (f): the reserved small sizes that the enumeration cannot reach
POWER_SIZES = [s for s in RESERVED_SMALL if s not in METHOD_SIZES]
POWER_PER_FAMILY, POWER_KMIN = 8, 4  # fmt: skip
POWER_FAMILIES = ("oneaxis", "hp", "factor1")
POWER_SEEDS = list(range(20))
# The codes on which the registered search stalled (examples/qec-distance, part 1 (c), 6x18 #1
# and #2), with k and the program's d in that run.
STALLED = [
    {"name": "stalled 6x18 #1", "l": 6, "m": 18, "n": 216, "A": [[2, 0], [0, 15], [0, 8]],
     "B": [[0, 0], [4, 0], [5, 0]], "k": 4, "d": 4},
    {"name": "stalled 6x18 #2", "l": 6, "m": 18, "n": 216, "A": [[1, 0], [0, 14], [0, 15]],
     "B": [[0, 6], [4, 0], [2, 0]], "k": 8, "d": 6},
]  # fmt: skip
PROGRAM, SEARCH, ANCHORED = "program", "search", "search (0, lm)"
INSTRUMENTS = (PROGRAM, SEARCH, ANCHORED)
STATUSES = {PROGRAM: first.PROGRAM_STATUSES, SEARCH: first.SEARCH_STATUSES,
            ANCHORED: first.SEARCH_STATUSES}  # fmt: skip
EXACT = {PROGRAM: "optimal", SEARCH: "complete", ANCHORED: "complete"}
CLASSES = first.CLASSES
OUTCOMES = ("agree", "consistent", "disagree", "method error", "not tested")  # part (c)
# What decide checks every record against (it is in the predictions; module docstring)
PROTOCOL = {
    "scip_fix": distance.SCIP_FIX,
    "deepen": True,
    "seeds": {"enumeration": METHOD_SEEDS, "fault": FAULT_SEEDS, "power": POWER_SEEDS},
}

EXCLUDED_SEEN = [
    "examples/qec-distance, registered and run on 2026-10-21: everything in its question's "
    "excluded_seen, and everything its run computed (its records.jsonl): its 200 method codes "
    "at 3x4, 2x8, 3x6, 4x5, 2x10, 3x8, 4x6 and 5x5 (both kinds), its 9 trinomial codes at 3x27, "
    "6x15 and 6x18 (6x18 #1 and #2 are this test's stalled codes), the toric code at 3x10, 4x9, "
    "5x11, 6x13, 8x10, 7x16, 10x14, 11x12, 12x13, 9x32, 13x14, 14x15, 15x16 and 16x17, and the "
    "12 published entries (the program and the search from (0, lm), kind Z)",
    "after that run, a scan for the fault: 280 random codes (2 to 6 terms, lm + k/2 <= 26) from "
    "random.Random('fault scan'), 40 at each of 4x4, 3x6, 2x9, 4x5, 4x6, 5x5 and 2x11 (an eighth "
    "size, 3x8, stopped unfinished), both kinds: distance_brute, and distance_ilp at seeds 0 to "
    "4 with SCIP's defaults, without its dual reductions and without the translation row; and "
    "the failing 4x5 code at seeds 0 to 7 under SCIP settings (presolve, dual reductions, single "
    "presolvers, propagators and constraint handlers, symmetry, the translation row)",
    "the SCIP fault hunt: distance_brute of both kinds, and distance_ilp under SCIP's defaults "
    "at seeds 0 to 19, both kinds, 60 s limit, on 2,476 distinct codes with k > 0 and lm + k/2 "
    "<= 26 (n = 8 to 50) from random.Random(f'scip fault hunt {family} {l}x{m}'), for the "
    "families random (two polynomials of 2 to 6 random terms), sparse (2 or 3 terms), factor "
    "(A = f g, B = f h; f of 2 or 3 terms, g and h of 1 or 2), oneaxis (a monomial times a "
    "polynomial of 2 or 3 terms in x alone or y alone) and trinomial (the published form); the "
    "first 30 per family and size in at most 3,000 draws, k computed for every draw: all five "
    "families at 2x2, 2x3, 2x4, 3x3, 2x5, 2x6, 3x4, 2x7, 4x4, 2x8, 3x6, 2x9, 6x3 and 2x12; "
    "oneaxis, factor and sparse at 4x5, 5x4, 2x10, 2x11, 4x6, 6x4, 3x8, 8x3 and 5x5, with the "
    "first 10 random and trinomial codes there and the first 13 random codes at 4x5",
    "candidate SCIP settings on the hunt's 48 failing programs and the 4x5 code, both kinds, "
    "seeds 0 to 19: dual reductions off (both, weak only, strong only), translation=False, "
    "presolve off, rapid learning off, rapid learning's applysolved, applyconflicts and "
    "applybdchgs off, constraints/linear/upgrade/xor off, constraints/xor/maxprerounds 0, and "
    "that with rapid learning off (SCIP_FIX)",
    "the 4x5 code, kind X, seeds 0 to 2 (translation on and off, weak dual reductions on and "
    "off): SCIP's transformed problem saved before rapid learning and replayed at seeds 0 to 99, "
    "with variants; an imitation of rapid learning's sub-SCIP at seeds 0 to 99; and all 780 "
    "weight-2 supports through verify_witness",
    "stress tests on 23 of the failing programs (one per class up to monomial factors and "
    "swapping A and B): 40 variants each from random.Random(f'stress {id}') and "
    "random.Random(f'stress2 {id}'), with c = 0 fixed on some qubits off a known least-weight "
    "logical and t capped at floor(d/2), each solved at seeds 0 to 2 under several settings",
    "the re-hunt: all 2,476 hunt codes, both kinds, seeds 0 to 9, under SCIP_FIX",
    "cost: the toric code at 13x13 and 14x14, and 9x9 #1, #2, #3, #10 and 12x9 #4, #11, #12 of "
    "the trinomials with k >= 4 from random.Random('qec-distance development LxM'), kind Z, "
    "seeds 0 and 1, 900 s limit, under the defaults, the candidate settings and SCIP_FIX",
    "the two stalled codes: distance_ilp under the defaults, without the XOR upgrade and under "
    "SCIP_FIX, seeds 0 to 4, both kinds",
    "the deepening search against distance_brute: the first 15 codes with k > 0 and lm + k/2 <= "
    "28 (2 to 4 random terms per polynomial) from random.Random(f'qec-distance deepen dev "
    "{l}x{m}') at each of 2x7, 2x9, 1x16, 2x11 and 1x25, both kinds: deepening, the single "
    "pass, the bound at d, and the old search, from every qubit and from (0, lm)",
    "the search on the toric code: 2x5, 3x6, 5x6, 6x8 and 10x10 (deepening, single pass, old); "
    "12x13, 14x14 and 16x17 (new and old, from every qubit and from (0, lm)); 20x20 (1 s limit)",
    "the search on the two stalled codes (both kinds, from every qubit and from (0, lm)) and on "
    "the 4x5 code (deepening and single pass, both kinds, with distance_brute)",
    "the search on check-independent/devcodes2.json: all 72 codes, kind Z from (0, lm), new and "
    "old (600 s); #42 to #71, kind Z from every qubit (new 600 s, old 300 s) and kind X from "
    "(0, lm) (new); #64 from (0, lm) with 2 s and 10 s limits. devcodes2 has codes at 3x9, 5x6 "
    "and 9x11, sizes reserved for this test: its codes are excluded here (equivalence_key)",
    "the search on the trinomials with k >= 4 from random.Random('qec-distance development "
    "LxM'), the first 16 at each of 7x7, 6x10, 9x9, 7x14, 12x9 and 6x24: kind Z from (0, lm), "
    "new (600 s) and old (600 s; 120 s for 6x24 #4 to #16)",
    "integrating the fixes: distance_ilp under SCIP_FIX on the 4x5 code (both kinds, seeds 0 to "
    "19; kind X at seeds 0 to 7 with scip_fix=False), and on the hunt's 48 failing programs at "
    "each of the 292 (program, seed) pairs where the defaults had failed, and without SCIP_FIX "
    "at the first of them; distance_brute and bb.k_linalg on the 38 codes of fault_cases.json, "
    "to write it; distance_brute on the toric code at 3x9 (timing)",
    "tests/test_qec_distance.py: codes from random.Random(1) to random.Random(5) at 2x2, 2x3, "
    "2x4, 3x3, 2x5, 2x6 and 4x4 (both instruments, the enumeration); the toric code at 2x5, "
    "3x3, 4x4, 3x6, 4x6, 5x6, 6x8, 3x4, 10x10 and 20x20; the 38 codes of fault_cases.json (the "
    "program at up to 3 of each program's failing seeds); the 4x5 code at seeds 0 to 7, with "
    "and without SCIP_FIX; the two stalled codes (the program, kind Z; the search, both kinds, "
    "from every qubit and from (0, lm)). tests/test_qec_distance_2.py: synthetic records, and 6 "
    "random codes at 3x4 from random.Random('test qec-distance-2 equivalence') with their "
    "images under equivalences (k and distance_brute)",
    "smoke tests of this study's jobs, writing no records: part (b)'s job for the 4x5 code "
    "(through _run), and job() with the code lists replaced by development codes: the toric "
    "code at 3x4 (the three instruments), the stalled code 6x18 #1 (the program and the search "
    "from (0, lm), and the three instruments as a stand-in for a part (c) code), and two codes "
    "from random.Random('smoke qec-distance-2 enumeration 2x4') at 2x4 (part (a)'s job)",
    "this test's codes drawn, their k computed, their equivalence keys compared with the "
    "checker's codes (devcodes*.json) and the toric code, and hashed, to fix them; no distance "
    "of any of them. k only, to choose part (c)'s forms: 3,000 published-form draws from this "
    "test's sequence random.Random('qec-distance-retest trinomial LxM') at each of 3x16, 4x15, "
    "5x13, 7x10, 3x28, 6x17, 7x15 and 9x11 (the first draws at 3x28 and 7x15 are part (c)'s "
    "codes there), 1,000 weight-3 draws from random.Random('scratch k census weight-3 LxM') "
    "at each of 3x16, 4x15, 5x13, 7x10, 6x17 and 9x11, and 20,000 weight-3 draws from this "
    "test's sequence at 5x13",
    "part (c)'s codes at 9x11 have the form, k and size of check-independent/devcodes2.json #63 "
    "to #65 (weight 3, k = 4, 9x11), on which the new search ran (above) and whose distances "
    "(18, 18 and 12) and search times were seen: those codes are excluded (equivalence_key), but "
    "that form at that size is not unseen",
    "the verification of the fixes, hunt H1 (distance_brute as the reference): 1,251 codes from "
    "random.Random('verify2 hunt H1 LxM'), of the families oneaxis, hp (A in x alone and B in y "
    "alone, each times a monomial), factor1 (a common factor in one variable times 1 to 3 "
    "random terms), sparse, factor and random, with k >= 2, lm + k/2 <= 26 and distinct "
    "equivalence_key, the first 30 at each of 2x2 (4), 2x3, 3x2, 2x4, 4x2, 3x3, 2x5, 5x2, 2x6, "
    "6x2, 3x4, 4x3, 2x7, 7x2, 4x4, 2x8, 8x2, 1x17, 3x6, 6x3, 2x9, 9x2, 1x19, 4x5, 5x4, 2x10, "
    "10x2, 2x11, 11x2, 1x23, 3x8, 8x3, 4x6, 6x4, 2x12, 12x2, 5x5, 1x13, 1x16, 1x20, 1x25, 1x24 "
    "(27) and 1x18 (20); on each, distance_brute of both kinds, distance_ilp under SCIP_FIX at "
    "seeds 0 to 9, both kinds, 60 s limit, the deepening search from every qubit and from "
    "(0, lm), both kinds, and the single pass from (0, lm), kind Z",
    "the verification's control on H1: distance_ilp with scip_fix=False at seeds 0 to 9, both "
    "kinds, on the first 1,188 of the 1,251 H1 codes",
    "the verification's power check of part (a): 511 codes from random.Random('verify2 power "
    "retest-like LxM'), drawn with this test's _draw over its FAMILIES, k <= 4, lm + k/2 <= 28 "
    "and distinct equivalence_key, 60 at each of 2x11, 11x2, 2x12, 12x2, 3x8, 8x3, 4x6 and 6x4, "
    "22 at 5x5 and 9 at 1x24; on each, the deepening search from (0, lm), both kinds, as the "
    "reference, and distance_ilp under SCIP_FIX and with scip_fix=False at seeds 0 to 4, both "
    "kinds",
    "the verification's hunt H2 (the search from (0, lm) as the reference): 296 codes from "
    "random.Random('verify2 hunt H2 LxM'), of the families oneaxis, hp, factor1, sparse, factor "
    "and weight3, with k >= 2, 10 at each of 3x11, 11x3, 2x17, 17x2, 2x19, 3x13, 13x3, 6x7, 7x6, "
    "3x14, 4x11, 11x4, 2x22, 2x23, 5x10, 10x5, 3x17, 4x13, 13x4, 5x11, 11x5, 7x8, 8x7, 4x14, "
    "8x8, 4x16, 6x11, 11x6 and 6x13, and 6 at 4x17; on each, the search from (0, lm), both "
    "kinds, 30 s limit, the search from every qubit, both kinds, the single pass from (0, lm), "
    "kind Z, and distance_ilp under SCIP_FIX and with scip_fix=False at seeds 0 to 5, both kinds",
    "the verification's stress test S3: the 49 programs of fault_cases.json (distance_brute "
    "computed again for each) and the 70 H1 programs of largest k/n at d = 2 to 6, 30 variants "
    "each from random.Random(f'verify2 stress3 {id}') keeping a least-weight logical W "
    "feasible (c = 0 fixed off W, c = 1 on part of W, t capped, z fixed, or an objective cut), "
    "each solved at SCIP seeds 0 to 2 under the defaults, SCIP_FIX, and SCIP_FIX with "
    "constraints/xor/gausspropfreq -1; and 40 of those programs presolved only, under SCIP_FIX, "
    "for the variable statuses in their XOR constraints",
    "the verification's rerun of the fault agent's reproduction (the SCIP fault hunt's random "
    "2x8 #26, kind Z, stress2 trial 14) at seed 1, and at seeds 0 to 5 under XOR maxprerounds "
    "0, 1 and 2, presolpairwise off, presolusehashing off, both off, gausspropfreq -1 and "
    "addextendedform on",
    "the verification's search stopped mid-pass: the toric code at 13x13, 16x16 and 11x19; "
    "check-independent/devcodes2.json #42, #44 and #47 (9x9), #60 and #61 (7x13), #66 and #67 "
    "(3x11); the stalled code 6x18 #2; both kinds, from every qubit and from (0, lm), a full run "
    "and then runs stopped at limits of 0.005 to 5 s",
    "the verification's comparison of the registered search.c (sha256 02d5133b) with the new "
    "one at deepen=False: 150 H1 codes sampled with random.Random('verify2 old vs single'), "
    "both kinds, from every qubit and from (0, lm); and the toric code at 15x16, distance_ilp "
    "under SCIP_FIX, kind Z, 1100 s limit",
    "the verification's runs of tests/test_qec_distance.py and tests/test_qec_distance_2.py "
    "(their own codes, above) and of decide on synthetic records; loading this study for _draw "
    "and equivalence_key computed nothing about its fresh codes",
    "applying the verification: part (f)'s codes drawn (power_codes), their k computed, their "
    "equivalence keys compared, and hashed, to fix them, no distance of any of them; k only, to "
    "choose part (f)'s design, 3,000 draws of each of its families from random.Random('scratch "
    "k census power FAMILY LxM') at each of 3x10, 4x7, 5x6, 2x14, 4x8 and 5x8, and the first 20 "
    "codes with k >= 4 of an earlier design (one family drawn per code) from "
    "random.Random('qec-distance-retest power LxM') at the same sizes; a smoke test of "
    "part (f)'s job (job() with power_codes replaced, writing no records) on 10 development "
    "codes of its families with k >= 4, the first 2 per family from random.Random('qec-distance-2 "
    "apply power smoke FAMILY LxM') at 3x11 (6 codes) and 2x19 (4; no hp code there had "
    "k >= 4): the search of both kinds from every qubit, and distance_ilp under SCIP_FIX and "
    "with scip_fix=False at seeds 0 to 19, both kinds; and the test suite, whose new tests of "
    "part (f) and of the protocol use synthetic records only",
]


# ---------------------------------------------------------------- equivalent codes


def _reduce(poly, ell: int, m: int) -> list[list[int]]:
    """poly's monomials reduced mod (l, m), repeated ones cancelling, sorted."""
    count = Counter((p % ell, q % m) for p, q in poly)
    return [[p, q] for (p, q), c in sorted(count.items()) if c % 2]


@functools.cache
def _isomorphisms(src: tuple[int, int], dst: tuple[int, int]) -> tuple:
    """Every isomorphism from Z_a x Z_b (src) onto Z_l x Z_m (dst), as the images of (1, 0) and
    (0, 1): the pairs of elements of orders dividing a and b that generate the whole group."""
    (a, b), (ell, m) = src, dst
    if a * b != ell * m:
        return ()
    group = [(p, q) for p in range(ell) for q in range(m)]
    firsts = [g for g in group if (a * g[0]) % ell == 0 and (a * g[1]) % m == 0]
    seconds = [g for g in group if (b * g[0]) % ell == 0 and (b * g[1]) % m == 0]
    out = []
    for g in firsts:
        for h in seconds:
            image = {((i * g[0] + j * h[0]) % ell, (i * g[1] + j * h[1]) % m)
                     for i in range(a) for j in range(b)}  # fmt: skip
            if len(image) == ell * m:
                out.append((g, h))
    return tuple(out)


def _mapped(poly, images, ell: int, m: int) -> list[tuple[int, int]]:
    (g0, g1), (h0, h1) = images
    return [((i * g0 + j * h0) % ell, (i * g1 + j * h1) % m) for i, j in poly]


def _translates(poly, ell: int, m: int) -> tuple:
    """The least, as a sorted tuple, of poly's translates. A least one contains (0, 0) (some
    translate does), so it is a translate by minus one of poly's monomials."""
    return min(tuple(sorted(((p - p0) % ell, (q - q0) % m) for p, q in poly)) for p0, q0 in poly)


def equivalence_key(A, B, ell: int, m: int) -> tuple:
    """A code's class under monomial factors on A and on B (H_X = [g A | h B] permutes the
    qubits of each block), swapping A and B (it swaps the blocks) and automorphisms of
    Z_l x Z_m (they permute the positions of both blocks alike): the least, over the
    automorphisms, of the sorted pair of the polynomials' least translates. Equivalent codes
    have the same distances; codes with different keys may still be equivalent under some other
    permutation of the qubits."""
    A, B = _reduce(A, ell, m), _reduce(B, ell, m)
    if not A or not B:  # a zero polynomial (the checker's edge cases): the reduced pair itself
        return tuple(tuple(map(tuple, P)) for P in (A, B))
    return min(
        tuple(sorted((_translates(_mapped(A, f, ell, m), ell, m),
                      _translates(_mapped(B, f, ell, m), ell, m))))
        for f in _isomorphisms((ell, m), (ell, m))
    )  # fmt: skip


def development_codes() -> list[dict]:
    """The development codes whose distances were computed and that can sit at this test's
    sizes: the independent checker's (check-independent/devcodes.json and devcodes2.json)."""
    out = []
    for name in ("devcodes.json", "devcodes2.json"):
        for c in json.loads((CHECKER / name).read_text()):
            out.append({"source": name, "l": c["l"], "m": c["m"], "A": c["A"], "B": c["B"]})
    return out


def _carried_key(A, B, src: tuple[int, int], dst: tuple[int, int]) -> tuple:
    """The equivalence key on dst of the code (A, B) on src, an isomorphic torus: the key of
    its image under one isomorphism (the key does not depend on which)."""
    images = _isomorphisms(src, dst)[0]
    A, B = (_mapped(_reduce(P, *src), images, *dst) for P in (A, B))
    return equivalence_key(A, B, *dst)


@functools.cache
def seen_keys(ell: int, m: int) -> frozenset:
    """The equivalence keys, carried onto Z_l x Z_m, of the toric code and of every development
    code on a torus isomorphic to Z_l x Z_m (development_codes)."""
    keys = {equivalence_key(*TORIC, ell, m)}
    for c in development_codes():
        if _isomorphisms((c["l"], c["m"]), (ell, m)):
            keys.add(_carried_key(c["A"], c["B"], (c["l"], c["m"]), (ell, m)))
    return frozenset(keys)


# ---------------------------------------------------------------- the codes


def _term(rng: random.Random, ell: int, m: int) -> list[int]:
    return [rng.randrange(ell), rng.randrange(m)]


def _times(f, g, ell: int, m: int) -> list[list[int]]:
    return _reduce([[a + c, b + d] for a, b in f for c, d in g], ell, m)


def _draw(rng: random.Random, family: str, ell: int, m: int) -> tuple[list, list]:
    """One draw of A and B (unreduced) from a family of method_codes or power_codes."""
    if family == "random":
        return tuple([_term(rng, ell, m) for _ in range(rng.randint(2, 6))] for _ in range(2))
    if family == "sparse":
        return tuple([_term(rng, ell, m) for _ in range(rng.randint(2, 3))] for _ in range(2))
    if family == "factor":
        f = [_term(rng, ell, m) for _ in range(rng.randint(2, 3))]
        g, h = ([_term(rng, ell, m) for _ in range(rng.randint(1, 2))] for _ in range(2))
        return _times(f, g, ell, m), _times(f, h, ell, m)
    if family == "oneaxis":
        axis, out = rng.randrange(2), []
        for _ in range(2):
            mono = _term(rng, ell, m)
            exponents = [rng.randrange(ell if axis == 0 else m) for _ in range(rng.randint(2, 3))]
            out.append(_times([mono], [[e, 0] if axis == 0 else [0, e] for e in exponents], ell, m))
        return tuple(out)
    if family == "trinomial":
        (a, e, f), (d, b, c) = first._three(rng, ell), first._three(rng, m)
        return [[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]
    if family == "hp":  # A in x alone and B in y alone, each times a monomial
        a = [[rng.randrange(ell), 0] for _ in range(rng.randint(2, 4))]
        b = [[0, rng.randrange(m)] for _ in range(rng.randint(2, 4))]
        return _times([_term(rng, ell, m)], a, ell, m), _times([_term(rng, ell, m)], b, ell, m)
    if family == "factor1":  # a common factor in one variable times random cofactors
        axis = rng.randrange(2)
        f = [[rng.randrange(ell), 0] if axis == 0 else [0, rng.randrange(m)]
             for _ in range(rng.randint(2, 3))]  # fmt: skip
        g, h = ([_term(rng, ell, m) for _ in range(rng.randint(1, 3))] for _ in range(2))
        return _times(f, g, ell, m), _times(f, h, ell, m)
    raise ValueError(family)


@functools.cache
def _method_codes(ell: int, m: int) -> str:
    rng = random.Random(f"qec-distance-retest method {ell}x{m}")
    out, keys, draws = [], set(seen_keys(ell, m)), 0
    while len(out) < PER_SIZE and draws < MAX_DRAWS:
        draws += 1
        family = FAMILIES[rng.randrange(len(FAMILIES))]
        A, B = (_reduce(P, ell, m) for P in _draw(rng, family, ell, m))
        if not A or not B:
            continue
        k = bb.k_linalg(A, B, ell, m)
        if not k or ell * m + k // 2 > distance.BRUTE_CAP:
            continue
        key = equivalence_key(A, B, ell, m)
        if key not in keys:
            keys.add(key)
            out.append({"family": family, "A": A, "B": B, "k": k})
    return json.dumps(out)


def method_codes(ell: int, m: int) -> list[dict]:
    """Part (a)'s codes at l x m: the first PER_SIZE, in at most MAX_DRAWS draws from
    random.Random('qec-distance-retest method LxM'), with A and B nonzero, k > 0, dim ker H_X =
    lm + k/2 within distance.BRUTE_CAP, and an equivalence_key that no earlier draw, development
    code or toric code has (seen_keys). Each draw picks its family (FAMILIES) at random."""
    return json.loads(_method_codes(ell, m))


@functools.cache
def _trinomial_codes(ell: int, m: int) -> str:
    rng = random.Random(f"qec-distance-retest trinomial {ell}x{m}")
    form, group = TRINOMIAL_FORMS[(ell, m)], [[p, q] for p in range(ell) for q in range(m)]
    out, keys, draws = [], set(seen_keys(ell, m)), 0
    while len(out) < TRINOMIAL_PER_SIZE and draws < MAX_DRAWS:
        draws += 1
        if form == "published":
            (a, e, f), (d, b, c) = rng.sample(range(ell), 3), rng.sample(range(m), 3)
            A, B = [[a, 0], [0, b], [0, c]], [[0, d], [e, 0], [f, 0]]
        else:
            A, B = (sorted(rng.sample(group, 3)) for _ in range(2))
        k = bb.k_linalg(A, B, ell, m)
        if not 4 <= k <= 12:
            continue
        key = equivalence_key(A, B, ell, m)
        if key not in keys:
            keys.add(key)
            out.append({"form": form, "A": A, "B": B, "k": k})
    return json.dumps(out)


def trinomial_codes(ell: int, m: int) -> list[dict]:
    """Part (c)'s codes at l x m: the first TRINOMIAL_PER_SIZE codes of the size's form
    (TRINOMIAL_FORMS: the published form, with a, e, f distinct and b, c, d distinct; or weight
    3, three distinct monomials in each of A and B), in at most MAX_DRAWS draws from
    random.Random('qec-distance-retest trinomial LxM'), with 4 <= k <= 12, the published
    entries' range, and an equivalence_key that no earlier draw, development code or toric code
    has. Nothing about them but k is known."""
    return json.loads(_trinomial_codes(ell, m))


@functools.cache
def _power_codes(ell: int, m: int) -> str:
    keys = set(seen_keys(ell, m))
    for src in POWER_SIZES[: POWER_SIZES.index((ell, m))]:
        if _isomorphisms(src, (ell, m)):
            keys |= {_carried_key(c["A"], c["B"], src, (ell, m)) for c in power_codes(*src)}
    out = []
    for family in POWER_FAMILIES:
        rng = random.Random(f"qec-distance-retest power {family} {ell}x{m}")
        found = draws = 0
        while found < POWER_PER_FAMILY and draws < MAX_DRAWS:
            draws += 1
            A, B = (_reduce(P, ell, m) for P in _draw(rng, family, ell, m))
            if not A or not B:
                continue
            k = bb.k_linalg(A, B, ell, m)
            if k < POWER_KMIN:
                continue
            key = equivalence_key(A, B, ell, m)
            if key not in keys:
                keys.add(key)
                found += 1
                out.append({"family": family, "A": A, "B": B, "k": k})
    return json.dumps(out)


def power_codes(ell: int, m: int) -> list[dict]:
    """Part (f)'s codes at l x m: for each family of POWER_FAMILIES in turn, the first
    POWER_PER_FAMILY codes in at most MAX_DRAWS draws from random.Random('qec-distance-retest
    power FAMILY LxM'), with A and B nonzero, k >= POWER_KMIN, and an equivalence_key that no
    earlier draw, development code or toric code has, nor any code of an earlier size of
    POWER_SIZES on an isomorphic torus. A family with fewer classes than that gives fewer codes
    (one axis, at the smallest tori). Nothing about them but k is known."""
    return json.loads(_power_codes(ell, m))


def fault_cases() -> list[dict]:
    """Part (b)'s codes (fault_cases.json): id, family, l, m, A, B, k, d, and by kind the SCIP
    seeds among 0 to 19 at which SCIP's defaults gave a wrong optimum."""
    return json.loads(CASES.read_text())["codes"]


def known_codes() -> list[dict]:
    """Part (d)'s entries: the published ones, built as examples/qec-distance builds them (its
    codes()), with their published d, and the two stalled codes with the program's d."""
    out = [{"name": c["name"], "l": c["l"], "m": c["m"], "n": c["n"], "A": c["A"], "B": c["B"],
            "k": c["k"], "d": c["d"], "source": "published (../qec-bb/codes.json)",
            "instruments": [PROGRAM, ANCHORED]} for c in first.codes()]  # fmt: skip
    return out + [
        {**c, "source": "the program in examples/qec-distance's run, part 1 (c)",
         "instruments": list(INSTRUMENTS)}
        for c in STALLED
    ]  # fmt: skip


def _sha256(obj) -> str:
    return first._sha256(obj)


def _known_sha256(c: dict) -> str:
    """A part (d) entry's hash: codes.json's for a published entry, as examples/qec-distance
    registered it; the code's own for a stalled code."""
    if c["source"].startswith("published"):
        return first._codes_sha256()
    return _sha256({key: c[key] for key in ("l", "m", "A", "B", "k")})


def code_hashes() -> dict:
    """The sha256 of each registered code (or code list), by the name its records carry: part
    (a)'s lists by job key, part (b)'s, (c)'s and (f)'s codes, and part (d)'s entries."""
    out = {f"enumeration {ell}x{m}": _sha256(method_codes(ell, m)) for ell, m in METHOD_SIZES}
    out.update({f"fault {c['id']}": _sha256(c) for c in fault_cases()})
    for ell, m in TRINOMIAL_SIZES:
        for i, c in enumerate(trinomial_codes(ell, m)):
            out[f"trinomial {ell}x{m} #{i + 1}"] = _sha256(c)
    for ell, m in POWER_SIZES:
        for i, c in enumerate(power_codes(ell, m)):
            out[f"power {ell}x{m} #{i + 1}"] = _sha256(c)
    out.update({c["name"]: _known_sha256(c) for c in known_codes()})
    return out


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- the rules


def intervals(rows: list[dict]) -> list:
    """examples/qec-distance's interval for each row that gave a result (None for a method
    error: other than k logicals, a status outside its instrument's, a witness that fails, or
    none with an exact value)."""
    return [
        first.interval(r["result"], r["k_linalg"], STATUSES[r["instrument"]])
        for r in rows
        if "result" in r
    ]


def classify(rows: list[dict], predicted: int) -> str:
    """examples/qec-distance's rule for one entry (its classify), from any number of
    instruments' records (an error row, or none, for one that gave no result), against the
    registered d: the entry's interval is the intersection of the instruments' intervals."""
    results = intervals(rows)
    if not results:
        return "not tested"
    if None in results:
        return "method error"
    lower = max(lo for lo, _ in results)
    uppers = [up for _, up in results if up is not None]
    upper = min(uppers) if uppers else None
    if upper is not None and lower > upper:
        return "method error"  # the instruments' intervals do not meet
    if upper == lower:
        return "reproduced" if upper == predicted else "contradicted"
    if (upper is not None and upper < predicted) or lower > predicted:
        return "contradicted"
    return "consistent but unresolved"


def compare(rows: list[dict]) -> str:
    """Part (c)'s rule for one code, from its instruments' records: "method error" (an
    instrument found other than k logicals, ended with another status, or returned a witness
    that fails, or none with an exact value); "disagree" (two intervals do not meet); "not
    tested" (an instrument gave no result, and neither of those); "agree" (all three exact, and so
    equal); "consistent" (at least one stopped at its limit, and the intervals meet). A code
    whose jobs have not all run is "not tested" too; decide reports those jobs as missing."""
    results = intervals(rows)
    if not results:
        return "not tested"
    if None in results:
        return "method error"
    uppers = [up for _, up in results if up is not None]
    if uppers and max(lo for lo, _ in results) > min(uppers):
        return "disagree"
    tested = [r for r in rows if "result" in r]
    if len(tested) < len(INSTRUMENTS):
        return "not tested"
    return "agree" if all(r["result"]["d"] is not None for r in tested) else "consistent"


def _run_failures(r: dict, k: int, d: int | None, exact: str, label: str) -> list[str]:
    """Why one run is not exact with d: its status, its logicals, its d, its witness."""
    out = []
    if r["status"] != exact:
        out.append(f"{label}: status {r['status']}")
    if r["k"] != k:
        out.append(f"{label}: {r['k']} logicals, k = {k}")
    if r["d"] != d:
        out.append(f"{label}: d = {r['d']}, expected {d}")
    if not (r.get("witness_check") or {}).get("logical"):
        out.append(f"{label}: no checked witness")
    return out


def enumeration_failures(row: dict) -> list[str]:
    """Part (a)'s rule for one code's record: why it fails, or [] when d_X = d_Z by enumeration,
    both enumeration witnesses pass, and every program and search is exact with k logicals, the
    enumeration's d and a checked witness."""
    brute, k = row["brute"], row["k"]
    out = [] if brute["Z"]["d"] == brute["X"]["d"] else ["enumeration: d_X != d_Z"]
    for kind in distance.KINDS:
        if not (brute[kind].get("witness_check") or {}).get("logical"):
            out.append(f"enumeration {kind}: no checked witness")
        for r in row["program"][kind]:
            out += _run_failures(r, k, brute[kind]["d"], "optimal", f"program {kind} {r['seed']}")
    for name in (SEARCH, ANCHORED):
        out += _run_failures(row["search"][name], k, brute["Z"]["d"], "complete", name)
    return out


def fault_failures(row: dict) -> list[str]:
    """Part (b)'s rule for one code's record: why it fails, or [] when bb.k_linalg and the
    enumeration give the file's k and d, and every program is optimal with k logicals, that d and
    a checked witness."""
    k, d = row["k"], row["known_d"]
    out = [] if row["k_linalg"] == k else [f"k_linalg = {row['k_linalg']}, k = {k}"]
    for kind in distance.KINDS:
        if row["brute"][kind]["d"] != d:
            out.append(f"enumeration {kind}: d = {row['brute'][kind]['d']}, expected {d}")
        for r in row["program"][kind]:
            out += _run_failures(r, k, d, "optimal", f"program {kind} {r['seed']}")
    return out


def toric_failures(row: dict) -> list[str]:
    """Part (e)'s rule for one instrument's record: why it fails, or [] when it is exact with
    d = min(l, m) (the record's l and m, which decide checks against its job's), k = 2 logicals
    (bb.k_linalg's too) and a checked witness."""
    if "error" in row:
        return ["not tested"]
    out = [] if row["k_linalg"] == 2 else [f"k_linalg = {row['k_linalg']}"]
    d = min(row["l"], row["m"])
    return out + _run_failures(row["result"], 2, d, EXACT[row["instrument"]], row["instrument"])


def power_failures(row: dict) -> list[str]:
    """Part (f)'s rule for one code's record: why it fails, or [] when bb.k_linalg gives the
    registered k, the search of each kind from every qubit is complete with k logicals, a d and a
    checked witness, d_X = d_Z, and every program under SCIP_FIX is optimal with k logicals, the
    search's d of its kind and a checked witness. The control is not judged (control_wrong)."""
    k, search = row["k"], row["search"]
    out = [] if row["k_linalg"] == k else [f"k_linalg = {row['k_linalg']}, k = {k}"]
    if search["Z"]["d"] != search["X"]["d"]:
        out.append("search: d_X != d_Z")
    for kind in distance.KINDS:
        d = search[kind]["d"]
        out += _run_failures(search[kind], k, d, "complete", f"search {kind}")
        for r in row["program"][kind]:
            out += _run_failures(r, k, d, "optimal", f"program {kind} {r['seed']}")
    return out


def control_wrong(row: dict) -> list[list]:
    """Part (f)'s control, reported and not judged: [kind, seed, status, d, lower] for each run
    under SCIP's defaults that is wrong against the search's d of its kind, where the search
    found one: an optimum other than d, a lower bound above d at a limit, or a status other than
    optimal or a limit (infeasible, say)."""
    out = []
    for kind in distance.KINDS:
        d = row["search"][kind]["d"]
        for r in row["control"][kind] if d is not None else []:
            if r["status"] == "optimal":
                wrong = r["d"] != d
            elif r["status"] in first.LIMITS:
                wrong = r["lower"] is not None and r["lower"] > d
            else:
                wrong = True
            if wrong:
                out.append([kind, r["seed"], r["status"], r["d"], r["lower"]])
    return out


def protocol_failures(r: dict, spec: dict | None, protocol: dict) -> list[str]:
    """Why a record was not made by the registered protocol (PROTOCOL, from the predictions):
    its l and m are not those of `spec` (its job's, or its part (d) entry's), a toric record's
    code is not the toric code, the programs of (a), (b) or (f) did not run at the registered
    seeds, a program ran without SCIP_FIX in its settings (or, in (f)'s control, with it), or a
    search did not deepen, or ran from other anchors than its instrument's. [] for a failed
    job's error row."""
    if "error" in r:
        return []
    fix, out = protocol["scip_fix"], []
    if spec is not None and "l" in spec and (r.get("l"), r.get("m")) != (spec["l"], spec["m"]):
        out.append(f"l x m = {r.get('l')}x{r.get('m')}, registered {spec['l']}x{spec['m']}")
    if r.get("test") == "toric" and [r.get("A"), r.get("B")] != list(TORIC):
        out.append("not the toric code")

    def program(p: dict, fixed: bool, label: str) -> list[str]:
        settings = p.get("settings") or {}
        applied = all(settings.get(key) == value for key, value in fix.items())
        if fixed and not (p.get("scip_fix") is True and applied):
            return [f"{label}: not under SCIP_FIX"]
        if not fixed and not (p.get("scip_fix") is False and not set(fix) & set(settings)):
            return [f"{label}: not under SCIP's defaults"]
        return []

    def search(s: dict, anchors, label: str) -> list[str]:
        if s.get("deepen") == protocol["deepen"] and s.get("anchors") == anchors:
            return []
        return [f"{label}: deepen {s.get('deepen')}, anchors {s.get('anchors')}"]

    def seeded(runs: dict, part: str, fixed: bool, label: str) -> list[str]:
        found = []
        for kind in distance.KINDS:
            seeds = [p.get("seed") for p in runs.get(kind, [])]
            if seeds != protocol["seeds"][part]:
                found.append(f"{label} {kind}: seeds {seeds}")
            for p in runs.get(kind, []):
                found += program(p, fixed, f"{label} {kind} {p.get('seed')}")
        return found

    if "result" in r:
        if r["instrument"] == PROGRAM:
            out += program(r["result"], True, PROGRAM)
        else:
            anchors = "all" if r["instrument"] == SEARCH else [0, r["l"] * r["m"]]
            out += search(r["result"], anchors, r["instrument"])
    elif r.get("test") == "enumeration":
        lm = r["l"] * r["m"]
        for i, c in enumerate(r["rows"]):
            out += seeded(c["program"], "enumeration", True, f"#{i + 1} program")
            out += search(c["search"][SEARCH], "all", f"#{i + 1} {SEARCH}")
            out += search(c["search"][ANCHORED], [0, lm], f"#{i + 1} {ANCHORED}")
    elif r.get("test") == "fault":
        out += seeded(r["program"], "fault", True, "program")
    elif r.get("test") == "power":
        out += seeded(r["program"], "power", True, "program")
        out += seeded(r["control"], "power", False, "control")
        for kind in distance.KINDS:
            out += search(r["search"][kind], "all", f"search {kind}")
    return out


# ---------------------------------------------------------------- the registration


def question() -> dict:
    return {
        "id": "qec-distance-retest",
        "title": "A re-test of the fixed distance instruments for bivariate bicycle codes: the "
        "integer program without SCIP's XOR presolving and rapid learning, and the deepening "
        "search",
        "statement": "After examples/qec-distance found a wrong optimum from SCIP 10.0 and two "
        "stalls of the search, distance.distance_ilp runs SCIP with SCIP_FIX and "
        "distance.distance_search deepens its bound. (a) On 50 fresh codes at 2x13 and 3x9, "
        "both equal the enumeration (the program at 5 seeds, both kinds); (c) on 14 fresh "
        "trinomial codes at 7 reserved sizes (n = 96 to 210; of the published form at 3x28 and "
        "7x15, of weight 3 elsewhere), the intervals of the program and of the search from "
        "every qubit and from (0, lm) meet, with 20-minute limits, and the search completes on "
        "every one; (e) both give min(l, m) on the toric code at 6 new sizes; (f) on 142 fresh "
        "structured codes with k >= 4 at the 6 other reserved small sizes (n = 56 to 80), of the "
        "families where SCIP's defaults failed, the program at 20 seeds, both kinds, equals the "
        "search from every qubit, while SCIP's defaults, run beside it as an unjudged control, "
        "are wrong at least once. "
        "(b) The 38 codes on which SCIP's defaults failed give the right d at seeds 0 to 19, "
        "and (d) the 12 published entries and the 2 stalled codes give their known d: "
        "regressions on known answers, not blind.",
        "source": "examples/qec-distance (its registration, run and records), "
        "docs/code-distances.md; distance.py's fixes",
        "fix": {
            "program": "distance_ilp with scip_fix=True (the default): SCIP_FIX, "
            "constraints/xor/maxprerounds 0 and separating/rapidlearning/freq -1, set in every "
            "program and recorded in its settings; the formulation is unchanged",
            "search": "distance_search with deepen=True (the default): passes with bound 2, 3, "
            "..., SEARCH_BOUND, stopping at the first logical found, whose weight is d; at a "
            "time-out, lower = the largest bound of a pass that found nothing",
        },
        "scip_fix": distance.SCIP_FIX,
        "solver": distance.scip_version(),
        "scip_seed": distance.SEED,
        "search_bound": distance.SEARCH_BOUND,
        "search_compiler": distance._search_binary()[1],
        "search_c_sha256": _file_sha256(distance.SEARCH_C),
        "distance_py_sha256": _file_sha256(FIRST / "distance.py"),
        "memory_limit_mb": distance.MEMORY_MB,
        "enumeration_cap": distance.BRUTE_CAP,
        "formulation": "binary c; H_X c = 2 s; L.c = 2 t_L + z_L for a basis L of the "
        "X-logicals, z_L binary, sum z_L >= 1; c_(0,0) + c_(lm+(0,0)) >= 1; minimise sum c "
        "(unchanged)",
        "reserved_small_sizes": [list(s) for s in RESERVED_SMALL],
        "method_sizes": [list(s) for s in METHOD_SIZES],
        "method_sizes_rule": "the reserved small sizes with lm + 1 <= enumeration_cap (k > 0 "
        "is even, so dim ker H_X = lm + k/2 >= lm + 1); the others cannot be enumerated",
        "method_codes": f"method_codes(l, m): the first {PER_SIZE} codes, in at most "
        f"{MAX_DRAWS} draws from random.Random('qec-distance-retest method LxM'), each of a "
        f"family drawn from {list(FAMILIES)}, with k > 0, lm + k/2 <= {distance.BRUTE_CAP} and "
        "an equivalence class new to the draws, the checker's codes and the toric code; at "
        "2x13, 16 factor, 5 random, 3 sparse and 1 oneaxis, k = 2 for 13 and 4 for 12; at 3x9, "
        "21 random, 3 factor and 1 sparse, k = 2 for all",
        "method_codes_sha256": _sha256(
            {f"{ell}x{m}": method_codes(ell, m) for ell, m in METHOD_SIZES}
        ),
        "method_seeds": METHOD_SEEDS,
        "method_time_limit_seconds": METHOD_LIMIT,
        "fault_cases_file": "fault_cases.json",
        "fault_cases_sha256": _file_sha256(CASES),
        "fault_seeds": FAULT_SEEDS,
        "reserved_pair_sizes": [list(s) for s in RESERVED_PAIR],
        "trinomial_sizes": [list(s) for s in TRINOMIAL_SIZES],
        "trinomial_forms": {f"{ell}x{m}": f for (ell, m), f in TRINOMIAL_FORMS.items()},
        "trinomial_forms_rule": "the published form (A = x^a + y^b + y^c, B = y^d + x^e + x^f) "
        "where it has codes with 4 <= k <= 12, otherwise weight 3 (three distinct monomials in "
        "each of A and B); the published form has k = 0 for every choice at 3x16 and 4x15, and "
        "in 3,000 draws each at 5x13, 7x10, 6x17 and 9x11; 5x13 is left out, weight 3 having "
        "k = 0 there in 20,000 draws (k only)",
        "trinomial_codes": f"trinomial_codes(l, m): the first {TRINOMIAL_PER_SIZE} codes of the "
        f"size's form with 4 <= k <= 12, in at most {MAX_DRAWS} draws from "
        "random.Random('qec-distance-retest trinomial LxM'), each of an equivalence class new "
        "to the draws, the checker's codes and the toric code; k is 4 at 3x16, 4x15, 6x17 and "
        "9x11, 6 at 7x10, 12 at 3x28 and 7x15",
        "trinomial_codes_sha256": _sha256(
            {f"{ell}x{m}": trinomial_codes(ell, m) for ell, m in TRINOMIAL_SIZES}
        ),
        "pair_time_limit_seconds": PAIR_LIMIT,
        "power_sizes": [list(s) for s in POWER_SIZES],
        "power_sizes_rule": "the reserved small sizes that the enumeration cannot reach (not "
        "method_sizes); 3x10 and 5x6 are isomorphic tori",
        "power_families": {
            "oneaxis": "a monomial times a polynomial of 2 or 3 terms in x alone, or in y alone, "
            "the same axis for A and B (as in method_codes)",
            "hp": "A a monomial times a polynomial of 2 to 4 terms in x alone, B a monomial "
            "times one of 2 to 4 terms in y alone",
            "factor1": "A = f g, B = f h, f of 2 or 3 terms in x alone or in y alone, g and h "
            "of 1 to 3 random terms",
        },
        "power_codes": f"power_codes(l, m): for each family, the first {POWER_PER_FAMILY} codes "
        f"with k >= {POWER_KMIN}, in at most {MAX_DRAWS} draws from "
        "random.Random('qec-distance-retest power FAMILY LxM'), each of an equivalence class "
        "new to the draws, the checker's codes, the toric code and the codes of an earlier "
        "power size on an isomorphic torus; 142 codes: 8 of each family at each size but 4x7, "
        "where one axis gave 6 classes in its draws; 46 oneaxis, 48 hp and 48 factor1; k from 4 "
        "to 40",
        "power_codes_sha256": _sha256(
            {f"{ell}x{m}": power_codes(ell, m) for ell, m in POWER_SIZES}
        ),
        "power_seeds": POWER_SEEDS,
        "power_time_limit_seconds": METHOD_LIMIT,
        "protocol": PROTOCOL,
        "toric_sizes": [list(s) for s in TORIC_SIZES],
        "time_limit_seconds": LIMIT,
        "codes_file": "../qec-bb/codes.json",
        "codes_sha256": first._codes_sha256(),
        "published_sizes": [list(s) for s in first.PUBLISHED_SIZES],
        "stalled_codes": STALLED,
        "instruments": {
            PROGRAM: "distance_ilp, kind Z (both kinds in (a), (b) and (f)), the translation "
            "row, SCIP_FIX (and SCIP's defaults in (f)'s control)",
            SEARCH: "distance_search, kind Z (both kinds in (f)), from every qubit, deepening, "
            "bound SEARCH_BOUND",
            ANCHORED: "distance_search, kind Z, from the anchors (0, lm), deepening, bound "
            "SEARCH_BOUND",
        },
        "parts": {
            "a": "enumeration: per code, distance_brute (both kinds), the program (both kinds, "
            "method_seeds), the search and the search from (0, lm) (kind Z), method limits",
            "b": "faults (a regression on known answers, not a prediction): per code of "
            "fault_cases.json, distance_brute and the program, both kinds, fault_seeds",
            "c": "program against search: per code, the three instruments, pair limits",
            "d": "known answers (not blind): the published entries (the program and the search "
            "from (0, lm)) and the stalled codes (all three instruments), limits",
            "e": "the toric code: the three instruments, limits",
            "f": "power against the fault: per code of power_codes, the search from every qubit "
            "(both kinds, the reference), the program (both kinds, power_seeds) under SCIP_FIX, "
            "and the same programs under SCIP's defaults (the control, recorded and not "
            "judged), method limits",
        },
        "classification": {
            "interval": "each instrument: lower = the program's dual bound (its optimum when "
            "optimal), or the search's d when complete, or at a time-out the largest bound of "
            "a pass that found nothing (1 if none); upper = its checked witness's weight; an "
            "entry's interval is the intersection",
            "method error": "an instrument found logicals != bb.k_linalg, ended with a status "
            "other than exact or a limit, or returned a witness that fails verify_witness (or "
            "none with an exact value); or the intervals do not meet",
            "known answers (d)": "reproduced (the interval is the registered d), consistent but "
            "unresolved (it holds the registered d and more), contradicted (it excludes it), "
            "method error, not tested (no instrument gave a result); a contradiction or a "
            "method error fails the instruments, the known d having been reproduced before",
            "program against search (c)": "agree (all three exact), consistent (one at a "
            "limit; the intervals meet), disagree (two intervals do not meet), method error, "
            "not tested (an instrument's job failed); (c) can show a program fault only where a "
            "search completes, since an optimum above d lies within the intervals of searches "
            "stopped at their limits below it",
            "protocol": "every record's l and m are its job's (or its entry's), a toric record "
            "holds the toric code, the programs of (a), (b) and (f) ran at the registered seeds, "
            "every program with SCIP_FIX in its settings ((f)'s control without it), every "
            "search deepening, from its instrument's anchors; otherwise the record fails",
            "verdict": "hold when (a), (b), (c), (e) and (f) pass, no entry of (d) is a method "
            "error or contradicted, and every record follows the protocol; fail when any of "
            "them fails, or a record's code differs from the registration; incomplete when jobs "
            "are missing and nothing failed",
        },
        "excluded_seen": EXCLUDED_SEEN,
        "hypotheses": {
            "instruments": "the fixed program and the deepening search are exact: equal to the "
            "enumeration on fresh codes at n = 52 and 54, consistent with each other on fresh "
            "trinomials at n = 96 to 210, min(l, m) on the toric code at 6 new sizes up to "
            "n = 510, and equal to each other at 20 seeds on fresh structured codes of high k "
            "at n = 56 to 80, where SCIP's defaults fail",
            "completion": "the deepening search, from (0, lm) and from every qubit, completes "
            "within 20 minutes on every fresh trinomial of part (c)",
            "power": "SCIP's defaults (scip_fix=False) are wrong at least once on part (f)'s "
            "codes, so that (f) can see the fault",
        },
    }


def predictions() -> list[dict]:
    hashes = code_hashes()
    out = [
        {
            "test": "enumeration",
            "part": "a",
            "predicted": "on every code of method_codes at each method size: d_X = d_Z by "
            "distance_brute; the program, both kinds, at each method seed, optimal with k "
            "logicals and the enumeration's d; the search (kind Z) from every qubit and from "
            "(0, lm) complete with k logicals and that d; every witness checked",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("enumeration")},
            "protocol": PROTOCOL,
        },
        {
            "test": "faults",
            "part": "b",
            "blind": False,
            "note": "a regression on known answers, not a prediction: these codes, their d and "
            "the seeds at which SCIP's defaults failed were known, and SCIP_FIX was chosen on "
            "them",
            "predicted": "on each code of fault_cases.json, distance_brute gives the file's d "
            "for both kinds, and the program, both kinds, at every fault seed, is optimal with k "
            "logicals, that d and a checked witness",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("fault ")},
            "protocol": PROTOCOL,
        },
        {
            "test": "program-search",
            "part": "c",
            "predicted": "on each code of trinomial_codes: the intervals of the program, the "
            "search from every qubit and the search from (0, lm) meet, each instrument finds k "
            "logicals, ends exact or at its limit, and every witness is checked",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("trinomial")},
            "protocol": PROTOCOL,
        },
        {
            "test": "search-completes",
            "part": "c",
            "instrument": ANCHORED,
            "predicted": "the search from (0, lm) completes with a d within the pair limit on "
            "every code of trinomial_codes",
        },
        {
            "test": "search-completes",
            "part": "c",
            "instrument": SEARCH,
            "predicted": "the search from every qubit completes with a d within the pair limit "
            "on every code of trinomial_codes",
        },
        {
            "test": "toric",
            "part": "e",
            "predicted": "at each toric size, the program optimal and the search from every "
            "qubit and from (0, lm) complete, each with d = min(l, m), k = 2 logicals and a "
            "checked witness",
            "sizes": [list(s) for s in TORIC_SIZES],
            "protocol": PROTOCOL,
        },
        {
            "test": "power",
            "part": "f",
            "predicted": "on every code of power_codes at each power size: the search from every "
            "qubit, both kinds, complete with k logicals, d_X = d_Z and checked witnesses; the "
            "program under SCIP_FIX, both kinds, at each power seed, optimal with k logicals, "
            "the search's d and a checked witness",
            "codes_sha256": {key: h for key, h in hashes.items() if key.startswith("power ")},
            "protocol": PROTOCOL,
        },
        {
            "test": "power-control",
            "part": "f",
            "note": "reported beside the verdict, not in it: the control shows whether (f) can "
            "see the fault",
            "predicted": "SCIP's defaults (scip_fix=False), run on the programs of part (f) at "
            "the power seeds, are wrong at least once against the search's d: an optimum other "
            "than d, a lower bound above d at a limit, or a status other than optimal or a limit",
        },
    ]
    return out + [
        {"test": "known", "part": "d", "blind": False, "name": c["name"], "l": c["l"],
         "m": c["m"], "n": c["n"], "k": c["k"], "known_d": c["d"], "source": c["source"],
         "instruments": c["instruments"], "codes_sha256": hashes[c["name"]]}
        for c in known_codes()
    ]  # fmt: skip


# ---------------------------------------------------------------- jobs


def jobs() -> list[dict]:
    """Every job, in the order they start: the published entries by decreasing n, the toric
    sizes by decreasing n, part (c)'s codes by decreasing n, the stalled codes (each code's
    instruments in INSTRUMENTS order), then part (a)'s sizes, part (b)'s codes and part (f)'s
    codes."""

    def each(test: str, code: str, instruments, **spec) -> list[dict]:
        return [{"test": test, "key": f"{code}: {name}", "code": code, "instrument": name, **spec}
                for name in instruments]  # fmt: skip

    known = sorted(known_codes(), key=lambda c: (-c["n"], c["name"]))
    toric = sorted(TORIC_SIZES, key=lambda s: (-s[0] * s[1], s))
    pairs = sorted(TRINOMIAL_SIZES, key=lambda s: (-s[0] * s[1], s))
    out = [j for c in known if c["name"] not in {s["name"] for s in STALLED}
           for j in each("known", c["name"], c["instruments"])]  # fmt: skip
    out += [
        j for ell, m in toric for j in each("toric", f"toric {ell}x{m}", INSTRUMENTS, l=ell, m=m)
    ]
    out += [
        j
        for ell, m in pairs
        for i in range(len(trinomial_codes(ell, m)))
        for j in each("trinomial", f"trinomial {ell}x{m} #{i + 1}", INSTRUMENTS, l=ell, m=m, i=i)
    ]
    out += [j for c in STALLED for j in each("known", c["name"], INSTRUMENTS)]
    out += [{"test": "enumeration", "key": f"enumeration {ell}x{m}", "l": ell, "m": m}
            for ell, m in METHOD_SIZES]  # fmt: skip
    out += [{"test": "fault", "key": f"fault {c['id']}", "id": c["id"]} for c in fault_cases()]
    return out + [
        {"test": "power", "key": f"power {ell}x{m} #{i + 1}", "l": ell, "m": m, "i": i}
        for ell, m in POWER_SIZES
        for i in range(len(power_codes(ell, m)))
    ]


def _program(
    A, B, ell: int, m: int, kind: str, limit: float, seed: int = distance.SEED, scip_fix=True
) -> dict:
    """The program's result, its witness checked, as a record's fields."""
    r = distance.distance_ilp(A, B, ell, m, kind, limit, seed=seed, scip_fix=scip_fix)
    keep = ("kind", "translation", "scip_fix", "seed", "k", "status", "d", "lower", "upper",
            "dual_bound", "witness", "seconds", "solving_seconds", "nodes", "time_limit",
            "settings", "parameters", "solver")  # fmt: skip
    return {**{key: r[key] for key in keep},
            "witness_check": first._checked(A, B, ell, m, kind, r["witness"])}  # fmt: skip


def _searched(A, B, ell: int, m: int, kind: str, limit: float, anchors) -> dict:
    """distance_search's result, its witness checked, as a record's fields."""
    s = distance.distance_search(A, B, ell, m, kind, anchors=anchors, time_limit=limit)
    keep = ("kind", "status", "d", "lower", "upper", "witness", "k", "nodes", "passes", "deepen",
            "bound", "anchors", "time_limit", "seconds", "compiler")  # fmt: skip
    return {**{key: s[key] for key in keep},
            "witness_check": first._checked(A, B, ell, m, kind, s["witness"])}  # fmt: skip


def _instrument(name: str, A, B, ell: int, m: int, limit: float) -> dict:
    if name == PROGRAM:
        return _program(A, B, ell, m, "Z", limit)
    return _searched(A, B, ell, m, "Z", limit, None if name == SEARCH else (0, ell * m))


def _brief(r: dict) -> dict:
    """A run's result as a list entry: what the rules read, and what decide checks against the
    registered protocol (scip_fix and settings, deepen and anchors)."""
    keep = ("seed", "status", "d", "lower", "upper", "k", "witness", "witness_check", "nodes",
            "seconds", "scip_fix", "settings", "deepen", "anchors")  # fmt: skip
    return {key: r[key] for key in keep if key in r}


def _enumerated(A, B, ell: int, m: int) -> dict:
    out = {}
    for kind in distance.KINDS:
        b = distance.distance_brute(A, B, ell, m, kind)
        out[kind] = {"d": b["d"], "dim": b["dim"], "witness": b["witness"], "seconds": b["seconds"],
                     "witness_check": first._checked(A, B, ell, m, kind, b["witness"])}  # fmt: skip
    return out


def _programs(A, B, ell: int, m: int, seeds, scip_fix: bool = True) -> dict:
    return {kind: [_brief(_program(A, B, ell, m, kind, METHOD_LIMIT, seed, scip_fix))
                   for seed in seeds]
            for kind in distance.KINDS}  # fmt: skip


def _enumeration_code(c: dict, ell: int, m: int) -> dict:
    A, B = c["A"], c["B"]
    searches = {name: _brief(_searched(A, B, ell, m, "Z", METHOD_LIMIT, anchors))
                for name, anchors in ((SEARCH, None), (ANCHORED, (0, ell * m)))}  # fmt: skip
    row = {**c, "brute": _enumerated(A, B, ell, m),
           "program": _programs(A, B, ell, m, METHOD_SEEDS), "search": searches}  # fmt: skip
    return {**row, "failures": enumeration_failures(row)}


def _power_code(c: dict, ell: int, m: int) -> dict:
    """Part (f)'s record fields for one code: the reference searches, the programs under
    SCIP_FIX, and the control under SCIP's defaults."""
    A, B = c["A"], c["B"]
    search = {kind: _brief(_searched(A, B, ell, m, kind, METHOD_LIMIT, None))
              for kind in distance.KINDS}  # fmt: skip
    row = {**c, "k_linalg": bb.k_linalg(A, B, ell, m), "search": search,
           "program": _programs(A, B, ell, m, POWER_SEEDS),
           "control": _programs(A, B, ell, m, POWER_SEEDS, scip_fix=False)}  # fmt: skip
    return {**row, "failures": power_failures(row), "control_wrong": control_wrong(row)}


def _code(spec: dict) -> dict:
    """The code of a job of part (c), (d) or (e): name, l, m, A, B, the hash it is registered
    under, and its known or expected d."""
    if spec["test"] == "known":
        c = next(c for c in known_codes() if c["name"] == spec["code"])
        return {**c, "codes_sha256": _known_sha256(c), "known_d": c["d"]}
    ell, m = spec["l"], spec["m"]
    if spec["test"] == "toric":
        return {"l": ell, "m": m, "A": TORIC[0], "B": TORIC[1], "expected_d": min(ell, m)}
    c = trinomial_codes(ell, m)[spec["i"]]
    return {"l": ell, "m": m, "A": c["A"], "B": c["B"], "form": c["form"], "k": c["k"],
            "codes_sha256": _sha256(c)}  # fmt: skip


def job(spec: dict) -> dict:
    """Run one job and return its record (execute calls it in a subprocess)."""
    solver = {"solver": distance.scip_version(), "scip_fix": distance.SCIP_FIX}
    if spec["test"] == "enumeration":
        ell, m = spec["l"], spec["m"]
        codes = method_codes(ell, m)
        rows = [_enumeration_code(c, ell, m) for c in codes]
        return {**spec, "codes_sha256": _sha256(codes), "codes": len(rows),
                "agree": sum(not r["failures"] for r in rows), "rows": rows, **solver,
                **first._usage()}  # fmt: skip
    if spec["test"] == "fault":
        c = next(c for c in fault_cases() if c["id"] == spec["id"])
        A, B, ell, m = c["A"], c["B"], c["l"], c["m"]
        row = {**spec, "l": ell, "m": m, "A": A, "B": B, "k": c["k"], "known_d": c["d"],
               "codes_sha256": _sha256(c), "k_linalg": bb.k_linalg(A, B, ell, m),
               "brute": _enumerated(A, B, ell, m),
               "program": _programs(A, B, ell, m, FAULT_SEEDS)}  # fmt: skip
        return {**row, "failures": fault_failures(row), **solver, **first._usage()}
    if spec["test"] == "power":
        ell, m = spec["l"], spec["m"]
        c = power_codes(ell, m)[spec["i"]]
        return {**spec, "n": 2 * ell * m, "codes_sha256": _sha256(c), **_power_code(c, ell, m),
                **solver, **first._usage()}  # fmt: skip
    c = _code(spec)
    A, B, ell, m = c["A"], c["B"], c["l"], c["m"]
    limit = PAIR_LIMIT if spec["test"] == "trinomial" else LIMIT
    extra = {key: c[key] for key in ("form", "codes_sha256", "known_d", "expected_d") if key in c}
    return {**spec, "l": ell, "m": m, "n": 2 * ell * m, "A": A, "B": B, **extra,
            "k_linalg": bb.k_linalg(A, B, ell, m),
            "result": _instrument(spec["instrument"], A, B, ell, m, limit), **solver,
            **first._usage()}  # fmt: skip


# The worker asks Linux to kill it when the study's process dies (PR_SET_PDEATHSIG is 1), and
# exits at once if that process is already gone.
WORKER = """
import ctypes, importlib.util, json, os, signal, sys
if sys.platform == "linux":
    ctypes.CDLL(None).prctl(1, signal.SIGKILL)
    if os.getppid() != int(sys.argv[2]):
        sys.exit("the study's process is gone")
spec = importlib.util.spec_from_file_location("qec_distance_retest", {path!r})
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
print(json.dumps(study.job(json.loads(sys.argv[1]))))
"""


def _run(spec: dict) -> dict:
    """One job in its own worker process. Any failure is returned as an error row (the job is
    then not tested, and resume does not retry it)."""
    code = WORKER.format(path=str(HERE / "study.py"))
    try:
        out = subprocess.run([str(PYTHON), "-c", code, json.dumps(spec), str(os.getpid())],
                             cwd=HERE, capture_output=True, text=True, timeout=TIMEOUT)  # fmt: skip
        if out.returncode:
            return {**spec, "error": out.stderr[-2000:]}
        return json.loads(out.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {**spec, "error": f"subprocess timeout after {TIMEOUT} s"}
    except Exception as exc:
        return {**spec, "error": f"{type(exc).__name__}: {exc}"}


def execute(path: Path, workers: int) -> None:
    """Run every job without a record in `path` (a failed job's error row counts as a record).
    A file that ends with an incomplete line (a record cut off as the study's process was killed
    writing it) is refused, with the offset of that line: appending after it would join the next
    record to it. The line is no record (record_lines reads complete lines only), and once it is
    removed (the file truncated to that offset) resume runs its job again."""
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
    with ThreadPoolExecutor(max(1, workers)) as pool:
        for future in as_completed([pool.submit(_run, j) for j in todo]):
            append_records(path, [future.result()])


# ---------------------------------------------------------------- the verdict


def _by_code(rows: list[dict], test: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        if r.get("test") == test:
            out.setdefault(r["code"], []).append(r)
    return out


def _completion(codes: dict[str, list[dict]], instrument: str, expected: list[str]) -> dict:
    """A completion prediction of part (c): "holds" when that instrument completed with a d on
    every code, "fails" when it stopped at its limit (or found nothing below its bound) on one,
    and "incomplete" otherwise; with the codes it stalled on and those not tested."""
    stalled, untested = [], []
    for code in expected:
        row = next((r for r in codes.get(code, []) if r["instrument"] == instrument), None)
        if row is None or "result" not in row:
            untested.append(code)
        elif row["result"]["status"] != "complete" or row["result"]["d"] is None:
            stalled.append(code)
    verdict = "fails" if stalled else ("incomplete" if untested else "holds")
    return {"verdict": verdict, "stalled": stalled, "not_tested": untested}


def _control(records: list[dict], expected: list[str]) -> dict:
    """Part (f)'s power prediction: "holds" when SCIP's defaults were wrong at least once
    (control_wrong) in the records, "fails" when no record shows it and every code was tested,
    and "incomplete" otherwise; with the runs, the wrong ones by code, and the programs (code
    and kind) with one."""
    tested = {r["key"]: r for r in records if "error" not in r}
    wrong = {key: control_wrong(r) for key, r in tested.items()}
    wrong = {key: w for key, w in wrong.items() if w}
    if wrong:
        verdict = "holds"
    else:
        verdict = "fails" if all(key in tested for key in expected) else "incomplete"
    runs = sum(len(r["control"][kind]) for r in tested.values() for kind in distance.KINDS)
    programs = sum(len({w[0] for w in ws}) for ws in wrong.values())
    return {"verdict": verdict, "runs": runs, "wrong_runs": sum(map(len, wrong.values())),
            "wrong_programs": programs, "wrong": wrong,
            "not_tested": [key for key in expected if key not in tested]}  # fmt: skip


def decide(rows: list[dict], registered: list[dict]) -> dict:
    hashes, known = {}, {}  # the registered hashes, by code (or list) name; part (d)'s entries
    for p in registered:
        if p.get("test") == "known":
            known[p["name"]] = p
            hashes[p["name"]] = p["codes_sha256"]
        else:
            hashes.update(p.get("codes_sha256", {}))
    protocol = next(p["protocol"] for p in registered if "protocol" in p)
    specs = {j["key"]: j for j in jobs()}
    expected = list(specs)
    keys = {r["key"] for r in rows}
    missing = [key for key in expected if key not in keys]
    mismatches = []
    # every record against the registered protocol; a part (d) record against its entry
    off_protocol = {}
    for r in rows:
        spec = known.get(r.get("code")) if r.get("test") == "known" else specs.get(r["key"])
        found = protocol_failures(r, spec, protocol)
        if found:
            off_protocol[r["key"]] = found

    def registered_as(r: dict, name: str) -> None:
        if "error" not in r and r.get("codes_sha256") != hashes.get(name):
            mismatches.append(r["key"])

    # (a) and (b): one record per size, or per code
    enumeration, faults = {}, {}
    for r in rows:
        if r.get("test") == "enumeration":
            registered_as(r, r["key"])
            if "error" in r:
                enumeration[r["key"]] = ["not tested"]
            else:
                bad = {f"#{i + 1}": enumeration_failures(c) for i, c in enumerate(r["rows"])}
                bad = {i: f for i, f in bad.items() if f}
                if r["codes"] != PER_SIZE:
                    bad["codes"] = [f"{r['codes']} codes, not {PER_SIZE}"]
                enumeration[r["key"]] = bad
        elif r.get("test") == "fault":
            registered_as(r, r["key"])
            faults[r["key"]] = ["not tested"] if "error" in r else fault_failures(r)
    # (f): one record per code
    power_rows = [r for r in rows if r.get("test") == "power"]
    power = {}
    for r in power_rows:
        registered_as(r, r["key"])
        power[r["key"]] = ["not tested"] if "error" in r else power_failures(r)
    power_codes_expected = [key for key in expected if specs[key]["test"] == "power"]
    # (c): three records per code
    pair_rows = _by_code(rows, "trinomial")
    for code, group in pair_rows.items():
        for r in group:
            registered_as(r, code)
    pair_codes = [f"trinomial {ell}x{m} #{i + 1}" for ell, m in TRINOMIAL_SIZES
                  for i in range(len(trinomial_codes(ell, m)))]  # fmt: skip
    outcomes = {code: compare(group) for code, group in pair_rows.items()}
    completed = {
        code: {r["instrument"]: r["result"]["status"] in ("optimal", "complete")
               and r["result"]["d"] is not None for r in group if "result" in r}
        for code, group in pair_rows.items()
    }  # fmt: skip
    # (d): two or three records per entry, judged against the registered d
    known_rows = _by_code(rows, "known")
    for name, group in known_rows.items():
        for r in group:
            if name in known:
                registered_as(r, name)
    classes = {name: classify(group, known[name]["known_d"])
               for name, group in known_rows.items() if name in known}  # fmt: skip
    alone = {
        name: {r["instrument"]: classify([r], known[name]["known_d"]) for r in group}
        for name, group in known_rows.items()
        if name in known
    }
    entry_intervals = {}
    for name, group in known_rows.items():
        results = [x for x in intervals(group) if x is not None]
        uppers = [up for _, up in results if up is not None]
        entry_intervals[name] = (
            [max(lo for lo, _ in results), min(uppers) if uppers else None] if results else None
        )
    # (e): three records per size
    toric = {code: {r["instrument"]: toric_failures(r) for r in group}
             for code, group in _by_code(rows, "toric").items()}  # fmt: skip
    failures = {
        "enumeration": {key: f for key, f in enumeration.items() if f},
        "faults": {key: f for key, f in faults.items() if f},
        "program-search": {
            code: outcomes[code]
            for code, group in pair_rows.items()
            if outcomes[code] in ("disagree", "method error") or any("error" in r for r in group)
        },
        "toric": {
            code: {i: f for i, f in by.items() if f}
            for code, by in toric.items()
            if any(by.values())
        },
        "power": {key: f for key, f in power.items() if f},
        "known": [name for name, c in classes.items() if c in ("method error", "contradicted")],
        "registration": mismatches,
        "protocol": off_protocol,
    }
    failed = any(failures.values())
    return {
        "instruments": "fail" if failed else ("incomplete" if missing else "hold"),
        "missing": missing,
        "failures": failures,
        "enumeration": {
            "sizes": len(enumeration),
            "codes": sum(r.get("codes", 0) for r in rows if r.get("test") == "enumeration"),
            "agree": sum(r.get("agree", 0) for r in rows if r.get("test") == "enumeration"),
        },
        "faults": {
            "codes": len(faults),
            "right": sum(not f for f in faults.values()),
            "note": "a regression on known answers, not a prediction",
        },
        "program_search": {
            "outcomes": outcomes,
            "counts": {o: sum(v == o for v in outcomes.values()) for o in OUTCOMES},
            "completed": completed,
        },
        "search_completes": {
            name: _completion(pair_rows, name, pair_codes) for name in (ANCHORED, SEARCH)
        },
        "toric": {code: not any(by.values()) for code, by in toric.items()},
        "power": {
            "codes": len(power),
            "right": sum(not f for f in power.values()),
            "control": _control(power_rows, power_codes_expected),
            "control_note": "SCIP's defaults, reported beside the verdict, not in it",
        },
        "known": {
            "note": "known answers, not blind",
            "classes": classes,
            "by_instrument": alone,
            "counts": {c: sum(v == c for v in classes.values()) for c in CLASSES},
            "intervals": entry_intervals,
            "contradicted": [name for name, c in classes.items() if c == "contradicted"],
            "k_mismatches": sorted(
                {
                    r["code"]
                    for g in known_rows.values()
                    for r in g
                    if "error" not in r
                    and r["code"] in known
                    and r["k_linalg"] != known[r["code"]]["k"]
                }
            ),
        },
        "registration_mismatches": mismatches,
        "protocol_failures": off_protocol,
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
