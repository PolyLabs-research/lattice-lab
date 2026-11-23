#!/usr/bin/env bash
# A registered study on a rented machine: set up, test, run. By default part 2 of the scale-up
# test (sides 2048 and 4096).
#
#   bash pod-run.sh BRANCH COMMIT WORKERS [STUDY_FOLDER] [TEST_FILES]
#
# Clones lattice-lab (public, so no token) at COMMIT of BRANCH, installs the locked versions,
# runs the study's own tests (which check that the code is as registered), records the
# hardware, and runs the registered study. A second start resumes a run that was cut short.
# /root/run/STATE says where it is: setup, selftest, running, done, or failed with the reason.
# Nothing is pushed from here: the machine that started this pulls the ledger and the records.
set -uo pipefail
BRANCH=${1:?branch}
COMMIT=${2:?commit}
WORKERS=${3:?workers}
D=${4:-examples/scale-up-sizes-large}
TESTS=${5:-tests/test_scale_up_sizes.py}
W=/root/run
mkdir -p "$W"
exec > >(tee -a "$W/pod-run.log") 2>&1
state() { echo "$*" > "$W/STATE"; echo "=== $(date -u +%FT%TZ) $*"; }
die() { state "failed: $*"; exit 1; }

state setup
export DEBIAN_FRONTEND=noninteractive
command -v rsync > /dev/null && command -v git > /dev/null && command -v curl > /dev/null \
  || { apt-get -qq update && apt-get -qq install -y rsync git curl ca-certificates > /dev/null; } \
  || die "apt"
export UV_INSTALL_DIR=/root/.uv-bin PATH=/root/.uv-bin:$PATH
command -v uv > /dev/null || curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
command -v uv > /dev/null || die "uv did not install"
cd "$W" || die "no $W"
[ -d lattice-lab ] || git clone -q --branch "$BRANCH" https://github.com/PolyLabs-research/lattice-lab.git \
  || die "clone"
cd lattice-lab || die "no checkout"
[ "$(git rev-parse HEAD)" = "$COMMIT" ] || die "the branch is at $(git rev-parse --short HEAD), not ${COMMIT:0:8}"
uv sync --frozen --group dev -q || die "uv sync"
{
  date -u
  grep -m1 'model name' /proc/cpuinfo
  echo "cpu quota: $(cat /sys/fs/cgroup/cpu.max 2> /dev/null)  nproc: $(nproc)"
  free -g | head -2
} > "$W/hardware.txt"

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
state selftest
# shellcheck disable=SC2086  # TESTS is a list of files
uv run --no-sync pytest -q $TESTS || die "the study's tests"

if grep -q '"run_started"' "$D/ledger.jsonl"; then step=resume; else step=run; fi
state "running ($step, $WORKERS workers)"
uv run --no-sync python "$D/study.py" "$step" --workers "$WORKERS" > "$W/verdict.json" || die "the study stopped"
state done
