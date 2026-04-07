#!/bin/bash
trap 'kill $(jobs -p) 2>/dev/null; pkill -f "save_me.py"; exit' INT TERM

for s in 1 2 3 4 5; do
    while true; do
        python3 save_me.py -s $s
    done &
done
wait
