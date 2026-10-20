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
