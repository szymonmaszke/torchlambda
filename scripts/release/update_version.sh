#!/usr/bin/env bash

set -e

repository="$(basename "$(git rev-parse --show-toplevel)")"
# Version equal to current timestamp
echo "Current working directory: $(pwd)"
echo "OLD VERSION CHECK:"
cat "$repository"/_version.py

echo "__version__ = \"$(date +%s)\"" >"$repository"/_version.py

echo "NEW VERSION:"
cat "$repository"/_version.py
