# Scaling up: a ladder from a rule to its large-scale law (plan)

**Status:** a plan, written 2026-11-23. **Its first step passed the same day: the instrument is
calibrated** (`examples/scale-up-linear`, 296 of 296 registered cases held). Nothing else in it
is built. The decisions that are yours are at the end.

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
| zooming out | `scaleup.py` here: square and hexagon, a sampled cell or a block's parity. LatticeLife's `local.py` has a b x b block test in row and column indices | counts per species, the leading species, the triangle, a home in LatticeLife |
| the closure test | `scaleup.closure`: two deterministic routes, compared exactly | cells with more than two states; coarse rules that are probabilistic |
| competing species without the app | nothing. Every headless experiment runs one species (`torus_config` sets `n_lifeforms = 1`), and a session seeds species by mixing them uniformly | sessions with chosen shares and layouts, and their records |
| a start of your choosing | experiments start from a density and a seed only | explicit starts: shares, half and half, stripes |
| domains and fronts | cluster counts, damage spreading | interface density, domain size, front speed, time until one species is left |
| large grids | one update rule, about 55 ns per cell per generation for one species, 93 for two and 125 for three (measured at 512 x 512). Adjacency is built by Python loops | a vectorised adjacency above about 2000 x 2000; nothing else up to 4096 x 4096 |
| reversible rules | nothing; the engine keeps one generation | a second-order wrapper (step 5) |
| growth laws | Kepler: `power`, `logarithmic`, the relaxation laws, `fit_replicates` | nothing |
| a win probability against a starting share | Kepler: `logistic_p` with a binomial likelihood | nothing |
| the same law across rules or lattices | Kepler: `fit_groups`, `compare_sharing` | nothing |
| conserved quantities | Kepler: `find_invariants` | wiring it to second-order runs |
| a probabilistic coarse rule | nothing: Kepler fits closed-form laws, not transition tables | decision D3 |
| registered tests | `lattice_lab.study` | `verify` cannot rerun a study's records |

Two things turned up that you should know about:

- **The competitive world is not a function of the grid alone.** With one species the update is
  deterministic. With two or more, a dead cell that two species could both be born into goes to
  one of them by a random draw (`core/lattice.py`, the birth step). A run is reproducible from
  its seed, but the next grid depends on the random stream as well as the present grid. That
  matters for anything said about determinism or reversibility of that world, and it is
  decision D1.
- **The local checkouts are behind the pins.** `~/Documents/dev/latticelife` is at `15aa710`,
  seven commits before the pinned `256450b`, and has none of `observables.py`, `local.py`,
  `damage.py`, `series.py` or `cost.py`. `~/Documents/dev/kepler` still points at the old
  `tripptytrip` remote and has no `src/kepler` at all. Any build starts by fetching.

## Build changes, in order

Each step ends in a gate. A step is not started until the gate before it has passed.

### Step 1: give the instrument a home in LatticeLife

- **Where:** a new `latticelife/experiments/coarse.py`, from `scaleup.py`, on a branch from
  `256450b`.
- **What:** the block geometry (`coarse_side`, `sample_cells`, `block_cells`), the projections,
  and the closure test with JSONL records in the house form. Add two projections for species:
  the count of each species in a block, and the leading species with a stated tie rule.
- **Also:** a vectorised wrapped adjacency with a `dilation` argument, replacing the Python
  loops. `dilated_adjacency` here is that code, and at dilation 1 it is LatticeLife's array.
- **Stable interface:** new names and new fields only, added to `test_stable_api.py`.
- **In lattice-lab:** move the pin, and give `Study` an optional rerun hook so that
  `lattice-lab verify` can rerun study records. The calibration's records carry the hash of the
  fine grid they ended on, so they can be checked byte for byte.
- **Gate:** the calibration's 296 cases rerun through the LatticeLife module give the same
  records as `examples/scale-up-linear/records.jsonl`.

### Step 2: the competitive world without the app, and a first look

- **Where:** LatticeLife `experiments/`: a multi-species session builder (rules, starting
  shares, layout, seed), its records, and the observables: each species' share per block,
  interface density, domain size, front position, and the generation at which one species is
  left.
- **Study:** `examples/scale-up-compete` in lattice-lab, **exploratory**, on tori up to 256:
  how domain size grows with time, how a front between two species moves, and how the chance of
  winning depends on the starting share. Kepler fits each (`power` against `logarithmic`,
  `logistic_p` with a binomial likelihood).
- **A known answer inside it:** two species with the same rule are interchangeable, so at equal
  shares each must win half the time, and the front between them must not drift. That is this
  step's calibration.
- **Gate:** laws with error bars at four or more sizes, and the symmetric contest fair within
  its binomial interval.

### Step 3: the registered scale-up test

- **What:** the laws fitted up to 256 predict the same quantities at 1024, 2048 and 4096. The
  predictions are registered with their bands and then run.
- **Where it runs:** 1024 here on one or two cores; 2048 and 4096 on a RunPod CPU pod
  (`docs/runpod-setup.md`), because of this machine's heat limit.
- **Gate:** the verdict, whichever way it goes. A failure says where the small grids stop being
  a guide, which is the horizon the ladder is for.

### Step 4: closure for the competitive world

- **What:** propose coarse rules on the leading species of each block and measure the closure
  error against block size and time. The honest baseline is a coarse rule that knows nothing,
  so the score is closure error against that.
- **Needs:** the closure test for many-state cells, and a comparison in distribution for coarse
  rules that are probabilistic (D3).
- **Gate:** a registered test of the best coarse rule at a block size and a torus it was not
  fitted on.

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

At the measured 55, 93 and 125 ns per cell per generation for one, two and three species. The
4,096 generations are a placeholder: step 2 will say how long a run needs to be.

| Run | Cells | Generations | One run | Where |
| --- | --- | --- | --- | --- |
| step 0, all 296 cases | up to 590,000 | up to 256 | 3.5 minutes in total (measured) | here, one core |
| step 2, two species at 256 | 65,536 | 4,096 | 25 seconds | here |
| step 3, two species at 1024 | 1.0 million | 4,096 | 7 minutes | here, one or two cores |
| step 3, two species at 4096 | 16.8 million | 4,096 | 1.8 hours, an estimated 2 GB | a pod, one run per core |

Sixteen starts at 4096 are about 28 core-hours. No step needs a faster engine. If one is wanted
later it must reproduce the one update rule cell for cell, with a test that says so.

## What is not planned

- A GPU or compiled engine.
- Discovering spatial laws (differential equations) in Kepler. Step 2's laws are curves against
  time, size or share, which Kepler fits today.
- The triangle lattice, beyond the small study named above.
- Any claim about the Planck scale or about physics.

## Decisions for you

- **D1. The tie-break.** Keep the random draw, or add a rule that is a function of the grid
  alone (for example: a contested cell stays empty)? I recommend running step 2 on the world as
  it is, then adding the deterministic rule as a second world. Whether the tie-break changes the
  large-scale laws is then the ladder's first question about classes. Step 5 needs the
  deterministic rule for more than one species.
- **D2. Which contest first.** I recommend Life against Life (the symmetric control), then Life
  against HighLife, the pair in LatticeLife's README.
- **D3. Where a probabilistic coarse rule lives.** I recommend a plain table of transition
  frequencies in lattice-lab first, and a Kepler extension only if a closed form shows up.
- **D4. When to move the instrument into LatticeLife.** Step 0's verdict is in, so step 1 can
  start when you say.
- **D5. The pod.** Step 3's two larger sizes need a RunPod launch, which I will cost and ask
  about before starting.
- **D6. This branch.** `scale-up-linear` holds the study, its tests and this plan. Like the
  unmerged `ccr-effac3f1-udftpr` (the qec-parents study), it adds its study to the census
  dashboards' table, so the two meet on one line: the count of studies and predictions in
  `tests/test_census_dashboards.py`. Whichever is merged second needs that line set to 36
  studies and 1,624 predictions.
