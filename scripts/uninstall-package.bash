#!/bin/bash
set -ueo pipefail

PROJECT_NAME=$(python -c "import toml; print(toml.load('pyproject.toml')['project']['name'])")
echo "Uninstalling $PROJECT_NAME..."
pip uninstall -y "$PROJECT_NAME"
echo "Done."
