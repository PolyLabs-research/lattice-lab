# Short version

The project's five "mechanisms" are, at the level of the group ring F2[Z/m × Z/m], one statement: **f is congruent to a power g^N of another rule modulo (x^m − 1, y^m − 1)**, in which case every eigenvalue is an N-th power and the period is P(g)/gcd(P(g), N). That single theorem is already in Lean in disguise (the twisted-power and cube files), it covers every prime q dividing 2^sord(m) − 1 and not just q = 3, and it makes sharp predictions at sizes the documents never test (fifth powers at m = 13, index-65 confinement at m = 37). The project should prove it once, register it for q ≠ 3, and then rebuild its chance model on Galois orbits, because the current notion of "coincidence" is not well defined. Below: three ranked suggestions, then the mis-posed question and the result I'd recheck.

Notation: m odd, ζ a primitive m-th root of unity in F(2^ord(m)), λ_{a,b}(g) = g(ζ^a, ζ^b), P(g, m) = odd part of the period = lcm of the orders of the nonzero λ_{a,b}(g) (the project's bridge theorem; I take it as given).

---

## 1. One theorem for all five mechanisms, then register it for primes q ≠ 3

**Claim A (proved, below).** Let m be odd and let f ≡ g^N in F2[x^±1, y^±1]/(x^m − 1, y^m − 1) for some rule g and integer N ≥ 1. Then for every (a, b), λ_{a,b}(f) = λ_{a,b}(g)^N, so λ_{a,b}(f) = 0 iff λ_{a,b}(g) = 0, and

  P(f, m) = P(g, m) / gcd(P(g, m), N).

*Proof.* Evaluation at (ζ^a, ζ^b) is a ring homomorphism F2[Z/m × Z/m] → F(2^ord(m)), so the congruence gives λ(f) = λ(g)^N. For a nonzero λ of order r, ord(λ^N) = r/gcd(r, N). For a prime ℓ, the ℓ-part of ord(λ^N) is ℓ^{max(v_ℓ(r) − v_ℓ(N), 0)}; taking the max over λ gives ℓ^{max(v_ℓ(P) − v_ℓ(N), 0)}, which is the ℓ-part of P/gcd(P, N). ∎

**Claim B (proved).** If d ≡ 2^k (mod m) then g(x^d, y^d) ≡ g^{2^k} in the group ring, because g(x^{2^k}, y^{2^k}) = g^{2^k} over GF(2) (Frobenius is additive) and x^d ≡ x^{2^k} mod x^m − 1. If d ≡ −2^k (mod m) and g is symmetric (g(1/x, 1/y) = g), the same holds. Hence:

- mechanism 2 (odd prime power g^q) is Claim A with N = q;
- mechanism 4 (twisted power g(x, y) g(x^d, y^d), d ≡ ±2^k) is Claim A with N = 1 + 2^k, and for symmetric g it is *literally* g^{1+2^k} in the group ring at that m — not a new mechanism;
- more generally f = ∏_i g(x^{d_i}, y^{d_i}) with d_i ≡ 2^{k_i} gives N = Σ 2^{k_i};
- mechanism 5 (f invariant under dilation by 2^k) is f ≡ f^{2^k}, so every nonzero eigenvalue lies in F(2^k)^* and P(f, m) divides 2^k − 1. (F(2^k)^* lies in the cubes of F(2^{2k})^* iff k is odd, since the index is 2^k + 1.)

The genuinely new case is d ≡ −2^k with g **not** symmetric: then λ(f) = λ(g) · λ(g*)^{2^k} with g* the inversion, and if −1 ∉ ⟨2⟩ mod m this is not a power of λ(g). I conjecture no confinement in general there; it is a place to look for a sixth mechanism rather than to expect one.

**Why now.** Round 4 is about to hard-code five steps into `atlas3.predict`, and the fifth pilot already found that "d = 3, which the census had not tried" explained three rules. Claim A says: don't enumerate d, enumerate N. The test "is f ≡ g^N mod (x^m − 1, y^m − 1) for some g, N" is a single group-ring computation, and it searches all primes q at once.

**What it establishes.** Every known confinement except the pure "small-field coincidences" becomes an instance of one Lean lemma with one proof, and the atlas gains confinements to 5th, 7th, 13th, ... powers that nobody has looked for.

**First concrete step.** Prove Claim A in Lean on top of `Bridge.lean` (it is the twisted-power proof with 1 + 2^k replaced by N; one afternoon). Then register these, which the documents do not settle:

- **m = 13** (2 is a primitive root; 2^12 − 1 = 4095 = 3²·5·7·13; powers of 2 mod 13 are k ↦ 2, 4, 8, 3, 6, 12, 11, 9, 5, 10, 7). For any **non-symmetric** g with P(g, 13) = 4095: f = g(x, y) g(x^10, y^10) has P(f, 13) = **819** (N = 1 + 2^10 = 1025, gcd = 5: every eigenvalue is a fifth power); f = g(x, y) g(x^5, y^5) has P(f, 13) = **455** (N = 513, gcd = 9); f = g(x, y) g(x^12, y^12) = g g* has P(f, 13) dividing **63** (N = 65 = 2^6 + 1, the norm to F(2^6)); f = g(x, y) g(x^3, y^3) has P(f, 13) = **4095** (N = 17, no confinement). Proved given P(g, 13) = 4095, which `eigen.py` should confirm for the chosen g.
- **m = 37** (2^36 − 1 = 3³·5·7·13·19·37·73·109; 2^6 ≡ 27). For non-symmetric g with P(g, 37) = 2^36 − 1: f = g(x, y) g(x^27, y^27) has P(f, 37) = (2^36 − 1)/**65** = 1,057,222,719. For **symmetric** g with P(g, 37) = 2^18 − 1 = 262143: f = g(x, y) g(x^6, y^6) has P(f, 37) = 262143/gcd(262143, 513) = **511** (N = 1 + 2^9; d = 6 ≡ −2^9), i.e. every eigenvalue drops into F(2^9). Since the same N = 513 is coprime to 2^18 − 1 at no other prime p where 2 is a primitive root and (p − 1)/2 = 18, this is specific to 37; at m = 13 the symmetric analogue g g(x^6, y^6) (6 ≡ 2^5, N = 33) gives P = P(g)/3.
- **A negative prediction (conjecture, testable):** at m = 37 no symmetric shell rule has all nonzero eigenvalues 7th powers *by any power mechanism*, because 1 + 2^k is never 0 mod 7 and no subfield of F(2^18) has index divisible by 7 (v_7(2^18 − 1) = 1 and 7 | 2^3 − 1). A census of 7th-power confinement at 37 therefore measures the chance model alone; with ~10 D4 × Galois orbits per rule, chance predicts about 7^{−10} ≈ 3.5 × 10^{−9} per rule — so any hit among 1,274 rules would be a new mechanism, not chance.

**What would show it was the wrong choice.** If the registered census of q-th-power confinement for q ∈ {5, 7, 13, 19} at m ≤ 61 finds nothing beyond Claim A's instances and the chance rate, the generalisation is correct but adds no new phenomena; that is still worth knowing but means the time should have gone to item 2. If a registered prediction above fails, either Claim A's hypothesis (the congruence) was not actually checked in the group ring, or the bridge theorem is being applied to a torus where it does not hold (see the recheck below).

---

## 2. Rebuild the chance model on Galois orbits before calling anything a coincidence

**Claim C (proved, elementary).** Let p be prime with 2 a primitive root mod p and f symmetric (f(1/x, 1/y) = f). The map (a, b) ↦ (2a, 2b) and (a, b) ↦ (−a, −b) generate the action of all of F_p^* on (Z/p)² \ {0} by scalars, so the eigenvalues of f fall into exactly **p + 1** Galois orbits, one per slope b/a ∈ P¹(F_p), each of size p − 1; and P(f, p) is the lcm of p + 1 orders, one per slope. For the 1D rule 90 (slope ∞ only) there is **one** orbit, so rule 90's eigenvalue is a q-th power "with probability 1/q" — which is why its confinement at 37, 101, 197 is common and why Fable's criterion has content, while a symmetric 2D rule with D4 symmetry has roughly (p + 5)/4 orbits and is confined by chance with probability about 3^{−(p+5)/4} (≈ 10^{−5} at p = 37, consistent with the quoted 1 in 20,000).

The null model the project should register is: **each D4 × Galois orbit is an independent uniform element of F(2^{sord})^*, except orbits tied by an identity** (axis orbits of a rule whose restriction f(x, 1) is a polynomial in t(x) inherit rule 90's confinement; (a, 0) and (0, a) coincide under x ↔ y; at composite m, orbits of different sizes live in different subfields and must be weighted accordingly). The 93.5% axis rate at m = 37 found by pilot 6 is a symptom of this, not a parameter to fit.

**Why now.** Open question 1 already says the model undercounts twice; open question 2 wants to "judge sizes below 30 by predicted chance". Both need the orbit count, not a per-class patch. And the census's "45 unexplained entries" cannot be adjudicated until "unexplained" means "probability under the orbit null below some registered threshold".

**What it establishes.** A number — the expected count of unexplained confinements at each (m, q) — that the census can be scored against, and a principled line between small-field coincidence and mechanism.

**First step.** Compute, for each odd m from 9 to 161 and each prime q | 2^sord(m) − 1, the number of D4 × Galois orbits of (Z/m)² \ {0} and the resulting expected number of chance-confined rules among the 1,274; register that table; then rerun the census. For m = 13: the orbits of F_13^* × D4 on (Z/13)² \ {0} number 7 for symmetric rules (slopes {0, ∞}, {1, −1}, and the pairs {s, 1/s, −s, −1/s} for s ∈ {2, 3, 4} give 3 more... I make it 5 slope classes but with the axis/diagonal subtleties the count should be done by machine; treat my 7 as a prediction to verify, not a fact). With 5–7 orbits, chance confinement to cubes at 13 is 3^{−5} to 3^{−7}, i.e. 0.6 to 5 rules out of 1,274 — not "mostly coincidence at 13" but a specific expected count to compare with the 16 the fifth pilot explained plus the remainder.

**What would show it was wrong.** If the orbit-null expected counts are off from the census by a factor of more than ~3 at three or more sizes above 30 (where no mechanism should operate), the eigenvalues are not behaving like independent uniform elements per orbit and the "generic elements generate" heuristic itself is wrong — which would be the most important discovery in the project.

---

## 3. Close the odd-part checks honestly, and separate "divides" from "equals"

The XOR law P(m) = 2^sord(m) − 1 is "checked by machine to 999 except ten". **Equality** of an order with 2^s − 1 can only be certified against the complete factorisation of 2^s − 1 (one has to show λ^{(2^s − 1)/ℓ} ≠ 1 for every prime ℓ); **divisibility** is free. I would guess the ten are exactly the m whose sord has 2^sord − 1 unfactored in the tables available, and the write-up should say which direction was checked at every m.

**Claim D (proved, one line).** For the square parity rule f = t(x) + t(y), t(x) = x + 1/x: λ_{a,0} = t(ζ^a), so rule 90's period divides P(f, m) for every odd m; λ_{a,a} = 0 (the rule is singular on both diagonals); and if 3 | m then λ_{a,m/3} = 1 + t(ζ^a), so rule 150's period at m divides P(f, m) too. In particular at m = 37 the 2D rule reaches 2^18 − 1 although its axis orbit does not; the off-axis orbits fill the index-3 gap. The documents never record which orbit supplies each prime factor of the bound; `eigen.py` can, and that is the right data for whoever eventually attacks "why generic rules reach the bound".

**Why now.** The XOR and triangle laws are the project's showpieces and the one unproved part is this. A stated "checked to 999" with an unstated meaning of "checked" is the kind of thing a referee will ask about first.

**First step.** For each of the ten, record sord(m), the known partial factorisation of 2^sord − 1, and whether the cofactor is a proven prime; where it is, the check completes immediately. Also reconcile the project's list of m at which rule 90 is confined with the classical tables (Martin–Odlyzko–Wolfram 1984 tabulate rule 90's period Π_n and its exceptions; I recall 37 and 101 among them but have not verified the full list and would not register it from memory).

**What would show it was wrong.** If all ten turn out already complete and the write-up merely mislabels them, this was bookkeeping. If one of the ten is a genuine counterexample (P(m) < 2^sord(m) − 1 for the XOR rule), then Claim C's orbit count at that m should show why — and if it doesn't, the heuristic is wrong.

---

## The open question I think is mis-posed

**"Why a non-confined rule reaches the full bound."** As stated it is a tautology: "confined" is defined as "the eigenvalues lie in a proper subgroup of F(2^sord)^*", and "reaches the full bound" is the negation. The content is in the word *generic*, and the honest version is an Artin-type statement ("for a rule with k Galois orbits of eigenvalues, the probability that all lie in the index-q subgroup is q^{−k}, corrected for identities"), which is not a theorem anyone will prove, but is a null model that can be registered and tested (suggestion 2). Relatedly, "coincidence" in open question 1 is not a property of a rule-size pair — ChatGPT's certificate shows every confinement is an identity (f^{N} idempotent in the group ring), so "unexplained" can only mean "no certificate of small description length". The project should fix a measure (degree of g and size of N in f ≡ g^N, or number of rule-90/Ψ factors in the unit) and report it, instead of the mechanism/coincidence dichotomy.

## The established result I would check again

**"Period = lcm of eigenvalue orders (odd tori); even sizes reduce to odd parts; the torus models agree with the atlas's engines at every size checked."** Not because I doubt the Lean statement, but because of the gap between it and what the engines measure. On an odd torus the rule matrix is semisimple (x^m − 1 is separable in characteristic 2), so the lcm theorem is about the *eventual* period of the full linear map, with transient exactly 1 when there is a zero eigenvalue — and the square parity rule has zero eigenvalues on both diagonals at every odd m (Claim D). An engine that reports the period of the orbit of a particular initial configuration measures the lcm over only those eigencomponents present in that configuration; a single random soup contains every component with probability about 1 − 2^{−(dimension of each eigenspace)}, which is fine for the bulk but can miss a one-dimensional eigenspace with probability 1/2 — and on an *even* torus the Jordan blocks make transients long and configuration-dependent. So the two things to re-verify by machine: (i) that every "period" in the ledgers (rounds 1–3, the census, `eigen.py`'s agreement with "11,662 exact records") is the period of the linear map, not of a sampled orbit, or if sampled, with how many soups; and (ii) that the Lean torus models and the engines agree on the definition at even n, where "P(2^v m) = 2^v P(m)" is a statement about eventual periods. If a ledger period was ever taken from one soup, the registered confirmations are slightly weaker than stated, and a confinement-looking undercount at a small m could be a missed eigencomponent rather than a coincidence — which would also bear on item 1.

A second, smaller recheck: the hexagon result is listed as "proved for every even n", but its 2-part theorem (`HexTwoPart.lean`) is stated for odd m ≥ 5; the cases n = 2^v·1 and 2^v·3 should be either covered by a finite check or excluded from the claim.
