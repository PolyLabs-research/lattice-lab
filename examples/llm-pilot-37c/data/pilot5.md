# Cubes at m = 25: cube certificates, twisted pairs, and a fibre correlation

## 1. The answer in brief

Of the seventeen rules, **five are confined to the cubes for a reason I can prove, and the
proof is formalized in Lean.** The other twelve are not explained, and the evidence says the
excess they make up is mostly not excess.

* **Two (family 3096 and 23608) have a cube certificate.** This is mechanism 5 with a perfect
  cube as the multiplier. Exactly, over GF(2),

      3096  · (t(x) t(y))³ = Sh(3,1) + Sh(4,1) + Sh(7,1) + Sh(7,3) + Sh(7,4),
      23608 · (t(x) t(y))³ = Sh(1,1) + Sh(3,1) + Sh(4,1) + Sh(7,3) + Sh(7,4) + Sh(7,7),

  with t(z) = z + 1/z and Sh(a, b) the D4 orbit of (a, b). Each right side is permuted by
  (x, y) ↦ (x⁷, y⁷) on the 25-torus, and 7 = 2⁵ mod 25, so its eigenvalues lie in F(2⁵). Every
  element of F(2⁵) is a cube in F(2¹⁰). So off the axes each eigenvalue of f is an element of
  F(2⁵) divided by a cube, which is a cube. On the axes, where t(x) t(y) vanishes, f restricts
  to t²(t + 1)² = t(z)·t(z³) = t^129, also a cube. Rule 90 need not be confined at all: it is
  not at 25, and that is what blocked mechanism 5 here.
* **Three (1227, 21029, 32184) are twisted pairs:** f = C(x, y)·C(x³, y³) exactly, with
  C = self + N4, self + D4 and N4 + D4 respectively. Since 3 = 2⁷ mod 25, C(x³, y³) has the
  eigenvalues c^(2⁷), so f has c^129, and 129 = 3·43. This is the card's mechanism 4 (twisted
  powers) with d = 3, and the census missed it for these three.
* **The other nine family rules and the three atlas rules have no structure I could find.**
  Section 6 lists what I searched for and ruled out. Part of the excess is not structure but a
  flaw in the chance model. That model treats each class as independent, but the cube character
  at an order-25 character c is tied to the value at the order-5 character 5c by an exact
  identity (Lemma 6):

      N_{F(2¹⁰)/F(4)}(λ(c)) = λ(5c) + E(c),

  where E is a sum over length-5 necklaces. The identity makes P(class (0,1) is a cube) 0.62
  when (0,5) is confined and 0.06 when it is not. A model that keeps each fibre {5c, c, …}
  intact and treats fibres as independent expects **6.1** unexplained confined family rules at
  25, where we see **9**. Letting the axis and diagonal fibres share a joint law raises the
  expectation to **11.8**. The card's model expected 1.7. In the radius-4 hexagonal family, the
  only unexplained confined rules at 25 are exactly the two atlas ones, against 0.57 expected.

`condition(f, m)` in `mechanism.py` implements both mechanisms, A and B, for every odd m. It
also calls the previous pilot's half-Frobenius condition. Beyond m = 25, mechanism B explains
**19 of the 45 rows of the census remainder**: 16 at m = 13 that had been filed as chance, and
3 of the 5 "coinciding eigenvalue" rules at m = 21. It also explains 4 of the 12 family hits at
m = 21.

## 2. Setting

m is odd, ζ is a primitive m-th root of unity in F(2^d), d = ord_m(2), and s = sord(m). For a
Laurent polynomial g over GF(2), λ_g(c) = g(ζ^c) is its eigenvalue at the character c ∈ (Z/m)².
The facts used below:

* (F1) λ_{gh} = λ_g λ_h and λ_{g+h} = λ_g + λ_h. λ_g depends only on g mod (x^m − 1, y^m − 1).
* (F2) λ_g(c)^(2^k) = λ_g(2^k c), and λ_{g(x^a, y^a)}(c) = λ_g(ac).
* (F3) If g is symmetric (g(1/x, 1/y) = g), then λ_g(−c) = λ_g(c) and λ_g(c) ∈ F(2^s).
* t_w = x^w + x^−w is rule 90 along w, with λ_{t_w}(c) = t_{w·c}, where t_j = ζ^j + ζ^−j.
  t_j = 0 iff j ≡ 0 (mod m). If e ≡ ±2^a (mod m), then t_{ej} = t_j^(2^a).
* Ψ_e (e odd, e ≥ 3) is defined by D_e(t) = t ∏_{1<e'|e} Ψ_{e'}(t)², where D_e is the Dickson
  polynomial, x^e + x^−e = D_e(x + 1/x). For example Ψ₃ = t + 1 (tools/halffrob.py).

The q-th powers of a cyclic group form its unique subgroup of index q. So "every nonzero
eigenvalue is a q-th power in F(2^d)*" is the same as "every nonzero eigenvalue has order
dividing (2^d − 1)/q". Being a q₁-th power and a q₂-th power means being an lcm(q₁, q₂)-th power.

## 3. Mechanism A: twisted pairs

**Theorem A.** Suppose f = C(x^a, y^a)·C(x^b, y^b) exactly, gcd(ab, m) = 1, and
b ≡ ε 2^k a (mod m) with ε = 1, or with ε = −1 and C symmetric. Then every nonzero eigenvalue
of f at m is a gcd(1 + 2^k, 2^d − 1)-th power in F(2^d)*.

*Proof.* By (F1) and (F2), λ_f(c) = λ_C(ac)·λ_C(bc), and λ_C(bc) = λ_C(ε 2^k ac) =
λ_C(ac)^(2^k). For ε = −1 this step uses the symmetry of C. So λ_f(c) = μ^(1+2^k) with
μ = λ_C(ac) ∈ F(2^d). ∎

With b/a ≡ 2 this is the powers mechanism, f = C³. With b/a ≡ ±2^k, k odd, and 3 | 2^d − 1, it
gives cubes, because 3 | 1 + 2^k when k is odd. At 25: 3 ≡ 2⁷, so C·C(x³, y³) has eigenvalues
μ^129, and 129 = 3·43.

`twisted_pair(f, m)` tries symmetric C supported in [−1, 1]², and unions of symmetry orbits
within radius 2. It tries every pair a < b with (a + b)·width(C) = width(f), which is necessary
because bounding boxes add under multiplication. It checks the identity exactly, with `pmul`.

## 4. Mechanism B: cube certificates

**Lemma 1 (half-Frobenius; previous pilot).** If g | d, n ≡ 2^g (mod m), and
B(x^n, y^n) ≡ B (mod x^m − 1, y^m − 1), then λ_B(c) ∈ F(2^g) for every c.
*Proof.* λ_B(c)^(2^g) = λ_B(2^g c) = λ_{B(x^n,y^n)}(c) = λ_B(c). ∎

**Lemma 2 (zeros of the multiplier).** Let v be primitive and G the rule's symmetry group. Let
O_v = ∏ t_w and P_{e,v} = ∏ Ψ_e(t_w), both products over one w from each pair ±w in the orbit
Gv, with gcd(e, m) = 1. Then λ_{P_{e,v}} never vanishes, and λ_{O_v}(c) = 0 iff w·c ≡ 0 (mod m)
for some w in the orbit.

*Proof.* The roots of Ψ_e are z + 1/z with z of order exactly e. If t_j = z + 1/z with
ζ^j = z′, then z′ = z^{±1}, which is impossible because the order of z′ divides m and
gcd(e, m) = 1, e > 1. Also Ψ_e(0) = 1 (checked for e < 61). The claim about t_w is in §2. ∎

**Lemma 3 (the line criterion).** Let H(t) = t^i ∏_e Ψ_e(t)^{k_e} over GF(2), where every
divisor e′ > 1 of every e satisfies gcd(e′, m) = 1 and e′ ≡ ±2^{a(e′)} (mod m). Put a(1) = 0 and

    A = 2i + Σ_e k_e Σ_{e'|e} μ(e/e') 2^{a(e')}.

Then H(t_j)² = t_j^A for every j ≢ 0 (mod m), and H(t_0) ∈ {0, 1}. If q | A and q | 2^s − 1,
every nonzero value of H(t_j) is a q-th power in F(2^s)*.

*Proof.* From the definition of Ψ, t_{ej}/t_j = D_e(t_j)/t_j = ∏_{1<e'|e} Ψ_{e'}(t_j)². Every
t_{e'j} is nonzero because gcd(e′, m) = 1. Möbius inversion gives
Ψ_e(t_j)² = ∏_{e'|e} t_{e'j}^{μ(e/e')}, using Σ_{e'|e} μ(e/e') = 0. Then
t_{e'j} = t_j^(2^{a(e')}) gives the exponent A. Squaring is a bijection on F(2^s)*, so
H(t_j) = t_j^{A/2}, where A/2 is taken mod 2^s − 1, which is odd. If q divides A, it divides
A/2 mod 2^s − 1. At j = 0: t_0 = 0, so H(0) = 0 if i > 0, and otherwise H(0) = ∏ Ψ_e(0)^{k_e} = 1. ∎

On the line {c : w·c ≡ 0} = {k(w₂, −w₁)}, with w primitive, a symmetric f restricts to
H(t_k), where H is f(z^{w₂}, z^{−w₁}) written in t = z + 1/z (halffrob's Lemma 3).

**Theorem B (cube certificate).** Let f be symmetric. Let M be 1, an O_v or a P_{e,v} (as in
Lemma 2), let E ≥ 0, and let g be a divisor of d with g < d and n = 2^g mod m. Let q be a prime
power with q | E (E = 0 only if M = 1), q | (2^d − 1)/(2^g − 1), and q | 2^s − 1. Suppose

1. B := f·M^E (mod x^m − 1, y^m − 1) satisfies B(x^n, y^n) ≡ B, and
2. for every w in the orbit of an O_v factor of M, f on the line {w·c ≡ 0} satisfies Lemma 3
   with q | A.

Then every nonzero eigenvalue of f at m is a q-th power in F(2^d)*.

*Proof.* Let c be a character with λ_f(c) ≠ 0. If λ_M(c) ≠ 0, then
λ_f(c) = λ_B(c)·λ_M(c)^{−E}. By Lemma 1, λ_B(c) ∈ F(2^g)*, which is the subgroup of
((2^d − 1)/(2^g − 1))-th powers, so it is a q-th power. λ_M(c)^{−E} is a q-th power because
q | E. Otherwise c lies on one of the lines of condition 2 (Lemma 2), and λ_f(c) is a q-th power
in F(2^s)* ⊂ F(2^d)* by Lemma 3. ∎

With M = 1 this is mechanism 5's pure case. With M = N a product of rule-90 factors and no
exponent, it is mechanism 5's mixed case, which needs rule 90 itself to be confined. The new
point is that the multiplier need not be confined at all if it enters as a q-th power.

**The returned q.** `condition` takes the lcm of the q's that Theorems A and B and the previous
pilot's `halffrob.condition` prove. For symmetric f it also includes (2^d − 1)/(2^s − 1), since
eigenvalues lie in F(2^s). It returns that lcm only if it is larger than the lift factor alone,
and 1 otherwise. At 25, a cube in F(2¹⁰) comes out as q = 3·1025 = 3075.

**The search.** M ranges over 1 and the atoms O_v and P_{3,v}, P_{5,v}, with v primitive and
|v|∞ ≤ 2. E = qk with k ≤ 3; q runs over the prime powers < 200 allowed by some level g.
Condition 1 is checked exactly, as an identity of polynomials mod (x^m − 1, y^m − 1)
(`_dense_product`, integer FFT convolution, reduced mod 2). Before that, a cheap filter: the
images under the ring homomorphisms x^(p,r) ↦ z^{v₁p+v₂r} mod z^m − 1 commute with dilation,
so their invariance is necessary. Condition 2 uses Lemma 3's Ψ-division. No eigenvalue of f is
computed. All 1,274 atlas rules take about 20–30 s at one m ≤ 300, about 45 s at m = 299
including the previous pilot's search. 2,000 family rules take about 30 s at m = 75.

## 5. The seventeen at m = 25

| rule | orbits | explained | witness |
| --- | --- | --- | --- |
| 1227 | (0,0) (1,0) (2,0) (3,0) (3,1) (4,0) | yes (A) | C(x,y) C(x³,y³), C = self + N4 |
| 3096 | (2,0) (2,1) (4,0) (4,1) | yes (B) | f (t_x t_y)³ = Sh(3,1)+Sh(4,1)+Sh(7,1)+Sh(7,3)+Sh(7,4); axes t²(t+1)² |
| 21029 | (0,0) (1,1) (2,2) (3,3) (4,2) (4,4) | yes (A) | C = self + D4 |
| 23608 | (2,0) (2,1) (2,2) (4,0) (4,1) (4,2) (4,4) | yes (B) | f (t_x t_y)³ = Sh(1,1)+Sh(3,1)+Sh(4,1)+Sh(7,3)+Sh(7,4)+Sh(7,7) |
| 32184 | 10 orbits | yes (A) | C = N4 + D4 |
| 6538, 10441, 11508, 12668, 21081, 22626, 24319, 25912, 26229 | | no | |
| triangle E+T7+self, hexagon H1+H3+H13, hexagon H3+H4+H5 | | no | |

Why B is permuted by ×7: 7·(3,1) = (21,7) ≡ (−4,7) ∈ Sh(7,4); 7·(4,1) ≡ (3,7) ∈ Sh(7,3);
7·(7,1) ≡ (−1,7); 7·(1,1) = (7,7). Shell norms scale by 7² ≡ −1, so 10 ↔ 65 ≡ 15 and
17 ↔ 58 ≡ 8. This is the same arithmetic as 37: 2⁵ = 7 and 7² ≡ −1 at 25, against 2⁹ ≡ −6 and
6² ≡ −1 at 37. At 13 it is 2³ = 8 with 8² ≡ −1, and at 21 it is 2³ = 8 with 8² ≡ 1. Those are
the sizes where mechanism B finds rules elsewhere (§7).

Rules 1227 and 21029 are equivalent under the 45° map R = [[1,1],[1,−1]] (exponents
v ↦ Rv). Since R² = 2 on characters, any invertible exponent map preserves confinement. Under
GL₂(Z/25) no other two of the fourteen are equivalent within the family (checked), so the hits
are thirteen independent events.

**Lean** (`proofs/LatticeProofs/Pilot.lean`, built with `lake build LatticeProofs.Pilot`):
`period_r3096_dvd`, `period_r23608_dvd`, `period_r1227_dvd`, `period_r21029_dvd` and
`period_r32184_dvd` each state `period 25 D ∣ 341`, i.e. every eigenvalue is a cube in F(2¹⁰).
They rest only on propext, Classical.choice and Quot.sound. The proofs follow the outline above.
The GF(2) identities are checked by `linear_combination`, with certificates generated by
`scratch/genlean.py`. The Frobenius permutation of B uses 2⁵ mod 25. Rule-90 values satisfy
t^1024 = t, and on the axes t²(t+1)² = t^129 (`axis_val`). The twisted pairs go through the
general lemma `twisted_val` (C symmetric, D = C·C(x³, y³) ⇒ D's value is c^129 with c^1023 = 1).

## 6. The rest: what is ruled out, and why the remainder looks like chance

**Searches that found nothing for the other nine and the three atlas rules:**

* Twisted pairs C(x^a)C(x^b) with C symmetric in [−2, 2]², for every nonsquare ratio mod 25.
  Also A·A(x^n, y^n) mod 25 for A any family rule and any of the ten nonsquare n, compared in
  eigenvalue space. These recover exactly 1227, 21029 and 32184.
* Single-multiplier certificates f·M^{3k} ∈ F(2⁵) for M any of the 32,767 family rules and
  k = 1…10. This is a mod-11 coincidence on about nine classes, with chance about 11^−9 per
  pair. Only 3096 and 23608 (M = t_x t_y or ((1+a)(1+b))⁴), the twisted three, and the trivial
  M = f, E = 21 (since f²² ∈ F(2⁵) for any cube f) were found. The same for M = family rule ×
  up to two units (t_w, Ψ_e(t_w), |w| ≤ 4, e ≤ 11), and for hexagonal M for the atlas rules.
* Two-multiplier certificates f·M₁³ ∈ F(2⁵)·M₂³: the nine hits have 2–9 solutions, while random
  targets have 1–10 (`scratch/pairs.py`). That is chance level, and the twisted three have about
  885 each.
* Exact factorization by small divisors. Five hits share (1 + a)(1 + b) = rule 150 along both
  axes. 3096 and 6538 also share u = t_x + t_y = t_{(x/y)^{1/2}} t_{(xy)^{1/2}} (a rule-90
  product along the diagonals). Their cores, K = a² + b² + a + b + ab and K′ = 1 + ab(a + b),
  are not twisted pairs or certificates. 23608, 24319 and 26229 have cores of 40–48 terms.
  25912 = (N4 + D4)²·K″.
* No 5-adic lifting. The 1-D restrictions on most lines do not have their roots closed under
  z ↦ z⁵ (`scratch/closed.py`).

**Lemma 6 (the fibre identity).** Let m = 25, f symmetric and c a character of order 25. Then

    λ_f(c)^341 = N_{F(2¹⁰)/F(4)}(λ_f(c)) = λ_f(5c) + E(c),

    E(c) = Σ ζ^{S + 5T} over the non-constant 5-tuples (v₀, …, v₄) of terms of f, one per
           cyclic rotation, with S = Σ_k v_k·c ≡ 0 (mod 5) and T = Σ_k k (v_k·c).

*Proof.* The exponents 1, 6, 11, 16, 21 (= 1 + 5k) are ±2^{0,8,6,4,2} mod 25, so
∏_k λ(c(1+5k)) = λ^{1+4+16+64+256} = λ^341, which is the norm to F(4). Expand the product as a
sum over tuples: the tuple (v_k) contributes ζ^{Σ_k (1+5k) v_k·c} = ζ^{S + 5T}. Rotating the
tuple multiplies its term by ω^{−S}, where ω = ζ⁵. So an orbit of five rotations sums to
5ζ^{S+5T} = ζ^{S+5T} if 5 | S, and to 0 otherwise. A constant tuple gives ζ^{5v·c} = ω^{v·c},
and these sum to λ(5c). ∎

λ(c) is a cube iff the norm is 1. When the necklace term E vanishes or is small, cube-ness at c
follows the order-5 value λ(5c) ∈ {0, 1}. Over the whole family:
P(class (0,1) is a cube | λ(0,5) ∈ {0,1}) = 0.625, against 0.0625 otherwise. The same holds for
(1,1) given (5,5). The chance model treats these classes as independent, so it underestimates.

**Refined chance model.** Classes are grouped into fibres: the order-5 class and the order-25
classes over it, linked by c ↦ 5c. Each fibre keeps the empirical joint law over the population,
with the explained and forced rules removed, and fibres are independent.

| population at 25 | unexplained confined | independent classes | independent fibres |
| --- | --- | --- | --- |
| square family (32,767) | 9 | 1.49 | 6.06 (11.8 with axis + diagonal fibres joint) |
| hexagonal family, radius 4 (511) | 2 (= the two atlas rules) | 0.17 | 0.57 |
| atlas hexagon (126) | 2 | 0.08 | 0.24 |
| atlas triangle (126) | 1 | 0.03 | 0.13 |
| atlas square (1,022) | 0 | 0.06 | 0.43 |

So the family's nine are consistent with chance, at Poisson p ≈ 0.2 against 6.1, and below
11.8. In the family, the axis and diagonal fibres are also correlated with each other
(joint/product = 1.95 after removing the explained rules). I have no proof of where that comes
from. The atlas's three against about 0.8 are a mild excess, p ≈ 0.05, and I cannot rule out
structure there.

## 7. Reach and predictions elsewhere

* **Census remainder** (`data/remainder.csv`): 19 of 45 rows explained. 16 at m = 13 had been
  filed as "chance": eleven square, one triangle VO+VS+T13+self, four hexagon. Witnesses use
  M = O_(1,0), O_(1,1) or P_{3,(1,1)} with E = 3, 6 or 9, and g = 2 or 3; at 13, 2³ = 8 and
  8² ≡ −1. The other 3 are at m = 21: N4+K8+C4+L8+M8, N4+D4+K8+C4+M8+E4 and
  N4+A4+K8+B4+L8+E4+self (M = O_(1,0), E = 6, g = 3, 8² ≡ 1 mod 21). Not explained:
  D4+A4+B4+C4+L8+M8+self and H4+H13+self at 21; the triangle with hidden symmetries; the
  m = 115 split; the 18 other m = 13 rules; K8+M8+self at 29; and the three at 25.
* **Square family at 21:** 4 of the 12 hits (466, 699, 854, 22429), leaving 8 against the card's
  7.0 ± 2.6 expected.
* **Atlas grid, checked against the eigenvalues:** 85 sizes (every odd m from 9 to 161, plus
  175, 189, 201, 225, 243, 255, 273 and 299). There are 1,060 claims and none is false, at
  22–39 s per size (`scratch/sound_atlas.log`). Most claims beyond the previous pilot's are
  twisted pairs with b/a = 2. Those are the powers mechanism (f = C³, about 10 atlas rules at
  every m with 3 | 2^d − 1), plus VO+T13-type pairs with b/a = 3 wherever 3 ≡ ±2^odd. Claims
  that only the certificate makes appear at m = 13 (24 rules), 21 (5), 25 (D4+K8+B4 and
  B4+M8+E4, with M = P_{3,(1,0)}), 35, 41 and 61. Two of them are not cubes:
  * at 35, D4+K8+B4+L8+M8+E4 is confined to **5th powers** (M = O_(1,0), E = 15, n = 2⁶ = 29);
  * at 61, N4+D4+C4+L8+E4+self is confined to **11th powers** (M = O_(1,0), E = 33,
    n = 2¹⁵ ≡ 11, and 11² ≡ −1 mod 61 again).

  Both are sizes the census never flagged, since its question was cubes. The pattern behind B
  is n = 2^g with n² ≡ ±1 (mod m) and q | 2^g + 1 (or q | (2^d − 1)/(2^g − 1) in general).
* **Square family, whole, checked against the eigenvalues:** at m = 15, 21 and 25 there are 135,
  21 and 32 claims, none false. The judge's grid includes sizes I have not run on the whole
  family. proposal.py samples 1,500 family rules at 21, 25, 27, 33, 35, 45, 49, 55 and 63.

## 8. How I found it

The fibre correlation turned up first, in a check of whether order-25 cube characters depend on
the order-5 values. It explains part of the excess but is not a mechanism. Factoring the hits by
small divisors exposed the three twisted pairs. A search for single multipliers M with
λ_f λ_M³ ∈ F(2⁵) found M = t_x t_y for 3096 and 23608. That is a coincidence of probability
about 11^−9 per candidate, so it pointed to structure. Computing B = f·M³ mod 25 showed shells
permuted by ×7, the 37-type identity. The general form, Theorem B, then needed only the observation
that a multiplier entering as a q-th power needs no confinement of its own.
