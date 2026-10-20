# Unit times cube: nine of the sixteen at m = 37 (and all three at 61), and why the other seven look like chance

## 1. The answer in brief

Write a = x + 1/x and b = y + 1/y (rule 90 along the axes). Every square-family rule is a symmetric
polynomial F(a, b) over GF(2) of degree at most 4 in each variable, because the D4 orbit of (i, j) is
D_i(a) D_j(b) + D_j(a) D_i(b), with D_n the Dickson polynomials. Factoring the sixteen targets this
way splits them into two groups.

**Nine of them are a unit times a cube, exactly over GF(2):**

| | g = a + b + 1 | g = ab + 1 | g = ab + a + b |
| --- | --- | --- | --- |
| U = a + b | **1112** | **10498** | **13584** |
| U = ab | **2436** | **17056** | **28944** |
| U = (a + 1)(b + 1) | **3461** (37, 61) | **26883** (37, 61) | **18246** (37, 61) |

Each entry is the rule f = U · g³. For example, 1112 = (a + b)(a + b + 1)³. In x and y, a + b + 1 is
N4 + self, ab + 1 is D4 + self, and ab + a + b is N4 + D4. The table holds every product of a
bidegree-(1, 1) unit with the cube of a bidegree-(1, 1) non-unit: the family's degree bound allows
no other cubes. **The three in the last row are exactly the three targets also confined at 61.**

* The **units** U take values that are q-th powers whenever they are nonzero, for structural
  reasons. ab = t_j t_k and a + b = t_j + t_k = t_{(j+k)/2} t_{(j−k)/2} are products of rule-90
  values. Rule 90 is confined to the cubes at 37, so these are cubes there. (a + 1)(b + 1) is
  Ψ₃(t_j) Ψ₃(t_k), with Ψ₃(t)² = t_{3j}/t_j. At 37 that is a quotient of rule-90 values. At 61,
  where 3 = 2⁶, it is t^63, a cube **without rule 90 being confined**. Rule 90 is not confined at 61.
* The **cube** g³ needs no reason at all.

So every nonzero eigenvalue is a cube: λ_f = λ_U · λ_g³. The general mechanism, a rule that is a
product of cyclotomic "units" along lattice directions times a q-th power, is stated and proved in
§3. It is implemented as `condition(f, m)` in `mechanism.py`, and formalised in Lean for all twelve
confinements (§6).

**The other seven (4850, 5972, 13822, 22064, 25183, 27390, 28586) I could not explain, and the
evidence says most of the excess they seem to make is the chance model's error, not structure.**
The census model takes every free class to be a cube with probability 1/3. At 37, two of the ten
free classes are a cube in **93.5%** of the family: the axis class and the diagonal class. The
reason is the same mechanism in one dimension. On the axis, a rule's eigenvalue is H(t_j) with
deg H ≤ 4, and every polynomial of degree ≤ 4 over GF(2) is a product of whole Ψ_e's (which are
units at 37), except the two quartic halves of Ψ₁₇. So 29 of the 31 possible H give cubes. The
diagonal is the same with H². Using the measured cube rate of each class, still with independent
classes, the expected number of chance confinements at 37 is **5.7, not 0.62**. Seven remain
unexplained, so the remainder is consistent with chance (Poisson P(≥ 7 | 5.7) ≈ 0.33). The model
with these rates also fits the rest of the distribution: rules with 1, 2 or 3 non-cube classes
number 82, 560 and 2,022, against 80, 534 and 2,044 predicted. What I ruled out for the seven is
in §5.

## 2. Setting

m is odd, ζ is a primitive m-th root of unity in F(2^d), d = ord_m(2), and s = sord(m). Then
d ∈ {s, 2s}, and R = (2^d − 1)/(2^s − 1) ∈ {1, 2^s + 1}. For a Laurent polynomial g over GF(2),
λ_g(c) = g(ζ^c) is its eigenvalue at the character c ∈ (Z/m)². Write t_j = ζ^j + ζ^−j (rule 90's
eigenvalues; t_j ∈ F(2^s), and t_j = 0 iff j ≡ 0) and h = (m + 1)/2, the inverse of 2 mod m.

* (F1) λ_{gh} = λ_g λ_h, λ_{g+h} = λ_g + λ_h, and λ_{x^v}(c) = ζ^{v·c}.
* (F2) A symmetric rule (f(1/x, 1/y) = f) has λ_f(−c) = λ_f(c) and λ_f(c) ∈ F(2^s).
* For odd e, Φ_e is the e-th cyclotomic polynomial, and Ψ_e (e ≥ 3) is defined by
  Φ_e(z) = z^{φ(e)/2} Ψ_e(z + 1/z). Equivalently D_e(t) = t ∏_{1<e'|e} Ψ_{e'}(t)², since
  z^e + z^−e = z^−e ∏_{e'|e} Φ_{e'}(z)² over GF(2) (previous pilots). Ψ_e(0) = Φ_e(1) mod 2 = 1.
  Φ_e is squarefree over GF(2) for odd e, and its irreducible factors are the polynomials whose
  roots have multiplicative order exactly e.
* For primitive w ∈ Z², X_w = x^{w₁} y^{w₂}. The **unit** u_{w,e} is Φ_e(X_w) ∈ GF(2)[x^±, y^±]. By
  (F1), with j = w·c,

      λ_{u_{w,e}}(c) = Φ_e(ζ^j) = ζ^{jφ(e)/2} Ψ_e(t_j)      (e > 1),
      λ_{u_{w,1}}(c) = 1 + ζ^j = ζ^{jh} t_{jh}                  (e = 1).                   (1)

  Write V_e(i) for Ψ_e(t_i) (e > 1) or t_i (e = 1). Then λ_u(c) = ζ^{(linear in c)} · V_e(i) with
  i = j or jh, and V_e(−i) = V_e(i).

The q-th powers of a cyclic group form its unique subgroup of index q. So for q | 2^s − 1, the
q-th powers of F(2^s)* are the (qR)-th powers of F(2^d)*.

## 3. The mechanism and its proof

**Definition.** For a prime power q dividing 2^s − 1, call (e, m, q) *good* if V_e(i) is 0 or a
q-th power in F(2^s)* for every i ∈ Z/m.

**Lemma 1 (good units).**
(a) Suppose every nonzero t_i is a q-th power in F(2^s)*, i.e. rule 90 is confined to the q-th
    powers at m. Then (e, m, q) is good for e = 1, for e prime, and for gcd(e, m) = 1.
(b) Suppose every divisor e' > 1 of e satisfies e' ≡ ±2^{a(e')} (mod m), and q divides
    A_e = Σ_{e'|e} μ(e/e') 2^{a(e')}, with a(1) = 0. Then (e, m, q) is good, whatever rule 90 does.

*Proof.* The q-th powers of F(2^s)* form a subgroup, and squaring permutes it, because the group
has odd order.
(a) For e = 1 the claim is the hypothesis. Let e = p be prime. From D_p(t) = t Ψ_p(t)² we get
t_{pi} = t_i Ψ_p(t_i)². If i ≡ 0, then Ψ_p(0) = 1. Otherwise t_i ≠ 0, and Ψ_p(t_i)² = t_{pi}/t_i is
0 or a quotient of q-th powers. So Ψ_p(t_i) is 0 or a q-th power.
For gcd(e, m) = 1 and i ≢ 0, every t_{e'i} is nonzero, and Möbius inversion of
D_e = t ∏ Ψ_{e'}² gives Ψ_e(t_i)² = ∏_{e'|e} t_{e'i}^{μ(e/e')}, a q-th power. For i ≡ 0, Ψ_e(0) = 1.
(b) For i ≢ 0, t_{e'i} = t_i^{2^{a(e')}} because t_{−n} = t_n and t_{2n} = t_n². The same Möbius
inversion gives Ψ_e(t_i)² = t_i^{A_e}, a q-th power since q | A_e (the second previous pilot's
Lemma 3). For i ≡ 0, Ψ_e(0) = 1. ∎

**Theorem (unit times power).** Let f be symmetric, m odd and q a prime power dividing 2^s − 1.
Suppose that, exactly in GF(2)[x^±1, y^±1],

    f = x^v · ∏_{(w,e)} Φ_e(X_w)^{k_{w,e}} · h^q

for some v ∈ Z², some Laurent polynomial h, and exponents k_{w,e} ≥ 0, with (e, m, q) good whenever
q ∤ k_{w,e}. Then every nonzero eigenvalue of f at m is a q-th power in F(2^s)*, hence a (qR)-th
power in F(2^d)*.

*Proof.* Fix c with λ_f(c) ≠ 0. Then every factor's eigenvalue at c is nonzero. By (F1) and (1),

    λ_f(c) = ζ^{ℓ(c)} · W(c) · λ_h(c)^q,      W(c) = ∏ V_{e}(i_{w,e}(c))^{k_{w,e}},

where ℓ is a linear form in c (mod m) and each V_e(i) is a nonzero element of F(2^s). A factor with
q | k is a q-th power because V ∈ F(2^s)*. A factor with q ∤ k is a q-th power because (e, m, q) is
good. So W(c) is a q-th power in F(2^s)*.

Since f is symmetric, λ_f(−c) = λ_f(c). Also W(−c) = W(c), because V_e(−i) = V_e(i), and
ℓ(−c) = −ℓ(c). Comparing the two expressions gives ζ^{2ℓ(c)} = y^q with
y = λ_h(−c)/λ_h(c) ∈ F(2^d)*. Hence ζ^{ℓ(c)} = (ζ^{2ℓ(c)})^h = (y^h)^q, and λ_f(c) = W(c) · x^q
with x = y^h λ_h(c) ∈ F(2^d)*.

Now x^q = λ_f(c)/W(c) ∈ F(2^s)*. If d = s we are done. If d = 2s, let z = x^{2^s−1}. Then
z^q = 1 and z^{2^s+1} = x^{2^d−1} = 1. Since q | 2^s − 1, gcd(q, 2^s + 1) = 1, so z = 1, that is,
x ∈ F(2^s)*. So λ_f(c) = W(c) x^q is a q-th power in F(2^s)*. ∎

**Remarks.**
* With no units (f = x^v h^q) this is mechanism 2 (powers). With no h it is mechanism 1
  (splitting): a product of one-dimensional rules along lattice directions.
* The new content is the *mixture*. The multiplier needs no confinement of its own when it enters
  as a q-th power. The units need not be cubes on their own either: they only have to be q-th
  powers *as functions on the torus*, for one of the reasons in Lemma 1.
* At 61 the unit (a + 1)(b + 1) is confined by Lemma 1(b) alone (3 = 2⁶, A₃ = 2⁶ − 1 = 63), with no
  help from rule 90. That is why only the U = (a + 1)(b + 1) row survives at 61.

**`condition(f, m)`** (`mechanism.py`) decides the hypothesis from the factorisation of f over
GF(2). It computes no eigenvalue of f.

1. *Line factors.* A factor that is a polynomial in one monomial X_w gives an edge of f's Newton
   polygon parallel to w (Newton polygons add under multiplication). For each edge direction w,
   take a unimodular change of variables (X, Y) = (X_w, X_{w'}). The line factors in direction w
   are then exactly the content of f as a polynomial in Y, the gcd of its coefficients in
   GF(2)[X]. This content is factored with sympy's univariate GF(2) factoriser. An irreducible
   factor π belongs to Φ_e(X_w), where e is the order of X modulo π. The factors of Φ_e(X_w) form
   one group, and the number of factors is φ(e)/ord_e(2).
2. *The core.* Divide f exactly by all line factors. The quotient (the product of the
   two-dimensional factors) must be h^q. This is tested by Kronecker substitution, a univariate
   square-free decomposition, a q-th root, and an exact check that h^q equals the core.
3. *The exponents.* Within each group (w, e), all factors of Φ_e(X_w) must occur with
   multiplicities that are congruent mod q (absent factors count 0). This holds iff
   f = x^v ∏ Φ_e(X_w)^k · (q-th power), with k = the least multiplicity in the group. If k ≢ 0 mod q,
   (e, m, q) must be good by Lemma 1. Part (a) uses rule 90's confinement, read off the rule-90
   values t_j by `halffrob._rule90_powers` (the same input as the splitting mechanism, and the
   only field computation). Part (b) is arithmetic mod m.

It returns R times the product of the largest valid prime powers, if that is more than R. It also
consults the two previous pilots' conditions (`tools/certificate.py`, which calls
`tools/halffrob.py`) and returns the lcm. The factorisation does not depend on m and is cached.
For all 1,274 atlas rules at one m, the whole condition takes 30 s (m = 37) to 40 s (m = 299); for
2,000 family rules at m ≤ 125, 25–40 s.

## 4. The nineteen targets

At 37, d = 36, s = 18 and R = 2^18 + 1. Rule 90 is confined to the cubes (its odd part is 87,381;
`proposal.py` checks the 3-part of its confinement). So Lemma 1(a) makes a + b, ab and
(a + 1)(b + 1) good for q = 3, and `condition` returns 3R = 786,435 for the nine rules of the table.

At 61, d = 60, s = 30. Rule 90 is not confined, but 3 = 2⁶ (mod 61) and 3 | 63, so Ψ₃ is good by
Lemma 1(b). `condition` returns 3(2^30 + 1) for 3461, 26883 and 18246 at 61, and nothing for the
other six.

In the Laurent ring these factorisations read, for example,

    1112 = (x + y)(1 + xy)/(xy) · (1 + x + y + 1/x + 1/y)³,
    3461 = Φ₃(x) Φ₃(y)/(xy) · (1 + x + y + 1/x + 1/y)³,

and `condition` finds them through the line content in the directions (1, ±1), respectively
(1, 0) and (0, 1).

| rule | m | explained | witness |
| --- | --- | --- | --- |
| 1112, 10498, 13584 | 37 | yes | U = a + b = units Φ₁(X_{(1,1)}), Φ₁(X_{(1,−1)}) |
| 2436, 17056, 28944 | 37 | yes | U = ab = Φ₁(x)² Φ₁(y)²/(xy) |
| 3461, 26883, 18246 | 37, 61 | yes (both) | U = (a + 1)(b + 1) = Φ₃(x) Φ₃(y)/(xy) |
| 4850, 5972, 13822, 22064, 25183, 27390, 28586 | 37 | no | see §5 |

The sixteen fall into GL₂(Z/37) classes as follows: 1112 and 17056 are images of each other under
the 45° map (consistent: a + b = pq and ab = (p + q)² in the rotated coordinates of the fourth
pilot), and no other two are equivalent (`scratch/equiv.py`).

## 5. The seven others, and the chance model

**What I ruled out for the seven**:

* *Unit × q-th power, in any form.* Over GF(2), five of the seven are irreducible as Laurent
  polynomials. 13822 = (17 terms)(12 terms) and 27390 = (N4 + D4)(32 terms) have only
  multiplicity-one factors, and none of those factors is a unit (`scratch/lfact.py`). Their images
  under all integer matrices with entries in [−3, 3] and determinant prime to m, put through the
  same condition, give nothing either (`scratch/images.py`, `scratch/images.log`). The same holds
  for every census remainder at 21, 25 and 29.
* *Twisted products with a multiplier*, f · M = C(x, y) C(x^n, y^n), C ⊂ [−1, 1]², n ∈ {3, …, 13}:
  none (`scratch/twsearch.py`).
* *Cube certificates with an arbitrary cube multiplier*: λ_f λ_U λ_g³ in F(2⁹) or in F(2⁶) at every
  class, for g any of the 32,767 family rules and U ∈ {1, a + b, ab, (a + 1)(b + 1), (a + b)²}.
  Both subfields lie inside the cubes, and nothing was found (`scratch/gsearch.py`,
  `scratch/gsearch2.py`). This generalises the previous pilots' certificates, whose multipliers
  were rule-90 orbit products.
* *Twisted identities* f(x³, y³) ≡ f² · (unit) · (cube): F(a, b)² does not even divide
  F(a³ + a, b³ + b).
* *Line by line.* On each line through the origin, a rule restricts to a one-variable H(t). If, for
  some representative direction vector, H is a product of whole Ψ_e's (units at 37) times a cube,
  that class is structurally a cube. For the seven this works on the axis and the diagonal (and
  on at most four other classes). For every one of them it fails on at least five of the eleven
  classes, for every one of the 36 representatives of each direction (`scratch/perline.py`).

**The chance model is wrong at 37, by a factor of about 9.** Measured over the whole family
(`scratch/refchance.py`, `scratch/dist2.py`), the cube rate of each free class at 37 is:

| class | (1,0) axis | (1,1) diagonal | (1,2) | (1,3) | (1,4) | (1,5) | (1,7) | (1,8) | (1,10) | (1,13) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P(cube) | 0.935 | 0.935 | 0.394 | 0.349 | 0.337 | 0.343 | 0.331 | 0.331 | 0.339 | 0.337 |

The axis value of a family rule is H(t_j), with H in the span of 1, t, t², t³ + t and t⁴. Of the
31 nonzero H, the 29 that are products of t, Ψ₃ = t + 1, Ψ₅, Ψ₇, Ψ₉ and Ψ₁₅ are cubes at 37 by
Lemma 1(a). The two that are not are t⁴ + t + 1 and t⁴ + t³ + t² + t + 1, the two halves of
Ψ₁₇ = (t⁴ + t + 1)(t⁴ + t³ + t² + t + 1) (`proposal.py` checks this). A half of Ψ₁₇ is not a unit,
and these two are indeed not cubes. The diagonal value is H(t)², the same distribution. Lines of
slope 2 carry polynomials of degree ≤ 12, slightly biased the same way (0.394).

With these marginals and classes still independent, the expected number of all-cube rules at 37 is
**5.71**, against the census model's 0.63, which the same code reproduces. Restricted to the
26,936 rules whose axis and diagonal are cubes and whose other eight classes are nonzero, the
count of non-cube classes among those eight matches the independent model:

| non-cube classes among the 8 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| observed | 42 | 82 | 560 | 2,022 | 4,891 | 7,341 | 7,075 | 3,961 | 962 |
| independent model | 5.2 | 80 | 534 | 2,044 | 4,885 | 7,464 | 7,122 | 3,879 | 924 |

Only the "0" column is in excess: 42 against 5.2. Of those 42, 35 have structural explanations
(mechanisms 1–6 and this one). The seven unexplained are within chance of the model's 5.2–5.7.
**So the seven are most likely chance**, with this caveat: I cannot exclude a mechanism I did not
think of. The prediction that would separate the two is that the seven are not confined at any
other size. They are not at 61 or at any other size in the census.

The same correction elsewhere: at 29 the refined expectation is 7.85 (census model 5.66), against
13 unexplained (Poisson p ≈ 0.05; the axis class is a cube 38.7% of the time there). At 61 it is
0.00, against 0 unexplained once the mechanism takes the three.

## 6. Lean

`proofs/LatticeProofs/Pilot.lean` (namespace `LatticeProofs.Pilot37b`) proves, for the nine rules
at 37,

    period_r1112_dvd_37 : period 37 r1112Offsets ∣ 87381        (and likewise for the other eight)

and for the three at 61,

    period_r3461_dvd_61 : period 61 r3461Offsets ∣ 357913941   (= (2^30 − 1)/3; also 26883, 18246)

These say that every eigenvalue is a cube of F(2^18), respectively F(2^30). The proofs follow §3:

* the identity f = U · g³ over a commutative ring with 2 = 0 and x·xi = y·yi = 1
  (`r…_identity`, by `linear_combination` with certificates generated by `scratch/genlean.py`);
* the units: a + b = t(XY) t(X/Y) with x = X², y = Y² (`sum_split`); ab = t(x) t(y); and
  a + 1 = (t(X) + 1)², handled by the fourth pilot's `Cubes37.line_val`. All of these rest on its
  certificate `Cubes37.r90_val` that rule 90 is cube-valued at 37. At 61, `psi3_val61` proves
  (t + 1)² = t⁶³ from t⁶⁴ = t(z³) (3 = 2⁶ mod 61) and t^{2^30} = t;
* the cube: g^{2^s} = g, so (g³)^{(2^s−1)/3} = 1 (`cube_val`);
* `period_dvd_of_ev`, from values at m-th roots of unity to the period (via `isPeriod_iff`).

## 7. Reach and predictions

* **Targets**: 9 of the 16 at 37, and all 3 at 61.
* **Census**: these 12 rows. None of the remainders at 21, 25 or 29 is explained (they are not unit
  × cube).
* **Atlas** (all 1,274 rules, every odd m from 3 to 301): 1,081 claims of this mechanism, each
  checked against the eigenvalues computed directly, **none false** (`scratch/sweep_atlas.log`).
  All of them are the splitting and powers cases (mechanisms 1–2, which the condition also proves).
  The atlas has no rule of the new mixed kind (`scratch/classify.py`), which is why the atlas
  census never flagged one.
* **Family** (all 32,767 rules at 39 odd sizes from 13 to 125, `scratch/famsweep.log`, and again
  at the composite sizes after the last change to Lemma 1(a), `scratch/famsweep_v2.log`): every
  claim checked against the eigenvalues, none false. The claims of the mixed kind
  (`scratch/classify_family.log`) are exactly the nine rules of the table, and they are confined
  * all nine wherever rule 90 is confined to the cubes: for m ≤ 301, at **37, 95, 101, 111, 141,
    197, 203 and 269**;
  * the three with U = (a + 1)(b + 1) also wherever Ψ₃ is good by Lemma 1(b) (3 ≡ ±2^{even} mod m,
    3 | 2^s − 1), or by (a): **13, 37, 61, 95, 101, 111, 141, 143, 169, 181, 193, 197, 203, 247,
    253, 259, 269, 299**.

  Those up to 151 were verified directly (`scratch/predict.py`). 13, 95, 101, 111, 141 and 143 are
  sizes the family census has not looked at.
* In the family no q other than 3 can occur in the mixed case: g^q with q ≥ 5 would need g of
  degree < 1. Larger rules (radius ≥ 5) would give 5th- and 7th-power versions wherever units are
  confined to those powers, for instance rule 90's 7th powers at 199 and 203.

## 8. How it was found

The card noted that nobody had looked at factorisations, because sympy cannot factor bivariate
polynomials over GF(2). I wrote the rules as symmetric polynomials in a = x + 1/x and b = y + 1/y,
the natural coordinates for D4-symmetric rules, and factored them by Kronecker substitution and
recombination (`scratch/fact2.py`). Nine targets came out as (a + b)(a + b + 1)³ and its
relatives. The three at 61 all have the unit (a + 1)(b + 1), which is good at 61 because 3 = 2⁶.
For the seven irreducible ones I measured the per-class cube rates over the whole family, and found
the 29/31 axis bias that the census model misses.

## 9. What I am unsure of

* The seven unexplained rules at 37. The refined model makes them unremarkable, but it is still a
  model: it assumes independent classes, with marginals measured on the same population.
* At 29 the excess, 13 against 7.85, is borderline (p ≈ 0.05), and I found no structure there.
* The condition is sufficient, not necessary. It looks only at exact factorisations over GF(2), not
  at identities that hold only on the m-torus.
