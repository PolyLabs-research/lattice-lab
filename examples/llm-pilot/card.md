# Problem card: the hexagon law's 2-part

This card is the whole brief for the pilot's proposer and prover. It states the problem and the
library. It does not say how to solve it.

## The setting

A **torus** is a finite abelian group G with a homomorphism ω : Z² → G from the lattice's
translations. A **rule** is a finite set D ⊂ Z² of translations. One step makes every cell v the
sum mod 2 of the cells v + ω(d), d ∈ D (`gstep ω D`). A rule's **period** on a torus is the least
p > 0 such that, from some time t on, step^(t+p) = step^t as maps of configurations
(`eventualPeriod`, `gperiod ω D`).

- **The square torus of side m:** G = Z/m × Z/m, with ω = reduction mod m (`offsetHom m`).
  `period m D` is a rule's period there.
- **The atlas's hexagonal torus of side n** (n even): G = Z/2n × Z/(n/2), with
  ω(q, r) = (q + 2r mod 2n, r mod n/2), in axial coordinates (`HexCell n`, `hexHom n`).
  `hexPeriod n D` is a rule's period there.
- **H1** (`hexH1Offsets`) is the hexagon's parity rule B135/S135: the six translations
  ±(1, 0), ±(0, 1), ±(1, −1).

**The hexagon law** says that for n = 2^v m with m odd and v ≥ 1, H1's period on the hexagonal
torus of side n is 2 · 2^v · R(m) when m ≥ 5. Here R(m) is the odd part. The library has proved
that R(m) = `period m hexH1Offsets` and that the 2-part is at most 2^(v+1). It has not proved that
the 2-part is exactly 2^(v+1). The law has been checked at every even n up to 400.

## The target

Prove this theorem, by replacing `sorry` in `proofs/LatticeProofs/Pilot.lean`:

```lean
theorem hexPeriod_hexH1_exact {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm5 : 5 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    hexPeriod n hexH1Offsets = 2 ^ (v + 1) * period m hexH1Offsets
```

The statement is fixed: the judge checks it against a pinned copy.

## The library (`proofs/LatticeProofs/`)

Lean 4 with mathlib v4.35.0, all in namespace `LatticeProofs`. Read the files for exact
statements. Each file starts with a summary.

| File | Contents |
| --- | --- |
| `Identities.lean` | Laurent polynomial identities over GF(2), generated, e.g. `hexagon_two_steps` (H1² = (x + 1/x)(y + 1/y)(x/y + y/x)) |
| `Eigen.lean` | order lemmas in rings of characteristic 2 |
| `Bridge.lean` | the square torus `Cell m`, `step`, `period`; `IsEventualPeriod`, `eventualPeriod`, `eventualPeriod_spec`, `isEventualPeriod_iff_dvd`, `iterate_add_mul_eq`; `eq_div_gcd_of_dvd_iff`; characters and eigenvalues at odd m (`chi`, `lam`, `isPeriod_iff`, `period_eq_eigenLcm`); `exists_primitiveRoot` (in `AlgebraicClosure (ZMod 2)`); `embed`; `pow_eq_pow_of_cast_eq`, `pow_val_intCast`; `period_odd` |
| `GroupRing.lean` | tori (G, ω): `gstep`, `gperiod`; the group ring `Laurent` and `act`; `gstep_iterate_two_pow` (Frobenius); `eventualPeriod_iterate` (f^[k] has period P / gcd(P, k)); `isEventualPeriod_restrict_iff`, `eventualPeriod_restrict` (restriction to a sub-torus); `zmodMul` and its lemmas; `offsetHom`, `period_eq_gperiod` |
| `Triangle.lean` | triangular tori (not needed here) |
| `Tori.lean` | reductions to odd parts: `period_div_gcd_two_pow`, `period_eq_two_pow_mul`, `period_eq_two_pow_mul_of_double`; the triangular torus; the hexagonal torus `HexCell`, `hexHom`, `hexPeriod`, `hexMul`, `hexPeriod_div_gcd`; `eq_two_pow_mul_of_div_gcd`, `half_eq` |
| `Rules.lean` | the atlas's neighbourhoods, generated: `hexH1Offsets` and its lemmas |
| `Periods.lean` | theorems about periods, including `hexPeriod_eq_two_pow_mul`: ∃ a ≤ v + 1, hexPeriod n D = 2^a · period m D |
| `TwoPart.lean` | the square XOR law's exact 2-part: `pair`, `adj`, `pair_gstep`, `even_of_jordan`, `period_two_mul_of_proj`, `period_sqN4D4` |

## Tools (`tools/`)

- `gf2.py`: `Field(m)`, the field F(2^d) with a primitive m-th root of unity `zeta`, for odd m.
- `tori.py`: tori as the library models them (`square`, `hexagon`, `torus`), `H1`, the exact
  period of a rule on a small torus (`period`), and `check_jordan`. The last checks whether two
  weights form a Jordan block of a rule's adjoint.

Run Python with `/home/user/pilot-sandbox/python`, which has numpy and sympy.

## Deliverables

1. `proposal.md`: the mechanism in words and formulas. Say what you claim and why it forces the
   2-part.
2. `proposal.py`: a numerical check of the mechanism, using the tools, at several (m, v). It
   prints what it checked and whether each check held.
3. `proofs/LatticeProofs/Pilot.lean` with the proof. You may add files under
   `proofs/LatticeProofs/Pilot/` and import them from `Pilot.lean`.
4. A final report: what you tried, what failed, what worked, and anything you are unsure of.

## Rules

- **Stay in the sandbox.** Work only in `/home/user/pilot-sandbox`. Do not read, list or search
  anything outside it, except the Lean toolchain under `~/.elan` and the Python interpreter. In
  particular stay out of `/home/user/lattice-lab` and the other repositories, `/root/.claude`
  and `/tmp`. Do not use the network.
- Do not change any existing file under `proofs/` except `LatticeProofs/Pilot.lean`. The judge
  compares them with a manifest.
- No `sorry`, no new `axiom`, no `native_decide`. The judge requires `#print axioms` to show only
  `propext`, `Classical.choice` and `Quot.sound`.
- Do not run `lake update` or `lake clean`, and do not touch `proofs/.lake/packages`. That is
  mathlib, built from source, and rebuilding it takes an hour.
- **Build:**

      cd /home/user/pilot-sandbox/proofs
      export PATH=$HOME/.elan/bin:$PATH ELAN_TOOLCHAIN=v4.35.0-local
      lake build LatticeProofs.Pilot
      lake env lean PilotCheck.lean

  `lake env lean <file>` compiles a single file quickly while you iterate.
