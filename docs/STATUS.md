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
| [lattice-lab](https://github.com/PolyLabs-research/lattice-lab) | the questions, registered studies, ledgers, write-ups, Lean proofs, the website (this repository) | private | 214 |
| [kepler](https://github.com/PolyLabs-research/kepler) | fitting, ranking and predicting laws; exact integer laws; known constants | public | 308 |
| [gameoflife_advanced](https://github.com/PolyLabs-research/gameoflife_advanced) (LatticeLife) | the cellular automata, experiments and observables | public | 1043 |

- **The website.** [polylabs-research.net](https://polylabs-research.net) is built from `site/`
  in lattice-lab; [site/README.md](../site/README.md) says how to rebuild and deploy it. While
  lattice-lab is private, the site must not link into it on GitHub.
- **Pins.** lattice-lab pins LatticeLife `256450b` and Kepler `0af9b28` (`pyproject.toml`,
  `uv.lock`). Both are current for code: every later commit on those repositories' working
  branches changes only the README.
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
and every record follows the run's start.

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
- **Next.** Register stage 2 on the held-out tori from the report's candidate predictions, and
  record the exposure it lists.

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
   repository, opening this one, or invited collaborators), whether they may use AI tools, and a
   licence; none of the repositories has one yet.

   Each pilot leaves two branches (`pilot-sandbox-*`, `pilot-*-submission`) that this session's
   git proxy would not delete; each pilot's `branches.bundle` holds everything on them, so they
   can be deleted on GitHub. Pilot 7's are in `examples/llm-pilot-37c/branches.bundle` too, with
   its second round's branch, `pilot-37c-round-2`.
5. **A specialist's view.**
   - The literature search was brief, and specialists in linear cellular automata may know parts
     of this.
   - lattice-lab is private, so Kepler's and LatticeLife's public READMEs point to the website,
     polylabs-research.net, and not into it.
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
