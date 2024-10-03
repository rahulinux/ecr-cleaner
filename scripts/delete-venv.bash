#!/bin/bash
readonly VENV="venv"

if [ ! -e "pyproject.toml" ]; then
    echo "Current directory does not appear to be a python package..." >&2
    echo
    exit 1
fi

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "You're in a virtualenv, deactivate it first." >&2
    echo
    exit 1
fi

if [ -d "$VENV" ]; then
    rm -rf "$VENV"
fi
