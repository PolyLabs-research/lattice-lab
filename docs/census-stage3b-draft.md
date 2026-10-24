# Census stage 3b: draft predictions (not registered)

**Status: a draft for review.** Nothing has been computed on the held-out tori for this family.
Stage 2 computed only the trinomial subfamily there.

**The family and instruments** are stage 3a's (examples/qec-census-3): every weight-6 code (three
monomials in A and three in B), classes under the census key, k by the common-zero rule and
bb.k_linalg, exact distances by the packing search (small-weight enumeration for k > 128).

**The tori.**
- **Random:** the 22 of holdout.json's held_out_random (lm 56 to 100, n up to 200).
- **Extrapolation:** the 79 of held_out_extrapolation that no earlier development mentioned (lm
  101 to 150, n 202 to 300).
- **Exposed:** the 21 exposed ones (12 x 12, home of [[288,12,18]], among them), judged apart, as
  stage 2 did.

## What stage 3a shows (the evidence)

| Pattern | Stage 3a |
| --- | --- |
| Isomorphic tori give identical class statistics | every isomorphic pair and triple (2x15, 3x10, 5x6; 2x45, 5x18, 9x10; ...) |
| Some code has k > 0 exactly when criterion E holds (below) | 116 of 116 tori (41 have no code with k > 0) |
| Best d is non-increasing in k (connected codes), so the maximum d sits at the smallest k | 75 of 75 tori with codes |
| d_max <= 1.39 sqrt(n) | reached at n = 168 (3x28, 4x21, 7x12), 1.34 at n = 180; never above |
| The best k d^2/n for n <= 200 is the gross code's 12.0 | yes; next [[180,8,16]] at 11.4 |

**Criterion E (proved, not a prediction).** By the common-zero rule, some weight-6 code has k > 0
exactly when A = B = 1 + u + v vanishes at some character. The images of the monomials under a
character of order e are all of mu_e, so this happens exactly when, for some e > 1 dividing the
exponent of the odd part, there is an a in mu_e with a != 1 and 1 + a in mu_e. For example, e = 3
and e = 7 qualify; e = 5, 25, 11, 13, 17 and 19 do not.

## Draft predictions

- **P0, instruments and theorem (decisive).**
  - Criterion E decides, on every held-out torus, whether any code has k > 0.
  - On each torus, k by the common-zero rule agrees with bb.k_linalg on a fixed random sample of
    raw codes.
  - Every witness passes verify_witness, and every class's distance is exact or flagged.
- **P1, monotonicity (decisive).** On every held-out torus with connected codes, the best exact d
  is non-increasing in k.
- **P2, the envelope (decisive).** On every held-out torus, the best d of a connected code is at
  most the largest even number <= 1.40 sqrt(n): 24 at n = 300, 20 at n = 202.
- **P3, no new record below the published one (decisive).**
  - No connected code on a random held-out torus (n <= 200) has k d^2/n above 12.0 (the gross
    code).
  - No connected code on an extrapolation torus (202 <= n <= 300) has k d^2/n above 13.5
    ([[288,12,18]], whose torus 12 x 12 is exposed).
- **P4, Liang et al.'s [[192,8,16]] (decisive).** It lives on Z_2 x Z_48, which is the random
  held-out torus 2 x 48. There the best d at k = 8 is exactly 16: the code exists in this family,
  and nothing beats it.
- **Reported, not judged:**
  - the frontier by (n, k) at n 202 to 300;
  - how often the family beats stage 2's trinomial frontier on the same tori;
  - the exposed tori, 12 x 12 included (prediction: [[288,12,18]] keeps the top score there).

**The verdict.** "hold" when P0 to P4 all pass; "fail" when any fails; "incomplete" when a needed
distance is not exact within the limits and nothing has failed.

## Cost, and a change it needs

- **Random tori:** about as costly as stage 3a. Under 2 hours.
- **Extrapolation tori:** need faster classing first.
  - Stage 3a sent every candidate pair to census.c's canonical key. At 7 x 14 that took 20
    minutes for 2.5 million pairs, and at lm = 150 a torus would have about 14 million.
  - The fix: take orbit representatives of A under the torus group first, and pair each with
    every B. That gives the same classes from about 30 times fewer key computations. It would be
    tested against stage 3a's classes on every stage-1 torus before registration.
- **Distances at n up to 300:** the largest d expected is about 22 to 24. The packing search takes
  seconds to minutes per class there.
- **Total:** an estimated 1 to 2 days on 4 cores, with resume.

## Open choices

1. **Scope.** All 101 unexposed held-out tori, or the random 22 now and the extrapolation later?
2. **P2's constant.** 1.40 is just above the observed 1.389, so it is a tight, risky prediction.
   A looser 1.50 would be safer but say less.
3. **P3.** It predicts that no weight-6 code on these tori beats the published record. If one
   does, that is a finding, but P3 fails.
