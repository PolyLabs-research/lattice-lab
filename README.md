# lattice-lab

A law-discovery loop over two existing projects. It asks "how does quantity y depend on setting
x" for a cellular-automaton rule, and answers with a named law, its constants with error bars,
and a verdict from experiments the fit never saw. Each prediction is recorded before the run
that tests it, in an append-only, hash-chained ledger.

- [LatticeLife](https://github.com/PolyLabs-research/gameoflife_advanced) runs the experiments
  and says what their numbers mean, including when a number is only a bound.
- [Kepler](https://github.com/tripptytrip/kepler) fits, ranks and predicts closed-form laws
  with error bars.
- lattice-lab owns what belongs to neither: the questions, the candidate laws, choosing the next
  experiment, pre-registered predictions, verdicts, and the record of every result.

Neither library imports lattice-lab or the other. See [docs/design.md](docs/design.md) for the
architecture, the loop step by step, and the milestones.

## Install

```bash
uv sync                      # LatticeLife and Kepler at the commits pinned in pyproject.toml
uv run pytest
```

Python 3.12 or 3.13 (LatticeLife's bound). To work against local checkouts of the libraries,
run `uv pip install -e ../gameoflife_advanced -e ../kepler` after `uv sync`, then use
`uv run --no-sync`; the ledger records their commits and whether they had uncommitted changes.

## Use

```bash
uv run lattice-lab ask questions/settling-time-hexagon-B2S34.toml --lab lab --workers 8
uv run lattice-lab verify --lab lab --rerun 5     # chain, order, and records rerun byte for byte
uv run lattice-lab report --lab lab               # rebuild the latest report from the ledger
uv run lattice-lab selfcheck --out docs/selfcheck.md
uv run lattice-lab laws
```

`ask` prints a JSON summary and writes `lab/reports/<id>-<n>.md`. The verdict is one of:

| Verdict | Meaning |
| --- | --- |
| found | One law passed its held-out test, no rival as simple is within 6 BIC points on all the data, and the verdict survives dropping the smallest sizes and each size in turn |
| fragile | A law passed, but the verdict changes when some fitted size is left out |
| inconclusive | Laws that passed are too close to call, or nothing could be tested (seeds unsettled at every cap, no budget, no sizes left) |
| none fits | Every candidate's held-out predictions were rejected, or none fits the data at all |

### A question

```toml
id = "settling-time-hexagon-B2S34"
rule = "B2/S34"
shape = "hexagon"            # square, hexagon, triangle (+ triangle_mode)
density = 0.5
seeds = 20
fit_sizes = [8, 10, 12, 16, 20, 24, 32]
heldout_pool = [40, 48, 64, 96, 128]   # "24x26" for a rectangular torus
```

Defaults (all overridable): `heldout_per_round = 3`, `max_rounds = 2`, `cap = 2000` and
`max_cap = 64000` generations, `laws` = constant, logarithmic, linear, power, exponential,
exponential in the area, `space = "auto"` (log when every value is positive), `alpha = 0.01`,
`decisive_bic = 6`, `budget_cell_steps = 2e11`. Version 1 asks one quantity, `settling_time`:
the median generation at which a soup's final cycle begins, against the torus size (for a
rectangle, the square root of its cells).

### The lab directory

```
lab/
  ledger.jsonl          every question, run, observation, plan, prediction and verdict
  records/<id>-<n>.jsonl  LatticeLife's raw records for that question
  reports/<id>-<n>.md   the report, rebuilt from the ledger by `report`
```

Keep a lab directory as data, apart from this code. Reports state how many questions the
ledger holds, since scanning many rules turns up chance fits.

## Example: B2/S34 on the hexagon lattice

`examples/lab-b2s34/` is a complete lab from `uv run lattice-lab ask
questions/settling-time-hexagon-B2S34.toml` on the pinned commits: the ledger, LatticeLife's 200
records and [the report](examples/lab-b2s34/reports/settling-time-hexagon-B2S34-0.md).
`uv run lattice-lab verify --lab examples/lab-b2s34` checks it.

Its answer is not the prototype's. Fitted on L = 8 to 32 and tested at 64, 96 and 128, the
verdict is **found: logarithmic**, T(L) = 37.6 log L − 36.3 (± 2.7 and ± 8.3, all sizes). A
power law also passed its held-out test (p = 0.09), but on all ten sizes it is 8.4 BIC points
worse. The verdict holds with the smallest sizes dropped and with each size left out. The
prototype reported T ≈ 27·L^0.35. Before the run, the plan said these sizes and seeds could
not be expected to separate the two (an expected BIC difference of 3.9 against a margin of 6;
about 1.5× the seeds would), so the margin seen is more than the design promised: treat this
as one answer to replicate with more seeds or larger tori, not a settled fact.

## Beyond settling time: what else Kepler finds in LatticeLife data

[docs/capabilities.md](docs/capabilities.md) runs each of Kepler's newer tools on real
LatticeLife simulations (`uv run python examples/capabilities/run.py`): survival windows and how
their edges move with torus size (binomial likelihood, one fit over density and size), times that
are only bounds (a censored likelihood), whether a law depends on the starting density (shared
constants), relaxation and damage over time with seed-to-seed error bars, distributions of object
sizes, exact formulas for periods (the XOR rule's period on an n x n torus; a
[pre-registered test](docs/xor-periods.md) confirmed it at 45 unseen sizes by simulation and at
every n up to 200 exactly, and found the rule never shares 1D rule 90's shortfalls; a
[partial proof](docs/xor-periods-proof.md) reduces it to odd sizes and settles every odd part up to
999 but ten; on the hexagonal and triangular lattices a [second registered test](docs/parity-lattices.md)
refuted Kepler's law on the hexagon at three of 210 sizes, which led to a proof that two hexagon
generations are three passes of rule 90), conserved quantities (with a parity of births found from data and then proved), and whether
a fitted constant is a known number. The loop itself still asks about settling time; those
studies are ready to become question types.

## Trusting the answers

- **Self-check.** `selfcheck` runs the loop on synthetic data from every law, with the sizes,
  seed spreads and censoring of real runs. It compares the outcome with pass marks committed in
  `thresholds.toml` before its first run and never edited to pass. The latest result is in
  [docs/selfcheck.md](docs/selfcheck.md); [docs/selfcheck-history.md](docs/selfcheck-history.md)
  records every full run, including the first, which failed, and what changed in the loop.
- **Known rules.** The empty rule `B/S` gives a constant. A linear rule's transients and periods
  match an independent GF(2) computation (`tests/test_known_rules.py`).
- **Order.** `verify` checks every verdict's predictions were written before its run started,
  and every held-out record was appended after that.
- **Reproducibility.** `verify --rerun N` reruns records from their seeds and settings and
  compares the bytes.
- **The prototype's traps** are regression tests (`tests/test_traps.py`): a zero starting
  constant must not vanish; a verdict must survive dropping the smallest sizes; an unsettled run
  must never count against a law.
