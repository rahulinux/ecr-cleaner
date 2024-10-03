#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

echo "Running pre-push hook..."
pushd "$DIR/.." >/dev/null 2>&1 || (echo "Could not set working directory" && exit 1)

if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "Virtual env not found, activating default venv..."
    eval "$(make venv)"
fi

echo "Running linters..."
make lint

echo "Running tests..."
make test

echo "Ensuring the app can be built..."
make build
make docker

popd >/dev/null 2>&1
echo "Pre-push checks passed."
