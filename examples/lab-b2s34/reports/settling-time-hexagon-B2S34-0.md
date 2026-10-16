# How does settling time grow with torus size? B2/S34 on hexagon tori, density 0.5

**Verdict: found**: logarithmic, `T(L) = a*log(L) + b`

logarithmic passed its held-out test; power also passed but fits all the data 8.4 BIC points worse.

- Fitted to the fit sizes (what was pre-registered): a = 38.74 ± 6.3, b = -39.81 ± 16.
- Refitted to every measured size: a = 37.6 ± 2.7, b = -36.27 ± 8.3.
- Held out: 3 of 3 sizes inside the 95% band; joint chi-square test p = 0.92.
- Robustness: 9 of 9 reduced fits (smallest sizes dropped, each size left out) lead with the same law.

| | |
| --- | --- |
| Question | `settling-time-hexagon-B2S34`, ledger entry 0 `8c093764f001` |
| Asked | 2026-10-16T20:39:09+00:00 |
| Experiment | B2/S34 on hexagon tori, density 0.5, 20 seeds per size, caps 2,000 to 64,000 |
| Laws considered | constant, logarithmic, linear, power, exponential, exponential_area |
| Code | lattice-lab 0.1.0 @ `25698fdb75` (uncommitted changes); LatticeLife 0.1.0 @ `25c2e18029`; Kepler 0.1.0 @ `3d0e1b4f19`; Python 3.13.16 |
| Records | `records/settling-time-hexagon-B2S34-0.jsonl` |
| Questions in this ledger | 1 (this was number 1); every one asked is counted, since scanning many rules turns up chance fits |
| Compute | 97,022,252 cell updates |

## Fit sizes

| Size | L | Seeds | Median settling time | 95% interval | Unsettled | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | 8 | 20 | 45 | 40 to 61 | 0 |  |
| 10 | 10 | 20 | 42.5 | 38 to 62 | 0 |  |
| 12 | 12 | 20 | 60.5 | 44 to 91.5 | 0 |  |
| 16 | 16 | 20 | 65.5 | 58.5 to 75.5 | 0 |  |
| 20 | 20 | 20 | 85 | 74 to 99.5 | 0 |  |
| 24 | 24 | 20 | 81.5 | 68.5 to 106 | 0 |  |
| 32 | 32 | 20 | 93 | 81 to 104 | 0 |  |

## Round 1: found

### Fits to 7 sizes (log space)

best fit by BIC: logarithmic (r2=0.9152).

| Law | ΔBIC | Constants | R² | Eligible |
| --- | --- | --- | --- | --- |
| logarithmic | 0 | a = 38.74 ± 6.3, b = -39.81 ± 16 | 0.9152 | yes |
| power | 0.17 | a = 12.07 ± 3.4, b = 0.6075 ± 0.098 | 0.9112 | yes |
| linear | 0.98 | a = 2.45 ± 0.41, b = 24.24 ± 6.5 | 0.8917 | yes |
| exponential | 3.5 | a = 35.91 ± 4.8, b = 0.03353 ± 0.0067 | 0.832 | yes |
| exponential_area | 8.9 | a = 48.89 ± 5.6, b = 0.000764 ± 0.00022 | 0.7033 | yes |
| constant | 36 | a = 66.26 ± 8 | 0 | yes |

Held-out sizes chosen: 64, 96, 128, where logarithmic, power, linear, exponential, exponential_area disagree most for the budget.

Can these sizes decide between logarithmic and power? Not in expectation: a BIC difference of 3.9 over all 10 sizes, against a margin of 6; about 1.5x the seeds would reach it. The round can still reject laws, but is unlikely to name one.

### Predictions, recorded before the run (entry 10) started

| Law | Size | Predicted | 95% band | Entry |
| --- | --- | --- | --- | --- |
| logarithmic | 64 | 121 | 102 to 144 | 4 `f0045e207773` |
| logarithmic | 96 | 137 | 114 to 165 | 4 `f0045e207773` |
| logarithmic | 128 | 148 | 122 to 180 | 4 `f0045e207773` |
| power | 64 | 151 | 115 to 199 | 5 `2a5c9d59333b` |
| power | 96 | 193 | 136 to 275 | 5 `2a5c9d59333b` |
| power | 128 | 230 | 153 to 345 | 5 `2a5c9d59333b` |
| linear | 64 | 181 | 145 to 227 | 6 `9f409fb0707d` |
| linear | 96 | 259 | 201 to 335 | 6 `9f409fb0707d` |
| linear | 128 | 338 | 257 to 444 | 6 `9f409fb0707d` |
| exponential | 64 | 307 | 166 to 567 | 7 `3155b1085ac0` |
| exponential | 96 | 898 | 320 to 2520 | 7 `3155b1085ac0` |
| exponential | 128 | 2630 | 614 to 11200 | 7 `3155b1085ac0` |
| exponential_area | 64 | 1120 | 222 to 5620 | 8 `40e7e620e237` |
| exponential_area | 96 | 55900 | 1200 to 2.6e+06 | 8 `40e7e620e237` |
| exponential_area | 128 | 1.34e+07 | 12700 to 1.4e+10 | 8 `40e7e620e237` |
| constant | 64 | 66.3 | 52.4 to 83.9 | 9 `3624adc41345` |
| constant | 96 | 66.3 | 52.4 to 83.9 | 9 `3624adc41345` |
| constant | 128 | 66.3 | 52.4 to 83.9 | 9 `3624adc41345` |

### Held-out measurements

| Size | L | Seeds | Median settling time | 95% interval | Unsettled | Note |
| --- | --- | --- | --- | --- | --- | --- |
| 64 | 64 | 20 | 123 | 119 to 132 | 0 |  |
| 96 | 96 | 20 | 134 | 128 to 138 | 0 |  |
| 128 | 128 | 20 | 140 | 133 to 159 | 0 |  |

### Held-out tests

| Law | Result | p (joint chi-square) | Inside 95% band |
| --- | --- | --- | --- |
| logarithmic | consistent | 0.92 | 3 of 3 |
| power | consistent | 0.09 | 2 of 3 |
| linear | rejected | 3.4e-08 | 0 of 3 |
| exponential | rejected | 1.1e-06 | 0 of 3 |
| exponential_area | rejected | 1.5e-08 | 0 of 3 |
| constant | rejected | 5.5e-07 | 0 of 3 |

### Laws that passed, refitted to every size

| Law | ΔBIC | Constants |
| --- | --- | --- |
| logarithmic | 0 | a = 37.6 ± 2.7, b = -36.27 ± 8.3 |
| power | 8.4 | a = 22.28 ± 3.3, b = 0.3979 ± 0.04 |

### Context: every law refitted to every size

Not part of the verdict, which rests on the pre-registered predictions. It shows whether a rejected law fails in shape or only in its extrapolation from the fit sizes.

| Law | ΔBIC | Constants | Eligible |
| --- | --- | --- | --- |
| logarithmic | 0 | a = 37.6 ± 2.7, b = -36.27 ± 8.3 | yes |
| power | 8.4 | a = 22.28 ± 3.3, b = 0.3979 ± 0.04 | yes |
| linear | 31 | a = 0.8584 ± 0.16, b = 54.33 ± 6.8 | yes |
| exponential | 46 | a = 63.37 ± 6.7, b = 0.00743 ± 0.0016 | yes |
| exponential_area | 78 | a = 75.62 ± 8, b = 4.751e-05 ± 1.5e-05 | yes |
| constant | 190 | a = 93.43 ± 11 | yes |

### Robustness

| Variant | Leading law | Verdict | Same law |
| --- | --- | --- | --- |
| without the 1 smallest | logarithmic | found | yes |
| without the 2 smallest | logarithmic | inconclusive | yes |
| without 8 | logarithmic | found | yes |
| without 10 | logarithmic | inconclusive | yes |
| without 12 | logarithmic | found | yes |
| without 16 | logarithmic | found | yes |
| without 20 | logarithmic | inconclusive | yes |
| without 24 | logarithmic | found | yes |
| without 32 | logarithmic | found | yes |

Verdict entry 12 `46f7a2632b69`.

## Checking this report

`lattice-lab verify --lab <lab>` checks that no ledger entry was edited, that every prediction was written before the run that tested it and that every held-out record was appended after it, and reruns records to confirm they reproduce byte for byte.
