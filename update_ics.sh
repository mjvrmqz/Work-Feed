#!/bin/bash

cd "$(dirname "$0")"

if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

git remote set-url origin https://github.com/mjvrmqz/Work-Feed.git
git stash --include-untracked
git fetch origin
git rebase origin/main
git stash pop

python3 work_feed_to_ics.py

git add "Work Feed.ics"
git diff --cached --quiet && echo "No changes to ICS, skipping commit." && exit 0
git commit -m "Update ICS feed $(date -u +"%Y%m%dT%H%M%SZ")"
git push origin main
