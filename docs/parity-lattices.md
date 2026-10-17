# Parity rules on the hexagonal and triangular lattices

**Status: judged, two rounds.** Kepler found one period law for all three rules from simulations up
to n = 60. **Round 1** registered it at 210 new (lattice, size) pairs: it held at all 140
triangular ones and was **refuted on the hexagon at n = 74, 148 and 190**, each time by exactly a
factor of 3. The refutations fell where the 1D rule 90 falls short of its bound, and this led to
a **proof that the hexagonal rule's odd period is rule 90's**: two hexagon generations are exactly
three passes of rule 90, one along each lattice direction. **Round 2** registered the corrected
law at every even n from 202 to 400; it is being computed now.

## The rules

The parity rule sets each cell to the parity of its live neighbours, whatever its own state. It
is linear over GF(2):

| Lattice (LatticeLife) | Rule | Neighbours |
| --- | --- | --- |
| hexagon (odd-q offset columns) | B135/S135 | 6 |
| triangle, edge | B13/S13 | 3 |
| triangle, edge+vertex | B1,3,5,7,9,11/S1,3,5,7,9,11 | 12 |

Both lattices alternate across columns, so their n x n tori need n even. Write n = 2^v(n) m with m
odd. sord(m), the suborder of 2, is the least j with 2^j = +-1 modulo m. The square XOR rule's
law, from the [earlier study](xor-periods.md), was 2^v(n) (2^sord(n) - 1).

## Discovery: what Kepler found (n = 6..60)

`examples/parity-lattices/discover.py` ran each rule in LatticeLife from a single live cell on
every even n from 6 to 60. On the triangle it ran one up cell and one down cell, the two kinds of
cell. The rules are linear, so the torus's longest period is the lcm of these single-cell
periods. Kepler's `find_integer_laws` then searched the periods (`laws.json`, committed in
`d89f1b0`):

    P(n) = 2 * 2^v(n) * (2^sord(n) - 1)

The fit is determined by one size and confirmed by the rest. That is 20 sizes for odd parts of at
least 5 on all three lattices, and 24 on the triangles once powers of 2 are excluded. The law is
twice the square rule's. Discovery also showed two small families:

- at powers of 2, the hexagon and edge+vertex triangle die, and the edge triangle has period n;
- on the hexagon, at odd part 3 the period is 2^v(n).

Transients: on the hexagon, 2 * 2^v(n), or n/2 at powers of 2. On the triangles they were
irregular, so they were not predicted.

## An exact engine

Simulation stops once periods reach millions of generations. Each rule is multiplication in the
group ring F2[T] of the torus's translation group, T = Z^2 / Lambda.

- **Hexagon.** In axial coordinates (q, r) = (column, row - floor(column / 2)), the six
  neighbours are the steps +-(1, 0), +-(0, 1), +-(1, -1). The torus is
  Lambda = <(n, -n/2), (0, n)>, and one generation multiplies by sigma, the sum of the six steps.
- **Triangle.** The up and down cells are two copies of one translation group. One generation
  multiplies the pair by a 2 x 2 matrix over F2[T], read off LatticeLife's own neighbour
  offsets.

The period is computed as an order: check M^(t0 + P) = M^t0 for a candidate P, then divide out
P's primes while that still holds. Products are exact FFT convolutions with a rounding check
(`examples/parity-lattices/lattices.py`). If the candidate fails, a bound valid on every torus
is used instead, so a wrong law is reported as wrong.

Two checks came before registration. The engine's one-step image matched LatticeLife's adjacency
for every cell on every torus from 6 to 14. It also reproduced all 84 simulated (period, transient)
pairs.

## Round 1: the registered test

The registration is in `examples/parity-lattices/ledger.jsonl`, committed and pushed in `bc47043`
at 2026-10-17T14:04:32Z, before the engine had run on any of these sizes. It holds:

- the period law at every even n from 62 to 200 on all three lattices (210 predictions);
- the hexagon transient law at the same 70 sizes.

| | Outcome |
| --- | --- |
| triangle, edge: 70 sizes | **confirmed at 70** |
| triangle, edge+vertex: 70 sizes | **confirmed at 70** |
| hexagon: 70 sizes | **confirmed at 67, refuted at 3** |
| hexagon transients: 70 sizes | **confirmed at 70** |

The refutations:

| n | odd part | predicted | exact | ratio |
| --- | --- | --- | --- | --- |
| 74 | 37 | 1048572 | 349524 | 3 |
| 148 | 37 | 2097144 | 699048 | 3 |
| 190 | 95 | 274877906940 | 91625968980 | 3 |

At the same three sizes, both triangular rules attained the law's value. The longest period in
round 1 was 8796093022204 (about 9 x 10^12 generations), on the 166 x 166 hexagon and on both
triangles.

## Why the hexagon falls short: two steps are three passes of rule 90

37 and 95 were already familiar. They are the first two odd sizes where rule 90 on an m-cycle
falls short of its bound 2^sord(m) - 1, both times by a factor of 3 (Martin, Odlyzko and Wolfram
1984; the [XOR study's round 2](xor-periods.md#round-2-exact-periods-by-algebra)). Comparing the
two directly: at all 98 hexagon sizes computed (28 simulated, 70 registered), the odd part of the
period equals rule 90's period on the odd-part cycle. That comparison was made after the
verdict. What follows explains it.

**Lemma (two steps, three passes).** With c(z) = z + 1/z (rule 90 along one direction),

    sigma(x, y)^2 = c(x) c(y) c(x/y)        in F2[x^+-1, y^+-1].

*Proof.* In characteristic 2, sigma(x, y)^2 = sigma(x^2, y^2). Also c(x) c(y) = c(xy) + c(x/y), so

    c(x) c(y) c(x/y) = c(xy) c(x/y) + c(x/y)^2 = c(x^2) + c(y^2) + c(x^2 / y^2) = sigma(x^2, y^2).

This is a polynomial identity, so it holds on the plane and on every torus. **Two generations of
the hexagonal parity rule are rule 90 applied along (1, 0), then (0, 1), then (1, -1).**
`tests/test_parity_lattices.py` checks this against LatticeLife's own stepping on random soups.

**Theorem.** Let n be even with odd part m. Then the odd part of the longest period of B135/S135
on LatticeLife's n x n hexagonal torus equals the period R(m) of rule 90 on the m-cycle, with
R(1) = 1.

*Proof.*

1. *A single cell has the longest period.* The ring is commutative, so the longest period is the
   period of sigma in F2[T]: every orbit's period divides the single cell's.
2. *Reduce to eigenvalues.* Split T = T_2 x T_odd. Since |T_odd| is odd, F2[T_odd] is a product
   of finite fields, one for each Frobenius orbit of characters chi of T_odd. So F2[T] is a
   product of local rings F_chi[T_2], in which sigma is lambda_chi = chi(sigma) plus a nilpotent.
   - Where lambda_chi = 0, sigma is nilpotent in that factor.
   - Elsewhere sigma is a unit. Its order is ord(lambda_chi) times a power of 2, because in
     characteristic 2 a unit of the form 1 + nilpotent has 2-power order.

   So the odd part of the period is the lcm of ord(lambda_chi) over the characters with
   lambda_chi != 0.
3. *Name the characters.* At each odd prime, Lambda localises to m Z^2, so T_odd = (Z/m)^2. Its
   characters are chi(q, r) = u^q w^r with u and w ranging over all m-th roots of unity, and
   lambda_chi = sigma(u, w).
4. *Rule 90 the same way.* Rule 90 on the m-cycle is multiplication by c(z) in F2[Z/m]. Its
   period is the lcm of ord(c(a)) over the m-th roots of unity a with c(a) != 0.
5. *Compare the two groups.* Everything lies in the cyclic group F(2^K)^*, K = ord_m(2). There the
   lcm of a set's orders is the order of the subgroup the set generates. Let H be generated by the
   nonzero sigma(u, w), and G by the nonzero c(a).
   - *H is in G.* By the lemma, a nonzero sigma(u, w) has square c(u) c(w) c(u/w), which lies in
     G. Squaring is a bijection on a group of odd order, so sigma(u, w) lies in G.
   - *G is in H.* sigma(a, 1/a) = c(a^2) = c(a)^2, which is nonzero for a != 1. So c(a) lies in H.

   Hence |H| = |G|. ∎

**Consequences.**

- Martin, Odlyzko and Wolfram showed that R(m) divides 2^sord(m) - 1. So round 1's law was
  always a multiple of the truth. It is exact precisely at the odd parts where rule 90 meets its
  bound. Among odd m up to 999, rule 90 falls short at least 50 times (37, 95, 101, 111, 141,
  197, 199, 203, ...; `examples/xor-periods-proof/results.jsonl`). The shortfall is usually a
  factor of 3, but 7 at m = 199.
- What stays observed, not proved: the 2-part, 2 * 2^v(n), with its families at m = 1 and m = 3.

How the lattices compare, at their odd part:

| Rule | Lattice | Neighbours | Odd part of the period, against rule 90 |
| --- | --- | --- | --- |
| sigma automaton | square | 4 | equal (Vadali and Turner 2025, proved) |
| B1357/S1357 | square | 8 | the full bound at every n up to 200, including all of rule 90's shortfalls ([XOR study](xor-periods.md)) |
| B135/S135 | hexagonal | 6 | **equal** (proved above) |
| B13/S13 | triangular, edge | 3 | the full bound at every size computed, including rule 90's shortfalls |
| B1,3,...,11/S1,3,...,11 | triangular, edge+vertex | 12 | the same |

## Round 2: the corrected hexagon law

Registered in `examples/parity-lattices-hexagon/ledger.jsonl`, committed and pushed in `f99dafc`
at 2026-10-17T14:17:39Z, before any of these sizes was computed:

- the corrected hexagon law, 2 * 2^v(n) * R(m), at every even n from 202 to 400 (100 sizes);
- round 1's law as the rival. The two differ at seven sizes: 202, 222, 282, 296, 380, 394 and
  398 (odd parts 101, 111, 141, 37, 95, 197 and 199);
- the triangles at those seven sizes, where round 1's law predicts no shortfall;
- the hexagon transients.

Results: pending; the computation is running.

## Not registered: the triangles' transients

The triangles' transients were not predicted. One pattern was noticed afterwards. On the edge
triangle, at all 93 sizes computed that are not powers of 2, the transient is positive exactly
when some m-th root of unity u has 1 + u also an m-th root of unity. Among odd parts up to 99,
that is m divisible by 3, 7, 31, 73 or 85. This fits the rule having a zero eigenvalue at those
odd parts, which a three-neighbour stencil of the form 1 + u + w would give; that is not worked
out here. When the transient is positive it is 2^(v(n)+1) at the odd parts in
S = {7, 15, 21, 31, 35, 45, 49, 63, 73, 75, 77, 85, 91, 93}, and 2^v(n) at the others
(3, 9, 27, 33, 39, ...). The edge+vertex triangle has a positive transient at every size. It is
2^(v(n)+1) at exactly the same odd parts S, and max(1, 2^(v(n)-1)) everywhere else. None of this
is proved or registered.

## What this does and does not establish

- **Proved, for every even n:** two hexagon generations are three passes of rule 90. The
  hexagon's odd period is rule 90's period on the odd-part cycle.
- **Observed, not proved:**
  - the factor 2 * 2^v(n) on all three lattices;
  - the triangles' periods: in every size computed, the full 2^sord(m) - 1 at the odd part;
  - every transient law.

  These rest on the computations: exact at every size listed, but finite.
- **Two methods, one answer.** Simulation and the exact engine agree at all 84 pairs where both
  exist, and the engine's one-step map is LatticeLife's.
- **Novelty, as far as the search went.** A web search found no work on parity rules over GF(2)
  on hexagonal or triangular tori. The nearest results:
  - Uğuz, Siap and Akın study hexagonal rules over Z_3, on reversibility.
  - Vadali and Turner (2025) prove the square four-neighbour sigma automaton has rule 90's cycle
    lengths. That is the same kind of statement as the theorem here, on another lattice.

  The lemma is elementary, and a specialist may well know it. The literature was not read in
  full (arXiv full text was not reachable from this environment).
- **Who did what.** Kepler found round 1's law from data. Its registered predictions were
  refuted at three sizes, and those refutations showed exactly where it was wrong. Matching them
  to rule 90's shortfalls, and the lemma and proof, were reasoning added afterwards, not output
  of the tools. Kepler's integer-law vocabulary has no term for another automaton's period, so it
  could not have proposed the corrected law.
