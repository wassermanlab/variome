#!/bin/bash
# Run all backend tests (middleware + VCF import tests) and re-run on file changes.
# Requires dev dependencies: uv sync --dev
# Unsets DB so Django falls back to the in-memory SQLite database for tests.

unset DB

uv run watchmedo shell-command \
    --patterns="*.py" \
    --recursive \
    --drop \
    --command='uv run python manage.py test variome_backend.tests --verbosity=2' \
    .
