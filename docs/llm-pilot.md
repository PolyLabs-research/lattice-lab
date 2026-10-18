# The LLM-central pilot: the hexagon law's 2-part

**Result: a fresh agent, given only a problem card and the Lean library, found the mechanism and
proved the theorem on its first attempt.** It took 15 minutes, 35 tool calls and about 204,000
tokens. The judge passed it, not the agent's own report:

- the proof builds against the real library;
- the statement matches a pinned copy;
- the axioms are only Lean's standard three.

The registered test, which predicted the period at 15 hexagon sizes nobody had computed, held at
all 15. The proof is now in the library as `proofs/LatticeProofs/HexTwoPart.lean`, verbatim.

    examples/llm-pilot/        the card, tools, sandbox builder, judge, registered study, log
    examples/llm-pilot/submission/   the agent's proof, proposal, checks, scratch files, report

## Why a pilot

The goal set earlier was a loop with the LLM at its centre: it proposes mechanisms, and machines
check them. Before aiming that loop at open questions, it needed a test on a problem whose
answer is known but which the agent could not look up. That makes it possible to judge the
loop's mechanics rather than the problem.

The problem: the hexagon law says that H1 (B135/S135) has period 2 · 2^v · R(m) on the atlas's
hexagonal torus of side n = 2^v m, for odd m ≥ 5. The library had proved the odd part and the
upper bound on the 2-part (`hexPeriod_eq_two_pow_mul`). The exact 2-part, 2^(v+1), had a hand
proof in [parity-lattices.md](parity-lattices.md#the-factor-2--2vn-proved) and no formal one.

## Design

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

## What happened

The agent was launched at 19:14 UTC, reported at 19:29, and the judge passed it at 19:30
(`judgements/round-1.json`). One round, so no judge output was ever sent back. The full log is
`examples/llm-pilot/log.md`.

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

## Issues

- **The agent wrote to /tmp.** It put five scratch files in the session scratchpad, against the
  card, and said so in its report. That directory also holds the orchestrator's older scratch
  files. None of them contains the mechanism.
- **The harness had a bug.** The sandbox's `python` was a symlink to the venv's interpreter, and
  through a symlink it does not activate the venv. So sympy was missing, although the card said
  it was there. The agent reimplemented the cyclotomic factorisation it needed.
- **Isolation was by instruction only.** The agent ran in the same container and could have read
  the hand proof. Its account is that it did not, and the different route is consistent with
  that, but the pilot cannot prove it.

## What the pilot shows, and what it does not

**It shows that the loop's mechanics work end to end.** A precise card, a sandbox and an
automatic judge were enough. Acceptance was decided by Lean, the pinned statement and the axioms,
not by the model's description of its work. An agent took a technique from the library, the
Jordan block of the XOR law's proof, and carried it to a new setting. That needed a new idea:
the intermediate sub-torus that keeps a Z/2 factor. It also needed the right character, the two
factorisations, and the reason for m ≥ 5. It wrote a correct proof without any feedback.

**It does not show discovery, or reliability.**
- The statement was given, known to be true, and proved by hand elsewhere.
- The library held a closely analogous worked example, and the card named its lemmas. So this
  tests adaptation, not discovery.
- It is one run.
- Isolation was not enforced.

## Next

- **More runs at this level:** the triangles' exact 2-part, and E + VO + VS. That would show
  whether this was luck.
- **A pilot where the agent must find the statement too:** give it the data, not the law. For
  example the hexagon at m = 3, or a triangle rule the library has no law for.
- **An open question:** the m = 37 lead of [STATUS.md](STATUS.md), where nobody knows the answer.
- **Harness fixes:** a real environment in the sandbox, and enforced isolation, for example a
  separate container.
