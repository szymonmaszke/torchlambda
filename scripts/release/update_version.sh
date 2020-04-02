#!/usr/bin/env bash

set -e

repository="$(basename "$(git rev-parse --show-toplevel)")"
# Version equal to current timestamp
cat "$repository"/_version.py
echo "__version__ = \"$(date +%s)\"" >"$repository"/_version.py
cat "$repository"/_version.py
