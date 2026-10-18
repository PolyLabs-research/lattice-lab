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
