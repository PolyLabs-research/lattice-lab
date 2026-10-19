# Problem card: why are the eigenvalues cubes at m = 25?

This card is the whole brief for the pilot's proposer. It states an open question, the data, and
the tools. **Nobody knows the answer**, including whoever wrote this card. A precise negative
result is also useful.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source (half an
hour to an hour). Lean is optional in this pilot; Python is ready within a minute.

## The setting

A **shell rule** of the atlas is a linear cellular automaton over GF(2) on the square, triangular
or hexagonal lattice: each cell becomes the sum mod 2 of the cells in a union of symmetric
neighbour shells, optionally with itself (`self`). On the square and hexagonal lattices a rule is a
Laurent polynomial f(x, y) over GF(2): the set of translations it reads. On the triangle it is a
2 × 2 matrix M with M² = s I, and s is the plane rule that governs it. `data/rules.json` lists all
1,274 shell rules with their polynomial (for the triangle, s) as exponent pairs, and
`data/shells.json` the shells.

**The square family** (`tools/family.py`) is every symmetric square rule within distance 4: the
32,767 nonempty unions of the D4 orbits of the translations with coordinates in [−4, 4]. A family
rule's id is its bit mask over the 15 orbits. The atlas's 1,022 square rules are among them.

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
   λ^(1+2^k) (triangle VO + T13).
5. **half-Frobenius confinement**, found by the previous pilot's agent at m = 37
   (`data/pilot4.md`, implemented as `condition` in `tools/halffrob.py`, proved in Lean in the
   library's `Cubes37.lean`). If 2^g ≡ ±n (mod m) and a polynomial B is invariant under the
   dilation (x, y) ↦ (x^n, y^n) on the m-torus, B's eigenvalues lie in F(2^g). At 37, 2^9 ≡ −6
   and 6² ≡ −1, every element of F(2^9) is a cube in F(2^18), and each of six rules becomes such
   a B after multiplying by rule-90 factors, whose values are cubes at 37 because rule 90 itself is
   confined there. The pure case, B = f, puts every eigenvalue in a subfield.

**Forced subfields and chance** (`tools/chance.py`). Frobenius gives λ(2c) = λ(c)², and a matrix M
that maps a rule's translations onto themselves mod m gives λ(Mᵀc) = λ(c). So if 2^i c = Mᵀc for
such an M, λ(c) lies in F(2^i) whatever the rule. Classes of characters forced into a field whose
elements are all cubes are cubes by structure; the rest are free. The chance model takes each free
class uniform over its forced field and independent, so a rule with k free classes is confined to
the cubes by chance about one time in 3^k. It is approximate: in small fields free classes are
cubes more often than one time in three (37 to 40% at m = 13).

**The census, sorted** (`data/remainder.csv`). The previous pilot's census of all 1,274 atlas rules
at every odd m from 9 to 161 where the cubes are a proper subgroup found 69 rules whose nonzero
eigenvalues are all cubes although mechanisms 1 to 4 do not account for it. Mechanism 5 explains
24. Of the other 45, 34 are consistent with chance (m = 13 and 29); one is a split the atlas
procedure mispredicts (m = 115); one triangle rule has hidden symmetries mod 21 and 69 (72 of
them, not the lattice's 12); five at m = 21 have coinciding eigenvalues and are a mild excess.
**Three, at m = 25, are not explained.** `data/expected.csv` gives the chance model's count at each
size beside the census's.

## The question

**At m = 25**, d = ord_25(2) = 20 and s = sord(25) = 10. The full bound is 2^10 − 1 = 1023 =
3 · 11 · 31, and the cubes are the subgroup of order 341.

- Three atlas rules, **triangle E + T7 + self** (its s), **hexagon H1 + H3 + H13** and
  **hexagon H3 + H4 + H5**, have every nonzero eigenvalue a cube at 25, with 5 or 6 free classes
  each (`data/remainder.csv`).
- In the square family, **14 of the 32,767 rules** are confined to the cubes at 25 although no
  mechanism above or forced subfield accounts for it, against **1.7 ± 1.3 expected by chance**
  (`data/family25.json`, with their orbits and polynomials). Each has 8 to 10 free classes, 6 to 8
  distinct values among them.

**What has been checked:**

- **No symmetry.** For all 14 family rules the stabiliser of the support in the whole of
  GL2(Z/25) is the lattice's 8, and for the three examined no matrix in GL2(Z/25) preserves even
  their eigenvalues on the characters of order 25.
- **Rule 90 is not confined at 25**: its odd part is the full bound, 1023. So mechanism 5's mixed
  case, as it stands, does not apply, and `tools/halffrob.py`'s `condition` makes no claim for
  any of the 17.
- **Some shared factors.** Five of the 14 family rules share the factor (1 + x + x²)(1 + y + y²)
  (up to a monomial: rule 150 along each axis, the atlas's N4 + D4 + self), and two others share
  a different one; the other pairs have no common factor. Neither rule 150 nor N4 + D4 + self is
  confined at 25 by itself (both have odd part 1023).
- **An observation, untested.** 25 has 37's arithmetic: 2^5 ≡ 7 (mod 25) and 7² ≡ −1, and
  2^5 − 1 = 31 is prime to 3, so F(2^5) lies in the cubes of F(2^10). A pair of rule-90 factors
  along w and 7w would have eigenvalue t · t^(2^5) = t^33, always a cube. This is the card
  writer's guess at a lead; it may be wrong or beside the point.

**For comparison** (`data/family21.json`): at m = 21 the family has 12 such rules against 7.0 ± 2.6
expected, a mild excess that may or may not be structure.

**Find the mechanism**: a condition on a rule f and an odd m that forces every nonzero eigenvalue
of f at m to be a cube (or, more generally, a q-th power), that holds for the rules at 25, and
that you can prove. Say which of the 17 it explains, which of the census remainder, and where
else it predicts confinement, including sizes and rules the data has not looked at. If part of the
excess at 25 is chance after all, say which part and why.

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
   (for instance `tools/halffrob.py`). It must take at most about a minute for all 1,274 atlas
   rules at one m ≤ 300, and about two minutes for 2,000 family rules at one m ≤ 75.
2. **`proposal.md`**: the mechanism, the proof that your condition implies the claim, how you
   found it, which of the 17 and of the census remainder it explains and which not, and where
   else it predicts confinement.
3. **`proposal.py`**: numerical checks of the mechanism with the tools. It prints what it checked
   and whether each check held.
4. **Optional, Lean**: any formal results in `proofs/LatticeProofs/Pilot.lean` (or files under
   `proofs/LatticeProofs/Pilot/`). The judge builds them and lists each theorem's axioms.
5. **`report.md`**: what you found, what you tried, what failed, and what you are unsure of.
   Write it last: the judge starts when it appears on your branch.

Scratch files go under `scratch/`. Commit and push your work to your branch as you go.

## How it is judged

- **Explains**: `condition` on the 17 rules at 25.
- **Sound**: the judge runs `condition` on all 1,274 atlas rules at every odd m in a grid that
  goes beyond the census, and on family rules (a fixed sample, and every confined one it knows
  of) at m = 21, 25 and at sizes you have not been given. It checks each claim with its own
  eigenvalue computation. One false claim refutes the mechanism as stated. You are not told the
  grid's results.
- **Reach**: how many confinements the condition accounts for, at 25 and elsewhere, and how many
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
- `halffrob.py`: the previous pilot's `condition` (mechanism 5), as it submitted it.

sympy is available for polynomial algebra over GF(2) (factoring, Gröbner bases, resultants). Run
Python with `./python` (after setup).

## The Lean library (`proofs/LatticeProofs/`), if you want it

Lean 4 with mathlib v4.35.0, namespace `LatticeProofs`. `Bridge.lean` has the square torus,
`period`, characters `chi`, eigenvalues `lam`, `isPeriod_iff`, `period_eq_eigenLcm` and
`exists_primitiveRoot`; `Eigen.lean` has order lemmas in characteristic 2; `Periods.lean` proves
the cube and twisted-power mechanisms for particular rules; `Cubes37.lean` is the previous
pilot's proof of mechanism 5 for its six rules at 37, a worked example of this kind of argument.
Define what you need in `Pilot.lean`.

## Rules

- **Stay in this checkout.** Work only inside this repository's directory. Do not read, list or
  search anything outside it, except the Lean toolchain under `~/.elan` and
  `~/lean-toolchains`, which setup.sh installs.
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
