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
| [lattice-lab](https://github.com/PolyLabs-research/lattice-lab) | the questions, registered studies, ledgers, write-ups, Lean proofs (this repository) | private | 124 |
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
uv sync && uv run pytest              # 124 tests
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
| Square parity rule B1357/S1357: period 2^v(n) (2^sord(m) - 1) | confirmed in advance at every n up to 200; proved for odd parts up to 999 except ten | [xor-periods.md](xor-periods.md), [xor-periods-proof.md](xor-periods-proof.md) |
| Hexagon parity rule B135/S135: period 2 * 2^v(n) R(m) | first law refuted at 3 of 70 sizes; the corrected law was confirmed at 100 and **proved for every even n** | [parity-lattices.md](parity-lattices.md) |
| Triangle parity rules: 2 * 2^v(n) (2^sord(m) - 1) | confirmed at 154 sizes; the 2-part is proved; the odd part is checked by machine to 999 except ten | [parity-lattices.md](parity-lattices.md) |
| Kepler finds the hexagon law itself, given 1D rule periods in its vocabulary | registered replay, 8 of 8 | [parity-lattices.md](parity-lattices.md#kepler-with-a-wider-vocabulary) |
| Atlas, round 1: Kepler's laws for 42 shell-built linear rules (38 unstudied) | blind; all 34 rules with a law kept a registered one at 1,930 new pairs | [linear-atlas.md](linear-atlas.md) |
| Atlas, round 2: the factorisation pattern | the 34 laws held at 624 harder pairs; the pattern was refuted on 116 new rules (7 of 113 failed); the failures showed cubes and dilations | [linear-atlas.md](linear-atlas.md#round-2-the-pattern-registered) |
| Atlas, round 3: the refined statement as a procedure, on 344 new rules | 11,315 of 11,358 held; **refuted** by 43. Every dilation and power held; a third mechanism (twisted power) was found and its expectation matched all 34 sizes; small-field coincidences at m <= 25; one case at 37 open | [linear-atlas.md](linear-atlas.md#round-3-the-refined-statement-registered) |
| Period = lcm of eigenvalue orders (odd tori); round 2's cubes and dilation as period laws | **proved in Lean** for every odd m, standard axioms only; agrees with `eigen.py` at every odd m up to 99 | [proofs.md](proofs.md) |
| B2/S34 settling time on the hexagon grows like log L | found by the loop; replicated to L = 1024; power law rejected | [settling-time.md](settling-time.md) |
| Settling-time fluctuations: one shape and ratio across lattices (Gumbel values) | eight random rules on four lattice types; B2/S34's early miss was a low draw | [settling-time.md](settling-time.md) |
| Cumulative births under B1357/S1357 are always even | found in data, then proved | [capabilities.md](capabilities.md) |

## The atlas, where it stands

A shell rule is linear over GF(2): one Laurent polynomial f on the square or hexagon, and on the
triangle a 2 x 2 matrix with M^2 = s I. At an odd part m, the odd part of its period is the lcm of
the multiplicative orders of its eigenvalues. Those are f evaluated at pairs of m-th roots of
unity, and they lie in F(2^sord(m)), so the period divides the full bound 2^sord(m) - 1. The
current statement is that the period **reaches the full bound unless something confines the
eigenvalues**. Four mechanisms are known, each a theorem once its inputs are known:

1. **one-dimensional splitting:** the eigenvalues are products of a 1D rule's (rounds 1 and 2);
2. **an odd prime power** g^k: the eigenvalues are k-th powers (round 2);
3. **a dilation** h(x^p, y^p) with p dividing m: the rule lives on the m/p torus (round 2);
4. **a twisted power** g(x, y) g(x^d, y^d) where d = +-2^k mod m: the eigenvalues are
   lambda^(1 + 2^k) (round 3, triangle VO+T13). Cubes are the case d = 2.

On top of these come **coincidences in small fields**. At m = 13, 15, 21 and 25, rules with only 3
to 7 distinct eigenvalues sometimes have all of them in a subfield or in the cube subgroup. Above
m = 37, in 6,365 round-3 predictions, the only failures were the twisted power's.

**Tools.**
- `examples/linear-atlas-3/eigen.py` computes the odd part from the eigenvalues in seconds. It
  agreed with all 11,662 exact records of round 3, and it is the checker to use from now on.
- `examples/linear-atlas/factor.py` (`split`) decides whether a polynomial has a 1D factor,
  completely.
- `examples/linear-atlas-3/atlas3.py` (`predict`) is the procedure.
- `examples/linear-atlas-3/failures.py` (`factor2d`) factors in two variables, slowly; it is
  capped.

## Open questions, roughly in order

1. **m = 37.** Two unrelated, irreducible rules have every eigenvalue a cube at m = 37, giving rule
   90's own period, 87381: square A4+K8+B4+self (round 2, 172 distinct eigenvalues) and triangle
   VS+T9+T13+self (round 3, 9). That is far beyond chance, and 37 is the first size where rule 90
   falls short. Searches for a torus-specific factorisation (products of rule-90 values along
   linear forms) found nothing. This is the most promising lead.
2. **Round 4.** Add the twisted-power step to `atlas3.predict`. That needs a faster test than
   Kronecker recombination for "f has a factor g with g(x^d, y^d) also a factor". Register it on
   new rules, with `eigen.py` as the checker. Judge sizes below about 30 by the predicted chance of
   a coincidence, not by exactness.
3. **Proofs.** `proofs/` (Lean 4, mathlib v4.35.0; [proofs.md](proofs.md)) now formalises:
   - the 12 identities behind the mechanisms, generated from the atlas code;
   - the order lemma, and the cube and twisted-power mechanisms at the eigenvalue level;
   - **the bridge** (`Bridge.lean`): on the m x m torus with m odd, p is a period exactly when
     every eigenvalue is 0 or a p-th root of unity. So the period is the lcm of the orders of the
     nonzero eigenvalues;
   - **round 2's mechanisms as theorems about periods** (`Periods.lean`), at every odd m, for the
     atlas's own neighbourhoods (generated into `Rules.lean`):
     - P(N4+K8+C4) = P(N4) / gcd(P(N4), 3);
     - P(A4+K8+C4+self) = P(N4+self) / gcd(P(N4+self), 3);
     - P(C4+self, m) = P(N4+self, m / gcd(m, 3)).

   They rest on Lean's standard axioms only. Next:
   - the triangle torus (two cells per unit cell, a 2 x 2 matrix), so the twisted power becomes a
     theorem about periods too;
   - the reduction from even sizes to odd parts, and the hexagon theorem's 2-part;
   - then, as research:
   - the rule-150 analogues of Vadali and Turner's theorem and of the hexagon theorem: square
     D4+A4+self has period P150(n), and hexagon H2+H3+self has 2 P150(n). Both are confirmed but
     unproved.
   - Why a non-confined rule reaches the full bound. At present it is a heuristic: generic
     elements generate.
4. **A specialist's view.**
   - The literature search was brief, and specialists in linear cellular automata may know parts
     of this.
   - lattice-lab is private, so links to it from Kepler's public README will not open for
     outsiders.
5. **Remaining machine checks.** The square and triangle odd parts beyond 999, and the ten odd
   parts below 999 whose check is incomplete.
6. **Settling time.** `identify` cannot yet name the Gumbel class at the current error bars;
   more soups would decide it.
7. **Kepler's vocabulary.**
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
