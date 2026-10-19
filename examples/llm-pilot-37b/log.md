# The sixth pilot (the square family at m = 37): log

The sixth LLM pilot, and the third on an open question. Its question comes from the fifth
pilot's registered census (examples/llm-pilot-25): at m = 37, 16 of the 32,767 symmetric square
rules within distance 4 are confined to the cubes that neither the fourth pilot's half-Frobenius
condition nor the fifth pilot's certificates explain, against 0.62 ± 0.79 expected by chance, and
three of them are also confined at m = 61.

## The pre-check

Before writing the card, the orchestrator checked that the 16 are not just beyond the two
conditions' search bounds (scratch scripts, results in the card):

- **At their own bounds**, neither condition makes a claim for any of the 19 targets (16 at 37,
  three at 61), and both explain known rules at 37 (family rules 57, 448 and 745, for example).
- **Wider bounds**: the half-Frobenius condition with up to four rule-90 orbit products of radius
  up to 3, and units up to radius 4 with Ψ_e for e ≤ 39; the certificate condition with
  multipliers of radius up to 3, Ψ_e for e ≤ 13, exponents up to 8q, and twisted-pair factors from
  orbits up to radius 3. Nothing. Products of two multipliers at radius 3 were too slow (19
  minutes on one rule without a result) and were stopped; at the fifth pilot's own radius, two
  multipliers give nothing.
- **Images**: confinement at m is invariant under GL2(Z/m) acting on exponents. Each of the 16
  has 264 distinct images under the 2,112 invertible maps with entries in [−3, 3]; neither
  condition explains any of them.
- **Symmetries**: in the whole of GL2(Z/37), and of GL2(Z/61) for the three, each rule's support
  has only the lattice's 8 symmetries. So 9 or 10 free classes each at 37 (chance 1.7 to 5.1 in
  100,000) and 16 at 61 (2.3 in 100 million).
- **Arithmetic**: at 37 rule 90 is confined (odd part 87,381) and every proper subfield of
  F(2^18) lies in the cubes; at 61 rule 90 is not confined (odd part the full bound,
  2^30 − 1) and F(2^6) is not in the cubes.

## Design

The harness is the fifth pilot's, with these changes:

- **The tools** add the fifth pilot's `condition` as `tools/certificate.py`, verbatim (it calls
  `halffrob.condition`, so it carries mechanism 5 too).
- **The data** (make_data.py) are the family's census at every size computed so far (21, 25 and
  the fifth pilot's 14 registered sizes from 29 to 75), each confined rule marked with what both
  earlier conditions prove; the 19 targets with their symmetries and chance; and both earlier
  proposals.
- **The judge** (judge.py) explains = the 19 targets; soundness on the atlas at 94 sizes as
  before, and on family rules (a fixed sample of 2,000, seed 37, and every unexplained
  confinement) at the 16 training sizes and the 17 registered held-out sizes.
- **The registered test** (study.py): the family's census at the 17 odd m from 77 to 125 where
  the cubes are a proper subgroup, with both earlier conditions counted as known. The
  expectation is chance again: at most expected + 3 sd + 1 at each size. Rules the atlas
  procedure finds to split are counted apart, since its split step mispredicts correlated
  factors (the m = 115 entry of the census remainder); none of the targets splits. The run warms
  the procedure's caches at m = 21, a seen size, then forks three workers.
- **The audit** also allows the output files of the session's own background commands, which
  the fifth pilot's audit flagged five times and the card now permits.

## Setup

- **The sandbox**: commit `ed7db10b6a9f` (`base.txt`), pushed as `pilot-sandbox-37b` and
  `pilot-37b-submission`; 37 protected files, no pinned statement. Its tools ran in the sandbox
  (target 1112: odd part 87,381 at 37, no claim from either condition; rule 57: explained).
- **The judge, tested before launch** with a toy mechanism (the fifth pilot's condition plus a
  planted false claim, N4 confined to the cubes at 61): the false claim was caught, none of the 19
  was explained, and the family check ran 2,015 rules at 37 in 32 seconds.
- **The registration** (`ledger.jsonl`, pushed in `461477e` before any computation at these
  sizes). A dry run of the census code at seen sizes (35, 37, 61, on a subset of the family)
  checked it first. One phrase of the registered question is loose: the atlas's square rules are
  "confined only at 37 and 115 among these sizes", where 37 is not among the grid's sizes; among
  the census sizes is meant.
- **The judge, round 0**, on the base: library unchanged, nothing submitted
  (`judgements/round-0.json`).
- **The held-out census** started at 21:51 UTC, detached (`nohup`), with three workers.

## Launch

- **21:51:40 UTC.** The agent's session, `session_018qfyPPSsY668o93hfGivki`, was created from
  `pilot-sandbox-37b` at depth 1, in its own container, with the prompt in `prompt.md`, verbatim,
  and asked to push to `pilot-37b-submission`. A watcher polls that branch for `report.md`.
