#!/usr/bin/env -S bash -euo pipefail
#
# Checkout the latest code (or a given SHA) and restart the application.

git fetch github

ref="${1:-github/main}"
git reset --hard $ref

export COMMIT_SHA=$(git show-ref --head --hash=7 | head -1)
./restart.sh
