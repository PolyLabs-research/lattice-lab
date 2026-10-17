# The XOR rule's period on n x n tori: a pre-registered test

**Status: registered 2026-10-17T11:14:10Z; runs in progress. Results follow when judged.**

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

Pending: the runs started after the registration was pushed; the verdict is written to the
ledger when they finish.

## What this does and does not establish

To be written with the results.

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
