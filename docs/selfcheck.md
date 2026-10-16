# lattice-lab self-check

**PASSED**, 20 synthetic questions per law.

| Check | Value | Pass mark | |
| --- | --- | --- | --- |
| mean_correct_rate | 0.550 | >= 0.5 | pass |
| max_wrong_rate | 0.050 | <= 0.05 | pass |
| thin_max_wrong_rate | 0.050 | <= 0.1 | pass |

## Normal data

| True law | Correct | Wrong | Fragile | Inconclusive | None fits | Wrong laws |
| --- | --- | --- | --- | --- | --- | --- |
| constant | 18 | 0 | 0 | 2 | 0 |  |
| logarithmic | 5 | 0 | 0 | 15 | 0 |  |
| linear | 2 | 1 | 0 | 16 | 1 | power x1 |
| power | 2 | 0 | 0 | 18 | 0 |  |
| exponential | 19 | 0 | 0 | 0 | 1 |  |
| exponential_area | 20 | 0 | 0 | 0 | 0 |  |

## Thin data

| True law | Correct | Wrong | Fragile | Inconclusive | None fits | Wrong laws |
| --- | --- | --- | --- | --- | --- | --- |
| constant | 0 | 0 | 0 | 19 | 1 |  |
| logarithmic | 0 | 0 | 0 | 17 | 3 |  |
| linear | 0 | 1 | 0 | 19 | 0 | exponential x1 |
| power | 0 | 0 | 0 | 19 | 1 |  |
| exponential | 16 | 0 | 0 | 3 | 1 |  |
| exponential_area | 19 | 0 | 1 | 0 | 0 |  |
