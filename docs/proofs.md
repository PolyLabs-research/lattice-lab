# Formal proofs

**Status: built and checked in Lean 4 with mathlib v4.35.0.** `proofs/` holds the proof side of
the pipeline. It covers:

- the algebraic identities behind the atlas's mechanisms;
- the eigenvalue lemmas that turn those identities into statements about eigenvalues;
- **the bridge**: a linear rule's period on an odd torus is the lcm of the multiplicative orders
  of its nonzero eigenvalues;
- through the bridge, **round 2's three mechanisms as theorems about periods**, for every odd
  size, stated for the atlas's own rules;
- **the bound**: on an odd torus the period divides 2^ord(m) − 1, and for a symmetric rule
  2^sord(m) − 1;
- **the triangular torus**, with **round 3's twisted power as a theorem about periods**.

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

### The triangular torus (`LatticeProofs/Triangle.lean`)

The triangular lattice has two cells per unit cell, an up and a down triangle. Its translations
form Z² in the atlas's τ coordinates. The triangular torus of side m is the quotient by mZ²:
m² unit cells and 2m² cells.

- **Rules.** A `TriRule` is four neighbourhoods: the translations an up cell reads among up cells
  (uu) and among down cells (ud), and those a down cell reads (du, dd). `triStep` is one step and
  `triPeriod` the period.
- **Relation to the atlas's torus.** The atlas's torus of side n = 2m has translation group
  Z²/Λ, with Λ = ⟨(m, −m), (m, m)⟩ ⊂ mZ² of index 2 in mZ². So its odd quotient is this torus,
  and the odd part of a rule's period there is the odd part of its period here. That reduction is
  the unformalised one below.

| Theorem | Statement |
| --- | --- |
| `triStep_triStep` | for a rule with uu = dd = ∅ whose cross eigenvalues multiply to those of a square-torus rule S, two steps are one step of S on each layer |
| `even_of_isEventualPeriod` | if the rule swaps the parities of the layers' live-cell counts, every period is even |
| `triPeriod_eq_two_mul` | together, on a torus of odd side, the period is exactly 2 P(S) |

The parity argument starts from a single live up cell: its up layer has an odd count exactly at
even times. The torus can need a transient of two steps, not one. Where s = 0 at a character,
the 2 × 2 eigenvalue matrix can be nilpotent of index 2.

### Theorems about periods (`LatticeProofs/Periods.lean`)

The rules are the atlas's own neighbourhoods. `proofs/generate.py` writes them as sets of offsets
into `LatticeProofs/Rules.lean`, from `atlas3.polynomial`, and proves that each set's Laurent
polynomial is the polynomial in `Identities.lean`. The field is the algebraic closure of GF(2),
which has a primitive m-th root of unity for every odd m (`exists_primitiveRoot`). For every odd
m, on the m × m torus:

| Theorem | Statement | Round 2 |
| --- | --- | --- |
| `period_sqN4K8C4` | P(N4 + K8 + C4) = P(N4) / gcd(P(N4), 3) | the cube |
| `period_sqA4K8C4self` | P(A4 + K8 + C4 + self) = P(N4 + self) / gcd(P(N4 + self), 3) | the first failure, a cube |
| `period_sqC4self` | P(C4 + self, m) = P(N4 + self, m / gcd(m, 3)) | the dilation |

So the mechanisms that broke round 2's registered pattern are now theorems at every odd size, not
just explanations of the sizes tested. Two general results carry them:

- `period_eq_of_lam_eq_pow`: if every eigenvalue of one rule is the n-th power of another's, its
  period is the other's divided by gcd(period, n);
- `eq_div_gcd_of_dvd_iff`: the number theory behind that step.

Round 3's triangle rules, on the triangular torus of every odd side m. Here E is the edge rule
(LatticeLife's B13/S13), s_E = 1 + VS is its s, and VO + T13 is round 3's twisted power:

| Theorem | Statement | Round 3 |
| --- | --- | --- |
| `triPeriod_triE` | P(E) = 2 P(s_E) | the edge rule squares to s_E I |
| `triPeriod_triVOT13` | P(VO + T13) = 2 P(s), s = s_E(x, y) s_E(x³, y³) | |
| `triPeriod_triE_dvd` | if 2^r ≡ ±1 (mod m), P(E) divides 2 (2^r − 1) | the triangle law's bound |
| `period_triSVOT13` | if 3 ≡ ±2^k (mod m), P(s) = P(s_E) / gcd(P(s_E), 1 + 2^k) | |
| `triPeriod_twisted` | **if 3 ≡ ±2^k (mod m) and P(E) = 2P, then P(VO + T13) = 2 (P / gcd(P, 1 + 2^k))** | the twisted power |

`triPeriod_twisted` is the mechanism round 3 found, now a theorem at every odd size, both signs
included; m = 35 needs the minus sign. When k is odd, 3 divides 1 + 2^k
(`three_dvd_one_add_two_pow`). Up to 141, the theorem lowers the period at 12 odd sizes: 5, 25,
29, 35, 53, 55, 77, 95, 97, 101, 115 and 125, each time by a factor of 3. Round 3 tested seven of
them, 25, 29, 35, 53, 55, 95 and 101, and those are exactly its seven VO + T13 failures.

The generated neighbourhoods follow the atlas's engine exactly. A cell at g reads g − e for each
exponent e of its polynomial, so a triangle entry's translations are its negated exponents.

## What is not

- **Even sizes.** The bridge is for odd m: only there is m a unit in a field of characteristic
  2, so that the transform can be inverted. At even sizes the rule is not semisimple. The atlas
  uses the standard reduction: the odd part of the period on a torus is the odd part of the period
  on its odd quotient. For the square that quotient is the torus of side odd(n). For the triangle
  at n = 2m it is the triangular torus of side m above. The reduction is not formalised, so the
  theorems speak about odd sides only. For the triangle, that is the triangular torus of side m,
  not the atlas's n × n torus itself.
- **Triangle rules with a same-orientation part.** `triStep_triStep` assumes uu = dd = ∅, which
  covers E and VO + T13. Rules such as E + VS + self would need the general 2 × 2 case.
- **The hexagon theorem as a whole.** That is the period law 2 · 2^v(n) · R(m), including the
  2-part. `hexagon_two_steps` is its key step.
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
   mostly for the algebraic closure, which took 36 minutes. In all that is 2,845 jobs and about
   50 minutes.

The proofs themselves then build in about 20 seconds. Where the cache hosts are allowed,
`lake exe cache get` replaces step 4.

`tests/test_proofs.py` also checks the period theorems against the atlas numerically. That is
not part of the proof; it checks that the formal definitions (the tori, the steps, the periods)
mean what the atlas means.

- The three square theorems are checked with `eigen.py` at every odd size up to 61. The exact
  matrix engine agrees at 3, 5, 9, 15, 21 and 27.
- On the triangular torus, the period 2 P(s) of E and of VO + T13 is checked with the exact engine
  at every odd side up to 13; outside the test, up to 31.
- The twisted power is checked with `eigen.py` at every odd m up to 101 with 3 ≡ ±2^k.
