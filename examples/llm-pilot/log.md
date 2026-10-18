# Orchestration log

Everything the orchestrator sent to the agent, and when, is recorded here verbatim. The
orchestrator's own mathematics is not shared with the agent.

## Setup (before the agent ran)

- The problem card (`card.md`), the tools (`tools/`), the target (`Pilot.lean`), the pinned
  statement (`PilotCheck.lean`), the sandbox builder and the judge were committed and pushed.
  The registered predictions (`ledger.jsonl`) were pushed too.
- Harness check: the judge, run on the unsolved template (`judgements/round-0.json`), fails it on
  `sorryAx`, as it should.
- The sandbox (`/home/user/pilot-sandbox`) holds the card, the tools and the Lean library. It
  leaves out `docs/` and `examples/`, which contain the hand proof of the hexagon 2-part.
- Isolation is by instruction, not enforced: the agent runs in the same container. The prompt
  and the card ask it to stay in the sandbox.

## Round 1

Prompt (`prompt.md`), sent to a fresh general-purpose agent with no other context.

- Launched 2026-10-18 19:14 UTC. The agent ran for 925 s (15.4 minutes), made 35 tool calls
  and used 203,597 tokens. It sent no messages before its final report, and the orchestrator
  sent it nothing after the prompt.
- Its final report is in `submission/report.md`, verbatim, with its files: `Pilot.lean`,
  `proposal.md`, `proposal.py`, and its scratch files under `scratch/`.

## Judgement, round 1

`judge.py 1`, 2026-10-18 19:30 UTC (`judgements/round-1.json`): **passed**.

- Library unchanged: every manifest file matches, and there are no unexpected files.
- `lake build LatticeProofs.Pilot`, against a fresh copy of the repository's library, succeeds
  in 13 s.
- The repository's PilotCheck.lean elaborates the pinned statement. Axioms:
  `[propext, Classical.choice, Quot.sound]`.
- The agent's `proposal.py`, rerun by the judge: 56 of 56 checks held, in 161 s.

No further rounds were needed, so no judge output was ever sent back to the agent.

## Boundary and harness issues

- **The agent wrote to /tmp.** It put five scratch files in the session scratchpad
  (`/tmp/claude-0/...`), against the card. It said so in its report. The scratchpad also holds
  the orchestrator's earlier scratch files. None of them contains the 2-part mechanism: they are
  build logs, Lean experiments for other files, and a torus-model check.
- **The sandbox's interpreter lacked sympy.** That is the orchestrator's bug, not the agent's.
  `pilot-sandbox/python` is a symlink to the venv's interpreter, and run through a symlink it
  does not activate the venv. The card was wrong to say sympy was available. The agent
  reimplemented the cyclotomic factorisation itself.

## Integration

The proof is in the library verbatim as `proofs/LatticeProofs/HexTwoPart.lean`, which is
byte-identical to `submission/Pilot.lean`. It imports the root module, so it is a root of the
`lean_lib`, not imported by it. `Axioms.lean` prints its axioms.

To rerun the pilot, build the sandbox from the registration commit `c2d58ac`. Later commits put
the answer in the library.
