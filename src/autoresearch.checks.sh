#!/bin/bash
set -euo pipefail

# Unit test checks for autoresearch
# Ensures harness integrity - must pass before any result can be kept

# Run pytest on the test directory, suppressing success output
# Only show errors to keep output minimal
uv run pytest test/ -v --tb=short 2>&1 | tail -80
