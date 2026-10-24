# Census stage 3b: independent spot-check of the frontier distances (plan)

**Status: a plan, committed before any of it runs.** It is not part of stage 3b's registered
verdict. It is reported beside it, and its sample rule and pass criteria are fixed here so that
the sample cannot be chosen after the fact.

## Why

Every exact distance in stages 3a and 3b comes from one method family: the check-driven search
(search.c, with the split and the packing cut). That search has been tested against exhaustive
enumeration, against itself without the cut, and on known codes. But no second, independent
method confirms the large frontier values (d >= 16). A flaw shared by every version of the search
would go unseen. This check targets that gap on a fixed sample.

## The sample (fixed now; drawn from the records after the run)

From the judged tori (RANDOM and EXTRAPOLATION) with connected classes:

1. **The top code of each of the 6 largest-n tori with codes.** For each, the class achieving the
   best connected d at the torus's smallest k (its d_max code), the first in record order if
   several tie.
2. **Both P2 counterexamples' groups:** the d_max code of 2 x 51 ([[204,4,20]]) and of 3 x 40
   ([[240,4,22]]), plus any later torus whose d_max exceeds P2's cap, up to 4 in all.
3. **6 more frontier codes drawn at random** with `random.Random("qec-census-3b spot-check")` from
   all (torus, k) frontier entries with d >= 14, where the entry's code is the first class in
   record order with that best d.

So between 12 and 16 codes, with the frontier's settled d as the value being checked.

## The checks

For each sampled code (A, B on its torus):

- **C1, the integer program** (distance_ilp, SCIP with SCIP_FIX, kind Z, 2 hours). This is the
  only exact route in the project that shares no code with the search: an LP-based branch and
  bound. Its interval [dual bound, best witness] must contain the search's d. The program rarely
  finishes at d >= 16 at these sizes, so it is mainly a check that no lighter logical exists
  below its dual bound, and that its witnesses are not lighter than d.
- **C2, the unpacked search from every qubit** (study 1's search_parts.c, deepening, all anchors,
  2 hours). This removes both the packing cut and the translation argument (anchors (0, lm)). It
  shares only the core search with the instrument it checks. If it completes, its d must equal
  the frontier d; if not, its lower bound must not exceed d.
- **C3, the other kind** (the packing search, kind X, deepening from (0, lm)). By d_X = d_Z for
  every bivariate bicycle code, it must give the same d. That checks the implementation on a
  different matrix.
- **C4, a long window** (random information sets, 8 seeds of 15 minutes, kind Z and X). It must
  find no logical lighter than d. A lighter one would refute the search's lower bound outright.

## What counts

- **Agreement:** every check is consistent with the frontier d, meaning intervals contain it,
  completed runs equal it, and nothing lighter is found.
- **A contradiction** in any check (a completed value other than d, or a verified logical lighter
  than d) is a finding against the instruments. It is reported against stage 3b's frontier and
  examined before any claim built on it stands.
- **Reported, not judged:** how many C1 and C2 runs finish within their limits.

## Cost and order

- **When:** after stage 3b's run ends, so the two do not compete for the 4 cores.
- **How long:** at most about 16 codes x (2 h + 2 h + under 1 h + 1 h). That is roughly 1 to 1.5
  days at 4 workers; most C3 and C4 runs are short.
- **Ordering:** if time is short, C4 and C3 come first, because they are cheap and can refute. C1
  and C2 follow.
- **Outputs:** records go to `examples/qec-census-3b/spotcheck/`. The write-up reports them
  beside the registered verdict.
