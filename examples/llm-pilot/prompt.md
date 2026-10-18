You are the proposer and prover in a pilot of an LLM-central research loop. Your brief is the problem card at /home/user/pilot-sandbox/CARD.md. Read it first and follow it, including its rules.

In short: find a mechanism that makes the hexagon parity rule's period on the atlas's hexagonal torus have 2-part exactly 2^(v+1) when the odd part m is at least 5, check it numerically with the tools in the sandbox, and prove the theorem `hexPeriod_hexH1_exact` in Lean in `proofs/LatticeProofs/Pilot.lean`.

Constraints (also in the card): work only inside /home/user/pilot-sandbox. Do not read, list, grep or search anything outside it: not /home/user/lattice-lab or the other repositories, not /root/.claude, not /tmp. The only exceptions are running the Lean toolchain (~/.elan) and the Python interpreter /home/user/pilot-sandbox/python. Do not use the network or web search. Do not modify existing library files. The pilot measures what you can find and prove from the card and the library alone, so please keep to the boundary even if a shortcut seems available.

An independent judge will check your work. It rebuilds Pilot.lean against the real library, checks the statement against a pinned copy, and requires the axioms to be only propext, Classical.choice and Quot.sound.

Take the time you need. When you finish, or if you conclude you cannot, reply with the final report the card describes: the mechanism, how you checked it, what you tried, what failed, and anything you are unsure of. Include the final contents of proposal.md in your reply.
