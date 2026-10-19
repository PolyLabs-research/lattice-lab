# Log: the m = 37 pilot

The orchestrator's record of the fourth LLM-central pilot, in order. The write-up is
[docs/llm-pilot.md](../../docs/llm-pilot.md).

## What is new in this pilot

The first three pilots asked for theorems whose answers were known, at least to the
orchestrator. This one asks an **open question**: why do some of the atlas's rules have every
eigenvalue a cube at m = 37? No one knows, the orchestrator included. So there is no pinned
statement. The agent submits a mechanism as code, `condition(f, m)`, returning q > 1 when its
mechanism proves that every nonzero eigenvalue of f at m is a q-th power, and a proof in
`proposal.md` (and Lean, optionally). The judge checks the claims rather than a theorem:

- **explains**: what `condition` says about the six unexplained rules at 37;
- **sound**: `condition` runs on all 1,274 rules at every m of the census and of a held-out grid;
  every claim is checked with the orchestrator's own eigenvalue computation (`census.confined`).
  One false claim refutes the mechanism as stated;
- **reach**: how many true claims, how many beyond the known mechanisms, and how many census
  entries they cover, at sizes the agent has and at sizes it has not seen.

The agent hears back only about the library, Lean, `condition` failing to run, the six, and false
claims at m ≤ 161; never the held-out grid.

## Before the pilot: the census

The question was sharpened first. `census.py` checks, for every shell rule of the three lattices
(1,274; `atlas3.all_rules`) at an odd m with ord_m(2) even, whether every nonzero eigenvalue is a
cube, and whether the known mechanisms account for it (`atlas3.predict`'s splitting, powers and
dilations, plus round 3's twisted power, which `predict` does not include). `run_census.py` ran it
at every such m from 9 to 161 (`census-train.jsonl`).

- **At m = 37, six rules are unexplained**, not two: square A4 + K8 + B4 + self and triangle
  VS + T9 + T13 + self, known from rounds 2 and 3, and square K8 + M8 + E4, C4 + L8 + M8,
  C4 + L8 + M8 + E4 and A4 + B4 + C4 + L8 + E4 + self, which no round had tested at 37.
- Up to Frobenius conjugacy they have 9 to 11 distinct nonzero eigenvalues each (the write-up's
  "172" for the first counted conjugates separately), so chance would confine each about once in
  20,000 to 180,000. Each has odd part exactly 87381 at 37 and the full bound at every other odd m
  from 9 to 161.
- Below 37 the census holds the small-field coincidences (51 rules at m = 13, 6 at 21, 4 at 25).
  Above 37 it holds single rules: K8 + M8 + self at 29, triangle E + VO + T7 + T9 + self at 21 and
  69, N4 + D4 + B4 + C4 at 115, and VO + T13 wherever the twisted power applies, which is
  explained and dropped from the data.

## Setup

- **The census** finished over all 65 sizes from 9 to 161 in 52 minutes. `data/unexplained.csv`
  holds its 69 unexplained entries, after dropping VO + T13's, which the twisted power explains.
- **The tools** (`tools/eigen.py`) agree with the census: odd part 87381 for A4 + K8 + B4 + self
  and VS + T9 + T13 + self at 37, the full bound 262143 for N4 + B4, and all cubes for
  K8 + M8 + E4.
- **The judge** was tested with a toy mechanism (perfect cubes, plus planted false claims at
  m = 41): true claims held and counted as known mechanisms, all 16 planted false claims were
  caught, and the six were correctly not explained.
- **Registered** before the launch: the held-out grid, 29 sizes (163 to 225 with ord_m(2) even,
  and 259 and 333), with the orchestrator's expectation of no unexplained confinement there
  (`ledger.jsonl`).
- **The sandbox** is commit `b79238c0ac07` (`base.txt`), pushed as `pilot-sandbox-37` and `pilot-37-submission`. It has
  29 protected files, and no pinned statement.
- **The judge, round 0**, on the base: library unchanged, no mechanism yet, no Lean changes
  (`judgements/round-0.json`).
