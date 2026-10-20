# Ninth powers at m = 37: exponent bookkeeping on the half-Frobenius identities

## 1. The answer in brief

**Four of the five targets (699738, 985232, 1431278, 1968276) are explained; 4850 is not, and I
can say precisely what it is not.**

The four radius-5 targets factor exactly over GF(2), with a = x + 1/x, b = y + 1/y,
Ψ₅(t) = t² + t + 1, and the two half-Frobenius cores of the fourth pilot,
W = A4 + K8 + B4 + self and V = C4 + L8 + M8 + E4:

| rule | factorisation | half-Frobenius identity of the core (exact, every m) |
| --- | --- | --- |
| 699738 | Ψ₅(a) Ψ₅(b) (a + b) · W | W(x², y²) t(x) t(y) t(xy) t(x/y) = Sh(7, 5) |
| 985232 | a² b² (a + b) · W | same |
| 1431278 | Ψ₅(a) Ψ₅(b) · V | V(x², y²) t(x) t(y) = Sh(7, 7) + Sh(5, 5) |
| 1968276 | a² b² · V | same |

At 37 the right sides are permuted by (x, y) ↦ (x⁶, y⁶), 6 ≡ −2⁹, so their eigenvalues lie in
F(2⁹), whose nonzero elements are **27th powers** of F(2¹⁸)* (513 = 27 · 19 is prime to 511).
The fourth pilot's mechanism stops at cubes because it bounds every unit by rule 90's
confinement (t_j is a cube, not a ninth power). The point of this proposal is that **the units
enter with exact exponents, and the exponents decide**: as functions on the torus,

    t_w^k  = (power of t_(w·c)) with exponent k,      Ψ₅(t_w)² = t_(w·c)^(2²³ − 1)     (5 ≡ 2²³ mod 37),

so for 1968276 at the character 2c, λ = t_j⁴ t_k⁴ · λ_V(2c) = t_j³ t_k³ · λ_SV(c): the cube of a
cube times an element of F(2⁹), a ninth power. For 1431278, λ(2c) = t_j^(2²³−2) t_k^(2²³−2) λ_SV(c)
and 3 divides 2²³ − 2. The 3-adic valuation of the net exponent in each direction (1 here), plus
rule 90's cube confinement (1), gives 3² = 9: the claim is q = 9 · (2¹⁸ + 1) in F(2³⁶)*, and the
eigenvalues are not 27th powers (the exponent has valuation exactly 1), as the census says.

The general statement (section 3) is a bookkeeping theorem on top of the known exact
factorisations and half-Frobenius identities: a rule f = U · C with U a product of line units
Φ_e(X_w) and C a core with C · N ≡ B (mod x^m − 1, y^m − 1), B invariant under a dilation by
2^g, N a product of orbit units, is confined to the p^k-th powers whenever p^k divides
q'_p · E_w for the **combined exponent E_w of U/N in every direction w**, with q'_p rule 90's own
confinement; and likewise for exact factorisations f = U · h^Q. Nothing about the eigenvalues
of f is computed. `condition(f, m)` in `mechanism.py` decides it from the factorisation of f over
GF(2) (the sixth pilot's line-content method) and a search for N (the fourth pilot's search,
re-scored). It returns 9 · (2¹⁸ + 1) on the four targets and is verified against the eigenvalues
on every claim I could check (section 7).

**4850** has none of this structure, and I show it is not of any of the following forms at 37
(section 6): a product of units in up to three directions (any directions mod 37, any exponents)
times an F(2⁹)-valued rule, even up to 27th roots of unity; g³ times a unit times an
F(2⁹)-valued rule for any g of radius ≤ 6; a twisted pair (impossible at 37); a per-line
cyclotomic certificate (the first consultation's certificate is vacuous: every cube in F(2¹⁸)*
is a power of t₁, and ⟨1 + ζ⟩ ∩ F(2¹⁸)* is exactly the cubes). Its 45° rotation and its three
unit multiples among the radius-6 ninth-power rules are the same unexplained event. Everything
else at radius ≤ 6 is explained (section 7).

## 2. Setting and notation

m odd, d = ord_m(2), s = sord(m), R = (2^d − 1)/(2^s − 1) ∈ {1, 2^s + 1}. ζ is a primitive m-th
root of unity in F(2^d); a symmetric rule f (f(1/x, 1/y) = f) has eigenvalues
λ_f(c) = f(ζ^c) ∈ F(2^s) at the characters c ∈ (Z/m)². t_j = ζ^j + ζ^−j are rule 90's
eigenvalues; t_j = 0 iff j ≡ 0. The q-th powers of a cyclic group are its unique subgroup of
index q, so "every nonzero eigenvalue is a q-th power in F(2^d)*" means "every nonzero eigenvalue
has order dividing (2^d − 1)/q"; a q₁-th power that is also a q₂-th power is an lcm(q₁, q₂)-th
power; and an element of F(2^s)* that is a q-th power there is a (qR)-th power in F(2^d)* (it is
an R-th power of F(2^d)*, and gcd(q, R) = 1 as q | 2^s − 1).

**Rule 90's confinement.** For a prime p let q'_p = p^{k'_p} be the largest power of p such that
every nonzero t_j is a q'_p-th power in F(2^s)*. It is read off the rule-90 values t_j (one per
Frobenius orbit of Z/m; `halffrob._rule90_powers`), the only field computation in `condition`
and the same input the splitting mechanism uses. At 37, q'_3 = 3.

**Line units.** For a primitive w ∈ Z², X_w = x^{w₁} y^{w₂} and t_w = X_w + 1/X_w. For odd e,
Φ_e is the e-th cyclotomic polynomial and Ψ_e(z + 1/z) = z^{−φ(e)/2} Φ_e(z). The line unit
Φ_e(X_w) has, at c with j = w·c,

    Φ_e(ζ^j) = ζ^{jφ(e)/2} Ψ_e(t_j)   (e > 1),      1 + ζ^j = ζ^{jh} t_{jh}   (e = 1, h = (m+1)/2),

and t_w = X_w^{−1}(1 + X_w)². Call e **representable at m** if every divisor e' > 1 of e is prime to
m and e' ≡ ±2^{a(e')} (mod m). Then (the fifth pilot's Lemma 3)

    Ψ_e(t_j)² = t_j^{A_e},   A_e = Σ_{e'|e} μ(e/e') 2^{a(e')}  (a(1) = 0),   for j ≢ 0,

and Ψ_e(0) = Φ_e(1) mod 2 = 1. Every e is representable at 37 (2 is a primitive root):
A₃ = 2²⁶ − 1, A₅ = 2²³ − 1, A₇ = 2³² − 1, A₉ = 2²⁷ − 2²⁶.

**Facts at 37** (checked in `proposal.py`): 2⁹ ≡ −6, 6² ≡ −1, so t^{2⁹} = D₆(t) = t⁶ + t² for
t = t₁, and the norm to F(2⁹) is N(t) = t⁵¹³ = t³(1 + t)⁴. t₁ has order 87381 = (2¹⁸ − 1)/3:
**the rule-90 values generate every cube of F(2¹⁸)*.** Since N(t) ∈ F(2⁹) is a 27th power and t³
is a ninth power, (1 + t)⁴ and hence 1 + t are ninth powers (rule 150's confinement, derived from
rule 90's). F(2⁹)* consists of 27th powers.

## 3. The mechanism and its proof

**Definition (exponent of a unit product).** Let P = ∏_{(w,e)} Φ_e(X_w)^{k_{w,e}} with integer
exponents k (negative allowed), e representable. Its exponent in direction w is

    E_w(P) = k_{w,1} + Σ_{e>1} k_{w,e} A_e.

**Lemma 1 (units by exponent).** Let c be a character with t_{w·c} ≠ 0 for every w with
k_{w,·} ≠ 0 (if some t_{w·c} = 0 the value of P is 0 or involves only Ψ-factors, which are 1
there). Then λ_P(c) = ζ^{ℓ(c)} · V(c) with ℓ linear in c and V(c)² = ∏_w t_{w·c}^{E_w}. If p^k
divides q'_p · E_w for every w, then V(c) is a p^k-th power in F(2^s)*.

*Proof.* Multiply the displayed values; squaring removes the half-exponents of e = 1 and gives
t_{w·c}^{k_{w,1}} ∏_e (Ψ_e(t_{w·c})²)^{k_{w,e}} = t_{w·c}^{E_w}. Each t_{w·c} is a q'_p-th power:
t = h^{q'_p}, so t^{E_w} = h^{q'_p E_w} is a p^k-th power when p^k | q'_p E_w. A product of p^k-th
powers is one; and V² a p^k-th power implies V is, because squaring is an automorphism of the
odd-order group F(2^s)* that preserves its subgroup of p^k-th powers. ∎

Non-representable units with gcd(e, m) = 1 (or e prime) still have values in the group T_m
generated by the t_j (the fourth pilot's Lemma 2b, or Ψ_p(t_j)² = t_{pj}/t_j), hence are q'_p-th
powers; `condition` counts such a factor Φ_e(X_w)^k as a p^{k'_p + v_p(k)}-th power on its own.

**Theorem A (units times a power).** Let f be symmetric and suppose, exactly in the Laurent ring,

    f = x^v · ∏_{(w,e)} Φ_e(X_w)^{k_{w,e}} · h^Q      (h = 1 allowed; Q ≥ 1).

Let p^k | 2^s − 1 with p^k | q'_p E_w for every direction w of the unit part, p^k | q'_p k_{w,e}
for every non-representable unit, and p^k | Q if h ≠ 1. Then every nonzero eigenvalue of f at m
is a p^k-th power in F(2^s)*, hence a (p^k R)-th power in F(2^d)*.

*Proof.* At c with λ_f(c) ≠ 0 all factors are nonzero, and λ_f(c) = ζ^{ℓ(c)} V(c) λ_h(c)^Q with
V(c) a p^k-th power in F(2^s)* by Lemma 1. The monomial is absorbed as in the sixth pilot:
f and V are even (λ(−c) = λ(c)) while ℓ(−c) = −ℓ(c), so ζ^{2ℓ(c)} = (λ_h(−c)/λ_h(c))^Q and
ζ^{ℓ(c)} = (y^h)^Q with y = λ_h(−c)/λ_h(c) (2h ≡ 1 mod m); hence λ_f(c) = V(c) · x^Q with
x = y^h λ_h(c) ∈ F(2^d)*. Now x^Q = λ_f(c)/V(c) ∈ F(2^s)*, so x^Q is both a Q-th power of F(2^d)*
and an R-th power; in a cyclic group that makes it an lcm(gcd(Q, 2^d − 1), R)-th power, and
p^k R divides that lcm since p^k | Q, p ∤ R. V(c) is a p^k R-th power in F(2^d)*. ∎

With h = 1 this is the splitting mechanism with exact exponents; with no units it is the power
mechanism. **Recursion on the power.** If h is itself confined to the p^j-th powers of F(2^s)*
(by this condition applied to h, re-centred), then λ_h^Q is a p^{v_p(Q) + j}-th power, and k may
be taken as min(v_p(Q) + j, v_p(2^s − 1)) instead of v_p(Q): a cube of a cube-confined rule is
ninth-power confined. Example: 212362513 = W³ with W = A4 + K8 + B4 + self cube-confined by the
half-Frobenius identity, so ninth powers at 37.

**Theorem B (half-Frobenius with bookkeeping).** Let f be symmetric, r ∈ {1, 2}, and

1. f(x^r, y^r) = U · C exactly, U = ∏ Φ_e(X_w)^{k_{w,e}} up to a monomial, C symmetric (the core);
2. N a product of orbit units O_v = ∏_{w ∈ Gv/±} t_w and P_{e,v} = ∏_{w ∈ Gv/±} Ψ_e(t_w) (G the
   rule's symmetry group), g a proper divisor of s, n = 2^g mod m, and
   B := C · N ≡ B(x^n, y^n) (mod x^m − 1, y^m − 1);
3. on each line {c : w·c ≡ 0} with w in an O_v of N, C restricts to a one-variable
   polynomial H(t) = t^i ∏ Ψ_e^{k_e} (representable e), with exponent A_H = 2i + Σ k_e A_e.

Let E_w be the exponents of U/N (U with its exponents, each t_w of N with −2, each Ψ_e(t_w) of N
with −A_e), and for each line of 3, with c₀ = (w₂, −w₁), let
A_line = A_H + Σ_{w'} E_{w'}(U) · 2^{a(w'·c₀)} over the directions w' of U with w'·c₀ ≢ 0
(each such w'·c₀ must be ±2^{a} mod m; a direction with w'·c₀ ≡ 0 and a positive t-exponent
makes f vanish on the line and is skipped). Let p^k divide (2^s − 1)/(2^g − 1), q'_p E_w for every
w, and q'_p A_line for every line. Then every nonzero eigenvalue of f at m is a p^k-th power in
F(2^s)*, hence a (p^k R)-th power in F(2^d)*. If U = N = 1, every eigenvalue lies in F(2^g) and f
is confined to the ((2^s − 1)/(2^g − 1))-th powers (the pure case).

*Proof.* Let c be a character. λ_f(rc) = λ_U(c) λ_C(c) and r is invertible mod m. If
λ_N(c) ≠ 0: λ_C(c) = λ_B(c)/λ_N(c) with λ_B(c) ∈ F(2^g) (λ_B(c)^{2^g} = λ_B(2^g c) = λ_B(c) by the
invariance), a ((2^s − 1)/(2^g − 1))-th power, hence a p^k-th power; and λ_U(c)/λ_N(c) is the
value of the unit product U/N, a p^k-th power by Lemma 1 (its monomial is absorbed as in
Theorem A, with h = B/N playing the role of h^Q: λ_f(rc) = V(c) · (monomial) · λ_B/λ_N, the
even-ness argument gives the monomial as a p^k-th power times something in F(2^s)*, and
F(2^s)* ∋ x^{p^k} = λ_f/(V λ_B/λ_N) is then itself a p^k R-th power as before). If λ_N(c) = 0,
c = k c₀ lies on a line of condition 3, λ_C(c) = H(t_k) with H(t_k)² = t_k^{A_H}, and every
unit of U takes the value (monomial) · t_{k w'·c₀}^{E/2} = (monomial) · t_k^{E 2^{a}/2}; so
λ_f(rc)² = (monomial)² t_k^{A_line}, a p^k-th power when p^k | q'_p A_line. ∎

**Corollary (the returned q).** `condition` returns R · ∏_p p^{k_p} with k_p the largest exponent
allowed by Theorem A or by the best Theorem-B witness, over the odd primes p < 20000 dividing
2^s − 1, and 1 if this is R alone. It also returns the lcm with the fifth pilot's exact twisted
pairs (f = C(x^a, y^a) C(x^b, y^b), b ≡ ±2^k a), which Theorems A and B do not cover. For f = h(x^p,
y^p) with p | m it recurses to h at m/p and lifts.

At 37 for the four targets (r = 2, witness N and exponents as `condition` finds them):

| rule | U (at r = 2) | N | E in direction (1, 0) | q |
| --- | --- | --- | --- | --- |
| 699738 | Ψ₅(a)²Ψ₅(b)² (a+b)² | t_x t_y · t_{xy} t_{x/y} | 2A₅ − 2 = 2²⁴ − 4, v₃ = 1 | 9R |
| 985232 | a⁸ b⁸ (a+b)² | same | 8 − 2 = 6, v₃ = 1 | 9R |
| 1431278 | Ψ₅(a)²Ψ₅(b)² | t_x t_y | 2A₅ − 2, v₃ = 1 | 9R |
| 1968276 | a⁸ b⁸ | t_x t_y | 6, v₃ = 1 | 9R |

(The direction (1, 1) has E = 0 for the first two: the (a + b)² of U cancels t_{xy}t_{x/y} of N.)
On the axes, where N vanishes, W and V restrict to (t + 1)² and t(t + 1)² at r = 1, i.e. to
Ψ₃⁴ and t²Ψ₃⁴ at r = 2, and the line exponents A_line (for 1431278: 2A₅ + 4 + 4A₃, which is
≡ 0 mod 9) impose nothing stronger; the diagonals of the W rules likewise. With q'_3 = 3 and
k ≤ v₃(513) = 3, k = 1 + 1 = 2 in every case: ninth powers, not 27th.

## 4. What `condition(f, m)` does

1. **Factorisation** (m-independent, cached): the sixth pilot's `unitpower.structure` gives the
   line factors of f by direction and cyclotomic index with multiplicities, and the core (the
   product of the two-dimensional factors). If some Φ_e(X_w) is present only partially (two of
   its irreducible factors with different multiplicities), the rule is treated as having no
   units and the whole of f is the core.
2. **Theorem A**: the exponents E_w per direction; the core must be an exact p^k-th power
   (`unitpower._core_root_ok`), unless it is 1; its root is scored recursively (depth ≤ 2).
3. **Theorem B**: the core is re-centred (it is symmetric up to a monomial), and for r ∈ {1, 2}
   the search multiplies C(x^r, y^r) by products of up to four orbit units O_v, P_{3,v}, P_{5,v}
   (v of radius ≤ 2) and P_{7,v}, P_{9,v} (v of radius 1), and by single units to powers up to
   36 (the fifth pilot's M^E certificates); for each product and each proper divisor g of s it
   tests invariance under (x, y) ↦ (x^{2^g}, y^{2^g}) mod m. The test is screened on the
   one-variable images x^{(p,q)} ↦ z^{v·(p,q)} mod z^m − 1 along two or three probe lines
   (ring homomorphisms commuting with the dilations, chosen so that no unit vanishes on them and
   inequivalent under the symmetries) by random projections, and every survivor is verified
   exactly on the dense m × m product; a verified witness is scored by Theorem B. Levels and
   witnesses that cannot beat the best score are skipped. The best witness over r, N and g wins.
4. **Lift and combine**: q_s = ∏ p^{k_p}, q = q_s R, lcm with twisted pairs and dilations.

Timing (one core, no other load): about 50 ms per rule at m = 37 for the atlas and 60-70 ms
for a radius-6 family rule; 15-25 ms at most other sizes; 70-90 ms at m = 299. Parameters are at
the top of `mechanism.py`.

## 5. Why 37, and what the condition predicts elsewhere

Three ingredients: an odd-index subfield inside the q-th powers (F(2⁹) at 37 inside the 27th
powers, because 9 | 2¹⁸ − 1 has 3-part 27 while 511 is prime to 3), the half-Frobenius pairing of
small shells under 2⁹ ≡ −6 (37 = 6² + 1), and rule 90's cube confinement (the fundamental unit of
Q(√37)). The **exponents** then decide between 3, 9 and 27: units t^3-like contribute k = 1 + 1,
units Ψ₃ = 1 + t contribute A₃ = 2²⁶ − 1 ≡ 0 mod 3 (so Φ₃(x)Φ₃(y)-multiples of the half-Frobenius
rules are ninth-power confined: that is the whole "rule-7 pattern" of the census, 7, 1023, 577,
17409, 1081345, …, which the condition claims with q = 9R or 27R), and F(2⁹)-valued cores
contribute 27.

Predictions the data does not cover, all checked against the eigenvalues where I could:

* **Radius 6 at 37** (my own census, `scratch/census6.json`, 128 chunks of the census method of
  `tools/census37.py`): among the 266 million new rules, 23,722 are cube-confined, 83 ninth-power
  confined and 29 of those 27th-power confined. `condition` claims 9 | q on **78 of the 83**, every
  claim verified; the five it does not claim are 8438150 = 4850 · Φ₃(xy)Φ₃(x/y), 43250486 =
  4850 · Φ₃(x)²Φ₃(y)², 10491524 = 4850 rotated by 45°, and two rules I could not explain,
  20982139 and 178279803, both with 4850's rotated class pattern but not 4850 times anything
  F(2⁹)-valued. Among the 78 are new mixed witnesses beyond the four targets' shapes, e.g.
  57515480 (units (a+b)², N = P₅(1,0)³ O(1,1)), 132692042 (N = P₃ P₇² O(1,1), q = 27R),
  133646261, 171949054, 231275595 (N = P₃ P₇ P₉, 27th powers), and 212362513 = W³.
* **Other sizes.** The four targets are claimed at no other m ≤ 301 (checked: the W and V identities
  need the shells (7, 5), (7, 7), (5, 5) paired by a dilation, which among m ≤ 301 happens only
  at 37), and are not confined at 101, 109, 185 or 197 by direct computation (`scratch/othersizes.log`).
  At other sizes `condition` claims what the fourth and fifth pilots' conditions claim (pure
  dilation invariance, splittings, the M^E certificates at 13, 21, 25, 35, 61) with exact
  exponents instead of the rule-90 bound, e.g. 5th powers at 35 and 11th powers at 61.
  `scratch/sweep_atlas_*.jsonl` lists every claim of the atlas grid with its witness.

## 6. 4850: what it is and what it is not

In a, b: F = s³ + P²s² + P³ + P² + P with s = a + b, P = ab (irreducible, the sixth pilot). In
the 45°-rotated coordinates (the rule 10491524, (x, y) ↦ (xy, x/y), a GL₂(Z/37) transport that
permutes the eigenvalues) it is a **cube plus a square**:

    F' = (ab)³ + (a + b)⁴ (1 + a)² (1 + b)² + (a + b)² = π³ + σ²(1 + σe)²,   σ = a + b, π = ab, e = (1+a)(1+b),

where π³ is a ninth power (π is a cube) and e is a ninth power (rule 7). Its eleven class values
have 27-adic logs (in units of 9) 2,1,1,2,0,1,0,1,1,1,2 on the classes (0,1),(1,1),…,(1,13): a
pattern that no product of units reproduces. What I excluded, all by computation at 37 with
the eigenvalues in `scratch/f18.py` (full discrete logs in F(2¹⁸)*):

1. **Unit times F(2⁹)-valued** — the half-Frobenius form, which is the only known source of
   27th powers. Since every cube is a power of t₁, "f · ∏_w t_w^{n_w} is F(2⁹)-valued" is the
   linear system Σ_w n_w 2^{a(w·c)} ≡ −log_t λ_f(c) (mod 171) over the lines c; it has **no
   solution** for symmetric orbit products of up to three orbits of radius ≤ 2 or two of radius
   ≤ 4 with any exponents (`scratch/orbsearch.py`), for any three directions among the 38 of
   (Z/37)² with any exponents (`scratch/alldirs.py`), nor modulo 19 or 9 alone (so not even
   F(2⁹) · μ₂₇-valued, `scratch/orbsearch_mod.py`); the same for F(2³) and F(2⁶). The only
   solutions of the 16-direction system are rank-deficiency noise covering six classes.
2. **g³ · U · F(2⁹)** for every g of radius ≤ 6 (268 million) and U among seven units
   (`scratch/cubesearch.py`): none.
3. **Twisted pairs and powers**: at 37 every residue is a power of 2, so C(x^a,y^a)C(x^b,y^b) ≡
   C^{2^α + 2^β} is a power of C; f ≡ C^e is a ninth-power statement about C itself unless
   9 | e, in which case C is one of the 3^{11} symmetric ninth roots, none sparse (the lightest
   symmetric cube root has 440 of 1369 terms, the next 452, against a mean of 678 and s.d. 46:
   chance level, `scratch/cuberoots.py`).
4. **Line certificates**: the lines k = 0, 1, 2 are exact cyclotomic products (t³, t²Ψ₅², t⁴Ψ₁₃),
   k = 3 is t²(a quintic factor of Ψ₃₁)(a septic factor of Ψ₁₂₇), and the lines k = 4, 5, 7,
   8, 10, 13 have irreducible factors of degrees 13, 13, 16, 19, 8 + 12 + 13 and 11 + 35
   (`scratch/linefactor.py`): no one-variable structure. The first consultation's identities
   g_k(x) g₄(x^n) ≡ cyclotomic hold for every cube-valued rule: 1 + ζ has order 37 · 87381 in
   F(2³⁶)*, so the cyclotomic units ⟨ζ, 1 + ζ⟩ = ⟨1 + ζ⟩ meet F(2¹⁸)* exactly in the cubes.
5. **Gauss sums**: the Gauss sums of the characters of order 9 of F₃₇* lie in F(2¹⁸) and are
   primitive 27th roots of unity (`scratch/gauss.py`), but 4850's eigenvalues have a nontrivial
   μ₁₉-part (ninth powers of F(2¹⁸)* are exactly F(2⁹)* · μ₃ · μ₁₉, and λ̄/λ has order 57 on most
   lines), so they are not Gauss sums times ninth powers.
6. **No other size**: 4850 is not 3-confined at 101, 109, 185 or 197; 109 and 185 are the other
   sizes with s = 18 (the only ones where 27 | 2^s − 1 and the same F(2¹⁸) arithmetic lives), and
   there rule 90 itself is not confined.

So 4850 is a genuinely two-dimensional ninth-power event with no multiplicative decomposition
into F(2⁹)-valued and unit-valued pieces of small complexity. My best guess at where to look
next is the cube-plus-square form, F' = N_{F(2⁵⁴)/F(2¹⁸)}(π + c) with c³ = Y², which transfers
the question to whether π + Y^{2/3} is a ninth power in F(2⁵⁴)*; I did not find a reason.

## 7. Checks

`proposal.py` prints 42 checks, all passing: the facts of section 2; the four exact
factorisations and the two half-Frobenius identities; the exponent computations; `condition` on
the six rules of `data/targets.json` with each claim verified against the eigenvalues; the
4850 family relations; the radius-6 census with every claim verified; samples of random
radius-6 rules and atlas rules at several sizes; the four targets at other sizes.

Beyond it (`scratch/`): the atlas grid, every odd m from 3 to 201 (`scratch/sweep_atlas_*.jsonl`,
each claim verified against the eigenvalues), the 125 ninth-power rules of radius ≤ 6 at 37, and
the regression against the three previous pilots' conditions on the atlas. The report lists the
numbers.

## 8. Lean

`proofs/LatticeProofs/Pilot.lean` (namespace `LatticeProofs.Pilot37c`, importing the fourth
pilot's `Cubes37`) proves, for the four radius-5 targets,

    period_r1968276_dvd : period 37 r1968276Offsets ∣ 29127
    period_r985232_dvd  : period 37 r985232Offsets  ∣ 29127
    period_r1431278_dvd : period 37 r1431278Offsets ∣ 29127
    period_r699738_dvd  : period 37 r699738Offsets  ∣ 29127

unconditionally (29127 = (2¹⁸ − 1)/9: every eigenvalue is a ninth power of F(2¹⁸)): the exact
factorisations (`r…_poly`, `linear_combination` certificates from `scratch/gen_pilot.py`), the
fourth pilot's identities and Frobenius permutations for W and V, rule 90's order 87381
(`Cubes37.r90_val`), the Ψ₅ exponent through t(z⁵) = t^{2²³} (`t_frob23`, `d5_identity`) and, on
the axes, the norm identity (t + 1)⁴ = t⁵¹⁰ (`t_norm`, from t^{2⁹} = t⁶ + t²). The report says
what built.

## 9. How it was found

The census logs of the four radius-5 targets coincide with the log pattern of rule 7 =
(1 + a)(1 + b) on every nonzero class, which said "rule 7 times a 27th-power-valued rule"; the
fourth pilot's tool then gave their witnesses, and tracking the exponents of each unit through
Ψ₅² = t^{2²³−1} and t_{j/2} = t_j^{1/2} gave 9 instead of 3. The negative results for 4850 came
from turning "unit × F(2⁹)" into linear algebra in the exponent of t₁ (section 6).

## 10. What it does not do

The mechanism is sufficient, not necessary, and bounded by its search (units of the line
content, orbit units of radius ≤ 2 with Ψ₃, Ψ₅, Ψ₇, Ψ₉, four factors, single units to the 36th
power, r ≤ 2). It does not explain 4850 or its images, and the two radius-6
rules 20982139 and 178279803 share 4850's rotated class pattern without being its multiples.
Rules that split into one-dimensional factors which are only partial cyclotomic products
(1825855: two of the six quintic factors of Φ₃₁ along each axis) are claimed only when the
half-Frobenius search succeeds on the whole rule, not through the factors' own values.
