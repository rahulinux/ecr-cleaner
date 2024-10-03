#!/bin/bash
set -euo pipefail
DIR=.

# Ensure the up-to-date requirements are installed
cd "$DIR"
# shellcheck disable=SC1090
eval "$(make venv)"
make setup
