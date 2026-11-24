# Scaling up: a ladder from a rule to its large-scale law (plan)

**Status:** a plan, written 2026-11-23. **Steps 0 to 3 are done, and the birth tie-break is a
setting.** The instrument is calibrated (`examples/scale-up-linear`, 296 of 296 registered
cases held), and it now lives in LatticeLife (`experiments.coarse`), which reproduces the
calibration's 3,084 records to the last bit. LatticeLife's update rule takes four kinds of
tie-break, two of them deterministic. Several species run without the app, and a registered
test of the tie-break held on all 15 predictions (`examples/scale-up-tie-break`): it matters
only where contests are common. Laws fitted for two worlds on grids of side 32 to 256 were
then tested on grids of side 512 to 4096 (`examples/scale-up-sizes`,
`examples/scale-up-sizes-large`): all 124 registered predictions held. One sample in that test
ran high against the other large grids, so a further registered test on fresh starts asked
whether the large grids agree with each other (`examples/scale-up-gap`): all nine predictions
held, and nothing creeps with the size of the grid. Step 4, the zoom-out, has its instrument,
a first look and a registered test (`examples/scale-up-closure`: 43 of 45 predictions held):
zoomed out, these worlds are maps of where things still move, with one exact law and a rule
that is nearly the same at every time but not at every scale. A search of the lab's rule
sets for a world organised over a growing distance, which those two are not
(`examples/scale-up-search`, exploratory), found that a rule alone seldom makes one, that
most of what grows alone is one kind of ground taking the whole grid, and that one rule in
six sorts into growing territories when it meets a copy of itself: which rules has little to
do with what they do alone and much to do with how few of its own kind a cell needs to be
born. A registered test of that on 600 rules no run had used held on all ten predictions
(`examples/scale-up-territories`). Step 5 is not built. The decisions that are yours are at
the end.

## What the ladder is for

Every result in this repository is about one grid size at a time. The question here is what a
rule does as the grid gets large, and whether that can be found from small grids. Simulating the
large grid directly stops being possible very quickly, so the method is to zoom out one step at
a time and check each step:

1. **Zoom out.** Replace each block of b x b fine cells by one supercell, and count T fine
   generations as one coarse generation.
2. **Propose a coarse rule** on the supercells: an exact rule where one exists, otherwise a law
   fitted by Kepler.
3. **Test it.** From the same start, take two routes and compare them supercell by supercell:

   ```
   fine start ──── run T·s generations ────> fine grid later
       │                                          │
    zoom out                                   zoom out
       ▼                                          ▼
   coarse start ── run s coarse generations ─> must match
   ```

4. **Repeat** with the coarse rule as the new fine rule. Each rung cuts the cost by about
   b² · T, so a few rungs reach sizes the fine rule never could.

What it measures:

| Quantity | Meaning |
| --- | --- |
| closure error | the share of supercells where the two routes differ, after s coarse generations |
| horizon | how many coarse generations pass before the closure error reaches what chance gives |
| what survives | how many details of the fine rule the coarse rule still needs |
| classes | which different fine rules land on the same coarse rule |
| fixed points | a rule that stops changing from rung to rung: that rule is the large-scale law |

Each rung is tested the way the rest of the lab is: predictions for sizes and seeds nobody has
run, written to a ledger and pushed before the run.

This measures whether a simpler world stands in for a finer one, in these automata. It says
nothing about physics.

## Step 0: calibrate the instrument on linear rules (registered; calibrated)

`examples/scale-up-linear`. The instrument is `scaleup.py`: worlds, projections and the closure
test, on LatticeLife's own update rule. Before its count is trusted on rules whose answer nobody
knows, it is tried where the answer is a theorem.

For a rule that is linear over GF(2), the library already proves both halves
(`proofs/LatticeProofs/GroupRing.lean`):

- `gstep_iterate_two_pow`: 2^k generations are one generation of the same rule with every
  neighbour 2^k cells away;
- `restrict_iterate`: each coset of the sublattice 2^k Z² then runs as a copy of the rule on the
  torus 2^k times smaller.

So zooming out by 2^k with the clock slowed by 2^k is exact, and the coarse rule is the fine
rule itself. A parity rule is its own large-scale law at every power of two: a fixed point of
the ladder.

The study registers three kinds of prediction, on LatticeLife's four parity rules (B1357/S1357
and B1357/S02468 on the square, B135/S135 and B135/S0246 on the hexagon):

| | Prediction | Cases | Sizes |
| --- | --- | --- | --- |
| H0, the mechanism | on one grid, 2^k generations equal one generation with neighbours 2^k apart: no cell differs | 32 | 2^k from 2 to 128, sides 48 to 320 |
| H1, the known zero | zoomed out by b = 2^k, no supercell differs at any coarse generation, for three ways of reading a supercell (a corner cell, another fixed cell, the block's parity) | 228 | b from 2 to 128, fine sides 10 to 768 |
| H2, the known half | where the scales do not match, every supercell is a fair coin, and the total over 64 starts lies in an exact binomial interval | 36 | a block of 3, a clock one generation early, at half speed, one generation late, and the wrong coarse rule |

H0 and H1 are the two theorems above. H2 is there because an instrument that always answered
zero would pass them. It is not in Lean: `mismatch.py` works out, from the group ring by
machine, how many of the supercells' coins are independent, and its ranks matched the engine's
own in every case tried on small grids. A control is registered only where all the coins, or all
but one, are independent, since the total is then a binomial count. Four candidates failed that
and are listed in the question as left out. A correct instrument fails a given control by chance
less than once in a million runs.

What was seen before registration is declared in the question: the instrument was written and
tested on fine sides 12, 16, 18 and 24, and no registered case uses them.

**The run (2026-11-23, 3.5 minutes on one core): calibrated.** Every case held.

| | Cases | Held | What the records show |
| --- | --- | --- | --- |
| H0 | 32 | 32 | no cell differed |
| H1 | 228 | 228 | no supercell differed; with H0, 10,105,746 comparisons, and between 20% and 80% of supercells live in every one, so none was a comparison of two dead grids |
| H2 | 36 | 36 | every total inside its interval; the shares that differed ran from 0.4959 to 0.5046, and over all controls 820,478 of 1,640,448 |

Two things the records show that were not registered as tests:

- Where the group ring gave all but one coin independent, it also said every start's count
  must be even. All 768 such counts are even. Of the 1,536 counts where every coin is
  independent, 760 are odd.
- The spread of a control's 64 counts is the binomial spread: the ratio of the two variances
  has a median of 1.03 over the 36 controls, and runs from 0.63 to 1.39.

```bash
uv run --no-sync lattice-lab verify --lab examples/scale-up-linear
```

The verdict shows that the instrument reports a true zero as zero, and a true half as a half
within its exact interval. It does not show that any other rule can be coarse-grained.

The triangle is left out. Its rule is a 2 x 2 matrix M with M² = s I, and Frobenius scales s,
not M, so the zoomed-out clock should count pairs of generations. That is untested, and is a
small registered study of its own.

## What exists today

From a reading of the pinned LatticeLife (`256450b`) and Kepler (`0af9b28`) on 2026-11-23.

| Need | Exists | Missing |
| --- | --- | --- |
| zooming out | LatticeLife `experiments.coarse` (since step 1): square and hexagon, a sampled cell, a block's parity, each species' count and the leading species | the triangle |
| the closure test | `coarse.closure` and `run_closure`: two deterministic routes, compared exactly | cells with more than two states; coarse rules that are probabilistic |
| competing species without the app | LatticeLife `experiments.competition` (since step 2): a start with chosen shares, a run under a named tie-break, and a record of each species' cells, births, mixing and extinction | layouts other than a uniform mix (half and half, stripes) |
| a start of your choosing | `species_start`: a density and a share for each species, every cell independently | half and half, stripes |
| the birth tie-break | a setting since 2026-11-23: `random` (as before), `standoff`, `strongest`, `weighted`; contested cells counted every generation | a hidden layer; noise in the rule |
| domains and fronts | cluster counts, damage spreading; since step 2 the adjacent pairs of two species and of one (how mixed the species are), and the generation each species died out | domain size, front speed |
| large grids | one update rule, about 55 ns per cell per generation for one species, 93 for two and 125 for three (measured at 512 x 512). Since step 1 a wrapped adjacency is built without loops: 2.5 seconds at 4096 x 4096 | nothing up to 4096 x 4096 |
| reversible rules | nothing; the engine keeps one generation | a second-order wrapper (step 5) |
| growth laws | Kepler: `power`, `logarithmic`, the relaxation laws, `fit_replicates` | nothing |
| a win probability against a starting share | Kepler: `logistic_p` with a binomial likelihood | nothing |
| the same law across rules or lattices | Kepler: `fit_groups`, `compare_sharing` | nothing |
| conserved quantities | Kepler: `find_invariants` | wiring it to second-order runs |
| a probabilistic coarse rule | since step 4, tables of what came next in `examples/scale-up-closure/zoom.py`: several species, several alphabets, four views of a neighbourhood, scored on starts they did not learn from and run on by themselves | a closed form for a table (Kepler), should one show up; a home in LatticeLife |
| registered tests | `lattice_lab.study`; since step 1 `verify` reruns the records of a study that names `rerun` | nothing |

Two things turned up that you should know about:

- **The competitive world was not a function of the grid alone.** With one species the update
  is deterministic. With two or more, a dead cell that two species could both be born into went
  to one of them by a random draw (`core/lattice.py`, the birth step). A run was reproducible
  from its seed, but the next grid depended on the random stream as well as the present grid.
  That matters for anything said about determinism or reversibility of that world. It was
  decision D1, and the tie-break is now a setting: the draw is still the default, and two of
  the other kinds make the world a function of its grid.
- **The local checkouts were behind the pins.** `~/Documents/dev/latticelife` was at
  `15aa710`, seven commits before the pinned `256450b`; step 1 fetched it and left it on
  `coarse-graining`. `~/Documents/dev/kepler` still points at the old `tripptytrip` remote and
  has no `src/kepler` at all, so a Kepler build starts by fetching.

## Build changes, in order

Each step ends in a gate. A step is not started until the gate before it has passed.

### Step 1: give the instrument a home in LatticeLife (done 2026-11-23)

**In LatticeLife** (`PolyLabs-research/gameoflife_advanced`, branch `coarse-graining`, commit
`d690cae`, one commit on the working branch the old pin was on):

- **`experiments/coarse.py`**, from `scaleup.py`: the block geometry (`coarse_grid`,
  `sample_cells`, `block_cells`), the projections, worlds, and the closure test, with resumable
  JSONL records in the house form (`ClosureTask`, `closure_point`, `run_closure`). Grids may be
  rectangles, as everywhere else in LatticeLife.
- **Two projections for species:** `block_counts`, each species' cells per block, and
  `leading_species`, the species with the most. A block with no live cell, or with two species
  level at the top, has no leader.
- **`build_adjacency(..., dilation=k)`**, and wrapped grids built in whole-array operations.
  The array is the one the per-cell loops gave, cell for cell and in the same order, on every
  shape: the tests compare the two over a range of sizes, and a wider check of 648 grids up to
  20 x 20 found no difference. A 512 x 512 grid builds about fifteen times faster and a
  4096 x 4096 one in 2.5 seconds.
- **Stable interface:** new names only, added to `test_stable_api.py` and the changelog.
- **Tests:** LatticeLife's whole suite passes, 1,190 tests with the new ones.

**In lattice-lab** (branch `scale-up-step-1`):

- **The pin** moved to `d690cae`, and on to `456e044` when the tie-break was built (below).
- **`Study.rerun`**, an optional fifth thing a study names: one stored record computed again.
  `lattice-lab verify` reruns sample records of a study that has it, as it always has for the
  loop's own records. `study.load(DIR)` gives the study a lab directory holds. The calibration
  has the hook.
- **`examples/scale-up-linear/promote.py`**, the gate.

**The gate: passed.** Every record of the calibration's registered run, through
`latticelife.experiments.coarse`: 3,084 of 3,084 identical (`promotion.json`). On the new pin
lattice-lab's own suite has no new failure (524 pass; the 9 that fail here are the 8 that need
the optional SCIP install and the one timing test, as before), and `verify` finds no problem in
any of the 35 ledgers: the older labs' LatticeLife sweeps rerun byte for byte.

### Step 2: the competitive world without the app, and a first look (started 2026-11-23)

**Built.** LatticeLife `experiments/competition.py` (branch `competition`, commit `f0ee136`,
which lattice-lab pins): `species_start` seeds a wrapped grid with a density and a share for
each species; `competition_point` runs it under a named tie-break and records, at chosen
generations, each species' live cells and births, the adjacent pairs of two species and of one,
the contested cells, and the generation each species died out. LatticeLife's suite passes with
it (1,293 tests).

**The first look** (`examples/scale-up-compete`, exploratory, the random draw only):

- **Life-like pairs coexist.** Conway's Life against itself and against HighLife, 128 x 128,
  16 starts each: no species was lost in 600 generations. The live fraction falls from 0.50 to
  0.14 by generation 50 and is still falling at 600 (0.060 and 0.055). Only 3% of adjacent live
  pairs are of two species, so they sit in separate patches. One species' share of the live
  cells wanders between runs, by 0.07 to 0.09 either side of a half.
- **Soups stay active.** Twelve five-species soups with rules drawn as `autorun` draws them,
  64 x 64, 8 starts each: the live fraction at generation 200 is between 0.27 and 0.92, and
  in most soups it has settled by generation 40. Two to five species survive, and contests are
  from 0.3% to 75% of births.

So the plan's picture of this step was partly wrong. With these rules nobody wins: there is no
"chance of winning against the starting share" and no generation "at which one species is
left" to fit a law to, and a front is not what separates the patches. What can be measured
against time and size is the live fraction, the species balance and its spread, and the mixing.

**The registered test of the tie-break** (`examples/scale-up-tie-break`; registered and run
2026-11-23, 3,584 runs in 12 minutes on one core). The random draw against the standoff, from
the same starts. All 15 predictions held.

| Claim | Worlds | Prediction | Result |
| --- | --- | --- | --- |
| S, a known answer | Life against itself, 128 x 128, 128 starts | two species with the same rule end level, under either tie-break | species 1's share at generation 600 averages 0.509 under the draw and 0.494 under the standoff; one half is inside both 99.9% intervals |
| A, no difference where contests are rare | Life against itself and against HighLife, 128 starts each | the standoff's mean is within a margin of the draw's, for the live fraction at generations 100, 300 and 600, the species balance and the mixing | all ten inside their margins; the largest difference in live fraction is 0.003, 4% of its value |
| B0 | the 5 soups (of 24) where contests are 1% of births or less | no difference in live fraction beyond 0.02 | the largest difference is 0.001, and no interval reaches 0.007 |
| B1, B2 | the 9 soups where contests are a fifth of births or more | the tie-breaks differ in at least three quarters, and the standoff lowers the live fraction by more than 0.02 in at least half | they differ in all 9, and the standoff lowers it in all 9, by 0.04 to 0.46 of the grid (6% to 75% of its value) |

Contests were 0.41% of births in the pairs, under both tie-breaks, and no species died out in
any of the 512 runs.

Three things in the records that were not registered:

- **The drop follows the contested share.** Over all 24 soups the rank correlation between the
  share of births contested under the draw and the change in live fraction is -0.82. Of the
  ten soups between the two groups, six differ: in five the standoff lowers the live fraction,
  in two of them by more than 0.02, and in one it raises it, by 0.008.
- **One interval in the pairs excludes zero.** For Life against itself at generation 300 the
  standoff's live fraction is lower by 0.003 (0.0005 to 0.005). It is inside its margin, and
  one such interval in ten is not surprising, but it may be a small real effect.
- **The standoff costs some soups a species.** In four soups fewer species survive under the
  standoff, by half a species to one on average. That is a difference in kind as well as in
  amount.

**Laws against time and size** (`examples/scale-up-compete/laws.py`, exploratory, run
2026-11-23: 672 runs in 13 minutes on one core). Two worlds, as you chose: Life against
HighLife under the standoff, and soup 19 of the tie-break test under both tie-breaks. Soup 19
is the one with the most contested births (68% under the draw) among those in which the
standoff did not cost a species. Seven sides from 32 to 256, 32 starts at each, Kepler's laws.

| Quantity | Life against HighLife, standoff | Soup 19, the draw | Soup 19, the standoff |
| --- | --- | --- | --- |
| live fraction against time, at side 256 | falls as c + a (1 + t/τ)^-b towards c = 0.042 (0.040 to 0.044), with τ = 75 and b = 1.3 | settles as c + a exp(-t/τ) to c = 0.766, with τ = 39 generations | the same form, to c = 0.500, with τ = 15 |
| mean live fraction against the side | does not depend on it: 0.0486 ± 0.0003 at generation 1,000 | does not: 0.7662 ± 0.0001 | does not: 0.4999 ± 0.0004 |
| mean share of species 1 | does not: 0.562 ± 0.002 (Life holds 56% of the live cells) | does not: 0.1732 ± 0.0002 | does not: 0.185 ± 0.002 |
| mean unlike share of adjacent pairs | does not: 0.027 ± 0.001 | does not: 0.6388 ± 0.0002 | does not: 0.3947 ± 0.0006 |
| spread over the starts, as a power of the side | -1.01 ± 0.08, -1.00 ± 0.07, -0.94 ± 0.08 (live, share, unlike) | -1.03, -0.99, -0.97, each ± 0.07 | -0.92 ± 0.07, -0.89 ± 0.10, -0.96 ± 0.07 |
| every species alive at the end | in all 224 runs | in 2 of 32 runs at side 32, rising to 29 of 32 at 256 | in 1 of 32 at side 32, rising to 26 of 32 at 256 |

What this says:

- **Bigger is more of the same.** No mean depends on the side: `constant` is the law Kepler
  ranks first for all nine, though a weak trend is not excluded (the next law is within 2 BIC
  points every time). All nine spreads fall as one over the side, each exponent within two
  standard errors of -1. That is what a grid made of independent patches does: nothing in
  these quantities is organised over a distance that 256 cells can see.
- **One thing does depend on size: which species survive.** In the soup one species of five
  (B4/S3) dies out on small grids and survives on large ones. The share of runs keeping all
  five follows a logistic curve in the logarithm of the side, reaching one half at side 124
  under the draw and 157 under the standoff. The form 1 - exp(-(side / L0)^d) fits as well,
  with d = 1.86 ± 0.22 and 1.86 ± 0.25: within one standard error of 2, as if each patch of
  the grid had its own small chance of keeping the species. No species was lost in the pair
  at any size.
- **That one thing is a lottery of the start** (found on 2026-11-23 in the same records,
  while preparing step 3). What is left of B4/S3 never changes after generation 20 and is
  always a multiple of four cells: 2 x 2 blocks. Nothing can break a block, because a cell is
  only ever born into an empty place and each species counts its own kind alone. So the species
  lives on when at least one block forms in the first generations, and is gone by generation 3
  when none does. The blocks are as dense at every size, 44 per million cells under the draw
  and 27 under the standoff, and their number scatters over the starts as independent events
  do (variance over mean 1.02 and 1.12). That density gives the survival seen at each side
  with nothing fitted to survival: under the draw 1.4, 3.1, 5.2, 10.6, 16.3, 25.6 and 30.2
  starts of 32, against the 2, 2, 4, 11, 18, 22 and 29 seen. So this is more of the same too:
  a large grid keeps the species because it has room for a block, and the logistic curve was
  a description of that, not a law of its own.
- **The two worlds relax differently.** The pair's live fraction falls slowly, as a power of
  time; the soup's settles exponentially, in tens of generations.
- **The standoff halves the soup's contests** as well as lowering its live fraction: 72% of
  births are contested under the draw and 34% under the standoff, at every size.

These are fits to the data that chose them, so they are descriptions, not tests. The pair's
c = 0.042 is where its curve points beyond generation 1,000, which nothing here checks.

**Gate: passed.** Laws with error bars at seven sizes, and the known answer (S, above) held.

### Step 3: the registered scale-up test (done 2026-11-23)

**Registered 2026-11-23**, in two parts from one set of laws, before either was run, so that
neither part's predictions can lean on the other's results:

- `examples/scale-up-sizes`: sides 512 and 1024, 32 starts each, run here;
- `examples/scale-up-sizes-large`: sides 2048 and 4096, 16 starts each, for a pod.

The same three worlds as the laws (Life against HighLife under the standoff, soup 19 under the
draw and under the standoff), from starts no earlier run used. Each part makes 62 claims, all
read from the step-2 fits (`examples/scale-up-compete/laws/results.json`, hashed into the
question):

| Claims | What is predicted at each new side |
| --- | --- |
| mean (22) | the mean over the starts of the live fraction, of species 1's share and of the unlike share of pairs is the constant fitted at sides 32 to 256; in the soup, so is the rare species' share of the grid (174 cells per million under the draw, 110 under the standoff) |
| spread (22) | the spread of each over the starts is an amplitude over the side: the exponent held at -1 and the amplitude fitted at sides 32 to 256. For the rare species nothing is fitted: independent blocks give a spread of sqrt(4 x density) / side |
| survival (6) | every species is alive at the end in at least 31 of 32 starts at side 512 under the draw, in at least 30 under the standoff, and in every start at the larger sides; the pair loses no species |
| time (12) | the live fraction's law against time, refitted at the new side, settles where it did at side 256 and as fast: c and b of c + a (1 + t/τ)^-b for the pair, c and τ of c + a exp(-t/τ) for the soup |

A claim holds when the measurement is within 3.29 combined standard errors of the law's value
(the 99.9% level). The level is strict because a part makes 62 claims: at it, laws that are
exactly right fail a claim in about one part in sixteen. Spreads are compared in logarithms.

Two things changed from what this section said before the registration, both worked out from
the step-2 records alone:

- **The spreads are tested as one over the side exactly**, not as the fitted power with its
  own error. That is the claim itself, and it is sharper: at side 4096 the fitted powers would
  have allowed a spread anywhere within a factor of 3 of the law, and this allows 1.9.
- **Survival is predicted from the blocks' density**, not from the logistic curve. The curve
  gave "at least 24 of 32" at side 512, which is less than the 29 of 32 already seen at 256;
  the density gives "at least 31 of 32", and adds a test that still means something where
  every start survives: the rare species' share of the grid, and its spread.

**A dry run on data already seen.** The same code, with laws fitted to the smaller step-2
sides and judged at the larger ones (up to 192 judged at 256; up to 128 judged at 192 and 256;
up to 96 judged at 128, 192 and 256): every claim held, the largest gap was 2.4 standard
errors, and 5 of 168 were above 2, which is what chance gives. This checks the method, not the
laws, which were chosen on this data.

- **Where it runs:** 512 and 1024 here on two cores; 2048 and 4096 on a RunPod CPU pod
  (`docs/runpod-setup.md`), because of this machine's heat limit. A run at side 4096 takes
  about 3 GB and 20 to 25 minutes on one core; the 96 runs of the large part were put at
  about 23 core-hours of this machine, and took 33 on the pod with fourteen at a time.
- **Gate:** the verdict, whichever way it goes. A failure says where the small grids stop being
  a guide, which is the horizon the ladder is for.

**The run at sides 512 and 1024** (2026-11-23: 192 runs in 69 minutes on two cores). All 62
predictions held. The ledger verifies, and four records computed again came out byte for byte.

| Claims | Result at 512 and 1024 |
| --- | --- |
| mean (22) | all hold, none further than 1.2 standard errors from its constant. The soup's live fraction under the draw is 0.76608 ± 0.00008 and 0.76622 ± 0.00004, against 0.76615 ± 0.00013; the pair's at generation 1,000 is 0.04839 at both sides, against 0.04864 ± 0.00027 |
| spread (22) | all hold. The furthest is the pair's species balance at side 512: 0.0142 against 0.0104, 2.3 standard errors (at 1024, 0.0066 against 0.0052, 1.7) |
| survival (6) | every species alive at the end of all 192 runs |
| time (12) | all hold. The soup settles as fast as at 256: τ = 39.0 and 39.3 against 39.4 ± 0.6 under the draw, 14.5 and 14.9 against 15.1 ± 0.3 under the standoff. The pair's c and b come out about two standard errors below the values from side 256, at both sides (see below) |

The rare species is where the test had most to lose, and it held: under the draw it holds 165
± 9 and 162 ± 4 cells per million at the two sides, against the 174 ± 14 of the small grids;
under the standoff 119 ± 9 and 106 ± 3, against 110 ± 11. Every count is a multiple of four
and none changes after generation 20. A start at side 512 has 11 blocks on average under the
draw and 8 under the standoff, and none had fewer than two.

What the records show beyond the predictions (`examples/scale-up-sizes/extras.py`,
exploratory):

- **The errors quoted were the right size.** Of the 56 comparisons with a score, two are
  beyond 2 standard errors (2.5 expected by chance) and none beyond 3; their root mean square
  is 0.91, where 1 is exact.
- **One over the side, more tightly.** Refitted over all nine sides, the nine powers run from
  -0.92 to -1.03 with errors of 0.04 to 0.05, about half of step 2's. All are within 1.8
  standard errors of -1. The two furthest are both the species balance (the pair's, -0.92 ±
  0.05, and the soup's under the standoff, -0.93 ± 0.05), which is worth watching at the
  larger sides.
- **The means, more tightly.** `constant` still ranks first for all nine over nine sides, and
  the constants are now known three times better: the pair's live fraction 0.04841 ± 0.00008,
  the soup's 0.76619 ± 0.00004 under the draw and 0.5001 ± 0.0001 under the standoff.
- **The pair's law against time was loosely pinned at 256.** Sides 512 and 1024 give the same
  constants to three figures: c = 0.0395, τ = 51, b = 1.09, against 0.0425, 75 and 1.33 from
  side 256. The curves themselves agree: averaged over generations 500 to 1,000 the live
  fraction is 0.05106 ± 0.00029 on sides 128 to 256 and 0.05096 ± 0.00010 on 512 and 1024. So
  this is four constants trading against each other on a noisier curve, not the world changing
  with size, and the better values are the new ones: the pair is heading for a live fraction
  of 0.040, not 0.042, and nears it about as one over the time. The large part's predictions
  for c and b were registered from side 256 and cannot be changed; expect them to hold by the
  same two standard errors.

**What this does and does not show.** Laws fitted on grids up to 256 across predicted grids
four times as wide, in 62 ways, at the precision the starts allow. How much a mean could have
moved before its claim failed differs a great deal: 0.06% for the soup's live fraction under
the draw, 2% for the pair's live fraction and species balance, 8% for the pair's mixing, and
about a quarter for the rare species' density. A spread off by a factor of 1.6 would have
failed. It does not show that nothing is organised over longer distances than 1,024 cells,
and the sixteen starts of the large part will test the spreads less sharply (a factor of 1.9)
than this part did.

**The run at sides 2048 and 4096** (2026-11-23, on a rented machine: 96 runs in 2 hours 20
minutes, fourteen at a time, $2.57). All 62 predictions held there too, so every one of the
124 held, on grids from twice to sixteen times as wide as any the laws were fitted on. The
ledger verifies, and records computed again on this machine match the pod's byte for byte.

| Claims | Result at 2048 and 4096 |
| --- | --- |
| mean (22) | all hold, none further than 1.4 standard errors from its constant. The soup's live fraction under the draw is 0.76626 ± 0.00003 and 0.76623 ± 0.00002, against 0.76615 ± 0.00013 |
| spread (22) | all hold. The furthest is the rare species' share under the standoff at side 4096: 8.1 against 5.1 parts in a million, 2.4 standard errors |
| survival (6) | every species alive at the end of all 96 runs |
| time (12) | all hold. τ = 38.9 and 39.3 against 39.4 ± 0.6 under the draw, 15.0 and 14.7 against 15.1 ± 0.3 under the standoff. The pair's c and b are about one and a half standard errors below side 256's, as at sides 512 and 1024 |

The rare species' density is now known to a part in a hundred: 166 ± 2 cells per million under
the draw at side 4096 and 114 ± 2 under the standoff, against the 174 ± 14 and 110 ± 11 that
sides 32 to 256 gave. A start at side 4096 holds about 700 blocks under the draw and 480 under
the standoff, and every count at every side is a multiple of four.

Over all eleven sides (`examples/scale-up-sizes/extras.py`, exploratory):

- **The errors quoted were the right size** here as well: one of the 56 scored comparisons is
  beyond 2 standard errors (2.5 expected), none beyond 3, and their root mean square is 0.92.
- **One over the side.** The nine powers are -0.93 to -1.03, each ± 0.03 or 0.04. Seven are
  within about one standard error of -1. The pair's species balance (-0.93 ± 0.03, 2.4
  standard errors off) and its mixing (-0.95 ± 0.03, 1.8) fall a little more slowly, if
  anything.
- **The blocks may not be quite independent at the largest sizes.** The variance of their
  number over its mean is 1.9 and 1.3 under the draw at sides 2048 and 4096, and 0.8 and 2.4
  under the standoff, where independent blocks give 1 (give or take 0.4 with sixteen starts).
  The registered spreads held; this is a hint, not a finding.
- **The large grids against each other, and one sample that ran high.** A registered claim
  compares a large grid with the small grids' constant, whose error is several times the
  large grid's own. Set against each other instead, the four large sides agree for eight of
  the nine means (chances of 0.23 to 0.89 that one constant lies behind them). The ninth is
  the pair's live fraction: 0.04861 ± 0.00006 at side 2048 against 0.04827 ± 0.00002 at side
  4096, five of their own standard errors apart at generation 1,000 and three to five at
  every sampled generation from 200 on.

  That could have meant the world changes with size after all, so I checked it three ways.
  Sixteen fresh starts at side 2048 (`recheck.py`, exploratory) gave 0.04833 ± 0.00007: where
  sides 1024 and 4096 are, and 2.9 standard errors below the registered sample. Two of the
  registered runs, the highest among them, computed again on this machine came out byte for
  byte as the pod's, so the sample is real data and not a fault of the rented machine. And
  the starts are independent of each other and have no structure at the scale of 64 cells.
  So the registered sixteen starts at side 2048 ran high. With the fresh starts in their
  place the four sides agree (chance 0.48); with both samples together side 2048 is still
  3.5 standard errors above side 4096, which is 0.4% of the value and a chance of 0.004 over
  the four sides. I cannot tell from these runs whether that remainder is the same unlucky
  sample or a small real difference; more starts at side 4096 would settle it. None of this
  touches a registered claim: the largest of these gaps is under half of what a claim
  allowed.
- **The pair's law against time**, at the four large sides: c = 0.0395 to 0.0404, τ = 51 to 57
  and b = 1.09 to 1.16. The fit at side 256 (0.0425, 75, 1.33) was the loose one.

**What this does and does not show.** Three worlds, eleven sides and a factor of 128 in width:
what was measured on grids a person can watch predicted grids of 16.8 million cells, in 124
ways, with nothing fitted to the large grids. For these worlds bigger is more of the same,
and the one thing that seemed to depend on size, which species survive, was a count of
unbreakable blocks all along. It does not show that every rule set scales this way: two
worlds were chosen, one of them because its species coexist quietly. Nor does it reach a
world in which something is organised over a distance that grows, which is where a law from
small grids would have to fail, and where this ladder would earn its keep. Step 4 looks for
that from the other side: by zooming out.

**Gate: passed.**

### Step 3b: do the large grids agree with each other? (done 2026-11-23)

Step 3 left one thing open: with the registered and the fresh starts together, the pair's live
fraction at side 2048 was 0.0002 above side 4096's, 0.4% of its value. You asked for that to
be closed before step 4, because step 4 compares a world with its zoomed-out self, and a mean
that crept with the size of the grid would be in the way of that.

`examples/scale-up-gap`: Life against HighLife under the standoff, as in step 3, at sides
1024, 2048 and 4096 from starts no earlier run used: 384, 96 and 32 of them, which gives the
three sides' mean live fractions about the same standard error (0.000025). The test I
sketched in decision D7, sixteen more starts at two sides, would not have been enough: its
interval would have been as wide as the gap.

Nine predictions. For each pair of sides, the means at generation 1,000 differ by less than a
margin: 0.0002 for the live fraction (the gap seen), 0.0028 for species 1's share of the
live cells (0.5% of its value) and 0.00053 for the unlike share of adjacent pairs (2%). A
claim holds when the 99% interval of the difference lies inside the margin. If the sides
truly agree, all nine pass about 98 times in 100; a real gap of 0.0002 in the live fraction
fails its claim more than 99 times in 100.

- **Where it runs:** the same kind of pod as step 3's large part, about 24 core-hours of this
  machine.
- **Gate:** the verdict. If the claims hold, the means do not creep between sides 1024 and
  4096 by more than these margins, and the intervals say how much less. If the live
  fraction's claim for sides 2048 and 4096 fails, the gap is real and step 4 has to allow
  for it.

**The run** (2026-11-23, on a rented machine: 512 runs in 2 hours 11 minutes, sixteen at a
time, $2.49). All nine predictions held. The ledger verifies, and records computed again on
this machine, one of them at side 4096, match the pod's byte for byte.

| Mean at generation 1,000 | Side 1024 (384 starts) | Side 2048 (96) | Side 4096 (32) | Largest difference, and its 99% interval | Margin |
| --- | --- | --- | --- | --- | --- |
| live fraction | 0.048302 ± 0.000028 | 0.048330 ± 0.000026 | 0.048267 ± 0.000023 | 0.000064 (-0.000027 to 0.000154), sides 2048 and 4096 | 0.0002 |
| species 1's share of the live cells | 0.56143 ± 0.00032 | 0.56084 ± 0.00035 | 0.56114 ± 0.00017 | 0.00059 (-0.00064 to 0.00181), sides 1024 and 2048 | 0.0028 |
| unlike share of adjacent pairs | 0.026395 ± 0.000058 | 0.026390 ± 0.000053 | 0.026380 ± 0.000051 | 0.000015 (-0.00019 to 0.00022), sides 1024 and 4096 | 0.00053 |

What it says:

- **The gap is closed.** On fresh starts sides 2048 and 4096 differ by 0.00006 ± 0.00003 in the
  live fraction: a third of the 0.0002 left after step 3, and a fifth of what the registered
  samples first showed. A gap of 0.0002 is outside the 99% interval of every pair of sides.
- **Nothing creeps.** A straight line through the three sides, with the re-check's starts
  added at side 2048, changes by -0.00002 ± 0.00002 for each doubling of the side: 0.04% ±
  0.04% of the live fraction. The species balance changes by 0.02% ± 0.03% a doubling and the
  mixing by 0.03% ± 0.15%. The three sides are what one constant would give (chances of 0.16,
  0.49 and 0.86). These last figures are from `extras.py` and were not registered.
- **What is not excluded.** The largest difference is 1.8 standard errors from zero, and both
  fresh samples at side 2048 (16 and 96 starts) gave 0.04833, where side 4096 gave 0.04827
  twice. So a real difference of about a tenth of a percent between those two sides is
  possible. It is not a drift with size: side 1024 lies between them.
- **The sample that started this stands alone.** The registered sixteen starts at side 2048
  gave 0.04861, 4.2 standard errors above the 112 fresh starts at the same side. Its records
  reproduce here to the byte and its starts are independent of each other, so I have nothing
  but chance to put it down to, and at that distance chance is a poor explanation. It is a
  loose end in the bookkeeping, not in the world: every later sample at that side disagrees
  with it.
- **At generation 200**, where the gap first showed, the three sides are within 0.00002 of each
  other (± 0.00007).
- **The spreads** between these three sides fall as the side to the power -1.08, -1.16 and
  -1.04 (live fraction, species balance, mixing), each ± 0.08. Step 3's hint that the pair's
  species balance falls more slowly than one over the side did not repeat.

**Gate: passed.** For step 4, between sides 1024 and 4096 the pair's means can be taken as
constants to within 0.3% for the live fraction and for the species balance, and 0.8% for the
mixing: those are the widest ends of the 99% intervals above.

### Step 4: closure for the competitive world (first look and registered test, 2026-11-24)

**The instrument** (`examples/scale-up-closure/zoom.py`; in lattice-lab until it has earned a
place in LatticeLife, as step 0's did). A fine world is run once and read through b x b blocks
every b generations: the clock is the block. That is not a convenience. These rules move
information one cell a generation at most, so in b generations nothing from beyond a block's
eight neighbours can reach it, and what a block does next is a function of the fine cells of
its 3 x 3 neighbourhood. A coarse rule replaces those 9 b² cells by nine symbols, and its
errors are what that loses.

- **What a supercell records:** the leading species of its block (this plan's first idea),
  whether the block *moved* (any of its cells differs from one coarse generation before),
  whether it holds a live cell, or a pair of these.
- **A coarse rule** is a table learned from zoomed-out runs: for each thing a supercell and
  its neighbours can look like, how often the supercell was each thing next. It can look at
  nothing, at the supercell alone, at how many of its neighbours are each symbol, or at its
  neighbours in place. It is tried on starts it was not learned from, and scored two ways: how
  often its likeliest symbol came, and its surprise (the bits it would take to be told what
  came, given the chances it gave).

Two known answers, both tested on LatticeLife's own engine:

- **Stillness is stable.** In a world that is a function of its grid (several species under
  the standoff), a block whose 3 x 3 neighbourhood did not change over the last coarse
  generation does not change over the next: the same cells give the same cells. So no block
  may move out of stillness, and with the clock four blocks long some must be able to.
- **A world that is its own zoom-out.** With every neighbour b steps away, and a start that is
  uniform on each block, the zoomed-out run is the same rules on the small grid, cell for
  cell, and the table learned from it is LatticeLife's update rule, learned back.

**A first look** (`look.py`, exploratory, 2026-11-24: 48 fine runs and their analysis in half
an hour on two cores). The three worlds of step 3, sixteen fresh starts each, eight to learn
from and eight to try on: the pair on side 1024 for 1,024 generations, soup 19 on side 512
for 512 generations under the standoff and under the draw. Blocks of 4, 8, 16 and 32.

1. **Who leads a block says little, and what it says is frozen.** In the pair the leader of a
   block stays the leader: a rule that knows only the block is wrong 13 times in a thousand
   at block 4 and 50 at block 32, and no view of the neighbours improves on that. The leader
   map is heading for one species everywhere as blocks grow: nobody leads 72% of the blocks
   of 4 at the end (most are empty), and Life leads 63% of the blocks of 32.
2. **What is left to describe is where things still move, and movement has an exact law.**
   No block moved out of stillness in either standoff world, at any block, on any start.
   Under the draw one did, as it may.
3. **In the pair, movement follows the same rule early and late, if the rule looks at the
   neighbours.** The chance that a block of 4 moves in the next coarse generation, after
   generation 256:

   | Moving neighbours | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
   | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
   | a still block | 0 | 0.008 | 0.08 | 0.18 | 0.24 | 0.31 | 0.38 | 0.45 | 0.52 |
   | a moving block | 0.22 | 0.46 | 0.63 | 0.76 | 0.81 | 0.87 | 0.91 | 0.94 | 0.96 |

   Movement spreads from moving neighbours and dies without them. The table learned up to
   generation 256, when 15% to 29% of the blocks are moving, serves after it, when 1% to 5%
   are: it has 0.4% more surprise there than the table learned there (0.7% at blocks 8 and
   16). A rule that knows the block alone does not carry over: 65%, 56% and 51% more. Its
   chances have to change as movement thins out; the rule with neighbours has no need to.
   The agreement is not perfect: late chances are 5% to 15% higher than early ones, and an
   isolated moving block keeps moving more often late (0.22) than early (0.16).
4. **The neighbours sharpen the odds; they do not change the best guess.** The likeliest
   next symbol is always "as it is", whatever the neighbours are doing: neighbour counts
   remove under half a percent of the errors. They remove 38% of the surprise at block 4,
   28% at block 8, 18% at 16 and 10% at 32. Where the neighbours are adds little to how many
   there are: another one or two hundredths of the surprise.
5. **One number is the same at every block.** A still block with exactly one moving neighbour
   starts moving with a chance of 0.0081, 0.0076, 0.0078 and 0.0086 at blocks 4, 8, 16 and
   32, with the clock at the block. Every other chance in the table changes with the block.
   Something that travels at a steady speed would do this: with the clock at the block, how
   far it gets is the same share of a block at every scale.
6. **Run by itself, the coarse rule keeps up for a while and then loses the thread.** Started
   from the zoomed-out world at generation 128 and run by drawing from its own table, the rule
   with neighbour counts has 0.86, 1.09, 1.22 and 1.11 of the fine world's moving blocks eight
   coarse generations on (blocks 4 to 32). By generation 1,024 its movement has died at
   blocks 4 and 8 (the fine world still has 0.9% and 1.7% of blocks moving), while at block
   32 it ends about where the fine world does. A rule that knows the block alone cannot let
   movement die at all: it settles at 10% of the blocks of 4 moving, 12 times the fine
   world's. A richer symbol carries further: with who leads as well as whether it moved, the
   rule at block 4 still has 0.61 of the fine world's movement 64 coarse generations on,
   where the single bit has 0.03. Which blocks will have changed, as opposed to how many, no
   rule foretells better than "none": the likeliest-symbol run is the start, frozen.
7. **The soups.** Under the standoff the soup is not frozen: 8% of its blocks of 4 still move
   at generation 512. But its movers are isolated things that keep going by themselves (a
   moving block with no moving neighbour keeps moving with a chance of 0.97), so neighbours
   remove only 15% of the surprise at block 4 and nothing at block 16. Under the draw there
   is nothing to learn: every block of 8 or more moves in every coarse generation, and one
   species leads every block.

What this says about the ladder. Zoomed out, these worlds are a map of where things still
move, with one exact law and, for the pair, a simple rule that is nearly the same at every
time. It is not the same at every scale, apart from the one number, so the pair has no rule
that "stops changing from rung to rung". And the simple rule is not the whole story: real
movement dies out more slowly than the rule allows, because some movers last and the single
bit does not say which.

**The registered gate** (`examples/scale-up-closure/study.py`): whether what the first look
saw of the moving bit holds on a torus twice as wide (side 2048), from sixteen fresh starts,
and at a block twice as large (64) as any it used. 45 predictions in six families:

| Family | What is predicted |
| --- | --- |
| S, stillness (10) | no block moves out of stillness, at blocks 4 to 64 in the pair and 4 to 32 in the soup under the standoff; read with the clock four blocks long, some do |
| N, the neighbours' share (10) | after generation 256 neighbour counts remove the share of the surprise the first look found, within 0.02 (at block 64, between 0.02 and 0.08, by the trend), and under 2% of the errors |
| T, one rule at every time (6) | at blocks 4, 8 and 16 the rule with neighbour counts learned early has at most 2% more surprise late than the rule learned late; the rule that knows the block alone has at least 30% more |
| X, another torus (4) | the first look's rule, learned on side 1024, has at most 0.2% more surprise on side 2048 than the rule learned there |
| E, one number at every scale (5) | a still block with exactly one moving neighbour moves next with a chance between 0.006 and 0.011 at blocks 4 to 32, and between 0.005 and 0.012 at block 64 |
| H, the horizon (10) | run on by itself from generation 128: eight coarse generations on, the rule with neighbour counts has within 30% of the fine world's movement at every block; at the end the rule that knows the block alone has at least 2.5 times it, and at blocks 4 and 8 the rule with neighbour counts has under a tenth of it |

The records hold tallies, not grids, and every number in the verdict is recomputed from them.

**The run** (2026-11-24: 54 records in 47 minutes on two cores). 43 of the 45 predictions
held, and what the first look saw on side 1024 came back on side 2048 to three figures. The
ledger verifies, and three records computed again from scratch came out byte for byte.

| Family | Result |
| --- | --- |
| S, stillness | no block moved out of stillness: none in 902 million still neighbourhoods, in the pair at blocks 4 to 64 and the soup at blocks 4 to 16. With the clock four blocks long 8,700 did, of 5.9 million. **The soup at block 32 failed as registered:** it had no still neighbourhood in any start, so there was nothing for the claim to hold on |
| N, the neighbours' share | 0.376, 0.279, 0.176 and 0.096 of the surprise at blocks 4 to 32 (the first look: 0.375, 0.278, 0.175, 0.096), and under half a percent of the errors. **Block 64 failed:** 0.084, where the band drawn from the trend stopped at 0.08 |
| T, one rule at every time | the rule with neighbour counts learned early has 0.4%, 0.8% and 0.8% more surprise late than the rule learned late (blocks 4, 8, 16); the rule that knows the block alone has 64%, 54% and 47% more |
| X, another torus | the rule learned on side 1024 has at most 0.02% more surprise on side 2048 than the rule learned there |
| E, one number at every scale | 0.0081, 0.0077, 0.0075 and 0.0075 at blocks 4 to 32, and 0.0086 ± 0.0010 at the block of 64 that no run had been read through |
| H, the horizon | eight coarse generations on, the rule with neighbour counts has 0.86, 1.10, 1.21 and 1.10 of the fine world's movement; at the end the rule that knows the block alone has 11, 9, 6 and 3.5 times it, and at blocks 4 and 8 the rule with neighbour counts has none left |

The two failures are mine, and say different things:

- **The band at block 64 was a guess dressed as a trend.** Between blocks 4 and 32 each
  doubling took more off the neighbours' share than the one before, so I expected about half
  again and drew the band round that. It fell from 0.096 to 0.084. With the clock at the
  block, a block of 64 after generation 256 is at a different point in its life from a block
  of 4: two thirds of the blocks of 64 are moving then, against one in twenty of the blocks
  of 4. How much the neighbours tell depends on that as well as on the size, so the share
  against the block was never a law to extend.
- **The soup at block 32 was a claim that could not be tested.** The first look had already
  shown that the soup has no still neighbourhoods at that block, and I registered the claim
  anyway and wrote the judge to count nothing-to-test as a failure. Nothing moved out of
  stillness there, or anywhere.

**What step 4 shows.** Zoomed out, these worlds are not a contest between species: who leads a
block is frozen and tends to one species everywhere. They are maps of where things still
move. Movement cannot start where nothing around it moved, which is exact. In the pair it
spreads from moving neighbours and dies without them by a rule that is the same early and
late to within a percent of its surprise, the same on a torus twice as wide to within a
fiftieth of a percent, and has one entry that is the same at every block from 4 to 64. The
rule is not the same at every scale otherwise, so this ladder has no rung-to-rung fixed point
here. And it is not the whole of the fine world: run on by itself it keeps the right amount
of movement for about eight coarse generations, then lets it die too fast at small blocks,
because some movers last and one bit does not say which.

**Gate: passed** in the sense the plan gave it (the verdict, whichever way it goes), with the
two misses above on the record.

- **What it would take to go further:** symbols that carry more than one bit (who leads as
  well as whether it moved kept 0.61 of the fine world's movement where the single bit kept
  0.03, in the first look); a comparison of whole runs beyond the share of blocks moving;
  and a world where something is organised over a growing distance. Neither of these two
  worlds is one, and that is the main thing steps 2 to 4 have established about them.

### Step 4b: the search for a world that organises itself (exploratory, 2026-11-24)

Step 4 ended on what its two worlds lack: nothing in them is organised over more than a few
cells, at any age. You chose to look for a world that is different before spending more on
those two (decision D8). This is that search. **Nothing in it is registered.** It sorts
worlds on a small grid, picks candidates, and runs the picks again on a larger grid from
fresh starts. What comes out is a candidate for a registered test, not the result of one.

**The measure** (`examples/scale-up-search/organised.py`). Take the live cells, or one
species' cells, as a field of 0s and 1s with mean p. Cut the grid into b x b blocks and add
up each block. Were the cells independent, the sums would scatter with variance b² p (1 - p).
The **correlation area** at block b is how many times more they scatter than that:

    area(b) = variance of the block sums / (b² p (1 - p))

- It is 1 where cells are independent.
- As the block grows it levels at the number of cells that go together.
- Inside domains larger than the block it is the block's own area, b².

So three numbers describe a world: the area at the largest block, the power of the block it
is still growing as there (0 once it has levelled), and the power of time it grows as. A
pattern can be ordered without its sums scattering (a chequerboard puts the same sum in
every block), so the live cells are also read against three masks of +1 and -1 by turns:
chequered, rows and columns.

A fourth number says **which clock goes with a zoom-out** (`organised.clock`). If a world
seen through blocks twice the size, some number of times later, is the same picture, each
block's cells go together as they did, and the area, which counts cells, is four times what
it was. So

    area(2b, wait x t) / (4 area(b, t))

is 1 where the wait is the right one, under 1 where it is too short and over 1 where it is
too long. Step 4 took the wait to be 2, the clock at the block. A world of patches has no
such clock: its area does not move, and the number is a quarter whatever the wait.

The measure gives the answers that are known (`tests/test_scale_up_search.py`): 1 at every
block for independent cells; the block's own area inside tiles of 8 x 8 and 64 from there
on; 0 for a chequerboard, and b² against its own mask; a clock of four waits for a made-up
world whose domains have a side of the square root of its age.

**The screen** (`search.py`): 2,407 worlds, each once from a half-full mixed start (start
11001) on a wrapped grid of side 256 for 512 generations, read at generations 32 to 512
through blocks of 2 to 32. It took 59 minutes on two cores. By the field of its that has the
largest area at block 32 at the end, a world is called:

- **growing**: 16 cells or more, still growing as the 0.25 power of time or faster over the
  last three readings;
- **organised**: 16 cells or more, no longer growing;
- **patches**: less than 16 cells, which is what the worlds of steps 2 to 4 are;
- **dead**: nothing alive at the end, or nothing empty.

The thresholds sort, they do not claim. Of the 2,407 worlds, 132 repeat a rule already
drawn (the draws below say how), so 2,275 are different, and the table counts each once.
Nine in ten of them have an area under 6.6 cells; 107 have 16 or more, and half of those (53)
grow slower than the 0.1 power of time.

| Family | Worlds | Dead | Patches | Organised | Growing |
| --- | --- | --- | --- | --- | --- |
| known: Life, HighLife, Life against HighLife, soup 19, Vote, Anneal, Day and Night | 7 | 0 | 2 | 3 | 2 |
| soups of 2 species: 150 rule sets drawn as `latticelife autorun` draws them, under the draw and under the standoff | 300 | 5 | 282 | 5 | 8 |
| soups of 3 species, the same | 300 | 4 | 287 | 2 | 7 |
| soups of 5 species, the same | 300 | 1 | 282 | 12 | 5 |
| one species: 1,200 draws from all 262,144 rules, each count in the birth set and in the survival set with chance one half (1,196 different rules) | 1,196 | 42 | 1,108 | 26 | 20 |
| one species, near majority: 300 draws of a rule born and surviving at or above a threshold, with up to two counts changed (172 different rules, of the 2,056 there are) | 172 | 73 | 82 | 17 | 0 |
| all | 2,275 | 125 | 2,043 | 65 | 42 |

- **Growing is rare, and patches are the rule.** Nine worlds in ten are patches. 42 grow: 20
  of the 1,196 one-species rules (one in sixty) and 20 of the 900 soups (16 of the 450 rule
  sets under one tie-break or the other, 4 under both).
- **A soup that grows is mostly one species left alone.** A species holds ground if it has
  one cell in twenty at the end. Two or more do in 552 of the 900 soups, and nearly all of
  those are patches. Of the 20 growing soups, 9 have one species left and one has none, and
  those have the large areas (up to 450 cells); the 10 where two or more hold ground have
  areas of 18 to 60 cells.
- **Near-majority rules mostly freeze or die.** None of the 172 drawn grows: 73 die out or
  fill the grid, 82 are patches, and 17 organise and stop (in 13 of them nothing changes
  again), as Vote does. Anneal and Day and Night, whose domains keep growing, are both in
  that family (each is a threshold rule with two counts changed) and were not among the
  draws: growing is as rare there as anywhere.
- **Eight of the 20 growing rules are ordered in stripes**, found against the masks of rows
  and columns, and 12 in the live cells themselves.
- **The two worlds of steps 2 to 4**: Life against HighLife has an area of 7.5 cells, where
  step 3 read about 6 off the spread of its live fraction between starts. Soup 19 under the
  standoff is ordered in rows over about 50 cells and is not growing; step 4 did not look
  for that.

**The contests** (`contests.py`; 312 worlds, 12 minutes). A rule that grows alone is not yet
a competition, so each of the 29 one-species rules that grew (the 2 known, the 20 of the
even draw, and 7 that were the last species of a soup) got a rival: a second species with
the same rule. (Those 29 turned out to be the wrong place to look: "Every rule against its
copy", below, gives all 1,196 rules of the draw a rival.) In this lab a species counts only its own kind, so the two meet in two ways
only: a cell holds one of them at a time, and where both would be born into the same empty
cell the tie-break settles it. Each contest was run from a full start (every cell live,
half of them each species) and from a half-full one, under the draw and under the standoff,
on the screen's grid. The two species **keep apart** if their counts in a block go against
each other (a correlation of -0.5 or under over the blocks of 32); they hold **territories**
if they keep apart and one of them has an area of 16 cells or more.

| A rule against a copy of itself, 29 rules | Both dead | Mixed in patches | Organised, not apart | Standing territories | Growing territories |
| --- | --- | --- | --- | --- | --- |
| full start, the draw | 2 | 25 | 0 | 1 | 1 |
| full start, the standoff | 3 | 22 | 0 | 1 | 3 |
| half-full start, the draw | 2 | 24 | 2 | 0 | 1 |
| half-full start, the standoff | 3 | 22 | 0 | 0 | 4 |

- **A rival usually undoes the organisation.** In 93 of the 116 contests both species hold
  ground in patches, with nothing left of the domains the rule made alone. Anneal and Day
  and Night die against their own copy, from both starts and under both tie-breaks: each
  species needs a majority of its own kind around a cell, and its rival is in the way.
- **Four rules of the 29 hold growing territories against their copy**: B2378/S25678 from
  both starts under both tie-breaks; B015/S1 and B237/S025678 from both starts under the
  standoff; B2/S0 from the half-full start under the standoff (from the full one its
  territories form and stand).
- **The standoff makes territories where the draw mixes.** Seven of the nine contests with
  growing territories are under the standoff. B015/S1 and B237/S025678 are the same two
  worlds under both tie-breaks until a cell is contested: left empty, the species sort
  themselves apart; drawn for, they stay mixed. Step 2's registered test found that the
  tie-break changes a world only where contests are common. Here it decides what kind of
  world it is.
- **Different rules do not share a grid in territories.** The twelve strongest rules against
  each other, two at a time (132 contests): one species is left in 45, they mix in patches
  in 77, both die in 5, something is organised without their keeping apart in 4, and one
  pair of the 66 holds growing territories (B013/S1 against B015/S1, under the standoff).
  The four rules above against each other (12 contests): one is left, every time.
  Territories are a thing between species with the same rule.
- **Territories take more than two species.** The four rules as three species and as five,
  all with the one rule, from a full start (16 contests): B2378/S25678 holds growing
  territories with three and with five under both tie-breaks, and all five species keep
  ground (5% to 14% of the grid each); so does B237/S025678, more weakly under the draw;
  B2/S0's territories stand with three and grow with five; B015/S1's do not survive a third
  species (all die under the standoff, and mix under the draw). With n species sharing the
  grid out, one species' count in a block goes against another's as -1 / (n - 1), and that
  is what B2378/S25678 gives: -0.50 with three and -0.25 with five.
- **The species need not be the same, but they must be close.** B2378/S25678 against each
  of the 18 rules one count away from it, from a full start (36 contests). A rival with one
  count more takes the grid, whichever count it is (all nine, under both tie-breaks). A
  rival with one count fewer loses the grid if the count is a low one (birth on 2 or 3,
  survival on 2 or 5), and holds territories beside it if the count is a high one: birth
  on 7 or 8, or survival on 6, 7 or 8, under the draw, and all of those but survival on 6
  under the standoff. Without birth on 8, or without survival on 8, the two stay level to
  generation 512 (0.21 to 0.29 of the grid each); with the others the fuller rule gains
  slowly, so those territories are a slow takeover.

**The candidates again** (`confirm.py`). The screen and the contests each read a world
once on a small grid, and a world picked out of thousands for its reading has a reading that
flatters it. So the picks were run again where the reading did not pick them: 38 worlds on a
grid of side 1,024 for 2,048 generations from a fresh start (12001), read at generations 64
to 2,048 through blocks of 4 to 128. The picks are the seven known worlds; the ten
one-species rules with the largest areas in the screen, and the rules of the contests below;
the four soups with the largest areas in which two or more species hold ground, and the four
in which one is left; the four rules whose own contest held growing territories, each under
both tie-breaks; the one pair of different rules that did; and five copies of B2378/S25678.
A known world, a rule alone, a contest or a pair whose first start kept growing was run from
two more starts (56 runs in all; the six rules of "Every rule against its copy", below,
were added later, in 18 more).

The larger grid needs two more words than the screen had. A world **keeps growing** only if
the field that grows keeps its share of the grid. If that share moves by a fifth of the grid
or more, or its smaller side halves, one kind of ground is **taking over**: the growth is
real, and it ends when that ground has the grid. A world where it has is **taken over**.

| World | Kind, tie-break, start | Starts | Called | Field | Area at generations 64 / 256 / 1,024 / 2,048 | Power of time | Clock x2 / x4 / x8 | Share of the grid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Life | known, half | 1 | organised | live | 14 / 18 / 24 / 24 | -0.08 | 0.33 / 0.37 / 0.38 | 0.11 → 0.03 |
| HighLife | known, half | 1 | patches | live | 12 / 18 / 22 / 5 | -1.08 | 0.31 / 0.34 / 0.34 | 0.14 → 0.02 |
| Life against HighLife | known, standoff, half | 1 | patches | species 1 | 14 / 14 / 8 / 5 | -0.80 | 0.28 / 0.23 / 0.15 | 0.06 → 0.03 |
| soup 19 | known, standoff, half | 1 | organised | rows | 80 / 94 / 97 / 96 | -0.00 | 0.40 / 0.41 / 0.41 | 0.49 → 0.50 |
| Vote | known, half | 1 | organised | live | 33 / 33 / 33 / 33 | 0.00 | 0.28 / 0.28 / 0.28 | 0.50 → 0.50 |
| Anneal | known, half | 3 | keeps growing | live | 160 / 540 / 1,770 / 3,142 | 0.84 | 0.77 / 0.97 / 1.25 | 0.50 → 0.48 |
| Day and Night | known, half | 3 | keeps growing | live | 97 / 662 / 1,831 / 2,864 | 0.66 | 0.88 / 1.03 / 1.40 | 0.50 → 0.52 |
| B01245/S235 | alone, half | 1 | taking over | live | 211 / 684 / 1,572 / 2,153 | 0.47 | 0.73 / 0.90 / 1.06 | 0.30 → 0.02 |
| B0124578/S0134 | alone, half | 1 | taken over | live | 187 / 351 / – / – | – | – | 0.20 → 0.00 |
| B013/S1 | alone, quarter | 1 | dead | live | 44 / – / – / – | – | – | 0.01 → 0.00 |
| B456/S0124678 | alone, half | 1 | taking over | live | 10 / 194 / 5,606 / 4,534 | 0.65 | 1.41 / 4.21 / 8.36 | 0.93 → 0.06 |
| B012457/S14 | alone, half | 3 | keeps growing | live | 66 / 512 / 1,645 / 2,805 | 0.80 | 0.90 / 1.03 / 1.52 | 0.50 → 0.53 |
| B012358/S0125 | alone, half | 1 | taking over | live | 150 / 536 / 1,411 / 2,531 | 0.79 | 0.78 / 0.93 / 1.10 | 0.64 → 0.92 |
| B027/S2 | alone, sixth | 1 | taken over | live | 70 / 121 / – / – | – | – | 0.10 → 0.01 |
| B012348/S01246 | alone, half | 1 | taking over | live | 311 / 850 / 2,075 / 2,432 | 0.44 | 0.73 / 0.94 / 1.10 | 0.32 → 0.03 |
| B015/S1 | alone, quarter | 1 | organised | live | 21 / 21 / 21 / 21 | 0.00 | 0.28 / 0.28 / 0.28 | 0.36 → 0.36 |
| B138/S123 | alone, quarter | 1 | organised | rows | 22 / 207 / 480 / 502 | 0.18 | 0.86 / 1.15 / 2.18 | 0.42 → 0.49 |
| B2378/S25678 | alone, half | 1 | taken over | live | 5 / 77 / 4 / 4 | -2.46 | 0.48 / 0.04 / 0.08 | 0.51 → 0.96 |
| B2/S0 | alone, sixth | 1 | patches | live | 2 / 2 / 2 / 3 | 0.07 | – / – / – | 0.22 → 0.22 |
| B237/S025678 | alone, half | 1 | taken over | live | 5 / 83 / 5 / 5 | -2.25 | 0.51 / 0.03 / 0.08 | 0.51 → 0.95 |
| soup 5 50092 | soup, shared, standoff, half | 1 | keeps growing | species 3 | 23 / 58 / 114 / 195 | 0.64 | 0.54 / 0.66 / 0.77 | 0.08 → 0.09 |
| soup 3 30145 | soup, shared, draw, half | 1 | keeps growing | species 3 | 13 / 45 / 160 / 183 | 0.45 | 0.60 / 0.96 / 1.66 | 0.07 → 0.24 |
| soup 5 50149 | soup, shared, standoff, half | 1 | keeps growing | species 4 | 15 / 42 / 95 / 192 | 0.71 | 0.52 / 0.77 / 1.06 | 0.05 → 0.04 |
| soup 3 30046 | soup, shared, standoff, half | 1 | organised | species 3 | 13 / 29 / 52 / 54 | 0.18 | 0.42 / 0.49 / 0.55 | 0.10 → 0.11 |
| soup 2 20032 | soup, one left, standoff, half | 1 | keeps growing | live | 199 / 681 / 2,278 / 3,780 | 0.78 | 0.77 / 1.00 / 1.25 | 0.47 → 0.51 |
| soup 3 30044 | soup, one left, standoff, half | 1 | keeps growing | live | 37 / 337 / 1,300 / 2,079 | 0.79 | 0.89 / 1.12 / 1.79 | 0.41 → 0.57 |
| soup 2 20093 | soup, one left, draw, half | 1 | taking over | species 1 | 139 / 336 / 836 / 816 | 0.28 | 0.56 / 0.83 / 1.02 | 0.67 → 0.99 |
| soup 2 20092 | soup, one left, draw, half | 1 | organised | columns | 23 / 285 / 595 / 658 | 0.21 | 0.82 / 1.12 / 2.09 | 0.42 → 0.49 |
| B2378/S25678 | against its copy, draw, full | 3 | keeps growing | species 2 | 22 / 104 / 877 / 3,008 | 1.80 | 0.85 / 1.78 / 3.74 | 0.25 → 0.40 |
| B2378/S25678 | against its copy, standoff, full | 3 | keeps growing | species 1 | 46 / 169 / 1,199 / 2,449 | 1.32 | 0.84 / 1.73 / 3.09 | 0.23 → 0.42 |
| B015/S1 | against its copy, draw, full | 1 | patches | columns | 1 / 1 / 1 / 1 | 0.03 | – / – / – | 0.94 → 0.94 |
| B015/S1 | against its copy, standoff, full | 3 | keeps growing | species 1 | 77 / 174 / 447 / 736 | 0.68 | 0.68 / 0.91 / 1.11 | 0.22 → 0.20 |
| B237/S025678 | against its copy, draw, full | 1 | patches | species 1 | 2 / 3 / 3 / 3 | 0.05 | – / – / – | 0.27 → 0.27 |
| B237/S025678 | against its copy, standoff, full | 3 | keeps growing | species 1 | 21 / 67 / 294 / 672 | 1.16 | 0.71 / 1.05 / 1.74 | 0.24 → 0.26 |
| B2/S0 | against its copy, draw, half | 1 | patches | species 1 | 7 / 10 / 11 / 13 | 0.34 | 0.28 / 0.26 / 0.29 | 0.13 → 0.13 |
| B2/S0 | against its copy, standoff, half | 3 | keeps growing | species 2 | 15 / 45 / 147 / 224 | 0.73 | 0.65 / 0.94 / 1.39 | 0.12 → 0.11 |
| B013/S1 against B015/S1 | two rules, standoff, full | 3 | keeps growing | species 1 | 47 / 119 / 328 / 455 | 0.61 | 0.62 / 0.79 / 0.98 | 0.26 → 0.26 |
| 5 copies of B2378/S25678 | five copies, standoff, full | 1 | keeps growing | species 3 | 55 / 184 / 593 / 1,478 | 1.14 | 0.72 / 1.20 / 1.89 | 0.09 → 0.13 |

The area is the correlation area at blocks of 128, the mean of the starts. The power of time
is over the last three readings. The clock is the area at twice the block and two, four or
eight times later, over four times the area: 1 where a zoom-out by two goes with that wait. A
rule alone that grew as the last species of a soup starts from the share of the grid it had
there (a quarter or a sixth), and the soups start as they did in the screen.

- **Most of the screen's strong growers are takeovers.** Of the 13 one-species rules, one
  keeps growing with its two kinds of ground level (B012457/S14). Four are taking the grid
  over and four have: among those, B2378/S25678 and B237/S025678, whose dense ground holds
  95% of the cells by generation 1,024. Two have set (B138/S123 in stripes that go together
  over about 500 cells, B015/S1 at 21), and two leave patches or nothing. A takeover is
  organised over a growing distance while it lasts, and no longer.
- **Growth with the grounds level looks the same wherever it turns up.** Anneal, Day and
  Night, B012457/S14 and soup 20032 all reach 2,800 to 3,800 cells by generation 2,048, and
  in all four a zoom-out by two goes with waiting four times as long: 0.97, 1.03, 1.03 and
  1.00. The powers of time in the table (0.66 to 0.84) are floors: by the end a block of
  128 is no longer much larger than a domain, and the area is still rising with the block.
  The clock compares like with like and does not have that fault.
- **A soup can set that balance up by accident.** In soup 20032 one species dies within the
  first generations, and what it leaves is the survivor (B013/S1) with its two kinds of
  ground level, which then grow as Anneal's do. The same rule alone, from the quarter of the
  grid it had in the soup, goes uniform within 128 generations. So the soup is run as the
  soup, and the species that dies is part of the start.
- **The soups in which species share the grid.** Three of the four still grow at generation
  2,048, with areas of 180 to 195 cells where the worlds above have thousands, and each is
  its own case: in 50092 two of the five species are left and both spread slowly; in 30145
  one species (B3/S234) is spreading through the other two, its share up from 0.07 to 0.24;
  in 50149 two species sit in a still pattern while two others organise. None is a world of
  territories.
- **Territories hold up under the standoff, and only there for three of the four rules.**
  All four rules keep growing territories against their copy under the standoff, on a grid
  sixteen times the contests' and from three fresh starts each, and so does the pair of
  different rules. Under the draw only B2378/S25678 does: the other three are patches (areas
  of 1 to 13 cells). Where there are territories the species keep apart as cleanly as the
  measure can say (-0.94 to -1.00), and in B015/S1, B2/S0 and the pair each species' share
  of the grid stays where it was at generation 64, to within two cells in a hundred.
- **The clock is not the same in every world of territories.** A zoom-out by two goes with
  waiting four times as long in B237/S025678 (1.05) and B2/S0 (0.94), as in the one-species
  worlds; with between four and eight times in B015/S1 (0.91 at four, 1.11 at eight); and
  with eight times in the pair (0.98).
- **B2378/S25678 against its copy does two things at once.** Its two species sort into
  territories within a few hundred generations. Then each fills in its own territory with
  the dense ground the rule makes when it is alone, and the live cells go from just under
  half of the grid to 0.76 (the draw) and 0.88 (the standoff) by generation 2,048. The area
  counts both, which is why it grows faster than the first power of time there and why its
  clock falls between two and four. Five copies do the same, and all five species still
  hold 12% to 16% of the grid at generation 2,048.
- **Life has a longer reach than the screen saw.** Its 24 cells are still rising with the
  block at blocks of 128 (as about the 0.6 power) and are not growing in time. Life against
  HighLife levels at 5 cells: the two worlds of steps 2 to 4 stay what step 4 said they
  were, apart from soup 19's rows, which go together over about 96 cells from generation
  256 on.

**The longer look** (`long.py`). Generation 2,048 cannot say what is left of B2378/S25678's
territories once the filling-in is over: territories that go on growing, or a map that has
set. So Anneal, the four contests with the largest territories and the world of five copies
were run to generation 16,384, on a grid of side 512 so that a run costs twice a confirm run
and not eight times, from one start each, read through blocks of up to 64.

- **The territories go on growing until the grid runs out.** In B2378/S25678 against its
  copy the filling-in is over by about generation 4,096 (live cells 0.91 of the grid), and
  the area at blocks of 64 goes on rising: 1,150, 1,880, 2,370 and 2,970 cells at
  generations 2,048 to 16,384 under the standoff, and 1,770 to 3,240 under the draw. A block
  of 64 has 4,096 cells, so by the end most blocks lie inside one territory, and the grid
  holds a handful of them. B237/S025678 does the same later (it fills in between
  generations 2,048 and 16,384), and B015/S1 without any filling-in: its live cells stay
  between 0.445 and 0.452 of the grid for the whole run.
- **Anneal does the same thing on this grid.** Its area rises to generation 4,096 and then
  levels near 2,900 as one of its two grounds takes the grid (live cells 0.53 to 0.94), which
  is what running out of grid looks like in this measure.
- **As the territories grow, the species stop being level.** On this grid, by generation
  16,384, one of B2378/S25678's two species holds 0.59 of the cells and the other 0.37
  (under both tie-breaks), one of B015/S1's has fallen from 0.22 to 0.10, and of the five
  copies one is down to 0.03. With fewer and larger territories a species can lose its last
  one. Whether that is the grid's size or the world's own law is not something one start on
  one grid can say.

**Every rule against its copy** (`rivals.py`; 4,784 worlds, 1 hour 45 minutes). The
contests above gave a rival only to the 29 rules that grow when alone, on the guess that
growing alone was what mattered. The large grid said it was not: of the four rules that
held territories, two fill the grid when alone, one sets and one is patches, and the rules
that keep growing alone die or mix against their copy. So "four of 29" counted the wrong 29.
You asked why those four and not the others; the first answer is that the others were never
the right ones to ask. Here every rule gets its rival: the 1,196 different rules of the
screen's even draw, each as two species with the one rule, from the full start and the
half-full one, under the draw and under the standoff, on the screen's grid.

| Every rule against a copy of itself, 1,196 rules | Both dead | One left | Mixed in patches | Organised, not apart | Standing territories | Growing territories |
| --- | --- | --- | --- | --- | --- | --- |
| full start, the draw | 58 | 0 | 1,014 | 4 | 29 | 91 |
| full start, the standoff | 108 | 0 | 903 | 6 | 29 | 150 |
| half-full start, the draw | 53 | 1 | 1,011 | 14 | 21 | 96 |
| half-full start, the standoff | 100 | 1 | 909 | 6 | 23 | 157 |

- **Territories are common.** 202 of the 1,196 rules hold them against their copy, one rule
  in six: 112 under both tie-breaks, 77 under the standoff only and 13 under the draw only.
  In 175 of the rules they grow, and in 78 they grow in all four contests. The 80 contests
  that both `contests.py` and this script ran came out the same to the last cell.
- **They come from rules that are nothing much alone.** 191 of the 202 are patches when they
  have the grid to themselves, and 144 of those are busy patches, with a fifth or more of
  their cells changing. Of the 20 rules that grow alone, two hold territories: the two the
  contests found. The organisation is not in the rule. It is in the meeting of the rule
  with its copy.
- **What they have in common is how few of its own kind a cell needs to be born.**

  | Fewest of its own kind for a birth | Rules | Hold territories | Under both tie-breaks | Under the standoff only | Under the draw only |
  | --- | --- | --- | --- | --- | --- |
  | 0 | 593 | 28 (5%) | 6 | 13 | 9 |
  | 1 | 279 | 41 (15%) | 10 | 29 | 2 |
  | 2 | 159 | 91 (57%) | 57 | 34 | 0 |
  | 3 | 82 | 41 (50%) | 38 | 1 | 2 |
  | 4 or more | 81 | 1 (1%) | 1 | 0 | 0 |
  | no births | 2 | 0 | 0 | 0 | 0 |

  A species that is born where it has no neighbours of its own turns up inside its rival's
  ground all the time, and nothing stays sorted: 509 of those 593 rules are mixed in all
  four contests. One that needs two or three of its own can only spread from where it
  already is, so each thickens where it is the many and thins where it is the few. One that
  needs four or more does not spread at all against a rival: 32 of those 81 rules die in
  every contest, as Anneal does, and 41 sit mixed in patches in all four.
- **And whether a cell can last on one or two of its own kind.** Among the 241 rules that
  need two or three for a birth, 44 of the 57 whose cells do not survive on one or two hold
  territories, against 88 of the 184 whose cells do. Ten of the 13 that fail die in every
  contest, as they nearly do alone. So of the 47 rules that need their own kind both to be
  born and to last, and that live at all, 44 hold territories against their copy, 37 of
  them under both tie-breaks. A straggler that can last inside the rival's ground keeps the
  mix mixed.
- **The standoff adds territories where births are easy.** Of the rules that need one
  neighbour for a birth and hold territories, 29 in 41 do so under the standoff only; of
  those that need three, 1 in 41. Where a single neighbour is enough, both species qualify
  for the same empty cell all along a border: drawn for, the species interleave there; left
  empty, the border stays a border.
- **How far to trust the cuts.** They were read off these runs, not predicted. The first was
  read off the first 458 rules while the rest were still running, and it holds on the other
  738 as it did on those: 4%, 13%, 56%, 48% and 2% of the rules hold territories at 0, 1, 2,
  3 and 4 or more, against 5%, 17%, 58%, 54% and 0%. The second was read off all 1,196 and
  has had no such check. The reasons given for both are my reading of the tables, not
  something tested.
- **The six sturdiest on the large grid.** Of the 78 rules whose territories grow in all
  four contests, the six with the largest were run as `confirm.py` runs its picks (side
  1,024, 2,048 generations, a fresh start), under both tie-breaks, and alone.

  | Rule | Alone | Against its copy, the draw: area at generations 64 / 256 / 1,024 / 2,048, and the clock at four | Against its copy, the standoff |
  | --- | --- | --- | --- |
  | B245678/S3678 | fills the grid and stops | keeps growing: 213 / 877 / 2,235 / 3,506; 1.01 | keeps growing: 209 / 877 / 2,643 / 4,216; 1.02 |
  | B24678/S34678 | fills the grid and stops | keeps growing: 131 / 482 / 1,584 / 2,954; 0.99 | keeps growing: 201 / 696 / 2,252 / 3,673; 1.01 |
  | B3568/S124678 | fills 98% of it and stops | keeps growing: 54 / 339 / 1,377 / 2,467; 1.10 | keeps growing: 62 / 361 / 1,224 / 2,128; 1.05 |
  | B2578/S135678 | fills 98% of it and stops | sets: 13 / 338 / 706 / 706 | sets: 69 / 304 / 323 / 324 |
  | B03458/S035678 | fills 91% of it and stops | keeps growing: 99 / 448 / 1,753 / 2,870; 1.11 | keeps growing: 12 / 195 / 1,150 / 1,500; 1.96 |
  | B23467/S4568 | busy patches, 71% live | keeps growing: 64 / 181 / 694 / 1,212; 0.95 | keeps growing: 108 / 400 / 1,493 / 2,530; 0.97 |

  Five of the six keep growing under both tie-breaks, to areas of 1,200 to 4,200 cells
  where Anneal has 3,100, and with Anneal's clock: a zoom-out by two goes with waiting four
  times as long (0.95 to 1.11; the one run that started late, B03458/S035678 under the
  standoff, has not come to it). One rule sets: after generation 512 its territories no
  longer grow. They are of two kinds. Five have a ground that fills the grid when the rule
  is alone and then stops; against a copy each species fills its own territory, the grid
  ends 95% to 98% live, and all that moves is the walls (1% to 5% of the cells change).
  The sixth is busy alone and busy in its territories (40% of the cells change), with each
  species level at 0.34 to 0.37 of the grid from generation 64 to the end. The screen says
  the same of the rest: its eight largest territories all come from rules that fill nine
  tenths of the grid or more alone.
- **The four rules of the contests, seen from here.** B2378/S25678 is one of the 78 that
  grow in all four contests. B237/S025678 holds under the standoff only, as it did. B2/S0
  needs two for a birth and does not survive on one or two. B015/S1, which the first
  version of D9 called the plainest, is the odd one out: it is born on no neighbours at all,
  holds territories under the standoff only, and loses them with a third species.

**What the search shows.**

1. **Alone, a rule seldom organises itself over a growing distance, and most that seem to
   are takeovers.** About one rule set in fifty grows on the small grid (42 of 2,275). Of
   the 13 strongest one-species rules, the large grid leaves one that keeps growing.
2. **What keeps growth going is balance:** two or more kinds of ground none of which can
   take the grid. Three one-species rules have it here (Anneal, Day and Night and
   B012457/S14), and a soup can fall into it.
3. **Competition supplies the balance, and often.** Species with one rule between them are
   level by construction, and one rule in six of the draw then sorts into territories
   against its copy (202 of 1,196), 78 of them from either start under either tie-break.
   What those rules share is how few of its own kind a cell needs: two or three to be born,
   and better still if it cannot last on one or two. The standoff adds rules where one
   neighbour is enough for a birth: left empty, a contested cell is a border.
4. **Growing alone and holding territories are different things.** Nearly all the rules
   that hold territories are patches alone. A rival undoes the domains of most rules that
   grow alone, Anneal and Day and Night die of it, and of the 20 rules of the draw that
   grow alone, two hold territories. The contests looked among those 20 and found those
   two; the other 200 were among the rules they did not try.
5. **The lab's soups, as drawn, do not hold such a world.** Rule sets with a few counts each
   give patches nineteen times in twenty; where a soup grows it is mostly one species left;
   and the few that grow with species sharing the grid are small and each its own case.
   What a soup lacks is not rivals but rivals alike enough: two different rules mix in
   patches or one of them is left, and they held territories only where they differ by one
   high count (five of the 18 tried) and in one pair of 66.
6. **The clock that goes with a zoom-out belongs to the world.** Four times the wait for a
   block twice the size where the grounds are level, so the square of the block; up to
   eight times in two worlds of territories whose species keep their shares; and none at all
   in a world of patches. Step 4 slowed the clock by the block. No world here that keeps
   growing runs on that clock, so a zoom-out of one of them has to choose its clock, and
   `zoom.py` already takes one per block.

**What it does not show.** Nothing here is registered. The screen read each world once, on
one grid, and a world its thresholds missed is missed: a slow grower under 16 cells at
generation 512, or one that needs another start than a half-full mix. The large-grid runs
stop at generation 2,048 and the longer ones are one start each on a grid that runs out. The
powers of time are floors, for the reason given above. That a takeover ends where it does
whatever the size of the grid is an inference from one size. The two cuts that say which
rules hold territories were read off the runs they describe: the first has held on rules it
was not read from, the second has been tried on none, and the reasons given for them are a
reading, not a test. Fresh rules would test both.

**Gate:** none, as nothing was registered. What it gives is the candidate worlds and the
question for decision D9.

### Step 4c: which rules hold territories (registered and run 2026-11-24: all ten held)

Step 4b read two cuts off its own runs: territories against a copy go with how few of its
own kind a cell needs to be born, and, among the rules that need two or three, with whether
a cell can last on one or two. The first had held on rules it was not read from; the second
had been tried on none. You chose to put both on the record before the ladder goes on
(decision D9). `examples/scale-up-territories` is that test.

- **What is run.** 600 fresh rules of the same even draw, from its number 1,201 on, leaving
  out the 3,287 rules that any earlier run has used alone, in a soup or against a rival. Each
  is run as the wider screen ran its rules: alone, and against a copy of itself from the
  full start and the half-full one under both tie-breaks, on side 256 for 512 generations.
  Every run begins from start 14001, which no run has used.
- **More rules for the second cut.** It lives among the rules that need two or three for a
  birth, and 600 rules hold 117 of them, 31 on its smaller side: too few to tell a real
  difference from none. So the draw goes on for 1,200 fresh rules more, and the 242 of that
  kind among them meet their copies too. The second cut is judged on all 359, 102 on its
  smaller side; everything else on the 600. In all 3,968 runs, about 75 minutes here.
- **Sizing first** (`sizing.py`, exploratory). The screen ran every contest from one start,
  so 200 of its rules were run again from another: 199 hold territories or not as they did,
  and 791 of the 800 contests come to the same verdict. A rule's verdict is the rule's, not
  its start's, and the bounds below allow for the number of rules alone.
- **Ten predictions in five families.** Each is a share of a group of the fresh rules, or a
  difference of two shares, against a bound set between what the screen gave and what would
  mean nothing. The last two columns are the chance a claim passes if the fresh rules are
  like the screen's, and if the cut it tests were worth nothing.

  | | Claim | Rules in its group | The screen gave | Passes if like the screen | Passes if worth nothing |
  | --- | --- | --- | --- | --- | --- |
  | R1 | of all the fresh rules, between 11% and 24% hold territories against their copy | 600 | 0.169 | 1.000 | – |
  | B1 | of the rules a cell of which is born with none of its own kind around it, at most 10% hold territories | 292 | 0.047 | 1.000 | 0.001 |
  | B2 | of the rules that need two or three of their own kind for a birth, at least 40% hold territories | 117 | 0.548 | 1.000 | 0.000 |
  | B3 | of the rules that need four or more of their own kind for a birth, or have no births, at most 8% hold territories | 43 | 0.012 | 0.998 | 0.053 |
  | B4 | the share of rules holding territories is higher by 0.20 or more among those that need two or three for a birth than among those that need one | 117 and 148 | 0.401 | 1.000 | 0.000 |
  | B5 | the share of rules holding territories is higher by 0.03 or more among those that need one of their own kind for a birth than among those that need none | 148 and 292 | 0.1 | 0.988 | 0.127 |
  | L1 | among the rules that need two or three for a birth, the share holding territories is higher by 0.10 or more where a cell does not survive on one or two of its own kind than where it does | 102 and 257 | 0.294 | 1.000 | 0.043 |
  | L2 | of the rules that need two or three for a birth, whose cells do not survive on one or two, and that do not die in every one of their contests, at least 70% hold territories | about 84 | 0.936 | 1.000 | 0.024 |
  | K1 | of the rules that hold territories under one tie-break and not the other, at least two in three hold them under the standoff | about 45 | 0.856 | 1.000 | 0.018 |
  | A1 | of the rules that the screen's judge calls organised or growing when they are alone, at most 35% hold territories against their copy | about 23 | 0.065 | 1.000 | 0.991 |

  R is how common territories are; B the first cut; L the second; K the tie-break; A what a
  rule does alone. A1 cannot tell "no likelier" from "less likely", and passes 99 times in
  100 if organising alone made no difference: what it can refuse is the guess the search
  began with, that the rules that organise alone are the ones to hold territories (it would
  pass one time in ten if half of them did).
- **Not tested is not failed.** A claim whose group turns out smaller than the number it
  names is recorded as not tested: a bound on a share of three rules says nothing. That is
  the lesson of step 4's soup at block 32. The groups by a rule's counts are known before
  any run and are all large enough.
- **Gate:** the verdict, whichever way it goes.

**The run** (2026-11-24: 3,968 runs in 1 hour 32 minutes on two cores, with pauses while
another job had the machine). **All ten predictions held.** The ledger verifies, and 24
records computed again from scratch came out byte for byte.

| | On the fresh rules | The screen gave | Bound |
| --- | --- | --- | --- |
| R1, all the rules | 106 of 600 hold territories: 17.7% | 16.9% | 11% to 24% |
| B1, born on none | 14 of 292: 4.8% | 4.7% | at most 10% |
| B2, on two or three | 72 of 117: 61.5% | 54.8% | at least 40% |
| B3, on four or more | 0 of 43 | 1.2% | at most 8% |
| B4, two or three over one | 61.5% against 13.5%: 0.48 higher | 0.40 | at least 0.20 |
| B5, one over none | 13.5% (20 of 148) against 4.8%: 0.09 higher | 0.10 | at least 0.03 |
| L1, cannot last over can | 82.4% (84 of 102) against 52.5% (135 of 257): 0.30 higher | 0.29 | at least 0.10 |
| L2, needs its own kind and lives | 84 of 85: 98.8% | 93.6% | at least 70% |
| K1, the standoff only, of one tie-break only | 35 of 41: 85.4% | 85.6% | at least two in three |
| A1, organises alone | 1 of 21 holds: 4.8% | 6.5% | at most 35% |

- **Both cuts hold on rules they were not read from**, from a start they were not read
  from, and at very nearly the screen's numbers. The second cut, which had been tried on no
  rule it was not read from, gives a difference of 0.30 where the screen gave 0.29.
- **A rule that needs its own kind to be born and to last, and lives, holds territories.**
  Of the 102 such rules, 17 die in every contest, and 84 of the other 85 hold territories.
  Among all 359 rules that need two or three for a birth, 219 do.
- **The rest is as the screen had it.** Territories in 17.7% of the rules: 65 under both
  tie-breaks, 35 under the standoff only, 6 under the draw only. 101 of the 106 rules that
  hold them are patches alone, and of the 8 that grow alone, one holds them.
- **What this does not settle.** The test is of the counts: which rules, how often. The
  reasons step 4b gave for the cuts (a species born among its rival's cells unsorts the
  grid; a straggler that can last keeps the mix mixed) are still a reading of the tables.
  It is one grid size and 512 generations, by the screen's own judge of what a territory
  is. And what the territories grow into has been followed on a large grid for six rules.

**Gate: passed.**

### Step 5: reversible variants

- **What:** the second-order form of a rule, next = F(now) + before (mod 2), as a wrapper that
  keeps two generations and calls the one update rule for F. LatticeLife keeps its single
  update rule.
- **Its own calibration, with two known answers.** Both were checked on small grids while
  writing this plan:
  - any second-order rule runs backward exactly (swap the two generations and run): on a
    12 x 12 grid, Conway's Life in this form returned to its start after 50 generations out and
    50 back;
  - a second-order parity rule scales exactly as the first-order one does:
    x(t + 2^k) + x(t − 2^k) is the rule with neighbours 2^k apart applied to x(t), so zoomed out
    by 2^k the samples obey the same second-order rule. This held for all four parity rules on
    12 x 12 and 24 x 24 grids, at 2^k up to 8.
- **Then:** look for conserved quantities with `find_invariants`, and run steps 2 to 4 on the
  reversible forms.
- **Gate:** a registered calibration like step 0.

## What the runs cost

Measured, on one core of this machine unless it says otherwise.

| Run | Cells | Generations | Cost | Where |
| --- | --- | --- | --- | --- |
| step 0, all 296 cases | up to 590,000 | up to 256 | 3.5 minutes in total | here, one core |
| step 2, the tie-break test, 3,584 runs | up to 16,384 | up to 600 | 12 minutes | here, one core |
| step 2, the laws, 672 runs | up to 65,536 | up to 1,000 | 13 minutes | here, one core |
| step 3, sides 512 and 1024, 192 runs | up to 1.0 million | up to 1,000 | 69 minutes | here, two cores |
| step 3, sides 2048 and 4096, 96 runs | up to 16.8 million | up to 1,000 | 2 hours 20 minutes on fourteen cores of a pod (about 33 core-hours); 3 GB a run at side 4096 | a pod |
| the re-check, side 2048, 16 runs | 4.2 million | 1,000 | 40 minutes | here, two cores |
| step 4, the first look, 48 runs read through blocks | up to 1.0 million | up to 1,024 | 30 minutes with its analysis | here, two cores |
| step 4, the registered test, 22 runs read through blocks | up to 4.2 million | up to 1,024 | 47 minutes with its analysis | here, two cores |
| step 3b, sides 1024, 2048 and 4096, 512 runs | up to 16.8 million | 1,000 | 2 hours 11 minutes on sixteen cores of a pod, $2.49 | a pod |
| step 4b, the screen, 2,407 worlds read through blocks | 65,536 | 512 | 59 minutes | here, two cores |
| step 4b, the contests, 312 worlds | 65,536 | 512 | 12 minutes | here, two cores |
| step 4b, the candidates again, 56 runs | 1.0 million | 2,048 | about 1 hour 50 minutes, with pauses while another job had the machine | here, two cores |
| step 4b, the longer look, 6 runs | 262,144 | 16,384 | 18 minutes | here, two cores |
| step 4b, every rule against its copy, 4,784 worlds | 65,536 | 512 | 1 hour 45 minutes | here, two cores |
| step 4b, its six sturdiest rules on the large grid, 18 runs | 1.0 million | 2,048 | 37 minutes, with pauses while another job had the machine | here, two cores |
| step 4c, the sizing look, 1,000 runs | 65,536 | 512 | 24 minutes, with pauses | here, two cores |
| step 4c, the registered test, 3,968 runs | 65,536 | 512 | 1 hour 32 minutes, with pauses | here, two cores |

A generation costs about 95 ns per cell for two species and 160 to 220 ns for five, and a
little more per cell on the largest grids, which no longer fit the processor's cache. The
pair's runs came out faster than the timing said (16 s at side 512 against 23 s), because
most of the grid is empty after the first hundred generations.

**The pod for the large part** (2026-11-23): a compute-optimised CPU pod with 32 vCPUs and
64 GB at $1.12 an hour, with a deadline of six hours after which it deletes itself, so $6.72
at most. It ran the 96 runs fourteen at a time in 2 hours 20 minutes and was deleted when
its results were home: $2.57. The same runs would have taken about twelve hours here on two
cores. RunPod's 16- and 32-vCPU pods were out of stock for minutes at a time that afternoon,
and four requests were refused (nothing was created) before one was taken; the launcher now
watches the stock and takes the first acceptable size
(`examples/scale-up-sizes-large/pod/`).

No step needs a faster engine. If one is wanted later it must reproduce the one update rule
cell for cell, with a test that says so.

## What is not planned

- A GPU or compiled engine.
- Discovering spatial laws (differential equations) in Kepler. Step 2's laws are curves against
  time, size or share, which Kepler fits today.
- The triangle lattice, beyond the small study named above.
- Any claim about the Planck scale or about physics.

## The birth tie-break (decision D1), in full

**What it is.** With two or more species, a dead cell can satisfy the birth rule of more than
one of them at once. LatticeLife gave the cell to one of them by a random draw with equal odds
(`core/lattice.py`), and still does unless told otherwise. Everything else in the update is a
function of the grid.

**How often it acts.** A first look on 2026-11-23, exploratory and not a registered result:
256 x 256, Life against Life and Life against HighLife, 600 generations from a mixed start, two
starts each at two densities.

| Share of births that are contested | Half-full start | 20% start |
| --- | --- | --- |
| generation 1 | about 9.4% (some 1,180 of 12,500) | about 0.5% |
| generation 10 | under 1% | about 0.1% or less |
| generation 100 onward | 0 to 2 births a generation, of 400 to 2,200 | 0 or 1 |
| over all 600 generations | 0.40% to 0.47% | 0.03% to 0.04% |

A contest needs exactly three neighbours of each species round one empty cell, which is rare
once the first crowded generations have passed. So for these pairs the species compete almost
entirely by occupying cells the other needs, and the tie-break is a rare event. Whether it
still shapes the large scale is a question step 2 can answer.

**In `autorun`'s own soups it is the opposite.** A second look the same day, once contests
were counted by the engine: 24 `autorun` sessions as it makes them (random rules with one to
four birth counts each, 1 to 10 species, 50 x 50, 100 generations, the random draw). Again
exploratory.

| Species | Sessions | Contested cells a generation, of 2,500 | Share of births that are contested |
| --- | --- | --- | --- |
| 2 | 5 | 26 | 4% |
| 3 to 5 | 9 | 217 to 315 | 26% to 33% |
| 7 to 10 | 7 | 445 to 591 | 40% to 69% |

Over the 22 sessions with two or more species, 38% of all births were contested. (One session
of six species sat at 2%: the rules drawn matter as much as their number.) With rules drawn
at random and several species, the tie-break is a large part of the dynamics, and its kind
should be expected to change them: a standoff withholds a third of the births.

**The options.** There are two separate choices: how the odds are set among the species that
could be born, and where the draw comes from.

| Option | Odds | Where the draw comes from | A function of the grid alone? |
| --- | --- | --- | --- |
| Today | equal | a random stream outside the grid | no |
| Standoff | none: a contested cell stays empty | no draw | yes |
| Strongest wins | the species with more cells nearby takes the cell; level means a standoff | no draw | yes |
| Weighted | in proportion to local strength, raised to a power: 0 gives today's rule, a large power gives strongest wins | a random stream outside the grid | no |
| Hidden layer | any of the above | hidden bits in every cell, which follow a deterministic rule of their own | yes, of the full grid; random to anyone who sees only the species |

A fixed priority (species 1 always wins) is also a function of the grid, but it builds a bias
into the contest, so it is not on the list.

What each one gives:

- **Standoff and strongest wins** make the world an ordinary cellular automaton with several
  states. Exact cycles and periods mean something again for several species, and the reversible
  construction of step 5 applies.
- **Weighted** is the "random within a range" option: the range is the set of species that
  could be born, and one dial runs from equal odds to strongest wins. For Life-like rules the
  strength must be counted over a wider neighbourhood than the birth neighbourhood, because two
  B3 species contesting a cell always have three neighbours each.
- **A hidden layer** makes the world deterministic on its full state and random to an observer
  who cannot see the layer. A parity rule would serve as the hidden rule, since the lab knows
  its behaviour exactly; in its reversible form the randomness is never used up.
- **Noise in the rule itself** is a different lever, listed because the tie-break fires so
  rarely: every birth or survival happens with odds set by the neighbourhood. That is the
  standard probabilistic cellular automaton. Its large-scale behaviour, sharp transitions with
  exponents shared across many rules, is well mapped, which makes it good ground for the
  ladder.

**What this has to do with quantum mechanics.**

- *What matches.* In quantum mechanics the state fixes the odds exactly, and between
  measurements the evolution is deterministic and reversible.
- *What is missing.* Interference: alternatives carry signed amounts that can cancel before
  they become odds. And entanglement: correlations between distant outcomes that no local rule
  with local dice can produce (Bell's theorem). A weighted draw gives a classical probabilistic
  automaton, which is worth studying and is not quantum.
- *The hidden layer* is the "deterministic underneath" position. Bell's theorem says a local
  hidden layer cannot reproduce quantum correlations unless the starting state is already
  correlated with every later choice of measurement.
- *Where the lab meets the real thing.* The reversible parity rules of step 5. A Clifford
  quantum cellular automaton acts on Pauli operators through a 2 x 2 matrix of Laurent
  polynomials over GF(2) (Schlingemann, Vogts and Werner, 2008, in one dimension), and
  x(t + 1) = f x(t) + x(t − 1) with a symmetric f is the matrix [[f, 1], [1, 0]]. That is the
  one family of quantum automata that can be simulated exactly at any size, it lives in the
  ring the rest of this repository lives in, and in it a measurement's outcome is either
  certain or an exact fair coin. This is established mathematics that has not been checked
  against the lab's code; it is a pointer for step 5.

**Built on 2026-11-23**, ahead of step 2 at your word (LatticeLife branch `tie-break`, commit
`456e044`, which lattice-lab pins). The tie-break is a setting of the one update rule:
`simulation.tie_break` in the config, `--tie-break` on `ui` and `autorun`, `TieBreak` in code.

| `tie_break` | Who is born in a contested cell | Draws? |
| --- | --- | --- |
| `random`, the default | one of the eligible species, each with the same chance: the rule as it was, draw for draw | yes |
| `standoff` | nobody | no |
| `strongest` | the eligible species with the most cells within `tie_break_radius` steps (2 unless set); nobody if the top is shared | no |
| `weighted` | a draw, with chances in proportion to that count raised to `tie_break_power`; power 0 is `random`, draw for draw | yes |

- **What the tests show.** Each kind does what the table says on a single contested cell worked
  by hand. A deterministic kind never advances the generator, and two different generators
  give one trajectory. No species is favoured by its id or its place in the list. One species
  runs the same under all four. With strengths of 4 against 3 the weighted draw gives the
  stronger species 4/7, 16/25 and 0.909 of 3,000 cells at powers 1, 2 and 8, each inside five
  standard deviations.
- **Contests are counted.** Every generation's contested cells are in its result
  (`UpdateResult.contested`), under every kind, so how often the tie-break acts is data from
  now on and needs no special measurement.
- **The recorder.** A new `autorun` database records each session's tie-break and each
  generation's contested cells (schema v3). A database from before is left as it is and takes
  only sessions that draw at random, which is what every session in it did.
- **Nothing else moved.** The draw is still the default and is the rule as it was, draw for
  draw. On the new pin LatticeLife's suite passes (1,269 tests), the calibration's 3,084
  records come out identical again, lattice-lab's suite has no new failure, and `verify` finds
  no problem in any of the 35 ledgers.
- **Not built:** the hidden layer (with step 5), and noise in the rule itself (its own world,
  if you want it). The app's settings panel does not offer the tie-break yet: set it in the
  config, or start the app with `--tie-break`.
- **Compared, the draw against the standoff** (`examples/scale-up-tie-break`, registered; step
  2 above): no measurable difference where contests are rare, in the Life-like pairs and in
  five soups; a lower live fraction under the standoff in every soup where a fifth or more of
  births are contested, by 0.04 to 0.46 of the grid. `strongest` and `weighted` have not been
  compared with anything, and no comparison has been made above 128 x 128.

## Decisions for you

- **D1. The tie-break.** Decided on 2026-11-23: build the setting first, so the option is
  there for discovery. It is built, and the draw has been compared with the standoff (step 2).
  What stays open: which tie-break the later steps run. For Life-like pairs it makes no
  measurable difference, so the standoff costs nothing there and buys a world that is a
  function of its grid. For soups it is a different world, and both are worth keeping. Noise
  in the rule is a separate lever, not built.
- **D2. Which contest first.** Done as recommended: Life against Life (the symmetric control)
  and Life against HighLife, the pair in LatticeLife's README. They coexist, so the next
  question is which worlds to follow to larger sizes: these pairs, whose ash is quiet, or a
  soup, which stays active.
- **D3. Where a probabilistic coarse rule lives.** Done as recommended: plain tables of what
  came next, in lattice-lab (`examples/scale-up-closure/zoom.py`). No closed form has shown
  up that would call for Kepler, apart from the one number that is the same at every block.
- **D8. Where the ladder goes next.** Done (2026-11-24). Of three ways on from step 4 you
  chose the search of the lab's rule sets for a world where something is organised over a
  growing distance. It is step 4b. The other two stay open: richer symbols for the pair,
  which the first look says carry much further, and step 5, the reversible variants, where
  nothing can die out and the zoomed-out world cannot freeze.
- **D9. What to take up the ladder, and on which clock** (2026-11-24; rewritten the same
  day, after every rule had met its copy). The first version of this decision named
  B015/S1 against its copy as the plainest world. The wider screen shows it is the odd one
  out, and that there are plainer and sturdier worlds by the dozen. Two kinds stand out, both
  holding under either tie-break with the clock at four: **B245678/S3678 against its copy**,
  two still grounds with nothing moving but the walls between them, the two-species
  counterpart of Anneal; and **B23467/S4568 against its copy**, two busy grounds whose
  shares of the grid stay level. Three ways on, cheapest first:
  (a) put the two cuts on the record: a registered test on fresh rules (the same draw,
  numbers 1,201 on, each rule against its copy as here) of which rules hold territories, by
  how few of its own kind a cell needs to be born and whether it can last on one or two.
  About an hour here for 600 rules. The cuts were read off the data, and that is exactly
  the kind of pattern that looks better the longer one looks;
  (b) a first look at those two worlds with step 4's instrument, with who leads a block as
  the symbol and a coarse rule learned at one block and tried at the next, with the clock
  at the block and at its square; a few hours here, and then a registered test of what it
  shows, as in step 4;
  (c) leave the search here and take up D8's other two.
  I recommend (a) and then (b). (a) is small, it settles "why" as far as counts can, and it
  is the last thing owed on the question you asked. (b) is what the ladder is for.
  You chose (a): it is step 4c, registered and run on 2026-11-24, and all ten predictions
  held. (b) is what is left of this decision: the first look up the ladder at
  B245678/S3678 and B23467/S4568 against their copies.
- **D4. When to move the instrument into LatticeLife.** Done: step 1.
- **D5. The pod.** Done. You chose the pod over this machine; it cost $2.57 of the $6.72
  agreed.
- **D7. The remainder at side 2048.** Done (step 3b). You chose to close it before step 4;
  the registered test held on all nine predictions, and the pod cost $2.49 of the $6.72
  agreed.
- **D6. The branches.** Nine, none merged and none with a pull request yet:
  - lattice-lab `scale-up-linear`: step 0, the study, its tests and this plan;
  - lattice-lab `scale-up-step-1`, on top of it: the pin, the rerun hook and the gate;
  - LatticeLife `coarse-graining`: the zoom-out module;
  - LatticeLife `tie-break`, on top of it: the tie-break setting, which `scale-up-step-1` pins;
  - lattice-lab `scale-up-step-2`, on top of `scale-up-step-1`: the first look and the
    tie-break test;
  - LatticeLife `competition`, on top of `tie-break`: several species without the app, which
    `scale-up-step-2` pins. A LatticeLife branch should stay, or be merged, before the
    lattice-lab branch that pins it is;
  - lattice-lab `scale-up-step-3`, on top of `scale-up-step-2`: the registered scale-up test,
    both parts and both runs, and step 3b;
  - lattice-lab `scale-up-step-4`, on top of `scale-up-step-3`: the zoom-out instrument, its
    first look and its registered test;
  - lattice-lab `scale-up-search`, on top of `scale-up-step-4`: the search of step 4b, which
    registers nothing, and the registered test of step 4c, which adds one study and ten
    predictions to the census dashboards' table.

  Like the unmerged `ccr-effac3f1-udftpr` (the qec-parents study), these branches add their
  studies to the census dashboards' table, so they meet it on one line: the count of studies
  and predictions in `tests/test_census_dashboards.py`. With everything merged that line is 42
  studies and 1,827 predictions.
