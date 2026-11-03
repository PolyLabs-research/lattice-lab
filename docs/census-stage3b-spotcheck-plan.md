# Census stage 3b: independent spot-check of the frontier distances (plan)

**Status: a plan, committed before any of it runs, and amended twice before any of it ran: first
to add C5, C6 and the tiers, then (2026-10-29, after the census's results, see the end) to fix
the sample rules exactly and add four codes.** It is not part of stage 3b's registered verdict. It is reported beside it, and
its sample rule and pass criteria are fixed here so that the sample cannot be chosen after the
fact.

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
- **C5, another implementation, two methods: DistQLDPC** (github.com/guluchen/DistQLDPC, at the
  commit cloned when the check starts, recorded). Its matrices are built from our A and B in its
  input format (Hx, Hz, logical bases), with the code's k checked on the way in. Two engines, each
  with a 2-hour limit:
  - its cluster engine, a clean-room implementation of the same kind of search;
  - its MaxSAT engine, a different method, a constraint solver.
  Each result (exact d, or certified lower and upper bounds) must be consistent with ours.
- **C6, proof certificates: SAT with DRAT.**
  - **Claim:** "no Z-logical of weight <= d - 1" is encoded as CNF and given to a solver that
    writes DRAT proofs (CaDiCaL). The encoding has a variable per qubit, each check as an XOR
    split by Tseitin, "some X-logical has odd overlap" over a basis of the X-logicals, and a
    sequential-counter cardinality bound.
  - **Certificate:** the solver's UNSAT answer is checked by drat-trim, built from source. The
    claim then rests only on the encoding and the checker.
  - **Testing the encoding:** before use, it is tested against exhaustive enumeration on small
    codes (UNSAT exactly below d, SAT at d, with the SAT model a verified logical).
  - **Which codes:** the sampled codes with d <= 16, plus the frontier codes with 12 <= d <= 16 on
    the 6 smallest judged tori with codes. Each claim has a limit of 4 hours. With d even, UNSAT
    at weight d - 1 certifies d.

## The tiers the write-up reports

Each frontier distance in the sample is reported at the highest tier its checks reach:

- **certified:** a DRAT proof of "nothing below d", checked by drat-trim, plus a verified witness
  of weight d;
- **confirmed by a second method:** SCIP (C1) or DistQLDPC's MaxSAT engine (C5) reaches d;
- **confirmed by a second implementation:** DistQLDPC's cluster engine (C5) or C2 reaches d;
- **search only:** none of the above finished. The value rests on the search, with C3 and C4
  having found no contradiction.

## What counts

- **Agreement:** every check is consistent with the frontier d, meaning intervals contain it,
  completed runs equal it, and nothing lighter is found.
- **A contradiction** in any check (a completed value other than d, or a verified logical lighter
  than d) is a finding against the instruments. It is reported against stage 3b's frontier and
  examined before any claim built on it stands.
- **Reported, not judged:** how many C1 and C2 runs finish within their limits.

## Cost and order

- **When:** after stage 3b's run ends, so the two do not compete for the 4 cores.
- **How long:** about 16 codes x (2 h + 2 h + under 1 h + 1 h + 4 h), plus the C6 claims. That
  is roughly 2 to 3 days at 4 workers; most runs end well before their limits.
- **Ordering:** if time is short, C4 and C3 come first, because they are cheap and can refute.
  C6 follows, because it gives certificates, then C5, then C1 and C2.
- **Outputs:** records go to `examples/qec-census-3b/spotcheck/`. The write-up reports them
  beside the registered verdict.

## Amendment 2 (2026-10-29): exact rules, four added codes, the machine

Written after stage 3b/3c's results were known (docs/code-census.md) and before any check ran.
The runner is `examples/qec-census-3b/spotcheck/run.py` (`sample`, `run`, `judge`), tested in
`tests/test_qec_census_3b_spotcheck_run.py`.

**The rules, made exact.** The text above left some choices open. They are fixed as follows,
and the runner applies them.

- **Records and order.** Stage 3b's records, then stage 3c's, in file order. Judged tori are
  those in groups random and extrapolation that have codes and no error.
- **A code's value.** It is the code's own exact distance, meaning the search finished on that
  class (exact.status "complete"). This holds whether or not the torus's frontier was settled.
- **The d_max code.** At the torus's smallest connected k, take the first class in record order
  whose exact d equals the torus's best connected d at that k.
- **Rule 2.** The P2 counterexamples are now 7 tori. These fall into 4 isomorphism classes of
  Z_l x Z_m:
  - Z_102: 2 x 51 and 3 x 34;
  - Z_120: 3 x 40, 5 x 24 and 8 x 15;
  - Z_123: 3 x 41;
  - Z_3 x Z_48: 3 x 48.

  "Up to 4 in all" is applied as one torus per class, the first in record order. That gives
  2 x 51, 3 x 40, 3 x 41 and 3 x 48.
- **Rule 3.** The frontier entries are each (torus, k) with best connected d >= 14, in record
  order and then by k. Each entry's code is the first complete class with that d. Entries whose
  code is already drawn are dropped. Then `random.Random("qec-census-3b spot-check").sample`
  draws 6 of them.
- **Rule 1 redundancy, disclosed.** The 6 largest-n tori include 2 x 75, 3 x 50 and 6 x 25,
  which are all Z_150. The rule was fixed beforehand, so they stay in the sample.

**Four codes added (rule 4).** These are the codes the write-up leans on:

- the two P3 counterexamples, [[294,10,20]] on 3 x 49 and on 7 x 21;
- the two highest extrapolation scores on 288 qubits, [[288,8,22]] on 3 x 48 and [[288,12,18]]
  on 4 x 36.

They were chosen after the results, for that reason. They add to the sample and replace
nothing.

**The sample this gives** (`run.py sample`): 20 codes, all of their d's settled by the search.
- 6 largest n: [[300,4,24]] on 2 x 75, 3 x 50, 5 x 30 and 6 x 25; [[294,4,22]] on 3 x 49;
  [[294,4,24]] on 7 x 21;
- P2: [[204,4,20]] on 2 x 51; [[240,4,22]] on 3 x 40; [[246,4,22]] on 3 x 41; [[288,4,24]] on
  3 x 48;
- random: [[192,8,16]] on 2 x 48; [[210,10,16]] on 5 x 21; [[282,4,22]] on 3 x 47;
  [[270,8,20]] on 5 x 27; [[240,8,18]] on 8 x 15; [[252,10,16]] on 2 x 63;
- added: the four above.

C6 runs on the 3 sampled codes with d <= 16 and on 8 frontier codes with 12 <= d <= 16 from the
6 smallest judged tori. In all there are 431 jobs.

**How each check is run.**

| Check | Kinds | Instrument | Settings | Limit |
|---|---|---|---|---|
| C4 | Z and X | window.c | seeds 0–7, one job per (kind, seed) | 900 s each |
| C3 | X | packing search | from (0, lm), 1 part | 2 h |
| C2 | Z | search_parts.c (no cut) | every qubit as anchor, 1 part | 2 h |
| C1 | Z | distance_ilp | translation row, SCIP_FIX | 2 h |
| C5 | — | DistQLDPC, cc and maxsat engines | — | 2 h each |
| C6 | — | sat.certify at weight d − 1 | anchors (0, lm); the census's witness of weight d checked by verify_witness | 4 h for CaDiCaL, then drat-trim |

- **C5's DistQLDPC commit.** The pod clones DistQLDPC's current head at its first start, as the
  plan says. It records the commit in `spotcheck/distqldpc-commit.txt` and checks that commit out
  at every later start. The runner was tested with e52d15baa7a430104329d20467c12375fe60f0f2.
- **C5's bounds.** These are DistQLDPC's last `c d_lb:` and `c d_ub:` lines. When the cc engine
  withdraws its bounds, they count as none. Any exit other than 0 (solved) or 1 (stopped) is an
  error.
- **C6's proofs.** CaDiCaL writes binary DRAT. Both CaDiCaL and drat-trim run under their own
  time limits. A proof over 8 GB is not checked (drat-trim holds it in memory), so the claim is
  "unverified".
- **The logical counts.** C1 and C6 check that the number of logicals they use equals the
  code's k.

**What counts, made exact** (`run.py assess`):

| Check | Consistent with d when | Contradicts d when | Reaches d when |
|---|---|---|---|
| C4 | its lightest logical has weight ≥ d | it finds a lighter logical | never |
| C2, C3 | an unfinished run's lower bound is ≤ d | a finished run returns a d other than d | a finished run returns d |
| C1 | [lower, upper] contains d | the interval excludes d (with SCIP's solution a verified logical), an optimal value other than d, or "infeasible" (the census's witness is feasible) | SCIP's optimal value is d |
| C5 | [lower, upper] contains d | the interval excludes d, or an exact value other than d | an exact value equal to d |
| C6 | — | the SAT model is a verified logical of weight ≤ d − 1, or the census's witness fails | a drat-trim-verified UNSAT plus the witness verified at weight d |

- **C6 with no conclusion.** A time limit, or a proof drat-trim does not verify (including
  drat-trim running out of time or memory), concludes nothing either way.
- **Errors.** A job that errors is reported, and is not counted as agreement.
- **Agreement overall** needs all three: a record for every job, no errors, and no
  contradiction.
- **A fault in a tool is not evidence about d.** If SCIP's solution is not a logical, or a SAT
  model is not a logical, that job concludes nothing. It is flagged in the judge's notes.
- **The tiers** are as above.

**The machine.** A RunPod CPU pod: compute-optimized, 32 vCPU, on-demand, with a 300 GB container
disk for the DRAT proofs. It runs `examples/qec-census-3b/spotcheck/pod-run.sh`, which commits
records to the branch.

- **Concurrency.** Up to 32 jobs run at once. At most 6 are integer programs (memory) and at
  most 3 are SAT claims (proof disk).
- **Isolation.** Each job runs in its own process. A process that dies without a result, out of
  memory say, is run again up to twice, then recorded as an error. Each job has its own process
  group, which is killed when the job ends, so no tool outlives its job.
- **Speed matters.** The limits are wall-clock, so a faster machine finishes more runs. The
  write-up gives the hardware.
