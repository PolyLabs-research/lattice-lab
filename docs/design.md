# lattice-lab: architecture, the loop, milestones

This completes the design note "LatticeLife × Kepler: design for a law-discovery loop"
(2026-10-16), whose architecture, loop and milestone sections were left open, as built.

## Architecture

Three packages, one dependency direction. lattice-lab imports both libraries; neither imports
lattice-lab or the other, and each stays useful on its own.

```
                 lattice-lab  (questions, loop, ledger, reports, self-check)
                  /                         \
                 v                           v
   LatticeLife (experiments,          Kepler (fit, rank, predict,
   what their numbers mean)           law library; any (x, y) data)
   numpy, pygame                      numpy, scipy, sympy
```

| Package | Owns | Python | Pinned by lattice-lab to |
| --- | --- | --- | --- |
| LatticeLife (`PolyLabs-research/gameoflife_advanced`) | Running experiments; turning records into observations with uncertainty; saying when a number is only a bound | 3.12-3.13 | a git commit |
| Kepler (`tripptytrip/kepler`) | Fitting a named law with error bars; ranking by BIC; predicting with a band and a covariance | 3.10+ | a git commit |
| lattice-lab (`tripptytrip/lattice-lab`) | Questions, candidate laws, choosing the next experiment, pre-registered predictions, verdicts, the ledger | 3.12-3.13 (LatticeLife's bound) | - |

### Data flow

```
question.toml
   -> LatticeExperimenter: LatticeLife sweep tasks -> records/<id>-<seq>.jsonl (append-only)
   -> latticelife.experiments.observables.median_transient -> TransientRow per size
   -> Observation (x = size, y = median, 95% interval, complete?)
   -> kepler.fit per law (weighted, log space) -> kepler.rank (BIC, Occam window)
   -> planner: held-out sizes where the laws disagree
   -> kepler.predict / predict_covariance -> ledger: prediction entries      (before the run)
   -> LatticeExperimenter on the held-out sizes -> ledger: observations      (after)
   -> judge (joint chi-square) -> decide -> fragility -> ledger: verdict
   -> report.render(ledger) -> reports/<id>-<seq>.md
```

### Data contracts

- **Records** (LatticeLife, JSONL): one per (rule, shape, torus, density, seed, cap), byte for
  byte reproducible from those fields and the LatticeLife commit. `no_repeat_before` is set only
  when no state repeated within the cap and bounds transient + period, never the transient
  alone. The fields are pinned by LatticeLife's `tests/experiments/test_stable_api.py`.
- **TransientRow** (LatticeLife): per torus, `median`, a seeded bootstrap 95% interval,
  `complete` (every seed settled), and for an incomplete row the bounds on the median and the
  seeds to rerun with a larger cap.
- **Fit** (Kepler): constants with standard errors and covariance, RMSE, R², BIC, the number of
  constants, the space and weighting, `ill_conditioned`.
- **Ledger entries** (lattice-lab, JSONL): `{seq, kind, time, prev, body, hash}`, hash-chained.
  Kinds: `question`, `run_started`, `observations`, `plan`, `prediction`, `verdict`.

## The discovery loop

1. **Question.** The question entry records the spec and the exact code (lattice-lab,
   LatticeLife and Kepler commits, dirty flags, the numerical stack).
2. **Measure the fit sizes.** Seeds that never repeat are rerun at 4x the cap, up to
   `max_cap`; a size still incomplete is recorded and left out of every fit.
3. **Propose and fit.** Every law in the question's library, weighted by each median's error,
   in log space when every value is positive. Errors are absolute and widened, never narrowed,
   by excess scatter (Kepler's `inflate`).
4. **Rank.** BIC with a 6-point Occam window. No eligible law: **none fits**.
5. **Choose the next experiment.** Held-out sizes where the contenders (eligible laws within 10
   BIC points) disagree most in units of their combined uncertainty, within the budget.
6. **Pre-register.** Every eligible law's predictions at those sizes, with bands and their full
   covariance, one ledger entry each, before the run starts.
7. **Run** the held-out sizes. The run entry records where the records file ended, so every
   held-out record provably comes after the predictions.
8. **Judge.** Each law's recorded predictions against the measurements, jointly:
   d² = rᵀ(P + S)⁻¹r ~ χ²(m). p < 0.01 rejects. Unsettled sizes are never judged.
9. **Decide.** All rejected: **none fits**. Otherwise the survivors are refitted to every size
   and ranked; a law is **found** only when every other survivor is 6 BIC points worse, or is
   richer but stays within ±50% of it at every measured size (95%), else **inconclusive**.
   Held-out tests decide which laws stay; BIC on all data picks among them. The equivalence
   clause stops a constant being named just because noisy data show no trend.
10. **Fragility.** A found law is recomputed without the smallest size, without the two
    smallest, and without each fitted size in turn. If any variant leads with another law or
    rejects it, the verdict is **fragile**.
11. **Record** the verdict, citing the predictions, the run and the observations. Found or none
    fits ends the question; otherwise the held-out sizes join the fit and the next round starts,
    up to `max_rounds`.

## Validation, as built

| Check | Where |
| --- | --- |
| Self-check against synthetic laws, pass marks committed before the first run | `lattice-lab selfcheck`, `thresholds.toml`, `docs/selfcheck.md` |
| The empty rule `B/S` dies at once; the loop says constant | `tests/test_known_rules.py` |
| A linear rule's transient and period match an independent GF(2) computation | `tests/test_known_rules.py` |
| Order check: predictions before the run, held-out records after it | `ledger.check_order`, `lattice-lab verify` |
| Records rerun byte for byte | `lattice-lab verify --rerun N` |
| The three prototype traps | `tests/test_traps.py` |

## Milestones

| # | Milestone | State |
| --- | --- | --- |
| 1 | Kepler's classical core as an installable library with fit, rank, predict; every existing test passing first | done |
| 2 | LatticeLife observables, `no_repeat_before`, rectangular tori, `damage` command, cost hints, stable interface | done |
| 3 | lattice-lab: settling time against torus size, end to end, with ledger, reports, verify and self-check | done |
| 4 | Survival against density (logistic, critical density x0 with error) and how it shifts with size (`shifted_power`) | tools done and shown on real data ([capabilities](capabilities.md)): binomial likelihood, `window`, one fit over density and size (`FSS_LAWS`), binomial designs; the loop does not ask it yet |
| 5 | Damage spreading and relaxation over time as quantities | tools done and shown: `TIME_LAWS`, seed-to-seed error bars (`fit_replicates`), `damage_curves`; not in the loop yet |
| 6 | The same rule across lattices (position paper Claim 1) | tools done (`fit_groups`, `compare_sharing`), shown across densities; across lattices open |
| 7 | More proposers: a language model through Kepler's `fit_skeleton`, Kepler's specialist models | open |

Kepler also gained, each with known-answer tests and a run on real data in
[capabilities](capabilities.md): a censored likelihood for times some of which are only bounds
(LatticeLife's `event_times`), distribution fitting (`kepler.distributions`), matching constants to
known numbers with a chance-match probability (`identify`), exact integer laws
(`find_integer_laws`), and conserved quantities (`find_invariants`, LatticeLife's
`count_series`).
