# A blind atlas: periods of 42 linear rules on three lattices

**Status: judged, two registered rounds.**

**Round 1** asked Kepler for period laws for every rule built from symmetric neighbour shells on
the square, hexagonal and triangular lattices: 42 rules, 38 of which nobody here had studied.
- Each law was fitted on tori up to 60, and every law Kepler proposed was registered with its
  value at each new size before any new size was computed.
- The new sizes were checked exactly: 1,930 (rule, size) pairs up to n = 160.
- **For all 34 rules that got a law, a registered law was the exact period at every test size.
  No rule had all its laws refuted.**
- Kepler's top-ranked law held for 19 rules; for the other 15, a tied rival registered alongside
  it held instead. Eight rules got no law.

Afterwards, a pattern was noticed: the polynomials sort the laws into two families.
- A rule whose polynomial splits into passes of 1D rules along lattice directions has a 1D
  rule's period, shortfalls included. On the triangle, the test is whether its matrix's square
  splits.
- A rule that does not split reaches the full bound.

**Round 2** registered that pattern ([below](#round-2-the-pattern-registered)) and made 5,048
exact checks:
- **A.** All 34 round-1 laws held at all 624 new sizes, chosen where the families part, up to
  n = 400. This includes odd parts 197 and 199, where rule 90 falls short by factors of 3 and 7.
- **B.** The pattern predicted the periods of 116 square rules from their factorisation alone,
  112 of them never computed before. **106 of the 113 predictions held, and 7 failed, so the
  pattern as registered is refuted.**

What the failures show, analysed afterwards:
- **Three of the failed rules break it the same way.** They are confined without splitting:
  two are perfect cubes, (N4 + self)^3 and N4^3, and one is a rule in x^3, y^3. After the first
  failure of each kind, the sizes and periods where these three must fail were committed before
  those sizes were computed. They failed at exactly those 55 sizes, with those periods, and
  nowhere else.
- **The other four** each fail at one small size (n = 13 or 37) and hold everywhere else. They
  are not explained.

## The rules

A cell's next state is the parity of the live cells in a set of shells, with or without the cell
itself (`examples/linear-atlas/engine.py`). Every such rule is linear over GF(2).

| Lattice | Shells |
| --- | --- |
| square | N4 (the four nearest), D4 (the four diagonals), A4 (the four at distance 2) |
| hexagon | H1 (the six nearest), H2 (the six at distance sqrt 3), H3 (the six at distance 2) |
| triangle | E (the three across an edge), VO (the three across a vertex with the opposite orientation), VS (the six that share a vertex and the orientation) |

Each lattice has 7 non-empty sets of shells, each with and without the cell: 14 rules per
lattice. Four had been studied before and are kept apart below: square N4+D4 (B1357/S1357,
[xor-periods.md](xor-periods.md)), hexagon H1 (B135/S135), and triangle E (B13/S13) and E+VO+VS
(B1,3,...,11/S1,3,...,11) ([parity-lattices.md](parity-lattices.md)). The other 38 are blind.

Notation:
- n = 2^v(n) m with m odd;
- sord(n) is the suborder of 2: the least j with 2^j = +-1 mod m;
- P90(n) and P150(n) are rules 90's and 150's periods on a ring of n cells (Kepler 0af9b28's
  vocabulary);
- odd(n) = m.

## Engine, validation, discovery

**The engine** treats each rule as multiplication in the group ring F2[T] of the torus's
translations. On the triangle it is a 2 x 2 matrix over F2[T], for the up and down cells. The
period is that of the matrix M: the least p with M^(4n + p) = M^(4n). Every period divides a bound
C = 2^(e+2) (2^(km) - 1); C's primes come from the cyclotomic factors of 2^(km) - 1, so
C is never factored. `Torus.check(p)` decides whether p is the period: p must divide C, M must
repeat after p, and M must not repeat after p/q for any prime q of C.

**Validation** (`validate.py`, `validation.json`), before anything was trusted:
- The eight rules LatticeLife can run, compared with LatticeLife's own simulation at small sizes:
  58 of 58 pairs agree.
- All 42 rules, compared with a direct simulation from the shells' offsets in LatticeLife's
  (row, column) grid, which never uses a group ring: 154 of 154 pairs agree.

**Discovery** (`discover.py`) computed each rule's exact period on every torus from 8 to 60:
- even n only on the hexagon and triangle, whose tori need an even side;
- below 8, a distance-2 shell folds onto itself.

Kepler's `find_integer_laws` was then run on three subsets in a fixed order: all n, then n not a
power of 2, then odd part at least 5. The proposal is the first subset with a law confirmed by at
least 10 points. Every law on that subset confirmed as often is registered with it, so tied rivals
were registered too. This rule was fixed before any law was seen. The outputs are
`discovery.jsonl` and `proposals.json`.

## Registration

`study.py` (built on `lattice_lab.study`) wrote 42 predictions to `ledger.jsonl`, one per rule.
Each gives every registered law's value at every test size, recomputed from the discovery data
by the same search. The registration was committed and pushed in `310819d` at
2026-10-17T21:16:36Z, before any test size was computed:

- **Test sizes:** every n from 61 to 140 on the square, and every even n from 62 to 160 on the
  hexagon and triangle, within the subset the law was found on.
- **Decision:** a law is confirmed when its value is the exact period at every test size, and
  refuted at the first size where it is not.

The run took six minutes. Results are in `records.jsonl`; the verdict, appended at 21:22:49Z, is
in the ledger. `uv run lattice-lab verify --lab examples/linear-atlas` passes: the hash chain is
intact, and the predictions precede the run.

## Result

**The square** (77 to 80 sizes per rule, n = 61 to 140). Each rule got a single law.

| Rule | Law | Outcome |
| --- | --- | --- |
| N4, D4 | P90(n) | confirmed at all 80 |
| N4+D4+self (B1357/S02468), D4+A4+self | P150(n) | confirmed at all 80 |
| N4+self, D4+self, N4+D4 (studied), D4+A4, N4+D4+A4, N4+D4+A4+self | 2^v(n) (2^sord(n) - 1) | confirmed at all 77 or 78 |
| A4, A4+self, N4+A4, N4+A4+self | none | - |

**The hexagon** (47 or 48 sizes per rule). Each rule got two or three tied laws. Two of them,
2 P90(n) and 2 * 2^v(n) P90(odd(n)), are equal at every test size.

| Rule | Law that held | Refuted |
| --- | --- | --- |
| H1 (studied), H2 | 2 P90(n) | 2 * 2^v(n) (2^sord(n) - 1), at 74 and 148 |
| H3 | P90(n) | 2^v(n) (2^sord(n) - 1), at 74 and 148 |
| H2+H3+self | 2 P150(n), and its other form 2 * 2^v(n) P150(odd(n)) | (none) |
| H1+self, H2+self, H1+H2, H1+H2+self, H2+H3, H1+H2+H3, H1+H2+H3+self | 2 * 2^v(n) (2^sord(n) - 1) | 2 P90(n), at 74 and 148 |
| H3+self | 2^v(n) (2^sord(n) - 1) | P90(n), at 74 and 148 |
| H1+H3, H1+H3+self | none | - |

**The triangle** (47 to 50 sizes per rule).

| Rule | Law that held | Refuted |
| --- | --- | --- |
| E+self, VO+self, VS | 2 P90(n), or P90(n) for VO+self and VS | the formula, at 74 and 148 |
| E (studied), E+VO, E+VO+self, E+VO+VS (studied), E+VO+VS+self | 2 * 2^v(n) (2^sord(n) - 1) | 2 P90(n), at 74 and 148 |
| VO, VS+self | 2^v(n) (2^sord(n) - 1) | P90(n), at 74 and 148 |
| VO+VS | the constant 2 | gcd(n, 31), gcd(n, 37), gcd(n, 41) variants |
| VO+VS+self | the constant 1 (the torus dies) | the same variants |
| E+VS, E+VS+self | none | - |

| | First law held | A rival held | Every law refuted | No law |
| --- | --- | --- | --- | --- |
| blind (38) | 17 | 13 | 0 | 8 |
| studied (4) | 2 | 2 | 0 | 0 |

In all, 85 laws were registered: 43 were confirmed and 42 refuted. Every refuted law had a
confirmed rival registered for the same rule. The refuted laws were:
- 30 rule-90 laws, a factor of 3 short at 74 and 148;
- 6 formulas, 3 times too large there;
- 6 gcd variants of the triangle's constants.

The four studied rules came out as the earlier studies found. The hexagon's law is a theorem, and
the square and triangle laws had been machine-checked.

### Which sizes decide

The two families agree at most sizes. They part only where rule 90 falls short of its bound,
which is at odd parts 37, 95, 101 and 111 within these ranges.
- **Square:** the test range holds four such sizes, n = 74, 95, 101 and 111.
- **Hexagon and triangle:** the even sizes up to 160 hold two, n = 74 and 148, both with odd part 37.

Each rule's family therefore rests on two or four decisive sizes, not on its 47 to 80. The
registered laws were also confirmed at the other sizes, but there all the candidates agree. On the
square, rule 150's period differs from the formula at 14 of the 80 test sizes. So P150(n) against
the formula is decided far more often.

### Known answers, as a check

- **Square N4 is Vadali and Turner's sigma automaton.** They proved its cycle lengths equal rule
  90's (2025). Kepler's blind law, P90(n), is their theorem.
- **D4 = (x + 1/x)(y + 1/y)** is a pass of rule 90 along each axis. On F2[Z_n] (x) F2[Z_n] that is
  sigma (x) sigma. Over GF(2), X (x) X = Y (x) Y forces X = Y: at an entry (a, b) where Y is 1,
  X_ab^2 = 1, so X_kl = X_ab X_kl = Y_ab Y_kl = Y_kl. So sigma^(t+p) (x) sigma^(t+p) =
  sigma^t (x) sigma^t exactly when sigma^(t+p) = sigma^t. **D4's period is P90(n) for every n**,
  and its transient is rule 90's.
- **N4+D4+self = (1 + x + 1/x)(1 + y + 1/y)** is rule 150 in each axis. By the same argument, **its
  period is P150(n) for every n.** This is LatticeLife's B1357/S02468.
- **H3 = H1^2.** By Frobenius, f(x)^2 = f(x^2) over GF(2), and H3's shell is H1's doubled. This is
  the identity behind the hexagon theorem: two H1 generations are three passes of rule 90.
  M^2's period is p / gcd(p, 2), so H3's period is half of H1's. **That is P90(n) for every even
  n, by the hexagon theorem.**

So for 4 of the 30 blind rules with a law (N4, D4, N4+D4+self and H3), the answer was already
a theorem or follows in a line from one. Kepler's laws agree with all four. That is a check on
the method, not a discovery.

## Not registered: the polynomials sort the rules into the two families

A rule on the square or hexagon is a Laurent polynomial f(x, y) over GF(2). Call a factor
one-dimensional if it is a polynomial g(u) in a single monomial u = x^a y^b, which is one pass of a
1D linear rule along the direction (a, b). `factor.py` decides whether f has one. A factor's
Newton polygon is a Minkowski summand of f's (Ostrowski). A one-dimensional factor's polygon is a
segment along (a, b) of length deg g. So (a, b) must be the direction of an edge of f's polygon,
and deg g can be at most that edge's lattice length. That leaves finitely many candidates, and
all are tried. (The first version tried a fixed list of small directions and degrees; the
complete search gives the same answer for all 42 rules.) It divides out each factor it finds and
checks that the factors multiply back to f. A rule splits when only a monomial is left. On the
triangle, M^2 = s I for a polynomial s on the translation lattice for all 14 rules, and the test
is whether s splits. Output: `factors.json`.

| Splits into 1D passes | Law that held |
| --- | --- |
| square N4 (rule 60 along each diagonal), D4 (rule 90 along each axis) | P90(n) |
| square N4+D4+self (rule 150 along each axis), D4+A4+self (rule 150 along each diagonal) | P150(n) |
| hexagon H1, H2 (rule 60 along three directions), H3 (rule 90 along three) | 2 P90(n), P90(n) |
| hexagon H2+H3+self (rule 150 along three directions) | 2 P150(n) |
| triangle E+self, VO+self, VS (s is rule 60 or rule 90 along three directions) | 2 P90(n), P90(n) |

| Does not split | Law that held |
| --- | --- |
| 6 square rules, 8 hexagon rules, 7 triangle rules: every other rule with a non-constant law | the full bound, 2^v(n) (2^sord(n) - 1), times 2 for most hexagon and triangle rules |

**The pattern has no exception among the 32.** 11 rules split. Each has a 1D rule's period
and shares that rule's shortfalls; for the rule-90 ones, that means at 74 and 148, or at 74, 95,
101 and 111 on the square. 21 rules do not split, and each reaches the full bound at every one
of those sizes. These are the only rules with
a constant law:
- VO+VS has M^2 = I, so its period is 2;
- VO+VS+self has M^2 = 0, so the torus dies.

The square eight-neighbour rule's escape from rule 90's shortfalls, found in the
[earlier study](xor-periods.md) and checked by machine for odd parts up to 999, is one case of
this.

Two cautions:
- The pattern was noticed after the verdict, on the same data, so it is a hypothesis.
- Its evidence is the decisive sizes, two or four per rule.

**Why splitting should give the 1D period.** This is easy when the factors run along two axes
(D4, N4+D4+self above). It is the content of Vadali and Turner's theorem for N4, whose factors
run along the diagonals, and of the hexagon theorem for H1. **A rule-150 analogue of each
appears here as a conjecture:**
- square D4+A4+self, rule 150 along both diagonals, has period P150(n), confirmed at all 80 test
  sizes;
- hexagon H2+H3+self, rule 150 along all three directions, has period 2 P150(n), confirmed at
  all 47.

**Why not splitting should give the full bound** is open. It would say that the shortfall of rule
90, a property of particular cyclotomic factors, is inherited only by rules built from 1D passes.

## Not registered: the eight rules without a law

`factor.py` also checks which rules are quadratics in the lattice's nearest-neighbour rule R (N4,
H1 or E), as matrices on the 12 and 16 tori. Each of the eight is one:

| Rule | As a quadratic in R |
| --- | --- |
| square A4, A4+self | N4^2, (1 + N4)^2 |
| square N4+A4, N4+A4+self | N4 (1 + N4), 1 + N4 + N4^2 |
| hexagon H1+H3, H1+H3+self | H1 (1 + H1), 1 + H1 + H1^2 |
| triangle E+VS+self, E+VS | E (1 + E), 1 + E + E^2 |

- **The two squares are explained exactly.** M^2's period is p / gcd(p, 2). So A4's period is
  P90(n) halved when even, which the discovery data confirm at every size. Kepler has no
  "halve when even" term. On the hexagon and triangle the roots' periods are always even, so the
  squares there (H3, H3+self, VS, VS+self) did get laws.
- **R (1 + R) and 1 + R + R^2 are left open.** Their eigenvalues are lambda (1 + lambda) and
  1 + lambda + lambda^2, whose orders need not follow lambda's. For example, square N4 (1 + N4)
  has period lcm(P(N4), P(1 + N4)) at 44 of the 53 discovery sizes, and less at the other 9 (8,
  10, 12, 16, 20, 24, 32, 40, 48).

## Round 2: the pattern, registered

`examples/linear-atlas-2` (`atlas2.py`, `study.py`). Registered in `25425b2` and pushed at
2026-10-17T22:04:24Z, before any of these sizes or rules was computed. The run went from 22:04:37Z
to 23:22:52Z. Before registration, two things were done:
- `factor.py`'s search was made complete. It now tries every factor the Newton polygon allows,
  and gives the same classification for all 42 atlas rules.
- A faster exact check (`atlas2.Exact`: the proper-divisor tests share a product tree) was
  validated against round 1's. They agreed, reason for reason, on 225 round-1 values, including
  all 104 from records with a failed check.

Three (rule, size) pairs were computed while timing the engine, and their outcomes were seen
(all full bound). The registration records them, and the two among the test sizes (n = 394) are
excluded.

**Part A: the 34 atlas rules with a law.** Each was registered with the law its factorisation
picks from those Kepler proposed. In every case that was a round-1 survivor. The test sizes are
where rule 90's or rule 150's period differs from the full bound:
- **square:** the 28 such sizes from 141 to 303;
- **hexagon and triangle:** the 15 such even sizes, 190, 192, 202, 206, 208, 222, 242, 244, 268,
  282, 286, 296, 380, 394 and 398.

This covers the next rule-90 shortfalls, odd parts 95, 101, 111, 141, 197 and 199. At 199 the
shortfall is a factor of 7, not 3. **All 34 held at all 624 pairs:**
- 11 rules that split shared rule 90's or rule 150's shortfalls;
- 21 rules that do not split reached the full bound;
- 2 constants held.

**Part B: the pattern alone, on rules never computed.** The square gets three more shells: K8
(the eight cells at distance sqrt 5), B4 (four at 2 sqrt 2) and C4 (four at 3). That gives 112 new
rules, and the four atlas square rules without a law are added. At odd n each period is predicted
from the factorisation:

| Call | Prediction | Rules | Held |
| --- | --- | --- | --- |
| does not split completely | the full bound 2^sord(n) - 1 | 106 | **100** |
| splits, factors 1 + u only | P90(n) | 5 | **4** |
| splits, factors 1 + u + u^2 only | P150(n) | 1 (A4+B4+self, = (N4+D4+self)^2) | **1** |
| splits, one other factor | that symmetric 1D rule's period | 1 (N4+D4+A4+K8+B4+self, a five-cell rule along each axis) | **1** |
| factors of more than one kind | none: computed | 3 (C4, N4+A4+K8, D4+K8+B4) | - |

The test sizes are every odd n from 13 to 61 for the new rules, plus the 14 odd sizes from 63 to
203 where rule 90's or rule 150's period differs from the full bound. That is 4,307 checks, plus
117 periods computed for the three rules without a call. The rule was checked first against
round 1's discovery data: the 14 atlas square rules at every odd n from 9 to 59. It held at all of
them, including the four with no law, whose irregularity is only at even n. In the round, the
four atlas rules held at all 14 new sizes.

**Seven predictions failed:** 59 checks, all on the square.

| Rule | Failed at | What it is (found afterwards) |
| --- | --- | --- |
| N4+K8+C4 | 22 of 39 sizes | N4^3 |
| A4+K8+C4+self | 25 of 39 | (N4 + self)^3 |
| C4+self | 8 of 39 | (N4 + self)(x^3, y^3) |
| A4+C4, A4+C4+self | n = 13 only (period 7, not 63) | not explained |
| A4+K8+B4+C4+self | n = 13 only (21, not 63) | not explained |
| A4+K8+B4+self | n = 37 only (87381, rule 90's period, not 262143) | not explained |

### Two mechanisms the pattern missed

**Perfect cubes.** The first failure was A4+K8+C4+self at n = 197, at a third of the full bound.
Writing a = x + 1/x and b = y + 1/y, the shells are:
- N4 = a + b and A4 = a^2 + b^2;
- K8 = ab(a + b) and C4 = a^3 + a + b^3 + b.

So A4+K8+C4+self = (1 + a + b)^3 = (N4 + self)^3. Likewise N4+K8+C4 = N4^3; these are the only
two cubes among the 126 rules of the six shells.

At odd n, M is diagonalisable and its period is the lcm of its eigenvalues' orders. A cube's
eigenvalues are cubes, and ord(x^3) = ord(x) / gcd(ord(x), 3), so the period of g^3 is p /
gcd(p, 3), where p is g's period. Splitting into 1D passes is one way to confine every eigenvalue
to a proper subgroup. Being a cube is another, and the pattern did not see it, because a cube of
a rule that does not split does not split either.

**Dilation.** C4+self failed at n = 141, with 2^23 - 1 against the predicted 2^46 - 1. It is
(N4 + self)(x^3, y^3). When 3 divides n, x -> x^3 maps the n-torus's group ring onto the
n/3-torus's, and the whole ring is a free module of rank 9 over that image. So the rule has N4 +
self's period on the n/3 torus. At 141 that is the full bound of 47, 2^23 - 1. C4 alone,
which had no prediction, shows the same thing: it has P90(n), or P90(n/3) when 3 divides n, at
all 39 sizes.

**Both were written down before the evidence.** The sizes and periods where these three rules
must fail were committed in `cube-expectation.json`:
- for the cubes, at 22:57:09Z (`977f81d`), when only n = 197 and 199 had been computed for them;
- for the dilation, at 23:20:00Z (`cca8923`), before 30 of its 39 sizes. That included the
  multiples of 3 where it must fail and two, 33 and 57, where the smaller torus has the same
  bound, so it must not.

`analyse.py` checks every size of the three rules against these: **all 117 match**. That is 55
failures with the stated periods, and 62 sizes where the registered prediction held as expected.
This was not registered: it was written during the run, after a first failure of each kind.

**The four accidents** are at the smallest test size and at 37, with period 7, 21 and 87381.
Each rule reaches the full bound at every other size tested, including 95, 101, 111, 141, 197,
199 and 203, where rule 90 falls short.

Afterwards, `subfield.py` computed every eigenvalue directly in F(2^ord). That is a separate
calculation from the engine's, and it reproduces all four periods. Every shell rule is a
polynomial in a = x + 1/x and b = y + 1/y, so its eigenvalues are values at rule 90's
eigenvalues t_j = zeta^j + zeta^-j.

- **A4+C4 and A4+C4+self at n = 13 are explained.** Both are additively separable: q(a) + q(b)
  and 1 + q(a) + q(b), with q(t) = t^3 + t^2 + t. At n = 13 the t_j lie in F(64), and q sends
  every one of them into the subfield F(8). So every eigenvalue lies in F(8), and the period
  divides 7. The t_j form a single Galois orbit, so this is one coincidence, not many. A value
  that lands in a proper subfield of F(64) has odds of roughly 1 in 6, and the odds shrink
  exponentially as the field grows. That is a reason for accidents of this kind to occur at
  small sizes only.
- **A4+K8+B4+C4+self at 13** has only 14 distinct eigenvalues. All are cubes in F(64) (orders 1,
  7, 21), which is plausible by chance with so few.
- **A4+K8+B4+self at 37 is not chance.** All 172 distinct eigenvalues are cubes in F(2^18), as
  rule 90's are there, so there is structure. One candidate cause is that the rule splits on the
  37-torus but not on the plane, since exponents only matter modulo n. A search for a product of
  rule-90 values along linear forms (up to four factors, coefficients up to 3) found none, and a
  full search over the torus's changes of coordinates was too slow. It is open.

### What round 2 says about the pattern

As registered, the pattern is refuted. What survives is a sharper statement, found afterwards:

> A shell rule's period at odd n reaches the full bound unless something confines its eigenvalues:
> splitting into 1D passes, being a perfect odd power, being a dilation by a divisor of n, or
> (four times in 4,307 checks) something not yet identified at a small size.

- **It accounts for every failure of round 2** except those four accidents, and is consistent
  with every law of round 1 at its odd part.
- **Every mechanism in it is a theorem.** The open part is the claim that nothing else confines
  the eigenvalues.
- **The first two mechanisms are standard algebra.** The new part is the observation, across 154
  rules, that they are nearly the only ones. It is a conjecture, and the accidents show it is not
  yet exact.

## What this does and does not establish

- **Registered:** Kepler's period laws for 30 blind rules, each held exactly at every test size
  (47 to 80 per rule, n up to 160). For each rule, the registered set contained a law that held,
  and the test decided which. **No rule had all its laws refuted, and none needed a law found
  afterwards.**
- **Kepler's first choice is not the point.** It was wrong for 13 of the 30 blind rules. It
  ranks the shorter 1D-period law first, and the data up to 60 cannot tell the two families
  apart on the hexagon and triangle (as in the
  [rediscovery test](parity-lattices.md#kepler-with-a-wider-vocabulary)). The method works
  because tied rivals are registered and the test includes the sizes where they part.
- **Thin where it decided, in round 1.** The family of each hexagon and triangle rule rested on
  n = 74 and 148 alone, both with odd part 37. Round 2 went where the families part again: 624
  pairs up to n = 400, at odd parts 95, 101, 111, 141, 197 and 199. All 34 laws held.
- **Proved or known:** N4 (Vadali and Turner), D4 and N4+D4+self (the tensor argument above),
  H1 (the hexagon theorem) and H3 = H1^2. The other laws are conjectures, confirmed exactly at
  every size tested.
- **New, as far as two brief web searches went:**
  - the periods of the 2D rule-150 analogues (square D4+A4+self, hexagon H2+H3+self);
  - the full-bound family on all three lattices, including the Lights Out rule N4+self on the
    torus;
  - the splitting pattern, and its round-2 refinement: confinement by splitting, odd powers or
    dilation, and almost nothing else.

  One search found Vadali and Turner, and a project listing the sigma game's period on m x n
  grids as an aim, with no results. The other found OEIS entries for 2D rule 150 grown from one
  cell, not its torus periods. Linear cellular automata are well studied, and a specialist may
  know these. The literature was not read in full.
- **Who did what.** Kepler proposed every registered law from data, including the
  rule-150 laws: P150 was in its vocabulary, but no one had pointed it at these rules. The
  factorisation pattern, the quadratic relations and the short proofs were reasoning added
  afterwards.
- **Round 2: the pattern, registered.**
  - It was registered with every prediction stated in advance. It predicted 100 of 106
    full-bound periods for rules nobody had computed, and was refuted by 7 of 113 predictions.
  - The refutation was informative: it showed two mechanisms the pattern had missed. After the
    first failure of each, it was written down exactly where they would fail, before those
    sizes were computed, and that was confirmed.
  - The four remaining failures are open.
  - A round 3 should register the refined statement on new rules, preferably on the hexagon and
    triangle too, with the small sizes kept in.

## Reproducing

    uv run python examples/linear-atlas/validate.py
    uv run python examples/linear-atlas/discover.py --workers 4
    uv run lattice-lab verify --lab examples/linear-atlas
    uv run python examples/linear-atlas/factor.py
    uv run lattice-lab verify --lab examples/linear-atlas-2
    uv run python examples/linear-atlas-2/analyse.py

`study.py run` will not run twice on one ledger, since a run must follow a bare registration.
Any record can be rechecked on its own with `engine.Torus(lattice, shells, n).check(value)`.
