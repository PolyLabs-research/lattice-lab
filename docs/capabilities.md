# What Kepler can find in LatticeLife data

Each of Kepler's capabilities, run on real LatticeLife simulations rather than synthetic data:

```bash
uv run python examples/capabilities/run.py --workers 4
```

The runs are seeded and deterministic. Their records are in `examples/capabilities/data/` (a
second run reuses them), and every number below is in `examples/capabilities/results.json`. Each
capability also has known-answer tests in Kepler, on data drawn from a stated law; this page is
about what it says on the simulator's own output. These are single runs of each study: treat each
finding as one result to replicate, as the [B2/S34 example](../README.md) says of its own.

| Question | Kepler | LatticeLife | Section |
| --- | --- | --- | --- |
| Where does a soup survive, and how do the edges move with size? | binomial likelihood, `window`, `FSS_LAWS` | `survival` | [1](#1-survival-against-density-and-size) |
| How do times grow when long runs only give a bound? | `likelihood="censored"` | `event_times` | [2](#2-times-that-are-only-bounds) |
| Does the growth law depend on the starting density? | `compare_sharing` | `event_times` | [3](#3-one-law-across-densities) |
| How does a quantity settle over time, with honest error bars? | `TIME_LAWS`, `fit_replicates` | `count_series`, `damage_curves` | [4](#4-laws-over-time-with-seed-to-seed-error-bars) |
| Which distribution do object sizes follow? | `kepler.distributions` | `object_sizes` | [5](#5-distributions-of-object-sizes-and-abundances) |
| Is an exact quantity given by a formula? | `find_integer_laws` | periods from `CycleDetector` | [6](#6-exact-laws-for-periods) |
| What does a rule conserve? | `find_invariants` | `count_series` | [7](#7-conserved-quantities) |
| Is a fitted constant a known number? | `identify` | (any fit) | [8](#8-is-a-constant-a-known-number) |

## 1. Survival against density and size

Conway's Life (B3/S23) on square tori of 16, 32 and 64 cells a side, 23 starting densities from
0.02 to 0.9, 30 seeds each: is a soup alive at generation 999? Every run's fate is exact, so the
counts are binomial: Kepler fits them by maximum likelihood (`likelihood="binomial"`), with -2 ln
L exact and the BIC counting every seed.

At every size the survival curve is a **window**, not a step: too sparse and nothing forms that
lasts, too dense and the first generation's overcrowding kills almost everything. A rise then a
fall beats a single step by 280 to 490 BIC points.

| L | rise x1 | fall x2 |
| --- | --- | --- |
| 16 | 0.100 ± 0.012 | 0.714 ± 0.006 |
| 32 | 0.047 ± 0.003 | 0.784 ± 0.004 |
| 64 | 0.031 ± 0.002 | 0.835 ± 0.005 |

The window widens with size on both sides. One fit over density and size (`fss_logistic`:
threshold r + a L^-b, sharpening as L^s) against a fixed threshold that sharpens (`sharpening`)
and no transition at all (`crossover`):

- **Falling edge** (densities 0.5 to 0.9): the drifting threshold wins by 226 BIC points over a
  fixed one; the deviance per degree of freedom is 1.13, so the law fits the counts. The edge
  sharpens as L^(0.51 ± 0.13) and its threshold extrapolates to r = 0.93 ± 0.07 at infinite size:
  consistent with 1, that is, with the window reaching every density on a large enough torus.
- **Rising edge** (0.02 to 0.3): the drifting threshold again wins (by 40 points), extrapolating
  to r = 0.024 ± 0.006, but the deviance per degree of freedom is 2.4: the law does not capture
  these counts fully. On a larger torus a sparse soup has more places to form something stable,
  so this threshold may keep falling towards zero more slowly than any power of L. The fitted
  r is the law's extrapolation, not a measured threshold.

Design for the next run (`separation` with the fitted law as the truth): telling the drifting
threshold from a fixed one needs a third of these seeds on the rising edge and a sixteenth on the
falling edge, so the size dependence is not in doubt; what more data would buy is larger tori,
to see whether the rising threshold settles.

## 2. Times that are only bounds

The [B2/S34 example](../examples/lab-b2s34)'s 200 records hold every seed's exact first repeated
state (transient + period, the quantity a cap really bounds). A run with a shorter cap would have
stopped and reported only that the repeat comes later; runs are deterministic, so capping the
complete records reproduces exactly what that run would have recorded. With the cap at 155
generations, 12% of the times become bounds, 60% at L = 128.

| Fit | log law slope a | power law exponent b |
| --- | --- | --- |
| every time exact | 39.8 ± 2.6 | 0.424 ± 0.026 |
| capped, censored likelihood | 42.2 ± 2.9 | 0.457 ± 0.029 |
| capped, bounds dropped | 36.9 ± 2.6 | 0.422 ± 0.029 |

The censored fit stays within about one standard error of the complete data's; dropping the
bounds pulls the log slope down by one. What the cap costs is evidence: with every time exact, the
logarithm beats the power law by 4.4 BIC points; capped, by 0.1. The censored likelihood does not
manufacture the missing information, and the ranking says so rather than leaning on a guess.

## 3. One law across densities

B2/S34 on the hexagon lattice, first repeat against size (L = 8 to 64), starting densities 0.3,
0.5 and 0.7, 20 seeds each (420 runs, none censored at a cap of 4000). `compare_sharing` fits
every pattern of shared and per-density constants:

| Law | chosen | p (vs nothing shared) | constants |
| --- | --- | --- | --- |
| logarithmic | everything shared | 0.45 | a = 39.4 ± 2.0, b = -37.1 ± 5.5 |
| power | everything shared | 0.49 | a = 17.2 ± 1.4, b = 0.497 ± 0.025 |

The starting density does not matter: one curve serves all three, and sharing everything is 20
BIC points better than a curve per density. Between the two laws the data do not decide (1.6 BIC
points), so on tori up to 64 this question is open; the example lab's settling times, with
L up to 128, favoured the logarithm.

## 4. Laws over time with seed-to-seed error bars

Points along one run are correlated, so a mean curve's scatter understates the uncertainty of a
law fitted to it. `fit_replicates` resamples whole seeds; `compare_replicates` counts how often
each law is chosen across those resamples.

**Density relaxation** (B2/S34, hexagon, L = 64, 20 seeds, 400 generations from density 0.5): a
stretched exponential, chosen in 100% of resamples over a plain exponential and a power-law
approach. Density settles at c = 0.0201 ± 0.0006 with tau = 15.2 ± 0.8 generations and
beta = 0.681 ± 0.015; the fit's own error bar for beta (0.0085) is half the seed-to-seed one.

**Damage spreading** (B2/S34, hexagon, L = 48, one flipped cell, 20 seeds, 300 generations): a
compressed exponential (beta = 2.53 ± 0.09), chosen in 100% of resamples: the damage grows
slowly, then fast, then stops, at c = 4.2% ± 0.2% of the torus. It does not spread over the whole
torus.

## 5. Distributions of object sizes and abundances

120 Life soups on a 64 x 64 torus (density 0.35, up to 4000 generations), every final object
identified: 2756 objects of 136 distinct kinds (15 components were not objects). Two samples:
each object's population (cells), and each distinct object's abundance (how many times it was
seen). Kepler fits discrete families above a cutoff xmin chosen by the KS distance, compares them
(Vuong's test; a likelihood-ratio test for a cutoff), and asks by bootstrap whether the best can
be ruled out.

**Populations** are a few common objects (blinkers, blocks, boats and gliders, beehives, loaves,
traffic lights of 12 cells) and a short tail: above the chosen xmin of 13 cells there are only 31
objects. A power law (alpha = 6.0 ± 0.9) and an exponential describe that tail equally well
(Vuong p = 0.7 against a lognormal for each), and the power law is not ruled out (p = 0.63). With
31 objects, no family is preferred: the honest answer is "not enough tail".

**Abundances** are more informative. Above xmin = 2 (99 kinds were seen once, below the cutoff):

| Family | parameters | AIC |
| --- | --- | --- |
| truncated power law | alpha = 1.26 ± 0.13, lambda = 0.0011 ± 0.0010 | 328.9 |
| lognormal | mu = -0.2, sigma = 3.1 | 330.7 |
| power law | alpha = 1.45 ± 0.07 | 331.5 |
| exponential | lambda = 0.014 | 390.7 |

An exponential is ruled out (Vuong p = 0.003 against the lognormal). A cutoff on the power law is
supported (likelihood ratio p = 0.016), at about 900 sightings, near the most common object's
count (the block, 972). Between the truncated power law and the lognormal the data do not decide,
and the truncated power law only just survives its goodness-of-fit test (p = 0.10). Object
abundances in Life soups are heavy-tailed with a cutoff set, here, by the size of the sample.

## 6. Exact laws for periods

Periods are exact, so `find_integer_laws` searches for formulas in rational arithmetic and reports
how many points determined each law and how many more it reproduces.

**A glider on an n x n torus** (Life, n = 6 to 24): period 4n, determined by one point and
confirmed by 18. The known answer: a glider moves one cell diagonally every 4 generations.

**The XOR rule B1357/S1357** (a cell's next state is the parity of its eight neighbours), the
longest period over three random soups on n x n tori, n = 3 to 30:

| n | 3 | 5 | 6 | 7 | 9 | 10 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 | 29 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| period | 1 | 3 | 2 | 7 | 7 | 6 | 31 | 63 | 15 | 15 | 511 | 63 | 2047 | 1023 | 511 | 16383 |

On tori whose side is a power of 2 every soup dies (period 1). On the other 25 sizes the search
finds

    period = 2^v(n) * (2^sord(n) - 1)

where 2^v(n) is the largest power of 2 dividing n and sord(n) is the suborder of 2 modulo the odd
part of n: the least j with 2^j = +-1 modulo it. It was determined by one point and confirmed by
24. Then, before running them, it predicted the periods at n = 31, 33, 34 and 35: 31, 31, 30 and
4095. The simulator gave 31, 31, 30 and 4095. This is the structure Martin, Odlyzko and Wolfram
proved for the one-dimensional rule 90 (1984), and the odd sizes up to 23 had already been
published, as a conjecture, by J. McLaughlin: a rediscovery. What was not known is what happens
where rule 90 falls short of the formula (first at n = 37): a later, pre-registered test found
this rule does not, at n = 37 and 74, and confirmed the law at 45 sizes from 36 to 100; exact
periods computed by algebra then confirmed it at every n up to 200, including all ten sizes where
rule 90 falls short. See [the XOR period test](xor-periods.md). On the hexagonal and triangular
lattices the same search found one law for all three parity rules. A registered test refuted it on
the hexagon at three sizes, all of them sizes where rule 90 falls short, and that led to a proof
that the hexagon's period is rule 90's, times a factor 2 * 2^v(n) that is also proved:
[parity rules on other lattices](parity-lattices.md).

## 7. Conserved quantities

`count_series` records, at every generation, the live cells, cumulative births and deaths, and
live and dead cells by live-neighbour count. `find_invariants` looks for integer combinations
that never change in any run (12 runs per rule: tori of 12, 13, 16 and 17 cells a side, or 12 to
18 on the hexagon lattice, three seeds each, 200 generations).

For Life, HighLife (B36/S23), B2/S34 on the hexagon lattice and the XOR rule, the exact
invariants are the four bookkeeping identities and nothing else: live = live(0) + births - deaths,
live = sum of live cells by neighbour count, cells = live + sum of dead cells by neighbour count,
and sum of k times the cells with k live neighbours = degree x live. Rediscovering them is the
check that the search works; that nothing else appears says these rules conserve no other linear
combination of these counts.

Modulo 2 two more appear:

- For every rule, the number of live cells with an odd number of live neighbours is even. This is
  the handshake lemma (the live cells and their adjacencies form a graph, and every graph has an
  even number of odd-degree vertices): a theorem, rediscovered.
- For the XOR rule only, **cumulative births are always even**, on even and odd tori alike, so
  every generation has an even number of births (it also held in 84 further runs: tori of 5 to
  25 cells, two rectangles, densities 0.1 to 0.9). Found from the data, it then has a short proof.
  With x the live cells and x' the next generation, births = |x'| - sum_i x_i x'_i. Each x'_i is
  the parity of i's live neighbours, so |x'| has the parity of the sum of every cell's live
  neighbours, which counts each live cell 8 times: even. And sum_i x_i x'_i has the parity of
  sum_i x_i (live neighbours of i), which counts each pair of adjacent live cells twice: even.
  The same holds for the parity rule on any lattice whose cells all have an even number of
  neighbours.

## 8. Is a constant a known number?

`identify` lists closed forms and named constants (percolation, Ising, directed percolation and
KPZ exponents, percolation thresholds) within two standard errors, with `p_chance`: the chance
that a value with that error bar, landing anywhere at that scale, would match something as simple.

| Constant | Value | Nearest simple match | p_chance |
| --- | --- | --- | --- |
| first-repeat exponent, power law (section 3) | 0.497 ± 0.025 | 1/2 | 0.19 |
| falling-edge threshold at infinite size (1) | 0.93 ± 0.07 | 1 | 0.21 |
| density relaxation beta (4) | 0.681 ± 0.015 | sqrt(1/2) (z = 1.75); 2/3 (z = -0.9) | 0.20; 0.30 |
| damage beta (4) | 2.53 ± 0.09 | 5/2 | 0.63 |
| rising-edge threshold (1) | 0.024 ± 0.006 | none simpler than (1/9)/pi | 0.68 |
| object abundance exponent, power law (5) | 1.45 ± 0.07 | sqrt(2) | 0.49 |

None of these is evidence for a closed form: at these error bars a match as simple turns up by
chance a fifth of the time or more. The exponent 1/2 and the relaxation's 2/3 are worth a second
look with more seeds, which `separation` can size. The periods in section 6, which are exact,
are where closed forms were found.

## What this does not show

- These are one run of each study, each on one rule and a few sizes.
- The loop (`lattice-lab ask`) still asks one kind of question, settling time against size. The
  survival, relaxation and sharing questions above are ready to become question types: the
  likelihoods, laws, designs and observables exist and are tested.
- An extrapolation to infinite size is a law's, not a measurement's; the rising-edge threshold
  in section 1 is the clearest case.
