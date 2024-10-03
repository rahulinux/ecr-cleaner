#!/bin/bash
set -euo pipefail
DIR=.

# Create a virtualenv
cd "$DIR"
make create-venv
