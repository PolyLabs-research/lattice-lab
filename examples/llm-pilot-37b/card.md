# Problem card: sixteen rules with only cube eigenvalues at m = 37

This card is the whole brief for the pilot's proposer. It states an open question, the data, and
the tools. **Nobody knows the answer**, including whoever wrote this card. A precise negative
result is also useful.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source (half an
hour to an hour). Lean is optional in this pilot; Python is ready within a minute.

## The setting

**The square family** (`tools/family.py`) is every symmetric linear cellular automaton over GF(2)
on the square lattice within distance 4: the 32,767 nonempty unions of the D4 orbits of the
translations with coordinates in [−4, 4]. A rule is a Laurent polynomial f(x, y) over GF(2), the
set of translations it reads; its id is its bit mask over the 15 orbits, and the orbit (a, b),
with 0 ≤ b ≤ a ≤ 4, is the D4 orbit of (a, b). `data/rules.json` also lists the 1,274 shell rules
of the atlas (square, triangular and hexagonal), for the soundness checks.

**Periods and eigenvalues.** On the torus (Z/m)², m odd, a rule f acts diagonally in the
characters: its eigenvalues are f(ζ^j, ζ^k), for ζ a primitive m-th root of unity in F(2^d),
d = ord_m(2). The **odd part** of the rule's period is the lcm of the multiplicative orders of its
nonzero eigenvalues (the Lean library proves this: `period_eq_eigenLcm` in `Bridge.lean`). Every
rule here is symmetric, so its eigenvalues lie in F(2^s), s = sord(m), the least j with
2^j ≡ ±1 (mod m), and the odd part divides the **full bound** 2^s − 1.

## What is known

**Mechanisms that confine eigenvalues to a proper subgroup**, each proved:

1. **splitting**: f is a product of one-dimensional rules along lattice directions, so its
   eigenvalues are products of theirs. Rule 90 (t = x + 1/x) is the basic one, with eigenvalues
   t_j = ζ^j + ζ^−j.
2. **powers**: f = g^k, so its eigenvalues are k-th powers.
3. **dilations**: f = h(x^p, y^p) with p dividing m, so f lives on the m/p torus.
4. **twisted powers**: f = g(x, y) g(x^d, y^d) with d ≡ ±2^k (mod m), so its eigenvalues are
   λ^(1+2^k).
5. **half-Frobenius confinement**, found by the fourth pilot's agent at m = 37
   (`data/pilot4.md`, implemented as `condition` in `tools/halffrob.py`). If n ≡ 2^g (mod m) and
   a polynomial B is invariant under the dilation (x, y) ↦ (x^n, y^n) on the m-torus, B's
   eigenvalues lie in F(2^g). At 37, 2^9 ≡ −6 and 6² ≡ −1. Six atlas rules become such a B after
   multiplying by rule-90 factors, whose eigenvalues are cubes at 37 because rule 90 itself is
   confined there; the pure case, B = f, puts every eigenvalue in a subfield.
6. **cube certificates and twisted pairs**, found by the fifth pilot's agent at m = 25
   (`data/pilot5.md`, implemented as `condition` in `tools/certificate.py`, which also calls
   `halffrob.condition`). A certificate is f · M^E ≡ B with B invariant under ×2^g and q dividing
   E: the multiplier M enters as a q-th power and need not be confined itself, with a separate
   check on the lines where M vanishes. A twisted pair is f = C(x^a, y^a) · C(x^b, y^b) with
   b ≡ ±2^k a; at 25 it explains rules with 3 ≡ 2^7 (mod 25).

Both conditions are proved; the two previous agents' proposals give the proofs. Their Lean
proofs for particular rules are in the library, `Cubes37.lean` and `Cubes25.lean`.

**Forced subfields and chance** (`tools/chance.py`). Frobenius gives λ(2c) = λ(c)², and a matrix M
that maps a rule's translations onto themselves mod m gives λ(Mᵀc) = λ(c). So if 2^i c = Mᵀc for
such an M, λ(c) lies in F(2^i) whatever the rule. Classes of characters forced into a field whose
elements are all cubes are cubes by structure; the rest are free. The chance model takes each free
class uniform over its forced field and independent, so a rule with k free classes is confined to
the cubes by chance about one time in 3^k. The fifth pilot's agent showed that at m = 25 this
undercounts, because characters of order 25 and 5 are tied by an exact identity; at a prime m
there is no such tie.

## The data

- `data/family.json`: the square family's census at every size computed so far: m = 21, 25,
  and every odd m from 29 to 75 where the cubes are a proper subgroup (the fifth pilot's
  registered census). Per size, the chance model's expected count and standard deviation, and
  every confined rule that the atlas procedure (mechanisms 1 to 4) and forced subfields do not
  account for, each with its polynomial, its free classes, its chance, what
  `halffrob.condition` (`pilot4_q`) and `certificate.condition` (`pilot5_q`) prove for it (q
  divisible by 3 means confined to the cubes), and whether it is one of the targets.
- `data/targets.json`: the 19 targets below, with their symmetries mod m, free classes, distinct
  free values and chance.
- `data/pilot4.md`, `data/pilot5.md`: the two previous proposals.

## The question

**At m = 37**, d = ord_37(2) = 36 and s = sord(37) = 18 (2^18 ≡ −1). The full bound is
2^18 − 1 = 262,143 = 3³ · 7 · 19 · 73, and the cubes are its subgroup of order 87,381. Every
proper subfield of F(2^18) lies inside the cubes, and so do rule 90's eigenvalues (its odd part at
37 is 87,381).

- In the square family, **34 rules are confined to the cubes at 37** beyond mechanisms 1 to 4
  and forced subfields. The half-Frobenius condition explains 18 of them; the certificate
  condition adds none. **The other 16 are unexplained**, against **0.62 ± 0.79** expected by
  chance. Each has 9 or 10 free classes, and 9 or 10 distinct values among them: chance confines
  each about once in 20,000 to 60,000.
- **Three of the 16 (rules 3461, 18246 and 26883) are also confined to the cubes at m = 61**,
  where nothing else in the family is, against 0.0009 expected, each with 16 free classes. At 61,
  d = 60, s = 30, and the full bound is 2^30 − 1 = 3² · 7 · 11 · 31 · 151 · 331. Rule 90 is
  **not** confined at 61 (its odd part is the full bound), and F(2^6) is not inside the cubes
  there, though F(2^2), F(2^3), F(2^5), F(2^10) and F(2^15) are.

The targets (orbits as (a, b) pairs; all in `data/targets.json`):

| rule | orbits | m |
| --- | --- | --- |
| 1112 | (2,0) (2,1) (3,0) (4,0) | 37 |
| 2436 | (1,1) (3,1) (3,2) (4,1) | 37 |
| 3461 | (0,0) (1,1) (3,1) (3,2) (4,0) (4,1) | 37, 61 |
| 4850 | (1,0) (2,1) (2,2) (3,0) (3,1) (3,3) (4,2) | 37 |
| 5972 | (1,1) (2,1) (3,0) (3,2) (3,3) (4,0) (4,2) | 37 |
| 10498 | (1,0) (3,2) (4,1) (4,3) | 37 |
| 13584 | (2,1) (3,2) (4,0) (4,2) (4,3) | 37 |
| 13822 | (1,0) (1,1) (2,0) (2,1) (2,2) (3,0) (3,1) (3,2) (4,0) (4,2) (4,3) | 37 |
| 17056 | (2,2) (3,1) (3,3) (4,4) | 37 |
| 18246 | (1,0) (1,1) (3,0) (3,2) (3,3) (4,0) (4,4) | 37, 61 |
| 22064 | (2,1) (2,2) (3,3) (4,0) (4,2) (4,4) | 37 |
| 25183 | (0,0) (1,0) (1,1) (2,0) (2,1) (3,0) (3,3) (4,3) (4,4) | 37 |
| 26883 | (0,0) (1,0) (3,2) (4,1) (4,3) (4,4) | 37, 61 |
| 27390 | (1,0) (1,1) (2,0) (2,1) (2,2) (3,0) (3,1) (3,3) (4,1) (4,3) (4,4) | 37 |
| 28586 | (1,0) (2,0) (2,2) (3,1) (3,2) (3,3) (4,0) (4,1) (4,3) (4,4) | 37 |
| 28944 | (2,1) (3,2) (4,2) (4,3) (4,4) | 37 |

**What has been checked** (by the orchestrator, before this card was written):

- **No symmetry.** For all 16, the stabiliser of the support mod 37 in the whole of GL2(Z/37) is
  the lattice's 8, so no hidden symmetry forces any class; the same holds mod 61 for the three.
- **The known conditions, searched wider.** Both conditions were rerun on the 19 targets with
  wider search bounds: the half-Frobenius condition with up to four rule-90 orbit products of
  radius up to 3, and units up to radius 4 with Ψ_e for e ≤ 39; the certificate condition with
  multipliers of radius up to 3, Ψ_e for e ≤ 13 and exponents up to 8q, twisted-pair factors
  from orbits up to radius 3, and, at its own radius, products of two multipliers. Nothing.
- **Images.** Confinement at m is unchanged by any invertible linear map of the exponents mod m.
  For each of the 16, its images under the 2,112 such maps with entries in [−3, 3] (264 distinct
  images each) were put to both conditions, at their own bounds. None is explained.
- **What is not known**: whether the 16 share factors. Two-variable factorisation over GF(2) is
  not in sympy, and nobody has looked.

**Elsewhere in the data**, for comparison: at m = 29 the family has 13 confinements neither
condition explains, against 5.6 ± 2.4 expected; at 25, nine against 1.7 (the fifth pilot's agent
argues these are mostly the chance model's error); at 21, eight against 7.0.

**Find the mechanism**: a condition on a rule f and an odd m that forces every nonzero eigenvalue
of f at m to be a cube (or, more generally, a q-th power), that holds for the targets, and that
you can prove. Say which of the 19 it explains, which other confinements in the data, and where
else it predicts confinement, including sizes and rules the data has not looked at. If part of it
is chance after all, say which part and why.

## Deliverables

1. **`mechanism.py`**, defining

   ```python
   def condition(f: frozenset[tuple[int, int]], m: int) -> int
   ```

   for f a rule's polynomial (a frozenset of exponent pairs, as in `data/rules.json` or
   `tools/family.py`) and m odd. Return q > 1 if your mechanism proves that every nonzero
   eigenvalue of f at m is a q-th power in F(2^d)*, d = ord_m(2), with q dividing 2^d − 1; return
   1 when it makes no claim. It must decide from the structure your mechanism names, not by
   computing the eigenvalues and testing them; the judge reads it. It may use the known mechanisms
   (for instance `tools/halffrob.py` and `tools/certificate.py`). It must take at most about a
   minute for all 1,274 atlas rules at one m ≤ 300, and about two minutes for 2,000 family rules
   at one m ≤ 125.
2. **`proposal.md`**: the mechanism, the proof that your condition implies the claim, how you
   found it, which of the 19 and which other confinements it explains and which not, and where
   else it predicts confinement.
3. **`proposal.py`**: numerical checks of the mechanism with the tools. It prints what it checked
   and whether each check held.
4. **Optional, Lean**: any formal results in `proofs/LatticeProofs/Pilot.lean` (or files under
   `proofs/LatticeProofs/Pilot/`). The judge builds them and lists each theorem's axioms.
5. **`report.md`**: what you found, what you tried, what failed, and what you are unsure of.
   Write it last: the judge starts when it appears on your branch.

Scratch files go under `scratch/`. Commit and push your work to your branch as you go.

## How it is judged

- **Explains**: `condition` on the 19 targets.
- **Sound**: the judge runs `condition` on all 1,274 atlas rules at every odd m in a grid that
  goes beyond the census, and on family rules (a fixed sample, and every confined one it knows
  of) at the sizes in `data/family.json` and at sizes you have not been given. It checks each
  claim with its own eigenvalue computation. One false claim refutes the mechanism as stated.
  You are not told the grid's results.
- **Reach**: how many confinements the condition accounts for, at 37 and elsewhere, and how many
  the known mechanisms do not.
- **Proof**: the orchestrator reads the argument in `proposal.md`; Lean results count for more.

## Tools (`tools/`)

- `eigen.py`: `Field(m)`, eigenvalues, Frobenius orbits, orders, `is_power`, `odd_part`,
  `full_bound`.
- `gf2.py`: the finite fields themselves.
- `tori.py`: small tori and exact periods by simulation, for spot checks.
- `family.py`: the square family: `ORBITS`, `rule(bits)`, `rules()`, `bits_of(orbits)`.
- `chance.py`: forced subfields and the chance model: `symmetries`, `full_symmetries` (all of
  GL2(Z/m), small m), `classes`, `analyse`.
- `halffrob.py`: the fourth pilot's `condition` (mechanism 5), as it submitted it.
- `certificate.py`: the fifth pilot's `condition` (mechanism 6, which includes mechanism 5), as it
  submitted it. It imports `halffrob`, so put `tools/` on the path.

sympy is available for polynomial algebra over GF(2) (univariate factoring, Gröbner bases,
resultants). Run Python with `./python` (after setup).

## The Lean library (`proofs/LatticeProofs/`), if you want it

Lean 4 with mathlib v4.35.0, namespace `LatticeProofs`. `Bridge.lean` has the square torus,
`period`, characters `chi`, eigenvalues `lam`, `isPeriod_iff`, `period_eq_eigenLcm` and
`exists_primitiveRoot`; `Eigen.lean` has order lemmas in characteristic 2; `Periods.lean` proves
the cube and twisted-power mechanisms for particular rules; `Cubes37.lean` and `Cubes25.lean` are
the fourth and fifth pilots' proofs of mechanisms 5 and 6 for particular rules at 37 and 25,
worked examples of this kind of argument (`Cubes37.lean` includes `period_r90_dvd`, rule 90's
confinement at 37). Define what you need in `Pilot.lean`.

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
