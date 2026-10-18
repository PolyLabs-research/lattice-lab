# Problem card: find VO + T13's period law, and prove it

This card is the whole brief for the pilot's proposer and prover. It states a question, the data
and the library. It does not say what the answer is or how to prove it.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source. The
Python part takes a minute; the mathlib build takes about half an hour to an hour. You can use the
tools, the data and the library while it builds. `setup.log` ends with `== done` when it has
finished.

## The setting

A **torus** is a finite abelian group G with a homomorphism ω : Z² → G from the lattice's
translations. A **plane rule** is a finite set D ⊂ Z² of translations. One step makes every cell v
the sum mod 2 of the cells v + ω(d), d ∈ D (`gstep ω D`). A rule's **period** on a torus is the
least p > 0 such that, from some time t on, step^(t+p) = step^t as maps of configurations
(`eventualPeriod`, `gperiod ω D`).

- **The square torus of side m:** G = Z/m × Z/m, with ω = reduction mod m (`offsetHom m`).
  `period m D` is a plane rule's period there.
- **Triangle rules** (`TriRule`). The triangular lattice has two cells per translation, up and
  down. A triangle rule is four neighbourhoods uu, ud, du, dd: an up cell reads uu among up cells
  and ud among down cells, and a down cell reads du among up cells and dd among down cells.
  `gtriStep ω R` is one step on the two layers over a torus (G, ω), and `gtriPeriod ω R` is its
  period.
- **The atlas's triangular torus of side n** (n even): G = Z/n × Z/(n/2), with
  ω(x, y) = (x − y mod n, y mod n/2) (`TriCell n`, `triHom n`). `atlasTriPeriod n R` is a
  triangle rule's period there.

## The question

**VO + T13** (`triVOT13`) is a triangle rule: an up cell reads nine down cells and a down cell
reads nine up cells (`triUdVOT13Offsets`, `triDuVOT13Offsets`). Its matrix squares to the plane
rule `triSVOT13Offsets` (49 translations) times the identity. What the library knows:

- `gtriPeriod_triVOT13`: on every triangular torus, its period is twice that of
  `triSVOT13Offsets`;
- `atlasTriPeriod_triVOT13`: on the atlas's triangular torus of side n = 2^v m, with m odd and
  v ≥ 1, its period is 2^(a+1) · `period m triSVOT13Offsets` for some a ≤ v.

It does not know a. **Find the exact power of 2, as a formula in v and m that holds at every
even side n ≥ 4, and prove it.**

**Data.** `data/vot13_periods.csv` gives VO + T13's exact period on the atlas's triangular torus
at every even n from 4 to 64, computed by the atlas's own engine. The tools compute more on
small tori.

## The target

In `proofs/LatticeProofs/Pilot.lean`:

1. **Define your law.** Replace the `sorry` in

   ```lean
   def vot13TwoExp (v m : ℕ) : ℕ
   ```

   with a formula, so that the period is `2 ^ vot13TwoExp v m * period m triSVOT13Offsets`. It
   must be computable and fast: the judge evaluates it with `#eval`, including at very large v
   and m, and compares it with the engine at sizes you have not seen. It does not tell you those
   results.
2. **Prove it.** Replace the `sorry` in

   ```lean
   theorem atlasTriPeriod_triVOT13_law {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
       (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (h4 : 4 ≤ n) :
       atlasTriPeriod n triVOT13 = 2 ^ vot13TwoExp v m * period m triSVOT13Offsets
   ```

The theorem's statement is fixed: the judge checks it against a pinned copy. If you cannot prove
all of it, prove what you can as further theorems in `Pilot.lean`, and say in the report what is
missing. The judge lists the axioms of every theorem in the file.

## The library (`proofs/LatticeProofs/`)

Lean 4 with mathlib v4.35.0, all in namespace `LatticeProofs`. Read the files for exact
statements. Each file starts with a summary.

| File | Contents |
| --- | --- |
| `Identities.lean` | Laurent polynomial identities over GF(2), generated, e.g. the squares of the triangle rules (`triangle_E_s`, `triangle_VOT13_s`, ...) and `triangle_VOT13_twisted` |
| `Eigen.lean` | order lemmas in rings of characteristic 2 |
| `Bridge.lean` | the square torus `Cell m`, `step`, `period`; `IsEventualPeriod`, `eventualPeriod`, `eventualPeriod_spec`, `isEventualPeriod_iff_dvd`, `iterate_add_mul_eq`; `eq_div_gcd_of_dvd_iff`; characters and eigenvalues at odd m (`chi`, `lam`, `isPeriod_iff`, `period_eq_eigenLcm`); `exists_primitiveRoot` (in `AlgebraicClosure (ZMod 2)`); `embed`; `pow_eq_pow_of_cast_eq`, `pow_val_intCast`; `period_odd` |
| `GroupRing.lean` | tori (G, ω): `gstep`, `gperiod`; the group ring `Laurent` and `act`; `gstep_iterate_two_pow` (Frobenius); `eventualPeriod_iterate` (f^[k] has period P / gcd(P, k)); `isEventualPeriod_restrict_iff`, `eventualPeriod_restrict` (restriction to a sub-torus); `zmodMul` and its lemmas; `offsetHom`, `period_eq_gperiod` |
| `Triangle.lean` | triangle rules: `TriRule`, `gtriStep`, `gtriPeriod`; `gtriStep_twice`, `gtriPeriod_div_two`, `gtriPeriod_eq_two_mul` |
| `Tori.lean` | reductions to odd parts: `period_div_gcd_two_pow`, `period_eq_two_pow_mul`, `period_eq_two_pow_mul_of_double`; the atlas's triangular torus `TriCell`, `triHom`, `atlasTriPeriod`, `triMul`, `triMul_offset`, `triMul_injective`, `half_eq`, `triPeriod_div_gcd`; the hexagonal torus `HexCell`, `hexHom`, `hexPeriod`, `hexMul`, `hexPeriod_div_gcd`; `eq_two_pow_mul_of_div_gcd` |
| `Rules.lean` | the atlas's neighbourhoods, generated: `triE`, `triEVOVS`, `triVOT13`, their neighbourhoods, their squares' plane rules (`triSEOffsets`, `triSEVOVSOffsets`, `triSVOT13Offsets`), and their lemmas (`grp_...`, `..._card`, `..._symm`) |
| `Periods.lean` | theorems about periods, including `gtriPeriod_triE`, `gtriPeriod_triVOT13`, `atlasTriPeriod_triE`, `atlasTriPeriod_triVOT13`, `atlasTriPeriod_twisted` (the odd part of VO + T13's period) |
| `TwoPart.lean` | the square XOR law's exact 2-part: `pair`, `adj`, `pair_gstep`, `even_of_jordan`, `period_two_mul_of_proj`, `period_sqN4D4` |
| `HexTwoPart.lean` | the hexagon law's exact 2-part: `hexSubHom`, `hexSubMul`, `hexSubMul_injective`, `hexSub_even`, `hexPeriod_hexH1_exact` |
| `TriTwoPart.lean` | the exact 2-part of the edge and edge+vertex triangle rules for m ≥ 3: `triSubHom`, `triSubMul`, `isEventualPeriod_atlasTri_iff`, `triSub_even`, `atlasTriPeriod_triE_exact`, `atlasTriPeriod_triEVOVS_exact` |

## Tools (`tools/`)

- `gf2.py`: `Field(m)`, the field F(2^d) with a primitive m-th root of unity `zeta`, for odd m.
- `tori.py`: tori as the library models them (`square`, `hexagon`, `triangle`, `torus`), the
  rules (`TRI_E`, `TRI_EVOVS`, `TRI_VOT13`, `S_E`, `S_EVOVS`, `S_VOT13`, `H1`), exact periods on
  small tori (`period` for plane rules, `tri_period` for triangle rules), and `check_jordan`. The
  last checks whether two weights form a Jordan block of a plane rule's adjoint.

Run Python with `./python` (after setup), which has numpy and sympy.

## Deliverables

1. `proposal.md`: your law and the mechanism behind it, in words and formulas: what you claim,
   why it holds, and how the data led you to it.
2. `proposal.py`: a numerical check of the law and the mechanism, using the tools and the data.
   It prints what it checked and whether each check held.
3. `proofs/LatticeProofs/Pilot.lean` with the definition and the proofs. You may add files under
   `proofs/LatticeProofs/Pilot/` and import them from `Pilot.lean`.
4. `report.md`: your law, what you tried, what failed, what worked, and anything you are unsure
   of. Write it last: the judge starts when it appears on your branch.

Scratch files go under `scratch/`. Commit and push your work to your branch as you go.

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
- No `sorry`, no new `axiom`, no `native_decide`. The judge requires `#print axioms` to show only
  `propext`, `Classical.choice` and `Quot.sound`.
- Do not run `lake update` or `lake clean`.
- **Build:**

      cd proofs
      export PATH=$HOME/.elan/bin:$PATH ELAN_TOOLCHAIN=v4.35.0-local
      lake build LatticeProofs.Pilot
      lake env lean PilotCheck.lean

  `lake env lean <file>` compiles a single file quickly while you iterate.
