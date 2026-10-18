# Log: the VO + T13 pilot

The orchestrator's record of the third LLM-central pilot, in order. The write-up is
[docs/llm-pilot.md](../../docs/llm-pilot.md).

## What is new in this pilot

The first two pilots gave the agent the statement to prove. This one gives it a question and
data. VO + T13 is the triangle rule of round 3's twisted power. The library knows its period on
the atlas's triangular torus is 2^(a+1) P(s, m) for some a ≤ v, and nothing more about a. The
agent must find the exact power of 2 at every even n ≥ 4, define it as `vot13TwoExp`, and prove
the pinned theorem `atlasTriPeriod_triVOT13_law` with its own definition in it.

Its harness is pilot 2's, with three additions:

- **data/vot13_periods.csv**: the exact period at every even n from 4 to 64 (`make_data.py`,
  with `exact.py`, since the base engine does not know round 3's shells);
- **the law is checked as a formula**: the judge evaluates `vot13TwoExp` with `#eval` at every
  (v, m) of the data and of the registered sizes, and at very large arguments. A noncomputable or
  slow definition fails;
- **the law against unseen sizes**: the registered study records the exact period at 20 sizes
  above 398. The judge compares the agent's law with them. The agent is never told the result.

## What the orchestrator knows

Before the launch, at sizes all computed before (n ≤ 128):

- for odd m ≥ 3 the exponent is v + 1, as for the edge and edge+vertex rules (n = 6 to 56);
- for m = 1 the period is 2^(v−1), at every n = 4 to 128. The edge rule has 2^v there and the
  edge+vertex rule dies, so VO + T13 matches neither. No hand proof covers this case.

So the orchestrator's law is `vot13TwoExp v m = if m = 1 then v − 1 else v + 1`. It fits all 31
rows of the data, and it is registered as a prediction at the 20 held-out sizes (`study.py`).
None of this is in the sandbox.

## Setup

- **The tools** (`tools/tori.py`) add VO + T13 and its square. Their neighbourhoods match
  `Rules.lean`, and their periods match `exact.py` at n = 4, 6, 8, 10, 12, 14 and 16, which
  include the m = 1 sizes 4, 8 and 16.
- **The target** elaborates against the library with `sorry`, and `#eval` refuses the template's
  definition, as the judge needs.
- **Registered** before the launch: the orchestrator's law at 20 sizes from 408 to 1024
  (`ledger.jsonl`).
- **The sandbox** is commit `877d01a60cb5` (`base.txt`), pushed as `pilot-sandbox-vot13` and as the agent's
  branch `pilot-vot13-submission`, with 25 protected files (`manifest.json`).
- **The judge, round 0**, on the base: library unchanged; the theorem depends on `sorryAx`; and
  the law is not computable, since `#eval` refuses a definition that is `sorry`
  (`judgements/round-0.json`). A first round 0 showed two judge bugs, both fixed before the
  launch: the law was evaluated before Pilot.lean was built, and Lean's line-wrapped list output
  was not parsed. The law path was then checked offline with the orchestrator's own law in place
  of the `sorry`: computable in 5.5 s, including at v = 100000, and 31 of 31 data rows agree.
