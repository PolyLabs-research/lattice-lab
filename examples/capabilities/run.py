"""
Every Kepler capability on real LatticeLife data.

    uv run python examples/capabilities/run.py [--workers 4]

Runs the experiments (records in examples/capabilities/data/, append-only and resumable: a second
run reuses them), analyses them, prints a summary and writes examples/capabilities/results.json.
docs/capabilities.md discusses the results. Every number here comes from a deterministic,
seeded simulation, so the same commits give the same results.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import kepler
import numpy as np
from kepler import (
    FSS_LAWS,
    GROWTH_LAWS,
    PROBABILITY_LAWS,
    TIME_LAWS,
    compare_distributions,
    compare_replicates,
    compare_sharing,
    find_integer_laws,
    find_invariants,
    find_xmin,
    fit,
    fit_distribution,
    fit_replicates,
    goodness_of_fit,
    identify,
    rank,
    separation,
)
from kepler.integer_laws import disagreement
from latticelife.config import DEFAULT_CONFIG_PATH, load_config
from latticelife.core.rules import Rule
from latticelife.experiments.damage import run_damage
from latticelife.experiments.harness import read_jsonl, single_species_session
from latticelife.experiments.objects import run_soups
from latticelife.experiments.observables import (
    damage_curves,
    event_times,
    object_sizes,
    survival,
)
from latticelife.experiments.periodicity import CycleDetector
from latticelife.experiments.series import count_series
from latticelife.experiments.sweeps import run_sweep

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CONFIG = load_config(DEFAULT_CONFIG_PATH)


def clean(obj):
    if isinstance(obj, dict):
        return {str(k): clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return round(v, 6) if math.isfinite(v) else None
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def matches(value, error, k=2.0, top=3):
    return [
        {
            "expression": m.expression,
            "z": round(m.z, 2),
            "p_chance": round(m.p_chance, 4),
            "named": m.named,
        }
        for m in identify(value, error, k)[:top]
    ]


def constants_of(f):
    """{constant: [value, standard error]} of a fit."""
    return {
        name: [value, error]
        for name, value, error in zip(f.param_names, f.params, f.stderr, strict=True)
    }


def summary_of(ranking):
    return [
        {"law": e.name, "delta_bic": e.delta_bic, "eligible": e.eligible, "reason": e.reason}
        for e in ranking.entries
    ]


# --- 1. Survival against density and size: binomial counts, window, finite-size scaling -----------

SURVIVAL_SIZES = [16, 32, 64]
SURVIVAL_DENSITIES = [
    0.02,
    0.04,
    0.06,
    0.08,
    0.1,
    0.12,
    0.15,
    0.2,
    0.25,
    0.3,
    0.4,
    0.5,
    0.6,
    0.65,
    0.7,
    0.72,
    0.74,
    0.76,
    0.78,
    0.8,
    0.82,
    0.85,
    0.9,
]
SURVIVAL_SEEDS = list(range(1, 31))


def survival_study(workers):
    out = DATA / "survival-life-square.jsonl"
    life = Rule.from_bs_string("B3/S23")
    list(
        run_sweep(
            CONFIG,
            life,
            "square",
            SURVIVAL_SIZES,
            SURVIVAL_DENSITIES,
            SURVIVAL_SEEDS,
            1000,
            str(out),
            workers,
        )
    )
    rows = survival(read_jsonl(out))
    result = {
        "rule": "B3/S23",
        "shape": "square",
        "steps": 1000,
        "seeds": len(SURVIVAL_SEEDS),
        "per_size": {},
    }
    for L in SURVIVAL_SIZES:
        mine = [r for r in rows if r.grid == L]
        rho = np.array([r.density for r in mine])
        k = np.array([r.survived for r in mine], dtype=float)
        n = np.array([r.runs for r in mine], dtype=float)
        ranking = rank(
            [fit(law, rho, k, likelihood="binomial", trials=n) for law in PROBABILITY_LAWS]
        )
        best = ranking.best.fit if ranking.best else None
        result["per_size"][L] = {
            "survived": {f"{d:g}": int(s) for d, s in zip(rho, k, strict=True)},
            "ranking": summary_of(ranking),
            "best": best.name if best else None,
            "constants": constants_of(best) if best else None,
        }

    # Finite-size scaling on each edge of the window, one fit over every size.
    rho = np.array([r.density for r in rows])
    size = np.array([r.size for r in rows])
    k = np.array([r.survived for r in rows], dtype=float)
    n = np.array([r.runs for r in rows], dtype=float)
    result["edges"] = {}
    for edge, keep in (("rising", rho <= 0.3), ("falling", rho >= 0.5)):
        x = {"rho": rho[keep], "L": size[keep]}
        fits = [fit(law, x, k[keep], likelihood="binomial", trials=n[keep]) for law in FSS_LAWS]
        ranking = rank(fits)
        entry = {
            "ranking": summary_of(ranking),
            "best": ranking.best.name if ranking.best else None,
        }
        if ranking.best:
            best = ranking.best.fit
            entry["constants"] = constants_of(best)
            entry["deviance_per_dof"] = best.rss / best.dof
            if "r" in best.param_names:
                entry["threshold_matches"] = matches(best.value("r"), best.error("r"))
            rival = next(
                (e.name for e in ranking.entries if e.name != best.name and e.eligible), None
            )
            if rival:
                design = separation(best, rival, x, likelihood="binomial", trials=n[keep])
                entry["design"] = {"rival": rival, **design.to_dict()}
        result["edges"][edge] = entry
    return result


# --- 2. Censored times: first repeats with an emulated cap ----------------------------------------


def censored_study():
    records = read_jsonl(
        HERE.parent / "lab-b2s34" / "records" / "settling-time-hexagon-B2S34-0.jsonl"
    )
    rows = [r for r in event_times(records, "first_repeat")]
    L = np.concatenate([[r.size] * len(r.times) for r in rows])
    T = np.concatenate([r.times for r in rows]).astype(float)
    exact = ~np.concatenate([r.is_censored for r in rows])
    # A shorter run stops at the cap and reports only that the first repeat comes later: runs are
    # deterministic, so capping complete records reproduces exactly what that run would record.
    cap = float(np.percentile(T[L == L.max()], 40))
    censored = (T > cap) | ~exact
    capped = np.minimum(T, cap)
    out = {
        "source": "examples/lab-b2s34 (B2/S34, hexagon)",
        "seeds_with_exact_times": int(exact.sum()),
        "rows": len(T),
        "cap": cap,
        "censored_share": float(censored.mean()),
        "censored_share_at_largest": float(censored[L == L.max()].mean()),
        "laws": {},
    }
    for law in ("logarithmic", "power"):
        full = fit(law, L, T, likelihood="censored", censored=~exact)
        honest = fit(law, L, capped, likelihood="censored", censored=censored)
        dropped = fit(law, L[~censored], T[~censored], likelihood="censored")
        out["laws"][law] = {
            name: constants_of(f)
            for name, f in (
                ("all_exact", full),
                ("capped_censored", honest),
                ("capped_dropped", dropped),
            )
        }
    ranking = rank(
        [fit(law, L, capped, likelihood="censored", censored=censored) for law in GROWTH_LAWS]
    )
    out["ranking_capped"] = summary_of(ranking)
    out["ranking_all_exact"] = summary_of(
        rank([fit(law, L, T, likelihood="censored", censored=~exact) for law in GROWTH_LAWS])
    )
    return out


# --- 3. One law across densities: is the growth rate shared? --------------------------------------

JOINT_SIZES = [8, 12, 16, 24, 32, 48, 64]
JOINT_DENSITIES = [0.3, 0.5, 0.7]


def joint_study(workers):
    out = DATA / "first-repeat-B2S34-hexagon.jsonl"
    rule = Rule.from_bs_string("B2/S34")
    list(
        run_sweep(
            CONFIG,
            rule,
            "hexagon",
            JOINT_SIZES,
            JOINT_DENSITIES,
            list(range(1, 21)),
            4000,
            str(out),
            workers,
        )
    )
    rows = event_times(read_jsonl(out), "first_repeat")
    L = np.concatenate([[r.size] * len(r.times) for r in rows])
    T = np.concatenate([r.times for r in rows]).astype(float)
    flags = np.concatenate([r.is_censored for r in rows])
    group = np.concatenate([[f"{r.density:g}"] * len(r.times) for r in rows])
    result = {
        "rule": "B2/S34",
        "shape": "hexagon",
        "censored": int(flags.sum()),
        "rows": len(T),
        "laws": {},
    }
    for law in ("logarithmic", "power"):
        sharing = compare_sharing(law, L, T, group, likelihood="censored", censored=flags)
        best = sharing.best.fit
        result["laws"][law] = {
            "verdict": sharing.note,
            "patterns": [e.to_dict() for e in sharing.entries],
            "constants": constants_of(best),
            "bic": best.bic,
        }
        for name in best.shared:
            result["laws"][law].setdefault("shared_matches", {})[name] = matches(
                best.value(name), best.error(name)
            )
    return result


# --- 4. Laws over time with seed-to-seed error bars -----------------------------------------------


def time_study(workers):
    result = {}
    seeds = list(range(1, 21))
    t = np.arange(400.0)
    Y = np.array(
        [
            np.array(count_series(CONFIG, "B2/S34", "hexagon", 64, 0.5, s, 400)["live"]) / 64**2
            for s in seeds
        ]
    )
    comparison = compare_replicates(TIME_LAWS, t, Y, resamples=100)
    best = fit_replicates(comparison.best, t, Y, resamples=200)
    result["density"] = {
        "rule": "B2/S34",
        "shape": "hexagon",
        "L": 64,
        "replicates": len(seeds),
        "shares": comparison.shares,
        "best": comparison.best,
        "constants": constants_of(best.fit),
        "naive_stderr": dict(zip(best.fit.param_names, best.naive_stderr, strict=True)),
    }
    out = DATA / "damage-B2S34-hexagon.jsonl"
    list(
        run_damage(
            CONFIG,
            Rule.from_bs_string("B2/S34"),
            "hexagon",
            [48],
            [0.5],
            seeds,
            300,
            str(out),
            workers,
        )
    )
    (row,) = damage_curves(read_jsonl(out))
    Yd = np.array(row.curves)
    td = np.arange(Yd.shape[1], dtype=float)
    comparison = compare_replicates(TIME_LAWS, td, Yd, resamples=100)
    best = fit_replicates(comparison.best, td, Yd, resamples=200)
    result["damage"] = {
        "rule": "B2/S34",
        "shape": "hexagon",
        "L": 48,
        "replicates": len(row.seeds),
        "shares": comparison.shares,
        "best": comparison.best,
        "constants": constants_of(best.fit),
        "naive_stderr": dict(zip(best.fit.param_names, best.naive_stderr, strict=True)),
    }
    for key in ("density", "damage"):
        constants = result[key]["constants"]
        for name in ("beta", "b"):
            if name in constants:
                result[key][f"{name}_matches"] = matches(*constants[name])
    return result


# --- 5. Distributions of object sizes and abundances ----------------------------------------------


def distribution_study(workers):
    out = DATA / "soups-life-square-64.jsonl"
    list(
        run_soups(
            CONFIG,
            Rule.from_bs_string("B3/S23"),
            "square",
            64,
            list(range(1, 121)),
            4000,
            0.35,
            str(out),
            workers,
        )
    )
    (row,) = object_sizes(read_jsonl(out))
    result = {
        "rule": "B3/S23",
        "L": 64,
        "soups": row.soups,
        "objects": row.objects,
        "distinct": len(row.abundances),
        "unidentified": row.unidentified,
    }
    for name, samples in (("populations", row.populations), ("abundances", row.abundances)):
        samples = np.asarray(samples, dtype=float)
        head = find_xmin(samples, "power_law", discrete=True, min_tail=10)
        fits = {
            f: fit_distribution(samples, f, head.xmin, discrete=True)
            for f in ("power_law", "truncated_power_law", "exponential", "lognormal")
        }
        best = max((f for f in fits.values() if f.success), key=lambda f: f.loglik - len(f.params))
        p, _ = goodness_of_fit(best, resamples=100, seed=1)
        entry = {
            "xmin": head.xmin,
            "n_tail": head.n_tail,
            "fits": {
                f: {
                    "params": g.params,
                    "stderr": g.stderr,
                    "loglik": g.loglik,
                    "aic": g.aic,
                    "ks": g.ks,
                }
                for f, g in fits.items()
            },
            "vuong_power_vs_lognormal": compare_distributions(
                fits["power_law"], fits["lognormal"]
            ).to_dict(),
            "vuong_exponential_vs_lognormal": compare_distributions(
                fits["exponential"], fits["lognormal"]
            ).to_dict(),
            "cutoff_test": compare_distributions(
                fits["power_law"], fits["truncated_power_law"]
            ).to_dict(),
            "best_by_aic": best.family,
            "goodness_of_fit_p": p,
            "histogram": {
                int(v): int(c) for v, c in zip(*np.unique(samples, return_counts=True), strict=True)
            },
        }
        if fits["power_law"].success:
            entry["alpha_matches"] = matches(
                fits["power_law"].params["alpha"], fits["power_law"].stderr["alpha"]
            )
        result[name] = entry
    return result


# --- 6. Exact integer laws: periods on n x n tori -------------------------------------------------


def _period(rule, n, cells=None, seed=1, density=0.5, cap=40000):
    session = single_species_session(
        CONFIG, Rule.from_bs_string(rule), "square", n, density if cells is None else 0.0, seed
    )
    if cells is not None:
        session.grid.occupancy[:] = 0
        for x, y in cells:
            session.grid.occupancy[y * n + x] = 1
    detector = CycleDetector()
    detector.observe(session.grid.occupancy, 0)
    for step in range(1, cap):
        session.step()
        found = detector.observe(session.grid.occupancy, step)
        if found is not None:
            return found[0]
    return None


def integer_study():
    glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
    sizes = list(range(6, 25))
    periods = [_period("B3/S23", n, glider) for n in sizes]
    glider_laws = find_integer_laws(sizes, periods)
    xor_sizes = list(range(3, 31))
    xor = {n: max(_period("B1357/S1357", n, seed=s) or 0 for s in (1, 2, 3)) for n in xor_sizes}
    powers = [n for n in xor_sizes if n & (n - 1) == 0]
    rest = [n for n in xor_sizes if n not in powers]
    xor_laws = find_integer_laws(rest, [xor[n] for n in rest])
    result = {
        "glider": {
            "rule": "B3/S23",
            "n": sizes,
            "period": periods,
            "laws": [law.to_dict() for law in glider_laws[:3]],
        },
        "xor": {
            "rule": "B1357/S1357",
            "n": xor_sizes,
            "period": [xor[n] for n in xor_sizes],
            "powers_of_two": {n: xor[n] for n in powers},
            "laws": [law.to_dict() for law in xor_laws[:5]],
        },
    }
    if len(xor_laws) > 1:
        result["xor"]["first_disagreement"] = disagreement(xor_laws[:2], max(rest) + 1)
    if xor_laws:
        law = xor_laws[0]
        check = [n for n in range(31, 36) if n & (n - 1)]
        result["xor"]["held_out"] = {
            n: {"predicted": int(law(n)), "measured": _period("B1357/S1357", n, cap=200000)}
            for n in check
            if law(n) is not None and law(n) <= 150000
        }
    return result


# --- 7. Conserved quantities ----------------------------------------------------------------------


def invariant_study():
    result = {}
    rules = [
        ("B3/S23", "square", 8),
        ("B36/S23", "square", 8),
        ("B2/S34", "hexagon", 6),
        ("B1357/S1357", "square", 8),
    ]
    for rule, shape, degree in rules:
        known = [
            {"live": 1, "births": -1, "deaths": 1},
            {"live": 1, **{f"live_{k}": -1 for k in range(degree + 1)}},
            {"live": 1, **{f"dead_{k}": 1 for k in range(degree + 1)}},
            {
                "live": -degree,
                **{f"live_{k}": k for k in range(degree + 1)},
                **{f"dead_{k}": k for k in range(degree + 1)},
            },
        ]
        entry = {}
        # A wrapped hexagon grid needs an even width, so odd tori are tried on the square only.
        splits = (
            (("all", [12, 13, 16, 17]), ("even", [12, 16]), ("odd", [13, 17]))
            if shape == "square"
            else (("all", [12, 14, 16, 18]),)
        )
        for label, sizes in splits:
            runs = [
                count_series(CONFIG, rule, shape, n, 0.4, s, 200) for n in sizes for s in (1, 2, 3)
            ]
            found = find_invariants(runs, modulus=2)
            entry[label] = {
                "sizes": sizes,
                "runs": found.runs,
                "rank": found.rank,
                "exact": len(found.exact),
                "known_identities_found": all(found.implies(k) for k in known),
                "beyond_bookkeeping": found.beyond(known),
                "mod_2": [str(i) for i in found.modular],
            }
        result[f"{rule} {shape}"] = entry
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--only", nargs="*", default=None, help="run only these studies")
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    studies = {
        "survival": lambda: survival_study(args.workers),
        "censored": censored_study,
        "joint": lambda: joint_study(args.workers),
        "time": lambda: time_study(args.workers),
        "distributions": lambda: distribution_study(args.workers),
        "integer": integer_study,
        "invariants": invariant_study,
    }
    path = HERE / "results.json"
    results = json.loads(path.read_text()) if path.exists() else {}
    for name, study in studies.items():
        if args.only and name not in args.only:
            continue
        print(f"== {name}", flush=True)
        results[name] = clean(study())
        results["kepler"] = kepler.__version__
        path.write_text(json.dumps(results, indent=1) + "\n")
        print(json.dumps(results[name])[:2000], flush=True)


if __name__ == "__main__":
    main()
