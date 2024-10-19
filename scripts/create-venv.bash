#!/bin/bash
readonly VENV="venv"

if [ ! -e "pyproject.toml" ]; then
    echo "Current directory does not appear to be a python package..." >&2
    echo
    exit 1
fi

if [ -d "$VENV" ]; then
    echo "Directory already exists: $VENV" >&2
    echo "Will not recreate it." >&2
    echo
    exit 0
fi

PYTHON=
if command -v python3.13 >/dev/null 2>&1; then
    PYTHON="python3.13"
elif command -v python3.12 >/dev/null 2>&1; then
    PYTHON="python3.12"
elif command -v python3.11 >/dev/null 2>&1; then
    PYTHON="python3.11"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "Could not find python interpreter on PATH" >&2
    echo
    exit 1
fi

# Create virtualenv
"$PYTHON" -m venv "$VENV"

# shellcheck disable=SC1091
source "$VENV"/bin/activate

pip install --upgrade pip
pip install -e .[cli,dev]
