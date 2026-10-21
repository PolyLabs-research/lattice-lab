# Code distances: the published bivariate bicycle codes, reproduced

**Result (registered test `examples/qec-distance`, run 2026-10-21): all 12 published distances
are reproduced.**
- **How.** An exhaustive search written for this project reproduced every one exactly. The
  integer program agrees on 11 and brackets the twelfth.
- **The method prediction failed once.** On 1 of 200 random test codes, the integer program,
  solved by SCIP, reported a wrong optimum. So the program alone is not trusted as a proof of a
  lower bound, and the published distances rest on the search.

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

## What this establishes

- **The published distances.** All twelve, including d = 18 for [[288,12,18]], hold by an exact
  method built here and checked independently, run blind to the published values. The gross
  code's distance takes the search 0.2 s.
- **The tools.** The search is the fast instrument on codes like these. The program is useful for
  upper bounds and, with the fault fixed and retested, for lower bounds where the search stalls.
- **Not established.** The search's lower bounds rest on its argument and its code, which part 1
  checked against other methods but which nothing certifies independently. And the codes.json
  entries are still transcriptions from search summaries of the papers, now consistent with
  both their published k and their published d.

## Next

1. **Fix both instruments, then register them again on fresh codes.**
   - The program: run SCIP without dual reductions. That gave the right answer at every seed on
     the failing code; its cost on large codes is to be measured.
   - The search: iterative deepening of its bound.
2. **The census of code families** (step 2 of next-direction.md), with the search for exact
   distances and the program for bounds.
