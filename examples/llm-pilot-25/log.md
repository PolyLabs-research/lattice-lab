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
- The held-out census ran alongside, in the orchestrator's container.

## The run

The agent's own messages are in `transcript/messages.md`; its tool calls in
`transcript/tool_calls.jsonl`, read from the server-side transcript.

- **16:53 (11 minutes in).** Three of the 14 family rules are exact twisted products,
  f = C(x, y) C(x³, y³), with C = self + N4, self + D4 and N4 + D4 (1227, 21029, 32184). As
  3 ≡ 2^7 (mod 25), their eigenvalues are c^129 = (c^43)³. This is mechanism 4 with d = 3, which
  the census's check for twisted powers did not try.
- **17:05 (23 minutes in).** The card's lead, generalised: for 3096 and 23608,
  f · (t(x) t(y))³ = B exactly, with B a union of shells that (x, y) ↦ (x^7, y^7) permutes mod 25.
  So B's eigenvalues lie in F(2^5), which lies in the cubes, and off the axes f = B / (a cube).
  On the axes f restricts to t²(t + 1)² = t · t(z³) = t^129. The previous pilot's mixed case
  needed rule 90 itself to be confined, and it is not at 25; a multiplier that enters as a cube
  needs no confinement of its own. The agent calls this a **cube certificate**.
- **17:30.** `mechanism.py` pushed (`2e8705c`): twisted pairs (Theorem A) and certificates
  f · M^E ≡ B (Theorem B: B invariant under ×2^g, q | E, and a check on the lines where M
  vanishes), plus the previous pilot's condition. It did not change after this commit; every
  later run of it, including the agent's checks on the whole family at 27, 33 and 35, came after.
- **17:37.** The certificates also explain 19 of the census remainder's 45: 16 at m = 13 that the
  orchestrator had filed as chance, and 3 of the 5 "coinciding eigenvalue" rules at 21.
- **17:36 to 17:56.** Lean, its mathlib build having finished in the background: a script
  generates the identities' certificates, it fixes its first build's errors, and `period 25 D ∣ 341`
  holds for all five on the standard axioms (`66eb18a`).
- **18:08.** A soundness sweep of `condition` over the atlas at 85 sizes up to 299: 1,060 claims,
  none false by its count. Two claims are not about cubes: 5th powers at 35 and 11th powers at 61.
- **18:17.** `report.md` pushed (`333a67d`); the watcher saw it at 18:17:41, 95 minutes after
  launch.

Beyond the mechanisms, the agent proved an identity it calls the fibre lemma: at 25, for a
character c of order 25, λ(c)^341 = N(λ(c)) = λ(5c) + a sum over necklaces of the rule's terms. So
whether λ(c) is a cube is tied to the order-5 value λ(5c), which the chance model treats as
independent. A model that keeps each fibre {5c, c, ...} together expects 6.1 of the nine
remaining family rules, or 11.8 with the axis and diagonal fibres coupled; it argues that the
rest of the excess at 25 is mostly the model's.

The session made 108 tool calls (102 Bash, 5 Write, 1 Edit) and cost about USD 14.2. Its only
inputs were the prompt and five notifications of its own background tasks.

## The audit

`transcript/audit.json`, over all 108 calls:

- no MCP tools, no web search or fetch, no subagents;
- its git commands: `status`, `checkout -b pilot-25-submission`, `add`, `commit`, `log --oneline`
  and `push` to its own branch, nothing else;
- 27 flags, none a step outside the boundary: 21 are Python divisions (`/3`, `/n`, `/q`) and `sed`
  patterns read as paths, one a `/dev/stdin` read, one a `grep` in `~/.elan` (allowed), and five
  read the output files of its own background commands, which the harness keeps under `/tmp`.

## The orchestrator's check

`tests/test_cubes25.py` multiplies the identities out again with the orchestrator's arithmetic
and the atlas's own shells, not the agent's code: both certificates hold exactly and are invariant
under ×7 mod 25; on the axes both rules restrict to t · t(z³); the three twisted pairs hold
exactly; `eigen.odd_part` divides 341 for all five at 25; and the three twisted pairs are cubes at
29, 35, 53 and 55, the held-out sizes where 3 ≡ ±2^odd. The five rules in `Pilot.lean` are
exactly the family's rules 3096, 23608, 1227, 21029 and 32184 (their offset sets compared).

## The registered held-out census

The study (`study.py`) finished at 18:07 UTC, after 91 minutes, and recorded its verdict in the
ledger: **chance is refuted.** At 6 of the 14 sizes the square family has more unexplained
confinement than the model's expected count + 3 sd + 1:

| m | confined | explained by pilot 4 | unexplained | expected by chance |
| --- | --- | --- | --- | --- |
| 29 | 16 | 0 | 16 | 5.6 ± 2.4 |
| 35 | 3 | 0 | 3 | 0.009 |
| 37 | 34 | 18 | 16 | 0.62 ± 0.79 |
| 53 | 3 | 0 | 3 | 0.008 |
| 55 | 3 | 0 | 3 | 3 × 10⁻⁶ |
| 61 | 3 | 0 | 3 | 0.0009 |

and none at 39, 41, 45, 51, 63, 65, 69 or 75. The three at 35, 53 and 55 are exactly the agent's
twisted pairs (1227, 21029, 32184), which are also among the 16 at 29. The three at 61 (3461,
18246, 26883) are also among the 16 unexplained at 37. The orchestrator's registered expectation
was wrong; the agent's mechanism, which never saw these sizes, is tested on them by the judge.
