# Report: VO + T13's period law on the atlas's triangular torus

## Law

For n = 2^v m with m odd, v ≥ 1 and n ≥ 4:

    atlasTriPeriod n triVOT13 = 2^(vot13TwoExp v m) · period m triSVOT13Offsets
    vot13TwoExp v m = if m = 1 then v - 1 else v + 1

- When m ≥ 3 the exponent is v + 1, the same as for the edge rule.
- When m = 1 (n = 2^v, v ≥ 2) it is v − 1, so the period is n/2, because P(1) = 1.

## Status

`atlasTriPeriod_triVOT13_law` in `proofs/LatticeProofs/Pilot.lean` is fully proved:

- **Build:** `lake build LatticeProofs.Pilot` succeeds.
- **Pinned statement:** `PilotCheck.lean` elaborates against it.
- **Axioms:** `#print axioms` gives only `[propext, Classical.choice, Quot.sound]`.
- **No shortcuts:** there is no `sorry`, `native_decide` or new axiom.
- **Other files:** none were changed.
- **Speed:** `vot13TwoExp` is a single `if` and evaluates instantly, for example `#eval vot13TwoExp 1000000 (10^100+1)` gives `1000001`.

## Mechanism

Two steps of VO + T13 are one step of s = `triSVOT13Offsets` on each layer. The library's `isEventualPeriod_atlasTri_iff` then gives: 2^v p is a period of VO + T13 on the torus of side n = 2^v m exactly when p is a period of s on the sub-torus Z/2m × Z/m (`triSubHom m`). That lemma does not need m to be odd, and I also use it with m = 2 and m = 4.

### m ≥ 3

The proof follows the edge-rule proof in `TriTwoPart.lean`. On Z/2m × Z/m, take:

- ψ₁(a, b) = ζ^a ζ^b
- ψ₂ = ψ₁ · [a even]

These form a Jordan block of s's adjoint with:

- λ = 1
- μ = ζ³ + ζ + ζ⁻¹ + ζ⁻³ = (ζ + ζ⁻¹)³

The reason is that s = s_E(x, y) · s_E(x³, y³) (`triangle_VOT13_twisted`). On this block λ multiplies and μ follows the product rule. With t = ζ + ζ⁻¹ this gives μ = t + (t³ + t) = t³.

μ is nonzero exactly when ζ² ≠ 1, which means m ≥ 3. So every period of s on the sub-torus is even. Combined with P(m) odd and the library's bound, the period is exactly 2^(v+1) P(m).

- Theorems: `triSub_even_triSVOT13`, `atlasTriPeriod_triVOT13_exact`.
- The λ and μ identities are proved by `simp`, `field_simp` and `linear_combination`, with a multiple of (2 = 0).

### m = 1

There is no non-trivial character, so the Jordan block disappears and the 2-part drops by two. I used a general lemma, `gstep_eq_self_of_fibers`: a rule is the identity on a torus if its translations land an odd number of times on 0 and an even number of times on every other cell. The facts below were checked with kernel `decide`:

1. **s is the identity on Z/4 × Z/2.** The reduction with (m, v) := (2, v−1) then shows that 2^(v−1) is a period.
2. **s is an involution on Z/8 × Z/4.** By Frobenius, s² = 2s, and the fibre lemma shows 2s is the identity there.
3. **s is not the identity on Z/8 × Z/4.** From one live cell at 0, the cell (6, 0) becomes live.

From (2) and (3), 1 is not an eventual period of s on Z/8 × Z/4. For v ≥ 3, the reduction with (m, v) := (4, v−2) then shows that 2^(v−2) is not a period. For v = 2, the period is even because the rule swaps the parities of the two layers' live-cell counts. So the period is exactly 2^(v−1). P(1) = 1 because P(1) divides 2¹ − 1.

- Theorems: `atlasTriPeriod_triVOT13_two_pow`, `period_one`.

## How I found and checked it

- **The data.** I divided P(m) (computed with `tools/tori.py`) out of every row of `data/vot13_periods.csv`. The quotient is always 2^e, with e = v − 1 when m = 1 (n = 4 to 64) and e = v + 1 for every m ≥ 3.
- **`proposal.py`.** Run with `./python proposal.py`; it ends with "ALL CHECKS HOLD". It checks:
  - every row of the data against the law;
  - the period on the atlas tori n = 4 to 22, recomputed independently;
  - the Jordan block for m = 3 to 15;
  - the fibre structure and the periods 1 and 2 of s on Z/4 × Z/2 and Z/8 × Z/4.
- **`proposal.md`.** States the law and the mechanism in full.

## What I tried and what failed

Nothing went wrong in substance. Two steps needed fixing along the way:

- **Coefficients.** The (2 = 0) coefficients in the two `linear_combination` steps had to be read from Lean's leftover goals and halved.
- **A `simp` call.** One `simp` did not close a goal, and I replaced it with `simpa using`.

The kernel `decide` checks, over 49 offsets on tori of 8 and 32 cells, worked first time and take a few seconds.

## Uncertainty

I see little. The theorem covers every case of the judge's hypotheses: m odd, v ≥ 1, n ≥ 4. The case m = 1 with v = 1, that is n = 2, is excluded by n ≥ 4, and the proof derives v ≥ 2 from that. The formula's values outside those hypotheses, for even m or m = 0, mean nothing.
