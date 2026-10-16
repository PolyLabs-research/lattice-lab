"""Which code produced a result: the version and git commit of lattice-lab, LatticeLife and
Kepler as installed (with a dirty flag for a working tree with uncommitted changes), and the
numerical stack. Written into every question's ledger entry, so a record can be rerun on the
same commits."""

from __future__ import annotations

import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path
from types import ModuleType


def git_state(path: Path) -> dict | None:
    """{"commit", "dirty"} of the git checkout holding `path`, or None outside one."""
    try:
        head = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if head.returncode != 0:
            return None
        status = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return {"commit": head.stdout.strip(), "dirty": bool(status.stdout.strip())}


def package_state(distribution: str, module: ModuleType) -> dict:
    """Version, commit, dirty flag and source of an installed package. A git install reports
    the commit it was built from; an editable or path install reports its checkout's state."""
    state: dict = {"version": None, "commit": None, "dirty": None, "source": None}
    try:
        dist = importlib.metadata.distribution(distribution)
        state["version"] = dist.version
        raw = dist.read_text("direct_url.json")
    except importlib.metadata.PackageNotFoundError:
        raw = None
    if raw:
        info = json.loads(raw)
        state["source"] = info.get("url")
        vcs = info.get("vcs_info")
        if vcs:
            state.update(commit=vcs.get("commit_id"), dirty=False)
        elif str(info.get("url", "")).startswith("file://"):
            found = git_state(Path(info["url"].removeprefix("file://")))
            if found:
                state.update(found)
    if state["commit"] is None and getattr(module, "__file__", None):
        found = git_state(Path(module.__file__).resolve().parent)
        if found:
            state.update(found)
    return state


def provenance() -> dict:
    import kepler
    import latticelife
    import numpy
    import scipy
    import sympy

    import lattice_lab

    return {
        "lattice_lab": package_state("lattice-lab", lattice_lab),
        "latticelife": package_state("latticelife", latticelife),
        "kepler": package_state("kepler", kepler),
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "sympy": sympy.__version__,
        "platform": platform.platform(),
    }
