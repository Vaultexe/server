#!/bin/bash

set -e
set -x

# Run entrypoint.py
# waits for DB connection
python3 ./app/entrypoint.py

# Run db migrations
alembic upgrade head

# Run db seed
python3 ./app/db/seed.py

# Start the server
# $@ is the command line arguments passed to the script
# $@ is the command in the CMD directive in the Dockerfile
exec "$@"
