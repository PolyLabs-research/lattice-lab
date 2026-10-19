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

## The run

The agent's own messages are in `transcript/messages.md`; its tool calls in
`transcript/tool_calls.jsonl`, read from the server-side transcript.

- **21:54.** It rewrote the rules in a = x + 1/x and b = y + 1/y: every rule of the square
  family is a symmetric polynomial F(a, b) of degree at most 4 in each, since the D4 orbit of
  (i, j) is D_i(a) D_j(b) + D_j(a) D_i(b), with D_n the Dickson polynomials.
- **By 22:02 (11 minutes in).** Factoring the 16 that way (Kronecker substitution and
  recombination, since sympy has no bivariate factoring over GF(2)): nine are a unit times a
  cube, f = U · g³, with U one of a + b, ab, (a + 1)(b + 1) and g one of a + b + 1 (N4 + self),
  ab + 1 (D4 + self), ab + a + b (N4 + D4), all nine combinations. The units' values are cubes:
  a + b and ab are products of rule-90 values, which are cubes at 37; (a + 1)(b + 1) has
  Ψ₃(t)² = t(z³)/t(z), a quotient of rule-90 values at 37, and at 61, where 3 = 2⁶, it is t^63,
  a cube with no help from rule 90. So the three in the (a + 1)(b + 1) row are exactly the three
  also confined at 61.
- **22:12.** `condition` (the theorem "unit times power": f = monomial × ∏ Φ_e(X_w)^k × h^q
  exactly, with each unit whose exponent q does not divide taking q-th-power values at m)
  explained the nine; pushed at 22:20 (`db13beb`).
- **22:14 onwards.** The chance model: over the whole family at 37, the axis and diagonal
  classes are cubes 93.5% of the time, not one in three, because a rule's value on the axis is
  H(t) with deg H ≤ 4, and 29 of the 31 such H are products of Ψ_e's (units at 37). With the
  measured per-class rates, the expected count of chance confinements at 37 is 5.7, not 0.62;
  seven remain unexplained.
- **22:27.** It checked its predictions (the nine wherever rule 90 is confined to the cubes; the
  (a + 1)(b + 1) row also where Ψ₃ is good on its own) directly, up to m = 151, which includes
  95, 101 and 111 of the registered grid. At 111 = 3 · 37 its condition missed the (a + 1)(b + 1)
  row, since 3 divides 111; at 22:27:50 it extended its Lemma 1(a) to prime e, with a proof
  (t_{pi} = t_i Ψ_p(t_i)²). So its coverage at 111 is not blind. `mechanism.py` changed once more
  (22:32, `_xorder` rewritten to the same result, faster), and not after.
- **22:53 to 22:55.** Lean, once its mathlib build finished: all twelve theorems built at the
  first attempt and rest on the standard axioms (`5aa26ef`).
- **22:57.** `report.md` pushed (`8b0d911`); the watcher saw it at 22:57:37, 66 minutes after
  launch.

The session made 99 tool calls (95 Bash, 4 Write). Its only inputs were the prompt and six
notifications of its own background tasks.

## The audit

`transcript/audit.json`, over all 99 calls:

- no MCP tools, no web search or fetch, no subagents (`transcript.py` first counted 13
  "subagent calls": they were `tool_progress` events, which carry a parent tool id; it now counts
  only assistant and user events);
- its git commands: `status`, `checkout -b pilot-37b-submission`, `add`, `commit`, `log`, and
  `push` to its own branch;
- 14 flags, none a step outside the boundary: Python divisions and text inside the files it
  wrote, read as paths, and one `ls ~/.elan/bin` (allowed).

## The orchestrator's check

`tests/test_unitcubes.py` multiplies all nine identities out again with the orchestrator's
arithmetic and the atlas's shells; checks the odd parts at 37 (all nine divide 87,381) and at 61
(exactly the (a + 1)(b + 1) row is confined, and rule 90 is not); and checks that the held-out
census's unexplained confinements are exactly the nine at 95, 101 and 111 and nothing elsewhere.
The per-class cube rates at 37 were recomputed over all 32,767 rules: 0.935 on the axis and the
diagonal, 0.394 on the class (1, 2), as the agent reported. The Lean file's nine rule
definitions are exactly the family's rules (offset sets compared).

## The registered held-out census

The study finished at 22:59 UTC, 68 minutes after it started and two minutes after the agent's
report; the caches warmed faster than in the fifth pilot. **Chance is refuted at 95, 101 and 111, and only there**: at each, 9
confinements that neither earlier pilot's condition explains, against at most 1.5 × 10⁻⁸
expected.
They are exactly the agent's nine rules, at exactly the sizes it predicted (where rule 90 is
confined to the cubes). At the other 14 sizes every confinement is explained: the fifth pilot's
twisted pairs 1227, 21029 and 32184 at 77, 95, 97, 101, 115 and 125 (and 31801 at 101), and at 115 two rules
that split into correlated rule-90 passes (102 and 1548), counted apart as registered. As far as
its transcript shows, the agent never computed which family rules are confined at these sizes:
it checked its own claims there, and its nine rules.

## The judge, round 1 (`8b0d911`)

`judgements/round-1.json`. The library was unchanged (only `Pilot.lean` touched, and the agent's
own new files), and:

- **Explains 12 of the 19**: `condition` returns q = 3(2^18 + 1) for the nine at 37 and
  3(2^30 + 1) for the three at 61, and nothing for the other seven.
- **Sound: 1,065 claims at the training sizes and 473 at the held-out sizes, none false**, each
  checked by the judge's own eigenvalue computation; 64 and 18 of them beyond the known
  mechanisms.
- **Coverage**: 19 of the census remainder's 45 (16 at 13 and 3 at 21, through the fifth
  pilot's condition, which this one calls); 12 of the 49 family confinements at the training sizes
  that neither earlier condition explains (the twelve targets); and at the held-out sizes 18 of
  18, the nine at 95 and at 111.
- **Lean**: `Pilot.lean` builds against the real library (30 s), and all 60 of its theorems rest
  on `propext`, `Classical.choice` and `Quot.sound` only.
- **The agent's own checks** (`proposal.py`): 32 of 32.

**A sequencing fault, the orchestrator's.** The judge started at 22:58, as soon as the report
appeared, and read the held-out census's records then. The census wrote its last size, 101, at
22:59. So round 1 judged the family at 101 on the fixed sample only, without the nine confined
rules there, and its held-out total (18) leaves them out. A targeted run of the same evaluation
at 101 afterwards: `condition` claims all nine (q = 3(2^50 + 1)) and every claim holds. Round 2
reruns the whole judge on the same commit with the complete records.
