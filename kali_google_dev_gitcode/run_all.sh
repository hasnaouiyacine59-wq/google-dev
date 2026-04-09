#!/bin/bash

run_session() {
    local s=$1
    while true; do
        echo "[session $s] starting..."
        python3 visual_automation.py -s $s
        echo "[session $s] restarting..."
    done
}

for s in 1 2 3 4 5; do
    run_session $s &
done

wait
