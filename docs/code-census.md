# A census of bivariate bicycle codes: stages 1 and 2

**Status.**
- **Stage 1** (`examples/qec-census`, run 2026-10-22) is exploratory, not a registered test.
- **Stage 2** (`examples/qec-census-2`, with its continuation `examples/qec-census-2b`) is a
  registered test, on 122 held-out tori, of the findings below. It ran 2026-10-22 to 23.
  - **H1 to H7 and H9 hold.** That includes the risky linear distance law, exact at all 19
    instances, up to d = 20 at n = 300.
  - **H8 does not hold as a general rule.** The pattern that the best codes reduce to the
    [[18,8,2]] base fails on 6 x 18.

  [Stage 2](#stage-2-the-registered-test) has the details.

**Result: every code of the published form on 116 tori with n ≤ 200 was computed, and every one of
its 3,330 classes with k > 0 has an exact distance. The published codes are at or near the top.**
- **The gross code [[144,12,12]] has the highest k d²/n in the census, 12.0.** It is the best of
  the 630 classes at n = 144.
- **The other published codes.** [[90,8,10]] is the best at n = 90. [[108,8,10]] is the best at
  n = 108, tied with one other class. [[72,12,6]] ranks second of 119 at n = 72, behind a
  [[72,8,8]] (k d²/n 6.0 against 7.11).
- **Other bests at their n** include [[98,6,12]], [[150,8,12]], [[162,8,14]], [[180,8,16]],
  [[196,6,18]] and [[198,8,16]]. [[180,8,16]] and [[98,6,12]] are equivalent to codes that other
  sources record with their polynomials ([below](#against-other-sources)). No novelty is claimed.
- **Only 35 of the 116 tori have any code of this form with k > 0.** An exact criterion for which
  tori do was proved by hand and agrees with all 116.
- **Distances.** The exhaustive search completed on all 3,330 classes. The integer program agreed
  on all 284 it solved and bracketed the other 13, all at d = 16 or 18. For the best codes at
  n = 180, 196 and 198, d rests on the search alone.
- **The recheck.** An independent recheck, with its own enumeration, ranks and canonical form,
  found no difference anywhere.

This is the census step of [next-direction.md](next-direction.md). It uses the two distance
instruments of [code-distances.md](code-distances.md), as fixed and retested there.

## What was computed

### The family

A raw code is a pair A = x^a + y^b + y^c, B = y^d + x^e + x^f on the l x m torus, with b ≠ c in
Z_m and e ≠ f in Z_l. This is the form of Bravyi et al.'s codes (`examples/qec-bb/codes.json`).
- A torus has l·C(m,2)·m·C(l,2) raw codes.
- Every code with k > 0 has weights 3 and 3: when two monomials cancel, A or B is a unit and
  k = 0.
- The checks are H_X = [A | B] and H_Z = [B^T | A^T]. A code has n = 2lm.

### The tori, and what was held out

`examples/qec-census/holdout.json` was fixed and committed before any census computation.
- **Stage 1** is every torus with 2 ≤ l ≤ m and lm ≤ 100, except 22 drawn at random and held
  out: 124 tori.
- **Held out for stage 2** are those 22 (`held_out_random`, 50 ≤ lm ≤ 100) and every torus with
  100 < lm ≤ 150 (`held_out_extrapolation`, 100 tori, n = 202 to 300, the published 12 x 12
  among them). They are held out in either orientation.
- **8 stage-1 tori were refused** because they are isomorphic as groups to a held-out torus: 2x36,
  3x26, 4x14, 5x14, 6x11, 6x13, 6x16 and 7x10. Codes on isomorphic tori correspond, so a census of
  6 x 11 would compute codes equivalent to some of the held-out 3 x 22's (`census.py`'s docstring).
- **That leaves 116 tori.** The orientation m x l adds nothing, because exchanging x and y and then
  swapping A and B is an equivalence.

`census.py`'s `guard` refuses every held-out and refused torus before any computation. One omission came to light later: examples/qec-distance-2 had computed the toric
code at 8x11 (in held_out_random) and 10x13 (in held_out_extrapolation) before holdout.json was
fixed, and holdout.json's list of development sizes leaves them out. The family has no code with
k > 0 on either, and stage 2 treats both as exposed. The
recheck confirmed that `data/` holds exactly the 116 allowed tori, and the run's log shows one run
of 116 tori, with no refusals and no failures.

### k, classes, and distances

- **k** = 2lm − 2 rank H_X, by Gaussian elimination in C over every raw code of a torus. There are
  5,472,121 raw codes, and 168,746 of them have k > 0. Each class's k was also recomputed from the
  characters (bb.local_terms), and the two agree on all 3,330 classes.
- **Classes.** Codes with k > 0 are grouped under monomial factors on A and on B, the A ↔ B swap,
  and automorphisms of Z_l x Z_m (examples/qec-distance-2's `equivalence_key`). Equivalent codes
  have the same n, k and d. Codes in different classes may still be equivalent under some other
  qubit permutation, so the classes are an upper bound on the number of inequivalent codes.
  - Classes on isomorphic tori (3x18 and 6x9, for example) are matched by carrying each key onto
    one torus of the type. Each n reports both its classes and its distinct classes.
- **d, the search** (`distance_search`, kind Z, deepening, from the anchors (0, lm)). It ran on
  every class representative and completed on all 3,330: 1,087 s in all, the slowest 26 s. Every
  witness passed `verify_witness`.
- **d, the integer program** (`distance_ilp`, SCIP 10 with `SCIP_FIX`, seed 0, 600 s limit). It
  ran on 297 classes: 118 because they are their torus's best by k d²/n (ties included), and a
  random 5% sample of the rest, 179.
  - 284 finished optimal and **agree** with the search.
  - 13 stopped at the limit and are **consistent**: the interval was [12, 16] or [12, 18], once
    [12, 20], around a search d of 16 or 18.
  - None **disagree**. The program finished on every class with d ≤ 14 it was run on, and on none
    with d ≥ 16.
- **d, the second search** (`recheck`: kind X, from every qubit). It ran on the 4 best classes
  whose cross-check was not "agree": 6x15#142, 7x14#113, 3x33#15 and 3x33#16. All 4 agree. It
  rests on neither the translation argument nor d_X = d_Z, but it shares search.c with the first
  search.

d values over the 3,330 classes: 314 at d = 2, 398 at 4, 427 at 6, 442 at 8, 530 at 10, 563 at
12, 369 at 14, 267 at 16 and 20 at 18.

**The run.** One run of all 116 tori, which finished 4,864 s after it started, with 6x15 last.
The headers' CPU times add up to 17,307 s, most of it in the program: for example 4,522 of 6x15's
4,864 s.

### The recheck

A separate adversarial recheck reused only bb.k_linalg, distance_search and distance_ilp. It
wrote its own guard, GF(2) ranks, witness check, enumeration, automorphisms and canonical form,
and used about 4.3 CPU hours.

| Check | Runs | Outcome |
| --- | --- | --- |
| k by bb.k_linalg and by its own rank, all classes | 3,330 | 0 differences |
| stored witnesses (search / program), its own check | 3,330 / 297 | all logicals of weight d |
| distance_search from every qubit, kinds Z and X, on 598 classes (note 1) | 1,196 | all complete, all equal to d |
| distance_ilp, SCIP_FIX, seed 1, 480 s | 328 (252 never run by the census) | 327 optimal and equal to d; 1 time limit, [12, 16] at d = 14 (7x14#100) |
| meet-in-the-middle distance on 3x9, 3x12, 6x6 (no search.c, no SCIP) | 141 classes | all equal to d |
| brute force of the whole family on 3x9, 3x12, 6x6, 3x15, 6x9, 3x18, 7x7, with distance_search on every raw code with k > 0 | 17,445 raw codes | same raw counts by k, same classes, same (k, d) multisets weighted by size |
| k on every raw code of 2x18, 4x9, 2x27 | 32,238 | k = 0 throughout, as recorded |
| orbit sizes, cross-torus matching, published placements, file hashes and counts | all | consistent |

Note 1: the 598 classes are 498 frontier classes plus 100 random ones. The frontier classes are
the best at each n (ties included), the best d for each k at each n, and every class with
k d²/n ≥ 6.

The brute force rederives the whole frontier at n = 54, 72, 98 and 108, since 2x18, 4x9 and 2x27
have no code with k > 0.

**One limit.** For 190 of the 498 frontier classes, nothing independent of search.c pins d: no
optimal program from either seed and no meet-in-the-middle result.
- They are 52 at d = 12, 74 at d = 14, 44 at d = 16 and 20 at d = 18.
- They include the bests at n = 180, 196 and 198.
- The every-qubit searches remove the translation argument and d_X = d_Z from under them, but not
  search.c.

**Ranks can only err on the pessimistic side.** Every recorded d has a verified witness, so it is
an upper bound on the true d. A class can therefore not truly beat a code that it does not beat on
the record, provided the ranked code's own d is right.
- The gross code's d = 12 is pinned by the program at both seeds.
- At n = 72 the meet-in-the-middle distance pins both [[72,12,6]] and [[72,8,8]], so the rank of
  [[72,12,6]], second, is exact.

## Results

The ranking is by k d²/n, a common figure of merit for codes of this kind.

### The frontier by n

These are the best classes at each n. "Distinct" counts each class once across isomorphic tori.
Every row matches `summary.json`, and regenerating `summary.json` from `data/` gives an identical
file.

| n | tori | classes (distinct) | best [[n,k,d]] (torus#class) | k d²/n | d rests on | best d for each k |
| --- | --- | --- | --- | --- | --- | --- |
| 18 | 3x3 | 4 | [[18,4,4]] 3x3#3 | 3.556 | search, program | k4:4, k8:2 |
| 30 | 3x5 | 1 | [[30,8,2]] 3x5#0 | 1.067 | search, program | k8:2 |
| 36 | 3x6 | 17 | [[36,4,6]] 3x6#16 | 4.000 | search, program | k4:6, k8:4, k16:2 |
| 42 | 3x7 | 1 | [[42,12,2]] 3x7#0 | 1.143 | search, program | k12:2 |
| 54 | 3x9 | 22 | [[54,8,6]] 3x9#6 | 5.333 | search, program | k4:8, k8:6, k12:4, k24:2 |
| 60 | 3x10, 5x6 | 10 (6) | [[60,8,4]]: 5 classes, 3 distinct | 2.133 | search, program | k8:4, k16:2 |
| 72 | 3x12, 6x6 | 119 | [[72,8,8]] 3x12#12 | 7.111 | search, program | k4:8, k8:8, k12:6, k16:4, k32:2 |
| 84 | 3x14, 6x7 | 8 (4) | [[84,12,4]]: 4 classes, 2 distinct | 2.286 | search, program | k12:4, k24:2 |
| 90 | 3x15, 5x9 | 72 | [[90,8,10]] 3x15#12 (published) | 8.889 | search, program | k4:10, k8:10, k12:2, k16:2, k20:4, k24:2, k40:2 |
| 98 | 7x7 | 15 | [[98,6,12]] 7x7#14 | 8.816 | search, program | k6:12, k12:4, k18:4 |
| 108 | 3x18, 6x9 | 352 (214) | [[108,8,10]]: 3x18#35, #39, 6x9#45 (published), #47; 2 distinct | 7.407 | search, program | k4:12, k8:10, k12:6, k16:6, k24:4, k48:2 |
| 120 | 3x20, 5x12, 6x10 | 53 (43) | [[120,16,6]] 6x10#7 | 4.800 | search, program | k8:8, k16:6, k32:2 |
| 126 | 7x9 | 4 | [[126,12,6]] 7x9#2 | 3.429 | search, program | k12:6, k36:2 |
| 144 | 3x24, 6x12 | 630 | [[144,12,12]] 6x12#56 (published) | 12.000 | search, program | k4:14, k8:12, k12:12, k16:8, k24:6, k32:4, k64:2 |
| 150 | 3x25, 5x15 | 50 | [[150,8,12]] 5x15#27, #30, #33 | 7.680 | search, program | k8:12, k16:8, k40:2 |
| 162 | 3x27, 9x9 | 247 | [[162,8,14]] 3x27#34, #35 | 9.679 | search, program | k4:16, k8:14, k12:8, k24:6, k36:4, k72:2 |
| 168 | 3x28, 6x14, 7x12 | 37 (27) | [[168,12,8]]: 10 classes, 7 distinct | 4.571 | search, program | k12:8, k24:4, k48:2 |
| 180 | 3x30, 5x18, 6x15, 9x10 | 1,279 (780) | [[180,8,16]] 6x15#142 | 11.378 | search; program [12, 16]; second search 16 | k4:18, k8:16, k12:4, k16:10, k20:6, k24:4, k32:2, k40:4, k48:2, k80:2 |
| 196 | 7x14 | 156 | [[196,6,18]] 7x14#113 | 9.918 | search; program [12, 18]; second search 18 | k6:18, k12:12, k18:8, k24:4, k36:4 |
| 198 | 3x33 | 253 | [[198,8,16]] 3x33#15, #16 | 10.343 | search; program [12, 16]; second search 16 | k4:18, k8:16, k44:4, k88:2 |

"search, program" means both are exact and agree. The best-d-for-each-k column counts classes,
and some are the same code on isomorphic tori: at n = 108, k = 4, d = 12 is reached by 45 classes
but only 27 distinct.

### The published codes

| Published | Census class (raw codes) | Rank by k d²/n at its n | Rank on its torus |
| --- | --- | --- | --- |
| [[72,12,6]] | 6x6#7 (4) | 2 of 119, behind [[72,8,8]] 3x12#12 | 1 of 47 |
| [[90,8,10]] | 3x15#12 (24) | 1 of 72 | 1 of 68 |
| [[108,8,10]] | 6x9#45 (18) | 1 of 214, tied with 6x9#47 (= 3x18#35) | 1 of 188 |
| [[144,12,12]], the gross code | 6x12#56 (16) | 1 of 630, and first in the census | 1 of 331 |
| [[288,12,18]] | 12 x 12 is held out | not placed; nothing was computed | - |
| [[30,4,6]], [[42,6,6]], [[70,6,8]], [[108,12,6]] (two versions), [[126,12,10]] (two versions) | none: not of the family's form up to its equivalences | - | - |

The 7 codes in the last row match no raw code of the family on their torus. At 5x7 and 2x27 the
family has no code with k > 0 at all.

**The two codes at n = 72.**

| | [[72,12,6]], 6x6#7 (published) | [[72,8,8]], 3x12#12 |
| --- | --- | --- |
| A, B | x^3 + y + y^2, y^3 + x + x^2 (Bravyi et al.'s polynomials) | 1 + y + y^5, y^9 + x + x^2 |
| torus | x^6 = y^6 = 1 | x^3 = y^12 = 1 |
| k from the characters | two Frobenius orbits of size 2 at the order-3 characters, terms 1 and 2: 2(2 + 4) = 12 | two orbits of size 2, terms 1 and 1: 2(2 + 2) = 8 |
| raw codes in the class; stabiliser | 4; 12 | 6; 8, including the dilation (x, y) → (x^5, y^5) |
| d | 6 (program optimal in 0.31 s; meet-in-the-middle 6) | 8 (program optimal in 0.87 s; meet-in-the-middle 8) |
| k d²/n | 6.000 | 7.111 |

### The Pareto front

A triple [[n,k,d]] is undominated if no other triple has n' ≤ n, k' ≥ k and d' ≥ d. **39 of the 225
distinct triples are undominated:**

| n | Undominated |
| --- | --- |
| 18 | [[18,8,2]], [[18,4,4]] |
| 36 | [[36,16,2]], [[36,8,4]], [[36,4,6]] |
| 54 | [[54,24,2]], [[54,12,4]], [[54,8,6]], [[54,4,8]] |
| 72 | [[72,32,2]], [[72,16,4]], [[72,12,6]], [[72,8,8]] |
| 90 | [[90,40,2]], [[90,20,4]], [[90,8,10]] |
| 98 | [[98,6,12]] |
| 108 | [[108,48,2]], [[108,24,4]], [[108,16,6]] |
| 144 | [[144,64,2]], [[144,32,4]], [[144,24,6]], [[144,16,8]], [[144,12,12]], [[144,4,14]] |
| 162 | [[162,72,2]], [[162,36,4]], [[162,8,14]], [[162,4,16]] |
| 180 | [[180,80,2]], [[180,40,4]], [[180,16,10]], [[180,8,16]], [[180,4,18]] |
| 196 | [[196,18,8]], [[196,6,18]] |
| 198 | [[198,88,2]], [[198,44,4]] |

- Two series run at constant k d²/n on the tori with 3 | l and 3 | m: k = 4n/9 at d = 2, and
  k = 2n/9 at d = 4.
- [[198,8,16]] is not on the front, because [[180,8,16]] dominates it.
- [[180,16,10]] on 3x30 is two disjoint copies of the published [[90,8,10]]: b, c and d are even,
  and each half is 3x15#12. The 6x15 class with the same parameters has the same halves.

**Highest k d²/n over all classes:**

| # | [[n,k,d]] | k d²/n | classes |
| --- | --- | --- | --- |
| 1 | [[144,12,12]] | 12.000 | 6x12: 1 |
| 2 | [[180,8,16]] | 11.378 | 6x15: 1 |
| 3 | [[198,8,16]] | 10.343 | 3x33: 2 |
| 4 | [[196,6,18]] | 9.918 | 7x14: 1 |
| 5 | [[162,8,14]] | 9.679 | 3x27: 2 |
| 6 | [[90,8,10]] | 8.889 | 3x15: 1 |
| 6 | [[180,16,10]] | 8.889 | 3x30: 1, 6x15: 1 |
| 8 | [[98,6,12]] | 8.816 | 7x7: 1 |
| 8 | [[196,12,12]] | 8.816 | 7x14: 1 |
| 10 | [[180,8,14]] | 8.711 | 3x30: 2, 6x15: 4 |

### Per torus

Only 35 of the 116 tori have a code with k > 0. "Programs" counts the classes the program ran on,
with how many agree and how many are consistent.

| Torus | n | raw codes with k > 0 | classes | classes by k | best [[n,k,d]] (classes) | programs (agree / consistent) |
| --- | --- | --- | --- | --- | --- | --- |
| 3x3 | 18 | 17 | 4 | 4:3 8:1 | [[18,4,4]] | 2 (2 / 0) |
| 3x5 | 30 | 4 | 1 | 8:1 | [[30,8,2]] | 1 (1 / 0) |
| 3x6 | 36 | 136 | 17 | 4:11 8:5 16:1 | [[36,4,6]] | 2 (2 / 0) |
| 3x7 | 42 | 6 | 1 | 12:1 | [[42,12,2]] | 1 (1 / 0) |
| 3x9 | 54 | 476 | 22 | 4:15 8:2 12:4 24:1 | [[54,8,6]] | 3 (3 / 0) |
| 3x10 | 60 | 32 | 6 | 8:5 16:1 | [[60,8,4]] (3) | 4 (4 / 0) |
| 5x6 | 60 | 32 | 4 | 8:3 16:1 | [[60,8,4]] (2) | 3 (3 / 0) |
| 3x12 | 72 | 1,088 | 72 | 4:48 8:18 16:5 32:1 | [[72,8,8]] | 5 (5 / 0) |
| 6x6 | 72 | 1,088 | 47 | 4:18 8:21 12:1 16:6 32:1 | [[72,12,6]] | 4 (4 / 0) |
| 3x14 | 84 | 48 | 4 | 12:3 24:1 | [[84,12,4]] (2) | 3 (3 / 0) |
| 6x7 | 84 | 48 | 4 | 12:3 24:1 | [[84,12,4]] (2) | 3 (3 / 0) |
| 3x15 | 90 | 2,389 | 68 | 4:51 8:10 12:1 16:1 20:3 24:1 40:1 | [[90,8,10]] | 5 (5 / 0) |
| 5x9 | 90 | 112 | 4 | 8:3 24:1 | [[90,8,6]] (3) | 4 (4 / 0) |
| 7x7 | 98 | 4,788 | 15 | 6:11 12:3 18:1 | [[98,6,12]] | 2 (2 / 0) |
| 3x18 | 108 | 3,808 | 164 | 4:107 8:27 12:20 16:2 24:7 48:1 | [[108,8,10]] (2) | 11 (11 / 0) |
| 6x9 | 108 | 3,808 | 188 | 4:135 8:27 12:16 16:2 24:7 48:1 | [[108,8,10]] (2) | 12 (12 / 0) |
| 3x20 | 120 | 256 | 24 | 8:18 16:5 32:1 | [[120,8,8]] (10) | 11 (11 / 0) |
| 5x12 | 120 | 256 | 14 | 8:10 16:3 32:1 | [[120,8,8]] (7) | 8 (8 / 0) |
| 6x10 | 120 | 256 | 15 | 8:7 16:7 32:1 | [[120,16,6]] | 2 (2 / 0) |
| 7x9 | 126 | 222 | 4 | 12:3 36:1 | [[126,12,6]] | 2 (2 / 0) |
| 3x24 | 144 | 8,704 | 299 | 4:202 8:73 16:18 32:5 64:1 | [[144,8,12]] (4) | 19 (19 / 0) |
| 6x12 | 144 | 8,704 | 331 | 4:139 8:133 12:3 16:46 24:1 32:8 64:1 | [[144,12,12]] | 18 (18 / 0) |
| 3x25 | 150 | 504 | 14 | 8:13 40:1 | [[150,8,10]] (10) | 11 (11 / 0) |
| 5x15 | 150 | 3,236 | 36 | 8:33 16:2 40:1 | [[150,8,12]] (3) | 5 (5 / 0) |
| 3x27 | 162 | 12,869 | 179 | 4:140 8:14 12:18 24:2 36:4 72:1 | [[162,8,14]] (2) | 11 (11 / 0) |
| 9x9 | 162 | 13,760 | 68 | 4:44 8:3 12:15 24:2 36:3 72:1 | [[162,8,12]] | 5 (5 / 0) |
| 3x28 | 168 | 384 | 14 | 12:10 24:3 48:1 | [[168,12,8]] (5) | 6 (6 / 0) |
| 6x14 | 168 | 384 | 10 | 12:4 24:5 48:1 | [[168,12,6]] (2) | 3 (3 / 0) |
| 7x12 | 168 | 384 | 13 | 12:9 24:3 48:1 | [[168,12,8]] (5) | 6 (6 / 0) |
| 3x30 | 180 | 19,112 | 529 | 4:361 8:121 12:7 16:15 20:11 24:6 32:1 40:5 48:1 80:1 | [[180,16,10]] | 28 (26 / 2) |
| 5x18 | 180 | 896 | 28 | 8:21 16:3 24:3 48:1 | [[180,8,12]] (14) | 15 (15 / 0) |
| 6x15 | 180 | 19,112 | 680 | 4:505 8:132 12:5 16:15 20:11 24:4 32:1 40:5 48:1 80:1 | [[180,8,16]] | 35 (30 / 5) |
| 9x10 | 180 | 896 | 42 | 8:33 16:3 24:5 48:1 | [[180,8,12]] (22) | 23 (23 / 0) |
| 7x14 | 196 | 38,304 | 156 | 6:121 12:29 18:2 24:3 36:1 | [[196,6,18]] | 9 (7 / 2) |
| 3x33 | 198 | 22,627 | 253 | 4:225 8:24 44:3 88:1 | [[198,8,16]] (2) | 15 (11 / 4) |

**The 81 tori with no code of k > 0.**
- **66 have l or m a power of 2**, which forces k = 0 by `census.py`'s lemma:
  - 36 with l = 2: 2x2 to 2x27, 2x30, 2x31, 2x37, 2x40, 2x42, 2x44, 2x45, 2x46, 2x49 and 2x50;
  - 3x4, 3x8, 3x16;
  - 4x4 to 4x13, 4x15, 4x16, 4x17, 4x20 to 4x25;
  - 5x8, 5x16, 6x8, 7x8, 8x8, 8x9, 8x10, 8x12.
- **The other 15 are 3x11, 3x13, 3x17, 3x19, 3x23, 5x5, 5x7, 5x10, 5x11, 5x13, 5x17, 7x11,
  7x13, 9x11 and 10x10.** The criterion below explains them.

### Against other sources

The literature could not be read in full. arXiv, ar5iv, quantum-journal.org and Semantic Scholar
were unreachable from this environment: DNS failed, and the proxy refused the connection. A web
search tool worked, but it returns summaries written by a model, not page text.

Three public GitHub sources were read directly:
- **(C)** Lin and Pryadko's catalog of abelian two-block group-algebra codes (QEC-pages/2BGA-codes,
  `abelian.zip`). It lists connected codes on abelian groups of order ≤ 50, so n ≤ 100.
- **(T)** the LaTeX source of arXiv:2606.02418 (qiskit-community/qcode-discovery).
- **(L)** the per-code records of a community leaderboard (unitaryfoundation/qldpc-challenge).
  Its distances are mostly upper bounds, and its provenance is as the submitters state it.

**Codes equivalent to a census class.** Some sources give a code's polynomials on a plain torus
that stage 1 covers. For five of them, the census's equivalence key was computed while drafting
this report, on stage-1 tori only. Equal keys mean the same code up to a permutation of the
qubits.

| Source code | Source | Census class |
| --- | --- | --- |
| [[180,8,16]] | (L): "Bivariate bicycle on Z_6 x Z_15, A={x^3, y, y^2}, B={y^6, x^4, x^5}. From arXiv:2408.10001v6 (Wang & Mueller, 2026)" | 6x15#142, the best at n = 180 |
| [[98,6,12]] | (L): Liang et al.'s twisted-torus code (arXiv:2503.03827), f = 1 + x + x^-1 y^2, g = 1 + y + x^-2 y^-1, whose twist gives the plain 7 x 7 torus | 7x7#14, the best at n = 98 |
| [[18,4,4]] | (L): Liang et al., f = 1 + x + xy, g = 1 + y + xy on 3 x 3 | 3x3#3, the best at n = 18 |
| [[144,24,6]] | (T): (l, m) = (12, 6), A = x^6 + y + y^2, B = y^3 + x^2 + x^4, with x and y exchanged | 6x12#9, on the Pareto front |
| [[150,16,8]] | (L): Z_5 x Z_15, A = 1 + y^6 + y^8, B = y^5 + x + x^4, citing Wang and Mueller's Table 1 | 5x15#1 |

These matches rest on the sources' transcriptions of the polynomials, and on x having the first
factor's order. The (L) record of [[180,8,16]] gives d only as an upper bound. The census gives
d = 16 exactly, by the search and the second search.

**The same [[n,k,d]], not tested for equivalence.**
- **The same group.** (C) has a code with the census best's [[n,k,d]] on the same group at n = 18,
  36, 42, 54, 72, 84 and 98: [[18,4,4]], [[36,4,6]], [[42,12,2]], [[54,8,6]], [[72,8,8]],
  [[84,12,4]] and [[98,6,12]]. It also has the Pareto codes [[36,8,4]] and [[54,4,8]].
  - (L)'s [[72,8,8]] record states that its code is isomorphic to (C)'s SmallGroup(36,8) code.
- **The same best score.** At n = 18, 36, 54, 72, 90 and 98, the census's best k d²/n equals the
  best in (C) over all abelian groups of order n/2. These are weight-6 codes with three terms in
  each polynomial.
- **Search summaries only.**
  - [[162,8,14]]: Symons, Rajput and Browne's table of k = 8 codes (arXiv:2511.13560). An (L)
    record also gives Liang et al.'s twisted-torus code with these parameters, on a group of order
    81.
  - [[108,16,6]] and [[162,24,6]]: Eberhardt et al., through a sentence of Wang and Mueller that
    the search tool quoted.
  - [[54,8,6]]: Wang and Mueller. The summaries disagree about this one.

**Where this form is weak.** Restricted to connected classes, the census's best d for each
(group, k) equals (C)'s in 20 of 24 pairs and never exceeds it.
- **(C) is higher in 4 pairs:**
  - C15, k = 8: 4 against 2;
  - C30, k = 8: 6 against 4;
  - C45, k = 8: 8 against 6;
  - C3 x C15, k = 12: 6 against 2.
- **At n = 30, 42, 60 and 84, the census's best is far below weight-6 codes on the same group.**
  These are [[30,4,6]] and [[42,6,6]], both in codes.json, and [[60,8,6]] and [[84,6,10]], in (C),
  which (L) attributes to Liang et al.
- **k values missing from (C).** Every census k that (C) does not list belongs only to
  disconnected classes, which (C) excludes.

Two caveats apply to this comparison. Groups were matched to tori by GAP SmallGroup ids recalled
from GAP's library, not computed. The catalog's method for certifying distances was not checked.

**Not found in the sources reached.**
- **Frontier bests:** [[30,8,2]], [[60,8,4]], [[120,16,6]], [[126,12,6]], [[150,8,12]],
  [[168,12,8]], [[196,6,18]] and [[198,8,16]].
- **Pareto codes:** [[144,4,14]], [[162,4,16]], [[180,4,18]] and [[196,18,8]].

This is absence in partial sources, not a claim of novelty.

**Several of these are dominated** by weight-6 codes of other forms on (L):
- [[182,6,18]] dominates [[196,6,18]], and [[120,8,12]] dominates [[150,8,12]]; both of those are
  upper bounds on (L);
- [[168,12,10]] and [[168,10,14]] dominate [[168,12,8]];
- [[96,16,6]] dominates [[120,16,6]].

## Structure

The k results rest on the local-term formula behind `census.py`'s lemma: k = 2 Σ dim L/(A_χ, B_χ)
over the characters χ = (α, β) of the torus's odd part (bb.local_terms).

Below, "proved" means argued by hand in the analysis. None of it is formalised in Lean, and every
proved statement was also checked on all the stage-1 data.

Notation:
- l', m' are the odd parts of l and m, 2^s and 2^t their 2-parts, and N = lcm(l', m');
- a character's **type** is (ord α, ord β);
- a character is **admissible** if it passes criterion 1's test below with its own orders in place
  of l' and m', that is, if it can be a common zero of some code of the form.

### Proved, and checked on all data

**1. Which tori have codes.** The family has a code with k > 0 on l x m if and only if:
- l' > 1 and m' > 1; and
- μ_m' has some ζ ≠ 1 with 1 + ζ in μ_N, and μ_l' has some ξ ≠ 1 with 1 + ξ in μ_N.

Equivalently, gcd(x^l' + 1, (x + 1)^N + 1) and gcd(x^m' + 1, (x + 1)^N + 1) are both nontrivial
over GF(2).
- **Why.** A term is nonzero only if both residues vanish, since L is local. A(α, β) = 0 means
  1 + ζ = α^a β^(−b) with ζ = β^(c−b) ≠ 1, and B is the same with α and β exchanged. The
  conditions only weaken as α and β get larger orders, so take them of orders l' and m', which
  generate μ_N. Conversely, such ζ and ξ give exponents a, ..., f, with b ≠ c and e ≠ f, at which
  both residues vanish, so k ≥ 2.
- **The power-of-2 lemma** is the case l' = 1 or m' = 1.
- **On the 116 tori, the criterion holds on exactly the 35 with classes** (0 mismatches). It
  explains the 15 empty tori that the lemma misses.

The order of 1 + ζ, for ζ of order q, decides the cases:

| q | 3 | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 23 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ord(1 + ζ) | 3 | 15 | 7 | 63 | 341 | 819 | 5 or 15 | 85 or 255 | 9709 | 2047 |

- **A side whose odd part is divisible by 3 or 7 always passes.** μ_3 and μ_7 are all of GF(4)*
  and GF(8)*, so 1 + ζ stays in them.
- **A side with odd part 5 needs 15 | N.** That rules out 5x5, 5x10, 10x10, 5x7, 5x11, 5x13 and
  5x17.
- **The other empty tori:**
  - 11 needs 341 = 11·31 to divide N, so 3x11, 7x11 and 9x11 are empty;
  - 13 needs 819 = 9·7·13, so 3x13 and 7x13;
  - 17 needs 85 or 255, both multiples of 5·17, so 3x17;
  - 19 needs 9709 = 7·19·73, so 3x19;
  - 23 needs 2047 = 23·89, so 3x23.

**2. The maximum k is set by the odd torus:** max k(l x m) = 2^(s+t) · max k(l' x m').
- **The upper bound.** Each term is at most dim L = 2^(s+t).
- **The lower bound.** Lifting the best odd code by x → x^(2^s), y → y^(2^t) gives 2^(s+t)
  disjoint copies of it.
- **Data.** It holds on all 35 tori.

**3. k ≤ 8lm/9 for every code of the family.** When 3 | l and 3 | m, the bound is reached by
lifting 3x3's A = 1 + y + y^2, B = 1 + x + x^2, which has d = 2. On stage 1, max k = 8lm/9
exactly on the 15 tori with 3 | l and 3 | m, and is below it on the other 20.

**4. Tori with exactly one even side.** Say l is odd and m = 2^t m'.
- **Every common zero has the same term**, 2^τ with τ = min(v2(b), v2(c), v2(d), t). The case
  with only l even is symmetric.
- **A term above 1** means b, c and d are all even, so the class is a disjoint union of copies of
  a smaller code.
- **The k values of such a torus** are therefore those of l' x m', each times 2^j for
  j = 0, ..., s + t.
- **Data.** The term formula holds on all 2,927 classes of odd or one-sided tori. A term above 1
  comes with a disconnected code in 318 of 318 cases. The k-set statement holds on 18 of 18
  one-sided tori.
- **Tori with both sides even.** Terms vary there; the gross code's are 1, 1, 2, 2. k values
  beyond the lifted set occur only at 12 on 6x6, and at 12 and 24 on 6x12. There are none on 6x10
  or 6x14.

**5. The minimum k.** k is at least twice the smallest Frobenius orbit among the admissible
characters, since the term is constant and at least 1 on a whole orbit of common zeros. Equality
holds on 35 of 35 tori, which is a pattern, not a proof. The minimum is:
- 4 when 3 divides both l' and m' (type (3,3), an orbit of size 2);
- otherwise 8 where the smallest type is (3,5) or (5,3), 12 where it is (3,7) or (7,3), and 6
  for (7,7).

**6. d is even for every code of the family.** A and B have odd weight, so the all-ones vector is
in the row space of H_X. All 3,330 recorded distances are even.

**7. When d = 2.** d = 2 if either of these holds:
- (i) B is a translate of A; or
- (ii) a nonzero translation g fixes A or B, and χ(g) ≠ 1 at some common zero χ.

The "if" direction is proved. The "only if" direction is checked, not proved: 263 classes satisfy
(ii) and 51 satisfy only (i), all 314 have d = 2, and all 3,016 that satisfy neither have d > 2.

**8. A quotient logical.** Take a subgroup H of odd order. Suppose that on G/H the image of B is
fixed by a translation ḡ, and some common zero χ is trivial on H with χ(g) ≠ 1. The same works with
A, or with B̄ a translate of Ā. Then a Z-logical of weight 2|H| exists, so d ≤ 2|H|.
- 2,482 classes have such a bound.
- No class violates it, and 873 attain it.

These counts compare the analysis' stored bounds with the data.

**9. A forced form.** On l = 3, a common zero of type (3, q) with 3 ∤ q forces B = y^d + x + x^2
with q | d. So d ≤ 2m/q whenever m/q is odd. On l = 5 or 7, a zero of type (l, 3) forces A's
y-exponents to {1, 2} mod 3, so d ≤ 2m/3 when m/3 is odd.
- **The explicit vector of weight 2m/q is a logical** in 33 of 33 classes with odd m/q.
- **With even m/q** it is a logical in 82 of 113 classes. Even so, no class of these types
  exceeds 2m/q there.

**10. Lifts keep the score.** x → x^c carries a code on l x m to c disjoint copies on cl x m, with
the same k d²/n. So the best score never decreases from a torus to a multiple of it. This holds
for every pair of the 35 tori.

### Patterns in the data (not proved)

**A linear distance law.** The maximum d over classes with a zero of type (3, q) on 3 x m, or of
type (5,3) or (7,3) on 5 x m or 7 x m, equals 2m/q in 16 of 17 stage-1 instances. The classes at
the maximum have k = 8 for types (3,5) and (5,3), and k = 12 for (3,7) and (7,3).

| Torus | Type | Classes | Max d | 2m/q |
| --- | --- | --- | --- | --- |
| 3x5, 3x10, 3x15, 3x20, 3x25, 3x30 | (3,5) | 1, 6, 1, 24, 13, 10 | 2, 4, **2**, 8, 10, 12 | 2, 4, **6**, 8, 10, 12 |
| 3x7, 3x14, 3x28 | (3,7) | 1, 4, 14 | 2, 4, 8 | 2, 4, 8 |
| 3x25 | (3,25) | 1 | 2 | 2 |
| 5x6, 5x9, 5x12, 5x15, 5x18 | (5,3) | 4, 3, 14, 11, 24 | 4, 6, 8, 10, 12 | 4, 6, 8, 10, 12 |
| 7x9, 7x12 | (7,3) | 2, 13 | 6, 8 | 6, 8 |

- **The miss is 3x15, and it is a matter of reading.** Judged by class representatives, it has a
  single (3,5) class, with k = 24 and d = 2. But on tori where gcd(l, m) > 1 the torus's
  automorphisms mix the factors, so whether a class has a zero of a given type can depend on
  which of its codes is asked. On 3x15, classes 10 and 16 (k = 8, d = 6 = 2m/q) contain codes with
  a (3,5) zero although their representatives have only (3,15) zeros. Judged by any code of the
  class, 3x15 meets the law too (found while building stage 2; the registered stage 2 keeps the
  representative reading).
- **In the larger instances, most of the k = 8 classes reach the bound:** 10 of 13 on 3x25, 14 of
  21 on 5x18, 10 of 18 on 3x20.
- **The largest m/q tested is 6.**
- **A caution from a similar series.** The k = 8 classes on 3 x m whose zeros are the order-3
  characters have a similar bound, 2m/3. Their best d meets it only up to m = 15: it is 10, 12, 14,
  14 and 16 at m = 18, 24, 27, 30 and 33.

**The best codes reduce to one small code.** Consider the 13 tori with 3 | l, 3 | m and lm ≥ 27:
3x9, 3x12, 3x15, 3x18, 3x24, 3x27, 3x30, 3x33, 6x6, 6x9, 6x12, 6x15 and 9x9.
- **Every class at a torus's best k d²/n reduces mod (3, 3) to the [[18,8,2]] code** A = 1 + y + y^2,
  B = 1 + x + x^2, 3x3's class 0. That is 20 of 20 classes, among them the gross code and the bests
  at n = 72, 90, 108, 162, 180 and 198.
- **On 3x3 and 3x6 it does not hold**, because the best there has k = 4.
- **Such classes are a minority of each torus**, for example 60 of 680 on 6x15. All of them have
  k ≥ 8, because the four characters with α and β of order 3 lift.
- **In covering language** (which is where the literature puts it, below): such a code's Tanner
  graph covers the base code's.
- **How it was checked.** The reduction of A is a coset of a line of F_3², and so is B's, on a
  different line. This test was written for this report. The frontier analysis' test used
  `equivalence_key` on 3x3, and the two give the same counts.
- **The literature.** This fits a search summary of Symons, Rajput and Browne (arXiv:2511.13560),
  who build k = 8 codes as covers of the base [[18,8,2]] code. The paper was not read.

**What the best codes look like.**
- **k sits on one or two Frobenius orbits of the smallest size.** Two orbits of order-3 characters
  give k = 8 at n = 54, 72, 90, 108, 162, 180 and 198; the gross code has terms 1 and 2 on them. One
  (7,7) orbit gives k = 6 at n = 98 and 196. One (5,15) orbit gives k = 8 at n = 150. One (3,7) or
  (7,3) orbit gives k = 12 at n = 126 and 168.
- **Where a torus with 3 | l and 3 | m has codes at some n, the best at n is on such a torus.**
  This holds at all 10 such n. Only n = 90 and 180 also have codes on other tori.
- **The best class is connected on 34 of 35 tori.** The exception is 3x30, whose best is two
  copies of [[90,8,10]], with the same score.
- **Symmetry is a weak signal** and is not used here.

## Candidate predictions for stage 2 (not registered)

These are candidates for the registered test on the held-out tori. None has been evaluated on any
held-out torus.
- **Values per torus.** Most of them give each torus's value from l and m alone, or from a stage-1
  look-up, and the registration can write those values down before anything is computed. This
  report does not list them.
- **One analysis did evaluate the criterion and the k formulas on the held-out sizes.** That was
  arithmetic on l and m only, with no code, k or d computed on any held-out torus. Those values are
  kept out of this report so that the registration can decide how to state them.

| # | Candidate, for each held-out torus l x m (either orientation) | Basis | Kind |
| --- | --- | --- | --- |
| S1 | Some raw code has k > 0 if and only if criterion 1 holds | proved; 116 of 116 | tests census.c and the proof |
| S2 | max k = 2^(s+t) · max k(l' x m'), at most 8lm/9, and equal to it when 3 \| l and 3 \| m | proved; 35 of 35 | a look-up wherever l' x m' is a stage-1 torus |
| S3 | min k = twice the smallest Frobenius orbit of admissible characters | lower bound proved; equality 35 of 35 | |
| S4 | With exactly one side even, the k values are those of l' x m', each times 2^j for j = 0, ..., s + t | proved; 18 of 18 | |
| S5 | d = 2 exactly when (i) or (ii) of result 7 holds | "if" proved; "only if" 3,330 of 3,330 | needs only whether d = 2, which is cheap |
| S6 | The proved bounds hold: d even, the quotient bound, d ≤ 2m/q for odd m/q | proved | tests the instruments |
| S7 | **Risky:** the linear law, max d = 2m/q over classes of each forced type | upper bound proved for odd m/q; equality 16 of 17 | quantitative; extrapolates from m/q ≤ 6 |
| S8 | With 3 \| l, 3 \| m and lm ≥ 27, every class at the torus's best k d²/n reduces mod (3, 3) to the [[18,8,2]] base | 20 of 20 on 13 tori | pattern; needs every d on those tori |
| S9 | At each n where a torus with 3 \| l and 3 \| m has codes, the best k d²/n is on such a torus | 10 of 10 n, 2 of them contested | pattern; needs every d at those n |
| S10 | Optional: the published [[288,12,18]] ranks first by k d²/n at n = 288 | 3 of 4 published codes rank first in stage 1 | costly; exposed (below) |

**What the registration has to fix.**
- **The thresholds.** For S7, the list of instances, which follows from l, m and the orders of the
  characters, and how many must hold exactly.
- **The instrument behind each d.** At d ≥ 16, only search.c finishes. So a registered distance
  should name the search from (0, lm), the search from every qubit in both kinds, and the program
  under SCIP_FIX where it is optimal.
- **The cost.** S1 to S4 need only k, which takes seconds for a torus. S5 needs only to decide
  whether d = 2. S6 to S10 need distances, and S8 to S10 need d for every class on the tori
  concerned. At n = 180 to 198 the census's k = 4 classes already reach d = 18, and only search.c
  finished there, so larger tori may exceed the search's budget.

**Exposure the registration should record.** Nothing was computed on a held-out or refused torus.
But some sources read during the analysis or while drafting this report concern held-out tori:
- **The published [[288,12,18]]** on 12 x 12 (codes.json), whose d was computed in
  [code-distances.md](code-distances.md).
- **(T)'s main table** gives codes of this family's form on 12 x 12, with their polynomials and
  distances. It was read in the frontier analysis and again while drafting this report. It has
  a weight-8 code on 8 x 18, and (T)'s catalog files list codes on 6 x 24 and 9 x 16. All of these
  tori are in `exposed_extrapolation`. The values are not repeated here.
- **(L) has one record each on groups isomorphic to the held-out random tori 2 x 48 and 3 x 29.**
  (L)'s list of weight-6 [[n,k,d]] up to n = 200 also includes the n of held-out tori.

## Stage 2: the registered test

**What was registered** (`examples/qec-census-2/ledger.jsonl`, committed and pushed before any
computation on a held-out torus).
- **The predictions** were computed only from l, m and stage-1 data, as candidates S1 to S9 above
  (H1 to H9).
- **The tori:** all 122 held-out ones.
- **Exposure.** Exposed tori (earlier development, or a source read during stage 1) were computed
  but judged apart, and tori isomorphic to an exposed one were also reported in a "strict"
  version.
- **Thresholds.** They were fixed in advance, H7's among them: it fails if any instance is above
  its value, and holds if at least 80% of the resolved instances are exactly equal.

**A tool fault, and the continuation.** The registered run ended "incomplete".
- **What went wrong.** census.c held lm ≤ 128 (stage 1 needed only 100), so the 54 jobs on tori
  with lm ≥ 129 failed before computing anything. Neither the builder nor the reviewer caught the
  limit.
- **That verdict stands.** Stage 2's registered verdict remains "incomplete".
- **The fix.** census.c's capacity was raised to 160, a change to capacity only: the old and new
  binaries give identical k on all 5,472,121 stage-1 raw codes.
- **The continuation.** `examples/qec-census-2b` re-registered stage 2's own predictions,
  verbatim, for exactly the failed jobs, before running them. Its verdict is **hold**.
- **The combined judgement.** It judges each part by stage 2's registered rules, over stage 2's
  successful records and the continuation's.

| Part | Prediction | Result (combined, judged tori) |
| --- | --- | --- |
| H1 | which tori have a code with k > 0 (criterion 1) | **holds** on all 97 judged tori, and on the exposed ones; 29 held-out tori have codes |
| H2 | max k (proved formula, or the bound where the value was open) | **holds**, 18 of 18 |
| H3 | min k = twice the smallest admissible orbit | **holds**, 18 of 18 |
| H4 | k-sets of tori with one even side | **holds**, 9 of 9 |
| H5 | d = 2 exactly when (i) or (ii) of result 7 holds | **holds**: 11,915 classes on 29 tori, 518 with d = 2, no mismatch |
| H6 | the proved bounds (d even, the quotient and forced bounds), every witness checked, intervals meeting across instruments | **holds** on every torus with codes, exposed ones included |
| H7 | the linear law, max d = 2m/q over classes of each forced type | **holds: 19 of 19 instances exactly equal**, among them d = 20 on 3 x 50 and 5 x 30 (n = 300) and d = 18 on 3 x 45 |
| H8 | the best classes reduce mod (3,3) to the [[18,8,2]] base (tori with n ≤ 252) | **not established**: holds on 3 x 21, 3 x 36 and 3 x 39; unresolved on 3 x 42 (judged); and on the exposed 6 x 18 it **fails** |
| H9 | the best k d²/n at each n is on a torus with 3 \| l, 3 \| m (n ≤ 252) | **holds** at all 4 sizes |

**H8 fails on 6 x 18.** All seven classes at the best k d²/n there, [[216,8,16]] with
k d² = 2,048, fail to reduce to the base. 6 x 18 is exposed: development had computed some codes
there. Exposure bears on whether the test was blind, not on the mathematics, so the pattern is
false as a general rule. The best codes on 3 x m in stage 1 and stage 2 do reduce to the base.
On 3 x 42, 6 x 21 and 9 x 12 the ranking stopped at its limits, with the best not yet pinned
down.

**What stage 2 establishes.**
- **Proved results confirmed.** Criterion 1 and the k formulas held on new tori up to n = 300.
- **The d = 2 rule.** Its unproved half held on 11,915 more classes.
- **The linear law.** It held exactly at every instance, extrapolated from m/q ≤ 6 in stage 1 to
  m/q = 10. It now stands as a well-tested conjecture, not a theorem.
- **The mod-3 pattern.** It is not a law of the family.
- **The instruments.** H6 held on every torus.

The new best codes found on held-out tori include [[216,8,16]], [[234,8,16]], [[252,8,18]] and
[[300,8,20]] (k d²/n 9.48, 8.75, 10.29 and 10.67). For the larger of these, d ≥ 16 rests on the
deepening search, as in stage 1.

## What this does not establish

- **One family, one form.** Other weight-6 forms do better at several n: at n = 30, 42, 60 and 84
  by a wide margin. The census says nothing about them.
  - Examples of such forms are coprime codes, mixed monomials, twisted tori and general two-block
    group-algebra codes.
- **Only n ≤ 200, on 116 tori.** The 22 held-out random tori, the 100 at 100 < lm ≤ 150 and the 8
  refused tori are untouched.
- **Classes are an upper bound on inequivalent codes.** A tie of several classes may still be one
  code. For example, the published [[108,8,10]] shares rank 1 with one other class.
- **d is exact by these instruments, not certified independently.**
  - Every d comes from a completed search with a verified witness.
  - The program agrees wherever it finished, which is every class with d ≤ 14 it ran on.
  - For 190 frontier classes, including the bests at n = 180, 196 and 198, the lower bound rests
    on search.c alone.
  - The search's lower bounds rest on its argument and its code. Two registered tests checked them
    against other methods ([code-distances.md](code-distances.md)), but nothing certifies them
    independently.
- **The sources are partial.** The main papers' tables were not read. "Not found" means not found
  in the sources reached. Same [[n,k,d]] does not mean the same code, and equivalence was tested
  only for the 5 codes listed above.
- **The proofs are by hand.** The criterion, the k formulas and the distance bounds were argued in
  the analysis and checked on stage-1 data. They are not formalised.
- **Distance is not performance.** Nothing here bears on logical error rates under circuit noise,
  on decoders, or on logical gates.

## Next

1. **Register stage 2.** Choose among S1 to S10, write the per-torus values and thresholds from l
   and m before anything is computed, name the instrument behind each d, and record the exposure
   above.
2. **An independent lower bound at d ≥ 16.** The program does not finish there within 600 s, and
   190 frontier classes rest on search.c alone.
3. **Widen the family** to the weight-6 forms that beat this one at n = 30, 42, 60 and 84, with the
   same classes, instruments and hold-out.
4. **Formalise** criterion 1 and the k formulas, building on the Lean bridge from polynomials to
   eigenvalues.
5. **Read the literature properly** when arXiv is reachable, and test the frontier codes for
   equivalence against published polynomials.

## Reproducing

    uv run --no-sync python examples/qec-census/census.py run          (--workers N; resumes)
    uv run --no-sync python examples/qec-census/census.py summary
    uv run --no-sync python examples/qec-census/census.py classes L M   (k and classes only)

`summary.json` holds the frontier, the cross-checks and the published placements. `data/LxM.jsonl`
holds one header per torus, then one row per class: its representative, size, k, characters and
Frobenius orbits, stabiliser, and both instruments' results with their witnesses. The structure
and literature analyses and the recheck were run from scratch scripts outside the repository.
Their checks read only `data/`, `summary.json` and `holdout.json`'s lists. The equivalence tests in
the literature section computed keys on stage-1 tori only.
