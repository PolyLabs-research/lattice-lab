# The seventh pilot (ninth powers at m = 37): log

The seventh LLM pilot, and the fourth on an open question, with **Claude Fable** as the agent
(the first six ran on the orchestrator's own model). Its question comes from the rule-4850
study (`examples/rule-4850`, docs/consultations.md section 4): at m = 37, rule 4850 of the
square family and four rules of radius 5 (699738, 985232, 1431278, 1968276) have every nonzero
eigenvalue a ninth power, which no known mechanism explains; a registered census refuted chance
(four independent such rules among 2,064,384 new radius-5 rules, against 0.0066 expected).

## Design

The harness is the sixth pilot's, with these changes:

- **The tools** add the sixth pilot's `condition` (unit times a power) as `tools/unitpower.py`,
  verbatim, and `tools/census37.py`, the fast census at 37 by class discrete logs, which builds
  its own field and reproduces the radius-4 counts (110 cube, 21 ninth-power, 4 27th-power
  rules).
- **The data** (make_data.py): the ninth-power census at 37 of radius 4 and of the new radius-5
  rules, each ninth-power rule with its 11 class logs, the atlas procedure's verdict and its
  role; the five targets and 482758 (4850 times rule 7, not a target); the cube censuses from the
  fifth and sixth pilots (21 to 125); the three previous proposals; and the two Fable
  consultations on 4850, verbatim.
- **Found while building the sandbox**: the fourth pilot's half-Frobenius condition proves the
  four radius-5 targets are cubes (q = 3(2^18 + 1)), though not ninth powers; for 4850 none of the
  conditions claims anything. The card says so.
- **The judge** (judge.py): explains = a claim with q divisible by 9 at 37 for the five targets;
  soundness on the atlas at 94 sizes as before, on radius-4 square rules at the 33 sizes of the
  cube data, and at 37 on the agent's 42 ninth-power rules and a radius-5 sample; held out, at 37
  every ninth-power rule of the registered radius-6 census and a radius-6 sample, and a radius-5
  sample at the odd m from 127 to 161 with ord_m(2) even.
- **The registered held-out test** (study.py, registered and pushed at 13:59 UTC in `7be0016`,
  before any radius-6 rule was computed): the ninth-power census at 37 of the 266,338,304 rules
  that use an orbit of radius 6, which the agent never sees, expecting more unexplained rules than
  chance.

## Setup and launch

- **The sandbox**: commit `63e6595f966e` (`base.txt`), pushed as `pilot-sandbox-37c` and
  `pilot-37c-submission`; 45 protected files. The tools ran in the sandbox (the census reproduced
  the radius-4 counts; the conditions ran on the six rules of `data/targets.json`).
- **14:12:24 UTC.** The agent's session, `session_01SRg7t4ekSkYRGHHbfZ4ARF`, was created from
  `pilot-sandbox-37c` at depth 1, in its own container, with the prompt in `prompt.md`, verbatim,
  **model `claude-fable-5-1`**, and asked to push to `pilot-37c-submission`. Its first turn was
  served by `claude-fable-5-1`. A watcher polls the branch for `report.md`.

## The registered held-out census (radius 6)

Run at 13:59 to 14:01 UTC, before the launch, in 117 seconds. Of the 266,338,304 rules that use
an orbit of radius 6: 23,722 are confined to the cubes at 37, **83 to the ninth powers** and 29 to
the 27th powers. Of the 83, the atlas procedure explains 39 (24 mixed splits, 8 dilations, 5
powers, 2 splits into rule-150 lines), one is an image of 4850 under a map in GL2(Z/37)
(10491524), six are a target times a rule with ninth-power values, and **37 are unexplained**
(20 of them confined to the 27th powers), against **0.70 expected** by chance (bar
expected + 3 sd + 1 = 4.2). Mechanism: supported, as registered. These 37 are the held-out set
for the agent's condition; the agent has not seen them.

**The baseline for the agent's reach** (`baseline.json`, computed before any submission): the
census counted as explained only what the atlas procedure (mechanisms 1 to 4) explains, as
registered. Of its 37, the earlier pilots' conditions prove ninth powers for 16 (12 by the
half-Frobenius condition, 4 more by the certificate condition); **21 are explained by none of the
seven known mechanisms**, still far beyond chance (0.70 expected, bar 4.2). For the five targets
none of those conditions proves ninth powers, as the card says. The judge reports the agent's
coverage of both the 37 and the 21.

**The judge, tested on a toy submission** (the sixth pilot's condition, true ninth-power claims
for the five targets, and a planted false claim), in a quick mode with a few sizes of each kind:
the first run found two module-name clashes in the judge (fixed: this pilot's study.py and the
fast census are loaded by path); the second ran every set (2,000 to 2,083 rules each, 32 to 86
seconds) but its planted claim, 4850 at 61, lay outside the sets the judge evaluates, so it was
moved to 4850 at 37 (q = 27, false) for a third run.
The third run caught it: two false claims (4850 at 37 is in two of the judge's sets), sound:
false, targets 4 of 5 (4850's only claim was the false one), and the toy's held-out coverage
exactly the baseline, 16 of the 37 and 0 of the 21 (`judgements/toy-run-2.json`,
`toy-run-3.json`).

## The run

The agent wrote almost no prose: six text blocks in 121 tool calls (115 Bash, 6 Write), the rest
tool calls and thinking (`transcript/`).

- **14:12 to 14:18.** It read the card, the tools, the data, the three earlier proposals and the
  two consultations, in parallel.
- **14:22.** A full discrete-log table of F(2¹⁸)*, which made every multiplicative question
  linear algebra on the class logs.
- **14:31.** **Its own radius-6 census** (`scratch/census6.py`, 44 seconds, from
  `tools/census37.py`): 23,722 cube-confined, 83 ninth-power, 29 27th-power rules, exactly the
  registered census's counts. The card did not forbid it, but it means the radius-6 rules the judge
  holds out were not unseen; see below.
- **14:37 to 14:50.** A half-Frobenius scorer with exact exponents explained the four radius-5
  targets; `mechanism.py` at 14:50. Most of the next hour went on 4850 (cube roots, unit and
  direction searches, the cube-plus-square form) and on making `condition` fast enough.
- **15:37 to 16:01.** Certificates for a Lean file (`scratch/gen_pilot.py`), proposal.md, and
  commits at 14:37, 15:41 and 16:01. Its mathlib build, started at 14:12, had still not finished
  at 16:03 (its own sweeps were using the cores), and it then blocked for 10 minutes waiting on it.
- **16:08.** The orchestrator asked it to wrap up, for cost (the person running the pilot chose
  this at about two hours, with the spend near £50): no new work, no waiting for Lean, write the report. Its
  blocking wait ended at 16:13; `report.md` was pushed at 16:14 (`b5014b6`) and its reply sent at
  16:15. This is the first pilot ended by the orchestrator rather than by the agent.

**Cost** (the session's own accounting, at list price, every turn served by `claude-fable-5-1`):
**$51.33**: $42.02 for the first turn (2 hours, 117 tool calls, 418K output tokens of which 296K
thinking, 37.5M cache-read input tokens) and $9.31 for the wrap-up turn, of which $8.02 rewrote
its 640K-token context to the prompt cache: the cache had expired during the 10-minute wait, so
any next step would have paid it.

## The judge, round 1

`judgements/round-1.json`, on `b5014b6`, 70 minutes:

- **Library unchanged**: yes; only the deliverables, Pilot.lean and scratch/ changed.
- **Explains 4 of the 5 targets**: 699738, 985232, 1431278 and 1968276, each with q = 9 · (2¹⁸ + 1)
  at 37. Not 4850.
- **Sound**: `condition` ran on all 144 sets without an error; **1,182 claims at the training
  sizes and 533 held out, none false**, each checked by the judge's own eigenvalue computation;
  152 of them are beyond what the atlas procedure accounts for, and 323 claim ninth powers or more.
- **Reach**: **35 of the radius-6 census's 37** unexplained ninth-power rules, and **19 of the 21**
  that none of the seven earlier mechanisms explains (baseline.json); the two it misses are
  20982139 and 178279803, which have 4850's rotated class pattern. 48 of the 76 cube hits at the
  training sizes. **27 of the atlas census's 45 remainder entries**: 17 of the 19 that the fifth and
  sixth pilots' conditions cover, and **10 that no earlier condition covered** (seven at 13, among
  them three hexagon and two triangle rules; at 21 one square rule and the triangle rule
  E+VO+T7+T9+self that census-remainder.md put down to hidden symmetries). It loses two of the
  earlier 19 (hexagon H4+H13 at 13, square N4+K8+C4+L8+M8 at 21): its searches are bounded
  differently.
- **Lean**: **does not build**. Pilot.lean has 11 errors: five `rw` steps that find no pattern,
  four heartbeat timeouts in `ring`/`whnf`, and two theorems that fail because their lemmas did.
  No theorem is accepted. The agent had said the file was unbuilt and might contain errors.
- **The agent's own checks** (proposal.py): 42 of 42, in 47 seconds.

**The held-out test is weaker than registered.** The radius-6 census was registered as rules the
agent never sees, and it computed them itself 19 minutes in. Its condition's reach there is
still measured by the judge, but it is reach on rules the agent could test against, not a
prediction. What remains held out is the sizes: 533 claims at the atlas's held-out sizes 163 to
333 and at 127 to 161 for radius 5, none false.

## The audit

`transcript/audit.json`, over all 121 calls: no MCP tools, no web search or fetch, no subagents.
Of the 27 flags, 14 are seven reads of the session's own persisted tool outputs, each flagged
twice (long `cat`s of the sandbox's tools and proposals that the harness saved under ~/.claude),
one is `git branch -a`, which listed only the sandbox's own branch, and the other 12 are false
positives on `/3`, `/9` and `/--` inside code the agent wrote. The inputs it received (`transcript/inputs.json`) are the prompt,
three notifications from its own background commands, and the orchestrator's wrap-up message.

## The orchestrator's check

`tests/test_ninth37.py` multiplies out the four factorisations (line units times the fourth
pilot's cores W and V), the two core identities, checks that their right sides are fixed by the
dilation by 6 at 37 (so the cores' values lie in F(2⁹)), and that Ψ₅(t)² = t^(2²³ − 1) for every
nonzero rule-90 value, with the net exponent 2²³ − 2 of valuation exactly 1 at 3: the step from
cubes to ninth powers. All pass.
