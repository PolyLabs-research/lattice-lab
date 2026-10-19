# Report: the m = 25 cubes

## What I found

Of the seventeen rules, five have a proved reason to be confined to the cubes at m = 25. The
proof is in `proposal.md` and formalized in Lean. The other twelve are unexplained. For those,
the evidence points mostly to a flaw in the chance model, not to a missing mechanism.

1. **Cube certificates: mechanism 5 with a cube as multiplier (Theorem B).** Rules 3096 and
   23608 satisfy, exactly over GF(2), f·(t(x)t(y))³ = B, where B is a union of shells permuted
   by (x, y) ↦ (x⁷, y⁷) on the 25-torus. Since 7 = 2⁵ mod 25, B's eigenvalues lie in F(2⁵), and
   F(2⁵) lies in the cubes of F(2¹⁰). So off the axes λ_f = B/(cube) is a cube. On the axes
   f = t²(t+1)² = t·t(z³) = t^129, also a cube. The previous pilot's mixed case needed rule 90
   to be confined, and it is not at 25. The new point is that a multiplier entering as a q-th
   power needs no confinement of its own. General form: f·M^E ≡ B (mod x^m − 1, y^m − 1),
   with B invariant under ×2^g, q | E and q | (2^d − 1)/(2^g − 1), and a 1-D Ψ-exponent criterion
   on the lines where M vanishes. Then every eigenvalue is a q-th power.
2. **Twisted pairs (Theorem A).** 1227, 21029 and 32184 are C(x, y)·C(x³, y³) exactly, and
   3 = 2⁷ mod 25, so the eigenvalues are c^129. This is the card's twisted-powers mechanism with
   d = 3. The census did not catch these three.
3. **The fibre identity (Lemma 6), which is not a mechanism.**
   λ(c)^341 = N_{F(2¹⁰)/F(4)} λ(c) = λ(5c) + (a necklace sum). So cube-ness at an order-25 class
   is strongly tied to the order-5 value λ(5c): P = 0.62 versus 0.06. The chance model treats
   these classes as independent. A fibre-respecting model expects 6.1 unexplained confined
   family rules at 25, or 11.8 with the axis and diagonal fibres joint. We see 9 after removing
   my five. In the radius-4 hexagonal family, the only unexplained confined rules at 25 are the
   two atlas ones, against 0.57 expected.

**Explained:** 1227, 3096, 21029, 23608, 32184.
**Not explained:** 6538, 10441, 11508, 12668, 21081, 22626, 24319, 25912, 26229, triangle
E+T7+self, hexagon H1+H3+H13, hexagon H3+H4+H5.

**Reach beyond the seventeen:**

* 19 of the 45 census-remainder rows: 16 at m = 13 that had been filed as chance, and 3 of the 5
  "coinciding eigenvalue" square rules at m = 21.
* 4 of the 12 family hits at m = 21 (466, 699, 854, 22429), leaving 8 against 7.0 expected.
* Predictions outside the census's cube question: D4+K8+B4+L8+M8+E4 has only **5th-power**
  eigenvalues at m = 35, and N4+D4+C4+L8+E4+self only **11th-power** eigenvalues at m = 61. Both
  are verified.
* The common arithmetic: n = 2^g with n² ≡ ±1 (mod m). That is 2⁵ = 7 at 25, 2³ = 8 at 13 and
  21, 2⁹ ≡ −6 at 37 and 2¹⁵ ≡ 11 at 61.

## Deliverables

* `mechanism.py`: `condition(f, m)` returns the lcm of what Theorems A and B and the previous
  pilot's `halffrob.condition` prove. For symmetric f it includes the F(2^s) lift, and it returns
  1 when it makes no claim beyond the lift. It decides from polynomial identities mod
  (x^m − 1, y^m − 1): exact products, dilation invariance, and Ψ-division of the line
  restrictions. It computes no eigenvalue of f. Timing: 22–39 s for all 1,274 atlas rules at
  one m ≤ 299; about 30 s for 2,000 family rules at m = 25 or 75.
* `proposal.md`: statements, proofs, the table for the seventeen, what was ruled out, and reach.
* `proposal.py`: by default, 31 checks in about 5 minutes, all passing
  (`scratch/proposal_out.txt`). An earlier run with the atlas at every odd m from 9 to 61 passed
  all 53 of its checks. `--full` adds a wider atlas grid, the whole family at 25 and the family
  chance model. The checks: the five claims against the eigenvalues; the exact identities and ×7
  permutations; the line exponent; soundness on the atlas and on family samples; the
  census-remainder count; Lemma 6 on random rules; and the refined chance model.
* `proofs/LatticeProofs/Pilot.lean`: `period_r3096_dvd`, `period_r23608_dvd`,
  `period_r1227_dvd`, `period_r21029_dvd`, `period_r32184_dvd`, each `period 25 D ∣ 341`, plus
  the general `twisted_val` and `period_dvd_of_val`. They build with
  `lake build LatticeProofs.Pilot` and rest only on propext, Classical.choice and Quot.sound. No
  sorry, no new axiom, no native_decide.

## How I checked it

* Every claim of `condition` was checked against a direct eigenvalue computation:
  * on the atlas at 85 sizes (every odd m from 9 to 161, and 175, 189, 201, 225, 243, 255, 273,
    299): 1,060 claims, **none false**;
  * on the whole square family at m = 15, 21, 25, 27, 33 and 35 (32,767 rules each): no false
    claim;
  * on 1,500-rule family samples at nine more sizes.
* The Lean proofs check the five m = 25 results independently of the Python.
* The identities were checked symbolically: exact Laurent products in Python, and
  `linear_combination` certificates in Lean.

## What I tried that failed

These searches found nothing more for the twelve unexplained rules:

* twisted pairs with C up to radius 2, for all ten nonsquare ratios mod 25;
* A·A(x^n, y^n) mod 25 for every family A;
* single-multiplier certificates over all 32,767 family M with E = 3k, k ≤ 10, also times up to
  two rule-90 or Ψ units;
* hexagonal M for the three atlas rules;
* GL₂(Z/25) equivalences between hits (only 1227 ↔ 21029, via the 45° map);
* 5-adic root closure of the line restrictions;
* exact factorization by small divisors. The cores K = a² + b² + a + b + ab and
  K′ = 1 + ab(a + b) of 3096 and 6538 have no structure I could use.

Two-multiplier certificates do exist for the unexplained rules. But they are as frequent for
random targets (1–10 solutions against 2–9), so they carry no information.

## What I am unsure of

* **Whether the remaining twelve hide structure.** For the family's nine, the refined model
  (9 seen against 6.1 or 11.8) leaves no excess. That model takes the fibre joint laws from the
  family itself. The axis–diagonal correlation (joint/product ≈ 1.95 after removing the explained
  rules) is measured, not explained. A mechanism acting across those two fibres could be hiding
  in it. The atlas's three, against about 0.8 expected (Poisson p ≈ 0.05), are a mild excess I
  cannot account for.
* **The judge's notion of "known mechanism".** Rules 1227, 21029 and 32184 are mechanism 4
  instances (twisted powers, d = 3), although the card lists them as unexplained.
* **Search bounds.** `condition` searches single atoms M with |v| ≤ 2, E ≤ 3q and q < 200, so
  it is sound but incomplete. Some certificate claims at other sizes coincide with what the
  splitting or powers mechanisms already give.
