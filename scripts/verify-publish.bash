#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

VERSION="$(cat "$DIR"/../VERSION)"
readonly VERSION

# Load project name from project manifest
PROJECT_NAME="$(python -c "import toml; print(toml.load('$DIR/../pyproject.toml')['project']['name'])")"
readonly PROJECT_NAME

# Retries a command up to 3 times
retry() {
    MAX_ATTEMPTS=4
    count=0
    base=5
    local command="$*"
    while [ "$count" -lt "$MAX_ATTEMPTS" ]; do
        count=$((count + 1))
        # shellcheck disable=SC2086
        eval $command && break

        if [ "$count" -eq "$MAX_ATTEMPTS" ]; then
            echo
            echo "Failed after $MAX_ATTEMPTS attempts" >&2
            exit 1
        fi

        echo
        echo "Retring ($count/$((MAX_ATTEMPTS - 1)))..."
        delay=$((base * count))
        echo "Sleeping for $delay seconds before retrying..."
        sleep "$delay"
    done
}

if [[ "$#" -eq 0 ]]; then
    echo "You must specify --test or --prod as arguments" >&2
    echo
    exit 1
fi

echo "Creating a virtual env..."
VENV="$(mktemp -d)"
python -m venv "$VENV"

echo "Copying verification script..."
cp "$DIR"/../src/scripts/verify_install.py "$VENV/verify_install.py"

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "Attempting to install version ($VERSION) in virtualenv ($VENV)..."
while [[ "$#" -gt 0 ]]; do
    case $1 in
    --test)
        echo "Installing requirements-cli from main index, since not all packages are available in test.pypi..."
        pip install -r "$DIR"/../requirements-cli.txt
        echo "Attempting install: ${PROJECT_NAME}==$VERSION"
        retry pip install --index-url https://test.pypi.org/simple/ "${PROJECT_NAME}==$VERSION"
        ;;
    --prod)
        echo "Attempting install: ${PROJECT_NAME}==$VERSION"
        retry pip install "${PROJECT_NAME}[cli]==$VERSION"
        ;;
    --*= | -*)
        echo "Error: Unsupported flag $1" >&2
        echo
        exit 1
        ;;
    esac
    shift
done

pushd "$VENV" >/dev/null 2>&1
python verify_install.py
popd >/dev/null 2>&1

echo "Virtualenv location: $VENV"
