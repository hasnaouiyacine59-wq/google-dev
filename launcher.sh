#!/bin/bash
set -m

PIDS=()

cleanup() {
    for pid in "${PIDS[@]}"; do kill -- -$pid 2>/dev/null; done
    pkill -9 -f "ca_open.py" 2>/dev/null
    kill $(jobs -p) 2>/dev/null
    wait 2>/dev/null
    exit 0
}

trap cleanup INT TERM EXIT

for s in 1 2 3 4 5 6; do
    (
        while true; do
            python3 ca_open.py -s $s || true
        done
    ) &
    PIDS+=($!)
done
wait
