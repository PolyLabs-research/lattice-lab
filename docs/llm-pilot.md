# The LLM-central pilots: three period laws and two open questions, worked by agents

**Result: in all five pilots so far, a fresh agent, given only a problem card and the Lean
library, passed the judge in its first round. In the third it also found the law itself, from
data. In the fourth, on a question nobody had answered, it found the mechanism, proved it in
Lean, and its general condition held at every one of 633 claims, 180 of them at held-out sizes
registered before it started. In the fifth, on a harder open question, it explained and proved
5 of 17 cases, said plainly that it could not explain the rest, and its condition held at all
1,381 claims, 414 of them at held-out sizes.** The judge accepted each proof, not the agent's own report:

- the proof builds against the real library;
- the statements match pinned copies;
- the axioms are only Lean's standard three.

In pilots 1 to 4 the registered predictions, at sizes nobody had computed, all held. In pilot 3 the agent's own
law also held at all 20 held-out sizes, which it never saw. In pilot 5 the orchestrator's own
registered expectation failed, at 6 of 14 held-out sizes; the agent's mechanism accounts for part
of that, and the rest is a new open question. All five proofs are now in the library:
`HexTwoPart.lean`, `TriTwoPart.lean` and `VOT13Law.lean` verbatim, `Cubes37.lean` and
`Cubes25.lean` with only their namespaces renamed.

| | Pilot 1: the hexagon law | Pilot 2: the triangle laws | Pilot 3: VO + T13's law | Pilot 4: the cubes at m = 37 | Pilot 5: the cubes at m = 25 |
| --- | --- | --- | --- | --- | --- |
| Given | the statement | the statements | a question and data | an open question, a census and data | an open question, a census remainder, a chance model and pilot 4's mechanism |
| Theorems | `hexPeriod_hexH1_exact` | `atlasTriPeriod_triE_exact`, `atlasTriPeriod_triEVOVS_exact` | `atlasTriPeriod_triVOT13_law`, with the agent's own `vot13TwoExp` | `period_w_dvd_87381` and five more, `period_r90_dvd`; and a `condition` in Python | `period_r3096_dvd` and four more; and a `condition` in Python |
| Where the agent ran | a subagent in the orchestrator's container | its own cloud session, whose container held only the sandbox | the same as pilot 2 | the same as pilot 2 | the same as pilot 2 |
| Isolation | by instruction only | a separate container, and the whole transcript audited | the same as pilot 2 | the same as pilot 2 | the same as pilot 2 |
| Time, tool calls | 15 minutes, 35 calls | 41 minutes (31 waiting for its mathlib build), 40 calls | 53 minutes (41 waiting for its build), 42 calls | 95 minutes, 131 calls; then a follow-up a person asked for, 20 minutes and 6 calls | 95 minutes, 108 calls |
| Judge | passed in round 1 | passed in round 1 | passed in round 1 | passed in round 1; the follow-up judged in round 2 | passed in round 1: 5 of 17 explained, none of 1,381 claims false |
| The agent's own checks | 56 of 56 | 54 of 54 | 63 of 63 | 39 of 39 | 31 of 31 |
| Registered test | 15 of 15 sizes | 40 of 40 predictions | 20 of 20, and the agent's law 20 of 20 | the census at 29 held-out sizes: no unexplained confinement, as registered; the agent's condition held at all 180 of its claims there | the orchestrator's expectation (chance) **refuted** at 6 of 14 sizes; the agent's condition explains 12 of the 44 unexplained confinements there, and held at all 414 of its claims |
| Route, against the hand proof | a different one | the same one | no hand proof existed for m = 1 | nobody knew the answer | nobody knew the answer |

    examples/llm-pilot/                 pilot 1: card, tools, sandbox, judge, study, log, submission
    examples/llm-pilot-triangle/        pilot 2: the same, plus setup.sh, audit.py, transcript/
    examples/llm-pilot-vot13/           pilot 3: the same, plus data/, exact.py, transcript.py
    examples/llm-pilot-37/              pilot 4: the same, plus census.py, evaluate.py
    examples/llm-pilot-25/              pilot 5: the same, plus the square family and the chance model

## Why pilots

The goal set earlier was a loop with the LLM at its centre: it proposes mechanisms, and machines
check them. Before aiming that loop at open questions, it needed a test on a problem whose
answer is known but which the agent could not look up. That makes it possible to judge the
loop's mechanics rather than the problem. The exact 2-parts of the parity laws were such
problems: each had a hand proof in [parity-lattices.md](parity-lattices.md#the-factor-2--2vn-proved),
and the library had the odd parts and the upper bounds, but not the exact 2-parts.

## Pilot 5: the cubes at m = 25

**The problem.** The census remainder ([census-remainder.md](census-remainder.md)) left one part
open: at m = 25, three atlas rules (triangle E + T7 + self, hexagon H1 + H3 + H13 and
H3 + H4 + H5) and **14 of the 32,767 symmetric square rules within distance 4** have every
eigenvalue a cube, against 0.24 and 1.7 ± 1.3 expected by chance, with no symmetry of any kind.
25 has 37's arithmetic (2^5 ≡ 7 and 7² ≡ −1 mod 25), but rule 90 is not confined there, so the
m = 37 mechanism does not apply as it stands. Nobody knew the answer.

**What the agent was asked for.** As in pilot 4: a `condition(f, m)` the judge can run on every
rule at every size, a proof, Lean optional. The card gave the family's confinements at 21 and
25, the remainder with the orchestrator's verdict on each entry, the chance model and its tools,
and pilot 4's condition.

**The registered test** was the orchestrator's, not the agent's: before the launch it registered
that the square family's census at the 14 odd sizes from 27 to 75 where the cubes are a proper
subgroup would show nothing beyond chance, once pilot 4's mechanism is counted
(`examples/llm-pilot-25/ledger.jsonl`). The judge also runs the agent's condition on the family
at those sizes, for which the agent was given no data.

**What happened** (`examples/llm-pilot-25/log.md`):

1. **Twisted pairs, in 11 minutes.** Three of the 14 family rules are exactly
   C(x, y) · C(x³, y³), with C = self + N4, self + D4 and N4 + D4. As 3 ≡ 2^7 (mod 25), the
   second factor's eigenvalue is the first's to the power 2^7, and the product is c^129 = (c^43)³.
   This is the known twisted-power mechanism with d = 3, which the census's check had not tried.
2. **Cube certificates, in 23 minutes.** The card's lead, turned around. For two more rules,

       3096 · (t(x) t(y))³ = Sh(3,1) + Sh(4,1) + Sh(7,1) + Sh(7,3) + Sh(7,4),

   with t(z) = z + 1/z and Sh(a, b) the shell of (a, b), and the right side is a union of shells
   that the dilation by 7 = 2^5 maps onto itself mod 25. So its eigenvalues lie in F(2^5), every
   one a cube in F(2^10), and off the axes f is such an element divided by a cube. On the axes f
   restricts to t · t(z³) = t^129. Pilot 4's mixed case needed rule 90 to be confined; a
   multiplier that enters as a cube needs nothing of its own. The general form, which the agent
   proved, is f · M^E ≡ B with B invariant under ×2^g and q | E, plus a check on the lines where
   M vanishes.
3. **`mechanism.py` at 48 minutes**, unchanged after that; Lean for all five by 74 minutes
   (`period 25 D ∣ 341`); report at 95 minutes, 108 tool calls.
4. **The rest.** For the other nine family rules and the three atlas rules it found no
   structure, and said so, with what it had ruled out. It proved an identity that ties a
   character of order 25 to one of order 5, λ(c)^341 = λ(5c) + a sum over necklaces, and argued
   that the chance model, which treats those as independent, underestimates: a model that keeps
   them together expects 6.1 of the nine (11.8 with two fibres coupled).

**The judge**, round 1 (`judgements/round-1.json`): `condition` explains 5 of the 17; it made
**967 claims at the training sizes and 414 at the held-out sizes, none false**, each checked by
the judge's own eigenvalue computation; it covers 19 of the census remainder's 45 entries and 12
of the 44 unexplained confinements at the held-out sizes; the Lean file builds against the real
library, all 39 theorems on the standard axioms; and the agent's own checks passed, 31 of 31.

**The registered held-out census refuted the orchestrator's expectation.** At 6 of the 14 sizes
(29, 35, 37, 53, 55 and 61) the family has more unexplained confinement than chance allows. 35, 53
and 55 hold exactly the three twisted pairs, and 29 holds them among its 16; the agent's
condition claims all twelve. ("Held-out" means the agent was given no data there, not that it
could not compute there: after its mechanism was fixed, it checked its own claims on the whole
family at 35 and on samples at 35, 45, 55 and 63, and on the atlas at four of the judge's
held-out sizes. Nothing it did at those sizes came before the mechanism.) With them counted, 29 has 13 left against a bound of
13.8. **But 37 has 16 square rules confined to the cubes that neither pilot explains**, against
0.6 expected, each with 9 or 10 free classes, and three of them (3461, 18246, 26883) are also
confined at 61. That is a new open question, found by the registered test.

**The audit** (`transcript/audit.json`, all 108 calls) found no MCP tools, no web access, no
subagents, no git beyond its own branch, and no step outside the checkout; its 27 flags are
Python divisions, `sed` patterns, an allowed read in `~/.elan`, and its own background tasks'
output files. Its only inputs were the prompt and five notifications of its own background tasks.

**The orchestrator's check** (`tests/test_cubes25.py`) multiplies every identity out again with
the orchestrator's arithmetic and the atlas's shells, and checks the five rules' odd parts at 25
and the twisted pairs' at 29, 35, 53 and 55 with `eigen.py`. The Lean file is in the library as
`Cubes25.lean`, its namespace renamed; it builds in about 3 minutes and its five theorems rest on
the standard axioms only.

**What it means.** Five of the seventeen are explained and proved, by a known mechanism
the orchestrator's census had applied too narrowly and by a new form of pilot 4's. The same
certificates explain 16 census entries at m = 13 that the orchestrator had filed as chance. The
agent said plainly what it had not explained, and gave a reason to think much of the rest at 25
is the chance model's error. The orchestrator was wrong twice, in its chance verdicts and its
registered expectation, and both errors were caught by checks it had set up for the agent.

## Pilot 4: the cubes at m = 37

**The problem.** At m = 37 the full bound is 2^18 − 1 = 3 · 87381, and 87381 is rule 90's own
period there. A census of all 1,274 shell rules of the atlas (`examples/llm-pilot-37/census.py`)
found **six** rules that none of the four known mechanisms touches with every eigenvalue a cube
at 37, and period 87381: square A4 + K8 + B4 + self, K8 + M8 + E4, C4 + L8 + M8, C4 + L8 + M8 + E4
and A4 + B4 + C4 + L8 + E4 + self, and triangle VS + T9 + T13 + self. Each has only 9 to 11
distinct eigenvalues up to Frobenius, so chance would confine it about once in 20,000 to 180,000.
None of them falls short at any other odd m from 9 to 161. This was open question 1 of
[STATUS.md](STATUS.md), and the orchestrator did not know the answer.

**What the agent was asked for.** A condition `condition(f, m)` on a rule and a size that forces
every eigenvalue to be a q-th power, implemented in Python so the judge could run it on every
rule at every size; a proof in `proposal.md`; Lean optional. The card gave the census up to 161,
the tools and the library.

**The judge's new checks.** It ran `condition` on all 1,274 rules at every odd m with ord_m(2)
even from 9 to 161 (65 sizes) and at the 29 held-out sizes from 163 to 333 registered before the
launch (`ledger.jsonl`), and checked each claim with its own eigenvalue computation. One false
claim would refute the mechanism as stated. The agent was told the held-out grid existed, not its
results.

**What happened** (`examples/llm-pilot-37/log.md`):

1. **A shared factor, in ten minutes.** Factoring the six, the agent found that three are the
   first one times rule-90 products: with a = x + 1/x and b = y + 1/y and W = A4 + K8 + B4 + self,
   K8 + M8 + E4 = ab W, C4 + L8 + M8 = (a + b) W, and A4 + B4 + C4 + L8 + E4 + self =
   (a + 1)(b + 1) W. No round of the atlas had looked for factors shared between rules.
2. **The mechanism, in 23 minutes**, which it calls half-Frobenius confinement. At 37,
   2^9 ≡ −6 and 6² ≡ −1, so the dilation by 6 acts on eigenvalues as the Frobenius x ↦ x^(2^9). A
   polynomial whose support mod 37 is invariant under it has every eigenvalue in F(2^9), and as
   3 does not divide 2^9 − 1, every element of F(2^9) is a cube in F(2^18). None of the six is
   invariant, but each becomes so after multiplying by rule-90 factors, whose eigenvalues are
   cubes at 37:

       W(x², y²) · t(x) t(y) t(xy) t(x/y) = the shell (±7, ±5), (±5, ±7),

   and 6 · (7, 5) ≡ (5, −7) (mod 37). C4 + L8 + M8 + E4 and the triangle rule have identities of
   the same kind. The general `condition` searches for such factorisations: a rule f(x^r, y^r)
   equal to rule-90 units times a core C, with C N invariant under the dilation by 2^g for g a
   proper divisor of sord(m), N a product of rule-90 factors. Without units, it is "f is invariant
   under a dilation by a power of 2", which puts the eigenvalues in a subfield, and explains 18 of
   the census's coincidences at m = 13.
3. **Lean**, once its mathlib build finished: `period 37 D ∣ lcm(511, period 37 r90)` for all six,
   in 21 minutes, with the triangle rule last. Rule 90's period at 37 was taken as given.
4. **Report** at 95 minutes.
5. **A follow-up.** Eight minutes after the report, the session received "Prove rule 90's cube
   property at 37 in Lean too". The orchestrator did not send it; the server records a person as
   its origin, typing in the Claude app. In 20 minutes the agent proved
   `period_r90_dvd : period 37 r90Offsets ∣ 87381` with an explicit cube root of t = z + 1/z in
   F(2^18) = GF(2)[t]/Ψ_37, and then `period 37 D ∣ 87381` for all six, unconditionally.

**The judge**, round 1, on the report as first submitted (`judgements/round-1.json`):

- `condition` explains all six (q = 786435 = 3 (2^18 + 1), every eigenvalue a cube in F(2^18));
- **sound: 453 claims at the training sizes and 180 at the held-out sizes, none false.** 30 of
  the training claims are confinements the four known mechanisms do not explain. At the held-out
  sizes it claimed nothing beyond them, and the registered census found nothing unexplained there
  either: at all 29, as the orchestrator had registered before the launch;
- it covers 24 of the census's 69 unexplained entries: the six at 37 and 18 at 13;
- the Lean file builds against the real library. The judge's axiom listing missed the agent's
  namespace, a harness bug since fixed; round 2, on the final branch, lists every theorem;
- the agent's own checks: 39 of 39.

**In the library.** The final branch's `Pilot.lean` (`6151adb`), with its namespace renamed, builds
in the orchestrator's library as `Cubes37.lean`, and `#print axioms` lists only `propext`,
`Classical.choice` and `Quot.sound` for `period_r90_dvd` and for all six `period_*_dvd_87381`.
The judge's round 2 reran every check on that branch (`judgements/round-2.json`): the same
mechanism results as round 1, and all 70 theorems of the file on the standard axioms, with no
`sorry`, `axiom` or `native_decide`.

**A caveat, found in pilot 5's audit.** "Held-out" means the agent was given no data at those
sizes, not that it could not compute there. Pilot 4's agent swept its condition over every odd m
up to 301 at 07:13, which covers 28 of the 29 held-out sizes, checking its own claims against
eigenvalues, and changed `mechanism.py` once afterwards (07:47, adding the pure case that acts at
m = 13). All 180 of its held-out claims were confinements the known mechanisms already explain,
so the held-out grid tested its soundness there, not new explanations.

**The audit** (`transcript/audit.json`, all 137 tool calls) found no MCP tools, no web access, no
subagents, and no fetch or listing of other refs. One step went outside the checkout: a
`find / -maxdepth 8` for mathlib's `CharP` sources, which found nothing; the agent reported it
itself. The other flags are Lean comment markers, Python divisions and `sed` patterns read as
paths.

**The orchestrator's check.** The identities were multiplied out again with the atlas's own
polynomials, not the agent's code, and all hold; `eigen.odd_part` gives 87381 for W at 37 and
511 = 2^9 − 1 for the shell.

**What it means.** The six are not six coincidences. They are one arithmetic fact about 37, a
square root of −1 that is a power of 2 and small enough to pair the atlas's shells, combined with
rule 90's own confinement there. By the agent's sweep up to m = 301, the mixed form of the
mechanism acts on the atlas's rules only at 37, which is why 37 looked unique. The remaining 45
entries of the census, mostly at 13, are still unexplained.

## Pilot 3: find VO + T13's law

**The problem.** VO + T13 is the triangle rule of round 3's twisted power. The library knew its
period on the atlas's triangular torus is 2^(a+1) P(s, m) for some a ≤ v, and nothing more about
a. The first two pilots gave the agent the statement. This one gave it a question and data:
find the exact power of 2 at every even n ≥ 4, as a formula in v and m; define it as
`vot13TwoExp`; and prove the pinned theorem

    atlasTriPeriod n triVOT13 = 2 ^ vot13TwoExp v m * period m triSVOT13Offsets

for m odd, v ≥ 1 and n = 2^v m ≥ 4, with the agent's own definition in it.

**What the agent had.** The card, the library (now with pilots 1 and 2's proofs), the tools, and
`data/vot13_periods.csv`: the exact period at every even n from 4 to 64. Nothing said that the
answer depends on m.

**What the orchestrator knew, and the agent did not.** At sizes all computed before, the exponent
is v + 1 for m ≥ 3, like the other triangle rules, and the period is 2^(v−1) at m = 1. The edge
rule has 2^v there and the edge+vertex rule dies, so VO + T13 matches neither, and no hand proof
covered the case. This law was registered at 20 held-out sizes from 408 to 1024 before the launch,
and held at all 20. The study recorded each exact period there, to judge the agent's law against.

**The judge's new checks.** The agent's law had to be a formula: `#eval` computed it at every
point of the data and of the held-out sizes, and at v = 100000, or the round failed. The law was
then compared with the data and with the held-out periods. The agent was told the held-out
comparison existed but never its result.

**What happened** (`examples/llm-pilot-vot13/log.md`):

1. **The law, from data, in three minutes.** The agent divided the odd part, computed with the
   tools, out of every row of the data. The quotient was always a power of 2, with exponent v + 1
   at m ≥ 3 and v − 1 at m = 1. It defined
   `vot13TwoExp v m = if m = 1 then v - 1 else v + 1`, the orchestrator's law.
2. **The proof, before Lean existed.** Eight minutes after launch it had written the whole proof,
   m = 1 included. It then waited 41 minutes for its mathlib build. On the first compile one
   `linear_combination` coefficient was wrong; it fixed that and pushed its report 53 minutes after
   launch.
3. **The judge passed it in round 1** (`judgements/round-1.json`). The law computed in 5.5 s and
   agreed with all 31 data rows and **all 20 held-out sizes**. All ten theorems in the file rest
   on the standard axioms. The audit found no step across the boundary.

**The mechanism** (`VOT13Law.lean`):

- **m ≥ 3** follows `TriTwoPart.lean`. On the sub-torus Z/2m × Z/m the same weights give a Jordan
  block with λ = 1 and μ = (ζ + 1/ζ)³. The agent derived μ from the twisted factorisation
  s = s_E(x, y) s_E(x³, y³) (`triangle_VOT13_twisted`), with λ multiplying and μ following the
  product rule.
- **m = 1 is new.** There is no nontrivial character, so no Jordan block. The agent proved a
  general fibre lemma, `gstep_eq_self_of_fibers`: a rule is the identity on a torus if its
  translations land an odd number of times on 0 and an even number of times on every other cell.
  It then proved three finite facts by kernel `decide` (49 translations, on tori of 8 and 32
  cells):
  1. s is the identity on Z/4 × Z/2, so by the restriction lemma 2^(v−1) is a period;
  2. 2s is the identity on Z/8 × Z/4, so s is an involution there;
  3. s is not the identity on Z/8 × Z/4: from one live cell at 0, the cell (6, 0) becomes live.
     So 2^(v−2) is not a period when v ≥ 3.

  At v = 2 the layer-parity argument makes the period even. So at m = 1 the period is exactly
  2^(v−1) = n/2.

This is the first pilot in which the agent was not given the statement, and its m = 1 case had
no proof of any kind before.

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

**They show that the loop's mechanics work end to end, five times, with real isolation in the
last four, and that the loop can answer a question its orchestrator could not.** A precise card,
a sandbox and an automatic judge were enough. Acceptance was decided by Lean, the pinned
statements and the axioms, not by the model's description of its work.

- In pilot 1 the agent carried a technique from the library, the Jordan block of the XOR law's
  proof, to a new setting. That needed a new idea, the intermediate sub-torus that keeps a Z/2
  factor.
- In pilot 2 the agent ran in a container that held nothing it could look the answer up in, and
  its whole transcript shows it did not try.
- In pilot 3 the agent found an unstated law from data, and it held at sizes it never saw. It
  then proved a case for which no proof existed, with an argument of its own: the fibre lemma and
  three finite checks, where the library's Jordan-block technique gives nothing.
- In pilot 4 nobody knew the answer. The agent found a factor shared by four of the six rules,
  then a mechanism, wrote it as a condition the judge could test on every rule at every size, and
  proved it. The condition held at 633 claims, 180 of them at held-out sizes.
- In pilot 5 the question was harder, and the agent answered part of it: five of seventeen
  cases, with a new form of pilot 4's mechanism and a known one the orchestrator had applied too
  narrowly. It reported the other twelve as unexplained rather than stretching its mechanism, and
  its condition made no false claim. The same checks caught the orchestrator: its chance verdicts
  on 16 census entries, and its registered expectation for the held-out census.

**They do not show reliability, or that the hard questions are within reach.**
- Pilot 3's law was easy to read off the data: one division per row. The orchestrator had found
  the same law beforehand, so the answer was known, if not to the agent.
- The m = 1 case is small. Its proof reduces to finite computations on tori of 8 and 32 cells.
- Each library held closely analogous worked examples, and the agents said they followed them.
- Pilot 4's mechanism is elementary once seen: a dilation that acts as half a Frobenius, and
  factors whose eigenvalues were already known to be cubes. The atlas's own tools could have
  found the shared factor W, had anyone looked for factors shared between rules.
- Its general condition is sufficient, not necessary: it searches a finite family, and leaves 45
  of the census's 69 entries unexplained.
- Pilot 5's answer is partial. Its search is bounded (one multiplier, small exponents), the
  twelve it left are unexplained, and its argument that most of them are chance rests on a
  model it fitted to the same family.
- Five runs, each on a different problem, each passed in the judge's first round. That says
  little about the failure rate, or about where the approach stops working.

## Next

- **The cubes at m = 37, again:** the held-out census found 16 square rules confined to the
  cubes at 37 that neither pilot's mechanism explains, against 0.6 expected, and three of them
  also at 61. That is the natural sixth pilot.
- **The rest at m = 25:** nine family rules and three atlas rules, which the agent argues are
  mostly the chance model's error. A chance model that keeps the fibres together could be
  registered and tested on a fresh family.
- **A harder law from data:** a rule whose period law the atlas has not settled, so that the
  law is not one division away. The rules round 3 left unexplained are candidates.
- **Harness:**
  - the agent's branch name: the session was asked to push to `pilot-triangle-submission` and
    did, but its record first named the source branch, so the watcher and the judge accept
    either;
  - the pilot branches cannot be deleted from the orchestrator's session (its git proxy refuses
    ref deletion), so each pilot leaves two branches behind. `branches.bundle` in each pilot's
    directory holds everything they had;
  - the transcript audit's path check reads `sed` patterns, URLs and Lean comment markers as
    paths. Its flags need a person, which is fine at this scale;
  - a person can message the agent's session in the Claude app. Pilot 4's follow-up came that way.
    It is recorded in the transcript with its origin, and judged as a separate round.
