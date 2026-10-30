#!/usr/bin/env bash
# Census stage 4, validation of the instrument (launch.py --job census-4-validate): fast4.py on
# 16 stage 3b/3c tori, compared with their records. A restart resumes (validate4 skips done tori).
#
#  1. packages, uv; DistQLDPC built at the pinned commit
#  2. the venv; self-test (tests/test_qec_census_4.py)
#  3. the hardware, committed once per machine
#  4. validate4.py run, committing its records as they arrive; then validate4.py compare
set -uo pipefail

W=/workspace
R=$W/lattice-lab
D=examples/qec-census-4/validation
BRANCH=ccr-ab9f0bb1-qb20sx
STATUS=$D/runpod-status.txt
RUNLOG=$W/s4v-run.log
DQ_COMMIT=8fe913e2ca79bda37cb755975b06b1b60416a418
exec > >(tee -a "$W/pod-run.log") 2>&1
echo "=== pod start $(date -u +%FT%TZ) pod=${RUNPOD_POD_ID:-?}"

export DEBIAN_FRONTEND=noninteractive
export UV_CACHE_DIR=$W/.uv-cache UV_PYTHON_INSTALL_DIR=$W/.uv-python UV_INSTALL_DIR=$W/.uv-bin
export PATH=$W/.uv-bin:$PATH
export DISTQLDPC=$W/tools/DistQLDPC
mkdir -p "$W/tools"

cd "$R" || exit 1
git config user.name "${POD_GIT_NAME:-lattice-lab census pod}"
git config user.email "${POD_GIT_EMAIL:-census-pod@users.noreply.github.com}"

push() {
  for t in 2 4 8 16; do
    git push -q -u origin "$BRANCH" && return 0
    # a merge, not a rebase: it leaves the files study.py is appending to untouched (no stash),
    # since nothing else commits to examples/qec-census-3d
    git pull -q --no-rebase --no-edit origin "$BRANCH" || git merge --abort 2>/dev/null
    sleep "$t"
  done
  echo "PUSH FAILED: commits stay on the pod until the next successful push"; return 1
}

commit() {  # commit the given paths if they changed (whole lines only), then push
  local msg=$1 f paths=(); shift
  for f in "$@"; do
    [ -e "$f" ] || continue
    [ -s "$f" ] && [ "$(tail -c1 "$f" | od -An -c | tr -d ' ')" != '\n' ] && return 0
    paths+=("$f")
  done
  [ ${#paths[@]} -gt 0 ] || return 0
  git add -- "${paths[@]}"
  if ! git diff --cached --quiet; then
    git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01LBDpbJNXFaJgMYrZEKJamq"
    push
  fi
}

records() { if [ -f "$D/records.jsonl" ]; then wc -l < "$D/records.jsonl"; else echo 0; fi; }
last_kind() { tail -1 "$D/ledger.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["kind"])'; }

status() {
  {
    echo "phase: $1"
    echo "detail: ${2:-}"
    echo "updated: $(date -u +%FT%TZ)"
    echo "pod: ${RUNPOD_POD_ID:-?}"
    echo "records: $(records) of 16 tori"
  } > "$STATUS"
  commit "Census stage 4 validation: pod status ($1)" "$STATUS"
}

hold() { echo "holding: $1"; sleep infinity; }

apt-get update -q && apt-get install -yq build-essential git curl zlib1g-dev ca-certificates python3 procps \
  || { echo "apt failed"; hold "apt"; }
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
command -v uv >/dev/null || { status failed "uv did not install"; hold "uv"; }

git fetch -q origin "$BRANCH" && [ -n "$(git log "origin/$BRANCH..HEAD" --oneline)" ] && push

mkdir -p "$D"
[ -f "$D/compare.json" ] && { status done "compare.json written"; hold "done"; }

# 1. DistQLDPC at the pinned commit
if [ ! -x "$DISTQLDPC/bin/distqldpc" ]; then
  status building "DistQLDPC $DQ_COMMIT"
  { [ -d "$DISTQLDPC/.git" ] || git clone -q https://github.com/guluchen/DistQLDPC "$DISTQLDPC"; } \
    && git -C "$DISTQLDPC" checkout -q "$DQ_COMMIT" \
    && (cd "$DISTQLDPC" && make -j"$(nproc)") > "$W/build-DistQLDPC.log" 2>&1 \
    || { status failed "DistQLDPC build (see /workspace/build-DistQLDPC.log)"; hold "distqldpc"; }
fi

# 2. the venv and the self-test
uv python install 3.13 && uv sync --frozen --group dev --group qec || { status failed "uv sync"; hold "sync"; }
status selftest
if ! uv run --no-sync pytest -q -rs tests/test_qec_census_4.py > "$W/selftest.log" 2>&1; then
  cat "$W/selftest.log"; status failed "tests/test_qec_census_4.py failed"; hold "tests"
fi
cat "$W/selftest.log"
grep -q SKIPPED "$W/selftest.log" && { status failed "a stage 4 test was skipped"; hold "skips"; }

# 3. the hardware, a new file when the machine changes
model=$(lscpu | grep 'Model name')
if ! grep -qlF "$model" "$D"/hardware-runpod*.txt 2>/dev/null; then
  out=$D/hardware-runpod.txt
  [ -e "$out" ] && out=$D/hardware-runpod-$(date -u +%Y%m%dT%H%M).txt
  { date -u +%FT%TZ; echo "pod: ${RUNPOD_POD_ID:-?}"; nproc
    lscpu | grep -E 'Model name|MHz|Thread|Core|Socket'; free -g | head -2; cc --version | head -1
    echo "DistQLDPC $(git -C "$DISTQLDPC" rev-parse HEAD)"; } > "$out"
  commit "Census stage 4 validation: hardware of the RunPod machine" "$out"
fi

# 4. validate, committing records as they arrive
workers=${S4_WORKERS:-$(nproc)}
run=""
on_stop() {
  commit "Census stage 4 validation: records ($(records) tori), pod stopping" "$D/records.jsonl"
  [ -n "$run" ] && kill "$run" 2>/dev/null; exit 0
}
trap on_stop TERM INT
status running "validate4.py run --workers $workers"
.venv/bin/python -u examples/qec-census-4/validate4.py run --workers "$workers" >> "$RUNLOG" 2>&1 &
run=$!
while kill -0 "$run" 2>/dev/null; do
  sleep 120 & wait $!
  commit "Census stage 4 validation: records ($(records) tori)" "$D/records.jsonl"
  status running "validate4.py run --workers $workers; last: $(tail -1 "$RUNLOG" | cut -c1-120)"
done
wait "$run"; code=$?
run=""
commit "Census stage 4 validation: records ($(records) tori), run ended" "$D/records.jsonl"
if [ "$code" = 0 ] && .venv/bin/python examples/qec-census-4/validate4.py compare > "$W/compare.json" 2>> "$RUNLOG"; then
  cp "$W/compare.json" "$D/compare.json"
  commit "Census stage 4 validation: compared with stage 3b/3c" "$D/compare.json"
  status done "compare.json written"
else
  status failed "validate4.py exited with $code, or compare failed (see /workspace/s4v-run.log)"
fi
hold "end"
