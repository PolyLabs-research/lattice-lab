# Report: the triangle laws' 2-part

**Result:** I proved both target theorems, `atlasTriPeriod_triE_exact` and `atlasTriPeriod_triEVOVS_exact`, in
`proofs/LatticeProofs/Pilot.lean`. There is no `sorry`, no new axiom and no `native_decide`.
`lake build LatticeProofs.Pilot` succeeds, and `lake env lean PilotCheck.lean` elaborates both
pinned statements. It prints:

    'LatticeProofs.atlasTriPeriod_triE_exact' depends on axioms: [propext, Classical.choice, Quot.sound]
    'LatticeProofs.atlasTriPeriod_triEVOVS_exact' depends on axioms: [propext, Classical.choice, Quot.sound]

The only existing file I changed is `Pilot.lean`. I added `proposal.md`, `proposal.py`, this
report, and scratch files under `scratch/`.

## Mechanism

Throughout, n = 2^v m with m odd, m ≥ 3 and v ≥ 1. R is `triE` or `triEVOVS`, and s is its
square's plane rule.

1. **Reduce to the sub-torus.** Two steps of R are one step of s on each layer. By Frobenius,
   2^(v-1) steps of s are one step of 2^(v-1)·s. Let G' = Z/2m × Z/m with
   ω'(x, y) = (x − y mod 2m, y mod m), the map `triSubHom`. Multiplication by 2^(v-1)
   (`triSubMul`) embeds G' injectively onto 2^(v-1)G, compatibly with ω. The library's
   restriction lemma then gives: 2^v·p is a period of R on G exactly when p is a period of s
   on G'. This is `isEventualPeriod_atlasTri_iff`, and it is the same for both rules.
2. **A Jordan block on G'.** Take ζ a primitive m-th root of unity, ψ₁(a, b) = ζ^a ζ^b, and
   ψ₂ = ψ₁·[a even]. Then adj ψ₁ = λψ₁ and adj ψ₂ = λψ₂ + μψ₁, where:
   - for s_E, λ = 1 and μ = ζ + ζ⁻¹;
   - for s_EVOVS, λ = μ = ζ² + ζ⁻².

   Both are nonzero once ζ² ≠ 1, which is where m ≥ 3 is used. `even_of_jordan` then makes
   every period of s on G' even (`triSub_even`, with `triSub_even_triSE` and
   `triSub_even_triSEVOVS`).
3. **Conclude.** P(m) is odd, so 2^v·P(m) is not a period of R on G. The library already gives
   period = 2^a·P(m) with a ≤ v + 1, so a = v + 1. This step is `atlasTriPeriod_exact_of_even`.

The argument copies `HexTwoPart.lean`'s structure, with the triangular torus's sub-torus in
place of the hexagonal one. It uses the triangle rule's square plus the Frobenius map, so it does
not need the layer-parity argument. That matters for `triEVOVS`, where the library only had
P / gcd(P, 2) = P(s).

## How I checked it

`proposal.py` uses the tools in `tools/`; its full output is in
`scratch/scratch_proposal_out.txt`. All of its checks pass:

- **The embedding:** it is injective and compatible with ω, for m ∈ {3, 5, 7, 9} and v ≤ 3.
- **The Jordan block:** `check_jordan` confirms it with the stated λ and μ for both rules, for
  m ∈ {3, 5, 7, 9, 11, 13, 15, 21}.
- **The sub-torus periods:** the period of s on G' is even, in fact 2·P(m), for m ≤ 11.
- **The law itself:** `tri_period(triangle(n), R) = 2^(v+1)·P(m)` holds for every
  n = 2^v m ≤ 28 with m ≥ 3, that is n ∈ {6, 10, 12, 14, 18, 20, 24, 28}.

## What I tried and what failed

There were no dead ends on the mathematics. The first character I tried, ζ^a (depending on a
only), gives μ = 0 for s_E. The character ζ^a ζ^b, the one used for the hexagon, works for both
rules.

On the Lean side, everything except the four explicit eigenvalue sums compiled on the first try.
For those sums I unfolded each neighbourhood with `simp`, then used `field_simp`, then
`linear_combination c * (2 = 0)`. I found the coefficients c from `ring`'s leftover goals.

## Uncertainties

- None of substance; the judge's rebuild is the final check.
- The build prints a module-system warning about `GroupRing.lean`. It was there before my changes
  and has nothing to do with them.
