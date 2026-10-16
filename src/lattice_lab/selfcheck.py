"""The self-check: the loop must recover laws it was not told.

Synthetic questions are generated from every law in the growth library with constants on the
scale of real settling times. Each seed's settling time is the law's value at that size times a
log-normal spread, plus a short period; a seed whose transient + period exceeds the cap is
unsettled at that cap and is "rerun" with a larger one, exactly as `LatticeExperimenter` does, and
the records go through LatticeLife's own observables. So the sizes, spreads and censoring are
those of real runs, and only the simulator is replaced.

The loop then answers each question, and the self-check counts how often it names the true law
(correct), names another (wrong), or answers fragile, inconclusive or none fits. The pass marks
come from `thresholds.toml`, committed before the self-check first ran and never edited to pass:
on average over the laws it must name the true law at least `min_correct_rate` of the time, for
every law name a wrong one at most `max_wrong_rate` of the time, and on thin data (few seeds, a
wide spread) still name a wrong law at most `thin.max_wrong_rate` of the time.
"""

from __future__ import annotations

import math
import tomllib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sympy
from kepler import LAWS
from latticelife.experiments.observables import median_transient

from lattice_lab.experiment import Measurement, observation_from_row
from lattice_lab.ledger import Ledger
from lattice_lab.loop import ask
from lattice_lab.question import Question, size_of

# True constants, on the scale of real settling times over L = 8..128 (the power law is the
# prototype's B2/S34 fit, the case where logarithmic and power laws are hardest to tell apart).
TRUE_LAWS: dict[str, dict[str, float]] = {
    "constant": {"a": 60.0},
    "logarithmic": {"a": 25.0, "b": -20.0},
    "linear": {"a": 2.5, "b": 10.0},
    "power": {"a": 27.0, "b": 0.35},
    "exponential": {"a": 20.0, "b": 0.05},
    "exponential_area": {"a": 30.0, "b": 0.0004},
}

FIT_SIZES = (8, 10, 12, 16, 20, 24, 32)
HELDOUT_POOL = (40, 48, 64, 96, 128)


def synthetic_question(name: str, seeds: int) -> Question:
    return Question(
        id=f"selfcheck-{name}",
        rule="B2/S34",
        shape="hexagon",
        fit_sizes=FIT_SIZES,
        heldout_pool=HELDOUT_POOL,
        seeds=seeds,
        cap=2000,
        max_cap=64000,
    )


class SyntheticExperimenter:
    """Settling times drawn from a known law, censored like real runs (module docstring)."""

    def __init__(
        self,
        law: str,
        params: dict[str, float],
        question: Question,
        spread: float,
        rng: np.random.Generator,
    ) -> None:
        expr, symbols = LAWS[law].parametrized()
        self._f = sympy.lambdify([sympy.Symbol("x"), *symbols], expr, "numpy")
        self._args = [params[p] for p in LAWS[law].params]
        self.question = question
        self.spread = spread
        self.rng = rng

    def offset(self) -> int:
        return 0

    def truth(self, x: float) -> float:
        return float(np.broadcast_to(self._f(np.asarray(x, dtype=float), *self._args), ()))

    def measure(self, labels, budget_cell_steps: float) -> Measurement:
        q = self.question
        records = []
        for label in labels:
            centre = self.truth(size_of(label))
            for seed in range(1, q.seeds + 1):
                transient = int(round(max(centre, 0.0) * math.exp(self.spread * self.rng.normal())))
                period = 1 + int(self.rng.poisson(2.0))
                cap = q.cap
                while True:
                    base = {
                        "rule": q.rule_text,
                        "shape": q.shape,
                        "triangle_mode": None,
                        "grid": label,
                        "density": q.density,
                        "seed": seed,
                        "steps": cap,
                    }
                    if transient + period <= cap - 1:
                        records.append(
                            {
                                **base,
                                "transient": transient,
                                "period": period,
                                "stopped_at": transient + period,
                                "extinction_step": None,
                                "no_repeat_before": None,
                            }
                        )
                        break
                    records.append(
                        {
                            **base,
                            "transient": None,
                            "period": None,
                            "stopped_at": cap - 1,
                            "extinction_step": None,
                            "no_repeat_before": cap - 1,
                        }
                    )
                    if cap >= q.max_cap:
                        break
                    cap = min(q.max_cap, cap * 4)
        rows = median_transient(records)
        return Measurement([observation_from_row(row) for row in rows])


@dataclass
class LawResult:
    law: str
    replicates: int
    correct: int = 0
    wrong: int = 0
    fragile: int = 0
    inconclusive: int = 0
    none_fits: int = 0
    wrong_laws: dict | None = None

    @property
    def correct_rate(self) -> float:
        return self.correct / self.replicates

    @property
    def wrong_rate(self) -> float:
        return self.wrong / self.replicates

    def to_json(self) -> dict:
        return {
            "law": self.law,
            "replicates": self.replicates,
            "correct": self.correct,
            "wrong": self.wrong,
            "fragile": self.fragile,
            "inconclusive": self.inconclusive,
            "none_fits": self.none_fits,
            "wrong_laws": self.wrong_laws or {},
            "correct_rate": self.correct_rate,
            "wrong_rate": self.wrong_rate,
        }


def run_law(law: str, replicates: int, seeds: int, spread: float, salt: int = 0) -> LawResult:
    result = LawResult(law, replicates, wrong_laws={})
    question = synthetic_question(law, seeds)
    law_index = list(TRUE_LAWS).index(law)
    for replicate in range(replicates):
        rng = np.random.default_rng([law_index, replicate, seeds, salt])
        experimenter = SyntheticExperimenter(law, TRUE_LAWS[law], question, spread, rng)
        outcome = ask(question, experimenter, Ledger(None))
        if outcome.verdict == "found":
            if outcome.law == law:
                result.correct += 1
            else:
                result.wrong += 1
                result.wrong_laws[outcome.law] = result.wrong_laws.get(outcome.law, 0) + 1
        elif outcome.verdict == "fragile":
            result.fragile += 1
        elif outcome.verdict == "none fits":
            result.none_fits += 1
        else:
            result.inconclusive += 1
    return result


def load_thresholds(path: str | Path) -> dict:
    return tomllib.loads(Path(path).read_text())


def run_selfcheck(thresholds: dict, replicates: int | None = None, progress=None) -> dict:
    """Run both parts of the self-check and compare them with the pass marks."""
    progress = progress or (lambda message: None)
    marks = thresholds["selfcheck"]
    thin = marks["thin"]
    reps = replicates or int(marks["replicates"])
    normal, sparse = [], []
    for law in TRUE_LAWS:
        progress(f"{law}: {reps} questions with {marks['seeds']} seeds")
        normal.append(run_law(law, reps, int(marks["seeds"]), float(marks["spread"])))
        progress(f"{law}: {reps} thin questions with {thin['seeds']} seeds")
        sparse.append(run_law(law, reps, int(thin["seeds"]), float(thin["spread"]), salt=1))
    mean_correct = float(np.mean([r.correct_rate for r in normal]))
    worst_wrong = max(r.wrong_rate for r in normal)
    worst_thin_wrong = max(r.wrong_rate for r in sparse)
    checks = {
        "mean_correct_rate": {
            "value": mean_correct,
            "mark": marks["min_correct_rate"],
            "passed": mean_correct >= marks["min_correct_rate"],
        },
        "max_wrong_rate": {
            "value": worst_wrong,
            "mark": marks["max_wrong_rate"],
            "passed": worst_wrong <= marks["max_wrong_rate"],
        },
        "thin_max_wrong_rate": {
            "value": worst_thin_wrong,
            "mark": thin["max_wrong_rate"],
            "passed": worst_thin_wrong <= thin["max_wrong_rate"],
        },
    }
    return {
        "passed": all(c["passed"] for c in checks.values()),
        "replicates": reps,
        "full_run": reps == int(marks["replicates"]),
        "checks": checks,
        "normal": [r.to_json() for r in normal],
        "thin": [r.to_json() for r in sparse],
    }


def render_selfcheck(result: dict) -> str:
    lines = ["# lattice-lab self-check", ""]
    verdict = "PASSED" if result["passed"] else "FAILED"
    scope = "" if result["full_run"] else " (reduced run: not the committed replicate count)"
    lines += [f"**{verdict}**{scope}, {result['replicates']} synthetic questions per law.", ""]
    lines += ["| Check | Value | Pass mark | |", "| --- | --- | --- | --- |"]
    for name, check in result["checks"].items():
        op = ">=" if name == "mean_correct_rate" else "<="
        lines.append(
            f"| {name} | {check['value']:.3f} | {op} {check['mark']} | "
            f"{'pass' if check['passed'] else 'FAIL'} |"
        )
    for part in ("normal", "thin"):
        lines += [
            "",
            f"## {'Thin data' if part == 'thin' else 'Normal data'}",
            "",
            "| True law | Correct | Wrong | Fragile | Inconclusive | None fits | Wrong laws |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in result[part]:
            wrong = ", ".join(f"{k} x{v}" for k, v in row["wrong_laws"].items()) or ""
            lines.append(
                f"| {row['law']} | {row['correct']} | {row['wrong']} | {row['fragile']} | "
                f"{row['inconclusive']} | {row['none_fits']} | {wrong} |"
            )
    return "\n".join(lines) + "\n"
