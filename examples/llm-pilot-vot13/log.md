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

## Launch

- **22:05:13 UTC.** The agent's session, `session_01HapH3CyxfZQENtrC6XEp12`, was created from
  `pilot-sandbox-vot13` at depth 1, in its own container, with the prompt in `prompt.md`,
  verbatim, and asked to push to `pilot-vot13-submission`.
- The registered study's run started at the same time, in the orchestrator's container.
- **22:35:03 UTC: the orchestrator's registered law held at all 20 held-out sizes**, including
  m = 1 at n = 512 and 1024 (periods 256 and 512). The records hold each exact period, for
  judging the agent's law; `lattice-lab verify` finds no problems.

## What the agent did

From its server-side transcript (`transcript/`, made by `transcript.py`): 42 tool calls (39
shell, 3 file writes), 53 minutes from launch to the pushed report, 41 of them waiting for its own
mathlib build. It wrote about 42,000 output tokens, its context reached about 182,000 tokens, and
the session cost $3.25.

| UTC | |
| --- | --- |
| 22:05:20 | started `setup.sh` in the background and read the card, the data and the library |
| 22:05:57–22:08 | **found the law**: divided P(m), computed with the tools, out of every row of the data; the quotient was always 2^e, with e = v − 1 at m = 1 and e = v + 1 at m ≥ 3 |
| 22:10:26 | checked how the 49 translations of s fall on the small tori Z/4 × Z/2 and Z/8 × Z/4 |
| 22:11:46 | wrote `proposal.py` |
| 22:13:30 | wrote the whole of `Pilot.lean`, the m = 1 argument included, before any Lean was available |
| 22:14–22:55 | waited for its mathlib build |
| 22:55:23 | first compile: one `linear_combination` coefficient wrong |
| 22:56:21 | fixed it; built; checked the pinned statement and the axioms |
| 22:57:50 | pushed `report.md` |

Its law is `vot13TwoExp v m = if m = 1 then v - 1 else v + 1`, the orchestrator's.

**The m = 1 argument is new.** No hand proof covered it, and the library had no lemma for it.
The agent proved a general fibre lemma (`gstep_eq_self_of_fibers`: a rule is the identity on a
torus if its translations land an odd number of times on 0 and an even number of times on every
other cell) and three finite facts by kernel `decide`:
1. s is the identity on Z/4 × Z/2, so 2^(v−1) is a period;
2. 2s is the identity on Z/8 × Z/4, so s is an involution there;
3. s is not the identity on Z/8 × Z/4, so 2^(v−2) is not a period when v ≥ 3.

The case v = 2 uses the layer-parity argument. The m ≥ 3 case follows TriTwoPart, with
λ = 1 and μ = (ζ + 1/ζ)³ from the twisted factorisation s = s_E(x, y) s_E(x³, y³).

## Judge, round 1

23:04 UTC, on `pilot-vot13-submission` at `4be5576` (`judgements/round-1.json`): **passed**.

- Library unchanged: the branch modifies only `Pilot.lean` and adds the deliverables and three
  scratch files.
- The proof builds against the real library, the pinned statement elaborates, and the theorem
  depends only on propext, Classical.choice and Quot.sound. So do the other nine theorems in the
  file.
- **The law is a formula**: `#eval` computed it at all 51 points and at v = 100000 in 5.5 s.
- **The law against the engine**: 31 of 31 rows of the data it was given, and **20 of 20
  held-out sizes it never saw**.
- `proposal.py`: 63 of 63 checks held on the judge's rerun.

No judge output was sent back.

## Audit

`audit.py --root /home/user/lattice-lab` over all 42 calls (`transcript/audit.json`): no MCP
tools, no web access, no subagents, no fetch or listing of other refs, no mention of the
write-ups. Nine flags, read by hand: four reads of the agent's own background-task output files
in its own container's /tmp (outside the checkout, as in pilot 2, and harmless), and five false
positives (`/P` inside Python, and the session URL in commit trailers). The session received two
inputs (`transcript/inputs.json`): the prompt, and one notification from its own background
task.

## Integration

- `proofs/LatticeProofs/VOT13Law.lean` is `submission/Pilot.lean`, verbatim, a root in
  `lakefile.toml`, with its axioms in `Axioms.lean`.
- `tests/test_proofs.py` checks VO + T13's exact 2-part at n = 6, 10, 12 and 14, and its period
  n/2 at n = 4, 8 and 16, against the engine.
- `branches.bundle` holds both pilot branches with their full history. The agent's session was
  archived. The remote branches could not be deleted from this session (its git proxy refuses
  ref deletion); the bundle holds everything they had.
