# Census stage 4b: probabilistic distances by ISD (prep, not registered)

**Status:** the instrument, a first model check, and the cost comparison. Nothing is registered,
and nothing has run on a stage 4 torus. Whether 4b is worth running depends on stage 4's records:
how many classes it leaves unsettled, and at which d.

## The idea

Stage 4's exact engine (DistQLDPC's cluster search) costs about 8 times more for each +2 in d.
That is 4 minutes at d = 24, an extrapolated 4.5 hours at d = 28, and 1.5 days at d = 30. So at
n = 350 to 400 some classes will not settle within the 4-hour limit.

Information-set decoding cannot prove that no light logical exists. It can bound the chance of
missing one: if a fixed codeword is seen with probability at least p per iteration, N iterations
miss it with probability at most exp(-N p). The result would be a separate tier, "probable d,
miss probability <= eps", and never mixed with exact results.

## The instrument (built)

**`isd.c`** is window.c with three changes:
- it checks every sum of two rows as well as every row (Lee-Brickell, p = 2);
- it runs a fixed number of iterations, so the outcome is the same on any machine;
- it counts the iterations that see a codeword of weight <= target;
- with `watch`, it counts how often a given codeword meets the information set in 1 or 2
  positions.

**`isd.py`** has:
- the model p_seen(n, K, w): the probability for a uniformly random K-subset;
- `budget`, the N for a given eps;
- `certify`, the probabilistic claim;
- `calibrate`, the measured rate against the model.

## The finding: the model is optimistic

isd.c's information set is not a uniform K-subset. It is the greedy basis of a random column
order. Measured on the spot-check's codes with known witnesses (calibration/):

| n | codes | measured / model |
|---|---|---|
| 72 ([[72,12,6]]) | 1 | 0.98 |
| 112 to 144 | 8 | 0.70 to 0.87, each from 430 to 1,500 hits |
| 192 to 294 | 11 | 0.24 to 1.7, from only 1 to 47 hits (too few to tell) |
| 240 to 300 | 9 | no hits at all in 60,000 iterations (p too small to measure) |

So per codeword, the greedy information set sees a minimum-weight logical about 20 to 30% less
often than the uniform model says, wherever this can be measured. Any registered use needs a
correction factor c < 1, measured with a margin at the sizes it is used at. That measurement
needs about 10^7 to 10^8 iterations per code at n = 300, d = 24: hours per code, or one pod-day
for a dozen codes.

## The cost, against the exact engine

Single-core hours, eps = 10^-6. ISD runs at about 3,750 iterations per second at n = 300 with
pair sums; n = 400 is assumed n^3-slower.

| claim at n = 400 | exact (DistQLDPC) | ISD, model as is | ISD, c = 0.35 |
|---|---|---|---|
| d = 26 | ~0.6 h | 0.3 h | 0.8 h |
| d = 28 | ~4.5 h | 1.1 h | 3.1 h |
| d = 30 | ~36 h | 4.4 h | 12.5 h |

With an honest margin, ISD with Lee-Brickell is about 1.5 times faster at d = 28 and 3 times at
d = 30, at the price of turning exact results into heuristic probabilities.

## Options, if stage 4 leaves enough unsettled to matter

1. **Run 4b as above,** only for d >= 30 classes, after a calibration run at n ~ 300 that fixes
   c with a margin. It is modest but simple.
2. **Stern / Dumer splitting** (collision search over the information set, p up to 4). Typical
   gains over Lee-Brickell are 10 to 100 times at these sizes. It needs a new C program and the
   same calibration.
3. **More exact time instead:** a stage 4c that reruns only the unsettled classes with a longer
   DistQLDPC limit (24 to 48 h each) across several pods. That keeps every result exact.

The cost profile from stage 4's own records will decide between these.
