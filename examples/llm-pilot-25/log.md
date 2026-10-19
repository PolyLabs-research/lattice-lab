# The m = 25 pilot: log

The fifth LLM pilot, and the second on an open question. Its question comes from the census
remainder (docs/census-remainder.md): at m = 25, three atlas rules and 14 of the 32,767 symmetric
square rules within distance 4 are confined to the cubes, against 0.24 and 1.7 ± 1.3 expected by
chance, and nothing known explains them.

## Design

The harness is the m = 37 pilot's (examples/llm-pilot-37), with these changes:

- **The data** add the square family (tools/family.py): its confinements at m = 21 and 25
  (data/family21.json, data/family25.json), the census remainder with the orchestrator's verdict
  on each entry (data/remainder.csv), the chance model's counts (data/expected.csv), and the
  m = 37 pilot's proposal (data/pilot4.md).
- **The tools** add the family, the forced-subfield and chance analysis (tools/chance.py, a
  self-contained copy of census-remainder/remainder.py's method), and the m = 37 pilot's
  `condition` as submitted (tools/halffrob.py).
- **The card** states what has been checked, including one observation the orchestrator could
  not test, marked as such: 25 has 37's arithmetic (2^5 = 7, 7^2 = -1 mod 25), and a pair of
  rule-90 factors along w and 7w has a cube for its eigenvalue. Checking the card before the
  launch caught one wrong line: five of the 14 family rules do share a factor,
  (1 + x + x^2)(1 + y + y^2), and two others another. The card says so.
- **The judge** (judge.py) runs `condition` on the atlas's 1,274 rules at the census sizes and
  at the m = 37 pilot's held-out sizes (94 in all), and on family rules (a fixed sample of 2,000
  and every known confinement) at m = 21, 25 and this pilot's held-out sizes. Every claim is
  checked by the orchestrator's eigenvalue computation. **Explains** is the 17 rules at 25.
  Tested before launch with a toy mechanism (the m = 37 pilot's condition, plus a planted false
  claim for N4 at 25): the false claim was caught, none of the 17 was explained, and the family
  check ran 2,012 rules at 25 in 21 seconds.
- **The registered test** (study.py, `ledger.jsonl`, pushed in `3cf8530` before any run at
  these sizes): the family's census at the 14 odd m from 27 to 75 where the cubes are a proper
  subgroup, with the orchestrator's expectation that what remains there is chance (at most the
  model's expected count + 3 sd + 1 at each size). Each confined rule is also put to the m = 37
  pilot's condition, and those it explains are counted apart. Seen pairs are declared: the
  atlas's square rules at every size (the remainder sweep) and a random 1,500 family rules at
  m = 29 (the calibration). The first registration commit (`7cf242a`) failed on an import order
  and held no ledger; `3cf8530` has it.

## Setup

- **The sandbox**: commit `5c231204be72` (`base.txt`), pushed as `pilot-sandbox-25` and
  `pilot-25-submission`; 36 protected files, no pinned statement. Its tools ran in the sandbox
  before the launch.
- **The judge, round 0**, on the base: library unchanged, nothing submitted
  (`judgements/round-0.json`).
- **The held-out census** started as soon as the registration was pushed.

## Launch

- **16:42:17 UTC.** The agent's session, `session_01Ksrsh7wMG2nHAELuaMo8jS`, was created from
  `pilot-sandbox-25` at depth 1, in its own container, with the prompt in `prompt.md`, verbatim,
  and asked to push to `pilot-25-submission`. A watcher polls that branch for `report.md`.
