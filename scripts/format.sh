#!/bin/bash
set -x

# Run all pre-commit hooks
pre-commit run --all-files

# Remove cache files
find .. | grep -E "(\.pytest_cache|\.ruff_cache|__pycache__)" | xargs rm -rf
