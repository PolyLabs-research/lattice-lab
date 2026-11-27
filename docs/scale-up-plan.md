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
(`examples/scale-up-territories`). A first look at two of those worlds zoomed out
(`examples/scale-up-closure-territories`, exploratory) found what step 4's worlds lacked, a
coarse description that works: who leads each block, with a table of what blocks with as
many rival neighbours did next, runs the world on without its cells and says where most of
its territories will be three thousand generations later. The table is nearly the same in
two worlds whose rules share nothing, and it still changes from rung to rung, by less at
each rung on the clock these worlds keep. A registered test of that, with three worlds no
run had zoomed out and a control (the same folder's `study.py`, 89 predictions), held on
73: everything the first look saw of its two worlds, on fresh starts; the control, where
the rule must not serve; and of the three unseen worlds one follows the still world's rule
as it is, one at half the pace, and one, a sparse world that grows on another clock, not at
all. A registered test of how wide that class is (`examples/scale-up-class`, 128
predictions, 54 held) refuted the simple account of it: 29 of 38 worlds no run had zoomed
out keep the same clock, but the still world's rule serves only the ten that have more
than half their grid live, about a quarter of the rules of a random draw that grow
territories; run on at the pace a world's walls give, it carries nineteen. A registered
test of one more rung (`examples/scale-up-rung`, side 2,048 to generation 16,384, blocks of
32) held on all 22 predictions: the fourth rung is the same picture as the three below, the
rule of each rung runs the rung above nearly as well as its own, and the rule changes less
again, by 1.4% and 1.6% where it was 2.8% and 3.0% a rung below. It has not stopped
changing, and the same records say the end is further off than that gap suggests: what
still moves is how often a block on a wall changes hands, and by the pattern so far three
more rungs would be needed to come near. A first look at a rule that also sees a block's
past (`examples/scale-up-memory`, exploratory) found that the coarse rule has a memory
though the worlds have none: how long a block has had its leader says what it does next.
With that in view the rule runs the world on better and keeps its walls, the rule of one
rung runs the rung above as well as that rung's own at blocks of 16 and 32, and the top of
the table is the same at every rung; one tick ahead the table still changes along the
walls. A registered test of that on fresh starts, at step 4e's size, is registered (the same
folder's `study.py`, 74 predictions). Step 5 is not built. The decisions that are yours are
at the end.

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

### Step 4d: a world of territories, zoomed out (first look, exploratory, 2026-11-25)

Step 4 zoomed out two worlds of patches and found maps of where things still move, with no
rule that is the same from one block size to the next. Steps 4b and 4c found worlds of another
kind: two species with one rule between them, which sort into territories that keep growing.
You chose a first look at two of them with step 4's instrument (decision D9, option b).
`examples/scale-up-closure-territories/look.py` is that look. Nothing in it is registered.

- **The two worlds.** Each is a rule against a copy of itself under the standoff, so the
  world is a function of its grid, from a full start (every cell live, half of them each
  species):
  - *still*, B245678/S3678: each species fills its ground and stops (98% of the grid is live
    by the end), and nothing moves but the walls;
  - *busy*, B23467/S4568: the grounds stay busy inside, with 71% of the grid live.
- **What is run.** A wrapped grid of side 1,024 for 4,096 generations, from eight fresh
  starts each (15001 to 15008): 16 runs, read through blocks of 4, 8, 16 and 32. Coarse rules
  are learned from four of the starts and tried on the other four. The reading begins at
  generation 64, when the sorting-out is over.
- **What a block is read as.** Who leads it: the species with more cells in the block. A
  second reading adds whether the block is contested (the rival holds a tenth or more of its
  live cells).
- **Two clocks.** Step 4 slowed the clock by the block, since nothing travels faster than a
  cell a generation. Step 4b found that these worlds keep another time: through blocks twice
  the size they are the same picture four times later, not twice. So every block is read on
  both: the *block clock* (one coarse generation is 4, 8, 16 and 32 fine ones at blocks of 4
  to 32) and the *square clock* (4, 16, 64 and 256: the square of the block, over four so
  that the two agree at blocks of 4).

**What it found.** For the reading by leader, with a rule that looks at how many of a
block's eight neighbours each species leads, unless it says otherwise.

1. **Who leads a block changes by a rule, and the rule is in the neighbours.** In step 4's
   pair the leader was frozen and the neighbours said nothing about it. Here a block of 4
   has a new leader four generations on with these chances:

   | Neighbours the rival leads | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
   | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
   | the still world | 0.0000 | 0.0000 | 0.002 | 0.037 | 0.17 | 0.37 | 0.47 | 0.42 | 0.59 |
   | the busy world | 0.0000 | 0.0000 | 0.0004 | 0.022 | 0.15 | 0.37 | 0.44 | 0.37 | 0.56 |

   A block changes hands by being surrounded. Few blocks do in any one coarse generation (10
   in a thousand in the still world, 7 in the busy one), so the likeliest next leader is
   nearly always the present one, and knowing the neighbours removes 2% of the errors. What
   it removes is surprise: 44% of it at blocks of 4 in both worlds, and 40%, 35% and 23% at
   blocks of 8, 16 and 32 on the square clock (still; 42%, 37% and 26% busy). Where the
   neighbours are adds little to how many there are: under one point of the surprise at
   blocks of 4 and 8, two to four at 16 and 32.
2. **It is the same rule early and late, where the blocks are small beside the
   territories.** The rule learned before generation 1,024, tried after it, has 0.24% more
   surprise than the rule learned there at blocks of 4, in both worlds; about 1% at blocks of
   8, 2.4% to 3.0% at blocks of 16, and 5% to 8% at blocks of 32 on the block clock. On the
   square clock blocks of 32 have too few early transitions to say.
3. **From one rung to the next the rule changes: less on the square clock, and less at each
   rung.** This is the ladder's fixed-point question, and step 4 found no sign of one. Here
   the rule learned at blocks of half the size, from as many transitions as the rung's own
   rule, has this much more surprise than the rung's own:

   | | at blocks of 8 | at 16 | at 32 |
   | --- | --- | --- | --- |
   | still, block clock | 16.4% | 11.2% | 7.9% |
   | still, square clock | 8.9% | 3.8% | 3.4% |
   | still, square clock, at matched ages | 9.0% | 2.6% | – |
   | busy, block clock | 10.2% | 10.1% | 6.9% |
   | busy, square clock | 6.7% | 4.5% | 2.4% |
   | busy, square clock, at matched ages | 5.8% | 2.4% | – |

   "At matched ages" compares the rungs as the square clock says they should be compared:
   blocks of 4 over generations 64 to 256, blocks of 8 over 256 to 1,024, blocks of 16 over
   1,024 to 4,096. The run is too short to do that for blocks of 32. The surprise is a
   forgiving measure: on the block clock the chances are out by a factor of two and more at
   every rung, and that costs 7% to 16%. So the chances themselves say it more plainly. A
   block with five of its neighbours under the rival changes hands with a chance of:

   | | blocks of 4 | 8 | 16 | 32 |
   | --- | --- | --- | --- | --- |
   | still, block clock | 0.37 | 0.16 | 0.063 | 0.026 |
   | still, square clock | 0.37 | 0.24 | 0.16 | 0.13 |
   | still, square clock, at matched ages | 0.31 | 0.24 | 0.20 | – |
   | busy, block clock | 0.37 | 0.18 | 0.072 | 0.030 |
   | busy, square clock | 0.37 | 0.25 | 0.17 | 0.14 |
   | busy, square clock, at matched ages | 0.30 | 0.26 | 0.22 | – |

   On the block clock a block twice the size changes hands under half as often, rung after
   rung, and nothing settles: that clock is too fast for these worlds. On the square clock
   the chances fall by a third at the first rung and by a fifth at the last, and at matched
   ages the surprise gap of the second rung is under half that of the first. That is not a
   fixed point. It is what coming to one would look like, and it is also what three rungs of
   something else could look like: step 4's failed band at block 64 was drawn from a trend
   no longer than this.
4. **The two worlds follow nearly the same coarse rule.** Cell by cell they share nothing:
   different rules, one still inside its grounds and one with two cells in five changing.
   The rule learned in one world, tried in the other, has this much more surprise than the
   rule learned there (square clock; the two directions):

   | | blocks of 4 | 8 | 16 | 32 |
   | --- | --- | --- | --- | --- |
   | the still world's rule in the busy world | 1.9% | 0.4% | 0.1% | −0.7% |
   | the busy world's rule in the still world | 1.6% | 0.4% | 0.2% | 0.3% |

   Blocks of 32 have too few transitions for the last figure to mean more than "near
   nothing". On the block clock it is 0.3% at blocks of 8 and 0.2% to 0.3% at 16. So from
   blocks of 8 a world's rule is nearer the other world's than it is to its own at another
   time (1% to 3%) or at the next rung (2% to 16%). The chances say the same. At blocks of
   16 on the square clock, a block with 4, 5 or 6 neighbours under the rival changes hands
   with chances of 0.070, 0.161 and 0.243 in the still world and 0.071, 0.170 and 0.249 in
   the busy one. On the block clock the chances are further apart, by up to a quarter, the
   busy world's blocks the quicker to change. Read with the contested mark, which looks
   inside the block, the worlds are further apart: 2.4% to 2.8% at blocks of 4 and still
   1.1% to 1.7% at 16 on the square clock.

   This is the row "classes" of the table at the top of this plan: different fine rules that
   land on the same coarse rule. Two worlds chosen for being sturdy are not a class, and two
   worlds whose walls happened to move at the same pace would look like this.
5. **Run on by itself, the coarse rule keeps the world, and says where most of its
   territories will be.** From the zoomed-out world at generation 1,024 the rule is run on
   to generation 4,096 by drawing every block's next leader from its table, with no fine
   cells under it. On the square clock, at the end:

   | | Coarse generations run | Walls, the rule's world over the real one | Blocks whose leader is not the real world's: the rule's world | the start, had nothing moved | two runs of the rule, one against the other |
   | --- | --- | --- | --- | --- | --- |
   | still, blocks of 4 | 768 | 0.75 | 12.1% | 21.4% | 6.0% |
   | still, 8 | 192 | 0.86 | 9.6% | 21.2% | 8.2% |
   | still, 16 | 48 | 0.95 | 10.5% | 21.0% | 11.8% |
   | still, 32 | 12 | 1.02 | 18.4% | 19.5% | 20.9% |
   | busy, 4 | 768 | 0.88 | 7.2% | 20.9% | 4.8% |
   | busy, 8 | 192 | 0.94 | 6.9% | 20.6% | 7.8% |
   | busy, 16 | 48 | 1.01 | 9.4% | 20.3% | 10.5% |
   | busy, 32 | 12 | 1.00 | 16.9% | 19.6% | 18.0% |

   - **It is the same kind of world.** The share of neighbouring blocks under different
     leaders (the walls) about halves in the real world over those 3,072 generations, and
     at blocks of 16 and 32 the rule's world ends within about 5% of it. At blocks of 4 the
     rule loses walls too fast: it ends with 75% of them in the still world and 88% in the
     busy one.
   - **And much of the same world.** A fifth of the blocks change leader in those
     generations. The rule's world has the real world's leader in all but 7% to 12% of the
     blocks at blocks of 4 to 16: it about halves the error of supposing nothing moved in
     the still world, and cuts it to a third at blocks of 4 and 8 in the busy one. In step
     4's pair no rule foretold which blocks would change better than "none". At blocks of
     32 the rule does little better than that here: a block of 32 is a third to a sixth of
     a territory across, and the run is twelve coarse generations.
   - **It errs like its own dice.** At blocks of 16 and 32, and at 8 in the busy world, the
     real world is no further from a run of the rule than a second run of the rule is,
     drawn afresh from the same start. At blocks of 8 in the still world it is a sixth
     further. At blocks of 4 it is twice as far (half as far again in the busy world),
     which is the walls again.
   - **Not at once.** At first the rule's world is further from the real one than the start
     is: it cannot say which wall blocks will change, and draws. It overtakes "nothing
     moved" between 128 and 1,024 generations on at blocks of 4 to 16, later the larger the
     block, when what matters is which territories go and which walls straighten.
   - **The square clock runs on better than the block clock** at every block above 4: 12.1%,
     15.3% and 23.8% of blocks amiss at blocks of 8, 16 and 32 in the still world on the
     block clock, against 9.6%, 10.5% and 18.4%.
   - **The pictures** (`pictures.py`, a page at
     `~/lattice-lab-runs/closure-territories/pictures/index.html`) show the real world and
     the rule's world side by side at generation 4,096 for one start, through blocks of 4,
     8 and 16. Most of the territories are the same territories, in the same places.
6. **The contested mark does not earn its place.** A rule that also knows whether a block
   is contested is surer of itself: two of its runs differ in 3% to 7% of the blocks at
   blocks of 4 to 16, where the plain rule's differ in 5% to 12%. It is nearer the real
   world at blocks of 16 and 32 (8.3% and 12.1% of blocks amiss in the still world against
   10.5% and 18.4%), little or no nearer at 4 and 8 in the still world, further at 4 and 8
   in the busy one (9.5% against 7.2% at blocks of 4), and it loses walls faster at every
   block. In step 4's pair a richer symbol carried much further. Here who leads is most of
   what there is to know.

**What step 4d shows.** These worlds have what step 4's lacked: a coarse description that
works. Who leads each block, and a table of what blocks with as many rival neighbours did
next, is enough to run the world on without its cells for three thousand generations, and
to say where most of its territories will be. The table is nearly the same in two worlds
whose fine rules have nothing in common. It is not the same from rung to rung on either
clock, but on the clock these worlds keep (the square of the block) the difference shrinks
from each rung to the next. Whether it goes to nothing is what another rung would say.

**What it does not show.** Nothing here is registered, and I looked at the numbers before
deciding what to say about them. It is one grid size, four starts to learn from and four to
try on, and two worlds picked for being the sturdiest of their kinds, both under the
standoff and both from a full start. Blocks of 32 are thin: 61,440 transitions on the square
clock, and territories only three to six blocks across. "At matched ages" is two
comparisons. "The same rule in both worlds" is a surprise within half a percent and chances
within about 5%, on one clock, in one pair of worlds. And why the rule works where it does
(walls that move by how they curve, at a pace that belongs to the world) is my reading of
the tables, not something this look tested.

**Gate:** none, as nothing was registered. What it gives is the claims for a registered
test, which is decision D10.

### Step 4e: the zoom-out of territories, registered (registered and run 2026-11-26: 73 of 89 held)

Step 4d read its findings off the runs they describe. You chose to put them on the record
(decision D10, option a): `examples/scale-up-closure-territories/study.py`, registered on
2026-11-26 with 89 predictions before any of its runs was made.

- **What is run.** Six worlds, each a rule against a copy of itself under the standoff on a
  wrapped grid of side 1,024 for 4,096 generations, from starts no run has used (16001 on;
  no two worlds share one). Coarse rules are learned from half of a world's starts and
  tried on the other half.

  | World | Rule | Starts | What it is here for |
  | --- | --- | --- | --- |
  | still | B245678/S3678 | 8 | the first look's two worlds, again |
  | busy | B23467/S4568 | 8 | |
  | near | B24678/S34678 | 8 | never zoomed out: a near relative of the still world's rule |
  | another | B3568/S124678 | 8 | never zoomed out: a still world whose rule shares little with it |
  | sparse | B2/S0 | 8 | never zoomed out: a quarter of the grid live, busy, territories under the standoff only; from a half-full start, the one it was seen to hold them from |
  | set | B2578/S135678 | 4 | the control: its territories set after generation 512 and stop |

  The three unseen worlds were chosen from what the search knew of them by its own measure
  (the correlation area on side 1,024): that they keep growing. None had been read by who
  leads a block, and no coarse rule had been learned from one.
- **The measures** (`ladder.py`) are the first look's, made so that everything but a run-on
  can be worked out again from the records. A record holds tallies, not grids: for every
  [leader of a block][neighbours under species 1][neighbours under species 2], how often
  the block had each leader one tick later, apart over three stretches of the run (64 to
  256, 256 to 1,024, 1,024 to 4,096) and at every tick a block is read at. A rule is a
  tally, a rule is scored on another tally, and the chance of changing hands is read off
  one. The tallies give the first look's own tables to the last count.
- **The reference rules** (`reference.json`) are the first look's: the tables all eight
  runs of each of its worlds give. They are fixed in the registration and tried,
  unchanged, on fresh starts and in worlds they have not seen.
- **Sizing first** (`sizing.py`, exploratory). The first look's sixteen runs were put
  through the study's own measures with the starts dealt six ways (which four to learn
  from), and twice more with a rule from four starts set against fresh rules from two. That
  says how far each number moves when nothing changes but the starts, and every bound was
  drawn outside it. Every claim of the first look's worlds held on all eight of those, as
  it must: they are the runs the claims were read from.
- **The control taught the test something before it was registered.** The sizing look ran
  the control once, small (side 512, two starts). Its leaders stop: after generation 1,024
  one block in a thousand has another leader 3,072 generations on. The still world's rule
  is 93% to 191% worse there than the control's own on the square clock, and run on it
  takes 37% to 40% of the blocks away from where they stay. But at the shortest tick it is
  kept at, where blocks change hands least, the still world's rule comes within 5% at
  blocks of 16: a world that has stopped looks like a world slowed right down. So "serves
  at another pace" cannot by itself tell one rule from a stopped world, and the test asks
  three things of each unseen world, not one: that it keeps growing, that the still world's
  rule serves, and that the still world's rule, run on, keeps it.
- **Not tested is not failed**, in three ways, all fixed beforehand. A claim about a world
  that keeps growing is not tested where the world does not (its walls at blocks of 16
  fall by under a fifth after generation 1,024, or under a twentieth of its blocks change
  leader). The control's claims are not tested unless the control has set. And a run-on is
  read only through blocks small beside a world's territories (five blocks across or more
  when the rule is started): through blocks of 32 the first look's rule did little better
  than supposing nothing moved, and a world with smaller territories would be in that
  place at blocks of 16.

**The predictions**, 89 in eight families. Surprise is as before; "amiss over changed" is
the share of blocks whose leader is not the real world's at generation 4,096 after a rule
has been run on by itself from generation 1,024, over the share that changed leader
meanwhile (1 is no better than supposing nothing moved).

| Family | What is predicted | The first look's runs gave | Bound |
| --- | --- | --- | --- |
| N, surrounded (6) | in the still and the busy world the neighbours remove this share of the surprise at blocks of 4 and 8 | 0.44; 0.40 to 0.42 | at least 0.35 |
| | a block of 4 with five neighbours under its rival changes hands with this chance | 0.371 in both | 0.32 to 0.42 |
| T, one rule at every time (6) | the rule learned before generation 1,024 has this much more surprise after it, at blocks of 4, 8, 16 | 0.2% to 0.3%; 0.9% to 1.1%; 1.9% to 3.4% | at most 0.6%, 2%, 5% |
| R, rungs and clocks (14) | the rule from blocks half the size is nearer the rung's own on the square clock than on the block clock, at blocks of 8 and 16 | by 3 to 8 points | nearer |
| | on the square clock its gap at blocks of 16 over its gap at blocks of 8 | 0.39 to 0.63 | under 1 |
| | and its gap at blocks of 16 is still | 3.4% to 4.2% | at least 1.5% |
| | at matched ages, the second gap over the first | 0.25 to 0.50 | at most 0.65 |
| | the chance of changing hands at blocks of 4 over that at blocks of 8, five rival neighbours | 2.28, 2.07 with the clock at the block; 1.53, 1.45 at its square | 1.8 to 2.9; 1.2 to 1.75 |
| X, fresh starts (4) | the first look's rule for a world has this much more surprise on fresh starts of it than a rule learned from them, at blocks of 8 and 16 | −0.4% to 0.05% with half the data | at most 0.3%, 0.5% |
| B, the other world (10) | the first look's rule for one world, in the other, at blocks of 4, 8, 16 | 1.6% to 1.8%; 0.4% to 0.5%; −0.2% to 0.3% | at most 2.5%, 0.8%, 0.8% |
| | the two worlds' chances of changing hands at 4, 5 and 6 rival neighbours, at blocks of 8 and 16 | within 5% and 7% (4% to 9% from half the starts) | within 12% |
| | the still world's rule run on in the busy world: amiss over changed, at blocks of 8 and 16 | 0.35 to 0.38; 0.45 to 0.57 | at most 0.70 |
| C, run on by itself (27) | a world's own rule: amiss over changed at blocks of 4, 8, 16 in the still and the busy world, and at 8 and 16 in the three unseen worlds | still 0.50 to 0.59, 0.41 to 0.43, 0.53 to 0.54; busy 0.31 to 0.39, 0.30 to 0.36, 0.45 to 0.48 | at most 0.70 |
| | the walls it keeps over the world's, at blocks of 16, in all five | 0.96 to 0.99; 0.99 to 1.03 | 0.85 to 1.12 |
| | at blocks of 4 it loses walls too fast (still, busy) | 0.72 to 0.81; 0.83 to 0.89 | at most 0.93 |
| | amiss over what two runs of the rule differ by, at blocks of 8 and 16 (still, busy) | 1.07 to 1.24, 0.84 to 0.94; 0.94 to 1.09, 0.83 to 0.92 | at most 1.4 |
| | amiss on the square clock over amiss on the block clock, at 8 and 16 (still, busy) | 0.70 to 0.83; 0.54 to 0.76 | under 1 |
| U, worlds never zoomed out (18) | in each of the three, at blocks of 8 and 16: the still world's rule has this much more surprise than the world's own | not run | at most 1% |
| | the same at the best of the ticks the rule is kept at | not run | at most 1% |
| | the still world's rule run on there: amiss over changed | not run | at most 0.70 |
| Z, the control (4) | in the world that has set, the still world's rule has this much more surprise, at blocks of 8 and 16 | 191%, 93% (side 512) | at least 25% |
| | run on there, blocks amiss less blocks that changed | 0.40, 0.37 | at least 0.10 |

What I expect, written before the run: the first look's two worlds to hold (they are a
second sample of what the claims were read from, and the sizing says how far a sample
moves); the near relative to follow the still world's rule as it is; the other still world
to follow it at least at some pace; and the sparse world to be the one that tells. Its
territories exist only because a contested cell stays empty, a quarter of its cells are
live, and its grounds never settle. If the still world's rule runs that world on, one
coarse rule covers worlds whose cells have nothing in common, and if it does not the class
has an edge, and the test says where.

**Gate:** the verdict, whichever way it goes.

**The run** (2026-11-26, on a rented pod, because two other jobs had this machine's spare
cores: 44 fine runs and 108 run-ons in 51 minutes on 22 workers, $0.96 of the $3.36 agreed).
**73 of the 89 predictions held, 8 failed and 8 were not tested.** The ledger verifies. Six
run-ons computed again on this machine came out byte for byte, and so did the records of
five fine runs recomputed here from scratch.

| Family | Held | Result |
| --- | --- | --- |
| N, surrounded | 6 of 6 | the neighbours remove 0.44 and 0.40 of the surprise at blocks of 4 and 8 in the still world, 0.44 and 0.41 in the busy one; a block of 4 with five rival neighbours changes hands with a chance of 0.372 in both (the first look: 0.371) |
| T, one rule at every time | 6 of 6 | the early rule has 0.23%, 1.0% and 2.2% more surprise late at blocks of 4, 8, 16 (still); 0.25%, 0.9% and 2.6% (busy) |
| R, rungs and clocks | 14 of 14 | the rule from the rung below is nearer on the square clock by 7.6 and 7.2 points (still), 3.5 and 6.0 (busy); its gap at blocks of 16 is 0.42 and 0.68 of its gap at 8, and still 3.7% and 4.4%; at matched ages 0.29 and 0.59; a block of 4 changes hands 2.27 and 2.04 times as often as a block of 8 with the clock at the block, 1.53 and 1.43 times with the clock at its square |
| X, fresh starts | 4 of 4 | the first look's rule is within 0.03% of a rule learned from the fresh starts, in both worlds at both blocks |
| B, the other world | 10 of 10 | the still world's rule in the busy world: 1.7%, 0.46%, 0.23% more surprise at blocks of 4, 8, 16; the busy world's in the still: 1.6%, 0.43%, 0.14%; the two worlds' chances of changing hands within 6% at blocks of 8 and 10% at 16; the still world's rule runs the busy world on nearly as well as the busy world's own (amiss over changed 0.37 and 0.56, against 0.36 and 0.53) |
| C, run on by itself | 21 of 27; 1 failed, 5 not tested | amiss over changed at blocks of 4, 8, 16: 0.52, 0.41, 0.54 (still), 0.38, 0.36, 0.53 (busy); walls kept at 16: 0.97, 0.99; at blocks of 4 the rule loses walls too fast (0.75, 0.83 of them); it errs like its own dice (1.15 and 0.94 times what two runs differ by in the still world, 0.98 and 0.85 in the busy); the square clock runs on better than the block clock (0.67 to 0.77 of its blocks amiss). In the near world its own rule gives 0.58 at blocks of 8 and **0.70003 at blocks of 16, against at most 0.70: failed**; walls 0.92. In the other still world 0.61 at blocks of 8; blocks of 16 are too large for its territories and were not tested. In the sparse world no block fits, and nothing was tested |
| U, worlds never zoomed out | 8 of 18; 7 failed, 3 not tested | see below |
| Z, the control | 4 of 4 | the control set, as it should (its walls stay where they were, 0.1% of blocks change leader). The still world's rule has 199% and 207% more surprise there than the control's own, and run on it ends with 42% and 40% of the blocks under another leader |

**The three worlds never zoomed out** gave three different answers, and they are the three I
wrote down before the run.

| World | The still world's rule, as it is | At its best tick | Run on, as it is | Its own rule, run on |
| --- | --- | --- | --- | --- |
| near, B24678/S34678 | 0.60%, 0.51% more surprise (blocks of 8, 16): **holds** | its own tick: **holds** | 0.55, 0.65 of the blocks that changed are amiss: **holds** | 0.58 holds; 0.70003 fails |
| another, B3568/S124678 | 1.8%, 2.5%: **fails** | half its tick, at both blocks: 0.50%, 0.52%: **holds** | 0.75 at blocks of 8: **fails**; blocks of 16 not tested | 0.61 holds; blocks of 16 not tested |
| sparse, B2/S0 | 60%, 57%: **fails** | 60%, 54%: **fails** | not tested (0.80, 0.81) | not tested (0.91, 1.04) |

- **The near relative follows the still world's rule as it is.** The rule read off the first
  look's still world, with nothing fitted to this world, runs it on for 3,072 generations
  as well as the near world's own rule does, and a little better (it was learned from twice
  the runs).
- **The other still world follows it at half the pace.** As it is, the still world's rule is
  1.8% to 2.5% worse there, and run on it moves the walls too fast. The still world's rule
  for half the tick is within 0.5% at both blocks, and the half is the same half at both.
  Its own rule runs it on (0.61 at blocks of 8).
- **The sparse world is not of this kind.** No pace brings the still world's rule within
  54% of its own. Its blocks do not change hands by being surrounded: with the clock at its
  square a block of 8 changes hands with a chance of 0.05, 0.12, 0.20, 0.29, 0.38 with 1 to
  5 neighbours under its rival, very nearly in proportion, where the still world has
  0.00005, 0.001, 0.015, 0.11, 0.24. Read by who leads a block it has no clean territories
  at any block: over a fifth of neighbouring blocks have different leaders at blocks of 8,
  and more at 4 (too few cells in a block to say who leads) and at 16 and 32 (territories too
  small). So its run-ons were not tested, by the rule fixed beforehand; what they measured
  is that its own rule does no better than supposing nothing moved (0.91 and 1.04). Its
  walls thin, but as the 0.27th power of time, where the other four worlds have 0.44 to
  0.49: it grows on another clock.
- **The control is outside, and the test can tell.** In the world that has set, the still
  world's rule is three times as surprised as the control's own and wrecks the world when
  run on. On the larger grid it does not serve there at any tick (62% more at its best,
  where the small sizing look had 5% at blocks of 16).

**The pace, read two ways** (`extras.py`, exploratory: read from the registered records
after the verdict, and one small thing run here). If territories grow as the square root
of the time, a world whose walls move at a share p of the still world's pace has the still
world's walls divided by the square root of p, at any generation. So a world's pace can be
read off how far its territories have got, with no coarse rule in it, and set beside the
tick at which the still world's rule serves it best.

| World | Its walls thin as time to the power | Pace by its walls (generation 1,024 and 4,096) | The still world's rule serves best at |
| --- | --- | --- | --- |
| still | 0.48 to 0.49 | 1 | its own tick |
| busy | 0.47 to 0.49 | 1.10, 1.08 | its own tick |
| near | 0.45 to 0.47 | 0.75 to 0.77, 0.71 to 0.72 | its own tick |
| another | 0.44 to 0.46 | 0.57 to 0.59, 0.52 to 0.53 | half its tick, at both blocks |
| sparse | 0.27 | (no meaning: another clock) | none |

The two readings agree: the world whose walls say half the pace is the one the rule serves
at half the tick, and the one whose walls say three quarters is nearer the whole tick than
the half. And the still world's rule for half the tick, run on in the other still world in
that world's own time, ends with 0.57 of the changed blocks amiss at blocks of 8: better
than as it is (0.75, the registered failure) and no worse than that world's own rule
(0.61). At blocks of 16, where its territories are too small for the registered test, 0.70
against 0.84 as it is and 0.80 for its own. None of this was registered.

**The failures.** Eight, of three kinds.

- *One by a hair, and mine.* The near world's own rule at blocks of 16 ends with 0.70003
  of the changed blocks amiss, against a bound I drew at 0.70. The near world at blocks of
  16 is at the edge of what the test reads at all (its walls are 0.197 of neighbouring
  pairs where the limit is 0.2). The claim failed as registered. What it measured is a rule
  that gets three blocks in ten right that "nothing moved" gets wrong, where the first
  look's worlds get nearly five in ten.
- *Three that say the pace belongs to the world.* In the other still world the rule as it
  is fails at both blocks and its run-on fails at blocks of 8, while the rule at half the
  tick holds at both. The claim "as it is" was the one I thought least likely to hold
  there, and the test was built to tell this from the next kind.
- *Four that find the edge.* The sparse world, as it is and at every pace, at both blocks.

**Not tested**, eight, all by the rule that a run-on is read only through blocks small
beside the territories: the other still world at blocks of 16, and the sparse world at
every block.

**What step 4e shows.**

1. **What the first look saw of its two worlds is so.** All 58 claims about them held on
   fresh starts, most at the first look's own figure to two places. The first look's
   tables, tried unchanged on starts they had not seen, are as good as tables learned from
   those starts.
2. **A coarse rule stands in for a world of this kind.** Who leads each block, and what
   blocks with as many rival neighbours did next, runs such a world on without its cells
   for three thousand generations, keeps its walls, and has the right leader in about half
   to two thirds of the blocks that change. It is now a registered result for two worlds,
   and holds for the two still worlds that had never been zoomed out at the block where
   the test could read them.
3. **It is one rule with a pace, for worlds whose grounds fill, and it has an edge.** Of
   three worlds whose cells share nothing with the still world's, one follows its rule as
   it is, one at half the pace, and one not at all. The one that does not is the one that
   is a different kind of world by every other reading too: sparse, without clean
   territories, on another clock. This is the "classes" row of the table at the top of this
   plan with something in it: a class of at least four fine rules, a number that places
   each in it (its pace), and a rule outside it.
4. **The ladder still has no fixed point**, and the test agrees with the first look about
   where it stands: from one rung to the next the rule changes on both clocks, by less on
   the square clock and by less at the second rung than the first, and at blocks of 16 the
   rule from blocks of 8 is still 4% short.

**What it does not show.** Five worlds and a control, all under the standoff, on one grid
size. "At another pace" was tried on a grid of ticks a factor of two apart, so a pace is
known to within about that. The class is four worlds: two it was read from, one near
relative, and one stranger at half the pace. One stranger is not many. That the sparse
world is outside is a finding about this reading of it (who leads a block): a reading that
suits a sparse world might find a rule there. And the fixed-point question is where the
first look left it, with one registered sample more.

**Gate: passed** in the sense the plan gives it, with eight failures on the record: one
mine, three that are the pace, four that are the edge.

### Step 4f: how wide is the class (registered and run 2026-11-26: 54 of 128 held)

Step 4e left "one rule with a pace" resting on four worlds and a stranger. You chose to ask
how wide the class is (decision D11, option a): `examples/scale-up-class/study.py`,
registered on 2026-11-26 with 128 predictions before any of its runs was made.

- **The worlds are not the ones I said.** I spoke of twenty worlds that fill their grid.
  Step 4c's runs do not hold twenty. Of its 842 rules, 207 grew territories against their
  copy under the standoff from a full start, and by how much of the grid was live at the
  end of that run they are mostly busy worlds, not filling ones:

  | Share of the grid live | under 0.3 | 0.3 to 0.5 | 0.5 to 0.7 | 0.7 to 0.9 | 0.9 or more (fills) |
  | --- | --- | --- | --- | --- | --- |
  | of the 207 | 8 | 76 | 100 | 12 | 11 |
  | of the 80 among the 600 rules of the even draw | 3 | 30 | 38 | 5 | 4 |

  So the test takes all 11 that fill and, from the even draw, 27 of the 76 that do not:
  all 3 under three tenths, the first ten drawn in each of the two middle bands, the first
  four of the top one. 38 worlds, none of them run on a large grid or zoomed out before.
  That asks more than I promised, at the same cost: how wide the class is among the worlds
  that fill, and where it ends among the far more numerous worlds that do not.
- **What is run.** Each world against its copy under the standoff from a full start, on side
  1,024 for 4,096 generations, from four fresh starts (two to learn its own rule from, two
  to try on; 17001 on). The still world is run again from eight, read so that its rule can
  be learned at eleven paces, a quarter to four times the square clock's (blocks of 8 are
  read every four generations for that). Its rule here is the one every world is tried
  with. 160 fine runs and 456 run-ons.
- **What is read of each world** (the measures are step 4e's).
  - *Its clock:* the power of time by which its walls thin between generations 1,024 and
    4,096, at blocks of 8.
  - *Whether the still world's rule serves it:* the least, over the eleven paces, of how
    much more surprise that rule has on the world's trial starts than the world's own.
  - *Its pace, two ways:* by its walls (the square of the still world's walls over its own,
    which owes nothing to any coarse rule), and by the rule (the pace at which the still
    world's rule serves it best).
  - *Run on:* the still world's rule for the pace the world's walls give, run on by itself
    from generation 1,024 in the world's own time.
- **Sizing** (`sizing.py`, exploratory; it ran nothing). The six worlds of step 4e through
  these measures, from its registered records:

  | World | Walls thin as time to the power | The still world's rule at its best pace | Pace by its walls | Pace by the rule (blocks of 16) | Run on at blocks of 8 |
  | --- | --- | --- | --- | --- | --- |
  | still | 0.49 | (itself) | 1 | 0.99 | – |
  | busy | 0.49 | 0.5% more surprise | 1.09 | 1.04 | 0.37 as it is |
  | near | 0.47 | 0.6% | 0.73 | 0.93 | 0.55 as it is |
  | another | 0.46 | 0.5% | 0.54 | 0.57 | 0.57 at half its pace; 0.75 as it is |
  | sparse | 0.27 | 60% | – | – | – |
  | the control (set) | 0.00 | 120% | – | – | – |

  One start's power is 0.40 to 0.55 in the first four and 0.21 to 0.31 in the sparse world.
  The two paces are within a factor of 1.05 of each other in two worlds and 1.28 in the
  near one, which is how loosely the pace claim is drawn.

**The predictions**, 128 in six families.

| Family | What is predicted | Bound |
| --- | --- | --- |
| A, its clock says (38) | for each world: if its walls thin as the 0.40th power of time or more, the still world's rule serves it at some pace; if as the 0.33rd or less, it does not | at most 1% more surprise; at least 5% more |
| F, a filling world's clock (11) | each world that fills keeps the square-root clock or has set | its power is 0.40 or more, or 0.10 or less |
| P, the pace two ways (38) | for each world on the square-root clock: the pace by the rule and the pace by its walls agree | within a factor of 1.5 |
| K, run on at its walls' pace (38) | for each such world: the still world's rule for that pace, run on by itself, keeps it | amiss in at most 0.70 of the blocks that changed leader |
| R, the ranks (1) | over those worlds, the faster by its walls is the faster by the rule | rank correlation at least 0.5 |
| X, the anchor (2) | the first look's rule serves on the still world's fresh starts here | at most 0.3% and 0.5% more surprise |

- **Not tested**, fixed beforehand: any claim about a world in which one species has all
  but taken the grid (the larger has over 0.8 of the live cells); A where the clock is
  between the two powers; P and K off the square-root clock, or at a pace the eleven do
  not come near (under 0.2 or over 5); K where blocks of 8 are too large for the world's
  territories; R over fewer than eight worlds.
- **What I expect, written before the run.** The anchor to hold. Most of the eleven filling
  worlds to keep the square-root clock and be served; one or two to have set, as step 4e's
  control did; and if any falls between it will be B0145678/S045678, born on no neighbours
  and holding territories under the standoff only. Most worlds of the two upper busy bands
  to be served, as the first look's busy world is. I do not know about the band from three
  to five tenths, which is where I expect the edge to run. The three under three tenths I
  expect outside, like B2/S0, though two of them hold territories under both tie-breaks and
  B2/S0 does not, so that is a guess. Family A is the claim I most want the answer to, and
  it can fail either way: a world on the square-root clock that the rule does not serve, or
  one off it that it does. It was read off five worlds.

**Gate:** the verdict, whichever way it goes.

**The run** (2026-11-26, on a rented pod: 160 fine runs and 456 run-ons in 81 minutes, $1.99;
getting there cost another $1.23, told under the costs below). **54 of the 128 predictions
held, 55 failed and 19 were not tested.** The ledger verifies; six records computed again on
this machine came out byte for byte, and so did the records of six fine runs recomputed here
from scratch.

| Family | Held | Failed | Not tested |
| --- | --- | --- | --- |
| A, its clock says whether the rule serves | 17 | 20 | 1 |
| F, a filling world keeps the square-root clock or has set | 8 | 3 | 0 |
| P, the pace two ways | 8 | 21 | 9 |
| K, run on at its walls' pace | 19 | 10 | 9 |
| R, the ranks | 0 | 1 | 0 |
| X, the anchor | 2 | 0 | 0 |

The claim I most wanted the answer to is refuted, and in the direction that matters: **a
world can keep the class's clock and not follow its rule.** The 38 worlds, by what they
did (live is the share of the grid live at the end; the clock is the power of time its walls
thin by; "more surprise" is the still world's rule at its best pace beside the world's own;
the last two columns are a rule run on by itself from generation 1,024, blocks amiss over
blocks that changed):

*Served: on the square-root clock, and the still world's rule within 1% (10 worlds).*

| World | Live | Clock | More surprise | Pace by its walls | The still world's rule at that pace, run on | Its own rule, run on |
| --- | --- | --- | --- | --- | --- | --- |
| B2357/S015678 | 0.98 | 0.51 | 0.5% | 0.87 | 0.50 | 0.40 |
| B24578/S034678 | 0.98 | 0.45 | 0.9% | 0.60 | 0.53 | 0.65 |
| B3568/S24678 | 0.97 | 0.46 | 0.8% | 0.84 | 0.40 | 0.42 |
| B23456/S34678 | 0.95 | 0.46 | 0.2% | 0.40 | 0.83 | 0.69 |
| B23456/S4678 | 0.95 | 0.51 | 0.5% | 1.19 | 0.43 | 0.31 |
| B345678/S03467 | 0.74 | 0.47 | 0.2% | 0.72 | 0.50 | 0.50 |
| B34567/S012457 | 0.69 | 0.50 | 0.2% | 0.86 | 0.38 | 0.38 |
| B356/S2456 | 0.62 | 0.46 | 0.8% | 0.69 | 0.58 | 0.66 |
| B345/S02457 | 0.61 | 0.47 | 0.3% | 1.02 | 0.39 | 0.40 |
| B34568/S247 | 0.56 | 0.50 | 0.5% | 1.08 | 0.40 | 0.48 |

*Near: on the clock, within 2% (4 worlds).*

| World | Live | Clock | More surprise | Pace by its walls | The still world's rule at that pace, run on | Its own rule, run on |
| --- | --- | --- | --- | --- | --- | --- |
| B24567/S0135678 | 0.99 | 0.47 | 1.4% | 0.79 | 0.46 | 0.29 |
| B2348/S25678 | 0.97 | 0.54 | 1.2% | 0.79 | 0.38 | 0.27 |
| B2456/S35 | 0.54 | 0.44 | 1.7% | 0.79 | 0.49 | 0.65 |
| B234678/S1578 | 0.52 | 0.47 | 1.7% | 0.54 | 0.57 | 0.77 |

*Not served: on the clock all the same (15 worlds).*

| World | Live | Clock | More surprise | Pace by its walls | The still world's rule at that pace, run on | Its own rule, run on |
| --- | --- | --- | --- | --- | --- | --- |
| B234567/S01247 | 0.61 | 0.46 | 6.9% | 0.24 | 0.84 | 1.14 |
| B13458/S358 | 0.53 | 0.44 | 12% | 0.61 | 0.59 | 0.83 |
| B24678/S1348 | 0.51 | 0.42 | 13% | 0.28 | 0.70 | 1.05 |
| B238/S1356 | 0.47 | 0.41 | 14% | 0.28 | 0.75 | 1.10 |
| B3468/S2378 | 0.47 | 0.43 | 3.8% | 0.56 | 0.50 | 0.73 |
| B2378/S1348 | 0.47 | 0.42 | 16% | 0.27 | 0.82 | 1.09 |
| B1234/S48 | 0.46 | 0.40 | 16% | 0.25 | 0.83 | 1.11 |
| B38/S013467 | 0.44 | 0.46 | 5.3% | 0.49 | 0.63 | 0.86 |
| B2478/S1467 | 0.42 | 0.41 | 20% | 0.35 | 0.78 | 1.04 |
| B2367/S3 | 0.41 | 0.46 | 4.7% | 0.69 | 0.47 | 0.78 |
| B2458/S578 | 0.38 | 0.47 | 4.9% | 0.72 | 0.46 | 0.68 |
| B358/S02378 | 0.35 | 0.44 | 21% | 0.28 | 0.71 | 1.04 |
| B2568/S05 | 0.29 | 0.41 | 29% | 0.35 | 0.71 | 0.99 |
| B25/S078 | 0.27 | 0.41 | 38% | 0.33 | 0.69 | 0.95 |
| B25/S678 | 0.25 | 0.42 | 26% | 0.43 | 0.72 | 0.92 |

*Off the clock (9 worlds): five have set, four thin their walls more slowly.*

| World | Live | Clock | More surprise |
| --- | --- | --- | --- |
| B358/S035678 | 0.99 | 0.27 | 9.1% |
| B2356/S025678 | 0.98 | 0.26 | 4.8% |
| B0145678/S045678 | 0.97 | 0.00 | 36% |
| B347/S0125678 | 0.97 | 0.14 | 16% |
| B024578/S014567 | 0.90 | 0.00 | 23% |
| B038/S034578 | 0.77 | 0.03 | 16% |
| B05678/S45678 | 0.75 | 0.00 | 28% |
| B02347/S034578 | 0.64 | 0.03 | 56% |
| B01458/S68 | 0.36 | 0.36 | 42% |

**What step 4f shows.**

1. **The clock is common; the rule is not.** 29 of the 38 worlds thin their walls as the
   0.40th to 0.54th power of time, the still world's clock. The still world's rule serves
   10 of those within 1% and 4 more within 2%. The other 15 it does not serve, by 4% to
   38%. So the square-root clock does not mark the class, and claim A failed for 20 worlds.
   Its other half held: no world off the clock is served (eight not by 9% to 56%; the
   ninth, B2356/S025678, by 4.8%, which fails a bound of 5% by a hair).
2. **What marks the class is how full the world is.** Every world the rule serves has more
   than half its grid live (0.56 to 0.98), and every world on the clock that it misses by
   more than 2% has 0.61 or less, all but two 0.51 or less. Over the 29, the fuller the world
   the nearer the rule (rank correlation −0.82 between the share live and the extra
   surprise). The edge runs at about half the grid, where I had guessed it somewhere
   between three and five tenths. Weighted by how many rules each band stands for, the
   class is 23% of the rules of an even draw that grow territories against their copy.
3. **Run on, the still world's rule reaches further than it serves.** At the pace a world's
   walls give, it keeps 19 of the 29 worlds on the clock (amiss in at most 0.70 of the
   blocks that changed): 9 of the 10 it serves, all 4 it nearly serves, and 6 of the 15 it
   does not. In those 15 the world's own rule, which is the better table one step ahead,
   is the worse rule to run: it ends little or no nearer the world than supposing nothing
   moved (0.68 to 1.14, seven of them over 1), where the still world's rule at their pace
   ends at 0.46 to 0.84. Over all 29 the still world's rule beats the world's own in
   23. A table that is best one step ahead is not the table that carries the territories:
   in a thin, busy world a block's leader flickers, the world's own table learns the
   flicker, and the flicker is not where the walls go.
4. **The pace is loose, and it is not the rule's pace.** Inside the class the pace by the
   rule is within a factor of 1.5 of the pace by the walls in 8 worlds of 10, and the two
   rank together only weakly (0.33). Outside it the rule's best pace means nothing, which
   is why claims P and R failed as registered: I drew them over every world on the clock,
   taking the clock for the class. The half-pace world of step 4e, whose two paces agreed
   to 5%, was a good case and not the rule. The walls' pace is still good enough to choose
   the table to run on.
5. **A world that fills can keep another clock.** Three of the eleven filling worlds thin
   their walls as the 0.14th to 0.27th power of time (claim F failed for them), and none
   of the three is served. All three let a cell with no neighbour of its own kind survive,
   but so do four of the other eight, so that explains nothing by itself. One filling world
   has set, as the control of step 4e did. The other seven are on the clock.
6. **The anchor held:** the first look's rule is within 0.2% of a rule learned from the
   still world's fresh starts here.

**Against what I wrote before the run.** The anchor held, as expected. "Most of the eleven
filling worlds to keep the square-root clock and be served": seven keep it and five are
served, so no. "One or two to have set": one. "If any falls between it will be
B0145678/S045678": it set; the three that fell between are others. "Most worlds of the two
upper busy bands to be served": five of fourteen, and three of the top band's four have
set. "I do not know about the band from three to five tenths, which is where I expect the
edge": none of its ten is served, and the edge is above it. "The three under three tenths
outside": yes, though they keep the clock, which B2/S0 did not. I was right about where the
uncertainty was and wrong about most of what I thought I knew.

**What it does not show.** One block size (8) for every claim, one grid size, four starts a
world. "Served" is a bound I chose (1%); the worlds do not fall into two heaps but run from
0.2% to 56%, and four sit just over the line. At blocks of 16 the fifteen the rule misses
are mostly a tenth to a third nearer (3.3% to 26%), and two of the four just over the line
are inside it (0.5% and 0.8%); so some worlds may join at larger blocks, and this run
cannot say. The share of 23% rests on 27 worlds for 76 rules. And the reason given in point
3 is a reading of the numbers, not something tested.

**Gate: passed** in the sense the plan gives it: the verdict is in, and it refutes the
claim it was built to test.

### Step 4g: one more rung (registered and run 2026-11-26: all 22 held)

The ladder looks for a rule that stops changing from rung to rung. Steps 4d and 4e found the
rule still changing at blocks of 16, by less at each rung on the square clock. You chose to
read one rung more after the class (decision D11, option b):
`examples/scale-up-rung/study.py`, registered on 2026-11-26 with 22 predictions before any
of its runs was made.

- **What is run.** The still world and the busy world, each against its copy under the
  standoff from a full start, on a wrapped grid of side 2,048 for 16,384 generations, from
  eight fresh starts each (18001 on): twice as wide and four times as long as before, which
  is what blocks of 32 need to be read at the age that matches them. Each such run is
  sixteen of step 4e's. 16 fine runs and 48 run-ons.
- **Every rung at its matched age.** Blocks of 4 over generations 64 to 256, of 8 over 256
  to 1,024, of 16 over 1,024 to 4,096, of 32 over 4,096 to 16,384, each on the square
  clock: 48 coarse generations at every rung.
- **The ladder's own test**, which no step has run until now. The plan's last move is to
  "repeat with the coarse rule as the new fine rule". Here the rule learned at one rung is
  used, unchanged, as the rule of the rung above and run on by itself there, beside the
  rung's own rule.
- **Sizing** (`sizing.py`, exploratory; it ran nothing). The first three rungs can be read
  at matched ages from the first look's kept runs:

  | | blocks of 4 | 8 | 16 | 32 |
  | --- | --- | --- | --- | --- |
  | still: walls when its age starts | 0.178 | 0.167 | 0.175 | 0.170 |
  | still: the rule from the rung below, more surprise | – | 8.7% | 2.6% | ? |
  | still: chance of changing hands, five rival neighbours | 0.310 | 0.238 | 0.200 | ? |
  | still: run on, amiss over changed, its own rule | – | 0.62 | 0.53 | ? |
  | still: the same with the rule from the rung below | – | 0.72 | 0.62 | ? |
  | busy: walls when its age starts | 0.163 | 0.164 | 0.162 | 0.166 |
  | busy: the rule from the rung below, more surprise | – | 5.7% | 2.5% | ? |
  | busy: chance of changing hands, five rival neighbours | 0.296 | 0.257 | 0.224 | ? |
  | busy: run on, amiss over changed, its own rule | – | 0.51 | 0.50 | ? |
  | busy: the same with the rule from the rung below | – | 0.54 | 0.53 | ? |

  Two things stand out before the new rung is run. At matched ages the two worlds have as
  many walls at every rung, to within 5%: through blocks twice the size, four times later,
  they are the same picture. And the ladder's own move already works at the rungs that
  exist: the rule from blocks half the size runs a world on with 5% to 18% more blocks
  amiss than the rung's own rule.

**The predictions**, 22 in six families.

| Family | What is predicted | Bound |
| --- | --- | --- |
| S, the same picture (2) | at the start of each rung's matched age (blocks of 8, 16, 32) a world has as many walls | within 10% |
| X, another grid (2) | the rule step 4e learned at blocks of 16 on side 1,024 serves on side 2,048 | at most 0.5% more surprise |
| G, the gap (4) | at blocks of 16 the rule from blocks of 8 is as far from the rung's own as before | 1.5% to 4.5% |
| | at blocks of 32 the rule from blocks of 16 is nearer than that | smaller |
| H, the chances level off (2) | a block of 32 with five rival neighbours changes hands this often beside a block of 16 | at least 0.80 times |
| C, the new rung (4) | at blocks of 32 a world's own rule, run on from generation 4,096 to 16,384, is amiss in this share of the blocks that changed leader; and keeps this share of the walls | at most 0.70; 0.80 to 1.15 |
| L, the ladder's own test (8) | the rule from the rung below, used as the rule at blocks of 16 and of 32 and run on there: amiss over changed; and over what the rung's own rule gets amiss | at most 0.75; at most 1.30 times |

- **Not tested:** a run-on through blocks too large for the world's territories when it
  starts (over a fifth of neighbouring blocks under different leaders), as in step 4e.
- **What I expect, written before the run.** S and X to hold: they are the scaling these
  worlds have shown at every step. The gap at blocks of 16 to come out where it was. At
  blocks of 32 I expect it smaller, about 1% in the still world and between 1% and 2% in
  the busy one if the fall goes on as it began, but that is two steps drawn into a third,
  which is the mistake step 4 made, so the claim registered is only "smaller". The
  ladder's own test I expect to hold at both rungs. What the run cannot do is show a fixed
  point reached: at best it shows the rule changing by a third less again.

**Gate:** the verdict, whichever way it goes.

**The run** (2026-11-26, on a rented pod: 16 fine runs and 48 run-ons in 3 hours 35 minutes,
$4.01). **All 22 predictions held.** The ledger verifies and the verdict, judged again from
the records, is the ledger's to the last figure. On this machine, 63 of the 64 records were
computed again from the block leaders the pod kept and came out byte for byte (the leaders of
one run, the busy world from start 18102, were not home before the pod was deleted). And one
whole fine run, the busy world from start 18105, was made again here from its start, in 1
hour 39 minutes of one core: it gave the pod's leaders at every reading of every block size
and the pod's record of the run, byte for byte, and the run-on the verifier asks for first,
computed again from those leaders, is the pod's too.

| Family | Held | Failed | Not tested |
| --- | --- | --- | --- |
| S, the same picture | 2 | 0 | 0 |
| X, another grid | 2 | 0 | 0 |
| G, the gap | 4 | 0 | 0 |
| H, the chances level off | 2 | 0 | 0 |
| C, the new rung | 4 | 0 | 0 |
| L, the ladder's own test | 8 | 0 | 0 |

The ladder as the run read it, on fresh starts and a grid twice as wide (the first three
rungs repeat the sizing table above; the fourth is new):

| | blocks of 4 | 8 | 16 | 32 |
| --- | --- | --- | --- | --- |
| matched age, generations | 64 to 256 | 256 to 1,024 | 1,024 to 4,096 | 4,096 to 16,384 |
| still: walls when its age starts, and ends | 0.178, 0.092 | 0.166, 0.091 | 0.173, 0.092 | 0.178, 0.093 |
| still: the rule from the rung below, more surprise | – | 8.6% | 2.8% | 1.4% |
| still: chance of changing hands, five rival neighbours | 0.310 | 0.239 | 0.204 | 0.182 |
| still: run on, amiss over changed, its own rule | – | 0.60 | 0.54 | 0.51 |
| still: the same with the rule from the rung below | – | 0.73 | 0.61 | 0.55 |
| still: walls kept, its own rule | – | 0.86 | 0.90 | 0.92 |
| busy: walls when its age starts, and ends | 0.162, 0.088 | 0.163, 0.085 | 0.164, 0.086 | 0.168, 0.084 |
| busy: the rule from the rung below, more surprise | – | 5.6% | 3.0% | 1.6% |
| busy: chance of changing hands, five rival neighbours | 0.296 | 0.259 | 0.226 | 0.209 |
| busy: run on, amiss over changed, its own rule | – | 0.53 | 0.46 | 0.39 |
| busy: the same with the rule from the rung below | – | 0.55 | 0.53 | 0.41 |
| busy: walls kept, its own rule | – | 0.89 | 0.94 | 1.00 |

Against their bounds (the still world first, then the busy one):

- **S:** the walls at the start of each rung's age are within 6.8% and 2.9% of each other
  (bound 10%).
- **X:** step 4e's rule, learned on side 1,024, has 0.05% and 0.10% more surprise on side
  2,048 than the rule learned there (bound 0.5%).
- **G:** at blocks of 16 the rule from blocks of 8 has 2.8% and 3.0% more surprise (bounds
  1.5% to 4.5%); at blocks of 32 the rule from blocks of 16 has 1.4% and 1.6%, smaller by 1.4
  and 1.5 points.
- **H:** a block of 32 with five rival neighbours changes hands 0.89 and 0.92 times as often
  as a block of 16 (at least 0.80).
- **C:** at blocks of 32 the world's own rule, run on from generation 4,096 to 16,384, is
  amiss in 0.51 and 0.39 of the blocks that changed leader (at most 0.70) and keeps 0.92 and
  1.00 of the walls (0.80 to 1.15).
- **L:** the rule from the rung below, run on as the rule of the rung above, is amiss in 0.61
  and 0.53 of the changed blocks at blocks of 16, and in 0.55 and 0.41 at blocks of 32 (at
  most 0.75): 1.13 and 1.15 times as many as the rung's own rule, then 1.08 and 1.06 times
  (at most 1.30).

**What step 4g shows.**

1. **The fourth rung is the same picture as the three below it.** At the start of its
   matched age a world has as many walls at every rung, and over each age, which is four
   times the time, they fall to 0.50 to 0.55 of what they were: the square-root clock
   again. Through blocks eight times the size and 64 times later, it is the same world to
   look at.
2. **The rule changes less again.** The rule from the rung below has 8.6%, 2.8% and 1.4%
   more surprise than the rung's own in the still world, and 5.6%, 3.0% and 1.6% in the busy
   one. At the last step the gap halved in both (0.49 and 0.51 of the one before). Start by
   start it is as firm as a difference can be: every trial start's gap at blocks of 32 (1.0%
   to 1.6%, 1.2% to 1.9%) is under every start's at blocks of 16 (2.6% to 2.9%, 2.9% to
   3.2%).
3. **The ladder's own move works at every rung.** The plan's last step, "repeat with the
   coarse rule as the new fine rule", had not been run before. A rule learned from blocks
   half the size, used unchanged, runs the world on and ends amiss in 6% to 15% more blocks
   than the rung's own rule at blocks of 16 and 32. (At blocks of 8, which no claim covered:
   21% and 4% more.)
4. **The higher the rung, the better the rule says where the territories will be.** A
   rung's own rule, run on by itself over the rung's age, is amiss in 0.60, 0.54 and 0.51 of
   the blocks that changed leader in the still world and in 0.53, 0.46 and 0.39 in the busy
   one, and keeps more of the walls each time (0.86 to 0.92, 0.89 to 1.00).
5. **A wider grid changes nothing:** the rule of side 1,024 is the rule of side 2,048 to a
   tenth of a percent.

**What the same records show beside the claims** (`extras.py`, exploratory: read after the
verdict, nothing registered, nothing run; `extras.json`). I looked because "the gap halves"
reads as "nearly there", and wanted to know whether it is. It is not.

- **The gaps do not add up; they compound.** Were the gap a plain distance, a rule from two
  rungs down would be as far off as the two steps between. It is twice as far: at
  blocks of 32 the rule from blocks of 8 has 8.3% and 9.2% more surprise, where the two
  steps between sum to 4.2% and 4.6%; and the rule from blocks of 4 has 36% and 27%, where
  the three steps sum to 12.8% and 10.2%. What adds is the square root of the gap, as it
  would if the gap were the square of a distance and the rule moved the same way at every
  rung: (√2.8 + √1.4)² is 8.0 where 8.3 was measured, (√3.0 + √1.6)² is 8.9 where 9.2 was,
  and the four other pairs come within a tenth as well. So a gap that halves is a step that
  shortens by three tenths, not by half: as square roots of the gap in percent the steps
  are 2.9, 1.7 and 1.2 in the still world and 2.4, 1.7 and 1.2 in the busy one, each 0.57
  to 0.74 of the one before.
- **What moves is how often a block on a wall changes hands.** Blocks with three or four
  of their eight neighbours under the rival are a fifth of all blocks, and they carry 77%
  to all of the gap at every rung. Their chance of changing hands falls by the same share at
  each rung: at three rival neighbours by half (0.042, 0.015, 0.0076, 0.0038 in the still
  world; 0.024, 0.012, 0.0053, 0.0024 in the busy one), at four by a quarter to a third
  (0.162, 0.104, 0.076, 0.058; 0.140, 0.105, 0.076, 0.055). The more rival neighbours, the
  less the chance still falls: at five by about a tenth at the last rung (the 0.89 and 0.92
  of claim H), at six by 6% and 1%. Beyond six there are too few blocks of 32 to say (one
  with seven rival neighbours was seen about 500 times in a world). So the table is
  settling from the top down.
- **The two worlds' rules stay as near each other as they were, and no nearer.** At blocks
  of 8, 16 and 32 the busy world's rule has 0.4%, 0.4% and 0.6% more surprise in the still
  world than its own, and the still world's 0.4%, 0.3% and 0.2% in the busy one. At blocks
  of 32 the difference between the worlds is a seventh to two fifths of the difference
  between rungs.
- **Blocks of 32 are few.** A start has 4,096 of them. On the mean of four trial starts the
  ladder's own test held with room; in single starts the rule from below is amiss in 0.94
  to 1.23 times as many blocks as the rung's own in the still world and 0.91 to 1.19 in the
  busy one, so in some starts it does the better of the two.

**Against what I wrote before the run.** S and X held, as expected, and the gap at blocks of
16 came out where it was (2.8% and 3.0%; 2.6% and 2.5% to 3.4% before). At blocks of 32 I
expected about 1% in the still world and between 1% and 2% in the busy one: 1.4% and 1.6%.
The ladder's own test held at both rungs. "At best it shows the rule changing by a third
less again": the gap halved, and the step it is the square of shortened by three tenths.

**What it does not show.** A rule that has stopped changing. One new rung, two worlds, both
inside the class of step 4f, four trial starts each. If the steps go on shortening as they
have, by about three tenths a rung, they add up to an end: a rule the ladder is climbing
towards. But from blocks of 32 that end is then still about as far as blocks of 32 are from
blocks of 8 (some 8% more surprise), it takes three more rungs to come within about 1% of
it, and each rung costs sixteen times the one before. That is two or three steps drawn into
many, which is the mistake step 4 made, so it is a guess and I registered nothing on it.
Where the chances at three and four rival neighbours stop falling, this run cannot say: they
were still falling by the same share at the last rung. And why it is the blocks on a wall
that keep changing I have not tested. One reading is that a wall wavers, and its wavering
is a smaller share of a larger block; a correction that fell as one over the square root of
the block would shorten each step by three tenths, as here. Another rung alone would not
tell that from other slow approaches.

**Gate: passed.** The verdict is in: every prediction held, and the rule has not stopped
changing. What to do about that is decision D12.

### Step 4h: a rule that remembers (first look, exploratory, 2026-11-27)

Step 4g left a rule that still changes from rung to rung, and a first number that said the
symbol leaves something out: who led a block a tick ago. You chose to look at the reading
that carries it (decision D12, option a). `examples/scale-up-memory/look.py` is that look.
Nothing in it is registered, and no world was run for it.

- **What is read.** The block leaders of step 4g's sixteen runs, every rung at its matched
  age, as there. Fifteen had come home from the pod. The sixteenth (the busy world from
  start 18102) was made again here in 1 hour 38 minutes of one core, and its record is the
  pod's byte for byte: with it, all 64 records of step 4g have been computed again on this
  machine.
- **A symbol that remembers.** The rule is asked the same question of a block, with more
  in view. *As it is:* the block's leader, and how many of its eight neighbours each
  species leads. *With its leader one tick before:* the same, and who led the block a tick
  ago (the reading D12 named). *With how long it has had its leader:* the same, and for how
  many ticks running the block has had its present leader, counted up to a cap (4 or 8
  ticks for a rule, 16 for the tables below). A matched age runs from 16 ticks of a rung's
  clock to 64 at every rung, so "how long" means the same thing at each.
- **Checked against the registered run on the way.** With nothing of the past in view
  every tally is step 4g's record, count for count, and every run-on is step 4g's run-on,
  figure for figure. The look stops if either is not so.
- **Little data at the top.** A grid of side 2,048 has 4,096 blocks of 32. A rule with
  more in view has more to learn, and at blocks of 32 what it has not yet learned from four
  starts costs it as much surprise as the differences this look is after. So one tick ahead
  every rule is scored twice, having learned from all its starts and from half of them, and
  told as it would be with endless data; and every way of choosing four of a world's eight
  starts to learn from is taken (70 of them), with the spread between them. Step 4g's own
  way, kept beside it, flatters the rule from the rung below a little at blocks of 32 (1.4%
  and 1.6% where this gives 1.5% and 1.8%), and far more for a rule with more in view.
  Run-ons do not have the trouble: a rule that learned from half its starts ends amiss in
  0.98 to 1.01 times as many blocks as one that learned from all four.

**What it found.**

1. **How long a block has had its leader says a great deal about what it does next.** The
   chance that a block of 16 has another leader one tick on, by how many of its neighbours
   its rival leads:

   | Ticks the block has had its leader | still: 3 rival neighbours | 4 | 5 | busy: 3 | 4 | 5 |
   | --- | --- | --- | --- | --- | --- | --- |
   | 1 | 0.114 | 0.306 | 0.551 | 0.097 | 0.327 | 0.627 |
   | 2 | 0.053 | 0.197 | 0.442 | 0.036 | 0.200 | 0.505 |
   | 3 or 4 | 0.025 | 0.135 | 0.392 | 0.017 | 0.128 | 0.438 |
   | 5 to 8 | 0.011 | 0.086 | 0.308 | 0.0059 | 0.075 | 0.319 |
   | 9 to 15 | 0.0040 | 0.054 | 0.187 | 0.0021 | 0.046 | 0.197 |
   | 16 and more | 0.0015 | 0.039 | 0.157 | 0.0008 | 0.041 | 0.190 |
   | whatever its past (the rule as it is) | 0.0076 | 0.076 | 0.204 | 0.0053 | 0.076 | 0.226 |

   The rule as it is has one number where the world has a ladder of them. A block that
   came over one tick ago, with four rival neighbours, goes again with a chance of 0.31;
   one that has held for sixteen ticks, with 0.04. Counted in surprise the gain is modest,
   because blocks that have just changed hands are few (one or two in a hundred): who led
   the block one tick before removes 5% to 8% of the plain rule's surprise, and how long it
   has had its leader 6% to 11%, in both worlds. What the symbol hides is where the wall
   inside the block is. A block that has just changed hands has it near its middle.
2. **With the past in view, the top of the table is the same at every rung. The bottom is
   not.** The chance of another leader one tick on, rung by rung:

   | | blocks of 4 | 8 | 16 | 32 |
   | --- | --- | --- | --- | --- |
   | still, 5 rival neighbours: the rule as it is | 0.310 | 0.239 | 0.204 | 0.182 |
   | still, 5: the same, were only the mix of young and old leads to change | 0.321 | 0.246 | 0.207 | 0.182 |
   | still, 5: a lead of 16 ticks or more | 0.182 | 0.164 | 0.157 | 0.156 |
   | still, 4: the rule as it is | 0.162 | 0.104 | 0.076 | 0.058 |
   | still, 4: a lead of 16 ticks or more | 0.080 | 0.051 | 0.039 | 0.033 |
   | still, 3: the rule as it is | 0.042 | 0.015 | 0.0076 | 0.0038 |
   | still, 3: a lead of one tick | 0.210 | 0.152 | 0.114 | 0.079 |
   | still, 3: a lead of 16 ticks or more | 0.016 | 0.0040 | 0.0015 | 0.0006 |
   | busy, 5 rival neighbours: the rule as it is | 0.296 | 0.259 | 0.226 | 0.209 |
   | busy, 5: the same, were only the mix of young and old leads to change | 0.300 | 0.264 | 0.230 | 0.209 |
   | busy, 5: a lead of 16 ticks or more | 0.203 | 0.190 | 0.190 | 0.190 |
   | busy, 4: the rule as it is | 0.140 | 0.105 | 0.076 | 0.055 |
   | busy, 4: a lead of 16 ticks or more | 0.072 | 0.051 | 0.041 | 0.035 |
   | busy, 3: the rule as it is | 0.024 | 0.012 | 0.0053 | 0.0024 |
   | busy, 3: a lead of one tick | 0.173 | 0.144 | 0.097 | 0.051 |
   | busy, 3: a lead of 16 ticks or more | 0.0075 | 0.0025 | 0.0008 | 0.0003 |

   At five rival neighbours the plain rule's chance falls by three to four tenths up the
   ladder, which is what step 4g's claim H was about. A block with an old lead does nothing
   of the kind: in the busy world it is 0.190 at blocks of 8, 16 and 32. What changes is
   the mix. The higher the rung, the fewer blocks have just changed hands: 2.3% of the
   still world's blocks of 4 have had their leader one tick, and 0.9% of its blocks of 32.
   The second row of each world is the rule as it is with the top rung's chance for each
   span of time and each rung's own mix: it falls as the plain rule does, a little more.
   So at five the whole of the plain rule's fall is the mix, and at six most of it. At four
   the mix is a third to two fifths of the fall, and at three about a tenth: there a
   block's chance itself falls at every rung, by a sixth to a half for a lead one tick old
   and by more than half for an old one. For an old lead at four the steps halve (0.080,
   0.051, 0.039, 0.033 and 0.072, 0.051, 0.041, 0.035), as they would on the way to a
   chance of about 0.03.
3. **So one tick ahead the rule that remembers still changes from rung to rung, a little
   less.** The rule learned one rung down has this much more surprise than the rung's own,
   with endless data (and the spread between choices of starts):

   | | at blocks of 8 | 16 | 32 |
   | --- | --- | --- | --- |
   | still: the rule as it is | 8.6% | 2.8% | 1.5% ± 0.2 |
   | still: with its leader one tick before | 8.0% | 2.6% | 1.2% ± 0.3 |
   | still: with how long, up to 4 ticks | 7.3% | 2.3% | 1.1% ± 0.5 |
   | still: with how long, up to 8 ticks | 7.0% | 2.1% ± 0.4 | 0.6% ± 0.9 |
   | busy: the rule as it is | 5.6% | 3.0% | 1.8% ± 0.2 |
   | busy: with its leader one tick before | 5.8% | 2.7% | 1.3% ± 0.3 |
   | busy: with how long, up to 4 ticks | 5.8% | 2.5% | 0.8% ± 0.5 |
   | busy: with how long, up to 8 ticks | 5.7% | 2.2% ± 0.3 | −0.4% ± 1.1 |

   Where no spread is given it is 0.1 or less. At blocks of 8 and 16 the data are ample and
   the answer is plain: with the most in view the gap is a quarter less at blocks of 16
   (a third less counted in bits), a fifth less at blocks of 8 in the still world, and no
   less there in the busy one. At blocks of 32 the spread is as wide as the differences,
   and for the rule with most in view wider than the gap: these runs cannot say.
4. **Run on, the rule that remembers is the better rule, most of all at the lower rungs.**
   Each rule run on by itself over a rung's matched age, sixteen runs from each of four
   trial starts. Blocks whose leader is not the real world's at the end, over blocks that
   changed leader meanwhile; and the walls kept:

   | | blocks of 8 | 16 | 32 |
   | --- | --- | --- | --- |
   | still, blocks amiss: the rule as it is | 0.60 | 0.54 | 0.51 |
   | still, blocks amiss: with its leader one tick before | 0.50 | 0.46 | 0.47 |
   | still, blocks amiss: with how long, up to 8 ticks | 0.44 | 0.43 | 0.47 |
   | busy, blocks amiss: the rule as it is | 0.51 | 0.46 | 0.38 |
   | busy, blocks amiss: with its leader one tick before | 0.42 | 0.41 | 0.37 |
   | busy, blocks amiss: with how long, up to 8 ticks | 0.40 | 0.41 | 0.39 |
   | still, walls kept: the rule as it is | 0.86 | 0.89 | 0.93 |
   | still, walls kept: with its leader one tick before | 0.94 | 0.97 | 0.99 |
   | still, walls kept: with how long, up to 8 ticks | 1.01 | 1.03 | 1.04 |
   | busy, walls kept: the rule as it is | 0.89 | 0.93 | 1.00 |
   | busy, walls kept: with its leader one tick before | 0.98 | 1.02 | 1.06 |
   | busy, walls kept: with how long, up to 8 ticks | 1.04 | 1.07 | 1.10 |

   - **Fewer blocks amiss.** With how long in view the rule ends with the wrong leader in
     0.73 and 0.77 of the plain rule's blocks at blocks of 8 (still, busy), in 0.80 and
     0.89 at blocks of 16, and in 0.91 and 1.02 at blocks of 32. At blocks of 8 and 16 that
     is so in every start (0.72 to 0.90). At blocks of 32 it is so in every start of the
     still world, and in the busy world there is no gain.
   - **The walls.** The plain rule's world coarsens too fast: it ends with 86% to 93% of
     the walls in the still world, and with 89% and 93% at blocks of 8 and 16 in the busy
     one. The rule that remembers keeps them in the still world (within 4%). In the busy
     world it keeps 4% to 10% too many, and at blocks of 32, where the plain rule had
     them right, that is a loss.
   - **It wavers as the world does.** In the real world a sixth to a quarter of all
     changes of hands are a block going back to the leader it had two ticks before (0.26,
     0.25, 0.21 at blocks of 8, 16, 32 in the still world; 0.27, 0.24, 0.17 in the busy
     one). In the plain rule's world it is 0.11, 0.07 and 0.05 in the still world and 0.12,
     0.08 and 0.05 in the busy one. In the remembering rule's: 0.27, 0.26, 0.23 and 0.28,
     0.27, 0.21.
5. **And by the ladder's own test it is nearly the same rule at every rung.** The rule
   from the rung below run on as the rule of the rung above: its blocks amiss over those of
   the rung's own rule (and the least and the most of one start):

   | | at blocks of 8 | 16 | 32 |
   | --- | --- | --- | --- |
   | still: the rule as it is | 1.20 (1.20 to 1.21) | 1.15 (1.13 to 1.17) | 1.12 (1.08 to 1.15) |
   | still: with its leader one tick before | 1.20 (1.19 to 1.20) | 1.11 (1.10 to 1.13) | 1.06 (1.01 to 1.10) |
   | still: with how long, up to 8 ticks | 1.14 (1.12 to 1.14) | 1.03 (1.02 to 1.04) | 0.99 (0.96 to 1.04) |
   | busy: the rule as it is | 1.09 (1.08 to 1.09) | 1.13 (1.12 to 1.14) | 1.10 (1.06 to 1.15) |
   | busy: with its leader one tick before | 1.09 (1.07 to 1.10) | 1.05 (1.03 to 1.08) | 1.01 (0.98 to 1.06) |
   | busy: with how long, up to 8 ticks | 1.03 (1.02 to 1.04) | 0.98 (0.97 to 0.99) | 0.97 (0.92 to 1.04) |

   The plain rule from the rung below pays 9% to 20%. With how long in view it pays 14%
   and 3% at blocks of 8, and within 3% of nothing at blocks of 16 and 32 in both worlds.
   That is the plan's last move, "repeat with the coarse rule as the new fine rule", coming
   out even: the rule of blocks of 16 is as good a rule for blocks of 32 as their own. And
   the remembering rule from the rung below runs a rung on better than that rung's own
   plain rule (in the busy world at blocks of 32, as well as). It does so although it
   still changes hands a third more often than the rung's own at blocks of 32, and two
   fifths more often at 16 (item 2). What the rule from below has too much of is wavering
   along walls, and a rule that remembers takes most of a waver back at the next tick,
   where the plain rule leaves it standing as a dent in the wall.
6. **The two worlds are a little further apart with a past in view, and each still runs
   the other.** One tick ahead, the other world's rule has 0.4%, 0.3% to 0.4% and 0.2% to
   0.3% more surprise than a world's own at blocks of 8, 16 and 32 as it is, which is what
   steps 4d and 4g found; with how long in view (up to 4 ticks) 0.7% to 0.8% at blocks of
   8 and 0.5% to 0.8% at 16. Run on, the busy world's remembering rule ends the still world
   with 0.96 to 0.98 of the blocks its own gets amiss, and the still world's ends the busy
   one with 1.04 to 1.06.
7. **The bottom rung has ties.** At blocks of 4, three in ten of all changes of hands in
   the still world leave the block with no leader, the two species having as many cells;
   at blocks of 8, 16 and 32 it is 9%, 3% and 1% (the busy world: 37%, 13%, 4%, 1%). That
   is part of why the first step up the ladder has always been the largest.

`pictures.py` draws item 2 as a page of charts (the chance against how long a block has had
its leader, a line for each rung; `~/lattice-lab-runs/memory/pictures/index.html`): at five
rival neighbours the four lines lie on one another, at three they stand a factor of two
apart.

**What step 4h shows.** The coarse rule of these worlds has a memory, though the worlds
have none. What a cell does next depends on the grid now and on nothing before it. But who
leads a block does not say where the wall inside it is, and the block's past does. A rule
that keeps that in view runs the world on better at blocks of 8 and 16, no longer loses
walls, and passes the ladder's own test at blocks of 16 and 32 with nothing to pay. It does not
make the table the same at every rung one tick ahead. The table settles from the top: where
a block is all but surrounded, its chance is already the same at every rung once its past
is in view, and what step 4g read there as the rule changing was the mix of young and old
leads. Along a wall it is not the same at any age of the lead, and goes on falling by
about half for each doubling of the block.

**What it does not show.** Nothing here is registered. I chose the readings after seeing
the first numbers and tried half a dozen (one I dropped: who led the block two ticks
before, which how long does better with less to learn), and I tell the best of them: that
flatters. The runs are step 4g's, which I had read; two worlds, both inside the class of
step 4f. One-tick comparisons at blocks of 32 cannot be made for a rule with much in view
(item 3), and the correction for endless data is rough. The look checks it with a rule
that learned from one start: at blocks of 16 and 32 a rule sheds 1.3 to 1.8 times as much
surprise going from one start to two as from two to four, where the law the correction
rests on says twice (in one case of the sixteen, 2.25). So what a rule lacks falls more
slowly than the correction supposes, and the figures of item 3 still flatter the rule from
below at the top. The run-ons rest on four trial starts a world. In the busy world at
blocks of 32 the remembering rule is no better than the plain one and keeps a tenth too
many walls. Why a block along a wall changes hands half as often at twice the size is not
tested. The reading I would test is that a wall wavers by a width of its own, which is a
smaller share of a larger block; step 4g's sums (each step three tenths shorter) fit that.
And one kind of reading was tried, a block's own past: not its neighbours' pasts, nor where
the neighbours are, which step 4d found adds little to how many.

**Gate:** none, as nothing was registered. What it gives is decision D13.

### Step 4i: the rule that remembers, registered (registered 2026-11-27)

Step 4h was read off runs I had seen, with the readings chosen after the first numbers. You
chose to put it on the record (decision D13, option a):
`examples/scale-up-memory/study.py`, registered on 2026-11-27 with 74 predictions before any
of its runs was made.

- **What is run.** The still world and the busy world, each against its copy under the
  standoff from a full start, on a wrapped grid of side 1,024 for 4,096 generations, from
  sixteen fresh starts each (19001 on): eight to learn from and eight to try on. Blocks of
  4, 8 and 16, each at its matched age on the square clock. That is step 4e's size, and
  blocks of 32, where the look's last word came from, are out of its reach. 32 fine runs and
  160 rules run on, sixteen times each.
- **Sixteen starts a world, where I had told you eight.** At this size blocks of 16 are
  4,096 to a start, as blocks of 32 were in step 4g, and in the sizing the walls a rule
  keeps at blocks of 16 moved by 0.04 between one choice of four trial starts and another.
  Eight trial starts steady that. It costs nothing but two more hours of this machine.
- **Two rules.** As it is; and with how long a block has had its leader in view, up to 8
  ticks, which was the look's best reading and is the only one registered.
- **The look's own rules** (`reference.json`): the tables the look learned on side 2,048,
  written down before the run and tried here unchanged, one tick ahead and run on.
- **Sizing** (`sizing.py`, exploratory; it ran no world). Step 4d kept the leaders of its
  sixteen runs at this very size (starts 15001 to 15008), which the look never used. Put
  through the study's own measures, with four starts to learn from and four to try on, both
  ways round, they give the look's numbers again: a young lead changes hands 6.2 to 8.1
  times as often as an old one at four rival neighbours; an old lead at five is 0.93 and
  0.97 as likely to change hands at blocks of 16 as at 8, where the plain rule gives 0.84
  and 0.87; run on, the remembering rule ends with 0.72 to 0.78 of the plain rule's blocks
  amiss at blocks of 8 and 0.82 to 0.91 at 16; and the remembering rule from blocks of 8
  runs blocks of 16 at 0.97 to 1.02 of their own, where the plain rule from below pays 14%
  to 19% more. All 74 claims would hold on those runs, both ways round. So the look has
  already been repeated once, on runs I had seen; the registered run asks it of fresh ones.

**The predictions**, 74 in seven families (each for both worlds).

| Family | What is predicted | Bound |
| --- | --- | --- |
| A, a block's past (10) | with four rival neighbours, a block that has had its leader one tick changes hands this many times as often as one that has had it 16 or more, at blocks of 8 and 16 | at least 4 |
| | how long removes this share of the plain rule's surprise, at blocks of 4, 8 and 16 | at least 4% |
| B, the top of the table (6) | an old lead at five rival neighbours is as likely to change hands at blocks of 16 as at 8 | within 10% |
| | while the rule as it is falls | to 0.93 or less |
| | and the plain rule at blocks of 8, made from its own mix of young and old leads and the chances of blocks of 16, is what it is | within 5% |
| C, along the walls (12) | at three rival neighbours the chance falls from blocks of 8 to 16: an old lead; a lead of one tick | to 0.6 or less; 0.9 or less |
| | an old lead at four falls | to 0.92 or less |
| | of the plain rule's fall at three, the share that is the mix | at most 30% |
| | one tick ahead the remembering rule from blocks of 4 has more surprise at blocks of 8 than the one learned there; and beside the plain rule's gap | at least 4%; at least 0.6 of it |
| D, run on (20) | blocks amiss, the remembering rule over the plain one, at blocks of 8; 16 | at most 0.90; 0.96 |
| | the walls the plain rule keeps, at blocks of 8; 16 | at most 0.95; 0.98 |
| | the walls the remembering rule keeps | 0.95 to 1.14 |
| | going back, the remembering rule's world beside the real one; the plain rule's over the real one | within 0.06; at most 0.6 |
| E, the ladder's own test (10) | blocks amiss, the remembering rule from the rung below over the rung's own, at blocks of 8; 16 | at most 1.22; 1.10 |
| | the plain rule from below pays more than that by | at least 0.02; 0.04 |
| | the remembering rule from blocks of 8, run on at 16, over the rung's own plain rule | at most 0.97 |
| R, the look's rules (12) | the look's rule of side 2,048, as it is and with how long, one tick ahead at blocks of 8 and 16 | at most 0.5% more surprise |
| | and run on, blocks amiss over those of the rule learned here | 0.93 to 1.07 |
| X, the anchor (4) | the plain gap at blocks of 16; the plain rule's own run-on there | 1.5% to 4.5%; at most 0.70 |

- **Not tested**, fixed beforehand: a claim about a chance where fewer than 200 blocks
  stand behind a chance it compares; a run-on through blocks too large for the world's
  territories when it starts (over a fifth of neighbouring blocks under different leaders),
  as in steps 4e and 4g.
- **What I expect, written before the run.** Nearly all of it to hold: two sets of seen
  runs on two grids agree, and the bounds stand clear of where they put each number. If
  something fails I expect it to be one of four, by a little. The
  still world's old leads at five rival neighbours do fall a little from blocks of 8 to 16
  (0.93 and 0.96 in the two sets), and "within 10%" could be missed. The walls at blocks of
  16 are the noisiest thing here. The busy world gains least from remembering at blocks of
  16 (0.89 to 0.91 of the plain rule's blocks amiss, against a bound of 0.96). And its
  remembering rule goes back a little more often than the world does (by 0.02 to 0.03,
  against 0.06). A failure of family E or R would be news: it would mean the ladder's own
  test coming out even was a property of the runs I had seen.

**Gate:** the verdict, whichever way it goes.

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
| step 4d, the first look, 16 runs read through blocks | 1.0 million | 4,096 | 1 hour 22 minutes for the runs, and 25 minutes for their analysis | here, two cores |
| step 4e, the sizing look: the first look's runs through the study's measures eight ways, and two control runs | up to 1.0 million | 4,096 | 21 minutes of one core, spread over 75 while two other jobs had the machine | here, one core |
| step 4e, the registered test, 44 runs read through blocks and 108 run-ons | 1.0 million | 4,096 | 51 minutes on 22 workers of a pod with 32 vCPUs, $0.96; a run takes 16 minutes there beside 21 others, the sparse world's 30 | a pod |
| step 4e, the extras: four runs again for their leaders | 1.0 million | 4,096 | 15 minutes | here, two cores |
| step 4f, the class test, 160 runs read through blocks and 456 run-ons | 1.0 million | 4,096 | 81 minutes on 30 workers of a pod with 32 vCPUs and 128 GB, $1.99; a run takes 8 to 19 minutes there | a pod |
| step 4f, getting that pod: one that landed on a small host, deleted after 54 minutes, and five refused within minutes | | | $1.02 and $0.21 | pods |
| step 4g, the next rung, 16 runs read through blocks and 48 run-ons | 4.2 million | 16,384 | 3 hours 35 minutes on 16 workers of a pod with 32 vCPUs, $4.01; a run takes 2 hours 45 minutes to 3 hours 25 minutes there beside fifteen others, and 1 hour 39 minutes of one core here | a pod |
| step 4h, the look: step 4g's block leaders read again, and 4,608 run-ons of coarse rules | | | 5 minutes; and 1 hour 38 minutes to make again the leaders of the one run that had not come home | here, one core |

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

**One pod type, hosts of very different sizes** (2026-11-26). The pod type used until now
(compute-optimised, 32 vCPUs) is served both by a 64-core host and by a 16-core one, and the
launcher's speed check, which times one idle loop, cannot tell them apart. Step 4e's run
got the large host and took 16 minutes a run. Step 4f's first pod got the small one, where
30 runs side by side took 45 minutes each: it could not have finished inside its four
hours, and you had it replaced. Five more pods of that type landed on small or overloaded
hosts and were refused in turn, by a check added for the purpose
(`examples/scale-up-sizes-large/pod/launch2.sh`: the host's cores to a socket, before
anything is run). A type with twice the memory, which the small hosts cannot hold, got the
large host at the first try, at $1.47 an hour against $1.12. My estimates were also wrong by
themselves: I guessed a run's cost on a busy pod where step 4e's own log would have told me
(224 ns a cell there, 276 for the busy world). The next rung's pod, of the first type, got
the large host and ran sixteen runs side by side in the three and a half hours first
quoted; a timing I took while it ran said five, and was wrong the other way.

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
  held. You then chose (b): it is step 4d, the first look, done on 2026-11-25. What it
  leaves is decision D10.
- **D10. What to put on the record from the first look up the ladder** (2026-11-25). Step
  4d is a look: I read its numbers before saying what they showed. Three ways on, cheapest
  first:
  (a) a registered test at the look's own size (side 1,024 to generation 4,096), on fresh
  starts, of the four things it saw: run on by itself the rule keeps the real world's walls
  and most of its leaders; it is the same rule early and late at small blocks; the gap
  between rungs is smaller on the square clock than on the block clock; and each world's
  rule serves in the other. With them, three worlds that have never been zoomed out, to ask
  whether a rule learned in the still world serves there as well. That is the claim most
  likely to fail and the one that would mean most: it may hold only up to the pace of each
  world's walls, and the test should be able to tell that from not holding at all. About
  four hours here;
  (b) another rung: side 2,048 to generation 16,384, so that blocks of 32 are read at
  matched ages with as many blocks as blocks of 16 have here. That is what says whether the
  square clock leads to a rule that stops changing. About 45 core-hours: a pod for $3 to
  $5, to be agreed before any launch, or a day and more here;
  (c) leave the ladder here and take up D8's other two.
  I recommend (a), and then (b) if (a) holds. (a) is cheap and puts at risk the two
  findings I did not expect, that the rule knows where the territories will be and that two
  worlds share it. (b) costs money and is worth it only if the rule it would extend is
  real.
  You chose (a): it is step 4e, registered and run on 2026-11-26, and 73 of its 89
  predictions held. When the run was due two other jobs had this machine's spare cores,
  and asked where it should go you chose a pod: $0.96 of the $3.36 agreed.
- **D11. Where next, now that the rule is on the record** (2026-11-26). Step 4e leaves two
  open ends, and either can be taken up first.
  (a) **How wide is the class?** One stranger follows the still world's rule at half the
  pace, and its pace read off its walls says the same half. That is one world. A registered
  test over many (the rules of step 4c that hold territories and whose grounds fill, twenty
  or so) would say whether "one rule and a pace" is a law of these worlds or a pair of
  coincidences, with a prediction that can fail for each: the pace its walls give is the
  tick at which the still world's rule serves. About 160 runs: a pod for about $3, to be
  agreed before any launch.
  (b) **Does the ladder come to a fixed point?** Another rung: side 2,048 to generation
  16,384, so that blocks of 32 are read at matched ages. Each such run is sixteen of this
  step's, so sixteen of them are about 70 pod-hours of work: a pod for $5 to $6.
  (c) The sparse world: a reading that suits a world with a quarter of its cells live,
  to see whether it has a coarse rule of its own. No runs to speak of, and no promise.
  (d) Leave the ladder here and take up D8's other two.
  I recommend (a), then (b). (a) is the cheaper, and it is the finding of this step that
  rests on least: four worlds. If it holds over twenty, the ladder has found what it was
  built to find, a law of the large scale that many fine rules share, and (b) then asks
  whether that law is also the same at every scale.
  You chose (a) and then (b). (a) is step 4f, registered and run on 2026-11-26: 54 of its
  128 predictions held, and the claim it was built to test (a world's clock says whether
  the rule serves it) failed for 20 worlds. (b) is step 4g, registered and run the same
  day: all 22 predictions held, and the rule has not stopped changing. The pods cost $3.22
  for (a), across the three launches you agreed, and $4.01 of the $6.72 agreed for (b).
- **D12. Where next, now that one more rung is read** (2026-11-26). Step 4g answers (b) as
  far as one rung can. The ladder's own move works, and the rule changes less at each
  rung; but it is still changing, the same way each time, and what changes is how often a
  block on a wall changes hands. Four ways on, cheapest first:
  (a) **Look for a reading whose rule does stop changing.** If much of what a block on a
  wall does is the wall wavering back and forth across the block's middle, then a symbol
  that also carries who led the block one tick before would hold that, and the rest of the
  table may already be the same at every rung. A first number says the symbol does leave
  that out (`examples/scale-up-rung/back.py`, exploratory, from the kept leaders of the
  trial starts): at every rung 18% to 29% of the blocks that go over to the rival had come
  from it one tick before, and with four rival neighbours a block that has just come over
  goes back with chance 0.25 to 0.32 where one that has held goes over with 0.04 to 0.09.
  Among blocks that have held, the chance at five and at six rival neighbours is the same at
  every rung to within a sixth, where the table as it is falls by three to four tenths at
  five. At three and four it still falls with the rung, so a block's past is not the whole
  of it. The leaders of fifteen of this step's sixteen runs are kept here at all four rungs,
  so the look is a re-reading: no runs, a few hours of one core, registering nothing. If it
  finds a rule that holds from rung to rung, a registered test of it on fresh starts
  follows, at step 4e's size (about $1 on a pod, to be agreed first).
  (b) **Put on the record how the rule changes with the rung.** What the extras read off
  was read after the verdict. A registered test on fresh starts, and on the ten worlds of
  step 4f that the rule serves, of three things: the gap sits at blocks with three or four
  rival neighbours, their chances fall by a fixed share a rung, and the steps add as
  distances. Side 1,024 to generation 4,096, so three rungs: about 100 runs of 16 minutes, a
  pod for about $2, to be agreed before any launch.
  (c) **Climb one more rung:** side 4,096 to generation 65,536, blocks of 64. Sixteen times
  this step: about 800 core-hours, $60 or so on pods over a day or two. By the pattern it
  would show the gap halved once more, to about 0.7%, and not a rule that has stopped.
  (d) **Leave the ladder here:** bring the ten branches home, and take up D8's other two
  (richer symbols for the pair; step 5, the reversible variants).
  I recommend (a). It costs nothing, it goes at exactly what this rung found still moving,
  the first number says there is something to find, and it is the one way on that could
  show a rule that stops changing at sizes within reach, where climbing can only show a
  slower approach to one. I do not recommend (c).
  You chose (a): it is step 4h, a look, done on 2026-11-27. It found the reading in part.
  Run on, the rule that remembers is the same rule at blocks of 16 and 32; one tick ahead
  it is not.
- **D13. What to do with a rule that remembers** (2026-11-27). Step 4h is a look, read off
  runs I had seen. It says a block's past belongs in the symbol: with it the rule runs the
  world on better, and by the ladder's own test it is the same rule at blocks of 16 and 32.
  It also says where the table still changes one tick ahead, along the walls, and that the
  rest of what step 4g saw changing was a mix. Four ways on, cheapest first:
  (a) **Put the look on the record at step 4e's size.** A registered test on fresh starts
  of the two worlds, side 1,024 to generation 4,096, so blocks of 4, 8 and 16 at their
  matched ages. Its claims would be the look's, where that size reaches: that the rule
  which knows how long runs the world on with fewer blocks amiss and keeps the walls; that
  it goes back as often as the world does; that the rule from blocks of 8 then runs blocks
  of 16 within a few percent of their own; that for an old lead the chance at five rival
  neighbours is the same at blocks of 8 and 16 and the plain rule's fall there is the mix;
  and that at three it still falls by half. Sixteen runs of ten minutes: under three hours
  of one core here, or a pod for about $1.
  (b) **The same with blocks of 32,** which is where the ladder's own test came out even:
  side 2,048 to generation 16,384 again, sixteen fresh runs, a pod for about $4, to be
  agreed before any launch.
  (c) **The class again, with the rule that remembers.** Step 4f found the still world's
  plain rule serving ten of 29 worlds and, run on at a world's own pace, carrying nineteen.
  Whether a rule that takes back a waver carries more of them is a registered test over
  those worlds: 152 runs, a pod for about $2, to be agreed before any launch.
  (d) **Leave the ladder here,** bring the ten branches home, and take up D8's other two.
  Step 5's reversible rules are rules with one tick of memory by construction; this look
  says the zoomed-out world wants one whether its cells have it or not.
  I recommend (a). It costs nothing but an afternoon of one core, it tests on fresh starts
  what I have only read off runs I had seen, and (b) and (c) are worth their price only if
  it holds.
  You chose (a): it is step 4i, registered on 2026-11-27 with 74 predictions, from sixteen
  starts a world where I had said eight (step 4i says why).
- **D4. When to move the instrument into LatticeLife.** Done: step 1.
- **D5. The pod.** Done. You chose the pod over this machine; it cost $2.57 of the $6.72
  agreed.
- **D7. The remainder at side 2048.** Done (step 3b). You chose to close it before step 4;
  the registered test held on all nine predictions, and the pod cost $2.49 of the $6.72
  agreed.
- **D6. The branches.** Ten, none merged and none with a pull request yet (the tenth now
  holds six steps):
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
    predictions to the census dashboards' table;
  - lattice-lab `scale-up-step-4d`, on top of `scale-up-search`: the first look at worlds
    of territories zoomed out (step 4d), which registers nothing; its registered test
    (step 4e, 89 predictions); the class test (step 4f, 128); the next rung (step 4g, 22);
    the look at a rule that remembers (step 4h), which registers nothing; and its
    registered test (step 4i, 74). Four studies and 313 predictions more in the census
    dashboards' table.

  Like the unmerged `ccr-effac3f1-udftpr` (the qec-parents study), these branches add their
  studies to the census dashboards' table, so they meet it on one line: the count of studies
  and predictions in `tests/test_census_dashboards.py`. With everything merged that line is 46
  studies and 2,140 predictions.
