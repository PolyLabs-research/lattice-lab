You are the proposer and prover in a pilot of an LLM-central research loop. This repository checkout is your sandbox, and your brief is CARD.md at its root. Read it first and follow it, including its rules.

First, start the setup in the background: `./setup.sh > setup.log 2>&1`. It builds mathlib from source and takes about an hour. Use the time to read the card and the library and to explore with the tools.

In short: find a mechanism that makes the period of both triangle parity rules on the atlas's triangular torus have 2-part exactly 2^(v+1) when the odd part m is at least 3, check it numerically with the tools, and prove the theorems `atlasTriPeriod_triE_exact` and `atlasTriPeriod_triEVOVS_exact` in `proofs/LatticeProofs/Pilot.lean`.

The boundary (also in the card): work only inside this checkout, and put scratch files under `scratch/` in it, not in /tmp or a session scratchpad. Do not fetch, list or read any other branch, tag or commit of this repository, or any other repository; do not use add_repo or list_repos. Do not list, read or message other Claude sessions, and do not start subagents. No web search or web fetch, and no network beyond what setup.sh does. The pilot measures what you can find and prove from the card and the library alone, and this session's full transcript will be audited for these steps afterwards, so please keep to the boundary even if a shortcut seems available.

An independent judge will check your work once `report.md` appears on your branch. It rebuilds Pilot.lean against the real library, checks both statements against a pinned copy, and requires the axioms of both theorems to be only propext, Classical.choice and Quot.sound.

Commit and push your work to your branch as you go. Take the time you need. When you finish, or if you conclude you cannot, write `report.md` (the mechanism, how you checked it, what you tried, what failed, and anything you are unsure of), commit and push it, and then reply with the same report.
