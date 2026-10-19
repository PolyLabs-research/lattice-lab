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

## Launch

- **06:40:26 UTC.** The agent's session, `session_01WGk9TPzDv4NH9NkB6zczhr`, was created from
  `pilot-sandbox-37` at depth 1, in its own container, with the prompt in `prompt.md`, verbatim,
  and asked to push to `pilot-37-submission`.
- The held-out census (the registered study) started at the same time, in the orchestrator's
  container.

## The run

The agent's own messages are in `transcript/messages.md`; its tool calls in
`transcript/tool_calls.jsonl`, read from the server-side transcript.

- **06:42.** It restated the question: t in F(2^18) is a cube exactly when its norm to F_4 is 1.
- **06:50 (10 minutes in).** It found that four of the five square rules are
  W = A4 + K8 + B4 + self times rule-90 products: K8 + M8 + E4 = ab W, C4 + L8 + M8 = (a + b) W and
  A4 + B4 + C4 + L8 + E4 + self = (a + 1)(b + 1) W, with a = x + 1/x and b = y + 1/y. No round of
  the atlas had looked for factors shared between rules.
- **07:03 (23 minutes in).** Its `condition` explained all six at 37. The mechanism, which it calls
  **half-Frobenius confinement**: at 37, 2^9 ≡ −6 and 6² ≡ −1, so the dilation (x, y) ↦ (x^6, y^6)
  acts on eigenvalues as the Frobenius x ↦ x^(2^9). A polynomial whose support mod 37 is invariant
  under it has every eigenvalue in F(2^9), and 3 does not divide 2^9 − 1, so every element of
  F(2^9) is a cube in F(2^18). None of the six is invariant, but each becomes invariant after
  multiplying by rule-90 factors, whose eigenvalues are cubes at 37:
  W(x², y²) t(x) t(y) t(xy) t(x/y) is the eight-cell shell (±7, ±5), (±5, ±7), and ×6 maps it to
  itself mod 37. V = C4 + L8 + M8 + E4 and the triangle rule have identities of the same kind.
- **07:09 to 07:16.** `mechanism.py`, `proposal.md`, `proposal.py`; a sweep of `condition` over all
  1,274 rules at every odd m from 9 to 301, each claim checked by eigenvalues (838 claims, none
  false, by its count).
- **07:44 to 08:05.** Lean, once its mathlib build finished: `period 37 D ∣ lcm(511, period 37 r90)`
  for W (07:47), the five square rules (07:52) and the triangle rule (08:05), on the standard
  axioms. Rule 90's period at 37 was an input, not proved.
- **08:14.** `report.md` pushed (`ace49c5`); the watcher saw it at 08:15:31, 95 minutes after
  launch.
- **08:23:49.** The session received a message the orchestrator did not send: "Prove rule 90's
  cube property at 37 in Lean too". The server records that turn's origin as a person; it was
  typed in the Claude app. The agent proved `period_r90_dvd : period 37 r90Offsets ∣ 87381` with an
  explicit cube root: Φ_37 is irreducible over GF(2), so t = z + 1/z generates F(2^18), and
  v(t) = t^15 + t^13 + t^12 + t^11 + t^9 + t^7 + t^6 + t satisfies v(t)³ = t (a certified identity).
  With 511 | 87381 it then proved `period 37 D ∣ 87381` for all six, unconditionally, and pushed at
  08:42 (`6151adb`). Its first Lean build of the new part succeeded.

The session made 137 tool calls (133 Bash, 4 Write) and cost about USD 16.6 in all.

## The judge, round 1 (`ace49c5`, the report as first submitted)

`judgements/round-1.json`. The library was unchanged, and:

- **Explains the six:** `condition` returns q = 786435 = 3 (2^18 + 1) for each at 37, which says
  every eigenvalue is a cube in F(2^18). (In F(2^36), q = 3 alone would be true of every rule at
  37, since F(2^18) lies in the cubes of F(2^36); the agent noticed this and chose the stronger
  q. The judge's test, q > 1 and 3 | q, passes either way.)
- **Sound:** 453 claims at the 65 training sizes and **180 at the 29 held-out sizes, none false**,
  each checked by the judge's own eigenvalue computation. 30 of the training claims are
  confinements the four known mechanisms do not explain; at the held-out sizes it made no such
  claim.
- **Census:** it covers 24 of the 69 unexplained entries, the six at 37 and 18 of the 51 at 13
  (the pure case there: invariance under ×8 or ×4, so eigenvalues in F(8) or F(4)).
- **Lean:** `Pilot.lean` builds against the real library (988 s). The axiom listing came back
  empty: a judge bug. It printed axioms for `LatticeProofs.<name>`, and the agent's theorems are
  in `namespace LatticeProofs.Pilot`. Fixed (`declared` reads the namespaces), and the listing is
  in round 2.
- **The agent's own checks** (`proposal.py`): 39 of 39 held.

No feedback was sent; the agent had finished.

## The audit

`transcript/audit.json`, over all 137 calls:

- no MCP tools, no web search or fetch, no subagents;
- no fetch, listing or reading of other branches or repositories. One `git merge-base HEAD
  origin/pilot-sandbox-37` names the agent's own source branch, which it was given;
- **one step outside the checkout**: at 07:19:30 a `find / -maxdepth 8 -name CharP`, looking for
  mathlib's sources. It found nothing, and the agent then used the copy in `proofs/.lake`. It
  reported this itself in `report.md`;
- 28 more flags are false positives: Lean comment markers (`/-`, `/--`), divisions such as `/3`
  in Python, and `sed` and `awk` patterns read as paths;
- the inputs (`transcript/inputs.json`): the prompt, four task notifications, one stop-hook
  message, and the person's message at 08:23.

## The orchestrator's own check

The identities were checked again with the atlas's own polynomials (`atlas3.polynomial`), not the
agent's code: W(x², y²) t(x) t(y) t(xy) t(x/y) is exactly the shell (±7, ±5), (±5, ±7); the three
factorisations through W hold; the shell is invariant under ×6 mod 37; and `eigen.odd_part` gives
87381 for W and 511 = 2^9 − 1 for the shell at 37.

## The registered held-out census

The study (`study.py`) stopped at the two-hour limit after 20 of its 29 sizes and was resumed
(`run_resumed` in `ledger.jsonl`). It finished at about 09:30 UTC. **At all 29 held-out sizes,
from 163 to 333, no shell rule has unexplained cube confinement**: the orchestrator's registered
expectation is supported, and `lattice-lab verify` finds no problems. Most sizes took seconds or
a few minutes; 163, 179, 201, 209 and 211 took 16 to 48 minutes each.

This agrees with the agent's mechanism: it predicts the mixed case only at 37 among the atlas's
rules, and its 180 claims at these sizes were all confinements the known mechanisms explain.

## Into the library

The final `Pilot.lean` is `proofs/LatticeProofs/Cubes37.lean`, verbatim except for its namespace
(`Pilot` became `Cubes37`), and a root in `lakefile.toml`. `lake build` took 12.6 minutes, and
`Axioms.lean` shows only the standard three axioms for `period_r90_dvd` and the six
`period_*_dvd_87381`. `tests/test_cubes37.py` checks the identities with the atlas's own
polynomials, the six rules' odd parts at 37, and the study's ledger.

## The judge, round 2 (`6151adb`, the final branch)

`judgements/round-2.json`, with the fixed axiom listing. The mechanism results are those of
round 1 (`mechanism.py` did not change): the six explained, 453 training and 180 held-out claims,
none false, 24 of 69 census entries. The Lean file builds (729 s), and **all 70 of its theorems
rest on `propext`, `Classical.choice` and `Quot.sound` only**, `period_r90_dvd` and the six
`period_*_dvd_87381` among them. No `sorry`, `axiom` or `native_decide`. `proposal.py` ran clean.
The pilot is complete.
