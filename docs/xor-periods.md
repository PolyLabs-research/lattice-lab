# The XOR rule's period on n x n tori: a pre-registered test

**Status: judged, two rounds. Round 1 (simulation): the law confirmed at all 45 registered sizes
and the rival refuted at n = 74. Round 2 (exact algebra): the law confirmed at all 198 sizes from
3 to 200, 120 of them new, and the rival refuted at all ten sizes where the two differ.**

## The law

B1357/S1357 is the parity rule on the square lattice: a cell's next state is the parity of its
eight neighbours, whatever its own state. On an n x n torus every run ends in a cycle. From
LatticeLife runs on n = 3 to 30 (the longest period over three random soups at each size),
Kepler's exact-law search (`find_integer_laws`) found

    period(n) = 2^v(n) * (2^sord(n) - 1)        n not a power of 2

where 2^v(n) is the largest power of 2 dividing n and sord(n), the suborder of 2, is the least j
with 2^j = +1 or -1 modulo the odd part of n. It was fixed by one size and reproduced the other
24 exactly. On tori whose side is a power of 2 every soup dies (period 1). The law, with its
data, was committed and pushed in lattice-lab `8d7bc58` on 2026-10-16
([capabilities, section 6](capabilities.md#6-exact-laws-for-periods)).

## What was already known

- **The odd sizes up to 23.** J. McLaughlin (West Chester University) lists this rule's periods on
  odd tori from 3 to 23, the same numbers, posed as a conjecture. Most of what the search found
  was a rediscovery.
- **The same structure in one dimension.** Martin, Odlyzko and Wolfram (1984) proved that rule 90
  (each cell becomes the parity of its two neighbours) on an n-cycle has period 1 when n is a
  power of 2, twice the period at n/2 when n is even, and a divisor of 2^sord(n) - 1 when n is
  odd: usually equal to it, but not always. The first exception is n = 37, where rule 90's period
  is 87381, a third of 2^18 - 1 = 262143.
- **Two dimensions, another rule.** Vadali and Turner (2025) proved that the 2D analogue of rule
  90 on the four nearest neighbours (the "sigma automaton") has the same cycle lengths as rule 90
  itself. Nothing found in a literature search covered this eight-neighbour rule beyond n = 23.

So the open question the law raises is sharp: **at the sizes where rule 90 falls short of its
bound, does this 2D rule fall short too?** The law says no. The rival, that the 2D rule's period
equals rule 90's (as it does for the four-neighbour analogue), says yes.

## Why the two can differ (reasoning, not a measurement)

Two facts bound the 2D rule's period from both sides; they are short arguments, given here so the
test's meaning is clear, not results of the search.

- *From below.* A configuration that is constant along one axis stays so, and since 3 = 1 modulo
  2, each column's new state is the parity of its two neighbouring columns: it evolves exactly as
  rule 90 on the n-cycle. So the torus has orbits of rule 90's period, and its longest period is
  a multiple of it.
- *From above.* Write the rule as a polynomial over GF(2), T = (1 + x + 1/x)(1 + y + 1/y) - 1. In
  characteristic 2, squaring is additive, so T^(2^j) is T with x and y replaced by x^(2^j) and
  y^(2^j). On an odd torus, x^n = 1, so if 2^j = +-1 modulo n then x^(2^j) = x^(+-1), which
  leaves T unchanged: T^(2^j) = T. Every run is then periodic from generation 1 (transient at
  most 1, which is McLaughlin's observation that generation 2 always recurs) with a period
  dividing 2^sord(n) - 1.

For odd n, then, the period lies between rule 90's and 2^sord(n) - 1, and wherever rule 90 attains
the bound (every odd n below 37) the law follows. Where rule 90 does not, both answers remain
possible, and only a measurement decides.

## n = 37: before the ledger

On 2026-10-17, after the law was public, n = 37 was run without first writing a prediction
into a ledger:

| Start | Period | Transient |
| --- | --- | --- |
| random soup, seed 1 | 262143 | 0 |
| random soup, seed 2 | 262143 | 0 |
| random soup, seed 3 | 262143 | 0 |
| constant along one axis (evolves as rule 90) | 87381 | 1 |

The soups give the law's value; the control gives rule 90's published value, which confirms
that the setup reproduces rule 90 exactly where it should. The law's prediction at 37 followed
from the committed law, but the choice to test 37 was not recorded in advance, so this result is
reported as background, not as the test.

## The registered test

`examples/xor-periods/ledger.jsonl` (lattice-lab's hash-chained ledger) holds, written at
2026-10-17T11:14:10Z and pushed in `6097179` before any of these runs existed:

1. the question and its design: every n from 36 to 100 that is not a power of 2 and whose
   predicted period costs at most 4 x 10^9 cell-generations, except 37 (45 sizes); three random
   soups per size (density 0.5, seeds 1 to 3) and one start constant along an axis; a cap of
   twice the predicted period, so a longer period would be seen;
2. the law's predicted period at each size, and its decision rule: *confirmed* when the longest
   period over the three soups equals the prediction, *refuted* when any soup's period does not
   divide it (a longer period or an unsettled run does not), *short* otherwise;
3. the rival's prediction, rule 90's period at each size, computed exactly in GF(2)[x]/(x^n - 1).
   Between 36 and 100 it differs from the law at affordable sizes only at **n = 74 = 2 x 37**:
   the law says 524286, the rival 174762;
4. the control's prediction: the axis-constant start's period divides rule 90's.

`study.py run` refuses to start until the registration is committed, and `lattice-lab verify`
checks that the predictions precede the run and that every record the verdict uses was written
after it started.

## Results

180 runs (45 sizes x three soups and one control), in `examples/xor-periods/records.jsonl`; the
verdict is ledger entry 6.

| | Registered prediction | Outcome |
| --- | --- | --- |
| The law, at 45 sizes | longest soup period = 2^v(n)(2^sord(n) - 1) | **confirmed at 45 of 45**; every soup at every size gave exactly the predicted period |
| The rival, at n = 74 | 174762 (rule 90's period) | **refuted**: all three soups gave 524286, the law's value |
| The rival, at the other 44 sizes | rule 90's period (equal to the law's there) | not refuted, as expected: there the two agree |
| The control, at 45 sizes | the axis-constant start's period divides rule 90's | **passed at 45 of 45**, and equal to it at every size; at n = 74, 174762 |
| Transients, odd n | at most 1 | **held** at every odd size |

The decisive size:

| n = 74 | Period | Transient |
| --- | --- | --- |
| soup, seed 1 | 524286 | 1 |
| soup, seed 2 | 524286 | 1 |
| soup, seed 3 | 524286 | 1 |
| constant along one axis (evolves as rule 90) | 174762 | 1 |

On the same 74 x 74 torus, the configurations that behave as rule 90 cycle with rule 90's period,
and every random soup cycles three times longer. With n = 37 before it, this is the second size at
which this rule does not share rule 90's shortfall. On n x n tori its period equals the bound
2^v(n)(2^sord(n) - 1) at every size measured, 75 of them (25 from 3 to 30, the held-out 31, 33,
34 and 35 of the first study, 37, and the 45 here), including the two where rule 90's period
is a third of it.

Not registered, so only an observation: on even tori the transients reach powers of 2 (2 at
n = 36, 8 at 40 and 48, 16 at 80 and 96), no larger than 2^v(n).

## Round 2: exact periods by algebra

Simulation stops where periods run to millions of generations: 47 (8 x 10^6), 49, 53, 61 and
beyond, including rule 90's next shortfall at n = 95 (a period of 6.9 x 10^10). But the rule is
linear, so the state at generation t from a single live cell is tau^t in the ring
GF(2)[x,y]/(x^n - 1, y^n - 1), and because that ring is commutative, the single cell has the
torus's longest period and transient. The period is then an order: check tau^(t0 + P) = tau^t0
for the predicted P, and divide out each prime factor of P while that still holds. That takes the
prime factors of 2^sord(n) - 1 and a few hundred ring multiplications (exact cyclic convolutions,
by FFT with a rounding check), not P generations
([algebra.py](../examples/xor-periods-algebra/algebra.py)).

Before it was trusted, the method reproduced the simulated period at all 74 sizes simulated in
round 1 and before it, and rule 90's published 87381 at n = 37. Then, in
`examples/xor-periods-algebra/ledger.jsonl`, written at 2026-10-17T12:38:07Z and pushed in
`d2eb97a` before the computation ran on any new size: the law's period at every n from 3 to 200
(1 for a power of 2), the transient bound (at most 1 for odd n, at most 2^v(n) for even n), and
the rival's prediction, rule 90's period, which differs from the law at ten of these sizes.

| | Outcome |
| --- | --- |
| The law, n = 3..200 | **confirmed at 198 of 198** (120 never simulated) |
| The rival, at the ten sizes where it differs | **refuted at all ten** |
| Transients | within their bounds at every size; exactly 1 at every odd n |

At every size where rule 90 falls short of 2^v(n)(2^sord(n) - 1), the 2D rule does not:

| n | 2D period (exact) | rule 90's period | ratio |
| --- | --- | --- | --- |
| 37 | 262143 | 87381 | 3 |
| 74 | 524286 | 174762 | 3 |
| 95 | 68719476735 | 22906492245 | 3 |
| 101 | 1125899906842623 | 375299968947541 | 3 |
| 111 | 68719476735 | 22906492245 | 3 |
| 141 | 70368744177663 | 23456248059221 | 3 |
| 148 | 1048572 | 349524 | 3 |
| 190 | 137438953470 | 45812984490 | 3 |
| 197 | 2^98 - 1 = 316912650057057350374175801343 | a third of it | 3 |
| 199 | 2^99 - 1 = 633825300114114700748351602687 | a seventh of it | 7 |

The longest period computed is at n = 199: 2^99 - 1, about 6 x 10^29 generations. Tori whose side
is a power of 2 die, as predicted (period 1), after exactly n/2 generations from a single cell.

## What this does and does not establish

- **Every n up to 200, exactly; beyond that, unproved.** Round 2's periods are exact, not
  estimates, at every size from 3 to 200. For all n, the bound argument above proves that for odd
  n the period divides 2^sord(n) - 1 and is a multiple of rule 90's; that the rule always attains
  the bound, unlike rule 90, holds at every size computed and remains to be proved. Even sizes
  rest on the computations alone.
- **The two methods agree.** Simulation (the longest period over three soups, a lower bound) and
  the exact computation give the same period at all 74 sizes where both exist, so the algebra
  describes LatticeLife's own dynamics, not an idealisation of them.
- **Beyond 200, factoring becomes the limit:** the method needs the prime factors of
  2^sord(n) - 1, which are known (Cunningham tables) far beyond what sympy factors quickly.
- **Novelty is as far as the search went.** The odd sizes to 23 were published by McLaughlin.
  Nothing found covers this rule at the sizes where rule 90 falls short, and the closest proved
  result, Vadali and Turner's for the four-neighbour analogue, goes the other way (2D equals 1D).
  The specialist literature on 2D linear automata (Kawahara et al. 1992 among it) was not read in
  full and should be before this is claimed as new.
- **Who did what.** Kepler's search found the law from data and predicted unseen sizes; the
  argument that told where to test (rule 90's shortfalls), why the law holds at most odd sizes,
  and how to compute periods exactly is reasoning added afterwards, not output of the tools.

## Checking it

```bash
uv run lattice-lab verify --lab examples/xor-periods   # chain, and predictions before the run
uv run lattice-lab verify --lab examples/xor-periods-algebra
git log --format='%h %ad %s' --date=iso -- examples/xor-periods
uv run python examples/xor-periods/study.py preregister   # refuses: already registered
```

Every record holds its rule, torus, seed, start and cap, and no timings, so any one can be rerun
with `study.py`'s `measure` and compared byte for byte.

## Sources

- J. McLaughlin, [a cellular automaton conjecture page](https://www.wcupa.edu/sciences-mathematics/mathematics/jMcLaughlin/cellauto.aspx), West Chester University.
- O. Martin, A. Odlyzko and S. Wolfram, Algebraic properties of cellular automata, *Comm. Math.
  Phys.* 93 (1984) 219-258; summarised by [Powley and Stepney](https://www-users.york.ac.uk/%7Ess44/bib/ss/nonstd/auto08.pdf)
  and in [Wolfram's NKS notes](https://wolframscience.com/nksonline/page-951a/), which give
  n = 37 as rule 90's first exception; rule 90's period 87381 at n = 37 is
  [OEIS A085587](https://oeis.org/A085587).
- A. Vadali and A. Turner, [Equality of cycle lengths in one- and two-dimensional sigma
  automata](https://arxiv.org/pdf/2502.10898) (2025).
- Kawahara, Kumamoto, Mizoguchi and Nomi, [Period lengths of cellular automata on square lattices
  with rule 90](https://catalog.lib.kyushu-u.ac.jp/opac_download_md/3062/54.ps.tar.pdf) (1992),
  not read in full here.
