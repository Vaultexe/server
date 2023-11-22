#!/bin/bash

# Exit on error
set -e
# Run in debug mode (display executed commands)
set -x

# Run tests
coverage run --rcfile=pyproject.toml -m pytest ./tests/
coverage combine
coverage report --rcfile=pyproject.toml -m
coverage html --rcfile=pyproject.toml
coverage erase --rcfile=pyproject.toml
