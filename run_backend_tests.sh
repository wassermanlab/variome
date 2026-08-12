#!/bin/bash
set -euo pipefail
# Run all backend tests (middleware + VCF import tests) and re-run on file changes.
# Requires dev dependencies: uv sync --dev
# Unsets DB so Django falls back to the in-memory SQLite database for tests.

export DB=""
COMMAND="uv run python manage.py test variome_backend.tests"
echo "Running backend tests with command: $COMMAND"
$COMMAND;

uv run watchmedo shell-command \
    --patterns="*.py" \
    --recursive \
    --drop \
    --command="$COMMAND" \
    .
