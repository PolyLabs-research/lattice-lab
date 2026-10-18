# Formal proofs

**Status: built and checked in Lean 4 with mathlib v4.35.0.** `proofs/` holds the proof side of
the pipeline. It covers:

- the algebraic identities behind the atlas's mechanisms;
- the eigenvalue lemmas that turn those identities into statements about eigenvalues;
- **the bridge**: a linear rule's period on an odd torus is the lcm of the multiplicative orders
  of its nonzero eigenvalues;
- through the bridge, **round 2's three mechanisms as theorems about periods**, for every odd
  size, stated for the atlas's own rules.

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
- `three_dvd_one_add_two_pow`: for odd k, 3 divides 1 + 2^k. So there, every eigenvalue of
  VO + T13 is a cube.

### The bridge (`LatticeProofs/Bridge.lean`)

Everything here is about the cellular automaton itself, not about an abstract ring.

- **The torus.** A cell is a pair in Z/m × Z/m, and a configuration is a value in GF(2) at every
  cell. A rule is given by its neighbourhood D, a finite set of integer offsets. `step m D` makes
  every cell the sum mod 2 of the cells at its offsets.
- **Periods.** `IsPeriod m D p` says that, from some time on, every configuration recurs after p
  steps: step^(t+p) = step^t as maps. `period m D` is the least positive such p.
  `exists_isPeriod` shows one exists, since there are finitely many maps.
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
equal; then step^(1+p) = step^1, so from the first step on, every configuration recurs after p
steps.

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

## What is not

- **Even sizes.** The bridge is for odd m: only there is m a unit in a field of characteristic
  2, so that the transform can be inverted. At even sizes the rule is not semisimple. The atlas
  uses the standard reduction: the odd part of the period at n is the period at the odd part of n.
  That reduction is not formalised.
- **The triangle.** The twisted power (round 3) is proved at the eigenvalue level
  (`triVOT13_value`), not yet as a theorem about periods. That needs the triangular torus, with
  two cells per unit cell and a 2 × 2 matrix of polynomials.
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

`tests/test_proofs.py` also checks the three period theorems against the atlas numerically, with
`eigen.py` at every odd size up to 61. That is not part of the proof; it checks that the formal
definitions (the torus, the step, the period) mean what the atlas means. The exact matrix engine
agrees at 3, 5, 9, 15, 21 and 27.
