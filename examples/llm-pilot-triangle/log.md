# Log: the triangle pilot

The orchestrator's record of the second LLM-central pilot, in order. The write-up is
[docs/llm-pilot.md](../../docs/llm-pilot.md).

## What changed from the first pilot

The first pilot's two harness faults are fixed:

- **The Python environment.** The first sandbox's `python` was a symlink to the venv's
  interpreter, and through a symlink Python does not find the venv, so sympy was missing. A
  wrapper that runs the venv's interpreter by its own path fixes it (checked: through the symlink
  `import sympy` fails, through the wrapper it works). `examples/llm-pilot/sandbox.py` now writes
  the wrapper. This pilot's sandbox makes its own venv in its container (`setup.sh`) and uses the
  same kind of wrapper.
- **Isolation.** The first agent ran in the orchestrator's container, where the hand proofs and
  the orchestrator's own transcript were on disk. This agent runs in **its own cloud session**,
  whose container clones only the orphan branch `pilot-sandbox-triangle` of this repository, at
  depth 1. That branch has one commit with no parent and no docs/ or examples/. Reaching the
  hand proof would take a deliberate step: fetching another branch, adding another repository,
  or reading another session. The rules forbid these, and the agent's full transcript, read from
  the server rather than from anything the agent wrote, is audited for them (`audit.py`).
  The user chose this layout over a separate repository, which the GitHub integration could not
  create (403).

## Setup

- **Targets.** `atlasTriPeriod_triE_exact` and `atlasTriPeriod_triEVOVS_exact`: on the atlas's
  triangular torus of side 2^v m, m odd ≥ 3, v ≥ 1, both parity rules have period exactly
  2^(v+1) P(m). The statements elaborate against the library with `sorry`
  (`judgements/round-0.json`).
- **Checked before registering, at sizes already computed** (all ≤ 56, so nothing new is seen):
  the exact 2-part holds for both rules at n = 6, 10, 12, 14, 18, 20, 22, 24, 26, 28, 30, 36, 40,
  48 and 56, including m = 3.
- **The tools** (`tools/tori.py`) add the triangular torus and both rules. Their neighbourhoods
  match `Rules.lean` exactly, and their periods match the atlas engine at n = 6, 10, 12 and 14.
- **setup.sh** was tested in an empty home directory: the venv (numpy 2.5.4, sympy 1.14.0), elan,
  Lean 4.35.0, and the start of the mathlib build (750 jobs in 6 minutes) all worked.
- **The registered test** (`study.py`) predicts both rules' periods at 20 sizes from 408 to 1024,
  40 predictions. No period of either rule had been computed above 398.
- **Registered** before the launch: 40 predictions (`ledger.jsonl`).
- **The sandbox** is commit `9d5a274d351f` (`base.txt`), pushed as `pilot-sandbox-triangle` and as the
  agent's branch `pilot-triangle-submission`. It holds 23 protected files (`manifest.json`) and
  `proofs/LatticeProofs/Pilot.lean`.
- **The judge, round 0**, on the base itself: library unchanged, both statements build, and the
  run fails only because both theorems depend on `sorryAx` (`judgements/round-0.json`).

## Launch

- **20:28:23 UTC.** The agent's session, `session_01GVScbB1SJ9jeHcJncfbzxC`, was created from
  `pilot-sandbox-triangle` at depth 1, in the same cloud environment as the orchestrator but its
  own container, with the prompt in `prompt.md`, verbatim. It inherited the orchestrator's
  permission mode (auto). The session was asked to push to `pilot-triangle-submission`, but its
  record names `pilot-sandbox-triangle` as its branch, so the watcher and the judge accept
  either; the judge always diffs against the base commit itself.
- The registered study's run started at the same time, in the orchestrator's container, which
  the agent cannot see.
- **20:47:22 UTC: the registered test held at all 40 predictions**, both rules at all 20 sizes
  (`records.jsonl`, the verdict in `ledger.jsonl`); `lattice-lab verify` finds no problems. This
  was before the agent had reported anything.

## What the agent did

From its server-side transcript (`transcript/`): 40 tool calls (34 shell, 3 file writes, 2
monitors, 1 wake-up), 41 minutes from launch to the pushed report. It wrote about 32,000 output
tokens, its context reached about 188,000 tokens, and the session cost $3.23.

| UTC | |
| --- | --- |
| 20:28:30 | started `setup.sh` in the background and read the card |
| 20:28–20:29 | read the library: Bridge, GroupRing, Triangle, Tori, Periods, TwoPart, HexTwoPart, Rules, and the tools |
| 20:29:59 | wrote `proposal.py`, the numerical check of the mechanism |
| 20:33:34 | wrote the whole of `Pilot.lean`, with four eigenvalue sums left as `sorry`, before any Lean was available |
| 20:34:08 | committed and pushed the proposal and the skeleton |
| 20:35–21:06 | waited for its mathlib build (31 minutes) |
| 21:06:26 | first compile: the skeleton built, with only the four sums open |
| 21:06–21:08 | closed the four sums (`simp`, `field_simp`, `linear_combination c * (2 = 0)`), built, and checked both pinned statements and their axioms |
| 21:08:53 | pushed `report.md` |

## Judge, round 1

21:09 UTC, on `pilot-triangle-submission` at `92c36f3` (`judgements/round-1.json`): **passed**.

- Library unchanged: against the base, the branch modifies only `Pilot.lean` and adds
  `proposal.md`, `proposal.py`, `report.md` and two files under `scratch/`; every manifest file
  matches.
- The proofs build against the real library (33 s), the repository's PilotCheck.lean elaborates
  both pinned statements, and both theorems depend only on propext, Classical.choice and
  Quot.sound. The word `sorry` survives only in the template's header comment.
- The agent's `proposal.py` held 54 of 54 checks on the judge's rerun (104 s).

So no judge output was sent back.

## Audit

`audit.py --root /home/user/lattice-lab` over all 40 calls (`transcript/audit.json`): no MCP
tools (no repositories, no other sessions), no web search or fetch, no subagents, no fetch or
listing of other refs, and no mention of the write-ups. It raised seven flags, read by hand:

- call 12 reads `/tmp/claude-0/.../tasks/b3dxud8tu.output`, the output file of the agent's own
  background command in its own container. Outside the checkout, as the card forbids, but it
  holds nothing but its own `proposal.py` output;
- the other six are false positives: `sed` patterns (`s/if n > 40:/...`, `/--`) and the session
  URL in commit trailers, which the path pattern reads as paths.

The inputs the session received are listed in `transcript/inputs.md`. One of them, "continue once
the build finishes" at 20:35:08, was not sent by the orchestrator and has no recorded origin; it
was most likely typed in the Claude app. It says nothing about the problem.

## Integration

- `proofs/LatticeProofs/TriTwoPart.lean` is `submission/Pilot.lean`, verbatim. It is a root in
  `lakefile.toml`, and `Axioms.lean` prints both theorems' axioms: standard.
- `tests/test_proofs.py` checks the exact 2-part of both rules against the atlas engine at
  n = 6, 10, 12 and 14.
- Both sandbox builders now leave out the proofs added after their pilots, so each rebuild
  reproduces what its agent saw.
