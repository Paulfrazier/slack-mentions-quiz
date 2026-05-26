#!/usr/bin/env bash
# Rebuild index.html from spec.json through the local no-score variant template.
set -e
cd "$(dirname "$0")"
python3 build.py
