# The agent's messages, verbatim

Every text block of the agent's session, in order, read from its server-side transcript.

## 2026-10-18T22:05:46.803464Z

I've read the card and the library; setup is building in the background. Now computing odd-part periods to read off the 2-exponent from the data.

## 2026-10-18T22:08:50.296890Z

Data so far shows exponent v+1 for m ≥ 3 and v−1 for m = 1. Checking the remaining rows, then designing the proofs.

## 2026-10-18T22:11:29.011313Z

Conjectured law: exponent v+1 when m ≥ 3, v−1 when m = 1. Writing the numerical check (proposal.py) while mathlib builds.

## 2026-10-18T22:12:47.579883Z

Mathlib is about a quarter built. Drafting Pilot.lean in the meantime.

## 2026-10-18T22:13:48.589282Z

Draft proof is written and pushed; waiting for mathlib to finish building so I can compile it. Meanwhile, writing proposal.md.

## 2026-10-18T22:14:15.405092Z

Waiting on the mathlib build (job ~750 of ~2800). When it finishes I'll be notified, and then I'll compile and fix the Lean proof.

## 2026-10-18T22:38:07.275692Z

The old exploratory scan hit its time limit and was stopped. proposal.py already covers it, so it doesn't need rerunning. The mathlib build is still going (job ~1950), and I'll compile Pilot.lean once it finishes.

## 2026-10-18T22:55:50.643857Z

The `decide` fibre checks all went through. Fixing the coefficients and small issues:

## 2026-10-18T22:56:18.737324Z

Clean compile. Now the official build, the pinned check, axioms, and `#eval`s:

## 2026-10-18T22:56:52.769243Z

Everything checks out. Tidying the docstring, confirming that no other tracked file changed, then writing the report.

## 2026-10-18T22:58:07.015129Z

# Report: VO + T13's period law on the atlas's triangular torus

I found the exact power of 2 and fully proved `atlasTriPeriod_triVOT13_law`. Everything is pushed to `pilot-vot13-submission`: Pilot.lean, `proposal.md`, `proposal.py` and `report.md`.

## Law

For n = 2^v m with m odd, v ≥ 1 and n ≥ 4:

    atlasTriPeriod n triVOT13 = 2^(vot13TwoExp v m) · period m triSVOT13Offsets
    vot13TwoExp v m = if m = 1 then v - 1 else v + 1

- **m ≥ 3:** the exponent is v + 1, the same as for the edge rule.
- **m = 1** (n = 2^v, v ≥ 2): the exponent is v − 1, and P(1) = 1, so the period is n/2.

## Status

- **Build:** `lake build LatticeProofs.Pilot` succeeds.
- **Pinned statement:** `PilotCheck.lean` elaborates against it.
- **Axioms:** only `propext`, `Classical.choice` and `Quot.sound`.
- **No shortcuts:** no `sorry`, no `native_decide`, no new axiom.
- **Other files:** none of the existing files changed.
- **Speed:** the formula is a single `if`. For example, `#eval vot13TwoExp 1000000 (10^100+1)` returns `1000001` instantly.

## Mechanism

Two steps of the rule are one step of s = `triSVOT13Offsets` on each layer. The library's `isEventualPeriod_atlasTri_iff` then says: 2^v p is a period on the torus of side n = 2^v m exactly when p is a period of s on the smaller torus Z/2m × Z/m. That lemma does not need m to be odd, so I also use it with m = 2 and m = 4.

### m ≥ 3

The proof follows the library's edge-rule proof. On Z/2m × Z/m, take ψ₁(a, b) = ζ^a ζ^b and ψ₂ = ψ₁ · [a even]. They form a Jordan block of s with λ = 1 and μ = (ζ + ζ⁻¹)³.

This comes from s = s_E(x, y) · s_E(x³, y³) (the library's twisted identity). With t = ζ + ζ⁻¹, μ = t + (t³ + t) = t³. That is nonzero exactly when ζ² ≠ 1, which means m ≥ 3. So every period on the smaller torus is even, which forces the exponent to v + 1.

### m = 1

There is no non-trivial character to separate cells, so the Jordan block disappears. I checked three facts with kernel `decide`, through a general lemma (a rule is the identity if its translations land an odd number of times only on 0):

- **s is the identity on Z/4 × Z/2.** So 2^(v−1) is a period.
- **s is an involution on Z/8 × Z/4,** because s² = 2s by Frobenius and 2s is the identity there.
- **s is not the identity on Z/8 × Z/4:** from one live cell at 0, the cell (6, 0) becomes live.

The last two together mean 2^(v−2) is not a period when v ≥ 3. For v = 2, the period is even because the rule swaps the parity of live cells between the two layers. Either way the period is exactly 2^(v−1).

## How I checked it

- **Data:** dividing P(m) out of every row of `data/vot13_periods.csv` always leaves 2^e. The m = 1 rows (n = 4 to 64) give e = v − 1, and every m ≥ 3 row gives e = v + 1.
- **`proposal.py`:** it prints "ALL CHECKS HOLD". It checks:
  - every row of the data against the law;
  - the period recomputed independently for n = 4 to 22;
  - the Jordan block for m = 3 to 15;
  - the behaviour of s on the two small tori.

## What failed along the way

Only small fixes were needed. I read the coefficients for the two `linear_combination` steps off Lean's leftover goals, and one `simp` call had to become `simpa`. The `decide` checks worked first time.

## Uncertainty

I see little doubt. The theorem covers every case the judge's hypotheses allow, and n ≥ 4 excludes n = 2, the only case where the m = 1 formula would not fit. The formula means nothing outside those hypotheses (even m or m = 0).

One note: my first exploratory script hit its time limit and was stopped. `proposal.py` repeats and extends its checks, so nothing depends on it.

