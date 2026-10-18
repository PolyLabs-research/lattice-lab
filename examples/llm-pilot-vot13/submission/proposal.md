# Proposal: the 2-part of VO + T13's period on the atlas's triangular torus

## The law

On the atlas's triangular torus of side n = 2^v m (m odd, v ≥ 1, n ≥ 4),

    atlasTriPeriod n triVOT13 = 2^e · P(m),   P(m) = period m triSVOT13Offsets,

    e = vot13TwoExp v m = v + 1   if m ≥ 3,
                          v − 1   if m = 1   (n = 2^v, v ≥ 2; P(1) = 1).

So VO + T13 behaves like the edge rule (`atlasTriPeriod_triE_exact`) at every side with an odd
factor m ≥ 3, while on the pure powers of two its 2-part drops by two from that: the period is
2^(v−1) = n/2.

## How the data led to it

For every row of `data/vot13_periods.csv` I computed P(m) with `tools/tori.py` and divided it
out. The quotient is always a power of two, 2^e. The rows with m = 1 (n = 4, 8, 16, 32, 64) give
e = 1, 2, 3, 4, 5 = v − 1. Every row with m ≥ 3 gives e = v + 1 (n = 6: 4 = 2²·1, n = 12: 8 = 2³·1,
n = 14: 28 = 2²·7, n = 24: 16 = 2⁴·1, n = 48: 32 = 2⁵·1, n = 44: 248 = 2³·31, …). No other
dependence on m shows up, and the mechanism below explains both cases.

## The mechanism

Two steps of VO + T13 are one step of s = triSVOT13Offsets on each layer (`grp_triVOT13`).
Frobenius turns 2^(v−1) steps of s into one step of 2^(v−1)s, and that acts on each coset of
2^(v−1)G the way s acts on the sub-torus G' = Z/2m × Z/m (`triSubHom m`). So 2^v p is a period of
VO + T13 on the torus of side n exactly when p is a period of s on G'
(`isEventualPeriod_atlasTri_iff`). That lemma does not need m odd, so I also use it with m = 2
and m = 4.

**m ≥ 3.** Let ζ be a primitive m-th root of unity in characteristic 2. Take ψ₁(a, b) = ζ^a ζ^b on
G' and ψ₂ = ψ₁ · [a even]. They form a Jordan block of s's adjoint, adj ψ₁ = λψ₁ and
adj ψ₂ = λψ₂ + μψ₁, with

    λ = Σ_{d∈s} ζ^{−d₁} = 1,
    μ = Σ_{d∈s} ζ^{−d₁} [d₁ − d₂ odd] = ζ³ + ζ + ζ⁻¹ + ζ⁻³ = (ζ + ζ⁻¹)³.

Why: s factors as s_E(x, y) · s_E(x³, y³) (`triangle_VOT13_twisted`). On this Jordan block λ is
multiplicative and μ follows the product rule, and s_E has λ = 1 and μ = ζ + ζ⁻¹. Tripling the
translation leaves the parity of d₁ − d₂ unchanged, so the factor s_E(x³, y³) has μ = ζ³ + ζ⁻³.
That gives μ_s = (ζ + ζ⁻¹) + (ζ³ + ζ⁻³) = t + (t³ + t) = t³ with t = ζ + ζ⁻¹, using
ζ³ + ζ⁻³ = t³ − 3t in characteristic 2. Here μ ≠ 0 exactly when ζ² ≠ 1, that is when m ≥ 3. So
every period of s on G' is even (`even_of_jordan`). P(m) is odd, so 2^v P(m) is not a period, and
the library's bound a ≤ v pins the period at exactly 2^(v+1) P(m).

**m = 1.** Now G' = Z/2 × Z/1 has only the trivial character, and the Jordan block is gone:
μ = Σ [d₁ − d₂ odd] = 0 mod 2. Indeed, the 49 translations of s land an odd number of times only
on 0 of Z/4 × Z/2 (`triSubHom 2`). So s is the identity there, and with m = 2, v − 1 in the
reduction, 2^(v−1) is a period of VO + T13 on the torus of side 2^v. On Z/8 × Z/4 (`triSubHom 4`),
the doubled translations 2s land oddly only on 0, so s is an involution there. But s is not the
identity there: from one live cell at 0, the cell (6, 0) becomes live. So 1 is not a period of s
on Z/8 × Z/4, and with m = 4, v − 2 in the reduction, 2^(v−2) is not a period on the torus of
side 2^v when v ≥ 3. At v = 2 the period is even because the layers' parities swap. In both cases
the period is exactly 2^(v−1).

## Checks

`proposal.py` checks the law against every row of the data. It recomputes VO + T13's period on
the atlas tori n = 4, …, 22 with the tools, and checks the Jordan block with λ = 1,
μ = (ζ + 1/ζ)³ (`check_jordan`) on Z/2m × Z/m for m = 3, …, 15. It also checks the fibre counts
on Z/4 × Z/2 and Z/8 × Z/4 and the periods 1 and 2 of s there. Every check holds.
