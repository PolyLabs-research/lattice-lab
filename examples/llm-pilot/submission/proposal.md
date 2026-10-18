# Proposal: the hexagon law's 2-part is a Jordan block on a sublattice torus

## Claim

Let n = 2^v m with m odd, m ≥ 5 and v ≥ 1, let G = Z/2n × Z/(n/2) be the atlas's hexagonal
torus with ω(q, r) = (q + 2r, r), and let P be the period of H1 (B135/S135) on it. Then
P = 2^(v+1) · P(m), where P(m) = `period m hexH1Offsets`.

The library already gives P = 2^a · P(m) with a ≤ v + 1 (`hexPeriod_eq_two_pow_mul`). So it is
enough to show that P does **not** divide 2^v · P(m).

## Mechanism

**Step 1: Frobenius moves P | 2^v p onto a sublattice torus.** 2^v steps of H1 are one step of
the dilated rule 2^v·H1 (`gstep_iterate_two_pow`). That rule only moves cells within cosets of
the subgroup 2^v G, and on each coset it acts as H1 acts on

    G' = Z/2m × Z/m,   ω'(q, r) = (q + 2r mod 2m, r mod m)        (Lean: hexSubHom m)

because ι(a, b) = (2^v a, 2^v b) is an injective homomorphism G' → G with image 2^v G and
ι(ω'(d)) = ω(2^v d) (Lean: `hexSubMul`, `hexSubMul_hexSubHom`, `hexSubMul_injective`). The
restriction lemma (`isEventualPeriod_restrict_iff`) then gives

    P | 2^v · p   ⟺   p is an eventual period of H1 on G'.

So it is enough to show that **every period of H1 on G' is even**, because P(m) is odd
(`period_odd`).

Note that G' is *not* a square torus: |G'| = 2m², and G' ≅ Z/2 × (Z/m)², where the Z/2 coordinate
is q mod 2. The previous index-2^(v+1) reduction (`hexPeriod_div_gcd`) lands on the odd torus
(Z/m)² and loses this Z/2 factor. Stopping one Frobenius step earlier keeps it, and that factor
is where the extra 2 lives.

**Step 2: a Jordan block of H1's adjoint on G'.** Over a field K of characteristic 2 the group
ring K[Z/2] = K[s]/(s + 1)² is not semisimple, and an element a + b·s acts on it as the Jordan
block (a + b) + b·ε with ε = s + 1, ε² = 0. Concretely, let ζ ∈ K be a primitive m-th root of
unity (so also ζ^(2m) = 1). Take the weights

    ψ₁(a, b) = ζ^a · ζ^b,       ψ₂(a, b) = ζ^a · ζ^b · [a even]

on G'. With adj ψ(w) = Σ_{d∈H1} ψ(w − ω'(d)), and since ψ₁(w − ω'(d)) = ψ₁(w) · ζ^(−d₁−3d₂)
and the parity of a changes exactly when d₁ is odd,

    adj ψ₁ = λ ψ₁,      adj ψ₂ = λ ψ₂ + μ ψ₁,

where

    λ = Σ_{d∈H1} ζ^(−d₁−3d₂) = ζ + ζ⁻¹ + ζ² + ζ⁻² + ζ³ + ζ⁻³    (H1 at x = ζ⁻¹, y = ζ⁻³),
    μ = Σ_{d∈H1, d₁ odd} ζ^(−d₁−3d₂) = ζ + ζ⁻¹ + ζ² + ζ⁻²       (from ±(1,0), ±(1,−1)).

In characteristic 2 these factor:

    ζ³ λ = (1 + ζ)(1 + ζ²)(1 + ζ³),        ζ² μ = (1 + ζ)(1 + ζ³).

(The first is the library's split H1 = x⁻¹(1 + x)(1 + y)(1 + x/y) at this character.)
Because ζ is a primitive m-th root of unity and m ≥ 5, none of ζ, ζ², ζ³ is 1, so λ ≠ 0 and
μ ≠ 0. A single live cell at the origin pairs to ψ₁(0) = 1 ≠ 0.

**Step 3: the block forces even periods.** `even_of_jordan` (TwoPart.lean): along an orbit, the
ψ₂-functional picks up t · λ^(t−1) · μ · ⟨ψ₁, c⟩, and t is only periodic mod 2 in
characteristic 2. So every eventual period of H1 on G' is even. P(m) is odd, so it is not a
period on G', so P ∤ 2^v · P(m), so a = v + 1.

## Why m ≥ 5 is needed

Over all characters, λ ≠ 0 needs x, y, x/y ≠ 1 and μ ≠ 0 needs y ≠ 1, x² (at x, y the
character's values on the two lattice directions). For m = 3 the only pairs of cube roots of unity
with x, y, x/y ≠ 1 are (ω, ω²) and (ω², ω), and both have y = x², so μ = 0 at every character
with λ ≠ 0, and no block appears. Numerically, at m = 3 the period on G' is P(m) (not 2P(m)) and
the hexagonal period is 2^v · P(m), one factor of 2 short of the law, which is why the law says
m ≥ 5.

## What was checked numerically (`proposal.py`, 56 checks, all held)

1. ι : G' → G is injective onto 2^v G and ι∘ω' = ω∘2^v, at (m, v) = (3,1), (5,1), (5,2),
   (5,3), (7,1), (7,2), (9,2), (15,1).
2. P / gcd(P, 2^v) = P(G') at (5,1), (5,2), (7,1), (7,2), (9,1), (11,1), (13,1), (3,1), (3,2),
   (3,3): the reduction of step 1.
3. The Jordan block, with the tools' `check_jordan` on G' and the weights above, at
   m = 5, 7, 9, 11, 13, 15, 17, 21, 25, 27 (λ, μ ≠ 0), and the two factorisations. At m = 3 the
   relations hold but λ = μ = 0.
4. P(G') = 2 P(m) and P = 2^(v+1) P(m) at (5,1), (5,2), (7,1), (7,2), (9,1), (11,1), (13,1);
   at m = 3, P(G') = P(m) and P = 2^v P(m).

## The Lean proof (`proofs/LatticeProofs/Pilot.lean`)

* `hexSubHom`, `hexSubMul`, `hexSubMul_hexSubHom`, `hexSubMul_injective`: G', the embedding.
* `hexSub_even`: every eventual period of H1 on G' is even (the Jordan block, via
  `even_of_jordan`, with ζ from `exists_primitiveRoot`).
* `hexPeriod_hexH1_exact`: from `hexPeriod_eq_two_pow_mul`, assume a ≤ v. Then P | 2^v P(m),
  which by `isEventualPeriod_iff_dvd`, `isEventualPeriod_iterate_iff`, `gstep_iterate_two_pow`
  and `isEventualPeriod_restrict_iff` makes P(m) a period on G'. That period is even, which
  contradicts `period_odd`.

`#print axioms hexPeriod_hexH1_exact`: propext, Classical.choice, Quot.sound.
