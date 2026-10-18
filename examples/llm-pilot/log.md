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
