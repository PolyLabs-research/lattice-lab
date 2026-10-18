# Formal proofs

**Status: built and checked in Lean 4 with mathlib v4.35.0.** `proofs/` holds the first piece of
the proof side of the pipeline:

- the algebraic identities behind the atlas's mechanisms;
- the eigenvalue lemmas that turn those identities into statements about periods.

Every result depends only on Lean's standard axioms (`propext`, `Quot.sound`, and for the order
results `Classical.choice`), and none uses `sorry`.

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

## What is not

- **The bridge.** A rule's period on an odd torus equals the lcm of the multiplicative orders of
  its nonzero eigenvalues. This is standard: F2[(Z/m)²] is semisimple for odd m, and the rule acts
  diagonally on its characters. It is not formalised here, because it needs the Fourier
  decomposition of the group algebra, which mathlib does not provide in this form. The
  experiments back it independently: `eigen.py` and the matrix-power engine agree on all 11,662
  round-3 records.
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
4. builds the imported part of mathlib from source: 1,317 jobs in 14.5 minutes on 4 cores,
   1.7 GB.

The proofs themselves then build in about 10 seconds. Where the cache hosts are allowed,
`lake exe cache get` replaces step 4.
