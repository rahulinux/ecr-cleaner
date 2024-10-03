#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

# shellcheck disable=SC1091
source "$DIR/functions.bash"

VERSION_FILE="$DIR/../VERSION"
readonly VERSION_FILE

# Check that the working directory is clean
if [ -n "$(is_dirty)" ]; then
    echo "Working directory is dirty, cannot proceed..." >&2
    git status
    exit 1
fi

# Retrieve current git sha
VERSION="$(get_tag_at_head)"
if [ -z "$VERSION" ]; then
    echo "No version tag found, cannot proceed..." >&2
    exit 1
fi

# Output the detected tag
echo "Updating version in '$VERSION_FILE' to: $VERSION"
echo "$VERSION" >"$VERSION_FILE"
