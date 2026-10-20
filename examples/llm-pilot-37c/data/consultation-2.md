# Consultation 2: Claude Fable on rule 4850 (2026-10-20)

Asked through the API, with code execution, at effort xhigh, independently of the other consultation. Its JSON block of identities was checked by machine: every one holds. Verbatim below.

---

Everything in the JSON block at the end has now been machine-checked in the group ring F₂[x,y]/(x³⁷−1, y³⁷−1) (37×37 cyclic-convolution arithmetic, eigenvalues computed in an explicit F(2¹⁸)).

## 1. Verdict

I did **not** find a mechanism. I verified the phenomenon independently, sharpened its statement to something smaller and more testable (nine Galois classes, one of which is special), unified the two "basic facts" the project uses (rule 90 cubes, rule 150 ninth powers) into a single fact about 1+ζ, and then excluded a substantially wider set of candidate mechanisms than the project lists — including the natural group-ring generalisations of mechanisms 4 and 7. What remains is: either a mechanism of a kind none of us has looked for, or a coincidence whose probability I calibrate below at roughly 1 in 3000 (not 1 in 10⁸, but also not "seven rules attributed to chance" territory). I give a registered test that discriminates between those.

## 2. What I verified (computation, F(2¹⁸) built from a primitive degree-18 polynomial, t_j obtained as roots of the degree-18 minimal polynomial Ψ of ζ+ζ⁻¹)

- Rule 4850 = F(t(x), t(y)) with the stated F (identity checked in the group ring, and 4850's bits decode to the stated orbits).
- At m = 37 the lcm of orders of nonzero eigenvalues is 29127 = (2¹⁸−1)/9; exactly one zero eigenvalue (at (0,0)); not all 27th powers. Group-ring form: **R(4850)^29127 = 1 + J·J_y** (J = Σx^k), and R(4850)^9709 ≠ 1 + J·J_y.
- F(a,b) irreducible over GF(2): Kronecker b→a⁹ gives univariate factor degrees [1,1,1,2,33], no recombination divides F. x⁴y⁴f(x,y) irreducible: factor degrees [1,1,1,1,1,1,4,4,4,4,6,6,22,22], all 2¹⁴ recombinations tested, none divides. Both project claims confirmed.
- λ(v)λ(10v)λ(26v) = N_{F(2¹⁸)/F(2⁶)}(λ) has order exactly 7 at all 1368 nonzero characters; λ(6v)/λ(v) = λ^{2⁹−1} has order 57, 19 or 1. Group-ring form: **f·f^{(10)}·f^{(26)} = f^{(8)}·f^{(6)}·f^{(23)}** (dilations; the D-names below). This element B = f^{4161} has 768 terms = 64 of the 114 ⟨8⟩-orbits: unstructured. So, as the project says, the norm formulation is a restatement.

## 3. Proved reductions (small, and worth putting in Lean)

**Class lemma (m = 37, any symmetric rule).** Since 2 generates (Z/37)*, every nonzero character is (j, ±2ⁱj) with j ≠ 0, or on an axis. Because λ(2v) = λ(v)², ninth-power-ness is constant on {(j, ±2ⁱ j)}; the symmetries identify i with −i and i+18, so there are exactly **10 classes i = 0,…,9 plus the axis class**. Class 9 (k = ±6j) is forced: 2⁹ ≡ −6 (mod 37), so Frob⁹ maps (j,6j) to (−6j, j), the rotation image of (j,6j); hence λ ∈ F(2⁹), its order divides 511 = 7·73, and 511 | 9709 = (2¹⁸−1)/27, so class 9 is always a **27th** power. The axis class for 4850 is t_j³, a ninth power iff t_j is a cube. Class 0 is F(t,t) = t²(1+t+t²)². So 4850's confinement is exactly the statement "F(t, t^{2ⁱ}) is a ninth power for i = 0,…,8"; the project's "10 free classes" should be 9 (i = 0 behaves very differently from i = 1..8, see §5).

**One fact behind both basic facts.** For j ≠ 0: t_j = ζ^{−j}(1+ζ^j)² and 1+t_j = ζ^{−j}(1+ζ^j)^{2²⁶−1}, because 2²⁶ ≡ 3 (mod 37) gives (1+ζ^j)^{2²⁶} = 1+ζ^{3j}. ζ^{−j} has order 37, coprime to 9. Hence: rule 90's values are cubes ⇔ rule 150's values are ninth powers ⇔ **1+ζ is a cube in F(2³⁶)***. Checked, together with the finer statement that 1+ζ is *not* a ninth power, in the form of two group-ring identities: **t(x)^87381 = 1 + J** and, sharper, **t(x)^29127 = Σ_{u non-residue mod 37} x^u** (so t_j^{29127} = ρ^{(j/37)}, ρ of order 3: *the ninth-power class of rule 90 at 37 is the Legendre symbol*), and **(1+t(x))^29127 = 1**. The "fundamental unit 6+√37" explanation in the project is therefore equivalent to "1−ζ₃₇ is a cubic residue at the prime above 2"; I did not prove that from reciprocity.

**Cheap product identities** (checked): R(2) = t(x¹⁹y¹⁹)·t(x¹⁹y⁻¹⁹) (so a+b = s is a product of two rule-90 values, hence a cube; p = ab likewise — F = s³+p²s²+p³+p²+p is a polynomial in two cubes, which explains nothing by itself because ninth-power-ness is not additive), R(7) = (1+t(x))(1+t(y)), R(13) = (1+t(xy))(1+t(x/y)).

## 4. What I excluded (all at m = 37, all by computation)

1. **Group-ring factorisation inside the family**: f ≡ g·h or f ≡ g·h² with g, h family rules — none except trivial (tested on 13 characters, hash lookup over all 32767 rules). Since f and g symmetric force h symmetric, this covers all symmetric factorisations in the 4-box.
2. **Mechanism 7 generalised to the group ring**: f ≡ U·g³ with g any of the 32 cube-confined family rules that are units; U = f·g⁻³ computed exactly; minimum weight 392 (g = 32767), random ≈ 685. No sparse U.
3. **Rule-150 units in all 684 torus directions**: f·(1+z+z²)⁻¹, z = x^p y^q; minimum weight 104, attained only for one-variable z, where the weight is small for trivial row-wise reasons.
4. **GL₂(Z/37) transport**: every A whose image of supp f fits in [−9,9]² has entries in {0,±1} (box 4: the 8 symmetries; box 6, 8: GL₂(Z) shears), i.e. is a Laurent-ring automorphism preserving irreducibility. No genuinely mod-37 transport to a small box exists.
5. Twisted-power/half-Frobenius forms in the group ring are *equivalent* to confinement (any ninth root g of f satisfies f ≡ g·g^{(8)}); they explain nothing unless g is sparse. The "440-term cube root" is one of 3³⁸ cube roots and says nothing about the minimum weight; the project should not cite it as evidence of randomness.
6. Univariate factorisations of Q_i(T) = F(T, T^{2ⁱ}) over GF(2) (classes i = 0..9): for i ≥ 3 the factor degrees are generic and the index-mod-9 sum vanishes with no visible pattern.

## 5. Where the project's chance calibration is off

Census over all 32767 rules at the 10 class characters (1, 2ⁱ): classes i = 1..8 are ninth powers for 3655–4408 rules each (≈ 1/9) and are pairwise independent (joint/product ratios 0.93–1.13); class 0 (diagonal, F(t,t), a polynomial of degree ≤ 8 in t) is a ninth power or zero for 15359/32767 ≈ 0.47; class 9 is forced. Hence a random rule is ninth-confined with probability ≈ 0.47·9⁻⁸ ≈ 1.1·10⁻⁸, expected ≈ 4·10⁻⁴ in the family. For cubes the same calculation gives ≈ 32767·0.94·3⁻⁸ ≈ 5 chance cube-confined rules — consistent with the sixth pilot's seven. So 4850 is **not** in the same category as those seven: it is either a mechanism or a ≈1-in-3000 coincidence. The counts 149/17 of rules with 5/6 good classes (vs ≈114/11 under this null) show no consistent pattern of failing classes, so there is no sign of a "partial" mechanism acting on 6 classes.

## 6. Predictions to register

- **P1 (discriminating test).** Extend the family to orbits 0 ≤ b ≤ a ≤ 5 (2²¹−1 rules) at m = 37. Under "4850 is a coincidence", the number of ninth-confined rules not explained by mechanisms 1–4 and not GL₂(Z)-images/dilations of 4850 is 0 (expected 0.02); if ≥ 2 such rules appear, there is a mechanism and it is tied to total degree ≥ 6 in (a,b). I predict 0–1.
- **P2 (proved, outside the family).** For any a, b coprime to 37, f(x^a, y^b) (reduced mod 37; e.g. f(x,y²), a 40-term non-symmetric rule in [−4,4]×[−8,8]) has odd period 29127 at m = 37 (checked for (1,2) and for f(xy, x/y)), since the spectrum is permuted; at every other odd m in 9..201 the odd part of f(x, y²) equals f's (the map (j,k)→(j,2k) is a bijection for odd m), i.e. the full bound.
- **P3 (proved).** For every symmetric rule at m = 37, the eigenvalues on the characters (j, ±6j) are 27th powers; for every symmetric rule the eigenvalue at (1,6) lies in F(2⁹). In particular all 4 rules confined to 27th powers and all 21 to ninth powers satisfy this class-9 statement for free.
- **P4 (checked at 37; conjectured generally).** t(x)^{(2^s−1)/9} ≡ Σ_{u∈NR} x^u. Conjecture: for a prime m with 2 a primitive root and 9 | 2^s−1, t(x)^{(2^s−1)/9} is Σ_{QR} x^u, Σ_{NR} x^u, or 1+J (i.e. the ninth-power class of rule 90 is always a quadratic character). Untested beyond 37.

```json
{"definitions": {"J": "1 + x^1 + x^2 + x^3 + x^4 + x^5 + x^6 + x^7 + x^8 + x^9 + x^10 + x^11 + x^12 + x^13 + x^14 + x^15 + x^16 + x^17 + x^18 + x^19 + x^20 + x^21 + x^22 + x^23 + x^24 + x^25 + x^26 + x^27 + x^28 + x^29 + x^30 + x^31 + x^32 + x^33 + x^34 + x^35 + x^36", "Jy": "1 + y^1 + y^2 + y^3 + y^4 + y^5 + y^6 + y^7 + y^8 + y^9 + y^10 + y^11 + y^12 + y^13 + y^14 + y^15 + y^16 + y^17 + y^18 + y^19 + y^20 + y^21 + y^22 + y^23 + y^24 + y^25 + y^26 + y^27 + y^28 + y^29 + y^30 + y^31 + y^32 + y^33 + y^34 + y^35 + y^36", "NR": "x^2 + x^5 + x^6 + x^8 + x^13 + x^14 + x^15 + x^17 + x^18 + x^19 + x^20 + x^22 + x^23 + x^24 + x^29 + x^31 + x^32 + x^35", "Fab": "t(x)^4*t(y)^2 + t(x)^3*t(y)^3 + t(x)^3 + t(x)^2*t(y)^4 + t(x)^2*t(y)^2 + t(x)^2*t(y) + t(x)*t(y)^2 + t(x)*t(y) + t(y)^3", "D10": "x^0*y^10 + x^0*y^-7 + x^0*y^7 + x^0*y^-10 + x^10*y^0 + x^10*y^-17 + x^10*y^-7 + x^10*y^7 + x^10*y^17 + x^-17*y^10 + x^-17*y^-17 + x^-17*y^3 + x^-17*y^-3 + x^-17*y^17 + x^-17*y^-10 + x^-7*y^0 + x^-7*y^10 + x^-7*y^-7 + x^-7*y^7 + x^-7*y^-10 + x^3*y^-17 + x^3*y^17 + x^-3*y^-17 + x^-3*y^17 + x^7*y^0 + x^7*y^10 + x^7*y^-7 + x^7*y^7 + x^7*y^-10 + x^17*y^10 + x^17*y^-17 + x^17*y^3 + x^17*y^-3 + x^17*y^17 + x^17*y^-10 + x^-10*y^0 + x^-10*y^-17 + x^-10*y^-7 + x^-10*y^7 + x^-10*y^17", "D26": "x^0*y^-11 + x^0*y^4 + x^0*y^-4 + x^0*y^11 + x^-11*y^0 + x^-11*y^15 + x^-11*y^4 + x^-11*y^-4 + x^-11*y^-15 + x^15*y^-11 + x^15*y^15 + x^15*y^-7 + x^15*y^7 + x^15*y^-15 + x^15*y^11 + x^4*y^0 + x^4*y^-11 + x^4*y^4 + x^4*y^-4 + x^4*y^11 + x^-7*y^15 + x^-7*y^-15 + x^7*y^15 + x^7*y^-15 + x^-4*y^0 + x^-4*y^-11 + x^-4*y^4 + x^-4*y^-4 + x^-4*y^11 + x^-15*y^-11 + x^-15*y^15 + x^-15*y^-7 + x^-15*y^7 + x^-15*y^-15 + x^-15*y^11 + x^11*y^0 + x^11*y^15 + x^11*y^4 + x^11*y^-4 + x^11*y^-15", "D8": "x^0*y^8 + x^0*y^-13 + x^0*y^13 + x^0*y^-8 + x^8*y^0 + x^8*y^16 + x^8*y^-13 + x^8*y^13 + x^8*y^-16 + x^16*y^8 + x^16*y^16 + x^16*y^-5 + x^16*y^5 + x^16*y^-16 + x^16*y^-8 + x^-13*y^0 + x^-13*y^8 + x^-13*y^-13 + x^-13*y^13 + x^-13*y^-8 + x^-5*y^16 + x^-5*y^-16 + x^5*y^16 + x^5*y^-16 + x^13*y^0 + x^13*y^8 + x^13*y^-13 + x^13*y^13 + x^13*y^-8 + x^-16*y^8 + x^-16*y^16 + x^-16*y^-5 + x^-16*y^5 + x^-16*y^-16 + x^-16*y^-8 + x^-8*y^0 + x^-8*y^16 + x^-8*y^-13 + x^-8*y^13 + x^-8*y^-16", "D6": "x^0*y^6 + x^0*y^18 + x^0*y^-18 + x^0*y^-6 + x^6*y^0 + x^6*y^12 + x^6*y^18 + x^6*y^-18 + x^6*y^-12 + x^12*y^6 + x^12*y^12 + x^12*y^-13 + x^12*y^13 + x^12*y^-12 + x^12*y^-6 + x^18*y^0 + x^18*y^6 + x^18*y^18 + x^18*y^-18 + x^18*y^-6 + x^-13*y^12 + x^-13*y^-12 + x^13*y^12 + x^13*y^-12 + x^-18*y^0 + x^-18*y^6 + x^-18*y^18 + x^-18*y^-18 + x^-18*y^-6 + x^-12*y^6 + x^-12*y^12 + x^-12*y^-13 + x^-12*y^13 + x^-12*y^-12 + x^-12*y^-6 + x^-6*y^0 + x^-6*y^12 + x^-6*y^18 + x^-6*y^-18 + x^-6*y^-12", "D23": "x^0*y^-14 + x^0*y^-5 + x^0*y^5 + x^0*y^14 + x^-14*y^0 + x^-14*y^9 + x^-14*y^-5 + x^-14*y^5 + x^-14*y^-9 + x^9*y^-14 + x^9*y^9 + x^9*y^18 + x^9*y^-18 + x^9*y^-9 + x^9*y^14 + x^-5*y^0 + x^-5*y^-14 + x^-5*y^-5 + x^-5*y^5 + x^-5*y^14 + x^18*y^9 + x^18*y^-9 + x^-18*y^9 + x^-18*y^-9 + x^5*y^0 + x^5*y^-14 + x^5*y^-5 + x^5*y^5 + x^5*y^14 + x^-9*y^-14 + x^-9*y^9 + x^-9*y^18 + x^-9*y^-18 + x^-9*y^-9 + x^-9*y^14 + x^14*y^0 + x^14*y^9 + x^14*y^-5 + x^14*y^5 + x^14*y^-9"},
 "factorisations": [{"rule": 7, "factors": [["1 + t(x)", 1], ["1 + t(y)", 1]]},
                    {"rule": 13, "factors": [["1 + t(x*y)", 1], ["1 + t(x*y^-1)", 1]]},
                    {"rule": 2, "factors": [["t(x^19*y^19)", 1], ["t(x^19*y^-19)", 1]]}],
 "congruences": [{"lhs": "R(4850)", "rhs": "Fab"},
                 {"lhs": "R(4850)^29127", "rhs": "1 + J*Jy"},
                 {"lhs": "t(x)^87381", "rhs": "1 + J"},
                 {"lhs": "t(x)^29127", "rhs": "NR"},
                 {"lhs": "(1 + t(x))^29127", "rhs": "1"},
                 {"lhs": "R(4850)*D10*D26", "rhs": "D8*D6*D23"},
                 {"lhs": "t(x)^4*t(y)^2 + t(x)^2*t(y)^4", "rhs": "O(4,2)"},
                 {"lhs": "t(x)^3 + t(x)", "rhs": "t(x^3)"}]}
```
