# How long a soup takes to settle: a replication and a universality test

**Status: judged, two registered studies.** Study A: B2/S34 on hexagon tori up to 1024. The log law
**replicated** and the power law was **rejected**. Of the two registered mechanisms, the
heavy-tailed one was rejected outright. The light-tailed one (Gumbel) matched the fluctuations'
shape and their constancy, but not their size. Study B: eight random rules on all four lattice
types, registered before Study A's verdict existed. The log law held and the power law failed for
**all eight**. Across them, the fluctuations share **one shape** and **one ratio of spread to
growth**, and both equal the Gumbel values for the largest of about L^2 independent times.

The parity-rule studies ([XOR](xor-periods.md), [other lattices](parity-lattices.md)) were about
linear rules, which can be solved exactly. These two studies are about rules with no such theory.
The quantity is the **settling time**: the generation at which a random soup (density 0.5) on an
L x L torus enters its final cycle, or empties.

## The question

The example lab ([examples/lab-b2s34](../examples/lab-b2s34)) asked how the median settling
time of B2/S34 soups on hexagon tori grows with L. Fitted on L = 8 to 32 and tested at 64, 96
and 128, it found **logarithmic**, T = 37.6 ln L - 36.3. A power law, T = 22.3 L^0.398, also
passed its held-out test and was 8.4 BIC points behind. A later study of first repeats up to
L = 64 could not tell the two apart ([capabilities, section 3](capabilities.md#3-one-law-across-densities)).
Both write-ups called it one answer to replicate.

## Two mechanisms

A soup settles when its last region does, so its settling time is the largest of about L^2
local settling times. The two classic limits for the largest of many independent values each
tie the seed-to-seed fluctuations to how the median grows, with nothing fitted to the
fluctuations ([lattice_lab.extremes](../src/lattice_lab/extremes.py)).

| | light tails (Gumbel) | heavy tails of index alpha (Frechet) |
| --- | --- | --- |
| median | 2 tau ln L + c: the **log law**, with tau = slope / 2 | proportional to L^(2/alpha): the **power law**, with alpha = 2 / exponent |
| interquartile range | 1.5725 tau, the same at every L | a fixed fraction of the median |
| shape: Kelly's skewness (Q90 + Q10 - 2 Q50)/(Q90 - Q10) | 0.2215, for every rule | a function of alpha alone |

So each law comes with a mechanism that predicts the fluctuations from the law's own constants.
Spread and shape are measured by quantiles, not moments. A tail of index 5 has no finite sixth
moment, so a sample's moment skewness has no usable error bar; quantiles do, for both kinds of
tail. Before registration, each study's decision code was run on synthetic data drawn from each
mechanism. On 20 replicates of each, it picked the right law and the right mechanism every time.
That run caught one flaw: a moment-based skewness test would have rejected true Frechet data.

## Study A: B2/S34 on hexagon tori up to 1024

`examples/settling-time-replication`, registered and pushed in `d9a7823` at
2026-10-17T15:40:02Z, before any run at these sizes:

- the six library laws, fitted to the example lab's ten sizes (8 to 128), predicting the
  median at L = 192, 256, 384, 512, 768 and 1024, with 100 seeds each;
- the Gumbel mechanism from the log law's slope: tau = 18.8, so an interquartile range of
  29.6 +- 2.1 at every size, and Kelly's skewness 0.2215;
- the Frechet mechanism from the power law's exponent: alpha = 5.03, so an interquartile range
  0.32 +- 0.03 of the median, and Kelly's skewness 0.363 +- 0.014.

The run took 28 minutes on four cores (600 runs, none unsettled at the 2000-generation
cap). `lattice-lab verify --rerun 3` reran three records byte for byte.

**The laws.** The logarithm passed (joint p = 0.15, all six sizes inside their 95% bands). The
power law was rejected (p = 10^-9), as were the constant, linear and both exponential laws.

| L | observed median | log law | power law |
| --- | --- | --- | --- |
| 192 | 159.0 | 161.4 [149, 175] | 180.5 [156, 209] |
| 256 | 160.5 | 172.2 [159, 187] | 202.4 [172, 239] |
| 384 | 181.0 | 187.5 [172, 204] | 237.8 [196, 289] |
| 512 | 187.5 | 198.3 [181, 217] | 266.6 [215, 331] |
| 768 | 197.0 | 213.5 [195, 234] | 313.3 [245, 400] |
| 1024 | 210.0 | 224.4 [204, 247] | 351.3 [269, 459] |

On tori up to 1024 the median settling time of B2/S34 grows like the logarithm of the size, not
a power of it. **The example lab's answer replicates.**

**The mechanisms.** Both were rejected, but not in the same way.

| test | observed | Gumbel (light tails) | Frechet (heavy tails) |
| --- | --- | --- | --- |
| interquartile range | 20.0 +- 1.0 | 29.6 +- 2.1: **fails** (z = -4.1) | |
| its slope against ln L | -1.5 +- 1.8 | 0: passes | |
| interquartile range / median | 0.109 +- 0.006 | | 0.32 +- 0.03: **fails** (z = -6.4) |
| Kelly's skewness | 0.208 +- 0.049 | 0.2215: passes | 0.363 +- 0.014: **fails** (z = -3.1) |

The heavy-tail mechanism is wrong on every count: the fluctuations are far narrower, and less
skewed, than a power law's tail would make them. The light-tail mechanism gets the shape right
(Gumbel's skewness) and the constancy right (the spread does not grow from 192 to 1024). It gets
the amplitude wrong: the spread is two thirds of what independent regions with tau = slope/2
would give.

| L | median | interquartile range | Kelly's skewness | standard deviation |
| --- | --- | --- | --- | --- |
| 192 | 159.0 | 27.3 +- 3.2 | 0.30 +- 0.11 | 18.8 |
| 256 | 160.5 | 16.5 +- 1.9 | 0.09 +- 0.13 | 14.3 |
| 384 | 181.0 | 31.0 +- 3.9 | 0.26 +- 0.10 | 24.1 |
| 512 | 187.5 | 21.5 +- 2.4 | 0.15 +- 0.13 | 20.4 |
| 768 | 197.0 | 16.3 +- 2.2 | 0.32 +- 0.16 | 23.9 |
| 1024 | 210.0 | 20.5 +- 2.7 | 0.12 +- 0.12 | 32.3 |

**After the verdict (not registered).** Three observations, for a later registered test:

- *The spread per unit slope.* Over the new sizes alone, the median's slope in ln L is
  31.4 +- 1.3, and the interquartile range over that slope is 0.64 +- 0.04, against Gumbel's
  0.786 for the largest of L^2 independent times. Taken at face value, that is the largest of
  about L^2.5 times.
- *The slope falls.* It was 37.6 when fitted on 8 to 128, and is 31.4 over 192 to 1024. Every
  observed median sits below the log law's prediction (z between -0.3 and -1.6), within the bands
  but on one side.
- *A far tail.* The standard deviation (32 at 1024) is larger than a Gumbel bulk of that
  interquartile range implies (17), because of a few seeds that run much longer (433 at 1024,
  against a median of 210).

One refinement seemed to explain the first two. If the local times' tail is exponential with a
power-law prefactor, about t^k e^(-t/tau), the largest of N of them has location
tau ln N + k tau ln ln N. Its slope in ln L exceeds 2 tau by a term that fades as L grows.

**Correction (made before round 2 was registered).** That reasoning was half wrong. It took the
spread to be 1.5725 tau, using the tail's asymptotic scale. But the largest of N times with any
smooth tail has spread and slope both set by the tail's hazard rate at the location b_N:
spread = 1.5725 / h(b_N) and slope = 2 / h(b_N). Their ratio is Gumbel's 0.786 whatever the
prefactor; worked out exactly, it is 0.785 to 0.786 for k from 0 to 5, at every L from 256 to
4096. So a fading correction can explain a falling slope, but it cannot explain a narrow spread.
No model in which settling is the largest of independent, identically distributed local times
can explain a ratio of 0.64. Fitted properly to all quantiles at 64 to 1024, the model prefers
k = 0 (tau = 14.5 +- 3.0), but k = 3 is within its errors, and every k fits poorly (chi-square
about 90 on 42 degrees of freedom). That misfit is the same tension: the medians grow faster
than the spread allows. Round 2, below, tests the assumption itself.

## Study B: the same question on every lattice

`examples/settling-universality`, registered and pushed in `48176fd` at 2026-10-17T15:48:11Z.
That was before any run at the test sizes, and before Study A's verdict (16:08:29Z) existed.

**The rules.** `select.py` drew rules at random from each lattice's whole rule space (birth on 0
excluded), with a fixed seed. It kept the first two on each lattice that settle within 2000
generations on 16 x 16 and 64 x 64 tori, take at least 20 generations to, and take longer on
the larger torus. Nothing about the growth law or the fluctuations was looked at. 79 rules were
tried and 8 kept (`selection.jsonl`).

**The predictions.** For each rule, the six library laws were fitted to tori of 8 to 64 (40
seeds) and predicted at 128, 256 and 512 (100 seeds). Each law's mechanism predicted the
fluctuations, as in Study A. Two predictions concern all eight rules at once, measured at the
test sizes only:

- **U1, one shape:** Kepler's `compare_sharing` prefers a single Kelly skewness for all eight
  rules over one per rule, and that value is Gumbel's 0.2215.
- **U2, one amplitude ratio:** the interquartile range divided by the slope of the median in
  ln L is the same for all eight, and equals 1.5725 / 2 = 0.786. That is the Gumbel value for the
  largest of L^2 independent times, whose location grows as 2 tau ln L.

Settling times were jittered by up to half a generation (seeded) before taking quantiles, as
registered: several rules settle within 30 to 50 generations, with spreads of a few generations,
where quantiles of whole numbers would be biased. The run took 90 minutes on four cores (2400
runs, every one settled). It was slowed by one rule, hexagon B134/S01345, whose soups on a
512 torus settle within 33 to 59 generations into many oscillators. Their combined periods
run to 2520, 27720 (the lcm of 1 to 12) and 47880, and confirming a repeat means waiting out a
whole period.

**Per rule.**

| Lattice | Rule | median at 128 / 256 / 512 | log law (p) | power law (p) | IQR: observed vs Gumbel | Kelly skewness | IQR / slope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| square | B3567/S248 | 294 / 337 / 358 | 0.19 | 2e-4 | 38.3 +- 3.1 vs 49.6 (z = -1.4) | 0.18 +- 0.06 | 0.84 +- 0.09 |
| square | B358/S034 | 162 / 180 / 201 | 0.43 | 8e-4 | 20.6 +- 1.5 vs 30.0 (z = -2.4) | 0.11 +- 0.07 | 0.74 +- 0.09 |
| hexagon | B1/S126 | 32 / 35 / 41 | 0.18 | 1e-4 | 4.1 +- 0.3 vs 5.5 (z = -2.5) | 0.29 +- 0.07 | 0.66 +- 0.07 |
| hexagon | B134/S01345 | 27 / 32 / 37 | 0.86 | 1e-4 | 5.3 +- 0.4 vs 5.0 (z = +0.5) | 0.06 +- 0.07 | 0.74 +- 0.07 |
| triangle, edge | B123/S012 | 64 / 72 / 79 | 0.04 | 2e-4 | 8.8 +- 0.6 vs 13.4 (z = **-3.4**) | 0.13 +- 0.07 | 0.82 +- 0.08 |
| triangle, edge | B23/S013 | 41 / 45 / 50 | 0.52 | 7e-4 | 5.2 +- 0.5 vs 6.6 (z = -1.6) | 0.25 +- 0.06 | 0.75 +- 0.09 |
| triangle, edge+vertex | B2,5,7,8,10/S0,2,7,8,9,10,11 | 46 / 50 / 55 | 0.24 | 1e-4 | 5.3 +- 0.4 vs 6.9 (z = -1.8) | 0.22 +- 0.06 | 0.77 +- 0.09 |
| triangle, edge+vertex | B3,7,8,9/S0,5,6,9,12 | 134 / 152 / 172 | 0.18 | 7e-6 | 23.9 +- 1.8 vs 30.2 (z = -1.8) | 0.16 +- 0.06 | 0.88 +- 0.09 |

- **Laws.** The logarithm passed for every rule and the power law failed for every rule
  (p <= 8e-4). The other four laws failed too.
- **Mechanisms.** The heavy-tailed mechanism failed for all eight: every rule's fluctuations
  are between a third and a half as wide, relative to the median, as a power law's tail
  implies. The Gumbel mechanism passed for seven of the eight. It failed for triangle-edge B123/S012, which is
  B2/S34's failure again: the spread is smaller than tau = slope/2 predicts, with the slope
  fitted on small tori.
- **A pattern in that failure.** The predicted spread is too large for seven of the eight rules
  (z < 0). The slope fitted on tori of 8 to 64 overstates the slope at 128 to 512, as Study A's
  did, so a spread predicted from it overshoots.

**Across rules.**

| claim | measured | prediction | outcome |
| --- | --- | --- | --- |
| U1: one Kelly skewness | one constant preferred by 13 BIC points over eight (p = 0.23 against one per rule); value 0.177 +- 0.023 | 0.2215 (z = -2.0) | **confirmed** |
| U2: one IQR per unit slope | the eight ratios agree (chi-square 5.1 on 7 degrees of freedom, p = 0.64); value 0.765 +- 0.029 | 0.786 (z = -0.7) | **confirmed** |

Measured at the test sizes alone, the ratio of spread to growth is the same on the square, the
hexagon and both triangular lattices, for rules with nothing in common but settling. It is the
number the largest of about L^2 independent light-tailed times gives. The shape is shared too,
and consistent with Gumbel's, though it sits two standard errors low. U2 explains the per-rule
misses. For seven rules the slope fitted on small tori is steeper than the slope at the test
sizes (38 against 28 for B358/S034, 17 against 11 for B123/S012), so a spread predicted from it
is too large. The eighth, B134/S01345, is the one whose slope rose (6.4 to 7.1), and the one
whose spread came out above its prediction. Measured together, spread and slope agree with
Gumbel.

**What Kepler's identify says.** Asked blind which known numbers the shared values match, it
cannot single one out at these error bars:

- **The shape** (0.177 +- 0.023): 366 candidates match, the simplest being 1/5, 1/6 and 1/7,
  with chance probabilities of 0.75 and above. Gumbel's Kelly skewness is the 21st, level with
  2D percolation's beta.
- **The ratio** (0.765 +- 0.029): 467 candidates match, the simplest 3/4 and sqrt(2/3). The 2D
  Gumbel ratio is the 12th, level with directed percolation's nu_perp.

The registered tests confirm consistency with Gumbel. Naming the class from the numbers alone
would need error bars five to ten times smaller: about 25 to 100 times the seeds.

**B2/S34 against the rest (after the fact).** Study A's ratio, 0.64 +- 0.04 over 192 to 1024,
is 2.5 standard errors below the eight rules' 0.765. A heavier tail prefactor cannot lower the
ratio (see the correction above). So either B2/S34's local times are not independent and
identically distributed on large tori, or the eight rules' sizes, 128 to 512, are still short
of where theirs falls too. Measuring the eight on tori of 1024 and 2048 would tell.

## What this does and does not establish

- **Replicated:** B2/S34's median settling time on hexagon tori is logarithmic in the size up
  to 1024, and a power law is ruled out there. The example lab's answer was right.
- **The same law on every lattice:** for eight rules drawn at random from four lattice types,
  the log law held and the power law failed, on tori up to 512.
- **One shape and one amplitude ratio across lattices**, both consistent with the Gumbel law for
  the largest of about L^2 independent light-tailed times. This is the registered universality
  claim, and it held. It is a universality of extreme-value statistics, not of a critical point.
  Directed percolation and the other critical classes concern transitions tuned by a rate; these
  rules have none, and their settling time is not a critical quantity.
- **A mechanism tested, not just a curve.** The registered mechanisms predicted the
  fluctuations from the medians' own law, with nothing fitted to the fluctuations. That is a
  stronger test than the curve alone. It separated the two laws a second way (the power law's
  mechanism fails on spread and shape), and it found something the curve could not: the
  light-tailed extreme-value picture gets the shape and the constancy right but not the size.
- **What is not settled.**
  - Per rule, the Gumbel spread predicted from small tori is too large for seven of the eight
    rules, and significantly so for two (B2/S34, triangle-edge B123/S012).
  - The shared shape sits two standard errors below Gumbel's.
  - B2/S34's ratio is low.
  - Kepler's identify cannot name the class at these error bars.
- **What is post hoc.** The falling slope, B2/S34's ratio and far tail, and the refinement were
  seen after the verdicts. They are hypotheses for a next registered round, not results.
- **Novelty, as far as a web search went.** Life soups' lifespans are known to have roughly
  exponential tails (Johnston 2009, on 20 x 20 tori). Their growth with grid size has been
  studied qualitatively (an ECAL 2005 paper; an APS 2023 abstract). Nothing found ties settling
  times to extreme-value statistics, or tests the amplitude that ties a log law to its
  fluctuations.
- **Who did what.** Kepler's ranking (through the loop) found the log law in the first place.
  The mechanisms, the decision rules and the refinement are reasoning added here. The quantile
  tests and the Gumbel constants are now library code (`lattice_lab.extremes`, Kepler's KNOWN),
  so later studies can reuse them.
