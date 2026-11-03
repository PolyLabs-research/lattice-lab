# Why the census scatter looks regular (exploratory, not registered)

**Question (2026-11-02).** The d-vs-n scatter of the census frontier looks more uniform than
expected. Is there a function that explains its regularity?

**Method.** A workflow with four independent analyses: the envelope function, the rate-distance
trade-off, theory and literature, and the discrete structure. Every key claim (16 in all) went
to a skeptic who tried to refute it by recomputing from the data or checking the source. Claims
that failed were dropped or corrected. The data are the census entries of stages 3a to 4 as of
2026-11-02 (stage 4 about 75% done; `examples/qec-census-4/explorer/build_data.py`).

- **The scripts** are in `scripts/`. The raw workflow result, with every claim and verdict, is
  in `workflow-result.json`.
- **The paths in the scripts** point at the session scratchpad where they ran. The data file
  there is the output of `build_data.py`.
- **The literature** was checked through search summaries only, because arxiv.org was blocked.

## Answer

Most of the regularity comes from arithmetic, not from a smooth law. The top edge does follow a simple curve, d_max ≈ 0.617·√(n ln n), but the data cannot pick that curve over several others, and no theorem selects it.

Three sources of regularity have nothing to do with a function. First, d is always even (proved), so the 533 entries use only 14 heights and land on just 221 distinct (n, d) points. Second, for lm ≤ 200 criterion E reduces to "lm divisible by 3, 7, 31, 73 or 85". Codes therefore exist at only 89 of the 153 possible n, and 65 of those are every multiple of 6 from 12 to 396, so the x-axis is close to an evenly spaced comb. Third, 209 of the 533 entries (39%) come from isomorphic tori and sit exactly on top of other points.

The top of every column is the smallest k its group allows (141 of 141 groups): k = 4 when 3 divides n/2, 6 when only 7 does, and 10, 16 or 18 for 31, 85 or 73. So the upper edge is one k = 4 staircase on the multiples of 6. It rises by 2 at each new even level and dips once, at n = 312. The other columns sit 0 to 16 below it.

Below the edge the k layers run roughly parallel. At fixed n, each extra logical qubit costs about one unit of distance: the median slope within a group is 0.91, drifting from about 0.7 at n ≤ 150 to about 1.25 above n = 300. Fitted only on n ≤ 300, d ≈ 2.31·n^0.443 − k predicts the 49 stage-4 frontier points with RMS 2.0 to 2.1, with 92 to 94% within one even step. The k·d² ≈ constant shape does much worse (RMS 3.7). The apparent ceiling of about 14 to 16 on k·d²/n is not real. The best score for each k still rises from band to band (k = 10 goes 4.3 → 15.6). The published [[360,12,24]] sits on Z6×Z30, which stage 4 has not computed yet, so the (360, 12) entry must rise to d ≥ 24, a score of 19.2.

On the top edge, d/√n at each new record rises at every step, from 1.155 at [[48,4,8]] to 1.488 at [[354,4,28]], so a constant ratio is ruled out. The tightest constant line, 1.46·√n (through [[270,4,24]]), falls about 0.6 short at the d = 26 and d = 28 steps. √n·ln n and a straight line overshoot.

The best simple description is d_max ≈ 0.617·√(n ln n), rounded down to even. But over n ≤ 400 it stays within 0.35 in d of 0.83·n^0.60 and 0.78·n^0.613. The form 1.75·√n − 4.6, in which d/√n levels off near 1.75, fits as well once the small-n steps are dropped. It is clearly worse only when they are kept (ΔAICc ≈ 12 from n ≥ 30). So the data say only that the edge grows faster than √n here, with a local exponent of about 0.6.

Out of sample, 0.615·√(n ln n) fitted on n ≤ 300 gets the record value right at 13 of the 14 stage-4 n where a record is set (14 of all 20 stage-4 n). Because d is even, that is really only two events. It placed d = 28 at n ≈ 353 (first seen at 354) and missed d = 26 (predicted at 311, seen at 306, the same point where the registered 0.801·n^0.607 failed by 0.1). One hit in two matches its in-sample rate (it misses 4 of its 10 training steps), and n^0.60 scores the same 13/14. The √(n ln n) form was also chosen after stage 4 was visible, so only its constant was really tested.

The edge is also a maximum over many code classes: only 1 to 5 classes hold each new record. The bulk of classes rises nearly as fast (mean, median and 90th percentile grow like n^0.68 to n^0.71 for n ≤ 198). But the best of a fixed-size sample grows like n^0.63, against n^0.67 for the real maximum. Classes per n grow about like n^2.7, and that alone is worth about one even step across the range. Any fitted curve absorbs this effect.

Theory does not fix the shape. The best proven upper bound for weight-6 BB codes, and for any abelian two-block code, is O(n^(3/4)), from a Bravyi–Terhal argument in 4 dimensions (Arnault, Gaborit, Rozendaal, Saussay, Zémor, arXiv:2502.04995; Postema & Kokkelmans, arXiv:2502.17052). Its explicit form, about 8.5·n^(3/4), holds only for n ≥ 16,384 and says nothing here. Caps of order √n are proven only for subfamilies that exclude the record codes: hypergraph products (Tillich–Zémor, arXiv:0903.0566) and codes whose A or B lies in a small subgroup (Lin–Pryadko, arXiv:2306.16400). Wang & Pryadko (arXiv:2203.17216) prove that codes with d of order √n exist at fixed weight, and found that A√n + B fits their k = 2 enumerations. So theory allows exponents from 1/2 to 3/4, and the observed ≈0.6 lies inside that window. Up to n = 384 the record codes can be drawn as 2D codes with small stencils (diameter ≤ 3, occasionally 4). So 2D bounds such as Bravyi–Poulin–Terhal's k·d² = O(n) apply, but their constants are unknown, so they do not predict the numbers. The literature was checked only through search summaries, because arxiv.org was blocked.

Several things are not established. The range stops at n = 384, and stage 4 is about 75% done: n = 360 and 384 are missing groups, and n = 390 to 396 have not run. The whole edge rests on about 12 step positions, each known only to within 6 in n, and one step of 2 is 7% of d at d = 28. The leading forms separate by one even step only at n ≈ 530 to 1500 (power law against the rest), n ≈ 1000 to 2000 (√(n ln n) against A√n + B), and n of order 10^4 (the log-corrected forms against each other).

## Formulas

**Top edge (record staircase; k = 4 codes on n divisible by 6):**
- d_max(n) ≈ 2·floor(0.617·√(n·ln n) / 2).
- c = 0.617 is fitted to all 12 record steps (d = 6 to 28, n ≤ 384). Fitting n ≤ 300 only gives 0.615. Single steps give values from 0.603 to 0.625, and no single c fits all of them.
- Over 30 ≤ n ≤ 400 these are equally good and within about 0.35 in d of each other: 0.78·n^0.613 (≈ 0.83·n^0.60), √n·(ln n)^0.55, and, if the fit starts at n ≳ 90, 1.75·√n − 4.6.
- Ruled out: c·√n (tightest constant 1.46, falls about 0.6 short by n = 306 to 354), c·√n·ln n, and a + b·n.
- Valid only for 30 ≤ n ≤ ~400 and only for the top edge. Columns where only 7 divides n/2 sit 0 to 2 lower; columns set by 31, 85 or 73 sit 4 to 16 lower.
- Do not extrapolate: at n = 10^4 the forms predict d/√n between 1.63 and 2.20.

**k layers below the edge:**
- d_best(n, k) ≈ 2.31·n^0.443 − k, fitted on n ≤ 300; 1.71·√n − k does about as well.
- Accuracy: about ±2 (one even step) for 92 to 94% of points, for k ≤ 16 and n ≤ 400.
- The cost per unit of k drifts from about 0.7 to about 1 as n grows.
- It fails for k ≥ 18, and for gross-type k = 12 codes (groups with two even sides and a Z3×Z3 part), which sit 1 to 2.5 steps above it.

**Arithmetic skeleton (exact, not a fit):**
- d is even.
- For lm ≤ 200, codes exist exactly when lm is divisible by 3, 7, 31, 73 or 85.
- The k at a column's top is 2·ord_t(2): 4, 6, 10, 16 or 18.

## A test that would separate the candidates

**Prediction to register before running (a targeted stage 5, not a full census).** Run k = 4 codes on the 3×m tori with m = 130 to 134, i.e. n = 780, 786, 792, 798, 804. These are all cyclic or near-cyclic groups with k = 4, the same family that holds every record so far. Record the best distance in that band. Fitted on all 12 record steps, the candidates predict:

| Model | Value at n = 804 | Predicted band maximum |
|---|---|---|
| Power law 0.78·n^0.613 | 46.9 | 46 |
| 0.617·√(n ln n) | 45.2 | 44 |
| A√n + B, 1.66√n − 3.3 | 43.8 | 42 |
| A√n + B, 1.75√n − 4.6 | 44.9 | 44 |
| Constant ratio c√n | 40.2 to 40.9 | 40 |

How to read the result:
- 46 or more favours the power law.
- 44 fits √(n ln n), or A√n + B fitted from n ≥ 100.
- 42 or less refutes both the power law and the √(n ln n) envelope, and favours d/√n levelling off.
- One-step misses happen (the √(n ln n) envelope misses 4 of its 10 in-sample steps), so only a two-step outcome (≤ 42 or ≥ 48) would be strong evidence.
- Separating √(n ln n) from A√n + B needs n ≈ 1000 to 2000.

**Feasibility.** Certifying d ≈ 46 exactly is beyond current tools: a d = 30 class already needs about 1.5 days against a 4-hour limit. So register the test in an asymmetric form:
- Cheap window upper bounds on every class in the band cap the true maximum. A largest upper bound of 44 or less refutes the power law; 42 or less also refutes √(n ln n).
- Refuting the lower curves needs one code certified at d ≥ 46.

**Stage 4's remaining tori cannot decide this.** These are n = 384 (Z4×Z48, Z8×Z24), 390 (Z195), 392 and 396. Every candidate predicts d = 28 at n = 384 and a first d = 30 somewhere between n = 390 and 402. A certified d = 30 at n = 390 would lean weakly toward the power law, and d = 30 may not be certifiable within the time limit anyway. Stage 4 will settle one thing: computing 6×30 must lift the (360, 12) entry to d ≥ 24 (score 19.2). That follows from the published code, so it is not a test.

The predictions were computed by /tmp/claude-0/-home-user/8f17707b-68ac-58ba-8e5d-b4b134d43d3d/scratchpad/regularity/synthesis/pred.py.

## Claims dropped or corrected by the skeptics

**Envelope**
- "0.615·√(n ln n) gets 13 of 14 stage-4 records exact" is reframed. Because d is even, that is 1 hit in 2 transitions (it misses d = 26 at 306 and hits d = 28 at 354). That matches its in-sample rate (it misses 4 of its 10 training steps). n^0.60 also scores 13/14, and the form was chosen after stage 4 was visible.
- "c·√n comes out a full even step too low" is replaced. The tightest constant (1.46) misses by about 0.6 and gets 10/14 exact. The −1.9 to −2.1 figure is mostly the model's misfit inside the training range, carried forward.
- c·√n·(1 − e^(−n/n0)) is not robustly ruled out: fitted on n = 200 to 300 it gets 13/14.
- "A√n + B cannot be separated" is corrected. Fitted from n ≥ 30 it is disfavoured (ΔAICc ≈ 12.4). It ties only once the fit starts at n ≳ 90.
- "Forms separate at n ≈ 630 to 1700" is corrected. The range runs from about 530 to about 20,000 depending on the pair, and the two-parameter log-corrected forms need n of order 10^4.
- "√(n ln n) and n^0.61 to 0.64 have the same shape within 1.7%" is corrected. That holds only for b ≈ 0.60 to 0.61. b = 0.64 is wrong at 10 of 79 n.
- "The two leading forms separate by one step around n ≈ 1000" is corrected to about n ≈ 620 to 750 (two steps at 1000).
- The 60/63 staircase match is in-sample only. The constant was tuned to a window of 0.6173 to 0.6181, and n^0.6 and the registered law also score 60/63.

**Extreme values**
- "The edge is a sharp cutoff, not an extreme-value lottery" and "class count is worth at most 0.5 in d" are dropped. The data cannot tell a cutoff from a lottery. Class count is worth about 1 to 2 in d across the range. The within-n pair result (3 higher / 12 equal / 1 lower) is what a pure lottery would also produce. The evt.py counts at d_max − 2 for the stage-3d tori were really counts at d_max − 4.
- "The rise of d/√n is not an extreme-value effect" is softened. The bulk of classes does rise, but about 20% of the maximum's extra exponent above 1/2 (0.67 against 0.63 for a fixed sample size) comes from the growing class count. Requiring at least 3 classes at the band maxima lowers them by about one step (1.265/1.333/1.389 become 1.231/1.306/1.342). The Gaussian benchmark is 2.67, not 3.19.

**k trade-off**
- "1.692·√n − k reproduces all eight band maxima within 0.03" is dropped. The first band misses by 0.040. All the band maxima are k = 4 codes, so they never test the −k term, and the agreement comes from errors cancelling. With a constant c the model is misspecified for k ≥ 6.
- "d + k is nearly constant" is softened. It holds only to within 1 to 2 even steps (median spread 4). The slope drifts with n, and a linear fall in k cannot be told apart from D(1 − k/28) or D·e^(−k/15).
- "Best k·d²/n is bounded at about 14 to 16" is dropped. It is still rising, and the uncomputed Z6×Z30 holds [[360,12,24]], which scores 19.2.

**Theory**
- "The best codes are not a fixed-stencil 2D-local family; the stencil grows like N^(1/4); BPT does not apply" is dropped. The minimal stencil levels off at diameter 3 for n = 200 to 384, so 2D bounds apply within the range, with unknown constants.
- "√n is proven only for hypergraph products" is corrected. Lin–Pryadko's bound d ≤ min(|G_a|, |G_b|) also gives √n for other subfamilies, though not for the record codes.
- The n^(3/4) bound's n counts group elements, so in census units it reads 8.49·n^(3/4), valid for n ≥ 16,384.

**Structure**
- The single-frontier-point rule holds on all census groups but is not a general iff (Z5×Z85 is a counterexample).
- The cyclic group's advantage at the column top is not fully explained by its larger class count (stratified test at n ≤ 200, P < 1e-4).
