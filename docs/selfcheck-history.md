# Self-check history

The pass marks in `thresholds.toml` were committed (bf94d34) before the self-check first ran,
and have not changed. Each full run is recorded here, failures included; the latest is in
[selfcheck.md](selfcheck.md).

## Run 1, 2026-10-16: FAILED

20 questions per law, the loop as first written (held-out tests at alpha = 0.05; each median's
error from its bootstrap interval; a simpler law named whenever no rival as simple was within 6
BIC points).

| Check | Value | Pass mark | |
| --- | --- | --- | --- |
| mean_correct_rate | 0.583 | >= 0.5 | pass |
| max_wrong_rate | 0.150 | <= 0.05 | FAIL |
| thin_max_wrong_rate | 0.150 | <= 0.1 | FAIL |

| True law | Correct | Wrong | Fragile | Inconclusive | None fits | Wrong laws |
| --- | --- | --- | --- | --- | --- | --- |
| constant | 17 | 0 | 0 | 2 | 1 |  |
| logarithmic | 7 | 0 | 0 | 9 | 4 |  |
| linear | 4 | 2 | 0 | 11 | 3 | power x2 |
| power | 4 | 3 | 0 | 13 | 0 | logarithmic x3 |
| exponential | 19 | 0 | 0 | 0 | 1 |  |
| exponential_area | 19 | 0 | 0 | 0 | 1 |  |

Thin data (4 seeds): wrong answers for logarithmic (constant x3), power (constant x2) and
linear (exponential x2).

What it showed, and what changed in the loop (not the marks):

1. **Each median's error was too small, with heavy tails.** On synthetic data the true law's
   held-out test failed the 1% level 4.7% of the time. A median's error now comes from the robust
   spread of its seeds' log settling times, pooled across sizes (`analysis.standard_error`). The
   true law then fails at 0.7% (1% level) and 4-5% (5% level).
2. **A constant was named because noisy data showed no trend.** A simpler law is now named over
   a richer one that also passed only when the richer one stays within +-50% of it at every
   measured size with 95% confidence (`analysis.equivalent`). On thin data the constant law now
   comes out inconclusive instead of wrongly confirmed or wrongly named for a power law.
3. **alpha 0.05 -> 0.01.** Each round tests every law again; a true law rejected by chance
   leaves room for a wrong one. On two random streams independent of the self-check's (40
   questions per law), 0.01 gave both more correct answers (0.608 vs 0.588) and fewer wrong
   ones (worst 0.050 vs 0.075).

These were tuned on random streams other than the self-check's own (`salt` 7-29), so run 2 is
not fitted to run 1's draws.

## Run 2, 2026-10-16: PASSED

20 questions per law, the loop with the three changes above. Full result in
[selfcheck.md](selfcheck.md).

| Check | Value | Pass mark | |
| --- | --- | --- | --- |
| mean_correct_rate | 0.550 | >= 0.5 | pass |
| max_wrong_rate | 0.050 | <= 0.05 | pass, at the mark (linear named power once) |
| thin_max_wrong_rate | 0.050 | <= 0.1 | pass |

The margin on wrong answers is thin: on the independent streams the worst law (a power law
with exponent 0.35, the hardest to tell from a logarithm) was named wrongly 2 times in 80.
Laws that are easy to tell apart (constant, the exponentials) are named 90-100% of the time;
the logarithm, linear and power laws mostly come out inconclusive rather than wrong.
