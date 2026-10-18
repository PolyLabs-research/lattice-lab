# Problem card: the triangle laws' 2-part

This card is the whole brief for the pilot's proposer and prover. It states the problem and the
library. It does not say how to solve it.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source. The
Python part takes a minute; the mathlib build takes about an hour on this machine. You can use the
tools and read the library while it builds. `setup.log` ends with `== done` when it has finished.

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
- **The two triangle parity rules:**
  - `triE`, the edge rule B13/S13: each cell reads its three edge neighbours;
  - `triEVOVS`, the edge+vertex rule B1,3,...,11/S1,3,...,11: each cell reads its twelve edge and
    vertex neighbours.

  Each rule's matrix squares to a plane rule times the identity: `triSEOffsets` for `triE`
  (7 translations) and `triSEVOVSOffsets` for `triEVOVS` (12).

**The triangle law** says that for n = 2^v m with m odd and v ≥ 1, both rules have period
2 · 2^v · L(m) on the atlas's triangular torus of side n when m ≥ 3, where L(m) is the odd part.
The library has proved that the odd part is the square torus period `period m triSEOffsets`
(respectively `period m triSEVOVSOffsets`), and it bounds the 2-part:

- `atlasTriPeriod_triE`: atlasTriPeriod n triE = 2^(a+1) · period m triSEOffsets for some a ≤ v;
- `atlasTriPeriod_triEVOVS`: atlasTriPeriod n triEVOVS = 2^a · period m triSEVOVSOffsets for
  some a ≤ v + 1.

It has not proved that the 2-part is exactly 2^(v+1). The law has been checked at every even n
up to 398.

## The target

Prove these two theorems, by replacing each `sorry` in `proofs/LatticeProofs/Pilot.lean`:

```lean
theorem atlasTriPeriod_triE_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triE = 2 ^ (v + 1) * period m triSEOffsets

theorem atlasTriPeriod_triEVOVS_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triEVOVS = 2 ^ (v + 1) * period m triSEVOVSOffsets
```

The statements are fixed: the judge checks them against a pinned copy.

## The library (`proofs/LatticeProofs/`)

Lean 4 with mathlib v4.35.0, all in namespace `LatticeProofs`. Read the files for exact
statements. Each file starts with a summary.

| File | Contents |
| --- | --- |
| `Identities.lean` | Laurent polynomial identities over GF(2), generated, e.g. the squares of the triangle rules (`triangle_E_s`, `triangle_EVOVS_s_up`, ...) |
| `Eigen.lean` | order lemmas in rings of characteristic 2 |
| `Bridge.lean` | the square torus `Cell m`, `step`, `period`; `IsEventualPeriod`, `eventualPeriod`, `eventualPeriod_spec`, `isEventualPeriod_iff_dvd`, `iterate_add_mul_eq`; `eq_div_gcd_of_dvd_iff`; characters and eigenvalues at odd m (`chi`, `lam`, `isPeriod_iff`, `period_eq_eigenLcm`); `exists_primitiveRoot` (in `AlgebraicClosure (ZMod 2)`); `embed`; `pow_eq_pow_of_cast_eq`, `pow_val_intCast`; `period_odd` |
| `GroupRing.lean` | tori (G, ω): `gstep`, `gperiod`; the group ring `Laurent` and `act`; `gstep_iterate_two_pow` (Frobenius); `eventualPeriod_iterate` (f^[k] has period P / gcd(P, k)); `isEventualPeriod_restrict_iff`, `eventualPeriod_restrict` (restriction to a sub-torus); `zmodMul` and its lemmas; `offsetHom`, `period_eq_gperiod` |
| `Triangle.lean` | triangle rules: `TriRule`, `gtriStep`, `gtriPeriod`; `gtriStep_twice` (two steps are one step of the square's plane rule on each layer), `gtriPeriod_div_two`, `gtriPeriod_eq_two_mul` |
| `Tori.lean` | reductions to odd parts: `period_div_gcd_two_pow`, `period_eq_two_pow_mul`, `period_eq_two_pow_mul_of_double`; the atlas's triangular torus `TriCell`, `triHom`, `atlasTriPeriod`, `triMul`, `triMul_offset`, `triMul_injective`, `half_eq`, `triPeriod_div_gcd`; the hexagonal torus `HexCell`, `hexHom`, `hexPeriod`, `hexMul`, `hexPeriod_div_gcd`; `eq_two_pow_mul_of_div_gcd` |
| `Rules.lean` | the atlas's neighbourhoods, generated: `triE`, `triEVOVS`, their four neighbourhoods, `triSEOffsets`, `triSEVOVSOffsets`, and their lemmas (`grp_...`, `..._card`, `..._symm`) |
| `Periods.lean` | theorems about periods, including `gtriPeriod_triE` (on every torus, period 2 · the square's), `gtriPeriod_triEVOVS`, `atlasTriPeriod_triE`, `atlasTriPeriod_triEVOVS` |
| `TwoPart.lean` | the square XOR law's exact 2-part: `pair`, `adj`, `pair_gstep`, `even_of_jordan`, `period_two_mul_of_proj`, `period_sqN4D4` |
| `HexTwoPart.lean` | the hexagon law's exact 2-part: `hexSubHom`, `hexSubMul`, `hexSubMul_injective`, `hexSub_even`, `hexPeriod_hexH1_exact` |

## Tools (`tools/`)

- `gf2.py`: `Field(m)`, the field F(2^d) with a primitive m-th root of unity `zeta`, for odd m.
- `tori.py`: tori as the library models them (`square`, `hexagon`, `triangle`, `torus`), the
  rules (`TRI_E`, `TRI_EVOVS`, `S_E`, `S_EVOVS`, `H1`), exact periods on small tori (`period` for
  plane rules, `tri_period` for triangle rules), and `check_jordan`. The last checks whether two
  weights form a Jordan block of a plane rule's adjoint.

Run Python with `./python` (after setup), which has numpy and sympy.

## Deliverables

1. `proposal.md`: the mechanism in words and formulas. Say what you claim and why it forces the
   2-part.
2. `proposal.py`: a numerical check of the mechanism, using the tools, at several (m, v). It
   prints what it checked and whether each check held.
3. `proofs/LatticeProofs/Pilot.lean` with the proofs. You may add files under
   `proofs/LatticeProofs/Pilot/` and import them from `Pilot.lean`.
4. `report.md`: what you tried, what failed, what worked, and anything you are unsure of. Write it
   last: the judge starts when it appears on your branch.

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
