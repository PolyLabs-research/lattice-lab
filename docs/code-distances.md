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
24 <= d <= 34**, since raised to 30 <= d <= 34 (the packing cut, below). Bravyi et al. give both distances only as upper bounds, [[360,12,<=24]] and
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
  - d = 24 for [[360,12]] was already established (Crocker, and DistQLDPC; "What the
    literature shows" below). Ours is an independent recomputation.
  - Our lower bound of 24 for [[756,16]] was below the public one of 30 (DistQLDPC).
- **What it rests on.** The lower bounds rest on the search's argument and code, the
  translation argument behind the anchors (0, lm), and the split's coverage. The tests check the
  split against enumeration, and check that the parts add up to the unsplit pass.

## The packing cut (`examples/qec-open-distance-2`)

**Result (registered, run 2026-10-23 to 24): [[756,16]] has 30 <= d <= 34.** That matches the
public state, and does not go beyond it (see "What the literature shows"). Our lower bound comes
from a second, independent implementation of the same kind of search, not from a different
method.

- **How we got there.** We asked Claude Fable whether symmetry could speed the search up
  (`consultations/2026-10-23-756-symmetry`, one call, $1.12). Its answer, checked by machine:
  - The code's automorphism group is just its 378 translations, which the search already uses.
    Our own scan of the torus maps, done before reading the answer, agrees. So symmetry gives
    nothing.
  - It proposed a stronger cut instead. Unsatisfied checks whose candidate qubits are pairwise
    disjoint each need a qubit of their own from the logical, so a branch with
    |S| + packing >= best can be dropped. The argument is the one behind the existing cut
    (search_pack.c's docstring).
  - Its other main suggestion, a Brouwer-Zimmermann bound reaching 30 in days, was wrong. The
    code has fewer than two disjoint information sets, not the 16 it assumed.
- **The registered test**, all parts passing:
  - **A1.** On 90 fresh small codes, the packing search, from (0, lm) and from every qubit,
    gave the exhaustive enumeration's d every time.
  - **A2.** On 20 fresh codes of the published form (d 6 to 18), the packing and unpacked
    searches both finished, with the same d. The cut's speedup there ranged from 0.8 (a
    little slower, on easy codes) to 4.5, the most at the largest d.
  - **B.** The packing search gave d = 12 for the gross code and 18 for [[288,12,18]], and found
    nothing below 24 for [[360,12]], in 8 minutes against study 1's 1.9 hours.
  - **C.** On [[756,16]], passes up to 29 found nothing, in 7 hours on 4 cores. So d >= 29, and
    d >= 30 since d is even. Study 1's search needed 2.4 hours for d >= 24. The packing search
    reached 24 in under 3 minutes. Its passes grew at almost the same rate per bound (about 2.8,
    against 2.9 at bounds 21 to 24), so the cut's gain is a roughly constant factor, about 50.
- **The run stopped early, disclosed.** A restart of the session's worker ended the run during the
  pass at 30. That pass cannot change the result (d is even), so it was not resumed. The study's
  rules, applied to the records, give "hold" on every part (`judged-after-stop.json`). The ledger
  itself has no verdict entry (`STOPPED.md`).
- **What it rests on.** The search's argument and code, the translation argument, the split's
  coverage, and the packing argument. A1, A2 and B test the cut on codes it was not developed on.

## What the literature shows (checked 2026-10-24, after both studies)

We read the sources directly only after both studies had run, so that the runs stayed blind. arXiv
could not be reached from this session, so the papers were read through search summaries. The
primary data are two public repositories, cloned and read as data.

- **[[756,16]].**
  - **Lower bound 30, from DistQLDPC** (github.com/guluchen/DistQLDPC, v1.0 of 14 Oct 2026).
    Its rename log (`data/matrices/README.md`, at commit e52d15ba of 2026-10-23) records:
    - lb 28 on 2026-10-21: "single canonical search, not cross-validated by a second method";
    - lb 30 on 2026-10-22: "reproduced with relabeled seeds ... same algorithm, not a second
      method". Its report (GH-138) calls the bound "PLAUSIBLE pending PI review".
  - **Upper bound 34.** Witnesses come from Bravyi et al. and from Webster, Jacob and Higgott
    (2026). DistQLDPC also verified one, on 2026-10-23.
  - **No published lower bound** before DistQLDPC's, by DistQLDPC's own literature survey.
  - **Webster, Jacob and Higgott** (arXiv:2603.22532; their `paper results` spreadsheets): every
    exact method (Gurobi, SCIP, Magma, CLISAT, dist-m4ri's cluster search) ran out its 8-hour
    limit on this code, and on [[360,12]], recording upper bounds only.
- **[[360,12]].** d = 24 exact by C. Crocker (Zenodo, 13 Oct 2026, two programs) and by
  DistQLDPC's cluster engine (about 1,700 s), before our study 1.
- **How our result relates.**
  - DistQLDPC's cluster engine is the same kind of search as ours: a check-driven cluster search,
    level by level, from translation-orbit anchors.
  - Its default rules already include the disjoint-check packing bound (`pack`, since
    2026-10-15), which is our packing cut. Crocker and Lee (arXiv:2610.06820, 5 Oct 2026) use
    one too. It also adds a parity rule (odd levels skipped: our "d is even") and a
    stabilizer-overlap rule from Lee, which cut its time to lb 28 about fourfold.
  - So our d >= 30 is a second, clean-room implementation of that method, with registered tests
    on fresh codes. It is not a different method: a fault common to the method would affect both.
  - Its value is to check DistQLDPC's code, which its own log says no second implementation had
    done.

## Next

1. **Done:** both instruments fixed and retested (above).
2. **The census of code families** (step 2 of next-direction.md), with the search for exact
   distances, the program as a cross-check, and both together where a code is hard. Stage 1 is
   done ([code-census.md](code-census.md)), and stage 2 is being registered.
3. **Done: the open distances of larger published codes** (above): [[360,12]] has d = 24;
   [[756,16]] has 30 <= d <= 34.
4. **[[756,16]] beyond 30.** The packing search's pass at 31 (which would show d >= 32, or find a
   weight-30 logical and settle d = 30) is estimated at about 33 hours on 4 cores, and the pass
   at 33 (for d = 34) at about ten times that. DistQLDPC is working on this code too, with a
   stronger rule set.
