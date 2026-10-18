# Proposal: the 2-part of the triangle parity rules

## Claim

Let n = 2^v m with m odd, m ≥ 3, v ≥ 1, let R be `triE` or `triEVOVS`, and s its square's plane
rule (`triSEOffsets`, resp. `triSEVOVSOffsets`). Then 2^v P(m) is **not** a period of R on the
atlas's triangular torus G = Z/n × Z/(n/2) (P(m) = period of s on the square torus of side m).
Combined with the library's bounds (period = 2^a P(m), a ≤ v + 1), the period is exactly
2^(v+1) P(m).

## Mechanism

1. **Reduce 2^v steps of R to one step of a dilated plane rule.** Two steps of R are one step of s
   on each layer (`gtriStep_twice`). So for any p,

       2^v p is a period of R on G  ⟺  2^(v-1) p is a period of s on G
                                    ⟺  p is a period of (s)^[2^(v-1)] = 2^(v-1)·s on G (Frobenius).

2. **Restrict to the sub-torus.** Let G' = Z/2m × Z/m with ω'(x, y) = (x − y mod 2m, y mod m),
   and μ : G' → G, (a, b) ↦ (2^(v-1) a mod n, 2^(v-1) b mod n/2). Then μ is a well defined
   injective homomorphism (n = 2^(v-1)·2m and n/2 = 2^(v-1) m) with μ(ω'(d)) = ω(2^(v-1) d).
   By the restriction lemma, the rule 2^(v-1)·s on G has exactly the periods of s on G'. So

       2^v p is a period of R on G  ⟺  p is a period of s on G'.

3. **A Jordan block on G' forces even periods.** G' ≅ Z/2 × (Z/m)², the Z/2 being a mod 2. Take
   ζ a primitive m-th root of unity in characteristic 2, and the weights

       ψ₁(a, b) = ζ^a ζ^b,       ψ₂(a, b) = ψ₁(a, b) · [a even].

   With c(d) = ζ^-(d₁−d₂) ζ^-d₂ = ζ^-d₁ we get adj ψ₁ = λ ψ₁ and adj ψ₂ = λ ψ₂ + μ ψ₁ with
   λ = Σ_{d∈s} c(d), μ = Σ_{d∈s, d₁−d₂ odd} c(d). Explicitly (in characteristic 2):

   * s_E = {0, ±(1,0), ±(0,1), ±(1,1)}: λ = 1 + 2(ζ + ζ⁻¹) = 1, and μ = ζ + ζ⁻¹
     (the four translations with d₁ − d₂ odd are ±(1,0), ±(0,1)); ζ μ = 1 + ζ².
   * s_EVOVS (12 translations): λ = ζ² + ζ⁻² and μ = ζ² + ζ⁻² (the four translations with
     d₁ − d₂ even, ±(1,1) and ±(1,−1), contribute ζ and ζ⁻¹ twice each, which cancel);
     ζ² λ = ζ² μ = (1 + ζ²)².

   Both are nonzero exactly when ζ² ≠ 1, i.e. m ≥ 3. By `even_of_jordan` (with the delta
   configuration, which pairs to 1 with ψ₁) every period of s on G' is even.

4. **Conclude.** P(m) is odd (`period_odd`), so P(m) is not a period of s on G', so 2^v P(m) is
   not a period of R on G. Since the period is 2^a P(m) with a ≤ v + 1 (`atlasTriPeriod_triE`
   gives a + 1 with a ≤ v; `atlasTriPeriod_triEVOVS` gives a ≤ v + 1), a ≤ v would make 2^v P(m)
   a period. So the exponent is v + 1.

Why m ≥ 3 is needed: at m = 1, ζ = 1 and μ = 0; indeed the law fails there.

## Numerical check

`proposal.py` checks, with `tools/`: the embedding μ (injective, compatible with ω) for several
(m, v); the Jordan block with the stated λ, μ via `check_jordan` for m ∈ {3,…,21}; that the period
of s on G' is even (in fact 2 P(m)) for m ≤ 11; and the end result
`tri_period(triangle(n), R) = 2^(v+1) P(m)` for all n = 2^v m ≤ 28.
