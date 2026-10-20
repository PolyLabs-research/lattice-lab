# Where we're up to

Written 2026-10-18, at the end of the session that ran the linear-rule atlas's third round. It is
for whoever picks this up next: what exists, what has been established, what is open, and how to
carry on.

## The three repositories

All three now live under **PolyLabs-research**, moved from `tripptytrip` on 2026-10-18. All work
is on the branch **`ccr-ab9f0bb1-qb20sx`** in each repository. Nothing has been merged into a
default branch and no pull request is open; merging is a decision for you.

| Repository | Role | Visibility | Tests |
| --- | --- | --- | --- |
| [lattice-lab](https://github.com/PolyLabs-research/lattice-lab) | the questions, registered studies, ledgers, write-ups, Lean proofs (this repository) | private | 172 |
| [kepler](https://github.com/PolyLabs-research/kepler) | fitting, ranking and predicting laws; exact integer laws; known constants | public | 308 |
| [gameoflife_advanced](https://github.com/PolyLabs-research/gameoflife_advanced) (LatticeLife) | the cellular automata, experiments and observables | public | 1028 |

- **Pins.** lattice-lab pins LatticeLife `256450b` and Kepler `0af9b28` (`pyproject.toml`,
  `uv.lock`). Both are current for code: every later commit in those repositories changes only
  the README.
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
uv sync && uv run pytest              # 132 tests
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
| Atlas, round 3: the refined statement as a procedure, on 344 new rules | 11,315 of 11,358 held; **refuted** by 43. Every dilation and power held; a third mechanism (twisted power) was found and its expectation matched all 34 sizes; small-field coincidences at m <= 25; one case at 37 open | [linear-atlas.md](linear-atlas.md#round-3-the-refined-statement-registered) |
| Period = lcm of eigenvalue orders (odd tori); even sizes reduce to odd parts; round 2's cubes and dilation at every size; round 3's twisted power on the atlas's own torus | **proved in Lean**, standard axioms only; the torus models agree with the atlas's engines at every size checked | [proofs.md](proofs.md) |
| B2/S34 settling time on the hexagon grows like log L | found by the loop; replicated to L = 1024; power law rejected | [settling-time.md](settling-time.md) |
| Settling-time fluctuations: one shape and ratio across lattices (Gumbel values) | eight random rules on four lattice types; B2/S34's early miss was a low draw | [settling-time.md](settling-time.md) |
| Cumulative births under B1357/S1357 are always even | found in data, then proved | [capabilities.md](capabilities.md) |
| The cubes at m = 37: six rules have every eigenvalue a cube, because a dilation by 6 acts as half a Frobenius and combines with rule 90's own confinement | **answered by an LLM agent** in the fourth pilot, on a question the orchestrator could not answer; **proved in Lean** for all six, unconditionally; its general condition held at 633 claims, 180 at held-out sizes, none false | [llm-pilot.md](llm-pilot.md#pilot-4-the-cubes-at-m--37), [linear-atlas.md](linear-atlas.md#m--37-answered-by-the-fourth-pilot) |
| Rule 90 at primes p = 5 (mod 8) with 2 a primitive root: confined to the cubes exactly when eps^h lies in Z[sqrt p]; then the pyramid rule at p = i^2 + 1 is too | **proposed by Claude Fable in a consultation**, with an argument that is a proof once Dirichlet's class number formula fills its one-line step; registered and confirmed at 405 primes from 302 to 20,000 and 4 pyramid primes, none wrong | [consultations.md](consultations.md) |
| An LLM agent, given a problem card and the Lean library, proves the hexagon and triangle laws' 2-parts, and finds and proves VO + T13's law from data | three pilots, each passed on the first attempt with no feedback; accepted by the judge (Lean, pinned statements, standard axioms); registered tests 15 of 15, 40 of 40 and 20 of 20. In the third the agent's own law held at 20 of 20 sizes it never saw, and its m = 1 case had no prior proof. The last two ran in their own containers, with their whole transcripts audited. The law was easy to read off the data, and the orchestrator knew it beforehand | [llm-pilot.md](llm-pilot.md) |

## The atlas, where it stands

A shell rule is linear over GF(2): one Laurent polynomial f on the square or hexagon, and on the
triangle a 2 x 2 matrix with M^2 = s I. At an odd part m, the odd part of its period is the lcm of
the multiplicative orders of its eigenvalues. Those are f evaluated at pairs of m-th roots of
unity, and they lie in F(2^sord(m)), so the period divides the full bound 2^sord(m) - 1. The
current statement is that the period **reaches the full bound unless something confines the
eigenvalues**. Five mechanisms are known, each a theorem once its inputs are known:

1. **one-dimensional splitting:** the eigenvalues are products of a 1D rule's (rounds 1 and 2);
2. **an odd prime power** g^k: the eigenvalues are k-th powers (round 2);
3. **a dilation** h(x^p, y^p) with p dividing m: the rule lives on the m/p torus (round 2);
4. **a twisted power** g(x, y) g(x^d, y^d) where d = +-2^k mod m: the eigenvalues are
   lambda^(1 + 2^k) (round 3, triangle VO+T13). Cubes are the case d = 2.

5. **a dilation acting as part of a Frobenius** (the fourth pilot, at m = 37): if (x, y) ↦ (x^n,
   y^n) with n = 2^g mod m leaves a polynomial unchanged, its eigenvalues lie in F(2^g). At 37,
   2^9 ≡ −6, and each of six rules becomes such a polynomial after multiplying by rule-90 factors,
   whose eigenvalues are cubes there. So every eigenvalue is a cube. Without the rule-90 factors it
   also explains 18 of the coincidences at m = 13. **The cube-certificate form** (the fifth pilot,
   at m = 25): if f · M^E is such a polynomial and 3 divides E, every eigenvalue of f is a cube
   whether or not M is confined, as long as f is checked on the lines where M vanishes. At 25,
   2^5 ≡ 7 and f · (t(x) t(y))^3 is invariant under ×7 for two square rules.

On top of these come **coincidences in small fields**. At m = 13, 15, 21 and 25, rules with only 3
to 7 distinct eigenvalues sometimes have all of them in a subfield or in the cube subgroup. Above
m = 37, in 6,365 round-3 predictions, the only failures were the twisted power's. A census of all
1,274 shell rules (`examples/llm-pilot-37`) leaves 45 unexplained entries from 9 to 161, mostly at
13, and none at the 29 held-out sizes up to 333; [census-remainder.md](census-remainder.md) sorts
them. Some of what looked like coincidence is not: the fifth pilot's cube certificates explain 16
of those at 13 and 3 at 21, and its twisted pairs (mechanism 4 with d = 3, which the census had not
tried) explain three square rules at 25, 29, 35, 53 and 55.

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
random codes agree and all 12 published k are reproduced. Next: distances, which nothing here
computes yet.

**First in line: rule 4850 at m = 37.** A registered census of the radius-5 family
(consultations.md, section 4) refuted chance for rule 4850: four more ninth-power rules at 37
that no known mechanism explains (699738, 985232, 1431278, 1968276), against 0.0066 expected.
The seventh pilot, on Claude Fable ([llm-pilot.md](llm-pilot.md#pilot-7-the-ninth-powers-at-m--37)),
explained those four: they are line units times pilot 4's half-Frobenius cores, and counting the
units' exponents exactly gives the extra factor of 3. Its condition held at all 1,715 claims and
covers 35 of the 37 unexplained ninth-power rules of radius 6. Its Lean file did not build (it
was stopped for cost before compiling it); a second round over the API ($4.47) fixed it, and the
judge accepts the four `period 37 D ∣ 29127` theorems on the standard axioms. **4850 stays open**, with two radius-6 rules of the same class pattern (20982139,
178279803), and the agent's report lists precisely what it is not (units times an F(2⁹)-valued
rule, g³ times one, a twisted pair, a sparse power, a line-by-line certificate, Gauss sums).

1. **The chance model.** Two pilots have shown the census's chance model undercounts. At m = 25
   it treats characters of order 25 and 5 as independent where an identity ties them (pilot 5);
   at m = 37 it treats every class as a cube one time in three, where the axis and diagonal classes
   are cubes 93.5% of the time because they inherit rule 90's confinement (pilot 6). With
   per-class rates, the seven of pilot 6's targets it did not explain are what chance expects
   (5.7). A corrected model should be registered and tested on a fresh family before anything is
   called chance again. Still open with it: the family at m = 29 (13 unexplained against 7.85 with
   per-class rates) and at 25 (nine, and the three atlas rules). **Two corrections from the
   consultation benchmark** (consultations.md, section 3), both checked by machine: rule 4850, one
   of pilot 6's seven, has every nonzero eigenvalue a *ninth* power at 37; and 17056 is 1112
   under the exponent map (a, b) -> (a + b, a - b), so pilot 6's sixteen were fifteen
   independent cases.
2. **Round 4.** Compute the split step exactly (the m = 115 entry), and add the twisted-power,
   half-Frobenius and hidden-symmetry steps to `atlas3.predict`. That needs a faster test than
   Kronecker recombination for "f has a factor g with g(x^d, y^d) also a factor". Register it on
   new rules, with `eigen.py` as the checker. Judge sizes below about 30 by the predicted chance of
   a coincidence, not by exactness.
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
     61, where 3 = 2^6.

   They rest on Lean's standard axioms only. Next:
   - one-dimensional tori, for the comparison with rule 90 in the hexagon theorem (R(m));
   - then, as research:
   - the rule-150 analogues of Vadali and Turner's theorem and of the hexagon theorem: square
     D4+A4+self has period P150(n), and hexagon H2+H3+self has 2 P150(n). Both are confirmed but
     unproved.
   - Why a non-confined rule reaches the full bound. At present it is a heuristic: generic
     elements generate.
4. **The LLM-central loop** ([llm-pilot.md](llm-pilot.md), `examples/llm-pilot*`). Six pilots
   have worked: fresh agents proved the hexagon and triangle laws' 2-parts from a card, found
   VO + T13's law from data and proved it, in the fourth answered the open m = 37 question and
   proved the answer, in the fifth explained and proved 5 of the 17 cube confinements at
   m = 25, and in the sixth 12 of the 19 at m = 37 and 61 (unit times cube, `UnitCubes.lean`),
   judged by Lean and, for the mechanism, by its claims at held-out sizes (none false in either).
   The sixth's registered census found its nine rules at exactly the three new sizes it
   predicted, and nothing else unexplained. The last five ran in their own cloud sessions, whose containers cloned only an orphan
   sandbox branch, and their transcripts were audited. Next:
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
   can be deleted on GitHub.
5. **A specialist's view.**
   - The literature search was brief, and specialists in linear cellular automata may know parts
     of this.
   - lattice-lab is private, so links to it from Kepler's public README will not open for
     outsiders.
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
- **Consultations: read `served_by`.** Fable's cyber classifier declines GF(2) arithmetic as a
  false positive (6 of 12 benchmark calls, 5 of 6 on pilot 4's question), and the server-side
  fallback answers with Claude Opus 4.8. The record says so; any comparison of models must
  check it first.
- **Consultations.** `lattice-lab consult` needs `uv sync --group consult`, the variables
  `CONSULT_ANTHROPIC_API_KEY`, `CONSULT_OPENAI_API_KEY` and `CONSULT_OPENAI_MODEL`, and network
  access to `api.openai.com`, which this cloud environment's policy denied on 2026-10-20
  ([consultations.md](consultations.md#running-a-consultation)).
