#!/bin/bash

# A script to synchronize the local repository with the remote.
#
# This script will:
# 1. Add all local changes to the staging area.
# 2. Commit the changes with a default or user-provided message.
# 3. Pull the latest changes from the remote, rebasing local commits on top.
# 4. Push the synchronized history to the remote.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The remote to sync with.
REMOTE="origin"
# The branch to sync. Gets the current branch name automatically.
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# --- Script Logic ---

echo ">>> Starting Git sync for branch '$BRANCH' with remote '$REMOTE'..."

# 1. Add all changes to the staging area.
echo ">>> Staging all changes..."
git add .

# 2. Commit the changes.
# A default commit message with a timestamp.
COMMIT_MESSAGE="Sync: $(date +'%Y-%m-%d %H:%M:%S')"

# If an argument is provided to the script, use it as the commit message.
if [ -n "$1" ]; then
    COMMIT_MESSAGE="$1"
fi

# Only commit if there are staged changes.
if git diff-index --quiet --cached HEAD --; then
    echo ">>> No local changes to commit."
else
    echo ">>> Committing with message: '$COMMIT_MESSAGE'"
    git commit -m "$COMMIT_MESSAGE"
fi

# 3. Pull remote changes, rebasing local commits on top.
echo ">>> Pulling remote changes with rebase..."
git pull --rebase "$REMOTE" "$BRANCH"

# 4. Push changes to the remote.
echo ">>> Pushing changes to remote..."
git push "$REMOTE" "$BRANCH"

echo ">>> Sync complete."
