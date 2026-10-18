# The LLM-central pilots: the hexagon and triangle laws' 2-parts

**Result: in both pilots so far, a fresh agent, given only a problem card and the Lean library,
proved its theorems on the first attempt.** The judge accepted each proof, not the agent's own
report:

- the proof builds against the real library;
- the statements match pinned copies;
- the axioms are only Lean's standard three.

Each law's registered predictions, at sizes nobody had computed, all held. Both proofs are now in
the library, verbatim: `HexTwoPart.lean` and `TriTwoPart.lean`.

| | Pilot 1: the hexagon law | Pilot 2: the triangle laws |
| --- | --- | --- |
| Theorems | `hexPeriod_hexH1_exact` | `atlasTriPeriod_triE_exact`, `atlasTriPeriod_triEVOVS_exact` |
| Where the agent ran | a subagent in the orchestrator's container | its own cloud session, whose container held only the sandbox |
| Isolation | by instruction only | a separate container, and the whole transcript audited |
| Time, tool calls | 15 minutes, 35 calls | 41 minutes (31 of them waiting for its own mathlib build), 40 calls |
| Judge | passed in round 1 | passed in round 1 |
| The agent's own checks | 56 of 56 | 54 of 54 |
| Registered test | 15 of 15 sizes | 40 of 40 predictions |
| Route, against the hand proof | a different one | the same one |

    examples/llm-pilot/                 pilot 1: card, tools, sandbox, judge, study, log, submission
    examples/llm-pilot-triangle/        pilot 2: the same, plus setup.sh, audit.py, transcript/

## Why pilots

The goal set earlier was a loop with the LLM at its centre: it proposes mechanisms, and machines
check them. Before aiming that loop at open questions, it needed a test on a problem whose
answer is known but which the agent could not look up. That makes it possible to judge the
loop's mechanics rather than the problem. The exact 2-parts of the parity laws were such
problems: each had a hand proof in [parity-lattices.md](parity-lattices.md#the-factor-2--2vn-proved),
and the library had the odd parts and the upper bounds, but not the exact 2-parts.

## Pilot 2: the triangle laws

**The problem.** The triangle law says that both triangle parity rules, the edge rule B13/S13
(`triE`) and the edge+vertex rule B1,3,...,11/S1,3,...,11 (`triEVOVS`), have period
2 · 2^v · L(m) on the atlas's triangular torus of side n = 2^v m, for odd m ≥ 3. The library had
the odd part and bounds on the 2-part. The targets are the exact 2-parts, for both rules.

**What changed from pilot 1.** Both of pilot 1's harness faults were fixed first:

- **The Python environment.** Pilot 1's `python` was a symlink to the venv's interpreter, and
  through a symlink Python does not find its venv: `import sympy` fails. A wrapper that runs the
  interpreter by its venv path works. Pilot 2's sandbox makes its own venv (`setup.sh`) and uses
  such a wrapper, and pilot 1's `sandbox.py` now writes one too.
- **Isolation.** The agent ran in **its own cloud session**. Its container cloned only
  `pilot-sandbox-triangle`, an orphan branch of this repository with one commit and no parent,
  at depth 1. That branch holds the card, the tools, the Lean library and `setup.sh`, and no
  docs/ or examples/. Neither the hand proofs nor the orchestrator's transcript were on its disk.
  Reaching them would have taken a deliberate step, such as fetching another branch, adding a
  repository, or reading another session. The rules forbade these steps, and the agent's whole
  transcript, read from the server and not from anything the agent wrote, was audited for them
  (`audit.py`). The user chose this layout; a separate repository was the alternative, but the
  GitHub integration could not create one.
- **Setup in a fresh container.** `setup.sh` installs elan and Lean from GitHub and builds mathlib
  from source; it was tested in an empty home directory first.
- **The judge** diffs the agent's branch against the base commit, and also checks the manifest,
  so the agent may change only `Pilot.lean` and add its deliverables.

**What happened.** The agent started its mathlib build, read the library, and wrote its numerical
check. By 20:33 UTC, five minutes in and before any Lean was available, it had written the whole
proof except four explicit eigenvalue sums. It then waited 31 minutes for its build. On the first
compile the skeleton built, with only the four sums open; it closed them in two minutes, and
pushed its report 41 minutes after launch. The judge passed it in round 1, so no feedback was ever
sent (`judgements/round-1.json`). The full record is `examples/llm-pilot-triangle/log.md`.

**The mechanism**, in the agent's words and lemmas (`TriTwoPart.lean`):

1. Two steps of either rule are one step of its square's plane rule s on each layer. 2^(v−1)
   steps of s are one step of 2^(v−1) s. Multiplication by 2^(v−1) embeds the torus
   G′ = Z/2m × Z/m, with (x, y) ↦ (x − y, y), onto 2^(v−1) G (`triSubMul_injective`). So 2^v p
   is a period of the rule exactly when p is a period of s on G′
   (`isEventualPeriod_atlasTri_iff`).
2. On G′, with ζ a primitive m-th root of unity, the weights ζ^a ζ^b and ζ^a ζ^b [a even] form a
   Jordan block (`triSub_even`):
   - for the edge rule, λ = 1 and μ = ζ + 1/ζ;
   - for the edge+vertex rule, λ = μ = ζ² + 1/ζ².

   Both are nonzero once ζ² ≠ 1, that is m ≥ 3, and `even_of_jordan` makes every period on G′
   even.
3. P(m) is odd, so with the library's bounds the 2-part is exactly 2^(v+1).

This is **the hand proof's route**: the same level 2^(v−1), the same character (α = ζ, β = 1 in
the hand proof's notation), and the same λ and w-coefficients. The agent says it copied
`HexTwoPart.lean`'s structure. For the edge+vertex rule this also gives the factor 2, which the
library had only as P / gcd(P, 2) = P(s).

**The registered test** predicted both rules' periods at 20 sizes from 408 to 1024, above every
size computed for them before. All 40 predictions held (`ledger.jsonl`, `records.jsonl`;
`lattice-lab verify` finds no problems). The run finished at 20:47 UTC, before the agent had
reported.

**The audit** (`transcript/audit.json`) found no MCP tools, no web access, no subagents, no
fetch or listing of other refs, and no mention of the write-ups. It raised seven flags. One is
real but harmless: the agent read the output file of its own background command, in its own
container's /tmp, which the card's "stay in this checkout" forbids. The other six are false
positives (`sed` patterns and commit-trailer URLs). The session received one input that the
orchestrator did not send, "continue once the build finishes" at 20:35 UTC
(`transcript/inputs.md`); it has no recorded origin, was most likely typed in the Claude app, and
says nothing about the problem.

## Pilot 1: the hexagon law

The hexagon law says that H1 (B135/S135) has period 2 · 2^v · R(m) on the atlas's hexagonal
torus of side n = 2^v m, for odd m ≥ 5. The library had proved the odd part and the upper bound
on the 2-part (`hexPeriod_eq_two_pow_mul`). The target was the exact 2-part, 2^(v+1).

### Design

Every piece below was committed and pushed (`c2d58ac`) before the agent started.

| Role | Who | What it does |
| --- | --- | --- |
| Orchestrator | this session | wrote the card, the tools and the judge; registered the predictions; launched the agent; passed back judge output only, at most three rounds; logged everything |
| Proposer and prover | a fresh general-purpose agent, with no other context | read the card; worked in the sandbox; proposed a mechanism, checked it numerically, proved it in Lean |
| Judge | `judge.py` | decided whether the proof counts |
| Registered test | `study.py` | checked the law's predictions at new sizes on the atlas engine |

- **The card** (`card.md`) states the problem and the library: definitions, the target theorem,
  and an index of every file with its main lemmas. It says nothing about the method.
- **The sandbox** (`/home/user/pilot-sandbox`, built by `sandbox.py`) holds the card, the tools
  and the Lean library. It leaves out `docs/` and `examples/`, where the hand proof is.
- **The tools** are generic: finite fields with roots of unity, the library's torus models,
  exact periods on small tori, and a checker for Jordan blocks of a rule's adjoint.
- **The judge** makes three checks:
  - no library file changed (a sha256 manifest);
  - the proof builds against a fresh copy of the repository's library;
  - the repository's own pinned statement elaborates against it, and `#print axioms` shows only
    `propext`, `Classical.choice` and `Quot.sound`.

### What happened

The agent was launched at 19:14 UTC, reported at 19:29, and the judge passed it at 19:30
(`judgements/round-1.json`). One round, so no judge output was ever sent back. It took 35 tool
calls and about 204,000 tokens. The full log is `examples/llm-pilot/log.md`.

**The mechanism it found:**

1. **Stop one Frobenius step early.** 2^v steps of H1 are one step of 2^v H1. Multiplication by
   2^v embeds the torus G′ = Z/2m × Z/m, with (q, r) ↦ (q + 2r, r), onto the subgroup 2^v G of
   the hexagonal torus G. By the restriction lemma, P divides 2^v p exactly when p is a period of
   H1 on G′. The library's existing reduction goes one step further, to (Z/m)². That loses the
   Z/2 factor of G′ ≅ Z/2 × (Z/m)², and the factor is where the extra 2 lives.
2. **A Jordan block on G′.** Take ζ a primitive m-th root of unity, the character
   ψ₁(a, b) = ζ^a ζ^b and ψ₂ = ψ₁ · [a even]. Then adj ψ₁ = λψ₁ and adj ψ₂ = λψ₂ + μψ₁, where:
   - λ = ζ^±1 + ζ^±2 + ζ^±3, and ζ³λ = (1 + ζ)(1 + ζ²)(1 + ζ³);
   - μ = ζ^±1 + ζ^±2, and ζ²μ = (1 + ζ)(1 + ζ³).

   Both are nonzero once m ≥ 5. The library's `even_of_jordan` then makes every period on G′
   even.
3. P(m) is odd, so P does not divide 2^v P(m), and the 2-part is 2^(v+1).

It also explained why m ≥ 5 is needed: at m = 3, every character with λ ≠ 0 has μ = 0.

This is **a different route from the hand proof**. The hand proof goes to 2^(v−1) steps and
reads off a 2-part of 4 in a Z/4 subgroup. The agent stays at 2^v and needs only a 2 × 2 block.
It is the route the orchestrator had expected. It was worked out before the launch and not
shared.

**The Lean proof** is 168 lines (`HexTwoPart.lean`):
- `hexSubHom`, `hexSubMul`, `hexSubMul_injective`: the sub-torus and its embedding;
- `hexSub_even`: the Jordan block;
- `hexPeriod_hexH1_exact`: the target.

The agent reported three small Lean errors on the way, each fixed in one edit.

**Its numerical checks** (`proposal.py`) held 56 of 56 when the judge reran them. They cover:
- the embedding at 8 sizes;
- the reduction at 10;
- the Jordan block at m = 5 to 27;
- the law at 7 sizes;
- the m = 3 exception at 3.

**The registered test** held at all 15 sizes (`ledger.jsonl`, `records.jsonl`; `lattice-lab
verify` finds no problems):

| n | m | v | predicted period | held |
| --- | --- | --- | --- | --- |
| 412 | 103 | 2 | 18,014,398,509,481,976 | yes |
| 418 | 209 | 1 | 140,737,488,355,324 | yes |
| 424 | 53 | 3 | 1,073,741,808 | yes |
| 432 | 27 | 4 | 16,352 | yes |
| 480 | 15 | 5 | 960 | yes |
| 544 | 17 | 5 | 960 | yes |
| 576 | 9 | 6 | 896 | yes |
| 608 | 19 | 5 | 32,704 | yes |
| 704 | 11 | 6 | 3,968 | yes |
| 800 | 25 | 5 | 65,472 | yes |
| 832 | 13 | 6 | 8,064 | yes |
| 896 | 7 | 7 | 1,792 | yes |
| 768 | 3 | 8 | 256 (2^v, beyond the theorem) | yes |
| 512 | 1 | 9 | 1 (dies, beyond the theorem) | yes |
| 1024 | 1 | 10 | 1 (dies, beyond the theorem) | yes |

### Issues

- **The agent wrote to /tmp.** It put five scratch files in the session scratchpad, against the
  card, and said so in its report. That directory also holds the orchestrator's older scratch
  files. None of them contains the mechanism.
- **The harness had a bug.** The sandbox's `python` was a symlink to the venv's interpreter, and
  through a symlink it does not activate the venv. So sympy was missing, although the card said
  it was there. The agent reimplemented the cyclotomic factorisation it needed. Fixed for
  pilot 2.
- **Isolation was by instruction only.** The agent ran in the same container and could have read
  the hand proof. Its account is that it did not, and the different route is consistent with
  that, but the pilot cannot prove it. Fixed for pilot 2.

## What the pilots show, and what they do not

**They show that the loop's mechanics work end to end, twice, and now with real isolation.** A
precise card, a sandbox and an automatic judge were enough. Acceptance was decided by Lean, the
pinned statements and the axioms, not by the model's description of its work. In pilot 1 the
agent carried a technique from the library, the Jordan block of the XOR law's proof, to a new
setting. That needed a new idea, the intermediate sub-torus that keeps a Z/2 factor. In pilot 2,
the agent ran in a container that held nothing it could look the answer up in, and its whole
transcript shows it did not try.

**They do not show discovery, or reliability.**
- Each statement was given, known to be true, and proved by hand elsewhere.
- Each library held a closely analogous worked example, and the card named its lemmas. Pilot 2's
  was pilot 1's own proof, and the agent said it copied its structure. So pilot 2 is the easier
  test: it shows the adaptation is dependable when the analogy is close, not that the agent can
  find a new idea.
- Two runs, each on a different problem, and each passed first time. That says little about the
  failure rate.

## Next

- **A pilot where the agent must find the statement too:** give it the data, not the law. For
  example the hexagon at m = 3, or VO + T13, a triangle rule whose exact 2-part the library does
  not state.
- **An open question:** the m = 37 lead of [STATUS.md](STATUS.md), where nobody knows the answer.
- **Harness:**
  - the agent's branch name: the session was asked to push to `pilot-triangle-submission` and
    did, but its record first named the source branch, so the watcher and the judge accept
    either;
  - the transcript audit's path check reads `sed` patterns and URLs as paths. Its flags need a
    person, which is fine at this scale.
