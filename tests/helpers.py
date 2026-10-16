"""Shared test helpers: observations with chosen values, and an experimenter that returns them."""

import math

from lattice_lab.experiment import Measurement, Observation


def obs(label, y, rel=0.08, seeds=20, complete=True):
    """A complete observation of median `y` with a ~`rel` relative standard error."""
    if not complete:
        return Observation(
            label, float(label), None, None, None, seeds, seeds, False, 63999, "unsettled"
        )
    # A spread whose median standard error is `rel`: 1.2533 * spread / sqrt(seeds) = rel.
    spread = rel * math.sqrt(seeds) / 1.2533
    return Observation(
        label,
        float(label),
        y,
        y * math.exp(-1.96 * rel),
        y * math.exp(1.96 * rel),
        seeds,
        0,
        True,
        None,
        "",
        spread,
        spread * y,
    )


class TableExperimenter:
    """Returns observations from a function of the size; `unsettled` sizes come back
    incomplete, as if their seeds never repeated within max_cap."""

    def __init__(self, f, rel=0.08, unsettled=()):
        self.f = f
        self.rel = rel
        self.unsettled = set(unsettled)
        self.calls = []

    def offset(self):
        return 0

    def measure(self, labels, budget):
        self.calls.append(list(labels))
        return Measurement(
            [
                obs(label, self.f(float(label)), self.rel, complete=label not in self.unsettled)
                for label in labels
            ]
        )
