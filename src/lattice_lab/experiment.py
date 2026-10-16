"""Running experiments and turning their records into observations.

The loop asks an experimenter to `measure` some torus sizes and gets back one `Observation` per
size. `LatticeExperimenter` runs LatticeLife's `sweep` tasks (one soup per seed, stopped as soon
as a state repeats), appends their records to the question's records file, and reads the
settling times back through LatticeLife's observables, which say when a number is only a bound.
A size with seeds that never repeated within the cap is rerun, for those seeds only, with a cap
four times larger, until every seed settles, the cap reaches `max_cap`, or the budget runs out.
A size still incomplete after that is reported as such and never counts for or against a law.

What the loop needs from an experimenter is small (`measure`, `offset`), so the self-check can
put synthetic data through the same loop (`selfcheck.SyntheticExperimenter`).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Protocol

import numpy as np
from latticelife.config import DEFAULT_CONFIG_PATH, Config, load_config
from latticelife.experiments.harness import GridLabel, parse_grid
from latticelife.experiments.observables import TransientRow, median_transient
from latticelife.experiments.sweeps import SweepTask, run_sweep, sweep_point

from lattice_lab.ledger import record_lines
from lattice_lab.question import Question, cells_of, size_of

CAP_GROWTH = 4


@dataclass(frozen=True)
class Observation:
    """The settling time measured at one torus size."""

    label: GridLabel
    x: float  # size: the side of a square torus with as many cells
    y: float | None  # median settling time over seeds, when every seed settled
    low: float | None  # bootstrap 95% interval of the median
    high: float | None
    seeds: int
    unsettled: int
    complete: bool
    max_cap: int | None  # the largest cap an unsettled seed reached
    note: str = ""
    # Robust spread of the seeds' settling times (1.4826 x the median absolute deviation, a
    # standard deviation for normal data): of log t, and of t itself.
    spread_log: float | None = None
    spread: float | None = None

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> Observation:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


LOG_FLOOR = 0.5  # half a generation: settling times are whole numbers


def robust_sd(values) -> float:
    """1.4826 x the median absolute deviation: the standard deviation for normal data, and
    not moved by a few seeds that took far longer than the rest."""
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return 0.0
    return float(1.4826 * np.median(np.abs(v - np.median(v))))


def observation_from_row(row: TransientRow) -> Observation:
    note = ""
    if not row.complete:
        upper = "unbounded" if row.median_at_most is None else f"{row.median_at_most:g}"
        note = (
            f"{row.unsettled} of {row.seeds} seeds never repeated within {row.max_cap + 1} "
            f"generations, so the median is only bounded: at least {row.median_at_least:g}, "
            f"at most {upper}"
        )
    times = np.asarray(row.settling_times, dtype=float)
    complete = row.complete and times.size > 0
    return Observation(
        label=row.grid,
        x=size_of(row.grid),
        y=row.median,
        low=row.low,
        high=row.high,
        seeds=row.seeds,
        unsettled=row.unsettled,
        complete=row.complete,
        max_cap=row.max_cap,
        note=note,
        spread_log=robust_sd(np.log(np.maximum(times, LOG_FLOOR))) if complete else None,
        spread=robust_sd(times) if complete else None,
    )


@dataclass
class Measurement:
    observations: list[Observation]
    records: list[dict] = field(default_factory=list)  # {"offset", "sha256", "grid", "seed", ...}
    spent_cell_steps: int = 0
    notes: list[str] = field(default_factory=list)


class Experimenter(Protocol):
    def offset(self) -> int: ...

    def measure(self, labels: list[GridLabel], budget_cell_steps: float) -> Measurement: ...


def question_config(question: Question, config_path: str | Path | None = None) -> Config:
    """LatticeLife's config for this question: its defaults, with the question's triangle
    neighbourhood. Grid shape and size come from each task, as in every experiment."""
    config = load_config(config_path or DEFAULT_CONFIG_PATH)
    if question.triangle_mode:
        config = replace(config, grid=replace(config.grid, triangle_mode=question.triangle_mode))
    return config


class LatticeExperimenter:
    """Runs a question's sweeps with LatticeLife into `records_path` (see the module
    docstring)."""

    def __init__(
        self,
        question: Question,
        records_path: str | Path,
        config: Config | None = None,
        workers: int = 1,
        progress=None,
    ) -> None:
        self.question = question
        self.records_path = Path(records_path)
        self.config = config if config is not None else question_config(question)
        self.workers = workers
        self.progress = progress or (lambda message: None)

    def offset(self) -> int:
        """Where the records file ends now: records written later lie past this byte."""
        return self.records_path.stat().st_size if self.records_path.is_file() else 0

    def _matching(self, labels: set) -> list[tuple[int, str, dict]]:
        q = self.question
        out = []
        for offset, digest, line in record_lines(self.records_path):
            record = json.loads(line)
            if (
                record.get("rule") == q.rule_text
                and record.get("shape") == q.shape
                and float(record.get("density", -1)) == float(q.density)
                and parse_grid(record["grid"]) in labels
            ):
                out.append((offset, digest, record))
        return out

    def _run(self, labels: list[GridLabel], seeds: list[int], cap: int) -> None:
        q = self.question
        from latticelife.core.rules import Rule

        for _ in run_sweep(
            self.config,
            Rule.from_bs_string(q.rule),
            q.shape,
            labels,
            [q.density],
            seeds,
            cap,
            str(self.records_path),
            self.workers,
        ):
            pass

    def measure(self, labels: list[GridLabel], budget_cell_steps: float) -> Measurement:
        q = self.question
        labels = [parse_grid(label) for label in labels]
        wanted = set(labels)
        start = self.offset()
        notes: list[str] = []
        self.progress(f"running {len(labels)} sizes x {q.seeds} seeds at cap {q.cap}")
        self._run(labels, list(range(1, q.seeds + 1)), q.cap)
        while True:
            rows = median_transient(record for _, _, record in self._matching(wanted))
            spent = self._spent(start, wanted)
            reruns = []
            for row in rows:
                if row.complete:
                    continue
                reached = row.max_cap + 1
                if reached >= q.max_cap:
                    notes.append(f"size {row.grid}: seeds still unsettled at max_cap {q.max_cap}")
                    continue
                cap = min(q.max_cap, reached * CAP_GROWTH)
                cost = cells_of(row.grid) * cap * len(row.unsettled_seeds)
                if spent + cost > budget_cell_steps:
                    notes.append(f"size {row.grid}: no budget left to rerun at cap {cap}")
                    continue
                reruns.append((row.grid, row.unsettled_seeds, cap))
                spent += cost
            if not reruns:
                break
            for grid, seeds, cap in reruns:
                self.progress(f"size {grid}: rerunning {len(seeds)} unsettled seeds at cap {cap}")
                self._run([grid], seeds, cap)
        refs = [
            {
                "offset": offset,
                "sha256": digest,
                "grid": record["grid"],
                "seed": record["seed"],
                "steps": record["steps"],
            }
            for offset, digest, record in self._matching(wanted)
        ]
        observations = [observation_from_row(row) for row in rows]
        return Measurement(observations, refs, self._spent(start, wanted), notes)

    def _spent(self, start: int, labels: set) -> int:
        """Generations x cells actually stepped by the records written since `start`."""
        return sum(
            (int(record["stopped_at"]) + 1) * cells_of(record["grid"])
            for offset, _, record in self._matching(labels)
            if offset >= start
        )


def rerun_record(record: dict, config: Config) -> str:
    """The JSON line LatticeLife writes for this sweep record's task, run again now. Equal to
    the stored line exactly when the run reproduces byte for byte."""
    task = SweepTask(
        config,
        record["rule"],
        record["shape"],
        record["grid"],
        float(record["density"]),
        int(record["seed"]),
        int(record["steps"]),
    )
    return json.dumps(sweep_point(task).to_json())
