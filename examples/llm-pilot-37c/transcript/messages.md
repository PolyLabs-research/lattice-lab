# The agent's messages, verbatim

Every text block of the agent's session, in order, read from its server-side transcript.

## 2026-10-20T14:12:34.253355Z

I'll read the card first and start setup in the background.

## 2026-10-20T14:12:42.727469Z

The card is clear. Now I'll create the designated branch and read the tools, data files, and prior proposals in one pass.

## 2026-10-20T15:26:25.148766Z

At 37 and 161 the budget is met (41 and 29 ms per atlas rule); 299 is still 163 ms. Let me profile 299 once more to see what remains there.

## 2026-10-20T15:30:33.151223Z

Next items, independent of each other: run proposal.py (background), read the regression and sweep logs, and check the Lean build.

## 2026-10-20T16:13:55.843395Z

I have the numbers I need. Now the final steps: write report.md, commit and push, then reply with it.

## 2026-10-20T16:15:03.810551Z

Everything is committed and pushed to `pilot-37c-submission` (`report.md`, `proposal.md`, `mechanism.py`, `proposal.py`, `proofs/LatticeProofs/Pilot.lean`, scratch). Nothing further is pending; the report follows.

# Report: ninth powers at m = 37 (seventh pilot)

## What I found

**Four of the five targets are explained by a mechanism I prove; 4850 is not, and I say precisely what it is not.**

The four radius-5 targets are exact products of cyclotomic line units and the fourth pilot's half-Frobenius cores W = A4+K8+B4+self and V = C4+L8+M8+E4 (a = x+1/x, b = y+1/y, Ψ₅(t) = t²+t+1):

```
699738  = Ψ₅(a) Ψ₅(b) (a + b) W        985232  = a² b² (a + b) W
1431278 = Ψ₅(a) Ψ₅(b) V                1968276 = a² b² V
```

The identities W(x²,y²) t(x)t(y)t(xy)t(x/y) = Sh(7,5) and V(x²,y²) t(x)t(y) = Sh(7,7)+Sh(5,5), whose right sides are permuted by (x,y) ↦ (x⁶,y⁶) at 37, put the cores' values, up to rule-90 factors, in F(2⁹), whose nonzero elements are 27th powers of F(2¹⁸)*. The fourth pilot stopped at cubes because it bounded every unit by rule 90's cube confinement. The new point is **exponent bookkeeping**: every line unit is, as a function on the torus, a power of a rule-90 value with an exact exponent (t_w^k has exponent k; Ψ_e(t_w)² = t^{A_e} with A_e = Σ_{e'|e} μ(e/e') 2^{a(e')}; at 37, A₅ = 2²³ − 1), and the 3-adic valuation of the net exponent per direction, added to rule 90's confinement, gives the power. For 1968276 at the character 2c, λ = t_j³ t_k³ · (element of F(2⁹)); for 1431278, λ(2c) = t_j^{2²³−2} t_k^{2²³−2} · (element of F(2⁹)) and 3 | 2²³ − 2. The claim is q = 9·(2¹⁸+1), not 27, as the census has it.

The mechanism (proposal.md §3): Theorem A, f = (line units)·h^Q with the units' exponents and h's own confinement deciding the prime power; Theorem B, f(x^r,y^r) = U·C with C·N dilation-invariant mod (x^m−1, y^m−1), scored by the exponents of U/N per direction and the line exponents where N vanishes. Both are proved there. `mechanism.py` decides the hypotheses from the GF(2) factorisation and a search for N, computing no eigenvalue of f.

## How I checked it

- `proposal.py`: 42 checks, all passing.
- At 37: 40 of the 42 ninth-power rules of radius ≤ 5 claimed with 9 | q (all but 4850 and 482758 = 4850·(1+a)(1+b)). My own radius-6 census (266 million rules: 23,722 cubes, 83 ninth, 29 of them 27th): 78 of 83 claimed, all verified; the five missed are three unit multiples or rotations of 4850 and two rules with 4850's rotated class pattern.
- Soundness sweeps against direct eigenvalues: atlas, all 1,274 rules at 60 odd sizes (3, 53–191): 694 claims, 0 false. Square family at 51 census sizes 21–125, the 136 census hits plus 300 random radius-6 rules per size: 105 claims, 0 false.
- Timing: about 50 ms per atlas rule at 37, up to 90 ms at m ≈ 300, 60–70 ms per radius-6 rule.
- Lean: `Pilot.lean` states `period 37 D ∣ 29127` for the four radius-5 targets with generated certificates, but **it is unbuilt** (the mathlib build did not finish in the budget) and may contain errors.

## 4850: the precise negative

4850 = s³ + P²s² + P³ + P² + P (s = a+b, P = ab), irreducible; rotated 45° it is (ab)³ + (a+b)⁴(1+a)²(1+b)² + (a+b)², a cube plus a square. At 37 it is not: units × F(2⁹)-valued (symmetric orbit products of radius ≤ 4 or any three directions mod 37, any exponents, even modulo 27th or 19th roots of unity); g³·U·F(2⁹)-valued for any g of radius ≤ 6; a twisted pair or sparse power (lightest symmetric cube root has 440 of 1369 terms, chance level); certified line by line (lines k ≥ 4 have irreducible factors of degree 13–35; the consultation's cyclotomic certificates are vacuous because ⟨1+ζ⟩ ∩ F(2¹⁸)* is exactly the cubes); or order-9 Gauss sums times ninth powers (its eigenvalues have a nontrivial μ₁₉-part). It is not confined at 109 or 185, the other sizes with s = 18.

## What I tried and what failed

A full discrete-log table of F(2¹⁸)* made every multiplicative question linear; it found the radius-5 structure immediately and produced the exclusions. Failed: every multiplicative decomposition of 4850; the cube-plus-square form as a norm from F(2⁵⁴); the 19-cyclotomic model of F(2¹⁸). The regression against the previous pilots' conditions did not finish.

## What I am unsure of

- 4850 and its family: a negative, not a mechanism; with 20982139 and 178279803 there are three unexplained events at radius ≤ 6.
- The Lean file is unbuilt.
- The atlas sweep did not cover sizes 5–51 (only spot checks at 13, 25, 37, 61, 95 passed), and the condition is bounded by its search parameters.
- The chance model was not recalibrated after removing the half-Frobenius family.

