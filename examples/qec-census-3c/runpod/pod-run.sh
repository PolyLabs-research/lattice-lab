#!/usr/bin/env bash
# Census stage 3c on a RunPod CPU pod (docs/runpod-setup.md). The pod's start command clones or
# updates the repository on the volume, then runs this script, at every start; so a pod restart
# resumes the run by itself. Each step is safe to repeat.
#
#  1. packages, and uv with its cache and Python on the volume
#  2. the venv (uv sync --frozen: the locked versions)
#  3. self-test: the stage 3b and 3c tests, and study.consistency() == []
#  4. the hardware, committed once (a second file if the hardware changes)
#  5. study.py resume --workers 4, as registered, with records committed as they arrive
#
# Progress is pushed to the branch: the records and ledger, and runpod-status.txt (the phase, the
# torus in progress, the record count). The full log is /workspace/pod-run.log on the pod.
set -uo pipefail

W=/workspace
R=$W/lattice-lab
D=examples/qec-census-3c
BRANCH=ccr-ab9f0bb1-qb20sx
STATUS=$D/runpod-status.txt
RUNLOG=$W/s3c-run.log
# the RunPod console shows the container output, so the log goes there as well as to the volume
exec > >(tee -a "$W/pod-run.log") 2>&1
echo "=== pod start $(date -u +%FT%TZ) pod=${RUNPOD_POD_ID:-?}"

export DEBIAN_FRONTEND=noninteractive
export UV_CACHE_DIR=$W/.uv-cache UV_PYTHON_INSTALL_DIR=$W/.uv-python UV_INSTALL_DIR=$W/.uv-bin
export PATH=$W/.uv-bin:$PATH
export SPOTCHECK_TOOLS=$W/tools DISTQLDPC=$W/tools/DistQLDPC

cd "$R" || exit 1
git config user.name "${POD_GIT_NAME:-lattice-lab census pod}"
git config user.email "${POD_GIT_EMAIL:-census-pod@users.noreply.github.com}"

push() {  # after a refused push, rebase onto the branch: the pod's commits touch only its own files
  for t in 2 4 8 16; do
    git push -q -u origin "$BRANCH" && return 0
    git pull -q --rebase --autostash origin "$BRANCH" || git rebase --abort 2>/dev/null
    sleep "$t"
  done
  echo "PUSH FAILED: commits stay on the volume until the next successful push"; return 1
}

commit() {  # commit the given paths if they changed, then push
  local msg=$1 f; shift
  for f in "$@"; do  # a file being appended to is committed only once it ends in a whole line
    [ -s "$f" ] && [ "$(tail -c1 "$f" | od -An -c | tr -d ' ')" != '\n' ] && return 0
  done
  git add -- "$@"
  if ! git diff --cached --quiet; then
    git commit -q -m "$msg

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01LBDpbJNXFaJgMYrZEKJamq"
    push
  fi
}

status() {  # phase [detail]: write and commit runpod-status.txt
  {
    echo "phase: $1"
    echo "detail: ${2:-}"
    echo "updated: $(date -u +%FT%TZ)"
    echo "pod: ${RUNPOD_POD_ID:-?}"
    echo "records: $(wc -l < "$D/records.jsonl")"
    echo "torus: $(grep -E '^[0-9]+x[0-9]+: ' "$RUNLOG" 2>/dev/null | tail -1 | cut -d: -f1)"
  } > "$STATUS"
  commit "Census stage 3c: pod status ($1)" "$STATUS"
}

hold() {  # stay up without working, so a stop through the API is the only thing that ends the pod
  echo "holding: $1"
  sleep infinity
}

# 1. packages and uv
apt-get update -q && apt-get install -yq build-essential git tmux curl zlib1g-dev ca-certificates python3 procps \
  || { echo "apt failed"; hold "apt"; }
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | env INSTALLER_NO_MODIFY_PATH=1 sh
command -v uv >/dev/null || { status failed "uv did not install"; hold "uv"; }

# unpushed commits from before a restart go first
git fetch -q origin "$BRANCH" && [ -n "$(git log "origin/$BRANCH..HEAD" --oneline)" ] && push

# the run has already finished: nothing to do
if [ "$(tail -1 "$D/ledger.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["kind"])')" = verdict ]; then
  status done "the ledger ends with the verdict"
  hold "done"
fi

# 2. the venv
uv python install 3.13 && uv sync --frozen --group dev --group qec \
  || { status failed "uv sync"; hold "sync"; }

# 3. self-test
status selftest
if ! uv run --no-sync pytest -q tests/test_qec_census_3c.py tests/test_qec_census_3b.py; then
  status failed "the stage 3b or 3c tests failed (see /workspace/pod-run.log)"
  hold "tests"
fi
problems=$(uv run --no-sync python -c "import importlib.util as u
s = u.spec_from_file_location('c', '$D/study.py'); c = u.module_from_spec(s); s.loader.exec_module(c)
print(c.consistency())")
if [ "$problems" != "[]" ]; then
  status failed "consistency: $problems"
  hold "consistency"
fi

# 4. the hardware
hw=$(mktemp)
{ nproc; lscpu | grep -E 'Model name|MHz|Thread|Core|Socket'; free -g | head -2; cc --version | head -1; } > "$hw"
model=$(grep 'Model name' "$hw")
[ -n "$model" ] || model="nproc $(nproc) $(uname -m)"
if ! grep -qlF "$model" "$D"/hardware-runpod*.txt 2>/dev/null; then
  out=$D/hardware-runpod.txt
  [ -e "$out" ] && out=$D/hardware-runpod-$(date -u +%Y%m%dT%H%M).txt
  { date -u +%FT%TZ; echo "pod: ${RUNPOD_POD_ID:-?}"; cat "$hw"; } > "$out"
  commit "Census stage 3c: hardware of the RunPod machine the run resumes on" "$out"
fi

# 5. resume, committing records as they arrive
status running "study.py resume --workers 4"
( cd "$R" && .venv/bin/python -u "$D/study.py" resume --workers 4 >> "$RUNLOG" 2>&1 ) &
run=$!
on_stop() {  # a pod stop: commit what is written, then end the run
  commit "Census stage 3c: records ($(wc -l < "$D/records.jsonl") tori), pod stopping" \
    "$D/records.jsonl" "$D/ledger.jsonl"
  kill "$run" 2>/dev/null; exit 0
}
trap on_stop TERM INT
seen=""
while kill -0 "$run" 2>/dev/null; do
  sleep 120 & wait $!  # in the background, so a stop's TERM reaches the trap at once
  torus=$(grep -E '^[0-9]+x[0-9]+: ' "$RUNLOG" 2>/dev/null | tail -1 | cut -d: -f1)
  commit "Census stage 3c: records ($(wc -l < "$D/records.jsonl") tori)" "$D/records.jsonl" "$D/ledger.jsonl"
  [ "$torus" != "$seen" ] && { seen=$torus; status running "study.py resume --workers 4"; }
done
wait "$run"; code=$?
commit "Census stage 3c: records ($(wc -l < "$D/records.jsonl") tori), run ended" "$D/records.jsonl" "$D/ledger.jsonl"
if [ "$(tail -1 "$D/ledger.jsonl" | python3 -c 'import json,sys; print(json.load(sys.stdin)["kind"])')" = verdict ]; then
  status done "verdict written"
else
  status failed "study.py exited with $code before the verdict (see /workspace/s3c-run.log)"
fi
hold "end"
