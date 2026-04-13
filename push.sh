#!/bin/bash
cd "$(dirname "$0")"
git add -A
git commit -m "${1:-update}"
git push
