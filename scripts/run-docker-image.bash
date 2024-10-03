#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

# shellcheck disable=SC1091
source "$DIR/functions.bash"

# Retrieve current git sha
TAG="$(get_git_sha)"
if [ -z "$(is_dirty)" ]; then
    # Working dir is clean, attempt to use tag
    GITTAG="$(get_tag_at_head)"

    # If git tag found, use it
    if [ -n "$GITTAG" ]; then
        TAG="$GITTAG"
    fi
fi
readonly TAG

# Load project name from project manifest
PROJECT_NAME="$(get_project_name)"
readonly PROJECT_NAME

# Run the image
docker run \
    --env-file .env \
    -it "$PROJECT_NAME:$TAG" \
    "$@"
