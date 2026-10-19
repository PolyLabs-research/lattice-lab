# The agent's messages, verbatim

Every text block of the agent's session, in order, read from its server-side transcript.

## 2026-10-19T16:43:28.495008Z

I've read the card and data; now computing eigenvalue structure of the 17 rules at m = 25 to look for the mechanism.

## 2026-10-19T16:53:37.180675Z

Three of the 14 (1227, 21029, 32184) turn out to be exact twisted products f = C·C(x³,y³) (3 ≡ 2⁷ mod 25). Now factoring the rest by small divisors to find the remaining structure.

## 2026-10-19T16:58:42.766660Z

I've found that confinement is invariant under the 45° map R = [[1,1],[1,−1]] (R² = 2I, a "half-Frobenius" on characters). Testing whether f∘R exposes known structure in the other hits.

## 2026-10-19T17:05:15.273152Z

Extended mechanism 5: f·M³ ≡ B with B ×7-invariant explains 3096 and 23608 (M = t_x t_y), plus the 3 twisted ones. Broadening the search for M to cover the other 9.

## 2026-10-19T17:21:51.026866Z

Mechanism implemented and explaining 5 of the 14 at m = 25; now checking soundness and speed over the whole atlas at several sizes.

## 2026-10-19T17:37:30.393608Z

The certificate also explains 19 of the 45 census-remainder rows: 16 at m = 13 that were filed as "chance", and 3 of the 5 at m = 21. Looking at the witnesses.

## 2026-10-19T17:53:38.987816Z

proposal.py passes all 53 checks (no false claims on the atlas at 9–61, family samples, 19/45 census-remainder rows explained). Fixing the Lean errors now.

## 2026-10-19T17:56:07.472169Z

Lean: all five theorems (`period 25 D ∣ 341` for 3096, 23608, 1227, 21029, 32184) build, depending only on propext, Classical.choice and Quot.sound. Committing.

## 2026-10-19T18:08:39.362774Z

Sweep is through m = 273 with no false claims. Listing the certificate-only claims at 25, 35, 41 and 61 to describe the predictions.

## 2026-10-19T18:16:50.094710Z

Final edits, then committing and pushing proposal and report.

## 2026-10-19T18:17:15.347253Z

I found a provable mechanism for 5 of the 17 rules at m = 25 and formalized all five in Lean. For the other 12 I found no structure; for the 9 family ones the excess largely disappears under a corrected chance model. Everything is pushed to `pilot-25-submission`, with `report.md` last.

## What explains the five

**Cube certificates (rules 3096 and 23608).** Exactly, over GF(2):

- 3096 · (t(x)t(y))³ = Sh(3,1) + Sh(4,1) + Sh(7,1) + Sh(7,3) + Sh(7,4)
- 23608 · (t(x)t(y))³ = Sh(1,1) + Sh(3,1) + Sh(4,1) + Sh(7,3) + Sh(7,4) + Sh(7,7)

Here t(z) = z + 1/z and Sh(a,b) is the D4 orbit of (a,b).

- **Why it works:** each right side is permuted by (x,y) ↦ (x⁷,y⁷) on the 25-torus, and 7 = 2⁵ mod 25. So its eigenvalues lie in F(2⁵), and every element of F(2⁵) is a cube in F(2¹⁰). Off the axes, f is an F(2⁵) element divided by a cube, hence a cube. On the axes, f restricts to t²(t+1)² = t^129, also a cube.
- **What is new:** this is the previous pilot's mechanism with the extra factor raised to a cube. That pilot's version needed rule 90 itself to be confined, which it is not at 25; a factor that enters as a q-th power needs no confinement of its own.
- **General form:** f·M^E ≡ B (mod x^m − 1, y^m − 1), with B invariant under (x,y) ↦ (x^n, y^n), n = 2^g mod m, and q dividing both E and (2^d − 1)/(2^g − 1). On the lines where M vanishes, a one-variable Ψ-exponent criterion is checked. Then every eigenvalue is a q-th power.

**Twisted pairs (rules 1227, 21029, 32184).** Each is exactly C(x,y)·C(x³,y³), with C = self+N4, self+D4 and N4+D4. Since 3 = 2⁷ mod 25, the eigenvalues are c^129, and 129 = 3·43. This is the card's twisted-powers mechanism with d = 3; the census missed it for these three.

**Lean.** `proofs/LatticeProofs/Pilot.lean` proves `period 25 D ∣ 341` (every eigenvalue a cube) for all five. The build succeeds, and the theorems rest only on Lean's three standard axioms (no `sorry`, no new axiom, no `native_decide`).

## What remains unexplained

Rules 6538, 10441, 11508, 12668, 21081, 22626, 24319, 25912 and 26229, plus triangle E+T7+self, hexagon H1+H3+H13 and hexagon H3+H4+H5.

**What I ruled out:**
- twisted pairs with C up to radius 2, for all ten nonsquare ratios mod 25;
- single-multiplier certificates over all 32,767 family rules, also combined with rule-90 and Ψ factors;
- hexagonally symmetric multipliers for the three atlas rules;
- equivalences under GL₂(Z/25): only 1227 and 21029 are related;
- exact factorization by small divisors;
- the line restrictions having roots closed under z ↦ z⁵.

Two-multiplier certificates do exist for the remaining rules, but no more often than for random targets, so they say nothing.

**Why the chance model overstates the excess.** I proved an exact identity:

λ(c)^341 = Norm to F(4) of λ(c) = λ(5c) + E(c)

where E(c) is a sum over length-5 necklaces of the rule's terms. So whether an order-25 class is a cube is strongly tied to the order-5 value at 5c: probability 0.62 when that value is 0 or 1, against 0.06 otherwise. The card's model treats these classes as independent.

| Population at 25 | Unexplained confined | Card-style model | Fibres kept intact |
| --- | --- | --- | --- |
| Square family | 9 | 1.5 | 6.1 (11.8 with axis and diagonal fibres coupled) |
| Hexagonal family, radius 4 | 2 (exactly the two atlas rules) | 0.17 | 0.57 |

## Reach beyond m = 25

- **Census remainder:** 19 of the 45 rows are explained — 16 at m = 13 that had been filed as chance, and 3 of the 5 "coinciding eigenvalues" rules at m = 21.
- **Family at 21:** 4 of the 12 hits are explained, leaving 8 against 7.0 expected.
- **New predictions, both verified:** D4+K8+B4+L8+M8+E4 has only 5th-power eigenvalues at m = 35, and N4+D4+C4+L8+E4+self only 11th-power eigenvalues at m = 61.
- **Common pattern:** n = 2^g with n² ≡ ±1 (mod m): 7 at 25, 8 at 13 and 21, −6 at 37, 11 at 61.

## How I checked it

- **Atlas:** every claim of `condition` was checked against a direct eigenvalue computation at 85 sizes (every odd m from 9 to 161, plus 175 to 299). That is 1,060 claims, none false, at 22–39 s per size.
- **Square family:** the whole family (32,767 rules) at m = 15, 21, 25, 27, 33 and 35 gave no false claim; so did 1,500-rule samples at nine more sizes.
- **Speed:** about 30 s for 2,000 family rules at m = 25 or 75. `condition` computes no eigenvalues of f; it decides from polynomial identities.
- **`proposal.py`:** 31 checks pass by default in about 5 minutes; an earlier run with the atlas at every odd m from 9 to 61 passed all 53.

## What I am unsure of

- **The atlas three.** Three seen against about 0.8 expected (p ≈ 0.05) is a mild excess I cannot account for.
- **The axis–diagonal correlation.** In the family the two fibres are correlated about 2× beyond independence. I measured this but have not explained it, and a mechanism could be hiding there.
- **"Known" versus new.** 1227, 21029 and 32184 are instances of the card's twisted-powers mechanism, although the card counts them as unexplained.
- **Search bounds.** `condition` only searches single multipliers with small vectors and small exponents, so it is sound but incomplete.

## Files
- `report.md`
- `proposal.md`
- `mechanism.py`
- `proposal.py`
- `proofs/LatticeProofs/Pilot.lean`

