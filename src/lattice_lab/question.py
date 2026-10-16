"""A question the loop answers: "how does quantity y depend on setting x" for one rule on one
lattice, with the sizes the fit may see, the pool held-out sizes are chosen from, and the limits
on seeds, caps, rounds and compute.

Version 1 asks one kind of question, `settling_time`: the median generation at which a soup's
final cycle begins, against the torus size L (for a rectangle, the square root of its cells).
The quantity is a field so later kinds (survival against density, damage, relaxation) can join
without changing what a question file means.

Questions are TOML files:

    id = "settling-time-hexagon-B2S34"
    quantity = "settling_time"
    rule = "B2/S34"
    shape = "hexagon"
    density = 0.5
    seeds = 20
    fit_sizes = [8, 10, 12, 16, 20, 24, 32]
    heldout_pool = [40, 48, 64, 96, 128]

Everything else has a default (see `Question`).
"""

from __future__ import annotations

import math
import re
import tomllib
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from kepler import GROWTH_LAWS, LAWS
from latticelife.core.geometries import SHAPES, validate_dimensions
from latticelife.core.rules import Rule
from latticelife.experiments.harness import GridLabel, grid_dimensions, grid_sort_key, parse_grid

QUANTITIES = ("settling_time",)
SPACES = ("auto", "linear", "log")


class QuestionError(ValueError):
    """A question file that cannot be asked as written."""


@dataclass(frozen=True)
class Question:
    id: str
    rule: str
    shape: str
    fit_sizes: tuple[GridLabel, ...]
    heldout_pool: tuple[GridLabel, ...]
    quantity: str = "settling_time"
    triangle_mode: str | None = None  # "edge" or "edge+vertex", triangle lattices only
    density: float = 0.5
    seeds: int = 20
    heldout_per_round: int = 3
    cap: int = 2000  # generations a run may take before it counts as not yet settled
    max_cap: int = 64000  # the largest cap an unsettled seed is rerun with
    laws: tuple[str, ...] = GROWTH_LAWS
    space: str = "auto"  # fit space: log when every value is positive, else linear
    max_rounds: int = 2
    budget_cell_steps: float = 2e11  # generations x cells the whole question may spend
    # A candidate whose held-out test has p below this is rejected. 0.01, not 0.05: each round
    # tests every law again, and a true law wrongly rejected leaves room for a wrong one.
    alpha: float = 0.01
    decisive_bic: float = 6.0  # a law is named only when no rival as simple is this close
    equivalence: float = 0.5  # a richer rival within +-50% of it everywhere does not block it
    contender_window: float = 10.0  # laws this close to the best BIC steer the planner
    min_points: int = 4  # complete sizes needed before anything is fitted
    note: str = ""
    extra: dict = field(default_factory=dict)  # unknown keys, kept for the record

    def __post_init__(self) -> None:
        problems = self.problems()
        if problems:
            raise QuestionError("; ".join(problems))

    def problems(self) -> list[str]:
        out: list[str] = []
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", self.id or ""):
            out.append(f"id {self.id!r} must be letters, digits, '.', '_' or '-'")
        if self.quantity not in QUANTITIES:
            out.append(f"quantity must be one of {QUANTITIES} (got {self.quantity!r})")
        if self.shape not in SHAPES:
            out.append(f"shape must be one of {SHAPES} (got {self.shape!r})")
        try:
            Rule.from_bs_string(self.rule)
        except ValueError as exc:
            out.append(f"rule: {exc}")
        if self.shape == "triangle" and self.triangle_mode not in ("edge", "edge+vertex"):
            out.append("a triangle question needs triangle_mode = 'edge' or 'edge+vertex'")
        if not 0.0 <= self.density <= 1.0:
            out.append(f"density must be in [0, 1] (got {self.density})")
        for name in ("seeds", "heldout_per_round", "cap", "max_cap", "max_rounds", "min_points"):
            if getattr(self, name) < 1:
                out.append(f"{name} must be at least 1")
        if self.max_cap < self.cap:
            out.append("max_cap must be at least cap")
        if self.space not in SPACES:
            out.append(f"space must be one of {SPACES} (got {self.space!r})")
        unknown = [law for law in self.laws if law not in LAWS]
        if unknown:
            out.append(f"unknown laws {unknown}; known: {', '.join(LAWS)}")
        several = [law for law in self.laws if law in LAWS and LAWS[law].variables != ("x",)]
        if several:
            out.append(
                f"laws {several} take several variables; a question asks about one (torus size)"
            )
        if not self.laws:
            out.append("laws is empty")
        if not 0 < self.alpha < 1:
            out.append("alpha must be between 0 and 1")
        if not self.equivalence > 0:
            out.append("equivalence must be positive")
        if len(set(self.fit_sizes)) != len(self.fit_sizes):
            out.append("fit_sizes repeats a size")
        if set(self.fit_sizes) & set(self.heldout_pool):
            out.append("a size cannot be both fitted and held out")
        if len(self.fit_sizes) < self.min_points:
            out.append(f"fit_sizes needs at least min_points = {self.min_points} sizes")
        if not self.heldout_pool:
            out.append("heldout_pool is empty")
        if not math.isfinite(self.budget_cell_steps) or self.budget_cell_steps <= 0:
            out.append("budget_cell_steps must be positive")
        if self.shape in SHAPES:
            mode = self.triangle_mode or "edge+vertex"
            for size in (*self.fit_sizes, *self.heldout_pool):
                width, height = grid_dimensions(size)
                try:
                    validate_dimensions(self.shape, width, height, True, mode)
                except ValueError as exc:
                    out.append(f"size {size}: {exc}")
        return out

    @property
    def rule_text(self) -> str:
        """The rule as LatticeLife writes it in records for this lattice."""
        from latticelife.core.geometries import max_degree

        n = max_degree(self.shape, self.triangle_mode or "edge+vertex")
        return Rule.from_bs_string(self.rule).to_bs_string(n)

    def title(self) -> str:
        mode = f" ({self.triangle_mode})" if self.shape == "triangle" else ""
        return (
            f"How does settling time grow with torus size? {self.rule_text} on {self.shape}"
            f"{mode} tori, density {self.density:g}"
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["fit_sizes"] = list(self.fit_sizes)
        data["heldout_pool"] = list(self.heldout_pool)
        data["laws"] = list(self.laws)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Question:
        known = {f.name for f in fields(cls)} - {"extra"}
        missing = [k for k in ("id", "rule", "shape", "fit_sizes", "heldout_pool") if k not in data]
        if missing:
            raise QuestionError(f"missing {', '.join(missing)}")
        values = {k: v for k, v in data.items() if k in known}
        values["extra"] = {
            **(data.get("extra") or {}),
            **{k: v for k, v in data.items() if k not in known and k != "extra"},
        }
        try:
            values["fit_sizes"] = _sizes(data["fit_sizes"])
            values["heldout_pool"] = _sizes(data["heldout_pool"])
        except ValueError as exc:
            raise QuestionError(str(exc)) from None
        if "laws" in values:
            values["laws"] = tuple(values["laws"])
        for name in (
            "density",
            "alpha",
            "decisive_bic",
            "equivalence",
            "contender_window",
            "budget_cell_steps",
        ):
            if name in values:
                values[name] = float(values[name])
        return cls(**values)

    @classmethod
    def from_toml(cls, path: str | Path) -> Question:
        try:
            data = tomllib.loads(Path(path).read_text())
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise QuestionError(f"{path}: {exc}") from None
        return cls.from_dict(data)


def _sizes(values) -> tuple[GridLabel, ...]:
    labels = [parse_grid(v) for v in values]
    return tuple(sorted(labels, key=grid_sort_key))


def size_of(label: GridLabel) -> float:
    """The x a size is plotted and fitted at: the side of a square torus with as many cells."""
    width, height = grid_dimensions(label)
    return math.sqrt(width * height)


def cells_of(label: GridLabel) -> int:
    width, height = grid_dimensions(label)
    return width * height
