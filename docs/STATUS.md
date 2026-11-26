# Where we're up to

Written 2026-10-18, at the end of the session that ran the linear-rule atlas's third round, and
last brought up to date on 2026-10-21, after the seventh pilot, the rule-4850 deep dive, the
hexagon-family test and the quantum-codes test. It is for whoever picks this up next: what
exists, what has been established, what is open, and how to carry on.

## The three repositories

All three now live under **PolyLabs-research**, moved from `tripptytrip` on 2026-10-18. The work
is on the branch **`ccr-ab9f0bb1-qb20sx`** in each repository. Merging it is a decision for you.

- **lattice-lab** has a `main` branch, the default, which carries the website's hosting commits.
  They were merged into `ccr-ab9f0bb1-qb20sx`, which is ahead of `main`.
- **kepler**: an earlier pull request (#8) from the working branch was merged into `main`, and the
  working branch is ahead of it again.
- **gameoflife_advanced**: `main` is behind the working branch.

| Repository | Role | Visibility | Tests |
| --- | --- | --- | --- |
| [lattice-lab](https://github.com/PolyLabs-research/lattice-lab) | the questions, registered studies, ledgers, write-ups, Lean proofs, the website (this repository) | public | 214 |
| [kepler](https://github.com/PolyLabs-research/kepler) | fitting, ranking and predicting laws; exact integer laws; known constants | public | 308 |
| [gameoflife_advanced](https://github.com/PolyLabs-research/gameoflife_advanced) (LatticeLife) | the cellular automata, experiments and observables | public | 1043 |

- **The website.** [polylabs-research.net](https://polylabs-research.net) is built from `site/`
  in lattice-lab; [site/README.md](../site/README.md) says how to rebuild and deploy it. It
  covers every PolyLabs Research programme, with lattice-lab's section at `/lattice`, and links
  into lattice-lab on GitHub, at `main`.
- **Licences.** lattice-lab's code is under Apache-2.0 and everything else under CC BY 4.0
  ([README](../README.md#licence)). Kepler and LatticeLife have no licence yet.
- **Pins.** lattice-lab pins LatticeLife `f0ee136` and Kepler `0af9b28` (`pyproject.toml`,
  `uv.lock`). LatticeLife's pin is its branch `competition`: the working branch, whose commits
  after `256450b` change only the README, plus three commits of the scale-up plan
  (2026-11-23): the zoom-out module (`coarse-graining`, `d690cae`), the birth tie-break as a
  setting (`tie-break`, `456e044`) and several species without the app. Kepler's is current for
  code: every later commit on its working branch changes only the README.
- **The move.** Links, the Kepler pin's URL and the lockfile point at PolyLabs-research. The
  study ledgers still record `tripptytrip` URLs in their provenance. That is deliberate: they are
  hash-chained records of what ran, and GitHub redirects the old URLs.
- **Old checkouts** still push through the redirect, with a "repository moved" notice. To quiet
  it, run `git remote set-url origin https://github.com/PolyLabs-research/<repo>`.

## Picking up in a new session

```bash
# in each of the three repositories
git checkout ccr-ab9f0bb1-qb20sx

# lattice-lab
uv sync && uv run pytest              # 214 tests
for d in examples/*/; do [ -f "$d/ledger.jsonl" ] && uv run lattice-lab verify --lab "$d"; done

# working against local checkouts of the libraries instead of the pins
uv pip install -e ../gameoflife_advanced -e ../kepler    # then use `uv run --no-sync`
```

A registered study runs in four steps:
1. `python examples/<study>/study.py register` writes the predictions to `ledger.jsonl`.
2. Commit and push.
3. `python examples/<study>/study.py run --workers 4`. The harness refuses to run until the
   registration is committed and pushed.
4. If the run is interrupted, `study.py resume` finishes it.

`lattice-lab verify --lab <dir>` checks the hash chain, and that every prediction precedes its run
and every record follows the run's start. A study that names `rerun` (one stored record computed
again) also has sample records rerun and compared, as the loop's own records are.

## What has been established

The details are in each write-up. "Registered" means the predictions were committed and pushed
before the runs that tested them.

| Finding | Status | Write-up |
| --- | --- | --- |
| Square parity rule B1357/S1357: period 2^v(n) (2^sord(m) - 1) | confirmed in advance at every n up to 200; the 2-part, P(2^v m) = 2^v P(m), **proved in Lean** for every m > 1; the odd part checked by machine up to 999 except ten | [xor-periods.md](xor-periods.md), [xor-periods-proof.md](xor-periods-proof.md), [proofs.md](proofs.md) |
| Hexagon parity rule B135/S135: period 2 * 2^v(n) R(m) for odd parts m >= 5 (2^v(n) at m = 3; the torus dies at m = 1) | first law refuted at 3 of 70 sizes; the corrected law was confirmed at 100 and **proved for every even n**; the 2-part also **proved in Lean**, by an LLM agent | [parity-lattices.md](parity-lattices.md), [llm-pilot.md](llm-pilot.md) |
| Triangle parity rules: 2 * 2^v(n) (2^sord(m) - 1) | confirmed at 154 sizes; the 2-part is proved, and also **in Lean**, by an LLM agent; the odd part is checked by machine to 999 except ten | [parity-lattices.md](parity-lattices.md), [llm-pilot.md](llm-pilot.md) |
| Kepler finds the hexagon law itself, given 1D rule periods in its vocabulary | registered replay, 8 of 8 | [parity-lattices.md](parity-lattices.md#kepler-with-a-wider-vocabulary) |
| Atlas, round 1: Kepler's laws for 42 shell-built linear rules (38 unstudied) | blind; all 34 rules with a law kept a registered one at 1,930 new pairs | [linear-atlas.md](linear-atlas.md) |
| Atlas, round 2: the factorisation pattern | the 34 laws held at 624 harder pairs; the pattern was refuted on 116 new rules (7 of 113 failed); the failures showed cubes and dilations | [linear-atlas.md](linear-atlas.md#round-2-the-pattern-registered) |
| Atlas, round 3: the refined statement as a procedure, on 344 new rules | 11,315 of 11,358 held; **refuted** by 43. Every dilation and power held; a third mechanism (twisted power) was found and its expectation matched all 34 sizes; small-field coincidences at m <= 25; one case at 37, since explained by the fourth pilot | [linear-atlas.md](linear-atlas.md#round-3-the-refined-statement-registered) |
| Period = lcm of eigenvalue orders (odd tori); even sizes reduce to odd parts; round 2's cubes and dilation at every size; round 3's twisted power on the atlas's own torus | **proved in Lean**, standard axioms only; the torus models agree with the atlas's engines at every size checked | [proofs.md](proofs.md) |
| B2/S34 settling time on the hexagon grows like log L | found by the loop; replicated to L = 1024; power law rejected | [settling-time.md](settling-time.md) |
| Settling-time fluctuations: one shape and ratio across lattices (Gumbel values) | eight random rules on four lattice types; B2/S34's early miss was a low draw | [settling-time.md](settling-time.md) |
| Cumulative births under B1357/S1357 are always even | found in data, then proved | [capabilities.md](capabilities.md) |
| The cubes at m = 37: six rules have every eigenvalue a cube, because a dilation by 6 acts as half a Frobenius and combines with rule 90's own confinement | **answered by an LLM agent** in the fourth pilot, on a question the orchestrator could not answer; **proved in Lean** for all six, unconditionally; its general condition held at 633 claims, 180 at held-out sizes, none false | [llm-pilot.md](llm-pilot.md#pilot-4-the-cubes-at-m--37), [linear-atlas.md](linear-atlas.md#m--37-answered-by-the-fourth-pilot) |
| The cubes at m = 25: five of seventeen rules have every eigenvalue a cube, two by cube certificates (f (t(x) t(y))^3 is invariant under the dilation by 7 = 2^5) and three as twisted pairs C(x, y) C(x^3, y^3) | **found and proved in Lean by an LLM agent** in the fifth pilot (`Cubes25.lean`); its condition held at 1,381 claims, 414 at held-out sizes, none false; twelve remain unexplained, and the registered census refuted the orchestrator's chance expectation at 6 of 14 held-out sizes | [llm-pilot.md](llm-pilot.md#pilot-5-the-cubes-at-m--25) |
| Unit times cube: nine square-family rules are f = U g^3, with U a product of rule-90 or Psi_3 factors, so every eigenvalue is a cube at m = 37, and for three of them at 61 | **found and proved in Lean by an LLM agent** in the sixth pilot (`UnitCubes.lean`): 12 of its 19 targets, none of 1,547 claims false; the registered census at 17 new sizes found these nine at exactly the three sizes predicted, and nothing else unexplained | [llm-pilot.md](llm-pilot.md#pilot-6-the-square-family-at-m--37) |
| Rule 90 at primes p = 5 (mod 8) with 2 a primitive root: confined to the cubes exactly when eps^h lies in Z[sqrt p]; then the pyramid rule at p = i^2 + 1 is too | **proposed by Claude Fable in a consultation**, with an argument that is a proof once Dirichlet's class number formula fills its one-line step; registered and confirmed at 405 primes from 302 to 20,000 and 4 pyramid primes, none wrong | [consultations.md](consultations.md) |
| The ninth powers at m = 37: four of five rules with no known mechanism (699738, 985232, 1431278, 1968276) are line units times pilot 4's half-Frobenius cores, and the units' exact exponents add the third factor of 3 | chance first refuted by a registered radius-5 census (four independent such rules against 0.0066 expected); **found by an LLM agent (Claude Fable)** in the seventh pilot, its condition sound at all 1,715 claims, 533 at held-out sizes; its Lean failed to build in round 1 and was fixed in a second round over the API (`Ninth37.lean`) | [llm-pilot.md](llm-pilot.md#pilot-7-the-ninth-powers-at-m--37), [consultations.md](consultations.md#4-rule-4850s-ninth-powers-at-m--37-2026-10-20) |
| Rule 4850, the fifth: (x + 1/x + y + 1/y) · 4850 is two hexagons; an order-3 symmetry that exists only at 37 (5² + 3·2² = 37) gives λ · t_α t_β = W⁴; a norm formula in Gauss periods puts every eigenvalue's norm to F64 in F8*, which is the ninth-power condition | **explained, with a proof**, by a multi-agent deep dive; three independent checkers found it stands with repairs, which they supplied, and the orchestrator rechecked the chain (`tests/test_rule4850_proof.py`); not yet one document, and not in Lean | [the deep dive's report](../examples/rule-4850/deep/REPORT.md) |
| The hexagon family at m = 37: p a non-residue gives ninth powers, p a residue gives cubes | classified in the deep dive; **confirmed by a registered held-out test**: 35 of 35 tested predictions correct, at 37, 13 and eight other sizes; the six at the largest sizes (709 to 1861) were not tested, two over the 45-minute limit and four recorded as not run | [the deep dive's report](../examples/rule-4850/deep/REPORT.md#4-the-hexagon-family), `examples/hexagon-family` |
| A bivariate bicycle quantum code's logical qubits k are read off the torus's characters | **confirmed by a registered rediscovery test**: the character method agrees with linear algebra on 3,000 of 3,000 random codes and reproduces all 12 published k, IBM's gross code included | [next-direction.md](next-direction.md) |
| Codes of the published form on every stage-1 torus (n ≤ 200): which tori have codes, their k, and exact distances | **stage 1 of a census, exploratory**: 3,330 classes on 35 of 116 tori, every d exact by the search, 297 cross-checked by the program with none disagreeing, independently rechecked; the gross code has the highest k d²/n; an exact criterion for which tori have codes is proved by hand and matches all 116; stage 2, registered on the held-out tori, is next | [code-census.md](code-census.md) |
| The published distances of those 12 codes, [[288,12,18]] included | **reproduced by a registered test**, blind to the published values: an exhaustive search built here gives every published d exactly ([[288,12,18]] in 3 minutes, the gross code in 0.2 s), and an integer program (SCIP) agrees on 11 and brackets the twelfth at 13 to 18. The registered method check **failed** once: on 1 of 200 random codes SCIP returned a wrong optimum. The fault (SCIP's XOR presolving) was then fixed, the search made faster, and a second registered test on fresh codes found both instruments hold (`examples/qec-distance-2`) | [code-distances.md](code-distances.md) |
| An LLM agent, given a problem card and the Lean library, proves the hexagon and triangle laws' 2-parts, and finds and proves VO + T13's law from data | three pilots, each passed on the first attempt with no feedback; accepted by the judge (Lean, pinned statements, standard axioms); registered tests 15 of 15, 40 of 40 and 20 of 20. In the third the agent's own law held at 20 of 20 sizes it never saw, and its m = 1 case had no prior proof. The last two ran in their own containers, with their whole transcripts audited. The law was easy to read off the data, and the orchestrator knew it beforehand | [llm-pilot.md](llm-pilot.md) |
| Zooming out a parity rule by 2^k with the clock slowed by 2^k gives the rule itself; the scale-up instrument counts none where the scales match and a fair coin per supercell where they do not | **registered calibration, 296 of 296 held** (2026-11-23): no supercell differed in 10.1 million comparisons at blocks 2 to 128, grids up to 768; 36 controls each inside their exact binomial interval. The exact cases are `gstep_iterate_two_pow` and `restrict_iterate`; the controls' law is by machine, not in Lean | [scale-up-plan.md](scale-up-plan.md) |
| What a world of several species does on grids of side 32 to 256 is what it does on grids up to sixteen times as wide: means are constants, spreads fall as one over the side, and the rare species' blocks are as dense | **registered test, 124 of 124 held** (2026-11-23): 62 predictions at sides 512 and 1024 and the same 62 at sides 2048 and 4096, registered together before either part was run, for Life against HighLife and one five-species soup under two tie-breaks; no comparison beyond 2.5 standard errors. Not registered: set against each other, the large sides agree on eight of nine means; one sample of sixteen starts ran high, and fresh starts did not | [scale-up-plan.md](scale-up-plan.md) |
| Zoomed out, Life against HighLife is a map of where things still move: movement cannot start where nothing around it moved, and it spreads and dies by a rule that is the same at every time if it looks at the neighbours | **registered test, 43 of 45 held** (2026-11-24), side 2048, blocks 4 to 64 with the clock at the block: no block moved out of stillness in 902 million still neighbourhoods; a rule with neighbour counts learned early has under 1% more surprise late than one learned late (47% to 64% more for a rule that knows the block alone); the rule learned on side 1024 serves on side 2048 to 0.02%; a still block with one moving neighbour moves next with a chance of 0.0075 to 0.0086 at every block. Failed: the band guessed for the neighbours' share at block 64 (0.084 against at most 0.08), and a stillness claim with nothing to test it on | [scale-up-plan.md](scale-up-plan.md) |
| A rule alone seldom organises itself over a growing distance, and most that seem to are one kind of ground taking the whole grid; but one rule in six sorts into growing territories when it meets a copy of itself, and which rules do goes with how few of its own kind a cell needs to be born | **a search, exploratory** (2026-11-24), nothing registered: a screen of 2,407 worlds on a 256 grid called 42 growing; on a 1,024 grid from fresh starts most of the strong one-species growers are takeovers and three rules keep growing with their grounds level (Anneal, Day and Night, B012457/S14); every one of 1,196 random rules against its copy: 202 hold territories, 112 under both tie-breaks, 191 of them patches when alone, in 5%, 15%, 57%, 50% and 1% of the rules whose births need 0, 1, 2, 3 and 4 or more of their own kind (a cut read off the first 458 rules that held on the other 738); a zoom-out by two goes with waiting four to eight times as long in the worlds that keep growing; the soups as drawn are patches nineteen times in twenty | [scale-up-plan.md](scale-up-plan.md) |
| Which rules hold territories against a copy of themselves goes with how few of its own kind a cell needs: to be born, and to last | **registered test, 10 of 10 held** (2026-11-24), on 600 fresh rules of a random draw from a fresh start, each against its copy under both tie-breaks from two starts, and 242 more rules for the second claim: territories in 4.8% of the rules born on none of their own kind, 13.5% of those that need one, 61.5% of those that need two or three, none of 43 that need four or more; among those that need two or three, 82% where a cell cannot last on one or two against 53% where it can, and 84 of the 85 such rules that live; of rules holding under one tie-break only, 35 of 41 under the standoff; of 21 rules that organise alone, one holds. Every number within 0.08 of the exploratory screen's | [scale-up-plan.md](scale-up-plan.md) |
| Zoomed out, a world of territories has a coarse description that works: who leads each block, and a table of what blocks with as many rival neighbours did next, runs the world on without its cells | **a first look, exploratory** (2026-11-25), nothing registered: two rules against their copies (B245678/S3678, whose grounds are still, and B23467/S4568, whose grounds are busy) on a 1,024 grid to generation 4,096, eight starts each, read through blocks of 4 to 32 on two clocks. Run on by itself from generation 1,024, the rule's world has the real world's leader in all but 7% to 12% of the blocks 3,072 generations later at blocks of 4 to 16 (a fifth of the blocks change leader meanwhile) and ends within about 5% of its walls at blocks of 16 and 32; the rule learned in one world serves in the other to within half a percent of its surprise from blocks of 8; it is the same early and late to 0.24% at blocks of 4 and 3% at 16; from rung to rung it changes on both clocks, by 7% to 16% with the clock at the block and by 2% to 9% with the clock at its square, less at each rung | [scale-up-plan.md](scale-up-plan.md) |
| A coarse rule stands in for a world of territories, and it is one rule with a pace for worlds whose grounds fill: who leads each block, and what blocks with as many rival neighbours did next | **registered test, 73 of 89 held** (2026-11-26; 8 failed, 8 not tested), six worlds on a 1,024 grid to generation 4,096 from fresh starts. All 58 claims about the first look's two worlds held at its figures: a block changes hands by being surrounded; the rule learned early serves late to 0.2% at blocks of 4 and 2.6% at 16; run on by itself for 3,072 generations it keeps the walls and is amiss in 0.36 to 0.54 of the blocks that change leader; each world's rule serves in the other to 0.5% from blocks of 8; from rung to rung it changes on both clocks, less on the square clock, and is still 4% short at blocks of 16. Of three worlds never zoomed out, a near relative follows the still world's rule as it is (0.5% to 0.6%, and that rule runs it on), another still world follows it at half the pace (0.5%; 1.8% to 2.5% as it is, which failed), and a sparse world on another clock not at all (54% to 60%, failed). In the control, a world whose territories set, the rule is three times as surprised as the world's own. One failure by a hair of a bound (0.70003 against 0.70) | [scale-up-plan.md](scale-up-plan.md) |
| The class of worlds one coarse rule runs is the full ones, not the ones that share its clock | **registered test, 54 of 128 held** (2026-11-26; 55 failed, 19 not tested), 38 worlds never zoomed out, chosen by rule from step 4c's runs (11 that fill their grid, 27 that hold territories without filling it), on a 1,024 grid to generation 4,096. 29 keep the still world's clock (walls thinning as the 0.40th to 0.54th power of time), 5 have set and 4 are slower. Of the 29 the still world's rule serves 10 within 1% and 4 more within 2%, every one with over half its grid live, and misses the other 15 by 4% to 38%: the registered claim that the clock says whether the rule serves **failed for 20 worlds**. Weighted, the class is 23% of the rules of a random draw that grow territories. Run on by itself at the pace a world's walls give, the still world's rule keeps 19 of the 29 (and beats the world's own rule in 23). The pace by the rule and the pace by the walls agree within half again in 8 of the 10 worlds served, and not outside them. Three filling worlds keep a slower clock | [scale-up-plan.md](scale-up-plan.md) |
| From rung to rung the coarse rule of a world of territories changes less each time, and the rule of one rung runs the rung above; it has not stopped changing | **registered test, 22 of 22 held** (2026-11-26), the still and the busy world on a 2,048 grid to generation 16,384, eight fresh starts each, read through blocks of 4, 8, 16 and 32, each at the age that matches it. At the start of its age a world has as many walls at every rung (within 7% and 3%). The rule from the rung below has 8.6%, 2.8% and 1.4% more surprise than the rung's own in the still world and 5.6%, 3.0% and 1.6% in the busy one. Used as the rule of the rung above and run on by itself, it ends amiss in 6% to 15% more blocks than the rung's own rule, which at blocks of 32 is amiss in 0.51 and 0.39 of the blocks that changed leader. Read after the verdict (exploratory): the gaps compound as squares of distances (from two rungs down, 8% and 9%), so the steps shorten by three tenths a rung and not by half, and what still changes is how often a block with three or four rival neighbours changes hands | [scale-up-plan.md](scale-up-plan.md) |
| The large grids agree with each other: between sides 1024 and 4096 the pair's live fraction, species balance and mixing do not creep with the size of the grid | **registered test, 9 of 9 held** (2026-11-23), on fresh starts (384, 96 and 32): each pair of sides agrees within 0.0002 for the live fraction by its 99% interval (the largest difference is 0.00006 ± 0.00003), 0.0028 for the species balance and 0.00053 for the mixing. Not registered: 0.04% ± 0.04% change in the live fraction for each doubling of the side | [scale-up-plan.md](scale-up-plan.md) |
| The birth tie-break changes a world of several species only where contests are common | **registered test, 15 of 15 held** (2026-11-23): the standoff against the random draw; no difference in two Life-like pairs (contests 0.4% of births), nor in five soups with rare contests; in all nine soups where a fifth or more of births are contested the standoff lowers the live fraction, by 0.04 to 0.46 of the grid | [scale-up-plan.md](scale-up-plan.md) |

## The atlas, where it stands

A shell rule is linear over GF(2): one Laurent polynomial f on the square or hexagon, and on the
triangle a 2 x 2 matrix with M^2 = s I. At an odd part m, the odd part of its period is the lcm of
the multiplicative orders of its eigenvalues. Those are f evaluated at pairs of m-th roots of
unity, and they lie in F(2^sord(m)), so the period divides the full bound 2^sord(m) - 1. The
current statement is that the period **reaches the full bound unless something confines the
eigenvalues**. Eight mechanisms are known, each a theorem once its inputs are known:

1. **one-dimensional splitting:** the eigenvalues are products of a 1D rule's (rounds 1 and 2);
2. **an odd prime power** g^k: the eigenvalues are k-th powers (round 2);
3. **a dilation** h(x^p, y^p) with p dividing m: the rule lives on the m/p torus (round 2);
4. **a twisted power** g(x, y) g(x^d, y^d) where d = +-2^k mod m: the eigenvalues are
   lambda^(1 + 2^k) (round 3, triangle VO+T13). Cubes are the case d = 2.

5. **a dilation acting as part of a Frobenius** (the fourth pilot, at m = 37): if (x, y) ↦ (x^n,
   y^n) with n = 2^g mod m leaves a polynomial unchanged, its eigenvalues lie in F(2^g). At 37,
   2^9 ≡ −6, and each of six rules becomes such a polynomial after multiplying by rule-90 factors,
   whose eigenvalues are cubes there. So every eigenvalue is a cube. Without the rule-90 factors it
   also explains 18 of the coincidences at m = 13.
6. **a cube certificate** (the fifth pilot, at m = 25): if f · M^E is invariant under such a
   dilation and 3 divides E, every eigenvalue of f is a cube whether or not M is confined, as long as f is
   checked on the lines where M vanishes. At 25, 2^5 ≡ 7 and f · (t(x) t(y))^3 is invariant under
   ×7 for two square rules.
7. **a unit times a power** (the sixth pilot, at m = 37 and 61): f = monomial × ∏ Φ_e(X_w)^k ×
   h^q exactly, where each unit whose exponent q does not divide takes q-th-power values at m, by
   rule 90's confinement or because e ≡ ±2^a. Nine square-family rules are U g³ this way.
8. **exact exponents** (the seventh pilot, at m = 37): counting each line unit's exponent exactly,
   instead of bounding it by rule 90's cube confinement, can find one more factor of 3. Four
   radius-5 rules, line units times the cores of mechanism 5, are ninth powers this way.

Rule 4850 at 37 is confined by none of these. The deep dive found its cause (see the open
questions below).

On top of these come **coincidences in small fields**. At m = 13, 15, 21 and 25, rules with only 3
to 7 distinct eigenvalues sometimes have all of them in a subfield or in the cube subgroup. Above
m = 37, in 6,365 round-3 predictions, the only failures were the twisted power's. A census of all
1,274 shell rules (`examples/llm-pilot-37`) leaves 45 unexplained entries from 9 to 161, mostly at
13, and none at the 29 held-out sizes up to 333; [census-remainder.md](census-remainder.md) sorts
them. Some of what looked like coincidence is not: the fifth pilot's cube certificates explain 16
of those at 13 and 3 at 21, and its twisted pairs (mechanism 4 with d = 3, which the census had not
tried) explain three square rules at 25, 29, 35, 53 and 55. The seventh pilot's condition covers
27 of the 45, among them 10 that no earlier condition covered.

**Tools.**
- `examples/linear-atlas-3/eigen.py` computes the odd part from the eigenvalues in seconds. It
  agreed with all 11,662 exact records of round 3, and it is the checker to use from now on.
- `examples/linear-atlas/factor.py` (`split`) decides whether a polynomial has a 1D factor,
  completely.
- `examples/linear-atlas-3/atlas3.py` (`predict`) is the procedure.
- `examples/linear-atlas-3/failures.py` (`factor2d`) factors in two variables, slowly; it is
  capped.

## Open questions, roughly in order

**A new direction: scaling up** ([scale-up-plan.md](scale-up-plan.md), 2026-11-23). A ladder
from a rule to its large-scale law: zoom out by blocks, propose a coarse rule, and test whether
running then zooming out matches zooming out then running.
- **Step 0 is done: calibrated.** `examples/scale-up-linear` tried the instrument on
  LatticeLife's four parity rules, where the answers are known. All 296 registered cases held:
  no supercell differed at blocks from 2 to 128 on grids up to 768 x 768 (10.1 million
  comparisons), and the 36 controls at mismatched scales each fell inside their exact binomial
  interval. The run took 3.5 minutes on one core.
- **Step 1 is done: the instrument lives in LatticeLife** (`experiments.coarse`, branch
  `coarse-graining`), with a dilated adjacency and wrapped grids built without loops. Its gate
  passed: LatticeLife's module reproduces all 3,084 records of the calibration
  (`examples/scale-up-linear/promote.py`, `promotion.json`). A study can now name `rerun`, and
  `lattice-lab verify` then reruns its records.
- **The birth tie-break is a setting** in LatticeLife (2026-11-23, built ahead of step 2):
  the random draw as before, or `standoff`, `strongest` or `weighted`. With `standoff` or
  `strongest` a world of several species is a function of its grid. First counts, exploratory:
  the tie-break decides under half a percent of births in Life-like contests, and about 38%
  of them in `autorun`'s soups of several species with random rules. Whether the kinds differ
  at large scale has not been tested.
- **Step 2 has started.** LatticeLife runs several species without the app
  (`experiments.competition`). A first look under the draw (`examples/scale-up-compete`,
  exploratory) found that Life-like pairs coexist, with no species lost in 600 generations, and
  that soups stay active. A registered test then compared the draw with the standoff
  (`examples/scale-up-tie-break`): all 15 predictions held. The tie-break changes nothing
  measurable where contests are rare, and lowers the live fraction by 0.04 to 0.46 of the grid
  where they are a fifth or more of births.
- **Step 2 is done.** Laws against time and size (`examples/scale-up-compete/laws.py`,
  exploratory) for Life against HighLife under the standoff and for one soup under both
  tie-breaks, at seven sides from 32 to 256: no mean depends on the side, every spread falls as
  one over the side, and the one thing that does depend on size is which species survive (the
  soup keeps all five in 6% of runs at side 32 and 91% at 256).
- **Step 3 is done.** The registered test of those laws at larger sides, in two parts
  registered together before either was run (2026-11-23). Before registering, the step-2
  records showed why the soup's rare species survives only on large grids: what is left of it
  is 2 x 2 blocks that nothing can break, as dense at every size, and a small grid often has
  none. Both parts held in full: 62 of 62 predictions at sides 512 and 1024
  (`examples/scale-up-sizes`, 32 starts each, run here) and 62 of 62 at sides 2048 and 4096
  (`examples/scale-up-sizes-large`, 16 starts each, on a RunPod pod for $2.57). The means are
  the small grids' constants, the spreads fall as one over the side, every species survived
  all 288 runs, and the rare species' blocks are as dense as predicted. One registered sample
  (the pair at side 2048) ran high against the other large sides, and sixteen fresh starts did
  not.
- **Step 3b is done: the large grids agree with each other.** A registered test on fresh
  starts (`examples/scale-up-gap`: the pair at sides 1024, 2048 and 4096; 384, 96 and 32
  starts; on a RunPod pod for $2.49) held on all nine predictions. The three sides' live
  fractions are within 0.00007 of each other, the gap of 0.0002 that step 3 left is outside
  every 99% interval, and a line through the three sides changes by 0.04% ± 0.04% for each
  doubling of the side.
- **Step 4, the zoom-out, has its first results** (2026-11-24, `examples/scale-up-closure`).
  An instrument reads a fine world through blocks with the clock at the block, learns a
  coarse rule as a table from some starts and tries it on others; it passes two exact checks
  on LatticeLife's own engine. A first look at the pair and the soup found that who leads a
  block is frozen and says little, and that what is left to describe is where things still
  move. A registered test on a torus twice as wide then held on 43 of 45 predictions: no
  block moves out of stillness; in the pair movement follows a rule that is the same early
  and late if it looks at the neighbours, the same on both tori, and has one entry that is
  the same at every block; run on by itself the rule keeps up with the fine world for about
  eight coarse generations. The two that failed were a band guessed for a block of 64 and a
  claim that could not be tested. Step 5 is not built.
- **Step 4b, the search for a world that organises itself, is done** (2026-11-24,
  `examples/scale-up-search`; exploratory, nothing registered). Step 4's two worlds are
  patches at every age, so the lab's rule sets were searched for one that is organised over
  a growing distance, read off how much more the block sums scatter than independent cells
  would (the correlation area). A screen of 2,407 worlds on a 256 grid called 42 growing,
  about one rule set in fifty. Run again on a 1,024 grid from fresh starts, most of the
  strong ones are takeovers: one kind of ground ends with the whole grid. What keeps growing
  is a world whose grounds stay level: Anneal, Day and Night and one rule of the draw
  (B012457/S14). A rule that grows alone usually loses its domains to a rival, and Anneal
  dies against its own copy. But growing alone was the wrong thing to look for: given a
  copy of itself as a rival, one rule in six of a random draw sorts into territories (202
  of 1,196, and 78 of them from either start under either tie-break), and nearly all of
  those are patches alone. What they share is how few of its own kind a cell needs to be
  born: territories in 5% of the rules that need none, 15% of those that need one, 57% and
  50% of those that need two and three, and 1% of those that need four or more. In the
  worlds that keep growing a zoom-out by two goes with waiting four to eight times as
  long, not twice, so the next zoom-out has to choose its clock. Which world to take up
  the ladder is decision D9 of the plan.
- **Step 4c, the registered test of which rules hold territories, held on all ten
  predictions** (2026-11-24, `examples/scale-up-territories`). The two cuts of step 4b were
  read off its own runs, so they were tried on 600 rules no run had used, from a start no
  run had used, with 242 more rules for the second cut. Territories against a copy in 4.8%
  of the rules born on no neighbours of their own, 13.5% of those that need one, 61.5% of
  those that need two or three and none of the 43 that need four or more; among the rules
  that need two or three, in 82% of those whose cells cannot last on one or two against 53%
  of those whose cells can; and in 84 of the 85 rules that need their own kind for both and
  live. The ledger verifies and 24 records recomputed from scratch match.
- **Step 4d, a first look at worlds of territories zoomed out, is done** (2026-11-25,
  `examples/scale-up-closure-territories`; exploratory, nothing registered). Two of the
  worlds steps 4b and 4c found (B245678/S3678 and B23467/S4568, each against its copy) were
  read through blocks of 4 to 32 with step 4's instrument, on the block clock and on the
  clock these worlds keep, the square of the block. Step 4's worlds had no coarse rule
  worth the name; these have one. Who leads a block changes by a rule that looks at how
  many neighbours the rival leads. Run on by itself for 3,072 generations, with no cells
  under it, that rule keeps the world's walls (within about 5% at blocks of 16 and 32) and
  has the real world's leader in all but 7% to 12% of the blocks, where supposing nothing
  moved is wrong in a fifth. The rule of one world serves in the other to within half a
  percent from blocks of 8, though the two rules share nothing cell by cell. It is not the
  same from rung to rung on either clock, but on the square clock the difference shrinks at
  each rung: 9%, 4% and 3% in one world, 7%, 5% and 2% in the other. What to register from
  it is decision D10 of the plan.
- **Step 4e, the registered test of the zoom-out of territories: 73 of 89 predictions
  held** (2026-11-26, `examples/scale-up-closure-territories/study.py`; run on a rented pod
  for $0.96). Six worlds on a 1,024 grid from fresh starts: the first look's two, three no
  run had zoomed out, and a control whose territories set. Everything the first look saw of
  its two worlds held on fresh starts (58 claims of 58), and its tables, tried unchanged on
  starts they had not seen, are as good as tables learned from them. In the control the
  still world's rule is three times as surprised as the world's own and wrecks it when run
  on. The three unseen worlds gave three answers. A near relative of the still world's rule
  follows that rule as it is. Another still world follows it at half the pace, and its
  walls, read with no coarse rule at all, say the same half (exploratory). A sparse, busy
  world does not follow it at any pace: its blocks change hands in proportion to the rival's
  neighbours, it has no clean territories at any block, and its walls thin as the 0.27th
  power of time where the others have about a half. So the coarse rule is one rule with a
  pace for worlds whose grounds fill, and the class has an edge. Eight claims failed: one by
  a hair of a bound I drew (0.70003 against 0.70), three that are the pace, four that are
  the edge. The ledger verifies, and six run-ons and five fine runs recomputed here match
  the pod's byte for byte. Where next is decision D11 of the plan.
- **Step 4f, how wide the class is: 54 of 128 predictions held, and the claim it was built
  to test failed** (2026-11-26, `examples/scale-up-class`; on rented pods, $3.22 in all).
  38 worlds no run had zoomed out, chosen by rule from step 4c's records. Nearly all of them
  coarsen as the still world does: 29 thin their walls as about the square root of the
  time, 5 have set, 4 are slower. But the still world's rule serves only 10 of the 29
  within 1% (14 within 2%), and what those have in common is not the clock but that more
  than half their grid is live; below that the rule is off by 4% to 38%. I had registered
  that the clock would tell, and it does not (20 failures); and that the pace at which the
  rule serves a world is the pace its walls give, which is loosely so inside the class and
  meaningless outside it. What did hold up is the run-on: at the pace a world's walls give,
  the still world's rule carries 19 of the 29 worlds for 3,072 generations, including 6 it
  does not serve, and does it better than the world's own rule in 23, because in a thin
  busy world a block's own table learns the flicker of its leader and not where the walls
  go. The class is about a quarter of the rules of a random draw that grow territories.
- **Step 4g, one more rung: all 22 predictions held, and the rule has not stopped changing**
  (2026-11-26, `examples/scale-up-rung`; on a rented pod, $4.01). The still and the busy
  world on a grid of side 2,048 to generation 16,384, so that blocks of 32 are read at the
  age that matches them. The fourth rung is the same picture as the three below it. The rule
  from the rung below has 1.4% and 1.6% more surprise at blocks of 32 than the rung's own,
  where it had 2.8% and 3.0% at blocks of 16 and 8.6% and 5.6% at blocks of 8. The ladder's
  own move, which no step had run, works: a rule learned from blocks half the size, used
  unchanged and run on by itself, ends amiss in 6% to 15% more blocks than the rung's own.
  Read after the verdict (exploratory): the rule moves the same way at every rung, so the
  gaps compound (from two rungs down 8% and 9%, twice the sum of the steps between) and the
  halving gap is a step shortening by three tenths; what still moves is how often a block on
  a wall, with three or four rival neighbours, changes hands, which falls by half and by a
  quarter at every rung. By that pattern a rule that has stopped changing is three or more
  rungs up, and a rung costs sixteen times the last. The ledger verifies; 63 of the 64
  records computed again here from the leaders the pod kept, and one whole fine run made
  again here from its start, match the pod's byte for byte. Where next is decision D12 of
  the plan.

**A direction with an application** ([next-direction.md](next-direction.md)): the ring every
result here lives in is the ring of bivariate bicycle quantum codes (IBM's gross code), and their
logical qubits are read off the same characters. Its first step, a registered rediscovery test
against linear algebra and twelve published codes (`examples/qec-bb`), passed: 3,000 of 3,000
random codes agree and all 12 published k are reproduced. Step 2's first part, the published
distances (`examples/qec-distance`, [code-distances.md](code-distances.md)), reproduced all twelve
with an exhaustive search; its integer program failed one method check through a SCIP fault.
The fault was traced to SCIP 10.0's XOR presolving and fixed (distance.SCIP_FIX), the search
was given iterative deepening, and a second registered test on fresh codes
(`examples/qec-distance-2`) found that both instruments hold. Its control, SCIP's unfixed
defaults, was wrong on 3 fresh codes.

**The census, stage 1** (`examples/qec-census`, [code-census.md](code-census.md); exploratory, not
registered):
- **What ran.** Every code of the published form on 116 tori with n ≤ 200, the held-out tori
  untouched. There are 3,330 classes with k > 0, on 35 tori. Each has an exact d by the search;
  297 were cross-checked by the program (284 agree, 13 consistent), and an independent recheck
  found no difference.
- **The published codes.** The gross code has the highest k d²/n of all. [[90,8,10]] and
  [[108,8,10]] are best at their n; [[72,12,6]] is second at 72, behind a [[72,8,8]].
- **Structure.** Proved: an exact criterion for which tori have codes, and formulas for the
  maximum k. Patterns: a linear distance law for some character types, and the fact that the best
  codes reduce mod 3 to one [[18,8,2]] base code.
- **Stage 2** (registered, `examples/qec-census-2` plus the continuation `examples/qec-census-2b`
  after a capacity fault in census.c):
  - H1 to H7 and H9 hold on the 122 held-out tori. That includes the linear distance law, exact
    at all 19 instances, up to d = 20 at n = 300.
  - H8, the mod-3 base pattern, fails on 6 x 18.
  - Stage 2's own registered verdict stays "incomplete"
    ([code-census.md](code-census.md#stage-2-the-registered-test)).

**Census stage 3b/3c: every weight-6 code on the 122 held-out tori** ([code-census.md](code-census.md#stage-3b3c-every-weight-6-code-on-the-held-out-tori-registered), registered 2026-10-24, run to 2026-10-28). **Verdict: fail.**
- **P3, the decisive prediction, fails.** [[294,10,20]] (on 3 x 49 and 7 x 21) has k d^2/n =
  13.61, above the published [[288,12,18]]'s 13.5. Close behind are [[288,8,22]] (13.44) and
  [[288,12,18]] on the unexposed 4 x 36.
- **P1 and P2 fail.** The best d is not always non-increasing in k (Z_105 tori, and one class pair
  on 7 x 21). The best d reaches 1.42 sqrt(n), beyond the 1.40 envelope.
- **P0 and P4 hold.** Criterion E held on 122 of 122 tori and the k sample on 6,100 codes. On
  2 x 48, Liang et al.'s [[192,8,16]] is the best code at k = 8.
- **Deviations, disclosed.**
  - Stage 3b hung at 2 x 67 in a trial-division routine. Stage 3c continued it with stage 3b's
    predictions verbatim and two registered in-process fixes.
  - Four cloud restarts lost the work on the tori in progress, and the last 25 tori ran on a
    RunPod CPU pod.
  - Its faster CPU settles more searches inside the 30-minute wall-clock limit. No verdict depends
    on the machine, and isomorphic tori agree across both machines.
- **Spot-check (2026-10-29): agreement.** A fixed sample of 20 frontier codes went through 431
  jobs with other tools: SAT/DRAT, DistQLDPC's two engines (Chen, Jafari and Lai,
  arXiv:2606.12445; github.com/guluchen/DistQLDPC, commit 8fe913e), SCIP, an unpruned search,
  the other logical type and long windows. No contradiction and no error.
  - 1 sampled code is certified by a checked DRAT proof, as are 8 smaller ones.
  - 9 are confirmed by a second method, including both [[294,10,20]] and [[288,8,22]].
  - 10 are confirmed by a second implementation (DistQLDPC's cluster engine).
- **Stage 3d (2026-10-30, registered): pass.** The 154 classes left unfinished on the 9
  "incomplete" tori all have d = 24, by DistQLDPC's cluster engine, with verified witnesses. The
  parity of d predicted this at registration.
  - P2 now fails on those tori except 3 x 49: [[n,4,24]] for n from 270 to 288, above the cap
    of 22.
  - No judged stage 3b/3c torus is left incomplete. The combined verdict stays fail.
  - Two exposed tori, which the verdict reports but does not judge, keep a lower bound at
    k = 4: 9 x 15 (d >= 22; its isomorphic twin 3 x 45, which carries the same codes, is
    settled at 24) and 6 x 24 (d >= 22). Stage 3d reran only judged tori.
- **Review dashboards (2026-11-02).** A private dashboard suite for reviewing the census:
  frontier, structure, populations, confidence, every registered study's predictions, and
  operations. Its data layer is `examples/qec-census-4/dashboards/build.py`, tested in
  `tests/test_census_dashboards.py`; the plan is [census-dashboards-plan.md](census-dashboards-plan.md).

**Census stage 4: the 110 tori with n = 302 to 400** ([code-census.md](code-census.md#stage-4-the-laws-refitted-and-tested-up-to-400-qubits-registered), registered 2026-10-30, run to 2026-11-05). **Verdict: fail.**
- **What ran.** Every weight-6 class on 110 tori: 633,390 classes on the 74 tori with codes.
  Exact distances came from DistQLDPC's cluster engine (Chen, Jafari and Lai, arXiv:2606.12445;
  commit 8fe913e), with 4 CPU-hours per class and a checked witness for every d. 13,380 exact
  runs took 5.4 days on one 32-vCPU pod. None errored.
- **E, the fitted envelope, fails** on 3 x 51. [[306,4,26]] is one even step above the cap of 24.
- **S2, the ceiling, fails.** [[384,12,24]] scores k d²/n = 18.0, above 17.0.
- **G and S1 pass.** Ten tori pass stage 3's d/√n record; the best is [[354,4,28]], at 1.488.
  29 tori beat the [[294,10,20]]'s score; the best is [[384,12,24]].
- **P0 and H hold.**
- **On the exposed 6 x 30**, the best k = 12 code has d = 24 exactly, so nothing of this form
  beats the published [[360,12,24]] there.
- **[[310,10,22]] (score 15.61)** is confirmed by a second method: DistQLDPC's MaxSAT engine.
- **Stage 4d** (`examples/qec-census-4d`, registered 2026-11-03, running) reruns the 53 classes
  that stage 4 left at its limit, all k = 4 at n = 396, with a 14-day limit.
  - The 17 recorded so far all have d = 30.
  - So the best k = 4 code on those tori is [[396,4,30]]. Its d/√n = 1.508 is the census's
    highest.

**Census stage 3a: every weight-6 code on the stage-1 tori** ([code-census.md](code-census.md#stage-3a-every-weight-6-code-examplesqec-census-3), exploratory, run 2026-10-24).
- **Scope.** All 36,496 classes, on 116 tori with n <= 200, have exact distances, in 1.3 hours
  on 4 cores.
- **Method.** A common-zero rule for k > 0 rules out 93% of the 306 million raw codes without a
  rank computation. Distances come from the packing search.
- **Checks.** The census matches Lin and Pryadko's catalog at 43 of 44 comparable (n, k) pairs
  and is never higher.
- **Results.**
  - It beats the trinomial form at 18 (n, k) pairs. The gross code still has the best k d^2 / n.
  - Seven leaderboard codes with 100 < n <= 200, listed there with upper bounds only, have the
    same d here exactly, and no code in this family does better on the tori covered.
  - The leaderboard's codes that do better at n = 144 and 168 are non-abelian.
- **Next.** Done: stage 3b/3c, above.

**The open distances of two larger published codes** ([code-distances.md](code-distances.md#the-open-distances-examplesqec-open-distance), registered, run 2026-10-23).
- **[[360,12]]: d = 24 exactly.** Bravyi et al. give only d <= 24.
  - A random-information-set window found a checked weight-24 logical.
  - The split exhaustive search proved nothing is lighter, in 1.9 hours on 4 cores.
  - The value was already established (Crocker, 13 Oct 2026; DistQLDPC), so this is an
    independent recomputation.
- **[[756,16]]: 30 <= d <= 34.**
  - The window found a checked weight-34 logical, matching the published bound.
  - A Fable consultation ($1.12, every claim checked by machine) showed that the code has no
    symmetry beyond its translations. It also proposed a packing cut for the search, which a
    second registered study tested on fresh codes and known distances.
  - With the cut, the search proved d >= 30 in 7 hours on 4 cores. That matches the public lower
    bound (DistQLDPC, 22 Oct 2026, one implementation) without going beyond it. Ours is a second
    implementation of the same kind of search, not a different method
    ([code-distances.md](code-distances.md#what-the-literature-shows-checked-2026-10-24-after-both-studies)).
  - The run stopped during a pass that could not change the result. Its rules give "hold" on
    every part, but the ledger has no verdict entry (disclosed in STOPPED.md).

**Rule 4850 at m = 37: explained** ([the deep dive's report](../examples/rule-4850/deep/REPORT.md)).
- **The seventh pilot** explained four of the five unexplained ninth-power rules at 37 (`Ninth37.lean`).
- **A multi-agent deep dive then explained 4850 itself, with a proof.**
  - The hexagon identity: (x + 1/x + y + 1/y) · 4850 = Hex(x,y) + Hex(y,x), with Hex = {±(4,0), ±(2,±5)}.
  - An order-3 symmetry that exists only at 37, since 5² + 3·2² = 37.
  - The closed form λ · t_α t_β = W⁴, with W a Kloosterman-type sum over μ6.
  - A norm formula in Gauss periods. At 37 it puts every eigenvalue's norm to F64 in F8*, and that
    is exactly the ninth-power condition.
- **Checking.** Three independent checkers each found that the proof stands with repairs, and the
  orchestrator rechecked the final chain (`tests/test_rule4850_proof.py`).
- **The relatives.** All six are accounted for by exact identities: 482758, 8438150 and 43250486
  are 4850 times ninth-power units, 10491524 is its 45° rotation, and the two radius-6 rules the
  seventh pilot missed, 20982139 and 178279803, are Frobenius conjugates of that rotation, times a
  ninth-power unit off the axes.
- **The hexagon family.** It is classified at 37: p a non-residue gives ninth powers, p a residue
  gives cubes. A held-out registered test (`examples/hexagon-family`) confirmed it: 35 of 35
  tested predictions are correct, at 37, 13 and eight other sizes; the six largest sizes were
  not tested.
- **Still open:**
  - the repaired proof as one document, and in Lean;
  - why 37's coset data are (4, 3, 5);
  - the classes mod 27;
  - non-confinement elsewhere, which is computed, not derived.

1. **The chance model.** Two pilots have shown the census's chance model undercounts. At m = 25
   it treats characters of order 25 and 5 as independent where an identity ties them (pilot 5);
   at m = 37 it treats every class as a cube one time in three, where the axis and diagonal classes
   are cubes 93.5% of the time because they inherit rule 90's confinement (pilot 6). With
   per-class rates, the seven of pilot 6's targets it did not explain are what chance expects
   (5.7). A corrected model should be registered and tested on a fresh family before anything is
   called chance again. Still open with it: the family at m = 29 (13 unexplained against 7.85 with
   per-class rates) and at 25 (nine, and the three atlas rules). **Two corrections from the
   consultation benchmark** (consultations.md, section 3), both checked by machine: rule 4850, one
   of pilot 6's seven, has every nonzero eigenvalue a *ninth* power at 37 (now explained, above);
   and 17056 is 1112 under the exponent map (a, b) -> (a + b, a - b), so pilot 6's sixteen were
   fifteen independent cases.
2. **Round 4.** Compute the split step exactly (the m = 115 entry), and add the twisted-power,
   half-Frobenius, cube-certificate, unit-times-power, exact-exponent and hidden-symmetry steps to
   `atlas3.predict`. That needs a faster test than Kronecker recombination for "f has a factor g
   with g(x^d, y^d) also a factor". Register it on new rules, with `eigen.py` as the checker.
   Judge sizes below about 30 by the predicted chance of a coincidence, not by exactness.
3. **Proofs.** `proofs/` (Lean 4, mathlib v4.35.0; [proofs.md](proofs.md)) now formalises:
   - the 18 identities behind the mechanisms, generated from the atlas code;
   - the order lemma, and the cube and twisted-power mechanisms at the eigenvalue level;
   - **the bridge** (`Bridge.lean`): on an odd torus, the period is the lcm of the orders of the
     nonzero eigenvalues;
   - **the bound**: on an odd torus the period divides 2^ord(m) - 1, or 2^sord(m) - 1 for a
     symmetric rule, so it is odd;
   - **the group ring** (`GroupRing.lean`): every rule acts on every torus through F2[Z^2], so
     every identity is a rule identity at every size;
   - **the even-size reduction** (`Tori.lean`): the period's odd part is the odd quotient's
     period and its 2-part is bounded. On the square, P(2^v m) = 2^a P(m) with a <= v, and
     P(2m) = 2 P(m) gives P(2^v m) = 2^v P(m). The same holds on the atlas's own triangular torus
     (Z/n x Z/(n/2)) and hexagonal torus (Z/2n x Z/(n/2)), which the tests check against the
     engine;
   - **round 2's mechanisms at every size n**: P(N4+K8+C4) = P(N4) / gcd(P(N4), 3), the same for
     A4+K8+C4+self and N4+self, and P(C4+self, n) = P(N4+self, n / gcd(n, 3));
   - **triangle rules on every triangular torus**: E and VO+T13 have period exactly 2 P(s). The
     general 2 x 2 case (E+VO+VS) has P / gcd(P, 2) = P(s);
   - **round 3's twisted power on the atlas's own torus**: if 3 = +-2^k mod m, then at n = 2^v m
     the odd part of VO+T13's period is P / gcd(P, 1 + 2^k), where P is the odd part of E's.
     Among round 3's tested sizes, this lowers the period exactly at its seven VO+T13 failures;
   - **the XOR law's 2-part** (`TwoPart.lean`): P(2^v m) = 2^v P(m) for B1357/S1357 and N4, for
     every odd m > 1. A Jordan block of rule 90 along y forces even periods at 2m. So the XOR law
     at every size is exactly the law at its odd parts;
   - **the hexagon law's 2-part** (`HexTwoPart.lean`, by the LLM pilot's agent): H1 has period
     exactly 2^(v+1) P(m) on the atlas's hexagonal torus of side 2^v m, for odd m >= 5, through a
     Jordan block on Z/2m x Z/m;
   - **the triangle laws' 2-part** (`TriTwoPart.lean`, by the second pilot's agent): both
     triangle parity rules have period exactly 2^(v+1) P(m) on the atlas's triangular torus, for
     odd m >= 3. So each triangle law holds at n = 2^v m exactly when P(m) = 2^sord(m) - 1, the
     open odd-part statement;
   - **VO + T13's law** (`VOT13Law.lean`, found from data and proved by the third pilot's agent):
     period 2^(v+1) P(m) for m >= 3, and 2^(v-1) at n = 2^v, on the atlas's triangular torus at
     every even n >= 4. The m = 1 case uses finite checks by kernel `decide` on two small tori;
   - **the cubes at m = 37** (`Cubes37.lean`, found and proved by the fourth pilot's agent): the
     six rules each have period dividing 87381 on the 37 x 37 torus, through the half-Frobenius
     identities, and rule 90's period there divides 87381 by an explicit cube root
     (`period_r90_dvd`). Its build takes about 13 minutes, most of it the triangle identity;
   - **the cubes at m = 25** (`Cubes25.lean`, found and proved by the fifth pilot's agent): five of
     the seventeen rules at 25 have period dividing 341 on the 25 x 25 torus, two through cube
     certificates (f (t(x) t(y))^3 is invariant under the dilation by 7 = 2^5) and three as
     twisted pairs C(x, y) C(x^3, y^3), with 3 = 2^7 mod 25;
   - **unit times cube** (`UnitCubes.lean`, found and proved by the sixth pilot's agent): nine
     square-family rules f = U g^3, with U a product of rule-90 or Psi_3 factors, have period
     dividing 87381 at m = 37, and the three with U = (a + 1)(b + 1) also divide (2^30 - 1)/3 at
     61, where 3 = 2^6;
   - **ninth powers at m = 37** (`Ninth37.lean`, found by the seventh pilot's agent and proved in
     its second round): four radius-5 rules, line units times the fourth pilot's half-Frobenius
     cores W and V, have period dividing 29127 = (2^18 - 1)/9 at 37, so every nonzero eigenvalue
     is a ninth power. The units' exact exponents give the third factor of 3.

   They rest on Lean's standard axioms only; `proofs/Axioms.lean` prints the axioms of every main
   theorem. Next:
   - rule 4850 at 37, which the deep dive proved but nobody has formalised; its report (section
     7.3) sets out a route, `Rule4850.lean`;
   - one-dimensional tori, for the comparison with rule 90 in the hexagon theorem (R(m));
   - then, as research:
   - the rule-150 analogues of Vadali and Turner's theorem and of the hexagon theorem: square
     D4+A4+self has period P150(n), and hexagon H2+H3+self has 2 P150(n). Both are confirmed but
     unproved.
   - Why a non-confined rule reaches the full bound. At present it is a heuristic: generic
     elements generate.
4. **The LLM-central loop** ([llm-pilot.md](llm-pilot.md), `examples/llm-pilot*`). Seven pilots
   have worked: fresh agents proved the hexagon and triangle laws' 2-parts from a card, found
   VO + T13's law from data and proved it, in the fourth answered the open m = 37 question and
   proved the answer, in the fifth explained and proved 5 of the 17 cube confinements at
   m = 25, in the sixth 12 of the 19 at m = 37 and 61 (unit times cube, `UnitCubes.lean`), and
   in the seventh, the first on Claude Fable, 4 of the 5 ninth-power rules at 37, its Lean
   fixed in a second round over the API (`Ninth37.lean`). Each was judged by Lean and, for the
   mechanism, by its claims at held-out sizes (none false in any of the last four).
   The sixth's registered census found its nine rules at exactly the three new sizes it
   predicted, and nothing else unexplained. The last six ran in their own cloud sessions, whose
   containers cloned only an orphan sandbox branch, and their transcripts were audited. Next:
   - the corrected chance model (item 1), and the rest at 25 and 29;
   - a law that is not one division away in the data, such as a rule round 3 left unexplained.

   **Parked: people in the proposer's seat.** Mathematicians could take the agent's role on the
   same cards, judged by the same checks: open problem cards, submissions as pull requests with
   the public half of the judge in CI, the held-out half run privately, held-out grids published
   as SHA-256 commitments before a card opens. Undecided: where contributors work (a new public
   repository, pull requests to this one, or invited collaborators) and whether they may use AI
   tools. lattice-lab now has a licence (Apache-2.0 for code, CC BY 4.0 for the rest); Kepler and
   LatticeLife do not yet.

   The pilots' twelve branches (`pilot-sandbox-*`, `pilot-*-submission`) were deleted from
   GitHub on 2026-11-03, before the repository went public. Each pilot's `branches.bundle` holds
   everything that was on them; pilot 7's also holds its second round's branch,
   `pilot-37c-round-2`. Now that lattice-lab is public, a pilot's held-out half waits in a private
   repository until its submission is frozen
   ([llm-pilot.md](llm-pilot.md#held-out-halves-now-that-lattice-lab-is-public)).
5. **A specialist's view.**
   - The literature search was brief, and specialists in linear cellular automata may know parts
     of this.
   - Kepler's and LatticeLife's READMEs point to the website, polylabs-research.net, and not into
     lattice-lab, because it was private when they were written. They can link into it now.
6. **Remaining machine checks.** The square and triangle odd parts beyond 999, and the ten odd
   parts below 999 whose check is incomplete.
7. **Settling time.** `identify` cannot yet name the Gumbel class at the current error bars;
   more soups would decide it.
8. **Kepler's vocabulary.**
   - It ranks the shorter rule-90 law first even when the data cannot separate the two;
     registering tied rivals is what saves the tests.
   - A "halve when even" feature would give the A4-type rules a law.

## Practical notes

- **Two-hour limit.** A cloud session's background commands stop after two hours. Long registered
  runs survive this through `study.py resume`, which records a `run_resumed` entry. Sort tasks
  slowest first so the cheap ones finish fast at the end.
- **Cost.** An exact check of a triangle rule at n = 280 takes about 30 seconds by matrix powers;
  `eigen.py` does the same odd part in well under a second.
- **A pilot on Fable costs real money.** Pilot 7's cloud session cost $51.33 at list price for
  two hours, $8.02 of it re-caching a 640K-token context after a 10-minute wait. Its second
  round over the API (`round2.py`, narrow tools, a $30 cap) cost $4.47
  (`examples/llm-pilot-37c/log.md`).
- **The stop hook** asks for a commit whenever files are uncommitted. During a long run that
  means committing snapshots of `records.jsonl`, which is harmless: `verify` checks records by
  offset and hash.
- **Seen pairs.** Any test pair computed before registration, even while timing, must be excluded
  and declared in the registration. Rounds 2 and 3 both did this.
- **Module names.** The example directories put each other on `sys.path` (round 3 imports round
  2's and round 1's modules), so names must not clash. That is why round 3's analysis is
  `failures.py`, not `analyse.py`.
- **Lean.** `proofs/check.sh` builds and prints the axioms. In this cloud environment the Lean
  release host and mathlib's cache are blocked, so the toolchain comes from the GitHub release zip
  (`elan toolchain link v4.35.0-local`, then `ELAN_TOOLCHAIN=v4.35.0-local`), and mathlib builds
  from source in about 50 minutes; see [proofs.md](proofs.md#building-it-here). A new session
  starts without `proofs/.lake`, so it pays that again.
- **uv** prints a warning about `UV_NATIVE_TLS` on every call; it is harmless.
- **Code distances.** `uv sync --group qec` installs SCIP (pyscipopt). The search
  (`examples/qec-distance/search.c`) needs a C compiler as `cc`. Every checked witness is an
  upper bound. Run the program only with `distance.SCIP_FIX` (its default): SCIP 10.0's own
  defaults return wrong optima on these programs, about 0.3% of runs on small high-k codes
  (code-distances.md). Where it matters, run both instruments and require their intervals to
  meet.
- **Consultations: read `served_by`.** Fable's cyber classifier declines GF(2) arithmetic as a
  false positive (6 of 12 benchmark calls, 5 of 6 on pilot 4's question), and the server-side
  fallback answers with Claude Opus 4.8. The record says so; any comparison of models must
  check it first.
- **Consultations.** `lattice-lab consult` needs `uv sync --group consult`, the variables
  `CONSULT_ANTHROPIC_API_KEY`, `CONSULT_OPENAI_API_KEY` and `CONSULT_OPENAI_MODEL`, and network
  access to `api.openai.com`, which this cloud environment's policy denied on 2026-10-20
  ([consultations.md](consultations.md#running-a-consultation)).
