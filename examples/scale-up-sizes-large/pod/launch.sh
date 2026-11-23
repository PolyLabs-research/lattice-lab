#!/usr/bin/env bash
# Run part 2 of the scale-up test (sides 2048 and 4096) on a rented CPU pod, from the lab's own
# machine: rent the pod, check its speed, start the registered run there, bring the ledger and
# the records back as they grow, and delete the pod when the verdict is in, when anything
# fails, or ten minutes before the deadline. Started detached, so it does not depend on the
# session that started it:
#
#   systemd-run --user --unit=sizes-large --collect \
#       bash examples/scale-up-sizes-large/pod/launch.sh HOURS MAX_RATE
#   e.g. HOURS 6 and MAX_RATE 1.12 (cpu5c, 32 vCPUs): $6.72 at most
#
# Large pods are often out of stock for minutes at a time. SIZES names the sizes that will do,
# best first (FLAVOUR:VCPUS, e.g. "cpu5c:32 cpu5g:16 cpu5c:16"), and WAIT the minutes to keep
# asking; the first in stock under MAX_RATE is taken.
#
# The log and the pulled files go to ~/lattice-lab-runs/sizes-large/. Nothing in the repository
# is changed: when the run is done, copy pulled/ledger.jsonl and pulled/records.jsonl into
# examples/scale-up-sizes-large/, verify, and commit. The pod's own deadline and the sweeper
# timer on this machine cap the cost whatever happens to this script.
set -u
HOURS=${1:?hours}
MAX_RATE=${2:?the confirmed ceiling in dollars an hour}
SIZES=${SIZES:-cpu5c:32}
WAIT=${WAIT:-0}
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
D=examples/scale-up-sizes-large
OUT=$HOME/lattice-lab-runs/sizes-large
mkdir -p "$OUT/pulled"
exec >> "$OUT/launch.log" 2>&1
CHESS=$HOME/Documents/dev/chess
RP=("$CHESS/.venv/bin/python" "$CHESS/scripts/runpod_pod.py")
PY=$REPO/.venv/bin/python
say() { echo "$(date -Is) $*"; }
cd "$REPO" || exit 1

# the pod clones from GitHub, so what runs there must be what is pushed, and still unrun
BRANCH=$(git rev-parse --abbrev-ref HEAD)
COMMIT=$(git rev-parse HEAD)
git fetch -q origin "$BRANCH"
[ "$(git rev-parse "origin/$BRANCH")" = "$COMMIT" ] || { say "HEAD is not what origin/$BRANCH holds"; exit 1; }
[ -z "$(git status --porcelain --untracked-files=no)" ] || { say "the tree has uncommitted changes"; exit 1; }
[ "$(tail -1 "$D/ledger.jsonl" | "$PY" -c 'import json, sys; print(json.loads(sys.stdin.read())["kind"])')" = prediction ] \
  || { say "the ledger does not end with the registration"; exit 1; }
[ ! -e "$D/records.jsonl" ] || { say "there are records already"; exit 1; }

say "launch: one of $SIZES, $HOURS h cap, at most \$$MAX_RATE/h, asking for $WAIT minutes; $BRANCH at ${COMMIT:0:8}"
# shellcheck disable=SC2086  # SIZES is a list
"$PY" -u "$D/pod/cpu_pod.py" --sizes $SIZES --hours "$HOURS" --max-rate "$MAX_RATE" --wait "$WAIT" --yes 2>&1 | tee "$OUT/launch.out"
got=$(grep '^launched ' "$OUT/launch.out" | tail -1)
POD=$(echo "$got" | sed -n 's/^launched \([a-z0-9]*\) .*/\1/p')
DEADLINE=$(echo "$got" | sed -n 's/^launched [a-z0-9]* taz-[a-z0-9_-]*-dl\([0-9]*\) .*/\1/p')
FLAVOR=$(echo "$got" | sed -n 's/.*(\(cpu[0-9a-z]*\), \([0-9]*\) vCPUs.*/\1/p')
VCPU=$(echo "$got" | sed -n 's/.*(\(cpu[0-9a-z]*\), \([0-9]*\) vCPUs.*/\2/p')
[ -n "$POD" ] && [ -n "$DEADLINE" ] && [ -n "$FLAVOR" ] && [ -n "$VCPU" ] || { say "no pod launched; stopping"; exit 1; }
# a run at side 4096 holds 3 GB: 64 GB takes fourteen at a time, 32 GB eight
case "$FLAVOR:$VCPU" in
    cpu5c:32 | cpu5g:16 | cpu3g:16 | cpu3c:32) workers=14 ;;
    cpu5c:16 | cpu3c:16) workers=8 ;;
    *) workers=4 ;;
esac
WORKERS=${WORKERS:-$workers}
# the speed gate: 0.6 s for the newer generation, 0.9 s for the older
case "$FLAVOR" in cpu3*) gate=0.9 ;; *) gate=0.6 ;; esac
GATE=${GATE:-$gate}
say "pod $POD: $FLAVOR, $VCPU vCPUs; $WORKERS workers; speed gate $GATE s"

SSH=()
pull() {  # whatever the pod has so far; a file that is not there yet is skipped
    [ ${#SSH[@]} -gt 0 ] || return 0
    local rsh="${SSH[*]:0:${#SSH[@]}-1}" host=${SSH[-1]} f
    for f in "lattice-lab/$D/records.jsonl" "lattice-lab/$D/ledger.jsonl" pod-run.log hardware.txt verdict.json STATE; do
        rsync -a -e "$rsh" "$host:/root/run/$f" "$OUT/pulled/" 2> /dev/null
    done
}
terminate() {
    for _ in 1 2 3 4 5 6; do
        "${RP[@]}" terminate "$POD" && { say "terminated $POD"; return 0; }
        sleep 30
    done
    say "COULD NOT TERMINATE $POD: its own deadline and the sweeper remain"
    return 1
}
fail() {
    say "FAILED: $*"
    pull
    terminate
    notify-send -u critical "lattice-lab sizes-large" "failed: $*" 2> /dev/null || true
    exit 1
}

ready=$("${RP[@]}" wait-ssh "$POD" --timeout 900) || fail "no SSH"
line=$(echo "$ready" | sed -n 's/^ssh ready: //p' | tail -1)
[ -n "$line" ] || fail "no ssh command in: $ready"
read -r -a SSH <<< "$line"  # resolved once: nothing below asks the API again until the end
say "ssh: ${SSH[-1]}"

# a host can be many times slower than it should be: time a plain loop (0.24 s on the lab's machine)
gate=$("${SSH[@]}" 'python3 -c "
import time
t = time.time(); x = 0
for i in range(5000000): x += i
print(round(time.time() - t, 2))"') || fail "the speed gate did not run"
say "speed gate: $gate s"
awk -v t="$gate" -v most="$GATE" 'BEGIN { exit !(t > most) }' \
    && fail "a slow host: $gate s for a loop that takes 0.24 s here (at most $GATE s allowed)"

"${SSH[@]}" 'cat > /root/pod-run.sh' < "$D/pod/pod-run.sh" || fail "staging"
timeout 30 "${SSH[@]}" "nohup setsid bash /root/pod-run.sh $BRANCH $COMMIT $WORKERS > /root/pod-run.out 2>&1 < /dev/null &" > /dev/null 2>&1
sleep 45
"${SSH[@]}" 'test -s /root/run/STATE' || fail "the job did not start"
say "job started on $POD"

while :; do
    sleep 180
    # the state is read before the pull: once it says done, what the pull brings is final
    state=$("${SSH[@]}" 'cat /root/run/STATE' 2> /dev/null)
    pull
    records=$(cat "$OUT/pulled/records.jsonl" 2> /dev/null | wc -l)
    say "state: ${state:-?}; $records of 96 records"
    case "$state" in
        done)
            kind=none
            for _ in 1 2 3 4 5; do  # the pod is deleted only once its results are here
                kind=$(tail -1 "$OUT/pulled/ledger.jsonl" | "$PY" -c 'import json, sys; print(json.loads(sys.stdin.read())["kind"])')
                records=$(cat "$OUT/pulled/records.jsonl" 2> /dev/null | wc -l)
                [ "$kind" = verdict ] && [ "$records" = 96 ] && break
                sleep 20
                pull
            done
            [ "$kind" = verdict ] && [ "$records" = 96 ] \
                || fail "done, but the pulled ledger ends with $kind and there are $records records"
            terminate
            say "done: the ledger and $records records are in $OUT/pulled"
            notify-send "lattice-lab sizes-large" "done: $records records pulled" 2> /dev/null || true
            exit 0
            ;;
        failed*) fail "the pod's run: $state" ;;
    esac
    [ "$(date +%s)" -lt $((DEADLINE - 600)) ] || fail "ten minutes to the deadline, at $records records"
done
