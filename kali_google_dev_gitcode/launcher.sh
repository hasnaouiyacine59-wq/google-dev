#!/bin/bash
set -m

PIDS=()

cleanup() {
    # kill all process groups
    for pid in "${PIDS[@]}"; do kill -- -$pid 2>/dev/null; done
    # force kill any remaining save_me.py
    pkill -9 -f "save_me.py" 2>/dev/null
    # kill all background jobs
    kill $(jobs -p) 2>/dev/null
    wait 2>/dev/null
    exit 0
}

trap cleanup INT TERM EXIT

for s in 1 2 3 4 5; do
    (
        while true; do
            python3 save_me.py -s $s || true
        done
    ) &
    PIDS+=($!)
done
wait
