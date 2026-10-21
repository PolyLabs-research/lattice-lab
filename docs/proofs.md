# Formal proofs

**Status: built and checked in Lean 4 with mathlib v4.35.0.** `proofs/` holds the proof side of
the pipeline. It covers:

- the algebraic identities behind the atlas's mechanisms;
- the eigenvalue lemmas that turn those identities into statements about eigenvalues;
- **the bridge**: a linear rule's period on an odd torus is the lcm of the multiplicative orders
  of its nonzero eigenvalues;
- **the group ring**: every rule acts on every torus through F2[Z²]. So each identity is an
  identity between rules on tori of every size;
- **the even-size reduction**: a torus's period has the period of its odd quotient as its odd
  part, and a bounded 2-part. This covers the square torus and the atlas's own triangular and
  hexagonal tori;
- **round 2's three mechanisms as theorems about periods at every size**, for the atlas's own rules;
- **the bound**: on an odd torus the period divides 2^ord(m) − 1, and for a symmetric rule
  2^sord(m) − 1;
- **triangular tori**, including rules with all four matrix entries, and **round 3's twisted
  power on the atlas's own torus**;
- **the XOR law's 2-part**: for B1357/S1357, P(2^v m) = 2^v P(m) at every n whose odd part m is
  greater than 1. So the XOR law holds at every size exactly when it holds at the odd sizes;
- **the hexagon law's 2-part**: for H1, P(2^v m) = 2^(v+1) P(m) on the atlas's hexagonal torus at
  every m ≥ 5. An LLM agent found and proved this in the first pilot of
  [llm-pilot.md](llm-pilot.md);
- **the triangle laws' 2-part**: for both triangle parity rules, P(2^v m) = 2^(v+1) P(m) on the
  atlas's triangular torus at every m ≥ 3. The second pilot's agent proved this. So each
  triangle law holds at n = 2^v m exactly when P(m) = 2^sord(m) − 1, the open odd-part statement;
- **VO + T13's law**: P(2^v m) = 2^(v+1) P(m) for m ≥ 3, and P(2^v) = 2^(v−1), on the atlas's
  triangular torus at every even n ≥ 4. The third pilot's agent found this law from data and
  proved it;
- **the cubes at m = 37**: six rules none of the atlas's first four mechanisms explains each have
  period dividing 87381 = (2^18 − 1)/3 on the 37 × 37 torus, so every eigenvalue is a cube in
  F(2^18), and rule 90's period there divides 87381 too. The fourth pilot's agent found the
  mechanism, half-Frobenius confinement, and proved it;
- **the cubes at m = 25**: five rules have period dividing 341 = (2^10 − 1)/3 on the 25 × 25
  torus, two by cube certificates and three as twisted pairs. The fifth pilot's agent found and
  proved this;
- **unit times cube**: nine square-family rules f = U · g³ have period dividing 87381 at m = 37,
  and three of them have period dividing (2^30 − 1)/3 at m = 61. The sixth pilot's agent found
  and proved this;
- **ninth powers at m = 37**: four radius-5 rules, line units times the fourth pilot's
  half-Frobenius cores, have period dividing 29127 = (2^18 − 1)/9, so every nonzero eigenvalue is
  a ninth power. The seventh pilot's agent found this, and proved it in its second round.

Every result depends only on Lean's standard axioms (`propext`, `Quot.sound`, and for most of them
`Classical.choice`), and none uses `sorry`.

    proofs/check.sh        # lake build, then the axioms of the main results

## What is proved

### Identities (`LatticeProofs/Identities.lean`, generated)

`proofs/generate.py` writes this file from the atlas code: `atlas3.polynomial` and
`atlas3._triangle_entries`, the same functions the registered experiments used. So these are
theorems about the rules as computed. Each identity is between Laurent polynomials over GF(2),
stated for x, x⁻¹, y, y⁻¹ in any commutative ring of characteristic 2. Concretely, there are four
variables x, xi, y, yi with x · xi = 1 and y · yi = 1. That is exactly where a rule's eigenvalues
live, so each identity holds at every eigenvalue at once.

| Theorem | Statement | Used for |
| --- | --- | --- |
| `hexagon_two_steps` | H1² = (x + 1/x)(y + 1/y)(x/y + y/x) | the hexagon theorem: two steps are three passes of rule 90 |
| `hexagon_split` | H1 = (1 + x)(1 + y)(1 + x/y) / x | H1 splits into rule-60 passes |
| `square_D4_tensor` | D4 = (x + 1/x)(y + 1/y) | D4 is rule 90 in each axis |
| `square_N4D4self_tensor` | N4 + D4 + self = (1 + x + 1/x)(1 + y + 1/y) | rule 150 in each axis |
| `square_D4A4self_diagonals` | D4 + A4 + self = (1 + xy + 1/(xy))(1 + x/y + y/x) | rule 150 along each diagonal |
| `square_K8_product` | K8 = N4 D4 | the knight shell splits |
| `square_N4K8C4_cube` | N4 + K8 + C4 = N4³ | round 2's cube |
| `square_A4K8C4self_cube` | A4 + K8 + C4 + self = (1 + N4)³ | round 2's first failure |
| `square_C4self_dilation` | C4 + self = 1 + N4(x³, y³) | round 2's dilation |
| `square_A4C4_separable` | A4 + C4 = q(x + 1/x) + q(y + 1/y), q(t) = t³ + t² + t | round 2's accident at n = 13 |
| `triangle_E_square` | ud_E du_E = 1 + VS | the edge rule squares to (1 + VS) I |
| `triangle_E_s`, `triangle_VOT13_s` | ud du = s, for E and for VO + T13 | the rules' s, as their neighbourhoods |
| `triangle_EVOVS_s_up`, `_ud`, `_du`, `_down` | [[uu, ud], [du, dd]]² = s I for E + VO + VS | the general 2 × 2 case |
| `triangle_VOT13_twisted` | ud du (VO + T13) = s_E(x, y) s_E(x³, y³) | round 3's twisted power |

Each proof is `linear_combination q1 * hx + q2 * hy + Q * h2`. The generator finds the
certificate by dividing lhs − rhs by x·xi − 1 and y·yi − 1 over the integers and halving the
remainder. Lean's `ring` rechecks the whole equation, so nothing in the Python is trusted.
`tests/test_proofs.py` checks two things without Lean: that the committed file is what the
generator writes now, and that every certificate closes.

### Eigenvalue lemmas (`LatticeProofs/Eigen.lean`)

For any commutative ring of characteristic 2:

- `orderOf_pow_div`: raising to the k-th power divides an element's order by gcd(order, k).
- `sqN4K8C4_value`, `sqN4K8C4_order`: every eigenvalue of N4 + K8 + C4 is the cube of N4's.
  Its order is N4's divided by gcd(order, 3).
- `sE_frobenius`: the edge rule's s = 1 + VS commutes with Frobenius:
  s(x, y)^(2^k) = s(x^(2^k), y^(2^k)).
- `triVOT13_value`, `triVOT13_order`: the twisted power. Suppose x³ = x^(2^k) and
  y³ = y^(2^k), as at a character of an m-torus with 3 ≡ 2^k (mod m). Then the eigenvalue of
  VO + T13 is the edge rule's raised to 1 + 2^k, and its order is divided by
  gcd(order, 1 + 2^k).
- `triVOT13_value_neg`: the same with the other sign. Where x³ = x^(−2^k) and y³ = y^(−2^k), as
  when 3 ≡ −2^k (mod m), the eigenvalue is again the edge rule's raised to 1 + 2^k, because s_E is
  symmetric (`triVS_symm`).
- `three_dvd_one_add_two_pow`: for odd k, 3 divides 1 + 2^k. So there, every eigenvalue of
  VO + T13 is a cube.

### The bridge (`LatticeProofs/Bridge.lean`)

Everything here is about the cellular automaton itself, not about an abstract ring.

- **The torus.** A cell is a pair in Z/m × Z/m, and a configuration is a value in GF(2) at every
  cell. A rule is given by its neighbourhood D, a finite set of integer offsets. `step m D` makes
  every cell the sum mod 2 of the cells at its offsets.
- **Periods.** `IsPeriod m D p` says that, from some time on, every configuration recurs after p
  steps: step^(t+p) = step^t as maps. `period m D` is the least positive such p. Both are
  instances of `IsEventualPeriod` and `eventualPeriod`, which apply to any map of a finite set.
  For any such map, `isEventualPeriod_iff_dvd` shows the eventual periods are exactly the
  multiples of the least one.
- **Characters.** Take any field K of characteristic 2 with a primitive m-th root of unity ζ;
  one exists exactly when m is odd. The characters are χ_{j,k}(v) = ζ^(j v₁ + k v₂). The
  eigenvalue at (j, k) is λ_{j,k} = Σ_{d ∈ D} χ_{j,k}(−d).

| Theorem | Statement |
| --- | --- |
| `hat_step` | one step multiplies a configuration's transform at (j, k) by λ_{j,k} |
| `inversion` | a configuration is recovered from its transform; this uses that m is a unit in K |
| `isPeriod_iff` | **p is a period exactly when every eigenvalue is 0 or satisfies λ^p = 1** |
| `isPeriod_iff_orderOf_dvd` | equivalently, p is a multiple of the order of every nonzero eigenvalue |
| `period_eq_eigenLcm` | **the period is the lcm of the orders of the nonzero eigenvalues** |
| `isPeriod_iff_period_dvd` | every period is a multiple of the period |
| `lam_eq_ev` | λ_{j,k} is the rule's Laurent polynomial at x = ζ^(−j), y = ζ^(−k) |

The proof is a finite Fourier transform on (Z/m)². For (⇒), apply the rule to a single live cell,
whose transform is 1 at every character. For (⇐), two configurations with the same transform are
equal (`eq_of_hat_eq`); then step^(1+p) = step^1, so from the first step on, every configuration
recurs after p steps.

**The bound.** Frobenius fixes every eigenvalue: if 2^r ≡ 1 (mod m), then λ^(2^r) = λ. So λ is 0
or λ^(2^r − 1) = 1 (`lam_pow_two_pow`). For a symmetric neighbourhood the same holds when
2^r ≡ −1 (`lam_pow_two_pow_of_symm`). Through the bridge:

| Theorem | Statement |
| --- | --- |
| `period_dvd_two_pow_sub_one` | if 2^r ≡ 1 (mod m), the period divides 2^r − 1 |
| `period_dvd_two_pow_sub_one_of_symm` | for D = −D, if 2^r ≡ −1 (mod m), the period divides 2^r − 1 |
| `period_odd` | on an odd torus every period is odd |

That is the atlas's full bound, 2^ord(m) − 1, or 2^sord(m) − 1 for a symmetric rule, as a theorem.
Whether a rule *reaches* it is the conjecture.

### The group ring (`LatticeProofs/GroupRing.lean`)

The bridge needs a primitive m-th root of unity, so it works only at odd sizes. The group ring
works at every size.

- **Tori.** A torus is any finite abelian group G with a homomorphism ω from the lattice's
  translations Z² to it. `gstep ω D` makes every cell v the sum mod 2 of the cells v + ω(d), and
  `gperiod ω D` is the period. The square torus of side n is G = (Z/n)² with reduction mod n
  (`offsetHom`), and `step n D` is `gstep (offsetHom n) D`.
- **Rules as polynomials.** `Laurent` is F2[Z²], the Laurent polynomials over GF(2). A
  neighbourhood is the polynomial `grp D`, the sum of its translations. `act ω` is the algebra
  homomorphism by which F2[Z²] acts on the configurations of (G, ω) by translations, and `act_grp`
  says `grp D` acts as one step of D.

| Theorem | Statement |
| --- | --- |
| `gstep_eq_iterate` | if grp D = (grp E)^k, a step of D is k steps of E, on every torus |
| `gperiod_eq_of_grp_eq_pow` | then P(D) = P(E) / gcd(P(E), k) |
| `gstep_iterate_two_pow` | Frobenius: 2^k steps of D are one step of 2^k D |
| `eventualPeriod_iterate` | f^[k] has period P / gcd(P, k), for any map of a finite set |
| `isEventualPeriod_restrict_iff` | **the restriction lemma**: let μ : G′ → G be injective with μ(ω′(d)) = ω(N d); then N D on G has exactly the periods of D on G′ |

The restriction lemma reads a configuration of G along each coset r + μ(G′). There N D acts as D
acts on G′, and the cosets cover G.

### The triangular torus (`LatticeProofs/Triangle.lean`)

The triangular lattice has two cells per unit cell, an up and a down triangle. Its translations
form Z² in the atlas's τ coordinates. A triangular torus is a torus (G, ω) of those translations,
with two layers of cells over it.

- **Rules.** A `TriRule` is four neighbourhoods: the translations an up cell reads among up cells
  (uu) and among down cells (ud), and those a down cell reads (du, dd). `gtriStep ω R` is one
  step and `gtriPeriod ω R` the period.
- **Two tori.** The rhombic torus of side m is G = (Z/m)² (`triStep`, `triPeriod`). The atlas's
  torus of side n is G = Z/n × Z/(n/2) (`Tori.lean`, `atlasTriPeriod`).

| Theorem | Statement |
| --- | --- |
| `gtriStep_twice` | if [[uu, ud], [du, dd]]² = S I as Laurent polynomials, two steps of the rule are one step of the plane rule S on each layer, on every torus |
| `gtriStep_twice_of_cross` | the case uu = dd = ∅, where the matrix squares to (ud du) I |
| `gtriPeriod_div_two` | then the period P has P / gcd(P, 2) = P(S) |
| `even_of_isEventualPeriod` | if the rule swaps the parities of the layers' live-cell counts, every period is even |
| `gtriPeriod_eq_two_mul` | then the period is exactly 2 P(S) |

The parity argument starts from a single live up cell: its up layer has an odd count exactly at
even times. Such tori can need a transient of two steps, not one: where s = 0 at a character, the
2 × 2 eigenvalue matrix can be nilpotent of index 2.

### Every size (`LatticeProofs/Tori.lean`)

The atlas's reduction from even sizes to odd parts, formally. Frobenius moves the steps: 2^k
steps of a rule are one step of the rule with every translation multiplied by 2^k. On a torus
whose 2-part has exponent 2^k, those translations stay inside the cosets of the odd part, where
the restriction lemma applies.

| Theorem | Torus | Statement |
| --- | --- | --- |
| `period_div_gcd_two_pow` | square, n = 2^k m′ | P(n) / gcd(P(n), 2^k) = P(m′) |
| `period_eq_two_pow_mul` | square, n = 2^v m | P(n) = 2^a P(m) for some a ≤ v |
| `period_eq_two_pow_mul_of_double` | square | if P(2m) = 2 P(m), then P(2^v m) = 2^v P(m) for every v ≥ 1 |
| `period_image_smul` | square, side n | the rule N D has the period of D on the torus of side n / gcd(n, N) |
| `triPeriod_div_gcd` | the atlas's triangular, n = 2^v m, m odd | a plane rule's period P has P / gcd(P, 2^v) = P(m) |
| `hexPeriod_div_gcd` | the atlas's hexagonal, n = 2^v m, m odd | P / gcd(P, 2^(v+1)) = P(m) |

The atlas's tori are modelled by their translation groups, with the maps of
[parity-lattices.md](parity-lattices.md#the-factor-2--2vn-proved):

- the triangular torus of side n is Z/n × Z/(n/2), via (x, y) ↦ (x − y mod n, y mod n/2);
- the hexagonal torus is Z/2n × Z/(n/2), via (q, r) ↦ (q + 2r mod 2n, r mod n/2).

`tests/test_proofs.py` checks that these models have the atlas engine's exact periods: the
triangle for E, VO + T13 and E + VO + VS, and the hexagon for H1, at n = 6, 10, 12 and 14.
Outside the test the check also covered 8, 16 and 18.

### Theorems about periods (`LatticeProofs/Periods.lean`)

The rules are the atlas's own neighbourhoods. `proofs/generate.py` writes them as sets of
translations into `LatticeProofs/Rules.lean`, from `atlas3.polynomial` and
`atlas3._triangle_entries`. For each set it proves the Laurent polynomial is the polynomial in
`Identities.lean`, both in a field (`ev_…`) and in the group ring (`grp_…`). They follow the
atlas's engine exactly: a cell at g reads g − e for each exponent e of its polynomial, so a
triangle entry's translations are its negated exponents.

Round 2, on the square torus of **every** side n:

| Theorem | Statement | Round 2 |
| --- | --- | --- |
| `period_sqN4K8C4` | P(N4 + K8 + C4) = P(N4) / gcd(P(N4), 3) | the cube |
| `period_sqA4K8C4self` | P(A4 + K8 + C4 + self) = P(N4 + self) / gcd(P(N4 + self), 3) | the first failure, a cube |
| `period_sqC4self` | P(C4 + self, n) = P(N4 + self, n / gcd(n, 3)) | the dilation |

The cubes come straight from the identities through the group ring, and the dilation from the
restriction lemma. They need neither the bridge nor oddness.

Round 3's triangle rules. E is the edge rule (LatticeLife's B13/S13), s_E = 1 + VS its s,
VO + T13 round 3's twisted power, and E + VO + VS LatticeLife's other triangle rule:

| Theorem | Torus | Statement |
| --- | --- | --- |
| `gtriPeriod_triE`, `gtriPeriod_triVOT13` | every triangular torus | P(R) = 2 P(s_R) |
| `gtriPeriod_triEVOVS` | every triangular torus | P / gcd(P, 2) = P(s), the general 2 × 2 case |
| `triPeriod_triE_dvd` | rhombic, odd m | if 2^r ≡ ±1 (mod m), P(E) divides 2 (2^r − 1) |
| `period_triSVOT13` | square, odd m | if 3 ≡ ±2^k (mod m), P(s) = P(s_E) / gcd(P(s_E), 1 + 2^k) |
| `triPeriod_twisted` | rhombic, odd m | if 3 ≡ ±2^k and P(E) = 2P, then P(VO + T13) = 2 (P / gcd(P, 1 + 2^k)) |
| `atlasTriPeriod_triE`, `_triVOT13` | the atlas's, n = 2^v m | P(R) = 2^(a+1) P(s_R, m) for some a ≤ v |
| `atlasTriPeriod_triEVOVS` | the atlas's, n = 2^v m | P = 2^a P(s, m) for some a ≤ v + 1 |
| `atlasTriPeriod_twisted` | the atlas's, n = 2^v m | **if 3 ≡ ±2^k (mod m): E's period has odd part some P, and VO + T13's has odd part P / gcd(P, 1 + 2^k)** |

`atlasTriPeriod_twisted` is round 3's mechanism, proved on the atlas's own tori and for the
quantities round 3 registered: the odd parts of the periods at n = 2m. It covers both signs; m = 35
needs the minus sign. When k is odd, 3 divides 1 + 2^k (`three_dvd_one_add_two_pow`). Up to 141,
the theorem lowers the period at 12 odd sizes, each time by a factor of 3: 5, 25, 29, 35, 53, 55,
77, 95, 97, 101, 115 and 125. Round 3 tested seven of them, 25, 29, 35, 53, 55, 95 and 101, and
those are exactly its seven VO + T13 failures. The twisted power alone still goes through the
bridge, because it holds at the characters (3 ≡ ±2^k), not as a polynomial identity.

The hexagon (`hexPeriod_eq_two_pow_mul`): on the atlas's hexagonal torus of side n = 2^v m, a
rule's period is 2^a P(m) for some a ≤ v + 1. Here P(m) is its period on the square torus of side
m, in axial coordinates. For H1 this is the hexagon law 2 · 2^v(n) · R(m) with its 2-part bounded
by the law's own 2 · 2^v. The odd part is that of a rule on (Z/m)².

### The XOR law's 2-part (`LatticeProofs/TwoPart.lean`)

`period_eq_two_pow_mul_of_double` reduces the 2-part at every even size to the single size 2m.
This file settles that size for the XOR rule, and for N4, with a Jordan block rather than the
local-ring analysis of [xor-periods-proof.md](xor-periods-proof.md#4-even-sizes-reduce-to-odd-ones).

- **Functionals.** A weight ψ on cells gives the linear functional `pair ψ` on configurations.
  One step of the rule turns it into the functional of the adjoint weight `adj ψ` (`pair_gstep`).
- **A Jordan block forces even periods** (`even_of_jordan`). Suppose adj ψ₁ = λψ₁ and
  adj ψ₂ = λψ₂ + μψ₁, with λ and μ nonzero, and some configuration pairs to nonzero with ψ₁. Along
  its orbit the second functional picks up t·λ^(t−1)·μ, and t is only periodic mod 2. So every
  period is even.
- **The XOR rule acts as rule 90 along y** on weights that depend only on y. The x-neighbours
  come in pairs that cancel (`sqN4D4_proj`; `sqN4_proj` for N4).
- **On the 2m-cycle, rule 90 has such a block.** Take ζ a primitive m-th root of unity. The
  weights ζ^y and ζ^y·[y even] have λ = μ = ζ + 1/ζ, which is nonzero for odd m > 1. A single live
  cell pairs to 1 with the first.

| Theorem | Statement |
| --- | --- |
| `period_two_mul_of_proj` | for odd m > 1, P(2m) = 2 P(m) for every rule that acts as rule 90 along y |
| `period_sqN4D4` | **the XOR law's 2-part**: P(2^v m) = 2^v P(m) for B1357/S1357, with m odd > 1 and v ≥ 1 |
| `period_sqN4` | the same for N4 |
| `period_sqN4D4_dvd` | with the bound, P(n) divides 2^v (2^s − 1) whenever 2^s ≡ ±1 (mod m) |

So the XOR law P(n) = 2^v(n) (2^sord(m) − 1) holds at every n with m > 1 exactly when it holds at
the odd part m. At the odd parts it is the open core, checked by machine up to 999 except ten.

### The hexagon law's 2-part (`LatticeProofs/HexTwoPart.lean`, by the pilot agent)

This file is the LLM pilot's proof, verbatim ([llm-pilot.md](llm-pilot.md)). It completes the
hexagon law's 2-part: `hexPeriod_eq_two_pow_mul` bounds it by 2^(v+1), and this file shows the
bound is attained.

- **Stop one Frobenius step early.** 2^v steps of H1 are one step of 2^v H1. Multiplication by
  2^v embeds the torus G′ = Z/2m × Z/m, with (q, r) ↦ (q + 2r, r), onto 2^v G
  (`hexSubMul_injective`). So by the restriction lemma, P divides 2^v p exactly when p is a period
  of H1 on G′. G′ ≅ Z/2 × (Z/m)² keeps the Z/2 factor that the reduction to (Z/m)² loses.
- **A Jordan block on G′** (`hexSub_even`). With ζ a primitive m-th root of unity, the weights
  ζ^a ζ^b and ζ^a ζ^b [a even] form a block with λ = ζ^±1 + ζ^±2 + ζ^±3 and μ = ζ^±1 + ζ^±2. In
  characteristic 2, ζ³λ = (1 + ζ)(1 + ζ²)(1 + ζ³) and ζ²μ = (1 + ζ)(1 + ζ³), so both are nonzero
  once m ≥ 5. `even_of_jordan` makes every period on G′ even, and P(m) is odd.

| Theorem | Statement |
| --- | --- |
| `hexPeriod_hexH1_exact` | **the hexagon law's 2-part**: on the atlas's hexagonal torus of side 2^v m, m odd ≥ 5, H1 has period exactly 2^(v+1) P(m) |

At m = 3 the 2-part is only 2^v: every character with λ ≠ 0 there has μ = 0. This is a different
route from the hand proof in [parity-lattices.md](parity-lattices.md#the-factor-2--2vn-proved),
which goes to 2^(v−1) steps and reads the factor 4 off a Z/4 subgroup.

### The triangle laws' 2-part (`LatticeProofs/TriTwoPart.lean`, by the second pilot's agent)

This file is the second LLM pilot's proof, verbatim ([llm-pilot.md](llm-pilot.md)). The agent
ran in its own container, which held the library but not the write-ups. It follows
`HexTwoPart.lean`'s structure, one level lower.

- **Two steps, Frobenius, restriction.** Two steps of either rule are one step of its square's
  plane rule s on each layer (`gtriStep_twice`). 2^(v−1) steps of s are one step of 2^(v−1) s,
  and multiplication by 2^(v−1) embeds G′ = Z/2m × Z/m, with (x, y) ↦ (x − y, y), onto
  2^(v−1) G (`triSubMul_injective`). So 2^v p is a period of the rule on G exactly when p is a
  period of s on G′ (`isEventualPeriod_atlasTri_iff`).
- **A Jordan block on G′** (`triSub_even`). The weights ζ^a ζ^b and ζ^a ζ^b [a even] give
  λ = 1 and μ = ζ + 1/ζ for the edge rule, and λ = μ = ζ² + 1/ζ² for the edge+vertex rule; both
  are nonzero once m ≥ 3 (`one_add_sq_ne_zero`). P(m) is odd, so every bound but 2^(v+1) is
  ruled out (`atlasTriPeriod_exact_of_even`).

| Theorem | Statement |
| --- | --- |
| `atlasTriPeriod_triE_exact` | **the edge rule's 2-part**: on the atlas's triangular torus of side 2^v m, m odd ≥ 3, B13/S13 has period exactly 2^(v+1) P(s_E, m) |
| `atlasTriPeriod_triEVOVS_exact` | **the edge+vertex rule's 2-part**: the same for B1,3,...,11/S1,3,...,11, with P(s_EVOVS, m) |

This is the hand proof's route (steps 4 and 5 of the triangles in
[parity-lattices.md](parity-lattices.md#the-triangles)): the same level, the same character and
the same coefficients. For the edge+vertex rule it also settles the factor 2, which
`gtriPeriod_triEVOVS` gives only as P / gcd(P, 2) = P(s).

### VO + T13's law (`LatticeProofs/VOT13Law.lean`, by the third pilot's agent)

This file is the third LLM pilot's proof, verbatim ([llm-pilot.md](llm-pilot.md)). The agent was
given a question and data, not the statement. It found the law, defined it as `vot13TwoExp`, and
proved it.

- **m ≥ 3** follows `TriTwoPart.lean`: on Z/2m × Z/m the same weights give a Jordan block with
  λ = 1 and μ = (ζ + 1/ζ)³ (`triSub_even_triSVOT13`), from the twisted factorisation
  s = s_E(x, y) s_E(x³, y³) (`triangle_VOT13_twisted`).
- **m = 1** needs another argument, since there is no nontrivial character. A rule is the
  identity on a torus if its translations land an odd number of times on 0 and an even number of
  times elsewhere (`gstep_eq_self_of_fibers`). Kernel `decide` checks that s is the identity on
  Z/4 × Z/2 (`gstep_triSub_two`), that 2s is the identity on Z/8 × Z/4
  (`gstep_triSub_four_twice`), and that s is not (`gstep_triSub_four_ne`). With the restriction
  lemma these give a period of 2^(v−1) and rule out 2^(v−2) (`atlasTriPeriod_triVOT13_two_pow`).

| Theorem | Statement |
| --- | --- |
| `atlasTriPeriod_triVOT13_exact` | for m odd ≥ 3, VO + T13 has period exactly 2^(v+1) P(s, m) |
| `atlasTriPeriod_triVOT13_two_pow` | at n = 2^v, v ≥ 2, it has period exactly 2^(v−1) |
| `atlasTriPeriod_triVOT13_law` | **VO + T13's law**: for every even n = 2^v m ≥ 4, period 2^(vot13TwoExp v m) P(s, m), with `vot13TwoExp v m = if m = 1 then v - 1 else v + 1` |

At m = 1 the edge rule's period is 2^v and the edge+vertex rule dies, so VO + T13 matches
neither; no hand proof covered this case.

### The cubes at m = 37 (`LatticeProofs/Cubes37.lean`, by the fourth pilot's agent)

The fourth pilot's proof ([llm-pilot.md](llm-pilot.md#pilot-4-the-cubes-at-m--37)), verbatim
except for its namespace, `Pilot` in the sandbox and `Cubes37` here. It takes about 13 minutes to
build here, most of it the triangle rule's identity.

- **The identities**, over GF(2) with x xi = y yi = 1 (`w_identity`, `v_identity`,
  `tri_identity`): for example W(x², y²) t(x) t(y) t(xy) t(x/y) = the eight-cell shell
  (±7, ±5), (±5, ±7), with W = A4 + K8 + B4 + self and t(z) = z + 1/z.
- **The half-Frobenius step**: at 37, 2^9 ≡ −6 and 6² ≡ −1, so the dilation by 6 permutes each
  shell on the right-hand sides, and their eigenvalues satisfy λ^(2^9) = λ: they lie in F(2^9),
  whose nonzero elements have order dividing 511.
- **The lines** where a rule-90 factor vanishes are handled by (t + 1)² = t(z³)/t(z) and
  t(z⁹)/t(z).
- **Rule 90 at 37** (`period_r90_dvd`): Φ_37 is irreducible over GF(2), so t = z + 1/z generates
  F(2^18) = GF(2)[t]/Ψ_37, and v(t) = t^15 + t^13 + t^12 + t^11 + t^9 + t^7 + t^6 + t satisfies
  v(t)³ = t there, by a certified identity. Since t is fixed by the 2^18-th power, so is v(t), and
  t^87381 = v(t)^(2^18 − 1) = 1.

| Theorem | Statement |
| --- | --- |
| `period_w_dvd`, … , `period_tri_dvd` | for each of the six, period 37 D ∣ lcm(511, period 37 r90) |
| `period_r90_dvd` | period 37 r90 ∣ 87381 |
| `period_w_dvd_87381`, … , `period_tri_dvd_87381` | **for each of the six, period 37 D ∣ 87381**, unconditionally |

The first six were in the agent's report; the person following the pilot then asked it for rule
90's case, and the last seven came from that.

### The cubes at m = 25 (`LatticeProofs/Cubes25.lean`, by the fifth pilot's agent)

The fifth pilot's proof ([llm-pilot.md](llm-pilot.md#pilot-5-the-cubes-at-m--25)), verbatim
except for its namespace, `Pilot25` in the sandbox and `Cubes25` here. Its own build takes
about 3 minutes here, and `#print axioms` lists only the standard three for all five theorems. At 25, d = 20, s = 10, and the cubes of F(2^10)* are its elements of order dividing
341 = (2^10 − 1)/3. The five rules are the square family's 3096, 23608, 1227, 21029 and 32184
(unions of D4 orbits within distance 4; `examples/llm-pilot-25/tools/family.py`).

- **Cube certificates** (`r3096_identity`, `r23608_identity`): over GF(2), with x xi = y yi = 1,
  f · (t(x) t(y))³ = B, with t(z) = z + 1/z and B a union of shells that the dilation by
  7 = 2^5 (mod 25) permutes (`r3096_frob`). So λ_B^(2^5) = λ_B: B = 0 or B^31 = 1. Rule-90
  values satisfy t^1024 = t, so off the axes f^341 = B^341 / (t(x) t(y))^1023 = 1. On the axes
  (`axis_val`) f restricts to t²(t + 1)² = t(z) t(z³) = t^129, as 3 = 2^7 (mod 25).
- **Twisted pairs** (`twisted_val`): if C is symmetric and D = C(x, y) C(x³, y³), then D's
  eigenvalue is c^129 with c^1023 = 1, so D^341 = 1. 1227, 21029 and 32184 are such pairs, with
  C = self + N4, self + D4 and N4 + D4.

| Theorem | Statement |
| --- | --- |
| `period_r3096_dvd`, `period_r23608_dvd` | period 25 D ∣ 341, by the cube certificates |
| `period_r1227_dvd`, `period_r21029_dvd`, `period_r32184_dvd` | period 25 D ∣ 341, as twisted pairs |
| `period_dvd_of_val` | if every value of D at 25th roots of unity is 0 or has order dividing 341, period 25 D ∣ 341 |

### Unit times cube at m = 37 and 61 (`LatticeProofs/UnitCubes.lean`, by the sixth pilot's agent)

The sixth pilot's proof ([llm-pilot.md](llm-pilot.md#pilot-6-the-square-family-at-m--37)),
verbatim except for its namespace, `Pilot37b` in the sandbox and `UnitCubes` here. It imports
`Cubes37.lean` for rule 90's confinement at 37, and builds in under a minute.

Nine square-family rules are exactly f = U · g³ over GF(2), with a = x + 1/x, b = y + 1/y,
U ∈ {a + b, ab, (a + 1)(b + 1)} and g ∈ {a + b + 1, ab + 1, ab + a + b}. The cube needs no reason;
the unit's values are cubes:

- a + b = t(XY) t(X/Y) with x = X², y = Y² (`sum_split`), and ab = t(x) t(y): products of rule-90
  values, cubes at 37 by `Cubes37.r90_val`;
- (a + 1)(b + 1): a + 1 = (t(X) + 1)², handled by `Cubes37.line_val` at 37; at 61, where rule 90
  is not confined, `psi3_val61` proves (t + 1)² = t⁶³ from t⁶⁴ = t(z³) (3 = 2⁶ mod 61).

| Theorem | Statement |
| --- | --- |
| `period_r1112_dvd_37`, … (nine) | period 37 D ∣ 87381 = (2^18 − 1)/3 |
| `period_r3461_dvd_61`, `period_r26883_dvd_61`, `period_r18246_dvd_61` | period 61 D ∣ 357913941 = (2^30 − 1)/3 |

### Ninth powers at m = 37 (`LatticeProofs/Ninth37.lean`, by the seventh pilot's agent)

The seventh pilot's proof ([llm-pilot.md](llm-pilot.md#pilot-7-the-ninth-powers-at-m--37)), from
its second round, verbatim except for its namespace: `Pilot37c` in the sandbox, `Ninth37` here. It
imports `Cubes37.lean`, and builds in about a minute.

Four rules of the radius-5 square family are exactly line units times the fourth pilot's
half-Frobenius cores W = A4 + K8 + B4 + self and V = C4 + L8 + M8 + E4, with a = x + 1/x,
b = y + 1/y and Ψ₅(t) = t² + t + 1:

- 699738 = Ψ₅(a)Ψ₅(b)(a + b) · W
- 985232 = a²b²(a + b) · W
- 1431278 = Ψ₅(a)Ψ₅(b) · V
- 1968276 = a²b² · V

The cores' values are F(2⁹)-valued up to rule-90 factors, and so are 27th powers. Exact
exponent bookkeeping shows the units contribute one more factor of 3 than rule 90's cube
confinement: Ψ₅(t)² = t^(2²³ − 1) at 37, since 5 ≡ 2²³. Together these make every eigenvalue a
ninth power.

| Theorem | Statement |
| --- | --- |
| `period_r1968276_dvd`, `period_r985232_dvd`, `period_r1431278_dvd`, `period_r699738_dvd` | period 37 D ∣ 29127 = (2^18 − 1)/9 |

The file holds 32 theorems, and the judge's round-2 build found all of them on the standard axioms
only. The fifth ninth-power rule, 4850, is not covered. The deep dive that followed found a proof
for it, which three independent checkers found stands with repairs
([report](../examples/rule-4850/deep/REPORT.md)). It is not yet written as one document, and not
formalised; section 7.3 of the report sets out a route to Lean.

## What is not
- **Powers of 2.** At n = 2^v (m = 1) the XOR torus dies (Theorem 3 of xor-periods-proof.md).
  That is not formalised.
- **The hexagon's R(m).** Formally, the odd part is H1's period on (Z/m)². That this equals rule
  90's period on the m-cycle (step 5 of the hexagon theorem's proof) is not formalised; there are
  no one-dimensional tori here yet.
- **The rule-150 analogues.** D4 + A4 + self has period P150(n), and H2 + H3 + self has
  2 P150(n). The identities above show these rules split along diagonals and lattice directions.
  That their periods are then exactly rule 150's is research-level, like Vadali and Turner's
  theorem for rule 90.
- **"Unconfined means full bound".** This is a conjecture, and it is false at small sizes (round
  3's coincidences).

## Building it here

In this cloud environment the hosts that serve Lean toolchains (`release.lean-lang.org`) and
mathlib's prebuilt cache (`lakecache.blob.core.windows.net`, `mathlib4.lean-cache.cloud`) are
blocked. GitHub release downloads and git clones work. So the build:

1. installs elan from its GitHub script;
2. downloads `lean-4.35.0-linux.zip` from the Lean 4 GitHub release and links it with
   `elan toolchain link v4.35.0-local`;
3. clones mathlib through `lake update`. Its post-update hook then hangs on the blocked cache,
   and can be stopped once the manifest is written;
4. builds the imported part of mathlib from source. The identities and eigenvalue lemmas need
   1,317 jobs, which took 14.5 minutes on 4 cores. The bridge and the periods add 1,528 more,
   mostly for the algebraic closure, which took 36 minutes. In all that is about 2,850 jobs and
   50 minutes.

The proofs themselves then build in about 20 seconds. Where the cache hosts are allowed,
`lake exe cache get` replaces step 4.

`tests/test_proofs.py` also checks the period theorems against the atlas numerically. That is
not part of the proof; it checks that the formal definitions (the tori, the steps, the periods)
mean what the atlas means.

- The three square theorems are checked with `eigen.py` at every odd size up to 61. The exact
  matrix engine agrees at 3, 5, 9, 15, 21 and 27.
- On the rhombic triangular torus, the period 2 P(s) of E and of VO + T13 is checked with the
  exact engine at every odd side up to 13; outside the test, up to 31.
- The atlas's triangular and hexagonal tori, as modelled in `Tori.lean`, are checked against the
  atlas's engine at n = 6, 10, 12 and 14, and their periods against the reduction theorems' form.
  H1's 2-part is checked to be exactly 2^(v+1) at the sizes with m ≥ 5, and so are the two
  triangle parity rules' and VO + T13's; VO + T13's period n/2 at n = 4, 8 and 16 is checked
  too. The pilots' registered studies checked the hexagon law at 15 further sizes up to 1024,
  both triangle laws at 20, and VO + T13's law at 20, all up to 1024.
- The twisted power is checked with `eigen.py` at every odd m up to 101 with 3 ≡ ±2^k.
- The XOR law's 2-part is checked with the exact engine for B1357/S1357 and N4 at
  m = 3, 5, 7, 9 and 11, with v = 1 and 2.
