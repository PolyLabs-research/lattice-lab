"""
A registered universality test: is the settling time of a soup Gumbel-distributed, with the
same shape, on every lattice?

    uv run python examples/settling-universality/select.py      # the rules (selection.jsonl)
    uv run python examples/settling-universality/study.py fit   # small tori (fit-records.jsonl)
    uv run python examples/settling-universality/study.py register
    uv run python examples/settling-universality/study.py run --workers 4
    uv run lattice-lab verify --lab examples/settling-universality

Eight rules, two per lattice (square, hexagon, triangle with edge and with edge+vertex
neighbours), drawn at random and kept by criteria that look only at whether they settle
(select.py). For each, the six library laws are fitted to the median settling time on tori of
8 to 64 (40 seeds), and their medians predicted at 128, 256 and 512 (100 seeds). Two mechanisms
(lattice_lab.extremes) predict the fluctuations from those fits, with no constant fitted to the
fluctuations: light-tailed extreme values (Gumbel) from the logarithmic law's slope, and heavy-
tailed ones (Frechet) from the power law's exponent.

Two predictions concern every rule at once, measured at the three large sizes only:

- U1, the shape: Kelly's quantile skewness is one constant shared by all eight rules (Kepler's
  compare_sharing on the per-size values, grouped by rule), equal to the Gumbel value 0.2215.
- U2, the amplitude ratio: the interquartile range divided by the slope of the median in ln L is
  one constant shared by all eight, equal to 1.5725 / 2 = 0.786 for the largest of ~L^2 times.

Kepler's identify is then asked, without being told the answer, what known numbers the shared
values match.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from kepler import compare_sharing, identify
from latticelife.experiments.observables import median_transient
from scipy import stats

from lattice_lab import extremes
from lattice_lab.analysis import fit_laws, judge_prediction, pooled_spread, prediction_body
from lattice_lab.experiment import LatticeExperimenter, observation_from_row, question_config
from lattice_lab.question import Question
from lattice_lab.study import Study, main

HERE = Path(__file__).resolve().parent
FIT_SIZES = [8, 12, 16, 24, 32, 48, 64]
FIT_SEEDS = 40
TEST_SIZES = [128, 256, 512]
TEST_SEEDS = 100
ALPHA = 0.01
LATTICES = {
    "square": ("square", None),
    "hexagon": ("hexagon", None),
    "triangle-edge": ("triangle", "edge"),
    "triangle-edge+vertex": ("triangle", "edge+vertex"),
}
FIT_RECORDS = HERE / "fit-records.jsonl"


def rules() -> list[tuple[str, str]]:
    chosen = json.loads((HERE / "selected.json").read_text())
    out = [(lattice, rule) for lattice in LATTICES for rule in chosen[lattice]["rules"]]
    texts = [question_for(lat, rule, 1).rule_text for lat, rule in out]
    if len(set(texts)) != len(texts):  # records are told apart by rule text and shape
        raise ValueError("two selected rules write the same rule text")
    return out


def slug(lattice: str, rule: str) -> str:
    return f"{lattice}-{rule}".replace("/", "_").replace(",", ".").replace("+", "p")


def question_for(lattice: str, rule: str, seeds: int) -> Question:
    shape, mode = LATTICES[lattice]
    return Question(
        id=slug(lattice, rule),
        rule=rule,
        shape=shape,
        triangle_mode=mode,
        density=0.5,
        seeds=seeds,
        fit_sizes=tuple(FIT_SIZES),
        heldout_pool=tuple(TEST_SIZES),
        cap=2000,
        max_cap=64000,
        budget_cell_steps=2e12,
    )


def _matching(records: list[dict], lattice: str, rule: str) -> list[dict]:
    q = question_for(lattice, rule, 1)
    shape, mode = LATTICES[lattice]
    return [
        r
        for r in records
        if r["rule"] == q.rule_text
        and r["shape"] == shape
        and (r.get("triangle_mode") or None) == (mode if shape == "triangle" else None)
    ]


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def run_fit_stage(workers: int) -> None:
    """The small tori the laws are fitted to, before anything is registered."""
    for lattice, rule in rules():
        q = question_for(lattice, rule, FIT_SEEDS)
        LatticeExperimenter(q, FIT_RECORDS, question_config(q), workers=workers).measure(
            FIT_SIZES, q.budget_cell_steps
        )
        print(f"fit stage: {lattice} {rule}", file=sys.stderr, flush=True)


def fit_observations(lattice: str, rule: str):
    rows = median_transient(_matching(_read(FIT_RECORDS), lattice, rule))
    return [observation_from_row(r) for r in rows]


def fits(lattice: str, rule: str):
    q = question_for(lattice, rule, FIT_SEEDS)
    return {f.name: f for f in fit_laws(q.laws, fit_observations(lattice, rule), "log")}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def question() -> dict:
    return {
        "id": "settling-time-universality",
        "title": "Is the settling time Gumbel-distributed, with one shape on every lattice?",
        "rules": [{"lattice": lat, "rule": rule} for lat, rule in rules()],
        "selection": {
            "script": "select.py",
            "log": "selection.jsonl",
            "log_sha256": _sha256(HERE / "selection.jsonl"),
            "selected_sha256": _sha256(HERE / "selected.json"),
        },
        "fit_stage": {
            "sizes": FIT_SIZES,
            "seeds": FIT_SEEDS,
            "records": FIT_RECORDS.name,
            "records_sha256": _sha256(FIT_RECORDS),
        },
        "test_sizes": TEST_SIZES,
        "test_seeds": TEST_SEEDS,
        "density": 0.5,
        "alpha": ALPHA,
        "quantity": "settling time: the generation each seed's final cycle begins (or the grid "
        "empties); medians for the laws, every seed's for the mechanisms, each first jittered "
        "uniformly within half a generation (seeded) so that quantiles of whole numbers are not "
        "biased where the spread is a few generations",
    }


def predictions() -> list[dict]:
    out = []
    for lattice, rule in rules():
        found = fits(lattice, rule)
        tag = {"lattice": lattice, "rule": rule}
        for law_fit in found.values():
            out.append(
                {
                    "role": "law",
                    **tag,
                    **prediction_body(law_fit, TEST_SIZES),
                    "decision": "the loop's joint held-out test of the medians: rejected when "
                    f"p < {ALPHA}",
                }
            )
        a, a_se = found["logarithmic"].params[0], found["logarithmic"].stderr[0]
        out.append(
            {
                "role": "mechanism",
                "mechanism": "gumbel",
                **tag,
                "a": a,
                "a_se": a_se,
                "iqr": extremes.GUMBEL_IQR * a / 2,
                "iqr_se": extremes.GUMBEL_IQR * a_se / 2,
                "kelly_skewness": extremes.GUMBEL_KELLY,
                "decision": "consistent when, each two-sided at 1%: the interquartile range "
                "averaged over the test sizes (inverse-variance weights) equals iqr; its slope "
                "against ln L is 0; Kelly's skewness averaged the same way equals "
                "kelly_skewness",
            }
        )
        b, b_se = found["power"].params[1], found["power"].stderr[1]
        body = {"role": "mechanism", "mechanism": "frechet", **tag, "b": b, "b_se": b_se}
        if b > 0:
            alpha_shape, alpha_se = 2 / b, 2 * b_se / b**2
            body.update(
                alpha=alpha_shape,
                alpha_se=alpha_se,
                **extremes.frechet_with_errors(alpha_shape, alpha_se),
                decision="consistent when, each two-sided at 1%: the interquartile range over "
                "the median, averaged over the test sizes, equals iqr_over_median; Kelly's "
                "skewness, averaged the same way, equals kelly_skewness",
            )
        else:
            body["decision"] = "no prediction: the power law does not grow"
        out.append(body)
    out.append(
        {
            "role": "universality",
            "claim": "U1 shape",
            "kelly_skewness": extremes.GUMBEL_KELLY,
            "decision": "confirmed when Kepler's compare_sharing (law 'constant' fitted to the "
            "per-size Kelly skewness at the test sizes, grouped by rule, bootstrap errors as "
            "absolute sigmas) prefers one shared constant and its likelihood-ratio p against "
            "a constant per rule is at least 0.01, and the shared constant equals "
            "kelly_skewness (two-sided at 1%)",
        }
    )
    out.append(
        {
            "role": "universality",
            "claim": "U2 amplitude ratio",
            "iqr_per_slope": extremes.gumbel_iqr_per_slope(2),
            "decision": "per rule, R = (interquartile range averaged over the test sizes) / "
            "(weighted slope of the test-size medians against ln L), its error from both; rules "
            "whose slope is not 3 errors above zero are left out. Confirmed when the rules' R "
            "share one value (chi-square of R about their weighted mean, p >= 0.01) and that "
            "value equals iqr_per_slope (two-sided at 1%)",
        }
    )
    return out


def execute(path: Path, workers: int) -> None:
    for lattice, rule in rules():
        q = question_for(lattice, rule, TEST_SEEDS)
        print(f"test sizes: {lattice} {rule}", file=sys.stderr, flush=True)
        LatticeExperimenter(q, path, question_config(q), workers=workers).measure(
            TEST_SIZES, q.budget_cell_steps
        )


def _mechanism_tests(p: dict, per_size: dict) -> dict:
    sizes = sorted(per_size)

    def col(key):
        return np.array([per_size[n][key] for n in sizes])

    if p["mechanism"] == "gumbel":
        slope, slope_err = extremes.weighted_slope(np.log(sizes), col("iqr"), col("iqr_error"))
        return {
            "iqr": extremes.z_test(
                *extremes.weighted_mean(col("iqr"), col("iqr_error")), p["iqr"], p["iqr_se"]
            ),
            "iqr_trend": extremes.z_test(slope, slope_err, 0.0),
            "kelly_skewness": extremes.z_test(
                *extremes.weighted_mean(col("kelly_skewness"), col("kelly_skewness_error")),
                p["kelly_skewness"],
            ),
        }
    if "alpha" not in p:
        return {}
    return {
        "iqr_over_median": extremes.z_test(
            *extremes.weighted_mean(col("iqr_over_median"), col("iqr_over_median_error")),
            p["iqr_over_median"],
            p["iqr_over_median_se"],
        ),
        "kelly_skewness": extremes.z_test(
            *extremes.weighted_mean(col("kelly_skewness"), col("kelly_skewness_error")),
            p["kelly_skewness"],
            p["kelly_skewness_se"],
        ),
    }


def decide(rows: list[dict], registered: list[dict]) -> dict:
    per_rule = {}
    for lattice, rule in rules():
        key = f"{lattice} {rule}"
        mine = _matching(rows, lattice, rule)
        transient_rows = median_transient(mine)
        new = [observation_from_row(r) for r in transient_rows]
        pooled = pooled_spread([*fit_observations(lattice, rule), *new])
        complete = {int(r.grid): r.settling_times for r in transient_rows if r.complete}
        per_size = extremes.fluctuations(complete, jitter=True)
        laws, mechanisms = {}, {}
        for p in registered:
            if p.get("lattice") != lattice or p.get("rule") != rule:
                continue
            if p["role"] == "law":
                test = judge_prediction(p, new, "log", ALPHA, pooled)
                laws[p["law"]] = {k: v for k, v in test.items() if k != "points"}
            elif p["role"] == "mechanism":
                tests = _mechanism_tests(p, per_size) if len(per_size) == len(TEST_SIZES) else {}
                mechanisms[p["mechanism"]] = {
                    "tests": tests,
                    "status": (
                        "consistent"
                        if tests and all(t["passes"] for t in tests.values())
                        else ("untested" if not tests else "rejected")
                    ),
                }
        per_rule[key] = {
            "laws": laws,
            "survivors": sorted(n for n, t in laws.items() if t["status"] == "consistent"),
            "mechanisms": mechanisms,
            "fluctuations": per_size,
            "unsettled": [o.label for o in new if not o.complete],
        }
    return {"rules": per_rule, **universality(per_rule, registered)}


def universality(per_rule: dict, registered: list[dict]) -> dict:
    claims = {p["claim"]: p for p in registered if p["role"] == "universality"}
    full = {k: v for k, v in per_rule.items() if len(v["fluctuations"]) == len(TEST_SIZES)}
    # U1: one Kelly skewness for every rule
    x, y, err, group = [], [], [], []
    for key, v in full.items():
        for n, f in v["fluctuations"].items():
            x.append(float(n))
            y.append(f["kelly_skewness"])
            err.append(f["kelly_skewness_error"])
            group.append(key)
    sharing = compare_sharing("constant", x, y, group, sigma=err, absolute_sigma=True)
    shared = sharing.entry(["a"])
    value, value_se = shared.fit.params[0], shared.fit.stderr[0]
    u1 = {
        "sharing": sharing.to_dict(),
        "shared_value": value,
        "shared_error": value_se,
        "test": extremes.z_test(value, value_se, claims["U1 shape"]["kelly_skewness"]),
        "identify": [m.to_dict() for m in identify(value, value_se)],
    }
    u1["status"] = (
        "confirmed"
        if sharing.best is not None
        and list(sharing.best.shared) == ["a"]
        and (shared.p_value is None or shared.p_value >= ALPHA)
        and u1["test"]["passes"]
        else "refuted"
    )
    # U2: one interquartile range per unit slope for every rule
    ratios, left_out = {}, []
    for key, v in full.items():
        sizes = sorted(v["fluctuations"])
        f = [v["fluctuations"][n] for n in sizes]
        slope, slope_err = extremes.weighted_slope(
            np.log(sizes), [g["median"] for g in f], [g["median_error"] for g in f]
        )
        iqr, iqr_err = extremes.weighted_mean([g["iqr"] for g in f], [g["iqr_error"] for g in f])
        if slope <= 3 * slope_err:
            left_out.append(key)
            continue
        r = iqr / slope
        ratios[key] = {
            "slope": slope,
            "slope_error": slope_err,
            "iqr": iqr,
            "iqr_error": iqr_err,
            "ratio": r,
            "ratio_error": abs(r) * math.hypot(iqr_err / iqr, slope_err / slope),
        }
    u2 = {"per_rule": ratios, "left_out": left_out}
    if len(ratios) >= 2:
        values = np.array([v["ratio"] for v in ratios.values()])
        errors = np.array([v["ratio_error"] for v in ratios.values()])
        mean, mean_err = extremes.weighted_mean(values, errors)
        chi2 = float(np.sum(((values - mean) / errors) ** 2))
        p_same = float(stats.chi2.sf(chi2, len(values) - 1))
        test = extremes.z_test(mean, mean_err, claims["U2 amplitude ratio"]["iqr_per_slope"])
        u2.update(
            shared_value=mean,
            shared_error=mean_err,
            chi2=chi2,
            p_same=p_same,
            test=test,
            identify=[m.to_dict() for m in identify(mean, mean_err)],
            status="confirmed" if p_same >= ALPHA and test["passes"] else "refuted",
        )
    else:
        u2["status"] = "untested"
    return {"U1 shape": u1, "U2 amplitude ratio": u2}


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    if sys.argv[1:2] == ["fit"]:
        workers = int(sys.argv[3]) if sys.argv[2:3] == ["--workers"] else 2
        run_fit_stage(workers)
    else:
        main(STUDY)
