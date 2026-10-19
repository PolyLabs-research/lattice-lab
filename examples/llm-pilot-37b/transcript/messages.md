# The agent's messages, verbatim

Every text block of the agent's session, in order, read from its server-side transcript.

## 2026-10-19T21:54:04.898002Z

I've read the card and the two prior proposals, and am now setting up computations in (a,b)=(t_j,t_k) coordinates to study the 16 rules at 37.

## 2026-10-19T22:02:30.050096Z

Working on the 7 targets that don't factor as unit × cube in (a,b). Next: full factorisation as Laurent polynomials in x, y (which may reveal non‑symmetric or rotated factors).

## 2026-10-19T22:12:12.901367Z

The new condition explains 9 of the 16 targets at 37, including all 3 that are also confined at 61. Now running soundness sweeps against direct eigenvalue computation.

## 2026-10-19T22:19:43.428212Z

Still verifying soundness (the atlas sweep is at m≈200 with no false claims). Next I'll look at how the Lean library structures its `period_*_dvd` proofs, so I can formalise the target rules.

## 2026-10-19T22:29:43.653472Z

Still waiting on mathlib (about 94%) and the re-sweeps. I'm drafting `proposal.md` now.

## 2026-10-19T22:32:00.277456Z

Another search for the remaining seven also came up empty: f·U·g³ landing in F(2⁹) or F(2⁶), for any family g and small units U. Now waiting on the mathlib build to compile the Lean proofs.

## 2026-10-19T22:32:36.009452Z

Python side is done and consistent. Waiting on the Lean build (mathlib about 95%), then I'll compile `Pilot.lean`.

## 2026-10-19T22:53:28.911715Z

Mathlib and the library are built. Now compiling `Pilot.lean`.

## 2026-10-19T22:55:15.953661Z

All 12 Lean theorems (9 at 37, 3 at 61) build and depend only on propext, Classical.choice and Quot.sound. Tidying up and committing.

## 2026-10-19T22:56:33.003258Z

`proposal.py` passes 32 of 32 checks and the family re-sweep is clean so far. Writing `report.md` now.

## 2026-10-19T22:57:29.773262Z

Every sweep is clean. Committing and pushing everything, with `report.md` going in last.

## 2026-10-19T22:57:58.017172Z

# Report: the sixteen cube-confined rules at m = 37

Nine of the sixteen are explained, including all three that are also confined at 61. The rule and its proof are in `mechanism.py` and `proposal.md`, and the twelve confinements are proved in Lean. The other seven are unexplained, but they are about what chance predicts once the census's chance model is corrected.

Everything is pushed to `pilot-37b-submission`, the branch named in the git instructions. The checkout started on `pilot-sandbox-37b`, and I created the submission branch from it. If the judge watches the sandbox branch instead, the work needs to be pushed there too.

## What I found

**Nine targets are a unit times a cube, as an exact identity over GF(2).** Write a = x + 1/x and b = y + 1/y (rule 90 along the axes). The nine rules are:

| | (a+b+1)³ | (ab+1)³ | (ab+a+b)³ |
|---|---|---|---|
| a + b | 1112 | 10498 | 13584 |
| ab | 2436 | 17056 | 28944 |
| (a+1)(b+1) | 3461 | 26883 | 18246 |

These are all nine possible products of this shape; the family's degree bound allows no others. The cube factor needs no reason to be a cube. The first factor (the "unit") is a cube for these reasons:
- **a + b and ab** are products of rule‑90 eigenvalues, and those are cubes at 37.
- **(a+1)(b+1)** satisfies Ψ₃(t)² = t₃ⱼ/tⱼ, a ratio of rule‑90 values.
  - At 37 that is a cube because rule 90 is confined there.
  - At 61, 3 = 2⁶ (mod 61), so it equals t⁶³, a cube, even though rule 90 is not confined at 61.
  - That is why exactly the bottom row (3461, 26883, 18246) is also confined at 61.

**The general mechanism, proved in `proposal.md` §3.** Suppose f = xᵛ · ∏ Φₑ(X_w)^k · h^q exactly over GF(2), where X_w is a lattice monomial and h is any polynomial. Suppose also that each unit factor Φₑ(X_w) whose exponent k is not a multiple of q takes q‑th‑power values at m. That holds either through rule 90's own confinement, or when every divisor e′ of e is ≡ ±2^a (mod m) and q divides the resulting exponent. Then every nonzero eigenvalue of f is a q‑th power. Splitting (no h) and powers (no units) are special cases; the mixture is new.

**The other seven** are 4850, 5972, 13822, 22064, 25183, 27390 and 28586. The census model gives every free class a 1/3 chance of being a cube, and at 37 that is wrong for two of the ten classes:
- The axis and diagonal classes are cubes for **93.5%** of the family. On the axis a rule's eigenvalue is H(tⱼ) with H of degree at most 4. Of the 31 possible H, only the two quartic halves of Ψ₁₇ are not products of whole Ψₑ's, which are cubes at 37. The diagonal behaves the same way.
- Using the measured per-class rates, still treating classes as independent, the expected number of chance confinements at 37 is **5.7** instead of 0.62. Seven remain unexplained, which is consistent with chance.
- The corrected model also matches the counts of rules with 1, 2 and 3 non‑cube classes: 82, 560 and 2,022 observed against 80, 534 and 2,044 predicted.
- Only the all‑cube count is in excess, 42 against 5.2. Of those 42, 35 are explained by mechanisms 1–6 and this one, and the 7 left are within chance.

## Deliverables
- **`mechanism.py`, `condition(f, m)`:**
  - It factors f over GF(2): factors along lattice directions are found from the edges of f's Newton polygon, and it checks whether the remaining two‑dimensional part is an exact q‑th power.
  - It tests each needed unit with the lemma above. The only field computation is rule 90's own confinement, which the earlier pilots also used; no eigenvalue of f is computed.
  - It returns the lcm with the previous pilots' conditions.
  - Timing: 30–40 s for all 1,274 atlas rules at one m (measured at 37 and 299), and 25–40 s for 2,000 family rules at m ≤ 125.
- **`proposal.md`:** the theorem and proof, the corrected chance analysis, what was ruled out, and predictions.
- **`proposal.py`:** 32 checks, all held.
- **`proofs/LatticeProofs/Pilot.lean`:**
  - `period 37 D ∣ 87381` for each of the nine rules, and `period 61 D ∣ 357913941` for 3461, 26883 and 18246. That is, every eigenvalue is a cube of F(2¹⁸), respectively F(2³⁰).
  - `lake build LatticeProofs.Pilot` succeeds. All twelve theorems use only propext, Classical.choice and Quot.sound, with no sorry and no native_decide.
  - The 37 proofs rely on the earlier pilot's `Cubes37.r90_val`; the 61 proofs are self‑contained.

## How I checked it
- **Atlas:** every claim on all 1,274 rules at every odd m from 3 to 301, against eigenvalues computed directly. 1,081 claims, none false.
- **Family:** all 32,767 rules at 39 sizes from 13 to 125, then again at 31 composite sizes up to 143 after my last change to the unit test. No false claim.
- **Where the new kind of claim appears:** in the family, only for exactly these nine rules. The atlas has none; all its claims are splitting or powers.
- **Predictions, verified directly up to m = 151:**
  - All nine rules are confined wherever rule 90 is confined to the cubes: up to 301, that is 37, 95, 101, 111, 141, 197, 203 and 269.
  - The bottom row is also confined at 13, 61, 143, 169, 181, 193, 247, 253, 259 and 299.
  - 13, 95, 101, 111, 141 and 143 are sizes the census has not looked at.

## What I tried that failed for the seven
- **Factorisation:** five are irreducible over GF(2). 13822 and 27390 each split into two factors, but neither factor is a unit.
- **Images under integer matrices** with entries in [−3, 3], put to the same condition: nothing. The same holds for every unexplained census rule at 21, 25 and 29.
- **Twisted products** f · M = C · C(xⁿ, yⁿ): nothing.
- **Cube‑multiplier certificates:** f × unit × g³ landing in F(2⁹) or F(2⁶), with g any family rule. Nothing.
- **Twisted identity:** f(x³, y³) is not divisible by f².
- **Line by line:** proving each class separately from how the rule factors on that line works for the axis, the diagonal and a few other classes. It fails on at least five of the eleven classes for every one of the seven.

## What I'm unsure of
- **That the seven are chance.** The corrected model assumes independent classes and takes its rates from the same population it is tested on.
- **m = 29:** 13 unexplained against 7.85 expected under the corrected model is borderline (p ≈ 0.05), and I found no structure there.
- **Scope of the condition:** it is sufficient, not necessary. It only sees exact factorisations over GF(2), not identities that hold only on the m‑torus.

