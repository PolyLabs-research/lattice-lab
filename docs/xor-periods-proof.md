# The XOR period law: what is proved, and what is not

The law, found by Kepler from LatticeLife runs and tested in two pre-registered rounds
([xor-periods.md](xor-periods.md)): for B1357/S1357 on the n x n torus, the longest period is

    P(n) = 2^v(n) * (2^sord(n) - 1)        (n not a power of 2)

where 2^v(n) is the largest power of 2 dividing n, N = n / 2^v(n) is its odd part, and sord(n),
the suborder of 2, is the least j >= 1 with 2^j = +-1 (mod N). Every soup dies when n is a power
of 2.

| Claim | Status |
| --- | --- |
| P(n) divides the law's value, for every n | **proved** (Theorem 2, 4) |
| Transients: exactly 1 for odd n; at most 2^v(n) for even n; tori of side 2^k die after exactly 2^(k-1) generations | **proved** (Theorems 2, 3, 4) |
| Even sizes reduce to odd: P(2^k N) = 2^k P(N) for odd N > 1 | **proved** (Theorem 4) |
| So the law holds for every n if and only if it holds for every odd n | **proved** |
| Odd n: P(N) is a multiple of rule 90's period, so the law holds wherever rule 90 meets its own bound, and wherever 2^sord(N) - 1 is prime | **proved** (Theorem 5) |
| Odd n in general: the eigenvalues generate F(2^s)^* | **open**; checked by machine for every odd N up to 999, completely for 489 of the 499 (section 7) |

So the law is now a theorem for every n whose odd part is at most 999, except ten odd parts
(529, 587, 719, 827, 839, 859, 883, 947, 983 and 991) where a large factor of 2^s - 1 could not
be factored here: an infinite set of sizes. It is also a theorem for every n whose odd part is
one where rule 90 meets its bound. What remains is a statement about multiplicative groups of
finite fields that the analogous one-dimensional problem, rule 90's exact period, has also
resisted; section 6 says why.

Everything below is over GF(2), where 1 + 1 = 0 and minus is plus.

## 1. Setup

A configuration on the n x n torus is a polynomial in x and y modulo x^n - 1 and y^n - 1: the
cell (i, j) is the monomial x^i y^j. Call this ring R_n. A cell's next state is the parity of its
eight neighbours, so one generation multiplies a configuration by

    tau = (1 + x + 1/x)(1 + y + 1/y) - 1 = c(x) + c(y) + c(x) c(y),   c(x) = x + 1/x.

From a single live cell the state at generation t is tau^t. Every configuration f evolves as
f tau^t, and R_n is commutative, so if tau^(t0 + p) = tau^t0 then f tau^(t0 + p) = f tau^t0 for
every f.

**Lemma 1.** The torus's longest period and longest transient are those of the single cell: the
eventual period and the transient of the powers of tau in R_n.

*Odd n.* Then x^n - 1 has no repeated factors, and evaluating at pairs (alpha, beta) of n-th
roots of unity (in an extension of GF(2)) identifies R_n with functions on those pairs. So tau^t
is determined by the eigenvalues

    tau(alpha, beta) = c_alpha + c_beta + c_alpha c_beta,      c_alpha = alpha + 1/alpha,

and the period of tau is the least common multiple of the multiplicative orders of the nonzero
eigenvalues. All of them lie in one field (Theorem 2), whose multiplicative group is cyclic, so
the period is the order of the group they generate.

## 2. Odd n: the upper bound and the transient

**Theorem 2.** For odd n with s = sord(n), every run is periodic from generation 1 on, with a
period dividing 2^s - 1. The transient is exactly 1.

*Proof.* Squaring is additive in characteristic 2, so tau^(2^j) is tau with x, y replaced by
x^(2^j), y^(2^j). With 2^s = +-1 (mod n) and x^n = 1, x^(2^s) = x^(+-1), and c is unchanged by
x -> 1/x, so tau^(2^s) = tau. Hence tau^(1 + (2^s - 1)) = tau^1: periodic from generation 1 with
a period dividing 2^s - 1. Since c_1 = 1 + 1 = 0, the eigenvalue at alpha = beta = 1 is
tau(1, 1) = 0: tau is not a unit, the single cell itself is not on a cycle, and the transient is
exactly 1. In the language of Lemma 1, every eigenvalue z satisfies z^(2^s) = z, so
the nonzero ones lie in F(2^s). []

This is McLaughlin's observation that generation 2 always recurs, and the bound Martin, Odlyzko
and Wolfram proved for rule 90, whose eigenvalues are c_alpha (the line beta = 1 below).

## 3. Powers of 2

**Theorem 3.** On a torus of side n = 2^k (k >= 1) every configuration dies, by generation
2^(k-1), and a single cell takes exactly that long.

*Proof.* Here x^n - 1 = (x - 1)^n, so x = 1 + e with e^n = 0, and c(x) = x + 1/x = e^2/(1 + e):
e^2 times a unit. So tau = c + c' + c c' with c = e1^2 u1, c' = e2^2 u2. Then
tau^(2^(k-1)) = c^(2^(k-1)) + c'^(2^(k-1)) + (c c')^(2^(k-1)), and every term contains
e1^(2^k) or e2^(2^k), which are 0. For the exact time, write 2^(k-1) - 1 = 1 + 2 + ... +
2^(k-2) and expand tau^(2^(k-1) - 1) as the product of the tau^(2^i): the only term free of e2
is c^(2^(k-1) - 1) = e1^(2^k - 2) times a unit, which is not 0. []

## 4. Even sizes reduce to odd ones

**Theorem 4.** For n = 2^k N with N odd, N > 1 and k >= 1: P(n) = 2^k P(N), and the transient is
at most 2^k.

*Proof.* Pick a with a = 1 (mod N) and a = 0 (mod 2^k), and put x^ = x^a, e1 = x / x^ - 1, and
likewise y^, e2. Then (x^)^N = 1; x / x^ is a power of x^N, whose 2^k-th power is x^n = 1, so
e1^(2^k) = 0; and the monomials (x^)^i (y^)^j e1^u e2^v (i, j < N; u, v < 2^k) are n^2 elements
that span R_n (x^ is a power of x, and x = x^ (1 + e1)), as many as its dimension, so they are a
basis:

    R_n = R_N [e1, e2] / (e1^(2^k), e2^(2^k)),     x = x^ (1 + e1),  y = y^ (1 + e2).

Write tau = tau^ + D, where tau^ is the odd torus's tau (in x^, y^) and D lies in the ideal of e1
and e2. In characteristic 2, D^(2^k) is a sum of 2^k-th powers of terms each containing e1 or e2,
so D^(2^k) = 0, and tau^(2^k) = tau^^(2^k).

*Upper bound.* By Theorem 2, tau^^(1 + P(N)) = tau^, so tau^(2^k (1 + P(N))) = tau^(2^k), and
multiplying through, tau^(t + 2^k P(N)) = tau^t for every t >= 2^k: the transient is at most
2^k and the period divides 2^k P(N).

*Lower bound.* Projecting (e1 = e2 = 0) sends tau to tau^, so P(N) divides P(n). The divisors of
2^k P(N) that P(N) divides are 2^i P(N), so it remains to show the period does not divide
2^(k-1) P(N). Since (1 + e1)^(-1) = 1 + e1 + e1^2 + ..., c(x) = c^ + c^ e1 + (terms in e1^2
and higher), where c^ = x^ + 1/x^; so, with d1 and d2 the coefficients of e1 and e2 in D, the
coefficient of e1 e2 is c^ c'^ (it comes only from the product c(x) c(y)), and

    D^(2^(k-1)) = d1^(2^(k-1)) e1^(2^(k-1)) + d2^(2^(k-1)) e2^(2^(k-1)) + (c^ c'^)^(2^(k-1)) (e1 e2)^(2^(k-1)),

all other terms vanishing. By the binomial theorem, tau^t = sum over i < 2^k of C(t, i) tau^^(t-i)
D^i. Take t large with t = 0 (mod 2^k), and t' = t + 2^(k-1) P(N), so t' = 2^(k-1) (mod 2^k)
since P(N) is odd. By Lucas's theorem, C(t, i) is even for 0 < i < 2^k, and C(t', i) is odd for
i < 2^k only at i = 0 and i = 2^(k-1). So, at an eigenvalue where tau^ is nonzero (and its powers
repeat with period dividing P(N)),

    tau^t' - tau^t = tau^^(t - 2^(k-1)) D^(2^(k-1)).

At the pair alpha = beta, alpha != 1 (it exists because N > 1), tau^ = c_alpha^2 != 0 and
c^ c'^ = c_alpha^2 != 0, so this is not zero. The period is therefore 2^k P(N). []

So the law holds for every n exactly when it holds for every odd n. This is the two-dimensional
counterpart of Martin, Odlyzko and Wolfram's P(2N) = 2 P(N) for rule 90.

## 5. Odd sizes: what rule 90 gives

**Theorem 5.** For odd N, rule 90's period on the N-cycle divides P(N), and P(N) = 2^s - 1
whenever rule 90's period is 2^s - 1, or 2^s - 1 is prime (N > 3).

*Proof.* The eigenvalues with beta = 1 are tau(alpha, 1) = c_alpha + 0 + 0 = c_alpha, rule 90's
own; equivalently, configurations constant along one axis evolve as rule 90. So the group the 2D
eigenvalues generate contains rule 90's, and its order P(N) is a multiple of rule 90's period;
it divides 2^s - 1 by Theorem 2. If 2^s - 1 is prime, any eigenvalue other than 0 and 1 generates
F(2^s)^*, and c_alpha is neither for alpha of order N > 3. []

In practice rule 90 meets its bound at most odd N (at 439 of the 489 odd N up to 999 whose
2^s - 1 was fully factored, section 7), so most sizes are settled here. The rest are the sizes where rule
90 falls short: 37, 95, 101, 111, 141, 197, 199, 203, ... (section 7).

## 6. The open core

**Conjecture.** For every odd N > 1, the eigenvalues tau(alpha, beta), alpha, beta ranging over
the N-th roots of unity, generate the whole multiplicative group of F(2^s), s = sord(N).

By Theorems 2 to 5 this is equivalent to the law for all n. Some equivalent forms:

- For every prime r dividing 2^s - 1, some eigenvalue is not an r-th power in F(2^s). Only the
  primes at which every rule-90 eigenvalue c_alpha is an r-th power need checking.
- With a = 1/(1 + alpha), b = 1/(1 + beta): a(a + 1) = 1/c_alpha and
  tau = (t^2 + t + 1) c_alpha c_beta with t = a + b. So the conjecture says the elements a(a + 1)
  and (a + b)^2 + (a + b) + 1, for a, b roots of (1 + a)^N + a^N, generate F(2^s)^*.
- Over F(4) = GF(2)(omega), the numerator of tau factors: (1 + x + x^2)(1 + y + y^2) + xy =
  L(x, y) L'(x, y) with L = (x + omega)(y + omega) + omega and L' its conjugate. The 2D rule's
  rescues at the prime 3 (all of rule 90's shortfalls but one up to 200 are at 3) presumably come
  from this structure; no proof along these lines was found.

Why it resists the usual tools. The eigenvalues are values of a fixed rational function at the
points of the subgroup of N-th roots of unity, a tiny subset of F(2^m), m = ord_N(2). Weil-type
bounds on character sums, applied through that subgroup, control the count of r-th powers only
when 2^m is below roughly N^2 / 16, which fails for almost every N. And for rule 90, whose
eigenvalue set is smaller, the same question has no general answer in the sources consulted: its
period falls short of 2^s - 1 at sizes such as 37 and 199, with no known rule for when. The 2D
rule has about N^2 / 4 eigenvalues against rule 90's N / 2, which is why it can meet the bound
where rule 90 does not, but turning "many" into "enough, always" needs an idea not found here.

## 7. What was checked by machine

- **Every odd N from 3 to 999**, with `examples/xor-periods-proof/check_odd.py`, results in
  `examples/xor-periods-proof/results.jsonl`. It works in GF(2)[z]/(z^N - 1), which for odd N is
  a product of fields, one per Frobenius orbit of N-th roots of unity: the element
  T = tau(z^p, z^q) carries the eigenvalues of the whole line (p, q) as its components, and
  some component is a nonzero non-r-th power exactly when T^((2^s - 1)/r) differs from
  T^(2^s - 1), the idempotent of T's support. No field has to be constructed and nothing has to
  be factored except 2^s - 1, through its cyclotomic parts Phi_d(2).
  - **No size has an unresolved prime.** For 489 of the 499 sizes the factorisation of
    2^s - 1 is complete, so the law is proved there. For the other ten (529, 587, 719, 827,
    839, 859, 883, 947, 983 and 991), 2^s - 1 has a composite cofactor of 55 to 138 digits that
    was not factored here (the Cunningham tables have them, but they could not be reached from
    this environment); there every prime below 10^6 was checked.
  - **Rule 90 falls short at 50 of the 499 sizes**, by the primes 3 (36 sizes), 7 (7), 5 (5),
    11 and 13 (2 each), 29, 41, 233 and 397 (1 each); at 203, 407, 655 and 995 by two or three
    primes at once. At every one a 2D line supplies the missing non-residue, most often one of
    the first few lines (1, q).
  - The method was checked first: it reproduced, size for size, the 260 results of a slower
    independent implementation (explicit fields F(2^m) and a primitive N-th root of unity), and
    its fast carry-less multiplication agreed with schoolbook multiplication on 300 random
    products.
- **Round 2's exact periods** (n = 3 to 200, `examples/xor-periods-algebra`) satisfy Theorem 4 at
  all 93 even sizes with an odd part above 1, Theorem 3 at every power of 2, and Theorem 2 at
  every odd size.
- The proofs above were checked against those numbers, not by a proof assistant.

Combining Theorem 4 with the scan, P(n) = 2^v(n) (2^sord(n) - 1) is proved for every n, not a
power of 2, whose odd part is at most 999 and not one of those ten.

## References

- O. Martin, A. Odlyzko and S. Wolfram, Algebraic properties of cellular automata, Comm. Math.
  Phys. 93 (1984) 219-258: rule 90's period bound and P(2N) = 2 P(N).
- J. McLaughlin, periods of this rule on odd tori up to 23, as a conjecture (see
  [xor-periods.md](xor-periods.md#sources)).
- A. Vadali and A. Turner (2025): equality of 1D and 2D cycle lengths for the four-neighbour
  analogue.
