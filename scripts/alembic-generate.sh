#!/bin/bash

# This script is used to auto generate a new alembic migration script.

set -e

# Check if the migration description is provided
if [ -z "$1" ]; then
    echo "Usage: $0 \"file_name\""
    exit 1
fi

#  Generate a the migration script
echo "Generating a new alembic migration script..."
alembic revision --autogenerate -m "$1"

#  Upgrade the database to the latest version
echo "Upgrading the database to the latest version..."
alembic upgrade head
