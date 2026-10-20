# Problem card: ninth powers at m = 37

This card is the whole brief for the pilot's proposer. It states an open question, the data, and
the tools. **Nobody knows the answer**, including whoever wrote this card. A precise negative
result is also useful.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source (half an
hour to an hour). Lean is optional in this pilot; Python is ready within a minute.

## The setting

**Square rules.** A rule is a Laurent polynomial f(x, y) over GF(2), the set of translations it
reads. The rules here are symmetric: unions of D4 orbits O(a, b) = {(±a, ±b), (±b, ±a)}. The
**square family of radius r** is every nonempty union of the orbits with 0 ≤ b ≤ a ≤ r, numbered
by bit masks in the order (0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), ... (`tools/family.py`
has radius 4, 32,767 rules; `tools/census37.py` takes any radius). Radius 4's numbering is the
start of radius 5's. `data/rules.json` also lists the 1,274 shell rules of the atlas (square,
triangular and hexagonal), for the soundness checks.

**Periods and eigenvalues.** On the torus (Z/m)², m odd, a rule f acts diagonally in the
characters: its eigenvalues are f(ζ^j, ζ^k), for ζ a primitive m-th root of unity in F(2^d),
d = ord_m(2). The **odd part** of the rule's period is the lcm of the multiplicative orders of its
nonzero eigenvalues (the Lean library proves this: `period_eq_eigenLcm` in `Bridge.lean`).
Symmetric rules have their eigenvalues in F(2^s), s = sord(m), the least j with 2^j ≡ ±1 (mod m),
and the odd part divides the **full bound** 2^s − 1.

**Coordinates.** With a = x + 1/x and b = y + 1/y, every symmetric rule is a symmetric polynomial
F(a, b): O(i, j) = D_i(a) D_j(b) + D_j(a) D_i(b), O(i, i) = D_i(a) D_i(b), O(i, 0) = D_i(a) + D_i(b),
O(0, 0) = 1, with D_n(a) = x^n + x^-n (D_1 = a, D_2 = a², D_3 = a³ + a, D_4 = a⁴, D_5 = a⁵ + a³ + a).
At a character, a and b take rule 90's values t_j = ζ^j + ζ^-j and t_k.

## What is known

**Mechanisms that confine eigenvalues to a proper subgroup**, each proved:

1. **splitting**: f is a product of one-dimensional rules along lattice directions. Rule 90,
   t(x) = x + 1/x, and rule 150, 1 + t(x), are the basic ones.
2. **powers**: f = g^k, so its eigenvalues are k-th powers.
3. **dilations**: f = h(x^p, y^p) with p dividing m.
4. **twisted powers**: f = g(x, y) g(x^d, y^d) with d ≡ ±2^k (mod m), so its eigenvalues are
   λ^(1+2^k).
5. **half-Frobenius confinement** (the fourth pilot, `data/pilot4.md`, `tools/halffrob.py`): if
   n ≡ 2^g (mod m) and B is invariant under (x, y) ↦ (x^n, y^n) on the m-torus, B's eigenvalues
   lie in F(2^g). At 37, 2^9 ≡ −6 and 6² ≡ −1.
6. **cube certificates and twisted pairs** (the fifth pilot, `data/pilot5.md`,
   `tools/certificate.py`): f · M^E ≡ B with B invariant under ×2^g and q dividing E; and
   f = C(x^a, y^a) · C(x^b, y^b) with b ≡ ±2^k a.
7. **a unit times a power** (the sixth pilot, `data/pilot6.md`, `tools/unitpower.py`):
   f = U · g^q exactly, with every nonzero eigenvalue of the unit U a q-th power at m. At 37,
   nine family rules are U · g³ with U one of a + b, ab, (a + 1)(b + 1).

All three conditions are proved; their proposals give the proofs. The Lean library has proofs for
particular rules: `Cubes37.lean`, `Cubes25.lean`, `UnitCubes.lean`.

**Facts at 37 that bear on the question** (all checked by machine):

- Rule 90's values t_j are cubes at 37 and not ninth powers. Its ninth-power class is the
  Legendre symbol: t(x)^29127 ≡ Σ x^u over the quadratic non-residues u mod 37, in
  F2[x]/(x^37 − 1). (Rule 90 is confined to the cubes at 37 because the fundamental unit of
  Q(√37), 6 + √37, lies in Z[√37].)
- Rule 150's values 1 + t_j are ninth powers at 37 (3 ≡ 4^13 mod 37, and 1 + ζ is a cube).
- A symmetric rule's characters at 37 fall into 11 classes, each a single Frobenius orbit: the
  axes, and the lines (1, k) up to k ↦ −k, 1/k. The class of k = ±6 is forced into F(2^9), whose
  elements are all 27th powers; the other ten are free.

## The question

**At m = 37**, d = 36 and s = 18. The full bound is 2^18 − 1 = 262,143 = 3³ · 7 · 19 · 73. The
cubes are its subgroup of order 87,381, the ninth powers of order 29,127, the 27th powers of order
9,709.

`data/ninth37.json` is the ninth-power census at 37 of the radius-4 family (all 32,767 rules) and
of the radius-5 family's new rules (the 2,064,384 that use an orbit of radius 5):

| | rules | cubes | ninth powers | 27th powers |
| --- | --- | --- | --- | --- |
| radius 4 | 32,767 | 110 | 21 | 4 |
| radius 5, new | 2,064,384 | 415 | 21 | 3 |

Of the 42 ninth-power rules, mechanisms 1 to 4 (the atlas procedure: splitting, powers,
dilations) explain all but six, which no known mechanism explains:

| rule | radius | orbits |
| --- | --- | --- |
| 4850 | 4 | (1,0) (2,1) (2,2) (3,0) (3,1) (3,3) (4,2) |
| 699738 | 5 | (1,0) (2,0) (2,1) (3,0) (3,2) (4,0) (4,1) (4,3) (5,0) (5,2) (5,4) |
| 985232 | 5 | (2,1) (3,1) (4,1) (5,1) (5,2) (5,3) (5,4) |
| 1431278 | 5 | (1,0) (1,1) (2,0) (2,2) (3,0) (3,1) (3,3) (4,0) (4,2) (4,4) (5,0) (5,1) (5,3) (5,5) |
| 1968276 | 5 | (1,1) (2,1) (3,1) (4,1) (5,2) (5,3) (5,4) (5,5) |
| 482758 | 5 | 4850 × rule 7, and rule 7 = (1 + a)(1 + b) has ninth-power values: not a target |

**The five targets** are 4850, 699738, 985232, 1431278 and 1968276 (`data/targets.json`, with their
exponents and class logs).

- Each is confined at 37 and at no other odd m from 11 to 101 (its odd part is the full bound).
- They are not multiples of one another, and no map in GL2(Z/37) sends one's support onto
  another's. 4850 is irreducible over GF(2), in a, b and as a Laurent polynomial in x, y.
- **What the known conditions do say.** For the four radius-5 targets, mechanism 5
  (`tools/halffrob.py`) proves the cubes: it returns q = 3(2^18 + 1), every eigenvalue a cube in
  F(2^36)*, but not the ninth powers. For 4850 none of the three conditions makes any claim.
- **Not chance.** Each free class is a ninth power about one time in nine, independently (rates
  in `data/ninth37.json`; the axis and diagonal classes more often), so chance expected 3 × 10⁻⁴
  such rules at radius 4 and 0.0066 among the new radius-5 rules. The radius-5 count was a
  registered test, and it refuted chance.
- **Two consultations** of a model (`data/consultation-1.md`, `data/consultation-2.md`, verbatim;
  every identity they list holds) found no mechanism. The first gives a certificate for 4850:
  on each line of characters, the restriction f(x, x^k), alone or times a twisted "hub" line, is a
  monomial times whole cyclotomic polynomials mod x^37 − 1, so every eigenvalue is a root of unity
  times a power of 1 + ζ; three of these identities are exact at every m, and it could not derive
  the rest. The second calibrated the chance model above and proposed the radius-5 test.
- The ninth-power condition is equivalent to f^29127 being idempotent in the group ring, or to
  the norm of each eigenvalue from F(2^18) to F(2^6) lying in F(2^3): restatements, not reasons.

**Find the mechanism**: a condition on a rule f and an odd m that forces every nonzero
eigenvalue of f at m to be a ninth power (or, more generally, a q-th power), that holds for the
targets, and that you can prove. Say which of the five it explains, which other confinements in
the data, and where else it predicts confinement, including families and sizes the data does not
cover. If you conclude there is no single mechanism, say precisely what you excluded.

## The data (`data/`)

- `ninth37.json`: the census above, with every ninth-power rule's orbits, its 11 class logs mod 27
  (the class characters are listed; `null` for a zero eigenvalue), what the atlas procedure says,
  whether it is explained, and its role (target, derived, explained).
- `targets.json`: the five targets and 482758, with exponents and class logs.
- `family.json`, `family_77_125.json`: the square family's **cube** census at every odd m
  computed so far (21, 25, 29 to 75, and 77 to 125), with every confined rule the earlier
  mechanisms do not account for, from the fifth and sixth pilots.
- `pilot4.md`, `pilot5.md`, `pilot6.md`: the three previous proposals.
- `consultation-1.md`, `consultation-2.md`: the two consultations on 4850.
- `rules.json`, `shells.json`: the atlas.

## Deliverables

1. **`mechanism.py`**, defining

   ```python
   def condition(f: frozenset[tuple[int, int]], m: int) -> int
   ```

   for f a rule's polynomial (a frozenset of exponent pairs) and m odd. Return q > 1 if your
   mechanism proves that every nonzero eigenvalue of f at m is a q-th power in F(2^d)*,
   d = ord_m(2), with q dividing 2^d − 1; return 1 when it makes no claim. It must decide from the
   structure your mechanism names, not by computing the eigenvalues and testing them; the judge
   reads it. It may use the known mechanisms (`tools/halffrob.py`, `tools/certificate.py`,
   `tools/unitpower.py`). It must take at most about a minute for all 1,274 atlas rules at one
   m ≤ 300, and about two minutes for 2,000 square rules of radius up to 6 at one m ≤ 161.
2. **`proposal.md`**: the mechanism, the proof that your condition implies the claim, how you
   found it, which of the targets and which other confinements it explains and which not, and
   where else it predicts confinement.
3. **`proposal.py`**: numerical checks of the mechanism with the tools. It prints what it checked
   and whether each check held.
4. **Optional, Lean**: any formal results in `proofs/LatticeProofs/Pilot.lean` (or files under
   `proofs/LatticeProofs/Pilot/`). The judge builds them and lists each theorem's axioms.
5. **`report.md`**: what you found, what you tried, what failed, and what you are unsure of.
   Write it last: the judge starts when it appears on your branch.

Scratch files go under `scratch/`. Commit and push your work to your branch as you go.

## How it is judged

- **Explains**: `condition` on the five targets at 37 (a claim with q divisible by 9).
- **Sound**: the judge runs `condition` on all 1,274 atlas rules at every odd m in a grid that
  goes beyond the census, on square-family rules at the sizes in the data, and on square rules of
  radius 6 at 37, which you have not been given: a fixed sample, and every ninth-power rule of a
  registered census of that family. It checks each claim with its own eigenvalue computation. One
  false claim refutes the mechanism as stated. You are not told the grid's results.
- **Reach**: how many confinements the condition accounts for, at 37 and elsewhere, and how many
  the known mechanisms do not; in particular, how many of the radius-6 ninth-power rules that no
  known mechanism explains.
- **Proof**: the orchestrator reads the argument in `proposal.md`; Lean results count for more.

## Tools (`tools/`)

- `eigen.py`: `Field(m)`, eigenvalues, Frobenius orbits, orders, `is_power`, `odd_part`,
  `full_bound`.
- `gf2.py`: the finite fields themselves.
- `tori.py`: small tori and exact periods by simulation, for spot checks.
- `family.py`: the square family of radius 4: `ORBITS`, `rule(bits)`, `rules()`, `bits_of(orbits)`.
- `census37.py`: the fast census at 37 for any radius: the 11 class characters, `class_logs`,
  `logs_of(f)`, `confined(logs, q)`. Radius 5 takes under a minute and about 100 MB.
- `chance.py`: forced subfields and the chance model: `symmetries`, `full_symmetries` (all of
  GL2(Z/m), small m), `classes`, `analyse`.
- `halffrob.py`, `certificate.py`, `unitpower.py`: the fourth, fifth and sixth pilots'
  `condition`s (mechanisms 5, 6 and 7), as they submitted them. Each imports the ones before it,
  so put `tools/` on the path.

sympy is available for polynomial algebra over GF(2) (univariate factoring, Gröbner bases,
resultants; not multivariate factoring). Run Python with `./python` (after setup).

## The Lean library (`proofs/LatticeProofs/`), if you want it

Lean 4 with mathlib v4.35.0, namespace `LatticeProofs`. `Bridge.lean` has the square torus,
`period`, characters `chi`, eigenvalues `lam`, `isPeriod_iff`, `period_eq_eigenLcm` and
`exists_primitiveRoot`; `Eigen.lean` has order lemmas in characteristic 2; `Periods.lean` proves
the cube and twisted-power mechanisms for particular rules; `Cubes37.lean`, `Cubes25.lean` and
`UnitCubes.lean` are the fourth, fifth and sixth pilots' proofs for particular rules, worked
examples of this kind of argument (`Cubes37.lean` includes `period_r90_dvd`, rule 90's confinement
at 37). Define what you need in `Pilot.lean`.

## Rules

- **Stay in this checkout.** Work only inside this repository's directory. Do not read, list or
  search anything outside it, except the Lean toolchain under `~/.elan` and
  `~/lean-toolchains`, which setup.sh installs, and the output files of your own background
  commands.
- **This branch only.** Do not fetch, check out, list or read any other branch, tag or commit of
  this repository, or any other repository (no `git fetch`, `git log --all`, `git ls-remote`,
  `add_repo`, `git clone`). Push only to your own branch.
- **No network** beyond what setup.sh does: no web search, no web fetch, no downloads.
- **No other sessions.** Do not list, read or message other Claude sessions, and do not start
  subagents: the pilot audits this session's own transcript, so all the work must be in it.
- Do not change any existing file except `proofs/LatticeProofs/Pilot.lean`. The judge compares
  the others with the base commit and with `manifest.json`.
- In Lean: no `sorry` in what you claim, no new `axiom`, no `native_decide`.
- **Build** (if you use Lean):

      cd proofs
      export PATH=$HOME/.elan/bin:$PATH ELAN_TOOLCHAIN=v4.35.0-local
      lake build LatticeProofs.Pilot
